#!/usr/bin/env python3
"""Structural tests for the MonteSprout static site.

There is no build step to fail, so these stand in for one: they guard the
invariants a copy or layout edit could silently break.

  - both pages are well-formed HTML and parse,
  - the pages render with **no JavaScript at all**,
  - every CSS class used in the HTML is actually defined in styles.css
    (a typo'd class is invisible in review and silently unstyled),
  - the contact email is a VISIBLE literal with a real mailto:,
  - in-page anchors resolve,
  - the **base path is consistent everywhere** — this is the load-bearing one.
    The site is a *project* Pages site today (served under /montesprout-site/),
    and becomes a *custom-domain* site (served under /) the moment a CNAME file
    lands. Every root-absolute link and every absolute URL must agree with
    whichever mode the repo is in, so adding CNAME turns these tests into the
    checklist for the swap (ROADMAP 18.4).
  - the Sunrise palette + type tokens are the app's, verbatim.

Run:  python3 -m unittest discover -s tests
"""

import html.parser
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
NOT_FOUND = ROOT / "404.html"
CSS = ROOT / "assets" / "styles.css"
CNAME = ROOT / "CNAME"
EMAIL = "support@mangogrovelabs.com"

# Locked Sunrise tokens (MonteSprout docs/architecture.md §8 — do not "improve").
SUNRISE = {
    "--paper": "#FBF6EF",
    "--ink": "#3B362D",
    "--sage": "#7C9A74",
    "--sage-deep": "#5E7D58",
    "--honey": "#D6A24A",
    "--accent": "#6E8C66",
}


def site_base():
    """The path every root-absolute link must sit under, and the canonical origin.

    No CNAME  → project site at mango-grove-labs.github.io/montesprout-site/
    CNAME     → custom domain at that apex, served from the root.
    """
    if CNAME.exists():
        domain = CNAME.read_text().strip()
        return "/", f"https://{domain}/"
    return "/montesprout-site/", "https://mango-grove-labs.github.io/montesprout-site/"


BASE_PATH, BASE_URL = site_base()


