# Peer-device pairing and system-picker design

Device discovery is a trust interaction before it is a networking interaction. A person is deciding which device may see a service, receive a file, control a screen, or remain available for future connections. The design should make that decision legible, bounded, and reversible.

The native shell should follow this sequence:

~~~text
explain the outcome
-> check support
-> present the system pairing surface
-> confirm what was selected
-> show pairing versus connection versus acknowledgement
-> offer a reversible forget/revoke action
~~~

Do not recreate Apple’s device-picker UI. Use DeviceDiscoveryUI’s system surface and spend the app-owned design effort on context, state, safety, and recovery.

## Design the trust moment

Before showing a pairing button, answer three questions in plain language:

1. What will this connection let the person do?
2. What data or commands can cross the link?
3. Can the person remove access later?

Good entry copy is specific:

- “Pair with another copy of this app to move a draft.”
- “Make this iPad available for the presentation controller.”
- “Add a nearby receiver for playback.”

Avoid vague copy such as “Connect devices” when the actual effect is remote control, file transfer, or persistent access. If the route uses permanent access, say so before the person confirms.

## Publisher and subscriber surfaces

| Role | Native surface | App-owned context |
| --- | --- | --- |
| Publisher | DevicePairingView or DDDevicePairingViewController | What this device will advertise, allowed service, access scope, and how to stop being discoverable |
| Subscriber | DevicePicker or DDDevicePickerViewController | Why the person is choosing a peer, what the app will do after selection, and how to cancel |
| Connected | App-owned status view | Peer identity, transport state, last acknowledgement, pending operation, and retry |
| Revoked | App-owned recovery view | Access removed, local data retained or deleted, and next pairing step |

DevicePicker is a full-screen modal system surface. The label that opens it should remain a normal semantic control. A GlassEffectContainer around the surrounding action row may group the action and status, but it should never hide the system picker’s purpose or make a status badge appear tappable when it is not.

## State language that does not overclaim

Use separate labels for separate facts:

| State | User-facing language | Do not say |
| --- | --- | --- |
| unsupported | “This device can’t use this pairing method.” | “No devices found” |
| configured | “Ready to add a device.” | “Connected” |
| pairing | “Choose a device in the system window.” | “Pairing complete” |
| paired | “Added for future connections.” | “Online” |
| browsing | “Looking for the selected service.” | “The device is ready” |
| selected | “Device selected. Establishing a secure connection.” | “Transfer started” |
| connecting | “Connecting to [peer].” | “Sent” |
| ready | “Connected. You can now [specific action].” | “Completed” |
| acknowledged | “The other device confirmed [specific operation].” | “Delivered everywhere” |
| degraded | “The connection is unavailable. Your local work is safe.” | “Data lost” |
| revoked | “Access was removed. Pair again to continue.” | “Device deleted” |

The distinction matters most for AI-assisted actions. A generated command is not accepted, an accepted command is not completed, and a transport callback is not domain truth.

## Pairing screen anatomy

An app-owned pairing entry screen can be compact:

1. A title that names the outcome.
2. A one-sentence explanation of the service and data boundary.
3. A primary semantic button that opens DevicePairingView or DevicePicker.
4. A small current-state row with an accessible label.
5. A secondary “What happens next?” disclosure.
6. A peer-management destination for forget/revoke.

Do not place a custom device grid beside the system picker and imply that the custom grid is authoritative. If the app keeps a paired-device projection, label it as “Devices you added” and refresh it from WAPairedDevice.allDevices or the app-service state.

## Access scope and reversibility

Default and permanent DeviceDiscoveryUI access are different product decisions. Make the choice visible:

| Product pattern | Recommended experience |
| --- | --- |
| One-time transfer | Use default access, confirm the selected peer, show a completed/failed transfer result, and avoid retaining a peer row unless the person asks |
| Repeated controller | Explain that the peer will remain available, provide a named peer list, show the last connection state, and expose Forget |
| Household or studio device | Explain who can discover the device, keep the service narrow, provide a stop-advertising control, and avoid revealing personal data in the device name |
| Shared presentation or game | Make the session owner and session end visible; do not treat persistent pairing as persistent session authorization |

Forget must affect the app’s local association and, where the framework exposes the relevant access boundary, the system-managed relationship. It should also cancel pending operations and prevent an old endpoint from being reused.

## Liquid Glass composition

The native Apple-like treatment is restrained:

- use standard SwiftUI controls for the primary pairing action;
- let standard bars, sheets, alerts, and system pickers receive their platform treatment;
- use a single glass group for app-owned status and action controls when grouping improves hierarchy;
- keep peer identity, access scope, and operation state outside decorative blur;
- use a material only when it helps separate controls from content;
- avoid applying glass to every row, badge, icon, or decorative container;
- do not use translucency to disguise uncertainty or a stale connection.

If the screen contains a large peer preview or transfer illustration, let the content remain the visual anchor. Glass should support controls around the content, not compete with the system-owned discovery moment.

When a state changes from paired to connected, use an identity-preserving transition: the peer row remains the same semantic element while its status, action, and progress update. Avoid morphing a “Pair” button into a “Forget” action without a clear label change and VoiceOver announcement.

