# SwiftUI document and file-workflow capability route

## Use this route when

Choose this route when the feature owns a user-facing file or document:

- a new or existing document is opened in a document browser;
- a file type has a stable Uniform Type Identifier;
- the editor must read, mutate, autosave, export, move, or share content;
- a reference-backed document needs change tracking and undo;
- a security-scoped URL or File Provider URL crosses an interaction boundary;
- the app must distinguish its source document from an exported projection;
- an iPadOS or Mac Catalyst editor needs document/window adaptation;
- an on-device AI review must be tied to the exact saved revision.

Do not make a generic in-memory model pretend to be a document. Decide where
the document is authoritative, how a URL is scoped, which format is written,
and which action commits a review before building the editor.

## Route contract

Write this contract before selecting an API.

| Contract field | Required decision |
| --- | --- |
| User task | Create, open, edit, review, export, move, share, or synchronize? |
| Document kind | What does one document mean to the user? |
| File type | Which UTType is imported, exported, or owned? |
| Format | Which versioned on-disk representation is authoritative? |
| Scene route | DocumentGroup, current scene picker, or a separate window? |
| Model route | FileDocument for value data or ReferenceFileDocument for a reference object? |
| Identity | Document ID, file URL, domain ID, scene/window identity, and source revision |
| URL scope | App-owned URL, security-scoped URL, bookmark, provider URL, or temporary URL |
| Provider | Local file system, Files provider, File Provider extension, or remote service |
| Save policy | Autosave, explicit export, coordinated write, conflict, and recovery |
| Transfer | Transferable projection, share item, export file, or move operation |
| AI | Capability, source revision, candidate, review, commit, cancellation, and privacy |
| Targets | iPhone, iPadOS, Mac Catalyst, visionOS, watchOS companion, extensions |
| Input | Touch, keyboard, pointer, Pencil, VoiceOver, Switch Control, and commands |
| Proof | Compile, fixture, UI, physical, provider/system, performance, archive, release |

## Route selector

Use the smallest route that preserves the user's file meaning.

| Need | Primary route | Boundary to verify |
| --- | --- | --- |
| A normal document browser with create/open/save | DocumentGroup | Document scene identity and target availability |
| A value-backed document format | FileDocument | Read/write format, errors, version migration |
| A reference-backed model with observable edits | ReferenceFileDocument | Change signaling, undo, coordination, and reference lifetime |
| Import one or more user-selected files | fileImporter | Security-scoped access and type validation |
| Create a file outside the current document | fileExporter | Export format, destination, cancellation, and naming |
| Move a file to a user-selected destination | fileMover | Source ownership, provider behavior, and cancellation |
| Share a file or representation | ShareLink/Transferable | Representation, privacy, and temporary-file lifetime |
| Expose remote or synchronized files to Files | File Provider | Extension process, placeholders, materialization, and sync |
| Transfer a large file representation | Transferable FileRepresentation | Streaming/temporary-file cleanup and type contract |
| Persist app records, not user files | SwiftData/CloudKit or another store | Record identity, sync, migration, and authorization |
| Optional AI review of document text | Foundation Models adapter | Capability, source revision, candidate review, and commit |

## 1. Model document identity explicitly

A file workflow usually has several IDs. Keep them separate.

~~~swift
struct DocumentRoute: Hashable, Codable, Sendable {
    let documentID: UUID
    let sourceRevision: Int
    let sceneToken: String
}

struct DocumentSnapshot: Sendable {
    let documentID: UUID
    let fileURL: URL?
    let formatVersion: Int
    let sourceRevision: Int
    let content: String
}
~~~

The document route is a small presentation value. The loaded document model is
the current authorized truth. A URL can identify a file location, but it does
not by itself authorize access, prove the file has not changed, or define the
domain record that an AI candidate should update.

At the feature boundary, resolve:

1. the requested document or file;
2. current authorization and account;
3. the URL access scope;
4. the supported UTType and format version;
5. the latest source revision;
6. the editor state and save coordinator.

Reject deleted, unauthorized, malformed, or stale input with a repairable state.

