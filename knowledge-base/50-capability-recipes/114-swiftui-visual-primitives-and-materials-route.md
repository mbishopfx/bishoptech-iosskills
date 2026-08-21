# SwiftUI visual primitives and materials capability route

## Use this route when

Use this route when an app idea needs a native SwiftUI surface with:

- local, user-selected, derived, or remote images;
- SF Symbols, labels, variable values, or symbol effects;
- adaptive colors, ShapeStyle, gradients, ImagePaint, or standard Material;
- backgrounds, overlays, masks, clipping, hit regions, and safe-area edges;
- functional Liquid Glass controls or navigation groups;
- geometry-aware visual effects or content transitions;
- on-device AI image, caption, crop, OCR, classification, or review output;
- accessibility, alternate input, reduced effects, and physical-device proof.

This route composes the existing SwiftUI layout, controls, collection,
accessibility, motion, Liquid Glass, Photos, Vision, Core ML, Foundation
Models, and verification routes. It is a decision path, not a list of every
SwiftUI drawing modifier.

## Route contract

    user outcome
      -> source type and authority
      -> primitive selection
      -> stable identity and loading state
      -> image/symbol sizing and semantics
      -> shape/style/material composition
      -> functional interaction
      -> optional visual effect/transition
      -> optional AI candidate
      -> review and deterministic commit
      -> accessibility/adaptation
      -> proof

Keep these owners separate:

| Concern | Owner |
| --- | --- |
| Asset or source identity | Feature/domain model |
| Remote request and cache | Repository or image loader |
| Image phase | View or feature presentation state |
| Symbol name and fallback | Design system/feature |
| Shape and style | View/design system |
| Control action | Typed domain command |
| Visual effect parameters | View/viewport presentation |
| AI candidate/provenance | AI feature boundary |
| Saved image or metadata | Domain store and revision policy |
| Accessibility meaning | Semantic control and accessible description |
| Device/release proof | Verification plan |

## Phase 0: write the visual outcome

Write a sentence that names content and action:

    A person can [view/edit/review] [content] from [source], understand
    [state], and [action] without losing [identity, privacy, or context].

Examples:

- “A person can browse local project photos, open one at full size, and retry
  a missing thumbnail without seeing another project's photo.”
- “A person can review an on-device crop suggestion, compare it with the
  original, and commit or reject the derivative.”
- “A person can toggle a local mode with a familiar symbol and understand the
  state with VoiceOver and without animation.”
- “A person can inspect a document over a standard material action bar while
  the content remains the primary surface.”

If the sentence only says “make it glassy,” the route is underspecified.

## Phase 1: classify the source

| Source | Start with | Required boundary |
| --- | --- | --- |
| Bundle/asset catalog | Image | Build-time asset availability and scale |
| SF Symbol | Image(systemName:) or Label | Symbol availability, meaning, and label |
| Photo/file picker result | PhotosUI/File/provider pipeline, then Image | Authorization, security scope, deletion, and revision |
| Remote URL | AsyncImage for simple cases | URLSession phase, error, cache, privacy |
| Remote feed with many images | Feature-owned loader/cache | Stable key, cancellation, downsample, stale-result rejection |
| Core Graphics/UIKit image | Image initializer | Scale, orientation, lifetime, decode policy |
| Vision/Core ML output | Candidate image/observation model | Input revision, model availability, confidence, review |
| Foundation Models text around image | Candidate metadata model | Prompt/model version, source citation, user review |

Do not begin with the visual modifier. Begin by deciding whether the visible
thing is content, metadata, a status, a control, or a proposal.

## Phase 2: choose Image or AsyncImage

Choose Image for a local or already-decoded value. Choose AsyncImage when the
retrieval is simple and its phase behavior is enough. Choose a custom loader
when the product needs request authentication, explicit cache ownership,
thumbnail size, cancellation, retry/backoff, offline behavior, or a source
revision.

The simple AsyncImage route is:

    stable URL/request key
      -> AsyncImage phase
      -> placeholder
      -> success Image
      -> failure and retry route

The custom route is:

    resource key + source revision
      -> repository request
      -> task cancellation
      -> decode/downsample
      -> memory/disk cache policy
      -> ready Image value
      -> stale-result check

A view identity change must not cause the wrong image to flash into a row.
Clear the phase or show a safe placeholder while a new resource is selected.

## Phase 3: define image geometry

Record the image's geometry contract:

