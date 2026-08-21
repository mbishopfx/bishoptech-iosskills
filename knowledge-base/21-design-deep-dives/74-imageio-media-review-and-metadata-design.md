# Image I/O media review and metadata design

An image-heavy iOS app should feel native before it feels decorative. The design job is to help a person recognize a visual asset, understand what the app knows about it, decide what an AI or export action will do, and recover when the source is incomplete or unsupported. Image I/O supplies the technical facts; SwiftUI and Human Interface Guidelines supply the interaction language.

The target composition is:

~~~text
recognize -> inspect -> understand provenance/privacy -> propose -> correct -> commit/export
~~~

Do not collapse all six stages into a translucent card with a single magic action. Apple-like polish comes from hierarchy, clear state, semantic controls, restraint, and fast recovery.

## Surface hierarchy

Use separate surfaces for separate user jobs:

| Job | Surface | Image I/O responsibility | Design responsibility |
| --- | --- | --- | --- |
| Browse | List, grid, or source picker | Generate bounded thumbnails and source facts | Make filename, type, revision, and loading/error state discoverable. |
| Inspect | Full-screen viewer or detail column | Decode the selected image or frame at an intentional size | Keep the visual content primary and controls easy to reach. |
| Understand | Inspector, metadata disclosure, or review sheet | Expose selected dimensions, orientation, frame count, and privacy state | Use plain-language labels; avoid dumping raw dictionaries into the primary flow. |
| Propose | AI review surface | Supply a bounded, orientation-correct derivative and source revision | Mark generated text or fields as suggestions, with source and uncertainty. |
| Correct | Form, editor, or focused review | Preserve the source and derivative relationship | Let the person edit values directly; do not make a model the authority. |
| Export/share | Confirmation sheet or ShareLink route | Write and reopen a verified destination with the selected metadata policy | State output type, destination, metadata behavior, and what is not preserved. |

The browse surface should not decode a full-resolution image for every row. The inspect surface should not silently mutate the source. The export surface should not report success until destination finalization and post-write verification are complete.

## Liquid Glass placement

Liquid Glass is most useful around controls that float above changing content: a compact toolbar, a filter control, a review action group, a source-status pill, or a bottom action bar. Keep the image itself legible and let the glass respond to the content behind it.

For an image review screen:

- use a system navigation bar, toolbar, tab, sheet, or semantic button when it already expresses the job;
- group related controls so the glass container can coordinate their visual relationship;
- place glass away from faces, document text, and important edges when the content is the focus;
- avoid stacking multiple opaque or translucent layers that reduce contrast;
- let the content determine the page background rather than forcing every screen into a decorative material;
- use one clear primary action such as Review, Export, or Analyze;
- use confirmation for irreversible or privacy-sensitive metadata changes;
- provide a non-glass readable fallback when reduced transparency or contrast settings require it.

Do not recreate Apple Photos, Files, or Quick Look chrome as a visual imitation. Adopt the interaction conventions, spacing, semantic controls, and system behavior that make a surface feel at home on iOS, while keeping the app’s content model original.

## Progressive and incomplete states

An incremental source needs a visible state model. A good image card can distinguish:

| State | Short user-facing language | Available action |
| --- | --- | --- |
| waiting for bytes | Loading image | Cancel, retry, or keep browsing. |
| header recognized | Preparing preview | View a bounded preview if safe. |
| partial preview | Preview from received data | Do not offer canonical export yet. |
| complete | Ready to inspect | Analyze, edit, or export according to policy. |
| unknown type | Unsupported image type | Choose another file or retry with a trusted type. |
| invalid | This file could not be read | Remove, replace, or report the problem. |
| incomplete end | File ended before it finished | Resume, redownload, or choose a different source. |

Avoid spinners that hide all context. Keep the source name or an accessible identifier visible, and ensure cancellation does not leave an apparently complete thumbnail in the model queue.

## Metadata disclosure that does not overwhelm

Most people do not need EXIF key names. They do need to know whether a share will include location, whether the output is a converted copy, whether the app received a limited derivative, and whether the source contains depth or a sequence.

Use progressive disclosure:

1. primary surface: image, title, source type, and current action;
2. review surface: dimensions, orientation correction, frame count, and generated-versus-source labels;
3. privacy disclosure: location included or removed, XMP included or removed, and whether proprietary maker data may remain;
4. advanced inspector: exact metadata tags for users whose workflow needs them.

Do not infer identity from a GPS coordinate, camera make, title, or embedded author string. Treat metadata as source context, not verified truth. If the app uses metadata to prefill a domain field, label it as imported and let the person correct it.

## AI review design

An on-device model can be fast and private while still being wrong. The review surface should show the relationship between the source and a generated proposal:

~~~text
source image
  -> bounded derivative used for analysis
  -> generated field or summary
  -> source location or frame reference
  -> confidence/uncertainty or needs-review state
  -> accept, edit, reject, retry
~~~

Design rules:

- show the exact image or frame that was analyzed when multiple images exist;
- preserve a source revision so a stale result cannot be applied to a changed file;
- distinguish model-generated text from user-authored text with accessible labels;
- keep destructive or externally visible actions behind a second review;
- make model unavailability, language limitations, memory pressure, and cancellation understandable;
- do not imply that image classification is identity verification, medical interpretation, legal proof, or a guarantee of correctness;
- avoid sending raw metadata to a model when a pixel-only derivative is sufficient.

When the AI result becomes an app-owned record, store the source reference, model or route version, timestamp, user edits, and acceptance event separately. This makes the review auditable without pretending the model output is a canonical fact.

## Frame, animation, and spatial media

For an animated source, make playback and selection explicit. A scrubber or frame count helps a user understand whether Analyze applies to the current frame, all frames, or a sampled subset. Do not hide a many-frame computation behind a single still preview.

For stereo or spatial content, use a plain-language status such as spatial pair detected, left/right views available, or converted to a standard still. Do not promise a spatial experience on a device or destination that cannot display it. If export drops depth, a gain map, a matte, or one eye, disclose that before the user commits.

The right surface for frame selection is usually an app-owned review view. The right surface for a system-owned file preview may be Quick Look. The right surface for camera capture is AVFoundation or the system camera entry point. Image I/O should remain the media container layer beneath those choices.

## Accessibility and alternate input

Media surfaces need more than a VoiceOver label for the image:

- expose the asset title, source type, revision, loading/error state, and primary action;
- provide a meaningful label or description for the image when the product knows one, and do not invent content as fact;
- make frame, zoom, play/pause, export, and metadata disclosure actions reachable with VoiceOver, Voice Control, Switch Control, keyboard, pointer, and controller input where supported;
- support Dynamic Type for labels, review fields, and errors;
- test long filenames, right-to-left text, localization expansion, and compact width;
- honor Reduce Motion and reduced transparency; avoid making a morphing glass transition the only way to understand a state change;
- maintain contrast over bright, dark, detailed, and animated images;
- use semantic Button, Toggle, Picker, Menu, Slider, and ProgressView controls rather than gesture-only affordances;
- ensure an image does not trap focus behind a full-screen viewer or sheet.

An accessibility audit, a Preview canvas, or a snapshot is diagnostic evidence. Verify the actual task on a signed build with the settings and input methods that matter to the product.

## Privacy-first export review

The export confirmation should answer four questions:

| Question | Example answer |
| --- | --- |
| What is being written? | JPEG copy, HEIC conversion, animated image, or spatial HEIC. |
| What is kept? | Orientation, selected authoring fields, or all supported metadata. |
| What is removed? | GPS and XMP, selected fields, or nothing. |
| What is not guaranteed? | Proprietary maker-note location, unsupported auxiliary data, or destination-specific fidelity. |

Use a primary action with the output consequence in its label when space allows, such as Export private copy. Use a secondary disclosure for advanced metadata details. If the export fails finalization, keep the review sheet open with a retry and a clear reason; do not show a success toast from a pre-finalization callback.

## Performance and energy as design quality

Fast scrolling, low memory, and predictable cancellation are part of Apple-native feel. Prefer small thumbnails, bounded concurrency, and task cancellation over eager full-resolution work. Show a placeholder that preserves layout when a thumbnail is unavailable. Do not make an AI analysis task hold every decoded frame in memory.

For expensive operations, expose progress in a form that survives Dynamic Type and VoiceOver. A progress indicator should correspond to meaningful work such as received bytes, frames inspected, or export finalization, not an arbitrary timer.

Record representative memory, CPU, energy, and hitch observations on physical devices. A newer device can hide a design that is unusable on a supported older device.

## Design acceptance checklist

- The list uses thumbnails and does not decode every source at full resolution.
- The detail view distinguishes source, derivative, proposal, and export.
- The source revision is visible in model and UI state even when it is not shown to the person.
- The AI action names what will be analyzed and allows correction.
- Metadata policy is understandable before sharing or saving.
- Liquid Glass surrounds controls and preserves the content hierarchy.
- Reduced transparency, large text, VoiceOver, alternate input, and RTL have a usable layout.
- Unsupported, invalid, partial, and cancelled states are designed, not just logged.
- Animation, auxiliary data, and spatial content have explicit preserve/drop behavior.
- The app does not imitate system-owned Photos, Files, or Quick Look screens.
- The final action is tied to verified destination output, not a draft buffer.

## Related routes

- [Image I/O source, destination, metadata, and media pipelines](../42-framework-deep-dives/54-imageio-source-destination-and-metadata.md)
- [Image I/O incremental decode and safe export route](../50-capability-recipes/77-imageio-incremental-decode-and-safe-export-route.md)
- [Image I/O source and destination proof matrix](../60-verification/71-imageio-source-destination-proof-matrix.md)
- [CGImageSource and CGImageDestination recipes](../70-code-recipes/89-imageio-cgimagesource-and-destination-recipes.md)

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [SwiftUI Image](https://developer.apple.com/documentation/swiftui/image)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
