# SwiftUI MapKit, location, and place-exploration recipes

## Recipe rules

These snippets are route starters for a named app target. They are not
compiled in this documentation workspace and do not prove MapKit rendering,
service availability, location authorization, search freshness, Look Around,
directions, WeatherKit attribution, AI grounding, accessibility, performance,
or release configuration.

Before copying:

1. Confirm the selected SDK initializer, modifier, availability, entitlement,
   and target-specific behavior.
2. Decide whether the feature actually needs Core Location permission.
3. Keep app IDs, framework observations, map session/camera generations,
   proposals, and committed records separate.
4. Add cancellation and stale-generation checks around search, weather,
   directions, Look Around, and AI work.
5. Provide a list/detail route and test physical devices, map styles,
   Dynamic Type, VoiceOver, reduced effects, and release builds.

Tilde fences keep the examples copyable inside this Markdown page.

## 1. App-owned place and map shell

Start with stable app-owned values. A map projection should not become the
canonical data store.

~~~swift
import MapKit
import SwiftUI

struct SavedPlace: Identifiable, Hashable, Sendable {
    let id: UUID
    let title: String
    let subtitle: String?
    let coordinate: CLLocationCoordinate2D

    static func == (lhs: Self, rhs: Self) -> Bool {
        lhs.id == rhs.id
    }

    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
}

struct PlacesMap: View {
    let places: [SavedPlace]
    @Binding var position: MapCameraPosition
    @Binding var selection: MapSelection<UUID>?

    var body: some View {
        Map(position: $position, selection: $selection) {
            ForEach(places) { place in
                Marker(
                    place.title,
                    systemImage: "mappin",
                    coordinate: place.coordinate
                )
                .tag(place.id)
            }
        }
        .mapStyle(.standard)
    }
}
~~~

Verify the target's generic selection type and Map initializer. Keep the fixed
map usable when Core Location is denied.

## 2. Camera commands versus user positioning

Do not let a refresh snap the person back after they explore.

~~~swift
@MainActor
final class CameraState: ObservableObject {
    @Published var position: MapCameraPosition = .automatic
    @Published private(set) var generation = 0
    @Published private(set) var lastCommand: String?

    func fit(_ rect: MKMapRect) {
        generation += 1
        lastCommand = "fit"
        position = .rect(rect)
    }

    func show(_ item: MKMapItem) {
        generation += 1
        lastCommand = "show-place"
        position = .item(item, allowsAutomaticPitch: true)
    }

    func recenter(_ fallback: MapCameraPosition) {
        generation += 1
        lastCommand = "recenter"
        position = .userLocation(
            followsHeading: false,
            fallback: fallback
        )
    }
}
~~~

Use position.positionedByUser to decide whether an automatic command should be
deferred. The exact API and availability should be checked in the named target.

## 3. MapReader coordinate draft

Convert a gesture to a coordinate, then make the result a draft.

~~~swift
struct CoordinateDraftMap: View {
    @Binding var position: MapCameraPosition
    @State private var coordinate: CLLocationCoordinate2D?

    var body: some View {
        MapReader { proxy in
            Map(position: $position) {
                if let coordinate {
                    Marker("Draft", coordinate: coordinate)
                }
            }
            .gesture(
                SpatialTapGesture()
                    .onEnded { value in
                        coordinate = proxy.convert(
                            value.location,
                            from: .local
                        )
                    }
            )
        }
    }
}
~~~

Before reverse geocoding or saving, attach a map session/camera generation,
timestamp, and review state. A coordinate is not a place identity.

## 4. Fit results with MapProxy

Use the proxy for map-aware framing instead of guessing a camera distance.

~~~swift
MapReader { proxy in
    Map(position: $position) {
        ForEach(places) { place in
            Marker(place.title, coordinate: place.coordinate)
        }
    }
    .toolbar {
        Button("Fit places") {
            guard let rect = rectThatFrames(places) else { return }
            position = .camera(proxy.camera(framing: rect))
        }
    }
}
~~~

