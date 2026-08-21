# SensorKit research-data capability route

Use this route only for an approved SensorKit research study with the exact Apple entitlement, study metadata, and user authorization. Keep the study protocol, system permission, reader lifecycle, device/source, holding period, deletion gaps, analysis, and export as separate layers.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | Participate in an approved research study using selected iPhone/Apple Watch sensor data |
| Approval | Apple-approved research study and `com.apple.developer.sensorkit.reader.allow` entitlement |
| Metadata | `NSSensorKitUsageDescription`, `NSSensorKitPrivacyPolicyURL`, and `NSSensorKitUsageDetail` |
| Reader | Current typed `SRReader<Sensor>` route where available; deprecated `SRSensorReader` compatibility route only when required |
| Consent | Granular user authorization per approved sensor, adjustable in Settings |
| Recording | Explicit start/stop lifecycle after authorization |
| Fetch | `SRFetchRequest` time/device window; current async sequences or legacy delegate callbacks |
| Delay | 24-hour holding period before newly recorded data is accessible |
| Integrity | `SRFetchResponse` sample errors, source device, timestamp, and deletion records |
| AI | Optional on-device quality check, feature analysis, or non-diagnostic summary |
| UI | Native participant consent/status/review surface; Liquid Glass only as a clear grouping treatment |
| Proof | Approved entitlement, signed physical iPhone/Watch, permission, holding-period, typed fetch, deletion, accessibility, privacy, and release evidence |

## 1. Stop if the study gate is missing

Do not scaffold a production claim until all of these are known:

- study purpose and sponsor;
- exact sensors requested;
- required versus optional sensors;
- Apple approval and entitlement path;
- target platform and device coverage;
- study privacy policy and retention;
- whether data stays on device or leaves it;
- participant withdrawal and support;
- research/medical claim review.

An unsigned entitlement file or an SDK symbol is not study approval.

## 2. Configure the target

Create the explicit App ID and manual provisioning profile required by the SensorKit setup guide. Add only the approved sensor values to `com.apple.developer.sensorkit.reader.allow`. Add the research-purpose, privacy-policy, and per-sensor usage-detail keys to the target’s Info.plist.

Validate the signed product, not just the source file:

1. inspect the built app’s entitlements;
2. inspect the Info.plist values;
3. compare sensor entries with the approved study;
4. install on the intended physical iPhone/Watch environment;
5. record the system sheet and Settings status.

## 3. Select the reader generation

For a current SDK target:

~~~swift
import SensorKit

let reader = try SRReader(sensor: SRPedometerDataSensor.pedometerData)
~~~

The current generic API is documented as beta and uses `SRDataSensor` associated sample types. Confirm the sensor type and initializer in the target SDK.

For a compatibility target, the older `SRSensorReader(sensor:)` and delegate route is documented but deprecated. Keep the compatibility adapter isolated so the rest of the study domain does not depend on deprecated callbacks.

## 4. Model granular authorization

Track one authorization state per sensor:

- `notDetermined`: do not start recording; prepare the approved system request;
- `authorized`: recording/fetch may be available subject to the reader and study;
- `denied`: do not retry in a loop; direct the participant to Settings/support;
- entitlement/configuration failure: fix the signed study target, not the UI copy.

The user’s choice is not the same as the study’s required flag. An optional denied sensor can produce a partial study; a required denied sensor may make the study ineligible.

## 5. Record only while the study needs it

The lifecycle is:

authorization -> startRecording -> active recording -> pause/stop policy -> holding period -> eligible fetch -> local review/export

Avoid recording every sensor continuously. State the purpose and expected battery/data impact. Stop when the participant pauses or withdraws according to the approved protocol. If a reader fails to start or stop, preserve the last known state and expose recovery rather than claiming data continuity.

## 6. Fetch by device and time range

Create an `SRFetchRequest` with the intended `SRDevice`, `from`, and `to` values. The result is constrained to data the app recorded for that device and time window. The 24-hour holding period means a just-finished window can correctly yield no data.

Current typed route:

~~~swift
var request = SRFetchRequest()
request.from = startTime
request.to = endTime

for try await response in reader.samples(matching: request) {
    switch response.sample {
    case .success(let sample):
        // Store only the approved, typed research representation.
        _ = sample
    case .failure(let error):
        // Record a redacted data-quality event.
        _ = error
    }
}
~~~

The exact sensor sample type and current request construction are SDK-sensitive. Do not use a sample loop as proof that every expected interval exists.

## 7. Reconcile deletion records

Fetch deletion records for the same study window when the current API and approved sensor support it. A deletion record names a time range and reason. Persist the gap as a gap; do not fill it with zeros or model predictions without a study-approved imputation protocol.

When a participant asks why a graph is incomplete, show the deletion/pending/denied distinction. Do not reveal more sensitive context than the study permits.

## 8. AI analysis boundary

The safe local route is:

approved sample window -> quality/deletion validation -> typed features -> local model -> confidence/coverage check -> participant/researcher review -> approved export

The model must know which sensors and time ranges were actually present. It should return “insufficient data” for a held, deleted, unauthorized, or out-of-range sample. Keep generated summaries non-diagnostic unless a separately approved research workflow supports stronger language.

## 9. Native participant surface

Use SwiftUI for study status, sensor authorization, recording state, pending availability, source device, deletion gaps, and review. Use semantic controls and clear copy. Liquid Glass can group the state cards but should not make sensitive collection feel like a game or hide the system permission boundary.

## 10. Failure states

Handle:

- missing Apple approval or entitlement;
- target sensor not in the signed entitlement;
- missing usage description/privacy URL/usage detail;
- not determined, denied, or revoked authorization;
- no compatible physical sensor/device;
- recording start/stop failure;
- 24-hour pending range;
- empty/partial fetch;
- per-sample decoding failure;
- deletion record;
- model unavailable/low coverage;
- export or retention policy refusal;
- participant withdrawal/support request.

## 11. Minimum evidence bundle

- approved study/entitlement record;
- target Info.plist and signed entitlements;
- permission sheet and Settings evidence;
- per-sensor recording state;
- physical iPhone and paired Watch identity;
- holding-period empty fetch and eligible fetch;
- typed sample and deletion-gap fixtures;
- non-diagnostic AI fallback;
- accessibility/localization/privacy review;
- archive and distribution evidence.

## Sources

- [SensorKit](https://developer.apple.com/documentation/sensorkit)
- [Configuring your project for sensor reading](https://developer.apple.com/documentation/sensorkit/configuring-your-project-for-sensor-reading)
- [SRReader](https://developer.apple.com/documentation/sensorkit/srreader)
- [SRDataSensor](https://developer.apple.com/documentation/sensorkit/srdatasensor)
- [SRFetchRequest](https://developer.apple.com/documentation/sensorkit/srfetchrequest)
- [SRFetchResponse](https://developer.apple.com/documentation/sensorkit/srfetchresponse)
- [SRDeletionRecord](https://developer.apple.com/documentation/sensorkit/srdeletionrecord)
- [SRAuthorizationStatus](https://developer.apple.com/documentation/sensorkit/srauthorizationstatus)
- [SensorKit reader entitlement configuration](https://developer.apple.com/documentation/sensorkit/configuring-your-project-for-sensor-reading)
- [NSSensorKitUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitusagedescription)
- [NSSensorKitPrivacyPolicyURL](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitprivacypolicyurl)
- [NSSensorKitUsageDetail](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitusagedetail)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
