# SwiftUI Core Location `CLMonitor` condition code recipes

These recipes are compile-oriented starting points for iOS 26. Add location usage descriptions and the required target capabilities, compile against the final SDK, and exercise transitions on a physical device. A map preview or an in-memory monitor is not location proof.

## 1. App-owned condition model

```swift
import CoreLocation
import Observation

struct PlaceCondition: Identifiable, Sendable {
    let id: String
    let label: String
    let center: CLLocationCoordinate2D
    let radius: CLLocationDistance
    let actionDescription: String
}

@MainActor
@Observable
final class LocationConditionCoordinator {
    let monitorName = "com.example.app.location-conditions"

    private(set) var authorizationText = "Not checked"
    private(set) var accuracyText = "Not checked"
    private(set) var conditions: [String] = []
    private(set) var latestEvents: [String: String] = [:]
    private(set) var diagnosticText: String?
    private(set) var lastError: String?

    private var monitorTask: Task<Void, Never>?

    deinit {
        monitorTask?.cancel()
    }

    func start() {
        monitorTask?.cancel()
        monitorTask = Task { [weak self] in
            guard let self else { return }
            await self.runMonitor()
        }
    }

    func stop() {
        monitorTask?.cancel()
        monitorTask = nil
    }

    private func runMonitor() async {
        let monitor = await CLMonitor(monitorName)

        do {
            // Reconcile from an app-owned manifest on every launch. Do not
            // create random monitor names or assume the prior process survived.
            let definition = CLMonitor.CircularGeographicCondition(
                center: CLLocationCoordinate2D(latitude: 41.8819, longitude: -87.6278),
                radius: 200
            )
            await monitor.add(definition, identifier: "studio")

            let identifiers = await monitor.identifiers
            await MainActor.run {
                self.conditions = identifiers
                self.authorizationText = "Monitoring configured"
            }

            for try await event in monitor.events {
                let record = await monitor.record(for: event.identifier)
                await MainActor.run {
                    self.latestEvents[event.identifier] = String(describing: event.state)
                    self.diagnosticText = diagnosticSummary(for: event)
                    _ = record
                }
            }
        } catch {
            await MainActor.run {
                self.lastError = String(describing: error)
            }
        }
    }
}
```

The manifest and the `studio` example are placeholders for the app’s real local policy. The event loop must remain active for the monitor’s lifetime and must be recreated with the same monitor name after relaunch.

## 2. Add geographic and beacon conditions

```swift
import CoreLocation

func addConditions(to monitor: CLMonitor) async {
    let studio = CLMonitor.CircularGeographicCondition(
        center: CLLocationCoordinate2D(latitude: 41.8819, longitude: -87.6278),
        radius: 200
    )
    await monitor.add(studio, identifier: "studio")

    let museumBeacon = CLMonitor.BeaconIdentityCondition(
        uuid: UUID(uuidString: "00000000-0000-0000-0000-000000000001")!,
        major: 7
    )
    await monitor.add(museumBeacon, identifier: "museum-entrance")

    // Use assuming only when the product has an intentional initial-state
    // policy. It is not a physical event and must not be presented as one.
    await monitor.add(
        studio,
        identifier: "studio-assumed",
        assuming: .unsatisfied
    )
}
```

Beacon major/minor values are optional refinements. A UUID-only condition treats major and minor as wildcards; a UUID-plus-major condition treats minor as a wildcard. Keep the raw identity in an installer/developer flow rather than ordinary user copy.

## 3. Consume events and diagnostics

```swift
import CoreLocation

func diagnosticSummary(for event: CLMonitor.Event) -> String? {
    var diagnostics: [String] = []

    if event.authorizationDenied { diagnostics.append("authorization denied") }
    if event.authorizationDeniedGlobally { diagnostics.append("location disabled globally") }
    if event.authorizationRequestInProgress { diagnostics.append("authorization request in progress") }
    if event.authorizationRestricted { diagnostics.append("authorization restricted") }
    if event.accuracyLimited { diagnostics.append("accuracy limited") }
    if event.conditionLimitExceeded { diagnostics.append("condition limit exceeded") }
    if event.conditionUnsupported { diagnostics.append("condition unsupported") }
    if event.insufficientlyInUse { diagnostics.append("insufficiently in use") }
    if event.persistenceUnavailable { diagnostics.append("persistence unavailable") }
    if event.serviceSessionRequired { diagnostics.append("service session required") }

    return diagnostics.isEmpty ? nil : diagnostics.joined(separator: ", ")
}

func stateDescription(_ state: CLMonitor.Event.State) -> String {
    switch state {
    case .satisfied:
        return "Satisfied"
    case .unsatisfied:
        return "Not satisfied"
    case .unknown:
        return "Unknown"
    case .unmonitored:
        return "Not monitored"
    default:
        return String(describing: state)
    }
}
```

The `default` branch is a compile-oriented guard for future SDK cases. The product should map diagnostic flags before acting on a state transition; a satisfied state with a serious diagnostic does not automatically mean the intended action is safe to run.

## 4. Reconcile monitor records after launch

```swift
import CoreLocation

struct ConditionManifest: Codable, Sendable {
    let monitorName: String
    let identifiers: [String]
    let revision: UUID
}

func reconcile(
    monitor: CLMonitor,
    manifest: ConditionManifest
) async -> [String] {
    let activeIdentifiers = await monitor.identifiers
    var missing: [String] = []

    for identifier in manifest.identifiers where !activeIdentifiers.contains(identifier) {
        missing.append(identifier)
    }

    return missing
}
```

Use reconciliation to decide whether to re-add an app-owned condition. Do not silently create a new random monitor or interpret a missing record as a location transition.

## 5. Explicit service-session diagnostics

