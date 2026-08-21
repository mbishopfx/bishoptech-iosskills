# SwiftUI Nearby Interaction and spatial-peer review

This deep dive covers the SwiftUI boundary around Nearby Interaction: device and feature capability checks, NISession ownership, discovery-token exchange, peer or accessory configuration, optional distance and direction, transport identity, suspension and invalidation, background limits, spatial review surfaces, local-AI proposals, accessibility, privacy, energy, and physical multi-device proof.

It extends [Core Bluetooth and nearby-accessory review](94-swiftui-core-bluetooth-and-nearby-accessory-review.md), [Nearby Interaction and peer transport](../42-framework-deep-dives/02-homekit-bluetooth-and-nearby.md), [Nearby Interaction transport route](../50-capability-recipes/36-nearby-interaction-peer-transport-route.md), and [Core Bluetooth transport and device-command route](../50-capability-recipes/49-core-bluetooth-transport-and-device-command-route.md).

## Spatial interaction is a composed route

Nearby Interaction is not peer discovery, authentication, messaging, or a general-purpose location service. It reports relative positioning for a participating peer or accessory after the app establishes the required configuration and token/data-link exchange.

Use this sequence:

~~~text
target, privacy strings, capability, and device support
  -> peer or accessory discovery through an agreed transport
  -> NISession creation and delegate queue
  -> temporary discovery-token or accessory configuration exchange
  -> NINearbyPeerConfiguration or NINearbyAccessoryConfiguration
  -> NISession.run
  -> optional permission prompt and session start
  -> nearby-object updates, suspension, removal, or invalidation
  -> typed spatial snapshot with freshness and capability flags
  -> SwiftUI status, guidance, or review surface
  -> optional local-AI proposal
  -> deterministic validation and explicit user action
  -> physical multi-device, system, archive, and release evidence
~~~

Keep authorities separate:

| Fact | Owner | Product meaning |
| --- | --- | --- |
| Device capability | Nearby Interaction runtime | This target/device may support a requested feature. |
| Discovery token | NISession | Temporary token for a session/device exchange, not a product identity. |
| Peer transport | Network, Multipeer Connectivity, Core Bluetooth, or another agreed link | Moves tokens/configuration and app messages. |
| Nearby object | Nearby Interaction | A participating peer/accessory with optional relative measurements. |
| Distance or direction | UWB/interaction result | A measurement that can be unavailable, stale, noisy, or environment-sensitive. |
| Session state | NISession delegate | Started, suspended, removed, invalidated, or awaiting configuration. |
| AI output | On-device model | Explanation or proposal without spatial authority. |
| Domain effect | Deterministic app boundary | The only place that commits an action. |

Proximity, direction, or a token must not silently become identity, consent, secure access, occupancy, safety clearance, or a physical command.

## Target configuration and privacy

A target using Nearby Interaction should have a concrete NSNearbyInteractionUsageDescription. Explain why the app needs to share relative position with nearby devices or accessories. The system permission can be declined; userDidNotAllow is a normal failure route that points the person to Settings.

The transport has its own requirements:

- Multipeer Connectivity discovery can require NSBonjourServices and NSLocalNetworkUsageDescription.
- A Network Framework or Bonjour route still needs the target’s local-network privacy policy where applicable.
- A Core Bluetooth accessory route has its own Bluetooth usage description and capability/background contract.
- An accessory protocol can require a partner specification, data link, and device pairing.
- Background Nearby Interaction requires the appropriate Uses Nearby Interaction capability and does not make a foreground session universally persistent.

Keep the Nearby Interaction usage explanation separate from local-network, Bluetooth, camera-assistance, and ARKit explanations. A single generic “nearby” string does not explain every protected resource.

## Capability and platform gates

Apple’s current Nearby Interaction guidance recommends checking NISession.deviceCapabilities for the feature required by the app. Depending on the target and device, capabilities may include precise distance, direction, extended distance, accessory interaction, or other supported features. The peer token also exposes device capabilities, so the app can reject an incompatible peer before running a configuration.

Do not use one Boolean for the whole route:

| Gate | Example state |
| --- | --- |
| Nearby Interaction supported | Supported, unsupported platform, or unknown. |
| Direction measurement | Available or distance-only. |
| Precise distance | Available, unavailable, or peer-incompatible. |
| Extended distance | Supported only on the required OS/device combination. |
| Camera assistance | Requires ARKit and camera conditions; optional. |
| Peer capability | The exchanged token can describe what the other device supports. |
| Accessory data link | Connected, paired, configured, or unavailable. |
| Background route | Foreground only, Bluetooth-paired, or Live Activity-capable. |
| Mac Catalyst/visionOS | Target-specific limitations; do not infer from iPhone behavior. |

The Nearby Interaction documentation notes that a compatible iPad or iPhone app running in visionOS has no effect from these APIs, and that precise distance capability is unavailable in Mac Catalyst. Record the selected platform instead of letting an empty result look like a peer being far away.

## NISession ownership

