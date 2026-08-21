# SwiftUI navigation transitions and presentation

## Purpose

Native navigation is a state and identity system with a visual transition on
top. A sheet, full-screen cover, popover, or zoom transition should help a
person understand where they came from, what task they entered, and how to
return. It should not become a second source of truth for an AI result,
authorization, or saved record.

This page joins the current SwiftUI NavigationStack, navigation-transition,
matched-transition-source, zoom, modal presentation, presentation sizing,
content margins, Liquid Glass, accessibility, and HIG Modality/Sheets routes.

Use this page with:

- [SwiftUI animation, motion, transitions, and feedback](78-swiftui-animation-motion-transitions-and-feedback.md)
- [Navigation, toolbar, and tab hierarchy](../21-design-deep-dives/09-navigation-toolbar-and-tab-hierarchy.md)
- [Sheets, forms, and focused editing](../21-design-deep-dives/10-sheets-forms-and-focused-editing.md)
- [Universal Links, Handoff, and scene delivery](72-universal-links-handoff-and-scene-delivery.md)
- [SwiftUI navigation and presentation route](../50-capability-recipes/110-swiftui-navigation-presentation-route.md)
- [SwiftUI navigation and presentation proof matrix](../60-verification/104-swiftui-navigation-presentation-proof-matrix.md)
- [SwiftUI navigation and presentation recipes](../70-code-recipes/122-swiftui-navigation-presentation-recipes.md)

## Presentation vocabulary

Choose the system surface by task and lifetime:

| Need | SwiftUI route | State shape | Design meaning |
| --- | --- | --- | --- |
| Push a destination in a stack | NavigationStack, NavigationLink, navigationDestination | Lightweight Hashable route/path | The person remains in the app’s navigation hierarchy |
| Programmatic/deep-link navigation | NavigationStack path or navigationDestination(item:) | Typed route values | The route can be restored, validated, and tested |
| Show a focused temporary task | sheet(isPresented:) or sheet(item:) | Bool or optional Identifiable item | Scoped task that returns to the parent context |
| Show an immersive or multistep task | fullScreenCover | Bool or optional Identifiable item | Full-screen focus, such as media/capture/editing |
| Offer supplementary choices | popover or confirmationDialog | Binding/presentation state | Contextual options without a new app hierarchy |
| Let a sheet rest at natural sizes | presentationDetents and selection | PresentationDetent binding | A user-resizable presentation with a known state |
| Control sizing on supported presentations | presentationSizing | PresentationSizing policy | Fitted/form/page or a documented custom size |
| Choose compact adaptation | presentationCompactAdaptation | Horizontal/vertical adaptation | Explicit behavior across size classes |
| Control what is behind the presentation | presentationBackgroundInteraction | Automatic/disabled/enabled/up-through detent | Whether the parent remains actionable |
| Control sheet swipe behavior | presentationContentInteraction | Scrolls or resizes policy | How content gestures compete with the sheet gesture |
| Show a related object growing into detail | matchedTransitionSource plus navigationTransition(.zoom(...)) | Stable source ID and Namespace | The same object is visually connected across navigation |

Use a presentation binding as presentation state. Keep the domain state
separate:

    route/presentation state -> destination/review view
      -> current domain lookup -> action/commit state

When the user dismisses a presentation, SwiftUI can reset the binding that
initiated it. Treat that as a presentation event, then decide explicitly what
happens to drafts, pending requests, and unsaved changes.

## Navigation is typed identity

NavigationStack exposes the visible stack through its path. Use a lightweight
Hashable route or a homogeneous array where possible. Use NavigationPath only
when a heterogeneous path genuinely helps the feature.

Recommended route shape:

    Route.inbox
    Route.detail(recordID)
    Route.review(proposalID)
    Route.settings

The route is not the model. At the destination:

1. resolve the current record by stable identity;
2. re-check authorization and freshness;
3. render unavailable/stale/deleted states safely;
4. keep unsaved drafts in their intended owner;
5. let the destination’s actions call the domain authority.

Avoid placing a full observable model, raw media, credentials, private model
context, or unsaved secret in a navigation path. A route should survive
encoding/decoding and be meaningful when the underlying record changes.

