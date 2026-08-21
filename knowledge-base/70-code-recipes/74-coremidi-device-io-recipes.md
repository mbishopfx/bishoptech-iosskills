# CoreMIDI device I/O code recipes

These are compile-oriented route sketches for a named iOS target. They show ownership and boundaries; they are not a drop-in guarantee for every SDK revision, endpoint type, or accessory. Compile each symbol against the selected SDK and keep real-time callback code free of UI, allocation-heavy work, blocking, persistence, and model calls.

## 1. A domain event that does not leak CoreMIDI pointers

~~~swift
import CoreMIDI

struct NormalizedMIDIEvent: Sendable {
    let sourceID: MIDIUniqueID
    let timestamp: MIDITimeStamp
    let protocolID: MIDIProtocolID
    let group: UInt8
    let channel: UInt8
    let messageType: UInt8
    let words: [UInt32]
}
~~~

The production version should define exact word-count/range invariants and decide whether raw words are copied for recording. Do not retain an unsafe pointer from the receive callback and use it later.

## 2. Enumerate devices and endpoint roles

~~~swift
import CoreMIDI

func enumerateMIDI() -> [(device: MIDIEndpointRef, name: String)] {
    var result: [(MIDIEndpointRef, String)] = []
    let count = MIDIGetNumberOfDevices()

    for index in 0..<count {
        let device = MIDIGetDevice(index)
        var name: Unmanaged<CFString>?
        MIDIObjectGetStringProperty(device, kMIDIPropertyName, &name)
        result.append((device, (name?.takeUnretainedValue() as String?) ?? "Unnamed MIDI device"))
    }
    return result
}
~~~

Treat this as a sketch. A production enumerator should inspect entities, sources, destinations, object properties, OSStatus values, external devices when appropriate, and endpoint identity. Publish an immutable snapshot instead of returning a UI-ready array directly from the transport owner.

## 3. Create a client with a notification boundary

~~~swift
import CoreMIDI

final class MIDIClientOwner {
    private var client = MIDIClientRef()

    func start() throws {
        let status = MIDIClientCreateWithBlock(
            "Example MIDI Client" as CFString,
            &client
        ) { notification in
            // Keep notification handling small. Re-enumerate asynchronously.
            // Do not mutate SwiftUI state from this callback.
            _ = notification
        }

        guard status == noErr else {
            throw NSError(domain: NSOSStatusErrorDomain, code: Int(status))
        }
    }

    func stop() {
        guard client != 0 else { return }
        MIDIClientDispose(client)
        client = 0
    }
}
~~~

The exact imported Swift signatures can vary with SDK overlays. The architectural rule is stable: one owner creates and disposes the client, notification handling triggers reconciliation, and view lifetime does not silently own the global device graph.

## 4. Create an input port and connect a source

~~~swift
import CoreMIDI

func makeInputPort(
    client: MIDIClientRef,
    source: MIDIEndpointRef,
    receive: @escaping (UnsafePointer<MIDIEventList>) -> Void
) throws -> MIDIPortRef {
    var port = MIDIPortRef()

    let status = MIDIInputPortCreateWithProtocol(
        client,
        "Input" as CFString,
        MIDIProtocolID._1_0,
        &port
    ) { eventList, _ in
        // This is a high-priority receive path.
        // Copy only bounded data and return; no UI, await, disk, or model call.
        receive(eventList)
    }

    guard status == noErr else {
        throw NSError(domain: NSOSStatusErrorDomain, code: Int(status))
    }

    let connectStatus = MIDIPortConnectSource(port, source, nil)
    guard connectStatus == noErr else {
        MIDIPortDispose(port)
        throw NSError(domain: NSOSStatusErrorDomain, code: Int(connectStatus))
    }
    return port
}
~~~

Validate the exact event-list pointer and Swift callback signature in the selected SDK. The receive closure should copy the words into a bounded handoff owned by the transport layer; the code above intentionally leaves that copy operation as a target-specific implementation detail.

## 5. Keep the receive callback real-time safe

~~~swift
final class MIDIReceiveHandoff {
    // Replace with a bounded ring or another measured real-time-safe handoff.
    // This placeholder must not be used as a production queue.
    private var pending: [NormalizedMIDIEvent] = []

    func receive(_ event: NormalizedMIDIEvent) {
        // The production callback must have a bounded overflow policy.
        pending.append(event)
    }

    func drain() -> [NormalizedMIDIEvent] {
        let values = pending
        pending.removeAll(keepingCapacity: true)
        return values
    }
}
~~~

This intentionally demonstrates the boundary, not a safe implementation. An Array append in a high-priority callback is not proof of real-time safety. Replace it with a measured bounded mechanism, document overflow behavior, and test under burst input before making latency claims.

## 6. Send a protocol-aware event list

~~~swift
import CoreMIDI

func sendNote(
    outputPort: MIDIPortRef,
    destination: MIDIEndpointRef,
    channel: UInt8,
    note: UInt8,
    velocity: UInt8
) -> OSStatus {
    // Prefer SDK message helpers and the protocol-aware event-list APIs.
    // The exact mutable buffer layout is SDK-sensitive and omitted here.
    let message = MIDI1UPNoteOn(channel: channel, note: note, velocity: velocity)
    _ = message
    _ = outputPort
    _ = destination
    return noErr
}
~~~

