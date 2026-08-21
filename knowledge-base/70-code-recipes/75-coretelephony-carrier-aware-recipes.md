# Core Telephony carrier-aware code recipes

These are compile-oriented sketches for a named iOS target. They keep carrier observations, Network path state, request results, system handoff, and AI proposals separate. Confirm the exact SDK signatures and availability before compiling.

## 1. Snapshot cellular service state

~~~swift
import CoreTelephony

struct CellularObservation: Sendable {
    var dataServiceIdentifier: String?
    var radioAccessTechnologyByService: [String: String]
    var cellularDataState: CTCellularDataRestrictedState
    var observedAt = Date()
}

final class CellularObservationOwner {
    private let telephonyInfo = CTTelephonyNetworkInfo()
    private let cellularData = CTCellularData()
    private(set) var observation: CellularObservation

    init() {
        observation = CellularObservation(
            dataServiceIdentifier: nil,
            radioAccessTechnologyByService: [:],
            cellularDataState: cellularData.restrictedState
        )

        cellularData.cellularDataRestrictionDidUpdateNotifier = { [weak self] state in
            // Reconcile on the app's observation executor.
            self?.updateCellularDataState(state)
        }
    }

    func refresh() {
        observation.dataServiceIdentifier = telephonyInfo.dataServiceIdentifier
        observation.radioAccessTechnologyByService =
            telephonyInfo.serviceCurrentRadioAccessTechnology ?? [:]
        observation.cellularDataState = cellularData.restrictedState
        observation.observedAt = Date()
    }

    private func updateCellularDataState(
        _ state: CTCellularDataRestrictedState
    ) {
        observation.cellularDataState = state
        observation.observedAt = Date()
    }
}
~~~

The production owner should marshal callback updates to one executor, publish immutable snapshots, and implement the current CTTelephonyNetworkInfo delegate for service changes. Do not keep deprecated single-service carrier properties as the source of truth.

## 2. Translate policy without claiming reachability

~~~swift
import CoreTelephony

enum CellularTransferDecision: Sendable {
    case proceed
    case waitForWiFi
    case offerOfflineAlternative
    case unknown
}

func decideTransfer(
    cellularState: CTCellularDataRestrictedState,
    hasUsableWiFiPath: Bool,
    isLargeTransfer: Bool
) -> CellularTransferDecision {
    switch cellularState {
    case .restricted where !hasUsableWiFiPath && isLargeTransfer:
        return .waitForWiFi
    case .restricted:
        return .offerOfflineAlternative
    case .notRestricted:
        return .proceed
    default:
        return .unknown
    }
}
~~~

This function is a policy layer, not a network test. Pair it with NWPathMonitor and an actual URLSession result. A permitted cellular policy does not mean that a server request will succeed.

## 3. Observe path state beside Core Telephony

~~~swift
import Network

final class PathOwner {
    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "path-observation")

    func start(onChange: @escaping (NWPath) -> Void) {
        monitor.pathUpdateHandler = { path in
            onChange(path)
        }
        monitor.start(queue: queue)
    }

    func stop() {
        monitor.cancel()
    }
}
~~~

Keep the path observer alive for the feature scope, not only while a view is visible. Combine path state with request results and an offline cache; do not use a radio-access value as a substitute for path observation.

## 4. Request and verify a preferred network slice

~~~swift
import CoreTelephony

func preferGamingSlice() async -> Result<CTSlicingManager.Slice?, Error> {
    let manager = CTSlicingManager.shared

    do {
        let available = try await manager.availableSliceAppCategories
        guard available.contains(.gaming) else {
            return .success(nil)
        }

        try await manager.activatePreferredSliceForCategory(.gaming)

        // Create new Network connections only after activation.
        let active = try await manager.activeSlices
        return .success(active.first { $0.appCategory == .gaming })
    } catch {
        return .failure(error)
    }
}
~~~

Treat a nil result, an unavailable category, and an error as normal fallback states. The active slice is an observed route, not a latency guarantee. The target also needs the required entitlement and carrier/device support.

