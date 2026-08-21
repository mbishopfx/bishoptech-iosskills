# SwiftUI controls, forms, commands, and adaptable tabs

## Purpose

SwiftUI’s system surfaces are a composition system, not a bag of decorative
widgets. A native result comes from keeping four contracts separate:

    semantic control
      -> adaptive system presentation
      -> command/input route
      -> domain action and proof

This deep dive covers the layer between the basic SwiftUI control catalog and
the larger navigation/accessibility routes already in this knowledge base. It
focuses on control styles, forms, menus, commands, toolbars, search, adaptable
tabs, bottom accessories, Liquid Glass functional layers, and on-device AI
actions that need a human approval boundary.

The exact overloads and availability in this page must be compiled against the
selected Xcode and SDK. Apple documentation can expose new symbols, beta
symbols, and platform-specific behavior before a project’s deployment target
can use them.

## The native-surface contract

For each visible control, record:

| Question | Example answer |
| --- | --- |
| What is the user outcome? | Save the edited note |
| What is the semantic control? | Button with the localized title Save |
| What state does it expose? | Enabled, saving, saved, failed |
| What alternate routes reach it? | Touch, VoiceOver, Voice Control, keyboard shortcut |
| Where does it appear? | Form toolbar, menu, command, App Intent |
| What owns the mutation? | Note editor domain command |
| What is the recovery path? | Preserve draft and show Retry |
| What proves it? | Compile, UI test, accessibility audit, device, signed system run |

Do not let the visual shell, menu presentation, keyboard shortcut, or AI
proposal become the owner of domain truth. The same domain command should be
reachable from the visible button, menu item, command, App Intent, and
accessibility action when those routes represent the same task.

## Standard controls before custom styles

Start with the semantic control that describes the behavior:

| Outcome | Native starting point |
| --- | --- |
| Initiate an action | Button |
| Change a Boolean | Toggle |
| Choose one or more values | Picker, Menu, or control group |
| Adjust a continuous value | Slider |
| Adjust a bounded value | Stepper |
| Enter a short value | TextField |
| Enter longer text | TextEditor |
| Choose a date/time | DatePicker |
| Show progress | ProgressView |
| Show a measured value | Gauge |
| Navigate to a destination | NavigationLink or a typed route |
| Offer an external URL | Link |

Standard controls bring platform behavior, accessibility semantics, keyboard
and pointer conventions, pressed/selected/disabled states, and container-aware
presentation. A custom drawing may look like a control, but it does not gain
those contracts merely by attaching an onTapGesture.

### Button and ButtonStyle

Button represents an action. Its label should be a localized title, a Label
with a title and system image, or another view that clearly describes the
action. The convenience initializers and Label pattern allow SwiftUI to adapt
the title and icon in toolbars and menus. An icon-only presentation can still
retain the title for VoiceOver.

Use ButtonRole when the action is cancel or destructive. The role lets the
system and custom ButtonStyle respond to the semantic purpose. A destructive
action still needs the appropriate confirmation and domain authorization; a
red tint is not confirmation.

ButtonStyle changes appearance while retaining the standard Button interaction
behavior. PrimitiveButtonStyle changes interaction behavior too, so reserve it
for a real interaction contract that cannot be represented by Button. A
custom style should read configuration state such as isPressed and role rather
than inventing a second action system.

Good style boundary:

    Button(action: save)
      -> ButtonStyle reads pressed/role state
      -> visual feedback
      -> save domain command

Bad style boundary:

    custom gesture shell
      -> private tap state
      -> mutation that the Button, menu, and VoiceOver cannot share

### ToggleStyle, LabelStyle, and ControlGroup

Toggle represents a persistent Boolean choice. SwiftUI supplies built-in
switch, button, checkbox, and automatic toggle styles. Use button-style
toggles when the context calls for a compact stateful action, but keep the
label and on/off state understandable without tint alone.

