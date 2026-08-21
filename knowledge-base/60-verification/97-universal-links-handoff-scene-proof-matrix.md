# Universal Links, Handoff, and scene-delivery proof matrix

## Purpose

Use this matrix to distinguish a parsed external event from a working signed
association, a delivered scene event, a restored destination, and a safe durable
effect. Record the selected SDK/Xcode version, deployment target, bundle IDs,
Team ID, domains, AASA revision, target entitlements, app state, device model/OS,
Apple ID/account, source app, exact URL/activity, and observed result.

A green preview, a parser test, an installed debug app, and a physical Handoff are
different evidence levels.

## Evidence levels

| Level | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| L0 source | Official Apple/Swift documentation and target API ledger | Documented contract | This app’s configuration |
| L1 parser | Unit tests with valid/invalid URL/activity fixtures | Normalization, allowlists, typed payload rejection | Association, browser routing, scene lifecycle |
| L2 build | Xcode compile and archive inspection | Imports, target membership, Info.plist, entitlements, signing inputs | Website delivery, physical system invocation |
| L3 app UI | Preview/UI test/manual simulator run | Arrival screens, navigation, duplicate handling, focus, state fixtures | Real AASA, Handoff, Safari, device-to-device |
| L4 physical | Signed app on device with website/source app | System link delivery, cold/warm scene behavior, accessibility task | Every device, browser, locale, release |
| L5 two-device | Handoff between intended Apple devices/accounts | Activity continuation and restore path | Universal production reliability |
| L6 distribution | TestFlight/release artifact and public domain | Distribution config, final association, release route | Unobserved future system state |

## Configuration and association

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| CFG-01 | Correct target owns Associated Domains | Build the app target and inspect signed entitlements | Entitlements dump and target matrix | com.apple.developer.associated-domains contains only intended services/domains |
| CFG-02 | AASA file is reachable | Fetch each host’s .well-known file with HTTPS | Response headers/body, certificate, redirect trace | Valid HTTPS, no redirect, JSON decodes |
| CFG-03 | AASA app identity matches | Compare appIDs/team/bundle or current components identity with archive | Redacted app/team/build record | Website and signed target refer to same app |
| CFG-04 | Path/component policy is narrow | Test allowed, excluded, sibling, query, fragment, encoded, and case variants | Parser/AASA fixture table | Only intended routes enter the app |
| CFG-05 | Each subdomain is tested | Repeat for apex, www, app, and any wildcard policy | Per-host results | No domain relies on another host’s file |
| CFG-06 | Development mode is isolated | Use developer alternate mode only in development | Entitlement/config diff | Distribution artifact has no development query |
| CFG-07 | Association cache timing is recorded | Install after file publish and repeat after a correction | Device install/file timestamps | Test report names the association revision actually observed |
| CFG-08 | Handoff domain is configured | Test activitycontinuation domain and same Team ID apps | Signed entitlements and two-device record | The selected Handoff route uses the intended association |

## URL parser and security rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| URL-01 | HTTPS Universal Link origin is allowlisted | Valid host, wrong host, userinfo, port, http, custom scheme | Parser tests | Only intended scheme/host/port policy is accepted |
| URL-02 | Path policy is bounded | Allowed path, sibling path, traversal-like encoding, repeated slashes | Normalized path fixtures | No path escape or accidental route |
| URL-03 | Query policy is bounded | Missing, duplicate, unexpected, empty, overlong, malformed percent encoding | URLComponents/decoder tests | Required values parse once; bad values reject |
| URL-04 | IDs are opaque and typed | UUID/ULID valid, wrong length, Unicode, reserved word | ID parser tests | No display name or raw path is treated as identity |
| URL-05 | Fragments are handled | Expected/forbidden fragment variants | Fixture results | Fragment is either explicitly supported or rejected |
| URL-06 | Custom scheme is treated as untrusted | Another app/source or crafted URL fixture | Source policy trace | No custom URL alone authorizes a mutation |
| URL-07 | Redaction is effective | Logs, analytics, crash fixture, VoiceOver route | Redacted outputs | Tokens, private query values, and document content are absent |
| URL-08 | Duplicate delivery is idempotent | Same event cold plus warm, repeated tap | Event key/state trace | One navigation/effect, no duplicate mutation |

