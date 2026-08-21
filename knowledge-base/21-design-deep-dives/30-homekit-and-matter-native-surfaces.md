# HomeKit and Matter native surfaces

The best HomeKit or Matter interface feels native because it respects the person’s existing home model, uses system setup where Apple owns the flow, and makes device state and side effects legible. It should not be a clone of Apple Home. Use the framework’s concepts, terminology, accessibility behavior, and authorization boundaries, then give the product its own task-focused perspective.

## The composition contract

Build the surface around this sequence:

~~~text
home selection -> room or service context -> current state -> safe control
                                      -> optional proposal -> review -> side effect
                                      -> freshness/error/reconciliation
~~~

The screen needs to communicate four questions without opening a debug inspector:

1. Which home and room does this control belong to?
2. What feature is being controlled or observed?
3. Is the displayed value current, cached, unreachable, or unknown?
4. What exactly happens if the person activates the control?

The HomeKit HIG recommends using the HomeKit object model and terminology, deferring to settings made in Apple Home, and avoiding duplicate home configuration. These are not only copy rules. They prevent a custom UI from creating a second, contradictory model of a person’s home.

## Use the system vocabulary

| API concept | User-facing language | Design implication |
| --- | --- | --- |
| HMHome | Home | Allow multiple homes where the product can support them; show the selected home in context. |
| HMRoom | Room | Treat it as a meaningful label, not a map coordinate or measured floor plan. |
| HMZone | Zone or area | Use it for grouping rooms when it helps a task; do not invent a second taxonomy without explaining it. |
| HMAccessory | Device or accessory | Use the physical device when identity matters, but do not expose every technical field by default. |
| HMService | Feature or control | Make user-interactive services the primary action surface when the app is task-focused. |
| HMCharacteristic | Setting, reading, or state | Show the unit, range, freshness, and control affordance from metadata where appropriate. |
| HMActionSet | Scene | Say scene in the interface; keep action set as an implementation term. |
| Matter commissioning | Add device or set up device | Prepare the person, then hand off to the system-owned flow instead of rebuilding pairing UI. |

Apple’s guidance says a service can be what the Home app labels as an accessory. A custom app can use a different grouping, but it should not hide room, zone, or home information in an opaque settings page. A service-centric interface often gives a person a faster route to the task than a deep tree of accessory internals.

## Dashboard hierarchy

A strong home dashboard uses a quiet hierarchy:

1. A compact home switcher or contextual home label.
2. A primary task group, such as lights, climate, security, or media.
3. Service cards or rows with state, freshness, reachability, and one clear control.
4. A secondary detail route for less common settings.
5. A setup or troubleshooting route that explains permissions and unavailable hardware.

Do not turn every characteristic into a floating pill. A brightness slider, temperature value, and power control can share one semantic surface if they belong to the same service. A lock or garage door action deserves its own visible state and confirmation behavior.

For an iPad or a wider window, use a split view or two-column composition that preserves the home/room context while showing service details. For a compact iPhone width, collapse secondary metadata before shrinking the control below a comfortable hit target. Test the same task in portrait, landscape, Dynamic Type extremes, and reduced-transparency settings.

## Liquid Glass without false confidence

Liquid Glass is a material and interaction treatment, not a status model. A translucent control can make a stale temperature look live or a failed lock action look successful if the state hierarchy is weak.

Use these rules:

- Put content and state underneath the glass, not behind a decorative haze.
- Keep action clusters bounded with a clear identity; avoid a dozen unrelated glass islands.
- Use native controls and semantic labels so the UI works without custom appearance.
- Show a loading or pending state after a write; do not animate directly to the desired value and leave it there on failure.
- Use tint for an intentional action or status, but pair it with text, icon, or shape.
- Let system-owned HomeKit setup, authorization, and Matter pairing retain their native presentation.
- Prefer a sheet or confirmation dialog for high-consequence changes over an ambiguous tap animation.
- Use reduced transparency and increased contrast as design inputs, not afterthoughts.

The visual goal is a calm instrument panel that communicates the home’s state. Glass should organize the task and make an action easy to find; it should not imply that the app owns the accessory, network, or system database.

## State visibility patterns

Every service surface should make its state machine visible:

| State | Recommended treatment |
| --- | --- |
| Loading topology | Skeleton or concise progress state with the selected home context. |
| No authorized access | Explain what HomeKit access enables and provide the next safe step. |
| No homes | Offer create/select/setup guidance; do not show fake empty device cards. |
| Accessory unreachable | Preserve known identity and last-seen value, clearly label it stale, and offer retry/details. |
| Cached value | Show the value with a freshness cue when the decision depends on current state. |
| Write pending | Disable conflicting controls or serialize intentionally; expose cancellation where safe. |
| Write succeeded | Reconcile against the reported value and explain if the accessory is still transitioning. |
| Write failed | Keep the prior known state, explain failure, and provide retry or fallback. |
| External change | Update the surface without stealing focus or rewriting an in-progress edit. |
| Removed or blocked | Remove unsafe action affordances and explain that the home changed elsewhere. |
| Unsupported Matter or platform | Describe the limitation and preserve non-pairing features. |

Use animation to show continuity and change, not to hide uncertainty. A glass morph between a compact service row and its detail view is useful when the identity is preserved. A looping glow while the network is unavailable is noise.

## Setup and pairing surfaces

Accessory setup has a high trust requirement. The app-owned preparation screen should answer:

- What device is being added?
- Which home will receive it?
- What information will iOS ask the person to approve?
- Does the person need the physical device or its setup code nearby?
- What happens if setup is cancelled or the code is invalid?

