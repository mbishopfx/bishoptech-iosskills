# SwiftUI HealthKit and personal-data review recipes

These are compile-oriented route sketches for a named iOS 26 target. They are not compiled in this documentation workspace and do not prove HealthKit authorization, physical sensors, background delivery, clinical-record completeness, medical interpretation, privacy compliance, accessibility task completion, or release readiness. Confirm the exact SDK signatures and target configuration in Xcode.

## Recipe rules

1. Request the minimum read/share/clinical types for the current feature.
2. Treat the authorization request’s success value separately from read access.
3. Keep query/session ownership outside SwiftUI body recomputation.
4. Preserve type, unit, date, source, and freshness.
5. An empty query is not proof of denied access or absent health data.
6. Background delivery requires signed-device proof and energy policy.
7. Native Activity rings are not medical claims or decorative clones.
8. On-device AI summarizes supplied records; it does not diagnose or write silently.

## Recipe 1: Define a minimum HealthKit request

Keep the read and write sets explicit:

~~~swift
import HealthKit

struct HealthRequest: Sendable {
    let readTypes: Set<HKObjectType>
    let shareTypes: Set<HKSampleType>
    let purpose: String
}

func dashboardRequest() throws -> HealthRequest {
    guard let stepCount = HKObjectType.quantityType(forIdentifier: .stepCount),
          let energy = HKObjectType.quantityType(forIdentifier: .activeEnergyBurned)
    else {
        throw HealthRouteError.unsupportedType
    }

    return HealthRequest(
        readTypes: [stepCount, energy],
        shareTypes: [],
        purpose: "Show activity totals for the selected dates."
    )
}
~~~

Add a write type only when the current screen explicitly logs data. Add clinical types only when the product genuinely presents or uses clinical records. Avoid requesting a full catalog “for future AI.”

## Recipe 2: Authorization owner

Own one HKHealthStore at the feature/service boundary:

~~~swift
@MainActor
final class HealthAuthorizationModel: ObservableObject {
    enum State: Equatable {
        case idle
        case unavailable
        case requesting
        case completed
        case failed(String)
    }

    @Published private(set) var state: State = .idle
    private let store = HKHealthStore()

    func request(_ request: HealthRequest) {
        guard HKHealthStore.isHealthDataAvailable() else {
            state = .unavailable
            return
        }

        state = .requesting
        Task { @MainActor in
            do {
                try await store.requestAuthorization(
                    toShare: request.shareTypes,
                    read: request.readTypes
                )
                state = .completed
            } catch {
                state = .failed(error.localizedDescription)
            }
        }
    }
}
~~~

After the request, run the feature’s query and report the result HealthKit supplies. Do not set readAuthorized to true from the completion Boolean. The system intentionally limits information about denied read access.

## Recipe 3: Query a quantity sample snapshot

A one-shot sample query can feed a deterministic display projection:

~~~swift
func readStepSamples(
    store: HKHealthStore,
    from start: Date,
    to end: Date,
    completion: @escaping @Sendable (Result<[HKQuantitySample], Error>) -> Void
) {
    guard let type = HKObjectType.quantityType(forIdentifier: .stepCount) else {
        completion(.failure(HealthRouteError.unsupportedType))
        return
    }

    let predicate = HKQuery.predicateForSamples(
        withStart: start,
        end: end,
        options: .strictStartDate
    )
    let sort = NSSortDescriptor(
        key: HKSampleSortIdentifierStartDate,
        ascending: true
    )
    let query = HKSampleQuery(
        sampleType: type,
        predicate: predicate,
        limit: HKObjectQueryNoLimit,
        sortDescriptors: [sort]
    ) { _, samples, error in
        if let error {
            completion(.failure(error))
            return
        }
        completion(.success((samples as? [HKQuantitySample]) ?? []))
    }

    store.execute(query)
}
~~~

The callback runs off the main queue. Hop to the main actor before changing SwiftUI state and preserve the query revision/date range used to produce the result.

## Recipe 4: Normalize a quantity with a unit

Use the type-specific unit policy:

~~~swift
struct QuantityDisplay: Identifiable, Sendable {
    let id: UUID
    let typeIdentifier: String
    let value: Double
    let unit: String
    let startDate: Date
    let endDate: Date
    let sourceName: String?
    let fetchedAt: Date
}

