# SwiftUI document apps and file workflows

## Purpose

Use this page when a SwiftUI feature opens, edits, imports, exports, moves,
shares, or synchronizes user-owned documents. The goal is to compose the
document scene, file representation, provider access, editor state, and
optional on-device AI without confusing any one layer for another.

The central contract is:

~~~text
document scene
    -> validated content type and document identity
    -> FileDocument or ReferenceFileDocument lifecycle
    -> coordinated read/write and version policy
    -> SwiftUI editor state
    -> optional AI proposal
    -> explicit document/domain commit
    -> export/share/provider/release proof
~~~

A file URL is not document truth. A document snapshot is not a provider
account. A generated summary is not an edit. A preview is not a file-system
or autosave proof.

## 1. Separate the content layers

| Layer | Owns | Examples | Must not own |
| --- | --- | --- | --- |
| User file | Bytes, filename, content type, provider location, file version | JSON package, plain text, PDF, custom UTType | App authorization or AI approval |
| Document model | Decoded editable representation and format version | FileDocument value, ReferenceFileDocument reference type | UI focus, account session, unbounded cache |
| Document scene | Open/create/save/window lifecycle | DocumentGroup, configuration, per-document scene state | Server sync truth or arbitrary URL parsing |
| Domain record | App-owned meaning and validated state | Project, note, review, account-scoped record | Raw provider URL as a permanent ID |
| Transfer projection | Typed import/export/share representation | Transferable, FileRepresentation, ShareLink | Broad private metadata by default |
| Provider boundary | External/local file access and synchronization | Files app, iCloud Drive, File Provider extension | Assumption that remote bytes are already local |
| AI proposal | Generated candidate with source/revision provenance | summary, tags, extracted fields, suggested edit | Automatic document mutation or user authorization |

Write the layer ownership into the app plan before implementing a document
editor.

## 2. Choose the document route

| Need | Start with | Important boundary |
| --- | --- | --- |
| Open/create/save a document app | DocumentGroup | SwiftUI manages document scene behavior; document model owns serialization |
| Value-type snapshot | FileDocument | SwiftUI tracks edits through the document binding; format version and migration remain yours |
| Observable reference document | ReferenceFileDocument | Register edits through the documented undo/change route; define save and conflict behavior |
| Existing file import | fileImporter or document picker | User grants a URL/representation; validate type, scope, and lifecycle |
| Export a value or Transferable | fileExporter or ShareLink | Export a snapshot/projection; destination acceptance and cancellation remain separate |
| Move a file | fileMover | Update stored identity only after successful move; provider errors are ordinary states |
| Remote files visible to other apps | File Provider extension | Extension target, domain, enumerators, placeholders/materialization, versions, progress, and sync |
| Large transfer | FileRepresentation | Pass a file efficiently; the recipient still owns import validation and retention |
| Durable app records in a file | SwiftData-backed DocumentGroup or explicit file format | Migration, schema, document URL, and store lifecycle must be tested in the selected SDK |

Choose the narrowest route. Do not create a File Provider extension merely to
share a local export.

## 3. DocumentGroup is a scene

DocumentGroup adds document-opening, creation, saving, and platform document
behavior. On platforms that support it, this can include a document browser
and multiple document windows.

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

The exact initializer and document configuration differ by SDK. Confirm the
current signature and availability in Xcode. If multiple groups match a file
type, declaration order and content-type specificity matter; declare the
narrower type before a broader type.

The document editor receives a configuration that can include a binding to the
document and the current file URL. A newly created document may not have a
file URL yet. When the URL changes, update presentation state without reading
or writing the file behind SwiftUI's document lifecycle.

Do not use the configuration URL as a shortcut for raw byte access. Use the
document protocol's read/write methods or a documented file coordinator for
work outside the managed lifecycle.

## 4. FileDocument versus ReferenceFileDocument

Use FileDocument when a value snapshot is a good model for the document. Use
ReferenceFileDocument when a reference object needs observable mutations and
explicit change tracking.

| Decision | FileDocument | ReferenceFileDocument |
| --- | --- | --- |
| Model shape | Value type | Reference type |
| Edit tracking | Binding changes | Registered reference-document changes and undo policy |
| Serialization | Read configuration and file wrapper | Read/write callbacks on the reference document |
| Good fit | Small/medium structured snapshots | Observable editors with coordinated mutable state |
| Risks | Large copies, accidental UI coupling | Mutation isolation, unsaved state, thread/actor ownership |
| Must verify | Format, migration, corruption, write failure | Change registration, undo, autosave, conflict, teardown |

Serialization should be deterministic and independent of a view model. Include
a format version, reject unsupported versions clearly, and define recovery for
partial or corrupt input.

