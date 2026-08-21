# Universal Links, Handoff, and scene-routing capability route

## Capability contract

Use this route when a feature must open a specific app destination from a website,
another Apple device, a widget, an App Intent, an App Clip, a document, a
notification, or another app.

The route should produce:

1. a domain/entitlement and AASA configuration;
2. one shared IncomingExternalEvent model;
3. deterministic URL and NSUserActivity parsers;
4. a MainActor route coordinator that owns navigation projection;
5. domain revalidation and authentication gates;
6. cold/warm/multi-scene handoff behavior;
7. accessible Liquid Glass arrival/review surfaces;
8. optional on-device AI proposals with deterministic validation;
9. parser, UI, physical-device, two-device, and release evidence.

Do not start with a NavigationPath. Start with the event contract and trust policy.

## Choose the entry path

| Entry need | Use | Use a different route when |
| --- | --- | --- |
| Public web content should open in the app | Universal Links | The product has no controlling HTTPS website/association |
| Cross-device task continuation | NSUserActivity/Handoff | The app only needs a one-time navigation URL |
| Legacy app-to-app trigger | Custom URL scheme | The route can be a normal web URL |
| Widget or App Intent action | App Intent parameter or validated deep link | The operation is a high-consequence mutation that needs confirmation |
| App Clip to full app | App Clip invocation and shared route enum | The full app needs to trust Clip-local state without server verification |
| Document provider import | File/document scene route | The feature is only a record detail deep link |
| Notification tap | UNNotificationResponse and scene connection options | The action requires a remote service call before the destination exists |

Prefer one canonical route shape, then adapt each source into it.

## Canonical event model

A route model should be small, Sendable, and safe to log after redaction:

~~~swift
enum IncomingSource: String, Sendable {
    case universalLink
    case customScheme
    case handoff
    case widget
    case appIntent
    case appClip
    case notification
    case document
}

enum IncomingRoute: Hashable, Sendable {
    case record(id: UUID, mode: RecordMode, sourceRevision: Int?)
    case collection(id: UUID?)
    case search(query: String)
    case actionReview(kind: ActionKind, recordID: UUID)
    case unsupported(reason: RouteRejection)
}

struct IncomingExternalEvent: Hashable, Sendable {
    let id: UUID
    let source: IncomingSource
    let route: IncomingRoute
    let arrival: ArrivalContext
    let receivedAt: Date
}
~~~

Use stable domain identifiers, not view names. Avoid putting arbitrary URLs,
access tokens, or full userInfo dictionaries into the canonical route.

## Configure the website and target

1. Add Associated Domains to the intended app target.
2. Add only required service-domain entries:
   applinks for Universal Links,
   activitycontinuation for Handoff,
   appclips for App Clip association,
   webcredentials only for shared web credentials.
3. Serve the AASA file from the website’s .well-known path using HTTPS and no
   redirects.
4. Put the correct Team ID/bundle identifier and allowed paths/components in the
   file.
5. Include NSUserActivityTypes in Info.plist for custom Handoff activities.
6. Add custom URL schemes only for a deliberate legacy/local integration.
7. Inspect the signed entitlements and final Info.plist in the archive.
8. Test every host/subdomain separately.
9. Remove development alternate-mode query parameters before distribution.
10. Keep the website fallback route useful when the app is absent.

The system checks association state on its own schedule. A recently changed AASA
file may not appear on every installed device immediately. Record when the file
was published, which device installed the build, and which link was tested.

## Parse URLs before navigation

Parse with URLComponents and an allowlist:

~~~swift
struct RouteParser: Sendable {
    let allowedHosts: Set<String> = ["app.example.com", "www.example.com"]

    func parse(_ url: URL, source: IncomingSource) -> IncomingRoute {
        guard let scheme = url.scheme?.lowercased() else {
            return .unsupported(reason: .missingScheme)
        }

        let isUniversal = source == .universalLink
            && scheme == "https"
            && allowedHosts.contains(url.host?.lowercased() ?? "")
        let isCustom = source == .customScheme
            && scheme == "myapp"
            && url.host == "open"

        guard isUniversal || isCustom else {
            return .unsupported(reason: .untrustedOrigin)
        }

        guard url.port == nil,
              let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              components.queryItems?.count ?? 0 <= 8 else {
            return .unsupported(reason: .malformed)
        }

        let path = components.percentEncodedPath
        let query = Dictionary(
            uniqueKeysWithValues: (components.queryItems ?? []).compactMap {
                guard let value = $0.value, value.utf8.count <= 256 else { return nil }
                return ($0.name, value)
            }
        )

        switch path {
        case "/items":
            guard let rawID = query["id"], let id = UUID(uuidString: rawID) else {
                return .unsupported(reason: .missingIdentifier)
            }
            return .record(id: id, mode: .view, sourceRevision: nil)
        default:
            return .unsupported(reason: .unsupportedPath)
        }
    }
}
~~~

