# Camera, Media, and Sensor Recipes

These recipes implement the capture portion of the [cross-framework feature lifecycle](../41-framework-deep-dives/06-cross-framework-feature-lifecycle.md). Pair them with the [device and companion capability contracts](../42-framework-deep-dives/08-device-and-companion-capability-contracts.md) for hardware, interruption, teardown, and physical-device evidence.

## Scope and compile boundary

These are compile-oriented route sketches for camera capture, PhotosUI import, video-frame backpressure, Core Motion, and Core Haptics. They keep permission, hardware availability, capture/session ownership, analysis, review, persistence, and teardown visible. They are not compiled in this documentation-only workspace and do not prove camera quality, sensor accuracy, haptic fidelity, audio routes, real-time latency, thermal behavior, or physical-device support.

Use the least-privilege source that satisfies the outcome. A person-selected photo does not require a live camera session; a camera preview does not prove saving or frame analysis; a motion sample does not prove an interpretation; and haptic feedback is an optional channel that needs a visible or audible equivalent.

## Recipe 1: request capture permission at the feature boundary

Request camera or microphone access when the person starts the feature, after the UI explains why it is needed. Provide the corresponding usage-description keys before requesting access.

```swift
import AVFoundation

func requestCameraAccessIfNeeded() async -> Bool {
    switch AVCaptureDevice.authorizationStatus(for: .video) {
    case .authorized:
        return true
    case .notDetermined:
        return await AVCaptureDevice.requestAccess(for: .video)
    case .denied, .restricted:
        return false
    @unknown default:
        return false
    }
}

func requestMicrophoneAccessIfNeeded() async -> Bool {
    switch AVCaptureDevice.authorizationStatus(for: .audio) {
    case .authorized:
        return true
    case .notDetermined:
        return await AVCaptureDevice.requestAccess(for: .audio)
    case .denied, .restricted:
        return false
    @unknown default:
        return false
    }
}
```

Add truthful `NSCameraUsageDescription` and `NSMicrophoneUsageDescription` values. If the product only imports photos, use PhotosUI instead of asking for live camera access. If the person denies access, explain the consequence and offer photo import, manual entry, or another meaningful fallback where possible.

## Recipe 2: configure a camera session on a serial queue

`AVCaptureSession.startRunning()` can block, so keep capture configuration and start/stop work off the main queue. Bracket input/output changes with `beginConfiguration()` and `commitConfiguration()`.

```swift
import AVFoundation

final class CameraSessionService {
    let session = AVCaptureSession()
    private let sessionQueue = DispatchQueue(label: "camera.session")
    private let photoOutput = AVCapturePhotoOutput()

    func configureAndStart() {
        sessionQueue.async { [session, photoOutput] in
            guard let camera = AVCaptureDevice.default(
                .builtInWideAngleCamera,
                for: .video,
                position: .back
            ) else {
                return
            }

            do {
                let input = try AVCaptureDeviceInput(device: camera)
                session.beginConfiguration()

                guard session.canAddInput(input), session.canAddOutput(photoOutput) else {
                    session.commitConfiguration()
                    return
                }

                session.sessionPreset = .photo
                session.addInput(input)
                session.addOutput(photoOutput)
                session.commitConfiguration()
                session.startRunning()
            } catch {
                // Publish a user-facing unavailable/error state on the main actor.
            }
        }
    }

    func stop() {
        sessionQueue.async { [session] in
            guard session.isRunning else { return }
            session.stopRunning()
        }
    }
}
```

The `defer` plus explicit `commitConfiguration()` in this sketch is illustrative only; a target implementation should use one clear commit path and return failure states rather than silently returning. Add the microphone input only when the product records audio, verify the actual device/connection, and configure orientation/camera selection from the target UI. Observe session interruption and runtime-error notifications, and stop dependent Vision/Core ML work when the session cannot deliver usable frames.

## Recipe 3: import a photo without broad library access

Use `PhotosPicker` for user-selected media. The selected item is a representation placeholder; load the required type asynchronously and retain the selection identity so a late result cannot overwrite a newer selection.

```swift
import PhotosUI
import SwiftUI

struct PhotoImportView: View {
    @State private var selection: PhotosPickerItem?
    @State private var imageData: Data?
    @State private var message = "Choose a source"

    var body: some View {
        VStack(spacing: 16) {
            PhotosPicker(
                "Choose photo",
                selection: $selection,
                matching: .images
            )

            Text(message)
                .foregroundStyle(.secondary)
        }
        .task(id: selection) {
            guard let selection else { return }
            do {
                let data = try await selection.loadTransferable(type: Data.self)
                guard self.selection == selection else { return }
                imageData = data
                message = data == nil ? "No usable representation" : "Source ready for review"
            } catch {
                guard self.selection == selection else { return }
                imageData = nil
                message = "The source could not be loaded"
            }
        }
    }
}
```

