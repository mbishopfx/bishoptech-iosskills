# SwiftUI text-editing and rich-content design

## Design premise

A writing surface should make four things obvious:

1. what content the person is editing;
2. where the insertion point or selection is;
3. what formatting and system tools are available;
4. what will be persisted or changed.

Use this task flow:

~~~text
document title and save state
    -> readable editor canvas
    -> selection/focus
    -> formatting/find/Writing Tools
    -> optional AI review
    -> explicit apply/discard
    -> validated document commit
~~~

The visual target is an original Apple-native writing surface: system typography,
clear focus, adaptable controls, and restrained Liquid Glass grouping. It is not
a replica of Notes, Pages, Mail, or another proprietary Apple screen.

## Choose the editor shape before the shell

| Task | Native starting shape | Design boundary |
| --- | --- | --- |
| Short single-line value | TextField | Validation and keyboard/input type |
| Plain long-form draft | TextEditor with String | Global text style; no inline formatting claim |
| Styled long-form document | Attributed TextEditor with attributed selection | Formatting definition, selection, serialization |
| Read-only article/review | Text with AttributedString | Selection/readability and link policy |
| Source Markdown editing | Plain source editor plus preview | Source/preview divergence and round-trip policy |
| Rich layout/attachments | SwiftUI shell with UIKit/TextKit 2 editor | Selection, viewport, attachment, and lifecycle ownership |

Do not present a formatting toolbar for a plain String editor unless the action
changes a defined document representation. Do not place a rich-document promise
on a reader that only renders a projection.

## The screen hierarchy

A calm document editor typically follows:

~~~text
navigation title
  -> title/metadata and save state
  -> editor canvas with readable measure
  -> selection and inline context
  -> formatting/find/review group
  -> optional inspector or sheet
~~~

Keep the text primary. Use system title styles, body styles, and Dynamic Type.
Let the editor grow with the available space and keyboard. Use margins,
background, and spacing to create an intentional page without turning the page
into a card collection.

The title and status should answer:

- which document is open;
- whether it is new, dirty, saving, saved, offline, or conflicted;
- whether the current surface is source Markdown, a rich projection, or a
  read-only review;
- whether a Writing Tools or AI operation is active;
- which action returns the person to safety.

## Plain versus attributed state

A plain editor can be visually polished without pretending to support inline
formatting. A rich editor should show the difference between:

| State | What the person sees |
| --- | --- |
| insertion point | Cursor and active editor focus |
| selection | Native selection affordance and selection-scoped actions |
| mixed formatting | A neutral or mixed control state |
| formatting available | System or custom control that can act on selection |
| dirty | Document status, not a glass color alone |
| Writing Tools active | System-owned editing state or honest progress state |
| AI candidate | Source and proposed change shown together |
| stale candidate | Apply blocked or explicit rebase/review |
| saved/committed | Status at the actual persistence boundary |

Do not make a selection highlight carry review meaning. A selected paragraph
and an AI-suggested paragraph may overlap, but they are different state.

## Selection-first actions

A selection-aware action should be discoverable near the selection or in a
semantic toolbar, while remaining available to keyboard and accessibility input.

Use a compact action group:

~~~text
selection
  -> Format
  -> Find/Replace
  -> Writing Tools
  -> Review selection
  -> Copy/share
~~~

Only enable actions that match the current content and source revision. If the
selection is empty, show insertion-point actions or a clear disabled state.
When the text changes, invalidate the selected source span before running an
async action.

For bidirectional text, selection affinity and visual direction can affect how
the insertion point behaves. Test mixed English/Arabic or Hebrew content rather
than assuming a left-to-right visual frame is the logical range.

## Formatting controls

Use system text formatting controls when the document's format can preserve the
result. If a custom toolbar is needed, keep it small:

- bold/italic/underline or the supported subset;
- paragraph/list controls only when the format supports them;
- link action with explicit URL policy;
- text style or color only when it has a semantic purpose;
- undo/redo and selection actions through native commands where available.

