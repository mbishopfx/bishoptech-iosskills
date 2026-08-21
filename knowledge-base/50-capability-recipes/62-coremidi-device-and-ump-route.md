# CoreMIDI device and UMP capability route

Use this route for an iOS app that discovers MIDI devices, connects selected source/destination endpoints, receives or sends MIDI 1/2 events, optionally supports BLE/network/virtual endpoints, and presents a native SwiftUI control surface.

The route is intentionally split into transport, domain, UI, and AI layers. Do not make the UI view own the MIDI client or let a model call a send function.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | Play, map, record, route, inspect, or explain MIDI behavior |
| Input | Physical MIDI endpoint, BLE MIDI peripheral, network session, virtual source, or saved recording |
| Framework | CoreMIDI; optionally CoreBluetooth, AVFAudio, SwiftUI, Foundation Models |
| Transport | MIDI 1 packet compatibility, MIDI 2 UMP event list, or a system-converted port |
| Domain model | Stable endpoint identity, protocol/capabilities, normalized MIDI event, connection state |
| UI | Device picker, route inspector, mapping editor, monitor, reviewable AI sheet |
| Side effects | Connect, send, forward, save mapping, record, or negotiate profile |
| Proof | Target compile, physical MIDI device, BLE/network denial/recovery, event capture/send, audio route if relevant |

## Step 1: Define the route contract

Write the user-visible contract before importing the framework:

- Which source and destination roles are supported?
- Is the product MIDI 1 only, MIDI 2 aware, or protocol-agnostic?
- Does it need raw UMP/SysEx recording?
- Does it need a virtual endpoint?
- Does it need network or BLE discovery?
- Does it render audio or only transport MIDI?
- Can the route operate offline?
- Which actions require explicit confirmation?

Keep a capability matrix for the exact target. Do not advertise a MIDI 2 profile or device control merely because CoreMIDI has a type for it.

## Step 2: Configure target and privacy

Use the selected SDK’s CoreMIDI availability and compile the named iOS target. Add protected-resource purpose strings for any Bluetooth or local-network route that needs them. If using CoreBluetooth for an unpaired BLE MIDI handoff, configure the Bluetooth capability and test the missing/denied usage description path.

If the app includes audio rendering, configure AVAudioSession separately. If it includes a network session, document whether it uses a user-selected peer, a local session, or an app-controlled network route.

## Step 3: Own one client and reconcile the graph

Create one client owner for the feature scope. The owner should:

1. create the MIDI client;
2. receive client notifications;
3. enumerate devices, external devices, entities, sources, and destinations;
4. publish immutable snapshots to the domain layer;
5. close or recreate ports when the selected endpoint changes;
6. surface errors and stale selections.

The snapshot should include endpoint role, name, stable ID, transport hint, protocol if known, selection, connection, and last event time. Keep a separate device graph from the UI list so a view can disappear without tearing down the transport unexpectedly.

## Step 4: Create protocol-aware ports

Prefer MIDIInputPortCreateWithProtocol and its matching output-port route. Choose the protocol deliberately:

- MIDI 1 compatibility when the target or app contract requires it;
- MIDI 2 UMP when the target supports it and the product needs the precision/features;
- system conversion only when the loss and destination behavior are acceptable.

Connect selected source endpoints to the input port. Keep the receive block small and real-time safe. Copy the minimum required words or bytes into a bounded handoff. Normalize on a task or actor after the callback returns.

## Step 5: Normalize and expose event provenance

Create a domain event with:

- timestamp and clock domain;
- source endpoint ID;
- MIDI protocol;
- UMP group;
- channel;
- message type;
- note/controller/program/pressure/pitch data;
- raw words or payload when recording is enabled;
- conversion or truncation warning if relevant.

Use this normalized event for mapping, recording, visualization, and AI context. Do not make every downstream consumer parse a CoreMIDI pointer or packet list.

## Step 6: Send through an explicit action gate

The send gate should validate:

- selected destination is still present;
- message type and range are valid;
- group/channel are in range;
- user has armed or confirmed the action when required;
- destination protocol can represent the requested message;
- rate and queue limits are safe.

Report the transport result separately from “instrument sounded.” If audio rendering is part of the app, observe AVAudioEngine/AVMIDIPlayer/audio-session state independently.

## Step 7: Add BLE, network, and virtual routes one at a time

Do not mix every transport in the first implementation:

1. Ship physical/virtual endpoint discovery and one input/output path.
2. Add Bluetooth MIDI after service/characteristic validation and permission recovery.
3. Add MIDINetworkSession with explicit contact/policy UI and local-network proof.
4. Add virtual sources/destinations if inter-app routing is part of the product.
5. Add MIDI-CI capabilities only after bidirectional transport and device-change handling are solid.

Each transport gets its own state and proof matrix. A network contact should not appear identical to a USB endpoint.

## Step 8: Add native SwiftUI and Liquid Glass

Project transport state into a view model or observable store:

- endpoint picker;
- route status;
- protocol/capability summary;
- arm/send/audition controls;
- event monitor;
- mapping editor;
- permission/reconnect sheet;
- AI review sheet.

Use Liquid Glass around contextual controls and status, not as a substitute for semantic hierarchy. Keep values readable, controls accessible, and event visualizations stable under high input rates.

## Step 9: Add bounded on-device AI

A safe AI route receives a redacted, user-approved snapshot:

endpoint capabilities + observed controls + app action catalog -> typed proposal -> validation -> user review -> deterministic apply

The model may propose labels, mappings, explanations, transforms, or practice summaries. The deterministic validator owns endpoint identity, protocol compatibility, ranges, persistence, and sends. Store the proposal and the user’s accepted changes so the result is explainable and undoable.

## Step 10: Proof gates

Before calling the route ready, record:

- build and target configuration;
- physical endpoint discovery and removal;
- MIDI 1 receive/send;
- MIDI 2 UMP receive/send where claimed;
- protocol conversion behavior;
- high-rate event handoff and overflow;
- BLE pairing/service/permission/reconnect if supported;
- network session/permission/peer lifecycle if supported;
- virtual endpoint interoperability if supported;
- audio session/output proof if audio is claimed;
- accessibility, Dynamic Type, VoiceOver, keyboard/controller, and reduced-motion behavior;
- signed device/TestFlight evidence for the actual release target.

## Sources

- [CoreMIDI](https://developer.apple.com/documentation/coremidi/)
- [MIDI Services](https://developer.apple.com/documentation/coremidi/midi-services)
- [Incorporating MIDI 2 into your apps](https://developer.apple.com/documentation/coremidi/incorporating-midi-2-into-your-apps)
- [MIDI input port with protocol](https://developer.apple.com/documentation/coremidi/midiinputportcreatewithprotocol%28_%3A_%3A_%3A_%3A_%3A%29)
- [MIDI receive block](https://developer.apple.com/documentation/coremidi/midireceiveblock)
- [MIDINetworkSession](https://developer.apple.com/documentation/coremidi/midinetworksession)
- [MIDI Bluetooth](https://developer.apple.com/documentation/coremidi/midi-bluetooth)
- [MIDI Thru Connection](https://developer.apple.com/documentation/coremidi/midi-thru-connection)
- [MIDICIDeviceManager](https://developer.apple.com/documentation/coremidi/midicidevicemanager)
- [AVFAudio](https://developer.apple.com/documentation/avfaudio)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nslocalnetworkusagedescription)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

***
