# SwiftUI Security, Keychain, CryptoKit, and protected local-AI recipes

These are compile-oriented route sketches for an iOS 26 target. They intentionally keep Keychain, CryptoKit, Secure Enclave, SwiftUI, and optional Foundation Models responsibilities separate. Compile against the final SDK, inspect signed entitlements, and exercise the physical lock/biometry/device-key behavior before treating any recipe as production-ready.

## 1. Map Keychain status into an app-owned error

Do not expose raw `OSStatus` values as the user experience, but preserve them for redacted diagnostics.

~~~swift
import Security

enum ProtectedStoreError: Error, Equatable {
    case missing
    case duplicate
    case locked
    case denied
    case missingEntitlement
    case interactionNotAllowed
    case invalidData
    case status(OSStatus)
}

func mapKeychainStatus(_ status: OSStatus) -> ProtectedStoreError {
    switch status {
    case errSecItemNotFound:
        return .missing
    case errSecDuplicateItem:
        return .duplicate
    case errSecInteractionNotAllowed:
        return .interactionNotAllowed
    case errSecAuthFailed, errSecUserCanceled:
        return .denied
    case errSecMissingEntitlement:
        return .missingEntitlement
    case errSecDecode:
        return .invalidData
    default:
        return .status(status)
    }
}
~~~

The exact statuses exposed by a selected OS can vary. Keep a default path and make sure an unknown status cannot unlock a protected feature.

## 2. Store a small generic-password secret

Generic-password items are a useful Keychain route for small credentials and opaque key material that does not have a native `SecKey` representation. The descriptor is stable and the value remains out of ordinary app persistence.

~~~swift
import Foundation
import Security

struct GenericPasswordStore: Sendable {
    let service: String

    func add(
        _ value: Data,
        account: String,
        accessibility: CFString = kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
        synchronizable: Bool = false
    ) throws {
        var query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecAttrAccessible as String: accessibility,
            kSecAttrSynchronizable as String: synchronizable,
            kSecValueData as String: value
        ]

        let status = SecItemAdd(query as CFDictionary, nil)
        guard status != errSecDuplicateItem else {
            throw ProtectedStoreError.duplicate
        }
        guard status == errSecSuccess else {
            throw mapKeychainStatus(status)
        }
        query.removeValue(forKey: kSecValueData as String)
    }

    func read(account: String) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess else {
            throw mapKeychainStatus(status)
        }
        guard let data = result as? Data else {
            throw ProtectedStoreError.invalidData
        }
        return data
    }

    func update(_ value: Data, account: String) throws {
        let search: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
        let attributes: [String: Any] = [
            kSecValueData as String: value
        ]
        let status = SecItemUpdate(
            search as CFDictionary,
            attributes as CFDictionary
        )
        guard status == errSecSuccess else {
            throw mapKeychainStatus(status)
        }
    }

    func delete(account: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw mapKeychainStatus(status)
        }
    }
}
~~~

The `update` method intentionally changes only the value. Changing accessibility, access group, or synchronizability is a migration decision; create a new descriptor and perform a tested read/write transition rather than silently mutating the policy.

## 3. Create and read a user-presence-bound item

Use a protected Keychain item when the secret itself must be unavailable until the person satisfies the selected policy. The system owns the authentication UI.

~~~swift
import LocalAuthentication
import Security

func saveUserPresenceSecret(
    _ secret: Data,
    service: String,
    account: String
) throws {
    guard let access = SecAccessControlCreateWithFlags(
        kCFAllocatorDefault,
        kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
        [.userPresence],
        nil
    ) else {
        throw ProtectedStoreError.invalidData
    }

    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: service,
        kSecAttrAccount as String: account,
        kSecAttrAccessControl as String: access,
        kSecValueData as String: secret
    ]

    let status = SecItemAdd(query as CFDictionary, nil)
    guard status == errSecSuccess else {
        throw mapKeychainStatus(status)
    }
}

