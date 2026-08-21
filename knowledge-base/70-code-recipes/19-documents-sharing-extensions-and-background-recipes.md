# Documents, Sharing, Extensions, and Background Recipes

These recipes are implementation seams for the [system-surface and extension composition guide](../43-system-framework-deep-dives/06-system-surface-and-extension-composition.md). Treat projections, deep links, background work, and system invocation as versioned protocols rather than an always-running app process.

## Scope and compile boundary

These are compile-oriented route sketches for PhotosUI, SwiftUI document import/export, security-scoped URLs/bookmarks, FileDocument, WebKit/PDFKit, sharing, App Groups, extension handoffs, WidgetKit, ActivityKit, and BackgroundTasks including the iOS 26 continuous background route. They are not compiled in this documentation-only workspace and do not prove provider access, file coordination, extension delivery, widget refresh timing, Live Activity push delivery, background scheduling, GPU resources, battery behavior, or physical-device/release readiness.

Keep the handoff visible:

`user action -> system-owned picker/surface -> typed input -> validation -> durable checkpoint -> bounded work -> user-visible completion|retry|cancel`

## Recipe 1: import an external file with a balanced security scope

Use a system picker for user-owned files. If the product only needs an app-owned copy, read or stream the file while the scope is active and copy it into the app container. Do not save the URL path as the source of truth.

```swift
import SwiftUI
import UniformTypeIdentifiers

enum ImportState {
    case idle
    case loading
    case imported(URL)
    case cancelled
    case failed
}

func copyImportedFileToAppContainer(from externalURL: URL) throws -> URL {
    let didStart = externalURL.startAccessingSecurityScopedResource()
    defer {
        if didStart {
            externalURL.stopAccessingSecurityScopedResource()
        }
    }

    guard didStart else { throw CocoaError(.fileReadNoPermission) }

    let destination = FileManager.default.urls(
        for: .applicationSupportDirectory,
        in: .userDomainMask
    )[0].appendingPathComponent(externalURL.lastPathComponent)

    try FileManager.default.createDirectory(
        at: destination.deletingLastPathComponent(),
        withIntermediateDirectories: true
    )
    try FileManager.default.copyItem(at: externalURL, to: destination)
    return destination
}

struct ImportButton: View {
    @State private var isImporterPresented = false
    @State private var state: ImportState = .idle

    var body: some View {
        Button("Import document") {
            isImporterPresented = true
        }
        .fileImporter(
            isPresented: $isImporterPresented,
            allowedContentTypes: [.data],
            allowsMultipleSelection: false
        ) { result in
            switch result {
            case .success(let urls):
                guard let url = urls.first else { return }
                state = .loading
                do {
                    let localURL = try copyImportedFileToAppContainer(from: url)
                    state = .imported(localURL)
                } catch {
                    state = .failed
                }
            case .failure:
                state = .failed
            }
        }
    }
}
```

For a large file, replace `Data(contentsOf:)` or a whole-file copy with a bounded stream and a checkpoint. Validate the file type, size, and format before adding it to the durable model. If the user cancels, leave no phantom import record.

## Recipe 2: persist and resolve a security-scoped bookmark intentionally

Bookmarks are a persistence mechanism for a user-granted resource, not an authorization bypass. Store the bookmark data in app-owned protected storage, resolve it later, handle staleness, and balance the access lease.

```swift
import Foundation

struct ScopedBookmarkStore {
    let key = "selected-folder-bookmark"

    func makeBookmark(for url: URL) throws -> Data {
        let didStart = url.startAccessingSecurityScopedResource()
        defer {
            if didStart {
                url.stopAccessingSecurityScopedResource()
            }
        }
        guard didStart else { throw CocoaError(.fileReadNoPermission) }

        return try url.bookmarkData(
            options: [.withSecurityScope],
            includingResourceValuesForKeys: nil,
            relativeTo: nil
        )
    }

    func resolve(_ data: Data) throws -> URL {
        var isStale = false
        let url = try URL(
            resolvingBookmarkData: data,
            options: [.withSecurityScope],
            relativeTo: nil,
            bookmarkDataIsStale: &isStale
        )

        if isStale {
            // Ask the user to reselect or replace the bookmark, then persist
            // a new bookmark. Do not silently widen access.
        }
        return url
    }

    func withAccess<T>(to url: URL, operation: () throws -> T) throws -> T {
        let didStart = url.startAccessingSecurityScopedResource()
        defer {
            if didStart {
                url.stopAccessingSecurityScopedResource()
            }
        }
        guard didStart else { throw CocoaError(.fileReadNoPermission) }
        return try operation()
    }
}
```

