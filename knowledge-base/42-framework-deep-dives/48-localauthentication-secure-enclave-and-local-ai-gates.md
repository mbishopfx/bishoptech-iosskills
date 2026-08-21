# LocalAuthentication, Secure Enclave, and local-AI access gates

LocalAuthentication lets an app ask the operating system to authenticate the device owner with biometry, a device passcode, a companion device, or another documented policy. The app receives an authentication outcome; it does not receive fingerprint images, Face ID data, Optic ID data, or the user’s passcode.

Use it as a local access gate:

feature intent -> policy availability -> system-managed authentication -> protected operation/keychain item/right -> explicit app state -> lock/retry/invalidate

Do not confuse:

- device-owner authentication with an app account login;
- a successful policy evaluation with a server identity proof;
- a keychain access-control prompt with an app-owned permission prompt;
- a Secure Enclave private key with a general-purpose encryption key;
- an authenticated user with a trustworthy AI result.

## 1. LAContext is the classic policy route

Create an LAContext for a bounded authentication attempt. Configure the reason and, when appropriate, cancel/fallback labels. Use canEvaluatePolicy(_:error:) before evaluatePolicy(_:localizedReason:reply:), then handle the Boolean result and LAError/other error.

Common policies include:

- deviceOwnerAuthenticationWithBiometrics: biometry only;
- deviceOwnerAuthentication: biometry when available, with device-passcode fallback;
- companion policies where the selected SDK and device family support them;
- deviceOwnerAuthenticationWithWristDetection for a watchOS-specific route.

Select the policy based on the user-facing operation. A high-sensitivity local vault may require current biometry; a convenience unlock may intentionally permit the device passcode. Do not show a biometric-only label when the chosen policy can fall back to a passcode.

The default system prompt is the source of truth. localizedReason should say what the person is unlocking, not merely “authenticate.” Use NSFaceIDUsageDescription when the target supports Face ID and the app allows biometric authentication. Never ask for biometric data as if the app could inspect or store it.

## 2. Availability and failure are state, not copy

canEvaluatePolicy can fail because the device has no supported mechanism, no passcode, no enrolled biometry, a policy is unavailable, or the environment cannot interact. The result may also fail because the user canceled, failed, fell back, the system canceled, the context was invalidated, or the biometry is locked out.

Model at least:

| State | Meaning | App response |
| --- | --- | --- |
| Not checked | No policy evaluation attempted | Choose policy and explain the protected action |
| Available | The selected policy can be evaluated | Present system authentication |
| Unavailable | The policy cannot run in this environment | Offer the documented fallback or keep the feature locked |
| Authorizing | System prompt is active | Disable duplicate triggers and preserve cancellation |
| Authorized | The operation may proceed | Perform only the bounded protected action |
| Canceled/failed/locked out | Authentication did not establish access | Keep data locked; explain recovery without blame |
| Context invalidated | The context cannot be reused | Create a fresh context |

LABiometryType describes supported hardware, not necessarily currently usable authentication. Check policy availability before treating Face ID, Touch ID, or Optic ID as available.

## 3. Authentication is not identity proof

LocalAuthentication proves that the device’s local policy succeeded. It does not establish:

- the user’s account identity to a server;
- that the same person owns an email address;
- that a remote request came from this device;
- that a model output is correct;
- that a clinical or financial operation is legally authorized.

If the app has a server account, run account authentication separately and bind server sessions to their own credential lifecycle. Use a local authentication result to gate a local action or re-unlock a protected app credential, not to mint a server account identity by itself.

## 4. Access-control items and Secure Enclave keys are different routes

Keychain items can be protected with SecAccessControl flags such as devicePasscode, biometryAny, or biometryCurrentSet. Choose the accessibility class and access-control flags from the threat model:

- biometryAny can survive a change in enrolled biometry;
- biometryCurrentSet invalidates access when the enrolled set changes;
- WhenPasscodeSetThisDeviceOnly depends on a passcode and does not migrate through backup;
- WhenUnlockedThisDeviceOnly keeps the item tied to the creating device and unlocked state.

The Secure Enclave is a hardware key manager. Apple documents that its supported private keys are 256-bit NIST P-256 elliptic-curve keys, generated directly on the Secure Enclave. Pre-existing keys cannot be imported. Secure Enclave keys are appropriate for signing and elliptic-curve key exchange; they are not a drop-in place to store arbitrary plaintext or an arbitrary symmetric model key.

For a local AI vault, a deliberate composition is:

1. generate or obtain a data-encryption key through an app-owned CryptoKit design;
2. protect the wrapping credential or a signing/key-exchange private key with Keychain/Secure Enclave access controls;
3. ask LocalAuthentication at the boundary where the key is used;
4. decrypt only the minimal local context needed for the operation;
5. clear derived in-memory state and re-lock on background/timeout policy.

Do not copy raw clinical, financial, or personal prompts into analytics because the vault unlocked successfully.

## 5. Current SwiftUI and persisted-right surfaces

