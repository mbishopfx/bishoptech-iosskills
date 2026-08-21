# External Accessory recipes

These are compile-oriented route sketches for MFi accessory inventory, protocol checking, EASession input/output streams, framed messages, MFi Wi-Fi configuration, native status, and proof capture. They are not compiled in this documentation-only workspace and do not prove MFi enrollment, manufacturer approval, physical accessory behavior, Wi-Fi configuration, stream delivery, background behavior, or release eligibility.

Before copying:

1. Obtain the accessory manufacturer’s protocol specification and physical test device.
2. Add the exact reverse-DNS protocol string to UISupportedExternalAccessoryProtocols.
3. Add the Wireless Accessory Configuration capability only for supported MFi Wi-Fi configuration.
4. Add external-accessory background mode only for a documented user-facing background requirement.
5. Confirm iPhone/iPad direct hardware support; apps running on a Mac with Apple silicon cannot connect to external accessories with this framework.
6. Keep stream framing and protocol validation out of SwiftUI views.

## Recipe 1: Declare the protocol and keep a typed register

Use a stable reverse-DNS protocol string supplied by the manufacturer:

~~~xml
<key>UISupportedExternalAccessoryProtocols</key>
<array>
    <string>com.example.accessory.control</string>
</array>
~~~

Keep the protocol register separate from UI code:

~~~swift
import Foundation

enum AccessoryProtocolRegister {
    static let control = "com.example.accessory.control"
    static let supportedVersions = Set([1, 2])
    static let maximumFrameSize = 4096
}

struct AccessoryIdentity: Equatable, Sendable {
    let connectionID: Int
    let manufacturer: String
    let model: String
    let firmware: String
}
~~~

The example string is a fixture. A protocol entry in source is not proof that the manufacturer has authorized the app or that a connected accessory supports it.

## Recipe 2: Read the current accessory inventory

EAAccessoryManager’s connected-accessory array is dynamic. Re-read it at feature entry and after connection changes:

~~~swift
import ExternalAccessory

struct AccessoryInventory {
    func compatibleAccessories() -> [EAAccessory] {
        EAAccessoryManager.shared().connectedAccessories.filter { accessory in
            accessory.protocolStrings.contains(
                AccessoryProtocolRegister.control
            )
        }
    }
}
~~~

Do not cache the array as durable truth. If protocolStrings is empty, wait for the accessory’s authentication/readiness path rather than creating a session optimistically.

## Recipe 3: Register for connection changes

The app must ask the shared manager to deliver local accessory notifications:

~~~swift
import ExternalAccessory
import Foundation

final class AccessoryNotificationRouter {
    private var tokens = [NSObjectProtocol]()

    func start() {
        let center = NotificationCenter.default
        let manager = EAAccessoryManager.shared()
        manager.registerForLocalNotifications()

        // Confirm the current Swift notification names in the selected SDK.
        tokens.append(
            center.addObserver(
                forName: .EAAccessoryDidConnect,
                object: manager,
                queue: .main
            ) { notification in
                let accessory = notification.userInfo?[EAAccessoryKey]
                    as? EAAccessory
                _ = accessory
            }
        )
    }

    func stop() {
        let center = NotificationCenter.default
        tokens.forEach(center.removeObserver)
        tokens.removeAll()
        EAAccessoryManager.shared().unregisterForLocalNotifications()
    }
}
~~~

The exact notification bridge can be SDK-sensitive. The proof requirement is a real physical connect/disconnect event after registration, not a local notification fixture alone.

## Recipe 4: Gate session creation on protocolStrings

Create an EASession only for a protocol the accessory currently advertises:

~~~swift
import ExternalAccessory

struct AccessorySessionFactory {
    func makeSession(
        for accessory: EAAccessory
    ) -> EASession? {
        guard accessory.isConnected,
              accessory.protocolStrings.contains(
                  AccessoryProtocolRegister.control
              )
        else {
            return nil
        }

        return EASession(
            accessory: accessory,
            forProtocol: AccessoryProtocolRegister.control
        )
    }
}
~~~

There can be only one session for a given accessory/protocol combination. Treat a nil result as a typed compatibility or communication failure and keep the app UI recoverable.

## Recipe 5: Configure session streams

Immediately retrieve and configure both streams. The stream delegate and run loop are part of the session lifecycle:

~~~swift
import ExternalAccessory
import Foundation

final class AccessoryStreamSession: NSObject, StreamDelegate {
    let session: EASession
    private let input: InputStream
    private let output: OutputStream
    private var inputBuffer = Data()

    init?(accessory: EAAccessory, protocolString: String) {
        guard let session = EASession(
            accessory: accessory,
            forProtocol: protocolString
        ),
        let input = session.inputStream,
        let output = session.outputStream
        else {
            return nil
        }

        self.session = session
        self.input = input
        self.output = output
        super.init()
    }

