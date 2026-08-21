# Scroll geometry, position, visibility, and phase

## Purpose

SwiftUI’s scroll APIs let a feature express reading position, visible content, programmatic navigation, page alignment, input policy, and scroll-driven effects without treating the scroll view as a bag of pixels.

Use the route:

    semantic content identity
    -> ScrollView/List/TextEditor
    -> scroll target layout
    -> ScrollPosition or id binding
    -> geometry/visibility/phase observation
    -> bounded UI state or explicit user action
    -> accessibility, input, performance, and device proof

The design rule is simple: observe or control scrolling to help people keep context. Do not use every offset change as a general-purpose application event bus.

## Route chooser

| Need | Preferred route | Boundary |
| --- | --- | --- |
| Show long content | ScrollView with a lazy layout, List, or TextEditor | Choose the container from content semantics, editing, and platform behavior |
| Jump to a known item | ScrollPosition with stable identity or ScrollViewReader | Keep IDs stable and verify the target exists |
| Remember/observe the current item | ScrollPosition view identity or an id binding | Treat the value as position state, not an approved domain change |
| Detect a header threshold | onScrollGeometryChange with a small Equatable projection | Do not store raw geometry on every frame |
| Know which targets are visible | onScrollTargetVisibilityChange | Use visibility to bound work, not to imply reading completion |
| Start/stop item work | onScrollVisibilityChange | Cancel or pause work when hidden and retain a fallback |
| React to user scroll versus programmatic motion | onScrollPhaseChange and ScrollPhase | Do not hide controls or change meaning without a non-motion route |
| Page or snap | scrollTargetLayout plus paging/view-aligned behavior | Test Dynamic Type, variable item heights, and accessibility input |
| Animate appearance while entering the viewport | scrollTransition | Keep effects restrained and remove or reduce them for accessibility |

## ScrollView is a semantic container

SwiftUI’s ScrollView displays content that does not fit in the current display. Lazy stacks load views as they become visible or nearly visible, while regular stacks and grids load their content at once. Lists and tables already contain scrolling.

Choose the container from the task:

- use List for row-oriented, scan-heavy, system-like content and its built-in behaviors;
- use ScrollView with a lazy stack for editorial, detail, review, or composed content;
- use TextEditor for editable text and selection;
- use a horizontal scroll view inside a vertical one only when the axes are intentionally different;
- avoid nesting scroll views with the same orientation because gesture and layout behavior can become unpredictable;
- expose scrollability through partial content, hierarchy, indicators, or a clear page control rather than assuming a hidden indicator is enough.

## ScrollPosition is semantic position

ScrollPosition describes where a scroll view is scrolled within its content. With a scroll target layout and stable IDs, it can:

- scroll to a view by identity;
- scroll to an edge;
- scroll to a concrete point or coordinate;
- expose the current positioned view identity;
- indicate whether the user has positioned the scroll view;
- preserve a semantic position when content or container size changes.

Prefer identity-based position for records, messages, chapters, and review sections. Use offsets for genuinely geometric documents or bounded canvas-like content. An offset is not a durable record identifier and should not be sent to a model as if it were semantic content.

When the content changes, decide whether the product should preserve:

    current item identity
    current edge
    approximate reading location
    explicit user choice

Do not automatically snap to the bottom merely because new AI text arrived. If the person has scrolled away from the bottom, preserve their position and show a “new content” action or badge.

## ScrollGeometry should be projected

ScrollGeometry describes bounds, container size, content insets, content offset, content size, and the visible rectangle. SwiftUI supplies it to onScrollGeometryChange and onScrollPhaseChange.

Use onScrollGeometryChange to transform the geometry into a small Equatable value:

    raw geometry
    -> isPastHeader: Bool
    -> nearBottom: Bool
    -> visibleSection: Section.ID?
    -> bounded progress bucket

The transform should be cheap and the action should update only the state that depends on that projection. Apple’s documentation warns that scroll geometry changes frequently and that large parts of the app should not update on every change.

Do not:

- persist every content offset;
- call a model, network, database, or navigation mutation for each geometry event;
- make layout feed back into geometry state without a finite guard;
- assume visibleRect coordinates are stable across safe areas, rotation, split views, or Dynamic Type;
- use a scroll threshold as proof that a person read or agreed to content.

## Visibility is not comprehension

onScrollVisibilityChange reports when a view crosses a visibility threshold. onScrollTargetVisibilityChange reports the IDs of target views considered visible. These are useful for:

- starting or pausing preview playback;
- prefetching bounded local resources;
- deciding which section can receive a contextual affordance;
- showing “new results” or a chapter marker;
- reducing work outside the viewport.

Visibility is an observation, not a guarantee that the person saw, understood, or accepted the content. Never mark a record read, approved, consented, or completed solely because it crossed a threshold. If product semantics require completion, define an explicit action or a clearly documented reading contract with its own accessibility route.

Use stable, app-owned IDs. Do not use array indices as identity when content can be inserted, reordered, or filtered.

## Scroll phases and user intent

ScrollPhase describes scrolling such as idle, panning, decelerating, and animating. onScrollPhaseChange can provide the phase transition and, in its context form, geometry and velocity at the transition.

Use phase state for bounded interaction policy:

- defer expensive nonessential work until deceleration or idle;
- distinguish a user gesture from a programmatic jump;
- decide when a “return to current” control should appear;
- coordinate a restrained toolbar collapse with the direction of an interaction;
- stop a page-level animation while the person is actively manipulating content.

Do not use phase changes to permanently hide a primary action, disable accessibility navigation, or create a motion-only route. A user can scroll with touch, pointer, keyboard, VoiceOver, Switch Control, or platform-specific input; test all supported routes.

## Targets, paging, and transitions

scrollTargetLayout marks the outermost layout that contains scroll targets. scrollTargetBehavior lets the scroll view settle using built-in paging/view-aligned behavior or a custom ScrollTargetBehavior.

Use paging when the content has meaningful page-sized units. Use view-aligned behavior for cards or items that should settle predictably. A custom behavior should express a bounded geometry rule, not a model-defined arbitrary snap or a hidden action trigger.

scrollTransition applies a visual effect as a view enters or leaves the visible region. It is appropriate for restrained scale, opacity, or depth cues when the content remains understandable without the effect. It is not appropriate for:

- conveying approval, authorization, or safety;
- hiding text until an item is centered;
- requiring a person to discover an action through animation;
- parallax that breaks Look to Scroll or other accessibility input;
- per-frame work that makes long feeds expensive.

## Default anchors and content changes

defaultScrollAnchor can control the initial position, size-change behavior, and alignment of content smaller than its container through ScrollAnchorRole. Treat these as separate product decisions:

- initialOffset: where the screen begins;
- sizeChanges: how insertion, rotation, keyboard, or Dynamic Type changes preserve context;
- alignment: how short content sits inside a larger container.

For a chat or streaming AI output, a bottom anchor is useful only while the person is intentionally following the bottom. A review screen should preserve the current item when a model status banner or source metadata changes.

## Input policy

scrollInputBehavior can enable or disable scrolling for a particular ScrollInputKind without disabling all scrolling. Use it only when a specific input conflict is real and documented. Do not disable touch, keyboard, pointer, VoiceOver, or platform-specific scrolling to compensate for an unmeasured overlay.

Support default gestures and keyboard shortcuts. If you use page-by-page scrolling, provide a clear page indicator or other context and avoid redundant indicators on the same axis.

## Long AI output route

For generated or transcribed content:

    source revision
    -> bounded output stream
    -> stable section IDs
    -> incremental approved/display draft
    -> user scroll position
    -> follow-bottom policy
    -> explicit new-content/review action

Keep a follow mode:

    followingBottom
    userBrowsing
    programmaticJump
    stalePosition
    unavailable

When followingBottom is true, a new chunk may keep the bottom visible. When the person scrolls up, change to userBrowsing and stop automatic scrolling. When a new chunk arrives, show a compact accessible affordance to return to the bottom. Do not reset position when a renderer, source span, or status label changes.

## Liquid Glass and scroll edges

