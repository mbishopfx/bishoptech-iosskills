# SwiftUI HomeKit and Matter accessory-control review

This deep dive covers the SwiftUI-specific boundary around HomeKit and Matter: projecting a shared home model into native views, making characteristic state legible, handing setup to Apple’s system flows, gating physical side effects, and using on-device AI only for reviewable proposals.

It extends the lower-level [HomeKit, Matter, and home-automation deep dive](15-homekit-matter-and-home-automation.md), the [HomeKit and Matter native surfaces](../21-design-deep-dives/30-homekit-and-matter-native-surfaces.md) page, and the [HomeKit and Matter automation route](../50-capability-recipes/33-homekit-matter-automation-route.md). The distinct question here is how a SwiftUI app should expose a trustworthy, adaptive control surface without creating a shadow home database or copying Apple Home’s private UI.

## The authority boundary

Use this sequence for a native accessory-control surface:

~~~text
target and entitlement configuration
  -> HomeKit authorization or Matter setup capability
  -> shared home/topology observation
  -> app-owned SwiftUI projection
  -> current-value read and capability validation
  -> optional on-device AI proposal
  -> explicit user review and safety gate
  -> HomeKit/Matter side effect
  -> completion, delegate, notification, and topology reconciliation
~~~

Keep the owners distinct:

| Fact or action | Authority | What SwiftUI may communicate |
| --- | --- | --- |
| Home, room, accessory, service, and characteristic graph | HomeKit shared database or the current Matter ecosystem | “This is the current framework projection for the selected home.” |
| App permission | System authorization and the target configuration | “Home access is allowed, denied, restricted, or not yet requested.” |
| Display selection and local draft | App-owned state | “This is the home, service, range, or scene the person is reviewing.” |
| Characteristic value | HomeKit plus the accessory and its reporting path | “This value is current, last known, pending, unreachable, or unknown.” |
| AI output | Foundation Models or another on-device model | “This is a proposal grounded in the selected snapshot.” |
| Device command or scene execution | Validated user action and HomeKit/Matter | “The app requested this side effect; completion and later reports decide the result.” |
| Evidence | Target, simulator, physical accessory, system account, and signed artifact | “This route passed a named proof gate,” not merely “the preview rendered.” |

A SwiftUI Binding is not a device connection. A Toggle can represent user intent while a write is pending; it must not silently become the canonical physical state before the framework reports success and the app reconciles the resulting value.

## HomeKit and Matter are related but not interchangeable

HomeKit coordinates configured accessories through a shared home model. The root object is one HMHomeManager for the app’s HomeKit activities; it exposes HMHome instances, which contain rooms, zones, action sets, triggers, and HMAccessory instances. An HMAccessory represents a physical device, HMService represents a controllable or readable feature, and HMCharacteristic represents a specific value or control point.

MatterSupport is an ecosystem-oriented setup route for compatible Matter accessories. Its request and extension-handler APIs coordinate commissioning and follow-up configuration. A Matter pairing result is not automatically the same thing as a ready HomeKit object graph or an app-owned device record.

Use the right route:

| Outcome | Native route | Boundary |
| --- | --- | --- |
| Show devices already configured in the person’s home | HomeKit HMHomeManager -> HMHome -> HMAccessory -> HMService -> HMCharacteristic | Project the shared graph; do not make a private copy authoritative. |
| Read or write a feature | HMCharacteristic readValue, value, metadata, properties, writeValue | Validate type, permissions, range, freshness, and side-effect policy. |
| Receive external changes | Characteristic notifications plus HomeKit manager/home/accessory delegates | Reconcile by identifier; do not treat a callback as a complete event log. |
| Add a HomeKit accessory | HMHome system setup or HMAccessorySetupManager | Let the system handle pairing, naming, room assignment, and authorization. |
| Commission a Matter device | MatterAddDeviceRequest and MatterAddDeviceExtensionRequestHandler | Treat criteria, onboarding payload, attestation, network selection, and ecosystem result as separate states. |
| Suggest a scene or device action | On-device AI -> typed proposal -> deterministic validation -> user confirmation | The model never receives direct write authority. |

