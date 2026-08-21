# SwiftUI accessibility and alternate input

## Purpose

Accessibility is not a finishing modifier pass. In a native SwiftUI feature,
the semantic tree, focus model, visual adaptation, and input routes are part
of the feature contract. A polished iOS 26 surface should remain understandable
when a person uses VoiceOver, Voice Control, Switch Control, Full Keyboard
Access, Dynamic Type, pointer input, reduced motion, increased contrast, or
reduced transparency.

This page turns Apple’s current SwiftUI accessibility collections and Human
Interface Guidelines into a buildable mental model. It is intentionally
specific about boundaries:

- standard SwiftUI controls already expose useful semantics;
- custom visuals need explicit semantics only where the default tree is
  incomplete or misleading;
- a visual Liquid Glass treatment is not a substitute for a label, value,
  trait, action, or focus route;
- a preview, simulator run, or accessibility identifier is not proof that a
  person can complete the task with an assistive technology;
- the selected Xcode/SDK and deployment target decide whether a symbol can be
  compiled for the app target.

Use this page with:

- [Accessibility and alternate-input design](../21-design-deep-dives/108-accessibility-and-alternate-input-design.md)
- [SwiftUI accessibility and input route](../50-capability-recipes/111-swiftui-accessibility-input-route.md)
- [SwiftUI accessibility and input proof matrix](../60-verification/105-swiftui-accessibility-input-proof-matrix.md)
- [SwiftUI accessibility and input recipes](../70-code-recipes/123-swiftui-accessibility-input-recipes.md)
- [SwiftUI animation, motion, transitions, and feedback](78-swiftui-animation-motion-transitions-and-feedback.md)
- [SwiftUI navigation transitions and presentation](79-swiftui-navigation-transitions-and-presentation.md)
- [Focus-first native input](../21-design-deep-dives/17-focus-first-native-input.md)

## The accessibility contract

Treat each important screen or task as four related graphs:

    visual hierarchy
      -> semantic accessibility tree
      -> focus/navigation order
      -> action/input routes

The graphs should describe the same task, but they do not need identical
shapes. A decorative glow may be hidden from assistive technologies. A
multi-part card may become one accessible element with a concise value. A
custom rotor may provide a shortcut to meaningful elements that are distant
in the visual or lazy layout. A keyboard shortcut can invoke the same domain
action as a button without creating a second business rule.

For every user-visible state, write down:

| Contract | Question |
| --- | --- |
| Perception | What must be visible, spoken, typed, or otherwise perceivable? |
| Identity | What is the element called, and what kind of element is it? |
| State | What value, selection, progress, error, or availability must be reported? |
| Action | What can the person do, and how can they do it without a custom gesture? |
| Focus | Where should keyboard or accessibility focus start after a meaningful state change? |
| Adaptation | What changes for Dynamic Type, contrast, transparency, motion, or pointer input? |
| Proof | Which device, setting, assistive technology, and task run demonstrates the contract? |

Do not treat all of these as labels. A label identifies an element; a value
describes state; a hint explains the result of an action; traits communicate
behavior; custom actions expose operations; focus state controls navigation.

## Start with native controls and semantic composition

SwiftUI introspects common elements such as navigation views, lists, text
fields, sliders, and buttons and provides basic accessibility information.
Start with those controls and their normal labels. Add modifiers when the
semantic output is incomplete, duplicated, ambiguous, or wrong.

Recommended order:

1. choose a standard control with the correct behavior;
2. give it a visible, localized title whenever possible;
3. inspect the resulting accessibility tree;
4. add a label, value, hint, heading, trait, custom content, action, or
   grouping modifier only for a specific observed gap;
5. repeat the task with VoiceOver, Voice Control, Switch Control, and keyboard
   input as appropriate.

Useful semantic tools include:

| Need | SwiftUI route | Design note |
| --- | --- | --- |
| Name a custom visual | accessibilityLabel | Keep it short and do not append the control type when the system supplies it |
| Report state | accessibilityValue | State should be current, localized, and useful without color |
| Explain the result | accessibilityHint | Say what activating the control does, not how to tap it |
| Describe hierarchy | accessibilityHeading | Apply to real section headings so rotor navigation has meaning |
| Communicate behavior | accessibilityAddTraits / accessibilityRemoveTraits | Do not combine mutually confusing roles |
| Add secondary facts | accessibilityCustomContent | Keep the primary announcement concise and put detail behind custom content |
| Add alternate spoken names | accessibilityInputLabels | Use words people may naturally say with Voice Control |
| Hide ornament | accessibilityHidden | Decorative glass, shadows, and duplicated icon layers should not become noise |
| Combine or reshape children | accessibilityElement(children:) / accessibilityChildren | Make the semantic element match the task, not the implementation tree |
| Expose an operation | accessibilityAction / accessibilityActions | Invoke the same domain command as the visible control |
| Control participation | accessibilityRespondsToUserInteraction | Use only when the default interaction inference is wrong |
| Test identity | accessibilityIdentifier | Stable test identity is not a spoken label |

