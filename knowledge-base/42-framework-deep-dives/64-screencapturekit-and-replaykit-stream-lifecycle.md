# ScreenCaptureKit and ReplayKit stream lifecycle

Screen capture is a privacy-sensitive media pipeline with a system-owned source selector, target-dependent availability, and a different lifecycle from camera capture. The current Apple reference positions ScreenCaptureKit as the high-control route for screen streaming and mirroring, recommends the shared system content picker, and says a broadcast extension is no longer necessary for that route. Apple’s current iOS sample also says it requires iOS 27 or later. For an iOS 26 product, that last fact is a release-planning constraint: compile and run the exact selected SDK and deployment target before treating any ScreenCaptureKit path as available.

This page is the API and lifecycle reference. The [screen-capture capability route](../50-capability-recipes/87-screen-capturekit-compatibility-capability-route.md) is the build worksheet, the [screen-capture trust and review design](../21-design-deep-dives/84-screen-capture-trust-and-review-design.md) is the native visual contract, the [proof matrix](../60-verification/81-screen-capturekit-replaykit-proof-matrix.md) defines evidence, and the [route recipes](../70-code-recipes/99-screen-capturekit-replaykit-recipes.md) are intentionally uncompiled sketches.

## The current Apple route decision

Use the narrowest route that satisfies the outcome:

| Outcome | Preferred investigation | Boundary to record |
| --- | --- | --- |
| Capture a person-selected display or app-owned content with fine-grained video/audio control | ScreenCaptureKit with `SCContentSharingPicker`, `SCContentFilter`, `SCStream`, and `SCStreamOutput` | Exact SDK/deployment availability, system picker behavior, consent, background configuration, and physical-device proof. |
| Capture one frame for OCR, visual understanding, or a preview | ScreenCaptureKit screenshot APIs or an app-owned image source | A single image proves neither a running stream nor a finalized movie. Keep source and timestamp metadata. |
| Record an app-scoped experience with an older compatibility target | ReplayKit `RPScreenRecorder` only after checking the selected SDK’s deprecation and availability state | Current Apple documentation marks the recorder methods deprecated and points to ScreenCaptureKit. Do not build a new product around a historical sample without target-specific evidence. |
| Send a live broadcast to a service | A current, documented ScreenCaptureKit or platform-supported service route | Historical ReplayKit broadcast controllers and sample handlers are deprecated or no longer supported in the current reference. An extension target is not automatically a valid architecture. |
| Capture the camera or microphone for app-owned media | AVFoundation | Camera/microphone permission, route changes, audio session, interruption, and `CMSampleBuffer` ownership are separate from screen recording. |

The adapter must be able to say `unsupported`, `needsPermission`, `pickerCancelled`, `available`, `running`, `stopped`, and `failed`. Avoid a Boolean named `screenRecordingSupported` that collapses OS version, SDK symbol presence, system consent, current device state, and background configuration into one untestable claim.

## The ScreenCaptureKit object graph

The high-control route has a clear ownership chain:

```text
SCContentSharingPicker.shared
        |
        | person chooses source and optional microphone/camera controls
        v
SCContentSharingPickerObserver -> SCContentFilter
        |
        +-> SCStreamConfiguration
        v
SCStream
  |      |\
  |      +-> SCStreamOutput -> CMSampleBuffer -> bounded analysis/render path
  |      +-> SCRecordingOutput -> finalized media artifact
  |      +-> SCStreamDelegate -> active/inactive/stopped/error state
  |
  +-> updateContentFilter / updateConfiguration / stopCapture
```

The system picker owns the privacy-sensitive source selection. The app owns the stream coordinator, its chosen configuration, downstream queues, the durable artifact record, and the review UI. Keep those responsibilities separate so the UI never implies that the system has granted a capability merely because a picker was presented.

## `SCContentSharingPicker` is a system surface

Apple recommends the shared picker instance rather than creating a custom source selector. The picker can present an initial selection surface, present for a running stream, present a style-specific selection, and notify an observer when the selected filter changes. Its configuration can restrict picker modes, exclude app/window identifiers where supported, and allow the person to change the selected content.

Practical rules:

1. Register the observer before presenting the picker so a selection cannot race the coordinator’s setup.
2. Use `SCContentSharingPicker.shared`; do not instantiate a private imitation of the operating-system picker.
3. Treat cancellation as a normal state, not an error banner.
4. Persist the requested capture mode separately from the filter the system returns.
5. Show the returned source in the app’s status surface, but do not reproduce unrelated window lists or private source metadata in a custom UI.
6. If the person changes the selected source, either update the running stream deliberately or stop and rebuild it; never let the old source remain visually implied.
7. Check every beta-marked API in the selected SDK. A current documentation page can expose a symbol without proving the deployment target or final OS behavior you intend to ship.

The current iOS sample demonstrates full-display and in-app picker entry points, but its stated iOS 27 minimum must remain visible in any iOS 26 planning document. Treat the sample as architecture guidance and the target build/device as the availability authority.

## `SCContentFilter` describes what the stream may see

The filter limits stream output to selected displays, windows, applications, or combinations of those sources. It is not a permission grant and it is not a durable identity for a future capture. A source can disappear, become unavailable, or be replaced while a stream is alive.

Record a filter snapshot for each capture revision:

```text
captureRevision
selectedSourceKind
selectedSourceIdentifiers
contentRect
pointPixelScale
streamStyle
microphoneEnabled
cameraEnabled
createdAt
```

Do not serialize private screen content into a model prompt or analytics event merely because it was present in a filter. Store only the minimum source description needed for the user’s review and artifact history.

## `SCStreamConfiguration` is a media and energy contract

The configuration controls output dimensions, source and destination rectangles, scaling, aspect-ratio behavior, pixel format, color handling, frame interval, capture resolution, queue depth, audio capture, microphone capture, process-audio exclusion, and related presentation settings. The right values depend on the outcome:

| Product need | Configuration question | Proof obligation |
| --- | --- | --- |
| OCR or UI understanding | Is the output large enough for the text and stable enough for the model? | Representative text fixtures, recognized-region quality, memory, and thermal observations. |
| Smooth preview | Is the frame interval and queue depth bounded for the device? | Physical frame pacing, drop policy, and cancellation evidence. |
| Final recording | Are pixel format, color, codec, file type, and audio choices compatible with the destination? | Finalized-file inspection, playback, Photos/share handoff, and failure recovery. |
| Microphone commentary | Does the person explicitly control microphone capture and does `AVAudioSession` remain valid? | Permission, route-change, interruption, background, and silent/denied paths. |
| Privacy review | Are unrelated app/window sources excluded and is the capture state conspicuous? | Picker selection, excluded-source checks, visible status, and redaction fixtures. |

`queueDepth` is not a license to retain unlimited frames. More queued frames consume memory and can increase latency. For AI review, prefer a bounded latest-frame or bounded-window policy unless the product truly requires every frame; record which policy was chosen and why.

## `SCStreamOutput` turns frames into a backpressure boundary

After a stream starts, `SCStreamOutput` receives `CMSampleBuffer` values with an `SCStreamOutputType`. Screen, audio, and microphone outputs are different media lanes and must not be treated as interchangeable. The sample buffer carries media timing and the ScreenCaptureKit frame metadata is available through attachments described by `SCStreamFrameInfo`.

The callback should do only bounded work:

```text
receive sample buffer
  -> inspect output type and frame status
  -> project a small timestamped record
  -> retain/copy only the representation the next stage owns
  -> enqueue to a bounded consumer or drop by declared policy
  -> return promptly
```

`SCFrameStatus` distinguishes a complete frame from idle, blank, started, suspended, and stopped states. An idle status is not necessarily a failure: the display may not have changed. A blank frame may be a privacy or source condition. A stopped frame must not be passed to AI as if it were new content.

Use the frame attachments for timing and geometry only after validating their presence and type. Keep the sample buffer’s presentation time, the capture revision, the model-start time, the model-completion time, and the display time as separate values. Converting everything to a `Double` too early loses the ability to reason about invalid, discontinuous, or differently timed media.

## `SCStreamDelegate` owns stream-level transitions

`SCStreamDelegate` reports stream stoppage and other stream-level events such as active/inactive transitions. The delegate is not the source of truth for whether a file is valid or an AI result is approved.

The coordinator should map stream events into explicit domain states:

```text
preparing
running
inactive(reason: systemState)
stopping
finalizing
reviewable(artifact)
cancelled
failed(captureError)
```

