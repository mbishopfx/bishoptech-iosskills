# Location, Map, and Weather Recipes

Use the [capability-first Apple SDK atlas](../40-framework-routes/10-capability-first-apple-sdk-atlas.md) to choose one-shot, live, map, search, directions, or weather routes, then keep freshness, accuracy, cancellation, and authorization visible in the [cross-framework feature lifecycle](../41-framework-deep-dives/06-cross-framework-feature-lifecycle.md).

## Scope and compile boundary

These are compile-oriented route sketches for Core Location authorization and accuracy, MapKit SwiftUI presentation, local search, directions, geocoding, and WeatherKit. They are not compiled in this documentation-only workspace and do not prove device accuracy, map-service availability, network latency, weather freshness, entitlement provisioning, background delivery, battery behavior, or App Store readiness.

Keep the boundaries visible:

`permission -> reading/search -> app-owned state -> presentation -> review/persistence`

A `CLLocation`, `MKMapItem`, `MKRoute`, or WeatherKit value is an input to the product. It is not automatically a confirmed address, a current user, a safe route, or a real-time weather measurement.

## Recipe 1: request location at the feature boundary

Start with When In Use access. The target must include truthful usage-description values before the request. A fixed map, saved place, or user-entered area should not request location merely because the app might eventually support “near me.”

```swift
import CoreLocation

final class LocationService: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()

    private(set) var authorization = CLAuthorizationStatus.notDetermined
    private(set) var accuracy = CLAccuracyAuthorization.reducedAccuracy
    private(set) var lastLocation: CLLocation?
    private(set) var lastError: Error?

    override init() {
        super.init()

        // Create and retain the manager on the run-loop/actor that should
        // receive its delegate callbacks. Publish UI state on that boundary.
        manager.delegate = self
    }

    func requestWhenInUseIfNeeded() {
        guard CLLocationManager.locationServicesEnabled() else { return }

        switch manager.authorizationStatus {
        case .notDetermined:
            manager.requestWhenInUseAuthorization()
        case .authorizedWhenInUse, .authorizedAlways:
            break
        case .denied, .restricted:
            // Show a limitation and an intentional Settings/manual route.
            break
        @unknown default:
            break
        }
    }

    func requestTemporaryFullAccuracyIfNeeded() {
        guard manager.authorizationStatus == .authorizedWhenInUse
                || manager.authorizationStatus == .authorizedAlways else {
            return
        }

        // The purpose key must also exist in
        // NSLocationTemporaryUsageDescriptionDictionary.
        manager.requestTemporaryFullAccuracyAuthorization(
            withPurposeKey: "PrecisePlaceSearch"
        )
    }

    func requestOneLocation() {
        guard manager.authorizationStatus == .authorizedWhenInUse
                || manager.authorizationStatus == .authorizedAlways else {
            return
        }

        manager.requestLocation()
    }

    func startForegroundUpdates() {
        guard manager.authorizationStatus == .authorizedWhenInUse
                || manager.authorizationStatus == .authorizedAlways else {
            return
        }

        // Tune these values to the outcome. Do not use navigation-grade
        // accuracy for a feature that only needs a broad local area.
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        manager.distanceFilter = 50
        manager.startUpdatingLocation()
    }

    func stop() {
        manager.stopUpdatingLocation()
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        authorization = manager.authorizationStatus
        accuracy = manager.accuracyAuthorization
    }

    func locationManager(
        _ manager: CLLocationManager,
        didUpdateLocations locations: [CLLocation]
    ) {
        guard let location = locations.last else { return }
        lastLocation = location
        lastError = nil
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        lastError = error
    }
}
```

The service must be owned by a lifecycle-aware feature, not recreated by every view update. Route delegate state to the main actor or the feature’s observation model deliberately. `requestLocation()` is a one-shot request; `startUpdatingLocation()` is a stream and must have an explicit stop path. Do not set `allowsBackgroundLocationUpdates` in this general recipe. Add Always authorization/background configuration only after a product-specific need, privacy review, battery plan, and physical-device test exist.

## Recipe 2: model readings with accuracy and freshness

