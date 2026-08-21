# TipKit feature-discovery capability route

Use this route when an app needs contextual education for a non-obvious native feature. TipKit should make the right action discoverable at the right moment while leaving the feature usable without the tip. It is especially useful around Liquid Glass controls, on-device AI tools, custom layouts, media review, widgets, and system handoffs—but only when the tip describes one current action.

Read the [TipKit contextual feature-discovery deep dive](../42-framework-deep-dives/65-tipkit-contextual-feature-discovery.md), the [Liquid Glass discovery design](../21-design-deep-dives/85-tipkit-liquid-glass-feature-discovery-design.md), the [proof matrix](../60-verification/82-tipkit-proof-matrix.md), and the [route recipes](../70-code-recipes/100-tipkit-contextual-discovery-recipes.md) together.

## Route decision

| Need | TipKit route | Alternative |
| --- | --- | --- |
| Explain one non-obvious control near the task | `TipView` or `popoverTip` | Inline empty state or `help` modifier if the information is stable and always available. |
| Teach a feature in a small sequence | `TipGroup` with ordered/first-available priority | Optional tutorial/help flow if more than a few actions are needed. |
| Gate help on current feature state | `Parameter` + `Rule` | App-owned conditional copy when persistence is not needed. |
| Gate help after repeated behavior | `Event` donation + `Rule` | App-owned counter if TipKit history is not the right source of truth. |
| Explain a UIKit feature | `TipUIView` or UIKit popover container | App-owned `UIView` help region with the same accessibility contract. |
| Teach an on-device AI action | TipKit around the deterministic feature, then a separate AI review surface | A local help screen or empty state if model availability is variable. |

Do not use TipKit as a marketing channel, a mandatory onboarding wizard, or a substitute for permission and availability UI.

## Step 1: write the feature contract

Before defining a tip, write:

```text
feature identifier
person’s current task
one non-obvious action
safe starting state
deterministic completion condition
permission/device/model prerequisites
fallback/help destination
localization/accessibility terms
```

If the feature cannot be used safely from the current screen, do not make a tip eligible there. If the feature is unavailable on a device, the app should show an availability state rather than a tip that points to a disabled control.

## Step 2: define stable tip content

Create a `Tip` type with concise title/message, an optional familiar symbol, and no more than the actions that help a person begin or learn more. Keep strings product-owned and localized. If AI is involved, use it as an authoring aid or separate explanation—not as an unreviewed runtime copy generator.

## Step 3: choose the eligibility source

| Eligibility question | Source |
| --- | --- |
| Has the person used this feature? | Persistent `@Parameter` or app-owned state mirrored into a minimal parameter. |
| Has the person reached a meaningful threshold? | `Event` donation with bounded history/time range. |
| Is the person in the right current mode? | Parameter derived from the feature’s current state. |
| Should only one of several tips appear? | `TipGroup` and display-frequency configuration. |
| Is the feature temporarily unavailable? | Keep the TipKit rule false and render the availability explanation in the feature UI. |

The rule must represent benefit, not business pressure. “Has not purchased” is not automatically a reason to show a tip; “has opened the editor but never used the revision control” can be a valid product-learning signal if it is handled respectfully.

## Step 4: configure the datastore and frequency

Call `Tips.configure` before presenting any tip. Choose:

- application-default persistence for a single app;
- group-container persistence only for intentional app/extension sharing;
- CloudKit synchronization only with explicit account/container/entitlement proof;
- display frequency based on task cadence, often daily/weekly rather than immediate;
- debug/test reset only before configuration and never as ordinary production startup behavior.

Record configuration failures and continue with the feature. TipKit should be optional infrastructure.

## Step 5: present near the relevant control

Use a native TipKit presentation and place it near the target. For a Liquid Glass UI, keep the tip’s semantic hierarchy visible and avoid a second custom glass layer that competes with the system style. If a custom style is necessary, test content, actions, dismissal, contrast, Dynamic Type, and focus—not just the background material.

## Step 6: donate after product truth changes

When a person completes the feature action, update the app-owned state first, then donate the event or update the parameter. Do not use a tip impression, open, or dismissal as the feature completion event unless the product specifically defines that as the outcome.

For an AI feature:

```text
model produced result -> person reviews -> person accepts/edits -> app truth
                                                        |
                                                        +-> TipKit event/parameter
```

Keep model version, confidence, cancellation, and unavailable states outside the tip datastore unless a deliberately derived Boolean is required for eligibility.

## Step 7: sequence multiple tips

Use `TipGroup` when several tips belong to the same feature area. Choose ordered priority when the sequence is intentional and first-available when the next relevant tip depends on current state. Keep the group small and provide a Help route for people who dismiss all tips.

## Step 8: prove the route

The route is ready for implementation only after the proof plan names:

- target SDK/deployment availability;
- configuration success/failure and datastore location;
- rule transitions and event/parameter persistence;
- display-frequency and invalidation behavior;
- SwiftUI/UIKit placement and actions;
- accessibility and localization task runs;
- AI feature unavailable/cancelled/reviewed states;
- physical device/system appearance if persistence or CloudKit is claimed;
- Release target membership, entitlements, and privacy/account configuration.

## Stop conditions

Stop and redesign if:

- the tip is promotional, mandatory, or a multi-step tutorial;
- the feature is not usable without the tip;
- the rule depends on raw sensitive data or opaque AI profiling;
- the tip action bypasses confirmation or commits an external side effect;
- a custom glass clone replaces native TipKit semantics without need;
- the datastore/sync target is unclear;
- the implementation claims cross-device/system behavior without proof;
- test reset logic could run in production.

## Sources

- [TipKit](https://developer.apple.com/documentation/tipkit)
- [Tip](https://developer.apple.com/documentation/tipkit/tip)
- [Rule](https://developer.apple.com/documentation/tipkit/tips/rule)
- [Parameter](https://developer.apple.com/documentation/tipkit/tips/parameter)
- [Event](https://developer.apple.com/documentation/tipkit/tips/event)
- [Event donation](https://developer.apple.com/documentation/tipkit/tips/event/donate%28%29)
- [TipGroup](https://developer.apple.com/documentation/tipkit/tipgroup)
- [Tips.configure](https://developer.apple.com/documentation/tipkit/tips/configure%28_%3A%29)
- [Configuration options](https://developer.apple.com/documentation/tipkit/tips/configurationoption)
- [CloudKit container option](https://developer.apple.com/documentation/tipkit/tips/configurationoption/cloudkitcontainer)
- [Datastore location option](https://developer.apple.com/documentation/tipkit/tips/configurationoption/datastorelocation)
- [Display frequency](https://developer.apple.com/documentation/tipkit/tips/configurationoption/displayfrequency)
- [TipView](https://developer.apple.com/documentation/tipkit/tipview)
- [TipUIView](https://developer.apple.com/documentation/tipkit/tipuiview)
- [Offering help](https://developer.apple.com/design/human-interface-guidelines/offering-help)
- [Onboarding](https://developer.apple.com/design/human-interface-guidelines/onboarding)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