## 5. Observe iPhone quick-switch state

~~~swift
import CoreTelephony

func readQuickSwitchState() async -> CTQuickSwitchManager.State? {
    let manager = CTQuickSwitchManager()

    do {
        return try await manager.deviceState
    } catch {
        return nil
    }
}
~~~

The production route can set the manager delegate and register for documented background quick-switch events when the app is eligible. Make the handoff idempotent and checkpoint state before treating active/passive changes as a completed migration.

## 6. Gate the carrier eSIM route

~~~swift
import CoreTelephony

func canOfferCarrierPlanProvisioning() -> Bool {
    let provisioning = CTCellularPlanProvisioning()
    return provisioning.supportsCellularPlan()
}

func addCarrierPlan(
    request: CTCellularPlanProvisioningRequest,
    completion: @escaping (CTCellularPlanProvisioningAddPlanResult) -> Void
) {
    let provisioning = CTCellularPlanProvisioning()
    guard provisioning.supportsCellularPlan() else {
        return
    }

    provisioning.addPlan(request: request, completionHandler: completion)
}
~~~

This is only an eligible carrier-app route. The entitlement, plan properties, region, hardware, user consent, and the success/cancel/fail/unknown result all require target-specific proof. A general app should not expose this as if it could provision arbitrary plans.

## 7. Project observations into a SwiftUI status surface

~~~swift
import Observation
import SwiftUI

@MainActor
@Observable
final class ConnectivityModel {
    var transferDecision = "Checking policy"
    var pathSummary = "Path unknown"
    var sliceSummary = "Preferred route not requested"
    var quickSwitchSummary = "Active-device state unknown"
}

struct ConnectivityStatusView: View {
    @State private var model = ConnectivityModel()

    var body: some View {
        List {
            Section("Current task") {
                Text(model.transferDecision)
            }
            Section("Observed conditions") {
                Text(model.pathSummary)
                Text(model.sliceSummary)
                Text(model.quickSwitchSummary)
            }
            Section("Recovery") {
                Button("Continue offline") { }
                Button("Retry when ready") { }
            }
        }
        .navigationTitle("Connection")
    }
}
~~~

Keep the status language derived from facts. Add Liquid Glass to a compact inspector or review sheet after the plain semantic layout works in light/dark, Dynamic Type, VoiceOver, and reduced motion.

## 8. Validate an AI transfer proposal

~~~swift
struct TransferProposal: Codable, Sendable {
    let action: String
    let requiresWiFi: Bool
    let explanation: String
}

func validate(
    _ proposal: TransferProposal,
    cellularRestricted: Bool,
    knownActions: Set<String>
) -> Bool {
    guard knownActions.contains(proposal.action) else {
        return false
    }
    if proposal.requiresWiFi && !cellularRestricted {
        return true
    }
    return proposal.action == "wait" || proposal.action == "offline"
}
~~~

The model may suggest a policy explanation or a smaller offline option. The deterministic app layer owns the current policy, path, user approval, request, cache, and retry. Never allow the model to activate network slicing, move credentials, provision an eSIM, or silently change account state.

## Sources

- [Core Telephony](https://developer.apple.com/documentation/coretelephony)
- [CTTelephonyNetworkInfo](https://developer.apple.com/documentation/coretelephony/cttelephonynetworkinfo)
- [CTCellularData](https://developer.apple.com/documentation/coretelephony/ctcellulardata)
- [CTSlicingManager](https://developer.apple.com/documentation/coretelephony/ctslicingmanager)
- [iPhone quick switch](https://developer.apple.com/documentation/coretelephony/iphone-quick-switch)
- [CTCellularPlanProvisioning](https://developer.apple.com/documentation/coretelephony/ctcellularplanprovisioning)
- [Network](https://developer.apple.com/documentation/network)
- [NWPathMonitor](https://developer.apple.com/documentation/network/nwpathmonitor)
- [URLSession](https://developer.apple.com/documentation/foundation/urlsession)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

***
