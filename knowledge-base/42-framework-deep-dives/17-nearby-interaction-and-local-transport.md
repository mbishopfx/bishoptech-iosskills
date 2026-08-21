# Nearby Interaction and local transport deep dive

Nearby Interaction, Multipeer Connectivity, and Network Framework solve related but different problems:

- Nearby Interaction reports a relationship such as distance and direction for a peer Apple device or supported accessory.
- Network Framework provides a modern route for discovering and connecting local services and moving application data.
- Multipeer Connectivity offers a high-level discovery/session experience for existing apps, but Apple’s current documentation marks MCSession as deprecated and points new work toward Network Framework.

The architecture should never treat “nearby” as identity, trust, transport, or permission by itself. A robust route is:

~~~text
user intent
  -> capability/permission check
  -> discovery
  -> user selection or explicit consent
  -> identity/protocol handshake
  -> transport
  -> optional Nearby Interaction token/configuration
  -> data/state exchange
  -> continuous UI feedback
  -> interruption/reconnect/teardown
~~~

## Route map

| User outcome | Primary API | Boundary |
| --- | --- | --- |
| Show direction/distance to a peer device | Nearby Interaction, NISession, NINearbyPeerConfiguration | UWB/device support, permission, token exchange, field of view, orientation, obstructions, and physical accuracy. |
| Interact with a supported accessory | NISession, NINearbyAccessoryConfiguration, accessory protocol | Accessory capability, configuration-data exchange, radio/transport, firmware, and accessory trust. |
| Discover local services | Network Framework NWBrowser/Bonjour or a product-owned discovery protocol | Local-network permission, service metadata, candidate validation, and no assumption that discovery proves identity. |
| Build a direct local data connection | NWConnection/NWListener with selected NWParameters | Transport state, security, protocol framing, reconnect, cancellation, and data ownership. |
| Maintain an existing high-level peer session | Multipeer Connectivity MCSession/browser/advertiser | Legacy/deprecation boundary, local-network/Bonjour declarations, foreground-only lifecycle, and session reestablishment. |
| Guide a physical action | Direction/distance plus visual/audio/haptic feedback | Continuous feedback, accessibility alternatives, portrait/field-of-view guidance, and no hidden physical requirement. |
| Let AI suggest a nearby target or action | Bounded local candidate list and proximity summary | Nearby data does not prove identity, consent, ownership, or safe side effects. |

## Nearby Interaction session

NISession is the central object for interacting with one nearby object. A session represents one peer/accessory relationship; multiple nearby objects require separate sessions. The app chooses a concrete NIConfiguration:

- NINearbyPeerConfiguration uses a discovery token from another Apple device.
- NINearbyAccessoryConfiguration uses configuration data exchanged with a supported accessory.
- Other configuration subclasses or device capabilities must be checked in the selected SDK.

The session delegate receives nearby-object updates and lifecycle events. Model the session:

~~~text
created -> checking device capabilities -> awaiting permission
       -> exchanging discovery/configuration data
       -> running
       -> updating distance/direction
       -> suspended/interrupted
       -> invalidated/stopped
~~~

Apple’s Nearby Interaction guidance describes discovery tokens as randomly generated identifiers that last only for the interaction session. A discovery token is therefore a session credential/input, not a permanent account identity. Store the minimum needed to complete the handshake and discard it when the session ends.

## Discovery, transport, and trust

Nearby Interaction does not replace data transport. A common peer flow uses a discovery or invitation transport to exchange tokens, then runs NI on the established relationship:

~~~text
device A discovers device B
  -> person selects/accepts B
  -> app-specific identity/protocol handshake
  -> token exchange
  -> NISession.run(configuration)
  -> NWConnection carries app messages
  -> NI updates guide the UI
~~~

Network Framework is the preferred new route for local service discovery and connections. NWBrowser can browse Bonjour services; NWListener can advertise or accept connections; NWConnection carries bidirectional data. The target may need NSLocalNetworkUsageDescription and NSBonjourServices when the route uses local network/Bonjour. Configure transport security and protocol framing explicitly.

Multipeer Connectivity is useful for existing high-level peer discovery/session UX, but it is not a general identity system. The app must accept/reject invitations, validate context data, define a protocol, and handle the fact that its open sessions disconnect when the app enters the background. Apple’s docs also state that new work should use Network Framework instead of the deprecated MCSession route.

Discovery answers “something matching this service is present.” It does not answer:

- whether the peer is the intended person/device;
- whether the device is trusted or authorized;
- whether the data is fresh or unmodified;
- whether a side effect should be performed.

Use an app-owned identity handshake, authenticated transport where appropriate, replay/revision protection, and explicit confirmation for consequential actions.

## Protocol boundary

Define a small versioned protocol before wiring the UI:

~~~text
Hello(version, capabilitySet, ephemeralSessionID)
  -> Accept/reject(reason)
  -> TokenExchange or accessory configuration
  -> Ready
Message(sequence, revision, type, payload)
  -> Ack or error where needed
  -> Reconnect/resync or close
~~~

Validate:

- service type and discovery metadata;
- message size and encoding;
- schema version and supported capabilities;
- session/peer identity for the current run;
- sequence/revision and duplicate handling;
- authorization for each side effect;
- cancellation and timeout;
- reconnect/resync behavior.

Treat discovery context, accessory payload, and peer message bytes as untrusted. Do not deserialize arbitrary objects or use a display name as authorization.

## Nearby feedback

Nearby Interaction HIG guidance emphasizes physical context, continuous feedback, direction/distance, field of view, device orientation, and obstacles. A good experience:

- starts with an ordinary app task;
- explains what physical action is useful;
- gives continuous but calm feedback as the person moves;
- uses visual, audio, and haptic channels together;
- helps the person hold the device in a supported orientation;
- explains that people, animals, or objects can reduce accuracy;
- keeps a manual or non-nearby route.

On iPhone, direction and distance data may depend on supported UWB hardware and the target device. A device outside the directional field of view may still provide distance without reliable direction. The route must state that limitation rather than showing a confident arrow.

## Local transport lifecycle

For Network Framework:

~~~text
idle -> preparing parameters -> browsing/listening
     -> candidate found -> user/protocol validation
     -> connecting -> ready
     -> sending/receiving
     -> waiting/reconnecting/failed
     -> cancelled
~~~

Handle browser/listener state, connection failure, path changes, local network permission, app backgrounding, peer departure, stream framing, partial reads, cancellation, and backpressure. Keep a bounded queue and avoid treating a connected socket as domain truth.

For Multipeer Connectivity, stop browsing/advertising when the feature ends, retain delegate/session ownership, reestablish sessions after foreground return when appropriate, and keep peer selection visible. Do not promise background continuity from its foreground behavior.

## Privacy and AI

Nearby interactions can reveal physical proximity and direction without becoming account identity. Use them only for the user-started task:

- let the person choose a nearby candidate;
- show what data will be shared;
- use ephemeral tokens and session IDs;
- avoid retaining precise traces unless the product needs them;
- do not expose nearby candidates as contacts without a separate identity/consent route;
- invalidate stale proximity when the session pauses or the device moves out of range.

On-device AI can rank a user-selected candidate, summarize the local session, or suggest a physical handoff. Keep it bounded by current discovery/session data and show uncertainty. Do not let AI infer who a nearby person is, claim consent, unlock a device, or transfer data without a confirmed target and protocol authorization.

## Platform and device boundaries

Check every selected platform. Nearby Interaction HIG guidance describes iPhone and Apple Watch capabilities differently and identifies unsupported platforms. Network transport may be broader, but local network permission and Bonjour declarations still apply. Multipeer Connectivity’s underlying transports differ across platforms and its background behavior requires explicit proof.

Maintain a matrix of:

- iPhone model/UWB support;
- Apple Watch peer behavior;
- accessory protocol/version;
- device orientation;
- distance/obstruction environment;
- local network permission;
- Wi-Fi/Bluetooth state;
- app foreground/background state;
- OS/deployment target;
- transport/security configuration.

## Evidence checklist

- capability and availability checks for NI, Network, MC, and selected hardware;
- local-network and Bonjour usage strings/declarations;
- explicit discovery/selection/consent and rejection behavior;
- token/configuration exchange with invalid, stale, duplicate, and wrong-peer fixtures;
- NISession delegate updates, suspension, invalidation, and multiple-object policy;
- NWBrowser/NWListener/NWConnection state, framing, security, cancellation, and reconnect;
- Multipeer foreground/background and session reestablishment if used;
- physical direction/distance/orientation/obstruction tests;
- visual/audio/haptic continuous feedback, VoiceOver, Reduce Motion, and manual fallback;
- AI candidate/proximity proposal review with no identity or silent side effect;
- battery, thermal, latency, transport throughput, and privacy/retention measurements;
- signed entitlements, supported-device metadata, and release-system proof.

## Sources

- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NIConfiguration](https://developer.apple.com/documentation/nearbyinteraction/niconfiguration)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [NINearbyAccessoryConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbyaccessoryconfiguration)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [MCSession](https://developer.apple.com/documentation/multipeerconnectivity/mcsession)
- [MCNearbyServiceBrowser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyservicebrowser)
- [MCNearbyServiceAdvertiser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyserviceadvertiser)
- [Network](https://developer.apple.com/documentation/network)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [NWListener](https://developer.apple.com/documentation/network/nwlistener)
- [Nearby interactions HIG](https://developer.apple.com/design/human-interface-guidelines/nearby-interactions/)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
