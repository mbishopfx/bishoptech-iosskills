# Media, Vision, Core ML, NFC, and Music Recipes

The Vision/Core ML portions connect to the [reviewable multimodal AI pipeline](../31-on-device-ai-recipes/06-reviewable-multimodal-ai-pipeline.md) and [on-device AI evaluation discipline](../30-on-device-ai/10-on-device-ai-evaluation-and-model-update-discipline.md). Keep media capture, inference, provenance, review, and domain commit as separate evidence boundaries.

## Scope and compile boundary

These are compile-oriented route sketches for AVKit/AVFoundation, Core Image, VideoToolbox, Vision, Core ML, Natural Language, Core NFC, MusicKit, and ShazamKit. They are not compiled in this documentation-only workspace and do not prove model quality, hardware codec support, camera/microphone/NFC availability, MusicKit account/subscription state, Shazam catalog access, audio/video timing, thermal behavior, or physical-device performance.

Keep processing reviewable:

`authorized source -> bounded input -> cancellable processing -> typed result -> provenance/confidence -> review/side effect`

## Recipe 1: reuse a Core Image context and isolate mutable filters

`CIImage` is a recipe; `CIFilter` is mutable; `CIContext` owns expensive rendering state. Reuse a context for a rendering surface, but create/configure a filter per operation or isolate access.

```swift
import CoreImage
import CoreImage.CIFilterBuiltins

final class ImageRenderer {
    private let context: CIContext

    init(device: MTLDevice? = MTLCreateSystemDefaultDevice()) {
        if let device {
            context = CIContext(mtlDevice: device)
        } else {
            context = CIContext()
        }
    }

    func renderSepia(_ input: CIImage) -> CGImage? {
        let filter = CIFilter.sepiaTone()
        filter.inputImage = input
        filter.intensity = 0.85
        guard let output = filter.outputImage else { return nil }
        return context.createCGImage(output, from: output.extent)
    }
}
```

Preserve orientation/color space, avoid creating a context per frame, and add cancellation between stages for batch work. Measure memory and render latency on real devices.

## Recipe 2: run Vision OCR with orientation and review state

Use the correct image orientation and treat recognized text as a proposal. Bound input size and use the request revision/language policy that the target SDK supports.

```swift
import Vision

struct OCRProposal: Sendable {
    let sourceID: UUID
    let text: String
    let confidence: Float?
    let reviewed: Bool
}

func recognizeText(
    data: Data,
    orientation: CGImagePropertyOrientation,
    sourceID: UUID
) throws -> OCRProposal {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["en-US"]

    let handler = VNImageRequestHandler(
        data: data,
        orientation: orientation,
        options: [:]
    )
    try handler.perform([request])

    let observations = request.results ?? []
    let strings = observations.compactMap {
        $0.topCandidates(1).first?.string
    }
    let confidence = observations.first?.topCandidates(1).first?.confidence
    return OCRProposal(
        sourceID: sourceID,
        text: strings.joined(separator: "\n"),
        confidence: confidence,
        reviewed: false
    )
}
```

Do not commit OCR output directly to contacts, payments, health records, or other consequential systems. Preserve source ID/model revision, allow correction, and define raw-media deletion.

## Recipe 3: load a Core ML model asynchronously with a measured policy

Compute-unit selection expresses a runtime policy; it does not promise a Neural Engine, GPU, latency, accuracy, or thermal result on every device.

```swift
import CoreML

actor ModelRuntime {
    private var model: MLModel?

    func load(compiledURL: URL) async throws {
        let configuration = MLModelConfiguration()
        configuration.computeUnits = .all
        model = try await MLModel.load(
            contentsOf: compiledURL,
            configuration: configuration
        )
    }

    func predict(_ features: MLFeatureProvider) throws -> MLFeatureProvider {
        guard let model else { throw CocoaError(.fileReadNoSuchFile) }
        return try model.prediction(from: features)
    }
}
```