Value-destination navigation is preferable when the app must observe or
restore the stack. View-destination links are fire-and-forget from the app’s
perspective and are less useful for explicit deep-link state.

## Matched navigation transitions and zoom

SwiftUI’s matchedTransitionSource identifies a view as the source of a
navigation transition, such as a zoom. The source uses a stable Hashable ID
inside a Namespace. A zoom navigation transition points at that source ID and
namespace.

The relationship is:

    source view
      -> matchedTransitionSource(id:in:)
      -> NavigationLink(value:)
      -> destination route
      -> navigationTransition(.zoom(sourceID:in:))

This is related to, but distinct from, matchedGeometryEffect:

| Feature | Scope | Best use |
| --- | --- | --- |
| matchedGeometryEffect | Two SwiftUI views in one view hierarchy/namespace | A card or control represented in two layout states |
| matchedTransitionSource + zoom | Navigation into a destination | A list/card thumbnail visually leading into a detail screen |
| Standard NavigationStack transition | System-selected navigation relationship | Most destinations where custom visual linking adds little |

The source and destination must represent the same meaningful object. Derive
the ID from stable record identity, not from a position in a list or a new
random value each render. Keep the destination correct if the source disappears
or the item becomes unavailable.

The navigationTransition modifier belongs on the destination view that appears
within a NavigationStack or sheet and outside of containers such as VStack,
according to the SwiftUI documentation. Compile the smallest version in the
target because navigation-transition declarations and availability can vary
with the selected SDK. Zoom is not supported on tvOS; keep platform conditions
explicit when sharing code.

Treat zoom as a visual aid. It does not replace:

- a navigation title and back behavior;
- VoiceOver labels and focus;
- a route value that can be restored/deep-linked;
- a reduced-motion alternative;
- correct destination state when the source record changes.

When Reduce Motion is enabled or the relation is not clear, use automatic or a
simple crossfade/identity route while preserving the same navigation task.

## Modal presentation as a scoped task

Apple’s HIG describes modality as a separate, dedicated mode that prevents
interaction with the parent and requires an explicit dismissal. Use a modal
only when it helps focus on a narrowly scoped task, decision, or immersive
content.

Modal rules:

- keep the task simple and short when possible;
- give the presentation a title that names the task;
- provide an obvious dismissal path;
- protect unsaved user-created content before dismissal;
- let people dismiss one modal before presenting another;
- avoid turning a sheet into an app-within-the-app;
- use full-screen presentation for complex editing, capture, media, or
  multistep tasks when a sheet would make context confusing;
- use an item-based presentation when the presence of a specific item is the
  source of truth;
- use a Boolean only when the presentation truly has no identity beyond
  presented/not presented.

For a reviewable AI proposal, an item-based sheet can carry a stable proposal
ID while the model resolves the current candidate. Do not put the generated
text or commit authority into a transient presentation Boolean.

## Sheet sizing and detents

Use presentationDetents when the sheet has meaningful natural sizes. A
selection binding lets the app observe or choose the current detent, but the
selection is still presentation state. It does not represent a domain phase.

Use presentationContentInteraction to define how swipe gestures interact with
the sheet’s content. Use presentationDragIndicator when the resize/dismiss
affordance would otherwise be unclear. Use interactiveDismissDisabled only when
there is a real data-loss or in-flight safety reason, and provide an explicit
save/cancel/recovery route.

Current SwiftUI presentation sizing also exposes automatic, fitted, form, and
page sizing policies through PresentationSizing. Use the system sizing first.
If content size changes frequently, consider a sticky direction so the
presentation does not resize in a distracting way. Define minimum/maximum
content bounds for custom or fitted routes and test long text/Dynamic Type.

Do not use a custom fixed height merely to imitate one screenshot. Sheets must
adapt to device size, orientation, text size, keyboard, localization, and
input method.

## Presentation background, interaction, and adaptation

Use presentationBackground to style a presentation’s background, including a
shape style or a custom view. If custom Liquid Glass is appropriate, keep it
inside the system presentation and preserve the system’s dismissal, margins,
contrast, and accessibility behavior.

Use presentationBackgroundInteraction deliberately:

| Policy | Use when |
| --- | --- |
| automatic | The system’s contextual default is correct |
| disabled | The modal task must be completed before the parent is actionable |
| enabled | The presentation is supplementary and parent interaction is safe |
| enabled(upThrough:) | A compact detent can coexist with parent interaction but a larger task should block it |

Use presentationCompactAdaptation to decide how a sheet/popover adapts in
compact size classes. Test iPhone portrait, iPhone landscape where supported,
iPad split view, iPad multitasking, keyboard, pointer, and Mac Catalyst if the
target supports it.

presentationCornerRadius requests a radius; it does not authorize a design
that ignores platform conventions. presentationSizing and presentation
background are system configuration, not a reason to rebuild a modal shell
from scratch.

## Content margins and native breathing room

SwiftUI’s contentMargins modifier configures margins for a placement such as
scrollContent or scrollIndicators. Use it to give a presentation or review
surface adaptive breathing room while preserving the system safe area.

Keep the responsibilities separate:

| Concern | Route |
| --- | --- |
| Space between the presentation and its content | Presentation sizing/background and content layout |
| Insets for scrollable content | contentMargins with scrollContent |
| Insets for scroll indicators | contentMargins with scrollIndicators |
| System unsafe-area boundary | safeAreaInset, safeAreaPadding, or ignoresSafeArea with an explicit reason |
| Glass shape bounds | GlassEffectContainer and the view’s shape |

Do not compensate for a wrong presentation size with large negative offsets.
Test content margins with large text, long localized strings, scroll indicators,
keyboard, Dynamic Type, and reduced transparency.

## Liquid Glass arrival shells

System components already use the current Liquid Glass treatment. For custom
content:

- prefer a standard sheet/navigation presentation and let the system own its
  outer behavior;
- use a small glass group for the review/action surface;
- use glassEffectID and GlassEffectContainer only for related shapes that
  should blend or morph;
- use matched geometry for related nearby shapes and materialize for distant
  add/remove behavior;
- keep a clear title, source, status, and action hierarchy;
- do not draw a duplicate full-screen glass background inside the modal;
- provide reduced-transparency and increased-contrast routes.

For a zoomed detail screen, a glass background can frame the destination after
navigation, but the source ID and destination route must remain understandable
without the visual effect.

## On-device AI presentation states

Model output needs a reviewable presentation contract:

    source -> availability -> generation
      -> proposal/refusal/error
      -> review presentation
      -> explicit acceptance
      -> apply/commit
      -> saved/stale/failed

Use a sheet for a small, focused review decision. Use a full-screen cover when
the review needs long source context, editing, camera/media, or a multistep
workflow. Use NavigationStack when the review is part of the app’s durable
information hierarchy or must be deep-linked/restored.

Presentation motion must not imply:

- the model is available when it is not;
- a generated candidate is a fact;
- a proposal is accepted before validation;
- a side effect succeeded because a sheet dismissed;
- a canceled request completed.

When a presentation dismisses, preserve or discard the draft according to the
feature’s explicit policy. If the model request continues after dismissal, its
owner should be an explicit model/service task, not an accidental view task.

## Accessibility and dismissal

Every presentation must be completable with:

- VoiceOver, including a clear title, focus target, status, and dismissal;
- Dynamic Type and long text;
- Reduce Motion, with a stable destination and no motion-only meaning;
- reduced transparency and increased contrast;
- Voice Control and Switch Control;
- keyboard/pointer when supported;
- localization and right-to-left layout.

Provide Cancel plus Done when a sheet has editable content and the user needs a
choice between discarding and accepting. Do not present Cancel, Done, and Back
in a confusing three-button cluster; choose the smallest clear navigation
model. If an interactive dismissal could lose edits, ask for confirmation and
make the recovery options explicit.

Do not stack sheets casually. If a task needs another modal, dismiss or
replace the first presentation intentionally and preserve the user’s context.

## Proof boundary

