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
PRIVACY = ROOT / "privacy.html"
SUPPORT = ROOT / "support.html"
NOT_FOUND = ROOT / "404.html"

# Every served page. `CONTENT` pages are only ever fetched at their own URL, so they may
# use relative hrefs; 404.html is served by GitHub for ANY missing depth, so its links
# must be root-absolute or they resolve differently per URL.
CONTENT = (INDEX, PRIVACY, SUPPORT)
PAGES = CONTENT + (NOT_FOUND,)
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


def last_commit_date(path):
    """YYYY-MM-DD of the last commit touching `path`, or "" if it has no history."""
    return subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", str(path.relative_to(ROOT))],
        cwd=ROOT, capture_output=True, text=True).stdout.strip()


class PageStructureTests(unittest.TestCase):
    """Every served page: well-formed, single-h1, no JS, no inline styles."""

    def test_files_exist(self):
        for f in PAGES + (CSS, ROOT / ".nojekyll",
                          ROOT / "robots.txt", ROOT / "sitemap.xml"):
            self.assertTrue(f.exists(), f"missing {f.relative_to(ROOT)}")

    def test_doctype_and_lang(self):
        for f in PAGES:
            head = f.read_text(  )[:200].lower()
            self.assertIn("<!doctype html>", head, f)
            self.assertIn('<html lang="en">', head, f)

    def test_single_h1(self):
        for f in PAGES:
            self.assertEqual(parse(f).tags.count("h1"), 1, f)

    def test_pages_render_without_javascript(self):
        for f in PAGES:
            self.assertEqual(parse(f).scripts, 0,
                             f"{f.name}: the site is deliberately script-free")

    def test_no_inline_styles(self):
        for f in PAGES:
            self.assertEqual(parse(f).inline_styles, 0,
                             f"{f.name}: styles belong in assets/styles.css")

    def test_local_stylesheet_linked_once_per_page(self):
        # css_links also holds the Google Fonts sheet, which is rel=stylesheet too.
        for f in PAGES:
            local = [h for h in parse(f).css_links if not h.startswith("http")]
            self.assertEqual(local, [self.expected_css(f)], f)

    @staticmethod
    def expected_css(page):
        return ("assets/styles.css" if page in CONTENT
                else BASE_PATH + "assets/styles.css")

    def test_no_template_syntax_leaked(self):
        for f in PAGES:
            self.assertNotIn("{{", f.read_text(), f)


class HiddenElementSpacingTests(unittest.TestCase):
    """An element CSS can hide must have whitespace beside it in the source.

    `hero__break` is a <br> hidden below 40rem. Written as `seconds.<br…>Reports`, hiding it
    fuses the neighbours and the mobile hero reads "seconds.Reports" — while desktop, where the
    <br> is visible, looks perfect. Nothing else here could catch it: the HTML is well-formed,
    the classes are defined, and this suite's own parser joins text nodes with a space, so even
    a "no fused sentences" check on the parsed text is **vacuous by construction** (it was
    written that way first, and only the planted-failure check exposed it).

    So the rule is applied to the raw source, and it derives the set of hideable classes from
    the stylesheet rather than hard-coding one: any class the CSS sets to `display: none`.
    """

    @classmethod
    def setUpClass(cls):
        css = CSS.read_text()
        cls.hideable = set()
        for block in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
            selector, body = block.group(1), block.group(2)
            if re.search(r"display\s*:\s*none", body):
                cls.hideable.update(re.findall(r"\.([A-Za-z][\w-]*)", selector))

    def test_the_rule_has_something_to_check(self):
        # Guards against the whole class silently passing because nothing matched.
        self.assertIn("hero__break", self.hideable,
                      "expected at least the hero break to be hideable — "
                      "if it was removed, delete this test with it")

    def test_hideable_elements_have_whitespace_beside_them(self):
        for f in PAGES:
            html = f.read_text()
            for cls in sorted(self.hideable):
                for m in re.finditer(rf'<(\w+)[^>]*class="[^"]*\b{re.escape(cls)}\b[^"]*"[^>]*>', html):
                    before = html[max(0, m.start() - 1):m.start()]
                    after = html[m.end():m.end() + 1]
                    self.assertTrue(
                        before.isspace() or after.isspace() or not before or not after,
                        f"{f.name}: <{m.group(1)} class={cls}> has no whitespace on either side — "
                        f"hiding it will fuse the neighbouring words "
                        f"({html[max(0, m.start()-25):m.end()+25]!r})")


class ClassCoverageTests(unittest.TestCase):
    """Every class used in the HTML exists in the stylesheet, and vice-versa is not required."""

    @classmethod
    def setUpClass(cls):
        cls.defined = set(re.findall(r"\.([A-Za-z][\w-]*)", CSS.read_text()))

    def test_every_used_class_is_defined(self):
        for f in PAGES:
            used = parse(f).classes
            missing = sorted(used - self.defined)
            self.assertEqual(missing, [], f"{f.name}: classes with no CSS rule: {missing}")


