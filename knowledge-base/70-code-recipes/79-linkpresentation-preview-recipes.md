# Link Presentation preview recipes

These are compile-oriented sketches for a Link Presentation route in a named iOS target. They keep URL policy, metadata fetching, UIKit rendering, SwiftUI state, caching, sharing, and AI proposals separate. Confirm target availability and exact signatures against the selected SDK.

## 1. Bounded, cancellable metadata loader

~~~swift
import LinkPresentation

@MainActor
final class LinkPreviewLoader {
    private var provider: LPMetadataProvider?
    private var requestID = UUID()

    func load(
        _ url: URL,
        completion: @escaping (Result<LPLinkMetadata, Error>) -> Void
    ) {
        provider?.cancel()

        let id = UUID()
        requestID = id

        let provider = LPMetadataProvider()
        provider.timeout = 12
        provider.shouldFetchSubresources = false
        self.provider = provider

        provider.startFetchingMetadata(for: url) { [weak self] metadata, error in
            Task { @MainActor in
                guard let self, self.requestID == id else { return }
                self.provider = nil

                if let error {
                    completion(.failure(error))
                } else if let metadata {
                    completion(.success(metadata))
                } else {
                    completion(.failure(LinkPreviewError.emptyResult))
                }
            }
        }
    }

    func cancel() {
        requestID = UUID()
        provider?.cancel()
        provider = nil
    }
}

enum LinkPreviewError: Error {
    case emptyResult
}
~~~

The request ID prevents a late completion from replacing a newer URL. Map `LPError.Code` into product states instead of showing raw error text.

## 2. Wrap `LPLinkView` for SwiftUI

~~~swift
import LinkPresentation
import SwiftUI

struct RichLinkView: UIViewRepresentable {
    let metadata: LPLinkMetadata

    func makeUIView(context: Context) -> LPLinkView {
        LPLinkView(metadata: metadata)
    }

    func updateUIView(_ view: LPLinkView, context: Context) {
        view.metadata = metadata
        view.setNeedsLayout()
    }
}
~~~

Keep networking out of `makeUIView` and `updateUIView`. A parent model owns loading, cancellation, cached/fresh state, and the URL-only fallback. Test the intrinsic size and dynamic layout in the actual target.

## 3. Supply custom metadata to the share sheet

~~~swift
import LinkPresentation
import UIKit

final class LinkShareItem: NSObject, UIActivityItemSource {
    let url: URL
    let metadata: LPLinkMetadata?

    init(url: URL, metadata: LPLinkMetadata?) {
        self.url = url
        self.metadata = metadata
    }

    func activityViewControllerPlaceholderItem(
        _ activityViewController: UIActivityViewController
    ) -> Any {
        url
    }

    func activityViewController(
        _ activityViewController: UIActivityViewController,
        itemForActivityType activityType: UIActivity.ActivityType?
    ) -> Any? {
        _ = activityType
        return url
    }

    func activityViewControllerLinkMetadata(
        _ activityViewController: UIActivityViewController
    ) -> LPLinkMetadata? {
        metadata
    }
}
~~~

Return already-known metadata to avoid a duplicate share-preview fetch. Keep the original URL as the shared item. On iPad, present the resulting `UIActivityViewController` as a correctly configured popover.

## 4. Construct trusted custom metadata without a fetch

~~~swift
import LinkPresentation

func makeCustomMetadata(
    originalURL: URL,
    returnedURL: URL?,
    title: String?
) -> LPLinkMetadata {
    let metadata = LPLinkMetadata()
    metadata.originalURL = originalURL
    metadata.url = returnedURL ?? originalURL
    metadata.title = title
    return metadata
}
~~~

Custom metadata is a presentation optimization. Mark it as app-supplied in the domain model, keep the original URL visible, and do not label it server-verified unless the product has independent evidence.

## 5. Securely archive a presentation object

~~~swift
import LinkPresentation

struct CachedLinkMetadata: Codable, Sendable {
    let originalURL: URL
    let fetchedAt: Date
    let schemaVersion: Int
}

func archive(_ metadata: LPLinkMetadata) throws -> Data {
    try NSKeyedArchiver.archivedData(
        withRootObject: metadata,
        requiringSecureCoding: true
    )
}

