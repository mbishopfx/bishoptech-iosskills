# SwiftUI EnergyKit load events, status, and historical insight review

EnergyKit is a narrow iOS 26 and iPadOS 26 system route for residential electricity experiences. The existing [EnergyKit and Home energy guidance deep dive](23-energykit-and-home-energy-guidance.md) explains venue discovery, shift/reduce guidance, and the broad product boundary. This page extends that material into the event and insight layer: how an EV or HVAC app represents a real session, how point-in-time vehicle status complements a session event, how historical insight queries are scoped, and how the Home app becomes a separate system projection.

The correct architecture is:

~~~text
EnergyVenue
  -> ElectricityGuidance.Query
  -> deterministic schedule proposal
  -> person approval
  -> physical charger/HVAC command
  -> observed device telemetry
  -> typed load/status event
  -> EnergyVenue.submitEvents
  -> Home presentation and historical insight processing
~~~

EnergyKit can provide guidance, validate and process submitted energy events, and expose historical insight records. It does not turn a recommendation into a charger command, prove that an HVAC compressor ran, guarantee a utility rate, or make a generated explanation authoritative.

## 1. Availability and capability boundary

Apple’s current EnergyKit material describes the framework as an iOS 26/iPadOS 26 route designed for electric-vehicle charging and smart thermostat apps. Energy guidance is currently limited to the contiguous United States. The current documentation marks the framework and related APIs as beta, so every signature, entitlement, and availability annotation must be recompiled against the final SDK before release.

The base EnergyKit capability and the LoadEvents capability are separate:

| Build condition | What it means |
| --- | --- |
| No EnergyKit entitlement | The executable must not present EnergyKit-backed features as available |
| Base EnergyKit entitlement | Venue, guidance, and supported EnergyKit service routes may be available to the target |
| Base plus LoadEvents entitlement | The target may submit the documented load events for the Home app energy experience |
| Signed archive with final approved configuration | Evidence that the shipped executable carries the intended entitlement values |

The capability is a signed-build fact. A source entitlements file, an Xcode checkbox, or a preview fixture is not proof that the installed executable can call the service. Inspect the archive and test the target that actually owns the EnergyKit code. Review widgets, extensions, and companion targets independently.

## 2. EnergyVenue is the physical-site anchor

EnergyVenue represents a physical site associated with a Home configuration. The current framework documentation exposes:

- EnergyVenue.venues() for available venues;
- EnergyVenue.venue(for:) for an identifier;
- EnergyVenue.venue(matchingHomeUniqueIdentifier:) for a Home identifier;
- id and name values;
- submitEvents for values conforming to ElectricalLoadEventProtocol.

The venue is not a latitude/longitude chosen by the app and is not a generic database row. Keep the framework venue identifier, the user-approved display label, and any product-owned device mapping separate. If a person has more than one Home, present an explicit choice. Never silently select the first venue or substitute another Home when the selected venue becomes unavailable.

Venue state should be modeled distinctly:

| State | Truthful UI |
| --- | --- |
| Loading | Looking for Homes available to EnergyKit |
| Empty | No EnergyKit venue is available for this account/device |
| Selected | The person chose this Home for this device |
| Venue unavailable | The previously selected Home must be revalidated |
| Permission denied | The app cannot continue on the requested Home path |
| Unsupported region | Guidance is unavailable in the current region |

A venue identifier is sensitive contextual data. Redact it in logs and shared test evidence, and do not expose a private Home address as if EnergyKit supplied one.

## 3. Guidance and event provenance are different records

ElectricityGuidance is a recommendation stream. Its current value contains an interval, values, options, energy venue identifier, suggested action, and guidance token. The token is the provenance handle used when constructing a related electrical load event.

The two suggested actions are semantically different:

| Suggested action | Example device behavior | Scheduling meaning |
| --- | --- | --- |
| shift | EV charging | Move a substantially similar load to a better time window |
| reduce | HVAC demand | Reduce or avoid load when comfort and safety constraints permit |

The guidance stream can update indefinitely. Apple’s sample material describes typical hourly updates while allowing more frequent updates when conditions change. Store the fetched time, interval, venue, suggested action, and token alongside the schedule proposal. A current guidance value does not prove that a device followed it.

Keep this provenance chain:

~~~text
guidance token
  -> schedule revision
  -> user approval or override
  -> device command
  -> observed telemetry
  -> event session
~~~

Do not copy a token to another venue or device, attach it to synthetic telemetry, or call a schedule “optimized” after the person overrides it without updating the product state.

## 4. ElectricalLoadEventProtocol is a closed system contract

