# Locked Camera Capture and Camera Control

## Scope

iOS 26 gives camera apps two related but distinct entry routes:

1. LockedCameraCapture lets a person launch a camera capture extension from a configured Control Center or Lock Screen control, or through the Action button, while the device is locked.
2. Camera Control lets a supported iPhone expose capture controls and capture events through a hardware interface while an active camera experience is using the camera.

These routes share AVFoundation capture infrastructure, but they do not share the same process, target, lifecycle, or privacy contract. The correct architecture is:

    system entry -> extension or app target -> active camera session -> temporary/finalized capture -> authenticated app handoff -> review and durable record

An entry point is not background permission. A locked-camera extension is not a general background camera service. A Camera Control event is not delivered to an inactive or backgrounded app that is not actively using the camera.

## Framework and target map

| Product boundary | Framework/API | Target/process owner | Key limit |
| --- | --- | --- | --- |
| Launch a camera experience while locked | LockedCameraCapture, LockedCameraCaptureExtension, LockedCameraCaptureUIScene | Dedicated capture extension target | Extension is sandboxed and has strict network/shared-container restrictions. |
| Pass a small configuration into the capture extension | CameraCaptureIntent and its AppContext | App target, control/widget target, capture extension target | AppContext is bounded user configuration, not a media store or arbitrary database. |
| Store capture-extension content | LockedCameraCaptureSession.sessionContentURL | Capture extension during current session | Temporary directory; system copies it to the containing app’s container and erases extension state on suspension according to the documented lifecycle. |
| Open the containing app after authentication | LockedCameraCaptureSession.openApplication(for:) and NSUserActivityTypeLockedCameraCapture | Capture extension requests; app receives launch | User authentication may be required; launch can fail and needs a visible fallback. |
| Consume extension content in the app | LockedCameraCaptureManager.sessionContentUpdates | Containing app target | Process initial, added, and removed directories; invalidate content when finished. |
| Present camera controls on Camera Control | AVCaptureControl, AVCaptureSlider, AVCaptureIndexPicker, system zoom/exposure sliders | App or capture extension’s active capture session | Check supportsControls, maxControlsCount, canAddControl, and a controls delegate. |
| Handle hardware capture events | SwiftUI onCameraCaptureEvent or AVKit AVCaptureEventInteraction | Active camera view | Events are for media capture only and are not delivered to inactive/backgrounded apps. |

## Locked Camera Capture lifecycle

The Locked Camera Capture template creates a separate extension target. Its scene receives a system-created LockedCameraCaptureSession. The extension’s camera view must become active quickly and use the capture event interaction route; otherwise the system may terminate it shortly after launch. The extension inherits the containing app’s camera permission. If permission is not available, the system can ask the person to authenticate and unlock before the app requests access.

The extension route is:

1. The person configures a control or Action button route.
2. A CameraCaptureIntent carries bounded app context into the system entry.
3. The system launches the capture extension while the device is locked.
4. LockedCameraCaptureUIScene provides a LockedCameraCaptureSession to the extension UI.
5. The extension presents an active camera view.
6. The camera session captures content into the temporary session content directory or through the documented Photos route.
7. The person dismisses the extension or chooses to continue to the containing app.
8. The system copies session content to the app’s container as the extension suspends.
9. LockedCameraCaptureManager.sessionContentUpdates reports directories to the app.
10. The app moves or imports the content into durable storage, performs review or AI processing, and invalidates the temporary directory when done.

The extension should be small and capture-first. Do not place the review, network upload, account login, or model-heavy workflow in the locked extension merely because it can display SwiftUI.

## Extension restrictions

Apple’s locked-camera guidance documents these restrictions while the extension is active:

- no network access;
- no read or write access to the App Group shared container;
- the extension’s container directory is erased when the system suspends the extension after the content is copied;
- the extension may terminate shortly after launch without an active camera view using AVCaptureEventInteraction or without camera authorization.

Treat these as architecture constraints:

| Need | Correct location |
| --- | --- |
| Capture a photo or movie | Locked extension’s active camera session. |
| Store in-progress content | sessionContentURL or the documented PhotoKit route. |
| Upload, sync, authenticate, or call a server | Containing app after the device is authenticated and the app is active. |
| Long-term persistence | Containing app’s sandbox/selected persistence store after import. |
| Foundation Models, remote AI, or large post-processing | Prefer the containing app after finalizing the source; verify any on-device extension use separately. |
| User account or private database access | Containing app after unlock; do not assume App Group access from the extension. |

