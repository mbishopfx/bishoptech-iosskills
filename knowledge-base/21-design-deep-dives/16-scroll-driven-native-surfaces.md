# Scroll-driven native surfaces

## Design thesis

Scrolling is not empty motion between cards. It is the way a person explores hierarchy, maintains a place, discovers more content, and decides when to act. A polished Apple-native screen makes the scroll relationship visible without turning every offset into an animation demo.

Use this loop:

    content hierarchy
    -> readable container
    -> stable item identity
    -> intentional scroll policy
    -> bounded edge/control treatment
    -> accessibility and input parity

## Choose the content grammar first

| Content | Native starting point | Scroll behavior |
| --- | --- | --- |
| Settings or scan-heavy rows | List/Form | System row behavior and section hierarchy |
| Editorial/detail content | ScrollView with lazy stack or regular composed sections | Natural reading, optional section jumps |
| Cards or pages | Lazy stack with scroll targets | View-aligned or paging when units are meaningful |
| Chat or streamed output | ScrollView with stable message/section IDs | Follow-bottom only while the person chooses to follow |
| Editable document | TextEditor or document route | Preserve focus, selection, and revision |
| Media feed | Lazy container plus visibility state | Bound playback/prefetch to the viewport |
| Dashboard with controls | ScrollView with measured sections and safe-area action ownership | Keep the primary action reachable without covering content |

Do not choose a scroll effect before deciding whether the content is a list, document, feed, page deck, or editor. The container determines identity, laziness, keyboard behavior, accessibility, and how much automatic motion is appropriate.

## The native reading surface

A good reading surface has:

- a visible title or context anchor;
- sections that remain distinguishable at larger text sizes;
- enough horizontal inset for indicators and pointer/touch movement;
- predictable reading order;
- a clear end state or next action;
- a way to return to the current section after a system or model update.

Use partial content, a section marker, or a page control to hint that more content exists. A hidden indicator is not the only cue.

## Floating controls and scroll edges

When controls float over a scroll view, the person needs to understand both the content boundary and the control boundary. Apple’s HIG recommends scroll edge effects where a scroll view meets floating interface elements and treats those effects as functional transitions rather than decorative overlays.

For a glass action group:

    content scroll view
    -> owned safe-area/toolbar region
    -> glass or system control group

The group should:

- remain compact enough not to hide the last useful line;
- retain labels and enabled/disabled states;
- respect the keyboard and focused editor;
- have an opaque/material fallback;
- use the same primary action when the edge effect is removed;
- avoid implying that new content is approved or ready merely because it is visually above the glass bar.

Use the system shell first. A custom overlay that is not measured into the safe area creates a false sense of polish and causes clipped text, inaccessible controls, or content hidden behind the bar.

## Scroll position is part of context

Treat a scroll position like focus: it can be user-owned, programmatic, stale, or unavailable.

    currentSection: Section.ID?
    userPositioned: Bool
    followMode: followingBottom | browsing
    pendingNewContent: Int
    programmaticReason: search | selection | apply | restore

When a model inserts a summary, a transcript segment, or a source citation:

- preserve the current section if the person is browsing;
- show a small new-content affordance rather than jumping;
- scroll automatically only when it resolves the action they just initiated;
- keep enough context visible around a selected item;
- allow the person to return to the previous position.

Automatic scrolling is helpful when it reveals a search result, insertion point, selection, or newly relevant content. It becomes disorienting when every background update moves the viewport.

## Visibility as resource policy

Visibility can govern expensive work, not human meaning:

    visible -> allow bounded preview/preload
    hidden -> cancel/pause nonessential work
    visible again -> resume from a checkpoint

This is useful for media, local embedding/index work, thumbnails, and contextual on-device suggestions. Keep work cancellable and cache the last safe result. Do not use visibility to:

- mark a document read or agreed;
- fire a purchase, destructive action, or permission;
- treat an AI response as reviewed;
- send a background request without a user-approved product rule.

