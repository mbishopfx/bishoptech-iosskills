# TipKit contextual feature discovery

TipKit is Apple’s system for showing concise, contextual help that makes a new or underused feature discoverable. It is not a replacement for product onboarding, a marketing banner, an AI chat surface, or a mandatory tutorial. Apple’s Human Interface Guidelines describe tips as small, transient views that should relate to the task the person is performing now, stay brief and actionable, and remain easy to dismiss or avoid.

This page is the framework reference. Use the [TipKit feature-discovery capability route](../50-capability-recipes/88-tipkit-feature-discovery-capability-route.md) as the build worksheet, the [TipKit Liquid Glass discovery design](../21-design-deep-dives/85-tipkit-liquid-glass-feature-discovery-design.md) for native visual decisions, the [proof matrix](../60-verification/82-tipkit-proof-matrix.md) for evidence, and the [route recipes](../70-code-recipes/100-tipkit-contextual-discovery-recipes.md) for uncompiled sketches.

## The TipKit object graph

```text
Tip protocol
  | title / message / image / actions
  | rules / options / status
  v
Tips.configure(options)
  | persistent datastore and display-frequency policy
  v
TipView / popoverTip / TipUIView / UIKit containers
  |
  +-> Parameter state changes -> Rule eligibility
  +-> Event donations -> Rule eligibility
  +-> TipGroup currentTip/currentTipUpdates -> ordered presentation
  +-> user action/dismissal -> invalidation and feature completion
```

The app owns the feature state and the tip copy. TipKit owns the eligibility and display state after configuration. Keep the app’s source of truth separate from the tip datastore: a tip being shown does not prove the feature was understood or used, and a tip being invalidated does not prove the domain action succeeded unless the app separately records that action.

## `Tip` defines content and eligibility

A type conforming to `Tip` describes:

| Surface | Responsibility | Design boundary |
| --- | --- | --- |
| `title` | Short action-oriented heading | Make the feature’s benefit or action clear without promotional language. |
| `message` | Optional one-sentence explanation | Keep it brief; explain the current task, not the whole app. |
| `image` | Familiar symbol or feature image | Use a symbol associated with the feature; avoid repeating the same image directly beside the tip when it adds noise. |
| `actions` | Primary/secondary help buttons | Send the person to settings, a safe setup action, or more information; do not hide a destructive side effect in a tip action. |
| `rules` | Parameter/event eligibility conditions | Gate tips to people who might benefit now. |
| `options` | Display count, duration, and frequency exceptions | Use sparingly; default frequency and dismissibility are part of trust. |
| `status` and update sequences | Current eligibility/invalidation state | Observe state for presentation and tests, not as a substitute for product truth. |

If a tip has no rules, Apple documents that it can display until the person dismisses it or its display-frequency/option policy makes it ineligible. That is rarely the right default for a dense app. Add a deterministic rule based on current feature state or a meaningful event.

## Configure TipKit before displaying tips

Call `Tips.configure(_:)` during app initialization before tips display. The call can throw and must be handled as a real configuration state. By default, TipKit persists state in its application datastore and uses an immediate display frequency; configure a different datastore location or display frequency only when the product has a clear reason.

Possible configuration responsibilities:

- load the application-default datastore;
- choose an App Group container when multiple app/extension targets intentionally share tips;
- choose a named CloudKit container only after the target’s CloudKit and account proof exists;
- set a reasonable hourly/daily/weekly/monthly display frequency;
- surface configuration failure in diagnostics and keep the feature usable without tips.

Do not treat `Tips.configure` success as permission, subscription, account, or feature readiness. It only establishes TipKit’s persistent tip state and policy.

## Parameters are persistent feature state

`Parameter` monitors a value and causes dependent rules to reevaluate when the value changes. Apple documents parameters as persistent by default; `ParameterOption.transient` can make a parameter reset to its default value the first time it is referenced.

Use parameters for compact, non-sensitive state such as:

```text
hasUsedAdvancedFilter
hasSeenEmptyState
hasCompletedFirstExport
selectedModeIsAdvanced
```

Do not put raw personal data, free-form text, precise location, health values, credentials, or model output in a TipKit parameter. If a rule depends on sensitive domain state, derive the smallest Boolean/enum necessary and document its retention/sync behavior.

Parameter truth must come from the feature, not from the tip’s appearance. If a tip explains an export control, set `hasUsedExport` only after the export workflow reaches its own deterministic completion state—not when the tip is opened or when the person taps the tip button.

## Rules use parameters or events

`Rule` controls eligibility. Apple documents two core rule shapes:

1. **Parameter-based rules** track current app state.
2. **Event-based rules** track repeatable user interactions through donations.