For external documents that multiple processes may edit, add `NSFileCoordinator` and, where the document remains presented, an appropriate `NSFilePresenter`/`UIDocument` lifecycle. A bookmark does not prove that the resource still exists, that it is the same version, or that a provider is online.

## Recipe 3: a versioned `FileDocument` snapshot

Use a typed document representation for serialization. Keep migration and domain validation outside the view and never make serialization depend on an ephemeral `MainActor` object.

```swift
import SwiftUI
import UniformTypeIdentifiers

struct Note: Codable, Hashable, Sendable {
    var id: UUID
    var title: String
    var body: String
}

struct NoteDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.json] }
    static var writableContentTypes: [UTType] { [.json] }

    var formatVersion = 1
    var notes: [Note] = []

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
        let notes: [Note]
    }
}
```

Add explicit migration for every older format, corrupt/partial-file recovery, export cancellation, and a test that opens the document through `DocumentGroup` or the selected picker—not only by constructing the struct in a unit test.

## Recipe 4: load a selected photo representation asynchronously

`PhotosPickerItem` is a provider-backed selection. Store the item identity only as provisional UI state, load the representation, and guard against a newer selection replacing the old task.

```swift
import PhotosUI
import SwiftUI

struct PhotoImportView: View {
    @State private var selection: PhotosPickerItem?
    @State private var importedData: Data?
    @State private var loadTask: Task<Void, Never>?

    var body: some View {
        PhotosPicker(
            "Choose an image",
            selection: $selection,
            matching: .images,
            photoLibrary: .shared()
        )
        .onChange(of: selection) { _, newItem in
            loadTask?.cancel()
            guard let newItem else { return }

            loadTask = Task {
                do {
                    let data = try await newItem.loadTransferable(type: Data.self)
                    guard !Task.isCancelled else { return }
                    await MainActor.run {
                        importedData = data
                    }
                } catch {
                    await MainActor.run {
                        importedData = nil
                    }
                }
            }
        }
        .onDisappear {
            loadTask?.cancel()
        }
    }
}
```

In a real feature, prefer a custom `Transferable` representation when the source type and metadata must be controlled. Validate bytes, dimensions, duration, and metadata before expensive Vision/Core ML work, and explain upload/retention before persisting originals.

## Recipe 5: share a redacted typed snapshot

Create a share snapshot from confirmed app state. `Transferable` describes the representation; it does not decide whether private fields should be present.

```swift
import CoreTransferable
import SwiftUI
import UniformTypeIdentifiers

struct ShareSnapshot: Codable, Transferable {
    let title: String
    let summary: String

    static var transferRepresentation: some TransferRepresentation {
        CodableRepresentation(contentType: .json)
    }
}

struct ShareSnapshotButton: View {
    let snapshot: ShareSnapshot

    var body: some View {
        ShareLink(item: snapshot) {
            Label("Share", systemImage: "square.and.arrow.up")
        }
    }
}
```

For large exports, use a file-backed representation or `NSItemProvider` and clean up temporary files after the handoff. Test that location, author, EXIF, internal IDs, and account tokens are absent unless the user-facing export explicitly needs them.

## Recipe 6: present UIKit sharing with the correct device geometry

Use UIKit when the app needs explicit activity-item or presentation control. The system decides which destinations exist.

```swift
import UIKit

@MainActor
func presentShareSheet(
    from presenter: UIViewController,
    items: [Any]
) {
    let controller = UIActivityViewController(
        activityItems: items,
        applicationActivities: nil
    )

    if let popover = controller.popoverPresentationController {
        popover.sourceView = presenter.view
        popover.sourceRect = CGRect(
            x: presenter.view.bounds.midX,
            y: presenter.view.bounds.midY,
            width: 1,
            height: 1
        )
    }

    presenter.present(controller, animated: true)
}
```

