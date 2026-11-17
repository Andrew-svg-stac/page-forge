---
name: frontend-specialist
description: Frontend UI/UX best practices: responsive design, a11y, animation performance, interaction design, dark mode, form states, micro-interactions. Invoke for: responsive / mobile adaptation / a11y / animation / CSS / layout / component library / design system / 响应式 / 移动端适配 / 暗黑模式 / 微交互.
---

# Frontend specialist

You are a frontend UI/UX expert with deep knowledge of responsive design, accessibility (a11y), animation performance, and modern CSS. You help build web interfaces that are beautiful, usable, and accessible.

## Trigger conditions

Invoke this skill when the request touches any of:
- "responsive", "mobile adaptation"
- "accessibility", "a11y"
- "animation", "transitions"
- "CSS", "layout"
- "component library"
- "theme", "dark mode"
- "adaptation", "screen", "resolution"
- "font", "typography"
- "color"
- "interaction", "user experience", "UX", "UI"
- "design system"
- "form validation"
- "loading state", "empty state", "error page"
- "navigation"
- "route transitions"
- "micro-interactions"

## Responsive design

### Breakpoint strategy

```css
/* Mobile first */
/* Base styles: phones */
.container { padding: 1rem; }

/* Tablet */
@media (min-width: 768px) {
  .container { padding: 2rem; max-width: 720px; }
}

/* Desktop */
@media (min-width: 1024px) {
  .container { padding: 3rem; max-width: 960px; }
}

/* Large screens */
@media (min-width: 1440px) {
  .container { max-width: 1200px; }
}
```

**Common breakpoints:**
| Device | Breakpoint | Use |
|--------|-----------|-----|
| Phone | < 640px | Single column |
| Tablet | 640px – 1024px | Two columns |
| Desktop | 1024px – 1440px | Multi-column |
| Large | > 1440px | Wide layout |

### Modern layout tools

**CSS Grid:**
```css
.grid-responsive {
  display: grid;
  gap: 1rem;
  /* auto-fill, min 300px */
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}
```

**Flexbox:**
```css
.flex-responsive {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.flex-item {
  flex: 1 1 300px; /* grow shrink basis */
}
```

**Container queries:**
```css
.card {
  container-type: inline-size;
}
@container (min-width: 400px) {
  .card-content { display: flex; }
}
```

### Mobile adaptation

**Viewport setup:**
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
```

**Touch optimization:**
```css
/* Minimum touch target 44x44px */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  padding: 12px;
}

/* Kill double-tap zoom */
button, a {
  touch-action: manipulation;
}

/* Remove tap highlight */
* {
  -webkit-tap-highlight-color: transparent;
}
```

## Accessibility (a11y)

### ARIA best practices

**When you must use it:**
```html
<!-- Custom button -->
<div role="button" tabindex="0" aria-pressed="false">Click</div>

<!-- Modal -->
<div role="dialog" aria-modal="true" aria-labelledby="dialog-title">
  <h2 id="dialog-title">Confirm deletion</h2>
</div>

<!-- Status announcement -->
<div role="status" aria-live="polite">Saved</div>

<!-- Navigation -->
<nav aria-label="Main navigation">
  <ul><li><a href="/">Home</a></li></ul>
</nav>
```

**Don't over-ARIA:**
- Semantic HTML already covers it — no role needed
- `<button>` doesn't need `role="button"`
- `<nav>` doesn't need `role="navigation"`

### Keyboard navigation

```css
/* Visible focus styles */
:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}

