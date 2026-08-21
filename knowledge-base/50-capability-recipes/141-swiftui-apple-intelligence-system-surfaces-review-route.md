# SwiftUI Apple Intelligence system-surfaces review route

This route card turns the Apple Intelligence system-surface review into implementation decisions. It is intended for an app idea that may combine Writing Tools, Image Playground, Genmoji, Visual Intelligence, App Intents, Spotlight, onscreen context, and Foundation Models. Use the route in order. Do not begin with a generic AI chat screen.

Read the [framework deep dive](../42-framework-deep-dives/110-swiftui-apple-intelligence-system-surfaces-review.md), [design guide](../21-design-deep-dives/138-swiftui-apple-intelligence-system-surfaces-review-design.md), [proof matrix](../60-verification/135-swiftui-apple-intelligence-system-surfaces-review-proof-matrix.md), and [recipes](../70-code-recipes/153-swiftui-apple-intelligence-system-surfaces-review-recipes.md) together.

## Route selector

| Desired outcome | First route | Add only when needed | First proof gate |
| --- | --- | --- | --- |
| Improve user-authored text | SwiftUI TextEditor or TextField with Writing Tools | AttributedString, selection, custom UIKit coordinator | Supported text editor and accept/reject/undo behavior |
| Generate a stylized image | SwiftUI imagePlaygroundSheet | ImagePlaygroundOptions, source image, personalization, restricted styles | supportsImagePlayground and temporary-file persistence |
| Preserve emoji-like generated content | Standard text view and adaptive image glyph attributes | Custom renderer, custom export format | Save/reopen rich-text fixture |
| Find matching app content from a camera/screenshot | IntentValueQuery with SemanticContentDescriptor | Pixel-buffer search, UnionValue, more-results schema | Supported Visual Intelligence invocation and OpenIntent |
| Make visible content available to Siri | AppEntity association | AppEntityUIElements, Transferable, user activity | Stable ID matches current visible content |
| Find app data in Spotlight | IndexedEntity and named CSSearchableIndex | IndexedEntityQuery and computed/deferred properties | Index, update, delete, and open result |
| Summarize or classify app-owned records | SystemLanguageModel and Foundation Models | Guided generation, tool calling, evaluated prompts | Available and unavailable model paths |
| Perform a real app action from language | AppIntent and an app schema | supportedModes, cancellation, undo, choice request | Parameter resolution, validation, and user confirmation |

A route is complete only when the system surface, app state, user review, domain truth, accessibility, privacy, and release artifact agree.

## Phase 0: write the boundary record

Before opening Xcode, write one record:

| Field | Example |
| --- | --- |
| User outcome | Turn a selected note into a shorter draft |
| System surface | Writing Tools |
| App-owned state | Note document revision 18 |
| Candidate output | Replacement AttributedString |
| Commit action | User taps Accept and saves revision 19 |
| Fallback | Manual edit and existing formatting controls |
| Sensitive input | Selected note text only |
| Evidence target | Physical device with Writing Tools, undo, rejection, and Dynamic Type |

If the request is “make it smart,” split it into an observable action. “Find the landmark in this screenshot,” “create a square illustration,” and “summarize these three records” are different routes.

## Phase 1: choose the system owner

Use this decision tree:

1. Does Apple provide a system UI that already owns the interaction?
   - Writing Tools: prefer the standard text route.
   - Image Playground: prefer the system sheet.
   - Visual Intelligence: implement the App Intents search contract.
2. Is the app exposing content or an action to Siri, Spotlight, or Shortcuts?
   - Define a stable AppEntity or AppIntent.
   - Prefer an app schema when the feature matches one.
3. Is the app transforming private data in a custom workflow?
   - Use Foundation Models only after availability, privacy, validation, and fallback are designed.
4. Is the action consequential?
   - Separate proposal from commit, add confirmation or undo, and log only the minimum safe metadata.

Do not use Foundation Models to reproduce a system surface that already has a better user-owned flow. Do not use a custom Glass panel to impersonate Siri, Writing Tools, or Visual Intelligence.

## Phase 2: configure the text route

### Standard text route

Use TextEditor or TextField whenever the app can. Decide:

- plain String or AttributedString;
- selection and focus ownership;
- WritingToolsBehavior.automatic, complete, limited, or disabled;
- Writing Tools affordance visibility;
- save and autosave behavior while the system is active;
- undo grouping and document revision;
- how links, attachments, lists, and adaptive image glyphs survive;
- what content is ignored, such as code or protected quotations.

### Custom text route

Choose UIWritingToolsCoordinator only when a standard view cannot render the product’s text engine. Then record:

- custom UIView and UIInteraction ownership;
- isWritingToolsAvailable gate;
- preferredBehavior and preferredResultOptions;
- context scopes and surrounding text policy;
- source revision and offset for every context;
- replacement transaction and stale-range behavior;
- selection, proofreading marks, previews, animations, and layout updates;
- limited versus complete rejection behavior;
- undo and cancellation.

If the custom engine cannot implement the range and lifecycle contract, choose the limited or disabled route instead of claiming complete support.

## Phase 3: configure the image route

Start with Image Playground availability:

1. Read supportsImagePlayground in the SwiftUI environment.
2. If false, show import, camera, or manual asset alternatives.
3. If true, present imagePlaygroundSheet only from a user task that benefits from generation.
4. Supply concepts and an optional source image, not a hidden prompt dump.
5. Apply ImagePlaygroundOptions only for behavior the product can explain.
6. On completion, copy the returned temporary URL to an app-owned destination.
7. Validate image dimensions, file type, storage quota, and user ownership.
8. Keep the result as a candidate until the user saves or applies it.
9. Delete the temporary or rejected copy.

If UIKit or AppKit owns the surface, use ImagePlaygroundViewController. Treat ImageCreator as a deprecated programmatic route and verify whether the deployment target still supports it before using it.

## Phase 4: preserve adaptive text content

If the app accepts system text input, test the entire document pipeline:

- input;
- selection;
- formatting;
- copy and paste;
- autosave;
- serialization;
- reopen;
- export;
- accessibility;
- search and indexing.

The adaptiveImageGlyph attribute must survive any custom attribute filtering. If the destination format cannot preserve it, choose a visible and accessible fallback. Never silently convert it to an empty string.

## Phase 5: implement Visual Intelligence search

The Visual Intelligence route is a typed search contract:

1. Define a lightweight AppEntity with stable identity and localized DisplayRepresentation.
2. Adopt one IntentValueQuery taking SemanticContentDescriptor.
3. Use labels when a general semantic search is enough.
4. Use pixelBuffer only when an image search is needed and the current target supports it.
5. Keep the search bounded and fast.
6. Return a limited list of matching entities.
7. Implement OpenIntent for each result type.
8. Use UnionValue when one query returns several entity types.
9. Add the semanticContentSearch schema for a more-results route.
10. Open the app at the search experience with the original semantic input.

The labels are not a canonical taxonomy and are not guaranteed to name the exact object. Do not use them as a destructive command without an additional app-owned confirmation.

### Visual result contract

| Field | Requirement |
| --- | --- |
| Stable identifier | Resolves to the current record or a clear not-found result |
| DisplayRepresentation title | Localized, concise, recognizable |
| DisplayRepresentation subtitle | One useful differentiator |
| Image | Bounded, safe thumbnail |
| Query latency | Fast enough for a system search panel |
| Result limit | Small initial set with an in-app more-results path |
| OpenIntent | Navigates to the entity and validates current state |

## Phase 6: expose onscreen context

For a standard SwiftUI view, associate an entity with appEntityIdentifier. For custom-drawn content, provide AppEntityUIElements with bounds, selected state, and subelements. For a cross-version or activity route, use NSUserActivity.appEntityIdentifier.

Make the association revision-aware:

| Event | Action |
| --- | --- |
| Record appears | Associate stable entity ID |
| Record changes | Update the displayed entity or its revision |
| Record leaves viewport | Remove or stop reporting association as appropriate |
| Record becomes unauthorized | Remove the association |
| Record is deleted | Resolve to not-found and remove index entry |
| User requests cross-app action | Provide only the selected safe representation |

If the system needs an image, PDF, plain text, or rich-text representation, conform the entity or value to Transferable with a bounded representation. Do not expose internal database files.

## Phase 7: add Spotlight and App Intent routes

Use IndexedEntity for the subset of app content that helps system search. Wrap only properties that are cheap, stable, and useful:

- @Property for direct values;
- @ComputedProperty for derived values;
- @DeferredProperty for values that can be loaded lazily and are not needed for every index operation.

Use a named CSSearchableIndex in production. Keep indexing idempotent by stable identifier, delete stale entities, and implement IndexedEntityQuery when the system needs to rebuild the index.

For actions:

- use AppIntent for app-specific behavior;
- choose an existing schema for common actions;
- define parameters and parameterSummary;
- validate authorization and current revision in perform();
- declare supportedModes;
- inspect systemContext.currentMode;
- adopt CancellableIntent for long-running work;
- adopt UndoableIntent for reversible mutations;
- use OpenIntent for navigation;
- use choice requests for ambiguity instead of guessing.

## Phase 8: add Foundation Models only where it helps

