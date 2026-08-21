# SwiftUI CarPlay and vehicle-surface review recipes

These are compile-oriented route sketches for a named iPhone app target with an approved CarPlay category and a configured CarPlay scene. They are not compiled in this knowledge-base workspace. They do not prove managed entitlement approval, scene discovery, vehicle rendering, Siri, locked-phone behavior, audio coexistence, accessibility, privacy, AI availability, physical head-unit behavior, or release readiness.

Read the [CarPlay review](../42-framework-deep-dives/108-swiftui-carplay-vehicle-surface-review.md), [design guide](../21-design-deep-dives/136-swiftui-carplay-vehicle-surface-review-design.md), [route](../50-capability-recipes/139-swiftui-carplay-vehicle-surface-review-route.md), and [proof matrix](../60-verification/133-swiftui-carplay-vehicle-surface-review-proof-matrix.md) first. Replace placeholders with the current SDK signatures and the actual target’s domain services.

## Recipe 1: record the category and target contract

Keep category eligibility and target configuration in one review record.

~~~swift
import Foundation

struct CarPlayTargetContract: Codable, Sendable, Equatable {
    enum Category: String, Codable, Sendable {
        case audio
        case communication
        case charging
        case navigation
        case parking
        case quickOrdering
    }

    let bundleID: String
    let category: Category
    let managedEntitlementKey: String
    let sceneConfigurationName: String
    let sceneDelegateName: String
    let isNavigation: Bool
    let dashboardEnabled: Bool
    let appIntentEnabled: Bool
    let activityKitEnabled: Bool
}
~~~

This record documents intent. Verify the actual signed archive separately. Do not let the app infer category permissions from this struct.

## Recipe 2: define an entitlement map

Use a single source for build-review output and tests.

~~~swift
enum CarPlayEntitlement {
    static func key(for category: CarPlayTargetContract.Category) -> String {
        switch category {
        case .audio:
            return "com.apple.developer.carplay-audio"
        case .communication:
            return "com.apple.developer.carplay-communication"
        case .charging:
            return "com.apple.developer.carplay-charging"
        case .navigation:
            return "com.apple.developer.carplay-maps"
        case .parking:
            return "com.apple.developer.carplay-parking"
        case .quickOrdering:
            return "com.apple.developer.carplay-quick-ordering"
        }
    }
}
~~~

The mapping is a checklist, not a request for a capability. Confirm that Apple approved the managed entitlement and that the exported archive contains the intended Boolean.

## Recipe 3: store a scene-scoped coordinator

A coordinator should own the interface controller and disconnect state. Keep it independent of a SwiftUI view lifecycle.

~~~swift
import CarPlay
import Foundation

@MainActor
final class CarPlaySceneStore: ObservableObject {
    @Published private(set) var interfaceController: CPInterfaceController?
    @Published private(set) var phase: Phase = .disconnected

    enum Phase: Sendable, Equatable {
        case disconnected
        case connecting
        case ready
        case limited
        case failed(String)
    }

    func connect(_ controller: CPInterfaceController) {
        phase = .connecting
        interfaceController = controller
    }

    func ready() {
        phase = .ready
    }

    func setLimited(_ limited: Bool) {
        phase = limited ? .limited : .ready
    }

    func disconnect() {
        interfaceController = nil
        phase = .disconnected
    }
}
~~~

The actual implementation may use the Observation framework rather than ObservableObject. The important boundary is that the scene store does not pretend a connected controller means synchronized domain data.

## Recipe 4: implement a non-navigation scene delegate

Use the system-created scene delegate and set a root template before returning.

~~~swift
import CarPlay
import Foundation

@MainActor
final class TemplateCarPlaySceneDelegate: NSObject, CPTemplateApplicationSceneDelegate {
    private let sceneStore = CarPlaySceneStore()
    private var interfaceController: CPInterfaceController?

    func templateApplicationScene(
        _ templateApplicationScene: CPTemplateApplicationScene,
        didConnect interfaceController: CPInterfaceController
    ) {
        self.interfaceController = interfaceController
        sceneStore.connect(interfaceController)

        let root = makeRootTemplate()
        interfaceController.setRootTemplate(root, animated: false) { [weak self] success, error in
            guard let self else { return }
            if let error {
                self.sceneStore.disconnect()
                return
            }
            if success {
                self.sceneStore.ready()
            }
        }
    }

