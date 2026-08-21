# SwiftUI WeatherKit forecast and alert surface design

Weather UI should help a person decide what to do while remaining honest about place, time, source, freshness, and uncertainty. A polished weather card is not a promise that the sky outside exactly matches a model response.

## Screen hierarchy

Use a source-aware hierarchy:

```text
place and location source
    -> current conditions + local time
    -> freshness / partial availability / alert state
    -> hourly or daily decision strip
    -> details, attribution, and optional explanation
```

| Region | Purpose | Native treatment |
| --- | --- | --- |
| Place header | Names the saved/search/current place and source | `NavigationStack`, `Menu`, `Picker`, or a standard place control |
| Current card | Shows typed condition, temperature, daylight, wind/precipitation, and data time | `Label`, `Text`, SF Symbol from `symbolName`, and clear units |
| Freshness row | Shows updated/expired/loading/partial state | Text plus refresh button; never a color-only dot |
| Alert card | Separates official alert from normal forecast | Severity label, source, summary, details link, and explicit “official alert” copy |
| Forecast strip | Supports the decision: next hour, hourly, or daily | Scrollable native list/chart with dates and time zone |
| Attribution | Gives provider/legal path and Apple Weather mark | Visible in the weather surface or an easily reached sheet, light/dark aware |
| AI explanation | Summarizes selected typed data | Label as AI explanation/draft, show source interval, review before action |

The first card should answer “where, when, and what?” before showing decorative weather animation.

## State model

Use one app-owned state enum or reducer that keeps query, place, response, attribution, and error state distinct:

```text
idle
  -> choosingPlace
  -> loading(placeRevision, queryRevision)
  -> current(response, freshness)
  -> partial(response, unavailableDatasets)
  -> stale(response, expiredAt)
  -> failed(reason, lastKnown)
```

An alert is an overlay on the response, not a replacement for all forecast data. Attribution is a release/display requirement, not a weather condition. A location permission state is not the same as a WeatherKit entitlement state.

| State | Copy | Action |
| --- | --- | --- |
| Loading | “Getting weather for Chicago…” | Cancel when the task is no longer relevant |
| Current | “72° · Clear · Updated 10:18 AM” | Refresh or inspect details |
| Stale | “Showing older weather from 10:18 AM” | Refresh; preserve source and expiration |
| Partial | “Minute precipitation unavailable here; hourly forecast is available.” | Use hourly or inspect availability |
| Alert | “Official alert from the National Weather Service” | Open details URL; do not rewrite official action text |
| No location | “Choose a place or allow current location.” | Place picker or Core Location purpose explanation |
| Service failure | “Weather couldn’t be updated.” | Retry with bounded backoff; show last known data if safe |
| Attribution | “Weather data provided by…” | Open legal attribution path |

## Liquid Glass composition

Use Liquid Glass as a restrained grouping material:

- a compact place/refresh/status cluster over the current card;
- a small segmented choice between Hourly and Daily when both are relevant;
- an alert action cluster with Details and Dismiss/Mark Read; and
- an AI explanation action group separated from raw forecast values.

Avoid:

- covering the entire forecast in a moving glass overlay;
- using a sun/rain animation as the only indicator of condition or alert severity;
- placing exact update time, units, or legal attribution in low-contrast translucent text;
- using glass color to imply confidence, safety, or currentness; and
- automatically morphing or scrolling the forecast when Reduce Motion is enabled.

Keep measurements, alert summary, source, and freshness opaque and readable when Reduce Transparency or Increase Contrast is enabled. When the person uses large text, allow cards to grow vertically rather than truncating the time zone or alert source.

## Forecast family layout

Choose the layout by task:

| Task | Layout | Detail to preserve |
| --- | --- | --- |
| Immediate clothing/commute | Current card + next-hour/hourly strip | Date/time, precipitation chance/type, temperature, source place |
| Day planning | Hourly strip + day summary | Local hour, daylight, precipitation amount/chance, wind, alert state |
| Travel/flight planning | Saved airport/place + daily route | Location time zone, date boundaries, stale state, attribution |
| Severe weather | Alert-first card + forecast context | Issuer, summary, severity, region, details URL, alert metadata |
| Weather change | Change list | Effective date, qualitative direction, comparison/source wording |
| Historical context | Separate comparison/statistics screen | Historical range, baseline, units, not current forecast truth |