## User activity and typed payload rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| ACT-01 | Activity type is declared | Inspect Info.plist and create activity | Archive/plist record | Reverse-DNS type is declared and stable |
| ACT-02 | Activity lifecycle is correct | becomeCurrent, update, resignCurrent, invalidate | Activity lifecycle trace | Only relevant active tasks are exposed |
| ACT-03 | Payload is minimal | Serialize current/future/oversized payload | Size and schema fixture | Identifier/revision fit policy; sensitive document is not embedded |
| ACT-04 | Typed decode rejects corruption | Empty, wrong type, version, missing field | TypedPayloadError/decoder tests | Invalid content becomes a safe route failure |
| ACT-05 | Activity restores current data | Delete/change/private record after source activity | Device/domain trace | Receiver revalidates and does not trust stale payload |
| ACT-06 | Cross-device Handoff works | Signed apps, same Team ID, same Apple ID, two physical devices | Handoff banner/launch/restore recording | Destination restores the tested activity |
| ACT-07 | Large handoff is separate | Activity with a file/reference and security scope | Stream/file proof | No assumption that userInfo contains the document |
| ACT-08 | Failure is visible | Receiver offline, signed out, deleted, incompatible | UI state/diagnostic | Stale/error/re-auth copy is truthful and recoverable |

## Scene and SwiftUI rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| SCENE-01 | Cold URL/activity is captured | Terminate, trigger source, launch | connectionOptions and UI trace | No event is lost before root coordinator is ready |
| SCENE-02 | Warm URL is delivered | Active and suspended scene, source tap | onOpenURL/scene callback trace | Current scene receives one normalized event |
| SCENE-03 | Warm activity is delivered | Active/suspended Handoff or activity | onContinueUserActivity/scene trace | Activity type and payload reach the resolver |
| SCENE-04 | Multiple windows match intentionally | Existing windows plus event | Window creation/selection recording | Event reaches correct scene or documented new scene |
| SCENE-05 | Matching strings are narrow | matching/preferring/allowing fixtures | Scene policy table | No unrelated event is routed to a detail scene |
| SCENE-06 | Scene disconnect is recoverable | Disconnect/reconnect while event resolves | Pending route/checkpoint trace | No UI reference is assumed durable |
| SCENE-07 | State restoration is distinct | Stop/relaunch, restore per-scene selection | SceneStorage/activity/model trace | Sensitive/canonical data is not stored only in SceneStorage |
| SCENE-08 | UIKit bridge is consistent | SwiftUI root and UIKit scene delegate target | Adapter tests/trace | One resolver, not competing callback policies |

## Domain and action rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| DOM-01 | Authorization follows routing | Signed out, wrong account, revoked permission | Resolver/state trace | Route never leaks private content |
| DOM-02 | Freshness is checked | Source revision old/current/missing | Domain reconciliation trace | Stale route becomes refresh/read-only/rejection |
| DOM-03 | Consequential action is reviewed | Link to edit/delete/checkout/send/join | Review screen and command trace | Route does not bypass confirmation |
| DOM-04 | Commit is idempotent | Duplicate tap/relaunch/retry after timeout | Request ID/server/local trace | One durable effect |
| DOM-05 | Unavailable source has fallback | App missing, association unavailable, offline | Website/browser/error trace | Useful browser or local fallback exists |
| DOM-06 | App Clip/widget/intent handoffs converge | Same record from each source | Cross-source route trace | Source adapters share the same resolver |
| DOM-07 | AI suggestion is bounded | Ambiguous text, stale source, arbitrary host | Proposal and rejection trace | Model cannot bypass parser/authorization |
| DOM-08 | Route metrics are privacy-safe | Instrument arrival/failure | Redacted event schema | No URL token or private content in analytics |