Label is the bridge between meaning and adaptive presentation. Its built-in
automatic, icon-only, title-and-icon, and title-only styles are useful when a
toolbar, menu, compact layout, or accessibility setting changes the available
space. A visually icon-only label should retain a useful title for assistive
technology.

ControlGroup is a semantic container for related controls. Its optional label
helps SwiftUI describe the group when the context moves it into an overflow
menu. Use it for a small family such as view modes, text formatting, or
transport controls. Do not use it to hide unrelated actions behind a branded
glass pill.

### Roles, states, and disabled controls

Disabled is a presentation and interaction state, not an explanation. If a
person needs to understand why an action is unavailable, show a nearby status
or help route and keep the explanation accessible. For an unavailable
on-device model, provide a manual route rather than leaving a permanently
disabled “magic” button.

Keep state families separate:

| State | Owner |
| --- | --- |
| Is the button pressed? | SwiftUI control configuration |
| Is the action currently allowed? | Domain capability/authorization |
| Is a request running? | Feature operation |
| Did the request produce a candidate? | Generated proposal |
| Was a candidate committed? | Domain record/revision |

## Forms and validation

Form, Section, and native input controls provide an adaptive editing surface.
They are especially valuable when the same task must work at multiple Dynamic
Type sizes, with keyboard input, with VoiceOver, and in a sheet or navigation
destination.

### The draft boundary

Use a draft model rather than binding every field directly to a committed
record:

    source record
      -> editable draft
      -> deterministic validation
      -> optional generated proposal
      -> explicit commit
      -> saved record/revision

Validation should be deterministic for constraints the app can know:
required fields, ranges, formats, duplicate IDs, permissions, stale
revisions, and external-service availability. An on-device AI proposal can
suggest a value or transform text, but it does not replace validation or
approval.

### Field-level and form-level errors

Place a concise error next to the invalid field. When multiple fields fail,
also provide a summary or status region that tells the person what to fix and
offers a route to the first actionable field. Preserve the entered draft when
validation, permission, model, or network work fails.

Model the form as a state machine:

    idle -> editing -> validating -> saving -> saved
                    |                  |
                    +-> invalid        +-> failed

Do not disable every field while saving if a cancel or correction route is
safe. Do prevent duplicate commits and make the current operation visible.

### Focus and submit behavior

Use FocusState for deliberate movement between fields after submit or
validation. Keep keyboard focus separate from AccessibilityFocusState. A
VoiceOver focus move to an error is not permission to mutate the draft, and
dismissing the keyboard is not a save action.

Use TextField/TextEditor’s native editing, selection, input methods,
submitLabel, and onSubmit behavior. Avoid model generation on every keystroke
unless the product has explicit debounce, cancellation, privacy, and cost
rules. For AI editing:

    text/revision/selection
      -> explicit Suggest or Transform action
      -> cancellable proposal
      -> review
      -> Accept, Edit, or Reject

### Form surfaces and Liquid Glass

Let Form, the sheet, the toolbar, and system controls own their standard
appearance first. Use custom Liquid Glass only for a compact functional group
that clarifies an action or status. Dense field labels, error text, and long
generated content should not sit on an unstable translucent background merely
to create a glass aesthetic.

Test a form in:

- largest supported Dynamic Type sizes;
- long localized labels and right-to-left layout;
- light and dark appearance;
- Increase Contrast and Differentiate Without Color;
- Reduce Transparency and Reduce Motion;
- hardware keyboard, VoiceOver, Voice Control, and Switch Control;
- small and large sheet detents or compact/regular windows.

## Menus and commands

Menus expose context-dependent commands. Commands expose related actions at
the scene level and can provide main-menu routes on macOS and key-command
routes on iOS. Use the same domain action authority under both.

### Menu composition

Use Menu for secondary or infrequent actions that belong near the current
context. Use contextMenu for a small set of item-related actions that are
helpful when people reveal the menu. Never put the only route to a core task
inside a hidden context menu.

