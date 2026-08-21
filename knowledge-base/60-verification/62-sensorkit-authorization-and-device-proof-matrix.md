# SensorKit authorization and device proof matrix

SensorKit proof must establish an approved study, signed entitlement, granular consent, actual recording, delayed availability, typed data, deletion behavior, and research-safe interpretation. A simulator or reader object is not sufficient.

| Claim | Evidence | Failure fixture / boundary |
| --- | --- | --- |
| The study is eligible | Apple approval record, exact sensor list, target bundle ID, and distribution/entitlement record | SDK symbol or local entitlement file without approval |
| The signed app has the right entitlement | Built app signature contains `com.apple.developer.sensorkit.reader.allow` with only approved sensor values | Missing, extra, or development-only sensor entry |
| Study copy matches data use | `NSSensorKitUsageDescription`, privacy URL, and per-sensor usage detail inspected in the built Info.plist | Vague copy, missing policy, or sensor list not explained |
| Permission is granular | System sheet shows the approved study and each sensor’s required/optional choice; later Settings change is observed | App-owned fake prompt, all-sensor assumption, or denial ignored |
| Authorization state is modeled | Authorized, denied, and not-determined states produce distinct UI and behavior | Permission state inferred from reader construction |
| The current reader route is real | `SRReader<Sensor>` compiles in the selected SDK or deprecated `SRSensorReader` adapter is isolated and labeled | Beta API treated as stable or legacy callbacks mixed with async route |
| Recording begins only when allowed | Authorized physical reader starts and produces a recorded-state observation | Start called while denied, entitlement error hidden, or no device |
| Recording stops safely | Stop/pause/withdrawal path completes or surfaces an error and preserves last known state | UI says stopped while reader continues or error is swallowed |
| Device topology is known | `devices`/`fetchDevices` identifies the actual iPhone/Watch source and OS build | Paired Watch assumed, wrong source, or device absent |
| Holding period is honored | A range overlapping the 24-hour holding period returns no results and the UI says pending availability | Empty range treated as zero or data loss |
| Eligible fetch is scoped | `SRFetchRequest` uses the intended device/time range and returns only approved recorded data | Wrong range, wrong source, or unbounded export |
| Sample errors are visible | Each `SRFetchResponse.sample` success/failure is counted and retained as a redacted quality event | One decode error marks the entire window valid |
| Deletion is represented | `SRDeletionRecord` or legacy deletion record fixture produces a visible gap and stored reason | Missing samples imputed without study protocol |
| AI uses approved evidence | Features include sensor identity, time range, source, coverage, and deletion state; model output is non-diagnostic/reviewable | Model fills gaps, claims diagnosis, or runs on unauthorized data |
| Data minimization works | Raw sensitive samples stay within approved boundary; logs, screenshots, analytics, and exports are redacted | Speech, face, keyboard, Messages, phone-usage, or location data leaks |
| Participant can withdraw/recover | Settings handoff, support, retention, export/delete, and partial-study states are tested | Coercive retry loop or irreversible-looking permission UI |
| Accessibility works | VoiceOver, Dynamic Type, high contrast, Reduce Motion, Voice Control, and Switch Control complete consent/status/review tasks | Color-only consent state or unreadable sensor purpose |
| Physical release proof exists | Signed device/test build and archive distribution artifacts name device, OS, entitlements, and study version | Simulator/preview/Debug run treated as research evidence |

## Fixture set

- entitlement matches approved sensor list;
- entitlement missing or extra sensor;
- missing purpose, privacy URL, or usage detail;
- every authorization state per sensor;
- required sensor denied versus optional sensor denied;
- no iPhone/Watch source device;
- recording start and stop success/failure;
- range within the 24-hour holding period;
- range after the holding period with samples;
- empty eligible range;
- per-sample decode error;
- deletion record with start/end and reason;
- paired-device source change;
- AI low coverage, no model, non-diagnostic output;
- participant withdrawal and Settings change;
- long localized purpose, large text, VoiceOver, reduced motion, and offline states.

## Evidence ladder

1. Study/configuration and Info.plist tests.
2. Signed entitlement inspection.
3. Reader/authorization/recording unit and adapter tests.
4. Holding-period, fetch-window, sample-error, and deletion fixtures.
5. Physical iPhone/paired Watch run with approved study build.
6. Participant accessibility/privacy task evidence.
7. AI analysis review and export/retention evidence.
8. Archive, signing, and distribution review.

Record the sensor, study version, entitlement hash or artifact reference, device model, OS build, paired-device state, request range, sample/deletion counts, and model version. A sensor value is evidence of a recorded datum in a constrained study window, not a diagnosis or general health claim.

## Sources

- [SensorKit](https://developer.apple.com/documentation/sensorkit)
- [Configuring your project for sensor reading](https://developer.apple.com/documentation/sensorkit/configuring-your-project-for-sensor-reading)
- [SRReader](https://developer.apple.com/documentation/sensorkit/srreader)
- [SRDataSensor](https://developer.apple.com/documentation/sensorkit/srdatasensor)
- [SRFetchRequest](https://developer.apple.com/documentation/sensorkit/srfetchrequest)
- [SRFetchResponse](https://developer.apple.com/documentation/sensorkit/srfetchresponse)
- [SRAuthorizationStatus](https://developer.apple.com/documentation/sensorkit/srauthorizationstatus)
- [SRDeletionRecord](https://developer.apple.com/documentation/sensorkit/srdeletionrecord)
- [NSSensorKitUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitusagedescription)
- [NSSensorKitPrivacyPolicyURL](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitprivacypolicyurl)
- [NSSensorKitUsageDetail](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitusagedetail)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
