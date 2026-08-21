# SwiftUI WeatherKit forecast, alert, and attribution recipes

These are compile-oriented route sketches for an iOS 26 target. They use native WeatherKit for a native app, keep Core Location separate, preserve response metadata and availability, and treat AI text as an optional proposal. Verify the WeatherKit entitlement/App ID, service configuration, network behavior, attribution, and real device/release build before shipping.

## 1. Fetch a combined forecast and attribution

Request only the datasets the screen needs. Attribution is a separate async service property and should have its own UI state.

~~~swift
import CoreLocation
import WeatherKit

struct WeatherPayload: Sendable {
    let weather: Weather
    let attribution: WeatherAttribution
}

func fetchWeatherPayload(
    for location: CLLocation,
    service: WeatherService = .shared
) async throws -> WeatherPayload {
    async let weather = service.weather(for: location)
    async let attribution = service.attribution

    return try await WeatherPayload(
        weather: weather,
        attribution: attribution
    )
}
~~~

If attribution is not ready, keep that state separate from a forecast failure. A product should not publish a weather surface that omits required attribution merely because the forecast request succeeded.

## 2. Request availability before optional datasets

Minute forecasts and alerts can be unsupported or temporarily unavailable. Ask for availability and render those states explicitly.

~~~swift
import CoreLocation
import WeatherKit

struct ForecastBundle: Sendable {
    let availability: WeatherAvailability
    let current: CurrentWeather
    let hourly: Forecast<HourWeather>
    let alerts: [WeatherAlert]?
}

func fetchForecastBundle(
    for location: CLLocation,
    service: WeatherService = .shared
) async throws -> ForecastBundle {
    let (availability, current, hourly, alerts) = try await service.weather(
        for: location,
        including: .availability,
        .current,
        .hourly,
        .alerts
    )

    return ForecastBundle(
        availability: availability,
        current: current,
        hourly: hourly,
        alerts: alerts
    )
}
~~~

An absent alert array is not evidence that no alert exists when `alertAvailability` is `unsupported` or `temporarilyUnavailable`. Keep the availability kind with the result.

## 3. Select a minute-or-hourly precipitation route

The minute query is optional. Use hourly data as a product-visible fallback, not as a silent substitution that changes the meaning of the screen.

~~~swift
import CoreLocation
import WeatherKit

enum PrecipitationRoute: Sendable {
    case minute(Forecast<MinuteWeather>)
    case hourly(Forecast<HourWeather>)
    case unavailable(WeatherAvailability.AvailabilityKind)
}

func fetchPrecipitationRoute(
    for location: CLLocation,
    service: WeatherService = .shared
) async throws -> PrecipitationRoute {
    let (availability, minute, hourly) = try await service.weather(
        for: location,
        including: .availability,
        .minute,
        .hourly
    )

    switch availability.minuteAvailability {
    case .available:
        if let minute {
            return .minute(minute)
        }
        return .unavailable(.temporarilyUnavailable)
    case .temporarilyUnavailable, .unsupported, .unknown:
        return .hourly(hourly)
    @unknown default:
        return .hourly(hourly)
    }
}
~~~

The product copy should say “hourly fallback” when the minute route is not available. Do not display a missing minute response as zero precipitation.

## 4. Preserve metadata and freshness

`WeatherMetadata` supplies the response date, expiration date, and location. Use those values to drive freshness instead of the time the view happened to render.

~~~swift
import Foundation
import WeatherKit

enum WeatherFreshness: Equatable, Sendable {
    case current
    case stale(expiredAt: Date)
}

enum WeatherFreshnessPolicy {
    static func evaluate(
        expirationDate: Date,
        now: Date = Date()
    ) -> WeatherFreshness {
        if now < expirationDate {
            return .current
        }
        return .stale(expiredAt: expirationDate)
    }

    static func evaluate(
        metadata: WeatherMetadata,
        now: Date = Date()
    ) -> WeatherFreshness {
        evaluate(expirationDate: metadata.expirationDate, now: now)
    }
}

