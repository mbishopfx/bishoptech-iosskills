# SwiftUI collections, scrolling, and adaptive layout

## Purpose

Collection interfaces are where a native SwiftUI screen can become either
calm and platform-appropriate or fragile and over-engineered. The container,
identity model, viewport, loading policy, and material layer each solve a
different problem:

    semantic collection
      -> stable identity and selection
      -> content state and domain pagination
      -> viewport and scroll intent
      -> adaptive layout and safe-area composition
      -> system input and accessibility
      -> optional on-device AI proposal
      -> proof

This deep dive covers List, ScrollView, lazy stacks and grids, Grid, Table,
hierarchical collections, scroll position and geometry, visibility and
pagination, ViewThatFits, AnyLayout, container-relative sizing, safe areas,
content margins, Liquid Glass edges, and AI result feeds. It complements the
existing scroll geometry and custom layout pages by making collection
ownership and pagination explicit.

The exact declarations and availability must be compiled against the selected
Xcode, SDK, and deployment target. Apple documentation may contain beta,
platform-specific, or future-release symbols. A documentation page is a
design reference, not evidence that a target can use every declaration.

## The four-state model

Do not store every collection concern in one observable object or one array.
At minimum, keep these state families distinct:

| State family | Examples | Owner |
| --- | --- | --- |
| Collection content | items, sections, groups, children, loading/error state | Feature store or view model |
| Identity and selection | item IDs, selected ID, selected set, edit mode | Collection feature |
| Domain pagination | cursor, page number, has-more, in-flight request, retry | Repository/feature operation |
| Viewport | current item ID, edge, near-top, near-bottom, phase, follow mode | SwiftUI surface or viewport coordinator |
| Presentation | layout mode, column count, toolbar/tab/material state | SwiftUI view state |
| AI proposal | source revision, candidate ID, partial output, approval state | AI feature boundary |

The viewport may request more content, but it does not own the items. A
visible item may be a reason to prefetch; it is not proof that a person read,
approved, purchased, completed, or accepted that item.

## Choose the container by the task

Start with the semantic and performance contract, not the visual shape.

| Product need | First container | Why | Escalate or change when |
| --- | --- | --- | --- |
| Text-heavy, platform-structured rows | List | Supplies a platform list surface, sections, row actions, refresh, and selection routes | The required layout is a genuinely visual collection or a custom feed |
| Large one-dimensional custom feed | ScrollView with LazyVStack or LazyHStack | Separates scrolling from a lazy repeating layout and supports custom row composition | The content is small enough for a regular stack, or a list gives better platform behavior |
| Image-heavy vertical collection | ScrollView with LazyVGrid | Gives a two-dimensional, vertically growing lazy grid | Text scanning, row selection, or platform list behavior is primary |
| Small, alignment-sensitive two-dimensional content | Grid and GridRow | Renders all children and can calculate shared row/column alignment | Profiling shows that initial creation is costly for a large scrollable grid |
| Large two-dimensional collection | LazyVGrid or LazyHGrid | Creates cells as needed | Exact shared alignment is more important than initial loading cost |
| Structured multi-column data | Table | Represents columns and sortable or selectable tabular content on supported platforms | The content is primarily visual media rather than text/data |
| Hierarchical rows | List with children or OutlineGroup | Gives disclosure and hierarchy semantics | The hierarchy needs a bespoke canvas or graph interaction |
| Static bounded content | VStack/HStack/Grid | All children are known and layout can be direct | Profiling shows the view tree is too large |

Apple’s SwiftUI guidance describes List as a single-column data container that
can support selection, refresh, sections, hierarchy, and editing. Lazy stacks
and lazy grids do not provide scrolling on their own; place them inside a
ScrollView. A regular Grid creates its children immediately, while a lazy grid
creates children as needed. Start with the simplest container that preserves
the interaction contract, then profile before changing to a lazy variant.

### List is more than a vertical VStack

List is appropriate when the person is scanning text or settings, selecting
rows, editing order, deleting, refreshing, or navigating a hierarchy. It
also allows SwiftUI to choose platform-appropriate row and list presentation.
Use listStyle to express a supported style; do not rebuild a list from
rounded rectangles only to imitate a system surface.

For a single-selection list, bind the selection to the item ID type. For
multiple selection, bind a Set of IDs and provide a clear edit-mode or
keyboard/pointer route where required by the platform. The selected value is
not the full model and should not become the domain mutation by itself:

    row tap
      -> selected item ID
      -> feature command or navigation
      -> domain read/mutation