    func templateApplicationScene(
        _ templateApplicationScene: CPTemplateApplicationScene,
        didDisconnectInterfaceController interfaceController: CPInterfaceController
    ) {
        self.interfaceController = nil
        sceneStore.disconnect()
    }

    private func makeRootTemplate() -> CPTemplate {
        let item = CPListItem(text: "Recent", detailText: "Choose an item")
        item.handler = { item, completion in
            completion()
        }
        let section = CPListSection(items: [item])
        return CPListTemplate(title: "Library", sections: [section])
    }
}
~~~

A real app should load a bounded projection before building the template and should report failures in CarPlay. Do not leave a handler pending forever.

## Recipe 5: implement the navigation connection

Navigation is the special path that receives a CPWindow. Keep the map root separate from template content.

~~~swift
import CarPlay
import UIKit

@MainActor
final class NavigationCarPlaySceneDelegate: NSObject, CPTemplateApplicationSceneDelegate {
    private var interfaceController: CPInterfaceController?
    private weak var carPlayWindow: CPWindow?

    func templateApplicationScene(
        _ templateApplicationScene: CPTemplateApplicationScene,
        didConnect interfaceController: CPInterfaceController,
        to window: CPWindow
    ) {
        self.interfaceController = interfaceController
        self.carPlayWindow = window

        let mapViewController = MapOnlyViewController()
        window.rootViewController = mapViewController

        let mapTemplate = CPMapTemplate()
        interfaceController.setRootTemplate(mapTemplate, animated: false) { success, error in
            // Publish root readiness and any failure into the domain state.
        }
    }

    func templateApplicationScene(
        _ templateApplicationScene: CPTemplateApplicationScene,
        didDisconnect interfaceController: CPInterfaceController,
        from window: CPWindow
    ) {
        self.interfaceController = nil
        self.carPlayWindow = nil
    }
}
~~~

The map view controller must draw only map content. Put controls, alerts, route choices, and user interaction in the CarPlay templates.

## Recipe 6: keep map content separate

Make the boundary visible in the type system.

~~~swift
import UIKit

final class MapOnlyViewController: UIViewController {
    override func loadView() {
        let view = UIView()
        view.backgroundColor = .systemBackground
        self.view = view
        // Add the map renderer here.
        // Do not add alert, button, route-card, or custom navigation-bar UI here.
    }
}
~~~

A source review can establish that the window is map-only. A physical head-unit run is needed to establish that the map, route, and system template remain usable together.

## Recipe 7: create a bounded list with safe handlers

Keep domain identifiers opaque to CarPlay and make handlers idempotent.

~~~swift
import CarPlay

struct CarPlayRow: Sendable {
    let id: String
    let title: String
    let detail: String?
}

@MainActor
func makeListTemplate(
    title: String,
    rows: [CarPlayRow],
    onSelect: @escaping @MainActor (String) async -> Result<CPTemplate, Error>
) -> CPListTemplate {
    let items = rows.prefix(50).map { row in
        let item = CPListItem(text: row.title, detailText: row.detail)
        item.userInfo = row.id
        item.handler = { item, completion in
            Task { @MainActor in
                let result = await onSelect(row.id)
                switch result {
                case .success:
                    break
                case .failure:
                    break
                }
                completion()
            }
        }
        return item
    }

    return CPListTemplate(
        title: title,
        sections: [CPListSection(items: Array(items))]
    )
}
~~~

The prefix is not a universal vehicle limit. Read maximumItemCount and vehicle session limits in the actual route. Map the result into a loading, committed, or error template rather than discarding it.

## Recipe 8: adapt to session limits

Use the session configuration as runtime input.

~~~swift
import CarPlay

struct CarPlayLimits: Sendable, Equatable {
    let limitedInterfaces: CPLimitableUserInterface
    let contentStyle: CPContentStyle
    let supportsVideoPlayback: Bool
}

@MainActor
func limits(from sessionConfiguration: CPSessionConfiguration) -> CarPlayLimits {
    CarPlayLimits(
        limitedInterfaces: sessionConfiguration.limitedUserInterfaces,
        contentStyle: sessionConfiguration.contentStyle,
        supportsVideoPlayback: sessionConfiguration.supportsVideoPlayback
    )
}
~~~

