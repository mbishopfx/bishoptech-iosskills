# SwiftUI AuthenticationServices and passkey capability recipe

Use this recipe when an iOS 26 app needs Sign in with Apple, passkeys,
security keys, account linking, or a Credential Provider Extension. The route
is complete only when the target configuration, server verification, native
system ceremony, accessibility, recovery, and release evidence agree.

The companion pages are the [AuthenticationServices route](../42-framework-deep-dives/141-swiftui-authenticationservices-passkeys-route.md),
[design guide](../21-design-deep-dives/169-swiftui-authenticationservices-passkeys-route-design.md),
[proof matrix](../60-verification/166-swiftui-authenticationservices-passkeys-proof-matrix.md),
and [compile-oriented Swift recipes](../70-code-recipes/184-swiftui-authenticationservices-passkeys-recipes.md).

## 1. Choose the capability lane

| Need | App target | Other target/configuration | Server contract |
| --- | --- | --- | --- |
| Sign in with Apple | AuthenticationServices import and Sign in with Apple capability | Apple Developer/App ID configuration; backend client/team configuration | State/nonce, authorization-code exchange, identity-token validation, stable subject mapping, revoke/recovery |
| Platform passkey | AuthenticationServices + Associated Domains | `webcredentials:` domain and AASA file; server RP/origin configuration | Registration/assertion challenge, WebAuthn validation, public-key/counter storage, session issuance |
| Security key | AuthenticationServices | Physical-key support policy and recovery UX | Same WebAuthn verification with key-specific registration and recovery |
| Browser/web passkey | AuthenticationServices browser/public-key route | Exact associated domain, website RP ID/origin, HTTPS/AASA | Client-data origin/top-origin/RP validation and server session binding |
| Credential provider | Containing app plus Credential Provider Extension | AutoFill Credential Provider entitlement, extension capability `Info.plist`, optional App Group/Keychain group | Credential lookup/update/revocation, provider identity, extension-safe lifecycle |

Do not add every entitlement because the product may eventually need it. Start
with a capability decision record that names the identity lane, target, minimum
OS, server environment, domain, data scope, recovery method, and proof owner.

## 2. Configure the app and website

For a passkey relying party, the declarations must agree:

~~~text
Xcode app target
  Associated Domains capability
  webcredentials:example.com

website
  https://example.com/.well-known/apple-app-site-association
  application identifier for the distributed app
  webcredentials details for the relying-party domain

server
  RP ID: example.com
  accepted origins: explicit allowlist
  challenge store: one-time, short-lived, transaction-bound
~~~

Every subdomain is a separate association decision. Check the application
identifier in the signed archive, the entitlement in the TestFlight build, and
the exact production domain. A local file, a development domain, or a browser
success does not prove the distributed app’s association.

For Sign in with Apple, configure the capability and server relationship in
Apple Developer and Xcode. Store the team/client identifiers and private-key
material only in the server’s secret manager. The app should receive the
minimum authorization result needed for the server transaction; it should not
contain a long-lived Apple client secret.

For a Credential Provider Extension, create a separate extension target,
subclass `ASCredentialProviderViewController`, add the AutoFill Credential
Provider entitlement to the correct target, and configure the supported
extension capabilities. Verify the extension’s embedded provisioning and
entitlements separately from the containing app.

## 3. Define server transactions before client requests

Create server-side transactions with an explicit type:

~~~text
AuthTransaction
  id: opaque transaction ID
  accountIntent: signIn | create | link
  provider: appleID | platformPasskey | securityKey
  relyingPartyID: server allowlist value
  expectedOrigin: server allowlist value
  challenge: random, one-time bytes
  nonce: random value when required by the provider flow
  accountID: server-selected for link or authenticated create context
  expiresAt: short deadline
  requestEpoch: monotonic client/server correlation
  usedAt: nil until atomically consumed
~~~

The server returns only the challenge and the minimum policy fields needed by
the app. Never let an unauthenticated client choose an arbitrary RP ID, origin,
account ID, or credential policy. Consume the transaction atomically when the
server verifies the response. A retry after consumption creates a new
transaction.

## 4. Native client flow

The app coordinator owns a short-lived authorization request and the SwiftUI
view owns a projection of its state:

~~~text
user action
  -> request server transaction
  -> check local framework/domain availability
  -> create provider request with server challenge
  -> retain ASAuthorizationController delegate/presentation coordinator
  -> perform system ceremony
  -> send returned credential envelope to server
  -> render pending/accepted/rejected state
  -> refresh app session and current account projection
~~~

