# Accessibility and alternate-input design

## Design goal

Apple-native polish is not only a visual resemblance to a system app. It is a
predictable relationship between hierarchy, semantics, focus, system settings,
and the physical ways a person can complete a task. Liquid Glass can make a
functional layer feel current, but the experience must still work when the
material becomes opaque, the animation becomes a cross-fade, the text becomes
large, or the person is using VoiceOver instead of sight.

This design page is the companion to the API deep dive. It is a review tool for
screens that use:

- SwiftUI standard controls and custom components;
- Liquid Glass navigation or action surfaces;
- on-device AI status, proposal, and commit flows;
- keyboard, pointer, hover, drag/drop, or Apple Pencil input;
- App Intents, widgets, controls, and other system entry points.

Related pages:

- [SwiftUI accessibility and alternate input](../42-framework-deep-dives/80-swiftui-accessibility-and-alternate-input.md)
- [SwiftUI accessibility and input route](../50-capability-recipes/111-swiftui-accessibility-input-route.md)
- [SwiftUI accessibility and input proof matrix](../60-verification/105-swiftui-accessibility-input-proof-matrix.md)
- [SwiftUI accessibility and input recipes](../70-code-recipes/123-swiftui-accessibility-input-recipes.md)
- [Animation, motion, and Liquid Glass design](106-animation-motion-and-liquid-glass-design.md)
- [Navigation transitions and presentation design](107-navigation-transitions-and-presentation-design.md)

## The four-layer screen review

Review every screen in this order:

    task hierarchy
      -> semantic hierarchy
      -> adaptive appearance
      -> alternate input and proof

### 1. Task hierarchy

Answer these questions before selecting a material or animation:

| Question | Design decision |
| --- | --- |
| What is the one primary outcome? | Name one primary action and make its result observable |
| What context must remain visible? | Keep source, title, current selection, and status near the action |
| What is secondary? | Move supporting facts behind custom content, a disclosure, or a secondary surface |
| What can be deferred? | Avoid time-boxed content and auto-dismissed feedback |
| What can fail? | Design unavailable, refused, stale, permission, and network states before the success state |
| What is the return path? | Provide a visible cancel/back/done route even when gestures are available |

An inaccessible screen often begins as an unclear task. A person should not
need to infer whether a translucent capsule is a button, whether a glowing
symbol is selected, or whether an AI result has been saved.

### 2. Semantic hierarchy

The accessibility tree should answer the same task questions without relying
on layout, color, translucency, or animation:

- the screen has a concise title or heading;
- major regions have meaningful headings;
- each action has a unique localized name;
- current values and status are announced as values, not only colors;
- decorative gradients, highlights, and glass effects do not add noise;
- independent actions remain independent elements;
- grouped content is atomic only when it is one meaningful concept;
- custom visualizations expose synthetic elements or a chart descriptor;
- the next sensible element is reachable in a predictable order.

Prefer visible text as the starting label. Add alternate input labels for
natural Voice Control phrases, not a list of internal IDs. Keep accessibility
identifiers for UI automation separate from spoken language.

### 3. Adaptive appearance

An Apple-like surface should survive at least this appearance matrix:

| Setting | What to inspect |
| --- | --- |
| Light and Dark appearance | Text, symbols, status colors, glass tint, and source content |
| Larger Text and accessibility sizes | Reflow, scroll behavior, button labels, sheet action visibility |
| Bold Text or stronger legibility | Weight, truncation, and contrast |
| Increase Contrast | Boundaries between control/content layers and selected/disabled states |
| Differentiate Without Color | Selection, errors, progress, and status without color alone |
| Reduce Transparency | Opaque or stronger surface fallback; text remains readable |
| Reduce Motion / Prefer Cross-Fade | No essential meaning is encoded only in morphing or depth |
| Dim Flashing Lights | No distracting or unsafe UI flashing |
| Color filters / Invert Colors | Important state remains understandable |
| RTL and long localization | Semantic order and action hierarchy stay correct |

Use system colors and text styles when the design permits. Custom colors,
fonts, and glass tints require a contrast and legibility review in every
supported appearance.

## Designing Liquid Glass for access

Liquid Glass belongs primarily to the functional layer: navigation, controls,
and focused task surfaces. It should help separate the controls from the
content layer while preserving context. Use standard SwiftUI controls and
containers first; they receive current system behavior and adapt to system
settings.

For custom glass:

| Decision | Preferred approach |
| --- | --- |
| Text-heavy surface | Regular glass or a more opaque material with clear contrast |
| Visually rich media surface | Clear glass only after testing the background and dimming layer |
| Several related controls | A small GlassEffectContainer when grouping/morphing improves hierarchy |
| Content background | Standard material or content surface, not a blanket glass wash |
| Accessibility fallback | Opaque or standard-material surface with the same semantics and actions |
| Reduced motion | Preserve the destination and action hierarchy without morphing |
| Reduced transparency | Let the surface become more solid and keep boundaries visible |