## 2. Choose DocumentGroup for a document scene

Use DocumentGroup when the app's primary experience is one document per scene
or window. The scene owns the document lifecycle while the editor owns the
document content and task presentation.

~~~swift
@main
struct NotesApp: App {
    var body: some Scene {
        DocumentGroup(newDocument: NoteDocument()) { configuration in
            NoteEditor(
                document: configuration.$document,
                fileURL: configuration.fileURL
            )
        }
    }
}
~~~

Treat the configuration as the seam between system document management and the
editor:

- configuration.$document is the editable document binding;
- configuration.fileURL is useful context, not a replacement for document
  identity or access policy;
- the editor should show loading, unavailable, dirty, saving, conflict, and
  committed states;
- source format and UTType belong to the document contract, not to a toolbar
  label;
- a document scene should not silently become a generic database editor.

If the task is a temporary import into an existing workspace, use a picker and
an explicit import transaction instead of creating a new document scene.

## 3. Implement the document format as a versioned contract

A FileDocument should make the representation and failure path explicit.

~~~swift
struct NoteDocument: FileDocument, Equatable, Sendable {
    static var readableContentTypes: [UTType] { [.bishopNote] }
    static var writableContentTypes: [UTType] { [.bishopNote] }

    var title: String
    var body: String
    var formatVersion: Int = 1

    init(configuration: ReadConfiguration) throws {
        guard let data = configuration.file.regularFileContents else {
            throw NoteDocumentError.missingContents
        }
        self = try NoteDocumentDecoder.decode(data)
    }

    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        let data = try NoteDocumentEncoder.encode(self)
        return FileWrapper(regularFileWithContents: data)
    }
}
~~~

The decoder should:

- validate the container before reading fields;
- accept only supported versions or perform an explicit migration;
- reject oversized, truncated, or invalid content;
- preserve user data where migration is safe;
- never execute content as code;
- report a useful recovery action.

The writer should:

- emit one canonical format;
- use a temporary/coordinated write where the owning system requires it;
- avoid writing a new format version without a migration plan;
- make large content and binary attachments explicit;
- be deterministic enough for tests and conflict inspection.

For a reference-backed model, use ReferenceFileDocument when the document is
better represented by a long-lived reference object. The reference must signal
changes correctly and coordinate its own mutation, undo, and lifetime. Do not
choose it merely to avoid designing a value representation.

## 4. Declare the UTType boundary

Register a custom type only when the app owns a meaningful file format.

~~~swift
extension UTType {
    static let bishopNote = UTType(
        exportedAs: "dev.bishoptech.note",
        conformingTo: .data
    )
}
~~~

The declaration, document readable/writable types, importer allowed types,
exporter content types, ShareLink representation, and File Provider metadata
must agree. Test:

- the app's own file opens;
- a file with the same extension but invalid contents fails safely;
- a valid file is visible in the intended system picker;
- export uses the expected type and filename;
- unsupported versions show a recovery path;
- provider metadata does not claim a format the app cannot read.

If the app only imports a system type, use the narrowest existing UTType instead
of inventing a custom one.

## 5. Import a file with a scoped access lifetime

A user-selected external URL may require security-scoped access. Treat access as
a bounded capability.

~~~swift
struct ImportedFile: Sendable {
    let url: URL
    let data: Data
}

func readImportedFile(_ url: URL) throws -> ImportedFile {
    let didStart = url.startAccessingSecurityScopedResource()
    defer {
        if didStart {
            url.stopAccessingSecurityScopedResource()
        }
    }

    let values = try Data(contentsOf: url, options: [.mappedIfSafe])
    return ImportedFile(url: url, data: values)
}
~~~

The importer boundary should:

1. confirm the URL and resource type;
2. start access only for the operation that needs it;
3. avoid retaining an inaccessible URL as if it were app-owned;
4. copy or adopt content according to the product's ownership policy;
5. stop access on every path;
6. persist a security-scoped bookmark only when the feature truly needs
   later access and the platform contract supports it;
7. re-resolve and revalidate a bookmark before later reads or writes.

