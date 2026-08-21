# Image I/O source, destination, metadata, and media pipelines

Image I/O is the lower-level image container boundary for an iOS app. It reads image data from a URL, data object, data provider, or incremental stream; exposes type, count, dimensions, properties, metadata, auxiliary data, thumbnails, and images; and writes one or more images to a URL, mutable data object, or data consumer. It is a strong fit when an app needs predictable memory behavior, format-aware inspection, metadata policy, image-sequence handling, or a controlled export contract.

It is not a replacement for Photos authorization, PhotosPicker, camera capture, Quick Look, Vision, Core Image, Core ML, or SwiftUI image presentation. Keep the container/parser responsibility separate from the user-facing surface, model inference, and canonical domain record.

## The source-to-destination mental model

Use this pipeline when the product owns the byte-to-derivative decision:

~~~text
user-selected URL or bytes
  -> access and size validation
  -> CGImageSource creation
  -> type/count/properties/metadata inspection
  -> thumbnail or bounded image decode
  -> optional Vision/Core ML/Foundation Models proposal
  -> user review and metadata policy
  -> CGImageDestination creation
  -> add image, source image, metadata, or auxiliary data
  -> finalize and reopen for verification
~~~

The source is an observation boundary. The destination is a write boundary. A non-nil CGImage proves that Image I/O produced a decoded image for that input; it does not prove that the image is authentic, safe, semantically correct, or approved for a business action.

## CGImageSource: inspect before decoding

Create a source from the narrowest input the app already has:

| Input | Source constructor | Product consequence |
| --- | --- | --- |
| Local file or security-scoped URL | CGImageSourceCreateWithURL | Keep the access scope alive for the read, and do not assume the URL extension describes the bytes. |
| In-memory file data | CGImageSourceCreateWithData | Useful for a downloaded or PhotosPicker materialized derivative; enforce a byte budget before constructing large pipelines. |
| Custom provider | CGImageSourceCreateWithDataProvider | Useful when the app already owns a CGDataProvider and its lifetime. |
| Arriving bytes | CGImageSourceCreateIncremental, followed by CGImageSourceUpdateData or CGImageSourceUpdateDataProvider | Keep all accumulated bytes and expose incomplete, invalid, and complete states separately. |

After creation, ask the source what it knows before requesting a full image:

- CGImageSourceGetType identifies the source container when Image I/O can determine it.
- CGImageSourceCopyTypeIdentifiers and CGImageDestinationCopyTypeIdentifiers are useful for a target-aware format decision, but the current SDK and destination must still be tested.
- CGImageSourceGetCount reports images in the source container, excluding thumbnails.
- CGImageSourceGetPrimaryImageIndex is relevant for HEIF containers that have a preferred image.
- CGImageSourceCopyProperties describes container-level properties.
- CGImageSourceCopyPropertiesAtIndex describes the image at a particular index.
- CGImageSourceCopyAuxiliaryDataInfoAtIndex can expose associated depth, disparity, portrait-effects-matte, or HDR gain-map data when that source contains it.

Do not use a filename extension as the only type check. Type identifiers are a better input to routing, but malformed bytes, unsupported variants, resource limits, and an unavailable decoder still need explicit failure states.

## Incremental image sources

Incremental sources are useful for a network response, a provider-backed stream, or any UI that should begin inspecting a file before all bytes arrive. Each CGImageSourceUpdateData call receives all accumulated data so far, not only the newest chunk. The final Boolean says whether that accumulated data is complete.

CGImageSourceGetStatus and CGImageSourceGetStatusAtIndex report the state of a source or image. The status vocabulary includes reading header, incomplete, complete, unknown type, invalid data, and unexpected end of file. Treat status as a state machine:

| Status | UI and pipeline meaning |
| --- | --- |
| reading header | Keep the route alive; do not promise that the type or count is final. |
| incomplete | A preview or partial derivative may be possible, but the canonical file is not complete. |
| complete | The source has reached its final data state; still verify the decoded derivative and destination. |
| unknown type | Ask for more bytes or use an explicit type hint if the product has a trustworthy one. |
| invalid data | Stop parsing, discard the derivative, and show a recoverable failure. |
| unexpected EOF | The stream ended before the container was complete; allow retry or resume rather than silently exporting. |

Do not publish an incremental thumbnail as if it were a finalized user file. Record whether it was produced before or after final input, and invalidate partial derivatives when the source revision changes.

## Decode only what the surface needs

CGImageSourceCreateImageAtIndex creates a CGImage for a selected image index. It is appropriate for a final preview or a bounded processing step, but it can be an expensive operation for a very large photo. The source read options let the app control caching, immediate decoding, floating-point output, subsampling, and thumbnail creation.

For list, grid, picker, or AI preflight surfaces, prefer CGImageSourceCreateThumbnailAtIndex with options such as:

- create a thumbnail from the image always or when a source thumbnail is absent;
- maximum pixel size;
- orientation and aspect-ratio transform;
- subsampling factor;
- cache behavior appropriate for the lifetime of the derivative.

The thumbnail maximum is a maximum dimension, not a promise that every image will have exactly that width and height. Preserve the source orientation in the presentation contract. If the model does not need full resolution, do not decode full resolution merely because the device can display it.

The cache options are resource policy, not correctness policy. A cached decoded image can remain resident longer than a view; an uncached decode can be recomputed. Tie cache lifetime to the screen or task, and release or replace large derivatives when the source changes.

## Multi-image containers, animation, and auxiliary data

Image I/O can represent containers with multiple images. That is useful for GIF/APNG frames, image sequences, and HEIF variants. Treat frame index, duration, loop count, primary image, and auxiliary data as source facts that need to be preserved in the domain model if the product depends on them.

The Image I/O animation functions can animate GIF or APNG data with a callback. For a custom SwiftUI player, it is usually clearer to extract only the frames needed by the current viewport, keep timing separate from frame storage, and make cancellation explicit. Do not treat every multi-image container as an animation; some containers use multiple images for stereo, alternate representations, or auxiliary content.

Depth, disparity, portrait-effects matte, and HDR gain maps are not interchangeable with the visible base image. If the app preserves or edits them, define a format-specific preservation contract and verify the round trip on a physical device with representative source files. If the route drops auxiliary data, say so before export.

## Properties and metadata are different layers

Image properties are dictionaries describing the image or container. They can include width, height, orientation, color information, EXIF, IPTC, GPS, format-specific fields, camera maker data, and other source-specific values.

CGImageSourceCopyMetadataAtIndex returns a CGImageMetadata object for XMP-oriented metadata. CGImageMetadata is immutable for reading and searching. CGMutableImageMetadata creates or modifies metadata, and Image I/O can serialize metadata back to XMP. The metadata APIs support tag lookup, paths, enumeration, namespaces, prefixes, values, and tag removal.

Design the metadata policy before writing:

| Policy | Input behavior | Export behavior |
| --- | --- | --- |
| preserve | Keep source metadata needed for the user’s workflow | Use explicit merge/preserve options and verify the destination. |
| minimize | Keep only fields required for the app’s record | Build a new metadata projection instead of copying every dictionary. |
| private share | Remove location and unnecessary XMP before sharing | Set the documented GPS/XMP exclusion options and reopen the output to verify. |
| forensic/authoring | Preserve provenance and selected technical fields | Display the policy and retain a source revision; do not promise that proprietary maker notes are fully covered by a GPS flag. |

The GPS exclusion option removes GPS metadata from EXIF and corresponding XMP tags, but Apple documents that it does not filter proprietary location data in maker notes or custom XMP properties. The XMP exclusion option can preserve EXIF and IPTC tags while omitting XMP when used with the destination metadata option. These are useful controls, not a universal privacy scrub. Test the actual output with representative files and a metadata inspector in the target build.

Metadata is potentially personal data. Do not send raw EXIF, GPS, XMP, face-related auxiliary data, or camera identifiers to an on-device or remote model unless the user’s task requires it. A model should receive a bounded image derivative plus only the metadata fields that are explicitly part of the product task.

## CGImageDestination: write, then finalize

Create a destination with an output URL, mutable data object, or data consumer; specify a supported uniform type identifier and the expected image count; add images and properties; then call CGImageDestinationFinalize.

The destination supports:

- CGImageDestinationAddImage for a decoded CGImage;
- CGImageDestinationAddImageFromSource for copying an image at an index from a source;
- CGImageDestinationSetProperties for properties that apply to all images;
- CGImageDestinationAddAuxiliaryDataInfo for associated depth, matte, or other auxiliary data;
- CGImageDestinationAddImageAndMetadata when the image and CGImageMetadata need to be passed together;
- CGImageDestinationCopyImageSource for a source-to-destination conversion route with options and an error pointer;
- quality, background color, maximum pixel size, thumbnail embedding, orientation, metadata merging, color optimization, gain-map preservation, and GPS/XMP policy keys.

Finalization is a hard proof boundary. Apple documents that output is not valid until CGImageDestinationFinalize returns true, and that no more data can be added afterward. A destination object, a mutable Data buffer, or a successful AddImage call is not export proof.

For safe export:

1. choose an output type that the selected target and consumer actually support;
2. decide whether to preserve, project, or remove metadata;
3. write to a temporary URL or buffer;
4. finalize and check the Boolean result;
5. reopen the output with CGImageSource;
6. verify type, count, dimensions, orientation, metadata policy, and any auxiliary data that the product promises;
7. atomically move or hand off the verified derivative;
8. keep the source and derivative revisions distinct.

When writing a spatial photo, follow Apple’s dedicated route: create an HEIC destination with two images, assign left/right image metadata to the appropriate images, set a primary image policy, add the source images, and finalize. This is a target-sensitive media format, so a compile result or a single simulator preview is not enough.

