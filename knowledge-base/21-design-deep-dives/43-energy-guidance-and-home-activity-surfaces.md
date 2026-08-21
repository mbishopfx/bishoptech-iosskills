# Energy Guidance and Home Activity Surfaces

EnergyKit surfaces need to make a probabilistic forecast feel useful without turning it into a promise. The native design goal is a calm decision surface:

~~~text
device goal -> selected Home venue -> current guidance -> feasible proposal
-> user approval/override -> physical result -> submitted evidence -> historical insight
~~~

Liquid Glass can group the selected venue, active schedule, and one next action. It should not make an unavailable forecast look live or turn a cost/cleanliness suggestion into a green “guaranteed savings” badge.

## Lead with the device decision

Use the person’s job as the entry point:

| Person’s job | First screen |
| --- | --- |
| Charge my EV by morning | Vehicle state, deadline, proposed charging window |
| Charge when electricity is cleaner | Guidance explanation, schedule preview, start/override |
| Reduce HVAC usage during a peak period | Comfort boundary, proposed reduction window, override |
| Review my home energy activity | Venue/device selector, date range, insight freshness |
| Understand missing energy data | Venue, region, permission, guidance, and event-state explanation |

Do not begin with a chart. The chart is useful after the app has established the device, venue, date range, and data source.

## Screen anatomy

A compact iPhone flow:

1. **Venue header** — Home/venue name and selected device.
2. **Current state** — EV charge, HVAC state, last observed telemetry, and freshness.
3. **Guidance card** — clean/cost context and its valid interval.
4. **Schedule proposal** — start/end window, deadline, and the inputs used.
5. **Primary action** — Start now, Use proposed window, or Review.
6. **Activity and insight detail** — submitted events, processing status, and historical results.

On iPad or Mac Catalyst, use a sidebar for venues/devices and a detail column for the schedule and insights. Preserve the same language across size classes.

## State model

Do not reduce EnergyKit to a single clean-energy Boolean:

| State | Copy | Action |
| --- | --- | --- |
| unavailableBuild | Energy guidance is not available in this build | Explain capability/SDK |
| unsupportedRegion | Energy guidance is unavailable in this region | Keep manual route |
| venueNeeded | Choose a Home location | Select venue |
| permissionNeeded | Permission needed to use home energy data | Explain and continue |
| loadingVenue | Loading Home locations | Wait/cancel |
| venueReady | Ready for this home | Request guidance |
| guidanceLoading | Getting the latest guidance | Wait/use manual route |
| guidanceReady | Guidance available through [time] | Review schedule |
| guidanceStale | Guidance needs an update | Refresh |
| scheduleDraft | Proposed window ready | Approve/edit |
| waitingForDevice | Waiting for charger/thermostat state | Refresh device state |
| actionRequested | Device action requested | Observe result |
| actionObserved | Physical action observed | Record event |
| eventPending | Energy event is being submitted | View activity |
| eventAccepted | Energy event accepted | Continue |
| eventRejected | Event needs correction | Inspect telemetry |
| insightProcessing | Historical insight is being prepared | Wait |
| insightReady | Historical insight available | Review |
| noData | Not enough events for this range | Show what is missing |
| failed | Could not continue | Retry or manual route |

The app should say “proposal,” “latest guidance,” and “observed” where those distinctions matter.

## Guidance card

The guidance card should contain:

- selected venue;
- guidance interval;
- suggested action: shift or reduce;
- explanation that lower ratings indicate relatively cleaner/less expensive periods when cost data exists;
- last updated time;
- “cost data unavailable” when rate information is absent;
- a details route for assumptions and missing inputs.

Avoid an arbitrary 0–100 score without the legend. If you convert EnergyKit’s normalized values into a visual scale, retain the direction and label the scale. Do not use red/green alone; pair color with text and a symbol.

Example:

> Latest guidance for Home: Cedar Street. The proposed EV window is 1:00–5:00 AM because those intervals are rated more favorably in the current forecast. Rate information is unavailable.

The last sentence prevents a clean-energy result from being misread as a guaranteed bill estimate.

## Schedule proposal design

The proposal should show the constraints that shaped it:

| Input | Show |
| --- | --- |
| Deadline | “Ready by 7:00 AM” |
| Current state | “Battery 43%” or “HVAC stage idle” |
| Device limit | “Uses charger’s configured power” |
| Guidance freshness | “Updated 18 minutes ago” |
| Missing data | “Rate data unavailable” |
| User override | “Start now” and “Choose another time” |

Use a stable primary action. An animated clock or gradient can supplement the schedule but should not carry the meaning alone. The schedule remains legible with Reduce Motion, Reduce Transparency, large text, dark appearance, and VoiceOver.

## Liquid Glass composition

Use one glass group for related controls:

- venue picker;
- current device state;
- guidance status;
- one primary schedule action.

Keep charts, explanations, and error copy on readable surfaces. Use native Button, Picker, DatePicker, Toggle, NavigationLink, and confirmationDialog controls. A custom glass control must retain semantic labels and an accessible value.

Do not use glass to:

- conceal missing data;
- suggest the Home app has accepted an event;
- imply a physical charger/HVAC command succeeded;
- place a dense analytics dashboard behind a translucent layer;
- create a fake Home app surface that could confuse people about ownership.

Morphing can connect a schedule card to a detail sheet when the identity remains stable. If a schedule changes because new guidance arrives, animate the changed interval only and announce the update in text.

## Consent and Home venue selection

Explain the Home relationship before requesting venue data:

> EnergyKit uses the homes available through Apple Home to provide guidance for this device. Choose the home where this charger or thermostat operates.

Then show:

- the venue name;
- what data the app requests;
- whether the app will submit load events;
- whether submitted events may appear in the Home app;
- how to continue with manual scheduling.

Never silently choose the first venue. If a person shares multiple homes, show the choice. If the selected Home disappears, show “Venue unavailable” and require a fresh selection.

## Home app handoff

When the LoadEvents capability is present, set expectations:

> When this app submits charging or HVAC activity, Apple Home may use it for activity logs, charts, and trend notifications. Processing and sync may take time.

Do not recreate Apple’s Home activity language so closely that a person thinks the screen is an Apple system surface. Use the product’s own visual identity, with native spacing, typography, controls, and accessibility behavior.

Show an activity state:

| App state | Honest label |
| --- | --- |
| Event constructed | Ready to submit |
| Submit called | Sending activity |
| Framework accepted | Activity accepted |
| Home sync pending | Home presentation pending |
| Insight available | Historical insight ready |
| Invalid event | Activity needs correction |

## EV charging surface

The EV route should separate:

- vehicle state of charge;
- charger connection;
- app’s requested schedule;
- physical charger action;
- guidance token and freshness;
- submitted load event state.

An EV may be unplugged, paused, limited by the vehicle, or unable to meet the deadline. Use a clear override:

> Start charging now

If the person chooses now, the app should not continue to imply that the cleanest window was used. Record the override as a product event and keep the EnergyKit load event aligned with the physical telemetry.

For V2G/V2H, show importing and exporting as separate session concepts. Avoid a single “energy movement” chart that hides direction.

## HVAC surface

HVAC control is comfort-sensitive. A “reduce” proposal should state:

- proposed interval;
- expected comfort/temperature boundary;
- whether the device supports the requested stage;
- override action;
- safety or freeze-protection limits owned by the device/controller.

Use copy such as:

> Reduce HVAC demand for 30 minutes, within your comfort limit. You can resume normal operation at any time.

Do not call a forecast “safe,” and do not let an AI model set a temperature or duration without deterministic limits and explicit confirmation.

## Insights design

Insights need provenance:

- device identifier/name;
- venue;
- date range;
- granularity;
- energy direction;
- requested options such as cleanliness or tariff;
- last event submission;
- data availability;
- “historical” label.

If tariff data is missing, omit the cost series rather than showing zero. If there are no events, explain what the person can do:

> No EnergyKit load events are available for this range. Run a charging session with this device and return after activity is submitted.

For accessibility, charts need a text summary and a table/detail route. A custom chart can be visually beautiful, but its values, dates, categories, and trends must be navigable without color or hover.

## Error and offline copy

| Condition | Copy | Fallback |
| --- | --- | --- |
| Unsupported region | Energy guidance is unavailable in this region. | Manual schedule |
| Location services denied | Home venue lookup needs Location Services enabled. | Open Settings or manual route |
| Guidance unavailable | The latest forecast is unavailable. | Use the saved/manual schedule |
| Service unavailable | EnergyKit could not start right now. | Retry with backoff |
| Rate-limited event | Activity is queued; the system asked us to slow down. | Deduplicate/retry later |
| Invalid event | This activity record does not match the device session. | Inspect telemetry, do not retry unchanged |
| Venue unavailable | This Home location is no longer available. | Choose a current venue |
| Device action not observed | The requested action was not confirmed by the device. | Retry or inspect device |

Do not display cached guidance as current. Label its timestamp and allow the person to use a manual schedule.

## AI explanation shell

An AI review sheet can summarize a deterministic proposal:

- source: latest EnergyKit guidance;
- venue and device;
- selected window;
- missing rate/telemetry data;
- why this window won;
- what the person can edit;
- physical action still pending.

Example:

> The proposed window fits your 7:00 AM deadline and uses the latest guidance for this home. Rate information was not available, so this explanation does not estimate your bill. The charger has not confirmed the action yet.

Keep the proposal editable and do not let the model submit events or start charging. If the on-device model is unavailable, present the deterministic explanation.

## Accessibility and localization

Test:

- VoiceOver reading order: venue, device, current state, guidance interval, proposal, primary action, override;
- Dynamic Type with schedule and chart content;
- Voice Control labels such as “Use proposed window” and “Start now”;
- Switch Control through the override and removal actions;
- Reduce Motion for schedule updates;
- Reduce Transparency with opaque cards;
- right-to-left layout;
- long Home and device names;
- localized units, dates, percentages, currency, and time zones;
- keyboard and pointer input on iPad.

Announce meaningful guidance refreshes, not every forecast-stream tick. Keep an explicit “Updated” timestamp.

## Visual and system proof

Capture:

- no capability build;
- unsupported region;
- one Home venue;
- multiple Home venues;
- guidance loading/ready/stale;
- schedule approved/edited/overridden;
- physical action pending/observed;
- load event accepted/rejected;
- Home app activity pending/visible;
- insight ready/no data;
- large text/reduced effects/VoiceOver.

Previews and fixtures prove the shell. Only a final target, correct entitlement, eligible region, real Home configuration, physical EV/HVAC telemetry, and system/Home evidence prove the EnergyKit route.

## Sources

- [EnergyKit](https://developer.apple.com/documentation/EnergyKit)
- [Introducing EnergyKit](https://developer.apple.com/energykit/)
- [Optimizing home electricity usage](https://developer.apple.com/documentation/EnergyKit/optimizing-home-electricity-usage)
- [Providing charging history for electric vehicles](https://developer.apple.com/documentation/EnergyKit/providing-informative-charging-history-for-electric-vehicles)
- [ElectricityGuidance](https://developer.apple.com/documentation/energykit/electricityguidance)
- [EnergyVenue](https://developer.apple.com/documentation/energykit/energyvenue)
- [ElectricityInsightService](https://developer.apple.com/documentation/energykit/electricityinsightservice)
- [EnergyKit LoadEvents Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit.loadevents-experience)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [Charts](https://developer.apple.com/design/human-interface-guidelines/charts)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
