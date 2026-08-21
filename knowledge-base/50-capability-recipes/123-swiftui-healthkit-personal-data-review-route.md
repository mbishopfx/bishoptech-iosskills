# SwiftUI HealthKit and personal-data review route

Use this route for a SwiftUI dashboard, activity summary, workout review, clinical-record viewer, or local AI health-data explanation. It is intentionally not a medical diagnosis route. HealthKit provides protected, user-authorized data; the app must preserve provenance, date, unit, source, privacy scope, and the limits of any interpretation.

Related pages:

- [SwiftUI HealthKit and personal-data review](../42-framework-deep-dives/92-swiftui-healthkit-personal-data-review.md)
- [SwiftUI HealthKit and personal-data review design](../21-design-deep-dives/120-swiftui-healthkit-personal-data-review-design.md)
- [SwiftUI HealthKit and personal-data review proof matrix](../60-verification/117-swiftui-healthkit-personal-data-review-proof-matrix.md)
- [SwiftUI HealthKit and personal-data review recipes](../70-code-recipes/135-swiftui-healthkit-personal-data-review-recipes.md)

## Route contract

~~~text
feature need
  -> minimum HealthKit type/read/share set
  -> target capability/usage/privacy configuration
  -> system authorization
  -> query/session/data-source owner
  -> normalized record with unit/date/source/revision
  -> SwiftUI review projection
  -> optional local AI proposal
  -> explicit user note/share/export/action
~~~

The route must answer:

| Question | Required answer |
| --- | --- |
| Why is access needed? | A health/fitness purpose stated in the current feature. |
| What is requested? | Exact read/share types and clinical/background capabilities. |
| What does the Boolean mean? | Request processing success, not blanket read authorization. |
| Who owns the store/query? | A lifecycle-aware service/coordinator, not a view body. |
| What is a value? | A sample/summary with type, unit, date, source, and freshness. |
| What does empty mean? | No returned data under the privacy/query model, not necessarily no data exists. |
| What can AI do? | Summarize supplied records or draft a question; it cannot diagnose or grant access. |
| Where do writes go? | HealthKit only after explicit user action and validated sample policy. |
| Where do exports go? | An explicit app/file/share destination with privacy review. |

## State machine

~~~text
Availability
  unknown -> unavailable | available | clinicalRecordsUnsupported

Authorization
  notRequested -> requesting -> completed
  share: notDetermined | authorized | denied
  read: dataAvailable | empty | unavailable | limitedByPolicy

Query
  idle -> loading(revision) -> ready(snapshot)
                       -> empty(range)
                       -> failed(error)
                       -> stale(snapshot)

Live/background
  stopped -> observing -> notified -> refreshing -> stopped
  background: registered | denied | delivered | completionRequired

Review
  hidden -> selected(record) -> detail
  detail -> aiPreparing -> aiProposal -> edit/save/dismiss

Commit
  none -> userConfirmed -> writing | sharing | exporting
                  -> succeeded | failed | cancelled
~~~

Do not use “healthy,” “normal,” or “improved” as a generic success state. Those are claims with product, clinical, and review implications.

## 1. Define the minimum type set

Create separate sets for what the feature reads and what it writes:

~~~swift
import HealthKit

struct HealthRequest: Sendable {
    let readTypes: Set<HKObjectType>
    let shareTypes: Set<HKSampleType>
    let reason: String
}

func activityDashboardRequest() throws -> HealthRequest {
    guard let stepType = HKObjectType.quantityType(forIdentifier: .stepCount),
          let activeEnergyType = HKObjectType.quantityType(forIdentifier: .activeEnergyBurned)
    else {
        throw HealthRouteError.unsupportedType
    }

    return HealthRequest(
        readTypes: [stepType, activeEnergyType],
        shareTypes: [],
        reason: "Show activity totals for the selected date range."
    )
}
~~~

The exact type identifiers depend on the product. Do not ask for all available types because the model or dashboard might someday use them. Add clinical types, workout types, and write types only when the current feature requires them.

## 2. Own authorization in a feature service

Request from an active user action or feature entry, not from every card:

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

The completion/success result means the authorization request processed without an error; it does not disclose every read choice. Re-run the query and reflect the data HealthKit returns. Use authorizationStatus for share status where appropriate, but do not infer denied read access from an empty query.

## 3. Normalize samples with provenance

Preserve unit, dates, source, and query revision:

~~~swift
struct HealthValue: Identifiable, Equatable, Sendable {
    let id: String
    let typeIdentifier: String
    let value: Double
    let unit: String
    let startDate: Date
    let endDate: Date
    let sourceName: String?
    let sourceBundleIdentifier: String?
    let queryRevision: Int
    let fetchedAt: Date
}

