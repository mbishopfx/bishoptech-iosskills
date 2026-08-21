# System-Service Route Cards

These cards cover Apple services that sit between an app and the operating system, a protected data domain, a system surface, or a signed developer service. They complement the [framework catalog](../40-framework-routes/00-framework-catalog.md) and the [system framework deep dives](../43-system-framework-deep-dives/README.md) with shorter route-selection guidance.

Use them when an idea needs more than an in-app view:

- [Privacy and device services](00-privacy-and-device-services.md) covers Screen Time APIs, on-device Spotlight indexing, accessibility/Assistive Access, and device-integrity routes.
- [Commerce and communication surfaces](01-commerce-and-communication-surfaces.md) covers Apple Pay/Wallet, CallKit/LiveCommunicationKit, PushKit, and communication notifications.
- [CallKit, LiveCommunicationKit, and VoIP system routes](04-callkit-livecommunicationkit-and-voip.md) deepens provider actions, PushKit/APNs delivery, default calling/dialer boundaries, audio lifecycle, privacy, and physical-device proof.
- [Group Activities and SharePlay system routes](05-group-activities-shareplay.md) deepens activity metadata/capability, eligibility and activation, GroupSession lifecycle, Messenger/Journal synchronization, late join, privacy, and two-device proof.
- [Collaboration and nearby sessions](02-collaboration-and-nearby-sessions.md) covers Group Activities/SharePlay, GroupSession messaging/journals, nearby peer discovery, Network Framework selection, local-network privacy, and collaborative protocol proof.
- [Discovery, Handoff, and preview services](03-discovery-handoff-and-preview-services.md) covers TipKit, Core Spotlight/App Entities, NSUserActivity/Handoff, Quick Look, preview extensions, and system-projection privacy.
- [Screen capture and broadcast services](06-screen-capture-and-broadcast-services.md) covers ReplayKit compatibility, ScreenCaptureKit availability gates, system content pickers, broadcast/extension boundaries, capture privacy, media finalization, and on-device AI handoff.

Every card identifies permissions, capabilities, entitlements, external configuration, fallback behavior, and the evidence required for a real system surface. A framework landing page is not proof that a project has access to the service.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Framework availability and device-proof matrix](../40-framework-routes/08-framework-availability-and-device-matrix.md)
