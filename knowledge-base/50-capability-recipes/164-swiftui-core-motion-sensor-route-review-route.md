# SwiftUI Core Motion sensor-route worksheet

Use this worksheet before implementing a motion, activity, pedometer, altitude, or headphone-pose feature for iOS 26. It keeps physical capability, privacy, service ownership, timestamps, energy, AI, and proof separate.

## Route card

| Field | Decision to record |
| --- | --- |
| User outcome | Exact task or insight the motion service enables. |
| Sensor family | Device motion, accelerometer, gyroscope, magnetometer, activity, pedometer, altimeter, or headphone motion. |
| Hardware gate | Availability properties and target/device/accessory matrix. |
| Privacy gate | `NSMotionUsageDescription`, purpose copy, authorization status, and denial fallback. |
| Service owner | One `CMMotionManager` owner plus separately owned activity/pedometer/altimeter/headphone services where needed. |
| Delivery style | Latest-value polling versus handler updates; queue and callback policy. |
| Sampling | Requested interval, actual timestamp interval, window size, throttling, and drop policy. |
| Coordinate model | Device/headphone axes, attitude reference frame, units, calibration/recenter, and orientation. |
| Projection | App-owned value/activity/step/altitude/pose state with freshness and confidence. |
| Energy | Start/stop conditions, background/suspension behavior, thermal and battery observation. |
| AI boundary | Derived feature schema, proposal/summary, validation, privacy, cancellation, and deterministic fallback. |
| Evidence | Fixture, simulator, signed physical device, accessory, system/account, archive, TestFlight, and release proof. |

## 1. Route selection

```text
Need an instantaneous gesture or tilt?
    -> CMMotionManager accelerometer / gyro / device motion

Need fused attitude or gravity/user acceleration?
    -> CMMotionManager device motion + available CMAttitudeReferenceFrame

Need walking/running/automotive classification?
    -> CMMotionActivityManager

Need steps/distance/floors/pace/cadence?
    -> CMPedometer

Need elevation change or absolute altitude?
    -> CMAltimeter

Need head pose from supported headphones?
    -> CMHeadphoneMotionManager + connection state
```

Add HealthKit or WorkoutKit only when the product needs a health/workout record, permission model, or long-term domain source. Add Core Haptics only when physical feedback is part of the outcome.

## 2. Availability and permission manifest

Before starting a service, record:

```text
target: iOS 26 / device family / final SDK
NSMotionUsageDescription: purpose-first string present
device motion available: yes/no
accelerometer/gyro/magnetometer available: yes/no
activity available/status
pedometer metric availability/status
relative/absolute altitude availability/status
headphone motion availability/status/connection
fallback: touch/manual/static/alternate sensor
```

Do not turn `false` availability into an error alert if the feature can simply choose a supported fallback. Do not request permission for a service the person did not invoke.

## 3. Ownership and lifecycle

Use one sensor coordinator:

```text
MotionFeatureCoordinator
  owns one CMMotionManager
  owns only the chosen additional service objects
  owns operation queue / task cancellation
  owns generation and freshness state
  publishes immutable SwiftUI projection
```

At Start:

1. check hardware and authorization;
2. establish the selected reference frame or coordinate convention;
3. configure the interval and queue;
4. increment a session generation;
5. start the service; and
6. publish ready/live only after the service is active or has delivered a valid sample.

At Stop or teardown:

1. stop the matching service;
2. cancel processing tasks;
3. clear or mark the last sample stale;
4. invalidate the session generation; and
5. release the feature’s queue/buffer references.

For a screen-owned interaction, stop in disappearance or explicit cancellation. For a workout or game session, document the longer owner and test suspension/resume/thermal behavior.

## 4. High-rate sampling contract

Record the following for every high-rate stream:

- requested update interval;
- timestamp of each accepted sample;
- actual inter-sample interval statistics;
- queue backlog or dropped-sample count;
- maximum ring-buffer length;
- feature extraction version; and
- time from sample to SwiftUI projection or action.

If the UI only needs a live cursor or tilt, poll the manager’s latest-value property at the render/update cadence. If a gesture recognizer or model needs a temporal window, use a bounded buffer and process off the callback queue. Never let the callback directly mutate a large SwiftUI view tree.

## 5. Device-motion frame contract