Rebuild the visible route when the delegate reports a limit change. A vehicle-specific limit is not a reason to show stale or inaccessible content.

## Recipe 9: provide search fallbacks

Keep search results bounded and make keyboard limits explicit in state.

~~~swift
struct SearchProjection: Sendable, Equatable {
    let query: String
    let recentIDs: [String]
    let favoriteIDs: [String]
    let keyboardLimited: Bool
    let resultIDs: [String]
}

func searchChoices(_ projection: SearchProjection) -> [String] {
    if projection.keyboardLimited && projection.query.isEmpty {
        return projection.favoriteIDs.isEmpty
            ? projection.recentIDs
            : projection.favoriteIDs
    }
    return Array(projection.resultIDs.prefix(20))
}
~~~

Use CPSearchTemplate for the system search surface. Do not force a long form when the current vehicle reports a limited keyboard.

## Recipe 10: wire an audio Now Playing route

Use the shared Now Playing template and update MediaPlayer state from the playback owner.

~~~swift
import CarPlay
import MediaPlayer

@MainActor
final class AudioCarPlayRouter {
    func showNowPlaying(on controller: CPInterfaceController) {
        let template = CPNowPlayingTemplate.shared
        template.allowsMiniPlayer = true
        controller.pushTemplate(template, animated: true) { success, error in
            // Record navigation result and error.
        }
    }

    func publish(itemTitle: String, artist: String?) {
        var info: [String: Any] = [
            MPMediaItemPropertyTitle: itemTitle
        ]
        if let artist {
            info[MPMediaItemPropertyArtist] = artist
        }
        MPNowPlayingInfoCenter.default().nowPlayingInfo = info
    }
}
~~~

This sketch does not prove the audio entitlement, audio session policy, buffering, interruption, or physical vehicle behavior.

## Recipe 11: configure a Siri assistant cell

Use the assistant cell only when the category-specific intent route exists.

~~~swift
import CarPlay

func assistantList(
    sections: [CPListSection],
    action: CPAssistantCellActionType
) -> CPListTemplate {
    let configuration = CPAssistantCellConfiguration(
        position: .top,
        visibility: .always,
        assistantAction: action
    )
    return CPListTemplate(
        title: "Library",
        sections: sections,
        assistantCellConfiguration: configuration
    )
}
~~~

Audio apps should support INPlayMediaIntent and communication apps should support INStartCallIntent for the documented assistant-cell paths. Test the actual Siri flow with the iPhone locked and the vehicle connected.

## Recipe 12: model a communication row

Use CPMessageListItem for the conversation/contact representation and let Siri own the flow.

~~~swift
import CarPlay

func makeConversationItem(
    conversationID: String,
    text: String,
    detail: String?,
    leading: CPMessageListItemLeadingConfiguration,
    trailing: CPMessageListItemTrailingConfiguration?
) -> CPMessageListItem {
    let item = CPMessageListItem(
        conversationIdentifier: conversationID,
        text: text,
        leadingConfiguration: leading,
        trailingConfiguration: trailing,
        detailText: detail,
        trailingText: nil
    )
    item.userInfo = conversationID
    return item
}
~~~

Do not add a custom selection handler to replace the system Siri compose/read/reply behavior. Re-resolve the conversation and recipient before committing any message action.

## Recipe 13: record a vehicle-aware command

Keep proposal, confirmation, and commit distinct.

~~~swift
import Foundation

struct VehicleCommand: Codable, Sendable, Equatable {
    enum Kind: String, Codable, Sendable {
        case startNavigation
        case playItem
        case callContact
        case sendMessage
        case placeOrder
    }

    let id: UUID
    let kind: Kind
    let entityID: String
    let sourceRevision: Int64
    let requiresConfirmation: Bool
}

enum CommandResult: Sendable, Equatable {
    case proposed(VehicleCommand)
    case awaitingConfirmation(VehicleCommand)
    case committed(revision: Int64)
    case rejected(reason: String)
    case unavailable(reason: String)
}
~~~

Every handler, Siri intent, App Intent, or AI proposal should call the same command service. Keep the command result separate from the CarPlay template callback.

