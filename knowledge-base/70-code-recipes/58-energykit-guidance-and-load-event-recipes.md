# EnergyKit Guidance and Load-Event Recipes

These are compile-oriented route sketches for EnergyKit venue discovery, guidance streams, deterministic schedule proposals, EV/HVAC load events, Home app state, insight streams, Liquid Glass UI, and bounded on-device AI explanations. They are not compiled in this documentation-only workspace and do not prove entitlements, region eligibility, Home venues, physical charger/HVAC behavior, Home app presentation, or historical insight quality.

Before copying:

1. Set an iOS 26 or iPadOS 26 deployment target and final SDK.
2. Add the base EnergyKit capability and inspect the signed entitlement.
3. Add the LoadEvents capability only for the Home app event route.
4. Confirm the contiguous-U.S. and beta/API availability conditions.
5. Keep physical device control and EnergyKit telemetry separate.
6. Verify every event initializer and unit in Xcode.

## Recipe 1: Route and build state

~~~swift
import Foundation

enum EnergyBuildState: Sendable {
    case unavailable(reason: String)
    case baseReady
    case loadEventsReady
}

enum EnergySuggestedAction: Sendable {
    case shift
    case reduce
}

struct EnergyRoutePlan: Sendable {
    let buildState: EnergyBuildState
    let suggestedAction: EnergySuggestedAction
    let requiresVenue: Bool
    let requiresPhysicalDeviceTelemetry: Bool
    let fallback: String
}
~~~

Use this state to hide or explain unavailable routes. Do not use a preview fixture to claim the signed entitlement exists.

## Recipe 2: Load Home energy venues

EnergyVenue represents a physical Home location available to EnergyKit:

~~~swift
import EnergyKit

func loadVenues() async throws -> [EnergyVenue] {
    try await EnergyVenue.venues()
}
~~~

Persist the selected venue identifier and a user-approved display mapping. If the array is empty, show a venue-needed state instead of assuming the person has no energy devices.

## Recipe 3: Select a venue explicitly

~~~swift
import EnergyKit
import Foundation

struct SelectedEnergyVenue: Sendable {
    let id: UUID
    let displayName: String
}

func reloadVenue(id: UUID) async throws -> EnergyVenue {
    try await EnergyVenue.venue(for: id)
}
~~~

The display name is not a substitute for the framework’s venue identity. Handle venueUnavailable, permissionDenied, locationServicesDenied, and unsupportedRegion with a manual product route.

## Recipe 4: Stream shift guidance

The venue route can include cost information when available:

~~~swift
import EnergyKit

func streamShiftGuidance(
    venueID: UUID,
    handle: @escaping @Sendable (ElectricityGuidance) -> Void
) async throws {
    let query = ElectricityGuidance.Query(suggestedAction: .shift)
    for try await guidance in ElectricityGuidance.sharedService.guidance(
        using: query,
        at: venueID
    ) {
        handle(guidance)
    }
}
~~~

Keep the returned guidance interval, venue ID, token, options, and fetched time with the schedule proposal. Cancel the task when the selected device or venue changes. A stream update does not itself change a charger.

## Recipe 5: Stream reduce guidance

~~~swift
import EnergyKit

func streamReduceGuidance(
    venueID: UUID,
    handle: @escaping @Sendable (ElectricityGuidance) -> Void
) async throws {
    let query = ElectricityGuidance.Query(suggestedAction: .reduce)
    for try await guidance in ElectricityGuidance.sharedService.guidance(
        using: query,
        at: venueID
    ) {
        handle(guidance)
    }
}
~~~

For a location-only route, confirm the current overload that accepts CLLocation and explain that cost information is not incorporated. Do not attach a tariff claim to a location-only result.

## Recipe 6: Build a deterministic schedule proposal

Keep the scheduler independent of SwiftUI and model output:

~~~swift
import Foundation

struct GuidanceWindow: Sendable {
    let interval: DateInterval
    let rating: Double
}

struct EnergyScheduleInput: Sendable {
    let now: Date
    let deadline: Date
    let windows: [GuidanceWindow]
    let requiredDuration: TimeInterval
    let devicePowerLimit: Measurement<UnitPower>
}

struct EnergyScheduleProposal: Sendable {
    let window: DateInterval
    let rating: Double
    let requiresApproval: Bool
    let reason: String
}

enum EnergyScheduleError: Error {
    case noFeasibleWindow
    case invalidGuidance
}

