# SwiftUI Core Bluetooth and nearby-accessory review design

Design a Bluetooth surface as a trustworthy session instrument: show what the app found, whether it has verified the accessory, what data is current, what action will be sent, and what evidence will confirm the physical result.

This page is the design companion to [SwiftUI Core Bluetooth and nearby-accessory review](../42-framework-deep-dives/94-swiftui-core-bluetooth-and-nearby-accessory-review.md), [Bluetooth setup and device trust design](46-bluetooth-setup-and-device-trust-design.md), and [Core Bluetooth transport and device-command route](../50-capability-recipes/49-core-bluetooth-transport-and-device-command-route.md).

## The design contract

The primary screen must make these facts visible:

1. Bluetooth permission and radio state.
2. Whether the app is scanning, connecting, discovering, handshaking, ready, or stale.
3. Which physical accessory the person selected.
4. Which service or characteristic the screen represents.
5. Whether a value is reported, last known, desired, pending, or unknown.
6. What will happen if the person activates the control.

Use this hierarchy:

~~~text
permission and radio context
  -> discovery/session context
  -> verified device identity
  -> typed service state
  -> native control or read-only value
  -> command result and physical reconciliation
  -> detail/support/AI review
~~~

Do not make a scan list look like a trusted device list. Discovery is a candidate stage, not the end of setup.

## State language

| Transport state | User-facing language | Design action |
| --- | --- | --- |
| Permission not determined | “Bluetooth access is needed to find this device.” | Explain the task before the system prompt. |
| Denied/restricted | “Bluetooth access is off for this app.” | Provide Settings/recovery and a non-Bluetooth path if one exists. |
| Powered off | “Turn on Bluetooth to continue.” | Disable unsafe controls; keep context. |
| Scanning | “Looking for nearby devices.” | Show cancel and a concise filter/context. |
| Candidate found | “Device found — not connected.” | Show name plus setup/trust next step. |
| Connecting | “Connecting to device.” | Preserve selection; prevent duplicate connects. |
| Discovering | “Checking supported features.” | Do not present controls before GATT discovery. |
| Verifying | “Verifying accessory.” | Keep protocol identity distinct from display name. |
| Ready | “Connected and ready.” | Show typed state, last update, and controls. |
| Stale | “Last known value from …” | Offer refresh/reconnect; avoid current language. |
| Sending | “Sending command.” | Do not animate to a reported state early. |
| Awaiting report | “Waiting for device response.” | Distinguish transport completion from physical outcome. |
| Failed | “Couldn’t update device.” | Preserve prior reported state and provide recovery. |

Use text and semantics with color, blur, tint, and motion. Do not rely on a green dot or a glass glow to communicate trust or success.

## Discovery and selection

The scan screen should be short-lived and intentional:

- state why the app is scanning;
- filter by required service UUIDs when possible;
- show a user-friendly name only as candidate metadata;
- show a relative signal clue only when it helps selection and label it as approximate;
- expire candidates or mark them stale;
- stop scanning as soon as the session no longer needs it;
- make cancel discoverable.

Avoid:

- an endless animated radar;
- a full table of raw UUIDs;
- sorting by RSSI as if it proves nearest physical identity;
- keeping a broad scan alive behind a detail view;
- presenting a discovered display name as the verified product name.

If pairing or protocol verification is required, show the next step instead of silently connecting and exposing commands.

## Device identity and trust

Use a two-stage identity surface:

### Candidate

Show:

- candidate name;
- approximate discovery context;
- service family or product category;
- “Not verified” or equivalent status;
- setup or connect action.

### Verified session

Show:

- app-owned product identity or serial after protocol validation;
- session status;
- protocol version when it matters;
- last report time;
- disconnect or forget route;
- support details without exposing secrets.

A Bluetooth UUID, local name, manufacturer data, or RSSI can help find a device but cannot automatically prove ownership or authorization. If the accessory provides a challenge-response or protected identity characteristic, put the verification transition in the state model.

## Service and value surfaces

A strong service card contains:

- feature name;
- device identity and room/context if the product has one;
- typed value and unit;
- reported/desired distinction;
- last update or freshness;
- reachability/session state;
- one semantic primary control;
- details for protocol or secondary settings.

Choose controls from protocol semantics:

| Data shape | UI | Required copy |
| --- | --- | --- |
| Reported Boolean plus writable endpoint | Toggle | Current reported value and pending state. |
| Bounded numeric value | Slider/Stepper | Unit, range, and precision. |
| Enumeration | Picker | Current label and supported options. |
| One-shot command | Button | Exact action and result state. |
| Stream or notification | Text/chart/status | Sample time, subscription state, and stale behavior. |
| Opaque bytes | Diagnostic/read-only | Never invent a user-facing control. |

Do not update the reported value merely because a person moved a slider. Show desired intent as pending until the accessory reports a result.

## Liquid Glass without transport theater

Liquid Glass can group related context and actions:

~~~text
GlassEffectContainer
  context: accessory identity and session state
  state: typed value and freshness
  action: one or two related controls
  result: sent, reported, failed
~~~

Keep the material behind functional groups:

- use a small glass group for related controls;
- keep identity and current state readable;
- let a failed command settle into a visible error state;
- do not animate a glass morph as a substitute for a device response;
- provide system-material or opaque fallback for reduced transparency and unsupported targets;
- keep the same semantics in high contrast and large text;
- do not use a glass surface to make a pairing flow look like it is already trusted.

The visual result should feel like a focused Apple-native utility, not a translucent dashboard that hides transport uncertainty.

## Connection and reconnect design

Connection is a session, not a permanent Boolean:

~~~text
idle -> scanning -> candidate
candidate -> connecting -> discovering -> verifying -> ready
ready -> sending -> awaiting report -> ready
ready -> disconnected -> reconnecting -> ready
any -> powered off / denied / unsupported / failed
~~~

When disconnected:

- preserve device identity and last-known state;
- make the stale boundary visible;
- allow a user-initiated reconnect;
- avoid infinite retries;
- show if the process has no supported background authority;
- restore focus after a successful reconnect.

Do not show the accessory as “ready” because a CBPeripheral object still exists in memory.

## Setup and secure commands

For a device setup flow, order the experience:

1. Explain what the accessory does.
2. Ask for Bluetooth permission in context.
3. Scan for a bounded session.
4. Identify a candidate.
5. Show any physical setup or pairing step.
6. Verify the protocol identity.
7. Expose typed capabilities.
8. Require confirmation for physical/security side effects.

Confirmation should identify the device, command, and consequence. Avoid generic “Are you sure?” copy. If a command controls a lock, medical sensor, heater, vehicle, or other high-consequence system, make the trust and safety policy more prominent than the glass treatment.

## AI review design

Use on-device AI as an interpretation layer over selected typed state:

~~~text
selected accessory
  -> current verified session
  -> typed service snapshot
  -> model explanation or command proposal
  -> exact UUID/type/value validation
  -> review
  -> explicit apply
~~~

The review surface should display:

- selected accessory and session;
- source time and protocol revision;
- exact service/characteristic;
- proposed value or command;
- warnings for stale, unreachable, or ambiguous state;
- whether the command receives a response;
- Apply and Cancel.

Never use an AI response as proof that a device is nearby, safe, authenticated, or physically changed. Do not include pairing keys, credentials, raw secrets, or unrelated discovery results in the model context.

## Background and restoration design

Do not promise “always connected” based on a background mode. Background execution has different scanning, advertising, wake, and timing behavior, and the system can terminate the process. Design the visible product promise around:

- a user-started active session;
- a bounded background monitor when the target supports it;
- an explicit restored session with last checkpoint;
- a reconnect route when the accessory is unavailable.

If the app wakes in the background, the user should not see a false foreground dashboard later. Show the last background event time and whether the device was actually reconnected and reconciled.

## Accessibility and alternate input

Make the transport state accessible:

- label the device and service;
- include “not verified,” “connected,” “stale,” “sending,” and “awaiting response”;
- expose the actual reported value as the accessibility value;
- announce a meaningful result after notification/reconciliation;
- keep focus stable after scan results insert;
- support keyboard and pointer selection on iPad;
- test Voice Control names for device and command;
- use Dynamic Type and avoid truncating the primary action;
- provide reduced-motion fallback for connection transitions.

An accessibility action must not bypass the same protocol, validation, and confirmation gate used by the visible Button or Toggle.

## Privacy and energy

Bluetooth discovery can expose nearby devices and behavior patterns. Keep the product’s collection narrow:

- do not log full advertisement payloads by default;
- do not upload discovery feeds for analytics;
- redact identifiers in user-visible screenshots and support logs;
- explain why the app needs Bluetooth;
- stop scan and disconnect when the session ends;
- use service filters, targeted discovery, and notification subscriptions;
- avoid allow-duplicates unless the product needs measurement;
- keep background processing short and relevant.

The design should make the battery cost legible when a person starts a long-running monitoring session.

## Platform adaptation

| Target | Design priority |
| --- | --- |
| iPhone | Fast scan/connect/control session with physical accessory context. |
| iPad | Wider discovery/detail composition, keyboard/pointer, split view. |
| watchOS companion | Glanceable, short commands; do not assume full GATT discovery and setup parity. |
| Two iOS devices | Explicit central/peripheral roles and a shared protocol proof. |
| Widget/system surface | Only project state that is safe, fresh enough, and meaningful outside the active session. |

The platform matrix must record role availability, background behavior, and physical test hardware separately.

## Design review checklist

- Is Bluetooth requested only in context of a concrete feature?
- Can a person distinguish candidate, verified, ready, stale, and disconnected?
- Does the primary control show reported versus desired state?
- Is write-without-response never described as delivery proof?
- Are device identity and protocol trust visible before commands?
- Does Liquid Glass organize state without hiding uncertainty?
- Does AI produce a reviewable proposal with exact targets and values?
- Are pairing keys, credentials, and raw discovery data excluded from prompts and logs?
- Does background/restoration behavior match the actual target?
- Can VoiceOver, Dynamic Type, keyboard, pointer, reduced motion, and increased contrast complete the task?
- Is there physical accessory evidence for any claim about the device effect?

## Sources

- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [About Core Bluetooth](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/AboutCoreBluetooth/Introduction.html)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [CBManager](https://developer.apple.com/documentation/corebluetooth/cbmanager)
- [CBManagerAuthorization](https://developer.apple.com/documentation/corebluetooth/cbmanagerauthorization)
- [CBManagerState](https://developer.apple.com/documentation/corebluetooth/cbmanagerstate)
- [CBPeripheral](https://developer.apple.com/documentation/corebluetooth/cbperipheral)
- [CBService](https://developer.apple.com/documentation/corebluetooth/cbservice)
- [CBCharacteristic](https://developer.apple.com/documentation/corebluetooth/cbcharacteristic)
- [CBDescriptor](https://developer.apple.com/documentation/corebluetooth/cbdescriptor)
- [CBPeripheralManager](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager)
- [Core Bluetooth Background Processing for iOS Apps](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/CoreBluetoothBackgroundProcessingForIOSApps/PerformingTasksWhileYourAppIsInTheBackground.html)
- [Best Practices for Interacting with a Remote Peripheral Device](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/BestPracticesForInteractingWithARemotePeripheralDevice/BestPracticesForInteractingWithARemotePeripheralDevice.html)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
