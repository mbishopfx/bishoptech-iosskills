# Collaboration, Discovery, and Preview Recipes

These are compile-oriented seams for Group Activities, nearby sessions, TipKit, Spotlight/Handoff, and Quick Look. They are route sketches, not claims that this documentation-only workspace compiles them. Confirm the selected SDK signatures, target membership, capabilities, `Info.plist` keys, entitlements, and platform availability before copying code.

## Recipe 1: start a typed SharePlay activity

Keep the activity payload small, `Codable`, versioned, and safe to share. The current Group Activities route requires the Group Activities capability on the app target.

```swift
import GroupActivities

struct SharedBoardActivity: GroupActivity {
    static let activityIdentifier = "com.example.board.activity"

    let schemaVersion: Int
    let boardID: String

    var metadata: GroupActivityMetadata {
        var value = GroupActivityMetadata()
        value.type = .generic
        value.title = "Shared board"
        value.subtitle = "Work on this board together"
        return value
    }
}

@MainActor
func start(_ activity: SharedBoardActivity) async -> Bool {
    switch await activity.prepareForActivation() {
    case .activationPreferred:
        do { return try await activity.activate() }
        catch { return false }
    case .activationDisabled, .cancelled:
        return false
    @unknown default:
        return false
    }
}
```

The exact activation result cases and metadata fields must be checked against the selected SDK. A `true` activation result means the system accepted the activity start; it does not mean every participant joined or that the board mutation was persisted.

## Recipe 2: join a session and separate messages from attachments

Use `GroupSessionMessenger` for small/time-sensitive messages and `GroupSessionJournal` for larger `Transferable` attachments. Keep listener tasks alive for the session and cancel them when it invalidates.

```swift
import GroupActivities

struct BoardEvent: Codable, Sendable {
    let schemaVersion: Int
    let eventID: UUID
    let boardID: String
    let sourceRevision: Int
    let operation: String
}

@MainActor
func observe(_ activity: SharedBoardActivity) -> Task<Void, Never> {
    Task {
        for await session in activity.sessions() {
            let messenger = GroupSessionMessenger(
                session: session,
                deliveryMode: .reliable
            )
            let messageTask = Task {
                for await (event, _) in messenger.messages(of: BoardEvent.self) {
                    await applyRemoteEvent(event)
                }
            }

            session.join()
            await session.$state.values.first { state in
                if case .invalidated = state { return true }
                return false
            }
            messageTask.cancel()
            // Drop the strong messenger/journal references for this session.
        }
    }
}
```

This sketch intentionally leaves `applyRemoteEvent` app-owned: it must check the activity ID, account, schema, source revision, authorization, and idempotency before mutating domain state. Confirm the current `GroupSession.State` observation and `AsyncSequence` signatures in Xcode; the state reducer and proof boundary matter more than copying a callback shape.

## Recipe 3: retain a legacy nearby adapter behind a protocol

Apple’s current `MCSession` documentation marks the Multipeer Connectivity session path deprecated and points new work toward Network Framework. If an existing product needs the browser/invitation UI, isolate it behind a transport protocol so it can be replaced.

```swift
import MultipeerConnectivity

final class LegacyNearbyTransport: NSObject {
    private let peer = MCPeerID(displayName: "Local peer")
    private lazy var session = MCSession(
        peer: peer,
        securityIdentity: nil,
        encryptionPreference: .required
    )
    private lazy var advertiser = MCNearbyServiceAdvertiser(
        peer: peer,
        discoveryInfo: ["protocol": "board-v1"],
        serviceType: "board-share"
    )

    func start() {
        // Set delegates, check local-network permission, then advertise/browse.
        advertiser.startAdvertisingPeer()
    }

    func stop() {
        advertiser.stopAdvertisingPeer()
        session.disconnect()
    }
}
```

Do not ship this as a complete transport without implementing the advertiser/browser/session delegates, invitation consent, protocol framing, authentication, reconnect, foreground/background behavior, and error mapping. Add `NSLocalNetworkUsageDescription` and the required `NSBonjourServices` entry, and verify the service-type constraints. For new designs, compare `NWBrowser`, `NWListener`, and `NWConnection` in Network Framework.

## Recipe 4: configure a contextual TipKit tip

Tips should explain a useful, non-obvious feature and remain optional. The app must work when the tip is hidden, dismissed, unavailable, or configured with an error.

```swift
import TipKit
import SwiftUI

struct BoardSearchTip: Tip {
    @Parameter
    static var hasOpenedSearch = false

    var title: Text {
        Text("Find boards faster")
    }

    var message: Text? {
        Text("Search your saved boards from the toolbar.")
    }

    var rules: [Rule] {
        #Rule(Self.$hasOpenedSearch) { hasOpenedSearch in
            hasOpenedSearch == false
        }
    }
}

struct SearchTipView: View {
    var body: some View {
        TipView(BoardSearchTip())
    }
}
```