| Field | Example decision |
| --- | --- |
| Aspect ratio | Preserve source ratio, fixed card ratio, or full-screen viewport |
| Content mode | Fit for documents; fill for approved discovery thumbnails |
| Focal point | Center, face/subject, user-selected anchor, or none |
| Clip shape | Rectangle, rounded rectangle, circle, custom shape |
| Minimum size | Smallest legible/reviewable frame |
| Maximum size | Prevent a large source from dominating the task |
| Zoom/inspect | Whether full-size inspection is available |
| Privacy | Whether to show placeholder when the source is revoked/stale |

The frame must remain stable across loading, failure, and success. If a crop
is AI-proposed, the candidate should include focal point and crop rectangle,
not only a new bitmap. The review screen can explain what was excluded.

## Phase 4: choose symbol and control semantics

For each symbol, record:

    product meaning
      -> symbol name/variant
      -> target availability/fallback
      -> rendering mode and role color
      -> accessibility label/value
      -> state-triggered effect, if any

Use a Button, Toggle, NavigationLink, Label, or other semantic control as the
outer route. Use Image(systemName:) as the glyph, not as a replacement for
the control. If the control is icon-only, add a localized action label and
test Voice Control and Full Keyboard Access.

Use symbol effects only after the underlying state changes. A value-based
symbolEffect can be triggered by an Equatable state value; it does not certify
that a server, purchase, model, or system side effect succeeded.

## Phase 5: choose ShapeStyle and material

Use a semantic style first:

| Need | Route |
| --- | --- |
| Text/symbol hierarchy | foregroundStyle and system semantic colors |
| Selection/accent | tint/selection role plus a non-color signal |
| Structural surface | background style or standard Material |
| Decorative brand surface | explicit adaptive custom color/gradient |
| Image texture | ImagePaint only when the repeated/painted behavior is intended |
| Functional control group | native control style or Liquid Glass adoption route |

Material is for visual separation and vibrancy. Liquid Glass is a distinct
dynamic material and should be reserved for controls, navigation, and focused
functional groups. Do not use either to imply that generated output is
verified or that a process is complete.

Test light/dark appearance, increased contrast, reduced transparency, and
colorful content beneath the material. If a semantic background or material
cannot maintain legibility, simplify the layer or supply a stronger fallback.

## Phase 6: compose the surface

Use this default composition order, then adjust only with a reason:

    content layout
      -> image or text
      -> clipShape
      -> background/material
      -> overlay border/badge/state
      -> shadow at the intended clipping level
      -> contentShape
      -> semantic control
      -> accessibility description

Use background when the layer belongs behind the modified view. Use overlay
for a same-bounds border, status marker, or action affordance. Use ZStack when
the backdrop has independent layout or must span a larger safe-area region.
Use mask or clipShape only when the loss of content is acceptable.

For edge controls, prefer safeAreaInset, content margins, and native
toolbar/tab/navigation placement. Do not place a bottom glass capsule over
scrolling content and call the hidden content “handled.”

## Phase 7: add visual effects and transitions

Use visualEffect for bounded appearance based on the view's geometry. The
closure should produce a VisualEffect and should not own model state,
navigation, persistence, or side effects.

Use ContentTransition when existing content changes and a transition helps
preserve continuity. Use identity when animation should be disabled for that
content. Use symbolEffect for symbol images, and prefer a static fallback
under Reduce Motion or when the effect does not add meaning.

Document:

- input geometry or state value;
- output parameter bounds;
- maximum update frequency;
- reduced-motion/reduced-transparency behavior;
- performance budget and representative device;
- whether the effect is disabled while the app is busy or under thermal
  pressure.

## Phase 8: add an on-device AI candidate

When local intelligence is optional, add it after the deterministic visual
surface works:

    source and authorization
      -> preprocessing
      -> capability availability
      -> local model request
      -> candidate
      -> source-linked review
      -> deterministic validation
      -> explicit commit/export/share

Candidate schema:

| Field | Example |
| --- | --- |
| sourceID/sourceRevision | Photo or document revision used by the request |
| candidateID | Stable identity for partial/corrected output |
| kind | crop, caption, label, OCR, grouping, derivative |
| modelID/modelVersion | Local model/capability identity if available |
| status | preparing, partial, ready, failed, stale, accepted |
| confidence/coverage | Only when the provider actually supplies it |
| rationale/source span | What evidence the person can inspect |
| approval | pending, accepted, rejected, corrected |
| commit revision | Domain revision produced after validation |

