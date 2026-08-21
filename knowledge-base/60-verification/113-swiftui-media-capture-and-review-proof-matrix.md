# SwiftUI media capture and review proof matrix

## Purpose

Use this matrix for any claim involving PhotosPicker, PhotoKit media access,
Transferable import, custom camera capture, AVCaptureSession,
AVCapturePhotoOutput, live preview, AVKit review, Image I/O metadata,
Vision/Core ML observations, Foundation Models review, Liquid Glass capture
controls, or an explicit save/export destination.

Record the following for every run:

- app/build, Xcode, SDK, deployment target, target membership, and platform;
- source kind, source ID, source revision, capture ID, selection generation, and
  representation type;
- content type, byte count, dimensions, orientation, duration, color, metadata
  policy, and derived-file identity;
- camera/microphone/photo-library authorization status and the processed usage
  descriptions;
- session owner, inputs, outputs, session queue, preview layer/player
  identity, orientation, interruption, route-change, and teardown state;
- transfer task, cancellation, iCloud/offline result, file copy, cleanup, and
  failure classification;
- Vision/Core ML request type, revision, model identifier, input region,
  coordinate transform, confidence, and observation source revision;
- Foundation Models availability, structured input, candidate ID, candidate
  revision, stale state, validation, review action, and commit result;
- destination choice, app file/record ID, export type, Photos authorization,
  change/add result, and recovery state;
- locale, layout direction, Dynamic Type, Bold Text, contrast, transparency,
  motion, VoiceOver, Voice Control, keyboard, pointer, Pencil, and camera
  control state;
- artifact path, test date, physical device/target identity, tester, and
  whether the evidence is static, simulated, or live.

A screenshot proves a visual fixture. It does not prove that a picker item
transfers, a camera is authorized, a session starts, a file survives, a model
result is current, or a save reaches the intended destination.

## Evidence levels

| Level | Can support | Cannot support alone |
| --- | --- | --- |
| Official source | API intent, platform contract, and HIG guidance | This app's implementation |
| Static route review | Ownership, state transitions, destination policy | Runtime capture, permissions, system UI |
| Named-target compile | Imports, availability, protocol/signature, target membership | Physical camera, picker, playback, model readiness |
| Unit/fixture test | IDs, revisions, parsing, metadata policy, candidate staleness | Camera hardware, system picker, VoiceOver feel |
| Preview | Loading/error/review hierarchy and labels | Live session, real transfer, system Writing/Photos surfaces |
| UI test | Labels, navigation, review actions, ordinary mock states | Camera hardware, iCloud, Photos changes, device-only AI |
| Simulator | Layout, localization, keyboard simulation, many lifecycle fixtures | Real camera/mic, hardware controls, actual model readiness |
| Signed physical target | Camera/mic, picker, playback, accessibility, device model state | App Store distribution or every device/OS |
| System-surface run | PhotosPicker, permission prompts, AVKit controls, share/Photos routes | Universal correctness and release metadata |
| Performance run | Decode, transfer, preview, inference, playback, memory, thermal behavior | Correctness of every source or target |
| Archive/release artifact | Processed usage descriptions, target membership, entitlements, signing | A completed media task or user-visible quality |
| TestFlight/release smoke | Signed build on selected devices and destinations | Universal correctness or production health |

## Fixture contract

Use deterministic fixtures for import, capture, review, model, and destination
states. A fixture should be inspectable without requiring a live camera.

~~~swift
struct MediaProofFixture: Hashable, Sendable {
    let target: String
    let sourceKind: String
    let sourceID: String
    let sourceRevision: Int
    let selectionGeneration: Int
    let contentType: String
    let representation: String
    let byteCount: Int64?
    let pixelSize: String?
    let orientation: String?
    let durationSeconds: Double?
    let permissionState: String
    let transferState: String
    let captureState: String
    let previewState: String
    let metadataPolicy: String
    let observationState: String
    let modelRevision: String?
    let reviewState: String
    let destinationState: String
    let localeIdentifier: String
    let layoutDirection: String
    let dynamicType: String
    let accessibilityModes: [String]
}
~~~

Minimum fixture families:

- picker empty, one item, many items, reordered items, cancelled selection,
  unsupported type, iCloud unavailable, deleted item, and transfer failure;
