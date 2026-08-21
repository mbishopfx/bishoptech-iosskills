# Universal Links, Handoff, and scene-delivery recipes

These are compile-oriented route sketches for a named iOS target. They are not
compiled in this documentation workspace and do not prove AASA delivery,
associated-domain entitlement signing, Universal Link routing, Handoff between
devices, scene selection, accessibility task completion, or release readiness.
Confirm imports, deployment target, exact SwiftUI/UIKit signatures, target
membership, Info.plist, entitlements, and current Xcode diagnostics before copying
a recipe.

## Recipe 1: typed URL route

Start with a domain enum that cannot represent an arbitrary host or action:

~~~swift
enum AppRoute: Hashable, Sendable {
    case record(UUID)
    case search(String)
    case unsupported
}

enum RouteSource: Sendable {
    case universalLink
    case customScheme
}

struct URLRouteParser: Sendable {
    let universalHosts: Set<String>
    let customScheme: String

    func route(for url: URL, source: RouteSource) -> AppRoute {
        guard let components = URLComponents(
            url: url,
            resolvingAgainstBaseURL: false
        ) else {
            return .unsupported
        }

        let scheme = components.scheme?.lowercased()
        let host = components.host?.lowercased()

        switch source {
        case .universalLink:
            guard scheme == "https",
                  host.map(universalHosts.contains) == true,
                  components.port == nil else {
                return .unsupported
            }
        case .customScheme:
            guard scheme == customScheme,
                  host == "open" else {
                return .unsupported
            }
        }

        guard components.queryItems?.count ?? 0 <= 8 else {
            return .unsupported
        }

        switch components.percentEncodedPath {
        case "/items":
            guard let rawID = components.queryItems?
                .first(where: { $0.name == "id" })?.value,
                let id = UUID(uuidString: rawID) else {
                return .unsupported
            }
            return .record(id)
        case "/search":
            guard let query = components.queryItems?
                .first(where: { $0.name == "q" })?.value,
                query.count <= 256,
                !query.isEmpty else {
                return .unsupported
            }
            return .search(query)
        default:
            return .unsupported
        }
    }
}
~~~

The target should reject duplicate keys, unexpected keys, fragments, userinfo,
ports, overlong strings, malformed percent encodings, and path variants that the
product did not explicitly support. Add those cases to the test matrix rather
than assuming URLComponents alone defines the policy.

## Recipe 2: normalize Universal Link and custom URL events

Use an adapter that names the source. Do not let the parser guess whether a URL
came from a trusted associated domain.

~~~swift
struct ExternalURLAdapter: Sendable {
    let parser: URLRouteParser

    func event(
        from url: URL,
        source: RouteSource,
        arrival: ArrivalContext
    ) -> IncomingExternalEvent? {
        let route = parser.route(for: url, source: source)
        guard route != .unsupported else { return nil }

        return IncomingExternalEvent(
            id: UUID(),
            source: source == .universalLink ? .universalLink : .customScheme,
            route: route,
            arrival: arrival,
            receivedAt: .now
        )
    }
}
~~~

The UUID above is an in-process event identifier. For durable deduplication, use
a stable source event ID or a normalized route plus source revision. A random ID
should not be used to make retries idempotent across process launches.

## Recipe 3: SwiftUI URL and activity handlers

Attach handlers near a stable root:

~~~swift
struct RootSurface: View {
    @Environment(RouteCoordinator.self) private var routes

    var body: some View {
        NavigationStack(path: routes.pathBinding) {
            HomeView()
        }
        .onOpenURL { url in
            routes.receive(
                adapter.event(
                    from: url,
                    source: .customScheme,
                    arrival: .warmScene
                )
            )
        }
        .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { activity in
            routes.receive(
                adapter.event(
                    from: activity,
                    source: .universalLink,
                    arrival: .warmScene
                )
            )
        }
    }
}
~~~

The exact observation injection and binding syntax depends on the target’s
Observation architecture. A Universal Link commonly arrives as a browsing-web
NSUserActivity; a custom URL route commonly arrives through onOpenURL. Keep both
adapters because their trust and payload shapes differ.

Convert NSUserActivity to a URL only when the activity type is
NSUserActivityTypeBrowsingWeb and webpageURL exists. For custom activities, decode
the typed payload or versioned userInfo instead of inventing a URL.

## Recipe 4: create a typed Handoff activity

~~~swift
struct EditActivityPayload: Codable, Sendable {
    let schemaVersion: Int
    let recordID: UUID
    let revision: Int
}

func makeEditActivity(recordID: UUID, revision: Int) throws -> NSUserActivity {
    let activity = NSUserActivity(activityType: "com.example.app.edit-record")
    activity.title = "Edit record"
    activity.targetContentIdentifier = recordID.uuidString
    activity.isEligibleForHandoff = true
    activity.requiredUserInfoKeys = ["schemaVersion", "recordID", "revision"]
    try activity.setTypedPayload(
        EditActivityPayload(
            schemaVersion: 1,
            recordID: recordID,
            revision: revision
        )
    )
    return activity
}
~~~

