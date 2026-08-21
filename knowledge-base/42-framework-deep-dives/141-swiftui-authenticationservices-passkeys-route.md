# SwiftUI AuthenticationServices, passkeys, and account-identity route

Authentication is a trust protocol with a SwiftUI projection. The app owns the
user journey and its local state, AuthenticationServices owns the system
credential ceremony, and the server owns the authority to accept a credential
and create or resume a session. Keep those three responsibilities separate.

~~~text
Sign in with Apple
  -> ASAuthorizationAppleIDProvider request
  -> system authorization
  -> identity token + one-time authorization code
  -> server verifies with Apple
  -> account/session decision

platform passkey
  -> server challenge and relying-party policy
  -> ASAuthorizationPlatformPublicKeyCredentialProvider
  -> system passkey ceremony
  -> registration/assertion credential
  -> server verifies WebAuthn data and signature
  -> account/session decision

security key
  -> server challenge and RP policy
  -> ASAuthorizationSecurityKeyPublicKeyCredentialProvider
  -> physical NFC/USB/Lightning key ceremony
  -> server verifies credential and counter
  -> account/session decision

credential-provider extension
  -> system AutoFill/credential request
  -> extension target and app-owned credential store
  -> user interaction or permitted no-UI response
  -> extension completes or cancels the system request
~~~

An authorization callback is evidence that the system returned a credential
object to the app. It is not evidence that a server accepted the credential,
that a person owns an account, or that an account-linking operation is safe.
Do not unlock durable account state from a display name, email string, passkey
user name, Apple ID credential object, or simulator callback alone.

## Choose the identity lane

| Product requirement | Primary Apple route | Server responsibility | Evidence boundary |
| --- | --- | --- | --- |
| Let a person use their Apple account to enter the product | Sign in with Apple through `ASAuthorizationAppleIDProvider` | Validate the authorization code and identity token with Apple, bind the verified subject to an app account, and issue the app session | The Apple callback is only an input to server verification |
| Create or use a passwordless credential for this relying party | Platform passkeys through `ASAuthorizationPlatformPublicKeyCredentialProvider` | Generate a one-time challenge, validate WebAuthn registration/assertion, store the credential public key and counter, and issue the session | A successful biometric sheet is not a verified assertion until the server checks it |
| Support a removable hardware authenticator | Security-key provider and WebAuthn | Store the public key, validate the authenticator data and counter, and provide recovery for a lost key | A key tap or USB insertion proves ceremony completion, not account policy |
| Authenticate inside a web or browser-oriented flow | AuthenticationServices browser/public-key APIs plus the website’s relying-party configuration | Verify the returned client data and origin against the configured web domain | A URL callback must not be treated as a trusted session without server validation |
| Supply credentials to other apps and websites | Credential Provider Extension, identity store, and credential data manager | Keep extension-visible credentials scoped, current, and revocable; handle provider requests safely | An identity-store row is discoverability metadata, not a usable credential or account session |
| Fast account creation with a passkey and contact identifiers | `ASAuthorizationAccountCreationProvider` on its supported OS | Correlate accepted contact identifiers only after the server establishes ownership and policy | A contact hint does not prove that the person controls that address |

Do not make “Sign in with Apple,” “passkey,” and “credential provider” one
generic `login()` boolean. They have different server contracts, recovery
paths, revocation semantics, target configuration, user education, and physical
proof.

## Framework and target boundaries

AuthenticationServices provides several distinct layers:

- `ASAuthorizationController` coordinates one or more authorization requests,
  presents the system ceremony, and calls its delegate.
- `ASAuthorizationAppleIDProvider` creates Sign in with Apple requests and
  reports the current state of an Apple user identifier.
- `ASAuthorizationPlatformPublicKeyCredentialProvider` creates platform
  passkey registration and assertion requests for a relying-party identifier.
- `ASAuthorizationSecurityKeyPublicKeyCredentialProvider` creates requests for
  physical security keys.
- `ASAuthorizationAccountCreationProvider` adds the iOS 26 account-creation
  request lane for platform public-key credentials.
- `ASCredentialProviderViewController` is the root of a Credential Provider
  Extension target. It is not the same lifecycle as the containing app.
- `ASCredentialIdentityStore` publishes searchable identity metadata for a
  credential provider. `ASCredentialDataManager` reports current credential
  updates to the system on the newer SDK route.
- `SignInWithAppleButton` is a SwiftUI projection of the system Sign in with
  Apple action. It does not replace the server exchange.

