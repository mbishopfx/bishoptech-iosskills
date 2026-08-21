# Authentication Services and passkey code recipes

These are target-oriented Swift sketches for named iOS or iPadOS apps. They are not claimed to compile in this documentation-only workspace and they do not prove an associated-domain deployment, system credential behavior, relying-party verification, account identity, PRF support, or release readiness. Confirm the exact SDK availability and signatures for the deployment target before shipping.

Read the [Authentication Services capability route](../50-capability-recipes/58-authentication-services-passkey-route.md), [framework deep dive](../42-framework-deep-dives/35-authentication-services-passkeys-and-apple-sign-in.md), [account authentication design guide](../21-design-deep-dives/55-account-authentication-and-passkey-review-design.md), and [proof matrix](../60-verification/52-authentication-services-passkey-proof-matrix.md) first.

## Recipe 1: Keep an authorization controller alive

The controller and its presentation delegate must live for the whole operation. Keep provider-specific data out of the view body.

~~~swift
import AuthenticationServices
import Foundation

@MainActor
final class AuthorizationCoordinator: NSObject,
    ASAuthorizationControllerDelegate,
    ASAuthorizationControllerPresentationContextProviding {

    enum Phase {
        case idle
        case presenting
        case returned(ASAuthorization)
        case canceled
        case failed(Error)
    }

    private(set) var phase: Phase = .idle
    private var controller: ASAuthorizationController?
    private var operationID = UUID()

    func perform(_ requests: [ASAuthorizationRequest]) {
        operationID = UUID()
        let next = ASAuthorizationController(authorizationRequests: requests)
        next.delegate = self
        next.presentationContextProvider = self
        controller = next
        phase = .presenting
        next.performRequests()
    }

    func cancel() {
        operationID = UUID()
        controller = nil
        phase = .canceled
    }

    func authorizationController(
        controller: ASAuthorizationController,
        didCompleteWithAuthorization authorization: ASAuthorization
    ) {
        phase = .returned(authorization)
        self.controller = nil
    }

    func authorizationController(
        controller: ASAuthorizationController,
        didCompleteWithError error: Error
    ) {
        phase = .failed(error)
        self.controller = nil
    }

    func presentationAnchor(
        for controller: ASAuthorizationController
    ) -> ASPresentationAnchor {
        // Resolve the app's active window from the scene coordinator.
        // Do not manufacture a detached window for the authorization sheet.
        fatalError("Connect this coordinator to the app's active scene.")
    }
}
~~~

The fatal error is an integration seam, not a production implementation. The app must return a real active presentation anchor for the scene that initiated the action.

## Recipe 2: Use the official Sign in with Apple control

Keep the official button as the provider control. Do not draw a custom Apple identity button and attach the provider request to it.

~~~swift
import AuthenticationServices
import SwiftUI

struct AppleSignInView: View {
    let onCredential: (ASAuthorizationAppleIDCredential) -> Void
    let onFailure: (Error) -> Void

    var body: some View {
        SignInWithAppleButton(
            .signIn,
            onRequest: { request in
                request.requestedScopes = [.fullName, .email]
                // Add a server-issued nonce when the server contract requires it.
            },
            onCompletion: { result in
                switch result {
                case .success(let authorization):
                    guard let credential =
                        authorization.credential as? ASAuthorizationAppleIDCredential
                    else {
                        return
                    }
                    onCredential(credential)
                case .failure(let error):
                    onFailure(error)
                }
            }
        )
        .signInWithAppleButtonStyle(.black)
        .frame(height: 50)
        .accessibilityHint("Uses your Apple Account to sign in.")
    }
}
~~~

Send the authorization code and identity token to the server over the product’s intended transport. Do not treat the credential’s presence as a local session. Persist name/email only under an explicit first-use profile policy.

## Recipe 3: Create a platform passkey registration request

The server owns the challenge, user ID, and relying-party policy. The app supplies those values to the platform public-key provider and forwards the result.

~~~swift
import AuthenticationServices
import Foundation

struct PasskeyRegistrationInput {
    let relyingPartyID: String
    let challenge: Data
    let userID: Data
    let userName: String
    let displayName: String
}

func makeRegistrationRequest(
    from input: PasskeyRegistrationInput
) -> ASAuthorizationPlatformPublicKeyCredentialRegistrationRequest {
    let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(
        relyingPartyIdentifier: input.relyingPartyID
    )

    return provider.createCredentialRegistrationRequest(
        challenge: input.challenge,
        name: input.userName,
        userID: input.userID
    )
}
~~~

