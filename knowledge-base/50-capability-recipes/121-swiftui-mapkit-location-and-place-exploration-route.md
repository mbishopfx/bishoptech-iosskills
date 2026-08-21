# SwiftUI MapKit, location, and place exploration route

This route is for map-heavy iOS 26 surfaces that need to combine SwiftUI composition, MapKit content, optional Core Location, place search, Look Around, directions, WeatherKit context, and a reviewable on-device AI layer. The route keeps the map, current-location authority, network-backed place identity, generated proposal, and user-approved side effect as separate state domains.

Related pages:

- [SwiftUI MapKit, location, and place exploration](../42-framework-deep-dives/90-swiftui-mapkit-location-and-place-exploration.md)
- [SwiftUI MapKit, location, and place exploration design](../21-design-deep-dives/118-swiftui-mapkit-location-and-place-exploration-design.md)
- [SwiftUI MapKit, location, and place exploration proof matrix](../60-verification/115-swiftui-mapkit-location-and-place-exploration-proof-matrix.md)
- [SwiftUI MapKit, location, and place exploration recipes](../70-code-recipes/133-swiftui-mapkit-location-and-place-exploration-recipes.md)

## Route contract

The feature is complete only when the following contract is explicit:

| Concern | App-owned contract | Evidence to collect |
| --- | --- | --- |
| Map entry | A fixed region, saved place, deep link, or user-location request determines the initial entry mode. | Cold launch and deep-link fixture showing the expected camera and visible controls. |
| Camera | App commands are separate from a `MapCameraPosition` binding that can be changed by the user. | Command-to-camera test and a post-pan state record showing `positionedByUser` behavior. |
| Content | Every marker, annotation, feature, and overlay has stable identity and a source revision. | Fixture showing content diffing, selection, and stale-response rejection. |
| Selection | A selected place or map feature is normalized before it reaches detail or AI review. | Selection fixture with known place, unknown feature, and deselection. |
| Location | A single owner requests authorization, observes authorization/accuracy, and starts/stops updates. | Permission matrix, accuracy state, update teardown, and physical-device trace. |
| Search | Text and viewport searches use cancellable generations and never silently replace newer results. | Query generation log with delayed and out-of-order responses. |
| Imagery | Look Around and map tiles are optional service results, not required for the core place record. | Coverage fixture showing unavailable imagery without breaking the detail route. |
| Directions | Route calculation begins only with confirmed source, destination, transport, and policy. | Review screen and route result fixture; no route begins from an unreviewed AI guess. |
| Weather | Weather is labeled with location/time freshness, attribution, and unavailable states. | Weather cache/freshness fixture and attribution screenshot. |
| AI | A local model may rank or summarize source-linked places, but it cannot invent identity, coordinates, route safety, or service availability. | Proposal fixture with source IDs, validation failures, rejection, and explicit acceptance. |
| Native shell | Liquid Glass is applied to functional controls and grouped content while the map remains the visual field. | Light/dark, accessibility, reduced-transparency, and target-device screenshots. |

## State machine

Use separate states instead of one broad `loading` flag:

~~~text
Entry
  -> fixedMap | locationRequest | savedPlace | deepLink

Location
  -> notRequested | denied | restricted | reducedAccuracy | fullAccuracy | updating | stale | unavailable

Search
  -> idle | typing | searching(generation) | results(generation) | empty | failed(generation)

Selection
  -> none | mapFeature | normalizedPlace | draftCoordinate | routeReview

Enrichment
  -> noLookAround | loadingLookAround | lookAround | noWeather | loadingWeather | weather

AI proposal
  -> unavailable | preparing | proposed(sourceRevision) | needsReview | accepted | rejected | stale

Side effect
  -> none | openingMaps | calculatingDirections | savingPlace | sharing | complete | failed
~~~

The UI may project these states into a compact status model, but the underlying owners should remain distinct. A search result arriving after a newer viewport generation is stale even if it is otherwise valid. A proposal is stale when its source place revision, coordinate, or selected transport mode changes.

## 1. Choose fixed versus location-aware entry

Start with the least privileged flow that satisfies the product:

1. Fixed map or saved-place browsing: use a known region and do not request location.
2. Search near a user-selected region: use the map viewport or a typed place without location authorization.
3. “Near me” search: explain the value, request the minimum authorization, then show the current authorization and accuracy state.
4. Continuous navigation or live proximity: use a dedicated location owner and a documented update policy; do not let a view callback become the service owner.

This keeps a useful map available when the user denies location and prevents the app from requesting sensitive access merely to render a map.

## 2. Own camera commands separately from user movement

The camera binding is a state projection, not a command bus. Keep commands typed and one-shot:

~~~swift
enum MapCommand: Equatable {
    case showSavedPlace(id: UUID)
    case fitPlaces
    case showUser
    case restoreEntry
}

@MainActor
final class MapRouteModel: ObservableObject {
    @Published var position: MapCameraPosition = .automatic
    @Published private(set) var lastCommand: MapCommand?

    func apply(_ command: MapCommand, savedPlace: MKMapItem? = nil) {
        lastCommand = command
        switch command {
        case .showSavedPlace:
            if let savedPlace { position = .item(savedPlace) }
        case .fitPlaces:
            position = .automatic
        case .showUser:
            position = .userLocation(fallback: .automatic)
        case .restoreEntry:
            position = .automatic
        }
    }
}
~~~

The exact SDK spelling of a route sketch must be checked against the project deployment target. The design contract is stable: a command is recorded, translated into a camera value, and allowed to yield to user movement. Never infer that a camera value is still app-owned after the user pans or zooms.

If a feature requires a bounded geographic area, use camera bounds or an explicit viewport policy. The policy should define whether the user may leave the area, whether search follows the viewport, and how the UI communicates that constraint.

## 3. Give every map item stable identity

Do not use array position as identity. Normalize `MKMapItem`, `MapFeature`, saved places, and AI candidates into an app-owned record:

~~~swift
struct PlaceRecord: Identifiable, Equatable, Sendable {
    let id: String
    let title: String
    let subtitle: String?
    let latitude: Double
    let longitude: Double
    let source: Source
    let sourceRevision: String

    enum Source: String, Sendable {
        case localSearch
        case viewportSearch
        case saved
        case userCoordinate
    }
}
~~~

The ID policy should prefer an official MapKit place identifier when one is available, then use a documented fallback only for the lifetime of the local result. Include the source and revision so an AI suggestion can say exactly which record it used. A coordinate alone is a draft location, not proof of a named place.

## 4. Use `MapReader` for coordinate drafts, not silent writes

Map-to-screen and screen-to-map conversion is useful for “drop a pin,” map-note, and itinerary-building flows. Keep the result as a draft until the user confirms it:

~~~swift
MapReader { proxy in
    Map(position: $model.position, selection: $model.selection) {
        ForEach(model.places) { place in
            Marker(place.title, coordinate: CLLocationCoordinate2D(
                latitude: place.latitude,
                longitude: place.longitude
            ))
            .tag(place.id)
        }
    }
    .onTapGesture { point in
        guard let coordinate = proxy.convert(point, from: .local) else { return }
        model.coordinateDraft = CoordinateDraft(
            latitude: coordinate.latitude,
            longitude: coordinate.longitude
        )
    }
}
~~~

Treat coordinate conversion as optional. A failed conversion, a tap on a control, or an unavailable map projection should leave the existing draft unchanged. Present the draft coordinate with an explicit “use this point” or “search here” action before saving, routing, or sending it to an AI model.

## 5. Separate map content, selection, and overlays

Use `MapContentBuilder` for map content and keep visual layers semantically distinct:

- markers and annotations represent app-owned places or clearly labeled user drafts;
- `MapFeature` selection represents a map-provided feature and must be normalized before detail use;
- polylines represent a calculated or imported route with a route revision;
- polygons and circles represent a stated region, radius, or boundary policy;
- user-location content is system-provided state and should not be copied into a saved place without confirmation;
- a glass control group belongs above the map and should not be mistaken for map content.

When selection is enabled, selection identity must be stable across refreshes. If the selected record disappears, clear or reconcile selection rather than showing detail for a record that is no longer in the visible result set.

## 6. Make one object the Core Location owner

The location owner should:

1. expose current authorization and accuracy as observable state;
2. request authorization only after the feature explanation and user intent;
3. start updates only for an active consumer;
4. stop or downgrade updates when the route leaves the foreground or no consumer remains;
5. publish timestamp, horizontal accuracy, source, and freshness with every location value;
6. keep denied, restricted, reduced-accuracy, and unavailable states actionable;
7. avoid sending raw location to the local model unless the feature explicitly requires it.

Use the async live-update API or delegate-based manager flow consistently within the owner. Mixing two update mechanisms in different views makes authorization and teardown behavior difficult to reason about. When the app only needs a one-time approximate region, do not keep a high-frequency stream alive.

The `Info.plist` usage description is part of the route contract. Test the first request, a denied request, limited/reduced accuracy, an authorization change in Settings, and the case where a user never grants access.

## 7. Search with generations and cancellation

Text search and viewport search are different intents:

| Intent | Input | Cancellation policy | Result use |
| --- | --- | --- | --- |
| Completion | Partial text | Cancel on query change or focus loss | Suggestions only; do not treat as a place identity. |
| Local search | Confirmed query plus region/filter | Cancel when query, region, or filter changes | Normalized places and map content. |
| Viewport POI | Visible map region plus category filter | Cancel when the viewport generation changes | Nearby map content; do not overwrite typed-search results. |
| Saved-place refresh | Stable place ID | Cancel on removal or scene teardown | Enrichment only; preserve saved identity. |

Store a monotonically increasing generation with each request. Before applying a result, confirm that the generation and input signature still match. Keep network/service failures visible as failures or stale data; never turn them into an empty successful result.

~~~swift
struct SearchGeneration: Equatable, Sendable {
    let number: Int
    let query: String
    let regionSignature: String
}

@MainActor
func runSearch(_ input: SearchInput) async {
    searchTask?.cancel()
    let generation = searchStore.begin(input)
    searchTask = Task {
        do {
            let response = try await searchStore.search(input)
            try Task.checkCancellation()
            guard searchStore.isCurrent(generation) else { return }
            searchStore.apply(response, for: generation)
        } catch is CancellationError {
            // Cancellation is an expected state transition.
        } catch {
            guard searchStore.isCurrent(generation) else { return }
            searchStore.fail(error, for: generation)
        }
    }
}
~~~

The route sketch intentionally leaves the concrete `MKLocalSearch.Request` configuration to the app. The request should carry the natural-language query, region, point-of-interest filter, and result-type policy that the user can understand.

## 8. Treat Look Around, directions, and weather as optional enrichments

Look Around imagery is a useful detail surface but may be unavailable by region, place, network, or service response. Keep the place detail route useful without it. A loading placeholder, unavailable message, or static map context should preserve the user’s selected place.

Directions should use confirmed `MKMapItem` inputs or confirmed coordinates plus an explicit transport type. Before calculating, show the source, destination, mode, and any user-visible route policy. A local model can suggest a destination or ordering, but it must not silently start directions.

WeatherKit belongs in a freshness-labeled context card. Keep the queried coordinate, query time, data timestamp if available, attribution requirement, and service error separate from the place’s identity. Weather data may represent a model prediction or service-derived condition rather than a direct observation; phrase the UI accordingly.

## 9. Add an on-device AI proposal layer only after normalization

The safe pipeline is:

~~~text
MapKit/Core Location/WeatherKit records
  -> normalized source bundle with IDs, coordinates, timestamps, and revisions
  -> local model proposal
  -> typed validation and policy checks
  -> native review card
  -> explicit accept/reject/edit
  -> app-owned action or system handoff
~~~

Useful local proposals include:

- ranking already returned places against a stated user preference;
- summarizing a selected place from supplied fields;
- grouping a confirmed set of places into a draft itinerary;
- explaining a route choice using confirmed route fields;
- generating a short, source-linked note for a saved place.

The model must not be treated as authoritative for place names, coordinates, opening hours, weather, road conditions, legal restrictions, or service coverage. The proposal should carry source IDs, source revision, model availability, generation status, and a validation result. If the model is unavailable, the deterministic map/search flow remains complete.

## 10. Compose a Liquid Glass map shell

