# SwiftUI Apple Intelligence system-surfaces review proof matrix

This matrix defines what evidence can establish for Writing Tools, Image Playground, Genmoji/adaptive glyphs, Visual Intelligence, App Intents context, Spotlight, and Foundation Models. Use it with the [framework review](../42-framework-deep-dives/110-swiftui-apple-intelligence-system-surfaces-review.md), [route card](../50-capability-recipes/141-swiftui-apple-intelligence-system-surfaces-review-route.md), [design guide](../21-design-deep-dives/138-swiftui-apple-intelligence-system-surfaces-review-design.md), and [recipes](../70-code-recipes/153-swiftui-apple-intelligence-system-surfaces-review-recipes.md).

## Evidence levels

| Level | Establishes | Does not establish |
| --- | --- | --- |
| Source | Apple’s intended API, system boundary, or design guidance | The app’s target compiles or behaves |
| Static | Correct route names, state model, privacy/configuration checklist | SDK availability or runtime behavior |
| Compile | The selected target resolves the APIs under its SDK/deployment settings | Device, region, model readiness, system invocation, or data quality |
| Unit | Deterministic parsing, revision checks, entity identity, validation, and fallback logic | System presentation or physical AI behavior |
| Simulator | Layout, navigation, fixture behavior, and some target wiring | Apple Intelligence availability, real model quality, device performance, or system-surface delivery |
| Physical device | Hardware, settings, model readiness, text input, image generation, audio/visual interaction, and accessibility | App Store distribution or every region |
| System surface | Siri, Spotlight, Visual Intelligence, Writing Tools, Image Playground, or App Intent execution in its host | Broad model quality, privacy approval, or release readiness |
| Archive/TestFlight | Signed target, entitlements, resources, and installed distribution artifact | All physical/system behavior unless exercised from that artifact |
| Release | Intended signed build, metadata, privacy declaration, test evidence, and delivery path | Future OS/model behavior |

Never use a higher-level word such as “AI works” without naming the evidence level and the exact route.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Strong evidence | Common false positive |
| --- | --- | --- | --- |
| Text editor supports Writing Tools | Compile with current SwiftUI/UIKit SDK | Physical supported device, selected text, limited/complete behavior, accept/reject, undo, external-edit handling | Modifier compiles |
| Custom text view supports Writing Tools | Coordinator and delegate compile | Physical custom editor with selection, context scope, replacement, preview, stale revision, cancellation, and layout update | Coordinator object exists |
| Image Playground is available | Environment gate is present | Physical supported device with supportsImagePlayground true and sheet presentation | Button is visible in Simulator |
| Generated image is retained | Completion callback receives URL | Copy to app storage, reopen, preview, metadata, cancellation cleanup, and storage error path | URL is stored in a model |
| Genmoji survives a rich-text round trip | Attribute type exists in the document fixture | Input, edit, copy, save, reopen, accessibility, export fallback, and archive migration | Image looks correct before save |
| Visual Intelligence returns app content | Query and entity types compile | Supported camera/screenshot invocation, bounded query, display result, OpenIntent, stale identity, and more-results handoff | A local image search returns a match |
| Onscreen entity context is correct | Identifier modifier or activity code exists | Siri or system invocation refers to the visible item, then opens current record | The entity ID is printed in a debug log |
| Spotlight indexing works | IndexedEntity and index code compile | Named index contains add/update/delete, reindex, stable IDs, and OpenIntent from a physical system search | CSSearchableIndex call returns |
| Foundation Model feature works | Availability switch and session code compile | Available, device-ineligible, model-not-ready, cancelled, malformed-output, and validated user-review fixtures on a supported device | A generated summary is displayed |
| App Intent action is safe | Parameters and perform() compile | Current-mode behavior, authorization, confirmation, cancellation, undo, and domain revision checks | Siri invokes a method once |
| Liquid Glass design is native | SwiftUI view renders | Appearance, Dynamic Type, Reduce Motion, VoiceOver, keyboard, background legibility, and system-surface coexistence | Screenshot with translucent cards |

