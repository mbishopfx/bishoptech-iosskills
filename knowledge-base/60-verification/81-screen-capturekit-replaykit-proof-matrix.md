# ScreenCaptureKit and ReplayKit proof matrix

This matrix prevents a screen-capture feature from being declared complete because a picker appeared, a stream object initialized, or a local file was written. Screen capture crosses OS availability, system consent, media timing, privacy, background configuration, AI, accessibility, and release boundaries.

## Evidence ladder

| Level | Evidence | What it can prove | What it cannot prove |
| --- | --- | --- | --- |
| Source | Current Apple page and exact SDK notes | Documented API intent and deprecation/availability clues | The chosen target’s compile/runtime behavior. |
| Compile | Named Xcode target, SDK, warnings, target membership | Symbols, imports, entitlements, privacy configuration, deprecation state | Physical screen/audio behavior or system consent. |
| Fixture | Synthetic sample buffers, status/error mapping, artifact cases | Deterministic state and media-contract behavior | Real picker/device availability. |
| Simulator | UI state and accessibility automation where supported | Layout, labels, navigation, deterministic fallback | Physical screen capture, microphone routes, thermal behavior, system picker guarantees. |
| Signed device | Physical target with Release-like configuration | Capture, audio, storage, interruptions, frame pacing, device availability | App Store/production service behavior. |
| System surface | Picker, Photos, ShareLink, permission, background, extension run | Real user-mediated handoff and system-owned behavior | All devices, locales, or future OS versions. |
| Release | Archive, signing, entitlements, TestFlight/App Store path | Distribution configuration and artifact membership | Universal hardware or production success without monitoring. |

## Claim matrix

| Claim | Required evidence | Failure cases |
| --- | --- | --- |
| ScreenCaptureKit route is valid for iOS 26 | Exact SDK/deployment compile plus intended iOS 26 physical-device run; record any current sample’s newer minimum | A newer iOS sample, framework import, or simulator run alone. |
| Person can choose the requested source | System picker presentation, selection, cancellation, source-change, and returned filter evidence | Custom picker screenshot or assumed window list. |
| Stream produces usable screen frames | `SCStream` start, `SCStreamOutput` callbacks, sample timing/status inspection, bounded handoff | Stream object creation or a single static preview. |
| Audio/microphone choice is honored | Picker/configuration state, authorization, `SCStreamOutputType` lane, audio session/route evidence | Microphone icon state without a recorded audio track. |
| Stream stops safely | User stop, system stop, cancellation, delegate error, and teardown run | Button action completing without finalization proof. |
| Recording is a valid artifact | Recording delegate finish, file readability/metadata, duration/size, playback and retention inspection | Temporary URL or nonzero file size. |
| Photos/share handoff works | Separate permission and destination run, success/failure receipt, recovery path | File exists in app sandbox. |
| AI review is correctly sourced | Source revision, media timestamp, model/version, confidence, stale/cancelled fixtures, human review | Model output displayed without source interval or approval state. |
| Privacy contract is visible | Preflight copy, system consent, source disclosure, recording indicator, deletion/retention run | A usage description alone. |
| Accessibility task is complete | VoiceOver, Dynamic Type, Reduce Motion, Voice Control, keyboard/pointer/Switch Control as applicable, task-based result | Accessibility audit output alone. |
| Performance is acceptable | Physical frame pacing, queue/drop metrics, memory, storage, CPU/GPU/energy/thermal observations in Release-like build | Debug preview, newest device, or average FPS without workload. |
| Distribution is ready | Signed archive, target membership, entitlements, background modes, privacy strings, TestFlight/system run | Successful local Debug build. |

## Target and availability fixture pack

Create a record for every target:

```text
target name
bundle identifier
deployment target
SDK/Xcode version
ScreenCaptureKit symbols and warnings
ReplayKit symbols and warnings
background modes
privacy usage descriptions
entitlements
device model and OS
result: available | fallback | unavailable | blocked
```

The fixture must include the case where Apple’s current iOS ScreenCaptureKit sample requires iOS 27 while the product target is iOS 26. The expected result is a deliberate capability state, not an inferred success or failure.

## Picker and consent fixtures

- picker presents and returns a display/app-owned filter;
- picker presents and the person cancels;
- observer registers too late and the coordinator recovers or reports a setup error;
- person changes selected source while stream is active;
- microphone enabled, denied, revoked, or unavailable;
- camera toggle selected where the target exposes it;
- another recorder or system route is active;
- system screen-recording permission is declined;
- source disappears or no display/window list is available;
- custom picker path is rejected in review because system picker is required.

## Stream and buffer fixtures

Use deterministic records for:

