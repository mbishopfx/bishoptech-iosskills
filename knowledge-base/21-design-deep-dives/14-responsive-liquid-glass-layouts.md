# Responsive Liquid Glass layouts

## Design goal

Create Apple-native screens whose hierarchy remains coherent when width, height, Dynamic Type, keyboard, language, input method, safe area, or platform changes. Liquid Glass can emphasize a functional group, but it must not become a fixed overlay that only works at one phone width.

## Composition contract

    domain state -> semantic actions/status -> layout strategy
    -> native controls -> functional glass treatment
    -> safe-area/system surface -> accessibility and proof

Each layer has one job:

| Layer | Owns | Does not own |
| --- | --- | --- |
| Domain | truth, freshness, validation, side effects | pixels or geometry |
| Semantic projection | labels, units, action priority, state explanation | device width |
| Layout | measurement, arrangement, spacing, placement | domain mutations or hidden actions |
| Glass group | visual grouping and system treatment | navigation, safe-area math, accessibility text |
| Screen shell | navigation, tabs, toolbar, sheets, safe areas | arbitrary child sizing |
| System surface | widget/Live Activity/App Intent projection | the live app layout |

## Choose the smallest layout tool

| Situation | Route | Liquid Glass implication |
| --- | --- | --- |
| Ordinary vertical/horizontal hierarchy | VStack/HStack/ZStack | Let system spacing and controls establish the baseline |
| A few meaningful alternatives | ViewThatFits | Preserve the same action/status outcome in every branch |
| Same children, horizontal/vertical choice | AnyLayout | Preserve focus and identity while changing arrangement |
| Reusable geometry algorithm | Layout | Keep semantic controls outside the geometry algorithm |
| Cards/pages relative to container | containerRelativeFrame | Avoid device-name breakpoints and screen-width magic |
| Real coordinate-space measurement | GeometryReader/anchors | Use only for geometry that cannot be expressed declaratively |
| Edge action/status group | toolbar/safeAreaInset/safeAreaBar | Reserve content space; do not cover scroll content |

Begin with the native container. Add custom Layout only after a failing or awkward relationship is described in the design brief.

## Action density route

For a glass action group, model actions by semantic priority:

    primary action
    secondary reversible action
    overflow action
    status/freshness label

Then define deliberate forms:

    regular width -> labeled primary + secondary + status
    compact width -> labeled primary + overflow menu
    large text -> primary button + menu + status below
    unavailable -> disabled/alternative action with explanation

ViewThatFits is useful when these are finite, designed alternatives. AnyLayout is useful when the same children can move between horizontal and vertical arrangement. A custom Layout is useful when the group has a reusable measurement rule such as equal-width actions or a bounded priority-based row.

Do not remove the only action because its label is long. Move secondary actions into a menu, sheet, or detail route and keep the primary outcome discoverable.

## Glass and safe areas

The screen shell should own the edge relationship:

    ScrollView
      -> content and bottom safe-area response
      -> safeAreaInset or native toolbar
      -> bounded glass control/status group

The group needs:

- a semantic label and individual control labels;
- a measured hit region;
- readable contrast in light/dark and increased contrast;
- a reduced-transparency fallback;
- a keyboard-aware position;
- a focus path for VoiceOver, Voice Control, Switch Control, and keyboard;
- an explicit unavailable/loading/error state.

Use the system’s toolbar or bar when it already expresses the relationship. Use safeAreaInset when a custom edge group genuinely needs to reserve space. Test scroll indicators, content margins, keyboard appearance, rotation, split view, and interactive dismissal.

## Content, proposal, and state

Layout proposals can change without a domain state change. Keep the action model and source snapshot stable while the projection changes:

    ActionModel
      -> regular ActionGroup
      -> compact ActionGroup
      -> large-text ActionGroup
      -> unavailable ActionGroup

