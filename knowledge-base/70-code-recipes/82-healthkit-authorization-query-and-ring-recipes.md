# HealthKit authorization, query, clinical, and activity-ring recipes

These are compile-oriented route sketches for a named iOS or watchOS target. Confirm the exact SDK availability, target capability, Info.plist keys, and physical-device behavior before treating a recipe as production code. The snippets intentionally keep authorization, query results, provenance, UI, and local AI separate.

## 1. Request a narrow read set

Use the async HealthKit authorization method when the deployment target supports it. A successful call means the system request completed without throwing; it does not mean every requested type is readable.

~~~swift
import HealthKit

@MainActor
final class HealthKitAccessCoordinator {
    enum AccessError: Error {
        case unavailable
        case unsupportedType
    }

    private let store: HKHealthStore

    init(store: HKHealthStore = HKHealthStore()) {
        self.store = store
    }

    func requestStepCountReadAccess() async throws {
        guard HKHealthStore.isHealthDataAvailable() else {
            throw AccessError.unavailable
        }

        guard let stepCount = HKObjectType.quantityType(forIdentifier: .stepCount) else {
            throw AccessError.unsupportedType
        }

        let readTypes: Set<HKObjectType> = [stepCount]
        let shareTypes: Set<HKSampleType> = []

        try await store.requestAuthorization(
            toShare: shareTypes,
            read: readTypes
        )
    }
}
~~~

For a write feature, add only the concrete HKSampleType that the app may save. Keep read and write copy distinct. Do not use the completion handler’s success result or the async method’s lack of an error as proof that a read query will contain data.

## 2. Make access-state rendering pure

HealthKit intentionally does not reveal a simple per-type “read denied” result. Keep the UI state based on device availability, request lifecycle, query outcome, and the recovery path instead of claiming a hidden permission state.

~~~swift
enum HealthDataSurfaceState: Equatable {
    case unavailable
    case notRequested
    case checking
    case emptyOrLimited
    case available(sampleCount: Int)
    case stale(lastRefresh: Date)
    case failed
}

struct HealthDataSnapshot: Equatable {
    var state: HealthDataSurfaceState
    var queriedType: String
    var from: Date
    var to: Date
    var sourceCount: Int
}

func title(for snapshot: HealthDataSnapshot) -> String {
    switch snapshot.state {
    case .unavailable:
        return "Health data is unavailable"
    case .notRequested:
        return "Choose what to share"
    case .checking:
        return "Checking selected data"
    case .emptyOrLimited:
        return "No data available for this request"
    case .available(let count):
        return "\(count) samples available"
    case .stale:
        return "Showing older data"
    case .failed:
        return "Couldn’t refresh health data"
    }
}
~~~

Use the queried type and date window in the supporting text. Do not turn an empty result into zero, denial, or a medical conclusion.

## 3. Build a bounded daily statistics query

Statistics collection queries are appropriate for quantity samples and fixed intervals such as daily step totals. They are not a generic route for workouts or correlation samples.

~~~swift
import HealthKit

struct DailyQuantityTotal: Sendable {
    let start: Date
    let end: Date
    let value: Double?
}

func loadDailyStepTotals(
    store: HKHealthStore,
    from: Date,
    to: Date,
    calendar: Calendar,
    completion: @escaping ([DailyQuantityTotal], Error?) -> Void
) {
    guard let stepType = HKObjectType.quantityType(forIdentifier: .stepCount) else {
        completion([], nil)
        return
    }

    let predicate = HKQuery.predicateForSamples(
        withStart: from,
        end: to,
        options: .strictStartDate
    )
    let anchor = calendar.startOfDay(for: from)
    var interval = DateComponents()
    interval.day = 1

    let query = HKStatisticsCollectionQuery(
        quantityType: stepType,
        quantitySamplePredicate: predicate,
        options: .cumulativeSum,
        anchorDate: anchor,
        intervalComponents: interval
    )

    query.initialResultsHandler = { _, collection, error in
        guard let collection else {
            completion([], error)
            return
        }

        var totals: [DailyQuantityTotal] = []
        collection.enumerateStatistics(from: from, to: to) { statistics, _ in
            let total = statistics.sumQuantity()?.doubleValue(for: .count())
            totals.append(
                DailyQuantityTotal(
                    start: statistics.startDate,
                    end: statistics.endDate,
                    value: total
                )
            )
        }
        completion(totals, nil)
    }

    store.execute(query)
}
~~~

The production adapter should also record the requested type, date range, source policy, time zone, query error, and refresh time. A nil total is an empty/limited interval, not a zero step count.

## 4. Observe changes and finish the background delivery

