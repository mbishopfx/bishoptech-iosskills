# Authentication Services and passkey capability route

Use this route when an iOS or iPadOS app needs passwordless account access, Sign in with Apple, a physical security key, a browser authentication handoff, or a passkey-backed local unlock. Start with the [Authentication Services deep dive](../42-framework-deep-dives/35-authentication-services-passkeys-and-apple-sign-in.md), the [account authentication design guide](../21-design-deep-dives/55-account-authentication-and-passkey-review-design.md), the [proof matrix](../60-verification/52-authentication-services-passkey-proof-matrix.md), and the [code recipes](../70-code-recipes/70-authentication-services-passkey-recipes.md).

## Route selector

| Product needs to… | Choose | Partner boundary |
| --- | --- | --- |
| Register or use a platform passkey | ASAuthorizationPlatformPublicKeyCredentialProvider | Server challenge, WebAuthn verifier, public-key credential store |
| Let a person use Apple Account identity | ASAuthorizationAppleIDProvider or SignInWithAppleButton | Sign in with Apple server verification, account policy, deletion/revocation |
| Use an NFC, USB, or Lightning security key | ASAuthorizationSecurityKeyPublicKeyCredentialProvider | Physical key fixture, relying-party verifier, recovery |
| Reuse an existing password credential | ASAuthorizationPasswordProvider or the supported AutoFill route | Credential configuration and account-linking policy |
| Use an external OAuth/OIDC website | ASWebAuthenticationSession or WebAuthenticationSession | Provider redirect, state/nonce, callback, server token exchange |
| Derive a local key from a passkey | PRF assertion extension | CryptoKit envelope design, recovery, in-memory key lifetime |
| Store a small authenticator-bound value | Large Blob assertion extension | Size, version, deletion, and unsupported-extension behavior |

Choose one named route per user action. “Sign in” and “Unlock local data” may use the same passkey but are not the same operation or proof.

## Target setup checklist

1. Select the minimum OS and device family for the exact Authentication Services APIs.
2. Add only the target capabilities needed by the selected route.
3. Configure Associated Domains when the passkey route requires webcredentials trust.
4. Publish and validate the production apple-app-site-association file.
5. Add Sign in with Apple capability and entitlement when that provider is offered.
6. Configure privacy text and account-deletion behavior before collecting identity data.
7. Keep provider-specific server keys, redirect configuration, and client identifiers out of the app bundle when they are server secrets.
8. Record the relying-party identifier, Apple client identifier, bundle identifier, team identifier, callback scheme, and environment in a release worksheet.
9. Add a manual or recovery route before requiring a credential.
10. Test the signed artifact, not only an unsigned source configuration.

### Configuration worksheet

| Field | Decision |
| --- | --- |
| App target |  |
| Deployment target |  |
| SDK/Xcode |  |
| Route | platform passkey / Apple / security key / web / PRF / Large Blob |
| Relying-party identifier |  |
| Associated domains |  |
| AASA deployment URL |  |
| Apple client identifier |  |
| Sign in with Apple scopes |  |
| Callback scheme |  |
| Server challenge endpoint |  |
| Verification endpoint |  |
| Account deletion endpoint |  |
| Recovery route |  |
| Physical fixtures |  |
| Signed artifact |  |

## Recommended architecture

Keep system authorization, provider adaptation, server verification, and app session state separate:

~~~text
AuthView
  -> AuthViewModel
     -> AuthOperationCoordinator
        -> Authentication Services request/controller
           -> ProviderCredentialAdapter
              -> server transport
                 -> deterministic verifier response
                    -> SessionStore
                       -> authorized app route
~~~

The view should render state. The coordinator should own the controller and operation identifier. The transport should send the minimum required provider result. The server should own signature and account verification. The session store should receive an authenticated session only after verification succeeds.

## Platform passkey route

### Registration

1. Ask the server for a fresh challenge and a stable app user ID.
2. Create ASAuthorizationPlatformPublicKeyCredentialProvider with the exact relying-party identifier.
3. Create a registration request with the challenge, user ID, user name, and display name.
4. Present the request through ASAuthorizationController or the SwiftUI authorization surface.
5. Send the returned credential result to the server without logging private material.
6. Verify the registration on the server and store the public credential.
7. Show the passkey as registered only after the server response succeeds.

Use a deliberate moment for registration: account creation, completion of a useful task, or a settings action. Do not display a credential sheet before explaining the value.

### Assertion