The image view renders the candidate; the feature owns whether acceptance
changes the domain. If the source changed while inference ran, mark the
candidate stale and do not apply it automatically.

## Phase 9: accessibility and alternate input

Run the route with:

- VoiceOver and accessibility focus;
- Voice Control and alternate input labels;
- Switch Control and Full Keyboard Access;
- Dynamic Type through accessibility sizes;
- increased contrast, reduced transparency, and Differentiate Without Color;
- Reduce Motion;
- right-to-left layout;
- pointer hover/focus and hardware keyboard;
- denied photo access, unavailable model, offline image, and stale source.

The same domain action must be available through the primary control,
keyboard/pointer route, accessibility action, and any App Intent or system
route that the product supports. Decorative images should be ignored by
accessibility systems; meaningful images and symbol-only controls need useful
labels.

## Phase 10: prove the route

Minimum evidence packet:

| Claim | Minimum evidence |
| --- | --- |
| Local asset renders | Named target compile plus preview/device fixture |
| Remote image is reliable | Phase tests for loading/success/failure/retry and request identity |
| Crop is correct | Fit/fill fixtures, focal-point cases, Dynamic Type and rotation |
| Symbol is valid | Target availability compile, fallback, accessibility label, effect/reduced-motion case |
| Material is legible | Light/dark, contrast, transparency, colorful-background screenshots/device run |
| Glass is restrained | UI review showing controls/navigation only and a non-glass content fallback |
| Visual effect is bounded | Geometry fixture, reduced-effects branch, performance observation |
| AI result is reviewable | Source revision, candidate, stale/cancel/fail, approval, deterministic commit test |
| Surface is accessible | Task-based VoiceOver/Voice Control/keyboard tests, not only an audit report |
| Release route works | Signed physical-device build and any required permission, system, TestFlight, or App Store evidence |

A simulator or preview can prove layout states and deterministic fixtures. It
does not prove physical rendering, touch feel, memory/thermal behavior,
camera/Photos/model availability, or release configuration.

## Route anti-patterns

Stop and repair the route when you see:

- every card has a blur/material/glass background;
- a symbol's color is the only status signal;
- a network image is the row identity;
- a placeholder can show a previous person's image;
- a gesture is attached to a styled shape instead of a semantic control;
- a visualEffect closure writes feature state or starts a task;
- a generated caption silently becomes the accessibility label;
- a model result overwrites the source before review;
- a symbol effect implies that a purchase or server operation succeeded;
- a full-screen image ignores safe areas without a deliberate composition;
- the same fixed image frame is used at all Dynamic Type and device sizes;
- “Apple replica” is used as a quality criterion without a task and proof
  criterion.

## Sources

- [SwiftUI Images](https://developer.apple.com/documentation/swiftui/images)
- [Image](https://developer.apple.com/documentation/swiftui/image)
- [AsyncImage](https://developer.apple.com/documentation/swiftui/asyncimage)
- [Fitting images into available space](https://developer.apple.com/documentation/swiftui/fitting-images-into-available-space)
- [ContentMode](https://developer.apple.com/documentation/swiftui/contentmode)
- [SF Symbols HIG](https://developer.apple.com/design/human-interface-guidelines/sf-symbols)
- [Label](https://developer.apple.com/documentation/swiftui/label)
- [ShapeStyle](https://developer.apple.com/documentation/swiftui/shapestyle)
- [ForegroundStyle](https://developer.apple.com/documentation/swiftui/foregroundstyle)
- [Material](https://developer.apple.com/documentation/swiftui/material)
- [backgroundMaterial](https://developer.apple.com/documentation/swiftui/environmentvalues/backgroundmaterial)
- [View appearance](https://developer.apple.com/documentation/swiftui/view-appearance)
- [Adding a background to your view](https://developer.apple.com/documentation/swiftui/adding-a-background-to-your-view)
- [VisualEffect](https://developer.apple.com/documentation/swiftui/visualeffect)
- [visualEffect(_:)](https://developer.apple.com/documentation/swiftui/view/visualeffect%28_%3A%29)
- [ContentTransition](https://developer.apple.com/documentation/swiftui/contenttransition)
- [View.symbolEffect(_:options:value:)](https://developer.apple.com/documentation/swiftui/view/symboleffect%28_%3Aoptions%3Avalue%3A%29)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Materials HIG](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Color HIG](https://developer.apple.com/design/human-interface-guidelines/color)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [SwiftUI accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
