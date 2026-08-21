# Collections, scrolling, and adaptive-layout design

## Design thesis

A polished Apple-like collection does not begin with cards, gradients, or
glass. It begins with the way people scan, choose, edit, and return to
content:

    content type
      -> information hierarchy
      -> collection grammar
      -> selection/editing feedback
      -> scroll and pagination cues
      -> adaptive arrangement
      -> functional control layer
      -> accessible and alternate input
      -> AI review boundary

Use the native row, grid, list, table, and scroll behavior that matches the
content. Then use Liquid Glass selectively for controls and navigation that
float above the content. This keeps the screen recognizable as an Apple
platform interface without turning every item into a translucent ornament.

## The collection decision

Ask what the person needs to compare.

| If the person mainly compares... | Prefer... | Design implication |
| --- | --- | --- |
| Text, settings, statuses, or options | List or table | Make labels scannable; use sections and hierarchy |
| Photos, covers, products, or visual tiles | Collection/grid | Give images room; keep titles and actions accessible |
| A sequence of reading cards or generated answers | ScrollView with a lazy stack | Preserve a calm reading column and explicit source/next actions |
| Full-screen stories, onboarding pages, or media | Paged scroll with page state | Make the page boundary visible and support a way back |
| Nested folders or categories | Hierarchical List/OutlineGroup | Use disclosure and indentation to explain structure |
| A small static comparison panel | Grid | Align columns deliberately; avoid lazy complexity |

Apple’s Human Interface Guidelines recommend standard row or grid layouts
when possible, list/table treatment for text, and collections for image-based
content. A custom arrangement needs a reason the standard grammar cannot
express, not merely a desire to appear unique.

## Visual hierarchy for a native collection

Keep three layers legible:

    content layer
      item identity, title, value, image, status, supporting text

    interaction layer
      selection, edit handles, swipe/context actions, inline controls

    functional edge layer
      navigation, toolbar, tab bar, search, accessory, scroll-edge effect

The content layer should carry the meaning. The interaction layer should
explain what is selected or editable. The functional edge layer should remain
available while content moves beneath it.

### A row anatomy

Use a predictable row rhythm:

    leading identity/icon/image
      -> primary title
      -> secondary value or status
      -> trailing disclosure/action/state

Do not make a row’s meaning depend on color, a tiny icon, or a glass tint.
Keep the title and value useful at large text sizes. A disclosure indicator
means “there is a next level”; an info action means “show more information.”
Do not substitute one for the other.

### A grid anatomy

Use a grid when the image or visual object is the primary scan target:

    image or visual preview
      -> short title or category
      -> concise state
      -> one clear activation route

Provide enough spacing around items for selection, focus, pointer hover, and
VoiceOver exploration. Avoid putting unrelated row actions into every card.
Use a detail screen, context menu, or a small action menu for secondary work.

### An AI result-card anatomy

Generated output needs stronger provenance than ordinary content:

    source label/revision
      -> generated candidate
      -> confidence/limitation language appropriate to the feature
      -> Review, Edit, Accept, Reject, Retry

Do not label a candidate “saved” until the domain commit succeeds. Do not
use a sparkle icon as the only explanation of what the feature does.

## Selection and editing design

Selection should answer “what is currently chosen?” Editing should answer
“what can I change?” Focus should answer “where will the next input go?”

| State | Visual language | Alternate-input requirement |
| --- | --- | --- |
| Unselected | Normal hierarchy | Row/card is still identifiable and actionable |
| Selected | Persistent highlight, checkmark, or selected value | State is exposed to VoiceOver and keyboard |
| Focused | Focus ring or platform focus treatment | Pointer and keyboard can move without changing domain state |
| Editing | Reorder/delete affordance or editable fields | Completion/cancel route is clear |
| Disabled | Reduced emphasis but readable explanation | Action has no false callback; recovery is available |
| Stale | Conflict/status treatment | Person can refresh, compare, or retry |

For multiple selection, show count and the available next action. When a list
is editable, preserve the selected IDs across reorder when the item still
exists. If an item disappears, explain or clear the selection intentionally.

Swipe actions and context menus are useful secondary routes, but a core task
must remain visible or available through a system command. The same action
should behave the same from a row, toolbar, menu, keyboard shortcut,
VoiceOver action, and App Intent when those routes are supported.

## Scroll design

### Make scrolling discoverable

Scroll indicators are transient, so provide other cues when content extends
beyond the viewport:

- partial content at an edge;
- a clear continuation pattern;
- a visible section or page title;
- a “new items” or “jump to latest” action;
- a page control for true pages;
- a stable bottom action that remains reachable.

Support the system’s default scrolling gestures and keyboard shortcuts. Avoid
same-axis nested scroll views because the gesture and viewport owner become
ambiguous. A horizontal carousel inside a vertical feed can work when its
height, target behavior, and accessibility boundary are explicit.

### Continuous versus page-by-page