EnergyKit documents ElectricalLoadEventProtocol as the common event contract for its supported event types. The current protocol is intended for Apple’s documented EV/HVAC event types and carries the standard Codable, Identifiable, and Sendable shape needed by the framework.

Do not invent a new event type by declaring an unsupported conformance. Use the documented event classes:

| Type | Role |
| --- | --- |
| ElectricVehicleLoadEvent | A session-based EV energy-flow record |
| ElectricVehicleStatusEvent | A point-in-time EV status snapshot |
| ElectricHVACLoadEvent | A session-based HVAC load record |

The app’s internal telemetry model may be richer, but the conversion to EnergyKit must be deterministic, validated, and traceable to an observed device record. A serialized object that happens to match a type is not evidence that the system accepted it.

## 5. EV load events are session-based

ElectricVehicleLoadEvent represents energy flow over a session. The session contains an identifier and state, with the current API also associating guidance state. Keep one stable session identity for a continuous imported or exported flow.

The product should treat the session as a state machine:

~~~text
no session
  -> begin
  -> active
  -> active transition*
  -> end
  -> closed
~~~

The current Apple guidance describes these event semantics:

- a begin event starts the session;
- active events report meaningful progress and changes;
- an end event closes the session;
- stable charging can be sampled at approximately fifteen-minute intervals;
- more frequent events may be appropriate during volatility, user actions, or power changes;
- V2G/V2H imported and exported flow uses separate sessions, even if both directions occur near the same time.

Do not emit a new session for every telemetry tick. Do not reuse a closed session for a later plug-in. Do not merge imported and exported energy into one directionless record.

### EV measurement validation

ElectricVehicleLoadEvent.ElectricalMeasurement currently includes:

- state of charge;
- ElectricityFlowDirection;
- instantaneous power;
- cumulative energy;
- optional performance metrics.

The documented units are milliwatts for power and milliwatt-hours for energy. Validate before conversion:

| Field | Validation |
| --- | --- |
| State of charge | Within the documented 0–100 range |
| Direction | Imported or exported is explicit |
| Power | Unit conversion is explicit; sign is not used to hide direction |
| Energy | Cumulative within the session and never silently moves backward |
| Begin | Use the documented zero-power/zero-energy contract where required |
| End | Use the documented stopped-power and cumulative-energy contract |
| Device | Stable EnergyKit device identity and user-meaningful name |
| Guidance | Token belongs to the venue/device decision that produced the schedule |

If the physical device gives an estimate, retain the estimate flag in the product record. Do not add false precision while converting into framework units.

## 6. EV status events are not load sessions

ElectricVehicleStatusEvent is a point-in-time snapshot that complements, rather than replaces, an EV load session. Its current initializer includes:

- timestamp;
- ElectricalLoadDevice;
- venue identifier;
- status;
- state of charge;
- energy;
- optional estimated range;
- optional charging target;
- optional session identifier.

The status enumeration describes situations such as:

- charger plugged in;
- charger unplugged;
- charging active with a reason;
- charging idle with a reason.

Use a status event to explain why a vehicle is or is not charging at a moment in time. Use ElectricVehicleLoadEvent to represent the continuity and energy movement of the charging session. If a status snapshot refers to a load session, include its session identifier so the system can correlate the two records.

These are separate claims:

| App fact | Correct representation |
| --- | --- |
| The cable was connected | Plugged-in status event |
| The vehicle was waiting for a rate/deadline condition | Charging-idle status with the documented reason |
| Energy was flowing into the vehicle | Imported EV load event with measured power/energy |
| The user changed the target | Status/telemetry record and updated product schedule |
| The vehicle is estimated to reach a range | Optional status snapshot value, clearly labeled as estimated |

Never derive “charging active” solely from an AI explanation or a schedule timer.

## 7. HVAC load events follow meaningful transitions

ElectricHVACLoadEvent is also session-based, but the session is about HVAC electrical activity rather than vehicle charging. Apple’s current documentation describes recording meaningful state transitions such as heating/cooling stage changes, a person-initiated action, a pause, or an idle transition. Do not create a high-frequency event for every thermostat or sensor sample, and do not emit an event for the entire idle period between cycles.

The app should keep two layers:

1. a device/controller telemetry log used for comfort, safety, equipment limits, and troubleshooting;
2. a reduced EnergyKit event stream containing the meaningful electrical-load transitions.

The controller, not EnergyKit and not a language model, owns:

- freeze protection;
- temperature boundaries;
- equipment lockouts;
- compressor staging safety;
- manual override;
- failure recovery.

