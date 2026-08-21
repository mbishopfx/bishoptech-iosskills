# SwiftUI WebKit, SafariServices, AuthenticationServices, PDF, and content-handoff proof matrix

This matrix proves browser/content configuration, authentication verification, passkey trust, PDF handling, link-preview behavior, Universal Links/Handoff delivery, local-AI review, accessibility, privacy, and release boundaries separately.

Use it with the [content-handoff review](../42-framework-deep-dives/103-swiftui-webkit-safariservices-authenticationservices-pdf-content-review.md), [design guide](../21-design-deep-dives/131-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-design.md), [route](../50-capability-recipes/134-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-route.md), and [recipes](../70-code-recipes/146-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-recipes.md).

## Evidence levels

| Level | Evidence | Boundary |
| --- | --- | --- |
| L0 | Current Apple documentation and SDK availability | API awareness |
| L1 | Named target, entitlements, Info.plist, privacy, and server configuration | Configuration contract |
| L2 | Unit/fixture tests for URLs, documents, callbacks, and state | App-owned validation |
| L3 | Simulator/local server/system fixture | Some app-side behavior |
| L4 | Signed physical-device/browser/credential/two-device run | System surfaces and device behavior |
| L5 | Archive/TestFlight/App Store packet | Distribution proof |
| L6 | Repeatable security/privacy/accessibility/recovery packet | Operational readiness |

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| WKWebView has intended configuration | Named target compile and runtime inspection | A configuration object in source |
| Navigation is constrained | Scheme/host/path/redirect fixtures and device run | A navigation delegate exists |
| JavaScript bridge is safe | Message schema/origin/authorization tests | A message handler callback |
| Website data follows policy | Persistent/nonpersistent/profile logout inspection | Store type in source |
| Safari surface is compliant | Visible presentation and dismissal run | A hidden or embedded controller |
| OAuth callback is valid | State/nonce/PKCE/provider/server verification | Callback URL arrival |
| Passkey is valid | Physical system credential flow and server assertion verification | Authorization controller success |
| Associated domain is deployed | Signed entitlement, AASA hosting, device fetch/tap | Local AASA file |
| Universal Link routes correctly | Physical tap, cold/warm scene, URL validation | openURL in same app |
| Handoff restores safely | Two-device activity plus current account/entity check | NSUserActivity payload |
| PDF is readable | PDFDocument/PDFView device fixture | PDFView object |
| PDF edit/export is committed | Reopened output and destination inspection | Annotation in memory |
| Link preview is bounded | Timeout/cancel/subresource/cache/redirect tests | LPLinkMetadata object |
| AI proposal is reviewable | Source/model/proposal/decision record | Summary or label |
| Accessibility works | VoiceOver/Dynamic Type/Reduce Motion/contrast/input run | Modifiers in source |
| Release is ready | Signed archive, privacy, system, TestFlight packet | Debug simulator build |

## Target and configuration packet

Record:

~~~text
App target:
Bundle ID:
Team ID/application identifier:
Deployment target:
Supported platform/device family:
WebKit/SafariServices/AuthenticationServices/PDFKit/LinkPresentation imports:
Associated Domains entitlement:
applinks domains:
webcredentials domains:
activitycontinuation domains:
AASA URL and response:
URL schemes/callback:
ATS/network/privacy configuration:
PDF/document provider configuration:
Credential provider/extension configuration:
Server environment and relying party:
Archive/TestFlight build:
~~~

Inspect the signed archive, not only the Xcode project settings. Confirm each target has the capabilities it actually uses.

## WKWebView matrix

| Check | Evidence | Failure to record |
| --- | --- | --- |
| Configuration created before web view | Runtime inspection | Default configuration accidentally used |
| Data store is correct | Persistent/nonpersistent/profile fixture | Cookies leak across accounts |
| Navigation allowlist works | Scheme/host/path/redirect table | Prefix bypass or unsafe redirect |
| App-bound domain policy works | Target entitlement/runtime test | Remote page unexpectedly allowed |
| Bridge is bounded | Oversize/malformed/untrusted-origin messages | Page triggers native side effect |
| Bridge lifecycle is safe | Teardown and retain-cycle test | Old scene receives messages |
| Loading cancellation works | Scene disappear/network stall | Stale progress/error |
| External browser route is clear | Physical tap/open test | App hides destination |

