# Authentication Services, passkeys, and Sign in with Apple

Authentication Services is the Apple-native boundary for credential requests and system authentication UI. It can coordinate passkeys stored in iCloud Keychain, physical security keys, Sign in with Apple, password credentials from iCloud Keychain, and web authentication sessions. It does not replace the relying party’s server, account model, session policy, or authorization rules.

The safe mental model is:

~~~text
app intent
-> server challenge or Apple authorization request
-> system credential UI and user verification
-> credential/assertion returned to the app
-> server or relying-party verification
-> app session
-> explicit authorization for domain actions
~~~

Face ID, Touch ID, a passkey sheet, a Sign in with Apple result, an identity token, a server session, and a local unlock are different facts. Keep them separate in code and in the UI.

## Route selector

| Desired outcome | Apple route | Required partner |
| --- | --- | --- |
| Passwordless account registration/sign-in | ASAuthorizationPlatformPublicKeyCredentialProvider | Relying-party server with WebAuthn challenge and public-key verification |
| Sign in with an Apple Account | ASAuthorizationAppleIDProvider or SwiftUI SignInWithAppleButton | App server and Sign in with Apple REST/token verification |
| Use a physical security key | ASAuthorizationSecurityKeyPublicKeyCredentialProvider | Relying-party server, physical NFC/USB/Lightning key, recovery plan |
| Offer existing iCloud Keychain credentials | ASAuthorizationPasswordProvider or AutoFill-assisted authorization | Credential configuration and account-linking policy |
| Authenticate through a web service | ASWebAuthenticationSession or SwiftUI WebAuthenticationSession | OAuth/OIDC provider, callback URL, state/nonce, redirect configuration |
| Derive an ephemeral local encryption key from a passkey | Passkey assertion PRF extension | Explicit user approval, CryptoKit use, and a recovery story |
| Store a small passkey-bound blob | Large Blob assertion extension | Passkey availability, size/operation limits, and migration/deletion policy |
| Serve passkeys from a browser app | Browser-specific Authentication Services APIs | Browser entitlement/access state and WebAuthn request routing |

Do not combine these routes merely because they all present a credential sheet. The relying party, credential type, server verification, recovery behavior, and user-facing copy differ.

## Passkey architecture

Apple’s passkey route uses public-key credentials. During registration, the authenticator creates a public/private key pair for the relying party. The private key remains with the authenticator, while the public key and credential metadata are sent to the relying-party server. During authentication, the server supplies a fresh challenge and verifies a signed assertion.

The app should model at least these values:

| Value | Owner | Meaning |
| --- | --- | --- |
| relying party identifier | App/server configuration | Domain that scopes the credential |
| challenge | Server | Fresh data proving the request is live and preventing replay |
| user ID | Server | Stable app account identifier associated with the credential |
| credential ID | Authenticator/server | Identifier for a registered credential |
| public key | Server | Key used to verify future assertions |
| private key | Authenticator | Secret key the app does not read or export |
| assertion/client data | Authentication Services | Evidence sent to the server for verification |
| app session | App/server | The product’s authenticated session after verification |

The app does not decide that a passkey is valid by checking that a system sheet completed. It forwards the credential result to the relying party, which verifies challenge, origin/relying-party binding, signature, counter or equivalent WebAuthn state, and the account policy appropriate to the service.

### Associated Domains are a trust boundary

Apple’s current passkey documentation requires an associated domain with the webcredentials service for registration and assertion requests. The target’s Associated Domains entitlement and the website’s apple-app-site-association file must agree.

Treat these as a deployment graph:

~~~text
bundle identifier + team
-> signed Associated Domains entitlement
-> public webcredentials domain
-> apple-app-site-association file
-> relying-party identifier
-> server WebAuthn configuration
-> physical/device authorization result
~~~

Every subdomain used for the service needs deliberate configuration. A local Xcode capability toggle does not prove that the installed app can retrieve or validate the domain association. The association file needs the correct service and App ID, public HTTPS delivery, and the target’s exact domain configuration.

### Registration

The registration flow is:

1. The user begins account creation or adds a passkey.
2. The app asks the server for a challenge, user ID, display name, and user name.
3. The app creates an ASAuthorizationPlatformPublicKeyCredentialProvider with the relying-party identifier.
4. The provider creates a registration request.
5. The app sends the request through ASAuthorizationController or SwiftUI AuthorizationController.
6. The system presents the credential-creation sheet.
7. The app receives the platform registration credential.
8. The app sends the credential and challenge context to the server.
9. The server validates and stores the public key.
10. The app shows the passkey as registered only after server acceptance.

