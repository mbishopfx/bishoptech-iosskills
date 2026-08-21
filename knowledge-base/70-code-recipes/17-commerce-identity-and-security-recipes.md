# Commerce, Identity, and Security Recipes

Keep product, identity, secret, biometric, and device-integrity routes separate using the [capability-first Apple SDK atlas](../40-framework-routes/10-capability-first-apple-sdk-atlas.md) and record server/account/signed evidence independently from local code behavior.

## Scope and compile boundary

These are compile-oriented route sketches for StoreKit 2 entitlements, Apple Pay/Wallet, Sign in with Apple, Keychain, LocalAuthentication, DeviceCheck, App Attest, and secure API boundaries. They are not compiled in this documentation-only workspace and do not prove App Store metadata, server verification, merchant processing, Wallet signing, Apple Account state, Secure Enclave behavior, App Attest validation, or release readiness.

Keep the trust chain explicit:

`system request -> signed/verified result -> server/business policy -> user-facing entitlement or side effect`

A product identifier, token, credential callback, keychain read, biometric success, or device token is not automatically proof of entitlement, identity, authorization, payment fulfillment, or security.

## Recipe 1: calculate StoreKit 2 entitlements from verified transactions

Use StoreKit 2 for digital goods and subscriptions. Load products from the App Store, listen for `Transaction.updates`, and refresh from `Transaction.currentEntitlements`. Unlock only from verified transaction state and finish a transaction after the feature has delivered its entitlement.

```swift
import StoreKit

enum EntitlementState {
    case loading
    case entitled(productID: String)
    case notEntitled
    case pending
    case unverified
    case cancelled
    case failed
}

actor PurchaseStore {
    private var updatesTask: Task<Void, Never>?
    private(set) var state: EntitlementState = .notEntitled

    func startListening() {
        updatesTask?.cancel()
        updatesTask = Task { [weak self] in
            guard let self else { return }

            for await result in Transaction.updates {
                await self.handle(result)
            }
        }
    }

    func refreshEntitlements() async {
        state = .loading

        for await result in Transaction.currentEntitlements {
            await handle(result)
        }
    }

    func purchase(productID: String) async throws -> EntitlementState {
        let products = try await Product.products(for: [productID])
        guard let product = products.first else {
            state = .failed
            return state
        }

        switch try await product.purchase() {
        case .success(let verificationResult):
            await handle(verificationResult)
            return state
        case .pending:
            state = .pending
            return state
        case .userCancelled:
            state = .cancelled
            return state
        @unknown default:
            state = .failed
            return state
        }
    }

    private func handle(
        _ result: VerificationResult<Transaction>
    ) async {
        switch result {
        case .verified(let transaction):
            // Apply the app’s product/business policy here. Consumables,
            // subscriptions, revocations, and expirations differ.
            state = .entitled(productID: transaction.productID)
            await transaction.finish()
        case .unverified:
            state = .unverified
            // Do not unlock from an unverified transaction.
        }
    }
}
```

This is a route sketch: a production entitlement service should model revocation, expiration, subscription grace/expiration, upgrades, consumables, restore, account association, and unverified errors separately. `currentEntitlements` does not contain consumable purchases. If a backend gates premium resources, send signed transaction/subscription data to a server that verifies it; do not accept an app-supplied Boolean.

StoreKit Testing and a local StoreKit configuration are deterministic fixtures, not App Store Connect, sandbox/TestFlight, production storefront, server-reconciliation, or review proof. Keep a signed target run for the actual environment.

## Recipe 2: separate Apple Pay authorization from fulfillment

Use PassKit/Apple Pay for physical goods or services when the merchant and payment provider support the route. Check device/network availability, configure the merchant ID and capabilities, create a payment request, present the system sheet, and send the payment token to the provider/server. The sheet/token does not itself confirm capture or fulfillment.

```swift
import PassKit

func applePayIsAvailable() -> Bool {
    PKPaymentAuthorizationController.canMakePayments()
}

func buildPaymentRequest() -> PKPaymentRequest {
    let request = PKPaymentRequest()
    request.merchantIdentifier = "merchant.example.app"
    request.supportedNetworks = [.visa, .masterCard, .amex]
    request.merchantCapabilities = .capability3DS
    request.countryCode = "US"
    request.currencyCode = "USD"
    request.paymentSummaryItems = [
        PKPaymentSummaryItem(
            label: "Example order",
            amount: NSDecimalNumber(string: "19.00")
        )
    ]
    return request
}
```

The merchant ID, payment-processing certificate/provider, supported networks, shipping/contact requirements, country/currency, backend order ID, and production configuration belong in the target project’s release checklist. Model `presenting -> authorizedToken -> processing -> fulfilled|declined|retry`; do not mark an order paid from the presentation callback alone.

## Recipe 3: add a signed Wallet pass with a system confirmation

Wallet passes must be signed artifacts with a pass type/distribution lifecycle. Confirm that the target can add passes, parse the signed pass, and let the system-owned UI prompt the person.

