# Navigation transitions and presentation design

## Design principle

The system should make it obvious whether a person is:

    moving within the app hierarchy
      -> completing a focused modal task
      -> reviewing a generated proposal
      -> returning to the prior context

Use native navigation and presentation surfaces to preserve context. Treat
Liquid Glass and zoom as an explanation layer, not as a substitute for route
identity or durable state.

Use this page with:

- [SwiftUI navigation transitions and presentation](../42-framework-deep-dives/79-swiftui-navigation-transitions-and-presentation.md)
- [Navigation, toolbar, and tab hierarchy](09-navigation-toolbar-and-tab-hierarchy.md)
- [Sheets, forms, and focused editing](10-sheets-forms-and-focused-editing.md)
- [Animation, motion, and Liquid Glass design](106-animation-motion-and-liquid-glass-design.md)
- [SwiftUI navigation and presentation route](../50-capability-recipes/110-swiftui-navigation-presentation-route.md)

## Choose hierarchy before decoration

| User outcome | Native surface | Why |
| --- | --- | --- |
| Browse records and open detail | NavigationStack | The path expresses durable app context |
| Review a small AI proposal | Sheet | Focused decision that returns to source context |
| Edit media, scan, or complete a long flow | Full-screen cover | Immersive/multistep task with clear finish/cancel |
| Pick a related option while staying oriented | Popover or confirmation dialog | Supplementary choice |
| Show a compact supplementary tool | Nonmodal sheet/panel appropriate to platform | Parent context remains meaningful |

Do not make every action a sheet. HIG Modality says modal experiences should
have a clear benefit, stay scoped, and have an obvious dismissal path. If the
user is navigating the app’s primary information architecture, use navigation
instead of stacking transient modals.

## Route identity and visual continuity

Use a route value for the destination and stable identity for the visual source:

    recordID -> Route.detail(recordID)
      -> source matchedTransitionSource(id: recordID, in: namespace)
      -> destination navigationTransition(.zoom(sourceID: recordID, in: namespace))

This creates a coherent visual relationship without putting the entire record
in the route. If the record is deleted, stale, unauthorized, or unavailable,
the destination should explain that state instead of crashing or showing a
stale screenshot.

Use zoom when the destination is the same meaningful object. Use automatic
navigation when the relationship is weak or when a standard transition is
clearer. Use a crossfade/identity reduced-motion route. Avoid visually zooming
from a decorative icon into unrelated content because the motion teaches the
wrong mental model.

The back button, title, accessibility labels, focus, and route path must remain
correct if the visual transition is removed.

## Presentation state chart

Write the presentation state separately from domain state:

| Presentation state | Domain meaning | Design |
| --- | --- | --- |
| not presented | Parent context visible | Primary task remains available |
| presenting | System is opening the surface | Do not duplicate controls behind the transition |
| presented | Focused task is active | Title, current task, and dismissal are obvious |
| dirty | Unsaved edits exist | Cancel/save/confirm policy is explicit |
| applying | A commit is in flight | Disable duplicate actions, preserve scope |
| dismissed | Surface closed | Parent reconciles current source and pending work |
| unavailable | Required device/model/permission cannot run | Manual route is visible in the surface or parent |

A binding or optional item can control presentation, but it is not a commit
record. On dismissal, reconcile with the model/service and decide whether a
draft was saved, discarded, retained, or returned to the parent.

## Sheet composition

For a small sheet:

    task title
      -> source/context
      -> one primary action
      -> cancel/back/dismiss path
      -> visible validation/error/status

For editable content:

- provide a title that names the task;
- pair Done with Cancel when the person needs to choose save versus discard;
- use Back only when there is a genuine multistep hierarchy;
- do not show Cancel, Done, and Back in a confusing cluster;
- protect unsaved changes before interactive dismissal;
- keep the sheet’s content scrollable at large text sizes;
- use system detents and a visible drag indicator when resizing is meaningful;
- avoid nesting another modal unless the first one is deliberately replaced.

For a long AI review, use a full-screen cover or a NavigationStack inside the
presentation only when the hierarchy is truly needed. Make the exit route
obvious and preserve the original source so the person can compare it to the
proposal.

## Detent and background design

Choose detents around meaningful stages, not arbitrary screenshots:

| Detent | Good use |
| --- | --- |
| small/custom | Compact status or one clear action |
| medium | Short review or focused choice |
| large | Long source, editor, or multistep flow |
| selected detent | Programmatic response to a meaningful state change |

