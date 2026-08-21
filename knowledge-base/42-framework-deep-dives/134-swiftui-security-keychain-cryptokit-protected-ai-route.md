# SwiftUI Security, Keychain, CryptoKit, and protected local-AI route

An on-device AI feature still needs an explicit security architecture. “Runs locally” describes where inference happens; it does not decide which data is retained, who can unlock it, how keys are created, whether a secret migrates to another device, or what happens when a device is locked, restored, reset, or loses a key.

The Apple-native route is a set of deliberately separate authorities:

```text
user outcome
    -> identify the secret and trust boundary
    -> choose Keychain item class/accessibility/access group
    -> add optional SecAccessControl / user-presence requirement
    -> use CryptoKit for a defined authenticated protocol
    -> use Secure Enclave only for supported private-key operations
    -> project state into SwiftUI and Liquid Glass
    -> optionally review a typed local-AI proposal
    -> rotate, delete, recover, and verify the signed release
```

A keychain read, successful biometric evaluation, ciphertext, signature, Secure Enclave key reference, or local-model response is not by itself proof of account identity, authorization, confidentiality, or production security. Recipes in this review are compile-oriented starting points; they must be checked against the final iOS 26 SDK, target entitlements, physical hardware, and the actual threat model.

## Choose the smallest security lane

| Product need | Apple route | Boundary that must stay explicit |
| --- | --- | --- |
| Small password, token, refresh credential, or app-owned identifier | Keychain Services generic-password item | Item class, accessibility, access group, migration, deletion, and redacted diagnostics |
| Secret shared by an app and its extension or sibling app | Keychain access group | Every target must be signed with the matching entitlement; an App Group container is not automatically the same authority |
| Secret that should follow a person through iCloud Keychain | Synchronizable Keychain item | Sync changes device and recovery semantics; do not use it for a device-bound local vault without an explicit product decision |
| Secret that must be unavailable while locked or without user presence | Keychain `SecAccessControl` | Access-control prompt, passcode/biometry policy, cancellation, lockout, enrollment changes, and fallback |
| Encrypt app-owned records at rest | CryptoKit AEAD plus a separately managed symmetric key | Algorithm, key origin, version, nonce uniqueness, associated data, tamper behavior, rotation, and deletion |
| Sign or perform elliptic-curve key exchange without exposing a private key | CryptoKit `SecureEnclave.P256` | Hardware support, P-256-only boundary, generated-key lifecycle, key reference recovery, and operation authorization |
| Derive a shared key from a peer exchange | CryptoKit `P256`, `Curve25519`, or a selected protocol | Peer authentication, key derivation context, replay/rotation, and server or peer verification |
| Protect a private on-device AI workspace | Keychain-gated key plus AEAD-encrypted app-owned data | The model is not the security authority; decrypt only after a real gate and keep raw context out of logs and unnecessary model prompts |
| Prove app-instance integrity to a service | DeviceCheck/App Attest | Server challenge and validation; this is not replaced by a local Keychain or biometric result |

Do not begin with “which encryption API should I call?” Begin with the protected object, its owner, its lifetime, the allowed devices, the recovery story, and the action that should be possible after a successful gate.

## Keychain Services is protected small-item storage

Apple documents Keychain Services as a way to store small chunks of user data, including passwords, credentials, cryptographic keys, certificates, and identities. Keychain Services manages an encrypted database and lets the app add, find, update, and delete items through query dictionaries. The item’s attributes are part of the retrieval and policy contract, not incidental metadata.

On iOS, common item classes include:

- `kSecClassGenericPassword` for app-owned tokens, small secrets, and opaque key material that has no native `SecKey` representation;
- `kSecClassInternetPassword` for internet-password semantics when the server, account, and protocol attributes actually fit that model;
- `kSecClassKey` for native keychain keys and `SecKey` representations; and
- certificate, identity, and other classes when the product explicitly uses those Security services.

Use stable, namespaced attributes such as service, account, application label, key version, and access group. Keep a schema version in app-owned metadata or in the item’s label/description only when that metadata is safe to expose. Never log the value, a private-key representation, an authentication context, or a complete query containing secret data.

Keychain storage does not replace app-owned data lifecycle design. Define what happens on:

| Event | Required decision |
| --- | --- |
| First install | Create the item lazily at the first feature action, not at launch, unless the workflow genuinely needs it immediately. |
| Duplicate add | Decide whether duplicate means idempotent update, conflict, or an old-version item that must be migrated. |
| Device lock/restart | Use the chosen accessibility class and show a locked/unavailable state rather than treating it as corruption. |
| Backup/restore or device migration | Decide whether the secret may migrate. `ThisDeviceOnly` classes intentionally change that behavior. |
| App update | Preserve the item identifier and migrate only when the schema or algorithm requires it. |
| Sign out | Delete or revoke the item that represents the session; do not delete unrelated app/extension secrets by broad query. |
| Account deletion | Remove local copies, encrypted envelopes, key references, sync projections, caches, logs, and server records covered by the product policy. |
| Access-group change | Treat it as a migration and signed-entitlement event, not a string edit. |
| Key loss or invalidation | Create a new key only after deciding whether old data is recoverable, discardable, or requires account recovery. |

`SecItemCopyMatching`, `SecItemUpdate`, and `SecItemDelete` return status codes. Map the status into an app-owned enum such as `missing`, `locked`, `denied`, `duplicate`, `missingEntitlement`, `interactionNotAllowed`, `invalidData`, and `unexpected(OSStatus)`. Avoid presenting every failure as “wrong password.” A locked item, a missing key, and a bad ciphertext are different user and recovery states.

## Accessibility classes express device-state policy

The `kSecAttrAccessible` value controls when the system makes an item available relative to the device lock state and restart. Apple’s current documentation lists classes including:

| Policy | Suitable question | Important consequence |
| --- | --- | --- |
| `WhenUnlocked` | Does the feature only need the secret while the person has unlocked the device? | A locked device cannot provide the item. |
| `AfterFirstUnlock` | Does a background operation need the item after the first post-restart unlock? | The item is unavailable after restart until the first unlock. |
| `WhenUnlockedThisDeviceOnly` | Should an unlocked foreground feature use a secret that must not migrate? | The item does not migrate to another device. |
| `WhenPasscodeSetThisDeviceOnly` | Should a particularly sensitive foreground secret require a device passcode and remain device-bound? | The item is unavailable without a passcode and is removed if the passcode is disabled; it does not migrate. |
| `Always` variants | Is access while locked truly required? | Apple marks the least restrictive options as a poor default; use only for a documented need. |

The “most restrictive” class is not always correct. A notification or background-refresh feature may need an `AfterFirstUnlock` credential, while a local vault that only opens after an intentional user action may prefer a passcode-bound, device-only class. Document the choice and test the lock, restart, first-unlock, background, restore, and passcode-change paths.

`kSecAttrAccessControl` is a different, stronger policy surface for conditions such as user presence, biometry, a current biometric set, a passcode, or an application password. Apple documents that the access-control attribute is mutually exclusive with the older `kSecAttrAccess` attribute. Build the access-control object deliberately and keep the reason shown to the person aligned with the protected action.

Do not assume that a prior `LAContext` success automatically authorizes an unrelated Keychain read. If the secret itself must be protected, bind the Keychain query to the intended authentication context or let the item’s access control invoke the system policy. Keep one source of truth for the protected action so that a “unlocked” SwiftUI Boolean cannot outlive the authorization it represents.

## Access groups, extensions, and synchronizability

Keychain items belong to one access group. An app can belong to multiple groups through its signed entitlements, and sibling targets from the same development team can share an item only when the target configuration and access group agree. Apple documents that an attempt to use a group to which the target does not belong fails with `errSecMissingEntitlement`; a group name in source code is not evidence that the signed target can use it.

For an app plus widget, watch companion, App Clip, or extension, write a target matrix:

| Target | Needs the secret? | Access group | Accessibility | Read/write authority |
| --- | --- | --- | --- | --- |
| Main app | Yes | Default or explicit group | Feature-specific | Owner |
| Widget | Usually no raw secret | Prefer a redacted projection or app-owned shared container | No secret unless necessary | Read-only projection |
| Share/intent extension | Only for a user-started action | Exact signed group | Short-lived | Narrow action |
| Watch companion | Depends on the product | Explicit companion strategy | Test separately | No assumption of live availability |
| App Clip | Only when the route and OS support it | Exact Clip/full-app boundary | Short-lived | Handoff or limited scope |