/*
 Keep response metadata at the boundary, then project only the fields the
 screen and evidence package need.
 */
func freshness(
    for metadata: WeatherMetadata,
    now: Date = Date()
) -> WeatherFreshness {
    if now < metadata.expirationDate {
        return .current
    }
    return .stale(expiredAt: metadata.expirationDate)
}

struct WeatherMetadataProjection: Sendable {
    let receivedAt: Date
    let expiresAt: Date
    let latitude: Double
    let longitude: Double
    let freshness: WeatherFreshness

    init(metadata: WeatherMetadata, now: Date = Date()) {
        receivedAt = metadata.date
        expiresAt = metadata.expirationDate
        latitude = metadata.location.coordinate.latitude
        longitude = metadata.location.coordinate.longitude
        freshness = WeatherFreshnessPolicy.evaluate(metadata: metadata, now: now)
    }
}
~~~

The policy helper makes deterministic tests possible without manufacturing a `WeatherMetadata` value, whose public interface is decoder-oriented. Redact or round coordinates in logs and evidence; keep exact values only where the controlled fixture requires them.

## 5. Cancel stale place requests

SwiftUI place changes can outlive a request. Cancel the old task and check the request generation before publishing.

~~~swift
import CoreLocation
import Foundation
import Observation
import WeatherKit

enum WeatherScreenState: Sendable {
    case idle
    case loading(placeID: String)
    case loaded(Weather)
    case failed(String)
}

@MainActor
@Observable
final class WeatherCoordinator {
    private let service: WeatherService
    private var task: Task<Void, Never>?
    private var generation = 0

    private(set) var state: WeatherScreenState = .idle

    init(service: WeatherService = .shared) {
        self.service = service
    }

    func load(placeID: String, location: CLLocation) {
        task?.cancel()
        generation &+= 1
        let requestGeneration = generation
        state = .loading(placeID: placeID)

        task = Task { [weak self, service] in
            do {
                let weather = try await service.weather(for: location)
                try Task.checkCancellation()

                guard let self, self.generation == requestGeneration else {
                    return
                }
                self.state = .loaded(weather)
            } catch is CancellationError {
                return
            } catch {
                guard let self, self.generation == requestGeneration else {
                    return
                }
                self.state = .failed(String(describing: error))
            }
        }
    }

    func cancel() {
        generation &+= 1
        task?.cancel()
        task = nil
        state = .idle
    }
}
~~~

Use a stable place revision in production instead of trusting only a display name. The response must match the place, query, unit/time-zone policy, and current generation before it changes the visible state.

## 6. Format measurements at the SwiftUI edge

Keep typed `Measurement` values in the domain model and format them according to the person’s locale or explicit setting only in the view layer.

~~~swift
import Foundation

func localizedTemperature(
    _ measurement: Measurement<UnitTemperature>,
    locale: Locale
) -> String {
    let formatter = MeasurementFormatter()
    formatter.locale = locale
    formatter.unitOptions = .providedUnit
    return formatter.string(from: measurement)
}

func localizedDate(
    _ date: Date,
    timeZone: TimeZone,
    locale: Locale
) -> String {
    let formatter = DateFormatter()
    formatter.locale = locale
    formatter.timeZone = timeZone
    formatter.dateStyle = .medium
    formatter.timeStyle = .short
    return formatter.string(from: date)
}
~~~

For a travel screen, use the forecast location’s time zone for forecast labels and state that choice in the UI. Do not turn a raw Celsius/Fahrenheit conversion into an unlabelled localized string that loses the source unit.

## 7. Project official alerts without rewriting them

Keep the source and details URL with the alert projection.

~~~swift
import Foundation
import WeatherKit

struct AlertProjection: Identifiable, Sendable {
    let id: String
    let summary: String
    let source: String
    let severity: String
    let region: String?
    let detailsURL: URL

    init(_ alert: WeatherAlert) {
        summary = alert.summary
        source = alert.source
        severity = String(describing: alert.severity)
        region = alert.region
        detailsURL = alert.detailsURL
        id = [alert.source, alert.summary, alert.detailsURL.absoluteString]
            .joined(separator: "|")
    }
}

