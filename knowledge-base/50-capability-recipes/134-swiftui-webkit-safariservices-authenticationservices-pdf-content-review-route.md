# SwiftUI WebKit, SafariServices, AuthenticationServices, PDF, and content-handoff review route

Use this route when an app needs embedded web content, public browsing, web authentication, passkeys, PDF viewing/editing, rich-link previews, Universal Links, Handoff, or a local-AI proposal over web/document content.

Read the [content-handoff deep dive](../42-framework-deep-dives/103-swiftui-webkit-safariservices-authenticationservices-pdf-content-review.md), [design guide](../21-design-deep-dives/131-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-design.md), [proof matrix](../60-verification/128-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-proof-matrix.md), and [recipes](../70-code-recipes/146-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-recipes.md) before implementation.

## Route selector

| User need | Route | Required proof boundary |
| --- | --- | --- |
| Public article/support/terms | SFSafariViewController | Visible system browser surface and dismissal |
| App-controlled web UI | WKWebView | Configuration, navigation allowlist, bridge, data store |
| OAuth/OIDC login | ASWebAuthenticationSession/WebAuthenticationSession | Callback, state/PKCE/nonce, server verification |
| Native passkey | AuthenticationServices | Relying party, challenge, system UI, server verification |
| Passkey in web content | WKWebView + webcredentials association | AASA/entitlement, WebAuthn, relying-party/server alignment |
| PDF read/annotate | PDFDocument/PDFView/PDFPage | Document permissions, draft, output validation |
| Rich URL card | LinkPresentation | URL validation, timeout/cancel, metadata attribution |
| Web-to-native content | Universal Links | Associated Domains, AASA, safe parser, current auth |
| Cross-device continuation | Handoff/NSUserActivity | Activity payload, current account, stale recovery |

## Contract worksheet

~~~text
User job:
Surface:
Allowed URL schemes:
Allowed hosts/paths:
Web content app-controlled: yes/no:
Website data: persistent / nonpersistent / profile:
Authentication provider:
Callback object or scheme:
Relying party:
Associated domains:
PDF source and security scope:
Document destination:
Preview timeout/subresources:
Universal Link/Handoff route:
AI proposal:
User review:
Physical-device proof:
Release proof:
~~~

## Target and entitlement gate

Inspect the intended target:

- WebKit, SafariServices, AuthenticationServices, PDFKit, LinkPresentation, UIKit, SwiftUI imports;
- deployment target and platform/device family;
- Associated Domains capability and signed entitlement;
- app identifier and Team ID used by the AASA/webcredentials relationship;
- URL schemes and callback configuration;
- ATS and network/privacy configuration;
- passkey relying-party server configuration;
- file/document provider and security-scoped access;
- extension membership if a credential provider or browser route exists;
- archive, TestFlight, and release metadata.

Keep the web server, app target, entitlements, and current device build in one evidence packet. A local AASA fixture is not deployment proof.

## Route A: visible public web content

1. Validate an https URL.
2. Explain that the app will open a website.
3. Present SFSafariViewController modally and visibly.
4. Do not overlay, embed, or scrape the controller.
5. Observe initial-load and dismissal events.
6. Treat dismissal as navigation completion only when the product can prove it.
7. Offer a native or Universal Link route where applicable.

Use this for public pages, support, terms, and browsing where the app does not need to read page content.

## Route B: controlled WKWebView content

1. Build WKWebViewConfiguration before WKWebView.
2. Choose default, nonpersistent, or profile data store.
3. Configure preferences, user scripts, content controller, and app-bound domains deliberately.
4. Attach navigation and UI delegates.
5. Allow only safe schemes, hosts, paths, and redirect destinations.
6. Keep native bridge methods narrow and authenticated.
7. Display loading, offline, blocked, and external-browser states.
8. Tear down tasks, message handlers, and delegates with the scene.
9. Delete data on logout or account switch when promised.

Do not make a WKWebView a hidden browser or credential scraper.

## Route C: web authentication

1. Ask the provider/server for a signed or nonce-bound authorization request.
2. Build the URL with state, PKCE, nonce, redirect, and scope policy.
3. Start ASWebAuthenticationSession or SwiftUI WebAuthenticationSession.
4. Keep the session alive until callback, cancellation, or error.
5. Validate callback object/scheme, state, and provider response.
6. Exchange the code on the server.
7. Verify issuer, audience, nonce, PKCE, expiry, and account binding.
8. Create the app session only after server success.
9. Remove auth query values from logs and navigation history.

An ephemeral browser setting can change reuse and sign-in friction. Make it a product decision.

## Route D: passkey

1. Obtain the server challenge and user ID.
2. Confirm the relying-party identifier and Associated Domains/webcredentials configuration.
3. Create a platform public-key credential provider.
4. Create registration or assertion request.
5. Present ASAuthorizationController with a presentation anchor.
6. Handle success, cancellation, missing credential, and error.
7. Send the credential response to the server.
8. Verify it on the server.
9. Update the app account or local unlock state after verification.

For WKWebView passkeys, keep the website origin, relying party, associated domain, and server verifier aligned. A passkey callback is not an account mutation until the server accepts it.

## Route E: PDF open, review, and export