Never use accessibilityIdentifier as a user-facing description. Never hide a
content-bearing view just because it is visually subtle. If a custom
UIViewRepresentable or other wrapped control does not expose useful labels,
values, or actions, repair the boundary rather than assuming the surrounding
SwiftUI view will infer them.

### Grouping and child behavior

The view tree and accessibility tree are different products. A card with a
thumbnail, title, status, and one primary action may be easiest to use as a
single element with a useful value and one action. A card with independent
favorite, share, and open controls should not be flattened into one ambiguous
announcement.

Use grouping deliberately:

- combine children when their parts form one atomic concept;
- keep independent controls separate;
- hide purely decorative images and background effects;
- replace a custom drawing’s children with synthetic accessibility elements
  when the drawn objects each matter;
- ensure a custom group does not swallow a control that must remain actionable;
- use sort priority sparingly and only when the natural reading order is
  genuinely wrong.

The accessibilityChildren route is especially useful when a custom chart,
canvas, or visualization has visual elements that do not exist as ordinary
SwiftUI children. Create synthetic entries that describe the data in a
stable order. For charts, use the chart accessibility descriptor APIs instead
of manually exposing every decorative mark when the chart type supports it.

## VoiceOver and accessibility focus

AccessibilityFocusState reads and writes the focus of an active accessibility
technology such as VoiceOver. Bind it with accessibilityFocused(_:), or with
the value-based overload, to identify the element that can receive focus.
Boolean state is useful for one element; an optional Hashable enum is safer for
several mutually exclusive destinations.

A meaningful focus transition has a cause:

    submit invalid form
      -> identify the first actionable error
      -> request accessibility focus
      -> keep the error visible and actionable

    open AI review
      -> present title/source/status
      -> focus a stable review heading or status
      -> let the person choose Accept, Edit, or Cancel

Good focus policy:

- request focus after a real state change, not on every body recomputation;
- focus the smallest element that explains the new context;
- do not steal focus while a person is reading or editing;
- use an optional value or Bool so absence of active accessibility focus is
  representable;
- keep the target mounted long enough for the system to focus it;
- make the target’s label/value meaningful even if the visual animation is
  removed;
- test focus after navigation, sheet presentation, validation, loading,
  failure, and dismissal.

AccessibilityDefaultFocus defines a region in which default accessibility focus
is evaluated. Use it for a new task surface when the initial reading position
would otherwise be unpredictable. It is not a command to repeatedly move
VoiceOver focus. The destination still needs a coherent accessibility order.

Accessibility focus is different from keyboard focus:

| Focus | State type | Main user | Typical route |
| --- | --- | --- | --- |
| Keyboard/input focus | FocusState | Hardware keyboard, Full Keyboard Access, text entry | focused(_:), focused(_:equals:), onKeyPress |
| Accessibility focus | AccessibilityFocusState | VoiceOver and other accessibility technologies | accessibilityFocused(_:), accessibilityDefaultFocus |
| Visual selection | Domain state | Every user | selected item, current tab, review phase |

Keep these states separate. A visible selection should not be changed merely
because VoiceOver moved to an element. A keyboard focus change should not
silently submit an AI request.

## Rotors and linked groups

An accessibility rotor is a shortcut to a meaningful subset of a screen.
SwiftUI can create a rotor from entries, assign explicit rotor-entry IDs, and
replace certain automatic system rotors. Apple specifically calls out rotors
for content that may be off screen, such as distant elements in a LazyVStack or
List.

Use a rotor when:

- the screen has repeated, high-value landmarks such as errors, headings,
  pending reviews, or unread items;
- a long list makes linear navigation unnecessarily slow;
- the system rotor cannot discover meaningful off-screen content;
- a data-rich view has a useful semantic subset that deserves direct access.

Rotor rules:

- label the rotor in the user’s language;
- give each entry a stable, concise label;
- attach an entry to the element that will actually receive focus;
- do not create a rotor for every visual category;
- preserve a useful default reading order;
- test the rotor after filtering, pagination, deletion, and empty states;
- make entries safe when the underlying item becomes unavailable.

AccessibilityLinkedGroup links multiple accessibility elements so a person can
move quickly between related elements even when they are not near one another
in the accessibility hierarchy. Use it for relationships such as a chart
legend and its distant data region, or a review heading and a status/action
cluster. It should strengthen an existing relationship, not compensate for a
confusing screen.

Stable IDs matter. Rotor and linked-group identity should come from the
domain item or a stable semantic role, not from array offsets or a new random
value on every render.

## Accessible actions and App Intents

Accessible actions are domain operations exposed through assistive
technologies. SwiftUI supports named actions, adjustable and scroll actions,
multiple action groups, and action overloads that invoke an App Intent.

Use one domain command for every route:

    visible Button
    accessibilityAction
    keyboardShortcut
    App Intent / App Shortcut
    widget or control
        -> the same authorization and domain operation

The accessible action should not call a private view mutation that bypasses
validation. A delete action must still validate identity and authorization. An
AI Accept action must still validate the candidate, current revision, and
write authority.

App Intents make app actions discoverable to Apple Intelligence, Siri,
Shortcuts, Spotlight, widgets, controls, and other system experiences.
Accessible controls can invoke an intent directly. This is useful when the
action needs the same localized title, parameters, validation, and result
handling across in-app and system entry points.

Keep the boundaries explicit:

- an App Intent is discoverability and invocation metadata plus executable
  action code;
- an accessibility label is the spoken identity of a visible element;
- an App Shortcut phrase is a system-level invocation phrase;
- a returned snippet is a system presentation, not proof of an in-app
  accessibility tree;
- a view action should remain available when Siri, Apple Intelligence, or a
  model is unavailable.

## Dynamic Type and readable layout

Dynamic Type is a system setting, and SwiftUI exposes the current
DynamicTypeSize through the environment. Use system text styles, scalable
metrics, and flexible layout before adding manual size branches.

The layout contract for large accessibility sizes:

- text can grow vertically;
- controls can grow without clipping labels;
- horizontal rows can reflow to a vertical stack;
- buttons remain discoverable and tappable;
- status and error text remains adjacent to the field or action it explains;
- sheets and review surfaces scroll instead of clipping primary actions;
- localization and right-to-left layout do not change the semantic order;
- custom fonts reproduce the legibility behavior expected from system text.

If a control must remain physically compact, the Large Content Viewer can
provide an enlarged representation. Apple explicitly positions it as a
solution for unavoidable small controls such as a tab bar, not as a
replacement for Dynamic Type.

Preview every important route with at least:

    .environment(\.dynamicTypeSize, .accessibility5)

Also test the real device setting because previews do not exercise every
keyboard, pointer, VoiceOver, presentation, or system integration behavior.

## Contrast, color, transparency, and Liquid Glass

Use system-defined colors when possible. They adapt to appearance and
accessibility contrast settings. Never communicate a state with color alone:
pair color with a symbol, shape, text, selection, or spoken value.

SwiftUI exposes system preferences including:

| Environment value | Required response |
| --- | --- |
| accessibilityDifferentiateWithoutColor | Add shapes, glyphs, patterns, or text so color is not the only state cue |
| accessibilityReduceTransparency | Make important custom surfaces opaque or materially more solid |
| accessibilityReduceMotion | Remove large/depth-like animation and choose a clear static or cross-fade route |
| accessibilityPrefersCrossFadeTransitions | Prefer cross-fade/low-motion transitions where the current SDK exposes the preference |
| accessibilityDimFlashingLights | Avoid UI flashing or communicate playback risk when relevant |
| accessibilityPlayAnimatedImages | Do not auto-play animated imagery when the preference is off |
| legibilityWeight | Preserve readable weight choices when the system requests stronger text |

Liquid Glass is adaptive. Standard SwiftUI components handle the current
system treatment automatically. Custom glass should stay limited to functional
surfaces such as navigation, controls, or a focused action group. Keep
content-layer backgrounds and semantic boundaries understandable when the
material becomes less translucent, higher contrast, or motion-reduced.

For a custom glass component:

1. use a standard control and system placement first;
2. choose regular for text-heavy or contrast-sensitive surfaces;
3. reserve clear for visually rich media backgrounds with a tested dimming
   strategy;
