# Core Media timeline and media-review design

Core Media makes the media pipeline precise; the interface should make that
precision understandable. A person should know whether the app is capturing,
waiting for data, processing a particular moment, showing a dropped/late
sample, or displaying an accepted result. They should not need to understand
`CMTime`, `CMSampleBuffer`, or a format description to recover from a failure.

## Design the media state, not the callback

Use a state model such as:

~~~text
idle
  -> requesting permission
  -> configuring source
  -> waiting for first sample
  -> capturing / playing / analyzing
  -> paused / interrupted / backgrounded
  -> format changed / reconfiguring
  -> review pending
  -> saved / exported / failed
~~~

For a live analyzer, include a separate freshness state:

| State | Customer-facing meaning |
| --- | --- |
| No sample | “Waiting for input” |
| Fresh sample | “Analyzing current input” |
| Stale sample | “Showing the last analyzed moment” |
| Dropped/late | “The device is catching up; reduce quality or pause” |
| Format change | “Reconfiguring the input” |
| Model unavailable | “Use manual entry or an imported recording” |

Never label the screen “live” simply because an `AsyncStream` or delegate is
active. Show the source timestamp/freshness policy when the result matters.

## Timeline hierarchy

| Layer | What the person sees | What the app must keep separate |
| --- | --- | --- |
| Source/session | Camera, microphone, file, or player state | Permission, route, interruption, and source ownership |
| Media timeline | Current position, duration, pause/scrub/seek | `CMTime` value/scale/flags and source clock |
| Sample/format | Preview, waveform, frame, or metadata | `CMSampleBuffer`, format description, attachments, and readiness |
| Analysis | Progress/partial/final result | Sample time versus model completion time |
| Review | Editable proposal and evidence | Canonical record and acceptance decision |
| Export/share | User-started action and result | Output timing/format/retention/destination behavior |

Do not make the review editor appear to rewrite the original media. Show the
source moment, the generated proposal, and the accepted domain value as
different layers.

## Liquid Glass controls with readable timing

Glass can group the controls that operate on the current timeline:

- Record/Pause/Stop for a deliberate capture session;
- Play/Pause/Scrub for playback;
- Mark current moment when the source timestamp is preserved;
- Review a model proposal before saving;
- Export/share after a user-started action.

Keep these outside or adjacent to the material:

- permission/authorization status;
- “waiting for data” or “last sample” freshness;
- dropped-frame/late-data warning;
- format/HDR/audio-route change;
- model unavailable/remote fallback;
- saved/exported/failed result.

An animated waveform or glossy preview does not prove that audio/video is
recording, a frame was stored, or an AI result is current. Use semantic labels,
values, and status text.

## Capture and playback affordances

For capture:

1. Explain the microphone/camera need immediately before the user starts.
2. Show a clear active state and a stop action.
3. Show interruption, route change, denied, no-input, and permission-revoked
   states.
4. Preserve a source/session ID and timing policy for later review.
5. Make cancellation distinct from successful save.

For playback:

1. Make current time/duration understandable at large text.
2. Keep seek/scrub separate from the accepted analysis position.
3. Expose stale/partial/unsupported media states.
4. Preserve the original file and derived edits according to product policy.
5. Test interruption, background, route change, and resumption.

## AI review design

The review card should answer:

1. Which source moment produced this proposal?
2. What input fields/frame/audio segment were used?
3. Is the value provisional, edited, or accepted?
4. What happens if the source changed or the model is unavailable?
5. Can the person undo/delete the derived result?

Use this composition:

~~~text
source frame/segment + timestamp
  -> typed model proposal
  -> evidence/source span or highlighted input
  -> Edit / Accept / Dismiss
  -> deterministic validation
  -> accepted record or render state
~~~

Do not let a model infer a timestamp, measurement, person identity, health
conclusion, or legal/financial fact from a media sample without a domain-
specific review policy. A confidence score is not evidence that the sample was
current or that the output is correct.

## Accessibility and alternate input

Media screens need a task route beyond sound, motion, or a rendered frame:

| Requirement | Design response |
| --- | --- |
| Deaf/hard-of-hearing access | Captions/transcript, visible level/status, and text alternative where relevant |
| Blind/low-vision access | Semantic playback/capture controls, timestamp/value announcements, transcript/inspector, haptic only as supplemental feedback |
| Dynamic Type | Native text/status/editor; never bake essential instructions into video/texture |
| Reduce Motion | Static preview/track state and no essential camera drift |
| Reduce Transparency/contrast | Preserve control boundaries and warning status without material effects |
| Keyboard/pointer/Switch/Voice Control | Focusable semantic actions and scrubbing alternative |
| No microphone/camera | Import a file, type a value, or use a deterministic sample fixture when the core task permits |

Use color, waveform, haptic, and animation as additional signals, not the only
meaning. Test the task at large text and with the source/audio disabled.

## Timeline and data language

If the person can see a timestamp, define its meaning in plain language:

- “recorded at source time” for a source timestamp;
- “analyzed after capture” for model completion;
- “last updated” for the app record;
- “exported” for a derived artifact;
- “approximate” when a conversion or clock alignment is not exact.

Do not show a raw rational/timebase value as a user-facing date. Format it
from the product’s known clock and locale, and preserve the raw media timing in
the evidence record.

## Privacy and retention

Media UI should state what is retained:

- live frames/audio kept only for the active pipeline;
- source recording retained until the user deletes it or according to policy;
- derived transcript/labels/embeddings saved separately;
- attachments/metadata/location/camera information included or removed;
- exports/shares and system destinations treated as new copies;
- logs contain IDs/metrics, not raw media/prompts unless explicitly approved.

Permission to capture is not permission to retain, upload, train, share, or
publish the content.

## Native design review checklist

- The screen distinguishes source state, media timeline, analysis, review, and
  export.
- Current/stale/dropped/format-change states are visible.
- Glass groups functional media controls and does not hide freshness/error copy.
- Source timestamp and model completion time remain distinct.
- AI results are editable, typed, source-linked, and reversible.
- Captions/transcripts/semantic values support people who cannot use the raw
  audio, motion, or visual surface.
- Dynamic Type, VoiceOver, reduced motion/transparency, contrast, keyboard,
  pointer, and cancellation are tested.
- Retention, export, deletion, and logging are legible.

## Sources

- [Core Media](https://developer.apple.com/documentation/coremedia)
- [CMTime](https://developer.apple.com/documentation/coremedia/cmtime)
- [CMSampleBuffer](https://developer.apple.com/documentation/coremedia/cmsamplebuffer)
- [CMFormatDescription](https://developer.apple.com/documentation/coremedia/cmformatdescription)
- [CMTimebase](https://developer.apple.com/documentation/coremedia/cmtimebase)
- [AVCaptureVideoDataOutputSampleBufferDelegate](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutputsamplebufferdelegate)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Human Interface Guidelines accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Speech](https://developer.apple.com/documentation/speech)
