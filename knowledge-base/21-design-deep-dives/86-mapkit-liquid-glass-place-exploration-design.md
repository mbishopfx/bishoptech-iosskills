# MapKit and Liquid Glass Place-Exploration Design

## Design goal

An Apple-native map surface should make place, context, and next action legible without turning the map into a decorative background or a pixel imitation of Apple Maps. MapKit provides the geographic surface and system conventions. The product supplies the task hierarchy, saved-place meaning, review policy, and accessible alternatives.

Use this composition loop:

`task -> map context -> selection/detail -> reviewable action -> confirmed domain state`

Liquid Glass belongs around the action hierarchy. The map, selected place, route, or list remains the content that earns attention.

## Start with the user’s map task

| Task | Primary surface | Supporting surface |
| --- | --- | --- |
| Browse saved places | Map with native markers and a compact list | Place detail, filters, empty/offline state. |
| Find a place | Search field and suggestions | Map region, results list, selected detail. |
| Choose an area | MapReader gesture or visible map selection | Coordinate/place draft, confirmation sheet, manual entry. |
| Explore a destination | Selected place detail with optional Look Around preview | Address, source, accessibility, action buttons. |
| Compare routes | Route summary/list and map overlay | Transport selector, calculation time, recalculate/error. |
| Review an AI itinerary | Structured proposal list with source IDs | Map highlights, deterministic route facts, approve/edit/discard. |

Do not begin with “make the map feel immersive.” Begin with the outcome. If a list or search screen is the better first step, keep the map as context rather than forcing every decision into a gesture.

## Native composition hierarchy

Use a clear z-order:

1. Map content and native map controls.
2. App-owned selection or route projection.
3. A small, grouped Liquid Glass control cluster for actions that belong to the visible map state.
4. A selected-place detail surface for text, provenance, and confirmation.
5. A full-screen or sheet route for editing, review, or consequential handoff.

The glass cluster should answer “what can I do here?” without hiding “what am I looking at?” Examples include search, recenter, map style, filter, Look Around, and route actions. Avoid placing a floating glass button over every marker or making the user hunt through glass controls for the selected place’s name and address.

## Camera state is user state

MapKit’s `MapCameraPosition` can be automatic, region-based, rectangle-based, item-based, user-location-based, or an explicit `MapCamera`. It can also reflect that the person positioned the camera. Treat a user-panned map as a meaningful state change:

- do not continuously recenter after the user explores;
- offer a clear “recenter” action with an honest permission/fallback state;
- fit a route or result set only after a deliberate action or new task;
- use `MapCameraBounds` when the task has a real geographic boundary;
- show a list/detail alternative when pitch or rotation makes spatial orientation difficult.

Camera animation is a transition between meaningful states, not a decorative loop. Under Reduce Motion, the map must still communicate the same selection, route, or recenter result without relying on movement.

## Glass composition rules

| Surface | Glass treatment | Why |
| --- | --- | --- |
| Search/filter controls | Compact grouped glass container with native buttons | Keeps actions discoverable without competing with map labels. |
| Selected place action bar | One primary action plus secondary actions in a stable order | Makes the next task obvious and keeps confirmation separate from decoration. |
| Route summary | Glass only around a concise summary or control row | The route geometry and textual turn/distance summary remain readable. |
| Look Around launch | A clear semantic button adjacent to the selected place | Imagery is optional; the action should not disappear when no scene exists. |
| AI proposal review | Glass around approve/edit/discard controls, not around unsupported claims | Separates generated suggestion from geographic truth and user commitment. |
| Map style/settings | Native menu or sheet with persistent labels | Avoids a glass-only icon vocabulary that fails VoiceOver or localization. |

Use native MapKit controls where they meet the task. Custom glass should have a reason tied to the product’s hierarchy, not a desire to make every element translucent.

## Selected place detail

The selected detail surface should make these values explicit:

- place title and address as returned or normalized by the app;
- source type: saved record, search result, map feature, or user-selected coordinate;
- fetched/resolved time and any stale state;
- actions such as save, edit, share, Look Around, directions, or dismiss;
- what is a proposal versus what has been confirmed;
- a manual route when MapKit data is missing or imagery is unavailable.

If the map feature was selected from Apple map data, do not silently present it as an app-owned record. Offer “use this place,” “save,” or another explicit commitment action.

## Map features and place identity

`MapFeature` can describe a tappable point of interest or physical map feature. Its title, category, image, color, and coordinate help the app explain what was selected, but they do not prove ownership, current operation, safety, or a relationship to the person.

Use an identity ladder:

`map feature -> detail context -> selected place draft -> user confirmation -> saved app record`

This is especially important when on-device AI is involved. A model may group or describe selected places, but it should receive stable source IDs and bounded fields rather than treating a map screenshot as ground truth.

## Search and viewport exploration

Search is an intent, not a passive stream of every map movement. For type-ahead, show suggestions in a focused results surface; for confirmed search, retain the query and region. For viewport points of interest, debounce map movement and allow the person to stop or refine the query.

Design states explicitly:

`idle -> typing -> suggestions -> searching -> results -> selected -> detail`

and:

`map moved -> waiting to query -> viewport results | no results | unavailable`

