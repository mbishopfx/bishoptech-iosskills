# Platform Adaptation and Conditional Composition

## User outcome

Use this route when the same product idea needs to feel native on iPhone, iPad, Mac Catalyst, visionOS, or watchOS. Share the domain model, feature rules, validation, persistence contracts, and evidence model where that is useful. Split the presentation, input, scene, system-surface, and device-capability routes where the platform changes the task.

“One codebase” and “one interface” are different goals. A shared SwiftUI view can reduce duplication, but it cannot prove that a touch-first iPhone layout is an effective iPad workspace, a Catalyst Mac window, a spatial visionOS window, or a glanceable watchOS task. Treat each target as a named product surface with an explicit proof plan.

## Three kinds of conditions

Conditional compilation, API availability, and runtime capability are related but not interchangeable.

| Question | Mechanism | What it answers | What it does not answer |
| --- | --- | --- | --- |
| Should this source be compiled for this platform or build environment? | `#if os(...)`, `#if targetEnvironment(...)`, `#if canImport(...)`, custom Swift compilation condition | Whether the compiler includes a branch or module reference | Whether a device has the hardware, permission, account, entitlement, or service needed at runtime |
| Can the selected OS execute this API? | `@available`, `if #available`, `#unavailable` | Whether an API is available for the running OS version | Whether the person granted permission or whether the capability is useful on this device |
| Can this installation perform the feature now? | A feature/capability adapter that checks hardware, permission, account, service, asset, entitlement, and current state | Whether the user can start the route and what fallback is honest | Whether the code compiles for every other target or whether the UI is well adapted |

Swift’s compiler conditions are evaluated at compile time. Apple’s availability conditions are evaluated at runtime and also let the compiler verify guarded API usage. Keep both visible instead of hiding all differences behind a boolean called `isSupported`.

### Conditional composition shape

~~~swift
import SwiftUI

struct FeatureRoot: View {
    var body: some View {
        platformSurface
    }

    @ViewBuilder
    private var platformSurface: some View {
        #if os(watchOS)
        WatchFeatureSurface()
        #elseif os(visionOS)
        SpatialFeatureSurface()
        #elseif os(iOS)
        #if targetEnvironment(macCatalyst)
        CatalystFeatureSurface()
        #else
        PhonePadFeatureSurface()
        #endif
        #else
        UnsupportedPlatformSurface()
        #endif
    }
}
~~~

This pattern selects a presentation surface. It should not select a different definition of the domain’s meaning. Keep platform-specific views close to the feature boundary, and keep the shared model free of UIKit, watchOS-only, or visionOS-only types unless the shared module is deliberately target-scoped.

Do not use a compile-time branch to pretend a feature is available. The selected surface still needs a runtime capability state such as `unavailable`, `needsPermission`, `needsAsset`, `requiresPairedDevice`, `requiresEntitlement`, `ready`, or `failed(reason:)`.

## Layout adaptation is more than device names

Use the environment and layout proposal as inputs to composition:

- `horizontalSizeClass` and `verticalSizeClass` describe the current environment, not a permanent device identity.
- `dynamicTypeSize`, `layoutDirection`, `colorScheme`, contrast, reduced motion, and reduced transparency can change the useful composition without changing the platform.
- `ViewThatFits` evaluates children in the order supplied and chooses the first child that fits the constrained axes. Put the preferred composition first, and make each candidate preserve the same meaning and important actions.
- `AnyLayout` can change the layout container without destroying the state of the subviews. Use it when the relationship is the same but the arrangement changes.
- A custom `Layout` is appropriate for a real reusable geometry rule, not as a collection of magic breakpoints.
- `NavigationStack`, `NavigationSplitView`, sheets, tabs, inspectors, and toolbars express different information and task hierarchies. Do not simulate one with a pile of conditional padding and glass cards.

