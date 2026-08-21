# SwiftUI WebKit, SafariServices, AuthenticationServices, PDF, and content-handoff design

Design this feature as a set of visible trust transitions. People should know whether they are reading a website, signing in, using a passkey, viewing a PDF, opening a link preview, or entering native app content.

This page is the design companion to the [content-handoff review](../42-framework-deep-dives/103-swiftui-webkit-safariservices-authenticationservices-pdf-content-review.md), [route](../50-capability-recipes/134-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-route.md), [proof matrix](../60-verification/128-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-proof-matrix.md), and [recipes](../70-code-recipes/146-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-recipes.md).

## Start with the user’s trust question

| Surface | What the person should understand |
| --- | --- |
| WKWebView | “This is interactive web content inside the app, with the app’s own navigation and privacy rules.” |
| SFSafariViewController | “This is a visible Safari browsing experience; the app is not inspecting the page.” |
| Web authentication | “A system browser is helping me sign in; the app will verify the result.” |
| Passkey | “The system is using a credential for this relying party; the server confirms the account.” |
| PDF | “This is a document; I can read, select, annotate, or export it according to its permissions.” |
| Link preview | “This is fetched metadata for a URL, not a guarantee about the destination.” |
| Universal Link | “This verified website route is opening related native content.” |
| Handoff | “This is context from another device; the app will check my current account and access.” |

Avoid one generic “Continue” button across all of these surfaces. Use verbs such as “Open website,” “Sign in,” “Use passkey,” “Review PDF,” “Open in app,” or “Continue reading.”

## The surface decision should be visible

The first screen can be a small native choice sheet when the product genuinely supports more than one route:

~~~text
Open this content

[Read in Safari]      Visible, private web browsing
[Open in app]         Verified native content
[Preview link]        Fetch title and image only
[Save PDF]            Download and review a document
~~~

Do not present a fake Safari or credential UI. When the correct system surface owns the browser or authentication interaction, let it remain visually obvious.

## WKWebView shell design

Use WKWebView for interactive, app-controlled content:

- native navigation bar with a concise title and source;
- progress indicator that says “Loading page,” not “Verified”;
- visible back/forward/reload controls where appropriate;
- an external-browser action for pages that should leave the app;
- an error state with retry and safe fallback;
- a privacy or profile indicator when cookies/data are isolated;
- a clear route back to native content.

Keep app-owned controls outside the page’s DOM. Do not place a translucent glass overlay over an interactive webpage in a way that blocks text selection, zoom, form fields, or VoiceOver.

If the page can invoke native actions, make the bridge user-visible and scoped. A page message should not silently open a camera, read private files, change account state, or export data.

## Safari view design

SFSafariViewController already supplies address and security affordances, Reader, content blocking, and browser gestures. Present it as a visible modal or supported sheet. Do not embed it inside a fake card or cover its address/security UI.

The app-owned screen before presentation should explain why the website is opening and what returns to the app. The screen after dismissal should not claim that the person completed an action merely because Safari closed.

For terms, support, and public documentation, use a lightweight native launch action. For interactive signed-in content, choose WKWebView or a web-auth route deliberately.

## Sign-in and passkey design

Use the system’s language:

~~~text
Sign in to Example

You’ll continue in a secure browser session.
The website will return you to this app when sign-in finishes.

[Continue]
~~~

For passkeys:

~~~text
Use a passkey for Example

Your device will ask you to confirm with Face ID, Touch ID, or your device passcode.
Example verifies the result before your account opens.

[Use passkey]
~~~

Do not call an account “signed in” until the server has verified the callback, challenge, assertion, issuer, audience, nonce, PKCE, and any provider-specific requirements. Show cancellation and no-credential states as recoverable outcomes.

If the product offers passwords, passkeys, Sign in with Apple, and security keys, let the system sheet communicate the credential choice. Avoid building a custom credential picker that reveals identifiers or makes a system credential look like an app password.

## Authentication callback design

The callback state is operational, not celebratory:

| State | Copy | Action |
| --- | --- | --- |
| Starting | “Opening secure sign-in…” | Cancel |
| System approval | System-owned | Follow system |
| Callback received | “Verifying sign-in…” | Wait |
| Server verified | “Signed in” | Continue |
| User cancelled | “Sign-in cancelled” | Try again or use another method |
| State mismatch | “We couldn’t verify that response” | Restart |
| Provider failure | Plain-language provider error | Retry/recovery |

Never show a callback URL, code, token, or passkey credential ID in the primary UI or accessibility value.

## PDF design

Use PDFView’s native behaviors for reading, zooming, page navigation, selection, and supported annotations. The surrounding SwiftUI shell should provide:

- document title and source;
- page count and current page;
- search and thumbnails where useful;
- permission-aware actions;
- a clear draft-versus-saved edit indicator;
- export or share destination;
- error states for password, unreadable, or security-scoped files.

For a PDF generated or edited by the app, use a staged draft:

~~~text
Original PDF
-> annotation draft
-> review
-> export copy or replace selected file
-> reopen and validate
~~~

Do not overwrite a source document merely because a PDFView annotation exists. A page-rendered preview is not an exported document.

If a PDF contains links, annotations, form fields, or extracted text, treat them as document content. Make user intent explicit before opening external URLs or submitting forms.