## Image I/O and SwiftUI

SwiftUI Image is a presentation value. It should receive a bounded CGImage, UIImage, data-backed image, or an app-owned async image result; it should not be asked to become the parser, authorization layer, metadata scrubber, and model pipeline at once.

For a Liquid Glass image surface:

- decode a thumbnail for browsing;
- use the full image only in an intentional inspection surface;
- keep controls in semantic SwiftUI controls;
- place glass around controls or review affordances rather than over the visual content;
- show source type, revision, and privacy state without forcing the user to inspect raw metadata;
- keep export and AI actions behind explicit review;
- preserve accessibility labels, Dynamic Type, reduced transparency, reduced motion, and contrast behavior.

The [ImageRenderer export route](../41-framework-deep-dives/08-swiftui-image-renderer-and-export.md) is for rendering a SwiftUI view. Image I/O is for reading and writing image containers. They can be composed, but a rendered view is not automatically a lossless or metadata-preserving re-encode of an original file.

## AI route and authority boundary

A strong local-AI image workflow is:

~~~text
source access
  -> Image I/O type and resource inspection
  -> orientation-correct thumbnail or bounded derivative
  -> Vision/Core ML/Foundation Models observation
  -> typed proposal with source revision and confidence/uncertainty
  -> user correction
  -> app-owned record
  -> optional Image I/O export with explicit metadata policy
~~~

The model output remains a proposal until the user accepts it and the app validates the domain fields. Image I/O can make the bytes readable and writable; it cannot establish identity, diagnose a person, prove an object, or authorize a side effect.

## Failure and safety checklist

- Reject or quarantine unknown, invalid, truncated, or oversized input.
- Apply byte, pixel, frame-count, and decoded-memory budgets before doing expensive work.
- Bound concurrent decodes; use cancellation when a row leaves the viewport.
- Do not trust a filename extension, embedded title, GPS value, or camera maker field as identity proof.
- Keep security-scoped URL access and temporary-file lifetime explicit.
- Separate a source revision from a generated derivative revision.
- Make metadata preservation or removal visible at the export decision.
- Reopen finalized output and verify the properties the product promises.
- Test malformed files and adversarial dimensions, not only friendly camera samples.
- Do not claim HDR, gain-map, stereo, animation, or color fidelity without target-format/device evidence.

## Related routes

- [Image I/O incremental decode and safe export route](../50-capability-recipes/77-imageio-incremental-decode-and-safe-export-route.md)
- [Image I/O media review and metadata design](../21-design-deep-dives/74-imageio-media-review-and-metadata-design.md)
- [Image I/O source and destination proof matrix](../60-verification/71-imageio-source-destination-proof-matrix.md)
- [CGImageSource and CGImageDestination recipes](../70-code-recipes/89-imageio-cgimagesource-and-destination-recipes.md)

## Sources

- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [Image I/O Functions](https://developer.apple.com/documentation/imageio/image-i-o-functions)
- [CGImageSourceStatus](https://developer.apple.com/documentation/imageio/cgimagesourcestatus)
- [CGImageSourceUpdateData](https://developer.apple.com/documentation/imageio/cgimagesourceupdatedata%28_%3A_%3A_%3A%29?language=objc)
- [CGImageSourceGetStatus](https://developer.apple.com/documentation/imageio/cgimagesourcegetstatus%28_%3A%29?language=objc)
- [CGImageSourceCreateThumbnailAtIndex](https://developer.apple.com/documentation/imageio/cgimagesourcecreatethumbnailatindex%28_%3A_%3A_%3A%29)
- [CGImageSourceCopyPropertiesAtIndex](https://developer.apple.com/documentation/imageio/cgimagesourcecopypropertiesatindex%28_%3A_%3A_%3A%29)
- [CGImageMetadata](https://developer.apple.com/documentation/imageio/cgimagemetadata)
- [CGMutableImageMetadata](https://developer.apple.com/documentation/imageio/cgmutableimagemetadata)
- [CGImageDestinationCopyImageSource](https://developer.apple.com/documentation/imageio/cgimagedestinationcopyimagesource%28_%3A_%3A_%3A_%3A%29)
- [CGImageDestinationFinalize](https://developer.apple.com/documentation/imageio/cgimagedestinationfinalize%28_%3A%29)
- [kCGImageMetadataShouldExcludeGPS](https://developer.apple.com/documentation/imageio/kcgimagemetadatashouldexcludegps)
- [kCGImageMetadataShouldExcludeXMP](https://developer.apple.com/documentation/imageio/kcgimagemetadatashouldexcludexmp)
- [Writing spatial photos](https://developer.apple.com/documentation/imageio/writing-spatial-photos)
- [EXIF Dictionary Keys](https://developer.apple.com/documentation/imageio/exif-dictionary-keys)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
