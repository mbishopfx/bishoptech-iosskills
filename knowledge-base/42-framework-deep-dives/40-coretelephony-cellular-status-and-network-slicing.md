# Core Telephony: cellular status, quick switch, eSIM, and network slicing

Core Telephony exposes selected cellular-service and carrier capabilities to apps. It is not a general-purpose signal-strength, speed-test, identity, or connectivity guarantee. The useful route is:

cellular policy or service signal -> Core Telephony snapshot -> conservative product decision -> Network/URLSession observation -> native status surface -> optional reviewed AI explanation

Keep the framework behind a small service boundary. A view should never infer “online,” “fast,” “secure,” or “the user is a carrier customer” from one Core Telephony value.

## 1. Route map

| Product need | Core Telephony route | Boundary |
| --- | --- | --- |
| Know which cellular service provides data | CTTelephonyNetworkInfo dataServiceIdentifier and delegate | Service identity can change while the app runs; it is not proof of reachability |
| Observe registered radio technology | serviceCurrentRadioAccessTechnology | Registration is not throughput, latency, or an available Internet path |
| Know whether app cellular data is restricted | CTCellularData restrictedState and notifier | Restriction is a policy signal; Wi-Fi, VPN, and server reachability are separate |
| Request a preferred cellular network slice | CTSlicingManager | Carrier, entitlement, device, and network conditions control availability |
| Transition app state between active/passive iPhones | CTQuickSwitchManager | Beta/eligibility and service-specific behavior require final-device proof |
| Provision a carrier eSIM | CTCellularPlanProvisioning | Carrier apps with the documented fine-grained entitlement only |
| Read legacy call information | Deprecated CTCall/CTCallCenter | Use CallKit for supported call-system routes |

The Core Telephony framework’s current documentation contains both modern and deprecated surfaces. Prefer current service dictionaries, delegates, async APIs, and the named managers where available. Record a target-specific availability decision instead of treating the framework landing page as a universal contract.

## 2. CTTelephonyNetworkInfo and changing service state

CTTelephonyNetworkInfo provides the current data service identifier and a delegate for changes. It also exposes a dictionary of the current radio access technology registered to each service. The older single-service carrier and radio-access properties are deprecated.

Design the app around a snapshot:

- service identifier, if available;
- radio-technology value, if available;
- timestamp and target;
- observed change event;
- unknown/unavailable state.

The user may swap a SIM, change the active cellular service, move between coverage areas, or use a device with no registered service. Reconcile the snapshot when the delegate reports a change. Do not persist a carrier label as permanent account identity, and do not treat a radio technology string as a promise of 5G performance.

## 3. CTCellularData is a policy signal

CTCellularData reports whether the app can access cellular data through restrictedState. The state can be not restricted, restricted, or unknown, and the notifier can report changes.

Use this signal to explain why a cellular-only operation may be blocked or to defer a large transfer. Pair it with Network framework path observation and the actual request result:

cellular policy -> path viability -> request attempt -> server response -> user-facing state

If cellular data is restricted, do not say “the Internet is unavailable.” The user may still have Wi-Fi, an offline cache, or a different permitted route. If the state is unknown, use a conservative fallback and avoid a hard failure message that claims more than the API knows.

## 4. Network slicing with CTSlicingManager

CTSlicingManager controls and monitors network-slicing traffic routing when the device, carrier, app entitlement, and current network conditions support it. The documented route is:

1. Query availableSliceAppCategories.
2. Check that the desired category is present.
3. Activate the preferred slice before creating the network connections that should use it.
4. Establish the app’s connections.
5. Inspect activeSlices when the product needs an operational status.
6. Disable slicing when the feature no longer needs the preferred route.

Categories include gaming, communication, and streaming, with additional categories documented as beta or target-dependent. The app must not present “low latency guaranteed.” Even if the category is available, observed latency and throughput remain runtime conditions.

Handle documented and runtime failures:

- network slicing unsupported;
- missing entitlement;
- category unavailable;
- activation failure;
- connection created before activation;
- active slice changed or disappeared;
- user disabled or carrier changed the service.

The routing decision belongs to a service owner, not a button animation. If a game surface offers a “prefer gaming route” control, show whether the request was available, accepted, active, or unavailable.

## 5. iPhone quick switch

iPhone quick switch lets eligible apps receive state changes when a phone number’s active device changes and query the current device or phone-number state. CTQuickSwitchManager can provide a delegate, asynchronous state queries, and registration for background launch on quick-switch state events.

The important product contract is continuity:

- active means the device currently owns the cellular service for the relevant number;
- passive means another device holds the service;
- not enrolled means the service is not configured;
- failed/unknown means the app cannot determine the state.