Editable List initializers and the onDelete/onMove routes are useful when the
collection itself is the editable surface. The mutation still belongs in the
feature or model owner so a drag reorder, keyboard command, context action,
and system route cannot disagree.

### Lazy stacks and lazy grids are not a loading policy

Lazy creation limits when SwiftUI creates child views. It does not
automatically make image decoding, network work, model requests, database
fetches, or tasks safe. A row must own cancellation and the feature must
bound work:

    row becomes visible
      -> optional resource request
      -> cancellation when no longer relevant
      -> cache or discard by policy

Use Instruments and a representative data set to decide whether the lazy
container improves the named workload. Do not claim “lazy” proves memory,
thermal, or scrolling performance.

### Grid versus LazyVGrid

Grid is useful when shared column alignment is part of the meaning and the
number of children is bounded. LazyVGrid is useful for a large scrollable
collection where initial creation of every cell is costly. Lazy layout can
trade some layout knowledge for on-demand work, so verify variable-height
cells, long text, Dynamic Type, and a changing column count.

For a media collection, give the item a stable identity and an accessible
label. Do not use an image-only grid when the person needs to compare
long-form textual information; a list or table is usually easier to scan.

## Stable identity is the collection contract

ForEach, List, lazy containers, selection, scroll targets, transitions, and
AI result updates all depend on identity. Choose an ID that remains stable
for the lifetime of the domain item:

    domain record identity
      -> collection ID
      -> selection ID
      -> scroll target ID
      -> task/cache key

An ID should not change because a title, sort order, filter, generated
summary, or presentation layout changed. Avoid array indices as IDs when
items can be inserted, deleted, filtered, or reordered. If the data has no
stable identity, create one in the feature/model boundary and keep it with
the item; do not derive it from a transient row position.

For generated candidates, use a candidate ID and source revision. A partial
stream update should replace the candidate content under the same candidate
identity, not create a new row for every partial token. If the candidate is
accepted, the committed domain record receives its own durable identity.

### Identity and filtering

When a filter hides the current item, decide explicitly:

- preserve the selected ID but show that it is not in the current result;
- clear selection because the task is scoped to visible results;
- navigate to a detail screen that is independent of the filtered collection;
- keep a viewport anchor only if the anchor item still exists.

Do not let SwiftUI’s reconciliation choose a business outcome by accident.
Record the policy in tests for insert, delete, reorder, sort, filter, and
refresh.

## Selection, editing, and row actions

Treat selection as a user-facing state with a visible and accessible
representation. A row can be:

    unselected
    selected
    focused
    editing
    disabled
    loading
    stale

These states can overlap. Selection is not focus, and focus is not approval.
VoiceOver focus, keyboard focus, pointer hover, and a selected item should
not be collapsed into one Boolean.

Use the semantic row action that matches the task:

| Need | Route |
| --- | --- |
| Navigate to details | NavigationLink or explicit selection-to-navigation |
| Choose one item | List selection or a Picker-like route |
| Choose many | Multiple selection with Set of IDs |
| Delete | onDelete or a visible destructive action with confirmation policy |
| Reorder | onMove/edit actions or a platform-appropriate drag route |
| Secondary item actions | swipeActions or contextMenu, with a visible alternative for important tasks |
| Refresh | refreshable with an async operation and visible failure/retry state |

Swipe actions and context menus are supplemental. Do not make the only route
to a primary task a long press or a hidden swipe. Preserve the same domain
command under the row, toolbar, menu, command, keyboard, and accessibility
routes.

## Viewport state and scroll intent

ScrollPosition describes semantic scroll location. It can target an item ID,
edge, point, or axis position. For ID-based positions, put scrollTargetLayout
on the repeating layout so SwiftUI knows which child views are targets.
ScrollPosition can also expose the current view ID and whether the user
positioned the view.

Use semantic intent for programmatic motion:

| Intent | Example |
| --- | --- |
| Search result | Scroll the matching ID into view |
| Restore | Return to the last domain item after relaunch or rotation |
| New output | Follow bottom only while the person is already following |
| Error recovery | Reveal the first actionable error |
| Navigation | Place the selected destination in context |
| User browsing | Do not move the viewport because background data arrived |

Avoid a timer or every-array-update auto-scroll. A stream can append content
without taking control away from a person who is reading earlier content.

### ScrollGeometry is a projection boundary

ScrollGeometry contains bounds, container size, content insets, content
offset, content size, and visible rect. Geometry changes frequently. Use
onScrollGeometryChange to transform that information into a small Equatable
value such as:

    nearTop
    nearBottom
    visibleBucket
    headerIsPast
    contentIsShort

