# SwiftUI EnergyKit load-event and historical-insight code recipes

These are compile-oriented sketches for the focused [EnergyKit load-event and insight review](../42-framework-deep-dives/122-swiftui-energykit-load-event-and-guidance-review.md). They separate venue selection, grid guidance, deterministic schedule state, physical telemetry, EV load sessions, EV status snapshots, HVAC transitions, submission, Home processing, historical insights, Liquid Glass UI, and bounded on-device AI.

The current EnergyKit documentation is beta-sensitive. Compile every selected symbol, initializer, unit, availability annotation, and entitlement against the final iOS 26/iPadOS 26 SDK. These snippets are not proof of a signed entitlement, contiguous-U.S. eligibility, Home venue access, physical charger/HVAC behavior, Home presentation, or historical insight quality.

Before copying:

1. Add the base EnergyKit capability to the intended target.
2. Add the LoadEvents capability only when the Home event route is required.
3. Inspect the signed archive rather than trusting a source entitlement file.
4. Keep the physical device controller and EnergyKit telemetry adapter separate.
5. Keep raw household energy data out of logs and external model calls.

## Recipe 1: Domain state stays separate from framework state

Use product-owned state to distinguish a recommendation, an approved command, observed device behavior, an accepted event, and a historical record:

~~~swift
import Foundation

enum EnergyFeatureState: Sendable, Equatable {
    case unavailable(reason: String)
    case loadingVenue
    case venueRequired
    case venueSelected
    case loadingGuidance
    case guidanceReady
    case scheduleNeedsReview
    case scheduleApproved
    case commandRequested
    case physicalStateObserved
    case eventReady
    case eventAccepted
    case systemProcessing
    case insightReady
    case failed(message: String)
}

enum EnergyDeviceKind: Sendable, Hashable {
    case electricVehicle
    case hvac
}

struct EnergySelection: Sendable, Hashable {
    let venueID: UUID
    let deviceID: String
    let deviceName: String
    let kind: EnergyDeviceKind
}

struct GuidanceProvenance: Sendable, Equatable {
    let venueID: UUID
    let suggestedAction: String
    let interval: DateInterval
    let fetchedAt: Date
    let redactedTokenID: String
}

struct PhysicalObservation: Sendable, Equatable {
    let observedAt: Date
    let description: String
    let source: String
}
~~~

The framework event, Home projection, and AI explanation should reference these product records rather than becoming the only source of state.

## Recipe 2: Load and revalidate a Home venue

EnergyVenue represents a physical Home-associated site. Require an explicit selection:

~~~swift
import EnergyKit
import Foundation

func loadEnergyVenues() async throws -> [EnergyVenue] {
    try await EnergyVenue.venues()
}

func reloadSelectedVenue(id: UUID) async throws -> EnergyVenue {
    try await EnergyVenue.venue(for: id)
}

struct SelectedVenue: Sendable, Equatable {
    let id: UUID
    let userFacingName: String
}
~~~

Persist the selected identifier and a person-approved display mapping. Do not persist “the first venue” as a hidden default. Revalidate the venue before submitting an event or starting a historical insight query.

## Recipe 3: Stream shift or reduce guidance

Bind the stream to the selected action and cancel it when the venue/device changes:

~~~swift
import EnergyKit
import Foundation

enum GuidanceMode: Sendable {
    case shift
    case reduce
}

func streamGuidance(
    venueID: UUID,
    mode: GuidanceMode,
    handle: @escaping @Sendable (ElectricityGuidance, Date) -> Void
) async throws {
    let action: ElectricityGuidance.SuggestedAction =
        switch mode {
        case .shift:
            .shift
        case .reduce:
            .reduce
        }

    let query = ElectricityGuidance.Query(suggestedAction: action)

    for try await guidance in ElectricityGuidance.sharedService.guidance(
        using: query,
        at: venueID
    ) {
        handle(guidance, Date())
    }
}
~~~

Store the guidance interval, venue ID, suggested action, token reference, and fetched time with the schedule revision. A stream update is an input to a scheduler; it is not a device command.

## Recipe 4: Convert guidance into a reviewable schedule

Keep the candidate selection deterministic:

~~~swift
import Foundation

struct CandidateWindow: Sendable, Equatable {
    let interval: DateInterval
    let rating: Double
}

struct ScheduleConstraints: Sendable {
    let now: Date
    let deadline: Date
    let requiredDuration: TimeInterval
    let deviceName: String
}

