# SwiftUI Core Motion sensor-route review

Core Motion is a family of sensor and activity services, not one interchangeable stream. The correct route depends on whether the product needs instantaneous device motion, fused attitude, recognized activity, historical steps, relative altitude, or motion from supported headphones.

The reliable mental model is:

```text
user outcome
    -> sensor family and availability gate
    -> authorization / privacy purpose
    -> one owned service and intentional sampling policy
    -> timestamped, bounded observation
    -> app-owned projection or optional typed AI summary
    -> stop / teardown / fallback
```

A motion sample, `is*Active` Boolean, simulator trace, activity classification, pedometer count, altitude event, or headphone pose is not proof of physical accuracy or a completed user workflow. Motion data is a measurement with hardware, coordinate-frame, timestamp, calibration, authorization, energy, and privacy boundaries.

This review is for iOS 26-targeted native apps. Recipes remain compile-oriented sketches until they are checked against the final SDK and exercised on the named physical device, sensor, and accessory.

## Choose one sensor lane first

| Product need | Core Motion route | Important boundary |
| --- | --- | --- |
| Tilt, shake, orientation, or high-rate controller input | `CMMotionManager` accelerometer, gyroscope, or device motion | Check the individual hardware service, choose an available attitude reference frame, use timestamps, and stop updates when the interaction ends. |
| Fused attitude and gravity/user acceleration | `CMMotionManager` device motion -> `CMDeviceMotion`/`CMAttitude` | The attitude is relative to a selected reference frame; Euler angles, quaternions, and matrices are representations of the same estimate, not independent truth. |
| Walking, running, cycling, automotive, stationary, or unknown state | `CMMotionActivityManager` | Activity flags can overlap and can all be false for movement that does not match the recognized categories; use confidence and timestamps. |
| Steps, distance, floors, pace, or cadence | `CMPedometer` | Check metric-specific availability; live values are cumulative from the requested start; historical queries have a bounded system cache. |
| Elevation change or absolute altitude | `CMAltimeter` | Check relative and absolute availability separately; altitude events can arrive at regular intervals even when values do not change. |
| Head pose from supported AirPods/headphones | `CMHeadphoneMotionManager` | Check device motion and connection availability; handle accessory removal and use the headphone coordinate axes correctly. |
| Long-term health/fitness record | HealthKit or WorkoutKit, with Core Motion only as an input/measurement route | Do not turn a raw motion stream into a health claim or a HealthKit record without the separate privacy, authorization, unit, and domain contract. |
| Tactile feedback | Core Haptics or SwiftUI `sensoryFeedback` | Haptics are an output route; they do not validate sensor accuracy or replace visual/accessibility feedback. |

Do not start every service because the device supports it. Start the smallest sensor family that answers the user’s question, and record the reason for the sampling policy.

## Hardware and authorization are separate gates

Core Motion services can be unavailable because the device lacks the sensor, the accessory is not connected, the service is unsupported on the target, or the person denied motion access. Keep those states distinct:

| State | Meaning | UI behavior |
| --- | --- | --- |
| Unsupported | The target hardware or OS does not provide the service. | Explain the alternate route; do not present a retry loop. |
| Available but inactive | The service can run but is not currently owned by the feature. | Show an intentional Start action. |
| Authorized | The system permits the selected service. | Start only after product state requests it. |
| Not determined | The app has not asked for the protected motion access. | Explain the purpose before the first call that prompts. |
| Denied/restricted | The service cannot provide the requested data. | Keep the feature usable with manual, visual, or non-motion fallback. |
| Accessory disconnected | Headphone motion is no longer available. | Stop accessory updates and return to a non-headphone route. |
| Active but stale | A handler is running or a value exists, but timestamps are old. | Mark data stale and stop treating it as current motion. |

Add `NSMotionUsageDescription` with a specific user-facing purpose. Apple’s current documentation explicitly calls out this key for motion activity, pedometer, altimeter, headphone motion, sensor recording, and related motion services, and warns of a runtime failure when the required key is absent. Verify the final target’s privacy configuration for every service actually used.

Hardware availability is not permission. `isGyroAvailable` or `CMPedometer.isStepCountingAvailable()` says that a capability exists; it does not say that the person granted access or that the current sample is valid.

## CMMotionManager ownership and service selection

Apple’s `CMMotionManager` guidance says to create only one `CMMotionManager` object for the app because multiple instances can affect the rate at which the system receives accelerometer and gyroscope data. Give that manager a clear owner—usually a feature coordinator or sensor actor—and let multiple screens observe an app-owned projection rather than creating competing managers.

The manager covers four primary data families:

