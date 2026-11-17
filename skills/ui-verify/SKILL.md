---
name: ui-verify
description: >
  Invoke when the user asks to "verify the UI", "accept a page", "see how it
  looks", "run it in the browser", "check this frontend change", or
  "screenshot the page". This skill is the single entry point for UI
  acceptance (start server → visual check via screenshots → walk interaction
  flows → deliver a results checklist). Every UI task must actually open the
  page and "look" — finishing based on code inference or numeric checks alone
  is forbidden. Tool examples use the agent-browser CLI, but any browser
  automation tool (Playwright / Puppeteer MCP, etc.) can be substituted; the
  workflow itself is tool-agnostic.
  Chinese triggers: 验证UI / 验收页面 / 看看效果 / 浏览器里跑一下 / 截图看看页面.
---

# UI acceptance workflow (ui-verify)

## Why this exists

Pure code inference and numeric checks (getComputedStyle, scrollWidth==offsetWidth) can't catch real visual bugs — text wrapping vertically because of flex compression, or a color hierarchy that reads wrong. You only find them by opening the page and looking. **This skill is a hard process: a UI task must complete all five steps before delivery.**

## Trigger conditions

- "Verify xxx in the browser" / "see how the page looks" / "accept the UI"
- "Check whether this frontend change is right" / "take a screenshot"
- Any request involving "confirm the page's actual behavior"

## Workflow (five steps, no skipping)

### Step 0: pick the approach

| Condition | Use |
|---|---|
| Local localhost page (95% of cases) | A browser automation tool (example: agent-browser) |
| Online system needing login state | Connect to a real browser with a debugging port (e.g. Playwright + `--remote-debugging-port`) |
| Multi-account / multi-environment parallel | Isolated sessions / separate profiles |

**Discipline: at most one live automated browser instance at a time.** Close it when done or when switching tasks — automated browsers are memory heavy; several at once will push the host machine into swapping.

### Step 1: start the server and confirm it responds

