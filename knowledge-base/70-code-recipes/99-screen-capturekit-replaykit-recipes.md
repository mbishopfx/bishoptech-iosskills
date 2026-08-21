# ScreenCaptureKit and ReplayKit route recipes

These are reusable route sketches, not compile proof. Confirm the exact SDK, deployment target, API availability, beta/deprecation status, privacy strings, entitlements, background modes, target membership, and physical-device behavior in a named Xcode target before shipping.

## 1. Keep capability selection target-aware

Do not let a framework import decide the user experience. Inject a probe that records the named target and selected SDK:

```swift
struct ScreenCaptureCapability: Sendable {
    enum Route: Sendable { case screenCaptureKit, replayKitCompatibility, screenshot, importOnly, unavailable }

    let route: Route
    let reason: String
    let deploymentTarget: String
    let sdkVersion: String
    let warning: String?
}

protocol ScreenCaptureAvailabilityProbing: Sendable {
    func evaluate() async -> ScreenCaptureCapability
}
```

The probe must be backed by compile and runtime evidence. Keep the current Apple iOS sample’s iOS 27 minimum as a recorded warning when the product target is iOS 26; do not hardcode a success or failure from the sample alone.

## 2. Model the stream as an actor-owned state machine

The coordinator owns the stream and its output lifetimes. The UI observes a projection:

```swift
enum CaptureState: Equatable, Sendable {
    case unavailable(String)
    case ready
    case requestingConsent
    case pickerPresented
    case preparing(source: String)
    case running(source: String, elapsed: Duration)
    case inactive(reason: String)
    case finalizing
    case reviewable(artifactID: UUID)
    case failed(message: String)
}

actor ScreenCaptureCoordinator {
    private(set) var state: CaptureState = .ready

    // Route sketch: hold SCStream, picker observer, output sinks,
    // recording output, and bounded consumers here.
}
```

Every state transition should be triggered by a source event: target probe, picker selection/cancellation, stream delegate event, output status, user stop, recording delegate completion, or downstream handoff. A button tap is an intent, not proof that the state changed.

## 3. Register the system picker observer before presentation

The exact observer method signature must be confirmed in the selected SDK. The ownership order is the important part:

```swift
final class PickerBridge: NSObject {
    private let picker = SCContentSharingPicker.shared
    private var observer: AnyObject?

    func present(for mode: CaptureMode) {
        // Route sketch:
        // 1. Build SCContentSharingPickerConfiguration for mode.
        // 2. Register SCContentSharingPickerObserver.
        // 3. Set the shared picker configuration.
        // 4. Update app state to pickerPresented.
        // 5. Call picker.present() or the target-supported mode-specific method.
    }

    func cancel() {
        // Remove the observer and return to a cancelled/ready state.
    }
}
```

Do not create a custom window/display list as a substitute for `SCContentSharingPicker`. Keep picker configuration and the returned filter in the coordinator, not in a SwiftUI view value.

## 4. Create a bounded ScreenCaptureKit stream

This route sketch follows Apple’s object graph but intentionally leaves exact availability and configuration properties to the target SDK:

```swift
final class StreamOutputBridge: NSObject, SCStreamOutput {
    private let sink: BoundedCaptureSink

    init(sink: BoundedCaptureSink) { self.sink = sink }

    func stream(
        _ stream: SCStream,
        didOutputSampleBuffer sampleBuffer: CMSampleBuffer,
        of type: SCStreamOutputType
    ) {
        let projection = CaptureSampleProjection.make(
            sampleBuffer: sampleBuffer,
            outputType: type
        )

        // The sink either accepts a bounded owned projection or records a
        // declared drop. Never start an unbounded Task per sample buffer.
        sink.offer(projection)
    }
}

struct ScreenCaptureStreamFactory {
    func make(
        filter: SCContentFilter,
        configuration: SCStreamConfiguration,
        output: SCStreamOutput,
        delegate: SCStreamDelegate,
        queue: DispatchQueue
    ) throws -> SCStream {
        let stream = SCStream(filter: filter, configuration: configuration, delegate: delegate)
        try stream.addStreamOutput(output, type: .screen, sampleHandlerQueue: queue)
        // Add audio/microphone outputs only when the returned consent/configuration allows it.
        return stream
    }
}
```

The `CaptureSampleProjection` must copy or retain only the representation its next stage owns. Use Core Media timing and ScreenCaptureKit frame attachments after validating them; preserve source revision and output lane.