- accelerometer data: instantaneous acceleration in the device’s three-dimensional space;
- gyroscope data: instantaneous rotation around the device’s primary axes;
- magnetometer data: magnetic-field orientation relative to Earth; and
- device-motion data: fused attitude, rotation rate, gravity, user acceleration, and calibrated magnetic-field measurements.

Choose between two delivery styles:

| Need | Delivery style |
| --- | --- |
| Game/render loop or a UI that only needs the latest sample | Start updates without a handler and periodically read the manager’s latest data properties. Apple documents this as a useful pattern for games because it avoids per-sample handler overhead. |
| Every sample matters for a bounded analysis window | Start updates to a dedicated `OperationQueue` with a handler, timestamp each sample, and bound the buffer or processing work. |

The update interval is a request, not a promise of exact cadence. Apple documents that delivered intervals can be capped by hardware and recommends checking sample timestamps when timing matters. Never derive velocity, cadence, or gesture duration from callback count alone.

Stop the specific service with `stopAccelerometerUpdates()`, `stopGyroUpdates()`, `stopMagnetometerUpdates()`, or `stopDeviceMotionUpdates()` when it is no longer needed. A manager object still in memory is not the same as an active service, and an active service is not a reason to keep a screen or sensor pipeline alive indefinitely.

## Coordinate frames and attitude provenance

`CMAttitudeReferenceFrame` defines the frame from which pitch, roll, and yaw are reported. Call `CMMotionManager.availableAttitudeReferenceFrames()` and choose a frame that is actually available on the current device. The magnetic-north and true-north frames have different heading and calibration implications from arbitrary-Z-vertical frames; choose deliberately and display the frame/provenance when it affects the user’s interpretation.

`CMAttitude` offers Euler angles, a rotation matrix, and a quaternion. They are mathematical representations of an attitude estimate. A UI can use one representation, while a renderer or filter may use another, but do not combine them as if they were independent sensor readings.

`CMDeviceMotion` separates gravity and user acceleration. That is useful for interaction design, but it does not automatically identify an exercise, a location, a person’s intent, or a medical event. Preserve:

```text
sample timestamp
reference frame
sensor family
device orientation / coordinate convention
availability and calibration state where exposed
processing revision or app filter version
```

When a sensor result drives an AI or domain action, pass that provenance along with the app-owned feature vector. Do not pass an unlabelled array of floats and later claim what it means.

## Activity classification is probabilistic state, not a binary truth

`CMMotionActivityManager` provides current updates and historical queries for recognized activity. Apple documents categories including stationary, walking, running, cycling, and automotive, plus unknown. `CMMotionActivity` properties are not mutually exclusive: more than one can be true, and all can be false when motion does not match the supported categories. The object also includes a start date and confidence.

Use an activity projection such as:

```text
observedAt
startDate
candidate categories: set, not one enum
confidence: low / medium / high
source: device motion activity
stale / unavailable state
```

Do not show “the person is driving” as a guaranteed fact. Use language such as “Motion is currently classified as automotive” and make the downstream action conservative. A navigation or notification feature should require a stable, policy-approved state window before changing behavior.

Stop live activity updates when the feature ends and bound historical queries to the user-visible time window. A historical classification result is not a continuous background subscription or a license to retain a person’s movement history indefinitely.

## Pedometer data has cumulative and historical semantics

`CMPedometer` exposes system-generated walking data such as steps, distance, floors ascended/descended, pace, and cadence where the current device supports each metric. Check each availability method independently; a device may provide steps but not every other metric.

Live `startUpdates(from:withHandler:)` values are cumulative from the requested start date through the current time. The handler runs on a serial dispatch queue, and delivery temporarily stops while the app is suspended. Query `CMPedometerData.startDate` and `endDate` rather than assuming the callback means “one new step.”

Historical `queryPedometerData(from:to:withHandler:)` is asynchronous and Apple documents that only the past seven days of data are available through this cache. If a product needs a longer history, define a separate user-approved persistence and HealthKit route; do not imply that the Core Motion query is an all-time database.

Pedometer values are a system estimate. Preserve units, start/end, availability, authorization, and the query window in the app projection. Never convert the value into a calorie, health, or medical claim without the appropriate domain source and review.

## Altimeter route: relative versus absolute

`CMAltimeter` provides relative altitude changes and, on supported devices, absolute altitude. Check `isRelativeAltitudeAvailable()` and `isAbsoluteAltitudeAvailable()` separately before starting the corresponding update service. Relative altitude answers “how has elevation changed from the starting point?”; absolute altitude has a different product meaning and availability contract.

