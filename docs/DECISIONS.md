# Decisions — montesprout-site

> Choices + rationale, append-only, dated. What we chose, why, and what we rejected. **Not** how a
> phase went (that's `docs/JOURNAL.md`), **not** step plans (that's `docs/ROADMAP.md`).
>
> Entries dated 2026-08-16 up to and including Phase 18.4 were **migrated from the app repo**
> (`MonteSprout`, `docs/DECISIONS.md`) by `/adopt` when this repo took ownership of the site roadmap.
> They are condensed here to the parts that bind *this* repo; the full originals stay over there and are
> named per entry. The app-side halves of Phase 18 (App Store Connect wiring, the AI-claims sweep) are
> not duplicated.

---

## 2026-08-16 — The site lives in its own public repo, as a sibling checkout

_(App repo DECISIONS, "2026-08-16" dec. 14 — the full alternatives are recorded there.)_

The site is `Mango-Grove-Labs/montesprout-site`, public, checked out as a **sibling** at
`~/Developer/montesprout-site`. Deploy is GitHub **Pages from a branch** — no CI, no secrets, no
Actions.

**Why its own repo.** The free org serves Pages only from public repos, and the app monorepo is private,
so "a `web/` folder in the monorepo plus an Actions deploy" was retired: a private monorepo on a free
plan can't Pages at all, and a CI mirror would need a PAT secret — owner input bought for nothing. The
company site (`Mango-Grove-Labs/mango-grove-labs` → mangogrovelabs.com) is the working precedent.

**Why a sibling, not a nested gitignored checkout.** One repo per folder tree, so `/commit` and the
autopilot loop never straddle two `.git`s. It matches the pattern already used for the fork and the
Mango packages. Nesting would have bought physical proximity and nothing else.

## 2026-08-16 — No design round for the dev-phase site

_(App repo DECISIONS, "2026-08-16" dec. 15.)_