The minimum useful composition should survive long strings, largest supported text sizes, right-to-left layout, empty/loading/error states, keyboard appearance, pointer hover, and a resized window. A width check can decide how to arrange content; it should not silently remove an essential action.

### Adaptation route table

| Change in context | Prefer | Avoid |
| --- | --- | --- |
| Compact width or one-handed task | `NavigationStack`, focused content, a short toolbar, sheet/editor route | Shrinking a dense iPad layout until labels truncate |
| Regular width with list/detail relationship | `NavigationSplitView`, sidebar, inspector, or persistent detail | A fake sidebar made from a horizontal stack that ignores selection and keyboard focus |
| A control group no longer fits | `ViewThatFits`, a menu, a toolbar item, or a deliberate alternate group | Clipping or hiding the primary action |
| Same content relationship, different arrangement | `AnyLayout` or a small custom `Layout` | Rebuilding the view identity with unrelated trees and losing draft/focus state |
| Large Dynamic Type | Text styles, scalable metrics, scrollable content, flexible stacks | Fixed heights, fixed font sizes, and text that is only visible in a screenshot |
| Keyboard or pointer present | Semantic controls, focus, keyboard shortcuts, hover/selection feedback | A touch-only gesture with no focused or accessible route |
| Spatial window or immersive context | Standard windows for UI-centric work; spatial frameworks for spatial work | Treating a 2D iPhone card layout as a spatial design system |
| Watch-sized glance | One essential result, shallow navigation, crown-friendly vertical content | Porting a multi-column phone dashboard |

## Scene and lifecycle boundaries

SwiftUI’s `Scene` describes an app’s user-facing scene structure. `WindowGroup` can create multiple scene instances on platforms that support them, and the system decides how a scene’s view hierarchy is presented in a platform-appropriate way. A scene declaration is therefore not a promise of one window, one process, one size, or one lifecycle callback.

Use `scenePhase` for scene operational state. Read it at the level whose meaning you need:

- A view observes the phase of the scene that contains it.
- An `App` or scene-level observer sees an aggregate across the app’s scenes; with a `WindowGroup`, another scene can remain active while a different window is backgrounded.
- Background is an opportunity to stop or reduce work and persist a safe draft, not a guarantee of unlimited cleanup time. Release camera/session resources promptly and use the appropriate background API for work that must be scheduled or continued.

Keep scene lifecycle separate from feature lifecycle. A feature coordinator should own the state machine for camera, audio, model sessions, live capture, or network work. The scene can send `becameActive`, `resignedActive`, and `enteredBackground` intents to that coordinator. The coordinator decides whether to pause, cancel, checkpoint, or resume based on the capability’s contract.

### App delegate and scene delegate seams

`UIApplicationDelegateAdaptor` is an escape hatch for a SwiftUI `App` that still needs UIKit app-delegate callbacks. Apple’s guidance is to prefer SwiftUI lifecycle tools such as `scenePhase` when they express the need. Declare the adaptor once in the `App` declaration; keep push registration, launch handoff, or a narrow integration callback there rather than turning the app delegate into a global feature store.

If a specific iOS scene callback is required, a `UIWindowSceneDelegate` can be supplied through the app delegate’s scene configuration. Document why that callback is not represented by a scene or view modifier, and keep the delegate’s output typed and routed to the feature coordinator.

## Platform composition matrix

