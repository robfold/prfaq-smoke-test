# Building and launching the three pages

The test compares messages, so everything except the message stays fixed: same layout, same price line, same image (or none), same form, same host, same ad format. A difference in anything else gives a second explanation for the result.

## The template

[`assets/landing.html`](../assets/landing.html) is one self-contained file with no dependencies. Two JSON blocks drive it:

- `product`: name, price line, footer, the fake-door panel text, and the event `endpoint`. It is byte-identical in all three files.
- `angle`: `variant` (`a`, `b`, `c`), `headline`, `subheadline`, three `points`, and `cta`. It is the only block that changes.

Fill `product` in the template once, copy it to `a.html`, `b.html`, `c.html`, then fill each `angle`. For a non-English page, set `product.lang` and translate the panel text in `product.door`; the template's own words all live in the JSON blocks.

If the user wants a different design, change the template once before copying, so the three pages still share every line outside `angle`.

## Writing an angle

- The headline states the angle's reason to buy in the customer's words. A reader who sees only the headline should be able to say which angle it is.
- The three points support that same reason. A point that argues a different angle blurs the test.
- The CTA is a verb plus the outcome of this angle ("Get my fix", "Save on my repair"), not a generic "Sign up".
- The price line is the same on all three pages. Leave `product.price` empty to hide it, in all three.

## The fake door

Clicking the CTA records `cta_click` and opens a panel that says the product is not open yet, why the page exists, and what the email will be used for. Submitting an email records `signup` and shows a thank-you line.

Keep the panel honest: it states that the product does not exist yet, before asking for anything. If the user wants to test willingness to pay, the price line on the page does that job; the panel still takes no payment.

## Events and storage

Each page records three events with the same fields: `event`, `variant`, `vid` (a random visitor id kept in the browser), `ts`, `path`, and any `utm_*` parameters from the URL.

- `window.__smokeEvents` holds the events in the page, for local checks.
- If `window.dataLayer` exists (Google Tag Manager), each event is pushed as `smoke_view`, `smoke_cta_click`, or `smoke_signup` with `smoke_variant`. No email goes there.
- If `product.endpoint` is set, each event is POSTed to it as a JSON text body, and the `signup` event adds `email`. Point it at storage the user owns: a small serverless function writing to a database or sheet, or a form backend. The `text/plain` body avoids a CORS preflight; the endpoint must still allow the page's origin if it is on another domain.

Count visitors as unique `vid` values with a `view` event, not raw page loads. Tag the team's own visits (for example `?utm_source=internal`) and drop them before counting.

## Local check

Serve the folder (`python3 -m http.server`) and open each page. Click the CTA, submit a test email, and read `window.__smokeEvents` in the console: it should list `view`, `cta_click`, `signup` with the page's variant. With an endpoint set, confirm the three events arrived there. Then run `diff a.html b.html` and `diff a.html c.html`: only lines inside the `angle` block may differ.

## Launch

Get the user's go-ahead first; publishing, collecting emails, and ad spend all reach real people.

- **Host**: any static host the user already uses. One URL per variant (`/a`, `/b`, `/c`, or three files). The template sets `noindex` so test pages stay out of search results. Make sure redirects keep the query string, or the `utm_*` values are lost.
- **Ads**: one ad set per variant. Same audience, placement, schedule, and budget; same image or video if any. The ad's text repeats its page's headline. Tag each ad's URL with `utm_content=a|b|c`.
- **Even spend**: use a fixed budget per ad set and turn off settings that move budget to the ad the platform thinks is winning. Those settings pick a winner on thin data and starve the other variants.
- **Same time**: run the three in parallel, start and stop together.
- **Without ads**: if traffic comes from one shared source (a newsletter, a community post), send it to a small router page that picks `a`, `b`, or `c` at random, remembers the pick so a returning visitor sees the same page, and keeps the query string. Random assignment replaces message match in that case.

```html
<script>
  const arms = ["a", "b", "c"];
  let v;
  try { v = localStorage.getItem("smoke_arm"); } catch {}
  if (!arms.includes(v)) {
    v = arms[Math.floor(Math.random() * arms.length)];
    try { localStorage.setItem("smoke_arm", v); } catch {}
  }
  location.replace(v + ".html" + location.search);
</script>
```

## Before spending

- **Privacy notice**: who collects the email, for what, how to be removed. Local law may ask for more (GDPR in the EU, PIPA in Korea, and others).
- **Ad policy**: ad platforms reject offers that misrepresent availability. Pages that say "coming soon" or "join the waitlist" plainly, before asking for anything, are the honest form.
- **Regulated categories**: health, medical, finance, supplements, and similar fields often need review or pre-approval of ad claims. Check the rules for the user's country and category before the ads run.