For many or large assets, prefer a file representation and copy it into an app-owned directory before processing. Remove temporary copies when no longer needed. An iCloud Photos download can fail without network; keep the original selection and show a retry/manual route rather than treating the failure as an empty photo.

## Recipe 4: use bounded video-frame processing

A live UI usually needs the newest useful frame, not an unbounded backlog. `AVCaptureVideoDataOutput.alwaysDiscardsLateVideoFrames` defaults to dropping late frames; use that policy only when the product can tolerate dropped frames.

```swift
import AVFoundation

final class LatestFrameDelegate: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    private let processingQueue = DispatchQueue(label: "camera.analysis")
    private var isProcessing = false

    func configure(_ output: AVCaptureVideoDataOutput) {
        output.alwaysDiscardsLateVideoFrames = true
        output.setSampleBufferDelegate(self, queue: processingQueue)
    }

    func captureOutput(
        _ output: AVCaptureOutput,
        didOutput sampleBuffer: CMSampleBuffer,
        from connection: AVCaptureConnection
    ) {
        guard !isProcessing else { return }
        isProcessing = true
        defer { isProcessing = false }

        // Convert the current sample buffer, run bounded analysis, and publish
        // only a reviewable/provenanced proposal. Keep this delegate fast.
        analyzeCurrentFrame(sampleBuffer)
    }
}
```

The delegate must not retain every sample buffer or launch an unbounded async task per frame. If the downstream model work is asynchronous, use an actor or bounded handoff with a cancellation/generation token and decide whether the newest frame replaces the pending one. If every frame matters, do not use a latest-frame policy; choose a recording/measurement architecture and prove its storage, timing, and thermal behavior separately.

## Recipe 5: keep capture, analysis, review, and persistence separate

Use a product-owned draft between device output and durable data:

`authorized -> preparing -> capturing -> proposal -> review -> confirmed -> persisted`

```swift
struct CaptureProposal: Sendable {
    let sourceID: String
    let capturedAt: Date
    let orientationDescription: String
    let observation: String
    let frameworkVersion: String
    var isConfirmed = false
}

func confirm(_ proposal: CaptureProposal) -> CaptureProposal {
    var confirmed = proposal
    confirmed.isConfirmed = true
    return confirmed
}
```

A Vision/Core ML result, barcode, OCR string, or sensor threshold is a proposal until the product validates it. Keep source identifiers and derived fields side by side. Require explicit confirmation before saving, opening a URL, changing a setting, sending a message, or making a sensitive record change.

## Recipe 6: sample motion only while the feature needs it

Check availability, set a product-appropriate update interval, choose a queue/handler intentionally, and stop updates when the feature leaves the screen. Add `NSMotionUsageDescription` for APIs that access motion data.

```swift
import CoreMotion

final class MotionService {
    private let manager = CMMotionManager()

    func start(on queue: OperationQueue, receive: @escaping (CMDeviceMotion) -> Void) {
        guard manager.isDeviceMotionAvailable else { return }

        manager.deviceMotionUpdateInterval = 1.0 / 30.0
        manager.startDeviceMotionUpdates(to: queue) { motion, error in
            guard error == nil, let motion else { return }
            receive(motion)
        }
    }

    func stop() {
        manager.stopDeviceMotionUpdates()
    }
}
```

The interval is illustrative. A game, compass, accessibility feature, and occasional orientation hint have different sampling needs. Do not infer a medical or behavioral conclusion from a raw motion stream. Downsample, aggregate, and delete motion samples when the product no longer needs them; measure battery and thermal cost on the target device.

## Recipe 7: provide haptics with hardware and lifecycle fallbacks

Check haptic capability before creating an engine, keep a strong engine reference, set reset/stopped handlers, and continue with visual/audio feedback when haptics are unavailable or interrupted.

