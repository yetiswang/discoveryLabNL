# DiscoveryLabNL briefing site

Public single-page site at https://discoverylabs.nl, served by GitHub Pages from `main`. Everything (content,
styles, behaviour) is in `index.html`; images in `img/`, fonts beside it, GSAP 3.13 vendored in `vendor/`.

## Commands
- Preview locally: `python3 -m http.server 8000`, then open http://localhost:8000/?v=<anything>
- Deploy: `git push origin main`. Pages deploys automatically; `CNAME` maps the domain.
- Verify after a deploy with a hard refresh or a new cache-buster query (`?v=2`). Browsers and Pages cache
  aggressively; an unchanged-looking page is usually the cache, not the code.

## Structure
- Sections in order: landing, challenge, pillars, domains, campus, positioning, roadmap, team, stakeholders, contact.
- The stakeholder map is an SVG with a 1000x1000 viewBox centred at (500,500). Rings: Core r=90, Committed r=200,
  In Dialogue r=310, Planned r=420. Node data lives in the JavaScript `stakeholders` object; the stats shown on the
  page are derived from it, so change the object, not the rendered SVG.
- The engagement data on this page (the `stakeholders` object) mirrors documents kept elsewhere. Change it only
  when the owner asks, and say in the commit what changed.

## Animation rules
- Reveals use an IntersectionObserver engine. Programmatic scrolls (rail, anchors, hash jumps) suppress reveals so
  they still play when the reader scrolls there.
- The Discovery Loop on the methodology section is a GSAP ScrollTrigger pin (600%) with one act per scroll step,
  arrow keys to step, and a static fallback below 1024 px, on touch and with reduced motion. Keep all three paths
  working.
- `html { scroll-behavior: smooth }` breaks GSAP scroll tweens. It is suspended during programmatic glides; keep it
  that way when touching scroll code.
- No third-party origins: vendor any library into `vendor/`.

## Conventions
- Wording is public and funding-neutral: describe the initiative's capability, not internal negotiations.
- Test in Safari and Chrome, at phone width (390 px) and desktop width, before pushing.
- Commit messages: plain, saying what changed on the page. No Claude trailers.
