# HomeKit and Matter automation route

Use this route when the product needs to discover, display, set up, control, or automate connected home features while remaining aligned with Apple Home and the user’s permission choices. The route is intentionally capability-first:

~~~text
user outcome
  -> target/capability/permission check
  -> shared HomeKit topology or Matter setup state
  -> deterministic characteristic/action model
  -> optional on-device AI proposal
  -> validation and user confirmation
  -> system/accessory side effect
  -> reconciliation and evidence
~~~

This page is an architecture recipe, not a compiled sample or a claim that HomeKit/Matter works in this documentation workspace.

## Choose the narrowest route

| Need | Route | Do not add |
| --- | --- | --- |
| Show a selected service’s state | HMHomeManager -> HMHome -> HMAccessory -> HMService -> HMCharacteristic | A second full home database or a cloud sync layer without a product requirement. |
| Toggle or set a value | Characteristic property/metadata validation -> read if needed -> write -> reconcile | Optimistic canonical state, blind writes, or a control that ignores unreachable state. |
| Watch a sensor or external Home app change | Characteristic notifications plus HomeKit delegates | A polling loop that treats cached values as fresh truth. |
| Add a HomeKit accessory | HMHome.addAndSetupAccessories or HMAccessorySetupManager | A custom pairing flow that duplicates Apple’s system UI. |
| Commission a Matter device into an ecosystem | MatterAddDeviceRequest -> optional extension handler -> ecosystem reconciliation | Collecting Wi-Fi credentials or assuming a successful sheet means the device is ready. |
| Create a scene | Validate a typed list of characteristic writes -> HMActionSet -> review -> execute | Natural-language text directly executing side effects. |
| Explain or draft home actions with AI | Read-only selected context -> typed proposal -> deterministic validator -> confirmation | Prompting the entire home graph or allowing the model to write directly. |

## State model

Keep app-owned state separate from framework objects and generated output:

~~~swift
struct HomeSnapshot {
    var selectedHomeID: UUID?
    var rooms: [RoomSummary]
    var services: [ServiceSnapshot]
    var authorization: AuthorizationState
    var topologyRevision: Int
}

struct ServiceSnapshot {
    var serviceID: UUID
    var homeID: UUID
    var roomName: String?
    var displayName: String
    var readableValue: AnyHashable?
    var writable: Bool
    var reachable: Bool
    var freshness: Freshness
    var capabilities: Set<Capability>
}

struct AutomationProposal {
    var homeID: UUID
    var writes: [CharacteristicWrite]
    var sceneName: String?
    var explanation: String
    var sourceContext: [SourceSpan]
    var validation: ValidationState
}
~~~

The exact model types should be chosen in the target project. The important boundary is ownership:

- HomeKit owns the shared home graph and accessory state.
- The app owns presentation selection, local drafts, evidence metadata, and its own feature configuration.
- The AI owns no canonical state. It emits a proposal with source context.
- A validated user action owns the decision to write or execute.
- The completion/delegate/notification path owns reconciliation.

## Route A: bootstrap the shared home model

1. Add the HomeKit capability to the app target and the appropriate HomeKit usage description.
2. Create one HMHomeManager for the app’s HomeKit activities.
3. Handle authorization and manager/home delegate updates.
4. Choose the selected home explicitly; support multiple homes where the product’s outcome requires it.
5. Build a small presentation projection of rooms and user-interactive services.
6. Subscribe to relevant changes and rebuild the projection when the shared database changes elsewhere.
7. Display no-home, denied, loading, and unavailable states before showing controls.

Do not store the framework object graph in a long-lived view model without a lifecycle policy. Keep references short-lived or actor/queue-owned as appropriate for the selected SDK, and test the callback/thread behavior in the real target.

## Route B: control one characteristic safely

For a control:

1. Resolve the service by current HomeKit identity and the app’s product filter.
2. Find the characteristic by a supported type or typed capability adapter.
3. Check readable/writable/event properties and metadata.
4. If the control depends on fresh state, call an explicit read before presenting a consequential choice.
5. Validate the proposed value against the characteristic’s metadata and the product’s safety policy.
6. Set a pending state and prevent conflicting writes unless the product intentionally serializes them.
7. Call the write API.
8. Reconcile the completion result and subsequent characteristic update.
9. Preserve the last known state with a stale marker when the accessory becomes unreachable.

For a slider, debounce app-owned UI intent but do not assume every characteristic supports a continuous stream of writes. The target needs a rate, cancellation, and error policy that matches the physical accessory and selected control. For a lock or garage door, favor an explicit button and outcome over a speculative toggle.

## Route C: observe external changes

HomeKit is shared with Apple Home and other apps. A notification or delegate callback can represent:

- a person changing a service in Apple Home;
- an accessory sensor changing independently;
- a room, name, or accessory topology change;
- a device becoming unreachable or reachable;
- a notification registration or setup failure.

Reconcile by identity, not list position:

~~~text
callback
  -> locate current object by identifier
  -> verify it still belongs to the selected home
  -> update projection and freshness
  -> invalidate stale proposals referencing removed/changed objects
  -> preserve focus and announce only material changes
~~~

Do not use a notification as proof of every event that happened while the app was terminated. If the product needs an audit history, define and verify a separate event source; HomeKit’s current value/notification APIs are not a general event log.

## Route D: add and set up a device

### HomeKit setup

Prepare a user-initiated setup action with the selected home. Choose the high-level add-and-setup flow when the standard system UI should find and configure the device. Use the directed HMAccessorySetupRequest/HMAccessorySetupManager route when a current SDK and product flow require a home ID, suggested name/room, or setup payload.

After the system flow returns:

1. Refresh HomeKit topology from the manager/home callbacks.
2. Find the new accessory/service by current identity.
3. Show its reachability and user-interactive services.
4. Treat setup completion and device reachability as separate states.

### Matter setup

Use MatterSupport only in a target and platform configuration that supports it:

1. Gate with MatterAddDeviceRequest.isSupported.
2. Build topology and device criteria from the product’s ecosystem contract.
3. Provide a validated MTRSetupPayload when the product has one; otherwise use the system’s scan path where appropriate.
4. Set shouldScanNetworks only when the workflow needs network choices.
5. Call perform from a user action and show the system flow’s result.
6. If an extension request handler is part of the ecosystem, validate credentials/attestation, select a home/room/network, commission, and surface errors.
7. Reconcile the resulting accessory in the ecosystem that the product owns.

Matter support in iOS emphasizes user permission and privacy around adding accessories and network credentials. Preserve that trust model in the app copy and do not ask the person to repeat sensitive network setup unnecessarily.

## Route E: build a scene or automation

Model an automation as typed writes and conditions, not a sentence:

~~~text
SceneDraft
  home
  name
  target services
  characteristic writes
  optional event/time trigger
  safety classification
  explanation/provenance
  validation errors
  confirmation status
~~~

Validation should reject:

- a service outside the selected home;
- a characteristic without write permission;
- an unsupported or out-of-range value;
- an unreachable or removed device when the product requires current access;
- a scene that changes a safety-sensitive device without explicit confirmation;
- an AI proposal whose source context is stale or incomplete.

When using HMActionSet, remember that the API calls the collection an action set while the interface should call it a scene. Do not claim an order between actions unless the product has a separate guarantee. Triggers and scheduled execution require their own proof of persistence, recurrence, home state, and failure handling.

## Route F: on-device AI proposal

Give the model the smallest useful context:

~~~text
allowed context
  selected home name, if user chose it
  selected room/service summaries
  normalized readable values and freshness
  product vocabulary and safety policy
  no secrets, tokens, raw camera/audio, or unrelated rooms

model output
  typed scene draft
  explanation
  uncertainty
  source references
~~~

Then:

1. Decode into a typed proposal.
2. Resolve candidate services against the current HomeKit graph.
3. Revalidate after any topology or characteristic update.
4. Show affected devices, old/current values, proposed values, and timing.
5. Confirm with the person.
6. Create or execute only the approved action.
7. Reconcile and retain the outcome separately from the generated text.

If the device is unavailable, the model should explain that it cannot confirm the action rather than pretending to have completed it. A local model’s availability does not grant HomeKit authorization or physical-world authority.

## Fallbacks

| Failure | Product fallback |
| --- | --- |
| HomeKit denied/restricted | Explain access, provide Settings guidance, and keep app-owned local features available. |
| No homes | Offer a clear setup path or show a private demo/empty state without fake device values. |
| Accessory unreachable | Preserve identity and last known state as stale; disable unsafe writes and offer retry. |
| Characteristic not writable | Render read-only state and explain the limitation. |
| Setup cancelled | Return to the setup preparation screen without claiming a device was added. |
| Invalid Matter payload | Offer scan/retry or support instructions; discard untrusted payload data. |
| Matter unsupported | Keep HomeKit or non-Matter routes visible only when they truly remain available. |
| AI unavailable | Use deterministic filters, manual controls, and typed scene templates. |
| Proposal stale | Recompute or require the person to review current state again. |
| Write failed | Keep the prior known value, report failure, and do not unlock premium or safety state from the local button animation. |

## Build slices

Implement in slices that expose the evidence boundary:

1. HomeKit capability, usage string, one manager, authorization, and no-home state.
2. A static projection of one home’s user-interactive services.
3. One read-only characteristic with freshness and unreachable states.
4. One safe write with pending/success/failure reconciliation.
5. External-change notifications and topology removal.
6. HomeKit setup or Matter commissioning in the target’s actual entitlement configuration.
7. A typed scene draft and manual confirmation.
8. On-device AI proposal generation with deterministic validation and no direct side effect.
9. Liquid Glass/adaptive/accessibility polish after the state contract is stable.
10. Simulator, physical accessory, Matter, privacy, performance, and release proof.

## Sources

- [HomeKit](https://developer.apple.com/documentation/homekit)
- [HMHomeManager](https://developer.apple.com/documentation/homekit/hmhomemanager)
- [HMHome](https://developer.apple.com/documentation/homekit/hmhome)
- [HMAccessory](https://developer.apple.com/documentation/homekit/hmaccessory)
- [HMService](https://developer.apple.com/documentation/homekit/hmservice)
- [HMCharacteristic](https://developer.apple.com/documentation/homekit/hmcharacteristic)
- [HMActionSet](https://developer.apple.com/documentation/homekit/hmactionset)
- [HMAccessorySetupRequest](https://developer.apple.com/documentation/homekit/hmaccessorysetuprequest)
- [Performing accessory setup](https://developer.apple.com/documentation/homekit/hmaccessorysetupmanager/performaccessorysetup%28using%3Acompletionhandler%3A%29)
- [Interacting with a home automation network](https://developer.apple.com/documentation/homekit/interacting-with-a-home-automation-network)
- [MatterSupport](https://developer.apple.com/documentation/mattersupport)
- [MatterAddDeviceRequest](https://developer.apple.com/documentation/mattersupport/matteradddevicerequest)
- [MatterAddDeviceExtensionRequestHandler](https://developer.apple.com/documentation/mattersupport/matteradddeviceextensionrequesthandler)
- [Matter support in iOS](https://developer.apple.com/apple-home/matter/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
