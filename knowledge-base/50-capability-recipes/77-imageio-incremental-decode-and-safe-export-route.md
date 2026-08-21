# Image I/O incremental decode and safe export route

Use this route when an app needs to accept an image or image container, inspect it without trusting its filename, derive a bounded preview or AI input, and write a user-approved output with an explicit metadata policy.

The route is:

~~~text
input -> access check -> source inspect -> bounded decode -> optional AI proposal
      -> human review -> destination write -> finalize -> reopen and verify -> handoff
~~~

This page is a capability recipe, not a compiled implementation. Confirm the current SDK signature, deployment target, target membership, and format availability in the named Xcode target before shipping.

## Choose the source boundary

| Product input | First boundary | Additional requirement |
| --- | --- | --- |
| User picks a photo | PhotosPicker or a Photos framework route | Respect the selected representation and its authorization contract before materializing bytes. |
| User opens a file | Document picker, FileDocument, File Provider, or security-scoped URL | Keep access scope, file revision, provider state, and temporary-copy lifetime explicit. |
| App receives bytes | Image I/O source from CFData | Enforce byte and pixel budgets before decoding. |
| App receives a stream | Incremental CGImageSource | Keep all accumulated bytes and expose source status to the route. |
| App owns a camera frame | AVFoundation or a camera entry point first | Image I/O is the container/export layer after capture, not camera authorization or capture-session ownership. |
| App receives a remote URL | URL loading and trust policy first | Do not let a remote URL become a parser or model input without size, type, and cancellation controls. |

Image I/O does not request Photos permission, create a security-scoped bookmark, or prove that a file belongs to a person. Those responsibilities stay in the input framework and app-owned record.

## Route phases

### Phase A: validate and inspect

1. Resolve access to the selected source for only as long as needed.
2. Apply a byte-size limit before loading an unbounded data object.
3. Create a CGImageSource from the URL, data, provider, or incremental source.
4. Read the source type, image count, primary-image index where relevant, and container properties.
5. Read per-image properties only for indices the task needs.
6. Decide whether the source is a still, sequence, animation, stereo pair, or a file that the current target cannot safely handle.

Keep an intake record with source identifier, source revision, observed type, byte count, pixel dimensions, image count, and parser status. Do not use a source title or metadata author as the record identity.

### Phase B: derive a bounded working image

For list or review entry, use CGImageSourceCreateThumbnailAtIndex with a maximum pixel size and orientation transform. For a model, use the smallest derivative that satisfies the model’s task. For a final edit, decode the selected image at a deliberate size and preserve the source orientation contract.

Bound at least:

- source bytes;
- width and height;
- decoded pixel count and estimated memory;
- frame count and total frame work;
- concurrent decode count;
- model input size;
- time spent waiting for a provider or stream.

Cancel work when the user leaves the surface or replaces the source. A cancellation is not an invalid-file error and should not create a red failure state.

### Phase C: optional local AI proposal

The handoff to Vision, Core ML, Natural Language, Speech, or Foundation Models should include:

- an orientation-correct, bounded derivative;
- task-specific context rather than the whole raw file;
- source revision and selected frame/page/index;
- a model or route identifier;
- a typed result with uncertainty or a needs-review state;
- an explicit cancellation and unavailable-model path.

The proposal can prefill a form, label a region, summarize visible text, or suggest a filename. It cannot become canonical truth without user review and deterministic validation. The route must not imply identity, medical diagnosis, legal evidence, or a guarantee of correctness.

### Phase D: review the output contract

Before writing, let the person choose or confirm:

| Decision | Example choices |
| --- | --- |
| Output format | Keep source type, convert to JPEG, convert to HEIC, or create a supported image sequence. |
| Size | Preserve pixels, cap the maximum dimension, or create a thumbnail derivative. |
| Metadata | Preserve, minimize, remove GPS/XMP, or use an app-owned metadata projection. |
| Auxiliary data | Preserve depth/matte/gain map only when the destination route supports it, or disclose that it will be dropped. |
| AI edits | Accept, correct, reject, or export without the proposal. |
| Destination | Temporary preview, Files handoff, ShareLink, app storage, or a canonical app record. |

The action label should describe the consequence. Export private copy is clearer than Save when metadata is being removed.

### Phase E: write and verify

1. Create a destination for the intended output URL, mutable data object, or data consumer.
2. Use a supported uniform type identifier and the expected image count.
3. Set destination-wide properties when the contract requires them.
4. Add a decoded image, copy an image from the source, or pass image and metadata together.
5. Add auxiliary data only when the destination format and target route support it.
6. Call CGImageDestinationFinalize and require a true result.
7. Reopen the output with CGImageSource.
8. Verify the type, count, dimensions, orientation, metadata policy, and promised auxiliary data.
9. Move or hand off only the verified derivative.

Finalization is the commit boundary for the image output. A destination that exists, a mutable data buffer that has bytes, or a successful AddImage call is not enough.

## Incremental route state

The stream path should own a state machine rather than expose a Boolean called loaded:

| State | Data action | UI/action boundary |
| --- | --- | --- |
| no bytes | Create or await the source | Show waiting; allow cancel. |
| header reading | Update with accumulated data | Show preparing; do not promise type/count. |
| incomplete | Continue accumulation | Offer a partial preview only if the task allows it. |
| complete | Mark final and inspect | Enable review and export after derivative checks. |
| unexpected EOF | Stop or resume provider | Offer retry/resume; never silently finalize. |
| invalid data | Quarantine input | Show recoverable error and discard derivatives. |
| unknown type | Ask for more bytes or trusted hint | Offer supported-source fallback. |

For repeated updates, retain the accumulated Data or an equivalent provider representation. Passing only the newest network chunk violates the Image I/O incremental update contract.

## Common app compositions

### Private image journal

PhotosPicker or a document URL -> Image I/O thumbnail -> Vision/Core ML observation -> editable journal fields -> SwiftData record -> private JPEG/HEIC export with GPS policy. Store the original source reference separately from the redacted derivative.

### AI-assisted document intake

File importer -> source type/properties -> bounded page or frame preview -> Vision text observation -> typed draft -> user correction -> FileDocument or app record. Keep page/index and source revision attached to every proposal.

### Image conversion utility

Document picker -> source inspection -> output type and metadata policy -> source-to-destination copy or bounded decode -> finalize -> reopen -> ShareLink or Files handoff. Test every advertised format and keep unsupported-format messaging honest.

### Animated media editor

Source -> count and per-frame properties -> timing/loop inspection -> bounded frame selection -> user edit -> multi-image destination -> finalize -> reopen and verify frame count/timing. Do not treat a single still thumbnail as proof that the animation round trip succeeded.

### Spatial-photo utility

Two image sources or a supported stereo source -> inspect left/right and metadata -> user confirms spatial output -> HEIC destination with the required image ordering and spatial properties -> finalize -> physical-device and visionOS-compatible verification. Keep this route separate from ordinary still conversion.

## Failure policy

Use typed failures so the UI and logging can distinguish:

- no access or expired security scope;
- source bytes too large;
- pixel dimensions exceed the product budget;
- unsupported or unknown type;
- invalid or truncated data;
- incremental input not final;
- frame/index unavailable;
- auxiliary data unavailable or unsupported by destination;
- model unavailable, cancelled, or out of memory;
- destination creation failure;
- finalization failure;
- post-write verification mismatch;
- destination handoff failure.

Keep raw source URLs, GPS, XMP, and provider tokens out of analytics by default. Log a stable internal source identifier and a coarse failure code. If diagnostics require metadata, obtain separate product authorization and redact values.

## Target, permission, and entitlement checklist

- Image I/O framework is linked in the target.
- PhotosPicker, Photos, document picker, File Provider, or camera framework is configured separately when used.
- Required usage descriptions and privacy manifest entries are present for the input framework.
- Security-scoped URL access is started and stopped around the actual read.
- Temporary output files have an explicit owner and cleanup policy.
- AI frameworks and model assets are available on the selected device and OS.
- Spatial, HDR, gain-map, or camera-origin formats are tested against the target SDK and device family.
- ShareLink, Files, or provider handoff accepts the output type and lifetime.

## Evidence boundary

| Evidence | What it can prove | What it cannot prove |
| --- | --- | --- |
| Unit fixture | Type/count/property/metadata and failure parsing | System permission, camera-origin fidelity, or destination consumer behavior. |
| Compile | Current imports, names, and type checking in a named target | Runtime decoder coverage, memory behavior, or finalization success for every file. |
| Simulator | UI state, deterministic fixtures, and cancellation | Camera/Photos library, HDR/spatial display, device memory, or system handoff fidelity. |
| Signed physical device | Real decoder resources, memory, color, and device-specific media route | Every device family, every destination app, or App Store behavior. |
| Reopened output | The destination can be parsed and selected properties survive | That a human received, opened, or approved the file elsewhere. |
| System/destination run | Actual Files/ShareLink/provider consumer behavior for that build | General support for every external destination or future OS. |
| Release artifact | Target membership, signing, entitlements, privacy metadata, and build identity | Successful delivery, adoption, or content semantics. |

Pair this page with the [Image I/O source and destination proof matrix](../60-verification/71-imageio-source-destination-proof-matrix.md), the [media review design page](../21-design-deep-dives/74-imageio-media-review-and-metadata-design.md), and the [code recipes](../70-code-recipes/89-imageio-cgimagesource-and-destination-recipes.md).

## Sources

- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [Image I/O Functions](https://developer.apple.com/documentation/imageio/image-i-o-functions)
- [CGImageSourceStatus](https://developer.apple.com/documentation/imageio/cgimagesourcestatus)
- [CGImageSourceUpdateData](https://developer.apple.com/documentation/imageio/cgimagesourceupdatedata%28_%3A_%3A_%3A%29?language=objc)
- [CGImageSourceCreateThumbnailAtIndex](https://developer.apple.com/documentation/imageio/cgimagesourcecreatethumbnailatindex%28_%3A_%3A_%3A%29)
- [CGImageDestinationFinalize](https://developer.apple.com/documentation/imageio/cgimagedestinationfinalize%28_%3A%29)
- [Writing spatial photos](https://developer.apple.com/documentation/imageio/writing-spatial-photos)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
