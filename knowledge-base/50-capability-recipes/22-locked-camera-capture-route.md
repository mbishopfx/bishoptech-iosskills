# Locked camera capture route

## Outcome

Offer a fast camera experience from the Lock Screen, Control Center, Action button, or Camera Control, then move the captured content into the containing app for review, on-device intelligence, persistence, and user-approved sharing.

This route is for a camera-first product such as a field note, receipt capture, visual log, inspection photo, or quick video. It is not a recipe for silent background capture.

## Route shape

    configured system control
      -> CameraCaptureIntent/AppContext
      -> LockedCameraCapture extension
      -> active camera session and hardware event
      -> temporary session content
      -> authenticated containing app
      -> idempotent import
      -> review and optional AI
      -> approved record/export

## Target register

| Target | Owns | Must be configured |
| --- | --- | --- |
| Main app | Durable model, review UI, import manager, optional AI, export/share | Camera permission, scene/lifecycle handling, selected persistence and media capabilities. |
| Capture extension | Locked camera UI and immediate capture | Locked Camera Capture Extension target, app camera permission inheritance, active camera view, capture event interaction. |
| Widget/control extension | Control Center/Lock Screen/Action button control and intent membership | WidgetKit control, CameraCaptureIntent membership, control display name/description/icon, user configuration. |
| Shared intent code | CameraCaptureIntent and AppContext | Target membership in app, control extension, and capture extension as required by Apple’s guide. |
| Optional storage/system target | PhotoKit or another system handoff | Separate authorization/entitlement and evidence; do not assume extension access. |

Keep target membership explicit. A source file compiling in the app target does not mean the capture extension or control extension can access it.

## Preflight decisions

Write these decisions before adding the extension:

- Is the fast path photo, video, or both?
- What is the minimum capture UI before unlock?
- What data can safely be carried in AppContext?
- Does the extension write to sessionContentURL, PhotoKit, or both?
- What happens when the user dismisses the extension before the containing app opens?
- What happens when the app launches before the newest session directory arrives?
- Which review and AI features wait until authentication?
- What is deleted after import?
- Which device families support Camera Control?
- What is the ordinary in-app fallback on unsupported hardware?

## Extension route

### Start

The capture extension scene receives a system-created LockedCameraCaptureSession. Use LockedCameraCaptureUIScene to build the view. The extension should create an active camera session quickly and use the capture event interaction route. A view that merely draws a preview but does not establish a functioning capture path can be terminated by the system.

### Capture

Use the narrowest AVFoundation route:

| Capture need | First choice |
| --- | --- |
| Still photo | AVCapturePhotoOutput or the documented system picker route. |
| Movie | AVCaptureMovieFileOutput when high-level file output is sufficient. |
| Live analysis before unlock | Only when it is essential, bounded, and supported by the extension contract; prefer post-unlock processing. |

Keep the extension’s graph short. Avoid opening a network-dependent model or account service. Record source metadata locally in the temporary directory if the app needs it after handoff.

### Store

Use sessionContentURL for content that must survive the extension process until the containing app imports it. Treat it as temporary:

1. Create a unique child path.
2. Write only finalized files or recoverable draft state.
3. Flush/close writers before considering capture complete.
4. Do not assume the directory is a permanent app store.
5. Do not rely on App Group shared storage.

If using PhotoKit, keep the authorization and system-library behavior separate from the session-directory importer. Saving to Photos is not the same as creating the app’s approved record.

### Continue

Call openApplication(for:) with an NSUserActivity carrying the documented locked-camera activity type when the user chooses to continue. Handle authentication and launch errors. The app should use the activity to route to a pending-capture review destination.

## Containing-app importer

Use LockedCameraCaptureManager.shared.sessionContentUpdates as the source of truth for temporary capture directories. The sequence can provide:

- initial directories already present;
- an added directory;
- a removed directory.

Implement an idempotent importer:

    directory URL -> validate manifest/files -> copy/move to durable location -> create source record -> queue review -> invalidate temporary directory

A directory URL is not a unique business record by itself. Generate a durable source ID, store the launch provenance, and keep an import ledger to avoid duplicate records after a process restart.

Do not invalidate the temporary directory before the durable copy and metadata write succeed. If import fails, retain a recoverable pending state and present retry/delete options.

## Camera Control route

Configure controls only when the active capture session supports them:

1. Check supportsControls.
2. Build the selected system/custom control list.
3. Call canAddControl for each control.
4. Add controls within the session configuration boundary where appropriate.
5. Set an AVCaptureSessionControlsDelegate.
6. Hide distracting app UI when the controls enter fullscreen appearance.
7. Restore app UI when controls exit.
8. Disable controls that do not apply to the current mode.

Possible controls:

- system zoom slider;
- system exposure-bias slider;
- bounded focus slider;
- filter picker;
- format or framing picker;
- timer or stabilization option where the value is truly useful at capture time.

Keep the Camera Control list small. Use short localized titles, SF Symbols, units, and prominent values. If a control is not relevant to the current mode, disable it or present a valid alternate value; do not leave a control active with no meaningful effect.

## CameraCaptureIntent/AppContext

Use CameraCaptureIntent for the system entry. AppContext is useful for bounded user preference, not authority:

    struct CaptureContext: Codable, Sendable {
        var cameraPosition: CameraPosition
        var captureMode: CaptureMode
        var selectedFilterID: String?
    }

