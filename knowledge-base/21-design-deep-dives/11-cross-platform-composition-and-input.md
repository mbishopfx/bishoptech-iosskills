# Cross-Platform Composition and Input Design

## Design objective

Make one product feel native across Apple platforms without copying Apple’s proprietary screens, branding, or content. The durable skill is to preserve the user outcome and domain meaning while changing the information hierarchy, controls, system surfaces, input model, and spatial/physical assumptions for the target.

Use this loop:

`outcome -> information hierarchy -> platform surface -> input path -> accessibility path -> material/motion -> proof`

Do not begin with “How do I make the same card look like Apple everywhere?” Begin with “What must the person understand or accomplish on this platform, and what is the shortest native path?”

## Shared meaning, split surfaces

Model a feature as four contracts:

1. **Domain contract.** The user outcome, records, validation rules, authorization rules, timestamps, provenance, and side-effect policy.
2. **Feature-state contract.** Loading, empty, permission, unavailable, draft, review, success, failure, cancellation, and navigation states.
3. **Surface contract.** The platform’s hierarchy, containers, controls, system bars, window/scene route, and material policy.
4. **Input/evidence contract.** Supported input modes, accessibility actions, device requirements, and the exact proof needed for the claim.

The first two contracts can often be shared. The last two should be composed per target. A phone view and a Catalyst view may call the same `saveDraft()` use case while presenting it through different navigation, toolbar, keyboard, menu, selection, and window behavior. A watch or visionOS surface may need a different task slice entirely.

### Composition layers

| Layer | Shared question | Platform-specific decision |
| --- | --- | --- |
| Meaning | What does this result/action mean? | What is the smallest useful slice on the target? |
| Content | Which title, value, explanation, and next action matter? | What can be shown at a glance, in a split view, in a window, or in space? |
| Controls | Which semantic control expresses the action? | What is reachable by touch, pointer, keyboard, eyes/hands, crown, notification, or complication? |
| Navigation | What state comes next? | Stack, split, sheet, tab, menu, window, volume, immersive space, or shallow watch route? |
| Surface | What needs grouping and separation? | System bar, toolbar, tab, standard window, spatial material, or minimal watch surface? |
| Feedback | What should confirm, warn, or explain? | Visual, text, focus, VoiceOver, pointer, keyboard, haptic, audio, or spatial feedback? |

## Platform hierarchy cards

### iPhone: one focused task

Use a compact hierarchy that keeps the primary content and next action obvious. `NavigationStack`, a focused list/detail route, a sheet/editor, toolbar actions, and safe-area-aware bottom actions are common choices. Let the system handle keyboard avoidance and standard control behavior. Avoid turning every action into a floating glass pill; a native control in a native container often communicates more.

Proof questions:

- Can a person complete the primary outcome one-handed or with the expected touch path?
- Does the screen remain usable at the largest Dynamic Type sizes and with long localized text?
- Are loading, permission, empty, error, cancellation, and retry states reachable without gesture timing?
- Does VoiceOver expose the same meaning as the visual hierarchy?

### iPad: parallel context and mixed input

Use the larger canvas to keep related context visible when that shortens the task: a sidebar plus detail, an inspector, a persistent search/browse relationship, or a source-and-review composition. iPad users can combine touch, an attached keyboard or pointing device, Apple Pencil, and voice. The design should not make any one input mode the only way to discover an important action.

Proof questions:

- Does the layout adapt through split view, window resize, orientation, and multitasking conditions the app supports?
- Can a keyboard user reach the same actions, and does pointer hover/selection add clarity without replacing touch?
- Does Apple Pencil add useful precision rather than forcing a separate hidden interaction model?
- Are sidebars, list selection, focus, drag and drop, and menu/toolbar hierarchy coherent?

### Mac Catalyst: command, pointer, and window

Mac Catalyst is a Mac target built from the UIKit-based iPad app route, not a promise that iPad composition is a finished Mac experience. Give the window room to resize. Recheck text scale, table/list density, pointer precision, keyboard commands, menus, toolbar placement, selection, hover, tooltips, and destructive-action confirmation. Use `#if targetEnvironment(macCatalyst)` only for code that truly belongs to the Catalyst target, and use API availability checks for symbols that may vary by SDK/OS.

