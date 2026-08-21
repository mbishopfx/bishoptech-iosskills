# Semantic search and onscreen context: native Apple-surface design contract

## Design intent

An app that participates in Spotlight, Siri, Apple Intelligence, and onscreen
context should feel like one coherent native product. The system may discover
an entity, but the app owns the moment where the person understands, filters,
opens, edits, or recovers that entity.

The design route is:

    system discovery
      -> concise entity representation
      -> app-owned search/detail destination
      -> current record and permission check
      -> accessible action or recovery

The visual goal is not to reproduce a private Apple surface. The goal is to use
public SwiftUI, App Intents, navigation, accessibility, and Liquid Glass
contracts so the handoff feels at home on current Apple platforms.

This page covers:

- semantic entity indexing and result representations;
- in-app search continuation from Siri/system search;
- visible entity annotations in SwiftUI, UIKit, and custom drawing;
- stable cross-device identity;
- Liquid Glass hierarchy and fallback behavior;
- accessibility, privacy, loading, and recovery states.

## The system boundary should be visible in the design

There are three surfaces with different owners:

| Surface | Owner | Design responsibility |
| --- | --- | --- |
| Spotlight/Siri/system result | System | Provide truthful metadata and a reliable open/search handoff |
| App search/detail | App | Show current data, filters, permissions, actions, and navigation |
| Onscreen context annotation | App plus system | Mark the visible entity without obscuring or exporting the screen |

Do not make the app-owned result screen look as if it were a system result
screen. Use the app's own brand, title, navigation, and data language after the
handoff. A small “Opened from Siri” or “Search from Spotlight” context cue can
be useful, but it should not compete with the content.

## Semantic result representation

A system-facing AppEntity needs to be understandable at a glance and resilient
when the system renders it in a compact container.

### Display hierarchy

Use a three-level hierarchy:

1. type: what kind of thing is this?
2. title: which thing is it?
3. context: why is it relevant?

Examples:

| Type | Title | Context |
| --- | --- | --- |
| Saved place | Lakeview Studio | Chicago · Workplaces |
| Document | Q3 launch brief | Projects · Updated yesterday |
| Recipe | Lemon rice | Dinner · 30 minutes |
| Collection | Weekend reads | 18 items · Personal |

Do not put internal IDs, confidence numbers, database states, or raw AI
explanations in a display representation. If a match is uncertain, say so in
the app-owned detail view with a user-understandable explanation.

### Localization and length

Treat all display strings as localized interface copy:

- keep the type name short;
- let the title carry the identity;
- use a subtitle that remains useful if truncated;
- avoid punctuation-heavy field dumps;
- test pluralization, right-to-left layouts, and long names;
- do not assume English label order;
- use a text alternative when an image is missing.

A semantic index is not a marketing channel. The searchable projection should
help a person find their own content, not repeat promotional keywords.

### Image treatment

A system result image is a cue, not the record of truth.

- use a safe thumbnail with a predictable aspect ratio;
- avoid an image that reveals sensitive content in a notification-like surface;
- provide a text representation that works without the image;
- do not use an image to imply visual certainty;
- replace or remove the index entry when the underlying image is withdrawn;
- make sure the app-owned detail view can load a current image or show a
  placeholder.

## The in-app search handoff

When Siri or a system search surface invokes system.searchInApp, the app should
open a real search experience with the same query string. The handoff should
preserve user intent while giving the app room to add its own search tools.

### Entry state

At launch or foreground handoff, show:

- the query in the native search field;
- the selected search scope;
- a clear navigation title;
- a loading state that does not pretend results are final;
- an accessible status announcement when results arrive;
- a back path that returns to the previous app context when possible.

If the system provides no usable criteria, open the app's ordinary search screen
with the scope chooser visible. Do not silently run an empty search that looks
like a failed handoff.

### Search result shell

A native result shell should have:

- one primary search field;
- optional scope/filter controls;
- predictable result rows;
- a short result count or status;
- an empty state that explains what to try next;
- a clear offline or authorization state;
- detail navigation that re-resolves the entity;
- a visible way to clear or revise the query.

Keep filters in a toolbar, menu, or sheet that works with Dynamic Type and
VoiceOver. A Liquid Glass toolbar can group search scope and filter controls,
but the results themselves still need ordinary content hierarchy.

### Loading, empty, and stale states

The handoff is not complete when a screen appears. Design the states:

