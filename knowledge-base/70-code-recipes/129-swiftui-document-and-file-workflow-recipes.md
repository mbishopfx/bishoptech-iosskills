# SwiftUI document and file-workflow recipes

## Recipe rules

These snippets are route starters for a named app target. They are not compiled
in this knowledge base and do not prove document-browser behavior, file-provider
delivery, security-scoped access, physical input, on-device model readiness, or
release packaging.

Before copying a recipe:

1. Confirm the current SDK signature and availability in Xcode.
2. Name the target, deployment target, document UTType, and persistence boundary.
3. Keep document route values lightweight and resolve current truth inside.
4. Test new, open, edit, autosave, export, move, share, conflict, cancellation,
   termination, stale, and unauthorized states.
5. Test Dynamic Type, localization/RTL, VoiceOver, keyboard, pointer, reduced
   effects, and the target's primary input.
6. Record physical, system-surface, provider, performance, archive, and release
   evidence separately.

Tilde fences are used so the examples remain copyable inside this Markdown page.

## 1. Declare a document type

Keep the document type, format version, and error surface together.

~~~swift
import SwiftUI
import UniformTypeIdentifiers

extension UTType {
    static let bishopNote = UTType(
        exportedAs: "dev.bishoptech.note",
        conformingTo: .data
    )
}

enum NoteDocumentError: LocalizedError {
    case missingContents
    case unsupportedVersion(Int)
    case invalidContents

    var errorDescription: String? {
        switch self {
        case .missingContents:
            return "The document has no readable contents."
        case .unsupportedVersion(let version):
            return "This document format version is not supported: \(version)."
        case .invalidContents:
            return "The document contents are invalid."
        }
    }
}
~~~

For a production app, place exported/imported type declarations in the target
that owns the file format and verify the generated Info.plist/UTExportedType
configuration where the app declares it.

## 2. Create a versioned FileDocument

Use a canonical envelope so migrations and corrupt-input tests have a stable
boundary.

~~~swift
struct NoteEnvelope: Codable, Sendable {
    let formatVersion: Int
    let title: String
    let body: String
}

struct NoteDocument: FileDocument, Equatable, Sendable {
    static var readableContentTypes: [UTType] { [.bishopNote] }
    static var writableContentTypes: [UTType] { [.bishopNote] }

    var title = ""
    var body = ""
    var formatVersion = 1

    init() {}

    init(configuration: ReadConfiguration) throws {
        guard let data = configuration.file.regularFileContents else {
            throw NoteDocumentError.missingContents
        }

        let envelope = try JSONDecoder().decode(NoteEnvelope.self, from: data)
        guard envelope.formatVersion == 1 else {
            throw NoteDocumentError.unsupportedVersion(envelope.formatVersion)
        }

        title = envelope.title
        body = envelope.body
        formatVersion = envelope.formatVersion
    }

    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        let envelope = NoteEnvelope(
            formatVersion: formatVersion,
            title: title,
            body: body
        )
        let data = try JSONEncoder().encode(envelope)
        return FileWrapper(regularFileWithContents: data)
    }
}
~~~

Add explicit migration code when a later release must read an older version.
Test invalid encoding, missing fields, unknown versions, oversized input, and
round-trip equality.

## 3. Use DocumentGroup as the scene route

Keep system document management at the scene boundary and pass the binding and
URL context into the editor.

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

struct NoteEditor: View {
    @Binding var document: NoteDocument
    let fileURL: URL?

    var body: some View {
        Form {
            TextField("Title", text: $document.title)
            TextEditor(text: $document.body)
                .frame(minHeight: 240)
        }
        .navigationTitle(fileURL?.deletingPathExtension().lastPathComponent ?? "Untitled")
    }
}
~~~

The URL is useful for context and diagnostics. Keep format, authorization,
domain identity, conflict, and AI revision policy in an owned document adapter.
Do not use a path string as the only identity.

## 4. Keep a reference-backed document explicit

Use ReferenceFileDocument only when a reference object is the correct ownership
model and can announce mutations.

~~~swift
@MainActor
final class NoteReference: ObservableObject {
    @Published var title = ""
    @Published var body = ""