func readUserPresenceSecret(
    service: String,
    account: String,
    context: LAContext,
    reason: String
) throws -> Data {
    context.localizedReason = reason

    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: service,
        kSecAttrAccount as String: account,
        kSecReturnData as String: true,
        kSecUseAuthenticationContext as String: context
    ]

    var result: CFTypeRef?
    let status = SecItemCopyMatching(query as CFDictionary, &result)
    guard status == errSecSuccess else {
        throw mapKeychainStatus(status)
    }
    guard let data = result as? Data else {
        throw ProtectedStoreError.invalidData
    }
    return data
}
~~~

Create a fresh `LAContext` for a bounded action and invalidate it when the action ends. The protected item remains the authority; a SwiftUI success state must not be reused for an unrelated secret or indefinite session.

## 4. Seal an app-owned record with AES.GCM

Keep algorithm, version, key ID, nonce, ciphertext, and tag in a versioned envelope. Reconstruct associated data from the expected record identity instead of trusting a cleartext field supplied by the envelope.

~~~swift
import CryptoKit
import Foundation

struct ProtectedEnvelope: Codable, Sendable {
    let version: Int
    let algorithm: String
    let keyID: String
    let nonce: Data
    let ciphertext: Data
    let tag: Data
}

enum EnvelopeError: Error, Equatable {
    case unsupportedVersion
    case unsupportedAlgorithm
    case authenticationFailed
}

func sealRecord(
    _ plaintext: Data,
    using key: SymmetricKey,
    keyID: String,
    associatedData: Data
) throws -> ProtectedEnvelope {
    let box = try AES.GCM.seal(
        plaintext,
        using: key,
        authenticating: associatedData
    )

    return ProtectedEnvelope(
        version: 2,
        algorithm: "AES.GCM",
        keyID: keyID,
        nonce: Data(box.nonce),
        ciphertext: box.ciphertext,
        tag: box.tag
    )
}

func openRecord(
    _ envelope: ProtectedEnvelope,
    using key: SymmetricKey,
    associatedData: Data
) throws -> Data {
    guard envelope.version == 2 else {
        throw EnvelopeError.unsupportedVersion
    }
    guard envelope.algorithm == "AES.GCM" else {
        throw EnvelopeError.unsupportedAlgorithm
    }

    do {
        let nonce = try AES.GCM.Nonce(data: envelope.nonce)
        let box = try AES.GCM.SealedBox(
            nonce: nonce,
            ciphertext: envelope.ciphertext,
            tag: envelope.tag
        )
        return try AES.GCM.open(
            box,
            using: key,
            authenticating: associatedData
        )
    } catch {
        throw EnvelopeError.authenticationFailed
    }
}
~~~

The associated-data contract might be `recordID + schemaVersion + accountScope`. Its exact bytes are part of the protocol and must be stable across encoding, migration, and restore. Test altered ciphertext, tag, nonce, key, associated data, version, and truncation. A successful decryption must precede decoding or committing the record.

## 5. Keep a symmetric key in the Keychain

CryptoKit’s `SymmetricKey` is strongly typed, but the Keychain stores bytes. Use a dedicated account and policy; never store the key alongside the encrypted envelope in ordinary persistence.

~~~swift
import CryptoKit
import Foundation

func saveSymmetricKey(
    _ key: SymmetricKey,
    in store: GenericPasswordStore,
    account: String
) throws {
    let data = key.withUnsafeBytes { rawBuffer in
        Data(rawBuffer)
    }
    try store.add(
        data,
        account: account,
        accessibility: kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly
    )
}

func loadSymmetricKey(
    from store: GenericPasswordStore,
    account: String
) throws -> SymmetricKey {
    let data = try store.read(account: account)
    return SymmetricKey(data: data)
}
~~~

For a production vault, bind the key item to the right access-control policy rather than relying only on an app-owned unlock Boolean. If the key is rotated, store the key version with the envelope and migrate records deliberately.

## 6. Generate a Secure Enclave P-256 signing key

The Secure Enclave route is for supported private-key operations. It is not arbitrary secure storage for a model or symmetric key.

~~~swift
import CryptoKit
import Security

enum SecureKeyError: Error {
    case accessControlUnavailable
}

