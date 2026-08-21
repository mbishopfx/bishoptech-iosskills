# LocalAuthentication and Secure Enclave proof matrix

Authentication proof must establish the selected policy, target configuration, actual physical-device outcome, and resource protection. A prompt or success Boolean alone does not prove that a secret, key, server account, AI context, or release path is secure.

| Claim | Evidence | Failure fixture / boundary |
| --- | --- | --- |
| The target can request Face ID | Built Info.plist contains accurate NSFaceIDUsageDescription and the named target imports LocalAuthentication | Source copy or simulator preview without built usage key |
| The selected policy is intentional | Product threat model names policy, fallback, and protected action | Button says Face ID while policy allows passcode or companion |
| Policy availability is checked | canEvaluatePolicy result and error are mapped before prompting | Prompt attempted with no passcode, no enrollment, or unsupported hardware |
| Hardware label is accurate | LABiometryType is read after availability check and copy names the actual policy | Hardware support confused with current usability |
| System authentication is used | LAContext evaluates the policy and no app-owned biometric data is collected | Fake scanner, custom biometric capture, or app-stored biometric image |
| Success is scoped | Authorized state unlocks one bounded operation or documented short session and then re-locks | Boolean success stored forever |
| Cancel/failure is safe | userCancel, authenticationFailed, systemCancel, appCancel, invalidContext, notInteractive, and lockout fixtures keep the resource locked | Error shown as success or retry loop |
| Passcode fallback is honest | deviceOwnerAuthentication fixture documents and tests the passcode path | Biometry-only copy for a fallback policy |
| Context lifecycle is correct | Fresh context, duplicate-trigger prevention, cancellation/invalidation, background/foreground, and timeout are recorded | Retained stale context or prompt completion used after background |
| Keychain access is protected | SecAccessControl flags, accessibility class, item query, and physical prompt evidence are captured | Plaintext secret, synchronizable item, or unrestricted keychain copy |
| Enrollment-change behavior is known | biometryCurrentSet fixture shows invalidation and recovery; biometryAny behavior is documented | User loses the only secret without recovery plan |
| Secure Enclave key is real | Physical device generates a new P-256 key with kSecAttrTokenIDSecureEnclave and signed/key-exchange operation succeeds | Simulator key, imported private key, unsupported algorithm, or exported secret |
| Secure Enclave limitation is respected | Key generation and operation test names P-256/signature or key-exchange use | Claim that the enclave stores arbitrary model data or symmetric plaintext |
| SwiftUI auth view is supported | Named SDK/OS compiles LocalAuthenticationView and result states are tested | New view assumed available on every deployment target |
| Persisted right is bound to resource | LARight/LARightStore identifier, authorize, secret load, remove, and failure evidence are recorded | Right success unlocks unrelated keychain/account state |
| Account identity remains separate | Server credential and local-auth tests have distinct evidence and failure paths | Local success treated as server identity proof |
| Local AI context is minimized | Only selected local context is loaded after auth; redacted logs and purge evidence exist | Raw prompts/HealthKit/clinical data sent to analytics or remote model |
| AI result is reviewable | Model-unavailable, low-confidence, user-correction, and side-effect-confirmation fixtures exist | Authentication presented as model truth or consent to side effect |
| Locked surface is accessible | VoiceOver, Dynamic Type, high contrast, Reduce Motion, Voice Control, Switch Control, keyboard focus, and localization tasks complete | Material/color-only lock state or inaccessible retry |
| Release proof exists | Signed archive, target/entitlement/Info.plist inspection, device/OS matrix, and privacy review | Preview, Debug run, prompt screenshot, or source import treated as release proof |

## Fixture set

- no passcode;
- no biometric enrollment;
- supported hardware but unavailable policy;
- biometry type available but canEvaluatePolicy false;
- success, user cancel, failed attempt, fallback, lockout, system cancel, app cancel, invalid context, and noninteractive;
- background during prompt and timeout re-lock;
- biometry enrollment change;
- Keychain item missing, access denied, and wrong accessibility class;
- Secure Enclave generation on intended device and unsupported simulator;
- LARight state unknown/authorizing/authorized/notAuthorized;
- SwiftUI view success/failure and non-available deployment fallback;
- local secret absent/corrupted;
- local model unavailable, insufficient context, low-confidence output, user edits, export confirmation;
- sign-out, delete, purge, accessibility, localization, and offline state.

## Evidence ladder

1. Pure state and error-mapping tests.
2. Built Info.plist and entitlement inspection.
3. Simulator layout, redaction, and deterministic UI fixtures.
4. Physical device policy, enrollment, passcode, lockout, keychain, and Secure Enclave tests.
5. Local-AI context/purge and side-effect review.
6. Accessibility, localization, privacy, and threat-model review.
7. Signed archive and distribution evidence.

Record the bundle ID, target, SDK/OS, device model, biometric enrollment, policy, error, protected resource identifier, key lifecycle, model version, and remaining release gaps. Do not record biometric templates or raw secrets as test evidence.

## Sources

- [Local Authentication](https://developer.apple.com/documentation/localauthentication)
- [LAContext](https://developer.apple.com/documentation/localauthentication/lacontext)
- [LAPolicy](https://developer.apple.com/documentation/localauthentication/lapolicy)
- [LABiometryType](https://developer.apple.com/documentation/localauthentication/labiometrytype)
- [LocalAuthenticationView](https://developer.apple.com/documentation/localauthentication/localauthenticationview)
- [LARight.State](https://developer.apple.com/documentation/localauthentication/laright/state-swift.enum)
- [LARightStore](https://developer.apple.com/documentation/localauthentication/larightstore)
- [Keychain Services](https://developer.apple.com/documentation/security/keychain-services)
- [Protecting keys with the Secure Enclave](https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave)
- [kSecAttrTokenIDSecureEnclave](https://developer.apple.com/documentation/security/ksecattrtokenidsecureenclave)
- [SecAccessControlCreateFlags](https://developer.apple.com/documentation/security/secaccesscontrolcreateflags)
- [NSFaceIDUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsfaceidusagedescription)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
