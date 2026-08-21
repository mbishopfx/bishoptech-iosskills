# GPU rendering and media visual surfaces

## Design objective

GPU-backed visuals should feel immediate, stable, and native. The person should experience the result—not the command queue, shader compilation, frame backpressure, or codec state behind it.

Use this interaction model:

~~~text
source ready
  -> previewing
  -> processing
  -> degraded|paused|cancelled
  -> result review
  -> export/share/save
~~~

Keep the visual surface and the system controls legible even when the GPU or media pipeline is under pressure.

## Surface ownership

| Surface | Design responsibility |
| --- | --- |
| SwiftUI shell | Navigation, permissions, settings, review, errors, accessibility, and system handoff |
| Preview | Show the current source/effect state with an honest loading/degraded indication |
| Metal/Core Image surface | Render the effect with bounded resource and frame policy |
| Video/audio control | Explain playback/capture/recording status and interruption |
| Review screen | Show source, effect/model version, output, and reversible decision |
| Export/share surface | State format, destination, redaction, and completion evidence |

Do not make a Metal or VideoToolbox callback update a SwiftUI view directly without an explicit state adapter. The callback may arrive on a different queue and may outlive the screen.

## State-driven visual feedback

| State | Visual treatment | Required action |
| --- | --- | --- |
| preparing | Static preview or placeholder with short message | Cancel |
| compiling | Avoid a blank screen; show known source/previous frame | Wait/cancel |
| live | Stable preview and explicit quality indicator only if useful | Pause/stop |
| dropped frames | Preserve scene and show a non-alarming degraded status | Lower quality/retry |
| thermal degraded | Reduce quality/frame rate and explain | Continue/cancel |
| unavailable feature | Offer a high-level fallback | Use fallback |
| processing export | Progress tied to real work, not a fake timer | Cancel |
| output ready | Show output and settings/source | Review |
| export failed | Preserve source and partial-safe cleanup | Retry/alternate format |
| share ready | Show redacted projection and format | Share/cancel |

Avoid flashing “GPU error” or “codec callback” at users. Translate the state into an actionable message and retain technical identifiers only in redacted diagnostics.

## Liquid Glass around live content

Use Liquid Glass for functional groups:

- play/pause/stop;
- capture/export;
- effect selection;
- quality or mode selection;
- review/accept/reject.

Keep glass controls in stable screen-space regions. Do not cover important video detail with a large translucent panel, and do not use a shader to fake a system surface that SwiftUI already provides.

When a visual effect changes the background behind glass:

- test contrast against bright/dark/high-frequency media;
- keep labels and symbols stable;
- provide reduced-transparency behavior;
- avoid morphing action groups while VoiceOver focus or keyboard focus is active;
- preserve a static, readable fallback when rendering is paused.

## Color, HDR, and visual truth

Color is part of the user-visible contract. A preview and an exported file can differ if the pipeline changes color space, transfer function, alpha mode, orientation, or pixel format.

Communicate only what the app actually controls:

- “HDR preview” requires the intended display and format evidence;
- “lossless” requires an output/container proof;
- “same colors” requires a defined color-space path;
- “real-time” requires a named device/workload/frame budget;
- “AI-enhanced” should identify the operation and preserve the original.

Do not hide a format conversion inside an AI preset. Show export choices in plain language and let the user compare original/output when fidelity matters.

## Direct manipulation and effect controls

Use controls that match the user’s mental model:

- slider for intensity with a visible value/scale;
- toggle for an optional effect;
- segmented control for mutually exclusive render modes;
- before/after comparison for a destructive-looking transformation;
- scrubbing timeline for video;
- reset for a reversible effect chain;
- explicit Save as Copy/Replace labels.

If a shader parameter has no useful human meaning, expose a high-level named preset rather than a raw number. Advanced controls can be placed in a secondary inspector, but the default path should remain concise.

## AI review surfaces

AI-generated visual changes require a reviewable comparison:

| Input | Proposal surface |
| --- | --- |
| Selected image | Before/after with effect name and source |
| Video segment | Preview with duration/output format |
| Frame classification | Label, confidence language, and source frame |
| Generated color/effect preset | Named intent, editable controls, reset |
| Export recommendation | Format/size/quality explanation |

AI should not silently:

- change a user’s original file;
- discard frames;
- alter timestamps;
- change color profile;
- export/share media;
- use a private frame as a notification/widget image;
- select a codec or quality setting with irreversible consequences.

Use a proposal object and deterministic commit. Let the person see the output before writing or sharing.

## Accessibility and sensory load

A visual effect is not accessible merely because the enclosing button has a label. Provide:

- semantic controls and status announcements;
- text labels for processing/degraded/error states;
- captions/transcripts where audio conveys meaning;
- alternate still image or list representation;
- VoiceOver access to effect name/intensity/output state;
- Voice Control names for Start, Stop, Reset, Export, and Share;
- keyboard/pointer equivalents on iPad/Mac Catalyst where supported;
- Reduce Motion behavior that removes decorative movement but preserves state;
- reduced-transparency behavior that maintains contrast;
- no-color-only status indication.

High-frequency animation, flashing, strong parallax, and continuous haptics can make a GPU-heavy surface uncomfortable even when frame rate is stable. Allow the user to reduce visual/sensory intensity.

## Performance as interaction design

Set a visible policy before optimizing:

- target frame cadence;
- maximum source dimensions;
- effect complexity;
- queue depth;
- acceptable frame dropping;
- export progress/cancellation;
- thermal degradation;
- fallback quality.

When work cannot keep up, preserving responsiveness is more native than insisting on every frame. A live preview can drop intermediate frames while an export route must preserve ordered timestamps. Those are different user contracts.

Use signposts and metrics to understand where latency originates. Do not show a spinner for a GPU stall if the last valid frame can remain visible with a brief status.

## Native navigation and system handoff

Place settings, source selection, export format, and privacy controls in standard SwiftUI navigation/sheets. Keep the live render surface focused. Use a review sheet before:

- replacing the original;
- saving a large output;
- sharing;
- changing a PhotoKit asset;
- starting a long background export;
- sending content to a provider or system surface.

System-owned share, file export, and Photos routes should remain system-owned. The app’s custom shell should explain what is being handed off and what remains in the app.

## Design review questions

- Does the preview stay understandable during shader compilation or frame dropping?
- Does the person know whether they are editing a copy or the original?
- Can they see color/format/quality consequences before export?
- Is the AI change visibly proposed and reversible?
- Does the UI expose a usable fallback when GPU/codec support is unavailable?
- Are processing and export states honest about cancellation?
- Can VoiceOver complete the task without watching the animation?
- Does reduced motion/transparency preserve the meaning of the screen?
- Is the material helping hierarchy rather than covering content?
- Is every performance claim tied to a device and workload?

## Sources

- [Metal](https://developer.apple.com/documentation/metal)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
- [Understanding the Metal 4 core API](https://developer.apple.com/documentation/metal/understanding-the-metal-4-core-api)
- [Validating your app’s Metal shader usage](https://developer.apple.com/documentation/xcode/validating-your-apps-metal-shader-usage)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [CIContext](https://developer.apple.com/documentation/coreimage/cicontext)
- [CIImage](https://developer.apple.com/documentation/coreimage/ciimage)
- [VideoToolbox](https://developer.apple.com/documentation/videotoolbox)
- [VTCompressionSession](https://developer.apple.com/documentation/videotoolbox/vtcompressionsession-api-collection)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
