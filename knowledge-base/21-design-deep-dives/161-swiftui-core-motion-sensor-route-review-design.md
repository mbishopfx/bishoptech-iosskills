# SwiftUI Core Motion sensor-route review design

This design review defines an Apple-native motion surface for sensor input, activity, steps, altitude, or supported headphone pose. The screen should help a person complete a physical task or understand a measured state; it should not turn raw sensor values into a decorative dashboard that hides authorization, freshness, uncertainty, or energy cost.

## Design brief

| Decision | Recommendation |
| --- | --- |
| Primary user outcome | Understand or use one selected motion capability with an honest current state and a clear stop/fallback path. |
| Primary surface | SwiftUI purpose card, capability/authorization state, current value/activity projection, units/timestamp/confidence, and accessible controls. |
| Sensor authority | One explicit service owner; high-rate samples stay out of the SwiftUI body and are reduced into app-owned state. |
| Liquid Glass role | Compact Start/Pause/Stop/Recenter/status group; never a translucent coating over every live sample. |
| AI role | Optional typed summary or gesture proposal from a bounded derived feature window, with provenance, review, and deterministic fallback. |
| Fallback | Touch, keyboard, switch control, text, static value, or another supported sensor family. |

The design contract is:

```text
purpose -> capability -> permission -> active session -> measured projection -> stop/fallback
```

## Start with purpose and sensor identity

The top of the screen should name the route in ordinary language:

- “Tilt the phone to steer”;
- “View today’s steps”;
- “Track elevation change”;
- “See how the phone classifies movement”; or
- “Use head pose while supported headphones are connected.”

Do not label a page merely “Motion.” The person should know whether the app is using device motion, activity classification, pedometer, altitude, or headphone motion and why.

If the feature combines services, show the combination explicitly. For example, “Pedometer total + app-owned walking session” is different from “Core Motion live orientation.”

## Recommended screen composition

```text
NavigationStack
  title: one sensor outcome
  toolbar: settings / privacy / stop action
  purpose and permission card
  capability card
    service family
    supported / unavailable / connected state
  live projection
    value + unit
    freshness timestamp
    confidence / calibration / frame context
  optional detail chart or activity timeline
  action group
    Start / Pause / Stop / Recenter / Use manual control
  AI proposal or summary card, only after explicit opt-in
  energy/privacy note for an ongoing session
```

Use one primary action. If the screen is already live, the primary action should be Pause or Stop—not another “Start” button that can create a second owner.

## State-driven visual language

| State | Visual hierarchy | Copy direction |
| --- | --- | --- |
| Unsupported | Neutral status card; no animated chart. | “This device does not provide gyroscope data.” |
| Permission needed | Purpose-first card with one request action. | “Allow motion access to classify movement during this session.” |
| Ready | Capability summary and a clear Start button. | Name the sensor family and expected energy/interaction behavior. |
| Calibrating | Static progress/status with an explanation. | “Hold the device steady while the reference frame settles.” |
| Live | Strong value, unit, timestamp, and Stop/Pause. | Use “classified as” or “estimated” when appropriate. |
| Low confidence | Value remains readable; confidence is supporting text and icon. | Avoid red error styling for every uncertain sample. |
| Stale | Freeze or dim the value, show last update time. | “No new motion sample since …” |
| Headphones disconnected | Accessory state takes priority over last pose. | “Connect supported headphones to resume head-motion input.” |
| Denied/restricted | Plain explanation and alternate action. | Offer touch/manual input or Settings without blocking the whole app. |
| Reduced effects | No continuous motion trail or parallax. | Use static delta and text change. |

Color can reinforce a state but cannot be the only signal. A green dot is not a substitute for “Live — updated 1 second ago.”

## High-rate motion control

For tilt, gesture, or game input, show the response rather than exposing every raw sample. Use a stable visual anchor, a bounded indicator, and a visible calibration/recenter action. The person should be able to understand:

- which device orientation is neutral;
- which direction maps to which action;
- whether the input is currently active;
- how to pause or disable motion control; and
- what manual alternative exists.

Avoid a UI that moves the whole screen in response to every gyroscope update. This can conflict with Reduce Motion, cause fatigue, and make the interface feel unstable. Animate the semantic object that responds to the input, and quantize or smooth the visual projection separately from the sensor pipeline.

## Activity and pedometer dashboards

Activity and pedometer data need context:

```text
Today’s movement
  walking — high confidence, since 9:14 AM
  4,820 steps · 3.1 km · 12 floors
  data window: 12:00 AM–now
  last updated: 9:42 AM
```

