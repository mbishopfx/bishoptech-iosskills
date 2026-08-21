# SwiftUI Core Motion sensor-route proof matrix

Use this matrix to separate deterministic signal policy from physical hardware, accessory, privacy, energy, accessibility, AI, and release evidence.

## Proof matrix

| Claim | Source/compile check | Simulator or fixture | Physical/device proof | Release evidence | Failure boundary |
| --- | --- | --- | --- | --- | --- |
| Motion privacy configuration is correct | Inspect built `Info.plist` for `NSMotionUsageDescription` and purpose-first text. | Missing/legacy-key configuration fixture. | Trigger the selected service on a clean device and record the prompt/result. | Archive/TestFlight built-target inspection. | A source plist line does not prove the shipped app prompt or runtime behavior. |
| Device motion hardware is available | Compile and inspect `CMMotionManager` availability properties. | Availability reducer fixtures. | Test each target device and record sensor availability. | Device matrix attached to archive/TestFlight build. | Available hardware is not authorization or accuracy proof. |
| One CMMotionManager is owned | Compile one coordinator/service owner and lifecycle state. | Inject duplicate-start/stop/session-generation fixtures. | Navigate between screens and verify no competing managers or duplicate streams. | TestFlight cold/warm navigation run. | A singleton name alone does not prove correct lifetime or teardown. |
| Accelerometer/gyro/magnetometer route works | Compile start/stop methods, intervals, handler queue or latest-value poll. | Synthetic samples, queue delay, dropped-frame, cancellation fixtures. | Physical movement across each axis; record timestamps and actual cadence. | Signed build on device matrix. | A callback or `is*Active` flag does not prove correct axis interpretation or usable data. |
| Device-motion reference frame is correct | Compile available-frame query and selected frame branch. | Frame unavailable/alternate-frame fixtures. | Recenter and rotate device in portrait/landscape/face-up/down; compare expected attitude. | Archive with target SDK and frame policy. | Euler/quaternion/matrix output without frame provenance is ambiguous. |
| Timestamp/cadence policy is correct | Compile sample timestamp capture and interval statistics. | Jitter, capped interval, late sample, and out-of-order fixtures. | Measure actual callback/poll intervals under device load. | Performance/energy result attached to release record. | Requested interval is not proof of delivered cadence. |
| Motion activity route is honest | Compile `CMMotionActivityManager` availability/status/live/query paths. | Overlapping flags, all-false, unknown, confidence, stale, and history fixtures. | Walk/run/vehicle/stationary transitions with timestamps. | TestFlight physical run. | A single enum label or low-confidence result is not physical activity truth. |
| Pedometer availability is scoped | Compile metric-specific availability and authorization handling. | Steps-only, distance-unavailable, floor-unavailable fixtures. | Verify steps/distance/floors/pace/cadence on a device that supports each. | Device/account matrix. | One available metric does not prove all metrics are available. |
| Pedometer live cumulative semantics are correct | Compile start date, handler projection, stop, and generation. | Start-date/cumulative/late callback fixtures. | Start at a known time, walk, suspend/resume, compare cumulative start/end to system data. | TestFlight physical run. | A single step count lacks window and freshness semantics. |
| Pedometer historical boundary is correct | Compile bounded query and error handling. | Before/within/after seven-day window fixtures. | Query a real device and compare with the documented available window. | Release build retest. | A historical array is not an all-time history. |
| Altimeter route is correct | Compile relative/absolute availability and matching start/stop methods. | Unsupported/unchanged-event/baseline/pressure fixtures. | Test relative elevation change and absolute route on supported hardware; record baseline and units. | Physical device matrix/TestFlight. | A periodic event or pressure value is not proof of elevation change. |
| Headphone motion route is correct | Compile availability, connection status, start/stop, delegate, and pose projection. | Disconnected/reconnected/stale-pose fixtures. | Use supported headphones, rotate/recenter, remove/reconnect, and verify fallback. | Signed physical accessory evidence. | Cached `CMDeviceMotion` after disconnect is not live pose. |
| Queue/backpressure policy holds | Compile dedicated queue/actor, ring-buffer bounds, and drop counters. | Slow handler, burst, cancellation, and memory-bound fixtures. | Run under load; measure queue latency, drop policy, thermal and battery impact. | Performance/energy report with archive. | No crash does not prove bounded latency or energy safety. |
| Teardown works | Compile matching stop methods and task cancellation. | Start/stop/restart/generation fixtures. | Leave/reenter view, background/foreground, lock/unlock, and stop a session. | TestFlight cold/warm lifecycle run. | A stopped Boolean is not proof no callbacks or retained work remain. |
| SwiftUI status is honest | Compile separate unsupported/permission/ready/calibrating/live/stale/disconnected states. | Preview matrix and reducer tests. | Complete the task on device with permission changes and stale conditions. | TestFlight screenshots/recording. | A live chart or green indicator alone is not proof of freshness. |
| Liquid Glass adapts | Compile target-available glass and standard fallback. | Reduce Transparency/Increase Contrast/Reduce Motion previews. | Test glass and fallback on target device/iPad layouts. | Archive minimum OS/device matrix. | A glass screenshot proves only one appearance state. |
| Accessibility task works | Compile semantic labels, values, actions, identifiers. | Dynamic Type/VoiceOver/reduced-effects fixture matrix. | VoiceOver start/stop/value/fallback, Switch Control, keyboard/pointer, RTL/localized units. | TestFlight accessibility pass. | An audit or label string is not task-completion proof. |
| AI summary is bounded | Compile typed schema, model availability, range/provenance validation, cancellation, fallback. | Invalid feature window, stale revision, unavailable/refusal, and unsupported output fixtures. | Run with model available/unavailable and compare summary to deterministic features. | TestFlight model/device matrix. | A plausible sentence or local-model claim is not proof of correct signal interpretation. |
| Privacy minimization holds | Audit raw sample retention, analytics, logs, prompts, and accessory identifiers. | Synthetic feature windows only. | Inspect device data and exercise pause/delete/deny flows. | Release privacy review. | On-device processing does not excuse unnecessary retention. |
| Release route works | Inspect bundle, SDK, deployment target, privacy strings, and linked frameworks. | N/A. | Signed archive/TestFlight install and full sensor/accessory task. | Archive export, TestFlight build, device/accessory matrix. | A debug run, simulator trace, or archive alone is not physical/release proof. |

