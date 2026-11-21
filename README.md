# prfaq-smoke-test

English · [한국어](README.ko.md)

An agent skill that tells you whether a product is worth building, and which pitch wins, before you write product code.

**PR/FAQ → three angles → three landing pages → small equal ads → compare → build the winner, or nothing.**

- **Working Backwards first.** The agent writes an Amazon-style press release and FAQ as if the product had launched. If the release cannot make the customer care, you stop there, for free.
- **Three angles, three pages.** It pulls three different reasons to buy from the PR/FAQ and builds one fake-door landing page per angle. The pages are byte-identical except for the message, so the message is the only variable.
- **Honest fake door.** The button opens a panel that says the product is not open yet and offers a waitlist. No payment, no fake testimonials, and the email never goes to analytics.
- **A verdict you can trust.** A small script sizes the test before you spend and reads the result after: `WINNER`, `TIE`, `BELOW_BAR`, or `UNDECIDED`.

## What you get

| File | What it holds |
| --- | --- |
| `prfaq.md` | Press release, external and internal FAQ, the agent's verdict, and later the decision with its numbers |
| `angles.md` | Three angles, each traced to a PR/FAQ line and the assumption it tests |
| `a.html`, `b.html`, `c.html` | Three single-file landing pages with a fake door and event tracking |
| `test-plan.md` | Metric, budget, minimum visitors, the bar, end date, fixed before launch |

Reading a result:

```
$ python3 scripts/compare.py results.csv --min-visitors 400 --min-rate 0.04
metric: signups per visitor, 95% Wilson interval
variant    visitors     signups    rate   interval          cost/conv
a               520          31   5.96%    4.23% – 8.34%         6.45
b               505          12   2.38%    1.36% – 4.11%        16.67
c               498          14   2.81%    1.68% – 4.66%        14.29
...
verdict: WINNER: a at 5.96% beats every other variant
```

<sub>Example numbers, not a real test.</sub>

## Install

Claude Code:

```
/plugin marketplace add robfold/prfaq-smoke-test
/plugin install prfaq-smoke-test@prfaq-smoke-test
```

Other agents, with the [skills CLI](https://skills.sh):

```
npx skills add robfold/prfaq-smoke-test
```

Or copy [`skills/prfaq-smoke-test/`](skills/prfaq-smoke-test/) into your agent's skills folder (`~/.claude/skills/` for Claude Code).

## Use

Tell your agent "write a PR/FAQ and three landing pages for this idea", "run a smoke test before we build", or call the skill by name. Give it the customer, the problem, and the idea; it looks up the rest and asks only what it cannot find.

The agent writes and builds everything locally. Publishing the pages, collecting emails, and spending on ads each wait for your explicit go-ahead.

The comparison script needs only Python 3. The landing page needs no build step and no dependencies.

## When to use something else

If the product already ships and has traffic, run an A/B test in your own product analytics instead. If you only need the PR/FAQ document, stop after step 2.

## Credits

The PR/FAQ comes from Colin Bryar and Bill Carr's *Working Backwards* (2021) and [Amazon's excerpt of it](https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes). The landing-page-before-product idea follows Buffer's [Idea to Paying Customers in 7 Weeks](https://buffer.com/resources/idea-to-paying-customers-in-7-weeks-how-we-did-it). The text is new; the three-angle chain, the identical-page rule, and the script are this skill's own combination. The end of [SKILL.md](skills/prfaq-smoke-test/SKILL.md) lists further reading.

## License

[MIT](LICENSE)
