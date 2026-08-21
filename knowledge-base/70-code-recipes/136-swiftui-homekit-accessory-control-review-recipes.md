# SwiftUI HomeKit and Matter accessory-control review recipes

These are compile-oriented route sketches for a named iOS target. They are intentionally explicit about ownership, authorization, freshness, and physical side effects. Replace placeholder types and error policy in the target; do not treat a pasted snippet as proof that HomeKit, Matter, an accessory, or an App Store archive is configured.

This page pairs with [SwiftUI HomeKit and Matter accessory-control review](../42-framework-deep-dives/93-swiftui-homekit-accessory-control-review.md), [SwiftUI HomeKit and Matter accessory-control review route](../50-capability-recipes/124-swiftui-homekit-accessory-control-review-route.md), and the [proof matrix](../60-verification/118-swiftui-homekit-accessory-control-review-proof-matrix.md).

## Recipe 1: define the route contract

Start with values and intents, not view references:

~~~swift
enum HomeRouteState {
    case unavailable(String)
    case needsPermission
    case loading
    case noHomes
    case ready(HomeSnapshot)
    case setupPending
    case commandPending(CommandID)
    case proposalNeedsReview(HomeControlProposal)
    case failed(String)
}

enum HomeIntent {
    case selectHome(UUID)
    case refresh
    case addAccessory
    case read(ServiceID)
    case set(ServiceID, CharacteristicValue)
    case reviewProposal(HomeControlProposal)
    case applyProposal(HomeControlProposal)
}
~~~

Keep view state, framework state, generated output, and physical side effects separate. A HomeIntent is not a HomeKit call; it is an input to the single command owner.

## Recipe 2: create one HomeKit lifecycle owner

The manager should be created once for the app’s HomeKit work and should outlive a single row or detail view:

~~~swift
import HomeKit
import SwiftUI

@MainActor
final class HomeKitStore: NSObject, ObservableObject {
    let homeManager = HMHomeManager()

    @Published private(set) var route: HomeRouteState = .loading
    @Published private(set) var topologyRevision = 0

    private var selectedHomeID: UUID?

    override init() {
        super.init()
        homeManager.delegate = self
        publishAuthorizationAndHomes()
    }

    func selectHome(_ id: UUID) {
        selectedHomeID = id
        rebuildProjection()
    }

    func refresh() {
        rebuildProjection()
    }

    private func publishAuthorizationAndHomes() {
        // Map authorizationStatus and homes to explicit UI states.
        // Do not request access merely to render a preview.
        rebuildProjection()
    }

    private func rebuildProjection() {
        // Resolve the selected home by UUID, normalize its current graph,
        // and publish a value-only HomeSnapshot.
    }
}

extension HomeKitStore: HMHomeManagerDelegate {
    func homeManagerDidUpdateHomes(_ manager: HMHomeManager) {
        topologyRevision += 1
        publishAuthorizationAndHomes()
    }
}
~~~

The exact delegate surface and concurrency annotations must be compiled against the selected SDK. The important rules are one manager, one reconciliation owner, and a UI-isolated value projection.

## Recipe 3: normalize the shared graph

Resolve by stable identifiers and filter for the product’s task:

~~~swift
struct HomeSnapshot {
    var homeID: UUID
    var homeName: String
    var services: [ServiceSnapshot]
    var topologyRevision: Int
    var refreshedAt: Date?
}

struct ServiceSnapshot: Identifiable {
    var id: UUID
    var homeID: UUID
    var accessoryID: UUID
    var roomName: String?
    var displayName: String
    var characteristicType: String
    var value: CharacteristicValue
    var readable: Bool
    var writable: Bool
    var supportsNotification: Bool
    var freshness: Freshness
    var reachability: Reachability
}

func project(home: HMHome, topologyRevision: Int) -> HomeSnapshot {
    let services = home.accessories
        .flatMap { accessory in
            accessory.services
                .filter { service in service.isUserInteractive }
                .compactMap { service in
                    makeSnapshot(home: home, accessory: accessory, service: service)
                }
        }

    return HomeSnapshot(
        homeID: home.uniqueIdentifier,
        homeName: home.name,
        services: services,
        topologyRevision: topologyRevision,
        refreshedAt: Date()
    )
}
~~~

