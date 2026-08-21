# WebKit, Safari Services, web authentication, and native handoff boundaries

Apple’s web stack is not one interchangeable browser surface. The correct route depends on who should own the web UI, who may inspect content, how cookies and website data are scoped, whether the user is authenticating, and whether a verified website-to-app handoff is part of the product.

Use this deep dive when an iOS 26 app needs to:

- show support, terms, documentation, or another visible website without building a browser;
- embed and customize web content inside a native SwiftUI/UIKit shell;
- bridge a controlled webpage to native code;
- run a secure web authentication session and receive a callback;
- open verified website links in the native app through associated domains;
- choose persistent, profile, or private web data;
- apply app-bound navigation and web-content restrictions;
- use on-device AI over approved web content without treating remote text as trusted instructions.

This route is version- and target-sensitive. Confirm the selected SDK, deployment target, platform, entitlement, server configuration, and physical-device behavior before shipping.

## Select the owner before selecting the framework

| Product need | Route | Ownership boundary |
| --- | --- | --- |
| Visible standard browser UI with no content inspection | SFSafariViewController | Safari Services owns browsing interaction and website data |
| App-owned web UI, navigation, scripts, or native bridge | WKWebView | The app owns configuration, delegates, bridge, and data policy |
| Sign in through a web service | ASWebAuthenticationSession | Authentication Services owns the browser session and callback delivery |
| Website link opens the installed native app | Associated Domains and universal links | Website association and the system decide verified handoff |
| User selects a link to stay in the browser | Safari or SFSafariViewController | Browser surface remains the user’s context |
| Native feature consumes page text | WKWebView plus an explicit extraction policy | Web content is untrusted input; AI does not receive authority |

Do not embed SFSafariViewController as a child view controller or cover it with an app-owned overlay. Do not use WKWebView merely to recreate Safari when Safari Services is the correct visible, system-managed route. Do not use a web view as an authentication substitute when ASWebAuthenticationSession is the intended route.

## Safari Services: visible, standard, and deliberately opaque

SFSafariViewController presents a self-contained web interface inside the app. It provides Safari behaviors such as Reader, AutoFill, fraudulent-website warning, content blocking, navigation controls, and a route to open the page in Safari.

The app should use it when:

- the user needs to see the page;
- the app does not need to inspect or alter the page;
- a standard browser surface is more trustworthy than a custom web shell;
- the feature is support, terms, documentation, or a user-requested page.

The app should not expect:

- DOM access;
- page JavaScript results;
- browsing history or AutoFill data;
- website data access;
- reliable observation of every user interaction.

SFSafariViewController’s delegate can report lifecycle events such as initial-load completion, dismissal, action-button activity, and opening in the browser. These events are not a page-content bridge.

Apple’s documentation also requires that the controller visibly present information and not be hidden or obscured by other views. Treat this as a product and review constraint, not just a presentation preference.

## WebKit: app-owned content with explicit trust boundaries

WKWebView is the route when the app needs to customize or interact with web content. A WKWebViewConfiguration must be assembled before the web view is created. Configuration choices include:

- website data store;
- user content controller;
- process pool;
- media and preference behavior;
- custom URL-scheme handlers;
- app-bound navigation;
- injected scripts and content rules.

The navigation delegate can allow, cancel, or redirect navigation. The UI delegate handles native UI requested by page content, such as alerts or contextual menus. Neither delegate makes remote web content trusted.

Keep these boundaries visible:

| Boundary | App responsibility |
| --- | --- |
| URL loading | Allowlist scheme, host, and path; reject malformed or unexpected URLs |
| Main-frame versus subframe | Apply different policy to top-level navigation and embedded content |
| JavaScript | Enable only what the feature needs; treat page input as untrusted |
| Native bridge | Accept named, typed, bounded messages from approved origins/frames |
| Cookies | Choose persistent, profile, or nonpersistent storage intentionally |
| Downloads | Verify destination, type, size, and user intent before writing |
| External links | Route to Safari, universal links, or native handling explicitly |
| Web content | Do not let page text silently mutate native state or call privileged APIs |

