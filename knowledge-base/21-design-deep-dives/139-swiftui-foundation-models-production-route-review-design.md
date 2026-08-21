# Foundation Models production-route design for SwiftUI

This design guide turns an on-device model request into a native iOS 26 screen that remains understandable when the model is unavailable, slow, cancelled, wrong, refused, or updated. It is for apps that want Apple-native polish and Liquid Glass hierarchy without pretending to own an Apple system surface.

The central design rule is simple:

The model proposes. The app explains. The person decides. The domain layer commits.

## The screen state machine

Model state should be explicit and renderable. Avoid a single Boolean called isLoading because it cannot distinguish model readiness, active generation, approval, cancellation, or failure.

| State | What the person sees | Allowed actions | Domain meaning |
| --- | --- | --- | --- |
| unavailable | Why the model lane cannot run and what still works | use fallback, learn more, retry later | no candidate exists |
| ready | A standard, discoverable AI affordance | start, edit input, dismiss | no work has started |
| preparing | A quiet progress state with cancel if the wait is meaningful | cancel | request owns resources |
| streaming | Partial output marked as draft or suggestion | stop, edit, dismiss | output is not committed |
| candidate | Complete typed or textual proposal with provenance | edit, retry, approve, dismiss | validation still required |
| tool approval | A concise explanation of the requested data or side effect | approve, deny, edit | no write is authorized yet |
| committing | Determinate progress for the app-owned operation | cancel only if the operation supports it | deterministic domain operation |
| committed | A normal product result with optional “created with assistance” provenance | undo, edit, share | domain state changed |
| cancelled | A quiet explanation and preserved user input when safe | retry, edit, dismiss | no late result may replace it |
| failed | Human-readable reason and fallback | retry, use fallback, report | no hidden partial commit |

State transitions should carry a request identifier. When a new request starts, the old request’s late result must not overwrite the new state. When a request is cancelled, clear or quarantine partial output and keep the user’s source material available when privacy policy permits.

## Native composition

### Use the system hierarchy first

Start with the same primitives used by the rest of the product:

- NavigationStack or the app’s existing navigation model;
- a prominent title and concise explanatory text;
- TextEditor or a standard field for user-owned input;
- a toolbar or inline Button with a clear verb;
- ProgressView for active generation;
- a ScrollView or List for reviewable output;
- confirmationDialog or sheet for consequential approval;
- alert for a failure that needs attention;
- a normal result screen after a commit.

The AI affordance should look like a feature of the app, not a floating assistant that competes with the app’s primary task. A label such as Suggest, Summarize, Draft, Find, or Organize is usually more honest than a generic sparkle icon with no explanation.

### Liquid Glass is a state-aware material

Use Liquid Glass to organize related controls and establish a legible hierarchy:

1. place the primary task content in the main surface;
2. group the AI action and its contextual controls in one container;
3. keep a persistent stop or cancel control easy to reach while generating;
4. use morphing or transitions only when the same action cluster changes state;
5. let the system handle contrast and vibrancy;
6. preserve a non-glass fallback for accessibility settings and older deployment paths.

Glass should not be used to make an uncertain answer look authoritative. A result card can be visually calm while still saying Draft, Suggested, or Needs review. Do not animate a candidate into a committed record without an explicit domain transition.

### AI controls need honest labels

Recommended control labels:

| State | Primary control | Secondary control |
| --- | --- | --- |
| ready | Generate suggestion | Clear or edit |
| preparing | Cancel | Hide |
| streaming | Stop | Edit source |
| candidate | Apply after review | Retry or edit |
| tool approval | Allow access or Confirm action | Deny |
| unavailable | Use standard workflow | Learn why |
| failed | Try again | Use standard workflow |

The exact wording should match the domain. “Apply” is not the same as “Send,” “Purchase,” “Delete,” or “Publish.” Consequential verbs should name the consequence.

## A reviewable AI card

A compact review card can contain:

- a title naming the task;
- a badge or secondary label saying Draft or Suggested;
- the source record or selection;
- output content in a readable type style;
- a short provenance line such as On-device suggestion when accurate;
- an optional model-version or prompt-version debug detail outside the main user flow;
- Edit, Retry, Dismiss, and the domain-specific approval action;
- an accessibility summary that states whether the content is partial, complete, or awaiting approval.

Keep generated prose visually subordinate to the user’s source content when the source is more authoritative. For structured output, show field labels and validation messages rather than dumping a raw JSON-shaped result. For a tool result, show which data was accessed and when it was retrieved.

## Input design and prompt boundaries

The screen should help the person understand what will be sent to the model or tool:

- show the selected source text, image, or record;
- allow the person to remove unrelated content;
- describe whether input stays on device or is sent to a configured external service;
- avoid copying hidden app state into a prompt without an intentional product reason;
- preserve user-authored text separately from generated text;
- make imported or network content visually distinct when prompt injection is a concern.

A prompt builder can conditionally include relevant sections, but the UI still owns selection, redaction, and consent. Do not let a long imported document silently consume the entire context budget. Provide a “use selected text” or “use this section” affordance when that is the safe default.

## Streaming without visual instability

Streaming output should feel alive without changing the layout on every token:

1. reserve a stable output region;
2. update text at a reasonable cadence;
3. keep controls fixed;
4. announce status changes to VoiceOver rather than every partial token;
5. show a stop action that remains available;
6. style partial content as draft;
7. promote the content to a review card only when the response finishes and validation succeeds;
8. discard a stale stream when a newer request wins.

Do not show a green checkmark while the model is still generating. Do not save every partial snapshot to the domain store. If the product needs draft persistence, save an explicitly labelled draft owned by the user, not a presumed final result.

## Guided generation and schema UX

Guided generation is a design contract as much as a technical contract. A small schema maps cleanly to a native review form:

| Generated field | SwiftUI review | Validation |
| --- | --- | --- |
| enum category | Picker or labeled choice | allowed category plus domain permission |
| bounded score | Slider or value label | numeric range plus semantic check |
| short title | TextField | length, empty, profanity or product policy |
| optional explanation | TextEditor or text block | length and sensitive-content policy |
| list of suggestions | List with selection | max count, duplicates, source |
| date or amount | native formatter/editor | deterministic parsing and authorization |

Schema descriptions should be short enough for context and clear enough for the model. A Guide can constrain a value, but the UI must still show what the person is accepting and the domain layer must validate it again.

If the model returns a typed candidate that cannot be decoded, keep the source input and offer a plain-text or deterministic fallback. A decoding failure is not a reason to show an empty success screen.

## Tool calling and approval surfaces

### Read tools

A read tool can fetch current app data or a narrow external value. Show freshness and source where it matters. If the tool reads personal data, keep the request and result within the product’s privacy policy. A model deciding to call the tool is not the same as the person asking for that data.

### Write tools

A write tool deserves a stronger visual and interaction boundary:

- show the proposed operation in domain language;
- list affected records or recipients;
- show data that will be sent;
- state whether the action is reversible;
- use a confirmation action that names the consequence;
- revalidate at commit time;
- provide undo or recovery where possible.

Never place a write tool behind a decorative “Continue” label. The approval surface should survive reduced motion, larger text, VoiceOver, keyboard navigation, and external input.

### Long-running tools

For a tool that may take time, use an explicit phase with progress when measurable, a cancel action, and an explanation of what remains local versus external. If the user leaves the screen, define whether the work continues, pauses, or is cancelled. Keep the view state separate from the durable operation state.

## Accessibility and alternate input

The native route must work with:

- VoiceOver;
- Dynamic Type and larger accessibility sizes;
- Reduce Motion;
- Increase Contrast and related display settings;
- Switch Control and Full Keyboard Access;
- hardware keyboard;
- pointer and trackpad;
- localization and right-to-left layout;
- reduced transparency or other material preferences where applicable.

Accessibility content should describe meaning and state:

- “Generate suggestion” instead of “sparkles”;
- “Draft response, still generating” instead of “loading”;
- “Suggested amount, review before applying” instead of a bare number;
- “Cancel generation” as an immediate action;
- “Model unavailable; use standard workflow” as the fallback label.

