# SwiftUI text-editing and rich-content proof matrix

## Purpose

Use this matrix for any claim involving SwiftUI TextEditor, attributed text
editing, TextSelection, AttributedTextSelection, formatting definitions, native
find/replace, Writing Tools, Markdown parsing, UIKit/TextKit 2 bridges,
Liquid Glass writing surfaces, or on-device AI writing review.

Record:

- app/build, Xcode, SDK, deployment target, target membership, and platform;
- content model, canonical format, UTType/document ID, and source revision;
- editor initializer and availability/fallback path;
- selection kind, range/affinity, focus owner, and selected source hash;
- allowed formatting scope, mixed attributes, formatting control visibility, and
  full-value validation result;
- find/replace owner, current query, replacement, undo group, and editor focus;
- Writing Tools policy, affordance state, capability/device state, temporary
  mutation gate, and final result;
- UIKit/TextKit 2 bridge, coordinator identity, selection, first responder,
  and teardown state;
- Markdown source, parsing options, base URL, custom attributes, diagnostics,
  links, and source-position policy;
- AI capability/model state, request scope, source revision, candidate, stale
  result, validation, review action, and commit;
- locale, layout direction, Dynamic Type, Bold Text, contrast, transparency,
  motion, input mode, and accessibility settings;
- artifact path, test date, physical device/target identity, and tester.

A screenshot proves a visual fixture. It does not prove rich editing, selection,
Writing Tools, find/replace, keyboard/Pencil input, document persistence, or
AI commit safety.

## Evidence levels

| Level | Can support | Cannot support alone |
| --- | --- | --- |
| Official source | API intent and HIG guidance | This app's behavior |
| Static route review | Content/selection/formatting ownership | Runtime editor/system behavior |
| Named-target compile | Initializers, availability, protocols, target membership | Physical input, formatting UI, system Writing Tools |
| Unit/fixture test | Parsing, selection revision, formatting validation, candidate staleness | Keyboard, VoiceOver, system text tools |
| Preview | Editor hierarchy and state fixtures | Text-system selection, Writing Tools, find, physical feel |
| UI test | Labels, typing, toolbar/find/review task | Device-only system features and physical ergonomics |
| Simulator | Layout, keyboard simulation, localization, many state paths | Hardware keyboard/Pencil, Writing Tools/model readiness, release |
| Signed physical target | iPhone/iPadOS/Catalyst input, accessibility, system model state | App Store distribution or every OS/device |
| System-surface run | Find/replace, Writing Tools, keyboard menus, share/provider entry | All target combinations and release metadata |
| Performance run | Long-document latency/hitches/memory/thermal on a target | Correctness of every format or language |
| Archive/release artifact | Target/extension membership, processed config, entitlements, signing | Editor task completion or system model availability |
| TestFlight/release smoke | Signed build task behavior on selected devices | Universal correctness or production health |

## Fixture contract

Use deterministic text fixtures rather than relying on generated content.

~~~swift
struct TextEditorProofFixture: Hashable, Sendable {
    let target: String
    let documentID: String
    let contentModel: String
    let canonicalFormat: String
    let sourceRevision: Int
    let textLength: Int
    let attributes: [String]
    let selectionState: String
    let selectionAffinity: String
    let formattingPolicy: String
    let findState: String
    let writingToolsPolicy: String
    let writingToolsState: String
    let markdownState: String
    let aiState: String
    let localeIdentifier: String
    let layoutDirection: String
    let dynamicType: String
    let inputMode: String
    let accessibilityModes: [String]
}
~~~

Minimum fixture families:

- empty, short, long, and paragraph-heavy plain text;
- attributed runs with valid, mixed, unsupported, and custom attributes;
- Markdown with valid links, relative links, malformed syntax, partial parse,
  extended attributes, source positions, and bidirectional text;
- insertion point, selected range, mixed-format range, empty selection, stale
  selection, and multi-selection where supported;
- clean, dirty, saving, conflict, and read-only document states;
- find no-match, one-match, many-match, replace, undo, and cancellation;
- Writing Tools automatic/limited/complete/disabled and unavailable/active/
  cancelled/completed fixtures;
- AI unavailable, reviewing, partial, candidate, stale, invalid, discarded,
  committed, and save-failed fixtures;
