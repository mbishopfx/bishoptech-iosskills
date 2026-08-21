# AuthenticationServices, passkeys, and account-identity proof matrix

Use this matrix to prevent a successful system credential callback from being
mistaken for a verified account, a configured relying party, or an approved
release. It pairs with the [AuthenticationServices route](../42-framework-deep-dives/141-swiftui-authenticationservices-passkeys-route.md),
[design guide](../21-design-deep-dives/169-swiftui-authenticationservices-passkeys-route-design.md),
[capability recipe](../50-capability-recipes/172-swiftui-authenticationservices-passkeys-route.md),
and [Swift recipes](../70-code-recipes/184-swiftui-authenticationservices-passkeys-recipes.md).

## Evidence levels

| Level | What it proves | What it does not prove |
| --- | --- | --- |
| Source | Apple documents the API, target, or policy | The project configured it correctly |
| SDK compile | The selected symbol typechecks against a named SDK | Entitlements, server verification, system UI, or hardware behavior |
| Local unit/integration | State machine, envelope, cancellation, and validation logic behave for fixtures | Apple identity, WebAuthn authenticity, AASA delivery, or device behavior |
| Simulator/UI | App-owned layout and deterministic callbacks work | Physical passkeys, security keys, Apple system account state, AutoFill, or release signing |
| Configuration | Capabilities, entitlements, AASA, target membership, server settings, and signing are aligned | A real person completed the full system and server flow |
| Physical/system | iPhone, system credential UI, domain association, key, or extension works | App Store approval or production reliability without release evidence |
| Server/staging | Challenges, origin, nonce, token exchange, counters, account binding, and recovery work against the service | Production rollout, Apple review, or all device/region combinations |
| Release | Archive/TestFlight build preserves the intended route and evidence | Apple approval unless Apple actually reviews and accepts the build |

## Configuration and source matrix

| Gate | Evidence to collect | Pass condition | Common false proof |
| --- | --- | --- | --- |
| Deployment target | Xcode target settings and SDK diagnostics | Minimum OS matches every API used and fallback is intentional | One successful build on a newer machine |
| Sign in with Apple capability | App ID, Xcode capability, signed archive entitlement | Bundle/client/team configuration agrees with server | Button renders in a preview |
| Associated Domains | Signed entitlement, exact domain list, AASA response, distributed app test | webcredentials entry matches the installed application identifier and domain | curl succeeds from a Mac |
| Credential Provider target | Extension target, embedding, AutoFill entitlement, extension Info.plist | System can discover the intended provider and the extension launches | Containing app can read a shared test file |
| App Group/Keychain access | Entitlements from both targets and access-control policy | Only required shared state is available to the intended targets | Target membership without signed entitlement verification |
| Server client configuration | Apple team/client identifiers, key rotation record, RP/origin allowlist | Staging uses explicit current configuration and secrets stay server-side | A client secret is present in the app bundle |
| Source revision | Official Apple docs, SDK headers, project notes | Claims and availability are linked to the current SDK/source review | A copied blog sample compiles |

## Sign in with Apple matrix

| Scenario | Setup | Expected evidence | Failure must not become |
| --- | --- | --- | --- |
| First authorization | New test Apple account or revoked relationship; requested scopes | Apple callback, server code exchange, validated token, stable subject mapping, optional fields handled | Assumption that name/email will always return |
| Subsequent authorization | Same account and app relationship | Server accepts current token/code; optional profile fields are not required | Duplicate account because optional fields are absent |
| User cancellation | Cancel the system sheet | Request epoch closes, no server session issued, recovery focus returns | Generic authentication failure with data loss |
| Invalid state | Mutate or mismatch state fixture | Server rejects without session and records redacted diagnostic | Client-side “looks valid” acceptance |
| Nonce mismatch | Mutate nonce or replay token fixture | Server rejects token and consumes or invalidates transaction | Local callback treated as proof |
| Expired authorization code | Delay beyond server policy | Exchange fails safely; user starts a new transaction | Infinite retry of a consumed code |
| Revoked credential | Revoke relationship and query state | App shows revoked/recovery state and preserves local content | Silent sign-out plus deletion |
| Transferred state | Exercise account transfer fixture where available | Server/account policy handles transferred identifier explicitly | New account auto-created |
| Private relay | Apple relay address returned | Server stores according to account policy and mail delivery is tested | Relay address shown as the person’s direct address |
| Server unavailable | Block staging auth exchange | Pending state times out with retry/recovery | Signed-in UI from a local callback |