## Accessibility rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| A11Y-01 | Arrival destination has correct focus | VoiceOver cold/warm arrival | Device recording/accessibility tree | Focus lands on useful heading/status/control |
| A11Y-02 | Progress/errors are announced | Verifying, auth, stale, offline, complete | Announcement trace | State change is available without vision |
| A11Y-03 | Large text/localization works | Largest Dynamic Type, long host/title, RTL | Device screenshots/UI test | No clipping or hidden action |
| A11Y-04 | Alternate input works | Voice Control, Switch Control, keyboard/pointer | Device route test | Open/retry/back/confirm are reachable |
| A11Y-05 | Reduced effects preserve meaning | Reduce Motion/transparency/increased contrast | Device settings run | State does not depend on glass/animation |
| A11Y-06 | Privacy survives assistive output | VoiceOver and lock-screen notification | Audio/visual review | Tokens/private query/content are not exposed |

## Release and system rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| REL-01 | Release entitlement is correct | Inspect Release/TestFlight archive | Exported entitlements | Intended associated domains only |
| REL-02 | Release Info.plist is correct | Inspect activity types, schemes, usage/privacy metadata | Archive plist | No staging host, debug route, or missing type |
| REL-03 | Release AASA is correct | Public domain and release bundle ID | Published file and archive | Production app is associated with production domain |
| REL-04 | Physical Universal Link works | Safari/Messages/Mail/Notes/source apps | Device recording and URL | Installed app opens intended route; uninstalled app opens web |
| REL-05 | Physical Handoff works | Mac/iPhone/iPad or intended pair | Two-device recording | Activity restores in the intended signed app |
| REL-06 | App Store/TestFlight route is proven | TestFlight build, update, reinstall, stale AASA | Release matrix | Distribution behavior matches the documented environment |
| REL-07 | Review copy is accurate | Link source, privacy, auth, stale, browser fallback | Copy/accessibility review | No false verified/secure/current claim |
| REL-08 | Support/recovery exists | Unsupported old app, deleted record, association delay | Runbook and UI | Person can recover without data loss |

## Recommended test matrix

Run at minimum:

- app installed and uninstalled;
- fresh install, update over an older route schema, and reinstall after AASA changes;
- Safari same-domain and different-domain taps;
- Messages, Mail, Notes, browser, and in-app WebKit sources where supported;
- custom URL scheme from a known and unknown source;
- cold launch, active scene, suspended scene, backgrounded process, and terminated
  process;
- iPhone single-window and iPad multi-window routes;
- Handoff with same Team ID signed apps and intended Apple ID;
- signed out, wrong account, revoked/deleted record, stale revision, offline, and
  server unavailable;
- duplicate link delivery, retry, and notification plus deep-link races;
- VoiceOver, Voice Control, Switch Control, keyboard/pointer, Dynamic Type, RTL,
  Reduce Motion, Reduce Transparency, and increased contrast;
- model unavailable, ambiguous proposal, stale proposal, rejected host/path, and
  user-approved proposal;
- Debug, Release, TestFlight, and final distribution artifact.

## Stop conditions

Stop and fix when:

- the app treats a valid URL parse as a verified association;
- a URL or activity directly deletes, purchases, sends, joins, or accepts without
  normal confirmation and current authorization;
- private data is shown before the account is checked;
- Universal Links and custom schemes use separate, drifting business routers;
- cold launch loses the event or pushes it twice;
- multi-window matching uses a broad wildcard accidentally;
- SceneStorage is the only copy of canonical or sensitive data;
- Handoff payload includes secrets or an unbounded document;
- a model chooses an arbitrary host/path or calls openURL as a side effect;
- simulator or UI-test output is reported as physical Universal Link/Handoff proof;
- a development alternate-mode entitlement reaches TestFlight/App Store;
- the website fallback is broken when the app is not installed.

## Sources

- [Allowing apps and websites to link to your content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content/)
- [Supporting universal links in your app](https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Debugging universal links](https://developer.apple.com/documentation/technotes/tn3155-debugging-universal-links)
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
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
