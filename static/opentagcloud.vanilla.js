/* openTagCloud — script-tag build. window.openTagCloud.{mount,defineElement,renderTagCloud,...}; registers <otc-tag-cloud> automatically. Generated from src/umd.ts. */
"use strict";
var openTagCloud = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // src/umd.ts
  var umd_exports = {};
  __export(umd_exports, {
    TAG_CLOUD_CSS: () => TAG_CLOUD_CSS,
    TagCloudLayout: () => TagCloudLayout,
    createTagElement: () => createTagElement,
    defineElement: () => defineElement,
    estimateCloudHeight: () => estimateCloudHeight,
    injectStyles: () => injectStyles,
    keyOf: () => keyOf,
    makeRng: () => makeRng,
    mount: () => mount,
    prepareTags: () => prepareTags,
    renderTagCloud: () => renderTagCloud
  });

  // src/prepare.ts
  var keyOf = (t) => t.id ?? t.label;
  var EXP = 1.9;
  var FLOOR = 9;
  var warnedBadWeight = false;
  function sanitizeWeight(w) {
    if (Number.isFinite(w) && w >= 0) return w;
    if (!warnedBadWeight) {
      warnedBadWeight = true;
      console.warn(
        "opentagcloud: negative or non-finite tag weight(s) clamped to 0"
      );
    }
    return 0;
  }
  function lengthFactor(name) {
    const chars = name.length;
    const longest = Math.max(...name.split(/\s+/).map((w) => w.length));
    return Math.max(
      0.45,
      Math.min(Math.min(1, 15 / Math.max(15, chars)), 11 / Math.max(11, longest))
    );
  }
  function labelParts(label) {
    const parts = [];
    for (const token of label.split(/(\s+)/)) {
      if (!token) continue;
      const nowrap = !/\s/.test(token) && token.includes("-");
      const prev = parts[parts.length - 1];
      if (!nowrap && prev && !prev.nowrap) prev.text += token;
      else parts.push({ text: token, nowrap });
    }
    return parts;
  }
  function prepareTags(items, options = {}) {
    const { minPx = 12, maxPx = 40, minOpacity = 0.62, ariaLabel } = options;
    const weights = items.map((t) => sanitizeWeight(t.weight));
    const maxW = Math.max(1, ...weights);
    const countFactor = Math.min(
      1.1,
      Math.max(0.5, Math.sqrt(18 / Math.max(1, items.length)))
    );
    return items.map((t, i) => {
      const w = weights[i];
      const ramp = minPx + Math.pow(w / maxW, EXP) * (maxPx - minPx);
      const fontPx = +Math.max(
        FLOOR,
        ramp * countFactor * lengthFactor(t.label)
      ).toFixed(1);
      const opacity = +(minOpacity + Math.pow(w / maxW, 0.8) * (1 - minOpacity)).toFixed(2);
      return {
        item: t,
        key: keyOf(t),
        weight: w,
        text: t.label,
        parts: labelParts(t.label),
        fontPx,
        opacity,
        title: t.title ?? String(t.weight),
        ariaLabel: ariaLabel ? typeof ariaLabel === "function" ? ariaLabel(t) : `${t.label}, weight ${t.weight}` : void 0,
        className: t.class ? `otc-tag ${t.class}` : "otc-tag",
        style: `font-size:${fontPx}px;opacity:${opacity};${t.color ? `--otc-tag-color:${t.color};` : ""}`
      };
    });
  }

  // src/styles.ts
  var TAG_CLOUD_CSS = `.otc-cloud {
  position: relative;
  display: block;
  flex: 1 1 auto;
  min-height: 0;
}
.otc-tag {
  display: inline-block;
  line-height: 0.95;
  text-align: center;
  font-weight: 700;
  /* Per-tag color (via --otc-tag-color) wins; then the --otc-color theme
     default; else inherit currentColor. */
  color: var(--otc-tag-color, var(--otc-color, currentColor));
  overflow-wrap: normal;
  word-break: normal;
  hyphens: none;
  text-decoration: none;
}
/* Hyphenated words are wrapped in .otc-nb so lines never break at a hyphen
   (the DOM text itself stays untouched \u2014 see prepareTags' label parts). */
.otc-tag .otc-nb {
  white-space: nowrap;
}
@media (prefers-reduced-motion: no-preference) {
  .otc-tag {
    transition:
      color var(--otc-transition, 150ms ease),
      opacity var(--otc-transition, 150ms ease),
      /* FLIP move/entrance animation on re-packs; set --otc-move-transition
         to 0s to disable */
        transform var(--otc-move-transition, 250ms cubic-bezier(0.22, 1, 0.36, 1));
  }
}
a.otc-tag:hover,
a.otc-tag:focus-visible {
  /* a per-tag color keeps its hue on hover; otherwise use the theme hover color */
  color: var(--otc-tag-color, var(--otc-hover-color, #2563eb));
  opacity: 1 !important;
  text-decoration: none;
}
/* Fallback before JS packs (and no-JS/SSR): justified inline flow. */
.otc-cloud:not(.otc-packed) {
  text-align: justify;
  text-align-last: justify;
  line-height: 1.15;
}
.otc-cloud:not(.otc-packed) .otc-tag {
  margin: 0.18em 0.3em;
  max-width: min(6.5em, 100%);
  vertical-align: middle;
}
`;
  var STYLE_ID = "opentagcloud-css";
  function injectStyles(doc) {
    const d = doc ?? (typeof document === "undefined" ? void 0 : document);
    if (!d || d.getElementById(STYLE_ID)) return;
    const style = d.createElement("style");
    style.id = STYLE_ID;
    style.textContent = TAG_CLOUD_CSS;
    d.head.appendChild(style);
  }

  // src/rng.ts
  function makeRng(seed) {
    let h = 1779033703 ^ seed.length;
    for (let i = 0; i < seed.length; i++) {
      h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
      h = h << 13 | h >>> 19;
    }
    let s = h >>> 0;
    return () => {
      s = Math.imul(s ^ s >>> 15, 1 | s) >>> 0;
      s = s + Math.imul(s ^ s >>> 7, 61 | s) >>> 0;
      return ((s ^ s >>> 14) >>> 0) / 4294967296;
    };
  }

  // src/layout.ts
  var PAD = 5;
  var LOOSEN = 1.4;
  var widthFactor = (w) => Math.min(1.25, Math.max(0.72, w / 460));
  function createSpatialHash() {
    const BUCKET = 64;
    const buckets = /* @__PURE__ */ new Map();
    const bucketKey = (bx, by) => by * 8192 + bx;
    const bucketRange = (x, y, w, h) => [
      Math.max(0, Math.floor((x - PAD) / BUCKET)),
      Math.max(0, Math.floor((x + w + PAD) / BUCKET)),
      Math.max(0, Math.floor((y - PAD) / BUCKET)),
      Math.max(0, Math.floor((y + h + PAD) / BUCKET))
    ];
    return {
      insert(r) {
        const [x0, x1, y0, y1] = bucketRange(r.x, r.y, r.w, r.h);
        for (let by = y0; by <= y1; by++)
          for (let bx = x0; bx <= x1; bx++) {
            const k = bucketKey(bx, by);
            let list = buckets.get(k);
            if (!list) buckets.set(k, list = []);
            list.push(r);
          }
      },
      hits(x, y, w, h) {
        const [x0, x1, y0, y1] = bucketRange(x, y, w, h);
        for (let by = y0; by <= y1; by++)
          for (let bx = x0; bx <= x1; bx++) {
            const list = buckets.get(bucketKey(bx, by));
            if (!list) continue;
            for (const r of list)
              if (x < r.x + r.w + PAD && x + w + PAD > r.x && y < r.y + r.h + PAD && y + h + PAD > r.y)
                return true;
          }
        return false;
      }
    };
  }
  var TagCloudLayout = class {
    #root;
    #fill;
    #injectStyles;
    #incremental;
    #lastW = -1;
    #lastH = -1;
    // packed base layout (natural top-left of each term) + its natural height;
    // distribute() spreads these to fill the container without re-packing.
    #base = [];
    #packH = 0;
    // last packed geometry, keyed by data-key — feeds incremental refresh
    #placed = /* @__PURE__ */ new Map();
    #packW = -1;
    // fit-mode font scale of the last pack — incremental refresh must measure
    // at the same scale or every kept tag would look "changed"
    #packScale = 1;
    #ro;
    #onResize;
    #destroyed = false;
    // suppress the FLIP for packs that belong to initial rendering (the
    // fonts.ready re-measure) — animating font-metric corrections reads as jank
    #skipFlip = false;
    constructor(root, options = {}) {
      this.#root = root;
      this.#fill = options.fill;
      this.#injectStyles = options.injectStyles ?? true;
      this.#incremental = options.incremental ?? false;
    }
    get #fillH() {
      return this.#fill === "height" || this.#fill === "both";
    }
    #tags() {
      return Array.from(this.#root.querySelectorAll(".otc-tag"));
    }
    /** Start observing the container and pack the initial layout. */
    attach() {
      if (typeof window === "undefined" || this.#destroyed) return;
      if (this.#injectStyles) injectStyles(this.#root.ownerDocument);
      this.pack();
      let raf = 0;
      const onResize = () => {
        if (raf) return;
        raf = requestAnimationFrame(() => {
          raf = 0;
          if (this.#destroyed) return;
          if (Math.abs(this.#root.clientWidth - this.#lastW) > 1) this.pack();
          else if (Math.abs(this.#root.clientHeight - this.#lastH) > 1)
            this.distribute();
        });
      };
      this.#onResize = onResize;
      this.#ro = new ResizeObserver(onResize);
      this.#ro.observe(this.#root);
      window.addEventListener("resize", onResize);
      document.fonts?.ready?.then(() => {
        if (this.#destroyed) return;
        this.#skipFlip = true;
        try {
          this.pack();
        } finally {
          this.#skipFlip = false;
        }
      });
    }
    /** Re-pack after the tag elements changed (items added/removed/re-weighted). */
    refresh() {
      if (typeof window === "undefined" || this.#destroyed) return;
      if (this.#incremental && this.#tryIncremental()) return;
      this.pack();
    }
    /** Change the fill mode; only term positions move, never the container height. */
    setFill(fill) {
      this.#fill = fill;
      if (typeof window !== "undefined" && !this.#destroyed) this.distribute();
    }
    /** Stop observing. The current positions are left in place. */
    destroy() {
      this.#destroyed = true;
      this.#ro?.disconnect();
      this.#ro = void 0;
      if (this.#onResize && typeof window !== "undefined") {
        window.removeEventListener("resize", this.#onResize);
      }
      this.#onResize = void 0;
    }
    // ---------- movement animation (FLIP) ----------
    // Animations are on unless the user asked for reduced motion or zeroed the
    // --otc-move-transition custom property.
    #moveEnabled() {
      if (typeof matchMedia !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches)
        return false;
      const v = getComputedStyle(this.#root).getPropertyValue("--otc-move-transition").trim();
      return v !== "none" && v !== "0s" && v !== "0ms";
    }
    // Visual positions (including any in-flight transform) relative to the root,
    // keyed by data-key — so interrupted animations hand off smoothly.
    #snapshot(tags) {
      const rootRect = this.#root.getBoundingClientRect();
      const map = /* @__PURE__ */ new Map();
      for (const el of tags) {
        const r = el.getBoundingClientRect();
        map.set(el.dataset.key ?? "", {
          x: r.left - rootRect.left,
          y: r.top - rootRect.top
        });
      }
      return map;
    }
    // Classic FLIP: positions are already final; put each moved tag back at its
    // old visual spot with a transform, flush, then release the transform so the
    // stylesheet's `transform var(--otc-move-transition)` rule animates it home.
    // Tags with no previous position (new items) scale in instead.
    #playFlip(tags, from) {
      for (const el of tags) {
        el.style.transition = "none";
        el.style.transform = "";
      }
      const rootRect = this.#root.getBoundingClientRect();
      const now = tags.map((el) => {
        const r = el.getBoundingClientRect();
        return { el, x: r.left - rootRect.left, y: r.top - rootRect.top };
      });
      let any = false;
      for (const { el, x, y } of now) {
        const prev = from.get(el.dataset.key ?? "");
        if (prev) {
          const dx = prev.x - x;
          const dy = prev.y - y;
          if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) {
            el.style.transform = `translate(${dx.toFixed(1)}px, ${dy.toFixed(1)}px)`;
            any = true;
          }
        } else {
          el.style.transform = "scale(0.5)";
          any = true;
        }
      }
      if (any) void this.#root.offsetWidth;
      for (const el of tags) {
        el.style.transition = "";
        el.style.transform = "";
      }
    }
    // ---------- layout ----------
    // Lay the cloud out to fill the container, adapting to its size and aspect
    // ratio. Heaviest terms are seeded at anchor points spread evenly across the
    // box (farthest-point order, so they never cram together); each term then
    // spirals out from its anchor only as far as needed to avoid overlaps. A
    // wide box gets more columns → fewer wrapped lines; corners get seeded so the
    // cloud fills rather than blobbing in the middle.
    pack() {
      const root = this.#root;
      const tags = this.#tags();
      if (!tags.length) return;
      const W = root.clientWidth;
      if (W < 2) return;
      this.#lastW = W;
      const flipFrom = root.classList.contains("otc-packed") && !this.#skipFlip && this.#moveEnabled() ? this.#snapshot(tags) : null;
      const weights = tags.map((el) => {
        const w = parseFloat(el.dataset.weight ?? "");
        return Number.isFinite(w) ? w : 1;
      });
      const keys = tags.map((el) => el.dataset.key ?? el.textContent ?? "");
      const prevMinHeight = root.style.minHeight;
      const prevPositions = tags.map((el) => el.style.position);
      root.style.minHeight = "0px";
      for (const el of tags) el.style.position = "absolute";
      const externalH = root.clientHeight;
      root.style.minHeight = prevMinHeight;
      tags.forEach((el, i) => el.style.position = prevPositions[i]);
      const fit = externalH > 40;
      root.classList.remove("otc-packed");
      for (const el of tags) {
        el.style.position = "";
        el.style.left = "";
        el.style.insetInlineStart = "";
        el.style.top = "";
        el.style.transform = "";
      }
      const wide = W >= 380;
      const setBase = (scale2) => {
        for (const el of tags) {
          el.style.whiteSpace = wide ? "nowrap" : "normal";
          el.style.maxWidth = wide ? "none" : "min(6.5em, 100%)";
          el.style.fontSize = `${Math.max(8, parseFloat(el.dataset.fs || "12") * widthFactor(W) * scale2).toFixed(1)}px`;
        }
      };
      const measure = () => tags.map((el) => ({ el, w: el.offsetWidth, h: el.offsetHeight }));
      setBase(1);
      let dims = measure();
      const baseArea = dims.reduce((s, d) => s + (d.w + PAD) * (d.h + PAD), 0);
      let scale = 1;
      if (fit && baseArea > 0) {
        scale = Math.min(
          2.5,
          Math.max(1, Math.sqrt(W * externalH / (baseArea * LOOSEN)))
        );
      }
      const n = dims.length;
      const order = dims.map((_, i) => i).sort((a, b) => weights[b] - weights[a]);
      let pos = new Array(n);
      let maxY = 0;
      const ATTEMPTS = 3;
      for (let attempt = 0; attempt < ATTEMPTS; attempt++) {
        if (scale !== 1 || attempt > 0) {
          setBase(scale);
          dims = measure();
        }
        const maxTagW = wide ? W * 0.85 : W;
        for (const d of dims) {
          if (d.w > maxTagW) {
            const cur = parseFloat(d.el.style.fontSize) || 12;
            d.el.style.fontSize = `${Math.max(9, cur * (maxTagW / d.w)).toFixed(1)}px`;
            d.w = d.el.offsetWidth;
            d.h = d.el.offsetHeight;
          }
        }
        const area = dims.reduce((s, d) => s + (d.w + PAD) * (d.h + PAD), 0);
        const boxH = Math.max(fit ? externalH : area * LOOSEN / W, 1);
        const aspect = W / boxH;
        const cols = Math.max(1, Math.round(Math.sqrt(n * aspect)));
        const rows = Math.max(1, Math.ceil(n / cols));
        const cellW = W / cols;
        const cellH = boxH / rows;
        const cells = [];
        for (let r = 0; r < rows; r++)
          for (let c = 0; c < cols; c++)
            cells.push({ x: (c + 0.5) * cellW, y: (r + 0.5) * cellH });
        const cx0 = W / 2;
        const cy0 = boxH / 2;
        const remaining = cells.slice();
        const ordered = [];
        remaining.sort(
          (a, b) => Math.hypot(a.x - cx0, a.y - cy0) - Math.hypot(b.x - cx0, b.y - cy0)
        );
        ordered.push(remaining.shift());
        const minDist = remaining.map(
          (c) => Math.hypot(c.x - ordered[0].x, c.y - ordered[0].y)
        );
        while (remaining.length) {
          let bi = 0;
          let bd = -1;
          for (let i = 0; i < remaining.length; i++) {
            if (minDist[i] > bd) {
              bd = minDist[i];
              bi = i;
            }
          }
          const next = remaining.splice(bi, 1)[0];
          minDist.splice(bi, 1);
          ordered.push(next);
          for (let i = 0; i < remaining.length; i++) {
            const d = Math.hypot(
              remaining[i].x - next.x,
              remaining[i].y - next.y
            );
            if (d < minDist[i]) minDist[i] = d;
          }
        }
        const { insert, hits } = createSpatialHash();
        pos = new Array(n);
        maxY = 0;
        order.forEach((idx, rank) => {
          const { w, h } = dims[idx];
          const a = ordered[rank % ordered.length];
          const rand = makeRng(keys[idx]);
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
            if (++steps > 4e3) break;
          }
          insert({ x, y, w, h });
          pos[idx] = { x, y };
          maxY = Math.max(maxY, y + h);
        });
        if (!fit || attempt === ATTEMPTS - 1 || maxY <= externalH * 1.08 || scale <= 1)
          break;
        scale = Math.max(1, scale * (externalH / maxY) * 0.95);
      }
      for (const el of tags) el.style.position = "absolute";
      this.#base = dims.map((d, i) => ({ x: pos[i].x, y: pos[i].y, h: d.h }));
      this.#packH = Math.ceil(maxY);
      this.#packW = W;
      this.#packScale = scale;
      this.#placed = new Map(
        dims.map((d, i) => [
          keys[i],
          { x: pos[i].x, y: pos[i].y, w: d.w, h: d.h }
        ])
      );
      root.classList.add("otc-packed");
      root.style.minHeight = `${this.#packH}px`;
      this.distribute(flipFrom);
    }
    // Incremental refresh (opt-in): keep every tag whose measured box still fits
    // at its previous position; spiral only new/changed/displaced tags out from
    // their old spot. Returns false to request a full pack (width changed, no
    // prior layout, or too much churn).
    #tryIncremental() {
      const root = this.#root;
      const tags = this.#tags();
      if (!tags.length) return false;
      const W = root.clientWidth;
      if (W < 2) return false;
      if (!this.#placed.size || Math.abs(W - this.#packW) > 1) return false;
      const flipFrom = this.#moveEnabled() ? new Map([...this.#placed].map(([k, r]) => [k, { x: r.x, y: r.y }])) : null;
      const weights = tags.map((el) => {
        const w = parseFloat(el.dataset.weight ?? "");
        return Number.isFinite(w) ? w : 1;
      });
      const keys = tags.map((el) => el.dataset.key ?? el.textContent ?? "");
      const wide = W >= 380;
      for (const el of tags) {
        el.style.whiteSpace = wide ? "nowrap" : "normal";
        el.style.maxWidth = wide ? "none" : "min(6.5em, 100%)";
        el.style.fontSize = `${Math.max(8, parseFloat(el.dataset.fs || "12") * widthFactor(W) * this.#packScale).toFixed(1)}px`;
        el.style.transform = "";
      }
      const dims = tags.map((el) => ({
        el,
        w: el.offsetWidth,
        h: el.offsetHeight
      }));
      const maxTagW = wide ? W * 0.85 : W;
      for (const d of dims) {
        if (d.w > maxTagW) {
          const cur = parseFloat(d.el.style.fontSize) || 12;
          d.el.style.fontSize = `${Math.max(9, cur * (maxTagW / d.w)).toFixed(1)}px`;
          d.w = d.el.offsetWidth;
          d.h = d.el.offsetHeight;
        }
      }
      const n = dims.length;
      const order = dims.map((_, i) => i).sort((a, b) => weights[b] - weights[a]);
      const { insert, hits } = createSpatialHash();
      const pos = new Array(n);
      const toPlace = [];
      for (const idx of order) {
        const old = this.#placed.get(keys[idx]);
        const { w, h } = dims[idx];
        if (old && Math.abs(old.w - w) <= 1 && Math.abs(old.h - h) <= 1 && old.x + w <= W + 1 && !hits(old.x, old.y, w, h)) {
          insert({ x: old.x, y: old.y, w, h });
          pos[idx] = { x: old.x, y: old.y };
        } else {
          toPlace.push(idx);
        }
      }
      if (toPlace.length > n * 0.4) return false;
      const step = Math.max(
        3,
        Math.sqrt(W * Math.max(this.#packH, 1) / Math.max(n, 1)) * 0.12
      );
      let maxY = 0;
      for (const p of pos) if (p) maxY = Math.max(maxY, p.y);
      for (const idx of toPlace) {
        const { w, h } = dims[idx];
        const old = this.#placed.get(keys[idx]);
        const rand = makeRng(keys[idx]);
        let angle = rand() * Math.PI * 2;
        const ax = old ? old.x + old.w / 2 : rand() * W;
        const ay = old ? old.y + old.h / 2 : rand() * Math.max(this.#packH, 1);
        let radius = 0;
        let x = ax - w / 2;
        let y = ay - h / 2;
        let steps = 0;
        while (true) {
          x = ax - w / 2 + radius * Math.cos(angle);
          y = ay - h / 2 + radius * Math.sin(angle);
          x = Math.max(0, Math.min(x, W - w));
          if (y < 0) y = 0;
          if (!hits(x, y, w, h)) break;
          angle += 0.5;
          radius += step;
          if (++steps > 4e3) break;
        }
        insert({ x, y, w, h });
        pos[idx] = { x, y };
      }
      maxY = 0;
      for (let i = 0; i < n; i++) maxY = Math.max(maxY, pos[i].y + dims[i].h);
      for (const el of tags) el.style.position = "absolute";
      this.#base = dims.map((d, i) => ({ x: pos[i].x, y: pos[i].y, h: d.h }));
      this.#packH = Math.ceil(maxY);
      this.#packW = W;
      this.#lastW = W;
      this.#placed = new Map(
        dims.map((d, i) => [
          keys[i],
          { x: pos[i].x, y: pos[i].y, w: d.w, h: d.h }
        ])
      );
      root.classList.add("otc-packed");
      root.style.minHeight = `${this.#packH}px`;
      this.distribute(flipFrom);
      return true;
    }
    // Spread the packed terms to fill the container's current height when
    // fill='height' (so a cloud in a taller grid cell reaches the bottom and
    // neighbours stay aligned). Terms are position:absolute, so moving them can't
    // change the container's own height — this is loop-safe by construction, unlike
    // reading/writing height during pack().
    //
    // `flipFrom` is internal plumbing from pack()/refresh(): the pre-layout
    // visual positions to animate from (null = don't animate). When called with
    // no argument (height resize, setFill), it snapshots itself.
    distribute(flipFrom) {
      const base = this.#base;
      if (!base.length) return;
      const tags = this.#tags();
      if (flipFrom === void 0) {
        flipFrom = this.#root.classList.contains("otc-packed") && this.#moveEnabled() ? this.#snapshot(tags) : null;
      }
      const H = this.#root.clientHeight;
      this.#lastH = H;
      let sy = 1;
      if (this.#fillH && H > this.#packH + 1) {
        sy = Infinity;
        for (const b of base) if (b.y > 0.5) sy = Math.min(sy, (H - b.h) / b.y);
        if (!isFinite(sy) || sy < 1) sy = 1;
        sy = Math.min(sy, 4);
      }
      tags.forEach((el, i) => {
        const b = base[i];
        if (!b) return;
        const top = sy === 1 ? b.y : Math.min(b.y * sy, Math.max(0, H - b.h));
        el.style.insetInlineStart = `${Math.round(b.x)}px`;
        el.style.top = `${Math.round(top)}px`;
      });
      if (flipFrom) this.#playFlip(tags, flipFrom);
    }
  };

  // src/render.ts
  function createTagElement(p, doc = document) {
    const el = doc.createElement(p.item.href ? "a" : "span");
    el.className = p.className;
    if (p.item.href) el.href = p.item.href;
    el.setAttribute("style", p.style);
    el.title = p.title;
    if (p.ariaLabel) el.setAttribute("aria-label", p.ariaLabel);
    el.dataset.fs = String(p.fontPx);
    el.dataset.weight = String(p.weight);
    el.dataset.key = p.key;
    for (const part of p.parts) {
      if (part.nowrap) {
        const nb = doc.createElement("span");
        nb.className = "otc-nb";
        nb.textContent = part.text;
        el.appendChild(nb);
      } else {
        el.appendChild(doc.createTextNode(part.text));
      }
    }
    return el;
  }
  function renderTagCloud(container, items, options = {}) {
    container.classList.add("otc-cloud");
    const doc = container.ownerDocument;
    const render = (list) => {
      container.replaceChildren(
        ...prepareTags(list, options).map((p) => createTagElement(p, doc))
      );
    };
    render(items);
    const layout = new TagCloudLayout(container, options);
    layout.attach();
    return {
      update(next) {
        render(next);
        layout.refresh();
      },
      repack() {
        layout.refresh();
      },
      setFill(fill) {
        layout.setFill(fill);
      },
      destroy() {
        layout.destroy();
        container.replaceChildren();
        container.classList.remove("otc-cloud", "otc-packed");
      }
    };
  }

  // src/vanilla.ts
  function mount(container, items, options = {}) {
    if (!container) throw new Error("openTagCloud.mount: container is required");
    const doc = container.ownerDocument || document;
    const root = doc.createElement("div");
    root.style.height = "100%";
    container.appendChild(root);
    const handle = renderTagCloud(root, items, options);
    return {
      el: root,
      update: (next) => handle.update(next),
      repack: () => handle.repack(),
      destroy() {
        handle.destroy();
        root.remove();
      }
    };
  }
  function defineElement(tagName) {
    const name = tagName || "otc-tag-cloud";
    if (typeof customElements === "undefined" || customElements.get(name)) return;
    class OtcTagCloudElement extends HTMLElement {
      static get observedAttributes() {
        return [
          "items",
          "min-px",
          "max-px",
          "min-opacity",
          "fill",
          "weight-labels",
          "incremental"
        ];
      }
      _handle = null;
      /** Set via the `items` property; wins over the attribute. */
      _items = null;
      get items() {
        if (this._items) return this._items;
        const raw = this.getAttribute("items");
        if (!raw) return [];
        try {
          return JSON.parse(raw);
        } catch {
          console.warn(`openTagCloud: invalid JSON in <${name}> items attribute`);
          return [];
        }
      }
      set items(value) {
        this._items = value || [];
        if (this._handle) this._handle.update(this._items);
      }
      connectedCallback() {
        if (!this.style.display) this.style.display = "block";
        this._mount();
      }
      disconnectedCallback() {
        if (this._handle) {
          this._handle.destroy();
          this._handle = null;
        }
      }
      attributeChangedCallback(attr) {
        if (!this.isConnected || !this._handle) return;
        if (attr === "items") {
          if (!this._items) this._handle.update(this.items);
        } else {
          this._handle.destroy();
          this._handle = null;
          this._mount();
        }
      }
      _mount() {
        if (this._handle) return;
        const num = (attr) => {
          const v = parseFloat(this.getAttribute(attr) || "");
          return isFinite(v) ? v : void 0;
        };
        this._handle = mount(this, this.items, {
          minPx: num("min-px"),
          maxPx: num("max-px"),
          minOpacity: num("min-opacity"),
          // boolean attribute: announce "<label>, weight <weight>" to screen readers
          ariaLabel: this.hasAttribute("weight-labels") || void 0,
          fill: this.getAttribute("fill") || void 0,
          incremental: this.hasAttribute("incremental")
        });
      }
    }
    customElements.define(name, OtcTagCloudElement);
  }

  // src/estimate.ts
  function estimateCloudHeight(items, width, options = {}) {
    if (!items.length || width < 2) return 0;
    const wf = widthFactor(width);
    const wide = width >= 380;
    const GLYPH = 0.58;
    let area = 0;
    let tallest = 0;
    for (const p of prepareTags(items, options)) {
      const fs = Math.max(8, p.fontPx * wf);
      const textW = p.text.length * fs * GLYPH;
      let w;
      let lines = 1;
      if (wide) {
        w = Math.min(textW, width);
      } else {
        const maxW = Math.min(6.5 * fs, width);
        lines = Math.max(1, Math.ceil(textW / maxW));
        w = Math.min(textW, maxW);
      }
      const h = lines * fs * 0.95;
      area += (w + PAD) * (h + PAD);
      tallest = Math.max(tallest, h);
    }
    return Math.ceil(Math.max(area * LOOSEN / width, tallest));
  }

  // src/umd.ts
  if (typeof customElements !== "undefined") defineElement();
  return __toCommonJS(umd_exports);
})();
