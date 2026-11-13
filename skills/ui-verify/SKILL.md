---
name: ui-verify
description: UI 验收流程总入口：选型分流→起服务→回归段→视觉段看图→交互段走流程→交付结果清单（移动端页面走移动端增量检查，原生App/真机走真机增量检查，条件触发时固化为spec）。触发：验证UI、验收页面、看看效果、浏览器里跑一下、截图看看页面、真机验收、真机走查、固化spec、跑回归。强制真开页面看，禁只靠代码推断收工。

---

# UI 验收流程（ui-verify）

## 为什么存在

用户明确批评过"每次感觉都不去看 UI"。纯代码推断和数字验证
（getComputedStyle、scrollWidth==offsetWidth）抓不到真实视觉 bug——
flex 压缩导致的文字竖排换行、颜色层级观感错误（实战中视觉模型抓到过
3 个数字验证全漏的真 bug）。**本 Skill 是硬流程：UI 活必须走完五步才交付。**

## 触发条件

- "验证一下 xxx 在浏览器里的效果" / "看看页面效果" / "验收 UI"
- "检查下这个前端改动对不对" / "截图看看"
- 任何涉及"确认页面实际表现"的请求

## 工作流程（第 0-4.5 步必走，不可跳步；第 5 步条件触发）

### 第 0 步：选型分流

| 条件 | 用什么 |
|---|---|
| 本地 localhost 页面（95% 场景） | agent-browser（默认） |
| 页面要 Edge 里的登录态（线上系统） | Playwright MCP 连 Edge 9222（先确认桌面「Edge调试模式.vbs」已跑） |
| 多账号/多环境并行 | agent-browser 加 `--session <名>` 隔离 |

### 第 0.5 步：端口地址簿（2026-10-10 定稿）

| 端口 | 谁来连 | profile | 用途 |
|---|---|---|---|
| **9222** | Playwright MCP（本机写死只连这个） | 按载体：登录态任务=用户真实 profile；降级验收=临时 profile | 唯一 MCP 门面，同一时间只一个实例占 |
| **9223** | 自定义脚本 `connect_over_cdp`（端口随意，此处预留） | 临时 profile | 未来并行场景预留 |

**纪律：**
- 同一时间只活一个自动化浏览器实例（16GB 内存红线）。开发会话内连续验证可保活（30min 内有操作 daemon 不退），收工/切任务才 close
- **浏览器是多窗口共享资源（2026-10-14 定稿）**：开浏览器前先问其他窗口是否在 UI 验证（或 `agent-browser session list` 查活跃会话）；收工只 `close --session <自己项目名>`，default 会话和别人的会话**一律不 close**。冲突症状是 CDP os error 10060，不是工具坏
- **并行项目隔离（2026-10-14）**：agent-browser 每个命名会话 = 独立浏览器实例（各自 cookie/状态）。发现有别的活跃会话（其他窗口在验收）→ 本项目全程带 `--session <项目名>` 隔离，防止共抢 default 标签页互毁截图和 @eN 引用；单项目场景仍用 default 不折腾。**项目可并行、浏览器验收必须排队**：N 个项目并行时主项目走完整五步，其余项目 UI 验收延后排队（先交付代码级检查），不靠多开浏览器实例硬扛——16GB 扛不住 3 个 Chromium
- open 前判断：`curl http://127.0.0.1:9222/json/version` 秒回 = 有实例活着 → 先查清是谁（session list / 查命令行），再决定接管或收掉，**不盲目重试 open**
- 隔久了的第一次 open 一律后台跑不设短超时——冷启动 60-120s 是物理成本，透明等待不算卡
- agent-browser 内部端口自己管理，不占用 9222/9223

### 第 1 步：起服务并确认通

- 长跑 node/引擎进程用 WMI `Win32_Process.Create` 隐藏窗口启动（见全局 CLAUDE.md 长跑进程纪律）
- `curl -s -o /dev/null -w "%{http_code}" http://localhost:端口` 返回 2xx/3xx 才继续，避免白等
- node --watch 服务行为诡异时：先 `node --check`，僵死则杀干净重启

### 第 1.5 步：回归段——有 spec 先跑 spec（2026-10-20 新增）

固化只写不跑 = 归档不是哨兵。起完服务先查本项目有没有既有固化 spec：

