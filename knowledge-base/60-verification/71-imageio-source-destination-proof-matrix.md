# Image I/O source and destination proof matrix

This matrix separates Image I/O documentation, compilation, deterministic fixture behavior, device media behavior, destination handoff, and release evidence. A green parser test is valuable, but it is not proof that a user’s camera-origin HEIC, spatial photo, HDR derivative, metadata policy, or Files handoff behaves correctly on a supported device.

The core proof chain is:

~~~text
source bytes -> source facts -> bounded derivative -> optional AI proposal
             -> destination finalize -> reopened output -> destination/system handoff
~~~

Every stage should record the source revision and the exact target/build when the route becomes a product feature.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Stronger evidence | Do not infer |
| --- | --- | --- | --- |
| The target imports and calls the selected Image I/O APIs | Named target compile against the selected SDK | Small test target with unit coverage | That every API works on every deployment target. |
| A file type is accepted | Fixtures with trusted and misleading extensions; source type inspection | Format matrix on each supported OS/device family | That an extension or MIME label validates bytes. |
| A thumbnail is bounded | Unit test for maximum dimension and orientation; memory measurement | Scroll test with cancellation and representative large files on device | That a thumbnail is canonical image content or full-resolution quality. |
| Incremental loading is correct | Accumulated-chunk test with status assertions | Network/provider stream with cancellation and resume on device | That partial preview means the source is complete. |
| Metadata is preserved or removed | Reopen output and inspect declared fields | Representative EXIF, IPTC, GPS, XMP, maker-note, and auxiliary-data files | That a GPS exclusion flag removes every proprietary location field. |
| Export succeeded | CGImageDestinationFinalize returns true and output reopens | Atomic handoff plus destination consumer run | That a destination object or Data buffer is valid before finalization. |
| An image sequence round-trips | Count, timing, loop, and per-frame fixture assertions | Physical-device playback and destination app run | That the first frame proves animation or stereo support. |
| HDR, gain map, depth, matte, or spatial data survives | Source/destination auxiliary-data and property assertions | Camera-origin physical-device round trip and compatible display | That a simulator or ordinary JPEG confirms advanced media fidelity. |
| AI analysis used the intended input | Recorded source revision, index/frame, derivative dimensions, and model route | Device resource/cancellation tests and human review | That a model result is true, canonical, or user-approved. |
| Sharing works | Signed build opens the intended ShareLink/Files/provider surface | TestFlight or production-like destination acceptance | That a local file URL is deliverable outside the app. |

## Fixture set

Keep fixtures small enough for unit tests and realistic enough to expose format boundaries:

- baseline JPEG with orientation, EXIF date, GPS, and an embedded thumbnail;
- PNG with alpha and a large pixel dimension;
- HEIC still with orientation and color information;
- multi-image HEIF or stereo sample where the target supports it;
- animated GIF or APNG with at least three frames and nonuniform delays;
- image with XMP, IPTC, and a deliberately retained authoring field;
- source containing depth, disparity, portrait-effects matte, or HDR gain-map data when licensed and available;
- truncated file that ends during the header;
- unknown or unsupported type with a misleading filename extension;
- very large dimension fixture whose compressed byte size is small enough to hide decoded-memory risk;
- incremental chunks split before type detection, during frame data, and at the final byte.

Do not put private photographs or real GPS values in a shared repository. Use synthetic metadata and scrub fixture provenance.

## Unit and integration assertions

### Source inspection

Assert:

- source creation fails or reports a typed error for invalid input;
- source type is driven by bytes and trusted hints, not extension alone;
- image count is correct;
- primary image index is recorded when applicable;
- container and per-image properties are kept separate;
- dimensions and frame count are checked before full decode;
- source status is recorded for incremental and final input.

### Thumbnail and bounded decode

For each supported source:

- request a thumbnail with the chosen maximum pixel size;
- verify both portrait and landscape orientation;
- verify that a huge source does not produce an unbounded derivative;
- assert that a canceled task does not publish an image after cancellation;
- exercise cache-on and cache-off policy where the product depends on it;
- measure peak memory for representative large assets;
- ensure the AI derivative uses the same orientation and source index the UI reviewed.

### Incremental source

Feed the same bytes in multiple chunk sizes and assert that:

- the source progresses through reading-header or incomplete states before final data;
- the route does not pass only the newest chunk to Image I/O;
- a partial thumbnail is never marked canonical;
- final input changes status to complete when the fixture is valid;
- invalid and unexpected-end fixtures reach distinct failure states;
- a later source revision invalidates earlier derivatives and proposals.

### Metadata policy

For preserve, minimize, and private-share routes:

- reopen the destination with Image I/O;
- inspect container and per-image properties;
- inspect XMP metadata where present;
- assert that fields explicitly promised to remain are present;
- assert that GPS and XMP exclusions have the documented effect;
- test a maker-note or custom XMP location field separately so the UI does not overpromise a universal location scrub;
- test that the output does not accidentally inherit stale metadata when the user chose a clean projection;
- record whether auxiliary data was preserved, transformed, or dropped.

### Destination finalization

Assert:

- destination creation uses a supported type and expected image count;
- all adds happen before finalization;
- a false finalization result produces a visible failure;
- the output is not handed off before finalization;
- the reopened output has the expected type, count, dimensions, orientation, and metadata;
- destination or temporary files are cleaned up on failure and cancellation;
- source and destination revisions remain distinct.

## UI and system proof

Use a signed app build for the user-facing task:

| Scenario | Evidence to capture |
| --- | --- |
| Browse | Scroll a large fixture set, observe thumbnail latency, cancellation, VoiceOver labels, and memory. |
| Inspect | Open portrait/landscape, animated, and multi-image fixtures; verify controls and orientation. |
| AI review | Show analyzed frame/index, generated proposal label, source revision, correction, retry, and unavailable-model state. |
| Export private copy | Review metadata policy, finalize, reopen, and share the actual output. |
| Files handoff | Use the real document/share surface, then reopen the output in the destination app. |
| Photos-origin asset | Select through the intended Photos route and confirm the representation actually delivered to Image I/O. |
| Security-scoped file | Test access start/stop, cancellation, missing access, and provider-backed materialization. |
| Reduced effects | Use reduced transparency, increased contrast, Reduce Motion, Dynamic Type, VoiceOver, Voice Control, and keyboard/pointer where applicable. |

A system sheet appearing is not proof that the output was delivered. A share callback is not proof that the recipient opened the file. Record the boundary you actually tested.

## Physical-device media matrix

Run on every supported device class that materially changes the route:

- older and newer iPhone models for memory and decode cost;
- iPad size classes for split view, pointer, keyboard, and large media;
- camera-origin HEIC/HEIF samples where the product supports them;
- HDR or gain-map samples on devices and displays that support the feature;
- depth, portrait-effects matte, or spatial samples where the app advertises them;
- low-storage, interrupted network, background/foreground, and thermal pressure conditions;
- no access, revoked access, provider failure, and user cancellation.

Simulator runs can validate deterministic UI and fixture state. They do not prove camera hardware, Photos library behavior, HDR/spatial display, physical memory pressure, sensor-origin metadata, or destination compatibility.

## Accessibility and performance proof

Perform task-based checks, not only snapshots:

- find an image, inspect it, analyze it, edit a proposal, and export using VoiceOver;
- complete the same workflow with large text and long localized strings;
- use reduced transparency and reduced motion through the entire flow;
- verify that loading, invalid, partial, and final states are announced without duplicate noise;
- test keyboard, pointer, Voice Control, Switch Control, and controller paths when in scope;
- measure thumbnail scroll hitching, peak memory, decode time, export time, and cancellation latency;
- collect release-like MetricKit or signpost evidence where the product needs ongoing fleet visibility.

## AI and privacy proof

For every AI route, record:

- exact source revision and frame/index;
- derivative dimensions and whether metadata was included;
- model availability state and model/route version;
- cancellation, timeout, memory-pressure, and fallback behavior;
- generated output, uncertainty, user edits, and acceptance event;
- whether the model ran on device and whether any network route was possible;
- retention and deletion behavior for source, derivative, proposal, and logs.

Do not retain raw GPS, EXIF, XMP, or private media in debug logs. If a diagnostic screenshot includes an image or generated proposal, treat it as potentially sensitive.

## Release artifact proof

Before calling the route release-ready, verify in the archive or signed artifact:

- the correct target and bundle identifier;
- the intended deployment target and SDK;
- Image I/O and any input/AI framework target membership;
- usage descriptions, privacy manifest, and required capabilities for Photos, files, camera, or model assets;
- extension membership if a provider or system extension is involved;
- output format declarations and supported document types;
- a version/build identity tied to the test report;
- no private fixture photographs, GPS, secrets, or debug-only destination URLs.

Release proof still does not guarantee every future OS decoder or external destination. Keep the source freshness log and repeat the matrix when Apple changes the SDK or a product promise expands.

## Related routes

- [Image I/O source, destination, metadata, and media pipelines](../42-framework-deep-dives/54-imageio-source-destination-and-metadata.md)
- [Image I/O media review and metadata design](../21-design-deep-dives/74-imageio-media-review-and-metadata-design.md)
- [Image I/O incremental decode and safe export route](../50-capability-recipes/77-imageio-incremental-decode-and-safe-export-route.md)
- [CGImageSource and CGImageDestination recipes](../70-code-recipes/89-imageio-cgimagesource-and-destination-recipes.md)

## Sources

- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [CGImageSourceStatus](https://developer.apple.com/documentation/imageio/cgimagesourcestatus)
- [CGImageSourceUpdateData](https://developer.apple.com/documentation/imageio/cgimagesourceupdatedata%28_%3A_%3A_%3A%29?language=objc)
- [CGImageSourceCopyPropertiesAtIndex](https://developer.apple.com/documentation/imageio/cgimagesourcecopypropertiesatindex%28_%3A_%3A_%3A%29)
- [CGImageSourceCreateThumbnailAtIndex](https://developer.apple.com/documentation/imageio/cgimagesourcecreatethumbnailatindex%28_%3A_%3A_%3A%29)
- [CGImageMetadata](https://developer.apple.com/documentation/imageio/cgimagemetadata)
- [CGMutableImageMetadata](https://developer.apple.com/documentation/imageio/cgmutableimagemetadata)
- [CGImageDestinationFinalize](https://developer.apple.com/documentation/imageio/cgimagedestinationfinalize%28_%3A%29)
- [CGImageDestinationCopyImageSource](https://developer.apple.com/documentation/imageio/cgimagedestinationcopyimagesource%28_%3A_%3A_%3A_%3A%29)
- [Writing spatial photos](https://developer.apple.com/documentation/imageio/writing-spatial-photos)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performance testing](https://developer.apple.com/documentation/xctest/performance-tests)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
