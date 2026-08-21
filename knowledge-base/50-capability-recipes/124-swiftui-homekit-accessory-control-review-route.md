# SwiftUI HomeKit and Matter accessory-control review route

Use this route when a SwiftUI app needs to display or control HomeKit data, prepare a HomeKit accessory setup, commission a Matter accessory, or draft a home action with on-device AI. It is a route contract, not a claim that a generic snippet works without a named target, entitlement, system account, and accessory.

The route is:

~~~text
user outcome
  -> target/capability/usage-description check
  -> HomeKit authorization or Matter support check
  -> shared topology owner
  -> normalized SwiftUI projection
  -> typed read/write or setup intent
  -> optional AI proposal
  -> deterministic validation and confirmation
  -> system/accessory side effect
  -> callback/notification reconciliation
  -> evidence packet
~~~

## Route contract

### Inputs

- selected target and deployment platform;
- HomeKit capability, usage description, signing, and entitlements;
- optional MatterSupport request/extension configuration;
- selected home or a user-requested home choice;
- supported service and characteristic types;
- current framework objects and revision;
- user action or selected AI context;
- safety policy for the side effect.

### Outputs

- a value-only SwiftUI home snapshot;
- a setup result or a documented failure state;
- a typed characteristic command or scene proposal;
- a completion and reconciliation record;
- an evidence record with simulator, physical, accessibility, and release gates.

### Non-goals

- copying the entire HomeKit database into a cloud backend;
- recreating Apple Home’s private screens;
- allowing natural-language output to write directly;
- treating an HMCharacteristic.value cache as guaranteed current;
- treating HomeKit Accessory Simulator as physical-device proof;
- claiming Matter commissioning is complete because a picker dismissed.

## Select the narrowest framework path

| Need | Minimum path | Add only when required |
| --- | --- | --- |
| Read a configured feature | HMHomeManager -> selected HMHome -> HMAccessory -> HMService -> HMCharacteristic | HomeKit delegates and characteristic notifications. |
| Write a feature | Metadata/properties check -> optional read -> typed write -> reconciliation | Confirmation, serialization, retry, or a scene route. |
| Add a HomeKit accessory | HMAccessorySetupManager or the current HMHome setup route | Target-home/context setup request. |
| Add Matter to an ecosystem | MatterAddDeviceRequest -> perform -> extension handler if required | Device criteria, onboarding payload, Wi-Fi/Thread selection, ecosystem database. |
| Group actions | Validated characteristic writes -> HMActionSet -> review -> execute | Trigger or schedule only if the product needs it. |
| Explain or draft | Selected snapshot -> local model -> typed proposal | Foundation Models availability gate and evaluation fixtures. |

## State machine

Use an explicit state rather than a collection of optional values:

~~~swift
enum HomeControlRouteState {
    case unavailable(reason: String)
    case needsPermission
    case loadingHomes
    case noHomes
    case ready(HomeSnapshot)
    case setupInProgress
    case commandPending(CommandID)
    case proposalNeedsReview(HomeControlProposal)
    case staleProposal
    case failed(message: String, retryable: Bool)
}
~~~

The exact names can change in the target, but these distinctions should remain:

- permission and topology;
- current versus last-known state;
- setup versus control;
- proposal versus committed action;
- completion versus later physical reconciliation.

## HomeKit owner route

Create one long-lived owner for the HomeKit boundary. Keep SwiftUI views dependent on value snapshots, not on the framework object graph:

~~~text
HomeKitCoordinator
  owns HMHomeManager
  receives manager/home/accessory/characteristic callbacks
  resolves current UUIDs
  builds HomeSnapshot
  owns setup and command tasks
  publishes route state

SwiftUI
  reads HomeSnapshot
  sends user intents
  renders state and evidence cues
~~~

Bootstrap:

1. Verify the target has HomeKit capability and NSHomeKitUsageDescription.
2. Construct the single HMHomeManager in the lifecycle owner.
3. Observe authorization and manager updates.
4. Select a home by stable UUID or ask the person to choose.
5. Project rooms and only the services required for the task.
6. Resolve characteristics by documented type and identity.
7. Register only required notifications.
8. Publish loading, empty, denied, stale, unreachable, and ready states.