Keep the action narrow. Do not write raw offsets into broad application
state or cause a large view tree to update on every pixel. A viewport
coordinator can publish a Boolean, enum, or bounded set of IDs to the feature.

### Visibility is a trigger, not a conclusion

onScrollVisibilityChange and onScrollTargetVisibilityChange can support
prefetch, media preparation, analytics, and bounded AI work. Use a stable ID,
an explicit threshold, and cancellation/cache policy. Visibility alone does
not prove that the person saw, understood, endorsed, or completed the item.

For resource work:

    target becomes visible
      -> check capability and cache
      -> start cancellable bounded work
      -> publish result for the same ID
      -> cancel or deprioritize when policy says it is no longer relevant

Do not launch one unbounded model request for every row in a fast fling.

## Scroll targets, paging, and nested scrolling

scrollTargetBehavior controls where a scroll settles. Paging behavior aligns
to container-based geometry. View-aligned behavior settles on individual
views configured by scrollTargetLayout. Choose the behavior from the content
contract:

- full-screen pages or deliberate chunks: paging;
- horizontally browsable cards: view-aligned;
- ordinary reading/feed content: default continuous scrolling.

Page controls can clarify page-by-page movement when the product actually has
pages. Avoid presenting a page control and a same-axis scroll indicator as
redundant competing signals.

Avoid nesting scroll views with the same orientation. A horizontal carousel
inside a vertical feed can be appropriate, but it needs bounded height,
clear focus/gesture behavior, and accessibility labels. A vertical scroll
inside a vertical scroll often creates gesture, keyboard, indicator, and
viewport ownership problems.

## Domain pagination and cancellation

Pagination is a data operation, not a scroll modifier. Model it explicitly:

    enum PageState {
        case idle
        case loading(cursor: String?)
        case loaded(nextCursor: String?)
        case failed(message: String, retryCursor: String?)
    }

Use the actual project’s typed cursor or page token rather than a generic
integer if the backend supports cursors. Protect the operation with:

- one in-flight request per feed and cursor;
- request identity or generation so stale responses cannot append to a new
  query;
- cancellation when the query/filter/scope changes;
- deduplication by stable item ID;
- ordering rules for out-of-order responses;
- explicit has-more and terminal-empty states;
- retry that does not duplicate existing rows;
- offline and model-unavailable fallback;
- refresh that resets the cursor intentionally.

The UI may ask for the next page when the last visible target crosses a
threshold. The feature decides whether the request is allowed. A visibility
callback must not bypass authorization, privacy, network, or rate policy.

## Adaptive layout and container-relative sizing

Use the environment and container proposal to adapt. Avoid hard-coded device
width checks when a layout container can express the relationship.

### ViewThatFits

ViewThatFits evaluates its children in order and chooses the first child whose
ideal size fits on the constrained axes. Put alternatives in preference
order, usually from richer to more compact:

    full action group
      -> compact action group
      -> single primary action plus Menu

Every branch must preserve the task, label meaning, state, and recovery path.
ViewThatFits is not permission to hide an essential control at compact sizes.
Test long localized labels and largest Dynamic Type because those inputs can
change which branch fits.

### AnyLayout

AnyLayout type-erases a Layout so the container can change between horizontal,
vertical, grid, or custom layout while preserving the identity of subviews.
Use it when the same content should remain the same content while the
arrangement changes. Do not use it to hide incompatible domain hierarchies.
Test focus, draft text, selection, and async row state across the transition.

### containerRelativeFrame

containerRelativeFrame sizes a view relative to the nearest container, which
can be a window, navigation column, tab, ScrollView, or List. It accounts for
safe-area insets in the container’s available size. The count/span form is
useful for keeping multiple cards visible without manually measuring the
screen:

    container width
      -> desired count and spacing
      -> item span
      -> card width
      -> stable content hierarchy

Use this relationship for carousel cards and full-width pages, then verify
variable text, Dynamic Type, split view, rotation, and pointer/keyboard input.

### Custom Layout remains a last-mile tool

Use Layout when the product has a real arrangement not expressible by the
standard containers. The measure/place contract must handle zero, infinity,
unspecified, and finite proposals. A custom layout should not become the
source of collection identity, data loading, or domain mutation.

## Safe areas, content margins, and edge composition

Safe-area composition is part of the collection contract:

    background/content layer
      -> scrollable content
      -> safe-area/content margin policy
      -> functional edge controls
      -> keyboard and system inset behavior

