# SwiftUI controls, commands, and adaptable-tabs capability route

## Use this route when

Use this route when an app idea needs a native SwiftUI surface with:

- semantic buttons, toggles, pickers, forms, or editors;
- reusable control styles that still behave like system controls;
- toolbars, menus, keyboard shortcuts, scene commands, or focused context;
- search in a toolbar, sidebar, inline surface, or dedicated tab;
- adaptable tabs with sections, customization, or a bottom accessory;
- a Liquid Glass functional layer around native controls;
- an on-device AI action that must remain a reviewable proposal;
- accessibility, alternate input, and physical-device proof.

This route is not a replacement for the broader navigation/presentation,
accessibility/input, or Foundation Models routes. It composes them around the
specific system-surface boundary.

## Route contract

    user outcome
      -> semantic model/control
      -> native system surface
      -> alternate input and accessibility
      -> deterministic validation/capability check
      -> domain command
      -> optional AI proposal/review
      -> persistence/system side effect
      -> proof packet

Keep these owners distinct:

| Concern | Owner |
| --- | --- |
| Label and visual state | SwiftUI view/style |
| Keyboard focus | FocusState |
| Accessibility focus | AccessibilityFocusState |
| Search query/scope | Feature/search state |
| Tab selection/path | Navigation/tab state |
| Toolbar/menu presentation | SwiftUI/system surface |
| Current focused document | FocusedValues/FocusedBinding |
| AI candidate | Feature/model boundary |
| Domain record/revision | Model/store/service |
| External side effect | Authorized system/service boundary |

## Phase 0: name the task

Write:

    A person can [outcome] from [starting context] and can recover when
    [validation, capability, permission, stale-data, or AI failure occurs].

Name the action in user language. “Generate” is incomplete; “Suggest three
titles” is a task. “Controls” is a framework category; “keep the garage
status reachable from Control Center and the app” is a product outcome.

## Phase 1: choose the semantic control

Use this starting table:

| Need | First API family | Escalate only when |
| --- | --- | --- |
| Run one action | Button | The standard button interaction cannot express a proven custom contract |
| Change Boolean | Toggle | The product needs a different presentation, not a different meaning |
| Choose values | Picker/Menu | The choices need a domain-specific searchable editor |
| Adjust value | Slider/Stepper | The value needs a custom canvas/editor with equivalent alternate input |
| Enter text | TextField/TextEditor | UIKit/TextKit is required for a capability SwiftUI does not expose |
| Group related commands | ControlGroup/Menu | The command set requires scene-level keyboard/menu integration |
| Navigate peer sections | TabView/Tab | The hierarchy needs NavigationStack or split detail |
| Search content | searchable | Systemwide indexing or semantic search needs Core Spotlight/App Intents |

Start with the native control even if the first visual mockup shows a custom
glass pill. The semantic shape determines the available accessibility,
keyboard, pointer, and system-surface routes.

## Phase 2: define the state machine

For an ordinary action:

    available -> running -> succeeded
                    |
                    +-> failed -> retry/manual

For an editor:

    presented -> pristine -> dirty -> validating -> saving -> saved
                         |                 |
                         +-> invalid      +-> failed

For on-device AI:

    unavailable
      -> checking
      -> generating
      -> proposal
      -> applying
      -> saved

Any state can route to:

    canceled | refused | stale | failed | manual continuation

Do not use a disabled Button alone as the state machine. Keep a visible
status/value and a recoverable route.

## Phase 3: build the control/style layer

Apply ButtonStyle, ToggleStyle, LabelStyle, or a built-in style at the
narrowest container that needs it. Prefer standard styles when they already
express the platform convention.

Style review:

1. Does the style keep standard control interaction?
2. Does it respect ButtonRole or Toggle state?
3. Does the label survive toolbar/menu/overflow adaptation?
4. Does the hit region remain usable at large text and with pointer input?
5. Does it expose selected, disabled, loading, and error state without color
   alone?
6. Does the custom style avoid attaching a second gesture?
7. Does the visual effect have a reduced-transparency/motion route?

Use PrimitiveButtonStyle only when custom interaction is the product behavior
and the keyboard/accessibility/domain routes are designed alongside it.

## Phase 4: build the form boundary

Create a draft value and keep the committed record separate. The form should
be able to:

- present empty, existing, and stale source records;
- retain user input across errors;
- validate local constraints before side effects;
- focus the first actionable error;
- show saving and prevent duplicate commits;
- cancel or recover a long-running operation;
- dismiss safely without claiming an uncommitted save.

For AI-assisted fields:

    field/selection + source revision
      -> explicit action
      -> bounded model request
      -> candidate
      -> visible comparison/edit
      -> validate
      -> commit

