# MapKit for SwiftUI Place-Exploration Recipes

These are compile-oriented route sketches for native MapKit surfaces. They show ownership and state boundaries; they are not proof that a snippet compiles in a particular iOS 26 target, that a region has MapKit/Look Around coverage, or that a physical device will render the same way.

Shared route:

`app model -> MapKit adapter -> normalized observation -> SwiftUI state -> user review -> committed record`

## Recipe 1: map shell with app-owned places

Use stable app IDs for selection and keep the camera binding in feature state.

```swift
import MapKit
import SwiftUI

struct SavedPlace: Identifiable, Hashable {
    let id: UUID
    let name: String
    let coordinate: CLLocationCoordinate2D

    static func == (lhs: Self, rhs: Self) -> Bool { lhs.id == rhs.id }
    func hash(into hasher: inout Hasher) { hasher.combine(id) }
}

struct SavedPlacesMap: View {
    let places: [SavedPlace]
    @Binding var position: MapCameraPosition
    @Binding var selection: MapSelection<UUID>?

    var body: some View {
        Map(position: $position, selection: $selection) {
            ForEach(places) { place in
                Marker(place.name, coordinate: place.coordinate)
                    .tag(place.id)
            }
        }
        .mapStyle(.standard)
    }
}
```

Route notes:

- The model is app-owned; the map is a projection.
- A selected UUID still needs a lookup, authorization check, and detail state.
- `MapCameraPosition` can be initialized with `.automatic`, `.region`, `.rect`, `.item`, or `.camera` depending on the task.
- Keep fixed-place browsing usable when Core Location is denied.

## Recipe 2: explicit camera commands and bounds

Treat camera changes as commands with an origin so a user-pan is not overwritten by an automatic refresh.

```swift
@MainActor
final class MapFeatureState: ObservableObject {
    @Published var position: MapCameraPosition = .automatic
    @Published private(set) var lastCommand: CameraCommand?

    enum CameraCommand: Equatable {
        case fitResults
        case showPlace(UUID)
        case recenter
        case userMoved
    }

    func fitResults(_ rect: MKMapRect) {
        lastCommand = .fitResults
        position = .rect(rect)
    }

    func noteUserMovement() {
        lastCommand = .userMoved
    }
}
```

Use an app-owned place ID for a production `showPlace` command. Do not use a process-local hash as persistence identity. Apply `MapCameraBounds` to a real task region or distance range, and provide a visible way to exit the constrained task.

## Recipe 3: map-reader coordinate draft

Use `MapReader` when a gesture needs to convert screen coordinates into map coordinates. Keep the result provisional.

```swift
struct CoordinatePickerMap: View {
    @Binding var position: MapCameraPosition
    @State private var draftCoordinate: CLLocationCoordinate2D?

    var body: some View {
        MapReader { proxy in
            Map(position: $position) {
                if let draftCoordinate {
                    Marker("Draft location", coordinate: draftCoordinate)
                }
            }
            .gesture(
                SpatialTapGesture()
                    .onEnded { value in
                        guard let coordinate = proxy.convert(
                            value.location,
                            from: .local
                        ) else { return }
                        draftCoordinate = coordinate
                    }
            )
        }
    }
}
```

Before saving or reverse-geocoding, attach a map session ID, camera generation, timestamp, and an explicit `requiresReview` flag. A coordinate from `MapProxy` is geometry, not a confirmed address or place identity.

## Recipe 4: fit content with `MapProxy`

Use the map-aware proxy rather than guessing camera distance from screen size.

```swift
MapReader { proxy in
    Map(position: $position) {
        ForEach(places) { place in
            Marker(place.name, coordinate: place.coordinate)
                .tag(place.id)
        }
    }
    .toolbar {
        Button("Fit places") {
            let region = regionThatFrames(places)
            position = .camera(proxy.camera(framing: region))
        }
    }
}
```

