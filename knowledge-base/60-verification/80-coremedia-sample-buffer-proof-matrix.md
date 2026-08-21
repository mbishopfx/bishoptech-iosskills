# Core Media sample-buffer proof matrix

Core Media evidence must cover time, format, readiness, memory ownership,
queue behavior, downstream handoff, and physical source behavior. A delegate
callback or sample-buffer object alone is not proof that a frame was current,
processed, rendered, saved, or accessible.

## Evidence ladder

| Level | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| L0 | Official Core Media/AVFoundation source review | Documented object responsibilities and API route | Target configuration or media quality |
| L1 | Deterministic timing/format fixtures | Time math, readiness, format validation, state, and proposal provenance | Camera/microphone/GPU/display behavior |
| L2 | Simulator/preview/UI fixture | Native state, timeline, review, fallback, and accessibility layout | Physical capture, route, timestamps, frame drops, or thermal behavior |
| L3 | Named-target compile/integration run | Capture/playback/export adapter and queue/lifecycle wiring | Device quality, long-session memory, or all formats |
| L4 | Signed physical-device run | Real source, audio/video route, timing observations, interruption, device memory/thermal | Every device/OS and production service |
| L5 | Release/TestFlight/archive evidence | Target resources, signing, privacy/release configuration | Review approval or universal behavior |

## Claim matrix

| Claim | Minimum evidence | False substitute |
| --- | --- | --- |
| Timestamp is current/meaningful | Source clock/timeline, valid `CMTime`, freshness policy, named sample observation | `Date()` at callback time |
| Sample data is ready | `CMSampleBuffer` readiness/validity check and data access result | Object exists |
| Format is supported | `CMFormatDescription` media/subtype/dimensions/audio fields and downstream acceptance | Pixel buffer or audio buffer exists |
| Frame has not been dropped | Capture delegate output/drop callbacks and queue accounting | UI timer or last-result update |
| Buffer handoff is safe | Ownership/lifetime/copy policy and bounded async test | Capturing buffer in a detached task |
| Queue is bounded | Capacity/late/drop/backpressure fixture and memory observation | `CMBufferQueue` compiles |
| Audio/video stays synchronized | Common clock/timebase, drift/interruption test, sample timelines | Matching wall-clock labels |
| AI result describes this input | Source ID/revision/time, format/input record, model result, review state | Model confidence or completion callback |
| Render frame is current | Sample time to display-time mapping and physical presentation observation | Metal command buffer committed |
| Export preserves intended timing | Asset-reader/writer output inspection and playback run | File exists on disk |
| Privacy is complete | Input/attachment/log/share/retention/deletion audit | Microphone/camera permission prompt |
| Accessibility works | Task test with transcript/semantic controls/Dynamic Type/VoiceOver/alternate input | Label on a preview view |

## Fixture pack

| Fixture | Expected observation |
| --- | --- |
| Numeric time with different timescales | Explicit conversion/rounding result |
| Invalid/indefinite/infinite time | Safe pending/error/sentinel branch |
| Nonzero duration/PTS/DTS | Correct display/order/export interpretation |
| Discontinuous timestamp | Flush/reconcile state, no false continuous timeline |
| Ready sample buffer | Valid media access |
| Not-ready sample buffer | Wait/make-ready/error path |
| Data-failed/invalidated buffer | Explicit failure and release/teardown |
| Missing format description | Rejected or route-specific recovery |
| Video format change | Reconfigure/unsupported state; no old-pipeline mix |
| Audio sample-rate/channel change | Reconfigure/route error and user-visible status |
| Required/unknown attachments | Preserve/interpret/redact policy |
| Contiguous block buffer | Direct bounded access path |
| Non-contiguous block buffer | Copy/contiguous conversion policy and memory bound |
| Queue full/late consumer | Drop/backpressure/cadence state |
| Cancellation during inference | Release sample/pixel/audio ownership and no stale commit |
| Source changes during AI | Stale revision rejected |
| Interruption/background/route change | Pause/finish/restart policy |
| No camera/microphone/model asset | Manual/imported/fallback route |

## Timing evidence

Record for every timing-sensitive claim:

~~~text
source and device clock:
CMTime value/timescale/flags/epoch:
presentation/decode/output timestamps:
duration/frame duration:
timebase/clock/rate/anchor:
wall-clock conversion policy:
discontinuity/late/drop behavior:
model completion time, if any:
display/export destination time:
~~~

Compare timelines with documented Core Media operations and explicit rounding.
Do not use a single callback timestamp as proof of synchronization.

## Buffer lifetime and queue evidence

Test the handoff under pressure:

- callback processing slower than source;
- consumer retaining buffers for too long;
- bounded latest-sample or every-sample policy;
- sample copy and release timing;
- cancellation during a block/pixel/audio read;
- queue drain/flush at discontinuity and format change;
- app background/interruption and source shutdown;
- memory peak and recovery after the feature ends.

For a capture source, capture both delivered and dropped samples. For a model
route, record which source sample was analyzed and whether a later result was
discarded as stale.

## Format and metadata evidence

Inspect:

- media type/subtype and immutable format-description identity;
- video dimensions, clean aperture, pixel aspect ratio, orientation, transfer,
  color/HDR metadata, and pixel-buffer format;
- audio sample rate, channel layout, packet descriptions, magic cookie, and
  sample format;
- sample/buffer attachments and tags used by the downstream API;
- format-change behavior and resource reconfiguration;
- redaction before logs, AI, persistence, export, or sharing.

An attachment should be recorded as supplied metadata with a source and
interpretation policy, not as ground truth.

## AI, accessibility, and native-design evidence

Capture:

- source media ID/revision and bounded input fields/frames/audio segments;
- timing/format/readiness validation;
- model route/version/availability and inference cancellation;
- typed output/provenance/evidence, review/edit/reject/accept, stale revision,
  manual fallback, and undo/delete;
- UI tests with status/freshness, transcript/semantic controls, Dynamic Type,
  VoiceOver, reduced motion/transparency, contrast, keyboard/pointer/Voice
  Control/Switch Control where relevant;
- Liquid Glass light/dark/reduced-effects states with readable errors/status;
- raw media/attachment/log/share/retention/deletion review.

## Physical and release evidence

For capture/playback/export/media-to-GPU features, record:

- exact device, OS, build, SDK, camera/microphone/audio route/display;
- permission/locked-data/interruption/route-change state;
- sample drop/late/timing observations and long-session memory/thermal;
- model/language asset and device readiness;
- render/display/export output on a named destination;
- archive target membership/resources/privacy manifest/usage descriptions;
- signed install/relaunch/TestFlight only if claimed.

## Verification record template

~~~text
feature/user task:
target/bundle/build/sdk/deployment target:
source/session/device/clock:
primary framework and Core Media boundary:
CMTime/timestamp/timebase policy:
sample readiness/validity/ownership:
format description/pixel/audio/metadata policy:
queue/backpressure/drop/cancellation:
AI source/proposal/review/fallback:
UI/freshness/accessibility/reduced-effects:
physical source/display/export evidence:
memory/thermal/performance:
archive/privacy/release evidence:
known limits:
claim level: documented / fixture / compile / simulator / device / release
~~~

## Sources

- [Core Media](https://developer.apple.com/documentation/coremedia)
- [CMTime](https://developer.apple.com/documentation/coremedia/cmtime)
- [CMSampleBuffer](https://developer.apple.com/documentation/coremedia/cmsamplebuffer)
- [CMBlockBuffer](https://developer.apple.com/documentation/coremedia/cmblockbuffer)
- [CMFormatDescription](https://developer.apple.com/documentation/coremedia/cmformatdescription)
- [CMBufferQueue](https://developer.apple.com/documentation/coremedia/cmbufferqueue)
- [CMTimebase](https://developer.apple.com/documentation/coremedia/cmtimebase)
- [AVCaptureVideoDataOutputSampleBufferDelegate](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutputsamplebufferdelegate)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [AVAssetReader](https://developer.apple.com/documentation/avfoundation/avassetreader)
- [AVAssetWriter](https://developer.apple.com/documentation/avfoundation/avassetwriter)
- [Core Video](https://developer.apple.com/documentation/corevideo)
- [CVPixelBuffer](https://developer.apple.com/documentation/corevideo/cvpixelbuffer)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing performance](https://developer.apple.com/documentation/xctest/performance-tests)
