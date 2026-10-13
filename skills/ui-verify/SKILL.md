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
