# SwiftUI AuthenticationServices, passkey, and identity recipes

These recipes target the installed iOS 26.4 SDK and are intentionally small.
They show API shape and state handoff, not a complete authentication system.
Every production flow still needs a server-created challenge or nonce, signed
target capabilities, associated-domain/AASA configuration, secure logging,
server verification, account recovery, accessibility, physical-device proof,
and release evidence.

The snippets are independent compile-sized route sketches. Do not put sample
challenge bytes, user IDs, credential IDs, or provider responses into a real
account without server validation.

## 1. Retain an authorization coordinator and delegate

Keep the coordinator alive through the system callback and provide the active
scene’s presentation anchor. A delegate callback is a pending input to server
verification, not a local session grant.

~~~swift
import AuthenticationServices
import UIKit

@available(iOS 26.0, *)
final class PasskeyAuthorizationCoordinator: NSObject,
    ASAuthorizationControllerDelegate,
    ASAuthorizationControllerPresentationContextProviding {
    let window: UIWindow

    init(window: UIWindow) {
        self.window = window
    }

    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        window
    }

    func authorizationController(
        controller: ASAuthorizationController,
        didCompleteWithAuthorization authorization: ASAuthorization
    ) {
        _ = controller
        _ = authorization
        // Copy to a short-lived server-verification envelope.
    }

    func authorizationController(
        controller: ASAuthorizationController,
        didCompleteWithError error: Error
    ) {
        _ = controller
        _ = error
        // Map cancellation separately from provider failure.
    }
}
~~~

## 2. Create a Sign in with Apple request

Request only the scopes the product needs. The server must validate the
authorization code and identity token before issuing the app session.

~~~swift
import AuthenticationServices

@available(iOS 26.0, *)
func makeSignInWithAppleController() -> ASAuthorizationController {
    let provider = ASAuthorizationAppleIDProvider()
    let request = provider.createRequest()
    request.requestedScopes = [.email, .fullName]
    return ASAuthorizationController(authorizationRequests: [request])
}
~~~

## 3. Project Sign in with Apple into SwiftUI

Use Apple’s native SwiftUI control. Its completion result still goes to the
server exchange and account policy layer.

~~~swift
import AuthenticationServices
import SwiftUI

@available(iOS 26.0, *)
struct NativeSignInView: View {
    var body: some View {
        SignInWithAppleButton(.signIn) { request in
            request.requestedScopes = [.email]
        } onCompletion: { result in
            _ = result
            // Send the redacted credential envelope for server verification.
        }
    }
}
~~~

## 4. Create a platform passkey registration controller

The challenge and user ID should come from the current server transaction.

~~~swift
import AuthenticationServices
import Foundation

@available(iOS 26.0, *)
func makePlatformPasskeyRegistrationController() -> ASAuthorizationController {
    let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(
        relyingPartyIdentifier: "example.com"
    )
    let request = provider.createCredentialRegistrationRequest(
        challenge: Data("server-challenge-fixture".utf8),
        name: "person@example.com",
        userID: Data("opaque-user-id-fixture".utf8)
    )
    return ASAuthorizationController(authorizationRequests: [request])
}
~~~

## 5. Create a platform passkey assertion controller

Use a new server challenge for every assertion and apply any server-supplied
credential allowlist without exposing account-existence details.

~~~swift
import AuthenticationServices
import Foundation

@available(iOS 26.0, *)
func makePlatformPasskeyAssertionController() -> ASAuthorizationController {
    let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(
        relyingPartyIdentifier: "example.com"
    )
    let request = provider.createCredentialAssertionRequest(
        challenge: Data("server-assertion-fixture".utf8)
    )
    return ASAuthorizationController(authorizationRequests: [request])
}
~~~

## 6. Create a physical security-key registration controller

This starts a physical-key ceremony; it does not prove that the server will
accept the resulting credential.

~~~swift
import AuthenticationServices
import Foundation

@available(iOS 26.0, *)
func makeSecurityKeyRegistrationController() -> ASAuthorizationController {
    let provider = ASAuthorizationSecurityKeyPublicKeyCredentialProvider(
        relyingPartyIdentifier: "example.com"
    )
    let request = provider.createCredentialRegistrationRequest(
        challenge: Data("server-key-registration-fixture".utf8),
        displayName: "Example account key",
        name: "person@example.com",
        userID: Data("opaque-user-id-fixture".utf8)
    )
    return ASAuthorizationController(authorizationRequests: [request])
}
~~~

## 7. Create a physical security-key assertion controller

Give the server the returned assertion and preserve a recovery route for a
missing, removed, or locked-out key.

~~~swift
import AuthenticationServices
import Foundation

@available(iOS 26.0, *)
func makeSecurityKeyAssertionController() -> ASAuthorizationController {
    let provider = ASAuthorizationSecurityKeyPublicKeyCredentialProvider(
        relyingPartyIdentifier: "example.com"
    )
    let request = provider.createCredentialAssertionRequest(
        challenge: Data("server-key-assertion-fixture".utf8)
    )
    return ASAuthorizationController(authorizationRequests: [request])
}
~~~

## 8. Create an assertion with explicit browser client data

Origin and top-origin values are security inputs. The server must compare them
to a configured allowlist instead of accepting an arbitrary URL string.

~~~swift
import AuthenticationServices
import Foundation

