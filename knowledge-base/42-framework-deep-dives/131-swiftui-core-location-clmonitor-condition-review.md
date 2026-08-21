# SwiftUI Core Location `CLMonitor` condition review

Modern Core Location condition monitoring is an actor and asynchronous-event route for geofences and beacon identity conditions. It is distinct from continuous location updates and from a static MapKit circle:

```text
location purpose and disclosure
        -> authorization/service-session diagnostics
        -> CLMonitor actor
        -> CLCondition with stable identifier
        -> CLMonitor.Events AsyncSequence
        -> SwiftUI state / local action / notification
        -> background relaunch and monitor recreation
```

This review targets iOS 26 projects using the modern Swift `CLMonitor` API. The legacy Objective-C `CLMonitor`/`CLMonitoringEvent` route exists in the documentation; do not mix its delegate/callback assumptions with the actor/`AsyncSequence` route without an explicit adapter.

## Choose the location lane

| Product lane | Primary route | Evidence boundary |
| --- | --- | --- |
| Enter/leave a geographic area | `CLMonitor` + `CLMonitor.CircularGeographicCondition` | A physical device transitions across a documented radius and delivers an event. |
| Proximity to an iBeacon identity | `CLMonitor` + `CLMonitor.BeaconIdentityCondition` | A physical beacon with the intended UUID/major/minor is observed and the event state changes. |
| Continuous or live location | `CLLocationUpdate`/`CLLocationManager` route | Location authorization, background mode/session, update stream, and power policy are separately proven. |
| Show the intended area | SwiftUI/MapKit visual overlay | The map is a visual explanation, not proof that Core Location’s condition triggered. |
| Act after a background transition | `CLMonitor.Events` plus app relaunch/recreate | The app recreates the monitor with the same name and continues iterating events after the system wakes it. |
| Let AI propose an action | Condition event + app-owned action policy -> typed proposal -> explicit review | The model does not infer a precise location, silently record a trail, or bypass authorization. |

Use `CLMonitor` for condition transitions. Do not keep a high-frequency `CLLocationUpdate` stream running just to infer whether a circular condition is satisfied.

## `CLMonitor` is an actor with durable identifiers

The modern `CLMonitor` is an actor. Create it asynchronously with a stable name:

```swift
let monitor = await CLMonitor("com.example.app.places")
```

Add a condition with a stable identifier, inspect `identifiers`, read a `record(for:)`, remove an identifier, and iterate `events`. A condition identifier is app-owned routing state; it is not a user identity or a location analytics ID.

The monitor contract is:

- `init(_:) async` creates or reopens a monitor with the specified name;
- `add(_:identifier:)` registers a `CLCondition`;
- `add(_:identifier:assuming:)` supplies an initial event state when the product has a reason to do so;
- `remove(_:)` removes the condition and its record;
- `identifiers` lists the conditions being monitored;
- `record(for:)` returns the condition and most recent event, if available; and
- `events` is an asynchronous sequence that the app must keep iterating.

Keep the monitor actor outside `View.body`. A SwiftUI view can observe an app-owned `@Observable` projection, but the actor owns condition operations and the event task owns its cancellation.

## Conditions and refinement

`CLCondition` is the protocol for monitor conditions. The modern nested condition types include:

### Circular geographic condition

`CLMonitor.CircularGeographicCondition` uses a center coordinate and radius. The radius is a location-condition boundary, not a promise of a GPS-precise ring on the screen. GPS accuracy, permissions, hardware, urban environment, and system power behavior all affect delivery.

### Beacon identity condition

`CLMonitor.BeaconIdentityCondition` uses a UUID and optional major/minor values. If only the UUID is supplied, major and minor behave as wildcards; if UUID and major are supplied, minor is a wildcard. Treat the identity as an intentional hardware/proximity contract and disclose what beacon the user is expected to encounter.

An event can include `refinement`, an optional condition representing the most specific condition to which the event applies. Do not discard it when a product supports nested or refined conditions; it can explain why a broad policy changed.