Use presentationContentInteraction when content scrolling and sheet resizing
would otherwise compete. Use presentationBackgroundInteraction only when the
parent can safely remain actionable. A partially expanded sheet that lets the
user tap a parent control should not allow conflicting edits or duplicate side
effects.

Use presentationSizing with system form/page/fitted policies when a content
driven presentation needs a stable size. Add sticky behavior only when frequent
content changes would create distracting resizing. Use contentMargins for
scrollContent or scrollIndicators rather than negative offsets.

## Liquid Glass inside presentations

The system owns the outer sheet/popover/cover treatment. Custom Liquid Glass
should be a small, functional group inside the presentation:

- source context and proposal status can share a visual group;
- primary review actions can use standard glass button styles;
- nearby related shapes can use a GlassEffectContainer;
- stable glass IDs can coordinate a compact-to-expanded action group;
- materialize is appropriate when an item appears at a distant location;
- the material must not be the only contrast or state signal;
- reduced transparency and increased contrast need a tested fallback.

Do not put a full-screen custom glass background behind a system modal and
assume it will match Apple’s implementation. Keep the system surface, safe
areas, content margins, and dismissal behavior intact.

## AI proposal review design

Use the presentation to make uncertainty and agency visible:

    source
      -> model availability and input scope
      -> generating/progress/cancel
      -> candidate/refusal/error
      -> provenance/schema/model version
      -> edit/accept/reject
      -> applying
      -> saved or failed

The review surface should answer:

- What source did the model see?
- What did it generate?
- Which parts are generated versus user-authored?
- What will accepting change?
- Can the person edit before applying?
- What happens if the model is unavailable?
- What happens if the source became stale?
- Can the person cancel without losing the source?

Use a short sheet for a bounded accept/reject decision. Use full screen for a
long document, image, or multimodal comparison. Use navigation when the
proposal is part of the app’s durable review history. Do not use presentation
dismissal or zoom completion as proof of acceptance.

## Accessibility contract

Navigation and presentation must work without visual continuity:

- VoiceOver announces the destination title, current status, and actions;
- the first focus target is useful after a presentation opens;
- the dismiss action is discoverable and does not require a custom gesture;
- the route remains understandable with Reduce Motion;
- large text does not clip the title, status, or primary action;
- reduced transparency keeps the surface and controls legible;
- increased contrast and Differentiate Without Color preserve state meaning;
- Voice Control can name the actions;
- Switch Control can complete the workflow;
- keyboard/pointer navigation does not depend on a timed transition;
- long localized strings and right-to-left layout do not break the source/
  destination relationship.

If an AI proposal uses a visual diff, also provide a semantic textual
description of the change. If a sheet contains a loading state, expose a
status and cancellation action rather than an indefinite visual effect.

## Review checklist

- Does the chosen surface match the task’s scope and lifetime?
- Is the route a lightweight stable value?
- Is zoom/geometry connecting the same meaningful object?
- Does the destination remain correct if the source record changes?
- Does the sheet have an obvious title and dismissal path?
- Are detents, background interaction, content interaction, and adaptation
  intentional?
- Can a user cancel without losing a draft or leaving an in-flight operation
  in an unknown state?
- Does the system own the outer presentation treatment?
- Does the Liquid Glass group preserve contrast and accessibility?
- Does the AI surface distinguish candidate, applying, saved, and failed?
- Can the complete task be finished with Reduce Motion and VoiceOver?
- Are route delivery and physical/system proof separate from a preview?

## Sources

- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [Understanding the navigation stack](https://developer.apple.com/documentation/swiftui/understanding-the-navigation-stack)
- [NavigationTransition](https://developer.apple.com/documentation/swiftui/navigationtransition)
- [matchedTransitionSource(id:in:)](https://developer.apple.com/documentation/swiftui/view/matchedtransitionsource%28id%3Ain%3A%29)
- [ZoomNavigationTransition](https://developer.apple.com/documentation/swiftui/zoomnavigationtransition)
- [Modal presentations](https://developer.apple.com/documentation/swiftui/modal-presentations)
- [Presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [PresentationSizing](https://developer.apple.com/documentation/SwiftUI/PresentationSizing)
- [presentationSizing(_:)](https://developer.apple.com/documentation/swiftui/view/presentationsizing%28_%3A%29)
- [contentMargins(_:_:for:)](https://developer.apple.com/documentation/SwiftUI/View/contentMargins%28_%3A_%3Afor%3A%29-1lt8b)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Modality](https://developer.apple.com/design/human-interface-guidelines/modality)
- [Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets)
- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