1. 查 spec 目录（如 `tests/e2e/`）里有没有本项目的固化 spec
2. 有 → **先跑一遍**（如 pytest），退出码 0 才继续视觉/交互段；非 0 按第 5 步红灯处置（修代码或删 spec，禁止挂红）
3. 没烂 spec 但有旧测试 → 旧测试失败先分辨是"真退化"还是"选择器过时"（2026-10-20 实证：OTCS 旧 test_screenshots 因 placeholder 改版已烂），过时的修复或删除，不并排堆第二份

这一步就是固化的"裁决执行点"：spec 的价值在每次验收被重放，不在库存里。

### 第 2 步：视觉段——看效果对不对（核心）

**端判定（拍图前先定，2026-10-20 新增）**：PC 页面用 PC 基线视口（2561×1314 或项目既有基线）；移动页面/移动端项目用移动基线（默认 375×812）。**移动页证据必须移动视口拍，PC 视口拍的作废**。移动端额外检查项见《移动端增量检查》节。

1. `agent-browser open http://localhost:端口`
2. `agent-browser screenshot --full "D:\路径\xxx.png"`（全页截图落盘）
3. `Read` 该 png → 多模态模型（默认 glm-5.3-flash）直接看图，图片进上下文即为"亲眼看过"
4. **看图前置检查**：当前会话若是纯文本模型（glm-5.3 旗舰）→ 必须先切 glm-5.3-flash 再做视觉验收；不看图只靠代码推断 = 没走本流程，禁止交付

视觉分析 prompt 要具体："详细描述布局结构、颜色、组件、交互元素"，
或逐项问"X 是横排还是竖排 / 有没有溢出"。
重点看：布局错乱、文字溢出/竖排换行、颜色层级、间距、移动端断点。

**参考对齐环（2026-10-29 新增，条件触发）**：任务带参考图/参考站截图（复刻/对齐类）时视觉段加机械对齐，无参考图跳过：

1. `PYTHONUTF8=1 python "C:/Users/Administrator/.claude/skills/ui-verify/scripts/diff.py" <实现页截图> <参考图>` → 整体差异率 + 自上而下 10 段热区分布 + 热力图（`<impl名>.diff.png`）；**热力图照样 Read 亲眼看**，热区指哪看哪
2. 指标清单逐项对（主判据）：布局骨架（区块顺序/栏数）、间距尺度、字阶、色板值——参考图上量出目标值，实现页用 eval `getComputedStyle` 量实际值
3. 不收敛 → 回实现改 → 重截重 diff；同一区域 2 轮无改善 → 停下把两张图+热区分段给用户人判，不自缠

**边界（防假闸）**：像素 diff 只对「同结构复刻」（照参考图 1:1 重做）收敛；「风格参考」任务内容不同像素必不重合——此时 diff 只当**差异区域定位器**，主判据回归指标清单，**禁止拿差异率当通过硬闸**。

### 第 3 步：交互段——看功能通不通

```bash
agent-browser snapshot -i              # 拿 @eN 引用（只列可交互元素）
agent-browser fill @e3 "测试内容"       # 或 find label/text 语义定位
agent-browser click @e5
agent-browser wait --text "成功标志"    # 关键：等结果出现，不等会误判
agent-browser errors                   # 页面 JS 报错
agent-browser console                  # console 消息
```

走核心流程（如 登录→操作→提交）；页面一变（导航/HMR）引用即过期，重新 snapshot。

### 第 4 步：交付结果

给用户两样，不让回翻：

- 截图路径（用户可自行打开核对）
- 通过/失败点清单

发现问题先报告再修，不擅自改。

### 第 4.5 步：轻量影响面兜底（只在本 skill 独立使用时做）

**跳过条件**：本次改动已走过 `feature-dev-pipeline` 的 P3.5 全量回归 → 不重复做，直接交付。

未走 pipeline 的独立验收（小改动/纯 UI 调整是主场景）：

1. `git status` / `git diff --name-only` 看这次实际碰了哪些文件（含后端文件——后端改了前端遭殃的回归，只看页面根本发现不了）
2. 对碰到的共享物（共享组件/工具函数/API）grep 谁还在用 → 列出受影响的兄弟页面
3. 挑 top 1-2 个受影响页面走**快速冒烟**（打开 → 核心交互点一下 → 看 errors），不用全五步
4. 结果写进交付清单，格式：
   - `影响面：本次改 A，连带检查 B（通过）/ C（未检查，理由）`
5. 红线：发现影响面比预期大（要动共享物/多页面遭殃）→ **停下建议升级走 feature-dev-pipeline**，不带病收工

### 第 5 步：固化（条件触发，默认跳过）

