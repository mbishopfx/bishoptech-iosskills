# HealthKit and HealthKitUI sensitive-data route

Use this route when an app needs a narrow, user-authorized health or activity feature on iPhone or Apple Watch. Add the clinical branch only when the product genuinely reads clinical records. Keep standard HealthKit samples, activity summaries, clinical FHIR, local AI, and exported data as separate contracts.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | View, compare, save, or locally review a selected health/fitness signal |
| Target | Named iOS or watchOS target with HealthKit capability and intended device coverage |
| Availability | Check isHealthDataAvailable and actual device/account/paired-Watch conditions |
| Purpose | NSHealthShareUsageDescription, NSHealthUpdateUsageDescription, and clinical purpose keys only when used |
| Authorization | Narrow read/write sets; request near the feature; handle limited, denied, unavailable, and changed states |
| Standard data | HKObjectType, HKQuantityType, HKCategoryType, workout/correlation, and the smallest fitting query |
| Updates | Snapshot, anchored changes, observer/background delivery, or statistics based on the feature |
| Activity UI | HKActivityRingView for an HKActivitySummary, wrapped into SwiftUI when needed |
| Clinical branch | Clinical Health Records capability, read-only HKClinicalRecord/FHIR access, privacy policy, and type-specific consent |
| AI | On-device review only when provenance, coverage, uncertainty, and non-diagnostic wording are explicit |
| Glass | Native controls and Liquid Glass around status/context/actions, never over missing or sensitive evidence |
| Proof | Signed target, permission/Settings, physical-device queries, background delivery, activity states, clinical data, accessibility, privacy, and release evidence |

## 1. Start with the smallest feature contract

Write the feature in one sentence:

- “Show a selected day’s activity summary.”
- “Chart step count for a selected range.”
- “Save a workout note with the user’s explicit action.”
- “Review a medication record locally.”

Then list:

- exact HealthKit types;
- read versus write;
- date range;
- expected source/device;
- offline behavior;
- app-owned retention;
- whether data leaves the device;
- whether the result is descriptive or medically interpreted.

If these answers are unknown, do not start with an all-data authorization sheet.

## 2. Configure the target and built artifact

In the named target:

1. add HealthKit;
2. add only the purpose keys required by the implementation;
3. add Clinical Health Records only for a real clinical-record feature;
4. inspect generated required-device-capability behavior;
5. build and inspect the signed entitlements and Info.plist;
6. verify the privacy policy URL and App Store metadata for clinical access.

Treat source settings and the built artifact as different evidence. A target can compile while the archive has the wrong bundle, missing usage key, incorrect capability, or unintended required-device restriction.

## 3. Request access close to use

Use the narrowest Set of HKObjectType and Set of HKSampleType that the feature needs. Requesting access is not the same as proving data exists. After authorization:

1. run a bounded query;
2. record the requested range and type;
3. interpret empty/limited data without claiming denial;
4. show last refresh, source, and recovery;
5. re-check after returning from Settings or Health.

For clinical records, request each intended HKClinicalTypeIdentifier and keep them read-only. Do not add clinical types to the share set.

## 4. Choose the query lifecycle

| Product behavior | Implementation route |
| --- | --- |
| One chart load | Snapshot/sample or statistics query |
| Incremental local cache | Anchored object query with persisted anchor and deletion handling |
| Daily/hourly aggregation | Statistics collection query over quantity samples |
| React to another app or Watch | Observer query followed by bounded fetch |
| Periodic background refresh | Observer plus background delivery, physically tested |
| Activity rings | Activity summary query and HKActivityRingView |

Do not use observer delivery as a data payload. The observer is a wake-up signal; query the actual data and call the completion handler.

## 5. Model no-data states

The route should distinguish:

- HealthKit unavailable;
- authorization not requested;
- authorization request completed;
- data empty or limited;
- data stale;
- source device missing;
- query error;
- user deleted/changed data;
- clinical records not downloaded;
- unsupported FHIR resource or attachment;
- local model unavailable.

