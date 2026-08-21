# Commerce, Networking, Security, and Identity

## Capability boundary

Keep purchase, identity, secrets, local authentication, cryptography, device integrity, and networking as separate trust boundaries. A system UI or framework callback can improve the signal, but the product must still decide what is authorized, what is stored, what is sent to a server, and what fallback is safe.

| Need | Native route | Core proof |
| --- | --- | --- |
| Digital purchase/subscription | StoreKit 2 | App Store-signed transaction verification, current entitlement/subscription state, restore/refund/expiry, and release configuration. |
| Physical payment | PassKit Apple Pay | Merchant/capability setup, payment request/token, provider/server processing, and signed physical-device sandbox flow. |
| Wallet pass | PassKit Wallet | Pass signing/type ID, Wallet capability, add/update/revoke lifecycle, and real Wallet presentation. |
| Apple Account sign-in | AuthenticationServices / Sign in with Apple | Nonce/state, server token verification, stable user ID, relay email, revocation, and account deletion/linking. |
| Secret/token/key storage | Keychain/Security | Item class, accessibility, access control, migration/sync, delete/update, and redacted diagnostics. |
| Local unlock | LocalAuthentication | Device-user presence, policy/fallback/lockout, protected Keychain item, and no server-identity claim. |
| App-instance/fraud signal | DeviceCheck/App Attest | Server challenge, attestation/assertion validation, replay defense, unsupported-device policy, and risk model. |
| API/custom transport | URLSession/Network | TLS/authentication, request integrity, cancellation/retry/idempotency, server authorization, and privacy. |

## StoreKit 2 entitlement route

### State and verification

Use StoreKit 2’s Swift/concurrency route for digital goods and subscriptions. Keep product loading, purchase, transaction update, verification, entitlement, pending, cancellation, refund/revocation, expiry/grace, restore, and error states separate:

`idle -> loadingProducts -> ready -> purchasing -> pending|verified|unverified|cancelled|failed -> entitled|notEntitled|expired`

Product metadata is not entitlement. A purchase result is not access until the transaction is verified and the product’s business rule grants it. Iterate `Transaction.updates` while the app is running and `Transaction.currentEntitlements` when refreshing access. Finish a verified transaction after delivering its content/entitlement so it does not remain unfinished. Consumables and current entitlements have different semantics; do not use one restore loop for every product type.

If a server account controls access across devices or a backend delivers premium data, send the appropriate signed transaction/subscription material to a server that verifies it. The app’s local verification and a server’s account authorization answer different questions. Never persist a product ID or “premium=true” flag as the only proof.

### Testing boundary

StoreKit Testing and a local StoreKit configuration can exercise product IDs, purchase paths, pending/cancelled outcomes, renewals, refunds, and restore logic deterministically. They do not prove App Store Connect metadata, sandbox/TestFlight Apple Account state, production storefronts, server reconciliation, regional availability, or App Review configuration. Keep a signed sandbox/TestFlight run in the release evidence.

## PassKit Apple Pay and Wallet

### Apple Pay

Use Apple Pay/PassKit for physical goods or services when the product and region/provider support it. Configure the merchant identifier, Apple Pay capability, payment-processing certificate/provider, supported networks/capabilities, country/currency, shipping/contact requirements, and server handoff. Check availability before presenting the sheet.

The Apple Pay sheet authorizes a payment request and gives the app a payment token for the payment processor. A presented sheet or token is not proof that the merchant backend captured funds or fulfilled the order. Model `unavailable -> presenting -> authorizedToken -> processing -> fulfilled|declined|retry` and show a clear result from the provider/server.

Do not use Apple Pay for digital content consumed inside the app where StoreKit is the appropriate route. A local simulator or fixture payment token is not a production payment proof.

### Wallet

Wallet passes are signed artifacts with a pass type/distribution lifecycle. Review the Wallet capability/pass type IDs, pass signing, add/update/revoke channel, user authorization, supported pass/device family, and privacy of pass fields. `PKAddPassesViewController` or the SwiftUI/system route can present adding; `PKPassLibrary` can inspect/manage the app’s allowed pass scope.

Identity presentment, payment passes, secure-element passes, car keys, and ordinary tickets/loyalty passes are different routes with different entitlements and review requirements. Do not treat “pass added” as identity verification or a guarantee that a pass is current.