class ContactTests(unittest.TestCase):
    """The support address is the site's only call to action — it must be real and visible."""

    def test_email_is_a_visible_literal(self):
        self.assertIn(EMAIL, parse(INDEX).text,
                      "the address must be readable on the page, not only in an href")

    def test_mailto_links_are_correct(self):
        for f in PAGES:
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
        for f in PAGES:
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

    @staticmethod
    def canonical_url(page):
        """The absolute URL a content page declares as its own."""
        return BASE_URL + ("" if page == INDEX else page.name)

    def test_each_content_page_declares_its_own_canonical(self):
        for f in CONTENT:
            canonical = [l for l in parse(f).links if l.get("rel") == "canonical"]
            self.assertEqual(len(canonical), 1, f"{f.name}: expected one canonical")
            self.assertEqual(canonical[0]["href"], self.canonical_url(f), f.name)

    def test_og_url_matches_the_canonical(self):
        for f in CONTENT:
            og = parse(f).meta(property="og:url")
            self.assertIsNotNone(og, f"{f.name}: og:url missing")
            self.assertEqual(og["content"], self.canonical_url(f), f.name)

    def test_sitemap_lists_exactly_the_content_pages(self):
        """A page added without a sitemap entry (or an entry pointing nowhere) fails here.

        404.html is deliberately absent — it is noindex.
        """
        root = ET.parse(ROOT / "sitemap.xml").getroot()
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = sorted(e.text for e in root.findall("s:url/s:loc", ns))
        self.assertEqual(locs, sorted(self.canonical_url(f) for f in CONTENT))

    def test_sitemap_lastmod_is_not_stale(self):
        """Each `lastmod` is hand-written, so it goes stale silently — pin it to git.

        The rule, per page: its `lastmod` must not be older than the last commit that
        touched that page's file. Editing a page and forgetting its date turns this red
        on the next run instead of quietly telling crawlers nothing changed.
        """
        root = ET.parse(ROOT / "sitemap.xml").getroot()
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        entries = {e.findtext("s:loc", namespaces=ns): e.findtext("s:lastmod", namespaces=ns)
                   for e in root.findall("s:url", ns)}
        checked = 0
        for page in CONTENT:
            lastmod = entries.get(self.canonical_url(page))
            self.assertIsNotNone(lastmod, f"{page.name}: no <lastmod> in the sitemap")
            self.assertRegex(lastmod, r"^\d{4}-\d{2}-\d{2}$",
                             f"{page.name}: W3C date format expected")
            committed = last_commit_date(page)
            if not committed:
                continue  # not committed yet — nothing to be stale against
            checked += 1
            self.assertGreaterEqual(
                lastmod, committed,
                f"{page.name}: sitemap lastmod {lastmod} predates its last commit {committed}")
        if not checked:
            self.skipTest("no page has commit history yet")

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


class LinkIntegrityTests(unittest.TestCase):
    """Every internal link lands somewhere real.

    A multi-page static site has no router to complain, so a renamed file or a typo'd
    href is a 404 nobody notices until a teacher — or Apple's reviewer following the
    privacy-policy URL — hits it.
    """

    def _targets(self, page):
        for url in parse(page).urls:
            if url.startswith(("mailto:", "http://", "https://")):
                continue
            path, _, fragment = url.partition("#")
            yield url, path, fragment

    def _resolve(self, page, path):
        """The file a link's path part names, or None if it points outside the site.

        A path that is empty or ends in "/" names a directory, which the server
        answers with that directory's index.html — do the same here.
        """
        if path.startswith("/"):
            if not path.startswith(BASE_PATH):
                return None
            rest = path[len(BASE_PATH):]
        else:
            rest = path
        if rest == "" or rest.endswith("/") or rest in ("./",):
            return (page.parent if not path.startswith("/") else ROOT) / rest / "index.html"
        return (ROOT if path.startswith("/") else page.parent) / rest

    def test_internal_hrefs_resolve_to_real_files(self):
        for page in PAGES:
            for url, path, _ in self._targets(page):
                if not path:
                    continue  # pure in-page anchor, checked below
                target = self._resolve(page, path)
                self.assertIsNotNone(target, f"{page.name}: {url!r} escapes the site base")
                self.assertTrue(target.exists(),
                                f"{page.name}: {url!r} points at nothing ({target})")

    def test_fragments_exist_on_the_page_they_point_at(self):
        for page in PAGES:
            for url, path, fragment in self._targets(page):
                if not fragment:
                    continue
                target = page if not path else self._resolve(page, path)
                if target is None or not target.exists():
                    continue  # the missing-file test above owns this failure
                self.assertIn(fragment, parse(target).ids,
                              f"{page.name}: {url!r} — no id={fragment!r} on {target.name}")

    def test_every_content_page_is_reachable_from_every_other(self):
        # The nav is copy-pasted per page, which is exactly how one page quietly loses
        # its link to another.
        for page in CONTENT:
            hrefs = {h for h, _ in parse(page).anchors}
            for other in CONTENT:
                if other == page:
                    continue
                self.assertTrue(
                    any(h.split("#")[0].endswith(other.name) or
                        (other == INDEX and h.split("#")[0] in ("", "./", "index.html"))
                        for h in hrefs),
                    f"{page.name} has no link to {other.name}")


