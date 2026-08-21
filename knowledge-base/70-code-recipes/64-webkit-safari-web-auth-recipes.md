# WebKit, Safari Services, and web-auth recipes

These are compile-oriented route sketches for visible Safari-managed pages, app-owned WKWebView content, typed JavaScript bridges, persistent/private data stores, secure web authentication, universal-link routing, and bounded AI over web content.

They are not compiled in this documentation-only workspace and do not prove provider authentication, cookie isolation, website association, universal-link delivery, web accessibility, physical-device behavior, or release readiness. Confirm exact API signatures, availability, entitlements, and target configuration in the selected SDK.

Before copying:

1. Choose SFSafariViewController, WKWebView, or ASWebAuthenticationSession for the actual user intent.
2. Keep authentication separate from arbitrary web browsing.
3. Configure data stores, handlers, delegates, and app-bound policy before creating a web view.
4. Treat every page, callback, bridge message, and model output as untrusted until validated.
5. Test on a physical device with a real provider sandbox and website association.

## Recipe 1: Keep route ownership typed

Use a route enum so a support page cannot silently become an auth or native-action surface:

~~~swift
import Foundation

enum WebRoute: Sendable, Equatable {
    case safari(URL)
    case embedded(URL, policy: EmbeddedPolicy)
    case authentication(URL)
    case universalLink(URL)
}

struct EmbeddedPolicy: Sendable, Equatable {
    let allowedHosts: Set<String>
    let allowsJavaScript: Bool
    let usesPersistentData: Bool
    let allowsNativeBridge: Bool
}

enum WebState: Sendable, Equatable {
    case idle
    case loading(URL)
    case loaded(URL)
    case blocked(URL, reason: String)
    case failed(URL, message: String)
    case canceled
}
~~~

The route coordinator owns transition decisions. Views should render state and invoke typed actions.

## Recipe 2: Present SFSafariViewController visibly

Use Safari Services for content that the app does not inspect:

~~~swift
import SafariServices
import SwiftUI

struct SafariPage: UIViewControllerRepresentable {
    let url: URL
    let onFinish: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onFinish: onFinish)
    }

    func makeUIViewController(
        context: Context
    ) -> SFSafariViewController {
        let configuration = SFSafariViewController.Configuration()
        let controller = SFSafariViewController(
            url: url,
            configuration: configuration
        )
        controller.delegate = context.coordinator
        return controller
    }

    func updateUIViewController(
        _ controller: SFSafariViewController,
        context: Context
    ) {}

    final class Coordinator: NSObject, SFSafariViewControllerDelegate {
        let onFinish: () -> Void

        init(onFinish: @escaping () -> Void) {
            self.onFinish = onFinish
        }

        func safariViewControllerDidFinish(
            _ controller: SFSafariViewController
        ) {
            onFinish()
        }
    }
}
~~~

Present it as a visible, supported modal surface. Do not embed it as a child, inspect its DOM, or place an app-owned overlay over the page.

## Recipe 3: Create a WKWebView with an intentional data store

Configuration choices are made before web-view creation:

~~~swift
import WebKit

@MainActor
func makeEmbeddedWebView(
    privateData: Bool,
    limitsToAppBoundDomains: Bool
) -> WKWebView {
    let configuration = WKWebViewConfiguration()
    configuration.websiteDataStore = privateData
        ? .nonPersistent()
        : .default()
    configuration.limitsNavigationsToAppBoundDomains =
        limitsToAppBoundDomains

    let contentController = WKUserContentController()
    configuration.userContentController = contentController

    let webView = WKWebView(
        frame: .zero,
        configuration: configuration
    )
    webView.allowsBackForwardNavigationGestures = true
    return webView
}
~~~

Record the data-store choice in the target register. A nonpersistent store avoids writing website data to disk, but it does not erase server-side records or make remote content trusted.

## Recipe 4: Keep a host and path allowlist

Use Foundation URL components rather than string-prefix checks:

~~~swift
import Foundation

struct WebURLPolicy: Sendable {
    let allowedHosts: Set<String>
    let allowedPathPrefixes: [String]

    func allows(_ url: URL) -> Bool {
        guard let components = URLComponents(
            url: url,
            resolvingAgainstBaseURL: false
        ),
        components.scheme?.lowercased() == "https",
        let host = components.host?.lowercased(),
        allowedHosts.contains(host)
        else {
            return false
        }

        let path = components.path
        return allowedPathPrefixes.contains { path.hasPrefix($0) }
    }
}
~~~

