# Foundation Models native review shell with Liquid Glass

## Design objective

A Foundation Models feature should feel like a native iOS capability with a clear job, not like a chatbot pasted into a glass card. The person should understand:

- what the feature can do;
- what content is being sent to the model;
- whether the result is a draft or accepted data;
- when the model is unavailable;
- what will happen if they accept an action;
- how to correct, dismiss, retry, or report the result.

The Liquid Glass treatment should support hierarchy and interaction. It should not obscure source content or become a visual badge for intelligence.

This page is a design route for iOS 26 SwiftUI. The visual decisions are original composition guidance grounded in Apple’s Human Interface Guidelines and Liquid Glass documentation, not a pixel-copy recipe for an Apple app.

## State machine before styling

Model the feature state before choosing materials or animations:

| Phase | Meaning | Primary UI |
| --- | --- | --- |
| checking | The app is reading model availability | Short status plus progress; keep the manual path visible |
| unavailable | The model cannot run here | Reason, retry/settings guidance, deterministic fallback |
| ready | The feature can accept a bounded source | Input, curated examples, disclosure |
| preparing | The app is building a bounded prompt or tool context | Source summary and cancel |
| generating | The request is running | Progress, cancel, no fake certainty |
| partial | A stream has returned an incomplete result | Draft badge, editable fields, no commit |
| review | The proposal passed local validation | Source, generated fields, exact action preview |
| committed | The person accepted and the use case saved | Confirmation and undo where possible |
| refused | The model declined or guardrails blocked the request | Plain explanation and alternate path |
| failed | A tool, schema, asset, or context issue occurred | Specific recovery, no raw diagnostic dump |

A single Boolean such as isLoading cannot represent this contract. A glass surface that looks polished while the model is unavailable is still a broken experience.

## Native composition hierarchy

Use the following hierarchy for an AI-assisted screen:

1. navigation title and task identity;
2. source or current record;
3. generated result or editable proposal;
4. provenance and limitations;
5. primary accept or apply action;
6. secondary actions such as edit, retry, copy, dismiss, or choose another source;
7. model status and fallback affordance.

The generated content should be the content layer. Glass belongs around a compact control cluster or a floating action group when it improves reachability and separation. Do not place a large opaque-looking glass panel behind the entire document and then put another glass card inside it.

Prefer system-defined NavigationStack, toolbar, sheet, confirmationDialog, Form, List, Button, Toggle, Picker, TextField, and ShareLink behavior before custom styling. Standard controls inherit platform behavior and accessibility support that a custom replica must recreate manually.

## Review shell anatomy

A reliable review shell has five visible regions:

| Region | Purpose | Design rule |
| --- | --- | --- |
| Source header | Shows what the model saw | Use a short source title, type, time, and privacy boundary |
| Result body | Shows the proposal | Keep text selectable/editable and distinguish generated from saved |
| Evidence rail | Shows why a value exists | Link to source fragments, tool results, or a “not verified” label |
| Decision bar | Accepts or rejects | Make the consequence explicit; keep destructive actions separate |
| Status footer | Explains model state | Use concise labels such as On device, Draft, Needs review, or Manual mode |

For a string transformation, the result body can use a before-and-after editor. For a structured proposal, use editable fields that map one-to-one to the Generable properties. For a tool-grounded answer, show the source or query scope without exposing private database details.

## Liquid Glass rules for AI surfaces

### Use the system treatment first

Adopt the platform’s current Liquid Glass behavior through standard controls and containers. Only add custom glass where the design needs a clear floating relationship, such as:

- a compact review action group over scrollable content;
- an inspector or mode switch that needs separation from a media surface;
- a transient status capsule that communicates model phase;
- a toolbar cluster with related controls.

Keep the main content legible in light mode, dark mode, increased contrast, and on busy source imagery. A glass effect is a material relationship with the content behind it, not a substitute for hierarchy.

### Group related glass elements

Use GlassEffectContainer when several nearby glass elements should read as one interactive group or transition between related states. Keep the container’s contents semantically related. Do not use one giant container to make unrelated cards merge into a glossy dashboard.