class _Parser(html.parser.HTMLParser):
    """Collects tags, ids, classes, links and visible text; fails on malformed nesting."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.ids = set()
        self.classes = set()
        self.anchors = []       # (href, inner_text)
        self.tags = []
        self.scripts = 0
        self.css_links = []     # href of every rel=stylesheet
        self.metas = []         # attr dicts
        self.links = []         # attr dicts for every <link>
        self.inline_styles = 0
        self.urls = []          # every href/src/content URL-ish value we see
        self._text_parts = []
        self._stack = []
        self._cur_anchor = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        if "id" in a:
            self.ids.add(a["id"])
        if "class" in a:
            self.classes.update(a["class"].split())
        if "style" in a:
            self.inline_styles += 1
        if tag == "script":
            self.scripts += 1
        if tag == "meta":
            self.metas.append(a)
        if tag == "link":
            self.links.append(a)
            if a.get("rel") == "stylesheet":
                self.css_links.append(a.get("href", ""))
        for key in ("href", "src"):
            if key in a:
                self.urls.append(a[key])
        if tag == "a":
            self._cur_anchor = [a.get("href", ""), ""]
        if tag not in self.VOID:
            self._stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "a" and self._cur_anchor is not None:
            self.anchors.append(tuple(self._cur_anchor))
            self._cur_anchor = None
        if tag in self.VOID:
            return
        assert self._stack and self._stack[-1] == tag, (
            f"malformed nesting: </{tag}> closes <{self._stack[-1] if self._stack else 'nothing'}>"
        )
        self._stack.pop()

    def handle_data(self, data):
        self._text_parts.append(data)
        if self._cur_anchor is not None:
            self._cur_anchor[1] += data

    @property
    def text(self):
        return " ".join(" ".join(self._text_parts).split())

    def meta(self, **match):
        for m in self.metas:
            if all(m.get(k) == v for k, v in match.items()):
                return m
        return None


def parse(path):
    p = _Parser()
    p.feed(path.read_text())
    assert not p._stack, f"{path.name}: unclosed tags {p._stack}"
    return p


class PageStructureTests(unittest.TestCase):
    """Both served pages: well-formed, single-h1, no JS, no inline styles."""

    def test_files_exist(self):
        for f in (INDEX, NOT_FOUND, CSS, ROOT / ".nojekyll",
                  ROOT / "robots.txt", ROOT / "sitemap.xml"):
            self.assertTrue(f.exists(), f"missing {f.relative_to(ROOT)}")

    def test_doctype_and_lang(self):
        for f in (INDEX, NOT_FOUND):
            head = f.read_text(  )[:200].lower()
            self.assertIn("<!doctype html>", head, f)
            self.assertIn('<html lang="en">', head, f)

    def test_single_h1(self):
        for f in (INDEX, NOT_FOUND):
            self.assertEqual(parse(f).tags.count("h1"), 1, f)

    def test_pages_render_without_javascript(self):
        for f in (INDEX, NOT_FOUND):
            self.assertEqual(parse(f).scripts, 0,
                             f"{f.name}: the site is deliberately script-free")

    def test_no_inline_styles(self):
        for f in (INDEX, NOT_FOUND):
            self.assertEqual(parse(f).inline_styles, 0,
                             f"{f.name}: styles belong in assets/styles.css")

    def test_local_stylesheet_linked_once_per_page(self):
        # css_links also holds the Google Fonts sheet, which is rel=stylesheet too.
        for f in (INDEX, NOT_FOUND):
            local = [h for h in parse(f).css_links if not h.startswith("http")]
            self.assertEqual(local, [self.expected_css(f)], f)

    @staticmethod
    def expected_css(page):
        # index.html is only ever served at the site root, so it may use a relative
        # href; 404.html is served at arbitrary depth and must be root-absolute.
        return "assets/styles.css" if page == INDEX else BASE_PATH + "assets/styles.css"

    def test_no_template_syntax_leaked(self):
        for f in (INDEX, NOT_FOUND):
            self.assertNotIn("{{", f.read_text(), f)


class ClassCoverageTests(unittest.TestCase):
    """Every class used in the HTML exists in the stylesheet, and vice-versa is not required."""

    @classmethod
    def setUpClass(cls):
        cls.defined = set(re.findall(r"\.([A-Za-z][\w-]*)", CSS.read_text()))

    def test_every_used_class_is_defined(self):
        for f in (INDEX, NOT_FOUND):
            used = parse(f).classes
            missing = sorted(used - self.defined)
            self.assertEqual(missing, [], f"{f.name}: classes with no CSS rule: {missing}")


class ContactTests(unittest.TestCase):
    """The support address is the site's only call to action — it must be real and visible."""

    def test_email_is_a_visible_literal(self):
        self.assertIn(EMAIL, parse(INDEX).text,
                      "the address must be readable on the page, not only in an href")

    def test_mailto_links_are_correct(self):
        for f in (INDEX, NOT_FOUND):
            mailtos = [h for h, _ in parse(f).anchors if h.startswith("mailto:")]
            self.assertTrue(mailtos, f"{f.name}: no contact link")
            for h in mailtos:
                self.assertEqual(h, f"mailto:{EMAIL}", f.name)

    def test_in_page_anchors_resolve(self):
        p = parse(INDEX)
        for href, _ in p.anchors:
            if href.startswith("#"):
                self.assertIn(href[1:], p.ids, f"dead in-page anchor {href}")


