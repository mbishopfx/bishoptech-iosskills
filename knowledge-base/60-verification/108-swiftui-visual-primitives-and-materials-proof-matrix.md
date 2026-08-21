# SwiftUI visual primitives and materials proof matrix

## Purpose

Use this matrix when a screen claims native SwiftUI visual quality, reliable
image handling, SF Symbol correctness, adaptive material hierarchy, bounded
visual effects, or reviewable on-device AI results. A screenshot can show a
composition; it cannot prove image lifecycle, accessibility, availability,
thermal behavior, or a release build.

Record the Xcode version, SDK, deployment target, device model and OS, build
configuration, locale, color scheme, Dynamic Type setting, accessibility
settings, source fixture, model/capability state, and evidence date for every
run.

## Evidence vocabulary

| Level | What it can support | What it cannot support |
| --- | --- | --- |
| Source/documentation | API intent, design guidance, availability questions to investigate | That this app compiles or behaves correctly |
| Static review | Ownership, semantic primitive choice, source links, fallback policy | Runtime loading, rendering, touch, accessibility, performance |
| Named-target compile | Imports, declarations, availability checks, target membership | Remote data, model readiness, physical rendering, release settings |
| Unit/feature test | Phase/state transitions, identity, stale-result rejection, candidate commit policy | Real image services, device GPU behavior, VoiceOver ergonomics |
| Preview/UI fixture | Layout branches, local states, labels, fit/fill geometry, deterministic review flow | Device glass rendering, real network, Photos permission, thermal behavior |
| Accessibility inspection | Accessibility tree and likely issues | Completion of real tasks under every assistive technology |
| Simulator | Screen states, UI automation, deterministic alternate layouts | Universal device performance, physical touch, camera/media/model hardware |
| Signed physical device | Rendering, input, accessibility task, memory/thermal observation, hardware capability | Every device/OS, release approval, production provider behavior |
| TestFlight/release build | Distribution configuration and install-path behavior | App Store approval, universal coverage, server/provider reliability |
| Production observation | Real operating conditions within the named scope | A guarantee for all users or all source/model inputs |

Never upgrade a source claim into a runtime claim without the evidence level
that supports the runtime behavior.

## Test fixture model

Create deterministic fixtures for:

| Fixture | Required data |
| --- | --- |
| Local image | Asset name, dimensions, orientation, light/dark background |
| Remote success | Stable test URL or local test server response, source revision |
| Remote failure | timeout, non-2xx, invalid bytes, cancellation, retry |
| Stale image | same row ID with a new resource key/source revision |
| Fit/fill | portrait, landscape, square, panoramic, transparent image, document |
| Symbol | supported symbol, unavailable symbol, rendering modes, variable value |
| Symbol state | unchanged value, committed change, rapid changes, reduced motion |
| Material | light/dark, increased contrast, reduced transparency, colorful content |
| Background/overlay | safe-area edge, clip, shadow, border, hit region, rotation |
| Visual effect | bounded geometry values, effect disabled/reduced, high-frequency scroll |
| AI candidate | source revision, partial, ready, stale, unavailable, rejected, accepted |
| Accessibility | labels, decorative art, large text, RTL, VoiceOver order, keyboard |
| Lifecycle | view disappearance, background, memory pressure/thermal fallback |

Use fixed identifiers for rows, resources, and AI candidates. A partial model
update should replace the same candidate fixture rather than create a new row.

## Core proof matrix

