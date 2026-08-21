# CGImageSource and CGImageDestination recipes

These are compile-oriented route sketches for Image I/O. They intentionally keep the source, derivative, proposal, and export boundaries visible. They are not claimed to compile in this documentation-only workspace; confirm the current SDK signatures and bridge types in the named Xcode target.

Before using a recipe:

- import ImageIO and UniformTypeIdentifiers in the target that owns the route;
- validate the URL or Data source and apply byte/pixel/frame budgets;
- keep security-scoped URL access and temporary files scoped;
- perform expensive decoding off the main actor and publish UI state on the main actor;
- test the actual source formats and deployment target;
- reopen finalized output before sharing or committing it.

## 1. Inspect a source without decoding full resolution

Use source inspection to decide what the next step is. Do not derive identity or domain truth from the returned dictionaries.

~~~swift
import Foundation
import ImageIO

struct ImageSourceSummary {
    let typeIdentifier: String?
    let imageCount: Int
    let primaryIndex: Int
    let containerProperties: [String: Any]
}

func inspectImageSource(data: Data) throws -> ImageSourceSummary {
    guard !data.isEmpty else {
        throw ImageRouteError.emptyInput
    }

    guard let source = CGImageSourceCreateWithData(data as CFData, nil) else {
        throw ImageRouteError.unreadableSource
    }

    let type = CGImageSourceGetType(source).map(String.init)
    let count = CGImageSourceGetCount(source)
    let primaryIndex = CGImageSourceGetPrimaryImageIndex(source)
    let properties = (CGImageSourceCopyProperties(source, nil) as NSDictionary?)
        .map { $0 as? [String: Any] ?? [:] } ?? [:]

    return ImageSourceSummary(
        typeIdentifier: type,
        imageCount: count,
        primaryIndex: primaryIndex,
        containerProperties: properties
    )
}

enum ImageRouteError: Error {
    case emptyInput
    case unreadableSource
    case invalidIndex
    case unableToCreateThumbnail
    case unableToCreateDestination
    case unableToFinalize
    case outputVerificationFailed
}
~~~

The exact Swift bridging of Core Foundation dictionaries can vary with the SDK. Treat this as a route sketch and let the target compiler choose the narrowest safe cast.

## 2. Create an orientation-correct thumbnail

Use a thumbnail for browse, list, grid, and AI preflight. Set the maximum pixel size deliberately and do not retain the full source image when a thumbnail is enough.

~~~swift
import Foundation
import ImageIO

func makeThumbnail(
    data: Data,
    index: Int = 0,
    maximumPixelSize: Int
) throws -> CGImage {
    guard let source = CGImageSourceCreateWithData(data as CFData, nil) else {
        throw ImageRouteError.unreadableSource
    }

    guard index >= 0 && index < CGImageSourceGetCount(source) else {
        throw ImageRouteError.invalidIndex
    }

    let options: [CFString: Any] = [
        kCGImageSourceCreateThumbnailFromImageAlways: true,
        kCGImageSourceCreateThumbnailWithTransform: true,
        kCGImageSourceThumbnailMaxPixelSize: maximumPixelSize,
        kCGImageSourceShouldCache: false
    ]

    guard let thumbnail = CGImageSourceCreateThumbnailAtIndex(
        source,
        index,
        options as CFDictionary
    ) else {
        throw ImageRouteError.unableToCreateThumbnail
    }

    return thumbnail
}
~~~

For a model derivative, use the same index and orientation that the review UI presents. If a model requires a different crop or color policy, record that derivative separately from the display thumbnail.

## 3. Decode one image with bounded caching

Full image creation should happen only when the selected task needs it. The read options are resource controls, not an authorization or safety check.

~~~swift
func decodeImage(
    data: Data,
    index: Int,
    allowFloatingPoint: Bool = false
) throws -> CGImage {
    guard let source = CGImageSourceCreateWithData(data as CFData, nil) else {
        throw ImageRouteError.unreadableSource
    }

    let options: [CFString: Any] = [
        kCGImageSourceShouldCache: false,
        kCGImageSourceShouldCacheImmediately: false,
        kCGImageSourceShouldAllowFloat: allowFloatingPoint,
        kCGImageSourceSubsampleFactor: 1
    ]

    guard let image = CGImageSourceCreateImageAtIndex(
        source,
        index,
        options as CFDictionary
    ) else {
        throw ImageRouteError.unreadableSource
    }

    return image
}
~~~

