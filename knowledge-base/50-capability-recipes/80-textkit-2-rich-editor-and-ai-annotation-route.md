# TextKit 2 rich-editor and on-device AI annotation route

Use this route for a private document, note, transcript, study surface, or
reviewable writing tool that needs native editing plus optional on-device
intelligence. The editor remains useful without a model. The model proposes;
the person reviews; the domain model commits.

## Route contract

~~~text
user-approved source
  -> document revision and stable source spans
  -> SwiftUI Text/TextEditor or UIKit UITextView
  -> TextKit 2 content + layout + viewport
  -> optional AI proposal
  -> source-span decoration and review actions
  -> user accept/reject/edit
  -> deterministic validation
  -> new document revision
  -> save/export/system handoff
~~~

Use Core Text instead of TextKit 2 only when the outcome is primarily custom
drawing, glyph measurement, PDF/image export, or text in arbitrary paths. Use
SwiftUI TextRenderer when the outcome is a bounded read-only run effect, not a
full editor.

## Step 1: define the document authority

Start with a document model that has explicit revision identity:

| Field | Purpose |
| --- | --- |
| Document ID | Stable identity for persistence and navigation |
| Revision ID | Invalidates stale layout or AI work |
| Content | Plain or attributed user-owned text |
| Selection | Short-lived editing state, not persistence truth |
| Source spans | Stable ranges/IDs for review and provenance |
| Attachments | Explicit content references and lifecycle |
| Review proposals | Generated records tied to revision and model route |
| Save state | Local write, conflict, export, or failure state |

For private/local-first products, keep the original text on device unless the
person explicitly chooses a different route. A model proposal is not a reason
to upload the entire document. Redact or minimize context when the feature
allows it, and state what remains local.

Store a source span with a stable identifier, a source revision, the original
text hash or anchor, and a user-visible range description. A raw UTF-16 offset
may be useful for a short-lived render query, but it is not a durable identity
after edits or localization.

## Step 2: select the editing surface

| Need | Route | Proof to plan |
| --- | --- | --- |
| Simple long-form text | SwiftUI TextEditor | Selection, keyboard, Dynamic Type, accessibility |
| Read-only rich output | SwiftUI Text + AttributedString | Attribute support, text selection, links, localization |
| UIKit editor behavior | UITextView using TextKit 2 | Target compile, selection, Writing Tools, focus, undo |
| Custom document renderer | NSTextContentStorage + NSTextLayoutManager | Fragment/viewport rendering, invalidation, hit testing |
| Exact export geometry | Core Text | Font substitution, layout path, drawing, export fidelity |

Keep the route behind a feature-owned adapter. The rest of the app should not
know whether the current target uses TextEditor, UITextView, or a custom
fragment renderer.

## Step 3: build the TextKit 2 graph

For a custom UIKit route:

1. Create an NSTextContentStorage for the attributed backing store.
2. Create an NSTextLayoutManager and add it to the content manager.
3. Assign an NSTextContainer with the destination geometry.
4. Put edits inside performEditingTransaction.
5. Use NSTextLayoutManager for usage bounds, fragments, segments, selections,
   rendering attributes, and invalidation.
6. Use NSTextViewportLayoutController when only a visible region should be
   laid out or when attachment view reuse matters.
7. Let UITextView own keyboard, scrolling, first responder, selection, and
   system text-input behavior when those are part of the product.

The content manager is the synchronization boundary. The layout manager is the
geometry boundary. The view is the interaction boundary. Do not put business
state in a layout fragment or a view's current frame.

## Step 4: model the proposal lifecycle

Use a state machine with cancellation:

~~~text
idle
  -> preparing(source revision)
  -> generating(model route/version)
  -> validating(proposal)
  -> ready for review
  -> accepted -> committing -> saved
  -> rejected -> idle
  -> edited -> generating again
  -> source changed -> stale
  -> unavailable/error -> deterministic fallback
~~~

Each model task captures the revision and a cancellation token. Before showing
or committing the result, verify:

- the document still has the same revision;
- the source span still matches its anchor/hash;
- the proposal schema is valid;
- ranges are within the current document;
- replacement text passes product validation;
- the person has not dismissed or superseded the proposal;
- the current accessibility and privacy policy permits the presentation.

If any check fails, mark the proposal stale and keep the user's current text.
Do not silently merge a stale replacement into a newer document.

## Step 5: present annotations without hiding the source

Use a calm review shell:

~~~text
document text
  -> subtle source-span mark
  -> small review affordance
  -> glass action group with semantic buttons
  -> sheet/inspector for rationale and replacement
~~~

The annotation should not depend on color alone. Pair it with a label, icon,
underline, or a review list. Accept, Reject, Edit, and Dismiss must be
reachable through touch, keyboard, VoiceOver, and the current text selection.

Use Liquid Glass for the action group or inspector, not as a blur over the
content. When reduced transparency is enabled, use a solid or high-contrast
fallback. When Reduce Motion is enabled, reveal a proposal directly rather
than requiring a moving highlight to explain the state.

The model's rationale is a generated explanation. Label it as such and keep
the original text visible. Never present confidence or fluency as evidence of
truth.

## Step 6: commit and persist

Accepting a proposal is a user action that should create a deterministic
document mutation:

1. re-check revision and source anchor;
2. apply the replacement to the canonical document;
3. create a new revision;
4. record the accepted proposal ID and model route if product policy requires;
5. remove or recompute obsolete annotations;
6. save locally or enter a visible conflict/error state;
7. update the layout and selection;
8. return focus without stealing it from another active interaction.

