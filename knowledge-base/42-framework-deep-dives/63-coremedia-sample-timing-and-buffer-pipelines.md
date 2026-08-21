# Core Media sample timing and buffer pipelines

Core Media is the low-level time-and-buffer layer used by AVFoundation and
other Apple media frameworks. It describes media samples, their format,
timing, readiness, attachments, and queues. It is the layer to understand when
a camera frame, audio sample, video decoder, AI analyzer, Metal renderer, or
exporter must agree about “which data, from when, in what format, and for how
long.”

Use Core Media to define a precise pipeline contract. Do not use it as a reason
to bypass AVFoundation’s capture/session lifecycle, VideoToolbox’s codec
contract, Core Video’s pixel-buffer semantics, Core ML/Vision’s model/input
requirements, or SwiftUI’s state and accessibility model.

The common path is:

~~~text
capture/file/decoder
  -> CMSampleBuffer
  -> CMFormatDescription + CMTime timing + attachments
  -> bounded queue/backpressure
  -> analysis or render proposal
  -> accepted output / playback / export
~~~

## The Core Media object graph

| Type | Responsibility | Product boundary |
| --- | --- | --- |
| `CMTime` | Rational media time with timescale/flags/epoch | Invalid/indefinite/infinite values and rounding must be handled explicitly |
| `CMSampleBuffer` | One or more samples of a uniform media type plus timing/format/attachments | Buffer ownership, readiness, invalidation, and callback lifetime |
| `CMBlockBuffer` | Potentially non-contiguous memory blocks for sample data | Copy/contiguity cost, memory ownership, and safe access |
| `CMFormatDescription` | Immutable description of audio/video/muxed media | Media type/subtype, dimensions, clean aperture, audio format, HDR/codec metadata |
| `CMBufferQueue` | Timed buffer queue with duration/presentation ordering policy | Capacity, readiness, late data, draining, and backpressure |
| `CMTimebase`/`CMClock` | Application-controlled or system-synchronized timeline | Rate, pause, anchor, jumps, and synchronization source |
| `CMAttachment`/sample attachments | Metadata about a sample or stream event | Privacy, propagation, interpretation, and lifetime |
| `CMTag`/tagged buffer groups | Typed tags associated with buffers | Stereo/spatial/projection/view identity and downstream compatibility |

Core Media objects are runtime media resources, not domain records. A sample
buffer can be copied, held, invalidated, or replaced. A persistent record
should store an asset ID, source revision, timestamps, format summary, and
accepted result—not a live `CMSampleBuffer` graph.

## `CMTime` is not a `Double`

Core Media represents time as a rational value: a value, timescale, flags, and
epoch. It can also represent invalid, indefinite, and positive/negative
infinite values. Keep that state visible:

| Time state | Meaning for a feature |
| --- | --- |
| Numeric | A valid point/duration in the selected media timeline |
| Invalid | The source did not provide a usable time; do not silently convert it to zero |
| Indefinite | The value is not currently knowable; show pending/unknown when user-visible |
| Positive/negative infinity | A sentinel that needs an intentional comparison policy |
| Different timescale/epoch | Convert/compare through documented Core Media functions, with a rounding policy |

Record the time scale and source when a result matters. Use presentation time
for display/order decisions, decode time when codec ordering matters, and
duration/output timing according to the selected API’s contract. Do not assume
that every sample has a meaningful decode timestamp or that presentation time
is strictly increasing across a discontinuity.

For a user-visible timeline, preserve:

~~~text
source clock/timebase
  -> sample presentation/decode time
  -> duration and discontinuity flags
  -> wall-clock/display mapping
  -> accepted domain timestamp
~~~

The last step is a product decision. A frame’s presentation timestamp is not
automatically a calendar date, a sensor capture truth, or the moment a model
finished inference.

## `CMSampleBuffer` has data, timing, and readiness

A `CMSampleBuffer` may contain compressed or uncompressed audio/video samples,
a `CMBlockBuffer`, a `CVImageBuffer`, a format description, timing, and
attachments. It may also describe samples whose data is not ready yet. Treat
these as separate states:

~~~text
created
  -> metadata/timing available
  -> data ready
  -> consumed / copied / handed off
  -> invalidated or released
~~~

Check data readiness before accessing data that may be deferred. If the source
uses a make-data-ready handler, call the documented readiness operation and
handle failure. A buffer-level discontinuity attachment may describe an event
such as a decoder reset; it is not an ordinary video frame and should not be
sent through an AI classifier as if it were one.