| State | User-facing treatment | Data rule |
| --- | --- | --- |
| Loading | Native progress indicator and query context | Do not show stale private rows as current |
| Results | Rows/cards with type, title, context, and action | Resolve current authorized records |
| No results | Explain the scope and suggest a broader query | Do not manufacture approximate records |
| Offline | Say whether local results are available | Never imply a server result succeeded |
| Signed out | Offer sign-in/account selection | Do not retain the previous account's rows |
| Stale index | Refresh or search current store | Index rank is only a candidate source |
| Deleted record | Unavailable state with search-back path | Do not open a different record |
| Permission filtered | Explain that some content is unavailable if safe | Avoid revealing the existence of private rows |

If the product uses optimistic cached results, label them as cached and replace
them after current authorization completes. A stale card should never become a
hidden data leak through a detail route.

## Liquid Glass composition for semantic search

Apple's Liquid Glass guidance favors a layered system treatment, restrained
custom glass, and a clear relationship between controls and content. Apply that
to search and context surfaces:

### Use system materials first

Prefer standard SwiftUI controls, navigation containers, toolbars, sheets,
menus, buttons, lists, and search fields. They receive the platform's current
treatment and accessibility behavior.

The app's custom layer should answer a real hierarchy question:

- where does the search/filter toolbar sit above the content?
- which controls float above a map, canvas, or media surface?
- which action is primary and which actions belong in an overflow menu?
- how does a selection or currently focused entity remain visible?

Do not add a glass rectangle behind every row. A result list should read as
content first, with glass reserved for control layers or an intentional
floating group.

### Search bar and toolbar

A good native search shell:

- places the search field in the platform search/navigation position;
- keeps scope and filter actions adjacent but secondary;
- uses a toolbar group for transient controls;
- lets the system collapse or adapt controls on small screens;
- respects compact height and Dynamic Type;
- preserves clear focus and keyboard dismissal behavior.

Do not put a custom decorative search bar over the native one. Avoid a blurred
full-screen overlay that reduces contrast behind result content.

### Result rows

Rows need stable geometry and reading order:

- type or category as secondary context;
- title as the strongest text;
- subtitle as supporting context;
- trailing action only when it is genuinely useful;
- enough padding for touch and pointer targets;
- selected state that is visible without color alone;
- image with an accessible label or decorative treatment as appropriate.

If a row is annotated with an AppEntity identifier, its visible content and
accessibility label should describe the same record. A visually empty row with
an entity annotation is not useful system context.

### Floating search controls over custom content

Maps, diagrams, cameras, and media editors may need controls over content.
Use a GlassEffectContainer or a small glass group only where the controls
float over changing content. Keep the group spatially coherent, use the
platform's interactive glass behavior for controls, and test the group when
controls appear/disappear.

Avoid:

- glass applied to the entire canvas;
- small text inside low-contrast translucent pills;
- multiple competing floating islands;
- custom blobs that imitate a system control without its semantics;
- controls that disappear when Reduce Transparency or high contrast is on.

The source of truth remains the entity model and current query, not the visual
effect.

## Onscreen context design

### One ordinary view, one honest entity

For a card, row, or detail header, associate the smallest view that represents
the entity. The modifier should not cover a surrounding navigation stack,
background, or unrelated action bar.

The visible text should answer:

- what entity is present?
- what is its current state?
- what will happen if it is opened?
- is it available to the current account?

For an entity that is loading, a placeholder, or deleted, remove the annotation
until a real current ID is available.

### Lists and selection

A list is a moving semantic surface:

- rows can be inserted, removed, filtered, or reused;
- selection can change without the row moving;
- a collapsed group may hide entities;
- a search result can be stale while the source store updates.

Use IDs from the domain store, never list indexes. Verify annotations after:

- sort changes;
- filter changes;
- pagination;
- refresh;
- account switching;
- row expansion;
- multi-selection;
- drag and drop;
- restoration from state restoration.

For a selectable List, the selection type should describe the entity type the
user is actually choosing. A row that contains two different entities should
use a deliberate subelement or a clear primary entity rather than an
ambiguous annotation.

### Custom canvas, maps, and diagrams

Custom rendered entities need a visual and semantic hit target. An
AppEntityUIElement can carry bounds, state, and subelements, but the design
must still work if the system does not surface the context.

Use:

- a visible selection ring or focus state;
- a minimum target size for touch and accessibility;
- a text alternative in an adjacent list or inspector;
- stable z-order and subelement identity;
- updates on zoom, pan, rotation, and data reload;
- an empty/hidden state when the entity is offscreen.

Do not expose every decoration as an entity. Annotate meaningful objects,
regions, or selections that a person could name and act on.

### Context should not surprise the user

Explain system-facing context in privacy settings or product documentation
when it is material to the app. If the product has a user-facing switch for
system discovery, make it easy to change. Do not use a hidden annotation to
expand the app's data collection or to send the entire view elsewhere.