## 5. Project a frame with status and source time

```swift
struct CaptureSampleProjection: Sendable {
    enum Lane: Sendable { case screen, audio, microphone, other }

    let captureRevision: UUID
    let lane: Lane
    let mediaTime: CMTime
    let status: SCFrameStatus?
    let payload: OwnedCapturePayload

    static func make(
        sampleBuffer: CMSampleBuffer,
        outputType: SCStreamOutputType
    ) -> CaptureSampleProjection {
        // Route sketch only. Inspect CMSampleBuffer timing/attachments,
        // map SCStreamOutputType, validate the payload, and create an owned
        // image/audio representation before returning from the callback.
        fatalError("Confirm the selected SDK and ownership strategy in a named target")
    }
}
```

`SCFrameStatus.idle` should not create duplicate model work. `blank`, `suspended`, and `stopped` require an explicit product policy. A malformed or missing attachment should become a diagnostic/drop, not a force-unwrapped frame.

## 6. Use a declared bounded sink

```swift
struct BoundedCaptureSink: Sendable {
    enum Policy: Sendable { case latestFrame, boundedWindow(Int), rejectWhenFull }

    let policy: Policy

    func offer(_ sample: CaptureSampleProjection) {
        // Route sketch: enqueue under the selected policy and increment
        // accepted/dropped counters. Keep queue depth and latency observable.
    }
}
```

Use `latestFrame` for a current-screen classifier, a bounded window for a rolling clip, and `rejectWhenFull` only when the caller can surface backpressure. The queue policy is part of the product contract and must appear in the proof record.

## 7. Attach direct recording output only after the artifact policy exists

```swift
struct RecordingPlan: Sendable {
    let temporaryURL: URL
    let outputFileType: AVFileType
    let videoCodecType: AVVideoCodecType
}

final class RecordingDelegateBridge: NSObject, SCRecordingOutputDelegate {
    func recordingOutputDidStartRecording(_ recordingOutput: SCRecordingOutput) {
        // State: recordingStarted. Do not claim finalized media.
    }

    func recordingOutputDidFinishRecording(_ recordingOutput: SCRecordingOutput) {
        // Validate URL, duration, size, readability, and metadata before
        // creating a reviewable artifact.
    }

    func recordingOutput(_ recordingOutput: SCRecordingOutput, didFailWithError error: Error) {
        // Preserve diagnostics and offer retry/delete recovery.
    }
}
```

The exact initializer and configuration properties are target-sensitive. The route must prove that the output file type and codec are available before the stream starts, and it must wait for the recording delegate’s finish event before Photos, ShareLink, or AI handoff.

## 8. Keep the ReplayKit adapter quarantined

ReplayKit is a compatibility adapter only when the selected target proves that the needed API remains usable:

```swift
final class ReplayKitCompatibilityAdapter {
    private let recorder = RPScreenRecorder.shared()

    func availability() -> Bool {
        // The symbol and property are deprecated in current Apple docs.
        // Record the compiler warning and target/device result.
        recorder.isAvailable
    }

    func startAppScopedCapture() {
        // Route sketch: call the target-supported compatibility method,
        // map callbacks into CaptureState, and preserve ReplayKit limits.
        // Never assume this records AVPlayer content or supports a new
        // broadcast-extension architecture.
    }
}
```

Do not use `RPBroadcastSampleHandler` as a new-product default: Apple’s current reference marks it deprecated and no longer supported. Keep historical extension code isolated so the main app can use a current route or an explicit fallback.

## 9. One-shot screenshot route

```swift
struct ScreenshotReviewRoute {
    func capture(
        filter: SCContentFilter,
        configuration: SCScreenshotConfiguration
    ) async throws -> ScreenshotObservation {
        // Route sketch: use the target-supported SCScreenshotManager API,
        // validate the returned image/sample buffer, attach source revision,
        // then pass only the owned representation to Vision/Core ML.
        fatalError("Confirm async or completion-handler signature in the target SDK")
    }
}
```

Use this route when a stream would be wasteful. It still needs source consent, target availability, privacy review, and a source-timestamp record.

## 10. Source-linked local AI proposal

