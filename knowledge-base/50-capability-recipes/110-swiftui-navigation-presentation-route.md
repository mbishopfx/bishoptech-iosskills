# SwiftUI navigation and presentation route

## Route contract

Use this route to turn an app idea into a typed NavigationStack, a matched
navigation transition, a focused sheet/full-screen task, or a reviewable
on-device AI presentation. Keep presentation state, route identity, domain
truth, and system delivery separate.

This route is for a named target. It does not claim that a preview or
simulator run proves public Universal Links, Handoff, physical interaction,
accessibility completion, or release behavior.

Related pages:

- [SwiftUI navigation transitions and presentation](../42-framework-deep-dives/79-swiftui-navigation-transitions-and-presentation.md)
- [Navigation transitions and presentation design](../21-design-deep-dives/107-navigation-transitions-and-presentation-design.md)
- [SwiftUI navigation and presentation proof matrix](../60-verification/104-swiftui-navigation-presentation-proof-matrix.md)
- [SwiftUI navigation and presentation recipes](../70-code-recipes/122-swiftui-navigation-presentation-recipes.md)
- [Universal Links, Handoff, and scene delivery](../42-framework-deep-dives/72-universal-links-handoff-and-scene-delivery.md)

## Route map

    user outcome
      -> hierarchy decision
      -> typed route/presentation state
      -> source identity and namespace
      -> navigation/presentation implementation
      -> sizing/background/interaction policy
      -> AI review and dismissal policy
      -> accessibility/adaptation proof
      -> deep-link/system/device/release proof

## Phase 0: choose navigation or presentation

Ask:

| Question | Route |
| --- | --- |
| Is this part of the app’s durable information hierarchy? | NavigationStack path |
| Is it a short decision that returns to the current context? | Sheet |
| Is it long, immersive, or multistep? | Full-screen cover or a dedicated navigation hierarchy |
| Is it supplementary while the parent remains meaningful? | Popover/nonmodal presentation where supported |
| Does an item’s presence define what is presented? | item-based binding |
| Is there only a presentation flag with no item identity? | Boolean binding |

Do not start by selecting a transition. Start by choosing the task boundary.

## Phase 1: define typed state

Create two different state families:

    enum Route: Hashable, Codable {
        case inbox
        case detail(recordID: UUID)
        case review(proposalID: UUID)
    }

    enum Presentation: Identifiable {
        case review(proposalID: UUID)
        case editor(recordID: UUID)
    }

For each value, record:

- owner and lifetime;
- stable identity and Codable policy;
- source of truth;
- what happens if the record disappears;
- whether the state can be restored;
- whether a deep link can set it;
- whether presentation dismissal cancels, saves, or preserves work.

Keep a full domain model out of the path. Resolve it at the destination.

## Phase 2: build the NavigationStack route

1. Store the path in the App/Scene/feature owner with the correct lifetime.
2. Use lightweight route values.
3. Map each route type with navigationDestination.
4. Re-check current authorization and freshness when resolving.
5. Handle deleted/stale/unavailable data as a visible destination state.
6. Test back navigation, programmatic pushes, restoration, and deep links.

For heterogeneous routes, use NavigationPath only when its type erasure is
useful. Keep homogeneous arrays or custom route enums easier to inspect and
test where possible.

## Phase 3: add matched navigation identity

For a list card to detail:

1. create a Namespace with a lifetime covering source and destination;
2. apply matchedTransitionSource to the source using the stable record ID;
3. navigate by value;
4. apply navigationTransition(.zoom(sourceID:in:)) to the destination;
5. place the transition on the destination outside layout containers;
6. add automatic/identity fallback for platform or accessibility policy;
7. verify the route still works when the source is no longer visible.

Use matchedGeometryEffect instead when the two representations are in the same
view hierarchy and the product is not navigating through the app stack.

## Phase 4: model presentation

Prefer item presentation for a domain-identified task:

    nil -> no review surface
    review(proposalID) -> resolve current proposal and present
    applying -> keep review surface or show explicit progress
    saved/failed -> show result, then dismiss or remain by policy

When the user dismisses:

- reconcile the proposal/draft with the model;
- cancel view-scoped work if it should not survive;
- leave explicit model-owned work running only when product behavior requires;
- prevent late results from changing a new presentation;
- preserve unsaved source or ask before discarding.

Use the dismiss environment action from inside the presentation. The action
closes the presentation; it does not decide whether a domain write succeeded.

## Phase 5: choose detents and sizing

1. choose a small set of meaningful detents;
2. use a selection binding only when the app genuinely needs current detent
   state;