When the system signals a transition, move credentials, persistent state, caches, and active-service ownership through a deliberate handoff. Do not log or display full phone numbers. Use the suffix/query input only within the documented service boundary and only when the product has a legitimate eligibility path.

Quick switch documentation marks portions of this route beta. Treat the page as a design and integration signal, then verify final operating-system behavior on eligible physical devices and the supporting service.

## 6. eSIM provisioning is a carrier-only route

CTCellularPlanProvisioning downloads and installs a carrier eSIM. Apple’s documentation states that the class is available only to carrier apps with the com.apple.CommCenter.fine-grained entitlement including public-cellular-plan. The route includes support checks, an eSIM request, optional plan properties, an add-plan result, and property updates.

For a normal app, this is a stop condition, not an invitation to build a fake onboarding flow. Do not claim that an app can provision arbitrary eSIM plans. For a carrier target, keep entitlement, region, hardware, plan-availability, user consent, cancellation, failure, and unknown-result states explicit.

## 7. Calls, identity, and adjacent frameworks

The current Core Telephony overview marks CTCall and CTCallCenter call-information routes deprecated. Use CallKit for supported call-system integration. Likewise:

- use Network and URLSession for actual path/request behavior;
- use Core Bluetooth or External Accessory for accessory transport;
- use PushKit/CallKit for the documented VoIP/system-call route;
- use AVFAudio for audio session and rendering;
- use authentication services for account identity.

Core Telephony is a signal source, not a substitute for these frameworks.

## 8. Liquid Glass and native status design

Use a compact status surface that tells the user what the app knows:

- Cellular data: allowed, restricted, or unknown
- Registered radio: available value or unavailable
- Preferred route: requested, active, unavailable, or not configured
- Path: Wi-Fi, cellular, constrained, expensive, or unavailable from the Network layer
- Request: queued, running, completed, failed, or cached

Liquid Glass can frame a route explanation, an adaptive-transfer inspector, or a review sheet. Keep the primary content readable when the glass is removed, reduced, or unavailable. Do not use a bright “5G” badge as a promise of speed or security.

## 9. Bounded on-device AI opportunities

AI can explain a known observation or propose a conservative policy:

- summarize why a transfer is waiting for Wi-Fi;
- suggest a smaller offline asset when cellular data is restricted;
- explain that network-slice availability depends on carrier and entitlement;
- propose a user-approved sync policy based on observed policy/path state;
- summarize a quick-switch handoff checklist after the system reports a transition.

The deterministic layer owns policy values, path state, entitlements, request execution, credential handoff, and any network-side effect. Never give a model raw permission to activate a slice, alter account identity, provision eSIM, or transfer credentials.

## 10. Availability and proof

Core Telephony values are device, service, carrier, region, entitlement, and OS dependent. A simulator value or a non-nil property does not prove a real cellular route. Record:

- target platform, SDK, deployment target, and device model;
- SIM/eSIM/carrier configuration and service identifier handling;
- cellular-data policy state and change recovery;
- radio-technology observation alongside actual Network/URLSession results;
- network-slicing entitlement, category availability, activation order, and active-slice observation;
- quick-switch eligibility and active/passive transition evidence;
- carrier-only eSIM entitlement evidence, if applicable;
- privacy, accessibility, reduced-motion, offline, and Wi-Fi fallback behavior;
- signed-device/TestFlight behavior for the target release.

## Sources

- [Core Telephony](https://developer.apple.com/documentation/coretelephony)
- [CTTelephonyNetworkInfo](https://developer.apple.com/documentation/coretelephony/cttelephonynetworkinfo)
- [CTCellularData](https://developer.apple.com/documentation/coretelephony/ctcellulardata)
- [CTCellularDataRestrictedState](https://developer.apple.com/documentation/coretelephony/ctcellulardatarestrictedstate)
- [CTSlicingManager](https://developer.apple.com/documentation/coretelephony/ctslicingmanager)
- [CTSlicingManager.AppCategory](https://developer.apple.com/documentation/coretelephony/ctslicingmanager/appcategory)
- [CTSlicingManager.Slice](https://developer.apple.com/documentation/coretelephony/ctslicingmanager/slice)
- [iPhone quick switch](https://developer.apple.com/documentation/coretelephony/iphone-quick-switch)
- [CTCellularPlanProvisioning](https://developer.apple.com/documentation/coretelephony/ctcellularplanprovisioning)
- [CTCellularPlanProvisioningAddPlanResult](https://developer.apple.com/documentation/coretelephony/ctcellularplanprovisioningaddplanresult)
- [Network](https://developer.apple.com/documentation/network)
- [NWPathMonitor](https://developer.apple.com/documentation/network/nwpathmonitor)
- [URLSession](https://developer.apple.com/documentation/foundation/urlsession)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

***