Use continuous scrolling for reading, settings, search results, and feeds.
Use paging for full-screen media, stories, or content where one interaction
should move to a deliberate chunk. If paging is used, show page state when it
helps orientation and do not duplicate the same-axis scroll indicator.

For card carousels, view-aligned settling can make the next card discoverable.
Keep enough of the next item visible to communicate continuation, but never
let the peek obscure the title, selected state, or action.

### New content and the reading position

Streaming and live content must respect the person’s reading position:

    following latest
      -> append and keep the latest item visible

    browsing earlier content
      -> append without moving the viewport
      -> show new-content affordance
      -> return to latest only on explicit action

Never auto-scroll merely because the array changed. Preserve context across
rotation, filtering, refresh, and navigation when the anchor item remains
valid.

## Pagination and loading states

Design loading as part of the collection, not as a spinner over the whole
screen:

| State | Surface |
| --- | --- |
| Initial load | Skeleton or bounded progress with task context |
| Refresh | Native refresh gesture and concise status |
| Loading next page | Inline footer/progress near the continuation edge |
| Empty | Explain why the collection is empty and give a next action |
| No results | Show query/scope and an easy clear/refine route |
| Offline | Preserve existing content and state what is unavailable |
| Failed page | Inline retry tied to the cursor/filter |
| End reached | Quiet terminal state; do not imply another page |
| Stale | Explain that content changed and offer review/refresh |

Avoid the pattern where every last visible card displays an independent
spinner. One feature-level page state prevents duplicate requests and gives
the person a coherent recovery route.

Pagination should not change the meaning of already visible rows. Maintain
stable identity, deduplicate repeated pages, and keep the user’s current
filter/sort scope visible. A page-loading affordance must not silently change
selection or move the viewport.

## Adaptive layout

### Adapt the arrangement, not the meaning

When width, height, Dynamic Type, keyboard, or split view changes, preserve
the hierarchy and adapt the container:

    wide/regular
      -> grid or two-column summary

    narrow/compact
      -> list or one-column cards

    very large text
      -> wrapped rows and vertical action groups

The action label, selected state, error, recovery, and source attribution
must survive every branch.

Use ViewThatFits for a small ordered set of complete alternatives. Use
AnyLayout when the same subviews should change arrangement without losing
identity or local state. Use container-relative sizing when a card or page
should be related to its nearest scroll, tab, navigation, or window
container. Use a custom Layout only when a standard stack/grid/list cannot
express the real relationship.

Do not make a “phone layout” and “iPad layout” that diverge in behavior
without an explicit product reason. A split view, a resizable window, or
landscape orientation can expose widths that do not match a device category.

### Responsive grid rules

For image collections:

- choose a minimum readable tile size;
- use the available container, not a fixed device width;
- keep spacing consistent across column changes;
- avoid changing columns during an active gesture if possible;
- preserve the visible item and selected item when columns change;
- test short, long, localized, and generated titles;
- verify focus and accessibility order after rearrangement.

For text collections, switching from a list to a dense grid often makes
scanning worse. Prefer a list with more horizontal breathing room or a
two-column detail layout when the text is the reason the collection exists.

## Safe areas and functional edges

Content should extend to the display where appropriate, while controls and
reading content remain clear of system regions. Decide which elements belong
to the edge layer:

| Element | Typical treatment |
| --- | --- |
| Background artwork | Extend behind safe areas if it remains noninteractive |
| Scroll content | Account for safe-area, tab, toolbar, and keyboard insets |
| Bottom action bar | Use a safe-area-aware inset and keep content visible above it |
| Tab bar or toolbar | Let the system surface own its placement and material |
| Search/filter rail | Keep its relationship to the collection explicit |
| New-content control | Place near the viewport edge without covering focusable rows |

Use content margins to control scroll content separately from indicators when
the collection needs a clipped or rounded visual boundary. Use safeAreaInset
for a functional bar that should reduce the usable content region. Treat
ignoresSafeArea as a deliberate background/composition decision, not a
shortcut around an overlap bug.

## Liquid Glass composition

Liquid Glass should clarify the control layer:

    content that people read or browse
      underneath
    controls, navigation, and transient functional groups

Use standard SwiftUI components first. If a custom group needs Liquid Glass,
keep it compact, semantic, and important. GlassEffectContainer is useful when
multiple custom effects need to blend or morph as a group. Do not apply glass
to every collection cell; that makes the content layer noisy and can harm
performance and legibility.

For a scroll view next to floating controls, a scroll-edge effect is a
transition between content and the control layer, not a decorative gradient.
Use one coherent edge per pane. The default soft treatment is a good starting
point for iOS/iPadOS; a stronger boundary needs a content-legibility reason.

Test:

- regular versus clear variant;
- rich and flat backgrounds;
- light/dark appearance;
- increased contrast;
- reduced transparency;
- large Dynamic Type;
- Reduce Motion;
- long text behind the edge;
- keyboard and bottom accessory overlap.

When effects are reduced, the action must still be recognizable from shape,
label, state, and layout. The fallback is part of the design, not a degraded
afterthought.