Set the activity as current only while the person is actually in the edit task.
Call resignCurrent or invalidate after save, cancel, sign-out, or record deletion.
Keep the payload small and use a current record fetch on the receiver.

A SwiftUI view can advertise an activity with the userActivity modifier:

~~~swift
EditView(record: record)
    .userActivity("com.example.app.edit-record", element: record) { record, activity in
        activity.title = "Edit " + record.title
        activity.targetContentIdentifier = record.id.uuidString
        activity.isEligibleForHandoff = true
        try? activity.setTypedPayload(
            EditActivityPayload(
                schemaVersion: 1,
                recordID: record.id,
                revision: record.revision
            )
        )
    }
~~~

The exact generic element constraints and typed-payload API must be compiled
against the selected SDK. Do not place private record content in title, keywords,
or public search metadata unless the product’s privacy policy allows it.

## Recipe 5: receive a custom activity in SwiftUI

~~~swift
struct RootSurface: View {
    @State private var selectedRecord: UUID?

    var body: some View {
        DetailOrHome(selection: selectedRecord)
            .onContinueUserActivity("com.example.app.edit-record") { activity in
                do {
                    let payload = try activity.typedPayload(EditActivityPayload.self)
                    Task { @MainActor in
                        selectedRecord = payload.recordID
                        // Fetch and validate current revision before editing.
                    }
                } catch {
                    // Show an honest unsupported/stale activity state.
                }
            }
    }
}
~~~

Do not treat a decoded payload as permission. Resolve the record using the
current account, authorization, revision, and privacy policy. If the activity
came from another platform, confirm the signed apps share the intended Team ID.

## Recipe 6: route cold-launch scene connection options

UIKit scene code should capture every relevant input before the root UI is ready:

~~~swift
final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?
    private var pendingEvents: [IncomingExternalEvent] = []

    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {
        for activity in connectionOptions.userActivities {
            if let event = adapter.event(
                from: activity,
                arrival: .coldLaunch
            ) {
                pendingEvents.append(event)
            }
        }

        for context in connectionOptions.urlContexts {
            if let event = adapter.event(
                from: context.url,
                arrival: .coldLaunch
            ) {
                pendingEvents.append(event)
            }
        }

        // Create the window/root coordinator, then drain pendingEvents once.
    }
}
~~~

The concrete SwiftUI App lifecycle may not expose a SceneDelegate in the same
shape. If using SwiftUI scenes, attach root handlers and keep a shared
coordinator; if using UIKit scenes, normalize connectionOptions and later scene
callbacks through the same adapter. Do not implement two competing route policies.

## Recipe 7: handle active UIKit scene events

~~~swift
final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    func scene(_ scene: UIScene, openURLContexts URLContexts: Set<UIOpenURLContext>) {
        for context in URLContexts {
            coordinator.receive(
                adapter.event(
                    from: context.url,
                    arrival: .warmScene
                )
            )
        }
    }

    func scene(_ scene: UIScene, continue userActivity: NSUserActivity) {
        coordinator.receive(
            adapter.event(
                from: userActivity,
                arrival: .warmScene
            )
        )
    }
}
~~~

UIKit calls these methods for the scene that handles the event. Do not force a
view-controller reference into a global singleton. The coordinator can hold a
pending typed route until the scene becomes active and can project it into
navigation.

## Recipe 8: choose a SwiftUI scene for an external event

~~~swift
@main
struct ExampleApp: App {
    var body: some Scene {
        WindowGroup {
            BrowserRoot()
        }

        WindowGroup("Record") {
            RecordRoot()
        }
        .handlesExternalEvents(
            matching: ["https://app.example.com/items/"]
        )
    }
}
~~~

At the view level, a scene can prefer or allow events:

~~~swift
RecordRoot()
    .handlesExternalEvents(
        preferring: ["https://app.example.com/items/"],
        allowing: ["https://app.example.com/items/"]
    )
~~~

SwiftUI compares strings from the incoming URL or, for an NSUserActivity, from
targetContentIdentifier or webpageURL. Match narrowly. Every matched scene must
actually register the handler that consumes the event.

## Recipe 9: provide an outgoing URL action

Use the openURL environment for a user-initiated external link:

~~~swift
struct HelpButton: View {
    @Environment(\.openURL) private var openURL

    var body: some View {
        Button("Open help") {
            guard let url = URL(string: "https://support.example.com/help") else {
                return
            }
            openURL(url) { accepted in
                // Accepted means the system accepted the request to open;
                // it is not proof that the destination loaded.
                logger.notice("openURL accepted: \(accepted)")
            }
        }
    }
}
~~~

If the URL is a Universal Link to the same app, do not use openURL as an
in-process navigation shortcut. Apple documents that an app opening its own
Universal Link may open the website instead. Update app-owned navigation directly
for internal routes and use openURL for an intentional external handoff.

## Recipe 10: AASA and entitlement fixtures

A development fixture for a website can look like:

~~~json
{
  "applinks": {
    "details": [
      {
        "appIDs": ["TEAMID.com.example.app"],
        "components": [
          { "/": "/items/*" },
          { "/": "/search/*", "?": { "q": "*" } },
          { "/": "/private/*", "exclude": true }
        ]
      }
    ]
  }
}
~~~