The model adapter should not write directly to the store. The domain command
receives an approved typed candidate and validates the current source
revision.

## Phase 5: expose commands and menus

For each primary domain command, map its supported surfaces:

| Domain command | Visible | Menu | Shortcut | App Intent |
| --- | --- | --- | --- | --- |
| Save draft | Button/toolbar | Menu/title menu | default action if suitable | Optional |
| Cancel editing | Button | Menu | cancel action if suitable | Usually no |
| Rewrite selection | Button | Menu | Custom only if frequent | Optional |
| Delete record | Button with confirmation | Menu/context menu | Rare | Optional |
| Switch view | Toggle/Picker | Menu | Optional | Optional |

Use Commands and CommandGroup for scene-level routes. Use FocusedValue or
FocusedBinding to pass the current document or selection. Handle missing or
read-only context explicitly.

Use Menu for compact secondary access and contextMenu for object-related
actions. Keep a visible route for core actions. Ensure destructive actions
use the correct role and confirmation.

## Phase 6: compose the toolbar

Record the toolbar intent:

    navigation | title/orientation | primary action | search | secondary menu

Use semantic ToolbarItemPlacement values. Allow the system to move items into
overflow as space changes. If the toolbar is customizable, use toolbar with a
stable ID and stable item IDs, then test the default and customized layouts.

ToolbarRole is useful when the toolbar represents a browser, editor, or
navigation stack and the semantic role should guide system composition.

Do not make a toolbar title or glass capsule the only place where the user can
recover a failed AI action. Keep status and retry visible in the content or
an accessible action route.

## Phase 7: add search

Choose the placement from the user task:

| Search task | Placement strategy |
| --- | --- |
| Filter one list | Apply searchable to the list/column |
| Search list/detail content | Apply to NavigationSplitView or relevant column |
| Fast retrieval | Toolbar search or search tab with immediate activation |
| Discovery | Search tab with suggestions/categories |
| Refinement | Tokens and search scopes |

Store:

    query text
    selected tokens
    selected scope
    isSearching/presentation state
    request ID/revision
    result state

For async search, cancel or ignore stale requests. For AI-assisted search,
show the deterministic result/source relationship and label generated
summaries as generated. Search should still work manually when the on-device
model is unavailable.

## Phase 8: build adaptable tabs

Define a stable tab value enum or equivalent identity. For each destination,
record:

| Field | Example |
| --- | --- |
| Selection value | library |
| User-facing label | Library |
| System image | books.vertical |
| Deep-link identity | library |
| Nested path owner | LibraryRoute |
| Customization ID | app.library |
| Essential? | Yes |
| Supports hidden state? | No |

Use TabSection for secondary groups and sidebarAdaptable where the hierarchy
should adapt across platforms. Keep the compact iPhone tab count understandable
and avoid treating a tab as an action button.

For TabViewCustomization:

1. attach stable customization IDs;
2. persist with AppStorage or SceneStorage at the correct scope;
3. disable customization for essential tabs/sections;
4. preserve sensible defaults;
5. provide a reset/migration rule;
6. test hidden tab plus deep link/App Intent behavior;
7. confirm VoiceOver still exposes selection and labels.

## Phase 9: add a bottom accessory only when it helps

Add tabViewBottomAccessory for a compact contextual status/action. Model:

    absent -> visible/normal -> inline/collapsed -> dismissed/completed

Read tabViewBottomAccessoryPlacement and make the content layout adapt. Do
not place a dense form or second navigation system in the accessory.

The accessory must not become the sole route to a core result. For example, a
mini-player can be opened from the selected tab and a Now Playing route; a
recording status can be reached from the recording screen and notification
route; an AI review can remain in the review screen with a compact resume
accessory.

## Phase 10: add the Liquid Glass layer

Use this composition order:

    standard SwiftUI/system surface
      -> native semantic controls
      -> custom glass only for a compact functional cluster
      -> reduced-effects fallback

Use standard system surfaces for tabs, toolbars, menus, and controls first.
When adding custom glass:

- keep the group’s semantics on native controls;
- use regular glass for dense/contrast-sensitive content;
- use clear glass only over a proven rich background;
- preserve stable IDs for transitions;
- remove or simplify morphing under Reduce Motion;
- switch to a more opaque/standard-material route under Reduce Transparency;
- test scrolling, Dynamic Type, contrast, and hit regions;
- inspect the accessibility tree for decoration and duplicates.

## Phase 11: attach an AI action safely

