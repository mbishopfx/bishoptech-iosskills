# SwiftUI controls, commands, and adaptable-tabs proof matrix

## Purpose

Use this matrix when an app claims native SwiftUI controls, forms, toolbars,
menus, commands, search, adaptable tabs, bottom accessories, Liquid Glass
composition, or on-device AI actions. It separates compile evidence from
visual evidence, semantic accessibility evidence, physical-input evidence,
system-surface evidence, and release evidence.

A screenshot can show that a screen rendered. It cannot prove that a command
has the right focused document, that a tab customization persists, that a
VoiceOver user can complete a form, or that an AI proposal became the intended
domain record.

## Evidence levels

| Level | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| P0 | Outcome/state contract | Task, state machine, recovery, and ownership are defined | API availability |
| P1 | Official source review | API/design choice has Apple/Swift support | Target compiles |
| P2 | Named-target compile | Signatures, generics, availability, target membership | Runtime system behavior |
| P3 | Preview/fixture matrix | Layout states and visual adaptation are inspectable | Physical input or system delivery |
| P4 | Unit/model tests | Validation, search filtering, selection mapping, command state, revision rules | SwiftUI hierarchy |
| P5 | UI automation | Semantic queries, labels/values, enabled/selected state, routes | Human assistive-technology ergonomics |
| P6 | Accessibility Inspector/audit | Hierarchy, attributes, hit regions, contrast/clipping diagnostics | Complete human task in every locale |
| P7 | Physical device | Touch, keyboard, pointer, VoiceOver, Voice Control, Switch Control, haptics/effects | App Store distribution |
| P8 | Signed system run | App Intent, deep link, tab/customization, entitlement, production-like behavior | Universal UX quality or backend reliability |
| P9 | Release/TestFlight/App Store | Archive identity, resources, privacy, entitlements, processed build | Future OS behavior or user success |

Record the Xcode version, SDK, deployment target, device/OS, build
configuration, appearance, accessibility settings, locale, input method,
fixture, action, expected result, observed result, and artifact path.

## Fixture contract

Create stable fixtures for every surface:

| Fixture | Required setup |
| --- | --- |
| Empty | No records, visible primary action, no stale tabs |
| Loaded | Several records with distinct labels, selection, and states |
| Long text | Largest supported Dynamic Type plus long localized labels |
| Editing | Dirty draft, keyboard visible, focus in a field |
| Invalid | Multiple invalid fields, one first actionable error |
| Saving | Duplicate-tap attempt, progress, cancel policy |
| Saved | Durable result and next action |
| Failed | Preserved draft/source and retry/manual route |
| Unavailable | Missing permission, model, language asset, or external service |
| Proposal | Source, generated candidate, provenance/caveat, Accept/Edit/Reject |
| Stale | Source revision changes before Apply |
| Search empty | Query/scope/tokens with no results and a recovery route |
| Search loaded | Local results, suggestions, token, scope, async cancellation |
| Tab customized | Hidden/reordered tabs, persisted customization, reset path |
| Tab deep link | Hidden destination opened by URL/App Intent |
| Accessory normal | Bottom accessory above normal tab bar |
| Accessory collapsed | Accessory inline with collapsed tab bar |
| Menu overflow | Toolbar items moved or customized |

Each fixture needs an expected visible status, semantic label/value, focused
element, primary action, domain result, and recovery action.

## Semantic control matrix

| Claim | Setup | Assertion | Evidence |
| --- | --- | --- | --- |
| Button owns the action | Native Button with localized label | One accessible action invokes the domain command | P2/P5/P6/P7 |
| Button role is correct | Cancel and destructive fixtures | Role/appearance/confirmation match the action | P2/P5/P6/P7 |
| Label adapts | Toolbar, menu, compact, large text | Icon/title presentation changes without losing meaning | P3/P5/P6/P7 |
| Toggle exposes state | On/off fixture | State is spoken/visible without tint alone | P5/P6/P7 |
| Picker/Menu choices are clear | Single/multiple choice fixture | Current selection and available options are understandable | P5/P6/P7 |
| ControlGroup is related | Formatting/view/transport group | Group label and actions remain intelligible in overflow | P3/P5/P6/P7 |
| Custom style preserves behavior | ButtonStyle/ToggleStyle | Standard activation, disabled, pressed, selected, role, and focus routes work | P2/P5/P7 |
| Primitive style is justified | Custom interaction fixture | Raw interaction has equivalent keyboard/accessibility/domain routes | P2/P5/P7 |
| Hit target works | Small/large text/pointer fixtures | Target is comfortable and not occluded by system areas | P6/P7 |
| Disabled state is honest | Capability unavailable fixture | Reason/recovery is visible; no false action callback | P4/P5/P6/P7 |

