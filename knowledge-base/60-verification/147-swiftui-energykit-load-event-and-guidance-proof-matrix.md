# SwiftUI EnergyKit load-event and historical-insight proof matrix

EnergyKit evidence crosses Apple SDK availability, signed entitlements, a real Home venue, grid guidance, physical device telemetry, event-session validation, system processing, and historical insight. This matrix keeps those claims separate.

The broad [EnergyKit guidance and load-event proof matrix](40-energykit-guidance-and-load-event-proof-matrix.md) remains the baseline. This page adds focused evidence for EV status snapshots, session continuity, HVAC transitions, insight query semantics, LoadEvents/Home projection, and on-device explanation review.

## 1. Test record

| Field | Record |
| --- | --- |
| Target | Bundle ID, target, extension/companion membership |
| SDK | Xcode and final SDK build |
| Deployment | iOS/iPadOS target and availability checks |
| Entitlements | Base EnergyKit and LoadEvents signed values |
| Region | Physical device region and contiguous-U.S. eligibility |
| Home account | Redacted test account and Home configuration |
| Venue | Selected EnergyVenue identifier, redacted |
| Device | EV/charger or HVAC model, firmware, device identity |
| Telemetry | Source, units, cadence, timestamp source, observed-state meaning |
| Guidance | Suggested action, venue, interval, fetched time, token redaction |
| Session | Imported/exported or HVAC session identity and state |
| Status | EV status snapshots and optional session correlation |
| Insights | Query options, date range, granularity, direction |
| Build evidence | Archive, signed entitlements, device model/OS, TestFlight build |
| System evidence | Home activity/insight surface, if available |
| Privacy | Retention, logs, backend, model input, Home sharing copy |

Do not include raw guidance tokens, private Home names, full device identifiers, household time series, or unredacted payloads in a shared evidence bundle.

## 2. Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| EnergyKit is the right framework | Product need is documented EV/HVAC/home energy guidance or insight | A generic energy chart |
| Base capability is configured | Signed archive contains com.apple.developer.energykit | Xcode source capability |
| LoadEvents is configured | Signed archive contains com.apple.developer.energykit.loadevents-experience and base capability | Home screenshot |
| API is available | Named target compiles against final SDK with availability checks | A web page symbol alone |
| Region is eligible | Physical device/account/Home meets current contiguous-U.S. boundary | Locale or VPN setting |
| Venue exists | EnergyVenue.venues returns a real venue on an eligible test account | Mock UUID |
| Venue selected correctly | Person chose the Home and device mapping is persisted | First array element |
| Guidance is live | AsyncSequence yields ElectricityGuidance with interval, venue, token, and fetched time | Hard-coded values |
| Guidance has cost context | Venue route returned relevant rate information | A tariff label drawn by the app |
| Schedule is feasible | Deterministic test covers deadline, device limits, and candidate windows | Lowest guidance rating |
| Schedule is approved | Explicit user action and revision before physical command | Notification tap or AI output |
| EV session is valid | Begin/active/end order, stable ID, units, direction, cumulative energy | Event initializer succeeds |
| EV status is valid | Snapshot contains documented status, state of charge, energy, device, venue | Connected cable UI |
| HVAC event is valid | Meaningful stage/active/idle transition and correct session | Every thermostat sample |
| Event accepted | submitEvents completes successfully | Event constructed or queued |
| Physical action occurred | Charger/HVAC telemetry or documented device acknowledgement | Schedule timer or API request |
| Home activity appears | Actual Home app/system presentation after processing | “Accepted” label in app |
| Insight exists | ElectricityInsightService query returns a record with range/provenance | Current guidance |
| Tariff exists | Returned record includes tariff category data | Missing category rendered as zero |
| AI is on-device | Device/model availability plus redacted-input audit | Copy saying “private AI” |
| Release is ready | Final SDK, archive, signed entitlements, device/TestFlight, region, privacy, App Review | Debug run |

## 3. Availability and entitlement tests

