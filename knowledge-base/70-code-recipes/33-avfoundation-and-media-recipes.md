# AVFoundation and media recipes

These are compile-oriented route sketches for iOS 26 and Swift 6.2-style projects. They are not compiled in this documentation workspace. Resolve every signature in the selected SDK, add the target’s privacy strings and capabilities, and prove camera, microphone, audio-route, codec, model, and export behavior on a signed physical device.

The snippets intentionally keep the framework adapter separate from SwiftUI. The UI receives values and states; it does not own a capture session or audio engine in its body.

## Recipe 1: Actor-owned camera session

Apple’s current AVCam sample uses an actor as the capture service because configuring and starting a session can block. Keep the actor’s mutable state small and keep delegate adapters at the framework boundary. The exact sendability annotations for AVFoundation delegate types may vary with the SDK; do not silence strict-concurrency diagnostics with unchecked sendability until the ownership is understood.

    import AVFoundation

    actor CameraCaptureService {
        private let session = AVCaptureSession()
        private let videoOutput = AVCaptureVideoDataOutput()
        private let sessionQueue = DispatchQueue(label: "camera.session")
        private var sessionToken = UUID()
        private var isConfigured = false

        func authorizeCamera() async -> Bool {
            switch AVCaptureDevice.authorizationStatus(for: .video) {
            case .authorized:
                true
            case .notDetermined:
                await AVCaptureDevice.requestAccess(for: .video)
            default:
                false
            }
        }

        func configure() async throws {
            guard await authorizeCamera() else {
                throw CaptureError.permissionDenied
            }

            try await withCheckedThrowingContinuation { continuation in
                sessionQueue.async {
                    do {
                        try self.configureOnSessionQueue()
                        continuation.resume()
                    } catch {
                        continuation.resume(throwing: error)
                    }
                }
            }
        }

        func start() async {
            await withCheckedContinuation { continuation in
                sessionQueue.async {
                    if !self.session.isRunning {
                        self.session.startRunning()
                    }
                    continuation.resume()
                }
            }
        }

        func stop() async {
            sessionToken = UUID()
            await withCheckedContinuation { continuation in
                sessionQueue.async {
                    if self.session.isRunning {
                        self.session.stopRunning()
                    }
                    continuation.resume()
                }
            }
        }

        func token() -> UUID {
            sessionToken
        }

        private func configureOnSessionQueue() throws {
            guard !isConfigured else { return }

            guard let device = AVCaptureDevice.default(
                .builtInWideAngleCamera,
                for: .video,
                position: .back
            ) else {
                throw CaptureError.cameraUnavailable
            }

            let input = try AVCaptureDeviceInput(device: device)

            session.beginConfiguration()
            defer { session.commitConfiguration() }

            guard session.canAddInput(input) else {
                throw CaptureError.cannotAddInput
            }
            guard session.canAddOutput(videoOutput) else {
                throw CaptureError.cannotAddOutput
            }

            session.addInput(input)
            videoOutput.alwaysDiscardsLateVideoFrames = true
            session.addOutput(videoOutput)
            isConfigured = true
        }
    }

    enum CaptureError: Error {
        case permissionDenied
        case cameraUnavailable
        case cannotAddInput
        case cannotAddOutput
    }

This is a route sketch, not a drop-in actor implementation. In a real target, keep the session queue ownership consistent, expose a preview connection through a dedicated preview bridge, and move UI updates to MainActor. A continuation must resume exactly once; if a queue/actor bridge becomes more complicated, prefer an Apple-provided async API or a smaller adapter.

## Recipe 2: Bounded video-frame delegate