class BasePathTests(unittest.TestCase):
    """The project-site subpath (or the custom domain) must be consistent everywhere.

    This is what breaks first when the site moves to montesprout.app (ROADMAP 18.4):
    a stale `/montesprout-site/` prefix 404s, and a stale github.io canonical hands
    search engines the wrong home. Both failures are silent in a browser check of the
    *current* deployment, which is exactly why they are tested.
    """

    PROJECT_PATH = "/montesprout-site/"

    def test_root_absolute_urls_sit_under_the_base_path(self):
        for f in (INDEX, NOT_FOUND):
            for url in parse(f).urls:
                if not url.startswith("/"):
                    continue
                self.assertTrue(
                    url.startswith(BASE_PATH),
                    f"{f.name}: {url!r} is not under the site base {BASE_PATH!r}")
                if BASE_PATH == "/":
                    # "/" prefixes everything, so the check above can't see a link left
                    # behind on the project path. This is the one that actually 404s.
                    self.assertFalse(
                        url.startswith(self.PROJECT_PATH),
                        f"{f.name}: {url!r} still points at the project-site path, but "
                        f"a CNAME moved the site to the domain root")

    def test_absolute_urls_dont_mix_the_two_hosts(self):
        stale = "mango-grove-labs.github.io" if BASE_PATH == "/" else None
        if stale is None:
            self.skipTest("still on the project site")
        for f in (INDEX, NOT_FOUND, ROOT / "sitemap.xml", ROOT / "robots.txt"):
            self.assertNotIn(stale, f.read_text(),
                             f"{f.name}: stale github.io URL after the domain swap")

    def test_404_uses_root_absolute_links_only(self):
        # GitHub serves 404.html for any missing depth, so relative links there
        # resolve differently per URL — they must be root-absolute.
        for url in parse(NOT_FOUND).urls:
            if url.startswith(("mailto:", "http://", "https://", "#")):
                continue
            self.assertTrue(url.startswith("/"),
                            f"404.html: {url!r} must be root-absolute")

    def test_canonical_matches_the_base_url(self):
        canonical = [l for l in parse(INDEX).links if l.get("rel") == "canonical"]
        self.assertEqual(len(canonical), 1)
        self.assertEqual(canonical[0]["href"], BASE_URL)

    def test_og_url_matches_the_canonical(self):
        og = parse(INDEX).meta(property="og:url")
        self.assertIsNotNone(og, "og:url missing")
        self.assertEqual(og["content"], BASE_URL)

    def test_sitemap_loc_matches_the_base_url(self):
        root = ET.parse(ROOT / "sitemap.xml").getroot()
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [e.text for e in root.findall("s:url/s:loc", ns)]
        self.assertEqual(locs, [BASE_URL])

    def test_sitemap_lastmod_is_not_stale(self):
        """`lastmod` is hand-written, so it goes stale silently — pin it to git.

        The rule: it must not be older than the last commit that touched
        index.html. Editing the page and forgetting the date turns this red on the
        next run instead of quietly telling crawlers nothing changed.
        """
        root = ET.parse(ROOT / "sitemap.xml").getroot()
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        lastmod = root.findtext("s:url/s:lastmod", namespaces=ns)
        self.assertIsNotNone(lastmod, "sitemap has no <lastmod>")
        self.assertRegex(lastmod, r"^\d{4}-\d{2}-\d{2}$", "W3C date format expected")

        committed = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", "index.html"],
            cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if not committed:
            self.skipTest("index.html has no commit history yet")
        self.assertGreaterEqual(
            lastmod, committed,
            f"sitemap lastmod {lastmod} predates index.html's last commit {committed}")

    def test_robots_points_at_the_sitemap(self):
        lines = (ROOT / "robots.txt").read_text().splitlines()
        pointers = [l.split(":", 1)[1].strip() for l in lines
                    if l.lower().startswith("sitemap:")]
        self.assertEqual(pointers, [BASE_URL + "sitemap.xml"])

    def test_robots_allows_crawling(self):
        text = (ROOT / "robots.txt").read_text().lower()
        self.assertIn("user-agent: *", text)
        self.assertIn("allow: /", text)


class HeadMetadataTests(unittest.TestCase):

    def test_title_names_the_product(self):
        m = re.search(r"<title>(.*?)</title>", INDEX.read_text(), re.S)
        self.assertIsNotNone(m)
        self.assertIn("MonteSprout", m.group(1))

    def test_meta_description_is_present_and_sane(self):
        d = parse(INDEX).meta(name="description")
        self.assertIsNotNone(d, "no meta description")
        self.assertGreater(len(d["content"]), 60)
        self.assertLess(len(d["content"]), 300)

    def test_open_graph_core_tags(self):
        p = parse(INDEX)
        for prop in ("og:type", "og:site_name", "og:title", "og:description", "og:url"):
            self.assertIsNotNone(p.meta(property=prop), f"missing {prop}")

    def test_twitter_card_matches_the_image_state(self):
        p = parse(INDEX)
        card = p.meta(name="twitter:card")
        self.assertIsNotNone(card)
        has_image = p.meta(property="og:image") is not None
        # summary_large_image without an image renders as a bare link — keep them together.
        self.assertEqual(card["content"] == "summary_large_image", has_image)

    def test_theme_color_is_the_accent_token(self):
        t = parse(INDEX).meta(name="theme-color")
        self.assertIsNotNone(t)
        self.assertEqual(t["content"].upper(), SUNRISE["--accent"])

    def test_404_is_noindex(self):
        r = parse(NOT_FOUND).meta(name="robots")
        self.assertIsNotNone(r, "404 must not be indexable")
        self.assertIn("noindex", r["content"])


