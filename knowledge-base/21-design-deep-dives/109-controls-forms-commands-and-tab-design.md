# Controls, forms, commands, and adaptable-tab design

## Design thesis

Apple-native polish is mostly a relationship between hierarchy, wording,
state, and adaptation. Liquid Glass can reinforce that relationship, but it
cannot replace it.

Use this loop:

    user goal
      -> content hierarchy
      -> semantic control
      -> adaptive placement
      -> input/assistive route
      -> state and recovery
      -> material and motion
      -> task proof

The visual question is not “Where can I add glass?” It is “Which functional
layer should remain available while the person reads, edits, searches, or
navigates the content below?”

## The Apple-native control hierarchy

### Level 1: direct task controls

Use a Button, Toggle, Picker, TextField, TextEditor, Slider, Stepper, or
DatePicker when the control’s purpose is direct and durable. Give it a
localized label that names the outcome rather than the implementation.

Examples:

- Save changes
- Add reminder
- Show completed
- Choose frequency
- Rewrite selection
- Search notes

Do not use “Magic,” “Smart,” or “AI” as the only action label. The person
needs to know what the action will try to do.

### Level 2: contextual groups

Use ControlGroup, Menu, a toolbar item group, or a context menu for related
secondary actions. Group by relationship, not by whichever actions happen to
fit inside the same capsule.

Good groups:

- text formatting;
- view mode;
- playback;
- share/export;
- sort and filter;
- proposal review actions.

If an action is destructive or commits an external side effect, do not make
its location in a compact group the only explanation of its consequence.

### Level 3: navigation and scene commands

Use TabView for peer areas, NavigationStack for hierarchy, a toolbar for
frequent commands/orientation, and Commands/keyboardShortcut for cross-input
access. A tab bar that contains “Delete,” “Save,” or “Generate” is carrying
the wrong design responsibility.

## Control styling that survives adaptation

Use the system style first. A custom ButtonStyle or ToggleStyle should make a
specific product distinction visible while preserving the native control’s
pressed, selected, disabled, role, focus, and accessibility behavior.

### Style checklist

| Check | Design decision |
| --- | --- |
| Label | Title and icon remain meaningful when the container changes |
| Role | Cancel/destructive intent is visible and semantically marked |
| State | Pressed/selected/loading/saved is not communicated by color alone |
| Size | Hit region remains comfortable at all supported sizes |
| Overflow | Toolbar/menu presentation still exposes a useful label |
| Input | Touch, pointer, keyboard, Voice Control, and VoiceOver reach the same action |
| Effects | Reduce Motion/Transparency leaves a clear state transition |
| Fallback | A failed or unavailable capability has an understandable route |

Label’s automatic, title-and-icon, title-only, and icon-only forms are useful
adaptation tools. An icon-only toolbar appearance does not mean the app should
remove the title from the accessibility tree.

For a toggle, describe the choice and expose its current value. Avoid a
custom “button” that internally flips a Boolean but looks identical in both
states.

## Form design for focused editing

A form is a promise that the person can finish a bounded task. It needs:

1. a clear entry reason;
2. a draft boundary;
3. field labels and formats;
4. immediate, local errors;
5. an explicit commit action;
6. a recoverable failure path;
7. a predictable dismissal rule.

### Layout rhythm

Keep labels close to fields and errors close to the value they explain. Let
Form and Section supply platform grouping unless the product has a documented
reason for a custom scroll rhythm. Use semantic text styles and scalable
metrics. Avoid a dense panel of translucent cards behind every field.

At larger text sizes, prefer:

    compact horizontal row
      -> wrapped row
      -> vertical field stack

The primary action must remain discoverable when the sheet is short, the
keyboard is visible, or the Dynamic Type size is large.

### Validation language

Use errors that tell the person what to do:

- “Enter a title.”
- “Use an email address such as name@example.com.”
- “This item changed elsewhere. Review the latest version.”
- “The on-device language model is unavailable. You can continue manually.”

Do not label a candidate model output “Saved” before the commit succeeds. Use
“Suggested,” “Draft,” “Review,” or another honest state.

### AI review editor

An AI-assisted form should look like an editor with an optional assistant,
not like a system that silently owns the form:

    source
      -> user invokes Suggest/Extract/Rewrite
      -> candidate appears with provenance
      -> user edits or accepts
      -> deterministic validation
      -> explicit commit

Give the candidate a visible boundary and keep the source available for
comparison. Provide Cancel during generation, Reject for a candidate, and a
manual path when the device capability or language asset is unavailable.