    func open() {
        input.delegate = self
        output.delegate = self
        input.schedule(in: .current, forMode: .default)
        output.schedule(in: .current, forMode: .default)
        input.open()
        output.open()
    }

    func close() {
        input.close()
        output.close()
        input.remove(from: .current, forMode: .default)
        output.remove(from: .current, forMode: .default)
    }

    func stream(_ aStream: Stream, handle eventCode: Stream.Event) {
        switch eventCode {
        case .openCompleted:
            break
        case .hasBytesAvailable:
            readAvailableBytes()
        case .hasSpaceAvailable:
            drainOutput()
        case .errorOccurred, .endEncountered:
            close()
        default:
            break
        }
    }

    private func readAvailableBytes() {
        // Read bounded chunks, append, and pass complete frames to a codec.
    }

    private func drainOutput() {
        // Write only while hasSpaceAvailable and retain partial output.
    }
}
~~~

Use a serial adapter or actor around stream state. The run-loop callbacks should not mutate SwiftUI state directly.

## Recipe 6: Bound input and decode frames

Keep the framing contract independent from the stream:

~~~swift
struct AccessoryFrame: Sendable, Equatable {
    let version: Int
    let type: UInt8
    let requestID: UUID
    let payload: Data
}

enum AccessoryCodecError: Error {
    case frameTooLarge
    case incomplete
    case invalidVersion
    case invalidChecksum
    case malformedPayload
}

struct AccessoryCodec: Sendable {
    let maximumFrameSize: Int

    func decode(_ data: Data) throws -> [AccessoryFrame] {
        guard data.count <= maximumFrameSize else {
            throw AccessoryCodecError.frameTooLarge
        }
        // Parse length, version, type, request ID, payload, and integrity.
        return []
    }
}
~~~

For partial reads, keep the incomplete suffix in a bounded buffer. For malformed frames, discard only the amount needed to resynchronize according to the manufacturer protocol.

## Recipe 7: Write with stream backpressure

OutputStream writes may be partial. Retain the unsent suffix:

~~~swift
final class AccessoryOutputQueue {
    private var pending = Data()

    func enqueue(_ frame: Data) {
        pending.append(frame)
    }

    func drain(to output: OutputStream) {
        guard output.hasSpaceAvailable, !pending.isEmpty else {
            return
        }

        let written = pending.withUnsafeBytes { bytes in
            output.write(
                bytes.bindMemory(to: UInt8.self).baseAddress!,
                maxLength: bytes.count
            )
        }

        if written > 0 {
            pending.removeFirst(written)
        }
    }
}
~~~

The output queue should have a maximum size, cancellation behavior, timeout, and a clear stale/error state. A positive byte count proves only stream progress.

## Recipe 8: Model a typed command/result

The app-owned command should be smaller and safer than the manufacturer wire format:

~~~swift
struct AccessoryCommand: Sendable, Equatable {
    let requestID: UUID
    let accessoryID: UUID
    let operation: Operation

    enum Operation: Sendable, Equatable {
        case setMode(String)
        case setLevel(Int)
        case requestStatus
        case stop
    }
}

struct AccessoryResult: Sendable, Equatable {
    let requestID: UUID
    let accessoryID: UUID
    let outcome: Outcome
    let receivedAt: Date

    enum Outcome: Sendable, Equatable {
        case accepted
        case rejected(code: String)
        case status(mode: String, level: Int)
    }
}
~~~

The codec maps these value types to manufacturer frames. Views and AI code do not construct arbitrary bytes.

## Recipe 9: Configure an MFi Wi-Fi accessory

Use the system configuration UI for the unconfigured accessory path:

~~~swift
import ExternalAccessory
import Foundation
import UIKit

final class WiFiAccessorySetup: NSObject,
    EAWiFiUnconfiguredAccessoryBrowserDelegate {
    private lazy var browser =
        EAWiFiUnconfiguredAccessoryBrowser(delegate: self, queue: .main)

    func startSearching() {
        browser.startSearchingForUnconfiguredAccessories(matching: nil)
    }

    func stopSearching() {
        browser.stopSearchingForUnconfiguredAccessories()
    }

    func configure(
        _ accessory: EAWiFiUnconfiguredAccessory,
        on viewController: UIViewController
    ) {
        browser.configureAccessory(
            accessory,
            withConfigurationUIOn: viewController
        )
    }

    func accessoryBrowser(
        _ browser: EAWiFiUnconfiguredAccessoryBrowser,
        didFinishConfiguringAccessory accessory: EAWiFiUnconfiguredAccessory,
        with status: EAWiFiUnconfiguredAccessoryConfigurationStatus
    ) {
        // Handle success, cancellation, and failure.
    }
}
~~~

Start only from explicit setup. Stop immediately after finding the desired accessory. After success, re-read connected accessories and protocolStrings before creating EASession.

