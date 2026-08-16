# MonteSprout — website

The public website for **MonteSprout**, a calm iOS app for Montessori teachers, by
**Mango Grove Labs LLC**. Static pages served by GitHub Pages.

- **Live:** <https://montesprout.app>

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

52 structural tests stand in for the build step there isn't one of: well-formed pages, no
stray JavaScript, no undefined CSS classes, internal links and anchors that resolve, every
page reachable from every other, locked Sunrise tokens, brand assets that match the app's
mark, privacy claims that stay inside what the app actually does, whitespace beside any
element the CSS can hide (hiding one fuses the words around it), and — the load-bearing
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
PROGRESS.md                the cursor: live roadmap, current status, what's next
docs/                      ROADMAP (future) · OVERVIEW (present) · JOURNAL (past) ·
                           DECISIONS · PRD pointer — planning only, never served content
```

Pages serves this repo raw (`.nojekyll`), so the last two *are* fetchable at the apex — they're
public either way, and `robots.txt` keeps them out of search results.

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

**Leave the folder on `/ (root)`.** The other option in that dropdown is `/docs`, and since the
planning docs landed this repo has one — selecting it would serve `ROADMAP.md` and friends as the
website. Harmless before; not any more.

## Custom domain

The site serves from the apex **montesprout.app** (since 2026-08-16). Apex `A`/`AAAA` records
and a `www` CNAME point at GitHub Pages from Namecheap, the repo carries a `CNAME` file, and
`.app` is on the HSTS preload list — so HTTPS is mandatory here, not optional.

Before that it was a GitHub *project* site under `/montesprout-site/`, and the move touched
four things at once: the `CNAME` file, every absolute URL (canonical, `og:url`, both image
URLs, sitemap `<loc>`, robots `Sitemap:`), every root-absolute path in `404.html`, and the
registrar records.

**The test suite is what made that safe, and still guards it.** `tests/test_site.py` derives
the expected base from whether `CNAME` exists, so adding the file turned ten tests red, each
naming a URL still pointing at the old base; the swap was done by working that list to green.
The same mechanism runs in reverse — delete `CNAME` and the suite immediately expects the
project-subpath form again.

`robots.txt` only started working at the same moment: crawlers read robots.txt exclusively at
the host root, which was not ours while the site lived on a subpath.

## Planning

Status: see [`PROGRESS.md`](PROGRESS.md) — the live checklist and what's next.

The rest of the planning layer is in [`docs/`](docs/): `ROADMAP.md` (scope prose for unshipped work),
`OVERVIEW.md` (the site as built), `JOURNAL.md` (per-phase narrative), `DECISIONS.md` (the *why*).
The site is still one deliverable of the MonteSprout product — the app repo owns the design tokens,
the data-behaviour claims the privacy page must stay inside, and the product PRD.

## Contact

support@mangogrovelabs.com
