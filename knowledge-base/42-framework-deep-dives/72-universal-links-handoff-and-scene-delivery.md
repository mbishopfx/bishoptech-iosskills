# Universal Links, Handoff, and scene delivery

## Scope

This page defines the route for external events that open or restore an iOS app:

- Universal Links from a website;
- custom URL schemes used only when a deliberate fallback is required;
- Handoff and other NSUserActivity restoration;
- SwiftUI URL/activity delivery and scene selection;
- UIKit UISceneConnectionOptions and scene-delegate delivery;
- cold launch, warm launch, suspension, termination, and multiple-window behavior;
- App Clip, widget, App Intent, document, notification, and web handoffs;
- privacy, authentication, accessibility, Liquid Glass, on-device AI, and proof.

The goal is one typed, validated app-owned route resolver. The system may deliver a
URL or activity, but the incoming value is only a request to interpret context. It
is not authorization, a database record, a payment result, or permission to
perform a destructive action.

## The route boundary

A system handoff has at least four layers:

    external event
      -> system association or scene delivery
      -> typed route parsing and validation
      -> current app/domain state and authorization
      -> app-owned navigation or explicit review
      -> durable effect only after normal validation

Keep these layers separate. A Universal Link can be associated with an installed
app and still refer to an expired item. An NSUserActivity can be well-formed and
still refer to a signed-out account. A scene can receive an event and still need
to present a login, conflict, consent, or recovery surface.

A useful route record contains:

| Field | Purpose |
| --- | --- |
| source | universalLink, customScheme, handoff, appClip, widget, appIntent, notification, document, or internal |
| rawValue | Redacted diagnostic representation; never log secrets by default |
| normalizedRoute | A typed enum or value object produced by the parser |
| accountScope | The account or privacy scope required to continue |
| sourceRevision | Optional server/local revision used for stale-route checks |
| arrival | coldLaunch, warmScene, resumedScene, or inApp |
| destination | App-owned navigation intent, not a view |
| state | received, validating, needsAuth, stale, ready, rejected, completed |

The route resolver should be deterministic and idempotent. Replaying the same
event after a scene reconnect must not duplicate a purchase, send a message, delete
content, join a match, or apply an AI proposal.

## Select the right external-event mechanism

| Product need | Primary mechanism | Important boundary |
| --- | --- | --- |
| Website link opens installed native content | Universal Links with applinks associated domain | AASA, entitlement, domain/path match, and route validation |
| Continue the same activity on another Apple device | NSUserActivity with Handoff eligibility | Same developer Team ID for cross-platform Handoff, small restorable payload, current activity lifecycle |
| Open a local app route from another app | Custom URL scheme | Collision and injection risk; Universal Links are preferred for web-addressable routes |
| Let SwiftUI receive a URL | onOpenURL or scene-level URL delivery | Use a shared parser; warm and cold delivery are distinct |
| Let SwiftUI receive a user activity | onContinueUserActivity | Activity type and payload are not domain authorization |
| Select a scene/window for an event | handlesExternalEvents on Scene/View | Matching rules use URL strings or NSUserActivity targetContentIdentifier/webpageURL |
| Open a widget/App Intent destination | Widget/App Intent-defined URL or intent | Treat extension output as a typed request; re-resolve in the main app |
| Hand an App Clip to the full app | App Clip invocation and shared route schema | Clip state is not full-app authorization or server truth |
| Open an imported document | File/document scene route | Security-scoped URL and provider lifetime must be honored |
| Open from a notification | Notification response plus scene connection options | Payload may be stale, redacted, or missing when the app is relaunched |

Do not use Universal Links as a replacement for in-process NavigationStack
navigation. Once a route is trusted and resolved, convert it into a domain-aware
navigation command.

## Associated Domains and the Apple App Site Association file

Universal Links, Handoff, App Clips, and shared web credentials use the
Associated Domains capability. Xcode writes the
com.apple.developer.associated-domains entitlement as an array of service-domain
strings. The service prefix matters:

    applinks:app.example.com
    activitycontinuation:app.example.com
    appclips:app.example.com
    webcredentials:app.example.com

Do not include path, query, or a trailing slash in the entitlement domain. Add
each subdomain that actually serves its own association file. A wildcard can be
appropriate for some services, but use the narrowest domain set the product needs.

The website must serve an Apple App Site Association file at:

    https://app.example.com/.well-known/apple-app-site-association

Apple’s documentation requires HTTPS and a valid certificate, and says the file
must be served without redirects. The installed app and website form a two-way
association: the entitlement names the domain and the website names the app/team
identifiers and allowed paths or components.

