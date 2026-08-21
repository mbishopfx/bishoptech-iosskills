# Device and Companion Capability Contracts

## Physical capabilities are state machines

Camera, microphone, location, motion, haptics, NFC, Bluetooth, Nearby Interaction, HomeKit, Watch, CarPlay, and communications are not ordinary data APIs. They depend on hardware, permission, radio/accessory/session state, system ownership, physical context, and often another device or service.

Use a capability contract for every physical route:

`requested -> permission/capability check -> preparing -> active -> interrupted/limited -> stopping -> ended`

The UI should expose enough state for the person to understand whether the app is waiting for authorization, hardware, a companion, a route, an asset, or a server.

## Capability contract matrix

| Capability | Apple route | Start condition | Stop/failure condition | Minimum proof |
| --- | --- | --- | --- | --- |
| Camera/video | AVFoundation, VisionKit | User starts capture; camera usage is explained/granted. | View leaves, interruption, camera unavailable, replacement source. | Physical camera, orientation, frame/backpressure, thermal, privacy. |
| Microphone/audio | AVFoundation, Speech | User records/calls; audio session and permission are ready. | Phone call/route change, interruption, stop, denial, analyzer finish. | Physical mic/speaker, route, interruption, transcript/audio quality. |
| Location | Core Location/MapKit | User asks for location or selected feature requires it. | Accuracy/goal satisfied, authorization change, background end. | Approximate/full accuracy, freshness, power, movement, physical device. |
| Motion | Core Motion | Feature owns a sensor-driven interaction. | View ends, hardware unavailable, sampling no longer needed. | Physical movement, rate, teardown, privacy and battery. |
| Haptics | Core Haptics/UIKit feedback | A visible/accessibility state change has occurred. | Engine reset/stopped, unsupported hardware, interruption. | Physical feel plus visual/audio/VoiceOver equivalent. |
| NFC | Core NFC | Person starts a tag scan and entitlement/usage is present. | Session invalidates, tag leaves, timeout, cancellation. | Physical tag/protocol, entitlement, foreground/session behavior. |
| Bluetooth/accessory | Core Bluetooth/HomeKit | User enters pairing/discovery/control flow. | Radio off, permission, disconnect, trust change, teardown. | Two-device/accessory protocol, reconnect, side-effect safety. |
| Proximity | Nearby Interaction | User starts a session and exchanges a valid token. | Session ends, token invalid, peer leaves, unsupported hardware. | Two physical devices, permission/token lifecycle, spatial behavior. |
| Watch | WatchConnectivity | Session activation and pairing state are known. | Not reachable, app inactive, account switch, queued transfer failure. | Two-device activation, context/event/file semantics, idempotency. |
| Vehicle | CarPlay | Vehicle connection and approved scene/category are available. | Vehicle disconnects, scene resigns, driver-attention constraint. | CarPlay simulator plus equipped vehicle where behavior matters. |
| Calling/communication | CallKit, PushKit, LiveCommunicationKit | Real communication service and required configuration are ready. | Call ends, provider failure, audio route/interruption, server mismatch. | System call UI, audio, APNs/server state, physical device, release policy. |

## Permission is not capability

A granted permission does not mean the hardware is present, the radio is on, the accessory is trusted, the language/asset is installed, the account is available, or the service can deliver. Conversely, an available device capability does not authorize access to personal data.

Keep these values separate:

- permission/authorization;
- hardware support;
- system service enabled state;
- session/connection state;
- data/input readiness;
- user intent and current ownership;
- physical-world side-effect authorization;
- server/account/entitlement state.

## Lifecycle rules

### Camera, audio, and sensors

Configure capture on the documented serial/session queue, keep the main actor for UI state, and stop the resource when the feature no longer owns it. Define frame/audio backpressure before adding Vision/Core ML or Speech. A preview can remain responsive while the latest inference result is stale, but the UI must say so.

For motion and haptics, sample or play only while the feature needs it. A haptic supplements visible and accessibility feedback; it cannot be the only confirmation of saving, unlocking, payment, or completion.

### Radios, accessories, and proximity

Discovery is not identity or trust. Define the protocol, ownership, pairing/trust state, reconnect behavior, timeout, and physical side-effect policy. Do not let a model, stale widget, or ambiguous gesture directly control a device without deterministic authorization and a user-visible state.

### Watch and CarPlay

WatchConnectivity transports have different semantics: latest context, queued user information, immediate messages, and file transfers are not interchangeable. CarPlay templates are hosted by the system and must respect the supported category, connection scene, and driver-attention constraints. The phone app remains the source of truth unless the feature explicitly defines a companion-owned projection.

### Communication surfaces

CallKit, PushKit, and LiveCommunicationKit are specialized communication routes, not generic background messaging. Tie provider actions to real service state, handle audio route/interruption, and keep APNs/server/account evidence distinct from local provider code. Do not register specialized VoIP delivery for ordinary notifications.

## Data and trust contract

Every physical result or companion message should include:

| Field | Why it matters |
| --- | --- |
| Stable source/session ID | Prevents a stale event from overwriting a newer session. |
| Captured/received time | Distinguishes current, delayed, and replayed state. |
| Device/accessory identity | Identifies the source without treating discovery as trust. |
| Authorization/trust state | Records why the app is allowed to read or act. |
| Quality/freshness | Accuracy, route, confidence, RSSI, sensor status, or stale marker. |
| User confirmation | Records approval for a physical or external side effect. |
| Idempotency/replay policy | Prevents duplicate writes, commands, calls, or transfers. |
| Retention/deletion | Defines what raw input and derived data survive. |

## Proof matrix

| Evidence level | What it can prove |
| --- | --- |
| Source/compile | API shape, import, availability annotation, and configuration intent. |
| Preview/unit test | Pure state mapping, deterministic validation, mock protocol behavior. |
| Simulator | UI/container behavior and selected simulated system route; not physical sensor/radio/thermal proof. |
| One physical device | Hardware/session/permission/audio/camera/sensor behavior for that device/build. |
| Two devices/accessory/vehicle | Pairing, radio, Watch, Nearby, Bluetooth, CarPlay, or communication interaction. |
| Signed artifact/system surface | Entitlement, extension, APNs, App Intent, widget/control, Live Activity, or provider behavior in the configured environment. |
| Production/service | Server, account, catalog, APNs, telephony, WeatherKit, or other external delivery only when observed in production. |

Do not use a simulator screenshot, a connected-but-unused accessory, or a green unit test as evidence for a physical-world claim.

## Sources

- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [Audio and video capture](https://developer.apple.com/documentation/avfoundation/audio-and-video-capture)
- [Core Motion](https://developer.apple.com/documentation/coremotion/)
- [Core Haptics](https://developer.apple.com/documentation/corehaptics/)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction/)
- [Core NFC](https://developer.apple.com/documentation/corenfc/)
- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth/)
- [HomeKit](https://developer.apple.com/documentation/homekit/)
- [WatchConnectivity](https://developer.apple.com/documentation/watchconnectivity/)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [CallKit](https://developer.apple.com/documentation/callkit/)
- [PushKit](https://developer.apple.com/documentation/pushkit/)
- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [Core Location UI](https://developer.apple.com/documentation/corelocationui)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