Organize menu items in a predictable order:

1. frequent or primary related actions;
2. state-changing or view options;
3. secondary actions;
4. destructive actions at the end, with the correct role.

Prefer one level of submenu when a menu needs grouping. A submenu title should
tell the person what it contains. Use uniform icon treatment within a menu
group; do not sprinkle symbols randomly. A toggled menu item should expose its
current state and change it through the same Toggle/domain command route.

ControlGroup can help a toolbar item or menu adapt when space changes. Use
labels that remain meaningful when the system moves an item to overflow.

### Scene commands and focused context

Use the commands scene modifier, Commands, CommandMenu, and CommandGroup for
commands that should be available beyond one button’s immediate view. Use
FocusedValue or FocusedBinding to publish the current document, selection, or
editor context to a command surface. The command must handle missing context,
read-only state, stale revision, and authorization failure.

Use keyboardShortcut for a semantic command that already exists as a Button
or Toggle. Use onKeyPress for a focused view that genuinely owns raw key
handling. Do not intercept a standard text-editing shortcut to imitate a
custom command.

The command contract is:

    discoverable label
      -> current focused context
      -> capability/authorization check
      -> domain command
      -> result/status
      -> keyboard/accessibility confirmation

### AI actions in menus and commands

On-device AI actions should be named for their user outcome: Suggest
summary, Rewrite selection, Extract fields, or Compare drafts. Avoid labels
that imply the model is authoritative. If a proposal is pending, expose
Review proposal, Accept, Edit, Reject, Cancel, or Continue manually as
appropriate.

Every AI action route should define:

| State | Surface behavior |
| --- | --- |
| Unavailable | Explain the limitation and show the manual route |
| Checking | Show a concise capability/status indicator |
| Generating | Show progress and Cancel; do not move focus per token |
| Proposal | Show source, candidate, caveat, and explicit review actions |
| Applying | Prevent duplicate commit and verify revision/authorization |
| Saved | Show durable result and next action |
| Stale/failed | Preserve source and offer refresh/retry/manual continuation |

The menu or shortcut invokes the same domain command as the visible review
button. A model output is candidate data until the user’s explicit action
passes validation and commits it.

## Toolbars and title menus

Toolbars orient people, expose frequent commands, and provide navigation or
search. A tab bar navigates between top-level areas; it is not a substitute
for a toolbar of actions.

Use semantic ToolbarItemPlacement values such as navigation, principal,
primaryAction, and secondaryAction where the intent is more important than an
exact coordinate. SwiftUI can move items into overflow as available space
changes. Positional placements are a narrow escape hatch for a known
platform-specific composition.

ToolbarRole describes the purpose of the toolbar content. Use it when the
role—browser, editor, or navigation stack—changes how the system should
compose the toolbar. ToolbarTitleMenu can expose common actions related to the
content represented by the navigation title; keep those actions available
elsewhere if they are core.

The toolbar(id:content:) form enables customization for eligible toolbar
content. Give customizable items stable IDs and preserve a sensible default.
The Apple documentation notes that iPadOS customization is limited to
secondary-action items; treat that as a target-specific behavior to verify in
the chosen SDK and device configuration.

Do not manually paint a page-wide background behind a system toolbar to
guarantee a particular Liquid Glass result. Prefer native toolbar appearance
and test system changes across OS releases.

## Search as a native surface

Search is a stateful input route, not a decorative magnifying-glass button.
Store the query in app state and apply searchable to a NavigationStack,
NavigationSplitView, or the view within the column whose content the query
represents. Structural placement can be more robust than guessing a
coordinate.

SwiftUI supports:

- automatic or explicit SearchFieldPlacement;
- text-only search;
- tokens and editable tokens;
- suggested tokens and text suggestions;
- search completion;
- scopes that divide a broad search space;
- isSearching and dismissSearch;
- programmatic presentation with the isPresented overloads.