- narrow iPhone, narrow/wide iPadOS, Catalyst, large Dynamic Type, RTL, and
  reduced-effects variants.

## Content model and initializer matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Plain TextEditor edits long-form text | Named-target compile plus UI task | Empty, multiline, long text, undo, cancel | Text changes are reflected in the owned model |
| Plain editor is not rich text | Static review plus formatting UI check | Formatting action, unsupported attribute | Product copy and controls match the actual model |
| Attributed TextEditor initializer compiles | Selected SDK compile | Deployment fallback, Catalyst/iPadOS differences | Target compiles with the intended binding types |
| Attributed text edits | Physical/UI run | Mixed runs, insertion, deletion, undo/redo | Attributed content changes and reopens correctly |
| Text renders supported attributes | Visual/UI run plus serialized fixture | Unsupported Foundation/UIKit/AppKit attributes | Rendered result is documented and validated |
| Text selection binds correctly | Compile plus selection UI task | Insertion point, range, multiple selections | Selection-dependent UI follows the actual selection |
| Attributed selection binds correctly | Compile plus formatted selection task | Mixed attribute range, stale index | Formatting/review actions target the current content |
| Plain fallback is useful | Availability compile plus target UI | Older deployment, unsupported surface | User can still complete the writing task |
| Content model remains authoritative | Static review plus edit/reopen test | View recreation, background result, conflict | No hidden view-only content is lost |

## Selection and focus matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Insertion point is represented | UI/accessibility task | Empty document, end/start, keyboard movement | Focus and insertion state are visible/announced |
| Selected range is represented | Physical/UI task | Drag, keyboard, pointer, Pencil, long text | Source text matches the selection |
| Affinity is handled | RTL/mixed-direction physical or UI run | Upstream/downstream boundary, bidi punctuation | Cursor/selection behavior is recorded for the target |
| Selection is revision-scoped | Unit test plus edit-during-task UI | Insert before range, replace, undo, external update | Stale selection cannot apply to wrong source |
| Selection action is disabled safely | State/UI fixture | Empty, protected, read-only, unavailable | User sees a useful reason or alternate action |
| Focus owner is deterministic | UI task with one/multiple editors | Find, sheet, background result, navigation | Actions affect the intended editor |
| Focus restoration works | Physical/UI lifecycle run | Review apply/discard, find close, relaunch | Focus returns to useful content without stealing it |
| Keyboard route works | iPad keyboard/Catalyst physical run | Command key, selection, undo, find, format | Core task completes without touch |
| Pointer/Pencil route works | Physical target run where supported | Hover, selection, handwriting, context menu | Alternate input is optional but usable |
| VoiceOver selection is meaningful | Accessibility task | Selection, formatting, generated candidate | User can discover source, selection, and actions |

## Formatting definition and control matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Formatting definition compiles | Named-target compile | SDK/deployment availability, scope imports | Target builds with the intended attribute scope |
| Allowed attributes are visible | UI/system run | Mixed value, empty selection, read-only | Controls match document policy |
| Value constraints affect system UI | Target run with controls | Incompatible values, disabled control | Incompatible controls are hidden/disabled as intended |
| Off-screen content is validated | Full-value unit/serialization test | Unrendered range, imported value, AI value | Writer rejects or normalizes invalid attributes |
| Formatting visibility is deliberate | UI/accessibility run | Context menu, keyboard toolbar, custom toolbar | No duplicate or inaccessible action path |
| Formatting action is undoable | UI/unit integration | Rapid repeated action, selection change | Undo returns prior attributed state |
| Formatting survives persistence | Round-trip document test | Migration, export, provider, conflict | Reopened content retains the allowed representation |
| Link attributes are safe | Parser/security/UI test | Scheme/host/port/Unicode/AI link | Link policy is enforced at interaction and write boundaries |
| Custom attributes are semantic | Unit/visual/accessibility test | Unknown attribute, unsupported renderer | Meaning is not lost or misrepresented as style |

