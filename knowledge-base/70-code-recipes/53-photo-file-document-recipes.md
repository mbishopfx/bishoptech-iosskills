# Photos, Files, document, PDF, and provider recipes

These are compile-oriented route sketches. Compile them in a named target with the selected deployment target, capabilities, extension membership, privacy strings, and real system surfaces. They do not claim that a picker, provider, document, PDF, or AI workflow works until the matching evidence is collected.

## 1. PhotosPicker selection and representation load

~~~swift
import PhotosUI
import SwiftUI

struct PhotoInputView: View {
    @State private var selection: PhotosPickerItem?
    @State private var state = "Choose a photo"

    var body: some View {
        VStack {
            PhotosPicker(selection: $selection, matching: .images) {
                Label("Choose photo", systemImage: "photo")
            }
            Text(state)
        }
        .task(id: selection) {
            guard let selection else { return }
            state = "Preparing selected photo…"

            do {
                let data = try await selection.loadTransferable(type: Data.self)
                guard let data, data.isEmpty == false else {
                    state = "No readable representation was returned"
                    return
                }
                state = "Selected representation is ready"
                // Decode/downsample/validate before an AI or persistence step.
            } catch {
                state = "The selected photo could not be prepared"
            }
        }
    }
}
~~~

Treat the item and loaded Data as separate state. If a full-resolution representation is not necessary, request a smaller or more specific Transferable type in the target app. Test iCloud retrieval failure and task cancellation.

## 2. Multiple selection with bounded work

~~~swift
import PhotosUI
import SwiftUI

struct BatchPhotoInputView: View {
    @State private var selections: [PhotosPickerItem] = []
    @State private var status = "No photos selected"

    var body: some View {
        PhotosPicker(
            selection: $selections,
            maxSelectionCount: 12,
            matching: .images
        ) {
            Label("Choose up to 12 photos", systemImage: "photo.on.rectangle")
        }
        .onChange(of: selections) {
            status = selections.isEmpty
                ? "No photos selected"
                : "\(selections.count) selected; review before processing"
        }
    }
}
~~~

Do not launch unbounded concurrent loads from an onChange callback. Use a task group or an actor-owned queue with cancellation, a memory budget, and a per-item error state. Preserve the original selection order only if the product needs it.

## 3. PhotoKit authorization boundary

~~~swift
import Photos

enum PhotoAccessState: Sendable {
    case notDetermined
    case restricted
    case denied
    case limited
    case authorized
}

@MainActor
func requestReadWritePhotoAccess() {
    let current = PHPhotoLibrary.authorizationStatus(for: .readWrite)
    guard current == .notDetermined else {
        return
    }

    PHPhotoLibrary.requestAuthorization(for: .readWrite) { status in
        let state: PhotoAccessState
        switch status {
        case .notDetermined:
            state = .notDetermined
        case .restricted:
            state = .restricted
        case .denied:
            state = .denied
        case .limited:
            state = .limited
        case .authorized:
            state = .authorized
        @unknown default:
            state = .denied
        }
        // Send only the state to the UI model; do not perform a full fetch
        // from inside the permission callback.
        _ = state
    }
}
~~~

If the feature only adds media, request add-only access. For one-off selected input, prefer PhotosPicker so broad PhotoKit access is not needed.

## 4. PhotoKit change request with confirmation

~~~swift
import Photos

func addImageToLibrary(
    _ image: UIImage,
    completion: @escaping (Result<Void, Error>) -> Void
) {
    PHPhotoLibrary.shared().performChanges {
        PHAssetChangeRequest.creationRequestForAsset(from: image)
    } completionHandler: { success, error in
        if let error {
            completion(.failure(error))
        } else if success {
            completion(.success(()))
        } else {
            completion(.failure(
                NSError(
                    domain: "PhotoRoute",
                    code: 1,
                    userInfo: [NSLocalizedDescriptionKey: "Photo change did not complete."]
                )
            ))
        }
    }
}
~~~

Call this only after the person confirms the destination and any AI-generated metadata. Re-check current authorization and source availability before committing a more complex change block.

## 5. Scoped file read

~~~swift
import Foundation

func readSecurityScopedFile(at url: URL) throws -> Data {
    let hasScope = url.startAccessingSecurityScopedResource()
    defer {
        if hasScope {
            url.stopAccessingSecurityScopedResource()
        }
    }
    return try Data(contentsOf: url)
}
~~~

Balance every successful scope. For a large file, replace Data(contentsOf:) with a bounded/streaming operation and keep the scope for exactly the duration of that operation. Do not store only url.path for later access.

## 6. SwiftUI file importer

~~~swift
import SwiftUI
import UniformTypeIdentifiers