- [ ] Target availability annotations compile without silencing EnergyKit availability warnings.
- [ ] Base entitlement is present on the executable that imports EnergyKit.
- [ ] LoadEvents entitlement is present only on the intended event/Home target.
- [ ] LoadEvents target also carries the base EnergyKit entitlement.
- [ ] Widget, extension, watch, and companion targets are checked separately.
- [ ] Archive inspection matches source target configuration.
- [ ] Beta API notes and final SDK changes are reviewed before distribution.
- [ ] Unsupported-region UI never calls the route as if it were available.
- [ ] Removing the entitlement produces a clear capability state rather than a crash.

Evidence levels:

| Level | Evidence |
| --- | --- |
| C0 | Source/API reading |
| C1 | Compile and unit tests |
| C2 | Simulator or preview state |
| C3 | Signed physical-device build |
| C4 | Eligible Home/account/device/system surface |
| C5 | TestFlight/App Review/release artifact and production monitoring |

Do not label C0–C2 evidence as physical or release proof.

## 4. Venue and guidance scenarios

| Fixture | Expected result |
| --- | --- |
| No venue | Empty state with manual/product-owned fallback |
| One venue | Explicit person selection and redacted persistence |
| Multiple venues | Correct Home selection; no silent first-choice behavior |
| Venue removed | Revalidation and selection recovery |
| Home account changed | Reload venues and invalidate device mapping |
| Permission denied | Typed denial state and settings/manual route |
| Location services denied | Documented locationServicesDenied recovery |
| Unsupported region | No guidance call; manual path remains clear |
| Shift query | EV candidate windows and guidance token |
| Reduce query | HVAC candidate windows and guidance token |
| Location-only query | No unsupported cost claim |
| Stream refresh | Current value replaces prior value with new freshness |
| Stream cancellation | Old venue/device stream cannot mutate current state |
| Service unavailable | Backoff and stale/failure label |
| Guidance empty | No fabricated candidate values |

For each successful guidance result, capture the suggested action, venue, interval, fetched time, and a redacted token reference. A screenshot of a card is not enough to prove the stream or its provenance.

## 5. Schedule and user-control tests

### EV

- [ ] State of charge, target, battery/charger rate, and deadline are present.
- [ ] Scheduler rejects a window that cannot meet the deadline.
- [ ] Scheduler does not choose a past or stale interval.
- [ ] Start-now override is explicit and changes the proposal revision.
- [ ] User approval precedes a physical command.
- [ ] Device command result is separated from observed charging state.
- [ ] Pause/resume and target changes invalidate or update the schedule.
- [ ] V2G/V2H import and export are separate flow/session states.

### HVAC

- [ ] Comfort range is visible.
- [ ] Freeze and equipment safety limits are deterministic.
- [ ] Reduce proposal is optional and reversible.
- [ ] Manual override cancels or updates the active proposal.
- [ ] AI cannot set a temperature or duration outside the validator.
- [ ] Physical stage/active state is observed separately from the schedule.

## 6. EV session fixtures

| Fixture | Expected result |
| --- | --- |
| Begin with documented zero power/energy | Accepted for local event construction |
| Active imported sample | Imported direction and cumulative energy increase |
| Active exported sample | Separate exported session |
| Power change | Additional transition event if product policy requires |
| Stable charging | Bounded sample cadence, approximately fifteen minutes where appropriate |
| Pause or idle | Session state and status snapshot are distinct |
| End with stopped power | Closed session and cumulative total |
| End before begin | Local validation failure |
| Duplicate begin | Rejected/deduplicated without a second physical session |
| Cumulative energy decreases | Local validation failure |
| State of charge below 0 or above 100 | Local validation failure |
| Wrong venue | Revalidation/invalid event path |
| Wrong guidance token | Event is not submitted as associated guidance |
| Missing device telemetry | No synthetic event |
| Submit timeout | Reconcile durable state; do not duplicate blindly |
| Rate limit | Backoff and preserve event identity |

Evidence should include the local session transition log, redacted device/venue references, measurement units, and the submit result. It should not include a claim that Home displayed the event unless the system surface was actually observed.

