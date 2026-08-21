# SwiftUI Apple Intelligence system-surfaces review

This review is a source-grounded route for iOS 26 apps that want to participate in Apple Intelligence, Writing Tools, Image Playground, Genmoji, Visual Intelligence, Siri, Spotlight, and on-device Foundation Models while still feeling native. It is deliberately a boundary document: a system-owned surface, an app-owned SwiftUI surface, and an app-owned model are different products with different availability, privacy, and proof requirements.

The current platform offers several complementary lanes:

| Lane | Primary owner | App contribution | What the app must not assume |
| --- | --- | --- | --- |
| Writing Tools | The system text-editing experience | Use standard text views, configure SwiftUI behavior, or bridge a custom UIKit text engine through UIWritingToolsCoordinator | A generated rewrite is not domain truth, and a custom editor does not gain support merely because it contains text |
| Image Playground | The system image-generation sheet or view controller | Supply concepts, an optional starting image, supported styles, options, and a completion URL | The device supports generation, the model is ready, or the temporary URL is durable |
| Genmoji and adaptive glyphs | The system text input and attributed-text pipeline | Preserve adaptive image glyph attributes in rich text and custom storage | A glyph is ordinary Unicode text or safe to discard when normalizing attributes |
| Visual Intelligence | The system camera or screenshot search experience | Provide an IntentValueQuery, SemanticContentDescriptor handling, AppEntity results, OpenIntent, and optional more-results route | Labels identify a precise object, one query may be registered per entity type, or a pixel buffer is a committed user request |
| Onscreen context | Apple Intelligence and Siri system experiences | Associate visible AppEntity identifiers or AppEntityUIElements, optionally use NSUserActivity and Transferable | Every visible view should expose data, or a local view model is automatically private-safe to share |
| Foundation Models | The app-owned feature using Apple’s on-device text model | Check SystemLanguageModel availability, create bounded sessions, validate output, and provide fallback | Model availability is universal, model output is guaranteed, or the model is a replacement for deterministic code |
| Native product shell | The app | Compose clear SwiftUI state, platform controls, accessibility, and Liquid Glass where appropriate | A custom sparkly panel is the same thing as a system Apple Intelligence surface |

Apple’s Apple Intelligence overview describes the system as a combination of language models, app actions, and app content. App Intents and App Entities are the contract that exposes the useful subset of an app’s actions and data. Writing Tools, Image Playground, Genmoji, and Visual Intelligence are separate system integrations with their own input and output contracts. Treat the framework boundaries as product decisions before writing a button.

## Ownership and route selection

Start by naming the user’s requested outcome rather than the model. The following questions choose the route:

1. Is the user editing text already in a text view? Prefer standard SwiftUI text views and the system Writing Tools experience.
2. Is the user creating a stylized image or emoji-like graphic? Prefer Image Playground’s system sheet. Use programmatic generation only when the current SDK and deployment target support the intended route and the product truly needs it.
3. Is the user searching for app content that matches a photo, screenshot, or camera observation? Use Visual Intelligence with an App Intents query and return lightweight entities.
4. Is the user referring to something visible in the app? Associate that entity with the view or user activity, and provide a transferable representation only when the user’s cross-app action needs it.
5. Is the app transforming or summarizing app-owned text without a system surface? Use Foundation Models only after checking availability and defining a deterministic fallback.
6. Is the action consequential, externally visible, destructive, paid, or privacy-sensitive? Keep model output as a proposal and require a separate user-reviewed commit.

This produces a useful architecture:

~~~text
system invocation
    -> typed app intent or system presentation
    -> app-owned input snapshot
    -> model or search proposal
    -> explicit user review
    -> domain validation
    -> committed mutation or navigation
    -> system projection and audit record
~~~

The system may perform intermediate work, display temporary state, or ask the person for confirmation. The app should not collapse those states into one Boolean such as aiFinished.

## Writing Tools

Writing Tools provides system proofreading, rewriting, summarization, and composition support for text views. UIKit’s standard UITextView and UITextField already support the feature. SwiftUI exposes environment modifiers for Text, selectable Text, TextField, and TextEditor.

The SwiftUI route has four relevant behavior values:

| SwiftUI value | Meaning | Use |
| --- | --- | --- |
| WritingToolsBehavior.automatic | Let the system choose an appropriate experience based on context | Default when the app has no content-specific reason to constrain the experience |
| WritingToolsBehavior.complete | Prefer the complete inline-editing experience if possible | Rich editors that can animate, reconcile, and undo inline replacements |
| WritingToolsBehavior.limited | Prefer the limited overlay-panel experience if possible | Editors that can safely incorporate a final replacement but cannot animate intermediate changes |
| WritingToolsBehavior.disabled | Disable Writing Tools for this environment | Code, protected records, generated output, or content where rewriting would violate the product contract |

Use writingToolsBehavior(_:) on the smallest view hierarchy that owns the text. Use writingToolsAffordanceVisibility(_:) when the product needs to control whether the system affordance is shown, especially for platform-specific or Mac Catalyst behavior. Do not build a second in-app Writing Tools panel merely to imitate the system surface.

Standard views are the preferred route because SwiftUI and UIKit already own text selection, keyboard behavior, rich text integration, and system interactions. The standard route still requires an app-owned model for the document, a revision policy, undo behavior, autosave coordination, and an answer to what happens when the person edits the text while Writing Tools is active.

### Attributed text and rich editing

For plain text, TextEditor(text:) is sufficient. For formatted text, use the TextEditor initializer that binds an AttributedString and TextSelection. The backing store must preserve attributes that the product does not render as visible characters, including adaptive image glyphs.

Treat a rich-text document as structured data:

| Document component | Persist? | Review |
| --- | --- | --- |
| Plain characters | Yes | Normal text validation |
| Formatting attributes | Yes when supported | Preserve only supported scopes |
| Links and attachments | Yes when the format supports them | Validate URL, attachment type, and security scope |
| Adaptive image glyph attribute | Yes | Preserve the glyph data and metadata; do not flatten to a placeholder |
| Writing Tools temporary replacement | No as an independent revision | Reconcile into the document only through the text system’s result |
| User-approved final change | Yes | Create an undoable, revisioned document mutation |

### Custom text engines

If the app uses TextKit or a proprietary text engine, use the UIKit Writing Tools APIs. UIWritingToolsCoordinator is attached to the custom UIView as a UIInteraction and communicates through its delegate. The custom view supplies text contexts, handles replacement proposals, updates selection, provides proofreading paths or previews when needed, and reports external edits or layout changes.

The custom route has a real cost:

- check UIWritingToolsCoordinator.isWritingToolsAvailable before attaching the interaction;
- choose preferredBehavior and preferredResultOptions from what the custom engine can actually render;
- supply requested context scope such as selection, full document, or visible area;
- include enough surrounding text for useful evaluation while respecting the requested range;
- map Writing Tools ranges back to the current text storage revision;
- apply replacements in a transaction owned by the text engine;
- distinguish limited final replacement from complete interactive replacement and rejection rollback;
- report external text or layout changes while Writing Tools is active;
- clear cached context mappings when the operation ends or the document changes;
- maintain undo grouping and selection state;
- leave the editor usable when the feature is unavailable or disabled.

The system can use local processing on suitable devices after required models are ready, while more complex requests can involve Private Cloud Compute. The app should communicate its own data handling clearly and should not promise that every request stays on-device merely because the app uses Writing Tools.

## Image Playground

Image Playground is a system interface for generating images from concepts, an optional source image, and a supported style. In SwiftUI, imagePlaygroundSheet presents the system sheet and returns a temporary file URL on completion. The system owns the interactive editing flow, available prompts, confirmation, and cancellation.

The SwiftUI sheet route is usually the correct default:

~~~swift
struct ImageCreationButton: View {
    @Environment(\.supportsImagePlayground) private var supportsImagePlayground
    @State private var isPresented = false
    @State private var savedImageURL: URL?

    var body: some View {
        Button("Create artwork") {
            guard supportsImagePlayground else { return }
            isPresented = true
        }
        .imagePlaygroundSheet(
            isPresented: $isPresented,
            concepts: [.text("A small paper boat on a moonlit lake")],
            sourceImage: nil
        ) { temporaryURL in
            savedImageURL = temporaryURL
        }
    }
}
~~~

This is a route sketch, not a claim that the snippet compiles in every deployment target. Confirm the current overload, availability annotation, and environment key in the SDK selected by the named app target.

When the system returns a URL, the file is temporary inside the app container. Move or copy it to an app-owned location before persisting a reference. If the user cancels, clear transient UI state without creating a document or an empty placeholder.

