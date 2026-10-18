# Problem and decision

Extract date: 30 September 2026. Fiscal year ends that day. Numbers below are from `warehouse.duckdb`, not from what people said in interviews.

## What people asked for

The CDO wants an always-on AI analyst in team chat, in review meetings, and as voice in the field app, for every sales role, in four regions. The 2025 bot is the reason to refuse that as the first build.

## What the 2025 bot actually did

`old_bot_usage_log`, launch through the extract date:

| | |
|---|---|
| Questions | 9,125 |
| Peak week | 413 questions, 83 people (week of 30 June 2025) |
| Answered | 5,205 (57%) |
| Not understood | 1,868 |
| Error | 1,163 |
| Timeout | 889, at the 90 second cap |
| Thumbs down on answered questions | 1,630 of 5,205 |

The CDO note says pilot territories grew after launch and that current models remove the limits. The log does not show hundreds of weekly users. Peak distinct users in a week is 83. Marathi (269), Hindi (206), Portuguese (591) questions are almost all "Not understood".

Three failures were rules, not model quality:

1. One service account. Territory managers could read other territories. The permission investigation is still open.
2. Amounts were summed as stored. Rupees, reais, euros and dollars became one number.
3. The bot had its own sales definition (M03: sum the amount column). Sales Operations uses M01 (gross, order date, local currency). Finance uses M02 (net, invoice date, USD). Nobody has agreed which wins.

## The job worth doing first

Riklr's first call listed six jobs. Two of them are the Monday morning of a territory manager, and they are not in any dashboard he can open on a phone:

- Which scheme credits are still pending
- Who is overdue, and whether the overdue is a real collection or a held credit

Vidarbha (IN-W01), the territory in the field interview, on the extract date:

| | |
|---|---|
| Distributors | 6 |
| Credits still accrued, not issued | 16 |
| Value of those credits | INR 2.07 crore |
| Oldest accrual | 4 April 2026, 179 days |
| Distributors where finance has already flagged a dispute | 3 (Malana, Vesorex, Tetalia) |

The territory manager copies the Monday finance list into a notebook by hand. His distributor's list of credits is better than the company's. That is the gap.

## What we did not build, and why

A free-text analyst on raw tables repeats the 2025 failure. A meeting bot and a voice bot add channels before the number is trustworthy. Forecasting the quarter needs Sales and Finance to pick a definition. The prototype does not pick one silently. It uses M01 for sales and labels it.

The Global Sales Head said the new tool has to be right every time, and it has to save time on something people already do. The Monday list is that job.

## Second finding, kept in the same screen

The Sales Head called the Brazil South returns weather, and said nobody saw them coming. The distributor in BR-S01 said dealers stopped reordering in October 2025, before the rain failed, and that the company only watched what he bought.

Brazil South returns, February to April 2026: **188,939 packs** across 18 distributors. Dealer scans in that sub-region had already fallen from 91,701 packs in October 2025 to 36,877 in January 2026, while sell-in was still being pushed.

The prototype does not forecast weather. It flags a distributor whose own scans drop 25% or more over 8 weeks while sell-in continues. It does not compare distributors to each other. Loyalty coverage is uneven (Vidarbha's Malana has 2 of 8 dealers enrolled). A distributor with no enrolled dealers is marked "no coverage", not "healthy".

## How to prove it helps

Do not measure weekly active users. The 2025 bot had users and still lost trust.

Measure, on one territory for one quarter:

1. Credits raised on the Monday call that were accrued and unissued. Baseline: the territory manager finds these by phoning the regional office.
2. Days from accrual to issue, for credits the list surfaces. Vidarbha's open set is already 81 days on average in India, 179 days for the oldest.
3. Trucks not pushed into a distributor already flagged "do not push". Baseline: Brazil South took 188,939 packs back after the push.
4. Wrong-territory answers. Target is zero. The 2025 bot's target was "the prompt will filter". It did not.