## 7. EV status fixtures

- [ ] Charger plugged-in status is shown without calling it active charging.
- [ ] Charger unplugged status closes or invalidates the related product state.
- [ ] Charging active includes the documented active reason when available.
- [ ] Charging idle includes the documented idle reason when available.
- [ ] State of charge and energy use the correct units.
- [ ] Estimated range is labeled as estimated.
- [ ] Charging target is labeled as a target, not observed attainment.
- [ ] Optional session identifier correlates to the load session.
- [ ] Status snapshots do not replace the load-event continuity record.
- [ ] A generated explanation cannot produce a status event.

## 8. HVAC transition fixtures

| Fixture | Expected result |
| --- | --- |
| Heating stage changes | Meaningful HVAC event |
| Cooling stage changes | Meaningful HVAC event |
| Person changes target | Product telemetry and event policy evaluated |
| HVAC pauses | Session transition captured |
| HVAC resumes | Session transition captured |
| Long idle period | No event spam |
| Repeated identical samples | Debounced |
| Controller measurement missing | No invented energy value |
| Timestamp moves backward | Local validation failure |
| Device/session mismatch | Event rejected before submit |
| Physical equipment safety lockout | No AI or guidance override |

Test the full controller route on representative hardware. A fake stage enum can prove reducer behavior but cannot prove compressor or heat-pump operation.

## 9. Submission and Home tests

### Submission

- [ ] Event builder validates session order before submit.
- [ ] Imported/exported direction is explicit.
- [ ] Device and venue identifiers are stable and redacted in diagnostics.
- [ ] Submit state is durable across relaunch.
- [ ] Invalid events are not blindly retried.
- [ ] Rate limits apply bounded backoff and deduplication.
- [ ] Venue errors return to selection/revalidation.
- [ ] Successful submit is labeled as EnergyKit acceptance only.

### Home projection

- [ ] LoadEvents entitlement is signed into the intended target.
- [ ] The person is told that accepted activity may appear in Home.
- [ ] Device name is meaningful.
- [ ] Home processing/presentation is treated as asynchronous.
- [ ] App status does not claim Home display prematurely.
- [ ] Shared Home visibility is explained according to current Apple behavior.
- [ ] System evidence is collected without exposing private Home data.
- [ ] Removing the capability hides or explains the unavailable Home route.

## 10. Historical insight tests

- [ ] Query cleanliness only.
- [ ] Query tariff only where rate data is meaningful.
- [ ] Query both options with a named range.
- [ ] Test hourly, daily, and weekly granularity.
- [ ] Test imported and exported flow directions.
- [ ] Test no events.
- [ ] Test events accepted but insight still processing.
- [ ] Test multiple devices at one venue.
- [ ] Test venue unavailable during a query.
- [ ] Cancel an old stream when the query changes.
- [ ] Preserve query range and freshness with the returned record.
- [ ] Show missing tariff/cleanliness categories as unavailable, not zero.
- [ ] Provide chart summary/table alternative for accessibility.
- [ ] Do not compare records with mismatched venue, range, direction, or units.

Insight evidence should state whether the result came from EnergyKit processing, the app’s own telemetry, or generated prose. It should not be presented as a live meter or guaranteed utility bill.

## 11. AI evaluation fixtures

| Fixture | Expected result |
| --- | --- |
| Complete current guidance | Explanation cites selected interval and constraints |
| Missing rate data | Explanation states cost context is unavailable |
| Stale guidance | Explanation includes freshness caveat |
| Infeasible deadline | Model explains validator result and offers alternatives |
| Unsupported region | No forecast is invented |
| EV connected but not active | No claim of energy flow |
| HVAC command sent but no telemetry | No claim of physical operation |
| Insight missing category | No invented tariff/cleanliness |
| Malformed typed proposal | Deterministic validator rejects it |
| User edits schedule | Recompute and require review |
| User declines | No device command or event mutation |
| Model unavailable | Deterministic explanation remains usable |
| Raw telemetry accidentally included | Redaction/input audit blocks the call |

