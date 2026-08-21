# Watch, CarPlay, App Clip, and Communication Recipes

Use the [device and companion capability contracts](../42-framework-deep-dives/08-device-and-companion-capability-contracts.md) and [system-surface/extension composition guide](../43-system-framework-deep-dives/06-system-surface-and-extension-composition.md) before claiming pairing, vehicle, communication, App Clip, or system-surface behavior.

## Scope and compile boundary

These are compile-oriented route sketches for WatchConnectivity, CarPlay templates/scenes, App Clip invocation handling, CallKit, PushKit, and LiveCommunicationKit. They are not compiled in this documentation-only workspace and do not prove pairing, reachability, transfer timing, CarPlay entitlement/category approval, App Clip App Store configuration, APNs delivery, server call state, system call UI, audio-session behavior, default-calling eligibility, or physical/two-device release readiness.

Keep system and product state separate:

`system availability -> activation/invocation/token -> validated domain event -> system-owned surface -> service completion|fallback`

## Recipe 1: activate Watch Connectivity with explicit state

Configure the session and delegate before activation on both the iPhone and Watch targets. Deliver UI changes to the main actor from delegate callbacks.

```swift
import WatchConnectivity

final class CompanionSession: NSObject, WCSessionDelegate {
    private let session = WCSession.default
    private(set) var state = "idle"

    func start() {
        guard WCSession.isSupported() else {
            state = "unsupported"
            return
        }

        session.delegate = self
        state = "activating"
        session.activate()
    }

    func session(
        _ session: WCSession,
        activationDidCompleteWith activationState: WCSessionActivationState,
        error: Error?
    ) {
        state = error == nil ? "activated" : "failed"
        let reachable = session.isReachable
        Task { @MainActor in
            // Publish activationState/reachable into the SwiftUI model.
            _ = reachable
        }
    }

    #if os(iOS)
    func sessionDidBecomeInactive(_ session: WCSession) {
        state = "inactive"
    }

    func sessionDidDeactivate(_ session: WCSession) {
        state = "deactivated"
        session.activate()
    }
    #endif
}
```

The exact session lifecycle is target-sensitive. A paired watch, installed companion, activated session, and reachable counterpart are different states. Do not send a new transfer while the iPhone session is inactive/deactivated.

## Recipe 2: choose the Watch transport by meaning

```swift
import WatchConnectivity

extension CompanionSession {
    func sendLatestContext(_ context: [String: Any]) throws {
        guard session.activationState == .activated else { return }
        try session.updateApplicationContext(context)
    }

    func queueEvent(_ event: [String: Any]) {
        guard session.activationState == .activated else { return }
        _ = session.transferUserInfo(event)
    }

    func queueFile(_ fileURL: URL, metadata: [String: Any]) {
        guard session.activationState == .activated else { return }
        _ = session.transferFile(fileURL, metadata: metadata)
    }

    func sendImmediate(_ message: [String: Any]) {
        guard session.isReachable else {
            // Show a retry or use an explicitly equivalent queued route.
            return
        }

        session.sendMessage(
            message,
            replyHandler: { reply in
                // Decode and validate the reply off the UI path.
                _ = reply
            },
            errorHandler: { error in
                // Map timeout/unreachable/transport errors to a retry state.
                _ = error
            }
        )
    }
}
```

Include a schema version, account/profile ID, event ID, monotonic revision, and generated timestamp. Background transfers are queued/opportunistic; `sendMessage` is immediate only while the counterpart is reachable. Do not treat any of these as server confirmation.

## Recipe 3: apply companion events idempotently

Use an actor or serial reducer so the iPhone and watch can receive a duplicate, delayed, or older event without repeating a side effect.

```swift
import Foundation

struct CompanionEvent: Codable, Sendable {
    let id: UUID
    let schemaVersion: Int
    let accountID: String
    let revision: Int64
    let kind: String
    let payload: Data
}

actor CompanionEventReducer {
    private var appliedIDs = Set<UUID>()
    private var latestRevision: Int64 = 0

    func apply(_ event: CompanionEvent) throws {
        guard event.schemaVersion == 1 else {
            throw CocoaError(.coderValueNotFound)
        }
        guard event.accountID == currentAccountID else { return }
        guard !appliedIDs.contains(event.id) else { return }
        guard event.revision >= latestRevision else { return }

        // Decode a typed payload, validate current domain state, then commit
        // one durable side effect before adding the event ID.
        latestRevision = event.revision
        appliedIDs.insert(event.id)
    }

    private var currentAccountID = "account-from-keychain-or-session"
}
```

Persist the revision/applied IDs if a duplicate side effect would be harmful. Clear or quarantine pending private events when the user signs out or the active companion changes.

## Recipe 4: build a CarPlay template scene

CarPlay supplies the interface controller. Most categories should use system templates rather than drawing a general iPhone UI.

