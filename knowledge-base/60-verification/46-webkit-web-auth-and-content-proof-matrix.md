# WebKit, web authentication, and content proof matrix

Web features cross system-managed browsing, embedded remote content, website data, JavaScript bridges, authentication callbacks, server association, universal links, accessibility, and AI input boundaries. Test each boundary separately.

This matrix does not treat a loaded webpage, a callback URL, an entitlement source file, a simulator tap, or a model summary as proof of identity, authorization, safe native mutation, physical-device dispatch, or release readiness.

## Test record

| Field | Record |
| --- | --- |
| Target | Bundle ID, app/extension targets, target membership, platform family |
| SDK/deployment | Xcode, SDK, iOS/iPadOS target, OS build |
| Web owner | SFSafariViewController, WKWebView, ASWebAuthenticationSession |
| URL policy | Allowed schemes, hosts, paths, redirects, external route |
| Data store | Default, identifier-backed profile, nonpersistent, Safari-managed |
| Bridge | Handler names, content world, origin/frame rule, payload schema |
| Auth | Provider sandbox, callback matcher, state/nonce/PKCE, ephemeral choice |
| Domains | Associated Domains entitlement, AASA server state, universal-link source |
| AI | Selected scope, redaction, prompt-injection fixture, proposal/result |
| Accessibility | VoiceOver, Dynamic Type, Voice Control, Switch Control, contrast |
| Device | Physical iPhone/iPad, network, browser/provider account, signed artifact |

Use synthetic pages and provider sandbox accounts for shared testing. Redact tokens, cookies, account IDs, private URLs, and page content from screenshots and logs.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Visible Safari route works | Physical target, visible SFSafariViewController, initial-load/dismissal behavior | A URL string or UIKit compile |
| Safari page remains unobscured | Full task observation with standard controls and no overlay | A view hierarchy |
| WKWebView route works | Final configuration, real page fixture, navigation/error/reload states | A web view appearing in a preview |
| Navigation is allowlisted | Allowed, redirect, malformed, blocked, and external-link tests | A host comparison in source |
| Bridge is bounded | Origin/frame checks, typed payload tests, unknown/oversized/replay rejection, teardown | A message handler registration |
| Content world is used correctly | Page/client fixture showing namespace behavior and DOM caveat | Naming a content world |
| Private data is nonpersistent | Runtime store selection plus disk/data-lifecycle inspection | Calling nonpersistent in code |
| Account switch clears intended state | Logout, store/cookie/cache cleanup, new-account fixture | Removing one cookie |
| Authentication works | Real sandbox provider, consent UI, callback, state/redirect validation, account result | A callback URL in a unit test |
| Auth cancellation recovers | User cancel, provider failure, mismatch, retry path | Completion-handler code |
| Universal link works | Signed entitlement, AASA state, physical link activation, native route | Opening the URL inside the app |
| Universal-link security holds | Malformed host/path/query/action fixtures rejected | A successful happy-path link |
| App-bound navigation works | Final configuration with allowed and blocked domains, redirects, recovery | A property value in source |
| AI is bounded | Redacted extraction, prompt-injection page, typed proposal, confirmation/rejection | A model-generated summary |
| Web/native accessibility works | Completed VoiceOver, Dynamic Type, alternate-input, focus-return tasks | Labels in source |
| Release is ready | Final signed artifact, entitlement/server review, provider evidence, privacy review | Debug build or simulator run |

## Safari Services scenarios

- [ ] Initial HTTPS support/terms URL is visible.
- [ ] SFSafariViewController is presented modally through the supported path.
- [ ] It is not embedded as a child or hidden behind an app-owned overlay.
- [ ] Reader, AutoFill, fraudulent-website warning, and standard controls remain system-owned.
- [ ] Initial load success and failure states are visible if the product depends on them.
- [ ] Done/dismissal returns focus and native context correctly.
- [ ] Action-button behavior does not become an unvalidated native mutation.
- [ ] Opening in the browser has a clear user-facing meaning.
- [ ] Mac Catalyst or visionOS-compatible target behavior is recorded when claimed.

## WKWebView navigation and process scenarios

| Scenario | Expected evidence |
| --- | --- |
| First-party main-frame load | Host/path allow decision and loaded state |
| First-party redirect | Documented redirect host and transition state |
| Unexpected host | Blocked state, safe recovery, no native action |
| HTTP or malformed URL | Rejected or explicitly handled per target policy |
| Cross-origin iframe | Stricter frame/bridge policy |
| External link | Browser or universal-link handoff with user intent |
| Custom scheme | Registered and typed action only |
| JavaScript alert/window request | UI delegate decision and accessible native presentation |
| Download | Type/size/destination/user-intent evidence |
| Web process termination | Recovery without unsafe automatic native action |
| Offline/slow page | Cancel/retry/error state without infinite spinner |
| Back-forward restoration | Safe navigation state and account boundary |

## Bridge and data-store scenarios

- [ ] Handler names are capability-specific rather than generic.
- [ ] Only the intended content world can call each handler.
- [ ] Main-frame and subframe origins are distinguished.
- [ ] Invalid JSON, unknown version, oversized strings, duplicate requests, and replay are rejected.
- [ ] Page-provided URLs, file paths, account IDs, and native action names are not trusted.
- [ ] Handler removal occurs when the web view or feature ends.
- [ ] Default persistent data is documented and intentionally retained.
- [ ] Nonpersistent data is used for the feature that requires reduced local retention.
- [ ] Identifier-backed profiles cannot read one another’s state.
- [ ] Logout/account switching handles cookies, caches, credentials, navigation, and native state.
- [ ] The team records that nonpersistent data does not erase network/provider records.

