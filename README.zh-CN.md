# page-forge

**A Claude Code skill pipeline that ships web pages without the "AI look" — from one-line brief to user-approved UI.**
一句话：前端页面 UI 全流程编排 skill——定向 → 实现 → 动效 → 交付验收，一条龙产出看不出 AI 味的高质感页面。

[English](README.md) | 简体中文

| 不用 page-forge | 用 page-forge |
|---|---|
| ![before](assets/demo-before.png) | ![after](assets/demo-after.png) |

（同一虚构产品的落地页：左侧是典型的 AI 生成页，右侧是走完 page-forge 流程的产出。源文件在 `examples/`，可自己打开对比。）

## 为什么有这个项目

让 AI 写页面，功能都对，但一眼假：紫色渐变 hero、三张等宽卡片排排坐、emoji 当图标、"智能·高效·赋能"的空话文案。模型每次都往这套安全模板里收敛。

page-forge 的答案不是换提示词，是**流程**：

- **闸门前置**：写代码之前先把风格定死，用户确认后才动手（闸门 A）
- **反 AI 味硬规则**：10 条可勾选的规则（禁等宽卡片阵 / 禁 emoji 图标 / 品牌色只做点缀 / 真实文案…），P2 实现时逐条对，违反任一=返工
- **亲眼验收**：交付前强制起服务、截图、桌面+移动两档核对（闸门 B），不许只靠"代码看起来对"收工
- **断点续跑**：状态落盘在项目 `docs/page-forge/state.md`，会话中断从断点继续，不从头来

## 仓库内容（3 个 skill，配套使用）

| skill | 职责 |
|---|---|
| `skills/page-forge` | 编排器：四阶段流水线 + 两个用户闸门 + 断点管理 + 内置风格规则（`taste-rules.md`） |
| `skills/frontend-specialist` | 实现层：响应式 / a11y / 动画性能 / 现代 CSS 的落地规范 |
| `skills/ui-verify` | 验收层：起服务 → 截图看视觉 → 走交互流程 → 交付通过/失败清单 |

## 安装

```bash
git clone https://github.com/Andrew-svg-stac/page-forge.git
# 把三个 skill 目录复制进 Claude Code 的 skills 目录
cp -r page-forge/skills/* ~/.claude/skills/
```

Windows 用户对应路径为 `C:\Users\<你>\.claude\skills\`。重启会话或新开会话后生效。

**可选依赖**（没有也能跑，对应阶段自动降级）：

- GSAP 类 skill（动效增强）——缺失时 P3 用 CSS transition + Intersection Observer 实现等价效果
- 浏览器自动化工具（验收增强）——`ui-verify` 的命令示例基于 [agent-browser](https://github.com/vercel-labs/agent-browser) CLI，可替换为 Playwright/Puppeteer 等任何工具，流程本身工具无关

## 使用

对 Claude Code 说：

```
帮我做一个落地页
把这个页面 UI 重做
```

触发后它会：确认项目根目录 → 给你四阶段路线图 → P1 出风格 brief 请你确认 → 实现 → （按需）动效 → 起服务截图请你亲眼验收。全程两个闸门，你不点头不动下一步。

## 风格拨盘（P1 怎么定调）

每个项目先定三个拨盘，后续布局/动效/密度决策全由它们驱动：

- **布局变化度** 1=完全对称 ↔ 10=艺术性错落
- **动效强度** 1=静态 ↔ 10=电影感
- **视觉密度** 1=画廊留白 ↔ 10=驾驶舱密排

不同场景有内置预设（极简编辑器风 5/3/2，高级品牌风 7/5/3，落地页默认 8/6/4…），详见 `skills/page-forge/taste-rules.md`。

## Credits

方法论吸收与致谢（本仓库为独立重写，非原文搬运）：

- 设计品味与反套路规则：社区 "anti-slop frontend" 设计品味 skill（Leonxlnx）的方法论
- 动效与微交互原则：[Emil Kowalski](https://emilkowalski.com/) 的交互设计原则
- 交付检查单：参考 [Vercel](https://vercel.com/) 的 web interface guidelines
- 动效库：[GSAP](https://gsap.com/)（可选依赖）

## License

[MIT](LICENSE)