struct FileInputView: View {
    @State private var showingImporter = false
    @State private var message = "Choose a document"

    var body: some View {
        Button("Import document") {
            showingImporter = true
        }
        .fileImporter(
            isPresented: $showingImporter,
            allowedContentTypes: [.pdf, .plainText, .json],
            allowsMultipleSelection: false
        ) { result in
            switch result {
            case .success(let urls):
                guard let url = urls.first else { return }
                do {
                    _ = try readSecurityScopedFile(at: url)
                    message = "Imported a readable document"
                } catch {
                    message = "The document could not be read"
                }
            case .failure:
                message = "The document was unavailable"
            }
        } onCancellation: {
            message = "Import cancelled"
        }
    }
}
~~~

The exact modifier overload is SDK-sensitive; compile the intended target and keep cancellation distinct from failure. Copy to app-owned storage only when independent retention is part of the product.

## 7. Security-scoped bookmark route

~~~swift
import Foundation

func makeSecurityScopedBookmark(for url: URL) throws -> Data {
    try url.bookmarkData(
        options: [.withSecurityScope],
        includingResourceValuesForKeys: nil,
        relativeTo: nil
    )
}

func resolveSecurityScopedBookmark(_ data: Data) throws -> URL {
    var isStale = false
    let url = try URL(
        resolvingBookmarkData: data,
        options: [.withSecurityScope],
        relativeTo: nil,
        bookmarkDataIsStale: &isStale
    )
    if isStale {
        // Ask the user to reselect and replace the bookmark.
    }
    return url
}
~~~

Resolving a bookmark does not prove that the file exists or that a provider can materialize it. Start a scope, perform the operation, stop the scope, and handle a stale or deleted result.

## 8. FileDocument with explicit content type

~~~swift
import SwiftUI
import UniformTypeIdentifiers

struct NoteDocument: FileDocument {
    static var readableContentTypes: [UTType] = [.plainText, .json]
    static var writableContentTypes: [UTType] = [.plainText, .json]

    var text: String

    init(text: String = "") {
        self.text = text
    }

    init(configuration: ReadConfiguration) throws {
        guard let data = configuration.file.regularFileContents else {
            throw CocoaError(.fileReadCorruptFile)
        }
        guard let decoded = String(data: data, encoding: .utf8) else {
            throw CocoaError(.fileReadInapplicableString)
        }
        text = decoded
    }

    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        FileWrapper(regularFileWithContents: Data(text.utf8))
    }
}
~~~

Add a schema/version envelope for a real format. Keep serialization Sendable and independent of a SwiftUI view model. For a reference-type model, use ReferenceFileDocument and define the dirty/autosave contract explicitly.

## 9. DocumentGroup

~~~swift
import SwiftUI

@main
struct NotesDocumentApp: App {
    var body: some Scene {
        DocumentGroup(newDocument: {
            NoteDocument()
        }) { configuration in
            NoteEditor(document: configuration.$document)
        }
    }
}

struct NoteEditor: View {
    @Binding var document: NoteDocument

    var body: some View {
        TextEditor(text: $document.text)
            .padding()
    }
}
~~~

Use DocumentGroup only when the target truly wants a document-based app. Test open/create/multiple windows, Files/provider sources, autosave, malformed input, migration, and restoration.

## 10. Coordinated file read

~~~swift
import Foundation

func coordinatedRead(at url: URL) throws -> Data {
    var coordinationError: NSError?
    var result: Result<Data, Error> = .failure(
        CocoaError(.fileReadUnknown)
    )

    let coordinator = NSFileCoordinator()
    coordinator.coordinate(
        readingItemAt: url,
        options: [],
        error: &coordinationError
    ) { coordinatedURL in
        result = Result {
            try Data(contentsOf: coordinatedURL)
        }
    }

    if let coordinationError {
        throw coordinationError
    }
    return try result.get()
}
~~~

Use a fresh coordinator per file operation. If the document is presented for ongoing edits, use the appropriate document/file-presenter lifecycle and handle backgrounding and external changes.

## 11. Redacted Transferable projection

~~~swift
import CoreTransferable
import Foundation
import UniformTypeIdentifiers

struct ShareableSummary: Transferable, Sendable {
    let title: String
    let summary: String

    static var transferRepresentation: some TransferRepresentation {
        DataRepresentation(exportedContentType: .plainText) { value in
            Data("\(value.title)\n\n\(value.summary)".utf8)
        }
    }
}
~~~

Create this projection from an app-owned record after redaction. Do not make a model with private fields Transferable merely because it is convenient. Add FileRepresentation when destinations need a file rather than data, and test named destinations separately.

## 12. PDFView bridge