## Fixture catalog

### Availability and privacy

- each `CMMotionManager` sensor unavailable/available/active/inactive;
- no `NSMotionUsageDescription`, purpose copy, not determined, authorized, denied, and restricted;
- device motion frame available versus unavailable;
- activity/pedometer/altimeter authorization and availability states; and
- headphone motion available, disconnected, reconnecting, and unsupported accessory.

### Timing and sensor data

- requested interval versus capped actual timestamp interval;
- slow handler, queue backlog, dropped sample, ring-buffer maximum, and cancellation;
- gravity plus user acceleration separation;
- frame/axis transforms across device orientations;
- overlapping activity flags, unknown/all-false, confidence, and start date;
- pedometer cumulative live window, seven-day history boundary, and metric-specific absence;
- relative altitude baseline, unchanged events, pressure units, and absolute availability; and
- stale headphone pose after disconnect.

### UI and AI

- unsupported, permission, ready, calibrating, live, stale, low-confidence, disconnected, and reduced-effects previews;
- Dynamic Type, VoiceOver, Switch Control, keyboard/pointer, RTL, and localized units;
- valid feature window and typed summary;
- invalid/out-of-range/stale feature window;
- model unavailable/refusal/error; and
- deterministic manual fallback with no sensor side effect.

## Evidence naming

```text
core-motion-device-motion-frame-iphone26-2026-08-20.json
core-motion-pedometer-seven-day-boundary-iphone26-2026-08-20.json
core-motion-altimeter-relative-baseline-iphone26-2026-08-20.mp4
core-motion-headphone-disconnect-fallback-airpods-2026-08-20.mp4
core-motion-queue-energy-teardown-<build>.json
core-motion-ai-summary-invalid-fallback-<model-state>.json
```

Redact raw sensor windows, timestamps that reveal routines, accessory identifiers, account information, and private health-adjacent data before sharing evidence.

## Sources

- [Core Motion](https://developer.apple.com/documentation/coremotion/)
- [CMMotionManager](https://developer.apple.com/documentation/coremotion/cmmotionmanager)
- [CMDeviceMotion](https://developer.apple.com/documentation/coremotion/cmdevicemotion)
- [CMAttitude](https://developer.apple.com/documentation/coremotion/cmattitude)
- [CMAttitudeReferenceFrame](https://developer.apple.com/documentation/coremotion/cmattitudereferenceframe)
- [CMMotionActivityManager](https://developer.apple.com/documentation/coremotion/cmmotionactivitymanager)
- [CMMotionActivity](https://developer.apple.com/documentation/coremotion/cmmotionactivity)
- [CMAuthorizationStatus](https://developer.apple.com/documentation/coremotion/cmauthorizationstatus)
- [CMPedometer](https://developer.apple.com/documentation/coremotion/cmpedometer)
- [CMPedometerData](https://developer.apple.com/documentation/coremotion/cmpedometerdata)
- [CMAltimeter](https://developer.apple.com/documentation/coremotion/cmaltimeter)
- [CMAltitudeData](https://developer.apple.com/documentation/coremotion/cmaltitudedata)
- [CMHeadphoneMotionManager](https://developer.apple.com/documentation/coremotion/cmheadphonemotionmanager)
- [NSMotionUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nsmotionusagedescription)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