Label the data window and source. If a live pedometer update is cumulative from a requested start time, say “session total” rather than “new steps.” If the data is a seven-day Core Motion history query, do not present it as an all-time record. If the feature is a health or workout product, route the domain record through HealthKit/WorkoutKit design and consent rather than letting a motion dashboard imply medical truth.

Activity classifications can overlap or be unknown. A stacked or multi-label chip is more honest than a single mutually exclusive icon. Use text such as “walking + automotive signals” only when that is meaningful to the product; otherwise show “mixed motion classification” with confidence.

## Altitude and pressure surface

Relative altitude is often the clearest user-facing route:

```text
Elevation change
  +42 m
  relative to session start
  baseline 118 m · updated 12 s ago
```

Make absolute versus relative explicit. Avoid fake precision, show a calibration/baseline state, and do not animate a climb for unchanged regular callbacks. Pressure can be a technical detail, not the headline, unless the product is designed for it.

## Headphone-motion surface

Headphone motion requires connection awareness at all times:

```text
Head pose input
  AirPods connected · motion available
  [Recenter] [Pause]

When disconnected:
  Head motion paused
  Connect supported headphones or use touch controls
```

Do not keep a ghosted head pose as if it were live after the accessory disconnects. If the product uses pose to aim or select, provide a touch/keyboard/switch-control route that is discoverable without wearing headphones.

## Liquid Glass for sensor controls

Apply Liquid Glass to functional clusters:

- Start/Pause/Stop with the current session state;
- Recenter and calibration actions;
- a compact sensor-family picker; or
- a small AI proposal action group.

Keep units, timestamps, confidence, and warnings on a legible surface. Do not wrap a high-rate chart in nested glass layers that reduce contrast or create reflections. Use a standard `Toolbar`, `ControlGroup`, `Button`, `Menu`, or `Picker` when it already expresses the interaction.

Glass transitions should not change the meaning of the action. A Start button can become a Stop button with a clear label and state, but it should not morph into a decorative orb that requires motion feedback to understand.

Test:

- glass enabled on the current target;
- reduced transparency;
- increased contrast;
- large text;
- landscape and iPad layouts; and
- no-glass fallback on older or unsupported targets.

## AI summary card

An AI summary should be a quiet interpretation layer after deterministic motion processing:

```text
Motion summary
  “The gesture matched your saved tilt-to-confirm pattern.”
  Based on: 1.2 s feature window · device motion · local processing
  Confidence: medium

[Use] [Try again] [Details]
```

Show the source window, feature revision, and uncertainty. “Local processing” is meaningful only if the actual route stayed on device; do not say it when data was sent to a server. The card should not silently change a workout, unlock a door, create a record, or send a message.

If the AI proposal is invalid or unavailable, keep the deterministic motion result and offer a manual action. If the device is not supported, do not show an AI card that implies sensor data exists.

## Accessibility and motion sensitivity

The app should be usable without the sensor:

- provide buttons and text alternatives for motion-controlled actions;
- expose current values, units, freshness, and confidence to VoiceOver;
- avoid making a screen shake or pan continuously in response to raw updates;
- respect Reduce Motion with static transitions and no parallax;
- respect Reduce Transparency and Increase Contrast for glass controls;
- support Dynamic Type without truncating the unit or last-update text;
- keep status changes announced at semantic boundaries, not every sensor callback; and
- test keyboard, pointer, Switch Control, Voice Control, and external controls where the target supports them.

For fitness-adjacent features, avoid language that pressures a person to move or implies a medical outcome. A sensor reading is not a diagnosis.

## Design review checklist

- [ ] The page names the exact motion service and user outcome.
- [ ] Unsupported, not-determined, denied, restricted, ready, live, stale, and disconnected states are distinct.
- [ ] The active service has one visible owner and one stop/pause path.
- [ ] Values include units, time window, timestamp/freshness, and confidence/calibration where relevant.
- [ ] Device-motion reference-frame and headphone-coordinate assumptions are documented.
- [ ] Pedometer cumulative versus historical semantics are visible.
- [ ] Relative versus absolute altitude is not conflated.
- [ ] Liquid Glass is limited to functional controls and remains legible without transparency.
- [ ] Motion-controlled actions have touch/text/keyboard/accessibility alternatives.
- [ ] Reduce Motion removes sensor-driven parallax and continuous motion trails.
- [ ] AI summaries identify source features, uncertainty, and local/server boundary, and remain dismissible.
- [ ] No screen screenshot or simulator trace is treated as physical accuracy proof.

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
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