Use a pixel budget before calling this function. A compressed file can expand into a large decoded bitmap.

## 4. Feed an incremental source

Each update must contain all accumulated bytes. The final flag is the only point at which the route can say the stream is complete.

~~~swift
import ImageIO

enum IncrementalImageState {
    case readingHeader
    case incomplete
    case complete
    case unknownType
    case invalid
    case unexpectedEnd
}

func updateIncrementalSource(
    source: CGImageSource,
    accumulatedData: Data,
    isFinal: Bool
) -> IncrementalImageState {
    CGImageSourceUpdateData(source, accumulatedData as CFData, isFinal)

    switch CGImageSourceGetStatus(source) {
    case .statusReadingHeader:
        return .readingHeader
    case .statusIncomplete:
        return .incomplete
    case .statusComplete:
        return .complete
    case .statusUnknownType:
        return .unknownType
    case .statusInvalidData:
        return .invalid
    case .statusUnexpectedEOF:
        return .unexpectedEnd
    @unknown default:
        return .incomplete
    }
}

func makeIncrementalSource() -> CGImageSource {
    CGImageSourceCreateIncremental(nil)
}
~~~

The status enum cases and Core Foundation bridge should be confirmed against the selected SDK. Publish a partial thumbnail only as a partial derivative, and invalidate it when final bytes or the source revision change.

## 5. Read properties and metadata separately

Properties are useful for dimensions, orientation, format-specific dictionaries, and container facts. CGImageMetadata is the XMP-oriented tag object. Keep both in the source record when the product needs them.

~~~swift
func inspectImageAtIndex(
    source: CGImageSource,
    index: Int
) -> (properties: NSDictionary?, metadata: CGImageMetadata?) {
    let properties = CGImageSourceCopyPropertiesAtIndex(
        source,
        index,
        nil
    ) as NSDictionary?

    let metadata = CGImageSourceCopyMetadataAtIndex(
        source,
        index,
        nil
    )

    return (properties, metadata)
}
~~~

Do not print the complete dictionaries into analytics or logs. Select fields for the product UI, and treat location, authoring, maker, and custom XMP values as potentially sensitive.

## 6. Export a decoded image with a privacy policy

This route writes to a temporary URL, checks finalization, and reopens the file. The destination option keys are policy inputs; they do not replace post-write verification.

~~~swift
import Foundation
import ImageIO
import UniformTypeIdentifiers

func exportPrivateJPEG(
    image: CGImage,
    to outputURL: URL,
    quality: Double = 0.9
) throws {
    let destinationOptions: [CFString: Any] = [
        kCGImageDestinationLossyCompressionQuality: quality,
        kCGImageMetadataShouldExcludeGPS: true,
        kCGImageMetadataShouldExcludeXMP: true,
        kCGImageDestinationMergeMetadata: false
    ]

    guard let destination = CGImageDestinationCreateWithURL(
        outputURL as CFURL,
        UTType.jpeg.identifier as CFString,
        1,
        nil
    ) else {
        throw ImageRouteError.unableToCreateDestination
    }

    CGImageDestinationAddImage(
        destination,
        image,
        destinationOptions as CFDictionary
    )

    guard CGImageDestinationFinalize(destination) else {
        throw ImageRouteError.unableToFinalize
    }
}
~~~

The GPS flag covers the documented EXIF and corresponding XMP GPS fields; it does not guarantee that maker-note or custom XMP location data has disappeared. If the product promises a stronger privacy projection, construct and verify a new metadata object or use a destination format that does not retain the unwanted fields.

## 7. Copy a source into a destination without an app-owned full decode

Use the source-to-destination route when the current task is a container conversion or metadata policy and the target format supports the source contents. Keep an error pointer and verify the final output.