A URL that passes this policy still does not prove page identity, account authorization, or safe action parameters. Apply server and account policy separately.

## Recipe 5: Gate WKWebView navigation

Keep navigation policy in a delegate, not inside the page:

~~~swift
import WebKit

final class NavigationGate: NSObject, WKNavigationDelegate {
    let policy: WebURLPolicy
    let openExternal: (URL) -> Void

    init(
        policy: WebURLPolicy,
        openExternal: @escaping (URL) -> Void
    ) {
        self.policy = policy
        self.openExternal = openExternal
    }

    func webView(
        _ webView: WKWebView,
        decidePolicyFor navigationAction: WKNavigationAction,
        decisionHandler: @escaping (WKNavigationActionPolicy) -> Void
    ) {
        guard let url = navigationAction.request.url else {
            decisionHandler(.cancel)
            return
        }

        if policy.allows(url) {
            decisionHandler(.allow)
        } else {
            openExternal(url)
            decisionHandler(.cancel)
        }
    }

    func webViewWebContentProcessDidTerminate(
        _ webView: WKWebView
    ) {
        webView.reload()
    }
}
~~~

The reload path is only a sketch. In a real app, restore safe native state first, avoid repeating a destructive navigation, and show an accessible recovery status.

## Recipe 6: Add a bounded content-world bridge

Use one named bridge and typed operations:

~~~swift
import WebKit

struct NativeWebMessage: Decodable, Sendable {
    let version: Int
    let operation: Operation
    let requestID: String

    enum Operation: String, Decodable, Sendable {
        case requestVisibleTitle
        case requestSelectedText
    }
}

final class WebBridge: NSObject, WKScriptMessageHandlerWithReply {
    let originIsAllowed: (WKSecurityOrigin) -> Bool
    let handle: (NativeWebMessage) -> Any?

    init(
        originIsAllowed: @escaping (WKSecurityOrigin) -> Bool,
        handle: @escaping (NativeWebMessage) -> Any?
    ) {
        self.originIsAllowed = originIsAllowed
        self.handle = handle
    }

    func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage,
        replyHandler: @escaping (Any?, String?) -> Void
    ) {
        guard let frameInfo = message.frameInfo.securityOrigin as WKSecurityOrigin?,
              originIsAllowed(frameInfo),
              let body = message.body as? String,
              body.utf8.count <= 16_384,
              let data = body.data(using: .utf8),
              let request = try? JSONDecoder().decode(
                  NativeWebMessage.self,
                  from: data
              ),
              request.version == 1
        else {
            replyHandler(nil, "rejected")
            return
        }

        replyHandler(handle(request), nil)
    }
}

@MainActor
func installBridge(
    on configuration: WKWebViewConfiguration,
    bridge: WebBridge
) {
    configuration.userContentController.add(
        bridge,
        contentWorld: .defaultClient,
        name: "appNative"
    )
}
~~~

Confirm the selected SDK’s reply-handler signature and content-world overload. Validate the security origin, frame, operation, version, request ID, and result shape. Do not expose a generic native command or JavaScript evaluator.

## Recipe 7: Tear down the bridge

Handlers are part of the web view lifecycle:

~~~swift
import WebKit

@MainActor
func removeBridge(
    from webView: WKWebView,
    name: String
) {
    webView.configuration.userContentController
        .removeScriptMessageHandler(
            forName: name,
            contentWorld: .defaultClient
        )
}
~~~

The exact Swift overload can vary by SDK. Pair removal with view dismissal, account switch, feature teardown, and process recovery so a stale handler does not mutate a new route.

## Recipe 8: Start ASWebAuthenticationSession

Use Authentication Services for web sign-in:

~~~swift
import AuthenticationServices

