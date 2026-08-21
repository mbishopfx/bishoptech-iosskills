# Location, Maps, Places, and Weather

## Choose the capability before the framework

Separate five often-confused outcomes:

| Outcome | Primary route | What it does not imply |
| --- | --- | --- |
| Show a map or fixed places | MapKit and MapKit for SwiftUI | No request for the person’s location is required. |
| Find places or complete a query | `MKLocalSearch` and, for type-ahead, `MKLocalSearchCompleter` | Search results are not a proof of the person’s current location or an always-current directory. |
| Show the person’s position or area | Core Location plus MapKit | Authorization does not guarantee full accuracy, a fix, or background delivery. |
| Convert an address/coordinate or calculate directions | MapKit search/geocoding/directions | A route calculation is not turn-by-turn navigation or a guarantee that roads remain open. |
| Display weather for a location | WeatherKit | A fetched forecast is not an unqualified real-time or future guarantee; label the request/fetch time and source. |

Start with fixed map content or search when that satisfies the product. Add Core Location only when the person explicitly chooses a location-sensitive action. Add WeatherKit only when the product has reviewed its WeatherKit capability, attribution, usage, quota, and data-freshness requirements.

For the advanced SwiftUI composition route, continue with [MapKit for SwiftUI advanced composition and place exploration](../41-framework-deep-dives/13-mapkit-swiftui-advanced-composition.md), the [MapKit place-exploration capability route](../50-capability-recipes/89-mapkit-place-exploration-capability-route.md), and the [MapKit proof matrix](../60-verification/83-mapkit-advanced-composition-proof-matrix.md). These pages cover camera state, MapReader conversion, map-feature selection, viewport POI search, Look Around, directions, Liquid Glass shells, and source-linked AI proposals.

## Select the least powerful location mode

Start with When In Use authorization unless the product truly needs delivery while the app is not running. Ask for access when the user enters the feature that needs location, explain the value in the surrounding UI, and handle denied, restricted, and reduced-accuracy states without making the whole app unusable.

Treat accuracy as data, not as an invisible implementation detail. Persist or display a reading with its timestamp, horizontal accuracy, authorization state, and whether it is approximate. A map centered on an old coordinate must say that it is using the last known position; it must not be presented as the user’s current position without a fresh reading.

## Route by lifecycle

| Product need | Recommended lifecycle | Review points |
| --- | --- | --- |
| One “use my location” action | Request When In Use, call the one-shot location route, then stop/finish | Permission, timeout/error, reduced accuracy, stale result, manual area fallback. |
| A visible foreground session | Start updates only while the session is active; tune desired accuracy and distance filter | Battery/thermal cost, interruption, app suspension, cancellation, physical device. |
| Regions, visits, or background delivery | Review Always authorization, background mode/indicator, and user-facing need before implementation | Strong justification, privacy copy, battery, settings changes, entitlement/configuration, release review. |
| Browse a map or a known set of places | Use MapKit without location permission | Offline/empty/error state, accessible annotations, selection, map controls. |
| Search nearby businesses | Search MapKit with an explicit region; request location only when the person chooses “near me” | Query cancellation, rate/latency states, stale results, search scope, privacy. |
| Plan a trip | Search places, let the user confirm source/destination, calculate directions, and store a draft route | Transport type, route errors, changing places, user confirmation, no-network fallback. |
| Add weather context | Use WeatherKit for a confirmed location and cache with freshness metadata | WeatherKit entitlement, attribution, availability, quota, errors, forecast timestamp. |

Do not set background delivery or Always authorization “just in case.” The feature must explain why foreground access is insufficient, and the target app must prove the resulting lifecycle on a physical device.

## Availability and failure state

Location can be unavailable because of app authorization, system location services, device settings, Airplane mode, hardware, reduced accuracy, no fix yet, or lifecycle/background behavior. Map search and directions can fail because of network/service conditions or a cancelled request. WeatherKit can fail because of service availability, entitlement/configuration, quota, or an invalid/unavailable location.

Represent these states explicitly instead of collapsing them into an empty map:

`idle -> requesting -> authorized|denied|restricted|reducedAccuracy -> fetching -> fresh|stale|unavailable|failed`

Every displayed location-sensitive result should have enough provenance for the UI to say what it is: source, fetched/observed time, uncertainty, and whether the result is a local cache, a MapKit response, a route calculation, or WeatherKit data. A retry must cancel or supersede the previous request so a late response cannot overwrite a newer query.

## Map UI structure

Keep map rendering separate from domain state. The map should display annotations/routes derived from domain data; it should not become the only source of truth for a saved place or trip. Model a place with a stable app identifier, display name, coordinate, address/metadata, source, and last-resolved time. Keep `MKMapItem` and search responses at the boundary and convert them into app-owned models before persistence.

Use MapKit for SwiftUI presentation and native map controls, but make important actions available outside the map surface too: a list, VoiceOver-readable labels, a selected-place detail view, and a manual address/coordinate route. Do not make color, pin position, or map zoom the only way to understand state.

## Search, geocoding, and directions boundaries

- Use `MKLocalSearchCompleter` for type-ahead suggestions and `MKLocalSearch` for a confirmed query. Debounce typing, cancel superseded work, keep a request generation/token, and show the query/region used for results.
- Use `MKMapItem` for place identity and detail at the MapKit boundary. Do not silently persist every search result or infer sensitive categories from a coordinate.
- Use MapKit directions for a user-confirmed source/destination and chosen transport type. Treat the result as a calculated route that can become stale; provide a recalculate/error path.
- Use `CLGeocoder` sparingly for user-intended address/coordinate conversion. It is network-backed and rate-limited; do not reverse-geocode every moving location update. Prefer MapKit search when it better matches the product outcome.

## Weather data boundary

WeatherKit requires the WeatherKit capability/entitlement in the app target and required attribution in the product UI. Request only the datasets needed, retain the returned metadata/fetch time, and cache deliberately so scrolling or every location update does not become a weather request. State the location and forecast time context, and expose a manual refresh/retry route.

WeatherKit’s “current conditions” and forecasts are service data for a requested location, not a promise that the device has measured the present weather or that a forecast will occur. Do not use weather data for safety-critical decisions without a separate product and domain review.

## Privacy

Location is sensitive. Minimize retention, avoid collecting a continuous trail when a single coordinate is enough, encrypt stored/sent data, explain usage, and allow deletion. Keep raw coordinates out of logs and analytics by default. Do not silently turn a foreground feature into a background tracker, and do not send location to an AI tool or remote service unless the person-facing product need and data boundary are explicit.

## Sources

- [Core Location](https://developer.apple.com/documentation/corelocation)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/corelocation/requesting-authorization-to-use-location-services)
- [Configuring your app to use location services](https://developer.apple.com/documentation/corelocation/configuring-your-app-to-use-location-services)
- [CLLocationManager](https://developer.apple.com/documentation/corelocation/cllocationmanager)
- [CLAccuracyAuthorization](https://developer.apple.com/documentation/corelocation/claccuracyauthorization)
- [CLGeocoder](https://developer.apple.com/documentation/corelocation/clgeocoder)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [MapKit for SwiftUI](https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui)
- [Map](https://developer.apple.com/documentation/mapkit/map)
- [MKLocalSearch](https://developer.apple.com/documentation/mapkit/mklocalsearch)
- [MKLocalSearchCompleterDelegate](https://developer.apple.com/documentation/mapkit/mklocalsearchcompleterdelegate)
- [MKMapItem](https://developer.apple.com/documentation/mapkit/mkmapitem)
- [MKDirections](https://developer.apple.com/documentation/mapkit/mkdirections)
- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [WeatherService](https://developer.apple.com/documentation/weatherkit/weatherservice)
- [weather(for:including:)](https://developer.apple.com/documentation/weatherkit/weatherservice/weather%28for%3Aincluding%3A%29-3cg1d)
- [WeatherAttribution](https://developer.apple.com/documentation/weatherkit/weatherattribution)
- [WeatherKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.weatherkit)