Keep a reading’s provenance beside its coordinate. Use the fetched/received timestamp in the UI and decide what “fresh enough” means for the feature instead of treating every non-nil location as current.

```swift
import CoreLocation

struct LocationReading {
    let location: CLLocation
    let receivedAt: Date
    let authorization: CLAuthorizationStatus
    let accuracyAuthorization: CLAccuracyAuthorization

    var isApproximate: Bool {
        accuracyAuthorization == .reducedAccuracy
    }

    var horizontalAccuracyMeters: CLLocationAccuracy {
        location.horizontalAccuracy
    }
}

enum LocationFreshness {
    case fresh
    case stale(receivedAt: Date)
    case unavailable(reason: String)
}

func freshness(
    for reading: LocationReading?,
    now: Date = .now,
    maximumAge: TimeInterval
) -> LocationFreshness {
    guard let reading else {
        return .unavailable(reason: "No location has been received")
    }

    guard now.timeIntervalSince(reading.receivedAt) <= maximumAge else {
        return .stale(receivedAt: reading.receivedAt)
    }

    return .fresh
}
```

Do not use `horizontalAccuracy` as a guarantee of application-level correctness. It is an uncertainty value for the reading, and reduced accuracy can still be an intentional user choice. If the product only needs a neighborhood or city, display that outcome rather than requesting or implying a street-level fix.

## Recipe 3: render a map without requesting location

MapKit can render fixed app-owned places without Core Location authorization. Keep the map’s camera state and annotations in the view layer while the app-owned place model remains the source of truth.

```swift
import CoreLocation
import MapKit
import SwiftUI

struct PlacePin: Identifiable {
    let id: UUID
    let name: String
    let coordinate: CLLocationCoordinate2D
}

struct PlaceMap: View {
    let places: [PlacePin]
    @State private var position: MapCameraPosition = .automatic

    var body: some View {
        Map(position: $position) {
            ForEach(places) { place in
                Marker(place.name, coordinate: place.coordinate)
            }
        }
        .mapStyle(.standard)
    }
}
```

Add native map controls and selection behavior in the target project as needed. Provide a list/detail route beside the map so a selected place remains understandable to VoiceOver users, people using large text, and people who need a manual route. A map preview or fixed coordinate does not prove the person’s current position.

## Recipe 4: search confirmed queries with cancellation

Use `MKLocalSearchCompleter` for type-ahead suggestions and `MKLocalSearch` for a confirmed query. Debounce text changes in the UI, cancel superseded work, and carry the query and region into the result state.

```swift
import MapKit

struct PlaceSearchService {
    func search(
        query: String,
        in region: MKCoordinateRegion?
    ) async throws -> [MKMapItem] {
        let request = MKLocalSearch.Request()
        request.naturalLanguageQuery = query

        if let region {
            request.region = region
        }

        let search = MKLocalSearch(request: request)

        return try await withTaskCancellationHandler(operation: {
            let response = try await search.start()
            try Task.checkCancellation()
            return response.mapItems
        }, onCancel: {
            search.cancel()
        })
    }
}
```

The target view model should attach a generation or request ID to this result. If the person changes the query while a response is in flight, cancel the previous task and ignore any result whose ID is no longer current. Preserve a useful prior result while loading the next one if that is clearer than flashing an empty map. Search responses can be empty, partial, delayed, rate-limited, or unavailable; expose those states.

## Recipe 5: calculate a user-confirmed route

Directions need a source, destination, and transport type chosen or confirmed by the person. Keep `MKMapItem` conversion and route presentation at the MapKit boundary; persist an app-owned trip draft rather than a framework object.

```swift
import MapKit

enum DirectionsError: Error {
    case noRoute
}

struct DirectionsService {
    func calculate(
        from source: MKMapItem,
        to destination: MKMapItem,
        transportType: MKDirectionsTransportType
    ) async throws -> [MKRoute] {
        let request = MKDirections.Request()
        request.source = source
        request.destination = destination
        request.transportType = transportType

        let directions = MKDirections(request: request)

        return try await withTaskCancellationHandler(operation: {
            let response = try await directions.calculate()
            try Task.checkCancellation()

            guard !response.routes.isEmpty else {
                throw DirectionsError.noRoute
            }

            return response.routes
        }, onCancel: {
            directions.cancel()
        })
    }
}
```