Inspect the accessibility tree after applying label styles, group modifiers,
glass effects, and custom containers. A custom appearance that produces
duplicate nodes or loses the role is a regression even if the screenshot looks
correct.

## Form and validation matrix

| Claim | Setup | Assertion | Evidence |
| --- | --- | --- | --- |
| Draft is isolated | Edit existing record | Typing does not mutate committed state before Apply/Save | P4/P5 |
| Required errors are local | Empty required fields | Error is next to the field with actionable language | P3/P5/P6/P7 |
| First error is reachable | Multiple invalid fields | Keyboard/accessibility focus reaches the same first actionable error | P5/P7 |
| Draft survives failure | Permission/network/model failure | Entered text/source remains available | P4/P5/P7 |
| Duplicate save is safe | Rapid taps/keyboard repeat | Exactly one authorized commit or clear in-flight policy | P4/P5/P7 |
| Stale revision is safe | Change source before Apply | Candidate is rejected/reviewed against current revision | P4/P5/P7 |
| Sheet/detent is usable | Small/large detents, keyboard | Commit, error, and dismissal remain reachable | P3/P5/P7 |
| Dynamic Type reflows | Largest sizes/localized strings | No clipped field, error, or primary action | P3/P5/P6/P7 |
| Reduced transparency works | System setting enabled | Form text and controls remain legible on fallback surface | P6/P7 |
| Reduced motion works | System setting enabled | Focus/state changes remain understandable without essential motion | P7 |

Record the domain revision or resulting model state separately from the button
callback. A callback is not proof of persistence.

## Toolbar and menu matrix

| Claim | Setup | Assertion | Evidence |
| --- | --- | --- | --- |
| Toolbar hierarchy is deliberate | Navigation/title/primary/secondary fixture | Items answer orientation and frequent-action needs without crowding | P3/P7 |
| Semantic placement adapts | Compact and regular windows | Items remain reachable; overflow is understandable | P2/P3/P7 |
| Toolbar role helps | Browser/editor/navigation fixtures | Role-specific composition remains coherent | P2/P3/P7 |
| Toolbar customization is stable | Stable toolbar/item IDs | Default, customized, reset, and relaunch states are correct | P2/P4/P7/P8 |
| Menu labels are verbs | Menu and submenu fixture | Labels explain action/state and order is predictable | P3/P5/P6/P7 |
| Destructive action is protected | Delete/remove menu fixture | Action is last/marked and confirmation policy is correct | P5/P6/P7 |
| Context menu is supplemental | Item context fixture | Core task has visible/system route; context menu is relevant | P5/P7 |
| Overflow preserves meaning | Move actions to overflow | Labels/icons still identify the command | P3/P5/P6/P7 |
| Title menu is not the only route | ToolbarTitleMenu fixture | Essential action remains discoverable elsewhere | P3/P5/P7 |

Test with VoiceOver, Voice Control, Switch Control, touch, pointer, and
hardware keyboard. Test right-to-left layout and long localized labels.

## Commands and keyboard matrix

| Claim | Setup | Assertion | Evidence |
| --- | --- | --- | --- |
| Command has one authority | Button/menu/shortcut fixture | All routes call the same typed domain command | P4/P5 |
| Focused context is correct | Two documents/selections | Command applies only to the focused/selected context | P4/P5/P7 |
| Missing context is safe | No document/selection | Command is unavailable or explains why; no guessed mutation | P4/P5/P7 |
| Read-only state is safe | Read-only fixture | Save/edit commands are disabled or routed to a truthful alternative | P4/P5/P7 |
| Shortcut is conventional | Standard plus custom shortcuts | Standard editing/system shortcuts remain available | P2/P7 |
| Raw key route is scoped | Focused custom interaction | Only intended keys are handled; unrelated input continues | P2/P7 |
| Full Keyboard Access works | iPad keyboard and setting | Every required action is reachable without pointer/touch | P7 |
| Repeat/cancel is safe | Key repeat and Escape/cancel | No duplicate destructive/commit action; cancellation preserves source | P4/P7 |
| App Intent converges | App Intent plus in-app action | System route reaches the same validation/authorization/domain boundary | P2/P8 |

