# SwiftUI Core Location `CLMonitor` condition proof matrix

Use this matrix to distinguish a configured condition from a physical location transition. A map circle, `CLMonitor` actor, stored identifier, satisfied state, or AI proposal is not alone proof that the intended physical event was delivered.

Related pages:

- [Core Location `CLMonitor` review](../42-framework-deep-dives/131-swiftui-core-location-clmonitor-condition-review.md)
- [Core Location condition design review](../21-design-deep-dives/159-swiftui-core-location-clmonitor-condition-review-design.md)
- [Core Location condition route](../50-capability-recipes/162-swiftui-core-location-clmonitor-condition-review-route.md)
- [Core Location condition recipes](../70-code-recipes/174-swiftui-core-location-clmonitor-condition-review-recipes.md)

## Evidence ladder

| Level | Proves | Does not prove |
| --- | --- | --- |
| Source review | The route uses documented actor, condition, event, authorization, background, and release APIs. | Permission, physical transition, or background launch. |
| Target configuration | Usage descriptions, background capability, deployment target, and location entitlements are present. | The user granted access or a condition persisted. |
| Monitor record | The app can reopen a named monitor and see identifiers/records. | A geographic/beacon transition happened. |
| Event proof | `CLMonitor.Events` delivered a state/diagnostic event. | Precise location, continuous tracking, or correct downstream action. |
| Physical proof | A named device/beacon/place produced a transition and action. | TestFlight signing or every supported device condition. |
| Release proof | Archive/TestFlight preserve the route and usage disclosures. | Production behavior across all locations and permission choices. |

## Matrix

| Claim | Positive evidence | Negative/edge evidence | Owner |
| --- | --- | --- | --- |
| Purpose is disclosed | Pre-permission screen names the location-triggered outcome and background behavior. | Generic “improve your experience” copy or prompt without context. | Design/privacy |
| Usage descriptions are correct | Inspect final Info.plist for When In Use/Always/explicit service-session keys as used. | Missing, stale, or overbroad usage message. | App/release |
| Authorization works | Physical device completes permission/service-session path and diagnostics are recorded. | Denied, restricted, globally disabled, prompt in progress. | App QA |
| Accuracy behavior is clear | Full/reduced accuracy changes the UI and action policy intentionally. | Reduced accuracy hidden behind an “active” label. | App |
| Modern monitor is used correctly | `await CLMonitor(name)` creates/reopens actor; operations stay outside SwiftUI body. | Legacy delegate assumptions mixed into actor/AsyncSequence code. | App |
| Monitor identity is stable | Same monitor name is recreated after launch; condition identifiers reconcile. | New random name on every launch loses the system route. | App |
| Geographic condition is correct | Center/radius values are recorded and a physical test crosses the intended area. | Map circle mistaken for precise GPS boundary. | App/device |
| Beacon condition is correct | Physical beacon UUID/major/minor fixture satisfies intended wildcard rules. | Wrong beacon, raw UUID exposed in user copy, or no hardware test. | Device |
| Condition budget is handled | Test reaches 20-condition limit and UI prioritizes/removes explicitly. | Silent replacement or unbounded add attempts. | App |
| Condition record recovers | `identifiers` and `record(for:)` reflect state after relaunch/recreate. | Stored manifest claims monitoring while system record is absent. | App |
| Event sequence is consumed | One task iterates `monitor.events` and updates app-owned state. | Task created per redraw, cancelled on background, or no longer iterated. | App |
| State transition is correct | Satisfied/unsatisfied/unknown/unmonitored states map to visible actions. | Empty event stream presented as proof of “not there.” | App |
| Diagnostics are handled | Authorization, accuracy, limit, unsupported, insufficient-use, persistence, and service-session flags each map to recovery. | Any diagnostic is ignored or collapsed into “GPS error.” | App |
| Background relaunch works | Terminate app, trigger condition, system relaunches, same monitor is recreated, event is processed. | Foreground-only success or network dependency. | Device QA |
| Reboot behavior works | Reboot, unlock, recreate monitor, and capture resumed monitoring. | App expects events before unlock or never recreates. | Device QA |
| Downstream action is safe | Notification/local action is idempotent and tied to identifier/policy revision. | Duplicate event causes repeated external side effect. | App |
| Map/list design is accessible | Map has text/list equivalent, focus/labels work, diagnostics are readable. | Map-only condition or precise coordinate exposed unnecessarily. | Design/QA |
| Liquid Glass is appropriate | App-owned controls remain legible with transparency/contrast variants. | Glass hides map/status or imitates permission sheet. | Design |
| AI proposal is bounded | Coarse app-owned context only, typed output, allowlist, stale/cancel/review/fallback tests. | Raw coordinates/beacon IDs/history in prompts or automatic sensitive action. | AI/privacy |
| Archive is correct | Signed artifact includes usage descriptions/background capabilities and target configuration. | Debug build only or missing release settings. | Release |
| TestFlight works | Distributed build completes permission, condition, background, action, and accessibility fixtures on device. | Simulator/map preview presented as release proof. | Release |

