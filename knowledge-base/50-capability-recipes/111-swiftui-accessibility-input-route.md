# SwiftUI accessibility and alternate-input route

## Route contract

Use this route when an app idea needs a native SwiftUI screen that works with
VoiceOver, Voice Control, Switch Control, Dynamic Type, reduced motion,
reduced transparency, Full Keyboard Access, pointer input, hover, or drag and
drop. The route also covers accessible AI review and App Intent entry points.

The output is not merely a list of modifiers. It is a contract between:

    user outcome
      -> semantic view model
      -> visual/adaptive surface
      -> focus and input routes
      -> domain action
      -> proof packet

Related pages:

- [SwiftUI accessibility and alternate input](../42-framework-deep-dives/80-swiftui-accessibility-and-alternate-input.md)
- [Accessibility and alternate-input design](../21-design-deep-dives/108-accessibility-and-alternate-input-design.md)
- [SwiftUI accessibility and input proof matrix](../60-verification/105-swiftui-accessibility-input-proof-matrix.md)
- [SwiftUI accessibility and input recipes](../70-code-recipes/123-swiftui-accessibility-input-recipes.md)
- [Focus and alternate-input proof matrix](../60-verification/14-focus-and-alternate-input-proof-matrix.md)

## Phase 0: name the task

Write one sentence:

    A person can [outcome] from [starting context] and can recover when
    [failure/unavailability].

List the durable domain action separately from view state:

| State family | Example | Owner |
| --- | --- | --- |
| Domain | record, draft, proposal, revision, authorization | model/service/store |
| Presentation | sheet, route, alert, popover | feature/root view |
| Keyboard focus | focused field or region | view |
| Accessibility focus | VoiceOver target | view |
| Appearance preference | Dynamic Type, motion, transparency, contrast | system environment |
| Input gesture | pointer hover, drag target, key phase | view/system |
| AI state | unavailable, generating, proposal, applying, saved, failed | feature/domain boundary |

Do not use accessibility focus as a domain selection. Do not use a sheet Boolean
as the identity of an AI proposal. Do not let a hover phase own a saved state.

## Phase 1: choose the semantic control

Prefer a standard SwiftUI control:

| Need | Start with |
| --- | --- |
| Invoke an action | Button |
| Change a Boolean | Toggle |
| Choose one value | Picker or Menu |
| Choose a range | Slider |
| Enter text | TextField or TextEditor |
| Navigate | NavigationLink |
| Present a focused task | sheet/fullScreenCover/popover |
| Scroll | ScrollView/List |
| Reorder or transfer | Transferable plus draggable/dropDestination |

Then inspect the semantic tree. Add explicit accessibility behavior only for a
known gap:

    standard control
      -> label/value/hint/trait
      -> custom action if needed
      -> focus/rotor relationship if needed
      -> glass/animation/hover treatment

The order matters. A visual custom shell should not decide whether something is
interactive.

## Phase 2: define the screen semantic map

For each important element, record:

| Field | Example |
| --- | --- |
| Visible title | “Review summary” |
| Accessibility label | “Review summary” |
| Value | “3 changes pending” |
| Hint | “Opens the proposed changes for editing” |
| Traits/role | heading, button, adjustable, selected |
| Actions | Accept, Edit, Reject, Delete |
| Input labels | “Review”, “Open summary” |
| Focus target | heading, field, error, result |
| Identifier | review.summary.heading |

Keep the user-facing strings localized. Accessibility identifiers can be
stable test keys but should not be spoken.

## Phase 3: group and order

Choose one of these shapes per region:

| Visual region | Semantic choice |
| --- | --- |
| Decorative glass background | Hidden |
| Icon plus label that is one action | One control |
| Card with one open action | One element or a NavigationLink |
| Card with favorite/share/open | Separate controls |
| Custom drawing with data marks | Synthetic accessibility children or chart descriptor |
| Form field and error | Field plus associated error value/focus route |
| Distant heading/status/actions | Linked group only if the relationship is valuable |

Test the linear order before adding a rotor. A rotor is a shortcut, not a
repair for a disorganized screen.

## Phase 4: route accessibility focus

Use AccessibilityFocusState for a deliberate state transition:

| Event | Focus policy |
| --- | --- |
| Present a new task | Heading or first meaningful control |
| Submit invalid form | First actionable invalid field/error |
| AI generation starts | Status only if it explains a new task; offer Cancel |
| AI proposal arrives | Proposal heading or summary, not every streamed update |
| Apply succeeds | Durable result or next action |
| Conflict/stale data | Conflict explanation and recovery action |
| Dismiss sheet | Parent control that restores context when useful |

