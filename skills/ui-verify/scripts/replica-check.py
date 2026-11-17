#!/usr/bin/env python3
"""ui-verify replica acceptance in one command: computed-style diff + pixel heatmap.

Usage:
    python replica-check.py <ref-demo-path-or-url> <replica-path-or-url>
        [--viewports 1920x1080,1366x768] [--out report-dir]
        [--selectors ".a,.b,..."] [--pixel-tolerance 0.0] [--session name]
        [--checks checks.json]

Layers (interaction comparison beyond the bundled checks is manual/semi-auto):
  1. Screenshot both pages at the same viewport
  2. Computed-style diff per element (auto-collects all class selectors, 21 key properties)
  3. Pixel diff + 10-band heatmap (same algorithm as diff.py)
  4. PASS/FAIL verdict (computed 0 diff AND pixel ratio <= --pixel-tolerance)
  5. Report written to --out dir (screenshots / heatmaps / diff details / summary.md)

Depends on: agent-browser (on PATH), Pillow. Before every screenshot all scrollable
containers are force-settled (scrollBehavior=auto + scroll to bottom) to prevent
smooth-scroll transient fake diffs (real pitfall hit 2026-11-16).
--checks format: [{"name":"drawer-toggle","js":"...string-returning expression..."}, ...];
each expression runs on both pages once, mismatched output = red.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageChops


def _resolve_ab_exe():
    """On Windows the npm .cmd shim routes args through cmd.exe, which mangles
    complex args containing newlines/quotes (eval JS silently returned null in
    practice) — resolve the native exe behind the shim and call it directly."""
    for cand in ('agent-browser', 'agent-browser.exe', 'agent-browser.cmd'):
        p = shutil.which(cand)
        if not p:
            continue
        if not p.lower().endswith('.cmd'):
            return p
        real = os.path.join(os.path.dirname(os.path.abspath(p)),
                            'node_modules', 'agent-browser', 'bin',
                            'agent-browser-win32-x64.exe')
        if os.path.exists(real):
            return real
        return p
    return 'agent-browser'


AB_EXE = _resolve_ab_exe()

PROPS = ['display', 'position', 'width', 'height', 'padding', 'margin',
         'fontSize', 'fontWeight', 'color', 'backgroundColor',
         'borderWidth', 'borderColor', 'borderRadius', 'boxShadow',
         'lineHeight', 'gap', 'flexDirection', 'justifyContent',
         'alignItems', 'overflowX', 'letterSpacing']

COLLECT_JS = """
(() => {
  const cap = 400, seen = new Set(), sels = [];
  document.querySelectorAll('*').forEach(el => {
    if (!el.className || typeof el.className !== 'string') return;
    el.className.split(/\\s+/).forEach(c => {
      c = c.trim();
      if (c && !seen.has(c)) { seen.add(c); sels.push('.' + c); }
    });
  });
  const out = {};
  for (const s of sels.slice(0, cap)) {
    const el = document.querySelector(s);
    if (!el) continue;
    const cs = getComputedStyle(el), o = {};
    for (const p of %PROPS%) o[p] = cs[p];
    out[s] = o;
  }
  return JSON.stringify(out);
})()
"""

SETTLE_JS = """
(() => {
  let n = 0;
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    if ((cs.overflowY === 'auto' || cs.overflowY === 'scroll') && el.scrollHeight > el.clientHeight) {
      el.style.scrollBehavior = 'auto';
      el.scrollTop = el.scrollHeight;
      n++;
    }
  });
  return 'settled=' + n;
})()
"""

# Custom-selector variant: resolved in the page itself (supports id/attribute
# selectors, not just classes)
COLLECT_CUSTOM_JS = """
(() => {
  const sels = %SELS%;
  const out = {};
  for (const s of sels) {
    let el = null;
    try { el = document.querySelector(s); } catch (e) {}
    if (!el) continue;
    const cs = getComputedStyle(el), o = {};
    for (const p of %PROPS%) o[p] = cs[p];
    out[s] = o;
  }
  return JSON.stringify(out);
})()
"""


def ab(args, session):
    env = dict(os.environ, AGENT_BROWSER_SESSION=session)
    r = subprocess.run([AB_EXE] + args, capture_output=True, text=True,
                       encoding='utf-8', env=env, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f'agent-browser {" ".join(args[:2])} failed: {r.stdout}\n{r.stderr}')
    return r.stdout.strip()


def to_url(target):
    if '://' in target:
        return target
    return 'file:///' + os.path.abspath(target).replace('\\', '/')


def ab_eval(js, session):
    raw = ab(['eval', js], session)
    try:
        val = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(val, str):
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            return val
    return val


def open_settle_shot(url, vp_w, vp_h, shot_path, session):
    ab(['open', url], session)
    ab(['set', 'viewport', str(vp_w), str(vp_h)], session)
    import time
    time.sleep(1.2)
    ab_eval(SETTLE_JS, session)
    time.sleep(0.3)
    ab(['screenshot', shot_path], session)


def collect_styles(url, vp_w, vp_h, shot_path, session, selectors=None):
    open_settle_shot(url, vp_w, vp_h, shot_path, session)
    if selectors:
        js = COLLECT_CUSTOM_JS.replace('%SELS%', json.dumps(selectors)).replace('%PROPS%', json.dumps(PROPS))
    else:
        js = COLLECT_JS.replace('%PROPS%', json.dumps(PROPS))
    return ab_eval(js, session)


def pixel_diff(impl_png, ref_png, threshold, heat_out):
    impl = Image.open(impl_png).convert('RGB')
    ref = Image.open(ref_png).convert('RGB')
    if impl.size != ref.size:
        ref = ref.resize(impl.size)
    d = ImageChops.difference(impl, ref).convert('L')
    w, h = d.size
    hist = d.histogram()
    ratio = sum(hist[threshold + 1:]) / (w * h)
    bands = []
    for i in range(10):
        top, bottom = h * i // 10, h * (i + 1) // 10
        bh = d.crop((0, top, w, bottom)).histogram()
        bands.append((top, bottom, sum(bh[threshold + 1:]) / (w * (bottom - top))))
    mask = d.point(lambda v: 140 if v > threshold else 0)
    heat = Image.composite(Image.new('RGB', impl.size, (255, 32, 32)), impl, mask)
    heat.save(heat_out)
    return ratio, bands


def main():
    p = argparse.ArgumentParser(description='Replica acceptance in one command (ui-verify)')
    p.add_argument('ref', help='reference demo (path or URL)')
    p.add_argument('rep', help='replica page (path or URL)')
    p.add_argument('--viewports', default='1920x1080,1366x768')
    p.add_argument('--out', default=None, help='report dir (default ./replica-check-report)')
    p.add_argument('--selectors', default=None, help='comma-separated selectors; default auto-collects class selectors from both pages')
    p.add_argument('--pixel-tolerance', type=float, default=0.0)
    p.add_argument('--diff-threshold', type=int, default=24, help='pixel grayscale diff threshold, default 24')
    p.add_argument('--session', default='replica-check', help='agent-browser session name')
    p.add_argument('--checks', default=None, help='interaction comparison JSON ([{"name","js"}]); runs on both pages, outputs must match')
    a = p.parse_args()

    out_dir = a.out or os.path.join(os.getcwd(), 'replica-check-report')
    os.makedirs(out_dir, exist_ok=True)
    ref_url, rep_url = to_url(a.ref), to_url(a.rep)
    vps = []
    for v in a.viewports.split(','):
        w, h = v.strip().lower().split('x')
        vps.append((int(w), int(h)))

    lines = [f'# replica-check report', f'- ref: {a.ref}', f'- rep: {a.rep}',
             f'- viewports: {a.viewports}', '']
    verdict_all = True

    for w, h in vps:
        tag = f'{w}x{h}'
        print(f'== viewport {tag} ==')
        custom = None
        if a.selectors:
            custom = [s.strip() for s in a.selectors.split(',') if s.strip()]
        ref_styles = collect_styles(ref_url, w, h, os.path.join(out_dir, f'ref-{tag}.png'), a.session, custom)
        rep_styles = collect_styles(rep_url, w, h, os.path.join(out_dir, f'rep-{tag}.png'), a.session, custom)

        rs, ps = ref_styles, rep_styles
        style_diffs = []
        for sel, rprops in rs.items():
            if rprops is None or ps.get(sel) is None:
                style_diffs.append(f'{sel} :: <missing> ref={rprops is not None} rep={ps.get(sel) is not None}')
                continue
            for prop, rv in rprops.items():
                mv = ps[sel].get(prop)
                if rv != mv:
                    style_diffs.append(f'{sel} :: {prop} :: ref={rv!r} rep={mv!r}')

        ratio, bands = pixel_diff(os.path.join(out_dir, f'rep-{tag}.png'),
                                  os.path.join(out_dir, f'ref-{tag}.png'),
                                  a.diff_threshold, os.path.join(out_dir, f'heat-{tag}.png'))

        check_rows = []
        if a.checks:
            checks = json.load(open(a.checks, encoding='utf-8'))
            for c in checks:
                open_settle_shot(ref_url, w, h, os.path.join(out_dir, f'_r.png'), a.session)
                rv = ab_eval(c['js'], a.session)
                open_settle_shot(rep_url, w, h, os.path.join(out_dir, f'_p.png'), a.session)
                pv = ab_eval(c['js'], a.session)
                ok = json.dumps(rv, sort_keys=True, default=str) == json.dumps(pv, sort_keys=True, default=str)
                check_rows.append((c['name'], ok, f'ref={rv!r} rep={pv!r}'))

        n_sel = sum(1 for v in rs.values() if v is not None)
        vp_ok = not style_diffs and ratio <= a.pixel_tolerance and all(ok for _, ok, _ in check_rows)
        verdict_all = verdict_all and vp_ok
        status = 'PASS' if vp_ok else 'FAIL'
        print(f'[{tag}] {status}: computed {n_sel} selectors x {len(PROPS)} props, {len(style_diffs)} diffs | '
              f'pixel {ratio:.2%} (tolerance {a.pixel_tolerance:.2%}) | interactions {sum(1 for _, ok, _ in check_rows if ok)}/{len(check_rows)} pass')
        for bd in style_diffs[:30]:
            print(f'  ~ {bd}')
        if len(style_diffs) > 30:
            print(f'  ...{len(style_diffs) - 30} more diffs')
        if ratio > a.pixel_tolerance:
            for top, bottom, br in bands:
                if br > 0:
                    print(f'  hotspot band y{top}-{bottom}: {br:.2%} (see heat-{tag}.png)')
        for name, ok, detail in check_rows:
            print(f'  {"√" if ok else "×"} {name}' + ('' if ok else f' :: {detail}'))

        lines += [f'## {tag}: {status}',
                  f'- computed styles: {n_sel} selectors x {len(PROPS)} props, {len(style_diffs)} diffs',
                  f'- pixel: {ratio:.2%} (heatmap heat-{tag}.png)']
        lines += [f'- {d}' for d in style_diffs]
        lines += [f'- {"√" if ok else "×"} {name} {detail}' for name, ok, detail in check_rows]
        lines.append('')

    lines.insert(4, f'## Verdict: {"PASS" if verdict_all else "FAIL"}')
    report_path = os.path.abspath(os.path.join(out_dir, "summary.md"))
    print(f"\nVerdict: {'PASS' if verdict_all else 'FAIL'} | report: {report_path}")
    with open(os.path.join(out_dir, 'summary.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return 0 if verdict_all else 1


if __name__ == '__main__':
    sys.exit(main())