An observer query signals that matching data may have changed. Run a bounded follow-up query and always call the completion handler. Background delivery needs a physical-device test; it is not proven by a simulator callback.

~~~swift
import HealthKit

final class HealthStoreObserver {
    private let store: HKHealthStore

    init(store: HKHealthStore) {
        self.store = store
    }

    func start(for sampleType: HKSampleType) {
        let observer = HKObserverQuery(
            sampleType: sampleType,
            predicate: nil
        ) { [weak self] _, completion, error in
            defer { completion() }

            guard let self, error == nil else {
                // Record a redacted refresh failure. Do not log health payloads.
                return
            }

            // Run a bounded sample/statistics/anchored query here.
            self.refreshBoundedWindow(for: sampleType)
        }

        store.execute(observer)
        store.enableBackgroundDelivery(
            for: sampleType,
            frequency: .hourly
        ) { success, error in
            // Persist only success/error category and the target type.
            _ = (success, error)
        }
    }

    private func refreshBoundedWindow(for sampleType: HKSampleType) {
        // Resolve the app-owned date window and query policy here.
        _ = sampleType
    }
}
~~~

Do not assume hourly means exactly hourly, that the app will run indefinitely, or that the observer callback contains a new sample. Respect the background budget and make the cached state timestamp visible.

## 5. Incrementally cache changes with an anchor

Use an anchored object query when the app owns a local cache and needs additions/deletions since its last checkpoint. Persist the anchor only after the result has been reconciled.

~~~swift
import HealthKit

struct HealthAnchorBatch {
    let added: [HKSample]
    let deleted: [HKDeletedObject]
    let anchor: HKQueryAnchor?
}

func makeAnchoredQuery(
    sampleType: HKSampleType,
    anchor: HKQueryAnchor?,
    receive: @escaping (HealthAnchorBatch) -> Void
) -> HKAnchoredObjectQuery {
    let query = HKAnchoredObjectQuery(
        type: sampleType,
        predicate: nil,
        anchor: anchor,
        limit: HKObjectQueryNoLimit
    ) { _, samples, deleted, nextAnchor, error in
        guard error == nil else {
            receive(HealthAnchorBatch(added: [], deleted: [], anchor: anchor))
            return
        }

        receive(
            HealthAnchorBatch(
                added: samples ?? [],
                deleted: deleted ?? [],
                anchor: nextAnchor
            )
        )
    }
    return query
}
~~~

Use an app-owned representation for source, unit, dates, and deletion state. Do not present a local cache as the entire HealthKit history unless the cache policy proves that claim.

## 6. Wrap HKActivityRingView in SwiftUI

HealthKitUI provides HKActivityRingView as a UIView. Supply a real or fixture HKActivitySummary and put explanatory/accessibility content around it.

~~~swift
import HealthKit
import HealthKitUI
import SwiftUI

struct ActivityRingsView: UIViewRepresentable {
    let summary: HKActivitySummary?
    var animated: Bool = true

    func makeUIView(context: Context) -> HKActivityRingView {
        HKActivityRingView()
    }

    func updateUIView(_ view: HKActivityRingView, context: Context) {
        view.setActivitySummary(summary, animated: animated)
    }
}

struct ActivitySummarySurface: View {
    let summary: HKActivitySummary?
    let dayDescription: String

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ActivityRingsView(summary: summary)
                .frame(width: 220, height: 220)
                .accessibilityLabel("Activity rings for \(dayDescription)")

            Text(dayDescription)
                .font(.headline)
            Text("Empty rings mean a value is unavailable. A dot can represent a zero value.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
    }
}
~~~

Use a nil quantity to represent no summary and a zero quantity to represent zero, as appropriate for the fixture. The ring view does not supply a permission explanation or a clinical interpretation.

## 7. Request clinical record types as read-only

Clinical types belong in the read set. The app should not attempt to save clinical records or treat them as app-authored samples.

~~~swift
import HealthKit

func clinicalReadTypes() -> Set<HKObjectType> {
    let identifiers: [HKClinicalTypeIdentifier] = [
        .medicationRecord,
        .labResultRecord,
        .vitalSignRecord
    ]

    return Set(
        identifiers.compactMap {
            HKObjectType.clinicalType(forIdentifier: $0)
        }
    )
}

@MainActor
func requestClinicalReadAccess(store: HKHealthStore) async throws {
    let readTypes = clinicalReadTypes()
    let shareTypes: Set<HKSampleType> = []
    try await store.requestAuthorization(
        toShare: shareTypes,
        read: readTypes
    )
}
~~~

Add NSHealthClinicalHealthRecordsShareUsageDescription, the nested capability, and the privacy-policy/App Store route in the named target. Request only the clinical types used by the feature.

