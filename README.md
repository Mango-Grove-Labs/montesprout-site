# MonteSprout — website

The public website for **MonteSprout**, a calm iOS app for Montessori teachers, by
**Mango Grove Labs LLC**. Static pages served by GitHub Pages.

- **Live:** <https://mango-grove-labs.github.io/montesprout-site/>
- **Planned:** `montesprout.app` (DNS not wired yet — see *Custom domain* below)

No build step, no framework — the repo root *is* the deployed site. A push to `main` is a
deploy.

## Stack

Plain HTML + CSS, two webfonts (Quicksand + Nunito via Google Fonts), **zero JavaScript**.
The palette, type and radius scale are MonteSprout's *Sunrise* tokens, transcribed from the
app's `docs/architecture.md` §8 — the site and the app are meant to look like the same
product.

The site itself has no dependencies. The one build-time tool, `tools/make_images.py`,
needs **Pillow** — see *Brand assets* below.

## Local preview

```bash
python3 -m http.server   # then open http://localhost:8000
```

No dependencies to install.

## Tests

```bash
python3 -m unittest discover -s tests
```

50 structural tests stand in for the build step there isn't one of: well-formed pages, no
stray JavaScript, no undefined CSS classes, internal links and anchors that resolve, every
page reachable from every other, locked Sunrise tokens, brand assets that match the app's
mark, privacy claims that stay inside what the app actually does, and — the load-bearing
one — **base-path consistency** (see below). Stdlib only; no install step.

## Layout

```
index.html                 home
privacy.html support.html  the legal/help pages (the privacy URL App Store Connect needs)
404.html                   not-found
assets/                    styles.css (Sunrise tokens at the top), favicon.svg,
                           og-image.png, apple-touch-icon.png
.nojekyll robots.txt sitemap.xml
tests/                     structural tests (unittest, stdlib only)
tools/                     make_images.py + the vendored OFL fonts it renders with
                           (build-time only — never served)
```

## Adding a page

Four things move together, and the tests fail until they do: the page itself (relative
asset paths — only `404.html` is root-absolute), a `<link rel="canonical">` matching its
real URL, an entry in `sitemap.xml`, and a link from the nav and footer of every other
page.

## Brand assets

`assets/favicon.svg` and the header mark on every page use the app's leaf path **verbatim**
(`DesignSystem/Motifs.swift` § `LeafArt`). A test asserts they still agree, so the site
can't drift into a second mark.

The two PNGs are generated, not hand-made:

```bash
python3 tools/make_images.py   # needs Pillow; writes both PNGs, then commit them
```

It renders the same leaf beziers and the app's own Quicksand/Nunito faces (vendored under
`tools/fonts/`, OFL), so output is byte-identical on any machine — regenerating without a
content change produces no diff. Edit the script, never the PNGs.

## Deployment

Deploy is automatic: commit and push to `main`; GitHub Pages publishes the root within
~a minute. There is no build to break.

GitHub Pages setup (already done): Settings → Pages → **Deploy from a branch** →
`main` / `/ (root)`.

## Custom domain

The site is a **project** Pages site today, so it is served under the **`/montesprout-site/`**
path. When `montesprout.app` is wired up, it moves to the root — and four things move
together:

1. add a `CNAME` file containing `montesprout.app`,
2. `<link rel="canonical">`, `<meta property="og:url">` and the two image URLs in
   `index.html`,
3. every root-absolute path in `404.html` (and the sitemap `<loc>` / robots `Sitemap:`),
4. the DNS records at the registrar, then **Enforce HTTPS** once the check goes green.

`robots.txt` starts working at the same moment: crawlers only read it at the host root, and
`mango-grove-labs.github.io/robots.txt` isn't ours to create — so today the file is committed
but inert (it says so at the top).

`tests/test_site.py` derives the expected base path from whether `CNAME` exists, so adding
that one file turns the suite red on every URL still pointing at the old base — the test
run *is* the checklist for the swap.

## Planning

This site is one deliverable of the MonteSprout project; its roadmap lives with the app, in
the `MonteSprout` repo (`PROGRESS.md` → Phase 18, `docs/ROADMAP.md` § 18, rationale in
`docs/DECISIONS.md`). No plan docs are duplicated here.

## Contact

support@mangogrovelabs.com
