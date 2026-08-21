# SensorKit research consent and data-review design

SensorKit interfaces are consent and research surfaces before they are dashboards. The visual design must make study purpose, sensor scope, delay, deletion, and interpretation boundaries clear at the exact moment a participant decides whether to share.

## Design the participant’s decision

The participant should be able to answer:

- What study am I joining?
- Which sensors are requested?
- Which sensors are required versus optional?
- What does each sensor contribute to the study?
- When will data become available?
- Can I change my choice later?
- What happens if data is deleted or missing?
- Is this an observation, a model suggestion, or a research conclusion?

Do not reduce a granular SensorKit permission sheet to a colorful “Allow all signals” illustration. Keep the system explanation and the study’s own explanation aligned.

## Study onboarding surface

The containing app should provide a plain-language study overview before requesting the system prompt:

1. study purpose and sponsor identity;
2. sensor-by-sensor reason and expected cadence;
3. required/optional distinction;
4. privacy policy and data retention;
5. 24-hour holding-period explanation;
6. local processing and server/export explanation;
7. withdrawal/support path;
8. what the app can and cannot conclude.

Then let the system present Apple’s Research Sensor & Usage Data sheet. Do not preselect a consent control in an app-owned imitation of the system sheet.

## Sensor status design

Represent each sensor separately:

| State | Copy | Action |
| --- | --- | --- |
| Not determined | “Not yet chosen” | Review system permission |
| Authorized | “Authorized for this study” | Show purpose and recording control |
| Denied | “Not shared” | Explain that the study may be partial; Settings if appropriate |
| Entitlement missing | “Study configuration unavailable” | Support/configuration path, never a new prompt loop |
| Authorized but not recording | “Ready; recording paused” | Start only after user understands the effect |
| Recording | “Recording; research data is held before access” | Pause/stop according to protocol |
| Eligible data | “Available for local review” | Fetch with source/time range visible |
| Deletion gap | “Some data was removed” | Explain gap reason and avoid imputation |

Do not use a green checkmark to imply that a sensor’s data is complete, accurate, or clinically meaningful.

## The 24-hour holding period as a first-class state

A participant should never think “the app lost my data” when SensorKit is intentionally withholding newly recorded samples. Show:

- recording date/time;
- earliest eligible fetch time;
- device source;
- whether the participant can still delete the held data;
- what the study will do if it never becomes available.

Avoid a live graph that draws a gap as zero. Use a neutral “pending availability” treatment and keep the current time window separate from the eligible research window.

## Research review screen

A review surface can show:

- selected sensor and source device;
- time range and data-availability state;
- sample count and deletion-gap count;
- raw/derived distinction;
- model-generated summary marked as generated;
- export or submit action only when allowed by the study;
- privacy/retention disclosure.

Use tables or compact sections for exact values; use charts only when the chart’s units, sampling, missingness, and interpretation are explicit. A polished graph must not make a sparse or delayed sample look continuous.

## Liquid Glass with consent clarity

Liquid Glass can group study status, sensor cards, and review actions while preserving a sober tone:

- high-contrast study title and purpose;
- separate sensor rows;
- a glass status container for current recording/fetch state;
- a visible delay badge such as “Available after holding period”;
- a plain privacy link and Settings handoff;
- no animated “brain” or “health score” that implies a medical result.

If Reduce Motion or increased contrast is enabled, the content hierarchy must stay identical. Do not make the glass tint communicate consent or risk by itself.

## AI review and non-diagnostic language

An on-device AI summary should show:

- the exact sensor/time window used;
- source-device and missingness status;
- that the text is generated;
- confidence or uncertainty in plain language;
- a correction or dismiss action;
- the study’s non-diagnostic boundary.

Avoid “your brain is…,” “you are depressed,” “you slept badly,” or “your focus is proven” from a SensorKit-derived model unless a separate validated clinical/research claim is authorized. Prefer “the model found a pattern in the available samples; this is not a diagnosis.”

## Accessibility, language, and participant control

Make consent and review tasks complete with VoiceOver, Dynamic Type, Voice Control, Switch Control, keyboard, and reduced motion:

- expose sensor name, purpose, state, required/optional flag, and consequence;
- avoid abbreviations that hide data sensitivity;
- announce delayed availability and deletion gaps in text;
- provide accessible labels for charts and exact data tables;
- support long privacy-policy and sponsor strings;
- keep withdrawal, support, Settings, and delete/export actions visible;
- ensure a participant can revisit a denied sensor without a coercive loop.

Localization must preserve whether a sensor is required, optional, pending, deleted, or merely unavailable. Do not translate research uncertainty into a confident verb.

## Data minimization and retention

Design the app to display the smallest useful representation:

- do not put raw face, speech, keyboard, Messages, or phone-usage data in a hero dashboard;
- separate participant-facing summaries from research export records;
- show what leaves the device and when;
- make cache/export deletion distinct from Settings authorization;
- avoid identifiers in analytics and screenshots;
- record sensor provenance with pseudonymous study IDs.

The interface should make it possible to participate partially. A study that cannot operate without a denied optional sensor should say so rather than silently substitute another signal.

## Proof-oriented handoff

The design handoff should name:

- approved study and sensor list;
- entitlement values and target;
- Info.plist purpose/privacy/usage-detail copy;
- authorization states and Settings route;
- recording/pause/stop behavior;
- 24-hour pending state;
- deletion-gap presentation;
- AI no-data/non-diagnostic fallback;
- VoiceOver, Dynamic Type, reduced motion, localization, physical-device, and release fixtures.

## Sources

- [SensorKit](https://developer.apple.com/documentation/sensorkit)
- [Configuring your project for sensor reading](https://developer.apple.com/documentation/sensorkit/configuring-your-project-for-sensor-reading)
- [SRAuthorizationStatus](https://developer.apple.com/documentation/sensorkit/srauthorizationstatus)
- [SRFetchRequest](https://developer.apple.com/documentation/sensorkit/srfetchrequest)
- [SRDeletionRecord](https://developer.apple.com/documentation/sensorkit/srdeletionrecord)
- [NSSensorKitUsageDetail](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitusagedetail)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