The route for a model-backed action is:

    explicit user invocation
      -> capability/language asset check
      -> source capture and revision
      -> bounded request with cancellation
      -> typed candidate
      -> review/edit
      -> deterministic validation
      -> explicit Apply
      -> domain commit
      -> saved/retry/conflict state

Use Button(intent:) or an App Intent route when the action should be exposed
to system surfaces, but keep the in-app command and App Intent on the same
domain authority. The App Intent should not bypass the review boundary for a
sensitive or destructive generated action.

## Phase 12: proof packet

Create one packet with:

| Artifact | Required evidence |
| --- | --- |
| Source record | Official API and HIG links |
| Build | Named target, SDK, deployment target, warnings |
| Fixture | Empty/loaded/editing/invalid/loading/proposal/saved/stale/failed |
| UI test | Semantic queries, selection, forms, commands, search, tabs |
| Accessibility | Inspector/audit plus physical VoiceOver/Voice Control/Switch Control |
| Input | Touch, keyboard/Full Keyboard Access, pointer/hover where supported |
| Adaptation | Dynamic Type, localization, light/dark, contrast/transparency/motion |
| System | App Intent/deep link/tab customization if claimed |
| Device | Signed physical run on representative iPhone/iPad |
| Release | Archive/entitlements/privacy/production-like account state |

The proof packet should state what was not tested. A preview of a glass button
does not prove Liquid Glass system treatment, and a generated candidate does
not prove a committed record.

## Common failure modes

| Failure | Better route |
| --- | --- |
| Custom glass pill owns a tap gesture | Native Button with a style/effect shell |
| One disabled “AI” button | Explain availability and provide manual route |
| Save command has separate logic in toolbar/menu | One typed domain command |
| Menu contains every feature | Keep frequent actions visible; group secondary commands |
| Search only filters visible rows | Query a source/result model with cancellation and scope |
| Dozens of top-level tabs | Reduce peer areas; use browse/search hierarchy |
| Bottom accessory becomes a second app bar | Keep it compact and contextual |
| Tab customization breaks deep links | Resolve semantic destination before presentation |
| Large text clips the primary action | Wrap/reflow and test max Dynamic Type |
| AI output appears as saved data | Show proposal/review and commit only after approval |

## Sources

- [Button](https://developer.apple.com/documentation/swiftui/button)
- [ButtonStyle](https://developer.apple.com/documentation/swiftui/buttonstyle)
- [ToggleStyle](https://developer.apple.com/documentation/swiftui/togglestyle)
- [LabelStyle](https://developer.apple.com/documentation/swiftui/labelstyle)
- [ControlGroup](https://developer.apple.com/documentation/swiftui/controlgroup)
- [Form](https://developer.apple.com/documentation/swiftui/form)
- [Menus and commands](https://developer.apple.com/documentation/swiftui/menus-and-commands)
- [Commands](https://developer.apple.com/documentation/swiftui/commands)
- [KeyboardShortcut](https://developer.apple.com/documentation/swiftui/keyboardshortcut)
- [FocusedValues](https://developer.apple.com/documentation/swiftui/focusedvalues)
- [ToolbarItemPlacement](https://developer.apple.com/documentation/swiftui/toolbaritemplacement)
- [ToolbarRole](https://developer.apple.com/documentation/swiftui/toolbarrole)
- [toolbar(id:content:)](https://developer.apple.com/documentation/swiftui/view/toolbar%28id%3Acontent%3A%29)
- [Adding a search interface to your app](https://developer.apple.com/documentation/swiftui/adding-a-search-interface-to-your-app)
- [Search](https://developer.apple.com/documentation/swiftui/search)
- [Performing a search operation](https://developer.apple.com/documentation/swiftui/performing-a-search-operation)
- [TabView](https://developer.apple.com/documentation/swiftui/tabview)
- [TabSection](https://developer.apple.com/documentation/swiftui/tabsection)
- [TabViewStyle](https://developer.apple.com/documentation/swiftui/tabviewstyle)
- [TabViewCustomization](https://developer.apple.com/documentation/swiftui/tabviewcustomization)
- [tabViewCustomization(_:)](https://developer.apple.com/documentation/swiftui/view/tabviewcustomization%28_%3A%29)
- [tabViewBottomAccessory(content:)](https://developer.apple.com/documentation/swiftui/view/tabviewbottomaccessory%28content%3A%29)
- [tabViewBottomAccessoryPlacement](https://developer.apple.com/documentation/swiftui/environmentvalues/tabviewbottomaccessoryplacement)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Human Interface Guidelines: Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- [Human Interface Guidelines: Menus](https://developer.apple.com/design/human-interface-guidelines/menus)
- [Human Interface Guidelines: Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)
- [Human Interface Guidelines: Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
