# Quick Look preview and thumbnail proof matrix

This matrix separates file access, thumbnail generation, system preview, custom extensions, AI analysis, and canonical persistence. A thumbnail or preview is evidence of a visual route only; it is not evidence that the file is valid, saved, synchronized, or semantically understood.

## Claim-to-evidence matrix

| Claim | Evidence required | Do not infer |
| --- | --- | --- |
| The app can preview an item | Target compiles, QLPreviewItem is valid, and QLPreviewController.canPreviewItem returns true in the target environment | Any file extension is previewable on every OS. |
| The user saw the current file | Source access, revision check, real Quick Look surface, and preview lifecycle record | A cached thumbnail or stale URL is current. |
| The preview can be edited | Delegate editing mode and updated/edited-copy callback tested with the exact file type | Opening a preview makes the app’s canonical record editable. |
| A thumbnail is available | QLThumbnailGenerator request, representation callback, source revision, size, scale, and fallback state recorded | A thumbnail is a full parse or a semantic summary. |
| Progressive thumbnails work | Icon/low-quality/high-quality callbacks, cancellation, replacement, and cell reuse tested | A single callback always represents the final quality. |
| A custom file has a Quick Look preview | Signed Preview Extension target, exact QLSupportedContentTypes, system invocation, valid/invalid file tests | A preview in the app target proves extension invocation from Files or Spotlight. |
| A custom file has a rich system thumbnail | Signed Thumbnail Extension target, exact UTI match, QLThumbnailMinimumDimension, requested-size/scale tests | Declaring a parent UTI or adding a file icon proves the extension works. |
| Provider content is ready | Provider item state, materialized bytes, security scope, iCloud/download state, and source revision | Enumerated metadata means the content is local and readable. |
| AI analyzed the source | Explicit user action, bounded input, parser/model output, source locations, and proposal review | A system thumbnail request is consent to run AI. |
| The app saved a result | App-owned write/commit and read-back validation | Preview dismissal or delegate callback is canonical persistence. |
| The file is private | Thumbnail/preview exposure audit across Files, Spotlight, widgets, lock screen, logs, and temporary files | Quick Look automatically redacts sensitive content. |
| The route is accessible | VoiceOver, Dynamic Type, Voice Control, Switch Control, keyboard/pointer, localization, reduced motion/transparency task completion | A thumbnail has an alt label or a preview opens, therefore the workflow is accessible. |
| The route is release-ready | Signed app/extension artifacts, supported target/device matrix, system invocation, performance/termination evidence | A simulator preview, Xcode canvas, or debug build proves release behavior. |

## Test matrix

### Quick Look controller

- one valid preview item and multiple-item navigation;
- canPreviewItem true and false;
- missing URL, security-scoped URL, provider placeholder, iCloud download delay;
- corrupt, encrypted, huge, and unsupported files;
- open/close lifecycle and return to the source screen;
- tapped external URL allow/deny policy;
- supported system edit, updated contents, edited-copy destination, and cancellation;
- iPhone, iPad, and Mac Catalyst behavior where supported;
- VoiceOver, Dynamic Type, reduced effects, keyboard/pointer, and localization.

### Thumbnail generator

- icon, low-quality, thumbnail, and all representation types;
- explicit contentType and extension-derived content type;
- display scale, size, minimumDimension, iconMode, and contentRect;
- progressive update ordering and final fallback;
- cancellation during scrolling and cell reuse;
- missing, stale, provider-backed, huge, malformed, and unsupported files;
- memory, CPU, storage, and thermal behavior for batch generation;
- file-backed saveBestRepresentation cleanup where used.

### Custom extensions

- exact QLSupportedContentTypes and schema version;
- preview extension invocation from the app, Files, Spotlight, and other supported surfaces;
- thumbnail extension invocation at sizes below and above QLThumbnailMinimumDimension;
- missing extension, generic icon, rendering error, termination, relaunch, and concurrent requests;
- no network/model dependency for the basic preview/thumbnail path;
- signed entitlements, target membership, Info.plist, and release artifact inspection.

### AI and privacy

- Analyze is explicit and never triggered by a thumbnail request;
- source scope and revision are visible;
- parser/model failure, unavailable model, ambiguous output, and cancellation;
- source-linked proposal with page/time/selection coordinates;
- changed source invalidates the proposal;
- sensitive thumbnails and previews across system surfaces;
- no private data in logs, screenshots, temporary files, or extension diagnostics.

## Evidence record

~~~text
target:
sdk:
deployment:
device_or_simulator:
source_type_and_uti:
source_revision:
access_scope:
quicklook_can_preview:
thumbnail_request_size_scale:
thumbnail_representation:
custom_preview_extension:
custom_thumbnail_extension:
system_surface:
ai_action:
delegate_or_callback_result:
accessibility_settings:
performance_and_termination:
artifact:
notes:
~~~

Use controlled fixtures. Do not put private documents, personal photos, provider credentials, or production URLs in the repository.

## Sources

- [Quick Look](https://developer.apple.com/documentation/quicklook)
- [QLPreviewController](https://developer.apple.com/documentation/quicklook/qlpreviewcontroller)
- [QLPreviewControllerDataSource](https://developer.apple.com/documentation/quicklook/qlpreviewcontrollerdatasource)
- [QLPreviewControllerDelegate](https://developer.apple.com/documentation/quicklook/qlpreviewcontrollerdelegate)
- [QLPreviewingController](https://developer.apple.com/documentation/quicklook/qlpreviewingcontroller)
- [QLPreviewProvider](https://developer.apple.com/documentation/quicklook/qlpreviewprovider)
- [Quick Look Thumbnailing](https://developer.apple.com/documentation/quicklookthumbnailing)
- [QLThumbnailGenerator](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailgenerator)
- [QLThumbnailGenerator.Request](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailgenerator/request)
- [QLThumbnailRepresentation](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailrepresentation)
- [QLThumbnailProvider](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailprovider)
- [QLFileThumbnailRequest](https://developer.apple.com/documentation/quicklookthumbnailing/qlfilethumbnailrequest)
- [Providing Thumbnails of Your Custom File Types](https://developer.apple.com/documentation/quicklookthumbnailing/providing-thumbnails-of-your-custom-file-types)
- [File management](https://developer.apple.com/design/human-interface-guidelines/file-management)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