1. Ask the server for a fresh challenge.
2. Create an assertion request scoped to the same relying-party identifier.
3. Present the system authorization surface.
4. Send authenticator data and signature fields to the server.
5. Wait for server verification and account/session policy.
6. Update the app state only after a verified session or an explicitly scoped local unlock result.

Never reuse a challenge after a cancellation, never accept an assertion for a different environment, and never use a model to interpret cryptographic validity.

## Sign in with Apple route

Use Apple’s official SignInWithAppleButton for a SwiftUI sign-in action or coordinate an ASAuthorizationAppleIDProvider request when the flow needs a custom operation model.

Request only the needed scopes. When the credential returns:

1. Send the authorization code and identity token to the server.
2. Verify the identity token signature and claims against Apple’s issuer and key set.
3. Check nonce, audience/client identifier, expiry, and stable user identifier.
4. Exchange the authorization code on the server when required.
5. Create or link the account using the stable Apple user identifier.
6. Store the initial name/email values only according to the product privacy policy.
7. Handle Hide My Email relay addresses as contact routes, not primary account keys.

The local credential state query is useful for prompting refresh or recovery. It is not the full account lifecycle. Plan for revoked, transferred, not-found, and deleted states.

## Security-key route

Make the hardware route explicit:

~~~text
Use a security key
-> explain NFC, USB, or Lightning expectation
-> create provider-specific registration/assertion request
-> system handles key interaction
-> send public-key result to relying party
-> show verified outcome or recovery
~~~

Support only the transports and key policies the target and server actually test. A physical key may be unavailable, already registered, canceled, or rejected by the relying party. Each condition needs a human-readable fallback.

## Browser authentication route

Use ASWebAuthenticationSession or WebAuthenticationSession when the provider’s authorization is web-based:

1. Generate state and nonce using a trusted app/server boundary.
2. Open the exact provider authorization URL.
3. Show the system domain context to the person.
4. Validate the callback scheme and state.
5. Send the one-time code to the server for token exchange.
6. End the session and remove sensitive callback values from logs.
7. Treat cancellation as a normal route back to the app.

An app callback is not a token verification result. The server must validate the provider response and account policy.

## PRF-backed local unlock

Use PRF only when the product can explain the local-first recovery tradeoff. A safe capability contract is:

| Contract | Rule |
| --- | --- |
| Input | Versioned salt policy with no secret embedded in user-facing copy |
| Trigger | Explicit unlock or key-rotation action |
| Output | In-memory key material passed directly to a CryptoKit operation |
| Storage | Store encrypted app data or a wrapped key, not raw PRF output |
| Failure | Unsupported extension, canceled assertion, missing passkey, or invalid ciphertext |
| Recovery | User-visible export/recovery/alternate key plan defined before launch |
| Deletion | Remove local ciphertext and derived-key references when the account is deleted |

Discard the derived key when the operation is complete. Do not send it to a server or let on-device AI inspect it.

## Large Blob route

Use a Large Blob only for a small, versioned authenticator-associated value. Define a schema before enabling it:

~~~text
version
checksum
purpose
wrapped-value or compact metadata
created-at
~~~

The app must handle unsupported read/write, size limits, failed write, credential replacement, migration, and deletion. Do not use the credential-associated blob for a user database, analytics queue, access token, or recovery secret that has no alternate path.

## SwiftUI and Liquid Glass

System authorization surfaces own their presentation, materials, controls, and accessibility behavior. The app-owned shell can use Liquid Glass for hierarchy around the action:

- place the primary sign-in or passkey action in a clear toolbar or prominent control;
- keep glass subordinate to the identity explanation and provider label;
- use the official Sign in with Apple control where Apple requires it;
- do not blur or recolor the system credential sheet;
- avoid stacking translucent cards around a single system action;
- preserve contrast, reduced transparency, Dynamic Type, and VoiceOver order;
- make recovery and deletion visible in the same account context.

Liquid Glass is a composition material, not an identity guarantee. A glossy local button must never look like evidence that server verification completed.

## AI-assisted account state

Safe local proposals include:

- plain-language explanation of a revoked or missing credential;
- a checklist for a known configuration failure;
- a summarized account recovery choice;
- a local label for a provider state.

Keep these deterministic:

- challenge generation;
- signature, token, nonce, audience, and issuer validation;
- relying-party and callback selection;
- account linking and deletion;
- session issuance;
- key derivation and secret retention.

Pass only typed, redacted state to the model. The model may explain a state; it may not grant a privilege.

## Failure and fallback matrix