Do not label a daily row “tomorrow” if the forecast location’s local calendar has changed relative to the device. Use the localized date/time from the response’s location and explain the place time zone in travel flows.

## Alerts are official-source content

Weather alerts can have missing localized descriptions and raw source restrictions. The design should:

1. state that the card is an official alert;
2. show source, summary, severity, affected region when available, and data time;
3. provide the details URL in a standard link/button;
4. preserve the source wording instead of turning it into a stronger recommendation; and
5. avoid claiming that a card was delivered as a background safety notification.

If the app later creates a local reminder or notification, make that a separate user-approved flow with its own trigger, provider, and delivery evidence.

## Attribution treatment

Attribution should feel like part of the weather product, not a hidden legal footnote. Support:

- light and dark Apple Weather marks;
- the legal attribution page and text;
- VoiceOver label and activation behavior;
- Dynamic Type and large-text wrapping;
- a clear state if attribution assets are still loading; and
- offline/stale views that still preserve the attribution path.

Do not use a custom provider badge that obscures or replaces the WeatherKit-provided service name and legal content. Keep the attribution control reachable from the same screen that presents the data.

## Location and privacy design

Offer a saved place or search route before requiring continuous current-location access when the product does not need it. If current location is useful:

- explain the purpose before the Core Location prompt;
- indicate approximate/reduced accuracy when relevant;
- show the place name/source and a change-place control;
- avoid exposing exact coordinates in copy or analytics;
- retain the last place intentionally, not as a silent location tracker; and
- provide manual place selection when location is denied.

The weather service’s `CLLocation` input is a coordinate contract, not proof that the app has the person’s permission to observe their location. Keep the Core Location state visible when it affects the result.

## AI explanation card

An optional on-device explanation should be visually subordinate to the typed forecast:

```text
Hourly forecast: rain chance rises from 20% to 70% between 3–5 PM
AI explanation: “Carry rain gear for the late afternoon.”
Source: Chicago, local time, forecast interval 3–5 PM
```

Label it “AI explanation” or “Draft suggestion,” not “weather prediction.” Show the input interval, location label, model availability, and a limitation such as “Review the forecast details.” Do not allow the model to rewrite official alerts, invent a warning, or trigger a safety action without a deterministic validation and user review.

When the model is unavailable, the typed forecast and a rule-based explanation remain usable. Do not silently send the data to a remote provider if the surface promised on-device processing.

## Accessibility and reduced effects

Verify complete tasks with:

- VoiceOver reading order: place, current value, freshness, alert, forecast interval, attribution, actions;
- meaningful labels for condition symbols and weather alerts;
- Dynamic Type and long localized place/source names;
- Reduce Motion and reduced transparency;
- Increase Contrast;
- Voice Control names for Refresh, Change Place, Details, and attribution;
- keyboard, pointer, and Switch Control access to forecast scrolling and alert details; and
- RTL, date, number, unit, and time-zone localization.

Weather animation must be optional. A person should understand rain chance, wind, severe alert, stale state, and time without sound, haptics, color, or motion.

## Design review checklist

- [ ] Place, coordinate source, local time, and forecast data time are distinct.
- [ ] Current/hourly/daily/minute/alert availability is rendered separately.
- [ ] Stale and expired data are clearly labelled.
- [ ] Official alerts identify source, severity, region/details, and limitations.
- [ ] Required WeatherKit attribution remains visible/reachable in both appearances.
- [ ] Liquid Glass groups controls without hiding measurements or legal text.
- [ ] Saved-place/manual fallback works when current location is denied.
- [ ] AI explanations show source interval and remain proposals.
- [ ] Dynamic Type, VoiceOver, contrast, reduced effects, keyboard/pointer, Switch Control, RTL, and localization are complete.
- [ ] Physical service/entitlement/archive proof is not substituted by a preview.

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
- [WeatherAlert](https://developer.apple.com/documentation/weatherkit/weatheralert)
- [WeatherAttribution](https://developer.apple.com/documentation/weatherkit/weatherattribution)
- [WeatherMetadata](https://developer.apple.com/documentation/weatherkit/weathermetadata)
- [WeatherKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.weatherkit)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