Use a snapshot or file URL whose lifetime is long enough for the activity handoff. Do not block the main thread generating a large item through `UIActivityItemSource`; use a provider for expensive work and handle completion/cancellation without claiming that a destination accepted or delivered the content.

## Recipe 7: constrain a WebKit message bridge

The page can send a message, but native code must validate its origin, shape, current navigation, and user authorization before performing a side effect.

```swift
import WebKit

final class NativeBridge: NSObject, WKScriptMessageHandler {
    private let allowedHost = "example.test"

    func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage
    ) {
        guard message.name == "appCommand" else { return }
        guard message.frameInfo.securityOrigin.host == allowedHost else {
            return
        }
        guard let body = message.body as? [String: Any],
              let command = body["command"] as? String,
              command == "requestReview" else {
            return
        }

        // Re-read app-owned state and require the app's current user intent.
        // Never execute a native action from an unvalidated arbitrary string.
    }
}

@MainActor
func makeWebView(bridge: NativeBridge) -> WKWebView {
    let controller = WKUserContentController()
    controller.add(bridge, contentWorld: .page, name: "appCommand")

    let configuration = WKWebViewConfiguration()
    configuration.userContentController = controller
    configuration.websiteDataStore = .nonPersistent()

    return WKWebView(frame: .zero, configuration: configuration)
}
```

The exact content world and data-store policy depend on whether the page is trusted app content, a user account session, or third-party content. Add navigation policy, handler removal, process-termination recovery, cookie/logout tests, and a host allowlist. A content world isolates script namespaces; it does not make the webpage trusted.

## Recipe 8: wrap a PDF document without rebuilding it on every update

Keep `PDFDocument` ownership outside the view update loop and validate imported data before opening it.

```swift
import PDFKit
import SwiftUI

struct PDFReader: UIViewRepresentable {
    let document: PDFDocument

    func makeUIView(context: Context) -> PDFView {
        let view = PDFView()
        view.autoScales = true
        view.displayMode = .singlePageContinuous
        view.document = document
        return view
    }

    func updateUIView(_ view: PDFView, context: Context) {
        if view.document !== document {
            view.document = document
        }
    }
}

func loadPDF(from data: Data) -> PDFDocument? {
    guard data.count < 100 * 1024 * 1024 else { return nil }
    return PDFDocument(data: data)
}
```

Add password/encryption policy, malformed-document handling, page-count/memory limits, annotations, text selection, export, accessibility, and temporary-file cleanup. Rendering a PDF is not proof that its contents are safe to parse or share.

## Recipe 9: finish or cancel a share/document extension request

The extension’s host context is the request boundary. Keep work bounded and call exactly one terminal path for a request.

```swift
import Foundation

final class ShareExtensionCoordinator {
    weak var extensionContext: NSExtensionContext?

    func finish(with resultItems: [NSExtensionItem] = []) {
        extensionContext?.completeRequest(
            returningItems: resultItems,
            completionHandler: nil
        )
    }

    func cancel() {
        extensionContext?.cancelRequest(
            withError: CocoaError(.userCancelled)
        )
    }
}
```

Read `inputItems` through `NSItemProvider`, request only the types needed, show a review/redaction step for sensitive content, and cancel provider loads when the extension is dismissed. Do not assume the containing app is running or that `open(_:)` is an acceptable replacement for completing the host request.

## Recipe 10: write a small redacted App Group projection atomically

Use an App Group only when the widget/extension and app need the same projection. Keep the canonical model elsewhere and write a complete replacement rather than mutating a shared JSON file in place.

```swift
import Foundation

struct WidgetProjection: Codable, Sendable {
    let version: Int
    let title: String
    let status: String
    let generatedAt: Date
}

func writeWidgetProjection(_ projection: WidgetProjection) throws {
    guard let container = FileManager.default.containerURL(
        forSecurityApplicationGroupIdentifier: "group.example.app"
    ) else {
        throw CocoaError(.fileNoSuchFile)
    }

    let fileURL = container.appendingPathComponent("widget-projection.json")
    let temporaryURL = fileURL.appendingPathExtension("tmp")
    let data = try JSONEncoder().encode(projection)
    try data.write(to: temporaryURL, options: [.atomic])

    if FileManager.default.fileExists(atPath: fileURL.path) {
        _ = try FileManager.default.replaceItemAt(
            fileURL,
            withItemAt: temporaryURL
        )
    } else {
        try FileManager.default.moveItem(at: temporaryURL, to: fileURL)
    }
}
```