## Recipe 10: Add an AI proposal validator

AI can propose an operation but cannot decide the protocol or claim completion:

~~~swift
struct AccessoryCommandProposal: Sendable, Equatable {
    let accessoryID: UUID
    let operation: AccessoryCommand.Operation
    let explanation: String
    let requiresConfirmation: Bool
}

enum ProposalError: Error {
    case wrongAccessory
    case protocolUnavailable
    case unsupportedOperation
    case invalidRange
    case confirmationRequired
}

func validate(
    _ proposal: AccessoryCommandProposal,
    selectedAccessoryID: UUID,
    sessionReady: Bool,
    confirmed: Bool
) throws -> AccessoryCommand {
    guard proposal.accessoryID == selectedAccessoryID else {
        throw ProposalError.wrongAccessory
    }
    guard sessionReady else {
        throw ProposalError.protocolUnavailable
    }
    guard !proposal.requiresConfirmation || confirmed else {
        throw ProposalError.confirmationRequired
    }

    return AccessoryCommand(
        requestID: UUID(),
        accessoryID: proposal.accessoryID,
        operation: proposal.operation
    )
}
~~~

The real validator must check manufacturer ranges, framing, authorization, request IDs, timeout, and device result mapping.

## Recipe 11: Display a native session surface

Keep system setup outside the app-owned status card:

~~~swift
import SwiftUI

enum AccessorySessionState: Equatable {
    case noAccessory
    case connected
    case checkingProtocol
    case ready
    case stale
    case disconnected
    case unknownResult
}

struct AccessoryStatusView: View {
    let state: AccessorySessionState
    let title: String
    let retry: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(title, systemImage: "rectangle.connected.to.line.below")
                .font(.headline)
            Text(statusText)
                .foregroundStyle(.secondary)

            if state == .disconnected || state == .stale {
                Button("Retry", action: retry)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .glassEffect(.regular, in: .rect(cornerRadius: 24))
    }

    private var statusText: String {
        switch state {
        case .noAccessory:
            return "Connect a supported accessory"
        case .connected:
            return "Accessory connected"
        case .checkingProtocol:
            return "Checking supported protocol"
        case .ready:
            return "Ready"
        case .stale:
            return "Last result may be stale"
        case .disconnected:
            return "Accessory disconnected"
        case .unknownResult:
            return "The accessory has not confirmed the result"
        }
    }
}
~~~

Verify the exact Liquid Glass API in the final SDK. Test the surface with long names, no accessory, protocol mismatch, reduced transparency, Dynamic Type, and VoiceOver.

## Recipe 12: Capture an evidence record

Store proof metadata separately from domain state:

~~~swift
struct AccessoryEvidence: Sendable, Equatable {
    let target: String
    let platform: String
    let accessoryModel: String
    let firmware: String
    let protocolString: String
    let sessionOpened: Bool
    let streamsTested: Bool
    let physicalResultObserved: Bool
    let wifiConfigurationTested: Bool
    let rawStreamUploaded: Bool
}
~~~

Reject a release claim when physicalResultObserved is false or rawStreamUploaded is true. A successful compile and a connected fixture are not release proof.

## Sources

- [External Accessory](https://developer.apple.com/documentation/externalaccessory)
- [EAAccessoryManager](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager)
- [EAAccessory](https://developer.apple.com/documentation/externalaccessory/eaaccessory)
- [EASession](https://developer.apple.com/documentation/externalaccessory/easession)
- [EAAccessory protocol strings](https://developer.apple.com/documentation/externalaccessory/eaaccessory/protocolstrings)
- [EASession initialization](https://developer.apple.com/documentation/externalaccessory/easession/init%28accessory%3Aforprotocol%3A%29)
- [EASession input stream](https://developer.apple.com/documentation/externalaccessory/easession/inputstream)
- [EASession output stream](https://developer.apple.com/documentation/externalaccessory/easession/outputstream)
- [Connected accessories](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager/connectedaccessories)
- [Register for local accessory notifications](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager/registerforlocalnotifications%28%29)
- [Supported external accessory protocols](https://developer.apple.com/documentation/bundleresources/information-property-list/uisupportedexternalaccessoryprotocols)
- [Wireless Accessory Configuration Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.external-accessory.wireless-configuration)
- [EAWiFiUnconfiguredAccessoryBrowser](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser)
- [Start searching for unconfigured accessories](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser/startsearchingforunconfiguredaccessories%28matching%3A%29)
- [Stop searching for unconfigured accessories](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser/stopsearchingforunconfiguredaccessories%28%29)
- [Configure an unconfigured accessory](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser/configureaccessory%28_%3Awithconfigurationuion%3A%29)
- [Configuration status](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessoryconfigurationstatus)
- [UIBackgroundModes](https://developer.apple.com/documentation/bundleresources/information-property-list/uibackgroundmodes)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