| Target | Primary interaction and shape | Native composition routes | Explicit adaptation | Proof that is required |
| --- | --- | --- | --- | --- |
| iPhone / iOS | Touch, voice, compact or changing width, short focused paths | `NavigationStack`, tabs, sheets, lists/forms, toolbars, safe-area actions | One-handed reach, keyboard avoidance, rotation, Dynamic Type, VoiceOver, reduced effects | iPhone simulator for deterministic UI plus physical iPhone for touch, safe areas, real capability, accessibility, performance, and haptics where used |
| iPad / iPadOS | Touch plus keyboard, pointer, Apple Pencil, multitasking, larger canvas | `NavigationSplitView`, sidebars, inspectors, menus, drag and drop, multiwindow | Split view, Stage Manager/window resize where supported, pointer hover, focus groups, keyboard shortcuts, Pencil route | iPad simulator/window configurations plus physical iPad with keyboard/pointer/Pencil paths that the app claims to support |
| Mac Catalyst | Resizable Mac window, keyboard, mouse/trackpad, menus, pointer | UIKit/Catalyst target, toolbar/menu integration, keyboard commands, window-aware layout | Mac idiom choice, pointer precision, menu hierarchy, hover/tooltips, window size, Catalyst-only APIs | Run the Mac Catalyst target on a Mac; verify menus, keyboard, pointer, resize, persistence, and Catalyst availability separately from iPad |
| visionOS | Eyes, indirect/direct hand gestures, spatial windows, volumes, immersion, optional keyboard/pointer | SwiftUI windows, `RealityView`, `Volume`, `ImmersiveSpace`, spatial focus/hover, RealityKit where needed | Comfort, field of view, depth, minimum immersion, indirect interaction, spatial accessibility, safety | visionOS simulator for layout plus Apple Vision Pro for claimed spatial input, comfort, performance, permissions, and physical safety behavior |
| watchOS | Glance, touch/swipe, Digital Crown, short actions, notifications/complications | watchOS SwiftUI, shallow navigation, crown-friendly scrolling, WidgetKit complications, notifications | One screen at a time, concise content, Always On, crown, paired-device/offline state | watch simulator for sizes and flows plus physical Apple Watch for crown, glance, Always On, sensors, notifications, and pairing |

The matrix is a design and evidence plan, not a claim that every framework or API supports every target. Check the symbol’s current availability and the target’s linked frameworks, capabilities, entitlements, and deployment settings in the actual project.

## Input and accessibility adaptation

Input is part of the product contract. Preserve the same outcome, but give each platform’s expected input a meaningful path:

| Input | iPhone/iPad | Mac Catalyst | visionOS | watchOS |
| --- | --- | --- | --- | --- |
| Touch | Primary on iPhone and important on iPad | May exist through the platform environment but is not the Mac default | Direct gestures can supplement indirect interaction | Primary alongside crown and swipe |
| Pointer | Additional precision and hover on iPad | Primary mouse/trackpad path | External pointer can coexist with eyes/hands | Not a primary route |
| Keyboard | Optional hardware keyboard; focus and shortcuts matter on iPad | Core navigation and command path | Optional attached keyboard; focus still matters | Text input may use dictation/Scribble/paired iPhone; keep it short |
| Pencil | Drawing, selection, drag, and precision tasks where valuable | Not an assumed input | Not an assumed input substitute | Not supported as a default target input |
| Eyes/hands | Not the default iOS input model | Not the default Catalyst input model | Core indirect/direct interaction; comfort and accessibility matter | Not applicable |
| Crown/complication/notification | Not applicable | Not applicable | Digital Crown controls immersion, but is not a generic app scroll substitute | Use the Digital Crown, complications, notifications, and short actions where the outcome benefits |
| Assistive technologies | VoiceOver, Voice Control, Switch Control, Full Keyboard Access, Assistive Access as applicable | VoiceOver, keyboard navigation, pointer settings, and platform accessibility | VoiceOver, Switch Control, Dwell/Head Pointer and spatial accessibility routes | VoiceOver and watchOS accessibility routes |

Prefer semantic SwiftUI controls so the system can expose actions to multiple input and assistive paths. When a custom gesture is essential, provide a visible or discoverable alternative, an accessibility action, keyboard/focus path where supported, and a test case for cancellation and state change. Do not encode meaning only in hover, haptic feedback, animation, color, or a spatial gesture.

## Liquid Glass across targets