Proof questions:

- Can a person perform the primary task with mouse/trackpad and keyboard without reaching for touch assumptions?
- Are menus, keyboard shortcuts, selection, focus, and window resizing consistent with a Mac context?
- Does the selected Mac idiom and target deployment behave as intended?
- Have Catalyst-specific frameworks and APIs been verified in the Catalyst target rather than inferred from iPad?

### visionOS: spatial comfort and minimum immersion

Use standard windows for UI-centric work. Add volumes, 3D content, or an immersive space only when the task benefits from spatial context. People commonly look at an object and use an indirect gesture, but direct gestures, keyboard, pointer, VoiceOver, Switch Control, Dwell Control, and other accessibility routes matter too. Keep content in a comfortable field of view, avoid unnecessary motion, and provide a stationary frame of reference when motion is meaningful.

Proof questions:

- Is the spatial treatment necessary, or would a standard window solve the task more comfortably?
- Can the person complete the action through indirect interaction without reaching or moving excessively?
- Does the hierarchy remain legible when a window is moved, resized by the system, or viewed at a different distance?
- Have permissions, spatial input, comfort, safety, performance, and accessibility been tested on the named spatial target?

### watchOS: glance, act, and leave

Design for a wrist, not for a shrunken phone. Keep interactions brief and specialized. Prefer a glanceable result, a shallow hierarchy, vertical/crown-friendly content, a small number of essential actions, and system surfaces such as complications or notifications when they are the right route. A watch app may be used while the person is moving, and its Always On state changes what should remain visible.

Proof questions:

- Is the content understandable within a glance, and can the action finish in a few gestures?
- Does the Digital Crown provide useful scrolling or selection where appropriate?
- Is sensitive information handled correctly in Always On, notifications, and complications?
- Does the feature degrade honestly when the watch is offline, unpaired, permission-limited, or missing data?

## Input matrix before visual polish

Create an input matrix for every important action. This prevents a beautiful surface from becoming an inaccessible gesture puzzle.

| Action | Touch | Pointer/hover | Keyboard/focus | Pencil | Eyes/hands | Crown/watch route | Assistive alternative |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Open detail | Tap semantic `NavigationLink` or button | Click, hover/selection state | Focus + Return/Space/shortcut | Optional selection | Look + indirect activate | Tap/crown selection | VoiceOver action, Voice Control phrase, Switch Control |
| Commit draft | Labeled toolbar/button action | Click and pointer feedback | Focusable action + shortcut | Not required unless drawing | Indirect activate | Single clear action | Accessible action with validation result |
| Adjust value | Slider/picker/stepper | Precise pointer adjustment | Key increments/selection | Pencil precision if product-relevant | Direct/indirect control | Crown increments | Labeled adjustable control |
| Cancel/undo | Button/menu/gesture with visible alternative | Click/menu | Escape/shortcut where supported | Gesture alternative | Indirect action | Back/action button | Named accessibility action |
| Inspect live state | Semantic text/value/visual | Hover detail only as supplement | Focus reads value | Optional markup | Look/activate | Glanceable value | VoiceOver value and status announcement |

The exact APIs vary by target. The invariant is that important outcomes remain discoverable and understandable without color alone, haptic feedback alone, animation alone, hover alone, or a single gesture.

## Native system surfaces and Liquid Glass

Use a surface hierarchy rather than a universal glass component:

1. **System layer:** navigation bars, toolbars, tabs, sheets, menus, standard controls, windows, notifications, complications, and system-provided backgrounds. Prefer these first.
2. **Content layer:** the information, media, records, charts, and primary work. Keep it readable beneath or beside system surfaces.
3. **Functional glass layer:** a small group of related controls or a stateful interaction that benefits from separation, emphasis, or continuity. Give it a semantic container, spacing, labels, hit regions, and a fallback.
4. **Decorative layer:** only where it does not compete with content, accessibility, or system behavior. Decorative blur is not a substitute for hierarchy.

