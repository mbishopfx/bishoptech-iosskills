# UIKit Interoperability and Representable Boundaries

## User outcome

Use this route when a feature needs a UIKit view or view controller that SwiftUI does not provide directly, or when an existing UIKit app is adopting SwiftUI incrementally. The goal is a small, reviewable bridge with explicit state and lifecycle ownership—not a second UI architecture hidden inside a SwiftUI wrapper.

The first question is still whether a native SwiftUI control, container, modifier, or system surface already expresses the outcome. Native SwiftUI often carries platform behavior, accessibility, focus, keyboard and pointer behavior, safe-area handling, and system styling that a custom UIKit bridge must reproduce deliberately.

## Choose the seam

| Situation | Route | Ownership rule | Proof requirement |
| --- | --- | --- | --- |
| A SwiftUI view is needed inside an existing UIKit screen | `UIHostingController` | UIKit owns presentation and containment; SwiftUI owns the hosted view’s state and rendering | Build the UIKit target and verify sizing, traits, navigation, dismissal, accessibility, and rotation/window changes |
| A UIKit `UIView` is the smallest missing capability | `UIViewRepresentable` | SwiftUI owns the wrapper inputs; the representable creates, updates, and tears down the UIKit view | Compile the selected target; test update identity, delegate callbacks, layout, focus, accessibility, and the real capability if it touches hardware |
| A UIKit `UIViewController` owns a controller-oriented flow | `UIViewControllerRepresentable` | SwiftUI owns the route and input state; the controller owns its internal UIKit view hierarchy; the coordinator translates callbacks | Test presentation, dismissal, controller lifecycle, cancellation, permission/error states, and trait changes |
| SwiftUI content belongs in a UIKit table or collection cell | `UIHostingConfiguration` | UIKit owns cell reuse and selection; SwiftUI owns the cell content and semantic actions | Exercise reuse, dynamic height, selection, swipe actions, large text, VoiceOver, and scrolling in the UIKit target |
| A native AppKit view is needed in a macOS target | `NSViewRepresentable` or `NSViewControllerRepresentable` | AppKit owns the native macOS object; SwiftUI owns the wrapper contract | Test the macOS target separately; Mac Catalyst evidence is not macOS/AppKit evidence |
| A watchOS or visionOS feature is missing a platform-native SwiftUI route | Check the target’s framework and symbol availability first | Do not assume an iOS UIKit bridge is portable to a watchOS or visionOS target | Build the named target and verify the platform-specific input and system presentation |

`UIHostingController` and `UIHostingConfiguration` are one-way composition routes from SwiftUI into UIKit. Representables are the reverse direction. A shared model or domain use case can sit underneath both, but a shared wrapper is not proof that the two surfaces behave identically.

## `UIViewRepresentable` lifecycle

The wrapper should make the bridge’s state machine visible:

1. **Create.** Use the protocol’s `makeUIView(context:)` route to create and minimally configure the UIKit view. Construction should not be mistaken for permission, capture, network, or model authorization.
2. **Connect.** Create a coordinator only when delegate, target-action, notification, data-source, or asynchronous callback translation is needed. Keep the coordinator focused on translating UIKit events into an explicit SwiftUI-facing callback or service action.
3. **Update.** Use `updateUIView(_:context:)` to reconcile the current value inputs with the already-created UIKit object. Make updates idempotent. Do not recreate expensive sessions, reset user input, or attach duplicate observers on every update.
4. **Tear down.** Use the representable’s teardown hook to remove delegates/observers, cancel work owned by the bridge, stop temporary capability use, and release resources that should not survive the view’s removal.
5. **Render.** Let SwiftUI own the representable’s placement and sizing. Apple’s documentation warns against directly changing layout-related properties on the UIKit view managed by the representable because that conflicts with SwiftUI’s layout system.

The context supplied by SwiftUI is a translation boundary, not a global service locator. Use it for the coordinator, transaction, environment, and other framework-provided information that belongs to the current update. Put durable state, permissions, model sessions, and persistence in an injected service or feature model instead of storing them as accidental view-instance state.

### A safe view bridge shape

~~~swift
import SwiftUI
import UIKit

struct PreviewableUIKitSurface: UIViewRepresentable {
    let title: String
    let onActivate: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onActivate: onActivate)
    }

    func makeUIView(context: Context) -> UIButton {
        let button = UIButton(type: .system)
        button.addTarget(
            context.coordinator,
            action: #selector(Coordinator.activate),
            for: .primaryActionTriggered
        )
        return button
    }

    func updateUIView(_ button: UIButton, context: Context) {
        button.setTitle(title, for: .normal)
        context.coordinator.onActivate = onActivate
    }

    static func dismantleUIView(_ button: UIButton, coordinator: Coordinator) {
        button.removeTarget(
            coordinator,
            action: #selector(Coordinator.activate),
            for: .primaryActionTriggered
        )
    }

    final class Coordinator: NSObject {
        var onActivate: () -> Void

        init(onActivate: @escaping () -> Void) {
            self.onActivate = onActivate
        }

        @objc func activate() {
            onActivate()
        }
    }
}
~~~