> 2026-10-20 PoC 实测后新增（OTCS 绿→红→绿验证通过）。原则：AI 只负责探索和固化，
> **"通过"由确定性测试的退出码裁决**，不由看图结论裁决。截图是档案，spec 是哨兵——档案不能站岗。

**触发条件（满足其一才做，否则跳过本步）：**
- 同一页面/路径第 2 次以上迭代（第 1 次只验收不固化）
- 用户明说"固化" / "沉淀成 spec"

**固化规范：**
- 只固化**核心路径**（一个项目 1-2 条，如 访客对话→回复出现），冷门页面不固化
- 顺着项目现有测试栈，不新装套件（如 OTCS 是 Python Playwright/pytest，就直接写 pytest spec）
- 项目**没有**测试栈 → 默认只验收不固化；要新引入测试栈（装依赖/建目录）先问用户，不擅自加
- 断言防假通过三件套：**阴性对照**（只认动作后新出现的元素）+ **计数增量**（消息/条目数严格增加）+ **确定性内容**（Mock 模式的固定回复）；选择器语义定位优先（get_by_placeholder / get_by_role），裸文本作辅助
- 端口不硬编码：读环境变量（OTCS 用 `OTCS_E2E_BASE_URL`，默认避开 5173——它常被其他项目前端占用，2026-10-20 实测踩过）
- 现有 spec 已烂的先修再固化，不并排堆第二份

**红灯处置（生命线，比写 spec 本身重要）：**
- 红 = 意外退化 → 修代码
- 红 = 功能被主动删除/需求变更 → **同一个 commit 删掉对应 spec**（功能和 spec 生死与共）
- **禁止挂红**：挂红的 spec 会让真 bug 的红灯被当噪音忽略，整个哨兵体系作废

**交付时附带**：spec 文件路径（完整绝对路径）+ 运行命令 + 退出码结果。

## 移动端增量检查（初版 2026-10-20，实战修订中）

> 适用：响应式 Web / H5 移动页面。主流程不变，走到视口与检查时用本节。
> 本节是通用工程实践初版，未在本机项目全量实测——踩坑后回填修订，暂不当硬规则。

**视口基线**：默认 375×812；项目有既有移动基线则对齐。agent-browser 语法 `set viewport 375 812`。

**五项检查（PC 不查的）**：
1. 断点断裂：横向滚动条出现、文字溢出/竖排换行、卡片错位
2. 触控目标：可点元素点击区 ≥44px（PC 能点的密集小按钮手机点不中）
3. 软键盘遮挡：输入框聚焦后键盘是否盖住输入区/发送按钮（聊天页重灾区）
4. hover 失效：PC 靠 hover 出现的菜单/提示，移动端不可达
5. safe-area：iPhone 底部横条不压住关键按钮

**要不要加移动变体（2026-10-20 补）**：按"路径的真实用户是否在手机上使用"决定——手机也用的路径加变体；纯桌面路径（如 admin 后台）不加；移动端项目反向，设备仿真即默认主形态。

**仿真边界（2026-10-20 补）**：布局是真实按手机宽度排（媒体查询真触发），断点断裂/横向溢出/功能闭环能自动抓；软键盘遮挡、Safari 特有怪癖、性能、摄像头权限**测不出**——这些靠真机连局域网人工终审（vite `npm run dev -- --host` 后手机开 Network 地址），人工项不进固化链。

**固化差异**：spec 用 Playwright 设备描述符仿真（如 `devices['iPhone 13']`，一次换视口+触摸+UA+DPR）；额外断言一行：横向溢出 `document.scrollWidth <= innerWidth`。

**边界（形态决定工具链，触到再启用不预开工）**：微信小程序 Playwright 进不去 → `miniprogram-automator` + 微信开发者工具；原生 App → Maestro/Appium + 真机规则（模拟器过 ≠ 真机过）。

## 真机增量检查（L3b，2026-11-06 补）

> 适用：原生 App / 原生+H5 混合壳 / 涉及系统权限、真实拨号、录音、推送等设备能力的验收。
> 升级判据：页面上看得见但 DOM/snapshot 找不到，或涉及原生壳/系统权限 → 从设备仿真升本节。
> 本节只管通用打法；项目专属常量（设备型号/包名/端口/发版链）归各项目 CLAUDE.md，不写进这里。
> 改动还没打进测试包就要求真机验 → 先走项目的发版链 skill（如 harnesstow 的 `fdj-release-test`）发完包，再回本节走查。

