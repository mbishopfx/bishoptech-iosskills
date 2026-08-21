# MapKit Place-Exploration Capability Route

## Route contract

Use this route when an app needs a native map, saved places, place search, map-feature selection, Look Around, directions, or a reviewable AI itinerary. Keep the responsibilities separate:

`MapKit surface -> framework response -> normalized place/route model -> user review -> persisted truth -> optional handoff`

This is a reusable route sketch, not compiled code or proof that any particular deployment target, region, device, or service will support every API.

## Capability decision

| Need | Route | Permission/entitlement note |
| --- | --- | --- |
| Show saved/fixed places | SwiftUI `Map` with `Marker`/`Annotation` | No Core Location permission is needed for fixed content. |
| Convert a tap to a coordinate | `MapReader` and `MapProxy.convert` | Coordinate conversion is not place identity; confirmation and optional resolution follow. |
| Search visible area | `MKLocalPointsOfInterestRequest` | Use the visible/selected region; do not imply the person’s current location. |
| Search by text | `MKLocalSearchCompleter` then `MKLocalSearch` | Debounce and cancel; treat results as service snapshots. |
| Explore imagery | `MKLookAroundSceneRequest` and `LookAroundPreview` | No scene is a normal outcome; keep map/detail fallback. |
| Calculate a trip | `MKDirections` and `MKRoute` | Confirm source, destination, and transport; do not infer navigation completion. |
| Use the person’s location | Core Location adapter plus MapKit | Ask for the smallest authorization at the point of action; model reduced accuracy and no fix. |
| Suggest a trip or label | Foundation Models/Core ML over approved MapKit-derived fields | Model output is a proposal; validate IDs/coordinates and require approval. |

## App-owned models

Do not persist `MKMapItem`, `MKRoute`, or a map view as the domain model. Normalize the boundary into types that carry provenance and lifecycle:

```swift
struct PlaceReference: Identifiable, Sendable {
    let id: UUID
    let title: String
    let subtitle: String?
    let coordinate: CLLocationCoordinate2D
    let source: Source
    let fetchedAt: Date?
    let requiresReview: Bool

    enum Source: Sendable {
        case saved
        case search(query: String)
        case mapFeature
        case userCoordinate
    }
}

struct RouteDraft: Sendable {
    let source: PlaceReference
    let destination: PlaceReference
    let transport: Transport
    var calculatedAt: Date?
    var selectedRouteID: UUID?
    var state: State

    enum Transport: Sendable { case walking, automobile, cycling, transit }
    enum State: Sendable { case draft, calculating, ready, stale, failed(String) }
}
```

Treat the snippet as a design boundary. The production target must decide how coordinates are persisted, whether the selected route needs a stable external identifier, how localization is represented, and how privacy/deletion works.

## Phase 1: map shell

1. Define the task: browse, select, search, explore, compare, or route.
2. Load an app-owned fixture or saved-place projection.
3. Render `Map` with the smallest content type that serves the task.
4. Choose `MapCameraPosition` and optional `MapCameraBounds` deliberately.
5. Keep a list/detail alternative available before adding glass overlays.

The map shell should work with no location permission, no network, empty data, and a failed map service. Use an explicit `MapLoadState` or equivalent app state; do not make a blank map indistinguishable from an empty result set.

## Phase 2: selection and coordinate conversion

For app-owned content, use stable tags and `MapSelection`. For a freeform tap, use `MapReader`/`MapProxy` and a spatial gesture. The result is a `PlaceDraft`, not a save:

`tap -> coordinate -> optional place resolution -> review -> save`

Record a map session ID and camera generation. If the map is replaced before the conversion completes, discard the result. If the coordinate is approximate or has no place match, keep the raw coordinate visible and offer manual naming.

## Phase 3: search

Use a separate coordinator for type-ahead and confirmed search:

```swift
actor PlaceSearchCoordinator {
    private var generation = 0

    func search(query: String, region: MKCoordinateRegion?) async throws -> [PlaceReference] {
        generation += 1
        let current = generation
        try Task.checkCancellation()

        let request = MKLocalSearch.Request()
        request.naturalLanguageQuery = query
        request.region = region
        let response = try await MKLocalSearch(request: request).start()
        try Task.checkCancellation()
        guard current == generation else { return [] }

        return response.mapItems.map { item in
            PlaceReference(
                id: UUID(),
                title: item.name ?? "Unnamed place",
                subtitle: item.placemark.title,
                coordinate: item.placemark.coordinate,
                source: .search(query: query),
                fetchedAt: .now,
                requiresReview: true
            )
        }
    }
}
```

This is intentionally a route sketch: production code must handle stable IDs, actor isolation for framework types, search cancellation, locale, errors, and coordinate validity. A search result can be displayed, but it should not become saved truth without an explicit selection/confirmation action.

For `MKLocalSearchCompleter`, debounce text and carry the query/region into the result. Do not treat every suggestion as a completed search or use a suggestion to trigger a side effect.

## Phase 4: viewport points of interest

When the task is “show what is in this visible area,” derive an `MKCoordinateRegion` from the current camera context and create an `MKLocalPointsOfInterestRequest`. Apply `MKPointOfInterestFilter` when the task has an explicit category. Tie the request to the camera generation and show the region/fetched time in debug/evidence fixtures.

Do not use viewport search as a hidden location tracker. A person can pan a map over a place without being there. Keep the source as `viewport(region)` rather than `currentUserLocation` unless Core Location separately supplied that state.

## Phase 5: Look Around

Create a scene request only for a selected place or coordinate:

```swift
func loadLookAroundScene(for place: MKMapItem) async -> MKLookAroundScene? {
    await withCheckedContinuation { continuation in
        let request = MKLookAroundSceneRequest(mapItem: place)
        request.getSceneWithCompletionHandler { scene, _ in
            continuation.resume(returning: scene)
        }
    }
}
```

The route sketch omits cancellation wiring and should not be copied without adding request ownership. In a real adapter, cancel an in-flight request when selection changes or the detail view disappears. A `nil` scene is expected when imagery is unavailable; retain the selected place and provide map/address actions.

Render `LookAroundPreview` only after the scene is available. Keep a textual place detail and a manual fallback beside it. Look Around imagery is exploratory context, not proof of current operation, access, safety, or identity.

## Phase 6: directions

Calculate only from confirmed source/destination/transport values:

```swift
func calculateRoute(
    from source: MKMapItem,
    to destination: MKMapItem,
    transport: MKDirectionsTransportType
) async throws -> [MKRoute] {
    let request = MKDirections.Request()
    request.source = source
    request.destination = destination
    request.transportType = transport
    let response = try await MKDirections(request: request).calculate()
    return response.routes
}
```

Keep the calculation generation and inputs with the response. Present alternatives as reviewable choices. Persist a `RouteDraft` only after the person selects or confirms it. A route overlay can be drawn with `MapPolyline`, but the route summary and cancellation/recalculation controls must remain available outside the map geometry.

## Phase 7: AI proposal and commit boundary

Give the model only the selected, approved fields it needs:

```swift
struct ItineraryProposal: Codable, Sendable {
    let sourcePlaceIDs: [UUID]
    let orderedPlaceIDs: [UUID]
    let rationale: String
    let proposedTransport: String?
    let generatedAt: Date
}
```

Validate before rendering an apply action:

- every ID exists in the supplied source set;
- ordering contains no unexpected or duplicate IDs unless the product allows them;
- coordinates come from app-owned source records, never generated text;
- transport is one of the supported enum values;
- rationale is clearly presented as generated explanation, not verified fact;
- stale/deleted/unauthorized places invalidate or require re-review;
- applying the proposal calls deterministic MapKit/search/directions code and a normal domain confirmation path.

Never allow a model to directly call `MKDirections`, change the map camera, save a place, start navigation, or share precise location. The tool/action boundary is app-owned and approval-gated.