## Sign in with Apple route

Keep native authorization, credential state, account linking, and server verification distinct:

1. Create the Apple ID authorization request with the requested scopes and a cryptographically random nonce/state strategy appropriate to the flow.
2. Present the system authorization controller and handle success/cancellation/error.
3. Persist the stable Apple user identifier and only the minimum returned profile data in Keychain/app state.
4. Send identity material to the server over authenticated transport when an account/backend exists; verify the authorization response/token server-side.
5. Treat name/email as first-authorization data that may not be returned on subsequent sign-ins, and support private relay email.
6. Check credential state at launch/return and handle `authorized`, `revoked`, `notFound`, and transient states.
7. Make sign-out, account linking, data deletion, and local-data ownership explicit.

Sign in with Apple authenticates a user to the Apple ID flow; it does not grant access to an app’s business resources without server authorization. A valid user identifier is not a subscription, organization membership, or permission to read another account’s data.

## Keychain and LocalAuthentication

### Store the minimum secret

Use Keychain Services for small credentials, refresh tokens, private key references, and stable local identifiers. Choose the item class, `kSecAttrAccessible` value, synchronizability, access group, and `SecAccessControl` from the threat model. The most restrictive setting that still supports the workflow is preferred; `ThisDeviceOnly` and passcode/biometric requirements change migration and recovery behavior.

Do not store secrets in `UserDefaults`, logs, analytics, source control, URLs, ordinary SwiftData fields, or screenshots. Keychain persistence across uninstall/reinstall, backup/restore, device migration, and access-group changes must be tested and documented.

### Gate a sensitive action

`LAContext` can evaluate device-owner authentication or an access-control operation. The result proves a device authentication policy succeeded at that moment; it does not prove server identity, account ownership, payment entitlement, or authorization to perform an unrelated business action. Use a protected Keychain item/access control when the secret itself must be gated, and handle cancellation, fallback, lockout, unavailable biometrics, passcode, and policy changes.

## CryptoKit and transport

Use CryptoKit’s established primitives for a defined protocol and document key generation, storage, rotation, nonce/IV, associated data, algorithm, recovery, deletion, and versioning. Do not invent encryption, password hashing, token signing, or certificate validation schemes.

Use URLSession for HTTP/API traffic and Network for custom/local protocols. Centralize request construction, TLS/authentication, timeouts, cancellation, redacted logs, retries, and idempotency. A client-side check is not server authorization. Never put access tokens or personal data in query strings unless the protocol explicitly requires it and the privacy review accepts the exposure.

## Trust-boundary API matrix

Choose the API from the claim the product needs to make. Keep credentials, authorization, cryptographic proof, and transport state behind separate adapters.

| Claim/need | API route | App-owned boundary | Proof gate |
| --- | --- | --- | --- |
| HTTP/API request | `URLSession`, `URLRequest`, `URLSessionTask` | Request builder, auth/header policy, decoder, cancellation, retry/idempotency | ATS/TLS, certificate/server policy, expired token, malformed response, offline/cache, redacted logs, and server authorization. |
| Custom/local transport | `NWConnection`, `NWParameters`, Network protocol options | Endpoint identity, framing, state machine, protocol version, reconnect | TLS/authentication, local-network permission, network changes, timeout, malformed peer, and topology/device test. |
| Apple Account sign-in | `ASAuthorizationAppleIDProvider` + authorization request/controller | Nonce/state, stable user ID, first-profile capture, credential state, account linking/deletion | Server token verification, revoked/not-found state, relay email, replay protection, and signed target. |
| Secret storage | Keychain `SecItemAdd`/`CopyMatching`/`Update`/`Delete` | Item class/accessibility/access group, migration, deletion, redacted diagnostics | Lock/passcode/biometric/access-group/device migration/backup/reinstall behavior. |
| Local gate | `LAContext` or Keychain access control | Operation purpose, fallback, lockout, protected-secret access | Device-owner authentication result plus protected operation; never treat it as account or payment identity. |
| Data confidentiality/integrity | CryptoKit `AES.GCM`, `SHA256`, Curve25519/signing primitives as appropriate | Key generation/storage/rotation, nonce/associated data, protocol version, recovery/deletion | Known-answer tests, key loss/rotation, tamper/replay, secure storage, and server/peer verification. |
| App-instance signal | `DCDevice` / `DCAppAttestService` | Server challenge, key ID, attestation/assertion request, degraded-risk policy | Server-side Apple validation, request binding, one-time nonce, replay rejection, unsupported/key-loss handling. |