Use a queue and a frame policy that matches the product contract. A live current-frame feature can discard late frames. An archival or measurement feature needs a different writer and cannot silently treat dropped frames as complete evidence.

    final class LiveFrameDelegate: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
        private let processor: LatestFrameProcessor

        init(processor: LatestFrameProcessor) {
            self.processor = processor
        }

        func captureOutput(
            _ output: AVCaptureOutput,
            didOutput sampleBuffer: CMSampleBuffer,
            from connection: AVCaptureConnection
        ) {
            guard CMSampleBufferDataIsReady(sampleBuffer) else { return }

            let snapshot = FrameSnapshot(
                sampleBuffer: sampleBuffer,
                presentationTime: CMSampleBufferGetPresentationTimeStamp(sampleBuffer),
                videoOrientation: connection.videoRotationAngle
            )

            processor.offer(snapshot)
        }

        func captureOutput(
            _ output: AVCaptureOutput,
            didDrop sampleBuffer: CMSampleBuffer,
            from connection: AVCaptureConnection
        ) {
            processor.recordDrop()
        }
    }

    actor LatestFrameProcessor {
        private var newest: FrameSnapshot?
        private var processing = false
        private var droppedFrameCount = 0
        private var token = UUID()

        func offer(_ frame: FrameSnapshot) {
            newest = frame
            guard !processing else { return }
            processing = true
            let currentToken = token

            Task {
                await drain(token: currentToken)
            }
        }

        func recordDrop() {
            droppedFrameCount += 1
        }

        func cancel() {
            token = UUID()
            newest = nil
            processing = false
        }

        private func drain(token currentToken: UUID) async {
            while let frame = newest {
                newest = nil
                guard currentToken == token else { break }
                do {
                    try Task.checkCancellation()
                    let observation = try await VisionOrModelService().analyze(frame)
                    guard currentToken == token else { break }
                    await publish(observation, frame: frame)
                } catch is CancellationError {
                    break
                } catch {
                    await publishFailure(error)
                }
            }
            processing = false
        }

        private func publish(
            _ observation: Observation,
            frame: FrameSnapshot
        ) async {
            // Send a value and its source metadata to the MainActor model.
        }

        private func publishFailure(_ error: Error) async {
            // Convert to a user-visible, recoverable state.
        }
    }

    struct FrameSnapshot: Sendable {
        let sampleBuffer: CMSampleBuffer
        let presentationTime: CMTime
        let videoOrientation: CGFloat
    }

The sample shows the lifecycle shape, but CMSampleBuffer is a framework reference whose sendability and lifetime need to be resolved in the selected SDK. A production implementation may convert to a pixel buffer or another bounded value at the delegate boundary instead of retaining the sample buffer. Do not construct a new model service for every frame; inject one with an explicit lifecycle and measure memory.

Set the delegate queue once, keep the callback fast, and record dropped frames:

    let frameQueue = DispatchQueue(label: "camera.frames")
    videoOutput.setSampleBufferDelegate(
        frameDelegate,
        queue: frameQueue
    )
    videoOutput.alwaysDiscardsLateVideoFrames = true

If the product cannot discard late frames, use a bounded writer/reader design and document how backpressure changes capture fidelity.

## Recipe 3: Audio-session activation and route changes

Configure category, mode, and options for the real behavior. Activate only when recording or playback begins. Observe interruptions and route changes and re-read the current route after each event.

    import AVFAudio

    actor AudioSessionCoordinator {
        private let session = AVAudioSession.sharedInstance()
        private var isActive = false

        func prepareForRecording() throws {
            try session.setCategory(
                .record,
                mode: .measurement,
                options: []
            )
        }

        func activate() throws {
            try session.setActive(true)
            isActive = true
        }

        func deactivate() throws {
            guard isActive else { return }
            try session.setActive(
                false,
                options: [.notifyOthersOnDeactivation]
            )
            isActive = false
        }

        func currentRouteDescription() -> String {
            let inputs = session.currentRoute.inputs.map(\.portName)
            let outputs = session.currentRoute.outputs.map(\.portName)
            return "in: \(inputs.joined(separator: ", ")); out: \(outputs.joined(separator: ", "))"
        }
    }

    final class AudioNotificationBridge {
        private var observationTokens: [NSObjectProtocol] = []

        func start(
            onInterruption: @escaping @Sendable (Notification) -> Void,
            onRouteChange: @escaping @Sendable (Notification) -> Void
        ) {
            let center = NotificationCenter.default
            observationTokens.append(
                center.addObserver(
                    forName: AVAudioSession.interruptionNotification,
                    object: AVAudioSession.sharedInstance(),
                    queue: nil,
                    using: onInterruption
                )
            )
            observationTokens.append(
                center.addObserver(
                    forName: AVAudioSession.routeChangeNotification,
                    object: AVAudioSession.sharedInstance(),
                    queue: nil,
                    using: onRouteChange
                )
            )
        }

        func stop() {
            let center = NotificationCenter.default
            observationTokens.forEach(center.removeObserver)
            observationTokens.removeAll()
        }
    }

