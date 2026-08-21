# SwiftUI EnergyKit load-event and historical-insight route

Use this route when an iOS 26 or iPadOS 26 app needs to connect a real EV charger or smart thermostat to Apple’s EnergyKit guidance, load-event, Home, or historical-insight surfaces. The earlier [EnergyKit guidance and load-event route](46-energykit-guidance-and-load-event-route.md) is the broad capability entry point. This route is the narrower implementation worksheet for session continuity, EV status snapshots, HVAC transitions, event acceptance, and delayed insight processing.

The route stops at the first missing prerequisite. A guidance preview can continue without a physical device; a submitted load event cannot honestly be presented without validated telemetry; a Home projection cannot be called complete without system evidence.

## 1. Define the outcome contract

Write one sentence:

> A person wants to [charge an EV / reduce HVAC demand / understand activity / inspect history] at [selected Home/device] so [specific outcome], while retaining [deadline, comfort, safety, or manual control].

Then choose the smallest route:

| Outcome | Required route |
| --- | --- |
| Explain a possible schedule | Existing product data plus optional on-device AI |
| Use grid guidance for EV | EnergyKit base entitlement, venue, shift guidance, deterministic scheduler |
| Use grid guidance for HVAC | EnergyKit base entitlement, venue, reduce guidance, deterministic comfort policy |
| Report EV energy flow | LoadEvents entitlement, ElectricVehicleLoadEvent, physical EV telemetry |
| Explain EV plugged/active/idle state | ElectricVehicleStatusEvent plus optional session identifier |
| Report HVAC electrical activity | LoadEvents entitlement, ElectricHVACLoadEvent, controller telemetry |
| Show Home energy activity | Base plus LoadEvents entitlement and accepted event submissions |
| Read historical energy context | Valid event history, ElectricityInsightQuery, ElectricityInsightService |

Do not add the Home projection just to make an app feel more Apple-like. Add it when the product outcome genuinely requires Apple Home energy history or system insight.

## 2. Preflight the target

Record this worksheet before implementation:

| Field | Decision |
| --- | --- |
| Xcode and SDK | Exact version used for compilation |
| Deployment target | iOS 26, iPadOS 26, or both |
| Base capability | com.apple.developer.energykit |
| LoadEvents capability | com.apple.developer.energykit.loadevents-experience or not used |
| Region | Contiguous-U.S. eligibility and physical test location |
| Home account | Test account with a configured Home |
| Venue | Person-selected EnergyVenue |
| Device | EV/charger or HVAC model and controller path |
| Telemetry | Source, units, cadence, clock, and observed-state meaning |
| Sessions | Imported/exported EV rules or HVAC transition rules |
| Insight | Query range, granularity, options, and direction |
| AI | Disabled, explanation-only, or typed proposal review |
| Privacy | Local retention, Home visibility, backend, logs, model input |
| Release | Final SDK, signed archive, TestFlight/device, App Review metadata |

An entitlement file and a successful preview are not signed-target proof. Inspect the archived executable and verify every target that imports or exposes the feature.

## 3. Choose the ownership graph

Keep system data, product policy, physical control, and generated language separate:

~~~text
EnergyFeatureModel
  -> VenueStore
  -> GuidanceStream
  -> ScheduleEngine
  -> UserApproval
  -> DeviceController
  -> TelemetryStore
  -> LoadEventBuilder
  -> EnergyVenue.submitEvents
  -> InsightStore
  -> optional ExplanationModel
~~~

| Component | Owns | Must not silently own |
| --- | --- | --- |
| VenueStore | Selected Home/venue identity and display mapping | A fallback Home choice |
| GuidanceStream | Latest values, interval, token, freshness | A physical device command |
| ScheduleEngine | Feasible candidate windows | AI prose or safety overrides |
| UserApproval | Explicit approval/override revision | Background approval inferred from a notification |
| DeviceController | Charger/HVAC protocol and observed state | EnergyKit forecast truth |
| TelemetryStore | Raw/product measurements and provenance | Fabricated values for missing fields |
| LoadEventBuilder | Event order, units, sessions, venue/device binding | Repairing a contradictory physical history silently |
| InsightStore | Query provenance and returned records | A live meter or bill guarantee |
| ExplanationModel | Plain language for typed facts | Event submission or device control |

## 4. Gate by build and regional availability

Use a visible capability state:

~~~text
notAvailable
  -> baseEnergyKitReady
  -> loadEventsReady
  -> venueReady
  -> guidanceReady
  -> physicalDeviceReady
  -> insightsReady
~~~

The app can still offer product-owned manual scheduling or a local activity view when EnergyKit is unavailable. It must not label those alternatives as Apple guidance or Home history.

Handle:

- unsupportedRegion;
- missing or denied permission;
- locationServicesDenied;
- empty or unavailable venue;
- serviceUnavailable;
- guidanceUnavailable;
- beta/API availability changes.

The fallback should preserve user control:

| Failure | Fallback |
| --- | --- |
| Unsupported region | Manual schedule or ordinary device control, clearly labeled |
| No venue | Let the person configure the device locally or retry Home selection |
| Guidance unavailable | Keep the prior proposal visibly stale or require manual choice |
| LoadEvents unavailable | Keep app-owned activity status without claiming Home presentation |
| Insight not ready | Show processing/no-data state and preserve query provenance |

## 5. Route A: venue and guidance

1. Load EnergyVenue.venues().
2. Show the available Home names and device association.
3. Require an explicit selection.
4. Revalidate the selected venue before each sensitive operation.
5. Select shift for EV or reduce for HVAC.
6. Start the ElectricityGuidance.Service AsyncSequence.
7. Retain interval, values, suggested action, venue ID, token, and fetched time.
8. Cancel the stream when the selected device or venue changes.
9. Pass only typed, validated candidate windows to the scheduler.

The location overload is a different product route. Apple’s documentation says the location form does not include cost information; never give it the same “rate-aware” copy as venue guidance.

The stream result is not a command:

~~~text
guidance received
  -> candidate windows
  -> feasible schedule
  -> person reviews
  -> person approves
  -> device controller acts
~~~

## 6. Route B: deterministic schedule review

For an EV, collect:

- state of charge;
- target state of charge;
- battery/charger constraints;
- expected duration;
- deadline;
- device availability;
- user override.

For HVAC, collect:

- current and target temperature;
- comfort range;
- equipment stage/limits;
- proposed duration;
- freeze/safety rules;
- manual override.

The scheduler must reject:

- windows in the past;
- windows that cannot meet the deadline;
- invalid or stale guidance;
- missing device constraints;
- comfort or safety violations.

An AI model may explain or rank already-valid candidates. It cannot create missing grid values or replace deterministic feasibility checks.

## 7. Route C: EV load-event sessions

Represent each physical energy direction as a session:

~~~text
device connected
  -> begin
  -> active measurements
  -> meaningful transition events
  -> end
  -> closed
~~~

Use one stable session identifier for the continuous flow. For V2G/V2H, use a separate session for imported and exported flow.

Before constructing an event:

1. confirm the selected EnergyVenue;
2. confirm the EnergyKit device identity;
3. confirm the guidance token came from this venue/device decision;
4. validate state-of-charge range;
5. validate imported/exported direction;
6. convert power to milliwatts and cumulative energy to milliwatt-hours;
7. validate the begin/active/end order;
8. validate cumulative energy monotonicity;
9. apply documented zero-power/zero-energy rules for begin/end;
10. attach observed timestamp and product telemetry provenance.

Stable charging can use bounded periodic samples, while changes in power, pause, target, or user action can justify an additional event. Do not submit every sensor tick.

## 8. Route D: EV status snapshots

Create a status event when the product needs a point-in-time explanation:

- charger plugged in;
- charger unplugged;
- charging active with the documented active reason;
- charging idle with the documented idle reason;
- current state of charge and energy;
- optional estimated range or charging target;
- optional session identifier for correlation.

Use the status route to answer “what is the vehicle doing now?” Use the load session route to answer “what energy flow occurred over time?”

The UI should never infer active charging from:

- a scheduled start time;
- a connected cable alone;
- a successful API command;
- an AI-generated summary.

Require device telemetry or a documented controller state.

## 9. Route E: HVAC transition events

Build ElectricHVACLoadEvent values only from meaningful controller transitions:

- heating or cooling stage changes;
- person-initiated setpoint action;
- pause or resume;
- transition into or out of active electrical load;
- other transitions Apple’s current event contract supports.

Keep high-frequency controller telemetry in the product store. Reduce it to EnergyKit events using a debounced state machine. The EnergyKit event is a system-facing energy projection, not the full HVAC diagnostic record.

Before submit:

- confirm the session is open or being closed correctly;
- confirm the measurement matches the event type;
- confirm device and venue identity;
- confirm the timestamp is monotonic for the session;
- suppress duplicate transitions;
- do not invent energy when the controller did not measure it.

## 10. Route F: submission and recovery

Use a durable submission record:

| State | Meaning |
| --- | --- |
| Built | Local event exists and has not been submitted |
| Validated | Session/order/measurement checks passed |
| Submitting | One attempt is in flight |
| Accepted | EnergyKit returned success |
| Processing | Home/insight system may still be processing |
| Invalid | Event must be corrected or discarded |
| Rate limited | Retry after bounded backoff |
| Venue unavailable | Revalidate selection |
| Service unavailable | Retry without changing the event identity |

Never create a second begin or end event merely because a network timeout obscured the result. Reconcile the local submission state and use an idempotent policy.

On EnergyKitError:

- invalidLoadEvent: surface a correction state and preserve diagnostic context;
- rateLimitExceeded: back off and deduplicate;
- venueUnavailable: return to venue validation;
- permissionDenied: explain the user action needed;
- locationServicesDenied: show the system settings path if appropriate;
- serviceUnavailable: retry with freshness labels;
- guidanceUnavailable: retain a stale label or ask for manual scheduling;
- unsupportedRegion: do not retry indefinitely.

