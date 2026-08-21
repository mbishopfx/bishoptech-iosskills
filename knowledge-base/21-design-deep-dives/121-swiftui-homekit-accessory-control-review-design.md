# SwiftUI HomeKit and Matter accessory-control review design

Design a HomeKit or Matter surface around a person’s task, the selected home, the current device state, and the exact side effect. Native polish comes from respecting Apple’s home model and system-owned setup flows. It does not come from cloning Apple Home or placing every control inside a glass capsule.

This page is the design companion to [SwiftUI HomeKit and Matter accessory-control review](../42-framework-deep-dives/93-swiftui-homekit-accessory-control-review.md), [HomeKit and Matter native surfaces](30-homekit-and-matter-native-surfaces.md), and [HomeKit and Matter automation route](../50-capability-recipes/33-homekit-matter-automation-route.md).

## The design contract

Every primary screen should answer:

1. Which home and room are in context?
2. Which physical device or service is represented?
3. Is the displayed value current, pending, stale, unreachable, or unknown?
4. What will happen if the person activates the control?
5. Can the person recover if permission, network, or the accessory fails?

Use this hierarchy:

~~~text
home context
  -> task group
  -> service identity and state
  -> one clear control
  -> detail or setup route
  -> optional AI proposal with evidence
  -> result and reconciliation
~~~

Do not let a decorative surface answer these questions ambiguously. A glowing power button that does not show a write failure is less native, not more native.

## Use HomeKit vocabulary without exposing the entire graph

| Framework concept | Design language | Default visibility |
| --- | --- | --- |
| Home | Home | Visible when multiple homes are possible or the action could affect the wrong location. |
| Room | Room | Visible in context and useful in lists, detail, and confirmation. |
| Accessory | Device or accessory | Use the person’s name first; technical manufacturer fields belong in detail. |
| Service | Feature or control | The primary card can be service-centric when the task is focused. |
| Characteristic | State, setting, or reading | Show the unit, range, and freshness when they affect a decision. |
| Action set | Scene | Use scene in user-facing copy; describe exact effects before execution. |
| Matter commissioning | Add device | Prepare, then hand off to the system-owned setup flow. |

An accessory can expose multiple services and a service can be what Apple Home presents as an accessory. A focused app may group services by task, but it should not silently change the selected home or room. Keep the underlying identity available in the detail route and accessibility labels.

## Native screen architecture

### Home context

Use a compact context label, menu, or picker that shows the selected home. If the product supports only one home, say that plainly and still handle a home change or no-home state. Do not default to the first array item as an invisible product choice.

For iPhone:

- keep the selected home discoverable at the top of the task;
- use a list or grouped stack for service summaries;
- open detail in a navigation destination or sheet with preserved identity;
- let the primary action remain reachable without scrolling through diagnostics.

For iPad and wider windows:

- use a split view or two-column layout when a room/service list and detail can remain visible together;
- preserve selection when a value updates;
- do not turn wide space into a dense technical inspector unless diagnostics are the product.

### Service summary

A good service row or card has:

- user-facing service or accessory name;
- room or home context when ambiguity is possible;
- current value and unit;
- reachability or freshness cue;
- one primary semantic control;
- a detail affordance for secondary capabilities.

Avoid showing raw UUIDs, manufacturer identifiers, or every characteristic on the primary surface. Use those in diagnostics or support routes.

### Detail and setup

Detail is for secondary characteristics, metadata, rename/room context, support, and recovery. Setup is a separate trust flow. Keep an add-device button near the feature it enables, but do not make the person infer why HomeKit or Matter access is needed.

The preparation screen should name the destination home, the physical device requirement, the setup-code step, and the likely system handoff. After setup, return to a fresh topology projection instead of pushing a hard-coded new card.

## State is the visual hierarchy

Use state-specific design rather than one card with a tiny error label:

| State | Content | Interaction |
| --- | --- | --- |
| Loading home | Home context plus concise progress | Preserve navigation; avoid fake device values. |
| No permission | Why access matters and next Settings step | No controls that imply HomeKit access exists. |
| No homes | Create/select/setup guidance | Do not display an invented empty home. |
| Empty selected home | Honest empty state and add-device action | Keep non-HomeKit features available. |
| Current value | Value, unit, and semantic control | Allow action if writable and reachable. |
| Cached/stale | Last-known value plus last-seen cue | Offer refresh/details; avoid “current” language. |
| Pending write | Target value and progress | Prevent conflicting actions intentionally; allow safe cancellation if supported. |
| Write failed | Prior known state and explanation | Retry or support; do not leave optimistic state in place. |
| Unreachable | Identity and last-known value | Disable or gate risky action; explain the boundary. |
| Removed/blocked | Changed-home explanation | Invalidate drafts and navigate safely. |
| Unsupported Matter | Device/platform reason | Keep setup alternatives and non-pairing paths. |
| AI proposal | Exact targets, values, warnings, source revision | Review and explicit apply; never auto-execute. |

Use motion to maintain continuity between these states. A morph from a service row to detail can preserve identity. A looping shimmer should not pretend that the network is making progress when the accessory is unreachable.

## Control selection

Choose the native control that matches the state semantics:

| Task | Control | Guardrail |
| --- | --- | --- |
| Stable Boolean state | Toggle | Only when the value and inverse target are clear. |
| Bounded numeric state | Slider or Stepper | Show unit, range, and pending/reported distinction. |
| Enumerated operating mode | Picker | Expose supported values and current value; do not invent options. |
| One-shot action or scene | Button | Show result state; do not represent it as a sticky Boolean. |
| Door, lock, alarm, heater | Button plus confirmation | Explain the device, room, target, and consequence. |
| Add device | Button to system flow | Keep pairing UI system-owned. |
| Room/home selection | Picker or menu | Keep the selected context visible after selection. |

A native control is not automatically accessible or truthful. Set labels, values, hints, and actions from the same projection that feeds visible state. Do not let a view-local binding bypass the command owner.

## Liquid Glass composition

Use Liquid Glass to group related app-owned content:

~~~text
glass context group: home and room
glass service group: identity, state, primary control
glass utility group: details, refresh, support
system-owned setup: HomeKit/Matter presentation
review group: AI proposal, source context, validation, apply
~~~

Rules:

- keep glass bounded to functional groups;
- preserve strong contrast behind state and localized names;
- place the state label near the control;
- use tint as a secondary signal, never as the only status;
- retain semantic controls and system focus behavior;
- provide opaque/system-material fallback for reduced transparency and unsupported targets;
- test large Dynamic Type and long translated room names;
- avoid animating a desired value as if a physical write already completed;
- keep confirmation and cancellation visually distinct from decoration.

Do not copy Apple Home’s private tab hierarchy, icons, or exact screen composition. Use system terminology and behavior while giving the app a focused task model.

## Setup and commissioning design

### HomeKit setup

The app-owned screen answers:

- What accessory is being added?
- Which home receives it?
- Is the setup code or physical device required?
- What will the system ask the person to approve?
- What happens if setup is cancelled or denied?

Then call the documented HomeKit setup API. The system can handle scanning, code verification, naming, and room assignment. When it returns, show a short result state and rebuild the home projection.

### Matter setup

Matter commissioning needs a stronger trust sequence:

~~~text
identify device
  -> show home destination
  -> system picker/criteria
  -> credential and onboarding validation
  -> network or Thread choice when required
  -> commission
  -> configure room/name
  -> reconcile and show readiness
~~~

Do not collect Wi-Fi credentials in a custom form when the supported system/extension route provides that selection. If the product supplies a QR payload, make the source and validation visible and keep it out of logs. Separate cancelled, unsupported, denied, commissioning-failed, commissioned, and commissioned-but-unreachable states.

## Reviewable AI surfaces

An on-device model can help a person explore a selected home snapshot:

- “Which room has the devices currently reporting as on?”
- “Draft a bedtime scene from the living room lights and thermostat.”
- “Explain why this device is unavailable.”

The design should show:

1. selected home and room;
2. source revision or last refresh;
3. device/service names and exact values;
4. warnings about stale, unreachable, or ambiguous data;
5. proposed writes or scene effects;
6. explicit review and apply controls.

Never show “AI turned off the lights” when the model only drafted a proposal. Never infer occupancy, safety, or consent from a sensor value. Never allow a model to choose a device by fuzzy name without deterministic resolution and a confirmation view.

Use a compact review card rather than a chatbot that hides side effects:

~~~text
Proposal
Home: Downstairs
Room: Living Room
Changes: Floor lamp -> off; thermostat -> 68°F
Source: current snapshot, refreshed 12:42 PM
Warnings: thermostat value is stale
[Review changes] [Cancel]
~~~

