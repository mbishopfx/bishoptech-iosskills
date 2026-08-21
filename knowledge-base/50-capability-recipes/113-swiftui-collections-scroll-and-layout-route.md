# SwiftUI collections, scroll, and adaptive-layout route

## Use this route when

Use this route when an app idea needs a native SwiftUI surface for:

- a structured List, table, outline, lazy stack, grid, or visual collection;
- stable item identity, single/multiple selection, editing, reorder, or
  row-level actions;
- a feed that refreshes, paginates, streams, or loads resources by visibility;
- semantic scroll position, target alignment, paging, or follow-latest behavior;
- safe-area-aware bars, content margins, scroll indicators, or scroll edges;
- compact/regular/Dynamic Type/RTL adaptation;
- a small functional Liquid Glass control layer;
- a reviewable on-device AI result feed;
- accessibility, alternate input, performance, and physical-device proof.

This route composes the existing scroll geometry, custom layout, navigation,
accessibility, Liquid Glass, and Foundation Models routes. It is deliberately
not a catalog of every List or ScrollView modifier.

## Route contract

    user outcome
      -> collection grammar
      -> stable domain identity
      -> selection/editing policy
      -> content state and pagination
      -> viewport state and scroll intent
      -> adaptive layout and safe-area composition
      -> alternate input and accessibility
      -> optional AI proposal
      -> deterministic validation and domain commit
      -> proof packet

Keep these owners separate:

| Concern | Owner |
| --- | --- |
| Item identity | Domain model or feature projection |
| Item order/filter/scope | Feature state |
| Selection | Collection feature |
| Edit/reorder/delete | Domain command |
| Page cursor and request | Repository/feature operation |
| Scroll position/phase/visibility | SwiftUI surface/viewport coordinator |
| Layout branch/column count | View/layout state |
| Material/edge effect | Functional UI layer |
| AI candidate/provenance | AI feature boundary |
| Saved result/revision | Domain store |

## Phase 0: write the product sentence

Write:

    A person can [scan/choose/edit/read/browse] [content] from [context],
    can recover when [load/model/permission/stale] work fails, and can return
    to [selection/reading position] after [refresh/reflow/navigation].

Examples:

- “A person can browse saved recipes in a grid, open one for details, and
  recover from an offline image load without losing the selected recipe.”
- “A person can review generated note summaries, reject a candidate, or
  accept it into the current revision without silently changing the source.”
- “A person can read a live transcript without being auto-scrolled away from
  earlier content, then jump to the latest output explicitly.”

Name the content type and the user outcome. “Build a card feed” is not enough
to choose a container or proof plan.

## Phase 1: choose the collection grammar

| Question | Choose |
| --- | --- |
| Is text scanning, settings, hierarchy, or selection primary? | List/Table/OutlineGroup |
| Is visual discovery primary? | LazyVGrid/LazyHGrid in a ScrollView |
| Is the collection bounded and alignment-sensitive? | Grid/GridRow |
| Is the content a custom one-dimensional feed? | ScrollView + LazyVStack/LazyHStack |
| Is each unit a full-screen page? | ScrollView + paging target behavior |
| Are rows nested? | Hierarchical List or OutlineGroup |
| Do you need a different grammar because of a real product relationship? | Custom Layout after standard options are rejected |

Record why the selected container matches the HIG content recommendation. If
the choice is based on performance, name the workload that was measured.

## Phase 2: define the identity schema

Before writing ForEach, define:

    ItemID: Hashable + Sendable
    Item: Identifiable
    order: feature-owned ordering
    selected IDs: one ID or Set of IDs
    target ID: same stable identity where possible
    candidate ID: separate from source/domain ID

Test identity under:

- insertion before the selected/visible item;
- deletion of the selected/visible item;
- reorder;
- filter and sort changes;
- refresh with updated values;
- pagination overlap;
- partial AI updates;
- layout changes and rotation.

If an ID changes when the title or generated summary changes, stop and repair
the model boundary before adding animation or scroll restoration.

## Phase 3: choose selection and row-action routes

For each action, record the primary and alternate routes:

| Action | Primary | Alternate | Recovery |
| --- | --- | --- | --- |
| Open details | row/card activation | keyboard return, VoiceOver action, deep link | missing item/permission |
| Select one | List selection or explicit control | keyboard/pointer/VoiceOver | item removed |
| Select many | Set of IDs/edit mode | keyboard range/assistive route | apply/cancel |
| Delete | visible destructive route or onDelete | command/context/swipe | undo/confirmation |
| Reorder | edit/reorder route | pointer/keyboard where supported | failed persistence |
| Filter/search | searchable/toolbar/sidebar | deep link or command | no results |
| Retry page | inline retry | refresh/command | offline/error |

Important actions cannot exist only inside a context menu. Keep the same
typed domain command under every supported route.

