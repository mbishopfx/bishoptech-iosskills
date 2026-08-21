# Account authentication and passkey-review design

Authentication should feel like a clear handoff to a trusted system surface, not a custom form wrapped in visual effects. The person should understand why identity is needed, what account or relying party is involved, and what happens after the system confirms the credential.

Use this sequence:

~~~text
value before sign-in
-> reason for identity
-> system credential choice
-> server verification
-> account/session result
-> local data and recovery controls
~~~

## Delay the account wall

Apple’s Human Interface Guidelines recommend asking for an account only when the product has a reason to need one and delaying sign-in long enough for the person to understand the app’s value. This matters especially for private/local-first utilities:

| Product state | Better behavior |
| --- | --- |
| Browsing or trying the core feature | Let the person continue without an account |
| Sync/collaboration/export requires identity | Explain the specific benefit at the moment it becomes relevant |
| A paid or protected action needs an account | Say what is being protected and why |
| A destructive or security-sensitive action needs reauthentication | Explain the action and let the system present verification |
| Account deletion | Provide an obvious in-app route and explain retained data if any |

Do not add a generic “Create account” button to a first-run screen just because the backend has users. Make the reason concrete: “Sign in to sync this notebook across your devices.”

## Choose the native credential surface

| User intent | Native UI | App-owned UI |
| --- | --- | --- |
| Sign in with Apple | SignInWithAppleButton or ASAuthorizationAppleIDButton | Brief benefit copy, account state, error recovery |
| Use a passkey | Authentication Services authorization sheet | Server challenge state and post-auth result |
| Use a security key | Authentication Services security-key sheet | Key name, backup/recovery guidance, account state |
| Use a password/AutoFill credential | System AutoFill or authorization request | Account-linking and migration explanation |
| Use an OAuth provider | ASWebAuthenticationSession/WebAuthenticationSession | Provider explanation and safe callback handling |
| Unlock local encrypted data | Passkey assertion plus local policy | What will be unlocked, which records, and recovery |

Do not draw a custom button that imitates an Apple credential control or a custom biometric sheet. The custom shell may explain a system operation; the system owns the credential selection and user-verification surface.

## Authentication screen anatomy

Use a quiet, readable composition:

1. Small product identity or document context.
2. Short reason the account is needed.
3. One primary native credential control.
4. Secondary passkey or recovery option when supported.
5. Privacy and account-deletion link.
6. A manual/support route that does not pretend to be authentication.

For example:

~~~text
Your notebooks stay on this device.
Sign in only if you want encrypted cross-device sync.
[ Sign in with Apple ]
[ Use a passkey ]
Not now
Privacy · Delete account
~~~

The copy must match the actual implementation. Do not promise encryption, sync, deletion, or recovery that the target and server do not provide.

## Passkey registration review

Before a person creates a passkey, show:

- the service or account name;
- the benefit of adding a passkey;
- whether it can sync through iCloud Keychain;
- how another device or recovery key can be used;
- what happens if the person cancels;
- how to remove or replace the passkey later.

The system sheet handles the credential creation and user verification. The app should show “Passkey added” only after the relying-party server accepts the registration credential and stores the public key.

If the registration request is a conditional upgrade from an existing password account, preserve the account identity and show that a passkey is being added to the same account. Do not create a duplicate account from a credential upgrade.

## Passkey sign-in review

Passkey sign-in should distinguish these states:

| State | Copy | Action |
| --- | --- | --- |
| Challenge loading | “Preparing secure sign-in…” | Cancel |
| System sheet | “Choose a passkey for [service].” | System-owned |
| Assertion received | “Checking your sign-in…” | None |
| Server accepted | “You’re signed in.” | Continue |
| No credential | “No passkey for this service was found on this device.” | Register or use recovery |
| Domain/configuration error | “This service isn’t configured for passkeys on this build.” | Contact support/fix deployment |
| User canceled | “Sign-in canceled.” | Try again or choose another route |
| Server rejected | “We couldn’t verify this sign-in.” | Retry or recovery |

Avoid wording such as “Face ID failed” when the system may have used a passcode, Touch ID, or a different authenticator. Say “The secure sign-in was canceled or could not be completed” unless the system provides a precise, user-safe reason.

## Sign in with Apple design

Use the official SignInWithAppleButton with the current platform style. Pair it with one sentence that explains the value. Request only the scopes the feature needs and make the choice to share information visible in Apple’s system UI.

Good copy:

- “Sign in to sync your saved designs.”
- “Use your Apple Account to create an account without another password.”
- “We’ll use this to keep your private workspace available on your devices.”

Avoid:

- “Continue with Apple” when the action actually creates an account and the label is ambiguous;
- a custom Apple logo button with a mismatched style;
- promising that Apple shares a full name or email on every sign-in;
- treating a relay email as the permanent human identity;
- hiding the account-deletion path.

If the person hides their email, show a privacy-preserving explanation instead of exposing the relay address as a confusing account name. Store the stable user identifier on the server and keep contact data separate.

## Security-key design

A physical security key needs a stronger recovery story than a normal passwordless button:

- name the service and the required key type;
- tell the person to insert, connect, or hold the key near the device;
- encourage registering a second backup key when the account permits it;
- explain that losing all registered keys can block sign-in;
- show which key was added or removed;
- require confirmation before removing the last key.

