# Screen Capture and Broadcast Recipes

These are compile-oriented route sketches for screen recording, broadcast, camera/microphone capture, finalization, and reviewable on-device analysis. They are not compiled in this documentation-only workspace and do not prove iOS 26 availability, permissions, entitlements, system-pickers, physical-device behavior, extension execution, media integrity, AI quality, or release readiness.

## Recipe 1: Keep capture state separate from the button

Use an app-owned state model so the UI can distinguish a request, a running session, a stop, finalization, and a failure.

~~~swift
enum CaptureState: Equatable {
    case idle
    case requestingPermission
    case selectingSource
    case preparing
    case running(source: String, microphone: Bool, camera: Bool)
    case interrupted(reason: String)
    case finalizing
    case ready(URL)
    case failed(message: String)
}

@MainActor
final class CaptureModel: ObservableObject {
    @Published private(set) var state: CaptureState = .idle

    func start() {
        guard case .idle = state else { return }
        state = .requestingPermission
        // The concrete adapter owns the system permission or picker route.
    }

    func stop() {
        guard case .running = state else { return }
        state = .finalizing
        // Await the adapter's finalized artifact before moving to .ready.
    }
}
~~~

The model is a route sketch. Confirm the selected observation model, actor isolation, and framework callbacks in the target SDK.

## Recipe 2: ReplayKit compatibility adapter

For an iOS 26 compatibility target, investigate the exact RPScreenRecorder surface first. Apple’s current reference marks the legacy recording methods deprecated, so keep this adapter isolated and easy to replace.

~~~swift
import ReplayKit

final class ReplayKitAdapter {
    private let recorder = RPScreenRecorder.shared()

    func canStart() -> Bool {
        recorder.isAvailable
    }

    func start(completion: @escaping (Error?) -> Void) {
        guard recorder.isAvailable else {
            completion(CaptureError.unavailable)
            return
        }
        recorder.startRecording { error in
            completion(error)
        }
    }

    func stop(completion: @escaping (URL?, Error?) -> Void) {
        // Choose the stop API that the selected SDK exposes and verify its
        // finalization semantics before handing a URL to review or sharing.
    }
}
~~~

Do not use the existence of this sketch as proof that a current iOS 26 target should ship the deprecated route. Compile it, inspect warnings, run the permission and interruption matrix, and record the result.

## Recipe 3: Gate a newer ScreenCaptureKit route

Apple’s current iOS ScreenCaptureKit sample requires iOS 27 or later. Keep the newer adapter behind an exact availability and target check, with an iOS 26 fallback.

~~~swift
@MainActor
final class ScreenCaptureKitAdapter {
    func presentPickerOrFallback() {
        // Verify the exact availability in the selected SDK.
        // On supported targets, use SCContentSharingPicker.shared and its
        // observer instead of building a custom source picker.
        // On unsupported targets, route to ReplayKit, AVFoundation, import,
        // or an unavailable state.
    }

    func startStream(from filter: Any) async throws {
        // Build SCStream from the system-returned content filter, attach only
        // the needed screen/audio outputs, and start after the selection.
        // The concrete signatures must be checked in the target SDK.
    }
}
~~~

When the selected target supports the current sample’s route, use the system picker, honor microphone/camera choices, bound sample handling, and await recording-output finalization. Do not claim iOS 26 support from an iOS 27 sample.

## Recipe 4: Bound camera frames before AI

Use AVFoundation when the feature needs camera or microphone input. Drop or coalesce frames deliberately before sending them to Vision or Core ML.

~~~swift
final class CameraFrameSink: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    private let queue = DispatchQueue(label: "capture.frames")
    private var analysisInFlight = false

    func captureOutput(
        _ output: AVCaptureOutput,
        didOutput sampleBuffer: CMSampleBuffer,
        from connection: AVCaptureConnection
    ) {
        guard !analysisInFlight else { return }
        analysisInFlight = true
        let retained = sampleBuffer
        Task {
            defer { analysisInFlight = false }
            // Convert only the bounded sample needed by the analyzer.
            // Check cancellation, model readiness, and source timestamps.
            _ = retained
        }
    }
}