## 8. Query and redact a clinical record

Clinical records require provenance-aware handling. Keep the underlying FHIR payload out of logs and ordinary analytics.

~~~swift
import HealthKit

struct ClinicalRecordSummary: Sendable {
    let displayName: String
    let clinicalType: String
    let fhirResourceType: String?
    let sourceURL: URL?
    let downloadedAt: Date
}

func makeClinicalQuery(
    type: HKSampleType,
    receive: @escaping ([ClinicalRecordSummary], Error?) -> Void
) -> HKSampleQuery {
    HKSampleQuery(
        sampleType: type,
        predicate: nil,
        limit: HKObjectQueryNoLimit,
        sortDescriptors: nil
    ) { _, samples, error in
        let summaries = (samples ?? []).compactMap { sample -> ClinicalRecordSummary? in
            guard let record = sample as? HKClinicalRecord else {
                return nil
            }

            let resource = record.fhirResource
            return ClinicalRecordSummary(
                displayName: record.displayName,
                clinicalType: record.clinicalType.identifier,
                fhirResourceType: resource?.resourceType.rawValue,
                sourceURL: resource?.sourceURL,
                downloadedAt: record.startDate
            )
        }
        receive(summaries, error)
    }
}
~~~

The exact FHIR resource and source properties should be checked against the selected SDK. Keep the downloaded-at/event-time distinction in the domain model and treat malformed/unsupported data as a review state.

## 9. Constrain local AI input

Pass derived, reviewable features instead of raw HealthKit or FHIR payloads whenever possible.

~~~swift
struct HealthReviewFeature: Codable, Sendable {
    let typeIdentifier: String
    let value: Double
    let unit: String
    let sourceCount: Int
    let from: Date
    let to: Date
}

struct LocalHealthReview {
    enum Result: Equatable {
        case insufficientData
        case reviewable(text: String)
    }

    func summarize(_ features: [HealthReviewFeature]) -> Result {
        guard !features.isEmpty else {
            return .insufficientData
        }

        // Call the on-device model only after coverage, authorization,
        // units, and date/source policy have been validated.
        return .reviewable(text: "Review the selected trend.")
    }
}
~~~

Keep the model output descriptive and user-reviewable. Do not infer diagnosis, treatment, or a guaranteed outcome from a local model result.

## 10. Swift Testing fixtures for semantic states

Test the interpretation boundary with pure fixtures before adding a physical HealthKit run.

~~~swift
import Testing

@Test
func emptyHealthResultIsNotZero() {
    let snapshot = HealthDataSnapshot(
        state: .emptyOrLimited,
        queriedType: "stepCount",
        from: .now.addingTimeInterval(-86_400),
        to: .now,
        sourceCount: 0
    )

    #expect(title(for: snapshot) == "No data available for this request")
}

@Test
func unavailableHealthKitUsesFallback() {
    let snapshot = HealthDataSnapshot(
        state: .unavailable,
        queriedType: "stepCount",
        from: .now.addingTimeInterval(-86_400),
        to: .now,
        sourceCount: 0
    )

    #expect(title(for: snapshot) == "Health data is unavailable")
}
~~~

These tests prove app-owned rendering semantics. They do not prove the signed HealthKit capability, the system permission sheet, clinical records, Watch sync, background delivery, or release behavior.

## Sources

- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Setting up HealthKit](https://developer.apple.com/documentation/healthkit/setting-up-healthkit)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [HKHealthStore](https://developer.apple.com/documentation/healthkit/hkhealthstore)
- [requestAuthorization(toShare:read:completion:)](https://developer.apple.com/documentation/healthkit/hkhealthstore/requestauthorization%28toshare%3Aread%3Acompletion%3A%29)
- [HKStatisticsCollectionQuery](https://developer.apple.com/documentation/healthkit/hkstatisticscollectionquery)
- [HKObserverQuery](https://developer.apple.com/documentation/healthkit/hkobserverquery)
- [HKAnchoredObjectQuery](https://developer.apple.com/documentation/healthkit/hkanchoredobjectquery)
- [HealthKitUI](https://developer.apple.com/documentation/healthkitui)
- [HKActivityRingView](https://developer.apple.com/documentation/healthkitui/hkactivityringview)
- [HKActivitySummary](https://developer.apple.com/documentation/healthkit/hkactivitysummary)
- [Accessing Health Records](https://developer.apple.com/documentation/healthkit/accessing-health-records)
- [HKClinicalTypeIdentifier](https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier)
- [HKClinicalRecord](https://developer.apple.com/documentation/healthkit/hkclinicalrecord)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing](https://developer.apple.com/documentation/testing)
