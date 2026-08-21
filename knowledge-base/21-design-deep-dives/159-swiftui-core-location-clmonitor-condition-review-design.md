# SwiftUI Core Location `CLMonitor` condition design review

This design lane is for native location experiences that react to entering/leaving a geographic area or encountering a beacon identity. The screen must communicate location purpose, authorization, accuracy, monitoring state, background behavior, and the action that follows a condition transition.

## Lead with the action, not the coordinate

Use a human-readable outcome:

- “Remind me when I arrive at the studio.”
- “Show the walking checklist when I leave work.”
- “Tell me when the museum beacon is nearby.”

Do not lead with a latitude, longitude, monitor name, or UUID. Those are implementation details and can expose sensitive location context unnecessarily.

## Screen hierarchy

```text
NavigationStack
  -> purpose and location relationship
  -> authorization/accuracy/service-session status
  -> map or beacon explanation
  -> active condition list
  -> latest event and diagnostics
  -> action policy and test/remove controls
```

### Purpose card

The first card answers:

1. What will happen?
2. Where or near what will it happen?
3. Does the app need background location?
4. What does the app keep or send?

Use the system permission sheet only after this context is clear. The app’s copy should not imply that a geofence is a live route or that a beacon condition is a precise indoor position.

## Authorization and accuracy status

Use a semantic status card with text, icon, and action:

| State | UI language |
| --- | --- |
| Not requested | “Allow location so this reminder can respond when you arrive.” |
| Request in progress | “Finish the Apple location permission step.” |
| Authorized, full accuracy | “Location monitoring is ready.” |
| Authorized, reduced accuracy | “Monitoring may be less precise. Review the location setting.” |
| Denied/restricted | “Location monitoring is off.” Button: “Open Settings.” |
| Service session required | “Location needs one more setup step while the app is open.” |
| Condition unsupported/limit | “This device cannot add another condition right now.” |
| Persistence unavailable | “The system could not keep this monitor active. Try again.” |

Do not show “Active” merely because a map circle exists. The monitor identifier, event consumer, and diagnostics need separate state.

## Map surface

Use MapKit to explain the intended condition:

- a center pin or user-provided place label;
- a circle for the configured radius;
- a selected place card with edit/remove actions; and
- an accessible text summary of the same information.

Keep the map secondary to the action. The circle is an explanation of the configured condition, not a visual assertion of GPS precision. When accuracy is limited, show that state over the map in text; do not simply shrink or blur the circle.

For privacy:

- hide precise coordinates by default;
- use an app-owned place label;
- avoid a map snapshot in logs or analytics;
- let the user remove a condition without dragging a map pin; and
- state whether the app reacts to transitions only or stores history.

## Beacon surface

Beacon experiences should describe the expected physical object without exposing a raw UUID in the main UI:

```text
Museum entrance beacon
When nearby: show the exhibit checklist
Status: waiting for the beacon
```

An advanced diagnostic screen can show UUID/major/minor to a developer or installer with an explicit disclosure. The primary user path should remain about the place and action.

## Active condition list

Use a list with one row per app-owned identifier:

```text
Studio                    Satisfied
Museum entrance           Waiting
Home                      Monitoring unavailable
```

Each row should expose:

- user-facing label;
- condition type (place/beacon);
- current state and date;
- diagnostic warning if present;
- the action that will run; and
- a remove/edit affordance.

Do not show “20/20 conditions” as a scary system quota without an explanation. If the limit is reached, guide the person through prioritizing and removing inactive conditions.

## Event detail and diagnostics

When an event arrives, show the state change and any relevant diagnostic:

```text
Arrived at Studio
Today at 9:04 AM
Reminder shown

Location accuracy: reduced
```

Do not claim a condition was “missed” when `persistenceUnavailable`, `insufficientlyInUse`, `conditionUnsupported`, or `serviceSessionRequired` indicates a different cause. A compact “Why this happened” disclosure can make these flags understandable without exposing system internals.

## Background and reboot copy

The user should know that the system may wake the app for a condition event and that monitoring resumes after the device is unlocked following a reboot. The app should not promise an event while the device is powered off, locked after reboot, globally restricted, or outside the system’s supported conditions.

If the app relaunches in the background, it should restore the monitor and event consumer without showing a full onboarding screen. If a user later opens the app, show the last-known state with a “checking system status” affordance.

## Liquid Glass rules

Use Liquid Glass around app-owned controls:

- “Add place” or “Add beacon” toolbar actions;
- a compact authorization/status cluster;
- event action choices;
- an inspector for radius/label/purpose; and
- a test/remove control group.

Avoid putting glass over the entire map or making status warnings translucent enough to disappear into map content. Do not use custom glass to imitate Apple’s permission sheet. The screen should remain legible when transparency is reduced or the glass effect is unavailable.

## AI proposal surface

An optional AI layer can help turn a condition event into an app-owned action draft:

```text
Event: Arrived at Studio
Suggested action: Open the local session checklist
Why: You selected this action for the Studio place

[Review] [Apply once] [Dismiss]
```

The proposal should show the source event label and exact action. Keep raw coordinates, beacon IDs, and location history out of the user-facing prompt by default. Require review for notifications, content changes, or actions with external consequences. Provide “no AI” and “model unavailable” paths.

AI should never silently start Always authorization, create a hidden location history, or infer a person’s routine from a single event.

## Accessibility and alternate input

- [ ] The map has an accessible list/summary equivalent.
- [ ] Authorization and accuracy status are announced with actionable recovery.
- [ ] Radius and condition label are exposed as values, not only graphics.
- [ ] Event state/date/action are readable without map interaction.
- [ ] Add, edit, remove, test, and open-settings controls are keyboard/Switch Control reachable.
- [ ] Dynamic Type does not clip place labels or diagnostics.
- [ ] Reduce Transparency and Increase Contrast preserve warning legibility.
- [ ] Reduce Motion avoids unnecessary map/circle animation.
- [ ] VoiceOver focus returns to the status/action after a permission sheet or background event.

## Design review checklist

- [ ] The outcome and background purpose appear before permission.
- [ ] Coordinates/UUIDs are not default user-facing identity.
- [ ] Authorization, accuracy, service session, monitor registration, and event state are separate.
- [ ] The map circle is labeled as an intended condition, not a precision promise.
- [ ] The 20-condition resource limit has a prioritization path.
- [ ] Background relaunch and reboot/unlock behavior are explained.
- [ ] Liquid Glass is limited to app-owned controls.
- [ ] AI proposals are exact, reviewable, cancellable, and privacy-bounded.
- [ ] Every location-triggered action has a visible and accessible equivalent.
- [ ] Physical transition and TestFlight behavior are planned before shipping.

## Sources

- [Core Location](https://developer.apple.com/documentation/corelocation)
- [CLMonitor actor](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v)
- [CLMonitor.Event](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/event)
- [CLMonitor.Events](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/events-swift.struct)
- [CLMonitor.Record](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/record)
- [CLMonitor.CircularGeographicCondition](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/circulargeographiccondition)
- [CLMonitor.BeaconIdentityCondition](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/beaconidentitycondition)
- [CLCondition](https://developer.apple.com/documentation/corelocation/clcondition-swift.protocol)
- [Monitoring the user’s proximity to geographic regions](https://developer.apple.com/documentation/corelocation/monitoring-the-user-s-proximity-to-geographic-regions)
- [Handling location updates in the background](https://developer.apple.com/documentation/corelocation/handling-location-updates-in-the-background)
- [CLServiceSession](https://developer.apple.com/documentation/corelocation/clservicesession-pt7n)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