This is a route sketch, not a claim that every SDK version accepts the exact sample unchanged. Compile it in the target project. For a production bridge, also map the UIKit control’s label, value, traits, enabled state, focus behavior, keyboard path, pointer path, and error state. If the UIKit control is not semantically a button, choose the UIKit class and SwiftUI representation that matches the user outcome instead of wrapping a decorative view in a tap gesture.

## `UIViewControllerRepresentable` lifecycle

Use a controller representable when the UIKit capability owns a controller-level flow: a picker, document controller, camera/capture controller, share/presentation controller, or another framework-provided interaction. The system calls the make/update/teardown routes at appropriate times, but it does not automatically forward changes from the controller back into the rest of the SwiftUI hierarchy. A coordinator or explicit callback boundary is required for delegate and target-action events.

Keep these boundaries separate:

| Concern | SwiftUI/feature owner | UIKit/controller owner |
| --- | --- | --- |
| Route presentation and dismissal | Navigation state, sheet/full-screen state, cancellation policy | View-controller presentation mechanics |
| User-visible state | Loading, unavailable, permission, draft, success, error | Controller-specific transient UI |
| Capability session | Feature service or adapter with explicit start/stop | UIKit callbacks and framework object |
| Delegate translation | Coordinator callback, async stream, or service event | Delegate/data-source methods |
| Durable result | Validated domain model and persistence service | Raw controller output only |
| Accessibility | Meaningful SwiftUI route and labels, plus UIKit metadata | Controller’s native elements and callbacks |

Do not save a raw controller result directly as trusted domain truth. Normalize it, record provenance and timestamp where relevant, validate it, and let the feature decide whether the person must review it. This is especially important for camera, photo, document, contact, map, payment, and system picker flows.

## Coordinator and callback discipline

The coordinator is a translator, not a second view model. It may hold delegates, weak references, task handles, cancellation tokens, or a small amount of bridge-local state. It should not become the owner of the app database, entitlement decision, or long-lived AI session merely because the UIKit object has a delegate.

Use the following callback discipline:

- Make callbacks idempotent. A dismissal, completion, cancellation, or error may arrive through more than one UIKit path.
- Record the feature identity or request identifier when starting asynchronous work. Ignore late results for a request that has been cancelled or replaced.
- Normalize framework callbacks before mutating SwiftUI-owned state. UIKit and framework callbacks can have their own delivery rules; keep UI and observable-state mutation on the actor required by the selected API.
- Remove delegates and observers during teardown. A stale coordinator callback must not update a new screen instance.
- Treat `nil`, empty, cancelled, denied, unavailable, and failed as different outcomes when the user experience needs to explain them differently.
- Keep the closure or async stream narrow. Send a typed event or domain input rather than leaking the controller object into every parent view.

## Hosting SwiftUI in UIKit

Create a `UIHostingController` when the containing navigation, storyboard, cell, or presentation flow remains UIKit-owned but the feature surface is SwiftUI. Set the root view from the feature’s explicit inputs and update that root view when the UIKit host’s state changes. Use the hosting controller as a normal view controller: containment, presentation, safe areas, sizing, transitions, status-bar behavior, and UIKit lifecycle still matter.

For table and collection cells, `UIHostingConfiguration` is a more targeted seam than embedding a hosting controller manually. It is designed to host SwiftUI content in `UICollectionViewCell` or `UITableViewCell`, and Apple documents automatic bridging for some list behavior such as swipe actions and separator alignment. Cell reuse is still UIKit state: make sure content identity, selection, asynchronous image/model work, and accessibility state are reset when the cell is reused.

## UIKit, Mac Catalyst, visionOS, and watchOS

### iPhone and iPad

UIKit representables can be useful for a capability that has no adequate SwiftUI surface, but iPhone and iPad are not the same layout/input target. A bridge must survive compact and regular width, rotation, split view, Stage Manager or other windowing contexts where supported, Dynamic Type, keyboard, pointer, Apple Pencil, VoiceOver, and dismissal behavior.

### Mac Catalyst