## WKContentWorld and message bridges

WKContentWorld gives scripts separate JavaScript namespaces. The default client world is the app’s script environment; the page world is the current webpage’s environment; custom worlds can isolate app-specific script groups.

Content worlds do not make the DOM private. DOM changes remain visible to page scripts. A message handler is still an authority boundary:

1. create a bridge with one named purpose;
2. register it for the intended content world;
3. validate the frame and security origin;
4. decode a small, typed payload;
5. reject unknown operations and oversized values;
6. execute only an allowlisted native action;
7. return a typed result where the selected API supports replies;
8. remove handlers when the web view or feature is torn down.

Do not expose a generic evaluate-anything or perform-any-native-action bridge. Do not accept a page-provided URL, file path, account ID, or command merely because it came through a handler.

## Website data and identity

WKWebsiteDataStore controls cookies, caches, and other website data:

| Store | Use |
| --- | --- |
| default | Normal persistent browsing or app web content that intentionally keeps state |
| nonpersistent | Private or sensitive flow that should not write website data to disk |
| identifier-backed persistent store | Separate profile or account boundary, with explicit lifecycle |
| cookie store | Narrow cookie inspection/management when the feature actually needs it |

Assign the data store to the configuration before creating the WKWebView. A later copy of the configuration does not reconfigure the existing web view.

A nonpersistent store reduces local retention; it does not make a website safe, anonymous, or free of network-side records. A persistent store can improve continuity; it also creates deletion, account-switching, and logout obligations.

SFSafariViewController owns its browser interaction and does not expose the app’s access to Safari website data. Use ASWebAuthenticationSession, not ad-hoc cookie sharing, for web authentication.

## App-bound navigation

WKWebViewConfiguration can limit navigation to pages within the app’s domain. Use this when the product has a defined first-party web boundary and the selected target supports the required app-bound configuration.

Record:

- the exact first-party domains;
- navigation behavior for redirects and third-party identity providers;
- whether a login flow belongs in ASWebAuthenticationSession instead;
- what happens when a page navigates outside the allowed domain;
- how web content that needs external resources is handled;
- the final configuration in the signed target.

App-bound navigation is not a replacement for URL allowlisting, server-side authorization, or origin validation.

## ASWebAuthenticationSession

Use ASWebAuthenticationSession for authentication through a web service:

1. construct the provider’s HTTPS authorization URL;
2. choose a callback matcher for the expected custom scheme or HTTPS host/path;
3. start the session from a user-initiated authentication action;
4. let the system show the authentication domain and consent UI;
5. receive the callback URL in the completion handler;
6. validate the callback against the expected state, redirect, and server contract;
7. exchange the authorization result through the provider’s secure flow;
8. store only the app’s resulting credential according to its account policy.

The callback URL is a transport result, not proof that a user account is authorized for every app operation. A canceled session, provider error, mismatched callback, or stale state must remain a recoverable authentication failure.

Use prefersEphemeralWebBrowserSession when the product wants to ask for a private browser session and the selected target supports it. Do not promise that ephemeral mode erases server-side records or guarantees a new identity at the provider.

## Associated domains and universal links

Associated domains establish a verified relationship between an app and a website. The target’s Associated Domains capability produces an entitlement containing service-domain entries such as:

- applinks for universal links;
- webcredentials for shared credentials;
- activitycontinuation for Handoff;
- appclips for App Clip association;
- authsrv for web authentication browser support where applicable.

The website must serve the Apple App Site Association file over HTTPS using the required path and valid server configuration. The app and website entries must match.

Universal-link handling should:

1. receive the NSUserActivity or scene continuation;
2. verify the activity type and HTTP/HTTPS URL;
3. parse URL components with Foundation APIs;
4. validate host, path, query, and allowed action;
5. reject malformed or dangerous parameters;
6. convert the URL to a typed native route;
7. require authorization before sensitive reads or writes;
8. preserve a browser fallback when the app is not installed.