A target entitlement fixture can look like:

~~~xml
<key>com.apple.developer.associated-domains</key>
<array>
    <string>applinks:app.example.com</string>
    <string>activitycontinuation:app.example.com</string>
</array>
~~~

Confirm the current AASA components syntax, application identifier fields,
exclusions, and domain service entries against Apple’s current documentation.
Use an actual public/reachable domain test for physical proof. A local JSON file
or unit test only proves that the fixture is syntactically valid.

## Recipe 11: validate an AI route proposal

~~~swift
struct RouteProposal: Sendable {
    let eventID: UUID
    let candidate: IncomingRoute
    let sourceRevision: Int?
    let modelRoute: String
    let visibleInputScope: String
}

func approve(
    _ proposal: RouteProposal,
    currentRevision: Int?,
    userApproved: Bool
) -> IncomingRoute? {
    guard userApproved,
          proposal.sourceRevision == currentRevision,
          proposal.modelRoute == "on-device-visible-context" else {
        return nil
    }

    switch proposal.candidate {
    case .record, .search:
        return proposal.candidate
    case .unsupported:
        return nil
    }
}
~~~

The real resolver must also check account, authorization, record existence, host
and path allowlists, revision, action policy, and idempotency. The model does not
own openURL, NavigationPath, a database mutation, or a system service call.

## Recipe 12: parser and delivery tests

Use pure tests for:

~~~swift
struct RouteFixtures {
    static let validUniversal = URL(
        string: "https://app.example.com/items?id=00000000-0000-0000-0000-000000000001"
    )!
    static let wrongHost = URL(string: "https://evil.example/items?id=1")!
    static let custom = URL(string: "myapp://open/items?id=00000000-0000-0000-0000-000000000001")!
}
~~~

Cover:

- valid/invalid scheme, host, port, path, query, encoding, fragment, and length;
- duplicate and unexpected query items;
- valid/current/stale/private/deleted activity payloads;
- duplicate delivery across cold and warm seams;
- scene matching with existing/new windows;
- account change while a route is resolving;
- offline/cache/browser fallback;
- model proposal with stale revision or unsupported candidate;
- VoiceOver focus and Dynamic Type on arrival.

Use UI tests and device runs to prove the system event itself. A call to a parser
with a URL fixture is not a Universal Link test.

## Recipe 13: route coordinator state

A small state machine keeps arrival UI honest:

~~~swift
enum ArrivalState: Equatable {
    case idle
    case received(IncomingExternalEvent)
    case validating(IncomingExternalEvent)
    case needsAuthentication
    case stale
    case ready(ResolvedDestination)
    case rejected(String)
    case completed
}
~~~

Render the state with standard SwiftUI navigation and controls. If using Liquid
Glass, apply it only to a compact functional control group. Keep raw URLs,
tokens, activity dictionaries, and model prompts out of the view state.

## Recipe 14: release handoff checklist

Before calling the route ready:

- compile the selected target and extensions against the selected SDK;
- inspect Release/TestFlight entitlements and Info.plist;
- fetch each public AASA file and record redirect/certificate results;
- test installed and uninstalled Universal Link behavior;
- test Safari same-domain and external-source behavior;
- test custom scheme from a known source and reject malformed input;
- test cold, warm, suspended, terminated, and multi-window delivery;
- test Handoff with signed apps, same Team ID, same Apple ID, and physical devices;
- test auth, stale, deleted, offline, wrong-account, and unsupported-version states;
- test VoiceOver, Dynamic Type, alternate input, reduced effects, and RTL;
- run release/testflight route tests separately from Debug;
- record what the evidence proves and what remains unverified.

## Sources

- [Allowing apps and websites to link to your content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content/)
- [Supporting universal links in your app](https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Configuring an associated domain](https://developer.apple.com/documentation/xcode/configuring-an-associated-domain)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Defining a custom URL scheme for your app](https://developer.apple.com/documentation/xcode/defining-a-custom-url-scheme-for-your-app)
- [NSUserActivity](https://developer.apple.com/documentation/foundation/nsuseractivity)
- [Implementing Handoff in Your App](https://developer.apple.com/documentation/foundation/implementing-handoff-in-your-app)
- [Restoring your app’s state with SwiftUI](https://developer.apple.com/documentation/swiftui/restoring-your-app-s-state-with-swiftui)
- [Input and event modifiers](https://developer.apple.com/documentation/swiftui/view-input-and-events)
- [openURL](https://developer.apple.com/documentation/swiftui/environmentvalues/openurl)
- [handlesExternalEvents(matching:)](https://developer.apple.com/documentation/swiftui/scene/handlesexternalevents%28matching%3A%29)
- [UIScene](https://developer.apple.com/documentation/uikit/uiscene)
- [UISceneDelegate](https://developer.apple.com/documentation/uikit/uiscenedelegate)
- [UISceneConnectionOptions](https://developer.apple.com/documentation/uikit/uiscene/connectionoptions)
- [UIOpenURLContext](https://developer.apple.com/documentation/uikit/uiopenurlcontext)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