~~~swift
func convertSource(
    sourceData: Data,
    to outputURL: URL,
    destinationType: CFString
) throws {
    guard let source = CGImageSourceCreateWithData(sourceData as CFData, nil) else {
        throw ImageRouteError.unreadableSource
    }

    guard let destination = CGImageDestinationCreateWithURL(
        outputURL as CFURL,
        destinationType,
        1,
        nil
    ) else {
        throw ImageRouteError.unableToCreateDestination
    }

    let options: [CFString: Any] = [
        kCGImageMetadataShouldExcludeGPS: true,
        kCGImageMetadataShouldExcludeXMP: true,
        kCGImageDestinationMergeMetadata: false
    ]

    var unmanagedError: Unmanaged<CFError>?
    let copied = CGImageDestinationCopyImageSource(
        destination,
        source,
        options as CFDictionary,
        &unmanagedError
    )

    if let unmanagedError {
        unmanagedError.release()
    }

    guard copied, CGImageDestinationFinalize(destination) else {
        throw ImageRouteError.unableToFinalize
    }
}
~~~

The source-to-destination function is format- and option-sensitive. Confirm the current SDK signature and test malformed, multi-image, auxiliary-data, and metadata-heavy files before treating this as a general converter.

## 8. Add multiple frames or source images

For an animation or multi-image container, create the destination with the expected count and add each image or source index in the intended order. Preserve timing and container properties according to the format contract.

~~~swift
func writeFrames(
    frames: [CGImage],
    to outputURL: URL,
    type: CFString,
    frameProperties: [[CFString: Any]]
) throws {
    guard frames.count == frameProperties.count else {
        throw ImageRouteError.outputVerificationFailed
    }

    guard let destination = CGImageDestinationCreateWithURL(
        outputURL as CFURL,
        type,
        frames.count,
        nil
    ) else {
        throw ImageRouteError.unableToCreateDestination
    }

    for (frame, properties) in zip(frames, frameProperties) {
        CGImageDestinationAddImage(
            destination,
            frame,
            properties as CFDictionary
        )
    }

    guard CGImageDestinationFinalize(destination) else {
        throw ImageRouteError.unableToFinalize
    }
}
~~~

Do not use the first frame as proof that timing, loop count, stereo grouping, or auxiliary data survived. Reopen the output and inspect the exact properties required by the product.

## 9. Reopen and verify a destination

Make verification a separate function so a caller cannot accidentally treat finalization as the entire export contract.

~~~swift
func verifyOutput(
    at outputURL: URL,
    expectedCount: Int
) throws {
    guard let source = CGImageSourceCreateWithURL(
        outputURL as CFURL,
        nil
    ) else {
        throw ImageRouteError.outputVerificationFailed
    }

    guard CGImageSourceGetCount(source) == expectedCount else {
        throw ImageRouteError.outputVerificationFailed
    }

    guard CGImageSourceGetStatus(source) == .statusComplete else {
        throw ImageRouteError.outputVerificationFailed
    }

    guard CGImageSourceCreateThumbnailAtIndex(
        source,
        0,
        [
            kCGImageSourceCreateThumbnailFromImageAlways: true,
            kCGImageSourceThumbnailMaxPixelSize: 512,
            kCGImageSourceShouldCache: false
        ] as CFDictionary
    ) != nil else {
        throw ImageRouteError.outputVerificationFailed
    }
}
~~~

Extend this function with the product’s required type, dimension, orientation, metadata, frame, and auxiliary-data assertions. A successful reopen proves parseability of the output, not acceptance by every external destination.

## 10. Keep the SwiftUI boundary small

The view model should publish a bounded derivative and typed state. The Image I/O work belongs in an async service or actor/queue that owns cancellation and memory policy.

~~~swift
import SwiftUI

@MainActor
final class ImageReviewModel: ObservableObject {
    enum State {
        case idle
        case loading
        case ready(CGImage)
        case failed(String)
    }

    @Published private(set) var state: State = .idle
    private var work: Task<Void, Never>?

    func loadThumbnail(data: Data) {
        work?.cancel()
        state = .loading

        work = Task {
            do {
                let image = try await Task.detached(priority: .userInitiated) {
                    try makeThumbnail(data: data, maximumPixelSize: 768)
                }.value

                guard !Task.isCancelled else { return }
                state = .ready(image)
            } catch {
                guard !Task.isCancelled else { return }
                state = .failed("The image could not be prepared.")
            }
        }
    }