## Phase 4: model content state and pagination

Use a feature-owned state machine:

    empty
      -> loadingInitial
      -> loaded(items, nextCursor)
      -> loadingNext(cursor)
      -> loadedMore(items, nextCursor)
      -> failed(scope, retry)

Refresh is a deliberate transition that resets the query/scope/cursor
according to product policy. Do not append a refreshed first page to an old
query by accident.

Required pagination rules:

1. one request per feed/cursor/query generation;
2. cancellation when query, scope, or owner disappears;
3. stale responses cannot overwrite a newer generation;
4. duplicate IDs are merged by policy, not appended blindly;
5. ordering is deterministic after concurrent responses;
6. terminal no-more state is distinct from an empty failure;
7. retry is idempotent;
8. offline and permission/model-unavailable paths are visible.

Use a visibility threshold as a signal to ask for the next page. The feature
store decides whether the signal may start work.

## Phase 5: define viewport state

Write down which movement is allowed:

| Viewport event | Allowed behavior |
| --- | --- |
| First appearance | Start at the named default edge/anchor |
| Search result | Move to the matching stable ID |
| Deep link | Reveal the destination only when route resolution succeeds |
| Insert above current item | Preserve current ID or explicit anchor policy |
| New live output | Follow only while follow-latest is true |
| User is browsing older output | Do not move; show new-content affordance |
| Filter removes target | Clear or preserve according to documented policy |
| Rotation/reflow | Keep semantic target visible when possible |
| Restore after relaunch | Restore only if the item and scope are still valid |

Use ScrollPosition for semantic IDs/edges/points and scrollTargetLayout for
the repeating layout. Use ScrollGeometry only to publish bounded projections
such as nearTop, nearBottom, visible IDs, or contentIsShort. Avoid storing a
raw pixel offset as business state.

## Phase 6: choose target behavior

| Content | Behavior |
| --- | --- |
| Reading/feed | Default continuous scroll |
| Full-screen pages | Paging |
| Card carousel | View-aligned |
| Search or selection jump | Explicit semantic ID scroll |
| New-content indicator | Explicit jump-to-latest action |

Test variable heights and long localized/generated content. A screenshot with
three short cards does not prove that a view-aligned or paged surface will
settle correctly with real content.

## Phase 7: choose adaptive layout

Write the alternatives before coding:

    regular width
      -> grid or richer horizontal summary

    compact width
      -> list or one-column card

    large Dynamic Type
      -> wrapped/vertical row with action group below

Choose:

- ViewThatFits for ordered complete alternatives;
- AnyLayout for changing the arrangement of the same subviews;
- containerRelativeFrame for item/page sizing tied to the nearest container;
- standard stack/grid/list before Layout;
- custom Layout only for a documented last-mile relationship.

Every branch must retain item identity, selection, state, primary action,
error, recovery, and accessibility meaning. Test layout changes while the
person is editing or a model request is running.

## Phase 8: compose safe areas and functional edges

Sketch the layers:

    background
      -> collection content
      -> content margins/scroll indicators
      -> safe-area-aware accessory/action bar
      -> toolbar/tab/navigation functional layer
      -> optional coherent scroll-edge effect

Use safeAreaInset for functional content that should reserve space. Use
contentMargins when scroll content and indicators require different insets.
Do not fix content overlap by hiding safe areas until the keyboard, rotation,
tab bar, and accessibility settings have been tested.

For Liquid Glass:

- start with standard system controls and navigation;
- use custom glass only for a compact important functional group;
- use a GlassEffectContainer for related custom glass effects;
- keep text-heavy collection content in the content layer;
- apply one intentional edge effect per scroll view/pane;
- include reduced-transparency and increased-contrast fallback checks.

## Phase 9: add AI only at a named boundary

Choose the AI job:

| Job | Collection presentation |
| --- | --- |
| Summarize source items | Candidate summary row with source link/revision |
| Extract fields | Reviewable structured row with field-level edits |
| Suggest titles/tags | Proposed values beside the original |
| Rank or cluster | Explain the scope and keep manual sort/filter |
| Generate a plan | Previewable staged sections, not auto-committed records |
| Stream a response | Bounded partial row with Cancel and stable request ID |

The Foundation Models route should include:

    capability check
      -> explicit request
      -> LanguageModelSession
      -> optional Generable schema/tool
      -> partial/complete candidate
      -> source/revision check
      -> review
      -> deterministic validation
      -> authorized commit

The model does not choose the collection’s durable identity, page cursor,
selection, or viewport. A generated tool call does not receive side-effect
authority without the feature’s authorization and confirmation boundary.

## Phase 10: create the proof packet