The product should decide which service types are supported. Do not show a technical service just because it exists, and do not infer a user-facing control from a raw characteristic type.

## Recipe 4: map characteristics with a typed adapter

The value property is not a universal Swift type. Normalize only known types:

~~~swift
enum CharacteristicValue: Equatable {
    case boolean(Bool)
    case number(Double, unit: String, minimum: Double?, maximum: Double?)
    case enumeration(raw: String, label: String)
    case text(String)
    case redactedData
    case unknown(type: String)
}

struct CharacteristicAdapter {
    let type: String
    let readable: Bool
    let writable: Bool
    let supportsNotification: Bool
    let metadataDescription: String?

    static func make(from characteristic: HMCharacteristic) -> CharacteristicAdapter {
        CharacteristicAdapter(
            type: characteristic.characteristicType,
            readable: characteristic.properties.contains(HMCharacteristicPropertyReadable),
            writable: characteristic.properties.contains(HMCharacteristicPropertyWritable),
            supportsNotification: characteristic.properties.contains(HMCharacteristicPropertySupportsEventNotification),
            metadataDescription: characteristic.metadata?.description
        )
    }
}
~~~

Use documented characteristic types and metadata in the target. An unknown value should fail closed into a diagnostic or read-only state, not become an invented Toggle.

## Recipe 5: wrap a read operation

An explicit read is useful when a consequential decision depends on freshness:

~~~swift
func read(_ characteristic: HMCharacteristic) async throws -> Any? {
    try await withCheckedThrowingContinuation { continuation in
        characteristic.readValue { error in
            if let error {
                continuation.resume(throwing: error)
            } else {
                continuation.resume(returning: characteristic.value)
            }
        }
    }
}
~~~

Do not assume that a read means the physical device is safe, complete, or permanently current. Record the read time and the source revision. If the target SDK exposes an async overload, prefer the documented overload after checking its availability and isolation.

## Recipe 6: validate and write a characteristic

Separate intent validation from the framework write:

~~~swift
struct PendingCommand {
    let id: UUID
    let homeID: UUID
    let serviceID: UUID
    let sourceTopologyRevision: Int
    let target: CharacteristicValue
    let requiresConfirmation: Bool
}

func write(
    _ characteristic: HMCharacteristic,
    value: Any?,
    pending: PendingCommand
) async throws {
    // Validate readable/writable properties, metadata bounds, type,
    // current home membership, and safety policy before this function.
    try await withCheckedThrowingContinuation { continuation in
        characteristic.writeValue(value) { error in
            if let error {
                continuation.resume(throwing: error)
            } else {
                continuation.resume()
            }
        }
    }
}
~~~

The successful completion records that HomeKit processed the request. It does not replace the subsequent characteristic notification or read that confirms the reported state. Keep pending state until the reconciliation policy resolves it.

## Recipe 7: register targeted notifications

Observe only values required by the visible route:

~~~swift
func enableObservation(_ characteristic: HMCharacteristic) async throws {
    try await withCheckedThrowingContinuation { continuation in
        characteristic.enableNotification(true) { error in
            if let error {
                continuation.resume(throwing: error)
            } else {
                continuation.resume()
            }
        }
    }
}
~~~

The coordinator should own registration and cleanup. A reused row must not attach a duplicate observer. On callback, locate the current characteristic by UUID, verify home membership, normalize the value, update freshness, and resolve pending commands.

## Recipe 8: model reconciliation states

Keep last-known state distinct from current and desired state:

~~~swift
enum Freshness: Equatable {
    case current(Date)
    case lastKnown(Date)
    case pending(Date)
    case unknown
}

enum Reachability: Equatable {
    case reachable
    case unreachable
    case unavailable
}

struct ControlPresentation {
    var reported: CharacteristicValue?
    var desired: CharacteristicValue?
    var freshness: Freshness
    var reachability: Reachability
    var errorMessage: String?
}
~~~