1. Obtain data or a security-scoped URL from an authorized source.
2. Enforce a byte budget and validate the PDF document.
3. Open a PDFDocument.
4. Display with PDFView or a native SwiftUI wrapper.
5. Show permissions, password, and annotation state.
6. Build annotations or page overlays as drafts.
7. Write a new output or replace the chosen file only after confirmation.
8. Reopen the output and inspect page count, metadata, annotations, and access.
9. Store the destination and source revision.

Keep an output file separate from the source until validation succeeds.

## Route F: link preview

1. Validate the URL scheme and host policy.
2. Create a new LPMetadataProvider per request.
3. Set timeout and subresource policy.
4. Start fetching and cancel when the card disappears.
5. Store original and returned/redirected URL separately.
6. Render title/icon/image as untrusted optional metadata.
7. Cache with a freshness/revision policy.
8. Open via Safari, WKWebView, Universal Link, or native route after validation.

Do not treat the presence of LPLinkMetadata as a source-authenticity decision.

## Route G: Universal Links and Handoff

1. Configure the correct Associated Domains service.
2. Host the AASA file for every subdomain without redirects.
3. Validate the signed entitlement and app identifier.
4. Build one parser for URLContexts, onOpenURL, and user activities.
5. Validate host, path, query, fragment, and route revision.
6. Resolve current app data and authorization.
7. Show missing/expired/unauthorized recovery.
8. Deliver to the correct SwiftUI scene.
9. Keep Handoff payload context separate from authentication.

Use applinks for Universal Links, webcredentials for shared credentials/passkeys, and activitycontinuation for Handoff. Do not use an HTTP URL as a universal-link test by calling openURL from the same app; that route may intentionally open the website instead.

## SwiftUI scene route

Converge cold and warm delivery:

~~~text
UIScene.ConnectionOptions URLContexts/userActivities
              \/
       shared route parser
          /        \
     onOpenURL   onContinueUserActivity
          \        /
         app route coordinator
                 |
    current entity/account resolution
                 |
       authorized SwiftUI destination
~~~

Pass a typed route value into the scene. Do not pass raw tokens, arbitrary JavaScript, or unvalidated URL parameters.

## On-device AI proposal route

1. Materialize the current web/document source.
2. Record URL/document revision and local model revision.
3. Run bounded on-device inference.
4. Show the source and proposal.
5. Require review for external navigation, account actions, forms, sharing, deletion, or credential use.
6. Re-validate the current source before committing.
7. Use normal app operations for the final action.

Keep model output out of WebKit message handlers and AuthenticationServices decisions.

## Accessibility and native design gate

Verify:

- browser origin/title and status are readable;
- passkey/authentication states do not expose secrets;
- PDF pages, search, selection, annotations, and page changes are navigable;
- link previews have text alternatives and retry;
- Universal Link/Handoff arrival explains current account or stale state;
- Dynamic Type, VoiceOver, Reduce Motion, contrast, keyboard, pointer, and Switch Control work;
- Liquid Glass does not cover web/PDF content or system auth chrome.

## Proof packet

~~~text
Target/deployment/platform:
WKWebView configuration/data-store:
Navigation allowlist and bridge:
SFSafariViewController visible run:
Auth provider/callback/state/PKCE:
Passkey relying-party/AASA/entitlement:
Server verification result:
PDF source/security scope/output:
Link metadata timeout/cancel/cache:
Universal Link/Handoff AASA/device run:
AI source/model/proposal/review:
Accessibility/input run:
Privacy/logout/data deletion:
Archive/TestFlight/release result:
Known unsupported cases:
~~~

## Completion checklist

~~~text
[ ] The surface matches the user job.
[ ] WKWebView and SFSafariViewController roles are not conflated.
[ ] WebKit data-store and navigation policy are explicit.
[ ] Auth callbacks are validated and server-verified.
[ ] Passkey relying party, associated domains, challenge, and verifier agree.
[ ] PDF source, permissions, draft, export, and replacement are separate.
[ ] Link metadata is bounded, cancellable, attributed, and not trusted as page truth.
[ ] Universal Links and Handoff parse and authorize current app state.
[ ] Local AI proposes without selecting credentials or bypassing verification.
[ ] Liquid Glass/native/accessibility/input behavior is reviewed.
[ ] Physical-device, system, archive, TestFlight, and release proof is attached.
~~~

## Sources

- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [WKWebViewConfiguration](https://developer.apple.com/documentation/webkit/wkwebviewconfiguration)
- [WKNavigationDelegate](https://developer.apple.com/documentation/webkit/wknavigationdelegate)
- [WKWebsiteDataStore](https://developer.apple.com/documentation/webkit/wkwebsitedatastore)
- [SafariServices](https://developer.apple.com/documentation/safariservices)
- [SFSafariViewController](https://developer.apple.com/documentation/safariservices/sfsafariviewcontroller)
- [Authentication Services](https://developer.apple.com/documentation/authenticationservices)
- [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession)
- [WebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/webauthenticationsession)
- [Authenticating a user through a web service](https://developer.apple.com/documentation/authenticationservices/authenticating-a-user-through-a-web-service)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [ASAuthorizationPlatformPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialprovider)
- [PDFKit](https://developer.apple.com/documentation/pdfkit)
- [PDFDocument](https://developer.apple.com/documentation/pdfkit/pdfdocument)
- [PDFView](https://developer.apple.com/documentation/pdfkit/pdfview)
- [Link Presentation](https://developer.apple.com/documentation/linkpresentation)
- [LPMetadataProvider](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider)
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