## Events are diagnostics as well as transitions

`CLMonitor.Event` carries:

- `identifier` and `date`;
- `state` (satisfied, unsatisfied, unknown, or unmonitored in the documented state type);
- optional `refinement`; and
- diagnostic flags for authorization, accuracy, persistence, condition limits, usage, and service-session requirements.

The diagnostic flags matter. A false assumption such as “no satisfied event arrived, therefore the person never entered” is unsafe. The event may indicate:

| Diagnostic | Product interpretation |
| --- | --- |
| `authorizationDenied` | The app lacks local authorization. Stop promising monitoring and show recovery. |
| `authorizationDeniedGlobally` | Location services are unavailable at the system level. |
| `authorizationRequestInProgress` | Do not duplicate a prompt or mutate the condition while the system request is active. |
| `authorizationRestricted` | The app cannot change authorization in the current context. |
| `accuracyLimited` | Reduced accuracy affects location-dependent expectations; update the UI and policy. |
| `conditionLimitExceeded` | The app/device condition budget is exhausted; reduce or prioritize conditions. |
| `conditionUnsupported` | The selected condition is not supported in the current environment. |
| `insufficientlyInUse` | The event reflects insufficient use conditions; do not treat it as a normal transition. |
| `persistenceUnavailable` | The system could not persist the monitor as expected. |
| `serviceSessionRequired` | Create/recreate the required location service session before relying on updates. |

Log diagnostic categories and the condition identifier, not a full location trail. A location transition has privacy weight even when the app only needs a local action.

## Condition limits and persistence

Core Location condition monitoring uses shared hardware resources. Apple documents a limit of 20 conditions of any type per app at a time. Build an eviction/prioritization strategy:

- keep stable identifiers for active user-facing places;
- remove conditions the user disabled;
- explain when a new place cannot be monitored;
- avoid silently replacing an important condition;
- persist the app-owned condition manifest without turning it into a location history; and
- reconcile the manifest with `monitor.identifiers` after launch.

The system can wake an iOS app when a condition is satisfied. After a launch or relaunch, recreate the monitor with the same name and continue iterating its event sequence. Monitoring after a device reboot begins only after the user unlocks the device. A relaunch, a monitor object, or a stored map circle is not proof that a transition was delivered.

## Authorization and service-session boundaries

Location services require usage descriptions and a user-facing purpose. Decide whether the route needs when-in-use or always authorization. The modern Core Location documentation describes `CLServiceSession` as a diagnostic/authorization-session boundary and includes `.whenInUse` and `.always` requirements.

For condition events and background use:

- create the appropriate service session while the app is in the foreground when the route requires it;
- recreate a required service session immediately when the app launches in the background after termination;
- understand whether Core Location implicitly establishes when-in-use authorization for the selected API or whether the app’s Info.plist requests explicit service-session behavior;
- do not ask for Always authorization merely because the design wants a map pin; and
- tell the user why a background condition can wake the app.

Authorization, accuracy, service-session diagnostics, and condition event state are separate. The map can show a region while permission is denied; the app must not present that visual as active monitoring.

## Event-consumer lifecycle

An event consumer should have a clear task and generation:

```text
launch/scene activation
  -> create monitor with stable name
  -> reconcile identifiers/records
  -> start one events task
event
  -> validate identifier and generation
  -> inspect state and diagnostics
  -> perform a deterministic local action
  -> update SwiftUI projection
background termination
  -> recreate monitor and events task on next launch
```

Do not create one `for await` task per SwiftUI redraw. Cancel the old consumer before replacing it. If the app uses a notification, task, or local automation after an event, keep that action idempotent; event delivery and app relaunch can produce repeated observations.

## SwiftUI and MapKit design

Use MapKit or a simple map overlay to help a person understand the intended condition. A native screen can contain:

1. an outcome title (“Arrive at the studio”);
2. authorization/accuracy/service-session status;
3. a map with the center and radius or beacon description;
4. a list of active condition identifiers with human-readable app-owned labels;
5. the latest event state and diagnostics; and
6. an action policy such as reminder, local notification, or content refresh.