```swift
import CoreLocation

@MainActor
final class LocationServiceSessionController {
    private var session: CLServiceSession?

    func beginWhenInUseSession() {
        session = CLServiceSession(authorization: .whenInUse)
    }

    func beginAlwaysSession() {
        session = CLServiceSession(authorization: .always)
    }

    func invalidate() {
        session?.invalidate()
        session = nil
    }
}
```

Choose the authorization requirement from the real product need. Create the session in the foreground when the route requires it, and recreate it immediately when a terminated app relaunches in the background. Pair the session with the exact Info.plist usage descriptions and a user-facing explanation.

## 6. SwiftUI map and list surface

```swift
import MapKit
import SwiftUI

struct PlaceConditionView: View {
    let condition: PlaceCondition
    let stateText: String
    let diagnostics: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Map {
                Marker(condition.label, coordinate: condition.center)
                MapCircle(
                    center: condition.center,
                    radius: condition.radius
                )
                .foregroundStyle(.blue.opacity(0.18))
                .stroke(.blue, lineWidth: 2)
            }
            .frame(minHeight: 240)
            .clipShape(RoundedRectangle(cornerRadius: 24))

            VStack(alignment: .leading, spacing: 6) {
                Text(condition.label)
                    .font(.headline)
                Text("Condition: \(stateText)")
                Text("Radius: \(condition.radius, format: .number) meters")
                Text("Action: \(condition.actionDescription)")
                if let diagnostics {
                    Label(diagnostics, systemImage: "exclamationmark.triangle")
                        .foregroundStyle(.orange)
                }
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(condition.label), \(stateText). \(condition.actionDescription)")
        }
        .padding()
        .glassEffect(.regular, in: .rect(cornerRadius: 28))
    }
}
```

The map is an explanation surface. Keep a list/text equivalent and do not treat the visible circle as proof of Core Location accuracy or event delivery.

## 7. Background/relaunch entry point

```swift
import SwiftUI

@main
struct ConditionApp: App {
    @State private var coordinator = LocationConditionCoordinator()

    var body: some Scene {
        WindowGroup {
            RootView(coordinator: coordinator)
                .task {
                    // Recreate the named monitor and event consumer whenever
                    // the app launches, including a system background relaunch.
                    coordinator.start()
                }
        }
    }
}
```

In a production app, gate `start()` on the app-owned authorization/manifest state and make it idempotent. After a reboot, Core Location monitoring resumes only after the user unlocks the device; do not claim earlier delivery.

## 8. Typed on-device AI action proposal

```swift
import FoundationModels

@Generable
struct LocationActionProposal {
    var title: String
    var action: String
    var explanation: String
}

struct LocationProposalService {
    func propose(
        placeLabel: String,
        eventDirection: String,
        configuredAction: String
    ) async throws -> LocationActionProposal {
        guard SystemLanguageModel.default.isAvailable else {
            throw ProposalError.unavailable
        }

        let session = LanguageModelSession()
        let prompt = """
        Create a concise, reviewable action proposal for a location condition.
        Use only the app-owned place label, event direction, and configured
        action. Do not infer coordinates, routines, identity, history, or a
        beacon identifier. Do not create a new permission or background route.

        Place: \(placeLabel)
        Event: \(eventDirection)
        Configured action: \(configuredAction)
        """

        let response = try await session.respond(
            to: prompt,
            generating: LocationActionProposal.self
        )
        return response.content
    }

    enum ProposalError: Error {
        case unavailable
    }
}
```

Require an explicit review before applying notifications, content changes, or other effects. Invalidate the proposal when the condition identifier, event generation, authorization, or configured action changes.

## 9. Swift Testing policy fixtures

```swift
import Testing

struct LocationConditionTests {
    @Test("condition identifiers are stable app-owned routes")
    func identifiersAreNotRandomPerLaunch() {
        let first = "studio"
        let second = "studio"
        #expect(first == second)
    }

    @Test("location action proposal does not require raw coordinates")
    func proposalInputIsCoarse() {
        let placeLabel = "Studio"
        let eventDirection = "arrived"
        let configuredAction = "show the session checklist"

        #expect(!placeLabel.isEmpty)
        #expect(!eventDirection.isEmpty)
        #expect(!configuredAction.isEmpty)
    }
}
```

Add physical integration tests for permission, accuracy, geographic transitions, beacon transitions, background relaunch, reboot/unlock, condition limit, service-session diagnostics, map/list accessibility, archive, and TestFlight.

## Sources

- [Core Location](https://developer.apple.com/documentation/corelocation)
- [CLMonitor actor](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v)
- [CLMonitor.Event](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/event)
- [CLMonitor.Events](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/events-swift.struct)
- [CLMonitor.Record](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/record)
- [CLMonitor.CircularGeographicCondition](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/circulargeographiccondition)
- [CLMonitor.BeaconIdentityCondition](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v/beaconidentitycondition)
- [CLCondition](https://developer.apple.com/documentation/corelocation/clcondition-swift.protocol)
- [CLMonitoringState](https://developer.apple.com/documentation/corelocation/clmonitoringstate)
- [Monitoring the user’s proximity to geographic regions](https://developer.apple.com/documentation/corelocation/monitoring-the-user-s-proximity-to-geographic-regions)
- [Handling location updates in the background](https://developer.apple.com/documentation/corelocation/handling-location-updates-in-the-background)
- [CLLocationUpdate](https://developer.apple.com/documentation/corelocation/cllocationupdate)
- [CLServiceSession](https://developer.apple.com/documentation/corelocation/clservicesession-pt7n)
- [NSLocationWhenInUseUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocationwheninuseusagedescription)
- [NSLocationAlwaysAndWhenInUseUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocationalwaysandwheninuseusagedescription)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
