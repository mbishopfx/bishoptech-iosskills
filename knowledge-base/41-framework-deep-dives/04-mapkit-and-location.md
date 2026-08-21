# MapKit and Core Location

## Capability boundary

MapKit renders maps, annotations, user-location context, search, place details, and calculated routes. Core Location supplies device location services, authorization, accuracy, and updates. WeatherKit is a separate service/data and entitlement boundary. Keep these seams visible: a map can show fixed places without requesting the person’s location, and a WeatherKit request does not itself grant location permission.

## Smallest route

1. Decide whether the product needs fixed places, search, directions, or the person’s current location.
2. Use MapKit for SwiftUI presentation, annotations, camera state, and native map controls.
3. Use `MKLocalSearchCompleter` for suggestions and `MKLocalSearch` for a confirmed search; keep result cancellation and query/region provenance.
4. Use `MKMapItem` as a place-detail boundary and convert it to an app-owned model before persistence.
5. Use `MKDirections` only when the product needs a calculated route for a confirmed source, destination, and transport type.
6. Introduce `CLLocationManager` only when a person-facing action needs device location. Choose one-shot `requestLocation()` versus continuous `startUpdatingLocation()` deliberately.
7. Add WeatherKit only after target capability/entitlement, attribution, usage/quota, and forecast-freshness requirements are understood.

## Authorization and accuracy state

Core Location supports When In Use and Always authorization levels. When In Use is the preferred starting point for most features because it limits background access and battery impact. Include truthful usage-description keys before requesting authorization, explain the benefit in the surrounding UI, and ask at the point of action rather than at launch.

Model both authorization and accuracy:

`notDetermined -> requestWhenInUse -> authorizedWhenInUse`

`authorizedWhenInUse + reducedAccuracy -> area-level experience | user-requested temporary full accuracy`

`denied | restricted | servicesDisabled -> explain limitation -> settings/manual route`

If a feature truly needs more accurate data, request temporary full accuracy with a purpose key at that feature boundary. A full-accuracy request is not a license to retain a continuous trail or to ask for Always authorization. The UI should still tolerate no fix, an old fix, a large `horizontalAccuracy`, and a Settings change while the app is running.

## One-shot, foreground, and background location

Use `requestLocation()` for a single action such as “use my current area.” Use `startUpdatingLocation()` only while a visible feature needs a stream, set a product-appropriate `desiredAccuracy` and `distanceFilter`, and call `stopUpdatingLocation()` when the session ends. Publish `lastUpdateAt`, horizontal accuracy, authorization, and a freshness policy with each reading.

Background updates and `requestAlwaysAuthorization()` require a separate product justification, usage copy, project configuration, indicator/privacy review, battery plan, and physical-device test. Do not set `allowsBackgroundLocationUpdates` in a general-purpose service by default. If the product does not need background delivery, keep the route foreground-only.

## Map, search, place, and route state

| State | Map UI behavior | Domain behavior |
| --- | --- | --- |
| `fixedContent` | Render known annotations and controls | No location permission; local app model is authoritative. |
| `searching(query, region)` | Show progress and preserve the query | Cancel/supersede the request; do not clear a useful previous result prematurely. |
| `searchResults(items, fetchedAt)` | Show results and selected detail | Treat results as a response snapshot; retain source and fetch time. |
| `routeCalculating(source, destination, transport)` | Show progress and a cancel action | Cancel old calculations; require confirmation before saving/starting a route. |
| `routeReady(route, calculatedAt)` | Show route summary and recalculate action | Treat route as time-sensitive calculated data, not guaranteed navigation. |
| `locationUnavailable(reason)` | Keep map usable and offer manual area/search | Do not substitute an old coordinate without labeling it stale. |

For type-ahead, debounce text changes and cancel a superseded `MKLocalSearchCompleter`/search request. For a confirmed query, constrain the search region when the product has a meaningful region. For directions, make source, destination, transport type, and calculation time visible enough for the person to correct them.

## Geocoding and reverse geocoding

`CLGeocoder` performs network-backed address/coordinate conversion and is rate-limited. Keep one active request per geocoder, cancel it when the field/query changes, and do not reverse-geocode every location update in a moving session. A user action such as “name this place” is an appropriate boundary; a background loop is not. Apple’s current Core Location documentation points developers toward MapKit for many search/place-discovery outcomes, so select the route that matches the UX instead of treating geocoding as a general directory.

## WeatherKit boundary

WeatherKit’s native Swift route uses `WeatherService` with a `CLLocation` and a selected `WeatherQuery`, such as current conditions or a forecast dataset. Enable the WeatherKit capability in Xcode so the target carries the WeatherKit entitlement, and include the required `WeatherAttribution`/Apple Weather mark and legal attribution surface in the product.

