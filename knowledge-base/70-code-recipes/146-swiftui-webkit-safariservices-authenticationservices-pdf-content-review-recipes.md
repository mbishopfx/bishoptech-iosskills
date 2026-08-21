# SwiftUI WebKit, SafariServices, AuthenticationServices, PDF, and content-handoff review recipes

These are compile-oriented Swift sketches for a named iOS target. They are not claimed to compile in this documentation-only workspace and they do not prove website trust, browser privacy, authentication, passkey registration, server verification, PDF fidelity, link-preview freshness, Associated Domains, Universal Links, Handoff, accessibility, physical-device behavior, or release readiness.

Read the [content-handoff review](../42-framework-deep-dives/103-swiftui-webkit-safariservices-authenticationservices-pdf-content-review.md), [design guide](../21-design-deep-dives/131-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-design.md), [route](../50-capability-recipes/134-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-route.md), and [proof matrix](../60-verification/128-swiftui-webkit-safariservices-authenticationservices-pdf-content-review-proof-matrix.md) first. Verify every API shape and availability against the target SDK.

## Recipe 1: Model a content route and trust decision

Keep the route decision explicit. A URL is data until the app has validated its scheme, host, path, and current user intent.

~~~swift
import Foundation

struct ContentURL: Sendable, Hashable {
    let original: URL
    let scheme: String
    let host: String
    let path: String
}

enum ContentSurface: Sendable, Equatable {
    case safari
    case controlledWebView
    case authentication
    case universalLink
    case handoff
    case nativeDocument
    case reject(reason: String)
}

struct ContentRoute: Sendable, Equatable {
    let url: ContentURL
    let surface: ContentSurface
    let sourceRevision: String
    let requiresAccount: Bool
}

enum ContentError: Error {
    case invalidURL
    case unsupportedScheme
    case untrustedHost
    case untrustedPath
    case staleRoute
    case missingAuthorization
}
~~~

Do not let model output, query parameters, JavaScript, or a callback token choose a native destination without passing through the same route parser.

## Recipe 2: Validate an HTTPS route with an allowlist

Use an allowlist owned by the feature. Do not use substring checks or accept a host merely because it contains the expected domain.

~~~swift
import Foundation

struct URLPolicy: Sendable {
    let hosts: Set<String>
    let pathPrefixes: [String]
    let allowedSchemes: Set<String> = ["https"]

    func validate(_ url: URL) throws -> ContentURL {
        guard
            let scheme = url.scheme?.lowercased(),
            allowedSchemes.contains(scheme),
            let rawHost = url.host
        else {
            throw ContentError.unsupportedScheme
        }

        let host = rawHost.lowercased()
        guard hosts.contains(host) else {
            throw ContentError.untrustedHost
        }

        let path = url.path.isEmpty ? "/" : url.path
        guard pathPrefixes.contains(where: path.hasPrefix) else {
            throw ContentError.untrustedPath
        }

        return ContentURL(
            original: url,
            scheme: scheme,
            host: host,
            path: path
        )
    }
}
~~~

Also decide how to handle fragments, user information, ports, redirects, internationalized domains, and query values. Log the decision without logging credentials, authorization codes, or full sensitive URLs.

## Recipe 3: Build WKWebViewConfiguration before the view

Select the website data policy before constructing the web view. Persistent storage, nonpersistent storage, and profile stores have different product and privacy consequences.

~~~swift
import WebKit

func makeWebViewConfiguration(
    persistent: Bool,
    userContentController: WKUserContentController
) -> WKWebViewConfiguration {
    let configuration = WKWebViewConfiguration()
    configuration.websiteDataStore = persistent
        ? .default()
        : .nonPersistent()
    configuration.userContentController = userContentController
    configuration.preferences.javaScriptCanOpenWindowsAutomatically = false
    return configuration
}

func makeWebView(
    persistent: Bool,
    userContentController: WKUserContentController,
    frame: CGRect = .zero
) -> WKWebView {
    let configuration = makeWebViewConfiguration(
        persistent: persistent,
        userContentController: userContentController
    )
    return WKWebView(frame: frame, configuration: configuration)
}
~~~

