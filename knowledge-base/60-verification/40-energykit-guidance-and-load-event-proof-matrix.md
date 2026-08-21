# EnergyKit Guidance and Load-Event Proof Matrix

EnergyKit claims cross a signed entitlement, Apple Home venue, region, guidance stream, physical device, telemetry, load-event validation, Home app presentation, and historical insight. Record evidence per layer.

## Test record

| Field | Record |
| --- | --- |
| App target | Bundle ID, target membership, configuration |
| SDK/deployment | Xcode, SDK, iOS/iPadOS target |
| Entitlements | Base EnergyKit and optional LoadEvents signed values |
| Region | Device region and contiguous-U.S. eligibility |
| Home account | Test account and Home configuration, without exporting personal data |
| Venues | Number of venues, selected venue ID redaction, selected Home |
| Device | EV/charger or HVAC model, firmware, device identifier redaction |
| Telemetry | Source, units, sampling cadence, clock/time zone |
| Guidance | Suggested action, venue, guidance interval, token redaction, fetched time |
| Event policy | Begin/active/end or HVAC transition rules, retry/backoff |
| Insight query | Venue, device, date range, granularity, options, flow direction |
| App build | Version/build, signed archive, physical device model/OS |
| Home result | Event processing/presentation evidence, if available |
| Privacy | Local retention, logs, model input, Home sharing explanation |

Do not include raw telemetry, full guidance tokens, user Home names, or personal energy histories in shared evidence.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| EnergyKit is the correct route | Product outcome is EV/HVAC/home energy guidance or insight | A generic electricity chart requirement |
| Base capability is configured | Xcode target capability, compile, signed entitlement | An entitlements source file |
| LoadEvents capability is configured | Base and LoadEvents capabilities on intended target, signed archive inspection | Home app screenshot alone |
| iOS 26 route is available | Final SDK/deployment target and API availability check | Current web page symbol |
| Region is eligible | Device/venue in contiguous U.S. test environment | Locale string or VPN |
| Venues are available | Physical test Home, EnergyVenue.venues result, selected venue | A local mock venue |
| Correct venue selected | Person-selected Home/venue and persisted redacted ID | First venue in an array |
| Guidance stream works | Real venue, shift/reduce query, AsyncSequence value, interval/token/freshness | Hard-coded forecast |
| Guidance reflects cost | Venue guidance with rate data and documented availability | A tariff label drawn by the app |
| Schedule is feasible | Deterministic engine with device limits, deadline, state, and candidate windows | Lowest guidance value alone |
| User approved schedule | Explicit approval or override recorded before device command | AI text or a preview |
| Physical action occurred | Charger/HVAC telemetry confirms action | Command call returned |
| EV load event is valid | Begin/active/end order, units, cumulative energy, direction, device/venue/guidance binding | A serialized event object |
| HVAC load event is valid | Meaningful stage/active/idle transitions with correct venue/device | A high-frequency sensor log |
| Event accepted | EnergyVenue.submitEvents completes successfully | Event constructed or queued |
| Home app shows activity | Actual Home app/system evidence after processing | Local app “sent” status |
| Insight is available | Historical query returns AsyncStream record with provenance | Current guidance result |
| AI is local | Model availability/device trace and redacted input audit | “On-device” marketing copy |
| Privacy boundary holds | No raw telemetry/model upload, retention/deletion test, Home sharing copy | End-to-end encryption statement alone |
| Release is ready | Final SDK, signed entitlements, region/product eligibility, beta recheck, release artifact | One development device run |

## Entitlement and target checks

- [ ] Base EnergyKit entitlement key is present on the intended executable.
- [ ] LoadEvents entitlement is present only when the Home app route is intended.
- [ ] LoadEvents target also has base EnergyKit capability.
- [ ] Widget/extension/companion targets are reviewed independently.
- [ ] Signed archive values match the source target configuration.
- [ ] Final SDK availability and beta changes are reviewed before release.
- [ ] App copy does not expose an unavailable route as a working feature.

## Venue scenarios

| Scenario | Expected result |
| --- | --- |
| No Home venue | Empty/venue-unavailable state; no silent fallback to another home |
| One venue | Person selects it; redacted identifier persists |
| Multiple venues | Person chooses the correct home/device location |
| Venue removed | Selected venue becomes unavailable; app asks for a new selection |
| Home account changes | Reload and revalidate venue/device association |
| Permission denied | Typed denial state and manual schedule route |
| Location Services disabled | Documented locationServicesDenied route |
| Unsupported region | Guidance unavailable with manual product flow |

Check that the app never displays a private Home address or invents venue identity from a coordinate.

## Guidance scenarios

- [ ] Shift query for an EV.
- [ ] Reduce query for HVAC.
- [ ] Venue guidance with cost information where available.
- [ ] Location overload without cost information.
- [ ] Initial guidance arrival.
- [ ] Guidance refresh.
- [ ] Guidance cancellation when device/venue changes.
- [ ] Guidance unavailable.
- [ ] Service unavailable.
- [ ] Stale guidance after the stream ends.
- [ ] Token stored with the schedule and bound to the requesting device/venue.
- [ ] No fabricated values when the stream is empty.

Record the interval and fetched time. If a schedule outlives the interval, show that the schedule was based on older guidance.

## Schedule and physical-device scenarios

### EV

