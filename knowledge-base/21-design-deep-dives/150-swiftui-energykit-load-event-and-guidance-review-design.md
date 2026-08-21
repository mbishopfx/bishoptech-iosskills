# SwiftUI EnergyKit load-event and guidance design

EnergyKit interfaces have three visual layers that must not be collapsed into one “green energy” dashboard:

1. Apple’s guidance and historical classification;
2. the app’s deterministic schedule and device state;
3. a system projection such as Home activity or a generated explanation.

The [existing Energy guidance and Home activity design](43-energy-guidance-and-home-activity-surfaces.md) covers the broad visual language. This page focuses on the interaction design needed when a person moves from a guidance proposal to a measured EV/HVAC session, then to a delayed Home or historical insight result.

The design goal is native Apple coherence: clear hierarchy, restrained Liquid Glass, adaptive SwiftUI composition, explicit ownership, and honest state language. The goal is not to imitate the Home app or make a forecast look like physical proof.

## 1. Start with the energy job

Define one job before choosing a surface:

| Job | Primary decision |
| --- | --- |
| EV charging | Charge now, choose a feasible window, or override |
| HVAC reduction | Reduce within comfort/safety limits, or continue normally |
| Live session | Understand what the physical device is doing now |
| Home activity | Understand what was submitted and what may appear in Home |
| Historical insight | Explore processed energy context over a named range |
| Error recovery | Fix venue, permission, measurement, or service state |

Do not put venue selection, forecast explanation, device control, event history, and insight charts into one first screen. The person should always be able to answer:

> What is this value, who produced it, how fresh is it, and what can I do next?

That sentence is more useful than a decorative energy score.

## 2. Recommended information architecture

Use a navigation stack or split view that keeps the current device task primary:

~~~text
Energy
  -> Venue and device
      -> Guidance
          -> Schedule review
              -> Active session
                  -> Activity status
      -> Historical insights
      -> Privacy and Home projection
~~~

For a compact iPhone layout, use a single-column progression:

1. selected Home venue and device;
2. current guidance freshness;
3. proposed or active action;
4. physical telemetry;
5. submission and Home status;
6. history link.

For iPad or a wider window, keep the selected device and action visible in a sidebar while the schedule, telemetry, or insight detail changes in the main column. Do not duplicate controls across columns without a shared source of truth.

## 3. State language is the visual hierarchy

Use explicit labels rather than color alone:

| State | Suggested copy | Visual treatment |
| --- | --- | --- |
| Guidance loading | Updating guidance | Quiet progress indicator |
| Guidance ready | Latest guidance: 10:15 AM | Secondary freshness line |
| Proposal | Suggested window | Review card with edit action |
| Approved | Scheduled by you | Strong status, cancel/override action |
| Command requested | Asking charger/thermostat | Activity indicator |
| Physical action observed | Charging active / HVAC stage 2 | Primary live state |
| Event ready | Activity ready to submit | Secondary status |
| Accepted | EnergyKit accepted activity | Checkmark plus provenance |
| Home pending | Home presentation pending | Non-final informational state |
| Insight processing | History is still processing | No-data/processing state |
| Error | Could not update activity | Recovery action and explanation |

Avoid “optimized,” “saved,” “clean,” or “completed” unless the underlying evidence supports that exact claim. A lower guidance rating can be described as a better current candidate under the documented guidance semantics; it is not a guaranteed bill or emissions result.

## 4. Venue selection should feel like a trust decision

Before requesting or showing venues, explain the relationship:

> EnergyKit uses Homes available through Apple Home to provide guidance for this device. Choose the Home where the charger or thermostat operates.

Use a native list or selection control with:

- the Home name supplied by the system;
- a device mapping the person can review;
- a selected-state indicator;
- a visible “continue manually” or “not now” path;
- a link to why the venue is needed;
- an error state for unavailable or permission-denied venues.

Do not display a private address unless the product independently owns and has permission to show it. Do not auto-select a venue because it appears first. If the account changes or the selected Home disappears, return to venue selection instead of silently substituting another home.

Accessibility requirements:

- expose the whole row as one semantic selection control;
- include the Home name and selected state in the accessibility label/value;
- keep the reason and permission explanation available to VoiceOver;
- ensure Dynamic Type does not truncate the selected Home;
- allow keyboard, pointer, Switch Control, and Voice Control activation.

## 5. Guidance card design

The guidance card is a recommendation surface, not a meter. Include:

- suggested action: shift or reduce;
- interval or candidate window;
- freshness timestamp;
- device and venue;
- whether rate information is available;
- a plain-language reason;
- an explicit edit/review control;
- a manual or start-now alternative.

Example EV card:

> Suggested: charge between 1:00–3:00 AM
> Based on the latest guidance for Home and your 7:00 AM deadline.
> [Review schedule] [Charge now]

Example HVAC card:

> Suggested: reduce HVAC demand for 30 minutes
> Within your comfort limit. You can resume normal operation at any time.
> [Review] [Keep normal settings]

The card should not show a large “100% clean” meter unless the value and scale are genuinely provided by the framework and the label explains what it means. Apple’s guidance values are normalized inputs; the app should provide a legend rather than a moralized score.

## 6. Liquid Glass hierarchy

Follow [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass) as a compositional rule:

- use glass for navigation, actions, and transient controls;
- keep primary energy content readable against a stable surface;
- group related controls into one glass container;
- use material and tint to establish hierarchy, not to create a translucent wall over every chart;
- let controls adapt to the container’s shape and placement;
- preserve semantic labels and focus order.

Recommended layering:

~~~text
background/content
  -> schedule and telemetry content
  -> compact glass action group
  -> temporary status or review control
~~~

For an active session:

- the live state and telemetry are content;
- Pause, Start now, Resume, and End are actions;
- “EnergyKit accepted” or “Home pending” is status;
- an AI explanation is secondary content that can be dismissed.

Do not create a glass card that implies “system accepted” merely because its background resembles Apple Home. Use the app name or an explicit “Apple Home may show…” explanation when discussing a system projection.

## 7. Schedule review is a commit surface

A schedule proposal should be editable before it becomes a device command. Put the decision in a focused sheet or detail page:

| Element | Required behavior |
| --- | --- |
| Device | Shows the selected EV/charger or thermostat |
| Venue | Shows the Home name and allows revalidation |
| Window | Shows start/end and the guidance freshness |
| Constraint | Shows deadline, target charge, or comfort limit |
| Reason | Describes the deterministic candidate selection |
| Override | Start now, keep normal, or edit |
| Approval | Explicit primary action |
| Cancellation | Leaves physical state unchanged |

The sheet should distinguish:

- “This is the proposed window”;
- “You approved the schedule”;
- “The device accepted the command”;
- “Telemetry shows the action happened.”

Use a confirmation action for starting a physical operation. If the person changes the deadline or comfort boundary, recompute the candidates and invalidate the prior proposal revision.

## 8. EV live-session design

An EV screen should keep vehicle state, charger state, schedule state, and EnergyKit event state in separate rows:

~~~text
Vehicle
  62% state of charge
  Target 80%

Charger
  Connected
  Charging active
  7.2 kW imported

Schedule
  Approved window: 1:00–3:00 AM
  User override: none

Energy activity
  Session started 10:14 PM
  Last event accepted 10:29 PM
  Home presentation pending
~~~

Use directional language for imported versus exported energy. A V2G/V2H flow should not look like a positive/negative chart with no explanation. Label the direction and show that import and export sessions are separate.

When the vehicle is plugged in but idle, show the documented status reason if available. Do not label it “failed” when the system is waiting for a target, rate, schedule, or user condition. Conversely, do not label a merely connected cable as active charging.

The Start now override should clearly change the schedule state:

> Start now will override the suggested window. The app will continue to record the device’s actual activity.

## 9. HVAC design is comfort-first

HVAC surfaces must make the comfort and safety boundary visible. A reduce card should include:

- current and target temperature;
- proposed duration;
- allowed comfort range;
- whether the controller supports the requested action;
- a Resume normal control;
- a persistent manual override;
- an explanation that the proposal is optional.

Use a calm, reversible interaction:

> Reduce demand for 30 minutes within your 68–74° comfort range?

The app should not bury freeze protection, equipment limitations, or compressor state in an AI-generated paragraph. Those are deterministic controller facts and belong near the action.

For an HVAC session timeline, show transitions:

~~~text
10:00  Heating stage 1 observed
10:18  Person changed target
10:19  Heating paused
10:41  Heating stage 2 observed
~~~

Do not draw a continuous “active” bar when the device only supplied sparse transition events. If the app has richer controller telemetry, label the EnergyKit projection separately.

## 10. Event submission and Home status

The event status component should be compact but inspectable:

| Status | UI behavior |
| --- | --- |
| Ready to submit | Show the event/session timestamp and device |
| Sending | Disable duplicate submission, keep cancel/recovery available |
| Accepted | Show EnergyKit acceptance, not Home completion |
| Processing | Explain that Home/insight surfaces may update later |
| Invalid | Point to measurement/order/device correction |
| Rate limited | Show retry timing without duplicating the event |
| Venue unavailable | Return to Home selection |

If the LoadEvents entitlement is not present, do not show a disabled fake Home chart. Explain that the current build does not provide the system projection and keep the app-owned activity history available if appropriate.

When a Home result is eventually observed, use a link or explanatory card:

> Apple Home may include this device activity in its energy surfaces. This app shows the event and insight data available to its own feature.

This copy keeps system ownership clear and avoids a replica system screen.

## 11. Historical insights design

Historical insight filters should be explicit:

- device;
- venue;
- date range;
- granularity;
- imported/exported direction;
- cleanliness and/or tariff options.