The category and mode are examples, not universal choices. Voice recording, play-and-record, spoken audio, movie playback, Bluetooth, and measurement have different requirements. Check the selected AVAudioSession documentation and test the actual route.

## Recipe 4: Sendable audio tap and bounded handoff

The current AVFAudio documentation exposes installAudioTap with a sendable callback and a read-only audio buffer. The API is marked beta in the documentation snapshot, so resolve availability in the target SDK before adopting it. If the target does not expose it, use the documented installTap bridge and keep the callback isolated.

    actor AudioBufferSink {
        private var stream: AsyncStream<AudioChunk>
        private var continuation: AsyncStream<AudioChunk>.Continuation

        init() {
            let result = AsyncStream.makeStream(
                of: AudioChunk.self,
                bufferingPolicy: .bufferingNewest(8)
            )
            stream = result.stream
            continuation = result.continuation
        }

        func values() -> AsyncStream<AudioChunk> {
            stream
        }

        func append(
            _ buffer: AVReadOnlyAudioPCMBuffer,
            time: AVAudioTime
        ) {
            let chunk = AudioChunk(
                frameLength: buffer.frameLength,
                sampleRate: buffer.format.sampleRate,
                hostTime: time.hostTime
            )
            continuation.yield(chunk)
        }

        func finish() {
            continuation.finish()
        }
    }

    struct AudioChunk: Sendable {
        let frameLength: Int
        let sampleRate: Double
        let hostTime: UInt64
    }

    final class AudioCaptureGraph {
        private let engine = AVAudioEngine()

        func installTap(sink: AudioBufferSink) throws {
            let input = engine.inputNode
            let format = input.outputFormat(forBus: 0)

            try input.installAudioTap(
                onBus: 0,
                bufferSize: 2_048,
                format: format
            ) { buffer, time in
                Task {
                    await sink.append(buffer, time: time)
                }
            }
        }

        func start() throws {
            try engine.start()
        }

        func stop() {
            engine.stop()
            engine.inputNode.removeTap(onBus: 0)
        }
    }

The example carries only bounded metadata to the stream. If SpeechAnalyzer or a recorder needs actual samples, use the documented audio-buffer representation and define a bounded ownership/copy policy. Do not use an unbounded AsyncStream for microphone data. Finish it when the graph stops or the owner is cancelled.

## Recipe 5: Write a finalized audio file

AVAudioFile reads and writes through PCM buffers. The file URL can be overwritten by the writing initializer, so choose a unique temporary URL or make replacement explicit.

    func makeAudioFile(at url: URL, format: AVAudioFormat) throws -> AVAudioFile {
        try AVAudioFile(
            forWriting: url,
            settings: format.settings
        )
    }

    func append(
        _ buffer: AVAudioPCMBuffer,
        to file: AVAudioFile
    ) throws {
        try file.write(from: buffer)
    }

    func finish(file: AVAudioFile) {
        file.close()
    }

Before handing the URL to playback, SpeechAnalyzer, or ShareLink, close the file and verify the source is still present. If the product writes a compressed format, check the file’s settings and target compatibility rather than assuming the extension determines a valid codec.

## Recipe 6: SwiftUI player state

Create the player in task-owned lifecycle work rather than repeatedly in body. Keep player state separate from the view’s layout.

    import AVKit
    import SwiftUI

    struct ReviewPlayer: View {
        let url: URL
        @State private var player: AVPlayer?
        @State private var isPlaying = false

        var body: some View {
            VStack {
                if let player {
                    VideoPlayer(player: player)
                        .aspectRatio(contentMode: .fit)

                    Button(
                        isPlaying ? "Pause" : "Play",
                        systemImage: isPlaying ? "pause.fill" : "play.fill"
                    ) {
                        if isPlaying {
                            player.pause()
                        } else {
                            player.play()
                        }
                        isPlaying.toggle()
                    }
                    .labelStyle(.titleAndIcon)
                } else {
                    ProgressView("Preparing media")
                }
            }
            .task(id: url) {
                let nextPlayer = AVPlayer(url: url)
                player = nextPlayer
                isPlaying = false
            }
            .onDisappear {
                player?.pause()
            }
        }
    }

