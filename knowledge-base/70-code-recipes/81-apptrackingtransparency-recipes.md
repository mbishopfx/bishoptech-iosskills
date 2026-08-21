# AppTrackingTransparency and AdSupport recipes

These are compile-oriented sketches for an active containing iOS app. They do not replace App Store privacy review, partner attribution policy, user disclosure, or a physical-device test. Never print or commit an advertising identifier.

## 1. Request tracking authorization once from the active app

~~~swift
import AppTrackingTransparency

@MainActor
final class TrackingAuthorizationCoordinator {
    private(set) var status = ATTrackingManager.trackingAuthorizationStatus

    func requestIfNeeded() async -> ATTrackingManager.AuthorizationStatus {
        status = ATTrackingManager.trackingAuthorizationStatus
        guard status == .notDetermined else { return status }

        // Call from an active containing-app scene after other prompts settle.
        status = await ATTrackingManager.requestTrackingAuthorization()
        return status
    }

    func refresh() -> ATTrackingManager.AuthorizationStatus {
        status = ATTrackingManager.trackingAuthorizationStatus
        return status
    }
}
~~~

The target must contain `NSUserTrackingUsageDescription`. The system remembers the choice for the installation, and the app should refresh status after returning from Settings.

## 2. Map status to a feature route

~~~swift
import AppTrackingTransparency

enum TrackingRoute: Equatable, Sendable {
    case explainAndRequest
    case permittedAdvertising
    case identifierFree
    case restricted
}

func route(
    for status: ATTrackingManager.AuthorizationStatus
) -> TrackingRoute {
    switch status {
    case .notDetermined:
        .explainAndRequest
    case .authorized:
        .permittedAdvertising
    case .denied:
        .identifierFree
    case .restricted:
        .restricted
    @unknown default:
        .restricted
    }
}
~~~

Do not make the denied or restricted route a crash, an empty screen, or a hidden product penalty. Keep its feature behavior explicit.

## 3. Read the advertising identifier only on the permitted path

~~~swift
import AdSupport
import AppTrackingTransparency

func authorizedAdvertisingIdentifier() -> UUID? {
    guard ATTrackingManager.trackingAuthorizationStatus == .authorized else {
        return nil
    }

    let identifier = ASIdentifierManager.shared().advertisingIdentifier
    let allZeros = "00000000-0000-0000-0000-000000000000"
    return identifier.uuidString == allZeros ? nil : identifier
}
~~~

Treat `nil` as the normal identifier-free route. Do not generate a replacement fingerprint from device properties, and do not store the UUID as an account identity.

## 4. A privacy-safe event boundary

~~~swift
struct MeasurementContext: Sendable {
    let route: TrackingRoute
    let campaignContext: String?
}

func makeMeasurementContext(
    status: ATTrackingManager.AuthorizationStatus,
    campaignContext: String?
) -> MeasurementContext {
    let route = route(for: status)
    return MeasurementContext(
        route: route,
        campaignContext: route == .permittedAdvertising ? campaignContext : nil
    )
}
~~~

Keep raw identifiers and partner payloads outside generic logs and model telemetry. This context is a route decision, not a guarantee that a downstream vendor is permitted to receive data.

## 5. SwiftUI status and fallback surface

~~~swift
import AppTrackingTransparency
import SwiftUI

@MainActor
final class TrackingStatusModel: ObservableObject {
    @Published private(set) var status = ATTrackingManager.trackingAuthorizationStatus

    func refresh() {
        status = ATTrackingManager.trackingAuthorizationStatus
    }

    var title: String {
        switch status {
        case .notDetermined: "Not requested"
        case .authorized: "Optional tracking allowed"
        case .denied: "Identifier-free mode"
        case .restricted: "Tracking restricted"
        @unknown default: "Tracking unavailable"
        }
    }
}

struct TrackingStatusView: View {
    @ObservedObject var model: TrackingStatusModel

    var body: some View {
        Form {
            Section("Privacy choice") {
                Text(model.title)
                Text("The app remains useful without cross-app tracking.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            Section {
                Button("Refresh status") {
                    model.refresh()
                }
            }
        }
        .navigationTitle("Privacy")
    }
}
~~~

Use a separate pre-prompt explanation and the system request. Do not present this Form as if it were Apple’s system permission sheet.

## 6. Keep on-device AI independent of IDFA

~~~swift
struct LocalPersonalizationInput: Sendable {
    let preferredTopics: [String]
    let recentLocalActions: [String]
}

func makeLocalAIInput(
    preferences: [String],
    localActions: [String]
) -> LocalPersonalizationInput {
    LocalPersonalizationInput(
        preferredTopics: preferences,
        recentLocalActions: localActions
    )
}
~~~

The local model can use explicit, first-party inputs without receiving `advertisingIdentifier` or ATT status as a hidden feature. Keep model prompts, logs, and generated output free of raw advertising identifiers.

## 7. Test deterministic fallback policy

~~~swift
import AppTrackingTransparency
import Testing

@Test
func unknownAndDeniedStatusesDoNotEnterAdvertisingRoute() {
    #expect(route(for: .notDetermined) == .explainAndRequest)
    #expect(route(for: .denied) == .identifierFree)
    #expect(route(for: .restricted) == .restricted)
}
~~~

System permission states require UI/device evidence. This test proves only the local routing policy.

## Sources

- [AppTrackingTransparency](https://developer.apple.com/documentation/apptrackingtransparency)
- [ATTrackingManager](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager)
- [requestTrackingAuthorization(completionHandler:)](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/requesttrackingauthorization%28completionhandler%3A%29)
- [trackingAuthorizationStatus](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/trackingauthorizationstatus)
- [AdSupport](https://developer.apple.com/documentation/adsupport)
- [ASIdentifierManager](https://developer.apple.com/documentation/adsupport/asidentifiermanager)
- [advertisingIdentifier](https://developer.apple.com/documentation/adsupport/asidentifiermanager/advertisingidentifier)
- [NSUserTrackingUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsusertrackingusagedescription)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
