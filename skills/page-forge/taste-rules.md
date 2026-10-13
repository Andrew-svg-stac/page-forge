# taste-rules — anti-slop style rules (built into page-forge)

> This is a condensed rewrite. For methodology sources and credits see the Credits section of the repo README.
> Three parts: taste dials (P1) → hard rules (P2) → motion principles & delivery checklist (P3/P4).

## 1. The three taste dials (set in P1)

Read the requirements and set three dials first; every later layout / motion / density decision is driven by them:

| Dial | 1 | 10 | Baseline |
|---|---|---|---|
| Layout variance DESIGN_VARIANCE | fully symmetric | artful asymmetry | 8 |
| Motion intensity MOTION_INTENSITY | static | cinematic / physical | 6 |
| Visual density VISUAL_DENSITY | gallery whitespace | cockpit density | 4 |

Adjust by requirement signal (explicit user words beat inference):

| Signal | Variance | Motion | Density |
|---|---|---|---|
| Minimal / calm / editorial | 5-6 | 3-4 | 2-3 |
| Premium consumer brand / Apple-like | 7-8 | 5-7 | 3-4 |
| Playful / Dribbble / agency | 9-10 | 8-10 | 3-4 |
| Landing page / portfolio (default) | 7-9 | 6-8 | 3-5 |
| Trust-first / government / accessibility-critical | 3-4 | 2-3 | 4-5 |
| Redo — keep the tone | keep current | +1 | keep current |
| Redo — start fresh | +2 | +2 | keep current |

## 2. Anti-slop hard rules (check one by one in P2; any violation = rework)

1. **Brand color only where it belongs** — buttons / selected states / links / key progress. Large brand-color areas in content regions = violation. Black/white/gray base + one accent.
2. **No gradients in content areas**, no glassmorphism, no glowing borders (gradient-strokeed cards become white cards + semantic-color side bars). Brand gradients stay only on existing brand assets like the logo.
3. **No equal-width identical card grids** — three or four identical cards in a row is the signature fingerprint of AI-generated pages. There must be hierarchy (one card enlarged, merged, or turned into a list).
4. **No emoji as icons** — use a consistent line icon set (lucide-style), currentColor following the text color.
5. **Check the typography trio**: ≤5 font-size steps with body ≥14px (auxiliary ≥12px); hierarchy via 400/600/700 weights, never just "smaller + grayer"; body line-height 1.5-1.7.
6. **Calibrate color**: neutral scale leans blue-gray, not pure gray; restrained saturation (use 8-10% alpha of the primary for 60%+ surfaces); semantic colors limited to success green / warning amber / danger red, everything else in grays; labels always light background + dark text.
7. **Copy that feels real**: no Lorem, no filler phrases ("empower · lead · enable"), no marketing triplets ("auto-X · auto-Y · auto-Z"). Write something specific, with numbers, with a human voice.
8. **Spacing on a scale system** (4/8 base), tight spacing inside components, generous between them — group by spacing, not by borders.
9. **Material feel**: shadows in two layers (near small shadow for hierarchy + far large shadow for elevation); 1px borders in light gray; ≤3 border-radius steps, consistent site-wide.
10. **Content density**: one visual focal point above the fold; don't stuff everything into the hero. Design empty states (gray icon + one sentence); no bare placeholders.

## 3. Motion principles (P3)

- Duration: UI feedback <150ms, enter/exit <300ms, never over 500ms
- Easing: ease-out for entrances, ease-in acceptable for exits; bounce comes from cubic-bezier, not from longer durations
- Animate only transform and opacity (compositor-friendly), never top/left/width/height
- Buttons get `:active { transform: scale(0.97) }` for tactile feedback
- Every motion effect must state its purpose (guide the eye / confirm an action / express spatial relation); if you can't, delete it
- Under `@media (prefers-reduced-motion: reduce)`, all motion degrades to instant state changes

## 4. Pre-delivery checklist (P4 safety net, MUST items)

- [ ] Keyboard reachable: sensible Tab order, visible focus on all interactive elements (focus-visible styles)
- [ ] Touch targets ≥24×24px (44 recommended)
- [ ] Forms: labels associated, clear error states, correct autocomplete
- [ ] Dark mode doesn't break (if present): contrast passes, images not glaring
- [ ] No overflow or horizontal scroll at 375px mobile width
- [ ] Images have alt, semantic tags (nav/main/button, not a mountain of divs)
- [ ] Build has zero errors, console has no red errors
