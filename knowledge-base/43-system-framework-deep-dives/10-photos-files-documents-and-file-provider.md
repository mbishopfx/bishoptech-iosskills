# Photos, Files, documents, File Provider, Quick Look, and PDF authority

## The authority problem

Media and document features look simple in a mockup because the system already owns much of the hard interaction. The app still needs to distinguish:

| User outcome | Native route | What the app actually receives |
| --- | --- | --- |
| Choose a photo or video for one task | PhotosUI PhotosPicker or PHPickerViewController | A user-selected item whose representation is loaded asynchronously |
| Browse or change the library later | PhotoKit PHPhotoLibrary | Authorized access to an evolving library, possibly limited |
| Import a file from Files | SwiftUI fileImporter or UIDocumentPickerViewController | A security-scoped URL with a lifetime and provider behavior |
| Build a document app | FileDocument/ReferenceFileDocument + DocumentGroup | A document model and a system document lifecycle |
| Expose remote documents to other apps | File Provider extension | A separate process/target that enumerates, materializes, and syncs items |
| Preview or annotate a PDF | Quick Look or PDFKit | A preview/editing surface with its own file and annotation semantics |
| Share a copy or representation | Transferable/ShareLink or UIKit sharing | A system handoff of explicitly declared representations |

Do not treat a picker result, URL, Photos asset, PDF annotation, or provider item as canonical business truth without validating its scope, freshness, format, ownership, and user intent.

## Ownership and lifecycle map

Use this chain:

~~~text
user selects or opens content
  -> system grants scoped representation/access
  -> app validates type/size/encoding/provenance
  -> app creates an editable draft
  -> user reviews and confirms
  -> app stores the minimum durable derivative
  -> optional export/share/provider sync/system projection
~~~

The system picker is part of the privacy boundary. A Photos picker can provide selected content without broad photo-library authorization. A document picker can provide a URL outside the app sandbox, but the security scope must be acquired and released correctly. A File Provider can make remote content appear local while the bytes remain unavailable or change between requests.

Keep these values separate in the domain layer:

- source identity: Photos asset identifier, file-provider item identifier, URL/bookmark, or imported copy ID;
- current representation: image/video/data/document snapshot;
- source revision or modification date;
- content type and declared conformance;
- access scope and expiration/reselect requirement;
- local derivative or cache;
- user edits and AI proposals;
- export/share/provider sync state;
- deletion and retention policy.

## PhotosUI: least-privilege selection

PhotosUI provides a system picker for choosing photos and videos. The app can filter media types, cap selection, and ask for a representation through PhotosPickerItem. The picker gives the app access to the items the person explicitly chooses, which is often the right route for a capture-to-AI feature.

### Selection route

1. Explain the feature in the surrounding screen.
2. Present PhotosPicker or PHPickerViewController in response to an intentional action.
3. Filter to the supported media types.
4. Limit selection count and preferred encoding.
5. Load the needed Transferable representation asynchronously.
6. Handle cancellation, iCloud download failure, unsupported representation, and large content.
7. Validate size, dimensions, duration, orientation, metadata, and format.
8. Show a reviewable draft before saving or sending content to an AI pipeline.

Loading a picker item is a request for a representation, not a promise that the bytes are already local. The load may require network access to iCloud Photos. Treat failure and cancellation as normal states. If the product only needs a thumbnail or a downsampled image for classification, do not request a full-resolution original by default.

### When PhotoKit is the right route

Use PhotoKit when the product needs to fetch a library collection, observe changes, create or delete assets, edit content, or offer a library-management workflow. Ask for the smallest access level:

| Need | Access decision |
| --- | --- |
| Add generated media only | Add-only access |
| Read selected/library assets and potentially edit | Read/write access |
| One-off user-selected input | Prefer PhotosUI first; broad PhotoKit access may be unnecessary |
| Limited-library experience | Model limited authorization and the person’s evolving selection |

Check PHPhotoLibrary.authorizationStatus(for:) before offering a route. Request access in context, not during app launch. If the person changes limited-library selection, refresh the app’s assumptions and provenance. A Photos asset can change or disappear; do not use a stale fetch result as an unconditional write target.

### PhotoKit mutation

