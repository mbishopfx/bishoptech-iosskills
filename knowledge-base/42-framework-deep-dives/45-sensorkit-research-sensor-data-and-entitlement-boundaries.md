# SensorKit: research-only sensor data, authorization, and deletion boundaries

SensorKit is a high-sensitivity, research-study framework for accessing selected raw sensor data and system-derived metrics from an iPhone or paired Apple Watch. It is not a general sensor picker, a consumer health database, a medical diagnostic API, or a shortcut around Apple’s study approval and entitlement process.

The route is:

approved study -> explicit entitlement and Info.plist purpose -> granular user authorization -> active sensor recording -> holding period -> typed fetch -> deletion-gap interpretation -> privacy-safe local analysis

Keep study purpose, entitlement, authorization, recording ownership, device/source, sensor samples, deletion records, AI output, and research conclusions as separate facts.

## 1. Availability and approval come first

Apple’s SensorKit setup documentation says that an app must be an approved research-study app and receive the sensor-reader entitlement before it can read SensorKit data. The required code-signing entitlement is `com.apple.developer.sensorkit.reader.allow`, with entries for the approved sensors. Apple’s setup path also calls for an explicit App ID, a manual provisioning profile, and matching code-signing configuration.

This is a product and distribution gate, not a runtime permission that any developer can request from a normal app. Do not promise users that a new app can read Messages usage, phone usage, speech metrics, face metrics, ECG, PPG, visits, or other SensorKit data merely because the symbols appear in the SDK.

SensorKit also documents platform limits: calls from Mac Catalyst apps and compatible iPhone/iPad apps running in visionOS are ignored. Verify the actual iOS device, paired Apple Watch, OS build, approved sensor list, and signed entitlements.

## 2. Current and legacy API surfaces

The current SDK documentation introduces a Swift generic `SRReader<Sensor>` where `Sensor` conforms to `SRDataSensor`. The current route provides:

- `init(sensor:)` for a typed reader;
- `authorizationStatus`;
- `devices`;
- `startRecording()` and `stopRecording()` async methods;
- `samples(matching:)` as an asynchronous sequence of typed `SRFetchResponse` values;
- `deletionRecords(matching:)` as an asynchronous sequence for deletion gaps.

Apple marks the current `SRReader`, `SRDataSensor`, and related generic types as beta in the current documentation. Treat them as SDK-version-sensitive and verify final availability before shipping.

The older `SRSensorReader` delegate API remains documented but is marked deprecated in current docs. It uses `requestAuthorization`, `startRecording`, `stopRecording`, `fetch`, `fetchDevices`, `SRSensorReaderDelegate`, and class-based sample types. Use it only for a target that still requires the compatibility surface, and do not mix its callback lifecycle with the generic async route without an explicit adapter.

## 3. Configure the study contract

SensorKit’s system request sheet uses project metadata to explain the study:

- `NSSensorKitUsageDescription`: short research purpose;
- `NSSensorKitPrivacyPolicyURL`: privacy policy link;
- `NSSensorKitUsageDetail`: per-sensor dictionaries explaining why each sensor is needed;
- a `Required` value for a sensor when the study cannot proceed without it;
- the approved sensor list in the code-signing entitlement.

The system presents purpose and sensor-specific explanations before the user decides. Keep the copy aligned with the approved research protocol. Do not describe a sensor as “helping focus,” “detecting depression,” “proving fatigue,” or “measuring truth” unless the authorized study and appropriate evidence support that claim.

Users can approve sensors individually, participate partially when optional sensors are denied, and later change authorization in Settings under Privacy and the Research Sensor & Usage Data surface. Model each sensor’s state independently.

## 4. Sensor selection and device topology

SensorKit exposes many sensor families, including motion, ambient light, device/app usage, visits, wrist state/temperature, speech metrics, media events, ECG/PPG, and other study-restricted data. The set available to a particular target is not the same as the set that is approved, authorized, recorded, or present on a device.

For each reader, track:

- requested sensor;
- entitlement entry;
- usage-detail copy;
- current authorization status;
- whether recording is active;
- available source devices;
- device model and OS build;
- time range and holding-period boundary;
- sample/deletion-record availability;
- local analysis and retention policy.

Paired Apple Watch data is a separate source dimension. A device list or successful reader initialization does not prove that a Watch is paired, that the sensor exists, or that the requested time range has samples.

## 5. Recording ownership and lifecycle

An authorized reader can start recording. The legacy documentation describes recording as shared among multiple readers and system processes; the sensor remains active while there are stakeholders, and stopping releases the app’s stake. The current `SRReader` route exposes async `startRecording()` and `stopRecording()` operations that can throw.

Treat recording as a resource:

1. confirm entitlement and authorization;
2. start only when the study actually needs recording;
3. record the start result and source devices;
4. stop on study pause, consent withdrawal, or lifecycle policy;
5. make restart and error states explicit;
6. never infer “no sample” as “sensor measured zero.”

