# Motion presets (P3 library)

Copy-paste GSAP 3 skeletons for the four most requested motion patterns.
Loaded on demand by P3 — do not inline into SKILL.md.

## Global rules (apply to every preset)

- Animate **transform and opacity only**. Layout properties (width/top/margin) cause reflow jank.
- Respect reduced motion — wrap everything:

```js
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (reduced) { /* set final state, skip animation */ }
```

- Run inside `gsap.context()` and revert it on unmount (React/Vue) to avoid leaks.
- Call `ScrollTrigger.refresh()` after webfonts load (`document.fonts.ready.then(...)`), or triggers misalign.
- One motion idea per page section. If two presets fight, delete one.

---

## Preset 1 — Hero entrance (first viewport reveal)

**When**: marketing/landing hero, one-time on load. Sets the tone in <1s.

```html
<!-- Structure: each line wrapped so overflow hides the reveal -->
<h1 class="hero-line"><span class="hero-inner">Ship pages that</span></h1>
<h1 class="hero-line"><span class="hero-inner">don't look AI-made</span></h1>
<p class="hero-sub">Open-source pipeline · MIT</p>
```

```js
if (reduced) {
  gsap.set(['.hero-inner', '.hero-sub'], { yPercent: 0, opacity: 1 });
} else {
  gsap.set('.hero-line', { overflow: 'hidden' });
  gsap.timeline({ defaults: { ease: 'power3.out' } })
    .from('.hero-inner', { yPercent: 110, duration: 0.9, stagger: 0.12 })
    .from('.hero-sub',  { opacity: 0, y: 16, duration: 0.6 }, '-=0.4');
}
```

| Dial | Default | Range | Effect |
|---|---|---|---|
| stagger | 0.12 | 0.08–0.2 | line cadence; higher = calmer |
| ease | power3.out | power2–4.out | sharper = lower number |
| yPercent | 110 | 100–130 | reveal travel distance |

**Pitfalls**: `overflow:hidden` must be on the wrapper, not the text node. Don't add scale to text reveals — it reads as template-y.

---

## Preset 2 — Scroll narrative (pinned storytelling)

**When**: explaining a process/product story in 3–5 steps while the user scrolls. The signature "premium" pattern.

```html
<section class="story">
  <div class="story-steps">      <!-- pinned; steps swap inside -->
    <div class="story-step" data-step="0">Step one copy</div>
    <div class="story-step" data-step="1">Step two copy</div>
    <div class="story-step" data-step="2">Step three copy</div>
  </div>
  <div class="story-visual"></div> <!-- pinned; crossfades per step -->
</section>
```

```js
if (!reduced) {
  const steps = gsap.utils.toArray('.story-step');
  gsap.set(steps, { opacity: 0, y: 24 });
  gsap.set(steps[0], { opacity: 1, y: 0 });

  ScrollTrigger.create({
    trigger: '.story',
    start: 'top top',
    end: () => '+=' + steps.length * 500,   // 500px scroll per step
    pin: '.story-steps',
    scrub: true,
    onUpdate: (self) => {
      const i = Math.min(steps.length - 1, Math.floor(self.progress * steps.length));
      steps.forEach((s, idx) => s.classList.toggle('is-active', idx === i));
    },
  });
}
```

```css
.story-step { position: absolute; inset: 0; transition: opacity 0.35s ease-out; }
.story-step.is-active { opacity: 1; }
```

| Dial | Default | Range | Effect |
|---|---|---|---|
| px per step | 500 | 350–700 | reading time per step |
| pin | .story-steps | any stable wrapper | what stays fixed |

**Pitfalls**: `end` must be a **function** so it recalculates on resize. Only one pinned section per page on mobile — two pins on touch = scroll traps. Test with the browser's touch emulation.

---

## Preset 3 — Micro-interactions (hover / press feedback)

**When**: every interactive surface. This is "手感", not decoration. All <300ms.

```css
/* Press: the single highest-value line in this file */
.button { transition: transform 120ms ease-out; }
.button:active { transform: scale(0.97); }

/* Card lift: shadow + translate, nothing else */
.card { transition: transform 200ms ease-out, box-shadow 200ms ease-out; }
.card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgb(0 0 0 / 12%); }

/* Focus ring that doesn't vanish */
:focus-visible { outline: 2px solid currentColor; outline-offset: 3px; }
```

```js
// Magnetic button — optional flourish, pointer devices only
if (!reduced && matchMedia('(pointer: fine)').matches) {
  document.querySelectorAll('[data-magnet]').forEach((el) => {
    el.addEventListener('pointermove', (e) => {
      const r = el.getBoundingClientRect();
      gsap.to(el, {
        x: (e.clientX - r.left - r.width / 2) * 0.25,
        y: (e.clientY - r.top - r.height / 2) * 0.25,
        duration: 0.3, ease: 'power2.out',
      });
    });
    el.addEventListener('pointerleave', () =>
      gsap.to(el, { x: 0, y: 0, duration: 0.4, ease: 'elastic.out(1, 0.5)' }));
  });
}
```

**Pitfalls**: magnetic pull factor ≤0.3 or it feels broken. Never magnetize inputs or nav links. `:active scale` needs `touch-action: manipulation` on mobile to avoid 300ms delay.

---

## Preset 4 — Count-up stats

**When**: numbers/metrics section. Animate **once** when scrolled into view — re-triggering on scroll-back screams template.

```html
<div class="stat"><span class="stat-num" data-count="1200" data-suffix="+">0</span><span class="stat-label">pages shipped</span></div>
```

```js
document.querySelectorAll('.stat-num').forEach((el) => {
  const end = parseFloat(el.dataset.count);
  const suffix = el.dataset.suffix || '';
  const obj = { v: 0 };
  if (reduced) { el.textContent = end.toLocaleString() + suffix; return; }
  gsap.to(obj, {
    v: end,
    duration: 1.4,
    ease: 'power2.out',       // fast start, decel landing — reads as "settling"
    snap: { v: 1 },
    scrollTrigger: { trigger: el, start: 'top 85%', once: true },
    onUpdate: () => { el.textContent = Math.round(obj.v).toLocaleString() + suffix; },
  });
});
```

| Dial | Default | Range | Effect |
|---|---|---|---|
| duration | 1.4 | 1–2 | >2s feels laggy |
| once | true | — | keep it true |
| start | top 85% | top 75–90% | trigger earliness |

**Pitfalls**: use a proxy object + `onUpdate` (as above), not `innerText` tweening. Locale-format with `toLocaleString()` or thousands separators flicker. Decimal stats: drop `snap` and fix decimals in `onUpdate`.

---

## Choosing presets (P3 decision rule)

| Brief says | Use |
|---|---|
| "第一印象要惊艳" / striking first impression | 1 + 3 |
| "讲清楚流程/产品故事" | 2 + 3 |
| "要有数据说服力" | 4 + 3 |
| "要手感" | 3 alone |

Never stack 1+2+4 on one page. Motion budget: **one signature pattern + micro-interactions**. The rest is typography.