When a capture delegate gives the app a sample buffer, process it efficiently.
If work must outlive the callback, establish the appropriate ownership before
retaining or copying it and release it when the work ends. Capture buffers can
reference reusable memory pools; retaining too many for too long can prevent
new samples from being delivered and cause drops. Prefer a bounded handoff or
copy only the data required by the next stage.

Use a typed sample projection at actor/task boundaries:

~~~text
CMSampleBuffer callback
  -> timestamp/format/pixel-buffer or audio snapshot
  -> bounded work item
  -> analysis/render/export
~~~

Do not casually put a live sample buffer in an `@MainActor` view model, send it
across actors as `Any`, or capture it in an unbounded task group. Verify the
selected SDK’s sendability annotations and make a safe copy/representation
when crossing an isolation boundary.

## `CMBlockBuffer` and memory ownership

`CMBlockBuffer` represents a contiguous range of offsets across possibly
non-contiguous memory blocks and references. It can be empty, contiguous, or
backed by memory/buffer references. Choose a data access route deliberately:

| Need | Route | Cost to record |
| --- | --- | --- |
| Read a small known range | Copy bytes or use a bounded contiguous access | Copy and lifetime cost |
| Pass data to a compatible Core Media API | Keep the block buffer/reference structure | Downstream lifetime and mutability contract |
| Need a contiguous payload | Make/copy a contiguous block | Memory spike and cancellation policy |
| Replace bytes | Use documented mutable/block operation | Ownership, bounds, and thread safety |

Do not treat `dataLength` as a sample count, assume a data pointer stays valid
after the buffer’s ownership ends, or convert every buffer to `Data` on a live
capture path. Measure copies and use bounded pools for sustained media.

## `CMFormatDescription` is the format contract

`CMFormatDescription` is immutable and can describe audio, video, muxed media,
metadata, text, or time code. For video, inspect media subtype, dimensions,
frame duration, clean aperture, pixel aspect ratio, parameter sets, extensions,
and transfer/HDR metadata when relevant. For audio, inspect stream basic
description, channel layout, sample rate, format list, and magic cookie.

The format contract should be checked at every handoff:

~~~text
source format description
  -> capture/output setting
  -> decoder/encoder expectation
  -> Vision/Core ML input conversion
  -> Metal/Core Image texture policy
  -> export/container format
~~~

Dimensions are not necessarily the display size: clean aperture and pixel
aspect ratio can affect presentation. A pixel buffer’s existence does not
prove orientation, color space, HDR interpretation, or model input readiness.
Preserve relevant attachments and explicitly decide which metadata is copied,
redacted, or discarded.

Format changes are state transitions, not incidental warnings:

~~~text
format A
  -> format description changed
  -> drain/reconfigure dependent stages
  -> accept format B or enter unsupported state
~~~

Do not feed old-format buffers into a pipeline configured for a new format
without a validated conversion/rebuild path.

## Queues, timing, and backpressure

`CMBufferQueue` is a queue of timed buffers. A capture/decoder pipeline needs
an explicit policy for capacity, readiness, presentation order, late data,
discontinuities, and downstream speed:

| Pipeline state | Safe response |
| --- | --- |
| Consumer keeps up | Process and release/handoff bounded buffers |
| Consumer is slower | Drop according to product policy, downsample, or pause the source |
| Buffer arrives late | Record/drop/display-late policy; do not silently reorder user-visible truth |
| Queue reaches capacity | Apply backpressure or a documented drop policy before memory grows |
| Discontinuity occurs | Flush/reconcile decoder/analyzer state as required |
| Format changes | Stop dependent work, reconfigure, and mark the transition |
| App backgrounds/interruption | Pause, finish, or discard with explicit state |

For live AI, “process every frame” is rarely the product requirement. Define a
sampling cadence, keep the newest relevant frame, cancel stale inference, and
retain enough timing/provenance to explain which frame produced a proposal.
For recording/export, dropping a frame may be unacceptable; route through the
appropriate writer/codec contract instead of applying a live-preview policy.

## `CMTimebase` and synchronization

A `CMTimebase` models a timeline under application control and has a source
clock or timebase. A rate of zero holds time fixed; a rate of one follows the
source; other rates speed, reverse, or scale relative to the source. Anchor
changes and discontinuous time jumps are observable events.

Use a timebase when a feature needs a controllable timeline, synchronized
playback, pause/resume, scrubbing, or a render clock. Keep these distinct:

| Timeline | Authority |
| --- | --- |
| Capture clock | Device/media source and capture pipeline |
| Asset timeline | File/sample presentation/decode timing |
| Playback timebase | App/player-controlled rate/anchor |
| Display cadence | View/render system and drawable timing |
| Model completion time | Analysis task, not necessarily sample time |

Never claim that a model result is “live” solely because it completed on the
main actor. Store source sample time and model completion time separately.

## Attachments, tags, and metadata

Attachments can describe a sample or the whole stream: dependency/keyframe
state, color/HDR information, discontinuities, camera metadata, or other
processing instructions. Tags and tagged buffer groups can carry structured
media identity such as view/projection/stereo information.

Treat attachments as an input contract:

1. enumerate only the keys the selected downstream API understands;
2. preserve keys needed for correct rendering/decoding;
3. redact location, camera, user, or source metadata before logs/AI/export;
4. copy metadata only when the output format and privacy policy allow it;
5. keep unknown attachments from becoming an unreviewed domain decision.

An attachment is not a verified fact about the world. It is metadata supplied
by the media pipeline and should be interpreted within the documented source
and format contract.

## On-device AI pipeline

Core Media supplies timed input; it does not decide whether a model result is
true or whether a person should accept it. A bounded capture-to-AI route is:

~~~text
sample buffer
  -> readiness/format/timestamp check
  -> bounded pixel/audio projection
  -> model request with source revision/time
  -> typed observation/proposal
  -> review/validation
  -> domain record or render configuration
~~~

Keep the following fields with a proposal:

- source asset/session ID;
- sample presentation time/duration and source clock;
- format revision/orientation/color policy;
- model route, revision, and device availability;
- input redaction/retention choice;
- output confidence/evidence fields;
- user review and accepted revision.

If the model or media source is unavailable, show a manual/imported route. Do
not turn a dropped frame, stale sample, or missing format into a confident
text result.

## SwiftUI and Liquid Glass media shell

The native screen should expose media state without pretending that a buffer
callback equals a finished user outcome:

~~~text
source/session status
  -> capture/playback/analyzer status
  -> current sample time or “waiting”
  -> preview/render surface
  -> reviewable AI result
  -> save/export/share controls
~~~

Liquid Glass can group pause, capture, mark, review, or export actions when
they are the real controls. Keep timestamps, dropped-frame warnings, format
changes, permission state, and error/recovery copy readable outside the glass.
Use Dynamic Type, VoiceOver, captions/transcripts, reduced motion, and a
non-camera/non-audio fallback where the task permits it.

## Proof boundary

The [Core Media capability route](../50-capability-recipes/86-coremedia-sample-buffer-capability-route.md)
is the build worksheet. The [Core Media proof matrix](../60-verification/80-coremedia-sample-buffer-proof-matrix.md)
defines timing, lifetime, format, queue, AI, accessibility, and physical-device
evidence. The [Core Media recipes](../70-code-recipes/98-coremedia-sample-buffer-recipes.md)
are route sketches until compiled in a named capture/playback/export target.

## Sources

- [Core Media](https://developer.apple.com/documentation/coremedia)
- [CMTime](https://developer.apple.com/documentation/coremedia/cmtime)
- [CMSampleBuffer](https://developer.apple.com/documentation/coremedia/cmsamplebuffer)
- [CMBlockBuffer](https://developer.apple.com/documentation/coremedia/cmblockbuffer)
- [CMFormatDescription](https://developer.apple.com/documentation/coremedia/cmformatdescription)
- [CMBufferQueue](https://developer.apple.com/documentation/coremedia/cmbufferqueue)
- [CMTimebase](https://developer.apple.com/documentation/coremedia/cmtimebase)
- [CMClock](https://developer.apple.com/documentation/coremedia/cmclock)
- [CMAttachment](https://developer.apple.com/documentation/coremedia/cmattachment-api)
- [CMTag](https://developer.apple.com/documentation/coremedia/cmtag)
- [CMTagCollection](https://developer.apple.com/documentation/coremedia/cmtagcollection)
- [CMTaggedBufferGroup](https://developer.apple.com/documentation/coremedia/cmtaggedbuffergroup)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [AVCaptureVideoDataOutputSampleBufferDelegate](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutputsamplebufferdelegate)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [Core Video](https://developer.apple.com/documentation/corevideo)
- [CVPixelBuffer](https://developer.apple.com/documentation/corevideo/cvpixelbuffer)
- [Metal](https://developer.apple.com/documentation/metal)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