Configure the data store, user scripts, message handlers, app-bound domain policy, media behavior, and navigation delegates as one reviewable unit. Do not rely on a later mutation to retrofit a privacy policy after the web view has started loading.

## Recipe 4: Keep navigation policy narrow

Navigation decisions are asynchronous. Reject unsupported schemes and hand off external destinations deliberately.

~~~swift
import WebKit

final class NavigationPolicy: NSObject, WKNavigationDelegate {
    private let policy: URLPolicy
    private let onExternalURL: @MainActor (URL) -> Void

    init(
        policy: URLPolicy,
        onExternalURL: @escaping @MainActor (URL) -> Void
    ) {
        self.policy = policy
        self.onExternalURL = onExternalURL
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

        do {
            _ = try policy.validate(url)
            decisionHandler(.allow)
        } catch {
            Task { @MainActor in
                onExternalURL(url)
            }
            decisionHandler(.cancel)
        }
    }

    func webView(
        _ webView: WKWebView,
        didFail navigation: WKNavigation!,
        withError error: Error
    ) {
        // Map cancellation, offline, server, and policy errors separately.
    }
}
~~~

Also validate redirects and server responses as part of the target’s tests. A delegate method existing in source is not proof that every route is constrained.

## Recipe 5: Wrap WKWebView in SwiftUI with lifecycle ownership

Create the view once for a route identity and keep navigation work cancellable. The wrapper should not recreate the browser on every SwiftUI body recomputation.

~~~swift
import SwiftUI
import WebKit

struct ControlledWebView: UIViewRepresentable {
    let url: URL
    let identity: String
    let policy: URLPolicy
    let onExternalURL: @MainActor (URL) -> Void

    func makeCoordinator() -> NavigationPolicy {
        NavigationPolicy(
            policy: policy,
            onExternalURL: onExternalURL
        )
    }

    func makeUIView(context: Context) -> WKWebView {
        let view = makeWebView(
            persistent: false,
            userContentController: WKUserContentController()
        )
        view.navigationDelegate = context.coordinator
        return view
    }

    func updateUIView(_ view: WKWebView, context: Context) {
        guard view.url != url else { return }
        view.load(URLRequest(url: url))
    }

    static func dismantleUIView(
        _ view: WKWebView,
        coordinator: NavigationPolicy
    ) {
        view.stopLoading()
        view.navigationDelegate = nil
        view.uiDelegate = nil
    }
}
~~~

Use an explicit identity in the surrounding SwiftUI route when a new browser session is required. Clear delegates, handlers, tasks, and temporary data when the scene or account changes.

## Recipe 6: Add a typed JavaScript bridge

Keep the bridge narrow and validate every message. A web page must not gain arbitrary native invocation.

~~~swift
import WebKit

struct WebMessage: Decodable, Sendable {
    let version: Int
    let action: String
    let requestID: String
}

final class BridgeHandler: NSObject, WKScriptMessageHandler {
    private let onMessage: @MainActor (WebMessage) -> Void

    init(onMessage: @escaping @MainActor (WebMessage) -> Void) {
        self.onMessage = onMessage
    }

    func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage
    ) {
        guard message.name == "appBridge" else { return }
        guard let body = message.body as? String else { return }
        guard let data = body.data(using: .utf8) else { return }

        do {
            let decoded = try JSONDecoder().decode(
                WebMessage.self,
                from: data
            )
            guard decoded.version == 1 else { return }
            Task { @MainActor in
                onMessage(decoded)
            }
        } catch {
            // Record a redacted parse failure and do not invoke native work.
        }
    }
}
~~~

Register only the message names required by the feature. Reject stale route revisions, unexpected origins, duplicate request identifiers, and requests that would use credentials, delete data, navigate externally, or share content without explicit user review.

## Recipe 7: Present SFSafariViewController as a visible browser surface

Use SafariServices for public browsing where the app does not need to read or alter page content. It is a visible, system-provided surface.

~~~swift
import SafariServices
import SwiftUI

struct SafariSheet: UIViewControllerRepresentable {
    let url: URL