An EnergyKit reduce recommendation may inform a feasible controller decision. It cannot authorize an unsafe setpoint or prove that the HVAC system accepted the command.

## 8. Submit events through the selected venue

EnergyVenue.submitEvents accepts an array of values conforming to ElectricalLoadEventProtocol. Submit only events that passed local validation and are bound to the selected venue. Keep submission state separate from event construction:

~~~text
telemetry observed
  -> event constructed
  -> locally validated
  -> submit started
  -> accepted by EnergyKit
  -> Home processing pending
  -> Home presentation observed, if applicable
~~~

EnergyKitError distinguishes failures such as invalidLoadEvent, rateLimitExceeded, venueUnavailable, permissionDenied, serviceUnavailable, guidanceUnavailable, locationServicesDenied, and unsupportedRegion. Handle them differently:

| Error | Response |
| --- | --- |
| invalidLoadEvent | Fix the local state machine or measurement; do not blindly retry |
| rateLimitExceeded | Deduplicate, back off, and preserve the event/session state |
| venueUnavailable | Revalidate the Home and device mapping |
| permissionDenied | Explain the missing permission and keep manual control available |
| serviceUnavailable | Retry with bounded backoff and mark the freshness state |
| unsupportedRegion | Keep any product-owned fallback clearly separate from EnergyKit |

A successful submit call means the framework accepted the submission request. It does not prove that Apple Home has rendered an activity row, that historical insights are ready, or that the physical device behaved as intended.

## 9. LoadEvents and the Home app are system projection surfaces

The EnergyKit LoadEvents entitlement adds the documented Home app energy experience. Apple’s entitlement page describes device names and usage appearing in Home activity logs, historical charts, and monthly trend notifications, including whole-home energy context where supported.

The app should disclose the projection before submitting:

> This app can send charging or HVAC activity to EnergyKit. Apple Home may use accepted events in its energy activity and insight surfaces.

Keep these status values separate:

| Product state | Label |
| --- | --- |
| Event built | Ready to submit |
| Submit in flight | Sending activity |
| Framework returned success | EnergyKit accepted |
| System processing | Home presentation pending |
| System surface observed | Home activity available |
| Event rejected | Activity needs correction |

Do not reproduce Apple Home’s UI so closely that the app appears to be a system surface. Use native SwiftUI layout, controls, typography, and Liquid Glass hierarchy while clearly labeling the app-owned screen.

Apple’s current EnergyKit event and entitlement documentation describes energy data storage and synchronization as end-to-end encrypted, with the data not accessible to anyone, even Apple. That statement describes the EnergyKit system path; it does not automatically cover an app’s own backend, analytics, logs, exports, or AI prompts. Review those separately.

## 10. Historical insight queries

ElectricityInsightQuery makes the historical request explicit. The current API includes:

- options such as cleanliness and tariff;
- a DateInterval range;
- a granularity such as hourly, daily, or weekly;
- ElectricityFlowDirection.

ElectricityInsightService is an actor with a shared service. Its documented methods can return streams of ElectricityInsightRecord values for energy measurements or runtime durations. A record can expose range, total energy or runtime, and category groupings such as grid cleanliness or tariff peak.

Treat insight processing as a delayed historical pipeline:

~~~text
accepted load events
  -> system processing
  -> insight query
  -> AsyncStream record
  -> provenance-aware UI
~~~

The insight screen should state:

- venue and device;
- imported or exported direction;
- query range and granularity;
- fetched time and data freshness;
- whether cleanliness and tariff categories are present;
- whether events are still processing;
- what the app measured versus what EnergyKit classified.

Missing tariff information is not zero cost. Missing cleanliness data is not a neutral environmental result. A no-data state must remain visible.

## 11. SwiftUI and Liquid Glass composition

Use the [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass) guidance as a hierarchy rule:

- content and charts remain readable before glass is applied;
- glass groups navigation, actions, and transient controls;
- a status chip communicates freshness or submission state without pretending to be system proof;
- the schedule card can use a glass container while the event timeline remains a high-contrast content surface;
- a Home handoff banner is an app-owned explanatory surface, not a fake Home dashboard.

Energy data is often dense and time-based. Avoid placing every metric behind translucent layers. Use a solid or high-contrast chart background when grid lines, labels, or VoiceOver values need stable contrast. Respect Dynamic Type, Reduce Motion, increased contrast, Voice Control, Switch Control, keyboard focus, and large content sizes.

The energy surface should support:

1. venue selection;
2. current guidance and freshness;
3. schedule proposal;
4. explicit approval/override;
5. live physical telemetry;
6. event submission status;
7. historical insights;
8. recovery and privacy explanations.

