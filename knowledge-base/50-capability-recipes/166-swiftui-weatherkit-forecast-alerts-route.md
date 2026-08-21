# SwiftUI WeatherKit forecast, alert, and attribution route

Use this worksheet for a native iOS weather feature that needs a current place, forecast family, severe alerts, weather-change explanations, or a local AI summary. Keep WeatherKit service configuration, Core Location, response metadata, SwiftUI state, and any side effect as separate contracts.

## Route card

| Field | Decision |
| --- | --- |
| User outcome | What decision will the weather screen help the person make? |
| Place source | Saved coordinate, search result, airport, explicit coordinate, or authorized current location |
| Location authority | App-owned place versus Core Location permission/accuracy state |
| Forecast family | Current, minute, hourly, daily, alerts, changes, historical/statistics |
| Query window | Default query or explicit `Date`/`DateInterval` range with time-zone policy |
| Freshness | `WeatherMetadata.date` and `expirationDate`; stale/refresh behavior |
| Dataset availability | `WeatherAvailability` minute/alert state and fallback |
| Units/locale | Foundation `Measurement` values and localized date/time formatting |
| Attribution | `WeatherAttribution` service name, marks, legal page/text |
| AI role | None, deterministic explanation, or typed on-device proposal |
| Side effect | Display only, user reminder, local notification, export, or system handoff |
| Proof | Entitlement, service, location, freshness, alert, attribution, accessibility, physical/release evidence |

## Choose the smallest query

```text
Need only a current card?
  -> .current

Need next-hour precipitation?
  -> request .availability, then .minute when available; otherwise .hourly

Need a daily plan?
  -> .daily, or an explicit bounded daily range

Need alert context?
  -> .alerts plus source/details UI

Need all data for one screen?
  -> one combined WeatherService request with only required queries

Need a qualitative “what is changing?” view?
  -> .changes, with effective dates and source context

Need historical comparison/statistics?
  -> separate historical/statistics route, never silently mixed into current forecast
```

The default `.hourly` route returns 25 contiguous hours beginning with the current hour; `.daily` returns 10 contiguous days beginning with the current day. Explicit ranges have additional limits and local-time semantics. Store the query description with the response projection.

## Target and service manifest

Create a target manifest before requesting data:

```yaml
target:
  bundle_id: com.example.weather-app
  deployment: iOS 26
  capabilities:
    weatherkit: true
  signed_entitlement:
    com.apple.developer.weatherkit: true
location:
  source: saved-place-or-core-location
  accuracy: exact-or-approximate-recorded
  retention: no-exact-coordinate-analytics
query:
  family: current-hourly-daily-alerts
  timezone: place-local
  units: locale-or-user-preference
freshness:
  use_metadata_expiration: true
  stale_policy: visible-and-refreshable
ai:
  provider: on-device-only
  source: typed-weather-projection
  side_effect: human-review-required
```

The WeatherKit entitlement is a signed target property. A capability shown in Xcode is not release evidence until the archived artifact contains the expected entitlement and the App ID/service configuration is valid.

## Place and location route

```text
saved place / search / airport
    -> stable place ID + coordinate + display time zone

current device location
    -> explain purpose
    -> Core Location authorization/accuracy
    -> location revision
    -> WeatherKit request
```

Do not pass a location-manager callback straight into a weather request without a generation. When the person changes place, cancel the old task and reject a response whose place revision no longer matches the visible screen. Keep approximate/reduced accuracy visible when it affects place identity.

## Response projection

Project WeatherKit into safe app-owned types:

```text
WeatherProjection
    placeID / placeLabel
    coordinate provenance: saved / search / authorized current
    query family and requested range
    current / hourly / daily / minute values
    alert summaries with source/details URL/severity
    availability flags
    metadata date / expiration / location
    display locale / unit / time-zone policy
    attribution readiness
    request generation
```

Keep Foundation `Measurement` and `Date` values in the domain model. Format to strings at the SwiftUI edge. Store dates with the forecast location’s calendar/time zone, then convert for display deliberately.

