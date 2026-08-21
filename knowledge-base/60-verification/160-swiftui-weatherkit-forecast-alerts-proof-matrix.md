# SwiftUI WeatherKit forecast, alert, and attribution proof matrix

Weather evidence must connect the signed target, place source, typed query, returned metadata, dataset availability, attribution, SwiftUI state, optional AI, and release configuration. A weather icon, cached response, or forecast screenshot is not enough.

## Claim matrix

| Claim | Minimum evidence | Common false proof |
| --- | --- | --- |
| The native WeatherKit target is configured | App ID/service configuration, Xcode capability, signed `com.apple.developer.weatherkit`, archive, and TestFlight install | WeatherKit import compiles |
| The request uses the intended place | Saved/search/current location source, stable place revision, coordinate/time-zone record, and redacted request evidence | Simulator location alone |
| Location permission is truthful | Core Location authorization/accuracy/service state and manual-place fallback | A `CLLocation` value exists |
| Query family matches the product | Typed `.current`/`.minute`/`.hourly`/`.daily`/`.alerts`/`.changes` query and expected date range | One `Weather` object displayed without query provenance |
| Minute/alert availability is handled | `WeatherAvailability` fixtures for supported, unsupported, and temporarily unavailable datasets | `nil` interpreted as no rain/no alert |
| Current values are framed honestly | Current `date`, metadata location, model-data wording, units, and freshness | “Live temperature” copy with no source date |
| Hourly/daily ranges are correct | 25-hour/10-day defaults, explicit range limits, local-midnight/date-boundary fixtures, and time-zone evidence | Array index rendered as a time label |
| Forecast freshness is correct | `WeatherMetadata.date`, `expirationDate`, stale state, refresh/cancel, and newer-place generation rejection | Last response remains labeled current forever |
| Alerts are source-faithful | Government/source name, summary, severity, region/details URL, missing-localization fixture, and no invented instruction | AI-generated warning text |
| Weather changes are interpreted correctly | Effective dates, qualitative direction, comparison context, and no numeric/safety overclaim | “Increase” treated as a guaranteed amount |
| Attribution is complete | `WeatherAttribution` service name, legal page/text, light/dark marks, offline/stale UI, and accessibility | A generic “weather powered by” footer |
| Units and time zones are correct | Measurement formatting, locale/user preference, place-local date/calendar, DST/travel fixtures, and VoiceOver values | Device time zone silently used for every place |
| Errors are recoverable | Permission denied, entitlement/configuration, network/provider failure, cancellation, dataset unavailable, expired response, and retry/backoff states | One generic “try again” alert |
| SwiftUI design is native | Dynamic Type, VoiceOver, Increase Contrast, Reduce Transparency/Motion, keyboard/pointer/Switch Control, iPad, localization | One glass-card preview |
| AI is bounded | Typed input interval/source revision, on-device availability, wrong-schema/stale/refusal/alert-rewrite fixtures, user review, deterministic fallback | Model summary sounds plausible |
| Weather side effects are separate | Notification/reminder/export has its own permission, trigger, commit, and delivery evidence | Forecast fetch callback treated as notification delivery |
| Release behavior is known | Physical device/service config, archive, signed artifact, TestFlight, current source refresh, and rollback/fallback | Debug simulator success |

## Target and service fixtures

For every build configuration, record:

```text
bundle identifier
team/App ID
iOS/SDK version
WeatherKit capability in project
signed WeatherKit entitlement
service registration/availability
network restrictions and test account if applicable
build/release identifier
```

The WeatherKit App ID registration and service configuration are external to the SwiftUI view. A target can look configured while its archive is signed with a different bundle ID or missing the entitlement. Keep the configuration evidence with the release artifact.

## Place and coordinate fixtures

Use controlled, redacted fixtures:

| Fixture | Expected result |
| --- | --- |
| Saved place | Weather request does not require current-location observation; place label and coordinate revision remain stable |
| Search result changed | Old response is rejected after the place generation changes |
| Current location authorized | Coordinate source and accuracy are visible; response metadata matches the requested location |
| Approximate/reduced accuracy | UI avoids false place/temperature precision and offers place selection |
| Permission denied | Manual place/search remains usable; no endless prompt loop |
| No location fix | Last saved place or stale result is explicit |
| Travel/time-zone change | Forecast location date/time remains correct; UI explains place-local time |
| Coordinate redaction | Logs/evidence do not expose exact personal location unnecessarily |

