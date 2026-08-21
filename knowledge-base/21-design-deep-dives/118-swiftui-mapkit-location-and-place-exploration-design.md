# SwiftUI MapKit, location, and place-exploration design

## Design goal

Make a place task legible across map pixels, list/detail content, location
permission, service responses, and user-approved actions.

Use this hierarchy:

~~~text
map or search entry
    -> camera/content context
    -> selected place or coordinate draft
    -> detail / Look Around / weather / route review
    -> optional AI suggestion
    -> save, share, route, or discard
~~~

The map is a spatial index and a visual context. It is not the only content
representation. Pair it with a list, detail card, or accessible route so a
person can complete the task without interpreting pin position or map motion.

This page extends the existing [MapKit Liquid Glass place-exploration
design](86-mapkit-liquid-glass-place-exploration-design.md) with a SwiftUI
state/permission/review boundary.

## Choose the entry

| Goal | Entry surface | Permission |
| --- | --- | --- |
| Browse saved places | Map + list/detail | None if data is app-owned |
| Search for a place | Search field + map/list results | None for explicit search |
| Explore a map feature | Tap/select + detail | None for map data |
| Pick a coordinate | MapReader + draft confirmation | None unless current location is needed |
| Show my location | LocationButton or explicit location action | Core Location |
| Show weather at a place | Place detail weather section | WeatherKit entitlement/data |
| Explore imagery | Look Around preview | No device location required; imagery may be unavailable |
| Plan a trip | Source/destination review + alternatives | Location optional; route service |
| Organize places | AI proposal card with known IDs | Depends on input context, not automatically location |

Do not request location permission simply because a map exists. Ask at the
moment the person chooses a current-location feature and provide a fixed/search
fallback.

## Map as a layered composition

Use four layers:

1. map content: markers, annotations, overlays, and camera;
2. contextual controls: search, filters, recenter, fit, map style;
3. selected-place detail: title, address, provenance, actions;
4. review/commit: save, route, share, weather, AI proposal.

Liquid Glass belongs mostly in layers 2–4. It should not form a full-screen
glass canvas behind the map or obscure labels and selection.

## Camera design

MapCameraPosition has two meanings:

- a command from the app, such as Fit results, Show place, or Recenter;
- an observation that the person moved the map.

Use a visible command label when the action changes the camera. After manual
movement, do not snap back on every data refresh. A recenter control should
explain when it uses current location and what happens if permission is denied.

For bounds:

- use them for a real venue, trip, campus, or geographic task;
- show enough surrounding context to orient the person;
- keep a list/detail alternative when rotation/pitch or zoom is constrained;
- do not use bounds to hide missing data or create a fake Apple Maps clone.

## Place identity and selection

Use a stable app ID for saved places. A map tag, search result, or MapFeature
selection is a discovery event. On selection:

1. announce the selected title/category;
2. open or update a detail state;
3. preserve source and fetched-at;
4. offer explicit actions;
5. require confirmation before saving/editing/sharing.

The detail view should distinguish:

- user-authored title/notes;
- MapKit result title/address/category;
- coordinate precision and source;
- weather observation date;
- Look Around imagery;
- route calculation date;
- AI-generated title/summary.

## Search and viewport design

Suggestions are not results. Results are not saved places. Viewport results are
not current-location results.

Use:

- query text and search completion for text entry;
- explicit submit for a confirmed search;
- map camera/visible region for viewport POI search;
- category filters for a bounded task;
- no-result, offline, cancellation, and stale-result states.

Keep the current query and region visible when a result list opens. If the
person moves the map, show “Search this area” instead of silently replacing a
carefully chosen result list.

## Coordinate draft design

A map tap should create a draft:

~~~text
tap location
    -> pin draft
    -> coordinate/provenance detail
    -> optional resolve/search
    -> confirm name/address
    -> save or discard
~~~

Do not label a coordinate with a reverse-geocoded street address without
showing that it is a service-derived approximation. Let the person correct the
place title, move the pin, or cancel.

## Current location and accuracy

When a feature uses current location:

- explain why before the system prompt;
- identify approximate/reduced accuracy;
- show a fallback when services are disabled;
- do not center the map repeatedly as updates arrive;
- stop updates when the task ends;
- avoid putting precise coordinates in logs/analytics;
- let the person complete search/browse without location where possible.

A current-location button is a system input boundary. The app does not get to
infer a person's presence from a map camera fallback.

## Place detail, Look Around, and weather

Place detail should be the stable semantic center:

~~~text
place title and address
source/fetched-at/selection state
map/Look Around preview
weather with date and attribution
route/share/save actions
optional AI proposal
~~~

Look Around is imagery and may be unavailable. Keep the no-imagery state
compact but useful. Weather is a location/time response, not a permanent
place field; show date, availability, and required attribution. A route is a
calculation with inputs and alternatives, not a navigation guarantee.

## AI place proposals

Use the model only over known, selected context. A good candidate card shows:

- “Suggested itinerary” or “Suggested label”;
- the selected source place IDs;
- what data was used;
- generated-at/model availability;
- Edit, Accept, and Discard;
- a stale state when the map/search/place set changes.

Avoid:

- model-invented coordinates;
- “nearby” claims based on hidden location;
- safety/opening/availability claims not supplied by a verified source;
- a generated route that starts navigation automatically;
- AI text styled like MapKit’s system-provided place facts.

## Liquid Glass control groups

Use small groups with one clear purpose:

- search/filter;
- camera/recenter/fit;
- selected-place actions;
- route/weather/Look Around;
- AI review/accept/discard.

Stable control placement matters while the map moves. Use bottom accessories or
compact floating groups appropriate to width, and preserve safe areas. Provide
opaque fallback for reduced transparency and a list/detail fallback for
assistive technology.

Test map styles, satellite imagery, bright/dark areas, selected states,
offline/error banners, and long place names. A translucent group that works
over standard map tiles may fail over satellite.

## Accessibility and input

The map should have a semantic summary and an alternate representation:

- accessible place list with title/address/category;
- selected state and actions;
- route alternative summary with distance/time;
- Look Around open/close and no-imagery state;
- weather date/condition/attribution;
- AI proposal source and uncertainty.

Support VoiceOver focus without stealing it on every camera update. Support
Voice Control/Switch Control, keyboard, pointer, Dynamic Type, RTL, reduced
motion, contrast, and reduced transparency. A gesture to pan or drop a pin
must have a non-gesture route.

## Target adaptation

| Target | Design |
| --- | --- |
| iPhone | One-handed controls, compact detail, explicit current-location action |
| iPadOS | Map/list split, pointer/keyboard, Stage Manager and multitasking |
| Catalyst | Larger list/detail, menus/shortcuts, file/search-first route |
| visionOS | Spatial map/detail composition and target-specific availability |
| watchOS | Place/status handoff, not a full map editor |
| CarPlay | Driving-safe templates, concise route/status actions |

## Design checklist

- [ ] Map rendering, Core Location, search, weather, and app identity are distinct.
- [ ] Fixed browsing works without current-location permission.
- [ ] Camera commands do not override manual exploration.
- [ ] Search results carry query/region/fetched-at and stale generation.
- [ ] Coordinate taps remain drafts until reviewed.
- [ ] Selected map features have accessible detail/list alternatives.
- [ ] Look Around no-imagery and WeatherKit availability states are useful.
- [ ] Directions show confirmed inputs and alternatives.
- [ ] AI proposals use only known IDs/fields and require review.
- [ ] Save, route, share, and discard have explicit destinations.
- [ ] Liquid Glass controls have task meaning and opaque/reduced-effects fallback.
- [ ] VoiceOver, Dynamic Type, RTL, keyboard, pointer, and reduced motion work.
- [ ] Physical location/service, performance, system, archive, and release proof are planned.

## Sources

- [MapKit for SwiftUI](https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui)
- [Map](https://developer.apple.com/documentation/mapkit/map)
- [MapCameraPosition](https://developer.apple.com/documentation/mapkit/mapcameraposition)
- [MapCamera](https://developer.apple.com/documentation/mapkit/mapcamera)
- [MapCameraBounds](https://developer.apple.com/documentation/mapkit/mapcamerabounds)
- [MapReader](https://developer.apple.com/documentation/mapkit/mapreader)
- [MapProxy](https://developer.apple.com/documentation/mapkit/mapproxy)
- [MapSelection](https://developer.apple.com/documentation/mapkit/mapselection)
- [MapSelectable](https://developer.apple.com/documentation/mapkit/mapselectable)
- [MapFeature](https://developer.apple.com/documentation/mapkit/mapfeature)
- [MapPolyline](https://developer.apple.com/documentation/mapkit/mappolyline)
- [MapPolygon](https://developer.apple.com/documentation/mapkit/mappolygon)
- [MapCircle](https://developer.apple.com/documentation/mapkit/mapcircle)
- [MKLocalSearch](https://developer.apple.com/documentation/mapkit/mklocalsearch)
- [MKLocalSearchCompleter](https://developer.apple.com/documentation/mapkit/mklocalsearchcompleter)
- [MKLocalPointsOfInterestRequest](https://developer.apple.com/documentation/mapkit/mklocalpointsofinterestrequest)
- [MKMapItem](https://developer.apple.com/documentation/mapkit/mkmapitem)
- [MKDirections](https://developer.apple.com/documentation/mapkit/mkdirections)
- [MKLookAroundSceneRequest](https://developer.apple.com/documentation/mapkit/mklookaroundscenerequest)
- [LookAroundPreview](https://developer.apple.com/documentation/mapkit/lookaroundpreview)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [CLLocationManager](https://developer.apple.com/documentation/corelocation/cllocationmanager)
- [CLAuthorizationStatus](https://developer.apple.com/documentation/corelocation/clauthorizationstatus)
- [CLLocationUpdate](https://developer.apple.com/documentation/corelocation/cllocationupdate)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/corelocation/requesting-authorization-to-use-location-services)
- [Adopting live updates in Core Location](https://developer.apple.com/documentation/corelocation/adopting-live-updates-in-core-location)
- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [WeatherService](https://developer.apple.com/documentation/weatherkit/weatherservice)
- [CurrentWeather](https://developer.apple.com/documentation/weatherkit/currentweather)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
