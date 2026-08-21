# SwiftUI HealthKit and personal-data review design

This page defines an Apple-native design language for sensitive health and fitness surfaces. The visual goal is calm clarity: the person should know what the app is asking to read or write, what data is available, how current it is, where it came from, and what a generated explanation can and cannot mean.

## Design goal

Use this sequence:

~~~text
why this feature needs health data
  -> system authorization
  -> current data/scope/freshness
  -> app-owned chart, ring, or record review
  -> optional local AI explanation
  -> explicit user note or non-medical action
~~~

The app should remain useful when the person declines access. A denied permission is not an empty product; it is a state with a clear alternative.

## Permission entry design

Do not ask for HealthKit access at launch unless the first task genuinely needs it. Instead:

1. show the feature and the benefit in plain language;
2. state the exact data types and whether the app reads or writes;
3. offer a skip/free/manual path;
4. present the system permission sheet;
5. return to an explicit result state;
6. link to Settings/Apple Health for later changes without recreating the system permission UI.

The explanatory screen is not a fake permission sheet. It should be shorter, product-specific, and visually distinct from Apple’s system authorization screen.

## Surface patterns

| Surface | Primary content | Trust cue |
| --- | --- | --- |
| Authorization explainer | Data types, purpose, read/write, skip | “You control this in Apple Health.” |
| Dashboard | Values, date range, unit, source, freshness | “Last updated…” plus source context. |
| Chart detail | Selected point, range, aggregation, unit | Show the exact selected value and date. |
| Activity summary | Native activity rings plus text | Date, goals, missing-data state, app-specific context. |
| Workout detail | Activity, duration, metrics, source | Saved workout versus live session distinction. |
| Clinical record | Record type, source, date, FHIR-derived fields | Imported record/provenance; not a diagnosis. |
| AI explanation | Summary or question draft | Source range, revision, proposal label, edit/dismiss. |
| No-data state | Why the view cannot show data | No data, not authorized, unavailable, stale, or unsupported. |

## Data card anatomy

Every health card should make these fields available:

- title/type;
- value and unit;
- start/end or calendar date;
- source/device/app where relevant;
- query time and freshness;
- aggregation rule such as total, average, minimum, or maximum;
- authorization/availability state;
- an action to inspect, refresh, change access, or dismiss.

Do not put “good,” “bad,” “normal,” or “abnormal” on a card unless the product has an appropriate reviewed policy and the wording is permitted for the intended use. A trend is not a diagnosis.

## Activity rings and Apple-native hierarchy

If the product uses HKActivityRingView, let the native ring be recognizable and give it breathing room. Surround it with the app’s own explanation rather than cloning the Activity app:

~~~text
today’s activity summary
  native Activity ring
  text values and goals
  app-specific insight or selected comparison
  source/date/freshness
~~~

Separate any app-specific ring, score, or trend visual with spacing, labels, or a different chart form. Do not use an Activity ring as a decorative badge for unrelated content. Provide a text summary for VoiceOver and for cases where the ring has missing or zero values.

## Liquid Glass for sensitive data

Use Liquid Glass as a bounded hierarchy layer:

~~~text
glass feature header: purpose and current status
  material/opaque data region: values, charts, and record fields
  glass utility group: refresh, source, privacy, review
  glass AI proposal group: source-linked and dismissible
~~~

Avoid making health numbers float in a transparent decorative layer over a busy background. Sensitive values should remain readable with reduced transparency, increased contrast, Dynamic Type, VoiceOver, and shoulder-surfing in mind.

Good glass candidates include:

- a small status bar showing data source and last update;
- a review card for a selected, local AI-generated summary;
- a toolbar for date range, source filter, and refresh;
- a post-workout summary shell around standard values.

Bad candidates include:

- glass behind every chart point or clinical field;
- animation that implies a health improvement;
- a translucent “permission granted” badge with no text;
- a blurred surface that makes a privacy disclaimer unreadable.

Always provide a system material or opaque fallback.

## No-data and partial-data design

Do not use one empty state for every cause:

| State | Copy direction | Action |
| --- | --- | --- |
| Health data unavailable | “Apple Health data isn’t available on this device.” | Learn more/use manual path. |
| Access not requested | “Connect Apple Health to see this view.” | Explain and request. |
| Query empty | “No records were found for this date range.” | Change date/source or add manual context. |
| Access changed | “Your Apple Health access may have changed.” | Review settings or retry. |
| Limited/partial | “Only the data available to this app is shown.” | Show scope/freshness. |
| Source delayed | “Waiting for the selected source to update.” | Refresh or continue with last known data. |
| Background unavailable | “Data will refresh when the device allows access.” | Keep last-known timestamp and retry. |
| Query failed | “We couldn’t load this data.” | Retry/support; preserve prior snapshot with stale label. |

Never say “You have no heart-rate data” when HealthKit may simply be hiding data the app cannot read.

## Chart design and selection

Charts should preserve units and time semantics:

- label the date range and timezone/calendar policy;
- show selected values with a readable tooltip/row, not only a point highlight;
- distinguish missing samples from zero values;
- label aggregation: total, average, maximum, minimum, or count;
- preserve source revisions when multiple devices contribute;
- allow the user to change range or source without losing context;
- avoid red/green health judgments as the only semantic channel;
- make the same selected value available to VoiceOver, keyboard, pointer, and touch.

