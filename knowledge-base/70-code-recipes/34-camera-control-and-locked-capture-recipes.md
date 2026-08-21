# Camera Control and locked capture recipes

These are route sketches for iOS 26 camera entry points. They are not compiled in this documentation workspace. Create the correct application, WidgetKit control, and Locked Camera Capture Extension targets first. Resolve availability, target membership, and exact signatures in the selected Xcode SDK.

The locked extension is not an ordinary app scene. It has a restricted process and data lifecycle. Keep capture-first code in the extension and move review, network, account, durable persistence, and optional AI work into the containing app.

## Recipe 1: Locked Camera Capture extension scene

The system provides a LockedCameraCaptureSession to the scene. The extension must present an active camera view quickly.

    import LockedCameraCapture
    import SwiftUI

    @main
    struct QuickCaptureExtension: LockedCameraCaptureExtension {
        var body: some LockedCameraCaptureExtensionScene {
            LockedCameraCaptureUIScene { session in
                LockedCaptureView(session: session)
            }
        }
    }

    struct LockedCaptureView: View {
        let session: LockedCameraCaptureSession
        @State private var isCapturing = false
        @State private var status = "Ready to capture"

        var body: some View {
            ZStack(alignment: .bottom) {
                LockedCameraPreview(session: session)
                    .ignoresSafeArea()

                VStack(spacing: 12) {
                    Text(status)
                        .font(.headline)
                        .accessibilityAddTraits(.isHeader)

                    Button(
                        isCapturing ? "Stop recording" : "Take photo",
                        systemImage: isCapturing ? "stop.circle.fill" : "circle"
                    ) {
                        isCapturing.toggle()
                        status = isCapturing ? "Recording" : "Captured temporarily"
                    }
                    .labelStyle(.titleAndIcon)
                    .buttonStyle(.borderedProminent)
                }
                .padding()
            }
            .onCameraCaptureEvent(
                isEnabled: true,
                defaultSoundDisabled: false
            ) { event in
                guard event.phase == .ended else { return }
                // Route the same capture action used by the visible button.
            }
        }
    }

The preview and capture implementation are intentionally placeholders. Replace them with a real AVCaptureSession or the documented picker route. The critical boundaries are the system-created session, active camera view, physical capture event, temporary content, and a real stop/finalize state. Do not claim that changing a local Boolean captured media.

## Recipe 2: Save finalized content to sessionContentURL

Use the session’s temporary directory for content that must survive the extension process until the containing app imports it. Use a unique child path and close the writer before reporting completion.

    struct LockedContentWriter {
        let session: LockedCameraCaptureSession

        func destination(
            named name: String,
            fileExtension: String
        ) -> URL {
            session.sessionContentURL
                .appending(path: "\(name).\(fileExtension)")
        }

        func copyFinalizedFile(
            from sourceURL: URL,
            named name: String,
            fileExtension: String
        ) throws -> URL {
            let destination = destination(
                named: name,
                fileExtension: fileExtension
            )
            try FileManager.default.copyItem(
                at: sourceURL,
                to: destination
            )
            return destination
        }
    }

Do not write to an App Group container from the locked capture extension. Do not treat the temporary directory as the permanent database. If the extension needs to store a manifest, keep it small, versioned, and alongside the finalized media.

## Recipe 3: Capture event handling in SwiftUI

Use onCameraCaptureEvent for a SwiftUI camera surface. The event API is for media capture and events are conditional on the system state and active camera use.

    struct HardwareCaptureSurface: View {
        let camera: CameraCaptureModel

        var body: some View {
            CameraPreview(camera: camera)
                .onCameraCaptureEvent(
                    isEnabled: camera.canHandleHardwareCapture,
                    defaultSoundDisabled: false,
                    primaryAction: { event in
                        camera.handle(primary: event)
                    },
                    secondaryAction: { event in
                        camera.handle(secondary: event)
                    }
                )
        }
    }

    @MainActor
    final class CameraCaptureModel: ObservableObject {
        @Published private(set) var canHandleHardwareCapture = false

        func handle(primary event: AVCaptureEvent) {
            switch event.phase {
            case .began:
                beginCapture()
            case .ended:
                finishCapture()
            case .cancelled:
                cancelCapture()
            default:
                break
            }
        }

        func handle(secondary event: AVCaptureEvent) {
            guard event.phase == .ended else { return }
            switchCaptureMode()
        }

        private func beginCapture() {}
        private func finishCapture() {}
        private func cancelCapture() {}
        private func switchCaptureMode() {}
    }