ImagePlaygroundOptions can configure:

- creation strategy for how a source image is interpreted;
- creation variety for variation across multiple results;
- personalization behavior;
- requested size and aspect ratio.

ImagePlaygroundStyle includes illustration, sketch, animation, and newer styles such as emoji or externalProvider where the SDK and device support them. Treat those values as capabilities, not as a permanent product guarantee. If the app supports a restricted set of styles, supply that restriction through the system options instead of showing choices the device cannot honor.

The ImagePlaygroundViewController is the UIKit/AppKit system-presentation route. ImageCreator is a programmatic route documented as deprecated in the current API surface; prefer the sheet or view-controller route for new features unless a named deployment target and migration plan justify the older API.

Generated images need a product contract:

| State | App-owned state | User-facing interpretation |
| --- | --- | --- |
| unsupported | No generation capability | Offer import, camera, or manual asset path |
| available but not presented | System can present | Show a clear entry point |
| presenting | System owns editing | Do not duplicate prompt or progress UI |
| completed temporary URL | Candidate asset | Copy, validate, and preview |
| user-approved persisted asset | Domain asset | Commit identity and metadata |
| cancelled or failed | No committed asset | Keep the prior state and explain recovery |

Do not infer content safety, brand suitability, or visual accuracy from the returned URL. Review generated content as user-provided or model-generated content according to the product’s risk.

## Genmoji and adaptive image glyphs

Genmoji-like content is represented in attributed text as an adaptive image glyph. Standard text views can receive and render this content through the system text-input pipeline. A custom rich-text engine must preserve the adaptiveImageGlyph attribute and the associated NSAdaptiveImageGlyph data when it copies, filters, serializes, or transforms attributes.

The essential identity is:

~~~text
NSAttributedString.Key.adaptiveImageGlyph
    -> NSAdaptiveImageGlyph
    -> imageContent, contentIdentifier, contentDescription
    -> persisted rich-text document
~~~

The Swift Foundation bridge exposes AttributedString.AdaptiveImageGlyph with encodable content and metadata. Persist the glyph data with the rest of the document when the app’s format supports it. If the app exports to a format that cannot carry the glyph, make the loss visible and choose a deliberate fallback such as an accessible textual description or a rasterized image.

Accessibility should not depend on the image alone. Use contentDescription as a candidate text equivalent, then verify how the chosen text view and VoiceOver experience expose it. Do not fabricate a description from the model or user prompt if the actual glyph metadata is available.

## Visual Intelligence

Visual Intelligence can pass information from a camera capture or screenshot into an App Intents query. The app receives a SemanticContentDescriptor containing general labels and, when available, a pixel buffer. The app searches its own content and returns AppEntity results to the system.

The core route is:

~~~text
Visual Intelligence capture
    -> IntentValueQuery.values(for: SemanticContentDescriptor)
    -> labels and/or pixelBuffer
    -> bounded app-owned search
    -> [AppEntity] or a UnionValue result
    -> DisplayRepresentation in the system panel
    -> OpenIntent for the selected entity
~~~

Important constraints from the official route:

- labels are general high-level terms and are currently described for the en_US locale;
- labels may change over time and do not necessarily contain the exact name of the object or place;
- the framework does not translate labels or provide synonyms;
- the query should return quickly and limit the first result set;
- the app cannot register more than one IntentValueQuery taking SemanticContentDescriptor;
- UnionValue can represent several entity types from the one query;
- a selected result needs an OpenIntent that can open the matching entity;
- a more-results intent can take the user into the app for the full search experience;
- the system uses the entity’s localized DisplayRepresentation to present results.

The query should be a search adapter, not a general-purpose model endpoint. Convert the pixel buffer through an appropriate image pipeline, apply a bounded search budget, and return only entities whose identity and display representation can be resolved quickly. If the local search needs a large server request, make latency and privacy explicit and give the system a fast empty or limited result path.

Visual Intelligence is not a license to expose an entire database. Define a small AppEntity projection with stable identity, a localized title, a useful subtitle, a safe thumbnail, and the minimum fields needed to open or explain the result.

## App Entities, onscreen context, and Spotlight

AppEntity is the system-facing projection of app data. It should be lightweight, stable, and quick to create. Do not make a heavyweight database record or an object with hidden network work the entity itself.

Use the right exposure:

| Need | Route |
| --- | --- |
| Parameter resolution for an intent | AppEntity and an EntityQuery |
| Search and system discoverability | IndexedEntity, indexed properties, and a named CSSearchableIndex |
| Entity visible in a SwiftUI view | appEntityIdentifier(_:) |
| Several custom-drawn or stateful onscreen items | appEntityUIElements(_:) with AppEntityUIElement values |
| Legacy or cross-surface activity association | NSUserActivity.appEntityIdentifier |
| Cross-app handoff of meaningful content | Transferable or an IntentValue representation |
| Open the entity in the app | OpenIntent |

AppEntityUIElement adds local bounds, selected state, and subelements for custom views or custom drawing. Use it when the system needs spatial or state context that a single view-level entity identifier cannot represent. For a standard List or a simple detail view, use the simpler SwiftUI modifier.

IndexedEntity and IndexedEntityQuery give the app’s entities a path into Spotlight. Use @Property, @ComputedProperty, and @DeferredProperty intentionally:

- direct properties are useful for fields that are cheap and stable;
- computed properties can expose derived values and indexing keys;
- deferred properties can avoid eager work but may not be indexed or sent to system experiences until fetched;
- expensive values should not turn indexing into an unpredictable network or model operation;
- use a named CSSearchableIndex for production indexing rather than relying on the default index;
- keep index updates and deletions tied to the app’s actual revision and authorization state;
- provide an OpenIntent for each entity type that can be opened from search.

For onscreen context, annotate only the content that the user is actively viewing or that the system experience needs. A user activity or entity association can make the content available to Siri and Apple Intelligence. If an entity supports Transferable, choose representations that are safe, bounded, and useful for the requested cross-app task. A PDF or rich-text representation can be useful; a private database dump is not.

## App-owned Foundation Models

Foundation Models is the app-owned on-device text-model route. Before creating a session, inspect SystemLanguageModel.default.availability. The official availability examples distinguish at least:

- available;
- unavailable because the device is not eligible;
- unavailable because the model is not ready, such as downloading;
- another unavailable reason that requires a general fallback.

Apple periodically updates the system language model with OS updates. A prompt that worked on one model version is not a timeless contract. Keep prompt and model versions in your evaluation record and avoid storing raw generated text as if it were deterministic domain state.

Use Foundation Models for bounded tasks such as summarization, extraction, classification, tagging, refinement, or creative text where a human can review the result. The official guidance calls out tasks the base model may not be suitable for, including basic arithmetic, arbitrary code generation, and some logical reasoning. Use deterministic code, a tool, guided generation, or a different system for tasks that need exactness.

The app should split a model feature into:

1. capability check;
2. input snapshot and privacy review;
3. prompt or instructions version;
4. model session and cancellation;
5. streamed or final output state;
6. validation and provenance;
7. user review;
8. domain commit;
9. fallback and telemetry that does not collect more data than necessary.

Do not let a model response directly mutate a purchase, medical record, contact, message recipient, or destructive document action. Return a typed proposal with source revision, requested operation, confidence or validation status, and a user-visible explanation.

## System-owned versus app-owned intelligence

The same word, such as summarize or search, can mean different routes:

| Product request | Prefer | Why |
| --- | --- | --- |
| Rewrite selected note text | Writing Tools | The system owns the interaction and result review |
| Generate a profile illustration | Image Playground | The system owns prompt experimentation and generation UI |
| Find the landmark visible in a screenshot | Visual Intelligence + IntentValueQuery | The system owns capture and result presentation; the app owns matching |
| Let Siri refer to the visible note | AppEntity association + Transferable when needed | The system needs explicit context and a safe content representation |
| Summarize a private set of app records | Foundation Models | The app owns input selection, availability, review, and commit |
| Perform an app action from a natural-language request | AppIntent with schema, parameters, supportedModes, and confirmation | The system resolves the request; the app validates and performs the action |

An app can use more than one lane, but the handoff needs a typed boundary. For example, Visual Intelligence may find a LandmarkEntity; OpenIntent opens it; a Foundation Models session may draft a description; the user approves; the app saves the description. The entity identity, draft text, and committed record are separate values.

## App Intents execution context

AppIntent supports runtime modes that determine whether an action runs in the foreground or background. The app can declare supportedModes and inspect systemContext.currentMode. The intent may be able to continue in the foreground, or it may need to remain in the background.