Registration should not claim account creation from a local callback. The server needs to bind the new public key to the intended account and protect against replay, mismatched user IDs, and wrong relying-party domains.

### Assertion

The assertion flow is similar but uses a fresh server challenge:

1. The user requests sign-in.
2. The app asks the server for a challenge.
3. The app creates a platform provider and assertion request.
4. The app optionally includes allowed credential descriptors.
5. The system displays available credentials and user-verification UI.
6. The app receives an assertion credential.
7. The app forwards the assertion and request context to the server.
8. The server verifies the signature and challenge.
9. The server creates or resumes the app session.
10. The app renders authenticated content.

If there is no credential for the relying party, show a registration or recovery route. Do not silently create a second account from a missing assertion.

### AutoFill-assisted requests

Authentication Services can perform AutoFill-assisted requests. Set username fields with the appropriate text content type and request credentials when the person interacts with the login field. This is an opportunity to support passkeys alongside existing passwords without forcing a separate credential-picker design.

Keep password migration and passkey registration separate. A successful password AutoFill result is not a passkey assertion, and a passkey proposal does not prove the legacy password account should be merged.

## Physical security keys

The public-private key authentication collection also covers physical security keys using NFC, USB, and Lightning. This is useful for high-security accounts, but it introduces a loss and recovery problem:

- a physical key may be unavailable, lost, or stolen;
- a person may need more than one registered key;
- account recovery must not become an undocumented bypass;
- the UI should say which key is expected and what to do if it is unavailable;
- the proof matrix must include physical fixtures and a recovery test.

Security-key authentication still uses a relying-party challenge and server verification. The app should not treat the fact that an NFC key was present as sufficient identity proof.

## Sign in with Apple

Sign in with Apple is a separate provider route. The native app uses ASAuthorizationAppleIDProvider or SwiftUI SignInWithAppleButton. The request can ask for scopes such as full name and email. The system may provide those values during the initial authorization; the app should store them immediately if the product needs them because later responses may not repeat the full name.

The native result can contain:

- a team-scoped user identifier;
- an identity token;
- a single-use authorization code;
- the request state;
- the user’s authorized scopes;
- full name and email when supplied;
- real-user status and other current credential fields.

The user identifier—not the email address—is the stable account key for the developer team. A person may choose Hide My Email, so the email may be a private relay address. Treat the email as contact data, not as the identity primary key.

### Server verification

The app should send the identity token and authorization code to the app server over a protected channel. Apple’s current server guidance requires the server to verify the token signature and relevant claims, including:

- the JWS signature using Apple’s public key;
- the nonce associated with the authentication request;
- issuer equal to Apple’s issuer;
- audience equal to the developer’s client identifier;
- expiration and time validity;
- authorization-code exchange and refresh-token state where the product uses server sessions.

The app’s local completion callback is not server verification. Do not create a privileged local session until the server accepts the credential and returns the app’s own session state.

### Credential state and revocation

Persist the Apple user identifier in a protected local store such as Keychain, then use ASAuthorizationAppleIDProvider.getCredentialState to reconcile local state at launch or when the app needs it. The documented states include authorized, revoked, notFound, and transferred.

Credential state is a local Apple Account relationship signal. It does not replace server-side token/session verification. When an account is revoked, transfer state must be handled, or the server session is invalid, sign out or reauthenticate according to the product policy.

Account deletion is part of the authentication route. If a person deletes the app account, remove the app’s session and data according to the product policy and follow Apple’s token-revocation and server-notification requirements for Sign in with Apple.

## Web authentication sessions

ASWebAuthenticationSession and SwiftUI WebAuthenticationSession are for authenticating through a web service. The system presents a modal browser surface that names the domain and returns a callback URL when the provider redirects.

Keep this route separate from passkeys:

| Route | System proves | App/server still must prove |
| --- | --- | --- |
| ASWebAuthenticationSession | A browser-based authentication flow returned through the app’s callback | State, nonce, redirect, token, issuer, audience, and server session |
| Passkey assertion | The authenticator created a signed assertion for the relying party | Challenge, origin, credential, account, and server verification |
| Sign in with Apple | Apple authorization returned a credential/token/code | Token claims, nonce, server exchange, account mapping, and session |

