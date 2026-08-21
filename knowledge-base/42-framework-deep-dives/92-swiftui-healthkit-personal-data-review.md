# SwiftUI HealthKit and personal-data review

This deep dive covers the SwiftUI orchestration layer for HealthKit and related personal health surfaces. It is deliberately privacy-first: HealthKit authorization, the data the system returns, app-owned projections, user-entered context, on-device AI proposals, and any health-related action remain separate facts.

It extends the existing [HealthKit, HealthKitUI, and clinical-records](47-healthkit-healthkitui-and-clinical-records.md) deep dive and the [HealthKit sensitive-data route](../50-capability-recipes/70-healthkit-sensitive-data-route.md). The distinct seam here is the SwiftUI review surface: how to ask at the right moment, represent missing or limited data, preserve provenance and units, use activity rings without copying Apple Health, and keep AI explanations from becoming medical conclusions.

## HealthKit is a protected source, not an app database

Use this boundary:

~~~text
product need and permission rationale
  -> HealthKit capability and usage descriptions
  -> separate read/share authorization
  -> HealthKit query or system data surface
  -> source/unit/date/authorization-aware normalization
  -> SwiftUI projection
  -> optional local AI explanation
  -> user review or app-owned action
~~~

Keep these concepts distinct:

| Concept | Meaning | Safe UI statement |
| --- | --- | --- |
| Authorization request completed | The system finished processing the request | “The permission flow finished.” Not necessarily “access granted.” |
| Share authorization | Whether the app may save a selected type | “This app can write this type,” if the status allows that claim. |
| Read result | The data HealthKit returns under its privacy model | “Data available to this app for this query.” |
| Empty result | No data returned, which can include denied read access | “No data available for this view,” not “the user has none.” |
| Sample | A dated value from HealthKit | “Recorded sample from source at time.” |
| Projection | App-owned chart, card, ring, or summary | “This screen summarizes the selected data.” |
| AI proposal | Local model output grounded in supplied records | “A generated explanation,” never a diagnosis by itself. |
| Clinical record | FHIR-backed health record with additional setup/privacy | “Record imported from a supported source,” not verified medical interpretation. |

HealthKit intentionally limits what an app can infer about denied read permissions. An empty query result is therefore not evidence that a person has no health data or that they denied access. Keep the UI conservative.

## Request the minimum data at the right moment

Define the feature before defining the authorization set:

1. Identify the exact quantity/category/workout/clinical types needed.
2. Decide whether the feature reads, writes, or both.
3. Explain the benefit in the current UI context before presenting the system sheet.
4. Configure the HealthKit capability and usage descriptions in the named target.
5. Request only the types needed for the current feature.
6. After the request, re-check availability and the usable result rather than trusting the Boolean completion value.
7. Provide a useful path when access is denied, limited, unavailable, or later changed in Settings/Apple Health.

Separate read and share sets. A feature that only displays steps should not request write access. A logging feature may request write access for the specific sample type while requesting read access only for the comparison it needs.

The usage descriptions are part of the product copy and release artifact. The read message should explain why the app wants to read data; the update message should explain what the app will save. Clinical records require their own additional usage description and capability/configuration.

## Availability, authorization, and privacy states

Use explicit state instead of one “HealthKit ready” Boolean:

~~~text
availability
  unavailable | available | unsupportedClinicalRecords

authorization
  notRequested | requestInFlight | requestCompleted
  shareAuthorized | shareDenied | shareNotDetermined
  readData | readNoData | readLimitedBySystem | readUnavailable

query
  idle | loading | ready | empty | failed | stale

source
  device/app/sourceRevision | unknownSource | mixedSources

freshness
  currentForQuery | delayed | partial | cached | unknown
~~~

The exact authorization enum reports sharing status; read privacy is intentionally more constrained. Do not tell the person “read permission denied” simply because the query is empty unless the system provides a documented signal for that specific route.

For any card, keep the data date range, unit, source/device context where relevant, query time, and freshness visible or inspectable. A number without a date and unit is not an adequate health-data representation.

## HealthKit type families and SwiftUI projections

Choose the query and display based on the type:

| HealthKit type | Typical source object | SwiftUI projection |
| --- | --- | --- |
| Quantity | HKQuantitySample and HKQuantity | Value with unit, date range, source, and aggregation policy. |
| Category | HKCategorySample | Labeled event or state with the category’s documented values. |
| Correlation | HKCorrelation with related samples | Composite record where the constituent data remains inspectable. |
| Workout | HKWorkout and activities/events | Workout detail with duration, activity type, statistics, and source. |
| Activity summary | HKActivitySummary | Activity ring or accessible goal summary for the date. |
| Clinical record | HKClinicalRecord/FHIR resource | Record list/detail with source, type, date, provenance, and privacy-aware parsing. |
| Series/document/specialized sample | Framework-specific sample subtype | Dedicated review route; do not flatten into an arbitrary number. |

HealthKit’s predefined types and units are part of its interoperability contract. Preserve the original type and unit through normalization; convert for display only with a documented unit policy.

## Query ownership and Swift concurrency

The SwiftUI view should not instantiate an unbounded query on every body recomputation. Create a feature-level query owner that:

- owns the HKHealthStore reference;
- starts a one-shot or long-running query for a known data type/predicate;
- retains an HKQuery or query descriptor until it stops;
- handles callback queues and hops to the main actor for UI state;
- cancels/stops the query when the feature no longer needs it;
- carries a revision and query signature into the published snapshot;
- treats errors and empty results as distinct states.

Use query type deliberately:

| Need | Route |
| --- | --- |
| One snapshot of samples | HKSampleQuery or the Swift concurrency descriptor. |
| Incremental changes/deletions | HKAnchoredObjectQuery with a persisted anchor. |
| Sum/min/max/average of quantity samples | HKStatisticsQuery. |
| Time-bucketed chart values | HKStatisticsCollectionQuery. |
| Notification that something changed | HKObserverQuery, followed by a concrete query to read changes. |
| Activity ring summaries | HKActivitySummaryQuery or its Swift concurrency descriptor. |
| Clinical records | HealthKit sample/query APIs with clinical types and FHIR parsing. |

An observer query tells the app that matching data changed; it does not deliver the changed samples itself. Follow it with a sample, anchored, or statistics query and then call the background delivery completion handler after the update is processed.

## Source and revision model

HealthKit data can be written by Apple Watch, iPhone, another app, or multiple devices. Normalize each value with source context:

~~~swift
struct HealthRecord: Identifiable, Sendable, Equatable {
    let id: String
    let typeIdentifier: String
    let startDate: Date
    let endDate: Date
    let displayValue: String
    let unitSymbol: String?
    let sourceName: String?
    let sourceBundleIdentifier: String?
    let queryRevision: Int
    let fetchedAt: Date
}
~~~

This model is a display projection, not a replacement for the HealthKit sample. Keep the original sample or a privacy-reviewed durable identifier only when the product needs it. Do not use a string formatted for a chart as the source of later medical logic.

When samples are deleted or an anchor changes, recompute affected projections. A cached weekly total is stale when the source deletes a sample, the user changes access, the query predicate changes, or the timezone/calendar policy changes.

## Activity rings are a system-derived projection

HKActivitySummary and HKActivityRingView show Move, Exercise, and Stand summaries. The ring view is a native HealthKitUI element with its own black rectangle and ring treatment. Use it when the app genuinely benefits from showing that activity summary, and surround it with app-specific context.

Do not:

- redraw Apple’s rings as a decorative clone;
- use the ring as a diagnosis, readiness score, or guarantee;
- show empty rings as zero data without distinguishing missing versus zero;
- place a second ring system directly beside the Activity rings without clear separation;
- repeat the system’s exact activity notification pattern as if it were app-specific.

Provide an accessible text summary alongside the ring: date, Move/Exercise/Stand values and goals where available, whether data is missing, and the source/freshness context. A ring screenshot does not prove that the underlying HealthKit summary was current on a physical device.

## Workouts and live surfaces

An HKWorkout is a HealthKit sample representing an activity. A live workout app adds session, builder, sensor, background, and device boundaries. Keep them separate from a post-workout dashboard:

~~~text
workout intent
  -> authorization and configuration
  -> session/builder active
  -> live metric updates
  -> pause/resume/error/interruption
  -> finish/save workout
  -> post-workout HealthKit query and review
~~~

Use HKWorkoutSession and HKLiveWorkoutBuilder on the appropriate Apple Watch route when the product needs live workout collection. An iPhone/iPad route may have different sensor availability and often needs an external heart-rate source for heart-rate data. Do not use a simulator or a post-workout sample to claim live sensor behavior.