Use shared `UserDefaults(suiteName:)` only for small values. Add a schema/version check, stale/locked-account state, partial-write recovery, and a deletion/account-switch path. Never put access tokens, raw health data, or unredacted private documents in a widget-readable projection.

## Recipe 11: register and schedule a short background refresh

Register identifiers early in app startup and keep the handler resumable. The requested date is not a promise.

```swift
import BackgroundTasks

let refreshIdentifier = "com.example.app.refresh"

func registerBackgroundTasks() {
    BGTaskScheduler.shared.register(
        forTaskWithIdentifier: refreshIdentifier,
        using: nil
    ) { task in
        guard let refreshTask = task as? BGAppRefreshTask else {
            task.setTaskCompleted(success: false)
            return
        }
        handleRefresh(refreshTask)
    }
}

func scheduleRefresh() throws {
    let request = BGAppRefreshTaskRequest(identifier: refreshIdentifier)
    request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
    try BGTaskScheduler.shared.submit(request)
}

func handleRefresh(_ task: BGAppRefreshTask) {
    let work = Task {
        // Load a small durable checkpoint, refresh if allowed, write a
        // projection, and return quickly.
    }

    task.expirationHandler = {
        work.cancel()
    }

    Task {
        await work.value
        task.setTaskCompleted(success: !work.isCancelled)
    }
}
```

The target also needs the correct permitted-task configuration. Test a normal system launch/termination, not only Xcode’s debug trigger. If a job is important enough to guarantee an outcome, persist its checkpoint and provide a foreground retry/resume route rather than claiming that the scheduler will run at the requested time.

## Recipe 12: schedule processing work with explicit requirements

Use `BGProcessingTaskRequest` for deferred maintenance that may need connectivity or power. A processing task is still interruptible.

```swift
import BackgroundTasks

func scheduleMaintenance() throws {
    let request = BGProcessingTaskRequest(
        identifier: "com.example.app.maintenance"
    )
    request.requiresNetworkConnectivity = true
    request.requiresExternalPower = false
    try BGTaskScheduler.shared.submit(request)
}
```

Split the work into idempotent units, record completed IDs, cancel on expiration, and make retry/backoff explicit. Measure memory and battery on a physical device. Do not use a processing task as a hidden real-time loop, a precise alarm, or a substitute for a server event.

## Recipe 13: a user-started iOS 26 continuous background task

`BGContinuedProcessingTaskRequest` is for a person-started foreground workload that may continue after backgrounding. API spelling, supported resources, and entitlement requirements must be checked against the selected iOS 26 SDK; this is intentionally a route sketch.

```swift
import BackgroundTasks

@available(iOS 26.0, *)
func submitUserStartedExport() throws {
    let request = BGContinuedProcessingTaskRequest(
        identifier: "com.example.app.export",
        title: "Exporting project",
        subtitle: "Preparing a file you requested"
    )

    // Verify the exact enum spelling and capability/entitlement in the
    // selected SDK before using a resource such as GPU.
    request.requiredResources = .default
    request.strategy = .queue

    try BGTaskScheduler.shared.submit(request)
}

@available(iOS 26.0, *)
func handleContinuedTask(_ task: BGContinuedProcessingTask) {
    let work = Task {
        // Checkpoint each export stage and publish meaningful progress.
        // Stop cleanly when Task.isCancelled becomes true.
    }

    task.expirationHandler = {
        work.cancel()
    }

    Task {
        await work.value
        task.setTaskCompleted(success: !work.isCancelled)
    }
}
```

The request must be submitted because of a user action such as tapping Export. The system may reject/queue the request, display progress, let the person cancel it, or terminate it under resource pressure. A continuous task is not proof that GPU/network/CPU work can run indefinitely, and it does not remove the need for a foreground resume/error state.

## Recipe 14: refresh a widget only after the projection changes

Widgets render the projection, not a live actor. Reload only the affected kind after the app commits a new projection.

```swift
import WidgetKit

func commitNewWidgetState(_ projection: WidgetProjection) throws {
    try writeWidgetProjection(projection)
    WidgetCenter.shared.reloadTimelines(
        ofKind: "ExampleStatusWidget"
    )
}
```

