"""Serve an explicit local rendering page that exports real effect PNG modules.

Open the printed HTTP URL in a WebGL 2 browser. No browser driver is required.
The page renders the repository's shader algorithms, then uploads PNG captures
only to this loopback server. It can also rasterize the generated SVG diagrams.
Stop the server with Ctrl+C after all outputs have been saved.
"""
from __future__ import annotations
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import runpy
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
EFFECTS = ["Original", "Holographic", "NeonEdge", "Kaleidoscope", "InkBleed", "Datamosh", "Disintegrate", "TouchRipple", "RefractLens"]
OUTPUTS = {name: WEB / f"assets/effects/{name}.png" for name in EFFECTS}
OUTPUTS.update(Overview=WEB / "assets/understanding-overview.png", Atlas=WEB / "assets/effect-atlas.png")

PAGE = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>真实效果模块导出</title>
<style>body{font:16px/1.7 system-ui;background:#111513;color:#e9eee6;margin:32px}h1{font-size:24px}#results{display:grid;grid-template-columns:repeat(5,1fr);gap:18px}canvas{width:100%;height:auto}figure{margin:0}figcaption{font-size:12px}#status{color:#d9f279}</style>
<h1>SwiftUIShaders · 真实效果模块导出</h1><p>相同素材、固定参数和时间；使用项目内的 WebGL 移植算法，结果直接保存到本地项目。</p><p id="status">准备渲染…</p><div id="results"></div>
<script type="module">
import {ShaderRenderer} from '/renderer.js';
const ids = ['Original','Holographic','NeonEdge','Kaleidoscope','InkBleed','Datamosh','Disintegrate','TouchRipple','RefractLens'];
const presets = {
 Holographic:{intensity:0.65,scale:12,speed:1.2},
 NeonEdge:{glowAmount:1.2,mixOriginal:0.45},
 Disintegrate:{threshold:0.48},
 TouchRipple:{touchAge:0.48,amplitude:28,decay:0.8}
};
const status = document.querySelector('#status');
let saved=0;
async function save(id,canvas){
 const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
 const response=await fetch('/__capture/'+id,{method:'POST',headers:{'Content-Type':'image/png'},body:blob});
 if(!response.ok)throw new Error('保存失败 '+id);
 saved++;status.textContent=`已保存 ${saved} / 11 个输出`;
 document.body.dataset.saved=String(saved);
}
try{
 const manifest=await (await fetch('/shaders.json')).json();
 const img=new Image();img.src='/assets/sample-cover.svg';await img.decode();
 const renderer=new ShaderRenderer(document.createElement('canvas'));renderer.setImage(img);
 for(const id of ids){
  const canvas=document.createElement('canvas');canvas.width=600;canvas.height=800;
  let values={},effect=null;
  if(id==='Original')canvas.getContext('2d').drawImage(img,0,0,600,800);
  else{
   effect=manifest.shaders.find(s=>s.id===id);
   values=Object.fromEntries(effect.params.filter(p=>p.type==='float').map(p=>[p.label,p.default]));
   Object.assign(values,presets[id]||{});
   renderer.draw(effect,values,{width:600,height:800,time:1.7,touch:[0.5,0.5]});
   canvas.getContext('2d').drawImage(renderer.canvas,0,0);
   if(renderer.gl.isContextLost())throw new Error('WebGL 上下文丢失：'+id);
  }
  const figure=document.createElement('figure');figure.append(canvas);
  const caption=document.createElement('figcaption');caption.textContent=id;figure.append(caption);
  document.querySelector('#results').append(figure);
  await save(id,canvas);
  await fetch('/__metadata/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,values,time:1.7,touch:[0.5,0.5],logicalSize:[450,600],outputSize:[600,800],renderer:'WebGL 2 browser capture',sourceCommit:manifest.commit})});
 }
 renderer.dispose();
 status.textContent='9 / 9 个真实效果模块已保存；等待 SVG 总览图生成后继续栅格化。';
 for(const [id,path,width,height] of [['Overview','understanding-overview',2000,2460],['Atlas','effect-atlas',1800,2750]]){
  let available=false;
  while(!available){available=(await (await fetch('/__status')).json())[id];if(!available)await new Promise(r=>setTimeout(r,1000));}
  const svg=new Image();svg.src='/assets/'+path+'.svg?build='+Date.now();await svg.decode();
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
  canvas.getContext('2d').drawImage(svg,0,0,width,height);
  await save(id,canvas);
 }
 status.textContent='完成：9 个真实效果模块 + 2 张完整图解。';document.title='11 / 11 图解与效果已导出';
}catch(error){status.textContent='导出失败：'+error.message;document.body.dataset.error=error.message;console.error(error);}
</script></html>'''


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/__render":
            data = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(data)
        elif path == "/__status":
            data = json.dumps({"Overview": (WEB / "assets/understanding-overview.svg").exists(),
                               "Atlas": (WEB / "assets/effect-atlas.svg").exists()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        else:
            super().do_GET()

    def do_POST(self):
        route, _, name = urlsplit(self.path).path.removeprefix("/").partition("/")
        length = int(self.headers.get("Content-Length", "0"))
        if name not in OUTPUTS or route not in {"__capture", "__metadata"} or not 0 < length <= 6_000_000:
            self.send_error(400)
            return
        body = self.rfile.read(length)
        if route == "__capture":
            if not body.startswith(b"\x89PNG\r\n\x1a\n"):
                self.send_error(400)
                return
            target = OUTPUTS[name]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
            print(f"Saved {target.relative_to(ROOT)} ({len(body):,} bytes)", flush=True)
            if name == EFFECTS[-1]:
                # Rebuild diagrams from the just-captured modules, before the
                # browser rasterizes them, keeping images and metadata in sync.
                runpy.run_path(str(ROOT / "scripts/build_visuals.py"), run_name="__main__")
        else:
            value = json.loads(body)
            target = WEB / f"assets/effects/{name}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8012), partial(Handler, directory=str(WEB)))
    print("Local visual renderer: http://127.0.0.1:8012/__render", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
