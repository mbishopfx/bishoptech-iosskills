# SwiftUI collections, scroll, and adaptive-layout proof matrix

## Evidence boundary

A collection that renders in a preview is not proven to have stable identity,
correct pagination, native scrolling, accessible selection, safe-area
behavior, or acceptable performance. A layout screenshot is not physical
device proof. A model-generated row is not a saved domain record.

Use this matrix to separate source, compile, deterministic behavior, UI,
accessibility, device, performance, AI, system, and release claims.

## Evidence levels

| Level | Evidence | Can prove |
| --- | --- | --- |
| P0 | Official source and target declaration | API meaning, documented contract, source grounding |
| P1 | Named target compile | Imports, signatures, availability, type checking |
| P2 | Preview/static fixture | Composition, labels, deterministic empty/loading/error branches |
| P3 | Unit/state test | Identity, pagination, cancellation, deduplication, state transitions |
| P4 | UI test/accessibility-tree inspection | Selection, navigation, viewport intent, labels, actions, error recovery |
| P5 | Simulator or controlled desktop input | Repeatable layout and input exploration under configured settings |
| P6 | Signed physical-device run | Touch, pointer/keyboard, VoiceOver, scrolling feel, material and system behavior |
| P7 | Performance/thermal trace | Named workload’s hitch, memory, energy, or model cost observation |
| P8 | Archive/TestFlight/system run | Packaged target, entitlement/configuration, release-like behavior |

Do not promote a lower level into a higher claim. P2 can show a glass card;
it cannot prove that Liquid Glass remains legible on a physical device with
reduced transparency. P3 can show a cursor merge is deterministic; it cannot
prove a backend returns the intended production data.

## Collection selection and identity matrix

| Claim | Fixture | Assertion | Minimum evidence | Does not prove |
| --- | --- | --- | --- | --- |
| Container matches content | Text list, image grid, hierarchy, table fixtures | Chosen container preserves scanning and interaction purpose | P0/P1/P2/P4 | It is the best choice for every device |
| Stable IDs survive insert | Insert before selected/visible item | Existing item keeps identity, local state, and semantic target | P3/P4 | Backend identity quality |
| Stable IDs survive reorder | Move items while selected/focused | Selection/focus/target follows the item or documented policy | P3/P4 | Drag feel on hardware |
| Delete is explicit | Delete selected and unselected items | Domain command, selection cleanup, undo/confirmation policy are correct | P3/P4 | Production deletion authorization |
| Filter policy is intentional | Filter hides current selection/anchor | Selection and viewport policy matches documented behavior | P3/P4 | Search ranking quality |
| Pagination deduplicates | Overlapping pages and repeated cursors | One row per ID, deterministic order, no duplicate commit | P3 | Production API correctness |
| Partial AI row is stable | Stream multiple partial updates | Same candidate ID updates in place; no token rows or false save | P3/P4 | Model quality |
| Empty state is truthful | Empty initial, no-results, end-of-feed | Next action and reason are distinguishable | P2/P4 | User comprehension for every locale |

### Identity fixture

Use at least:

- zero, one, many, and duplicate-attempt records;
- insertion before and after the current item;
- deletion of the current item;
- reorder with a selected item;
- filter and sort changes;
- refresh returning updated values;
- overlapping page boundaries;
- partial/complete AI candidate updates;
- long titles and localized identifiers.

Record the ItemID, selected IDs, current target ID, current query/scope,
request generation, and resulting domain revision in test output.

## Selection, editing, and action matrix