class ScreenshotTests(unittest.TestCase):
    """The app screenshots are the page's only images — pin what silently rots.

    They are generated by hand from a simulator (18.7), so nothing regenerates them: a
    renamed file, a missing alt, or width/height that stop matching the file would all ship
    unnoticed, the last one as layout shift while the image loads.
    """

    @classmethod
    def setUpClass(cls):
        cls.imgs = re.findall(r"<img\b[^>]*>", INDEX.read_text())

    def test_the_strip_is_present(self):
        # Guards the rest of the class against passing vacuously if the strip is removed.
        self.assertGreaterEqual(len(self.imgs), 3, "expected the screenshot strip on the home page")

    def test_every_image_resolves_has_alt_and_declares_its_real_size(self):
        from struct import unpack
        for tag in self.imgs:
            src = re.search(r'src="([^"]+)"', tag)
            self.assertIsNotNone(src, f"img with no src: {tag[:60]}")
            path = ROOT / src.group(1)
            self.assertTrue(path.exists(), f"missing image file: {src.group(1)}")

            alt = re.search(r'alt="([^"]*)"', tag)
            self.assertIsNotNone(alt, f"img with no alt: {src.group(1)}")
            self.assertGreater(len(alt.group(1)), 30,
                               f"{src.group(1)}: alt text should describe the screen, not label it")

            declared = {k: int(v) for k, v in re.findall(r'\b(width|height)="(\d+)"', tag)}
            self.assertEqual(set(declared), {"width", "height"},
                             f"{src.group(1)}: declare width and height or the page shifts on load")
            self.assertEqual((declared["width"], declared["height"]), self._size(path),
                             f"{src.group(1)}: declared size disagrees with the file")

    @staticmethod
    def _size(path):
        data = path.read_bytes()
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":       # VP8L / VP8X / VP8
            if data[12:16] == b"VP8 ":
                import struct
                w, h = struct.unpack("<HH", data[26:30])
                return (w & 0x3FFF, h & 0x3FFF)
            if data[12:16] == b"VP8L":
                b = int.from_bytes(data[21:25], "little")
                return ((b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1)
            if data[12:16] == b"VP8X":
                return (int.from_bytes(data[24:27], "little") + 1,
                        int.from_bytes(data[27:30], "little") + 1)
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return (int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big"))
        raise AssertionError(f"unrecognised image format: {path.name}")

    def test_images_are_lazy_below_the_fold(self):
        for tag in self.imgs:
            self.assertIn('loading="lazy"', tag,
                          "the strip sits below the fold; it should not block first paint")


class PolicyPageTests(unittest.TestCase):
    """The privacy policy is the page Apple's reviewer opens — hold it to its own rules."""

    def test_policy_states_a_last_updated_date(self):
        text = parse(PRIVACY).text
        m = re.search(r"Last updated (\d{1,2} \w+ \d{4})", text)
        self.assertIsNotNone(m, "the policy must say when it was last updated")

    def test_last_updated_is_not_older_than_the_file(self):
        """Editing the policy without moving its date is how a stale policy ships."""
        from datetime import datetime
        m = re.search(r"Last updated (\d{1,2} \w+ \d{4})", parse(PRIVACY).text)
        stated = datetime.strptime(m.group(1), "%d %B %Y").date().isoformat()
        committed = last_commit_date(PRIVACY)
        if not committed:
            self.skipTest("privacy.html has no commit history yet")
        self.assertGreaterEqual(
            stated, committed,
            f"policy says {stated} but the file was last changed {committed}")

    def test_policy_names_the_contact_and_the_opt_out(self):
        text = parse(PRIVACY).text
        self.assertIn(EMAIL, text, "the policy must carry a contact address")
        self.assertIn("Settings", text)
        self.assertIn("Privacy", text)

    def test_support_page_offers_a_way_to_get_help(self):
        anchors = [h for h, _ in parse(SUPPORT).anchors]
        self.assertIn(f"mailto:{EMAIL}", anchors)

    def test_both_pages_are_indexable(self):
        # A noindex here would hide the very URL App Store Connect is given.
        for f in (PRIVACY, SUPPORT):
            robots = parse(f).meta(name="robots")
            if robots is not None:
                self.assertNotIn("noindex", robots["content"], f.name)


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
        for f in PAGES:
            html = f.read_text()
            for d in (self.LEAF_BODY, self.LEAF_VEIN):
                self.assertIn(d, html, f"{f.name}: header mark diverged from the favicon")

    def test_icons_linked_in_both_pages(self):
        for f in PAGES:
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
        # The possessive is widened past the app's own pattern: a marketing page slips
        # into the third person ("stays on the teacher's device") where the app never
        # would, and that is the same absolute wearing a different pronoun.
        (r"(observation|note|report|classroom|data|everything)[^“”\".!]{0,40}"
         r"(stay|stays) (on|in) (this|your|the [a-z]+’?'?s?|a [a-z]+’?'?s?) "
         r"(device|iPhone|phone)",
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
        for f in PAGES:
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