Do not rely on color, shimmer, blur, or animation to communicate whether output is draft or committed. Keep focus stable when a glass container morphs. When a sheet appears for approval, move accessibility focus to its heading and return focus to the initiating control after dismissal.

## Privacy in the visual design

Privacy is visible product behavior:

- explain on-device processing accurately, without claiming that every connected tool is local;
- disclose when input leaves the device;
- avoid showing private prompt content in notifications, logs, screenshots, or feedback attachments;
- provide a way to remove or narrow source material before generation;
- make transcript retention and deletion understandable;
- do not expose private records through App Intents, widgets, Spotlight, or system context without an intentional access policy.

The design can say “On-device suggestion” only when the route is actually using the on-device model. If a fallback uses a server, name the change.

## Platform adaptation

The same model route can appear in multiple shells:

| Platform context | Adaptation |
| --- | --- |
| iPhone | compact composer, bottom sheet or navigation destination, thumb-reachable cancel |
| iPad | split view with source and review side by side, keyboard-first actions |
| Mac Catalyst or macOS target | menu command, resizable inspector, full keyboard access |
| visionOS | spatial review panel, explicit focus and input affordance |
| widget or system surface | expose a narrow App Intent or snapshot, not a hidden multi-turn session |
| CarPlay or watchOS | only the approved platform route and category; keep attention and energy limits |

Do not place a full Foundation Models session inside a surface whose lifecycle or privacy contract cannot support it. Use App Intents or a deterministic handoff where the system surface owns invocation.

## Microcopy patterns

Use specific, non-magical language:

- “Draft a reply from the selected message.”
- “This suggestion is generated on device and may contain mistakes.”
- “Review before applying.”
- “The on-device model is not ready yet. You can use the standard editor.”
- “This action will update 3 items.”
- “The model could not produce a valid suggestion. Your original text is unchanged.”
- “No changes were made.”

Avoid:

- “The app knows what you mean.”
- “Guaranteed accurate.”
- “AI fixed it.”
- “Done” when only a proposal exists.
- “Apple Intelligence” as a product-owned brand claim unless the system surface and wording are actually appropriate.

## Design acceptance checklist

Before calling the screen native-ready:

- primary task and AI task are visually distinct;
- unavailable, not-ready, refusal, error, and fallback states are designed;
- streaming output is visibly provisional;
- cancellation remains available;
- typed candidates are editable and validated;
- tool writes require a domain-specific approval;
- no model output is saved as a committed record without a deterministic transition;
- Liquid Glass groups related controls instead of covering the content;
- reduced motion and accessibility sizes preserve the interaction;
- VoiceOver announces state and action meaning;
- keyboard, pointer, and alternate input work;
- privacy and data-flow copy match the actual route;
- iPhone and iPad layouts have been reviewed;
- physical-device behavior has been tested before release claims.

## Related local routes

- [Foundation Models production-route review](../42-framework-deep-dives/111-swiftui-foundation-models-production-route-review.md)
- [Foundation Models native review and Liquid Glass design](91-foundation-models-native-review-and-liquid-glass-design.md)
- [AI review shell and glass state](../20-liquid-glass/06-ai-review-shell-and-glass-state.md)
- [Adaptive AI screen and evaluation fixtures](../70-code-recipes/24-adaptive-ai-screen-and-evaluation-fixtures.md)
- [Tool approval and App Intents](../31-on-device-ai-recipes/07-tool-approval-and-app-intents.md)
- [Accessibility and adaptability checklist](../60-verification/02-accessibility-and-adaptability-checklist.md)
- [Privacy, performance, and release proof](../21-design-deep-dives/103-release-ready-native-design-and-privacy.md)

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Prompt](https://developer.apple.com/documentation/foundationmodels/prompt)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Guide(description:)](https://developer.apple.com/documentation/foundationmodels/guide%28description%3A%29)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Foundation Models updates](https://developer.apple.com/documentation/updates/foundationmodels)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