## Find and replace matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Native find navigator presents | Named-target UI/system run | No focus, keyboard, cancel | Find interface appears for the intended editor |
| Find target is deterministic | One-editor/multi-editor test | Several editors, navigation, sheet | Intended editor owns the operation |
| Replace mutates document safely | Integration/UI test | Many matches, no match, cancel | Revision/dirty/save state updates once |
| Replace is undoable | UI test | Repeated replace, undo after close | Full replacement is recoverable |
| Find/replace can be disabled | Compile/UI fixture | Read-only/protected document | Disabled state has honest explanation |
| FindContext custom route works | Named target compile/UI | supportsReplace false, close, focus | Custom route follows native presentation state |
| Localization/accessibility works | VoiceOver/RTL/Dynamic Type run | Long labels, no matches | Query, results, replacement, and actions are clear |

## Writing Tools matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Policy compiles | Named-target compile | iOS/iPadOS/Catalyst availability | Target accepts the intended behavior |
| Automatic policy is honest | Target/device run | Feature unavailable, system changes | App does not imply a guaranteed model route |
| Limited behavior is useful | Physical editor run | Accept, reject, cancel, partial | User can review system changes |
| Complete behavior is safe | Physical editor run | Temporary edits, interruption, final change | App mutation gate prevents racing transforms |
| Disabled policy works | UI/accessibility run | Protected text, code, quotes | No accidental system mutation |
| Affordance visibility is correct | Catalyst/device run | macOS/Catalyst, hidden/visible | System affordance follows product policy |
| App autosave does not race | Integration/physical run | Active Writing Tools, background, conflict | Confirmed revision remains safe |
| Writing Tools unavailable fallback | Capability fixture/device run | Unsupported device/language/setting | Plain editor and app actions remain useful |
| Custom UIKit Writing Tools route works | Named target compile plus physical run | Ignored ranges, coordinator teardown | Protected ranges and lifecycle are correct |

## Markdown and attributed-content matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Markdown parses with explicit policy | Parser unit tests | Full, inline-only, whitespace, language | Options and failure result are recorded |
| Partial parse is recoverable | Fixture/UI test | Malformed delimiter/link/table | Raw source and diagnostics remain available |
| Source positions are useful | Parser fixture | Unicode, localized, multi-line | Source spans map back correctly or are omitted honestly |
| Extended attributes are controlled | Parser/security test | Allowed/forbidden custom syntax | Custom attribute policy is explicit |
| Base URL policy is safe | Link/security test | Relative/absolute/malicious URL | Link interaction is validated |
| AttributedString serializes | Round-trip test | Supported/unsupported/custom attrs | Format preserves intended content |
| Preview/editor divergence is clear | UI/design test | Source mode, rich mode, read-only projection | User knows which representation is editable |
| AI/imported attributes are validated | Unit/integration test | Unknown style, unsafe link, oversized run | Invalid content is rejected or normalized |

## UIKit and TextKit 2 bridge matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Bridge is justified | Static route review | TextRenderer/SwiftUI route could suffice | Escalation reason is documented |
| TextKit 2 target compiles | Named-target compile | Minimum OS, Catalyst, conditional code | Intended target builds without hidden legacy graph |
| SwiftUI updates UIKit once | Integration test | View recreation, equal value, rapid edits | No cursor jump or update loop |
| UIKit changes reach model | UI/integration test | Selection, undo, composition, Writing Tools | Normalized content updates current revision |
| Coordinator lifecycle is safe | UI teardown/instrumented run | Navigation, sheet close, document switch | No stale callbacks or retained view |
| TextKit selection is mapped | Selection fixture/UI run | UTF-16, Unicode grapheme, bidi | Range mapping is explicit and tested |
| Accessibility survives bridge | VoiceOver/physical run | Labels, selection, actions, Dynamic Type | Editor remains a semantic text surface |
| Custom Writing Tools works | Physical target run | Ignore ranges, temporary edits, cancellation | Protected ranges and final result are correct |

