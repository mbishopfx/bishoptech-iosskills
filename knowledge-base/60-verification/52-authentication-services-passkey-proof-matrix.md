# Authentication Services and passkey proof matrix

Authentication Services crosses system-owned UI, secure authenticators, associated-domain delivery, app transport, a relying-party/server verifier, account lifecycle, and optional local cryptography. Prove each boundary separately. A system sheet or local callback is never proof of an authenticated app session.

Use this matrix with the [Authentication Services deep dive](../42-framework-deep-dives/35-authentication-services-passkeys-and-apple-sign-in.md), the [capability route](../50-capability-recipes/58-authentication-services-passkey-route.md), the [account design guide](../21-design-deep-dives/55-account-authentication-and-passkey-review-design.md), and the [code recipes](../70-code-recipes/70-authentication-services-passkey-recipes.md).

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| The selected API is available for the target | Current Apple API page, deployment target, and a target compile | A copied snippet or an autocomplete result |
| Passkey registration is configured | Signed Associated Domains entitlement, deployed webcredentials AASA, server relying-party configuration, physical registration | A local capability checkbox |
| Passkey registration succeeded | Real authenticator sheet, redacted credential result, server verification, and public-key storage | The sheet dismissed without error |
| Passkey assertion succeeded | Fresh server challenge, physical assertion, server signature/origin/rp ID verification, and session response | A non-empty assertion object |
| The correct account was signed in | Server account binding and authorization policy | Credential ID or user handle alone |
| Sign in with Apple succeeded | Physical Apple Account authorization, identity-token signature/claim verification, authorization-code handling, and account policy | A local Apple user identifier |
| Sign in with Apple profile is complete | First-use scope evidence and stored profile policy | A later credential with missing name/email |
| Apple credential state is current | Provider state plus server session/account state and notification/revocation handling | A single getCredentialState result |
| Security-key support works | Real NFC/USB/Lightning fixture, provider result, relying-party verification, and recovery test | A configured security-key provider |
| Web authentication works | Real provider session, domain presentation, state/nonce validation, callback, server exchange, and cancellation | A callback URL |
| PRF local unlock works | Supported physical authenticator, assertion with versioned salts, derived-key operation, discard test, and recovery path | PRF output bytes in a log |
| Large Blob support works | Supported authenticator, read/write result, schema/version check, migration, deletion, and unsupported branch | A successful request construction |
| The app is accessible | VoiceOver, Voice Control, Switch Control, Dynamic Type, reduced motion/transparency, localization, and recovery task runs | Labels visible in source |
| The route is release-ready | Signed archive, exact entitlements, real domains, server configuration, privacy/deletion review, and physical-device test report | Debug build or simulator success |

## Evidence vocabulary

Use precise words in test reports:

| Word | Meaning |
| --- | --- |
| configured | The source or signed artifact contains the intended declaration |
| presented | The system-owned or app-owned UI appeared |
| returned | Authentication Services delivered a provider result or error |
| transported | The app sent the intended redacted fields to the intended endpoint |
| verified | The relying party deterministically validated the response |
| authorized | The product policy granted a defined capability |
| unlocked | A local operation used an approved key and completed |
| released | The signed distribution artifact and external configuration were tested |

Do not use “authenticated” for a credential sheet result when the server has not verified it.

## Test environment record

| Field | Value |
| --- | --- |
| App target |  |
| Version/build |  |
| SDK/Xcode |  |
| Deployment target |  |
| Device model/OS |  |
| Apple Account state |  |
| iCloud Keychain/passkey state |  |
| Security-key fixture/transport |  |
| Relying-party identifier |  |
| AASA URL and response hash |  |
| Signed entitlements hash |  |
| Apple client identifier/environment |  |
| Server verifier revision |  |
| Challenge ID/revision |  |
| Test account |  |
| Recovery fixture |  |

Never place raw identity tokens, authorization codes, signatures, private key material, PRF output, access tokens, or full callback URLs in a normal test report.

## Passkey registration matrix