- small photo, large photo, HEIC/JPEG/PNG where supported, orientation variants,
  alpha, wide color, malformed bytes, and metadata-bearing source;
- short video, long video, audio/no-audio, interrupted recording, partial file,
  unsupported codec, and playback failure;
- camera authorization requesting, authorized, denied, restricted, and changed
  in Settings;
- session idle, configuring, running, interrupted, runtime error, stopping,
  stopped, and deallocated;
- preview loading, live, rotated, mirrored, cropped, obscured, safe-area
  collision, and unavailable;
- observation unavailable, running, partial, complete, cancelled, failed,
  low-confidence, out-of-bounds, and stale;
- AI candidate absent, generating, partial, malformed, stale, accepted,
  edited, rejected, committed, and commit-failed;
- destinations app, export, Photos add-only, Photos limited, Photos denied,
  change-confirmation, discard, and cleanup-failed;
- iPhone narrow/wide, iPad split view, Catalyst, large Dynamic Type, RTL,
  reduced transparency, reduced motion, high contrast, VoiceOver, keyboard,
  pointer, and Pencil where supported.

## PhotosPicker selection and transfer matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Picker presents | Named-target UI/system run | Empty selection, cancel, target availability | The intended picker and filter appear |
| Selection is a placeholder | Static route review plus transfer fixture | Item selected but no bytes loaded | UI does not claim a decoded original prematurely |
| One item loads | Physical/system run plus fixture | Large file, iCloud, unsupported representation | Transfer reaches app-owned review state |
| Multiple items load deterministically | UI/integration run | Completion out of order, duplicate IDs, cancel | Display order and item identity remain stable |
| A new selection supersedes old work | Async/unit/UI run | Late completion, rapid changes | Old task cannot overwrite current source |
| Cancellation is safe | Async/UI run | Dismissal, navigation, scene loss | No late error or file appears in the new review |
| Transferable representation is valid | Named-target compile plus import run | Type mismatch, empty file, size limit | Imported type and file are validated |
| Temporary file is owned safely | File fixture/integration run | Cleanup, relaunch, background | Review does not depend on an expired temporary URL |
| iCloud/offline failure is legible | Device/system run | Network off, optimized storage | User can retry or choose another source |
| Picker-only flow is honest | Permission/system run | No Photos read authorization | UI does not request unnecessary access |
| Limited access is explained | Physical/system run | Limited selection, changes in Settings | Available scope and next action are clear |

## Import representation and file lifetime matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Content type is recorded | Unit/import fixture | Generic item, missing type, subtype | Review and export use the recorded type |
| File representation avoids avoidable memory growth | Performance run | Large photo/video, cancellation | Peak memory and copy time are recorded |
| Data representation is bounded | Unit/performance run | Large bytes, malformed data | Size is checked before decode |
| Image decoding preserves orientation | Image fixture/visual run | Portrait EXIF, mirrored, wide color | Rendered orientation matches expected fixture |
| Video duration is correct | AVAsset fixture/system run | Variable frame rate, no duration | Playback/review uses a verified duration |
| Derived file identity is new | Static/integration test | Thumbnail, crop, transcode, redaction | Source is not silently replaced |
| App copy survives review | Relaunch/integration run | Background, scene loss, cleanup | App-owned file can be reopened or fails clearly |
| Export representation is explicit | Export/system run | HEIC/JPEG/MOV/share cancel | Type, quality, and destination are visible |
| Metadata policy is applied | Image I/O fixture/export run | GPS, device, time, unknown keys | Intended keys are preserved/redacted and verified |
| Cleanup is recoverable | Failure/termination test | Disk full, interrupted copy | Orphaned derived files are identified and handled |

