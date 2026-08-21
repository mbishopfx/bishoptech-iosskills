# Capability recipe: scroll-aware AI review and feed

## User outcome

Build a long-form review, transcript, feed, or generated document that keeps the person’s place, avoids surprise scrolling, bounds viewport work, and exposes AI actions without confusing visibility with approval.

## Composition

    source or feed data
    -> stable item/section IDs
    -> ScrollView/List/TextEditor
    -> scroll target layout
    -> semantic ScrollPosition
    -> projected geometry/visibility/phase state
    -> bounded resource/model work
    -> review action or system handoff

| Layer | Responsibility | Ownership |
| --- | --- | --- |
| Content model | Record source, revision, section/item IDs, freshness, and errors | Domain |
| Scroll model | Position, follow mode, visible IDs, phase, pending content | SwiftUI/UI state |
| Resource work | Prefetch, playback, local indexing, or contextual proposal | Cancellable service |
| AI proposal | Summary, rewrite, annotation, or explanation | Model route; never approved truth |
| Review action | Apply, edit, copy, export, retry, discard, or return | User-controlled UI |
| System surface | Share, widget, App Intent, Live Activity, or handoff projection | Explicit projection target |

## State model

    content: loading | partial | ready | stale | failed
    position: initial | userPositioned | programmatic | missing
    follow: followingBottom | browsing | paused | unavailable
    visibility: none | some(ids) | all(ids)
    phase: idle | interacting | decelerating | animating
    proposal: none | queued | generating | ready | stale | rejected | canceled
    handoff: none | presenting | completed | failed

Position and follow state are not domain truth. A person can browse without approving a document, and a cell can be visible without being understood.

## Build order

1. Define stable IDs and the content revision.
2. Choose List, ScrollView/lazy stack, TextEditor, or a media-specific container.
3. Add the base composition with no scroll-driven visual effects.
4. Add scrollTargetLayout and semantic position only where the product needs it.
5. Project ScrollGeometry to a few Equatable state values.
6. Add visibility-triggered work only with cancellation, checkpoint, and fallback.
7. Add follow-bottom or programmatic jumps with an explicit intent policy.
8. Add AI generation from user action or a documented bounded trigger.
9. Add a reviewable result and apply boundary.
10. Add glass/edge treatment and scroll transitions after the semantic route works.
11. Test input, accessibility, long text, source updates, and physical behavior.

## Follow-bottom policy

Use a small explicit policy:

    if followMode == followingBottom
        keep the latest approved/displayed section visible
    else
        preserve user position
        increment pendingNewContent
        show an accessible return action

Switch to browsing when the person positions the scroll view away from the bottom. Switch back only after an explicit action or a product-defined “resume following” gesture. Do not infer follow mode from a fixed offset alone when content insets and Dynamic Type can change.

## Geometry projection

Project geometry to product state:

    nearTop: visibleRect.minY <= contentInsets.top + threshold
    nearBottom: visibleRect.maxY >= contentSize.height - bottomThreshold
    contentHeightBucket: bounded bucket for diagnostics only

Use nearTop/nearBottom to update a small view model or action visibility. Do not pass raw geometry into a model prompt, persist it as user meaning, or use it to select arbitrary layout code.

## Visibility-triggered work

For each visible item:

    visibility enters
    -> check authorization and freshness
    -> start bounded cancellable work
    -> checkpoint partial result
    -> cancel/pause when hidden
    -> resume or use cached result when visible again

Examples include:

- prefetching a local thumbnail or audio segment;
- loading a Core ML/Vision request only for a selected visible item;
- generating a short explanation after a user taps an item;
- updating a local “current section” indicator;
- preparing a share/export representation.

Do not run an expensive model call for every cell merely because the user flings through a feed. Prefer an explicit action or a debounced, privacy-reviewed route with a clear budget.

## Programmatic scroll reasons

Every programmatic scroll should have a reason:

    searchResult
    selection
    focus
    applyResult
    restorePosition
    returnToNewContent

Log the reason without sensitive text. Use the smallest scroll that makes the relevant content visible, preserve surrounding context, and avoid chaining a jump into a model call without user intent.

## Reviewable AI actions

For a visible section or selected range:

    user intent
    -> source revision capture
    -> bounded request
    -> proposal
    -> text/selection review
    -> apply or discard

If the user scrolls away while a proposal is generating, keep the proposal tied to its source ID and revision. If that section changes, mark it stale. The proposal can be reopened, but it must not silently apply to a different section.

## Glass action shell

Use a bounded glass group for:

- return-to-new-content;
- apply/discard/retry actions;
- current section/status;
- a small playback/control group.

Keep the group out of the content’s measured reading region using the shell’s safe-area ownership. When reduced transparency is active, use standard material or an opaque background with the same labels, state, and hit regions.

## Fallback matrix

| Condition | Route |
| --- | --- |
| No stable IDs | Use simple content order and disable semantic restore until IDs exist |
| Content changes during generation | Mark proposal stale; keep current view and source |
| User scrolls away during stream | Stop automatic scroll; show pending count/return action |
| Visibility work canceled | Use cached/partial result or a clear unavailable state |
| Model unavailable | Keep browsing/review usable without the AI action |
| Large Dynamic Type | Allow variable heights and stack actions |
| Right-to-left | Test leading/trailing, selection, and section jumps |
| Reduce Motion | Remove scroll transitions and preserve state |
| Keyboard visible | Keep focus and commit action reachable |
| Physical performance issue | Reduce effects/work; keep semantic content intact |

## Proof packet

Capture content revision, stable IDs, initial/restore position, follow-mode transitions, geometry projection, visibility events, cancellation/checkpoint state, model request/proposal/review/apply state, and the actual system projection if any. Add accessibility and physical-device evidence for the named target.

## Sources

- [Scroll views](https://developer.apple.com/documentation/swiftui/scroll-views)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [ScrollGeometry](https://developer.apple.com/documentation/swiftui/scrollgeometry)
- [onScrollGeometryChange(for:of:action:)](https://developer.apple.com/documentation/swiftui/view/onscrollgeometrychange%28for%3Aof%3Aaction%3A%29/)
- [onScrollVisibilityChange(threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrollvisibilitychange%28threshold%3A_%3A%29)
- [onScrollPhaseChange(_:)](https://developer.apple.com/documentation/swiftui/view/onscrollphasechange%28_%3A%29)
- [ScrollTargetBehavior](https://developer.apple.com/documentation/swiftui/scrolltargetbehavior)
- [scrollTransition(_:axis:transition:)](https://developer.apple.com/documentation/swiftui/view/scrolltransition%28_%3Aaxis%3Atransition%3A%29)
- [scrollInputBehavior(_:for:)](https://developer.apple.com/documentation/swiftui/view/scrollinputbehavior%28_%3Afor%3A%29)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Human Interface Guidelines: Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
