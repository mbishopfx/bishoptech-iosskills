# Core Media sample-buffer capability route

Use this route when a feature crosses capture/playback/export, timed samples,
audio/video format changes, live AI, or a Metal/Core Image/VideoToolbox handoff.
Start with the high-level framework that owns the user outcome, then add Core
Media for the exact sample, timing, format, queue, or synchronization contract.

## Route decision

| User outcome | Primary route | Add Core Media for |
| --- | --- | --- |
| Capture camera/microphone | AVFoundation | `CMSampleBuffer` timing/format/attachments, bounded handoff, dropped-frame policy |
| Play audiovisual media | AVKit/AVFoundation | Sample timing, format changes, timebase/synchronization, custom render path |
| Decode/encode a codec | VideoToolbox/AVFoundation | Buffer/format/timing contracts and completion boundaries |
| Analyze live media with Vision/Core ML/Speech | Capture + model framework | Selective frame/audio projection, timestamp/provenance, backpressure |
| Render frames in Metal/MetalKit | Metal/MetalKit | Pixel-buffer/sample timing, color/HDR metadata, presentation mapping |
| Export/edit a media asset | AVAsset/AVAssetReader/Writer | Sample timing, format description, copy/transform policy |
| Build a simple SwiftUI visual | SwiftUI/Canvas/Charts | Only use Core Media if the source is actually time-based media |

Core Media is not a general-purpose data queue, file database, or model store.

## Step 1: write the media contract

~~~text
source: camera / microphone / file / decoder / generated media
user outcome:
target/platform/deployment target/SDK:
primary framework owner:
sample type: audio / video / muxed / metadata / tagged
time authority and timestamp meaning:
format description and conversion policy:
readiness/ownership/lifetime policy:
queue capacity/backpressure/drop policy:
discontinuity/format-change recovery:
AI input/output/provenance policy:
render/export destination:
privacy/retention/deletion:
accessibility/fallback:
proof levels required:
~~~

Do not start with a callback signature alone. The pipeline contract must state
what a sample timestamp means and which stage is allowed to drop, copy, hold,
or transform data.

## Step 2: map the pipeline

~~~text
source/session
  -> sample buffer callback or asset reader
  -> readiness/format/timing validator
  -> bounded queue or latest-sample gate
  -> analysis/render/encode stage
  -> reviewable result or destination
  -> durable domain record/export artifact
~~~

At every arrow, record the input/output type, ownership, isolation/queue,
cancellation, and error state. Keep the live object graph out of SwiftData,
Core Data, widgets, App Intents, or system projections.

## Step 3: select the timing policy

Choose the timestamp that drives the product outcome:

| Need | Timing policy |
| --- | --- |
| Display a preview | Presentation time/display clock; document late/drop behavior |
| Synchronize audio/video | Shared clock/timebase and explicit drift/anchor policy |
| Analyze a frame | Source presentation time plus model completion time |
| Decode/reorder | Decode timestamp and codec-specific contract |
| Export | Preserve/transform asset timing according to the writer/container route |
| User annotation | Store source timestamp and app record creation/update time separately |

Validate invalid/indefinite times and define a rounding/timescale policy before
formatting a user-visible value.

## Step 4: select the buffer policy

For live capture or analysis, decide:

- whether each stage retains, copies, or consumes a buffer;
- maximum queue depth/in-flight work;
- whether newest, oldest, keyframe, or every sample is preserved;
- what happens when the downstream stage is slow;
- how a format change/discontinuity flushes work;
- how cancellation releases sample/pixel/audio memory;
- whether data is safe to cross an actor or task boundary.

For a live AI feature, a common policy is “keep the newest eligible sample,
cancel stale inference, preserve source time, and never display a final result
without a valid source revision.” For recording/export, use the route’s required
lossless/ordered policy instead.

## Step 5: validate format and attachments

Before a model/render/encoder accepts a sample, validate:

- media type and subtype;
- sample count and timing entries;
- video dimensions, clean aperture, pixel aspect ratio, orientation/color/HDR;
- audio sample rate, channel layout, packet/format description;
- data readiness and validity;
- attachments/tags needed by the downstream consumer;
- source revision and privacy/retention scope.

Reject or convert an unsupported format deterministically. Do not let a model
or shader silently reinterpret a new format.

## Step 6: add reviewable AI

AI can classify, transcribe, summarize, or propose a derived value. Its input
should be a bounded projection:

~~~text
sample buffer
  -> ready/format/timing check
  -> redacted image/audio/text projection
  -> local model
  -> typed proposal with source time/revision
  -> person review/validation
  -> accepted record or visual configuration
~~~

Store model route/version and source timing with the proposal. A dropped frame,
stale buffer, or ambiguous format must become an explicit unavailable/uncertain
state, not a confident output.

## Step 7: native UI and Liquid Glass

Use a SwiftUI shell for permissions, source state, timeline, review, save,
export, and fallback. Glass can group capture/playback/review actions. Keep
freshness, timestamps, format changes, dropped/late data, privacy, and errors
in readable semantic content. Provide captions/transcripts, static/list
fallbacks, Dynamic Type, VoiceOver, reduced motion/transparency, and alternate
input where relevant.

## Step 8: proof packet

The proof packet should include:

- fixture samples with valid/invalid/indefinite timing;
- readiness/invalid/discontinuity/format-change cases;
- queue capacity, late/drop/backpressure, cancellation, and teardown;
- known pixel/audio formats, attachments, color/HDR/orientation behavior;
- actor/queue/lifetime boundary tests;
- capture/playback/export integration in a named target;
- AI source-time/provenance/review/stale-revision/fallback evidence;
- physical camera/microphone/audio route/display/GPU/device evidence;
- accessibility task and retention/deletion/export review;
- signed Release/TestFlight/archive evidence when claimed.

## Stop conditions

Stop before shipping if:

- a `CMTime` is converted to seconds without invalid/rounding policy;
- a callback sample buffer is held indefinitely or moved across isolation
  without an ownership/sendability plan;
- a queue has no capacity/drop/backpressure policy;
- a format/attachment change is ignored;
- a model result has no source timestamp/revision;
- a preview or simulator is treated as camera/audio/GPU evidence;
- a glass control says “saved” when only a buffer callback completed.

## Sources

- [Core Media](https://developer.apple.com/documentation/coremedia)
- [CMTime](https://developer.apple.com/documentation/coremedia/cmtime)
- [CMSampleBuffer](https://developer.apple.com/documentation/coremedia/cmsamplebuffer)
- [CMBlockBuffer](https://developer.apple.com/documentation/coremedia/cmblockbuffer)
- [CMFormatDescription](https://developer.apple.com/documentation/coremedia/cmformatdescription)
- [CMBufferQueue](https://developer.apple.com/documentation/coremedia/cmbufferqueue)
- [CMTimebase](https://developer.apple.com/documentation/coremedia/cmtimebase)
- [CMClock](https://developer.apple.com/documentation/coremedia/cmclock)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [AVCaptureVideoDataOutputSampleBufferDelegate](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutputsamplebufferdelegate)
- [AVAssetReader](https://developer.apple.com/documentation/avfoundation/avassetreader)
- [AVAssetWriter](https://developer.apple.com/documentation/avfoundation/avassetwriter)
- [Core Video](https://developer.apple.com/documentation/corevideo)
- [CVPixelBuffer](https://developer.apple.com/documentation/corevideo/cvpixelbuffer)
- [Metal](https://developer.apple.com/documentation/metal)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