For richer native playback, bridge AVPlayerViewController or use its documented system presentation path. Track readiness, failure, buffering, end, captions, route, and PiP/background configuration separately. The snippet’s play/pause state is only a local UI projection; it is not a complete player state machine.

## Recipe 7: Async asset load and export

Use AVFoundation’s asynchronous asset properties and export method in an async service. The source asset, output type, and preset must be compatible. A successful export is the only point at which the output URL becomes a finalized handoff.

    enum ExportError: Error {
        case noExportSession
        case incompatible
        case cancelled
    }

    struct MediaExporter {
        func export(
            sourceURL: URL,
            destinationURL: URL,
            preset: String = AVAssetExportPresetHighestQuality,
            fileType: AVFileType = .mov
        ) async throws -> URL {
            let asset = AVURLAsset(url: sourceURL)

            guard await AVAssetExportSession.compatibility(
                ofExportPreset: preset,
                with: asset,
                outputFileType: fileType
            ) else {
                throw ExportError.incompatible
            }

            guard let session = AVAssetExportSession(
                asset: asset,
                presetName: preset
            ) else {
                throw ExportError.noExportSession
            }

            session.outputFileType = fileType
            session.outputURL = destinationURL

            do {
                try await session.export(
                    to: destinationURL,
                    as: fileType
                )
            } catch is CancellationError {
                try? FileManager.default.removeItem(at: destinationURL)
                throw ExportError.cancelled
            } catch {
                try? FileManager.default.removeItem(at: destinationURL)
                throw error
            }

            return destinationURL
        }
    }

The current SDK offers more than one export shape, and some configurations are version-sensitive. Do not set the output URL twice unless the selected signature requires it. Resolve the exact initializer/export method and output-type compatibility in Xcode. For progress, consume the export session’s documented state AsyncSequence and expose cancellation to the review model.

## Recipe 8: Reviewable speech or OCR

Keep deterministic source observations separate from optional generated organization.

    struct MediaProposal: Identifiable, Sendable {
        let id: UUID
        let sourceID: UUID
        let range: CMTimeRange?
        let text: String
        let status: ProposalStatus
        let modelRevision: String?
    }

    enum ProposalStatus: Sendable {
        case provisional
        case final
        case edited
        case rejected
        case accepted
    }

    actor ReviewModel {
        private var proposals: [UUID: MediaProposal] = [:]
        private var sessionToken = UUID()

        func begin(sourceID: UUID) -> UUID {
            sessionToken = UUID()
            proposals.removeAll()
            return sessionToken
        }

        func accept(
            proposalID: UUID,
            token: UUID
        ) throws -> MediaProposal {
            guard token == sessionToken else {
                throw ReviewError.staleProposal
            }
            guard let proposal = proposals[proposalID] else {
                throw ReviewError.missingProposal
            }
            let accepted = MediaProposal(
                id: proposal.id,
                sourceID: proposal.sourceID,
                range: proposal.range,
                text: proposal.text,
                status: .accepted,
                modelRevision: proposal.modelRevision
            )
            proposals[proposalID] = accepted
            return accepted
        }
    }

    enum ReviewError: Error {
        case staleProposal
        case missingProposal
    }

Feed SpeechAnalyzer, Vision, or Core ML results into the review model with source metadata and provisional/final state. Do not allow an analyzer callback to write SwiftData, trigger an App Intent, or share a file directly. The review action is the domain boundary.

## Recipe 9: Share only a finalized artifact

Use Transferable or ShareLink after the source/export state is complete. Keep a user-facing file name and content type derived from the actual output.

    struct ExportedMedia: Transferable {
        let fileURL: URL

        static var transferRepresentation: some TransferRepresentation {
            FileRepresentation(
                contentType: .movie
            ) { media in
                SentTransferredFile(media.fileURL)
            } importing: { received in
                let destination = URL.documentsDirectory
                    .appending(path: received.file.lastPathComponent)
                try FileManager.default.copyItem(
                    at: received.file,
                    to: destination
                )
                return ExportedMedia(fileURL: destination)
            }
        }
    }

    struct ShareMediaButton: View {
        let exported: ExportedMedia

        var body: some View {
            ShareLink(
                item: exported,
                subject: Text("Exported media"),
                message: Text("A finalized copy of your media.")
            ) {
                Label("Share", systemImage: "square.and.arrow.up")
            }
        }
    }

