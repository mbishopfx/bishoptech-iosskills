# SwiftUI HealthKit and personal-data review proof matrix

This matrix separates source knowledge, fixture rendering, query logic, system authorization, simulator sample data, signed physical-device behavior, clinical-record account behavior, privacy/release configuration, and any claim about a health outcome. HealthKit proof must remain proportional to the sensitive claim.

## Evidence levels

| Level | Evidence | Can prove | Cannot prove |
| --- | --- | --- | --- |
| H0 | Official Apple source | Framework role, privacy boundary, and stated platform behavior | The app’s target configuration or health-data truth. |
| H1 | SwiftUI fixture/preview | State copy, chart/ring composition, accessibility tree, and fallback rendering | HealthKit authorization, current samples, or physical sensors. |
| H2 | Unit/Swift Testing | Type/unit/date normalization, query revision, stale/deletion policy, AI claim filtering | System store scope, device data, or background delivery. |
| H3 | Simulator sample account | Sample query, clinical-record parsing, ring/chart projection, and UI route | Physical sensor data, background server queries, real institution/account, or production release. |
| H4 | Signed physical device | HealthKit capability, permission sheet, Apple Health store, selected device/source, workout/session and physical input | Complete health history, clinical validity, medical diagnosis, all hardware/OS conditions. |
| H5 | Clinical-record account | Supported institution import and tested FHIR parsing/source presentation | General institution coverage, record completeness, or clinical interpretation. |
| H6 | Privacy/server review | Data minimization, sharing/retention, privacy policy, optional server transfer and deletion | UI accessibility or physical sensor quality. |
| H7 | Archive/TestFlight/release | HealthKit/clinical/background entitlements, usage strings, target membership, privacy URL, signed artifact | User outcomes, medical claims, future data availability, or App Review approval by itself. |

## Fixture contract

Every HealthKit fixture should record:

- target, bundle ID, SDK, deployment target, platform, and device/OS;
- HealthKit availability and capability/entitlement state;
- read/share/clinical/background type sets;
- usage-description text and privacy-policy URL fixture;
- authorization result and data-scope interpretation;
- query type, predicate/date range/calendar/timezone, unit, and aggregation;
- sample/summary/record source, source revision, device, and fetched timestamp;
- missing, deleted, stale, partial, empty, and error states;
- AI model availability, input range, source revision, proposal, validation result, and claim policy;
- accessibility settings, locale/RTL, input mode, transparency/motion/contrast, and Dynamic Type;
- signed account/institution/physical-device details when the claim reaches H4+.

## Availability and authorization matrix

| Gate | Scenario | Expected evidence | Do not infer |
| --- | --- | --- | --- |
| HealthKit unavailable | Unsupported device/setting | Useful fallback and no query attempt | The user denied access. |
| First request | System sheet appears with exact read/share rationale | Usage descriptions and target capability are present. | Completion Boolean means every permission was granted. |
| Share status | Authorized/denied/not determined | Share status is shown only for write policy. | Read status is disclosed the same way. |
| Read empty | Query returns no samples | “No data available for this range” with an alternate action. | User has no health data or denied read access. |
| Access changed | Permission modified in Settings/Apple Health | Foreground refresh and changed state | Cached snapshot remains current. |
| Clinical records | Clinical capability and usage description | Separate consent path and privacy URL | Enabling capability alone proves real records. |
| Background capability | Background delivery configured | Signed target and device observer evidence | Simulator background behavior is representative. |

## Query and normalization matrix

| Query route | Test cases | Evidence |
| --- | --- | --- |
| Sample query | Quantity/category/workout, sort, limit, predicate | Correct type, date, unit, source, and main-actor projection. |
| Statistics query | Sum/average/min/max and incompatible type | Correct aggregation and unit; unsupported request fails visibly. |
| Statistics collection | Day/week buckets, calendar/timezone, missing bucket | Stable date labels, missing versus zero, no duplicate buckets. |
| Anchored query | New samples, deletions, anchor persistence/reset | Incremental projection and deleted-record handling. |
| Observer query | Change notification with follow-up query | Completion handler called after processing; stale response rejected. |
| Activity summary | Missing summary, zero values, Move/Exercise/Stand values | Ring/text projection matches source and date. |
| Clinical query | Valid FHIR, unsupported resource, malformed payload | Source/type/date/provenance retained; parser error visible. |
| Cancellation | Date/type/source changes while query runs | Older revision cannot overwrite newer state. |

## Data interpretation matrix

| Claim | Minimum evidence | Unsafe shortcut |
| --- | --- | --- |
| A value was returned | Sample/summary, type, unit, date, source | A number without unit/date. |
| A day’s activity summary is available | HKActivitySummary for a date | An empty ring means zero activity. |
| A workout was recorded | HKWorkout with dates/activity/source | A live metric means saved workout. |
| Data is current | Source timestamp, query time, freshness policy | “Latest” label without timestamp. |
| Trend exists | Valid range, aggregation, missing-data policy | A few points become a medical trend. |
| Clinical record imported | Authorized record from tested source with FHIR context | A parsed string becomes a diagnosis. |
| AI summary is grounded | Source IDs/revision/range and deterministic values | Model text alone proves record truth. |
| Health outcome improved | Product-specific, reviewed outcome methodology | Chart/ring movement or model confidence. |

## Activity rings and workouts matrix

