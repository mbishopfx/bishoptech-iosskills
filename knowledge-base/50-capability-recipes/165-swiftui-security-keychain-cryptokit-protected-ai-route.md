# SwiftUI Security, Keychain, CryptoKit, and protected local-AI route

Use this worksheet when an app needs to keep credentials, encrypted local records, private model context, or device-bound signing material behind Apple-native security APIs. It is a route selector and evidence contract, not a promise that one API makes the whole product secure.

## Route card

| Field | Decision to record |
| --- | --- |
| User outcome | What becomes possible after the protected operation succeeds? |
| Protected object | Token, record envelope, symmetric key, P-256 private key, model context, or other small secret |
| Authority | Device security state, app account/server, Apple Account/iCloud Keychain, or a combination |
| Device scope | Migrates, synchronizes, stays on this device, or is recoverable only through an account |
| Storage | Keychain item class, file/SwiftData envelope, App Group projection, or external server |
| Access policy | Locked/unlocked, passcode, user presence, biometry-any, current biometric set, application password |
| Cryptography | AEAD/signature/key agreement, algorithm/version, key origin, nonce/AAD policy |
| AI role | None, local deterministic transform, typed on-device proposal, or reviewed provider fallback |
| Commit boundary | Exactly which user action writes, exports, deletes, or triggers a side effect |
| Recovery | Missing item, invalidated key, changed passcode/biometry, reinstall, device migration, sync delay, account deletion |
| Proof | Target entitlements, physical device, lock/biometry, tamper, migration, UI accessibility, archive/TestFlight |

## Select the lane

```text
Does the product store a small secret or key reference?
  yes -> Keychain Services

Must the item be gated by a user/device policy?
  yes -> SecAccessControl + an explicit access reason

Does the product encrypt app-owned records?
  yes -> CryptoKit AEAD envelope + separately managed key

Does it require a private signing or key-agreement key that should not be plaintext in app memory?
  yes -> SecureEnclave.P256 on supported hardware

Does another app target or extension need the value?
  yes -> exact Keychain access-group target map; prefer a redacted projection when possible

Does it need to follow the person’s devices?
  yes -> evaluate synchronizability and recovery; do not combine with a device-only policy casually

Does local AI need protected context?
  yes -> unlock -> decrypt bounded window -> typed proposal -> validate/review -> commit
```

Avoid a “universal secure store” abstraction that silently selects an accessibility class, sync policy, or algorithm. Make those decisions visible in the route manifest and tests.

## Target and entitlement manifest

Create this before implementation:

```yaml
targets:
  - name: App
    bundle_id: com.example.app
    keychain_access_groups:
      - $(AppIdentifierPrefix)com.example.app.private
    app_groups: []
    reads:
      - local-vault-key-v2
    writes:
      - local-vault-key-v2
  - name: ShareExtension
    bundle_id: com.example.app.share
    keychain_access_groups:
      - $(AppIdentifierPrefix)com.example.app.private
    reads:
      - redacted-session-token
    writes: []
policy:
  item_class: generic-password
  accessibility: when-passcode-set-this-device-only
  synchronizable: false
  access_control: user-presence
crypto:
  envelope: aes-gcm
  version: 2
  associated_data: record-id-and-schema
  key_origin: app-generated-keychain-item
ai:
  provider: on-device-only
  raw-secret-input: false
  commit: human-review-required
```

The manifest is not a secret and can be reviewed in the project. Never commit actual credentials, Keychain values, signing keys, or private-key representations.

## Data contracts

Keep the Keychain record, encrypted envelope, and UI state separate.

### Keychain descriptor

```text
SecretDescriptor
    id: stable app-owned identifier
    itemClass: genericPassword / key / other selected class
    service/account/label: query identity
    accessibility: exact device-state policy
    accessControl: optional user-presence/biometry/passcode policy
    accessGroup: exact signed group or app default
    synchronizable: explicit true/false decision
    algorithm: purpose and algorithm identifier
    version: migration version
```

The descriptor describes how to find and use an item. It must not contain the secret value.

### Authenticated envelope

```text
ProtectedEnvelope
    schemaVersion
    algorithm
    keyID / keyVersion
    nonce
    ciphertext
    authenticationTag
    associatedData contract
    sourceRevision
```

The envelope can live in SwiftData, a protected file, or another app-owned store. Store only the ciphertext and safe metadata there. The symmetric key belongs in the Keychain or is derived through a reviewed key-agreement route.

### UI projection

```text
ProtectionState
    locked
    authenticating
    unlocked(scope, expiresAt)
    unavailable(reason)
    missing
    invalidated
    corrupt
    proposalReady(sourceRevision, provider)
    saved(revision)
```

The UI projection should never expose `Data` containing a secret, a CryptoKit private key, a `SecKey`, or a complete Keychain query. It should carry safe labels, scope, revision, and an actionable error.