- Start the dev server in the background (for long-running processes, detach from the current shell session so it doesn't die with the session)
- `curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>` must return 2xx/3xx before continuing — don't wait on a dead server

### Step 2: visual check — does it look right (core)

1. Open `http://localhost:<port>`
2. Save a full-page screenshot (agent-browser: `agent-browser screenshot --full <path>`, flag BEFORE the path)
3. **Look at the image**: hand it to a multimodal model or eyeball it item by item. The analysis prompt must be specific: "describe the layout structure, colors, components, and interactive elements in detail", or ask point questions like "is X horizontal or vertical / does anything overflow"
4. Focus on: broken layouts, text overflow / vertical wrapping, color hierarchy, spacing, mobile breakpoints

**Reference alignment loop (conditional — runs only when the task ships reference screenshots, i.e. replication / alignment work; skip otherwise):**

1. `python scripts/diff.py <impl-screenshot> <ref-screenshot>` → overall difference ratio + top-to-bottom 10-band hotspot distribution + heatmap (`<impl>.diff.png`); **open and look at the heatmap too** — let the hot bands direct your eyes
2. Verify the metric checklist item by item (the primary criterion): layout skeleton (section order / column count), spacing scale, type scale, palette values — measure the target values on the reference, then measure the implemented page's actual values via devtools `getComputedStyle`
3. Not converging → back to implementation → fix → re-screenshot → re-diff; a region stuck for 2 rounds with no improvement → stop, hand both screenshots + the band breakdown to the user for a human call — don't loop yourself into a hole

**Boundary (guard against a fake gate)**: pixel diff only converges for *same-structure replication* (1:1 rebuilds of the reference). For "style reference" tasks the content differs, so pixels will never coincide — there the diff is only a **difference-region locator**, the metric checklist stays the primary criterion, and **using the difference ratio as a pass/fail hard gate is forbidden**.

### Step 3: interaction check — does it work

```bash
agent-browser snapshot -i              # get element refs (interactive elements only)
agent-browser fill @e3 "test content"  # or locate semantically
agent-browser click @e5
agent-browser wait --text "success marker"  # key: wait for the result, or you'll misjudge
agent-browser errors                   # page JS errors
agent-browser console                  # console messages
```

Walk the core flow (e.g. login → act → submit). After any page change (navigation / hot reload) element refs expire — re-snapshot.

### Step 4: deliver results

Give the user two things so they don't have to scroll back:

- Screenshot path (they can open and check themselves)
- A pass/fail checklist

Report problems before fixing; don't change things unilaterally.

### Step 4.5: lightweight blast-radius check

1. `git status` / `git diff --name-only` to see which files were actually touched (backend included — a backend change breaking the frontend won't show up by looking at pages alone)
2. For shared artifacts (shared components / utility functions / APIs), grep who else uses them → list affected sibling pages
3. Pick the top 1-2 affected pages for a quick smoke test (open → click through the core interaction → check errors); no need for all five steps
4. Add to the delivery checklist: `Blast radius: this change touched A; also checked B (pass) / C (not checked, reason)`
5. If the blast radius turns out bigger than expected (touching shared artifacts / multiple pages affected) → stop and escalate instead of shipping in a broken state

## Mobile incremental checks (initial 2026-10-20, revised in practice)

> Applies to responsive web / H5 mobile pages. The main workflow is unchanged; this
> section kicks in when choosing the viewport and the checks. It is a first cut of
> general engineering practice — revise it as real projects hit issues; don't treat
> it as a hard rule set yet.

**Endpoint decision (before screenshots)**: PC pages use the project's PC baseline
viewport; mobile pages / mobile projects use the mobile baseline (default **375×812**,
align to the project's existing baseline if it has one). **Mobile evidence must be
shot at the mobile viewport — anything shot at PC width doesn't count.**

**Viewport baseline**: default 375×812. CLI: `set viewport 375 812`.

**Five incremental checks (what the PC baseline doesn't cover)**:

> Meaning of the label: these are *additions checked at the mobile viewport*, not
> "never checked on PC" — check 1 also runs on PC (at PC width); the other four are
> mobile-specific.

1. **Breakpoint breakage**: horizontal scrollbar appears (measure `scrollWidth > innerWidth`), text overflow / vertical wrapping, card misalignment
2. **Touch targets (measured, not eyeballed)**: every key tappable element gets a `getBoundingClientRect` reading; **<44×44px = red, report the concrete value**; adjacent tappables closer than 8px apart risk mis-taps (2026-11-16: upgraded from qualitative to mechanical)
3. **Soft-keyboard occlusion**: after focusing an input, does the keyboard cover the input area / send button (chat pages are the disaster zone; emulation can't test this — see simulation boundary)
4. **Hover dead-ends**: menus/tooltips that only appear on hover are unreachable on mobile
5. **Safe area**: the iPhone home indicator must not cover key buttons

**Key-button geometry archive (2026-11-16)**: record x/y/width/height of the hero CTA
and every key interactive button in the acceptance notes. Criteria: fully inside the
viewport (not clipped, not covered by the keyboard or the home indicator), tap area
≥44×44. Acceptance only accepts measured numbers, never "looks fine".

**Mobile variant or not**: decide by "do real users of this path use it on a phone" —
phone-used paths get a mobile variant; purely desktop paths (e.g. an admin console)
don't; for mobile-first projects it inverts — device emulation is the default form.

**Simulation boundary**: layout is genuinely laid out at phone width (media queries
really fire), so breakpoint breakage / horizontal overflow / functional loops can be
caught automatically; **soft-keyboard occlusion, Safari-specific quirks, performance,
and camera permissions cannot be tested in emulation** — those need a human final pass
on a real phone over LAN (`vite npm run dev -- --host`, then open the Network address
on the phone); human-only items never enter the spec-snapshot chain.
**Root-cause tip (for the implementation side, not an acceptance criterion)**: the
high-frequency root cause of mobile breakpoint breakage is fixed-px absolute
positioning / fixed-width containers — prefer flex/grid + relative units
(% / `clamp()` / `min()`). Acceptance still only measures behavior (did it break, is
the button where it should be), and **never checks which CSS technique was used**.

**Snapshot difference**: the spec uses a Playwright device descriptor for emulation
(e.g. `devices['iPhone 13']` — one call sets viewport + touch + UA + DPR); add one
extra assertion: no horizontal overflow, `document.scrollWidth <= window.innerWidth`.

**Boundary (toolchain follows the form factor — enable when touched, don't pre-open)**:
WeChat mini-programs are out of Playwright's reach → `miniprogram-automator` + WeChat
devtools; native apps → Maestro/Appium + real-device rules (emulator pass ≠ device pass).

## Replica acceptance in one command (2026-11-16)

For HTML-demo replication tasks, the pixel alignment loop plus the computed-style
checklist plus interaction comparison are packaged into one script:

```bash
PYTHONUTF8=1 python scripts/replica-check.py <ref-demo.html> <replica.html> \
  --viewports 1920x1080,1366x768 --checks checks.json --out report
```

It automatically screenshots both pages (forcing all scroll containers to settle first
— smooth-scroll transients used to produce fake diff hotspots), diffs computed styles
element-by-element (auto-collects every class selector × 21 key properties), runs the
pixel diff + 10-band heatmap, runs the interaction comparison (`--checks` takes
`[{"name","js"}]`; each JS expression runs on both pages and the outputs must match),
then prints a PASS/FAIL verdict and writes `summary.md` with screenshots, heatmaps,
and the full diff list. Measured baseline: a same-source replica passes 102 selectors ×
21 properties × 2 viewports with 0.00% pixel diff; tampering a single color value gets
caught red (self-validated in both directions).

**Mobile replica**: same command, swap `--viewports 375x812` and pass the bundled
`scripts/mobile-checks.json` (4 mechanical checks: horizontal overflow, per-element
44px touch targets, CTA geometry + in-viewport, tappable spacing <8px; adjust the CTA
selector). **Caveat: parity green means the two pages match, not that either is good**
— read the returned values by hand (real demos commonly have several sub-44px targets;
a full-screen overlay makes the spacing check count covered buttons as noise).
Soft-keyboard / Safari quirks / real safe-area pressure stay with the human device pass.

**When class names differ between the two sides (HTML→Vue scenario)**: a component
port rewrites class names (e.g. scoped-CSS transforms). Default auto-collection then
misfires (measured: renaming 73 structural classes → 71 selector mismatches, FAIL) —
but **the pixel layer is class-agnostic and stays 0.00%**, so in that scenario: treat
the pixel layer as the primary evidence, and pass `--selectors` with a mapping table
of selectors that exist on both sides (`#historyDrawer`, `[aria-label="…"]` — ids and
attribute selectors work; they are resolved in the page, not filtered from the class
universe). Measured: 12 mapped selectors × 21 properties, 0 diff → PASS.

## Example output format

```
## UI acceptance: <page/feature name>

✅ Pass
- Layout: overall structure matches the design, nothing misaligned
- Interaction: login → submit flow works, no JS errors

❌ Fail
- Text overflow: the "Submit" button is truncated at 375px width

Screenshot: <path>/verify-20260101.png
```

## Pitfall list (hit in practice — don't repeat)

- Full-page screenshot flag goes BEFORE the path; after the path it's treated as the filename
- Element refs expire after navigation / hot reload → re-snapshot before acting
- Fixed-position elements have offsetParent===null; don't use that to judge visibility
- A single eval over ~15s drags the debug channel to a halt → split into short commands
- Testing right after editing can be confused by hot reload (module state reset) → if results look weird, `location.reload()` and retest before concluding
- Browser commands hanging → check for session/process leftovers before retrying; don't blindly retry the same command
- Unsure about command syntax → check the tool's own docs; don't write commands from memory