Do not imply that NFC proximity alone establishes identity. The security-key protocol and server assertion verification do that.

## Local unlock and PRF-derived encryption

For a private local-first app, a passkey assertion can be an unlock event for a local encryption key. The interface should show what is about to unlock:

~~~text
Passkey verified
-> Unlock private notebook
-> Load only this workspace
-> Discard temporary key when finished
~~~

The PRF-derived SymmetricKey is sensitive even though it is derived from a passkey. Never show it, log it, send it to a model, or store it as a normal app setting. If the app cannot recover after all passkeys are lost, say so before the person enables the encryption mode and offer the product’s approved recovery method.

Do not use “encrypted” as a general badge for an app that only protects one local projection. State the actual scope: “This notebook is encrypted when locked.”

## Browser authentication design

ASWebAuthenticationSession is a modal web handoff, not an embedded app-owned login form. The system names the domain being used. The app should:

- show why the browser flow is needed;
- keep the callback state pending until validated;
- handle cancel and provider errors;
- avoid displaying or logging access tokens;
- use an ephemeral browser session when the product needs cookie isolation and the browser honors it;
- return to a clear account state after the callback.

The callback URL is an input boundary. Parse only the expected scheme, host/path, state, error, and authorization values. Let the server exchange or verify tokens where required.

## Liquid Glass guidance

Authentication is a functional layer, so Liquid Glass can help group the primary action and its current state. Use it sparingly:

- one primary identity action group;
- one account-state surface;
- one recovery/action group.

Do not stack glass cards around every provider or make the login screen look like a glossy credential vault. Standard forms, buttons, sheets, and system controls already adapt to the platform’s current Liquid Glass appearance.

System-owned passkey, Sign in with Apple, security-key, and web-authentication surfaces stay system-owned. Place app-owned copy outside them and return to a standard navigation or sheet surface after completion.

Test:

- dark and light appearances;
- increased contrast;
- reduced transparency;
- reduced motion;
- large Dynamic Type;
- VoiceOver labels and reading order;
- keyboard/pointer focus;
- landscape and split-view layouts.

## AI review and account state

AI can help summarize a non-secret account state or draft user-facing recovery copy. It must never become the authenticator:

| AI input | Safe use |
| --- | --- |
| “No passkey found” | Explain registration/recovery choices |
| Verified server session state | Summarize what features are now available |
| User-edited account name | Suggest a display label |
| Credential state revoked | Explain that sign-in is required again |
| PRF-derived key or identity token | Do not provide to the model |
| APDU/WebAuthn challenge/signature | Do not interpret as a model decision |

Keep system authorization, server verification, local unlock, model context, and domain side effects as separate state. A model should not decide which account to merge or whether a new device is trusted.

## Recovery and deletion surfaces

The account area should include:

- current sign-in method;
- passkeys/security keys registered;
- last successful authentication time if the product stores it;
- sign out;
- revoke/remove credential;
- recovery guidance;
- delete account.

If the person deletes their account, explain which local data is deleted, which server data is removed, and what happens to Sign in with Apple tokens, relay email, passkey-bound blobs, or encrypted local records. Do not leave a private local workspace inaccessible without warning.

## Accessibility and localization

Use the official Sign in with Apple control and allow the system to provide credential labels. For app-owned content:

- label each provider clearly;
- do not rely on the Apple logo alone;
- announce transitions from system UI back to the app;
- keep manual and recovery routes reachable without a credential sheet;
- expose account state as text, not just color or an icon;
- localize service names, pluralization, and security warnings;
- avoid exposing email relay addresses as a label when a stable account name exists.

Run the complete task with VoiceOver, Switch Control, Voice Control, large text, and keyboard navigation. A visually polished sign-in screen is not evidence of an accessible authentication task.

## Preview and device proof

Previews should cover ready, challenge loading, provider selection, no credential, server rejected, revoked, signed in, locked, recovery, and deletion states. Use fake credentials and clearly labeled fixtures.

Physical and integration proof requires:

- a signed target with the exact entitlements;
- a real associated domain and AASA file;
- an actual server challenge and verifier;
- an Apple Account for Sign in with Apple;
- iCloud Keychain/passkey state;
- a physical security-key fixture when supported;
- callback and cancellation paths;
- account reset/revocation and deletion.

Do not claim passkey sync, Apple Account state, key hardware, server verification, or App Store configuration from a preview.

## Sources

- [Managing accounts](https://developer.apple.com/design/human-interface-guidelines/managing-accounts)
- [Sign in with Apple](https://developer.apple.com/design/human-interface-guidelines/sign-in-with-apple)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Authentication Services](https://developer.apple.com/documentation/authenticationservices)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [Connecting to a service with passkeys](https://developer.apple.com/documentation/authenticationservices/connecting-to-a-service-with-passkeys)
- [Supporting Security Key Authentication Using Physical Keys](https://developer.apple.com/documentation/authenticationservices/supporting-security-key-authentication-using-physical-keys)
- [Implementing User Authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [Displaying Sign in with Apple buttons in your app](https://developer.apple.com/documentation/signinwithapple/displaying-sign-in-with-apple-buttons-in-your-app)
- [SignInWithAppleButton](https://developer.apple.com/documentation/authenticationservices/signinwithapplebutton)
- [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession)
- [WebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/webauthenticationsession)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