SwiftUI can display live state and controls, but the session/builder owner should be lifecycle-aware and device-specific. Preserve the difference between an observed live metric, a saved workout, an app goal, and a generated coaching suggestion.

## Clinical records need a separate trust surface

Clinical records are FHIR-backed data from supported healthcare institutions. They have additional setup, usage description, privacy-policy, review, and data-format considerations:

- enable the Clinical Health Records capability only when the app uses it;
- request read permission for each clinical type needed;
- do not request share permission for read-only clinical record types;
- parse and display FHIR resources with source/type/date/provenance;
- keep raw FHIR JSON and derived presentation separate;
- expect no records when a person has not downloaded supported records;
- do not present an imported record as a current diagnosis or complete chart;
- provide privacy policy and clinical-data deletion/retention explanation;
- test sample accounts or simulator data separately from a real signed device/account.

Use a record detail view that makes the source, record type, effective date, authored date if present, and “not medical advice”/care-provider boundary appropriate to the product. Do not let a local model rewrite clinical facts without showing the original record context.

## On-device AI review boundary

HealthKit data is sensitive. A local model can reduce data movement, but on-device processing does not turn a model output into medical truth. Restrict the model input and proposal shape:

~~~text
authorized, minimum-needed records
  -> normalized values with units/dates/source revisions
  -> local model summary or question draft
  -> deterministic validation and claim policy
  -> user review with source references
  -> optional user-entered note or non-medical action
~~~

Reasonable bounded proposals include:

- summarizing a selected week of user-visible activity;
- explaining a chart’s direction using the exact supplied points;
- drafting a question for a clinician from user-selected records;
- grouping workouts by confirmed activity type;
- identifying missing data or conflicting source revisions.

Do not allow the model to diagnose, prescribe, triage an emergency, guarantee a health outcome, infer a condition from a sparse trend, or write health data without explicit user review and a deterministic validation path. If the data is incomplete, the correct output may be “insufficient data.”

Every proposal should include source IDs/revisions, date range, unit policy, model availability, validation result, and a visible “review/edit/dismiss” path. The model cannot expand HealthKit authorization or silently upload records.

## Liquid Glass and sensitive data

Use Liquid Glass to group review context, not to make sensitive collection feel playful or invisible:

~~~text
privacy-aware feature explanation
  glass status/header group
  legible chart/ring/record content
  source/date/unit/freshness labels
  glass review group for a local AI proposal
  explicit save/share/export destination
~~~

Avoid putting private values into an always-visible translucent surface over a shared or lock-screen-like context. Consider the device state, shoulder-surfing, Dynamic Type, VoiceOver, and reduced transparency. A glass background does not replace redaction or authorization.

Use standard charts, labels, and semantic controls. If a chart is interactive, expose the selected date/value/source through accessibility and keyboard/pointer input. Do not rely on color or a ring animation to show a sensitive state.

## Privacy and App Review boundaries

HealthKit is for health and fitness functionality. Keep data use aligned with the product’s stated purpose and do not use HealthKit data for advertising, marketing, or data mining. Do not sell it, disclose it to unrelated third parties, or store personal health information in iCloud. Define the minimum data, retention, sharing, deletion, and support policy before implementation.

Do not build a second in-app settings system that pretends to control HealthKit permissions. Link to the system-managed Settings/Apple Health route when access needs changing. The app can show current product status, but the system owns the authorization controls.

## Accessibility and alternate input

Health data screens must be task-complete for:

- VoiceOver reading a chart/ring/record with date, unit, value, source, and availability;
- Dynamic Type with long clinical labels, dates, units, and source names;
- increased contrast and reduced transparency;
- reduced motion without losing the meaning of a live update;
- Voice Control, Switch Control, keyboard, pointer, and touch on supported targets;
- right-to-left and localized unit/date formatting;
- privacy-aware focus so a sensitive value is not unexpectedly announced after background return.

For every “no data” state, explain whether the data is unavailable, not loaded, empty for the range, outside the permitted window, or not supported on the target. Do not expose private raw values in accessibility labels when the user has not opened the sensitive detail route.

## Performance, energy, and lifecycle

HealthKit queries can involve substantial data. Limit date ranges, predicates, sample counts, and requested fields to the screen. Prefer statistics or anchored queries where they match the need. Avoid querying on every SwiftUI body update or every chart drag without debouncing/cancellation.