## Toolbars, menus, and commands

### Toolbar hierarchy

A toolbar should answer:

- Where am I?
- How do I go back or close?
- What is the primary action on this content?
- Where is search?
- Where are the secondary commands?

Use a small set of high-value items. Put secondary commands in a Menu with
predictable labels. Use ToolbarItemPlacement intent values before exact
positional placement. If a toolbar can customize items, give the items stable
IDs and preserve a useful default.

The title is a navigation/orientation element. A toolbar title menu can host
content-related actions, but those actions should still have an obvious route
if they are essential.

### Menu hierarchy

Menu labels should use verbs for actions and clear state language for
toggles. Put common actions first and destructive actions last. Keep nested
menus to one level where possible. Use icons consistently within a group.

Do not hide a primary action only in a context menu. Context menus are
discoverable through long press or secondary input, so any important task
needs a visible or system-routed alternative.

### Commands are not a second app

Commands, keyboard shortcuts, buttons, toolbar items, and App Intents should
converge on the same action authority:

    Button / Menu / Shortcut / App Intent
                    |
                    v
             typed domain command
                    |
                    v
          validation, authorization, commit

FocusedValues can supply the current document or selection to a command
surface. If no document is focused, the command should be disabled or explain
why it is unavailable. It should not guess at a target.

For on-device AI, use command names that explain the result:

| Weak | Better |
| --- | --- |
| AI | Summarize selection |
| Smart edit | Rewrite in a shorter tone |
| Generate | Suggest three titles |
| Fix | Review detected fields |

## Search design

Choose the search pattern based on the task:

| Task | Pattern |
| --- | --- |
| Fast retrieval while preserving context | Toolbar search |
| Filter a sidebar/list | Sidebar search |
| Rich discovery and suggestions | Search tab with landing content |
| Small local collection | Inline searchable content |

Search as a tab can either provide a landing page or immediately focus the
field. Use the landing pattern when suggestions/categories help discovery.
Use immediate focus when the person is trying to retrieve something quickly.
Test virtual keyboard behavior on iPad; an automatic keyboard can cover the
very content needed to orient.

Use searchable’s query, tokens, suggestions, scopes, isSearching, and
dismissal state as a coherent contract. Empty results should explain the
query or offer a next action. Do not show an AI-generated answer without
indicating whether it is a local indexed result, a generated interpretation,
or an app-owned record.

### Search result hierarchy

1. show the query and active scope;
2. show deterministic local results when available;
3. show suggestions as suggestions;
4. show generated summaries in a labeled review surface;
5. preserve the source result and route to the underlying record.

## Adaptable tabs

Tabs are stable destinations, not a carousel of every feature. Start with a
small set of top-level peer areas. Use concise labels and familiar symbols.
Preserve each destination’s navigation state when returning to it.

### Tab decision table

| Need | Choose |
| --- | --- |
| Four or five peer destinations on iPhone | TabView |
| More sections plus hierarchy on iPad | sidebarAdaptable with TabSection |
| A temporary filter | Toolbar/Menu/search scope |
| A single primary action | Toolbar/Button |
| A content pager | Page-style TabView only when pages are the task |
| A large catalog | Navigation/search/browse hierarchy, not dozens of tabs |

If the tab set changes by window size, make the mapping explicit and preserve
the selected semantic destination. A compact “Browse” tab can represent
secondary regular-width sections, but the deep-link and back behavior must
remain understandable.

### Customization contract

Tab customization should be a benefit, not a chore. Give the person:

- a sensible default order;
- stable customization IDs;
- a way to hide nonessential tabs;
- protection for essential destinations;
- persistence at the right scope;
- a reset path when the product changes the hierarchy.

When a tab is hidden, deep links and App Intent opens still need to select or
temporarily reveal the destination according to the product’s policy. Never
report that an item is unavailable merely because the person customized the
tab bar.

## Bottom accessories

A tab bottom accessory is a contextual bridge between the selected area and a
small ongoing state. It should be:

- compact;
- related to the current task;
- understandable when inline;
- dismissible or naturally absent;
- safe when the tab bar collapses.

Examples include a mini-player, recording state, upload progress, or a
single “Resume review” action. Avoid using it for a second navigation layer or
a dense collection of AI controls.

Design both states:

    normal tab bar: accessory above the bar
    collapsed tab bar: accessory inline with the tab surface

The content may need a different label, layout, or action density in those
placements. Inspect the placement environment value instead of using a
screen-size guess.

## Liquid Glass design rules for functional surfaces

