# HomeKit and Matter code recipes

These are compile-oriented route sketches for a selected iOS target. They are not compiled in this documentation-only workspace and do not prove HomeKit authorization, physical accessory behavior, Matter commissioning, ecosystem configuration, extension lifecycle, safety, accessibility, or release readiness. Re-check the current SDK signatures and availability in Xcode before copying them.

## Recipe 1: own one HomeKit manager and project the selected home

HomeKit is a shared system database. Keep one manager for the app’s HomeKit work, update a small app-owned projection from delegate callbacks, and do not assume the primary home is the only home.

~~~swift
import HomeKit

@MainActor
final class HomeStore: NSObject, HMHomeManagerDelegate {
    private let manager = HMHomeManager()

    private(set) var authorization: HMHomeManagerAuthorizationStatus = .notDetermined
    private(set) var selectedHome: HMHome?
    private(set) var homes: [HMHome] = []

    override init() {
        super.init()
        manager.delegate = self
        authorization = manager.authorizationStatus
    }

    func homeManagerDidUpdateHomes(_ manager: HMHomeManager) {
        homes = manager.homes
        selectedHome = selectedHome.flatMap { old in
            homes.first { $0.uniqueIdentifier == old.uniqueIdentifier }
        } ?? manager.primaryHome
    }

    func chooseHome(_ home: HMHome) {
        guard homes.contains(where: { $0.uniqueIdentifier == home.uniqueIdentifier }) else {
            return
        }
        selectedHome = home
    }
}
~~~

Verify the exact delegate callback and authorization enum cases against the selected SDK. In production, add the HomeKit capability, NSHomeKitUsageDescription, signing, denial/restriction UI, no-home behavior, and external-change reconciliation.

## Recipe 2: read, validate, observe, and write one characteristic

A characteristic value may be cached, and the accessory or another app can change it. Check properties and metadata before presenting a control.

~~~swift
import HomeKit

final class CharacteristicAdapter: NSObject, HMAccessoryDelegate {
    func refresh(_ characteristic: HMCharacteristic) {
        guard characteristic.properties.contains(HMCharacteristicPropertyReadable) else {
            return
        }

        characteristic.readValue { error in
            guard error == nil else {
                // Keep the prior value with a stale/unavailable state.
                return
            }
            let currentValue = characteristic.value
            let metadata = characteristic.metadata
            // Decode only the value types allowed by this characteristic.
            _ = (currentValue, metadata)
        }
    }

    func observe(_ characteristic: HMCharacteristic) {
        guard characteristic.properties.contains(
            HMCharacteristicPropertySupportsEventNotification
        ) else {
            return
        }

        characteristic.enableNotification(true) { error in
            // Treat registration failure as a visible capability state.
            _ = error
        }
    }

    func write(_ value: Any, to characteristic: HMCharacteristic) {
        guard characteristic.properties.contains(HMCharacteristicPropertyWritable) else {
            return
        }

        // Validate range, unit, mode, and safety policy before this call.
        characteristic.writeValue(value) { error in
            // Reconcile from the completion and a later delegate update.
            _ = error
        }
    }

    func accessory(
        _ accessory: HMAccessory,
        service: HMService,
        didUpdateValueFor characteristic: HMCharacteristic
    ) {
        // Another app or the physical accessory changed the value.
        _ = (accessory, service, characteristic)
    }
}
~~~

The property constants and delegate signature are intentionally shown as a route sketch. Test readable, writable, event-capable, hidden, range, stale, unreachable, removed, rejected, and transitioning states.

## Recipe 3: use system-owned HomeKit accessory setup

Use the standard home setup flow when a person wants to add an accessory. Do not replace it with a custom pairing sheet.

~~~swift
import HomeKit

@MainActor
func addAccessories(to home: HMHome) {
    home.addAndSetupAccessories { error in
        if let error {
            // Cancellation, unsupported hardware, or setup errors remain visible.
            _ = error
            return
        }

        // Refresh from HMHomeManager/HMHome callbacks.
        // Do not assume the new accessory is reachable yet.
    }
}
~~~

For a directed current-SDK route:

~~~swift
import HomeKit

@MainActor
func performDirectedSetup(for homeID: UUID, suggestedName: String?) async {
    let request = HMAccessorySetupRequest()
    request.homeUniqueIdentifier = homeID
    request.suggestedAccessoryName = suggestedName

    // Supply a supported setup payload only when the product owns a valid one.
    // request.payload = validatedPayload

    let setupManager = HMAccessorySetupManager()
    do {
        let result = try await setupManager.performAccessorySetup(using: request)
        // Reconcile the result with the current home graph.
        _ = result
    } catch {
        // Keep the setup screen useful after cancellation or failure.
    }
}
~~~

The manager initializer, async overload, payload type, and availability must be checked in the selected SDK. A completion callback or setup result does not replace post-setup topology and reachability verification.

## Recipe 4: start a MatterSupport setup request

MatterSupport is an ecosystem commissioning route. It is distinct from using HomeKit to control a Matter accessory already present in Apple Home.

~~~swift
import MatterSupport
import Matter

@MainActor
func addMatterDevice(
    topology: MatterAddDeviceRequest.Topology,
    criteria: MatterAddDeviceRequest.DeviceCriteria,
    payload: MTRSetupPayload?
) async {
    guard MatterAddDeviceRequest.isSupported else {
        // Offer a non-Matter or manual setup fallback.
        return
    }

    let request = MatterAddDeviceRequest(
        topology: topology,
        setupPayload: payload,
        showing: criteria,
        shouldScanNetworks: true
    )

    do {
        try await request.perform()
        // Reconcile the ecosystem’s accessory state after the system flow.
    } catch {
        // Distinguish cancellation, unsupported device, invalid payload,
        // network failure, and commissioning failure in the product state.
    }
}
~~~