## Keychain policy decision table

| Question | Route choice | Test |
| --- | --- | --- |
| Only foreground after unlock? | `WhenUnlocked` or `WhenUnlockedThisDeviceOnly` | Lock/unlock and backgrounding |
| Background after first unlock? | An appropriate `AfterFirstUnlock` class | Restart, before first unlock, and background delivery |
| No migration and passcode required? | `WhenPasscodeSetThisDeviceOnly` | No passcode, passcode disable, backup restore, new device |
| User presence at read time? | `SecAccessControl` with an explicit flag and `kSecUseAuthenticationContext` where appropriate | Allow, cancel, deny, lockout, enrollment change |
| Shared extension/sibling target? | Keychain access group with matching signed entitlements | Archive each target and run a real cross-target action |
| iCloud Keychain desired? | Synchronizable item only after recovery/sync review | Two devices, account changes, delayed/conflicting results |
| Device-bound local AI? | Non-synchronizable, device-only protected key | Reinstall, restore, migration, missing-key UI |

`kSecAttrAccessControl` and legacy `kSecAttrAccess` are not interchangeable. Pick one policy route and preserve it through migration. A successful access-control prompt does not make a server account session valid.

## Lifecycle route

```text
idle
  -> explain purpose
  -> request the least-privilege system access needed
  -> build/locate Keychain item
  -> authenticate only at the protected action
  -> read key / perform Secure Enclave operation
  -> decrypt bounded envelope
  -> project safe state
  -> edit or generate a proposal
  -> validate deterministic invariants
  -> user confirms
  -> encrypt and commit new revision
  -> clear plaintext caches
  -> lock / expire / teardown
```

At every failure, retain the last known protected state. Do not replace a valid old envelope until the new envelope has passed encryption/authentication and the commit is durable. If key rotation is required, retain a versioned decrypt path only for the documented migration window, then delete the old key/material according to the product policy.

## Local-AI route

Keep the model behind the security coordinator:

```text
user selects records
    -> app confirms scope and unlocks the selected key
    -> app decrypts only the bounded feature window
    -> app redacts unnecessary fields and attaches source revision
    -> optional Foundation Models session produces typed proposal
    -> app validates schema, ranges, source revision, and policy
    -> person reviews / edits / rejects
    -> app encrypts and commits accepted output
```

The model must not:

- choose a Keychain access group or accessibility class;
- produce a private key, token, account ID, or authorization decision;
- bypass a failed or cancelled authentication operation;
- decide that a ciphertext or signature is valid without the app’s verifier;
- delete the source record without a separate confirmation; or
- silently move private context to a remote provider.

Use `Foundation Models` only when the target/device/model availability is true. A deterministic summary or explicit unavailable state is a valid fallback. Record provider, source revision, model availability, and acceptance status in app-owned metadata—not raw secret content.

## SwiftUI and Liquid Glass composition

Use an observable coordinator or actor to own Keychain/CryptoKit operations, then publish only `ProtectionState` and safe projections to SwiftUI. A screen can be composed as:

```text
NavigationStack
  -> ScrollView
      -> purpose header
      -> protection status card
      -> primary Unlock/Lock button
      -> redacted record scope
      -> local proposal review card
      -> recovery and deletion section
```

Apply Liquid Glass to the small status/action group if it improves hierarchy. Keep errors, state text, and destructive consequences readable under reduced transparency. Use ordinary `Button`, `Label`, `Form`, `alert`, `confirmationDialog`, `sheet`, and `ContentUnavailableView` semantics so the feature remains native across iPhone/iPad sizes and input modes.

## Evidence package

Save one redacted evidence package per target:

```text
security-route/
  route-manifest.yaml
  target-entitlements-redacted.plist
  built-info-plist-redacted.plist
  keychain-policy-matrix.md
  lifecycle-log-redacted.jsonl
  crypto-known-answer-fixtures.json
  tamper-and-replay-results.md
  physical-device-lock-biometry-results.md
  secure-enclave-key-lifecycle.md
  extension-access-group-results.md
  local-ai-privacy-and-fallback-results.md
  accessibility-results.md
  archive-testflight-release-results.md
```

Logs should include state transitions, status categories, item IDs, schema/key versions, and source revisions—but never secret values, raw private-key data, full encrypted payloads, biometric details, or unredacted AI context.

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
- [Apple CryptoKit](https://developer.apple.com/documentation/cryptokit)
- [AES.GCM](https://developer.apple.com/documentation/cryptokit/aes/gcm)
- [ChaChaPoly](https://developer.apple.com/documentation/cryptokit/chachapoly)
- [HKDF](https://developer.apple.com/documentation/cryptokit/hkdf)
- [SecureEnclave.P256](https://developer.apple.com/documentation/cryptokit/secureenclave/p256)
- [Protecting keys with the Secure Enclave](https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