| Claim | Fixture | Assertion | Minimum evidence | Failure to record |
| --- | --- | --- | --- | --- |
| Single selection is clear | List with one selected row | Selected state is visible and semantic | P2/P4/P6 | Selection only changes tint |
| Multiple selection is usable | Set of IDs/edit-mode fixture | Count, selected values, apply/cancel, and removal are clear | P4/P6 | Set contains stale IDs |
| Row activation is distinct | Navigate versus select fixture | Tap/click/return follows the documented route | P4/P6 | Activation mutates model unexpectedly |
| Reorder is safe | Move first/middle/last items | Order persists or failure is recoverable | P3/P4/P6 | UI order changes without durable commit |
| Swipe actions are supplemental | Important and secondary actions | Core action has visible/system route; swipe is discoverable extra | P2/P4/P6 | Primary task hidden in swipe |
| Context actions are relevant | Long press/secondary click | Menu contains item-scoped actions and stable labels | P4/P6 | Context menu is the only path |
| Accessibility action matches domain | VoiceOver custom action fixture | Action invokes same command and state result | P4/P6 | Separate gesture owns mutation |
| Keyboard route works | Hardware keyboard/Full Keyboard Access | Selection, open, edit, cancel, delete, and search work as required | P4/P6 | Pointer/touch-only completion |

Inspect the accessibility tree after styles, glass effects, custom containers,
selection modifiers, and row actions are applied. Check for duplicate
elements, missing labels, incorrect selected values, and focus loss after
updates.

## Pagination, refresh, and cancellation matrix

| Claim | Fixture | Assertion | Minimum evidence | Does not prove |
| --- | --- | --- | --- | --- |
| Initial load is bounded | Slow success/failure/cancel | Loading, content, retry, and cancel states are coherent | P3/P4 | Network availability |
| Next page is idempotent | Same cursor triggered twice | One request/one append according to policy | P3 | Server-side deduplication |
| New query cancels old work | Query A then Query B | A cannot overwrite B | P3/P4 | Model/network scheduler behavior |
| Out-of-order responses are safe | Page 2 returns before page 1 | Order is deterministic or response is rejected | P3 | Production latency distribution |
| Refresh resets intentionally | Pull refresh during pagination | Cursor/items/selection/viewport reset or preserve per policy | P3/P4/P6 | Native refresh feel on all OS versions |
| Offline path is honest | Disable network after cached content | Existing content remains usable; retry/manual route is visible | P3/P4/P6 | Every network condition |
| Visibility prefetch is bounded | Fast fling through many targets | Work is throttled/canceled/cached; no request storm | P3/P7 | Unlimited real-world content |
| End state is clear | Empty terminal page | No spinner or false “load more” remains | P2/P4 | Server’s has-more correctness |

Use a fake repository with deterministic cursors and delays. Log:

    query/scope generation
    cursor
    request ID
    cancellation time
    response order
    merged IDs
    final page state

## Viewport and scroll matrix

| Claim | Fixture | Assertion | Minimum evidence | Does not prove |
| --- | --- | --- | --- | --- |
| Default position is correct | Short and long content | Initial edge/anchor matches product policy | P2/P4/P6 | All screen sizes |
| ID jump is correct | Search/deep-link target | Target is revealed and aligned without losing context | P4/P6 | Universal Link delivery |
| Restore is stable | Reorder, rotation, size change | Semantic target remains visible when valid | P3/P4/P6 | State restoration after every interruption |
| User browsing is respected | Append while scrolled away from bottom | Viewport does not move; new-content route appears | P3/P4/P6 | User preference beyond fixture |
| Follow-latest is explicit | Append while at bottom | New content stays visible only in follow mode | P3/P4/P6 | Streaming throughput |
| Geometry projection is bounded | Long continuous scroll | Only intended Bool/enum/ID bucket changes trigger view work | P3/P7 | Smoothness on every device |
| Visibility threshold is correct | Enter/exit at threshold | Event fires according to stable target ID and policy | P3/P4 | Person read/understood item |
| Phase behavior is safe | Drag/deceleration/programmatic scroll | Essential controls stay available through phases | P4/P6 | Haptic quality |
| Paging is correct | Full-screen pages/incomplete final page | Settles to intended boundary and keeps labels/actions visible | P4/P6 | Preference for paging |
| View-aligned carousel is clear | Variable cards/long titles | Cards settle predictably and continuation remains visible | P4/P6 | Physical scrolling comfort |
| Same-axis nesting is controlled | Nested-scroll fixture if unavoidable | Gesture, focus, indicator, and viewport owner is unambiguous | P4/P6 | All assistive input |