Before calling the route ready, collect:

    source links and API declarations
    named target/SDK/deployment target
    compile log
    unit tests for identity and pagination
    UI tests for selection, viewport, and error paths
    accessibility tree/manual input notes
    compact/regular/Dynamic Type/RTL fixtures
    light/dark/contrast/reduced-effects checks
    performance trace on representative data
    physical-device scrolling/input check
    AI availability/cancel/stale/review/commit evidence
    archive/release target evidence when claimed

Use the [SwiftUI collections, scroll, and layout proof matrix](../60-verification/107-swiftui-collections-scroll-and-layout-proof-matrix.md)
to label each claim. A preview is useful for composition; it does not close
physical input, model readiness, performance, accessibility, or release
claims.

## Route deliverables

The implementation handoff should contain:

- container decision and rejected alternatives;
- ItemID/Item schema and identity tests;
- selection/edit/reorder/delete action matrix;
- pagination state machine and cancellation policy;
- viewport intent table and target behavior;
- adaptive layout alternatives and branch fixtures;
- safe-area/content-margin/edge-layer sketch;
- Liquid Glass use and fallback policy;
- AI candidate schema, source revision, and approval path;
- accessibility/alternate-input plan;
- proof packet with unproven claims explicitly listed.

## Stop conditions

Pause before implementation if:

- an array index or title is being used as durable identity;
- selection, focus, and viewport are one state variable;
- a visibility callback starts unbounded network/model work;
- pagination has no request generation or cancellation policy;
- a background update can auto-scroll a browsing person;
- a compact layout hides the only primary action;
- a same-axis nested scroll view has no documented gesture owner;
- custom glass is applied to content rows without a functional reason;
- AI output can be inserted as saved content without review/revision checks;
- a screenshot is being used as performance, accessibility, physical, or
  release proof.

## Related pages

- [SwiftUI collections, scroll, and adaptive layout](../42-framework-deep-dives/82-swiftui-collections-scroll-and-adaptive-layout.md)
- [Collections, scrolling, and adaptive-layout design](../21-design-deep-dives/110-collections-scroll-and-adaptive-layout-design.md)
- [Scroll geometry and visibility route](../50-capability-recipes/19-scroll-aware-ai-review-and-feed.md)
- [Scroll geometry and position recipes](../70-code-recipes/31-scroll-geometry-and-position-recipes.md)
- [SwiftUI collections, scroll, and layout recipes](../70-code-recipes/125-swiftui-collections-scroll-and-layout-recipes.md)

## Sources

- [List](https://developer.apple.com/documentation/swiftui/list)
- [Lists](https://developer.apple.com/documentation/swiftui/lists)
- [Grouping data with lazy stack views](https://developer.apple.com/documentation/swiftui/grouping-data-with-lazy-stack-views)
- [LazyVStack](https://developer.apple.com/documentation/swiftui/lazyvstack)
- [LazyVGrid](https://developer.apple.com/documentation/swiftui/lazyvgrid)
- [Grid](https://developer.apple.com/documentation/swiftui/grid)
- [Table](https://developer.apple.com/documentation/swiftui/table)
- [OutlineGroup](https://developer.apple.com/documentation/swiftui/outlinegroup)
- [ForEach](https://developer.apple.com/documentation/swiftui/foreach)
- [Scroll views](https://developer.apple.com/documentation/swiftui/scroll-views)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [ScrollGeometry](https://developer.apple.com/documentation/swiftui/scrollgeometry)
- [onScrollGeometryChange(for:of:action:)](https://developer.apple.com/documentation/swiftui/view/onscrollgeometrychange%28for%3Aof%3Aaction%3A%29/)
- [onScrollVisibilityChange(threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrollvisibilitychange%28threshold%3A_%3A%29)
- [onScrollTargetVisibilityChange(idType:threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrolltargetvisibilitychange%28idtype%3Athreshold%3A_%3A%29)
- [scrollTargetLayout(isEnabled:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetlayout%28isenabled%3A%29)
- [scrollTargetBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetbehavior%28_%3A%29)
- [PagingScrollTargetBehavior](https://developer.apple.com/documentation/swiftui/pagingscrolltargetbehavior)
- [ViewAlignedScrollTargetBehavior](https://developer.apple.com/documentation/swiftui/viewalignedscrolltargetbehavior)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [containerRelativeFrame(_:alignment:_:)](https://developer.apple.com/documentation/swiftui/view/containerrelativeframe%28_%3Aalignment%3A_%3A%29)
- [safeAreaInset(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [safeAreaPadding(_:)](https://developer.apple.com/documentation/swiftui/view/safeareapadding%28_%3A%29)
- [contentMargins(_:_:for:)](https://developer.apple.com/documentation/swiftui/view/contentmargins%28_%3A_%3Afor%3A%29-1lt8b)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Collections](https://developer.apple.com/design/human-interface-guidelines/collections)
- [Lists and tables](https://developer.apple.com/design/human-interface-guidelines/lists-and-tables)
- [Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
- [Swift concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