Use safeAreaInset for a bar or accessory that must sit beside the modified
content and cause the content region to account for it. Use safeAreaPadding
when the content needs additional breathing room inside the safe area. Use
contentMargins to target scroll content and scroll indicators separately when
the view needs that distinction. Do not solve every overlap with ignoresSafeArea.

Test:

- top and bottom system areas;
- keyboard region;
- tab bar and toolbar;
- safe-area action bars;
- scroll indicators after clipping;
- rotation and split view;
- Dynamic Type and long labels;
- right-to-left leading/trailing edges.

## Liquid Glass and scroll edges

Apple describes Liquid Glass as a functional layer for controls and
navigation. Keep the content layer readable and let the system components
provide their native appearance where possible. Custom glass should be
limited to important controls or compact control groups, not every card and
row.

For collections adjacent to floating controls:

- use the appropriate scroll edge effect to clarify where content meets the
  functional control layer;
- apply one coherent edge effect per scroll view/pane;
- use a soft edge effect for the usual iOS/iPadOS transition and reserve a
  harder boundary for cases that need stronger separation;
- keep content visible and legible beneath the edge;
- provide reduced-transparency and increased-contrast fallbacks;
- avoid stacking a custom opaque overlay, a glass group, and a scroll-edge
  effect for the same boundary.

Clear Liquid Glass is for visually rich backgrounds where showing the content
through matters; regular is the safer choice when text or changing content
needs stronger legibility. A glass group does not turn a collection row into
a system control. Keep the row’s semantic label, selection, actions, and
focus independent of the material.

## Accessibility and alternate input

Collections need a stable semantic order, not just a visually attractive
grid. Verify:

- every row/card has a useful label and value;
- selection is exposed as selection, not only color or a border;
- destructive and secondary actions have discoverable labels;
- VoiceOver can move through sections, rows, and actions;
- Voice Control can address visible controls by name;
- Switch Control and Full Keyboard Access can complete the core task;
- hardware keyboard arrows, return, escape, and delete have predictable
  routes where supported;
- pointer hover/focus does not replace selection;
- Dynamic Type reflows cells and keeps the primary action reachable;
- right-to-left layout uses leading/trailing semantics;
- Reduce Motion and Reduce Transparency preserve state meaning;
- content does not disappear solely because a custom layout branch is small.

For grids, announce enough context to distinguish an item without forcing the
person to infer its row/column from visuals. For a multiselect list, expose
selection count and a clear action to finish or apply. For a feed, do not
move accessibility focus on every streamed partial update.

## On-device AI result feeds

Foundation Models can produce text, structured Generable values, streamed
partial output, and tool-assisted results. A collection is a useful
presentation surface for those results, but the model should not own the
collection’s durable truth.

Use this boundary:

    source record + source revision
      -> explicit AI request
      -> capability/language/model check
      -> cancellable session
      -> typed candidate or partial candidate
      -> user review
      -> deterministic validation
      -> authorized commit
      -> durable collection item

Each candidate row should carry:

- stable candidate ID;
- source record ID and revision;
- generation/request ID;
- partial/complete state;
- provenance and limitations appropriate to the feature;
- Accept, Edit, Reject, Retry, and Cancel routes as relevant;
- a stale policy if the source changed while generation ran.

For an AI feed, separate:

    model output order
      from
    domain sort/order
      from
    viewport position

Do not use model output text as an identity key. Do not insert a partial
candidate into a committed list until the feature’s review/commit boundary is
crossed. If Foundation Models is unavailable, provide a manual path or a
truthful unavailable state. If a tool can cause side effects, place
authorization and confirmation outside the model’s generated arguments.

## Proof boundary

| Claim | Needed evidence |
| --- | --- |
| The container compiles | Named target, SDK/deployment target, imports, compile log |
| IDs survive updates | Tests for insert/delete/reorder/filter/refresh |
| Selection behaves | UI test plus accessibility tree and input routes |
| Viewport restores | UI test for ID/edge/size changes, then physical device where claimed |
| Pagination is safe | Deterministic cursor, cancellation, deduplication, stale-response fixtures |
| Visibility work is bounded | Threshold/cancel/cache tests and a representative performance trace |
| Layout adapts | Compact/regular, Dynamic Type, localization, RTL, keyboard, split view |
| Glass edge is legible | Light/dark/contrast/reduced-transparency device checks |
| Scrolling feels native | Physical touch/pointer/keyboard/accessibility run |
| AI result is trustworthy | Source revision, candidate, unavailable/canceled/stale/review/commit fixtures |
| Performance is acceptable | Instruments or XCTest performance on a named workload and device |
| Release route is ready | Archive, packaged target/configuration, and intended install/system proof |