The `#Rule` macro syntax is compiler- and SDK-sensitive, so treat code snippets as route sketches until they compile in the target. The conceptual contract is stable:

```text
tip eligible when parameter == desired state
tip eligible after event.donations satisfies threshold/time-window condition
```

A rule should answer “why would this person benefit right now?” If the answer is only “we want to announce a feature,” use an optional onboarding/help surface instead of forcing TipKit into a promotional role.

## Events and donations

An `Event` represents a repeatable user-defined action. The app donates the event asynchronously when the action occurs. Events can carry a `DonationInfo` value when it conforms to the documented Codable/Sendable constraints, allowing rules to inspect structured event history.

Use event donations for counts or bounded properties:

```text
didOpenAdvancedEditor
didCompleteExport(format: pdf)
didUseMode(mode: focus)
didViewFeature
```

Donations are not analytics by default and should not become a hidden telemetry pipeline. Keep event identifiers stable, bound stored history with a donation limit/time range when appropriate, and avoid including content that could identify a person or reveal sensitive behavior.

Donate after the app action has reached the correct product boundary. For an AI feature, that might be “review opened,” not “model generated output.” For a payment or deletion feature, it should be the confirmed result, not an intent or preview.

## Actions are help controls, not hidden automation

`Tips.Action` describes a control associated with a tip. Apple documents actions as buttons that help people get started or learn more. Give each action a stable identifier and a clear label. The handler should navigate to a safe, reversible, or clearly confirmed destination.

Good actions:

- “Try filter” -> focuses the existing filter control;
- “Open settings” -> navigates to the relevant settings page;
- “See example” -> opens a local example state;
- “Learn more” -> opens concise help.

Risky actions should not be concealed in a tip. A tip action that deletes data, shares private content, purchases, changes an account, sends a message, or triggers a physical-world effect needs the same explicit confirmation and authorization as the main UI.

## Tip options and invalidation

TipKit provides options such as maximum display count, maximum display duration, and ignoring the configured display frequency. Use options to keep help from becoming repetitive, not to force a marketing campaign through the system.

`Tips.Status` distinguishes at least:

- `available` — eligible for display;
- `pending` — not currently eligible;
- `invalidated(reason)` — permanently ineligible for the current datastore state.

Apple documents invalidation reasons such as action performed, display count exceeded, display duration exceeded, and tip closed. Keep the invalidation reason for diagnostics/test assertions, but never infer that a person completed a feature merely because a tip was closed or invalidated. Record feature completion separately.

## Tip groups sequence contextual help

`TipGroup` collects tips and exposes a current tip plus an async update sequence. It can present tips one at a time using an ordered priority or the first eligible tip. Use groups for a small, coherent set of tips within one task, not for a disguised multi-screen tutorial.

An ordered group should have a clear progression that does not require memorizing earlier tips. A first-available group is useful when several controls may be relevant but only one should interrupt the current task. Test the group when the first tip is pending, invalidated, dismissed, or completed.

## SwiftUI and UIKit presentation

SwiftUI provides `TipView` for inline tips and `popoverTip` for a popover anchored to a view. UIKit has `TipUIView`, `TipUIPopoverViewController`, and collection-view containers. Use the presentation that fits the task:

| Presentation | Use when | Risk |
| --- | --- | --- |
| Inline `TipView` | The surrounding content should remain visible and the help belongs in the flow | It can displace content; verify Dynamic Type and scroll behavior. |
| `popoverTip` | A control needs a short annotation without permanently changing layout | It can obscure the control or compete with system transitions; verify focus and dismissal. |
| UIKit tip view/popover | The feature lives in a UIKit hierarchy | Observe status updates and remove the view when no longer eligible. |
| Custom `TipViewStyle` | A product needs restrained visual adaptation | Preserve content hierarchy, actions, labels, dismissal, contrast, and platform behavior. |

Use a native TipKit surface first. A custom glass card that merely looks like a tip is not equivalent to TipKit’s persistence, eligibility, accessibility, or testing behavior.

## TipKit, Liquid Glass, and Apple-native polish

Liquid Glass is a shell around functional hierarchy, not a reason to display more help. Keep a tip adjacent to the control it describes, use the system-provided tip presentation when possible, and avoid stacking a tip on top of a glass toolbar, alert, sheet, and AI suggestion at the same moment.

For a glass-heavy screen:

- let the tip explain one current control;
- keep the tip’s text readable over changing material and appearance;
- preserve a clear action order and dismissal affordance;
- avoid using blur or translucency to hide an ineligible/unavailable state;
- keep Reduce Motion and Dynamic Type paths visible;
- do not use animated morphing to imply that the tip action succeeded.