This is a route sketch. In a real target, reject duplicate query keys where the
policy requires one value, reject unexpected fragments, cap the whole URL length,
normalize percent encoding once, and use a parser test matrix. Do not use a model
to decide whether an arbitrary host or path is trusted.

## Resolve against current domain state

Parsing is local and cheap. Resolution can require the account, database, network,
or a system service:

    parsed route
      -> account/session check
      -> record lookup
      -> authorization check
      -> source-revision/freshness check
      -> stale/needs-auth/ready
      -> app-owned destination

A resolver should return a typed result:

~~~swift
enum RouteResolution: Sendable {
    case ready(ResolvedDestination)
    case needsAuthentication(context: AuthContext)
    case stale(recordID: UUID, fallback: StaleFallback)
    case unavailable(reason: UnavailableRouteReason)
    case rejected(RouteRejection)
}
~~~

Never make a URL parser perform a mutation. For a route such as
myapp://open/delete?id=..., the parser should return a review or rejection, not
delete. The normal command layer must still check current authorization, revision,
confirmation, idempotency, and server/domain response.

## Deliver cold and warm events through one adapter

The adapters are lifecycle-specific; the route policy is not:

| Lifecycle seam | Adapter input |
| --- | --- |
| SwiftUI URL | onOpenURL URL |
| SwiftUI activity | onContinueUserActivity NSUserActivity |
| SwiftUI scene selection | handlesExternalEvents matching/preferring |
| UIKit cold scene | UISceneConnectionOptions.URLContexts/userActivities |
| UIKit active scene | scene openURLContexts/continue userActivity |
| App Clip/widget/notification | source-specific URL/activity/response normalized to event |
| Internal navigation | already-typed IncomingRoute |

For a cold scene, hold a pending IncomingExternalEvent until the model container,
account session, and root coordinator are ready. For a warm scene, enqueue it on
the MainActor and deduplicate against the currently displayed route.

The adapter should capture arrival context:

~~~swift
enum ArrivalContext: String, Sendable {
    case coldLaunch
    case newScene
    case warmScene
    case resumedScene
    case inApp
}
~~~

Do not assume a scene remains connected after receiving the event. Persist only a
safe pending identifier or route record when recovery across termination is needed.

## Handoff activity route

For a custom activity:

1. Pick a reverse-DNS activity type.
2. Declare it in NSUserActivityTypes.
3. Create a small NSUserActivity.
4. Add a title and stable target content identifier.
5. Put a compact typed payload or minimal userInfo in the activity.
6. Set isEligibleForHandoff only when the task is genuinely continuable.
7. Call becomeCurrent while active.
8. Update the activity when the task changes.
9. Call resignCurrent or invalidate when the task ends or becomes private.
10. On another device, decode and resolve against current authorized data.
11. Handle a missing, deleted, newer, or incompatible record.
12. Test the same Team ID, signed apps, Apple ID/Handoff settings, and physical devices.

Keep Handoff payloads small. A stable ID and revision can be better than copying a
document. If the product must transfer a larger file, use the documented file or
continuation route and prove its security scope and lifecycle separately.

## SwiftUI integration

A root coordinator owns the route state:

~~~swift
@MainActor
final class RouteCoordinator: ObservableObject {
    @Published private(set) var pending: IncomingExternalEvent?
    @Published var path = NavigationPath()
    @Published var sheet: ArrivalSheet?

    func receive(_ event: IncomingExternalEvent) {
        pending = event
        Task { await resolve(event) }
    }

    private func resolve(_ event: IncomingExternalEvent) async {
        // Resolve account, record, authorization, and revision.
        // Update published UI state on the MainActor.
    }
}
~~~