Record keyboard layout, modifiers, focus, selected document ID, and command
result. A unit test that calls the domain function directly does not prove the
command was enabled or routed correctly.

## Search matrix

| Claim | Setup | Assertion | Evidence |
| --- | --- | --- | --- |
| Placement matches task | Toolbar/sidebar/tab/inline fixtures | Search appears where the content relationship requires it | P2/P3/P7 |
| Query is source state | Type/delete/clear | Results derive from query and no stale query remains | P4/P5/P7 |
| Scope works | Multiple scopes | Scope changes result set and label/value is visible | P4/P5/P6/P7 |
| Tokens work | Known token/invalid token | Token state is typed, removable, and included in query semantics | P2/P4/P5/P7 |
| Suggestions are suggestions | Suggested terms/results | Selecting one completes/searches without pretending it is a saved record | P5/P7 |
| Async cancellation works | Slow query/model fixture | Stale response cannot overwrite a newer query | P4/P7 |
| Empty results recover | Unknown query | Person can clear/refine/query again and understands no-result state | P3/P5/P6/P7 |
| Search tab activation is honest | Standard/button appearance | Keyboard/focus/return-to-previous-tab behavior matches the choice | P3/P7 |
| AI search is labeled | Generated summary fixture | Generated content has source/review boundary and manual search remains available | P5/P7 |

On iPad, test whether automatic field focus and the virtual keyboard obscure
the context needed to begin searching. On split views, verify the search field
filters the intended column.

## Tab and customization matrix

| Claim | Setup | Assertion | Evidence |
| --- | --- | --- | --- |
| Tabs are peer destinations | Four/five top-level fixture | Tab bar is navigation, not an action list | P3/P7 |
| Selection is stable | Relaunch and deep link | Correct tab and nested path restore/select | P4/P5/P8 |
| TabSection hierarchy is clear | Regular/compact fixtures | Secondary tabs remain understandable in each representation | P3/P7 |
| Sidebar adaptation works | iPad regular/compact, Mac/visionOS if supported | Tab/sidebar/ornament representation is usable | P2/P3/P7 |
| Customization persists | Hide/reorder/relaunch fixture | User changes persist at the intended AppStorage/SceneStorage scope | P4/P7/P8 |
| Essential tabs are protected | Disabled customization behavior | Core destination cannot be removed accidentally | P2/P7 |
| Reset/migration works | Changed default order | Existing customization is handled intentionally | P4/P7/P8 |
| Hidden deep link is truthful | Hidden destination URL/App Intent | App selects/reveals/resolves destination according to policy | P4/P7/P8 |
| VoiceOver sees tab state | VoiceOver tab fixture | Label, selected state, order, and return context are understandable | P6/P7 |
| Too many tabs are avoided | Large tab set | Compact representation remains scannable and reachable | P3/P7 |

Do not claim a tab is “available everywhere” from one iPhone run. Record the
device family and supported representations.

## Bottom accessory matrix

| Claim | Setup | Assertion | Evidence |
| --- | --- | --- | --- |
| Accessory is contextual | Mini-player/status/resume fixture | It relates to selected tab without duplicating navigation | P3/P5/P7 |
| Normal placement works | Normal tab bar | Content inset and action hit regions are correct | P3/P7 |
| Collapsed placement works | Scroll/collapse fixture | Accessory adapts inline without clipped text or confusing hierarchy | P3/P7 |
| Placement environment is used | Different placement fixtures | Layout/label density changes from placement, not a guess | P2/P3/P7 |
| Enable/disable is safe | Absent/visible/completed | No stale empty slot, focus target, or false status remains | P4/P5/P6/P7 |
| Accessibility is stable | VoiceOver in both placements | Accessory order/label/action is understandable | P6/P7 |
| Core task has another route | Accessory action fixture | Screen/toolbar/system route remains available | P5/P7/P8 |