~~~swift
import PDFKit
import SwiftUI

struct PDFSurface: UIViewRepresentable {
    let url: URL

    func makeUIView(context: Context) -> PDFView {
        let view = PDFView()
        view.autoScales = true
        view.displayMode = .singlePageContinuous
        view.document = PDFDocument(url: url)
        return view
    }

    func updateUIView(_ view: PDFView, context: Context) {
        guard view.document?.documentURL != url else { return }
        view.document = PDFDocument(url: url)
    }
}
~~~

For a real document editor, add page/selection/annotation state outside PDFView, validate malformed/encrypted files, and preserve a source revision. A displayed PDF is not automatically safe to export or link-open.

## 13. Quick Look bridge shape

~~~swift
import QuickLook
import SwiftUI

final class PreviewItem: NSObject, QLPreviewItem {
    let previewItemURL: URL?

    init(url: URL) {
        previewItemURL = url
    }
}

final class PreviewDataSource: NSObject, QLPreviewControllerDataSource {
    let item: PreviewItem

    init(item: PreviewItem) {
        self.item = item
    }

    func numberOfPreviewItems(in controller: QLPreviewController) -> Int {
        1
    }

    func previewController(
        _ controller: QLPreviewController,
        previewItemAt index: Int
    ) -> QLPreviewItem {
        item
    }
}

struct QuickLookSurface: UIViewControllerRepresentable {
    let url: URL

    func makeUIViewController(
        context: Context
    ) -> QLPreviewController {
        let controller = QLPreviewController()
        controller.dataSource = PreviewDataSource(item: PreviewItem(url: url))
        return controller
    }

    func updateUIViewController(
        _ controller: QLPreviewController,
        context: Context
    ) {}
}
~~~

Keep the preview item’s file available for the preview lifetime and do not hold provider files open longer than needed. Add a custom Quick Look extension only when the product owns a file type that needs a system preview.

## 14. File Provider item state

~~~swift
struct ProviderItemRecord: Sendable, Equatable {
    let identifier: String
    let contentTypeIdentifier: String
    let version: String
    let isMaterialized: Bool
    let isUploading: Bool
    let isConflicted: Bool
}

enum ProviderCommitResult: Sendable {
    case queued
    case completed
    case conflict
    case unavailable
}
~~~

Use a stable item ID and version separate from a local URL. In a replicated provider, return Progress and call the completion handler for create/modify/delete/fetch work. Make retries and termination replayable.

## 15. AI proposal and commit boundary

~~~swift
struct DocumentProposal: Codable, Sendable, Equatable {
    let sourceID: String
    let sourceRevision: String?
    let selectedRange: String?
    let schemaVersion: Int
    let proposedTitle: String?
    let proposedFields: [String: String]
    let citations: [String]
}

enum ProposalDecision: Sendable {
    case rejected
    case edited(DocumentProposal)
    case accepted(DocumentProposal)
}
~~~

The deterministic commit layer must revalidate source revision, permission, file scope, document schema, and destination before changing anything. A model result must not directly call PhotoKit, File Provider, fileExporter, ShareLink, or a URL opener.

## 16. Fixture matrix

~~~swift
struct DocumentFixture: Sendable, Equatable {
    let id: String
    let typeIdentifier: String
    let byteCount: Int
    let schemaVersion: Int
    let sourceRevision: String?
    let expectedOutcome: String
}
~~~

Include fixtures for:

- selected local/iCloud photo;
- cancelled/failed PhotosPicker load;
- limited PhotoKit access;
- deleted or changed PHAsset;
- file-provider placeholder/offline/remote revision;
- security scope success/denial/stale bookmark;
- malformed/oversized document;
- old/current/unknown document schema;
- interrupted package write;
- PDF page/annotation/link/encryption cases;
- Quick Look unsupported type;
- redacted and non-redacted share projection;
- AI accepted/edited/rejected/invalid proposal;
- deletion and retention cleanup.

## Verification stop list

- Compile every recipe inside the target that owns the relevant capability or extension.
- Inspect Info.plist, UTType declarations, target membership, App Groups, provider configuration, and signing.
- Test on a physical device with real Photos/Files/provider accounts where claimed.
- Verify scopes/bookmarks/coordination and extension termination behavior.
- Test accessibility and privacy on the source, review, preview, and share surfaces.
- Prove every AI side effect is downstream of explicit user confirmation.

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
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [startAccessingSecurityScopedResource](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [NSFileProviderReplicatedExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderreplicatedextension)
- [Quick Look](https://developer.apple.com/documentation/quicklook)
- [QLPreviewController](https://developer.apple.com/documentation/quicklook/qlpreviewcontroller)
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