### Layer the screen

    content layer: records, media, editor text, results
    functional layer: navigation, toolbar, tabs, compact actions/status
    system layer: keyboard, sheets, alerts, permissions, system pickers

Keep the content layer visually strong enough to read without glass. Let
standard SwiftUI and system surfaces provide the current Liquid Glass
treatment. A custom glass group should make one relationship clearer, such as
“these are transport controls” or “this is the current review status.”

### Glass review checklist

- Is the group functional rather than decorative?
- Does the group contain native semantic controls?
- Does regular versus clear make a meaningful readability difference?
- Does Reduce Transparency produce an understandable solid/material fallback?
- Does Increase Contrast preserve boundaries and state?
- Does Reduce Motion remove essential morphing while keeping the task?
- Does the group remain legible behind changing content and scrolling?
- Does the accessibility tree omit decorative glass layers?
- Does the effect stay performant on representative hardware?

Avoid page-wide glass backgrounds, fake system bars, and “Apple replica”
copying that removes product identity. Use native hierarchy, spacing, symbols,
typography, control behavior, and adaptation to achieve the feel.

## Accessibility and alternate input

Every visual control needs:

- a visible or spoken label;
- a meaningful role;
- a state/value when applicable;
- a target reachable at large text and with pointer/keyboard;
- an equivalent action route;
- a recovery result that is announced or visible.

Test tab selection, toolbar/menu order, search activation, form errors,
bottom-accessory collapse, and AI proposal arrival with VoiceOver. Test
Voice Control naming and Switch Control scanning on a physical device. Test
hardware keyboard and Full Keyboard Access on iPad when supported.

Do not allow a glass glow, hover state, red tint, or animated transition to be
the only indicator of selection, failure, generation, or saved state.

## Design review worksheet

Before implementation, answer:

| Decision | Answer |
| --- | --- |
| Primary task |  |
| Primary semantic control |  |
| Secondary command group |  |
| Toolbar role and placements |  |
| Search pattern and scope |  |
| Tab destinations and stable IDs |  |
| Accessory state and collapse behavior |  |
| AI proposal boundary |  |
| Manual/offline route |  |
| Large text fallback |  |
| Reduced-effects fallback |  |
| Physical-device proof task |  |

## Sources

- [Human Interface Guidelines: Controls](https://developer.apple.com/design/human-interface-guidelines/controls)
- [Human Interface Guidelines: Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)
- [Human Interface Guidelines: Menus](https://developer.apple.com/design/human-interface-guidelines/menus)
- [Human Interface Guidelines: Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- [Human Interface Guidelines: Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars)
- [Human Interface Guidelines: Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)
- [Human Interface Guidelines: Entering data](https://developer.apple.com/design/human-interface-guidelines/entering-data)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Button](https://developer.apple.com/documentation/swiftui/button)
- [ButtonStyle](https://developer.apple.com/documentation/swiftui/buttonstyle)
- [ToggleStyle](https://developer.apple.com/documentation/swiftui/togglestyle)
- [LabelStyle](https://developer.apple.com/documentation/swiftui/labelstyle)
- [ControlGroup](https://developer.apple.com/documentation/swiftui/controlgroup)
- [Form](https://developer.apple.com/documentation/swiftui/form)
- [Menus and commands](https://developer.apple.com/documentation/swiftui/menus-and-commands)
- [Commands](https://developer.apple.com/documentation/swiftui/commands)
- [FocusedValues](https://developer.apple.com/documentation/swiftui/focusedvalues)
- [KeyboardShortcut](https://developer.apple.com/documentation/swiftui/keyboardshortcut)
- [ToolbarItemPlacement](https://developer.apple.com/documentation/swiftui/toolbaritemplacement)
- [ToolbarRole](https://developer.apple.com/documentation/swiftui/toolbarrole)
- [ToolbarTitleMenu](https://developer.apple.com/documentation/swiftui/toolbartitlemenu)
- [Adding a search interface to your app](https://developer.apple.com/documentation/swiftui/adding-a-search-interface-to-your-app)
- [Search](https://developer.apple.com/documentation/swiftui/search)
- [TabView](https://developer.apple.com/documentation/swiftui/tabview)
- [TabSection](https://developer.apple.com/documentation/swiftui/tabsection)
- [TabViewCustomization](https://developer.apple.com/documentation/swiftui/tabviewcustomization)
- [tabViewBottomAccessory(content:)](https://developer.apple.com/documentation/swiftui/view/tabviewbottomaccessory%28content%3A%29)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
