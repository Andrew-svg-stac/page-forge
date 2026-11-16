---
name: page-forge
description: End-to-end frontend page UI pipeline (direction → implementation → motion → delivery acceptance) producing polished pages without the "AI look". Invoke for: build a page / landing page / redo this page's UI / replicate a reference page / 做页面 / 落地页 / 页面UI重做 / 前端页面一条龙.
---

# page-forge — end-to-end frontend page pipeline

## Positioning

From a one-line brief to a user-approved page, via a 4-phase pipeline. This skill only handles **orchestration, gates, and checkpoint management**; implementation details are delegated to `frontend-specialist` and `ui-verify` in the same repo. Target output: polished pages that don't look AI-generated.

## Trigger boundaries

**Should invoke**: build a page / landing page / portfolio / marketing site / redo a page's UI / end-to-end frontend page / replicate a reference page or redesign on top of one.

**Should NOT invoke**:
- Bug fixes, error chasing, single-property style tweaks
- Pure backend / API / database work
- User explicitly opts out

## Startup actions (every run)

1. Determine the project root (ask the user or infer from context; never guess paths)
2. Create the checkpoint dir `<project-root>/docs/page-forge/` and read `docs/page-forge/state.md` — **if it exists, resume from the recorded phase; never start over**. If not, initialize all four phases as pending
3. Report the roadmap to the user: four phases + two user gates + expected pace

## P0 Scenario routing (decide at entry)

One-sentence test: **did the user hand over a reference page as the "answer" for the layout, and are they happy with it?** A valid reference is a **full page whose rendered result you can capture** (a URL you can open, or a full-page screenshot) — design specs, style guides, and scattered reference images don't count; route those to ③ and fold them into P1 direction. Three routes; later phases get trimmed accordingly:

**① Pure replication (reference page + follow it exactly)**
- **Skip** P1 direction (the answer is pinned by the reference; style freedom is zero); **Gate A is replaced by the replication instruction itself** — but before touching code, still present the "replication scope + asset-replacement plan" for the user to review
- Align the layout by **measuring per-element geometry against the reference at the target viewport** (computed styles / rects, not eyeballing); motion goes through P3 step 6 (capture → reverse-engineer → rebuild → numeric verification ±80ms)
- **Asset red line**: never copy the reference page's logos, ads, product images, or brand fonts — replace everything with the user's own brand assets. Layout mechanics may align; brand assets may not be copied
- Acceptance runs the reference alignment loop (ui-verify) + motion numeric verification (pixels may differ due to swapped assets; timing parameters must pass)