func normalize(
    _ sample: HKQuantitySample,
    revision: Int,
    unit: HKUnit
) -> HealthValue {
    HealthValue(
        id: sample.uuid.uuidString,
        typeIdentifier: sample.quantityType.identifier,
        value: sample.quantity.doubleValue(for: unit),
        unit: unit.unitString,
        startDate: sample.startDate,
        endDate: sample.endDate,
        sourceName: sample.sourceRevision.source.name,
        sourceBundleIdentifier: sample.sourceRevision.source.bundleIdentifier,
        queryRevision: revision,
        fetchedAt: .now
    )
}
~~~

This is a display projection. Keep conversions explicit and type-specific. Do not convert different quantities into a common score merely to make a chart easier to draw.

## 4. Choose one-shot versus incremental query

Use the smallest query that satisfies the screen:

| Screen need | Query route | Lifecycle |
| --- | --- | --- |
| Latest samples | HKSampleQuery/descriptor | One-shot; cancel or replace on input change. |
| Daily totals | HKStatisticsCollectionQuery/descriptor | Date-bucketed and unit-aware. |
| New/deleted samples | HKAnchoredObjectQuery | Persist/reconcile anchor and deleted objects. |
| Refresh notification | HKObserverQuery | Follow notification with a concrete query. |
| Activity rings | HKActivitySummaryQuery | Date-based summary, with missing/zero distinction. |
| Clinical records | HKSampleQuery or descriptor for clinical type | Parse FHIR with record/source context. |

`HKObserverQuery` does not contain the changed records. A background update handler must perform the follow-up query and call the provided completion handler after processing. Background server queries are not proven by the Simulator.

## 5. Keep query ownership and revision explicit

~~~swift
actor HealthQueryCoordinator {
    private var revision = 0
    private var activeQuery: HKQuery?
    private let store: HKHealthStore

    init(store: HKHealthStore) {
        self.store = store
    }

    func begin(type: HKSampleType, predicate: NSPredicate?) -> Int {
        revision += 1
        if let activeQuery { store.stop(activeQuery) }
        // Build and execute the concrete query for this revision.
        return revision
    }

    func stop() {
        if let activeQuery { store.stop(activeQuery) }
        activeQuery = nil
    }
}
~~~

The exact query callback and actor bridge are SDK-sensitive. The invariant is that a response from an older query revision cannot overwrite a newer date range, type set, source filter, or authorization state.

## 6. Project activity summaries and rings

Activity summaries use a date predicate and can be rendered in the native ring view or a text/chart projection:

~~~swift
struct ActivityDay: Identifiable, Sendable {
    let id: Date
    let move: String?
    let exercise: String?
    let stand: String?
    let hasData: Bool
}

func activityDay(_ summary: HKActivitySummary, calendar: Calendar) -> ActivityDay {
    let day = summary.dateComponents(for: calendar)
    let date = calendar.date(from: day) ?? .now
    return ActivityDay(
        id: date,
        move: summary.appleMoveTime?.description,
        exercise: summary.appleExerciseTime?.description,
        stand: summary.appleStandHours?.description,
        hasData: summary.appleMoveTime != nil
    )
}
~~~

The property names and formatting must be checked against the selected SDK. The visual contract matters more than the sketch: a nil summary value is not the same as a zero value, and the user receives text context even when the ring view is empty.

## 7. Use HealthKitUI only for the appropriate native surface

Embed HKActivityRingView through a platform bridge when the product needs the Apple activity ring. Keep it visually distinct from app-specific rings and label the selected day. If the app wants a custom chart, use Swift Charts or standard SwiftUI visuals with explicit units and no implication that the custom chart is an Apple Health system surface.

For a clinical record, prefer a native app-owned list/detail route with a source/date/type label rather than a decorative card. Use HealthKitUI or system-owned UI only where the framework provides the intended surface; do not assume every HealthKit class has a SwiftUI view.

## 8. Clinical-record route

~~~swift
struct ClinicalRecordSummary: Identifiable, Sendable {
    let id: String
    let recordType: String
    let sourceName: String?
    let authoredDate: Date?
    let effectiveDate: Date?
    let summaryText: String
    let parserRevision: String
}
~~~

The app must enable Clinical Health Records, provide the clinical-record usage description, request read permission for the exact clinical types, and preserve the FHIR source context. Clinical records are read-only in the documented route; do not offer a generic “save this diagnosis” button.

If no supported institution has been connected, show that no records are available rather than an empty “healthy” state. A model may draft a question from selected records, but the original record stays accessible and the result is labeled as generated.

## 9. Background delivery and live updates

Use background delivery only when the feature has a clear need and the target is configured:

~~~text
signed HealthKit/background capability
  -> observer query installed early
  -> background delivery enabled for specific type/frequency
  -> system wakes app/handler
  -> follow-up query reads changes
  -> projection updates
  -> completion handler called
  -> stale/energy policy applied