For a configurable widget, use `getCurrentConfigurations` or the async equivalent when the app needs to identify which configured instance changed. Keep timeline policies honest: `.after` is an earliest refresh request, `.never` requires an explicit later reload, and the system may coalesce or defer work.

## Recipe 15: update and end a Live Activity with explicit states

ActivityKit is the live-status route, not a widget timeline. Keep content state Codable/sendable and include a final state when ending.

```swift
import ActivityKit

struct ExportAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable {
        var phase: String
        var completed: Int
        var total: Int
        var isStale: Bool
    }

    let exportID: UUID
}

func endExportActivity(
    _ activity: Activity<ExportAttributes>,
    exportID: UUID
) async {
    let finalState = ExportAttributes.ContentState(
        phase: "Complete",
        completed: 1,
        total: 1,
        isStale: false
    )

    await activity.end(
        ActivityContent(state: finalState, staleDate: nil),
        dismissalPolicy: .default
    )
}
```

Start eligibility, foreground/background behavior, push-token environment, stale dates, user permission, supported surfaces, and remote error handling must be verified in the target. Do not display optimistic progress after the work has failed or the app has lost the source of truth.

## Recipe 16: evidence matrix before calling a route complete

| Route | Local/preview evidence | Must still be verified |
| --- | --- | --- |
| PhotosPicker | Picker appears and a fixture loads | iCloud/offline, limited/full access, large assets, physical device, retention. |
| File importer/bookmark | Fixture URL opens and scope balances | Files/iCloud/third-party providers, folder scope, stale bookmark, coordination, revoke. |
| FileDocument/DocumentGroup | Known fixture opens/exports | Migration, corrupt file, autosave, multiwindow, provider conflicts, release target. |
| WebKit bridge | Test page sends a typed message | Redirect/origin attack, process restart, cookie/logout policy, real account, accessibility. |
| PDFKit/share | Fixture renders/share sheet opens | Hostile/malformed PDF, metadata redaction, no destination, large-file memory, iPad geometry. |
| Extension/App Group | Host fixture invokes target | Separate process termination, schema version mismatch, entitlements, signing, real host. |
| Widget/Live Activity | Preview or debug reload | Refresh budget, stale state, foreground start/push, lock screen, supported device/surface. |
| BGAppRefresh/BGProcessing | Xcode debug trigger | Normal system scheduling, expiration, retry, battery, no-network, physical device. |
| BGContinuedProcessingTask | Foreground submission in a target app | iOS 26 SDK/device support, queue/rejection, progress/cancel UI, resource entitlement, resume. |

## Sources

- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [PhotosPickerItem.loadTransferable](https://developer.apple.com/documentation/photosui/photospickeritem/loadtransferable%28type%3A%29)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [SwiftUI presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [UIDocumentPickerViewController](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller)
- [NSURL](https://developer.apple.com/documentation/foundation/nsurl)
- [startAccessingSecurityScopedResource](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [UIActivityViewController](https://developer.apple.com/documentation/uikit/uiactivityviewcontroller)
- [NSItemProvider](https://developer.apple.com/documentation/foundation/nsitemprovider)
- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [WKScriptMessageHandler](https://developer.apple.com/documentation/webkit/wkscriptmessagehandler)
- [WKContentWorld](https://developer.apple.com/documentation/webkit/wkcontentworld)
- [PDFKit](https://developer.apple.com/documentation/pdfkit)
- [PDFDocument](https://developer.apple.com/documentation/pdfkit/pdfdocument)
- [PDFView](https://developer.apple.com/documentation/pdfkit/pdfview)
- [NSExtensionContext](https://developer.apple.com/documentation/foundation/nsextensioncontext)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [Configuring app groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [Timeline](https://developer.apple.com/documentation/widgetkit/timeline)
- [WidgetCenter](https://developer.apple.com/documentation/widgetkit/widgetcenter)
- [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Activity](https://developer.apple.com/documentation/activitykit/activity)
- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [BGTaskScheduler](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler)
- [BGAppRefreshTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgapprefreshtaskrequest)
- [BGProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgprocessingtaskrequest)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
- [BGTask expirationHandler](https://developer.apple.com/documentation/backgroundtasks/bgtask/expirationhandler)