Do not start all sensors at app launch. Keep a study sensor plan with explicit user consent, battery/thermal expectations, and a stop policy.

## 6. Fetch windows and the 24-hour holding period

`SRFetchRequest` defines a device and a time window. A fetch can return only data the app recorded, and only data that remains available for that device and time range. SensorKit places a 24-hour holding period on newly recorded data before an app can access it, giving the user an opportunity to delete data they do not want to share. A request whose range overlaps that holding period returns no results.

Design the study around delayed availability:

- show “recording” and “available for research” as different states;
- do not poll continuously for data inside the holding period;
- communicate when a study day becomes eligible for fetch;
- keep the requested date range and device in the research record;
- test empty results as a normal privacy-preserving outcome.

The holding period is not a streaming buffer. SensorKit is not the right route for a consumer feature that needs immediate motion, audio, heart-rate, or location feedback.

## 7. Typed fetch and deletion records

The current async route yields `SRFetchResponse<Sample>` values. Each response can carry a successful sample or a decoding error, a source device, and a timestamp. The app must handle per-sample failures without treating the entire day as complete.

`SRReader.deletionRecords(matching:)` surfaces `SRDeletionRecord` values describing time ranges and reasons for data gaps. Deletion records are important evidence:

- a missing sample may be an intentional system deletion;
- the user may have removed data during the holding period;
- a source device may have changed or stopped recording;
- the dataset may be partial by design.

Never impute a zero, interpolate a medical metric, or claim continuous coverage without recording the gap reason and study policy.

## 8. AI and research interpretation boundary

On-device AI can help with approved, local research workflows:

- summarize a day of authorized samples for user review;
- detect data-quality gaps before export;
- cluster a typed sensor feature vector;
- flag missing device/source metadata;
- draft a non-diagnostic participant explanation;
- validate that an analysis used the approved sensor and time window.

The model is not the study protocol, a clinical instrument, a diagnosis, or consent. Keep raw samples, derived features, model outputs, human review, and research conclusions separate. Default to “insufficient data” when samples are missing, deleted, outside the approved sensor list, or below the model’s evaluation envelope.

Do not send SensorKit data to a server or model provider merely because a model could improve the result. The study’s consent, privacy policy, entitlement, retention plan, and review protocol must cover the data flow. On-device processing can reduce exposure but does not erase the need for consent or research governance.

## 9. Native and Liquid Glass participant surfaces

The containing app can use SwiftUI for a participant-facing study status surface:

- approved sensor list and purpose;
- each sensor’s authorized/denied/not-determined state;
- recording active/paused/stopped;
- data holding-period status;
- last eligible fetch and source device;
- deletion gaps and what they mean;
- local model availability and non-diagnostic wording;
- export/delete/support actions allowed by the study.

Liquid Glass can group status and review controls, but it must not turn sensitive sensor collection into a playful dashboard that hides consent or uncertainty. Keep raw sensor values out of decorative hero cards. Provide accessible text, Dynamic Type, Reduce Motion, clear data-retention language, and an obvious way to revisit Settings.

## 10. Verification boundary

Prove the route in layers:

- approved study and exact entitlement;
- Info.plist purpose/privacy/usage-detail configuration;
- granular permission sheet and partial-consent behavior;
- current or legacy reader compile in the named target;
- recording start/stop and error lifecycle;
- paired-device discovery and source identity;
- 24-hour holding-period empty range;
- eligible fetch with typed sample responses;
- deletion records and missing-data policy;
- AI no-data/low-confidence/non-diagnostic fallback;
- participant accessibility and privacy tasks;
- signed physical iPhone/Apple Watch evidence and release review.

An SDK symbol, entitlements file, authorization prompt, reader object, simulated sample, or local model output does not prove approved study access, sensor availability, data completeness, scientific validity, or release readiness.

## Sources

- [SensorKit](https://developer.apple.com/documentation/sensorkit)
- [Configuring your project for sensor reading](https://developer.apple.com/documentation/sensorkit/configuring-your-project-for-sensor-reading)
- [SRReader](https://developer.apple.com/documentation/sensorkit/srreader)
- [SRDataSensor](https://developer.apple.com/documentation/sensorkit/srdatasensor)
- [SRFetchRequest](https://developer.apple.com/documentation/sensorkit/srfetchrequest)
- [SRFetchResponse](https://developer.apple.com/documentation/sensorkit/srfetchresponse)
- [SRSensorReader](https://developer.apple.com/documentation/sensorkit/srsensorreader)
- [SRSensorReaderDelegate](https://developer.apple.com/documentation/sensorkit/srsensorreaderdelegate)
- [SRAuthorizationStatus](https://developer.apple.com/documentation/sensorkit/srauthorizationstatus)
- [SRDeletionRecord](https://developer.apple.com/documentation/sensorkit/srdeletionrecord)
- [NSSensorKitUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitusagedescription)
- [NSSensorKitPrivacyPolicyURL](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitprivacypolicyurl)
- [NSSensorKitUsageDetail](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitusagedetail)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