Select the actual UTType for audio, image, or movie output. The source must remain available for the duration of the transfer. A ShareLink can present a system handoff, but it does not prove the recipient accepted, saved, or published the file.

## Recipe 10: Test the route without hardware

Test the adapter-independent state machine with fixtures:

    struct MediaFixture: Sendable {
        let sourceID: UUID
        let hasCameraPermission: Bool
        let hasMicrophonePermission: Bool
        let sourceFinalized: Bool
        let analysisState: AnalysisState
    }

    enum AnalysisState: Sendable {
        case unavailable
        case provisional
        case final
    }

    @Test("A proposal cannot be accepted after a new capture starts")
    func staleProposalIsRejected() async throws {
        let review = ReviewModel()
        let firstToken = await review.begin(sourceID: UUID())
        _ = await review.begin(sourceID: UUID())

        // Insert a fixture proposal using the model's test seam.
        await #expect(throws: ReviewError.staleProposal) {
            try await review.accept(
                proposalID: UUID(),
                token: firstToken
            )
        }
    }

Keep hardware tests separate from state tests. Use a signed physical device for actual camera, microphone, route, orientation, frame-drop, codec, audio, and thermal behavior. Use previews and simulator tests for layout, navigation, accessibility labels, Dynamic Type, reduced effects, and error copy.

## Compile and evidence checklist

- Replace every placeholder with the target’s real source, destination, model, and content type.
- Confirm all APIs are available for the deployment target and not only the installed SDK.
- Resolve Swift 6.2 isolation and sendability diagnostics; do not add unchecked sendability as a shortcut.
- Add camera, microphone, speech, photo-library, or file usage descriptions only for the routes the target needs.
- Use task cancellation and explicit cleanup for capture, analysis, and export.
- Test no permission, interruption, route change, storage failure, model unavailable, and user cancellation.
- Verify the final media file before ShareLink or a system surface.
- Run accessibility tasks and reduced-effects variants.
- Record physical-device results separately from preview, simulator, archive, and release evidence.

## Sources

- [AVCam: Building a camera app](https://developer.apple.com/documentation/avfoundation/avcam-building-a-camera-app)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCaptureDevice](https://developer.apple.com/documentation/avfoundation/avcapturedevice)
- [AVCapturePhotoOutput](https://developer.apple.com/documentation/avfoundation/avcapturephotooutput)
- [AVCaptureMovieFileOutput](https://developer.apple.com/documentation/avfoundation/avcapturemoviefileoutput)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [Receiving captured video data](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput/samplebufferdelegate)
- [Dropping late video frames](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput/alwaysdiscardslatevideoframes)
- [AVFAudio](https://developer.apple.com/documentation/avfaudio)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioNode](https://developer.apple.com/documentation/avfaudio/avaudionode)
- [installAudioTap](https://developer.apple.com/documentation/avfaudio/avaudionode/installaudiotap%28onbus%3Abuffersize%3Aformat%3Atapprovider%3A%29)
- [AVAudioFile](https://developer.apple.com/documentation/avfaudio/avaudiofile)
- [AVAudioPCMBuffer](https://developer.apple.com/documentation/avfaudio/avaudiopcmbuffer)
- [AVAsset](https://developer.apple.com/documentation/avfoundation/avasset)
- [Loading media data asynchronously](https://developer.apple.com/documentation/avfoundation/loading-media-data-asynchronously)
- [AVAssetExportSession](https://developer.apple.com/documentation/avfoundation/avassetexportsession)
- [Exporting video to alternative formats](https://developer.apple.com/documentation/avfoundation/exporting-video-to-alternative-formats)
- [AVPlayer](https://developer.apple.com/documentation/avfoundation/avplayer)
- [AVKit](https://developer.apple.com/documentation/avkit)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [AVPlayerViewController](https://developer.apple.com/documentation/avkit/avplayerviewcontroller)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