## Camera authorization and session matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Camera usage description is processed | Archive inspection | Missing key, wrong target, localized value | Built app contains the intended description |
| Microphone usage description is processed | Archive inspection | Video/audio target split | Built target contains only required copy |
| Authorization request is explicit | Physical/system run | First launch, cancel, denial | Prompt follows user intent and state updates |
| Denied camera is safe | Physical/system run | Denied, restricted, Settings change | No active-looking black camera surface |
| Picker fallback works | UI/physical run | Camera unavailable, no permission | Existing-media route completes |
| Session graph is configured once | Static/instrumented run | SwiftUI redraw, navigation, retake | One owner controls inputs/outputs |
| Inputs/outputs are capability-checked | Named-target compile/runtime | Missing camera, no audio, unavailable output | Unsupported route becomes an honest state |
| Configuration is atomic | Instrumented integration run | Add/remove device, interruption | Partial graph is not exposed as ready |
| Start/stop occur off the view body | Static/concurrency review | Recomposition, scene transitions | Session lifecycle follows explicit intent |
| Session queue is serialized | Concurrency/instrumented run | Rapid start/stop, retake | No race or duplicate start/stop |
| Runtime error recovers or fails clearly | Physical/system run | Media services reset, route error | User gets retry/fallback and no stale capture button |
| Interruption is visible | Physical run | Call, camera use, audio interruption | Preview and controls explain paused state |
| Background policy is safe | Physical lifecycle run | Home, lock, scene inactive | Capture stops or follows documented supported design |

## Preview and capture matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Preview renders the intended session | Physical run | Session replacement, view recreation | Preview shows current session, not a stale one |
| Preview orientation is correct | Physical rotation run | Portrait/landscape, mirrored front camera | Subject and capture result agree |
| Aspect fill/crop is understood | Visual fixture plus physical run | Subject near edge, model region | UI communicates crop and coordinate transform |
| Safe areas protect the subject | iPhone/iPad visual run | Dynamic Island, notch, split view, keyboard | Overlay does not cover critical content |
| Capture button state is semantic | UI/accessibility run | Configuring, running, recording, denied | Label/value/action reflect actual state |
| Photo settings are recorded | Compile/fixture/device run | Flash, high resolution, Live Photo | Capture result records settings and capability |
| Photo output result arrives once | Physical/integration run | Cancel, error, duplicate callback | One capture ID yields one final review state |
| Photo metadata is retained intentionally | Image I/O fixture | Orientation, dimensions, privacy keys | Review shows normalized data without leaking policy |
| Video start/stop is deterministic | Physical run | Short tap, long record, interruption | Final asset has valid duration and state |
| Partial video is handled | Failure/physical run | Termination, disk full, interruption | Partial file is marked or removed |
| Audio route is correct | Physical run | Silent mode, Bluetooth route, mic denial | Audio behavior matches product copy |
| Live Photo/depth features are honest | Capability/physical run | Unsupported target/device | Feature is hidden or explained, not assumed |
| Retake invalidates prior work | Async/UI run | Model request in flight, old preview | Old capture/result cannot commit |

## AVKit review matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| VideoPlayer receives a valid player | Named-target compile plus fixture | Missing file, unsupported codec | Review displays playback or clear failure |
| Player lifetime is stable | UI/lifecycle run | Row reuse, navigation, sheet, background | Playback does not reset unexpectedly |
| AVPlayerViewController route is justified | Static/physical review | SwiftUI-only route sufficient | Controller surface adds required behavior |
| Playback controls are discoverable | Physical/accessibility run | VoiceOver, Dynamic Type, landscape | Play/pause/seek/close have labels |
| Review does not mutate source | Static/integration run | Crop, scrub, export | Derived output gets a new identity |
| Playback interruption is handled | Physical/system run | Audio interruption, route change | Resume/stop behavior is documented |
| Video review is not analysis proof | Static/product review | “Detected” overlay, confidence | UI distinguishes playback from observation |
| Background behavior is intentional | Physical lifecycle run | Lock, audio, scene inactive | Player follows supported product policy |

## Image I/O and metadata matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Source properties can be read | Image fixture/unit test | Corrupt data, unknown format | Failure is explicit and non-destructive |
| Thumbnail is not original | Static/state test | Low-resolution preview, zoom | UI does not export thumbnail as original |
| Orientation is normalized once | Fixture/visual test | EXIF orientation variants | No double rotation on review/export |
| Dimensions are recorded | Fixture test | Huge dimensions, integer overflow | Memory policy sees real dimensions |
| Metadata keys are classified | Unit/security test | GPS, device, time, custom keys | Preserve/redact decisions are explicit |
| Destination writer applies policy | Export fixture/system run | HEIC/JPEG, unknown properties | Output inspection matches policy |
| Color interpretation is considered | Physical/visual/performance run | Wide color, HDR where supported | Review/export does not silently misrepresent color |
| Thumbnail generation is bounded | Performance run | Large source, many assets | Time/memory evidence is recorded |

