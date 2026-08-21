---
name: ios-commerce-identity-and-security
description: Route, implement, or review iOS commerce, identity, secrets, local authentication, cryptography, app-integrity, and secure-network features. Use when a feature sells digital goods, accepts Apple Pay, adds Wallet passes, signs users in, protects credentials, gates a local action, or needs server-verified integrity.
---

# iOS Commerce, Identity, and Security

Use this skill to keep purchase, payment, identity, secrets, device-user authentication, app-instance signals, transport security, server authorization, and product entitlement as separate trust boundaries.

`user intent -> system authorization/input -> local or server verification -> policy decision -> bounded side effect -> durable entitlement/audit state`

## Read before acting

- Inspect the actual Xcode targets, deployment target, product type, capabilities, entitlements, App Store Connect/merchant/service configuration, server contract, Keychain access groups, URL/transport layer, privacy copy, and existing entitlement/authentication adapters.
- Read the [commerce/identity/security route](../../../40-framework-routes/05-commerce-identity-and-security.md), [StoreKit and entitlements deep dive](../../../41-framework-deep-dives/02-storekit-and-entitlements.md), [networking/security/identity deep dive](../../../42-framework-deep-dives/03-networking-security-and-identity.md), and [commerce/identity/security recipes](../../../70-code-recipes/17-commerce-identity-and-security-recipes.md).
- Read the [data/device-services package](../ios-data-and-device-services/SKILL.md) when local persistence, CloudKit, account state, or protected personal data is involved. Refresh the exact official Apple pages in the Sources section before relying on an API, entitlement, region/device rule, or server-validation requirement.

## Route workflow

1. Classify the user outcome: digital content/subscription, physical goods/services payment, Wallet pass, Apple Account sign-in, secret/token storage, local device-user gate, app-instance abuse signal, or authenticated network request.
2. Choose the narrowest route. Use StoreKit for digital goods distributed through the App Store; PassKit/Apple Pay for supported physical payment; Wallet for signed passes; AuthenticationServices for Sign in with Apple; Security/Keychain for secrets; LocalAuthentication for a device-user policy; CryptoKit for an established protocol; DeviceCheck/App Attest as server inputs; URLSession/Network for transport.
3. Record the trust matrix before implementation: target, capability/entitlement, merchant/product/service IDs, server role, nonce/challenge, account state, Keychain accessibility/access control, data retention/deletion, supported device/region, and offline/manual fallback. Mark unknown setup as `to-verify`.
4. Model separate state machines. For StoreKit, separate product loading, purchase, pending, verified/unverified, entitlement, expiry, refund/revocation, restore, and transaction finishing. For identity, separate request, user cancellation, credential receipt, account linking, server verification, credential revocation, sign-out, and deletion. For secrets/auth, separate item availability, policy evaluation, lockout, fallback, migration, and deletion.
5. Draw the proof boundary: `system result -> local validation -> server verification when required -> product policy -> user-facing effect`. A framework callback, product ID, token, credential, biometric result, pass, or device signal is not automatically the policy decision.
6. Keep free/local functionality useful when a paid, account, server, biometric, or integrity service is unavailable unless the user outcome inherently requires that service. Never unlock premium/security-sensitive effects from a local flag that stronger verification did not establish.
7. Minimize sensitive data. Keep tokens/private keys out of source, logs, analytics, URLs, screenshots, UserDefaults, ordinary model fields, and error messages. Use Keychain configuration appropriate to the threat model and define deletion, migration, reinstall, backup, restore, and access-group behavior.
8. Verify with deterministic fixtures first, then signed sandbox/TestFlight/physical-device and server evidence. Record environment, Apple Account/merchant/product configuration, device, OS, transaction/credential state, server response, and remaining release gaps; do not generalize local StoreKit or simulator results to production.

## Framework boundaries

### StoreKit and PassKit

- StoreKit product metadata is not entitlement. Unlock digital content only from verified transaction/current-entitlement state, deliver the product before finishing the transaction, and handle updates while the app runs. Keep consumable, non-consumable, subscription, pending/Ask to Buy, refund/revocation, expiry/grace, restore, and account-change semantics explicit.
- StoreKit Testing and a local configuration are deterministic route fixtures. They do not prove App Store Connect metadata, sandbox/TestFlight account state, regional storefronts, server reconciliation, production pricing, or App Review configuration.
- Apple Pay authorizes a payment request and supplies a provider-bound token; a presented sheet or token is not provider capture, fulfillment, refund, or order success. Model provider/server processing separately and do not use Apple Pay for digital in-app content when StoreKit is the appropriate route.
- Wallet passes are signed artifacts with pass type IDs, add/update/revoke lifecycle, supported device/role rules, and privacy constraints. “Pass added” is not identity verification, payment authorization, or proof that the provider’s state is current.

### Sign in with Apple and account state

- Generate and validate nonce/state for the request, request only the scopes needed, preserve the stable Apple user identifier securely, and expect name/email availability to differ between first and subsequent authorization. Support private relay email, account linking, sign-out, credential revocation, deletion, and a returning-user path.
- Native authorization proves a system credential result for that flow. It does not grant access to app business data until the server verifies and authorizes the account. Keep Apple credential verification, session/token issuance, account ownership, organization membership, and product entitlement separate.
- Do not make Sign in with Apple mandatory for a local utility unless identity is part of the user outcome. A user identifier is not permission to access another account’s records.