Where a custom effect is needed, apply the current Glass and glassEffect APIs to a small semantic surface. Prefer a system shape or a shape that matches the control’s hit target. Let the system handle the material response rather than stacking blur, opacity, gradients, and shadows until the content becomes muddy.

### Keep content and controls separate

A useful default is:

- source and generated text in the normal scroll content;
- compact controls in the toolbar or safe-area action region;
- confirmation in a system sheet or confirmation dialog;
- error and availability states as normal readable content.

Do not hide the only explanation of a side effect behind a floating glass button. Do not make the user hunt for the distinction between “try again” and “apply.”

## Proposed SwiftUI shell

This is a route sketch. It communicates structure and API intent; compile it against the selected iOS 26 SDK before using it.

~~~swift
import SwiftUI

@available(iOS 26.0, *)
struct AIReviewShell<Source: View, Proposal: View, Actions: View>: View {
    let source: Source
    let proposal: Proposal
    let actions: Actions
    let phaseLabel: String
    let isDraft: Bool

    init(
        phaseLabel: String,
        isDraft: Bool,
        @ViewBuilder source: () -> Source,
        @ViewBuilder proposal: () -> Proposal,
        @ViewBuilder actions: () -> Actions
    ) {
        self.phaseLabel = phaseLabel
        self.isDraft = isDraft
        self.source = source()
        self.proposal = proposal()
        self.actions = actions()
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    source
                    proposal
                        .overlay(alignment: .topTrailing) {
                            if isDraft {
                                Label("Draft", systemImage: "wand.and.stars")
                                    .labelStyle(.titleAndIcon)
                                    .font(.caption.weight(.semibold))
                                    .accessibilityAddTraits(.isStaticText)
                            }
                        }
                }
                .frame(maxWidth: 720, alignment: .leading)
                .frame(maxWidth: .infinity, alignment: .center)
                .padding(.horizontal)
                .padding(.vertical, 24)
            }
            .navigationTitle("Review")
            .safeAreaInset(edge: .bottom) {
                GlassEffectContainer(spacing: 12) {
                    actions
                        .padding(.horizontal)
                        .padding(.vertical, 10)
                }
            }
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Text(phaseLabel)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .accessibilityLabel("Model status: \(phaseLabel)")
                }
            }
        }
    }
}
~~~

The route still needs app-specific focus management, cancellation, accessibility actions, error views, and commit validation. The presence of a GlassEffectContainer does not prove that the app follows the correct Liquid Glass spacing, material, or accessibility behavior.

## Action-bar hierarchy

Use one visually primary action per state:

| Phase | Primary | Secondary |
| --- | --- | --- |
| Ready | Generate | Choose source, use manual mode |
| Generating | Cancel | View source |
| Partial | Continue or edit draft | Cancel, discard |
| Review | Apply or Save | Edit, reject, retry |
| Committed | Done or View result | Undo, share |
| Unavailable | Use manual mode | Retry, learn how to enable |
| Refused | Try a different request | Use manual mode, report |
| Failed | Retry after recovery | View source, manual mode |

A glass action group should not place Apply, Delete, and Retry in identical pill shapes. Consequence, emphasis, and destructive semantics should remain obvious without color.

## AI disclosure and source trust

Disclose AI use near the feature’s first meaningful interaction and again where the person reviews generated content. The disclosure should explain the model boundary in ordinary language, for example:

- “Generated on this device when Apple Intelligence is available.”
- “This draft may contain mistakes. Review before saving.”
- “The search uses the selected local records.”
- “Nothing is sent to a server in manual mode.”

Do not claim “private” without identifying the actual data path. On-device generation, a network tool, Private Cloud Compute, and a third-party provider have different privacy and availability properties.

If the result is grounded in app data, show a compact “Based on” section. If a field is inferred rather than observed, label it as a suggestion. If a value is not found, show “Not found” instead of inventing an empty-looking default.

## Accessibility contract

### VoiceOver and semantic order

The accessibility tree should follow the decision path:

1. source identity;
2. model status and limitation;
3. generated result;
4. field labels and edit controls;
5. provenance;
6. primary action;
7. alternate actions.

