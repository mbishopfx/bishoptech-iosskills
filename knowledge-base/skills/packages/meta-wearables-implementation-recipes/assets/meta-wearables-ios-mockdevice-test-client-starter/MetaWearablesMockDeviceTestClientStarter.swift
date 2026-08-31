import Foundation
import MWDATCore
import MWDATMockDeviceTestClient

public enum MetaWearablesMockDeviceTestClientEvent: Sendable {
    case serverReady
    case serverUnavailable
    case paired
    case unpaired
    case actionSucceeded
    case actionFailed
    case noPairedDevice
}

/// A UI-test-process boundary for the DAT 0.9.0 MockDevice test server.
///
/// The paired device identifier remains private to the harness. State queries
/// expose only sanitized counts, while media resource names are passed to the
/// SDK and never logged or emitted. This client controls a mock server; it is
/// not a runtime glasses capability and never proves physical behavior.
@MainActor
public final class MetaWearablesMockDeviceTestClientHarness {
    public typealias EventSink = @Sendable (MetaWearablesMockDeviceTestClientEvent) -> Void

    private let client: MockDeviceTestClient
    private let eventSink: EventSink
    private var deviceID: String?

    public init(
        portFilePath: String,
        eventSink: @escaping EventSink = { _ in }
    ) {
        self.client = MockDeviceTestClient(portFilePath: portFilePath)
        self.eventSink = eventSink
    }

    public init(
        port: UInt16,
        eventSink: @escaping EventSink = { _ in }
    ) {
        self.client = MockDeviceTestClient(port: port)
        self.eventSink = eventSink
    }

    public init(eventSink: @escaping EventSink = { _ in }) {
        self.client = MockDeviceTestClient()
        self.eventSink = eventSink
    }

    public var hasPairedDevice: Bool { deviceID != nil }

    @discardableResult
    public func waitForServer(timeout: TimeInterval = 10) -> Bool {
        let ready = client.waitForServer(timeout: timeout)
        eventSink(ready ? .serverReady : .serverUnavailable)
        return ready
    }

    @discardableResult
    public func healthCheck() -> Bool {
        let healthy = client.healthCheck()
        eventSink(healthy ? .serverReady : .serverUnavailable)
        return healthy
    }

    @discardableResult
    public func pairRayBanMeta() -> Bool {
        guard deviceID == nil else { return true }
        guard let pairedID = client.pairDevice(deviceType: .rayBanMeta) else {
            eventSink(.actionFailed)
            return false
        }
        deviceID = pairedID
        eventSink(.paired)
        return true
    }

    @discardableResult
    public func unpair() -> Bool {
        guard let deviceID else {
            eventSink(.noPairedDevice)
            return false
        }
        let success = client.unpairDevice(deviceId: deviceID)
        if success {
            self.deviceID = nil
            eventSink(.unpaired)
        } else {
            eventSink(.actionFailed)
        }
        return success
    }

    public func powerOn() { perform { $0.powerOn(deviceId: $1) } }
    public func powerOff() { perform { $0.powerOff(deviceId: $1) } }
    public func unfold() { perform { $0.unfold(deviceId: $1) } }
    public func fold() { perform { $0.fold(deviceId: $1) } }
    public func don() { perform { $0.don(deviceId: $1) } }
    public func doff() { perform { $0.doff(deviceId: $1) } }
    public func tap() { perform { $0.captouchTap(deviceId: $1) } }
    public func tapAndHold() { perform { $0.captouchTapAndHold(deviceId: $1) } }

    public func setCameraFeed(resourceName: String, ext: String) {
        perform { $0.setCameraFeed(deviceId: $1, resourceName: resourceName, ext: ext) }
    }

    public func setCapturedImage(resourceName: String, ext: String) {
        perform { $0.setCapturedImage(deviceId: $1, resourceName: resourceName, ext: ext) }
    }

    /// Return only a sanitized count from the server state response.
    public func pairedDeviceCount() -> Int? {
        client.getDeviceState()?["pairedDeviceCount"] as? Int
    }

    /// Release the test-process device. The app process owns server shutdown.
    public func teardown() {
        guard deviceID != nil else { return }
        _ = unpair()
    }

    private func perform(_ operation: (MockDeviceTestClient, String) -> Bool) {
        guard let deviceID else {
            eventSink(.noPairedDevice)
            return
        }
        eventSink(operation(client, deviceID) ? .actionSucceeded : .actionFailed)
    }
}
