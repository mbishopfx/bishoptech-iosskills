# Quick Look and QuickLookThumbnailing preview pipeline

Quick Look is Apple’s system-owned way to preview common files inside an app. QuickLookThumbnailing is a non-UI framework for producing thumbnail representations. They solve related but different problems:

~~~text
file reference
  -> type and access validation
  -> thumbnail for browse/list context
  -> Quick Look preview for inspection
  -> optional simple system edit or app-owned review
  -> canonical save/export/AI action
~~~

A thumbnail is not a preview. A preview is not a parsed domain model. A preview edit is not an app database mutation. Keep those boundaries explicit.

## Choose the route by user outcome

| User outcome | Primary route | What it owns |
| --- | --- | --- |
| Show a common document, image, audio/video file, PDF, or USDZ | Quick Look QLPreviewController | System preview UI, navigation, supported basic interactions, and preview lifecycle. |
| Show a file card in a list or grid | QuickLookThumbnailing QLThumbnailGenerator | Asynchronous icon/low-quality/high-quality thumbnail representations. |
| Give Files, Finder, Spotlight, or iCloud a thumbnail for a proprietary format | Thumbnail Extension and QLThumbnailProvider | A separate extension target that renders a bounded thumbnail for declared UTIs. |
| Preview a proprietary format | Quick Look Preview Extension | A view-based QLPreviewingController or data-based QLPreviewProvider/QLPreviewReply route. |
| Perform advanced editing or playback | Lower-level app framework such as PDFKit, AVFoundation, ImageIO, or a custom editor | App-owned editing semantics, validation, persistence, and accessibility. |
| Extract content for AI | App-owned parser/OCR/media route after user selection and validation | Typed observations and source provenance; Quick Look remains a viewing surface. |

Do not select Quick Look merely because a file has an extension. Check the actual URL, security scope, content type, file size, and whether the current OS supports the intended preview.

## Quick Look inside an app

QLPreviewController is a UIKit view controller. Its data source supplies QLPreviewItem values and the number of items in the preview navigation list. A preview item exposes a previewItemURL and may provide a previewItemTitle. The controller canPreviewItem check is useful before offering a preview action.

The common supported types include iWork and Microsoft Office documents, RTF, PDF, images, text, CSV, audio/video, Live Photos, and USDZ on iOS and iPadOS. Apple notes that the supported common file list can change between operating-system releases. Maintain a visible fallback when the controller cannot preview an item.

The controller can be presented modally or pushed through a navigation controller. In a SwiftUI app, UIViewControllerRepresentable is the normal bridge. The Coordinator forwards data-source and delegate callbacks, including preview dismissal, URL-opening policy, and editing callbacks where the selected system route supports them.

The QLPreviewControllerDelegate contract matters:

- previewControllerWillDismiss and previewControllerDidDismiss are lifecycle observations, not save confirmations;
- shouldOpen lets the app decide whether a tapped URL should leave the preview;
- editingModeFor describes how the preview handles supported edits;
- didUpdateContentsOf and didSaveEditedCopyOf report system preview editing outcomes;
- transition callbacks can provide a source view or image for a zoom animation, but they do not change content authority.

Do not modify the Quick Look view hierarchy. Use app-owned controls before the preview or lower-level frameworks when the product needs a custom toolbar, an always-visible inspector, advanced playback, or a domain-specific editing workflow.

## Preview extensions for custom files

When the app owns a proprietary file type, a Quick Look Preview Extension can make that type previewable to Files, Spotlight, and other system surfaces. Declare the exact supported content types in the extension’s QLSupportedContentTypes entry.

There are two main extension shapes:

### View-based preview

A view controller conforms to QLPreviewingController and implements at least one relevant preparation method, such as preparePreviewOfFile(at:completionHandler:). The completion handler tells the system when the view is ready. The preview controller is the main surface; avoid presenting additional view controllers over it.

The extension should:

- open the file only for the duration needed to prepare or interact;
- avoid heavy work on the main thread;
- validate the file before rendering;
- handle corrupt, missing, encrypted, or stale input;
- keep its UI accessible without relying on app-owned navigation;
- return a clear error to the system when it cannot provide a preview.

### Data-based preview

A subclass of QLPreviewProvider can produce a QLPreviewReply from a QLFilePreviewRequest. A reply can be based on a file URL, PDF drawing, bitmap drawing, or data of a supported content type; it can also include attachments for HTML previews. Use the simplest representation that preserves the content contract and avoids unnecessary memory pressure.

The preview extension is a separate target and process boundary. Its presence in the app target, a local preview in Xcode, or a successful file export does not prove that Files or Spotlight can invoke it. Verify extension membership, Info.plist declarations, signing, supported UTIs, termination/relaunch, and a real system-surface invocation.

## QuickLookThumbnailing

QLThumbnailGenerator.shared generates representations from a QLThumbnailGenerator.Request. The request identifies:

- file URL;
- requested size;
- display scale;
- representationTypes;
- optional contentType;
- minimumDimension and iconMode where appropriate.

Representation types are icon, lowQualityThumbnail, and thumbnail. Request all when a list benefits from progressive replacement; request only what the surface needs when memory and energy matter. The generator may call a progressive update handler as better representations become available, and the request can be cancelled.

Set contentType when the file has no meaningful extension or the app knows the type more accurately than the URL name. If contentType is not set, QuickLookThumbnailing derives content from the extension. A declared type still does not validate bytes; the app needs its own file checks.

QLThumbnailRepresentation exposes a CGImage and, when UIKit is linked, a UIImage. It also exposes the representation type and contentRect. Use contentRect when a document’s actual content occupies only part of the returned image. Do not crop it blindly or assume that the image bounds equal the document’s semantic bounds.

