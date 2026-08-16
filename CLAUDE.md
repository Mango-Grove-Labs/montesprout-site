# CLAUDE.md — montesprout-site

The public marketing/legal site for **MonteSprout**, served by GitHub Pages from this repo's
root. No build step: a push to `main` is a deploy.

## Where the plan lives (not here)

This repo carries **no planning docs**. The roadmap, decisions and cursor for the site are in
the **app** repo, `Mango-Grove-Labs/MonteSprout` (sibling checkout `~/Developer/MonteSprout`):

- `PROGRESS.md` → **Phase 18** — the live checklist (18.2 repo+Pages · 18.3 privacy/support ·
  18.5 landing · 18.6 favicon/OG/SEO · 18.4 owner-op DNS)
- `docs/ROADMAP.md` § 18 — scope prose · `docs/DECISIONS.md` — the *why*
- `docs/plans/2026-08-16-external-testing-drafts.md` — the **paste-ready privacy + support
  copy** (§§1–2). Use those drafts; don't re-draft policy prose from scratch.

Work on this site is planned and reported from there. Commit here, record there.

## Conventions

- **Plain HTML + CSS. Zero JavaScript.** No bundler, no framework, no npm. If a page ever
  needs a script, that is a decision to record in the app repo's `DECISIONS.md` first — the
  test suite asserts a script count of zero on every page.
- **`.nojekyll` is intentional** — Pages serves files raw. Don't remove it.
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
- **Base path.** This is a *project* Pages site: it lives under `/montesprout-site/`.
  `index.html` uses relative asset paths; `404.html` must use **root-absolute** ones (GitHub
  serves it for any missing depth). The tests derive the expected base from the presence of a
  `CNAME` file — see README § Custom domain.
- **Privacy copy is a contract, not marketing.** Anything the site claims about what leaves a
  teacher's device must match the app's behaviour (architecture §13). If a claim and the code
  disagree, that's a bug to surface in the app repo — never soften the page to fit. Before
  editing `privacy.html`, **re-verify the touched claim against the code**, the way 18.3 did:
  the drafts annex in the app repo carries a claim→source trace table, and two of its rows were
  already wrong by the time the page was written. Move the "Last updated" date with any edit —
  a test compares it against the file's own git date.
- **Adding a page?** The page, its `canonical`, its `sitemap.xml` entry, and a link from every
  other page's nav *and* footer all move together. The tests fail until they do.
- **No secrets, ever** (public repo): no keys, no tokens, no personal address or phone.
- **Preview before committing:** `python3 -m http.server`, then `http://localhost:8000`.
- **Run the tests before committing:** `python3 -m unittest discover -s tests`.