**前置核对**：`adb devices` 确认插线在线；多台并存用 `adb shell getprop ro.product.model` 认准设备防串；真机包名常与生产包名是不同变体——动包前 `adb shell pm list packages | grep <关键词>` 核对，别操作错包。

**驾驶配方骨架**：

**⭐ 首选 Pinky（2026-11-10 起，实测评估全过后定稿）**：能走 Pinky 就不走裸 adb——`phone_connect { task: "<人话任务名>" }` → `phone_launch` → `phone_tap { ref }` 全链。优势：结构树+OCR 双读（uni-app/webview 混合页全读出，角标数字都能读）、ref 锚点跨屏稳定（天然消灭裸 adb 的坐标漂移）、Android 13+ 在隐藏副屏操作人机不打架、危险动作网关强制人审。坑：①遇 `uncertain` 先 `phone_observe` 核实再动，禁盲重试（11-09 实测规程有效）；②`phone_*` 工具新会话才加载（MCP 会话启动时挂）；③前置=Pinky.exe 开着+手机插线；④旧机型（iOS<17.4 / iPhone 8 Plus 级）连不上，回退 Mac 老链路或裸 adb。Pinky 不可用（没装/没开/不在网）→ 走下面 1-6 的裸 adb 配方。

1. 唤醒解锁：`adb shell input keyevent KEYCODE_WAKEUP` + `adb shell wm dismiss-keyguard`（设了锁屏密码的机型自动化过不去，请人解锁一次）
2. 拉起 App：`adb shell am start -n <包名>/<Activity>`；冷启动吃新包先 `am force-stop <包名>` 再 start
3. 点按输入：`input tap x y` / `input text`（`input text` 进不去中文——走 ADBKeyboard 或 App 内粘贴）
4. 看结果：`adb exec-out screencap -p > 截图.png` 后**必须 Read 逐张看**（同浏览器截图纪律）；原生层结构 `adb shell uiautomator dump` 拉 XML 定位
5. webview 内部：uiautomator dump 只见原生层不见 webview DOM → 首选 Pinky 结构树+OCR（混合页可全读）；CDP 路（`adb forward tcp:9222 localabstract:webview_devtools_remote`）依赖 webview 调试开关，**未开调试的包走不通**（房当家现役测试包实测仅 about:blank，11-09）——包没开调试别死磕 CDP
6. 系统能力（拨号/录音/权限弹窗）：真实触发；权限弹窗用 uiautomator 定位点「允许」；被拒过的权限 `adb shell pm grant <包名> <权限>` 补，别死循环点弹窗

**通用坑（实战在案）**：
- **keyevent 挂断通话会连带触发锁屏**（真人挂断不会）→ 挂断断言前 wake+dismiss-keyguard+am start 补刀再继续
- **App 内状态跨轮残留**（录音中/会话态/弹窗）→ 找 App 官方「结束/重置」入口自愈，别硬杀进程了事
- **模拟器过 ≠ 真机过**：厂商 ROM 差异（权限文案/后台杀策略/键盘行为）是真机层固有变量，诡异行为先怀疑 ROM 再怀疑代码
- **送达盲区**：浏览器/接口层冒烟永远测不到「新包有没有真送达设备」→ 发版后必须查服务端分发文件的访问日志（看设备 UA 真来拉过），再让设备冷启动吃包
- **验设备跑的哪版代码**：解包安装产物 grep 业务 js / 二进制 manifest 提权限清单——版本以包内容为准，别信界面显示

## 输出格式示例

```
## UI 验收结果：<页面/功能名>

✅ 通过项
- 布局：整体结构与设计一致，无错位
- 交互：登录→提交流程走通，无 JS 报错

❌ 失败项
- 文字溢出：按钮"确定提交"在 375px 宽度下被截断

截图：D:\xxx\verify-20261002.png
```

## 坑清单（实战踩过，别再踩）

