# SwiftUI MapKit, location, and place exploration

## Purpose

Map features feel native when the map is a source-aware surface rather than a
decorative canvas with pins. MapKit for SwiftUI owns map rendering, camera,
content, map-feature selection, search handoff, Look Around, and overlays.
Core Location owns permission and device readings. WeatherKit owns weather
responses for a requested location. App models own stable places, user
decisions, saved records, and reviewable AI proposals.

Use this flow:

~~~text
fixed/search/map entry
    -> camera and content state
    -> optional location permission and updates
    -> map selection or coordinate draft
    -> search/place/Look Around/weather observation
    -> review and source normalization
    -> optional on-device AI proposal
    -> explicit save, route, share, or system handoff
~~~

This page adds the SwiftUI orchestration seam to the existing [MapKit and
Location deep dive](../41-framework-deep-dives/04-mapkit-and-location.md),
[advanced MapKit for SwiftUI composition](../41-framework-deep-dives/13-mapkit-swiftui-advanced-composition.md),
[least-privilege location route](55-corelocationui-and-least-privilege-location.md),
and [WeatherKit system-data route](../43-system-framework-deep-dives/03-weatherkit-and-system-data.md).

## Capability boundary

| Concern | Framework | App-owned responsibility |
| --- | --- | --- |
| Map pixels/interaction | MapKit for SwiftUI | Task hierarchy, fallback list, semantic labels |
| Camera | MapCameraPosition/MapCamera/MapCameraBounds | Deliberate camera commands, user-positioned state, session generation |
| Content | MapContent/Marker/Annotation/overlays | Stable IDs, provenance, delete/edit, display policy |
| Map feature | MapFeature/MapSelection | Discovery detail, resolution, review, persistence decision |
| Device location | Core Location | Permission explanation, accuracy policy, update lifetime, privacy |
| Search | MKLocalSearch/Completer/POI request | Query/region generation, cancellation, normalization, freshness |
| Look Around | MKLookAroundSceneRequest/LookAroundPreview | Optional imagery state, selected-place identity, no-imagery fallback |
| Directions | MKDirections/MKRoute | Confirmed inputs, alternative review, stale route, no silent navigation |
| Weather | WeatherService/Weather | Location/time/data availability, attribution, stale copy |
| AI proposal | Foundation Models/Core ML | Bounded context, source IDs, validation, review, commit |

A coordinate is not a place identity. A search response is not a saved record.
A weather value is not a guarantee. An AI itinerary is not permission to
change a route or message a person.

## Route contract

Write down:

| Field | Required decision |
| --- | --- |
| User outcome | Browse, select, search, explore, route, weather, save, or share |
| Map entry | Fixed app data, text search, viewport POI, map feature, coordinate draft, or user location |
| Camera owner | Which model owns MapCameraPosition and deliberate commands? |
| Map session | Generation for camera/search/selection/AI work |
| Content identity | App ID, framework ID, coordinate, source, fetched-at, freshness |
| Location | Whether Core Location is needed; when/what accuracy; update stop policy |
| Search | Query, region/viewport, category filter, debounce, cancellation, no-result/error |
| Place detail | Which fields are observations versus app-authored values? |
| Look Around | Scene identity, loading/no imagery/cancelled/error state |
| Directions | Source/destination/transport, alternatives, route revision, explicit handoff |
| Weather | Requested location, datasets, validity date, attribution, failure |
| AI | Allowed place IDs/fields, proposal schema, stale policy, prohibited inference |
| UI | Map/list/detail relation, Liquid Glass control groups, fallback surface |
| Accessibility | Semantic list/detail, labels, focus, alternate input, Dynamic Type |
| Targets | iPhone/iPad/Catalyst/visionOS/watchOS/CarPlay and availability branches |
| Proof | Fixture, compile, UI, simulator, physical, system, performance, archive/release |

## 1. Start with a fixed map when possible