## Recipe 14: validate an AI candidate

Use a closed candidate schema and revalidation.

~~~swift
struct AICandidate: Codable, Sendable, Equatable {
    let entityID: String
    let label: String
    let sourceRevision: Int64
    let reason: String?
}

struct CandidatePolicy: Sendable {
    let allowedKinds: Set<VehicleCommand.Kind>
    let maxReasonCharacters: Int
}

func validate(
    _ candidate: AICandidate,
    currentRevision: Int64,
    policy: CandidatePolicy,
    kind: VehicleCommand.Kind
) -> Result<VehicleCommand, Error> {
    guard policy.allowedKinds.contains(kind) else {
        return .failure(CocoaError(.operationNotPermitted))
    }
    guard candidate.sourceRevision == currentRevision else {
        return .failure(CocoaError(.fileReadInapplicableStringEncoding))
    }
    guard candidate.entityID.isEmpty == false else {
        return .failure(CocoaError(.validationMissingMandatoryProperty))
    }

    return .success(
        VehicleCommand(
            id: UUID(),
            kind: kind,
            entityID: candidate.entityID,
            sourceRevision: candidate.sourceRevision,
            requiresConfirmation: true
        )
    )
}
~~~

The exact error types and domain validation belong to the app. The important behavior is stale rejection, allowlisting, explicit confirmation, and a deterministic fallback.

## Recipe 15: gate Foundation Models

Do not assume the model is available because the code compiles.

~~~swift
import FoundationModels

enum LocalModelState: Sendable, Equatable {
    case available
    case unavailable(String)
}

func localModelState() -> LocalModelState {
    let model = SystemLanguageModel.default
    switch model.availability {
    case .available:
        return .available
    case .unavailable(let reason):
        return .unavailable(String(describing: reason))
    @unknown default:
        return .unavailable("Unknown availability")
    }
}
~~~

Use the current SDK’s availability cases and deployment checks. If the model is unavailable, route to deterministic candidates or defer to the iPhone review surface.

## Recipe 16: keep the iPhone Liquid Glass shell separate

Use SwiftUI for app-owned review and settings, not for the CarPlay template layer.

~~~swift
import SwiftUI

struct VehicleReviewShell: View {
    let title: String
    let summary: String
    let confirm: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(title)
                .font(.largeTitle.bold())
            Text(summary)
                .foregroundStyle(.secondary)
            Button("Confirm", action: confirm)
                .buttonStyle(.borderedProminent)
        }
        .padding()
        .glassEffect()
    }
}
~~~

Use current SwiftUI and Liquid Glass guidance, then test Reduce Transparency, increased contrast, Dynamic Type, VoiceOver, and reduced motion. Do not attempt to host this view in the CarPlay CPWindow or treat its appearance as vehicle proof.

## Recipe 17: preserve a pending command across disconnect

Keep domain state on iPhone.

~~~swift
import Foundation

struct PendingVehicleAction: Codable, Sendable, Equatable {
    let id: UUID
    let kind: VehicleCommand.Kind
    let entityID: String
    let sourceRevision: Int64
    let createdAt: Date
    let expiresAt: Date?
    let state: State

    enum State: String, Codable, Sendable {
        case waitingForCarPlay
        case waitingForConfirmation
        case committed
        case failed
        case expired
    }
}

func reconnectable(_ action: PendingVehicleAction, now: Date) -> Bool {
    guard action.state == .waitingForCarPlay || action.state == .waitingForConfirmation else {
        return false
    }
    return action.expiresAt.map { $0 > now } ?? true
}
~~~

A disconnect should clear scene references, not erase a user-approved record or a recoverable draft.

## Recipe 18: make a Live Activity passive in CarPlay

Keep the content model concise and do not assume interactive controls in CarPlay.

~~~swift
import ActivityKit

struct VehicleProgressAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var title: String
        var detail: String
        var progress: Double
        var revision: Int64
    }

    var taskID: String
}
~~~

Use ActivityKit and the Live Activities HIG to design the CarPlay presentation. If the user needs an action, provide it through a permitted CarPlay template. The Live Activity is a system projection of committed progress.

## Recipe 19: define evidence records

Record exactly what a run established.

~~~swift
import Foundation