func display(
    sample: HKQuantitySample,
    unit: HKUnit
) -> QuantityDisplay {
    QuantityDisplay(
        id: sample.uuid,
        typeIdentifier: sample.quantityType.identifier,
        value: sample.quantity.doubleValue(for: unit),
        unit: unit.unitString,
        startDate: sample.startDate,
        endDate: sample.endDate,
        sourceName: sample.sourceRevision.source.name,
        fetchedAt: .now
    )
}
~~~

Do not use the formatted chart label as the source for later calculations. Preserve the HealthKit sample or a privacy-reviewed typed record.

## Recipe 5: Use statistics for a total or average

Statistics queries are preferable when the UI needs an aggregate rather than every sample:

~~~swift
func readDailyStepTotal(
    store: HKHealthStore,
    predicate: NSPredicate?,
    completion: @escaping @Sendable (Result<Double?, Error>) -> Void
) {
    guard let type = HKObjectType.quantityType(forIdentifier: .stepCount) else {
        completion(.failure(HealthRouteError.unsupportedType))
        return
    }

    let query = HKStatisticsQuery(
        quantityType: type,
        quantitySamplePredicate: predicate,
        options: .cumulativeSum
    ) { _, statistics, error in
        if let error {
            completion(.failure(error))
            return
        }

        let unit = HKUnit.count()
        completion(.success(
            statistics?.sumQuantity()?.doubleValue(for: unit)
        ))
    }
    store.execute(query)
}
~~~

Use only options that match the data type’s aggregation semantics. A nil result means no aggregate returned; do not display it as zero without a product decision.

## Recipe 6: Incremental changes with an anchor

Use an anchored query for new/deleted samples:

~~~swift
final class HealthAnchorStore {
    private var anchor: HKQueryAnchor?

    func makeQuery(
        type: HKSampleType,
        store: HKHealthStore,
        apply: @escaping @Sendable ([HKSample], [HKDeletedObject]) -> Void
    ) -> HKAnchoredObjectQuery {
        let query = HKAnchoredObjectQuery(
            type: type,
            predicate: nil,
            anchor: anchor,
            limit: HKObjectQueryNoLimit
        ) { [weak self] _, samples, deleted, nextAnchor, error in
            guard error == nil else { return }
            self?.anchor = nextAnchor
            apply(samples ?? [], deleted ?? [])
        }
        return query
    }
}
~~~

Persist the anchor only after the app has applied the returned changes safely. If the data model or query predicate changes, reset the anchor and rebuild the projection. Deleted objects matter; ignoring them produces stale charts and summaries.

## Recipe 7: Observe changes and follow up

An observer is a notification, not the data payload:

~~~swift
func startObserver(
    store: HKHealthStore,
    sampleType: HKSampleType,
    refresh: @escaping @Sendable () -> Void
) -> HKObserverQuery {
    HKObserverQuery(
        sampleType: sampleType,
        predicate: nil
    ) { _, completion, error in
        guard error == nil else {
            completion()
            return
        }

        refresh()
        completion()
    }
}
~~~

Use the query’s completion handler after the follow-up work for background delivery. Install the observer early enough for the system to deliver updates, and stop it when the feature no longer needs it. The exact async/concurrency bridge should be implemented in the named target.

## Recipe 8: Activity summary query and text projection

Build a date predicate for activity summaries and preserve missing data:

~~~swift
func activitySummaryQuery(
    calendar: Calendar,
    start: Date,
    end: Date,
    handle: @escaping @Sendable ([HKActivitySummary]) -> Void
) -> HKActivitySummaryQuery {
    let startComponents = calendar.dateComponents(
        [.calendar, .era, .year, .month, .day],
        from: start
    )
    let endComponents = calendar.dateComponents(
        [.calendar, .era, .year, .month, .day],
        from: end
    )
    let predicate = HKQuery.predicate(
        forActivitySummariesBetweenStart: startComponents,
        end: endComponents
    )

    return HKActivitySummaryQuery(predicate: predicate) { _, summaries, _ in
        handle(summaries ?? [])
    }
}
~~~

The exact predicate labels must be checked in the selected SDK. Render a text summary next to HKActivityRingView so VoiceOver and non-ring layouts expose date, values, goals, missing data, and source context.

## Recipe 9: Embed the native activity ring

Use a UIKit bridge only for the intended HealthKitUI native surface:

~~~swift
import SwiftUI
import HealthKitUI