The same IDs should represent the same actions. This keeps focus, editing, cancellation, and analytics meaningful when the layout changes. Do not let a measurement pass trigger a save, model call, network request, or haptic.

For a custom Layout:

- measure with zero/infinity/unspecified deliberately;
- treat nil proposal dimensions as unspecified;
- use LayoutSubview dimensions, spacing, priority, and custom layout values;
- return a container size that can contain the placements;
- cache only when profiling shows repeated calculation matters;
- make directional assumptions explicit and test RTL.

## Platform and size adaptation

Avoid treating iPhone, iPad, Mac Catalyst, and visionOS as screen widths. Platform changes may alter input, windowing, safe areas, system bars, focus, hover, keyboard, and system surfaces. Use environment values, size classes, container-relative sizing, system navigation, and deliberate alternatives.

Examples:

- a compact iPhone action group may use one primary button and a menu;
- an iPad regular-width group may show labeled controls beside a detail pane;
- Mac Catalyst may need pointer/keyboard emphasis and different menu placement;
- visionOS may need a different spatial container rather than a 2D glass overlay;
- watchOS should use a focused native route rather than shrinking the iPhone composition.

Share the semantic route and state model, not an assumption that the same geometry belongs on every platform.

## AI-bounded layout suggestions

On-device AI may suggest density, action ordering, or a semantic presentation mode. It must return a typed proposal:

    density: compact | standard | spacious
    actionMode: full | overflow | primaryOnly
    emphasis: normal | high

Validate against allowlists, accessibility, current source state, target platform, and user preferences. The model must not emit arbitrary Layout code, geometry constants, view identity, shader source, or hidden action removal. If the model is unavailable or invalid, use the deterministic layout policy.

## Accessibility and visual hierarchy

Every layout branch must preserve:

- the same task outcome;
- the current state and freshness;
- labels, values, traits, and actions;
- a logical reading/focus order;
- large text and localization capacity;
- reduced-motion and reduced-transparency meaning.

Use a custom drawn surface only for visual detail that has a semantic alternative. A glass group should emphasize hierarchy, not make low-contrast text or tiny controls appear premium.

## State and recovery

    evaluating proposal
      -> regular
      -> compact
      -> large-text
      -> reduced-effects
      -> unavailable/fallback

The layout mode is a projection. Domain state remains separate:

    idle | loading | partial | ready | stale | failed | canceled

When the layout changes, preserve the source revision, pending draft, user intent, and recovery action. If a glass effect or custom layout cannot run, fall back to native stacks and plain materials without losing the task.

## Verification

Use fixtures for proposals, width/height, Dynamic Type, long localization, RTL, keyboard, safe-area changes, inserted/removed actions, source staleness, and model-unavailable state. Use UI tests for branch selection and complete tasks. Use physical devices for touch, pointer, keyboard, haptics, safe areas, glass/material rendering, performance, and accessibility interaction. Inspect signed targets/resources when extensions or system surfaces consume the projection.

## Sources

- [Layout](https://developer.apple.com/documentation/swiftui/layout)
- [ProposedViewSize](https://developer.apple.com/documentation/swiftui/proposedviewsize)
- [LayoutSubview](https://developer.apple.com/documentation/swiftui/layoutsubview)
- [LayoutValueKey](https://developer.apple.com/documentation/swiftui/layoutvaluekey)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [GeometryReader](https://developer.apple.com/documentation/swiftui/geometryreader)
- [containerRelativeFrame(_:alignment:_:)](https://developer.apple.com/documentation/swiftui/view/containerrelativeframe%28_%3Aalignment%3A_%3A%29)
- [safeAreaInset(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [SafeAreaRegions](https://developer.apple.com/documentation/swiftui/safearearegions)
- [Layout adjustments](https://developer.apple.com/documentation/swiftui/layout-adjustments)
- [Composing custom layouts with SwiftUI](https://developer.apple.com/documentation/swiftui/composing-custom-layouts-with-swiftui)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues)