## TipKit and on-device AI

AI can be adjacent to TipKit without controlling it invisibly:

```text
deterministic feature state -> TipKit eligibility
optional local AI observation -> reviewable explanation/proposal
person action -> app-owned feature truth
feature truth -> parameter/event update
```

Safe patterns:

- a tip teaches a deterministic AI feature after the person reaches the relevant screen;
- a local model proposes a concise explanation that the product team reviews before shipping as tip copy;
- an AI review card links to the feature while TipKit handles contextual discovery;
- a tip action opens a review surface rather than executing an unreviewed model proposal.

Unsafe patterns:

- AI decides to show a tip because it inferred a person’s private state;
- a generated tip copy is sent to people without localization/content review;
- a tip action silently performs a model-generated side effect;
- TipKit parameters store embeddings, transcripts, health data, or user profiling signals.

## Persistence, CloudKit, and multiple targets

TipKit’s default datastore is appropriate for a single app when local persistence is sufficient. A group-container datastore can coordinate tips across related targets only when App Group membership and schema ownership are deliberate. CloudKit synchronization should be treated as an optional system route with account, container, entitlement, development/production, conflict, privacy, and deletion proof.

Do not sync tips merely because the app already uses CloudKit. Decide whether “dismissed this tip” or “completed this feature” should be shared across devices, and keep those concepts separate. If the person uses multiple devices, a tip state arriving from another device may make local eligibility change; the app must still keep the underlying feature discoverable through settings/help.

## Testing controls

TipKit provides testing methods to show or hide all tips, show/hide selected tips, and reset the datastore. Apple documents that reset must happen before configuration and is primarily for testing the first-launch experience. Keep reset calls behind a test/debug boundary and never reset a production datastore on ordinary app launch.

Test with:

- first launch and already-used feature state;
- rule transitions before/after parameter updates;
- event donations below/at/above threshold;
- display frequency across multiple tips;
- action performed and tip-closed invalidation;
- group ordering/first-available behavior;
- app restart and process termination;
- App Group/CloudKit configuration failure;
- VoiceOver, Dynamic Type, Reduce Motion, contrast, and localization;
- AI unavailable/cancelled/low-confidence states when the tip points to AI features.

## Proof boundary

A rendered `TipView`, a successful `Tips.configure()`, a donated event, or a screenshot does not prove that the tip is useful, non-repetitive, accessible, localized, correctly synchronized, or tied to actual feature completion. Use the [TipKit proof matrix](../60-verification/82-tipkit-proof-matrix.md) for source, compile, fixture, UI, physical, system, and release evidence.

## Sources

- [TipKit](https://developer.apple.com/documentation/tipkit)
- [Tip](https://developer.apple.com/documentation/tipkit/tip)
- [Tip actions](https://developer.apple.com/documentation/tipkit/tip/actions)
- [Tip options](https://developer.apple.com/documentation/tipkit/tip/option)
- [Tip rules](https://developer.apple.com/documentation/tipkit/tip/rules)
- [Tip status](https://developer.apple.com/documentation/tipkit/tip/status-swift.property)
- [Tips](https://developer.apple.com/documentation/tipkit/tips)
- [Tips.configure](https://developer.apple.com/documentation/tipkit/tips/configure%28_%3A%29)
- [Tips configuration options](https://developer.apple.com/documentation/tipkit/tips/configurationoption)
- [TipKit datastore locations](https://developer.apple.com/documentation/tipkit/tips/configurationoption/datastorelocation)
- [TipKit CloudKit containers](https://developer.apple.com/documentation/tipkit/tips/configurationoption/cloudkitcontainer)
- [Parameter](https://developer.apple.com/documentation/tipkit/tips/parameter)
- [Rule](https://developer.apple.com/documentation/tipkit/tips/rule)
- [Event](https://developer.apple.com/documentation/tipkit/tips/event)
- [Event donations](https://developer.apple.com/documentation/tipkit/tips/event/donate%28%29)
- [TipGroup](https://developer.apple.com/documentation/tipkit/tipgroup)
- [TipView](https://developer.apple.com/documentation/tipkit/tipview)
- [TipUIView](https://developer.apple.com/documentation/tipkit/tipuiview)
- [Tips status](https://developer.apple.com/documentation/tipkit/tips/status)
- [TipKit invalidation reasons](https://developer.apple.com/documentation/tipkit/tips/invalidationreason)
- [TipKit reset datastore](https://developer.apple.com/documentation/tipkit/tips/resetdatastore%28%29)
- [Offering help](https://developer.apple.com/design/human-interface-guidelines/offering-help)
- [Onboarding](https://developer.apple.com/design/human-interface-guidelines/onboarding)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