In a memory-constrained File Provider or thumbnail extension, use the saveBestRepresentation route to write a thumbnail to a file URL when appropriate. Clean up the generated file according to the documented lifetime. Do not keep large bitmap data alive across an extension request.

## Custom thumbnail extensions

A Thumbnail Extension uses QLThumbnailProvider and provides a QLThumbnailReply for a custom file type. The extension’s Info.plist must declare exact UTIs in QLSupportedContentTypes. A parent UTI alone is not enough when the system requests a specific child type. QLThumbnailMinimumDimension can prevent the extension from being invoked for sizes too small to render usefully.

The provider receives a QLFileThumbnailRequest with the file URL, maximum/minimum size, and scale. It can return a drawing block or an image file URL. Keep the renderer deterministic, bounded, and safe for untrusted input. Do not use network access, user interaction, or a long-running model session as a required dependency for a tiny system thumbnail.

If the file cannot be rendered, return the error or nil reply so the system can use a generic icon. A generic icon is a valid fallback; it is better than a misleading thumbnail that claims content the provider did not parse.

## File, provider, and security boundaries

Quick Look and QuickLookThumbnailing may receive:

- security-scoped URLs from Files;
- provider-backed placeholders;
- iCloud files that need download;
- temporary exports;
- files modified by another process;
- malformed or adversarial content.

Resolve and validate access before handing a URL to the system. Keep a source record, content type, modification state, and local derivative separate. If a provider item changes while a preview is open, mark the app-owned draft stale. Never use a thumbnail as a cache key for a canonical document without the source revision and type.

For custom document types, the file format, UTType declaration, preview extension, thumbnail extension, File Provider metadata, and app parser must agree. Version the file format and make migration explicit. A preview extension that can display an old file does not automatically mean the editor can save it without loss.

## AI and reviewable preview

Quick Look is a useful inspection step before on-device AI:

~~~text
user-selected file
  -> thumbnail/browse
  -> Quick Look inspection
  -> explicit “Analyze” action
  -> bounded parser/OCR/media extraction
  -> typed AI proposal with source locations
  -> user review
  -> app-owned commit or export
~~~

The model should receive the smallest representation required for the selected task. Preserve page number, selection range, time range, or file revision when available. A generated summary, extracted field, or suggested annotation is a proposal, not a modification to the PDF, file, or provider record.

Do not run a model in a thumbnail provider merely because a thumbnail looks like a convenient AI entry point. System thumbnail requests are not user consent for analysis. Keep AI work in the app-owned, user-started route or a specifically authorized extension.

## Native design and accessibility

Use thumbnails for recognition and Quick Look for inspection. Keep titles, file types, source locations, and error states readable when the thumbnail is missing. A Liquid Glass card can contain an app-owned document row or review action, but it should not cover the content with translucent decoration or recreate Quick Look’s system controls.

Test:

- VoiceOver labels for filename, type, revision, thumbnail state, and preview action;
- Dynamic Type with long filenames and localized file types;
- high contrast, reduced transparency, and reduced motion;
- Voice Control, Switch Control, keyboard, and pointer actions;
- URLs and external links inside previews;
- large PDFs, high-resolution media, and memory pressure;
- stale provider files, iCloud download delay, cancellation, and missing thumbnails.

## Evidence checklist

- named app target imports QuickLook or QuickLookThumbnailing and compiles against the selected SDK;
- QLPreviewItem data source and delegate lifecycle are tested;
- canPreviewItem true/false and supported-type fallback are recorded;
- preview editing behavior is tested separately from app-owned persistence;
- custom preview extension target, exact QLSupportedContentTypes, and system invocation are verified;
- QLThumbnailGenerator progressive representations, contentType, scale, cancellation, and error states are measured;
- custom thumbnail extension target, minimum dimension, exact UTI match, and generic-icon fallback are verified;
- file-provider/security-scoped/iCloud/temporary-file lifetimes are tested;
- AI analysis is explicit, bounded, source-linked, and reviewable;
- accessibility, device performance, extension termination, signed artifact, and release evidence are recorded.

## Sources

- [Quick Look](https://developer.apple.com/documentation/quicklook)
- [QLPreviewController](https://developer.apple.com/documentation/quicklook/qlpreviewcontroller)
- [QLPreviewItem](https://developer.apple.com/documentation/quicklook/qlpreviewitem)
- [QLPreviewControllerDataSource](https://developer.apple.com/documentation/quicklook/qlpreviewcontrollerdatasource)
- [QLPreviewControllerDelegate](https://developer.apple.com/documentation/quicklook/qlpreviewcontrollerdelegate)
- [QLPreviewingController](https://developer.apple.com/documentation/quicklook/qlpreviewingcontroller)
- [QLPreviewProvider](https://developer.apple.com/documentation/quicklook/qlpreviewprovider)
- [QLFilePreviewRequest](https://developer.apple.com/documentation/quicklook/qlfilepreviewrequest)
- [QLPreviewReply](https://developer.apple.com/documentation/quicklook/qlpreviewreply)
- [QuickLook Thumbnailing](https://developer.apple.com/documentation/quicklookthumbnailing)
- [QLThumbnailGenerator](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailgenerator)
- [QLThumbnailGenerator.Request](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailgenerator/request)
- [QLThumbnailRepresentation](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailrepresentation)
- [QLThumbnailProvider](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailprovider)
- [QLFileThumbnailRequest](https://developer.apple.com/documentation/quicklookthumbnailing/qlfilethumbnailrequest)
- [QLThumbnailReply](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailreply)
- [Providing Thumbnails of Your Custom File Types](https://developer.apple.com/documentation/quicklookthumbnailing/providing-thumbnails-of-your-custom-file-types)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [File management](https://developer.apple.com/design/human-interface-guidelines/file-management)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