HomeKit’s documentation describes its database as shared among Apple’s Home app, HomeKit-enabled apps, and other peer apps. That means another app, the Home app, a user, or an accessory can change the graph after the SwiftUI view rendered. Preserve identity and revision information in the app-owned projection.

## Authorization and target configuration

HomeKit requires the HomeKit capability and the NSHomeKitUsageDescription purpose string. The system can prompt when the app first uses HomeKit, typically when it creates an HMHomeManager. If a person denies access, HomeKit calls can fail with a homeAccessNotAuthorized error; the person can also revoke access later in Settings. A screen that only handles the first prompt is incomplete.

Use an explicit state machine:

~~~text
unconfigured
  -> capabilityMissing
  -> usageDescriptionMissing
  -> readyToRequest
readyToRequest -> requesting
requesting -> authorized
           -> denied
           -> restricted
authorized -> loadingHomes
loadingHomes -> noHomes
             -> ready
             -> loadError
ready -> settingsRevoked -> denied
ready -> externalTopologyChange -> reconciling -> ready
~~~

The HomeKit capability, usage description, signing team, provisioning profile, and selected target are one configuration gate. Test the actual target, not only a source file that imports HomeKit. The target matrix should also record whether the route is supported on iOS, iPadOS, watchOS, or another platform; the MatterSupport documentation specifically calls out errors for Mac Catalyst apps, so a Catalyst compile is not a Matter proof.

Do not request HomeKit access to render a generic dashboard, run advertising personalization, or provide an unconnected AI chat. Explain the concrete home task first. If access is denied, preserve useful non-HomeKit features and clearly explain the next user action.

## The SwiftUI lifecycle owner

Use one long-lived, app-owned owner for the framework boundary and publish a small value projection to SwiftUI. A typical shape is an @MainActor observable store with:

- one HMHomeManager;
- a selected-home identifier rather than a fragile array index;
- authorization and lifecycle state;
- a topology revision;
- value projections containing source, timestamp, reachability, and pending state;
- setup and command tasks that can be cancelled;
- one reconciliation path for delegate callbacks, notification callbacks, and completion handlers.

Avoid these failure modes:

- creating an HMHomeManager every time a view appears;
- attaching a new characteristic delegate every time a row is reused;
- storing framework objects in a Sendable model without checking the selected SDK’s isolation rules;
- mutating SwiftUI state from an arbitrary HomeKit callback queue;
- using the first home or first service as an implicit product decision;
- retaining a selected service after it was removed or moved in the shared graph.

The UI may receive immutable snapshots:

~~~text
HomeKit callback
  -> lifecycle owner
  -> resolve current object by UUID
  -> normalize type, value, metadata, and reachability
  -> increment topology/value revision
  -> publish value snapshot on the UI isolation boundary
~~~

When a callback arrives, first check that the referenced home, accessory, service, or characteristic still exists. A callback for an object that has been removed should invalidate drafts that reference it rather than resurrecting the object in a list.

## Project the object graph without flattening trust

The object hierarchy should remain visible enough that the user understands context:

| Framework object | App projection | Important state |
| --- | --- | --- |
| HMHome | HomeSummary | UUID, user name, primary status, rooms, zones, revision. |
| HMRoom | RoomSummary | UUID, user name, selected-home identity, service membership. |
| HMAccessory | DeviceSummary | UUID, name, manufacturer/model metadata where useful, reachability, room membership. |
| HMService | ServiceSummary | UUID, service type, name, user-interactive status, related accessory, controls. |
| HMCharacteristic | CapabilitySnapshot | UUID, characteristic type, readable/writable/event properties, metadata, typed value, freshness, pending/error. |

HMCharacteristic.value is Any? and its interpretation depends on the characteristic type. Standard characteristic types may use Boolean, number, string, data, or documented enumerations. HMCharacteristicMetadata can describe units, bounds, and related presentation information. Do not display a raw value without mapping the type and unit to a known product capability.