## Vision/Core ML observation matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Request accepts the chosen input | Named-target compile plus fixture | URL/Data/CGImage/CIImage/pixel buffer/sample buffer | Input conversion is explicit |
| Request revision is recorded | Unit/integration test | OS/model revision change | Observation includes revision |
| Orientation is passed correctly | Fixture/physical visual run | Portrait, mirrored, crop | Text/boxes align with content |
| Regions map to displayed media | Geometry fixture/visual run | Aspect fill, letterbox, rotation | Overlay coordinates are demonstrably correct |
| OCR output is source-scoped | Unit/UI run | Partial text, no text, language | Text result links to source revision/region |
| Core ML model is optional | Device/availability fixture | Model unavailable, load failure | Core media task remains usable |
| Confidence is not truth | Static/UI review | Low confidence, threshold, unknown | Copy and actions expose uncertainty |
| Partial observations are safe | Async/UI run | Cancellation, supersession | Partial result cannot commit as complete |
| Model input is privacy-scoped | Static/security review | Metadata, full-res vs thumbnail | Only intended pixels/data are processed |
| Performance is acceptable | Physical performance run | Long video, repeated frames, thermal | Latency, memory, and cancellation are recorded |

## Foundation Models review matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Capability is optional | Availability/device fixture | Unsupported hardware/settings | Feature falls back to deterministic copy |
| Input is structured and bounded | Static adapter review | Long OCR, many labels, sensitive metadata | Only allowed observations are sent |
| Candidate has source revision | Unit request/response test | Edit during generation | Candidate becomes stale after source change |
| Candidate is typed/validated | Schema/fixture tests | Empty, huge, malformed, unsafe tags | Invalid output is rejected before UI/commit |
| User can review candidate | Physical/accessibility run | Partial, refusal, no-op, stale | Source, proposal, and actions are distinct |
| Cancellation is safe | Async/lifecycle test | Navigate away, retake, scene loss | No late callback mutates the next source |
| Commit follows ordinary app path | Integration/save test | Serialization, conflict, Photos failure | AI never bypasses destination/permission logic |
| Privacy copy is accurate | Static/UI review | On-device state, logs, telemetry | User-facing promise matches implementation |

## Destination and Photos matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| App save is distinct from Photos save | UI/static/integration | Same asset, derived asset | Destination is visible before action |
| App file reopens | Integration/relaunch test | Migration, missing file, conflict | Saved media and review state recover |
| Export is cancellable | System/UI run | Share dismissal, invalid type | No false success state |
| Photos add request is authorized | Physical/system run | Add-only, denied, restricted | Prompt and outcome are clear |
| Limited Photos access is safe | Physical/system run | Limited selection, Settings change | App shows available scope and fallback |
| Photos change is confirmed | Physical/system run | Original vs derived, cancel | Mutation is explicit and result is reported |
| Save failure is recoverable | Integration/system run | Disk full, Photos failure, permission change | Source remains intact and retry is possible |
| Discard cleans up | Integration/failure test | Tasks, temp files, partial export | No stale action or unowned derived file remains |

## Liquid Glass and interaction matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Glass group has task meaning | Design review plus preview | Decorative full-screen glass | Each group maps to a named task |
| Media remains primary | Light/dark physical visual run | Bright/dark source, controls, zoom | Controls do not obscure subject |
| Capture state is semantic | UI/accessibility run | Recording, denied, interrupted | Text/value/action are not color-only |
| Review status is distinct | Fixture/visual run | Source, observation, AI candidate | User can tell fact, suggestion, and edit |
| Narrow layouts adapt | iPhone/iPad/Catalyst visual run | Dynamic Type, keyboard, split view | Controls stack or move without collision |
| Reduced transparency works | Physical settings run | Reduce Transparency, contrast | Opaque fallback remains legible |
| Reduced motion works | Physical settings run | Start/stop, review transition | No required animation conveys state |
| Symbols are understandable | Accessibility/system run | Unfamiliar icon, VoiceOver | Label/value/hint clarify icon actions |
| Camera Control assumptions are bounded | Hardware/target run | Unsupported target | App fallback works without Camera Control |