The exact event phase cases and overload names must be checked in the selected SDK. If the camera is not active or the model cannot respond, set isEnabled to false. A disabled interaction is a correctness and accessibility state, not merely a visual choice.

## Recipe 4: UIKit AVCaptureEventInteraction bridge

Use AVCaptureEventInteraction when the camera surface is a UIKit view controller or a representable that needs an explicit interaction object.

    final class CameraViewController: UIViewController {
        private let camera = CameraCaptureModel()
        private var eventInteraction: AVCaptureEventInteraction?

        override func viewDidLoad() {
            super.viewDidLoad()

            let interaction = AVCaptureEventInteraction { [weak self] event in
                guard let self else { return }
                guard event.phase == .ended else { return }
                self.camera.finishCapture()
            }

            view.addInteraction(interaction)
            eventInteraction = interaction
        }

        func setHardwareCaptureEnabled(_ enabled: Bool) {
            eventInteraction?.isEnabled = enabled
        }
    }

The interaction overrides default hardware-button behavior while enabled. Always handle the event or disable the interaction. Backgrounded apps and apps not actively using the camera should not expect event delivery.

## Recipe 5: Configure Camera Control sliders and pickers

The capture session owns system and custom controls. Check support, capacity, and canAddControl before adding anything. Provide a controls delegate so the system can activate and present the controls.

    import AVFoundation

    final class CameraControlsDelegate: NSObject, AVCaptureSessionControlsDelegate {
        var onFullscreenChange: (@MainActor (Bool) -> Void)?

        func sessionControlsDidBecomeActive(_ session: AVCaptureSession) {
            Task { @MainActor in
                onFullscreenChange?(true)
            }
        }

        func sessionControlsWillEnterFullscreenAppearance(
            _ session: AVCaptureSession
        ) {
            Task { @MainActor in
                onFullscreenChange?(true)
            }
        }

        func sessionControlsWillExitFullscreenAppearance(
            _ session: AVCaptureSession
        ) {
            Task { @MainActor in
                onFullscreenChange?(false)
            }
        }

        func sessionControlsDidBecomeInactive(
            _ session: AVCaptureSession
        ) {
            Task { @MainActor in
                onFullscreenChange?(false)
            }
        }
    }

    func configureCameraControls(
        session: AVCaptureSession,
        device: AVCaptureDevice,
        delegate: CameraControlsDelegate,
        controlQueue: DispatchQueue
    ) {
        guard session.supportsControls else { return }

        let zoom = AVCaptureSystemZoomSlider(device: device)
        let exposure = AVCaptureSystemExposureBiasSlider(device: device)
        let filterPicker = AVCaptureIndexPicker(
            "Filters",
            symbolName: "camera.filters",
            localizedIndexTitles: ["Natural", "Warm", "Mono"]
        )

        session.beginConfiguration()
        defer { session.commitConfiguration() }

        for control in session.controls {
            session.removeControl(control)
        }

        for control in [zoom, exposure, filterPicker] {
            guard session.canAddControl(control) else { continue }
            session.addControl(control)
        }

        session.setControlsDelegate(
            delegate,
            queue: controlQueue
        )
    }

The system zoom and system exposure sliders derive their ranges from the active device format. Rebuild or update the controls when the active format changes. For a custom AVCaptureSlider, set localizedValueFormat and prominentValues where appropriate. Use SF Symbols and short localized titles.

## Recipe 6: Bounded custom slider action

Use a custom slider only for a value that is meaningful at capture time. Send changes to a queue or actor that owns the device configuration; do not mutate a capture device from an arbitrary UI callback.

    let focusSlider = AVCaptureSlider(
        "Focus",
        symbolName: "scope",
        in: 0...1,
        step: 0.05
    )
    focusSlider.localizedValueFormat = "%.2f"
    focusSlider.prominentValues = [0, 0.5, 1]
    focusSlider.setActionQueue(
        DispatchQueue(label: "camera.controls")
    ) { value in
        // Acquire the device configuration lock in the session owner,
        // validate the value, apply it, and unlock.
    }

The exact value-format syntax and control availability are SDK-sensitive. Validate localized output and avoid relying on the symbol to communicate the current state; the value label carries that meaning.

## Recipe 7: CameraCaptureIntent and bounded app context