## Liquid Glass shell route

Use a compact glass group for search/filter/recenter and a selected-place action bar for Look Around, directions, save, and share. Keep the map content visually primary. When the map is moving, avoid placing animated or high-contrast glass over important labels. When reduced transparency or increased contrast is enabled, simplify the shell without removing labels or actions.

Use native SwiftUI controls and MapKit controls first. If a custom glass treatment is needed, keep it in a reusable surface component with:

- semantic labels and hints;
- stable focus order;
- Dynamic Type-compatible text;
- reduced-motion and reduced-transparency variants;
- a non-glass fallback;
- no hidden state that exists only in an icon or map gesture.

## State machine

```text
idle
  -> mapReady
  -> cameraChanged
  -> selecting
  -> placeDraft
  -> placeConfirmed
  -> lookAroundLoading -> lookAroundReady | lookAroundUnavailable
  -> routeCalculating -> routeReady | routeFailed | routeCancelled
  -> aiProposing -> aiReview | aiRejected | aiUnavailable
  -> saved | discarded
```

Orthogonal states include location authorization/accuracy, network/service availability, map session generation, selection identity, accessibility settings, and release configuration. Do not flatten these into one `isLoading` flag.

## Proof route

| Claim | Minimum evidence |
| --- | --- |
| Fixed map works without location permission | Deterministic fixture and denied-location UI run. |
| Camera commands respect user positioning | UI test for fit/recenter plus physical interaction and reset behavior. |
| Selection maps to the correct place | Tagged-content/coordinate fixtures, stale-generation test, and task-based UI run. |
| Search results are current for the shown query/region | Cancellation/generation tests, no-result/service-error fixtures, and recorded query/region/fetched-at state. |
| Look Around is available | Physical target run with supported and unsupported/no-imagery places; never infer from a non-nil request. |
| Directions are reviewable | Source/destination/transport fixture, alternatives/error/cancel tests, and physical service run if the product claims it. |
| AI itinerary is safe to apply | Unknown-ID/duplicate/stale/unsupported-claim rejection fixtures plus explicit edit/approve/discard UI tests. |
| Liquid Glass map shell is usable | Light/dark, satellite/standard, Dynamic Type, RTL, contrast, reduced effects, VoiceOver, pointer, and physical-device runs. |
| Release readiness | Named target compile, entitlements/privacy/configuration inspection, signed artifact, and any system handoff evidence. |

## Sources

- [MapKit for SwiftUI](https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui)
- [Map](https://developer.apple.com/documentation/mapkit/map)
- [MapCameraPosition](https://developer.apple.com/documentation/mapkit/mapcameraposition)
- [MapCameraBounds](https://developer.apple.com/documentation/mapkit/mapcamerabounds)
- [MapReader](https://developer.apple.com/documentation/mapkit/mapreader)
- [MapProxy](https://developer.apple.com/documentation/mapkit/mapproxy)
- [MapSelection](https://developer.apple.com/documentation/mapkit/mapselection)
- [MapFeature](https://developer.apple.com/documentation/mapkit/mapfeature)
- [MapPolyline](https://developer.apple.com/documentation/mapkit/mappolyline)
- [MKLocalSearch](https://developer.apple.com/documentation/mapkit/mklocalsearch)
- [MKLocalSearchCompleter](https://developer.apple.com/documentation/mapkit/mklocalsearchcompleter)
- [MKLocalPointsOfInterestRequest](https://developer.apple.com/documentation/mapkit/mklocalpointsofinterestrequest)
- [MKMapItem](https://developer.apple.com/documentation/mapkit/mkmapitem)
- [MKDirections](https://developer.apple.com/documentation/mapkit/mkdirections)
- [MKLookAroundSceneRequest](https://developer.apple.com/documentation/mapkit/mklookaroundscenerequest)
- [LookAroundPreview](https://developer.apple.com/documentation/mapkit/lookaroundpreview)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