class BrandAssetTests(unittest.TestCase):
    """The favicon and the social card are the mark leaving the site — pin both."""

    FAVICON = ROOT / "assets" / "favicon.svg"
    OG_IMAGE = ROOT / "assets" / "og-image.png"
    # The app's leaf, verbatim (DesignSystem/Motifs.swift § LeafArt).
    LEAF_BODY = "M12 2C5.5 2 2 5.5 2 12c6.5 0 10-3.5 10-10Z"
    LEAF_VEIN = "M4.5 9.5C6.5 8.5 8.5 6.5 9.5 4.5"

    def test_favicon_is_wellformed_svg(self):
        self.assertTrue(self.FAVICON.exists())
        root = ET.parse(self.FAVICON).getroot()
        self.assertTrue(root.tag.endswith("svg"))

    def test_favicon_is_the_apps_leaf(self):
        svg = self.FAVICON.read_text()
        for d in (self.LEAF_BODY, self.LEAF_VEIN):
            self.assertIn(d, svg, "favicon must use the app's leaf path verbatim")
        self.assertIn(SUNRISE["--sage"], svg)

    def test_header_mark_matches_the_favicon(self):
        # Three copies of the mark exist (favicon + both page headers); a change to
        # one and not the others is the drift this catches.
        for f in (INDEX, NOT_FOUND):
            html = f.read_text()
            for d in (self.LEAF_BODY, self.LEAF_VEIN):
                self.assertIn(d, html, f"{f.name}: header mark diverged from the favicon")

    def test_icons_linked_in_both_pages(self):
        for f in (INDEX, NOT_FOUND):
            rels = {l.get("rel"): l.get("href") for l in parse(f).links}
            self.assertIn("icon", rels, f"{f.name}: no favicon link")
            self.assertTrue(rels["icon"].endswith("assets/favicon.svg"))
            # Safari ignores an SVG apple-touch-icon, so that slot must be the PNG —
            # pointing it at the SVG is a silently dead tag, not a fallback.
            self.assertIn("apple-touch-icon", rels, f"{f.name}: no touch icon")
            self.assertTrue(rels["apple-touch-icon"].endswith(".png"),
                            f"{f.name}: apple-touch-icon must be a PNG")

    def test_apple_touch_icon_is_a_180px_square_png(self):
        icon = ROOT / "assets" / "apple-touch-icon.png"
        self.assertTrue(icon.exists(), "run tools/make_images.py and commit the result")
        head = icon.read_bytes()[:24]
        self.assertEqual(head[:8], b"\x89PNG\r\n\x1a\n", "not a PNG")
        self.assertEqual((int.from_bytes(head[16:20], "big"),
                          int.from_bytes(head[20:24], "big")), (180, 180))

    def test_og_image_is_a_1200x630_png(self):
        self.assertTrue(self.OG_IMAGE.exists(),
                        "run tools/make_og_image.py and commit the result")
        head = self.OG_IMAGE.read_bytes()[:24]
        self.assertEqual(head[:8], b"\x89PNG\r\n\x1a\n", "not a PNG")
        width = int.from_bytes(head[16:20], "big")
        height = int.from_bytes(head[20:24], "big")
        self.assertEqual((width, height), (1200, 630))

    def test_og_image_meta_agrees_with_the_file(self):
        p = parse(INDEX)
        ref = p.meta(property="og:image")
        self.assertIsNotNone(ref, "og:image missing")
        self.assertEqual(ref["content"], BASE_URL + "assets/og-image.png")
        head = self.OG_IMAGE.read_bytes()[:24]
        for prop, offset in (("og:image:width", 16), ("og:image:height", 20)):
            declared = p.meta(property=prop)
            self.assertIsNotNone(declared, f"missing {prop}")
            self.assertEqual(int(declared["content"]),
                             int.from_bytes(head[offset:offset + 4], "big"),
                             f"{prop} disagrees with the PNG header")

    def test_twitter_image_matches_the_og_image(self):
        p = parse(INDEX)
        self.assertEqual(p.meta(name="twitter:image")["content"],
                         p.meta(property="og:image")["content"])


