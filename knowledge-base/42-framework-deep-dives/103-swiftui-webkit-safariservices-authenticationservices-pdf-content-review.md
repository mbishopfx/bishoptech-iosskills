# SwiftUI WebKit, SafariServices, AuthenticationServices, PDF, and content-handoff review

Web content, browser authentication, passkeys, PDF documents, rich link previews, and Universal Links all cross trust boundaries, but they are not interchangeable. A WKWebView is an app-controlled web-content surface. SFSafariViewController is a visible Safari-managed browsing surface. ASWebAuthenticationSession and SwiftUI WebAuthenticationSession are authentication handoffs. AuthenticationServices passkeys are challenge-based credentials that require a relying-party/server contract. PDFKit renders and edits document data. Link Presentation fetches remote metadata. Associated Domains and scene delivery establish verified routing, not account authorization.

This review extends the existing [WebKit and web-auth boundary deep dive](29-webkit-safariservices-and-web-auth-boundaries.md), [Authentication Services/passkeys deep dive](35-authentication-services-passkeys-and-apple-sign-in.md), [Link Presentation deep dive](44-linkpresentation-rich-link-metadata.md), [Universal Links/Handoff deep dive](72-universal-links-handoff-and-scene-delivery.md), [web content/native-shell design](../21-design-deep-dives/49-web-content-and-native-shell-design.md), and [web-auth route](../50-capability-recipes/52-webkit-safariservices-web-auth-route.md). Its distinct focus is the end-to-end content handoff: selecting the correct browser/document/auth surface, validating navigation and callbacks, preserving privacy and identity boundaries, rendering PDFs and previews safely, routing verified links into SwiftUI scenes, and keeping local-AI proposals outside security decisions.

## The content-handoff contract

Keep the authorities explicit:

~~~text
user job
-> choose native content, WKWebView, Safari view, web-auth session, passkey, PDFKit, or link preview
-> target/entitlement/privacy configuration
-> allowlisted URL/document/credential request
-> system or app-owned loading process
-> navigation/callback/document/metadata result
-> current account and authorization validation
-> app-owned record or scene route
-> user-reviewed side effect
~~~

The network server, browser, WebKit process, system credential UI, associated-domain verifier, PDF renderer, and app scene may each own a different part of the route. Do not compress those into “the page loaded,” “the callback arrived,” or “the user has signed in.”

## Choose the correct surface

| User job | Preferred surface | Authority boundary |
| --- | --- | --- |
| Show a public article or terms | SFSafariViewController | Safari owns browsing interaction; app receives limited lifecycle events |
| Render interactive app-owned web content | WKWebView | App owns configuration, navigation policy, bridge, data store, and UI |
| Authenticate with an OAuth/OIDC website | ASWebAuthenticationSession or SwiftUI WebAuthenticationSession | System/browser owns login UI and callback delivery; server verifies response |
| Use a platform passkey | AuthenticationServices | System credential UI and server challenge/relying party verify identity |
| Use passkeys in a WKWebView | WKWebView plus associated-domain/webcredentials setup | WebAuthn page, relying-party domain, app association, and server stay aligned |
| Display or annotate a PDF | PDFKit | PDFDocument/PDFView/PDFPage own document rendering and edits |
| Fetch a rich URL preview | LinkPresentation | Remote metadata is untrusted, optional, cancellable, and cacheable |
| Open a verified web URL in native content | Universal Links/Associated Domains | Website association and system route; app validates URL and current access |
| Continue an activity between devices | Handoff/NSUserActivity | Activity payload is context, not authentication |

If the product needs to read or mutate page content, use WKWebView deliberately. If it only needs a visible web page, prefer SFSafariViewController. If it needs login, use the authentication session rather than scraping Safari cookies or embedding a password form.

## WKWebView is an app-owned boundary

WKWebView can display interactive web content and lets the app control navigation through WKNavigationDelegate and UI behavior through WKUIDelegate. That power creates obligations:

- create the WKWebViewConfiguration before the web view;
- choose a persistent, nonpersistent, or profile-specific WKWebsiteDataStore;
- decide whether cookies and website data may persist;
- configure user content scripts and message handlers with a narrow contract;
- use a navigation delegate to allow, cancel, or redirect navigation;
- validate schemes, hosts, paths, and redirect destinations;
- treat page JavaScript and remote HTML as untrusted input;
- keep bridge methods idempotent and authorization-aware;
- cancel and tear down the view when its scene or task no longer owns it.