Then use HomeKit’s or MatterSupport’s system flow. Do not imitate a pairing scanner, create a custom “Apple Home” button, or collect Wi-Fi credentials when the system flow is designed to provide them. If a product supports its own QR scanner for a Matter onboarding payload, make that an optional input to the supported pairing API rather than a replacement for the permission and commissioning contract.

For Matter device setup extension UI, keep firmware/attestation/network/room choices ordered by trust:

~~~text
identify device -> validate credential -> select home/room
                -> select network if required -> commission
                -> show result -> reconcile ecosystem state
~~~

Show a distinct failure state for invalid attestation, unsupported device criteria, no eligible network, cancelled system approval, and a device that was paired but is not yet reachable.

## Controls and safety-sensitive actions

Use semantic controls:

- Toggle for a clear Boolean service when the current and target values are unambiguous.
- Slider or stepper for a bounded numeric characteristic with visible units and range.
- Picker for enumerated modes, with the current value and unavailable options explained.
- Button for a one-shot scene or action, with an explicit result state.
- Confirmation for door locks, garage doors, alarms, heaters, or actions with material consequences.

Do not let a generated phrase such as “make it cozy” directly map to a heater write. Present the proposed interpretation, affected services, values, and timing. If the product supports a “run scene” shortcut, the shortcut should still pass through the same authorization and validation policy as the visible button.

Avoid using HomeKit or Apple Home logos as interactive app chrome. Apple’s HIG explicitly warns against creating custom HomeKit or Home app icons or mimicking Apple-provided designs. Use the product’s own identity, system SF Symbols where appropriate, and plain language such as “Works with HomeKit” when the compatibility relationship matters.

## On-device AI as a review layer

Home automation is a strong place for on-device intelligence, but it is also a strong place to overreach. Useful bounded AI tasks include:

- Summarize current conditions from an explicitly selected room or service set.
- Suggest a scene draft from natural language.
- Explain why a scene could not be created because a characteristic is read-only, unavailable, or out of range.
- Group repetitive controls into a proposed task view without changing the HomeKit hierarchy.
- Turn a user-approved scene into a concise accessibility description.

The review card should show source context, proposed services and values, confidence or uncertainty in plain language, and the final action the person must confirm. Keep the generated text separate from canonical HomeKit state. If the home changes while the proposal is open, invalidate or revalidate it instead of applying stale assumptions.

## Accessibility and alternate input

The essential task is not “see a glass card.” It is “know what is happening and safely control it.” Test:

- VoiceOver reading order: home, room, service, current state, freshness, control, result.
- Voice Control names that are unique and action-oriented.
- Dynamic Type with long room names, localized units, and multi-line errors.
- Switch Control and Full Keyboard Access for setup, control, confirmation, and retry.
- Reduced motion and reduced transparency without losing state visibility.
- Color-independent distinctions between on, off, pending, stale, unreachable, and failed.
- Hit targets and pointer hover/focus behavior on iPad and Mac Catalyst where the route is supported.

When a notification updates a characteristic, do not steal accessibility focus from a person editing another service. Announce a material change only when it helps the task, and offer a detail route for noisy sensor updates.

## Copy and localization

Prefer:

- “Living Room — 21° — updated 12 seconds ago”
- “Front Door Lock — locked”
- “Garage Door — unreachable; last reported open 8 minutes ago”
- “Set up a device in Apple Home”
- “Review scene: turn off 3 lights at 10:00 PM”

Avoid:

- “HomeKit unlocked the door”
- “AI knows everyone is home”
- “Instantly synced” when the value is cached
- “Pair with Apple HomeKit” as a product name or custom branded setup flow

Keep device names, room names, scene names, and error reasons user-provided or system-provided where possible. Preserve the original value and unit in localization; do not concatenate number and unit into an untranslatable string.

## Review checklist

Before approving a HomeKit or Matter surface, ask:

- Does the person always know which home and room are in scope?
- Does the UI defer to Apple Home’s configuration instead of duplicating it?
- Is every control tied to a current characteristic capability and freshness state?
- Is a safety-sensitive action visibly confirmable and reversible where possible?
- Does the system own pairing and authorization UI?
- Does Liquid Glass organize the task without masking stale/error state?
- Can VoiceOver, Dynamic Type, reduced transparency, and alternate input complete the same task?
- Does AI produce a reviewable proposal rather than a hidden side effect?
- Does the fallback remain useful without authorization, network, accessory, or Matter support?

## Sources

- [HomeKit HIG](https://developer.apple.com/design/human-interface-guidelines/homekit/)
- [HomeKit](https://developer.apple.com/documentation/homekit)
- [HMHomeManager](https://developer.apple.com/documentation/homekit/hmhomemanager)
- [HMHome](https://developer.apple.com/documentation/homekit/hmhome)
- [HMAccessory](https://developer.apple.com/documentation/homekit/hmaccessory)
- [HMService](https://developer.apple.com/documentation/homekit/hmservice)
- [HMCharacteristic](https://developer.apple.com/documentation/homekit/hmcharacteristic)
- [Interacting with a home automation network](https://developer.apple.com/documentation/homekit/interacting-with-a-home-automation-network)
- [MatterSupport](https://developer.apple.com/documentation/mattersupport)
- [MatterAddDeviceRequest](https://developer.apple.com/documentation/mattersupport/matteradddevicerequest)
- [Matter support in iOS](https://developer.apple.com/apple-home/matter/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