## Link preview design

Use a consistent rich-link card:

~~~text
[source icon] example.com
Article title
Short metadata line

[Open link] [Share] [Remove preview]
~~~

Show a loading placeholder, timeout state, and missing-metadata fallback. Attribute the destination and let the person open it through the correct browser or Universal Link route.

Do not use a fetched page title as a verified brand identity. Do not allow a remote image to create a confusing system-like control. Keep the card accessible when the thumbnail fails.

## Universal Links and Handoff design

Native arrival should feel like a continuation of a web task:

1. show the destination context;
2. confirm the current account or invite state;
3. resolve the current entity;
4. show missing, expired, or unauthorized states;
5. route to the app-owned destination.

Do not open private content solely because the URL contains an identifier. A Universal Link verifies a website-to-app association and routes context; it does not replace authentication.

For Handoff, show “Continuing from [device]” only when the app can identify that context safely. If the activity is stale, require a fresh load or offer the web fallback.

## Liquid Glass and content

Use Liquid Glass for app-owned controls:

- a browser toolbar;
- PDF action groups;
- a native review/confirmation bar;
- a link-preview action group;
- a post-auth account destination.

Do not:

- cover SFSafariViewController;
- imitate a passkey or system authentication sheet;
- make untrusted web HTML look like verified native text;
- put bright glass over small PDF text;
- hide the origin or security indicator;
- animate a navigation transition that implies verification before the server confirms it.

Use opaque backgrounds and contrast fallbacks for web content, PDF pages, code fields, and high-contrast settings. The content remains primary; glass is a functional layer.

## Accessibility and input

Every surface should communicate:

- source/origin;
- current task;
- loading or verification state;
- next action;
- failure and recovery.

Support:

- VoiceOver navigation through browser controls and PDF pages;
- Dynamic Type for native shell copy;
- Reduce Motion for page arrival and PDF transitions;
- keyboard shortcuts or focus movement for PDF search/navigation;
- pointer and trackpad actions on iPad and Mac Catalyst;
- Switch Control paths through sign-in, document review, and external handoff;
- accessible names for link thumbnails, passkey actions, and document annotations.

Do not rely on URL text, color, a lock icon, or a motion effect alone to communicate trust.

## Privacy and recovery copy

Be direct:

| Situation | Copy pattern |
| --- | --- |
| Private browsing | “This session won’t keep website data after you leave.” |
| Persistent profile | “This website may keep you signed in on this device.” |
| Web callback error | “We couldn’t verify the sign-in response. Nothing was changed.” |
| PDF password | “This document needs its password to open.” |
| External link | “You’re leaving the app to open this website.” |
| Invalid Universal Link | “This link is unavailable or no longer belongs to your account.” |
| Remote preview failure | “Preview unavailable; open the link to try again.” |

Avoid logging or showing sensitive query parameters, access codes, cookie data, document text, or passkey identifiers.

## Local AI design

For a PDF summary or link classification, show source and revision:

~~~text
Suggested summary
Based on: “Project brief.pdf,” page 3
Generated on device
Needs your review

[Use summary] [Edit] [Discard]
~~~

Do not let a model:

- choose a credential;
- accept an authentication callback;
- open an unvalidated URL;
- submit a PDF form;
- send a document;
- navigate a web bridge;
- unlock an account;
- change a Universal Link destination.

The model may propose; the app and system verify.

## Design checklist

~~~text
[ ] The feature names the correct browser/document/auth surface.
[ ] WKWebView and SFSafariViewController roles are visibly different.
[ ] Authentication callback verification is distinct from callback receipt.
[ ] Passkey UI preserves system credential semantics and server verification.
[ ] PDF draft, export, and replacement destinations are separate.
[ ] Link metadata is attributed and treated as remote/untrusted.
[ ] Universal Link and Handoff arrival validate current account and entity state.
[ ] Liquid Glass groups app-owned controls without hiding content or system chrome.
[ ] VoiceOver, Dynamic Type, Reduce Motion, contrast, keyboard, pointer, and Switch Control work.
[ ] AI proposals identify source/model state and require review for side effects.
[ ] Privacy, logout, data-store deletion, callback logging, and recovery copy are explicit.
~~~

## Sources

- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [WKWebViewConfiguration](https://developer.apple.com/documentation/webkit/wkwebviewconfiguration)
- [WKNavigationDelegate](https://developer.apple.com/documentation/webkit/wknavigationdelegate)
- [WKWebsiteDataStore](https://developer.apple.com/documentation/webkit/wkwebsitedatastore)
- [SFSafariViewController](https://developer.apple.com/documentation/safariservices/sfsafariviewcontroller)
- [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession)
- [WebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/webauthenticationsession)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [PDFKit](https://developer.apple.com/documentation/pdfkit)
- [PDFDocument](https://developer.apple.com/documentation/pdfkit/pdfdocument)
- [PDFView](https://developer.apple.com/documentation/pdfkit/pdfview)
- [Link Presentation](https://developer.apple.com/documentation/linkpresentation)
- [LPMetadataProvider](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Allowing apps and websites to link to your content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content)
- [Supporting universal links in your app](https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app)
- [System events](https://developer.apple.com/documentation/swiftui/system-events)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
