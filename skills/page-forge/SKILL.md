---
name: page-forge
description: |
  前端页面 UI 全流程编排：定向→实现→动效→交付验收，一条龙产出无 AI 味的高质感页面
  当用户说以下任意内容时调用本 skill：
  - 帮我做一个页面
  - 做一个落地页
  - 把这个页面UI重做
  - 前端页面一条龙
  English triggers: build a page, make a landing page, redo this page's UI,
  end-to-end frontend page.
---

# page-forge — 前端页面 UI 全流程一条龙

## 定位

从一句话需求到用户亲眼验收的页面，四阶段流水线。本 skill 只做**编排、闸门、断点管理**；实现细节交给同仓的 `frontend-specialist` 与 `ui-verify`。产出目标：看不出 AI 味的高质感页面。

## 触发边界

**应该调用**：做一个页面 / 落地页 / 作品集 / 官网页 / 重做某页 UI / 前端页面一条龙。

**不应该调用**：
- 修 bug、改报错、单点样式微调
- 纯后端 / API / 数据库
- 用户明确说不用本 skill

## 启动动作（每次必做）

1. 确定项目根目录（问用户或从上下文推断，不猜路径）
2. 建 `<项目根>/docs/page-forge/` 断点目录，读 `docs/page-forge/state.md`——**存在则从记录的阶段续跑，不从头来**；不存在则初始化四阶段全 pending
3. 报路线图给用户：四阶段 + 两个用户闸门 + 预计节奏

## P1 定向

目的：动代码之前把「做什么样的页面」定死。

1. 推断 brief——页面类型 / 氛围词 / 参考站 / 受众 / 品牌资产（logo、色、字体）；用户给过参考图就以参考图为准
2. 按 `taste-rules.md`（本目录）的风格拨盘定调：三拨盘（布局变化度 / 动效强度 / 视觉密度）+ 用例预设
3. 产出 `docs/page-forge/brief.md`：风格结论 + 反 AI 味要点（禁紫渐变、禁居中 hero + 三等分卡片、禁 emoji 图标、禁 Inter+默认蓝、禁满屏玻璃拟态、文案禁空话）
4. **用户闸门 A**：把风格结论（可用 1-2 张参考截图佐证）给用户确认。确认前禁止写任何页面代码。用户说「随便/你定」= 授权跳过，在 state.md 记录

## P2 实现（frontend-specialist）

1. 把 brief.md + taste 规则要点喂给 `frontend-specialist` 写页面代码
2. 硬规则（写进实现要求）：黑白灰为主 + 一个强调色、真实文案不许用 Lorem/占位空话、图标用图标库不用 emoji、间距用尺度系统（4/8 基数）、字体最多两族
3. 完成后构建/语法检查通过，state.md 记 P2 done

## P3 动效（可选依赖）

仅当 brief 含动效需求或用户要过「有手感」时执行；纯静态后台页跳过。

1. 若环境有 GSAP 相关 skill（如 gsap-core / gsap-scrolltrigger）则调用做主动效与滚动触发；**没有则降级**——用 CSS transition/animation + Intersection Observer 实现等价效果，不因缺依赖卡死
2. 微交互遵循 `taste-rules.md` 的动效原则：UI 动效 <300ms、ease-out 进入、按钮 `:active scale(0.97)`、只动 transform/opacity、尊重 `prefers-reduced-motion`
3. 动效宁少勿滥：每处动效说得出目的，说不出的删

## P4 交付（ui-verify + taste 检查单）

1. `ui-verify` 起服务截图验收：全页 + 关键交互态，桌面 + 移动两档
2. 截图先自查 AI 味清单（P1 的反 AI 味要点逐条对 + `taste-rules.md` 附录检查单），不合格回 P2 改完再截
3. 过一遍 `taste-rules.md` 的接口兜底清单（键盘可达、触控目标 ≥24px、focus 可见、表单规范、暗色模式）
4. **用户闸门 B**：截图 + 改前改后对比（重做类任务）给用户亲眼验收，通过才算交付
5. 通过后 state.md 标 delivered，收掉验收用的浏览器/服务进程

## 断点续跑

- 状态全部写在 `<项目根>/docs/page-forge/state.md`：四阶段各 pending/in_progress/done + brief 路径 + 每阶段结束时一句话进展
- 会话中断后重新触发本 skill：读 state.md，从最后一个非 done 阶段继续
- 用户中途改需求：完成当前阶段收尾 → 更新 brief.md → 从 P2 重跑（P1 只在风格变了才重跑）

## 输入输出

输入：一句话需求 + （可选）参考图/参考站/品牌资产。
输出：验收通过的页面代码 + `docs/page-forge/brief.md` + 验收截图。

## 错误处理与兜底

1. **子 skill 调用失败**：记录失败步骤，同阶段重试一次；仍失败停下报告用户，不猜着继续
2. **构建/运行报错**：修复后才许进下一阶段，禁止带病推进
3. **需求中途变化**：按「断点续跑」的重跑规则处理
4. **破坏性操作**：删除、覆盖未提交文件、推送，先问用户
5. **兜底**：任何阶段卡死，把当前产物 + state.md 交给用户说明卡在哪