```swift
import CoreHaptics

final class HapticFeedback {
    private var engine: CHHapticEngine?

    func prepare() throws {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else {
            return
        }

        let engine = try CHHapticEngine()
        engine.resetHandler = { [weak self] in
            try? self?.engine?.start()
        }
        engine.stoppedHandler = { reason in
            // Publish an unavailable state; this callback is not on the main thread.
            _ = reason
        }
        try engine.start()
        self.engine = engine
    }

    func playTap() throws {
        guard let engine else { return }

        let event = CHHapticEvent(
            eventType: .hapticTransient,
            parameters: [],
            relativeTime: 0
        )
        let pattern = try CHHapticPattern(events: [event], parameters: [])
        let player = try engine.makePlayer(with: pattern)
        try player.start(atTime: CHHapticTimeImmediate)
    }

    func stop() {
        engine?.stop(completionHandler: nil)
        engine = nil
    }
}
```

The haptic engine can stop because of an audio interruption, app suspension, or system error. A transient tap should reinforce visible state, not be the only confirmation. Test devices that do not support haptics, system settings, phone calls, backgrounding, repeated start/stop, and thermal/battery behavior.

## Recipe 8: teardown and permission state contract

For every device-input feature, make the state and owner explicit:

| Transition | Required action |
| --- | --- |
| `idle -> requesting` | Explain purpose and request only the required resource. |
| `requesting -> denied/restricted` | Show consequence, settings route if useful, and a fallback. |
| `authorized -> preparing` | Configure the session/service on its owner queue and verify hardware availability. |
| `preparing -> capturing` | Publish active state and begin bounded output handling. |
| `capturing -> interrupted` | Stop or pause dependent work; inspect the interruption and route before resuming. |
| `capturing -> background` | Apply the product’s background policy; do not assume capture continues. |
| `capturing -> stopped` | Stop outputs/updates, finish or cancel analysis, release buffers, and deactivate audio/haptic engines. |
| `proposal -> confirmed` | Preserve source/provenance and require the product’s review/authorization rule. |

No view disappearance should leave a camera session, motion manager, haptic engine, audio tap, or frame-analysis task running unintentionally. Make cancellation idempotent so repeated lifecycle callbacks do not crash or duplicate cleanup.

## Physical-device verification matrix

| Test | Evidence to capture |
| --- | --- |
| Camera permission | First-use explanation, allow/deny/restricted, Settings change, missing usage description behavior, and manual fallback |
| Camera session | Front/back/external camera where supported, orientation, focus/exposure, start/stop, interruption, runtime error, and background/foreground |
| Photo import | User-selected-only access, iCloud Photos offline/download failure, cancellation, unsupported representation, large asset, and file cleanup |
| Frame analysis | Frame rate, late-frame policy, dropped-frame count, cancellation, slow model work, memory, thermal behavior, and source provenance |
| Motion | Availability, update interval, app lifecycle, permission/usage description, device orientation, noisy data, battery, and stop behavior |
| Haptics | Supported/unsupported hardware, engine reset/stopped handlers, phone call/background interruption, visual/audio fallback, and repeated playback |
| Privacy | Raw media and sensor samples absent from logs/analytics by default, retention/deletion, file protection, export, and network instrumentation |
| Accessibility | Capture state labels, stop/cancel/retry controls, captions/text alternatives, reduced motion, VoiceOver, and non-haptic confirmation |

Previews and simulators can validate state rendering and pure data transforms. They do not prove camera input, sensor values, haptic output, audio routes, frame timing, thermal behavior, or capture quality. Those claims require the target physical device family, OS build, permissions, and a named test run.

## Sources

- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [AVCaptureDevice authorization](https://developer.apple.com/documentation/avfoundation/avcapturedevice/authorizationstatus%28for%3A%29)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCapturePhotoOutput](https://developer.apple.com/documentation/avfoundation/avcapturephotooutput)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [alwaysDiscardsLateVideoFrames](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput/alwaysdiscardslatevideoframes)
- [NSCameraUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nscamerausagedescription)
- [NSMicrophoneUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsmicrophoneusagedescription)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [loadTransferable(type:)](https://developer.apple.com/documentation/photosui/photospickeritem/loadtransferable%28type%3A%29)
- [Bringing Photos picker to your SwiftUI app](https://developer.apple.com/documentation/photokit/bringing-photos-picker-to-your-swiftui-app)
- [Core Motion](https://developer.apple.com/documentation/coremotion)
- [CMMotionManager](https://developer.apple.com/documentation/coremotion/cmmotionmanager)
- [NSMotionUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsmotionusagedescription)
- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [CHHapticEngine](https://developer.apple.com/documentation/corehaptics/chhapticengine)
- [Preparing your app to play haptics](https://developer.apple.com/documentation/corehaptics/preparing-your-app-to-play-haptics)
