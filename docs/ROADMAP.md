# Roadmap — montesprout-site

> **Future only.** Scope prose for *unshipped* phases: what a phase means, why, what's out of scope.
> No checkboxes, no completion markers — execution state lives in `PROGRESS.md` § Roadmap alone, and a
> phase's prose is pruned from this file when it ships. The story of what happened is `docs/JOURNAL.md`.
>
> Phase labels continue the app repo's **Phase 18** because this repo's commit messages reference them;
> new site phases take 19+ in *this* repo's namespace (unrelated to the app repo's Phase 19+).

---

## Phase 18 — Marketing/legal site (montesprout.app)

The site is live at **montesprout.app** on enforced HTTPS with its landing, privacy and support pages.
Only one box remains open.

- **18.7 — real app screenshots for the landing page** (split out of 18.5, owner call 2026-08-16). A
  strip of real screens on `index.html`, replacing nothing — it slots between the highlights and the
  closing panel. The three-step Notice → Save → Draft strip already covers the visual gap, so this is a
  page that reads finished getting better, not a half-built page getting finished.

  **It needs an app build, so it needs a free checkout.** Building in a `MonteSprout` checkout another
  session is mid-flight in risks landing `Package.resolved` drift under that session. Use a
  `sim-sandbox` clone and DEBUG sample data — **never the home phone's real classroom**, whose child
  names would end up on a public page. Out of scope: a device frame/mockup treatment (that is Phase 21's
  call), and App Store screenshots (app-side, different aspect ratios and rules).

---

## Phase 19 — Post-launch site growth

Two post-tester niceties, re-filed to backlog on 2026-08-16. Neither gates anything.

- **19.1 — cookieless web analytics** (PostHog or similar). **Blocked on a decision, not on work:** this
  repo's standing convention is *plain HTML + CSS, zero JavaScript*, and `tests/test_site.py` asserts a
  script count of zero on every page. Adding analytics means either a script tag — which requires a
  recorded decision in `docs/DECISIONS.md` and a change to the test — or a log-based/serverless approach
  that keeps the zero-JS property. Decide that first; the integration itself is small either way. The
  open question is registered in `PROGRESS.md` § Needs You, tagged `(not blocking until 19.1)`.
- **19.2 — "notify me at launch" email capture.** A static site has no backend, so this is a form
  action pointed at a hosted list provider, or a `mailto:`. Whatever is chosen must not smuggle a
  tracking script in through the side door (see 19.1) and must not collect anything the privacy page
  doesn't account for.

---

## Phase 20 — School-admin trust one-pager

**Trigger: the school-paid conversation.** Not scheduled — it starts when a school procurement
discussion is real.

Schools buy on a different axis than teachers do: a privacy/AI one-pager an administrator can forward.
The substance is already true and already *stated* by 18.3's privacy page — client-side
pseudonymization, never-custodian, zero retention, the on-device assist tier. This phase is the
school-facing productization of it: a dedicated page written for an administrator rather than a
teacher, and DPA/written-agreement readiness alongside it. The app-side halves of the same package (an
in-app "how AI sees your data" explainer near the report screen) stay in the app repo's roadmap.

Adding a page here is never a one-file change — the page, its `canonical`, its `sitemap.xml` entry, and
a link from every other page's nav *and* footer all move together, and the tests fail until they do.

---

## Phase 21 — Design pass

**Post-tester.** The current site is deliberately hand-rolled: on-brand Sunrise (Quicksand + Nunito,
Sage accent, paper background, the app's leaf mark) but with no design-handoff round — an owner call on
2026-08-16, taken because it is cheap to restyle later and a design round would have blocked the
privacy URL that external testing was actually waiting on.

This phase spends that credit: a real design round on the landing page. The constraints that survive it
are the ones in `CLAUDE.md` — zero JavaScript, tokens transcribed from the app rather than invented, one
source for the leaf mark — because they are what keeps the site and the app looking like one product.