Keep weather state separate from location authorization and label it with:

- the requested coordinate/area and whether it came from a fresh fix, a saved place, or a manual selection;
- the request/fetch time and any source-provided observation/forecast metadata;
- freshness/expiry policy, loading, unavailable, quota, entitlement, and retry states;
- the fact that a forecast or “current conditions” response is service data, not a device measurement or guarantee.

Cache only what the product can explain and refresh intentionally. Do not request weather on every map camera movement or every location update. Severe weather, safety, health, travel, or other high-consequence experiences require domain-specific review and a second source/operational plan where appropriate.

## Cancellation and stale-response defense

Search, geocoding, directions, and WeatherKit calls are asynchronous. Keep a request ID or generation in the feature state, cancel the prior task when the query/location changes, call the framework’s cancellation method where available, and check `Task.isCancelled`/`Task.checkCancellation()` before publishing. A response that arrives after the person selected a new place is stale even if the network call succeeded.

## Product route examples

| User outcome | Framework route | Proof boundary |
| --- | --- | --- |
| Browse a fixed set of places | MapKit map and annotations | Verify layout, selection, camera, labels, VoiceOver, and no-permission behavior. |
| Find nearby businesses | MapKit search plus an explicit location request | Test denied, reduced accuracy, no fix, no network, cancellation, and stale responses. |
| Build a trip plan | MapKit search plus directions and SwiftData draft state | Verify route errors, transport selection, changing places, recalculation, and confirmation. |
| Track a foreground session | Core Location updates plus local persistence/ActivityKit if separately justified | Requires permission, sampling policy, cancellation, battery/thermal test, and a physical device. |
| Show weather for a saved place | WeatherKit plus saved coordinate and freshness metadata | Requires entitlement, attribution, service/account configuration, quota/error tests, and timestamped UI. |

## API route matrix

MapKit and Core Location should be composed as separate adapters. Start with a map and app-owned place data when the outcome does not require the person’s position; add authorization only at the point where a location-dependent operation begins.

| User need | Native API route | Data crossing the domain boundary | Configuration/lifecycle gate |
| --- | --- | --- | --- |
| Show a fixed or saved map | SwiftUI `Map` with `MapContentBuilder`, `Marker`, `Annotation`, and map controls | Place ID, coordinate, display name, source, and user-selected state | No location permission for fixed content; test map style, camera, selection, accessibility, and no-network fallback. |
| Convert map interaction into app state | `MapReader`/`MapProxy`, camera position, selection, and map content callbacks | Explicit coordinate/selection event with timestamp and source | Normalize map coordinates and reject stale selections after a view/task replacement. |
| Draw a path or area | `MapPolyline`, overlays, or the UIKit `MKMapView` overlay route | App-owned points, route ID, style, and freshness | Keep geometry separate from navigation truth; test large/empty/invalid geometry and Dynamic Type labels. |
| Search for a confirmed place | `MKLocalSearchCompleter` for suggestions, then `MKLocalSearch`/`MKLocalPointsOfInterestRequest` | Query, region, result identifier, name/address, coordinate, fetched-at | Cancel superseded requests; retain source/fetch time; handle no results, rate limits, and network failure. |
| Inspect a selected place | `MKMapItem` and the relevant place-detail/Look Around route | Stable place identifier where available, user-visible fields, provenance | Ask for confirmation before persisting or starting a consequential route; do not treat a search result as identity verification. |
| Calculate directions | `MKDirections.Request` and `MKDirections` producing `MKRoute`/ETA | Source, destination, transport, route geometry, calculated-at, alternative selection | Recalculate when inputs change; show that route/ETA is calculated service data, not guaranteed navigation. |
| Get one current location | `CLLocationManager.requestLocation()` | Coordinate, horizontal accuracy, timestamp, authorization, accuracy level | Require a fresh-enough fix; tolerate timeout/no-fix/reduced accuracy and offer manual selection. |
| Stream foreground location | `startUpdatingLocation()` with `desiredAccuracy` and `distanceFilter` | Bounded samples plus sampling policy and stop reason | Stop explicitly; measure battery/thermal cost and handle interruptions, stale samples, and Settings changes. |
| Use background location | `requestAlwaysAuthorization()` plus the documented background route | Timestamped samples, user-visible purpose, retention/deletion policy | Separate capability/usage copy, indicators, scheduling, battery, and physical-device proof; do not enable by default. |
| Show weather for a place | `WeatherService.weather(for:including:)` and a selected `WeatherQuery` | Area/coordinate, observation/forecast data, fetched-at, expiry, attribution state | WeatherKit entitlement, attribution, service/quota/account state, and freshness/retry policy are separate from location permission. |

