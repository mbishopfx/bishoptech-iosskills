# SwiftUI Core Location `CLMonitor` condition route worksheet

Use this worksheet before implementing a geofence or beacon-condition feature with modern Core Location. It separates condition monitoring from continuous location updates, MapKit visualization, and location-history analytics.

Related references:

- [Core Location `CLMonitor` review](../42-framework-deep-dives/131-swiftui-core-location-clmonitor-condition-review.md)
- [Core Location condition design review](../21-design-deep-dives/159-swiftui-core-location-clmonitor-condition-review-design.md)
- [Core Location condition proof matrix](../60-verification/156-swiftui-core-location-clmonitor-condition-proof-matrix.md)
- [Core Location condition code recipes](../70-code-recipes/174-swiftui-core-location-clmonitor-condition-review-recipes.md)

## Route record

| Field | Decision |
| --- | --- |
| Product outcome | `TBD` |
| Target / deployment | `TBD / iOS 26` |
| Condition lane | geographic / beacon / both: `TBD` |
| User-facing label | `TBD` |
| Location purpose | `TBD` |
| Authorization | when-in-use / always / service session: `TBD` |
| Accuracy behavior | full / reduced / no action: `TBD` |
| Usage descriptions | When In Use / Always / explicit session: `TBD` |
| Background capability | location updates / not needed / `TBD` |
| Monitor name | stable `CLMonitor` name: `TBD` |
| Condition identifiers | label -> identifier map: `TBD` |
| Geographic condition | center/radius: `TBD` |
| Beacon condition | UUID/major/minor: `TBD` |
| Initial assumed state | `TBD` |
| Event consumer | one task / actor adapter: `TBD` |
| Recreate policy | launch/background/reboot-unlock: `TBD` |
| Condition budget | active count / prioritization: `TBD` |
| Action policy | local UI / notification / task / other: `TBD` |
| Map surface | overlay/list/accessibility summary: `TBD` |
| AI proposal | allowed input/output/review: `TBD` |
| Physical fixture | device/location/beacon/time: `TBD` |
| Release artifact | archive/TestFlight/production: `TBD` |

## Step 1: choose condition monitoring

- [ ] Confirm the product only needs entry/exit or beacon-identity transitions.
- [ ] Use live `CLLocationUpdate` only if continuous/current location is genuinely required.
- [ ] Define whether a map is explanatory or part of the action.
- [ ] Define whether the product stores a history; default to transition-only local state.
- [ ] Define the user action that follows a satisfied/unsatisfied event.

If the feature needs turn-by-turn navigation, continuous tracking, or a live trail, route it through the location-update/background design instead of stretching `CLMonitor` into a telemetry stream.

## Step 2: authorization and purpose

1. Explain the location action before showing a permission sheet.
2. Choose when-in-use versus always based on the actual background requirement.
3. Configure the exact Info.plist usage descriptions.
4. Decide whether the modern `CLServiceSession` should be explicit.
5. Observe authorization, accuracy, restriction, and service-session diagnostics.
6. Provide Settings recovery without claiming the monitor is active.

Authorization record:

```text
authorizationRevision: UUID
authorizationState: app-owned semantic state
accuracyAuthorization: full/reduced
serviceSessionDiagnostic: String
promptShownAt: Date?
```

## Step 3: stable monitor and condition manifest

```text
monitor name: com.example.app.location-conditions
conditions:
  studio: geographic, 200m
  museum-entrance: beacon, UUID + major
policy revision: UUID
```

- [ ] Create the actor with a stable name.
- [ ] Recreate it with the same name after relaunch.
- [ ] Give every condition an app-owned stable identifier.
- [ ] Reconcile the persisted manifest with `monitor.identifiers`.
- [ ] Use `record(for:)` to recover the latest event state.
- [ ] Remove disabled conditions explicitly.
- [ ] Do not use a monitor identifier as a user or location-history identity.

