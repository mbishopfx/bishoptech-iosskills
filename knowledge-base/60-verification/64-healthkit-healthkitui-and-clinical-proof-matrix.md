# HealthKit, HealthKitUI, and clinical proof matrix

HealthKit proof must establish the signed target, purpose, actual authorization state, bounded query behavior, source/date interpretation, and privacy-safe output. Clinical-record proof adds the nested capability, read-only type permissions, FHIR provenance, privacy policy, and institution/device conditions. A simulator sample or activity-ring preview is not enough.

| Claim | Evidence | Failure fixture / boundary |
| --- | --- | --- |
| The named target can use HealthKit | Built target has the HealthKit capability and intended required-device behavior | Xcode checkbox or source import without signed artifact |
| HealthKit is available | Physical target records isHealthDataAvailable and device/account context | Simulator or unsupported device treated as production proof |
| Purpose strings match behavior | Built Info.plist contains accurate read/write strings only for used features | Generic copy, missing key, or string broader than implementation |
| Authorization is narrow | System sheet and target logs show only the selected read/write types | All-data onboarding request or feature requests unused types |
| Empty read is handled privately | Denied/limited/empty fixtures render “no data available for this request” without claiming denial | App infers permission from zero samples |
| Limited date access is visible | A restricted window shows query range, last refresh, and a smaller-range/Settings recovery | Full-history copy when only recent data is accessible |
| Settings changes are rechecked | Return-from-Settings test updates the app-owned state and reruns a bounded query | Permission state cached forever |
| Standard sample identity is preserved | Stored fixture includes type, unit, date/time zone, source, and derived/raw marker | Value copied without provenance |
| Snapshot query is bounded | Query fixture names sample type, predicate, date window, source count, and result count | Unbounded history fetch or query used as a subscription |
| Anchored changes are correct | Persisted anchor, added samples, deleted samples, and replay behavior are tested | Anchor discarded or deletion ignored |
| Statistics are interpreted correctly | Quantity-only aggregation fixture explains interval, options, empty bucket, and source merge behavior | Workout/correlation data treated as quantity statistics |
| Observer delivery is completed | Physical-device observer callback runs follow-up query and always calls completion handler | Callback treated as payload or completion omitted |
| Background delivery is real | Physical device receives the configured delivery and records wake/query evidence | Simulator background query treated as proof |
| Activity rings use Apple semantics | HKActivityRingView renders a supplied HKActivitySummary with date/source context | Custom gradient called an Apple ring without semantic equivalence |
| Empty ring differs from zero ring | Nil quantity and zero quantity fixtures produce distinct text and visual evidence | Missing data shown as no activity |
| Paired-Watch state is known | Device and Watch pairing/source evidence recorded with summary query | Watch availability assumed from ring appearance |
| Clinical capability is justified | Signed target includes Clinical Health Records only for a real feature and App Review evidence | Capability enabled but records unused |
| Clinical usage copy is present | Built Info.plist includes NSHealthClinicalHealthRecordsShareUsageDescription and valid policy URL | Standard HealthKit copy used for clinical records |
| Clinical types are read-only | Authorization set uses clinical types in read only; save path is rejected by design | Clinical records placed in share set or saved |
| Required clinical types are deliberate | If used, three or more required types and denial behavior are tested without exposing which type failed | Required key used as a broad prompt shortcut |
| FHIR provenance is preserved | Fixture stores clinical type, FHIR resource type, identifier, source, download timestamp, event fields, and parser status | Download time confused with event time |
| Clinical attachments are protected | Note/attachment fixture verifies type, redaction, local retention, and unsupported-file behavior | Raw document data in logs/screenshots |
| AI uses authorized evidence | Model fixture contains type, source, date window, coverage, and uncertainty; output is reviewable | Model fills gaps, diagnoses, or uses unauthorized data |
| Local processing boundary is visible | Test verifies no raw HealthKit/FHIR payload is sent to analytics or a remote model unless explicitly authorized | “On device” claim with hidden upload/logging |
| Accessibility is complete | VoiceOver, Dynamic Type, high contrast, Reduce Motion, Voice Control, and Switch Control complete permission/review/settings tasks | Color-only status or inaccessible glass controls |
| Privacy/release proof exists | Privacy policy, data retention/export/delete review, archive, signing, device/OS, and distribution artifacts are attached | Preview, Debug, or screenshot treated as release proof |

## Fixture set

- HealthKit unavailable;
- not requested, request-complete, empty, limited, stale, changed-in-Settings;
- denied read with only app-authored sample visible;
- narrow quantity and category type sets;
- source/device/time-zone variation;
- anchored additions and deletions;
- statistics empty bucket and merged-source fixture;
- observer callback with follow-up error and completion;
- physical background delivery;
- activity ring nil, zero, partial, future-day, and no-paired-Watch states;
- clinical type authorization and read-only guard;
- required clinical authorization denial;
- FHIR identifier/type/source collision;
- download timestamp versus clinical-event timestamp;
- malformed JSON and unsupported attachment;
- local model unavailable, low coverage, non-diagnostic result, and user correction;
- raw-data redaction, export/delete, accessibility, localization, and offline recovery.

## Evidence ladder

1. Unit and fixture tests for pure access-state, query-window, provenance, and AI-fallback logic.
2. Built Info.plist and entitlement inspection for the named target.
3. Simulator UI/query fixtures where Apple documents supported sample data.
4. Physical iPhone and intended Apple Watch/paired-device tests for authorization, source, activity, and background behavior.
5. Clinical-record test account/institution fixture and FHIR parser review when that branch is used.
6. Accessibility, privacy, retention, export/delete, and App Review checks.
7. Archive, signing, and distribution evidence.

Record the bundle ID, target, SDK/OS, device model, paired-Watch state, HealthKit type set, query window, source count, authorization outcome, sample/anchor/deletion state, model version, and remaining proof gaps. Never generalize one person’s HealthKit result into a medical claim.

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
- [HKActivitySummary](https://developer.apple.com/documentation/healthkit/hkactivitysummary)
- [Accessing Health Records](https://developer.apple.com/documentation/healthkit/accessing-health-records)
- [HKClinicalTypeIdentifier](https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier)
- [HKClinicalRecord](https://developer.apple.com/documentation/healthkit/hkclinicalrecord)
- [NSHealthRequiredReadAuthorizationTypeIdentifiers](https://developer.apple.com/documentation/bundleresources/information-property-list/nshealthrequiredreadauthorizationtypeidentifiers)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