Show the selected source, destination, transport type, calculation time, route alternatives, and a recalculate/error action. A calculated route can become stale and is not itself turn-by-turn navigation. Do not silently start a trip, send a message, or change durable state from a route response without the product’s confirmation rule.

## Recipe 6: geocode a deliberate user action

Use geocoding for an intentional conversion such as “find this address” or “name this saved place.” Do not reverse-geocode every moving location update. `CLGeocoder` is network-backed and rate-limited; keep one request active per geocoder and cancel it when the query changes.

```swift
import CoreLocation

struct GeocodingService {
    func geocode(
        address: String,
        near region: CLRegion?
    ) async throws -> [CLPlacemark] {
        let geocoder = CLGeocoder()

        return try await withTaskCancellationHandler(operation: {
            let placemarks = try await geocoder.geocodeAddressString(
                address,
                in: region
            )
            try Task.checkCancellation()
            return placemarks
        }, onCancel: {
            geocoder.cancelGeocode()
        })
    }
}
```

Throttle repeated requests, avoid starting a second request before the first completes, and provide manual text/coordinate correction. If the product is really searching for a place or business, use MapKit search instead of turning geocoding into an unbounded directory. Preserve the entered text even when no placemark is returned.

## Recipe 7: request only the WeatherKit dataset needed

Enable the WeatherKit capability in the app target so the WeatherKit entitlement is present. The native Swift API uses `WeatherService` with a `CLLocation` and a selected query. Keep the fetch time and location context in app-owned state, and provide the required attribution in the product.

```swift
import CoreLocation
import WeatherKit

struct WeatherFetch {
    let current: CurrentWeather
    let requestedLocation: CLLocation
    let fetchedAt: Date
}

func fetchCurrentWeather(for location: CLLocation) async throws -> WeatherFetch {
    let service = WeatherService.shared
    let current = try await service.weather(
        for: location,
        including: .current
    )

    return WeatherFetch(
        current: current,
        requestedLocation: location,
        fetchedAt: .now
    )
}

func loadWeatherAttribution() async throws -> WeatherAttribution {
    try await WeatherService.shared.attribution
}
```

`fetchedAt` is the time this app received the response; it is not a claim that the conditions were measured at that exact moment. Preserve any source-provided metadata available for the selected dataset and label the UI accordingly. Request the smallest dataset that satisfies the screen, cache deliberately, and do not request weather on every map-camera change or location update. Handle entitlement/configuration errors, unavailable data, service failures, quota/usage limits, cancellation, and retry.

## Recipe 8: compose a location-sensitive feature state

Make the source and freshness visible to the UI. A saved place can remain useful without a fresh device fix, and weather for a saved place is a different route from weather for “where I am now.”

```swift
enum PlaceSource: Equatable {
    case userEntered
    case mapSearch
    case deviceLocation
    case imported
}

struct AppPlace {
    let id: UUID
    let title: String
    let coordinate: CLLocationCoordinate2D
    let source: PlaceSource
    let resolvedAt: Date?
}

enum LocationFeatureState {
    case idle
    case requestingPermission
    case permissionLimited(reason: String)
    case locating
    case displaying(AppPlace, freshness: LocationFreshness)
    case searching(query: String)
    case showingSearchResults([AppPlace], fetchedAt: Date)
    case calculatingRoute
    case showingRoute(calculatedAt: Date)
    case loadingWeather
    case showingWeather(fetchedAt: Date)
    case stale(message: String)
    case failed(message: String, canRetry: Bool)
}
```

The enum is illustrative: a real feature may use nested state models and an observation framework. The important contract is that permission, source, network/service work, freshness, review, and failure are not hidden behind a single optional coordinate or optional weather value.

## Recipe 9: entitlements, usage descriptions, and fallback