| Claim under review | Minimum proof | Stronger proof | Do not claim from |
| --- | --- | --- | --- |
| Image is a valid bundled asset | Target compile and asset lookup fixture | Signed device in each intended appearance | A design screenshot |
| Image is accessible | Labeled/decorative fixture and accessibility tree | VoiceOver task with action completion | Visible text alone |
| AsyncImage handles phase changes | Deterministic loading/success/failure fixture | Network interruption and retry on device | One successful load |
| Custom loader cancels safely | Unit test for owner/key changes and stale-result rejection | Feed scroll, background, memory/thermal observation | Lazy container alone |
| Crop preserves product meaning | Fit/fill/focal-point fixtures | Physical device across rotation and Dynamic Type | A single thumbnail |
| Symbol is available | Target compile with availability/fallback | Named oldest supported OS device | Symbol name remembered from another SDK |
| Symbol has correct meaning | Design review and localized accessibility label | Voice Control/VoiceOver task | Color or glyph shape alone |
| Symbol effect is state-bound | Equatable value test and reduced-motion fixture | Physical interaction under Reduce Motion | Animation appearing once |
| Semantic color adapts | Light/dark and increased-contrast fixtures | Device settings task with custom colors | One light-mode screenshot |
| Material remains legible | Background/appearance/contrast fixture | Device test over representative content | Material's apparent tint |
| Liquid Glass is restrained | Surface inventory showing functional use | Device review with content, controls, and reduced effects | A blurred rounded rectangle |
| Background/overlay bounds are correct | Geometry fixture for clip/overlay/content shape | Touch/pointer/rotation device task | Visual approximation |
| VisualEffect is bounded | Closure/static review, parameter bounds, reduced-effect fixture | Instruments/profile on representative device | A successful preview |
| Content transition preserves context | State change fixture and identity fallback | Device interaction with reduced motion | A GIF or isolated animation |
| AI candidate is reviewable | Candidate schema, source revision, stale/cancel/failure tests | Physical device with model availability and review commit | A generated image or caption |
| Accessibility route is usable | Accessibility tree plus task fixture | VoiceOver, Voice Control, keyboard, Switch Control device runs | Automated audit alone |
| Performance is acceptable | Named workload and baseline metric | Release build on representative devices with Instruments/MetricKit plan | Newest device Debug run |
| Release visual route works | Signed build archive/install evidence | TestFlight/release install with permission/system states | Simulator or preview |

## Image and AsyncImage proof

### Phase tests

For each remote image, exercise:

1. initial empty/loading state;
2. successful response;
3. invalid image bytes;
4. timeout or offline;
5. cancellation because the row/resource changed;
6. retry after failure;
7. source revision changed while the request was in flight;
8. access revoked or the asset was deleted;
9. low-memory or thermal fallback if the loader has one;
10. app background/foreground behavior.

Confirm the failure branch does not display a previous private image. Confirm
the retry command maps to the same feature-owned request policy, and confirm a
stale response cannot overwrite a newer source revision.

### Geometry tests

Use portrait, landscape, square, panoramic, transparent, and document
fixtures. Prove that:

- fit does not crop required content;
- fill clips only where the product permits it;
- the clip shape matches the surface;
- the placeholder and success frame remain stable;
- the image remains usable at large Dynamic Type and in compact width;
- rotation and split view do not create accidental distortion;
- a full-screen background has deliberate safe-area behavior.

### Resource and privacy tests

Record whether the loader holds original bytes, decoded images, thumbnails,
or only a cache key. Confirm deletion and revocation clear or invalidate
private content according to policy. Do not use a screenshot or a memory
snapshot as proof that retention is correct; inspect the actual owner and
lifecycle.

## SF Symbol proof

| Case | Verify |
| --- | --- |
| Supported symbol | Name resolves in the target SDK and renders on the oldest intended OS |
| Unsupported symbol | Semantic fallback preserves the action and label |
| Rendering mode | Monochrome/hierarchical/palette/multicolor result is legible and meaningful |
| Weight/scale | Aligns with text/control hierarchy at Dynamic Type sizes |
| Variable value | Bounded value is clamped and paired with an exact accessible value where needed |
| Icon-only control | Localized accessibility label, Voice Control name, keyboard route |
| Symbol effect | Trigger occurs only for the intended Equatable value change |
| Reduced motion | Static state remains understandable and action remains available |
| Rapid changes | Effects do not create a misleading queue or imply completed side effects |
| Localization/RTL | Directional meaning and placement remain correct |

Keep a fixture for an unavailable symbol. A current Xcode preview using a
newer symbol does not prove that the deployment target has it.

## Material and Liquid Glass proof

Test each material or glass surface over:

- high-contrast and low-contrast content;
- light and dark appearance;
- increased contrast;
- reduced transparency;
- colorful images and dynamic content;
- large and small text;
- portrait, landscape, and iPad split layouts;
- an empty, loading, error, and candidate state.

Record whether the surface is content, separation, functional control, or
transient. If it is functional, verify the control action, label, focus,
keyboard/pointer route, and safe-area relationship. If it is content, ask
whether a simpler background style would preserve hierarchy better.

A Liquid Glass visual inspection should include:

- content remains visible and legible beneath the functional layer;
- actions are not hidden only in the glass treatment;
- grouped glass controls use one coherent visual group;
- content cards do not all receive the same glass shell;
- reduced transparency and contrast preserve the task;
- the surface does not imply that AI output is approved or a task completed.

## Background, overlay, and hit-region proof