CameraCaptureIntent can carry small user configuration into the capture extension. Keep the context Codable, Sendable, versionable, and free of secrets or raw media.

    import AppIntents

    enum CameraPosition: String, Codable, Sendable {
        case front
        case rear
    }

    struct CaptureAppContext: Codable, Sendable {
        var version: Int
        var cameraPosition: CameraPosition
        var mode: String
        var filterID: String?
    }

    struct QuickCaptureIntent: CameraCaptureIntent {
        typealias AppContext = CaptureAppContext

        static let title: LocalizedStringResource = "Quick capture"
        static let description = IntentDescription(
            "Open the camera to capture a photo or video."
        )

        @MainActor
        func perform() async throws -> some IntentResult {
            // The system uses this intent to launch the camera activity.
            return .result()
        }
    }

    func updateCameraContext(
        position: CameraPosition,
        mode: String,
        filterID: String?
    ) async throws {
        try await QuickCaptureIntent.updateAppContext(
            CaptureAppContext(
                version: 1,
                cameraPosition: position,
                mode: mode,
                filterID: filterID
            )
        )
    }

    func readCameraContext() async -> CaptureAppContext? {
        try? await QuickCaptureIntent.appContext
    }

The app, control/widget extension, and capture extension must share the intent according to Apple’s target-membership guidance. Validate stale or unsupported context in the extension and choose a safe default.

## Recipe 8: Open the containing app after unlock

Use the session to request an app transition with a user activity. Authentication may be required and the launch can fail.

    func continueInApp(
        session: LockedCameraCaptureSession,
        sourceHint: String?
    ) async {
        do {
            let activity = NSUserActivity(
                activityType: NSUserActivityTypeLockedCameraCapture
            )
            activity.userInfo = [
                "sourceHint": sourceHint as Any
            ]
            try await session.openApplication(for: activity)
        } catch {
            // Render a recoverable handoff failure in the extension.
        }
    }

The containing app must route the activity to a pending-capture review destination. The activity is a handoff hint, not the media itself. The media may arrive through LockedCameraCaptureManager.sessionContentUpdates before or after the app scene becomes visible.

## Recipe 9: Consume session content in the app

Consume the manager’s AsyncSequence in an app-owned task. Import idempotently and invalidate only after durable copy succeeds.

    actor LockedCaptureImporter {
        private let manager = LockedCameraCaptureManager.shared
        private var knownDirectories = Set<URL>()

        func run() async {
            for await update in manager.sessionContentUpdates {
                switch update {
                case .initial(let urls):
                    for url in urls {
                        await importIfNeeded(url)
                    }
                case .added(let url):
                    await importIfNeeded(url)
                case .removed(let url):
                    knownDirectories.remove(url)
                @unknown default:
                    break
                }
            }
        }

        private func importIfNeeded(_ url: URL) async {
            guard !knownDirectories.contains(url) else { return }
            knownDirectories.insert(url)

            do {
                let source = try await copyAndValidate(url)
                try await savePendingCapture(source)
                try await manager.invalidateSessionContent(at: url)
            } catch {
                knownDirectories.remove(url)
                // Keep a pending retry state; do not claim import succeeded.
            }
        }

        private func copyAndValidate(
            _ url: URL
        ) async throws -> ImportedSource {
            // Validate files, media types, size, and finalization.
            fatalError("Replace with app storage implementation")
        }

        private func savePendingCapture(
            _ source: ImportedSource
        ) async throws {
            // Create a durable source and review draft.
        }
    }

    struct ImportedSource: Sendable {
        let sourceID: UUID
        let fileURLs: [URL]
    }

This is an importer sketch. Do not use fatalError in production. The important behavior is idempotency, durable copy before invalidation, and recovery after a process restart. The manager sequence can report removed content, so the app must not interpret every removal as a successful import.

## Recipe 10: Review and AI handoff after import

Keep the extension source and AI proposal separate:

    struct PendingCapture: Identifiable, Sendable {
        let id: UUID
        let sourceURLs: [URL]
        let origin: CaptureOrigin
        var reviewState: ReviewState
    }

    enum CaptureOrigin: Sendable {
        case inApp
        case lockedExtension
        case cameraControl
    }

    enum ReviewState: Sendable {
        case imported
        case analyzing
        case proposalReady
        case accepted
        case rejected
        case exportReady
    }

    @MainActor
    func analyzeAfterImport(
        capture: PendingCapture
    ) async throws -> ReviewProposal {
        let observations = try await VisionOrSpeechService()
            .observe(capture.sourceURLs)
        let proposal = try await OptionalFoundationModelsService()
            .organize(observations)
        return ReviewProposal(
            sourceID: capture.id,
            observations: observations,
            generatedProposal: proposal
        )
    }

