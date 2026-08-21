# CoreMIDI: MIDI 1/2, networking, and device I/O

CoreMIDI is the Apple transport layer for MIDI devices and MIDI endpoints. It is useful for hardware keyboards, pad controllers, synthesizers, drum machines, audio-control surfaces, virtual instruments, and networked MIDI peers. Treat it as a real-time device and transport boundary, not as a generic audio API and not as a reason to put timing-sensitive work in a SwiftUI view.

The reusable route is:

device or virtual endpoint -> CoreMIDI object graph -> client and port -> MIDI 1/2 event transport -> deterministic domain state -> SwiftUI/control surface -> optional reviewed AI proposal

The control surface can look native and use Liquid Glass, but the transport must remain independently testable, observable, and safe under device removal, interruption, high event rates, and permission changes.

## 1. The CoreMIDI object graph

The system exposes a graph rather than one flat list:

- A MIDI device contains one or more entities.
- An entity exposes source and destination endpoints.
- An input port receives from one or more source endpoints.
- An output port sends to one destination endpoint at a time for each send operation.
- A client owns ports and receives system notifications through a client notification block.
- Virtual sources and destinations let an app publish or consume MIDI without a physical device.

The CoreMIDI Services documentation groups the creation, enumeration, connection, event-list, and virtual-endpoint APIs. The useful design consequence is that discovery, selection, connection, and event processing should be separate state machines. A display name is presentation; a selected endpoint identity and its current connection state belong in the domain model.

Typical discovery work includes:

1. Create one MIDI client for the app process.
2. Enumerate devices and external devices when the route needs both local and externally exposed hardware.
3. Inspect each device’s entities and each entity’s sources and destinations.
4. Preserve the endpoint’s stable identity and current metadata in a device snapshot.
5. Create input and output ports only for the routes the user has selected.
6. Listen for client notifications and reconcile the graph when devices or properties change.

Do not assume that a device remains present between enumeration and connection. Every connection attempt needs a failure path and a later reconciliation path.

## 2. MIDI 1.0, MIDI 2.0, and Universal MIDI Packets

MIDI 2.0 uses Universal MIDI Packets, or UMPs. MIDI 1.0 messages can also travel in UMP form through MIDI 1.0 Universal Packet messages. The group field allows multiple MIDI streams to share a transport. MIDI 2.0 adds higher-resolution channel voice messages, per-note data, profiles, property exchange, and MIDI Capability Inquiry.

CoreMIDI’s protocol-aware APIs let an app create a port with a requested MIDI protocol. The system can convert between the port’s protocol and a destination’s supported protocol. This is valuable for compatibility, but it does not remove the need to test the actual source and destination pair:

- A MIDI 1 destination may receive a legacy packet list.
- A MIDI 2 destination may receive a MIDI event list containing UMP words.
- A MIDI 2 device requires bidirectional communication for MIDI-CI negotiation.
- A conversion path may discard precision or message types that the older destination cannot represent.
- A group, channel, note, controller, and timestamp must remain visible in the normalized domain event.

Keep transport representations and app actions separate. A normalized NoteOn action may be produced from a MIDI 1 packet or a MIDI 2 UMP, but the app should retain enough provenance to explain the source protocol and preserve the original message when recording or forwarding.

CoreMIDI exposes message helpers for common MIDI 1 and MIDI 2 messages, event-list initialization and insertion, protocol identifiers, message-type inspection, and MIDI event packets. Use those helpers instead of hand-building words when the target message is covered by the SDK. For vendor-specific data, preserve the raw UMP or SysEx payload and validate its length before interpretation.

## 3. Client, port, endpoint, and event lifecycle

The minimum lifecycle has four ownership boundaries:

| Boundary | Owns | Must survive |
| --- | --- | --- |
| Discovery model | Device/entity/source/destination metadata and stable IDs | UI redraws, device list refreshes, selection changes |
| MIDI client | Client reference and notification callback | Port recreation and endpoint churn |
| Port layer | Input/output ports and endpoint connections | View disappearance and scene phase changes |
| Event pipeline | Receive callback, bounded handoff, normalization, recording/output queue | SwiftUI scheduling and actor hops |

Use the modern protocol-aware port APIs for new work. The older MIDIInputPortCreate path is deprecated in favor of MIDIInputPortCreateWithProtocol. The receive block is invoked on a separate high-priority thread. It must do only real-time-safe, nonblocking work: inspect the event list, copy or reference bounded data safely, enqueue a compact event, and return. It must not perform SwiftUI mutations, allocate unbounded collections, await an actor, write to disk, call a model, or wait for a lock.