~~~swift
struct NoteDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.json] }
    static var writableContentTypes: [UTType] { [.json] }

    var formatVersion = 1
    var notes: [String] = []

    init(configuration: ReadConfiguration) throws {
        guard let data = configuration.file.regularFileContents else {
            throw CocoaError(.fileReadCorruptFile)
        }
        let envelope = try JSONDecoder().decode(
            Envelope.self,
            from: data
        )
        guard envelope.formatVersion <= 1 else {
            throw CocoaError(.fileReadUnsupportedScheme)
        }
        formatVersion = envelope.formatVersion
        notes = envelope.notes
    }

    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        let envelope = Envelope(formatVersion: 1, notes: notes)
        let data = try JSONEncoder().encode(envelope)
        return FileWrapper(regularFileWithContents: data)
    }

    private struct Envelope: Codable {
        let formatVersion: Int
        let notes: [String]
    }
}
~~~

The snippet is a route sketch. Compile it against the selected SDK and add
schema migration, bounded size, encoding, actor/sendability, and write-error
tests before using it in an app.

## 5. Content type is part of the product contract

Use Uniform Type Identifiers to describe the actual content. A file extension
alone is not a format contract.

For a custom format, define:

- exported/imported type identifier;
- conformance to the closest standard type;
- readable versus writable behavior;
- filename extension and display name;
- document icon or thumbnail route;
- migration and unsupported-version policy;
- share/import/export representations;
- Quick Look or File Provider behavior if claimed.

Do not advertise a generic file URL when the content is actually a PDF, image,
text, or custom document. A precise type improves system routing and
destination compatibility.

## 6. Import with a user-mediated file URL

Use fileImporter for a copy/import task when the app does not own the document
scene.

~~~swift
struct ImportButton: View {
    @State private var isImporting = false
    @State private var result: ImportResult = .idle

    var body: some View {
        Button("Import note") {
            isImporting = true
        }
        .fileImporter(
            isPresented: $isImporting,
            allowedContentTypes: [.json],
            allowsMultipleSelection: false
        ) { response in
            result = ImportResult.from(response)
        }
    }
}
~~~

The exact overload and cancellation handler depend on the SDK. On completion:

1. validate the content type and file size;
2. start security-scoped access when the URL requires it;
3. balance every successful access with stopAccessing;
4. coordinate reads for external/provider-backed documents;
5. copy into app-owned storage if the product needs an independent copy;
6. store a secure bookmark only if later access is truly required;
7. surface provider offline, cancellation, and reselect states;
8. do not persist a plain path string as durable authorization.

A URL returned by a picker is a permission boundary with a lifetime, not a
guarantee of local availability.

## 7. Export and move are distinct

fileExporter creates a user-mediated export destination. fileMover changes
the location of an existing file. ShareLink/Transferable projects content to
a system transfer destination.

| Operation | Source truth | Destination result |
| --- | --- | --- |
| Export | Current validated snapshot | New URL/copy; source remains |
| Move | Existing file identity | New URL after successful move |
| Share | Redacted transfer projection | Recipient-specific accepted representation |
| Save in place | Document scene/file lifecycle | Current file version or an error/conflict state |

Never update the canonical file URL before a move succeeds. On export, do not
silently replace the source document unless that is an explicit product
action. On sharing, include only the representation and metadata the user
intended.

## 8. Provider and security-scoped access

File Provider content can be local, placeholder-backed, materialized, remote,
offline, or in conflict. A directory URL does not prove that every descendant
is local or permanently accessible.

For an external document route:

- keep access scope around the actual read/write operation;
- use NSFileCoordinator for coordinated external access;
- use a UIDocument or file-presenter lifecycle for ongoing external editing;
- handle file move, deletion, eviction, version change, and provider errors;
- resolve stale bookmarks by asking the user to reselect;
- do not retain a security scope for the whole process without a reason;
- cancel provider/network work when the document scene disappears;
- clean up temporary copies and sensitive logs.

A File Provider extension is a separate target and process boundary. It needs
item identifiers, enumeration, placeholders or replicated content, progress,
cancellation, change signaling, version/conflict policy, account handling, and
real Files/Finder evidence.

## 9. Autosave, versioning, and conflict

Saving a document is not one successful fileWrapper call. Define:

~~~text
edit
    -> dirty/change registration
    -> bounded autosave request
    -> coordinated write
    -> provider/file version result
    -> clear dirty state or present error/conflict
~~~

Test:

- autosave during typing and when leaving the document;
- cancellation and repeated save requests;
- process termination during a write;
- provider offline or placeholder state;
- external edit by Files, another app, or another window;
- incompatible format version;
- unresolved NSFileVersion conflicts;
- migration failure and recovery copy;
- account change and security-scope loss.

Keep file-format migration deterministic. If a conflict cannot be merged
safely, preserve both versions or ask the user; do not silently overwrite.

## 10. SwiftUI editor state

The editor should separate document binding, scene-local editing UI, and
domain validation.

| State | Owner |
| --- | --- |
| Document bytes/model | FileDocument or ReferenceFileDocument |
| Cursor/focus/selected tab | SwiftUI scene/view state |
| Unsaved draft annotation | Feature-owned document/editor model |
| Undo registration | Document environment and documented undo boundary |
| Account/permission | Feature/domain service |
| File URL presentation | Document configuration/read-only display state |
| AI suggestion | AI adapter/candidate store |
| Commit | Domain use case with revision check |
| Export/share | Transfer projection and user-mediated system route |

