# Interactive system snippet surfaces

## Design goal

An interactive App Intent snippet should feel like a focused native continuation of the person’s current task. It is not a miniature app screen and it is not a custom replacement for Spotlight, Siri, Control Center, or the Action button.

The durable design formula is:

    system invocation -> one clear result -> one or two useful next actions
      -> explicit confirmation when needed -> refreshed current state

The system owns the outer presentation, timing, placement, dismissal, and much of the surrounding Liquid Glass treatment. The app owns the content hierarchy, semantic controls, domain truth, privacy boundary, and honest fallback states.

## Surface anatomy

| Layer | Owner | Design question |
| --- | --- | --- |
| Invocation and outer container | System | Can the result be reached from the supported system experience without requiring a custom visual shell? |
| Snippet content | App | What is the one fact or decision the person needs now? |
| Interactive control | App Intent plus SwiftUI control | What is the smallest safe follow-up action? |
| Confirmation/cancel affordance | System plus snippet intent | Is the scope and consequence obvious before mutation? |
| Re-render | System plus SnippetIntent | Does the view show current domain truth after the action? |
| Full app handoff | App | Where does the person continue if the compact surface is insufficient? |

Do not design against an invented fixed pixel canvas. The snippet can be invoked in different system contexts, with different typography, contrast, safe-area, localization, and input behavior. Keep content compact and let the system establish the presentation.

## Hierarchy recipe

Use this order:

1. Identify the object or operation.
2. State the current status or result.
3. Show freshness or scope when it affects trust.
4. Offer one primary action.
5. Offer a secondary action only when it is clearly related.
6. Provide a full-app route when the task needs editing, authentication, or detail.

For example:

    “Morning review”
    “3 items waiting · updated 2 min ago”
    [Review next] [Open list]

Avoid:

- a dashboard of unrelated metrics;
- a scroll-heavy editor;
- duplicate navigation bars and tabs;
- a custom bottom sheet inside a system snippet;
- decorative glass layers that compete with the system container;
- model-generated copy that hides the source or certainty;
- a destructive control whose label is only an icon.

## Native controls before custom decoration

Use the system’s semantic SwiftUI controls first:

| Need | Prefer | Why |
| --- | --- | --- |
| One immediate action | Button with an AppIntent | The system understands the action and can re-run the snippet |
| True on/off state | Toggle with an AppIntent | State is legible to assistive technologies and re-rendering |
| Short mutually exclusive choice | Picker or a small set of labeled controls | Avoids custom selection semantics |
| Open full app context | Link or the documented open-app intent route | Makes the handoff explicit |
| Read-only status | Text, Label, ProgressView, and semantic grouping | Clear hierarchy without pretending the status is interactive |

Use custom drawing only for product-specific content that standard controls cannot express. A Canvas, image, or decorative shape does not create accessibility or interaction semantics automatically.

## Liquid Glass guidance

Interactive snippets participate in system-owned presentation. Apply Liquid Glass as a hierarchy and material rule, not as a repeated decoration:

- let the system provide the outer container and platform treatment;
- use standard controls and semantic typography so the system can adapt them;
- avoid placing opaque cards behind every line of content;
- do not stack multiple translucent layers to imitate an Apple surface;
- keep important text and controls readable over changing backgrounds;
- use current SwiftUI glass APIs only when the selected SDK supports them and the component genuinely needs a custom glass surface;
- test increased contrast, reduced transparency, and accessibility settings before keeping a custom effect;
- keep content visually calm when the result is shown over a system-owned context.

The closest Apple-native look usually comes from spacing, hierarchy, system symbols, Dynamic Type, platform controls, and correct handoff behavior, not from a high count of glass modifiers.

## State-driven composition

Model the snippet as a projection of domain state:

~~~text
unknown -> loading -> current | empty | needs-review | unavailable | failed
current + action -> pending -> current | failed
current + destructive action -> confirmation -> canceled | pending
~~~

Every state must have a view:

| State | Content treatment | Action treatment |
| --- | --- | --- |
| Loading | One short explanation and restrained progress | No duplicate taps; let the system retry or use a safe refresh |
| Current | Primary fact, source/scope, freshness if needed | One high-value action |
| Empty | Explain what is absent | Create, search, or open the relevant app destination |
| Needs review | Show the proposed value and source | Confirm, edit, or reject |
| Unavailable | Explain permission/device/model/service reason | Settings, retry, or manual fallback |
| Failed | Preserve the last confirmed value if safe | Retry or open the full app |
| Mutating | Use clear pending copy | Disable duplicate action where the system supports it |

Never show a success label before the domain write or external system handoff is complete. “Saved” means durable product state, not that an intent started.

## Interactive actions and re-rendering

Treat each button or toggle as a separate use case:

    visible state -> AppIntent validates -> domain write/reconciliation
      -> result/error -> SnippetIntent performs again -> new visible state

The snippet view should not own a hidden binding that becomes the source of truth. If a toggle is shown, its value must come from the snapshot fetched by the SnippetIntent. If an action fails, the next render must show the prior confirmed value.

