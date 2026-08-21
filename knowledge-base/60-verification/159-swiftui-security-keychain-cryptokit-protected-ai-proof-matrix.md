# SwiftUI Security, Keychain, CryptoKit, and protected local-AI proof matrix

Security evidence must connect the signed target, physical device state, Keychain policy, cryptographic protocol, UI state, optional local AI, and release artifact. A preview, successful `SecItemAdd`, biometric callback, ciphertext, or model response proves only one small part of that chain.

## Claim matrix

| Claim | Minimum evidence | Common false proof |
| --- | --- | --- |
| The intended target can use Keychain | Built entitlements, bundle/team mapping, exact access group, and real add/read/update/delete result | A matching string in source code |
| Item policy matches the threat model | Item class, `kSecAttrAccessible`, sync flag, access-control flags, migration/deletion decision | “Keychain is secure” without the item attributes |
| A user-presence gate is real | Physical device prompt, allow/cancel/deny/lockout fixtures, and a protected item read | `LAContext` returns `true` for an unrelated operation |
| Device-only behavior is real | Restore/migration/new-device test showing the expected missing or non-migrated state | A `ThisDeviceOnly` constant in code |
| Synchronization is intentional | Two signed devices/account states, delayed sync/conflict/revoke evidence, and privacy review | A local item exists on one device |
| Extension sharing is correct | Separate archive/install of each target, signed access-group entitlement, narrow read/write evidence | An App Group folder is visible to both targets |
| Keychain CRUD is durable | Relaunch, lock/restart, duplicate add, update, delete, missing, and status mapping | An in-memory test double |
| The crypto envelope is authenticated | Known-answer round trip plus wrong key, altered ciphertext, nonce, tag, AAD, version, and truncation fixtures | Decrypting a sample string once |
| Nonces and key versions are safe | Repeated-seal uniqueness policy, persisted envelope metadata, rotation/migration tests, and retry/crash behavior | A random nonce generated in a demo without a protocol |
| Key type conversion is correct | Same-type CryptoKit/Keychain reconstruction, representation metadata, and mismatch rejection | Casting arbitrary bytes into a different key type |
| Secure Enclave is used | Supported physical hardware, generated P-256 key, signing/ECDH operation, opaque persistence, and no plaintext export/log | `SecureEnclave` appears in an import statement |
| Key invalidation/recovery is honest | Passcode/biometry/policy-change/key-loss fixtures and product-specific recovery/reset result | Silently generating a new key and showing old data as recovered |
| Local AI is on device when promised | Target/model availability record, provider route, network policy, and redacted prompt/response evidence | A model label in the UI |
| AI cannot bypass security | Model unavailable/wrong schema/stale source/refusal fixtures and deterministic commit gate | Model output looks plausible |
| Raw secrets are not leaked | Redacted logs, crash/analytics review, memory/cache lifetime review, and extension/widget projection audit | No obvious secret in the happy-path screenshot |
| SwiftUI state is truthful | Locked/unlocked/denied/missing/corrupt/proposal/saved reducer fixtures | One `isUnlocked` Boolean |
| Liquid Glass is accessible | Reduce Transparency, Increase Contrast, Dynamic Type, VoiceOver, keyboard, pointer, and reduced-motion tasks | A glass preview on one iPhone size |
| Deletion is complete for the declared scope | Keychain deletion, encrypted-store deletion, cache cleanup, sync/server deletion, and relaunch proof | A row disappears from the list |
| Release configuration is correct | Archive inspection, signed entitlements/Info.plist, TestFlight installation, physical retest, and rollback/recovery record | Debug run or simulator success |

## Target and entitlement fixtures

Create a fixture for each target and configuration:

```text
target
  bundle identifier
  team identifier
  deployment target / SDK
  keychain access groups
  app groups
  App Attest / associated capabilities if present
  privacy usage descriptions
  Debug / Release / TestFlight differences
```

Check the built artifact, not only the Xcode project. A target can compile while the signed entitlement is missing, has the wrong team prefix, or is not present in the extension that attempts the read. Record the exact `OSStatus` and map it to an app-owned diagnostic without logging sensitive query values.

## Keychain policy matrix

| Fixture | Expected observation |
| --- | --- |
| Fresh install, no item | `missing`; app offers create/recovery, not unlock failure |
| Add same descriptor twice | Explicit idempotent update or conflict; no accidental duplicate secret |
| Device locked | Item follows selected accessibility/access-control policy |
| Restart before first unlock | `AfterFirstUnlock` and foreground-only policies behave differently as documented |
| Passcode absent | Passcode-bound item cannot be created/read; UI explains requirement |
| Passcode disabled | Device-only passcode-bound items follow the documented deletion/unavailability behavior |
| Biometry allowed | Protected read succeeds and scope is visible |
| Biometry cancelled/denied/locked out | Data remains locked; no stale success is retained |
| Biometric enrollment changes | `biometryCurrentSet` item follows invalidation policy; recovery is explicit |
| Background or extension access | Only the target and accessibility class that were designed for it can read |
| Wrong access group | Signed target receives missing-entitlement/no-match behavior; source string alone is not trusted |
| Device migration/restore | `ThisDeviceOnly` and migratable items show their intentionally different results |
| iCloud Keychain delayed/conflict state | UI shows pending/unavailable/reconciled state without claiming sync completion |
| Sign out/delete | Exact item IDs are removed or revoked; unrelated items survive |

