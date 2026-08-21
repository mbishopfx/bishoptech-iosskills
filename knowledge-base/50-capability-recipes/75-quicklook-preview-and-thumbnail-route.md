# Quick Look preview and thumbnail route

Use this route when a document, media item, custom file, or provider-backed record needs Apple-native recognition and inspection before an app-owned action.

## Select the smallest route

| Need | Route |
| --- | --- |
| Preview a common file inside the app | QLPreviewController with QLPreviewItem data source |
| Decide whether a preview action should be offered | QLPreviewController.canPreviewItem |
| Show a list/grid image | QLThumbnailGenerator with a bounded Request |
| Support a proprietary file in Quick Look | Quick Look Preview Extension |
| Support a proprietary file in Files/Spotlight/iCloud thumbnails | Thumbnail Extension |
| Read fields or run AI | App-owned parser/OCR/media route after explicit user action |

Do not use a thumbnail generator as a document parser or a preview controller as the app’s canonical editor.

## Route contract

~~~text
source URL or provider item
  -> scope/access/type/size validation
  -> thumbnail request for browse state
  -> canPreviewItem check
  -> Quick Look preview
  -> optional system edit or app-owned Analyze action
  -> source revision check
  -> typed app proposal
  -> confirmed app-owned save/export
~~~

## Step 1: establish the source

Store a source reference that survives the screen:

- security-scoped URL or bookmark;
- File Provider identifier and revision;
- local temporary URL with cleanup policy;
- app-owned document identifier and schema version.

Resolve scope only for the operation that needs it. Validate the file’s declared and observed type, size, modification state, and provider availability before requesting a thumbnail or preview.

## Step 2: make the browse surface cheap

Create a QLThumbnailGenerator.Request with the intended size and display scale. Request an icon, low-quality thumbnail, or high-quality thumbnail according to the surface. For scrolling grids, use progressive representations and cancellation; do not start unlimited work for every cell.

Set contentType when the extension is missing or ambiguous. Keep the generated representation tied to the source URL, content type, and revision. If the source changes, invalidate the thumbnail rather than presenting an old image as current.

For a file-provider or extension process, consider saving the best representation to a file URL instead of retaining a large in-memory image. Clean temporary output and provide a generic icon fallback.

## Step 3: open the system preview

Wrap QLPreviewController in UIViewControllerRepresentable when the app is SwiftUI-first. Provide a stable array of QLPreviewItem objects and a Coordinator for data-source/delegate callbacks.

Before presenting:

1. confirm the source remains available;
2. call canPreviewItem;
3. preserve the current source revision;
4. disable duplicate launch actions;
5. present the controller using a supported UIKit context.

On dismissal, reconcile only the evidence returned by the delegate. A preview closing is not a save. A system edit callback is not necessarily the same as the app’s canonical save unless the app adopts the edited copy and validates it.

## Step 4: add custom file support

For a proprietary file:

1. define an exact UTType and schema/version;
2. add a Quick Look Preview Extension if system preview is needed;
3. set QLSupportedContentTypes to the exact UTI values;
4. choose view-based QLPreviewingController or data-based QLPreviewProvider;
5. add a Thumbnail Extension when rich thumbnails are needed;
6. set exact QLSupportedContentTypes and QLThumbnailMinimumDimension;
7. make generic-icon/error fallback valid;
8. test invocation from Files, Spotlight, iCloud, and the app.

The preview and thumbnail extensions are separate targets. Keep their parsing code small, deterministic, and safe for termination. Do not make a cloud connection or an AI model download a prerequisite for a basic preview.

## Step 5: run AI only after intent

~~~text
previewed file
  -> user taps Analyze
  -> app shows source scope/privacy
  -> parser or on-device model
  -> typed proposal with page/time/source locations
  -> review/edit
  -> commit/export
~~~

The app should preserve the original file revision with the proposal. If the file changes after preview, invalidate or re-run the proposal. Never let a model silently modify a PDF, provider item, document record, or thumbnail source.

## Fallbacks

| Failure | Route |
| --- | --- |
| No thumbnail | Generic icon with file title and type |
| Thumbnail cancelled | Keep placeholder and retry on visibility |
| Preview unsupported | App-owned metadata view or explicit open-in/share route |
| Provider unavailable | Preserve source reference and show retry/reselect |
| File corrupt/encrypted | Explain that the content cannot be previewed; do not feed arbitrary bytes to AI |
| Extension missing | App-owned preview or export to supported format |
| AI unavailable | Manual inspection and entry |
| Source changed | Refresh and ask before re-analysis |

## Proof gates

The route is only a route sketch until compiled in the intended target. Verify the real Quick Look UI, custom extension invocation, thumbnail behavior at requested sizes/scales, provider/iCloud availability, cancellation, extension termination, accessibility, and signed target configuration.

## Sources

- [Quick Look](https://developer.apple.com/documentation/quicklook)
- [QLPreviewController](https://developer.apple.com/documentation/quicklook/qlpreviewcontroller)
- [QLPreviewItem](https://developer.apple.com/documentation/quicklook/qlpreviewitem)
- [QLPreviewControllerDataSource](https://developer.apple.com/documentation/quicklook/qlpreviewcontrollerdatasource)
- [QLPreviewControllerDelegate](https://developer.apple.com/documentation/quicklook/qlpreviewcontrollerdelegate)
- [Quick Look Thumbnailing](https://developer.apple.com/documentation/quicklookthumbnailing)
- [QLThumbnailGenerator](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailgenerator)
- [QLThumbnailGenerator.Request](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailgenerator/request)
- [QLThumbnailGenerator.Request.RepresentationTypes](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailgenerator/request/representationtypes-swift.struct)
- [QLThumbnailProvider](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailprovider)
- [Providing Thumbnails of Your Custom File Types](https://developer.apple.com/documentation/quicklookthumbnailing/providing-thumbnails-of-your-custom-file-types)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