The geometry helper must handle empty data, one place, invalid coordinates,
large spans, and antimeridian cases. The Fit action is deliberate; do not call
it on every model update.

## 5. Search with a generation token

Search results should carry the query and region that produced them.

~~~swift
@MainActor
final class PlaceSearchModel: ObservableObject {
    enum State: Equatable {
        case idle
        case searching(generation: Int)
        case results
        case noResults
        case failed
    }

    @Published var query = ""
    @Published private(set) var state: State = .idle
    @Published private(set) var items: [MKMapItem] = []

    private var generation = 0
    private var task: Task<Void, Never>?

    func submit(region: MKCoordinateRegion?) {
        generation += 1
        let current = generation
        task?.cancel()

        let text = query.trimmingCharacters(
            in: .whitespacesAndNewlines
        )
        guard !text.isEmpty else {
            items = []
            state = .idle
            return
        }

        state = .searching(generation: current)
        task = Task { [weak self] in
            do {
                let request = MKLocalSearch.Request()
                request.naturalLanguageQuery = text
                if let region {
                    request.region = region
                }
                let response = try await MKLocalSearch(
                    request: request
                ).start()
                try Task.checkCancellation()
                guard let self, self.generation == current else { return }
                items = response.mapItems
                state = items.isEmpty ? .noResults : .results
            } catch is CancellationError {
                // A newer query owns the state.
            } catch {
                guard let self, self.generation == current else { return }
                state = .failed
            }
        }
    }
}
~~~

Confirm the async search signature for the target SDK. For suggestions, use
MKLocalSearchCompleter behind a separate adapter. Typing alone does not save or
confirm a place.

## 6. Viewport points-of-interest request

Tie a viewport search to a camera generation and explicit filter.

~~~swift
struct ViewportSearchRequest: Sendable, Equatable {
    let generation: Int
    let region: MKCoordinateRegion
    let categoryDescription: String
}

actor ViewportSearchService {
    func search(
        region: MKCoordinateRegion,
        filter: MKPointOfInterestFilter?
    ) async throws -> [MKMapItem] {
        let request = MKLocalPointsOfInterestRequest(region: region)
        request.pointOfInterestFilter = filter
        let response = try await MKLocalSearch(
            request: request
        ).start()
        try Task.checkCancellation()
        return response.mapItems
    }
}
~~~

Use debounce and cancellation in the owner. Label results as “in this area,”
not “near you,” unless the person explicitly chose current location.

## 7. Normalize a map item

Convert framework output to an app observation.

~~~swift
struct PlaceObservation: Identifiable, Codable, Sendable {
    let id: UUID
    let title: String
    let subtitle: String?
    let latitude: Double
    let longitude: Double
    let source: String
    let fetchedAt: Date
}

func normalize(
    _ item: MKMapItem,
    source: String,
    now: Date = .now
) -> PlaceObservation? {
    let coordinate = item.placemark.coordinate
    guard CLLocationCoordinate2DIsValid(coordinate) else { return nil }
    return PlaceObservation(
        id: UUID(),
        title: item.name ?? "Unnamed place",
        subtitle: item.placemark.title,
        latitude: coordinate.latitude,
        longitude: coordinate.longitude,
        source: source,
        fetchedAt: now
    )
}
~~~

Use a stable provider identifier when the target/source exposes one and the
product needs re-resolution. Otherwise mark the UUID as a draft identity.

## 8. Core Location state owner

Use the least-privilege permission route and stop updates when the task ends.

~~~swift
import CoreLocation