@available(iOS 26.0, *)
func makeBrowserClientDataAssertionController() -> ASAuthorizationController {
    let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(
        relyingPartyIdentifier: "example.com"
    )
    let clientData = ASPublicKeyCredentialClientData(
        challenge: Data("server-browser-challenge-fixture".utf8),
        origin: "https://example.com"
    )
    let request = provider.createCredentialAssertionRequest(clientData: clientData)
    return ASAuthorizationController(authorizationRequests: [request])
}
~~~

## 9. Request iOS 26 fast account creation

Gate this route with availability and keep a normal passkey registration
fallback for targets where it is unavailable.

~~~swift
import AuthenticationServices
import Foundation

@available(iOS 26.0, *)
func makeAccountCreationRequest() -> ASAuthorizationAccountCreationPlatformPublicKeyCredentialRequest {
    ASAuthorizationAccountCreationProvider().createPlatformPublicKeyCredentialRegistrationRequest(
        acceptedContactIdentifiers: [],
        shouldRequestName: true,
        relyingPartyIdentifier: "example.com",
        challenge: Data("server-account-creation-fixture".utf8),
        userID: Data("opaque-user-id-fixture".utf8)
    )
}
~~~

## 10. Read the Sign in with Apple credential state

Credential state is a signal for recovery and session reconciliation. It is
not a substitute for validating the current server session.

~~~swift
import AuthenticationServices

@available(iOS 26.0, *)
func currentAppleCredentialState(
    for userID: String
) async throws -> ASAuthorizationAppleIDProvider.CredentialState {
    try await ASAuthorizationAppleIDProvider().credentialState(forUserID: userID)
}
~~~

## 11. Publish a passkey identity to a credential provider store

Identity-store metadata helps the system find a provider credential. Keep it in
sync with server state and do not treat it as an active account session.

~~~swift
import AuthenticationServices
import Foundation

@available(iOS 26.0, *)
func savePasskeyIdentity() async throws {
    let identity = ASPasskeyCredentialIdentity(
        relyingPartyIdentifier: "example.com",
        userName: "person@example.com",
        credentialID: Data("credential-id-fixture".utf8),
        userHandle: Data("opaque-user-id-fixture".utf8)
    )
    try await ASCredentialIdentityStore.shared.saveCredentialIdentities([identity])
}
~~~

## 12. Report a credential-provider public-key update

On the newer SDK route, report the provider’s current knowledge to the system,
then reconcile the provider’s own store and server state separately.

~~~swift
import AuthenticationServices
import Foundation

@available(iOS 26.2, *)
func reportUnknownCredentialToSystem() async throws {
    try await ASCredentialDataManager().reportUnknownPublicKeyCredential(
        relyingPartyIdentifier: "example.com",
        credentialID: Data("credential-id-fixture".utf8)
    )
}
~~~

## 13. Skeleton a Credential Provider Extension controller

The extension can be launched independently of the containing app. Keep the
request lifecycle short and cancel explicitly when the provider cannot fulfill
it.

~~~swift
import AuthenticationServices
import Foundation

@available(iOS 26.0, *)
final class ExampleCredentialProvider: ASCredentialProviderViewController {
    override func prepareCredentialList(for serviceIdentifiers: [ASCredentialServiceIdentifier]) {
        _ = serviceIdentifiers
        // Resolve only identities the extension can currently provide.
    }

    override func prepareInterfaceToProvideCredential(for credentialRequest: any ASCredentialRequest) {
        _ = credentialRequest
        let error = NSError(domain: "ExampleCredentialProvider", code: 1)
        extensionContext.cancelRequest(withError: error)
    }
}
~~~

## 14. Validate a typed, non-authoritative account proposal

This is an AI boundary recipe, not a model invocation. A model may propose an
explanation or provider order; deterministic policy must revalidate it before
starting a credential ceremony or account mutation.

~~~swift
import Foundation

struct AccountSetupProposal: Codable, Sendable {
    enum Provider: String, Codable, Sendable {
        case appleID
        case platformPasskey
        case securityKey
        case existingSession
    }

    let provider: Provider
    let policyRevision: String
    let explanation: String
    let requiresUserConfirmation: Bool
}

func acceptProposal(
    _ proposal: AccountSetupProposal,
    currentPolicyRevision: String,
    hasActiveServerTransaction: Bool
) -> AccountSetupProposal? {
    guard proposal.policyRevision == currentPolicyRevision,
          hasActiveServerTransaction,
          proposal.requiresUserConfirmation else {
        return nil
    }
    return proposal
}
~~~

## Sources

- [AuthenticationServices](https://developer.apple.com/documentation/authenticationservices)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [ASAuthorizationAppleIDProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidprovider)
- [Implementing user authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [SignInWithAppleButton](https://developer.apple.com/documentation/authenticationservices/signinwithapplebutton)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [Public-private key authentication](https://developer.apple.com/documentation/authenticationservices/public-private-key-authentication)
- [Supporting security key authentication using physical keys](https://developer.apple.com/documentation/authenticationservices/supporting-security-key-authentication-using-physical-keys)
- [ASAuthorizationAccountCreationProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationaccountcreationprovider)
- [ASPublicKeyCredentialClientData](https://developer.apple.com/documentation/authenticationservices/aspublickeycredentialclientdata)
- [ASCredentialProviderViewController](https://developer.apple.com/documentation/authenticationservices/ascredentialproviderviewcontroller)
- [ASCredentialIdentityStore](https://developer.apple.com/documentation/authenticationservices/ascredentialidentitystore)
- [ASCredentialDataManager](https://developer.apple.com/documentation/authenticationservices/ascredentialdatamanager)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