Use ephemeral browser sessions when the product requires a session that does not share normal browser cookies and the current browser honors that request. Do not place access tokens in logs or trust arbitrary query parameters without validating the callback structure and state.

## Passkey PRF and Large Blob extensions

The current Authentication Services documentation includes WebAuthn extension routes that are useful for local-first apps, but they need careful boundaries.

### PRF-derived symmetric keys

The passkey PRF extension can derive one or two SymmetricKey values from a passkey assertion and salt inputs. Apple documents that the same input values with the same passkey produce the same key and that the keys can be used for application-specific encryption of user data.

This is a useful route for:

- unlocking an encrypted local record after a verified passkey assertion;
- deriving a stable per-passkey encryption key without storing the key itself;
- protecting a small local AI memory or private document layer that follows the passkey.

The key is not a replacement for account authorization or server verification. Apple’s documentation says not to store or export PRF output keys; derive them after assertion and discard them when the operation finishes. If the user loses every passkey, a recovery path is required because the app should not silently fall back to an unrelated key.

Use domain-separated salt inputs and version them. A change in salt or passkey changes the derived key; plan migrations before shipping a format that cannot be decrypted after a credential reset.

### Large Blob

The Large Blob assertion extension can read an existing passkey-bound blob or write a new blob, with one operation per assertion. It is a small credential-associated storage primitive, not a replacement for SwiftData, CloudKit, a server database, or a file provider.

Use it only when the product can explain:

- why the blob belongs to the passkey;
- how it is versioned and bounded;
- what happens when the passkey is replaced;
- how account deletion removes related data;
- what happens when the operation is unsupported or fails.

Do not put raw personal data or an unbounded model context in a credential-bound blob.

## Browser and credential-provider boundaries

WKWebView can use WebAuthn when the service’s relying-party identifier is configured as an associated domain. The app cannot use passkeys for arbitrary websites that are not configured for the app. Browser apps have a separate Authentication Services route for handling website WebAuthentication requests and asking the person for passkey access.

Credential provider extensions have their own process, entitlements, privacy, and user-consent boundaries. A normal app’s passkey flow does not prove an AutoFill credential provider works in Safari or another app. Treat extension packaging and host invocation as separate evidence.

## Native design and Liquid Glass

Authentication is a high-trust moment. Use the system control and system sheet:

- SignInWithAppleButton for Sign in with Apple;
- Authentication Services presentation for passkey and security-key requests;
- ASWebAuthenticationSession or WebAuthenticationSession for browser authentication;
- standard SwiftUI forms and controls around the identity task;
- Keychain and server state for the resulting session.

Do not draw a fake Apple logo button, fake passkey sheet, or fake Face ID confirmation. A custom Liquid Glass card can explain why sign-in is needed, show the benefit, or display current account state, but it should not imitate the system authorization surface.

Apple’s HIG recommends delaying account creation until the product has provided value, explaining why a sign-in is needed, and making account deletion discoverable. For a private/local-first app, prefer keeping the core workflow account-free until sync, collaboration, or a server authorization truly requires identity.

Use Liquid Glass sparingly for:

- a single primary identity action;
- a compact account-state toolbar;
- a review card before linking a passkey or account;
- a recovery/action sheet.

Keep credential values, identity tokens, email relay addresses, PRF-derived keys, and server errors out of decorative surfaces and normal logs. Test large text, VoiceOver, reduced transparency, reduced motion, and the system appearance settings.

## On-device AI boundaries

AI can help explain the current authentication state or draft account-recovery guidance from approved, non-secret facts. It cannot:

- choose or invent a credential;
- see a private key;
- decide that a signature is valid;
- replace the server’s relying-party verification;
- infer an account from an email address when a stable user identifier is available;
- bypass a user confirmation or system sheet;
- generate or modify a WebAuthn challenge;
- store a PRF key or identity token in a model context;
- merge two accounts without deterministic account-linking proof.

For a local-first encrypted notebook, a safe composition is:

~~~text
user starts unlock
-> passkey assertion and system verification
-> server/local policy validation
-> derive PRF key for this operation
-> decrypt the minimum local data
-> optional on-device AI use
-> discard the derived key
~~~

The model sees the decrypted projection only if the user and product policy allow it. Authentication is not evidence that the model may read every private record.

## Availability and evidence vocabulary

