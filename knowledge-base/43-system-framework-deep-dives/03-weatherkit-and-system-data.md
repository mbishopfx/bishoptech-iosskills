# WeatherKit and System Data

## Capability

WeatherKit provides current conditions, precipitation, forecasts, and alerts through Apple’s weather service. It is a network-backed system service with service configuration, attribution, location, caching, and regional availability concerns.

## Weather route

1. Decide whether the user chooses a place, uses current location, or enters coordinates.
2. Request location only when the feature needs current location; a weather app can start with manual place selection.
3. Configure the WeatherKit capability/service for the target app and environment.
4. Request the smallest weather datasets needed.
5. Cache with an explicit freshness timestamp and show when data was last updated.
6. Display required attribution and explain alerts/forecast uncertainty in product language.

Weather is not a sensor reading from the phone itself. Network availability, service limits, region, request authorization, and forecast freshness all affect the result.

## State model

`place selection -> requesting -> current/forecast loaded -> stale refresh -> unavailable/error`

Keep location selection separate from weather fetching so a person can use the app without granting location access. If a request fails, preserve the last known data with a timestamp only when that is safe and clearly labeled.

## Boundaries and failure modes

- WeatherKit requires the relevant service setup, entitlement, and usage/account configuration; verify them in the selected project.
- Location permission is separate from WeatherKit access.
- Forecasts and alerts are time- and region-dependent; do not represent them as guarantees.
- Display Apple Weather attribution and any required data-source/legal link for the selected presentation.
- Avoid storing precise location history when a place identifier or coarse region satisfies the feature.

## API, target, and dataset matrix

| Need | API route | Target/configuration boundary | Proof and fallback |
| --- | --- | --- | --- |
| Fetch a selected place | `WeatherService.weather(for:including:)` with a `CLLocation` derived from a place/coordinate | App or companion target with the WeatherKit capability/service configuration; the place picker/geocoder is a separate concern | Record the normalized place/coordinate, request ID, query set, timestamp, and service error; keep the last safe result only with an expiry label. |
| Fetch current conditions | `WeatherQuery.current` / `CurrentWeather` | Selected SDK availability and WeatherKit service access; no location permission is needed when the person supplies a place | Verify `WeatherMetadata.date`/`expirationDate`, units, locale, and `WeatherAttribution`; do not present a modelled condition as an exact sensor observation. |
| Fetch forecasts and alerts | `WeatherQuery.hourly`, `.daily`, `.minute`, `.alerts`, and `.availability` | Request only the datasets the target surface can display; forecast/alert availability can vary by location and service response | Render empty/unsupported datasets distinctly from a network error; preserve severity/source/time metadata and expose stale/refresh state. |
| Use current device location | Core Location authorization and location stream/one-shot adapter, then WeatherKit | Location usage description, authorization/reduced-accuracy behavior, and background location policy belong to the target; WeatherKit permission/configuration remains separate | Prove denied/reduced/changed-location and cancellation paths; offer manual place selection without forcing location access. |
| Project weather to a widget, Watch, or CarPlay surface | App-owned redacted weather projection, then WidgetKit/Watch Connectivity/CarPlay adapter | Companion/extension target, shared projection, attribution placement, and surface-specific freshness/privacy limits | Prove the actual surface, stale/unknown rendering, attribution, account switch, and process termination; a main-app fetch does not prove companion delivery. |
| Cache and refresh | App-owned persistence keyed by place/region and dataset | Storage/privacy/retention policy is app-owned; service freshness is returned by WeatherKit metadata | Store source, query, fetched/expiry dates, locale/units, and redaction state; invalidate on expiry, place change, sign-out, or schema migration. |

The route is network-backed system data, not an on-device weather model. Keep the service adapter behind a typed repository so the UI, widget, and companion projections can represent `loading`, `partial`, `stale`, `unavailable`, and `failed` without inventing values.

## Weather request state machine

```text
manualPlace | locationPermissionPending
        -> placeResolved | locationResolved
        -> querying
        -> loaded(current/forecast/alerts)
        -> stale
        -> refreshing -> loaded | stale | unavailable | failed
```

Carry a request generation/cancellation token so a slow result for an old place cannot overwrite the current place. Persist the place/region identity, selected `WeatherQuery` set, request date, metadata expiration date, attribution payload, service availability, and last error. A service response may be partial; do not collapse missing alerts or unsupported minute forecasts into an empty “all clear” state. A widget or companion can receive a redacted stale projection, but it cannot be used as proof that the main app has a fresh service response.

## Verification route

- Test manual place, current location, denied/reduced location, no network, stale cache, service error, and unsupported/empty data.
- Test units, time zones, locale, daylight changes, severe alerts, and long forecast content.
- Verify attribution at every surface, including widgets, watch, and CarPlay variants if supported.
- Test on physical devices with the real entitlements and service configuration; mocks only prove UI states.

## Sources

- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [WeatherService](https://developer.apple.com/documentation/weatherkit/weatherservice)
- [WeatherQuery](https://developer.apple.com/documentation/weatherkit/weatherquery)
- [CurrentWeather](https://developer.apple.com/documentation/weatherkit/currentweather)
- [WeatherMetadata](https://developer.apple.com/documentation/weatherkit/weathermetadata)
- [WeatherAttribution](https://developer.apple.com/documentation/weatherkit/weatherattribution)
- [Get Started with WeatherKit](https://developer.apple.com/weatherkit/)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/corelocation/requesting-authorization-to-use-location-services)