## Writing Tools matrix

| Test case | Setup | Expected evidence | Failure response |
| --- | --- | --- | --- |
| Plain TextEditor | Standard SwiftUI text editor | Writing Tools affordance and edit result | Keep manual editor path |
| Attributed TextEditor | Rich text with selection and formatting | Formatting and selection survive accepted replacement | Reject or reconcile result |
| Limited behavior | writingToolsBehavior(.limited) | Changes remain in system panel until approval | Do not apply temporary result |
| Complete behavior | writingToolsBehavior(.complete) | Inline replacement, animation, accept/reject, undo | Fall back to limited |
| Disabled content | Code or protected content | No Writing Tools mutation | No replacement |
| External save during operation | Autosave or sync writes a new revision | System operation is paused, reconciled, or cancelled safely | Invalidate stale context |
| Custom view selection | UIWritingToolsCoordinator custom context | Selection and range map to current text storage | Abort replacement if range is stale |
| Custom layout change | Resize or font change during operation | Reflow update reaches coordinator | Re-request preview or cancel |
| Unavailable model | Device not eligible or model not ready | Editor remains usable and communicates fallback | Do not block editing |

## Image Playground matrix

| Test case | Setup | Expected evidence | Failure response |
| --- | --- | --- | --- |
| Unsupported device | supportsImagePlayground false | Entry point hidden or replaced | Import/manual route |
| Basic sheet | Concepts and no source image | System sheet presents and completion returns URL | Keep prior state |
| Source image | User-selected image | System allows editing without overwriting source | Keep source until approval |
| Personalization disabled | Options personalization disabled | Result uses only supplied inputs | Explain behavior if relevant |
| Restricted styles | Allowed style list | System honors the current supported style set | Remove unsupported choice |
| Cancellation | User exits without choosing | Cancellation callback and no document mutation | Restore prior state |
| Temporary URL | Completion path | Copy to app-owned location and reopen | Treat as failure; do not retain URL |
| Storage failure | Copy or validation fails | User sees recovery and no half-saved asset | Preserve prior asset |
| Generated output review | Candidate image | Edit, retry, dismiss, save, accessibility label | Do not mark saved early |

## Genmoji and rich-text matrix

| Test | Expected result |
| --- | --- |
| Insert adaptive image glyph | Glyph renders inline with surrounding text |
| Copy attributed substring | Glyph attribute and content data remain available |
| Change font or color | Glyph metadata is preserved |
| Save and reopen | AttributedString or custom format recreates the glyph |
| Export unsupported format | App gives a textual or raster fallback and discloses loss |
| Accessibility inspection | Content description or equivalent is exposed meaningfully |
| Delete glyph | Cursor, selection, undo, and document revision remain correct |
| Unknown attribute filtering | adaptiveImageGlyph is not silently discarded |

## Visual Intelligence matrix

| Test case | Setup | Expected result | Evidence boundary |
| --- | --- | --- | --- |
| Labels only | Descriptor has labels and no pixel buffer | Bounded semantic search returns useful entities or empty result | Labels are general, not canonical identity |
| Pixel buffer | Supported descriptor with image input | Bounded image search returns current entities | Pixel buffer is sensitive input, not user approval |
| Empty query | No match | Fast empty result and in-app alternative | No claim of no object in the real world |
| Many matches | Hundreds of matches | Limited panel result and more-results intent | Search is not allowed to stall |
| Mixed entity types | UnionValue result | Each result type has an OpenIntent | One query must own the descriptor |
| Selected result | Tap result in system panel | OpenIntent navigates to stable current record | Not just a generic app launch |
| Stale result | Record deleted or revised | Not-found or updated detail, not wrong record | ID and revision are checked |
| Localization | Non-en_US locale | Localized display values; no claim that labels translate | Apple docs describe labels as general and locale-dependent |
| Privacy | Screenshot or camera input | Input bounded, retained only as needed | Do not log raw buffer |