A universal link is an entry point, not authorization. Never let a URL directly delete data, expose a private record, or apply an irreversible AI proposal.

Development alternate modes for associated domains are not release configuration. Remove development query parameters and verify the final signed entitlement before submission.

## Native shell and Liquid Glass

For WKWebView, keep the native shell responsible for:

- title, loading/error state, back/forward/close actions;
- account and privacy status;
- download/share/export confirmation;
- native route changes and universal-link handoff;
- accessibility labels and focus return;
- app-owned AI review controls.

Use Liquid Glass only around app-owned controls where it improves grouping. Do not place a glass overlay over a Safari-managed page or pretend that remote HTML is an Apple system surface. In a WKWebView shell, preserve the website’s readable content area and keep native controls visually distinct from web content.

When Reduce Transparency, increased contrast, large text, VoiceOver, or keyboard navigation is active, the native shell must still communicate loading, errors, external handoff, and destructive-action confirmation.

## On-device AI over web content

AI can help with:

- summarizing a user-requested page;
- extracting a bounded list of visible items;
- proposing a native bookmark or note;
- explaining a selected passage;
- mapping a verified universal link to a native destination.

AI must not:

- treat arbitrary page instructions as developer or system instructions;
- receive cookies, authentication headers, hidden DOM, or full browsing history by default;
- navigate to a model-selected domain without policy;
- submit a form, purchase, send a message, or change native data without deterministic validation and confirmation;
- claim that a page, provider, or authentication result is trustworthy solely because a model summarized it.

Use:

user selection -> origin and frame check -> bounded text extraction -> redaction -> typed AI proposal -> user review -> deterministic native action

Remote page text is data. It is not authority.

## Platform and lifecycle notes

- SFSafariViewController behavior differs on Mac Catalyst and compatible iPhone/iPad apps running in visionOS; verify the target’s presentation path.
- WKWebView processes can terminate or reload; persist only the state the product needs and restore navigation carefully.
- Web content, downloads, cookies, and authentication callbacks can outlive the visible view; define teardown and logout behavior.
- Network reachability, provider redirects, server certificates, content-security policy, and third-party content remain external dependencies.
- A browser page loaded in a simulator does not prove universal links, real provider callbacks, cookie policy, or physical-device presentation.

## Proof boundary

| Claim | Required evidence |
| --- | --- |
| Safari-managed page is presented | Named physical target, visible SFSafariViewController surface, dismissal |
| WKWebView route works | Target configuration, navigation delegate, real page fixture, recovery states |
| Bridge is bounded | Origin/frame/payload tests, handler teardown, rejected unauthorized messages |
| Private data is nonpersistent | Runtime data-store choice and disk/data-lifecycle test |
| Authentication works | Real provider sandbox, consent UI, callback, state/redirect validation, token result |
| Universal link works | Signed entitlement, AASA/server validation, physical tap, native route |
| App-bound domain works | Final configuration, allowed/blocked navigation scenarios |
| AI is safe | Redacted extraction, prompt-injection fixture, typed proposal, confirmation, rejection |
| Accessibility works | VoiceOver, Dynamic Type, alternate-input, contrast, web/native focus tasks |
| Release is ready | Final signed target, domains/entitlements, privacy review, physical/provider evidence |

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
- [Authentication Services](https://developer.apple.com/documentation/authenticationservices)
- [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession)
- [ASWebAuthenticationSession.Callback](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession/callback)
- [Authenticating a user through a web service](https://developer.apple.com/documentation/authenticationservices/authenticating-a-user-through-a-web-service)
- [Configuring an associated domain](https://developer.apple.com/documentation/xcode/configuring-an-associated-domain)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Allowing apps and websites to link to your content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content)
- [Supporting universal links in your app](https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
