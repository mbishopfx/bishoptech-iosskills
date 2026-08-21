# EnergyKit and Home Energy Guidance

EnergyKit is an iOS 26 and iPadOS 26 route for apps that manage residential electricity usage, especially electric-vehicle charging and smart thermostats. It provides grid guidance, accepts electrical load events, and can provide historical energy insights. With the LoadEvents entitlement, the Home app can display activity logs, charts, and trend notifications for the events an app submits.

This is a focused platform integration, not a generic energy dashboard API. Apple’s current developer material says EnergyKit is designed for EV charging and smart thermostat apps, requires iOS 26 or iPadOS 26 or later, and is available only in the contiguous United States. The framework and LoadEvents capability are marked beta in the current documentation, so build against the final SDK and re-verify every signature and entitlement before distribution.

## What EnergyKit owns

| Product responsibility | EnergyKit responsibility | Keep separate |
| --- | --- | --- |
| Decide whether a vehicle or HVAC device may shift/reduce usage | Provide guidance about cleaner or less expensive periods | Hardware control, user safety, comfort, charging protocol, and utility compliance |
| Identify a Home location | Expose EnergyVenue values for homes configured in the Home app | Arbitrary GPS location or a custom “home” database |
| Report electrical activity | Validate and process EV/HVAC load events | Meter accuracy, charger telemetry, HVAC sensor calibration, and durable device truth |
| Show historical energy context | Return electricity insight streams and Home app presentation | A guaranteed bill, emissions accounting, or real-time meter |
| Explain the result | Supply structured records and guidance values | AI-generated claims about savings or environmental impact |

The correct mental model is:

~~~text
Home app venue -> EnergyKit guidance -> product schedule/decision
product telemetry -> load events -> EnergyKit insights/Home app
~~~

EnergyKit can inform a device schedule. It does not itself turn a charger or thermostat on, verify that a physical action happened, or guarantee a cost or carbon outcome.

## Entitlements and target gates

The base EnergyKit Entitlement is the Boolean key com.apple.developer.energykit. The EnergyKit LoadEvents Entitlement is the Boolean key com.apple.developer.energykit.loadevents-experience. Apple’s entitlement documentation says the LoadEvents capability requires the base EnergyKit capability as well.

Model the build states:

| Build state | Allowed surface |
| --- | --- |
| No EnergyKit capability | Explain that this build cannot access EnergyKit |
| Base entitlement only | Venue discovery, guidance, and product-owned schedule/decision route as supported by the current SDK |
| Base plus LoadEvents entitlement | Load event submission and Home app energy presentation route |
| Final SDK and approved release configuration | Re-verify beta/API/region/entitlement conditions before distribution |

Inspect the signed archive. An .entitlements source file or Xcode capability checkbox does not prove that the executable carries the intended value. If the app has a widget, extension, or companion target that touches EnergyKit, verify target membership and entitlement placement separately.

## Energy venues

An EnergyVenue represents a physical site associated with a Home configured in the Home app. The current API exposes:

- EnergyVenue.venues() to retrieve available venues;
- EnergyVenue.venue(for:) to retrieve a venue by identifier;
- EnergyVenue.venue(matchingHomeUniqueIdentifier:) to resolve a HomeKit identifier;
- id and name for the venue;
- submitEvents for typed electrical load events.

Persist the venue identifier and a user-approved display name, not a fabricated address or arbitrary GPS coordinate. A person may have multiple homes or charging locations; let them select the venue intentionally and keep the selected venue attached to the schedule and telemetry.

The venue list can be empty or fail because Home configuration, permissions, region, service availability, or entitlement state is not ready. Do not treat a missing venue as “no energy usage.”

## Electricity guidance

ElectricityGuidance.Service provides an AsyncSequence of forecasts. Use ElectricityGuidance.Query with a SuggestedAction:

- shift for a task whose time can move while the total energy is broadly similar, such as EV charging;
- reduce for a task that can lower or avoid energy usage, such as a thermostat reduction decision.

The current guidance includes:

- energyVenueID;
- interval;
- guidanceToken;
- values for time intervals;
- normalized values and options.

Apple’s current sample explains that lower ratings indicate cleaner, less expensive electricity. Rate-plan information is available only when the relevant utility/home data exists. A guidance value is a recommendation input, not a promise that a chosen period is always cheapest or cleanest.

There are two guidance forms:

| API route | When to use |
| --- | --- |
| guidance(using:at:) | A Home energy venue with venue-specific cost information when available |
| guidance(using:for:) | A CLLocation-based route without cost information incorporated |

The venue route is the normal Home energy workflow. The location route has different privacy and data semantics; do not present it as a utility-rate result.

The stream can continue indefinitely and Apple’s sample notes that updates often arrive hourly but may arrive more frequently when conditions change. The app should cancel the stream when the feature or selected venue changes, and store only the latest guidance needed for the current scheduling decision.

## Schedule generation

The product owns the physical scheduling algorithm. A minimal EV schedule needs:

- current state of charge;
- target state of charge;
- battery capacity;
- charger power and limitations;
- expected charging duration;
- user’s deadline;
- vehicle/charger availability;
- current guidance values;
- a fallback when guidance is unavailable.

The algorithm should select the best feasible windows within the user’s constraints. It should not simply choose the lowest value without considering the deadline, charger rate, current state, or user override.

For HVAC:

- prefer a reduce strategy when comfort and safety rules allow;
- keep a hard minimum/maximum temperature policy outside the model;
- make the person’s target and override explicit;
- never let “cleaner” or “cheaper” override freeze protection, equipment limits, or safety behavior.

Show the schedule as a proposal:

> Charge by 7:00 AM. The proposed window uses the latest available guidance for this home. Your charger and vehicle may change the result.

The person should be able to start now, follow the proposed window, edit the deadline, or disable guidance.

## Guidance tokens and load events

The device that requests ElectricityGuidance must submit the corresponding load events. The guidance token is used to associate an event with the forecast that informed the decision. Keep the token bound to the phone/device and venue that retrieved it; do not assume it can be copied between devices.

For EV charging, Apple’s current guidance recommends:

- a begin event when a session starts;
- active events approximately every 15 minutes during stable charging;
- additional events for meaningful power changes, pauses, or user actions;
- an end event when charging finishes;
- separate sessions for charging and discharging in V2G/V2H scenarios.

For HVAC, submit events when the heating/cooling stage changes, the person initiates an action, or the unit moves between active and idle states. Do not emit a high-frequency event for every sensor tick.

The event lifecycle is:

~~~text
guidance retrieved
-> session begin
-> session active / meaningful transition
-> session end
-> venue.submitEvents
-> accepted / invalid / rate-limited / unavailable
~~~

EnergyKit validates event order and values. Apple’s current documentation names invalidLoadEvent and rateLimitExceeded among the failure cases. A rejected event is not energy telemetry proof and should not be counted as submitted.

## Electrical measurements

EV measurements include state of charge, electricity flow direction, instantaneous power, cumulative energy, and optional performance metrics. The current documentation describes power in milliwatts and energy in milliwatt-hours, with cumulative energy resetting for a new session. Use the framework’s units and validate:

- non-negative energy where required;
- zero power for a begin event before charging starts;
- zero power for an end event after charging stops;
- cumulative energy that does not move backward within one session;
- state-of-charge values within the documented 0–100 range;
- imported versus exported direction;
- stable device ID and meaningful device name.

Do not make a measurement more precise than the underlying charger or vehicle telemetry. If a device reports an estimate, label it as an estimate in the product’s own records.

## Home app integration

With the LoadEvents Entitlement, the Home app can display device names and energy context derived from EV/HVAC events. The current entitlement page describes activity logs, historical charts, and trend notifications. Apple’s EnergyKit pages state that load-event data is stored and synced with end-to-end encryption so that Apple cannot access it.

This integration changes the product boundary:

- the app should explain that submitted events may appear in the Home app;
- all people who share the associated Home may be able to see the load-event experience as documented;
- the app should provide a meaningful device name;
- the app does not need to recreate Home’s full historical charts;
- deleting EnergyKit data is a person-controlled Home/system concern that must be explained according to Apple’s current behavior.

Never promise that the Home app will show an event immediately. Submission, validation, processing, sync, and presentation are separate states.

## Historical insights

ElectricityInsightService is an actor with a shared instance. The current API can return an AsyncStream of:

- energy insights for a device using ElectricityInsightQuery;
- runtime insights for a device using ElectricityInsightQuery.

An insight query includes options such as cleanliness or tariff, a date range, granularity, and flow direction. A result is historical context after load events have been processed. It is not a live meter and not a guaranteed utility bill.

The UI should show:

- venue and device;
- query range and granularity;
- data freshness;
- whether tariff information was available;
- whether a cleanliness category was present;
- a “not enough data” state;
- a link to the schedule/telemetry provenance.

Avoid percentages that hide missing categories. If no tariff data exists, say “Rate data unavailable for this venue” rather than drawing a zero-cost chart.

## Region, privacy, and availability

Energy guidance is currently available only in the contiguous United States. The framework also exposes errors such as unsupportedRegion, locationServicesDenied, permissionDenied, venueUnavailable, guidanceUnavailable, serviceUnavailable, invalidLoadEvent, and rateLimitExceeded.

Treat region and permission as product states:

| State | Product response |
| --- | --- |
| unsupportedRegion | Keep manual scheduling and local telemetry available if the product supports it |
| locationServicesDenied | Explain why Home/venue resolution cannot continue; do not repeatedly prompt |
| permissionDenied | Preserve the person’s control and show Settings or alternative route |
| venueUnavailable | Refresh the Home/venue selection; do not silently use another home |
| guidanceUnavailable | Use the documented fallback schedule and label it |
| serviceUnavailable | Retry with backoff; do not show stale guidance as current |
| invalidLoadEvent | Fix the event contract; never blindly retry the same invalid payload |
| rateLimitExceeded | Back off and deduplicate events |

Energy usage can reveal routines, occupancy, charging behavior, and home activity. Minimize local retention, redact logs, keep device IDs stable only as required, and avoid uploading raw telemetry to an unrelated backend.

## On-device AI boundary

Good bounded AI tasks:

- explain an ElectricityGuidance schedule in plain language;
- summarize historical insights with the exact date range and missing-data caveats;
- convert a person’s natural-language preference into a typed deadline or comfort rule for review;
- draft a troubleshooting summary for missing venue/guidance/events;
- suggest an alternate schedule from deterministic candidate windows.

The model should not:

- invent grid forecasts or tariff values;
- claim a schedule guarantees savings or emissions reduction;
- override a person’s deadline, comfort, charging, or safety limits;
- infer occupancy or identity from energy events;
- send raw load telemetry to a model or external server without an explicit privacy decision;
- submit load events or change physical device state without user-approved deterministic code.

Use a typed schedule proposal:

~~~text
EnergyScheduleProposal:
  venueID
  deviceID
  suggestedAction
  startWindow
  endWindow
  reason
  guidanceFreshAt
  missingInputs
  requiresUserApproval
~~~

The scheduler validates feasibility. The model explains or ranks candidate windows. The device controller performs the physical action. EnergyKit receives telemetry after the action is observed.

## Proof boundary

Keep these claims separate:

- entitlement present;
- venue listed;
- guidance stream opened;
- current guidance received;
- schedule computed;
- person approved;
- charger/HVAC action requested;
- physical action observed;
- load event constructed;
- load event accepted;
- Home app presentation observed;
- historical insight returned;
- savings/cleanliness trend measured.

Simulator previews and fake measurements can prove layout and state handling. They cannot prove region eligibility, Home venues, current guidance, entitlement behavior, physical charging, HVAC operation, Home app sync, or insight quality.

## Sources

- [EnergyKit](https://developer.apple.com/documentation/EnergyKit)
- [Introducing EnergyKit](https://developer.apple.com/energykit/)
- [Optimizing home electricity usage](https://developer.apple.com/documentation/EnergyKit/optimizing-home-electricity-usage)
- [Providing charging history for electric vehicles](https://developer.apple.com/documentation/EnergyKit/providing-informative-charging-history-for-electric-vehicles)
- [ElectricityGuidance](https://developer.apple.com/documentation/energykit/electricityguidance)
- [ElectricityGuidance.Service](https://developer.apple.com/documentation/energykit/electricityguidance/service)
- [EnergyVenue](https://developer.apple.com/documentation/energykit/energyvenue)
- [ElectricVehicleLoadEvent](https://developer.apple.com/documentation/energykit/electricvehicleloadevent)
- [ElectricHVACLoadEvent](https://developer.apple.com/documentation/energykit/electrichvacloadevent)
- [ElectricityInsightService](https://developer.apple.com/documentation/energykit/electricityinsightservice)
- [EnergyKitError](https://developer.apple.com/documentation/energykit/energykiterror)
- [EnergyKit Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit)
- [EnergyKit LoadEvents Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit.loadevents-experience)
- [Introducing EnergyKit](https://developer.apple.com/energykit/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