- **截图拍了必须 Read 逐张看（2026-10-15）**：对照「这张要证明什么」逐项核验；拍了没看的截图=没有证据，等于没走本流程
- **视口必须与基线口径一致（2026-10-15）**：agent-browser 默认开小窗（约 1256×563），会触发页面响应式断点导致证据失真；有既有基线时开工先 `agent-browser set viewport <宽> <高>`（语法是 `set viewport`，裸 `viewport` 是 Unknown command）；发现视口不对立即停下修正重拍，不带病继续
- 全页截图 flag 是 `--full`（不是 --full-page）；flag 放路径**前**，放路径后会被当成保存文件名
- 找元素：`find text "xxx"`（不是 `find "xxx"` 也不是 `--text`）
- 导航/HMR 后 `@eN` 引用过期 → 重新 snapshot 再操作
- **`@eN` 定位飘/反复点不中且恢复链无效 → 查页面语义（2026-10-26）**：`@eN` 引用走浏览器 accessibility 树，骨架差（`<div>` 冒充按钮、控件无可访问名）会让定位系统性发飘——用 `eval` 查目标元素真身（tagName / aria-label），该是 `<button>` 的别用 div 糊；自己写页面顺手用真语义控件+label，给下轮验收铺路（这条查的是"地基质量"，恢复链治的是工具故障，两码事）
- fixed 定位元素 offsetParent===null，别用它判断可见性
- agent-browser 命令挂死 → `agent-browser session list` 看会话 → `close --all` 清僵尸守护进程，别傻重试
- **并行窗口互杀（2026-10-14）**：SessionEnd 全局钩子是 `close --all`——另一个 Claude 窗口收工会把你的浏览器一起杀掉。被杀的表现是下次命令冷启动 60-120s 或报连不上，不是工具坏了：重新 open 即可，不要去清守护进程（那是活的）
- **`close --all`+杀守护后 `open` 仍永挂** = 它的 chrome 子进程残着锁 profile（2026-10-08 实战）。按命令行杀：`Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" | ? {$_.CommandLine -match 'agent-browser-browsers'} | ? { Stop-Process -Id $_.ProcessId -Force }`。它的 Chromium 在 `D:\Programs\agent-browser-browsers\`、profile 在 `%TEMP%\agent-browser-*`；**别按映像名杀 chrome.exe**（可能是用户自己的浏览器——先看命令行再动手）
- agent-browser 整体不可用时降级路径：Playwright MCP（本机配置为连 9222）→ 需要一个 9222 载体浏览器：优先 WMI 隐藏窗口拉独立 profile Edge（`--user-data-dir` 指临时目录 + `--remote-debugging-port=9222`，用 `&` 裸拉会被会话回收杀掉）；要连用户已登录态才用 `D:\Desktop\Edge调试模式.vbs`（会先杀掉用户所有 Edge，跑前提醒）
- 命令语法拿不准 → 先跑 `agent-browser skills get core`（文档跟 CLI 版本走，永不依赖记忆写命令）
- `eval` 的裸 const 会跨调用残留（同名再跑报 Identifier already declared）→ 一律 IIFE 包裹 `(()=>{...})()`
- eval 长耗时（>15s 轮询类）会拖死 CDP 报 os error 10060 → 拆短命令，shell 侧 sleep + 多条短 eval
- 改完代码立刻测前端行为可能被 HMR 干扰（模块级单例状态被重置、轮询被打断）→ 结果诡异先 `location.reload()` 重测再下结论
- **参考图 diff 前先对齐视口口径（2026-10-29）**：参考图与实页尺寸/视口不一致会整图假红（脚本会 warn 并缩放，缩放救度量救不了断点错位）——先用同基线视口把两边重拍同口径再 diff；参考图是站外图量不了 getComputedStyle，指标值从图上估，估算误差写进对照清单
- **screenshot 相对路径按 agent-browser 守护进程 cwd 落盘，不是 shell cwd（2026-10-29 实测）**：症状是「✓ Screenshot saved to xxx.png」但自己 cd 的目录里没有文件——一律写绝对路径，不赌 cwd

## 与其他 Skill / 记忆的分工

- **agent-browser skill**：工具语法手册（命令怎么写）——本 Skill 只管流程（什么时候做什么）
- **feature-dev-pipeline**：走它的大功能在 P3.5 已做全量回归，本 skill 被它调用验收时跳过第 4.5 步（第 1.5 步回归段仍执行——spec 重放属于回归的一部分）；独立使用时第 4.5 步是唯一的回归兜底
- **端的分工（2026-10-20 审计定稿）**：建站时移动适配由 frontend-specialist（响应式专节）/ design-taste-frontend（dvh、移动渲染细节）负责；本 skill 是**唯一验收闸门**，管的移动端 = 验收 + 固化。跨 skill 的横切关注点收敛于此，不散落复制
- **记忆 visual-verification-loop**：本 Skill 的知识来源，流程已收编于此，以本文件为准
- **page-forge `quality-loop.md`（2026-10-29）**：新建/重做页面的「十维质感评分 + 修最弱三项」迭代循环归 page-forge（建完页的品味打磨，允许自动改）；本 skill 是对错验收闸门（发现问题先报告），两者不混——本 skill 报告的质感类问题可转 quality-loop 处理
