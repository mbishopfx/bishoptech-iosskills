# Visual primitives, images, symbols, and materials design

## Design outcome

A polished Apple-native screen does not come from applying the same rounded
rectangle, blur, gradient, and shadow to every component. It comes from
making the content hierarchy obvious, using familiar controls, preserving
system adaptability, and letting visual effects support an action.

Use this design loop:

    purpose
      -> content hierarchy
      -> image or symbol meaning
      -> shape and style role
      -> material/background composition
      -> functional control layer
      -> state and AI review
      -> accessibility and alternate input
      -> device proof

The target is an original product that feels at home on iOS 26. “Apple-like”
means disciplined use of platform conventions, not a pixel replica of Apple's
private applications or a claim of Apple endorsement.

## 1. Start with the semantic hierarchy

Before choosing an image, symbol, or material, write what the person should
notice and what they should do:

| Layer | Question | Typical visual treatment |
| --- | --- | --- |
| Primary content | What is the thing being viewed or edited? | Text, image, chart, document, or media surface with the strongest room |
| Primary action | What can the person do next? | Button, navigation route, toolbar item, or compact functional glass control |
| Context | What explains the content? | Secondary text, metadata, source, timestamp, or subtle semantic style |
| State | Is the content loading, stale, partial, failed, or awaiting review? | Explicit text/indicator plus restrained symbol or style |
| Optional decoration | Does this improve recognition or mood? | Decorative Image, Shape, gradient, or low-emphasis material |
| System handoff | Is a system surface or external capability involved? | Native picker, sheet, App Intent, share, permission, or confirmation |

A photo, generated caption, SF Symbol, and action button do not belong in one
undifferentiated card. Give each a job and an accessible order.

## 2. Image direction

### Choose the image role

Use the source and the person's goal to choose the visual treatment:

| Image role | Design decision |
| --- | --- |
| Hero or source image | Give the image room; preserve its focal content and label it |
| Thumbnail | Use a consistent crop only if edge loss is acceptable |
| Document/receipt | Prefer full-content fit, readable zoom, and an inspect route |
| Profile or identity image | Avoid ambiguous fallback images; protect privacy during loading |
| Media artwork | Use the media's meaning and preserve the playback/metadata route |
| Empty-state illustration | Mark decorative if adjacent text explains the message |
| AI derivative | Show source, candidate state, and review/commit actions |
| Background atmosphere | Keep contrast and safe-area behavior under control; do not hide content |

Fit and fill are not interchangeable styles. A full-bleed image can be
beautiful but is a bad choice when it removes information. For a feed or grid,
define the crop/focal policy in the data model or fixture rather than letting
different cells choose different crops accidentally.

### Preserve image stability

An image surface should maintain its frame through loading, failure, and
success. A good placeholder has the same aspect ratio and an obvious state.
Avoid displaying stale content from the previous row while a new request is
pending. Avoid a skeleton that looks like a confirmed photo, person, or
document.

When an image is remote or user-selected, the screen should be able to say:

- loading or queued;
- loaded from a source;
- unavailable or failed;
- access revoked or expired;
- stale relative to the current domain revision;
- derived by an on-device operation;
- ready to review or committed.

A thumbnail can be lower fidelity than the source, but the interface should
not imply that the thumbnail is the original file or the complete analysis.

## 3. SF Symbols and iconography

### Use symbols for familiar actions

A familiar action should use a recognizable SF Symbol inside the standard
SwiftUI control or Label when the symbol is available. Keep the label
visible when the action is not obvious from context. Symbol-only buttons need a
localized accessibility label and an alternate input name where appropriate.

Good symbol decisions are:

- direct rather than metaphorically clever;
- consistent across the same action;
- available on the target deployment;
- visually aligned with nearby text;
- not dependent on color alone;
- backed by a text or accessibility meaning.

Use a custom asset when the visual is genuinely product-specific, a logo,
an illustration, or an object that SF Symbols does not represent. Do not
replace a standard action icon with a custom line drawing simply to make a
screen look different.

### Weight, scale, and rendering

Treat symbol weight and scale like typography. A compact toolbar action,
body-text glyph, empty state, and hero illustration have different visual
roles. Avoid manually forcing every symbol to the same fixed size.

Use monochrome, hierarchical, palette, or multicolor rendering according to
the symbol's meaning and supported configuration. A palette should have
stable role colors; a multicolor symbol should not become a random status
badge. If a custom tint makes a symbol look like a link, destructive action,
or selected state, use that role consistently everywhere.

A variable symbol value is a visual encoding of a bounded value, not a
replacement for a label or exact measurement. Put the number, unit, or
accessible value next to it when precision matters.

