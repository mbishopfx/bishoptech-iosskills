# Screen Capture and Broadcast Proof Matrix

This matrix separates documentation, compilation, simulator behavior, signed-device capture, system delivery, and release evidence. A screen-capture page or a successful local file is not proof of the complete feature.

## Version and target record

Record this before testing:

| Field | Example evidence |
| --- | --- |
| Deployment target | Project setting and built binary |
| SDK/Xcode | Xcode version and SDK build |
| Device OS/build | Settings or device log |
| Device family | Exact iPhone/iPad model |
| Capture adapter | ReplayKit, ScreenCaptureKit, or AVFoundation |
| Deprecation state | Compiler warnings and selected Apple docs |
| Extension targets | Target names, bundle IDs, host process, signing |
| Capabilities/permissions | Entitlements, Info.plist purpose strings, runtime authorization |
| Destination | App container, Photos, Files, ShareLink, service, or server |
| AI configuration | Framework, model asset/version, locale, time range, fallback |

Apple’s current iOS ScreenCaptureKit sample requires iOS 27 or later. If the product targets iOS 26, record the result of the exact SDK availability check and do not infer support from a newer sample.

## Evidence matrix

| Claim | Minimum useful evidence | Does not prove the claim |
| --- | --- | --- |
| The route compiles | Clean build of the named target with the selected SDK | Autocomplete, a copied snippet, or a different deployment target |
| Permission flow works | Fresh install on a signed device, denial and grant runs, purpose strings observed | A normal simulator run or a pre-alert screenshot |
| System picker works | Actual picker presentation, source selection, cancellation, and returned selection on the claimed OS | A custom picker or static preview |
| Capture starts | Device run with observed start callback/state and media samples or recording output | Button animation or a state fixture alone |
| Capture stops | Device run with stop, interruption, cancellation, and finalization evidence | A file URL created before the writer finishes |
| Media is valid | Playback/parse check, duration/codec/container metadata, checksum, and corruption case | File existence or nonzero byte count |
| Microphone/camera state is correct | Runtime authorization, route changes, muted/disabled branch, and recorded media inspection | Assuming an enabled button means audio exists |
| Backpressure is safe | Stress run with queue depth, dropped-frame policy, latency, memory, and thermal observations | A short happy-path recording |
| AI is on device | Build/model configuration and runtime logs that identify the local route, with no unapproved upload | A label that says “private” or a model object that loaded once |
| AI proposal is reviewable | Source ranges, model/version metadata, invalid output, edits, cancel, and approval fixture | Text appearing in a view |
| Photos save works | Authorization state and observed PHPhotoLibrary change result on device | A temporary file or Photos picker selection |
| Share works | Share sheet presentation and selected destination result for the test | A URL passed to ShareLink |
| Extension broadcast works | Signed extension target, host lifecycle, sample-buffer handling, stop/error callback, and destination evidence | Main-app logs or a historical ReplayKit sample |
| Background continuation works | Claimed OS/device run while backgrounding, with mode/configuration and termination cases | Foreground capture or a simulator-only run |
| Accessibility works | VoiceOver task matrix, Dynamic Type, Reduce Motion/Transparency, Voice Control, Switch Control, keyboard/pointer where applicable | A static accessibility inspector tree |
| Release route is configured | Archive inspection, entitlements, extension membership, privacy metadata, and TestFlight run | Debug run or local source configuration |

## Test scenarios

### Permission and source

- Fresh install, camera allowed, microphone allowed, Photos denied.
- Camera denied, microphone allowed.
- Microphone denied while silent capture remains useful.
- User cancels the system picker.
- User changes permission in Settings and returns.
- Unsupported or unavailable capture route.
- Another recorder, AirPlay, or system route is active if applicable.

### Lifecycle

- Start, stop, and immediate stop.
- Background and foreground transition.
- Incoming call or audio interruption.
- Route change, Bluetooth route, and microphone disconnect.
- Low storage and failed output URL.
- Process termination during capture and during finalization.
- Device rotation or size-class change during live UI.
- Thermal pressure or sustained capture.

### Artifact and AI

- Zero-length or very short capture.
- Long recording and rolling clip export.
- A finalized movie with no audio.
- Frame drop or out-of-order timestamp fixture.
- Unsupported language/model unavailable.
- AI cancellation while the user leaves the review screen.
- Invalid typed output or missing source span.
- Edit, discard, retry, and duplicate approval.

### System and accessibility

- VoiceOver starts and stops capture.
- VoiceOver announces microphone/camera state and interruption.
- Dynamic Type at the largest supported size.
- Reduce Motion and Reduce Transparency.
- Voice Control phrases for start, stop, save, discard, and retry.
- Switch Control scan reaches the primary action.
- iPad keyboard and pointer route if the target supports them.
- System picker cancellation returns focus to a meaningful control.

## Performance record

For live capture and analysis, record:

- frame/sample rate and output dimensions;
- queue depth and dropped samples;
- end-to-end latency from capture to visible state;
- memory peak and file growth;
- CPU/GPU/Neural Engine use when measurable;
- temperature or thermal-state changes;
- battery impact for a representative session;
- behavior after an interruption or route change.

Use a bounded design. A feature that looks correct for ten seconds can still be unsafe for a twenty-minute recording.

## Evidence packet

Attach the following to a release candidate:

1. target and SDK record;
2. signed build identifier;
3. permission/purpose-string evidence;
4. capture start/stop/interruption traces;
5. media integrity result;
6. AI evaluation fixture and model/version record;
7. accessibility task results;
8. physical-device photos or screen recording of the actual system route where permitted;
9. extension/entitlement/archive inspection if applicable;
10. known unsupported devices and fallback behavior.

Keep the packet honest: “capture started” is not “broadcast delivered,” “file finalized” is not “saved to Photos,” and “proposal displayed” is not “domain action committed.”

## Sources

- [ReplayKit](https://developer.apple.com/documentation/replaykit)
- [RPScreenRecorder](https://developer.apple.com/documentation/replaykit/rpscreenrecorder)
- [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit)
- [Capturing screen content on iOS](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-on-ios)
- [SCContentSharingPicker](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpicker)
- [AVCam: Building a camera app](https://developer.apple.com/documentation/avfoundation/avcam-building-a-camera-app)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Swift Testing](https://developer.apple.com/documentation/testing)