4. group related effects with GlassEffectContainer only when morphing helps;
5. test Reduce Transparency, Increase Contrast, Differentiate Without Color,
   Dark Mode, large text, VoiceOver, and Reduce Motion;
6. provide an opaque/standard-material fallback when the custom effect becomes
   illegible;
7. keep the accessibility element independent of the glass shape.

Do not infer that a glass shape is a button. The button or other semantic
control must own the label, traits, hit target, action, and focus behavior.

## Keyboard, focus, pointer, and hover

FocusState models keyboard/input focus. Use a single typed enum for fields and
other focusable regions when programmatic routing matters. Avoid binding the
same enum case to multiple views: the framework cannot choose an unambiguous
target.

For hardware keys:

- use keyboardShortcut for a command that should activate a control;
- use onKeyPress when a focused view needs raw key phases or a key-specific
  interaction;
- return handled only when the view owns the event;
- return ignored when normal system or parent dispatch should continue;
- respect standard shortcuts and Full Keyboard Access;
- keep a visible/button route for the same task.

On iPadOS, Apple’s HIG distinguishes text/sidebar keyboard navigation from
letting Full Keyboard Access handle ordinary control activation. Do not make
buttons, toggles, or segmented controls depend on a custom key loop when the
system route already provides the expected behavior.

Pointer and hover are progressive enhancements:

- hoverEffect communicates pointer/indirect focus;
- onHover reports enter/exit;
- onContinuousHover reports a pointer phase and location;
- isHoverEffectEnabled can gate custom visual behavior;
- hover should not be the only way to reveal a control or state;
- pointer visual feedback should not change the semantic label or action;
- pointer hit shapes and accessibility shapes should remain intentional.

The same action should be reachable by touch, Voice Control, Switch Control,
Full Keyboard Access, and a pointer where the platform supports it.

## Gestures, hit regions, and drag and drop

Apple’s HIG recommends more than one way to interact with an app. A swipe,
long press, drag, or custom gesture should have an onscreen control or
accessible action when it performs a core task.

Use contentShape with the correct ContentShapeKinds to separate:

- interaction/hit testing;
- accessibility visuals and sorting;
- hover preview;
- focus effect;
- drag preview.

Do not enlarge a visual shape accidentally and make a neighboring control
ambiguous. On iOS/iPadOS, the HIG lists 44x44 pt as the default control size
and 28x28 pt as the minimum target guidance. Treat spacing between controls as
part of the hit-target design.

Modern SwiftUI drag and drop uses Transferable values:

    source view
      -> draggable(transferable)
      -> system representation/preview
      -> dropDestination(for:action:isTargeted:)
      -> validate payload and destination
      -> commit domain change

The data representation is a security and product boundary. Prefer stable
identifiers or intentionally scoped data; do not export private generated
content merely because a view can be dragged.

For accessibility:

- expose the same move/copy/import operation as a named action when a gesture
  is not available;
- use accessibilityDragPoint and accessibilityDropPoint when custom geometry
  needs explicit assistive drag/drop locations;
- provide a text/button route for reordering;
- announce the resulting state through the updated value or focused result,
  not a decorative animation alone;
- test source/destination identity, invalid payloads, duplicate drops, and
  cancellation.

## Text input and speech input labels

Text fields should have visible prompts or labels, predictable focus routing,
and a clear submit/cancel path. For custom text or icon controls, use
accessibilityInputLabels so Voice Control users can identify the element with
natural alternate words. Do not fill input labels with every conceivable
phrase; choose a small localized set.

Validation should be a state machine:

    editing
      -> submit
      -> invalid field + explanatory value
      -> focus first actionable problem
      -> editable correction
      -> submit again

Keep keyboard dismissal separate from saving. A keyboard focus change is not
evidence that input is valid, and a VoiceOver focus change is not a submit.

For AI-assisted text entry, display the source text, model status, candidate,
and explicit edit/accept/reject controls. Never replace user text silently
because a model generated a suggestion.

## On-device AI review accessibility

An on-device model can produce a result that is visually polished but
semantically unsafe. Treat AI output as reviewable content:

| AI state | Semantic output |
| --- | --- |
| unavailable | Explain that the device/model path is unavailable and show a manual route |
| checking permission or capability | State what is being checked without implying generation has begun |
| generating | Expose a concise progress/status value and a cancel action |
| proposal | Identify source, candidate, caveats, and edit/accept/reject actions |
| refused/invalid | Describe the safe failure and preserve the original input |
| applying | Make the write scope and duplicate protection clear |
| saved | Report the committed record/revision and next action |
| stale/conflict | Explain that source data changed and require review |

