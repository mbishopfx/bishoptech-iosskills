# Blueprint: adaptive native glass composition

## Product outcome

Build one feature surface that keeps its state, actions, and accessibility intact while its arrangement adapts to compact width, regular width, Dynamic Type, keyboard, platform, safe area, and reduced effects.

## Route composition

    domain state -> semantic ActionModel
    -> layout policy (native stack/ViewThatFits/AnyLayout/Layout)
    -> native controls -> bounded functional glass group
    -> safe-area/system surface -> evidence

| Layer | Route | Ownership |
| --- | --- | --- |
| Domain | SwiftData/local source/service | Truth, freshness, draft, errors, cancellation |
| Semantic model | Sendable action/status projection | Labels, values, priority, enabled/unavailable state |
| Layout policy | HStack/VStack/Grid, ViewThatFits, AnyLayout, Layout | Measurement and arrangement only |
| Glass surface | System/custom Liquid Glass route | Visual grouping, contrast, fallback |
| Shell | NavigationStack, split view, toolbar, sheet, safeAreaInset | Navigation and safe areas |
| System projection | App Intent, widget, Live Activity, share/export | Bounded projection, not live layout |

## State model

Keep feature truth separate from layout mode:

    domain: idle | loading | partial | ready | stale | failed | canceled
    layout: regular | compact | large-text | reduced-effects | fallback
    handoff: none | presenting | canceled | completed | unavailable

Changing layout must not clear a draft, run a side effect, mark a record saved, or hide the only recovery action.

## Build order

1. Write the user task and the primary/secondary/overflow action model.
2. Build the regular composition with native containers and semantic controls.
3. Add a finite ViewThatFits fallback only when the task has a deliberate alternate form.
4. Use AnyLayout when the same child identity should move between horizontal and vertical arrangements.
5. Create a custom Layout only for a reusable geometry rule that built-ins cannot express.
6. Add a bounded glass group after the semantic control hierarchy works without effects.
7. Use toolbar, safeAreaInset, or safeAreaBar for edge ownership; avoid an unmeasured overlay.
8. Add Dynamic Type, RTL, keyboard, reduced-effects, unavailable, and source-stale fixtures.
9. Project the same domain state to widgets/App Intents/share only after the in-app route is truthful.

## Action-density pattern

Define three intentional arrangements:

    regular: labeled primary, secondary, status
    compact: labeled primary, overflow menu, status
    large text: primary action, menu, status below

Every branch must retain the primary outcome and explain unavailable or stale state. Use a menu or sheet for secondary actions rather than hiding them because a label no longer fits.

## Custom layout boundary

Use LayoutSubview measurements and proposals to arrange children. Keep the layout generic:

- it may read layout priority, spacing, dimensions, and custom layout values;
- it may use a cache when profiling justifies it;
- it may expose alignment/layout properties;
- it must not own model calls, persistence, navigation mutations, or permissions;
- it must not place controls outside the tested safe-area/hit-region contract.

For model-suggested density, accept only a typed enum or bounded value. Validate it before choosing a layout. Never allow AI to emit layout code, geometry constants, arbitrary resources, or action deletion.

## Liquid Glass contract

Use functional glass for a bounded action/status group, not as a full-screen substitute for hierarchy:

- standard SwiftUI controls remain the semantic owners;
- contrast and reduced-transparency routes remain available;
- the glass group is measured by the chosen layout;
- content is inset when the group sits at an edge;
- state text remains readable when effects are disabled;
- the group does not imply success, freshness, or AI availability by appearance alone.

## Fallback matrix

| Condition | Response |
| --- | --- |
| Compact proposal | ViewThatFits branch or AnyLayout vertical arrangement |
| Large Dynamic Type | Stack labels and controls; preserve primary action |
| Keyboard visible | Let safe-area/scroll behavior respond; keep focused field reachable |
| RTL | Verify semantic leading/trailing and reading order |
| Reduced transparency | Standard material/opaque background and same state |
| Reduce Motion | Static layout switch or restrained transition |
| Custom Layout unavailable/buggy | Built-in stack/grid with same action model |
| AI unavailable/invalid | Deterministic density policy |
| Source stale/partial | Preserve state label and recovery action in every branch |

## Target and resource register

Record selected deployment target, target membership, UIKit/extension host, image/font/color resources, Liquid Glass availability branch, app-extension/system-surface target, and test plan. Availability or compilation is not proof of physical glass/material rendering or system invocation.

## Proof plan

- fixture: zero/infinity/unspecified proposals, compact/regular widths, long strings, Dynamic Type, RTL, keyboard, source states, and layout transitions;
- compile: named iOS 26 app target, exact imports, availability branches, and resources;
- UI: branch selection, focus, editing, action reachability, safe area, cancellation, and recovery;
- accessibility: VoiceOver, Voice Control, Switch Control, keyboard, contrast, reduced transparency, Reduce Motion;
- physical device: touch/pointer/keyboard, glass/material rendering, thermal/memory/performance, safe areas, and haptics if used;
- release: signed resources, target membership, extension/system-surface configuration, and claim wording.

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
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