### Motion for symbols

Use a symbol effect when a committed local state changes and the effect helps
the person notice that change. Use it for feedback, not for suspense:

| Event | Good motion role | Do not imply |
| --- | --- | --- |
| Toggle changed | Brief symbol transition | Server synchronization completed |
| Item saved locally | Small confirmation effect | Cloud backup is complete |
| Playback state changed | Play/pause replacement | Audio is audible on every route |
| New review candidate | Controlled insertion/replacement | Candidate is approved |
| Destructive action | Usually a stable state plus confirmation/undo | Deletion is reversible without policy |

Honor Reduce Motion and keep a static state that is equally understandable.

## 4. Surface hierarchy

Use a small number of surface tiers:

1. content layer: the image, text, chart, document, or media itself;
2. separation layer: background color, standard Material, divider, or
   structural shape;
3. functional layer: a button group, toolbar, tab bar, navigation control, or
   focused review action;
4. transient layer: confirmation, progress, selection, or error state.

Liquid Glass is primarily a functional/control and navigation layer in this
system. It should not coat every content card. Standard materials can support
content separation without making content feel like a control.

### Material choices

Choose a material because it separates layers and preserves legibility, not
because it produces a pleasing tint in one screenshot. Test with light/dark
appearance, increased contrast, colorful backgrounds, reduced transparency,
and Dynamic Type. If the content becomes hard to read, simplify the background
or use a stronger semantic surface.

A useful native surface often looks like:

    content
      -> one coherent separator/material
      -> one functional action group where needed
      -> system placement and safe-area handling

Avoid stacking a translucent material, blur, gradient, shadow, and Liquid
Glass effect on the same small card. The resulting surface may be visually
busy, less accessible, and more expensive to render.

## 5. Backgrounds, overlays, masks, and shapes

Design with bounds in mind:

| Layering tool | Design question |
| --- | --- |
| Background | Should this layer sit behind the modified view and share its size? |
| Overlay | Should this border, badge, or status layer sit above the content? |
| Clip shape | Should the artwork be trimmed to a geometric frame? |
| Mask | Should alpha from another view control what is visible? |
| Content shape | What region should respond to touch, pointer, or accessibility? |
| ZStack | Does the background need an independent layout, larger frame, or safe-area reach? |

A visible surface and an interaction surface may need different bounds, but
that difference should be intentional. A card whose whole rounded rectangle
is tappable should use a semantic control or contentShape; a tiny icon should
not unexpectedly capture the entire row.

A border should follow the same shape as the surface. A shadow that needs to
extend outside a clip should be applied at the correct level. A full-screen
background that ignores safe areas should be visually separate from the
safe-area-aware content and controls.

## 6. Image and symbol states in a native screen

A component library should define visual states before it defines tokens:

| State | Image | Symbol | Text/action |
| --- | --- | --- | --- |
| Empty | Neutral illustration or no image | Empty-state symbol | Explain what is absent and next action |
| Loading | Stable placeholder | Progress or pending symbol | Say what is being loaded when useful |
| Ready | Source image or asset | Normal semantic glyph | Show content and primary action |
| Stale | Existing image with subtle stale marker | Refresh or warning glyph | Explain freshness and recovery |
| Failed | Safe fallback, never stale private content | Error/retry glyph | Offer retry, offline, or alternate route |
| Selected | Same content with selection state | Check or selection glyph | Preserve selection semantics |
| Disabled | Same structure with disabled treatment | Dimmed but legible symbol | Explain unavailable action if useful |
| Candidate | Source plus bounded derivative/annotation | Review/edit glyph | Accept, reject, correct, inspect |

Do not encode the whole state through opacity. People with low vision,
Differentiate Without Color enabled, or VoiceOver enabled need a meaningful
state through structure, words, actions, or accessibility values.

## 7. On-device AI visual review

Design AI output as an inspectable layer over a known source:

    source image/document
      -> local observation or inference
      -> candidate overlay or derivative
      -> provenance and uncertainty
      -> accept / reject / edit / retry
      -> deterministic commit

A good review surface answers four questions without opening a debug panel:

1. What source did this result use?
2. What did the device produce?
3. What is uncertain, partial, or unavailable?
4. What changes if the person accepts it?

Keep the source image visually primary. Use a restrained candidate badge,
annotation overlay, or side-by-side comparison. Do not style an unreviewed
candidate like a final system-confirmed fact.

For image captions, object labels, OCR, crop suggestions, or generated
summaries, preserve a user correction route. Do not silently overwrite the
source asset or accessibility label. If the candidate affects sharing,
deletion, payment, health, identity, or communication, add an explicit
confirmation and show the deterministic validation result before the side
effect.