Keep the map as the spatial field and place functional controls in a small number of grouped surfaces:

- a top search or query field;
- a compact map-control group for location, layers, and recentering;
- a bottom accessory or sheet for the selected place;
- a review card for AI-generated itinerary or note proposals;
- a route-review group before opening Maps or calculating directions.

Use native materials and controls where they communicate platform behavior. Apply custom Liquid Glass only to a bounded functional group that needs a distinct container. Avoid glass behind every marker, every row, and every label. The grouped controls should remain legible over light and dark map imagery, Dynamic Type, increased contrast, reduced transparency, VoiceOver, keyboard, pointer, and touch input.

If the glass effect is unavailable or inappropriate for a target, preserve the functional grouping with an opaque or system-material fallback. The fallback is part of the design, not an error state.

## 11. Define destinations explicitly

Every action should name its destination:

| Action | Destination |
| --- | --- |
| Select a marker | App-owned place detail. |
| Select a map feature | Normalized feature detail or search result. |
| Save a place | Local persistence with source revision and user confirmation. |
| Add a coordinate draft | Draft editor; no implicit place claim. |
| Open Look Around | Optional imagery detail. |
| Get directions | Review, then `MKDirections` or Maps handoff. |
| Share a place | `Transferable`/share sheet with a privacy-reviewed representation. |
| Ask local AI | Source-linked proposal review. |
| Open current weather | Weather context with freshness and attribution. |

This prevents an AI proposal, map tap, or stale search response from becoming an external side effect by accident.

## 12. Verification gates

Before calling the route ready, prove each layer independently:

- compile the named app target with the intended SDK and deployment target;
- launch with a fixed map and no location permission;
- test search completion, text search, viewport search, cancellation, and out-of-order responses;
- test marker, annotation, map-feature, overlay, and deselection behavior;
- test MapReader coordinate conversion success and failure;
- test denied, restricted, reduced-accuracy, full-accuracy, stale, and unavailable location states;
- test Look Around unavailable and available states;
- test directions review and route-result failure;
- test WeatherKit entitlement/configuration, attribution, freshness, and failure states;
- test AI unavailable, loading, valid proposal, invalid proposal, stale proposal, rejection, and acceptance;
- test VoiceOver, Dynamic Type, reduced motion/transparency, increased contrast, keyboard, pointer, and touch;
- test network loss and service latency without losing the selected place;
- test a physical device for location/compass/service behavior and the actual system handoff;
- test an archive/release build for privacy strings, entitlements, target membership, and asset/configuration completeness.

Do not close the route on a simulator pin, a screenshot, a successful compile, or a plausible AI itinerary alone.

## Sources

- [MapKit for SwiftUI](https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui)
- [Map](https://developer.apple.com/documentation/mapkit/map)
- [MapCameraPosition](https://developer.apple.com/documentation/mapkit/mapcameraposition)
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
- [MKPointOfInterestFilter](https://developer.apple.com/documentation/mapkit/mkpointofinterestfilter)
- [MKMapItem](https://developer.apple.com/documentation/mapkit/mkmapitem)
- [MKLookAroundSceneRequest](https://developer.apple.com/documentation/mapkit/mklookaroundscenerequest)
- [LookAroundPreview](https://developer.apple.com/documentation/mapkit/lookaroundpreview)
- [MKDirections](https://developer.apple.com/documentation/mapkit/mkdirections)
- [MKRoute](https://developer.apple.com/documentation/mapkit/mkroute)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [CLLocationManager](https://developer.apple.com/documentation/corelocation/cllocationmanager)
- [CLAuthorizationStatus](https://developer.apple.com/documentation/corelocation/clauthorizationstatus)
- [CLLocationUpdate](https://developer.apple.com/documentation/corelocation/cllocationupdate)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/corelocation/requesting-authorization-to-use-location-services)
- [Adopting live updates in Core Location](https://developer.apple.com/documentation/corelocation/adopting-live-updates-in-core-location)
- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [WeatherService](https://developer.apple.com/documentation/weatherkit/weatherservice)
- [CurrentWeather](https://developer.apple.com/documentation/weatherkit/currentweather)
- [Weather](https://developer.apple.com/documentation/weatherkit/weather)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