A preview or simulator screenshot can show composition and deterministic
state. It does not prove physical scrolling, touch feel, pointer/keyboard
behavior, accessibility completion, model availability, performance,
thermal behavior, or release delivery.

## Related pages

- [Scroll geometry and position](../10-swiftui/11-scroll-geometry-and-scroll-position.md)
- [Custom layouts and proposals](../10-swiftui/09-custom-layouts-and-proposals.md)
- [Scroll-driven native surfaces](../21-design-deep-dives/16-scroll-driven-native-surfaces.md)
- [Custom layout and adaptive glass recipes](../70-code-recipes/29-custom-layout-and-adaptive-glass-recipes.md)
- [Scroll geometry and position recipes](../70-code-recipes/31-scroll-geometry-and-position-recipes.md)
- [SwiftUI collections, scroll, and layout route](../50-capability-recipes/113-swiftui-collections-scroll-and-layout-route.md)
- [SwiftUI collections, scroll, and layout proof matrix](../60-verification/107-swiftui-collections-scroll-and-layout-proof-matrix.md)

## Sources

- [List](https://developer.apple.com/documentation/swiftui/list)
- [Lists](https://developer.apple.com/documentation/swiftui/lists)
- [Grouping data with lazy stack views](https://developer.apple.com/documentation/swiftui/grouping-data-with-lazy-stack-views)
- [LazyVStack](https://developer.apple.com/documentation/swiftui/lazyvstack)
- [LazyVGrid](https://developer.apple.com/documentation/swiftui/lazyvgrid)
- [Grid](https://developer.apple.com/documentation/swiftui/grid)
- [GridRow](https://developer.apple.com/documentation/swiftui/gridrow)
- [Table](https://developer.apple.com/documentation/swiftui/table)
- [OutlineGroup](https://developer.apple.com/documentation/swiftui/outlinegroup)
- [ForEach](https://developer.apple.com/documentation/swiftui/foreach)
- [Creating performant scrollable stacks](https://developer.apple.com/documentation/swiftui/creating-performant-scrollable-stacks)
- [Scroll views](https://developer.apple.com/documentation/swiftui/scroll-views)
- [ScrollView](https://developer.apple.com/documentation/swiftui/scrollview)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [ScrollGeometry](https://developer.apple.com/documentation/swiftui/scrollgeometry)
- [onScrollGeometryChange(for:of:action:)](https://developer.apple.com/documentation/swiftui/view/onscrollgeometrychange%28for%3Aof%3Aaction%3A%29/)
- [onScrollVisibilityChange(threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrollvisibilitychange%28threshold%3A_%3A%29)
- [onScrollTargetVisibilityChange(idType:threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrolltargetvisibilitychange%28idtype%3Athreshold%3A_%3A%29)
- [onScrollPhaseChange(_:)](https://developer.apple.com/documentation/swiftui/view/onscrollphasechange%28_%3A%29)
- [ScrollPhase](https://developer.apple.com/documentation/swiftui/scrollphase)
- [scrollTargetLayout(isEnabled:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetlayout%28isenabled%3A%29)
- [scrollTargetBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetbehavior%28_%3A%29)
- [PagingScrollTargetBehavior](https://developer.apple.com/documentation/swiftui/pagingscrolltargetbehavior)
- [ViewAlignedScrollTargetBehavior](https://developer.apple.com/documentation/swiftui/viewalignedscrolltargetbehavior)
- [refreshable(action:)](https://developer.apple.com/documentation/swiftui/view/refreshable%28action%3A%29)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [Layout](https://developer.apple.com/documentation/swiftui/layout)
- [ProposedViewSize](https://developer.apple.com/documentation/swiftui/proposedviewsize)
- [containerRelativeFrame(_:alignment:_:)](https://developer.apple.com/documentation/swiftui/view/containerrelativeframe%28_%3Aalignment%3A_%3A%29)
- [safeAreaInset(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [safeAreaPadding(_:)](https://developer.apple.com/documentation/swiftui/view/safeareapadding%28_%3A%29)
- [contentMargins(_:_:for:)](https://developer.apple.com/documentation/swiftui/view/contentmargins%28_%3A_%3Afor%3A%29-1lt8b)
- [SafeAreaRegions](https://developer.apple.com/documentation/swiftui/safearearegions)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Collections](https://developer.apple.com/design/human-interface-guidelines/collections)
- [Lists and tables](https://developer.apple.com/design/human-interface-guidelines/lists-and-tables)
- [Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Swift concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
- [Improving your app’s performance](https://developer.apple.com/documentation/xcode/improving-your-app-s-performance/)