PhotoKit asset and collection objects are immutable representations. Use PHPhotoLibrary change requests inside performChanges or performChangesAndWait. Combine related mutations into one change block when the user expects an atomic operation. Report success and error separately from the fact that a change request was constructed.

If an AI feature proposes adding an image or album, the proposal must stop before the PhotoKit change request. Show the destination, asset list, metadata, and privacy impact. Require explicit confirmation, then re-check authorization and source availability before committing.

## Files: scoped URLs and coordination

The file importer and document picker are user-mediated access routes. A returned URL can reference a file in Files, iCloud Drive, or a third-party provider. It may be a placeholder, may need download, and may become unavailable.

### Security-scoped access

When a route returns a security-scoped URL:

1. Keep the URL value, not only its path string.
2. Call startAccessingSecurityScopedResource().
3. If it returns true, balance it with stopAccessingSecurityScopedResource().
4. Do the smallest read/write operation possible.
5. Release the scope immediately after the operation.
6. If the app needs future access, use a deliberate security-scoped bookmark strategy and handle stale/reselect states.

Leaking scopes consumes kernel resources. Keeping a scope open for the whole app lifetime is not a persistence strategy. A bookmark does not mean the file is still present, readable, or authorized; resolve it, check staleness, reacquire access, and provide a reselection route.

### Coordinated file access

Use NSFileCoordinator and NSFilePresenter/UIDocument when a file can be changed by another process or provider while the app is reading or writing it. Coordinate each operation on the appropriate thread/queue. On iOS, active file presenters and backgrounding have lifecycle implications; remove and re-add presenters according to the documented rules.

The coordinator is not a document database. It prevents conflicting operations from corrupting cooperating presenters. The app still needs:

- atomic writes or a package-level transaction;
- format version and migration;
- conflict policy;
- temporary-file cleanup;
- cancellation and provider errors;
- reloading when an external change wins.

## FileDocument, ReferenceFileDocument, and DocumentGroup

### FileDocument

FileDocument is a Sendable value-type serialization contract. It declares readable and writable UTTypes, constructs a document from a read configuration, and emits a FileWrapper from a write configuration. SwiftUI may invoke these methods from different isolation domains, so serialization should not depend on main-actor UI state.

Use a single file for a compact document or a directory FileWrapper package when independent subfiles improve incremental updates. In both cases:

- define a schema/version inside the format;
- reject malformed or unsafe content;
- migrate old versions explicitly;
- avoid serializing transient UI state;
- ensure all required resources are inside or referenced by a clear policy;
- test interrupted writes and partial packages.

### ReferenceFileDocument

Use ReferenceFileDocument when a reference-type model owns observable edits or a document is too large/complex to treat as an immutable value snapshot. Keep serialization and UI mutation coordinated. The document object should expose a clear dirty/commit state rather than allowing a view to infer it from arbitrary changes.

### DocumentGroup

DocumentGroup supplies a SwiftUI document scene. On iOS, it contributes document-browser behavior and multiwindow support. The content types declared by the document model determine which files the scene can open. DocumentGroup is not a substitute for a file format, conflict policy, or migration plan.

Separate:

~~~text
document file format
  -> document model
  -> editing state
  -> autosave/commit
  -> file/provider coordination
  -> system document scene
~~~

If the product also has a private local-first database, do not silently treat the document file and database record as two mutable sources of truth. Pick an ownership model and define import/export boundaries.

## File Provider: a different product boundary

Use File Provider when the app owns or syncs remote documents that should appear in Files and other apps. The extension is a separate target/process with a system protocol.

### Replicated provider

With NSFileProviderReplicatedExtension, the system manages local copies while the extension reports metadata, fetches content, handles create/modify/delete, and synchronizes with remote storage. The provider needs item identifiers, enumerators, versions, placeholders/materialization, Progress-returning operations, completion handlers, and server conflict semantics.

### Nonreplicated provider

With NSFileProviderExtension, the extension manages the local copy and placeholder behavior. This can be appropriate for a provider that needs direct control, but it increases lifecycle and correctness responsibility.

### Provider states

Model provider item state explicitly:

| State | Meaning |
| --- | --- |
| enumerated | Metadata exists; content may not |
| placeholder | The system knows the item but bytes are not materialized |
| downloading | Content request is active and cancellable |
| materialized | A local copy is available for the current operation |
| locally-edited | The device has a change that needs upload |
| remote-changed | Server revision differs from the local base |
| conflict | The provider needs a resolution policy |
| unavailable | Account/network/provider/permission prevents access |
| deleted | The item is no longer valid at the source |

Do not call a provider item “saved” because an upload was requested. Require the provider’s completion state and a reconciliation strategy.

## UTType is part of the contract

Use Uniform Type Identifiers to describe content for storage, import, export, and transfer. For a proprietary document type, declare a unique reverse-DNS identifier, choose exported versus imported ownership correctly, and declare conformance to the appropriate system type. Do not invent a new identifier for a type another app already owns.

Use UTType in:

- PhotosPicker filters and Transferable representations;
- FileDocument readable/writable content types;
- fileImporter/fileExporter;
- DocumentGroup;
- Quick Look supported content types;
- document-provider item metadata;
- ShareLink and drag/drop transfer.

Type conformance influences which system surfaces can display or accept a document. Validate the actual bytes too; a file extension or declared type is not sufficient input validation.

## Quick Look, thumbnails, and PDFKit

Use Quick Look for a system preview of common files and custom preview extensions when the app owns a proprietary format. The supported common file list can change between OS releases, so maintain a fallback.

Use QuickLookThumbnailing for fast thumbnails of common files such as images, text, PDFs, media, and USDZ on supported platforms. A thumbnail is a visual projection, not a full-content parse and not proof that an asset can be opened or edited.

Use PDFKit when the product needs document-level PDF behavior:

- PDFDocument for loading, searching, and writing PDF data;
- PDFView for display, navigation, selection, zoom, copy, and page history;
- PDFPage/PDFSelection for page and text operations;
- PDFAnnotation for links, markup, form widgets, and other annotation types.

Treat PDF content as untrusted input. Validate file size, page count, malformed/encrypted behavior, external links, annotation actions, embedded media, and export policy. AI extraction should preserve page/selection coordinates and the original PDF revision. An AI-generated highlight is a proposal until the person reviews it.

## Transferable and ShareLink

Transferable declares one or more representations of a type. ShareLink presents the system sharing UI for a Transferable item. Prefer a FileRepresentation when the destination expects a file, and include only the representations that the product is prepared to share. A source object may contain fields that should never enter a share payload.

Build a share snapshot:

~~~text
canonical record
  -> redacted share projection
  -> declared UTType/TransferRepresentation
  -> optional preview
  -> system share surface
~~~

Do not make the system share surface the place where privacy filtering happens accidentally. Redact before the Transferable representation is produced. Test destinations that accept URLs but not arbitrary data and vice versa.

## On-device AI over media and documents

Use AI after the user selects the source and the app establishes a bounded representation:

| Input | Useful on-device task | Guardrail |
| --- | --- | --- |
| Selected photo or scan | OCR, field extraction, classification | Keep source asset ID and bounding boxes; show editable fields |
| Selected PDF pages/text | Summarization, checklist, question answering | Preserve page/selection citations; do not silently send the whole document |
| User-owned document draft | Rewrite, tagging, outline, metadata suggestion | Never overwrite canonical content without a review/undo path |
| File-provider item metadata | Search or summarize titles/tags | Do not materialize/download content without user-authorized need |
| Room/media export | Generate a description or filename | Avoid exposing sensitive content in notifications or sharing previews |

The model cannot grant Photos, Files, provider, or share authorization. It cannot decide that a document is safe to export or that a PDF link should be opened. Store source IDs, selected ranges, prompt/context/model version, proposal, user edits, and commit outcome if an AI result becomes durable.

## Native design and Liquid Glass

Use system-owned surfaces where they express the user’s intent:

- PhotosPicker for choosing Photos content;
- fileImporter/fileExporter or DocumentGroup for document access;
- Quick Look for a standard preview;
- PDFView for a focused PDF reading/editing surface;
- ShareLink for a system share action.