## Onscreen context and Spotlight matrix

| Test | Expected result | Evidence |
| --- | --- | --- |
| Standard detail view | appEntityIdentifier matches visible record | System context refers to correct item |
| List selection | Selection-specific IDs remain current | “This item” maps to selected item |
| Custom canvas | AppEntityUIElements include bounds and state | System receives correct spatial elements |
| Offscreen item | Association stops or is updated as designed | No stale visible claim |
| Unauthorized item | Association and index entry removed | Privacy state is respected |
| Entity update | Stable ID resolves newest revision | No duplicate or stale navigation |
| Transferable content | Selected representation is bounded | Cross-app route receives safe data only |
| Spotlight index | Named index add/update/delete | Search result opens via OpenIntent |
| Deferred property | Expensive value loads only when needed | Indexing remains bounded and predictable |
| Reindex request | IndexedEntityQuery rebuilds correct entities | Reindex does not corrupt or duplicate |

## Foundation Models matrix

| State or fixture | Expected behavior | Required evidence |
| --- | --- | --- |
| available | Feature can present a model action | Supported hardware and model-ready device |
| deviceNotEligible | Show deterministic fallback | Device ineligible path |
| modelNotReady | Explain waiting or offer fallback | Model downloading/not-ready path |
| unknown unavailable | Keep core workflow usable | Generic fallback |
| empty input | Reject or handle explicitly | Input validation |
| long input | Bound or summarize input before session | Context budget behavior |
| cancellation | Stop generation and clear transient state | User or system cancellation |
| malformed output | Do not commit | Parser and validation fixture |
| stale source revision | Recompute or reject | Revision mismatch test |
| plausible but false output | Show proposal and source | Human review and deterministic validation |
| exact task | Use deterministic code, tools, or guided generation | Avoid base-model overclaim |
| model update | Prompt/model version recorded | Regression fixture across versions |

## App Intent execution matrix

| Mode | Test | Expected result |
| --- | --- | --- |
| background | Intent performs safe non-UI work | No assumption that a SwiftUI scene exists |
| foreground immediate | Intent needs visible UI before perform | App foregrounds before action |
| foreground dynamic | Intent may continue to UI | currentMode and canContinueInForeground are honored |
| foreground deferred | Background work completes before UI | Action checkpoints and transitions correctly |
| cancellation | Long-running model or indexing task | CancellableIntent cleanup leaves no partial commit |
| undo | User-visible mutation | UndoableIntent restores prior state |
| ambiguity | Multiple entity matches | requestChoice or system dialog, not guessing |
| OpenIntent | Entity selected from system | Main app opens current entity |

## Accessibility and privacy matrix

| Check | Pass condition |
| --- | --- |
| VoiceOver | Availability, progress, result, source, error, and actions are announced |
| Dynamic Type | Review content remains usable at large sizes |
| Reduce Motion | No critical meaning depends on replacement animation |
| Keyboard | Focus, selection, accept, reject, retry, and undo work |
| Voice Control | Labels are discoverable and actions have stable names |
| Contrast | Text and controls remain legible over Liquid Glass and generated imagery |
| Input minimization | Only the selected or needed data enters the route |
| Temporary-file hygiene | Image Playground temporary assets are copied or removed intentionally |
| Model disclosure | The app accurately says when AI is used and what it can do |
| Retention | Raw prompts, screenshots, and outputs are not logged by default |
| Fallback | Core task remains possible when AI is unavailable or declined |

## Physical-device and system proof record