`regionThatFrames` is app-owned geometry code. Handle an empty collection, invalid coordinates, antimeridian cases, and a single-place minimum span. The toolbar action is a deliberate camera command; it should not fire on every data update after the person has explored the map.

## Recipe 5: viewport points-of-interest search

Bind viewport search to the visible region and cancel stale work.

```swift
actor ViewportPOISearch {
    private var generation = 0

    func search(
        region: MKCoordinateRegion,
        filter: MKPointOfInterestFilter?
    ) async throws -> [MKMapItem] {
        generation += 1
        let current = generation
        try Task.checkCancellation()

        let request = MKLocalPointsOfInterestRequest(region: region)
        request.pointOfInterestFilter = filter
        let response = try await MKLocalSearch(request: request).start()
        try Task.checkCancellation()
        guard current == generation else { return [] }
        return response.mapItems
    }
}
```

This is a route sketch. Verify the selected SDK’s initializer and async signatures in the named target. Use a debounce before calling it, retain the region/fetched-at with the result, and label the source as viewport rather than current user location.

## Recipe 6: text search with supersession

Keep suggestions separate from confirmed searches.

```swift
@MainActor
final class PlaceSearchModel: ObservableObject {
    @Published var query = ""
    @Published private(set) var results: [MKMapItem] = []
    @Published private(set) var state: State = .idle

    enum State { case idle, searching, noResults, failed }
    private var searchTask: Task<Void, Never>?

    func submit(region: MKCoordinateRegion?) {
        searchTask?.cancel()
        let query = query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty else {
            results = []
            state = .idle
            return
        }

        state = .searching
        searchTask = Task { [weak self] in
            do {
                let request = MKLocalSearch.Request()
                request.naturalLanguageQuery = query
                request.region = region
                let response = try await MKLocalSearch(request: request).start()
                try Task.checkCancellation()
                await MainActor.run {
                    guard let self else { return }
                    self.results = response.mapItems
                    self.state = response.mapItems.isEmpty ? .noResults : .idle
                }
            } catch is CancellationError {
                // Expected when the query or region changes.
            } catch {
                await MainActor.run { self?.state = .failed }
            }
        }
    }
}
```

Use `MKLocalSearchCompleter` behind a delegate/adapter for suggestions and submit only an intentional query. The example omits a request-generation token and should add one when multiple actors or adapters can publish results.

## Recipe 7: normalize a selected map item

Convert framework data at the boundary and preserve source information.

```swift
struct PlaceObservation: Identifiable, Sendable {
    let id: UUID
    let title: String
    let subtitle: String?
    let coordinate: CLLocationCoordinate2D
    let observedAt: Date
    let source: Source

    enum Source: Sendable {
        case search(query: String)
        case mapFeature
        case userCoordinate
    }
}

func observe(
    _ item: MKMapItem,
    query: String,
    now: Date = .now
) -> PlaceObservation? {
    let coordinate = item.placemark.coordinate
    guard CLLocationCoordinate2DIsValid(coordinate) else { return nil }
    return PlaceObservation(
        id: UUID(),
        title: item.name ?? "Unnamed place",
        subtitle: item.placemark.title,
        coordinate: coordinate,
        observedAt: now,
        source: .search(query: query)
    )
}
```

Use a stable external identifier when the selected SDK/provider exposes one and the product needs re-resolution. Otherwise treat the generated UUID as a draft identity, not a durable identity across searches. Require a user action before promoting the observation to a saved record.

## Recipe 8: map-feature review

Treat an Apple `MapFeature` selection as a discovery suggestion. The exact selection initializer and map modifier should be checked against the target SDK.

```swift
@State private var featureSelection: MapSelection<MapFeature>?

var featureMap: some View {
    Map(position: $position, selection: $featureSelection) {
        // App-owned markers and annotations can coexist with map features.
    }
    .onChange(of: featureSelection) { _, selection in
        guard let feature = selection?.value else { return }
        draftFeature = FeatureDraft(
            title: feature.title,
            coordinate: feature.coordinate,
            category: feature.pointOfInterestCategory,
            requiresReview: true
        )
    }
}
```