Liquid Glass is a system-aware visual and interaction layer, not a universal background token. Use the platform’s standard bars, navigation, tabs, controls, menus, sheets, and materials first. Add a custom glass effect only to a functional group whose boundaries, spacing, hit regions, labels, and fallback behavior are understood.

Keep these decisions target-specific:

- **iPhone/iPad:** preserve readable content beneath and around glass; keep safe-area bars and keyboard-adjacent actions reachable; let pointer/focus states remain visible.
- **Mac Catalyst:** do not cover Mac menu, toolbar, window, or pointer conventions with a phone-shaped glass capsule; check the selected Mac idiom and resizable window.
- **visionOS:** use standard windows for UI-centric work and spatial materials/volumes where the task needs them; prioritize legibility, comfort, depth, indirect gestures, and minimum necessary immersion.
- **watchOS:** prioritize glanceable hierarchy and system-provided controls; do not port a large translucent surface system into a tiny watch task.

Respect reduced transparency, increased contrast, reduced motion, Dynamic Type, localization, and assistive technologies. A glass effect that is beautiful in a preview but obscures a label, creates a small hit target, or removes a keyboard path is not a successful native adaptation.

## Verification route

For every platform branch, record:

1. User outcome and the smallest target-specific surface.
2. Shared domain/state contract and the platform-specific presentation contract.
3. Compilation conditions and API availability used, with the actual target and deployment target.
4. Runtime capability checks: permission, hardware, entitlement, account, asset, paired device, service, and current lifecycle state.
5. Input/accessibility route: touch, pointer, keyboard, Pencil, eyes/hands, crown, VoiceOver, and fallback actions as relevant.
6. Liquid Glass/system-surface decision and reduced-effects fallback.
7. Preview fixtures for empty/loading/error/large text/long localization and representative platform sizes.
8. Simulator/UI test evidence for deterministic state transitions and navigation.
9. Physical-device or paired-system evidence for hardware, spatial, crown, haptic, thermal, audio, camera, sensor, and external-surface claims.

Conditional compilation and `if #available` are implementation evidence. They are not target-support evidence. A shared SwiftUI view is architecture evidence. It is not cross-platform behavior evidence.

## Sources

- [Conditional compilation and availability conditions in Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/statements/)
- [Running code on a specific platform or OS version](https://developer.apple.com/documentation/xcode/running-code-on-a-specific-version)
- [EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues)
- [horizontalSizeClass](https://developer.apple.com/documentation/swiftui/environmentvalues/horizontalsizeclass)
- [verticalSizeClass](https://developer.apple.com/documentation/swiftui/environmentvalues/verticalsizeclass)
- [dynamicTypeSize](https://developer.apple.com/documentation/swiftui/environmentvalues/dynamictypesize)
- [Scene](https://developer.apple.com/documentation/swiftui/scene)
- [WindowGroup](https://developer.apple.com/documentation/swiftui/windowgroup)
- [ScenePhase](https://developer.apple.com/documentation/swiftui/scenephase)
- [UIApplicationDelegateAdaptor](https://developer.apple.com/documentation/swiftui/uiapplicationdelegateadaptor)
- [UIWindowSceneDelegate](https://developer.apple.com/documentation/uikit/uiwindowscenedelegate)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [Layout](https://developer.apple.com/documentation/swiftui/layout)
- [Input and event modifiers](https://developer.apple.com/documentation/swiftui/view-input-and-events)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Designing for iPadOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ipados)
- [Designing for Mac Catalyst](https://developer.apple.com/design/human-interface-guidelines/mac-catalyst)
- [Designing for visionOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos)
- [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos)
- [Pointing devices](https://developer.apple.com/design/human-interface-guidelines/pointing-devices)
- [Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)
- [Virtual keyboards](https://developer.apple.com/design/human-interface-guidelines/virtual-keyboards)
- [Mac Catalyst](https://developer.apple.com/documentation/uikit/mac-catalyst)
- [WatchOS apps](https://developer.apple.com/documentation/watchos-apps)