3. choose presentationContentInteraction when scroll/resizing competition is
   meaningful;
4. show a drag indicator when resize/dismissal is not obvious;
5. use system PresentationSizing policies before custom sizing;
6. add content margins for scroll content/indicators rather than offsets;
7. test keyboard, Dynamic Type, localization, iPad split view, orientation,
   and compact adaptation.

Avoid a fixed height that clips the action or hides the state. A large text
fixture is part of the presentation route, not a late polish task.

## Phase 6: set parent interaction and dismissal

Choose:

- background interaction automatic, disabled, enabled, or up through a detent;
- interactive dismissal allowed or disabled;
- explicit Cancel/Done/Back policy;
- unsaved-change confirmation;
- whether the parent can receive input while the presentation is compact.

Use disabled background interaction for a review/apply task that must be
resolved before the parent can change. Use enabled/up-through only for a
supplementary surface with safe, independent parent actions.

## Phase 7: connect an AI review route

    source record
      -> device/model/permission availability
      -> generating task
      -> typed candidate/refusal/error
      -> review presentation
      -> edit/accept/reject
      -> validation/authorization
      -> applying
      -> saved/stale/failed

The presentation can display generating, proposal, or applying. The domain
model decides saved or failed. If the user dismisses during generation, cancel
the view task or deliberately transfer to a model-owned task. Reject late
results using request identity/revision.

Use a sheet for a bounded proposal decision, full screen for a rich source or
multistep editor, and NavigationStack for a durable review history. Always
keep a manual fallback for model unavailable/refused/unsupported input.

## Phase 8: make route delivery converge

Universal Links, Handoff, notifications, widgets, App Intents, and scene
delivery should converge on the same typed Route/Presentation reducer:

    external payload -> validate/authorize/freshness
      -> Route or Presentation
      -> current model lookup
      -> visible state

Do not trust an external URL, activity, or model-generated route as domain
authority. Re-check the current user/account, record availability, and
permission before presenting a sensitive review screen.

## Phase 9: proof

| Proof layer | Required run |
| --- | --- |
| Compile | Named target, selected SDK, availability fallbacks |
| UI | Push, pop, sheet, cover, detents, dismiss, background interaction |
| Identity | Source/destination zoom or geometry relationship |
| Async | Cancel/dismiss/generation/stale-result behavior |
| Accessibility | VoiceOver, Reduce Motion, Dynamic Type, contrast/transparency, alternate input |
| Deep link | Cold/warm path delivery and invalid payload fallback |
| Physical/system | Target device, Safari/source app, Handoff, widget/App Intent/system surface as applicable |
| Release | Signed archive, target/resource/capability/privacy inspection |

## Acceptance checklist

- [ ] The task boundary is navigation, sheet, cover, popover, or system surface.
- [ ] Route values are lightweight, stable, and restorable where required.
- [ ] Presentation bindings are not domain truth.
- [ ] Zoom source IDs derive from stable record identity.
- [ ] Destination transition is applied at the correct hierarchy level.
- [ ] Detents, sizing, background interaction, and adaptation are intentional.
- [ ] Dismissal protects drafts and has a cancellation policy.
- [ ] AI proposal/generating/applying/saved/failed states are distinct.
- [ ] Universal Links/Handoff/App Intent payloads are validated before routing.
- [ ] Reduce Motion and VoiceOver preserve the workflow.
- [ ] Long text, keyboard, iPad, localization, and compact layouts work.
- [ ] Physical/system/release proof is recorded separately from previews.

## Sources

- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [Navigation](https://developer.apple.com/documentation/swiftui/navigation)
- [Understanding the navigation stack](https://developer.apple.com/documentation/swiftui/understanding-the-navigation-stack)
- [NavigationTransition](https://developer.apple.com/documentation/swiftui/navigationtransition)
- [matchedTransitionSource(id:in:)](https://developer.apple.com/documentation/swiftui/view/matchedtransitionsource%28id%3Ain%3A%29)
- [ZoomNavigationTransition](https://developer.apple.com/documentation/swiftui/zoomnavigationtransition)
- [Modal presentations](https://developer.apple.com/documentation/swiftui/modal-presentations)
- [Presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [PresentationSizing](https://developer.apple.com/documentation/SwiftUI/PresentationSizing)
- [contentMargins(_:_:for:)](https://developer.apple.com/documentation/SwiftUI/View/contentMargins%28_%3A_%3Afor%3A%29-1lt8b)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Universal Links, Handoff, and scene delivery](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Modality](https://developer.apple.com/design/human-interface-guidelines/modality)
- [Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets)