A feature’s title/category/coordinate is not an authorization or a claim that the place is open, safe, owned, or relevant to the person. Render a detail/review state and keep “save” or “use this place” explicit.

## Recipe 9: Look Around scene adapter

Load imagery for a selected map item and preserve the no-scene state.

```swift
@MainActor
final class LookAroundModel: ObservableObject {
    @Published private(set) var scene: MKLookAroundScene?
    @Published private(set) var state: State = .idle
    private var request: MKLookAroundSceneRequest?

    enum State { case idle, loading, ready, unavailable, failed }

    func load(for item: MKMapItem) {
        request?.cancel()
        let request = MKLookAroundSceneRequest(mapItem: item)
        self.request = request
        scene = nil
        state = .loading
        request.getSceneWithCompletionHandler { [weak self] scene, error in
            Task { @MainActor in
                guard let self, self.request === request else { return }
                self.scene = scene
                self.state = scene == nil ? .unavailable : .ready
                if error != nil { self.state = .failed }
            }
        }
    }

    func cancel() {
        request?.cancel()
        request = nil
        state = .idle
    }
}
```

The identity comparison and actor behavior are route-sketch concerns; verify the selected SDK’s object isolation and adapt the ownership model. `LookAroundPreview(initialScene:)` can render when `scene` is non-nil. Keep title/address/actions visible outside the preview.

## Recipe 10: directions and route overlay

Calculate a route from explicit, confirmed inputs, then project its polyline.

```swift
struct CalculatedRoute: Identifiable, Sendable {
    let id: UUID
    let sourceID: UUID
    let destinationID: UUID
    let transport: MKDirectionsTransportType
    let calculatedAt: Date
    let route: MKRoute
}

func calculate(
    source: MKMapItem,
    destination: MKMapItem,
    transport: MKDirectionsTransportType
) async throws -> [MKRoute] {
    let request = MKDirections.Request()
    request.source = source
    request.destination = destination
    request.transportType = transport
    let response = try await MKDirections(request: request).calculate()
    return response.routes
}

Map(position: $position) {
    if let route {
        MapPolyline(route.polyline)
            .stroke(.blue, lineWidth: 5)
    }
}
```

Keep route input IDs, calculation time, alternatives, transport, and stale state outside the polyline. A line on a map is not navigation completion or a safe/legal route. Use a list/detail route for the distance/time/alternative summary.

## Recipe 11: typed AI itinerary proposal

Feed a model only a bounded source set and validate its IDs before rendering an apply action.

```swift
struct ItineraryProposal: Codable, Sendable {
    let sourceIDs: [UUID]
    let orderedIDs: [UUID]
    let explanation: String
    let generatedAt: Date
}

enum ProposalValidationError: Error {
    case unknownSource(UUID)
    case duplicateID(UUID)
    case unsupportedOrder
}

func validate(
    _ proposal: ItineraryProposal,
    against places: [PlaceObservation]
) throws {
    let known = Set(places.map(\.id))
    for id in proposal.orderedIDs {
        guard known.contains(id) else {
            throw ProposalValidationError.unknownSource(id)
        }
    }
    var seen = Set<UUID>()
    for id in proposal.orderedIDs {
        guard seen.insert(id).inserted else {
            throw ProposalValidationError.duplicateID(id)
        }
    }
    guard Set(proposal.sourceIDs).isSuperset(of: proposal.orderedIDs) else {
        throw ProposalValidationError.unsupportedOrder
    }
}
```

The model cannot create coordinates, call `MKDirections`, alter the camera, save a place, or start a system handoff directly. After validation, the app resolves IDs to current domain records, lets the person edit/approve/discard, and calls deterministic MapKit/domain code.

## Recipe 12: Liquid Glass action shell

Keep map content and action state separate. The exact Liquid Glass modifiers must be checked against the selected iOS 26 SDK.

