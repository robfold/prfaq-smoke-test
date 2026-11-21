# Sizing the test and reading the result

## Metrics

Per variant, from unique visitor ids:

- **visitors**: ids with a `view` event, excluding the team's own visits.
- **cta rate**: ids with `cta_click` ÷ visitors. Interest in the angle.
- **signup rate**: ids with `signup` ÷ visitors. Interest strong enough to leave an email. The default primary metric.
- **cost per signup**: ad spend ÷ signups. With equal budgets, it folds in how well each ad pulled clicks, since each ad carries its own angle.

Pick one primary metric in `test-plan.md` before launch. The others are context.

## Size it before launch

```
python3 scripts/compare.py plan --base 0.03 --target 0.06 --cpc 0.8
```

```
To tell 3.0% from 6.0% with 80% power
(alpha 0.05 split over 3 pairs = 0.0167 per pair):
  visitors per variant: 999
  visitors in total:    2997
  budget at 0.8 per visitor: 2,397.60 in total, 799.20 per variant
```

`--base` is the rate you expect from the weaker angle; `--target` is the rate you need to tell apart from it. `--cpc` is the expected cost per visitor. The 5% error rate is split across all three pairs, because three variants mean three comparisons.

Small budgets can only detect big gaps. If the user's budget buys 300 visitors per variant, rerun with a larger `--target` until the visitor count fits, and tell the user that is the smallest difference this test can see. Agree on that before the money is spent.

Write into `test-plan.md`: primary metric, minimum visitors per variant (from `plan`), the bar (`--min-rate`, the lowest rate that still makes the product worth building), end date, and stop conditions (a broken page, an ad rejection, overspend).

## Read it after the end date

Export a CSV with one row per variant:

```
variant,visitors,cta_clicks,signups,spend
a,520,61,31,200
b,505,40,12,200
c,498,44,14,200
```

```
python3 scripts/compare.py results.csv --min-visitors 400 --min-rate 0.04
```

The script prints each variant's rate with a 95% Wilson interval, cost per conversion, pairwise tests, and one verdict:

| Verdict | Meaning | Usual decision |
| --- | --- | --- |
| `UNDECIDED` | A variant has fewer visitors than the minimum. | Extend or stop, as the test plan says. No winner is named. |
| `BELOW_BAR` | Even the best variant is under the bar. | Change the offer or drop the product. |
| `WINNER` | One variant beats each of the others. | Build with that angle as the PR headline. |
| `TIE` | The top variants cannot be told apart. | They pull alike. Choose on cost per signup or fit, or test the top two again. |

With `--min-rate` set, a `WINNER` can carry a `note:` line: the winner's interval starts under the bar, so more traffic could put it below. Record that build decision as provisional.

The verdict describes the data. The decision is the user's, written into `prfaq.md` with the counts.

## Habits that keep the result honest

- Decide at the planned end date. Looking early is fine; stopping early because one variant looks ahead inflates false winners.
- Report intervals, not only rates. Three signups against one is noise.
- Keep the losing angles and their numbers. A later test may need them.
- Count unique visitor ids. A reload is not a new visitor.
- Interest is not payment. A strong signup rate supports the next small step, such as a pre-sale, not a full build on its own.