When the shared HomeKit database changes, rebuild or reconcile the projection. Do not patch only the row that happened to be visible; the home may have been renamed, moved, removed, or changed in Apple Home.

## Projection contract

Use a typed, value-only model:

~~~swift
struct HomeSnapshot {
    var homeID: UUID
    var homeName: String
    var rooms: [RoomSnapshot]
    var topologyRevision: Int
    var refreshedAt: Date?
}

struct ServiceSnapshot: Identifiable {
    var id: UUID
    var homeID: UUID
    var accessoryID: UUID
    var roomName: String?
    var displayName: String
    var characteristicType: String
    var value: CharacteristicValue
    var readable: Bool
    var writable: Bool
    var supportsNotification: Bool
    var freshness: Freshness
    var reachability: Reachability
}
~~~

Do not expose Any? directly to a view. Normalize the supported characteristic types into product-owned values:

~~~text
Boolean
boundedNumber(value, unit, min, max, step)
enumeration(raw, label)
string
data(redacted)
unknown(rawType)
~~~

Unknown values should be visible in diagnostics and safe in the main route. They must not become a guessed Boolean or numeric control.

## Read/write route

For each command:

1. Resolve the current HomeKit object by stable ID.
2. Confirm the object remains in the selected home.
3. Confirm writable property and supported characteristic type.
4. Validate metadata bounds, unit, and app safety policy.
5. If required, read current value.
6. Create a pending command with source topology revision.
7. Present confirmation for high-consequence actions.
8. Call writeValue with the validated value.
9. On completion, update operation state only; wait for framework reconciliation for the reported physical state.
10. Invalidate or retry when a topology revision changes.

For a numeric slider, debounce user intent and use a target-specific write policy. For a lock or garage door, use a discrete action and an explicit result. For a thermostat, show the target value and the last reported value when those can differ.

## Notification and reconciliation route

Notifications and delegates are inputs to the coordinator, not direct view mutations:

~~~text
framework callback
  -> identify source object
  -> check current membership and revision
  -> normalize value/reachability
  -> update snapshot
  -> resolve pending command
  -> announce material change without stealing focus
~~~

When a notification is unavailable or the app resumes after time away, perform the supported read/reload path. Keep last-seen timestamps and source labels in app state if the UI needs to explain freshness. Do not use polling to compensate for an unclear ownership model.

If the product needs background behavior, document the actual supported process/lifecycle route and test it on the intended device. A HomeKit delegate callback alone does not authorize an indefinitely running background task.

## HomeKit setup route

When the person taps Add device:

1. Resolve the destination home and show it in the preparation UI.
2. Check supported target and authorization/configuration state.
3. Choose the current setup API for the selected SDK.
4. Call the system-owned setup flow from the user action.
5. Map cancellation, denial, unsupported, invalid-code, and other errors to UI state.
6. On success, use the returned home/accessory identifiers to refresh the projection.
7. Do not synthesize an accessory card before the shared model confirms it.

HMAccessorySetupManager’s documentation states that its setup APIs can perform the process of setting up accessories with Apple Home and that they don’t require current home-data authorization. Keep that setup authorization distinction visible in the route; do not use it to bypass the later data-access contract.

## Matter route

Use MatterSupport when the app is adding Matter accessories to its own ecosystem:

~~~text
runtime supported?
  no -> unsupported state
  yes
    -> build topology and home list
    -> apply narrow DeviceCriteria
    -> optionally set validated onboarding payload
    -> request.perform
    -> extension validates/commissions/configures
    -> setup result
    -> ecosystem reload
~~~

Required records:

- ecosystem name and home/room destination;
- criteria used and why;
- whether the onboarding payload was system-scanned or app-supplied;
- extension target and Info.plist principal class when used;
- credential/attestation/commissioning result;
- network or Thread selection outcome;
- post-commissioning device identity and reachability.

Do not log setup payloads or credentials. Do not assume all Matter devices are supported by the selected ecosystem. The MatterSupport documentation says calls return errors to Mac apps built with Mac Catalyst; record that in availability and proof.

## Typed AI proposal route

Use local AI only after the deterministic snapshot exists:

~~~swift
struct HomeControlProposal {
    var homeID: UUID
    var sourceTopologyRevision: Int
    var writes: [CharacteristicWrite]
    var explanation: String
    var warnings: [String]
    var requiresConfirmation: Bool
}
~~~