Filter deliberately:

1. Select the home explicitly.
2. Include the rooms needed for the user outcome.
3. Filter accessories by the product’s supported vendor or service policy when appropriate.
4. Include only user-interactive services for the primary task surface.
5. Choose characteristics by documented type and capability, not by array position.
6. Retain hidden or technical services only when a specific diagnostic route needs them.

An app can expose a focused service view without trying to reproduce every configuration field in Apple Home. It should still respect names, room assignments, and changes made elsewhere.

## Read, write, and reconcile one characteristic

The reliable control route is:

1. Resolve the current service and characteristic by UUID and supported type.
2. Check that the characteristic is readable, writable, and/or notification-capable as required.
3. Inspect metadata and validate the proposed value.
4. Perform an explicit read when a consequential decision needs fresh state.
5. Render pending, stale, unreachable, and unknown states.
6. Require confirmation for locks, garage doors, alarms, heaters, or similarly surprising actions.
7. Write the validated value.
8. Reconcile the completion result with the next characteristic report.

Use an app-owned control state:

~~~text
known(value, source, timestamp)
  -> userIntent(value)
  -> pending(value)
  -> reported(value)
  -> failed(previousValue, error)
  -> stale(lastKnownValue, lastSeen)
  -> unreachable(lastKnownValue)
  -> unknown
~~~

The completion handler says that HomeKit processed the request, not that every physical effect is complete. A garage door may still be moving; a thermostat may apply a value later; a sensor may report a different value immediately. Show the operation state and accept subsequent framework updates as reconciliation evidence.

For continuous numeric controls, debounce app-owned intent and serialize writes according to the target’s needs. Do not assume that every accessory can accept a stream of writes at slider cadence. For Boolean controls, use a Toggle only when the current value and target value are unambiguous. For one-shot actions, use a Button with a result state rather than a Toggle that pretends an action has a persistent Boolean state.

## Observing changes made elsewhere

Enable notifications only for the characteristics the surface needs and only while the lifecycle owner needs them. Use HomeKit delegates and characteristic callbacks to observe:

- changes made in Apple Home or another HomeKit app;
- accessory-reported sensor changes;
- service or characteristic removal;
- accessory reachability changes;
- room/name/topology changes;
- notification registration errors.

Notifications are not guaranteed historical records. If the app was not running, the accessory was unreachable, or notification registration failed, re-read the current value and mark the freshness boundary. Do not infer every intermediate transition from the final callback.

When the app needs background or remote behavior, verify the actual supported HomeKit route, entitlement, process lifetime, and device configuration. Do not promise continuous background monitoring merely because a delegate exists. A foreground device, a Home hub, and a server-backed automation are different authorities and require separate evidence.

## Setup is a system-owned trust surface

For a user-requested HomeKit accessory addition, use the documented system setup flow. HMHome.addAndSetupAccessories can launch the interactive flow, while HMAccessorySetupManager.performAccessorySetup(using:) is the newer directed setup route and returns an HMAccessorySetupResult with the identifiers of the configured accessories and home. The setup UI can locate the accessory, verify the code, name services, and assign rooms.

The app-owned SwiftUI preparation screen should state:

- which home will receive the accessory;
- whether the physical device or setup code is needed;
- what the system flow will ask the person to do;
- what information stays in Apple’s home model;
- what happens on cancellation, denial, invalid code, or unsupported hardware.

Do not rebuild Apple’s pairing sheet with a decorative glass modal. Do not treat sheet dismissal as proof of a configured, reachable, or usable accessory. Refresh the HomeKit projection after setup and reconcile the returned identifiers with the selected home.

## MatterSupport commissioning boundary

MatterSupport lets an app add compatible Matter accessories to its ecosystem. The route is broader than a QR scanner:

~~~text
runtime support check
  -> build MatterAddDeviceRequest topology
  -> apply DeviceCriteria when the product can filter safely
  -> optionally provide a validated onboarding payload
  -> perform from an explicit user action
  -> extension handler validates credentials and commissions
  -> configure home/room/network choices
  -> reconcile ecosystem state