Apple documents that altitude events are delivered at regular intervals regardless of whether the data changed. Do not treat every callback as a meaningful climb or emit a new database record for every unchanged pressure sample. Store a bounded baseline and apply a product-specific change threshold only when the user outcome needs it.

Stop with the matching method: `stopRelativeAltitudeUpdates()` or `stopAbsoluteAltitudeUpdates()`. Keep pressure units and timestamps with the measurement, and show a “calibrating” or “unavailable” state rather than displaying false precision.

## Headphone motion route

`CMHeadphoneMotionManager` delivers device-motion updates from supported Apple headphones. Check `isDeviceMotionAvailable` before starting. If the feature needs accessory connection state, also use connection-status updates and a delegate that can respond to connection changes. Stop device-motion and connection-status updates when the accessory leaves or the feature ends.

Headphone attitude uses headphone-specific coordinate axes. Do not reuse an iPhone coordinate-frame diagram or assume the user’s head is aligned with the phone. Pair the pose with an accessory identity/connection state, sample timestamp, and app-owned calibration/recenter action if the product needs a stable spatial gesture.

The user can remove headphones, switch routes, or use an unsupported accessory. The fallback should return to ordinary touch, device motion, or a visible control—not keep displaying the last pose as live.

## Sampling, queues, backpressure, and energy

Sensor work is a budgeted live pipeline:

```text
physical sensor
    -> Core Motion service
    -> operation queue / latest-value poll
    -> bounded reducer or ring buffer
    -> throttled UI projection
    -> optional model window
```

Rules:

- choose the lowest update rate that answers the interaction;
- use one `OperationQueue`/actor ownership boundary for a high-rate service;
- avoid publishing raw sensor values into SwiftUI state at the sensor frequency;
- drop old frames when only the latest state matters;
- use a bounded ring buffer when a model or gesture recognizer needs a window;
- timestamp samples and measure the actual interval;
- do not perform model inference, disk I/O, or network work inside a sensor callback;
- stop or reduce updates when the screen, capture session, workout, or accessory interaction ends; and
- cancel timers/tasks and clear stale state during teardown.

The sensor pipeline can continue after a view disappears if the product explicitly owns a longer session, but that ownership must be visible and tested for energy and privacy. “The manager is retained in a singleton” is not a lifecycle policy.

## SwiftUI and Liquid Glass sensor surfaces

An Apple-native motion surface should communicate the user outcome, not expose a raw oscilloscope by default:

```text
purpose and active session
    -> capability / authorization card
    -> current projection with units and timestamp
    -> calibration / confidence / stale state
    -> optional detail chart or debug view
    -> stop / pause / fallback action
```

Use standard SwiftUI controls, `Gauge`, `ProgressView`, charts, lists, and text labels before custom rendering. Apply Liquid Glass to a small status/action cluster—such as Start, Pause, Recenter, and sensor status—rather than to every live data point. Keep measurement labels and units opaque and legible when Reduce Transparency is enabled.

Recommended state copy:

| State | Surface behavior |
| --- | --- |
| Unsupported | “This device does not provide this motion sensor.” Offer a manual or alternate interaction. |
| Permission needed | Explain what motion data will do before requesting access. |
| Ready | Show the selected sensor family and an explicit Start action. |
| Calibrating | Explain that the frame or baseline is settling; do not display false precision. |
| Live | Show value, unit, timestamp/freshness, and a Stop/Pause action. |
| Low confidence | Keep the observation visible but qualify the downstream action. |
| Stale | Stop live animations and show when the last sample arrived. |
| Disconnected | For headphones, show accessory removal and a fallback. |
| Reduced effects | Replace animated motion trails with a static value and text delta. |

Provide VoiceOver labels for sensor family, value, unit, confidence, timestamp, and action. A motion-controlled action needs a button, keyboard, switch-control, or text alternative. Haptics can reinforce a threshold but cannot be the only notification.

## Optional on-device AI motion summaries

Foundation Models can summarize a bounded, app-owned feature window—for example, “the gesture likely completed” or “activity classification was mixed”—when the product has a clear user benefit. Use a typed proposal or summary after deterministic signal processing:

```text
timestamped bounded feature window
    -> filter / normalization / feature extraction
    -> optional typed Foundation Models summary
    -> confidence and policy validation
    -> user-visible review or conservative action
```

Keep raw sensor streams out of the model when derived features are enough. Do not send the person’s continuous motion history, headphone pose, or health-adjacent data to a server by default. A model must not directly start/stop sensors, change sampling rates, write HealthKit, trigger a notification, or label a medical/fitness condition. Validate ranges, window length, feature revision, model availability, and staleness; fall back to the deterministic signal path when the model is unavailable or refuses.

