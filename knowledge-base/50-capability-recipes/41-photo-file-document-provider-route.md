# Photos, Files, document, provider, and AI route

## Use this route when

Use this route when a feature starts from user-owned photos, videos, PDFs, files, or remote documents and ends in a reviewed local record, document edit, export, share, or provider sync.

## Route selector

| Need | First route | Avoid assuming |
| --- | --- | --- |
| One-off photo/video input | PhotosPicker | Picker selection is not a full photo-library grant |
| Multi-item photo selection | PhotosPicker with bounded selection | Every selected item is already local or decodable |
| Library browser/editor | PhotoKit and PHPhotoLibrary | A fetched PHAsset remains current or writable |
| Import an external file | fileImporter/UIDocumentPicker | A URL string preserves access |
| Edit a document in place | FileDocument/ReferenceFileDocument/UIDocument | Serialization equals conflict resolution |
| Build a document app | DocumentGroup | The document format migrates itself |
| Share a projection | Transferable/ShareLink | A share sheet filters sensitive fields for you |
| Preview common files | Quick Look/QuickLookThumbnailing | Preview means editability or trusted content |
| Read/annotate PDF | PDFKit | PDF links, annotations, and text are safe actions |
| Expose remote documents to Files | File Provider extension | Provider callbacks are the same as upload completion |
| On-device AI over content | Selected representation + bounded model | AI can authorize, export, or mutate source content |

## Shared lifecycle

~~~text
idle
  -> choosing
  -> selected
  -> loadingRepresentation
  -> validating
  -> draftReady
  -> aiProposalReady
  -> userReviewed
  -> committing
  -> saved|exported|shared|synced
  -> unavailable|conflict|failed|cancelled
~~~

Make each transition observable and cancellable. Keep source identity and derivative identity separate so deleting a local copy does not accidentally imply that the Photos asset or provider document was deleted.

## Route A: PhotosPicker capture-to-AI

1. Use PhotosPicker for the smallest needed media scope.
2. Filter to images, videos, or Live Photos as the feature supports.
3. Set a selection limit.
4. Request a representation with loadTransferable.
5. Handle iCloud download and cancellation.
6. Validate type, size, orientation, duration, and metadata.
7. Create a draft with asset/provider identity and source revision if available.
8. Run Vision/Core ML/Foundation Models only on the selected representation.
9. Show editable fields and source context.
10. Commit a local record or export only after confirmation.

If the feature needs to revisit the photo library, re-check PhotoKit authorization and fetch freshness. Do not keep arbitrary raw images solely because the AI pipeline once used them.

## Route B: PhotoKit library workflow

1. Check PHPhotoLibrary.authorizationStatus(for:).
2. Explain the requested level of access in context.
3. Request read/write or add-only access only when needed.
4. Fetch assets with a bounded predicate/sort.
5. Register a change observer if the screen depends on library state.
6. Treat limited access, deletion, iCloud availability, and asset changes as normal.
7. Create PHAssetChangeRequest values inside a single user-confirmed change block.
8. Re-fetch or reconcile after the change completes.

For an AI-generated album/title/metadata proposal, show the target assets and destination before the PhotoKit commit. Re-check authorization and current asset existence at commit time.

## Route C: fileImporter and security-scoped file

1. Declare the accepted UTTypes.
2. Present fileImporter or UIDocumentPickerViewController on a user action.
3. Keep the returned URL as a URL.
4. Start security-scoped access and record whether it succeeded.
5. Coordinate the read/write if another process or provider can change the item.
6. Validate content type, size, package structure, and schema.
7. Copy to app-owned storage only when the product needs an independent durable copy.
8. Stop security-scoped access immediately after the operation.
9. If future access is needed, store a deliberately scoped bookmark and handle stale/reselect.

Do not assume that an external URL remains readable after the importer callback. If the user cancels, preserve the existing draft and do not report a failure.

## Route D: document editor

Choose the model:

| Document shape | Route |
| --- | --- |
| Small value snapshot | FileDocument |
| Observable/reference-heavy model | ReferenceFileDocument |
| UIKit document lifecycle/legacy integration | UIDocument |
| Full SwiftUI document app | DocumentGroup |

Define:

- format identifier and UTType;
- schema version and migration;
- readable/writable types;
- atomic save behavior;
- dirty/autosave state;
- external-change/conflict policy;
- package/resource lifetime;
- temporary and partial-write cleanup;
- undo/redo and recovery behavior.

Keep AI rewrites as a draft or operation log until the person accepts them. Store the original document revision and the selected range.

## Route E: provider-backed documents

Use a File Provider extension when other apps need to discover and edit app-owned remote documents. Choose replicated versus nonreplicated architecture deliberately.

The extension route needs:

- a stable item identifier scheme;
- root and child enumerators;
- item metadata and content type;
- placeholder and materialization behavior;
- local/remote version model;
- progress and cancellation;
- upload/download retry;
- remote change signaling;
- conflict and delete semantics;
- extension termination recovery;
- account/offline state.

Expose a user-facing status that distinguishes a queued upload, a completed upload, and a conflict. The main app should remain correct when the extension is terminated between callbacks.

## Route F: Quick Look/PDF/share

### Preview

Use Quick Look for a system preview. If the type is not supported, show a controlled fallback instead of a blank or misleading preview. Use QuickLookThumbnailing for list thumbnails, but do not parse sensitive content solely to make a thumbnail.

### PDF

Use PDFKit for page/text/annotation behavior. Make PDF links and embedded actions explicit. If the app generates or modifies a PDF, validate the output by reopening it, checking page count, annotations, metadata, and expected text.

### Share

Create a redacted share projection, then expose it through Transferable/ShareLink. Provide FileRepresentation when a destination expects a file. Do not make the canonical document itself the share payload if it contains private fields.

## Route G: bounded on-device AI

~~~text
selected source
  -> minimal representation
  -> deterministic parse/validation
  -> on-device model proposal
  -> source-linked review
  -> explicit commit
~~~

Good candidates:

- receipt or form field extraction;
- selected PDF page summary;
- document title/tag suggestion;
- duplicate or related-item suggestion;
- image caption or alt-text draft;
- file naming proposal;
- redacted export draft.

Guardrails:

- keep page/asset/range provenance;
- limit model context to selected material;
- keep typed output and schema version;
- provide edit/reject/undo;
- never let model text open links, mutate Photos, export, share, delete, or upload;
- revalidate source revision and permission before commit;
- omit sensitive content from notifications and system surfaces.

## Native handoff

| Moment | Native surface |
| --- | --- |
| Choose content | PhotosPicker/fileImporter/document picker |
| Read source | Quick Look/PDFView/document editor |
| Inspect metadata | Sheet/inspector with standard SwiftUI hierarchy |
| Review AI | Source-linked card with edit/reject/accept |
| Save | DocumentGroup/autosave or explicit local commit |
| Export | fileExporter with declared content type |
| Share | ShareLink or system activity surface |
| Provider status | Native list row/status badge with offline/conflict detail |

Use Liquid Glass to group actions such as Extract, Edit, Save, Export, and Share. Keep source content readable and put destructive actions behind explicit confirmation.

## Failure matrix

| Failure | Preserve | Fallback |
| --- | --- | --- |
| Picker cancelled | Existing draft | Keep screen ready |
| Representation load fails | Source identifier and error state | Retry, choose another representation |
| iCloud/provider offline | Selection/metadata | Retry or cached preview |
| Photo access limited | Selected items | Manage access or picker route |
| Photo asset deleted | Local derivative/provenance | Mark source unavailable |
| Security scope denied | Current draft | Reselect file |
| Bookmark stale | Bookmark record | Ask user to choose again |
| External file changed | Previous snapshot | Compare/reload/save copy |
| Document corrupt | Original bytes/copy | Recovery/import-as-new |
| File Provider conflict | Both revisions/IDs | User choice or explicit merge |
| PDF malformed/encrypted | Safe error | Quick Look/alternate app/manual |
| Share representation rejected | Canonical record | Offer another declared type |
| AI output invalid | Original source/draft | Manual editing |
| Commit permission changed | Proposal and source | Ask again or cancel |

## Verification questions

- Is the chosen route PhotosUI selection, PhotoKit library access, Files import, document editing, provider sync, preview, or share?
- What is the source identity and revision?
- When is a representation loaded, copied, or retained?
- Are security scopes balanced and bookmarks recoverable?
- Can the person recover from provider/offline/corrupt/conflict states?
- Does the document format have a schema/migration policy?
- Is the share projection redacted before Transferable is created?
- Can an AI proposal be rejected without changing the source?
- Does the signed target contain the required app/extension capabilities and privacy strings?
- What was tested on a physical device versus a fixture?

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [PHPhotoLibrary](https://developer.apple.com/documentation/photos/phphotolibrary)
- [Delivering an Enhanced Privacy Experience in Your Photos App](https://developer.apple.com/documentation/photokit/delivering-an-enhanced-privacy-experience-in-your-photos-app)
- [Requesting Changes to the Photo Library](https://developer.apple.com/documentation/photokit/requesting-changes-to-the-photo-library)
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
- [Quick Look Thumbnailing](https://developer.apple.com/documentation/quicklookthumbnailing)
- [PDFKit](https://developer.apple.com/documentation/pdfkit)
- [PDFView](https://developer.apple.com/documentation/pdfkit/pdfview)
- [PDFAnnotation](https://developer.apple.com/documentation/pdfkit/pdfannotation)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