    private(set) var hasUnsavedChanges = false

    func updateBody(_ body: String) {
        self.body = body
        hasUnsavedChanges = true
    }
}

struct ReferenceNoteDocument: ReferenceFileDocument {
    static var readableContentTypes: [UTType] { [.bishopNote] }
    static var writableContentTypes: [UTType] { [.bishopNote] }

    @Published var reference: NoteReference

    init() {
        reference = NoteReference()
    }

    init(configuration: ReadConfiguration) throws {
        reference = try NoteReferenceDecoder.decode(configuration.file)
    }

    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        try NoteReferenceEncoder.encode(reference)
    }
}
~~~

The exact ObservableObject/change-signaling requirements are SDK-sensitive. In a
real target, verify the protocol's associated types and use the document
reference's change/undo/coordinator mechanisms rather than relying only on a
local Boolean.

## 5. Build a lightweight document route value

A route request should carry identity and freshness, not an entire document.

~~~swift
struct DocumentWindowValue: Hashable, Codable, Sendable {
    let documentID: UUID
    let sourceRevision: Int
}

enum DocumentRouteState: Equatable, Sendable {
    case unavailable(String)
    case loading
    case ready(documentID: UUID, revision: Int)
    case stale(requested: Int, current: Int)
}
~~~

Resolve the ID against current authorized truth when the scene opens. Test
deleted, moved, unauthorized, account-switched, and stale values.

## 6. Import with fileImporter and scoped access

Keep access inside the operation that reads or copies the selected URL.

~~~swift
struct ImportingView: View {
    @State private var showingImporter = false
    @State private var importError: String?

    var body: some View {
        Button("Import note") {
            showingImporter = true
        }
        .fileImporter(
            isPresented: $showingImporter,
            allowedContentTypes: [.bishopNote],
            allowsMultipleSelection: false
        ) { result in
            switch result {
            case .success(let urls):
                guard let url = urls.first else { return }
                Task {
                    await importURL(url)
                }
            case .failure(let error):
                importError = error.localizedDescription
            }
        }
    }

    @MainActor
    private func importURL(_ url: URL) async {
        let didStart = url.startAccessingSecurityScopedResource()
        defer {
            if didStart {
                url.stopAccessingSecurityScopedResource()
            }
        }

        do {
            let data = try Data(contentsOf: url, options: [.mappedIfSafe])
            try await DocumentImporter().copyIntoAppDomain(
                data: data,
                sourceURL: url
            )
        } catch {
            importError = error.localizedDescription
        }
    }
}
~~~

For a provider or external file that must remain linked, replace the copy
policy with a documented security-scoped bookmark and revalidation flow. Do not
retain the URL after access ends and assume it remains readable.

## 7. Export a document representation

Export is a destination choice and should not silently change the source
document.

~~~swift
struct ExportingView: View {
    let document: NoteDocument
    @State private var showingExporter = false
    @State private var exportError: String?

    var body: some View {
        Button("Export copy") {
            showingExporter = true
        }
        .fileExporter(
            isPresented: $showingExporter,
            document: document,
            contentTypes: [.bishopNote],
            defaultFilename: "Note"
        ) { result in
            switch result {
            case .success(let destination):
                recordExport(destination)
            case .failure(let error):
                exportError = error.localizedDescription
            }
        }
    }
}
~~~

The exact generic signature and cancellation overloads vary with SDK revision;
check the current SwiftUI file-presentation documentation. Verify filename,
UTType, overwrite behavior, cancellation, and destination reopen.

## 8. Move a file explicitly

Use fileMover only when the user means to relocate the source.

~~~swift
struct MovingView: View {
    let sourceURL: URL
    @State private var showingMover = false
    @State private var moveError: String?

    var body: some View {
        Button("Move document") {
            showingMover = true
        }
        .fileMover(isPresented: $showingMover, file: sourceURL) { result in
            switch result {
            case .success(let destination):
                updateDocumentLocation(destination)
            case .failure(let error):
                moveError = error.localizedDescription
            }
        }
    }
}
~~~

