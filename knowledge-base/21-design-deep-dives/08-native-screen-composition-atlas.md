# Native Screen Composition Atlas

## How to use this atlas

Choose a screen structure from the user’s task and information hierarchy. Then assign each region to a native container, state model, content layer, or functional/system layer. Do not begin with a screenshot or a glass effect; begin with the action the person needs to complete.

`task -> hierarchy -> container -> state -> native controls -> adaptation -> material/motion -> proof`

## Composition matrix

| User task | First SwiftUI route | Functional layer | Common failure |
| --- | --- | --- | --- |
| Move among a few top-level areas | `TabView` with stable `Tab` identity | System tab bar, optional bottom accessory | Using tabs for actions or hiding them unpredictably |
| Browse a collection and inspect one item | `NavigationSplitView` on regular width; `NavigationStack` on compact width | Sidebar/list/detail navigation and toolbar | Duplicating selection state or forcing a desktop sidebar into portrait iPhone |
| Read one rich item and act on it | `ScrollView`/`List` inside `NavigationStack` | Toolbar actions and contextual menus | Covering content with a custom floating card/toolbar |
| Create or edit focused content | `.sheet` or navigation destination with `Form`/editor | Save/cancel toolbar, keyboard/focus, validation state | Treating draft text as saved domain truth |
| Monitor a live session | A state-driven shell with a clear status region | Toolbar/control group, optional ActivityKit projection | Making the animation or Live Activity the canonical state |
| Review AI/capture output | Source + editable review form + explicit commit | Confirmation toolbar/sheet | Applying generated output directly to a consequential record |
| Show a compact action cluster over content | Native toolbar/safe-area inset first; small `GlassEffectContainer` if needed | Related semantic buttons/status | Applying glass to the whole content layer |

## Three-layer screen recipe

### 1. Content layer

Place the primary information and user work here. Use semantic typography, native list/form behavior, standard materials where differentiation is needed, and explicit loading/empty/error/permission states. Let content extend beneath a system bar when the platform route supports it, but keep text and controls legible as it scrolls.

### 2. Functional layer

Place navigation and actions in `TabView`, toolbars, sidebars, safe-area bars, menus, or a small related glass group. Controls should have predictable placement and remain discoverable. A functional layer may float above content; it should not compete with the content’s meaning.

### 3. System layer

Use system-owned sheets, alerts, share sheets, widgets, Live Activities, notifications, App Intents, and document/photo pickers. Configure the system surface and validate its route instead of rebuilding the surface with app-owned pixels.

## State before styling

Every screen should be able to render at least:

`loading -> empty -> content -> editing -> saving -> saved -> failed -> permissionDenied -> unavailable`

Add domain-specific states such as `stale`, `offline`, `partiallyLoaded`, `modelNotReady`, `captureInterrupted`, `syncConflict`, or `exporting`. Keep these values distinct:

- view presentation state;
- draft/edit state;
- persisted domain truth;
- external service/system state;
- generated/model proposal;
- operation/progress state.

If styling changes when a state changes, ensure the label/value/action also changes. A color, blur, morph, or icon alone is not a sufficient state explanation.

## Adaptation matrix

| Dimension | Required response |
| --- | --- |
| Compact width | Keep the primary path one-handed and navigable; use a stack or tab bar rather than a forced sidebar. |
| Regular width/iPad | Consider split navigation, an inspector, or a sidebar when it keeps related information visible; allow the user to understand selection. |
| Dynamic Type | Reflow, wrap, or substitute composition; do not merely clip or permanently cap text size. |
| Long localization/RTL | Expand labels, mirror directional layout, and test toolbar/menu crowding. |
| Reduced transparency | Use opaque/standard-material alternatives and preserve hierarchy. |
| Reduced motion | Remove nonessential morphing/scale/parallax; preserve state and focus. |
| VoiceOver/alternate input | Preserve semantic controls, labels, values, traits, focus order, and non-gesture paths. |
| Keyboard/pointer/controller | Keep focusable controls and hover/selection feedback meaningful where supported. |
| System surface | Redact private content, support stale/unavailable state, and avoid assuming the app process is alive. |

## Screen blueprints

### Dashboard

Use a clear title, one primary next action, grouped status, and recent/secondary content. Use `LazyVStack`/`List` based on interaction needs. A glass group can contain the primary action/status if it floats above scrolling content; use standard materials inside the content layer. The dashboard should still communicate progress with text and semantic values when motion or transparency is reduced.

### Detail/inspector

Make the primary object and its provenance/source visible. Use a toolbar for actions and a sheet or navigation destination for focused edits. If a matched transition is useful, match a real object identity to a detail destination and keep the destination usable when the transition is unavailable.

### Form/editor

Model `draft`, validation, save progress, conflict, saved, and cancel/discard explicitly. Use `Form`, `TextField`, `TextEditor`, `Picker`, `Toggle`, and native keyboard/focus behavior. Keep a persistent action bar in the safe area only if it adds value; avoid a manually positioned overlay that covers fields or the keyboard.

### Search/browse

Use `searchable` with a semantic search role and stable navigation destinations. Keep empty query, no results, loading, error, offline, and stale index states distinct. Do not put search actions in a tab bar whose job is navigation unless the search tab is genuinely a top-level destination.

### Live/session screen

Show the current operation, elapsed/progress state, pause/stop actions, and interruption/error state. Use a separate service/actor for capture or model work. A Live Activity or widget is a compact projection; it does not replace the in-app session state or physical-device proof.

## Proof plan

- Previews: all state cases, injected fixtures, width/height categories, Dynamic Type, appearance, reduced motion/transparency, and representative localization.
- Simulator: navigation/deep links, keyboard/pointer, permission branches with fakes, system-layout routes where supported, and deterministic UI tests.
- Physical device: touch/gesture ergonomics, material legibility, haptics, VoiceOver/Voice Control/Switch Control, device-family differences, thermal/performance, camera/audio/sensor routes, and system-owned surfaces.
- Signed/release: target membership, entitlements, privacy resources, extensions, widgets/App Intents/ActivityKit, TestFlight metadata, and production/server/account state.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Human Interface Guidelines: Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Human Interface Guidelines: Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars)
- [Human Interface Guidelines: Sidebars](https://developer.apple.com/design/human-interface-guidelines/sidebars)
- [Human Interface Guidelines: Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Navigation](https://developer.apple.com/documentation/swiftui/navigation)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [NavigationSplitView](https://developer.apple.com/documentation/swiftui/navigationsplitview)
- [TabView](https://developer.apple.com/documentation/swiftui/tabview)
- [Toolbars](https://developer.apple.com/documentation/swiftui/toolbars)
- [Presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [Layout adjustments](https://developer.apple.com/documentation/swiftui/layout-adjustments)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