Mac Catalyst is a UIKit-based Mac target. Apple describes it as a way to create a Mac version of an iPad app with shared project/source code, while also documenting that only AppKit APIs marked available for Mac Catalyst can be used. Use `#if targetEnvironment(macCatalyst)` for Catalyst-specific code and verify the Catalyst target on a Mac. Do not substitute a Mac Catalyst run with a native macOS/AppKit run, and do not treat an iPad simulator as proof of Mac menus, pointer/keyboard expectations, resizable windows, or Catalyst API availability.

If the product later adds a native macOS target, use AppKit integration and `NSViewRepresentable`/`NSViewControllerRepresentable` where appropriate. Keep the domain and feature contracts shared only where they remain meaningful.

### visionOS

Prefer visionOS-native SwiftUI, windows, volumes, `RealityView`, and `ImmersiveSpace` routes when the feature is spatial. An iOS UIKit wrapper may compile only under a particular target and SDK combination; it is not evidence that eyes, hands, indirect gestures, direct gestures, spatial focus, window placement, depth, comfort, or immersion behavior is correct. If a UIKit framework surface is required, document the exact target availability and provide a visionOS-specific input and comfort proof plan.

### watchOS

Prefer watchOS SwiftUI and WatchKit routes for glanceable, short, crown-aware tasks. A watch app is not a narrow iPhone layout. If a WatchKit object or controller must be bridged, use the WatchKit representable/hosting route documented for the watch target. Validate Digital Crown behavior, Always On presentation, short interaction depth, notifications/complications, paired-device state, and the physical watch. iPhone or iPad UIKit evidence does not prove watchOS behavior.

## Liquid Glass and system-surface boundaries

Bridging UIKit does not automatically make a view Liquid Glass or Apple-native. Keep the hierarchy explicit:

1. Prefer the platform’s standard navigation containers, toolbars, tabs, sheets, controls, and system bars.
2. Use Liquid Glass on a functional SwiftUI control or group only when the selected SDK and target support the route and the effect improves hierarchy or interaction.
3. Keep the UIKit bridge responsible for its own content and semantics. Do not paint an opaque or translucent universal glass card over a UIKit system surface just to imitate an Apple screenshot.
4. Give reduced-transparency, increased-contrast, large-text, reduced-motion, and VoiceOver states a usable fallback.
5. Expect glass, focus, hover, window, and material behavior to vary by platform. The same modifier or wrapper is not a visual-parity guarantee.

## Verification matrix

| Evidence | What it can show | What it cannot show by itself |
| --- | --- | --- |
| Preview with a fake UIKit object | The SwiftUI wrapper can render controlled states and callbacks | Real controller presentation, permission, hardware, system surface, or physical input |
| Unit test for adapter/coordinator | Mapping, idempotency, cancellation, stale-result rejection, and state transitions | UIKit layout, VoiceOver quality, real hardware, entitlement, or system delivery |
| Simulator/UI test | Navigation, dismissal, text input, focus, reuse, accessibility identifiers, and deterministic callback paths | Camera/sensor/haptic fidelity, thermal behavior, physical ergonomics, and every target family |
| Physical iPhone/iPad | Touch, keyboard/pointer/Pencil where supported, hardware framework behavior, safe areas, rendering, and accessibility interaction | Mac Catalyst, watchOS, visionOS, production scale, or App Store approval |
| Mac Catalyst target on Mac | Catalyst availability, menus, pointer/keyboard, window resizing, and Mac idiom decisions | Native macOS/AppKit, iPad multitasking, watch, or visionOS behavior |
| Physical Apple Watch or Apple Vision Pro | Named target’s interaction, sensors, spatial/comfort or crown behavior | Other platforms, unsupported devices, release delivery, or cross-device sync at scale |

Record the target name, SDK/deployment target, build, device/OS, route, permissions, input mode, accessibility settings, and result. “The representable works” is too broad to be useful evidence.

## Sources

- [UIKit integration](https://developer.apple.com/documentation/swiftui/uikit-integration)
- [UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [UIViewRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewrepresentablecontext)
- [UIViewControllerRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentablecontext)
- [UIHostingController](https://developer.apple.com/documentation/swiftui/uihostingcontroller)
- [UIHostingConfiguration](https://developer.apple.com/documentation/swiftui/uihostingconfiguration)
- [AppKit integration](https://developer.apple.com/documentation/swiftui/appkit-integration)
- [NSViewRepresentable](https://developer.apple.com/documentation/swiftui/nsviewrepresentable)
- [WatchKit integration](https://developer.apple.com/documentation/swiftui/watchkit-integration)
- [Mac Catalyst](https://developer.apple.com/documentation/uikit/mac-catalyst)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Designing for iPadOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ipados)
- [Designing for visionOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos)
- [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