## Accessibility and alternate input

Collection design must survive the removal of visual shortcuts:

- include labels and values for image tiles;
- keep row/card activation distinct from secondary actions;
- expose selected, expanded, loading, stale, and disabled state;
- preserve a logical reading order after grid reflow;
- avoid moving VoiceOver focus on every insertion or streamed partial update;
- make selection count and editing completion discoverable;
- keep the primary action reachable with Full Keyboard Access;
- support pointer hover/focus without requiring a pointer;
- use leading/trailing semantics for right-to-left languages;
- let Dynamic Type grow the row/card instead of clipping it;
- ensure reduced motion does not remove an essential state cue;
- ensure reduced transparency does not erase boundaries or status.

Do not use a custom gesture as the only way to select, reorder, reveal, or
advance. If the interaction is important, expose a semantic control or
system-supported action.

## AI result-feed design

An on-device model can help summarize, classify, extract, rewrite, or
generate structured suggestions. The collection should present the model as
an assistant to a human-owned task:

    visible source
      -> explicit request
      -> generating state with cancel
      -> candidate feed
      -> review/edit
      -> deterministic validation
      -> commit or discard

Design each candidate with a stable label and clear source relationship.
Partial streamed output can appear in a bounded preview row, but the UI must
not present partial text as a committed record. If the source changes, mark
the candidate stale and require a refresh or review.

Prefer generated structure for collection rows when the feature needs
reliable fields, but keep the schema small and meaningful. The model’s
language, tool, and capability failures need ordinary empty/error/manual
designs. “AI unavailable” should not strand the person in an empty feed.

## A practical visual review checklist

### Content

- Can a person identify the collection’s organizing principle immediately?
- Is the primary item information visually dominant?
- Are sections, titles, and metadata in a predictable reading order?
- Does the empty state explain what to do next?

### Interaction

- Is selection visible without color alone?
- Is editing mode explicit and reversible?
- Are destructive actions marked and recoverable?
- Is the primary action visible outside a hidden context menu?

### Scrolling

- Is continuation obvious when indicators are hidden?
- Does new content respect the current reading position?
- Does paging have page state and a clear return route?
- Are same-axis nested scroll views avoided?

### Adaptation

- Does the content survive compact width and large text?
- Does the selected/visible item remain stable after reflow?
- Do localized and right-to-left strings preserve hierarchy?
- Does the keyboard leave the primary action and error reachable?

### Materials

- Is Liquid Glass reserved for functional controls/navigation?
- Does the edge effect clarify rather than cover?
- Does reduced transparency preserve meaning?
- Is the content layer still the visual focus?

### AI

- Is the request explicit and cancellable?
- Can the person see source and candidate?
- Is a candidate distinct from saved content?
- Is there a manual path when the model is unavailable?

## Related pages

- [Adaptive layout and platform design](02-adaptive-layout-and-platform-design.md)
- [Responsive Liquid Glass layouts](14-responsive-liquid-glass-layouts.md)
- [Scroll-driven native surfaces](16-scroll-driven-native-surfaces.md)
- [Responsive Liquid Glass layouts](14-responsive-liquid-glass-layouts.md)
- [SwiftUI collections, scroll, and adaptive layout](../42-framework-deep-dives/82-swiftui-collections-scroll-and-adaptive-layout.md)
- [SwiftUI collections, scroll, and layout route](../50-capability-recipes/113-swiftui-collections-scroll-and-layout-route.md)

## Sources

- [Collections](https://developer.apple.com/design/human-interface-guidelines/collections)
- [Lists and tables](https://developer.apple.com/design/human-interface-guidelines/lists-and-tables)
- [Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left)
- [List](https://developer.apple.com/documentation/swiftui/list)
- [Lists](https://developer.apple.com/documentation/swiftui/lists)
- [LazyVStack](https://developer.apple.com/documentation/swiftui/lazyvstack)
- [LazyVGrid](https://developer.apple.com/documentation/swiftui/lazyvgrid)
- [Grid](https://developer.apple.com/documentation/swiftui/grid)
- [Table](https://developer.apple.com/documentation/swiftui/table)
- [OutlineGroup](https://developer.apple.com/documentation/swiftui/outlinegroup)
- [ScrollView](https://developer.apple.com/documentation/swiftui/scrollview)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [ScrollGeometry](https://developer.apple.com/documentation/swiftui/scrollgeometry)
- [scrollTargetBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetbehavior%28_%3A%29)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [containerRelativeFrame(_:alignment:_:)](https://developer.apple.com/documentation/swiftui/view/containerrelativeframe%28_%3Aalignment%3A_%3A%29)
- [safeAreaInset(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [safeAreaPadding(_:)](https://developer.apple.com/documentation/swiftui/view/safeareapadding%28_%3A%29)
- [contentMargins(_:_:for:)](https://developer.apple.com/documentation/swiftui/view/contentmargins%28_%3A_%3Afor%3A%29-1lt8b)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
