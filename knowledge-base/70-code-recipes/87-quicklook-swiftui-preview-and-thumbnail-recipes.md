# Quick Look SwiftUI preview and thumbnail recipes

These are compile-oriented route sketches. They demonstrate the architecture for a SwiftUI app, but they are not claimed to compile in this documentation-only workspace. Confirm current SDK signatures, target membership, extension configuration, and system behavior in Xcode.

## Preview item model

~~~swift
import QuickLook

final class LocalPreviewItem: NSObject, QLPreviewItem {
    let previewItemURL: URL?
    let previewItemTitle: String?

    init(url: URL, title: String?) {
        self.previewItemURL = url
        self.previewItemTitle = title
    }
}
~~~

Keep the preview item tied to a validated source snapshot. Do not pass a temporary URL whose lifetime ends while Quick Look is still reading it.

## QLPreviewController in SwiftUI

~~~swift
import QuickLook
import SwiftUI

struct QuickLookPreview: UIViewControllerRepresentable {
    typealias UIViewControllerType = QLPreviewController

    let items: [LocalPreviewItem]
    let onDismiss: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(items: items, onDismiss: onDismiss)
    }

    func makeUIViewController(context: Context) -> QLPreviewController {
        let controller = QLPreviewController()
        controller.dataSource = context.coordinator
        controller.delegate = context.coordinator
        return controller
    }

    func updateUIViewController(
        _ controller: QLPreviewController,
        context: Context
    ) {
        context.coordinator.items = items
        controller.reloadData()
    }

    final class Coordinator: NSObject,
        QLPreviewControllerDataSource,
        QLPreviewControllerDelegate {

        var items: [LocalPreviewItem]
        let onDismiss: () -> Void

        init(items: [LocalPreviewItem], onDismiss: @escaping () -> Void) {
            self.items = items
            self.onDismiss = onDismiss
        }

        func numberOfPreviewItems(
            in controller: QLPreviewController
        ) -> Int {
            items.count
        }

        func previewController(
            _ controller: QLPreviewController,
            previewItemAt index: Int
        ) -> any QLPreviewItem {
            items[index]
        }

        func previewControllerDidDismiss(
            _ controller: QLPreviewController
        ) {
            onDismiss()
        }

        func previewController(
            _ controller: QLPreviewController,
            shouldOpen url: URL,
            for item: any QLPreviewItem
        ) -> Bool {
            // Apply the app's host/scheme policy before leaving the preview.
            url.scheme == "https"
        }
    }
}
~~~

The app should call QLPreviewController.canPreviewItem before presenting. The delegate callback means the preview closed; it does not mean the app’s document was saved.

## Present from an app-owned screen

~~~swift
import QuickLook
import SwiftUI

struct DocumentRow: View {
    let url: URL
    @State private var showingPreview = false
    @State private var message = "Ready"

    var body: some View {
        VStack(alignment: .leading) {
            Text(url.lastPathComponent)
            Button("Preview") {
                guard QLPreviewController.canPreviewItem(url) else {
                    message = "This file cannot be previewed here."
                    return
                }
                showingPreview = true
            }
            Text(message)
                .font(.caption)
        }
        .sheet(isPresented: $showingPreview) {
            QuickLookPreview(
                items: [LocalPreviewItem(url: url, title: url.lastPathComponent)]
            ) {
                showingPreview = false
            }
        }
    }
}
~~~

For production, validate the URL, security scope, provider state, revision, and temporary-file lifetime before this screen offers the action. Use a stable app-owned identifier instead of relying on a path string for long-lived document state.

## Generate a thumbnail asynchronously

~~~swift
import QuickLookThumbnailing
import UniformTypeIdentifiers

enum ThumbnailError: Error {
    case unavailable
}

func generateThumbnail(
    for url: URL,
    size: CGSize,
    scale: CGFloat
) async throws -> CGImage {
    let request = QLThumbnailGenerator.Request(
        fileAt: url,
        size: size,
        scale: scale,
        representationTypes: .thumbnail
    )

    if let type = UTType(filenameExtension: url.pathExtension) {
        request.contentType = type
    }

    return try await withCheckedThrowingContinuation { continuation in
        QLThumbnailGenerator.shared.generateBestRepresentation(
            for: request
        ) { representation, error in
            if let representation {
                continuation.resume(returning: representation.cgImage)
            } else {
                continuation.resume(
                    throwing: error ?? ThumbnailError.unavailable
                )
            }
        }
    }
}
~~~

Update SwiftUI state on the main actor after this async operation. Do not use a thumbnail as proof that parsing, editing, or AI extraction will succeed.

