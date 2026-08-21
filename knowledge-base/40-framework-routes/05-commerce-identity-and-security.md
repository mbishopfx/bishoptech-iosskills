# Commerce, Identity, and Security

## Choose the trust boundary before the API

| User outcome | Native route | What must be verified |
| --- | --- | --- |
| Sell digital content or subscriptions | StoreKit 2 | App Store product configuration, signed transaction verification, entitlement state, restore/refund/expiry, and target release metadata. |
| Accept payment for physical goods/services | PassKit Apple Pay | Merchant ID/capability, payment request, payment token handoff, provider/server processing, supported network/device, and sandbox/production setup. |
| Add a ticket, loyalty card, or pass | PassKit Wallet | Signed pass, pass type ID/capability, add/update lifecycle, user authorization, and real Wallet presentation. |
| Sign in with an Apple Account | AuthenticationServices | Nonce/state, credential lifecycle, server token verification/linking, private relay email, sign-out, and revocation. |
| Store a token/private key | Keychain/Security | Accessibility/access control, device migration/sync choice, update/delete behavior, and no plaintext logging. |
| Gate a local action | LocalAuthentication + Keychain access control | Device-user presence, fallback/lockout, protected-item policy, and no claim of server identity. |
| Reduce abuse or assert app-instance integrity | DeviceCheck/App Attest | Server challenge/verification, key lifecycle, unsupported devices, replay defense, and risk-policy fallback. |

Do not let a local Boolean, a UI sheet, an identity callback, a device token, or a successful API call stand in for the server/account/entitlement/security assertion the product actually needs.

## Commerce

Use StoreKit 2 for digital goods and subscriptions in new iOS 26 work. Keep product loading, purchase, transaction updates, verification, entitlement calculation, restore, refunds, pending/ask-to-buy, and expired access as explicit states. Unlock content only from verified transaction/entitlement state, finish a transaction after the product has delivered the entitlement, and isolate entitlement logic from the feature so free/local workflows remain readable when a purchase is unavailable or expired.

StoreKit Testing and a local StoreKit configuration are useful for deterministic product/transaction fixtures. They do not prove App Store Connect metadata, sandbox/TestFlight account behavior, server reconciliation, regional availability, or a production review/release configuration. If a backend gates premium access, establish a server-side transaction/subscription validation boundary rather than trusting an app-supplied product ID or flag.

For physical goods or services, check the payment route and App Review rules instead of assuming StoreKit is appropriate. For Apple Pay, use PassKit and the merchant configuration documented for the product.

## Identity

AuthenticationServices supports Sign in with Apple and related system authentication features. Model request nonce/state, account linking, the stable Apple user identifier, first-name/email availability on first authorization, private relay email, credential revocation, sign-out, and server verification. Do not make an account mandatory for a local utility unless identity is part of the user outcome.

## Local protection

- LocalAuthentication: gate access using a system policy such as biometrics/passcode; handle fallback and lockout.
- Security/Keychain: store secrets and credentials, with access controls and migration/deletion behavior.
- CryptoKit: use established cryptographic primitives and protocols; do not invent a custom encryption scheme.
- Data Protection: choose file protection for sensitive local files and verify behavior while locked.

## App/device integrity

DeviceCheck and App Attest can support abuse/fraud decisions that involve a server. App Attest uses a device-generated key, an Apple attestation flow, server challenges, and assertions over request data; DeviceCheck provides an authenticated device token and server-managed bits. Neither is a replacement for authorization, authentication, secure transport, or a complete security model. Define what the server verifies, how replay is prevented, how keys rotate/recover, and what the app can do when the service is unsupported or unavailable.

## Entitlements and privacy

Security and commerce APIs may require capabilities, entitlements, merchant IDs, associated domains, or privacy descriptions. Record them as part of the feature brief and verify the built app’s entitlements rather than relying on a source-file search.

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [Choosing a StoreKit API for In-App Purchases](https://developer.apple.com/documentation/storekit/choosing-a-storekit-api-for-in-app-purchases)
- [In-App Purchase](https://developer.apple.com/documentation/storekit/in-app-purchase)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [Transaction](https://developer.apple.com/documentation/storekit/transaction)
- [currentEntitlements](https://developer.apple.com/documentation/storekit/transaction/currententitlements)
- [PassKit](https://developer.apple.com/documentation/passkit)
- [Offering Apple Pay in your app](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app)
- [PKPaymentAuthorizationController](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontroller)
- [Wallet](https://developer.apple.com/documentation/passkit/wallet)
- [PKAddPassesViewController](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontroller)
- [AuthenticationServices](https://developer.apple.com/documentation/authenticationservices)
- [Implementing user authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [LocalAuthentication](https://developer.apple.com/documentation/localauthentication)
- [LAContext](https://developer.apple.com/documentation/localauthentication/lacontext)
- [Security](https://developer.apple.com/documentation/security)
- [Using the keychain to manage user secrets](https://developer.apple.com/documentation/security/using-the-keychain-to-manage-user-secrets)
- [Restricting keychain item accessibility](https://developer.apple.com/documentation/security/restricting-keychain-item-accessibility)
- [CryptoKit](https://developer.apple.com/documentation/cryptokit)
- [DeviceCheck](https://developer.apple.com/documentation/devicecheck)
- [DCDevice](https://developer.apple.com/documentation/devicecheck/dcdevice)
- [DCAppAttestService](https://developer.apple.com/documentation/devicecheck/dcappattestservice)
- [Establishing your app’s integrity](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity)
- [Validating apps that connect to your server](https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server)