### AI review visual contract

| Candidate state | Design treatment |
| --- | --- |
| Preparing | Stable source frame plus bounded progress state |
| Unavailable | Explain device/model/permission limitation and alternate route |
| Partial | Show what exists and what is incomplete |
| Ready to review | Candidate layer and clear accept/reject/edit actions |
| Rejected | Return to source without losing source state |
| Accepted locally | Show committed revision and undo/restore if product policy supports it |
| Stale | Identify source revision mismatch and require re-run |
| Failed | Preserve source and provide retry or export fallback |

A glass container can group the review actions when they are compact and
functional. The candidate itself should not become a decorative glass object.

## 8. Adaptive and accessible visual design

Test the visual system as a set of environments:

- iPhone compact width and regular width;
- iPad split view and multitasking;
- portrait and landscape;
- light and dark appearance;
- Dynamic Type through accessibility sizes;
- increased contrast and reduced transparency;
- Reduce Motion;
- right-to-left languages;
- VoiceOver, Voice Control, Switch Control, and Full Keyboard Access;
- pointer hover/focus and hardware keyboard;
- offline, denied, unavailable-model, and stale-source paths.

Use semantic system colors and styles where possible. If custom colors are
part of the brand, provide variants for appearance and increased contrast.
Do not make an image overlay, material tint, or glass reflection carry the
only distinction between primary and secondary content.

Use layout adaptation instead of shrinking typography or controls until they
fit. An image can move above text, a label can become title-only or icon-only
where the meaning remains clear, and a functional action group can move into
a toolbar or sheet. Preserve the same domain command and accessibility
route through every branch.

## 9. Native polish review

A visual review should ask:

- Is the primary content obvious at a glance?
- Does every icon have a reason and a stable meaning?
- Are images framed according to what must remain visible?
- Are materials separating layers rather than disguising content?
- Is Liquid Glass limited to controls, navigation, or focused actions?
- Do loading and failure states keep geometry stable?
- Does a generated candidate look like a candidate?
- Can the person understand and complete the task without motion, color, or
  a hidden gesture?
- Does the surface still work with a large Dynamic Type size?
- Does it look and feel correct on a real physical device?

Avoid describing a screen as “Apple replica” in product copy or internal
requirements. Describe the concrete native qualities instead: semantic
controls, system typography, adaptive layout, restrained material hierarchy,
SF Symbols, accessible states, and physical-device proof.

## Design token starter

Use semantic tokens, not component-specific colors:

| Token family | Examples |
| --- | --- |
| Content | primary text, secondary text, tertiary text, content background |
| Action | tint, destructive, selected, disabled, focus |
| Surface | background, elevated, separator, standard material, functional glass |
| State | loading, success, warning, error, stale, candidate |
| Geometry | control shape, card shape, image crop shape, hit shape |
| Motion | emphasis, state change, insertion, reduced-motion fallback |
| Accessibility | label, value, hint, trait, alternate input name |

A token should have a role and an adaptation policy. “Blue card” is not a
role. “Primary action tint” is a role that can be inspected across appearance,
contrast, and platform context.

## Sources

- [Images HIG](https://developer.apple.com/design/human-interface-guidelines/images)
- [SF Symbols HIG](https://developer.apple.com/design/human-interface-guidelines/sf-symbols)
- [Icons HIG](https://developer.apple.com/design/human-interface-guidelines/icons)
- [Materials HIG](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Color HIG](https://developer.apple.com/design/human-interface-guidelines/color)
- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Motion HIG](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Image](https://developer.apple.com/documentation/swiftui/image)
- [AsyncImage](https://developer.apple.com/documentation/swiftui/asyncimage)
- [Fitting images into available space](https://developer.apple.com/documentation/swiftui/fitting-images-into-available-space)
- [Label](https://developer.apple.com/documentation/swiftui/label)
- [ShapeStyle](https://developer.apple.com/documentation/swiftui/shapestyle)
- [Material](https://developer.apple.com/documentation/swiftui/material)
- [View appearance](https://developer.apple.com/documentation/swiftui/view-appearance)
- [Adding a background to your view](https://developer.apple.com/documentation/swiftui/adding-a-background-to-your-view)
- [ContentShapeKinds](https://developer.apple.com/documentation/swiftui/contentshapekinds)
- [VisualEffect](https://developer.apple.com/documentation/swiftui/visualeffect)
- [ContentTransition](https://developer.apple.com/documentation/swiftui/contenttransition)
- [View.symbolEffect(_:options:value:)](https://developer.apple.com/documentation/swiftui/view/symboleffect%28_%3Aoptions%3Avalue%3A%29)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