## 11. Route G: Home projection

Add the LoadEvents entitlement only when the Home app energy experience is a real product requirement. Then:

1. disclose that accepted events may appear in Home;
2. use a meaningful device name;
3. submit only validated EV/HVAC events;
4. show accepted versus processing states;
5. avoid promising immediate Home presentation;
6. test the shared Home/account behavior with the intended physical device;
7. keep the app-owned activity timeline separate from the system projection.

The signed entitlement is a release gate. The Home screenshot is a separate system-surface gate. Neither proves physical charging or HVAC operation.

## 12. Route H: historical insights

Build an ElectricityInsightQuery with:

- explicit options;
- named DateInterval;
- hourly, daily, or weekly granularity;
- imported or exported flow direction.

Query through ElectricityInsightService and retain:

- device and venue;
- query parameters;
- returned record range;
- total energy or runtime;
- cleanliness/tariff categories;
- data freshness;
- no-data/processing state.

The correct UI query state is:

~~~text
noEvents
  -> eventsAccepted
  -> processing
  -> insightAvailable
  -> queryChanged
  -> processing
~~~

Do not call a current guidance stream an insight. Do not call a historical insight a real-time meter. Do not show tariff as zero when the record has no tariff data.

## 13. Optional on-device AI route

Use Foundation Models only after the deterministic route has produced typed facts:

~~~text
typed guidance/insight facts
  -> redaction/input audit
  -> local explanation or candidate ranking
  -> user review
  -> no automatic event/device side effect
~~~

Good AI actions:

- explain the selected window;
- summarize an insight record;
- translate a preference into a typed deadline or comfort constraint;
- draft recovery copy from a known error;
- rank feasible candidates.

Block the model if it:

- invents a rating or tariff;
- claims activity not observed by telemetry;
- changes safety/comfort limits;
- submits an event;
- chooses a Home;
- sends raw household history to an external service;
- issues a physical command without explicit app approval.

## 14. SwiftUI route composition

Use a shared observation model for:

- build/capability state;
- venue;
- guidance;
- schedule proposal;
- device state;
- event submission;
- insight query;
- explanation state.

The view hierarchy should observe the state; it should not construct EnergyVenue, start an unbounded guidance stream, or submit events from a body recomputation. Tie stream tasks to the selected venue/device identity and cancel old generations.

Recommended screens:

1. Energy capability/region explanation;
2. Home venue and device selection;
3. guidance and schedule review;
4. active EV/HVAC session;
5. event/Home status;
6. historical insights;
7. privacy and data controls.

Use Liquid Glass for action groups and navigation while keeping telemetry and chart content readable. Use native controls with labels rather than custom tap-only translucent shapes.

## 15. Proof gates

Do not advance a route until the matching evidence exists:

| Gate | Evidence |
| --- | --- |
| Source | Official Apple API/entitlement page and current SDK |
| Compile | Named target builds with availability checks |
| Entitlement | Signed archive inspection |
| Venue | Physical eligible Home and explicit selection |
| Guidance | Live venue stream with token/freshness |
| Schedule | Deterministic candidate test and user approval |
| Device | Physical telemetry or controller evidence |
| Event | Validated session/status/HVAC conversion |
| Submit | EnergyVenue.submitEvents success |
| Home | Actual system presentation/process evidence |
| Insight | Historical query returns a record |
| AI | Model/input audit and refusal fixtures |
| Accessibility | Dynamic Type, VoiceOver, Reduce Motion, alternate input |
| Release | Archive, TestFlight/device, privacy, entitlement, region, App Review checks |

## Sources

- [EnergyKit](https://developer.apple.com/documentation/EnergyKit)
- [Introducing EnergyKit](https://developer.apple.com/energykit/)
- [Optimize home electricity usage with EnergyKit](https://developer.apple.com/videos/play/wwdc2025/257/)
- [EnergyVenue](https://developer.apple.com/documentation/energykit/energyvenue)
- [ElectricityGuidance](https://developer.apple.com/documentation/energykit/electricityguidance)
- [ElectricityGuidance.Service](https://developer.apple.com/documentation/energykit/electricityguidance/service)
- [ElectricalLoadEventProtocol](https://developer.apple.com/documentation/energykit/electricalloadeventprotocol)
- [ElectricVehicleLoadEvent](https://developer.apple.com/documentation/energykit/electricvehicleloadevent)
- [ElectricVehicleStatusEvent](https://developer.apple.com/documentation/energykit/electricvehiclestatusevent)
- [ElectricHVACLoadEvent](https://developer.apple.com/documentation/energykit/electrichvacloadevent)
- [ElectricityInsightQuery](https://developer.apple.com/documentation/energykit/electricityinsightquery)
- [ElectricityInsightService](https://developer.apple.com/documentation/energykit/electricityinsightservice)
- [EnergyKitError](https://developer.apple.com/documentation/energykit/energykiterror)
- [EnergyKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit)
- [EnergyKit LoadEvents entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit.loadevents-experience)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