## Request and identity state machines

For network calls, model:

`idle -> preparing -> authenticating -> connecting -> sending -> receiving -> decoding -> authorized|success|retryable|reauthenticate|failed|cancelled`

Do not retry every error. Classify transport failure, timeout, server 4xx/5xx, expired credential, malformed response, authorization denial, and user cancellation. Only retry idempotent operations or operations with an explicit idempotency key; persist an outbox for consequential writes rather than replaying an unknown POST.

For Sign in with Apple:

`signedOut -> requesting -> authorizedLocally -> serverVerifying -> linked|serverRejected -> credentialRevoked|accountDeleted`

For App Attest:

`noKey -> generating -> attesting -> keyRegistered -> asserting -> serverAccepted|serverRejected|degraded`

For Keychain/local authentication, distinguish `itemMissing`, `itemLocked`, `biometricUnavailable`, `biometricChanged`, `userCancelled`, `accessDenied`, `authenticated`, and `serverSessionExpired`. The same UI “unlock” action can cross several trust boundaries; report which one succeeded.

## Target and configuration matrix

| Route | Target/configuration | Do not infer |
| --- | --- | --- |
| URLSession backend | App/service target with ATS and URL/request policy | A successful local HTTP response proves server authorization or production TLS configuration. |
| Sign in with Apple | App target plus associated server/client identifier and account-deletion route | A locally returned credential proves the server accepted or linked the account. |
| Keychain access group | Exact app/extension targets and shared access group entitlement | An App Group or bundle ID alone proves a Keychain item is readable. |
| LocalAuthentication | Device policy and protected Keychain item | A biometric/passcode result proves identity, payment, entitlement, or authorization to another account. |
| App Attest/DeviceCheck | App target plus server validation and development/production environment | A generated key or client-side assertion proves app integrity without server validation. |
| CryptoKit | Shared protocol module with explicit key/nonce/version contract | Encryption alone solves key management, authorization, deletion, or endpoint compromise. |
| Local-network/accessory transport | Network target/permissions plus peer protocol | Discovery/name/IP proves peer identity or trust. |

Return a typed trust result to the domain layer, for example `transportConnected`, `serverAuthorized`, `userAuthenticated`, `secretUnlocked`, `entitlementVerified`, or `appAttested`. Avoid a single `isSecure` flag that collapses different evidence.

## DeviceCheck and App Attest

DeviceCheck can provide a server-managed token and per-device bits for a fraud/abuse policy. App Attest can create a device-backed key, request Apple attestation, and generate assertions over server challenges/request data. The server must validate the attestation/assertion and apply a risk policy; the app cannot verify its own integrity authoritatively.

Model unsupported service, key missing, attestation pending, invalid assertion, replay/challenge failure, server unavailable, and degraded-risk states. Use a one-time server challenge, bind the assertion to the request hash, store the key identifier without the private key, and define key loss/reinstall/restore behavior. Neither service is absolute protection against a compromised device or fraudulent user; they are inputs to a broader authorization/risk system.

## Unified proof and fallback

| Claim | Minimum evidence |
| --- | --- |
| “The user owns this digital entitlement” | Verified StoreKit transaction/current entitlement plus account/server policy where applicable. |
| “The provider processed this payment” | Apple Pay/PassKit token plus payment-provider/server success and fulfillment state. |
| “This pass is valid/current” | Signed pass lifecycle and current Wallet/provider update state. |
| “This is the same Apple Account” | Sign in with Apple credential state and server verification/linking. |
| “This secret is protected locally” | Keychain configuration, access control, device lock/backup/migration tests, and redacted logs. |
| “The person authenticated locally” | LocalAuthentication policy result plus the protected operation; no unrelated identity claim. |
| “This request came from a legitimate app instance” | Server-validated App Attest assertion/DeviceCheck signal plus nonce/replay/risk policy. |