An App Group container is useful for shared non-secret state, but do not put the secret in a shared file merely because the targets can see the container. Keep the Keychain access group and App Group data boundary distinct.

Synchronizable items can participate in iCloud Keychain behavior. That can be appropriate for a user credential that should follow their Apple Account/device set, but it is usually the wrong default for a device-bound local-AI vault, a key tied to a physical sensor, or a secret whose recovery policy intentionally excludes migration. Test delayed sync, conflict/duplicate behavior, sign-out, account changes, and a device without the expected iCloud state. A local success is not evidence that another device can or should read the item.

## CryptoKit defines cryptographic operations, not product authorization

Apple recommends CryptoKit for common cryptographic operations such as secure digests, message authentication, symmetric encryption, public-key signatures, and key exchange. It provides strongly typed keys and sealed boxes and handles sensitive memory more safely than ad-hoc raw-pointer code. It still does not define the application’s identity, access policy, key rotation, server protocol, or deletion behavior.

For new app-owned encrypted data, prefer an authenticated-encryption design that is documented as a protocol:

```text
algorithm identifier + schema version
    + key identifier / key version
    + nonce
    + ciphertext
    + authentication tag
    + authenticated associated data
```

`AES.GCM` and `ChaChaPoly` both produce a sealed box containing ciphertext, an authentication tag, and a nonce. Associated data can authenticate cleartext context such as record type, user scope, schema version, or key version without encrypting it. On open, authentication must succeed before the app decodes or commits the plaintext. Tampered ciphertext, wrong key, wrong associated data, and unsupported version should produce explicit failures.

Nonce handling is a protocol requirement. With a fixed symmetric key, do not reuse a nonce in a way that violates the selected algorithm’s contract. Generate or manage nonces through the selected CryptoKit API, store the nonce with the sealed envelope when needed, and test repeated-seal, restore, retry, crash, and key-rotation paths. A nonce is not the secret key, but it is part of the authenticity and decryption contract.

Use the cryptographic primitive that matches the job:

| Job | Candidate | Do not infer |
| --- | --- | --- |
| Confidentiality plus integrity for an app-owned record | `AES.GCM` or `ChaChaPoly` | Encryption does not grant authorization or prevent a compromised process from reading plaintext after unlock. |
| Digest or content identity | `SHA256`/another documented hash | A hash is not encryption and does not prove the source was authorized. |
| Message authentication with a shared key | `HMAC` | A shared HMAC key needs a safe storage and rotation boundary. |
| Symmetric key derivation from a shared secret | `HKDF` | HKDF is not a password-hashing or account-authentication system. |
| Signature | `P256.Signing`, `Curve25519.Signing`, or a selected protocol | A valid signature proves possession of a key, not that the signer is the correct account. |
| Key agreement | `P256.KeyAgreement` or `Curve25519.KeyAgreement` | Agreement needs peer authentication, context binding, and replay/rotation policy. |
| Hybrid or post-quantum protocol | Current CryptoKit HPKE/ML-KEM/ML-DSA surfaces when the target supports them | A new or beta API requires an exact SDK, platform, protocol, and server review. |

Do not invent password encryption, nonce formats, certificate validation, or “secure” obfuscation. If a product needs password-based encryption, account recovery, or network identity, select and document a reviewed protocol and server boundary.

## Store CryptoKit keys with a type-preserving bridge

CryptoKit key types do not all map to one native Keychain representation. Apple’s “Storing CryptoKit Keys in the Keychain” sample distinguishes NIST keys that can use an X9.63/`SecKey` representation from key types such as Curve25519 that are stored as generic password data. The type used to reconstruct a key must match the type used to store it; loading bytes under the wrong algorithm is not a safe migration.

Treat a stored key record as:

```text
key identifier
algorithm and purpose
representation kind: native SecKey or generic password bytes
schema/version
accessibility/access-control policy
creation and rotation metadata
```

Keep only public key material or an opaque encoded private-key representation where the selected API explicitly supports restoring the key. Never export or log a Secure Enclave private key as plaintext. For symmetric keys, protect the keychain item with the same or stronger access policy as the encrypted data and keep it separate from ordinary SwiftData records.

## Secure Enclave is a constrained private-key boundary

Apple describes the Secure Enclave as a hardware-based key manager isolated from the main processor. The current documented `SecureEnclave.P256` route supports NIST P-256 signing and key agreement. The private key is generated by the Secure Enclave and is used through operations whose output is returned to the app; the app does not handle the plaintext private key.

