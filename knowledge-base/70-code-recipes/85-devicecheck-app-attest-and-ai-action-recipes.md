# DeviceCheck, App Attest, and AI-action recipes

These are compile-oriented client route sketches. The server must issue challenges, validate attestation/assertion objects, manage keys/counters, and make the authorization/risk decision. Never treat a client callback or local preview as server proof.

## 1. Hash server challenge data with CryptoKit

The client hashes a one-time server block before passing it to App Attest. Keep the challenge/request context opaque and do not generate the security challenge solely on the client.

~~~swift
import CryptoKit
import Foundation

func clientDataHash(_ data: Data) -> Data {
    Data(SHA256.hash(data: data))
}
~~~

Apple’s App Attest documentation requires a unique, single-use block and recommends sufficient entropy for a server challenge. The server owns challenge generation and replay tracking.

## 2. Create and attest an App Attest key

Use one key per account/device route and persist the identifier as soon as key generation succeeds.

~~~swift
import DeviceCheck
import Foundation

enum AppAttestError: Error {
    case unsupported
    case missingKey
}

struct AttestationPayload: Sendable {
    let keyIdentifier: String
    let attestationObject: Data
    let challengeID: String
}

@available(iOS 14.0, *)
func createAppAttestPayload(
    challengeID: String,
    challenge: Data
) async throws -> AttestationPayload {
    let service = DCAppAttestService.shared
    guard service.isSupported else {
        throw AppAttestError.unsupported
    }

    let keyIdentifier = try await service.generateKey()
    let attestation = try await service.attestKey(
        keyIdentifier,
        clientDataHash: clientDataHash(challenge)
    )

    // Persist keyIdentifier in app storage and send the attestation
    // object to the server for validation. Do not store raw attestation
    // objects as a substitute for the key identifier.
    return AttestationPayload(
        keyIdentifier: keyIdentifier,
        attestationObject: attestation,
        challengeID: challengeID
    )
}
~~~

If attestation returns a server-unavailable error, retry with the same key and client-data hash according to the documented recovery path. Do not generate a new key for a transient server outage. If the server rejects the attestation, discard/revoke the key identifier according to the product policy.

## 3. Generate an assertion for a protected request

Bind the server challenge and the exact request context before asking App Attest to sign.

~~~swift
import DeviceCheck
import Foundation

struct AssertionPayload: Sendable {
    let keyIdentifier: String
    let challengeID: String
    let assertion: Data
}

@available(iOS 14.0, *)
func createAssertion(
    keyIdentifier: String,
    challengeID: String,
    challenge: Data,
    requestBody: Data
) async throws -> AssertionPayload {
    let service = DCAppAttestService.shared
    guard service.isSupported else {
        throw AppAttestError.unsupported
    }

    var clientBlock = Data()
    clientBlock.append(challenge)
    clientBlock.append(clientDataHash(requestBody))
    let assertion = try await service.generateAssertion(
        keyIdentifier,
        clientDataHash: clientDataHash(clientBlock)
    )

    return AssertionPayload(
        keyIdentifier: keyIdentifier,
        challengeID: challengeID,
        assertion: assertion
    )
}
~~~

The server must verify the assertion signature, challenge, request body/context, key identifier, and counter before accepting the request. The client should not decide that the assertion is valid.

## 4. Represent an authenticated server request

Use a transport model that makes the challenge and assertion binding visible without putting secrets in logs.

~~~swift
import Foundation

struct AttestedRequest: Encodable {
    let challengeID: String
    let keyIdentifier: String
    let requestBody: Data
    let assertion: Data
}

func redactedAuditFields(
    challengeID: String,
    keyIdentifier: String
) -> [String: String] {
    [
        "challengeID": challengeID,
        "keyIdentifier": keyIdentifier,
        "requestBody": "<redacted>",
        "assertion": "<redacted>"
    ]
}
~~~

If the transport is text-based HTTPS, Base64-encode binary attestation/assertion data for the wire format. Keep the original binary value available only in the request encoder and do not emit it in diagnostics.

## 5. Generate a DeviceCheck token

DeviceCheck is a server-backed two-bit state route. The app supplies an ephemeral token; the server talks to Apple and owns the bit semantics.

~~~swift
import DeviceCheck

enum DeviceCheckError: Error {
    case unsupported
    case missingToken
}

