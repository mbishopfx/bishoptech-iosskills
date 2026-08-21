# Camera Control and lock-screen capture proof matrix

## Evidence rule

Locked Camera Capture and Camera Control are target, process, hardware, and authentication features. Verify the complete route instead of substituting a normal in-app camera run for system entry proof.

    claim -> target membership/configuration -> locked or active-device fixture -> evidence -> limitation

## Entry-point matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Control Center launches the capture extension | Signed device with user-configured control, locked and unlocked runs, extension log/state | A WidgetKit control preview or AppIntent compile. |
| Lock Screen launches the capture extension | Supported iPhone, configured Lock Screen control, locked launch, active camera view | An in-app deep link. |
| Action button launches capture | Supported device with Action button configuration and locked capture run | A button in the app. |
| Camera Control launches/controls the app | Supported iPhone hardware, active camera session, overlay and controls interaction | A standard camera run on an unsupported simulator. |
| Camera Control controls have correct limits | supportsControls, maxControlsCount, canAddControl, controls delegate, overlay evidence | Constructing an AVCaptureSlider. |
| Hardware capture event reaches the view | Physical press with begin/end/cancel and active camera state | Calling the SwiftUI action directly. |
| Disabled event restores default behavior | isEnabled false while camera cannot handle event, then hardware test | Hiding a button. |
| Locked extension remains active | Extension starts an active camera view using the documented event interaction | A static extension scene. |
| Extension content reaches app | Initial/added/removed sessionContentUpdates and durable import | Calling openApplication and assuming a file exists. |
| App handoff waits for authentication | Locked device, openApplication(for:), authentication success/failure | An unlocked app launch. |

## Target and archive matrix

Inspect the built target graph:

- main application target;
- Locked Camera Capture Extension target;
- WidgetKit control extension target;
- shared CameraCaptureIntent/AppContext source membership;
- extension embedding and signing;
- deployment target and device family;
- camera/microphone privacy strings;
- entitlements and capabilities;
- intent/control metadata;
- scene and launch configuration;
- resource and media type membership;
- release archive and TestFlight installation where the route is intended for distribution.

| Configuration claim | Archive evidence | Runtime evidence |
| --- | --- | --- |
| Extension exists in the product | Archive target/extension bundle inspection | Device can launch it from the configured system location. |
| CameraCaptureIntent is available | Target membership and symbol/interface inspection | Control or Action button actually launches the intended extension. |
| Privacy strings are present | Info.plist/archive inspection | Permission prompt appears with truthful copy. |
| Camera Control support is declared by code | Compiled selected SDK and availability branch | Supported hardware presents overlay and rejects unsupported path gracefully. |
| AppContext is shared | Source membership and serialization tests | Value arrives in extension and falls back safely when stale/missing. |
| Temporary handoff is wired | Extension/app target inspection | Content directory is copied, imported, and invalidated. |

## Locked lifecycle fixtures

Run every fixture on a supported physical device:

1. Permission not determined, locked launch, authentication prompt, and grant.
2. Permission denied, locked launch, and safe exit.
3. Permission revoked after a prior successful capture.
4. Launch from Control Center.
5. Launch from the Lock Screen.
6. Launch from the Action button.
7. Extension starts without an active camera view.
8. Extension starts with camera unavailable.
9. Capture a still photo.
10. Record and stop a movie.
11. Capture and dismiss by swiping up.
12. Capture and dismiss with the side button.
13. Capture, open the containing app, and import.
14. Open app before the newest content directory arrives.
15. Import failure and retry.
16. Invalidate the directory after durable copy.
17. Extension process suspension/termination during a draft.
18. Attempted network-dependent work and correct no-network fallback.
19. Authentication failure or cancellation.
20. Multiple sessions and duplicate importer restart.

Capture:

- timestamps and orientation;
- source file finalization;
- photo/movie media type;
- storage size and partial-file cleanup;
- extension/session provenance;
- correct review destination after unlock.

## Camera Control fixtures

| Fixture | Observe |
| --- | --- |
| Supported iPhone, camera active | Camera Control overlay appears and shows the configured controls. |
| Unsupported iPhone/iPad | No dead control claim; ordinary touch capture remains usable. |
| Zoom slider | Range follows the active device format; value and unit are legible. |
| Exposure slider | EV value updates the capture device and is not confused with a model observation. |
| Custom slider | Bounded range, step, action queue, prominent values, and localized value format. |
| Index picker | Short titles, selection, mode applicability, and accessibility identifier. |
| Maximum controls reached | canAddControl returns false; app avoids exception and chooses a fallback. |
| Controls active | App hides distracting UI and leaves the viewfinder readable. |
| Controls fullscreen | App restores UI only after controls become inactive. |
| Photo mode versus video mode | Irrelevant controls disabled or replaced with valid values. |
| Format change | System sliders update their device-recommended ranges. |
| Camera Control press phases | Begin, end, and cancel produce correct capture state. |
| Event disabled | Hardware defaults behave normally when the app cannot respond. |
| Background/inactive app | Events are not expected; app does not claim capture occurred. |