Current LocalAuthentication documentation includes a SwiftUI LocalAuthenticationView that visually represents an LAPolicy evaluation and reports a Result. It is a system-aware control, not a custom biometric scanner. Use it when the selected deployment target and SDK provide it; otherwise use LAContext with a native SwiftUI state wrapper.

Current documentation also includes LARight, LARightStore, LAPersistedRight, and LASecret. A right groups requirements for a protected operation. LARightStore can persist a secret behind authorization requirements and Secure Enclave-backed protection. These APIs are availability-sensitive; verify the exact iOS 26 SDK, target, and runtime before adopting them.

Do not mix multiple authorization authorities casually. If a feature uses LocalAuthenticationView, LAContext, a Keychain access-control prompt, and an LARight, write down which one is authoritative for each protected resource. A successful UI state should not unlock a different resource unless the implementation actually binds them.

## 6. Context lifetime and reuse

An LAContext is an authentication transaction object. Create it close to the operation, prevent duplicate evaluation, invalidate it when the flow is canceled or the app no longer needs it, and do not retain an old success as permanent authorization. The documented context includes domain-state and credential-reuse surfaces; use them only with a deliberate security policy.

When a view leaves the foreground:

- preserve only the minimum state needed to render recovery;
- stop or invalidate an in-flight context if the operation must not continue;
- do not treat a backgrounded prompt as completed;
- re-check the protected resource before use;
- re-lock after a timeout or user sign-out.

## 7. SwiftUI design and Liquid Glass

The protected surface should say what is behind the gate:

- “Unlock local journal analysis”;
- “Reveal saved payment details”;
- “Open private HealthKit review”;
- “Use the signing key for this device.”

Use Liquid Glass around the explanation, primary action, timeout state, and recovery controls. Keep the actual system authentication control recognizable and reachable. Do not build a fake Face ID scanner, animated eye, fingerprint drawing, or glass card that implies the app can inspect biometric data.

Respect Dynamic Type, VoiceOver, high contrast, Reduce Motion, Voice Control, Switch Control, keyboard focus, and cancel/retry semantics. Ensure the locked and unlocked states have clear text, not only a material/color change.

## 8. Local-AI gate pattern

A safe local-AI pattern is:

locked state -> explain local purpose -> authenticate -> load minimal protected context -> run model locally -> show editable/reviewable result -> purge/lock

Examples:

- unlock a local meeting transcript before summarization;
- unlock a private health-data feature before reading its local derived features;
- unlock a private prompt library before the model sees it;
- authenticate before a signing operation approves an AI-proposed action.

The model must not receive “authenticated” as evidence that a person agreed with the output. Keep consent, review, model availability, confidence, and side-effect confirmation separate. If a model is unavailable or context decryption fails, show a deterministic locked/offline fallback.

## 9. Physical-device and release boundaries

Simulator policy prompts can exercise app state and some UI, but they do not prove Face ID, Touch ID, Optic ID, Apple Watch/companion behavior, Secure Enclave key lifecycle, biometric enrollment changes, passcode lockout, or production accessibility. Prove those on the intended physical device family.

A release evidence bundle should include:

- target Info.plist and NSFaceIDUsageDescription when applicable;
- selected policy and fallback rationale;
- physical-device availability matrix;
- success, cancel, failure, lockout, and context-invalidation evidence;
- keychain access-control and Secure Enclave key-generation evidence;
- background/timeout/re-lock behavior;
- local AI redaction and purge evidence;
- accessibility/localization review;
- signed archive and distribution configuration.

An authentication prompt, a Boolean success, a key reference, a preview, or a generated summary is not proof of account identity, secure storage, biometric hardware coverage, or release readiness.

## Sources

- [Local Authentication](https://developer.apple.com/documentation/localauthentication)
- [LAContext](https://developer.apple.com/documentation/localauthentication/lacontext)
- [LAPolicy](https://developer.apple.com/documentation/localauthentication/lapolicy)
- [LAPolicy.deviceOwnerAuthentication](https://developer.apple.com/documentation/localauthentication/lapolicy/deviceownerauthentication)
- [LABiometryType](https://developer.apple.com/documentation/localauthentication/labiometrytype)
- [LocalAuthenticationView](https://developer.apple.com/documentation/localauthentication/localauthenticationview)
- [LARight](https://developer.apple.com/documentation/localauthentication/laright)
- [LARightStore](https://developer.apple.com/documentation/localauthentication/larightstore)
- [LARight.State](https://developer.apple.com/documentation/localauthentication/laright/state-swift.enum)
- [Local Authentication Embedded UI](https://developer.apple.com/documentation/localauthenticationembeddedui)
- [Keychain Services](https://developer.apple.com/documentation/security/keychain-services)
- [Protecting keys with the Secure Enclave](https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave)
- [kSecAttrTokenIDSecureEnclave](https://developer.apple.com/documentation/security/ksecattrtokenidsecureenclave)
- [SecAccessControlCreateFlags](https://developer.apple.com/documentation/security/secaccesscontrolcreateflags)
- [Key Generation Attributes](https://developer.apple.com/documentation/security/key-generation-attributes)
- [NSFaceIDUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsfaceidusagedescription)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