Record the minimum deployment target for every new symbol. In the installed
iOS 26.4 SDK, the important additions for this route include:

| API or capability | Installed SDK boundary | Product implication |
| --- | --- | --- |
| `ASAuthorizationController` | Earlier iOS releases; verify the app’s deployment target | Keep the delegate/presentation lifecycle available in the target that owns the flow |
| Platform passkey provider | iOS 15 and later | The relying-party/domain configuration and server WebAuthn contract still gate usability |
| Security-key provider | iOS 15 and later | Physical-key loss and recovery are product requirements, not optional polish |
| `ASPublicKeyCredentialClientData` | iOS 17.4 and later | Browser-origin and top-origin claims require explicit server validation |
| `ASAuthorizationAccountCreationProvider` | iOS 26.0 and later | Gate fast account creation and keep a supported fallback for older targets |
| `ASCredentialDataManager` | iOS 26.2 and later | Use availability checks and retain a compatible update path where needed |
| Sign in with Apple SwiftUI button | Verify the installed SDK and target | Use the system control and current HIG label/style guidance; do not redraw the brand |

The exact deployment target is a build decision. The installed interface and
the current Apple documentation are the authority for the project being built;
this table is a route map, not a promise that every future SDK retains the same
surface.

### App capabilities and entitlements

The app target needs the capabilities appropriate to the selected lanes:

1. Add Sign in with Apple in Xcode for the Sign in with Apple route.
2. Add Associated Domains for passkeys/webcredentials and declare each relying
   party domain the app actually uses.
3. For a Credential Provider Extension, add the AutoFill Credential Provider
   entitlement to the extension target and configure its extension capability
   keys in the extension’s `Info.plist`.
4. If an App Group or Keychain access group carries credential metadata between
   the container and extension, configure and verify the signed target
   entitlements for both targets. Do not assume that target membership alone
   grants access.
5. Keep server configuration, Apple Developer configuration, Xcode project
   configuration, and signed-archive entitlements as separate evidence items.

For a passkey relying party such as `example.com`, the app’s associated-domain
entitlement uses the `webcredentials:` service. The website publishes an
Apple App Site Association file under `/.well-known/apple-app-site-association`
with the correct application identifier and webcredentials details. Each
subdomain is its own security and deployment boundary. Test the exact domain,
scheme, path, application identifier, certificate/HTTPS behavior, and the
distributed build on a physical device. A file that answers correctly to a
local `curl` request is not proof that the installed app received the current
association.

## `ASAuthorizationController` owns the ceremony, not the account

The coordinator must remain alive until the delegate callback or cancellation.
It supplies a presentation anchor for system UI and handles success and error
as separate states:

~~~text
idle
  -> request prepared
  -> system UI presenting
  -> credential returned | user cancelled | provider failed
  -> server verification pending
  -> session accepted | rejected | retry/recovery
~~~

Use `performRequests()` for an explicit request flow and use the documented
AutoFill-assisted route only where the product’s credential-provider behavior
requires it. Keep `cancel()` wired to the app’s cancel action and teardown.
Cancellation must stop pending work and invalidate the request epoch so a late
callback cannot commit an older account choice.

The delegate should copy the credential into a short-lived domain envelope,
redact logs, and hand it to a server-verification coordinator. It should not
write an authenticated session directly from the callback. The server response
must be bound to the request’s state, nonce/challenge, account intent, and the
current app session or account-linking transaction.

## Sign in with Apple choreography

For a native app flow:

1. Generate an unpredictable state value and nonce in the app or, preferably,
   obtain a server-created authorization transaction that the server can
   correlate. Never reuse a literal sample nonce.
2. Create an Apple ID request and ask only for the scopes the product needs.
   The first successful authorization may include name and email; later
   authorizations may not repeat those values.
3. Present `ASAuthorizationController` or `SignInWithAppleButton` from an
   intentional user action.
4. Send the authorization code, identity token, state/nonce correlation, and
   the minimum required credential fields to the server over an authenticated
   transport. Treat the code as short-lived and one-time.
5. The server validates the token signature/claims and exchanges the
   authorization code with Apple according to Apple’s current server contract.
   It verifies issuer, audience, expiry, nonce, and the app’s configured
   client/team relationship.
6. The server maps Apple’s stable subject identifier to the app account. Do not
   use the relay email as the durable primary key. Store the first-authorized
   optional profile fields only when the user has provided them and the product
   has a clear purpose.
7. Issue the app’s own session only after verification and account policy pass.
   The app then refreshes its domain state from the server.

