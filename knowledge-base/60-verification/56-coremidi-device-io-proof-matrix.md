# CoreMIDI device I/O proof matrix

Use this matrix to separate a route that is documented from one that is compiled, connected, observable, accessible, and releasable. CoreMIDI evidence should name the target, endpoint, protocol, transport, and device rather than only saying “MIDI works.”

## Evidence levels

| Level | What it can establish | What it cannot establish |
| --- | --- | --- |
| Source inspection | API names, object model, documented lifecycle, privacy requirements | Availability for the selected target, accessory behavior, latency, successful audio |
| Compile | Imports, symbol availability, type signatures, target configuration | Physical endpoint discovery, timing, permissions, system route behavior |
| Unit/fixture | Normalization, validation, mapping, UMP parsing, replay determinism | Bluetooth/network hardware, real callback pressure, audio output |
| Simulator/preview | SwiftUI hierarchy, empty/error states, accessibility labels, visual transitions | USB/BLE MIDI, physical timing, audio route, device removal |
| Physical device | Endpoint discovery, callback/send path, haptics/audio if applicable, permission recovery | Every device family, every OS version, App Store delivery |
| Signed/TestFlight | Entitlements, privacy manifests/strings, release-build behavior, real install | Universal compatibility or production success without monitoring |

## Route matrix

| Claim | Minimum evidence | Failure and recovery cases |
| --- | --- | --- |
| The app discovers MIDI endpoints | Named iOS target enumerates devices/entities/endpoints on a physical device | No devices, duplicate names, stale selection, endpoint removed |
| The app identifies source and destination roles | UI and logs show the actual endpoint role and stable identity | Source chosen as destination, name collision, external device differs from local device |
| MIDI input works | Physical source sends known MIDI 1 and/or MIDI 2 messages; app records normalized events with timestamps and provenance | Burst input, malformed/unsupported message, callback queue pressure, event loss |
| MIDI output works | Physical destination receives a known test message and app records the send result | Destination removed, unsupported protocol, invalid channel/group/range, rate limit |
| MIDI 1 compatibility works | Named MIDI 1 source/destination test with expected packet representation | Conversion loses precision or unsupported message types |
| MIDI 2 UMP works | Named MIDI 2-capable route sends/receives event lists and verifies group/channel/message fields | Device accepts transport but ignores unsupported profile/property |
| MIDI-CI is supported | Bidirectional physical device test confirms discovered device/profile/property state | Device does not respond, profile changes, partial capability |
| Virtual endpoint route works | A separate MIDI-aware app or named test target observes the virtual source/destination | No external consumer, endpoint disappears, app background lifecycle |
| Network MIDI works | Two physical devices join the intended MIDINetworkSession and exchange labeled events | Local-network denial, peer removal, duplicate sources, session disabled |
| Bluetooth MIDI works | Supported BLE MIDI peripheral is paired or explicitly discovered, service/characteristic validated, and CoreMIDI connection is active | Bluetooth denial, missing service, disconnect, reconnect, background/foreground |
| Audio rendering is claimed | AVAudioSession and the audio engine/player show active output on a named route after a known MIDI action | Audio interruption, route change, silent mode, headphones/Bluetooth audio, engine stopped |
| Real-time safety is claimed | Instruments/logging and stress fixture show bounded callback work and a measurable handoff policy | Allocation, lock contention, actor hop, disk/network/model work in receive block |
| Recording is claimed | Start/stop, event ordering, timestamps, protocol, and persistence are verified with replay | Clock discontinuity, app termination, storage failure, corrupt payload |
| Mapping is claimed | Learn/confirm/cancel/conflict/undo flow works with two controls and a disconnected device | Duplicate binding, endpoint change, range mismatch, accidental send |
| AI mapping help is claimed | Fixed snapshot produces typed proposal; validator rejects invalid endpoint/protocol/range; user approval is required | Prompt injection in device labels, hallucinated controls, stale snapshot, model unavailable |
| Native design is claimed | SwiftUI/Glass states are checked in light/dark, Dynamic Type, VoiceOver, reduced motion, keyboard/controller input | Color-only status, unreadable event rate, focus trap, motion discomfort |
| Release readiness is claimed | Signed build installed on target device with privacy strings, capabilities, and route behavior verified | TestFlight metadata mismatch, entitlement change, device/OS coverage gap |

## Environment record

Record an environment row for every physical run:

- app version/build and git revision;
- iOS version, device model, SDK/Xcode version;
- endpoint model, firmware if available, transport, source/destination role;
- protocol requested and observed;
- local-network/Bluetooth authorization state;
- AVAudioSession category/route if audio is involved;
- test fixture or exact physical gesture/message;
- expected result, observed result, logs/artifacts, and follow-up.

## Safety checks

Never infer any of these from a single successful callback:

- low latency;
- zero event loss;
- MIDI 2 profile support;
- correct audio rendering;
- safe SysEx behavior;
- network trust;
- universal accessory compatibility;
- accessibility;
- release readiness.

Add bounded queue metrics, endpoint-change logs, and a visible recovery state before expanding the route.

## Sources

- [CoreMIDI](https://developer.apple.com/documentation/coremidi/)
- [MIDI Services](https://developer.apple.com/documentation/coremidi/midi-services)
- [Incorporating MIDI 2 into your apps](https://developer.apple.com/documentation/coremidi/incorporating-midi-2-into-your-apps)
- [MIDI event packets](https://developer.apple.com/documentation/coremidi/midieventpacket)
- [MIDI receive block](https://developer.apple.com/documentation/coremidi/midireceiveblock)
- [MIDINetworkSession](https://developer.apple.com/documentation/coremidi/midinetworksession)
- [MIDI Bluetooth](https://developer.apple.com/documentation/coremidi/midi-bluetooth)
- [MIDICIDeviceManager](https://developer.apple.com/documentation/coremidi/midicidevicemanager)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

***
