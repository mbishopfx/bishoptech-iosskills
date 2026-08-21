# HealthKit, HealthKitUI, and clinical-record boundaries

HealthKit is Apple’s permission-controlled store for health and fitness data on iPhone and Apple Watch. HealthKitUI adds a small UIKit surface for presenting activity-ring state. Clinical-record support adds a more sensitive, read-only route for FHIR-backed records from supported healthcare institutions. These are related surfaces, not interchangeable permissions or a general-purpose sensor API.

Use this route when an app needs a narrow health-data workflow:

setup and capability -> availability -> purpose strings -> just-in-time authorization -> query/observer -> source and date interpretation -> local review -> privacy-safe output

Keep the requested type set, user authorization, data actually returned, source device, clinical-record provenance, derived features, AI output, and medical conclusion as separate facts.

## 1. HealthKit is a target capability and privacy contract

The normal setup path is:

1. enable the HealthKit capability for the named target;
2. create an HKHealthStore;
3. check HKHealthStore.isHealthDataAvailable();
4. add the read and write purpose strings the target actually uses;
5. request only the concrete sample/object types needed for the current feature;
6. handle denial, limited access, unavailable data, and settings changes.

Xcode may add HealthKit to the target’s required device capabilities. If HealthKit is optional for the product, inspect that generated requirement rather than accidentally preventing installation on unsupported devices. A source-level capability checkbox, an Info.plist key, or an HKHealthStore instance is not proof that the signed target has the correct entitlement.

The standard keys are:

- NSHealthShareUsageDescription for reading;
- NSHealthUpdateUsageDescription for saving;
- NSHealthClinicalHealthRecordsShareUsageDescription for clinical records;
- NSHealthRequiredReadAuthorizationTypeIdentifiers when required clinical types are part of the app’s minimum function.

Only enable Clinical Health Records when the app truly uses those records. The setup documentation calls out App Review risk for an app that enables the capability without using it.

## 2. Authorization is fine-grained and intentionally non-observational

HKHealthStore.requestAuthorization(toShare:read:) accepts separate sets for types the app may save and types it wants to read. Request access close to the feature that needs it so the system sheet has a comprehensible purpose. Do not ask for every type during onboarding merely because the SDK exposes them.

HealthKit’s privacy model has an important asymmetry: an app generally cannot distinguish “the person denied read access” from “there are no readable samples.” For a type the app cannot read, a query can return only data the app successfully wrote. A person can also grant a limited recent window rather than the full history. Store an app-owned access state such as not-requested, request-complete, feature-available, limited-or-empty, and unavailable; do not label an empty query “permission denied” unless a separate system error says so.

getRequestStatusForAuthorization can help decide whether presenting a request is useful, but it is not a data-availability test and does not replace handling the query result. Authorization can change in the Health app or Settings while the app is not running.

## 3. Types and provenance matter

Use HKObjectType factories to request the narrowest supported type:

- quantity types for measurements such as step count or active energy;
- category types for discrete states;
- workouts and correlations for compound activity records;
- characteristic types for relatively stable attributes;
- clinical types for FHIR-backed records.

HealthKit samples carry dates, source information, metadata, and type identity. A daily aggregate is not the same fact as a raw sample; a sample from Apple Watch is not automatically equivalent to one written by the iPhone; and a value copied into an app database loses context unless the app stores the source, unit, time zone, and query policy beside it.

Normalize into an app-owned model only after the query result is known. Keep a redacted audit record of requested type, predicate/window, source count, sample count, and authorization outcome. Do not log raw health values, clinical JSON, medications, notes, or identifiers into ordinary analytics.

## 4. Query choice is a lifecycle decision

Choose the smallest query that matches the feature:

| Need | Route | Important boundary |
| --- | --- | --- |
| One bounded set of samples | Sample query | The result is a snapshot, not a subscription |
| New/deleted changes since a token | Anchored object query | Persist the anchor and handle deletions; a token is not a complete history |
| Aggregate graph over fixed intervals | Statistics or statistics-collection query | Statistics collection is for quantity samples; explain empty/limited intervals |
| React to store changes | Observer query | It signals work; run the follow-up query and always call the completion handler |
| Activity-ring day summary | Activity summary query | The summary is not a writable HealthKit sample |

Observer queries and background delivery are separate from guaranteed execution. The app must be able to start, resume, and finish work within the system’s background budget. Apple explicitly notes that background server queries are not supported by the Simulator; prove this route on an intended physical device.

For an observer callback, treat the callback as “something may have changed,” then run a bounded query for the relevant type and time range. Never infer that a callback means a new sample exists, that every source synchronized, or that a user’s entire history is now available.

## 5. Activity rings are a UIKit semantic surface

HealthKitUI defines HKActivityRingView, a UIView that renders an HKActivitySummary. The view can show Move, Exercise, and Stand rings, or only the Move ring for the move-time mode. Apple documents meaningful visual states:

- nil-valued summary quantities produce empty rings, useful for no summary or a future day;
- zero-valued quantities produce a dot at the top of the ring;
- each visible ring requires both its value and goal quantity;
- data from the HealthKit store may show only the Move ring when no Apple Watch is paired.

Do not rebuild the rings as decorative SwiftUI gradients when the product is meant to represent Apple activity-summary semantics. Wrap HKActivityRingView with UIViewRepresentable when it belongs in a SwiftUI screen, and put surrounding copy, date context, goal explanation, privacy state, and VoiceOver labels in SwiftUI. The ring view’s black rectangle and color treatment are part of the documented control; preserve contrast and ensure the surrounding surface does not imply that empty means zero or that zero means missing data.

The ring view is not a permission prompt, a diagnosis, a readiness score, or an AI recommendation. It is a display of a supplied HKActivitySummary.

## 6. Clinical records are a separate read-only route

Clinical records use HealthKit’s FHIR support. Users first download records from a supported healthcare institution; HealthKit then represents individual records such as conditions, procedures, lab results, medications, and vital signs as HKClinicalRecord samples.

Clinical access requires:

- the HealthKit capability;
- the nested Clinical Health Records capability;
- NSHealthClinicalHealthRecordsShareUsageDescription;
- permission for every clinical record type the app intends to read;
- a valid privacy policy URL for the App Store submission and clinical permission sheet;
- a real reason for the app to use clinical records.

Clinical record types are read-only. Do not put them in the share set or attempt to create/save new HKClinicalRecord objects. Clinical permission may appear in a separate sheet from ordinary HealthKit authorization so the person understands the sensitivity of the approval.

HKClinicalRecord.startDate and endDate represent when HealthKit downloaded the FHIR data, not necessarily when the clinical event occurred. For identity, consider the FHIR identifier, resource type, and source together. HKFHIRResource.data contains the underlying JSON and demands deliberate parsing, redaction, retention, and error handling. A clinical type and an FHIR resource type are related but not one-to-one; medication queries can span multiple FHIR resource kinds unless narrowed with the documented predicates.

The NSHealthRequiredReadAuthorizationTypeIdentifiers key is a hard requirement route, not a convenience switch. Apple requires at least three required clinical types for this privacy mechanism, and a denial can fail authorization without revealing which required type was denied. Use it only when the app genuinely cannot operate without those records.

## 7. On-device AI must preserve source and uncertainty

HealthKit can supply features to an on-device model, but authorization is not a medical validation layer and a local model is not a clinician. A reviewable local route is:

authorized type set -> bounded query -> source/date/unit normalization -> missing/limited-data check -> local inference -> confidence and provenance -> user review -> optional app-owned export

The model input should retain type identity, unit, source, date window, coverage, and whether a value is directly observed or derived. The result should be able to say insufficient data, limited history, conflicting sources, unavailable on this device, or needs professional review.