Test unexpected schemes, userinfo, Unicode hosts, percent-encoding, fragments, query parameters, redirects, nested frames, and JavaScript disabled/error states.

## SafariServices matrix

| Check | Evidence | Boundary |
| --- | --- | --- |
| Controller is visible | Physical presentation | Not an invisible fetcher |
| Presentation is modal/supported | View hierarchy and dismissal | Not embedded as a child |
| Public content loads | HTTPS device fixture | Not authentication proof |
| Initial load failure is shown | Delegate and UI fixture | No silent success |
| Dismissal is handled | Delegate callback | User completed website task |
| App does not scrape website data | Code/data inspection | Safari session is not app cookies |

## Authentication callback matrix

| Check | Evidence | Boundary |
| --- | --- | --- |
| Authorization request originates from server | Request/nonce/PKCE fixture | Client-created token |
| Callback is for current session | Session identity and state | URL scheme alone |
| State/nonce/PKCE verified | Negative fixtures and server logs | Successful redirect |
| Issuer/audience/expiry verified | Server verifier result | UI message |
| Account binding verified | Server account response | Provider display name |
| Cancellation is safe | User cancel run | Retry loop |
| Tokens are not logged | Redacted logs/crash review | Source comments |
| Logout removes intended state | Account-switch/data-store fixture | UI sign-out button |

## Passkey matrix

| Check | Evidence | Not enough |
| --- | --- | --- |
| Relying party is correct | Server, client, and associated-domain inspection | Host string in UI |
| webcredentials association is deployed | AASA/entitlement/device run | Entitlement in project |
| Challenge is fresh and bound | Server challenge logs/negative replay | Data passed to request |
| System credential UI appears | Physical device | Controller object |
| Success is server-verified | Assertion verifier result | Delegate success |
| No credential is available is recoverable | Physical no-credential path | Crash-free success path |
| WebView passkey works | Associated domain, WebAuthn, device, server run | JavaScript availability check |
| Local unlock is separate | Key policy/account/recovery test | Sign-in Boolean |

## PDF matrix

| Check | Evidence | Boundary |
| --- | --- | --- |
| Source URL/data is authorized | Security-scoped scope or app-owned source | File URL string |
| Byte/document budget works | Oversize/malformed/password fixtures | PDFDocument non-nil |
| Permissions are respected | Copy/print/annotation fixture | Page visible |
| PDFView accessibility works | VoiceOver/page/search/selection run | PDFView displayed |
| Annotation is staged | Draft/revert fixture | In-memory annotation |
| Output is valid | Reopen, page count, metadata, annotations | write returned true |
| Destination is explicit | Export/replace confirmation | Default overwrite |
| External PDF links are validated | Scheme/host/confirmation tests | Annotation URL |

## Link Presentation matrix

| Check | Evidence | Boundary |
| --- | --- | --- |
| URL policy is applied | Scheme/host/path tests | LPMetadataProvider fetch |
| Timeout is bounded | Slow-server fixture | Default timeout |
| Cancellation works | Card removal/stalled request | Completion handler exists |
| Subresources follow policy | shouldFetchSubresources fixture | Title returned |
| Redirect is recorded | Original/final URL inspection | Preview title |
| Cache is bounded | TTL/URL/revision tests | Permanent metadata |
| Missing metadata is usable | No-image/no-title/error fixture | Broken card |

## Associated Domains and scene matrix

| Check | Evidence | Boundary |
| --- | --- | --- |
| Entitlement is signed into intended target | Archive inspection | Xcode capability tab |
| AASA is publicly hosted | HTTPS, no redirect, correct content type | Local file |
| CDN/device association is current | Install/device logs or physical route | Curl alone |
| Universal Link path is matched | Physical tap for allowed/disallowed paths | Any URL opens app |
| Cold scene delivery works | Terminated app tap | Warm callback |
| Warm scene delivery works | Existing scene tap | Cold callback |
| Handoff activity arrives | Two-device run | Local NSUserActivity |
| Route parser rejects malformed values | Negative URL/activity fixtures | Happy path |
| Current account/entity is checked | Expired/unauthorized/deleted fixture | ID in payload |