| Test | Expected evidence | Failure boundary |
| --- | --- | --- |
| Fresh account registration | Server challenge, system registration, credential result, verified public-key storage | App/server mismatch |
| Registration canceled | Cancellation state; no credential stored; UI returns safely | Cancellation handling |
| Wrong relying-party identifier | Request rejected or server refuses result; no account mutation | Domain/configuration |
| Missing AASA/webcredentials | Association failure is visible; recovery remains available | External deployment |
| Duplicate credential | Server policy explains existing credential; no accidental duplicate account | Account policy |
| Invalid challenge | Server rejects replayed, expired, or wrong-account challenge | Cryptographic verifier |
| Invalid attestation/result | Server rejects malformed or disallowed registration | Verifier policy |
| Display-name change | Stored display name follows explicit profile policy | Data lifecycle |
| Device restart/locked state | Supported behavior is documented and tested | Authenticator availability |
| Delete credential/account | Credential/account deletion path and local cleanup are proven | Recovery/deletion |

## Passkey assertion matrix

| Test | Expected evidence | Failure boundary |
| --- | --- | --- |
| Returning person with passkey | Fresh challenge, physical assertion, verified server session | Full chain |
| Wrong account or credential | Server refuses account binding | Authorization policy |
| Replayed assertion | Reused challenge or assertion is rejected | Replay defense |
| Wrong rp ID/origin | Server rejects mismatched domain | Relying-party configuration |
| Bad signature | Server rejects without creating a session | Cryptographic verification |
| Expired challenge | Server returns a recoverable retry state | Challenge lifecycle |
| User cancels | No session; no alarming error; retry remains possible | UX/cancellation |
| No credential | Clear alternative or recovery | Provider availability |
| Server unavailable | No false signed-in state; safe retry | Transport/session |
| Late callback after a new operation | Old operation cannot overwrite current state | Lifetime/concurrency |

## Sign in with Apple matrix

| Test | Expected evidence | Failure boundary |
| --- | --- | --- |
| First authorization | Official button, requested scopes, identity token, authorization code, server verification | Apple provider/server |
| Returning authorization | Stable user identifier maps to existing account | Account binding |
| Hide My Email | Relay address is stored and explained under privacy policy | Profile handling |
| Name omitted later | Existing name is preserved; missing scope is not treated as deletion | Profile lifecycle |
| Invalid issuer | Token rejected | Token verifier |
| Invalid audience/client ID | Token rejected | Environment/configuration |
| Invalid nonce | Token rejected | Replay/CSRF defense |
| Expired token | Token rejected or refreshed through server policy | Token lifecycle |
| Revoked credential | Server/session policy ends or reauthorizes access | Revocation |
| Transferred credential | Transfer migration path is exercised | Account migration |
| Account deletion | Apple-side and app-side deletion policy is executed | Deletion compliance |
| Server notification | Signed notification is verified and account state changes | External lifecycle |

The Apple identity token is evidence for a verifier. It is not a UI state variable that the app can trust solely because it is present.

## Security-key matrix

| Fixture | Test | Expected evidence |
| --- | --- | --- |
| NFC key | Registration | Physical key prompt, provider result, server public-key storage |
| NFC key | Assertion | Key interaction, signature, server verification |
| USB key | Registration/assertion | Same proof with USB transport |
| Lightning key | Registration/assertion | Same proof with Lightning transport where supported |
| Unsupported key | Attempt auth | Clear unsupported/recovery path; no infinite retry |
| Key removed | Mid-operation removal | Cancellation/error and no partial session |
| Key already registered | Duplicate registration | Account policy and safe explanation |
| Lost key | Recovery | Alternate credential/recovery path works |

Do not generalize from one security-key model to every key, firmware, transport, or policy.

## Browser authentication matrix

| Test | Expected evidence |
| --- | --- |
| Correct provider domain | System session names the intended domain |
| Valid state/nonce | Callback is accepted and server exchange succeeds |
| Wrong state | Callback rejected without session |
| Wrong callback scheme | Callback ignored/rejected safely |
| User cancels | Session ends without error escalation |
| Provider returns an error | App shows provider-safe recovery |
| One-time code reused | Server rejects replay |
| Ephemeral mode | Product privacy behavior is documented and tested |
| Provider account differs | Account-linking policy is explicit |

## Associated-domain evidence

Capture a redacted deployment record:

~~~yaml
bundle_id: ""
team_id: ""
signed_associated_domains:
  - "webcredentials:example.com"