func generateDeviceCheckToken() async throws -> Data {
    let device = DCDevice.current
    guard device.isSupported else {
        throw DeviceCheckError.unsupported
    }

    return try await withCheckedThrowingContinuation { continuation in
        device.generateToken { token, error in
            if let token {
                continuation.resume(returning: token)
            } else {
                continuation.resume(
                    throwing: error ?? DeviceCheckError.missingToken
                )
            }
        }
    }
}
~~~

Do not call a token “trusted” in app state. The server must authenticate with Apple, query/update the two bits, apply the product’s meaning, and send back a decision.

## 6. Select a safe fallback mode

Unsupported environments should degrade deliberately.

~~~swift
import DeviceCheck

enum IntegrityRoute: Equatable {
    case appAttest
    case deviceCheck
    case limitedLocalOnly
}

func chooseIntegrityRoute() -> IntegrityRoute {
    if DCAppAttestService.shared.isSupported {
        return .appAttest
    }
    if DCDevice.current.isSupported {
        return .deviceCheck
    }
    return .limitedLocalOnly
}
~~~

This is an availability choice, not a server authorization. A high-risk operation can reject the limited route instead of silently accepting it.

## 7. Protect a remote AI or tool action

Keep account authentication, App Attest, model input, server policy, and user confirmation separate.

~~~swift
struct ProtectedAIAction {
    enum Result: Equatable {
        case unsupported
        case verificationRequired
        case reviewDraft(String)
        case rejected
    }

    let accountID: String

    func prepare(
        requestBody: Data,
        challengeID: String,
        challenge: Data,
        keyIdentifier: String
    ) async throws -> Result {
        guard DCAppAttestService.shared.isSupported else {
            return .unsupported
        }

        let assertion = try await createAssertion(
            keyIdentifier: keyIdentifier,
            challengeID: challengeID,
            challenge: challenge,
            requestBody: requestBody
        )

        // Send assertion and request to the server. The server validates
        // account, challenge, key, counter, request, rate, and entitlement.
        // Only then should it return an AI draft for user review.
        _ = (accountID, assertion)
        return .verificationRequired
    }
}
~~~

Never treat this client return value as a completed server decision. The UI should move to a “waiting for server verification” state until the actual response arrives.

## 8. Test challenge and fallback semantics

Test app-owned policy before physical server validation.

~~~swift
import Testing

@Test
func unsupportedRouteDoesNotClaimVerification() {
    let result: IntegrityRoute = .limitedLocalOnly
    #expect(result != .appAttest)
}

@Test
func requestBodyChangesClientHash() {
    let first = clientDataHash(Data("first".utf8))
    let second = clientDataHash(Data("second".utf8))
    #expect(first != second)
}
~~~

These tests do not prove attestation verification, assertion counters, Apple service behavior, server authentication, or abuse resistance.

## Sources

- [DeviceCheck](https://developer.apple.com/documentation/devicecheck)
- [DCDevice](https://developer.apple.com/documentation/devicecheck/dcdevice)
- [DCAppAttestService](https://developer.apple.com/documentation/devicecheck/dcappattestservice)
- [DCAppAttestService.isSupported](https://developer.apple.com/documentation/devicecheck/dcappattestservice/issupported)
- [generateKey(completionHandler:)](https://developer.apple.com/documentation/devicecheck/dcappattestservice/generatekey%28completionhandler%3A%29)
- [attestKey(_:clientDataHash:completionHandler:)](https://developer.apple.com/documentation/devicecheck/dcappattestservice/attestkey%28_%3Aclientdatahash%3Acompletionhandler%3A%29)
- [generateAssertion(_:clientDataHash:completionHandler:)](https://developer.apple.com/documentation/devicecheck/dcappattestservice/generateassertion%28_%3Aclientdatahash%3Acompletionhandler%3A%29)
- [Establishing your app’s integrity](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity)
- [Validating apps that connect to your server](https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server)
- [Attestation Object Validation Guide](https://developer.apple.com/documentation/devicecheck/attestation-object-validation-guide)
- [Accessing and modifying per-device data](https://developer.apple.com/documentation/devicecheck/accessing-and-modifying-per-device-data)
- [CryptoKit](https://developer.apple.com/documentation/cryptokit)
- [Testing](https://developer.apple.com/documentation/testing)