This matters for AI features:

- a voice-only action may return a concise dialog without opening a visual editor;
- an action requiring a user-visible review should request or require an appropriate foreground mode;
- a file write or long-running model task may need cancellation and a background-safe checkpoint;
- an OpenIntent must be implemented in the main app because it launches the app;
- app-intent code may live in an app extension or package and cannot assume the main scene is present;
- the same intent can have different behavior when triggered through Siri, Shortcuts, Spotlight, or a visible app surface.

Use supportedModes as an execution contract, not as a styling hint. The app should choose a fallback that fits the current mode instead of trying to force a foreground panel while the user is driving, wearing headphones, or using a system surface that cannot display it.

## Liquid Glass and native intelligence surfaces

Liquid Glass is an app-owned visual material and interaction system. It is not a replacement for system-owned Writing Tools, Image Playground, Siri, Visual Intelligence, or Spotlight surfaces. Use the system surface when Apple provides one, and reserve Liquid Glass for the surrounding app shell:

- toolbar controls that invoke a system sheet;
- a compact status row showing availability or current generation state;
- a review panel for a generated proposal;
- an entity detail view after OpenIntent;
- a source and provenance card;
- a fallback action when the system model is unavailable.

Keep functional content outside ornamental glass. Group related controls, keep text readable over changing backgrounds, allow the system to handle safe-area and appearance changes, and use native controls for buttons, menus, sheets, toolbars, and navigation. Avoid an app-wide translucent overlay that makes a model response look official or inevitable.

The visual state must follow the true state:

| State | Surface |
| --- | --- |
| capability unavailable | Ordinary fallback control with explanation |
| capability available | Native entry point |
| system surface presenting | Minimal app shell behind the system surface |
| generating or searching | Progress and cancellation, not a fake completed result |
| candidate ready | Review surface with source and edit affordance |
| committed | Domain record and undo path |
| failed or cancelled | Prior valid state plus recovery |

## Accessibility and privacy

AI and system-integration features create more than visual requirements:

- make the task usable without color, animation, or a generated image;
- expose the status of generation, search, or model availability to VoiceOver;
- let people cancel, reject, retry, or undo;
- support Dynamic Type and larger text in the app-owned shell;
- preserve text selection, focus, keyboard, and alternate input behavior;
- use meaningful labels for generated images and adaptive glyphs;
- do not use sparkles as the only indication of an AI action;
- do not announce a proposal as a fact;
- make the data sent to a system feature or model explicit where the feature requires user awareness;
- prefer on-device processing when it provides a good experience, but describe server or Private Cloud Compute involvement accurately;
- request only the personal information needed for personalization;
- keep generated content and raw source data separate in logs;
- delete temporary Image Playground files when they are not retained;
- treat screenshot pixel buffers and onscreen entities as sensitive input;
- provide a non-AI path when AI is complementary rather than critical.

The Generative AI HIG emphasizes user control, clear AI disclosure, privacy, feedback, correction, and fallbacks. The Apple Intelligence and Siri guidance also warns against advertising in Siri responses and recommends concise, audible responses that do not depend on an unseen visual panel.

## Failure matrix

| Failure | Likely cause | Safe response |
| --- | --- | --- |
| Writing Tools affordance missing | Unsupported device, disabled behavior, or system readiness | Keep the editor functional and use the non-AI editing path |
| Custom Writing Tools result corrupts text | Range mapped against a stale document revision | Abort or reconcile against the current revision; never blindly replace |
| Image Playground sheet cannot present | supportsImagePlayground is false or current target lacks support | Hide or disable the entry point and offer import/manual creation |
| Image completion URL disappears | App retained a temporary URL as if it were permanent | Copy into an app-owned location immediately |
| Adaptive glyph vanishes after save | Attribute filter or file format discarded it | Preserve the adaptiveImageGlyph attribute or show a deliberate fallback |
| Visual Intelligence returns no result | Labels are general, pixelBuffer unavailable, or search budget too slow | Return an empty/limited result quickly and offer in-app search |
| Visual Intelligence result opens the wrong record | Entity ID or OpenIntent resolution is stale | Resolve by stable identity and surface a not-found state |
| Siri references the wrong onscreen item | Missing or broad entity association | Annotate the visible item with stable IDs and current state |
| Foundation Model unavailable | Device, region, Apple Intelligence setting, or model readiness | Show availability-specific fallback and keep domain workflow usable |
| Model output is plausible but wrong | Open-ended generation without validation | Label as a proposal, validate against source data, and require review |
| AI surface is inaccessible | Status only shown through animation or iconography | Add spoken status, text alternatives, focus order, and cancel/retry actions |