### Keychain, LocalAuthentication, and CryptoKit

- Store small credentials, refresh tokens, private-key references, and stable local identifiers in Keychain. Choose item class, accessibility, synchronizability, access group, and `SecAccessControl` from the threat model; document what happens across lock, migration, backup/restore, reinstall, passcode changes, and key loss.
- LocalAuthentication evaluates a device-user policy or protected access-control operation. Success proves that policy evaluation succeeded at that moment; it is not server identity, account ownership, payment entitlement, or permission for an unrelated business action. Handle cancellation, lockout, no passcode, unavailable biometrics, enrollment changes, and fallback.
- Use CryptoKit’s established primitives and a documented protocol. Define key generation/storage/rotation, nonce/IV, associated data, algorithm/version, recovery, deletion, and server verification. Do not invent encryption, password hashing, token signing, or certificate-validation schemes.

### DeviceCheck, App Attest, and networking

- DeviceCheck and App Attest are server-managed abuse/integrity signals. Use one-time server challenges, bind assertions to request data, validate attestation/assertions server-side, prevent replay, handle unsupported/key-loss states, and feed results into a broader risk/authorization policy.
- Neither DeviceCheck nor App Attest is absolute device security, user identity, payment proof, or a replacement for server authorization. The app cannot authoritatively verify its own integrity.
- Centralize URLSession/Network request construction, TLS/ATS configuration, authentication, timeouts, cancellation, retries, idempotency, cache/offline policy, response validation, and redacted diagnostics. A client-side check or successful TLS connection is not server authorization.
- Never place secrets or personal data in query strings unless the protocol and privacy review explicitly require it. Validate response schema, expiry, signatures, and account scope before committing a server decision.

## Non-negotiable safety and evidence rules

- Never treat an unverified transaction, local “premium” flag, product ID, payment sheet/token, Wallet pass, Apple credential, biometric callback, Keychain item, DeviceCheck/App Attest signal, client-side certificate check, or successful HTTP response as sufficient entitlement, payment capture, identity, authorization, or absolute security proof.
- Keep local verification, server verification, and product policy visibly separate. State exactly which proof unlocks which effect and what happens when a service is unavailable or returns an ambiguous result.
- Do not store credentials, access tokens, private keys, payment data, health/personal data, or attestation material in logs, screenshots, analytics, source control, URLs, UserDefaults, or ordinary SwiftData fields.
- Do not add an account, payment route, backend, biometric prompt, tracking signal, or integrity telemetry beyond the stated user-facing need. Preserve supplied privacy scope and provide deletion/sign-out/account unlink behavior.
- Never claim production payment, entitlement, credential, app-integrity, hardware-security, or App Store readiness from previews, simulators, local fixtures, a successful compile, or a single sandbox run.

## Deliverable

Produce a compact route note or implementation change containing:

- selected framework and rejected alternatives;
- target, product/merchant/service IDs, capabilities, entitlements, account/server, Keychain, privacy, retention, region/device, and fallback matrix;
- purchase/credential/secret/integrity/network state machines with cancellation, retry, revocation, expiry, deletion, and stale-state behavior;
- exact local, server, signed sandbox/TestFlight, physical-device, App Store, privacy, signing, and release evidence plan;
- remaining `to-verify` gaps and claims deliberately not made.

For implementation, change only the requested target and directly related adapters/configuration. Do not add a server, account flow, payment capability, entitlement, secret, biometric prompt, integrity signal, analytics, or telemetry without a stated product need and authorization.

## Related routes and recipes

- [Commerce, identity, and security routes](../../../40-framework-routes/05-commerce-identity-and-security.md)
- [StoreKit and entitlements](../../../41-framework-deep-dives/02-storekit-and-entitlements.md)
- [Networking, security, and identity](../../../42-framework-deep-dives/03-networking-security-and-identity.md)
- [Commerce, identity, and security recipes](../../../70-code-recipes/17-commerce-identity-and-security-recipes.md)
- [Data and device services package](../ios-data-and-device-services/SKILL.md)
- [Permission, entitlement, and privacy checklist](../../../60-verification/04-permission-entitlement-and-privacy-checklist.md)
- [Build, device, and release checklist](../../../60-verification/01-build-device-and-release-checklist.md)

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
- [Security](https://developer.apple.com/documentation/security)
- [Keychain Services](https://developer.apple.com/documentation/security/keychain-services)
- [Using the keychain to manage user secrets](https://developer.apple.com/documentation/security/using-the-keychain-to-manage-user-secrets)
- [Restricting keychain item accessibility](https://developer.apple.com/documentation/security/restricting-keychain-item-accessibility)
- [Local Authentication](https://developer.apple.com/documentation/localauthentication)
- [LAContext](https://developer.apple.com/documentation/localauthentication/lacontext)
- [CryptoKit](https://developer.apple.com/documentation/cryptokit)
- [DeviceCheck](https://developer.apple.com/documentation/devicecheck)
- [DCDevice](https://developer.apple.com/documentation/devicecheck/dcdevice)
- [DCAppAttestService](https://developer.apple.com/documentation/devicecheck/dcappattestservice)
- [Establishing your app’s integrity](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity)
- [Validating apps that connect to your server](https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server)
- [URL Loading System](https://developer.apple.com/documentation/foundation/url_loading_system)
- [Network](https://developer.apple.com/documentation/network)