The top of the chart should show provenance:

> EnergyKit historical insight
> Home: Apartment
> Device: Garage EV charger
> Jan 1–Jan 31 · Daily · Imported

Use category legends such as grid cleanliness or tariff peak only when a returned record contains those categories. Do not convert missing categories into gray zero bars. Use a “still processing,” “no events,” or “rate data unavailable” state.

For accessibility, provide a chart summary and table alternative:

> Daily imported energy ranged from 6.2 to 18.4 kWh. Tariff classification was unavailable for 4 days.

VoiceOver users should be able to reach the date range, filter, legend, summary, and individual data points in a useful order. Do not rely on color gradients alone to convey peak categories.

## 12. AI explanation surface

An on-device explanation should appear after the source facts, not in place of them. Use a disclosure or secondary sheet:

~~~text
Latest guidance
  1:00–3:00 AM · freshness 10:15 AM

Your schedule
  Approved for a 7:00 AM deadline

Why this window?
  [Explain]
~~~

When the person taps Explain, show:

- the source query or schedule revision;
- the selected constraints;
- missing data;
- a “generated explanation” label;
- a way to dismiss or report a confusing explanation.

The model can explain a deterministic candidate or summarize a returned insight. It cannot provide a cleaner value that EnergyKit did not return, claim physical activity that telemetry did not observe, or submit/change an event.

Keep household energy telemetry out of external model calls by default. If Foundation Models is unavailable, the deterministic explanation must remain useful.

## 13. Accessibility and alternate input

Follow [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals) and the [HIG accessibility guidance](https://developer.apple.com/design/human-interface-guidelines/accessibility):

- use semantic SwiftUI controls instead of tap-only glass surfaces;
- include freshness and ownership in labels;
- expose selected Home/device as a value;
- announce a change from proposal to observed physical state;
- preserve the action order in VoiceOver;
- support Dynamic Type without truncating safety or timing text;
- respect Reduce Motion when a live session changes;
- preserve contrast behind translucent materials;
- test Voice Control phrases for review, start-now, pause, resume, and end;
- provide keyboard and pointer equivalents on iPad and Mac idioms;
- use haptics as reinforcement, not as the only event signal.

An accessibility label should say “Charging active, 7.2 kilowatts imported” rather than “green card.” A generated explanation should be reachable as content and never replace the raw typed facts.

## 14. Privacy-first visual disclosure

Energy activity can reveal routines, occupancy patterns, vehicle use, and household behavior. Explain:

- which Home venue the person selected;
- what event data the app submits;
- that accepted activity may appear in the Home app according to Apple’s system behavior;
- what the app stores locally;
- whether any analytics or backend receives data;
- whether AI processing is on-device;
- how to delete or disconnect app-owned records.

Do not print venue identifiers, guidance tokens, raw event payloads, or household time series into screenshots, logs, clipboard content, or support attachments by default. Redact the timeline in diagnostics.

## 15. Design proof checklist

- [ ] Venue choice is explicit and reversible.
- [ ] Guidance is labeled as recommendation input.
- [ ] Schedule approval is distinct from device command.
- [ ] Physical telemetry is distinct from a timer or command response.
- [ ] EV imported/exported sessions are visually separate.
- [ ] EV status snapshots are not drawn as load continuity.
- [ ] HVAC comfort and safety limits are visible near the action.
- [ ] Event accepted is distinct from Home presentation.
- [ ] Insight processing and missing categories have honest states.
- [ ] Liquid Glass is used for hierarchy, not to fake Home ownership.
- [ ] AI explanation is labeled, optional, and sourced.
- [ ] Dynamic Type, VoiceOver, Reduce Motion, contrast, keyboard, pointer, Voice Control, and Switch Control are tested.
- [ ] Screenshots and logs redact household energy context.

## Sources

- [EnergyKit](https://developer.apple.com/documentation/EnergyKit)
- [Introducing EnergyKit](https://developer.apple.com/energykit/)
- [Optimize home electricity usage with EnergyKit](https://developer.apple.com/videos/play/wwdc2025/257/)
- [EnergyVenue](https://developer.apple.com/documentation/energykit/energyvenue)
- [ElectricityGuidance](https://developer.apple.com/documentation/energykit/electricityguidance)
- [ElectricVehicleLoadEvent](https://developer.apple.com/documentation/energykit/electricvehicleloadevent)
- [ElectricVehicleStatusEvent](https://developer.apple.com/documentation/energykit/electricvehiclestatusevent)
- [ElectricHVACLoadEvent](https://developer.apple.com/documentation/energykit/electrichvacloadevent)
- [ElectricityInsightQuery](https://developer.apple.com/documentation/energykit/electricityinsightquery)
- [ElectricityInsightRecord](https://developer.apple.com/documentation/energykit/electricityinsightrecord)
- [EnergyKit LoadEvents entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.energykit.loadevents-experience)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
