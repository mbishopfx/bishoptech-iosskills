# ScreenCaptureKit compatibility capability route

Use this route when an app needs to record, stream, inspect, or analyze screen content on iOS 26-era targets while preserving an honest fallback when the current ScreenCaptureKit route is unavailable. The route is deliberately adapter-first: ScreenCaptureKit is the preferred investigation, ReplayKit is a quarantined compatibility path, and AVFoundation/import are explicit alternatives rather than silent substitutions.

The [ScreenCaptureKit and ReplayKit stream lifecycle](../42-framework-deep-dives/64-screencapturekit-and-replaykit-stream-lifecycle.md) explains the API graph. The [screen-capture trust and review design](../21-design-deep-dives/84-screen-capture-trust-and-review-design.md) defines the native shell. The [proof matrix](../60-verification/81-screen-capturekit-replaykit-proof-matrix.md) defines evidence, and the [recipes](../70-code-recipes/99-screen-capturekit-replaykit-recipes.md) show uncompiled route sketches.

## Route decision

| Desired outcome | Route | Fallback |
| --- | --- | --- |
| Person chooses a display/app/window and the app receives timed frames | ScreenCaptureKit picker + `SCStream` | App-owned camera/import route, or ReplayKit only if the exact target proves it is still usable. |
| One screenshot for visual intelligence | ScreenCaptureKit screenshot API | App-owned rendered snapshot or user-selected image. |
| App-scoped recording with older deployment constraints | Isolated ReplayKit adapter | Import or in-app AVFoundation capture. |
| Direct finalized movie | ScreenCaptureKit `SCRecordingOutput` where the target exposes and supports it | Explicit buffer-to-AVAsset writer route only if the target and media contract support it. |
| Live on-device AI review | `SCStreamOutput` -> bounded projection -> Vision/Core ML/Speech/Foundation Models | Analyze a finalized artifact or a user-selected frame. |

Never select the route solely from a framework import. The capability state needs compile-time target facts, runtime availability, user authorization/selection, background configuration, and current device state.

## Step 1: create a target-aware capability record

Record the decision before presenting UI:

```text
targetPlatform = iOS
deploymentTarget = exact value from the named target
sdkVersion = exact Xcode/SDK used to compile
screenCaptureKitSymbolSet = compile result
screenCaptureKitRuntime = unknown | available | unavailable | denied
replayKitSymbolSet = compile result
replayKitDeprecation = warning/error record
backgroundConfiguration = signed target evidence
deviceState = supported | unavailable | busy | unknown
```

Apple’s current iOS ScreenCaptureKit sample says it requires iOS 27 or later. Do not translate that into “ScreenCaptureKit cannot exist on iOS 26” or “ScreenCaptureKit definitely works on iOS 26” without the exact SDK and device check. Store the sample’s minimum as a warning and make the target build the authority.

## Step 2: choose the source through the system

For ScreenCaptureKit:

1. configure the shared `SCContentSharingPicker` for the intended capture mode;
2. register an `SCContentSharingPickerObserver`;
3. present the system picker;
4. receive the returned `SCContentFilter`;
5. record the selected source revision;
6. create a stream configuration and stream;
7. attach output/recording destinations before starting capture.

The app can describe the mode before the picker and the selected result afterward. It should not build a custom list of private windows or displays as a replacement for Apple’s picker.

## Step 3: write the media contract

Define this before choosing configuration values:

```text
source: display | app-owned content | window | app camera | imported artifact
video: required | optional
audio: app audio | microphone | both | none
output: preview | AI observation | finalized movie | rolling clip
maximumLatency
dropPolicy
retentionPolicy
color/pixel-format requirement
destination and export policy
```

If the product needs every frame, the route must include a storage and processing budget. If the product needs only current screen state, use a latest-frame policy and record dropped frames as expected behavior.

## Step 4: configure and start a bounded stream

Choose dimensions, frame interval, queue depth, pixel format, color behavior, audio toggles, and microphone behavior from the contract. Use a dedicated coordinator to own:

- picker observer registration;
- stream and output lifetimes;
- serial state transitions;
- bounded sample-buffer handoff;
- cancellation and stop ordering;
- recording-output finalization;
- artifact creation.

The output callback should project the smallest safe record needed downstream. Do not retain arbitrary `CMSampleBuffer` values across unbounded tasks. If a Core Video pixel buffer, audio block buffer, or copied image is the ownership boundary, document it in the coordinator.

## Step 5: handle frame status and errors

Map `SCFrameStatus` and `SCStreamError` to product states:

