---
name: page-forge
description: |
  End-to-end frontend page UI pipeline: direction → implementation → motion
  → delivery acceptance, producing polished pages without the "AI look".
  Invoke when the user says any of:
  - build a page / make a landing page
  - redo this page's UI
  - end-to-end frontend page
  Chinese triggers: 帮我做一个页面 / 做一个落地页 / 把这个页面UI重做 / 前端页面一条龙
---

# page-forge — end-to-end frontend page pipeline

## Positioning

From a one-line brief to a user-approved page, via a 4-phase pipeline. This skill only handles **orchestration, gates, and checkpoint management**; implementation details are delegated to `frontend-specialist` and `ui-verify` in the same repo. Target output: polished pages that don't look AI-generated.

## Trigger boundaries

**Should invoke**: build a page / landing page / portfolio / marketing site / redo a page's UI / end-to-end frontend page.

**Should NOT invoke**:
- Bug fixes, error chasing, single-property style tweaks
- Pure backend / API / database work
- User explicitly opts out

## Startup actions (every run)

1. Determine the project root (ask the user or infer from context; never guess paths)
2. Create the checkpoint dir `<project-root>/docs/page-forge/` and read `docs/page-forge/state.md` — **if it exists, resume from the recorded phase; never start over**. If not, initialize all four phases as pending
3. Report the roadmap to the user: four phases + two user gates + expected pace

## P1 Direction

Goal: lock down "what kind of page" before touching code.

1. Infer the brief — page type / mood words / reference sites / audience / brand assets (logo, colors, fonts). If the user provided reference images, those win
2. Set direction with the taste dials from `taste-rules.md` (this dir): three dials (layout variance / motion intensity / visual density) + scenario presets
3. Produce `docs/page-forge/brief.md`: style conclusions + anti-slop key points (no purple gradients, no centered hero + three equal cards, no emoji icons, no Inter + default blue, no full-page glassmorphism, no filler copy)
4. **User Gate A**: present the style conclusions (optionally with 1-2 reference screenshots) for user confirmation. No page code before confirmation. "Up to you" = authorized to skip; record that in state.md

## P2 Implementation (frontend-specialist)

1. Feed brief.md + taste-rule highlights to `frontend-specialist` to write the page code
2. Hard rules (baked into the implementation requirements): black/white/gray base + one accent color; real copy — no Lorem ipsum or filler; icon library instead of emoji; spacing on a 4/8 scale; at most two font families
3. When done, build/syntax checks must pass; mark P2 done in state.md

## P3 Motion (optional dependency)

Run only if the brief includes motion requirements or the user asked for a "lively feel"; skip for purely static admin pages.

1. If GSAP-related skills are available (e.g. gsap-core / gsap-scrolltrigger), use them for hero motion and scroll triggers; **otherwise degrade gracefully** — CSS transitions/animations + Intersection Observer achieve equivalent effects. Never block on a missing dependency
2. Micro-interactions follow the motion principles in `taste-rules.md`: UI motion <300ms, ease-out entrances, button `:active scale(0.97)`, animate only transform/opacity, respect `prefers-reduced-motion`
3. Less is more: every motion effect must justify its purpose; delete the ones that can't

## P4 Delivery (ui-verify + taste checklist)

1. `ui-verify` starts a server and screenshots for acceptance: full page + key interaction states, at both desktop and mobile widths
2. Self-check screenshots against the anti-slop list (the P1 key points + the checklist appendix in `taste-rules.md`); on failure, go back to P2, fix, re-screenshot
3. Run the interface safety checklist from `taste-rules.md` (keyboard reachable, touch targets ≥24px, visible focus, form conventions, dark mode)
4. **User Gate B**: hand the screenshots (and before/after comparisons for redo tasks) to the user for visual sign-off. Delivered only when they pass
5. After passing, mark state.md as delivered and shut down the browser/server processes used for acceptance

## Checkpoint resume

- All state lives in `<project-root>/docs/page-forge/state.md`: per-phase pending/in_progress/done + brief path + one-line progress per completed phase
- If a session is interrupted, re-trigger this skill: read state.md and continue from the first non-done phase
- Mid-flight requirement changes: finish the current phase → update brief.md → re-run from P2 (P1 only re-runs if the style direction changed)

## Input / output

Input: a one-line brief + (optional) reference images / reference sites / brand assets.
Output: accepted page code + `docs/page-forge/brief.md` + acceptance screenshots.

## Error handling and fallbacks

1. **Sub-skill invocation failure**: record the failed step, retry the same phase once; if it still fails, stop and report to the user — never guess onward
2. **Build/runtime errors**: must be fixed before advancing; no moving forward with a broken state
3. **Mid-flight requirement change**: follow the checkpoint-resume rerun rules
4. **Destructive operations**: deleting, overwriting uncommitted files, pushing — ask the user first
5. **Fallback**: if any phase dead-ends, hand the current artifacts + state.md to the user and explain where it's stuck