Keep an optional enum for multiple targets:

    enum AccessibilityTarget: Hashable {
        case heading
        case titleField
        case summary
        case error
    }

The actual property wrapper and modifier signature must be compiled in the
selected SDK. The design contract remains the same if a platform fallback is
needed.

## Phase 5: add rotor and linked-group routes

Add a custom rotor only when a person benefits from skipping linear traversal:

1. name the semantic category;
2. generate entries from stable domain IDs;
3. attach explicit entry identity to the target view;
4. use concise localized entry labels;
5. handle empty, filtered, deleted, and off-screen items;
6. test VoiceOver rotor navigation on device.

Use AccessibilityLinkedGroup for separated but related elements. Do not link
every element in a card or every row in a list.

Good route examples:

- Pending reviews rotor -> each unresolved proposal heading;
- Errors rotor -> each actionable form error;
- Sections rotor -> headings in a long settings screen;
- Chart points rotor -> data points with labels and values.

## Phase 6: Dynamic Type and appearance policy

Define the supported appearance fixture before implementing the layout:

    normal / dark / accessibility5 / reduce transparency /
    increase contrast / differentiate without color / reduce motion

For each fixture, confirm:

- primary actions remain visible;
- text wraps and does not clip;
- sheets and popovers remain scrollable;
- glass surfaces preserve boundaries;
- state is not conveyed by color alone;
- animations do not carry the only meaning;
- the semantic order remains stable after reflow.

Use dynamicTypeSize and scalable metrics for code. Use
accessibilityShowsLargeContentViewer only for genuinely compact controls that
cannot grow.

For Liquid Glass:

1. let system components own the default treatment;
2. use custom glass sparingly for functional surfaces;
3. use regular for dense text/contrast-sensitive content;
4. use clear only over tested rich backgrounds;
5. gate custom opacity/material treatment with
   accessibilityReduceTransparency;
6. choose a static/opaque or standard-material route under reduced
   transparency or motion;
7. keep labels/actions independent from the visual effect.

## Phase 7: keyboard and pointer route

Use FocusState to model keyboard focus with a typed field/region enum:

    enum Field: Hashable {
        case search
        case title
        case notes
    }

Then decide:

| Requirement | Route |
| --- | --- |
| Activate an existing command | keyboardShortcut |
| Handle a focused key sequence | onKeyPress |
| Move focus after validation | FocusState assignment |
| Observe a focused value | FocusedValue / FocusedBinding where appropriate |
| Give pointer feedback | hoverEffect |
| Run enter/exit logic | onHover |
| Track pointer coordinates | onContinuousHover |

Do not override a standard shortcut without a strong reason. Do not make a
custom key loop the only way to activate an ordinary control. Return handled
only when the focused view consumed the key; otherwise return ignored.

Pointer behavior is additive:

- hover can highlight or lift a control;
- pointer location can update a preview;
- touch and Voice Control must still reveal and activate the same feature;
- a hover-only tooltip is not a substitute for a label or visible affordance.

## Phase 8: drag/drop route

For a transferable model:

    Transferable model
      -> draggable(model)
      -> system transfer representation
      -> dropDestination(for:action:isTargeted:)
      -> payload validation
      -> visible target feedback
      -> domain commit

Record:

- exportable representation and privacy scope;
- accepted destination and allowed operation;
- duplicate/invalid/cancel behavior;
- reorder/index behavior;
- visible button/action alternative;
- accessibility drag and drop points if geometry is custom;
- post-drop value/status/focus result.

Use identifiers or intentionally scoped representations rather than exporting
an entire private model. A successful drop callback only proves that the view
received a payload; it does not prove the domain write succeeded.

## Phase 9: text-entry route

Define a focused editing loop:

    idle
      -> field focused
      -> editing
      -> submit
      -> validation
      -> invalid field/error focus
      -> editing
      -> valid commit
      -> result

Use visible prompts and text content semantics. Add accessibilityInputLabels
for natural Voice Control names when a custom control needs them. Keep
keyboard dismissal, validation, and persistence as separate events.

For a form with several fields:

1. use one FocusState enum;
2. give each field a unique enum case;
3. select the first actionable error after validation;
4. place the error near the field and expose it as value/custom content;
5. keep the Save/Next action available through touch, keyboard, and assistive
   input;
