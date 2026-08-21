# TextKit 2 typography proof matrix

This matrix keeps text layout, editing, selection, accessibility, on-device
AI proposals, Liquid Glass review controls, and release evidence separate. A
beautiful paragraph in a preview is not proof that the editor remains usable
after a Dynamic Type change, a bidirectional selection, a stale model result,
or a physical-device keyboard interaction.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Stronger evidence | Do not infer |
| --- | --- | --- | --- |
| The target can use the selected text route | Minimal named-target compile with the iOS 26 SDK | A small sample target with route-specific tests | That the runtime text behavior is correct |
| The selected TextKit 2 graph is wired correctly | Compile plus a fixture that inserts, replaces, and lays out text | A UI test with selection, undo, and viewport changes | That a text view frame is the document model |
| A document lays out correctly | Deterministic paragraph and width fixtures | Long-document, attachment, and rotation tests | That one screenshot proves all fonts/locales |
| Viewport layout is bounded | Fragment/viewport instrumentation and cancellation tests | Device scroll traces with memory and hitch measurements | That a viewport controller makes all work cheap |
| Selection and hit testing are correct | Character-range and caret fixture tests | Touch, keyboard, pointer, Pencil, and VoiceOver device tasks | That a highlighted rectangle represents the right source |
| Dynamic Type is supported | Smallest/largest size fixture and UI review | Full accessibility-size matrix on physical devices | That a fixed preview size proves adaptation |
| RTL and localization are supported | Locale and layout-direction UI tests | Arabic/Hebrew plus mixed bidirectional paragraphs on device | That mirroring alone proves text semantics |
| Custom rendering remains accessible | Semantic hierarchy or accessibilityRepresentation review | VoiceOver, Switch Control, Voice Control, keyboard, and Dynamic Type tasks | That visible text automatically makes a canvas accessible |
| Core Text export is correct | Known attributed-string and bounds fixture | PDF/image comparison across fonts and color appearances | That a rendered bitmap preserves selection or accessibility |
| AI annotations are reviewable | Revision, span, schema, stale-result, and bounded-output tests | On-device model availability, cancellation, privacy, and accept/reject tasks | That fluent generated text is true or accepted |
| Liquid Glass review controls are native | SwiftUI/HIG review and reduced-transparency states | Signed physical-device interaction and contrast inspection | That custom blur is equivalent to system Liquid Glass |
| Performance is acceptable | Controlled baseline for layout, typing, scrolling, and proposal application | Representative devices with hitches, memory, energy, and thermal data | That the newest device or Debug build represents the fleet |
| Release configuration is correct | Archive inspection for target, resources, privacy, and signing | TestFlight install and physical-device smoke task | That an archive proves App Store delivery or model quality |

## Deterministic fixture set

Create fixtures before styling the feature:

- empty document;
- one short paragraph;
- a long paragraph with explicit line breaks;
- headings, links, lists, and mixed attributes;
- a replacement that changes the length before a second proposal span;
- emoji and composed character sequences;
- left-to-right, right-to-left, and mixed-direction text;
- localized strings that are longer than the development language;
- custom font and system font at every planned Dynamic Type boundary;
- a document with attachments or placeholders;
- a selection at the start, middle, end, and across paragraph boundaries;
- collapsed insertion point with typing attributes;
- selection replaced while the keyboard is visible;
- layout width changes and viewport relocation;
- model unavailable, model cancelled, malformed proposal, and stale revision;
- accepted, rejected, edited, and dismissed proposal;
- increased contrast, reduced transparency, Reduce Motion, and dim flashing
  lights;
- save failure, conflict, export cancellation, and re-opened document.

The fixture should have a known document revision and stable source IDs. Assert
both the visible text and the domain state after each mutation.

## TextKit 2 graph tests

Verify that:

- content storage has the intended attributed backing store;
- layout manager attachment occurs exactly once;
- the text container geometry is updated when the view changes size;
- edit transactions notify the layout route;
- a replacement creates the expected revision and invalidates old proposals;
- layout fragments correspond to the expected source ranges;
- line fragments return sensible typographic bounds and character mapping;
- usage bounds update after edits;
- viewport layout stops or reduces work when the surface leaves the screen;
- a secondary layout manager is synchronized intentionally, not accidentally;
- an editor rebuild does not duplicate observers, text views, or layout managers.

For a custom renderer, compare fragment and line geometry to a known reference
only after fixing the SDK, font availability, locale, scale, and container
width. Avoid pixel-only assertions when the framework legitimately changes
antialiasing or device scale.

## Selection and editing tasks

Run these tasks with touch and keyboard input:

1. place the insertion point after a composed character;
2. select a word and a paragraph;
3. extend the selection across a line wrap;
4. replace the selected content;
5. undo and redo;
6. accept a proposal that changes the selection's source range;
7. edit while an asynchronous proposal is generating;
8. rotate or resize the surface while selected text remains visible;
9. dismiss the keyboard and return focus;
10. use VoiceOver to discover text, selection, and review actions.

Record the canonical document state separately from caret geometry. A caret
that looks correct in one frame does not prove that the document range or undo
stack is correct.

## Typography and adaptation tasks

For each target screen, capture the smallest useful design and the largest
accessibility design. Check:

- no clipping, overlap, or hidden action labels;
- line spacing remains comfortable;
- metadata does not become unreadably small;
- the editor does not shrink text to fit a glass toolbar;
- headings remain headings for assistive technology;
- link and selection contrast remain usable;
- source-span annotations are not color-only;
- the review sheet grows or scrolls instead of truncating the proposal;
- toolbar controls remain discoverable when text becomes large;
- the layout works in both writing directions.

Use the HIG typography guidance as the design reference, then record the
actual target, device, locale, Dynamic Type size, appearance, and accessibility
settings for the run.

## AI proposal tests

Every proposal fixture should include:

| Fixture | Expected result |
| --- | --- |
| Current revision and matching source hash | Proposal may enter review |
| Document edited before result returns | Result is marked stale |
| Range outside the document | Proposal is rejected |
| Overlapping or ambiguous spans | Proposal requires deterministic policy or rejection |
| Invalid enum/value/string length | Proposal falls back or shows a safe error |
| Model unavailable | Editor remains usable with a deterministic non-AI path |
| Task cancelled | No review mark or domain mutation is applied |
| Person rejects | Source remains unchanged |
| Person edits before accepting | Acceptance revalidates and may become stale |
| Person accepts | New revision is persisted and annotations recompute |

Do not assert quality by matching one model's prose. Test schema validity,
provenance, range safety, cancellation, privacy, and user control. Keep raw
source content out of logs and diagnostic snapshots unless the person has
explicitly opted into that handling.

## Custom renderer and Core Text tests

For TextRenderer, verify:

- sizeThatFits and draw use the same visual assumptions;
- display padding prevents clipping of an effect;
- custom TextAttribute values map to visible runs;
- the default text remains readable when the renderer is disabled;
- animations are bounded and respect reduced-motion settings;
- the semantic text remains available to VoiceOver and selection.

For Core Text, verify:

- attributed-string attributes are intentionally supported;
- framesetter constraints match the export surface;
- frame visible range is handled and reported;
- line origins and coordinate transforms are correct;
- hit testing uses CTLine APIs rather than guessed character widths;
- font fallback and missing-font behavior are visible;
- framesetter/frame/line work stays on one controlled queue or operation;
- export is reopened and inspected by the destination consumer.

## Physical-device evidence packet

For a signed iOS 26 build, record:

- device model, OS build, display scale, and orientation;
- target bundle identity and build number;
- SDK/deployment target and availability branches;
- keyboard, pointer, Pencil, and touch path used;
- Dynamic Type and accessibility settings;
- locale and layout direction;
- document fixture and revision;
- model route, availability state, and cancellation outcome;
- frame hitches, memory, energy, and thermal observations for long content;
- screenshots or recordings only as supplemental evidence;
- whether a system text feature, share sheet, or file provider was actually
  invoked.

If the feature uses files, cloud sync, Writing Tools, or another protected
system surface, keep its evidence record separate from the local editor run.

## Release evidence

Inspect the archive for:

- target membership and framework linkage;
- privacy manifest and usage-description resources if applicable;
- custom fonts and document templates;
- extension or App Group configuration if used;
- release flags that could change model, typography, or rendering behavior;
- absence of debug-only mock documents and fake model results.

Then install the signed artifact and repeat a small physical-device smoke task.
The archive proves configuration and signing. It does not prove that all
supported devices, locales, keyboards, accessibility settings, or model states
behave identically.

## Related routes

- [TextKit 2 and Core Text layout](../42-framework-deep-dives/57-textkit-2-and-core-text-layout.md)
- [Native typography and rich-editor design](../21-design-deep-dives/77-native-typography-and-rich-editor-design.md)
- [TextKit 2 rich-editor and AI annotation route](../50-capability-recipes/80-textkit-2-rich-editor-and-ai-annotation-route.md)
- [TextKit 2 and Core Text recipes](../70-code-recipes/92-textkit-2-and-core-text-recipes.md)
- [Accessibility and adaptable UI](../10-swiftui/05-accessibility-and-adaptable-ui.md)
- [On-device AI evaluation and model-update discipline](../30-on-device-ai/10-on-device-ai-evaluation-and-model-update-discipline.md)

## Sources

- [TextKit 2 interaction sample](https://developer.apple.com/documentation/uikit/using-textkit-2-to-interact-with-text)
- [NSTextContentStorage](https://developer.apple.com/documentation/uikit/nstextcontentstorage)
- [NSTextLayoutManager](https://developer.apple.com/documentation/uikit/nstextlayoutmanager)
- [NSTextLayoutFragment](https://developer.apple.com/documentation/uikit/nstextlayoutfragment)
- [NSTextLineFragment](https://developer.apple.com/documentation/uikit/nstextlinefragment)
- [NSTextViewportLayoutController](https://developer.apple.com/documentation/uikit/nstextviewportlayoutcontroller)
- [NSTextSelection](https://developer.apple.com/documentation/uikit/nstextselection)
- [NSTextLocation](https://developer.apple.com/documentation/uikit/nstextlocation)
- [UITextView](https://developer.apple.com/documentation/uikit/uitextview)
- [Core Text](https://developer.apple.com/documentation/coretext)
- [CTFramesetter](https://developer.apple.com/documentation/coretext/ctframesetter)
- [CTFrame](https://developer.apple.com/documentation/coretext/ctframe)
- [CTLine](https://developer.apple.com/documentation/coretext/ctline)
- [SwiftUI text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Supporting VoiceOver](https://developer.apple.com/documentation/uikit/supporting-voiceover-in-your-app)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Performance testing](https://developer.apple.com/documentation/xctest/performance-tests)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