- first `started` frame;
- `complete` frame with valid presentation time and attachments;
- `idle`, `blank`, `suspended`, and `stopped` frame status;
- missing or malformed frame attachment;
- screen, app-audio, and microphone output lanes;
- monotonic and discontinuous timestamps;
- bounded queue full condition;
- latest-frame replacement/drop policy;
- cancellation while a model task is pending;
- output callback after coordinator shutdown;
- stream delegate stop with user cancellation, system stop, and configuration error.

The expected result for each fixture must name whether the buffer is dropped, projected, retained, finalized, or surfaced as a user-visible state.

## Artifact and finalization fixtures

| Fixture | Expected evidence |
| --- | --- |
| Stop while recording | Stream stop, recording-output finish, readable file, durable artifact record. |
| Stop before any complete frame | No misleading “saved recording” state; clear empty/incomplete outcome. |
| Disk full | Recording failure, preserved diagnostic, cleanup/retry path. |
| Output file type unavailable | Configuration failure before start or explicit fallback. |
| Recording delegate failure | No Photos/share/AI handoff until a valid artifact exists. |
| Photos permission denied/limited | Artifact remains reviewable; destination state is separate. |
| Share cancelled | Artifact remains; no false “shared” receipt. |
| Temporary file cleanup | Retention policy runs without deleting user-selected durable output. |

## AI and review fixtures

- model unavailable on the device;
- model asset not installed or language unsupported;
- low-confidence result;
- result references an interval from an older capture revision;
- source artifact deleted before analysis completes;
- model task cancelled during a frame handoff;
- transcript/label generated successfully but user rejects it;
- typed proposal approved once and retried to verify idempotency;
- AI result would trigger an external side effect and is held for explicit confirmation;
- local-only analysis path versus later user-initiated share/upload.

## Accessibility and native-design fixtures

Run the complete task under:

- VoiceOver with the capture source, active state, stop control, review, and proposal;
- largest supported Dynamic Type sizes;
- Increase Contrast and Reduce Transparency;
- Reduce Motion;
- Voice Control and keyboard/pointer input;
- landscape/portrait and split/resized contexts where supported;
- localized strings with long source names and error messages;
- dark/light appearance over bright and dark captured content.

Record whether the system picker, app shell, preview, and review card each remain understandable. Do not treat a static screenshot as proof of reading order or physical usability.

## Physical and release evidence

For the intended device matrix, record:

```text
device model / OS
screen source kind
audio route and microphone state
foreground/background transition
interruption or phone-call simulation where permitted
frame interval / drops / queue depth
memory / CPU / GPU / energy / thermal observation
artifact size / duration / playback
Photos/share result
AI result and review action
accessibility settings used
build configuration / signing / entitlements
```

If a route is unavailable on iOS 26, the evidence should show the fallback state and alternative workflow rather than a green check for an untested path.

## Verification record template

```text
Route: ScreenCaptureKit | ReplayKit compatibility | screenshot | import | AVFoundation
Target: <named target>
SDK/deployment: <exact values>
Device/OS: <exact values>
Source selection: <picker result or fallback>
Consent: <screen/audio/camera result>
Stream lifecycle: <start/output/inactive/stop/finalize>
Media evidence: <timing/status/format/drop record>
AI evidence: <model/version/source revision/review>
Accessibility evidence: <settings and task result>
Release evidence: <archive/entitlements/target membership>
Result: pass | fallback | blocked | fail
Open evidence: <what remains unproven>
```

## Sources

- [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit)
- [Capturing screen content on iOS](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-on-ios)
- [SCContentSharingPicker](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpicker)
- [SCContentFilter](https://developer.apple.com/documentation/screencapturekit/sccontentfilter)
- [SCStream](https://developer.apple.com/documentation/screencapturekit/scstream)
- [SCStreamConfiguration](https://developer.apple.com/documentation/screencapturekit/scstreamconfiguration)
- [SCStreamOutput](https://developer.apple.com/documentation/screencapturekit/scstreamoutput)
- [SCStreamDelegate](https://developer.apple.com/documentation/screencapturekit/scstreamdelegate)
- [SCFrameStatus](https://developer.apple.com/documentation/screencapturekit/scframestatus)
- [SCStreamError](https://developer.apple.com/documentation/screencapturekit/scstreamerror)
- [ScreenCaptureKit error constants](https://developer.apple.com/documentation/screencapturekit/error-constants)
- [SCRecordingOutput](https://developer.apple.com/documentation/screencapturekit/screcordingoutput)
- [ReplayKit](https://developer.apple.com/documentation/replaykit)
- [RPScreenRecorder](https://developer.apple.com/documentation/replaykit/rpscreenrecorder)
- [RPBroadcastSampleHandler](https://developer.apple.com/documentation/replaykit/rpbroadcastsamplehandler)
- [Core Media](https://developer.apple.com/documentation/coremedia)
- [CMSampleBuffer](https://developer.apple.com/documentation/coremedia/cmsamplebuffer)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [XCTest performance tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