A practical handoff is:

MIDIReceiveBlock -> bounded ring or lock-free handoff -> task/actor -> normalized event stream -> feature state

The exact queue implementation should be chosen for the target’s latency and correctness requirements. The important boundary is observable: the receive block is not the place to do UI, persistence, network work, or AI.

For output, create the output port once per client, validate that the destination is still available, build the protocol-correct event list, send it, and surface the status in diagnostics. Do not make a SwiftUI button’s tap handler responsible for discovering the whole device graph each time it sends a note.

## 4. Input and output route families

### Physical and externally exposed devices

CoreMIDI can communicate with attached and externally exposed MIDI hardware. The exact transport can be USB, a compatible accessory path, Bluetooth MIDI, or a network session. The app’s route card should report the transport and endpoint identity that it actually discovered, not promise that every keyboard or interface works.

### Virtual endpoints

Virtual sources and destinations create an app-facing MIDI endpoint. Use them when the product needs to publish generated events to other MIDI-aware apps or receive events from them. A virtual endpoint is not proof that external software is connected; the app should show published, connected, receiving, and idle states separately.

### Network MIDI

MIDINetworkSession provides a default network MIDI session with source and destination endpoints, connections, contacts, connection policy, local/network names, and session-change notifications. A session may merge incoming data and broadcast outgoing data to its connections. That makes it useful for a multi-device rehearsal or control surface, but it also creates a trust and routing boundary:

- Ask the user to enable or join the intended session.
- Display the peer or contact identity that the user selected.
- Keep connection policy explicit.
- Deduplicate or label events if multiple peers can produce the same action.
- Treat a send callback as transport acceptance, not a confirmed sound or remote side effect.

Network MIDI requires local-network privacy planning. Include the local-network purpose string when the app uses the local network directly or through the networking route, and test denial and later approval.

### Bluetooth MIDI

For paired Bluetooth MIDI peripherals, current iOS behavior can reconnect supported peripherals automatically. For an unpaired peripheral, the documented Core Bluetooth handoff is:

1. Scan for and connect to the BLE peripheral.
2. Confirm that the Bluetooth MIDI service is present.
3. Confirm the MIDI I/O characteristic.
4. Activate the CoreMIDI Bluetooth driver connections.
5. Disconnect the driver connection when the peripheral is no longer usable.

Do not activate every discovered BLE device. Require the service and characteristic checks, maintain a user-visible pairing state, and test reconnect, disappearance, denial, and background/foreground transitions. Bluetooth usage text is a protected-resource boundary and should explain the user benefit in plain language.

## 5. MIDI Thru, transformation, and routing

When the app is forwarding or transforming MIDI between endpoints, CoreMIDI’s MIDI Thru Connection services can reduce app-level overhead and provide routing and transformation structures. Consider MIDI Thru for simple, always-on forwarding or channel/filter transformations. Keep routing in the app when the product needs:

- a reviewable user action before forwarding;
- an editable route graph;
- recording, undo, provenance, or per-event analytics;
- AI-generated mapping proposals that need approval;
- a deterministic state machine that can be replayed in tests.

The app should state whether a route is direct, transformed, recorded, or proposed. “Connected” is not the same as “forwarding,” and “forwarding” is not the same as “heard.”

## 6. MIDI Capability Inquiry and profiles

MIDI-CI provides a capability and negotiation layer for MIDI 2 devices. MIDICIDeviceManager exposes discovered MIDI-CI devices and notifications for device, profile, and property changes. Use it to discover what a device actually supports before presenting controls for profiles, property exchange, or higher-resolution messages.

A safe flow is:

1. Discover the device and establish bidirectional transport.
2. Observe the MIDI-CI device manager and device capabilities.
3. Offer only controls supported by the current profile/property state.
4. Show negotiation and device-change state.
5. Reconcile when the user changes the device externally or disconnects it.

Do not treat a device’s marketing name as proof of MIDI 2 profile support. Record the protocol, capability, and profile evidence that the route used.

## 7. AVFAudio is a separate boundary

CoreMIDI transports musical control messages. AVFAudio owns the app’s audio session and audio graph: category, mode, activation, interruptions, route changes, audio engine, samplers, and MIDI/audio player components. A MIDI note arriving successfully does not prove that an instrument rendered sound.