struct CarPlayEvidence: Codable, Sendable, Equatable {
    enum Kind: String, Codable, Sendable {
        case source
        case project
        case compile
        case simulator
        case lockedPhone
        case siri
        case physicalVehicle
        case archive
        case testFlight
        case production
    }

    let kind: Kind
    let device: String?
    let headUnit: String?
    let appVersion: String?
    let build: String?
    let observation: String
    let timestamp: Date
    let artifacts: [String]
}
~~~

Never write “works in CarPlay” without naming the device/head unit, build, route, and observation.

## Recipe 20: test the command reducer

Keep side effects behind a deterministic reducer.

~~~swift
import Testing

@Test
func staleAICandidateDoesNotCommit() {
    let candidate = AICandidate(
        entityID: "destination-1",
        label: "Home",
        sourceRevision: 4,
        reason: "Recent"
    )
    let policy = CandidatePolicy(
        allowedKinds: [.startNavigation],
        maxReasonCharacters: 120
    )

    let result = validate(
        candidate,
        currentRevision: 5,
        policy: policy,
        kind: .startNavigation
    )

    #expect({
        if case .failure = result { return true }
        return false
    }())
}
~~~

Add tests for duplicate command IDs, unauthorized entities, missing model, limited keyboard, disconnected scene, expired pending action, and a failed domain commit. Testing a reducer does not test Siri or a physical vehicle.

## Recipe 21: archive review commands

Keep release inspection separate from source confidence.

~~~text
xcodebuild -scheme YourApp -configuration Release archive -archivePath build/YourApp.xcarchive

codesign -d --entitlements :- build/YourApp.xcarchive/Products/Applications/YourApp.app

plutil -p build/YourApp.xcarchive/Products/Applications/YourApp.app/Info.plist

xcrun simctl list devices
~~~

Use the actual project’s scheme, signing settings, provisioning, and archive paths. Verify the selected CarPlay entitlement, scene manifest, embedded extensions, ActivityKit or WidgetKit targets, and version/build. Then install the signed artifact on the intended device and head unit.

## Recipe 22: record the final route decision

Before calling the route ready, fill the record:

~~~text
category:
managed entitlement:
scene configuration:
root template:
navigation window required:
vehicle limits observed:
locked-phone result:
Siri result:
audio result:
physical vehicle/head unit:
accessibility result:
privacy result:
AI fallback result:
archive signed-entitlement result:
TestFlight install result:
open risks:
~~~

A blank field is an unresolved release or product risk, not a reason to infer success.

## Sources

- [CarPlay](https://developer.apple.com/documentation/carplay)
- [Requesting CarPlay entitlements](https://developer.apple.com/documentation/carplay/requesting-carplay-entitlements)
- [Displaying content in CarPlay](https://developer.apple.com/documentation/carplay/displaying-content-in-carplay)
- [Using the CarPlay Simulator](https://developer.apple.com/documentation/carplay/using-the-carplay-simulator)
- [CPTemplateApplicationSceneDelegate](https://developer.apple.com/documentation/carplay/cptemplateapplicationscenedelegate)
- [CPInterfaceController](https://developer.apple.com/documentation/carplay/cpinterfacecontroller)
- [CPListTemplate](https://developer.apple.com/documentation/carplay/cplisttemplate)
- [CPListItem](https://developer.apple.com/documentation/carplay/cplistitem)
- [CPMapTemplate](https://developer.apple.com/documentation/carplay/cpmaptemplate)
- [CPNowPlayingTemplate](https://developer.apple.com/documentation/carplay/cpnowplayingtemplate)
- [CPMessageListItem](https://developer.apple.com/documentation/carplay/cpmessagelistitem)
- [CPAssistantCellConfiguration](https://developer.apple.com/documentation/carplay/cpassistantcellconfiguration)
- [CPSessionConfiguration](https://developer.apple.com/documentation/carplay/cpsessionconfiguration)
- [CarPlay HIG](https://developer.apple.com/design/human-interface-guidelines/carplay)
- [Live Activities HIG](https://developer.apple.com/design/human-interface-guidelines/live-activities)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [Configuring Siri support](https://developer.apple.com/documentation/xcode/configuring-siri-support)
- [Resolving and handling intents](https://developer.apple.com/documentation/sirikit/resolving-and-handling-intents)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