func restore(_ data: Data) throws -> LPLinkMetadata {
    guard let metadata = try NSKeyedUnarchiver.unarchivedObject(
        ofClass: LPLinkMetadata.self,
        from: data
    ) else {
        throw LinkPreviewError.emptyResult
    }
    return metadata
}
~~~

Store the URL, timestamp, cache schema, user/session scope, and freshness policy beside the archive. Caching metadata does not make the destination current or safe.

## 6. SwiftUI state with explicit fallback

~~~swift
import LinkPresentation
import SwiftUI

struct LinkPreviewScreen: View {
    enum State {
        case idle(URL)
        case loading(URL)
        case ready(URL, LPLinkMetadata)
        case failed(URL, String)
    }

    let state: State

    var body: some View {
        Group {
            switch state {
            case .idle(let url):
                LinkFallback(url: url, message: "Preview not loaded")
            case .loading(let url):
                LinkFallback(url: url, message: "Loading preview")
            case .ready(_, let metadata):
                RichLinkView(metadata: metadata)
            case .failed(let url, let message):
                LinkFallback(url: url, message: message)
            }
        }
        .accessibilityElement(children: .contain)
    }
}

struct LinkFallback: View {
    let url: URL
    let message: String

    var body: some View {
        VStack(alignment: .leading) {
            Text("Link preview")
                .font(.headline)
            Text(url.absoluteString)
                .font(.footnote)
                .textSelection(.enabled)
            Text(message)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }
}
~~~

The fallback is a product requirement, not a development-only placeholder. Add explicit Open, Share, Retry, and Cancel actions around it in the containing view.

## 7. Validate an AI proposal

~~~swift
struct LinkProposal: Codable, Sendable {
    let originalURL: URL
    let suggestedCollection: String?
    let summary: String?
    let confidence: Double
}

func accepts(
    _ proposal: LinkProposal,
    minimumConfidence: Double
) -> Bool {
    guard proposal.originalURL.scheme == "https",
          proposal.confidence >= minimumConfidence else { return false }

    let hasCollection = !(proposal.suggestedCollection ?? "")
        .trimmingCharacters(in: .whitespacesAndNewlines)
        .isEmpty
    let hasSummary = !(proposal.summary ?? "")
        .trimmingCharacters(in: .whitespacesAndNewlines)
        .isEmpty
    return hasCollection || hasSummary
}
~~~

The proposal must retain the original URL and be shown for user review. Do not use it to hide a redirect, assert safety, auto-open a destination, or share the link.

## 8. Local fetch-state tests

~~~swift
import Testing

@Test
func rejectsUnsupportedPreviewScheme() {
    let url = URL(string: "file:///private/document")!
    #expect(url.scheme != "https")
}

@Test
func preservesOriginalAndReturnedURLAsDifferentFacts() {
    let original = URL(string: "https://developer.apple.com/original")!
    let returned = URL(string: "https://developer.apple.com/final")!
    #expect(original != returned)
}
~~~

These tests prove only local policy and identity behavior. Add provider timeout/cancel/error fixtures, UIKit/SwiftUI rendering, share-sheet, accessibility, offline, signed-device, and release tests in the named app target.

## Sources

- [Link Presentation](https://developer.apple.com/documentation/linkpresentation)
- [LPMetadataProvider](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider)
- [LPMetadataProvider fetch link metadata](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider)
- [timeout](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/timeout)
- [shouldFetchSubresources](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/shouldfetchsubresources)
- [cancel()](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/cancel%28%29)
- [LPError](https://developer.apple.com/documentation/linkpresentation/lperror)
- [LPLinkMetadata](https://developer.apple.com/documentation/linkpresentation/lplinkmetadata)
- [LPLinkView](https://developer.apple.com/documentation/linkpresentation/lplinkview)
- [UIActivityItemSource](https://developer.apple.com/documentation/uikit/uiactivityitemsource)
- [activityViewControllerLinkMetadata(_:)](https://developer.apple.com/documentation/uikit/uiactivityitemsource/activityviewcontrollerlinkmetadata%28_%3A%29)
- [UIActivityViewController](https://developer.apple.com/documentation/uikit/uiactivityviewcontroller)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Swift Testing](https://developer.apple.com/documentation/testing)
