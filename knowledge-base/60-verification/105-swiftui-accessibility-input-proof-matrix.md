# SwiftUI accessibility and alternate-input proof matrix

## Purpose

Use this matrix to prove that an accessibility and alternate-input contract
works as a user task. It separates source/compile evidence, UI automation,
Accessibility Inspector evidence, physical assistive-technology runs, and
visual adaptation evidence.

A label query, screenshot, preview, or successful button callback is useful
evidence, but it does not prove the full task. Record build, SDK, OS, device,
appearance, accessibility settings, input method, fixture, and observed result
for every meaningful run.

Related pages:

- [SwiftUI accessibility and alternate input](../42-framework-deep-dives/80-swiftui-accessibility-and-alternate-input.md)
- [Accessibility and alternate-input design](../21-design-deep-dives/108-accessibility-and-alternate-input-design.md)
- [SwiftUI accessibility and input route](../50-capability-recipes/111-swiftui-accessibility-input-route.md)
- [SwiftUI accessibility and input recipes](../70-code-recipes/123-swiftui-accessibility-input-recipes.md)
- [Focus and alternate-input proof matrix](14-focus-and-alternate-input-proof-matrix.md)

## Evidence levels

| Level | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| A0 | Task and semantic contract | The user outcome, labels, values, actions, focus, and adaptation are defined | API correctness or runtime behavior |
| A1 | Official-source and SDK review | The chosen APIs and design constraints have primary-source support | The target compiles or behaves correctly |
| A2 | Named-target compile | The selected SwiftUI/App Intents/Transferable symbols build for the target | Assistive technology task completion |
| A3 | Preview and fixture matrix | Large text, light/dark, empty/error/loading/proposal states render | Physical VoiceOver, speech, switch, pointer, or system proof |
| A4 | UI automation and accessibility audit | Elements, labels, values, identifiers, actions, hit regions, contrast, Dynamic Type, and clipping issues are detectable | A human can complete the task with VoiceOver or Switch Control |
| A5 | Accessibility Inspector | Hierarchy, attributes, actions, order, contrast, and system setting responses are inspectable | Every device, localization, or physical gesture |
| A6 | Physical assistive-technology run | VoiceOver, Voice Control, Switch Control, Assistive Access, and real input can complete the task | App Store, every device, or future OS |
| A7 | Device adaptation run | Keyboard, pointer, hover, drag/drop, Dynamic Type, reduced motion/transparency, and presentation behavior are usable | Release signing, public links, backend reliability |
| A8 | Signed/release run | The shipped target contains the intended resources, entitlements, intents, and capabilities | Real-world accessibility quality without user-task evidence |

Apple’s accessibility testing guidance recommends identifying the main tasks
per screen and testing visual settings plus assistive technologies. Treat that
task matrix as the primary artifact, not a late checklist.

## Test fixture contract

Create stable fixtures for:

| Fixture | Required state |
| --- | --- |
| First launch | Onboarding or opt-out route |
| Empty | No records, clear primary action |
| Loaded | Several records with distinct labels and states |
| Long content | Long localized strings, large generated text |
| Editing | Multiple fields, keyboard visible, dirty draft |
| Invalid | Multiple errors with one first actionable error |
| Loading | Async/on-device AI generation with cancel |
| Proposal | Source, candidate, caveats, Accept/Edit/Reject |
| Refused/unavailable | No model/device capability, manual route |
| Stale/conflict | Source revision changed before commit |
| Saved | Durable result and next action |
| Failure | Recoverable error with preserved source |
| Empty rotor | No entries in custom semantic subset |
| Dynamic list | Filtering, pagination, deletion, insertion |
| Drag/drop | Valid, invalid, duplicate, and canceled payload |

For each fixture, define the expected spoken summary, focus target, primary
action, and recovery path.

## Semantic tree matrix

| Claim | Setup | Assertion | Evidence |
| --- | --- | --- | --- |
| Standard controls are discoverable | Native Button, Toggle, Picker, Slider, TextField | Label and role are correct without duplicate decorative elements | A4/A5 |
| Custom control has a concise name | Custom visual with accessibilityLabel | VoiceOver/Inspector reports a localized name and correct role | A5/A6 |
| State is not color-only | Selected/error/progress/saved fixtures | Value, symbol, text, or trait communicates state | A4/A5/A6 |
| Hint is useful | Action with a non-obvious result | Hint explains the result without giving gesture instructions | A5/A6 |
| Heading hierarchy works | Long screen with sections | Heading traits/order support navigation | A5/A6 |
| Grouping is intentional | Card with one action and card with three actions | Atomic card is concise; independent controls remain separate | A5/A6 |
| Decorative glass is quiet | Glass background, tint, shadow, icon layers | Decorative pieces do not create duplicate accessibility elements | A5 |
| Custom drawing is represented | Canvas/chart/visualization fixture | Synthetic children or chart descriptor expose meaningful content | A5/A6 |
| Identifier is not label | UI test identifiers added | Test query can use identifier while spoken label remains natural | A4/A5 |
| Wrapped UIKit/AppKit control is repaired | Representable or bridged control | Underlying accessible properties are present and correct | A5/A6 |

