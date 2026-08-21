# SwiftUI WeatherKit forecast, alert, and attribution route

WeatherKit is a service-backed weather data route, not a live sensor and not a safety guarantee. A native app gives `WeatherService` a `CLLocation` and receives typed current conditions, minute precipitation, hourly and daily forecasts, availability, severe alerts, metadata, attribution, and selected change/statistics datasets. The product still owns location consent, query scope, freshness, unit presentation, error recovery, and the language used around uncertainty.

The reliable mental model is:

```text
user-selected place or approved location
    -> coordinate/source and privacy policy
    -> WeatherKit entitlement/service readiness
    -> smallest forecast query that answers the task
    -> typed response + metadata/availability/attribution
    -> freshness/cancellation/error projection
    -> SwiftUI native surface
    -> optional typed on-device explanation
    -> alert/source handoff and evidence
```

A forecast response, weather symbol, cached value, alert object, simulator coordinate, or AI explanation is not proof of current physical conditions or user safety. The current WeatherKit documentation explicitly notes that current conditions may be the result of a mathematical weather model based on real observations rather than a literal observation at the requested moment.

## Select the forecast family by user outcome

| User outcome | WeatherKit route | Boundary |
| --- | --- | --- |
| “What is it like at this place?” | `WeatherQuery.current` / `CurrentWeather` | Preserve `date`, metadata location, freshness, units, and the fact that current conditions are modeled data. |
| “Will I need an umbrella soon?” | `WeatherQuery.minute` when `WeatherAvailability.minuteAvailability` allows it; otherwise hourly precipitation | Minute data is optional/region-dependent and covers the next-hour route; provide the hourly fallback explicitly. |
| “What happens through today/tomorrow?” | `.hourly` / `Forecast<HourWeather>` | The default query returns 25 contiguous hours beginning with the current hour; preserve each hour’s date/time zone and units. |
| “Plan the next week” | `.daily` / `Forecast<DayWeather>` | The default query returns 10 contiguous days beginning with the current day; arbitrary ranges have documented limits and local-midnight semantics. |
| “Is severe weather relevant?” | `.alerts` / `[WeatherAlert]?` | Alerts are issued by a governmental authority, may contain raw or missing localized descriptions, and require source/details presentation. |
| “What will materially change?” | `.changes` / `WeatherChanges?` | This is a qualitative significant-change route; do not convert `increase/decrease/steady` into a numeric guarantee. |
| “Compare historical norms” | historical comparison/statistics queries | Historical context is a separate dataset and should not be mixed with a current forecast without dates, location, and provenance. |
| “Show weather for a saved place” | App-owned coordinate plus WeatherKit | Saved coordinates need a user-visible name/source and a refresh/freshness policy; do not silently replace a saved place with current device location. |

Use a combined `WeatherService.weather(for:including:)` request when the screen truly needs several datasets together. Use a single query when the screen needs one lane, so unsupported minute/alerts availability does not make current/hourly data appear unavailable.

## Service, entitlement, and location are separate gates

Native WeatherKit requires the WeatherKit capability/entitlement. Apple’s current entitlement documentation identifies `com.apple.developer.weatherkit` as a Boolean entitlement and directs developers to enable the capability in Xcode. The WeatherKit sample also requires an App ID with WeatherKit enabled and a target whose bundle identifier matches that App ID. Verify the signed archive, not just the project capability checkbox.

The weather service accepts a `CLLocation`; that does not grant the app permission to obtain the person’s location. Keep these authorities separate:

| State | Meaning | UI behavior |
| --- | --- | --- |
| Saved place | App owns a coordinate selected or entered by the person | Request weather for that coordinate without implying live device tracking. |
| Location permission needed | The screen wants current device location but Core Location has not authorized it | Explain the purpose, request the least-privilege location access, and retain a place/search fallback. |
| Approximate location | Core Location provided reduced accuracy | Label the location scope and avoid false precision in weather/place identity. |
| Location unavailable | No current fix or the service is disabled | Show the saved-place/search route and preserve the last valid weather as stale. |
| WeatherKit entitlement missing | The target cannot use the native service | Treat as a build/configuration failure in development; do not create an end-user retry loop. |
| Provider unavailable | WeatherKit request failed or the provider is temporarily unavailable | Keep the last non-expired or stale projection with timestamp and retry policy. |
| Dataset unavailable | Minute or alerts data is unsupported/temporarily unavailable for this location | Keep current/hourly/daily if available and explain the missing dataset. |
| Attribution not ready | Required attribution assets/text have not been loaded | Do not publish a weather surface until the legal attribution path is available. |