Validate every field when the extension launches. The current device may not support the remembered camera position, mode, filter, or format. Fall back to a supported safe default.

Do not place credentials, full database objects, raw images, or arbitrary media data in AppContext. Keep the payload small and stable across app/extension versions.

## State and fallback matrix

| State | Extension behavior | Containing app behavior |
| --- | --- | --- |
| Camera permission not determined | System may require unlock and app authorization | Request at the real camera action; explain why. |
| Permission denied/revoked | Show a clear unavailable state and exit path | Offer Settings or in-app import fallback. |
| Device lacks Camera Control | Use touch capture and ordinary in-app route | Do not render a dead hardware-control claim. |
| Controls unsupported or full | Keep the camera usable with touch/default controls | Log/evaluate configuration failure; do not call addControl blindly. |
| Extension suspended | Finish or preserve content in sessionContentURL | Import when a directory update arrives; handle missing directory. |
| User dismisses extension | Show temporary-state copy if possible | Process removed/update state and retain no false “saved” record. |
| App opens before content arrives | Show Pending capture state | Await the update sequence; do not show an empty success record. |
| Authentication fails | Remain in extension or show failure | Keep pending content safe and offer retry after unlock. |
| Import fails | Extension content remains temporary per system lifecycle | Retry or explain loss risk before invalidation. |
| Network unavailable | Capture locally | Defer upload/AI/account work until app is active. |
| Model/AI unavailable | Keep the original media | Offer manual review and later retry. |
| Low storage | Stop or reject capture clearly | Retain source if valid; clean partial output. |

## On-device AI handoff

After import and source validation:

    source -> Vision/OCR/Speech/Core ML -> optional Foundation Models organization -> review -> SwiftData/system surface

Attach provenance to each proposal:

- source ID;
- capture time and orientation;
- extension/session origin;
- model/framework and revision;
- crop or preprocessing;
- provisional/final state;
- user correction and acceptance.

Keep network calls, account context, and consequential side effects in the containing app. An on-device proposal can still be wrong or stale. It must not publish, send, or write sensitive data merely because the extension completed capture.

## Native UI composition

Locked extension:

- minimal camera preview;
- primary capture action;
- hardware event feedback;
- recording/time state;
- temporary-storage/continue explanation.

Containing app:

- media review;
- retake/discard;
- edit/AI proposal;
- approve/save;
- export/share.

Use Liquid Glass only around functional actions in the unlocked app. Keep the camera content itself outside the material group. If the system Camera Control overlay is active, reduce or hide duplicate app controls.

## Verification packet

### Preview and simulator

Prove mocked states, import/review navigation, Dynamic Type, VoiceOver labels, reduced effects, empty/pending/error copy, and AppContext fallback.

### Signed physical device

Prove supported hardware entry, locked/unlocked transition, actual camera session, physical capture event, Camera Control overlay, temporary-directory transfer, authentication, and imported media.

### Archive/system configuration

Inspect target membership, extension embedding, privacy strings, intent membership, WidgetKit control configuration, entitlements, supported device family, and signed archive. A successful in-app capture does not prove the system control or locked extension is configured.

## Sources

- [LockedCameraCapture](https://developer.apple.com/documentation/LockedCameraCapture)
- [Creating a camera experience for the Lock Screen](https://developer.apple.com/documentation/LockedCameraCapture/Creating-a-camera-experience-for-the-Lock-Screen)
- [LockedCameraCaptureUIScene](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracaptureuiscene)
- [LockedCameraCaptureSession](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracapturesession)
- [LockedCameraCaptureManager](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracapturemanager)
- [CameraCaptureIntent](https://developer.apple.com/documentation/appintents/cameracaptureintent)
- [CameraCaptureIntent app context](https://developer.apple.com/documentation/appintents/cameracaptureintent/appcontext-swift.type.property)
- [Creating controls to perform actions across the system](https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system)
- [Controls](https://developer.apple.com/documentation/widgetkit/controls-collection)
- [Enhancing your app experience with the Camera Control](https://developer.apple.com/documentation/avfoundation/enhancing-your-app-experience-with-the-camera-control)
- [AVCaptureSession controls](https://developer.apple.com/documentation/avfoundation/avcapturesession/controls)
- [Adding a control to a capture session](https://developer.apple.com/documentation/avfoundation/avcapturesession/addcontrol%28_%3A%29)
- [AVCaptureControl](https://developer.apple.com/documentation/avfoundation/avcapturecontrol)
- [AVCaptureSystemZoomSlider](https://developer.apple.com/documentation/avfoundation/avcapturesystemzoomslider)
- [AVCaptureSystemExposureBiasSlider](https://developer.apple.com/documentation/avfoundation/avcapturesystemexposurebiasslider)
- [AVCaptureSlider](https://developer.apple.com/documentation/avfoundation/avcaptureslider)
- [AVCaptureIndexPicker](https://developer.apple.com/documentation/avfoundation/avcaptureindexpicker)
- [AVCaptureEventInteraction](https://developer.apple.com/documentation/avkit/avcaptureeventinteraction)
- [onCameraCaptureEvent](https://developer.apple.com/documentation/swiftui/view/oncameracaptureevent%28isenabled%3Adefaultsounddisabled%3Aaction%3A%29)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Camera Control](https://developer.apple.com/design/human-interface-guidelines/camera-control)
