# Photos, Files, Documents, and Provider Access

## Scope

This route covers the boundary between app-owned data and user-owned content selected from Photos, Files, iCloud Drive, or a third-party File Provider. The core design is:

`user intent -> system picker/provider -> scoped representation -> validation/review -> app-owned draft -> durable model -> optional export/share`

The system picker is part of the privacy model. A returned URL, `PhotosPickerItem`, or provider metadata is not automatically a trusted, current, small, local, or retained copy of the user’s content.

## Capability map

| Product need | Preferred route | Why | Common false assumption |
| --- | --- | --- | --- |
| One-off photo/video input | PhotosUI `PhotosPicker` | The person chooses the assets and the app asks for a representation | A picker item is already decoded bytes or a full photo-library permission. |
| Library-wide organization/edit/delete | PhotoKit | Gives the app the authorization and change-observation model for library operations | A selected item implies permission to browse or mutate the rest of the library. |
| Import a file into an app-owned workflow | SwiftUI `fileImporter` or `UIDocumentPickerViewController` | User-mediated access to a supported `UTType` | A URL path can be saved and used forever without a security scope. |
| Open/edit a document in place | `UIDocument`, `FileDocument`, or `ReferenceFileDocument` | Coordinates serialization, autosave, and external-file lifecycle | Reading bytes once is equivalent to supporting edits, conflicts, or provider changes. |
| Build a document app | SwiftUI `DocumentGroup` | Adds document opening/creation and platform document behavior | Any `FileDocument` is automatically a robust multi-version format. |
| Access a folder or remote provider | Directory picker/File Provider | User grants a scoped tree or the provider resolves placeholders/downloads | A folder URL proves that all descendants are local and permanently available. |
| Share a copy | `ShareLink`/`Transferable` or UIKit activity APIs | System handoff with typed representations | The share sheet is allowed to expose every field or embedded metadata. |

## PhotosUI selection is a representation request

`PhotosPicker` returns `PhotosPickerItem` values that act as provider-backed placeholders. Ask for the narrowest content type and load the specific `Transferable` representation needed by the current step. The load is asynchronous and can fail, including when iCloud Photos needs a network connection. Treat a nil or failed representation as an ordinary state, not as a corrupted app database.

Use this staged pipeline:

1. Explain the current feature before presenting the picker.
2. Filter to the media types the feature understands and cap the selection count.
3. Load the representation with cancellation and progress where applicable.
4. Decode and validate dimensions, duration, format, metadata, and size before expensive processing.
5. Create a reviewable app-owned draft with provenance only if the feature needs it.
6. Persist only the minimum derivative or original required by the user-visible outcome.
7. Define deletion and reprocessing behavior if the user removes the source or revokes access.

If the app needs to fetch, edit, or delete arbitrary library assets later, route that feature through PhotoKit authorization and change handling. A picker-first design is usually the least-privilege route for a capture or import workflow.

## Files are URLs with a lifetime, not strings

SwiftUI’s file importer and UIKit’s document picker can return security-scoped URLs for external documents. The app must balance each successful `startAccessingSecurityScopedResource()` with `stopAccessingSecurityScopedResource()` and release the scope as soon as the read/write is complete. A path string loses the security scope; do not turn a scoped URL into a string and expect to recover authorization from it.

If access must survive a later launch, ask whether the product truly needs it. If it does, create and store a security-scoped bookmark only after obtaining the access the documented route requires. When resolving it, handle stale or unresolvable bookmark data, reacquire the scope, and provide a user-facing reselect route. Do not retain a scope throughout the entire app lifetime merely because a bookmark exists.

For external documents, use `NSFileCoordinator` for reads and writes. If the app presents an external document for ongoing viewing/editing, use a file presenter or `UIDocument` lifecycle and handle changes, moves, deletion, eviction, and backgrounding. The coordinator is per operation; keeping a coordinator alive as a global manager can retain presenters and complicate teardown.

## `UIDocument`, `FileDocument`, and `DocumentGroup`

Choose the document abstraction based on ownership and lifecycle:

| Abstraction | Use it for | Implementation seam | Evidence to capture |
| --- | --- | --- | --- |
| `FileDocument` | A value-type document snapshot | `readableContentTypes`, optional `writableContentTypes`, `init(configuration:)`, `fileWrapper(configuration:)` | Sendability/isolation, format version, corrupt input, export failure, and large-file behavior. |
| `ReferenceFileDocument` | A reference-type document with observable edits | Reference document change tracking and serialization callbacks | Autosave, dirty state, conflict handling, and mutation isolation. |
| `DocumentGroup` | A SwiftUI document-based app | One or more document scenes with matching content types | Opening/creating, multiwindow, external provider, migration, and scene restoration. |
| `UIDocument` | Coordinated UIKit document lifecycle | Read/write, autosave, file coordination, presenters | Background behavior, provider changes, version conflicts, and cancellation. |

Keep serialization and domain validation separate. The document format should have an explicit version and migration plan. A `FileDocument` method can be called from different isolation domains, so serialization should not silently depend on a `MainActor` view model or mutate UI state. For a package format, a directory-backed `FileWrapper` can allow targeted rewrites, but the package still needs atomicity, versioning, and recovery from a partial write.

## Directory and File Provider routes

Use a directory-capable document picker when the feature needs a user-selected folder. The returned directory scope can cover descendants and future items in that directory, which makes it powerful and privacy-sensitive. Enumerate lazily, validate symlinks/format/size, and avoid recursively loading an unbounded tree into memory.

If the product owns remote documents that should appear in other apps’ document pickers, use a File Provider extension. Decide between a nonreplicated provider, where the extension manages local copies/placeholders, and a replicated provider, where the system manages local document copies and the extension synchronizes metadata/content with remote storage. That route requires item identifiers, enumerators, versions, placeholders/materialization, upload/download progress, errors, change signaling, and server conflict policy. It is a storage-provider product, not a shortcut for a normal share button.

## App Groups and extension-visible files

Widgets, share extensions, document providers, and the containing app may share an App Group container when the targets are signed for the same group. Keep the shared format small, versioned, privacy-reviewed, and resilient to a process being terminated mid-write. Use a single owner or coordinated/atomic writes; do not have a widget mutate the canonical document while the app is editing it.

An App Group is not a general-purpose secret store. Put credentials and high-value tokens in Keychain with a deliberate accessibility policy. Put widget-safe projections, redacted thumbnails, and pending handoff records in the shared container, and make it possible to delete or rebuild them from the app-owned source of truth.

## API and target route matrix

Choose the representation and target from the user’s ownership intent. A picker, a document app, a provider, and a share extension have different lifecycles and privacy contracts.

| Outcome | API route | Domain handoff | Target/configuration/proof gate |
| --- | --- | --- | --- |
| Select existing photo/video | `PhotosPicker` + `PhotosPickerItem.loadTransferable` | Typed representation, asset/provider ID, dimensions/duration, provenance | Picker-first privacy, transfer cancellation/iCloud availability, representation failure, and physical device/library state. |
| Browse/mutate the library | PhotoKit `PHPhotoLibrary`/fetch/change-observer route | App-owned asset ID and authorized operation | Photo Library capability/usage, read/write authorization, limited-library changes, change observer, and device proof. |
| Import a file copy | SwiftUI `fileImporter` or `UIDocumentPickerViewController` | Scoped URL/temporary copy plus UTType/size/hash | Security-scoped access, provider cancellation/offline, type/size validation, temporary cleanup, and Files/provider test. |
| Edit an external document | `UIDocument`, `FileDocument`, or `ReferenceFileDocument` | Versioned document model and coordinated save result | Autosave, file coordination, external changes, migration, conflict, and process-termination proof. |
| Build a document-based app | `DocumentGroup` | Document scene/model with explicit format version | App target scene/document declarations, multiwindow, create/open/save, corrupt input, and update migration. |
| Expose remote files to other apps | Replicated `NSFileProviderReplicatedExtension` or nonreplicated provider route | Item identifiers, metadata/content versions, progress, errors, change tokens | File Provider extension target, domains/entitlements, enumerator/placeholders/materialization, upload/download/conflict, and real Files integration. |
| Share/export a copy | `Transferable`/`ShareLink`, `NSItemProvider`, or UIKit activity controller | Redacted immutable export snapshot/temporary file | Destination/cancellation, metadata redaction, large-file memory, iPad presentation, and physical share UI. |

## Target and data-ownership register