```text
available frames
    -> choose product frame
    -> document x/y/z and neutral orientation
    -> start device motion
    -> retain sample timestamp + frame identity
    -> recenter only at an explicit user/session boundary
```

If a frame is unavailable, choose a supported alternate or disable the feature. Do not silently interpret magnetic-north values as arbitrary-Z-vertical values. If the app transforms the coordinate frame, version the transform and test portrait/landscape/face-up/face-down cases.

## 6. Activity route

For `CMMotionActivityManager`:

```text
activity availability/status
    -> live or historical query window
    -> CMMotionActivity set of flags + confidence + startDate
    -> stability/debounce policy
    -> visible “classified as” projection
```

Keep overlapping flags. Define the minimum stability window before a product action such as changing navigation language or pausing a timer. Store the classification and confidence only as long as the feature needs them.

## 7. Pedometer route

For `CMPedometer`:

```text
metric availability/status
    -> choose live start date or historical bounded window
    -> handler receives cumulative CMPedometerData
    -> project steps/distance/floors/pace/cadence with start/end
    -> stop or cancel at feature boundary
```

Call out the seven-day historical cache in the product contract. Do not use a historical query to imply lifetime totals. Check step/distance/floor/pace/cadence availability separately.

## 8. Altimeter route

Choose relative or absolute altitude explicitly:

```text
relative available -> baseline at session start -> delta / pressure / timestamp
absolute available -> absolute route and units -> timestamp / confidence policy
```

Ignore or coalesce unchanged periodic events according to the product’s threshold policy. Keep the matching stop method and a calibration state in the route.

## 9. Headphone route

```text
headphone motion available?
  no -> touch/device-motion fallback
  yes -> connection status -> start pose updates
       -> pose + headphone axes + timestamp
       -> disconnect -> stop and clear live pose
```

Use a delegate/connection observer for accessory changes. Do not treat a cached `CMDeviceMotion` as current after disconnect.

## 10. SwiftUI and Liquid Glass route

Compose:

```text
SensorPurposeView
  -> CapabilityStatusCard
  -> CurrentProjectionView
  -> FreshnessConfidenceView
  -> SessionControls
  -> ManualFallbackView
  -> OptionalAISummaryView
```

Use Liquid Glass only around `SessionControls` or a small status cluster. Keep units, timestamps, and warnings on the content surface. Provide static, readable fallback under Reduce Motion/Transparency and when the sensor is unavailable.

## 11. AI proposal route

Use derived features, not raw streams, unless raw data is essential and explicitly justified:

```text
bounded feature window
  [duration, normalized axes, peaks, activity flags, confidence]
      -> typed model proposal/summary
      -> range and provenance validation
      -> user review or conservative deterministic action
      -> no direct sensor or system side effect
```

Reject stale windows, mismatched feature revisions, impossible ranges, missing timestamps, and unsupported model output. Keep model-unavailable and model-refusal states equal to a valid deterministic fallback, not an empty black box.

## 12. Evidence package

```text
motion-route.json
  target / SDK / OS / device / accessory
  service family and availability properties
  NSMotionUsageDescription redacted copy
  authorization state and prompt result
  owner/session generation/queue policy
  requested versus actual timestamp interval
  reference frame / axes / units
  sample-drop/backpressure/energy data
  stop/teardown/reconnect result
  SwiftUI/accessibility/reduced-effects result
  AI proposal/fallback result, if used
  archive/TestFlight metadata
screenshots or recordings
  purpose/permission
  ready/live/stale/unsupported
  physical interaction or accessory disconnect
```

Simulator motion injection can exercise reducers and UI states. It does not prove sensor accuracy, activity semantics, pedometer history, pressure/elevation behavior, headphone pose, energy cost, or a person’s physical task.

## Sources

- [Core Motion](https://developer.apple.com/documentation/coremotion/)
- [CMMotionManager](https://developer.apple.com/documentation/coremotion/cmmotionmanager)
- [CMDeviceMotion](https://developer.apple.com/documentation/coremotion/cmdevicemotion)
- [CMAttitude](https://developer.apple.com/documentation/coremotion/cmattitude)
- [CMAttitudeReferenceFrame](https://developer.apple.com/documentation/coremotion/cmattitudereferenceframe)
- [CMMotionActivityManager](https://developer.apple.com/documentation/coremotion/cmmotionactivitymanager)
- [CMMotionActivity](https://developer.apple.com/documentation/coremotion/cmmotionactivity)
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