Drive the Toggle, Slider, or Button from this model. Do not mutate reported to desired just because the user touched the control.

## Recipe 9: start HomeKit accessory setup

Prefer the current documented setup route for the selected SDK:

~~~swift
func addAccessory() async throws -> HMAccessorySetupResult {
    let setupManager = HMAccessorySetupManager()
    let request = HMAccessorySetupRequest()

    // Configure the request for the selected home/context according to
    // the SDK and target. Do not store setup payloads in logs.
    return try await setupManager.performAccessorySetup(using: request)
}
~~~

This is a compile-oriented sketch. The concrete request configuration and availability must be verified in the named target. After the result returns, use the home and accessory identifiers to rebuild the shared projection. Do not create an app-owned “new accessory” record solely from the fact that the system sheet closed.

## Recipe 10: route the legacy or home-owned setup path

When the current target calls for HMHome setup, keep it user-initiated and refresh afterward:

~~~swift
func addToHome(_ home: HMHome) {
    home.addAndSetupAccessories { error in
        Task { @MainActor in
            if let error {
                // Map cancellation, denial, unsupported, and setup errors.
                self.route = .failed(error.localizedDescription)
            } else {
                // Re-read the home graph. Do not assume list positions.
                self.refresh()
            }
        }
    }
}
~~~

Apple’s current documentation marks older overloads/deprecated variants, so quarantine them behind a target-specific adapter rather than spreading deprecated calls through SwiftUI views.

## Recipe 11: build a MatterSupport request

Matter setup has a request/topology and, when required, an extension handler:

~~~swift
import MatterSupport

func makeMatterRequest() -> MatterAddDeviceRequest {
    let homes = [
        MatterAddDeviceRequest.Home(name: "Main Home")
    ]
    let topology = MatterAddDeviceRequest.Topology(
        ecosystemName: "Example Ecosystem",
        homes: homes
    )
    let request = MatterAddDeviceRequest(topology: topology)
    request.showDeviceCriteria = .allDevices
    return request
}

func startMatterSetup() async throws {
    guard MatterAddDeviceRequest.isSupported else {
        throw SetupError.unsupported
    }
    let request = makeMatterRequest()
    try await request.perform()
    // Reload ecosystem state and show readiness separately.
}
~~~

Use a narrower DeviceCriteria when the product can safely identify the intended class of device. Criteria filter the picker; they are not a substitute for commissioning or credential validation. Check the exact initializer, support property, and async route against the selected SDK.

## Recipe 12: keep extension setup credentials out of the app UI

When the target uses MatterAddDeviceExtensionRequestHandler, keep the handler’s responsibilities explicit:

~~~text
extension request
  -> select/validate home
  -> validate device credential and attestation
  -> commission with the onboarding payload
  -> select system/default Wi-Fi or Thread route as supported
  -> configure name and room
  -> return only after commissioning is complete
~~~

Do not print onboarding payloads, Wi-Fi credentials, or attestation material. The extension’s principal-class and Info.plist configuration are part of the target artifact and must be verified in the built extension, not only in the source.

## Recipe 13: define a typed AI proposal

Keep the model output bounded:

~~~swift
struct CharacteristicWrite {
    let serviceID: UUID
    let characteristicType: String
    let value: CharacteristicValue
}

struct HomeControlProposal {
    let homeID: UUID
    let sourceTopologyRevision: Int
    let writes: [CharacteristicWrite]
    let explanation: String
    let warnings: [String]
    let requiresConfirmation: Bool
}
~~~

Provide only selected, typed context:

~~~text
home name
room name
service display name
supported characteristic type
typed current value
unit and freshness
reachable/unreachable
user request
~~~

Keep cameras, microphones, locks, credentials, raw setup payloads, and unrelated rooms out of context unless the person explicitly selected them and the product requires them. An AI explanation is optional; exact device identity, metadata validation, and side-effect policy remain deterministic.

## Recipe 14: validate an AI proposal before apply

Use the same validation path as a manual control:

~~~swift
enum ProposalValidation {
    case valid
    case stale
    case ambiguous(String)
    case unwritable(String)
    case outOfRange(String)
    case unsafe(String)
}

func validate(
    _ proposal: HomeControlProposal,
    against snapshot: HomeSnapshot
) -> ProposalValidation {
    guard proposal.homeID == snapshot.homeID else {
        return .stale
    }
    guard proposal.sourceTopologyRevision == snapshot.topologyRevision else {
        return .stale
    }
    // Resolve IDs, type-check values, inspect metadata, and apply safety rules.
    return .valid
}
~~~

At apply time, revalidate against the latest snapshot. Show exact writes, room/device context, warnings, and the confirmation decision. The model cannot call writeValue, execute an action set, create a trigger, unlock a door, or change a heater without passing this gate.

## Recipe 15: SwiftUI service card

Render the projection, not the framework object:

~~~swift
struct ServiceCard: View {
    let service: ServiceSnapshot
    let onSet: (CharacteristicValue) -> Void
    let onDetails: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading) {
                    Text(service.displayName)
                    Text(service.roomName ?? "Home")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer()
                freshnessLabel
            }

            valueView

            HStack {
                primaryControl
                Button("Details", action: onDetails)
            }
        }
        .padding()
        .accessibilityElement(children: .contain)
    }

    private var freshnessLabel: some View {
        Text(service.freshness.description)
            .font(.caption2)
            .foregroundStyle(.secondary)
    }

    private var valueView: some View {
        Text(service.value.displayLabel)
    }

    @ViewBuilder
    private var primaryControl: some View {
        if service.writable {
            Button("Change", action: {})
        } else {
            Text("Read only")
        }
    }
}
~~~

Use a real Toggle, Slider, Picker, or Button in the target once the characteristic adapter knows the type. The sample deliberately avoids pretending that every service is a Boolean.

## Recipe 16: apply a bounded glass group

Keep glass optional and functional:

~~~swift
struct AccessoryGlassGroup<Content: View>: View {
    @ViewBuilder let content: () -> Content

    var body: some View {
        content()
            .padding()
            .background {
                // Use the selected SDK's Liquid Glass API when available.
                // Keep the same hierarchy with a system material fallback.
                RoundedRectangle(cornerRadius: 24)
                    .fill(.regularMaterial)
            }
    }
}
~~~

When adopting Liquid Glass in the named target, use GlassEffectContainer for related controls, preserve semantic content, and test reduced transparency/increased contrast. Do not wrap system-owned HomeKit or Matter setup UI in an app-owned glass shell.

## Recipe 17: proposal review view

The review card should expose the side effect:

~~~swift
struct ProposalReview: View {
    let proposal: HomeControlProposal
    let validation: ProposalValidation
    let onApply: () -> Void
    let onCancel: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Review changes")
                .font(.title3)
            Text(proposal.explanation)
            ForEach(proposal.writes.indices, id: \.self) { index in
                Text(writeLabel(proposal.writes[index]))
            }
            if !proposal.warnings.isEmpty {
                Text(proposal.warnings.joined(separator: " "))
                    .foregroundStyle(.orange)
            }
            HStack {
                Button("Cancel", action: onCancel)
                Button("Apply", action: onApply)
                    .disabled(!isValid(validation))
            }
        }
        .padding()
    }
}
~~~

If the source revision changes while the review is open, replace Apply with “Refresh proposal” or ask the person to review the changed targets again.

## Recipe 18: failure and recovery mapping

Map errors to product states, not generic red text:

~~~swift
enum HomeFailure {
    case notAuthorized
    case noHome
    case accessoryUnavailable
    case characteristicNotWritable
    case valueRejected
    case setupCancelled
    case setupUnsupported
    case commissioningFailed
    case staleProposal
    case unknown(String)
}

func recovery(for failure: HomeFailure) -> RecoveryAction {
    switch failure {
    case .notAuthorized:
        return .openSettings
    case .noHome:
        return .showHomeSetup
    case .accessoryUnavailable:
        return .retryRead
    case .characteristicNotWritable, .valueRejected:
        return .showDetails
    case .setupCancelled, .setupUnsupported, .commissioningFailed:
        return .retrySetup
    case .staleProposal:
        return .refreshContext
    case .unknown:
        return .support
    }
}
~~~