The AI test result should capture prompt/input classification, model availability, output schema validation, refusal behavior, and user-review state. Do not accept a fluent answer as domain proof.

## 12. SwiftUI/Liquid Glass/accessibility tests

- [ ] Guidance content remains readable with translucent materials.
- [ ] Charts and status labels preserve contrast in light/dark/high-contrast modes.
- [ ] Dynamic Type does not truncate deadline, comfort, or error copy.
- [ ] VoiceOver announces venue, device, freshness, direction, and state.
- [ ] Voice Control can select venue, review, approve, override, pause, resume, and end.
- [ ] Switch Control reaches all actions.
- [ ] Keyboard and pointer work on iPad/Mac idioms.
- [ ] Reduce Motion does not hide state changes.
- [ ] A system projection is visually labeled as external/system-owned.
- [ ] Glass is not used as a disabled-looking substitute for missing data.
- [ ] The AI explanation is secondary and dismissible.
- [ ] Home or insight processing states are not announced as completed.

## 13. Privacy and security tests

- [ ] Venue names and IDs are redacted from diagnostics.
- [ ] Guidance tokens are not logged or copied.
- [ ] Raw EV/HVAC telemetry is excluded from analytics unless explicitly reviewed.
- [ ] Household energy history is not sent to an external model by default.
- [ ] Local retention and deletion are documented.
- [ ] Home projection disclosure appears before submission.
- [ ] Backend storage is reviewed separately from EnergyKit’s system encryption.
- [ ] Screenshots and support exports mask time series and personal Home context.
- [ ] App-owned device identifiers are rotated or retained only as needed.

## 14. Physical-device and release gates

### Physical/device gate

- [ ] Eligible account, region, Home, and device are present.
- [ ] Venue discovery works on the intended device.
- [ ] Guidance stream returns current values.
- [ ] EV charger/vehicle or HVAC controller provides telemetry.
- [ ] Begin/active/end or HVAC transition events are observed.
- [ ] Status snapshots correlate when applicable.
- [ ] Event submission returns success and recovery paths are exercised.
- [ ] Home activity/insight presentation is tested if claimed.

### Release gate

- [ ] Final SDK signatures and beta changes are rechecked.
- [ ] Signed archive contains intended EnergyKit capabilities.
- [ ] Privacy strings, App Privacy responses, and Home disclosure are accurate.
- [ ] App Review metadata does not claim guaranteed savings, cleanliness, or device behavior.
- [ ] TestFlight build works on the eligible physical route.
- [ ] Crash/diagnostic logging redacts energy data.
- [ ] Release build is tested separately from Debug and previews.

## Sources

- [EnergyKit](https://developer.apple.com/documentation/EnergyKit)
- [Introducing EnergyKit](https://developer.apple.com/energykit/)
- [Optimize home electricity usage with EnergyKit](https://developer.apple.com/videos/play/wwdc2025/257/)
- [EnergyVenue](https://developer.apple.com/documentation/energykit/energyvenue)
- [ElectricityGuidance](https://developer.apple.com/documentation/energykit/electricityguidance)
- [ElectricalLoadEventProtocol](https://developer.apple.com/documentation/energykit/electricalloadeventprotocol)
- [ElectricVehicleLoadEvent](https://developer.apple.com/documentation/energykit/electricvehicleloadevent)
- [ElectricVehicleStatusEvent](https://developer.apple.com/documentation/energykit/electricvehiclestatusevent)
- [ElectricHVACLoadEvent](https://developer.apple.com/documentation/energykit/electrichvacloadevent)
- [ElectricityInsightQuery](https://developer.apple.com/documentation/energykit/electricityinsightquery)
- [ElectricityInsightService](https://developer.apple.com/documentation/energykit/electricityinsightservice)
- [ElectricityInsightRecord](https://developer.apple.com/documentation/energykit/electricityinsightrecord)
- [EnergyKitError](https://developer.apple.com/documentation/energykit/energykiterror)
- [EnergyKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit)
- [EnergyKit LoadEvents entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit.loadevents-experience)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