## Cross-device identity in the experience

A cross-device continuation can fail even when the identifier is stable.

Design the handoff for these states:

| State | Destination |
| --- | --- |
| Same account, local data ready | Current detail |
| Same account, local data syncing | Loading with retry or current partial data |
| Stable ID known, record deleted | Unavailable with app search |
| Different account | Account selection/sign-in |
| Sharing revoked | Privacy-safe unavailable state |
| Local-only entity | Stay on current device or show a local-only explanation |
| Network required | Clear offline state and retry |

Do not show a record's name in a cross-device error if the second device is
not authorized to know it. The stable ID is a routing key, not a bearer token.

When an entity is opened from a system surface, avoid surprising mutations.
Opening should navigate or display. Editing, sending, deleting, purchasing, or
sharing should remain explicit and confirmable.

## Accessibility contract

The semantic route is also an accessibility route.

### VoiceOver and spoken context

- Make the row/card label identify the same AppEntity as the annotation.
- Include type and essential state in the accessibility label/value.
- Announce result changes without reading every private field.
- Preserve focus when a search handoff opens.
- Ensure custom canvas elements have accessible names and actions.
- Expose an alternate list or inspector for visual-only content.
- Test with VoiceOver, Switch Control, and keyboard navigation where supported.

### Dynamic Type and layout

- use text styles;
- allow titles and subtitles to wrap;
- avoid fixed-height glass controls;
- test large accessibility sizes;
- keep result actions reachable when rows grow;
- check landscape, split view, and external display cases where supported.

### Motion, contrast, and transparency

- respect Reduce Motion in handoff animations and entity highlights;
- respect Reduce Transparency/high contrast in glass overlays;
- do not rely on blur, translucency, or color alone for state;
- test light, dark, increased contrast, and grayscale conditions;
- keep a clear non-glass hierarchy.

### Privacy and accessibility together

A spoken result can reveal data in a public environment. Minimize sensitive
subtitles and support the system's privacy expectations. A visually hidden
private field may still be read by VoiceOver if it is in the accessible tree.
Review both the index projection and the accessibility representation.

## App navigation and state restoration

The system handoff should land in a stable navigation state:

- define an explicit route for a search query and optional scope;
- define an explicit route for a resolved entity ID;
- restore the query without restoring stale private results;
- use the current model/store to rebuild the detail destination;
- support a back path and dismiss path;
- handle cold launch, warm launch, and an already-present detail screen;
- avoid pushing duplicate destinations when the same handoff arrives twice.

App Intents can be invoked while the app is already running or while it is
cold. The route should be idempotent: applying the same search or open request
twice should not duplicate navigation or create duplicate side effects.

## Design review checklist

- [ ] The system result is concise and does not impersonate an Apple-owned UI.
- [ ] The app-owned search screen shows the received query and scope.
- [ ] A person can revise, clear, or broaden the search.
- [ ] Empty, offline, signed-out, stale, and deleted states are designed.
- [ ] Standard SwiftUI search/navigation/toolbar controls are preferred.
- [ ] Custom Liquid Glass is limited to a clear control-surface need.
- [ ] The result rows remain readable without translucency or color.
- [ ] Every visible entity annotation uses a current stable domain ID.
- [ ] List and collection updates cannot leave a reused cell with a stale ID.
- [ ] Canvas/maps have accessible, visible, bounded entity elements.
- [ ] Stable cross-device IDs have account and authorization recovery.
- [ ] VoiceOver, Dynamic Type, Reduce Motion, and contrast are verified.
- [ ] Search and OpenIntent routes are safe on cold and warm launch.
- [ ] No annotation, index, or system handoff retains more data than needed.

## Sources

- https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views
- https://developer.apple.com/documentation/swiftui/glasseffectcontainer
- https://developer.apple.com/documentation/swiftui/glass
- https://developer.apple.com/documentation/swiftui/navigation
- https://developer.apple.com/documentation/swiftui/view-input-and-events
- https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight
- https://developer.apple.com/documentation/appintents/showinappsearchresultsintent
- https://developer.apple.com/documentation/appintents/appschema/systemintent/searchinapp
- https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri
- https://developer.apple.com/documentation/appintents/appentityuielement
- https://developer.apple.com/documentation/appintents/syncableentity
- https://developer.apple.com/documentation/appintents/syncableentityidentifier
- https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences
- https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28_%3A%29
- https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28forselectiontype%3Aidentifier%3A%29
- https://developer.apple.com/documentation/swiftui/view/appentityuielements%28_%3A%29
- https://developer.apple.com/design/human-interface-guidelines/