## Scroll phases and motion

Use phase changes to coordinate motion, not to create a second interaction language:

- during active panning, keep the content stable and avoid expensive effects;
- during deceleration, allow a light settling effect if it preserves context;
- during programmatic animation, show the reason for movement when it might surprise the person;
- at idle, restore the normal toolbar/status presentation.

Provide a Reduce Motion route that keeps the same hierarchy and action reachability. For visionOS Look to Scroll, Apple’s HIG advises removing custom scroll effects and animations that can behave unexpectedly with gaze-based scrolling. The same caution applies to accessibility modes and alternate inputs more broadly.

## Rich AI output patterns

### Review document

    title and source
    -> generated draft
    -> source highlights
    -> apply/edit/discard

Keep the bottom action group stable while the content scrolls. If the draft changes during generation, do not force the viewport to the end unless follow mode is active.

### Streaming transcript

    live status
    -> time/section markers
    -> partial text
    -> final text
    -> correction action

Partial and final text should be visually and semantically distinguishable. A visible item is not automatically final. Keep the scroll position and focused correction field stable while updates arrive.

### Feed or browse surface

    stable item IDs
    -> visible IDs
    -> bounded prefetch
    -> user-selected item
    -> on-device explanation or action

A feed should not start a model request just because a cell entered the viewport unless that behavior is expected, bounded, cancellable, and privacy-reviewed. Prefer a user-started action for expensive generation.

## Native transitions and Liquid Glass

Use scrollTransition for a small amount of visual response to entering/leaving the viewport. Keep opacity, scale, and material changes subtle enough that a person can still scan the content when the effect is disabled.

Do not apply a unique glass capsule to every list item. A small number of functional groups creates hierarchy; a glass coating everywhere flattens hierarchy and raises contrast/performance costs. Use system controls and system-defined materials where they express the action.

## Adaptation matrix

| Condition | Design response |
| --- | --- |
| Compact width | Reduce side-by-side actions; keep current context visible |
| Large Dynamic Type | Let rows and sections grow; avoid fixed-height cards |
| Keyboard | Preserve focused content and keep the commit action reachable |
| Right-to-left | Use leading/trailing semantics and test scroll affordances |
| VoiceOver | Keep focus stable across insertions and programmatic scrolls |
| Reduce Motion | Remove scroll-driven transitions; preserve section and action state |
| Reduce Transparency | Use standard material/opaque controls; retain contrast |
| Pointer/keyboard | Support expected scrolling and focus movement |
| visionOS Look to Scroll | Use broad, clear scroll areas; remove conflicting custom effects |
| Model unavailable | Keep browsing/review usable with deterministic content |

## Visual system details

Use a small visual language for scroll state:

    normal content
    current/selected content
    new content
    stale or partial content
    loading/canceled/error content

Every state needs text, structure, or an accessible value. A fading header is not a status message. A blurred edge is not a loading state. A bottom pill is not a confirmation.

## Proof and handoff

Capture design evidence for:

- initial position, restored position, and content-size changes;
- programmatic jumps from search, selection, and apply actions;
- user browsing while new AI content arrives;
- follow-bottom mode and return-to-bottom action;
- visible/hidden resource cancellation;
- page alignment and variable-height content;
- Dynamic Type, right-to-left, keyboard, VoiceOver, Reduce Motion, and Reduce Transparency;
- physical touch/pointer feel, memory, thermal behavior, and actual glass/edge rendering where used.

## Sources

- [Human Interface Guidelines: Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views)
- [Human Interface Guidelines: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Human Interface Guidelines: Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Scroll views](https://developer.apple.com/documentation/swiftui/scroll-views)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [ScrollGeometry](https://developer.apple.com/documentation/swiftui/scrollgeometry)
- [ScrollPhase](https://developer.apple.com/documentation/swiftui/scrollphase)
- [ScrollTargetBehavior](https://developer.apple.com/documentation/swiftui/scrolltargetbehavior)
- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left)
