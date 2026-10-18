# Monday list

Riklr AI FDE internship case. Candidate `fw22_0669`. Case: sales analyst.

The ask was an always-on AI analyst in chat, meetings and the field app. The 2025 bot already tried that. This prototype does not. It is the list a territory manager needs before the Monday 9:30 call: unissued credits first, then the visit brief, then a stock flag that says do not push another truck.

Demo user is `U042`, territory manager for Vidarbha (`IN-W01`). The screen does not open another territory.

## Run

Python 3.11 or newer. One dependency.

```bash
python3 -m pip install -r requirements.txt
PYTHONPATH=. python3 -m app.server
```

Open http://127.0.0.1:8765/ for the Monday list. Open http://127.0.0.1:8765/deck for the 8 slides. Right arrow moves forward, left arrow moves back.

The warehouse extract is already in the repo:

`case-pack/fde-case-study/sales-analyst/data/warehouse.duckdb`

The server is read-only against that file. It does not connect to a client chat tool, field app or live warehouse. No API key, no database server, no login.

`HOST` and `PORT` are optional. Locally they default to `127.0.0.1` and `8765`.

## Deploy

The app is one Python process plus the DuckDB file already in the repo. Anything that runs a Python web process can host it. Render is the shortest path.

1. Push this repo. It is already at https://github.com/Summi51/AI-FDE-Assignment
2. On Render, create a **Web Service** and connect that repo. Branch `main`.
3. Runtime: **Python 3**.
4. Build command: `pip install -r requirements.txt`
5. Start command: `PYTHONPATH=. python3 -m app.server`
6. Render sets `PORT` itself. The server reads it. Leave `HOST` unset only on your laptop. On Render set `HOST` to `0.0.0.0`, or the service will bind to localhost and the health check will fail.
7. Deploy. Open the service URL for the Monday list. Add `/deck` for the slides.

There is no database to provision and no secret to paste. The warehouse file ships with the code.

To run it the same way on any machine that already has Python 3.11:

```bash
git clone https://github.com/Summi51/AI-FDE-Assignment.git
cd AI-FDE-Assignment
python3 -m pip install -r requirements.txt
HOST=0.0.0.0 PORT=8765 PYTHONPATH=. python3 -m app.server
```

Then open `http://<the machine>:8765/`.

## Check

```bash
PYTHONPATH=. python3 -m unittest tests.test_brief -v
python3 scripts/smoke_http.py
```

The smoke script expects the server to be running.

## Notes

- `notes/01-problem-and-decision.md` — why the chatbot lost, and the numbers behind the Monday list
- `notes/04-research-and-assumptions.md` — what was looked up outside the pack, the options compared, and the ten assumptions the screen depends on
- `notes/02-deck.md` — slide outline
- `notes/03-video-script.md` — narration, under four minutes. The video itself is not in the repo until it is recorded.

## What the brief will not do

- It will not add INR and BRL, or convert either to USD.
- It will not treat a cancelled credit as pending.
- It will not call a scan drop when no dealers are enrolled.
- It will not compare one distributor's scans with another's.
- A territory manager who asks for another territory gets 403.

## What a real connection would need

Role permissions from the existing identity system, not a shared service account. Metric definitions owned by Sales Operations and Finance, named on the screen. A warehouse connection that stays inside the user's territory. Hindi, Marathi and Portuguese only after the number on the screen is one the manager already trusts.