The production implementation must construct a valid MIDIEventList for the requested protocol, preserve timestamps, validate channel/group/ranges, call the appropriate send API, and report OSStatus. A successful send call means CoreMIDI accepted the operation; it does not prove that a synthesizer rendered audible sound.

## 7. Configure a network session explicitly

~~~swift
import CoreMIDI

func configureNetworkMIDI() -> MIDINetworkSession {
    let session = MIDINetworkSession.default()
    session.isEnabled = true
    session.connectionPolicy = .anyone

    // Use the session's sourceEndpoint and destinationEndpoint with
    // CoreMIDI ports after the product has explained the trust boundary.
    return session
}
~~~

Do not ship .anyone as an unexamined default for a product that sends commands. Prefer an explicit policy and user-selected contacts when the route can affect external equipment. Add local-network privacy copy and test denial, peer removal, and session changes.

## 8. BLE MIDI activation boundary

~~~swift
import CoreBluetooth
import CoreMIDI

func activateIfMIDIServiceIsConfirmed(
    peripheral: CBPeripheral,
    hasMIDIService: Bool,
    hasMIDICharacteristic: Bool
) {
    guard hasMIDIService, hasMIDICharacteristic else {
        return
    }

    // The production route calls the CoreMIDI Bluetooth driver activation
    // only after Core Bluetooth discovery has confirmed the MIDI service and
    // I/O characteristic for this peripheral.
    _ = peripheral
    MIDIBluetoothDriverActivateAllConnections()
}
~~~

Keep the Core Bluetooth discovery state and CoreMIDI driver state separate. Test the missing-service path and disconnect cleanup. Never activate every BLE peripheral discovered by the app.

## 9. Project transport into SwiftUI

~~~swift
import Observation
import SwiftUI

@MainActor
@Observable
final class MIDIControlModel {
    var endpoints: [String] = []
    var selectedSource: String?
    var selectedDestination: String?
    var connectionStatus = "Not connected"
    var lastEventSummary = "No MIDI events yet"
    var pendingProposal: MappingProposal?
}

struct MIDIControlSurface: View {
    @State private var model = MIDIControlModel()

    var body: some View {
        NavigationStack {
            List {
                Section("Route") {
                    Text(model.connectionStatus)
                    Text(model.lastEventSummary)
                }

                Section("Actions") {
                    Button("Choose source") {
                        // Present a picker backed by a transport snapshot.
                    }
                    Button("Choose destination") {
                        // Selection is an intent; connection state arrives later.
                    }
                    Button("Arm mapping") {
                        // Explicitly enter learn mode.
                    }
                }
            }
            .navigationTitle("MIDI")
        }
    }
}
~~~

The view model should receive immutable snapshots and normalized events from a transport owner. Add Liquid Glass to contextual status or review surfaces only after the hierarchy works in plain semantic controls. Keep connection, input, audio, and AI states separate.

## 10. Typed AI proposal with deterministic validation

~~~swift
struct MappingProposal: Codable, Sendable {
    let actionID: String
    let sourceEndpointID: MIDIUniqueID
    let channel: UInt8
    let controller: UInt8
    let reason: String
}

enum ProposalValidation {
    case accepted(MappingProposal)
    case rejected(String)
}

func validate(
    _ proposal: MappingProposal,
    currentEndpointIDs: Set<MIDIUniqueID>,
    actionIDs: Set<String>
) -> ProposalValidation {
    guard currentEndpointIDs.contains(proposal.sourceEndpointID) else {
        return .rejected("The source endpoint is no longer connected.")
    }
    guard actionIDs.contains(proposal.actionID) else {
        return .rejected("The action is not available in this target.")
    }
    guard proposal.channel < 16, proposal.controller < 128 else {
        return .rejected("The MIDI range is invalid.")
    }
    return .accepted(proposal)
}
~~~

The model proposes data; the validator decides whether the current endpoint graph, protocol, range, permissions, and user action allow it. Require a visible review and use an explicit apply step before saving or sending anything.

## Sources

- [CoreMIDI](https://developer.apple.com/documentation/coremidi/)
- [MIDI Services](https://developer.apple.com/documentation/coremidi/midi-services)
- [Incorporating MIDI 2 into your apps](https://developer.apple.com/documentation/coremidi/incorporating-midi-2-into-your-apps)
- [MIDI messages](https://developer.apple.com/documentation/coremidi/midi-messages)
- [MIDI event packets](https://developer.apple.com/documentation/coremidi/midieventpacket)
- [MIDI receive block](https://developer.apple.com/documentation/coremidi/midireceiveblock)
- [MIDI input port with protocol](https://developer.apple.com/documentation/coremidi/midiinputportcreatewithprotocol%28_%3A_%3A_%3A_%3A_%3A%29)
- [MIDINetworkSession](https://developer.apple.com/documentation/coremidi/midinetworksession)
- [MIDI Bluetooth](https://developer.apple.com/documentation/coremidi/midi-bluetooth)
- [MIDICIDeviceManager](https://developer.apple.com/documentation/coremidi/midicidevicemanager)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

***
