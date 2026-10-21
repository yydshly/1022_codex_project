"""Integration QA: real WebGL compile/render, controls, mobile and offline entry.

Requires Playwright for Python and its Chromium browser. Uses an owned, temporary
HTTP server and software WebGL for reproducibility; never claims device FPS.
"""
from __future__ import annotations
import base64
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


PIXEL_CHECK = """() => {
  const lab = window.shaderLab;
  const renderer = new lab.ShaderRenderer(document.createElement('canvas'));
  renderer.setImage(lab.state.source);
  const gl = renderer.gl;
  const read = () => { const p = new Uint8Array(96 * 128 * 4); gl.readPixels(0, 0, 96, 128, gl.RGBA, gl.UNSIGNED_BYTE, p); return p; };
  const difference = (a, b) => { let n = 0; for (let i=0; i<a.length; i+=4) n += Math.abs(a[i]-b[i])+Math.abs(a[i+1]-b[i+1])+Math.abs(a[i+2]-b[i+2]); return n / (a.length / 4 * 3); };
  const results = [];
  for (const effect of lab.state.effects) {
    const values = lab.valuesFor(effect, true);
    const options = {width:96,height:128,time:1.7};
    renderer.draw(effect, values, {...options,compare:1});
    const original = read();
    renderer.draw(effect, values, options);
    const preview = read();
    const delta = difference(original, preview);
    const errors = [];
    for (const edge of ['min','max']) {
      const extreme = {...values};
      for (const p of effect.params) if(p.type==='float') extreme[p.label] = p[edge] ?? p[edge==='min'?'uiMin':'uiMax'];
      renderer.draw(effect, extreme, options);
      read();
      const error = gl.getError();
      if(error !== gl.NO_ERROR) errors.push(error);
    }
    renderer.draw(effect, values, {...options,time:2.9});
    let animationDelta = difference(preview, read());
    if(effect.timeUsed && animationDelta < 0.01) {
      for (const t of [0.1, 0.3, 0.5, 0.9, 3.7, 4.3]) {
        renderer.draw(effect, values, {...options,time:t});
        animationDelta = Math.max(animationDelta, difference(preview, read()));
      }
    }
    results.push({id:effect.id,delta,animationDelta,errors});
  }
  renderer.dispose();
  return results;
}"""