Apply an attributed formatting definition to constrain the user-visible
formatting surface. Keep serialization validation separate because off-screen
attributed content may not have been normalized by the view.

If the system formatting controls duplicate a custom toolbar, hide only the
duplicate controls and preserve a discoverable, accessible alternative. Do not
remove native formatting affordances merely to make the screenshot cleaner.

## Find and replace

Find is an editor task, not a global search screen. Use the native find navigator
for one focused editor. Keep the current document visible and preserve undo.

If the screen contains multiple editors, make the active editor explicit or
provide a custom FindContext-backed route. A button that opens a system find
surface without a deterministic editor owner creates surprising behavior.

Find/replace should preserve:

- current document ID and source revision;
- selection/focus after close;
- undo grouping;
- Dynamic Type and keyboard behavior;
- localized labels and VoiceOver announcements;
- an honest “no matches” state;
- a way to cancel without mutating the document.

## Writing Tools design

Writing Tools belongs to the system text interaction model. Use its SwiftUI
behavior values to express product intent:

- automatic when the system should choose the appropriate experience;
- limited when a contained review panel is preferable;
- complete when inline editing is appropriate and available;
- disabled for code, immutable quotations, identifiers, or protected text.

The editor must remain useful if Writing Tools is unavailable. Do not show a
persistent sparkle control that implies app-owned generation. If the system
provides the affordance, let the system label and placement do the work.

During Writing Tools activity:

- pause app-specific text rewrites and cloud sync transformations;
- avoid stealing focus or replacing the current selection;
- keep unsaved state and temporary edits understandable;
- reconcile the final result through the document revision pipeline;
- test accept, reject, cancel, interruption, and unavailable behavior.

For custom UIKit text views, use the UIKit Writing Tools contract and ignored
ranges rather than placing a fake SwiftUI control over a view that does not
support the system feature.

## AI review design

An app-owned Foundation Models writing feature needs a different visual
contract:

~~~text
selected source
  -> instruction and scope
  -> reviewing/partial
  -> proposed replacement
  -> compare/edit
  -> apply or discard
  -> saved document revision
~~~

Show:

- the selected source and proposed output;
- the source revision;
- an explicit generated/provisional state;
- the actions Apply, Edit, Discard, and Cancel where applicable;
- a stale or unavailable explanation;
- a recovery path to the original text.

Keep rationale concise and optional. Never hide generated changes inside an
attributed highlight or a glass badge. The document remains the source of truth
until the person explicitly applies the proposal.

## Liquid Glass composition

Glass is useful around a functional formatting/review group:

~~~text
opaque/readable document canvas
    -> selection and text content
        -> compact glass action cluster
            -> status and explicit commit
~~~

Good glass boundaries:

- a formatting control group;
- a find/review action cluster;
- a compact AI state tray;
- a document status/control group that opens a fuller inspector.

Avoid:

- glass behind every paragraph;
- translucent backgrounds that lower selection contrast;
- a floating bar that covers the insertion point or keyboard;
- sparkle-only AI status;
- a glass surface that remains “saved” after a failed write;
- fake window chrome or Apple-branded controls.

The same editor should remain understandable with an opaque fallback under
reduced transparency, increased contrast, or accessibility sizes.

## Content/source design

When the document starts as Markdown or imported attributed content, show the
user which mode they are in:

| Mode | Visual cue | Safe action |
| --- | --- | --- |
| source editing | source language or format label | preserve source or convert explicitly |
| rich editing | document title and format status | save through attributed format |
| read-only projection | “Preview” or equivalent | return to source to edit |
| imported content | import/source status | copy, adopt, or link according to policy |
| AI proposal | generated/provisional label | review before applying |

Do not silently flatten rich content because a custom editor cannot preserve it.
If conversion is required, show a clear choice and keep a recovery copy.