## Location state and task ownership

Initialize a `CLLocationManager`, assign its delegate immediately, then drive the feature from `locationManagerDidChangeAuthorization(_:)` and the manager’s current `authorizationStatus`/`accuracyAuthorization`. Keep a single owner for starting and stopping updates; a SwiftUI view may request a state transition, but it should not create competing managers on every render.

Use this state model for a location-dependent feature:

`notDetermined -> explaining -> requesting -> authorizedWhenInUse | authorizedAlways`

and orthogonal states:

`fullAccuracy | reducedAccuracy`, `servicesDisabled`, `denied`, `restricted`, `waitingForFix`, `staleFix`, `freshFix`, `interrupted`, `stopped`, `manualPlace`.

When authorization changes, re-evaluate the operation rather than retrying blindly. If reduced accuracy is adequate, continue with an area-level route; otherwise present the product’s purpose for temporary full accuracy and a manual place alternative. Store a reading’s timestamp and accuracy with the value so an old or approximate coordinate cannot silently appear current.

## Search, directions, and weather cancellation contract

Use a generation token or task identity for every search/directions/weather operation:

`input changed -> cancel previous -> start request -> check cancellation -> normalize response -> publish only if generation is current`

Keep the framework request object behind an adapter so a view can cancel without knowing whether the implementation uses `MKLocalSearch`, `MKDirections`, `CLGeocoder`, or `WeatherService`. Cache only normalized, user-explainable values. Never let a late response for an old coordinate replace a newly selected place or append a forecast with an earlier fetch time.

For route handoff, distinguish these records:

| Record | Meaning |
| --- | --- |
| Search result | A service response for a query and region at a time. |
| Saved place | A user-selected app record with explicit provenance and edit/delete policy. |
| Calculated route | A time-sensitive response for source, destination, transport, and calculation time. |
| Location sample | A device measurement with authorization, accuracy, timestamp, and retention policy. |
| Forecast | A WeatherKit service response with area, query, fetch time, expiry, and attribution state. |

Do not collapse these into one `Location` model and then infer permission, freshness, identity, navigation, or weather certainty from a coordinate alone.

## Verification route

- Confirm `Info.plist` usage descriptions and any temporary-accuracy purpose dictionary are present and truthful.
- Exercise first request, allow, deny, restricted, reduced accuracy, full-accuracy request, Settings revocation, services disabled, no fix, and stale-fix states.
- Test a fixed map without permission, search with no network, type-ahead cancellation, search result selection, directions cancellation, changed transport, and route recalculation.
- Verify WeatherKit capability/entitlement, attribution, supported target configuration, unavailable location, service error, quota/error messaging, caching, and fetch timestamps.
- Run background location, route handoff, or Live Activity behavior on a physical device if the product depends on it. Simulator location playback is useful for UI/state tests, not proof of sensor, battery, background, or service behavior.
- Verify that map annotations, location status, route summaries, and weather freshness are accessible and understandable without relying only on color, pin position, or map zoom.

## Sources

- [MapKit for SwiftUI](https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui)
- [Map](https://developer.apple.com/documentation/mapkit/map)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [MKLocalSearch](https://developer.apple.com/documentation/mapkit/mklocalsearch)
- [MKLocalSearchCompleterDelegate](https://developer.apple.com/documentation/mapkit/mklocalsearchcompleterdelegate)
- [MKLocalSearchResponse](https://developer.apple.com/documentation/mapkit/mklocalsearch/response)
- [MKMapItem](https://developer.apple.com/documentation/mapkit/mkmapitem)
- [MKDirections](https://developer.apple.com/documentation/mapkit/mkdirections)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/corelocation/requesting-authorization-to-use-location-services)
- [CLLocationManager](https://developer.apple.com/documentation/corelocation/cllocationmanager)
- [CLAccuracyAuthorization](https://developer.apple.com/documentation/corelocation/claccuracyauthorization)
- [CLGeocoder](https://developer.apple.com/documentation/corelocation/clgeocoder)
- [Geocoding an address](https://developer.apple.com/documentation/corelocation/clgeocoder/geocodeaddressstring%28_%3Ain%3Acompletionhandler%3A%29)
- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [WeatherService](https://developer.apple.com/documentation/weatherkit/weatherservice)
- [weather(for:including:)](https://developer.apple.com/documentation/weatherkit/weatherservice/weather%28for%3Aincluding%3A%29-3cg1d)
- [WeatherAttribution](https://developer.apple.com/documentation/weatherkit/weatherattribution)
- [WeatherKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.weatherkit)
- [Apple Maps Server API](https://developer.apple.com/documentation/applemapsserverapi)