**② Mixed (reference page + partly unhappy / wants changes or additions)**
- First produce a **three-class section list** for user confirmation: keep as-is (follow the reference) / change (reference is just the base) / add (not in the reference)
- Keep-as-is sections → reverse-align per ①; changed/new sections → **run a lightweight forward direction step for that section** (2–3 design options for the user to pick → implement after sign-off; no need for the full-page P1, just its direction output)
- **Unified design tokens**: one set of color/type/spacing tokens across the whole page — replicated and redesigned sections must not each do their own thing and become a frankenpage
- Replicated sections affected by the redesign **re-run motion verification**: pixels may change (the visuals changed), timing parameters may not (the animation wasn't broken)

**③ Pure forward (no reference page)**: run P1–P4 as written; this section changes nothing.

**Input substitution for ①**: skipping P1 means no brief.md; P2's inputs become "measured geometry data from the reference page + the user's brand asset list".

**Re-entry after delivery**: the user looks at the replica and says "I want this section redesigned" → that section switches to the ② forward chain for options; everything else stays.

**Rule tiers (same mechanism as quality-loop's three-tier gates)**:
- **Floor (mechanically checkable, never waived)**: measured geometry data must be produced and archived (rects/computed styles); motion timing numbers must pass; before a redesign, mechanically capture the full inventory (links / fields / handlers — per quality-loop's "redesign safety belt") and verify item-by-item after — one missing = fail; no resource references to the reference page's CDN domains in the output; build passes
- **Reflex (judgment calls, default applies, deviations logged)**: the three-class section split (the user confirms it, never the AI), motion-tier choices, style direction — any deviation from the default must be recorded with a reason in the delivery notes
- **Finish (polish, never blocks delivery)**: icon style tweaks, minor spacing deltas, copy polish

## P1 Direction

Goal: lock down "what kind of page" before touching code.

0. **Design-system retrieval (optional enhancement, degrades gracefully)**: if a design-system retrieval tool is installed locally (e.g. the `ui-ux-pro-max` skill — check for its `scripts/search.py`), generate a design system from the brief keywords (product type + audience; if the brief isn't final, extract from the user's own words) and save it to `docs/page-forge/design-system.md` (on resume, reuse the existing file — don't regenerate); then pull 1–2 candidate styles with the same keywords. If the tool is absent, skip this step silently and note "no design-system retrieval, P1 runs native" in state.md
1. Infer the brief — page type / mood words / reference sites / audience / brand assets (logo, colors, fonts). If the user provided reference images, those win
2. Set direction with the taste dials from `taste-rules.md` (this dir): three dials (layout variance / motion intensity / visual density) + scenario presets
3. **Scenario four questions (infer them, don't interrogate)**: the AI infers four answers from context and writes them into the brief for the user to correct — never asks them as a question list: who is this for / expected effect (conversion-trust vs atmosphere-creative) / traffic temperature / decision cost. These four set the P3 motion tier and the P4 acceptance focus
4. **Style rotation rule (simplified)**: user names a past style to reuse → reuse it; user says "close enough" → same family, different knobs (swap the type scale / whitespace / density / motion tier); AI-autonomous with no reference → **must switch style family** (differing from recent outputs and anything already in `archives.md` — prevents every page having the same face)
5. Produce `docs/page-forge/brief.md`: style conclusions + four-question assumptions + anti-slop key points (no purple gradients, no centered hero + three equal cards, no emoji icons, no Inter + default blue, no full-page glassmorphism, no filler copy). When a design system was retrieved, copy the selected one (Pattern / Style / Colors / Typography / Effects / AVOID / delivery checklist) into the brief as a **binding constraint**
6. **User Gate A**: present two things for the user to pick — ① an **experience-direction menu** (illustrated-poster / living-page / functional-app / hybrid; each with a one-line sample-style description + an effort magnitude; if `archives.md` has saved profiles, nominate them — the AI nominates, the user decides); ② the style conclusions (optionally with 1-2 reference screenshots). **With a retrieved design system: list the recommended style and the alternatives together for the user — never default to the top retrieval hit**; data-driven ≠ aesthetically right, industry-standard answers tend to collide. No page code before confirmation. "Up to you" = authorized to skip; record that in state.md

## P2 Implementation (frontend-specialist)

1. Feed brief.md + taste-rule highlights to `frontend-specialist` to write the page code
2. Hard rules (baked into the implementation requirements): black/white/gray base + one accent color; real copy — no Lorem ipsum or filler; icon library instead of emoji; spacing on a 4/8 scale; at most two font families. **When brief.md binds a design system, its palette / fonts / style / AVOID list is the highest-priority hard constraint** (palette items land as CSS variables one by one); on conflict with the generic rules, the design system wins
3. When done, build/syntax checks must pass; mark P2 done in state.md

## P3 Motion (optional dependency)

Run only if the brief includes motion requirements or the user asked for a "lively feel"; skip for purely static admin pages.

1. If GSAP-related skills are available (e.g. gsap-core / gsap-scrolltrigger), use them for hero motion and scroll triggers; **otherwise degrade gracefully** — CSS transitions/animations + Intersection Observer achieve equivalent effects. Never block on a missing dependency
2. Pick from the four presets in `motion-presets.md` (this dir): hero entrance / scroll narrative / micro-interactions / count-up stats — each with a copy-paste skeleton, tuning table, and pitfalls. **Plan motion in four layers (supersedes the single per-page budget)**: ambient (background atmosphere: video / grain / floating elements) · reactive (hover / focus / active micro-interactions) · narrative (scroll-driven: scrub / word-by-word reveal / sticky sections — **no longer blanket-banned**; often where the page's signature lives) · state (loading / success / error feedback). Tier by the P1 four questions: conversion-trust pages keep the narrative layer minimal (≤1 spot), atmosphere-creative pages may open ambient + narrative together; never stack multiple signatures within one layer; every effect must still justify its purpose
3. Micro-interactions follow the motion principles in `taste-rules.md`: UI motion <300ms, ease-out entrances, button `:active scale(0.97)`, animate only transform/opacity, respect `prefers-reduced-motion`
4. Less is more: every motion effect must justify its purpose; delete the ones that can't
5. **Motion must never hide content**: scroll-reveal animations are progressive enhancement only — content stays visible and readable by default, with no JS, in print, and in full-page screenshots (initial opacity must not be 0 waiting for JS to lift it)
6. **Replicating a moving reference**: when the user provides a *moving* reference and wants its motion precisely cloned (a section on a live URL / an mp4 screen recording / a GIF / a Lottie), use a frame-by-frame cloning tool if one is installed (e.g. the `reanimate` skill): capture → reverse-engineer → rebuild → numeric verification (default ±80ms) — never imitate by feel. Clone the animation behavior only; copy, colors, and content still follow this page's own plan. No tool installed → fall back to manual capture-and-compare against the reference recording

## P4 Delivery (ui-verify + taste checklist)

1. `ui-verify` starts a server and screenshots for acceptance: full page + key interaction states, at both desktop and mobile widths
2. Self-check screenshots against the anti-slop list (the P1 key points + the checklist appendix in `taste-rules.md`); on failure, go back to P2, fix, re-screenshot. **Tasks with reference screenshots (replication / alignment) additionally run the reference alignment loop** (ui-verify): metric checklist + pixel-diff heatmap as a difference locator — never the pass bar
3. **Quality score loop (optional enhancement, default on for new builds and redesigns)**: per `quality-loop.md` (this dir) — screenshot → score ten dimensions → fix the three weakest (concrete value changes) → re-shoot, max 3 rounds, bar = average ≥8 with no dimension under 7; skip for purely functional admin pages. Correctness problems still route through `ui-verify`; this loop only iterates on polish. **Redesign tasks additionally run the "redesign safety belt"** (quality-loop.md §3): mechanically capture the full inventory of links / form fields / interaction handlers / heading hierarchy before touching code, verify item-by-item after — one missing = fail, roll back. Blocker tiers follow the same file's three-tier gates (Floor never passes / Reflex overridable with a recorded reason / Finish never blocks)
4. Run the interface safety checklist from `taste-rules.md` (keyboard reachable, touch targets ≥24px, visible focus, form conventions, dark mode)
5. **User Gate B**: hand the screenshots (and before/after comparisons for redo tasks) to the user for visual sign-off. Delivered only when they pass
6. **Brand taste archive (optional)**: when Gate B passes, ask the user whether this project's taste profile is worth archiving — if yes, append the four-question answers + style family + anti-slop points + signature mechanism to `archives.md` (this dir; created on first save), tagged by brand / page type. Future same-brand pages get it nominated at Gate A; adopting it stays the user's call. Declined → archive nothing
7. After passing, mark state.md as delivered and shut down the browser/server processes used for acceptance

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