Limit the number of actions. A snippet is strongest when it shortens one decision, not when it exposes a full workflow that should live in the app.

## Confirmation design

Use a confirmation snippet when the action is destructive, externally visible, financially meaningful, privacy-sensitive, or likely to be misunderstood without context.

Show:

- the exact object and account scope;
- what will change;
- the affected count or destination when known;
- whether the operation can be undone;
- a clear confirm label;
- a clear cancel path.

The system confirmation boundary should be treated as part of the design. Do not hide it behind a decorative custom button. If a person changes a parameter inside the snippet, the intent must read the updated value after confirmation returns.

## Apple Intelligence and model-generated content

Apple Intelligence can discover app actions and entities through App Intents, but the app does not control the system’s ranking, model, wording, context selection, or language support. Design the snippet so it remains correct when invoked from a direct Shortcut, Siri, Spotlight, Apple Intelligence, or a manual in-app button.

For an on-device AI workflow:

    source content -> typed proposal -> provenance/confidence -> snippet review
      -> person confirms -> AppIntent mutation -> refreshed record/snippet

The model may propose a label, destination, grouping, or summary. It must not silently perform a consequential action. Keep the original source visible or reachable, distinguish proposal from confirmed data, and preserve a manual path when the model is unavailable.

Avoid:

- “AI approved” language when no person approved the result;
- guaranteed accuracy, focus, safety, or health claims;
- exposing private model context in an entity title or spoken dialog;
- converting free-form output directly into a record identifier or command;
- a custom glass “AI confirmation” that bypasses the documented App Intent confirmation route.

## Accessibility and input

Design for:

- VoiceOver reading order that starts with object, status, then action;
- Voice Control names that match visible labels;
- Switch Control reaching every action without a gesture-only dependency;
- Dynamic Type without clipped titles or hidden confirm labels;
- increased contrast and reduced transparency;
- Reduce Motion without essential information depending on animation;
- localization expansion, right-to-left layout, pluralization, and voice-friendly dialog;
- keyboard, pointer, and external input where the invoking platform supports them.

Use semantic labels and values for icons, toggles, progress, and error states. A symbol such as a pin or trash can is not sufficient without an accessible action name.

## Privacy and trust

Snippets can appear outside the app’s main screen and may be spoken or shown while the person’s context differs from the app’s normal privacy assumptions. Minimize content in:

- titles and parameter summaries;
- static and interactive snippet text;
- voice dialogs;
- entity display representations;
- widget/control projections reused by the snippet.

Require app handoff or authentication for private details and operations whose authorization cannot be proven in the system context. On sign-out, account switch, deletion, or permission loss, invalidate or rebuild every projection that could expose the old state.

## Full-app handoff

The snippet should answer the small task itself when possible. Open the app when the person needs:

- long-form editing;
- authentication or account selection;
- a complex conflict resolution;
- a private detail that should not appear in a system surface;
- a media review or accessibility mode that needs more room;
- a nontrivial irreversible decision.

Route to the precise destination. Preserve the operation’s durable state so a failed or interrupted handoff can resume without claiming completion.

## Design review checklist

- [ ] The system surface is genuinely useful outside the app.
- [ ] The outer container is left to the system.
- [ ] The snippet has one clear hierarchy and no miniature navigation shell.
- [ ] Each interactive control maps to a narrow AppIntent.
- [ ] The snippet re-fetches current state after every action.
- [ ] Confirmation shows scope and consequence.
- [ ] Loading, empty, stale, unavailable, and failed states are designed.
- [ ] Model-generated content is labeled as a proposal and has a manual fallback.
- [ ] Private data and spoken text are minimized.
- [ ] Dynamic Type, VoiceOver, Voice Control, Switch Control, reduced motion, and reduced transparency are checked.
- [ ] Localization and right-to-left expansion are checked.
- [ ] The full-app handoff is precise and preserves durable state.
- [ ] Liquid Glass is restrained and does not cover content or duplicate system chrome.
- [ ] The supported invocation list is explicit; Control Center controls are not assumed to show snippets.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Alerts](https://developer.apple.com/design/human-interface-guidelines/alerts)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Displaying static and interactive snippets](https://developer.apple.com/documentation/appintents/displaying-static-and-interactive-snippets)
- [SnippetIntent](https://developer.apple.com/documentation/appintents/snippetintent)
- [ShowsSnippetView](https://developer.apple.com/documentation/appintents/showssnippetview)
- [AppIntent requestConfirmation with a snippet](https://developer.apple.com/documentation/appintents/appintent/requestconfirmation%28conditions%3Aactionname%3Adialog%3Ashowdialogasprompt%3Asnippetintent%3A%29-jxb8)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Button](https://developer.apple.com/documentation/swiftui/button)
- [Toggle](https://developer.apple.com/documentation/swiftui/toggle)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [App Intents updates](https://developer.apple.com/documentation/updates/appintents)