```swift
import CarPlay

final class CarPlaySceneDelegate: NSObject, CPTemplateApplicationSceneDelegate {
    private var interfaceController: CPInterfaceController?

    func templateApplicationScene(
        _ templateApplicationScene: CPTemplateApplicationScene,
        didConnect interfaceController: CPInterfaceController
    ) {
        self.interfaceController = interfaceController

        let item = CPListItem(
            text: "Current status",
            detailText: "Ready"
        )
        let list = CPListTemplate(
            title: "Example",
            sections: [CPListSection(items: [item])]
        )
        interfaceController.setRootTemplate(
            list,
            animated: false,
            completion: nil
        )
    }

    func templateApplicationScene(
        _ templateApplicationScene: CPTemplateApplicationScene,
        didDisconnectInterfaceController interfaceController: CPInterfaceController
    ) {
        self.interfaceController = nil
        // Persist safe domain state; tear down CarPlay-only observers/resources.
    }
}
```

The scene manifest, target entitlement/category, templates, and approval are part of the route. Test the CarPlay Simulator for lifecycle/template behavior and a real vehicle or aftermarket system for connection loss, audio, safe interaction, and hardware differences.

## Recipe 5: handle App Clip and full-app invocations

Handle a fresh URL and a resume without a URL. Use the same parser in the App Clip and full app, but validate all identifiers against current server/app state.

```swift
import SwiftUI

struct InvocationRouter: View {
    @State private var destination: String = "start"

    var body: some View {
        ContentView(destination: destination)
            .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { activity in
                guard let url = activity.webpageURL else {
                    destination = restoreLastFocusedTask()
                    return
                }
                destination = route(url: url)
            }
    }

    private func route(url: URL) -> String {
        guard url.scheme == "https",
              url.host == "example.test" else {
            return "invalid-invocation"
        }

        let components = URLComponents(
            url: url,
            resolvingAgainstBaseURL: false
        )
        let path = components?.path ?? "/"
        guard path.hasPrefix("/order/") else {
            return "unsupported-invocation"
        }
        let id = path.replacingOccurrences(of: "/order/", with: "")
        guard id.count < 100 else { return "invalid-invocation" }
        saveFocusedTask(id)
        return "order-\(id)"
    }

    private func restoreLastFocusedTask() -> String { "restored" }
    private func saveFocusedTask(_ id: String) { _ = id }
}
```

An invocation URL may be absent when a person returns from a notification, App Library, or App Switcher. Keep local state minimal and expired. After full-app installation replaces the App Clip, the full app must handle the same invocations. Treat URL parameters as hints, not payment/account/permission proof.

## Recipe 6: register PushKit only for a real VoIP service

PushKit is not a generic background wake mechanism. For VoIP on current SDKs, report the call through CallKit quickly.

```swift
import CallKit
import PushKit

final class VoIPPushCoordinator: NSObject, PKPushRegistryDelegate {
    private let provider: CXProvider
    private var registry: PKPushRegistry?

    override init() {
        let configuration = CXProviderConfiguration(localizedName: "Example Calls")
        configuration.supportsVideo = true
        configuration.supportedHandleTypes = [.phoneNumber, .generic]
        provider = CXProvider(configuration: configuration)
        super.init()
        provider.setDelegate(self, queue: nil)
    }

    func start() {
        let registry = PKPushRegistry(queue: nil)
        registry.delegate = self
        self.registry = registry
        registry.desiredPushTypes = [.voIP]
    }

    func pushRegistry(
        _ registry: PKPushRegistry,
        didUpdate pushCredentials: PKPushCredentials,
        for type: PKPushType
    ) {
        guard type == .voIP else { return }
        // Send the opaque token and environment to the server over an
        // authenticated channel. Never log the raw token.
    }

    func pushRegistry(
        _ registry: PKPushRegistry,
        didReceiveIncomingPushWith payload: PKPushPayload,
        for type: PKPushType,
        completion: @escaping () -> Void
    ) {
        guard type == .voIP,
              let call = ValidatedCall(payload.dictionaryPayload) else {
            completion()
            return
        }

        let update = CXCallUpdate()
        update.remoteHandle = CXHandle(type: .generic, value: call.handle)
        update.hasVideo = call.hasVideo

        provider.reportNewIncomingCall(
            with: call.uuid,
            update: update
        ) { error in
            // Reconcile the server call and local state. Report failure or
            // end the call if the service cannot connect.
            _ = error
            completion()
        }
    }
}
```

The actual target also needs a complete `CXProviderDelegate` implementation and a server that binds the call UUID/token/account. A push token or payload is not identity, delivery, or an active call. If the product cannot show the system call UI, use UserNotifications for notification behavior instead.

## Recipe 7: fulfill CallKit actions after the service is ready

CallKit actions are commands from the system UI. Fulfill only after the app’s service has reached the matching state; fail or time out honestly.

```swift
import CallKit

final class CallProviderDelegate: NSObject, CXProviderDelegate {
    func providerDidReset(_ provider: CXProvider) {
        // Tear down media, clear transient calls, and reconnect the service.
    }

    func provider(
        _ provider: CXProvider,
        perform action: CXAnswerCallAction
    ) {
        Task {
            do {
                try await callService.answer(callID: action.callUUID)
                action.fulfill()
            } catch {
                action.fail()
            }
        }
    }

    func provider(
        _ provider: CXProvider,
        perform action: CXEndCallAction
    ) {
        Task {
            await callService.end(callID: action.callUUID)
            action.fulfill()
        }
    }

    private let callService = CallService()
}
```