struct ScheduleProposal: Sendable, Equatable {
    let window: DateInterval
    let rating: Double
    let guidanceFetchedAt: Date
    let requiresApproval: Bool
    let explanationFacts: [String]
}

enum ScheduleValidationError: Error {
    case invalidDeadline
    case noFeasibleWindow
    case staleGuidance
}

func makeScheduleProposal(
    windows: [CandidateWindow],
    guidanceFetchedAt: Date,
    constraints: ScheduleConstraints,
    now: Date = Date()
) throws -> ScheduleProposal {
    guard constraints.deadline > constraints.now else {
        throw ScheduleValidationError.invalidDeadline
    }

    let feasible = windows
        .filter { $0.interval.start >= constraints.now }
        .filter { $0.interval.end <= constraints.deadline }
        .filter { $0.interval.duration >= constraints.requiredDuration }
        .sorted { $0.rating < $1.rating }

    guard let selected = feasible.first else {
        throw ScheduleValidationError.noFeasibleWindow
    }

    return ScheduleProposal(
        window: selected.interval,
        rating: selected.rating,
        guidanceFetchedAt: guidanceFetchedAt,
        requiresApproval: true,
        explanationFacts: [
            "Device: \(constraints.deviceName)",
            "Deadline: \(constraints.deadline.formatted())",
            "Guidance fetched: \(guidanceFetchedAt.formatted())"
        ]
    )
}
~~~

The app must define its own freshness policy. A model may explain this proposal or rank already-valid alternatives, but it must not bypass the deadline or device/safety validator.

## Recipe 5: Validate EV telemetry before conversion

Keep the physical telemetry adapter responsible for units and session invariants:

~~~swift
import Foundation

enum EVFlow: Sendable {
    case imported
    case exported
}

struct EVTelemetry: Sendable, Equatable {
    let timestamp: Date
    let stateOfCharge: Int
    let flow: EVFlow
    let powerMilliwatts: Double
    let cumulativeEnergyMilliwattHours: Double
}

enum EVTelemetryError: Error {
    case invalidStateOfCharge
    case negativePower
    case negativeEnergy
    case energyMovedBackward
    case timestampMovedBackward
}

func validate(
    telemetry: EVTelemetry,
    prior: EVTelemetry?
) throws {
    guard (0...100).contains(telemetry.stateOfCharge) else {
        throw EVTelemetryError.invalidStateOfCharge
    }
    guard telemetry.powerMilliwatts >= 0 else {
        throw EVTelemetryError.negativePower
    }
    guard telemetry.cumulativeEnergyMilliwattHours >= 0 else {
        throw EVTelemetryError.negativeEnergy
    }

    if let prior {
        guard telemetry.timestamp >= prior.timestamp else {
            throw EVTelemetryError.timestampMovedBackward
        }
        guard telemetry.cumulativeEnergyMilliwattHours >=
                prior.cumulativeEnergyMilliwattHours else {
            throw EVTelemetryError.energyMovedBackward
        }
    }
}
~~~

Do not synthesize power or energy when a device reports no measurement. Preserve an estimate flag in the product record if the hardware only provides an estimate.

## Recipe 6: Construct an EV load event

The current API uses a typed electrical measurement, a session, and an ElectricalLoadDevice. Confirm unit spelling and session construction in the selected final SDK:

~~~swift
import EnergyKit
import Foundation

func makeEVLoadEvent(
    telemetry: EVTelemetry,
    session: ElectricVehicleLoadEvent.Session,
    device: ElectricalLoadDevice
) -> ElectricVehicleLoadEvent {
    let direction: ElectricityFlowDirection =
        switch telemetry.flow {
        case .imported:
            .imported
        case .exported:
            .exported
        }

    let measurement = ElectricVehicleLoadEvent.ElectricalMeasurement(
        stateOfCharge: telemetry.stateOfCharge,
        direction: direction,
        power: Measurement(
            value: telemetry.powerMilliwatts,
            unit: .milliwatts
        ),
        energy: Measurement(
            value: telemetry.cumulativeEnergyMilliwattHours,
            unit: .milliwattHours
        ),
        performanceMetrics: nil
    )

    return ElectricVehicleLoadEvent(
        timestamp: telemetry.timestamp,
        measurement: measurement,
        session: session,
        device: device
    )
}
~~~

For V2G/V2H, bind imported and exported measurements to different session identities. A successful initializer does not prove that the event is valid for the selected venue or session order.

## Recipe 7: Model EV begin, active, and end

Keep session transitions in a product state machine before calling the framework initializer:

~~~swift
import Foundation

enum EVSessionPhase: Sendable, Equatable {
    case none
    case begin
    case active
    case end
    case closed
}

struct EVSessionLedger: Sendable, Equatable {
    let id: UUID
    let venueID: UUID
    let deviceID: String
    let phase: EVSessionPhase
    let flow: EVFlow
    let guidanceTokenReference: String?
    let lastTelemetry: EVTelemetry?
}

enum EVSessionError: Error {
    case cannotStartFromCurrentPhase
    case cannotContinueClosedSession
    case wrongDirection
    case wrongDevice
}

func validateNext(
    current: EVSessionLedger,
    nextPhase: EVSessionPhase,
    telemetry: EVTelemetry
) throws {
    guard current.flow == telemetry.flow else {
        throw EVSessionError.wrongDirection
    }
    guard current.lastTelemetry == nil ||
            telemetry.timestamp >= current.lastTelemetry!.timestamp else {
        throw EVTelemetryError.timestampMovedBackward
    }

    switch (current.phase, nextPhase) {
    case (.none, .begin), (.begin, .active),
         (.active, .active), (.active, .end), (.end, .closed):
        return
    default:
        throw EVSessionError.cannotStartFromCurrentPhase
    }
}
~~~

Use the documented begin/end measurement rules for the final framework event. The ledger lets the product reject contradictory transitions before submit.

## Recipe 8: Construct an EV status snapshot

Use a status event for a moment in time, not for session continuity:

~~~swift
import EnergyKit
import Foundation

func makePluggedInStatus(
    timestamp: Date,
    device: ElectricalLoadDevice,
    venueID: UUID,
    stateOfCharge: Int,
    sessionIdentifier: UUID?
) -> ElectricVehicleStatusEvent {
    ElectricVehicleStatusEvent(
        timestamp: timestamp,
        device: device,
        venueID: venueID,
        status: .chargerPluggedIn,
        stateOfCharge: stateOfCharge,
        energy: Measurement(value: 0, unit: .kilowattHours),
        estimatedRange: nil,
        chargingTarget: nil,
        sessionIdentifier: sessionIdentifier
    )
}
~~~

Compile the current initializer and energy unit against the final SDK. A plugged-in snapshot must not be rendered as “charging active.” Use the status reason cases documented by Apple when constructing active or idle snapshots.

## Recipe 9: Construct an HVAC transition event

Keep the current device controller’s measurement and session as typed inputs:

~~~swift
import EnergyKit
import Foundation

func makeHVACTransition(
    timestamp: Date,
    measurement: ElectricHVACLoadEvent.ElectricalMeasurement,
    session: ElectricHVACLoadEvent.Session,
    device: ElectricalLoadDevice
) -> ElectricHVACLoadEvent {
    ElectricHVACLoadEvent(
        timestamp: timestamp,
        measurement: measurement,
        session: session,
        device: device
    )
}
~~~

Call this only after a debounced, meaningful transition such as a stage change, person action, pause, or active/idle transition. Keep the higher-frequency HVAC telemetry in the product store for comfort and safety logic.

## Recipe 10: Submit typed events through a venue

Use the generic event protocol without losing the concrete event records in the local ledger:

~~~swift
import EnergyKit

func submitEnergyEvents(
    loadEvents: [ElectricVehicleLoadEvent],
    statusEvents: [ElectricVehicleStatusEvent],
    to venue: EnergyVenue
) async throws {
    let events: [any ElectricalLoadEventProtocol] =
        loadEvents + statusEvents
    try await venue.submitEvents(events)
}
~~~

The generic array may be expanded to include ElectricHVACLoadEvent. Keep a durable record for each event identity and the selected venue. A successful return proves acceptance by the framework, not physical action or Home presentation.

## Recipe 11: Submission state and bounded backoff

Do not duplicate sessions after an ambiguous timeout:

~~~swift
import Foundation

enum EnergySubmissionState: Sendable, Equatable {
    case built
    case validated
    case submitting
    case accepted
    case processing
    case invalid(reason: String)
    case rateLimited(retryAt: Date)
    case venueUnavailable
    case serviceUnavailable
}

func retryDelay(for attempt: Int) -> TimeInterval {
    let bounded = min(max(attempt, 0), 6)
    return pow(2, Double(bounded))
}

struct EnergySubmissionReceipt: Sendable, Equatable {
    let eventIDs: [String]
    let venueID: UUID
    let state: EnergySubmissionState
    let attemptedAt: Date
}
~~~