## Content and importer evidence

For each session content directory, record:

- directory URL and session provenance;
- initial/added/removed event;
- file names and media types;
- final file size and readability;
- source ID assigned by the containing app;
- durable destination;
- review state;
- invalidation result;
- duplicate handling result.

Test the importer as a state machine:

    unknown directory -> discovered -> validating -> copying -> imported -> reviewable -> invalidated

Side states:

    malformed
    missing
    alreadyImported
    copyFailed
    invalidationFailed
    appNotAuthenticated
    extensionEnded

The importer must be safe to restart. A process kill between copy and record creation must not create an ambiguous duplicate or delete the only copy.

## Privacy and security matrix

| Claim | Fixture | Evidence |
| --- | --- | --- |
| No network in locked extension | Instrumented extension route and attempted network call | Operation unavailable/fails as documented; no media upload occurs. |
| No App Group shared-container access | Extension test path | Access fails/does not exist; content uses sessionContentURL or PhotoKit route. |
| No private data on lock screen | Locked screenshot/task run | No account name, library record, transcript, or sensitive label leaks. |
| Unlock before private review | Handoff and auth failure | Review/account/network actions remain in containing app. |
| AppContext is least privilege | Serialization fixture and size/field audit | Only non-sensitive bounded configuration is included. |
| Temporary content is deleted | Durable import then invalidate | Directory removed and app retains intended source copy. |

## Accessibility and design evidence

Run the tasks from both the extension and app:

- identify Ready/Recording/Paused/Unavailable;
- capture a photo with touch;
- capture a photo with the hardware event;
- start/stop movie;
- discard;
- continue to app;
- review imported media;
- accept/edit/reject AI proposal;
- share finalized content.

Vary:

- Dynamic Type sizes and long localized labels;
- VoiceOver;
- Voice Control;
- Switch Control and Full Keyboard Access;
- Reduce Motion;
- Reduce Transparency;
- Differentiate Without Color;
- portrait and landscape;
- right-to-left language;
- low-light preview and high-contrast content.

The Camera Control overlay is system-owned, but the app’s state and extension UI must still expose equivalent semantic labels and a touch path.

## Release evidence packet

Do not call the route release-ready until the packet contains:

1. Selected SDK/deployment target and supported device list.
2. Main app, control extension, and capture extension archive inspection.
3. Camera/microphone privacy strings.
4. CameraCaptureIntent target membership and AppContext fixture.
5. Physical locked/unlocked entry results.
6. Camera Control controls and event results.
7. Session-directory import/invalidation results.
8. Authentication/error/fallback results.
9. Accessibility and reduced-effects task results.
10. Review/AI/export proof after unlock.
11. TestFlight or release-build run when distribution behavior is in scope.

## Sources

- [LockedCameraCapture](https://developer.apple.com/documentation/LockedCameraCapture)
- [Creating a camera experience for the Lock Screen](https://developer.apple.com/documentation/LockedCameraCapture/Creating-a-camera-experience-for-the-Lock-Screen)
- [LockedCameraCaptureSession](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracapturesession)
- [LockedCameraCaptureManager](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracapturemanager)
- [sessionContentURL](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracapturesession/sessioncontenturl)
- [Enhancing your app experience with the Camera Control](https://developer.apple.com/documentation/avfoundation/enhancing-your-app-experience-with-the-camera-control)
- [AVCaptureControl](https://developer.apple.com/documentation/avfoundation/avcapturecontrol)
- [AVCaptureSession controls](https://developer.apple.com/documentation/avfoundation/avcapturesession/controls)
- [Adding a control to a capture session](https://developer.apple.com/documentation/avfoundation/avcapturesession/addcontrol%28_%3A%29)
- [AVCaptureEventInteraction](https://developer.apple.com/documentation/avkit/avcaptureeventinteraction)
- [AVCaptureEvent](https://developer.apple.com/documentation/avkit/avcaptureevent)
- [onCameraCaptureEvent](https://developer.apple.com/documentation/swiftui/view/oncameracaptureevent%28isenabled%3Adefaultsounddisabled%3Aaction%3A%29)
- [CameraCaptureIntent](https://developer.apple.com/documentation/appintents/cameracaptureintent)
- [Creating controls to perform actions across the system](https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system)
- [Camera Control](https://developer.apple.com/design/human-interface-guidelines/camera-control)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