If an AI explanation refers to a chart, anchor it to the visible date range and source revision. A chart generated from stale data should visibly say so.

## Workout and live-session design

A live workout screen is not a static dashboard:

~~~text
ready to start
  -> session preparing
  -> active
  -> paused
  -> interrupted/error
  -> ending
  -> saved/reviewable
~~~

The active screen should show session state, elapsed time, selected metrics, device/source, and what the controls do. A stop button should not be disguised as a decorative glass close button. After finish, show the saved workout and the source data used for the summary; do not imply that every displayed metric is collected directly by the phone.

If the app has a watch companion, distinguish primary watch session, mirrored iPhone session, reachability, and stale companion state. A phone dashboard can show the last known update while clearly labeling that it is not live.

## Clinical record design

Clinical records need a more formal detail surface than wellness cards:

- display record type and source institution where available;
- show dates as provided and distinguish authored/effective/update dates;
- preserve original clinical terms alongside any friendly explanation;
- let the person open the source/detail context;
- separate imported record from app-generated note;
- show unavailable, unsupported, incomplete, and parsing-error states;
- avoid alert colors and badges that suggest diagnosis or urgency unless a reviewed product policy requires it;
- show the privacy policy and clinical-record purpose in the consent route.

Do not use the Apple Health icon as a button or imitate Apple Health screenshots. Refer to the Apple Health app in user-facing copy according to Apple’s editorial guidance; HealthKit is the developer-facing framework name.

## On-device AI review card

Keep generated output visibly bounded:

~~~text
Generated summary
Based on: activity records, Jan 1–Jan 7, selected sources
What the records show: concise source-linked description
What is missing: absent or stale data
What this does not determine: no diagnosis/guarantee
Actions: edit, save as note, ask a clinician, dismiss
~~~

The model should not be allowed to write to HealthKit or clinical records from a generated sentence. If the user wants to save a note, make that a separate explicit action with its own data model and destination. If the model detects a concerning phrase, route the person to an appropriate human/support path rather than presenting a confident medical conclusion.

## Accessibility and privacy-aware input

Design for:

- VoiceOver reading type, value, unit, date, source, freshness, and state;
- Dynamic Type for clinical names and long localized units;
- reduced transparency and increased contrast;
- reduced motion for live updates and ring progress;
- pointer, keyboard, Voice Control, Switch Control, and touch;
- right-to-left dates and localized number/unit formats;
- focus that does not expose sensitive values unexpectedly after a background refresh;
- explicit confirmation before sharing, exporting, or saving sensitive summaries.

Never hide a data source or permission state in a tooltip that is inaccessible to keyboard or assistive technology. Never rely only on color to communicate a clinical record type or chart status.

## Privacy review checklist

- [ ] The feature genuinely provides health/fitness functionality.
- [ ] Only required read/share types are requested.
- [ ] Read and write purpose text is specific and current.
- [ ] The app does not claim to know data that HealthKit may hide.
- [ ] HealthKit data is not used for advertising or unrelated profiling.
- [ ] Data sent to any server/model is documented, minimized, and user-authorized.
- [ ] Personal health information is not stored in iCloud.
- [ ] Clinical records have capability, usage description, privacy URL, and appropriate purpose.
- [ ] Delete/export/share actions have explicit destinations and confirmation.
- [ ] Local AI proposals are source-linked and non-diagnostic.

## Design review checklist

- [ ] Permission is requested in context, not on cold launch without need.
- [ ] Denied, empty, stale, partial, unavailable, and error states remain useful.
- [ ] Every value has unit/date/freshness/source context.
- [ ] Native Activity rings are not cloned or used as a medical claim.
- [ ] Glass groups the task and falls back legibly.
- [ ] AI cannot expand permission or commit health data silently.
- [ ] VoiceOver, Dynamic Type, reduced transparency/motion, contrast, RTL, keyboard, pointer, and touch are tested.
- [ ] Physical device and signed target evidence is separate from preview/simulator evidence.

## Sources

- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [Setting up HealthKit](https://developer.apple.com/documentation/healthkit/setting-up-healthkit)
- [HKHealthStore](https://developer.apple.com/documentation/healthkit/hkhealthstore)
- [HKAuthorizationStatus](https://developer.apple.com/documentation/healthkit/hkauthorizationstatus)
- [Queries](https://developer.apple.com/documentation/healthkit/queries)
- [HKStatisticsCollectionQuery](https://developer.apple.com/documentation/healthkit/hkstatisticscollectionquery)
- [HKObserverQuery](https://developer.apple.com/documentation/healthkit/hkobserverquery)
- [HKAnchoredObjectQuery](https://developer.apple.com/documentation/healthkit/hkanchoredobjectquery)
- [HKActivitySummary](https://developer.apple.com/documentation/healthkit/hkactivitysummary)
- [HKActivitySummaryQuery](https://developer.apple.com/documentation/healthkit/hkactivitysummaryquery)
- [HKActivityRingView](https://developer.apple.com/documentation/healthkitui/hkactivityringview)
- [HealthKit human interface guidelines](https://developer.apple.com/design/human-interface-guidelines/healthkit)
- [Accessing Health Records](https://developer.apple.com/documentation/healthkit/accessing-health-records)
- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
