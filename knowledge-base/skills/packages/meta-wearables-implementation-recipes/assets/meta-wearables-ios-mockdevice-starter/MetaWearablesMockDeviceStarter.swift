import Foundation
import MWDATCore
import MWDATMockDevice

public enum MetaWearablesMockDeviceEvent: Sendable {
    case enabled
    case disabled
    case pairedRayBanMeta
    case unpairedRayBanMeta
    case lifecycleChanged
    case cameraPermissionConfigured
    case cameraFeedConfigured
    case capturedImageConfigured
    case captouchTriggered
    case noPairedDevice
    case pairFailed
}

/// A small, target-owned MockDeviceKit harness for deterministic DAT tests.
///
/// The harness reports only sanitized test events. It never logs device
/// identifiers, URLs, media bytes, or account state, and it does not convert a
/// mock result into physical-glasses evidence.
@MainActor
public final class MetaWearablesMockDeviceHarness {
    public typealias EventSink = @Sendable (MetaWearablesMockDeviceEvent) -> Void

    private let kit: any MockDeviceKitInterface
    private let eventSink: EventSink
    private var glasses: (any MockGlasses)?

    public init(
        kit: any MockDeviceKitInterface = MockDeviceKit.shared,
        eventSink: @escaping EventSink = { _ in }
    ) {
        self.kit = kit
        self.eventSink = eventSink
    }

    public var isEnabled: Bool { kit.isEnabled }
    public var hasPairedRayBanMeta: Bool { glasses != nil }

    public func enable(
        initiallyRegistered: Bool = true,
        initialPermissionsGranted: Bool = true
    ) {
        kit.enable(
            config: MockDeviceKitConfig(
                initiallyRegistered: initiallyRegistered,
                initialPermissionsGranted: initialPermissionsGranted
            )
        )
        eventSink(.enabled)
    }

    public func pairRayBanMeta() throws {
        guard glasses == nil else { return }

        do {
            glasses = try kit.pairGlasses(model: .rayBanMeta)
            eventSink(.pairedRayBanMeta)
        } catch {
            eventSink(.pairFailed)
            throw error
        }
    }

    public func unpairRayBanMeta() {
        guard let glasses else {
            eventSink(.noPairedDevice)
            return
        }
        kit.unpairDevice(glasses)
        self.glasses = nil
        eventSink(.unpairedRayBanMeta)
    }

    public func powerOn() { performLifecycle { $0.powerOn() } }
    public func powerOff() { performLifecycle { $0.powerOff() } }
    public func unfold() { performLifecycle { $0.unfold() } }
    public func fold() { performLifecycle { $0.fold() } }
    public func don() { performLifecycle { $0.don() } }
    public func doff() { performLifecycle { $0.doff() } }

    public func setCameraPermission(
        status: PermissionStatus,
        requestResult: PermissionStatus
    ) {
        kit.permissions.set(.camera, status)
        kit.permissions.setRequestResult(.camera, result: requestResult)
        eventSink(.cameraPermissionConfigured)
    }

    public func setCameraFeed(fileURL: URL) {
        guard let glasses else {
            eventSink(.noPairedDevice)
            return
        }
        glasses.services.camera.setCameraFeed(fileURL: fileURL)
        eventSink(.cameraFeedConfigured)
    }

    public func setCameraFeed(cameraFacing: CameraFacing) {
        guard let glasses else {
            eventSink(.noPairedDevice)
            return
        }
        glasses.services.camera.setCameraFeed(cameraFacing: cameraFacing)
        eventSink(.cameraFeedConfigured)
    }

    public func setCapturedImage(fileURL: URL) {
        guard let glasses else {
            eventSink(.noPairedDevice)
            return
        }
        glasses.services.camera.setCapturedImage(fileURL: fileURL)
        eventSink(.capturedImageConfigured)
    }

    public func tap() { performInput { $0.services.captouch.tap() } }
    public func tapAndHold() { performInput { $0.services.captouch.tapAndHold() } }

    /// Release the paired mock before disabling the shared kit.
    public func disable() {
        if let glasses {
            kit.unpairDevice(glasses)
            self.glasses = nil
        }
        kit.disable()
        eventSink(.disabled)
    }

    private func performLifecycle(_ operation: (any MockGlasses) -> Void) {
        guard let glasses else {
            eventSink(.noPairedDevice)
            return
        }
        operation(glasses)
        eventSink(.lifecycleChanged)
    }

    private func performInput(_ operation: (any MockGlasses) -> Void) {
        guard let glasses else {
            eventSink(.noPairedDevice)
            return
        }
        operation(glasses)
        eventSink(.captouchTriggered)
    }
}