Hand-rolled HTML/CSS reusing the company site's skeleton and SEO/OG conventions, with the tokens swapped
to Sunrise (Quicksand + Nunito, Sage accent, paper background, the app's leaf mark). Temporary but
on-brand.

**Why.** A design round would have blocked the privacy-policy URL that external testing was actually
waiting on, to improve a page nobody had visited yet. Restyling later is cheap; the real design pass is
scheduled as Phase 21. **The constraints that outlive the restyle** — zero JavaScript, tokens
transcribed rather than invented, one source for the leaf mark — are what keep the site and the app
looking like one product, and they are recorded in `CLAUDE.md` rather than left to the styling.

## 2026-08-16 — Phase 18.2: the guards that are worth their tests

_(App repo DECISIONS § "Phase 18.2 (+18.6)" — full record, including the rejected alternatives.)_

1. **The base path is a tested contract, not a note.** `index.html` and the content pages use relative
   asset paths; `404.html` **must** use root-absolute ones, because GitHub serves that one file at any
   missing depth, so a relative href there resolves differently per URL. `tests/test_site.py` derives
   the expected base from **whether a `CNAME` file exists** — so the domain swap starts by adding the
   file and reading the failures it produces. The failure list *is* the checklist. Rejected: a README
   paragraph, which nobody re-reads under a DNS change. (Vindicated at 18.4: ten red tests, worked to
   green, done.)
2. **The app's privacy-claim bans are ported to the served HTML.** `PrivacyClaimConventionTests` exists
   in the app because it twice told teachers their data never leaves the device, which stopped being
   true at Phase 13. A marketing page is exactly where that absolute grows back, so the same patterns
   scan the HTML here. Red-checked with a planted "Your notes never leave your iPhone." Rejected: an
   offline-only pitch with the AI path unmentioned — three cards away from "reports are drafted for
   you", it reads as a denial.
3. **`robots.txt` is committed even though it was inert, and the file says so.** Crawlers read
   robots.txt only at the host root, which a project site does not own. Kept rather than deferred so
   18.4 had nothing extra to remember; it became load-bearing the moment the domain landed.
4. **18.6 pulled forward into 18.2** (owner call, in the review loop): favicon, OG card, touch icon and
   SEO meta. The two PNGs are **generated deterministically** by `tools/make_images.py` (same leaf
   beziers, the app's faces vendored under `tools/fonts/`, no PNG `tIME` chunk) — two runs hash
   identically, so regenerating without a content change produces no diff. `og:image:width`/`height` are
   asserted against the file's real PNG header, so a resize that skips the meta tags fails.
   `apple-touch-icon` is a real 180×180 PNG: Safari ignores an SVG in that slot, so pointing it at
   `favicon.svg` (as the company site does) is a silently dead tag.

## 2026-08-16 — Phase 18.3: page shape, and copy that had to change

_(App repo DECISIONS § "Phase 18.3" — includes the full claim→source trace.)_

1. **Root-level `privacy.html` / `support.html`, not `privacy/index.html` directories.** Extensionless
   URLs would need a *third* base-path rule (sub-pages resolving assets via `../`) purely for cosmetics,
   and `montesprout.app/privacy.html` is a perfectly ordinary policy URL for App Store Connect.
2. **Support is written as FAQ answers**, not the drafts annex's single paragraph — the questions a
   first tester actually asks: where is my data, how do I export, how do I delete, how do I turn
   analytics off, does it work offline.
3. **Three drafted claims were wrong and were corrected against the code, not softened.** The one to
   remember: both the annex and the app's telemetry catalog said the analytics guarantee is that
   `AnalyticsValue` has "no free-form case" — it has `case string(String)`, and always has. Two
   documents had rounded a convention up to a structural promise, and a public privacy policy was about
   to publish it. Fixed on the page *and* in both sources, because fixing only the page leaves the thing
   that generates the next overclaim. Also corrected: "export your complete data" (media is
   metadata-only by design) and a `⟪placeholder⟫` that would have shipped as literal brackets.
4. **The ported guard widened, the app's did not.** "classroom data stays in the teacher's device" is
   the retired absolute in the third person; the site's copy of the pattern now covers possessive third
   person, while the app's own test stays deliberately narrow — the narrow pattern is right for source
   files, and widening it there would invite false positives on prose the app never writes.
5. **Public contact is `support@mangogrovelabs.com`** (it already works). A `montesprout.app` address
   takes over only if forwarding for the domain exists — a one-line page edit plus an ASC field.

## 2026-08-16 — Phase 18.4: the apex domain

_(App repo DECISIONS § "Phase 18.4" — full registrar record.)_

1. **Apex `montesprout.app`, `www` redirecting to it.** GitHub Pages' four `A` and four `AAAA` records
   plus a `www` CNAME, replacing the parking records. The IPs were **re-resolved from GitHub's live
   Pages host at the time of the change**, not copied from the company site's README — which explicitly
   says not to trust its own list. The Email-Forwarding SPF `TXT` was deliberately left alone.
2. **`.app` is on the HSTS preload list**, so HTTPS here is mandatory rather than a setting.
3. **The org-level domain-verification `TXT` was added** (Settings → Pages, org scope), so nobody can
   re-bind Pages to the domain if it ever lapses or is detached.
4. **A local `dig` is not evidence right after a DNS change** — recorded as an operating rule, not a
   finding. The site looked dead from one Mac for ~9 minutes while the certificate was already approved,
   purely a cached parking IP in macOS's own resolver. `dscacheutil -q host -a name <domain>` shows what
   apps actually see; `curl --resolve <domain>:443:<ip>` proves the server independently.

## 2026-08-16 — `/adopt`: this repo owns its own roadmap

**Supersedes** the app repo's Phase 18.2 dec. 5 ("the site repo carries no planning docs, by design").
That decision was correct while the site was one deliverable of an app phase; it stopped being correct
once the site became a thing work gets *added* to. Its stated fear — two `PROGRESS.md` files drifting —
is answered by ownership rather than absence: the app repo's Phase 18 becomes historical record, and
site completion truth lives here alone.

1. **Owner-chosen, this run.** The alternative considered and rejected was keeping the roadmap in the
   app repo and giving this repo docs only — which leaves `autopilot-doctor.sh` at exit 3 and every
   roadmap tool dead here, i.e. it does not solve the stated problem.
2. **Phase labels continue from 18; new site phases take 19+ in this repo's namespace.** Shipped labels
   are identifiers — this repo's four commits are `feat(18.2)`…`feat(18.5)`, and the app repo's JOURNAL
   and DECISIONS index the same numbers. Renumbering to Phase 1 was rejected for that reason. The
   accepted cost: "Phase 19" means MangoDesign in the app repo and post-launch site growth here.
   Contained, because the repos are separate and each parser reads only its own `PROGRESS.md`.
3. **`18.1` stays in the app repo.** It is the monorepo restructure — app-side work that happens to
   carry an 18-series label. Not copied here.
4. **No `docs/architecture.md` in this repo.** The site's entire engineering contract is four rules in
   `CLAUDE.md` (zero JS · transcribed Sunrise tokens · one leaf source · the base-path split), and the
   *authoritative* source for the tokens and the beziers is the app's `docs/architecture.md` §8 and
   `DesignSystem/Motifs.swift`. A second architecture file here would be the exact drift
   `tests/test_site.py` exists to catch. The `PROGRESS.md` router points at the app's file instead.
5. **The repo root stays the deployed site — no `<surface>/` fold.** The monorepo structure spec would
   normally want `web/`, but GitHub Pages serves only a branch root or `/docs`. Root-serving is a hard
   constraint of the deploy, not a shortcut, and this repo is deliberately single-surface (no
   `server/`/`mobile/` folders are coming — the app is its own repo). Recorded so the structure audit
   reads this as a documented deviation rather than a migration to schedule.
6. **The five Phase 18 journal entries were copied, not moved.** The app repo's copies are untouched.
   Journals are append-only past, so the duplication cannot drift, and it makes this repo self-contained
   for the gotchas a future domain move or base-path change will need.
7. **`robots.txt` regained a `Disallow` list, for the surface this run created.** 18.2 dropped the
   inherited `Disallow: /docs/` on the stated grounds that "this repo has no `docs/`" — a premise this
   commit invalidates. `.nojekyll` makes Pages serve every file, so `/docs/`, `/PROGRESS.md` and the
   rest are now fetchable at the apex. They are public either way (public repo), so this is not a
   confidentiality fix; it is keeping internal planning prose out of search results for the product's own
   domain. `Allow: /` stays first, so the content pages are unaffected. `tests/` and `tools/` were added
   to the same list — they were already exposed before this run, and splitting the rule would be
   arbitrary.

## 2026-08-16 — The hero headline: one chosen, five kept, rotation declined

**Chosen (live):** *"Notes in seconds. Reports from evidence, not memory."*

It is the shortest line that states **both** of the product's strengths — how cheap capture is, and that
reports are built from the term's real notes rather than reconstructed from recall. "Not memory" does the
persuasive work in three words, because reconstructing a term from scraps and recall is exactly what a
guide does today. The sub-line was rewritten to carry what the headline leaves implicit (who it is for,
and that a note can be text, photo or voice) rather than restating it.

**Replaced:** *"You saw something important. Save it in ten seconds."* — owner disliked it. Diagnosis
worth keeping: it read as a landing-page trick, and it was the only line on the site making a
**quantitative promise nothing verifies**. "In seconds" is idiomatic; "ten seconds" is a number a
sceptical reader will test.

**Kept as candidates** (owner shortlist, for a future A/B — see ROADMAP § 19.3):

1. "Jot it while it's fresh. Report from evidence, not memory." — the chosen line without any speed
   number at all; the fallback if "seconds" ever feels like overclaiming.
2. "Quick notes all term. Real evidence when it counts."
3. "Reports built from what you saw, not what you remember." — best single-sentence option; drops the
   capture half to make the memory contrast the whole message.
4. "Montessori observation, made quick — and finally worth something at report time."
5. "Montessori observations. For the modern age." — the owner's own line. Positions by category rather
   than by benefit; the most brand-forward and the least specific, which makes it the most interesting
   A/B counterweight to the chosen line rather than a near-duplicate of it.

**Rotation declined for now (owner agreed).** Cycling headlines every N seconds was considered and
rejected on three grounds, none of them taste:
- **It costs a real property.** This repo is zero-JavaScript and `tests/test_site.py` asserts it. The
  CSS-only alternative puts every variant in the DOM at once, which means multiple `<h1>`s for crawlers
  and a screen reader announcing all of them.
- **It measures nothing.** Rotation is not A/B testing — with no analytics (19.1, itself blocked on the
  zero-JS decision) and effectively no traffic during private beta, every visitor sees a random line and
  nothing is learned.
- **Motion fights the brand.** A hero that swaps text on a timer is the opposite of "calm", and would owe
  `prefers-reduced-motion` handling.
The version worth building is a real A/B — one variant per visitor, held stable, measured — which is why
it is filed as **19.3, explicitly downstream of 19.1**, not as a rotation feature.