WeatherKit’s `CLLocation` input is not a substitute for the Core Location permission test. Test both separately.

## Forecast and availability fixtures

```text
forecast/
  current-with-metadata
  current-expired
  hourly-default-25-hours
  daily-default-10-days
  daily-local-midnight-boundary
  daily-historical-and-future-limit
  minute-supported
  minute-unsupported
  minute-temporarily-unavailable
  alerts-present
  alerts-empty
  alerts-unavailable
  changes-chronological
  combined-query-partial
  cancelled-place-generation
```

Verify query selection and not only JSON/model decoding. A combined request should still render current/hourly/daily when minute or alerts are unavailable if those datasets were returned successfully. A missing optional dataset is a partial state, not a zero value.

## Freshness and error fixtures

| Fixture | Expected behavior |
| --- | --- |
| Response before expiration | Render current state with data date and refresh affordance |
| Response at/after expiration | Render stale state; no “current” wording |
| User changes place while request is pending | Cancel or reject old task; new place remains authoritative |
| Provider/network failure with last response | Show error plus age/source; retry is bounded |
| Provider/network failure with no response | Show unavailable state and saved-place/manual fallback |
| Permission denied | Explain the location route and do not claim WeatherKit is denied if only Core Location is denied |
| WeatherKit entitlement missing | Development/release configuration failure with diagnostic evidence |
| Attribution request fails | Do not publish an attribution-incomplete release surface |
| Scene background/foreground | Reconcile freshness and reload when the user returns if the policy requires it |

## Alert and attribution proof

For a real or controlled alert fixture, capture:

- source and details URL;
- summary and severity;
- region if available;
- metadata date/expiration/location;
- missing localized-description behavior; and
- the UI text that makes the official-source boundary clear.

For attribution, verify the `WeatherAttribution` service name, legal page URL, legal text fallback, light mark, dark mark, and square mark paths. Test VoiceOver labels, Dynamic Type, offline/stale states, and the legal action on both appearances.

## SwiftUI accessibility tasks

Run these tasks rather than isolated screenshots:

1. Choose a saved place with VoiceOver and understand the location source.
2. Load current and hourly data, hear value/unit/date/freshness, and refresh.
3. Switch to a daily range in a different time zone and verify date labels.
4. Read an official alert, identify its source/severity, and open Details.
5. Trigger minute/alert unavailable and understand the hourly fallback.
6. Use stale data, refresh failure, and manual-place fallback.
7. Review/reject/accept an AI explanation without changing the forecast source.
8. Repeat at large text, Increase Contrast, Reduce Transparency/Motion, RTL, keyboard, pointer, and Switch Control.

## AI/privacy fixtures

| Fixture | Required result |
| --- | --- |
| AI unavailable | Typed forecast remains usable; deterministic explanation or clear unavailable state |
| Stale source | AI card says stale or is not generated; no fresh-sounding claim |
| Wrong schema/date/source revision | Proposal rejected without forecast mutation |
| Official alert supplied | Model cannot strengthen/rewrite it into an unverified safety instruction |
| Exact coordinate unnecessary | Prompt uses place label/coarse context instead of raw coordinate |
| User rejects draft | No reminder, notification, export, or saved change |
| Provider fallback | No silent remote route if the product promised on-device processing |
| Logs/crashes | No exact coordinate, full alert payload, raw prompt, or personal place history in diagnostics |

## Release evidence package

```text
weather-proof/
  target-entitlement-results.md
  place-and-location-results.md
  forecast-query-fixtures.md
  availability-and-freshness-results.md
  alert-and-source-results.md
  attribution-results.md
  accessibility-results.md
  ai-fallback-and-privacy-results.md
  physical-device-and-network-results.md
  archive-testflight-results.md
```

Include target, build, OS, device, source/query, metadata date/expiration, test outcome, and known limitation. Redact exact coordinates and provider payloads when they are not required for the proof.

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
- [WeatherError](https://developer.apple.com/documentation/weatherkit/weathererror)
- [WeatherKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.weatherkit)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [CLLocation](https://developer.apple.com/documentation/corelocation/cllocation)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