Use ScrollPosition view IDs and semantic reasons in logs. Raw content offsets
are diagnostic data, not a substitute for the product’s viewport policy.

## Adaptive layout matrix

| Claim | Fixture | Assertion | Minimum evidence | Does not prove |
| --- | --- | --- | --- | --- |
| ViewThatFits preserves task | Rich/compact alternatives | First fitting branch keeps primary action, state, and recovery | P2/P4/P6 | Choice is optimal |
| AnyLayout preserves identity | HStack/VStack/grid transition | Draft, selection, focus, and row async state survive | P3/P4/P6 | Animation quality |
| Container-relative sizing is bounded | Narrow/wide/rotation/split view | Items fit nearest container and keep readable minimums | P2/P4/P6 | Every window configuration |
| Grid column changes are safe | Column count changes during browsing | Visible/selected item remains understood | P3/P4/P6 | Performance of images |
| Large text reflows | Largest supported Dynamic Type | Labels, values, errors, and actions do not clip | P2/P4/P6 | Localization completeness |
| RTL is correct | Arabic/Hebrew/mixed direction | Leading/trailing, alignment, selection, and gestures remain coherent | P2/P4/P6 | Every script |
| Keyboard is safe | Keyboard-visible sheet/scroll | Focused field and primary action remain reachable | P4/P6 | Every keyboard layout |
| Custom layout is bounded | zero/infinity/unspecified/finite proposals | No invalid size, clipping, or hidden essential action | P3/P4/P7 | General layout quality |

Record proposed size, container size, chosen branch, column count, selected
ID, visible IDs, focus, and accessibility order for each fixture.

## Safe area, margins, and functional edge matrix

| Claim | Fixture | Assertion | Minimum evidence | Failure to record |
| --- | --- | --- | --- | --- |
| Bottom accessory reserves content | Accessory plus long feed | Last row/action is not covered and remains reachable | P2/P4/P6 | Safe-area inset inferred from screenshot |
| Scroll indicators remain usable | Clipped/rounded scroll view | Indicator placement is distinct from content margin | P2/P4/P6 | Indicator hidden by custom clip |
| Keyboard inset is correct | Text field near bottom | Focused field, error, and commit remain reachable | P4/P6 | Content covered after keyboard transition |
| Rotation/split view works | Portrait/landscape and split | Edge controls and collection remain aligned | P4/P6 | One fixed device only |
| RTL edge behavior works | RTL with bottom/leading accessory | Functional controls use semantic edges | P4/P6 | Hard-coded left/right |
| Glass edge is functional | Content beneath toolbar/tab/edge | Transition clarifies boundary without obscuring content | P2/P6 | Edge effect treated as decoration |
| Reduced transparency works | System setting enabled | Fallback preserves hierarchy and selected/error states | P4/P6 | Glass-only state meaning |

## Accessibility and alternate-input matrix

| Claim | Fixture | Assertion | Minimum evidence | Does not prove |
| --- | --- | --- | --- | --- |
| VoiceOver can scan | List/grid/feed with state changes | Labels, values, selection, sections, and actions are understandable | P4/P6 | All rotor behavior |
| VoiceOver focus survives updates | Insert/append/partial AI stream | Focus stays stable or moves with an announced reason | P4/P6 | User preference |
| Voice Control works | Named row/card/action fixture | Visible controls are addressable by meaningful names | P4/P6 | Every language |
| Switch Control works | Core collection task | Person can select, open, edit, confirm, cancel, and recover | P4/P6 | Motor accessibility broadly |
| Full Keyboard Access works | Hardware keyboard | Core task has reachable focus and commands | P4/P6 | External keyboard models |
| Pointer behavior is additive | iPad pointer/trackpad | Hover/focus does not replace selection or obscure content | P5/P6 | Every pointer device |
| Reduced motion works | Paging, transitions, reflow | State change remains clear without required animation | P4/P6 | Perceived comfort |
| Contrast/transparency works | Increase Contrast/Reduce Transparency | Boundaries and status remain legible | P4/P6 | Every display |