Use the inspector’s hierarchy and linear navigation view. A correct list of
identifiers does not prove that the order, role, value, or action is usable.

## VoiceOver and accessibility focus matrix

| Claim | Setup | Required assertion | Evidence |
| --- | --- | --- | --- |
| Initial focus is useful | Present a new screen or sheet | Heading/first task element is reachable and not buried under decoration | A6 |
| Invalid submit moves focus | Submit a form with multiple errors | First actionable error/field receives accessibility focus and remains visible | A6 |
| Proposal arrival is understandable | AI proposal enters review state | Focus moves once to heading/summary when appropriate; candidate is not announced as saved | A6 |
| Streaming does not steal focus | Generate incremental output | Focus remains stable while status/value updates are coalesced | A6/A7 |
| Focus target is mounted | Conditional view appears/disappears | Focus request succeeds only when target exists; no dead route | A6 |
| Dismissal restores context | Present and dismiss a task surface | Parent context remains understandable and return focus is sensible | A6/A7 |
| Accessibility focus is not selection | Move VoiceOver focus across a list | Domain selection does not change unless an explicit action is performed | A6 |
| Keyboard focus is separate | Focus a field and move VoiceOver focus | FocusState and AccessibilityFocusState represent their own systems | A6/A7 |

VoiceOver, Voice Control, Switch Control, and Assistive Access require a
physical-device run according to Apple’s accessibility testing documentation.
Simulator evidence is useful for layout and UI automation but is not a
replacement for this matrix.

## Rotor and linked-group matrix

| Claim | Setup | Required assertion | Evidence |
| --- | --- | --- | --- |
| Rotor appears | Screen with meaningful custom subset | User-visible rotor name is localized and discoverable | A6 |
| Entries are stable | Dynamic list with stable domain IDs | Each entry focuses the intended element after reload/filter | A6 |
| Off-screen content works | LazyVStack/List with distant entries | Rotor can reach the target without manual scrolling | A6 |
| Empty rotor is safe | No matching entries | Rotor is absent/empty without stale references or crash | A6 |
| Deletion is safe | Delete current rotor item | Entry disappears and next/previous navigation remains valid | A6 |
| Linked group is useful | Separated heading/status/actions | Related elements can be reached without confusing unrelated content | A6 |
| Rotor is not a hierarchy patch | Temporarily disable rotor | Default reading order is still understandable | A5/A6 |

Record the fixture, item ID, rotor label, expected sequence, and result. Do not
record only a screenshot of the rotor menu.

## Dynamic Type and visual-accessibility matrix

| Setting | Setup | Required assertion | Evidence |
| --- | --- | --- | --- |
| Large text | Dynamic Type accessibility5 or largest supported size | Text wraps, controls grow/reflow, no primary action is clipped | A3/A4/A6 |
| Long localization | Long labels and translated strings | Layout does not rely on English width or truncation | A3/A4/A7 |
| Bold Text/legibility | System setting enabled | Weight remains readable and hierarchy remains clear | A6/A7 |
| Increase Contrast | Setting enabled | Text, symbols, selected/disabled/error states remain distinct | A4/A5/A6 |
| Differentiate Without Color | Setting enabled | State has shape, glyph, text, or value in addition to color | A5/A6 |
| Reduce Transparency | Setting enabled | Custom glass/material becomes sufficiently solid and legible | A5/A6/A7 |
| Reduce Motion | Setting enabled | Morphing, zoom, depth, and large animations have a clear reduced route | A6/A7 |
| Cross-fade preference | Setting enabled where supported | Transition avoids unnecessary motion while preserving context | A6/A7 |
| Dim Flashing Lights | Setting enabled where relevant | UI/video behavior does not create distracting flashes | A6/A7 |
| Invert/colors | Display settings enabled | Core state and text remain understandable | A6/A7 |
| Large Content Viewer | Compact control fixture | Enlarged representation is useful but Dynamic Type still works where expected | A6/A7 |

Use system colors and text styles as a baseline, then inspect custom tints and
fonts. Accessibility Inspector can help detect text clipping and contrast
issues, but it does not replace the task run.

## Keyboard and Full Keyboard Access matrix

