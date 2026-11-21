---
name: prfaq-smoke-test
description: Decide whether a product is worth building before building it. Writes an Amazon-style PR/FAQ, pulls three value-proposition angles from it, builds one fake-door landing page per angle, and compares their conversion under a small equal ad budget. Use when the user says "PR/FAQ", "working backwards", "smoke test", "fake door test", "three landing pages", or "validate demand before we build". Korean triggers "PR/FAQ 써", "워킹 백워드", "스모크 테스트", "페이크 도어", "랜딩 3개", "만들기 전에 수요부터". Not for a feature spec or for A/B testing a product that already ships.
---

# PR/FAQ Smoke Test

Find out whether a product deserves to be built, and which reason to buy it wins, before writing product code. One chain:

**PR/FAQ → three angles → three pages → small equal ads → compare → build the winner, or nothing.**

The PR/FAQ is the cheap filter: if the press release cannot make the target customer care, stop there. The smoke test is the behavioral filter: three pages that differ only in the message, and real visitors deciding which message they act on.

Work done on the user's machine is free to do. Three steps reach the outside world: **publishing pages, collecting emails, and spending ad money**. Each one waits for the user's explicit go-ahead in this task.

## Steps

### 1. Pin the bet

Collect the customer, the problem, the product idea, the price (or `[TBD]`), what the test will decide (build, change, or drop), and the money and days the user will spend. Read the conversation, files, and repo first. Ask the user only what they alone know, one question at a time.

Done when: one line reads *"We are deciding whether to build [product] for [customer]. The test spends at most [budget] over [days]."* Unknown values stay `[TBD]`.

### 2. Write the PR/FAQ

Read [references/prfaq.md](references/prfaq.md) and fill its template. The press release is dated on the imagined launch day and fits on less than one page. The FAQ has an external part (what customers ask) and an internal part (cost, risk, economics, the riskiest assumption).

Then judge the release as the target customer would. Name its weakest line. If the headline and first paragraph would not make that customer want the product, say so plainly, and stop or rewrite before going further.

Done when: the PR/FAQ is saved as `prfaq.md`, your verdict is written under it, and either the verdict is "compelling" or the user chose to continue anyway.

### 3. Pull three angles

An **angle** is one reason a customer would pick this product. Draw each from a different line of the PR/FAQ. Common sources: the outcome they get, the pain that goes away, the mechanism that makes it believable, speed or price, who it is for.

Three angles are three different reasons to buy. The test: a real customer could prefer A and shrug at B. Three phrasings of one reason fail that test, so replace one.

For each angle write: headline (10 words or fewer), subheadline, three supporting points, CTA label, the PR/FAQ line it came from, and the assumption it tests.

Done when: `angles.md` holds a three-row table, each row traced to a PR/FAQ line, and every pair passes the prefer-A-shrug-at-B test.

### 4. Build three pages

Read [references/landing-pages.md](references/landing-pages.md). Fill the `product` JSON block of [assets/landing.html](assets/landing.html) once, then copy the file as `a.html`, `b.html`, `c.html` and edit only the `angle` JSON block in each. The `product` block, layout, price, form, and footer stay byte-identical, so the message is the only variable.

The CTA opens a **fake door**: an honest panel saying the product is not available yet, with an optional waitlist email. It never takes payment.

Open each page in a browser, click the CTA, submit a test email, and watch the events.

Done when: `diff a.html b.html` and `diff a.html c.html` show changes inside the `angle` block only, and each page fires `view`, `cta_click`, and `signup` with its own variant id.

### 5. Fix the rules before launch

Write `test-plan.md` before any traffic: primary metric, traffic source, budget per variant, run length, minimum visitors per variant, the bar a winner must clear, and stop conditions. Size the test with `python3 scripts/compare.py plan` (see [references/reading-results.md](references/reading-results.md)). If the budget cannot buy enough visitors to detect the difference the user cares about, say so now, while the money is unspent.

Done when: every field in `test-plan.md` is filled or marked `[TBD]`, and the user has approved the launch.

### 6. Launch

Deploy the three pages on the user's static host, one URL per variant. Give each variant its own ad set with the same audience, budget, schedule, and format, and let each ad repeat its page's headline (**message match**). Run all three at the same time. Before spending, confirm the privacy notice, the ad platform's policy on not-yet-available offers, and any rules for regulated categories such as health or finance.

Done when: three live URLs load, events from each arrive where the user stores them, and the ads are approved.

### 7. Read the result and decide

Export per-variant counts to a CSV and run `python3 scripts/compare.py results.csv` with the minimums and bar from `test-plan.md`. Report each variant's rate with its interval, cost per signup, and the verdict line. A variant under its minimum visitors makes the whole test `UNDECIDED`, and the test plan's rules decide whether to extend it.

Write the decision into `prfaq.md`: build with angle X, change the offer, drop it, or undecided. If building, the winning angle becomes the PR headline. Keep the losing angles and their numbers in the record.

Done when: `prfaq.md` has a dated decision with the counts it rests on, and the verdict matches what `compare.py` printed.

## Honesty

- A fake door measures interest. To learn whether people will pay, show the price before the waitlist form, as Buffer did with a pricing page. Taking real money is a pre-sale, a different test with its own delivery and refund promises.
- The customer quote in the press release is imagined and marked so. Pages and ads carry no testimonials or user counts that have not happened.
- Emails go only to the user's own store, with a one-line promise of how they will be used. Analytics events carry the variant and event name, never the email.
- Small samples mislead. Report the intervals, name the winner only when the pre-set rule names it, and keep the losers' numbers.

## Credits

- PR/FAQ: Colin Bryar and Bill Carr, *Working Backwards* (2021), on how Amazon writes a press release and FAQ before building. [Amazon's excerpt](https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes).
- Landing page before product: Joel Gascoigne, [Idea to Paying Customers in 7 Weeks](https://buffer.com/resources/idea-to-paying-customers-in-7-weeks-how-we-did-it) (Buffer).
- Further reading: David J. Bland and Alexander Osterwalder, *Testing Business Ideas* (2019); Ash Maurya, *Running Lean*, 3rd ed. (2022); Alexander Osterwalder et al., *Value Proposition Design* (2014); Tim Ash et al., *Landing Page Optimization*, 2nd ed. (2012).

The text is new. The three-angle chain, the byte-identical page rule, and the comparison script are this skill's own combination, not an official method from these authors.
