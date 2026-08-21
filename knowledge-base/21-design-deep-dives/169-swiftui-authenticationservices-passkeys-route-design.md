# SwiftUI passkey and Sign in with Apple design

Authentication should feel calm, native, and explicit about what the person is
doing. The app can be visually refined without imitating a system credential
sheet or turning a glass effect into a claim of trust. Let AuthenticationServices
own the credential ceremony; let SwiftUI explain the task before it and the
verified result after it.

This page pairs with the [AuthenticationServices, passkeys, and account
identity route](../42-framework-deep-dives/141-swiftui-authenticationservices-passkeys-route.md).

## Design the relationship before the button

The first screen should answer three questions:

1. What will this action let the person do?
2. Which identity or credential is being used?
3. What happens if the person cancels, loses a key, or already has an account?

Do not begin with a row of unexplained provider logos. Choose language that
matches the product relationship:

~~~text
returning account
  “Sign in to your account”
  Sign in with Apple / Use a passkey / Other supported recovery

new account
  “Create your account”
  Create with a passkey / Continue with Apple

credential linking
  “Add another way to sign in”
  current account context -> provider ceremony -> review -> commit

hardware key
  “Use your security key”
  explain NFC/USB/Lightning and recovery before the system prompt
~~~

“Verified” should be reserved for the server-confirmed account state. A local
passkey sheet being dismissed successfully is a pending result, not a verified
badge.

## The native screen sequence

Use a small state-driven composition rather than a single boolean:

~~~text
purpose
  -> capability check
  -> provider choice
  -> system credential ceremony
  -> server verification
  -> account review or session entry
  -> recovery, linking, or signed-in state
~~~

| State | Primary content | Primary action | Secondary/recovery action |
| --- | --- | --- | --- |
| `purpose` | Benefit, account scope, privacy explanation | Continue with selected provider | Other sign-in methods |
| `providerChoice` | Apple, passkey, security-key options with short descriptions | Use the selected method | Cancel / use another method |
| `presentingSystemUI` | Quiet progress and what to expect | System-owned | Cancel if the framework exposes cancellation |
| `serverVerifying` | “Checking your sign-in securely” and a bounded progress state | None that duplicates the request | Cancel only if the transaction can be safely abandoned |
| `verified` | Account name/identifier from the server, not raw credential data | Continue | Manage credentials |
| `linkReview` | Existing account, new credential, consequence, expiry | Add sign-in method | Cancel |
| `recovery` | Why the method is unavailable and supported alternatives | Choose recovery route | Contact/support path if the product has one |
| `revoked` | Credential no longer authorizes this account | Sign in again or recover | Preserve local work / sign out |

The view model should include a request or transaction epoch. A late delegate
callback from an abandoned flow must not replace a newer provider choice or
turn a signed-out view into a signed-in view.

## Use Apple’s system controls correctly

Use `SignInWithAppleButton` for the native SwiftUI Sign in with Apple action.
Respect Apple’s current button label, color, corner-radius, spacing, and
contrast guidance. Do not create a custom button that resembles the Apple
button but changes its semantics, hides required disclosure, or makes a
non-Apple action look equivalent.

For passkeys and security keys, the app’s button starts the request; the system
owns the credential picker, Face ID/Touch ID/passcode prompt, and hardware-key
ceremony. Keep the app-owned label action-oriented:

- “Use a passkey” when the server has an assertion transaction ready;
- “Create a passkey” when the person is creating a new credential;
- “Use security key” when an external key is actually supported by the route;
- “Add another sign-in method” when the person is linking a credential.

Do not label a generic button “Continue” if the person cannot tell what
credential or account operation it will start.

## Liquid Glass: group the task, not the trust

Liquid Glass is appropriate for a functional action group, a compact account
status card, or a review bar that remains legible over the current content. It
is not appropriate as a decorative full-screen frame around a sensitive system
ceremony or as a visual substitute for server verification.

Use this hierarchy:

~~~text
content background
  account purpose and short privacy explanation
  functional provider/action group
    Sign in with Apple system button
    Use a passkey
    Use security key (only when available)
  recovery/help action
  small server-verification status
~~~

Guidelines:

- Keep one clear primary action in the glass group.
- Use material and contrast that remain meaningful under Reduce Transparency.
- Avoid stacking several glass capsules around every provider; the hierarchy
  should come from labels and grouping, not repeated translucency.
- Keep system-owned authentication UI visually separate from the app’s shell.
- Use a plain semantic button and solid fallback treatment if the glass effect
  cannot convey boundaries in the current accessibility configuration.
- Avoid animating a transition into “verified” until the server response is
  received and current.
- Keep account identifiers and email text redacted or purpose-limited; do not
  put credential IDs, nonce values, or token fragments into the glass card.

The design should still read correctly as a static screenshot with all effects
disabled. If removing glass removes the distinction between pending, verified,
and revoked, the state design is too dependent on decoration.

## Account creation and linking screens

Account creation and credential linking are different tasks. Use different copy
and different proof gates:

### Create an account

Show the intended product account, the provider, any optional profile scope,
and the fact that the server will create an account after verification. If the
new iOS 26 account-creation provider uses accepted contact identifiers, explain
that the contact is used as part of setup and is not itself proof of ownership.

### Link a credential

Show the existing signed-in account before starting the second ceremony:

~~~text
Current account: alex@example app account
Adding: a passkey for example.com
Result: this passkey can be used to sign in to this account
Review expires: soon
[Add passkey] [Cancel]
~~~