## Accessibility and alternate input

Pairing must be usable without relying on proximity, color, or animation:

- give the entry button an action-oriented label;
- expose whether the system picker is available and why a fallback is shown;
- make peer names and roles part of the accessibility value, not only visual text;
- announce connection and acknowledgement changes without repeatedly interrupting the user;
- keep touch targets large enough for finger and pointer input;
- support Dynamic Type without truncating the service purpose;
- respect Reduce Motion and Reduce Transparency;
- use shape, text, and state labels in addition to green/red color;
- make Forget a separate, discoverable action with confirmation;
- test VoiceOver rotor order, Voice Control phrases, Switch Control scanning, and Full Keyboard Access where supported.

The fallback view should be actionable. “Not supported” is not enough; say whether the device is unsupported, the service is unavailable, the required capability is absent, or the person needs to use another device.

## Error and recovery design

Map the transport state into a small number of user actions:

| Failure | What the person needs | Suggested action |
| --- | --- | --- |
| unsupported host | A clear reason | Use another device or another route |
| invalid target configuration | A developer/support explanation, not a user retry loop | Fix target capability, entitlement, or service declaration |
| pairing canceled | No error alarm | Return to the entry surface |
| access revoked | A safe local-data statement | Pair again or continue locally |
| peer disappeared | Confidence that local state remains | Retry, choose another peer, or save locally |
| protocol mismatch | A version or compatibility explanation | Update the peer or use a compatible route |
| malformed or unauthorized message | No raw payload dump | Reject, log a redacted category, and offer a safe recovery |
| timeout after send | Uncertain result | Show “Needs confirmation” and reconcile before retrying |

Never make a retry button blindly repeat a remote mutation. Use an operation ID, reconcile with the peer, or ask the person whether to retry when the result is unknown.

## Multi-device and companion layouts

For a two-device experience, decide which device owns each truth:

| Concern | Owner | Projection |
| --- | --- | --- |
| Pairing relationship | System plus app configuration | Added-peer list |
| Session membership | App domain/session layer | Connected status |
| Current command | Originating app/domain | Pending operation row |
| Completion | Receiving domain or acknowledged protocol | Completed result |
| Device health | Remote device or accessory protocol | Last-seen and diagnostics |
| Local history | Each device’s local store or deliberate sync authority | History list |

Do not mirror every internal state to both devices. Send only the events needed by the product and make stale projections obvious. A Live Activity, widget, or watch companion can show a projection, but it cannot turn a transport callback into proof of completion.

## AI review shell

If on-device AI helps select a peer or draft an action, keep the review shell deterministic:

1. Show the user’s request.
2. Show the resolved peer name and stable app-owned identifier.
3. Show the service and data/action scope.
4. Show the model’s proposal separately from verified facts.
5. Require an explicit approval for transfer, remote control, or persistent pairing.
6. Validate the proposal against the current paired-device projection and protocol schema.
7. Show transport acknowledgement and domain completion separately.

The model may say “your office display,” but the app must resolve that phrase against current, user-visible peer records. If resolution is ambiguous, show choices. If the peer is not paired or the service is not available, the proposal remains unexecutable.

## Platform-specific review

DeviceDiscoveryUI spans iOS, iPadOS, watchOS, tvOS, and Mac Catalyst according to the relevant provider and route. The tvOS application-service path has additional constraints around Apple TV 4K, universal purchase, bundle identity, account visibility, and one-device connection behavior. Do not promise one layout or one pairing story across platforms.

For iPad, support side-by-side or stage-style presentation without shrinking the system picker into an unusable panel. For watchOS, keep the pairing explanation short and move complex protocol or data review to a companion app when appropriate. For Mac Catalyst, check pointer, keyboard, windowing, and entitlement behavior separately.

## Design evidence checklist

- [ ] The entry screen names the outcome, service, and data boundary.
- [ ] The system picker is used for pairing rather than copied.
- [ ] Unsupported and unavailable states have useful fallbacks.
- [ ] Default versus permanent access is deliberate and explained.
- [ ] Paired, reachable, connected, acknowledged, stale, and revoked states are distinct.
- [ ] Glass is limited to app-owned functional groups and does not obscure identity or uncertainty.
- [ ] Dynamic Type, VoiceOver, Voice Control, Switch Control, Reduce Motion, and Reduce Transparency were tested.
- [ ] Forget/revoke cancels pending work and removes stale associations.
- [ ] AI proposals show verified peer facts and require approval before side effects.
- [ ] A physical two-device run proves the system picker, pairing, transport, and domain acknowledgement separately.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [Default device-pairing access](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess/default?changes=_6)
- [Permanent device-pairing access](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess/permanent?changes=_7)
- [Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware?changes=_7)
- [Adopting Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware/Adopting-Wi-Fi-Aware)
- [Connecting devices for peer-to-peer Wi-Fi](https://developer.apple.com/documentation/wifiaware/connecting-paired-devices)
- [WACapabilities](https://developer.apple.com/documentation/wifiaware/wacapabilities)
- [WAPairedDevice.allDevices](https://developer.apple.com/documentation/wifiaware/wapaireddevice/alldevices)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