~~~

MatterAddDeviceRequest.DeviceCriteria can describe all devices, vendor/product/serial/commissioning identifiers, fabric identity, and compound all/any/not predicates. Use the narrowest safe filter. A filter is not device authentication; the commissioning flow and the extension handler still need to validate the result.

An extension request handler can own ecosystem-specific steps such as credential validation, commissioning, room configuration, and network association. Keep onboarding payloads, credentials, attestation material, and network details out of analytics and AI prompts. The MatterSupport documentation describes system-managed setup and notes that framework calls return errors for Mac Catalyst apps; record those target boundaries explicitly.

Treat these outcomes separately:

| Outcome | UI state |
| --- | --- |
| User cancelled | Setup cancelled; no claim that anything was added. |
| Access denied | Explain entitlement/permission or Settings action. |
| Unsupported | Preserve non-setup features and identify the unsupported target/device. |
| Commissioning failed | Show safe retry and preserve no secret payload in logs. |
| Commissioned | Re-read ecosystem state and show the resulting device identity. |
| Commissioned but not reachable | Device exists in the ecosystem but is not ready for control. |

## Scenes, automations, and physical side effects

HomeKit action sets represent groups of actions that user-facing interfaces may call scenes. A proposed scene should be a typed list of characteristic writes with a selected home, source revision, validation result, and human-readable explanation.

~~~text
natural-language request or button
  -> candidate services
  -> current topology and capability resolution
  -> typed values and range checks
  -> safety policy
  -> user review
  -> create/update/execute scene or write characteristic
  -> completion and reconciliation
~~~

Do not describe a group as a guaranteed sequence unless the target API and product behavior establish that guarantee. A model-generated phrase such as “make the house safe” is not an executable command. Resolve it to exact devices, exact values, and exact consequences before asking for confirmation.

For locks, garage doors, heaters, alarms, and similar controls:

- show the selected home and room;
- show the exact device and target state;
- make the confirmation action explicit;
- avoid a silent side effect from an AI suggestion or system shortcut;
- keep the failure state visible;
- provide a safe retry or manual route.

## SwiftUI and Liquid Glass composition

Use SwiftUI semantic controls and let Liquid Glass organize app-owned control groups:

~~~text
context: selected home and room
  glass header or compact context group
service state: value, unit, reachability, freshness
  native control or action button
  pending / success / failure result
detail route: secondary characteristics and setup
AI route: proposal, evidence, validation, explicit action
~~~

Liquid Glass is not a truth source. Keep the material bounded to functional groups, preserve readable state and contrast, and provide an opaque or system-material fallback for reduced transparency, increased contrast, unsupported targets, and accessibility settings. Keep HomeKit permission, Apple Home setup, and Matter commissioning system-owned.

Avoid:

- a separate floating glass capsule for every characteristic;
- a glossy toggle that animates to the desired value before the write succeeds;
- translucent text that hides a stale or unreachable label;
- a cloned Apple Home tab bar, icon set, or private visual language;
- a model-generated command presented as if it came from the accessory.

Apple-like polish comes from semantic hierarchy, system routes, names and rooms that agree with Apple Home, adaptive layout, and truthful feedback.

## On-device AI proposal boundary

Foundation Models can summarize a selected home snapshot, answer a question about visible device state, or draft a scene proposal. It must not be the authority for:

- whether HomeKit access is authorized;
- which device UUID a phrase refers to;
- whether a characteristic is writable or within range;
- whether a lock, door, alarm, or heater action is safe;
- whether a write succeeded;
- whether a device is physically reachable;
- whether an occupant is home or safe;
- whether the app should upload the home graph.

Use a typed proposal tied to a source revision:

~~~swift
struct HomeControlProposal {
    let sourceHomeID: UUID
    let sourceTopologyRevision: Int
    let writes: [CharacteristicWrite]
    let explanation: String
    let warnings: [String]
    let requiresConfirmation: Bool
}
~~~