Build a geometry fixture that exposes:

- modified view bounds;
- background bounds;
- overlay bounds;
- clip shape;
- shadow extent;
- contentShape/hit region;
- safe-area inset and scrolling content region.

Then exercise:

- tap in the visible surface but outside the label;
- tap outside the intended shape;
- pointer hover/focus;
- VoiceOver focus;
- keyboard activation;
- scrolling under bottom controls;
- rotation and keyboard appearance;
- Dynamic Type reflow.

A passing screenshot only proves visual alignment at one size. The command
must still be available through the correct semantic control.

## VisualEffect and transition proof

For a visual effect, record the geometry input and bounded output. Confirm:

- the effect closure is visual-only;
- no model, persistence, navigation, or network side effect occurs;
- the effect can be disabled or simplified;
- high-frequency updates do not cause a large state tree to recompute;
- reduced-motion/reduced-transparency behavior remains legible;
- representative images and devices meet the performance budget.

For a content transition, test unchanged content, the intended state change,
rapid changes, insertion/removal, cancellation, and Reduce Motion. Confirm
that identity is used when animation should not expose intermediate or
misleading content.

## On-device AI result proof

Use an evaluation fixture with:

    sourceID + sourceRevision
      -> requestID
      -> capability/model state
      -> candidateID
      -> partial/ready/error
      -> review action
      -> deterministic validation
      -> commit revision

Verify:

- unavailable model/device produces an explicit fallback;
- permission denial does not fabricate an image or label;
- cancellation stops or ignores stale work;
- partial output stays under one candidate identity;
- source revision mismatch marks the result stale;
- rejection preserves the source;
- acceptance changes only the intended domain fields;
- user correction is retained according to the product policy;
- generated text is not silently used as accessibility truth;
- private image bytes and candidate metadata follow retention/deletion policy;
- share/export/side-effect routes require the product's explicit review;
- model and prompt/version metadata are captured where the feature needs them.

A successful model request is not proof that the suggestion is correct. The
proof claim should name what was tested: for example, “candidate source
revision and rejection flow pass on device,” not “AI understands images.”

## Accessibility and alternate-input proof

Run task-based tests:

1. open the screen;
2. identify the primary image/content;
3. understand loading/error/candidate status;
4. activate the primary action;
5. inspect or correct an AI candidate;
6. recover from failure;
7. complete the task without color or animation;
8. complete the task with a hardware keyboard or alternate input where
   supported.

Record VoiceOver order, labels, values, traits, focus movement, and whether
decorative images are ignored. Test large text and right-to-left layout, not
only an accessibility audit report.

## Performance and device proof

Measure a representative fixture:

- number and dimensions of images;
- scroll length and reuse;
- cache warm/cold state;
- number and size of material/effect layers;
- model preprocessing and inference work;
- cancellation frequency;
- memory, CPU/GPU, frame hitch, energy, and thermal behavior;
- release versus Debug configuration.

Use the tools appropriate to the claim, such as Xcode performance testing,
Instruments, signposts, and MetricKit. A lazy stack, a preview, or a device
run on the newest hardware does not establish a universal performance claim.

## Release packet

For a release candidate, attach:

- selected SDK/Xcode and deployment target;
- target availability and fallback record;
- asset/resource membership and privacy strings;
- entitlements and Photos/provider/model permissions as applicable;
- signed archive and installation evidence;
- physical-device screenshots or recordings for visual material/glass states;
- accessibility task results;
- AI model availability and fallback behavior;
- TestFlight or release-build result if distribution behavior is in scope;
- known unsupported devices, OS versions, symbols, formats, and model states.

Separate “compiles,” “renders,” “is accessible for the tested task,” “works on
the named device,” and “is release-ready.” They are different claims.

## Sources

- [Image](https://developer.apple.com/documentation/swiftui/image)
- [AsyncImage](https://developer.apple.com/documentation/swiftui/asyncimage)
- [Fitting images into available space](https://developer.apple.com/documentation/swiftui/fitting-images-into-available-space)
- [SF Symbols HIG](https://developer.apple.com/design/human-interface-guidelines/sf-symbols)
- [Icons HIG](https://developer.apple.com/design/human-interface-guidelines/icons)
- [ShapeStyle](https://developer.apple.com/documentation/swiftui/shapestyle)
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
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [XCUITest](https://developer.apple.com/documentation/xctest)
- [XCUIAutomation](https://developer.apple.com/documentation/xcuiautomation)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