Keep the website fallback in the evidence packet. A Universal Link route is useful partly because the same HTTP URL remains meaningful when the app is absent.

## AI and side-effect matrix

| Stage | Evidence | Boundary |
| --- | --- | --- |
| Web/PDF source | URL/document revision and access scope | Source is trustworthy |
| Local model | Model ID/revision/compute policy | Model quality |
| Proposal | Typed output, uncertainty, source | Committed action |
| Review | User decision and edited values | Automatic execution |
| Navigation | URL re-validation | Model-chosen trust |
| Authentication | Server challenge/verification | Model-selected credential |
| PDF mutation | User confirmation and output inspection | Generated bytes |

## Accessibility, privacy, and recovery matrix

| Check | Evidence |
| --- | --- |
| Browser title/origin/status is accessible | VoiceOver run |
| Auth states do not expose secrets | Spoken-content/log review |
| PDF navigation/search/annotations work with accessibility | VoiceOver and keyboard run |
| Link preview has text fallback | Missing-image/accessibility run |
| Universal Link/Handoff stale state is understandable | Expired/deleted/unauthorized fixture |
| Dynamic Type and contrast preserve controls | Device settings run |
| Reduce Motion preserves arrival and document comparison | Device settings run |
| Web data/cookies follow logout policy | Data-store inspection |
| Callback URLs/tokens are redacted | Logs/crash review |
| Temporary PDFs and cached previews are removed | File-system/storage inspection |

## Release packet

~~~text
[ ] Named target compile and archive
[ ] Signed Associated Domains, AASA, URL schemes, and callback inspection
[ ] WKWebView data store, bridge, navigation, and cancellation run
[ ] Visible SFSafariViewController run
[ ] OAuth/OIDC callback negative and server-verification run
[ ] Passkey physical device and server verifier run
[ ] PDF permissions, accessibility, edit, export, and reopen run
[ ] Link preview timeout/cancel/redirect/cache run
[ ] Universal Link cold/warm and Handoff two-device run
[ ] AI source/model/proposal/review packet
[ ] Privacy/log/data-deletion review
[ ] VoiceOver/Dynamic Type/Reduce Motion/contrast/input run
[ ] TestFlight/release-system run
[ ] Known unsupported cases and recovery copy
~~~

## Sources

- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [WKWebViewConfiguration](https://developer.apple.com/documentation/webkit/wkwebviewconfiguration)
- [WKNavigationDelegate](https://developer.apple.com/documentation/webkit/wknavigationdelegate)
- [WKWebsiteDataStore](https://developer.apple.com/documentation/webkit/wkwebsitedatastore)
- [SFSafariViewController](https://developer.apple.com/documentation/safariservices/sfsafariviewcontroller)
- [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession)
- [WebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/webauthenticationsession)
- [Authenticating a user through a web service](https://developer.apple.com/documentation/authenticationservices/authenticating-a-user-through-a-web-service)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [ASAuthorizationPlatformPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialprovider)
- [PDFKit](https://developer.apple.com/documentation/pdfkit)
- [PDFDocument](https://developer.apple.com/documentation/pdfkit/pdfdocument)
- [PDFView](https://developer.apple.com/documentation/pdfkit/pdfview)
- [PDFPageOverlayViewProvider](https://developer.apple.com/documentation/pdfkit/pdfpageoverlayviewprovider)
- [Link Presentation](https://developer.apple.com/documentation/linkpresentation)
- [LPMetadataProvider](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider)
- [LinkMetadata](https://developer.apple.com/documentation/linkpresentation/linkmetadata)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Allowing apps and websites to link to your content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content)
- [Supporting universal links in your app](https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app)
- [UIScene.ConnectionOptions](https://developer.apple.com/documentation/uikit/uiscene/connectionoptions)
- [System events](https://developer.apple.com/documentation/swiftui/system-events)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