Use cached data only with a timestamp and clear stale treatment. Never replace missing health data with zero.

## 6. Add HealthKitUI only for its semantics

HKActivityRingView is a UIKit view. Use UIViewRepresentable in SwiftUI when the app wants the documented activity-ring visual. Supply an HKActivitySummary and provide text context outside the view:

- date and time zone;
- Move/Exercise/Stand meaning;
- paired-Watch/source status;
- empty versus zero explanation;
- refresh and privacy actions.

If the product needs a custom chart, use Swift Charts or a deliberately tested custom visual and do not call it an Apple activity ring. Preserve the distinction between a HealthKit activity summary and an app-created preview fixture.

## 7. Add the clinical branch deliberately

Clinical records require:

- nested Clinical Health Records capability;
- clinical usage string;
- required record-type metadata only when the feature cannot function without it;
- per-type read authorization;
- privacy policy URL;
- FHIR parsing and type/source identity;
- read-only UI and export/retention policy.

Clinical records are not a substitute for a live medical API or a diagnosis. If an app translates or summarizes FHIR, show the underlying record identity and review path. If the app cannot verify a source or parse the supported resource, stop at “needs review.”

## 8. On-device AI route

Use:

authorized query -> bounded model input -> source/unit/date/coverage validation -> on-device inference -> confidence/uncertainty -> user review -> optional export

Recommended local tasks:

- summarize an activity range in plain language;
- flag a missing-data day;
- cluster user-selected trends;
- extract structured fields from a clinical note for review;
- suggest a follow-up question without diagnosing.

Unsafe shortcuts:

- calling a denied or empty read “zero”;
- treating ring completion as health status;
- generating a treatment recommendation;
- uploading raw HealthKit/FHIR to a model service without a separate consent and data-flow review;
- retaining raw data in logs or analytics.

## 9. Native design and Liquid Glass

Use SwiftUI for the state machine, settings handoff, date/source filters, accessible text, and review controls. Use Liquid Glass to group a small number of controls and preserve a readable fallback. Keep system permission sheets and clinical privacy explanations native/system-owned. Do not use animated material to hide a stale query, limited access, or uncertainty.

## 10. Minimum evidence bundle

- target configuration and built Info.plist;
- signed HealthKit/clinical entitlements;
- availability and device-family matrix;
- read/write/clinical permission states;
- limited or empty-read fixture;
- bounded query with source/date evidence;
- anchor/deletion or observer/background evidence where used;
- physical-device/paired-Watch activity evidence;
- HKActivityRingView empty/zero/partial states;
- clinical-record/FHIR evidence if used;
- local AI no-data and non-diagnostic fallback;
- accessibility/privacy/data-retention review;
- archive and distribution artifacts.

## Sources

- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Setting up HealthKit](https://developer.apple.com/documentation/healthkit/setting-up-healthkit)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [Configuring HealthKit access](https://developer.apple.com/documentation/xcode/configuring-healthkit-access)
- [HKHealthStore](https://developer.apple.com/documentation/healthkit/hkhealthstore)
- [HKObserverQuery](https://developer.apple.com/documentation/healthkit/hkobserverquery)
- [HKAnchoredObjectQuery](https://developer.apple.com/documentation/healthkit/hkanchoredobjectquery)
- [HKStatisticsCollectionQuery](https://developer.apple.com/documentation/healthkit/hkstatisticscollectionquery)
- [HealthKitUI](https://developer.apple.com/documentation/healthkitui)
- [HKActivityRingView](https://developer.apple.com/documentation/healthkitui/hkactivityringview)
- [Accessing Health Records](https://developer.apple.com/documentation/healthkit/accessing-health-records)
- [HKClinicalTypeIdentifier](https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier)
- [HKClinicalRecord](https://developer.apple.com/documentation/healthkit/hkclinicalrecord)
- [NSHealthRequiredReadAuthorizationTypeIdentifiers](https://developer.apple.com/documentation/bundleresources/information-property-list/nshealthrequiredreadauthorizationtypeidentifiers)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