## Accessibility and alternate input matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Picker entry is labeled | VoiceOver/system run | Multi-selection, cancel | Selection count and current item are announced |
| Camera state is announced | VoiceOver/physical run | Permission, interrupted, recording | Current state and next action are discoverable |
| Preview has useful semantics | VoiceOver/design review | Decorative preview, captured media | Subject/source is described without noisy duplication |
| Capture/retake/review actions work | VoiceOver/UI run | Disabled, loading, stale | Actions expose why unavailable |
| Video controls are reachable | VoiceOver/physical run | Seek, playback, close | AVKit/system controls remain usable |
| AI uncertainty is audible | VoiceOver/UI run | Low confidence, stale, refusal | “Suggestion” is not announced as fact |
| Keyboard route works | iPad/Catalyst physical run | Commands, focus, escape, return | Core task completes without touch |
| Pointer route works | iPad/Catalyst physical run | Hover, context menu, drag | Controls have pointer affordance where useful |
| Dynamic Type does not cover media | Physical visual run | Largest sizes, landscape | Labels and actions remain reachable |
| RTL is correct | Physical/UI run | Mirrored controls, text/boxes | Directional controls and regions remain correct |

## Target, performance, archive, and release matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| iPhone capture works | Signed physical iPhone run | Camera, mic, rotation, thermal | Artifact names device/OS/build and result |
| iPadOS route works | Signed physical iPad run | Split view, keyboard, pointer | Target-specific layout/input proof |
| Catalyst route works | Named-target compile plus Mac run | File import, menus, AVKit | Unsupported camera features are honest |
| visionOS/watchOS projection is safe | Named-target compile/review | Missing APIs, companion route | No iPhone-only route is claimed |
| Long media is bounded | Physical performance run | Large photo/long video | Memory/latency/thermal evidence |
| Repeated analysis is cancellable | Performance/async run | Rapid retake, many frames | Work does not accumulate unboundedly |
| Processed usage descriptions are present | Archive inspection | Wrong target/configuration | Built artifact contains intended keys |
| Entitlements/privacy are correct | Archive/static review | Photos, camera, microphone, extensions | No unneeded capability is shipped |
| Release build behaves like debug | Release physical run | Optimization, file access, model loading | Signed release completes fixture task |
| TestFlight smoke succeeds | TestFlight physical run | Install, update, restore | Selected path works in distributed build |

## Required artifact set

For a serious media feature, keep:

1. a named-target compile result for every claimed SDK surface;
2. deterministic import, metadata, model, candidate, destination, and failure
   fixtures;
3. a simulator/preview capture for layout and accessibility state coverage;
4. physical iPhone/iPad evidence for camera, picker, playback, permissions,
   alternate input, and device-only model claims;
5. archive evidence for processed usage descriptions, entitlements, target
   membership, and release configuration;
6. a short performance record for representative media sizes and model work;
7. an explicit list of unverified targets and unsupported capabilities.

## Sources

- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [Bringing the Photos picker to your SwiftUI app](https://developer.apple.com/documentation/PhotoKit/bringing-photos-picker-to-your-swiftui-app)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [AVFoundation capture setup](https://developer.apple.com/documentation/avfoundation/capture-setup)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [AVCaptureDevice](https://developer.apple.com/documentation/avfoundation/avcapturedevice)
- [AVCapturePhotoSettings](https://developer.apple.com/documentation/avfoundation/avcapturephotosettings)
- [AVCapturePhotoOutput](https://developer.apple.com/documentation/avfoundation/avcapturephotooutput)
- [AVCaptureVideoPreviewLayer](https://developer.apple.com/documentation/avfoundation/avcapturevideopreviewlayer)
- [AVCam: Building a camera app](https://developer.apple.com/documentation/avfoundation/avcam-building-a-camera-app)
- [AVKit](https://developer.apple.com/documentation/avkit)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [AVPlayerViewController](https://developer.apple.com/documentation/avkit/avplayerviewcontroller)
- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [Vision](https://developer.apple.com/documentation/vision)
- [RecognizeTextRequest](https://developer.apple.com/documentation/vision/recognizetextrequest)
- [CoreMLRequest](https://developer.apple.com/documentation/vision/coremlrequest)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Camera Control HIG](https://developer.apple.com/design/human-interface-guidelines/camera-control)
- [Live Photos HIG](https://developer.apple.com/design/human-interface-guidelines/live-photos)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