Use an epoch on every request. On cancellation, timeout, view teardown, or
account switch, mark the epoch inactive. A callback from an inactive epoch may
be logged as a redacted diagnostic but cannot commit authentication state.

The presentation anchor must belong to the active window/scene that owns the
flow. In a multiwindow app, do not use a global window lookup that can present
system UI over the wrong scene.

## 5. Sign in with Apple route

1. Start a server transaction with state and nonce correlation.
2. Create `ASAuthorizationAppleIDProvider().createRequest()` and request only
   the scopes needed by the product.
3. Present through `ASAuthorizationController` or SwiftUI’s
   `SignInWithAppleButton`.
4. On success, send the authorization code and identity token to the server
   over the app’s authenticated API channel. Redact them from logs and crash
   reports.
5. The server validates the Apple token claims and performs the current Apple
   authorization-code exchange. It validates issuer, audience, expiry, nonce,
   and the configured client/team relationship.
6. Map the verified Apple subject to the product account. Store optional name
   and email only when returned and needed. Support relay email and missing
   profile data.
7. Return the app’s own session and a redacted account projection.

The app’s `user` field is an opaque identifier. Do not make an email address,
display name, or first-time profile payload the account primary key. On later
authorization the optional name/email values may be absent. Handle credential
state changes and revocation as server/account events, not as an invitation to
silently create a duplicate account.

## 6. Platform passkey registration route

The server sends the challenge, RP ID, and an opaque stable user ID. The app
creates `ASAuthorizationPlatformPublicKeyCredentialProvider` with the exact RP
ID and creates the registration request with the server challenge, display
name, and user ID. After the system ceremony:

~~~text
registration response
  -> clientDataJSON / client data
  -> RP ID hash and authenticator data
  -> credential ID and public key material
  -> server validation of challenge, origin, flags, algorithm, and policy
  -> credential record stored against the verified account
~~~

The server must decide whether it accepts or ignores attestation, how it
handles user verification flags, and how it stores the sign counter. The app
does not make those security decisions from a local callback. A successful
registration must be idempotent for the transaction but must not accidentally
replace an existing credential without an explicit product policy.

## 7. Platform passkey assertion route

1. Ask the server for a fresh assertion transaction.
2. Pass the challenge to `createCredentialAssertionRequest(challenge:)`.
3. If the server supplied an allowlist of credential IDs, apply it exactly and
   do not reveal whether a credential exists in a local error message.
4. Send the assertion response to the server.
5. Verify the challenge, expected origin, RP ID, signature, flags, user handle,
   credential ID, and counter policy.
6. Update the credential record and issue the app session atomically.

An assertion is not a login until the server accepts it. Preserve the signed-out
state while verification is pending. If verification fails, create a new
transaction for retry rather than replaying the old challenge.

## 8. Security-key route

Use `ASAuthorizationSecurityKeyPublicKeyCredentialProvider` with the same
server-owned challenge and RP policy, but provide copy that makes the physical
key requirement clear. Test:

- NFC tap and removal during the ceremony;
- USB/Lightning connection and cancellation;
- a key that is not registered for the account;
- a key with a changed PIN or lockout state;
- a lost key with another recovery method;
- registration of multiple keys and explicit removal;
- returning to the app after the system prompt is dismissed.

The server stores the public credential and key metadata, never the private
key. The local app does not treat a key display name or transport type as an
account identity.

## 9. Account creation and linking

For a new account, use the server’s account-creation transaction and make the
resulting account scope explicit. For a link:

~~~text
verified existing session
  -> server creates link transaction for account A
  -> second credential ceremony
  -> server verifies credential independently
  -> SwiftUI review shows account A + new credential + consequence
  -> server commits idempotent link
  -> app refreshes session/credential list
~~~

`ASAuthorizationAccountCreationProvider` can supply a fast platform-public-key
registration path on iOS 26. Gate it with `if #available`, preserve an older
passkey route, and keep accepted contact identifiers as server policy inputs.
Do not use a model or a matching email to select account A.

For merge/collision recovery, require authenticated proof for both account
roots and define ownership of data, subscriptions, entitlements, and existing
credentials. If the product cannot safely merge, preserve both accounts and
route the person to support.

## 10. Credential Provider Extension route

Implement the extension as a small system service:

1. `prepareCredentialList(for:)` resolves only identities that the extension
   can currently provide.
2. The user chooses a credential and the extension completes the system request
   with the correct credential type.
3. For passkeys or specialized requests, use the documented
   `prepareInterfaceToProvideCredential(for:)` and related lifecycle methods.