Background delivery needs a signed device test, a configured capability, observer setup early enough for delivery, completion-handler discipline, and an energy policy. The Simulator does not prove background server queries. Treat device lock/encryption as a normal state that can make background reads unavailable.

Measure query latency, main-actor projection cost, chart/ring frame behavior, memory for clinical/raw resources, background wake frequency, and battery impact. A local AI summary should be cancellable and bounded.

## Proof boundary

The evidence ladder is separate:

| Artifact | Proves | Does not prove |
| --- | --- | --- |
| Preview fixture | State rendering/copy and accessibility tree for supplied data | HealthKit authorization or current data. |
| Unit/query fixture | Normalization, units, date range, stale/revision policy | System store, privacy filtering, physical sensors. |
| Simulator sample account | UI/query wiring and sample-data behavior | Physical device sensors, background delivery, real account/store, App Review. |
| Signed physical device | Capability, authorization, HealthKit store, system settings, selected sensor/account route | Medical validity, complete history, every OS/device, production release. |
| Clinical-record account | Supported institution import and FHIR parsing for the tested data | General institution coverage or clinical interpretation. |
| Release archive/TestFlight | Entitlement, usage strings, target resources, privacy policy, signed artifact | The user’s health outcomes or every regional/system state. |

Never say “the app knows the user’s health” because a query returned a value. Say what was read, when, from which authorized source, under which data and privacy policy.

## Sources

- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [About the HealthKit framework](https://developer.apple.com/documentation/healthkit/about-the-healthkit-framework)
- [Setting up HealthKit](https://developer.apple.com/documentation/healthkit/setting-up-healthkit)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [HKHealthStore](https://developer.apple.com/documentation/healthkit/hkhealthstore)
- [HKAuthorizationStatus](https://developer.apple.com/documentation/healthkit/hkauthorizationstatus)
- [HKSample](https://developer.apple.com/documentation/healthkit/hksample)
- [HKQuantitySample](https://developer.apple.com/documentation/healthkit/hkquantitysample)
- [HKCategorySample](https://developer.apple.com/documentation/healthkit/hkcategorysample)
- [Units and quantities](https://developer.apple.com/documentation/healthkit/units-and-quantities)
- [Queries](https://developer.apple.com/documentation/healthkit/queries)
- [HKSampleQuery](https://developer.apple.com/documentation/healthkit/hksamplequery)
- [HKAnchoredObjectQuery](https://developer.apple.com/documentation/healthkit/hkanchoredobjectquery)
- [HKStatisticsQuery](https://developer.apple.com/documentation/healthkit/hkstatisticsquery)
- [Executing Statistics Collection Queries](https://developer.apple.com/documentation/healthkit/executing-statistics-collection-queries)
- [HKObserverQuery](https://developer.apple.com/documentation/healthkit/hkobserverquery)
- [Executing Observer Queries](https://developer.apple.com/documentation/healthkit/executing-observer-queries)
- [HKActivitySummary](https://developer.apple.com/documentation/healthkit/hkactivitysummary)
- [HKActivitySummaryQuery](https://developer.apple.com/documentation/healthkit/hkactivitysummaryquery)
- [Executing Activity Summary Queries](https://developer.apple.com/documentation/healthkit/executing-activity-summary-queries)
- [HKActivityRingView](https://developer.apple.com/documentation/healthkitui/hkactivityringview)
- [Workouts and activity rings](https://developer.apple.com/documentation/healthkit/workouts-and-activity-rings)
- [HKWorkout](https://developer.apple.com/documentation/healthkit/hkworkout)
- [HKWorkoutSession](https://developer.apple.com/documentation/healthkit/hkworkoutsession)
- [HKLiveWorkoutBuilder](https://developer.apple.com/documentation/healthkit/hkliveworkoutbuilder)
- [Accessing Health Records](https://developer.apple.com/documentation/healthkit/accessing-health-records)
- [Accessing a User’s Clinical Records](https://developer.apple.com/documentation/healthkit/accessing-a-user-s-clinical-records)
- [HKClinicalRecord](https://developer.apple.com/documentation/healthkit/hkclinicalrecord)
- [HKFHIRResource](https://developer.apple.com/documentation/healthkit/hkfhirresource)
- [HealthKitUI](https://developer.apple.com/documentation/healthkitui)
- [HealthKit human interface guidelines](https://developer.apple.com/design/human-interface-guidelines/healthkit)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