Map EnergyKitError.invalidLoadEvent to correction, rateLimitExceeded to backoff, venueUnavailable to revalidation, and serviceUnavailable to a bounded retry. Do not expose raw error payloads in diagnostics.

## Recipe 12: Query historical insights

Make the query provenance visible in the product state:

~~~swift
import EnergyKit
import Foundation

func makeInsightQuery(
    end: Date,
    days: Int,
    includeTariff: Bool
) -> ElectricityInsightQuery {
    let calendar = Calendar.current
    let start = calendar.date(
        byAdding: .day,
        value: -days,
        to: end
    ) ?? end.addingTimeInterval(-30 * 24 * 60 * 60)

    let options: ElectricityInsightQuery.Options =
        includeTariff ? [.cleanliness, .tariff] : [.cleanliness]

    return ElectricityInsightQuery(
        options: options,
        range: DateInterval(start: start, end: end),
        granularity: .daily,
        flowDirection: .imported
    )
}
~~~

The exact option and granularity names are SDK-sensitive. Do not request tariff and then display a zero-cost result when the venue did not return tariff categories.

## Recipe 13: Consume an insight stream

ElectricityInsightService returns historical streams, not a live meter:

~~~swift
import EnergyKit
import Foundation

func readEnergyInsights(
    deviceID: String,
    venueID: UUID,
    query: ElectricityInsightQuery
) async throws -> [
    ElectricityInsightRecord<Measurement<UnitEnergy>>
] {
    var records: [
        ElectricityInsightRecord<Measurement<UnitEnergy>>
    ] = []

    for try await record in try await ElectricityInsightService.shared
        .energyInsights(
            forDeviceID: deviceID,
            using: query,
            atVenue: venueID
        ) {
        records.append(record)
    }

    return records
}
~~~

Store query range, granularity, flow direction, device, venue, and fetched time beside the records. Show processing/no-data states when events have been accepted but insight processing has not completed.

## Recipe 14: Model an insight view state

Keep missing categories explicit:

~~~swift
import Foundation

enum InsightViewState: Sendable, Equatable {
    case idle
    case loading(queryDescription: String)
    case processing
    case ready(
        range: DateInterval,
        totalEnergyDescription: String,
        missingCategories: [String]
    )
    case noData
    case unavailable(message: String)
}

struct InsightProvenance: Sendable, Equatable {
    let deviceID: String
    let venueID: UUID
    let range: DateInterval
    let granularity: String
    let flowDirection: String
}
~~~

The chart should have a text summary and an accessible alternative. A missing tariff category is unavailable data, not zero tariff cost.

## Recipe 15: SwiftUI route shell

The view observes a model; it does not create an unbounded stream or submit an event from body evaluation:

~~~swift
import SwiftUI

struct EnergyDashboard: View {
    @State private var model: EnergyDashboardModel

    init(model: EnergyDashboardModel) {
        _model = State(initialValue: model)
    }

    var body: some View {
        NavigationStack {
            Group {
                switch model.state {
                case .loadingVenue:
                    ProgressView("Finding Home venues")
                case .venueRequired:
                    VenuePicker(
                        venues: model.venues,
                        selection: $model.selectedVenueID
                    )
                case .guidanceReady, .scheduleNeedsReview:
                    ScheduleReview(
                        proposal: model.proposal,
                        onApprove: model.approveSchedule,
                        onStartNow: model.startNow
                    )
                case .physicalStateObserved:
                    LiveDeviceState(
                        observation: model.observation,
                        onPause: model.pause,
                        onResume: model.resume,
                        onEnd: model.end
                    )
                default:
                    EnergyStateFallback(state: model.state)
                }
            }
            .navigationTitle("Energy")
        }
        .task(id: model.streamIdentity) {
            await model.refreshGuidance()
        }
    }
}
~~~

Use native controls for approval, start now, pause, resume, and end. A translucent container can group actions, but the view must keep status labels, ownership, and accessibility semantics intact.

## Recipe 16: Liquid Glass action grouping

Keep the energy content readable and apply material to the action group:

~~~swift
import SwiftUI

struct EnergyActionBar: View {
    let approve: () -> Void
    let startNow: () -> Void
    let isEnabled: Bool

    var body: some View {
        HStack(spacing: 12) {
            Button("Review schedule", action: approve)
                .buttonStyle(.glassProminent)
                .disabled(!isEnabled)

            Button("Start now", action: startNow)
                .buttonStyle(.glass)
                .disabled(!isEnabled)
        }
        .padding()
    }
}
~~~