One NISession represents an interaction between the user’s device and a nearby object. Keep the session in a feature coordinator, not in a SwiftUI row or a transient sheet.

The coordinator owns:

- the NISession;
- its delegate and delegateQueue;
- the current configuration and peer token;
- the transport session that exchanged the token;
- a session generation;
- the current nearby-object snapshot;
- cleanup on stop, suspension, removal, and invalidation.

Assign a delegate queue intentionally. Delegate callbacks can arrive away from the main actor. Normalize the callback into a small spatial value and publish that value to SwiftUI on the MainActor.

A new NISession has a discoveryToken. Apple describes it as a temporary, random identifier unique to the session and used to identify the device that created it. Exchange it only through the intended transport and treat it as sensitive session material. It is not a printed serial number, login identity, cryptographic authorization, or proof that the person selected the intended device.

## Token exchange is a separate trust boundary

For an iPhone-to-iPhone or iPhone-to-Watch peer route:

1. Discover or select a peer using the agreed transport.
2. Create a local NISession and obtain its discoveryToken.
3. Serialize the token using secure coding where the selected transport requires it.
4. Send the token to the selected peer.
5. Receive the peer’s token.
6. Inspect the peer token’s device capabilities.
7. Create NINearbyPeerConfiguration with the peer token.
8. Run that configuration on the local NISession.
9. Wait for start and nearby-object callbacks.
10. Match updates by discovery token and peer-transport identity.

Multipeer Connectivity is shown in Apple’s Nearby Interaction sample routes for discovery and token exchange. Its browser/advertiser flow can invite a nearby device, but an invitation is not authentication. Apple’s current Multipeer Connectivity documentation also marks MCSession deprecated and points new work toward Network Framework, so record the selected transport and SDK availability instead of copying a sample’s transport choice blindly.

For new projects, make the transport adapter replaceable. The token exchange contract should not depend on SwiftUI or assume that a successful local-network connection makes the peer trusted.

## Nearby object measurements

NINearbyObject can contain:

- discoveryToken;
- distance in meters, when available;
- direction vector, when available;
- horizontal angle, when camera assistance and the target support it;
- vertical direction estimate;
- removal or lifecycle context from the delegate.

Distance and direction may be nil or unavailable. A missing direction is not “straight ahead,” and a missing distance is not “zero.” Use typed optionals and a UI state that says unavailable, acquiring, stale, or reported.

Apple explicitly warns that Nearby Interaction does not implement secure ranging. Do not use a distance threshold as secure access, security clearance, proof of consent, or proof that a person is in a room. Environmental factors and line of sight affect detectable range. If the product needs authorization, use authentication and explicit user intent separately.

For a multi-peer session, match a nearby object by its discoveryToken and the configuration’s peerDiscoveryToken. Do not match by array position, display name, RSSI, or the latest callback.

## Session lifecycle

Use an explicit state machine:

~~~text
idle
  -> checkingSupport
  -> discoveringPeer
  -> tokenExchange
  -> awaitingPermission
  -> configured
  -> running
  -> reporting
  -> suspended
  -> removed
  -> invalidated
  -> stopped
~~~

NISessionDelegate provides callbacks for session start, nearby-object updates, object removal, suspension, suspension end, invalidation, and algorithm convergence. Treat each as a state transition:

- sessionDidStartRunning means the session started or resumed; it does not mean a current measurement has arrived;
- didUpdate supplies a new measurement snapshot; preserve timestamp and token;
- didRemove requires clearing or marking the related peer stale;
- sessionWasSuspended requires a stale/unavailable UI and no unsafe action;
- sessionSuspensionEnded requires revalidation before resuming an action;
- didInvalidateWith error requires a bounded recovery path and a new-session policy;
- algorithm convergence guidance is coaching for camera assistance, not a measurement itself.

Stop the session when the feature ends. Do not leave multiple live sessions running without a documented reason; Nearby Interaction can report active-session limits and incompatible peer/configuration errors.

## Accessory configuration

For a third-party accessory, the app first establishes a two-way data link using a technology such as Core Bluetooth, local network, or a secure internet connection. For UWB accessories, the accessory sends configuration data formatted according to the accessory specification. The app creates NINearbyAccessoryConfiguration and runs it. Nearby Interaction can then report accessory updates through the session delegate.

Compare an accessory update’s discoveryToken to accessoryDiscoveryToken when correlating measurements. Keep accessory identity, Bluetooth pairing identity, protocol identity, and Nearby Interaction token identity separate. A paired accessory can still be on an incompatible firmware or wrong product route.

NINearbyAccessoryConfiguration also includes camera-assistance and accessory-specific lifecycle boundaries. Verify exact availability before using any newer accessory or Bluetooth Channel Sounding initializer; beta or future-OS APIs must not be treated as an iOS 26 baseline.

## Background and relaunch

Foreground ranging and background ranging are different claims. Apple’s Nearby Interaction overview says that in the background, ranging can continue with BLE-paired and connected devices. It also documents a newer route in which a Live Activity started as the app goes to the background can allow supported-device ranging, with the appropriate background capability.