func makeProposal(
    from input: EnergyScheduleInput
) throws -> EnergyScheduleProposal {
    let candidates = input.windows
        .filter { $0.interval.start >= input.now }
        .filter { $0.interval.end <= input.deadline }
        .filter { $0.interval.duration >= input.requiredDuration }
        .sorted { $0.rating < $1.rating }

    guard let selected = candidates.first else {
        throw EnergyScheduleError.noFeasibleWindow
    }

    return EnergyScheduleProposal(
        window: selected.interval,
        rating: selected.rating,
        requiresApproval: true,
        reason: "Selected from feasible windows in the latest guidance."
    )
}
~~~

The rating direction and cost/cleanliness legend must be documented in the actual UI. This function does not guarantee savings or emissions reduction.

## Recipe 7: EV event state

Keep session order explicit:

~~~swift
import Foundation

enum EVSessionState: Sendable {
    case begin
    case active
    case end
}

struct EVTelemetry: Sendable {
    let timestamp: Date
    let stateOfCharge: Int
    let powerMilliwatts: Int64
    let cumulativeEnergyMilliwattHours: Int64
    let isExporting: Bool
}

struct EVSession: Sendable {
    let id: UUID
    let state: EVSessionState
    let guidanceToken: UUID
}
~~~

Before constructing the framework event, validate state-of-charge range, cumulative energy, direction, begin/active/end order, and device/venue/guidance identity. Never synthesize telemetry to fill a missing reading.

## Recipe 8: Construct an EV load event

The current EnergyKit documentation uses a measurement, session, and ElectricalLoadDevice. Verify exact unit and initializer availability in the final SDK:

~~~swift
import EnergyKit
import Foundation