When `stream(_:didStopWithError:)` reports a user-stop code, render it as an intentional stop if the person initiated it. Distinguish `userStopped`, `userDeclined`, missing entitlements, missing background mode, storage failure, invalid state, no capture source, and system stop where the current SDK exposes those codes. Do not show an opaque “recording failed” message for a normal cancellation.

## Recording output and artifact finalization

`SCRecordingOutput` is a direct recording output attached to an `SCStream`. Its configuration includes an output URL and file/video choices exposed by the selected SDK; the output reports start, finish, and failure events and exposes recorded duration/file-size information.

The artifact lifecycle is:

```text
reserved temporary URL
  -> recording started
  -> bytes and duration observed
  -> stream stopped
  -> recording output finished
  -> file exists and is readable
  -> media metadata inspected
  -> durable artifact record written
  -> Photos/share/review handoff
```

Do not open Photos, ShareLink, or an AI review job merely because `stopCapture` completed. The media output must finish and be inspected first. If finalization fails, keep the capture record as failed/incomplete and give the person a retry/delete path rather than exposing a broken URL.

For rolling clips, use a bounded clip policy and explicitly define whether the requested duration is wall-clock time, media time, or the last complete interval. If the product exports a clip from a buffer, preserve the source revision and the first/last sample times so AI observations do not drift away from the exported artifact.

## Screenshot routes are not stream routes

`SCScreenshotManager` provides single-frame capture paths. This is a useful fit for a one-shot visual-intelligence action, preview, or OCR request when a running stream would be wasteful. A screenshot path still needs source selection, availability, privacy, and output validation.

Keep these outcomes distinct:

| Result | What it proves |
| --- | --- |
| `CGImage` or image file returned | One image was produced. |
| `CMSampleBuffer` returned | One timed media buffer was produced. |
| `SCStream` active | A stream is producing or attempting to produce outputs. |
| `SCRecordingOutput` finished | A recording output reported completion; inspect the file separately. |
| Photos change succeeded | The user authorized and Photos accepted the requested library mutation. |

## ReplayKit is a compatibility boundary, not a greenfield default

ReplayKit historically provided app recording, app audio, microphone commentary, preview/editing, and broadcast-extension integration. Apple’s current reference marks the recorder’s recording/capture methods deprecated and directs developers toward ScreenCaptureKit. The current reference also marks the broadcast controller, broadcast handler, broadcast sample handler, preview controller, and system broadcast picker surfaces as deprecated or no longer supported.

If an iOS 26 compatibility target still requires ReplayKit, isolate it behind an adapter:

- check the exact SDK and deployment-target availability;
- preserve the deprecation warnings in the build evidence;
- check `RPScreenRecorder.shared().isAvailable` where the target exposes it;
- keep recording app-scoped and respect ReplayKit’s documented limitations, including its inability to record `AVPlayer` content;
- map user confirmation, interruptions, and stop callbacks into the same artifact state machine as ScreenCaptureKit;
- do not add a new broadcast-extension architecture from a historical sample without a current target-specific proof packet.

`RPBroadcastSampleHandler` is especially important to quarantine: Apple’s current page says it is deprecated and no longer supported. A type that remains in an SDK header is not a safe product route.

## Background modes, entitlements, and target configuration

Screen capture that continues while the app is not frontmost needs the appropriate target configuration. Apple’s current iOS sample declares screen-capture and audio background modes; Apple’s Xcode documentation emphasizes selecting only the background modes the app actually requires because they affect battery and system behavior.

For every target, record:

```text
deployment target
selected SDK/Xcode version
framework import/linkage
background modes
camera/microphone/photo usage strings if needed
entitlements or privacy declarations required by the selected route
app target versus extension target membership
Debug versus Release configuration
```

Do not copy a background mode from a newer sample into an iOS 26 target and call the route supported. Verify the generated `Info.plist`, the signed entitlements, and the physical behavior on the intended OS.

## On-device AI handoff

Screen capture is an input source, not an AI feature. A safe local pipeline has typed, reviewable stages:

```text
CMSampleBuffer / finalized media
  -> bounded projection (image/audio/timestamp/source revision)
  -> Vision/Core ML/Speech/Foundation Models observation
  -> confidence and model/version record
  -> user-visible review
  -> optional typed domain proposal
  -> explicit approval
  -> app-owned commit or system handoff
```

For each proposal retain:

- capture revision and artifact identifier;
- source media timestamp and optional frame metadata;
- model/framework/version and device-availability decision;
- deterministic input summary or hash, not an unnecessary copy of private content;
- confidence/uncertainty and “not enough evidence” state;
- generated output separate from approved domain truth;
- cancellation, stale-source, and model-unavailable outcomes.

Never let a transcript, visual label, or Foundation Models output silently trigger a message, file share, purchase, deletion, or external system action. The screen-recording consent is not consent for every later AI or sharing side effect.

## Native Liquid Glass shell

Liquid Glass should clarify the capture task, not camouflage it. Use one dominant capture surface and a small number of functional controls:

- a source/status capsule showing capture mode, selected source, elapsed media time, and microphone state;
- a prominent stop control with a semantic label and a non-gesture path;
- a bounded preview or review panel that can collapse when it competes with the captured content;
- a clear transition from recording to finalizing to reviewable;
- an AI review card that names the source interval, confidence, and proposed action;
- a disabled/unavailable state that explains whether the cause is target support, permission, picker cancellation, or a system stop.

Avoid stacking multiple translucent panels over moving content, hiding the stop action in a morphing control, or using color alone to communicate that capture is active. The system picker remains system-owned; the app’s glass shell should describe the app-owned state around it.

## Proof boundary

The minimum proof packet should include:

1. official-source and SDK availability record;
2. compile result for the named target and deprecation warnings;
3. permission and picker cancellation paths;
4. stream start/output/stop/finalization fixture;
5. frame-status, timestamp, drop/backpressure, and queue evidence;
6. microphone/audio-session and background-mode evidence if used;
7. physical-device screen, audio, storage, thermal, and interruption runs;
8. AI review and stale-source tests;
9. VoiceOver, Dynamic Type, Reduce Motion, Voice Control, keyboard/controller, and contrast checks;
10. Release signing, target membership, entitlements, privacy strings, and artifact inspection.

A preview, a successful picker presentation, a single sample buffer, a local file URL, a model result, or a simulator screenshot proves only that narrow event. It does not prove iOS 26 availability, private-source handling, durable media integrity, system delivery, accessible completion, or release readiness.

## Sources

- [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit)
- [Capturing screen content on iOS](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-on-ios)
- [SCContentSharingPicker](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpicker)
- [SCContentSharingPickerConfiguration](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpickerconfiguration)
- [SCContentSharingPickerObserver](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpickerobserver)
- [SCContentFilter](https://developer.apple.com/documentation/screencapturekit/sccontentfilter)
- [SCStream](https://developer.apple.com/documentation/screencapturekit/scstream)
- [SCStreamConfiguration](https://developer.apple.com/documentation/screencapturekit/scstreamconfiguration)
- [SCStreamOutput](https://developer.apple.com/documentation/screencapturekit/scstreamoutput)
- [SCStreamDelegate](https://developer.apple.com/documentation/screencapturekit/scstreamdelegate)
- [SCStreamFrameInfo](https://developer.apple.com/documentation/screencapturekit/scstreamframeinfo)
- [SCFrameStatus](https://developer.apple.com/documentation/screencapturekit/scframestatus)
- [SCStreamError](https://developer.apple.com/documentation/screencapturekit/scstreamerror)
- [ScreenCaptureKit error constants](https://developer.apple.com/documentation/screencapturekit/error-constants)
- [SCRecordingOutput](https://developer.apple.com/documentation/screencapturekit/screcordingoutput)
- [SCRecordingOutputConfiguration](https://developer.apple.com/documentation/screencapturekit/screcordingoutputconfiguration)
- [SCScreenshotManager](https://developer.apple.com/documentation/screencapturekit/scscreenshotmanager)
- [ReplayKit](https://developer.apple.com/documentation/replaykit)
- [RPScreenRecorder](https://developer.apple.com/documentation/replaykit/rpscreenrecorder)
- [RPScreenRecorderDelegate](https://developer.apple.com/documentation/replaykit/rpscreenrecorderdelegate)
- [RPBroadcastSampleHandler](https://developer.apple.com/documentation/replaykit/rpbroadcastsamplehandler)
- [Core Media](https://developer.apple.com/documentation/coremedia)
- [CMSampleBuffer](https://developer.apple.com/documentation/coremedia/cmsamplebuffer)
- [CMTime](https://developer.apple.com/documentation/coremedia/cmtime)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Dynamic Type](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
