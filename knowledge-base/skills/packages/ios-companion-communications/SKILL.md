---
name: ios-companion-communications
description: Design, route, implement, or review iOS companion and communication features using WatchConnectivity, CarPlay, App Clips, CallKit, LiveCommunicationKit, PushKit, APNs, and UserNotifications. Use when a feature spans iPhone/Watch, a vehicle screen, an App Clip/full app handoff, VoIP/calling, default calling/dialer behavior, or specialized push delivery.
---

# iOS Companion and Communications

Use this skill to keep paired-device, vehicle, App Clip, push, call, audio, server, and system-UI state separate.

## Read before acting

- Inspect the actual iPhone/Watch/App Clip/CarPlay targets, bundle identifiers, deployment targets, scene manifests, entitlements, capabilities, associated domains, App Groups, APNs environment, server contract, and audio/session adapters.
- Read the [networking/companion route](../../../40-framework-routes/07-networking-and-collaboration.md), [Watch/CarPlay/App Clip deep dive](../../../43-system-framework-deep-dives/04-watch-carplay-and-app-clips.md), [Watch Connectivity state deep dive](../../../42-framework-deep-dives/06-watch-connectivity-and-multiplatform.md), and [communication surfaces card](../../../44-system-services/01-commerce-and-communication-surfaces.md).
- Refresh the exact official framework pages in the Sources section before relying on current OS/region/device availability, an entitlement, push rule, or system-owned UI behavior.

## Routing workflow

1. Identify the user outcome: paired-device state, queued companion event, immediate companion request, vehicle glance/action, App Clip task, ordinary message, incoming VoIP call, or default calling/dialer action.
2. Select the route by semantics: `updateApplicationContext` for latest Watch state, `transferUserInfo` for queued events, `transferFile` for file handoffs, `sendMessage` only for reachable immediate interaction; CarPlay templates for supported vehicle categories; App Clip invocation URLs for focused entry; UserNotifications for ordinary notification; PushKit only for documented VoIP/file-provider/complication uses.
3. Draw the system boundary: `activation/invocation/token -> validation/account/server reconciliation -> system-owned surface -> service/action completion -> fallback`.
4. Model separate fields for paired, installed, activated, active, reachable, queued, connected, token-registered, call-reported, call-active, stale, failed, and ended. Never reduce them to one `connected` Boolean.
5. Make every payload versioned, scoped to the correct account/device, bounded, privacy-minimized, and idempotent. Persist revisions/event IDs where a duplicate side effect matters.
6. Define unavailable/fallback behavior: no Watch, not reachable, inactive watch, CarPlay disconnect, no invocation URL, App Clip replaced by full app, push token rotation, server timeout, call rejection, audio interruption, and no system entitlement.
7. Test the actual two-device/system surface. A simulator, mock push, local URL, or screenshot does not prove pairing, APNs, vehicle behavior, system call UI, audio, default-role eligibility, or delivery timing.

## Non-negotiable communication rules

- PushKit is not a general-purpose background wake channel. For VoIP on current SDKs, report the incoming call to CallKit quickly; if the app cannot use CallKit, use UserNotifications instead.
- A PushKit token/payload is not identity, permission, delivery, or an active call. Reconcile with the server and deduplicate call UUIDs.
- CallKit actions are system commands. Fulfill answer/end/hold only after the underlying service/audio state is ready; fail or report an end reason honestly.
- LiveCommunicationKit coordinates conversations and possible default roles; it does not provide the VoIP backend or guarantee broad OS/region eligibility.
- CarPlay apps use supported templates and category rules; do not mirror an unrestricted iPhone UI or put dense editing in a driver-facing surface.
- App Clip URLs are context, not account/payment/permission proof. Parse and validate them; handle launches without a URL; share the invocation parser with the full app.
- Watch reachability is only immediate availability. Queued transfers are delayed/opportunistic; delivery is not server sync.
- Keep contact, call, location, health, and vehicle metadata out of logs and shared projections unless explicitly needed and retained.

## Deliverable

Produce:

- selected route and rejected alternatives;
- target, pairing, server, entitlement, APNs, associated-domain, and account matrix;
- protocol envelope/reducer and state machine;
- user-facing fallback/offline/error policy;
- physical/two-device/system-surface evidence plan;
- source links and unproven claims.

During implementation, preserve target boundaries and do not add server accounts, VoIP pushes, telephony/default-role entitlements, tracking, recording, or external communications without explicit need and authorization.

## Related recipes

- [Watch, CarPlay, App Clip, and communication recipes](../../../70-code-recipes/20-watch-carplay-appclips-and-communications-recipes.md)
- [Watch/CarPlay/App Clip deep dive](../../../43-system-framework-deep-dives/04-watch-carplay-and-app-clips.md)
- [Watch Connectivity and multiplatform state](../../../42-framework-deep-dives/06-watch-connectivity-and-multiplatform.md)
- [System-surface checklist](../../../60-verification/05-system-surface-checklist.md)
- [Build/device/release checklist](../../../60-verification/01-build-device-and-release-checklist.md)

## Sources

- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [WCSession](https://developer.apple.com/documentation/watchconnectivity/wcsession)
- [WCSessionDelegate](https://developer.apple.com/documentation/watchconnectivity/wcsessiondelegate)
- [Transferring data with Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity/transferring-data-with-watch-connectivity)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [CPTemplateApplicationScene](https://developer.apple.com/documentation/carplay/cptemplateapplicationscene)
- [CPInterfaceController](https://developer.apple.com/documentation/carplay/cpinterfacecontroller)
- [Displaying content in CarPlay](https://developer.apple.com/documentation/carplay/displaying-content-in-carplay)
- [App Clips](https://developer.apple.com/documentation/appclip)
- [Responding to invocations](https://developer.apple.com/documentation/appclip/responding-to-invocations)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [Making and receiving VoIP calls](https://developer.apple.com/documentation/callkit/making-and-receiving-voip-calls)
- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [PKPushRegistry](https://developer.apple.com/documentation/pushkit/pkpushregistry)
- [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
- [UserNotifications](https://developer.apple.com/documentation/usernotifications)