Proposal generation:

1. Select only the rooms/services the person asked about.
2. Include typed values, units, freshness, and reachability.
3. Ask the model for a proposal, not an executable command.
4. Parse into the typed schema.
5. Resolve names to current IDs deterministically.
6. Reject unknown, ambiguous, stale, out-of-range, or unsafe writes.
7. Show exact effects and warnings.
8. Require confirmation.
9. Revalidate at apply time.
10. Execute through the same command owner as a manual action.

The model must not infer occupancy, safety, consent, or physical completion. It must not receive network credentials, setup payloads, or the full home graph by default.

## SwiftUI shell route

The view layer should have separate destinations for:

- home/room context;
- service list;
- service detail;
- setup preparation;
- system setup handoff;
- pending/completion/failure;
- AI proposal review.

Use semantic controls and bounded Liquid Glass groups:

~~~text
NavigationStack or adaptive split view
  -> HomeContextBar
  -> ServiceList
       -> ServiceRow
       -> ServiceDetail
  -> AddDevicePreparation
  -> ProposalReview
~~~

When Liquid Glass is unavailable, reduced, or inappropriate, retain the same hierarchy with system materials or opaque backgrounds. Do not place a second glass layer around system-owned pairing UI.

## Validation and stop conditions

Stop the route if:

- the target lacks HomeKit capability or usage description;
- authorization is denied and the UI has no recovery;
- a service/characteristic cannot be resolved by stable identity;
- metadata or write properties are missing for a control;
- an AI proposal contains an ambiguous or stale target;
- the user has not reviewed a physical side effect;
- a Matter setup result has not been reconciled;
- the screen implies current state from a last-known value without a freshness cue;
- a simulator-only route is being described as physical-device proof.

## Evidence packet

Record:

- target, SDK, entitlements, Info.plist, signing, and extension configuration;
- authorization allow/deny/revocation;
- no home, multiple homes, room changes, and topology changes from Apple Home;
- read/write/notification fixtures and error mapping;
- HomeKit Accessory Simulator state;
- physical accessory state and side-effect result;
- Matter criteria, setup, cancellation, commissioning, network, and room result;
- AI proposal with stale-revision and invalid-value rejection;
- VoiceOver, Dynamic Type, alternate input, reduced effects, and localization;
- archive and signed release target.

## Sources

- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Enabling HomeKit in your app](https://developer.apple.com/documentation/homekit/enabling-homekit-in-your-app)
- [HMHomeManager](https://developer.apple.com/documentation/homekit/hmhomemanager)
- [HMHome](https://developer.apple.com/documentation/homekit/hmhome)
- [HMAccessory](https://developer.apple.com/documentation/homekit/hmaccessory)
- [HMService](https://developer.apple.com/documentation/homekit/hmservice)
- [HMCharacteristic](https://developer.apple.com/documentation/homekit/hmcharacteristic)
- [Characteristic types](https://developer.apple.com/documentation/homekit/characteristic-types)
- [HMAccessorySetupManager](https://developer.apple.com/documentation/homekit/hmaccessorysetupmanager)
- [HMAccessorySetupResult](https://developer.apple.com/documentation/homekit/hmaccessorysetupresult)
- [performAccessorySetup(using:completionHandler:)](https://developer.apple.com/documentation/homekit/hmaccessorysetupmanager/performaccessorysetup%28using%3Acompletionhandler%3A%29)
- [Configuring a home automation device](https://developer.apple.com/documentation/homekit/configuring-a-home-automation-device)
- [Interacting with a home automation network](https://developer.apple.com/documentation/homekit/interacting-with-a-home-automation-network)
- [Testing your app with the HomeKit Accessory Simulator](https://developer.apple.com/documentation/homekit/testing-your-app-with-the-homekit-accessory-simulator)
- [MatterSupport](https://developer.apple.com/documentation/mattersupport)
- [Adding Matter support to your ecosystem](https://developer.apple.com/documentation/mattersupport/adding-matter-support-to-your-ecosystem)
- [MatterAddDeviceRequest](https://developer.apple.com/documentation/mattersupport/matteradddevicerequest)
- [MatterAddDeviceRequest.DeviceCriteria](https://developer.apple.com/documentation/mattersupport/matteradddevicerequest/devicecriteria)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [HomeKit Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/homekit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
