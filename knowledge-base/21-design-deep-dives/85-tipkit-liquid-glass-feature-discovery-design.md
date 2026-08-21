# TipKit Liquid Glass feature-discovery design

TipKit belongs at the edge of a task, not at the center of a launch funnel. Apple’s Human Interface Guidelines describe tips as short, contextual help for simple features and recommend making them direct, actionable, dismissible, and relevant to the current task. A Liquid Glass shell can make a tip feel native, but it should never turn contextual help into a persistent marketing layer.

Use the [TipKit contextual feature-discovery deep dive](../42-framework-deep-dives/65-tipkit-contextual-feature-discovery.md) for API semantics, the [capability route](../50-capability-recipes/88-tipkit-feature-discovery-capability-route.md) for implementation sequencing, the [proof matrix](../60-verification/82-tipkit-proof-matrix.md) for evidence, and the [recipes](../70-code-recipes/100-tipkit-contextual-discovery-recipes.md) for route sketches.

## Start with the task, not the tip

Ask:

```text
What is the person trying to accomplish now?
What one non-obvious control would make that task easier?
Can the feature be tried safely in one or two actions?
What deterministic app state proves the feature was used?
```

If the answer requires a sequence of more than a few actions, use an optional onboarding/help flow or a dedicated empty state instead. TipKit should point to the next useful action, not carry an entire product curriculum.

## Choose the right presentation

Apple’s HIG distinguishes popover, annotation-style inline, and hint-style inline tips. Match the presentation to the relationship between help and control:

| Design situation | Presentation | Liquid Glass guidance |
| --- | --- | --- |
| A toolbar or control has one unfamiliar action | Popover tip anchored to the control | Keep the anchor visible; do not cover the control with multiple glass layers. |
| A feature belongs in a scrollable content flow | Inline annotation | Let surrounding content remain readable at large Dynamic Type sizes. |
| Help is relevant to a section but not one specific control | Inline hint | Keep it visually subordinate to the task content. |
| The feature needs a safe hands-on example | Tip action into a preview state | Keep the example reversible and separate from production side effects. |
| UIKit surface or extension | TipUIView/popover UIKit route | Preserve the same status/eligibility model across frameworks. |

Do not place a tip where it blocks the primary action, a system picker, an active recording control, a keyboard field, a scroll target, or a VoiceOver focus destination.

## Glass composition rules

Use Liquid Glass for hierarchy and continuity, not decoration:

- keep the tip near the control it explains;
- use the platform tip surface before building a custom styled equivalent;
- group the tip with the existing control region rather than adding a floating glass island;
- preserve text contrast over light/dark, vivid, and dynamic backgrounds;
- use one clear action and an obvious dismiss path;
- avoid simultaneous tip, alert, sheet, tooltip, AI proposal, and onboarding overlays;
- allow the person to keep using the underlying feature after dismissing the tip;
- make status changes legible through text, layout, and semantics, not blur or motion alone.

If a custom `TipViewStyle` is necessary, treat the style as a presentation adapter. It must not remove actions, change the meaning of dismissal, make the tip persistent, or imply that an AI-generated suggestion is endorsed by the app.

## State map for a glass-heavy native screen

| Product state | Tip state | Surface behavior |
| --- | --- | --- |
| Feature not yet used and user is at relevant control | Eligible | Show one concise tip near the control. |
| Feature used successfully | Parameter/event updated | Let the tip become pending or invalidated through its rule; do not keep showing it because it looks good. |
| User dismissed tip | Tip closed/invalidation state | Respect dismissal; make help available later through a stable Help/Settings route. |
| Feature is unavailable due to permission/device/entitlement | Pending or separate app state | Explain the real blocker in the feature UI; do not show a tip that points to an unusable action. |
| AI feature is loading/unavailable | Eligible only if the deterministic feature is usable | Teach the feature’s actual control; never promise model availability through tip copy. |
| Tip configuration fails | Tip surface absent | The feature remains usable; diagnostics record the configuration error. |
| Multiple tips compete | TipGroup/frequency | Show one relevant tip, not a glass carousel of interruptions. |

## Copy that feels native

Use one or two sentences, direct verbs, and product terminology that matches the control:

```text
Good: “Pin a filter to keep it at the top of this list.”
Weak: “Unlock a powerful new way to supercharge your workflow.”
Good: “Tap Analyze to review this frame on your device.”
Weak: “Our intelligent engine will understand everything for you.”
```

The copy must stay accurate when permission is denied, a model is unavailable, the device is offline, or the app is running on another platform. Localize title, message, action labels, source-specific terminology, and accessibility output together.

## Actions and agency

Tip actions should help people get started or learn more. A button labeled “Try it” should navigate to a safe state or focus the actual control. If the action could modify data, share information, create a purchase, send a message, or invoke a physical device, the destination must provide the same confirmation and review as the primary workflow.

Avoid a tip action that:

- runs a model and commits its output without review;
- changes settings without a visible destination;
- opens a permission prompt with no explanation;
- sends the person into a dead end when the feature is unavailable;
- uses “Dismiss” as a hidden completion event.

## Accessibility is part of the tip layout

Verify the full task under VoiceOver and Dynamic Type, not just the tip’s existence:

- the tip title and message are read in the correct order;
- the anchored control remains discoverable and has a meaningful label/value;
- the action buttons describe their result;
- dismissal does not strand focus;
- inline tips do not interrupt the reading order of the main content;
- popovers do not hide a control that VoiceOver needs to activate;
- text remains legible with increased contrast and reduced transparency;
- Reduce Motion removes unnecessary tip entrance/morph effects;
- Voice Control can identify the visible action labels;
- keyboard, pointer, and Switch Control paths can reach the same feature.

If the tip points at a custom Canvas, chart, camera preview, or Metal surface, provide a semantic control and text explanation. Do not require visual inspection of a moving background to understand the tip.

## AI-adjacent discovery

TipKit and on-device AI should form a transparent chain:

```text
feature state -> TipKit eligibility -> person opens feature
feature input -> on-device model observation -> reviewable result
person confirms outcome -> app-owned truth -> TipKit parameter/event update
```

An AI model can power the feature the tip teaches, but it should not silently profile the person to decide when to interrupt them. If AI proposes tip copy or a contextual explanation, keep the proposal in a reviewable authoring workflow; ship localized, deterministic, product-owned strings.

## Frequency, quiet moments, and recovery

Set a reasonable default display frequency. A tip appearing immediately after every other tip can make a polished glass UI feel noisy. Respect task boundaries: avoid showing a tip while the person is entering text, handling a permission alert, recording media, paying, navigating a system picker, or recovering from an error.

If TipKit state is unavailable or reset, the feature should still provide a quiet Help route. A tip is a convenience, not the only way to discover or use functionality.

## Design review checklist

- Is the tip about one current task and one non-obvious feature?
- Can the person use the feature without seeing the tip?
- Can they dismiss or avoid it without losing access to the feature?
- Is the copy concise, localized, accurate, and non-promotional?
- Does the action lead to a safe, reversible path?
- Is the tip anchored to the correct control/content region?
- Does the Liquid Glass composition preserve hierarchy and contrast?
- Does the tip respect feature availability, permissions, and AI model state?
- Is app truth updated by feature completion rather than tip impression/dismissal?
- Does the experience work with VoiceOver, Dynamic Type, Reduce Motion, contrast, Voice Control, and keyboard input?
- Is repeated display controlled through rules, frequency, groups, or options?
- Is there a stable help/settings fallback if TipKit does not configure?

## Sources

- [Offering help](https://developer.apple.com/design/human-interface-guidelines/offering-help)
- [Onboarding](https://developer.apple.com/design/human-interface-guidelines/onboarding)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [TipKit](https://developer.apple.com/documentation/tipkit)
- [TipView](https://developer.apple.com/documentation/tipkit/tipview)
- [TipUIView](https://developer.apple.com/documentation/tipkit/tipuiview)
- [TipGroup](https://developer.apple.com/documentation/tipkit/tipgroup)
- [Tip actions](https://developer.apple.com/documentation/tipkit/tips/action)
- [Tip options](https://developer.apple.com/documentation/tipkit/tipoption)
- [Tips display frequency](https://developer.apple.com/documentation/tipkit/tips/configurationoption/displayfrequency)
- [Max display count](https://developer.apple.com/documentation/tipkit/tips/maxdisplaycount)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Dynamic Type](https://developer.apple.com/documentation/swiftui/dynamictypesize)