Before calling this function, validate that the target’s webcredentials associated domain, deployed AASA file, server relying-party identifier, and request value refer to the same service. The returned authorization must be sent to the server for registration verification.

## Recipe 4: Create a platform passkey assertion request

Use a fresh challenge for every assertion. A local cached assertion request is not a replay defense.

~~~swift
import AuthenticationServices
import Foundation

func makeAssertionRequest(
    relyingPartyID: String,
    challenge: Data
) -> ASAuthorizationPlatformPublicKeyCredentialAssertionRequest {
    let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(
        relyingPartyIdentifier: relyingPartyID
    )
    return provider.createCredentialAssertionRequest(challenge: challenge)
}
~~~

After the system returns, adapt the concrete assertion into a transport object containing only the fields the verifier needs. The server should verify challenge, relying-party/origin binding, credential lookup, signature, authenticator state, and account policy before returning a session.

## Recipe 5: Adapt a returned passkey without logging secrets

Keep the wire format explicit and redacted. The exact properties available on the authorization result depend on the selected SDK API and credential type.

~~~swift
import AuthenticationServices
import Foundation

struct PasskeyAssertionPayload: Encodable {
    let credentialID: Data
    let rawClientDataJSON: Data
    let rawAuthenticatorData: Data
    let signature: Data
    let userID: Data
}

func assertionPayload(
    from authorization: ASAuthorization
) throws -> PasskeyAssertionPayload {
    guard let assertion =
        authorization.credential
            as? ASAuthorizationPlatformPublicKeyCredentialAssertion
    else {
        throw NSError(
            domain: "AuthRoute",
            code: 1,
            userInfo: [NSLocalizedDescriptionKey: "Unexpected credential type."]
        )
    }

    return PasskeyAssertionPayload(
        credentialID: assertion.credentialID,
        rawClientDataJSON: assertion.rawClientDataJSON,
        rawAuthenticatorData: assertion.rawAuthenticatorData,
        signature: assertion.signature,
        userID: assertion.userID
    )
}
~~~

Treat this as a field-mapping sketch. Verify the concrete SDK property names and server encoding for the target SDK. Never put the Data values into ordinary logs or user-facing error messages.

## Recipe 6: Convert server verification into app state

Do not publish a signed-in state from the Authentication Services callback alone.

~~~swift
enum VerifiedAuthResult {
    case signedIn(sessionToken: String)
    case localUnlock(opaqueOperationID: UUID)
    case needsRecovery(reason: String)
}

@MainActor
final class AuthViewModel: ObservableObject {
    @Published private(set) var status = "Ready"

    func receiveCredential(_ credential: ASAuthorization) {
        status = "Verifying"

        Task {
            do {
                let result = try await sendToVerifier(credential)
                switch result {
                case .signedIn:
                    status = "Signed in"
                case .localUnlock:
                    status = "Unlocked"
                case .needsRecovery(let reason):
                    status = reason
                }
            } catch {
                status = "We could not verify that sign-in."
            }
        }
    }

    private func sendToVerifier(
        _ credential: ASAuthorization
    ) async throws -> VerifiedAuthResult {
        // Serialize a provider-specific, redacted payload and call the server.
        fatalError("Connect this seam to the app's authenticated transport.")
    }
}
~~~

The placeholder keeps the security boundary visible. The production transport should use a server response that is typed, scoped, and safe to show—not a model-generated interpretation of a token or signature.

## Recipe 7: Sign in with Apple credential adapter

The Apple credential includes a stable provider identifier and may include a first-use name/email, identity token, authorization code, state, and real-user status. Treat all optional values as optional.

~~~swift
import AuthenticationServices

struct AppleCredentialPayload: Encodable {
    let user: String
    let identityToken: Data?
    let authorizationCode: Data?
    let email: String?
    let givenName: String?
    let familyName: String?
    let state: String?
}

func applePayload(
    from credential: ASAuthorizationAppleIDCredential
) -> AppleCredentialPayload {
    AppleCredentialPayload(
        user: credential.user,
        identityToken: credential.identityToken,
        authorizationCode: credential.authorizationCode,
        email: credential.email,
        givenName: credential.fullName?.givenName,
        familyName: credential.fullName?.familyName,
        state: credential.state
    )
}
~~~

The server should verify the identity token’s JWS signature and claims, validate the authorization code when used, and bind the stable user value to the product account. Do not use a missing email or name on a later sign-in to erase a stored profile.