Do not expose decorative sparkles, glass shapes, or redundant status text as interactive elements. Give the draft state a concise accessibility label such as “AI-generated draft, not saved.” If the result updates while the person is focused elsewhere, announce the change without repeatedly stealing focus.

### Dynamic Type and layout

Test at the largest supported Dynamic Type sizes. Do not rely on a single-line glass pill for the only label of a critical action. Allow action labels to wrap or move into a menu. Keep the review content scrollable and maintain a reachable decision bar.

### Reduce Motion and contrast

When Reduce Motion is enabled, avoid requiring a morphing glass transition to understand that the feature changed state. Use a stable layout and a short text/status update. Test increased contrast, bold text, color filters, and light/dark appearances. Never make “generated,” “saved,” or “error” distinguishable only through translucency or hue.

### Input and cancellation

Every generation route needs a visible cancel action and a deterministic behavior when the view disappears. A cancellation gesture must not accidentally apply a proposal. If a tool is running, communicate whether cancel stops the network/domain work or only stops waiting for the model response.

## Motion and interaction

Use motion to explain state changes:

- a compact status changes from checking to ready;
- the review bar appears after validation;
- a field receives focus after a person chooses Edit;
- a committed result returns to the source screen.

Keep animations short, interruptible, and subordinate to content. Do not animate the entire document whenever a single generated field updates. Avoid continuous shimmer that implies progress when the model is stalled or unavailable. Provide a textual status for every animated state.

## Failure-state visual language

| Failure | Person-facing copy shape | Avoid |
| --- | --- | --- |
| Model unavailable | “This feature is unavailable on this device. You can continue manually.” | Blaming the person or hiding the rest of the app |
| Assets loading | “Apple Intelligence is still preparing. Try again later.” | Endless spinner with no exit |
| Context too large | “That source is too long for this on-device draft. Choose a smaller section.” | Automatically uploading it without consent |
| Tool unauthorized | “The selected records aren’t available to this feature.” | Asking the model to work around permission |
| Refusal | “This request isn’t supported here. Try a narrower request.” | Arguing with or exposing guardrail internals |
| Invalid proposal | “Some fields need correction before saving.” | Saving the valid-looking subset silently |
| Cancellation | “Draft discarded” or “Generation stopped” | Treating cancellation as success |

## Native visual tokens

Use semantic tokens instead of hard-coded “Apple replica” values:

| Token | Default | Adaptation |
| --- | --- | --- |
| Content surface | system background and grouped background | Respect appearance and contrast |
| Glass surface | system Glass or glassEffect | Use only for compact controls |
| Primary text | primary | Never encode state only by color |
| Secondary text | secondary | Keep sufficient contrast and size |
| Draft accent | tint plus text/icon | Add a label and accessibility value |
| Destructive action | system destructive role | Separate from accept/apply |
| Radius and spacing | system control geometry | Re-check across Dynamic Type and iPad widths |
| Motion | short state transition | Reduce or remove under Reduce Motion |

The exact visual result depends on the system version, display, accessibility settings, and content behind the surface. A screenshot is useful design evidence, not a universal guarantee.

## Review checklist

Before calling a design ready for implementation:

- Can a person complete the task without the model?
- Is the model’s data path obvious?
- Is generated content visibly a draft until accepted?
- Can every result be edited, dismissed, retried, or reported?
- Is the primary action distinct from retry and destructive actions?
- Does the content remain readable without the custom glass?
- Does the layout work in portrait, landscape, iPad split view, and larger Dynamic Type?
- Does VoiceOver announce status and decision consequences in order?
- Does Reduce Motion preserve comprehension?
- Does a cancelled or failed tool leave domain state unchanged?
- Is the native system control used where one already matches the task?
- Has the design been inspected on a named physical device with the target iOS 26 build?

## What this page proves

This page defines a native visual and interaction contract for AI-assisted SwiftUI screens. It does not prove exact Liquid Glass rendering, accessibility success, or model behavior. Those require previews, accessibility inspection, UI tests, and physical-device evidence under the target system settings.

## Sources

- [Generative AI](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