Search state should include:

    inactive
      -> active query
      -> suggestions or tokens
      -> filtered/local results
      -> async results
      -> empty/error/canceled

Keep search results derived from the query and selected scope. Do not mutate
the source collection just to filter the view. For async or AI-assisted
search, capture the query revision, cancel stale work, and keep a deterministic
local/manual search route.

On iOS, search can be a dedicated tab, a top/bottom toolbar item, or inline
with content. Choose based on whether discovery, rapid retrieval, or content
visibility is the priority. On iPadOS and Mac, a sidebar or toolbar search
often preserves the list/detail context. The HIG’s current search guidance
describes these placements as distinct patterns, not interchangeable
decorations.

When search is a tab, define activation behavior and return-to-previous-tab
behavior explicitly. If the keyboard opens immediately, test whether that is
helpful on the target device and input method.

## TabView, TabSection, and customization

Use TabView for top-level peer destinations. Give tabs stable selection values,
concise labels, and symbols that remain recognizable when labels are hidden.
Each tab should preserve its own nested navigation state where the product
needs that behavior.

TabSection adds secondary hierarchy inside a tab view. The sidebarAdaptable
style can represent the hierarchy differently on iPadOS, iOS, macOS, tvOS,
and visionOS. Treat those platform representations as the point of the API:
do not build a fake custom sidebar just to control the pixels.

For an adaptable tab surface, define:

| Contract | Rule |
| --- | --- |
| Selection | Stable Hashable/Identifiable value |
| Identity | Stable customizationID for customizable tabs/sections |
| Default | Small, understandable default set |
| Customization | Hide/reorder only nonessential content where appropriate |
| Persistence | AppStorage or SceneStorage only when the scope is correct |
| Deep link | Select tab, validate record, then route nested path |
| Deletion | Remove or redirect stale selections truthfully |
| Accessibility | Tab names, selected state, and order work under VoiceOver |

TabViewCustomization stores a person’s changes to an adaptable sidebar tab
view. Use tabViewCustomization with a binding only on a style that supports
customization. Attach customization IDs to each tab or section that
participates. Mark essential tabs non-customizable with the documented
customization behavior. If the default section order changes in a later
release, define the migration/reset rule rather than silently invalidating
stored customization.

Use default visibility deliberately. Too many tabs make a system surface
harder to scan even when the framework can scroll or collapse them.

## Bottom accessories and minimization

tabViewBottomAccessory is a narrow route for a related status or compact
control above the tab bar when it is at normal size, and inline when the bar
collapses on iPhone. Read tabViewBottomAccessoryPlacement to adapt the content
to that placement. The isEnabled overload is useful when the accessory truly
does not exist in a given feature state.

Good bottom accessories:

- a compact now-playing or recording status;
- a resumable task with one clear action;
- a transient but useful sync/capture/model status;
- a small context-preserving control related to the selected tab.

Poor bottom accessories:

- a second tab bar;
- a dense form;
- a permanent dashboard competing with the selected tab;
- a hidden core action that no other route exposes.

Tab bar minimization should improve the content task and remain reversible.
Test the accessory in normal, collapsed, disabled, empty, long-text, reduced
transparency, and VoiceOver states. A collapsed accessory is a different
layout contract, not merely a smaller frame.

## Liquid Glass functional-layer composition

Apple’s Liquid Glass guidance separates the functional layer—navigation,
controls, toolbars, tabs, and compact floating actions—from the content layer.
The correct order is:

    content remains legible
      -> system surfaces carry navigation/actions
      -> custom glass groups emphasize a small functional cluster
      -> semantic controls retain labels, focus, and actions

Use system-provided treatment for system bars, toolbar items, tabs, menus, and
controls. Add custom glass only when it clarifies a compact action or status
relationship. Do not wrap every card, text block, and background in a glass
effect.

For a custom group:

1. keep native Button, Toggle, Menu, or Label semantics;
2. use stable identity for stateful transitions;
3. keep clear glass over a tested rich background only when it helps;
4. use regular or standard-material/opaque fallback for dense text;
5. honor Reduce Transparency, Increase Contrast, and Reduce Motion;
6. make the same task available without the visual effect;
7. inspect the accessibility tree for duplicate decorative layers.

Glass is an appearance boundary. It does not create a control, a permission,
an AI result, a saved record, or proof of a system appearance contract.

## Evidence boundary

Separate evidence by what it can prove:

| Evidence | Can establish | Cannot establish |
| --- | --- | --- |
| Source review | API/design rationale | Target compiles |
| Named-target compile | Symbol signatures and availability | Correct hierarchy or device behavior |
| Preview | State/layout fixture | Real keyboard, VoiceOver, tab customization |
| UI automation | Queries, values, enabled state, routes | Ergonomics and physical assistive technology |
| Accessibility audit/Inspector | Exposed semantics and detectable issues | Complete human task |
| Physical device | Touch, keyboard, VoiceOver, Voice Control, Switch Control, adaptation | App Store/release configuration |
| Signed/system run | App Intent, control, deep-link, entitlement, production-like behavior | Universal UX quality |

Treat Liquid Glass screenshots as visual evidence only. Treat a successful
AI callback as a proposal/request result only until the domain commit is
verified.

## Sources

- [Button](https://developer.apple.com/documentation/swiftui/button)
- [ButtonStyle](https://developer.apple.com/documentation/swiftui/buttonstyle)
- [buttonStyle(_:)](https://developer.apple.com/documentation/swiftui/view/buttonstyle%28_%3A%29)
- [ToggleStyle](https://developer.apple.com/documentation/swiftui/togglestyle)
- [LabelStyle](https://developer.apple.com/documentation/swiftui/labelstyle)
- [Label](https://developer.apple.com/documentation/swiftui/label)
- [ControlGroup](https://developer.apple.com/documentation/swiftui/controlgroup)
- [Controls and indicators](https://developer.apple.com/documentation/swiftui/controls-and-indicators)
- [Form](https://developer.apple.com/documentation/swiftui/form)
- [TextField](https://developer.apple.com/documentation/swiftui/textfield)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [Menus and commands](https://developer.apple.com/documentation/swiftui/menus-and-commands)
- [Menu](https://developer.apple.com/documentation/swiftui/menu)
- [Commands](https://developer.apple.com/documentation/swiftui/commands)
- [KeyboardShortcut](https://developer.apple.com/documentation/swiftui/keyboardshortcut)
- [ToolbarItemPlacement](https://developer.apple.com/documentation/swiftui/toolbaritemplacement)
- [ToolbarRole](https://developer.apple.com/documentation/swiftui/toolbarrole)
- [toolbar(id:content:)](https://developer.apple.com/documentation/swiftui/view/toolbar%28id%3Acontent%3A%29)
- [ToolbarTitleMenu](https://developer.apple.com/documentation/swiftui/toolbartitlemenu)
- [Adding a search interface to your app](https://developer.apple.com/documentation/swiftui/adding-a-search-interface-to-your-app)
- [Search](https://developer.apple.com/documentation/swiftui/search)
- [Performing a search operation](https://developer.apple.com/documentation/swiftui/performing-a-search-operation)
- [TabView](https://developer.apple.com/documentation/swiftui/tabview)
- [TabSection](https://developer.apple.com/documentation/swiftui/tabsection)
- [TabViewStyle](https://developer.apple.com/documentation/swiftui/tabviewstyle)
- [SidebarAdaptableTabViewStyle](https://developer.apple.com/documentation/swiftui/sidebaradaptabletabviewstyle)
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
- [Human Interface Guidelines: Entering data](https://developer.apple.com/design/human-interface-guidelines/entering-data)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