## Recipe 8: Query Apple credential state as a recovery signal

The provider state is a local signal. Pair it with server state and a deliberate user-facing policy.

~~~swift
import AuthenticationServices

func refreshAppleCredentialState(
    user: String,
    completion: @escaping (ASAuthorizationAppleIDProvider.CredentialState) -> Void
) {
    ASAuthorizationAppleIDProvider().getCredentialState(forUserID: user) {
        state, _ in
        completion(state)
    }
}
~~~

Map revoked, transferred, not found, authorized, and unknown conditions to product policy. Never disclose raw provider diagnostics when a short recovery explanation is sufficient.

## Recipe 9: Physical security-key provider seam

Keep physical-key transport as an explicit provider branch. The registration/assertion request constructors and supported algorithms must match the SDK version and server policy.

~~~swift
import AuthenticationServices
import Foundation

struct SecurityKeyRoute {
    let relyingPartyID: String

    func provider() -> ASAuthorizationSecurityKeyPublicKeyCredentialProvider {
        ASAuthorizationSecurityKeyPublicKeyCredentialProvider(
            relyingPartyIdentifier: relyingPartyID
        )
    }

    func start(requests: [ASAuthorizationRequest]) {
        // Pass a provider-specific registration or assertion request to
        // AuthorizationCoordinator.perform(_:).
        // Keep NFC, USB, and Lightning fixture expectations in the proof matrix.
        _ = requests
    }
}
~~~

The system may ask for the physical key or user verification. That interaction must be tested with real hardware. Configure a recovery path before making the security key the only credential.

## Recipe 10: Start a web authentication session

ASWebAuthenticationSession owns a system browser-authentication surface. The provider and server own the web authorization contract.

~~~swift
import AuthenticationServices
import Foundation

final class WebAuthCoordinator: NSObject,
    ASWebAuthenticationPresentationContextProviding {
    private var session: ASWebAuthenticationSession?
    private let presentationAnchor: ASPresentationAnchor

    init(presentationAnchor: ASPresentationAnchor) {
        self.presentationAnchor = presentationAnchor
    }

    func start(url: URL, callbackScheme: String) {
        let next = ASWebAuthenticationSession(
            url: url,
            callbackURLScheme: callbackScheme
        ) { [weak self] callbackURL, error in
            self?.session = nil
            if let error {
                // Map cancellation separately from provider failure.
                _ = error
                return
            }
            guard let callbackURL else { return }
            // Validate state and send the one-time code to the server.
            _ = callbackURL
        }

        next.presentationContextProvider = self
        next.prefersEphemeralWebBrowserSession = false
        session = next
        next.start()
    }

    func presentationAnchor(
        for session: ASWebAuthenticationSession
    ) -> ASPresentationAnchor {
        presentationAnchor
    }
}
~~~

Generate and validate state and nonce at the correct trust boundary. Do not log the callback URL if it can contain a code or token.

## Recipe 11: PRF assertion design seam

PRF support should be an optional assertion extension with a versioned salt policy. The exact property names and initializer signatures must be checked against the SDK target.

~~~swift
struct LocalKeyRequest {
    let saltVersion: UInt8
    let saltInput: Data
}

enum LocalKeyResult {
    case derived(Data)
    case unsupported
    case canceled
}

func handlePRFOutput(
    _ output: Data?,
    request: LocalKeyRequest
) -> LocalKeyResult {
    guard let output else { return .unsupported }
    guard !output.isEmpty else { return .canceled }

    // Convert directly into a CryptoKit key for the current operation.
    // Store ciphertext or a wrapped key, never the raw PRF output.
    _ = request.saltVersion
    return .derived(output)
}
~~~

On the actual target, construct the Authentication Services PRF assertion input, attach it to the passkey assertion request as documented for that SDK, and read the PRF assertion output. Do not export it, send it to a model, or use it as a replacement for server authorization.

## Recipe 12: Large Blob schema adapter

Large Blob is one authenticator-associated value, not an app database. Keep the app schema small and versioned.

~~~swift
struct AuthenticatorBlob: Codable {
    let version: UInt8
    let purpose: String
    let checksum: Data
    let value: Data
}

func encodeAuthenticatorBlob(
    purpose: String,
    value: Data,
    checksum: Data
) throws -> Data {
    let blob = AuthenticatorBlob(
        version: 1,
        purpose: purpose,
        checksum: checksum,
        value: value
    )
    return try JSONEncoder().encode(blob)
}
~~~

