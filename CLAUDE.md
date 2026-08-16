# CLAUDE.md — montesprout-site

The public marketing/legal site for **MonteSprout**, served by GitHub Pages from this repo's
root. No build step: a push to `main` is a deploy.

## Where the plan lives (here, since 2026-08-16)

**This repo owns the site roadmap.** `PROGRESS.md` at the root is the cursor and the only live
checklist; `docs/` holds ROADMAP (future) · OVERVIEW (present) · JOURNAL (past) · DECISIONS.
Read `PROGRESS.md` first — it routes to the rest. Phase labels continue from **Phase 18** because
this repo's commit messages reference them; new site phases take 19+ in *this* repo's namespace.

There is **no `docs/architecture.md` here, by design** — the four Conventions below are the whole
engineering contract, and the tokens/mark they point at are owned by the app.

Still in the **app** repo, `Mango-Grove-Labs/MonteSprout` (sibling checkout `~/Developer/MonteSprout`):

- `docs/architecture.md` §8 — the **authoritative** Sunrise tokens · §13 — the data behaviour the
  privacy page may not exceed
- `docs/plans/2026-08-16-external-testing-drafts.md` §§1–2 — the **paste-ready privacy + support
  copy**. Use those drafts rather than re-drafting policy prose — but re-verify each claim against
  the code, as 18.3 did (three were wrong).
- Its `docs/JOURNAL.md` / `docs/DECISIONS.md` carry the app-side half of Phase 18.

## Conventions

- **Plain HTML + CSS. Zero JavaScript.** No bundler, no framework, no npm. If a page ever
  needs a script, that is a decision to record in **this repo's** `docs/DECISIONS.md` first —
  the test suite asserts a script count of zero on every page. (Open now: 19.1 wants analytics;
  see `PROGRESS.md` § Needs You.)
- **`.nojekyll` is intentional** — Pages serves files raw. Don't remove it.
- **Pages source stays `main` / `/ (root)`.** Since the planning docs landed (2026-08-16) the
  repo has a `docs/` folder, so GitHub's other source option — `main` / `/docs` — would quietly
  serve `ROADMAP.md` and friends *as the website*. It was harmless before; it isn't now.
- **Sunrise tokens are transcribed, not invented.** The palette / type / radius values at the
  top of `assets/styles.css` come from the app's `docs/architecture.md` §8. Changing one here
  without changing it there is drift, and `tests/test_site.py` fails on it.
- **The leaf mark has one source.** `assets/favicon.svg`, both page headers, and
  `tools/make_images.py` all use the app's `LeafArt` bezier paths verbatim; a test pins them
  together. Redraw it in the app first, then copy the paths here.
- **The PNGs are generated.** `assets/og-image.png` and `assets/apple-touch-icon.png` come
  from `python3 tools/make_images.py` (Pillow, the repo's only build-time dependency; the
  fonts it uses are vendored under `tools/fonts/`). Output is deterministic — edit the script
  and re-run, never touch the PNGs by hand. `og:image:width`/`height` are asserted against the
  file's real PNG header, so a resize that skips the meta tags fails the suite.
- **Base path.** The site serves from the apex **montesprout.app**, so root-absolute paths are
  plain `/…`. `index.html` and the content pages use relative asset paths; `404.html` must use
  **root-absolute** ones (GitHub serves it for any missing depth, so a relative href there
  resolves differently per URL). The tests derive the expected base from the presence of the
  `CNAME` file, so removing it flips every expectation back to the old project subpath — see
  README § Custom domain.
- **Privacy copy is a contract, not marketing.** Anything the site claims about what leaves a
  teacher's device must match the app's behaviour (the app's `docs/architecture.md` §13 — there
  is no architecture doc in this repo). If a claim and the code
  disagree, that's a bug to surface in the app repo — never soften the page to fit. Before
  editing `privacy.html`, **re-verify the touched claim against the code**, the way 18.3 did:
  the drafts annex in the app repo carries a claim→source trace table, and two of its rows were
  already wrong by the time the page was written. Move the "Last updated" date with any edit —
  a test compares it against the file's own git date.
- **Adding a page?** The page, its `canonical`, its `sitemap.xml` entry, and a link from every
  other page's nav *and* footer all move together. The tests fail until they do.
- **Anything CSS can hide needs whitespace beside it in the source.** A responsive `<br>` or
  span written as `seconds.<br class="hero__break">Reports` fuses its neighbours the moment the
  rule hides it — mobile reads "seconds.Reports" while desktop, which shows the break, looks
  perfect. `HiddenElementSpacingTests` derives the hideable classes from every `display: none`
  in the stylesheet and checks the **raw source**: the parser joins text nodes with a space, so
  any assertion over parsed text is vacuous by construction here (the first version of that
  test was, and only a planted failure exposed it).
- **No secrets, ever** (public repo): no keys, no tokens, no personal address or phone.
- **Preview before committing:** `python3 -m http.server`, then `http://localhost:8000`.
- **Run the tests before committing:** `python3 -m unittest discover -s tests`.