struct ActivityRingRepresentable: UIViewRepresentable {
    let summary: HKActivitySummary?

    func makeUIView(context: Context) -> HKActivityRingView {
        HKActivityRingView()
    }

    func updateUIView(_ view: HKActivityRingView, context: Context) {
        view.activitySummary = summary
    }
}
~~~

Confirm property names and availability in the selected SDK. The ring is a native activity summary element, not a permission indicator, health score, or diagnosis. Separate it from any app-specific circular visualization.

## Recipe 10: Clinical record route sketch

Keep FHIR record identity separate from friendly text:

~~~swift
struct ClinicalRecordProjection: Identifiable, Sendable {
    let id: UUID
    let recordType: String
    let sourceName: String?
    let effectiveDate: Date?
    let authoredDate: Date?
    let code: String?
    let displayText: String
    let parserRevision: String
}

func requestClinicalTypes() -> Set<HKObjectType> {
    var types = Set<HKObjectType>()
    if let allergy = HKObjectType.clinicalType(forIdentifier: .allergyRecord) {
        types.insert(allergy)
    }
    if let medication = HKObjectType.clinicalType(forIdentifier: .medicationRecord) {
        types.insert(medication)
    }
    return types
}
~~~

Clinical record types are read-only in the documented route. Enable the clinical capability and usage description only when the target actually uses the records. Parse supported FHIR resources conservatively and retain an “unknown/unsupported” state instead of dropping a record into an unqualified summary.

## Recipe 11: HealthKit authorization-aware SwiftUI shell

Keep permission, availability, data, and AI state visible:

~~~swift
struct HealthDashboard: View {
    @StateObject private var model = HealthDashboardModel()

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                PermissionPurposeView(state: model.authorization)
                AvailabilityView(state: model.availability)
                HealthChartView(snapshot: model.snapshot)
                ActivitySummaryView(summary: model.activitySummary)
                HealthAIProposalView(proposal: model.proposal)
                PrivacyAndSourceView(snapshot: model.snapshot)
            }
            .padding()
        }
        .task { await model.refreshIfAuthorized() }
    }
}
~~~

Do not start a query from every chart cell or rely on a view appearing as the only owner of a long-running observer. Give the feature model an explicit start/stop lifecycle.

## Recipe 12: Typed local AI proposal

Pass selected records, not an unrestricted HealthKit store:

~~~swift
struct HealthPromptContext: Codable, Sendable {
    let revision: Int
    let rangeStart: Date
    let rangeEnd: Date
    let records: [Record]

    struct Record: Codable, Sendable {
        let id: String
        let type: String
        let value: Double
        let unit: String
        let date: Date
        let source: String?
    }
}

struct HealthProposal: Codable, Sendable {
    let revision: Int
    let factualSummary: String
    let missingData: [String]
    let clinicianQuestion: String?
}

func acceptProposal(
    _ proposal: HealthProposal,
    context: HealthPromptContext
) -> Bool {
    proposal.revision == context.revision
}
~~~

Before rendering, validate revision/range and run a claim policy that rejects diagnosis, treatment, emergency, guarantee, and unsupported causal language. The app’s deterministic values and units remain the visible facts. Saving a note is an explicit user action; writing to HealthKit is a separate typed route.

## Recipe 13: Explicit save/share route

Make sensitive side effects visible:

~~~swift
enum HealthDestination: Sendable {
    case healthKitSample
    case appNote
    case shareSheet
    case fileExport
}

struct HealthCommitReview: Sendable {
    let destination: HealthDestination
    let type: String
    let dateRange: ClosedRange<Date>
    let sourceSummary: String
    let userConfirmed: Bool
}

func validateCommit(_ review: HealthCommitReview) throws {
    guard review.userConfirmed else { throw HealthRouteError.needsConfirmation }
    guard !review.type.isEmpty else { throw HealthRouteError.invalidType }
}
~~~

Show the data range, source, destination, and exact text/value before sharing or saving. Do not automatically contact another person from health data or a model proposal.

## Recipe 14: Glass and accessibility fallback

Use a bounded shell with an opaque fallback:

~~~swift
struct HealthReviewGroup<Content: View>: View {
    @ViewBuilder let content: () -> Content

    var body: some View {
        content()
            .padding()
            .background {
                RoundedRectangle(cornerRadius: 24)
                    .fill(.regularMaterial)
            }
            .glassEffect(in: .rect(cornerRadius: 24))
    }
}
~~~

