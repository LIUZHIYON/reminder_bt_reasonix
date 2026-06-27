# -*- coding: utf-8 -*-
"""reminder_bt frontend server - port 8001
Serves the web frontend and proxies API to board's port 8000"""
import json, os, time, uuid, threading, urllib.request, urllib.error
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

BOARD_API = "http://127.0.0.1:8000"
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

class H(BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        b = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(b))
        self.end_headers(); self.wfile.write(b)
    def _file(self, path, ct):
        if not os.path.exists(path): self.send_error(404); return
        with open(path, "rb") as f: d = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", len(d))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers(); self.wfile.write(d)
    def _proxy(self, method, path, body=None):
        url = BOARD_API + path
        try:
            data = json.dumps(body).encode() if body else None
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("Content-Type", "application/json")
            resp = urllib.request.urlopen(req, timeout=10)
            result = json.loads(resp.read())
            return result, resp.status
        except urllib.error.HTTPError as e:
            return {"error": str(e)}, e.code
        except Exception as e:
            return {"error": str(e)}, 500
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/api/reminders":
            data, status = self._proxy("GET", "/api/reminders")
            return self._json(data, status)
        if p.path in ("/", "/index.html"):
            return self._file(os.path.join(WEB_DIR, "index.html"), "text/html; charset=utf-8")
        if p.path.startswith("/static/"):
            fp = os.path.join(WEB_DIR, p.path[1:])
            ct = "text/css" if fp.endswith(".css") else "application/javascript"
            return self._file(fp, ct)
        self.send_error(404)
    def do_POST(self):
        p = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}
        if p.path == "/api/reminders":
            data, status = self._proxy("POST", "/api/reminders", body)
            return self._json(data, status)
        if "/trigger" in p.path:
            rid = p.path.rstrip("/").split("/")[-2] if "/trigger" in p.path else p.path.split("/")[-1]
            data, status = self._proxy("POST", f"/api/reminders/{rid}/trigger")
            return self._json(data, status)
        self.send_error(404)
    def do_DELETE(self):
        p = urllib.parse.urlparse(self.path)
        rid = p.path.rstrip("/").split("/")[-1]
        data, status = self._proxy("DELETE", f"/api/reminders/{rid}")
        self._json(data, status)
    def log_message(self, *a): pass

if __name__ == "__main__":
    print("Frontend server: http://0.0.0.0:8001")
    print("Proxying API to:", BOARD_API)
    HTTPServer(("0.0.0.0", 8001), H).serve_forever()