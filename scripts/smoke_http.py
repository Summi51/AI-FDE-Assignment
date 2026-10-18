"""Smoke the local prototype. Exit 1 if any check fails."""
import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8765"
fails = 0


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=8) as r:
        return r.status, r.read()


def check(name, ok, detail=""):
    global fails
    if not ok:
        fails += 1
    print(("PASS" if ok else "FAIL"), name, detail)


for path in ["/", "/deck", "/styles.css", "/app.js", "/deck/deck.css", "/deck/deck.js", "/deck.css"]:
    try:
        code, body = get(path)
    except urllib.error.HTTPError as exc:
        code, body = exc.code, b""
    expect = 404 if path == "/deck.css" else 200
    check(path, code == expect and (expect == 404 or len(body) > 50), f"{code} {len(body)}b")

code, body = get("/api/monday?user=U042")
monday = json.loads(body)
names = [i["name"] for i in monday["call_first"]]
check("monday starts with Malana", names and names[0].startswith("Malana"), str(names))
check(
    "quiet has Sumonia",
    any("Sumonia" in i["name"] for i in monday.get("quiet", [])),
    str([i["name"] for i in monday.get("quiet", [])]),
)

code, body = get("/api/brief?user=U042&distributor=D1101")
brief = json.loads(body)
check("malana do not push", brief["stock"]["flag"] == "Do not push", brief["stock"]["flag"])
check("malana talking point", bool(brief.get("talking_point")))
blob = json.dumps(brief)
check("amounts stay INR", "INR" in blob and "USD" not in blob)

try:
    get("/api/brief?user=U042&distributor=D1001")
    check("cross territory blocked", False, "got 200")
except urllib.error.HTTPError as exc:
    check("cross territory blocked", exc.code in {401, 403}, str(exc.code))

code, body = get("/api/brief?user=U042&distributor=D1102")
quiet = json.loads(body)
check(
    "sumonia no coverage",
    quiet["stock"]["flag"] == "No scan coverage",
    quiet["stock"]["flag"],
)

code, page = get("/deck")
html = page.decode()
check("deck links absolute css", 'href="/deck/deck.css"' in html)
check("deck links absolute js", 'src="/deck/deck.js"' in html)
check("deck does not use relative css", 'href="deck.css"' not in html)

print(fails, "failed")
sys.exit(1 if fails else 0)