Model `reported`, `ringing`, `answering`, `active`, `ending`, `ended`, and `failed`. Handle blocked handles, Focus, interruption, audio-session activation/deactivation, server timeout, remote hangup, duplicate UUID, and app termination. Do not keep a call in “active” because the system UI once appeared.

## Recipe 8: map LiveCommunicationKit conversation actions deliberately

Use a typed product boundary rather than sprinkling framework actions through views:

```swift
enum CommunicationAction {
    case startVoIP(recipient: String)
    case end(conversationID: UUID)
    case fallbackToSystem(recipient: String)
}

struct CommunicationPolicy {
    let supportsVoIP: Bool
    let allowsSystemFallback: Bool
    let requiresUserConfirmation: Bool
}

func routeCommunication(
    _ action: CommunicationAction,
    policy: CommunicationPolicy
) -> String {
    switch action {
    case .startVoIP where policy.supportsVoIP:
        return "LiveCommunicationKit ConversationManager action"
    case .fallbackToSystem where policy.allowsSystemFallback:
        return "documented system/cellular fallback"
    default:
        return "user-facing unavailable or confirmation state"
    }
}
```

The concrete `ConversationManager` action and entitlement signatures must be checked in the selected SDK. Verify default calling/dialer eligibility, regional/device requirements, user choice, recipient disclosure, conversation delegate resets/timeouts, and `AVAudioSession` activation/deactivation. LiveCommunicationKit coordinates the system; it does not supply a VoIP server or guarantee a call will connect.

## Recipe 9: evidence matrix for companion and communication routes

| Route | Development fixture | Required real evidence |
| --- | --- | --- |
| WatchConnectivity | Unit-test reducer and run both targets with fixtures | Physical paired iPhone/Watch, activation/deactivation, reachability, queued delay, duplicate/order, file transfer, storage, account switch. |
| CarPlay | CarPlay Simulator templates/scenes | Exact entitlement/category approval, real vehicle/aftermarket system, disconnect/reconnect, audio, locked phone, safe interaction. |
| App Clip | `_XCAppClipURL` local invocation | Physical QR/NFC/Code/website/Maps path as applicable, AASA/App Store Connect, slow network, no URL resume, full-app replacement. |
| CallKit/PushKit | Unit-test payload parser and mock provider | Signed physical device, APNs environment/token, server call state, incoming/outgoing/answer/end/failure, lock screen/Focus/audio. |
| LiveCommunicationKit | Compile against selected SDK and test typed policy | Actual OS/device/region/entitlement/default-role settings, system fallback, delegate/action timeout, audio, privacy disclosure. |

## Sources

- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [WCSession](https://developer.apple.com/documentation/watchconnectivity/wcsession)
- [WCSessionDelegate](https://developer.apple.com/documentation/watchconnectivity/wcsessiondelegate)
- [Transferring data with Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity/transferring-data-with-watch-connectivity)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [CPTemplateApplicationScene](https://developer.apple.com/documentation/carplay/cptemplateapplicationscene)
- [CPInterfaceController](https://developer.apple.com/documentation/carplay/cpinterfacecontroller)
- [Displaying content in CarPlay](https://developer.apple.com/documentation/carplay/displaying-content-in-carplay)
- [Using the CarPlay Simulator](https://developer.apple.com/documentation/carplay/using-the-carplay-simulator)
- [App Clips](https://developer.apple.com/documentation/appclip)
- [Responding to invocations](https://developer.apple.com/documentation/appclip/responding-to-invocations)
- [Configuring App Clip experiences](https://developer.apple.com/documentation/appclip/configuring-the-launch-experience-of-your-app-clip)
- [Testing the launch experience of your App Clip](https://developer.apple.com/documentation/appclip/testing-the-launch-experience-of-your-app-clip)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [CXCallController](https://developer.apple.com/documentation/callkit/cxcallcontroller)
- [Making and receiving VoIP calls](https://developer.apple.com/documentation/callkit/making-and-receiving-voip-calls)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [PKPushRegistry](https://developer.apple.com/documentation/pushkit/pkpushregistry)
- [Supporting PushKit Notifications](https://developer.apple.com/documentation/pushkit/supporting-pushkit-notifications-in-your-app)
- [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
- [PKPushTypeVoIP](https://developer.apple.com/documentation/pushkit/pkpushtype/voip)
- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [Initiating VoIP conversations with LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit/initiating-voip-conversations-with-livecommunicationkit)
- [Preparing your app to be the default dialer app](https://developer.apple.com/documentation/livecommunicationkit/preparing-your-app-to-be-the-default-dialer-app)
- [ConversationManagerDelegate](https://developer.apple.com/documentation/livecommunicationkit/conversationmanagerdelegate)