let videoOutput = AVCaptureVideoDataOutput()
videoOutput.alwaysDiscardsLateVideoFrames = true
videoOutput.setSampleBufferDelegate(frameSink, queue: frameQueue)
~~~

This is a latest-acceptable-frame policy, not a universal rule. If every frame matters, use a different architecture and prove storage, timing, memory, and thermal behavior.

## Recipe 5: Finalize before Photos or ShareLink

Treat finalization as a state boundary:

~~~swift
struct MediaArtifact: Sendable {
    let url: URL
    let duration: TimeInterval
    let source: String
    let capturedAt: Date
    let checksum: String?
}

func finishAndReview(
    outputURL: URL,
    source: String
) async throws -> MediaArtifact {
    // Await the capture writer or SCRecordingOutput delegate/callback.
    // Validate that the URL is readable and the container is complete.
    // Read duration and media metadata, then create the artifact record.
    // Only after this returns should the UI enable save, share, or analysis.
    fatalError("Route sketch: implement with the selected media writer")
}
~~~

A URL in a temporary directory is not a finalized movie. PhotoKit changes, ShareLink presentation, and server upload are downstream operations with their own results and failures.

## Recipe 6: Reviewable AI proposal

Keep model output subordinate to source evidence and approval:

~~~swift
struct CaptureProposal: Sendable {
    let artifactID: String
    let sourceRange: ClosedRange<TimeInterval>
    let text: String
    let modelIdentifier: String
    let modelRevision: String?
    let confidence: Double?
    let status: Status

    enum Status: Sendable {
        case draft
        case edited
        case approved
        case rejected
    }
}

func approve(_ proposal: CaptureProposal) throws {
    guard proposal.status == .draft || proposal.status == .edited else {
        throw ProposalError.notReviewable
    }
    // Re-read or validate source identifiers and schema before committing.
    // The deterministic domain use case owns the write and idempotency key.
}
~~~

Do not commit a transcript, label, summary, or action because a model returned text. Require source-range validation, user approval, and an idempotent domain use case.

## Recipe 7: Explicit fallback surface

Render capability state instead of hiding it:

~~~swift
enum CaptureCapability {
    case screenCapture
    case appScopedRecording
    case cameraOrMicrophone
    case importOnly
    case unavailable(String)
}

@ViewBuilder
func captureEntry(for capability: CaptureCapability) -> some View {
    switch capability {
    case .screenCapture:
        Label("Record selected content", systemImage: "rectangle.dashed.badge.record")
    case .appScopedRecording:
        Label("Record this app", systemImage: "record.circle")
    case .cameraOrMicrophone:
        Label("Capture camera or microphone", systemImage: "camera")
    case .importOnly:
        Label("Import a recording", systemImage: "square.and.arrow.down")
    case .unavailable(let reason):
        Label(reason, systemImage: "exclamationmark.triangle")
    }
}
~~~

The icons and wording are illustrative. Use the system symbol and localized copy that fit the actual product and target, and pair the label with a real action or an accessible explanation.

## Compile and proof gates

- Confirm ReplayKit or ScreenCaptureKit availability in the selected SDK.
- Confirm iOS 26 versus newer-OS branching in a real target.
- Add only the camera, microphone, Photos, and background configuration required by the route.
- Compile the adapter and its extension targets separately.
- Test permission denial, cancellation, interruption, finalization, and save/share failure.
- Measure bounded capture and analysis on a signed physical device.
- Test VoiceOver, Dynamic Type, Reduce Motion, Reduce Transparency, Voice Control, Switch Control, keyboard, and pointer where applicable.
- Inspect the archive, entitlements, target membership, privacy metadata, and extension configuration before release.

## Sources

- [ReplayKit](https://developer.apple.com/documentation/replaykit)
- [RPScreenRecorder](https://developer.apple.com/documentation/replaykit/rpscreenrecorder)
- [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit)
- [Capturing screen content on iOS](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-on-ios)
- [SCContentSharingPicker](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpicker)
- [SCStream](https://developer.apple.com/documentation/screencapturekit/scstream)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [AVCam: Building a camera app](https://developer.apple.com/documentation/avfoundation/avcam-building-a-camera-app)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Vision](https://developer.apple.com/documentation/vision)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