Apple’s Human Interface Guidelines describe the scroll view itself as having no appearance, with indicators providing feedback, and recommend scroll edge effects when a scroll view meets floating interface elements. Treat an edge effect as a transition between content and a control area, not as a decorative overlay.

For a native glass shell:

- keep the scroll content measured under the screen’s safe-area ownership;
- use a toolbar, safeAreaInset, or system edge composition for floating actions;
- avoid covering the last paragraph or focused editor line;
- use one consistent edge treatment per view;
- keep text and controls legible when the material or edge effect is unavailable;
- avoid a full-screen glass layer that makes scroll position and hierarchy harder to understand.

## Accessibility and adaptation

- preserve standard scrolling gestures and keyboard input;
- test VoiceOver focus as content appears, changes, and is programmatically scrolled;
- keep automatic scrolling minimal and contextual;
- provide a non-motion way to reach new content or return to a section;
- test Dynamic Type, right-to-left layout, split view, rotation, and keyboard;
- avoid same-axis nested scrolling;
- keep indicators, page controls, and edge effects from competing for the same meaning;
- test reduced motion, reduced transparency, increased contrast, and pointer/keyboard input;
- ensure any scroll-driven control state has a semantic label and stable focus order.

## Performance and lifecycle

Bound the number of observed IDs, visible resources, and in-flight tasks. Visibility-triggered work must be cancellable and must have a deterministic unavailable/error state. Lazy containers reduce initial work but do not make model, image, audio, or network tasks safe by themselves.

Keep geometry transforms pure and cheap. Use signposts or controlled performance tests for long content, frequent updates, and programmatic scrolls. Do not claim smoothness from a preview or simulator alone.

## Target and proof register

Record the deployment target, SDK, target membership, content container, stable ID type, scroll target layout, position route, input routes, edge/material route, keyboard behavior, accessibility settings, and fixture IDs. Verify the actual device for touch/pointer/keyboard feel, focus behavior, glass/edge rendering, memory, and thermal behavior where the product depends on them.

## Sources

- [Scroll views](https://developer.apple.com/documentation/swiftui/scroll-views)
- [ScrollView](https://developer.apple.com/documentation/swiftui/scrollview)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [scrollPosition(_:anchor:)](https://developer.apple.com/documentation/swiftui/view/scrollposition%28_%3Aanchor%3A%29)
- [scrollPosition(id:anchor:)](https://developer.apple.com/documentation/swiftui/view/scrollposition%28id%3Aanchor%3A%29)
- [ScrollGeometry](https://developer.apple.com/documentation/swiftui/scrollgeometry)
- [onScrollGeometryChange(for:of:action:)](https://developer.apple.com/documentation/swiftui/view/onscrollgeometrychange%28for%3Aof%3Aaction%3A%29/)
- [onScrollVisibilityChange(threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrollvisibilitychange%28threshold%3A_%3A%29)
- [onScrollPhaseChange(_:)](https://developer.apple.com/documentation/swiftui/view/onscrollphasechange%28_%3A%29)
- [ScrollPhase](https://developer.apple.com/documentation/swiftui/scrollphase)
- [ScrollPhaseChangeContext](https://developer.apple.com/documentation/swiftui/scrollphasechangecontext)
- [scrollTargetBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetbehavior%28_%3A%29)
- [ScrollTargetBehavior](https://developer.apple.com/documentation/swiftui/scrolltargetbehavior)
- [scrollTransition(_:axis:transition:)](https://developer.apple.com/documentation/swiftui/view/scrolltransition%28_%3Aaxis%3Atransition%3A%29)
- [scrollInputBehavior(_:for:)](https://developer.apple.com/documentation/swiftui/view/scrollinputbehavior%28_%3Afor%3A%29)
- [ScrollInputBehavior](https://developer.apple.com/documentation/swiftui/scrollinputbehavior)
- [defaultScrollAnchor(_:for:)](https://developer.apple.com/documentation/swiftui/view/defaultscrollanchor%28_%3Afor%3A%29)
- [ScrollAnchorRole](https://developer.apple.com/documentation/swiftui/scrollanchorrole)
- [Human Interface Guidelines: Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views)
- [Human Interface Guidelines: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Human Interface Guidelines: Right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left)