| Capability | Configuration to review | Product fallback |
| --- | --- | --- |
| When In Use location | `NSLocationWhenInUseUsageDescription` | Manual address, saved place, or approximate area. |
| Always/background location | `NSLocationAlwaysAndWhenInUseUsageDescription`, background policy, user-facing justification, and physical-device proof | Foreground-only session or user-initiated refresh. |
| Temporary full accuracy | `NSLocationTemporaryUsageDescriptionDictionary` with the exact purpose key | Continue with reduced-accuracy area-level UX. |
| WeatherKit | WeatherKit capability/entitlement, target/account configuration, attribution, and usage/quota review | Saved/manual weather source or an explicit unavailable state. |
| Map/search/directions | MapKit route, network/error/loading state, route confirmation | Manual place entry, saved places, or retry. |

Never use a missing permission or entitlement as a silent empty result. Explain the limitation, preserve the person’s input, and make a meaningful next action available. Do not put raw coordinates, full search responses, or weather payloads into analytics by default.

## Recipe 10: physical-device verification matrix

| Test | Evidence to capture |
| --- | --- |
| Permission | First-use explanation, allow, deny, restricted, Settings revocation, services disabled, and manual fallback. |
| Accuracy | Reduced accuracy, temporary full-accuracy purpose, no fix, old fix, horizontal accuracy label, and changed Settings state. |
| Foreground updates | One-shot versus continuous behavior, desired accuracy/distance filter, stop on teardown, app background/foreground, battery, and thermal observations. |
| Map/search | Fixed map without permission, camera/control behavior, type-ahead debounce, cancellation, empty/error/rate/latency states, accessible place detail, and stale result rejection. |
| Directions | Source/destination confirmation, transport type, no route, alternatives, cancellation, recalculation, changed place, and handoff behavior. |
| Geocoding | One request per action, rate-limit handling, cancellation, no result, network loss, entered-text preservation, and deletion/retention. |
| WeatherKit | Capability/entitlement in the signed target, attribution, unavailable location, service error, quota/error state, fetched timestamp, cache policy, and retry. |
| Privacy | Raw coordinates/search/weather data absent from logs/analytics by default, retention/deletion, export, and network instrumentation. |
| Accessibility | VoiceOver map/list alternative, labels for accuracy/freshness, Dynamic Type, reduced motion, color-independent status, and large hit targets. |

Previews and simulator location playback can validate pure state rendering and repeatable UI transitions. They do not prove physical sensor accuracy, battery/thermal behavior, background delivery, network/service availability, WeatherKit entitlement behavior, or release configuration. Record the target device family, OS build, permissions, account/configuration, and test date for any claim that matters.

## Sources

- [Core Location](https://developer.apple.com/documentation/corelocation)
- [CLLocationManager](https://developer.apple.com/documentation/corelocation/cllocationmanager)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/corelocation/requesting-authorization-to-use-location-services)
- [Configuring your app to use location services](https://developer.apple.com/documentation/corelocation/configuring-your-app-to-use-location-services)
- [CLGeocoder](https://developer.apple.com/documentation/corelocation/clgeocoder)
- [Geocoding an address](https://developer.apple.com/documentation/corelocation/clgeocoder/geocodeaddressstring%28_%3Ain%3Acompletionhandler%3A%29)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [MapKit for SwiftUI](https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui)
- [Map](https://developer.apple.com/documentation/mapkit/map)
- [MKLocalSearch](https://developer.apple.com/documentation/mapkit/mklocalsearch)
- [MKLocalSearchCompleterDelegate](https://developer.apple.com/documentation/mapkit/mklocalsearchcompleterdelegate)
- [MKLocalSearchResponse](https://developer.apple.com/documentation/mapkit/mklocalsearch/response)
- [MKMapItem](https://developer.apple.com/documentation/mapkit/mkmapitem)
- [MKDirections](https://developer.apple.com/documentation/mapkit/mkdirections)
- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [WeatherService](https://developer.apple.com/documentation/weatherkit/weatherservice)
- [weather(for:including:)](https://developer.apple.com/documentation/weatherkit/weatherservice/weather%28for%3Aincluding%3A%29-3cg1d)
- [WeatherAttribution](https://developer.apple.com/documentation/weatherkit/weatherattribution)
- [WeatherKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.weatherkit)
