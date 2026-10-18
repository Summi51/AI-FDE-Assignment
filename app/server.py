"""Local prototype server. No client chat tool, no live warehouse."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
DECK = ROOT / "deck"

from app.access import AccessDenied
from app.brief import monday_list, visit_brief
from app.warehouse import connect

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8765"))


def territory_list(user_id: str) -> dict:
    con = connect()
    try:
        user = con.execute(
            """
            select user_id, role, territory_code, primary_language
            from users_and_roles where user_id = ?
            """,
            [user_id],
        ).fetchone()
        if not user:
            raise AccessDenied("Unknown user")
        if user[1] != "Territory Manager":
            raise AccessDenied("This screen is the territory manager morning list")
        rows = con.execute(
            """
            select distributor_id, distributor_name, tier
            from distributors
            where territory_code = ?
            order by distributor_name
            """,
            [user[2]],
        ).fetchall()
        return {
            "user_id": user[0],
            "role": user[1],
            "territory_code": user[2],
            "language": user[3],
            "distributors": [
                {"id": r[0], "name": r[1], "tier": r[2]} for r in rows
            ],
        }
    finally:
        con.close()


class Handler(BaseHTTPRequestHandler):
    def _send_file(self, path: str):
        rel = "index.html" if path in {"", "/"} else path.lstrip("/")
        root = DECK if rel == "deck" or rel.startswith("deck/") else WEB
        if rel == "deck":
            rel = "index.html"
        elif rel.startswith("deck/"):
            rel = rel[len("deck/"):]
        root = root.resolve()
        target = (root / rel).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            self._send(404, {"error": "not found"})
            return
        kind = {".html": "text/html", ".css": "text/css", ".js": "text/javascript"}.get(
            target.suffix, "application/octet-stream"
        )
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send(self, code: int, payload: dict):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        try:
            if parsed.path == "/api/me":
                self._send(200, territory_list(qs.get("user", ["U042"])[0]))
                return
            if parsed.path == "/api/monday":
                con = connect()
                try:
                    self._send(200, monday_list(con, qs.get("user", ["U042"])[0]))
                finally:
                    con.close()
                return
            if parsed.path == "/api/brief":
                user = qs.get("user", ["U042"])[0]
                dist = qs.get("distributor", [""])[0]
                if not dist:
                    self._send(400, {"error": "distributor is required"})
                    return
                con = connect()
                try:
                    self._send(200, visit_brief(con, user, dist))
                finally:
                    con.close()
                return
            self._send_file(parsed.path)
        except AccessDenied as exc:
            self._send(403, {"error": str(exc)})
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception:
            self._send(500, {"error": "Could not build that brief"})

    def log_message(self, fmt, *args):
        return


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Visit brief running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