A map-only browsing surface can work without location permission. Use app-owned
places and a stable camera model; add Core Location only when the feature needs
the person's current location.

~~~swift
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

struct SavedPlacesMap: View {
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

The exact Map initializer, selection generic, and content modifiers are
deployment-sensitive. Confirm the target SDK. Keep selection separate from
detail presentation, and keep the map usable when location is denied.

## 2. Treat camera as command plus user observation

MapCameraPosition can represent automatic framing, a region, map rectangle,
map item, explicit camera, or user location with fallback. When the person
pan/zooms, the position can become positionedByUser. Do not continuously
overwrite that state with incoming place refreshes.

~~~swift
@MainActor
final class MapCameraModel: ObservableObject {
    @Published var position: MapCameraPosition = .automatic
    @Published private(set) var sessionGeneration = 0
    @Published private(set) var lastCommand: String?

    func fit(_ rect: MKMapRect) {
        sessionGeneration += 1
        lastCommand = "fit-results"
        position = .rect(rect)
    }

    func show(_ item: MKMapItem) {
        sessionGeneration += 1
        lastCommand = "show-place"
        position = .item(item, allowsAutomaticPitch: true)
    }

    func userMoved() {
        lastCommand = "user-moved"
    }
}
~~~

Use a deliberate command for fit/recenter/show-place. Use a visible recenter
action when the person has explored. Camera generation should scope viewport
search and AI work so late responses cannot repopulate a different map state.

## 3. Use MapReader for provisional coordinate selection

MapReader provides MapProxy for converting between a map coordinate space and
geographic coordinates. Treat a conversion as a coordinate draft.

~~~swift
struct CoordinateDraftMap: View {
    @Binding var position: MapCameraPosition
    @State private var draft: CLLocationCoordinate2D?