A minimal Universal Links-shaped file looks like this:

~~~json
{
  "applinks": {
    "details": [
      {
        "appIDs": ["TEAMID.com.example.app"],
        "components": [
          { "/": "/items/*" }
        ]
      }
    ]
  }
}
~~~

Treat this as a configuration sketch. Confirm the exact AASA schema, app
identifier, components, exclusions, and target bundle identifier in the selected
Apple documentation and Xcode environment. If the website has multiple domains,
test each host independently. Apple’s associated-domain delivery uses an
Apple-managed CDN on current systems, so a corrected file may not be observed
immediately by every device. Development alternate modes are for development
only and must be removed before App Store submission.

Configuration proof includes:

- the final entitlement in the intended target and archive;
- the website file at the correct path with valid JSON and content type;
- no redirect from the served association file;
- app identifier/team identifier agreement;
- exact allowed paths and excluded paths;
- public reachability or documented development alternate mode;
- a device installed after the association is available;
- a test link for an installed app and for an uninstalled app.

An Xcode capability checkbox is not association proof.

## Universal Link delivery

When a person activates a Universal Link, the system sends an NSUserActivity with
activityType equal to NSUserActivityTypeBrowsingWeb. The webpageURL contains the
HTTP or HTTPS URL. The current delivery method depends on the app lifecycle:

| App condition | Scene-oriented delivery to handle |
| --- | --- |
| App has no scene yet | UISceneDelegate connection options contain userActivities or URLContexts as appropriate |
| Existing scene is active/suspended | scene continuation/open-URL callbacks, or SwiftUI onContinueUserActivity/onOpenURL |
| Multiple scenes are available | SwiftUI scene/view matching and the app’s selected window policy decide the destination |
| User taps while Safari is already browsing the same domain | Safari may keep the person in Safari according to documented system intent rules |
| App is not installed | The website opens in the browser; the web route must still be useful |

Prefer scene APIs in a scene-based app. Older application-delegate continuation
callbacks remain useful when maintaining a UIKit architecture, but a new SwiftUI
target should make scene delivery and app-owned routing explicit.

Do not assume that every external link arrives through the same callback. Build a
single adapter that accepts:

- URL values from URL contexts and onOpenURL;
- NSUserActivity values from user-activity callbacks;
- scene connection options at cold launch;
- notification or App Intent requests that contain an equivalent typed route.

For a Universal Link, extract and validate webpageURL. Do not treat
userInfo as the source of truth for a Universal Link.

## Custom URL schemes

A custom scheme is useful for local app-to-app or legacy integrations that do not
have a website association. Apple’s current guidance strongly recommends
Universal Links for web-addressable deep linking.

Custom schemes have important risks:

- another app may register the same scheme;
- another app can construct a syntactically valid URL;
- URLs can be copied, logged, or displayed;
- query values can be malformed or unexpectedly large;
- an old app version may receive a route it no longer understands.

Register only a narrow scheme and route family. Validate scheme, host, path,
query names, lengths, encoding, and action policy. Never use a custom-scheme URL
as proof that a payment, login, purchase, deletion, or server mutation happened.
The route can request a review screen; the domain operation must still confirm
current state.

## Handoff and NSUserActivity

Use NSUserActivity to describe a meaningful activity that can be restored later.
Choose reverse-DNS activity types and declare the types in NSUserActivityTypes when
the activity must be received by Handoff or restoration.

An activity commonly contains:

- activityType;
- a human-readable title;
- a stable targetContentIdentifier or appEntityIdentifier when applicable;
- a webpageURL when the activity is tied to web content;
- a small userInfo payload or typed payload;
- isEligibleForHandoff, isEligibleForSearch, or other features only when policy allows;
- a version and stable entity identifier needed to restore state.

Make an activity current when the person begins a meaningful task, refresh it as
the state changes, and call resignCurrent or invalidate when it is no longer
relevant. Never leave a completed or private activity eligible for continuation.

The Handoff documentation recommends keeping userInfo small, under approximately
3 KB, and using continuation streams for a larger transfer. Prefer identifiers and
small state descriptors over embedding the full document or private media. On the
receiving device, fetch the current authorized record and handle a missing,
changed, or deleted record honestly.

Typed payloads can improve local safety:

~~~swift
struct ActivityPayload: Codable, Sendable {
    let schemaVersion: Int
    let recordID: UUID
    let mode: String
    let sourceRevision: Int?
}

