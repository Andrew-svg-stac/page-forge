# quality-loop — screenshot-score-fix loop + media shelf mechanism

> Optional P4 enhancement for new-build / redo page tasks. It scores and iterates on
> *polish*; correctness acceptance (broken layout, console errors, failed flows)
> stays with `ui-verify`. If the loop finds a correctness problem, route it back
> through ui-verify first.

## 1. The screenshot-score-fix loop

Run after the anti-slop self-check and the interface safety checklist in P4.
Default on for new builds and redesigns; skip for purely functional admin pages.

### 1.1 Blockers — fix before scoring (any one fails → repair first)

- Console errors / failed asset requests / a video or animated background that should play but doesn't
- Horizontal overflow on mobile (`scrollWidth > innerWidth`)
- White flash on dark designs in the first paint (page background not set on `html, body` as the first CSS rule)
- Body text unreadable over imagery, or contrast below 4.5:1
- Display font not loaded (headline falls back to a system font)
- Broken layout: elements overlapping that shouldn't, nav wrapping to two lines, hero CTA pushed out of the viewport
- Placeholder copy (Lorem ipsum, "Your tagline here", "Feature 1")

### 1.2 Score on ten dimensions (1–10 each, honestly, like a jury member)

| # | Dimension | What to look at |
|---|---|---|
| 1 | First glance | The 3-second test: one focal point, you know where to look, feels intentional — studio work, not a template |
| 2 | Signature | One thing worth screenshotting and sharing (media, interaction, or a type moment) |
| 3 | Typography | Display type big, confident, tightly tracked; body calm and readable; ≤2 families; nothing default-looking |
| 4 | Composition & space | Deliberate negative space; eye travels hero → message → CTA; no clutter, no orphaned elements |
| 5 | Colour & light | Small palette, one accent used with intent; text protected over media; depth from layering, not decoration |
| 6 | Media integration | Image/video/3D feels part of the design (crop, position, layering on purpose), not a rectangle dropped in |
| 7 | Motion | Choreographed entrance (staggered, 0.6–1.2s, ease-out); physical interactions; no distracting loops; reduced-motion respected |
| 8 | Mobile | Not just stacked: type rescaled, media re-cropped, tap targets ≥44px, the signature survives |
| 9 | Copy | Short, specific, has a point of view; verb-first CTA; zero filler |
| 10 | Polish | Hover/focus states, consistent radii, favicon/title, no stray scrollbars, no layout shift on load |

**The bar: average ≥8 with no dimension under 7.** First drafts usually land at 6–7 —
that's normal; the fixing is where the value is.

### 1.3 The fix loop (max 3 rounds)

1. Pick the **three weakest dimensions**; write a concrete, value-carrying change for each (no adjectives):
   - Good: "H1 from 64px to `clamp(56px, 8vw, 128px)`, tracking −0.04em"
   - Bad: "make the headline bolder"
2. Fix → re-screenshot → re-look → re-score
3. Still below the bar after 3 rounds: stop, hand the score table and blockers to the
   user — User Gate B is a human decision anyway
4. High-frequency fixes: looks generic → bigger type, fewer words, stronger signature, cut a section;
   looks busy → remove decoration, unify radii, one step more whitespace, palette down to bg/ink/muted/accent;
   looks flat → add a media layer, scrim, subtle grain, or glass surface;
   text fights media → move text to the calm zone or add a scrim;
   mobile broken → re-crop with `object-position`, `clamp()` the type, collapse secondary nav into a menu

## 2. Media shelf mechanism (stop hunting for assets every build)

### The mechanism (reusable pattern, not any specific stockpile)

1. **Three pieces**: a `MEDIA.md` index table (number / type / size / source / URL) +
   numbered **contact sheets** (thumbnail boards so a human or a model can pick by eye) +
   the assets themselves hosted remotely (pages reference URLs; the shelf never lives inside project repos)
2. **Selection discipline**: browse the contact sheet first, then take the exact URL from
   `MEDIA.md` by number. **The index table is the source of truth for numbering** — picking
   from thumbnail row-memory caused a real mismatch (a bright keyboard clip taken for a
   dark silk ribbon; same shelf, adjacent numbers, opposite moods)
3. **Sourcing rules**: free/commercial-usable licenses, reachable from your network, and
   stylistically coherent (one shelf = one mood; don't collage across shelves)

### Optional ready-made shelf

If the [Motionsites-AI/claude-skill](https://github.com/Motionsites-AI/claude-skill) skill is
installed locally, its media shelf (50+ cinematic hero videos, transparent 3D cut-outs,
images, publicly hosted) can serve as a ready-made shelf for cinematic hero work — respect
its license terms (shelf content remains © MotionSites; usable in sites built with that
skill; keep shelf files where they are, never copy them into repos). User-owned assets
always come first; lawful free sources (Unsplash / Pexels / Pixabay) are the fallback for
building your own shelf.