Construct the documented Large Blob assertion input for read or write on the actual SDK target. Handle unsupported extension, oversize value, failed write, malformed read, migration, credential replacement, and deletion as explicit outcomes.

## Recipe 13: Provider-neutral operation state

A provider-neutral state machine prevents one provider’s callback from granting another provider’s privilege.

~~~swift
enum AuthProvider: Equatable {
    case passkey
    case apple
    case securityKey
    case web
}

enum AuthOperationState: Equatable {
    case ready
    case requestingChallenge(AuthProvider)
    case presenting(AuthProvider)
    case returned(AuthProvider)
    case verifying(AuthProvider)
    case verified(AuthProvider)
    case canceled(AuthProvider)
    case recovery(AuthProvider, String)
}
~~~

Store provider, operation ID, environment, challenge ID, and expected destination with the operation. Clear them on completion. A model may produce copy for a recovery state, but the state transition itself comes from deterministic provider/server results.

## Recipe 14: Redacted logging

Log lifecycle facts, not credential material.

~~~swift
struct AuthLogEvent: Encodable {
    let operationID: UUID
    let provider: String
    let phase: String
    let environment: String
    let result: String
}

func log(_ event: AuthLogEvent) {
    // Send only the redacted event to the diagnostic system.
    // Never add token, code, signature, key, PRF, or callback contents.
    _ = event
}
~~~

Keep a separate, access-controlled server verifier log for challenge and claim diagnostics. Redact values there too, and retain only what the incident and privacy policies require.

## Recipe 15: Test seams before physical proof

Mocks can validate app state transitions but cannot prove Apple system UI, passkey sync, associated-domain delivery, NFC/USB/Lightning behavior, or server cryptography. Keep both layers:

~~~swift
protocol AuthTransport {
    func verify(_ payload: Data) async throws -> VerifiedAuthResult
}

struct FakeAuthTransport: AuthTransport {
    let result: VerifiedAuthResult

    func verify(_ payload: Data) async throws -> VerifiedAuthResult {
        _ = payload
        return result
    }
}
~~~

Use mocks for canceled, rejected, expired, recovery, revoked, transferred, deleted, and success states. Then run the proof matrix on physical devices and a real server verifier before claiming support.

## Sources

- [Authentication Services](https://developer.apple.com/documentation/authenticationservices)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [AuthorizationController](https://developer.apple.com/documentation/authenticationservices/authorizationcontroller)
- [ASAuthorizationAppleIDProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidprovider)
- [ASAuthorizationAppleIDCredential](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidcredential)
- [Implementing User Authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [Displaying Sign in with Apple buttons in your app](https://developer.apple.com/documentation/signinwithapple/displaying-sign-in-with-apple-buttons-in-your-app)
- [SignInWithAppleButton](https://developer.apple.com/documentation/authenticationservices/signinwithapplebutton)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [Connecting to a service with passkeys](https://developer.apple.com/documentation/authenticationservices/connecting-to-a-service-with-passkeys)
- [Public-Private Key Authentication](https://developer.apple.com/documentation/authenticationservices/public-private-key-authentication)
- [ASAuthorizationPlatformPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialprovider)
- [ASAuthorizationPlatformPublicKeyCredentialRegistrationRequest](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialregistrationrequest)
- [ASAuthorizationPlatformPublicKeyCredentialAssertionRequest](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialassertionrequest)
- [ASAuthorizationPlatformPublicKeyCredentialAssertion](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialassertion)
- [Supporting Security Key Authentication Using Physical Keys](https://developer.apple.com/documentation/authenticationservices/supporting-security-key-authentication-using-physical-keys)
- [ASAuthorizationSecurityKeyPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationsecuritykeypublickeycredentialprovider)
- [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession)
- [WebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/webauthenticationsession)
- [ASAuthorizationPublicKeyCredentialPRFAssertionInput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentialprfassertioninput-swift.struct)
- [ASAuthorizationPublicKeyCredentialPRFAssertionOutput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentialprfassertionoutput-swift.struct)
- [ASAuthorizationPublicKeyCredentialLargeBlobAssertionInput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentiallargeblobassertioninput-swift.struct)
- [ASAuthorizationPublicKeyCredentialLargeBlobAssertionOutput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentiallargeblobassertionoutput-swift.struct)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Sign in with Apple Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.applesignin)
- [Managing accounts](https://developer.apple.com/design/human-interface-guidelines/managing-accounts)
- [Sign in with Apple](https://developer.apple.com/design/human-interface-guidelines/sign-in-with-apple)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