## Camera Control route

Camera Control provides a system overlay for controls such as zoom and exposure and can launch a supported app’s camera experience. AVFoundation supplies:

- AVCaptureSystemZoomSlider;
- AVCaptureSystemExposureBiasSlider;
- AVCaptureSlider for a bounded continuous or stepped float;
- AVCaptureIndexPicker for mutually exclusive options;
- AVCaptureControl as the base type;
- AVCaptureSession.addControl and removeControl;
- supportsControls, maxControlsCount, and canAddControl;
- AVCaptureSessionControlsDelegate for activation and fullscreen presentation changes.

Configure controls as part of the capture session’s responsibilities. The framework may refuse a control because the platform does not support controls, the session has reached its maximum, or the current system state cannot accept it. Attempting to add a control without checking can raise an exception.

The system invokes a control’s action on MainActor for the built-in system slider route. Keep that action small and route any device graph work through the session owner. A control’s value is input to the capture configuration; it is not a domain record.

When controls become active or enter fullscreen appearance, hide distracting app UI and restore it when controls become inactive. Do not duplicate a zoom or exposure control in the viewfinder while the system overlay presents the same control.

## Hardware capture events

SwiftUI provides onCameraCaptureEvent for supported capture-event handling. AVKit provides AVCaptureEventInteraction for UIKit or bridge-based surfaces. Use the SwiftUI modifier when the feature is already SwiftUI-native; use the interaction object when a UIKit camera view or extension needs the explicit interaction.

Event rules:

- use the event only for a media capture action;
- respond to the event phase, not just the existence of a callback;
- always provide a meaningful primary/secondary response if the app has enabled the event;
- set isEnabled to false when the app cannot respond so default system behavior is restored;
- do not expect events while the app is backgrounded or not actively using the camera;
- test cancellation and multiple event sources;
- provide an audible/visual/haptic confirmation according to the system event contract and accessibility route.

Adopting the event interaction overrides the default hardware-button behavior for the active camera surface. Leaving it enabled without a functioning action creates a nonfunctional system control.

## App context and system entry

CameraCaptureIntent is an App Intents protocol that designates an intent for an activity using the device camera. Its AppContext can carry small Codable, Sendable configuration such as:

- front or rear camera preference;
- capture mode;
- selected filter identifier;
- user-selected framing option;
- a non-sensitive workflow identifier.

Do not place raw media, tokens, secrets, large model input, or a database snapshot in AppContext. The locked extension is a separate process with a separate privacy boundary. Treat context as a hint that needs validation, not as authority.

Controls placed in Control Center, on the Lock Screen, or on the Action button are configured through WidgetKit and App Intents. The control’s presence is user-configured. A system control can launch the locked camera extension, but it does not guarantee that the user has granted camera permission, that a device has a camera, or that a capture can complete.

## Content handoff

The extension’s sessionContentURL is temporary. In the containing app:

1. Observe LockedCameraCaptureManager.shared.sessionContentUpdates.
2. Handle the initial set of directories as well as added and removed updates.
3. Validate each directory and file before importing.
4. Move or copy content into a durable location owned by the app.
5. Preserve source metadata and session provenance.
6. Present a review state rather than silently publishing.
7. Call invalidateSessionContent(at:) when the directory is no longer needed.

The most recent directory may arrive shortly after the app launches. Do not assume the app receives it synchronously from the openApplication call. Use an idempotent importer keyed by directory URL and source identifiers.

When the extension opens the app, use an NSUserActivity with NSUserActivityTypeLockedCameraCapture. Handle ApplicationLaunchError, authentication failure, user cancellation, and the case where content has not arrived yet. The app should land in a capture-review destination, not a generic home screen.

## Availability and platform matrix

