# EnergyKit Guidance and Load-Event Route

Use this route when an EV charging or smart-thermostat app needs Apple’s Home energy venue, grid guidance, load-event processing, or historical electricity insights. Keep the framework’s recommendation, the product’s physical device control, and the user-facing explanation as separate stages.

## Outcome contract

The person can:

1. select the correct Home energy venue;
2. understand whether EnergyKit is available in this build and region;
3. receive current guidance for a device-specific shift or reduce task;
4. review and edit a feasible schedule;
5. approve or override the schedule;
6. observe the physical device result;
7. submit valid EV/HVAC load events;
8. see when Home presentation or historical insight is available;
9. recover without treating stale guidance or missing data as a live forecast.

## Choose the smallest route

| Need | Minimum route |
| --- | --- |
| Home venue and grid guidance | EnergyKit base capability, EnergyVenue, ElectricityGuidance |
| EV shift schedule | Base capability, venue guidance with suggestedAction shift, product EV telemetry/control |
| HVAC reduce schedule | Base capability, venue guidance with suggestedAction reduce, product HVAC comfort/control |
| Home app energy experience | Base plus EnergyKit LoadEvents Entitlement, EV/HVAC events, event submission |
| Historical energy insight | Load events first, ElectricityInsightQuery, ElectricityInsightService |
| Local explanation of schedule | Deterministic schedule plus optional on-device AI explanation |

Do not add EnergyKit just to build a generic home energy chart. Use ordinary product telemetry for a private chart when Home venues, guidance, and Home integration are not required.

## Project and entitlement gate

Record:

- Xcode/SDK and iOS/iPadOS deployment target;
- base entitlement com.apple.developer.energykit;
- optional LoadEvents entitlement com.apple.developer.energykit.loadevents-experience;
- target membership for every executable using EnergyKit;
- region and Home app requirements;
- device protocol for the EV charger or HVAC system;
- venue/device identifier storage policy;
- event sampling and retry policy;
- privacy and Home sharing explanation;
- beta API review and final-release recheck.

The LoadEvents capability depends on the base EnergyKit capability. Inspect the signed archive and do not infer entitlement presence from a source file.

## Ownership graph

~~~text
SwiftUI schedule surface
  -> EnergyCoordinator
      -> EnergyVenue / ElectricityGuidance
      -> deterministic ScheduleEngine
      -> EV/HVAC DeviceController
      -> LoadEventBuilder
      -> EnergyVenue.submitEvents
      -> ElectricityInsightService
  -> optional on-device AI explanation
~~~

| Layer | Owns | Does not own |
| --- | --- | --- |
| SwiftUI | Goal, venue choice, schedule review, accessibility, approval | Forecast truth or physical action |
| EnergyCoordinator | Venue/guidance/event/insight orchestration and cancellation | Charger protocol or HVAC safety limits |
| ScheduleEngine | Feasible candidate windows and deterministic constraints | AI prose or system permission |
| DeviceController | Device command and observed telemetry | EnergyKit forecast interpretation |
| LoadEventBuilder | Correct session/order/units and event provenance | Fabricating missing measurements |
| InsightStore | Query range, freshness, records, and deletion policy | Real-time meter truth |
| AI Explanation | Plain-language explanation of typed data | Forecast creation, device action, event mutation |

## State machine

~~~text
build:
  unavailable -> baseReady -> loadEventsReady

venue:
  unknown -> loading -> selected
  loading -> empty | unavailable | permissionDenied

guidance:
  notRequested -> loading -> ready
  loading -> unsupportedRegion | unavailable | failed
  ready -> stale -> loading

schedule:
  noDraft -> draft -> approved | edited | overridden
  draft -> infeasible

device:
  unknown -> commandRequested -> actionObserved
  commandRequested -> notObserved | failed

events:
  none -> begin -> active -> end
  any -> rejected | accepted | rateLimited

insights:
  noQuery -> loading -> records | noData | failed
~~~

Keep build, venue, guidance, schedule, physical device, event, and insight state as separate values. A guidance result cannot move the device to “charging.”

## Venue onboarding

1. Explain that venues correspond to Homes configured in Apple Home.
2. Load EnergyVenue.venues().
3. Show all available homes with user-facing names.
4. Let the person choose the venue for this charger or thermostat.
5. Persist only the venue identifier and an approved display mapping.
6. Associate the product device identifier with the selected venue.
7. Refresh the venue if it becomes unavailable.

If the product has multiple charging locations, create a separate local mapping per venue. Never silently switch a vehicle to the first returned venue.

## Request guidance

For a venue:

1. Select shift or reduce based on the product task.
2. Create ElectricityGuidance.Query.
3. Stream ElectricityGuidance.sharedService.guidance(using:at:).
4. Store the latest guidance with interval, venue ID, token, options, and freshness.
5. Cancel the stream when the selected venue/device changes.
6. Recompute the schedule when new guidance arrives.

For a location-only query, use the CLLocation overload and label the result as guidance without cost information. Do not mix it with the venue route’s tariff claims.

The guidance stream may update over time. A schedule should record which guidance token and interval informed the approval so the product can explain and reconcile later.

## Deterministic schedule engine

The schedule engine accepts:

~~~text
ScheduleInput:
  venueID
  deviceID
  suggestedAction
  guidanceValues
  guidanceToken
  now
  deadline
  stateOfCharge or comfortState
  devicePowerLimit
  requiredEnergy or reductionBudget
  userConstraints
  fallbackPolicy
~~~

The engine returns:

~~~text
ScheduleResult:
  candidateWindows
  selectedWindow
  infeasibleReason
  guidanceFreshAt
  missingInputs
  requiresApproval
