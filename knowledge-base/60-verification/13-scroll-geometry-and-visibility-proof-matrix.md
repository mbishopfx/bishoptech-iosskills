# Scroll geometry, visibility, and position proof matrix

## Evidence boundary

Scroll behavior has separate proof layers. A list that renders in a preview does not prove stable position restoration, correct visibility policy, VoiceOver focus, keyboard input, or physical-device performance. A model request triggered by visibility does not prove user intent or content comprehension.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Stronger evidence | Failure to record |
| --- | --- | --- | --- |
| Content has stable identity | Unit test for IDs across insert, delete, reorder, and filter | Multi-step UI run with restoration after updates | Array indices or transient labels used as IDs |
| Position restores correctly | UI test for initial, identity, edge, and size-change behavior | Physical device after rotation, keyboard, Dynamic Type, and split view | Restore jumps to wrong item or loses focus |
| Programmatic scroll is intentional | Unit/UI test with named reason and target | Screen recording of search/selection/apply/restore routes | Background update silently moves the viewport |
| Geometry state is bounded | Unit test for Bool/enum/bucket projection | Instruments/signpost run during a long scroll | Raw offsets stored or broad view updates fire continuously |
| Visibility policy is correct | UI test for threshold enter/exit and stable IDs | Physical media/model resource cancellation and resume | Visibility is treated as read/approved/completed |
| Phase policy is correct | UI test for idle/interacting/decelerating/animating | Device run with touch, keyboard, pointer, and accessibility input | Phase changes hide or disable essential actions |
| Follow-bottom is correct | State tests for following/browsing/return | Device run while new output arrives after the user scrolls away | New content forces a jump or loses context |
| Lazy content is bounded | Unit/UI test for item/task limits | Memory and thermal run with realistic feed size | Lazy container assumed to make all work safe |
| Paging/view alignment is useful | UI fixture with variable item heights and long labels | Physical touch/pointer/keyboard/page-control run | Snap behavior clips or skips content |
| Scroll transition has parity | Renderer-on/off fixture and Reduce Motion test | Device run with VoiceOver/Look to Scroll where relevant | Visual effect is the only signal or breaks alternate input |
| Glass edge control is safe | Layout/accessibility fixture with safe-area inset | Physical device with keyboard, rotation, light/dark, reduced transparency | Floating bar covers content or focus |
| Indicators and edge effects communicate | UI review for scrollable affordance and control boundary | Device review across supported platforms | Hidden indicator and hidden content create ambiguity |
| Input routes work | UI tests for touch/keyboard/pointer where available | Physical device with VoiceOver, Switch Control, and platform input | scrollInputBehavior disables a needed route |
| AI proposal is source-bound | Unit tests for source ID/revision and stale transition | Screen recording of source edit during generation | Proposal applies to a different section |
| Visibility-triggered AI is bounded | Test debounce/cancel/cache and model-unavailable path | Device/network/privacy review with real workload | Flings trigger unbounded requests |
| Accessibility focus is stable | Accessibility audit and manual VoiceOver path | Physical device during insertion, jump, and new-content action | Focus is lost or moves without explanation |
| Right-to-left is correct | Arabic/Hebrew/mixed-direction UI fixture | Physical device with selection, restore, and section jumps | Leading/trailing or thresholds assume LTR |
| Performance is acceptable | Controlled XCTest/fixture with long text/feed | Instruments/signposts and thermal observation on device | Preview/simulator used as smoothness proof |
| Release target is correct | Archive target/configuration/entitlement check | TestFlight or production-like install and actual system state | Source sketch or debug run treated as release proof |

## Deterministic fixture pack

- empty, one-item, short, and long content;
- stable ID insertion, deletion, reorder, and filter;
- content smaller than container and content much larger than container;
- variable-height rows with long localized and generated text;
- top, middle, bottom, and exact-threshold positions;
- bottom streaming output while following and while browsing;
- user scroll during model generation;
- programmatic search jump and selection jump;
- visibility enter/exit at thresholds 0, 0.2, 0.5, 0.9, and 1.0;
- phase transitions from user interaction, deceleration, and animated scroll;
- page alignment with incomplete final page and variable item sizes;
- keyboard, pointer, VoiceOver, Switch Control, and reduced-effects settings;
- English, Arabic, Hebrew, mixed-direction, emoji, diacritics, and large Dynamic Type;
- light/dark color scheme, increased contrast, and standard/reduced transparency;
- model unavailable, canceled, stale, partial, and approved states;
- safe-area action bar, keyboard inset, rotation, split view, and compact width.

## Scroll geometry assertions

Prefer assertions on semantic projections:

    nearTop
    nearBottom
    visibleIDs
    currentID
    followMode
    phase
    pendingNewContent

Use raw bounds and offsets only as diagnostic evidence for a named geometry contract. Avoid snapshot assertions that encode a single device’s exact scroll offset when the product behavior is semantic.

## Device and release notes

Record OS/SDK, device model, locale, Dynamic Type, accessibility settings, color scheme, build, data fixture, and target. A simulator helps explore content and state transitions; it does not prove touch feel, physical scrolling, glass/edge material rendering, text rasterization, thermal behavior, camera/audio/media resources, or system-surface delivery.

## Sources

- [Scroll views](https://developer.apple.com/documentation/swiftui/scroll-views)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [ScrollGeometry](https://developer.apple.com/documentation/swiftui/scrollgeometry)
- [onScrollGeometryChange(for:of:action:)](https://developer.apple.com/documentation/swiftui/view/onscrollgeometrychange%28for%3Aof%3Aaction%3A%29/)
- [onScrollTargetVisibilityChange(idType:threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrolltargetvisibilitychange%28idtype%3Athreshold%3A_%3A%29)
- [onScrollVisibilityChange(threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrollvisibilitychange%28threshold%3A_%3A%29)
- [onScrollPhaseChange(_:)](https://developer.apple.com/documentation/swiftui/view/onscrollphasechange%28_%3A%29)
- [ScrollPhase](https://developer.apple.com/documentation/swiftui/scrollphase)
- [ScrollPhaseChangeContext](https://developer.apple.com/documentation/swiftui/scrollphasechangecontext)
- [ScrollTargetBehavior](https://developer.apple.com/documentation/swiftui/scrolltargetbehavior)
- [scrollTargetBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetbehavior%28_%3A%29)
- [scrollTransition(_:axis:transition:)](https://developer.apple.com/documentation/swiftui/view/scrolltransition%28_%3Aaxis%3Atransition%3A%29)
- [scrollInputBehavior(_:for:)](https://developer.apple.com/documentation/swiftui/view/scrollinputbehavior%28_%3Afor%3A%29)
- [ScrollInputBehavior](https://developer.apple.com/documentation/swiftui/scrollinputbehavior)
- [ScrollAnchorRole](https://developer.apple.com/documentation/swiftui/scrollanchorrole)
- [Human Interface Guidelines: Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Human Interface Guidelines: Right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left)