## Liquid Glass and visual-adaptation matrix

| Claim | Setup | Assertion | Evidence |
| --- | --- | --- | --- |
| Functional layer is scoped | Content plus toolbar/tab/custom group | Glass supports navigation/actions without washing the content | P3/P7 |
| Native semantics remain | Button/Toggle/Menu in glass shell | Accessibility tree exposes the control, not duplicate decoration | P5/P6/P7 |
| Regular glass is legible | Dense text/status fixture | Text, icons, focus, and error remain readable | P3/P6/P7 |
| Clear glass is justified | Rich changing background | Content remains visible and contrast remains acceptable | P3/P6/P7 |
| Reduced transparency works | System setting | Surface becomes more solid/standard and task remains complete | P7 |
| Increased contrast works | System setting | Boundaries/selected/disabled/error states remain distinct | P6/P7 |
| Reduced motion works | System setting | Morphing/zoom/depth is reduced while state transition remains clear | P7 |
| Dynamic Type works | Largest sizes/localized strings | Glass group expands/reflows without clipping | P3/P6/P7 |
| Performance is acceptable | Representative hardware/release build | No avoidable hitch/energy/rendering regression | P7/P9 |

A design-system screenshot is not proof of a particular system Liquid Glass
implementation. Record the OS and SDK, and treat appearance as versioned
evidence.

## On-device AI action matrix

| State | Visible assertion | Semantic assertion | Domain assertion |
| --- | --- | --- | --- |
| Unavailable | Manual route and plain-language limitation | Status is discoverable | No model request |
| Checking | Capability/language asset state | Focus remains stable | Request not yet committed |
| Generating | Progress and Cancel | No token-by-token focus/speech storm | Request ID/cancellation works |
| Proposal | Source/candidate/caveat and review actions | Candidate is not announced as saved | Candidate uncommitted |
| Applying | Scope and duplicate policy | Applying status is understandable | Revision/authorization checked |
| Saved | Durable result and next action | Saved value/status is clear | Store/revision changed correctly |
| Stale | Conflict and refresh/review route | Conflict is actionable | Current source wins |
| Refused/failed | Reason/retry/manual route | Error is not color/toast-only | No partial false commit |

Record the device/model availability reason, source revision, candidate ID,
user approval, resulting revision, and whether the request used an on-device
or other path. Never treat “the model returned text” as “the app saved truth.”

## Physical-device task scripts

### Form script

1. Open the editor from the visible route.
2. Enter a valid value with touch and keyboard.
3. Submit with the primary action and the standard shortcut if supported.
4. Submit invalid values and follow the first error with VoiceOver.
5. Enable Reduce Transparency and largest Dynamic Type.
6. Start a model suggestion, cancel it, retry, and accept a candidate.
7. Change the source revision before Apply and confirm stale recovery.
8. Verify the committed record/revision, not only the screen.

### Command/search script

1. Open two documents or selections.
2. Invoke the same command from button, menu, and shortcut.
3. Confirm the focused document is the only mutation target.
4. Search from the intended placement with a token and scope.
5. Type a slow query, replace it, and confirm stale results do not win.
6. Run Voice Control and Full Keyboard Access routes.

### Tab/accessory script

1. Select every top-level tab and verify nested path restoration.
2. Customize tab order/visibility on an adaptable surface.
3. Relaunch and reset customization.
4. Open a deep link to a hidden destination.
5. Collapse the tab bar and test the bottom accessory inline.
6. Run VoiceOver through normal and collapsed placements.
7. Repeat in the supported iPad compact/regular windows.

## Sources

- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [XCUIAutomation](https://developer.apple.com/documentation/xcuiautomation)
- [XCUIElementAttributes](https://developer.apple.com/documentation/xcuiautomation/xcuielementattributes)
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
- [Human Interface Guidelines: Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- [Human Interface Guidelines: Menus](https://developer.apple.com/design/human-interface-guidelines/menus)
- [Human Interface Guidelines: Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)
- [Human Interface Guidelines: Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Human Interface Guidelines: Entering data](https://developer.apple.com/design/human-interface-guidelines/entering-data)