func makeEVEvent(
    telemetry: EVTelemetry,
    session: ElectricVehicleLoadEvent.Session,
    device: ElectricalLoadDevice
) -> ElectricVehicleLoadEvent {
    let direction: ElectricityFlowDirection =
        telemetry.isExporting ? .exported : .imported

    let measurement = ElectricVehicleLoadEvent.ElectricalMeasurement(
        stateOfCharge: telemetry.stateOfCharge,
        direction: direction,
        power: Measurement(
            value: Double(telemetry.powerMilliwatts),
            unit: .milliwatts
        ),
        energy: Measurement(
            value: Double(telemetry.cumulativeEnergyMilliwattHours),
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

The unit spellings and session constructors are SDK-sensitive. Confirm them in Xcode. For V2G/V2H, use separate session IDs/states for import and export.

## Recipe 9: Submit EV/HVAC events

EnergyVenue accepts load events through the generic event protocol:

~~~swift
import EnergyKit

func submit(
    loadEvents: [ElectricVehicleLoadEvent],
    statusEvents: [ElectricVehicleStatusEvent],
    to venue: EnergyVenue
) async throws {
    let allEvents: [any ElectricalLoadEventProtocol] =
        loadEvents + statusEvents
    try await venue.submitEvents(allEvents)
}
~~~

Submit promptly after meaningful events. Handle invalidLoadEvent and rateLimitExceeded separately. A successful method return proves EnergyKit accepted the submission, not that the Home app already displays it.

## Recipe 10: HVAC transition events

Use the current ElectricHVACLoadEvent initializer with a typed measurement and session:

~~~swift
import EnergyKit
import Foundation

func makeHVACEvent(
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

Create events for meaningful heating/cooling stage or active/idle transitions. Do not submit an event for every thermostat sample.

## Recipe 11: Event submission state and backoff

~~~swift
import Foundation

enum EventSubmissionState: Equatable, Sendable {
    case ready
    case submitting
    case accepted
    case invalid
    case rateLimited(retryAt: Date)
    case unavailable
}

func retryDelay(attempt: Int) -> TimeInterval {
    let boundedAttempt = min(max(attempt, 0), 6)
    return pow(2, Double(boundedAttempt))
}
~~~

Persist a stable event/session identity for retry decisions. Do not blindly duplicate a begin or end event after a timeout; reload the local submission state and choose a documented reconciliation path.

## Recipe 12: Historical insight query

Use an explicit range and granularity:

~~~swift
import EnergyKit
import Foundation

func insightQuery(for date: Date) -> ElectricityInsightQuery {
    let calendar = Calendar.current
    let start = calendar.date(byAdding: .day, value: -30, to: date)!
    return ElectricityInsightQuery(
        options: [.cleanliness, .tariff],
        range: DateInterval(start: start, end: date),
        granularity: .daily,
        flowDirection: .imported
    )
}
~~~

The current option names and granularity cases must be checked in the final SDK. Do not request tariff data and then display a zero when the venue has no rate-plan information.

## Recipe 13: Consume insight records

~~~swift
import EnergyKit

func loadInsights(
    deviceID: String,
    venueID: UUID,
    query: ElectricityInsightQuery
) async throws -> [ElectricityInsightRecord<Measurement<UnitEnergy>>] {
    var records: [ElectricityInsightRecord<Measurement<UnitEnergy>>] = []
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

The stream is historical processing, not a real-time meter. Store query provenance and present a no-data/processing state.

## Recipe 14: Typed AI explanation

~~~swift
import Foundation

struct EnergyExplanationInput: Sendable {
    let venueName: String
    let deviceName: String
    let action: String
    let selectedWindow: DateInterval
    let guidanceUpdatedAt: Date
    let rateDataAvailable: Bool
    let missingInputs: [String]
    let physicalActionObserved: Bool
}

struct EnergyExplanation: Sendable {
    let summary: String
    let assumptions: [String]
    let missingData: [String]
    let nextAction: String
    let requiresApproval: Bool
}
~~~

Give the model redacted, typed values. Keep savings, carbon, comfort, and physical-action claims in deterministic product code. If the model is unavailable, render a fixed explanation from the same input.

## Recipe 15: SwiftUI schedule surface

~~~swift
import SwiftUI

struct EnergyScheduleView: View {
    let venueName: String
    let proposal: EnergyScheduleProposal
    let onApprove: () -> Void
    let onStartNow: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(venueName)
                .font(.headline)

            Text("Proposed window")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            Text(proposal.window.formatted())
                .font(.title3)
                .accessibilityLabel("Proposed energy use window")

            Text(proposal.reason)
                .font(.footnote)
                .foregroundStyle(.secondary)

            Button("Use Proposed Window", action: onApprove)
                .buttonStyle(.glassProminent)

            Button("Start Now", action: onStartNow)
                .buttonStyle(.bordered)
        }
        .padding()
        .glassEffect()
    }
}
~~~

Confirm Liquid Glass modifier names and availability in the selected SDK. The visual surface does not prove guidance freshness or physical action.

## Recipe 16: Fixtures and proof labels

~~~swift
enum EnergyFixtureState: String {
    case venueNeeded
    case guidanceReady
    case scheduleDraft
    case physicalActionPending
    case eventAccepted
    case insightReady
    case unsupportedRegion
}
~~~

Use fixtures to prove copy, layout, accessibility, and action routing. Use a final signed target, eligible Home venue, real guidance, real device telemetry, event acceptance, and Home/insight evidence for system claims.

## Compile and proof gates

- Verify base and LoadEvents entitlements in the signed artifact.
- Compile at the final iOS 26/iPadOS 26 SDK.
- Test region, Home venue, permission, and service errors.
- Test shift and reduce guidance streams with cancellation.
- Test schedule feasibility and start-now override.
- Test EV begin/active/end and HVAC transition event validation.
- Test rate limits, invalid events, retry, and deduplication.
- Test Home app processing separately from app submission.
- Test historical insight query range, granularity, freshness, and no-data.
- Test VoiceOver, Dynamic Type, Reduce Motion, Reduce Transparency, RTL, and localized units.
- Audit AI input for raw telemetry and verify no autonomous device command.

## Sources

- [EnergyKit](https://developer.apple.com/documentation/EnergyKit)
- [Introducing EnergyKit](https://developer.apple.com/energykit/)
- [Optimizing home electricity usage](https://developer.apple.com/documentation/EnergyKit/optimizing-home-electricity-usage)
- [Providing charging history for electric vehicles](https://developer.apple.com/documentation/EnergyKit/providing-informative-charging-history-for-electric-vehicles)
- [EnergyVenue](https://developer.apple.com/documentation/energykit/energyvenue)
- [ElectricityGuidance](https://developer.apple.com/documentation/energykit/electricityguidance)
- [ElectricityGuidance.Service](https://developer.apple.com/documentation/energykit/electricityguidance/service)
- [ElectricVehicleLoadEvent](https://developer.apple.com/documentation/energykit/electricvehicleloadevent)
- [ElectricVehicleLoadEvent electrical measurement](https://developer.apple.com/documentation/energykit/electricvehicleloadevent/electricalmeasurement)
- [ElectricHVACLoadEvent](https://developer.apple.com/documentation/energykit/electrichvacloadevent)
- [ElectricalLoadEventProtocol](https://developer.apple.com/documentation/energykit/electricalloadeventprotocol)
- [ElectricityInsightService](https://developer.apple.com/documentation/energykit/electricityinsightservice)
- [EnergyKitError](https://developer.apple.com/documentation/energykit/energykiterror)
- [EnergyKit Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit)
- [EnergyKit LoadEvents Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit.loadevents-experience)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