Glass decisions should change with the target. A floating iPhone control group, a Catalyst toolbar, a visionOS window, and a watchOS glance surface do not need the same material geometry. Keep the interaction and content meaning stable while allowing shape, placement, density, motion, hover, focus, and transparency to follow the platform.

Avoid:

- copying Apple’s app layouts, proprietary copy, icons, or brand marks;
- adding glass behind every card, list row, and label;
- hiding a semantic control behind a custom `onTapGesture`;
- placing a high-contrast text layer over dynamic glass without checking appearance and accessibility settings;
- using a glass animation as the only confirmation of a save, purchase, permission, or AI action;
- claiming “native” because a screenshot resembles an Apple product.

## State and transition choreography

The same feature state should have target-specific presentation but stable semantics. A reviewable AI result, for example, can map to:

| State | iPhone | iPad/Catalyst | visionOS | watchOS |
| --- | --- | --- | --- | --- |
| Capturing | Focused capture screen with visible cancel | Source and live preview panes | Window or spatial capture context with comfort boundary | Short capture action or handoff to iPhone |
| Proposal ready | Review sheet or detail route | Side-by-side proposal and source | Window/volume review with readable provenance | Summary and defer/open-on-phone action |
| Needs approval | One clear commit button | Persistent review action and keyboard path | Indirectly reachable approval with clear consequence | One short confirmation action |
| Failed/unavailable | Explanation, retry, alternate input | Error state kept alongside source/context | Fallback window or manual route | Concise explanation and handoff |

A platform-specific view should not silently change “draft” into “saved,” “permission denied” into “empty,” or “model unavailable” into “no result.” Keep those meanings in the feature-state contract.

When a scene backgrounds, a camera/audio/model route may pause, cancel, checkpoint, or continue through an appropriate system API. When a window resizes, the feature should adapt layout without losing draft state or focus unexpectedly. When a watch loses its phone, the app should show the actual sync/offline state rather than painting stale data as current.

## Design review checklist

### Before implementation

- Name the target and the primary user outcome.
- Choose the native container/control before choosing the material.
- Write the platform-specific input matrix.
- Identify the shared domain/state contract and the surface-specific route.
- Mark API availability, target conditionals, permissions, entitlements, and physical dependencies.

### During implementation

- Keep `#if` branches at the platform surface or adapter boundary.
- Use `ViewThatFits`, `AnyLayout`, size classes, Dynamic Type, and layout proposals for layout changes instead of device-name magic numbers.
- Keep system surfaces system-owned where possible.
- Give glass groups meaningful boundaries and reduced-effects fallbacks.
- Preserve accessible labels, values, traits, focus, and non-gesture actions.
- Keep scene lifecycle, capability lifecycle, and domain persistence as separate state machines.

### Before calling it native-ready

- Preview every meaningful state on representative target sizes.
- Run deterministic simulator/UI tests for navigation, focus, keyboard, cancellation, and state transitions.
- Test VoiceOver and relevant alternate input paths.
- Test actual iPhone/iPad/Catalyst/watchOS/visionOS targets named by the product claim.
- Record device/OS/build, input mode, accessibility settings, permissions, framework availability, and observed result.

## Sources

- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Designing for iPadOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ipados)
- [Designing for Mac Catalyst](https://developer.apple.com/design/human-interface-guidelines/mac-catalyst)
- [Designing for visionOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos)
- [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Pointing devices](https://developer.apple.com/design/human-interface-guidelines/pointing-devices)
- [Focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection)
- [Virtual keyboards](https://developer.apple.com/design/human-interface-guidelines/virtual-keyboards)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues)
- [Input and event modifiers](https://developer.apple.com/documentation/swiftui/view-input-and-events)
- [Scene](https://developer.apple.com/documentation/swiftui/scene)
- [ScenePhase](https://developer.apple.com/documentation/swiftui/scenephase)
- [Conditional compilation and availability conditions in Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/statements/)