@MainActor
final class LocationOwner: NSObject, ObservableObject,
    CLLocationManagerDelegate {
    @Published private(set) var status:
        CLAuthorizationStatus = .notDetermined
    @Published private(set) var accuracy:
        CLAccuracyAuthorization = .reducedAccuracy
    @Published private(set) var location: CLLocation?

    private let manager = CLLocationManager()

    override init() {
        super.init()
        manager.delegate = self
        status = manager.authorizationStatus
        accuracy = manager.accuracyAuthorization
    }

    func request() {
        manager.requestWhenInUseAuthorization()
    }

    func start() {
        manager.startUpdatingLocation()
    }

    func stop() {
        manager.stopUpdatingLocation()
    }

    func locationManagerDidChangeAuthorization(
        _ manager: CLLocationManager
    ) {
        status = manager.authorizationStatus
        accuracy = manager.accuracyAuthorization
    }

    func locationManager(
        _ manager: CLLocationManager,
        didUpdateLocations locations: [CLLocation]
    ) {
        location = locations.last
    }
}
~~~

Newer SDKs may prefer async live updates or a LocationButton/LocationButton
route. Confirm availability. Test denied, reduced, precise, Settings-changed,
services-off, and background behavior.

## 9. Look Around state

Keep the place identity and scene state separate.

~~~swift
enum LookAroundState: Equatable {
    case idle
    case loading(placeID: UUID)
    case ready(placeID: UUID)
    case noImagery(placeID: UUID)
    case failed(placeID: UUID)
}

func loadLookAround(
    for coordinate: CLLocationCoordinate2D
) async throws -> MKLookAroundScene? {
    let request = MKLookAroundSceneRequest(coordinate: coordinate)
    return try await request.scene
}
~~~

The exact async property/availability should be confirmed in the named SDK.
No scene is a valid state. The preview is imagery, not proof of current
opening status, safety, access, or ownership.

## 10. Route review with confirmed inputs

Keep directions as a calculation record.

~~~swift
struct DirectionInputs: Codable, Sendable, Equatable {
    let requestID: UUID
    let sourcePlaceID: UUID
    let destinationPlaceID: UUID
    let transportDescription: String
    let requestedAt: Date
}

struct RouteCandidate: Codable, Sendable, Equatable {
    let inputs: DirectionInputs
    let routeID: String
    let distanceMeters: Double
    let expectedTravelTime: Double
    let isStale: Bool
}
~~~

Use MKDirections with user-confirmed source/destination/transport. Display
alternatives and make route handoff a separate explicit action. Do not claim
navigation completion or road safety from a route overlay.

## 11. Weather context

Keep WeatherKit data tied to place and response date.

~~~swift
import WeatherKit

struct PlaceWeatherState: Sendable, Equatable {
    let placeID: UUID
    let requestedAt: Date
    let observedDate: Date?
    let summary: String
    let isStale: Bool
}

func fetchCurrentWeather(
    for location: CLLocation
) async throws -> CurrentWeather {
    let service = WeatherService.shared
    return try await service.weather(
        for: location,
        including: .current
    )
}
~~~

The exact WeatherKit entitlement, attribution, query, and availability
behavior are target-sensitive. Show attribution and date; a weather response
is not a permanent place property.

## 12. Typed AI place proposal

Supply known IDs/fields and reject unknown or invented output.

~~~swift
struct PlaceProposalInput: Codable, Sendable {
    let mapGeneration: Int
    let sourcePlaceIDs: [UUID]
    let selectedFields: [String]
    let routeIDs: [String]
}

struct PlaceProposal: Codable, Sendable, Equatable {
    let proposalID: UUID
    let mapGeneration: Int
    let sourcePlaceIDs: [UUID]
    let title: String
    let explanation: String
    let orderedPlaceIDs: [UUID]
    let actions: [String]
}

func validate(
    _ proposal: PlaceProposal,
    against input: PlaceProposalInput
) -> Bool {
    guard proposal.mapGeneration == input.mapGeneration else {
        return false
    }
    let allowed = Set(input.sourcePlaceIDs)
    return Set(proposal.sourcePlaceIDs).isSubset(of: allowed)
        && Set(proposal.orderedPlaceIDs).isSubset(of: allowed)
}
~~~