The constraints matter:

- hardware support is required;
- the supported Secure Enclave elliptic-curve route is P-256, not an arbitrary curve or arbitrary symmetric model key;
- pre-existing plaintext private keys cannot be imported into the Secure Enclave;
- signing and key agreement are the supported purposes, with symmetric encryption possible by deriving a shared secret; and
- an encoded key representation can be persisted and reconstructed through the documented CryptoKit API, but it is an opaque key reference/representation with its own Keychain and invalidation lifecycle—not a guarantee that the key can be recovered on every device.

Use Secure Enclave when a private signing or key-agreement operation genuinely benefits from hardware isolation. Do not use it as a place to store a large AI database, model weights, arbitrary plaintext, or a generic symmetric key. A common local-vault design is:

```text
Secure Enclave P-256 key
    -> signing or key agreement
    -> derived/wrapped symmetric key
    -> CryptoKit AEAD over app-owned data
    -> Keychain policy and deletion/recovery
```

If the person changes the biometric enrollment and the policy uses `biometryCurrentSet`, or if the passcode/key is lost, the key may no longer be usable. The app must state whether the vault is recoverable through an account, intentionally device-bound, or safely discardable. Do not silently generate a replacement key and present old encrypted data as still available.

## A protected local-AI vault

Use a local-AI security architecture with four separate stages:

1. **Collect.** Keep raw user data in the narrowest app-owned store. Do not copy it into analytics, a shared extension container, or a prompt unless required.
2. **Unlock.** Perform the actual Keychain/SecAccessControl/Secure Enclave operation at the user action boundary. A SwiftUI state flag is only a projection of that result and should expire when the protected task ends.
3. **Transform.** Decrypt or derive only the feature window needed for the current operation. Keep plaintext lifetime short and prevent logging of raw context, key bytes, or generated output that contains private data.
4. **Review.** Let Foundation Models or another on-device model propose a typed summary, classification, or transformation. Validate the proposal against deterministic app-owned rules and require confirmation before a side effect such as export, sharing, deletion, or account action.

For example:

```text
Keychain-gated encrypted journal record
    -> short-lived plaintext feature window
    -> deterministic redaction / schema validation
    -> optional on-device summary proposal
    -> user review
    -> encrypted save or explicit export
```

The model is not an authorization layer. It must not decide that a Keychain error is safe to ignore, invent an account ID, unlock a record, choose an access group, rotate a key, or confirm that deletion is complete. When Foundation Models is unavailable, the feature should fall back to a deterministic local summary or a clear “AI unavailable” state.

## SwiftUI and Liquid Glass trust surfaces

Security UI should be quiet, specific, and reversible. A good native screen makes the protected object and next action understandable:

```text
Private workspace
    -> current protection state and last verified time
    -> protected data count / redacted metadata
    -> Unlock or Lock action
    -> key/device/recovery explanation
    -> AI draft or summary marked as proposal
    -> Delete, export, and recovery controls
```

Use standard SwiftUI controls, labels, confirmation dialogs, alerts, forms, and `ContentUnavailableView` states before inventing a custom lock surface. Liquid Glass can group the primary status and action cluster, but it should not be used to blur the meaning of a security state or to make a biometric prompt look like an app-owned scanner. Use `.glassEffect` and related glass-container APIs on a small, stable surface; keep secret values and recovery instructions readable when transparency is reduced.

Distinguish states such as:

| State | User-facing meaning |
| --- | --- |
| Locked | The protected operation has not been authorized for this session. |
| Needs device passcode | The selected Keychain class or access control requires a passcode. |
| User presence required | The system will ask for the person’s approved authentication method. |
| Unavailable | The target, hardware, policy, or current lock state cannot satisfy the route. |
| Missing | No item/key exists for this app-owned identifier. |
| Invalidated | The key exists conceptually but cannot be used after a policy or device change. |
| Corrupt | The envelope or associated data fails validation/authentication. |
| Proposal ready | Local AI produced a reviewable result; no side effect has happened. |
| Saved | The app completed its own authenticated write and can point to the record revision. |

