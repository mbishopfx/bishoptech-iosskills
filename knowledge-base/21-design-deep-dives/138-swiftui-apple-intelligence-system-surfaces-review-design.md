# SwiftUI Apple Intelligence system-surfaces review design

This guide turns the Apple Intelligence, Writing Tools, Image Playground, Genmoji, Visual Intelligence, App Intents, Foundation Models, and Liquid Glass review into interface decisions. The central design rule is simple: use Apple’s system surface when the system owns the interaction, and use the app’s native SwiftUI surface to make the result understandable, reviewable, accessible, and useful.

## Design premise

An Apple-native AI feature should feel like a capability woven into the app, not a separate chatbot bolted onto every screen. Start with a useful non-AI task, then add intelligence where it removes friction:

| Task | Native entry point | App-owned follow-through |
| --- | --- | --- |
| Improve text | TextEditor or TextField with Writing Tools | Save, undo, selection, and document revision |
| Create an image | Image Playground system sheet | Copy the temporary result, preview, classify, and persist |
| Find visual content | Visual Intelligence result panel | Search entities, open the selected result, and show more results |
| Refer to visible content | AppEntity association | Resolve the stable entity and provide a safe transferable representation |
| Summarize or classify private records | App-owned Foundation Models feature | Availability state, progress, validation, review, and commit |
| Perform an action from natural language | App Intent or schema | Parameter resolution, authorization, confirmation, and domain action |

Do not make the person learn whether the app used Writing Tools, Foundation Models, Visual Intelligence, or a deterministic search unless that distinction affects trust, privacy, or expected behavior. Do make the distinction visible when it changes where data goes, whether a result is a proposal, or what fallback exists.

## Surface map

Use this hierarchy when composing a screen:

~~~text
navigation and title
    -> task content
        -> native text/media/system entry point
        -> app-owned state and provenance
        -> review and commit controls
    -> fallback and accessibility status
~~~

The main content should remain legible without the intelligence feature. A disabled or unavailable model should not leave a large empty card where the core workflow used to be.

### Writing Tools

For Text, TextField, and TextEditor:

- keep the system editing surface primary;
- use WritingToolsBehavior.automatic unless the content needs a narrower contract;
- use complete only when inline replacements, selection, layout, and undo are reliable;
- use limited when a final accepted replacement is safe but inline streaming is not;
- use disabled for code, protected content, or a field whose semantics cannot tolerate rewriting;
- let the system provide the affordance instead of duplicating it in a custom toolbar;
- keep document autosave and external synchronization quiet or revision-aware while Writing Tools is active;
- expose selection and focus with the same priority as generated actions.

For a custom text engine, design around the coordinator lifecycle rather than around a generic progress spinner. The editor needs a way to show text being evaluated, preview replacement regions, accept or reject changes, recover from stale ranges, and end the operation without losing edits made outside the system interaction.

### Image Playground

The system sheet should feel like a deliberate modal creation step, not an in-app image carousel. The app-owned screen behind it should:

- explain the purpose of the generated image in the context of the task;
- keep the original source or prior asset intact until the new result is approved;
- show an unavailable fallback when supportsImagePlayground is false;
- copy the temporary completion URL before leaving the completion handler;
- display the generated result as a candidate until the user chooses to save it;
- preserve a user-selected style or size only where the current API supports that option;
- avoid pretending that a system style picker is an app-owned brand style system.

If personalization uses a person or a photo, make the choice and its effect understandable. Do not infer a person’s identity or attributes in an app-owned panel when the system’s personalization controls already own that decision.

### Genmoji and rich text

Adaptive image glyphs should sit on the same baseline and text-selection model as surrounding characters. For a custom renderer:

- preserve the glyph’s content identifier and content description;
- retain the adaptiveImageGlyph attribute during formatting operations;
- give the glyph a text equivalent for accessibility;
- make cursor movement, selection, deletion, copy, and paste predictable;
- show an export fallback when the destination format cannot preserve the glyph;
- keep the glyph within the document revision rather than saving it as an unrelated image attachment.

Avoid placing an oversized decorative Genmoji above the text when the user created it as an inline character. The user’s document model should determine whether it behaves like text, an attachment, or a standalone image.

### Visual Intelligence

Visual Intelligence results are a search panel, not a marketing grid. Design entity representations for speed and clarity:

- title: the most recognizable localized name;
- subtitle: one differentiating fact, such as place, category, or date;
- image: a safe thumbnail that can load quickly;
- result count: limited to what the system panel can usefully display;
- open action: deterministic resolution by stable entity identity;
- more results: a route into the app’s search experience with the original semantic input;
- empty state: a concise explanation and an in-app alternative.

Do not put model confidence, internal IDs, or long summaries in the display representation. If a visual match is uncertain, use the app’s own review surface after the person opens the result.

### Onscreen context