| Claim | Setup | Required assertion | Evidence |
| --- | --- | --- | --- |
| Form navigation works | Hardware keyboard, multi-field form | Tab/Full Keyboard Access reaches every required field and action | A7 |
| Invalid focus route works | Submit invalid form from keyboard | Focus moves to the same actionable error as the accessibility route | A7 |
| Shortcut is conventional | Custom shortcut plus standard system commands | Custom action does not steal an expected standard shortcut | A2/A7 |
| onKeyPress is scoped | Focused custom interaction | Matching key is handled only by owning view; other input continues | A2/A7 |
| Keyboard dismissal is safe | Editing and submit fixtures | Dismissing keyboard does not silently save or discard content | A7 |
| iPadOS controls remain conventional | iPad with keyboard/Full Keyboard Access | System navigation/activation remains available; custom loop is not required | A7 |
| Focus identity is unambiguous | Multiple fields and focus enum | No repeated focus case causes ambiguous programmatic focus | A2/A7 |

Record the hardware, keyboard layout, modifier keys, focused element, and
whether Full Keyboard Access or ordinary text editing was used.

## Pointer and hover matrix

| Claim | Setup | Required assertion | Evidence |
| --- | --- | --- | --- |
| Hover feedback is additive | iPad pointer or Mac Catalyst | Hover effect improves targeting without revealing the only action | A7 |
| Enter/exit state is stable | onHover fixture | Enter/exit does not trigger duplicate commands or stale state | A2/A7 |
| Continuous hover is scoped | Pointer coordinate fixture | Pointer movement updates only intended preview/feedback | A2/A7 |
| Focus and hover agree | Button/card with glass feedback | Focused/hovered state remains legible under contrast/transparency settings | A7 |
| Touch remains complete | Same screen without pointer | All core tasks are still visible and actionable | A6/A7 |
| Voice Control remains complete | Same screen with voice | Hover-only affordance is not required | A6 |

Test pointer behavior at different window sizes and in split view if the
feature supports iPadOS or Mac Catalyst. Record platform-specific differences
instead of assuming one pointer model everywhere.

## Drag and drop matrix

| Claim | Setup | Required assertion | Evidence |
| --- | --- | --- | --- |
| Payload is typed | Transferable source and destination | Expected representation is accepted and invalid types are rejected | A2/A7 |
| Privacy scope is intentional | Cross-app or internal drag | Only intended data representation leaves the source | A2/A7 |
| Preview is clear | Custom drag preview | Preview identifies the item without relying on tiny text or glass | A7 |
| Target feedback works | Valid/invalid target | Target state is visible and not color-only | A7 |
| Drop commit is correct | New, existing, duplicate, and invalid items | Domain action validates identity and writes exactly once | A7 |
| Cancel is safe | Start and cancel drag | No partial domain mutation or false success | A7 |
| Reorder has an alternative | List reorder fixture | Button/accessibility action or Edit route performs the same task | A6/A7 |
| Assistive drag points work | Custom geometry | Accessibility drag/drop point descriptions are correct if needed | A6/A7 |
| External transfer is safe | Another app or Files/Photos source | Import validates type, size, authorization, and content | A7 |

The drop callback proves receipt, not persistence. Record the domain revision or
resulting model state separately.

## Text input and App Intent matrix

| Claim | Setup | Required assertion | Evidence |
| --- | --- | --- | --- |
| Text field identity is clear | VoiceOver/Voice Control form | Prompt, label, value, and editing state are understandable | A5/A6 |
| Alternate input labels work | Custom icon/text control | Natural spoken name activates intended control | A6 |
| Form error is recoverable | Invalid values | Error is spoken/visible and field can be corrected | A6/A7 |
| App Intent is discoverable | App Shortcut/Shortcuts/Siri fixture | Title, phrase, parameters, and result describe the action | A2/A7 |
| Accessible action shares authority | Visible button plus accessibilityAction(intent:) | Both routes validate and commit through the same domain command | A2/A6/A7 |
| System route opens safely | OpenIntent/deep-link result | Current identity and authorization are rechecked before sensitive UI | A7/A8 |
| No AI is still usable | Model unavailable fixture | Manual input/action completes the user outcome | A6/A7 |

Do not call a Siri or App Intent result proof of in-app VoiceOver behavior.
Record them as separate system-surface evidence.

## Liquid Glass and motion proof

| Claim | Setup | Required assertion | Evidence |
| --- | --- | --- | --- |
| Glass is functional-layer scoped | Screen with content and controls | Glass separates navigation/action layer without washing all content | A3/A7 |
| Regular glass is legible | Text-heavy review/control surface | Source, status, and action text remain readable over light/dark content | A3/A5/A7 |
| Clear glass is justified | Rich media background | Background remains visible while text/actions pass contrast review | A3/A5/A7 |
| Reduced transparency works | System setting enabled | Surface becomes more solid or standard material and remains understandable | A6/A7 |
| Increased contrast works | System setting enabled | Boundaries and selected/disabled states are distinct | A5/A6/A7 |
| Reduced motion works | System setting enabled | Same task completes without essential morph/zoom/depth motion | A6/A7 |
| Glass does not own semantics | Accessibility Inspector | Glass layers are not duplicate controls and button owns the action | A5 |
| Effect count is reasonable | Maximum fixture | Instruments/hitches check shows no avoidable rendering degradation | A7 |