| Failure | User-facing meaning | Fallback |
| --- | --- | --- |
| No passkey available | No credential is available on this device/account | Offer security key, Apple, or recovery |
| Associated domain unavailable | The app cannot establish the configured webcredentials trust | Explain setup issue; keep a tested recovery path |
| Authorization canceled | The system flow ended without a credential result | Return quietly; preserve the intended action |
| Provider unavailable | The selected authenticator cannot be used here | Offer only configured alternatives |
| Server challenge expired | The request is no longer valid | Request a new challenge |
| Signature/token rejected | The relying party could not verify the result | Do not grant access; show recovery |
| Apple credential transferred | Account identity needs migration | Follow the server transfer policy |
| Apple credential revoked | Provider authorization ended | Reauthorize or end the affected session |
| Security key not detected | Hardware is absent or moved away | Explain transport and retry |
| PRF unsupported | This authenticator cannot derive the requested key | Use alternate local unlock/recovery |
| Large Blob unsupported/failed | Authenticator storage is unavailable | Continue without the optional extension |
| Account deleted | The product must remove or disable associated data | Confirm deletion and offer no silent reactivation |

## Route completion checklist

- [ ] The named provider and user action are documented.
- [ ] The target entitlements match the route.
- [ ] Associated Domains and AASA are deployed and tested where required.
- [ ] The server challenge and verification contract is written.
- [ ] Server-side negative tests cover replay, wrong audience, wrong relying party, bad signature, expired token, and wrong account.
- [ ] Cancellation, unavailable provider, and recovery states are designed.
- [ ] Passkey, Apple Account, and physical-key flows are tested on physical hardware.
- [ ] PRF/Large Blob are optional branches with migration and deletion behavior.
- [ ] AI is constrained to explanation/classification and cannot authorize.
- [ ] Liquid Glass is limited to app-owned surfaces.
- [ ] Accessibility, localization, privacy, and account deletion are tested.
- [ ] The signed archive contains the exact entitlements and privacy configuration.

## Sources

- [Authentication Services](https://developer.apple.com/documentation/authenticationservices)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [AuthorizationController](https://developer.apple.com/documentation/authenticationservices/authorizationcontroller)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [Connecting to a service with passkeys](https://developer.apple.com/documentation/authenticationservices/connecting-to-a-service-with-passkeys)
- [Public-Private Key Authentication](https://developer.apple.com/documentation/authenticationservices/public-private-key-authentication)
- [ASAuthorizationPlatformPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialprovider)
- [ASAuthorizationPlatformPublicKeyCredentialRegistrationRequest](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialregistrationrequest)
- [ASAuthorizationPlatformPublicKeyCredentialAssertionRequest](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialassertionrequest)
- [Supporting Security Key Authentication Using Physical Keys](https://developer.apple.com/documentation/authenticationservices/supporting-security-key-authentication-using-physical-keys)
- [ASAuthorizationSecurityKeyPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationsecuritykeypublickeycredentialprovider)
- [Implementing User Authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [Displaying Sign in with Apple buttons in your app](https://developer.apple.com/documentation/signinwithapple/displaying-sign-in-with-apple-buttons-in-your-app)
- [SignInWithAppleButton](https://developer.apple.com/documentation/authenticationservices/signinwithapplebutton)
- [Receiving a User’s Identity Token](https://developer.apple.com/documentation/signinwithapple/receiving-a-users-identity-token)
- [Verifying a user](https://developer.apple.com/documentation/signinwithapple/verifying-a-user)
- [Processing changes for Sign in with Apple accounts](https://developer.apple.com/documentation/signinwithapple/processing-changes-for-sign-in-with-apple-accounts)
- [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession)
- [WebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/webauthenticationsession)
- [ASAuthorizationPublicKeyCredentialPRFAssertionInput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentialprfassertioninput-swift.struct)
- [ASAuthorizationPublicKeyCredentialPRFAssertionOutput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentialprfassertionoutput-swift.struct)
- [ASAuthorizationPublicKeyCredentialLargeBlobAssertionInput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentiallargeblobassertioninput-swift.struct)
- [ASAuthorizationPublicKeyCredentialLargeBlobAssertionOutput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentiallargeblobassertionoutput-swift.struct)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Sign in with Apple Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.applesignin)
- [Managing accounts](https://developer.apple.com/design/human-interface-guidelines/managing-accounts)
- [Sign in with Apple](https://developer.apple.com/design/human-interface-guidelines/sign-in-with-apple)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
