# WebKit, Safari Services, and web-auth capability route

Use this route when an app needs a web surface, a secure web login, or a verified website-to-native handoff. Select one owner for each stage and keep remote content, authentication state, native state, and AI proposals separate.

This is a compile-oriented route sketch. It does not prove provider login, cookie behavior, universal-link dispatch, app-bound navigation, server association, web accessibility, or release readiness.

## Route selector

| Need | Route | Do not add |
| --- | --- | --- |
| Read a visible support or terms page | SFSafariViewController | DOM bridge or hidden overlay |
| Customize page UI or navigation | WKWebView | Unbounded native bridge |
| Authenticate against a web service | ASWebAuthenticationSession | Manual cookie scraping or embedded password form |
| Open a verified HTTPS link in the app | Associated Domains and universal links | Trust in URL text alone |
| Load private app-owned HTML | WKWebView with nonpersistent data store | Persistent cookies by accident |
| Share a web result with native code | Typed WKWebView bridge or selected-text extraction | Generic JavaScript execution endpoint |

## Target register

| Field | Record |
| --- | --- |
| App target | Bundle ID, platform family, deployment target, selected SDK |
| Web owner | Safari Services, WebKit, or Authentication Services |
| Domains | First-party hosts, partner hosts, redirect hosts, blocked hosts |
| Data store | Default persistent, identifier-backed profile, or nonpersistent |
| Bridge | Message names, content world, origin/frame policy, payload schema |
| Auth | Provider, callback matcher, state/nonce/PKCE policy, ephemeral choice |
| Entitlement | Associated Domains entries and final signed values |
| Server | HTTPS, Apple App Site Association, redirect and callback behavior |
| AI | Extraction scope, redaction, model boundary, review and confirmation |
| Accessibility | Native focus, web content behavior, Dynamic Type, alternate input |
| Evidence | Physical device, provider sandbox, link source, signed artifact |

The target register is not runtime proof. Inspect the final signed entitlements and Info.plist values.

## Ownership graph

Native shell -> web-route coordinator -> selected web owner -> navigation/data/auth event -> typed native state

Web page -> validated bridge message -> deterministic native command -> user review if consequential -> domain result

Website link -> associated-domain dispatch -> URL parser -> authorized native route -> screen state

Page selection -> origin/frame check -> bounded extraction -> redaction -> on-device AI proposal -> review -> native action

The app owns:

- route selection, allowlists, native UI, and recoverable state;
- data-store choice and logout/deletion policy;
- bridge schemas and command validation;
- callback validation and account mapping;
- universal-link URL parsing and authorization;
- AI context reduction and proposal application.

The system/framework owns:

- Safari-managed browsing and auth presentation;
- website data storage mechanics;
- process and navigation callbacks;
- associated-domain verification and link dispatch;
- the browser or web provider’s page content.

## Route A: SFSafariViewController

Use for visible browsing without content inspection:

1. validate the initial URL is HTTPS or another supported product route;
2. create the controller with the intended configuration;
3. present it modally using the supported presentation path;
4. do not embed it as a child or obscure it;
5. record initial-load and dismissal events when product state needs them;
6. return to the native screen with a truthful “viewed,” “dismissed,” or “failed” state.

The app should not expect page DOM access, cookies, AutoFill data, browsing history, or arbitrary interaction callbacks.

## Route B: WKWebView

Assemble configuration before web-view creation:

1. choose the data store;
2. create the user content controller;
3. create the process pool policy;
4. add only needed scripts, rules, and handlers;
5. decide the app-bound navigation policy;
6. assign navigation and UI delegates;
7. create the WKWebView with that configuration;
8. load a validated URL request;
9. reconcile navigation, process termination, downloads, and errors.

Navigation policy:

| Event | Decision |
| --- | --- |
| First-party HTTPS main frame | Allow only the expected host/path |
| Partner redirect | Allow only documented hosts and transition states |
| HTTP or malformed URL | Reject or upgrade only under an explicit policy |
| External browser link | Ask the user or route with a supported system API |
| Custom scheme | Allow only registered, typed actions |
| Subframe content | Apply stricter origin and bridge rules |
| Download | Validate type, size, destination, and user initiation |

Do not use navigation success as proof that the page content is authentic or that a backend action completed.

## Route C: data-store policy

Choose the store with the feature:

| Store | Product route |
| --- | --- |
| Default | Persistent app browsing that intentionally retains website state |
| Nonpersistent | Private read, short-lived auth-adjacent page, or sensitive content |
| Identifier-backed persistent | Explicit account/profile partition with deletion and switching |
| Safari Services data store | Safari-managed visible browsing; use only documented operations |

Create and assign the data store before creating WKWebView. On logout or account switch, define which native credentials, cookies, cached data, and navigation state are removed. A nonpersistent store is not an anonymity guarantee.

## Route D: typed web-to-native bridge

Use a narrow message contract:

1. register one handler name per capability;
2. choose defaultClient or a named content world for app-owned scripts;
3. require the expected origin and frame;
4. decode a bounded Codable payload;
5. reject unknown versions and operations;
6. map to a typed domain proposal;
7. require confirmation for writes, payments, account changes, or sharing;
8. return a typed result or error;
9. remove the handler on teardown.

Page scripts can change the DOM even when scripts run in different content worlds. Content worlds are namespaces, not a complete trust model.

## Route E: ASWebAuthenticationSession

Use the system authentication path:

1. construct the provider URL without private account data in logs;
2. create a callback matcher for the expected custom scheme or HTTPS host/path;
3. start from a user action;
4. set the ephemeral preference only when the product intends to request it;
5. handle callback and cancellation separately;
6. validate state, redirect, provider result, and account identity;
7. exchange the result through the provider/server contract;
8. store the app credential in the app’s identity layer;
9. clear transient auth state after completion.

Do not treat a callback URL, visible login page, or handler completion as proof of an authorized account. Do not send full callback URLs to analytics by default.

## Route F: associated domains and universal links

Configure:

1. Associated Domains capability in the intended target;
2. exact service-domain entries;
3. matching Apple App Site Association server data;
4. HTTPS and certificate behavior;
5. scene/app delegate continuation handling;
6. a typed URL parser and authorization gate;
7. browser fallback for unsupported or uninstalled states.

Validate host, path, query, fragment, scheme, and expected action. Treat incoming parameters as untrusted. Use development alternate mode only for development and remove it from the release entitlement.

## Route G: bounded AI over web content

Use an explicit context envelope:

~~~swift
struct WebAIContext: Sendable, Equatable {
    let origin: String
    let title: String?
    let selectedText: String
    let contentVersion: String
}

enum WebProposal: Sendable, Equatable {
    case summarize
    case saveNote(text: String)
    case createBookmark(url: URL)
    case openNativeRoute(String)
}
~~~

Before calling a model:

- confirm the user selected or requested the scope;
- reject hidden DOM, cookies, auth headers, and unrelated frames;
- cap text size and remove sensitive values;
- label remote content as untrusted data;
- use a structured output schema;
- validate every URL, native route, and write action;
- ask for confirmation when the proposal changes native state.

The AI can suggest. The web page, model, or callback cannot become the authority for account, payment, deletion, or privileged native actions.

## Fallback matrix

| Failure | Fallback |
| --- | --- |
| SFSafariViewController unavailable for target | Open the supported browser route or native fallback |
| WKWebView navigation blocked | Explain the allowed domain boundary and offer browser fallback |
| Page process terminates | Restore safe shell state and reload only after policy check |
| Bridge message malformed | Reject and keep the page usable |
| Bridge origin/frame unexpected | Reject and record a redacted diagnostic |
| Download not allowed | Keep the page visible and explain the constraint |
| Auth canceled | Return to signed-out state without a failure claim |
| Auth callback mismatch | Reject and require a new sign-in |
| Associated-domain verification stale | Preserve web route and explain native handoff is unavailable |
| Universal-link parameter invalid | Reject the native action and show a safe destination |
| Web data store unavailable | Use a new safe store or a nonpersistent fallback |
| AI unavailable or unsafe | Keep read-only page and deterministic native actions |

## Evidence route

Capture:

1. final target/SDK, entitlements, URL handlers, and data-store policy;
2. SFSafariViewController visible presentation and dismissal;
3. WKWebView navigation allow/deny and process-recovery scenarios;
4. bridge origin/frame/payload allow and reject fixtures;
5. persistent/nonpersistent data lifecycle and logout/account switch;
6. provider sandbox auth consent, callback, cancel, mismatch, and token result;
7. AASA/associated-domain verification and physical universal-link taps;
8. app-bound allowed/blocked navigation;
9. AI prompt-injection, redaction, typed proposal, confirmation, and rejection;
10. accessibility, reduced transparency, localization, and final signed artifact.

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
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