def run() -> dict:
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "web")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/"
    output = {"engine": "Chromium / ANGLE SwiftShader (software WebGL 2)", "nativeMetal": "not run: Windows host"}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--disable-gpu-watchdog"])
            page = browser.new_page(viewport={"width": 1440, "height": 1330}, device_scale_factor=1, reduced_motion="reduce")
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            response = page.goto(url, wait_until="networkidle")
            assert response.status == 200
            page.wait_for_function("window.shaderLab?.state.ready === true")
            assert page.locator('.effect-card[data-rendered="true"]').count() == 41
            assert page.locator('.card-error').count() == 0
            assert not page.evaluate("window.shaderLab.state.errors")
            output["pixels"] = page.evaluate(PIXEL_CHECK)
            assert all(not item["errors"] for item in output["pixels"])
            assert all(item["delta"] > 0.1 for item in output["pixels"]), "Every showcase must visibly differ from its original"
            # All modes whose original implementation uses time must change at
            # these times; an intermittent effect can be allowed separately if
            # its source is intentionally unchanged at both sampled moments.
            animated = page.evaluate("window.shaderLab.state.effects.filter(s=>s.timeUsed).map(s=>s.id)")
            output["animatedChanged"] = sum(item["animationDelta"] > 0.01 for item in output["pixels"] if item["id"] in animated)
            assert output['animatedChanged'] == len(animated) == 36
            page.screenshot(path=str(ROOT / "assets/cover.png"))
            cover_data = page.evaluate("window.shaderLab.state.source.toDataURL('image/png').split(',')[1]")
            (ROOT / "assets/sample-cover.png").write_bytes(base64.b64decode(cover_data))
            # A non-flat material with text, edges and color serves all 41 shaders.
            page.locator('#search').fill('涟漪')
            assert page.locator('.effect-card:visible').count() > 0
            page.locator('#search').fill('no-such-shader-xyz')
            assert page.locator('#empty').is_visible()
            assert page.locator('.effect-card:visible').count() == 0
            page.locator('#search').fill('')
            page.locator('#category').select_option(label='触摸交互')
            assert page.locator('.effect-card:visible').count() == 2
            page.locator('#category').select_option('all')
            assert page.locator('.effect-card:visible').count() == 41
            # Sliders update actual rendering inputs and the exported Swift call.
            page.locator('#param-intensity').fill('0.23')
            assert 'intensity: 0.23' in page.locator('#swift-code').inner_text()
            page.locator('#reset').click()
            assert 'intensity: 0.4' in page.locator('#swift-code').inner_text()
            page.locator('#compare').click()
            assert page.locator('#compare').get_attribute('aria-pressed') == 'true'
            canvas = page.locator('#preview')
            canvas.click(position={"x": 60, "y": 80})
            assert page.evaluate('window.shaderLab.state.split') != 0.5
            page.locator('#compare').click()
            # Exercise each scalar slider for every effect, including absent and
            # out-of-range upstream metadata, against actual UI event bindings.
            control_count = 0
            for item in page.evaluate("window.shaderLab.state.effects.map(e=>({id:e.id, params:e.params}))"):
                page.locator(f'.effect-option[data-id="{item["id"]}"]').click()
                for param in item['params']:
                    if param['type'] == 'point':
                        continue
                    slider = page.locator(f'#param-{param["label"]}')
                    lo, hi = float(slider.get_attribute('min')), float(slider.get_attribute('max'))
                    step = float(slider.get_attribute('step'))
                    aligned = lo + round((hi - lo) * 0.5 / step) * step
                    slider.fill(str(round(aligned, 3)).removesuffix('.0'))
                    control_count += 1
                assert not page.locator('#preview-error').is_visible()
            output['scalarControlsExercised'] = control_count
            page.locator('.effect-option[data-id="RefractLens"]').click()
            canvas.click(position={"x": 100, "y": 120})
            touch = page.evaluate('window.shaderLab.state.touch')
            assert abs(touch[0] - 0.5) > 0.01
            canvas.press('ArrowRight')
            assert page.evaluate('window.shaderLab.state.touch[0]') > touch[0]
            page.locator('.effect-option[data-id="TouchRipple"]').click()
            canvas.click(position={"x": 90, "y": 160})
            assert page.evaluate('window.shaderLab.state.rippleStart') is not None
            page.locator('[data-material="flower"]').click()
            page.wait_for_function("window.shaderLab.state.material === 'flower' && window.shaderLab.state.ready")
            assert page.locator('.effect-card[data-rendered="true"]').count() == 41
            page.locator('[data-material="type"]').click()
            page.wait_for_function("window.shaderLab.state.material === 'type' && window.shaderLab.state.ready")
            page.locator('#upload').set_input_files(str(ROOT / 'web/assets/sample-cover.svg'))
            page.wait_for_function("window.shaderLab.state.material === 'upload' && window.shaderLab.state.ready")
            assert '本地图片' in page.locator('#stage-caption').inner_text()
            with page.expect_download() as download:
                page.locator('#download').click()
            assert download.value.suggested_filename.endswith('.png')
            # Dedicated collection screenshot: every tile was rendered on GPU.
            page.locator('[data-material="cover"]').click()
            page.wait_for_function("window.shaderLab.state.material === 'cover' && window.shaderLab.state.ready")
            page.locator('#toast').wait_for(state='hidden')
            page.locator('#gallery').screenshot(path=str(ROOT / 'assets/collection.png'))
            # Mobile and reduced-motion behavior, with no horizontal overflow.
            page.set_viewport_size({"width": 390, "height": 1200})
            page.locator('.effect-option[data-id="Holographic"]').click()
            page.locator('#showcase').click()
            page.evaluate('window.scrollTo(0,0)')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=str(ROOT / 'assets/gallery-mobile.png'))
            assert not page.evaluate('window.shaderLab.state.playing')
            # The portable artifact must also run directly from disk without an
            # HTTP server, fetch, external fonts, image hosts or JS dependencies.
            offline = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion='reduce')
            offline.goto((ROOT / 'web/standalone.html').as_uri(), wait_until='load')
            offline.wait_for_function('window.shaderLab?.state.ready === true')
            assert offline.locator('.effect-card[data-rendered="true"]').count() == 41
            assert not offline.evaluate('window.shaderLab.state.errors')
            offline.locator('[data-material="flower"]').click()
            offline.wait_for_function("window.shaderLab.state.material === 'flower' && window.shaderLab.state.ready")
            output['offline'] = '41/41; local file entry and embedded material switching passed'
            unsupported = browser.new_page()
            unsupported.add_init_script("""const original = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                  return type === 'webgl2' ? null : original.call(this, type, ...args);
                };""")
            unsupported.goto(url)
            unsupported.wait_for_function('window.shaderLab !== undefined')
            assert unsupported.locator('#preview-error').is_visible()
            assert unsupported.locator('.effect-option').count() == 41
            unsupported.locator('.effect-option[data-id="TouchRipple"]').click()
            assert unsupported.locator('#preview-error').is_visible()
            output['withoutWebGL'] = 'Explicit error retained; all 41 parameter/source entries remain accessible'
            assert not errors, errors
            assert not page.evaluate('window.shaderLab.state.errors')
            output['browserErrors'] = errors
            output['result'] = 'passed'
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    return output


if __name__ == '__main__':
    result = run()
    target = ROOT / 'verification.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"PASS: 41 shaders, {result['scalarControlsExercised']} scalar controls, touch, materials, mobile, PNG and offline HTML.")
    print(f"Time-dependent algorithms changed: {result['animatedChanged']}/36. Full results: {target}")