The exact topology, criteria, payload, and initializer availability are SDK-sensitive. Do not log onboarding payloads or network credentials. If the ecosystem requires an extension, add the extension target and request handler rather than putting commissioning logic in the view.

## Recipe 5: model a scene as a typed proposal

Generated text should never be the direct input to a HomeKit write. Decode into a typed proposal, resolve every target against current state, validate values, and require confirmation.

~~~swift
struct CharacteristicWrite {
    var serviceID: UUID
    var characteristicType: String
    var value: SendableValue
}

struct SceneProposal {
    var name: String
    var writes: [CharacteristicWrite]
    var explanation: String
    var sourceContext: [String]
    var validation: ValidationState
}

enum ValidationState {
    case valid
    case stale
    case needsConfirmation
    case rejected(String)
}
~~~

The product’s resolver should:

1. Reject targets outside the selected home.
2. Require a writable characteristic and valid metadata.
3. Revalidate after topology or state changes.
4. Explain the exact services and values.
5. Classify lock, garage, alarm, heater, and other high-consequence writes.
6. Apply only after explicit confirmation.

Foundation Models can create the proposal or explanation, but it does not own the HomeKit graph and cannot grant authorization.

## Recipe 6: construct an action-set route after validation

The API uses action set while the user-facing design should say scene. Confirm the action order limitation before promising a sequence.

~~~swift
import HomeKit

func buildScene(
    named name: String,
    writes: [(HMCharacteristic, Any)],
    in home: HMHome
) {
    home.addActionSet(withName: name) { actionSet, error in
        guard let actionSet, error == nil else {
            return
        }

        for (characteristic, value) in writes {
            let action = HMCharacteristicWriteAction(
                characteristic: characteristic,
                targetValue: value
            )
            actionSet.addAction(action) { error in
                // A failed add invalidates the draft; do not execute blindly.
                _ = error
            }
        }

        // Execute only after every action has been added and the person confirmed.
        home.executeActionSet(actionSet) { error in
            // Reconcile each service from current HomeKit state.
            _ = error
        }
    }
}
~~~

The action-set initializer, completion signatures, and execution APIs should be compiled against the target SDK. Apple’s documentation says actions in an action set execute in an unspecified order; design the scene copy and safety policy accordingly.

## Recipe 7: keep AI context bounded and invalidate stale drafts

Only pass the selected context the person authorized for this task. Do not include the entire home graph by default.

~~~swift
struct AIHomeContext {
    var selectedHomeName: String
    var roomSummaries: [RoomSummary]
    var readableServiceValues: [ServiceValue]
    var safetyPolicyVersion: String
    var topologyRevision: Int
}

func canApply(
    _ proposal: SceneProposal,
    currentTopologyRevision: Int,
    currentValidation: ValidationState
) -> Bool {
    proposal.validation == .needsConfirmation
        && currentTopologyRevision == proposalTopologyRevision(proposal)
        && currentValidation == .needsConfirmation
}
~~~

The revision comparison is illustrative; store it explicitly in the real proposal. If a room or service changes while the review sheet is open, mark the proposal stale and require a fresh review. Use deterministic validators for value ranges, writable properties, selected-home membership, safety class, and confirmation.

## Recipe 8: test the route with a state fixture

Keep framework callbacks at the adapter boundary and test the product state machine with fixtures:

~~~swift
struct HomeRouteFixture {
    var authorization: AuthorizationFixture
    var topology: TopologyFixture
    var service: ServiceFixture
    var writeResult: WriteResultFixture
    var matter: MatterFixture
}

func expectedState(for fixture: HomeRouteFixture) -> HomeRouteState {
    // Exercise no access, no home, stale, unreachable, non-writable,
    // pending, success, rejected, removed, unsupported Matter,
    // cancelled setup, and stale AI proposal branches.
    fatalError("Implement in the selected app target")
}
~~~

Use the HomeKit Accessory Simulator for deterministic service coverage, then repeat the critical route on a signed physical device and a real Matter accessory when those capabilities are part of the product.

## Recipe 9: proof-first route table

| Slice | Local/fixture proof | Physical/system proof |
| --- | --- | --- |
| Authorization/topology | State reducer and no-home fixtures | Signed prompt, denial, multiple homes, external Apple Home change |
| Read/control | Value decoder, metadata/range, write reducer | Physical read/write, unreachable, transition, accessory removal |
| Notifications | Callback-to-projection reducer | Change from Apple Home, another app, and accessory |
| HomeKit setup | Setup state machine | System setup, cancellation, post-setup reachability |
| Matter | Payload/criteria validation | MatterSupport consent, scan/network, attestation, commissioning, ecosystem result |
| Scenes | Typed proposal and action validation | Scene creation/execution/trigger behavior and safety confirmation |
| AI | Prompt fixture, typed decode, stale invalidation | On-device availability, privacy review, user-confirmed side effect |
| Native design | Preview matrices and accessibility identifiers | VoiceOver, Dynamic Type, reduced transparency/motion, compact/wide device |

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
- [MatterSupport](https://developer.apple.com/documentation/mattersupport)
- [MatterAddDeviceRequest](https://developer.apple.com/documentation/mattersupport/matteradddevicerequest)
- [MatterAddDeviceExtensionRequestHandler](https://developer.apple.com/documentation/mattersupport/matteradddeviceextensionrequesthandler)
- [Matter support in iOS](https://developer.apple.com/apple-home/matter/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