`ASAuthorizationAppleIDCredential.user` is an opaque Apple identifier, not a
display identity. Apple documents that the identifier is stable for the
developer relationship while the user remains connected and can change after
the user disconnects. Support the credential states returned by
`getCredentialState(forUserID:)`, including authorized, revoked, not found, and
transferred cases exposed by the SDK. Also handle Apple’s revoked-credential
notification in a way that does not log the token or silently delete local
work.

Private Relay addresses, missing optional name data, account transfer, revoked
credentials, and user-requested deletion are normal states. Design an explicit
recovery and account-linking path rather than asking the person to create a
second account because an email string changed.

## Passkey registration and assertion

Passkeys use public-key authentication. The authenticator keeps the private key;
the relying-party server stores the public key and credential metadata. The
server must create the challenge and must verify the authenticator’s response.

### Registration

~~~text
server: create registration transaction
  -> RP ID and origin policy
  -> random challenge with expiry and transaction ID
  -> user/account ID that is stable for this relying party
app: createCredentialRegistrationRequest(challenge, name, userID)
system: user selects/creates a passkey
app: receives ASAuthorizationPlatformPublicKeyCredentialRegistration
server: verify client data, RP ID hash, flags, attestation policy if used,
        challenge, origin, algorithm, credential ID, and public key
server: store credential + counter + user binding + revision
server: issue session or continue explicit account setup
~~~

Use the server’s challenge bytes exactly. `Data("challenge".utf8)` is useful
only in a compile recipe; it is not a production challenge. Keep the account’s
passkey user ID opaque and stable. Do not derive it from a mutable email or
display name. Treat a credential ID as an identifier for one authenticator
credential, not as proof that the current device is trusted.

### Assertion

~~~text
server: create assertion transaction and random challenge
app: createCredentialAssertionRequest(challenge)
      optionally restrict to server-supplied allowedCredentials
system: user selects a passkey and completes local verification
app: receives assertion credential
server: verify challenge, origin, RP ID, signature, flags, user handle,
        credential ID, and the monotonic sign counter policy
server: update credential counter and issue/refresh session
~~~

Use `allowedCredentials` only from the current server transaction. An empty
list and a stale list have different UX and account-discovery implications.
Do not reveal whether a credential ID exists to an unauthenticated caller.
Counter rollback, duplicate assertions, challenge reuse, wrong origin, wrong RP
ID, expired transactions, and server/session mismatch must be explicit failure
states. If the product allows a passkey to replace another credential for the
same user ID, show the consequence and verify the current account policy first.

### Browser and origin data

When using the browser/public-key client-data APIs, the origin and optional
top-origin are security inputs. Configure the RP ID and domain association to
match the actual relying party. Do not accept `https://example.com` merely
because a returned string looks well formed. The server should compare the
origin to an allowlist for the transaction, verify the RP ID relationship, and
reject unexpected cross-origin or top-origin values.

## Security keys are a physical recovery problem

The security-key provider uses an external authenticator over the supported
physical transports. Build the user journey around the fact that a person can
lose, replace, lock out, or register multiple keys:

- show which account and relying party the key is being registered for;
- allow a person to name a key without treating that name as identity;
- require server verification before marking the key active;
- support more than one recovery credential when the product risk warrants it;
- make removal/revocation a server-authorized action;
- explain that losing every recovery method can make the account inaccessible;
- test NFC, USB, and Lightning behavior on the actual supported hardware and
  OS combinations rather than using a simulator callback.

Do not copy a security-key registration flow into a platform-passkey flow and
hide the transport difference. The ceremony, hardware failure mode, recovery
copy, and physical evidence differ.

## Account creation and account linking

`ASAuthorizationAccountCreationProvider` can help a product request a platform
public-key registration with accepted contact identifiers and an optional name
request on supported iOS 26 targets. Treat accepted contacts as server-issued
hints in a bounded account-creation transaction, not as proof of ownership.

For linking a new credential to an existing account:

1. The person must already have an authenticated app session or complete a
   fresh strong authentication for the existing account.
2. Start a server-issued link transaction with a short expiry and explicit
   account ID; do not let the client choose an arbitrary account ID.
3. Complete the second credential ceremony and verify it independently.
4. Show the account, credential type, relying party, and consequences before
   committing the link.
5. Commit on the server with an idempotency key and audit event.
6. Refresh local sessions and credential state from the server; never merge
   accounts from matching display names or relay addresses alone.