    func cancel() {
        work?.cancel()
        work = nil
        state = .idle
    }
}
~~~

The detached task is only a route sketch. Confirm Sendable and Core Graphics ownership behavior in the selected SDK, and prefer an actor or dedicated service when the pipeline shares caches or mutable buffers.

## 11. Build a reviewable AI handoff

Keep the model input and output typed:

~~~swift
struct ImageAnalysisInput: Sendable {
    let sourceID: String
    let sourceRevision: String
    let imageIndex: Int
    let derivativePixelSize: Int
    let includesMetadata: Bool
}

struct ImageAnalysisProposal: Sendable {
    let sourceRevision: String
    let suggestedTitle: String
    let needsReview: Bool
    let modelRouteVersion: String
}

func accept(
    proposal: ImageAnalysisProposal,
    currentSourceRevision: String
) throws {
    guard proposal.sourceRevision == currentSourceRevision else {
        throw ImageRouteError.outputVerificationFailed
    }
}
~~~

The proposal is not a domain record until the user accepts it and the app validates the fields. Keep the source revision check even when the view currently shows only one image.

## 12. Compile and proof checklist

- Compile source creation, thumbnailing, status handling, destination creation, and finalization in a named target.
- Verify the current SDK’s Core Foundation dictionary and error-pointer bridge types.
- Run deterministic fixtures for type, count, dimensions, orientation, metadata, incremental status, invalid data, and finalization failure.
- Exercise cancellation and source replacement while a decode or model task is running.
- Run large-image memory and scrolling tests on a physical device.
- Test PhotosPicker, security-scoped files, document providers, and ShareLink in the actual target.
- Reopen every finalized output and verify the promised properties.
- Test VoiceOver, Dynamic Type, reduced transparency, Reduce Motion, contrast, RTL, keyboard, pointer, and other in-scope input methods.
- Test camera-origin HEIC, HDR, depth, gain-map, animation, and spatial files only when the product advertises the route.
- Keep source, derivative, proposal, and destination evidence in separate records.

## Related routes

- [Image I/O source, destination, metadata, and media pipelines](../42-framework-deep-dives/54-imageio-source-destination-and-metadata.md)
- [Image I/O media review and metadata design](../21-design-deep-dives/74-imageio-media-review-and-metadata-design.md)
- [Image I/O incremental decode and safe export route](../50-capability-recipes/77-imageio-incremental-decode-and-safe-export-route.md)
- [Image I/O source and destination proof matrix](../60-verification/71-imageio-source-destination-proof-matrix.md)
- [ImageRenderer, PDF, and Transferable recipes](28-image-renderer-export-recipes.md)
- [Vision, capture, and review recipes](09-vision-capture-and-review-recipes.md)

## Sources

- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [Image I/O Functions](https://developer.apple.com/documentation/imageio/image-i-o-functions)
- [CGImageSourceStatus](https://developer.apple.com/documentation/imageio/cgimagesourcestatus)
- [CGImageSourceUpdateData](https://developer.apple.com/documentation/imageio/cgimagesourceupdatedata%28_%3A_%3A_%3A%29?language=objc)
- [CGImageSourceCreateThumbnailAtIndex](https://developer.apple.com/documentation/imageio/cgimagesourcecreatethumbnailatindex%28_%3A_%3A_%3A%29)
- [CGImageMetadata](https://developer.apple.com/documentation/imageio/cgimagemetadata)
- [CGMutableImageMetadata](https://developer.apple.com/documentation/imageio/cgmutableimagemetadata)
- [CGImageDestinationCopyImageSource](https://developer.apple.com/documentation/imageio/cgimagedestinationcopyimagesource%28_%3A_%3A_%3A_%3A%29)
- [CGImageDestinationFinalize](https://developer.apple.com/documentation/imageio/cgimagedestinationfinalize%28_%3A%29)
- [Writing spatial photos](https://developer.apple.com/documentation/imageio/writing-spatial-photos)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