An animated transition from “schedule proposal” to “active session” should only occur after the app has observed the physical state it claims. A timer reaching zero is not a charging event.

## 12. Bounded on-device AI

Foundation Models can be an optional explanation or preference-parsing layer, but the typed EnergyKit and device state remain authoritative. Good local tasks include:

- explain why a deterministic candidate window was selected;
- summarize a historical record with its exact range and missing categories;
- turn a natural-language preference into a typed deadline or comfort constraint for review;
- draft troubleshooting copy from a known EnergyKitError;
- rank already-valid schedule candidates.

The model must not:

- invent guidance ratings, tariff peaks, or grid cleanliness;
- claim that charging or HVAC action happened without telemetry;
- submit load events;
- alter a safety or comfort boundary;
- silently choose a Home venue;
- send raw household telemetry to an external model;
- trigger a physical charger or HVAC command without the product’s explicit, deterministic approval path.

Use a typed proposal:

~~~text
EnergyInsightExplanation:
  venueID
  deviceID
  sourceQuery
  sourceRecordIDs
  summary
  missingCategories
  freshness
  requiresUserReview
~~~

The UI should show which parts came from EnergyKit, which came from device telemetry, and which are generated wording.

## 13. Proof boundary

Keep the following claims separate in architecture, UI, logs, tests, and release notes:

| Claim | Evidence needed |
| --- | --- |
| EnergyKit route is available | Current SDK availability, entitlement, region, and supported target |
| Venue selected | Physical Home account and explicit person choice |
| Guidance received | Live guidance stream value with interval, venue, token, and fetched time |
| Schedule approved | User action recorded before the device command |
| Device action occurred | Physical telemetry or device acknowledgement with an honest meaning |
| Event is valid | Locally validated session, measurements, device, venue, and guidance binding |
| Event accepted | submitEvents completed successfully |
| Home shows activity | Home/system surface observed after processing |
| Insight exists | Historical query returned a record with provenance |
| AI is on-device | Device/model availability and input audit, not merely product copy |
| Release is ready | Signed archive, entitlement review, final SDK, TestFlight/device proof, and App Review metadata |

Simulator fixtures can prove reducer behavior and Liquid Glass layout. They cannot prove a real Home venue, region entitlement, charger/HVAC behavior, Home processing, or historical insight quality.

## Sources

- [EnergyKit](https://developer.apple.com/documentation/EnergyKit)
- [Introducing EnergyKit](https://developer.apple.com/energykit/)
- [Optimize home electricity usage with EnergyKit](https://developer.apple.com/videos/play/wwdc2025/257/)
- [Providing informative charging history for electric vehicles](https://developer.apple.com/documentation/EnergyKit/providing-informative-charging-history-for-electric-vehicles)
- [EnergyVenue](https://developer.apple.com/documentation/energykit/energyvenue)
- [ElectricityGuidance](https://developer.apple.com/documentation/energykit/electricityguidance)
- [ElectricityGuidance.Service](https://developer.apple.com/documentation/energykit/electricityguidance/service)
- [ElectricityGuidance.SuggestedAction](https://developer.apple.com/documentation/energykit/electricityguidance/suggestedaction-swift.enum)
- [ElectricalLoadEventProtocol](https://developer.apple.com/documentation/energykit/electricalloadeventprotocol)
- [ElectricVehicleLoadEvent](https://developer.apple.com/documentation/energykit/electricvehicleloadevent)
- [ElectricVehicleLoadEvent.ElectricalMeasurement](https://developer.apple.com/documentation/energykit/electricvehicleloadevent/electricalmeasurement)
- [ElectricVehicleStatusEvent](https://developer.apple.com/documentation/energykit/electricvehiclestatusevent)
- [ElectricVehicleStatusEvent.Status](https://developer.apple.com/documentation/energykit/electricvehiclestatusevent/status-swift.enum)
- [ElectricHVACLoadEvent](https://developer.apple.com/documentation/energykit/electrichvacloadevent)
- [ElectricityFlowDirection](https://developer.apple.com/documentation/energykit/electricityflowdirection)
- [ElectricityInsightQuery](https://developer.apple.com/documentation/energykit/electricityinsightquery)
- [ElectricityInsightService](https://developer.apple.com/documentation/energykit/electricityinsightservice)
- [ElectricityInsightRecord](https://developer.apple.com/documentation/energykit/electricityinsightrecord)
- [EnergyKitError](https://developer.apple.com/documentation/energykit/energykiterror)
- [EnergyKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit)
- [EnergyKit LoadEvents entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit.loadevents-experience)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