Associate an AppEntity with a standard SwiftUI view when one entity represents the visible content. Use AppEntityUIElements when a custom-drawn view, Metal surface, gallery, or stateful canvas contains several entities and the system needs bounds, selection, or subelement information.

The visual affordance is not a badge that says “shared with Siri.” It is a context contract. Keep the association synchronized with the visible record, selected state, and current revision. Remove it when the record is no longer visible or authorized.

## Liquid Glass composition

Liquid Glass should group actions and support hierarchy. It should not turn the entire AI response into a translucent spectacle.

### Preferred layout

| Region | Content | Material guidance |
| --- | --- | --- |
| Top bar | Title, navigation, system entry point | Use native toolbar items and let the system handle placement |
| Content | Document, image, search result, or record | Prefer ordinary content backgrounds and readable typography |
| Status row | Availability, progress, route, source, or revision | A compact glass group can show transient state |
| Review group | Accept, edit, retry, dismiss, undo | Use native buttons and clear labels; glass should support grouping |
| Secondary detail | Provenance, privacy, model version, source | Use disclosure or a standard sheet rather than permanent visual noise |

Functional rules:

- keep text and primary imagery visually dominant;
- use a small number of glass containers with coherent spacing;
- preserve contrast over changing content;
- avoid stacking glass over glass unless the system component requires it;
- separate destructive or external actions from generated suggestions;
- do not use a sparkle icon as a substitute for a label;
- do not place an app-owned glass panel over a system-owned sheet to compete with it;
- use the system’s toolbar, sheet, menu, confirmation, and alert behavior before custom animation;
- ensure Reduce Motion and larger text remain usable;
- treat the material as adaptive appearance, not as a fixed color token.

### State-driven glass

The material and controls should follow state:

| State | Visual treatment | Required action |
| --- | --- | --- |
| unavailable | Ordinary fallback styling | Tell the user what still works |
| ready | Quiet native entry point | Allow the task to begin |
| active | Subtle progress and cancel | Prevent duplicate starts |
| candidate | Highlight the result but keep it editable | Approve, edit, retry, or dismiss |
| committed | Ordinary domain content | Offer undo where relevant |
| stale | Warning or neutral revision state | Re-run against current input |
| failed | Clear error with recovery | Preserve the last valid state |

## Trust and provenance

The visual system should help the person answer:

- What input did this use?
- Is this a proposal or committed content?
- Can I change it?
- Can I undo it?
- What happens if the model is unavailable?
- Did the app share anything beyond the device?
- Is the result from a system surface, an app model, or a deterministic search?

Use a small source row or disclosure sheet rather than a dense technical banner. A useful review card can contain:

~~~text
result title
short candidate content
source: selected note, image, or record revision
state: draft / needs review / saved
actions: Edit, Accept, Retry, Dismiss
secondary: Why this is available / Privacy / Model status
~~~

Do not expose raw prompts, hidden model instructions, personal-data summaries, or internal confidence values unless they help the user make a decision.

## Accessibility and alternate input

Generative features should add choices, not remove them:

- every generated result needs a readable label and an announced state;
- a loading animation must have a spoken or textual status;
- cancel, dismiss, retry, edit, and undo must be keyboard, VoiceOver, Switch Control, and Voice Control reachable;
- use Dynamic Type and avoid text embedded only in generated images;
- preserve a visible text or semantic equivalent for adaptive glyphs;
- expose selected state and bounds for custom AppEntityUIElements;
- do not require a visual scan or a color difference to understand a match;
- support reduced motion for generation and replacement transitions;
- keep the primary action reachable when the keyboard or writing tools surface is active;
- test landscape, split layouts where supported, large content sizes, and bold text;
- ensure voice responses can stand alone when an App Intent runs without a visible app scene.

The app’s accessibility label should describe the user action or content, not merely say “AI.” For example, “Summarize selected note” and “Generated illustration, not saved” are more useful than “AI button” and “Result.”

## Privacy and data boundaries

Use an input ledger for each route:

| Input | Owner | Sharing decision |
| --- | --- | --- |
| Selected text | User and app document | Send only the selected or requested context |
| Full document | User and app document | Share only when the operation needs it |
| Starting image | User and system sheet | Keep source and generated output separate |
| Screenshot pixel buffer | System capture | Process only for the requested bounded search |
| Ongoing onscreen entity | App | Associate only while visible and authorized |
| Personalization photo | User and system feature | Let the system own selection and explain persistence |
| Model prompt and output | App-owned feature | Keep revisions, privacy, and retention explicit |

Prefer on-device processing when it provides a good experience. If the system feature or app route may use Private Cloud Compute or a server, do not describe the feature as strictly on-device. Do not log raw screenshots, private notes, full prompts, or generated responses merely to debug a prototype.

## Navigation and system handoff

System integrations need a stable route back into the app:

1. create or resolve a stable AppEntity;
2. provide a localized DisplayRepresentation;
3. implement OpenIntent for the entity;
4. map the entity to a navigation route;
5. verify the route against current authorization and revision;
6. render the detail view;
7. offer the next action as a normal app control.

For Visual Intelligence more results, use the semanticContentSearch schema and carry the semantic input into the app’s search screen. For a Siri or onscreen context handoff, use appEntityIdentifier or userActivity only for content that is actually visible and current. Avoid a route that opens a generic home screen and makes the user repeat the original search.

## Model-result interaction patterns

Use one of these patterns:

| Pattern | Good for | Guard |
| --- | --- | --- |
| Inline revision | Writing Tools or a short refinement | Keep undo and reject visible |
| Candidate card | Summary, title, image, or classification | Require approval before persistence |
| Compare view | Rewriting or image variant selection | Preserve original |
| Suggested action | Low-risk shortcut | Validate parameters and provide undo |
| Search result | Visual Intelligence | Stable identity and OpenIntent |
| Quiet background enrichment | Tags or local indexing | Never silently change the user’s source content |

When the model is complementary, the primary task must still work without it. When the model is essential, the unavailable state must explain what the person can do next.

## Evaluation-facing design

Design fixtures before polish:

- short, long, empty, multilingual, and malformed text;
- selected versus full-document Writing Tools scopes;
- documents containing links, lists, attachments, and adaptive glyphs;
- Image Playground with no source image, source image, personalization disabled, unsupported styles, cancellation, and temporary-file loss;
- Visual Intelligence with labels only, pixel buffer only, both, no match, stale match, and many matches;
- entity visible, selected, scrolled off-screen, unauthorized, deleted, and revised;
- Foundation Model available, not eligible, not ready, cancelled, malformed, and semantically wrong;
- VoiceOver, Dynamic Type, Reduce Motion, keyboard, Voice Control, and appearance variants.

Evaluate the user experience as a state machine, not just as a screenshot. A beautiful candidate card is not a passing feature if the app cannot undo it, explain the source, or recover from a missing model.

## Design review checklist

- Is the core workflow useful without intelligence?
- Does the system own the presentation where Apple provides a system surface?
- Is the app’s contribution typed and bounded?
- Does the user know whether a result is a proposal or committed?
- Can the user cancel, reject, edit, retry, and undo?
- Does Liquid Glass group actions without obscuring content?
- Do Dynamic Type, VoiceOver, keyboard, Voice Control, and Reduce Motion work?
- Are AppEntity identifiers stable and synchronized with visible content?
- Does Visual Intelligence return concise localized results and a real OpenIntent?
- Does Image Playground copy temporary files before persisting them?
- Does rich text preserve adaptive image glyph attributes?
- Does Foundation Models show availability-specific fallback?
- Are privacy and model-processing claims honest?
- Is the final claim backed by compile, system, physical-device, archive, TestFlight, or release evidence?

## Sources

- [Apple Intelligence](https://developer.apple.com/documentation/technologyoverviews/apple-intelligence/)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [Writing Tools](https://developer.apple.com/documentation/uikit/writing-tools)
- [Customizing Writing Tools behavior for UIKit views](https://developer.apple.com/documentation/uikit/customizing-writing-tools-behavior-for-system-views)
- [Adding Writing Tools support to a custom UIKit view](https://developer.apple.com/documentation/uikit/adding-writing-tools-support-to-a-custom-uiview)
- [WritingToolsBehavior](https://developer.apple.com/documentation/swiftui/writingtoolsbehavior)
- [writingToolsBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsbehavior%28_%3A%29)
- [writingToolsAffordanceVisibility(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsaffordancevisibility%28_%3A%29)
- [Text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [NSAdaptiveImageGlyph](https://developer.apple.com/documentation/uikit/nsadaptiveimageglyph)
- [AttributedString.AdaptiveImageGlyph](https://developer.apple.com/documentation/foundation/attributedstring/adaptiveimageglyph)
- [Image Playground](https://developer.apple.com/documentation/imageplayground)
- [ImagePlaygroundOptions](https://developer.apple.com/documentation/imageplayground/imageplaygroundoptions)
- [ImagePlaygroundStyle](https://developer.apple.com/documentation/imageplayground/imageplaygroundstyle)
- [imagePlaygroundSheet(isPresented:concepts:sourceImageURL:onCompletion:onCancellation:)](https://developer.apple.com/documentation/swiftui/view/imageplaygroundsheet%28ispresented%3Aconcepts%3Asourceimageurl%3Aoncompletion%3Aoncancellation%3A%29)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [AppEntityUIElement](https://developer.apple.com/documentation/appintents/appentityuielement)
- [appEntityIdentifier(_:)](https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28_%3A%29)
- [Providing contextual cues to Apple Intelligence and Siri](https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [supportedModes](https://developer.apple.com/documentation/appintents/appintent/supportedmodes)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Siri HIG](https://developer.apple.com/design/human-interface-guidelines/siri)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