## Authentication scenarios

| Scenario | Expected evidence |
| --- | --- |
| User starts sign-in | Provider domain and consent UI appear |
| Successful callback | Callback matcher, state/redirect validation, account result |
| User cancels | Signed-out/recoverable state; no false auth failure |
| Provider error | Error state and retry path |
| Callback mismatch | Rejected callback and no account mutation |
| Stale state | Rejected attempt and fresh-session recovery |
| Ephemeral request | Selected preference and actual provider behavior recorded |
| Account switch | Old account state is cleared or isolated |
| Process interruption | Session ends safely; retry does not reuse unsafe transient state |
| Token result | Credential storage and server authorization result are separately recorded |

A callback URL means that the authentication session received a redirect. It does not independently prove token validity, account entitlement, or backend authorization.

## Associated-domain and universal-link scenarios

- [ ] Associated Domains capability is present in the intended target.
- [ ] Final signed entitlement contains only intended service-domain entries.
- [ ] Each required domain serves the expected Apple App Site Association file.
- [ ] HTTPS, certificate, redirects, and server freshness are checked.
- [ ] Development alternate mode is removed before release evidence.
- [ ] Valid universal link opens the expected native route.
- [ ] App-not-installed link opens the web fallback.
- [ ] Host, path, query, fragment, and action validation rejects malformed inputs.
- [ ] Sensitive routes still require native authorization.
- [ ] Scene continuation works from cold, suspended, and foreground states.
- [ ] Same-domain browser behavior and cross-domain handoff are tested where relevant.

## AI and privacy scenarios

- [ ] Only user-selected or explicitly requested visible content is extracted.
- [ ] Cookies, authorization headers, hidden DOM, browsing history, and unrelated frames are excluded.
- [ ] Remote page instructions are treated as untrusted data.
- [ ] A prompt-injection fixture attempts to call a native command and is rejected.
- [ ] URLs are validated before a model proposal can use them.
- [ ] Saving, importing, signing in, paying, sharing, or changing native data requires deterministic validation and confirmation.
- [ ] Logs and telemetry redact tokens, cookies, account identifiers, and private page text.
- [ ] Model failure leaves the read-only web route usable.
- [ ] The app never labels a model summary as provider or page authenticity proof.

## Accessibility and visual matrix

- [ ] VoiceOver reaches native shell controls and web content in a predictable order.
- [ ] Focus returns after Safari dismissal, auth callback, blocked navigation, and error recovery.
- [ ] Dynamic Type preserves domain, state, errors, and confirmation actions.
- [ ] Voice Control and Switch Control reach Back, Done, Retry, Open in Safari, Cancel, and Apply.
- [ ] Reduce Transparency and increased contrast preserve native status and destructive-action hierarchy.
- [ ] Liquid Glass does not obscure remote content or system-managed Safari surfaces.
- [ ] Long domains, localized errors, right-to-left content, and keyboard/pointer navigation work.
- [ ] Web content accessibility is tested as content, not inferred from native labels.

## Evidence vocabulary

| Term | Meaning |
| --- | --- |
| visible | Named physical system or app surface was observed by a person/test |
| loaded | Web content reached the expected load state |
| allowed | URL/frame/message passed the current policy |
| blocked | Policy rejected the route without claiming content identity |
| persistent | Web data is intentionally stored according to the selected store |
| private | The selected store avoids writing web data to disk; broader privacy remains separate |
| callback-received | Authentication session received a matching redirect URL |
| authenticated | Provider/server/app validation established the intended account state |
| associated | Entitlement and website association passed the required checks |
| routed | A validated link became a typed native destination |
| proposed | AI returned a typed candidate action |
| applied | Deterministic validation and user policy allowed the native action |
| unknown | The test cannot prove the next system/provider/native result |

## Sources

- [Safari Services](https://developer.apple.com/documentation/safariservices)
- [SFSafariViewController](https://developer.apple.com/documentation/safariservices/sfsafariviewcontroller)
- [SFSafariViewControllerDelegate](https://developer.apple.com/documentation/safariservices/sfsafariviewcontrollerdelegate)
- [SFSafariViewController.DataStore](https://developer.apple.com/documentation/safariservices/sfsafariviewcontroller/datastore)
- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [WKWebViewConfiguration](https://developer.apple.com/documentation/webkit/wkwebviewconfiguration)
- [WKWebsiteDataStore](https://developer.apple.com/documentation/webkit/wkwebsitedatastore)
- [WKUserContentController](https://developer.apple.com/documentation/webkit/wkusercontentcontroller)
- [WKContentWorld](https://developer.apple.com/documentation/webkit/wkcontentworld)
- [App-bound navigation](https://developer.apple.com/documentation/webkit/wkwebviewconfiguration/limitsnavigationstoappbounddomains)
- [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession)
- [ASWebAuthenticationSession.Callback](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession/callback)
- [Authenticating a user through a web service](https://developer.apple.com/documentation/authenticationservices/authenticating-a-user-through-a-web-service)
- [Configuring an associated domain](https://developer.apple.com/documentation/xcode/configuring-an-associated-domain)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Allowing apps and websites to link to your content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content)
- [Supporting universal links in your app](https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
