# Local Authentication and private-AI unlock design

Authentication screens should make a sensitive action feel deliberate without pretending the app owns biometric data. The system evaluates a device policy; the app receives an outcome; the protected resource has its own storage and lifecycle.

Use this state chain:

locked -> explain purpose -> check policy -> system authentication -> authorized action -> review result -> timeout/re-lock

## 1. Put the protected outcome in the copy

A generic “Use Face ID” button makes the person guess what will happen. Name the action:

- “Unlock private notes”;
- “Reveal the local HealthKit review”;
- “Approve this device signature”;
- “Open saved account credentials.”

The reason should match the actual operation. If the selected LAPolicy permits passcode fallback, say “Use Face ID or your device passcode” rather than promising biometry-only behavior.

Do not imply that the app sees a face, fingerprint, eye pattern, or passcode. The system owns that interaction.

## 2. Use one authority per resource

Define which gate protects which resource:

| Resource | Preferred authority | Visible state |
| --- | --- | --- |
| One immediate app action | LAContext policy evaluation | Authorized for this action, then return to locked |
| Keychain item | Keychain access control with optional LAContext | Item unavailable/available; handle enrollment and lockout |
| Device-bound signing key | Secure Enclave key and access control | Key operation succeeded/failed; never expose private key |
| Persisted secret/right | LARight/LARightStore where supported | Right state and secret availability |
| Server account | App/server credential lifecycle | Signed-in/account state, separate from local auth |

Avoid a glass lock badge that claims “verified” while a separate vault, keychain item, and account remain unauthenticated.

## 3. The locked surface is still a useful screen

While locked, show:

- the feature name;
- why the app is asking;
- what stays on device;
- a primary system-authentication action;
- cancel/back;
- a documented fallback such as passcode, manual entry, or a non-private view;
- a recovery route for no passcode, no enrollment, lockout, or unavailable hardware.

Do not render private previews underneath a blur if a user could reveal them through accessibility, screenshots, a transition frame, an accessibility tree, or a widget. Redact notifications and logs at the same boundary.

## 4. Liquid Glass around a system-owned action

Liquid Glass is useful for grouping the reason, state, retry, and settings/support actions. Keep the authentication action visually stable and recognizable. Do not use:

- a fake biometric scanning animation;
- a glass overlay that intercepts the system prompt;
- a permanently glowing “unlocked” material;
- an ambiguous toggle that silently changes the policy;
- a gesture-only unlock;
- a screenshot of the lock screen as a design substitute for the actual system policy.

When the system control is unavailable, preserve a clear text fallback. Material should not be the only contrast or state cue.

## 5. Design the state machine, not only the success path

The important states are:

- available;
- no passcode;
- no enrolled biometry;
- hardware supported but temporarily unavailable;
- prompt active;
- user canceled;
- authentication failed;
- fallback selected;
- biometry locked out;
- system canceled;
- context invalidated;
- app backgrounded;
- protected resource missing;
- local model unavailable;
- timeout/re-lock.

The user should never be trapped in a retry loop. After cancellation, let them return to the locked state. After lockout, explain the system-controlled recovery without exposing a security-sensitive reason the framework does not provide.

## 6. Local-AI privacy boundary

For private AI:

1. show what local material will be loaded;
2. authenticate;
3. load only the selected context;
4. display a “processing locally” or equivalent state only when true;
5. keep the generated result editable and reviewable;
6. purge ephemeral context on timeout/background/sign-out policy;
7. ask separately before exporting or causing an external side effect.

Authentication should not be inserted into the model prompt as proof that a user approved a conclusion. The user can authenticate to view a result and still disagree with it. Keep authentication, model output, user review, and side-effect confirmation separate.

## 7. Secure storage must be explainable

Use simple copy:

- “Stored in this app’s protected local storage.”
- “This device-bound key cannot be exported.”
- “Changing enrolled biometrics may require setting up access again.”
- “The model runs only after the selected local context is unlocked.”

Do not claim “military-grade,” “unhackable,” “Apple cannot access this,” or “biometrics are stored in your app.” Explain the actual access-control and retention behavior instead.

When biometryCurrentSet is used, a change in enrolled biometry may invalidate the item. Make the recovery action explicit and ensure the app does not silently delete the user’s only copy of a secret without a separately designed recovery policy.

## 8. Accessibility and inclusive authentication

Test:

- VoiceOver labels for the protected action and current state;
- Dynamic Type on the reason and fallback;
- Voice Control phrases;
- Switch Control focus and activation;
- keyboard focus on iPad/Mac Catalyst where supported;
- Reduce Motion and reduced transparency;
- high contrast and color-blind interpretation;
- localized reason strings that remain specific;
- system prompt return focus.

Never make biometry the only way to use the feature unless the security contract truly requires it and the product has a responsible alternative for unsupported/locked-out users.

## 9. Test with evidence tiers

Use deterministic unit/UI fixtures for the state machine, then physical-device runs for the system:

- simulator: locked/unlocked layout, copy, fallback, redaction, and pure state logic;
- physical device: Face ID/Touch ID/Optic ID, passcode fallback, cancel, failed attempt, lockout, enrollment change, app background, and re-lock;
- signed target: NSFaceIDUsageDescription, deployment, entitlements, keychain access, Secure Enclave generation;
- local AI fixture: no secret, secret loaded, model unavailable, low-confidence output, user correction, purge;
- release artifact: archive, signing, device family, and privacy review.

A screenshot proves appearance. It does not prove the system prompt, hardware, secret protection, or model data boundary.

## Sources

- [Local Authentication](https://developer.apple.com/documentation/localauthentication)
- [LAContext](https://developer.apple.com/documentation/localauthentication/lacontext)
- [LAPolicy](https://developer.apple.com/documentation/localauthentication/lapolicy)
- [LocalAuthenticationView](https://developer.apple.com/documentation/localauthentication/localauthenticationview)
- [LARightStore](https://developer.apple.com/documentation/localauthentication/larightstore)
- [Protecting keys with the Secure Enclave](https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave)
- [SecAccessControlCreateFlags](https://developer.apple.com/documentation/security/secaccesscontrolcreateflags)
- [NSFaceIDUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsfaceidusagedescription)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