## Freshness and cancellation contract

```text
visible place + query revision
    -> loading task
    -> cancellation when place/query/scene changes
    -> response metadata validation
    -> current / stale / partial / failed projection
```

Rules:

- use `metadata.expirationDate` to decide whether the response is current or stale;
- never treat an unavailable minute/alert dataset as zero precipitation/no alert;
- preserve the last known result only when the product can explain its age and source;
- avoid a timer that fetches continuously when a user refresh or visible-screen task is enough;
- back off after service/provider errors; and
- prevent a cancelled or older task from overwriting a newer place revision.

## Alert and attribution route

For each alert, retain:

```text
summary
severity
region if available
source
detailsURL
metadata date/expiration/location
```

Show alerts as official-source content. Preserve raw/source limitations and avoid turning a summary into a stronger emergency instruction. `WeatherAttribution` must be loaded and presented with service name, legal page/text, and appropriate Apple Weather mark. Keep an attribution state even when the forecast is loading, stale, or partial.

## SwiftUI/Liquid Glass route

```text
NavigationStack
  -> place picker / current-place action
  -> current weather card
  -> freshness and availability row
  -> alert card when present
  -> hourly/daily forecast section
  -> details and attribution sheet
  -> optional AI explanation card
```

Use Liquid Glass only for a small action/status cluster. Measurements, alert source, data date, and legal attribution remain readable under reduced transparency. Use SF Symbols and typed labels; do not make color or animated sky effects the only meaning.

## Optional typed on-device AI route

```text
typed WeatherProjection
    -> select bounded interval and metrics
    -> normalize units/time zone deterministically
    -> optional Foundation Models explanation
    -> validate source revision, dates, alert language, and claims
    -> show as AI explanation/draft
    -> person reviews before reminder/export/action
```

The model must not invent a weather value, rewrite an official alert into a safety order, or trigger a notification without a separate deterministic and user-approved route. If on-device model availability is false, keep the deterministic forecast usable.

## Evidence package

```text
weather-route/
  target-entitlement-redacted.plist
  app-id-and-service-configuration.md
  place-source-and-location-results.md
  query-family-and-timezone-fixtures.md
  availability-and-freshness-results.md
  alert-source-and-details-results.md
  attribution-light-dark-accessibility-results.md
  ai-proposal-and-fallback-results.md
  physical-device-and-network-results.md
  archive-testflight-release-results.md
```

Redact exact coordinates in evidence unless they are necessary for a controlled fixture. Include device/OS/build, place source, query, response metadata, and outcome. A screenshot alone does not prove the forecast source, entitlement, service freshness, or alert delivery.

## Sources

- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [WeatherKit overview](https://developer.apple.com/documentation/weatherkit)
- [WeatherService](https://developer.apple.com/documentation/weatherkit/weatherservice)
- [Weather](https://developer.apple.com/documentation/weatherkit/weather)
- [WeatherQuery](https://developer.apple.com/documentation/weatherkit/weatherquery)
- [WeatherAvailability](https://developer.apple.com/documentation/weatherkit/weatheravailability)
- [CurrentWeather](https://developer.apple.com/documentation/weatherkit/currentweather)
- [HourWeather](https://developer.apple.com/documentation/weatherkit/hourweather)
- [DayWeather](https://developer.apple.com/documentation/weatherkit/dayweather)
- [MinuteWeather](https://developer.apple.com/documentation/weatherkit/minuteweather)
- [Forecast](https://developer.apple.com/documentation/weatherkit/forecast)
- [WeatherAlert](https://developer.apple.com/documentation/weatherkit/weatheralert)
- [WeatherChanges](https://developer.apple.com/documentation/weatherkit/weatherchanges)
- [WeatherMetadata](https://developer.apple.com/documentation/weatherkit/weathermetadata)
- [WeatherAttribution](https://developer.apple.com/documentation/weatherkit/weatherattribution)
- [WeatherKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.weatherkit)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [CLLocation](https://developer.apple.com/documentation/corelocation/cllocation)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