When a service, account, entitlement, device, or server is unavailable, preserve local/free functionality where possible. Never unlock premium or security-sensitive effects from a fallback flag that the stronger verification did not establish.

## Verification route

- StoreKit: local StoreKit configuration, product metadata, verified/unverified transactions, unfinished updates, restore, pending/cancelled, refunds/revocation/expiry, subscription grace, sandbox/TestFlight, server reconciliation, and release build.
- Apple Pay: merchant ID/capability/certificates, availability, supported networks, payment token handoff, provider decline/timeout, shipping/contact validation, sandbox physical device, and fulfillment.
- Wallet: pass signing/type IDs, add/display/update/revoke, pass privacy, supported device, stale pass, and real Wallet presentation.
- Sign in with Apple: first sign-in name/email, private relay, nonce/state, returning sign-in, credential state/revocation, account linking/deletion, Keychain storage, and server verification.
- Keychain/LocalAuthentication: lock/unlock, no passcode, biometric enrollment/change/lockout, fallback, access control, uninstall/reinstall, backup/restore, device migration, and keychain access groups.
- DeviceCheck/App Attest: supported/unsupported, development/production environment, key generation/attestation/assertion, one-time challenge/replay, server rejection, key loss, reinstall, and degraded-risk fallback.
- Networking: TLS/ATS, authentication, cancellation/retry/idempotency, malformed/expired responses, offline/cache, redaction, and server authorization.

Previews and local fixtures validate state rendering. They do not prove signed entitlements, App Store transactions, merchant processing, Wallet pass signing, Apple Account credential state, Secure Enclave behavior, App Attest server validation, or physical-device release configuration.

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [In-App Purchase](https://developer.apple.com/documentation/storekit/in-app-purchase)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [Transaction](https://developer.apple.com/documentation/storekit/transaction)
- [currentEntitlements](https://developer.apple.com/documentation/storekit/transaction/currententitlements)
- [PassKit](https://developer.apple.com/documentation/passkit)
- [Offering Apple Pay in your app](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app)
- [PKPaymentAuthorizationController](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontroller)
- [Wallet](https://developer.apple.com/documentation/passkit/wallet)
- [PKAddPassesViewController](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontroller)
- [Authentication Services](https://developer.apple.com/documentation/authenticationservices)
- [Implementing user authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [ASAuthorizationAppleIDProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidprovider)
- [ASAuthorizationAppleIDRequest](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidrequest)
- [Security](https://developer.apple.com/documentation/security)
- [Using the keychain to manage user secrets](https://developer.apple.com/documentation/security/using-the-keychain-to-manage-user-secrets)
- [SecItemAdd](https://developer.apple.com/documentation/security/secitemadd%28_%3A_%3A%29)
- [SecItemCopyMatching](https://developer.apple.com/documentation/security/secitemcopymatching%28_%3A_%3A%29)
- [Restricting keychain item accessibility](https://developer.apple.com/documentation/security/restricting-keychain-item-accessibility)
- [Adding a password to the keychain](https://developer.apple.com/documentation/security/adding-a-password-to-the-keychain)
- [Item attribute keys and values](https://developer.apple.com/documentation/security/item-attribute-keys-and-values)
- [Local Authentication](https://developer.apple.com/documentation/localauthentication)
- [LAContext](https://developer.apple.com/documentation/localauthentication/lacontext)
- [CryptoKit](https://developer.apple.com/documentation/cryptokit)
- [AES.GCM](https://developer.apple.com/documentation/cryptokit/aes/gcm)
- [Curve25519](https://developer.apple.com/documentation/cryptokit/curve25519)
- [DeviceCheck](https://developer.apple.com/documentation/devicecheck)
- [DCDevice](https://developer.apple.com/documentation/devicecheck/dcdevice)
- [DCAppAttestService](https://developer.apple.com/documentation/devicecheck/dcappattestservice)
- [Establishing your app’s integrity](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity)
- [Validating apps that connect to your server](https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server)
- [URL Loading System](https://developer.apple.com/documentation/foundation/url_loading_system)
- [Network](https://developer.apple.com/documentation/network)
- [URLRequest](https://developer.apple.com/documentation/foundation/urlrequest)
- [URLSession](https://developer.apple.com/documentation/foundation/urlsession)