Configure TipKit once at app launch with `try Tips.configure()`, handle the thrown error, and update the parameter from deterministic product state. Verify the current macro/property signatures and accessibility behavior in the selected SDK. Do not use a tip as a marketing banner or a mandatory tutorial.

## Recipe 5: index and restore a current activity

Keep the system projection minimal and re-resolve the record when the person selects it.

```swift
import CoreSpotlight
import Foundation

func indexBoard(id: String, title: String, summary: String) async throws {
    let attributes = CSSearchableItemAttributeSet(contentType: "public.text")
    attributes.title = title
    attributes.contentDescription = summary

    let item = CSSearchableItem(
        uniqueIdentifier: id,
        domainIdentifier: "boards",
        attributeSet: attributes
    )
    try await CSSearchableIndex.default()
        .indexSearchableItems([item])
}

func makeActivity(for boardID: String) -> NSUserActivity {
    let activity = NSUserActivity(activityType: "com.example.board.open")
    activity.title = "Open board"
    activity.targetContentIdentifier = boardID
    activity.isEligibleForHandoff = true
    activity.isEligibleForSearch = true
    return activity
}
```

The async `CSSearchableIndex` overload and `NSUserActivity` property availability should be verified against the selected SDK; use the documented completion-handler form where the target requires it. Declare `NSUserActivityTypes` in `Info.plist`, and only call `becomeCurrent()` while the activity is actually current. Index/delete operations need retry and deletion synchronization; Handoff receipt needs account, schema, authorization, and record-existence checks.

## Recipe 6: bridge Quick Look into SwiftUI

Use a small UIKit adapter for `QLPreviewController` and keep file access scoped to the preview lifecycle.

```swift
import QuickLook
import SwiftUI

struct PreviewItem: QLPreviewItem {
    let previewItemURL: URL?
    let previewItemTitle: String?
}

struct QuickLookPreview: UIViewControllerRepresentable {
    let item: PreviewItem

    func makeCoordinator() -> Coordinator {
        Coordinator(item: item)
    }

    func makeUIViewController(context: Context) -> QLPreviewController {
        let controller = QLPreviewController()
        controller.dataSource = context.coordinator
        return controller
    }

    func updateUIViewController(_ controller: QLPreviewController, context: Context) {
        context.coordinator.item = item
        controller.reloadData()
    }

    final class Coordinator: NSObject, QLPreviewControllerDataSource {
        var item: PreviewItem

        init(item: PreviewItem) { self.item = item }

        func numberOfPreviewItems(in controller: QLPreviewController) -> Int { 1 }

        func previewController(
            _ controller: QLPreviewController,
            previewItemAt index: Int
        ) -> QLPreviewItem { item }
    }
}
```

Before presenting, validate the URL’s security scope, content type, size, and account ownership. If Quick Look reports an edited copy, validate and import that new artifact through the domain’s normal review/save path. A preview or edit callback is not proof that a record was saved.

## Recipe evidence contract

| Route | Compile/fixture | Physical/system | Release/service |
| --- | --- | --- | --- |
| Group Activities | Codable message reducer, activation state, duplicate/out-of-order event tests | FaceTime/Messages/share sheet, two devices, join/leave/late join/invalidation | Group Activities capability, signed targets, supported platform/device matrix, privacy/review state |
| Nearby | Protocol reducer, invite/identity/reconnect tests | Two devices, local-network prompt, background disconnect, packet loss | Network/Bonjour configuration, authentication, supported transport, privacy strings |
| TipKit | Rule/parameter fixture and accessibility layout | Persistence, dismissal/reset, task completion, VoiceOver/Dynamic Type | Tip copy/localization and product discovery policy |
| Spotlight/Handoff | Index/delete/deep-link/revalidation tests | Actual Spotlight result and two-device Handoff | `Info.plist`, Team ID/signing, associated domain if used, privacy/index policy |
| Quick Look | URL/UTType/size/edit-copy validation | Real files, malformed files, editing, accessibility, extension termination | Preview extension/content-type declaration, signed target, supported device family |

## Sources

- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [GroupSessionMessenger](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionJournal](https://developer.apple.com/documentation/groupactivities/groupsessionjournal)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [MCSession](https://developer.apple.com/documentation/multipeerconnectivity/mcsession)
- [Network](https://developer.apple.com/documentation/network)
- [TipKit](https://developer.apple.com/documentation/tipkit)
- [Rule](https://developer.apple.com/documentation/tipkit/tips/rule)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [CSSearchableIndex](https://developer.apple.com/documentation/corespotlight/cssearchableindex)
- [NSUserActivity](https://developer.apple.com/documentation/foundation/nsuseractivity)
- [Implementing Handoff in your app](https://developer.apple.com/documentation/foundation/implementing-handoff-in-your-app)
- [Quick Look](https://developer.apple.com/documentation/quicklook)
- [QLPreviewController](https://developer.apple.com/documentation/quicklook/qlpreviewcontroller)
- [QLPreviewItem](https://developer.apple.com/documentation/quicklook/qlpreviewitem)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