```swift
struct CaptureAIProposal: Codable, Sendable {
    let artifactID: UUID
    let captureRevision: UUID
    let sourceStart: CMTime
    let sourceEnd: CMTime?
    let modelIdentifier: String
    let modelVersion: String
    let confidence: Double?
    let summary: String
    let requiresReview: Bool
}

actor CaptureAIReviewCoordinator {
    func propose(from sample: CaptureSampleProjection) async throws -> CaptureAIProposal {
        // Route sketch: perform local Vision/Core ML/Speech/Foundation Models
        // work with cancellation, memory, and availability checks. Never
        // commit a side effect from this method.
        fatalError("Inject a concrete model route after target/device proof")
    }
}
```

The proposal must be rejected as stale if its capture revision no longer matches the reviewable artifact. Approval should be a separate typed command with idempotency and authorization checks.

## 11. SwiftUI state shell

```swift
struct CaptureStatusView: View {
    let state: CaptureState

    var body: some View {
        VStack {
            // Route sketch: use semantic SwiftUI controls, grouped glass
            // surfaces, Dynamic Type-safe labels, and an always-reachable
            // stop action when state is running.
            Text(statusLabel)
            Button("Stop capture") {
                // Send intent to the coordinator; do not mutate visual state
                // optimistically before the stream confirms the transition.
            }
            .disabled(!canStop)
        }
        // Apply the target-supported Liquid Glass composition in the named
        // SwiftUI target. Keep source, microphone, and analysis state visible.
    }

    private var statusLabel: String { "Capture status" }
    private var canStop: Bool { true }
}
```

The UI should distinguish unsupported, picker-cancelled, running, finalizing, reviewable, saved, shared, and analyzed. Use the [screen-capture trust and review design](../21-design-deep-dives/84-screen-capture-trust-and-review-design.md) for the visual state map.

## 12. Deterministic tests before hardware

```swift
struct CaptureFixture {
    let frameStatus: SCFrameStatus
    let mediaTime: CMTime
    let lane: CaptureSampleProjection.Lane
    let queueIsFull: Bool
    let sourceRevision: UUID
}

@Test
func idleFramesDoNotCreateDuplicateAnalysisWork() async {
    // Route sketch: feed a fixture through the bounded sink and assert the
    // declared drop/accept counters and source-time policy.
}
```

Add fixtures for picker cancellation, user stop, missing background mode, user decline, `SCStreamError` codes, stale AI proposals, recording-output failure, Photos denial, and accessibility state labels. These tests prove domain behavior, not physical screen capture availability.

## Verification boundary

Before treating a recipe as implemented, prove:

- exact target and SDK availability;
- system picker selection and cancellation;
- physical screen/audio/microphone behavior;
- bounded queue and frame-status policy;
- recording finalization and media inspection;
- AI source/timestamp/review behavior;
- Liquid Glass state transitions and accessibility;
- signed target membership, background modes, entitlements, privacy strings, and Release evidence.

## Sources

- [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit)
- [Capturing screen content on iOS](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-on-ios)
- [SCContentSharingPicker](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpicker)
- [SCContentSharingPickerConfiguration](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpickerconfiguration)
- [SCContentSharingPickerObserver](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpickerobserver)
- [SCContentFilter](https://developer.apple.com/documentation/screencapturekit/sccontentfilter)
- [SCStream](https://developer.apple.com/documentation/screencapturekit/scstream)
- [SCStreamConfiguration](https://developer.apple.com/documentation/screencapturekit/scstreamconfiguration)
- [SCStreamOutput](https://developer.apple.com/documentation/screencapturekit/scstreamoutput)
- [SCFrameStatus](https://developer.apple.com/documentation/screencapturekit/scframestatus)
- [SCStreamError](https://developer.apple.com/documentation/screencapturekit/scstreamerror)
- [SCRecordingOutput](https://developer.apple.com/documentation/screencapturekit/screcordingoutput)
- [SCRecordingOutputConfiguration](https://developer.apple.com/documentation/screencapturekit/screcordingoutputconfiguration)
- [SCScreenshotManager](https://developer.apple.com/documentation/screencapturekit/scscreenshotmanager)
- [ReplayKit](https://developer.apple.com/documentation/replaykit)
- [RPScreenRecorder](https://developer.apple.com/documentation/replaykit/rpscreenrecorder)
- [RPBroadcastSampleHandler](https://developer.apple.com/documentation/replaykit/rpbroadcastsamplehandler)
- [Core Media](https://developer.apple.com/documentation/coremedia)
- [CMSampleBuffer](https://developer.apple.com/documentation/coremedia/cmsamplebuffer)
- [CMTime](https://developer.apple.com/documentation/coremedia/cmtime)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Swift Testing](https://developer.apple.com/documentation/testing)
