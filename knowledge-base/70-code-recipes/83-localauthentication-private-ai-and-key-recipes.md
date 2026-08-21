# LocalAuthentication, private-AI, and key-protection recipes

These are compile-oriented route sketches for a named target. Check SDK availability, target Info.plist, physical hardware, and the exact keychain/Secure Enclave threat model before shipping. The snippets never handle raw biometric data.

## 1. Wrap LAContext in a bounded async operation

Use a fresh context for a bounded action. The async wrapper converts the documented callback into an app-owned result; it does not change the system policy.

~~~swift
import LocalAuthentication

enum LocalUnlockError: Error {
    case unavailable
    case failed
}

@MainActor
func authenticate(
    policy: LAPolicy = .deviceOwnerAuthentication,
    reason: String
) async throws {
    let context = LAContext()
    var availabilityError: NSError?

    guard context.canEvaluatePolicy(policy, error: &availabilityError) else {
        throw availabilityError ?? LocalUnlockError.unavailable
    }

    defer { context.invalidate() }

    try await withCheckedThrowingContinuation { continuation in
        context.evaluatePolicy(
            policy,
            localizedReason: reason
        ) { success, error in
            if success {
                continuation.resume(returning: ())
            } else {
                continuation.resume(
                    throwing: error ?? LocalUnlockError.failed
                )
            }
        }
    }
}
~~~

Map the thrown error into a locked, canceled, unavailable, or retry state. Do not persist a generic “authenticated” Boolean as a permanent credential.

## 2. Map LAError into UI state

Keep the system error for diagnostics, but expose a safe app-owned state to SwiftUI.

~~~swift
import LocalAuthentication

enum UnlockSurfaceState: Equatable {
    case locked
    case checking
    case prompting
    case unlocked
    case canceled
    case unavailable
    case failed
    case lockedOut
    case expired
}

func surfaceState(for error: Error) -> UnlockSurfaceState {
    guard let authenticationError = error as? LAError else {
        return .failed
    }

    switch authenticationError.code {
    case .userCancel, .systemCancel, .appCancel:
        return .canceled
    case .biometryLockout:
        return .lockedOut
    case .biometryNotAvailable, .biometryNotEnrolled, .passcodeNotSet,
         .notInteractive:
        return .unavailable
    default:
        return .failed
    }
}
~~~

The exact set of codes can evolve. Compile this against the selected SDK and keep an unknown/default case so a new error does not unlock the resource.

## 3. Use the SwiftUI LocalAuthenticationView when available

Current LocalAuthentication documentation includes a SwiftUI view that represents policy evaluation. Guard it with the target’s real availability and keep a non-available fallback.

~~~swift
import LocalAuthentication
import SwiftUI

struct PrivateReviewUnlockView: View {
    @State private var state: UnlockSurfaceState = .locked
    let onUnlock: () -> Void

    var body: some View {
        Group {
            if #available(iOS 26.0, *) {
                LocalAuthenticationView(
                    "Unlock private review",
                    reason: Text("Use your device authentication to reveal this local review.")
                ) { result in
                    switch result {
                    case .success:
                        state = .unlocked
                        onUnlock()
                    case .failure(let error):
                        state = surfaceState(for: error)
                    }
                }
            } else {
                Button("Unlock private review") {
                    state = .checking
                    Task {
                        do {
                            try await authenticate(
                                reason: "Reveal this private local review."
                            )
                            state = .unlocked
                            onUnlock()
                        } catch {
                            state = surfaceState(for: error)
                        }
                    }
                }
            }
        }
        .accessibilityValue(String(describing: state))
    }
}
~~~

The exact availability for the selected platform and SDK must be verified. The view is an authentication interface, not a biometric-data API.

## 4. Read a Keychain item with access control

Use a Keychain access-control item when the protected value is a secret or token rather than a Secure Enclave private key.

~~~swift
import LocalAuthentication
import Security

enum KeychainSecretError: Error {
    case accessControl
    case save(OSStatus)
    case read(OSStatus)
}

func saveBiometryBoundSecret(
    _ secret: Data,
    account: String
) throws {
    guard let access = SecAccessControlCreateWithFlags(
        kCFAllocatorDefault,
        kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
        [.biometryCurrentSet],
        nil
    ) else {
        throw KeychainSecretError.accessControl
    }

    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: account,
        kSecAttrAccessControl as String: access,
        kSecValueData as String: secret
    ]

    let status = SecItemAdd(query as CFDictionary, nil)
    guard status == errSecSuccess else {
        throw KeychainSecretError.save(status)
    }
}

func loadBiometryBoundSecret(
    account: String,
    context: LAContext
) throws -> Data {
    context.localizedReason = "Unlock the private local context."

    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: account,
        kSecReturnData as String: true,
        kSecUseAuthenticationContext as String: context
    ]

    var result: CFTypeRef?
    let status = SecItemCopyMatching(query as CFDictionary, &result)
    guard status == errSecSuccess, let data = result as? Data else {
        throw KeychainSecretError.read(status)
    }
    return data
}
~~~

The production route should handle duplicate-item updates, deletion, enrollment changes, lockout, and a recovery policy. Do not log the Data or place it in a preview.

## 5. Generate a Secure Enclave signing key