    func makeUIViewController(
        context: Context
    ) -> SFSafariViewController {
        SFSafariViewController(url: url)
    }

    func updateUIViewController(
        _ controller: SFSafariViewController,
        context: Context
    ) {}
}
~~~

Present it modally and visibly. Do not hide controls, embed it as an obscured child, scrape its website data, or treat its dismissal callback as proof that a server-side action completed. Use WKWebView when the app must own the content UI and interaction.

## Recipe 8: Start web authentication with a callback boundary

The callback is only the handoff from the browser session. The server must exchange and verify the authorization result before the app creates an account session.

~~~swift
import AuthenticationServices
import Foundation

struct WebAuthResult: Sendable {
    let callbackURL: URL
}

@MainActor
final class WebAuthCoordinator: NSObject {
    private var session: ASWebAuthenticationSession?

    func authenticate(
        authorizationURL: URL,
        callbackScheme: String
    ) async throws -> WebAuthResult {
        try await withCheckedThrowingContinuation { continuation in
            let session = ASWebAuthenticationSession(
                url: authorizationURL,
                callbackURLScheme: callbackScheme
            ) { [weak self] callbackURL, error in
                self?.session = nil
                if let error {
                    continuation.resume(throwing: error)
                } else if let callbackURL {
                    continuation.resume(
                        returning: WebAuthResult(callbackURL: callbackURL)
                    )
                } else {
                    continuation.resume(
                        throwing: ContentError.invalidURL
                    )
                }
            }

            self.session = session
            guard session.start() else {
                self.session = nil
                continuation.resume(
                    throwing: ContentError.missingAuthorization
                )
                return
            }
        }
    }
}
~~~

Add cancellation handling around the continuation in the real target. Validate the callback scheme, state, nonce, PKCE result, issuer, audience, expiry, and account binding. Keep authorization codes and tokens out of logs and URL display.

## Recipe 9: Use SwiftUI WebAuthenticationSession when available

The SwiftUI environment provides a system-managed web authentication route for a SwiftUI app. Keep the callback and server verification contract visible in the model.

~~~swift
import AuthenticationServices
import SwiftUI

struct SignInView: View {
    @Environment(\.webAuthenticationSession) private var webAuthentication
    @State private var authURL: URL?
    @State private var authError: String?

    var body: some View {
        Button("Sign in") {
            guard let authURL else { return }
            Task {
                do {
                    let callback = try await webAuthentication.authenticate(
                        using: authURL,
                        callbackURLScheme: "example-app"
                    )
                    // Send the callback to the server for verification.
                    _ = callback
                } catch {
                    authError = String(describing: error)
                }
            }
        }
    }
}
~~~

Confirm the exact environment API and availability in the target SDK. A callback URL scheme is not a substitute for server-side verification or current account binding.

## Recipe 10: Use a platform passkey provider

Passkey requests need a server challenge, a relying-party identifier, a presentation anchor, and a server verifier. The native completion is not itself proof of account authentication.

~~~swift
import AuthenticationServices

@MainActor
final class PasskeyCoordinator: NSObject,
    ASAuthorizationControllerDelegate,
    ASAuthorizationControllerPresentationContextProviding {

    private var continuation:
        CheckedContinuation<ASAuthorization, Error>?

    func presentationAnchor(
        for controller: ASAuthorizationController
    ) -> ASPresentationAnchor {
        // Return the active window for the named scene.
        fatalError("Provide the active scene presentation anchor")
    }

    func authorizationController(
        controller: ASAuthorizationController,
        didCompleteWithAuthorization authorization: ASAuthorization
    ) {
        continuation?.resume(returning: authorization)
        continuation = nil
    }

    func authorizationController(
        controller: ASAuthorizationController,
        didCompleteWithError error: Error
    ) {
        continuation?.resume(throwing: error)
        continuation = nil
    }

    func assertion(
        relyingParty: String,
        challenge: Data
    ) async throws -> ASAuthorization {
        try await withCheckedThrowingContinuation { continuation in
            self.continuation = continuation
            let provider =
                ASAuthorizationPlatformPublicKeyCredentialProvider(
                    relyingPartyIdentifier: relyingParty
                )
            let request = provider.createCredentialAssertionRequest(
                challenge: challenge
            )
            let controller = ASAuthorizationController(
                authorizationRequests: [request]
            )
            controller.delegate = self
            controller.presentationContextProvider = self
            controller.performRequests()
        }
    }
}
~~~