## On-device AI collection matrix

| Claim | Fixture | Assertion | Minimum evidence | Does not prove |
| --- | --- | --- | --- | --- |
| Model availability is handled | Available, unavailable, unsupported language | Manual/unavailable route is clear; no false request | P3/P4/P6 | Apple Intelligence eligibility for every device |
| Request is explicit | Tap/command/submit required | No generation starts from passive visibility alone unless documented | P3/P4 | User intent outside fixture |
| Candidate is source-bound | Edit source during generation | Source ID/revision mismatch yields stale/review state | P3/P4 | Model factual accuracy |
| Streaming is bounded | Partial output and cancel | Candidate updates in place, cancel works, focus is not spammed | P3/P4/P6 | Model latency |
| Structured output is safe | Valid/invalid/refused values | Schema/validation rejects invalid domain mutation | P3 | Model quality |
| Tool side effect is authorized | Tool proposal with confirm/reject | App authorization and confirmation own the side effect | P3/P4 | External service correctness |
| Approval commits once | Rapid accept/retry | One domain revision is created or clear failure occurs | P3/P4 | Server persistence without integration test |
| Stale candidate recovers | Source revision changes | Review/refresh/manual route preserves source | P3/P4/P6 | User comprehension |
| AI feed order is honest | Model order versus domain sort | Generated ranking does not silently replace explicit sort or selection | P3/P4 | Ranking usefulness |

Record model availability reason, language/locale, request ID, source ID,
source revision, candidate ID, prompt/schema version, approval action, and
resulting domain revision. Do not put private source text in general logs.

## Performance and rendering matrix

| Claim | Fixture | Assertion | Minimum evidence | Does not prove |
| --- | --- | --- | --- | --- |
| Lazy container helps | Large representative feed/grid | Initial creation and visible work improve for named workload | P7 | All device classes |
| Row work is bounded | Images/model/network work by visibility | Cancellation/cache policy prevents runaway work | P3/P7 | Backend behavior |
| Geometry projection is efficient | Continuous scroll | Narrow state projection avoids broad invalidation | P7 | Battery lifetime |
| Glass use is acceptable | Representative glass controls/content | No named hitch/energy/rendering regression | P6/P7 | Future OS rendering |
| AI feed is responsive | Stream/large result set | Main-thread/UI responsiveness and cancellation are acceptable | P6/P7 | Model quality |
| Long text is stable | Localized/generated long rows | No hitch/clipping from text expansion in named workload | P6/P7 | Every localization |

Use Instruments, SwiftUI performance tools, XCTest performance metrics, or
signposts appropriate to the claim. Record build configuration, device/OS,
dataset size, content mix, and settings.

## Device and release matrix

| Claim | Evidence |
| --- | --- |
| Touch scrolling feels native | Signed physical-device run with representative content |
| Pointer/keyboard routes work | Physical iPad/Mac or intended device family and input |
| VoiceOver completion works | Physical device with VoiceOver and task script |
| Material/edge rendering is correct | Physical device, light/dark, contrast/transparency settings |
| Model runs on device | Intended Apple Intelligence-capable physical device with availability state recorded |
| Performance is acceptable | Physical release-like build and named trace/workload |
| Packaged app includes route | Archive inspection and intended install/TestFlight-like run |
| System delivery is correct | Actual system surface/scene/deep link run where claimed |

Previews and simulator runs are valuable for deterministic exploration, but
they do not close claims about physical scrolling, touch feel, pointer,
keyboard, VoiceOver, thermal behavior, model availability, or release
delivery.