Do not offer Retry for a safety-sensitive command without re-reading the current state and requiring confirmation again.

## Recipe 19: fixture matrix

Build deterministic fixtures before connecting a physical accessory:

~~~text
fixture/authorized-single-home
fixture/denied-access
fixture/revoked-in-settings
fixture/no-homes
fixture/multiple-homes
fixture/room-renamed
fixture/accessory-unreachable
fixture/service-removed
fixture/boolean-readable-writable
fixture/numeric-range-and-unit
fixture/enumeration
fixture/notification-update
fixture/write-failure
fixture/setup-cancelled
fixture/matter-unsupported
fixture/matter-criteria-mismatch
fixture/matter-commissioning-failure
fixture/ai-stale-revision
fixture/ai-ambiguous-device
fixture/ai-out-of-range
~~~

HomeKit Accessory Simulator is useful for reproducible services and characteristics. It does not replace a physical accessory run, actual reachability, or release-build evidence.

## Recipe 20: acceptance record

Store an evidence record with the target and route:

~~~text
route: swiftui-homekit-accessory-control
target: <named Xcode target>
sdk: <selected SDK>
device: <physical device or simulator>
accessory: <simulated or physical identity>
home: <redacted stable test identity>
authorization: allow / deny / revoked
setup: HomeKit / Matter / not used
topology_revision: <value>
read_write: pass / fail
notification_reconciliation: pass / fail
ai_validation: pass / fail / not used
accessibility: VoiceOver / Dynamic Type / keyboard / pointer
performance: <measurement or not run>
archive: <artifact path or not run>
release_gate: pass / blocked
known_limits: <unsupported targets/accessories>
~~~

Do not report this as complete until every claimed gate has evidence from the named target.

## Sources

- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Enabling HomeKit in your app](https://developer.apple.com/documentation/homekit/enabling-homekit-in-your-app)
- [Configuring HomeKit access](https://developer.apple.com/documentation/xcode/configuring-homekit-access)
- [NSHomeKitUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nshomekitusagedescription)
- [HMHomeManager](https://developer.apple.com/documentation/homekit/hmhomemanager)
- [HMHome](https://developer.apple.com/documentation/homekit/hmhome)
- [HMAccessory](https://developer.apple.com/documentation/homekit/hmaccessory)
- [HMService](https://developer.apple.com/documentation/homekit/hmservice)
- [HMCharacteristic](https://developer.apple.com/documentation/homekit/hmcharacteristic)
- [Characteristic types](https://developer.apple.com/documentation/homekit/characteristic-types)
- [HMAccessorySetupManager](https://developer.apple.com/documentation/homekit/hmaccessorysetupmanager)
- [HMAccessorySetupResult](https://developer.apple.com/documentation/homekit/hmaccessorysetupresult)
- [performAccessorySetup(using:completionHandler:)](https://developer.apple.com/documentation/homekit/hmaccessorysetupmanager/performaccessorysetup%28using%3Acompletionhandler%3A%29)
- [Configuring a home automation device](https://developer.apple.com/documentation/homekit/configuring-a-home-automation-device)
- [Interacting with a home automation network](https://developer.apple.com/documentation/homekit/interacting-with-a-home-automation-network)
- [Testing your app with the HomeKit Accessory Simulator](https://developer.apple.com/documentation/homekit/testing-your-app-with-the-homekit-accessory-simulator)
- [MatterSupport](https://developer.apple.com/documentation/mattersupport)
- [Adding Matter support to your ecosystem](https://developer.apple.com/documentation/mattersupport/adding-matter-support-to-your-ecosystem)
- [MatterAddDeviceRequest](https://developer.apple.com/documentation/mattersupport/matteradddevicerequest)
- [MatterAddDeviceRequest.DeviceCriteria](https://developer.apple.com/documentation/mattersupport/matteradddevicerequest/devicecriteria)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [HomeKit Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/homekit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