The exact request and response properties should be compiled against the target SDK. Send the credential response to the server, verify the challenge and origin there, and only then update the app account or local unlock state.

## Recipe 11: Gate passkeys in web content by origin and association

Keep the web origin, relying party, Associated Domains entitlement, AASA file, and server verifier in one configuration record.

~~~swift
struct PasskeyWebContract: Sendable {
    let websiteOrigin: URL
    let relyingPartyIdentifier: String
    let associatedDomain: String
    let appIdentifier: String
    let serverVerifierRevision: String

    var isConsistent: Bool {
        websiteOrigin.scheme == "https"
            && websiteOrigin.host == relyingPartyIdentifier
            && associatedDomain.hasPrefix("webcredentials:")
            && !appIdentifier.isEmpty
            && !serverVerifierRevision.isEmpty
    }
}
~~~

For a WKWebView passkey flow, prove the deployed association and website behavior on a physical device. A local AASA file, a matching string in source, or a successful web page load does not prove credential availability.

## Recipe 12: Open a PDF from authorized data

Keep security-scoped access and document ownership explicit. Do not assume a file-provider URL remains usable after the access scope ends.

~~~swift
import PDFKit
import UniformTypeIdentifiers

struct OpenPDFResult: Sendable {
    let document: PDFDocument
    let sourceURL: URL
    let didStartSecurityScope: Bool
}

func openPDF(from url: URL) throws -> OpenPDFResult {
    let didStart = url.startAccessingSecurityScopedResource()
    defer {
        if didStart {
            url.stopAccessingSecurityScopedResource()
        }
    }

    guard
        let document = PDFDocument(url: url),
        document.pageCount > 0
    else {
        throw ContentError.invalidURL
    }

    return OpenPDFResult(
        document: document,
        sourceURL: url,
        didStartSecurityScope: didStart
    )
}
~~~

For long-lived work, copy authorized input into an app-owned temporary or document location while access is valid, subject to the user’s privacy and retention policy. Enforce size, page-count, password, and unsupported-content limits before expensive work.

## Recipe 13: Wrap PDFView for SwiftUI review

Use PDFView for viewing and navigation while the SwiftUI layer owns document state, draft annotations, errors, and export confirmation.

~~~swift
import PDFKit
import SwiftUI

struct PDFDocumentView: UIViewRepresentable {
    let document: PDFDocument
    let displayMode: PDFDisplayMode

    func makeUIView(context: Context) -> PDFView {
        let view = PDFView()
        view.autoScales = true
        view.displayMode = displayMode
        view.displayDirection = .vertical
        view.document = document
        return view
    }

    func updateUIView(
        _ view: PDFView,
        context: Context
    ) {
        if view.document !== document {
            view.document = document
        }
        view.displayMode = displayMode
    }
}
~~~

Test page changes, selection, search, annotations, password-protected files, rotation, Dynamic Type around companion controls, VoiceOver labels, and large documents. Do not declare PDF editing complete because a PDFView rendered one fixture.

## Recipe 14: Export to a new PDF and reopen it

Write a new output, then reopen and inspect it before replacing or sharing the source.

~~~swift
import PDFKit

struct PDFOutputInspection: Sendable {
    let pageCount: Int
    let fileSize: Int64
}

func exportAndInspect(
    document: PDFDocument,
    to destination: URL
) throws -> PDFOutputInspection {
    guard document.write(to: destination) else {
        throw ContentError.invalidURL
    }

    let attributes = try FileManager.default.attributesOfItem(
        atPath: destination.path
    )
    let fileSize = (attributes[.size] as? NSNumber)?.int64Value ?? 0
    guard
        let reopened = PDFDocument(url: destination),
        reopened.pageCount == document.pageCount,
        fileSize > 0
    else {
        throw ContentError.invalidURL
    }

    return PDFOutputInspection(
        pageCount: reopened.pageCount,
        fileSize: fileSize
    )
}
~~~