## Test fixture pack

Maintain fixtures for:

- empty, initial-loading, one-item, many-item, and terminal pages;
- insert/delete/reorder/filter/sort/refresh;
- overlapping and out-of-order cursors;
- slow, canceled, failed, offline, and stale loads;
- top/middle/bottom/follow-latest/browsing-earlier viewport modes;
- exact visibility thresholds and fast flings;
- paging, view-aligned, and continuous scroll;
- variable row/card heights;
- compact/regular/split/rotation/keyboard-visible containers;
- Dynamic Type extremes and long localized strings;
- light/dark/increased contrast/reduced transparency/Reduce Motion;
- RTL/mixed direction;
- VoiceOver, Voice Control, Switch Control, Full Keyboard Access, pointer;
- AI unavailable, unsupported language, partial, canceled, stale, refused,
  approved, and committed states;
- performance dataset with realistic images/text/model output.

## Stop conditions

Do not call the collection route complete when:

- a preview is the only evidence for physical or accessibility claims;
- selection is not stable across updates;
- page requests can race and overwrite newer content;
- visibility triggers unbounded work;
- viewport state mutates domain content;
- compact/Dynamic Type branches hide the primary action;
- a glass layer obscures content or is the only state signal;
- AI candidates have no source revision or explicit approval;
- no representative performance/device run exists for a performance claim;
- the archive/release target has not been inspected for release claims.

## Related pages

- [SwiftUI collections, scroll, and adaptive layout](../42-framework-deep-dives/82-swiftui-collections-scroll-and-adaptive-layout.md)
- [Collections, scrolling, and adaptive-layout design](../21-design-deep-dives/110-collections-scroll-and-adaptive-layout-design.md)
- [Scroll geometry and visibility proof matrix](13-scroll-geometry-and-visibility-proof-matrix.md)
- [Custom layout and adaptive Liquid Glass proof matrix](11-custom-layout-and-adaptive-composition-proof-matrix.md)
- [SwiftUI controls, forms, commands, and adaptable-tabs proof matrix](106-swiftui-controls-commands-and-tabs-proof-matrix.md)

## Sources

- [List](https://developer.apple.com/documentation/swiftui/list)
- [Lists](https://developer.apple.com/documentation/swiftui/lists)
- [LazyVStack](https://developer.apple.com/documentation/swiftui/lazyvstack)
- [LazyVGrid](https://developer.apple.com/documentation/swiftui/lazyvgrid)
- [Grid](https://developer.apple.com/documentation/swiftui/grid)
- [Scroll views](https://developer.apple.com/documentation/swiftui/scroll-views)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [ScrollGeometry](https://developer.apple.com/documentation/swiftui/scrollgeometry)
- [onScrollGeometryChange(for:of:action:)](https://developer.apple.com/documentation/swiftui/view/onscrollgeometrychange%28for%3Aof%3Aaction%3A%29/)
- [onScrollVisibilityChange(threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrollvisibilitychange%28threshold%3A_%3A%29)
- [onScrollTargetVisibilityChange(idType:threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrolltargetvisibilitychange%28idtype%3Athreshold%3A_%3A%29)
- [scrollTargetLayout(isEnabled:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetlayout%28isenabled%3A%29)
- [scrollTargetBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetbehavior%28_%3A%29)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [containerRelativeFrame(_:alignment:_:)](https://developer.apple.com/documentation/swiftui/view/containerrelativeframe%28_%3Aalignment%3A_%3A%29)
- [safeAreaInset(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [contentMargins(_:_:for:)](https://developer.apple.com/documentation/swiftui/view/contentmargins%28_%3A_%3Afor%3A%29-1lt8b)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Collections](https://developer.apple.com/design/human-interface-guidelines/collections)
- [Lists and tables](https://developer.apple.com/design/human-interface-guidelines/lists-and-tables)
- [Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Swift concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