Use Core Location only when the product needs current position. A user-selected airport, address, map coordinate, or saved place can be a lower-privacy route. If the app uses current location, explain why and keep the location permission prompt separate from the WeatherKit service configuration.

## WeatherService and request ownership

`WeatherService` exposes async throwing methods and a documented shared service object. Give the feature a clear coordinator/actor owner and cancel the task when the place, screen, or user intent changes. Do not start one network request per SwiftUI redraw or attach stale results to a newer location.

Use a generation or request identity:

```text
placeID + coordinate revision + query family + request generation
    -> WeatherService request
    -> check cancellation and generation
    -> normalize response with metadata
    -> publish only if it still matches the visible place
```

When a person types a place name or drags a map, separate the place/search route from the weather route. Cancel the old weather task, do not let an earlier response overwrite the new coordinate, and keep a last-known projection marked with its source date and expiration.

`WeatherQuery` lets the app request current, availability, alerts, minute, hourly, daily, and change datasets and combine queries. The current default ranges documented by Apple are:

| Query | Documented default |
| --- | --- |
| `.current` | Current weather value for the requested location |
| `.hourly` | 25 contiguous hours beginning with the current hour |
| `.daily` | 10 contiguous days beginning with the current day |
| `.minute` | Optional minute-by-minute precipitation route for the next hour |
| `.alerts` | Optional severe weather alerts |
| `.changes` | Optional significant qualitative changes |
| `.availability` | Dataset availability flags for the requested location |

The date-range query forms have additional caveats. Apple documents that daily ranges include a day when local midnight falls within the inclusive start/exclusive end range, can return at most 10 days, expose historical data from August 1, 2021, and forecast up to 10 days into the future. Keep the service’s returned metadata and dates as the source of truth rather than assuming a UTC-day boundary.

## Metadata and freshness are first-class data

`WeatherMetadata` includes the request date, expiration date, and request location. Treat `expirationDate` as a data contract:

```text
receivedAt
metadata.date
metadata.expirationDate
metadata.location
query family and requested date interval
display time zone / locale / unit policy
source place revision
```

Use explicit states:

| State | Meaning |
| --- | --- |
| Loading | A request for the current place/query is in flight. |
| Current | The response is before its metadata expiration and matches the visible place revision. |
| Stale | The response is retained for continuity but is expired or no longer the selected place. |
| Partial | Current/hourly/daily data exists but minute or alert data is unavailable. |
| Failed | No valid response exists for the requested route. |
| Cancelled | The user changed place/query or left the task; no error banner is needed. |

Do not show “now” for an expired response. Show the data date and a refresh action, and decide whether to serve stale data based on the user outcome. A hiking warning, flight plan, or safety-critical workflow needs a stricter freshness policy than a decorative home-screen card.

## Current, hourly, daily, and minute semantics

`CurrentWeather` provides typed `Measurement` values for temperature, apparent temperature, dew point, pressure, visibility, and precipitation intensity, plus humidity/cloud cover, wind, UV index, daylight, condition, date, metadata, and an SF Symbol name. `symbolName` is a representation for the weather condition and daylight state; it is not a forecast confidence score.

`HourWeather` is time-indexed data for an hour and includes temperature/apparent temperature, precipitation type/chance/amount, wind, cloud cover, UV, visibility, daylight, pressure, date, and symbol name. Display an hourly date using the forecast location’s calendar/time zone and label a chart axis with a localized hour, not an unlabeled array index.

`DayWeather` is a daily view. Keep daytime/overnight, high/low, precipitation, wind, sunrise/sunset, and date semantics separate. Do not collapse a day into one icon when the user needs to decide about a particular period.

`MinuteWeather` is a specialized next-hour precipitation stream where available. `WeatherAvailability` documents that minute data and alerts can be temporarily unavailable from the provider or unsupported in some regions. A missing minute forecast is not a zero-precipitation result. Show the hourly route or a clear “minute forecast unavailable” state.