If a feature includes both MIDI and audio:

- configure AVAudioSession for the product’s playback/recording use case;
- handle interruptions and route changes independently;
- make the audio engine’s running/rendering state observable;
- keep MIDI transport status separate from audio output status;
- test headphones, speaker, Bluetooth audio, silent mode, interruptions, and denied/changed routes where relevant.

This separation also improves AI honesty. A model may suggest a chord or map a controller, but the product must report whether the MIDI message was accepted and whether audio is actually active as separate facts.

## 8. Native SwiftUI and Liquid Glass composition

Use a layered native surface:

- device/endpoint picker;
- route status and protocol badge;
- compact input monitor;
- mapping or transform editor;
- explicit arm/send/audition control;
- diagnostics and permission recovery;
- optional AI suggestion sheet.

Liquid Glass is appropriate for transient route controls, status clusters, inspector panels, and review sheets. Keep high-frequency event visualization visually quiet: a small meter or event count is better than a constantly morphing decorative surface. Do not put the real-time callback behind a glass view or let material animation determine transport timing.

Use semantic SwiftUI controls, focus behavior, Dynamic Type, VoiceOver labels, keyboard/controller alternatives, and reduced-motion behavior. A musician should be able to identify source, destination, channel, armed state, and last event without relying on color or audio alone.

## 9. Bounded on-device AI opportunities

AI can help with interpretation and setup, not with pretending to be a transport guarantee:

- suggest a mapping from a controller’s observed controls to app actions;
- explain a MIDI 1/2 compatibility warning;
- propose a named preset from a user-approved device snapshot;
- summarize a recording after the user stops capture;
- suggest a routing transform or channel normalization;
- generate a human-readable explanation of a MIDI-CI capability.

Keep model output typed and reviewable. The deterministic layer should validate endpoint identity, protocol, ranges, channels, message types, user permissions, and side effects before any send, transform, or persistent change. Never let a model call a raw MIDI send function directly.

## 10. Availability, privacy, and release proof

CoreMIDI documentation includes platform-specific behavior and examples that may target iPadOS or Mac Catalyst. A documented API or sample is not proof that a particular iPhone model, iOS deployment target, accessory transport, or app entitlement behaves the same way. Inspect the selected SDK’s availability annotations and compile the named target.

Record, at minimum:

- target platform, deployment target, SDK, and device model;
- source and destination endpoint identities;
- protocol used and whether conversion occurred;
- physical, BLE, network, or virtual transport;
- local-network/Bluetooth purpose strings and denial recovery;
- input callback handoff and queue-overflow behavior;
- MIDI 1, MIDI 2, SysEx, and MIDI-CI behavior where claimed;
- audio session and rendering evidence if audio is part of the product;
- accessibility and reduced-motion evidence;
- signed device/TestFlight evidence for the final target.

The knowledge-base recipe is a route plan until those artifacts exist.

## Sources

- [CoreMIDI](https://developer.apple.com/documentation/coremidi/)
- [MIDI Services](https://developer.apple.com/documentation/coremidi/midi-services)
- [Incorporating MIDI 2 into your apps](https://developer.apple.com/documentation/coremidi/incorporating-midi-2-into-your-apps)
- [MIDI messages](https://developer.apple.com/documentation/coremidi/midi-messages)
- [MIDI event packets](https://developer.apple.com/documentation/coremidi/midieventpacket)
- [MIDI event list protocol](https://developer.apple.com/documentation/coremidi/midieventlist/protocol)
- [MIDINetworkSession](https://developer.apple.com/documentation/coremidi/midinetworksession)
- [MIDI networking](https://developer.apple.com/documentation/coremidi/midi-networking)
- [MIDI Bluetooth](https://developer.apple.com/documentation/coremidi/midi-bluetooth)
- [MIDI Thru Connection](https://developer.apple.com/documentation/coremidi/midi-thru-connection)
- [MIDICIDeviceManager](https://developer.apple.com/documentation/coremidi/midicidevicemanager)
- [MIDI receive block](https://developer.apple.com/documentation/coremidi/midireceiveblock)
- [MIDI input port with protocol](https://developer.apple.com/documentation/coremidi/midiinputportcreatewithprotocol%28_%3A_%3A_%3A_%3A_%3A%29)
- [AVFAudio](https://developer.apple.com/documentation/avfaudio)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Playing audio](https://developer.apple.com/design/human-interface-guidelines/playing-audio)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nslocalnetworkusagedescription)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)

***