## App-owned AI writing matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Capability is optional | Device/availability fixture | Unsupported hardware, disabled model | Editor works without app AI |
| Request scope is bounded | Static adapter review plus fixture | Selection, paragraph, attachment, full doc | Only intended source is sent |
| Source revision is captured | Unit request/response test | Edit during request, undo, external update | Candidate records exact source revision |
| Candidate is typed | Parse/schema/length/attribute tests | Empty, huge, unsafe link, invalid attr | Invalid output cannot reach document |
| Candidate is reviewable | UI/accessibility task | Partial, stale, failed, no-op | Source/proposal/actions are discoverable |
| Cancellation is safe | Async/UI lifecycle test | Selection change, scene close, termination | No late callback mutates new state |
| Stale candidate is blocked | Revision conflict test | Concurrent edit, save, provider update | Apply is blocked/rebased/confirmed |
| Commit uses document path | Integration/save test | Serialization/provider failure | AI edit follows ordinary dirty/conflict/recovery |
| Privacy copy is accurate | Static/UI review | On-device claim, logs, telemetry | Product says what is processed/stored |
| Performance is bounded | Target performance run | Long selection, repeated requests, thermal | Timing/memory/cancellation evidence exists |

## Liquid Glass and visual hierarchy matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Glass group has task meaning | Design review plus preview | Full-page decorative glass, no-op controls | Group can be named and removed without losing meaning |
| Text remains primary | Light/dark target visual run | Long content, selection, attachments | Glass does not obscure text or cursor |
| Formatting controls adapt | iPhone/iPadOS/Catalyst visual run | Narrow width, keyboard, Dynamic Type | Controls move/stack without covering editor |
| Status is semantic | UI/accessibility fixture | dirty, saving, conflict, AI stale | Status is text/label, not only material/color |
| Reduced effects work | Device settings run | Reduced transparency/motion, contrast | Actions and selection remain legible |
| AI review is distinct | UI fixture | partial, stale, committed | Review and document state are not conflated |

## Target, performance, and release matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| iPhone editing works | Physical iPhone task | keyboard, focus, VoiceOver, long text | Create/edit/find/review/save completes |
| iPadOS editing works | Physical iPad task | external keyboard, Pencil, resize, Stage Manager | Selection/format/find/review works at widths |
| Mac Catalyst works | Actual Catalyst compile/run | menu, pointer, Writing Tools affordance | Core task completes as a Mac app |
| visionOS/watchOS claim is bounded | Target run if claimed | unsupported full editor, projection | Only tested task is described |
| Long text is responsive | Performance/hitch run | attributes, attachments, rapid edit, AI | Hitches/memory/thermal evidence names target |
| Archive preserves editor route | Archive/processed build inspection | target membership, availability branches | Signed artifact has intended code/configuration |
| Release task works | TestFlight/release smoke | system feature unavailable, account/provider | Build identity and evidence are recorded |

## Sources

- [Text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [AttributedTextFormattingDefinition](https://developer.apple.com/documentation/swiftui/attributedtextformattingdefinition)
- [AttributedTextValueConstraint](https://developer.apple.com/documentation/swiftui/attributedtextvalueconstraint)
- [Text input and symbol modifiers](https://developer.apple.com/documentation/swiftui/view-text-and-symbols)
- [Text input formatting control visibility](https://developer.apple.com/documentation/swiftui/view/textinputformattingcontrolvisibility%28_%3Afor%3A%29)
- [findNavigator(isPresented:)](https://developer.apple.com/documentation/swiftui/view/findnavigator%28ispresented%3A%29)
- [FindContext](https://developer.apple.com/documentation/swiftui/findcontext)
- [WritingToolsBehavior](https://developer.apple.com/documentation/swiftui/writingtoolsbehavior)
- [writingToolsBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsbehavior%28_%3A%29)
- [writingToolsAffordanceVisibility(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsaffordancevisibility%28_%3A%29)
- [Writing Tools for UIKit](https://developer.apple.com/documentation/uikit/writing-tools)
- [Customizing Writing Tools behavior for system views](https://developer.apple.com/documentation/uikit/customizing-writing-tools-behavior-for-system-views)
- [TextKit 2 interaction sample](https://developer.apple.com/documentation/uikit/using-textkit-2-to-interact-with-text)
- [UIKit integration](https://developer.apple.com/documentation/swiftui/uikit-integration)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [Instantiating attributed strings with Markdown syntax](https://developer.apple.com/documentation/foundation/instantiating-attributed-strings-with-markdown-syntax)
- [MarkdownParsingOptions](https://developer.apple.com/documentation/foundation/attributedstring/markdownparsingoptions)
- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Text views HIG](https://developer.apple.com/design/human-interface-guidelines/text-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