If the document is synchronized, keep conflict resolution separate from the
AI proposal. A model may suggest a merge, but the app must show the competing
revisions and commit only after a deterministic validation and user decision.

## Step 7: use the system text intelligence boundary

Writing Tools and other system text features have their own view configuration,
context, range, and lifecycle. Treat a system-generated change as a proposal
from an external system surface. Track the range relative to the supplied
context, then translate it back to the document's authority before applying it.

Do not assume that a local Foundation Models result, a Writing Tools result,
and a Core ML/Natural Language annotation have the same privacy, availability,
latency, or output contract. Keep each route's model/system state explicit.

## Availability and permissions

Plain local text editing does not need a model or protected-data permission.
Additional capabilities may introduce their own requirements:

| Capability | Boundary |
| --- | --- |
| Files/document providers | User-selected URL, security scope, bookmark, and file coordination |
| Photos/camera/audio | User authorization and source retention policy |
| Foundation Models | Availability, model readiness, prompt/context, cancellation, and fallback |
| Writing Tools | UIKit view configuration and system-controlled operation lifecycle |
| Cloud sync | Account state, container configuration, conflicts, and privacy |
| Export/share | User-mediated destination and representation policy |

Ask for the smallest permission that matches the actual source. Do not ask for
camera, microphone, contacts, or network access merely because a future AI idea
could use it.

## Accessibility and alternate input

The feature is not complete if the person can see a colored annotation but
cannot discover or act on it with VoiceOver. Verify:

- the document remains readable and selectable;
- headings, links, and review state have meaningful labels;
- a proposal's source and action are spoken clearly;
- Accept and Reject are keyboard and Switch Control actions;
- Dynamic Type does not clip the review shell;
- selection and focus remain stable after a proposal arrives;
- reduced transparency, reduced motion, dim flashing lights, and increased
  contrast have understandable fallbacks;
- right-to-left and bidirectional text preserve source-span meaning.

## Evidence boundary

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| Preview | Static typography and deterministic review states | Selection, keyboard, VoiceOver, model readiness, or device performance |
| Compile | Symbol names, target imports, and availability diagnostics | Correct ownership, document persistence, or model quality |
| Unit/state test | Revision invalidation, range validation, and bounded proposals | Text rendering or user comprehension |
| UI test | Editing, review actions, focus, and navigation in a controlled build | Real Dynamic Type ergonomics, thermal behavior, or model availability |
| Simulator | Layout variants and scripted interaction | Physical keyboard/Pencil/device text rendering or Apple Intelligence readiness |
| Signed device | Real editor interaction, accessibility settings, performance, and system behavior on that device | Every supported device and future SDK |
| Release/TestFlight | Target membership, entitlements, resources, and artifact identity | Universal AI quality or user acceptance |

## Reusable acceptance checklist

- The canonical document is separate from the editor and renderer.
- Every proposal records source revision, source span, model/system route, and
  validation state.
- Stale or cancelled work cannot mutate newer text.
- The editor remains valuable when AI is unavailable.
- Glass groups semantic actions and has a readable fallback.
- Dynamic Type, localization, RTL, VoiceOver, keyboard, and selection are
  tested.
- Persistence, conflicts, export, and system text services have separate
  evidence.

## Related routes

- [TextKit 2 and Core Text layout](../42-framework-deep-dives/57-textkit-2-and-core-text-layout.md)
- [Native typography and rich-editor design](../21-design-deep-dives/77-native-typography-and-rich-editor-design.md)
- [TextKit 2 typography proof matrix](../60-verification/74-textkit-2-typography-proof-matrix.md)
- [TextKit 2 and Core Text recipes](../70-code-recipes/92-textkit-2-and-core-text-recipes.md)
- [Reviewable rich text and on-device AI output](18-reviewable-rich-text-and-ai-output.md)
- [Focused AI editor and command surface](20-focused-ai-editor-and-command-surface.md)
- [Writing Tools, Image Playground, and model surfaces](../32-apple-intelligence-surfaces/01-writing-tools-image-generation-and-model-surfaces.md)

## Sources

- [NSTextContentManager](https://developer.apple.com/documentation/uikit/nstextcontentmanager)
- [NSTextContentStorage](https://developer.apple.com/documentation/uikit/nstextcontentstorage)
- [NSTextLayoutManager](https://developer.apple.com/documentation/uikit/nstextlayoutmanager)
- [NSTextViewportLayoutController](https://developer.apple.com/documentation/uikit/nstextviewportlayoutcontroller)
- [NSTextLayoutFragment](https://developer.apple.com/documentation/uikit/nstextlayoutfragment)
- [NSTextLineFragment](https://developer.apple.com/documentation/uikit/nstextlinefragment)
- [NSTextSelection](https://developer.apple.com/documentation/uikit/nstextselection)
- [NSTextLocation](https://developer.apple.com/documentation/uikit/nstextlocation)
- [UITextView](https://developer.apple.com/documentation/uikit/uitextview)
- [Using TextKit 2 to interact with text](https://developer.apple.com/documentation/uikit/using-textkit-2-to-interact-with-text)
- [SwiftUI text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Generating content with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [Writing Tools coordinator context](https://developer.apple.com/documentation/uikit/uiwritingtoolscoordinator/context)
- [Adding Writing Tools support to a custom UIKit view](https://developer.apple.com/documentation/uikit/adding-writing-tools-support-to-a-custom-uiview)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