Do not turn step count, activity rings, sleep, heart rate, medications, clinical notes, or FHIR JSON into diagnostic, treatment, or guaranteed wellness claims. Avoid sending raw health or clinical records to a server merely because remote inference is convenient. On-device execution can reduce exposure but does not replace consent, data minimization, privacy policy, or review obligations.

## 8. Liquid Glass belongs around state, not over uncertainty

Use native SwiftUI controls and system surfaces for permission explanations, status, filters, review, and settings handoff. Liquid Glass can group a small number of meaningful controls:

- data source and last refresh;
- authorization or limited-access state;
- selected date range;
- “review locally” and “manage access” actions;
- data deletion or export status.

Do not make sensitive data collection look like a game by placing live clinical values inside a glowing hero. Do not use translucency to hide unavailable, limited, or stale data. Keep a stable readable text layer, respect Dynamic Type and Reduce Motion, and make the privacy policy and settings route reachable without a decorative interaction.

## 9. Availability and proof boundaries

HealthKit support differs by OS, device family, account state, paired Watch, sample type, clinical-record availability, and signed capability. Simulator sample data can exercise deterministic query and UI states, but it does not prove Watch synchronization, background delivery, institution data, permission behavior, or production entitlement. Activity-ring previews and manually created HKActivitySummary objects prove rendering only.

Prove separately:

1. target capability, usage strings, clinical nested capability, and signed entitlements;
2. isHealthDataAvailable and target device behavior;
3. authorization sheet, limited access, denial, and Settings changes;
4. bounded query, source/date interpretation, deletion/anchor behavior;
5. background observer delivery on a physical device;
6. activity-ring empty, zero, partial, and paired-device states;
7. clinical FHIR record access and read-only handling;
8. local AI no-data, low-confidence, and non-diagnostic fallback;
9. accessibility, privacy, data retention, and release artifacts.

An API symbol, permission sheet, nonempty simulator fixture, ring preview, or model summary is not proof of lawful access, complete history, clinical correctness, or release readiness.

## Sources

- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Setting up HealthKit](https://developer.apple.com/documentation/healthkit/setting-up-healthkit)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [Configuring HealthKit access](https://developer.apple.com/documentation/xcode/configuring-healthkit-access)
- [HKHealthStore](https://developer.apple.com/documentation/healthkit/hkhealthstore)
- [requestAuthorization(toShare:read:completion:)](https://developer.apple.com/documentation/healthkit/hkhealthstore/requestauthorization%28toshare%3Aread%3Acompletion%3A%29)
- [HKObjectType](https://developer.apple.com/documentation/healthkit/hkobjecttype)
- [HKObserverQuery](https://developer.apple.com/documentation/healthkit/hkobserverquery)
- [HKAnchoredObjectQuery](https://developer.apple.com/documentation/healthkit/hkanchoredobjectquery)
- [HKStatisticsCollectionQuery](https://developer.apple.com/documentation/healthkit/hkstatisticscollectionquery)
- [HKActivitySummary](https://developer.apple.com/documentation/healthkit/hkactivitysummary)
- [HealthKitUI](https://developer.apple.com/documentation/healthkitui)
- [HKActivityRingView](https://developer.apple.com/documentation/healthkitui/hkactivityringview)
- [Accessing Health Records](https://developer.apple.com/documentation/healthkit/accessing-health-records)
- [HKClinicalTypeIdentifier](https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier)
- [HKClinicalRecord](https://developer.apple.com/documentation/healthkit/hkclinicalrecord)
- [NSHealthClinicalHealthRecordsShareUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nshealthclinicalhealthrecordsshareusagedescription)
- [NSHealthRequiredReadAuthorizationTypeIdentifiers](https://developer.apple.com/documentation/bundleresources/information-property-list/nshealthrequiredreadauthorizationtypeidentifiers)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