Apple documents the Secure Enclave route for generated P-256 private keys. The private key cannot be imported or exported as plaintext.

~~~swift
import Security

enum SecureEnclaveError: Error {
    case accessControl
    case generation(String)
}

func generateSecureEnclaveKey(tag: Data) throws -> SecKey {
    guard let access = SecAccessControlCreateWithFlags(
        kCFAllocatorDefault,
        kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
        [.privateKeyUsage, .biometryCurrentSet],
        nil
    ) else {
        throw SecureEnclaveError.accessControl
    }

    let privateAttributes: [String: Any] = [
        kSecAttrIsPermanent as String: true,
        kSecAttrApplicationTag as String: tag,
        kSecAttrAccessControl as String: access
    ]
    let attributes: [String: Any] = [
        kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom,
        kSecAttrKeySizeInBits as String: 256,
        kSecAttrTokenID as String: kSecAttrTokenIDSecureEnclave,
        kSecPrivateKeyAttrs as String: privateAttributes
    ]

    var error: Unmanaged<CFError>?
    guard let key = SecKeyCreateRandomKey(
        attributes as CFDictionary,
        &error
    ) else {
        let message = error?
            .takeRetainedValue()
            .localizedDescription ?? "Secure Enclave key generation failed."
        throw SecureEnclaveError.generation(message)
    }
    return key
}
~~~

Use the private key through supported signing or key-exchange operations. Store only a reference/public key and app-owned metadata. For symmetric local-AI data encryption, use a deliberate CryptoKit/wrapping design rather than assuming the Secure Enclave stores arbitrary model data.

## 6. Persist a right and secret when the target supports it

Current LocalAuthentication documentation includes LARightStore and async persisted-right examples. Keep this route behind the actual target/SDK availability.

~~~swift
import LocalAuthentication

@available(iOS 26.0, *)
func savePrivateAISecret(_ secret: Data) async throws {
    let right = LARight()
    _ = try await LARightStore.shared.saveRight(
        right,
        identifier: "private-ai-context",
        secret: secret
    )
}

@available(iOS 26.0, *)
func loadPrivateAISecret() async throws -> Data {
    let right = try await LARightStore.shared.right(
        forIdentifier: "private-ai-context"
    )
    try await right.authorize(
        localizedReason: "Unlock the local AI context."
    )
    return try await right.secret.rawData
}
~~~

Do not use both an LARight and an unrelated Keychain item as hidden competing authorities. Bind the right identifier, user-facing purpose, removal, timeout, and sign-out behavior to the protected feature.

## 7. Gate a local-AI operation without leaking raw context

The app should unlock only the minimal context needed for the selected action.

~~~swift
struct LocalReviewInput: Sendable {
    let redactedText: String
    let source: String
    let createdAt: Date
}

enum LocalReviewResult: Equatable {
    case locked
    case insufficientContext
    case draft(String)
}

@MainActor
func runPrivateReview(
    loadInput: () throws -> LocalReviewInput,
    summarizeLocally: (LocalReviewInput) async throws -> String
) async -> LocalReviewResult {
    do {
        try await authenticate(
            reason: "Unlock the selected local context for review."
        )
        let input = try loadInput()
        guard !input.redactedText.isEmpty else {
            return .insufficientContext
        }
        let draft = try await summarizeLocally(input)
        return .draft(draft)
    } catch {
        return .locked
    }
}
~~~

In a real vault, loadInput should decrypt or retrieve the approved local context only after authentication, and the caller should clear the input/draft according to the timeout and privacy policy. Authentication does not approve a generated side effect.

## 8. Test pure state transitions

Use Swift Testing or XCTest for the app-owned state machine, then run device tests for the system.

~~~swift
import Testing

@Test
func cancelKeepsPrivateReviewLocked() {
    #expect(
        surfaceState(for: LAError(.userCancel)) == .canceled
    )
}

@Test
func lockoutDoesNotUnlockTheFeature() {
    #expect(
        surfaceState(for: LAError(.biometryLockout)) == .lockedOut
    )
}
~~~

These tests prove error mapping only. They do not prove Face ID/Touch ID/Optic ID, passcode lockout, Secure Enclave, Keychain behavior, LARightStore persistence, or a signed release.

## Sources

- [Local Authentication](https://developer.apple.com/documentation/localauthentication)
- [LAContext](https://developer.apple.com/documentation/localauthentication/lacontext)
- [LAPolicy](https://developer.apple.com/documentation/localauthentication/lapolicy)
- [LocalAuthenticationView](https://developer.apple.com/documentation/localauthentication/localauthenticationview)
- [LARightStore](https://developer.apple.com/documentation/localauthentication/larightstore)
- [Keychain Services](https://developer.apple.com/documentation/security/keychain-services)
- [Protecting keys with the Secure Enclave](https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave)
- [kSecAttrTokenIDSecureEnclave](https://developer.apple.com/documentation/security/ksecattrtokenidsecureenclave)
- [SecAccessControlCreateFlags](https://developer.apple.com/documentation/security/secaccesscontrolcreateflags)
- [Key Generation Attributes](https://developer.apple.com/documentation/security/key-generation-attributes)
- [NSFaceIDUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsfaceidusagedescription)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing](https://developer.apple.com/documentation/testing)