After a move, update identity and any bookmark/provider metadata through the
document boundary. Treat cancellation, cross-provider behavior, permission
failure, and a missing source as normal test cases.

## 9. Provide a file-backed Transferable

Use a file representation when the data is large or when a receiver expects a
file rather than an in-memory value.

~~~swift
struct NoteTransfer: Transferable {
    let fileURL: URL

    static var transferRepresentation: some TransferRepresentation {
        FileRepresentation(
            contentType: .bishopNote
        ) { item in
            SentTransferredFile(item.fileURL)
        } importing: { received in
            let ownedURL = try await TemporaryFileStore.copyToOwnedLocation(
                received.file
            )
            return NoteTransfer(fileURL: ownedURL)
        }
    }
}
~~~

The concrete Transferable/FileRepresentation signatures are SDK-sensitive.
Verify the current Core Transferable documentation, especially whether the
exporting value must create a temporary copy and who owns cleanup. Never expose
a secret or an unstable app-private path as a share contract.

## 10. Keep a security-scoped bookmark boundary

Persist a bookmark only if later access is part of the product.

~~~swift
struct ExternalFileReference: Codable, Sendable {
    let bookmarkData: Data
}

func makeReference(for url: URL) throws -> ExternalFileReference {
    let data = try url.bookmarkData(
        options: [.withSecurityScope],
        includingResourceValuesForKeys: nil,
        relativeTo: nil
    )
    return ExternalFileReference(bookmarkData: data)
}

func resolve(_ reference: ExternalFileReference) throws -> URL {
    var isStale = false
    let url = try URL(
        resolvingBookmarkData: reference.bookmarkData,
        options: [.withSecurityScope],
        relativeTo: nil,
        bookmarkDataIsStale: &isStale
    )

    if isStale {
        // Resolve, revalidate, and replace the stored bookmark through policy.
    }
    return url
}
~~~

Resolve the bookmark, validate the file type and account policy, start the
security scope for the operation, and stop it afterward. Test revoked access,
stale data, sign-out, moved files, and app relaunch.

## 11. Represent save and conflict state

Make persistence state a first-class value in the editor.

~~~swift
enum DocumentSaveState: Equatable, Sendable {
    case clean(revision: Int)
    case dirty(revision: Int)
    case saving(revision: Int)
    case saved(revision: Int)
    case conflict(local: Int, remote: Int)
    case failed(revision: Int, message: String)
}

struct DocumentStatusLabel: View {
    let state: DocumentSaveState

    var body: some View {
        switch state {
        case .clean:
            Label("Up to date", systemImage: "checkmark.circle")
        case .dirty:
            Label("Unsaved changes", systemImage: "pencil")
        case .saving:
            Label("Saving", systemImage: "arrow.triangle.2.circlepath")
        case .saved:
            Label("Saved", systemImage: "checkmark.circle.fill")
        case .conflict:
            Label("Conflict needs review", systemImage: "exclamationmark.triangle")
        case .failed:
            Label("Save failed", systemImage: "xmark.octagon")
        }
    }
}
~~~

Use wording that names the real boundary: local save, provider upload, remote
sync, or conflict resolution. Test newer edits winning over older async writes.

## 12. Add an on-device AI review fixture

Keep model availability, source revision, candidate review, and commit separate.

~~~swift
enum ReviewState: Equatable, Sendable {
    case unavailable(String)
    case ready
    case reviewing
    case partial(String)
    case candidate(sourceRevision: Int, replacement: String)
    case stale(candidateRevision: Int, currentRevision: Int)
    case committed(revision: Int)
    case failed(String)
}

struct DocumentReviewFixtureView: View {
    let state: ReviewState
    let apply: () -> Void
    let discard: () -> Void