6. test long text, localization, Dynamic Type, and Switch Control.

## Phase 10: App Intent route

Create an App Intent when a meaningful app capability belongs in Siri,
Apple Intelligence, Shortcuts, Spotlight, widgets, controls, or a system
button. Provide:

- a localized title and description;
- parameters with clear summaries;
- an App Shortcut for a common action;
- a result that explains success/failure;
- an OpenIntent or URL/deep-link policy when navigation is needed;
- the same domain validation as the visible control.

If an in-app accessibility action invokes an App Intent, treat it as a shared
entry point, not as a bypass. Recheck current model identity, authorization,
revision, and user confirmation in the action layer.

## Phase 11: on-device AI review route

Use a typed feature state:

    unavailable
    checking
    generating
    proposal(candidateID)
    applying(candidateID, revision)
    saved(recordID, revision)
    refused(reason)
    failed(reason)
    stale(candidateID, currentRevision)

Map it to the accessibility contract:

| State | Visible surface | Accessible output | Allowed action |
| --- | --- | --- | --- |
| unavailable | Explanation plus manual path | “On-device suggestions unavailable” | Manual action |
| generating | Progress/status plus Cancel | Concise status value | Cancel |
| proposal | Source/candidate/review controls | Candidate and caveats | Edit, Accept, Reject |
| applying | Scope and progress | “Applying…” value | Cancel only if supported |
| saved | Result/revision | Saved state and next action | Open, Undo if supported |
| refused/failed | Recovery message | Reason and source preserved | Retry/manual |
| stale | Conflict surface | Data changed; review required | Refresh/review |

Do not stream every token to VoiceOver. Do not move accessibility focus for
every progress update. Do not announce an uncommitted candidate as a saved
record.

## Phase 12: verification route

Run in layers:

1. compile the named target with the selected SDK and deployment target;
2. exercise previews with large text and environment overrides;
3. run UI tests for labels, identifiers, values, actions, and focus;
4. run Accessibility Inspector audits;
5. run the task manually with VoiceOver, Voice Control, Switch Control, and
   Full Keyboard Access where supported;
6. run pointer/hover and drag/drop on iPad or Mac Catalyst where in scope;
7. run Liquid Glass with reduced transparency, contrast, and motion settings;
8. install on a physical device for assistive technologies;
9. record build, SDK, OS, device, settings, fixture, and observed result.

Stop the route if:

- a core action is only reachable through an unexposed gesture;
- the semantic tree cannot describe the state without the glass animation;
- Dynamic Type clips a title, error, or primary action;
- an accessible action bypasses authorization or validation;
- an AI result is presented as saved before a domain commit;
- a test passes only because it queries an identifier instead of the actual
  label/value/action;
- physical-device proof is claimed from a simulator run.

## Minimal route template

Copy this into a feature brief:

    Outcome:
    Primary domain action:
    Standard control:
    Visible title:
    Accessibility label/value/hint:
    Traits/heading/grouping:
    Accessible actions:
    Accessibility focus target:
    Keyboard focus target:
    Rotor/linked-group reason:
    Dynamic Type reflow:
    Contrast/color fallback:
    Reduce Transparency route:
    Reduce Motion route:
    Touch/VoiceOver/Voice Control/Switch Control routes:
    Keyboard/pointer route:
    Drag/drop alternative:
    App Intent route:
    AI availability/refusal/review/commit states:
    Physical-device proof:
    Release boundary:

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
- [accessibilityShowsLargeContentViewer()](https://developer.apple.com/documentation/swiftui/view/accessibilityshowslargecontentviewer%28%29)
- [accessibilityDifferentiateWithoutColor](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilitydifferentiatewithoutcolor)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [Adopting drag and drop using SwiftUI](https://developer.apple.com/documentation/swiftui/adopting-drag-and-drop-using-swiftui)
- [Making a view into a drag source](https://developer.apple.com/documentation/swiftui/making-a-view-into-a-drag-source)
- [draggable(_:)](https://developer.apple.com/documentation/swiftui/view/draggable%28_%3A%29)
- [Gestures](https://developer.apple.com/design/human-interface-guidelines/gestures)
- [Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)
- [Pointing devices](https://developer.apple.com/design/human-interface-guidelines/pointing-devices)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [App intents](https://developer.apple.com/documentation/appintents/app-intents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