## Passkey registration and assertion matrix

| Scenario | Setup | Expected evidence | Failure must not become |
| --- | --- | --- | --- |
| Registration | Fresh server challenge/RP/user ID and supported iPhone | Registration credential reaches server; challenge, origin, RP ID, flags, algorithm, public key, and policy pass | Credential marked active from UI dismissal |
| Duplicate registration | Existing credential for same account/user ID | Product policy decides whether to add, replace, or reject; user sees consequence | Silent replacement of a recovery method |
| Assertion success | Stored credential and fresh challenge | Signature, client data, RP ID, flags, user handle, credential ID, counter, and account binding pass | Client-side credential ID match only |
| Wrong origin | Mutated origin fixture | Server rejects and records redacted reason | Accepted because string is HTTPS |
| Wrong RP ID | Challenge for a different RP | Server rejects before session issuance | App’s local RP string wins over server policy |
| Challenge replay | Reuse consumed challenge | Atomic transaction prevents second session | Idempotent session from a stale assertion |
| Expired challenge | Wait or force expiry | Server rejects; app requests new transaction | Repeated retries with old bytes |
| Unknown credential | Assertion from unregistered credential | Server rejects without account enumeration | Account created from credential name |
| Counter rollback | Decrease or repeat sign counter fixture | Server policy detects or reviews anomaly | Counter ignored because signature verified |
| User cancellation | Cancel Face ID/passkey UI | No session and no credential record mutation | Error shown as account deletion |
| Domain association unavailable | Remove/stale AASA or wrong entitlement | App offers fallback and configuration diagnostic | Fake passkey success or arbitrary web flow |

## Security-key physical matrix

| Scenario | Hardware/setup | Expected evidence |
| --- | --- | --- |
| Register NFC key | Supported iPhone and compatible key | System ceremony completes; server stores verified public credential |
| Register USB/Lightning key | Actual connector/adapter path | System prompt, physical insertion/removal, and server assertion are recorded |
| Key absent | Begin assertion without key | Clear recovery; no account enumeration or lockout loop |
| Wrong key | Use another test account key | Server rejects; app remains signed out |
| Key removed mid-flow | Remove during system ceremony | Cancellation/error returns to a stable state and closes request epoch |
| Key lockout/PIN issue | Exercise safe test fixture | App preserves account and routes to another recovery method |
| Lost key | Revoke/remove from verified account | Server credential state changes; alternate credential still works |
| Multiple keys | Register two independent keys | Each credential has an explicit label/ID and independent removal audit |
| Device change | Use a second physical iPhone | Domain association, passkey availability, and account behavior are recorded separately |

Never record private-key material, raw authorization tokens, complete assertion
payloads, or personal account identifiers in a routine test artifact.

## Credential Provider Extension matrix

| Scenario | Expected evidence | Stop condition |
| --- | --- | --- |
| Provider discovery | Extension appears in the intended system settings/AutoFill path | Containing app works but extension never launches |
| Service identifier list | prepareCredentialList resolves only current identities | Stale identity is shown as usable |
| User-selected credential | Extension completes the request with the right credential type | UI selection is treated as server authorization |
| No-user-interaction request | Extension honors the system contract without unauthorized UI | Method opens custom UI or hangs |
| User cancellation | extensionContext.cancelRequest completes with a typed error | System request remains pending |
| Extension termination | Kill/relaunch extension during list or request | Stale completion mutates a new request |
| Shared store | App Group/Keychain item access on signed targets | Sensitive data stored in defaults/logs |
| Identity removal | Remove/revoke server credential and refresh identity store | Stale passkey remains discoverable |
| Credential update report | Data-manager parameters accepted and provider reconciliation logged | API success treated as completed server update |
| Configuration UI | Extension setup state can be reached and returns cleanly | Configuration flow depends on the app’s memory |

## Account-linking and recovery matrix

| Risk | Test | Pass condition |
| --- | --- | --- |
| Email collision | Two accounts share or change display email | No automatic merge; both ownership proofs required |
| Apple relay change | Relay address differs from a prior profile | Opaque verified subject/account policy wins |
| Unauthenticated link | Start link from signed-out or expired session | Server rejects; no client-selected account ID accepted |
| Stale link review | Change account or provider in another scene | Old transaction cannot commit into new account |
| Double-submit | Tap commit/retry rapidly | Idempotency key produces one link or clear conflict |
| Credential revocation | Revoke Apple/passkey after link | Account remains recoverable only through registered methods |
| Lost key | Remove the only physical key | Alternate method and local work remain available |
| Deletion | Delete account/credential | Server revokes credentials and app clears only scoped session data |
| AI suggestion | Model proposes an account or merge | Deterministic validator rejects arbitrary IDs and user reviews consequence |