aasa_url: "https://example.com/.well-known/apple-app-site-association"
aasa_http_status: 200
aasa_content_hash: ""
aasa_service: "webcredentials"
app_id_entry_present: true
relying_party_id: ""
server_configuration_revision: ""
physical_device: ""
result: ""
~~~

The HTTP response and signed entitlement are separate evidence. A local curl response from a development machine does not prove that the device received the same production file or that the installed build carries the expected bundle/team identity.

## PRF and Large Blob matrix

### PRF

| Test | Expected evidence | Does not prove |
| --- | --- | --- |
| Supported passkey and fixed salt | Assertion returns PRF output; CryptoKit operation succeeds | Server authorization |
| Same passkey/salt | Deterministic result under documented conditions | Cross-device recovery |
| Different salt version | Explicit migration or new key path | Automatic compatibility |
| Unsupported authenticator | Optional feature disabled with recovery | Universal support |
| Canceled assertion | No key published; ciphertext remains protected | Successful unlock |
| Key discard | Memory/key-lifetime test shows operation ends without persistence | Source code intent alone |
| Passkey removed | Local data is inaccessible or recovery policy runs | Silent data recovery |

### Large Blob

| Test | Expected evidence |
| --- | --- |
| Read supported blob | Schema, version, checksum, and purpose validate |
| Write supported blob | Exact size, write result, and read-back verification |
| Oversize value | Write is rejected before mutation |
| Unsupported extension | Feature falls back without corrupting local state |
| Migration | Old version is upgraded or retired intentionally |
| Credential replacement | Blob association behavior is documented |
| Deletion | Blob and related app references are removed according to policy |

## Accessibility and design evidence

Test the complete task, not merely the button:

- VoiceOver can identify provider, purpose, current phase, errors, recovery, and deletion.
- Voice Control can activate the intended action without ambiguous duplicate labels.
- Switch Control can reach the action, cancel, and recovery route.
- Dynamic Type preserves the explanation and status without clipping.
- Reduced motion and reduced transparency preserve hierarchy without making glass essential.
- Localized provider names, security warnings, pluralization, and error recovery fit.
- The app-owned screen does not pretend to control the system-owned credential sheet.

For Liquid Glass, capture the app-owned shell separately from the system authorization surface. A screenshot of the shell is not proof of a successful credential operation.

## Server negative-test matrix

The relying-party verifier should have automated negative cases for:

- wrong challenge;
- reused challenge;
- wrong relying-party identifier or origin;
- malformed client data;
- invalid signature;
- wrong credential ID;
- wrong user/account binding;
- expired token;
- wrong issuer;
- wrong audience/client identifier;
- invalid nonce;
- revoked/transferred/deleted account;
- one-time authorization code replay;
- mismatched environment;
- missing required user verification policy.

Record verifier version and test fixture hashes. Do not use a model-generated interpretation as the oracle for any negative case.

## Release evidence

The release packet should include:

1. Signed archive/TestFlight artifact and entitlement dump.
2. Production associated-domain URL, status, content hash, and application entry.
3. Server verifier and provider configuration revision.
4. Physical-device registration/assertion results.
5. Sign in with Apple first-use, returning, relay, revocation, transfer, and deletion results.
6. Security-key transport results for every claimed transport.
7. Browser callback/state/nonce results.
8. PRF/Large Blob optional-route and recovery results.
9. Accessibility/localization/reduced-transparency results.
10. Redacted logs and incident rollback plan.

Preview, simulator, local callback, development entitlement, and a successful build are useful development signals but not release proof.

## Sources

- [Authentication Services](https://developer.apple.com/documentation/authenticationservices)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [AuthorizationController](https://developer.apple.com/documentation/authenticationservices/authorizationcontroller)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [Connecting to a service with passkeys](https://developer.apple.com/documentation/authenticationservices/connecting-to-a-service-with-passkeys)
- [Public-Private Key Authentication](https://developer.apple.com/documentation/authenticationservices/public-private-key-authentication)
- [Supporting Security Key Authentication Using Physical Keys](https://developer.apple.com/documentation/authenticationservices/supporting-security-key-authentication-using-physical-keys)
- [ASAuthorizationPlatformPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationplatformpublickeycredentialprovider)
- [ASAuthorizationSecurityKeyPublicKeyCredentialProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationsecuritykeypublickeycredentialprovider)
- [Implementing User Authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
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