    var body: some View {
        VStack(alignment: .leading) {
            switch state {
            case .unavailable(let reason):
                Label("Review unavailable: \(reason)", systemImage: "sparkles")
            case .ready:
                Button("Review selection") { /* start bounded task */ }
            case .reviewing:
                ProgressView("Reviewing selection")
            case .partial(let text):
                Text(text)
                Button("Cancel review") { discard() }
            case .candidate(let revision, let replacement):
                Text("Proposed from revision \(revision)")
                Text(replacement)
                HStack {
                    Button("Apply", action: apply)
                    Button("Discard", action: discard)
                }
            case .stale:
                Label("Review is out of date", systemImage: "clock.arrow.circlepath")
            case .committed:
                Label("Review applied", systemImage: "checkmark")
            case .failed(let message):
                Label(message, systemImage: "exclamationmark.triangle")
            }
        }
        .accessibilityElement(children: .contain)
    }
}
~~~

The real adapter should check capability, bound the selected source, cancel on
document/selection replacement, and commit through the same mutation/save route
as a human edit. The fixture is also useful for VoiceOver, Dynamic Type, and
reduced-effects testing without requiring a model-capable device.

## 13. Apply a bounded Liquid Glass group

Keep the material around a semantic review or formatting cluster.

~~~swift
struct ReviewToolbar: View {
    let state: ReviewState
    let review: () -> Void
    let apply: () -> Void
    let discard: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Label("Document review", systemImage: "sparkles")

            switch state {
            case .ready:
                Button("Review", action: review)
            case .candidate:
                Button("Apply", action: apply)
                Button("Discard", action: discard)
            case .unavailable, .reviewing, .partial, .stale, .committed, .failed:
                EmptyView()
            }

            DocumentStatusLabel(state: .clean(revision: 0))
        }
        .padding(10)
        .glassEffect()
    }
}
~~~

Verify the exact Liquid Glass API for the target SDK and availability. Keep the
document canvas, selection, and save/conflict meaning visible outside the glass
group. Test light/dark, contrast, transparency, Dynamic Type, and narrow
iPadOS/Catalyst layouts.

## 14. Add target-specific document commands

Share document meaning while adapting input and shell.

~~~swift
struct DocumentCommands: Commands {
    var body: some Commands {
        CommandGroup(after: .saveItem) {
            Button("Export Copy…") {
                // Send a typed action to the document coordinator.
            }
            .keyboardShortcut("e", modifiers: [.command, .shift])

            Button("Review Selection") {
                // Start only when a valid selection and model capability exist.
            }
            .keyboardShortcut("r", modifiers: [.command, .option])
        }
    }
}
~~~

On iPadOS, expose the same actions through visible controls and keyboard
commands. On Mac Catalyst, verify menu placement, focus, pointer, and
selection. On iPhone, provide a compact route. On visionOS and watchOS, keep
only the task that was actually designed and tested for that surface.

## 15. Build an acceptance fixture

Keep one checklist object that can drive previews and proof logs.

~~~swift
struct DocumentAcceptanceFixture: Hashable, Sendable {
    let target: String
    let documentKind: String
    let contentType: String
    let formatVersion: Int
    let providerState: String
    let saveState: String
    let sourceRevision: Int
    let reviewState: String
    let dynamicType: String
    let inputMode: String
}

let fixture = DocumentAcceptanceFixture(
    target: "iPadOS",
    documentKind: "Note",
    contentType: "dev.bishoptech.note",
    formatVersion: 1,
    providerState: "local",
    saveState: "dirty",
    sourceRevision: 12,
    reviewState: "candidate",
    dynamicType: "accessibility3",
    inputMode: "keyboard"
)
~~~

For each fixture, record:

- what the user sees;
- what action is allowed;
- what action is intentionally blocked;
- what data is persisted;
- which revision is authoritative;
- what accessibility output says;
- which target/device/system surface produced evidence.

## Sources

- [Documents](https://developer.apple.com/documentation/swiftui/documents)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [ReferenceFileDocument](https://developer.apple.com/documentation/swiftui/referencefiledocument)
- [Creating a document-based app](https://developer.apple.com/documentation/swiftui/creating-a-document-based-app)
- [SwiftUI view presentation](https://developer.apple.com/documentation/swiftui/view-presentation)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [URL security-scoped resource access](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [NSFileVersion](https://developer.apple.com/documentation/foundation/nsfileversion)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [Replicated File Provider extension](https://developer.apple.com/documentation/fileprovider/replicated-file-provider-extension)
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