```swift
import PassKit

func canOfferPass(_ pass: PKPass) -> Bool {
    PKAddPassesViewController.canAddPasses()
        && pass.passTypeIdentifier.isEmpty == false
}

func makeAddPassController(
    for pass: PKPass
) -> PKAddPassesViewController? {
    guard canOfferPass(pass) else { return nil }
    return PKAddPassesViewController(pass: pass)
}
```

Keep pass signing, pass type IDs, update/revoke channels, issuer identity, privacy fields, and supported device families explicit. Adding a pass is not identity verification, payment authorization, or proof that the issuer will keep the pass current. Test add/display/update/revoke on a signed physical device and handle a stale or revoked pass.

## Recipe 4: start Sign in with Apple with nonce/state boundaries

Use a cryptographically random nonce and a state/correlation value appropriate to the flow. Store only the minimum local identifier/profile data, and verify the authorization response/token at the server when an account/backend exists.

```swift
import AuthenticationServices

struct AppleSignInRequestData {
    let request: ASAuthorizationAppleIDRequest
    let nonce: String
    let state: String
}

func makeAppleSignInRequest(
    nonce: String,
    state: String
) -> AppleSignInRequestData {
    let provider = ASAuthorizationAppleIDProvider()
    let request = provider.createRequest()
    request.requestedScopes = [.fullName, .email]
    request.nonce = nonce
    request.state = state
    return AppleSignInRequestData(request: request, nonce: nonce, state: state)
}
```

On completion, validate the returned state/correlation and hand identity material to the server boundary. Persist the stable Apple user identifier in Keychain/app-owned state. Name and email may be present only on the first authorization, and a person may choose a private relay address. At launch or return, use `ASAuthorizationAppleIDProvider.getCredentialState(forUserID:)` and handle authorized, revoked, not-found, and transient states. Sign out, unlink, account deletion, and local-data ownership must be explicit.

## Recipe 5: store a secret with a deliberate Keychain policy

Keychain accessibility is part of the threat model. The example uses a device-only, unlocked policy; choose a different policy only when the workflow requires it and document migration/backup behavior.

```swift
import Security

struct KeychainSecretStore {
    func save(_ data: Data, account: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: account,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            kSecValueData as String: data
        ]

        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess || status == errSecDuplicateItem else {
            throw KeychainError.status(status)
        }

        if status == errSecDuplicateItem {
            let lookup: [String: Any] = [
                kSecClass as String: kSecClassGenericPassword,
                kSecAttrAccount as String: account
            ]
            let values: [String: Any] = [kSecValueData as String: data]
            let updateStatus = SecItemUpdate(
                lookup as CFDictionary,
                values as CFDictionary
            )
            guard updateStatus == errSecSuccess else {
                throw KeychainError.status(updateStatus)
            }
        }
    }

    func load(account: String) throws -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.status(status)
        }
        return result as? Data
    }

    func delete(account: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: account
        ]
        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.status(status)
        }
    }
}

enum KeychainError: Error {
    case status(OSStatus)
}
```

Never print or include the secret in an error. Test the selected accessibility and access-control behavior while locked, after restart, after backup/restore, after migration, and after uninstall/reinstall. `ThisDeviceOnly` intentionally changes recovery/sync behavior; it is not a universal default.

## Recipe 6: gate a local action with LocalAuthentication

LocalAuthentication evaluates a device-owner policy. It does not prove a server account, payment entitlement, or authorization to change unrelated data.

```swift
import LocalAuthentication

func authenticateForProtectedAction() async throws -> Bool {
    let context = LAContext()
    var error: NSError?

    guard context.canEvaluatePolicy(
        .deviceOwnerAuthentication,
        error: &error
    ) else {
        // Map no passcode, unavailable biometrics, restriction, or lockout
        // to an intentional fallback; do not expose raw error text.
        return false
    }

    return try await context.evaluatePolicy(
        .deviceOwnerAuthentication,
        localizedReason: "Unlock the saved secret for this action"
    )
}
```

Include `NSFaceIDUsageDescription` when the target allows biometric authentication. For the strongest boundary, combine a LocalAuthentication policy with a Keychain `SecAccessControl` item so the secret cannot be read without the required policy. Test passcode fallback, biometric lockout/enrollment changes, cancellation, backgrounding, and a person who declines.

## Recipe 7: App Attest is a server challenge protocol

App Attest requires a registered App ID and server validation. The app creates a device-backed key, sends the attestation object and key ID to the server, then signs later request hashes with a one-time server challenge. DeviceCheck’s token/bits route is related but not interchangeable.

```swift
import CryptoKit
import DeviceCheck

final class AppAttestClient {
    private let service = DCAppAttestService.shared

    func createKey() {
        guard service.isSupported else { return }

        service.generateKey { keyID, error in
            guard error == nil, let keyID else {
                // Use a documented degraded-risk/fallback policy.
                return
            }

            // Persist only the key identifier. The private key stays managed
            // by the App Attest/Secure Enclave boundary.
            _ = keyID
        }
    }

    func makeAssertion(
        keyID: String,
        serverChallenge: Data,
        requestBody: Data
    ) {
        var clientData = Data()
        clientData.append(serverChallenge)
        clientData.append(requestBody)
        let clientDataHash = Data(SHA256.hash(data: clientData))

        service.generateAssertion(
            keyID,
            clientDataHash: clientDataHash
        ) { assertion, error in
            guard error == nil, let assertion else { return }

            // Send keyID, assertion, the request/challenge context, and the
            // exact request to a server that validates replay and binding.
            _ = assertion
        }
    }
}
```