| Technical observation | Product interpretation |
| --- | --- |
| `complete` | New frame available for the selected output lane. |
| `idle` | No new display change; do not treat it as a failure or duplicate analysis blindly. |
| `blank` | Source produced blank content; preserve privacy semantics and decide whether to skip AI. |
| `started` | First frame boundary; initialize source/timeline state. |
| `suspended` | Updates are suspended; show stale/inactive state. |
| `stopped` | Stream no longer supplies valid new frames. |
| user stopped | Normal cancellation if initiated by the person. |
| user declined | Permission/consent failure with a recovery explanation. |
| missing background mode/entitlement | Configuration failure; do not retry in a tight loop. |
| insufficient storage or failed start/stop | Recovery or artifact failure with retained diagnostics. |

Do not present every technical error string directly to the person. Preserve the raw code in diagnostics and provide a concise recovery state.

## Step 6: add local AI as a reviewable consumer

Use the capture route as an input adapter:

```text
ScreenCaptureKit / ReplayKit / import
  -> CaptureRecord(sourceRevision, mediaTime, status, payload)
  -> local observation
  -> AIReviewProposal(sourceRevision, interval, model, confidence, payload)
  -> person review
  -> typed domain action
```

A model may classify a screen region, extract text, transcribe commentary, summarize a selected interval, or propose an app-owned action. It must not bypass review because the source was screen content or because processing happened on device.

Prefer deterministic pre-processing and typed outputs. Keep model availability, language/model assets, cancellation, memory, and thermal pressure visible. A local model result is a proposal until the user or an explicit product policy approves it.

## Step 7: finalize and hand off

For a direct recording output, wait for the recording delegate’s finish event and inspect the file. For a custom media writer, wait for the writer’s completion and validate duration, readability, and format. Only then:

- save to Photos with the requested permission;
- present ShareLink or a share sheet;
- enqueue AI analysis;
- write a durable app record;
- delete temporary media according to retention policy.

Keep “stopped,” “finalized,” “saved,” “shared,” and “analyzed” as separate state transitions. If a downstream handoff fails, the reviewable artifact should remain recoverable unless the user chose deletion.

## Step 8: provide the fallback honestly

Fallback copy should identify what changes:

```text
Full-display selection is unavailable on this target.
You can record this app only, import an existing recording, or use the camera workflow.
```

If ReplayKit is used, describe it as an app-scoped compatibility route and keep its deprecation state in the build record. If neither route works, disable the action with a useful alternative; never silently start a different source than the one the person requested.

## Step 9: prove the route

The smallest credible proof packet contains:

- named target, SDK, deployment target, and compiler warnings;
- runtime capability record on the intended iOS device;
- system picker selection, cancellation, and source-change run;
- stream start, output, pause/inactive, stop, and error run;
- audio/microphone permission and route-change run if enabled;
- frame-status and drop/backpressure metrics;
- finalized artifact inspection and Photos/share handoff;
- local AI review with stale-source and cancellation fixtures;
- VoiceOver, Dynamic Type, Reduce Motion, and alternate-input run;
- Release build/entitlement/privacy/target-membership inspection.

## Stop conditions

Stop the implementation slice if:

- the selected SDK does not expose the intended API;
- current Apple documentation marks the chosen ReplayKit route deprecated/no longer supported and no compatibility requirement justifies it;
- the iOS 26 deployment target cannot prove the ScreenCaptureKit route;
- the stream needs unbounded retention to meet the product claim;
- a custom picker is being proposed to replace Apple’s system selection surface;
- AI output is being treated as an automatic side effect;
- a recipe would claim device, system, accessibility, or release behavior without matching evidence.

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
- [SCFrameStatus](https://developer.apple.com/documentation/screencapturekit/scframestatus)
- [SCStreamError](https://developer.apple.com/documentation/screencapturekit/scstreamerror)
- [ScreenCaptureKit error constants](https://developer.apple.com/documentation/screencapturekit/error-constants)
- [SCRecordingOutput](https://developer.apple.com/documentation/screencapturekit/screcordingoutput)
- [SCScreenshotManager](https://developer.apple.com/documentation/screencapturekit/scscreenshotmanager)
- [ReplayKit](https://developer.apple.com/documentation/replaykit)
- [RPScreenRecorder](https://developer.apple.com/documentation/replaykit/rpscreenrecorder)
- [RPBroadcastSampleHandler](https://developer.apple.com/documentation/replaykit/rpbroadcastsamplehandler)
- [Core Media](https://developer.apple.com/documentation/coremedia)
- [CMSampleBuffer](https://developer.apple.com/documentation/coremedia/cmsamplebuffer)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
