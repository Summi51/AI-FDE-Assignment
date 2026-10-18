# Research and assumptions

Candidate `fw22_0669`. Case: sales analyst. Extract date: 30 September 2026.

This note is the secondary research the brief asked for, plus the assumptions the prototype depends on. Numbers come from `warehouse.duckdb`. Claims about the job come from the seven interviews and the internal notes. Where those disagree, the disagreement is written down.

## What I looked up outside the pack

I did not treat the CDO's "current models fix this" line as a fact. Three public findings shaped the refusal.

1. **A better model does not fix a wrong metric.** Text-to-SQL benchmarks (Spider, BIRD) score whether the query returns the labelled answer. They do not score whether two departments agree on the label. This company has three sales definitions (M01, M02, M03) and no owner who wins. A model that writes cleaner SQL still has to pick one. The 2025 bot picked M03 and lost the argument in the meeting.

2. **A second screen is the failure mode, not the fix.** Agribusiness salespeople have been reporting this since sales-force automation arrived: the tool is liked, and it still does not give time back (Baker, 1996, *Agribusiness*). Current ag-sales write-ups say the same thing in plainer words: the CRM launched, the team does not use it. McKinsey's farmer work points the other way for the buyer (one mobile surface, so the rep stops hunting for a number) and does not support a chatbot in a second app. The Vidarbha manager described a notebook. He did not describe a missing chat box.

3. **Loyalty-scan coverage is a known trap in agri-inputs.** Dealer-scan programmes under-enrol. A national average of "scans down" mixes enrolled dealers with dealers who were never in the programme. The dictionary says coverage is uneven. The prototype therefore compares a distributor only with its own prior window, and says "no coverage" when enrolment is zero.

I did not research a voice stack, a meeting bot, or a forecasting model. Those were the options I rejected, and researching the build would have been the wrong use of the week.

## Options I weighed

| Option | What it fixes | Why it lost |
|---|---|---|
| Always-on analyst in chat, meetings and voice | The CDO's note | The 2025 bot already shipped this shape. Peak week was 83 people. Rules were wrong: one service account, mixed currencies, a private sales definition. |
| A governed text-to-SQL box, one channel | Ad-hoc questions the dashboards miss | Still needs a metric owner. Still asks the manager to type on a bike. Useful later, not first. |
| A quarterly forecast | The plan the regional manager reviews | Sales and Finance have not agreed the number being forecast. Forecasting the wrong one makes the meeting worse. |
| Monday list plus visit brief | The notebook, the credit argument, the truck pushed into a silent dealer base | One person, one morning, one screen. The data for it is already in the warehouse. |

The Monday list won because it is a job people already do, the data exists, and the failure of the last tool is evidence against the other three.

## Assumptions the prototype makes

These are choices, not facts. A reviewer who disagrees should be able to find each one.

1. **The user is one territory manager.** Demo user `U042`, Vidarbha, `IN-W01`. A regional manager's screen is a different job and is not built.
2. **Sales on the brief is M01.** Gross sell-in, order date, local currency, returns excluded. Finance's M02 (net, invoice date, USD) is not shown and is not converted into M01. The label on the screen says which definition it is.
3. **A credit is pending only while it is accrued and not issued.** Cancelled credits are excluded. Issued credits are excluded. This matches the finance note, not the 2025 bot.
4. **Overdue is read from the latest aging snapshot for distributors in that territory**, not from the latest snapshot in the whole warehouse. Regions close on different days.
5. **Sell-in packs are counted from deduped `line_id`s.** The raw extract has duplicate lines. Summing them would invent stock.
6. **A stock flag needs two windows of the same distributor.** Recent 8 weeks against the prior 8 weeks, on the India load date. A drop of 25% or more, with sell-in still arriving, is "do not push". Zero enrolled dealers is "no coverage", never "healthy".
7. **The screen does not rank distributors against each other on scans.** Coverage differs (Malana is 2 of 8). A cross-distributor rank would punish the enrolled ones.
8. **Currency is never converted.** INR and BRL are not added. USD is not a display currency for a territory manager.
9. **Access is the permission matrix, not a prompt.** A territory manager asking for another territory gets 403. The 2025 bot's "the prompt will filter" is treated as a failed control.
10. **The prototype is read-only.** It does not post a credit, place an order, or write back to the warehouse. A real connection would need the identity system, not a shared service account.

## What I am not claiming

- I am not claiming the Monday list raises sell-in. The proof metrics are credits raised, days to issue, trucks not pushed, and zero wrong-territory answers.
- I am not claiming the Brazil returns were caused by the scan drop. I am claiming the scan drop was visible before the returns, and nobody was asked to look.
- I am not claiming 83 weekly users is a failure of demand. It is a failure of the claim that the bot had hundreds of weekly users, and of the claim that usage meant trust. 1,630 answered questions were thumbs-down.