let activity = NSUserActivity(activityType: "com.example.app.edit-record")
try activity.setTypedPayload(
    ActivityPayload(
        schemaVersion: 1,
        recordID: recordID,
        mode: "edit",
        sourceRevision: revision
    )
)
~~~

The exact typed-payload availability and overloads depend on the selected SDK.
Decode with typedPayload and reject encodingError or invalidContent. Even a
successful decode is only a transport result. Re-check account, permissions,
current revision, record existence, and allowed action before navigation or
mutation.

For cross-platform Handoff, the participating apps must use the same developer
Team ID. Test the actual signed apps on the intended devices; a local fixture or
same-process activity does not prove Handoff.

## SwiftUI scene delivery

SwiftUI provides several seams:

- onOpenURL handles URLs delivered to a view hierarchy;
- onContinueUserActivity handles a named NSUserActivity type;
- userActivity advertises an activity from a view;
- handlesExternalEvents(preferring:allowing:) tells an open scene which external
  events it can handle;
- handlesExternalEvents(matching:) helps the Scene choose a new instance when no
  existing scene handles the event;
- scenePhase reports scene activation changes but is not a delivery receipt.

A useful composition is:

    App
      -> WindowGroup or DocumentGroup
      -> root route coordinator
      -> onOpenURL / onContinueUserActivity
      -> shared IncomingEventAdapter
      -> typed resolver
      -> NavigationPath or sheet state

The view modifier should translate the incoming event into a coordinator action,
not parse business rules inside a leaf view. Keep the coordinator on the
MainActor only for UI projection. Parsing, validation, and remote reconciliation
can use an actor or service layer where appropriate.

When multiple scenes are supported, choose a matching strategy deliberately:

- use a stable targetContentIdentifier or URL prefix for a detail scene;
- keep conditions narrow and non-overlapping;
- provide at least one scene that can handle every claimed event;
- do not use a wildcard condition unless the product truly has one universal
  destination;
- distinguish opening a new scene from updating an existing scene;
- preserve per-scene selection in SceneStorage only for small non-sensitive UI state;
- keep canonical records in the app data model.

SwiftUI scene matching does not authorize a destination. It only helps choose where
the external event goes.

## UIKit scene connection options

UIKit passes UISceneConnectionOptions to the scene delegate when it creates a
scene. The object can contain:

- userActivities;
- URLContexts;
- handoffUserActivityType;
- shortcutItem;
- notificationResponse;
- cloudKitShareMetadata;
- sourceApplication;
- other context appropriate to the event.

At connection time, consume the set without assuming order. Normalize every item
into the shared route resolver, deduplicate by a stable event key, and store a
pending route if the domain model is not ready. When a connected scene receives a
new event, use the scene delegate’s URL or user-activity methods and feed the same
adapter.

Do not hold onto a UIContext or view controller from the connection callback as if
it were durable. The scene may disconnect. Store a typed pending route or domain
identifier and ask the current scene to render it when active.

A UIKit adapter should separate:

    UISceneDelegate callback
      -> IncomingExternalEvent
      -> route resolver
      -> coordinator/MainActor state
      -> view-controller or SwiftUI navigation

The app delegate can still configure scene sessions and support legacy callbacks,
but do not split routing policy between application(_:continue:), scene callbacks,
and SwiftUI modifiers. One resolver prevents cold/warm behavior from drifting.

## State restoration is not deep-link authorization

Use SceneStorage for small, per-scene UI state that can be recreated. Use a
durable model for records, drafts, account data, and edits. Use NSUserActivity for
the current activity or a restoration descriptor. Use a Universal Link or
notification route as an incoming request.

For example:

    scene UI selection
      -> SceneStorage
    current document identity
      -> NSUserActivity/typed payload
    document contents
      -> SwiftData/Core Data/CloudKit/File Provider
    incoming website link
      -> URL parser and authorized fetch

The operating system controls when scene storage is persisted and restored. It is
not a secret store, an account database, or a guaranteed transaction log. Do not
put authentication tokens, health data, private model prompts, or irreversible
actions in scene storage or a URL query.

## Handoffs from other Apple surfaces

Use one route schema across system entry points, but keep each source’s trust
boundary explicit.

| Source | Normalize | Re-check |
| --- | --- | --- |
| Widget deep link | URL or stable app record ID | Record still exists, account scope, current revision |
| App Intent | Typed AppEntity/AppIntent parameter | Intent authorization, current entity, mutation confirmation |
| App Clip | Invocation URL/activity | Clip/full-app context, installation state, server record |
| Notification | Notification response/userInfo | Notification freshness, account, notification action, privacy |
| Document provider | Security-scoped URL/document identity | Scope lifetime, file type, provider availability, conflict |
| Spotlight/Core Spotlight | NSUserActivity or indexed entity | Index staleness, stable ID, current authorization |
| Game Center activity | Service activity/match identity | Current player, game version, match state, invitation validity |
| SharePlay/Handoff | NSUserActivity or Group Activity context | Participant/account/session and current record |
| Website | Universal Link | Host/path/query allowlist, association, current account |