## Alerts and weather changes

`WeatherAlert` represents an alert issued for the requested location by a governmental authority. Apple notes that alerts may be severe or non-severe, may lack localized descriptions, and can be served as raw information because of source restrictions. Preserve:

```text
summary
severity
region if present
source
detailsURL
metadata location/date/expiration
```

An alert card should identify the issuing source, display the summary and severity, link to details, and avoid rewriting raw official language into a stronger instruction. The app can explain the alert’s presence; it should not invent an evacuation or medical/safety order.

`WeatherChanges` is a chronological collection of `WeatherChange` records. Each change has an effective date and qualitative directions for high temperature, low temperature, and day/night precipitation amount. “Increase” means significantly higher relative to before; it is not a numeric guarantee. Make the comparison date and location visible.

Alerts are not local notifications. If a product wants to notify a person later, it needs a separate notification/provider policy, a refresh strategy, and a clear statement about whether it observed a newly changed alert. Do not promise background alert delivery from a foreground WeatherKit fetch.

## Attribution is a release requirement

WeatherKit attribution is required for published software. `WeatherAttribution` supplies the service name, legal attribution page, legal attribution text, and light/dark/square Apple Weather marks. Keep attribution in the visible weather surface or an easily reached sheet according to Apple’s current requirements, and make it work in light/dark appearance, Dynamic Type, VoiceOver, and offline/stale states.

Attribution loading is separate from forecast loading. If the legal page/mark cannot be prepared, do not ship a weather card that omits the required provider information. Do not download or cache arbitrary provider assets outside the documented attribution route, and do not replace the Apple mark with a custom “powered by” badge that changes the legal meaning.

The WeatherKit REST API is a different route for web or other platforms and uses developer-token authentication. A native iOS app should use the native WeatherKit framework unless the product has a documented reason to cross that boundary. Do not put a REST developer token in an iOS app.

## Units, locale, calendar, and coordinate policy

WeatherKit values use Foundation `Measurement` types and localized descriptive strings. Choose the display unit system from the person’s locale/settings or an explicit in-app preference, then format measurements with `MeasurementFormatter` or the selected SwiftUI formatting API. Preserve the raw typed measurement in the domain projection and format only at the UI edge.

Time has two distinct meanings:

- the forecast location’s local calendar/time zone, which determines day/hour labels and daily range inclusion; and
- the device’s current display locale/time zone, which determines how the UI presents that result.

Do not let a device time-zone change silently reclassify the forecast location’s day without reloading/normalizing the source metadata. For travel apps, show the airport/place time zone explicitly.

Coordinates are sensitive location data. Keep exact coordinates out of logs and analytics, round or redact them in evidence, and let a person choose a saved place when current position is unnecessary. A weather request for an arbitrary coordinate should not be described as “your location” unless it actually came from the person’s approved location route.

## SwiftUI and Liquid Glass weather surfaces

Design the screen around the decision the person wants to make:

```text
place name + source
    -> current condition + local time + freshness
    -> alert/availability status
    -> short hourly or daily decision strip
    -> details and attribution
    -> optional AI explanation
```

Use native `List`, `ScrollView`, `TabView`, `Gauge`, `Chart`, `Label`, `ProgressView`, `ContentUnavailableView`, `Map`, and system symbols before custom weather graphics. `symbolName` can drive an SF Symbol with an accessibility label based on the typed condition, but the symbol must not be the only carrier of precipitation, severe alert, stale, or unavailable state.

Liquid Glass works best as a small control/status group—place picker, refresh, alert status, or a compact current-condition card—rather than an opaque glass layer over every forecast row. Keep temperature, units, forecast time, alert severity, data date, and attribution readable under reduced transparency. Avoid animated rain/sun effects that imply live weather or create motion overload; Reduce Motion should retain the same information as text and static symbols.

Recommended state copy:

| State | Surface |
| --- | --- |
| Current | “72° · Clear · Updated 10:18 AM” with place and source date |
| Stale | “Showing older weather from 10:18 AM · Refresh” |
| Minute unavailable | “Minute precipitation is unavailable here; hourly forecast is available.” |
| Alert present | “Official weather alert from [source]” with severity and details link |
| No location permission | “Choose a place or allow location to use your current position.” |
| Service failure | “Weather couldn’t be updated. Last known result: …” |
| Attribution | “Weather data provided by …” with required legal/mark path |