## CryptoKit fixture catalog

Use deterministic fixture data only in tests. Keep real users’ content and production key material out of fixtures.

```text
crypto-known-answer/
  aes-gcm-round-trip
  chacha-poly-round-trip
  associated-data-binding
  wrong-key-fails
  altered-ciphertext-fails
  altered-tag-fails
  altered-nonce-fails
  truncated-envelope-fails
  unsupported-version-fails
  key-rotation-migrates-once
  duplicate-retry-does-not-reuse-invalid-state
```

For each envelope record:

- algorithm and schema version;
- key identifier/version;
- nonce and tag lengths as required by the selected CryptoKit type;
- associated-data contract and source revision;
- plaintext size limits;
- decode/authentication order; and
- expected failure category.

Test that the app authenticates and validates the envelope before decoding untrusted fields or committing the result. A digest of ciphertext can identify bytes; it does not replace AEAD authentication or server/user authorization.

## Key storage and Secure Enclave fixtures

| Claim | Fixture |
| --- | --- |
| Symmetric key is protected | Generate a test key, store it under the selected Keychain policy, close/relaunch, read only after the intended gate, and delete it |
| Native NIST conversion is safe | Store/retrieve a same-type P-256 `SecKey` representation and verify a signature; reject mismatched curve/type |
| Generic CryptoKit key conversion is safe | Store/retrieve the exact generic representation for the selected type; verify an operation and then delete |
| Secure Enclave key is device-backed | Generate on supported hardware, use for P-256 sign/ECDH, persist the documented representation, and verify no plaintext private key is logged/exported |
| Hardware fallback is safe | Run on unsupported/simulator target and show an explicit alternate route; never silently downgrade a device-bound promise |
| Key invalidation is safe | Change passcode/biometric policy or remove the key where applicable; show recovery/reset behavior and protect old ciphertext |
| Private AI key boundary is safe | Decrypt only the bounded record window after authorization; clear projection/cache at lock/timeout and test crash/log surfaces |

The Secure Enclave does not turn arbitrary model weights or large encrypted data into hardware-protected storage. Test the actual key operation and the storage boundary separately.

## AI and privacy fixtures

| Fixture | Required result |
| --- | --- |
| Foundation Models unavailable | Deterministic summary or clear unavailable state; no remote fallback unless explicitly disclosed and permitted |
| Model refuses or times out | Source remains unchanged; cancellation is visible; no partial proposal commits |
| Wrong schema/range | Proposal rejected and logged only with redacted metadata |
| Stale source revision | Proposal cannot overwrite a newer record without re-review |
| Prompt contains unnecessary secret | Redaction fixture fails the build/review or strips the field before model invocation |
| Model invents account/key/permission data | Validator rejects it; security coordinator remains authoritative |
| User rejects proposal | No encrypted write or side effect occurs |
| User edits and accepts | The edited output is encrypted under the declared key/version and the commit revision is recorded |
| Widget/extension requests data | Only an intentionally redacted projection is exposed unless a separate target policy proves the raw read is necessary |
| Logging/crash review | No raw plaintext, Keychain data, private-key representation, biometric result detail, or full AI context appears |

## SwiftUI and accessibility fixtures

Run complete tasks, not isolated snapshots:

1. Open a locked workspace with VoiceOver and understand why it is locked.
2. Authenticate, confirm the protected scope, and complete one edit.
3. Cancel or deny authentication and verify that no data opened.
4. Review an AI proposal, edit it, reject it, and accept it with Dynamic Type.
5. Trigger missing, invalidated, corrupt, unavailable, and sync-pending states.
6. Lock, background, relaunch, and use the Lock action.
7. Delete the declared scope and verify the recovery/deletion explanation.

Repeat under Reduce Motion, Reduce Transparency, Increase Contrast, Switch Control, Voice Control, keyboard/pointer, RTL, and at large text sizes. Verify that glass is not the only state cue, that destructive buttons remain reachable, and that proposal status is spoken as text.

## Release evidence package

```text
evidence/
  security-route-manifest.yaml
  signed-entitlements-debug-redacted.plist
  signed-entitlements-release-redacted.plist
  built-info-plist-redacted.plist
  keychain-policy-results.md
  access-group-results.md
  crypto-fixture-results.md
  secure-enclave-device-results.md
  ai-fallback-and-privacy-results.md
  accessibility-results.md
  archive-and-testflight-results.md
  deletion-and-recovery-results.md
```

The evidence should identify target, bundle ID, OS/SDK, device model, app build, test date, fixture/result, and known limitations. Redact secret values and avoid treating a screenshot as the only proof of a cryptographic or entitlement claim.

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
- [Curve25519](https://developer.apple.com/documentation/cryptokit/curve25519)
- [SecureEnclave.P256](https://developer.apple.com/documentation/cryptokit/secureenclave/p256)
- [Protecting keys with the Secure Enclave](https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