    var body: some View {
        MapReader { proxy in
            Map(position: $position) {
                if let draft {
                    Marker("Draft location", coordinate: draft)
                }
            }
            .gesture(
                SpatialTapGesture()
                    .onEnded { value in
                        guard let coordinate = proxy.convert(
                            value.location,
                            from: .local
                        ) else { return }
                        draft = coordinate
                    }
            )
        }
    }
}
~~~

Record map session, camera generation, timestamp, and accuracy/provenance.
Before reverse geocoding, searching, saving, or giving the coordinate to AI,
show a review action. A coordinate can fall on a road, building, water, or
private property and does not itself prove a place name.

## 4. Keep map content and selection stable

App-tagged content should use a stable app ID. The selected ID is not itself
the detail model or permission to mutate it.

Recommended projection:

~~~text
app-owned place record
    -> MapContent projection
    -> selected app ID
    -> detail state
    -> edit/save/delete review
~~~

Use Marker when a system-labeled place marker is appropriate. Use Annotation
for custom content only when the visual customization has equivalent semantic
labels and a list/detail alternative. Use MapPolyline/MapPolygon/MapCircle
for visual geometry and label the meaning; an overlay is not automatically a
route, legal boundary, or user-owned radius.

When selecting an Apple MapFeature, normalize its category/title/coordinate
into a discovery observation. Resolve a place through an explicit user action
when the product needs a durable identity.

## 5. Add Core Location only for a location outcome

Core Location permission is separate from map rendering, search, and fixed
coordinates. Decide whether the feature needs:

- one current location;
- live updates;
- heading/follow behavior;
- region monitoring or background location;
- only a user-selected coordinate.

Use the least-privilege route. Show reduced accuracy as a real state. Stop
updates when no screen or task needs them. Do not label a fallback camera as
current location.

~~~swift
@MainActor
final class LocationStateModel: NSObject, ObservableObject,
    CLLocationManagerDelegate {
    @Published private(set) var authorization:
        CLAuthorizationStatus = .notDetermined
    @Published private(set) var accuracy:
        CLAccuracyAuthorization = .reducedAccuracy
    @Published private(set) var location: CLLocation?

    private let manager = CLLocationManager()

    override init() {
        super.init()
        manager.delegate = self
        authorization = manager.authorizationStatus
        accuracy = manager.accuracyAuthorization
    }

    func requestWhenNeeded() {
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
        authorization = manager.authorizationStatus
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

This is a route sketch. The selected SDK may favor newer async live-update
APIs or a LocationButton/Core Location UI entry point. Test denied, restricted,
reduced, precise, services-disabled, background, and Settings-changed states.

## 6. Search with query and viewport generations

Use MKLocalSearchCompleter for suggestions and MKLocalSearch for a confirmed
query. Use MKLocalPointsOfInterestRequest for explicit viewport/category
search. These requests are service observations, not canonical app data.

~~~swift
struct PlaceSearchRequest: Sendable, Equatable {
    let generation: Int
    let query: String
    let regionDescription: String
    let requestedAt: Date
}

struct PlaceSearchObservation: Sendable, Equatable {
    let request: PlaceSearchRequest
    let items: [PlaceObservation]
}
~~~

Debounce text, cancel or supersede prior requests, retain query/region/
fetched-at with the result, and distinguish no results, offline, denied, and
service failure. A late response is stale when its generation does not match.

Normalize MKMapItem at the adapter boundary. Keep title, subtitle, coordinate,
source query/region, fetched-at, and any stable provider identifier separately.
Do not persist a framework object as the app's domain record.

## 7. Add Look Around as optional imagery

MKLookAroundSceneRequest can return a scene, no scene, cancellation, or error.
LookAroundPreview is a preview/viewer surface, not a proof that the place is
open, safe, current, or accessible.

Model:

~~~swift
enum LookAroundState: Equatable, Sendable {
    case unavailable
    case loading(placeID: UUID)
    case ready(placeID: UUID)
    case noImagery(placeID: UUID)
    case failed(placeID: UUID)
}
~~~

Keep selected place detail above or beside the preview. Provide a no-imagery
state and an accessible address/detail fallback. Retain selected place ID
separately from the scene object.

## 8. Add directions only after confirmation

Directions are a calculation from confirmed inputs. Keep source, destination,
transport, calculation date, alternatives, selected route, and stale status.

~~~swift
struct RouteRequest: Codable, Sendable, Equatable {
    let requestID: UUID
    let sourcePlaceID: UUID
    let destinationPlaceID: UUID
    let transport: String
    let requestedAt: Date
}

struct RouteReview: Codable, Sendable, Equatable {
    let request: RouteRequest
    let routeID: String
    let distanceDescription: String
    let expectedTravelTimeSeconds: Double
    let isStale: Bool
}
~~~

Do not silently start navigation. Show alternatives and ask which route to use
if the product persists or hands off the choice. Recalculate when inputs or
transport changes.

## 9. Weather is location/time context

WeatherService returns data for a CLLocation and can provide current,
hourly/daily, minute, and alert datasets. Weather responses have validity and
availability metadata and require attribution. Keep the requested coordinate,
request time, dataset, and response date in the view state.

~~~swift
struct WeatherContext: Sendable, Equatable {
    let placeID: UUID
    let coordinateDescription: String
    let requestedAt: Date
    let observedDate: Date?
    let summary: String
    let isStale: Bool
}
~~~

Do not present weather as a permanent place attribute. A forecast can be
unavailable or stale. Include required attribution in the final surface and
use the selected target's WeatherKit entitlement/configuration.

## 10. Source-linked on-device AI place proposals

Use AI after MapKit/Core Location/WeatherKit results are deterministic and
source-linked. Good bounded tasks include grouping selected place IDs,
suggesting a title, or comparing route alternatives from known fields.

~~~swift
struct PlaceProposalInput: Codable, Sendable {
    let mapSessionGeneration: Int
    let sourcePlaceIDs: [UUID]
    let selectedFields: [String]
    let routeIDs: [String]
    let weatherContextAllowed: Bool
}

struct PlaceProposal: Codable, Sendable, Equatable {
    let proposalID: UUID
    let mapSessionGeneration: Int
    let sourcePlaceIDs: [UUID]
    let title: String
    let explanation: String
    let orderedPlaceIDs: [UUID]
    let suggestedActions: [String]
}
~~~

Reject unknown/duplicate place IDs, invented coordinates, unsupported opening/
safety claims, unrequested navigation, or actions not in an allowlist. Keep
precise location history and unrelated search content out of context. The
person edits/accepts/discards the proposal; app state or system handoff changes
only through the ordinary validated path.

## 11. Liquid Glass map shell

Use a compact functional shell:

~~~text
map content
    -> selected place/detail state
    -> glass search/filter/camera controls
    -> detail/review card
    -> explicit save/route/share action
~~~

Groups can contain search, filters, recenter, fit results, Look Around, route,
weather, and save actions. Do not cover the whole map with translucent glass.
For satellite/dark imagery or reduced transparency, use a solid fallback with
the same semantics. Test map movement, selection, VoiceOver focus, Dynamic
Type, RTL, keyboard, pointer, and reduced motion.

## 12. Lifecycle and privacy

| Event | Required action |
| --- | --- |
| Map appears | Load app-owned content; do not request location without intent |
| Search text changes | Cancel/debounce; increment query generation |
| Camera moves | Update user-positioned state; debounce viewport search |
| Location permission changes | Refresh authorization/accuracy; stop/start updates deliberately |
| Map session changes | Invalidate coordinate/search/AI work from old generation |
| Look Around disappears | Release scene/view state; keep place identity |
| Route inputs change | Mark route stale and require recalculation |
| Weather date expires | Mark stale; refresh only by policy |
| Scene backgrounds | Stop location updates unless supported policy requires them |
| AI completes | Compare map generation and place IDs before showing Apply |
| Save fails | Keep source observation and proposal recoverable |

Minimize precise location, search history, and weather data retention. Do not
put raw coordinates in analytics identifiers. If the app exports a place, say
which fields and precision are included.

## 13. Target and accessibility boundaries

| Target/input | Route |
| --- | --- |
| iPhone | Map selection, one-handed controls, location/permission, physical motion |
| iPadOS | Split view, pointer, keyboard, larger map/detail composition |
| Mac Catalyst | Search/file/menu/detail adaptation; verify map/API availability |
| visionOS | Spatial map/detail composition; do not assume iPhone camera/map shell |
| watchOS | Companion place/status handoff rather than full map editor |
| CarPlay | Driving-safe system templates and restricted interactions |
| VoiceOver | List/detail representation of map content and actions |
| Keyboard/pointer | Search, selection, recenter, fit, detail, route, save, close |

## Stop conditions

Stop and resolve the seam when:

- a map preview is treated as physical/service/system proof;
- a fixed map requests live location without a user-facing reason;
- camera updates constantly override user positioning;
- a coordinate is persisted as a place without review/provenance;
- a late search/weather/AI response can populate a new map generation;
- a search result or map feature becomes domain truth automatically;
- weather is shown without date/availability/attribution policy;
- a route is drawn and presented as navigation or a safety guarantee;
- a model invents coordinates/place IDs or silently starts a system action;
- map pixels or pin colors are the only accessible representation;
- Liquid Glass obscures the map or communicates location state by color alone;
- simulator/fixed-preview evidence is presented as physical location or service proof.

## Sources

- [MapKit for SwiftUI](https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui)
- [Map](https://developer.apple.com/documentation/mapkit/map)
- [MapContentBuilder](https://developer.apple.com/documentation/mapkit/mapcontentbuilder)
- [MapContent](https://developer.apple.com/documentation/mapkit/mapcontent)
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
- [MapStyle](https://developer.apple.com/documentation/mapkit/mapstyle)
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
- [Weather](https://developer.apple.com/documentation/weatherkit/weather)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