## Step 4: geographic condition

- [ ] Choose center coordinate from an intentional user action.
- [ ] Choose radius based on the user’s task and document its limits.
- [ ] Show the radius as a visual explanation with a text equivalent.
- [ ] Record the label/purpose, not a broad location history.
- [ ] Test inside, outside, boundary, reduced accuracy, denied authorization, and device movement.
- [ ] Test after app termination, relaunch, reboot, and unlock.

Do not silently request a large radius or claim that a map circle equals a precise physical boundary.

## Step 5: beacon condition

- [ ] Require the UUID.
- [ ] Treat major/minor as optional wildcard refinements only when intended.
- [ ] Document the physical beacon placement and expected proximity.
- [ ] Test unavailable beacon, duplicate IDs, signal changes, and background delivery.
- [ ] Keep raw beacon identity out of general analytics and user-facing copy.

## Step 6: event stream and diagnostics

- [ ] Start exactly one event-consumer task per monitor generation.
- [ ] Keep iterating `monitor.events` for the lifetime of the route.
- [ ] Handle satisfied, unsatisfied, unknown, and unmonitored states.
- [ ] Handle authorization/accuracy/limit/unsupported/insufficient-use/persistence/service-session flags.
- [ ] Use event date and identifier to update app-owned state.
- [ ] Inspect `refinement` when the condition hierarchy needs it.
- [ ] Make downstream actions idempotent.
- [ ] Cancel the task when the feature is intentionally removed.

Do not treat an empty event stream as proof of “not at the place.” A diagnostic flag or an unstarted/recreated monitor may explain the absence.

## Step 7: condition budget and recovery

Core Location documents a maximum of 20 conditions of any type per app. Define a prioritization policy:

- pinned user favorites first;
- currently active workflow next;
- inactive or expired conditions last;
- explicit removal when the budget is full; and
- an explanation before a condition is not registered.

Recovery fixtures:

```text
authorization denied -> show Settings recovery
reduced accuracy -> show limited state and continue only if policy allows
condition limit -> prioritize/remove, do not replace silently
persistence unavailable -> retry/reconcile with monitor identifiers
app terminated -> recreate monitor at launch
device rebooted -> wait for unlock, recreate monitor, resume events
```

## Step 8: SwiftUI/MapKit bridge

- [ ] Keep monitor/actor operations outside `body`.
- [ ] Project event state into an `@Observable` main-actor model.
- [ ] Use a map/list/summary combination.
- [ ] Keep precise coordinates out of default logs and status cards.
- [ ] Use Liquid Glass for app-owned add/edit/status controls only.
- [ ] Preserve focus after permission sheets and background re-entry.
- [ ] Provide a list equivalent for map-only content.

## Step 9: AI action proposal

Pass only app-owned, coarse context by default:

```text
place label + event direction + user-selected action policy
        -> typed proposal
        -> hard allowlist and stale check
        -> review
        -> local action
```

- [ ] Exclude raw coordinates, beacon UUIDs, and location history unless separately approved.
- [ ] Require explicit review for notifications or external effects.
- [ ] Invalidate on new event/condition/authorization revision.
- [ ] Stop generation on screen exit or user cancel.
- [ ] Provide deterministic fallback.

## Step 10: evidence package

- [ ] Info.plist usage descriptions and background capability.
- [ ] Service-session/authorization/accuracy diagnostics.
- [ ] Stable monitor and condition manifest.
- [ ] `identifiers` and `record(for:)` reconciliation.
- [ ] Physical geographic transition evidence.
- [ ] Physical beacon transition evidence where applicable.
- [ ] Background relaunch and reboot/unlock evidence.
- [ ] 20-condition limit/prioritization evidence.
- [ ] SwiftUI/map/accessibility and Liquid Glass variants.
- [ ] AI data exclusion, stale, cancellation, review, and fallback tests.
- [ ] Archive/TestFlight physical retest.

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