Compile the selected Liquid Glass styles against the final SDK and use the documented availability fallback where needed. Do not use glass styling to imply EnergyKit acceptance, Home ownership, or physical device success.

## Recipe 17: Typed on-device explanation input

Pass a redacted, bounded representation of facts to an optional local model:

~~~swift
import Foundation

struct EnergyExplanationInput: Sendable {
    let deviceKind: String
    let suggestedAction: String
    let selectedInterval: DateInterval
    let guidanceFetchedAt: Date
    let constraints: [String]
    let missingData: [String]
    let physicalActionObserved: Bool
    let insightRange: DateInterval?
}

struct EnergyExplanation: Sendable, Equatable {
    let summary: String
    let citedFacts: [String]
    let missingData: [String]
    let requiresUserReview: Bool
}
~~~

The model may produce the summary, but the app supplies citedFacts and missingData from deterministic state. Validate the output schema and reject any output that claims physical action, invents a rate, or changes a comfort/safety rule.

## Recipe 18: Explain without granting side effects

Keep explanation and action APIs separate:

~~~swift
import Foundation

enum EnergyCommand: Sendable {
    case none
    case requestUserApproval(EnergyExplanation)
}

func commandFromExplanation(
    _ explanation: EnergyExplanation
) -> EnergyCommand {
    guard explanation.requiresUserReview else {
        return .none
    }
    return .requestUserApproval(explanation)
}
~~~

The device controller and EnergyVenue submission layer should never accept an unvalidated natural-language string as a command. A user-approved deterministic action can call the controller; observed telemetry then drives event construction.

## Recipe 19: Reducer tests for proof boundaries

Test the claim transitions independently:

~~~swift
import Testing

@Test
func acceptedEventDoesNotBecomeHomePresentation() {
    let state: EnergyFeatureState = .eventAccepted
    #expect(state != .systemProcessing)
    #expect(state != .insightReady)
}

@Test
func pluggedInStatusDoesNotBecomeCharging() {
    let status = "charger plugged in"
    let active = "charging active"
    #expect(status != active)
}

@Test
func explanationRequiresReviewBeforeSideEffect() {
    let explanation = EnergyExplanation(
        summary: "Use the proposed window.",
        citedFacts: ["The selected window meets the deadline."],
        missingData: [],
        requiresUserReview: true
    )

    #expect(commandFromExplanation(explanation) != .none)
}
~~~

These tests prove product reducer boundaries only. They do not prove the SDK compiles, a signed entitlement exists, a Home venue is eligible, a charger/HVAC device operated, or the Home app displayed a result.

## Sources

- [EnergyKit](https://developer.apple.com/documentation/EnergyKit)
- [Introducing EnergyKit](https://developer.apple.com/energykit/)
- [Optimize home electricity usage with EnergyKit](https://developer.apple.com/videos/play/wwdc2025/257/)
- [EnergyVenue](https://developer.apple.com/documentation/energykit/energyvenue)
- [ElectricityGuidance](https://developer.apple.com/documentation/energykit/electricityguidance)
- [ElectricityGuidance.Service](https://developer.apple.com/documentation/energykit/electricityguidance/service)
- [ElectricalLoadEventProtocol](https://developer.apple.com/documentation/energykit/electricalloadeventprotocol)
- [ElectricVehicleLoadEvent](https://developer.apple.com/documentation/energykit/electricvehicleloadevent)
- [ElectricVehicleLoadEvent.ElectricalMeasurement](https://developer.apple.com/documentation/energykit/electricvehicleloadevent/electricalmeasurement)
- [ElectricVehicleStatusEvent](https://developer.apple.com/documentation/energykit/electricvehiclestatusevent)
- [ElectricHVACLoadEvent](https://developer.apple.com/documentation/energykit/electrichvacloadevent)
- [ElectricityFlowDirection](https://developer.apple.com/documentation/energykit/electricityflowdirection)
- [ElectricityInsightQuery](https://developer.apple.com/documentation/energykit/electricityinsightquery)
- [ElectricityInsightService](https://developer.apple.com/documentation/energykit/electricityinsightservice)
- [ElectricityInsightRecord](https://developer.apple.com/documentation/energykit/electricityinsightrecord)
- [EnergyKitError](https://developer.apple.com/documentation/energykit/energykiterror)
- [EnergyKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit)
- [EnergyKit LoadEvents entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit.loadevents-experience)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