Validate model description/input shape, model version, normalization, output schema, missing asset, compilation failure, cancellation, and memory. Keep a manual/older-model fallback and store evaluation fixtures with the model version. Measure representative devices and thermal states rather than inferring quality from a successful prediction.

## Recipe 4: run an NFC tag reader as a user-mediated session

Core NFC requires target configuration and a physical tag. A reader session expires or invalidates; only one session can be active at a time.

```swift
import CoreNFC

final class NDEFReader: NSObject, NFCNDEFReaderSessionDelegate {
    private var session: NFCNDEFReaderSession?

    func begin() {
        guard NFCNDEFReaderSession.readingAvailable else {
            // Show an unavailable/manual-entry route.
            return
        }

        let reader = NFCNDEFReaderSession(
            delegate: self,
            queue: nil,
            invalidateAfterFirstRead: true
        )
        reader.alertMessage = "Hold your iPhone near the tag."
        session = reader
        reader.begin()
    }

    func readerSession(
        _ session: NFCNDEFReaderSession,
        didDetectNDEFs messages: [NFCNDEFMessage]
    ) {
        let payloads = messages.flatMap(\.records)
        // Parse a strict allowlist of payload types/schemes and validate the
        // action before updating app state.
        _ = payloads
    }

    func readerSession(
        _ session: NFCNDEFReaderSession,
        didInvalidateWithError error: Error
    ) {
        // Map user cancellation, timeout, no-tag, and protocol errors to
        // recoverable UI. Do not treat invalidation as a successful read.
        _ = error
    }
}
```

Add `NFCReaderUsageDescription` and the NFC reader entitlement/formats required by the protocol. A tag payload is untrusted input; it is not proof of authenticity, payment, identity, or location. Verify with real tag fixtures on a physical device.

## Recipe 5: request MusicKit authorization before catalog/playback work

Keep permission, Apple Music subscription/capability, catalog request, and playback state separate.

```swift
import MusicKit

func requestMusicAccess() async -> MusicAuthorization.Status {
    await MusicAuthorization.request()
}

func loadSongs(searchTerm: String) async throws -> MusicCatalogSearchResponse {
    var request = MusicCatalogSearchRequest(
        term: searchTerm,
        types: [Song.self]
    )
    request.limit = 10
    return try await request.response()
}
```

Before calling a real feature, check authorization and the current `MusicSubscription` capabilities. Handle no subscription, account switch, catalog/network failure, content restrictions, playback interruption, and user-selected audio routes. Keep Apple Music catalog provenance and licensing/product policy explicit; a search result is not an app-owned canonical record.

## Recipe 6: use ShazamKit match/no-match/error states

Use a signature or streaming buffer, stop capture when the feature ends, and preserve only the result/signature needed by the product.

```swift
import ShazamKit

func matchSignature(_ signature: SHSignature) async -> String {
    let session = SHSession()
    let result = await session.result(from: signature)

    switch result {
    case .match(let match):
        return "match:\(match.mediaItems.count)"
    case .noMatch:
        return "no-match"
    case .error(let error, _):
        return "error:\(String(describing: error))"
    }
}
```

For microphone matching, configure the audio session and consent first. Handle noisy/partial audio, no match, catalog access, custom catalog, session reset, and raw-audio retention. A match means a signature resembles catalog content; it does not prove a speaker, ownership, authorization, or legal identity.

## Recipe 7: keep video compression lifecycle explicit

VideoToolbox is a low-level CF-style session route. Use it only when higher-level AVFoundation export is insufficient, and keep the API spelling/bridging verified against the selected SDK.