func makeSecureSigningKey() throws -> SecureEnclave.P256.Signing.PrivateKey {
    guard let access = SecAccessControlCreateWithFlags(
        kCFAllocatorDefault,
        kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
        [.privateKeyUsage, .userPresence],
        nil
    ) else {
        throw SecureKeyError.accessControlUnavailable
    }

    return try SecureEnclave.P256.Signing.PrivateKey(
        compactRepresentable: true,
        accessControl: access
    )
}

func signMessage(
    _ message: Data,
    with key: SecureEnclave.P256.Signing.PrivateKey
) throws -> Data {
    let digest = SHA256.hash(data: message)
    let signature = try key.signature(for: digest)
    return signature.rawRepresentation
}

func restoreSecureSigningKey(
    from representation: Data
) throws -> SecureEnclave.P256.Signing.PrivateKey {
    try SecureEnclave.P256.Signing.PrivateKey(
        dataRepresentation: representation
    )
}
~~~

Persist only the documented opaque representation and safe metadata in a protected Keychain item. Record the public key when a verifier needs it. Test unsupported hardware, key generation, operation authorization, restore, invalidation, and deletion on a real device. Do not assume that a Secure Enclave key can be recreated on another device from the same representation.

For key agreement, use the corresponding `SecureEnclave.P256.KeyAgreement.PrivateKey` route and derive a symmetric key from the returned shared secret through a documented context. Do not use a signing key for an unrelated protocol.

## 7. SwiftUI protection-state surface

Publish an app-owned state enum, not secrets or `SecKey` objects.

~~~swift
import SwiftUI

enum ProtectionState: Equatable {
    case locked
    case authenticating
    case unlocked(scope: String)
    case unavailable(String)
    case missing
    case invalidated
    case corrupt
    case proposalReady(sourceRevision: Int)
}

struct ProtectedStatusView: View {
    let state: ProtectionState
    let unlock: () -> Void
    let lock: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(title, systemImage: icon)
                .font(.headline)

            Text(detail)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            HStack {
                if case .unlocked = state {
                    Button("Lock", action: lock)
                } else {
                    Button("Unlock private workspace", action: unlock)
                        .buttonStyle(.borderedProminent)
                }
            }
        }
        .padding(20)
        .glassEffect(.regular, in: .rect(cornerRadius: 24))
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Private workspace")
        .accessibilityValue(detail)
    }

    private var title: String {
        switch state {
        case .locked: return "Locked"
        case .authenticating: return "Confirming access"
        case .unlocked: return "Open for this action"
        case .unavailable: return "Unavailable"
        case .missing: return "Key not found"
        case .invalidated: return "Recovery required"
        case .corrupt: return "Integrity check failed"
        case .proposalReady: return "Draft ready for review"
        }
    }

    private var detail: String {
        switch state {
        case .locked: return "Your private records remain closed on this device."
        case .authenticating: return "Confirm with the device authentication method."
        case .unlocked(let scope): return "Open for \(scope). Lock when finished."
        case .unavailable(let reason): return reason
        case .missing: return "This device has no key for this workspace."
        case .invalidated: return "The device security state changed."
        case .corrupt: return "The record failed its authenticity check."
        case .proposalReady(let revision): return "Local draft from source revision \(revision); nothing is saved yet."
        }
    }

    private var icon: String {
        switch state {
        case .locked: return "lock.fill"
        case .unlocked: return "lock.open.fill"
        case .proposalReady: return "sparkles"
        case .corrupt, .invalidated, .missing, .unavailable: return "exclamationmark.shield"
        case .authenticating: return "person.badge.key"
        }
    }
}
~~~

The exact glass API and availability must be compiled against the target SDK. The material is decoration and grouping; text and accessible state remain authoritative. Add reduced-transparency and reduced-motion checks if the surface uses more than a static glass cluster.

## 8. Validate a typed local-AI proposal before commit

Foundation Models APIs are availability-sensitive. Keep the model output typed and app-validated; the security coordinator still owns unlock, save, delete, and key operations.

~~~swift
import Foundation

struct PrivateSummaryProposal: Codable, Sendable, Equatable {
    let sourceRevision: Int
    let title: String
    let bullets: [String]
    let confidence: Double
}

enum ProposalValidationError: Error {
    case emptyTitle
    case invalidConfidence
    case staleSource
    case tooManyBullets
}