The exact model service is product-specific. The route must preserve the source, deterministic observations, generated proposal, and approval action. Do not run the analysis before the extension has produced a finalized source unless the feature has a separately verified live-analysis contract.

## Recipe 11: Capability and fallback test seam

Keep hardware and system state injectable:

    struct CameraEntryCapabilities: Sendable {
        let supportsLockedCapture: Bool
        let supportsControls: Bool
        let canAddControl: Bool
        let cameraAuthorized: Bool
        let extensionContentAvailable: Bool
        let isAuthenticated: Bool
    }

    enum CameraEntryRoute: Sendable {
        case lockedExtension
        case inApp
        case unavailable(reason: String)
    }

    func chooseRoute(
        capabilities: CameraEntryCapabilities
    ) -> CameraEntryRoute {
        guard capabilities.cameraAuthorized else {
            return .unavailable(reason: "Camera permission is required.")
        }
        if capabilities.supportsLockedCapture {
            return .lockedExtension
        }
        return .inApp
    }

Test:

- unsupported device chooses the ordinary app route;
- denied permission never starts the session;
- canAddControl false never calls addControl;
- a stale AppContext uses a safe default;
- a removed session directory does not become a success record;
- importer retry is idempotent;
- extension network work is not required;
- AI unavailability leaves the original media reviewable;
- the app does not publish until the user approves.

## Compile and device checklist

- Add a real Locked Camera Capture Extension target.
- Add a real WidgetKit control target when using Control Center, Lock Screen, or Action button entry.
- Add CameraCaptureIntent to the targets Apple’s guide requires.
- Add camera and microphone usage descriptions only for the capture features used.
- Verify the capture extension’s restricted network and shared-container behavior.
- Compile the Camera Control APIs against the selected iOS 26 SDK.
- Run on supported physical iPhone hardware for lock-screen and Camera Control behavior.
- Test permission, authentication, dismissal, temporary content, import, and invalidation.
- Test touch fallback and accessibility when hardware events are unavailable.
- Inspect the signed archive and TestFlight build separately from local preview and simulator evidence.

## Sources

- [Creating a camera experience for the Lock Screen](https://developer.apple.com/documentation/LockedCameraCapture/Creating-a-camera-experience-for-the-Lock-Screen)
- [LockedCameraCapture](https://developer.apple.com/documentation/LockedCameraCapture)
- [LockedCameraCaptureExtension](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracaptureextension)
- [LockedCameraCaptureUIScene](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracaptureuiscene)
- [LockedCameraCaptureSession](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracapturesession)
- [LockedCameraCaptureManager](https://developer.apple.com/documentation/lockedcameracapture/lockedcameracapturemanager)
- [CameraCaptureIntent](https://developer.apple.com/documentation/appintents/cameracaptureintent)
- [CameraCaptureIntent app context](https://developer.apple.com/documentation/appintents/cameracaptureintent/appcontext-swift.type.property)
- [Enhancing your app experience with the Camera Control](https://developer.apple.com/documentation/avfoundation/enhancing-your-app-experience-with-the-camera-control)
- [AVCaptureEventInteraction](https://developer.apple.com/documentation/avkit/avcaptureeventinteraction)
- [AVCaptureEvent](https://developer.apple.com/documentation/avkit/avcaptureevent)
- [onCameraCaptureEvent](https://developer.apple.com/documentation/swiftui/view/oncameracaptureevent%28isenabled%3Adefaultsounddisabled%3Aaction%3A%29)
- [AVCaptureControl](https://developer.apple.com/documentation/avfoundation/avcapturecontrol)
- [AVCaptureSession controls](https://developer.apple.com/documentation/avfoundation/avcapturesession/controls)
- [Adding a control to a capture session](https://developer.apple.com/documentation/avfoundation/avcapturesession/addcontrol%28_%3A%29)
- [AVCaptureSlider](https://developer.apple.com/documentation/avfoundation/avcaptureslider)
- [AVCaptureIndexPicker](https://developer.apple.com/documentation/avfoundation/avcaptureindexpicker)
- [AVCaptureSystemZoomSlider](https://developer.apple.com/documentation/avfoundation/avcapturesystemzoomslider)
- [AVCaptureSystemExposureBiasSlider](https://developer.apple.com/documentation/avfoundation/avcapturesystemexposurebiasslider)
- [Creating controls to perform actions across the system](https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system)
- [Camera Control](https://developer.apple.com/design/human-interface-guidelines/camera-control)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