## SwiftUI and accessibility matrix

| Test | Evidence | Pass condition |
| --- | --- | --- |
| Dynamic Type | Largest supported sizes on a signed build | Provider, account, consequence, and recovery remain readable |
| VoiceOver | Full sign-in, cancel, retry, and link flow | Focus returns to a meaningful next action after system UI |
| Voice Control | Spoken commands for every provider and recovery action | Labels are unique and not all “Continue” |
| Switch Control | Traversal through pending/revoked/recovery states | No critical action depends only on a gesture or glass affordance |
| Keyboard/pointer | iPad keyboard/pointer run | Focus and cancellation are coherent across sheets |
| Reduce Motion | Presentation, verification, and success transitions | Meaning does not depend on animation |
| Reduce Transparency | Glass disabled | Trust/review/pending distinction remains legible |
| Contrast/color | Increase contrast and color-filter fixtures | Server status is not conveyed by color alone |
| Localization/RTL | Long provider/privacy/account strings | No clipped action or incorrect mirrored hierarchy |
| AI unavailable | Disable model/asset | Native deterministic route remains complete |

## Archive, TestFlight, and release matrix

| Artifact | Verification |
| --- | --- |
| Debug build | Source route and deterministic fixtures compile; no secrets in bundle/logs |
| Release archive | Extract entitlements, bundle IDs, Associated Domains, extension capabilities, and target membership |
| AASA | Validate production HTTPS response, application identifier, domain/subdomain entries, and no unexpected redirects |
| TestFlight | Install the distributed build on a physical iPhone and repeat domain/passkey/Apple ID flows |
| Security key | Record actual NFC/USB/Lightning route, cancellation, removal, and recovery |
| Credential provider | Enable provider on the test device, invoke from a real app/site, and capture extension lifecycle evidence |
| Server staging | Record challenge IDs, transaction revisions, verification outcomes, and redacted audit events |
| Privacy | Review usage/capability copy, relay handling, logs, crash data, and AI context exclusion |
| Accessibility | Complete assistive-technology task run on the signed build |
| App Store readiness | Check metadata, account deletion/recovery disclosures, privacy details, and review notes against the actual route |

## Redacted evidence record

~~~text
runID:
date:
build: archive digest / TestFlight build
device: model / OS / scene
route: appleID | platformPasskey | securityKey | credentialProvider
rpID/domain:
transactionID: redacted or test fixture ID
requestEpoch:
systemResult: success | cancel | error
serverResult: verified | rejected | expired | unavailable
credentialState: authorized | revoked | notFound | transferred | n/a
linking: none | reviewed | committed | rejected
accessibilitySettings:
ai: unavailable | proposal-reviewed | not-used
knownLimitations:
~~~

## Sources

- [AuthenticationServices](https://developer.apple.com/documentation/authenticationservices)
- [ASAuthorizationController](https://developer.apple.com/documentation/authenticationservices/asauthorizationcontroller)
- [ASAuthorizationAppleIDProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidprovider)
- [Implementing user authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys)
- [Public-private key authentication](https://developer.apple.com/documentation/authenticationservices/public-private-key-authentication)
- [Supporting security key authentication using physical keys](https://developer.apple.com/documentation/authenticationservices/supporting-security-key-authentication-using-physical-keys)
- [ASAuthorizationAccountCreationProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationaccountcreationprovider)
- [ASCredentialProviderViewController](https://developer.apple.com/documentation/authenticationservices/ascredentialproviderviewcontroller)
- [ASCredentialIdentityStore](https://developer.apple.com/documentation/authenticationservices/ascredentialidentitystore)
- [ASCredentialDataManager](https://developer.apple.com/documentation/authenticationservices/ascredentialdatamanager)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
- [Configuring Sign in with Apple](https://developer.apple.com/documentation/xcode/configuring-sign-in-with-apple)
- [SignInWithAppleButton](https://developer.apple.com/documentation/authenticationservices/signinwithapplebutton)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