func validate(
    _ proposal: PrivateSummaryProposal,
    currentSourceRevision: Int
) throws {
    guard !proposal.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
        throw ProposalValidationError.emptyTitle
    }
    guard (0...1).contains(proposal.confidence) else {
        throw ProposalValidationError.invalidConfidence
    }
    guard proposal.sourceRevision == currentSourceRevision else {
        throw ProposalValidationError.staleSource
    }
    guard proposal.bullets.count <= 8 else {
        throw ProposalValidationError.tooManyBullets
    }
}
~~~

The model may produce this proposal; it may not produce a Keychain query, access group, private key, account authorization, or delete command. When the proposal is accepted, encrypt the edited, validated output and record the new source/output revision.

## 9. Swift Testing policy fixtures

Pure envelope and proposal fixtures are useful in Swift Testing. They do not replace physical security or release evidence.

~~~swift
import CryptoKit
import Testing

struct ProtectedRouteTests {
    @Test("authenticated envelope round trips")
    func envelopeRoundTrip() throws {
        let key = SymmetricKey(size: .bits256)
        let plaintext = Data("private fixture".utf8)
        let aad = Data("record:1:schema:2".utf8)

        let envelope = try sealRecord(
            plaintext,
            using: key,
            keyID: "fixture-key-v2",
            associatedData: aad
        )
        #expect(try openRecord(envelope, using: key, associatedData: aad) == plaintext)
    }

    @Test("altered associated data fails authentication")
    func alteredAssociatedDataFails() throws {
        let key = SymmetricKey(size: .bits256)
        let envelope = try sealRecord(
            Data("private fixture".utf8),
            using: key,
            keyID: "fixture-key-v2",
            associatedData: Data("record:1:schema:2".utf8)
        )

        #expect(
            (try? openRecord(
                envelope,
                using: key,
                associatedData: Data("record:2:schema:2".utf8)
            )) == nil
        )
    }

    @Test("stale proposal cannot be committed")
    func staleProposalFails() {
        let proposal = PrivateSummaryProposal(
            sourceRevision: 4,
            title: "Draft",
            bullets: ["Review"],
            confidence: 0.8
        )
        #expect(
            (try? validate(proposal, currentSourceRevision: 5)) == nil
        )
    }
}
~~~

Add separate physical/manual fixtures for device lock, passcode, biometry cancellation/lockout, biometric enrollment changes, access-group entitlements, Keychain migration, Secure Enclave support, archive/TestFlight, and local-model availability. Test doubles can prove reducers and error mapping; they cannot prove hardware security or Apple system behavior.

## Sources

- [Keychain services](https://developer.apple.com/documentation/security/keychain-services)
- [Keychain items](https://developer.apple.com/documentation/security/keychain-items)
- [Storing keys in the keychain](https://developer.apple.com/documentation/security/storing-keys-in-the-keychain)
- [Storing CryptoKit keys in the keychain](https://developer.apple.com/documentation/cryptokit/storing-cryptokit-keys-in-the-keychain)
- [Sharing access to keychain items among a collection of apps](https://developer.apple.com/documentation/security/sharing-access-to-keychain-items-among-a-collection-of-apps)
- [Restricting keychain item accessibility](https://developer.apple.com/documentation/security/restricting-keychain-item-accessibility)
- [Item attribute keys and values](https://developer.apple.com/documentation/security/item-attribute-keys-and-values)
- [SecAccessControlCreateFlags](https://developer.apple.com/documentation/security/secaccesscontrolcreateflags)
- [Apple CryptoKit](https://developer.apple.com/documentation/cryptokit)
- [AES.GCM](https://developer.apple.com/documentation/cryptokit/aes/gcm)
- [ChaChaPoly](https://developer.apple.com/documentation/cryptokit/chachapoly)
- [Curve25519](https://developer.apple.com/documentation/cryptokit/curve25519)
- [P256](https://developer.apple.com/documentation/cryptokit/p256)
- [SecureEnclave.P256](https://developer.apple.com/documentation/cryptokit/secureenclave/p256)
- [Protecting keys with the Secure Enclave](https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing in Swift](https://developer.apple.com/documentation/testing)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
