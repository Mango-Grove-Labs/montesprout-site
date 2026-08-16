<!--
  PROGRESS.md — the CURSOR for the montesprout-site repo.
  Sections are OVERWRITTEN, never appended. Per-phase narrative goes to
  docs/JOURNAL.md in the same commit. See ~/.dotfiles/docs/autopilot/doc-contract.md.
-->

# Project Progress

- **Project:** MonteSprout — website (montesprout.app)
- **Target milestone:** launch-ready site — stop here for review
- **Status:** `in-progress`
- **Updated:** 2026-08-16

---

## Reference docs (the router — `docs/` files don't auto-load)

- **PRD (immutable intent):** [`docs/PRD.md`](./docs/PRD.md) — a pointer; product intent of record is the app repo's
- **Roadmap (future — plan prose for unshipped phases):** [`docs/ROADMAP.md`](./docs/ROADMAP.md)
- **Overview (present — the site as built):** [`docs/OVERVIEW.md`](./docs/OVERVIEW.md)
- **Journal (past — append-only per-phase narrative):** [`docs/JOURNAL.md`](./docs/JOURNAL.md)
- **Decisions log:** [`docs/DECISIONS.md`](./docs/DECISIONS.md)
- **Engineering contract:** this repo has **no `docs/architecture.md` by design** — the site's four
  invariants live in [`CLAUDE.md`](./CLAUDE.md) § Conventions, and the authoritative source for the
  Sunrise tokens and the leaf mark is the **app** repo (`~/Developer/MonteSprout/docs/architecture.md`
  §8 · `ios/…/DesignSystem/Motifs.swift` § `LeafArt`). A second architecture file here would be the
  drift `tests/test_site.py` exists to prevent.
- **Sibling app repo** (`~/Developer/MonteSprout`): its `docs/JOURNAL.md` / `docs/DECISIONS.md` carry
  the app-side half of Phase 18, and `docs/plans/2026-08-16-external-testing-drafts.md` §§1–2 holds the
  paste-ready privacy + support copy.
- **Active surface:** the **repo root is the deployed site** (GitHub Pages serves only a branch root or
  `/docs`, so the monorepo `<surface>/` layout is deliberately not used here — DECISIONS § "/adopt").

---

## Roadmap

<!-- The only live checklist — completion truth. Plan prose for unshipped phases: docs/ROADMAP.md.
     Phase labels continue from the app repo's Phase 18 because this repo's commit messages
     (feat(18.2)…feat(18.5)) reference them; new site phases take 19+ in THIS repo's namespace. -->

- [x] **Phase 18 — Marketing/legal site** (web) <!-- founding phase; labels match this repo's commit prefixes -->
  - [x] 18.2 Site repo + GitHub Pages live
  - [x] 18.6 Favicon, OG image, touch icon + SEO meta — pulled forward into 18.2 (owner call)
  - [x] 18.3 Privacy + support pages
  - [x] 18.5 Landing page — screenshot strip split out to 18.7 (owner call)
  - [x] 18.4 montesprout.app live on enforced HTTPS; org domain-verification TXT in place
  - [x] 18.7 Real app screenshots — three-shot strip, sample classroom only (no real child data)
- [x] 🏁 **MILESTONE: launch-ready site** — reached 2026-08-16
- [ ] **Phase 19 — Post-launch site growth** (web) <!-- backlog, re-filed from the app repo's ROADMAP § 18 -->
  - [ ] 19.1 Cookieless web analytics — blocked on a zero-JS exemption decision (CLAUDE.md bans scripts; the tests assert zero)
  - [ ] 19.2 "Notify me at launch" email capture
  - [ ] 19.3 Headline A/B test — candidates already chosen (DECISIONS § "The hero headline"); downstream of 19.1
- [ ] **Phase 20 — School-admin trust one-pager** (web) <!-- trigger: the school-paid conversation -->
  - [ ] 20.1 Privacy/AI one-pager for school administrators — the school-facing productization of what 18.3 already states
- [ ] **Phase 21 — Design pass** (web) <!-- post-tester; today's site is deliberately hand-rolled -->
  - [ ] 21.1 Design round on the landing page — the current pages are on-brand but unstyled by a designer

---

## Current Status

- **Current phase / sub-phase:** none in flight — **Phase 18 is complete**; the site is launch-ready
- **State:** idle
- **Last completed:** 18.7 — the screenshot strip (capture → evidence → report), shot from the sample classroom
- **Build:** n/a (no build step) · **Tests:** green (55/55, zero skips) · **Simulator-verified:** n/a (web)

---

## Next Concrete Action

> **Nothing is queued.** Phase 18 is done and the site is launch-ready at montesprout.app. The
> remaining phases are all trigger-gated, not scheduled: **19** (analytics → email capture → headline
> A/B) waits on the zero-JS decision in Needs You; **20** (school-admin one-pager) waits on the
> school-paid conversation; **21** (design pass) is post-tester. Pick one deliberately rather than by
> frontier order.

---

## Open Decisions (reversible — defaults chosen, proceeding)

- _none yet_

---

## Needs You (irreversible / load-bearing — halts the run)

- **Does the site get JavaScript for analytics?** — 19.1 needs either a script tag, which changes this
  repo's zero-JS convention *and* the test that asserts it (so it needs a `docs/DECISIONS.md` entry
  first), or a log-based/serverless approach that keeps the property. Options: cookieless script /
  server-side only / drop 19.1. (not blocking until 19.1)

The app repo's `PROGRESS.md` § Phase 18 still shows the site checklist from before this repo owned it.
That is a one-line cleanup over there, not a halt here — see DECISIONS § "/adopt".

---

## Assumptions & Risks

- **The site is downstream of the app's design system.** Sunrise tokens (`assets/styles.css`) and the
  leaf beziers (`assets/favicon.svg`, both page headers, `tools/make_images.py`) are transcriptions.
  Changing either here without changing the app first is drift; `tests/test_site.py` fails on it.
- **Privacy copy is a contract.** Any claim about what leaves a teacher's device must match the app's
  behaviour (app repo `docs/architecture.md` §13). Re-verify a touched claim against the code before
  editing `privacy.html`; a claim and the code disagreeing is a bug to raise in the app repo, never a
  reason to soften the page.
- **18.7 needs privacy care, not just a build:** real classroom data must never reach a public page.
- **Pillow** is the only build-time dependency, used solely by `tools/make_images.py`; the fonts it
  renders with are vendored under `tools/fonts/` (OFL).
- **A push to `main` is a deploy.** There is no CI and no staging; `python3 -m http.server` is the
  preview and the test suite is the gate.

---

## How to Resume

A fresh session should: read this top-to-bottom → do **Next Concrete Action** → on completion, check
off the roadmap item, **overwrite** **Current Status** + **Next Concrete Action** (the outgoing
narrative goes into a new `docs/JOURNAL.md` entry, not stacked here), add any new **Open Decisions**
one-liners (full rationale → `docs/DECISIONS.md`), run the tests, commit, then continue or stop at the
milestone. If **Needs You** is non-empty, STOP and surface those items.