Use Liquid Glass around app-owned actions and metadata, not as a permanent opaque layer over a document or image. A native review surface can use a glass toolbar with actions such as Edit, Extract, Save, and Share while leaving the source media readable.

Make these states distinct:

- no source selected;
- selection loading;
- representation downloading;
- unsupported format;
- permission limited/denied;
- provider unavailable;
- draft ready for review;
- AI proposal ready;
- saving/coordination in progress;
- conflict or external change;
- export/share complete;
- source deleted or access revoked.

Every state needs a non-AI, non-animation explanation and a recovery path.

## Privacy and retention

Photos, documents, PDFs, and provider content can contain personal, financial, health, location, or household information. Define:

- whether the original is retained;
- whether only a derivative is retained;
- whether thumbnails are redacted;
- whether AI input is local-only;
- whether provider content is downloaded;
- what appears in logs, notifications, widgets, search, and share previews;
- how the user deletes the source, derivative, cache, bookmark, and shared projection.

A permission prompt is not a retention policy. A local model is not permission to expose its output on a lock screen.

## Verification stop list

- PhotosPicker and PHPicker selection/cancellation, multi-selection, iCloud retrieval failure, and limited library boundaries.
- PhotoKit authorization levels, limited-library changes, asset deletion/change observation, and mutation confirmation.
- File importer/document picker security-scoped access, cancellation, provider offline state, and balanced scope release.
- Security-scoped bookmarks, stale resolution, reselection, and app relaunch.
- FileDocument/ReferenceFileDocument read/write, Sendable isolation, corrupt input, version migration, large documents, package partial failure, and autosave.
- DocumentGroup open/create/multiwindow/Files behavior on the intended target.
- File Provider enumerator, placeholder, materialization, upload/download, conflict, cancellation, and extension termination.
- UTType declaration and actual content validation.
- Quick Look preview/thumbnail fallback and custom extension process behavior.
- PDFKit malformed/encrypted PDF, annotation/link policy, selection, export, and accessibility.
- ShareLink redaction and destination-specific representations.
- AI proposal review, source citations, rejection, deletion, and no-hidden-export/share/provider mutation.
- Dynamic Type, VoiceOver, Voice Control, Reduce Motion, Increased Contrast, reduced transparency, localization, and large document/media performance.
- Signed target capabilities, extension membership, privacy declarations, App Group configuration, and release artifact inspection.

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [Photos](https://developer.apple.com/documentation/photokit)
- [PHPhotoLibrary](https://developer.apple.com/documentation/photos/phphotolibrary)
- [Delivering an Enhanced Privacy Experience in Your Photos App](https://developer.apple.com/documentation/photokit/delivering-an-enhanced-privacy-experience-in-your-photos-app)
- [Requesting Changes to the Photo Library](https://developer.apple.com/documentation/photokit/requesting-changes-to-the-photo-library)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [ReferenceFileDocument](https://developer.apple.com/documentation/swiftui/referencefiledocument)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [File importer and exporter presentation](https://developer.apple.com/documentation/swiftui/view-presentation)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [Defining file and data types for your app](https://developer.apple.com/documentation/uniformtypeidentifiers/defining-file-and-data-types-for-your-app)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [startAccessingSecurityScopedResource](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [NSFileProviderReplicatedExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderreplicatedextension)
- [Replicated File Provider extension](https://developer.apple.com/documentation/fileprovider/replicated-file-provider-extension)
- [Quick Look](https://developer.apple.com/documentation/quicklook)
- [QLPreviewController](https://developer.apple.com/documentation/quicklook/qlpreviewcontroller)
- [Quick Look Thumbnailing](https://developer.apple.com/documentation/quicklookthumbnailing)
- [Creating Quick Look Thumbnails to Preview Files in Your App](https://developer.apple.com/documentation/quicklookthumbnailing/creating-quick-look-thumbnails-to-preview-files-in-your-app)
- [PDFKit](https://developer.apple.com/documentation/pdfkit)
- [PDFView](https://developer.apple.com/documentation/pdfkit/pdfview)
- [PDFDocument](https://developer.apple.com/documentation/pdfkit/pdfdocument)
- [PDFAnnotation](https://developer.apple.com/documentation/pdfkit/pdfannotation)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
