# Journal — montesprout-site

> **Past.** Append-only, one entry per phase/session, newest last: what shipped, test counts, gotchas.
> Never auto-loaded, so it grows freely — this is the one place per-phase narrative belongs. No commit
> shas (a commit can't contain its own sha); `git log --follow docs/JOURNAL.md` recovers the mapping.
>
> The five Phase 18 entries below were **migrated verbatim from the app repo** (`MonteSprout`,
> `docs/JOURNAL.md`) by `/adopt` on 2026-08-16, when this repo took ownership of the site roadmap. The
> originals are untouched over there — this is a copy, not a move, and the site half of that history now
> lives with the site. They were written while the site was still a *project* Pages site, so URLs inside
> them read `mango-grove-labs.github.io/montesprout-site/…`; 18.4 is the entry where that changes.
>
> **They were written from the app repo, and kept verbatim — so read their deixis from there.** Inside
> those five entries "this repo" / "this checkout" / "beside this one" mean the **app** repo
> (`~/Developer/MonteSprout`), not this one. Two lines depend on it: 18.2's "sibling checkout beside
> this one" is the site repo sitting beside the *app* checkout, and 18.5's "building in this checkout
> risks the `Package.resolved` drift trap" is about the *app* checkout — this repo has no Swift package
> and nothing to drift. That second line is 18.7's real constraint, so it matters.

---

## 2026-08-16 — Phase 18.2 (+18.6): the site goes live

`https://mango-grove-labs.github.io/montesprout-site/` — MonteSprout's marketing/legal site, in its own
public repo (`Mango-Grove-Labs/montesprout-site`, sibling checkout beside this one), Pages
deploy-from-branch, no CI. Plain HTML + CSS, zero JavaScript, no build step: a push to `main` is a
deploy. Structure came from the Mango Grove Labs company site; every token is the app's Sunrise, and the
leaf mark is `LeafArt`'s two beziers verbatim in the favicon, both page headers and the OG generator.
**42 structural tests, green**, stdlib `unittest` — they stand in for the build step there isn't one of.

Two of them are the point. The **base-path** tests derive what they expect from whether a `CNAME` file
exists, so 18.4's domain swap starts by adding that file and reading the 7 failures it produces — the
suite is the checklist, not a README paragraph. And the app's **`PrivacyClaimConventionTests`** bans are
ported to the served HTML, so 18.3's privacy page is born under the same guard the app has: the page may
not claim notes never leave the device, because report generation posts pseudonymised text through the
proxy. Both were red-checked by planting a violation (a `CNAME`; "Your notes never leave your iPhone.")
before being trusted.

Gotchas worth keeping. `404.html` is served by GitHub at *any* missing depth, so its links must be
root-absolute while `index.html`'s stay relative — the two files genuinely differ. `robots.txt` does
nothing on a project site (crawlers read it only at the host root, which 404s and isn't ours to create);
it's committed with a comment saying so rather than deferred. Pillow's line drawing has no
anti-aliasing, so the OG leaf's vein is stamped as round dabs along the flattened bezier, and the body's
1.2-unit stroke — right at 13pt in the app — was dropped, since at 104px it only produced a mitre
artefact at the tip. `apple-touch-icon` is a real 180×180 PNG: Safari ignores an SVG there.

18.6 (favicon + OG + SEO meta) was pulled forward into this box by owner call during the review loop, so
Phase 18's remaining work is 18.3 (privacy + support), 18.5 (the landing page) and 18.4 (owner-op DNS).

## 2026-08-16 — Phase 18.3: the privacy policy (and what writing it found)

`…/montesprout-site/privacy.html` and `…/support.html` are live. That URL is the last thing 16.2c's Test
Information was waiting on, so external testing is now unblocked on the agent side. Both pages came from
the drafts annex written during the 2026-08-16 planning session — which told its own reader not to trust
it without re-checking each claim against the code. Worth doing: three claims were wrong.

The analytics one is the one to remember. The annex *and* `docs/telemetry-catalog.md` both said the
guarantee is that `AnalyticsValue` has "no free-form case"; it has `case string(String)`, and has all
along. The type's own doc comment says the accurate thing — no free-form `track()` entry point, a closed
event enum, no `.any` case, and `.string` kept prose-free by catalog and review rather than by the
compiler. Two documents had quietly rounded that up to a structural promise, and a public privacy policy
was about to publish it. Corrected on the page, in the catalog, and in the annex's trace table, because
fixing only the page would have left the source that generates the next overclaim.

Also: "export your complete data" isn't true (media is metadata-only by design — the Export boundary), and
§5 still held an unresolved `⟪placeholder⟫` that would have shipped as literal brackets.

The guard ported in 18.2 paid for itself immediately. The school-facing paragraph said "classroom data
stays in the teacher's device" — 40.7's retired absolute in the third person, which the app's pattern
doesn't match because the app never writes about "the teacher". Sentence rewritten; the site's copy of the
pattern widened to the possessive third person (the app's own test left deliberately narrow). Red-checked
both ways — and the first attempt at that control was itself vacuous, because the replacement string used
a curly apostrophe where the file has `&rsquo;`.

42 → 50 tests: link and fragment integrity, every content page reachable from every other, the sitemap
listing exactly the content pages, and the policy's "Last updated" date pinned against its own git date.
Each red-checked by planting its failure. Both pages verified rendering at 1280px and 390px.

## 2026-08-16 — Phase 18.5: the landing page

The holding page is gone; `…/montesprout-site/` is now a real landing page — hero on the capture moment,
a short "what it is", a Notice → Save → Draft strip, five highlights, and a "Coming to the App Store"
close. The copy comes from `docs/research/montessori-software-gaps.md`: the incumbents' 1.2★/1.9★ iOS
reviews complain about exactly one thing, capture friction, and the research's conclusion is that the
ten-second moment is the gap to own. So the page sells that moment rather than a feature list.

Two things worth remembering. First, **the plan's own headline was unusable**: ROADMAP § 18.5 specified
"works fully offline — your data lives on your device", which is the absolute the app retired at 40.7 and
the site's ported guard bans outright. The phase note added at 18.2 predicted this, which is the only
reason it was caught before it was written rather than after. Second, **three claims changed after
reading the code, and each rewrite was better copy than the draft**: quick capture's `studentID` is
optional ("the common case, since matching is cleanup's job") so you needn't name the child at all;
`QuickCaptureFeature` is `savesDraft`, so closing the sheet *saves* rather than merely "not losing";
and "file it later, or never" was false — unfiled captures prune after 7 days.

The screenshot strip 18.5 called for is split to **18.7**. It needs an app build, the only current build
belongs to the concurrent Phase 49 session, and building in this checkout risks the `Package.resolved`
drift trap landing under them — owner chose ship-now. The three-step strip covers the visual gap, so the
page reads finished rather than half-built.

50 tests green (no new ones — the landing page is copy and layout over existing primitives, and the
link/anchor/reachability guards from 18.3 already cover it). Verified at 1280px and 390px.

## 2026-08-16 — Phase 18.4: montesprout.app

The domain is live and HTTPS is enforced. Owner logged into Namecheap; the parking records (an apex URL
Redirect and a `www` CNAME to Namecheap's parking page) were replaced with GitHub Pages' four `A`, four
`AAAA`, and a `www` CNAME. IPs were re-resolved from GitHub's live Pages host rather than copied from a
README. The Email-Forwarding SPF record was left alone. `www` and the old `github.io` URL both 301 to the
apex now.

**The suite did the migration.** Adding `CNAME` turned ten tests red, each naming a URL still on the
project subpath; the swap was working that list to green rather than hunting through files. That is the
whole reason 18.2 built it this way, and it worked exactly as designed — including catching robots.txt's
now-false "this file is inert" comment. Post-swap the suite runs with **zero skips** for the first time.

Two gotchas worth remembering. Namecheap's DNS editor is AngularJS + Select2: the type control is a
styled overlay over a hidden `<select>` with *numeric* option values, and the inputs are `ng-model`-bound,
so setting `.value` does nothing — it needs the native setter plus `input`/`change` events, and a jQuery
`.trigger('change')` for the select. And after the change, `https://montesprout.app` looked dead from this
machine for ~9 minutes *while the certificate was already approved* — purely the local resolver caching
the old parking IP. Public resolvers were correct immediately, and `curl --resolve` proved the site was
serving. A local `dig` is not evidence right after a DNS change.

50 site tests green. Every page, asset, the sitemap, robots and the depth-404 verified over HTTPS on the
real domain. Remaining in Phase 18: only 18.7 (screenshots), plus an optional org-level domain-verification
TXT that needs a GitHub browser login.

## 2026-08-16 — Phase 18.4 follow-up: domain verified, and the DNS-cache red herring

`montesprout.app` is **Verified** for the org (Settings → Pages), which stops anyone re-binding Pages to
it if it ever lapses. The challenge TXT went in at Namecheap beside the A/AAAA/CNAME set; Namecheap
lowercases the host, which DNS doesn't care about.

The part worth remembering is the false alarm. The site looked broken from this Mac — `curl` and Safari
both failed — while it loaded perfectly in Chrome and returned 200 with a valid certificate when the IP
was pinned. Cause: **macOS's own resolver was still caching Namecheap's parking IP**, and `dscacheutil -q
host` proves it directly while `dig` cannot (dig queries DNS servers, not the system cache). Chrome
bypasses it with its own Secure DNS. Fix is `sudo dscacheutil -flushcache; sudo killall -HUP
mDNSResponder`. Two diagnostics worth keeping for any future domain move: `dscacheutil -q host -a name
<domain>` is what apps actually see, and `curl --resolve <domain>:443:<ip>` proves whether the *server*
is fine independent of any local resolution.

Second Namecheap gotcha: a saved row can render blank for a moment and look like a failed save. Re-read
the record list before retrying, or you will enter the record twice.

## 2026-08-16 — `/adopt`: the site repo gets its own cursor

The repo was born deliberately doc-less: 18.2's decision 5 said the site carries no planning docs, its
`CLAUDE.md` routed to the app repo's `PROGRESS.md` § Phase 18, and the stated reason was that a second
`PROGRESS.md` "would drift the moment either side moved." That was right while the site was one
deliverable of an app phase. It stopped being right once the site became a thing you add work to.

The cost was concrete: `autopilot-doctor.sh` exited **3** (*not an autopilot repo*) and the progress
parser exited **1**, so `/progress`, `/roadmap`, `/next`, the statusline and the autopilot loop were all
dead here. Planning site work meant editing the app repo and implementing in this one, across two `.git`
trees — the exact straddle decision 14 created the sibling repo to avoid.

So this repo now owns the site roadmap. What that took: a root `PROGRESS.md` carrying **Phase 18 with
its labels verbatim** (18.2–18.7 — this repo's commit messages are `feat(18.2)`…`feat(18.5)`, and
shipped labels are identifiers), the three backlog items from the app repo's ROADMAP § 18 promoted to
real phases 19–21, a `docs/` set (ROADMAP, OVERVIEW, JOURNAL, DECISIONS, a pointer PRD), and the five
Phase 18 journal entries copied across so a session working on the site never has to open the app repo
to find out why `404.html` is the one file with root-absolute paths.

Two things deliberately **not** done. There is **no `docs/architecture.md`** here: the site's whole
engineering contract is four rules in `CLAUDE.md`, and the authoritative source for the Sunrise tokens
and the leaf beziers is the app's `architecture.md` §8 — a second architecture file is precisely the
drift `tests/test_site.py` exists to catch. And the repo is **not** folded into a `<surface>/` folder,
which the monorepo structure spec would otherwise want: GitHub Pages serves only a branch root or
`/docs`, so root-serving is a hard constraint of the deploy, not a shortcut.

`18.1` was left behind on purpose — it is the app's monorepo restructure, app-side work that happens to
carry an 18-series label. It stays in the app repo's Phase 18 where it belongs.

One served file did change, and only because the docs arrived: `robots.txt` got a `Disallow` list back.
18.2 had dropped the inherited `Disallow: /docs/` because "this repo has no `docs/`" — true then, false
as of this commit, and `.nojekyll` means Pages serves every file. Nothing confidential (the repo is
public), but `montesprout.app/docs/JOURNAL.md` has no business in search results for the product's
domain.

Doctor **clean**, parser green (`Phase 18/21 · 18.7/18.7 · 5/10 sub-phases · 50%`), 50 site tests still
green — no page, asset or test was touched.

**Then it was reviewed, and the review was worth running.** `/adopt` hands straight to `/commit`, whose
own contract says it assumes review already happened — so the convergence commit went out unreviewed,
and green tests plus a clean doctor were not evidence otherwise: both were green while two real defects
sat in the diff. The first was self-inflicted routing — `CLAUDE.md`'s zero-JS escape hatch still said to
record the decision in the *app* repo's `DECISIONS.md`, one bullet below a section this same commit had
rewritten, and it happens to be the gate on 19.1. The second: 19.1's blocking question (does the site
get JavaScript?) lived only in prose, while `Needs You` — the surface fleet, `/progress` and autopilot
actually read — said `_none_`; it is now registered with the deferred tag. Three smaller fixes followed:
the migrated entries' deixis is explained above (18.5's "this checkout" means the *app* checkout, which
matters because that sentence is 18.7's constraint), Pages' source folder is pinned to `/ (root)` in
`CLAUDE.md` and `README.md` now that a `/docs` source would serve the roadmap as the website, and
`README.md` § Layout finally lists the planning layer it had never heard of.

## 2026-08-16 — The hero headline, and a guard that was vacuous until it was tested

The hero is now **"Notes in seconds. Reports from evidence, not memory."** — the shortest line carrying
both of the product's strengths, where the old one ("You saw something important. Save it in ten
seconds.") was the only copy on the site making a quantitative promise nothing verifies. The sub-line was
rewritten to add what the headline leaves implicit rather than restate it. Five runner-up lines are kept
in DECISIONS for the A/B filed as 19.3; rotation-on-a-timer was considered and declined there, with
reasons.

Typography: the headline is two beats, so it gets a `<br class="hero__break">` that CSS hides below
40rem, and `.hero__title`'s measure went 760px → 900px because at the old width the second beat wrapped
and stranded "memory." alone on a line.

**The bug worth remembering.** Hiding that `<br>` fused its neighbours — mobile read
"seconds**.**Reports" while desktop looked perfect, because desktop shows the `<br>`. Fixed with a space
before the tag. Then the first regression test written for it **passed against the planted bug**: this
suite's parser joins text nodes with a space, so any check on parsed text is blind to fusing *by
construction*. The real guard works on the raw source and derives the hideable classes from the
stylesheet (anything CSS sets to `display: none`), plus a test asserting the rule matched something, so
it can't quietly go vacuous again. Both were red-checked by planting the failure — which is the only
reason the first version's uselessness was ever noticed.

52 tests green (+2). Verified at 1280px and 390px.

## 2026-08-16 — Phase 18.7: real screenshots, and how to build beside a busy session

The landing page shows three real screens now — the quick-note sheet, a child's evidence page, and a
generated report with its "Evidence used" panel open. That last one is the point: the headline claims
reports come from evidence rather than memory, and the screenshot shows the dated notes sitting under
the paragraph.

**The interesting part was doing it while another session held the app checkout.** A `git worktree` at
the last commit solved it structurally: its own `Package.resolved`, its own DerivedData, and it builds a
commit rather than someone's work in progress. Zero drift in either tree afterwards. The one global thing
that *would* have leaked is `flowdeck config` — it is per-machine, so it was snapshotted and restored,
and every command passed `-w`/`-S` explicitly. Own sim clone via `sim-sandbox start`, deleted after;
theirs untouched.

Two safety checks worth repeating. The sandbox clone inherits the home phone's data, so the names on
screen were verified against `SampleData.swift` before a single shot was taken — Maya, Leo, Ava… teacher
Sarah, Primary Room — an exact match for the fixed-UUID fixtures, so no real child appears. And the
report screenshot needed no AI call at all: the sample data already carried a generated report.

_Re-verified independently in review, since this is the one claim the site cannot take back: the roster
matches `Models/SampleData.swift`, and `report.webp`'s paragraph is **verbatim** the draft pinned by
`ReportGenerationTests.sampleDraftIsPinned` — a snapshot test over the fixtures, so that screen provably
came from sample data rather than a classroom._

Gotchas: **FlowDeck's screenshots are 1× (402×874) with no scale option** — fine for agent verification,
too soft for a retina page, so the pixel grab (only) went through `simctl` for the native 1206×2622.
**WebP over PNG** was a 715 KB → 95 KB difference. And the full-page browser screenshot showed three
blank boxes at first, which was `loading="lazy"` not a broken asset — worth knowing before debugging the
wrong thing.

55 tests green (+3). Verified at desktop and phone widths.
