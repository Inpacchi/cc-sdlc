#!/usr/bin/env python3
"""The factory's echo service as a small HTTP server, for anywhere that runs a container or a process
behind HTTPS (z-sdlc factory bundle; factory.json's smoke.echo_host). It answers like echo/worker.js:
the method, URL, query arguments and request headers as indented JSON, one header per line, so smoke can
read what the sandbox proxy injected. It stores and logs nothing. Standard library only.

    python3 server.py [port]      (default 8080; put TLS in front, smoke calls https://<host>/headers)
"""
import http.server
import json
import sys
import urllib.parse


class Echo(http.server.BaseHTTPRequestHandler):
    def answer(self):
        url = urllib.parse.urlsplit(self.path)
        headers = {"-".join(part.capitalize() for part in name.split("-")): value for name, value in self.headers.items()}
        body = json.dumps({"args": dict(urllib.parse.parse_qsl(url.query)), "headers": headers,
                           "method": self.command, "url": self.path}, indent=2) + "\n"
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = answer

    def log_message(self, *args):  # store and log nothing
        pass


def main(port=8080):
    http.server.ThreadingHTTPServer(("", port), Echo).serve_forever()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8080)