4. If a request cannot be fulfilled, call `extensionContext.cancelRequest` with
   an explicit error instead of leaving the system hanging.
5. Keep no-UI methods free of unapproved custom presentation and respect the
   system’s interaction contract.
6. Remove stale `ASCredentialIdentityStore` rows and report server-driven
   updates through the current `ASCredentialDataManager` path where available.

The extension may be relaunched independently. Reopen the provider store from
durable, least-privilege state and use a request epoch. Do not assume a shared
in-memory account session or a network connection. If the extension needs
shared data, verify App Group/Keychain policy in the signed artifact.

## 11. SwiftUI review shell

Use a `NavigationStack` or a focused sheet for app-owned context. A simple
review shell contains:

- account/task context;
- provider and relying-party display text from an allowlist;
- one native system action;
- a server-verification progress state;
- recovery/cancel actions;
- a result projection from the server, not raw credential fields.

Use Liquid Glass only where it groups a functional action or status. Preserve
meaning under reduced transparency and increased contrast. Keep the Apple
button/system prompt system-owned and do not place a fake lock/verified badge
over it.

## 12. Optional typed AI proposal

If on-device AI is available, give it a redacted, typed context such as
`providerAvailability`, `accountIntent`, `recoveryOptions`, and a policy
revision. It may produce an explanation or a proposed provider ordering. A
deterministic validator must:

- accept only allowlisted provider enum values;
- re-read current session, domain, entitlement, server transaction, and
  availability state;
- reject arbitrary domains, account IDs, scopes, tokens, challenge bytes, or
  credential material;
- expire proposals when the transaction or policy revision changes;
- require user review for create, link, recover, register, remove, or scope
  changes; and
- fall back to a static route when the model is unavailable.

The model never verifies a credential, issues a session, or makes an account
merge decision.

## 13. Minimum acceptance checklist

### Configuration

- [ ] The chosen lane, target, minimum OS, RP ID, origin, and server environment
  are recorded.
- [ ] Sign in with Apple, Associated Domains, or AutoFill Credential Provider
  capabilities are present only where needed.
- [ ] AASA and `webcredentials` configuration match the distributed bundle ID.
- [ ] Extension target, Info.plist capability flags, App Group, and Keychain
  access policy are signed and separately verified.

### Runtime

- [ ] Coordinator/delegate/presentation anchor lifetime is retained correctly.
- [ ] Every request uses a fresh server transaction and epoch.
- [ ] Cancellation, timeout, late callback, and scene teardown are safe.
- [ ] Apple token/code and passkey assertion are sent only to the server and
  never logged.
- [ ] Server verifies all provider-specific claims before issuing a session.
- [ ] Account linking, revocation, lost-key recovery, and duplicate-account
  collisions are explicit.

### Design and proof

- [ ] Native system controls are used with correct labels and accessibility.
- [ ] Liquid Glass is functional grouping, not a fake trust indicator.
- [ ] Dynamic Type, VoiceOver, Voice Control, Switch Control, keyboard, pointer,
  Reduce Motion, and Reduce Transparency are tested.
- [ ] Physical iPhone and actual security-key/AutoFill/domain behavior are tested.
- [ ] Archive/TestFlight entitlements and AASA behavior are verified.
- [ ] Optional AI is typed, redacted, stale-safe, user-reviewed, and never the
  authority for credential acceptance or account mutation.

## Sources

- [AuthenticationServices](https://developer.apple.com/documentation/authenticationservices)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [ASAuthorizationAppleIDProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidprovider)
- [Implementing user authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [Configuring Sign in with Apple](https://developer.apple.com/documentation/xcode/configuring-sign-in-with-apple)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [Connecting to a service with passkeys](https://developer.apple.com/documentation/authenticationservices/connecting-to-a-service-with-passkeys)
- [Public-private key authentication](https://developer.apple.com/documentation/authenticationservices/public-private-key-authentication)
- [Supporting security key authentication using physical keys](https://developer.apple.com/documentation/authenticationservices/supporting-security-key-authentication-using-physical-keys)
- [ASAuthorizationAccountCreationProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationaccountcreationprovider)
- [ASCredentialProviderViewController](https://developer.apple.com/documentation/authenticationservices/ascredentialproviderviewcontroller)
- [ASCredentialIdentityStore](https://developer.apple.com/documentation/authenticationservices/ascredentialidentitystore)
- [ASCredentialDataManager](https://developer.apple.com/documentation/authenticationservices/ascredentialdatamanager)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [SignInWithAppleButton](https://developer.apple.com/documentation/authenticationservices/signinwithapplebutton)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