~~~

For shift, choose a feasible window that meets the deadline and charger limits. For reduce, apply comfort/safety rules before ranking guidance values. If no window is feasible, say why and offer start-now/manual control.

Do not call the selected window “optimal” unless the product defines the objective and validates all required inputs. “Best among the available candidate windows” is often more accurate.

## EV load-event route

Track one charging session:

1. get guidance for the device/venue;
2. create a begin session with appropriate zero-power/zero-energy values;
3. create active events at the documented cadence while stable;
4. create additional events for pause, resume, power changes, or person actions;
5. create an end event with final cumulative energy and stopped power;
6. submit promptly through EnergyVenue.submitEvents;
7. persist submission result and retry only with an idempotent event policy.

If the vehicle can export energy, use separate sessions for charging and discharging. Do not merge imported and exported energy into one directionless total.

## HVAC load-event route

Submit a load event when:

- heating or cooling becomes active;
- a stage changes;
- the person initiates a change;
- the device pauses or becomes idle;
- the current guidance-driven reduction state changes.

Avoid event spam from high-frequency thermostat samples. The event record should represent meaningful energy-state transitions.

## Submission and retry

Build event batches only when event order and session identity remain clear. Validate:

- venue matches the selected EnergyVenue;
- device requested the corresponding guidance;
- guidance token belongs to the device/phone/venue route;
- begin/active/end order is valid;
- cumulative values are monotonic where required;
- units and signs are valid;
- event timestamps are sane;
- device ID/name is stable.

Handle:

| Error | Route |
| --- | --- |
| invalidLoadEvent | Inspect the event builder; do not retry unchanged |
| rateLimitExceeded | Deduplicate, back off, and retry later |
| venueUnavailable | Refresh venue and ask for selection |
| permissionDenied | Show system/privacy recovery |
| serviceUnavailable | Queue a bounded retry |
| guidanceUnavailable | Use manual/fallback schedule |
| unsupportedRegion | Keep non-EnergyKit product route |

The app should report “accepted” only after EnergyKit accepts the submission. Home app presentation is a later system state.

## Historical insight route

1. Define a date range and granularity.
2. Choose cleanliness/tariff options only when they are meaningful for the venue.
3. Set electricity flow direction.
4. Call ElectricityInsightService.shared.
5. Consume the returned AsyncStream with cancellation.
6. Record the query and freshness.
7. Render available breakdowns with a no-data state.

Insight records are historical. A new event may take time to appear. Never use a missing recent record to claim that the device did not consume energy.

## Home app route

When LoadEvents is enabled:

- choose a clear device name;
- explain that load events may be visible in Home;
- show app state separately from Home presentation;
- include event provenance in support diagnostics without raw telemetry;
- respect Home sharing and deletion behavior;
- avoid rebuilding the Home app’s complete analytics surface.

The app can offer a link or explanation to the Home app but should not claim that a local row is already visible there.

## On-device AI route

Provide only redacted typed input:

~~~text
EnergyExplanationInput:
  venueName
  deviceName
  suggestedAction
  selectedWindow
  deadline
  guidanceUpdatedAt
  rateDataAvailable
  missingInputs
  physicalActionObserved
~~~

Return a proposal:

~~~text
EnergyExplanation:
  summary
  assumptions
  missingData
  nextAction
  savingsClaimAllowed: false
  requiresApproval: true
~~~

The scheduler remains deterministic. The AI does not create guidance, invent rates, submit events, or start a charger/HVAC system. It may explain “why this window” and summarize a historical record with its date range.

## Minimum proof sequence

1. Compile base EnergyKit target at iOS 26/iPadOS 26.
2. Add and inspect base entitlement.
3. Verify the target’s region and Home venue prerequisites.
4. Discover one and multiple venues.
5. Stream guidance for shift and reduce.
6. Handle unsupported region, permission, venue, guidance, and service errors.
7. Generate and review one deterministic schedule.
8. Observe a real EV/HVAC action.
9. Build and submit valid begin/active/end or HVAC transition events.
10. Test invalid event, rate limit, retry, and cancellation.
11. Add LoadEvents capability and verify the signed target.
12. Observe Home app activity/processing if the release route supports it.
13. Query historical insights after data processing.

## Sources

- [EnergyKit](https://developer.apple.com/documentation/EnergyKit)
- [Introducing EnergyKit](https://developer.apple.com/energykit/)
- [Optimizing home electricity usage](https://developer.apple.com/documentation/EnergyKit/optimizing-home-electricity-usage)
- [Providing charging history for electric vehicles](https://developer.apple.com/documentation/EnergyKit/providing-informative-charging-history-for-electric-vehicles)
- [EnergyVenue](https://developer.apple.com/documentation/energykit/energyvenue)
- [ElectricityGuidance](https://developer.apple.com/documentation/energykit/electricityguidance)
- [ElectricityGuidance.Service](https://developer.apple.com/documentation/energykit/electricityguidance/service)
- [ElectricVehicleLoadEvent](https://developer.apple.com/documentation/energykit/electricvehicleloadevent)
- [ElectricHVACLoadEvent](https://developer.apple.com/documentation/energykit/electrichvacloadevent)
- [ElectricalLoadEventProtocol](https://developer.apple.com/documentation/energykit/electricalloadeventprotocol)
- [ElectricityInsightService](https://developer.apple.com/documentation/energykit/electricityinsightservice)
- [EnergyKitError](https://developer.apple.com/documentation/energykit/energykiterror)
- [EnergyKit Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit)
- [EnergyKit LoadEvents Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit.loadevents-experience)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
