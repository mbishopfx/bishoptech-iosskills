import Foundation
import MWDATCamera
import MWDATCore

public enum MetaWearablesCameraFallback: Sendable {
    case noSession
    case permissionDenied
    case cameraUnavailable
    case captureFailed
    case sessionUnavailable
    case datAppUpdateRequired
}

public enum MetaWearablesCameraFailure: Sendable {
    case session
    case stream
    case permission
}

public enum MetaWearablesCameraEvent: Sendable {
    case sessionStarted
    case streamStarted
    case firstFrameReceived
    case photoReceived
    case streamStopped
    case phoneFallback(MetaWearablesCameraFallback)
    case failure(MetaWearablesCameraFailure)
}

/// A small DAT 0.9 camera/photo adapter.
///
/// Raw frames never cross the event boundary. The optional photo sink is an
/// explicit phone-local handoff; callers must decide whether to decode, retain,
/// delete, or send the bytes and must not treat it as glasses-native processing.
@MainActor
public final class MetaWearablesCameraCoordinator {
    public typealias EventSink = (MetaWearablesCameraEvent) -> Void
    public typealias PhotoSink = (Data) -> Void

    private let wearables: any WearablesInterface
    private let eventSink: EventSink
    private let photoSink: PhotoSink
    private let frameRate: UInt

    private var epoch = 0
    private var session: DeviceSession?
    private var camera: MWDATCamera.Camera?
    private var stream: MWDATCamera.Stream?
    private var sessionTokens: [any AnyListenerToken] = []
    private var streamTokens: [any AnyListenerToken] = []
    private var firstFrameSeen = false

    public init(
        wearables: any WearablesInterface,
        frameRate: UInt = 24,
        eventSink: @escaping EventSink,
        photoSink: @escaping PhotoSink = { _ in }
    ) {
        self.wearables = wearables
        self.frameRate = max(1, frameRate)
        self.eventSink = eventSink
        self.photoSink = photoSink
    }

    /// Create and start a session. Registration and device UI remain target-owned.
    public func connect() {
        guard session == nil else { return }

        do {
            let selector = AutoDeviceSelector(wearables: wearables)
            let nextSession = try wearables.createSession(deviceSelector: selector)
            session = nextSession
            observeSession(nextSession)
            try nextSession.start()
        } catch {
            eventSink(.failure(.session))
            eventSink(.phoneFallback(.sessionUnavailable))
        }
    }

    /// Query camera permission without surprising the user with an app switch.
    public func startCameraIfPermitted() async {
        guard let session else {
            eventSink(.phoneFallback(.noSession))
            return
        }
        guard session.state == .started else {
            eventSink(.phoneFallback(.sessionUnavailable))
            return
        }

        do {
            guard try await wearables.checkPermissionStatus(.camera) == .granted else {
                eventSink(.phoneFallback(.permissionDenied))
                return
            }
            attachCamera(to: session)
        } catch {
            eventSink(.failure(.permission))
            eventSink(.phoneFallback(.permissionDenied))
        }
    }

    /// Use only after an app-owned confirmation of the Meta AI permission redirect.
    public func requestCameraPermissionAndStart() async {
        do {
            guard try await wearables.requestPermission(.camera) == .granted else {
                eventSink(.phoneFallback(.permissionDenied))
                return
            }
            await startCameraIfPermitted()
        } catch {
            eventSink(.failure(.permission))
            eventSink(.phoneFallback(.permissionDenied))
        }
    }

    public func capturePhoto() {
        guard let stream, stream.state == .streaming else {
            eventSink(.phoneFallback(.cameraUnavailable))
            return
        }
        guard stream.capturePhoto(format: .jpeg) else {
            eventSink(.failure(.stream))
            eventSink(.phoneFallback(.captureFailed))
            return
        }
    }

    /// Stop listeners and the camera before stopping the parent session.
    public func stop() async {
        epoch &+= 1
        await stopStreamAndCamera()
        let tokens = sessionTokens
        sessionTokens.removeAll()
        for token in tokens {
            await token.cancel()
        }
        session?.stop()
        session = nil
    }

    private func attachCamera(to session: DeviceSession) {
        guard camera == nil else { return }

        let configuration = StreamConfiguration(
            videoCodec: .hvc1,
            resolution: .low,
            frameRate: frameRate
        )

        do {
            guard let nextCamera = try session.addCamera(config: configuration) else {
                eventSink(.phoneFallback(.cameraUnavailable))
                return
            }
            camera = nextCamera
            stream = nextCamera.stream
            observeStream(nextCamera.stream)
            nextCamera.stream.start()
        } catch {
            eventSink(.failure(.stream))
            eventSink(.phoneFallback(.cameraUnavailable))
        }
    }

    private func observeSession(_ session: DeviceSession) {
        sessionTokens.removeAll()
        sessionTokens.append(
            session.statePublisher.listen { [weak self] state in
                Task { @MainActor [weak self] in
                    guard let self else { return }
                    if state == .started {
                        self.eventSink(.sessionStarted)
                    } else if state == .stopped {
                        self.eventSink(.phoneFallback(.sessionUnavailable))
                    }
                }
            }
        )
        sessionTokens.append(
            session.errorPublisher.listen { [weak self] error in
                Task { @MainActor [weak self] in
                    guard let self else { return }
                    self.eventSink(.failure(.session))
                    if error == .datAppOnTheGlassesUpdateRequired {
                        self.eventSink(.phoneFallback(.datAppUpdateRequired))
                    } else {
                        self.eventSink(.phoneFallback(.sessionUnavailable))
                    }
                }
            }
        )
    }

    private func observeStream(_ stream: MWDATCamera.Stream) {
        firstFrameSeen = false
        streamTokens.removeAll()
        streamTokens.append(
            stream.statePublisher.listen { [weak self] state in
                Task { @MainActor [weak self] in
                    guard let self else { return }
                    if state == .streaming {
                        self.eventSink(.streamStarted)
                    } else if state == .stopped {
                        self.eventSink(.streamStopped)
                        await self.stopStreamAndCamera()
                    }
                }
            }
        )
        streamTokens.append(
            stream.videoFramePublisher.listen { [weak self] _ in
                Task { @MainActor [weak self] in
                    guard let self, !self.firstFrameSeen else { return }
                    self.firstFrameSeen = true
                    self.eventSink(.firstFrameReceived)
                }
            }
        )
        streamTokens.append(
            stream.errorPublisher.listen { [weak self] _ in
                Task { @MainActor [weak self] in
                    guard let self else { return }
                    self.eventSink(.failure(.stream))
                    self.eventSink(.phoneFallback(.cameraUnavailable))
                }
            }
        )
        streamTokens.append(
            stream.photoDataPublisher.listen { [weak self] data in
                Task { @MainActor [weak self] in
                    guard let self else { return }
                    self.photoSink(data.data)
                    self.eventSink(.photoReceived)
                }
            }
        )
    }

    private func stopStreamAndCamera() async {
        let tokens = streamTokens
        streamTokens.removeAll()
        for token in tokens {
            await token.cancel()
        }
        camera?.stop()
        camera = nil
        stream = nil
        firstFrameSeen = false
    }
}