Never let a late response for an old viewport replace the current results without an indication of what region was searched. Preserve previous useful results while a new query loads if doing so is less confusing than clearing the map.

## Look Around as an optional evidence surface

Look Around can make a selected destination concrete, but coverage is not universal. The empty state must be designed as well as the imagery state:

- `scene available`: show preview and an obvious viewer action;
- `loading`: preserve selected place identity and use a bounded loading state;
- `no imagery`: explain that imagery is unavailable and keep address/map actions;
- `failed/cancelled`: allow retry or continue without imagery.

Keep the selected place title and action context outside the preview. Do not use a Look Around image as a full-screen brand backdrop that hides the destination’s textual identity.

## Route comparison and confirmation

MapKit directions returns calculated route data. Make source, destination, transport type, alternatives, distance, expected time, and calculation time available for review. The person should be able to change a source/destination or transport type without losing the rest of the draft.

Use route geometry as a visual aid, not the only explanation. Provide a text summary and accessible route description. A “start” or “share” action should be a distinct commit step; showing a calculated route must not trigger a system handoff.

## AI proposal shell

An AI-assisted place feature needs a visible source/proposal/commit separation:

| Layer | Native presentation | User action |
| --- | --- | --- |
| Source | Search results, saved places, route fields, selected map feature | Inspect or change source. |
| Proposal | Typed itinerary, label, grouping, or explanation | Edit, accept, reject, regenerate. |
| Validation | Unknown IDs, missing coordinates, stale records, unsupported claims | See why a proposal cannot be applied. |
| Commit | Saved place, trip draft, or chosen route | Confirm the exact side effect. |

Use Liquid Glass for the review controls and status grouping, not to make generated text look like system truth. AI copy should not claim current opening hours, safety, presence, or navigation completion unless the app has a separate verified source and policy for that claim.

## Accessibility and localization

The map is a spatial visualization; it must be paired with semantic content. Provide a list/detail route with accessible place names, categories, addresses, route summaries, and actions. Use stable labels for recenter, map style, filter, selection, Look Around, and route actions.

Verify:

- VoiceOver focus moves to selected detail without losing the map context;
- actions remain reachable without a map drag or precise pin tap;
- Dynamic Type does not truncate the selected place or route summary;
- long place names, right-to-left text, pluralized distances, and localized time units fit;
- increased contrast and reduced transparency preserve labels and selected state;
- reduced motion preserves the same camera/selection outcome;
- keyboard, pointer, Voice Control, and Switch Control have an equivalent task path.

## Privacy and trust

Separate fixed maps, search, device location, and AI context. A person can browse a fixed map without granting location access. If a “near me” action needs location, ask in context and label approximate/reduced accuracy. Do not retain a continuous location trail for a one-shot map action.

If precise coordinates or search history enter an AI context, explain the purpose, minimize the fields, and retain only what the feature needs. Keep raw coordinates out of logs and analytics. For shared widgets, Live Activities, or collaboration, project only the minimum place/status data needed by that surface.

## Design review checklist

- The first screen names the map task and keeps the selected place/route understandable without interpreting pixels.
- MapKit native controls are preferred where they meet the task; custom Liquid Glass has a clear hierarchy reason.
- Camera recenter/fit actions respect user positioning and use explicit fallbacks.
- Search, viewport results, selection, Look Around, and directions have loading/empty/error/cancelled states.
- Search results and map features remain drafts until the user confirms an app-owned record.
- AI proposals reference source IDs, show validation, and separate edit/approve/discard from map facts.
- Accessibility, Dynamic Type, RTL, reduced motion/transparency, and alternate input are designed before visual polish.
- Physical-device and signed/release evidence are planned for claims involving location, service availability, map performance, or system handoff.

## Sources

- [MapKit for SwiftUI](https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui)
- [Map](https://developer.apple.com/documentation/mapkit/map)
- [MapCameraPosition](https://developer.apple.com/documentation/mapkit/mapcameraposition)
- [MapCamera](https://developer.apple.com/documentation/mapkit/mapcamera)
- [MapCameraBounds](https://developer.apple.com/documentation/mapkit/mapcamerabounds)
- [MapReader](https://developer.apple.com/documentation/mapkit/mapreader)
- [MapProxy](https://developer.apple.com/documentation/mapkit/mapproxy)
- [MapFeature](https://developer.apple.com/documentation/mapkit/mapfeature)
- [MapSelection](https://developer.apple.com/documentation/mapkit/mapselection)
- [MapPolyline](https://developer.apple.com/documentation/mapkit/mappolyline)
- [MKLocalSearch](https://developer.apple.com/documentation/mapkit/mklocalsearch)
- [MKLocalPointsOfInterestRequest](https://developer.apple.com/documentation/mapkit/mklocalpointsofinterestrequest)
- [MKMapItem](https://developer.apple.com/documentation/mapkit/mkmapitem)
- [MKDirections](https://developer.apple.com/documentation/mapkit/mkdirections)
- [MKLookAroundSceneRequest](https://developer.apple.com/documentation/mapkit/mklookaroundscenerequest)
- [LookAroundPreview](https://developer.apple.com/documentation/mapkit/lookaroundpreview)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
