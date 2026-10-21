// Derived from MPMyburgh/dr-aria @ ff26c94; MIT, (c) 2026 Michael Myburgh.
// See LICENSE.dr-aria.txt and ../NOTICE.md.
import { ART } from './upstream-art.js';
  const pad = (s, w) => { const g = w - s.length; if (g <= 0) return s.slice(0, w);
    const l = (g >> 1); return " ".repeat(l) + s + " ".repeat(g - l); };

  /* ---------------- animated part libraries ---------------- */
  const BROWS = {                                   // 13
    warm:       "\u2581\u2583\u2584\u2584\u2583   \u2583\u2584\u2584\u2583\u2581",
    thoughtful: "\u2583\u2584\u2584\u2583\u2581   \u2581\u2583\u2584\u2584\u2583",   // inner ends lifted — weighing something
  };
  const LASHES = {                                  // 13, sits directly over the whites
    open: "\u2582\u2584\u2584\u2582     \u2582\u2584\u2584\u2582",
    low:  "\u2581\u2582\u2582\u2581     \u2581\u2582\u2582\u2581",
  };
  const EYES = {                                    // 13, upper half; whites are cols 31-34 / 40-43
    open:  " \u2584\u2584       \u2584\u2584 ",
    half:  "\u2584\u2584\u2584\u2584     \u2584\u2584\u2584\u2584",
    shut:  "             ",
    smile: "\u256d\u2500\u2500\u256e     \u256d\u2500\u2500\u256e",
    left:  "\u2584\u2584       \u2584\u2584  ",
    right: "  \u2584\u2584       \u2584\u2584",
    up:    " \u2580\u2580       \u2580\u2580 ",              // pupils ride high — looking off and thinking
    down:  "             ",              // and low — reading, or writing on the pad
  };
  const EYES_LO = {                                 // 13, lower half
    open:  " \u2580\u2580       \u2580\u2580 ",
    half:  " \u2580\u2580       \u2580\u2580 ",
    shut:  "\u2500\u2500\u2500\u2500     \u2500\u2500\u2500\u2500",
    smile: "             ",
    left:  "\u2580\u2580       \u2580\u2580  ",
    right: "  \u2580\u2580       \u2580\u2580",
    up:    "             ",
    down:  " \u2584\u2584       \u2584\u2584 ",
  };
  const MOUTH = {                                   // [upper, lower] 11 — a continuous curve
    smile: ["           ", "  \u2572\u2581\u2581\u2581\u2581\u2581\u2571  "],
    grin:  ["  \u2572     \u2571  ", "   \u2572\u2581\u2581\u2581\u2571   "],
    rest:  ["           ", "   \u2572\u2581\u2581\u2581\u2571   "],
    ah:    ["   \u2584\u2584\u2584\u2584\u2584   ", "   \u2580\u2580\u2580\u2580\u2580   "],
    aa:    ["  \u2584\u2584\u2584\u2584\u2584\u2584\u2584  ", "  \u2580\u2580\u2580\u2580\u2580\u2580\u2580  "],
    oo:    ["    \u2584\u2584\u2584    ", "    \u2580\u2580\u2580    "],
    ee:    [" \u2584\u2584\u2584\u2584\u2584\u2584\u2584\u2584\u2584 ", " \u2580\u2580\u2580\u2580\u2580\u2580\u2580\u2580\u2580 "],
    eh:    ["   \u2584\u2584\u2584\u2584\u2584   ", "    \u2580\u2580\u2580    "],
    mm:    ["   \u2500\u2500\u2500\u2500\u2500   ", "           "],
    small: ["    \u2584\u2584\u2584    ", "           "],
  };
  const MOODS = {
    warm: { brow: "warm", eyes: "open", rest: "smile" },
  };
  const FRINGE = ["▓", "▒", "▓", "░"];
  const LOCK_L = ["▒", "░", "▒", "▓"];
  const LOCK_R = ["▒", "▓", "▒", "░"];
  const LEAF   = ["~", "≈", "~", "-"];
  const STEAM  = ["(", " ", ")", "~", "'", " "];
  const PEN    = ["╱", "│", "╲", "│"];
  const NOTE   = ["≡≡≡≡≡≡≡  ≡ ", "≡≡≡≡≡≡≡≡≡  ", "≡≡≡≡≡ ≡≡≡≡ ", "≡≡≡≡≡≡≡≡≡≡ "];

  const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");


export class AriaRenderer {