- [ ] Vehicle state of charge is known and units are validated.
- [ ] Target state of charge and deadline are explicit.
- [ ] Charger power limit and vehicle charging time are represented.
- [ ] Shift schedule meets the deadline or explains infeasibility.
- [ ] Start-now override is available.
- [ ] Pause/resume is reflected.
- [ ] Power change causes a meaningful event.
- [ ] Charging end is observed from telemetry.
- [ ] V2G/V2H import and export use separate sessions.

### HVAC

- [ ] Comfort limit is explicit.
- [ ] Reduce proposal cannot exceed deterministic temperature/safety limits.
- [ ] Stage change produces a meaningful event.
- [ ] Person override is available.
- [ ] Idle periods do not create event spam.
- [ ] Freeze/safety protections are owned by the device/controller, not the model.

## Load-event validation

Test invalid and valid sequences:

| Event case | Expected result |
| --- | --- |
| EV begin with nonzero pre-charge power when zero is required | Invalid event or documented rejection |
| EV active with cumulative energy moving backward | Rejected before submission |
| EV end before begin | Invalid session order |
| EV end with nonzero power after charging stopped | Rejected or corrected from actual telemetry |
| Device did not request the guidance | Rejected; app must not fabricate association |
| Wrong venue | venueUnavailable/invalid event path |
| Duplicate event | Deduplicated or handled idempotently |
| Stable 15-minute charging | Bounded event cadence |
| Volatile charging/pause/power change | Additional transition event |
| HVAC stage transition | One meaningful event |
| Idle HVAC period | No continuous high-frequency events |
| Too many events | rateLimitExceeded with backoff |
| Submit succeeds | Accepted state, not Home display proof |

Keep a local event state machine so a failed submission can be retried without generating a new contradictory session.

## Insight scenarios

- [ ] Query cleanliness only.
- [ ] Query tariff only when rate data is relevant.
- [ ] Query both with a documented flow direction.
- [ ] Hourly, daily, and weekly granularity against suitable ranges.
- [ ] No load events.
- [ ] Newly submitted events not processed yet.
- [ ] Partial cleanliness/tariff breakdown.
- [ ] Multiple devices at one venue.
- [ ] Venue unavailable.
- [ ] Insight stream cancellation.
- [ ] Historical record freshness and source label.

Do not turn missing tariff data into zero cost. Do not compare two devices unless their venue, date range, units, and query options match.

## Home app and privacy checks

- [ ] Device name is meaningful and user-appropriate.
- [ ] Person understands that load events may appear in Apple Home.
- [ ] Shared Home visibility is explained according to current Apple behavior.
- [ ] Local app status distinguishes submitted from Home-presented.
- [ ] No raw telemetry appears in logs, analytics, crash reports, clipboard, or AI prompts.
- [ ] Energy history deletion and local retention are documented.
- [ ] End-to-end encrypted system handling is not expanded into an unsupported claim about all product/backend data.

## AI evaluation matrix

| Fixture | Expected result |
| --- | --- |
| Latest guidance, complete inputs | Explain selected window and constraints |
| Missing tariff data | State that cost estimate is unavailable |
| Stale guidance | Mark freshness and suggest refresh |
| Infeasible deadline | Explain why and offer start-now/manual alternatives |
| Unsupported region | Do not fabricate a forecast |
| Missing physical action | Do not claim charging/HVAC happened |
| Malformed proposal | Deterministic validator rejects it |
| Person edits schedule | Revalidate deadline, comfort, device limits |
| Person declines | No device command or event mutation |
| Model unavailable | Deterministic explanation remains usable |
| Raw telemetry supplied accidentally | Input audit fails and blocks the model call |

The model can explain or rank deterministic candidates. It cannot create grid values, guarantee savings, submit events, or control a physical device without the product’s approved path.

## Accessibility and release checks

- [ ] VoiceOver reads venue, device, guidance interval, schedule, freshness, and primary action.
- [ ] Dynamic Type keeps the deadline and override visible.
- [ ] Voice Control reaches schedule and manual actions.
- [ ] Switch Control reaches the recovery path.
- [ ] Reduce Motion preserves schedule changes.
- [ ] Reduce Transparency preserves contrast.
- [ ] Charts have text summaries and details.
- [ ] Long Home/device names and localized units fit.
- [ ] Backgrounding/lock/call/system prompt does not falsely advance physical action.
- [ ] Final release build has target, entitlement, privacy, and Home integration evidence.

## Evidence vocabulary

| Term | Meaning |
| --- | --- |
| available | EnergyKit returned an available venue/guidance/service result |
| current | Guidance was fetched at a recorded time and remains within the product freshness window |
| proposed | Deterministic schedule exists but is not approved |
| approved | Person accepted the schedule |
| requested | Product sent a device command |
| observed | Physical telemetry confirmed the result |
| constructed | Event object passed local validation |
| accepted | EnergyKit accepted event submission |
| presented | Home app/system surface visibly processed or displayed the data |
| historical | Insight query returned processed data for a defined interval |

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
- [EnergyKitError](https://developer.apple.com/documentation/energykit/energykiterror)
- [ElectricityInsightService](https://developer.apple.com/documentation/energykit/electricityinsightservice)
- [EnergyKit Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit)
- [EnergyKit LoadEvents Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit.loadevents-experience)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