If the person changes the selected home, room, or service while the proposal is open, invalidate or re-evaluate the proposal. A source revision should be visible in debugging and available to support; it need not become technical clutter in the main UI.

## Privacy and trust surfaces

Home data can expose routines, occupancy patterns, camera presence, locks, alarms, and network context. Design for least disclosure:

- do not show private room names on a public or lock-screen surface by default;
- mask or omit sensitive device details when the app is backgrounded or protected;
- avoid putting full home graphs into analytics;
- keep onboarding codes, credentials, and attestation material out of logs and model prompts;
- explain optional cloud features separately from local control;
- preserve local controls when a model or cloud service is unavailable;
- make permission denial and Settings recovery understandable.

HomeKit’s product-purpose and privacy constraints are not solved by a beautiful card. The app must be primarily about home configuration or automation when it uses HomeKit, and it must not repurpose home data for unrelated advertising or profiling.

## Accessibility and input

Provide:

- VoiceOver labels containing home, room, device/service, state, and freshness;
- accessibility values that distinguish last known from current or pending;
- custom actions that use the same validation and safety gate as visible controls;
- visible focus and reliable post-write focus retention;
- keyboard and pointer activation on iPad and Mac-like input;
- Voice Control names that match visible labels;
- Dynamic Type layouts that do not hide the primary action;
- reduced motion and reduced transparency behavior;
- color-independent error, reachability, and pending signals.

Test setup and confirmation with VoiceOver, not only the dashboard. A system-owned picker can change focus and return in a different state; the app must restore context without dropping the person in an unrelated route.

## Adaptive platform design

| Environment | Design focus |
| --- | --- |
| iPhone | Fast service control, clear home context, compact detail, physical-device trust. |
| iPad | Split view, multiple rooms, pointer/keyboard, Stage Manager resizing. |
| watchOS companion | Glanceable state and bounded actions; do not assume full home graph or setup parity. |
| Mac Catalyst | Verify HomeKit target behavior; MatterSupport calls may return errors. |
| Widgets or system surfaces | Use only projections safe for the surface; do not expose private device state without an intentional policy. |

The platform matrix is a proof plan, not a promise that every framework route exists on every target.

## Design review checklist

- Does the selected home remain visible when the control could affect multiple locations?
- Can a person tell current, cached, pending, unreachable, and unknown apart?
- Does every write use a single command owner and a post-write reconciliation path?
- Are lock, door, heater, alarm, and similar controls explicitly confirmable?
- Does setup hand off to HomeKit or Matter system UI rather than imitate it?
- Does the AI surface show exact targets, values, source revision, warnings, and an apply decision?
- Does Liquid Glass group function without hiding status or reducing contrast?
- Does the UI survive VoiceOver, Dynamic Type, keyboard/pointer input, reduced effects, and long localization?
- Does the empty, denied, unsupported, removed, and revoked state retain a useful recovery route?
- Is the screen recognizable as the app’s focused task rather than a clone of Apple Home?

## Sources

- [HomeKit Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/homekit)
- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Enabling HomeKit in your app](https://developer.apple.com/documentation/homekit/enabling-homekit-in-your-app)
- [Configuring a home automation device](https://developer.apple.com/documentation/homekit/configuring-a-home-automation-device)
- [Interacting with a home automation network](https://developer.apple.com/documentation/homekit/interacting-with-a-home-automation-network)
- [Testing your app with the HomeKit Accessory Simulator](https://developer.apple.com/documentation/homekit/testing-your-app-with-the-homekit-accessory-simulator)
- [HMHomeManager](https://developer.apple.com/documentation/homekit/hmhomemanager)
- [HMHome](https://developer.apple.com/documentation/homekit/hmhome)
- [HMAccessory](https://developer.apple.com/documentation/homekit/hmaccessory)
- [HMCharacteristic](https://developer.apple.com/documentation/homekit/hmcharacteristic)
- [HMAccessorySetupManager](https://developer.apple.com/documentation/homekit/hmaccessorysetupmanager)
- [MatterSupport](https://developer.apple.com/documentation/mattersupport)
- [Adding Matter support to your ecosystem](https://developer.apple.com/documentation/mattersupport/adding-matter-support-to-your-ecosystem)
- [MatterAddDeviceRequest.DeviceCriteria](https://developer.apple.com/documentation/mattersupport/matteradddevicerequest/devicecriteria)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