| Target/process | Owns | Must not assume |
| --- | --- | --- |
| Main app | Canonical model, import/review/edit/export orchestration | A returned URL is permanently accessible or a provider is online. |
| Share/action extension | Host-provided input, short transform, user review, completion/cancel | The containing app is running, the input is fully local, or a long job can remain in memory. |
| Document provider/File Provider | Enumeration, placeholders, fetch/upload, remote change signaling | A network request finishes before expiration or a remote item is a local file. |
| Widget/App Intent projection | Small redacted display state and safe handoff | A widget can open the app’s live model context or write a canonical document without coordination. |
| Shared App Group | Versioned projection, pending handoff, atomic file exchange | It is a secret store, database transaction, or substitute for Keychain/file coordination. |

For every imported or exported artifact retain only the fields needed for the user outcome: source/provider identity, representation/UTType, size/hash when useful, captured/modified time, redaction policy, review state, and deletion/retry state. Keep raw bytes and metadata on an explicit retention path. A provider callback can arrive after the originating view is gone, so the operation must be cancellable and independent of view lifetime.

## Failure and privacy matrix

| Failure/state | User-facing response | Data rule |
| --- | --- | --- |
| Picker canceled | Return to the prior state without an error alarm | Do not create a phantom draft. |
| Provider cannot load representation | Explain retry/offline/unsupported format | Do not mark the item imported. |
| Scope denied or bookmark stale | Ask the person to choose again | Delete or quarantine the unusable bookmark. |
| File moved/deleted by another process | Show a recoverable missing-file state | Do not overwrite a replacement without confirmation. |
| Format invalid/oversized | Show supported types/size and a recovery path | Do not parse untrusted bytes as a valid domain model. |
| App/extension killed during write | Reopen last committed version | Use atomic replacement or a journal/recovery marker. |
| Source contains sensitive metadata | Offer redaction or export policy | Strip location/author/EXIF/custom fields when not required. |

## Verification matrix

- Photos: no selection, one/many selection, unsupported type, iCloud offline, large asset, Live Photo/video duration, limited/full authorization, and denied access.
- Files: local provider, iCloud Drive, third-party provider, folder selection, read-only item, in-place edit, move/delete/evict, revoked bookmark, and low storage.
- Documents: open/create/save/export, corrupt file, migration from every supported version, autosave cancellation, two writers, app update, and process termination.
- Sharing: no destination, cancellation, large file, redacted metadata, temporary-file cleanup, and destination-specific failures.
- Evidence: a simulator or preview proves only the local view path; provider availability, scoped access, Photos behavior, file coordination, performance, and physical device ergonomics need target-device/system-surface testing.

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [loadTransferable(type:)](https://developer.apple.com/documentation/photosui/photospickeritem/loadtransferable%28type%3A%29)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [PHPhotoLibrary](https://developer.apple.com/documentation/photokit/phphotolibrary)
- [PHFetchOptions](https://developer.apple.com/documentation/photokit/phfetchoptions)
- [PHPhotoLibraryChangeObserver](https://developer.apple.com/documentation/photokit/phphotolibrarychangeobserver)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [ReferenceFileDocument](https://developer.apple.com/documentation/swiftui/referencefiledocument)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [fileImporter](https://developer.apple.com/documentation/swiftui/view/fileimporter%28ispresented%3Aallowedcontenttypes%3Aallowsmultipleselection%3Aoncompletion%3A%29)
- [fileExporter](https://developer.apple.com/documentation/swiftui/view/fileexporter%28ispresented%3Adocument%3Acontenttypes%3Adefaultfilename%3Aoncompletion%3Aoncancellation%3A%29)
- [SwiftUI presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [UIDocumentPickerViewController](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller)
- [Providing access to directories](https://developer.apple.com/documentation/uikit/providing-access-to-directories)
- [NSURL](https://developer.apple.com/documentation/foundation/nsurl)
- [startAccessingSecurityScopedResource](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [NSFilePresenter](https://developer.apple.com/documentation/foundation/nsfilepresenter)
- [NSFileProviderReplicatedExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderreplicatedextension)
- [NSFileProviderEnumerating](https://developer.apple.com/documentation/fileprovider/nsfileproviderenumerating)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [Configuring app groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
- [Shared data](https://developer.apple.com/documentation/technologyoverviews/shared-data)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