## Progressive thumbnails with cancellation

~~~swift
import QuickLookThumbnailing

final class ThumbnailJob {
    private var request: QLThumbnailGenerator.Request?

    func start(
        url: URL,
        size: CGSize,
        scale: CGFloat,
        onUpdate: @escaping (QLThumbnailRepresentation) -> Void,
        onFailure: @escaping (Error) -> Void
    ) {
        cancel()

        let request = QLThumbnailGenerator.Request(
            fileAt: url,
            size: size,
            scale: scale,
            representationTypes: .all
        )
        self.request = request

        QLThumbnailGenerator.shared.generateRepresentations(
            for: request
        ) { representation, _, error in
            if let representation {
                onUpdate(representation)
            } else if let error {
                onFailure(error)
            }
        }
    }

    func cancel() {
        if let request {
            QLThumbnailGenerator.shared.cancel(request)
        }
        request = nil
    }
}
~~~

In a scrolling view, bind the job to cell identity and cancel when the source leaves the visible work set. Add a source revision to the cell model so a late callback cannot overwrite a newer file.

## Custom Thumbnail Extension skeleton

~~~swift
import QuickLookThumbnailing

final class ThumbnailProvider: QLThumbnailProvider {
    override func provideThumbnail(
        for request: QLFileThumbnailRequest,
        _ handler: @escaping (QLThumbnailReply?, (any Error)?) -> Void
    ) {
        let reply = QLThumbnailReply(
            contextSize: request.maximumSize,
            drawing: { context in
                // Draw a bounded, truthful representation of request.fileURL.
                // Validate the file and return false when rendering fails.
                context.setFillColor(UIColor.secondarySystemBackground.cgColor)
                context.fill(
                    CGRect(
                        origin: .zero,
                        size: request.maximumSize
                    )
                )
                return true
            }
        )
        handler(reply, nil)
    }
}
~~~

The extension’s exact Info.plist and template configuration are part of the target contract. Declare exact UTIs in QLSupportedContentTypes and set QLThumbnailMinimumDimension deliberately. The renderer must tolerate missing/corrupt files and must not require user interaction, network access, or a model download for its basic result.

## AI review handoff

~~~swift
struct AnalysisRequest {
    let sourceURL: URL
    let sourceRevision: String
    let requestedFields: [String]
}

enum AnalysisState {
    case previewing
    case readyForExplicitAnalysis(AnalysisRequest)
    case analyzing
    case proposal(sourceRevision: String, fields: [String])
    case stale
    case failed
}
~~~

The Analyze button should create the request only after the person has inspected or selected the source. A local model or parser can then produce a proposal with page, selection, or time-range provenance. Re-check sourceRevision before committing anything.

## Proof checklist

- compile QuickLook and QuickLookThumbnailing in the named app target;
- compile extension targets separately;
- test canPreviewItem and unsupported-file fallback;
- inspect real preview open/close, external-link policy, and supported edits;
- test thumbnail size, scale, progressive representations, cancellation, and memory;
- verify exact UTIs and Info.plist entries for custom extensions;
- test Files/Spotlight/iCloud invocation for signed extensions;
- test source revision, provider state, temporary-file cleanup, and corrupt input;
- keep AI user-started, typed, source-linked, and reviewable;
- test accessibility and reduced effects on the complete route.

## Sources

- [Quick Look](https://developer.apple.com/documentation/quicklook)
- [QLPreviewController](https://developer.apple.com/documentation/quicklook/qlpreviewcontroller)
- [QLPreviewItem](https://developer.apple.com/documentation/quicklook/qlpreviewitem)
- [QLPreviewControllerDataSource](https://developer.apple.com/documentation/quicklook/qlpreviewcontrollerdatasource)
- [QLPreviewControllerDelegate](https://developer.apple.com/documentation/quicklook/qlpreviewcontrollerdelegate)
- [Quick Look Thumbnailing](https://developer.apple.com/documentation/quicklookthumbnailing)
- [QLThumbnailGenerator](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailgenerator)
- [QLThumbnailGenerator.Request](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailgenerator/request)
- [QLThumbnailRepresentation](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailrepresentation)
- [QLThumbnailProvider](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailprovider)
- [QLFileThumbnailRequest](https://developer.apple.com/documentation/quicklookthumbnailing/qlfilethumbnailrequest)
- [QLThumbnailReply](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailreply)
- [Providing Thumbnails of Your Custom File Types](https://developer.apple.com/documentation/quicklookthumbnailing/providing-thumbnails-of-your-custom-file-types)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [File management](https://developer.apple.com/design/human-interface-guidelines/file-management)