## Optional on-device AI explanations

An on-device model can turn typed weather data into a bounded explanation such as “The rain window is most likely between 3 and 5 PM; the hourly forecast is the source.” It should not create a forecast, invent a severe alert, or make a guarantee.

```text
typed forecast subset + metadata date/expiration + source place revision
    -> deterministic unit/time normalization
    -> optional Foundation Models summary proposal
    -> validate dates, source revision, alert severity, and prohibited claims
    -> show as “AI explanation” with source data visible
    -> user reviews before a reminder/packing/action side effect
```

Keep raw exact coordinates out of the prompt when a place label and coarse region are enough. Never feed a model an alert and let it rewrite it into an unverified evacuation instruction. If the model is unavailable or stale, use the typed deterministic UI.

## Verification boundary

| Claim | Minimum proof |
| --- | --- |
| Native service is configured | App ID, WeatherKit capability, signed entitlement, bundle ID, archive, and TestFlight install. |
| Place/coordinate is correct | User-selected or authorized Core Location source, coordinate revision, time zone, and privacy/redaction record. |
| Query family is correct | Typed query, requested interval, expected default/range semantics, and dataset availability handling. |
| Freshness is honest | `WeatherMetadata.date`, `expirationDate`, location, stale/partial UI, and cancellation/generation evidence. |
| Units/time are correct | Measurement formatting, locale/setting, place time zone, DST/travel fixtures, and accessible labels. |
| Alerts are trustworthy | Real alert fixture/source/details/severity, missing localization, unavailable route, and no invented instruction. |
| Attribution is present | Light/dark mark, legal page/text, service name, offline/stale surface, and accessibility evidence. |
| SwiftUI is native and accessible | Dynamic Type, VoiceOver, contrast, reduced effects, iPad input, localization, alert/refresh task, and large/small layout. |
| AI is subordinate | Unavailable/stale/wrong-schema/alert-rewrite fixtures, source-linked output, user review, and deterministic fallback. |
| Release works | Physical device or approved service configuration, archive, signed entitlements, TestFlight, and current source refresh. |

The companion [WeatherKit design guide](../21-design-deep-dives/163-swiftui-weatherkit-forecast-alerts-route-design.md), [route worksheet](../50-capability-recipes/166-swiftui-weatherkit-forecast-alerts-route.md), [proof matrix](../60-verification/160-swiftui-weatherkit-forecast-alerts-proof-matrix.md), and [code recipes](../70-code-recipes/178-swiftui-weatherkit-forecast-alerts-recipes.md) turn this review into reusable build artifacts.

## Sources

- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [WeatherKit overview](https://developer.apple.com/documentation/weatherkit)
- [WeatherService](https://developer.apple.com/documentation/weatherkit/weatherservice)
- [Weather](https://developer.apple.com/documentation/weatherkit/weather)
- [WeatherQuery](https://developer.apple.com/documentation/weatherkit/weatherquery)
- [CurrentWeather](https://developer.apple.com/documentation/weatherkit/currentweather)
- [HourWeather](https://developer.apple.com/documentation/weatherkit/hourweather)
- [DayWeather](https://developer.apple.com/documentation/weatherkit/dayweather)
- [MinuteWeather](https://developer.apple.com/documentation/weatherkit/minuteweather)
- [Forecast](https://developer.apple.com/documentation/weatherkit/forecast)
- [WeatherAvailability](https://developer.apple.com/documentation/weatherkit/weatheravailability)
- [WeatherAlert](https://developer.apple.com/documentation/weatherkit/weatheralert)
- [WeatherChanges](https://developer.apple.com/documentation/weatherkit/weatherchanges)
- [WeatherChange](https://developer.apple.com/documentation/weatherkit/weatherchange)
- [WeatherMetadata](https://developer.apple.com/documentation/weatherkit/weathermetadata)
- [WeatherAttribution](https://developer.apple.com/documentation/weatherkit/weatherattribution)
- [WeatherError](https://developer.apple.com/documentation/weatherkit/weathererror)
- [WeatherKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.weatherkit)
- [WeatherKit REST API](https://developer.apple.com/documentation/weatherkitrestapi)
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
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