Design the semantic control first:

    Button / Toggle / Slider / NavigationLink
      -> label, value, trait, action, focus
      -> padding, hit region, content shape
      -> glass effect as the visual treatment
      -> pressed/hover/selected feedback

Do not place an inert Text or Image over a glass shape and expect it to behave
like a button. Do not make a large glass group one accessibility element if it
contains separate actions. Do not use clear glass over busy content without a
contrast test and a plan for Reduce Transparency.

### Glass and hierarchy

Use three visual levels:

1. content: the object, document, image, chart, or AI source;
2. functional layer: navigation, tabs, toolbars, primary actions, and
   contextual controls;
3. transient feedback: status, progress, confirmation, and error surfaces.

Liquid Glass is strongest in the functional layer. A custom glass card in the
content layer should have a specific interactive reason. If every card is
glass, the hierarchy disappears and the material becomes decoration.

## Designing for VoiceOver

VoiceOver navigation is a linear experience through the semantic tree. Design
the order before implementation:

    screen heading
      -> source/context
      -> current state
      -> primary action
      -> secondary actions
      -> supporting detail

This is a starting point, not a universal order. A form may place the first
field immediately after its heading. A media player may put transport controls
near the current time. A chart may need a compact summary plus a rotor for
individual data points.

Use a custom rotor when it saves meaningful traversal:

- Errors: jump between fields with an actionable error.
- Headings: move through a long knowledge or settings screen.
- Reviews: jump between pending AI proposals.
- Unread or selected items: move among items with a clear state.
- Chart data: navigate semantic data points or regions.

Use linked groups when two elements are semantically related but spatially
separated. The relationship should still make sense if the visual connection
or animation is removed.

Accessibility focus should follow task context:

- a new screen can focus a heading or first meaningful control;
- a failed submit can focus the first actionable error;
- a completed save can focus the result or the next action;
- a streamed AI token should not repeatedly steal focus;
- dismissal should return to a stable parent element when the task requires it.

## Designing for Dynamic Type

Start from the largest content size that the screen can reasonably support,
then make the normal size feel calm. This keeps the design from treating
accessibility as an exception.

Layout rules:

- use text styles and scalable metrics;
- let labels wrap;
- avoid fixed heights around user text;
- let primary actions become wider or stack vertically;
- keep status near its source field;
- allow scroll containers to scroll rather than compressing text;
- place icons beside, above, or below text when a single row cannot grow;
- test empty, error, editing, and long generated text states;
- keep the same semantic order after reflow.

If a compact control cannot grow because the platform layout requires it,
provide a Large Content Viewer representation. Do not use it to excuse a
fixed-size custom card or a clipped form.

## Designing color and contrast

Use more than color to communicate:

| State | Visual channels |
| --- | --- |
| Selected | Tint plus symbol, shape, weight, or explicit spoken value |
| Error | Color plus icon, text, field value, and focus route |
| Progress | Motion plus text/value and an accessible status |
| Success | Color plus checkmark/text and a durable result |
| Disabled | Reduced emphasis plus disabled trait and clear contrast |
| AI refusal | Neutral status icon plus plain-language explanation and manual route |

For glass and vibrant backgrounds, test the worst plausible content behind
the control. A beautiful blue control over a blue image is not a usable
control. System-defined colors are safer because they have accessible variants
and adapt to appearance.

If a state is difficult to distinguish under Differentiate Without Color, the
problem is usually the design hierarchy rather than a missing environment
branch.

## Designing alternate input

Every core task should have a route map:

| Input | Design expectation |
| --- | --- |
| Touch | Standard controls, expected gestures, clear target spacing |
| VoiceOver | Linear navigation, labels/values/actions, rotor where valuable |
| Voice Control | Visible/natural names, alternate input labels, no gesture-only action |
| Switch Control | Complete task without timing precision or hidden swipe-only actions |
| Full Keyboard Access | Every important destination and action is reachable |
| Hardware keyboard | Standard shortcuts respected; custom keys are additive |
| Pointer/trackpad | Hover/focus feedback without functionality hidden from touch |
| Drag and drop | Transferable payload, visible target feedback, button/action alternative |
| Apple Pencil or other device input | Standard alternative if drawing/precision input is core |

Do not make the pointer reveal the only way to discover an action. Do not make
long press reveal the only delete route. Do not make drag/drop the only way to
reorder. Custom gestures are enhancements until the equivalent action is
available through a standard control or accessible action.

### Keyboard and pointer polish

Focus is a state, not a decoration. A focused field should have a clear
editing relationship, while a focused card or button should not unexpectedly
change the domain selection. Hover may add a subtle lift, highlight, or
glass response, but the underlying action and label must remain the same.

For iPadOS, follow platform conventions for ordinary controls and let Full
Keyboard Access provide the expected navigation/activation route where Apple
recommends it. Add onKeyPress for a focused custom interaction only when the
target owns that event and a visible route exists.