Add fixture assertions for metadata, annotations, permissions, page bounds, links, and expected text/image fidelity. Keep the source and output revisions in the app’s model.

## Recipe 15: Fetch a cancellable rich-link preview

Create one LPMetadataProvider per request, bound it with a timeout, and cancel it when the card disappears.

~~~swift
import LinkPresentation

struct PreviewResult: Sendable {
    let originalURL: URL
    let returnedURL: URL?
    let title: String?
}

func fetchPreview(
    for url: URL,
    timeoutNanoseconds: UInt64 = 6_000_000_000
) async throws -> PreviewResult {
    let provider = LPMetadataProvider()
    provider.shouldFetchSubresources = false

    let metadata = try await withThrowingTaskGroup(
        of: LPLinkMetadata.self
    ) { group in
        group.addTask {
            try await provider.startFetchingMetadata(for: url)
        }
        group.addTask {
            try await Task.sleep(nanoseconds: timeoutNanoseconds)
            throw ContentError.invalidURL
        }
        defer { group.cancelAll() }
        return try await group.next()!
    }

    return PreviewResult(
        originalURL: url,
        returnedURL: metadata.originalURL,
        title: metadata.title
    )
}
~~~

Check the exact async overload in the target SDK. Store original and returned URLs separately, treat title/icon/image as optional untrusted metadata, cache only under a freshness policy, and never interpret a preview as a security or authorization decision.

## Recipe 16: Converge Universal Link and Handoff delivery

Feed URL contexts and user activities through one typed parser so cold and warm scene delivery cannot drift.

~~~swift
import Foundation
import UIKit

enum IncomingContent: Sendable, Equatable {
    case universalLink(URL)
    case handoff(activityType: String, webpageURL: URL?)
}

func parse(
    connectionOptions: UIScene.ConnectionOptions
) -> [IncomingContent] {
    let links = connectionOptions.urlContexts.compactMap {
        IncomingContent.universalLink($0.url)
    }
    let activities = connectionOptions.userActivities.compactMap {
        IncomingContent.handoff(
            activityType: $0.activityType,
            webpageURL: $0.webpageURL
        )
    }
    return links + activities
}
~~~

The real parser must validate the app’s associated host, path, query, route revision, account, and authorization before routing. Handoff payload context is not an authentication assertion.

## Recipe 17: Deliver system events into a SwiftUI coordinator

SwiftUI can receive URL and user-activity events, but the coordinator should own route validation and current-account resolution.

~~~swift
import SwiftUI

struct ContentScene: View {
    @State private var coordinator = ContentRouteCoordinator()

    var body: some View {
        RootContentView(route: coordinator.currentRoute)
            .onOpenURL { url in
                coordinator.receive(url: url)
            }
            .onContinueUserActivity(
                NSUserActivityTypeBrowsingWeb
            ) { activity in
                coordinator.receive(activity: activity)
            }
    }
}

@MainActor
@Observable
final class ContentRouteCoordinator {
    private(set) var currentRoute: ContentRoute?

    func receive(url: URL) {
        // Parse, validate, check account state, then publish a typed route.
    }

    func receive(activity: NSUserActivity) {
        // Validate activity type, webpageURL, handoff revision, and account.
    }
}
~~~

Add a queue for events arriving before the account/session store is ready. Expired, unauthorized, malformed, and unsupported routes need user-facing recovery rather than silent drops.

## Recipe 18: Keep browser/document AI proposals reviewable

On-device AI can summarize or classify a locally available document or a user-approved page. It should propose an operation, not silently navigate, submit, authenticate, share, or delete.

~~~swift
import Foundation

struct ContentSourceRevision: Sendable, Equatable {
    let sourceID: String
    let revision: String
    let capturedAt: Date
}

struct AIContentProposal: Sendable, Equatable {
    let source: ContentSourceRevision
    let modelRevision: String
    let title: String
    let body: String
    let suggestedAction: String?
    let requiresReview: Bool
}

