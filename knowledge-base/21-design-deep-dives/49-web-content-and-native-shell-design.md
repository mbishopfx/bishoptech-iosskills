# Web content, native shell, and verified handoff design

Web features feel native when the app makes ownership obvious. Safari Services owns a standard browsing surface; WebKit embeds app-owned content; Authentication Services owns a sign-in session; associated domains verify a website-to-app route. The visual design should follow those boundaries instead of flattening them into one fake browser.

## Begin with the user’s web intent

| Intent | Best surface | First design question |
| --- | --- | --- |
| Read support or terms | SFSafariViewController | Can the person see the domain and use standard browser controls? |
| Browse app-owned content | WKWebView | Which navigation, data, and native actions are allowed? |
| Sign in | ASWebAuthenticationSession | What provider, callback, cancellation, and account state are visible? |
| Open a shared link | Universal link or browser fallback | What native route is safe for this exact URL? |
| Summarize a page | WKWebView or selected text | What content was selected, redacted, and approved for on-device processing? |

Do not make the user believe that the app can inspect an SFSafariViewController page when it cannot. Do not make an embedded WKWebView look like a security boundary when it is loading arbitrary remote content.

## Surface ownership

| Surface | App owns | System or website owns |
| --- | --- | --- |
| Safari Services page | Presentation, entry URL, dismissal, app-level context | Browser controls, page interaction, website data, security indicators |
| WKWebView page | Configuration, navigation policy, delegates, bridge, shell | HTML/CSS/JavaScript behavior and remote content |
| Auth session | Start intent, provider choice, callback validation, account result | Consent UI, browser session, provider page, callback delivery |
| Universal-link route | URL validation, native destination, authorization | Website association and system link dispatch |
| Native AI review | Proposed action, confirmation, outcome state | Model output, which remains untrusted until validated |

Use an explicit state label such as “Opening secure sign-in,” “Reading support page,” or “Returning to the app” instead of exposing implementation jargon.

## Native shell anatomy

For an app-owned WKWebView feature, a compact native shell should contain:

- a clear title or domain label;
- back, forward, reload, close, or done actions appropriate to the feature;
- loading and failure status;
- a visible external-browser action when the product allows it;
- account/privacy state when cookies or authentication are involved;
- a bounded download/share action;
- a native AI action that names the selected scope;
- a focus target for returning after navigation or a callback.

Keep the web page’s content area primary. Do not stack multiple translucent navigation bars over remote content. A single app-owned glass group around controls is enough.

## Safari Services design

SFSafariViewController already supplies a standard browser surface. Design around it:

- use a full-screen or supported modal presentation;
- keep the page visible and unobscured;
- explain why the page is opening when the action is not obvious;
- use the Done action and delegate completion to return to app context;
- do not add a fake address bar, fake Safari toolbar, or DOM-driven overlay;
- make support and terms pages readable at Dynamic Type sizes;
- preserve the user’s browser mental model when a link opens in Safari.

If the app needs to style the web page, inspect content, or coordinate page actions, switch to WKWebView and own the additional security and accessibility work.

## WKWebView trust tiers

Design the web feature as one of three tiers:

| Tier | Content | Native power |
| --- | --- | --- |
| First-party | Controlled app domain and reviewed pages | Typed, narrow bridge; app-bound navigation where appropriate |
| Partner | Known service with a documented integration | Explicit host/path rules and limited actions |
| Untrusted | Arbitrary user-selected or external page | Read-only viewing, selected text, or no native bridge |

Never let a Tier 3 page call the same native actions as Tier 1. A visual similarity between pages is not an identity signal.

## Loading, blocked, and offline states

Show states that tell the truth:

| State | UI |
| --- | --- |
| Preparing | Progress and the destination context |
| Loading | Page skeleton or progress without false content |
| Loaded | Content plus available native actions |
| Redirecting | Explain the new destination if host policy changes |
| Blocked | Say that the destination is outside the feature’s allowed boundary |
| Authentication required | Offer secure sign-in, not a raw login form in the page shell |
| Offline | Offer retry, cached native content, or browser fallback when valid |
| Process terminated | Restore only safe navigation state and revalidate identity |
| Canceled | Return to the previous native state without claiming success |