WKWebView content renders in WebKit-managed processes. A web-content process boundary improves stability and isolation but does not make remote content trusted. A JavaScript message is not an authenticated user instruction.

### Process and data-store choices

WKWebsiteDataStore.defaultDataStore persists cookies, caches, and other website data. WKWebsiteDataStore.nonPersistentDataStore keeps data in memory and is appropriate for a private or one-session route. A profile data store can isolate a named browsing profile. Select the store before creating the WKWebView.

WKProcessPool is a historical process-sharing mechanism. Current Apple documentation marks creating multiple instances as deprecated and says multiple instances no longer have an effect. Do not build a modern privacy boundary around a pool identity. Use the current WebKit data-store and target configuration APIs, and verify the selected SDK.

Choose the data store from the user job:

| Need | Store | Review |
| --- | --- | --- |
| App-owned signed-in web experience | Persistent or profile-specific | Cookie lifecycle, logout, data deletion, account switch |
| Preview or one-time tool | Nonpersistent | No later reuse, clean teardown |
| Separate accounts | Named persistent stores where supported | Store identity, migration, logout isolation |
| Authentication | ASWebAuthenticationSession | Never share cookies by copying them from WKWebView |

Do not reuse a persistent store across unrelated accounts unless the product has an explicit account-switch and deletion policy.

### Navigation allowlist

The navigation delegate should make a decision for every navigation:

1. parse the URL;
2. reject unsupported schemes;
3. distinguish app-owned hosts from external hosts;
4. validate path/query parameters;
5. handle redirects through the same policy;
6. route universal links or external browser actions intentionally;
7. prevent sensitive data from being placed in URLs;
8. log only safe route metadata.

An allowlist should be based on scheme, host, path, and purpose. A string prefix check is not sufficient for a security boundary. Treat userinfo, Unicode hostnames, fragments, query values, and percent-encoded paths carefully.

### JavaScript bridge

If the app injects a user script or registers a WKScriptMessageHandler:

- use a named message namespace;
- validate message shape and size;
- require a page-origin or document-session check where appropriate;
- expose narrowly scoped operations;
- require app-side authorization for every mutation;
- return structured success/error values;
- prevent a page from opening arbitrary local files or URLs;
- remove handlers on teardown to avoid retain cycles and stale ownership.

A trusted first-party page can still be compromised by a redirect, injected content, or an unexpected frame. Keep the native bridge conservative.

## SFSafariViewController is visible Safari-managed browsing

Use SFSafariViewController when the person needs to browse a visible website and the app does not need to customize or inspect its content. Apple documents that Safari features such as Reader, AutoFill, Fraudulent Website Warning, and content blocking remain available, while the app cannot access browsing history, AutoFill data, or website data.

The view controller must visibly present information. Do not cover it with an overlay, use it as an invisible tracking engine, embed it as a child view controller, or use it to scrape login state. Present it modally and let the person dismiss it.

Use its delegate for lifecycle and activity events such as initial-load result and dismissal. The delegate does not turn the page into app-owned authenticated content.

When the product needs to interact with the content, use WKWebView. When it needs to authenticate, use ASWebAuthenticationSession or the SwiftUI webAuthenticationSession environment value. If a link should open in native content, use Universal Links and validate the route.

## Web authentication is a callback protocol

ASWebAuthenticationSession presents a system-managed authentication experience and returns a callback URL to the calling session. SwiftUI WebAuthenticationSession wraps the same concept in an environment value and async method.

The app’s callback handler should:

1. verify that the session is still current;
2. validate the callback scheme or callback object;
3. parse state, code, error, and provider data;
4. reject missing or mismatched state;
5. exchange a code server-side with the intended redirect URI and client;
6. verify issuer, audience, nonce, PKCE, expiration, and token binding as required by the provider;
7. create an app session only after server verification;
8. discard callback URLs and tokens from logs.

An arriving callback is not proof of a signed-in account. A provider page that displays a name is not proof that the app may unlock private local data.

Ephemeral browser sessions can reduce reuse of previous web session state but may force the person to authenticate again. Treat the choice as a privacy and conversion decision, not a hidden implementation detail.

## Passkeys require aligned relying-party configuration

Passkeys use public-key credentials and a server challenge. The device keeps the private key; the server verifies the assertion against the registered public key. The app should never invent a local “passkey success” state from a button tap or a non-verified callback.

For native or web passkey routes:

- obtain the challenge and user data from the server;
- use the correct relying-party identifier;
- configure Associated Domains webcredentials when the documented route requires it;
- create the platform public-key credential provider;
- create registration or assertion requests;
- present ASAuthorizationController with a valid presentation context;
- handle success and error delegate callbacks;
- send the credential response to the server;
- create or unlock the app account only after server verification.

When passkeys are used in a WKWebView, the relying-party domain and associated-domain configuration must align. WebAuthn JavaScript availability does not prove that a particular credential is available or that the server will accept the assertion.

### Passkey and local-unlock separation

A passkey can authenticate an account, while a local app may use a separate key-encryption or Secure Enclave policy. Do not use a server sign-in result as an unreviewed command to decrypt or export all local data. Model:

~~~text
server challenge
-> system credential UI
-> assertion response
-> server verification
-> app account/session
-> local unlock policy
-> user-approved data access
~~~

Identity, entitlement, and local-data authorization are related but separate decisions.

## PDFKit is a document surface, not a web browser

PDFDocument can load PDF data or a URL, inspect pages and text, search and select content, add annotations, and write a document. PDFView provides a native display and navigation surface. PDFPage and PDFAnnotation represent document content and user edits.

Choose the document authority:

- a security-scoped file URL from the user’s file picker;
- an app-owned URL;
- data downloaded through URLSession after network validation;
- a PDFDocument created from Data;
- a PDF supplied by a share or document provider.

Keep security-scoped access alive for the duration of the read/write operation. Validate the content type and byte budget before creating a document. Do not trust a PDF’s title, annotation, embedded URL, or extracted text as an instruction to mutate app data.

For editable PDFs:

1. open the current document;
2. create or update an annotation or page overlay;
3. let the person review the draft;
4. write to a new app-owned URL or explicit document destination;
5. reopen the output;
6. inspect page count, metadata, annotations, and permissions;
7. replace the source only when the user chose that destination.

PDF permissions can affect copying, printing, and other operations. The viewer’s ability to display a page is not proof that every requested action is permitted.

## Link Presentation is remote metadata

LPMetadataProvider fetches optional title, icon, image, and video metadata. It can fail because of network loss, a timeout, a cancellation, or an unknown server response. Set a timeout and subresource policy, cancel when the card disappears, and cache metadata only with a source URL and redirect-aware revision.

Link metadata is not the page content, not a security verdict, and not a user’s intent. Validate the URL before starting a fetch, prevent SSRF-like internal URL behavior in any server-assisted route, and avoid rendering remote HTML as if it were native text.

When a link preview is shared or indexed:

- keep original and returned URLs separate;
- show the final destination where it matters;
- avoid claiming that the preview is current indefinitely;
- use a standard LinkPresentation view or a clearly attributed native card;
- provide an open action that repeats URL validation.

## Associated Domains create verified routing

Associated Domains support services such as:

- applinks for Universal Links;
- webcredentials for shared web credentials and passkey trust;
- activitycontinuation for Handoff;
- appclips for App Clip association.

The app target needs the Associated Domains entitlement and the website needs a correctly hosted apple-app-site-association file. Domain, subdomain, path, Team ID/application identifier, deployment, and CDN timing all matter. A source file in a repository is not proof that the installed device fetched the current association.

Universal Links provide an HTTP/HTTPS URL that can open app content when installed and web content when the app is absent. The app should validate every received URL and restrict actions to safe routes. Apple specifically warns that Universal Links are a potential attack vector and that URL parameters must be validated.

Handoff carries user activity context between devices. An NSUserActivity with a webpageURL can help restore a scene, but it is not an authentication token and should not bypass current account or entitlement checks.

## Scene delivery and SwiftUI

SwiftUI can receive URLs with onOpenURL, named activities with onContinueUserActivity, and external events with handlesExternalEvents. UIKit scene connection options can carry URL contexts and user activities when a scene is cold-launched.

Use one parser and route coordinator for:

- warm onOpenURL delivery;
- cold UIScene.ConnectionOptions URLContexts;
- Handoff NSUserActivity;
- share-sheet or document-provider URLs;
- App Intent or Spotlight destinations.

Pass a small typed route value to the scene. Resolve current data after the scene arrives. If a web URL identifies an item, validate the host, path, query, account, and authorization before showing it. Do not let a URL directly delete, export, or expose private content.

## On-device AI and web/document content

Local AI can summarize a PDF, classify a page, suggest a route, draft a reply, or propose a document annotation. Treat the output as a proposal:

- preserve the source URL/document revision;
- capture the model and prompt policy revision;
- keep web content untrusted;
- show source excerpts and uncertainty;
- require review for credentials, account changes, sharing, deletion, and external navigation;
- prevent model output from becoming JavaScript or a native bridge command without validation;
- re-open and re-validate the current document or route before committing.