## Adaptive layout

| Width/context | Design response |
| --- | --- |
| iPhone compact | editor first, toolbar actions in native placement, review in sheet |
| iPad narrow window | collapse side tools, keep the document measure readable |
| iPad wide/Stage Manager | allow browser/inspector/editor separation without covering text |
| Mac Catalyst | menu/keyboard/pointer and multiple windows; avoid iPhone-style floating controls |
| visionOS window | system window plus readable content; use spatial controls only when task benefits |
| external keyboard | preserve visible commands and selection actions |
| Dynamic Type accessibility size | stack actions and let labels wrap |
| RTL | mirror layout where semantic, preserve document text direction |

Do not reduce type or remove text to make a formatting bar fit. Let available
space choose between a compact action group, menu, sheet, or inspector.

## Accessibility and input

A writing surface should be task-completable with:

- VoiceOver for document title, editor value, selection, formatting, find, and
  review state;
- Voice Control and Switch Control for every action;
- hardware keyboard commands on iPadOS and Mac Catalyst;
- pointer and trackpad selection where supported;
- dictation and Pencil input where supported;
- Dynamic Type, Bold Text, contrast, reduced transparency, and reduced motion;
- localized and bidirectional content.

Focus rules:

- place focus intentionally when a document opens;
- do not move focus when an AI result arrives;
- return focus to the editor after review or find closes;
- move focus to a conflict or parse error only when it is the useful repair path;
- keep the selected range visible after keyboard/toolbar changes.

## Review checklist

- The document representation is named: String, AttributedString, source Markdown,
  or a richer editor model.
- The TextEditor initializer matches the formatting claim.
- Selection is modeled as transient editor state with a revision check.
- Formatting controls match what the writer can preserve.
- Find/replace has one deterministic editor owner.
- Writing Tools behavior is deliberate and the unavailable path is useful.
- AI candidates show source, revision, scope, and explicit apply/discard.
- Glass groups real actions and has an accessible fallback.
- UIKit/TextKit 2 is isolated behind a named ownership boundary.
- Dynamic Type, RTL, VoiceOver, keyboard, pointer, Pencil, and reduced effects
  are part of the design before implementation.
- File and release proof are tracked separately from a screenshot.

## Sources

- [Text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [AttributedTextFormattingDefinition](https://developer.apple.com/documentation/swiftui/attributedtextformattingdefinition)
- [Text input and symbol modifiers](https://developer.apple.com/documentation/swiftui/view-text-and-symbols)
- [Text input formatting control visibility](https://developer.apple.com/documentation/swiftui/view/textinputformattingcontrolvisibility%28_%3Afor%3A%29)
- [findNavigator(isPresented:)](https://developer.apple.com/documentation/swiftui/view/findnavigator%28ispresented%3A%29)
- [FindContext](https://developer.apple.com/documentation/swiftui/findcontext)
- [WritingToolsBehavior](https://developer.apple.com/documentation/swiftui/writingtoolsbehavior)
- [writingToolsBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsbehavior%28_%3A%29)
- [writingToolsAffordanceVisibility(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsaffordancevisibility%28_%3A%29)
- [Writing Tools for UIKit](https://developer.apple.com/documentation/uikit/writing-tools)
- [Customizing Writing Tools behavior for system views](https://developer.apple.com/documentation/uikit/customizing-writing-tools-behavior-for-system-views)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [Instantiating attributed strings with Markdown syntax](https://developer.apple.com/documentation/foundation/instantiating-attributed-strings-with-markdown-syntax)
- [MarkdownParsingOptions](https://developer.apple.com/documentation/foundation/attributedstring/markdownparsingoptions)
- [TextKit 2 interaction sample](https://developer.apple.com/documentation/uikit/using-textkit-2-to-interact-with-text)
- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Text views HIG](https://developer.apple.com/design/human-interface-guidelines/text-views)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