| Claim | Exact proof |
| --- | --- |
| Passkey API compiles | Named target build with selected SDK |
| Passkey sheet appears | Signed physical device with an associated domain and a server challenge |
| Registration succeeds | Credential returned and relying-party server accepts/stores public key |
| Assertion succeeds | Server verifies challenge, relying-party binding, signature, and account |
| Sign in with Apple works | Real Apple Account/device flow plus server token verification |
| Credential state is reconciled | Named user identifier, credential-state result, and local/session action |
| PRF unlock works | Supported passkey assertion, derived key used, decryption succeeded, key discarded |
| Security key works | Physical NFC/USB/Lightning fixture and server assertion verification |
| Browser auth works | ASWebAuthenticationSession modal, callback, state/nonce, provider/server proof |
| Account deletion works | In-app deletion, server cleanup, Apple revocation/notification handling |
| Release works | Signed archive/TestFlight configuration and public associated-domain files |

Simulator layouts and preview state reducers are useful for UI. They do not prove iCloud Keychain sync, physical security keys, real Apple Account state, public AASA delivery, server verification, or release entitlements.

## Sources

- [Authentication Services](https://developer.apple.com/documentation/authenticationservices)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [AuthorizationController](https://developer.apple.com/documentation/authenticationservices/authorizationcontroller)
- [ASAuthorizationAppleIDProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidprovider)
- [ASAuthorizationAppleIDCredential](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidcredential)
- [Implementing User Authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [Displaying Sign in with Apple buttons in your app](https://developer.apple.com/documentation/signinwithapple/displaying-sign-in-with-apple-buttons-in-your-app)
- [SignInWithAppleButton](https://developer.apple.com/documentation/authenticationservices/signinwithapplebutton)
- [Configuring Sign in with Apple support](https://developer.apple.com/documentation/xcode/configuring-sign-in-with-apple)
- [Sign in with Apple](https://developer.apple.com/documentation/signinwithapple)
- [Authenticating users with Sign in with Apple](https://developer.apple.com/documentation/signinwithapple/authenticating-users-with-sign-in-with-apple)
- [Receiving a User’s Identity Token](https://developer.apple.com/documentation/signinwithapple/receiving-a-users-identity-token)
- [Verifying a user](https://developer.apple.com/documentation/signinwithapple/verifying-a-user)
- [Processing changes for Sign in with Apple accounts](https://developer.apple.com/documentation/signinwithapple/processing-changes-for-sign-in-with-apple-accounts)
- [Sign in with Apple REST API](https://developer.apple.com/documentation/signinwithapplerestapi)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [Connecting to a service with passkeys](https://developer.apple.com/documentation/authenticationservices/connecting-to-a-service-with-passkeys)
- [Public-Private Key Authentication](https://developer.apple.com/documentation/authenticationservices/public-private-key-authentication)
- [ASAuthorizationPlatformPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialprovider)
- [ASAuthorizationPlatformPublicKeyCredentialRegistrationRequest](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialregistrationrequest)
- [ASAuthorizationPlatformPublicKeyCredentialAssertionRequest](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialassertionrequest)
- [ASAuthorizationPlatformPublicKeyCredentialAssertion](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialassertion)
- [Supporting Security Key Authentication Using Physical Keys](https://developer.apple.com/documentation/authenticationservices/supporting-security-key-authentication-using-physical-keys)
- [ASAuthorizationSecurityKeyPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationsecuritykeypublickeycredentialprovider)
- [ASAuthorizationPublicKeyCredentialPRFAssertionInput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentialprfassertioninput-swift.struct)
- [ASAuthorizationPublicKeyCredentialPRFAssertionOutput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentialprfassertionoutput-swift.struct)
- [ASAuthorizationPublicKeyCredentialLargeBlobAssertionInput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentiallargeblobassertioninput-swift.struct)
- [ASAuthorizationPublicKeyCredentialLargeBlobAssertionOutput](https://developer.apple.com/documentation/authenticationservices/asauthorizationpublickeycredentiallargeblobassertionoutput-swift.struct)
- [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession)
- [WebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/webauthenticationsession)
- [Passkey use in web browsers](https://developer.apple.com/documentation/authenticationservices/passkey-use-in-web-browsers)
- [Authenticating people by using passkeys in browser apps](https://developer.apple.com/documentation/authenticationservices/authenticating-people-by-using-passkeys-in-browser-apps)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Sign in with Apple Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.applesignin)
- [Managing accounts](https://developer.apple.com/design/human-interface-guidelines/managing-accounts)
- [Sign in with Apple](https://developer.apple.com/design/human-interface-guidelines/sign-in-with-apple)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