The client must not decide that an assertion is valid by itself. The server verifies the attestation/assertion, challenge freshness, app identity/environment, request binding, and risk policy. Handle unsupported devices, key loss, reinstall/restore, server timeout, invalid/replayed challenge, and gradual rollout. App Attest reduces a class of abuse; it is not absolute tamper proofing or authorization.

## Recipe 8: compose verification without a local bypass

```swift
enum TrustState {
    case unknown
    case loading
    case verifiedEntitlement
    case verifiedIdentity
    case localAuthenticationPassed
    case serverAccepted
    case pending
    case unavailable(reason: String)
    case rejected(reason: String)
}

struct ProtectedAction {
    let id: UUID
    let purpose: String
    let requiresServerAuthorization: Bool
    let requiresLocalUserPresence: Bool
}
```

A protected action should state which proof it needs and gate on that proof. Do not unlock from “purchase sheet completed,” “Apple ID credential returned,” “biometric callback true,” “App Attest supported,” or “device token exists.” Keep free/local functionality available when a stronger service is unavailable unless the user outcome inherently requires it.

## Recipe 9: privacy, release, and device proof matrix

| Route | Configuration | Evidence |
| --- | --- | --- |
| StoreKit | Product IDs, StoreKit capability/configuration, App Store Connect, server policy | Verified/unverified/pending/refund/expiry/restore, sandbox/TestFlight, server reconciliation, release metadata. |
| Apple Pay | Merchant ID, capability, certificates/provider, country/currency/networks | Availability, payment token, provider decline/timeout, fulfillment, signed physical-device sandbox run. |
| Wallet | Wallet capability, pass type IDs, signed pass/update channel | Add/display/update/revoke, stale pass, device support, real Wallet. |
| Sign in with Apple | Capability/service ID/server client config, nonce/state, Keychain | First/returning sign-in, relay, revocation, deletion/linking, server verification. |
| Keychain/biometrics | Accessibility, access control, Face ID usage, access groups | Lock/restart/migration/backup/uninstall, passcode/biometric changes, fallback, no secret logs. |
| DeviceCheck/App Attest | Registered App ID, server keys/challenge/validation, environment | Supported/unsupported, attestation/assertion, replay/rejection, key loss, degraded risk. |
| API security | ATS/TLS/auth/session/refresh/retry policy | Offline, timeout, cancellation, malformed/expired token, replay/idempotency, redaction, server authorization. |

Previews and local StoreKit/security fixtures validate state rendering and pure parsing. They do not prove signed entitlements, payment capture, Wallet signing, Apple credential state, Keychain migration, biometric hardware, Secure Enclave, App Attest server validation, or App Store release readiness.

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [In-App Purchase](https://developer.apple.com/documentation/storekit/in-app-purchase)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [Transaction](https://developer.apple.com/documentation/storekit/transaction)
- [currentEntitlements](https://developer.apple.com/documentation/storekit/transaction/currententitlements)
- [PassKit](https://developer.apple.com/documentation/passkit)
- [Offering Apple Pay in your app](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app)
- [PKPaymentAuthorizationController](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontroller)
- [Wallet](https://developer.apple.com/documentation/passkit/wallet)
- [PKAddPassesViewController](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontroller)
- [Authentication Services](https://developer.apple.com/documentation/authenticationservices)
- [Implementing user authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [ASAuthorizationAppleIDProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidprovider)
- [Security](https://developer.apple.com/documentation/security)
- [Using the keychain to manage user secrets](https://developer.apple.com/documentation/security/using-the-keychain-to-manage-user-secrets)
- [Restricting keychain item accessibility](https://developer.apple.com/documentation/security/restricting-keychain-item-accessibility)
- [Adding a password to the keychain](https://developer.apple.com/documentation/security/adding-a-password-to-the-keychain)
- [Item attribute keys and values](https://developer.apple.com/documentation/security/item-attribute-keys-and-values)
- [Local Authentication](https://developer.apple.com/documentation/localauthentication)
- [LAContext](https://developer.apple.com/documentation/localauthentication/lacontext)
- [CryptoKit](https://developer.apple.com/documentation/cryptokit)
- [DeviceCheck](https://developer.apple.com/documentation/devicecheck)
- [DCDevice](https://developer.apple.com/documentation/devicecheck/dcdevice)
- [DCAppAttestService](https://developer.apple.com/documentation/devicecheck/dcappattestservice)
- [Establishing your app’s integrity](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity)
- [Validating apps that connect to your server](https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server)
- [URL Loading System](https://developer.apple.com/documentation/foundation/url_loading_system)
- [Network](https://developer.apple.com/documentation/network)