```swift
struct PlaceActionBar: View {
    let place: PlaceObservation
    let lookAroundAvailable: Bool
    let onDirections: () -> Void
    let onSave: () -> Void
    let onLookAround: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Button("Directions", systemImage: "arrow.triangle.turn.up.right.diamond") {
                onDirections()
            }
            if lookAroundAvailable {
                Button("Look Around", systemImage: "binoculars") {
                    onLookAround()
                }
            }
            Button("Save", systemImage: "bookmark") {
                onSave()
            }
        }
        .labelStyle(.titleAndIcon)
        // Apply the project’s native Liquid Glass container/effect here.
        // Preserve a non-glass fallback for reduced transparency/contrast.
        .accessibilityElement(children: .contain)
    }
}
```

The action bar should not be the only place that exposes the selected place’s title, address, or review state. Test it over standard and satellite maps, with long labels, Dynamic Type, VoiceOver, reduced effects, and map movement.

## Recipe 13: deterministic map test fixtures

Use a fake adapter for state tests and keep service/device tests separate.

```swift
struct FakeMapService: Sendable {
    var searchResult: [PlaceObservation] = []
    var lookAroundAvailable = false

    func search(_ query: String) async throws -> [PlaceObservation] {
        searchResult
    }
}

struct MapScenario {
    let name: String
    let places: [PlaceObservation]
    let locale: Locale
    let reduceMotion: Bool
    let reduceTransparency: Bool
}
```

Fixtures should cover no permission, empty data, stale results, no Look Around scene, route failure, unknown AI IDs, long localized labels, RTL, reduced effects, and changed camera generation. A successful fake response does not prove MapKit service delivery.

## Route review checklist

- Keep `Map`, search, directions, Look Around, and Core Location in separate adapters.
- Record query/region/camera generation and fetched/calculated time with service results.
- Cancel or supersede search, viewport, Look Around, and directions work when inputs change.
- Keep map features, search results, and coordinates as drafts until the user confirms the app-owned record.
- Make list/detail and manual alternatives available for map-only state.
- Validate every AI place/itinerary ID against the supplied source set before showing an apply action.
- Use native controls and a restrained Liquid Glass action group; test reduced effects and accessibility.
- Label every snippet as a route sketch until it compiles in the named target.

## Sources

- [MapKit for SwiftUI](https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui)
- [Map](https://developer.apple.com/documentation/mapkit/map)
- [MapCameraPosition](https://developer.apple.com/documentation/mapkit/mapcameraposition)
- [MapCamera](https://developer.apple.com/documentation/mapkit/mapcamera)
- [MapCameraBounds](https://developer.apple.com/documentation/mapkit/mapcamerabounds)
- [MapReader](https://developer.apple.com/documentation/mapkit/mapreader)
- [MapProxy](https://developer.apple.com/documentation/mapkit/mapproxy)
- [MapSelection](https://developer.apple.com/documentation/mapkit/mapselection)
- [MapFeature](https://developer.apple.com/documentation/mapkit/mapfeature)
- [MapPolyline](https://developer.apple.com/documentation/mapkit/mappolyline)
- [MKLocalSearch](https://developer.apple.com/documentation/mapkit/mklocalsearch)
- [MKLocalSearchCompleter](https://developer.apple.com/documentation/mapkit/mklocalsearchcompleter)
- [MKLocalPointsOfInterestRequest](https://developer.apple.com/documentation/mapkit/mklocalpointsofinterestrequest)
- [MKPointOfInterestFilter](https://developer.apple.com/documentation/mapkit/mkpointofinterestfilter)
- [MKMapItem](https://developer.apple.com/documentation/mapkit/mkmapitem)
- [MKDirections](https://developer.apple.com/documentation/mapkit/mkdirections)
- [MKRoute](https://developer.apple.com/documentation/mapkit/mkroute)
- [MKLookAroundSceneRequest](https://developer.apple.com/documentation/mapkit/mklookaroundscenerequest)
- [LookAroundPreview](https://developer.apple.com/documentation/mapkit/lookaroundpreview)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