For unlink, deletion, Apple credential revocation, passkey replacement, and
lost security keys, require a recovery method that still exists. Preserve
local drafts and provide a clear signed-out state; do not erase user content
as a side effect of a rejected token.

## Credential Provider Extension lifecycle

A Credential Provider Extension is a separate target with a separate process
and lifecycle. It may be asked to:

- prepare a credential list for service identifiers;
- prepare a credential for an explicit request;
- provide a credential without user interaction when the system permits it;
- prepare an extension configuration interface;
- begin passkey registration or password generation/save flows on supported
  SDKs; and
- cancel through `extensionContext` when the user or system ends the request.

Design the extension around small, deterministic operations:

~~~text
system request
  -> extension launched
  -> configuration/credential list prepared
  -> user selection or permitted no-UI resolution
  -> credential supplied OR explicit cancellation/error
  -> extension releases request-scoped state
~~~

The extension must not assume the containing app is running, that network is
available, or that the app’s in-memory session exists. Put only the minimum
shared state in a correctly configured App Group or Keychain access group.
Keep secrets out of logs and out of display metadata. A no-user-interaction
method must not silently open custom UI or perform an unreviewed account
mutation.

`ASCredentialIdentityStore` is an index of identities the system can search.
Publish only identities the provider can actually resolve, remove stale
identities when the server or user revokes them, and bind service identifiers
to the correct relying-party/domain policy. `ASCredentialDataManager` update
reports are requests to inform the system; Apple’s documentation distinguishes
well-formed parameters from proof that the provider successfully completed its
own server-side update. Retain an app-owned reconciliation log and retry
policy.

## SwiftUI and Liquid Glass composition

Use `SignInWithAppleButton` for the system Sign in with Apple action and use
the documented system credential ceremonies for passkeys and security keys.
The system owns the sensitive authentication sheet, biometric prompt, and
brand treatment. Do not draw a fake Apple button, a fake passkey sheet, or a
custom “verified” glass badge that suggests the local callback is already a
server-authenticated session.

The app-owned SwiftUI shell can use native layout and, where appropriate,
Liquid Glass for functional grouping:

- explain the outcome and account context above the system action;
- group related sign-in choices in one hierarchy without making all choices
  look identical;
- show a quiet pending state while server verification runs;
- show recovery and account-linking consequences before a mutation;
- use glass for a functional action group or status container, not as a trust
  signal or permanent decorative frame;
- keep the system button visually recognizable and accessible;
- preserve a useful non-glass fallback under reduced transparency, contrast,
  Dynamic Type, VoiceOver, and keyboard/pointer input.

Authentication copy should explain what the app will receive and what it will
not receive. Do not promise that an email or name will be returned on every
authorization.

## Optional on-device AI account-setup proposals

An on-device model can help explain a choice or organize a person’s account
setup options, but it must not become the authority that accepts credentials,
chooses a relying-party domain, generates a security policy, invents a recovery
route, or commits an account link.

Use a typed proposal with deterministic fields such as:

~~~text
AccountSetupProposal
  provider: appleID | platformPasskey | securityKey | existingSession
  purpose: signIn | createAccount | linkCredential | recover
  relyingPartyID: allowlisted server value only
  requestedScopes: allowlisted values only
  explanation: model-generated, non-authoritative text
  sourceRevision: current server/app policy revision
  expiresAt: short-lived review deadline
  requiresUserConfirmation: true
~~~

The deterministic layer must re-resolve provider eligibility, current session,
server transaction, domain association, and account state after the model
responds. Reject stale revisions, unknown enum values, raw tokens, arbitrary
URLs, account IDs, or model-generated credential bytes. The final action must
be user-reviewed where it changes identity, links accounts, registers a key, or
requests a scope.

## Failure and recovery map

| Failure | Preserve | Recovery |
| --- | --- | --- |
| User cancels system UI | Current signed-in session and local drafts | Return to the same task with a clear retry or alternate credential action |
| Server rejects challenge/nonce | No authenticated state | Start a fresh transaction; do not retry a consumed challenge |
| Passkey domain association unavailable | Existing account data | Explain that this build/domain is not ready and offer a supported fallback |
| Apple credential revoked | Local content and audit record | Require an available recovery method and allow explicit reauthentication/linking |
| Apple account transferred/not found | Local content and non-secret preferences | Show a recovery route; do not silently create a second account |
| Security key missing | Server account and other credentials | Offer another registered credential or recovery process |
| Credential-provider extension killed | Durable provider state | Reopen request with a new request-scoped epoch; never reuse stale completion |
| Account-link collision | Both source accounts | Require authenticated review of both accounts and an explicit merge policy |
| AI unavailable or stale | Deterministic auth route | Continue with native controls and current server policy |