func propose(
    source: ContentSourceRevision,
    modelRevision: String,
    extractedText: String
) async throws -> AIContentProposal {
    guard !extractedText.isEmpty else {
        throw ContentError.invalidURL
    }
    return AIContentProposal(
        source: source,
        modelRevision: modelRevision,
        title: "Review proposal",
        body: extractedText,
        suggestedAction: nil,
        requiresReview: true
    )
}
~~~

Capture the source revision and model revision. Revalidate the current source before applying a user-approved edit or export. Keep model output out of WebKit message handlers and AuthenticationServices decisions.

## Recipe 19: Record the evidence packet

Store proof as structured data so a release review can distinguish source code from system behavior.

~~~swift
struct ContentEvidence: Codable, Sendable {
    let target: String
    let build: String
    let deploymentTarget: String
    let device: String
    let configurationRevision: String
    let associatedDomainsRevision: String?
    let serverVerifierRevision: String?
    let sourceRevision: String
    let modelRevision: String?
    let checks: [Check]

    struct Check: Codable, Sendable {
        let name: String
        let result: String
        let artifact: String
        let recordedAt: Date
    }
}
~~~

Include target settings, signed entitlements, AASA response, server verification result, callback negative cases, browser/data-store policy, PDF fixture results, preview timeout/cancel results, Universal Link/Handoff device runs, accessibility settings, privacy review, archive, and TestFlight evidence. Redact credentials and personal content.

## Recipe 20: Keep Liquid Glass at the native shell boundary

The browser page, PDF page, and system authentication surface remain the content or system authority. Use Liquid Glass for the app-owned navigation and action layer, not as a translucent overlay that reduces readability or obscures system UI.

~~~swift
import SwiftUI

struct ContentShell<Content: View>: View {
    let title: String
    @ViewBuilder let content: () -> Content

    var body: some View {
        NavigationStack {
            content()
                .navigationTitle(title)
                .toolbar {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button("More", systemImage: "ellipsis") {
                            // Present app-owned actions with explicit labels.
                        }
                        .buttonStyle(.glass)
                    }
                }
        }
    }
}
~~~

Verify the exact Liquid Glass APIs and availability in the target SDK. Preserve legibility, hit targets, reduced-transparency behavior, Reduce Motion behavior, keyboard and pointer access, and system authentication visibility.

## Recipe 21: Test the failure paths before the success path

Use fixtures and a physical-device packet for the system-dependent routes.

~~~text
[ ] Unsupported scheme and lookalike host are rejected
[ ] Redirect to an untrusted host is rejected
[ ] WKWebView cancellation cannot publish stale content
[ ] JavaScript bridge rejects malformed and duplicate messages
[ ] Website data is cleared or retained according to the account policy
[ ] SFSafariViewController is visibly presented and dismisses safely
[ ] Auth callback has wrong scheme, state, nonce, expiry, or issuer
[ ] Server rejects an unverified authorization response
[ ] Passkey has missing credential, canceled UI, wrong RP, and bad challenge
[ ] PDF has invalid bytes, password, huge page count, and failed export
[ ] Link metadata times out, cancels, redirects, or returns no title
[ ] Universal Link is cold, warm, unauthorized, stale, and malformed
[ ] Handoff arrives on another device with missing current data
[ ] AI proposal uses stale source revision and requires re-review
[ ] VoiceOver, Dynamic Type, contrast, Reduce Motion, keyboard, pointer,
    and Switch Control remain usable
~~~

## Sources

- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [WKWebViewConfiguration](https://developer.apple.com/documentation/webkit/wkwebviewconfiguration)
- [WKNavigationDelegate](https://developer.apple.com/documentation/webkit/wknavigationdelegate)
- [WKWebsiteDataStore](https://developer.apple.com/documentation/webkit/wkwebsitedatastore)
- [SafariServices](https://developer.apple.com/documentation/safariservices)
- [SFSafariViewController](https://developer.apple.com/documentation/safariservices/sfsafariviewcontroller)
- [AuthenticationServices](https://developer.apple.com/documentation/authenticationservices)
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