final class WebLoginCoordinator: NSObject,
    ASWebAuthenticationPresentationContextProviding {
    private var session: ASWebAuthenticationSession?
    let presentationAnchor: () -> ASPresentationAnchor
    let finish: (Result<URL, Error>) -> Void

    init(
        presentationAnchor: @escaping () -> ASPresentationAnchor,
        finish: @escaping (Result<URL, Error>) -> Void
    ) {
        self.presentationAnchor = presentationAnchor
        self.finish = finish
    }

    func start(url: URL, callbackScheme: String) {
        let callback = ASWebAuthenticationSession.Callback
            .customScheme(callbackScheme)
        let session = ASWebAuthenticationSession(
            url: url,
            callback: callback
        ) { [weak self] callbackURL, error in
            if let callbackURL {
                self?.finish(.success(callbackURL))
            } else {
                self?.finish(.failure(error ?? CancellationError()))
            }
        }
        session.presentationContextProvider = self
        session.prefersEphemeralWebBrowserSession = true
        self.session = session
        session.start()
    }

    func presentationAnchor(
        for session: ASWebAuthenticationSession
    ) -> ASPresentationAnchor {
        presentationAnchor()
    }

    func cancel() {
        session?.cancel()
        session = nil
    }
}
~~~

The callback must still be validated against the expected state, redirect, provider, and server-side result. Ephemeral preference is a request, not a guarantee that the provider creates a new account or discards all records.

## Recipe 9: Handle a universal link as a typed route

Use URLComponents and an allowlist:

~~~swift
import Foundation

enum NativeLink: Equatable, Sendable {
    case article(id: String)
    case account
}

struct UniversalLinkParser {
    let host = "www.example.com"

    func parse(_ url: URL) -> NativeLink? {
        guard let components = URLComponents(
            url: url,
            resolvingAgainstBaseURL: false
        ),
        components.scheme == "https",
        components.host == host
        else {
            return nil
        }

        switch components.path {
        case "/account":
            return .account
        case "/article":
            guard let id = components.queryItems?
                .first(where: { $0.name == "id" })?.value,
                id.count <= 128,
                id.allSatisfy({ $0.isLetter || $0.isNumber || $0 == "-" })
            else {
                return nil
            }
            return .article(id: id)
        default:
            return nil
        }
    }
}
~~~

The associated-domain entitlement and server association must be configured separately. A successfully parsed link still needs native authorization before accessing private data or applying a side effect.

## Recipe 10: Keep the associated-domain entitlement explicit

Use target configuration for the intended services:

~~~xml
<key>com.apple.developer.associated-domains</key>
<array>
    <string>applinks:www.example.com</string>
    <string>webcredentials:www.example.com</string>
</array>
~~~

The domain and service values are fixtures. The final signed artifact must contain the exact target-specific values, and the website must serve the matching Apple App Site Association file. Remove development alternate-mode query parameters before release.

## Recipe 11: Bound AI extraction and native proposals

Keep remote page data and native actions typed:

~~~swift
struct WebSelection: Sendable, Equatable {
    let origin: String
    let title: String?
    let visibleText: String
    let selectedText: String?
}

enum WebNativeProposal: Sendable, Equatable {
    case summarize
    case saveNote(String)
    case bookmark(URL)
    case openRoute(String)
}

enum WebProposalError: Error {
    case originNotAllowed
    case tooLarge
    case hiddenOrUnselectedContent
    case invalidURL
    case confirmationRequired
}

struct WebProposalValidator {
    let allowedHosts: Set<String>

    func validate(
        _ proposal: WebNativeProposal,
        selection: WebSelection,
        confirmed: Bool
    ) throws {
        guard allowedHosts.contains(selection.origin) else {
            throw WebProposalError.originNotAllowed
        }
        guard selection.visibleText.utf8.count <= 64_000 else {
            throw WebProposalError.tooLarge
        }
        switch proposal {
        case .summarize:
            return
        case let .saveNote(text):
            guard confirmed, !text.isEmpty else {
                throw WebProposalError.confirmationRequired
            }
        case let .bookmark(url):
            guard url.scheme == "https",
                  let host = url.host,
                  allowedHosts.contains(host)
            else {
                throw WebProposalError.invalidURL
            }
        case .openRoute:
            guard confirmed else {
                throw WebProposalError.confirmationRequired
            }
        }
    }
}
~~~

Do not include cookies, authorization headers, hidden DOM, browsing history, or page-provided instructions as model authority. Prompt-injection fixtures are required proof.

## Recipe 12: Record web evidence without secrets

Keep a semantic evidence record:

~~~swift
struct WebEvidence: Sendable, Equatable {
    let route: String
    let host: String?
    let state: String
    let messageName: String?
    let callbackReceived: Bool
    let nativeResult: String
    let timestamp: Date
    let device: String
}
~~~

Pair it with the exact target, provider sandbox, domain association state, physical device, and signed artifact. Never substitute a callback URL, cookie dump, or screenshot for the required authorization and release evidence.

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
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