~~~yaml
claim: Visual Intelligence returns a current landmark entity
target: Main iOS app plus App Intents implementation
sdk: named Xcode and iOS SDK
device: supported iPhone model and OS build
settings: Apple Intelligence enabled; region and language recorded
system_invocation: screenshot or Camera Control visual search
input: label and pixel-buffer cases
result: bounded entities with localized display representation
open: OpenIntent navigates to current entity
fallback: empty results and more-results route
accessibility: VoiceOver, Dynamic Type, Reduce Motion
privacy: no raw pixel-buffer logging; entity visibility checked
artifact: archive and TestFlight installation
status: pending until observed
~~~

Do not change status to pass because the query returns a local fixture. The fixture is useful unit evidence, not system evidence.

## Release matrix

| Release item | Check |
| --- | --- |
| Target | App, extension, package, and deployment target are correct |
| SDK | All Writing Tools, Image Playground, Visual Intelligence, and Foundation Models symbols match the selected SDK |
| Entitlements and capabilities | Only required system integrations are enabled |
| Privacy | App Store privacy details, usage descriptions, and data-flow claims match implementation |
| Resources | Model prompts, image assets, rich-text fixtures, and fallback resources are present |
| Archive | Release build links correct frameworks and contains intended targets |
| TestFlight | Installed artifact exercises the system route on supported hardware |
| App Store | Generated content, AI disclosure, system-surface use, and accessibility are represented honestly |
| Regression | Availability, cancellation, stale data, accessibility, and fallback fixtures pass |

## Acceptance checklist

- one system owner is named for every intelligence feature;
- system and app-owned routes are not visually or semantically conflated;
- availability and fallback state are testable;
- input, proposal, review, and commit are separate;
- stable entity identity and current revision are proven;
- temporary image and adaptive glyph persistence are proven;
- Visual Intelligence query, OpenIntent, and more-results routes are proven;
- model limitations and prompt versions are recorded;
- accessibility and privacy evidence exists;
- the signed artifact has been installed and the intended system surface exercised.

## Sources

- [Apple Intelligence](https://developer.apple.com/documentation/technologyoverviews/apple-intelligence/)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [Writing Tools](https://developer.apple.com/documentation/uikit/writing-tools)
- [Adding Writing Tools support to a custom UIKit view](https://developer.apple.com/documentation/uikit/adding-writing-tools-support-to-a-custom-uiview)
- [WritingToolsBehavior](https://developer.apple.com/documentation/swiftui/writingtoolsbehavior)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [NSAdaptiveImageGlyph](https://developer.apple.com/documentation/uikit/nsadaptiveimageglyph)
- [AttributedString.AdaptiveImageGlyph](https://developer.apple.com/documentation/foundation/attributedstring/adaptiveimageglyph)
- [Image Playground](https://developer.apple.com/documentation/imageplayground)
- [ImagePlaygroundOptions](https://developer.apple.com/documentation/imageplayground/imageplaygroundoptions)
- [ImagePlaygroundStyle](https://developer.apple.com/documentation/imageplayground/imageplaygroundstyle)
- [imagePlaygroundSheet(isPresented:concepts:sourceImageURL:onCompletion:onCancellation:)](https://developer.apple.com/documentation/swiftui/view/imageplaygroundsheet%28ispresented%3Aconcepts%3Asourceimageurl%3Aoncompletion%3Aoncancellation%3A%29)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [Visual intelligence app schema](https://developer.apple.com/documentation/appintents/app-schema-domain-visual-intelligence)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [IndexedEntity](https://developer.apple.com/documentation/appintents/indexedentity)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [Providing contextual cues to Apple Intelligence and Siri](https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri)
- [AppEntityUIElement](https://developer.apple.com/documentation/appintents/appentityuielement)
- [appEntityIdentifier(_:)](https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28_%3A%29)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [supportedModes](https://developer.apple.com/documentation/appintents/appintent/supportedmodes)
- [IntentModes.Current](https://developer.apple.com/documentation/appintents/intentmodes/current)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Siri HIG](https://developer.apple.com/design/human-interface-guidelines/siri)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
