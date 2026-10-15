# LG webOS Remote landing page

## 1. Direction and audience

A calm, editorial introduction for Home Assistant users installing their first dashboard remote. The existing dark remote is the focal object on a pale, spacious page. Preserve its actual screenshot and distinguish the card from the Bridge before asking the visitor to install anything. The site is published at `https://webos.royjen.com/`; it is independent of the Home Assistant app/card release.

Reference inputs: the existing remote tokens in `src/lg-webos-remote-card.js`, its public screenshot, the frontend minimalist reference (system typography, restrained borders, generous space), and the Linear reference (compressed display headings, restrained product framing and luminance layers). Adapt the references to this project; do not copy their branding. No generated artwork is required for an existing product screenshot.

## 2. Color tokens

Light: canvas #fafbfd, surface #ffffff, secondary #f0f3f7, ink #182331, muted #526174, border #d7dfe8, accent #315cbd, accent-hover #234795, accent-soft #eaf0fc, success #226645. Dark: canvas #101720, surface #16202c, secondary #1c2938, ink #f0f4fa, muted #b4c0d0, border #39495e, accent #9ebcff, accent-hover #bdd0ff, accent-soft #243650, success #a4dcb8. Code uses the existing remote's #111923 / #eef4fe / #a6c1fc. System color preference selects the theme. The optional `?theme=light` or `?theme=dark` URL parameter previews that theme locally; no persistent user settings are modified.

## 3. Type

Native system sans, SFMono-Regular/Menlo monospace. Display 72px desktop / 44px compact, -0.055em tracking, 1.04 line height, weight 650. Section title 40px / 32px, 1.15; subsection 24px. Body 18px with 1.65 line height; secondary, labels and buttons 15px, 1.5; code 14px, 1.75. The 390px layout retains 18px body. Technical paths may wrap anywhere.

## 4. Layout and space

Document owns vertical scroll. Header is in normal flow. Content limiter 1120px, outer inset 32px desktop / 24px compact, prose at most 62ch. Rhythm 4/8/12/16/24/32/40/48/64/80/96px. Hero uses two columns at 900px and up, one column below. Preview is an actual image with reserved dimensions; no false online status or working control simulation. Section grid becomes one column below 760px. Code wraps long placeholders rather than scrolling horizontally. Radius 6px controls, 12px code/small panels, 24px product stage. Borders separate grouped information; no accent side stripes. Screenshot carries the product's material and depth.

## 5. Primitives and states

Home Assistant identification: keep the project's TV mark in the header. Its `for Home Assistant` subtitle uses the 18px body token at weight 600 and primary ink. Add a `.platform-label` above the hero headline using the original official color logomark with built-in margins, a 56px square image and 24px/650 text `For Home Assistant`. The logo keeps its original colors, geometry and embedded clear space; no filters, recoloring or certification badge. The community/release eyebrow follows the label. Mobile keeps the same label size and wraps its text if needed. The hero note says `Independent community project` and the footer retains the non-affiliation notice. The asset is identified separately from the repository MIT license in third-party notices.

Reusable `.container`, `.section`, `.eyebrow`, `.button`, `.codebox`, `.step`, `.feature`, `.flow-node` and native FAQ details. Buttons and links have resting, hover, pressed and visible keyboard-focus states, minimum 44px height. Copy buttons copy the associated code or prompt and show success/failure adjacent to the action with polite announcement. Failure selects text for manual copying. Native details expose expanded state and keyboard support. Navigation and installation anchors work with JavaScript disabled; copy functionality is progressive enhancement.

## 6. Behavior

No entrance animation, autoplay, tracking, external fonts or dependencies. Color/opacity transitions 140ms on interactive controls; reduced-motion removes those transitions. The product screenshot is explicitly static. Repository, manual, compatibility, security and official documentation links navigate to real sources. The installation has three jobs: install Bridge, install card, configure and verify. Never put private device addresses, MACs or tokens in examples.

## 7. Accessibility and verification

Semantic landmarks, skip link, ordered installation steps, unique headings, descriptive image alternative, summary controls, named copy actions and live status. Check 390px, tablet, 1440px and 1920px in both themes, whole-page/end captures, keyboard navigation, copy success, copy failure, open FAQs and no primary-content overflow. Review screenshot clarity and content accuracy against README and compatibility guide. HACS and app installation remain separate; HTTPS requires trusted WSS; Wake ready is not proof that a TV will wake.

## 8. Scope and limitations

Existing screenshot shows an illustrative expanded keyboard layout, not a new device test. StanbyME Max 2 is the tested device; other compatible LG webOS families remain intended targets. The build copies the public image and landing files into an isolated static asset directory. No app/frontend runtime changes, release version changes or invented testimonials are part of this website.