| Gate | Required scenario | Evidence |
| --- | --- | --- |
| Ring view | Data summary with full values | Native ring plus accessible text summary. |
| Missing ring data | Nil activity summary values | Empty/missing visual is distinguished from zero. |
| No paired watch | Summary only has supported Move context | UI does not imply Exercise/Stand data exists. |
| Workout session | Start/pause/resume/stop/error | Signed physical session state and final saved workout. |
| Device source | iPhone, Apple Watch, external sensor where supported | Source label and device-specific limitation. |
| Lock/background | Device lock and background transition | Observed behavior and stale/read policy. |
| Post-workout | Finish and query saved workout | Saved record differs clearly from live display. |

## Clinical-record matrix

| Gate | Evidence |
| --- | --- |
| Capability | Signed target includes HealthKit and Clinical Health Records only when needed. |
| Usage copy | Clinical record usage description is specific and visible in the system route. |
| Privacy policy | Valid, accessible privacy URL in the app/release metadata. |
| Authorization | Exact clinical types requested and user choice recorded. |
| Source | Supported institution/patient portal or documented simulator sample account. |
| FHIR parsing | Tested resource types, code systems, dates, and malformed/unknown handling. |
| Data boundary | Raw FHIR, parsed record, app summary, and AI proposal are separate artifacts. |
| Review | No diagnosis/treatment/urgency claim is derived solely from a parser or model. |

## On-device AI matrix

| AI state | Fixture | Required behavior |
| --- | --- | --- |
| Unavailable | Model missing/unsupported | Deterministic chart/detail remains usable. |
| Partial data | Missing days/source | Proposal says what is missing and avoids confidence claims. |
| Valid summary | Source-linked selected records | Values/units/dates are deterministic and visible. |
| Stale data | Query revision changes | Proposal is invalidated or marked stale. |
| Diagnostic language | Model emits diagnosis/treatment/guarantee | Validation rejects or rewrites to a safe user-reviewed question. |
| Raw-data overreach | Model asks for full history/clinical payload | Input policy blocks unnecessary data. |
| Write attempt | Proposal requests HealthKit write | No automatic write; explicit typed action required. |
| Export attempt | Proposal asks to share | User chooses destination and reviews the data range/source. |

## Design and accessibility matrix

| Gate | Required fixtures |
| --- | --- |
| VoiceOver | Value, unit, date, source, freshness, missing state, and action read in order. |
| Dynamic Type | Largest supported size with clinical names, units, dates, and chart labels. |
| Contrast/transparency | Increased contrast and reduced transparency preserve sensitive data legibility. |
| Motion | Reduced motion still communicates query refresh, live workout state, and stale data. |
| RTL/localization | RTL date/order, localized units, long source names, and translated consent copy. |
| Keyboard/pointer | Range/source selection, record detail, AI review, save/share, and dismissal. |
| Privacy focus | Sensitive values are not unexpectedly announced after background refresh. |
| Glass fallback | Opaque/system material retains the hierarchy and privacy cue. |

## Background and physical-device matrix

Record:

- observer query setup time and owner;
- background delivery type/frequency/capability;
- device lock/unlock state;
- Apple Watch pairing/reachability if applicable;
- source/device revision and sample timestamps;
- background completion-handler call and retry behavior;
- query duration, memory, main-actor work, and energy impact;
- physical device model/OS, locale, authorization, and test date;
- simulator versus device distinction in every report.

The Simulator is useful for deterministic UI/sample/clinical fixtures but does not close background server-query or sensor evidence.

## Privacy and release matrix

| Gate | Artifact |
| --- | --- |
| Target configuration | HealthKit/clinical/background capability and target membership. |
| Info.plist | Health share/update/clinical usage descriptions. |
| Privacy policy | Valid release URL and app-facing explanation of collection/use/sharing. |
| Data flow | Local storage, server/model transfer, retention, deletion, and export map. |
| Marketing | No health-data advertising/marketing/data mining claims; Apple Health wording follows HIG. |
| iCloud | Personal health information is not stored in iCloud. |
| Archive | Signed entitlements, privacy resources, bundle ID, version/build, and target device requirements. |
| TestFlight/production | Signed account/institution/device evidence with exact environment and date. |

## Artifact checklist

1. Official source registry and target SDK notes.
2. Feature type/read/share/clinical/background matrix.
3. Authorization explanation and usage-description copy.
4. Query fixtures and normalized source/unit/date model.
5. SwiftUI accessibility/localization/Glass screenshots or UI results.
6. Simulator/sample-account test report with clear limitations.
7. Signed physical-device report for the claimed device/session route.
8. Clinical-record source/FHIR parser report if applicable.
9. AI input/proposal/validation/rejection fixtures.
10. Privacy/data-flow/deletion/retention review.
11. Archive/entitlement/Info.plist/privacy URL inspection.

## Stop conditions

Do not close the route from a chart screenshot, sample account, simulator ring, empty-query result, permission Boolean, AI summary, or successful compile. Those artifacts support specific claims, not current health truth, medical interpretation, physical sensor performance, or release readiness.

## Sources

- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Setting up HealthKit](https://developer.apple.com/documentation/healthkit/setting-up-healthkit)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [HKHealthStore](https://developer.apple.com/documentation/healthkit/hkhealthstore)
- [HKAuthorizationStatus](https://developer.apple.com/documentation/healthkit/hkauthorizationstatus)
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
- [HealthKit human interface guidelines](https://developer.apple.com/design/human-interface-guidelines/healthkit)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