Use the current Liquid Glass APIs in the selected SDK. Do not use a custom
effect as evidence that a system component’s exact appearance is guaranteed
across releases.

## On-device AI review matrix

| State | User-task assertion | Accessibility assertion | Domain assertion |
| --- | --- | --- | --- |
| unavailable | Manual path is visible | Limitation is stated in plain language | No generation task starts |
| checking | Capability/permission check is understandable | Status is concise; focus is stable | Decision is recorded before request |
| generating | Progress/cancel route exists | No token-by-token focus or speech storm | Cancellation and request identity work |
| proposal | Source and candidate can be compared/edited | Candidate is not announced as saved | Typed candidate is uncommitted |
| refused | Source is preserved | Reason and recovery are accessible | No false success |
| applying | Scope and duplicate behavior are visible | Applying state is announced once or usefully | Authorization/revision validated |
| saved | Durable result and next action are visible | Saved status/value is clear | Persistence is authoritative |
| stale/conflict | User can refresh/review | Conflict is explained and actionable | Current revision wins |
| failed | User can retry or continue manually | Error is not only color/toast | No partial false commit |

Record model/profile, availability reason, input fixture, candidate ID,
source revision, user action, resulting revision, and whether the device or
network path was used.

## Accessibility Inspector and UI test evidence

Use Accessibility Inspector to inspect:

- label, value, role/traits, hint, and identifier;
- hierarchy and linear navigation order;
- custom actions and adjustable/scroll actions;
- hit region and clipped text;
- contrast and Dynamic Type issues;
- system accessibility setting responses.

UI automation can query XCUIElement attributes such as label, value,
identifier, element type, enabled/selected state, focus, and frame. Use those
queries to prove the exposed accessibility contract, not only internal view
identity.

Accessibility audits can cover categories such as:

- action;
- contrast;
- Dynamic Type;
- element detection;
- hit region;
- parent/child relationship;
- sufficient element description;
- text clipping;
- traits.

An audit issue that is manually waived needs a recorded reason and a separate
user-task test.

## Release and evidence packet

For a complete accessibility evidence packet, attach:

    task list
    semantic map
    selected SDK/deployment target
    compile result
    preview fixtures
    UI test/audit output
    Accessibility Inspector notes
    physical VoiceOver/Voice Control/Switch Control run
    Dynamic Type/contrast/transparency/motion results
    keyboard/pointer/drag/drop run
    App Intent/system-surface result
    AI state and domain revision evidence
    device/OS/build identifiers
    known gaps and follow-up owner

Do not mark accessibility complete if only the code or a screenshot exists.
The task must be possible through the intended assistive technology, and the
record must identify what was and was not tested.

## Sources

- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [Inspecting the accessibility of the screens in your app](https://developer.apple.com/documentation/accessibility/inspecting-the-accessibility-of-screens)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [XCUIAutomation](https://developer.apple.com/documentation/xcuiautomation)
- [XCUIElementAttributes](https://developer.apple.com/documentation/xcuiautomation/xcuielementattributes)
- [XCUIAccessibilityAuditType](https://developer.apple.com/documentation/xcuiautomation/xcuiaccessibilityaudittype)
- [XCUIApplication.performAccessibilityAudit(for:_:)](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication/performaccessibilityaudit%28for%3A_%3A%29)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)
- [Accessible navigation](https://developer.apple.com/documentation/swiftui/accessible-navigation)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [FocusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [Input events](https://developer.apple.com/documentation/swiftui/input-events/)
- [onKeyPress(_:action:)](https://developer.apple.com/documentation/swiftui/view/onkeypress%28_%3Aaction%3A%29)
- [HoverEffect](https://developer.apple.com/documentation/swiftui/hovereffect)
- [Adopting drag and drop using SwiftUI](https://developer.apple.com/documentation/swiftui/adopting-drag-and-drop-using-swiftui)
- [Making a view into a drag source](https://developer.apple.com/documentation/swiftui/making-a-view-into-a-drag-source)
- [draggable(_:)](https://developer.apple.com/documentation/swiftui/view/draggable%28_%3A%29)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityDifferentiateWithoutColor](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilitydifferentiatewithoutcolor)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [VoiceOver](https://developer.apple.com/design/human-interface-guidelines/voiceover)
- [Gestures](https://developer.apple.com/design/human-interface-guidelines/gestures)
- [Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)
- [Pointing devices](https://developer.apple.com/design/human-interface-guidelines/pointing-devices)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [App Intents](https://developer.apple.com/documentation/appintents)