| Route | Supported shape | Verify |
| --- | --- | --- |
| Camera Control | Supported iPhone hardware; HIG marks it unavailable on iPadOS, macOS, watchOS, tvOS, and visionOS | Device model, OS, capture session support, and actual overlay. |
| LockedCameraCapture | iOS camera capture extension with configured system control/entry point | Target type, extension embedding, control configuration, permission, locked/unlocked device. |
| SwiftUI capture events | Active camera surface using onCameraCaptureEvent | Deployment target, import, event delivery, active camera state, and fallback button. |
| AVCaptureEventInteraction | UIKit or representable camera surface | Active view, event source, enabled state, and device hardware. |
| CameraCaptureIntent | App, control/widget, and capture-extension membership as required | Intent membership, AppContext serialization, control gallery/entry configuration. |

Use availability checks and a regular in-app capture button for unsupported platforms or devices. Do not condition only on OS version when the feature depends on hardware.

## Security and privacy

The locked route deliberately limits what can happen before authentication. Preserve that boundary:

- do not reveal private library data or account state in the locked preview;
- redact control labels or require authentication when the control would expose sensitive text;
- do not upload or sync from the capture extension;
- keep temporary content in the documented session directory;
- delete or invalidate content after the containing app imports it;
- use least-privilege AppContext values;
- explain camera use with the containing app’s truthful usage description;
- do not interpret a locked capture as user consent to publish, share, or run an irreversible AI action.

## Proof route

The simulator can cover target composition, mocked state, navigation, and review UI. It cannot prove lock-screen entry, Camera Control overlay behavior, camera hardware, physical button events, temporary-directory copying, or authentication transitions.

Minimum physical proof:

- supported iPhone model and iOS 26 build;
- control configured in Control Center/Lock Screen/Action button;
- locked launch and authenticated continuation;
- camera permission not determined, granted, denied, and revoked;
- extension dismissal by swipe and side button;
- photo and movie capture;
- Camera Control zoom/exposure/custom control activation;
- fullscreen control overlay hiding/restoring app UI;
- hardware event start/end/cancel;
- session content initial/added/removed updates;
- durable import and invalidate cleanup;
- no-network behavior in the extension;
- app launch failure and missing-content fallback;
- Dynamic Type, VoiceOver, Voice Control, Reduce Motion, and reduced transparency in the extension and app review surface.

## Sources

- [LockedCameraCapture](https://developer.apple.com/documentation/LockedCameraCapture)
- [Creating a camera experience for the Lock Screen](https://developer.apple.com/documentation/LockedCameraCapture/Creating-a-camera-experience-for-the-Lock-Screen)
- [LockedCameraCaptureExtension](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracaptureextension)
- [LockedCameraCaptureUIScene](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracaptureuiscene)
- [LockedCameraCaptureSession](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracapturesession)
- [LockedCameraCaptureManager](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracapturemanager)
- [sessionContentURL](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracapturesession/sessioncontenturl)
- [Enhancing your app experience with the Camera Control](https://developer.apple.com/documentation/avfoundation/enhancing-your-app-experience-with-the-camera-control)
- [AVCaptureControl](https://developer.apple.com/documentation/avfoundation/avcapturecontrol)
- [AVCaptureSlider](https://developer.apple.com/documentation/avfoundation/avcaptureslider)
- [AVCaptureIndexPicker](https://developer.apple.com/documentation/avfoundation/avcaptureindexpicker)
- [AVCaptureSystemZoomSlider](https://developer.apple.com/documentation/avfoundation/avcapturesystemzoomslider)
- [AVCaptureSystemExposureBiasSlider](https://developer.apple.com/documentation/avfoundation/avcapturesystemexposurebiasslider)
- [Adding a control to a capture session](https://developer.apple.com/documentation/avfoundation/avcapturesession/addcontrol%28_%3A%29)
- [AVCaptureEventInteraction](https://developer.apple.com/documentation/avkit/avcaptureeventinteraction)
- [AVCaptureEvent](https://developer.apple.com/documentation/avkit/avcaptureevent)
- [onCameraCaptureEvent](https://developer.apple.com/documentation/swiftui/view/oncameracaptureevent%28isenabled%3Adefaultsounddisabled%3Aaction%3A%29)
- [CameraCaptureIntent](https://developer.apple.com/documentation/appintents/cameracaptureintent)
- [Creating controls to perform actions across the system](https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system)
- [Controls](https://developer.apple.com/documentation/widgetkit/controls-collection)
- [Camera Control](https://developer.apple.com/design/human-interface-guidelines/camera-control)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