A temporary import should become app-owned data or a durable document in one
explicit transaction. Do not leave the editor pointing at a URL whose access
scope ended.

## 6. Keep export, move, and share distinct

These actions have different ownership semantics.

| Action | User meaning | Design consequence |
| --- | --- | --- |
| Export | Make a copy or representation at a chosen destination | Original document remains authoritative |
| Move | Change the file's location | Source identity and provider coordination change |
| Share | Give another surface a representation or access | Recipient and temporary-file lifetime matter |
| Save | Persist edits to the current document | Autosave/conflict/recovery rules apply |
| Import | Bring content into this app's domain | Type, migration, and ownership rules apply |

Show the correct system action and name it precisely. Do not label an export
"Save" if the original document is unchanged. Do not call a move a share.

For large data, make the transfer representation streamable or file-backed and
clean up temporary artifacts after the receiving system has consumed them.

## 7. Design for File Provider and coordinated access

A provider-backed URL can be available, downloading, evicted, offline, or
temporarily unavailable. The editor must expose those states instead of
pretending every URL is a local byte array.

Use File Provider when the product needs to expose a remote or synchronized
document collection to system file surfaces. Define:

- item identity and parent/container identity;
- placeholder versus materialized content;
- fetch/upload/delete/rename behavior;
- metadata and content type;
- offline and authentication states;
- conflict and version policy;
- extension process boundaries;
- cancellation and retry;
- security and account isolation.

Coordinate reads and writes around files that another process can mutate. An
NSFileCoordinator/NSFilePresenter design belongs at the file-ownership boundary,
not scattered through text-field callbacks. If the app is both a document editor
and a provider client, test provider state changes while the editor is open.

## 8. Make autosave, versioning, and conflicts visible

A document editor should answer "is my work safe?" without requiring the user to
understand Foundation internals.

Represent at least:

~~~swift
enum DocumentSaveState: Equatable, Sendable {
    case clean(revision: Int)
    case dirty(revision: Int)
    case saving(revision: Int)
    case saved(revision: Int)
    case conflict(local: Int, remote: Int)
    case failed(revision: Int, message: String)
}
~~~

The state machine should specify:

- when edits mark the document dirty;
- whether the system document scene autosaves and when app work must
  checkpoint separately;
- how cancellation affects a pending write;
- how an interrupted write is recovered;
- how file versions or provider conflicts are surfaced;
- whether the user can keep local changes, accept remote changes, duplicate,
  export, or retry;
- when an AI candidate becomes an ordinary edit;
- what “saved” actually means for local, provider, and remote persistence.

Autosave is not proof of sync, backup, or successful provider upload. Use a
specific status such as "Saved on this device", "Uploading", or "Conflict
needs review" when those distinctions matter.

## 9. Keep editor ownership simple

The editor should own presentation of document state, not every storage concern.

A useful boundary is:

~~~text
DocumentGroup configuration
    -> document adapter
        -> format/coordination layer
            -> editor model
                -> SwiftUI fields, selection, commands, accessibility
                    -> optional AI review adapter
                        -> explicit document mutation
~~~

The editor can bind to document content, but a large editor should not make each
keystroke independently open a security scope, parse a whole file, or invoke a
model. Debounce and checkpoint through one owned coordinator. Keep selection,
focus, dirty state, and review selection scene-local; keep format versions,
durable revisions, and conflict resolution in the document layer.

## 10. Add a bounded on-device AI review route

Foundation Models can be an optional review capability, not an invisible
rewrite engine.

Define an adapter:

~~~swift
struct DocumentReviewRequest: Sendable {
    let documentID: UUID
    let sourceRevision: Int
    let selectedText: String
    let instruction: String
}

enum DocumentReviewState: Equatable, Sendable {
    case unavailable(reason: String)
    case ready
    case reviewing
    case partial(String)
    case candidate(sourceRevision: Int, text: String)
    case stale(candidateRevision: Int, currentRevision: Int)
    case committed(revision: Int)
    case failed(String)
}
~~~

The route should:

1. check model availability and user-visible policy;
2. send only the selected or intentionally scoped content;
3. bind the session/task to the current document revision;
4. allow cancellation when selection, document, scene, or task changes;
5. show partial output as provisional;
6. require explicit review before mutating the document;
7. reject or rebase a candidate when the source revision changed;
8. commit through the same document mutation/save path as a human edit;
9. record that the edit was AI-assisted when the product needs auditability;
10. never imply that on-device inference makes the document automatically safe,
    correct, or synchronized.

The unavailable state should be a supported product state. Keep the editor fully
useful without the model.

## 11. Apply Liquid Glass to the document shell

Use system document/window chrome where available. Apply custom Liquid Glass to a
small semantic group: a floating formatting cluster, inspector, review tray,
or status control. The file browser, editor canvas, and document content remain
the primary surfaces.

A practical hierarchy:

~~~text
system navigation/title/document controls
    -> editor content and selection
        -> compact glass formatting/review group
            -> status and explicit commit action
~~~

Keep glass:

- attached to a meaningful task or control group;
- separate from text-selection and dense editing content;
- readable in light/dark, increased contrast, reduced transparency, and
  accessibility sizes;
- visually subordinate to the document;
- free of fake window chrome that claims system behavior;
- tested at narrow and wide iPadOS/Catalyst sizes.

A glass review tray should make “Review”, “Apply”, “Discard”, “Unavailable”, and
“Stale” distinct actions and statuses. Material is not a persistence state.

## 12. Adapt the document route by target

| Target | Route emphasis | Proof |
| --- | --- | --- |
| iPhone | compact browser/editor transition, import/share, readable status | physical device plus UI fixture |
| iPadOS | split editor/browser, multiwindow, keyboard/Pencil, Stage Manager resize | signed iPad run at narrow/wide sizes |
| Mac Catalyst | menu/toolbar/keyboard/pointer, multiple windows, file destinations | actual Catalyst compile/run |
| visionOS | system window or spatial route only when task benefits | visionOS target run and spatial interaction evidence |
| watchOS | projection or handoff, not full document editing | watch target behavior |
| File Provider extension | placeholder, materialization, metadata, sync boundary | extension build plus provider/system run |
| Widget/App Intent/Shortcuts | small typed entry request into the document route | system-surface delivery |

Share domain meaning across targets, not an assumption that every target has the
same document browser, file APIs, window model, or input.

## 13. Stop conditions

Stop and repair the route if any of these are true:

- DocumentGroup is used but the feature has no document identity or format;
- an external URL is retained after its security scope ends;
- export mutates the source without telling the user;
- a provider-backed file is treated as always-local;
- autosave status says "saved" before the intended persistence boundary;
- a conflict silently overwrites local or remote work;
- AI output mutates the document without review and revision validation;
- Liquid Glass is used as a full-page background or as fake window chrome;
- a target claim is based only on a preview or simulator;
- accessibility or keyboard input is only checked after the visual work;
- the source document and the AI candidate do not share a traceable revision.

## Sources

- [Documents](https://developer.apple.com/documentation/swiftui/documents)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [ReferenceFileDocument](https://developer.apple.com/documentation/swiftui/referencefiledocument)
- [Creating a document-based app](https://developer.apple.com/documentation/swiftui/creating-a-document-based-app)
- [Handling advanced document scenarios](https://developer.apple.com/documentation/swiftui/handling-advanced-document-scenarios)
- [SwiftUI view presentation](https://developer.apple.com/documentation/swiftui/view-presentation)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [URL security-scoped resource access](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [NSFilePresenter](https://developer.apple.com/documentation/foundation/nsfilepresenter)
- [NSFileVersion](https://developer.apple.com/documentation/foundation/nsfileversion)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [Replicated File Provider extension](https://developer.apple.com/documentation/fileprovider/replicated-file-provider-extension)
- [Synchronizing the File Provider extension](https://developer.apple.com/documentation/FileProvider/synchronizing-the-file-provider-extension)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [File management HIG](https://developer.apple.com/design/human-interface-guidelines/file-management)
- [Collaboration and sharing HIG](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Windows HIG](https://developer.apple.com/design/human-interface-guidelines/windows)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
