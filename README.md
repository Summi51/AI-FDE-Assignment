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

The server is read-only against that file. It does not connect to a client chat tool, field app or live warehouse.

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