Never allow a model to choose a passkey credential, accept an authentication callback, or bypass the server’s verification.

## SwiftUI and Liquid Glass composition

Use native Apple controls for browser, authentication, PDF, and share actions. Liquid Glass can group app-owned navigation, document actions, or review controls, but should not obscure the page, cover SFSafariViewController, imitate system credential UI, or make an untrusted web preview look like verified app content.

Use typed visual states:

~~~text
web loading -> verified navigation -> page visible -> external handoff
auth starting -> system approval -> callback received -> server verified
PDF opening -> document loaded -> edit draft -> output validated
link fetching -> metadata ready -> preview attributed -> URL opened
Universal Link received -> route parsed -> current entity authorized -> scene opened
~~~

Provide opaque fallbacks for reduced transparency, high contrast, or unavailable blur. Keep content readable under Dynamic Type and respect Reduce Motion.

## Accessibility and privacy

Web, auth, and document surfaces should expose:

- a clear title and source;
- loading, failure, and offline status;
- focused recovery actions;
- accessible PDF page and annotation semantics;
- meaningful labels for link preview images and destination actions;
- passkey and sign-in result states without reading secrets aloud;
- keyboard/pointer/Switch Control routes for web controls and document actions;
- reduced-motion and high-contrast alternatives.

Do not log URLs containing authorization codes, callback fragments, tokens, passkey credential IDs, cookie values, PDF content, or extracted private text. Delete temporary files and nonpersistent web data when the feature ends.

## Verification boundary

| Claim | Evidence | Still not enough |
| --- | --- | --- |
| WKWebView navigation is constrained | Physical target with allowlist/redirect tests | A navigation delegate declaration |
| Website data is private or persistent as promised | Data-store inspection and logout/account-switch run | Choosing nonpersistentDataStore in source |
| Safari surface is compliant | Visible modal system run | A hidden or embedded controller |
| OAuth callback is safe | Provider/server state, nonce, PKCE, and callback test | URL parsing alone |
| Passkey login works | Physical system credential flow and server verification | ASAuthorizationController success |
| PDF edit is committed | Reopened output and destination verification | PDFView annotation |
| Link preview is current enough | Timeout/cancel/cache/redirect test | LPLinkMetadata object |
| Universal Link is trusted | Signed entitlement, AASA, physical tap, route validation | A URL string or simulator open |
| Handoff restores safely | Two-device activity run plus current account check | NSUserActivity payload |
| AI output is reviewable | Source/model/proposal/decision record | Summary or suggested action |
| Release is ready | Signed archive, privacy, device, system, and TestFlight packet | Debug run |

## Sources

- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [WKWebViewConfiguration](https://developer.apple.com/documentation/webkit/wkwebviewconfiguration)
- [WKNavigationDelegate](https://developer.apple.com/documentation/webkit/wknavigationdelegate)
- [WKUIDelegate](https://developer.apple.com/documentation/webkit/wkuidelegate)
- [WKWebsiteDataStore](https://developer.apple.com/documentation/webkit/wkwebsitedatastore)
- [WKProcessPool](https://developer.apple.com/documentation/webkit/wkprocesspool)
- [SafariServices](https://developer.apple.com/documentation/safariservices)
- [SFSafariViewController](https://developer.apple.com/documentation/safariservices/sfsafariviewcontroller)
- [SFSafariViewControllerDelegate](https://developer.apple.com/documentation/safariservices/sfsafariviewcontrollerdelegate)
- [Authentication Services](https://developer.apple.com/documentation/authenticationservices)
- [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession)
- [WebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/webauthenticationsession)
- [Authenticating a user through a web service](https://developer.apple.com/documentation/authenticationservices/authenticating-a-user-through-a-web-service)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [ASAuthorizationControllerDelegate](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontrollerdelegate)
- [ASAuthorizationPlatformPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialprovider)
- [Supporting passkeys in browser apps](https://developer.apple.com/documentation/authenticationservices/authenticating-people-by-using-passkeys-in-browser-apps)
- [PDFKit](https://developer.apple.com/documentation/pdfkit)
- [PDFDocument](https://developer.apple.com/documentation/pdfkit/pdfdocument)
- [PDFView](https://developer.apple.com/documentation/pdfkit/pdfview)
- [PDFPage](https://developer.apple.com/documentation/pdfkit/pdfpage)
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
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