Avoid an infinite spinner. Keep external URL, error details, cookies, and authentication data out of user-visible diagnostics unless the feature needs them.

## Web authentication design

The sign-in sequence should be:

native sign-in intent -> provider domain explanation -> ASWebAuthenticationSession -> callback or cancel -> validation -> account state

The native UI should identify:

- the provider or domain;
- why sign-in is needed;
- what a successful callback unlocks;
- how cancellation differs from an invalid login;
- which account is now active;
- how to sign out and clear local web/account state.

Do not put a secret token in a universal link or use a page bridge as the account authority. A callback is a handoff; the app still validates it and the server still decides account authorization.

Ephemeral sessions can be offered for a privacy-sensitive flow, but the UI should not promise that the provider forgets the interaction or that no server-side record exists.

## Associated domains and link design

Design links as reversible, typed routes:

1. show or receive the HTTPS URL;
2. verify the associated domain and activity context;
3. parse host/path/query;
4. render a safe preview if the destination is consequential;
5. require app authorization;
6. route to a native screen;
7. preserve a web fallback for unsupported or unauthenticated cases.

Avoid generic “Open” buttons that hide whether the person is entering a browser, an auth session, or a native action. For high-impact links, include the destination and intended action in plain language.

## Liquid Glass and web content

Liquid Glass should express app-owned controls, not erase the difference between native and remote content:

- use it for a compact native toolbar, status pill, or AI review action;
- keep text, focus, and progress readable over unpredictable web colors;
- do not overlay glass across an SFSafariViewController;
- do not wrap the entire WKWebView in nested translucent cards;
- provide solid contrast and reduced-transparency fallbacks;
- keep destructive actions in a stable native confirmation surface.

If web content already uses transparency, choose a stable native background behind controls. The page’s CSS is not an Apple system material.

## AI review surface

Use a review card that names:

- the source domain;
- the selected passage or visible scope;
- what the model found;
- what it proposes to do;
- whether the action changes native data;
- the exact Apply, Copy, Save, Open, or Cancel action.

Examples:

- “Summarize the selected section” stays read-only.
- “Save this product” creates a typed bookmark after confirmation.
- “Open the account page” must pass URL policy.
- “Import this event” becomes a draft requiring review, not an automatic calendar write.

Show uncertainty when the page is incomplete, blocked, localized differently, or changed during analysis.

## Accessibility and alternate input

Test the native shell and the page separately:

- VoiceOver reaches web content and native controls in a predictable order;
- focus returns to the initiating control after auth or dismissal;
- Dynamic Type does not hide domain, error, or confirmation text;
- Voice Control can say Back, Done, Retry, Open in Safari, and Cancel;
- Switch Control can reach navigation and recovery actions;
- reduced transparency and increased contrast preserve state meaning;
- web content’s own accessibility is not assumed from the native shell;
- keyboard and pointer users have a non-gesture path;
- localized domains, long titles, right-to-left layout, and error text remain clear.

## Design proof

Review a complete task, not just an attractive screenshot:

- open a support page in SFSafariViewController;
- navigate a first-party WKWebView page;
- attempt a blocked external navigation;
- load a page with a process/data-store failure;
- sign in, cancel, and return through a real provider callback;
- tap a universal link with valid and malformed parameters;
- switch account and clear the intended web state;
- review a prompt-injection fixture and reject unsafe AI action;
- complete the task with VoiceOver and Dynamic Type;
- run with reduced transparency and a slow/offline network.

## Sources

- [Safari Services](https://developer.apple.com/documentation/safariservices)
- [SFSafariViewController](https://developer.apple.com/documentation/safariservices/sfsafariviewcontroller)
- [SFSafariViewControllerDelegate](https://developer.apple.com/documentation/safariservices/sfsafariviewcontrollerdelegate)
- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [WKWebViewConfiguration](https://developer.apple.com/documentation/webkit/wkwebviewconfiguration)
- [WKWebsiteDataStore](https://developer.apple.com/documentation/webkit/wkwebsitedatastore)
- [WKUserContentController](https://developer.apple.com/documentation/webkit/wkusercontentcontroller)
- [WKContentWorld](https://developer.apple.com/documentation/webkit/wkcontentworld)
- [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession)
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