## Proof levels

Keep these evidence levels separate:

1. **Source level:** official docs and SDK headers describe the API.
2. **Compile level:** a recipe typechecks against a named SDK.
3. **Configuration level:** capabilities, entitlements, AASA, target membership,
   and server settings are present in the built artifact.
4. **Simulator level:** deterministic UI and callback paths work in a test
   environment.
5. **Physical/system level:** a real iPhone completes passkey, Apple ID,
   security-key, or AutoFill system behavior with the intended domains.
6. **Server level:** challenges, origin, nonce, token exchange, counters,
   account binding, revocation, and recovery are verified against a staging
   service.
7. **Release level:** the archived/TestFlight build carries the same target
   configuration and the real distribution path works.

Do not collapse these into “authentication works.” A local callback proves only
one link in the chain.

## Related route pages

- [Passkeys and authentication design](../21-design-deep-dives/169-swiftui-authenticationservices-passkeys-route-design.md)
- [Authentication capability recipe](../50-capability-recipes/172-swiftui-authenticationservices-passkeys-route.md)
- [Authentication proof matrix](../60-verification/166-swiftui-authenticationservices-passkeys-proof-matrix.md)
- [Authentication Swift recipes](../70-code-recipes/184-swiftui-authenticationservices-passkeys-recipes.md)
- [Security, Keychain, CryptoKit, and protected local AI](134-swiftui-security-keychain-cryptokit-protected-ai-route.md)

## Sources

- [AuthenticationServices](https://developer.apple.com/documentation/authenticationservices)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [ASAuthorizationControllerDelegate](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontrollerdelegate)
- [ASAuthorizationControllerPresentationContextProviding](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontrollerpresentationcontextproviding)
- [ASAuthorizationAppleIDProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidprovider)
- [ASAuthorizationAppleIDRequest](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidrequest)
- [ASAuthorizationAppleIDCredential](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidcredential)
- [Implementing user authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [Configuring Sign in with Apple](https://developer.apple.com/documentation/xcode/configuring-sign-in-with-apple)
- [ASAuthorizationPlatformPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialprovider)
- [ASAuthorizationPlatformPublicKeyCredentialRegistrationRequest](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialregistrationrequest)
- [ASAuthorizationPlatformPublicKeyCredentialAssertionRequest](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialassertionrequest)
- [Public-private key authentication](https://developer.apple.com/documentation/authenticationservices/public-private-key-authentication)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [Connecting to a service with passkeys](https://developer.apple.com/documentation/authenticationservices/connecting-to-a-service-with-passkeys)
- [Performing fast account creation with passkeys](https://developer.apple.com/documentation/authenticationservices/performing-fast-account-creation-with-passkeys)
- [ASAuthorizationSecurityKeyPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationsecuritykeypublickeycredentialprovider)
- [Supporting security key authentication using physical keys](https://developer.apple.com/documentation/authenticationservices/supporting-security-key-authentication-using-physical-keys)
- [Passkey use in web browsers](https://developer.apple.com/documentation/authenticationservices/passkey-use-in-web-browsers)
- [Authenticating people by using passkeys in browser apps](https://developer.apple.com/documentation/authenticationservices/authenticating-people-by-using-passkeys-in-browser-apps)
- [ASPublicKeyCredentialClientData](https://developer.apple.com/documentation/authenticationservices/aspublickeycredentialclientdata)
- [ASAuthorizationAccountCreationProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationaccountcreationprovider)
- [ASCredentialProviderViewController](https://developer.apple.com/documentation/authenticationservices/ascredentialproviderviewcontroller)
- [ASCredentialProviderExtensionContext](https://developer.apple.com/documentation/authenticationservices/ascredentialproviderviewcontroller/extensioncontext)
- [Preparing the interface for extension configuration](https://developer.apple.com/documentation/authenticationservices/ascredentialproviderviewcontroller/prepareinterfaceforextensionconfiguration%28%29)
- [ASCredentialIdentityStore](https://developer.apple.com/documentation/authenticationservices/ascredentialidentitystore)
- [ASCredentialDataManager](https://developer.apple.com/documentation/authenticationservices/ascredentialdatamanager)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [SignInWithAppleButton](https://developer.apple.com/documentation/authenticationservices/signinwithapplebutton)
- [Sign in with Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/sign-in-with-apple)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