Confirm the exact modifier and availability for the target. The visual effect must not be the only contrast boundary, and sensitive values should remain understandable under reduced transparency, increased contrast, Dynamic Type, VoiceOver, reduced motion, pointer, keyboard, and touch.

## Recipe 15: Fixture matrix

Create state fixtures rather than relying on a live store in previews:

~~~swift
enum HealthFixture {
    static let unavailable = HealthAvailability.unavailable
    static let noData = HealthSnapshot.empty(
        range: .lastWeek,
        explanation: "No data is available for this range."
    )
    static let stale = HealthSnapshot.stale(
        lastUpdated: Date(timeIntervalSinceNow: -86_400)
    )
    static let aiUnavailable = AIState.unavailable
    static let aiInsufficient = AIState.proposal(
        text: "Insufficient data for a useful summary.",
        sourceRevision: 4
    )
}
~~~

Add fixtures for missing versus zero rings, partial ranges, deleted samples, query failure, clinical parser error, live workout paused/interrupted, denied/changed access, reduced transparency, RTL, and large Dynamic Type. Fixtures prove projection behavior, not HealthKit access.

## Recipe 16: Named-target acceptance record

~~~text
target/scheme: ___________________________
bundle ID: _______________________________
SDK/deployment target: ____________________
physical device/OS: _______________________
HealthKit capability: _____________________
clinical/background capability: ____________
Info.plist usage strings: _________________
privacy policy URL: _______________________
read/share/clinical types: ________________
query/predicate/unit policy: ______________
source/revision/freshness policy: _________

[ ] availability and no-data routes pass
[ ] authorization and settings-change routes pass
[ ] sample/statistics/anchored/observer routes pass
[ ] activity summary/ring missing-zero routes pass
[ ] workout/device/lock/background routes pass
[ ] clinical/FHIR route passes if used
[ ] AI proposal is source-linked and non-diagnostic
[ ] no silent HealthKit write/export/share
[ ] VoiceOver/Dynamic Type/contrast/motion/RTL/input pass
[ ] privacy/data-flow/retention/deletion pass
[ ] signed archive/entitlement/privacy inspection pass
~~~

## Sources

- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Setting up HealthKit](https://developer.apple.com/documentation/healthkit/setting-up-healthkit)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [HKHealthStore](https://developer.apple.com/documentation/healthkit/hkhealthstore)
- [HKAuthorizationStatus](https://developer.apple.com/documentation/healthkit/hkauthorizationstatus)
- [HKSampleQuery](https://developer.apple.com/documentation/healthkit/hksamplequery)
- [HKAnchoredObjectQuery](https://developer.apple.com/documentation/healthkit/hkanchoredobjectquery)
- [HKStatisticsQuery](https://developer.apple.com/documentation/healthkit/hkstatisticsquery)
- [HKStatisticsCollectionQuery](https://developer.apple.com/documentation/healthkit/hkstatisticscollectionquery)
- [HKObserverQuery](https://developer.apple.com/documentation/healthkit/hkobserverquery)
- [Executing Observer Queries](https://developer.apple.com/documentation/healthkit/executing-observer-queries)
- [HKActivitySummary](https://developer.apple.com/documentation/healthkit/hkactivitysummary)
- [HKActivitySummaryQuery](https://developer.apple.com/documentation/healthkit/hkactivitysummaryquery)
- [HKActivityRingView](https://developer.apple.com/documentation/healthkitui/hkactivityringview)
- [Workouts and activity rings](https://developer.apple.com/documentation/healthkit/workouts-and-activity-rings)
- [HKWorkout](https://developer.apple.com/documentation/healthkit/hkworkout)
- [HKWorkoutSession](https://developer.apple.com/documentation/healthkit/hkworkoutsession)
- [HKLiveWorkoutBuilder](https://developer.apple.com/documentation/healthkit/hkliveworkoutbuilder)
- [Accessing Health Records](https://developer.apple.com/documentation/healthkit/accessing-health-records)
- [HKClinicalRecord](https://developer.apple.com/documentation/healthkit/hkclinicalrecord)
- [HKFHIRResource](https://developer.apple.com/documentation/healthkit/hkfhirresource)
- [HealthKit human interface guidelines](https://developer.apple.com/design/human-interface-guidelines/healthkit)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