```swift
import VideoToolbox

final class EncoderLifetime {
    private var session: VTCompressionSession?

    func start(width: Int32, height: Int32) throws {
        var created: VTCompressionSession?
        let status = VTCompressionSessionCreate(
            allocator: kCFAllocatorDefault,
            width: width,
            height: height,
            codecType: kCMVideoCodecType_H264,
            encoderSpecification: nil,
            imageBufferAttributes: nil,
            compressedDataAllocator: nil,
            outputCallback: nil,
            refcon: nil,
            compressionSessionOut: &created
        )
        guard status == noErr, let created else {
            throw NSError(domain: NSOSStatusErrorDomain, code: Int(status))
        }
        session = created
    }

    func finish() {
        guard let session else { return }
        VTCompressionSessionCompleteFrames(
            session,
            untilPresentationTimeStamp: .invalid
        )
        VTCompressionSessionInvalidate(session)
        self.session = nil
    }
}
```

The callback, pixel format, timestamps, bitrate/quality, color transfer, frame submission, completion, and container/muxing policy are omitted here deliberately. Measure frame latency, dropped frames, hardware support, memory, and thermal behavior on the target device.

## Recipe 8: bound live media inference and cancel stale work

Do not create one unbounded inference task per camera/audio frame. Prefer a latest-value buffer for guidance, or a durable ordered queue when every sample matters.

```swift
actor LatestFrameGate<Frame: Sendable> {
    private var latest: Frame?
    private var consumerRunning = false

    func offer(_ frame: Frame) {
        latest = frame
    }

    func consume(
        _ process: @escaping (Frame) async -> Void
    ) async {
        guard !consumerRunning else { return }
        consumerRunning = true
        defer { consumerRunning = false }

        while let frame = latest {
            latest = nil
            await process(frame)
        }
    }
}
```

Add a cancellation token/generation when a view/session ends, release sample buffers promptly, and record whether dropping frames is acceptable for the feature. Do not call a live route “real time” without a measured device/fixture budget.

## Recipe 9: proof matrix

| Route | Fixture evidence | Physical/release evidence |
| --- | --- | --- |
| Core Image | Deterministic image output and color-space fixture | Device GPU/CPU path, memory, color accuracy, thermal, and live-frame performance. |
| Vision/Core ML/Natural Language | Versioned fixtures, output schema, no-input/low-confidence cases | Model asset/device availability, latency, memory/thermal, language/locale, quality review, privacy. |
| Core NFC | Payload parser/unit test, session state reducer | Entitlement/usage description, real tag/protocol, timeout/cancel, hardware orientation/range, physical device. |
| MusicKit | Mock/fixture request and permission reducer | Real Apple Music authorization/subscription/catalog, account switch, playback route/interruption, release configuration. |
| ShazamKit | Signature/match reducer and custom catalog fixture | Microphone permission, noisy/partial audio, catalog access, no match/error, raw-audio retention, physical device. |
| VideoToolbox/AVFoundation | Mock asset/export and state machine | Codec/device support, frame/audio timing, hardware path, cancellation, disk, battery/thermal, real media. |

## Sources

- [AVKit](https://developer.apple.com/documentation/avkit)
- [AVPlayerViewController](https://developer.apple.com/documentation/avkit/avplayerviewcontroller)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [CIContext](https://developer.apple.com/documentation/coreimage/cicontext)
- [CIFilter](https://developer.apple.com/documentation/coreimage/cifilter-swift.class)
- [Video Toolbox](https://developer.apple.com/documentation/videotoolbox)
- [VTCompressionSession](https://developer.apple.com/documentation/videotoolbox/vtcompressionsession-api-collection)
- [Vision](https://developer.apple.com/documentation/vision)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [VNRecognizeTextRequest](https://developer.apple.com/documentation/vision/vnrecognizetextrequest)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [Building an NFC Tag-Reader App](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [MusicKit](https://developer.apple.com/documentation/musickit)
- [MusicAuthorization](https://developer.apple.com/documentation/musickit/musicauthorization)
- [MusicCatalogSearchRequest](https://developer.apple.com/documentation/musickit/musiccatalogsearchrequest)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)
- [Matching audio using the built-in microphone](https://developer.apple.com/documentation/shazamkit/matching-audio-using-the-built-in-microphone)