The source can suggest a destination; the app-owned domain state decides what is
actually available.

## On-device AI boundaries

An on-device model can help with low-risk route work:

- classify a user-provided request into a small set of route intents;
- suggest which visible record the person meant;
- summarize the destination or explain why it is stale;
- propose a search query or alternate route;
- generate localized, reviewable fallback copy.

Keep the route itself deterministic. The model must not:

- execute openURL without app policy;
- select an arbitrary host or path;
- bypass associated-domain validation;
- infer authorization from a URL or userInfo field;
- expose private Handoff data to a prompt;
- mutate data, accept a purchase, join a match, or send a message directly.

A safe proposal envelope includes model route, source event ID, visible input
scope, candidate destination, source revision, generated-at, and review state.
The resolver validates the candidate against the allowlist and current domain
state. Only a normal app-owned action commits the result.

## Accessibility and privacy

External routing is an accessibility feature when it returns people to work without
forcing them through a generic home screen. It can also create an accessibility
failure if focus lands on a hidden destination or if the app announces a private
URL.

For every route:

- provide a descriptive destination title;
- restore VoiceOver focus to the meaningful content or status;
- announce loading, authentication, stale, and failure states;
- provide a visible back/cancel path;
- support Dynamic Type and long localized titles;
- do not rely on URL text, color, or animation to convey state;
- keep touch targets and keyboard/controller actions available;
- honor reduced motion and reduced transparency;
- redact URLs, IDs, prompts, and notification payloads in diagnostics;
- do not place sensitive content in public Handoff/search metadata;
- clear or invalidate activities when the account signs out or the record becomes
  private/deleted.

## Evidence levels

| Level | What it proves | What it does not prove |
| --- | --- | --- |
| Source | API/configuration contract | Target behavior |
| Parser unit test | URL/activity normalization and rejection | System association |
| SwiftUI/UI test | Navigation, focus, cold/warm fixture, duplicate handling | A real Universal Link or Handoff |
| Signed archive | Entitlement, Info.plist, target membership | AASA delivery or system invocation |
| Physical device | Association, Safari/app routing, scene delivery, accessibility | Every device/locale/release |
| Two-device Handoff | Activity continuation between the selected devices/accounts | Production reliability |
| TestFlight/release | Distribution artifact and configured domain | Unobserved future OS/service state |

Never report “deep linking works” without naming the event source, device, app
state, domain association, and observed destination.

## Sources

- [Allowing apps and websites to link to your content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content/)
- [Supporting universal links in your app](https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Configuring an associated domain](https://developer.apple.com/documentation/xcode/configuring-an-associated-domain)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Defining a custom URL scheme for your app](https://developer.apple.com/documentation/xcode/defining-a-custom-url-scheme-for-your-app)
- [NSUserActivity](https://developer.apple.com/documentation/foundation/nsuseractivity)
- [Implementing Handoff in Your App](https://developer.apple.com/documentation/foundation/implementing-handoff-in-your-app)
- [Continuing User Activities with Handoff](https://developer.apple.com/documentation/foundation/continuing-user-activities-with-handoff)
- [Restoring your app’s state with SwiftUI](https://developer.apple.com/documentation/swiftui/restoring-your-app-s-state-with-swiftui)
- [openURL](https://developer.apple.com/documentation/swiftui/environmentvalues/openurl)
- [Input and event modifiers](https://developer.apple.com/documentation/swiftui/view-input-and-events)
- [handlesExternalEvents(matching:)](https://developer.apple.com/documentation/swiftui/scene/handlesexternalevents%28matching%3A%29)
- [UIScene](https://developer.apple.com/documentation/uikit/uiscene)
- [UISceneDelegate](https://developer.apple.com/documentation/uikit/uiscenedelegate)
- [UISceneConnectionOptions](https://developer.apple.com/documentation/uikit/uiscene/connectionoptions)
- [UIOpenURLContext](https://developer.apple.com/documentation/uikit/uiopenurlcontext)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [App Clips](https://developer.apple.com/documentation/appclip)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Debugging universal links](https://developer.apple.com/documentation/technotes/tn3155-debugging-universal-links)