Define the model feature as a bounded proposal:

| Stage | Route decision |
| --- | --- |
| Availability | SystemLanguageModel.default.availability |
| Input | Snapshot selected records and redact unnecessary fields |
| Instructions | Version prompt and task contract |
| Session | Create, stream, cancel, finish |
| Output | Parse or keep as text candidate |
| Validation | Check source revision, allowed values, and business rules |
| Review | Show editable result and explain source |
| Commit | Save through domain service, not directly from model callback |
| Fallback | Deterministic summary, manual edit, or no-op |

Use guided generation or tools for tasks that need structured or exact behavior. Do not ask the base model to perform arithmetic, arbitrary code generation, or unsupported logical reasoning and then trust the prose.

## Phase 9: compose the native shell

Use an ordinary SwiftUI screen with:

- native navigation and toolbar;
- clear task content;
- a small availability or progress state;
- a review surface for proposals;
- native buttons for accept, edit, retry, dismiss, and undo;
- a disclosure for source and privacy;
- Liquid Glass only where it groups those controls.

The app-owned shell must work when:

- Apple Intelligence is off;
- the device is ineligible;
- the model is not ready;
- the user rejects generation;
- the system sheet cancels;
- the route returns no visual matches;
- the input is stale;
- accessibility settings remove animation or enlarge text;
- the app runs in a background App Intent mode.

## Phase 10: evidence and release

For each route, collect:

- target, SDK, deployment, and capability configuration;
- physical device and region/model readiness;
- system invocation or presentation;
- input and output fixtures;
- cancellation, unavailable, stale, and error states;
- accessibility checks;
- privacy and temporary-file handling;
- archive and entitlements;
- TestFlight installation and system-surface proof;
- App Store metadata and review notes where relevant.

The correct end state is not “the model answered.” It is “the user could complete the task safely and accessibly, with honest capability and privacy boundaries, on the intended signed build.”

## Compact route record

~~~yaml
route: image-playground
user_outcome: create a square illustration for a saved card
system_surface: ImagePlayground SwiftUI sheet
availability: supportsImagePlayground
input: user concepts plus optional selected source image
temporary_output: completion URL copied into app-owned storage
review: preview, replace, save, cancel
fallback: import or choose existing image
proof: physical device, cancel, persistence, accessibility, archive, TestFlight
~~~

## Sources

- [Apple Intelligence](https://developer.apple.com/documentation/technologyoverviews/apple-intelligence/)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [IndexedEntity](https://developer.apple.com/documentation/appintents/indexedentity)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [Providing contextual cues to Apple Intelligence and Siri](https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri)
- [AppEntityUIElement](https://developer.apple.com/documentation/appintents/appentityuielement)
- [appEntityIdentifier(_:)](https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28_%3A%29)
- [appEntityIdentifier](https://developer.apple.com/documentation/foundation/nsuseractivity/appentityidentifier)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [Visual intelligence app schema](https://developer.apple.com/documentation/appintents/app-schema-domain-visual-intelligence)
- [Writing Tools](https://developer.apple.com/documentation/uikit/writing-tools)
- [WritingToolsBehavior](https://developer.apple.com/documentation/swiftui/writingtoolsbehavior)
- [writingToolsBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsbehavior%28_%3A%29)
- [Adding Writing Tools support to a custom UIKit view](https://developer.apple.com/documentation/uikit/adding-writing-tools-support-to-a-custom-uiview)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [NSAdaptiveImageGlyph](https://developer.apple.com/documentation/uikit/nsadaptiveimageglyph)
- [AttributedString.AdaptiveImageGlyph](https://developer.apple.com/documentation/foundation/attributedstring/adaptiveimageglyph)
- [Image Playground](https://developer.apple.com/documentation/imageplayground)
- [ImagePlaygroundOptions](https://developer.apple.com/documentation/imageplayground/imageplaygroundoptions)
- [ImagePlaygroundStyle](https://developer.apple.com/documentation/imageplayground/imageplaygroundstyle)
- [imagePlaygroundSheet(isPresented:concepts:sourceImageURL:onCompletion:onCancellation:)](https://developer.apple.com/documentation/swiftui/view/imageplaygroundsheet%28ispresented%3Aconcepts%3Asourceimageurl%3Aoncompletion%3Aoncancellation%3A%29)
- [ImageCreator](https://developer.apple.com/documentation/imageplayground/imagecreator)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [supportedModes](https://developer.apple.com/documentation/appintents/appintent/supportedmodes)
- [IntentModes.Current](https://developer.apple.com/documentation/appintents/intentmodes/current)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Siri HIG](https://developer.apple.com/design/human-interface-guidelines/siri)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
