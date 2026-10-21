# DiscoveryLabNL briefing site

Public single-page site at https://discoverylabs.nl, served by GitHub Pages from `main`. Everything (content,
styles, behaviour) is in `index.html`; images in `img/`, fonts beside it, GSAP 3.13 vendored in `vendor/`.

## Commands
- Preview locally: `python3 -m http.server 8000`, then open http://localhost:8000/?v=<anything>
- Deploy: `git push origin main`. Pages deploys automatically; `CNAME` maps the domain.
- Verify after a deploy with a hard refresh or a new cache-buster query (`?v=2`). Browsers and Pages cache
  aggressively; an unchanged-looking page is usually the cache, not the code.

## Structure
- Sections in order: landing, claim slides, world today, pillars, domains, consortium, landscape, positioning
  (hidden by a feature-flag rule), roadmap, contact.
- The consortium map is an SVG built from the JavaScript `consortium` object (campus, national and international
  rings; every member has status `partner` or `open`). Industry partners are chips built from the `industry` array;
  both open the same slide-in panel. Change the data, not the rendered SVG.
- Partner data mirrors documents kept elsewhere. Change it only when the owner asks, and say in the commit what
  changed.

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
