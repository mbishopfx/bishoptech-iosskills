# LocalAuthentication and private-data route

Use this route when a feature needs a device-local access gate for sensitive data, a protected keychain item, a Secure Enclave key operation, or a private on-device AI context. Choose one authority for each resource and keep server identity separate.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | Unlock one local action or protected resource |
| Prompt | Specific localized reason naming the action |
| Policy | Biometry-only, device-owner authentication with passcode fallback, companion, or watchOS policy as required |
| Availability | LAContext.canEvaluatePolicy plus physical device/OS/lockout conditions |
| Result | Boolean/error outcome, never raw biometric data |
| Immediate gate | Fresh LAContext, duplicate-trigger prevention, bounded action, invalidate/re-lock |
| Persistent secret | Keychain item with SecAccessControl or current LARight/LARightStore route |
| Device key | Secure Enclave-generated P-256 key for supported signing/key-exchange use |
| AI | Load minimum local context after authorization; keep output reviewable and purge/re-lock |
| UI | SwiftUI state machine; LocalAuthenticationView where the target exposes it; accessible fallback |
| Glass | Group reason, status, retry, and settings/support; do not imitate biometrics |
| Proof | Signed usage strings, policy fixtures, physical biometry/passcode/lockout, protected-resource operation, purge, accessibility, and release evidence |

## 1. Name the protected action

Write the exact action before selecting a policy:

- reveal local private data;
- authorize a key operation;
- unlock a private AI context;
- approve a local destructive action;
- retrieve an app credential.

If the operation is server account access, add the account credential route. LocalAuthentication can gate the local credential; it does not replace server authentication.

## 2. Choose the policy

| Need | Policy direction | Tradeoff |
| --- | --- | --- |
| Strict current biometry | deviceOwnerAuthenticationWithBiometrics | No passcode fallback; can fail when biometry is unavailable/locked |
| Convenient device-owner proof | deviceOwnerAuthentication | Allows biometry and the device passcode on iOS |
| Companion-assisted access | Current companion policy in the selected SDK | Requires actual paired-device/environment proof |
| watchOS wrist route | watchOS wrist-detection policy where supported | Target-specific and physical-Watch proof |

Do not copy an old deprecated policy into a new target without checking current availability. Keep the policy label and fallback copy aligned with behavior.

## 3. Configure the target

For Face ID-capable targets, add an accurate NSFaceIDUsageDescription. Confirm deployment target and framework imports. Build and inspect the final Info.plist; a source file or preview does not prove the usage key exists in the signed product.

If using Keychain access controls:

- select the accessibility class deliberately;
- choose biometryAny versus biometryCurrentSet intentionally;
- decide whether the item may migrate or must remain device-only;
- document passcode and lockout behavior;
- do not put secrets in logs, previews, screenshots, or analytics.

If using Secure Enclave:

- generate the private key on the device;
- use only supported P-256 key operations;
- do not attempt to import a pre-existing private key;
- store the reference and public key as app-owned metadata;
- test key invalidation/recovery.

## 4. Implement the transaction

The runtime sequence is:

availability check -> fresh context -> system prompt -> result/error mapping -> protected read/sign/decrypt -> bounded feature -> timeout/background -> re-lock

Do not keep the unlocked state forever. A LocalAuthentication success can be scoped to one operation, a short session, or a documented reuse interval. Invalidate the context and clear ephemeral state when the policy requires.

## 5. Add the SwiftUI path

Use LocalAuthenticationView when the selected SDK/OS exposes it and the desired interaction fits its system-aware contract. Otherwise, keep LAContext in an observable coordinator and expose only an app-owned enum to SwiftUI:

- locked;
- checking;
- prompting;
- unlocked;
- canceled;
- failed;
- unavailable;
- expired.

The view should not inspect or store biometric state. Use semantic labels and keep fallback/recovery visible.

## 6. Add a protected local-AI operation

Use:

locked -> authenticate -> retrieve minimal local secret/context -> prepare bounded input -> run on-device model -> show draft -> user review -> optional side effect -> purge

The model may summarize private notes or user-selected HealthKit-derived features, but authentication does not make a result true. Keep a clear “needs review” and “model unavailable” state. Export, sync, and network calls need their own privacy/consent route.

## 7. Failure and recovery cases

Handle:

- no passcode;
- no biometric enrollment;
- unsupported policy;
- prompt canceled;
- failed attempt;
- biometry lockout;
- system cancellation;
- context invalidation;
- background/foreground transition;
- enrolled-biometry change;
- keychain item missing;
- Secure Enclave key unavailable;
- model unavailable;
- protected context corrupted;
- timeout/re-lock;
- account sign-out;
- inaccessible action with VoiceOver/keyboard.

Never delete the only secret silently after an authentication or enrollment failure. Provide a recovery policy or keep the feature unavailable.

## 8. Proof bundle

- Info.plist and target configuration;
- selected policy and reason copy;
- availability/error mapping fixtures;
- simulator UI and pure state tests;
- physical Face ID/Touch ID/Optic ID/passcode/companion tests;
- Keychain access-control prompt and item lifecycle;
- Secure Enclave key generation/use/invalidation;
- LARight/LARightStore evidence if used;
- local AI input redaction, output review, and purge;
- accessibility, localization, Reduce Motion, and fallback;
- signed archive and release configuration.

An authentication prompt, success Boolean, key reference, or preview is not proof of a server identity, secure data lifecycle, physical-device coverage, or release readiness.

## Sources

- [Local Authentication](https://developer.apple.com/documentation/localauthentication)
- [LAContext](https://developer.apple.com/documentation/localauthentication/lacontext)
- [LAPolicy](https://developer.apple.com/documentation/localauthentication/lapolicy)
- [LAPolicy.deviceOwnerAuthentication](https://developer.apple.com/documentation/localauthentication/lapolicy/deviceownerauthentication)
- [LocalAuthenticationView](https://developer.apple.com/documentation/localauthentication/localauthenticationview)
- [LARight](https://developer.apple.com/documentation/localauthentication/laright)
- [LARightStore](https://developer.apple.com/documentation/localauthentication/larightstore)
- [Keychain Services](https://developer.apple.com/documentation/security/keychain-services)
- [Protecting keys with the Secure Enclave](https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave)
- [kSecAttrTokenIDSecureEnclave](https://developer.apple.com/documentation/security/ksecattrtokenidsecureenclave)
- [SecAccessControlCreateFlags](https://developer.apple.com/documentation/security/secaccesscontrolcreateflags)
- [NSFaceIDUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsfaceidusagedescription)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
