#!/usr/bin/env python3
"""Graphics renderer — local control panel.

    python3 ui.py

Opens http://localhost:7303 in your browser. Everything runs on this machine;
nothing is uploaded. Standard library only — no framework, no pip install.
"""
import json
import mimetypes
import os
import platform
import shlex
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PORT = int(os.environ.get("PORT", "7303"))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
os.makedirs(OUT, exist_ok=True)

ACTIONS = [{'id': 'render', 'label': 'Render HTML to PNG'}]
FIELDS = [{'n': 'file', 'l': 'HTML file', 't': 'pick', 'k': 'file', 'p': 'the page to screenshot'}, {'n': 'size', 'l': 'Size', 't': 'select', 'o': [['youtube', 'YouTube thumbnail 1280x720'], ['x', 'X post 1600x900'], ['square', 'Square 1080x1080'], ['story', 'Story / Reel 1080x1920'], ['pin', 'Pinterest 1000x1500'], ['og', 'Link card 1200x630']]}]

JOBS = {}
LOCK = threading.Lock()


def native_pick(kind):
    """A real Finder dialog on macOS; typed paths everywhere else."""
    if platform.system() != "Darwin":
        return None
    script = "choose folder" if kind == "folder" else "choose file"
    r = subprocess.run(["osascript", "-e",
                        f'POSIX path of ({script} with prompt "Choose")'],
                       capture_output=True, text=True)
    return r.stdout.strip().rstrip("/") if r.returncode == 0 else None


def run_job(jid, cmd, cwd):
    job = JOBS[jid]
    try:
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            line = line.rstrip()
            if line:
                with LOCK:
                    job["lines"].append(line)
                    job["lines"] = job["lines"][-300:]
        p.wait()
        job["ok"] = p.returncode == 0
        if job["ok"]:
            fresh = [f for f in os.listdir(OUT)
                     if os.path.getmtime(os.path.join(OUT, f)) >= job["started"] - 1]
            job["files"] = sorted(fresh)
    except Exception as e:
        job["ok"] = False
        job["lines"].append(f"error: {e}")
    finally:
        job["done"] = True


def start(cmd, cwd):
    jid = uuid.uuid4().hex[:8]
    JOBS[jid] = {"lines": [], "done": False, "ok": None, "files": [],
                 "started": time.time()}
    threading.Thread(target=run_job, args=(jid, cmd, cwd), daemon=True).start()
    return jid


PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Graphics renderer</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
:root{--bg:#0d1015;--card:#161b22;--line:#242c38;--fg:#e6edf3;--dim:#8b97a6;--acc:#ff9f68}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,sans-serif}
header{padding:24px 30px 18px;border-bottom:1px solid var(--line);display:flex;
align-items:baseline;gap:14px;flex-wrap:wrap}
h1{margin:0;font-size:19px;letter-spacing:-.2px}
h1 b{color:var(--acc)}
header span{color:var(--dim);font-size:13px}
main{max-width:760px;margin:0 auto;padding:26px 22px 60px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px}
label{display:block;font-size:12px;color:var(--dim);margin:14px 0 5px;
text-transform:uppercase;letter-spacing:.5px}
input,select{width:100%;background:#0b0e13;border:1px solid var(--line);color:var(--fg);
border-radius:8px;padding:10px 12px;font:14px/1.5 inherit}
input:focus,select:focus{outline:none;border-color:var(--acc)}
.row{display:flex;gap:9px}.row>*{flex:1}
.pick{display:flex;gap:8px}.pick input{flex:1}
button{background:var(--acc);color:#14100a;border:0;border-radius:8px;padding:11px 16px;
font-weight:650;font-size:14px;cursor:pointer;font-family:inherit}
button:hover{filter:brightness(1.08)}button:disabled{opacity:.5;cursor:default}
button.ghost{background:#212936;color:var(--fg);font-weight:500;padding:10px 13px}
.go{width:100%;margin-top:20px;padding:13px}
.log{margin-top:16px;background:#080a0e;border:1px solid var(--line);border-radius:8px;
padding:12px 14px;font:12px/1.65 ui-monospace,Menlo,monospace;color:#a9b6c6;
max-height:220px;overflow:auto;white-space:pre-wrap;display:none}
.log.on{display:block}
.files{margin-top:14px;display:none}.files.on{display:block}
.files a{display:block;color:var(--acc);font-size:13px;padding:5px 0;text-decoration:none}
.files a:hover{text-decoration:underline}
footer{text-align:center;color:var(--dim);font-size:12px;padding:22px}
</style></head><body>
<header><h1>Designer <b>panel</b></h1>
<span>localhost:7303 &middot; runs on this machine &middot; nothing uploaded</span></header>
<main><div class="card" id="form"></div></main>
<footer>Output goes to <code>output/</code>. Want it to make the judgment calls —
which moment, which order, what it says? Run the skill in Claude Code instead.</footer>
<script>
const ACTIONS = __ACTIONS_JSON__, FIELDS = __FIELDS_JSON__;

function fieldHTML(f){
  const id = 'f_'+f.n;
  if(f.t==='select') return `<label>${f.l}</label><select id="${id}">`+
    f.o.map(o=>`<option value="${o[0]}">${o[1]}</option>`).join('')+'</select>';
  if(f.t==='pick') return `<label>${f.l}</label><div class="pick">
    <input id="${id}" placeholder="${f.p||''}" value="${f.v||''}">
    <button class="ghost" onclick="pick('${id}','${f.k}')">Choose…</button></div>`;
  return `<label>${f.l}</label><input id="${id}" placeholder="${f.p||''}" value="${f.v||''}">`;
}

document.getElementById('form').innerHTML =
  `<label>Action</label><select id="action">`+
  ACTIONS.map(a=>`<option value="${a.id}">${a.label}</option>`).join('')+`</select>`+
  FIELDS.map(f=>Array.isArray(f)
    ? '<div class="row">'+f.map(x=>`<div>${fieldHTML(x)}</div>`).join('')+'</div>'
    : fieldHTML(f)).join('')+
  `<button class="go" id="go" onclick="run()">Run</button>
   <div class="log" id="log"></div><div class="files" id="files"></div>`;

async function pick(id,kind){
  const r = await fetch('/api/pick?type='+kind); const d = await r.json();
  if(d.path) document.getElementById(id).value = d.path;
}

async function run(){
  const data = {action: document.getElementById('action').value};
  FIELDS.flat().forEach(f=>{
    const el = document.getElementById('f_'+f.n); if(el) data[f.n] = el.value;
  });
  const go=document.getElementById('go'), log=document.getElementById('log'),
        files=document.getElementById('files');
  go.disabled=true; go.textContent='Working…';
  log.className='log on'; log.textContent='starting…'; files.className='files';
  const r = await fetch('/api/run',{method:'POST',
    headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
  const d = await r.json();
  if(d.error){ log.textContent=d.error; go.disabled=false; go.textContent='Run'; return; }
  const t=setInterval(async()=>{
    const s=await (await fetch('/api/job?id='+d.job)).json();
    log.textContent=s.lines.join(String.fromCharCode(10));
    log.scrollTop=log.scrollHeight;
    if(!s.done) return;
    clearInterval(t); go.disabled=false; go.textContent='Run';
    if(s.files && s.files.length){
      files.className='files on';
      files.innerHTML='<label>Output</label>'+s.files.map(f=>
        `<a href="/api/file?p=${encodeURIComponent(f)}" target="_blank">${f}</a>`).join('');
    }
  },600);
}
</script></body></html>"""


def page():
    return (PAGE.replace("__ACTIONS_JSON__", json.dumps(ACTIONS))
                .replace("__FIELDS_JSON__", json.dumps(FIELDS)))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path == "/":
            return self.send(200, page(), "text/html; charset=utf-8")
        if u.path == "/api/pick":
            return self.send(200, {"path": native_pick(q.get("type", ["file"])[0])})
        if u.path == "/api/job":
            job = JOBS.get(q.get("id", [""])[0])
            if not job:
                return self.send(404, {"error": "no such job"})
            with LOCK:
                return self.send(200, {k: job[k] for k in ("lines", "done", "ok", "files")})
        if u.path == "/api/file":
            name = os.path.basename(q.get("p", [""])[0])
            path = os.path.join(OUT, name)
            if not os.path.exists(path):
                return self.send(404, {"error": "gone"})
            data = open(path, "rb").read()
            ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
            return self.send(200, data, ctype)
        return self.send(404, {"error": "not found"})

    def do_POST(self):
        if urlparse(self.path).path != "/api/run":
            return self.send(404, {"error": "not found"})
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or "{}")
        try:
            cmd, err = build_command(body)
        except Exception as e:
            return self.send(200, {"error": str(e)})
        if err:
            return self.send(200, {"error": err})
        return self.send(200, {"job": start(cmd, OUT)})


def build_command(b):
    tool = os.path.join(HERE, "render.py")
    f = b.get("file", "").strip()
    if not f or not os.path.exists(f):
        return None, f"File not found: {f or '(empty)'}"
    return [sys.executable, tool, f, os.path.join(OUT, "render.png"),
            "--size", b.get("size", "x")], None


def main():
    url = f"http://localhost:{PORT}"
    print(f"Graphics renderer\n  {url}\n  Ctrl+C to stop\n")
    if platform.system() == "Darwin":
        subprocess.run(["open", "-a", "Google Chrome", url], capture_output=True)
    else:
        webbrowser.open(url)
    try:
        ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