Avoid putting raw latitude/longitude, a private address, or a beacon UUID in a large decorative card by default. Use the user’s label and a coarse summary, with precise data only where the task requires it.

Liquid Glass should wrap app-owned map controls, status actions, or a compact condition editor. Keep map content readable, and do not use a translucent overlay to hide an accuracy-limited or denied state. A region circle is an explanation layer, not a claim about actual GPS accuracy.

## Optional on-device AI location-action proposals

Foundation Models can propose a human-readable action from app-owned condition context:

```text
condition label: "Studio"
event: satisfied
action policy: "remind me to start my session"
        -> typed proposal
        -> explicit review
        -> local notification/task/action
```

Keep raw coordinates, beacon identifiers, location history, and precise timestamps out of the model unless the product has a separate, explicit, privacy-reviewed reason. Prefer a coarse event label, the direction of the state change, and the user’s configured action policy.

Validate proposals against a hard allowlist. A model can suggest “show the local session checklist” but should not silently upload a location, change an Always authorization, or trigger a sensitive action without user review. Invalidate a proposal when authorization, event generation, condition identifier, or policy revision changes. On unsupported devices or unavailable Foundation Models, run the deterministic action path.

## Accessibility and privacy

Location condition UX should:

- explain why monitoring is needed before the system prompt;
- announce authorization, accuracy, and service-session diagnostics;
- expose the condition label, radius/purpose, state, date, and action in text;
- provide a list/summary equivalent for map-only information;
- make a condition removable without requiring precise map gestures;
- respect Dynamic Type, VoiceOver, Increase Contrast, Reduce Transparency, Reduce Motion, keyboard, and Switch Control; and
- never make a location-triggered action the only way to understand a state change.

Privacy copy should say whether the app keeps a history or only reacts to transitions, whether data leaves the device, and what happens after the user disables location services. Do not log every event with exact coordinates if the app only needs an identifier and state.

## Verification boundary

| Claim | Minimum proof |
| --- | --- |
| Authorization works | Physical device completes the documented permission/service-session route and diagnostic state is captured. |
| Condition is registered | `CLMonitor` has the stable name/identifier and `record(for:)` reflects the condition. |
| Geographic transition works | Physical device crosses a test radius and `events` delivers satisfied/unsatisfied state. |
| Beacon transition works | Physical beacon with the intended UUID/major/minor produces the expected event. |
| Diagnostics are handled | Denied, reduced accuracy, unsupported, limit, persistence, insufficient-use, and service-session states map to UI/action. |
| Background works | Terminate/background the app, trigger a condition, relaunch/recreate monitor, and capture the event. |
| Reboot behavior works | Reboot, unlock, recreate monitor, and verify monitoring resumes only after unlock. |
| SwiftUI design works | Map/list/status/task flows pass accessibility and Liquid Glass setting variants. |
| AI is bounded | Proposal excludes precise/raw data, is stale-safe, cancellable, reviewable, and has deterministic fallback. |
| Release works | Archive/TestFlight install preserves usage descriptions, background capability, and physical transition behavior. |

The [Core Location route worksheet](../50-capability-recipes/162-swiftui-core-location-clmonitor-condition-review-route.md), [design review](../21-design-deep-dives/159-swiftui-core-location-clmonitor-condition-review-design.md), [proof matrix](../60-verification/156-swiftui-core-location-clmonitor-condition-proof-matrix.md), and [recipes](../70-code-recipes/174-swiftui-core-location-clmonitor-condition-review-recipes.md) make these claims repeatable.

## Sources

- [Core Location](https://developer.apple.com/documentation/corelocation)
- [CLMonitor actor](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v)
- [CLMonitor.Event](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/event)
- [CLMonitor.Events](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/events-swift.struct)
- [CLMonitor.Record](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/record)
- [CLMonitor.Event.State](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/event/state-swift.typealias)
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