Use careful language. “The motion classifier reports walking with high confidence” is different from “the person walked.” “Relative altitude increased 8 meters” is different from “the person climbed eight meters accurately.”

## Privacy and accessibility

Motion data can reveal routines, transportation, exercise, location context, and accessory use. Use the least sensor family, shortest retention, and narrowest sampling interval that meets the purpose. Avoid analytics on raw samples. Redact sensor windows and headphone identity from logs.

Test VoiceOver, Dynamic Type, Increase Contrast, Reduce Transparency, Reduce Motion, Switch Control, keyboard/pointer input, and localized/RTL unit layouts. Provide a way to pause or stop continuous sensing. Do not make an important action depend on a person shaking, tilting, walking, or wearing a specific accessory without a conventional alternative.

## Verification boundary

| Claim | Minimum proof |
| --- | --- |
| Target supports the service | Device matrix captures the appropriate availability property for each sensor family. |
| Privacy configuration is correct | Built `Info.plist` contains `NSMotionUsageDescription` with purpose-first text and the request does not crash. |
| Motion updates are owned correctly | One `CMMotionManager`, one feature owner, intentional queue, update intervals, and matching stop methods. |
| Device-motion math is interpretable | Reference frame availability, coordinate convention, timestamps, calibration/recenter, and representation tests. |
| Activity classification is handled honestly | Overlapping flags, confidence, unknown/all-false, historical/current, stale, and denied fixtures. |
| Pedometer semantics are correct | Metric availability, cumulative live start date, seven-day historical boundary, units, and Reminders/HealthKit separation. |
| Altimeter semantics are correct | Relative/absolute availability, baseline, unchanged-event behavior, units, pressure, and stop/restart proof. |
| Headphone pose works | Supported headphone connection, axes, start/stop, disconnect/reconnect, and physical pose evidence. |
| Energy/backpressure is safe | Queue latency, dropped-frame policy, ring-buffer bounds, thermal/energy observation, and teardown. |
| SwiftUI design works | Start/pause/stop, stale/unsupported/permission states, accessibility task, reduced-effects fallback, and iPad input. |
| AI is safe | Availability, typed schema/range validation, feature provenance, cancellation/stale rejection, privacy minimization, and deterministic fallback. |
| Release works | Archive, signed installation, TestFlight retest, target/device matrix, and physical sensor/accessory evidence. |

The [Core Motion sensor design review](../21-design-deep-dives/161-swiftui-core-motion-sensor-route-review-design.md), [route worksheet](../50-capability-recipes/164-swiftui-core-motion-sensor-route-review-route.md), [proof matrix](../60-verification/158-swiftui-core-motion-sensor-route-proof-matrix.md), and [code recipes](../70-code-recipes/176-swiftui-core-motion-sensor-route-review-recipes.md) turn these boundaries into reusable project artifacts.

## Sources

- [Core Motion](https://developer.apple.com/documentation/coremotion/)
- [CMMotionManager](https://developer.apple.com/documentation/coremotion/cmmotionmanager)
- [CMDeviceMotion](https://developer.apple.com/documentation/coremotion/cmdevicemotion)
- [CMAttitude](https://developer.apple.com/documentation/coremotion/cmattitude)
- [CMAttitudeReferenceFrame](https://developer.apple.com/documentation/coremotion/cmattitudereferenceframe)
- [deviceMotionUpdateInterval](https://developer.apple.com/documentation/coremotion/cmmotionmanager/devicemotionupdateinterval)
- [CMMotionActivityManager](https://developer.apple.com/documentation/coremotion/cmmotionactivitymanager)
- [CMMotionActivity](https://developer.apple.com/documentation/coremotion/cmmotionactivity)
- [CMAuthorizationStatus](https://developer.apple.com/documentation/coremotion/cmauthorizationstatus)
- [CMPedometer](https://developer.apple.com/documentation/coremotion/cmpedometer)
- [CMPedometerData](https://developer.apple.com/documentation/coremotion/cmpedometerdata)
- [startUpdates(from:withHandler:)](https://developer.apple.com/documentation/coremotion/cmpedometer/startupdates%28from%3Awithhandler%3A%29)
- [queryPedometerData(from:to:withHandler:)](https://developer.apple.com/documentation/coremotion/cmpedometer/querypedometerdata%28from%3Ato%3Awithhandler%3A%29)
- [CMAltimeter](https://developer.apple.com/documentation/coremotion/cmaltimeter)
- [CMAltitudeData](https://developer.apple.com/documentation/coremotion/cmaltitudedata)
- [CMHeadphoneMotionManager](https://developer.apple.com/documentation/coremotion/cmheadphonemotionmanager)
- [NSMotionUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nsmotionusagedescription)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