func alertProjections(
    from alerts: [WeatherAlert]?
) -> [AlertProjection] {
    (alerts ?? []).map(AlertProjection.init)
}
~~~

Display the source, summary, severity, region when present, and a Details link. Do not replace the official text with a model-generated safety instruction.

## 8. Render a native Liquid Glass status card

Keep the material around a small status/action cluster and keep the weather data itself accessible as text.

~~~swift
import SwiftUI
import WeatherKit

struct CurrentWeatherCard: View {
    let current: CurrentWeather
    let freshnessText: String
    let refresh: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(current.condition.description, systemImage: current.symbolName)
                .font(.headline)

            Text(current.temperature, format: .measurement(width: .abbreviated))
                .font(.system(.largeTitle, design: .rounded).weight(.semibold))

            Text(freshnessText)
                .font(.caption)
                .foregroundStyle(.secondary)

            Button("Refresh", action: refresh)
                .buttonStyle(.borderedProminent)
        }
        .padding(20)
        .glassEffect(.regular, in: .rect(cornerRadius: 24))
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Current weather")
        .accessibilityValue("\(current.condition.description), \(current.temperature), \(freshnessText)")
    }
}
~~~

Compile the exact formatting overload against the target SDK. Always retain a text label and freshness state if the selected SF Symbol or glass material is unavailable, reduced, or not meaningful on another platform.

## 9. Validate a typed on-device explanation

The following proposal type is app-owned. A Foundation Models session may produce it, but the validator and user review own acceptance.

~~~swift
import Foundation

struct WeatherExplanationProposal: Codable, Sendable, Equatable {
    let sourceDate: Date
    let expirationDate: Date
    let placeLabel: String
    let explanation: String
    let actionSuggestion: String?
}

enum WeatherProposalError: Error {
    case staleSource
    case missingPlace
    case emptyExplanation
    case unsafeAlertRewrite
}

func validate(
    _ proposal: WeatherExplanationProposal,
    currentSourceDate: Date,
    now: Date = Date()
) throws {
    guard !proposal.placeLabel.isEmpty else {
        throw WeatherProposalError.missingPlace
    }
    guard !proposal.explanation.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
        throw WeatherProposalError.emptyExplanation
    }
    guard proposal.sourceDate == currentSourceDate,
          now < proposal.expirationDate else {
        throw WeatherProposalError.staleSource
    }

    let prohibited = ["evacuate", "guaranteed safe", "medical advice"]
    if prohibited.contains(where: proposal.explanation.localizedCaseInsensitiveContains) {
        throw WeatherProposalError.unsafeAlertRewrite
    }
}
~~~

This is a policy sketch, not a complete safety classifier. For actual severe-alert workflows, preserve and link official source content instead of asking the model to paraphrase it into an instruction.

## 10. Swift Testing fixtures for deterministic weather policy

Use typed fixtures to test freshness and availability without claiming that the simulator reproduces weather service behavior.

~~~swift
import Foundation
import Testing
import WeatherKit

struct WeatherPolicyTests {
    @Test("expired metadata is stale")
    func expiredMetadataIsStale() {
        let now = Date(timeIntervalSince1970: 2_000)
        let expirationDate = Date(timeIntervalSince1970: 1_500)

        #expect(WeatherFreshnessPolicy.evaluate(
            expirationDate: expirationDate,
            now: now
        ) == .stale(
            expiredAt: expirationDate
        ))
    }

    @Test("unsupported minute data does not become zero rain")
    func unsupportedMinuteDataIsExplicit() {
        let kind = WeatherAvailability.AvailabilityKind.unsupported
        #expect(kind != .available)
    }
}
~~~

If the selected SDK changes a public initializer or formatter overload, adjust the fixture to the current interface. These tests prove reducer/policy behavior only; they do not prove an App ID, entitlement, provider response, location permission, attribution delivery, physical weather, or release build.

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
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing in Swift](https://developer.apple.com/documentation/testing)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