Focus the review heading or status only when entering a new task or surfacing a
blocking error. Do not repeatedly move focus as tokens stream. Queue or
coalesce status changes rather than making VoiceOver speak every partial
output. Make the candidate selectable/editable when possible, and keep a
non-AI path that completes the same user outcome.

If an App Intent or accessible action accepts the candidate, validate current
identity, authorization, and revision in the domain layer. A successful model
callback is never a saved-state proof.

## Anti-patterns

Avoid:

- adding a decorative image’s filename as its spoken label;
- using a visible icon with no accessible name or action;
- putting the same label on every row in a list;
- flattening a card that contains independent controls;
- using accessibilitySortPriority to hide an incorrect hierarchy;
- auto-focusing every loading update;
- relying on a glass tint, color, or motion effect to communicate status;
- making a swipe or drag the only delete, reorder, or submit route;
- intercepting standard keyboard shortcuts without a strong reason;
- using onHover to expose functionality unavailable to touch or speech;
- constraining Dynamic Type with a fixed height;
- using Large Content Viewer instead of allowing content to grow;
- making a custom canvas accessible only through a screenshot or identifier;
- exposing sensitive AI output through a drag representation or system snippet
  without a deliberate privacy decision;
- claiming VoiceOver, Voice Control, Switch Control, or Liquid Glass proof from
  a simulator screenshot.

## Build sequence

1. Write the user task and domain action.
2. Choose standard controls and the navigation/presentation boundary.
3. Define the semantic tree: labels, values, traits, headings, actions, and
   grouping.
4. Define keyboard and accessibility focus ownership.
5. Add rotor/linked-group shortcuts only where linear navigation is costly.
6. Make Dynamic Type, contrast, transparency, and motion policy explicit.
7. Add pointer, hover, drag/drop, and keyboard enhancements with touch and
   accessible alternatives.
8. Connect App Intents to the same domain command.
9. Add an AI review state machine and manual fallback if AI is involved.
10. Run the proof matrix on a physical device and record SDK, OS, device,
    settings, fixture, and result.

## Sources

- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)
- [Accessible navigation](https://developer.apple.com/documentation/swiftui/accessible-navigation)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [FocusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [Input events](https://developer.apple.com/documentation/swiftui/input-events/)
- [onKeyPress(_:action:)](https://developer.apple.com/documentation/swiftui/view/onkeypress%28_%3Aaction%3A%29)
- [HoverEffect](https://developer.apple.com/documentation/swiftui/hovereffect)
- [onHover(perform:)](https://developer.apple.com/documentation/swiftui/view/onhover%28perform%3A%29)
- [onContinuousHover(coordinateSpace:perform:)](https://developer.apple.com/documentation/swiftui/view/oncontinuoushover%28coordinatespace%3Aperform%3A%29)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [dynamicTypeSize](https://developer.apple.com/documentation/swiftui/environmentvalues/dynamictypesize)
- [accessibilityDifferentiateWithoutColor](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilitydifferentiatewithoutcolor)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues)
- [accessibilityShowsLargeContentViewer()](https://developer.apple.com/documentation/swiftui/view/accessibilityshowslargecontentviewer%28%29)
- [Adopting drag and drop using SwiftUI](https://developer.apple.com/documentation/swiftui/adopting-drag-and-drop-using-swiftui)
- [Making a view into a drag source](https://developer.apple.com/documentation/swiftui/making-a-view-into-a-drag-source)
- [draggable(_:)](https://developer.apple.com/documentation/swiftui/view/draggable%28_%3A%29)
- [ContentShapeKinds](https://developer.apple.com/documentation/swiftui/contentshapekinds)
- [Gestures](https://developer.apple.com/design/human-interface-guidelines/gestures)
- [Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)
- [Pointing devices](https://developer.apple.com/design/human-interface-guidelines/pointing-devices)
- [VoiceOver](https://developer.apple.com/design/human-interface-guidelines/voiceover)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [App intents](https://developer.apple.com/documentation/appintents/app-intents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [XCUIAccessibilityAuditType](https://developer.apple.com/documentation/xcuiautomation/xcuiaccessibilityaudittype)
- [XCUIApplication.performAccessibilityAudit(for:_:)](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication/performaccessibilityaudit%28for%3A_%3A%29)
- [XCUIElementAttributes](https://developer.apple.com/documentation/xcuiautomation/xcuielementattributes)