| Claim | Evidence | Does not prove |
| --- | --- | --- |
| Route is deep-linkable | Typed route/path fixture and cold/warm UI run | Public Universal Link/Handoff delivery |
| Zoom source is paired | Named target compile and source/destination run | Accessibility or reduced-motion completion |
| Sheet has correct detents | Selection/detent run across device sizes | Every text/keyboard/localization layout |
| Dismissal is safe | Unsaved draft/cancel/interactive-dismiss tests | Data durability without a persistence test |
| Presentation background is legible | Appearance/accessibility fixture | All material/GPU/thermal states |
| AI proposal review is honest | Availability/refusal/cancel/accept/commit state test | Model quality or factual correctness |
| Parent interaction policy is correct | Background interaction and detent UI test | All multi-window/system interruptions |
| Navigation transition is smooth | Animation Hitches/device trace | Every supported device or release version |
| Release route works | Signed archive/TestFlight target/resource proof | App Review or production health |

## Sources

| Topic | Official source |
| --- | --- |
| Navigation structure and path state | [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack), [Understanding the navigation stack](https://developer.apple.com/documentation/swiftui/understanding-the-navigation-stack), and [Navigation](https://developer.apple.com/documentation/swiftui/navigation) |
| Navigation transitions | [NavigationTransition](https://developer.apple.com/documentation/swiftui/navigationtransition), [navigationTransition(_:)](https://developer.apple.com/documentation/swiftui/view/navigationtransition%28_%3A%29), [ZoomNavigationTransition](https://developer.apple.com/documentation/swiftui/zoomnavigationtransition), and [zoom(sourceID:in:)](https://developer.apple.com/documentation/SwiftUI/NavigationTransition/zoom%28sourceID%3Ain%3A%29) |
| Matched transition source | [matchedTransitionSource(id:in:)](https://developer.apple.com/documentation/swiftui/view/matchedtransitionsource%28id%3Ain%3A%29) and [MatchedTransitionSourceConfiguration](https://developer.apple.com/documentation/swiftui/matchedtransitionsourceconfiguration) |
| Modal presentations | [Modal presentations](https://developer.apple.com/documentation/swiftui/modal-presentations), [Presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation), [sheet(item:onDismiss:content:)](https://developer.apple.com/documentation/swiftui/view/sheet%28item%3Aondismiss%3Acontent%3A%29), and [fullScreenCover(item:onDismiss:content:)](https://developer.apple.com/documentation/swiftui/view/fullscreencover%28item%3Aondismiss%3Acontent%3A%29) |
| Sheet sizing and interaction | [PresentationDetent](https://developer.apple.com/documentation/swiftui/presentationdetent), [PresentationSizing](https://developer.apple.com/documentation/SwiftUI/PresentationSizing), [presentationSizing(_:)](https://developer.apple.com/documentation/swiftui/view/presentationsizing%28_%3A%29), [PresentationContentInteraction](https://developer.apple.com/documentation/swiftui/presentationcontentinteraction), and [PresentationBackgroundInteraction](https://developer.apple.com/documentation/swiftui/presentationbackgroundinteraction) |
| Presentation styling/adaptation | [presentationBackground(_:)](https://developer.apple.com/documentation/swiftui/view/presentationbackground%28_%3A%29), [presentationCompactAdaptation(_:)](https://developer.apple.com/documentation/swiftui/view/presentationcompactadaptation%28_%3A%29), [presentationCornerRadius(_:)](https://developer.apple.com/documentation/swiftui/view/presentationcornerradius%28_%3A%29), and [interactiveDismissDisabled(_:)](https://developer.apple.com/documentation/swiftui/view/interactivedismissdisabled%28_%3A%29) |
| Content margins and safe areas | [Layout adjustments](https://developer.apple.com/documentation/swiftui/layout-adjustments), [contentMargins(_:_:for:)](https://developer.apple.com/documentation/SwiftUI/View/contentMargins%28_%3A_%3Afor%3A%29-1lt8b), [ContentMarginPlacement](https://developer.apple.com/documentation/swiftui/contentmarginplacement), and [safeAreaPadding(_:)](https://developer.apple.com/documentation/swiftui/view/safeareapadding%28_%3A%29) |
| Modality and sheets | [Modality](https://developer.apple.com/design/human-interface-guidelines/modality) and [Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets) |
| Liquid Glass | [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views), [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer), and [GlassEffectTransition](https://developer.apple.com/documentation/swiftui/glasseffecttransition) |
| Accessibility and motion | [Motion](https://developer.apple.com/design/human-interface-guidelines/motion), [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility), [Accessible navigation](https://developer.apple.com/documentation/swiftui/accessible-navigation), and [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance) |