    _subst(line) {
      const m = MOUTH[this.mouth] || MOUTH.smile;
      let fi = 0, li = 0, ri = 0, si = 0, vi = 0;
      return line
        .replace(/B{13}/g, () => pad(BROWS[this.brow] || BROWS.warm, 13))
        .replace(/L{13}/g, () => (this.eyes === "shut" || this.eyes === "half") ? LASHES.low : LASHES.open)
        .replace(/E{13}/g, () => EYES[this.eyes] || EYES.open)
        .replace(/A{13}/g, () => EYES_LO[this.eyes] || EYES_LO.open)
        .replace(/M{11}/g, () => m[0])
        .replace(/W{11}/g, () => m[1])
        .replace(/N{11}/g, () => NOTE[(this.tick >> 2) % NOTE.length])
        .replace(/F/g, () => FRINGE[(this.tick + fi++ * 2) % FRINGE.length])
        .replace(/Q/g, () => LOCK_L[((this.tick >> 1) + li++) % LOCK_L.length])
        .replace(/R/g, () => LOCK_R[((this.tick >> 1) + ri++) % LOCK_R.length])
        .replace(/S/g, () => STEAM[(this.tick + si++ * 2) % STEAM.length])
        .replace(/V/g, () => LEAF[((this.tick >> 2) + vi++) % LEAF.length])
        .replace(/P/g, () => PEN[(this.state === "listening" || this.state === "thinking"
                                  || this.state === "writing")
                                  ? (this.tick % PEN.length) : 1]);
    }

    /* ---------------- render ---------------- */
    render() {
      const out = [];
      for (let r = 0; r < ART.ch.length; r++) {
        let line = this._subst(ART.ch[r]), col = ART.co[r];
        if (this.headShift && r >= 2 && r <= 17) {           // nod: shift only the head window
          const A = 22, B = 53;
          line = line.padEnd(B, " "); col = col.padEnd(B, " ");
          const seg = line.slice(A, B), sc = col.slice(A, B);
          const ns = this.headShift > 0 ? " " + seg.slice(0, -1) : seg.slice(1) + " ";
          const nc = this.headShift > 0 ? " " + sc.slice(0, -1)  : sc.slice(1) + " ";
          line = line.slice(0, A) + ns + line.slice(B);
          col  = col.slice(0, A)  + nc + col.slice(B);
        }
        let html = "", run = "", cur = null;
        for (let i = 0; i < line.length; i++) {
          const k = col[i] || " ";
          if (k !== cur) { if (run) html += cur === " " ? esc(run) : `<i class="x${cur}">${esc(run)}</i>`; run = ""; cur = k; }
          run += line[i];
        }
        if (run) html += cur === " " ? esc(run) : `<i class="x${cur}">${esc(run)}</i>`;
        out.push(html);
      }
      this.el.innerHTML = out.join("\n");
    }

}
export { MOODS };
export const PALETTE = "\n  .xw{color:#27333f}   .xf{color:#8a6a4c}  .xC{color:#131c25}  .xc{color:#3c5a68}\n  .xh{color:#8a6449}   .xH{color:#a8815f}  .xk{background:#241b1d}\n  .xl{color:#4f8079;background:#2c524f}    .xL{color:#8cc3ba;background:#2c524f}\n  .xr{color:#c8452c}   .xR{color:#7d2a1a}  .xG{color:#dd5c38}\n  .xs{color:#d7a67c;background:#f3cca9}    .xS{color:#a8764f;background:#f3cca9}\n  .xi{color:#3a2a24;background:#f3cca9}    .xp{color:#9b3644;background:#f3cca9}\n  .xb{color:#e0917f;background:#f3cca9}\n  .xW{color:#241713;background:#fbf6ec}    .xq{color:#c4805a;background:#f3cca9}\n  .xj{color:#8f3d22;background:#f3cca9}\n  .xZ{color:#5a3f34;background:#f3cca9}    .xz{color:#e5a68d;background:#eec2a3}\n  .xa{color:#bdb5a0;background:#efe8d5}    .xI{color:#7d8794;background:#efe8d5}\n  .xn{color:#e8e2d0}\n  .xg{color:#63ab5e}   .xe{color:#4b8043}  .xo{color:#b06a45}  .xO{color:#6d4331}\n  .xm{color:#cfd9e2}   .xB{color:#3b2618;background:#6b4630}  .xt{color:#7f96a8}\n  .xD{color:#7a5a41}   .xy{color:#ffd79c}  .xu{color:#2c3843}  .xx{color:#27333f}\n  .xr,.xG{text-shadow:0 0 9px rgba(200,69,44,.28)}\n  .xy{text-shadow:0 0 12px rgba(255,215,156,.55)}\n";