## Evidence ladder

Documentation and source links establish what an API is for. They do not prove the app works.

| Claim | Minimum evidence |
| --- | --- |
| SwiftUI code uses the intended route | SDK compile in the named target and deployment configuration |
| Writing Tools works in the editor | Supported physical device or system environment, text selection, rewrite/undo/rejection behavior, and custom-editor range proof where applicable |
| Image Playground works | Supported physical device with availability true, sheet presentation, completion/cancellation, temporary-file persistence, and resource cleanup |
| Genmoji survives persistence | Rich-text fixture containing adaptive glyph data, save/reopen, export fallback, accessibility review |
| Visual Intelligence integration works | Supported system invocation, query execution, bounded results, DisplayRepresentation, OpenIntent, and more-results handoff |
| Onscreen context is correct | Visible entity annotations, Siri or system invocation, stable entity resolution, and privacy review |
| Foundation Models feature works | Supported device/model-ready path, unavailable fallback, cancellation, output validation, and evaluated fixtures |
| Native design is ready | Accessibility Inspector, Dynamic Type, reduced motion, contrast/appearance, keyboard/VoiceOver, and system-surface review |
| Release is ready | Archive inspection, signed entitlements and target membership, TestFlight install, privacy/App Store metadata, and the intended physical/system tests |

## Implementation checklist

- name the user outcome and choose system-owned versus app-owned intelligence;
- select a target, deployment range, and supported device matrix;
- use standard SwiftUI text views before designing a custom text engine;
- configure Writing Tools only where the content contract supports it;
- preserve AttributedString attributes and adaptive glyph data;
- gate Image Playground with supportsImagePlayground and persist returned files;
- bound Visual Intelligence queries and provide stable AppEntity and OpenIntent routes;
- expose only relevant onscreen entities and safe Transferable representations;
- use named Spotlight indexing and stable IDs;
- inspect SystemLanguageModel availability before creating a model session;
- use typed proposals, revision checks, validation, review, and undo;
- set AppIntent supportedModes and make foreground/background behavior deliberate;
- put Liquid Glass around the app’s functional review surface, not around system-owned panels;
- provide fallback, accessibility, privacy, cancellation, and release evidence;
- record which claims are compile, simulator, physical-device, system, archive, TestFlight, or release evidence.

## Sources

- [Apple Intelligence](https://developer.apple.com/documentation/technologyoverviews/apple-intelligence/)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [App entities](https://developer.apple.com/documentation/appintents/app-entities)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [IndexedEntity](https://developer.apple.com/documentation/appintents/indexedentity)
- [Defining app entities for your custom data types](https://developer.apple.com/documentation/appintents/defining-app-entities-for-your-custom-data-types)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [Providing contextual cues to Apple Intelligence and Siri](https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri)
- [appEntityIdentifier(_:)](https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28_%3A%29)
- [AppEntityUIElement](https://developer.apple.com/documentation/appintents/appentityuielement)
- [appEntityIdentifier](https://developer.apple.com/documentation/foundation/nsuseractivity/appentityidentifier)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [Visual intelligence app schema](https://developer.apple.com/documentation/appintents/app-schema-domain-visual-intelligence)
- [Writing Tools](https://developer.apple.com/documentation/uikit/writing-tools)
- [Customizing Writing Tools behavior for UIKit views](https://developer.apple.com/documentation/uikit/customizing-writing-tools-behavior-for-system-views)
- [Adding Writing Tools support to a custom UIKit view](https://developer.apple.com/documentation/uikit/adding-writing-tools-support-to-a-custom-uiview)
- [WritingToolsBehavior](https://developer.apple.com/documentation/swiftui/writingtoolsbehavior)
- [writingToolsBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsbehavior%28_%3A%29)
- [writingToolsAffordanceVisibility(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsaffordancevisibility%28_%3A%29)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [Building rich SwiftUI text experiences](https://developer.apple.com/documentation/swiftui/building-rich-swiftui-text-experiences)
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
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [App Intents updates](https://developer.apple.com/documentation/updates/appintents)