## Designing drag and drop accessibly

Drag/drop is a data transfer route and a direct-manipulation gesture. Define:

1. what model value is transferable;
2. what representations can leave the app;
3. what destination accepts it;
4. what visual feedback identifies a valid target;
5. what happens for duplicates, invalid payloads, and cancellation;
6. how a person can do the same action without dragging.

For a reorderable list, provide Edit/reorder controls or accessible actions.
For a file import, provide an Import button and document picker route. For
moving an AI proposal, keep the proposal ID and current revision authoritative;
do not let a rendered preview become the saved object.

## Designing text input and AI review

A text or AI screen should make the source/candidate relationship visible:

    source
      -> generated candidate or manual edit
      -> review controls
      -> validation
      -> commit
      -> durable result

Design status as content:

- Available: tell the person what the action will do.
- Generating: show state and offer cancellation.
- Unavailable: explain the limitation and keep the manual route.
- Proposal: distinguish candidate from saved content.
- Refused or invalid: preserve the source and explain recovery.
- Applying: show scope and prevent duplicate activation.
- Saved: identify the durable result.

Use accessible values and custom content for useful status details, not a
stream of every token. Keep Accept, Edit, Reject, Cancel, and Retry as
ordinary controls with accessible names. A model’s confident tone is not a
permission to skip human review.

## App Intents as a design surface

App Intents extend a feature beyond the app. Design the system entry point and
in-app entry point together:

| Surface | Design responsibility |
| --- | --- |
| App Intent title/description | State the capability in plain language |
| App Shortcut phrase | Use a phrase a person would naturally say |
| Siri/Apple Intelligence result | Return a useful textual or visual result |
| In-app accessible action | Invoke the same domain command |
| Widget/control | Keep the action small, safe, and current |
| Deep link/open intent | Validate the destination before showing sensitive data |

System discoverability does not replace in-app accessibility. A person using
VoiceOver inside the app still needs a clear hierarchy, labels, values, and
actions. A person using Siri still needs a result that says whether the
operation succeeded, failed, was refused, or needs review.

## Component review cards

Use these review cards while designing.

### Glass button

- standard Button owns action and label;
- glass is applied to the button or its style, not a separate fake control;
- selected/disabled/pressed states have non-color cues;
- target spacing meets platform guidance;
- VoiceOver announces a concise title and state;
- Voice Control can say the visible or alternate name;
- Reduce Transparency and Increase Contrast preserve boundaries;
- Reduce Motion does not remove the action.

### AI proposal sheet

- sheet has a task title and explicit dismissal;
- source and candidate are distinguishable;
- status is an accessible value;
- Accept/Edit/Reject/Cancel are separate controls;
- dirty edits are protected;
- focus enters the heading or first useful status;
- large text scrolls without hiding actions;
- unavailable/refused/stale states keep a manual route;
- commit proof is separate from generation proof.

### Data-rich list

- rows have stable identity and useful labels;
- row actions do not become duplicate announcements;
- headings and filters are reachable;
- rotor entries are stable and useful;
- pagination/deletion updates the rotor safely;
- reordering has an accessible non-drag route;
- pointer/hover does not hide actions from touch or Voice Control.

## Design review checklist

Before implementation sign-off:

- [ ] The primary task and success state are named.
- [ ] Every important state has a semantic label/value/action plan.
- [ ] Standard controls are used where their behavior fits.
- [ ] Custom grouping does not swallow independent actions.
- [ ] Dynamic Type can reflow the actual content.
- [ ] Color is paired with text, shape, glyph, or value.
- [ ] Reduce Transparency has a tested surface result.
- [ ] Reduce Motion has a tested route result.
- [ ] VoiceOver order and initial focus are intentional.
- [ ] Rotor/linked groups are justified by traversal cost.
- [ ] Voice Control names are natural and unique.
- [ ] Switch Control can complete the task.
- [ ] Keyboard and pointer routes are additive and conventional.
- [ ] Drag/drop has a visible and accessible alternative.
- [ ] App Intent actions use the same domain authority.
- [ ] AI output is reviewable and never silently replaces user content.
- [ ] Physical-device proof is planned for assistive technologies.

## Sources

- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [VoiceOver](https://developer.apple.com/design/human-interface-guidelines/voiceover)
- [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Gestures](https://developer.apple.com/design/human-interface-guidelines/gestures)
- [Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)
- [Pointing devices](https://developer.apple.com/design/human-interface-guidelines/pointing-devices)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Color](https://developer.apple.com/design/human-interface-guidelines/color)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)
- [Accessible navigation](https://developer.apple.com/documentation/swiftui/accessible-navigation)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [FocusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [Input events](https://developer.apple.com/documentation/swiftui/input-events/)
- [HoverEffect](https://developer.apple.com/documentation/swiftui/hovereffect)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