## Fixture plan

```text
CL-01 permission: when-in-use/always/service-session states
CL-02 accuracy: full and reduced accuracy behavior
CL-03 geographic: inside -> outside -> inside at test radius
CL-04 beacon: UUID-only and UUID+major+minor wildcard behavior
CL-05 monitor: same name and identifiers across relaunch
CL-06 records: record(for:) after event and restart
CL-07 budget: 20 conditions and prioritization path
CL-08 diagnostics: denied, unsupported, insufficient-use, persistence, session required
CL-09 background: terminated app wakes and consumes events
CL-10 reboot: unlock gate and monitor recreation
CL-11 UI: map/list/VoiceOver/Dynamic Type/Reduce Transparency
CL-12 AI: coarse input, stale event, cancellation, allowlist, fallback
CL-13 release: archive, TestFlight, physical device retest
```

Record device model, iOS build, authorization/accuracy state, monitor name, condition identifier, center/radius or beacon fixture, event date/state/diagnostic, app build, and downstream action. Keep precise location and beacon identity out of shared logs unless the test requires controlled private evidence.

## Stop conditions

Stop before release if:

- the route has no accurate usage-disclosure and authorization path;
- the monitor is recreated with random names or conditions exceed the 20-condition budget;
- the app does not inspect diagnostic flags;
- background relaunch/reboot-unlock recreation is untested;
- a map overlay is treated as transition proof;
- the action is not idempotent;
- AI receives raw location history or can trigger sensitive effects without review; or
- archive/TestFlight has not been tested on a physical device.

## Sources

- [Core Location](https://developer.apple.com/documentation/corelocation)
- [CLMonitor actor](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v)
- [CLMonitor.Event](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/event)
- [CLMonitor.Events](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/events-swift.struct)
- [CLMonitor.Record](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/record)
- [CLMonitor.CircularGeographicCondition](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/circulargeographiccondition)
- [CLMonitor.BeaconIdentityCondition](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/beaconidentitycondition)
- [CLCondition](https://developer.apple.com/documentation/corelocation/clcondition-swift.protocol)
- [CLMonitoringState](https://developer.apple.com/documentation/corelocation/clmonitoringstate)
- [Monitoring the user’s proximity to geographic regions](https://developer.apple.com/documentation/corelocation/monitoring-the-user-s-proximity-to-geographic-regions)
- [Handling location updates in the background](https://developer.apple.com/documentation/corelocation/handling-location-updates-in-the-background)
- [CLLocationUpdate](https://developer.apple.com/documentation/corelocation/cllocationupdate)
- [CLServiceSession](https://developer.apple.com/documentation/corelocation/clservicesession-pt7n)
- [NSLocationWhenInUseUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocationwheninuseusagedescription)
- [NSLocationAlwaysAndWhenInUseUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocationalwaysandwheninuseusagedescription)
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