~~~

Do not request background delivery for a dashboard that only refreshes when opened. Do not assume background reads work while the device is locked; HealthKit encrypts the store and access can be constrained. Keep the last-known snapshot with timestamp and explain when a refresh is delayed.

## 10. On-device AI proposal route

Only pass selected, minimum-needed, normalized data:

~~~swift
struct HealthAIContext: Codable, Sendable {
    let sourceRevision: Int
    let dateRange: ClosedRange<Date>
    let values: [Value]

    struct Value: Codable, Sendable {
        let type: String
        let value: Double
        let unit: String
        let date: Date
        let source: String?
    }
}

struct HealthAIProposal: Codable, Sendable {
    let sourceRevision: Int
    let summary: String
    let missingContext: [String]
    let suggestedQuestion: String?
}
~~~

Validate that the proposal’s revision and range match the visible data. Replace model-written values with the deterministic display values. Reject diagnostic, treatment, emergency, or guaranteed-outcome language according to the product policy. A safe fallback is a source-linked factual summary or “insufficient data.”

## 11. Explicit destinations and writes

HealthKit data should go only to destinations the person chooses:

| Action | Destination |
| --- | --- |
| View data | App-owned dashboard/detail. |
| Refresh | Query coordinator. |
| Change permission | System Settings/Apple Health. |
| Save a workout/metric | HealthKit after explicit confirmation and valid sample policy. |
| Save AI note | App-owned note storage after edit/confirm; not automatically HealthKit. |
| Share/export | Share sheet/file destination with data-range/source summary and confirmation. |
| Ask clinician | User-composed message or note, never automatic contact. |
| Start live workout | HealthKit workout session route with device/session proof. |

Do not let a generated string become a HealthKit write. The model proposes; typed code validates; the user confirms; the selected framework performs the action.

## 12. SwiftUI shell and Liquid Glass

~~~swift
struct HealthReviewScreen: View {
    @StateObject private var model = HealthReviewModel()

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HealthPurposeHeader(state: model.authorization)
                HealthAvailabilityView(state: model.availability)
                HealthDataProjectionView(snapshot: model.snapshot)
                HealthAIReviewView(proposal: model.aiProposal)
                HealthPrivacyActions(model: model)
            }
            .padding()
        }
        .task { await model.refreshIfAuthorized() }
    }
}
~~~

Apply Liquid Glass to bounded headers/status/review groups only. Keep sensitive values and clinical text on a high-contrast material or opaque surface. Use accessibility-aware fallback, and do not visually imply a live update or health improvement that the data does not support.

## 13. Verification fixtures

Create fixtures for:

- HealthKit unavailable;
- authorization not requested, request error, share denied, share authorized;
- empty read result that must not be described as no health data;
- partial/limited date range;
- stale cached snapshot;
- one quantity with unit/date/source;
- category sample with documented category value;
- deleted anchored sample;
- observer notification followed by failed query;
- activity ring missing versus zero values;
- workout active/paused/interrupted/finished;
- clinical record absent, malformed FHIR, and valid selected record;
- AI unavailable/insufficient data/valid proposal/diagnostic language rejected;
- reduced transparency/Dynamic Type/VoiceOver/RTL/input.

## 14. Stop conditions

Stop before implementation if:

- the app cannot explain why it needs each requested type;
- it requests read/write/clinical/background access “just in case”;
- the design equates an empty query with denial or absence of data;
- values have no units, dates, source, or freshness;
- an activity ring or AI summary is being marketed as a medical conclusion;
- background delivery lacks a signed device/energy plan;
- an AI feature would need raw clinical records or broad history without a minimum-data policy;
- the release artifact lacks HealthKit capabilities, usage descriptions, privacy policy, or target/device proof.

## Sources

- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Setting up HealthKit](https://developer.apple.com/documentation/healthkit/setting-up-healthkit)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [HKHealthStore](https://developer.apple.com/documentation/healthkit/hkhealthstore)
- [HKAuthorizationStatus](https://developer.apple.com/documentation/healthkit/hkauthorizationstatus)
- [HKSample](https://developer.apple.com/documentation/healthkit/hksample)
- [HKQuantitySample](https://developer.apple.com/documentation/healthkit/hkquantitysample)
- [HKCategorySample](https://developer.apple.com/documentation/healthkit/hkcategorysample)
- [Queries](https://developer.apple.com/documentation/healthkit/queries)
- [HKSampleQuery](https://developer.apple.com/documentation/healthkit/hksamplequery)
- [HKAnchoredObjectQuery](https://developer.apple.com/documentation/healthkit/hkanchoredobjectquery)
- [HKStatisticsQuery](https://developer.apple.com/documentation/healthkit/hkstatisticsquery)
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
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