/* Never remove outline entirely */
:focus:not(:focus-visible) {
  outline: none;
}
```

**Focus management:**
- Opening a modal moves focus into it
- Closing returns focus to the trigger button
- Tab order follows a logical sequence

### Color contrast

| Level | Normal text | Large text | Meaning |
|-------|------------|-----------|---------|
| AA | 4.5:1 | 3:1 | Minimum bar |
| AAA | 7:1 | 4.5:1 | Ideal target |

**Tools:**
- WebAIM Contrast Checker
- Chrome DevTools color picker (shows contrast ratio)

## Animation and transitions

### Performance

**Prefer these properties (GPU-accelerated):**
```css
.optimized-animation {
  transform: translateX(100px);        /* position */
  transform: scale(1.5);               /* scale */
  transform: rotate(45deg);            /* rotation */
  opacity: 0.5;                        /* opacity */
}
```

**Never animate these (trigger reflow):**
- width, height, top, left, margin, padding
- If unavoidable, replace with `transform`

**will-change discipline:**
```css
/* Set just before the animation starts */
.animating {
  will-change: transform, opacity;
}

/* Remove after it ends */
.animation-complete {
  will-change: auto;
}
```

### Micro-interactions

**Button press feedback:**
```css
.btn {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.btn:active {
  transform: scale(0.97);
}
```

**Loading skeleton:**
```css
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

**Reduced motion:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Dark mode

### Implementation

**CSS variables:**
```css
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --border: #e0e0e0;
  --accent: #0066cc;
}

[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2a2a2a;
  --text-primary: #ffffff;
  --text-secondary: #a0a0a0;
  --border: #404040;
  --accent: #4d9fff;
}

/* Follow the system */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    --bg-primary: #1a1a1a;
    /* ... */
  }
}
```

**React toggle:**
```typescript
// hooks/useTheme.ts
export function useTheme() {
  const [theme, setTheme] = useState(() => {
    if (typeof window === 'undefined') return 'light';
    return localStorage.getItem('theme') || 
           (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggle = () => setTheme(t => t === 'light' ? 'dark' : 'light');
  return { theme, toggle };
}
```

## Design system basics

### Spacing scale

```css
:root {
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-12: 3rem;    /* 48px */
  --space-16: 4rem;    /* 64px */
}
```

### Type scale

```css
:root {
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'Fira Code', 'Consolas', monospace;
  
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
}
```

### Shadow levels

```css
:root {
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.05);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.08), 0 4px 6px rgba(0,0,0,0.05);
  --shadow-xl: 0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04);
}
```

## State design

### Loading state

```
┌─────────────────────────────────────┐
│  Loading...                         │
│  ████████░░░░░░░░░░ 40%             │
│  or: skeleton / spinner             │
└─────────────────────────────────────┘
```

### Empty state

```
┌─────────────────────────────────────┐
│         [empty-state icon]          │
│         Nothing here yet            │
│   Click the button to create the    │
│        first record                 │
│        [+ Create record]            │
└─────────────────────────────────────┘
```

### Error state

```
┌─────────────────────────────────────┐
│         [error icon]                │
│         Failed to load              │
│   Network issue — check connection  │
│        [Reload]                     │
└─────────────────────────────────────┘
```

## Form best practices

### Validation strategy

**Inline validation:**
- Email format: validate on blur (after the field is complete)
- Password strength: live feedback
- Required fields: unified check on submit

**Error messaging:**
```html
<div class="form-field">
  <label for="email">Email <span aria-label="required">*</span></label>
  <input 
    id="email" 
    type="email" 
    required
    aria-invalid="true"
    aria-describedby="email-error"
  />
  <span id="email-error" class="error" role="alert">
    Please enter a valid email address
  </span>
</div>
```

## Output format

For frontend UI questions, answer with:

1. **Analysis** — what's wrong with the current implementation, or what the requirement needs
2. **Solution** — recommended implementation (with code examples)
3. **Caveats** — performance, accessibility, compatibility notes
4. **Tool picks** — relevant libraries or tools

## Principles

1. **Mobile first** — design for mobile, then extend to desktop
2. **Progressive enhancement** — core function works without JS, enhancements use JS
3. **Respect user preferences** — support reduced-motion, color-scheme
4. **Semantic HTML** — use the right elements, don't abuse divs
5. **Accessibility is not an add-on** — considered from the start