Accessibility must not be an afterthought. Provide text and control alternatives to a lock animation, announce errors without exposing secrets, use Dynamic Type-compatible layouts, support VoiceOver, Switch Control, Voice Control, keyboard/pointer input, Increase Contrast, Reduce Transparency, Reduce Motion, and localization. Do not use green glass as the sole indicator that a secret is protected.

## Verification boundary

| Claim | Minimum evidence |
| --- | --- |
| The target can use the item | Built entitlements, bundle ID/team mapping, item class, and a real Keychain add/read/update/delete result. |
| The secret is unavailable under the intended conditions | Physical lock/restart/passcode/biometry/denial tests with the exact accessibility and access-control policy. |
| Sibling targets share only what they should | App/extension/watch target matrix, signed access groups, and redacted cross-target read/write evidence. |
| Synchronization behavior is deliberate | Device pair/account state, delayed sync/conflict/revoke tests, and proof that device-only items do not silently migrate. |
| Encryption detects tampering | Known-answer round trip, wrong key, wrong AAD, altered nonce/ciphertext/tag, unsupported version, and duplicate/retry fixtures. |
| Key material is type-safe | Algorithm/representation metadata and a successful same-type reconstruction; mismatched-type rejection fixture. |
| Secure Enclave is actually used | Physical supported device, key generation, operation success, no plaintext export/log, key invalidation/recovery test, and target entitlement/artifact review. |
| Local AI remains subordinate to security | Model unavailable/refusal/stale/wrong-schema fixtures, deterministic gate, no raw-secret logging, and confirmation before side effects. |
| The native screen is accessible | Complete VoiceOver/Dynamic Type/contrast/reduced-effects/keyboard task with locked, denied, missing, corrupt, and proposal states. |
| Release configuration is trustworthy | Archive inspection, signed entitlements/Info.plist, TestFlight install, physical retest, and deletion/recovery evidence. |

The companion [protected-data design review](../21-design-deep-dives/162-swiftui-security-keychain-cryptokit-protected-ai-route-design.md), [route worksheet](../50-capability-recipes/165-swiftui-security-keychain-cryptokit-protected-ai-route.md), [proof matrix](../60-verification/159-swiftui-security-keychain-cryptokit-protected-ai-proof-matrix.md), and [code recipes](../70-code-recipes/177-swiftui-security-keychain-cryptokit-protected-ai-recipes.md) turn this review into reusable app-build artifacts.

## Sources

- [Keychain services](https://developer.apple.com/documentation/security/keychain-services)
- [Keychain items](https://developer.apple.com/documentation/security/keychain-items)
- [Storing keys in the keychain](https://developer.apple.com/documentation/security/storing-keys-in-the-keychain)
- [Storing CryptoKit keys in the keychain](https://developer.apple.com/documentation/cryptokit/storing-cryptokit-keys-in-the-keychain)
- [Sharing access to keychain items among a collection of apps](https://developer.apple.com/documentation/security/sharing-access-to-keychain-items-among-a-collection-of-apps)
- [Configuring keychain sharing](https://developer.apple.com/documentation/xcode/configuring-keychain-sharing)
- [Restricting keychain item accessibility](https://developer.apple.com/documentation/security/restricting-keychain-item-accessibility)
- [Item attribute keys and values](https://developer.apple.com/documentation/security/item-attribute-keys-and-values)
- [SecAccessControlCreateFlags](https://developer.apple.com/documentation/security/secaccesscontrolcreateflags)
- [kSecAttrAccessControl](https://developer.apple.com/documentation/security/ksecattraccesscontrol)
- [Apple CryptoKit](https://developer.apple.com/documentation/cryptokit)
- [Performing common cryptographic operations](https://developer.apple.com/documentation/cryptokit/performing_common_cryptographic_operations)
- [AES.GCM](https://developer.apple.com/documentation/cryptokit/aes/gcm)
- [ChaChaPoly](https://developer.apple.com/documentation/cryptokit/chachapoly)
- [Curve25519](https://developer.apple.com/documentation/cryptokit/curve25519)
- [P256](https://developer.apple.com/documentation/cryptokit/p256)
- [HKDF](https://developer.apple.com/documentation/cryptokit/hkdf)
- [SecureEnclave](https://developer.apple.com/documentation/cryptokit/secureenclave)
- [SecureEnclave.P256](https://developer.apple.com/documentation/cryptokit/secureenclave/p256)
- [Protecting keys with the Secure Enclave](https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
