/* openTagCloud vanilla (UMD/global) build — see src/lib/vanilla.js for the
   authored ESM source. Load via <script src="opentagcloud.vanilla.js"></script>
   then call openTagCloud.mount(el, items, opts). Also works as CommonJS/AMD. */
(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined'
    ? (module.exports = factory())
    : typeof define === 'function' && define.amd
      ? define(factory)
      : ((global = typeof globalThis !== 'undefined' ? globalThis : global || self),
         (global.openTagCloud = factory()));
})(this, function () {
  'use strict';

/**
 * openTagCloud — framework-agnostic (vanilla JS) build.
 *
 * A dependency-free port of the Svelte 5 <TagCloud> component's layout engine
 * so the cloud can be used in plain HTML, or from any framework, without a
 * Svelte/build toolchain. The packing algorithm (seeded scatter + spiral) is
 * identical to the component; only the render/lifecycle glue is vanilla.
 *
 * Usage (ESM):
 *   import { mount } from 'opentagcloud/vanilla';
 *   const cloud = mount(document.getElementById('cloud'), items, { minPx: 14, maxPx: 44 });
 *   cloud.update(newItems);  // re-render
 *   cloud.destroy();         // tear down observers + DOM
 *
 * Usage (script tag):
 *   <script src="opentagcloud.vanilla.js"></script>
 *   openTagCloud.mount(el, items, opts);
 *
 * `items` is an array of { label, weight, href?, id?, title?, color?, class? }
 * (see the TagCloudItem type). Give the container a size; the cloud fills it.
 */

const STYLE_ID = 'otc-vanilla-styles';
const CSS = `
.otc-cloud { position: relative; flex: 1 1 auto; min-height: 0; }
.otc-cloud .tag {
  display: inline-block; line-height: 0.95; text-align: center; font-weight: 700;
  color: var(--otc-tag-color, var(--otc-color, currentColor));
  overflow-wrap: normal; word-break: normal; hyphens: none; text-decoration: none;
  transition: color var(--otc-transition, 150ms ease), opacity var(--otc-transition, 150ms ease);
}
.otc-cloud a.tag:hover, .otc-cloud a.tag:focus-visible {
  color: var(--otc-tag-color, var(--otc-hover-color, #2563eb)); opacity: 1 !important; text-decoration: none;
}
.otc-cloud:not(.packed) { text-align: justify; text-align-last: justify; line-height: 1.15; }
.otc-cloud:not(.packed) .tag { margin: 0.18em 0.3em; max-width: min(6.5em, 100%); vertical-align: middle; }
`;

function injectStyles(doc) {
  if (doc.getElementById(STYLE_ID)) return;
  const el = doc.createElement('style');
  el.id = STYLE_ID;
  el.textContent = CSS;
  doc.head.appendChild(el);
}

// Deterministic per-term RNG (seeded by the tag's key) — identical to the
// component, so a given item set always scatters the same way.
function makeRng(seed) {
  let h = 1779033703 ^ seed.length;
  for (let i = 0; i < seed.length; i++) {
    h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  let s = h >>> 0;
  return () => {
    s = Math.imul(s ^ (s >>> 15), 1 | s) >>> 0;
    s = (s + Math.imul(s ^ (s >>> 7), 61 | s)) >>> 0;
    return ((s ^ (s >>> 14)) >>> 0) / 4294967296;
  };
}

const keyOf = (t) => (t.id != null ? t.id : t.label);
// Render hyphens as non-breaking hyphens so multi-word tags don't wrap on them.
const nbLabel = (name) => name.replace(/-/g, '‑');

/**
 * Mount a tag cloud into `container`.
 * @param {HTMLElement} container A sized element to fill.
 * @param {Array} items Tag items.
 * @param {{minPx?:number,maxPx?:number,fill?:'width'|'height'|'both'}} [options]
 * @returns {{update:(items:Array)=>void, repack:()=>void, destroy:()=>void, el:HTMLElement}}
 */
function mount(container, items, options) {
  if (!container) throw new Error('openTagCloud.mount: container is required');
  const opts = options || {};
  const minPx = opts.minPx != null ? opts.minPx : 12;
  const maxPx = opts.maxPx != null ? opts.maxPx : 40;
  const fill = opts.fill;
  const fillH = fill === 'height' || fill === 'both';

  const doc = container.ownerDocument || document;
  injectStyles(doc);

  const root = doc.createElement('div');
  root.className = 'otc-cloud';
  container.appendChild(root);

  // Font ramp constants (identical to the component).
  const EXP = 1.9;
  const FLOOR = 9;

  let current = items ? items.slice() : [];
  let maxW = 1;
  let countFactor = 1;

  function lengthFactor(name) {
    const chars = name.length;
    const longest = Math.max.apply(null, name.split(/\s+/).map((w) => w.length));
    return Math.max(
      0.45,
      Math.min(Math.min(1, 15 / Math.max(15, chars)), 11 / Math.max(11, longest)),
    );
  }
  const fontPx = (w, name) => {
    const ramp = minPx + Math.pow(w / maxW, EXP) * (maxPx - minPx);
    return Math.max(FLOOR, ramp * countFactor * lengthFactor(name));
  };
  const widthFactor = (w) => Math.min(1.25, Math.max(0.72, w / 460));
  const opacity = (w) => 0.62 + Math.pow(w / maxW, 0.8) * 0.38;

  let lastW = -1;
  let lastH = -1;
  let base = [];
  let packH = 0;
  const PAD = 5;

  function render() {
    maxW = Math.max.apply(null, [1].concat(current.map((t) => t.weight)));
    countFactor = Math.min(1.1, Math.max(0.5, Math.sqrt(18 / Math.max(1, current.length))));

    root.classList.remove('packed');
    root.style.minHeight = '';
    root.textContent = '';
    for (const t of current) {
      const fs = fontPx(t.weight, t.label).toFixed(1);
      const tag = doc.createElement(t.href ? 'a' : 'span');
      tag.className = 'tag' + (t.class ? ' ' + t.class : '');
      tag.dataset.fs = fs;
      tag.style.fontSize = fs + 'px';
      tag.style.opacity = opacity(t.weight).toFixed(2);
      if (t.color) tag.style.setProperty('--otc-tag-color', t.color);
      tag.title = t.title != null ? t.title : String(t.weight);
      if (t.href) tag.setAttribute('href', t.href);
      tag.textContent = nbLabel(t.label);
      root.appendChild(tag);
    }
    pack();
  }

  function pack() {
    const tags = Array.prototype.slice.call(root.querySelectorAll('.tag'));
    if (!tags.length) return;
    const W = root.clientWidth;
    if (W < 2) return;
    lastW = W;

    root.classList.remove('packed');
    for (const el of tags) {
      el.style.position = '';
      el.style.left = '';
      el.style.top = '';
    }

    const wide = W >= 380;
    for (const el of tags) {
      el.style.whiteSpace = wide ? 'nowrap' : 'normal';
      el.style.maxWidth = wide ? Math.round(W * 0.6) + 'px' : 'min(6.5em, 100%)';
      el.style.fontSize =
        Math.max(8, parseFloat(el.dataset.fs || '12') * widthFactor(W)).toFixed(1) + 'px';
    }

    let dims = tags.map((el) => ({ el, w: el.offsetWidth, h: el.offsetHeight }));
    const area = dims.reduce((s, d) => s + (d.w + PAD) * (d.h + PAD), 0);
    const LOOSEN = 1.4;
    const availH = (area * LOOSEN) / W;

    for (const d of dims) {
      if (d.w > W) {
        const cur = parseFloat(d.el.style.fontSize) || 12;
        d.el.style.fontSize = Math.max(9, cur * (W / d.w)).toFixed(1) + 'px';
        d.w = d.el.offsetWidth;
        d.h = d.el.offsetHeight;
      }
    }

    const n = dims.length;
    const boxH = Math.max(availH, 1);
    const aspect = W / boxH;
    const cols = Math.max(1, Math.round(Math.sqrt(n * aspect)));
    const rows = Math.max(1, Math.ceil(n / cols));
    const cellW = W / cols;
    const cellH = boxH / rows;
    const cells = [];
    for (let r = 0; r < rows; r++)
      for (let c = 0; c < cols; c++) cells.push({ x: (c + 0.5) * cellW, y: (r + 0.5) * cellH });

    const cx0 = W / 2;
    const cy0 = boxH / 2;
    const remaining = cells.slice();
    const ordered = [];
    remaining.sort((a, b) => Math.hypot(a.x - cx0, a.y - cy0) - Math.hypot(b.x - cx0, b.y - cy0));
    ordered.push(remaining.shift());
    while (remaining.length) {
      let bi = 0;
      let bd = -1;
      for (let i = 0; i < remaining.length; i++) {
        let md = Infinity;
        for (const o of ordered) md = Math.min(md, Math.hypot(remaining[i].x - o.x, remaining[i].y - o.y));
        if (md > bd) {
          bd = md;
          bi = i;
        }
      }
      ordered.push(remaining.splice(bi, 1)[0]);
    }

    const order = dims.map((_, i) => i).sort((a, b) => current[b].weight - current[a].weight);
    const placed = [];
    const hits = (x, y, w, h) =>
      placed.some(
        (r) => x < r.x + r.w + PAD && x + w + PAD > r.x && y < r.y + r.h + PAD && y + h + PAD > r.y,
      );

    const pos = new Array(n);
    let maxY = 0;
    order.forEach((idx, rank) => {
      const { w, h } = dims[idx];
      const a = ordered[rank % ordered.length];
      const rand = makeRng(keyOf(current[idx]));
      let angle = rand() * Math.PI * 2;
      let radius = 0;
      let x = a.x - w / 2;
      let y = a.y - h / 2;
      let steps = 0;
      while (true) {
        x = a.x - w / 2 + radius * Math.cos(angle);
        y = a.y - h / 2 + radius * Math.sin(angle);
        x = Math.max(0, Math.min(x, W - w));
        if (y < 0) y = 0;
        if (!hits(x, y, w, h)) break;
        angle += 0.5;
        radius += Math.max(3, Math.min(cellW, cellH) * 0.12);
        if (++steps > 4000) break;
      }
      placed.push({ x, y, w, h });
      pos[idx] = { x, y };
      maxY = Math.max(maxY, y + h);
    });

    for (const el of tags) el.style.position = 'absolute';
    base = dims.map((d, i) => ({ x: pos[i].x, y: pos[i].y, h: d.h }));
    packH = Math.ceil(maxY);
    root.classList.add('packed');
    root.style.minHeight = packH + 'px';
    distribute();
  }

  function distribute() {
    if (!base.length) return;
    const tags = Array.prototype.slice.call(root.querySelectorAll('.tag'));
    const H = root.clientHeight;
    lastH = H;
    let sy = 1;
    if (fillH && H > packH + 1) {
      sy = Infinity;
      for (const b of base) if (b.y > 0.5) sy = Math.min(sy, (H - b.h) / b.y);
      if (!isFinite(sy) || sy < 1) sy = 1;
      sy = Math.min(sy, 4);
    }
    tags.forEach((el, i) => {
      const b = base[i];
      if (!b) return;
      const top = sy === 1 ? b.y : Math.min(b.y * sy, Math.max(0, H - b.h));
      el.style.left = Math.round(b.x) + 'px';
      el.style.top = Math.round(top) + 'px';
    });
  }

  const onResize = () => {
    if (Math.abs(root.clientWidth - lastW) > 1) pack();
    else if (Math.abs(root.clientHeight - lastH) > 1) distribute();
  };

  const ro = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(onResize) : null;
  if (ro) ro.observe(root);
  const win = doc.defaultView || window;
  win.addEventListener('resize', onResize);
  if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(() => pack());

  render();

  return {
    el: root,
    update(nextItems) {
      current = nextItems ? nextItems.slice() : [];
      render();
    },
    repack: pack,
    destroy() {
      if (ro) ro.disconnect();
      win.removeEventListener('resize', onResize);
      if (root.parentNode) root.parentNode.removeChild(root);
    },
  };
}

  return { mount: mount, default: { mount: mount } };
});