Never make the model or a matching email address silently choose the account to
link. The server transaction must name the account and the user must review the
consequence. If two accounts collide, show a recovery path instead of offering
an automatic merge.

## Recovery is part of the first-run design

People lose devices, revoke Apple credentials, replace security keys, and use
private relay addresses. A polished authentication screen makes recovery
discoverable without making it the visual equal of the primary action.

Provide:

- another already registered credential when available;
- an explicit “I can’t use this method” route;
- a description of what local drafts and account data remain safe;
- a support or recovery handoff if the product has one;
- clear signed-out and revoked states;
- a way to manage/remove credentials after a verified session.

Do not promise that the app can recover an account if the server has no
verified recovery method. Do not delete local data simply because a credential
was revoked.

## Accessibility and alternate input

Authentication is a short task with high consequence. Verify the complete flow,
not just the initial button:

| Concern | Design requirement |
| --- | --- |
| VoiceOver | Announce provider, account context, pending server verification, and recovery state; keep focus on the next meaningful action after system UI dismisses |
| Dynamic Type | Preserve the distinction between provider name, account, scope, and consequence without truncation |
| Reduce Motion | State changes must be understandable without a glass morph or animated success transition |
| Reduce Transparency/Increase Contrast | Pending, verified, revoked, and destructive actions remain distinguishable without translucency |
| Voice Control | Use unique spoken labels such as “Use a passkey” and “Add passkey” rather than multiple “Continue” buttons |
| Switch Control | The system-button return, cancellation, retry, and recovery paths are reachable in order |
| Keyboard/pointer | Focus, Return, Escape/cancel, and sheet dismissal do not strand the person in a stale state |
| Localization/RTL | Provider names, legal/privacy copy, button labels, and account text wrap and mirror correctly |
| Color/contrast | Never use a green glass tint alone to mean server verification |

Use standard controls first. If a custom visual wrapper is needed, expose the
action and state through SwiftUI accessibility modifiers without hiding the
system control’s semantics.

## Privacy and disclosure copy

The privacy explanation should be brief and true:

- Sign in with Apple may return an opaque user identifier and, depending on the
  first authorization and requested scopes, optional name/email information.
- A private relay email is still an email address controlled by Apple’s relay;
  do not imply that it is the person’s direct address.
- A passkey registers a public credential with the relying party; the app does
  not receive the private key.
- A security key is a physical recovery dependency; tell the person what to do
  if it is lost.
- The app sends only the minimum credential result needed to the server and
  should not display or log tokens.

Avoid security theater such as “military grade,” “100% secure,” or a glass lock
icon that claims a state the server has not confirmed.

## Optional on-device AI explanation layer

Use on-device intelligence, if available, to explain the route in the person’s
language, summarize recovery choices, or prepare a comparison of provider
options. Treat the model output as a proposal:

~~~text
model proposal
  -> deterministic allowlist of providers and scopes
  -> current server transaction and domain revalidation
  -> human review for create/link/recovery consequence
  -> native AuthenticationServices action
~~~

The model must not receive authorization codes, identity tokens, passkey
assertions, private-key material, raw credential IDs, or unnecessary account
data. It must not invent an RP ID, origin, account ID, recovery method, or
server result. If the model is unavailable, stale, or fails validation, render
the same deterministic auth route with concise static explanations.

## Proof-oriented visual states

Design evidence fixtures for every meaningful state:

- provider available and unavailable;
- system UI presented, cancelled, and failed;
- server verification pending, accepted, rejected, and timed out;
- first Sign in with Apple authorization with optional fields;
- subsequent authorization without repeating optional profile fields;
- passkey registration and assertion;
- security-key connected, absent, cancelled, and lost/recovery states;
- associated-domain unavailable or stale;
- credential-provider extension list, selection, no-UI refusal, and cancellation;
- account-link review, collision, commit, and rollback;
- revoked Apple credential or server-revoked passkey;
- AI available, unavailable, stale, and rejected proposal.

Each fixture should keep a source revision and request epoch so a screenshot or
UI test cannot accidentally present a result from an older transaction.

## Related route pages

- [AuthenticationServices, passkeys, and account identity route](../42-framework-deep-dives/141-swiftui-authenticationservices-passkeys-route.md)
- [Authentication capability recipe](../50-capability-recipes/172-swiftui-authenticationservices-passkeys-route.md)
- [Authentication proof matrix](../60-verification/166-swiftui-authenticationservices-passkeys-proof-matrix.md)
- [Authentication Swift recipes](../70-code-recipes/184-swiftui-authenticationservices-passkeys-recipes.md)

## Sources

- [SignInWithAppleButton](https://developer.apple.com/documentation/authenticationservices/signinwithapplebutton)
- [Sign in with Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/sign-in-with-apple)
- [AuthenticationServices](https://developer.apple.com/documentation/authenticationservices)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [Implementing user authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [Public-private key authentication](https://developer.apple.com/documentation/authenticationservices/public-private-key-authentication)
- [Supporting security key authentication using physical keys](https://developer.apple.com/documentation/authenticationservices/supporting-security-key-authentication-using-physical-keys)
- [ASAuthorizationAccountCreationProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationaccountcreationprovider)
- [ASCredentialProviderViewController](https://developer.apple.com/documentation/authenticationservices/ascredentialproviderviewcontroller)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