For a background claim, prove:

1. the target contains the Uses Nearby Interaction capability;
2. the transport remains connected or the Live Activity path is valid;
3. the NISession lifecycle survives the intended transition;
4. the app handles suspension, relaunch, and invalidation;
5. the user-facing system surface remains accurate;
6. no side effect occurs solely because a stale background measurement arrived.

A capability checkbox, background callback, or Live Activity preview does not prove physical ranging after termination. Test the exact release target on supported devices.

## SwiftUI and Liquid Glass spatial surface

Use a small functional layer over content:

~~~text
peer identity chosen in transport
  -> spatial status group
  -> direction/distance guidance
  -> source and freshness detail
  -> reviewable AI suggestion
  -> explicit action confirmation
~~~

A glass group can contain pause, stop ranging, retry, or open details. Use standard materials or opaque fallback for the spatial content itself when that improves legibility. Do not use glass shine, arrow animation, or proximity color as the only signal for direction, consent, trust, or safety.

A good spatial status card distinguishes:

| State | Copy |
| --- | --- |
| Discovering | Looking for the selected peer. |
| Exchanging | Preparing a temporary spatial session. |
| Waiting | Nearby Interaction permission is required. |
| Unsupported | This device or peer cannot provide the requested capability. |
| Acquiring | Waiting for a usable spatial measurement. |
| Reported | About 1.8 meters; direction available. |
| Partial | Distance available; direction unavailable. |
| Stale | Last measurement received 2.1 seconds ago. |
| Suspended | Spatial updates are paused. |
| Invalidated | Session ended; restart is required. |

For VoiceOver, expose the peer label, distance freshness, direction semantics, capability limitations, and actions in a stable order. A radial arrow is decorative unless its semantic value is also spoken or represented textually.

## Local AI and action boundaries

A local language model can explain “the peer is to your left” from a typed spatial snapshot, draft a navigation instruction, or suggest a next UI step. It must not:

- identify an unknown person from proximity;
- treat distance as authentication or consent;
- invent direction when the framework reports nil;
- convert a stale measurement into current safety;
- unlock, purchase, message, or control a physical device automatically;
- claim that a peer is safe, authorized, or present beyond the measured snapshot.

Attach the source token/session generation, timestamp, capabilities, and missing-value warnings to any proposal. Require a refresh and explicit confirmation for actions that affect the device, another person, an account, or the physical environment.

## Privacy, energy, and proof

Token exchange can reveal that devices are participating in a shared app session. Spatial data can reveal proximity, movement, and location context. Minimize retention, redact tokens and peer IDs from logs, and explain which transport and data stay on-device.

Measure sustained sessions on physical devices:

- ranging update cadence;
- transport messages and token exchange failures;
- session suspension and resume;
- power and thermal state;
- camera-assistance cost where used;
- foreground/background transition;
- stale-result duration;
- accessibility task completion;
- behavior when the peer leaves range or changes orientation.

A simulator can exercise selected UI and transport fixtures, but it does not prove UWB direction, physical distance, camera assistance, accessory interoperability, or thermal behavior.

## Sources

- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NISessionDelegate](https://developer.apple.com/documentation/nearbyinteraction/nisessiondelegate)
- [NIDiscoveryToken](https://developer.apple.com/documentation/nearbyinteraction/nidiscoverytoken)
- [NISession discovery token](https://developer.apple.com/documentation/nearbyinteraction/nisession/discoverytoken)
- [NISession device capabilities](https://developer.apple.com/documentation/nearbyinteraction/nisession/devicecapabilities)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [NINearbyAccessoryConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbyaccessoryconfiguration)
- [NINearbyObject](https://developer.apple.com/documentation/nearbyinteraction/ninearbyobject)
- [NINearbyObject distance](https://developer.apple.com/documentation/nearbyinteraction/ninearbyobject/distance-676dm)
- [Nearby Interaction errors](https://developer.apple.com/documentation/nearbyinteraction/nierror)
- [userDidNotAllow](https://developer.apple.com/documentation/nearbyinteraction/nierror/userdidnotallow)
- [Implementing interactions between users in close proximity](https://developer.apple.com/documentation/nearbyinteraction/implementing-interactions-between-users-in-close-proximity)
- [Discovering peers with Multipeer Connectivity](https://developer.apple.com/documentation/nearbyinteraction/discovering-peers-with-multipeer-connectivity)
- [Implementing spatial interactions with third-party accessories](https://developer.apple.com/documentation/nearbyinteraction/implementing-spatial-interactions-with-third-party-accessories)
- [Finding devices with precision](https://developer.apple.com/documentation/nearbyinteraction/finding-devices-with-precision)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [MCSession](https://developer.apple.com/documentation/multipeerconnectivity/mcsession)
- [Network Framework](https://developer.apple.com/documentation/network)
- [NSNearbyInteractionUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsnearbyinteractionusagedescription)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nslocalnetworkusagedescription)
- [NSBonjourServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbonjourservices)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
