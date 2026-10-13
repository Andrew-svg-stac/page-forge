# page-forge

**A Claude Code skill pipeline that ships web pages without the "AI look" — from one-line brief to user-approved UI.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill%20pipeline-7c3aed)](https://claude.com/claude-code)

English | [简体中文](README.zh-CN.md)

| Without page-forge | With page-forge |
|---|---|
| ![before](assets/demo-before.png) | ![after](assets/demo-after.png) |

(Landing pages for the same fictional product: on the left, a typical AI-generated page. On the right, the output after running the page-forge pipeline. Source files in `examples/` — open them and compare.)

## Why this exists

Ask an AI to build a web page and the functionality will be correct — but it looks fake at a glance: purple gradient hero, three equal-width cards in a row, emoji as icons, and copy full of "intelligent · efficient · empowering" filler. Every model converges on the same safe template.

page-forge's answer isn't a better prompt. It's **process**:

- **Gate the direction first**: style is locked down before any code is written, and only after you confirm it (Gate A)
- **Hard anti-slop rules**: 10 checkable rules (no equal-width card grids / no emoji icons / brand color as accent only / real copy…). Phase 2 checks against every rule — violate one, rework
- **Verify with your own eyes**: before delivery it must start a server, take screenshots, and check desktop + mobile breakpoints (Gate B). "The code looks right" is not allowed as a finish line
- **Resumable**: state is persisted to `docs/page-forge/state.md` in your project, so an interrupted session picks up where it left off

## What's in this repo (3 skills, working together)

| Skill | Role |
|---|---|
| `skills/page-forge` | The orchestrator: 4-phase pipeline + 2 user gates + checkpoint management + built-in style rules (`taste-rules.md`) |
| `skills/frontend-specialist` | Implementation layer: responsive / a11y / animation performance / modern CSS standards |
| `skills/ui-verify` | Acceptance layer: start server → screenshot & inspect → walk the interaction flows → deliver a pass/fail checklist |

## Install

```bash
git clone https://github.com/Andrew-svg-stac/page-forge.git
# Copy the three skill directories into Claude Code's skills folder
cp -r page-forge/skills/* ~/.claude/skills/
```

On Windows the path is `C:\Users\<you>\.claude\skills\`. Restart or start a new session for the skills to take effect.

**Optional dependencies** (works without them; the corresponding phase degrades gracefully):

- A GSAP skill (enhanced motion) — when missing, Phase 3 falls back to CSS transitions + Intersection Observer
- A browser automation tool (enhanced acceptance) — the `ui-verify` examples use the [agent-browser](https://github.com/vercel-labs/agent-browser) CLI, but any tool (Playwright / Puppeteer) works; the workflow itself is tool-agnostic

## Usage

Just tell Claude Code:

```
Build me a landing page
Redo this page's UI
```

It will: confirm the project root → give you a 4-phase roadmap → present a style brief for your approval in Phase 1 → implement → (optionally) add motion → start a server, screenshot, and ask you to visually sign off. Two gates throughout — nothing advances until you nod.

## The taste dials (how Phase 1 sets direction)

Every project starts by setting three dials. All later layout / motion / density decisions are driven by them:

- **Layout variance** 1 = fully symmetric ↔ 10 = artful asymmetry
- **Motion intensity** 1 = static ↔ 10 = cinematic
- **Visual density** 1 = gallery whitespace ↔ 10 = cockpit density

Built-in presets per scenario (minimal editor 5/3/2, premium brand 7/5/3, landing page default 8/6/4…) — see `skills/page-forge/taste-rules.md`.

## Credits

Methodology absorbed with thanks (this repo is an independent rewrite, not a copy):

- Design taste & anti-slop rules: the community "anti-slop frontend" taste skill (Leonxlnx)
- Motion & micro-interaction principles: [Emil Kowalski](https://emilkowalski.com/)'s interaction design principles
- Delivery checklist: informed by [Vercel](https://vercel.com/)'s web interface guidelines
- Motion library: [GSAP](https://gsap.com/) (optional dependency)

## License

[MIT](LICENSE)