class PrivacyClaimTests(unittest.TestCase):
    """The site is the app's other user-facing surface — the same claims contract applies.

    Ported from the app's `PrivacyClaimConventionTests` (MonteSprout, Phase 40.7). The app
    may not tell a teacher her notes never leave the device, because generating a report
    posts pseudonymised note text through the proxy and iCloud sync moves data off-device
    by design (architecture §13.4/§13.6). A marketing page is exactly where that absolute
    grows back, and the privacy page (18.3) inherits this guard the day it lands.

    What is banned is the **absolute**, not the honest specific: "photos and recordings are
    never sent" is true and stays legal; "your notes never leave your iPhone" is not.
    """

    BANNED = [
        (r"(observation|note|report|classroom|data|everything)[^“”\".!]{0,40}"
         r"never (leave|leaves)[^“”\".!]{0,20}(iPhone|device|phone)",
         "report generation sends pseudonymised note text off the device"),
        (r"never (sent|shared)[^“”\".!]{0,20}(our|any) server",
         "the proxy is our server, and the report path posts through it"),
        (r"(observation|note|report|classroom|data|everything)[^“”\".!]{0,40}"
         r"(stay|stays) (on|in) (this|your) (device|iPhone|phone)",
         "iCloud sync and the report path both move this data off the device"),
        (r"(on|to) (your|this) (iPhone|device|phone) only",
         "an absolute framed as a location claim — say what actually leaves, and how"),
    ]

    def test_no_absolute_on_device_claims(self):
        for f in sorted(ROOT.glob("*.html")):
            text = parse(f).text
            for pattern, why in self.BANNED:
                m = re.search(pattern, text, re.IGNORECASE)
                if m is not None:
                    self.fail(f"{f.name}: retired absolute privacy claim "
                              f"{m.group(0)!r} — {why}")


class SunriseTokenTests(unittest.TestCase):
    """The tokens are transcribed from the app; drift here is drift from the product."""

    @classmethod
    def setUpClass(cls):
        cls.css = CSS.read_text()

    def test_palette_tokens_are_verbatim(self):
        for token, value in SUNRISE.items():
            self.assertRegex(self.css, rf"{re.escape(token)}:\s*{value};",
                             f"{token} must be {value} (architecture §8)")

    def test_both_app_faces_are_used(self):
        self.assertIn("'Quicksand'", self.css)
        self.assertIn("'Nunito'", self.css)
        for f in (INDEX, NOT_FOUND):
            fonts = [l["href"] for l in parse(f).links
                     if l.get("rel") == "stylesheet"
                     and "fonts.googleapis.com" in l.get("href", "")]
            self.assertEqual(len(fonts), 1, f"{f.name}: expected one font request")
            self.assertIn("Quicksand", fonts[0])
            self.assertIn("Nunito", fonts[0])

    def test_named_radius_scale_matches_the_app(self):
        for token, value in (("--radius-chip", "12px"), ("--radius-control", "16px"),
                             ("--radius-card", "20px"), ("--radius-sheet", "28px")):
            self.assertRegex(self.css, rf"{re.escape(token)}:\s*{value};")

    def test_reduced_motion_is_respected(self):
        self.assertIn("prefers-reduced-motion", self.css)


class DeployInfraTests(unittest.TestCase):

    def test_nojekyll_exists_and_is_empty(self):
        f = ROOT / ".nojekyll"
        self.assertTrue(f.exists())
        self.assertEqual(f.read_text().strip(), "")

    def test_gitignore_ignores_python_caches(self):
        text = (ROOT / ".gitignore").read_text()
        self.assertIn("__pycache__/", text)
        self.assertIn(".DS_Store", text)

    def test_cname_if_present_is_a_bare_apex_domain(self):
        if not CNAME.exists():
            self.skipTest("no custom domain yet (ROADMAP 18.4)")
        value = CNAME.read_text().strip()
        self.assertNotIn("/", value)
        self.assertFalse(value.startswith("http"))
        self.assertRegex(value, r"^[a-z0-9.-]+\.[a-z]{2,}$")


if __name__ == "__main__":
    unittest.main()