Before apply:

1. Verify the selected home and each service/characteristic still exists.
2. Verify the topology revision or re-resolve and show changed context.
3. Validate typed values, metadata bounds, write permissions, and safety policy.
4. Show the exact devices, rooms, values, and consequences.
5. Require explicit confirmation for the product’s side-effect class.
6. Perform through the single command owner.
7. Reconcile completion and subsequent reports.

Keep prompts minimal and local. Exclude cameras, microphones, locks, occupancy, private room names, and network credentials unless the person explicitly selected the context and the feature genuinely needs it. A generated explanation may be wrong; the UI should still be usable without it.

## Accessibility and alternate input

Use semantic SwiftUI controls first:

- Toggle for a stable Boolean state;
- Slider or Stepper for a bounded numeric value with visible unit;
- Picker for a documented enumeration;
- Button for a one-shot action;
- confirmation dialog for material side effects.

The accessibility label should identify home, room, service, current state, freshness, and action. The accessibility value should not read a raw Any value or claim “on” when the app only has a stale last-known value. Expose a custom accessibility action only when it has the same validation and confirmation path as the visible control.

Test:

- VoiceOver reading order and focus after asynchronous reconciliation;
- Voice Control names for device and room;
- Switch Control and Full Keyboard Access;
- hardware keyboard commands and pointer activation;
- Dynamic Type and long localized room/service names;
- increased contrast, reduced transparency, and reduced motion;
- compact width and iPad split-view layouts.

Do not make color, blur, or animation the only indication of reachability, pending, or success.

## Performance, energy, and privacy

Home dashboards can become expensive when they observe every characteristic or repeatedly rebuild a large graph. Prefer:

- one manager and one reconciliation owner;
- targeted services and characteristics;
- notifications only for visible or product-required values;
- value projections rather than passing the full framework graph into every view;
- debounced search and writes;
- cancellation when a detail route disappears;
- signposts around topology refresh and command latency;
- no polling loop when HomeKit notification/delegate routes suffice.

Treat home data as sensitive. Do not send a full HomeKit graph to a cloud model just to answer a local question. Keep secrets, onboarding payloads, credentials, and raw device identifiers out of logs. The App Store Review and Apple developer terms impose product-purpose and data-use constraints; verify the current text for the target release.

## Evidence boundary

A SwiftUI preview proves injected rendering. A HomeKit Accessory Simulator run proves a simulated route. A signed physical-device run with an actual accessory proves a different gate. MatterSupport setup, HomeKit authorization, Apple Home changes, and the intended release archive are separate evidence.

Minimum evidence packet:

- target membership, HomeKit capability, NSHomeKitUsageDescription, signing, and any Matter extension configuration;
- authorization allow, deny, revoke, and restricted behavior;
- no home, multiple homes, room changes, removed/blocked/unreachable accessories, and external Apple Home changes;
- characteristic read/write/notification, metadata/range, pending, stale, and error fixtures;
- HomeKit Accessory Simulator route for deterministic states;
- representative physical accessory route for reachability and real side effects;
- Matter supported/unsupported, criteria, onboarding, cancellation, credential/commissioning, network, room, and post-setup reconciliation;
- AI proposal with stale topology and invalid-value rejection;
- VoiceOver, Dynamic Type, alternate input, reduced effects, and localization task evidence;
- release target, archive, entitlements, privacy configuration, and App Review review.

## Sources

- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Enabling HomeKit in your app](https://developer.apple.com/documentation/homekit/enabling-homekit-in-your-app)
- [Configuring HomeKit access](https://developer.apple.com/documentation/xcode/configuring-homekit-access)
- [NSHomeKitUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nshomekitusagedescription)
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
- [commissionDevice(in:onboardingPayload:commissioningID:)](https://developer.apple.com/documentation/mattersupport/matteradddeviceextensionrequesthandler/commissiondevice%28in%3Aonboardingpayload%3Acommissioningid%3A%29)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [HomeKit Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/homekit)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