Do not make a generated suggestion mutate the document binding before review.
Keep candidate source revision and document revision visible to the validator.

## 11. Liquid Glass document editors

Document apps already benefit from system navigation, toolbars, menus,
document browsers, and window behavior. Use those system surfaces first.

A bounded Liquid Glass group can clarify a review state or focused tool palette,
but it should not replace:

- the document title and current file status;
- open/save/export/move controls;
- undo/redo and conflict state;
- keyboard commands and pointer affordances;
- accessibility labels and focus;
- platform window/document chrome.

For iPadOS and Catalyst, preserve document workspace hierarchy and resize
behavior. For visionOS, use the documented window and spatial document
composition. File management guidance differs from watchOS, where document
browsing and editing are not the normal product model.

## 12. On-device AI document review

Keep AI work downstream of a validated document snapshot:

~~~text
document revision N
    -> bounded extracted source
    -> model availability/session
    -> typed candidate with source revision N
    -> human review/validation
    -> document/domain commit at revision N or conflict
~~~

Possible candidates include a summary, tags, outline, redaction proposal,
structured fields, or a suggested edit. The adapter must define:

- model availability and language;
- input size/context budget;
- privacy and retention policy;
- cancellation when the scene/file changes;
- candidate identity and source revision;
- validation and refusal behavior;
- explicit commit and conflict handling;
- deterministic fallback when the model is unavailable.

A preview or generated text does not prove model readiness, factual accuracy,
document privacy, or a successful write.

## 13. Accessibility and input

Document tasks are often long-lived and input-rich:

- provide clear document title, file status, dirty/saved/conflict state;
- expose open, save, export, move, share, undo, redo, and close semantics;
- test VoiceOver reading order in the browser and editor;
- support Dynamic Type, localization, RTL, keyboard, pointer, and Pencil where
  the target claims them;
- keep drag/drop and Transferable actions semantic;
- make AI review state and commit action understandable;
- do not use a custom glass overlay as the only place to find file status;
- provide recoverable unavailable/reselect/error states.

On iPadOS and Catalyst, test command discoverability and keyboard navigation.
On visionOS, test spatial focus and comfort. On watchOS, expose a short
projection or companion action rather than a document browser.

## 14. Proof contract

Record, for every document feature:

- target, SDK, deployment, bundle/extension target, and content-type declarations;
- document scene declaration and window/document identity;
- format version, migration fixtures, supported read/write types;
- open/create/save/autosave/export/move/cancel results;
- security-scoped access interval and bookmark/stale policy;
- provider state, file coordination, conflict/version result;
- AI capability, input snapshot revision, candidate, validation, and commit;
- light/dark, Dynamic Type, locale/RTL, input, accessibility, and reduced
  effects state;
- signed device, iPad/Catalyst, Files/Provider, system share, archive, and
  release artifacts.

A successful import is not proof of autosave. A File Provider unit test is not
proof of Files app behavior. A model candidate is not proof of a document edit.

## Common failure modes

- Passing a file URL string through the app as if it were durable authorization.
- Reading/writing the DocumentGroup URL behind SwiftUI's document lifecycle.
- Using a broad UTType that admits formats the parser cannot read.
- Treating FileDocument serialization as migration/conflict handling.
- Updating a moved-file URL before the system move succeeds.
- Retaining a security-scoped URL scope forever.
- Treating a placeholder as local bytes.
- Building a File Provider extension for a simple share/export workflow.
- Mutating a document from AI output without revision validation and review.
- Applying a glass layer over document status, file controls, or conflict state.
- Claiming watchOS is a document-browser target because the iPhone app is.
- Calling a preview or simulator file picker an autosave or provider proof.

## Sources

- [Documents](https://developer.apple.com/documentation/swiftui/documents)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [ReferenceFileDocument](https://developer.apple.com/documentation/swiftui/referencefiledocument)
- [Creating a document-based app](https://developer.apple.com/documentation/swiftui/creating-a-document-based-app)
- [Handling advanced document scenarios](https://developer.apple.com/documentation/swiftui/handling-advanced-document-scenarios)
- [SwiftUI presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [startAccessingSecurityScopedResource](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [NSFilePresenter](https://developer.apple.com/documentation/foundation/nsfilepresenter)
- [NSFileVersion](https://developer.apple.com/documentation/foundation/nsfileversion)
- [UIDocument](https://developer.apple.com/documentation/uikit/uidocument)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [Replicated File Provider extension](https://developer.apple.com/documentation/fileprovider/replicated-file-provider-extension)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [Windows HIG](https://developer.apple.com/design/human-interface-guidelines/windows)
- [File management HIG](https://developer.apple.com/design/human-interface-guidelines/file-management)
- [Collaboration and sharing HIG](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