Foundation Models availability and guided-generation signatures are SDK-
sensitive. Keep the proposal reviewable and call domain save/route/share only
after user acceptance and validation.

## 13. Liquid Glass map controls

Keep map content primary and controls semantic.

~~~swift
struct MapControlBar: View {
    let onSearch: () -> Void
    let onFit: () -> Void
    let onRecenter: () -> Void
    let onSave: () -> Void

    var body: some View {
        HStack {
            Button("Search", systemImage: "magnifyingglass", action: onSearch)
            Button("Fit", systemImage: "scope", action: onFit)
            Button("Recenter", systemImage: "location", action: onRecenter)
            Button("Save", systemImage: "bookmark", action: onSave)
        }
        .padding()
        .glassEffect()
    }
}
~~~

Check the exact Liquid Glass modifier/availability. Provide an opaque fallback,
test satellite/dark/light imagery, and ensure VoiceOver labels explain each
action. Do not put a full decorative glass plane over the map.

## 14. Place detail with explicit destinations

Keep selected observation, proposal, and commit separate.

~~~swift
enum PlaceDestination: String, CaseIterable, Identifiable {
    case save
    case route
    case share
    case discard

    var id: String { rawValue }

    var title: String {
        switch self {
        case .save: "Save place"
        case .route: "Review route"
        case .share: "Share place"
        case .discard: "Discard draft"
        }
    }
}

struct PlaceDestinationChooser: View {
    @Binding var destination: PlaceDestination
    let onContinue: () -> Void

    var body: some View {
        Form {
            Picker("Next action", selection: $destination) {
                ForEach(PlaceDestination.allCases) { value in
                    Text(value.title).tag(value)
                }
            }
            Button("Continue", action: onContinue)
        }
        .navigationTitle("Review place")
    }
}
~~~

Only report success after the selected operation completes. Preserve the
observation/proposal if save/share/route is cancelled or fails.

## 15. Acceptance fixture

Use a deterministic fixture for stale map/service/AI work.

~~~swift
struct MapAcceptanceFixture: Equatable, Sendable {
    let mapGeneration: Int
    let sourcePlaceIDs: [UUID]
    let cameraState: String
    let locationState: String
    let searchState: String
    let lookAroundState: String
    let weatherState: String
    let routeState: String
    let aiState: String
    let destinationState: String
}

let selectedPlaceReview = MapAcceptanceFixture(
    mapGeneration: 8,
    sourcePlaceIDs: [
        UUID(uuidString: "00000000-0000-0000-0000-000000000003")!
    ],
    cameraState: "positioned-by-user",
    locationState: "not-needed",
    searchState: "confirmed-result-with-provenance",
    lookAroundState: "no-imagery-fallback",
    weatherState: "current-with-date-and-attribution",
    routeState: "not-requested",
    aiState: "candidate-requires-review",
    destinationState: "choose-save-route-share-or-discard"
)
~~~

Acceptance should assert:

- fixed browsing works without location permission;
- camera commands do not override user positioning;
- old search/weather/AI work cannot update a new map generation;
- coordinate drafts remain drafts until confirmed;
- selected place identity and source/fetched-at survive detail/reopen;
- no-imagery, no-result, denied, reduced-accuracy, and offline states are useful;
- AI proposals contain only known IDs and cannot start actions automatically;
- list/detail, VoiceOver, Dynamic Type, keyboard, pointer, RTL, and reduced
  effects complete the core task.

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
- [MKPointOfInterestFilter](https://developer.apple.com/documentation/mapkit/mkpointofinterestfilter)
- [MKMapItem](https://developer.apple.com/documentation/mapkit/mkmapitem)
- [MKDirections](https://developer.apple.com/documentation/mapkit/mkdirections)
- [MKRoute](https://developer.apple.com/documentation/mapkit/mkroute)
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
