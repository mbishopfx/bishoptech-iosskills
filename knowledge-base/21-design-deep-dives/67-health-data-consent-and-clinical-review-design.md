# Health data consent, activity context, and clinical-review design

HealthKit screens sit inside a permission and trust system. A polished iOS 26 surface should make the person understand what data is requested, what the app can actually see, when it was last refreshed, what is missing, and how to change access. Native controls and Liquid Glass can make that state feel calm and precise; they cannot make a vague health claim safe.

The design contract is:

purpose -> narrow request -> system authorization -> visible data scope -> source/date context -> reviewable result -> settings, deletion, and support

## 1. Design the permission moment around a real feature

Do not make the first screen a generic “unlock your health data” wall. Start with the feature the person chose:

- “Show today’s activity summary”;
- “Compare your selected step-count days”;
- “Review a medication record you imported”;
- “Prepare a local, non-diagnostic trend summary.”

Before the system sheet, explain:

1. which HealthKit type is needed;
2. whether the app reads, saves, or both;
3. the date range and source context the feature uses;
4. what the app does when the person declines or grants limited access;
5. whether any data leaves the device;
6. how to revisit access and delete the app’s derived copy.

The app-owned explanation should be shorter than a policy document. The system usage string and privacy policy carry the formal context; the screen should make the immediate decision legible.

## 2. Model health access as visible state

Use separate state dimensions rather than one green “connected” badge:

| State | What the person should see | What the app may do |
| --- | --- | --- |
| Device unavailable | Health data is unavailable on this device | Offer a non-HealthKit route |
| Not requested | Explain the chosen feature and show an action | Request only the needed types |
| Request completed | Access was configured; data is still unknown | Run a bounded query |
| Limited or empty | Show the queried range/source and explain that no complete history is visible | Offer a smaller date range or Settings |
| Data available | Show the last refresh and source/date context | Render the feature and preserve provenance |
| Stale or failed | Explain the last successful refresh and recovery action | Retry bounded work or show cached data with timestamp |
| Clinical access not configured | Explain that records are a separate sensitive route | Do not silently substitute standard samples |

HealthKit’s privacy behavior means the app should not claim “you denied access” merely because a read query is empty. Use language such as “No data was available for this request” and provide the query window and settings route when useful.

## 3. Separate activity display from health interpretation

Activity rings are recognizable, but the surrounding design must preserve their meaning:

- empty rings mean a missing or nil quantity, not necessarily zero activity;
- a dot can represent a zero quantity;
- a ring requires a value and a goal for the relevant metric;
- no paired Apple Watch can change which ring information is available.

Pair an HKActivityRingView with a date, a source explanation, a loading/error state, and a text summary. Do not use ring completion as a diagnosis, personality score, moral judgment, or automatic prescription. Avoid labels such as “good user,” “lazy day,” or “you failed.”

When rings are shown in a Liquid Glass card, the glass is a container for context and actions. It is not the source of truth. Keep the black ring view and value explanation stable while other controls adapt.

## 4. Clinical-record access needs a different visual hierarchy

Clinical records are read-only FHIR-backed data from supported institutions. They deserve a review surface closer to document provenance than to a wellness dashboard:

- record type and display name;
- source institution or source URL when available;
- download/import timestamp versus event date;
- whether the app has full record data or a redacted/unsupported subset;
- attached document availability and file type;
- parsing or validation status;
- local-only versus exported state;
- a clear “not medical advice” boundary where interpretation is offered.

Do not present a clinical record as if it were an app-authored measurement. HKClinicalRecord dates can reflect the time HealthKit downloaded the FHIR data rather than the event date in the record. Preserve both concepts in the UI when the data provides them.

Medication, condition, lab, immunization, procedure, vital-sign, coverage, and clinical-note records may carry very different sensitivity and action implications. Use type-specific copy and avoid a single “health data” label that hides the difference.

## 5. Use an explicit local-review pipeline for AI

For an on-device AI review screen, show the evidence before the conclusion:

1. selected types and date window;
2. source/device coverage;
3. unavailable or limited fields;
4. derived features;
5. model result and confidence/quality cue;
6. user correction or “not useful” action;
7. retention/export controls.

The model should have a visible “insufficient data” state. The app should not fill gaps with invented values, interpret a permission boundary as a medical absence, or imply that a correlation is a diagnosis. Keep model text reviewable and editable, and ensure that a generated explanation never sounds more certain than the measured coverage.

If the app allows an export, identify whether the export contains raw samples, derived aggregates, clinical JSON, or only user-edited notes. Default to the smallest payload and ask again at the boundary where data leaves the device.

## 6. Liquid Glass interaction rules for sensitive state

Liquid Glass can support a calm hierarchy:

- one prominent current-state surface;
- small controls for date range/source/filter;
- secondary actions for Settings, privacy, and support;
- a stable fallback when the glass style is unavailable.

Avoid:

- translucent panels behind dense clinical text;
- animated blur that hides a changed permission state;
- decorative material over a warning or error;
- color-only status;
- automatically opening a permission sheet under a glass tap;
- requiring a long press or gesture to discover deletion/settings actions.

Use content that remains legible when the user enables larger text, increased contrast, Reduce Motion, VoiceOver, Voice Control, or Switch Control. Keep the system prompt as the system prompt; an app-owned glass card must not imitate it.

## 7. Privacy copy should be concrete

Good copy answers “what, why, when, and where”:

- “Read step count for the days you select so the local chart can compare them.”
- “Read clinical medication records you choose to review. Records remain on this device unless you export them.”
- “This summary uses the samples available for the selected range; it does not diagnose or treat a condition.”

Avoid:

- “We need all your health data to personalize everything.”
- “Authorize access to unlock your full potential.”
- “Your denied data means you did not exercise.”
- “AI knows what your body needs.”

Keep permission purpose strings aligned with the actual implementation and App Store metadata. A beautiful explanation with a broader data request than the feature needs is still a trust failure.

## 8. Recovery and settings are part of the happy path

Every HealthKit screen should provide a non-destructive recovery:

- rerun a bounded query;
- choose a shorter range;
- check data source or paired Watch context;
- open Settings/Health access instructions;
- continue with manual or local-only input;
- export or delete the app-owned derived copy;
- contact support without exposing raw health data in a screenshot or log.

Do not loop a permission prompt after denial. Do not make the person re-authorize every launch. Re-check the state when returning from Settings or the Health app, then explain what changed.

## 9. Test the visual meaning, not just the colors

Fixtures should include:

- unavailable device;
- not-requested and request-complete states;
- empty result that could be limited or denied;
- partial date-window access;
- multiple sources with different timestamps;
- stale cached data;
- activity ring nil quantities, zero quantities, partial completion, and no paired Watch;
- clinical record downloaded timestamp versus event timestamp;
- malformed or unsupported FHIR payload;
- local model unavailable, low coverage, and user-corrected output;
- large text, VoiceOver, high contrast, Reduce Motion, and localization expansion.

Screenshot tests can verify layout. They cannot prove HealthKit authorization, background delivery, institution data, or clinical correctness. Pair visual fixtures with signed target, physical-device, privacy, and release evidence.

## Sources

- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Setting up HealthKit](https://developer.apple.com/documentation/healthkit/setting-up-healthkit)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [Accessing Health Records](https://developer.apple.com/documentation/healthkit/accessing-health-records)
- [HKActivityRingView](https://developer.apple.com/documentation/healthkitui/hkactivityringview)
- [HKActivitySummary](https://developer.apple.com/documentation/healthkit/hkactivitysummary)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