The exact observation architecture may use Observation instead of
ObservableObject in the target. The invariant is that callbacks are converted into
one coordinator command and navigation is a projection of route resolution.

A SwiftUI App can attach handlers close to the root:

~~~swift
@main
struct ExampleApp: App {
    @State private var routes = RouteCoordinator()

    var body: some Scene {
        WindowGroup {
            RootView()
                .onOpenURL { url in
                    routes.receive(adapter.event(from: url, source: .customScheme))
                }
                .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { activity in
                    routes.receive(adapter.event(from: activity, source: .universalLink))
                }
        }
        .handlesExternalEvents(matching: ["https://app.example.com/items"])
    }
}
~~~

The exact ownership syntax and Observation annotations depend on the selected
deployment target. Keep URL/activity handling attached to a stable root or scene
rather than a detail view that may not exist at cold launch.

## View and scene matching

Use handlesExternalEvents(preferring:allowing:) on a view when an already-open
scene should express which external events it handles. Use
handlesExternalEvents(matching:) on a Scene to help SwiftUI create a new scene
when no open scene matches.

Match on stable prefixes or identifiers:

    https://app.example.com/items/
    record=
    com.example.app.edit-record

Avoid matching on untrusted free-form text. Do not use an empty set or assume an
empty string matches. Treat a wildcard as a deliberate catch-all with a proof
case for every source event.

## Surface and AI handoff

The app-owned arrival surface should show:

- the destination title;
- whether the record is current, cached, or needs verification;
- the account or workspace;
- the next action and a cancel/back route;
- a system/browser fallback when the app cannot continue.

Use Liquid Glass only around functional actions. Keep the content itself stable and
readable. The model can propose a destination or explanation from visible,
user-authorized input, but it cannot choose an arbitrary URL or call the navigation
or mutation layer directly.

A proposal must be tied to the event and source revision:

~~~swift
struct RouteProposal: Sendable {
    let eventID: UUID
    let candidate: IncomingRoute
    let sourceRevision: Int?
    let modelRoute: String
    let reviewRequired: Bool
}
~~~

Validate the candidate using the same parser/resolver as a manually chosen route.
If the source changed while inference ran, reject the stale proposal and ask for a
fresh route.

## Fallback and failure policy

Implement named fallbacks:

- app not installed: website route;
- association unavailable: open the website or show a supported-link error;
- signed out: authenticate without revealing private content;
- stale: search/refresh/reopen browser;
- offline with safe cache: show cached timestamp and read-only policy;
- offline without cache: explain and retry;
- unsupported app version: update or browser;
- wrong account: switch only through an explicit account flow;
- duplicate event: focus existing destination;
- invalid payload: reject and log only redacted diagnostics.

A fallback is a different state, not a hidden success. Keep the original route
available for retry when it is safe.

## Capability handoff checklist

- [ ] Source type and trust boundary documented.
- [ ] Associated domains and AASA are configured per target/domain.
- [ ] Universal Link host/path/query allowlists exist.
- [ ] Custom schemes are narrow and validated.
- [ ] NSUserActivityTypes and activity identifiers are versioned.
- [ ] Handoff payload is small and contains no secret.
- [ ] Cold/warm/resumed/new-scene adapters use one resolver.
- [ ] Multi-window destination policy is explicit.
- [ ] Auth/stale/offline/unsupported/duplicate states are designed.
- [ ] Liquid Glass is limited to functional app-owned controls.
- [ ] AI proposals are reviewable and revision-bound.
- [ ] VoiceOver, Dynamic Type, Reduce Motion, and alternate input are tested.
- [ ] Physical association, Handoff, signed entitlements, and release artifact are
      separately recorded.

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
- [handlesExternalEvents(matching:)](https://developer.apple.com/documentation/swiftui/scene/handlesexternalevents%28matching%3A%29)
- [UIScene](https://developer.apple.com/documentation/uikit/uiscene)
- [UISceneDelegate](https://developer.apple.com/documentation/uikit/uiscenedelegate)
- [UISceneConnectionOptions](https://developer.apple.com/documentation/uikit/uiscene/connectionoptions)
- [UIOpenURLContext](https://developer.apple.com/documentation/uikit/uiopenurlcontext)
- [App Clips](https://developer.apple.com/documentation/appclip)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
