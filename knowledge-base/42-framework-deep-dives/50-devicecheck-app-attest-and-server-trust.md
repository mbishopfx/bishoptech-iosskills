# DeviceCheck, App Attest, and server-trust boundaries

DeviceCheck provides server-backed device state and app integrity services. Its two main routes are complementary:

- DCDevice generates a token that your server uses with Apple’s DeviceCheck service to query or update two per-device binary bits;
- DCAppAttestService creates a Secure Enclave-backed key, asks Apple to attest it, and creates assertions that your server verifies for important requests.

Neither route is a universal fraud detector, a user identity provider, or a reason to place sensitive security logic only in the client. Apple explicitly frames DeviceCheck as one input to an overall risk assessment.

Use this chain:

account/request context -> server one-time challenge -> device capability check -> app token/key operation -> server verification -> risk/authorization decision -> auditable response

Keep account identity, app integrity, device state, request body, challenge, key identifier, attestation/assertion, server decision, AI output, and side effect separate.

## 1. DeviceCheck and App Attest solve different problems

Choose DeviceCheck when the server needs a small per-device state, such as whether a device has consumed a limited offer or needs additional fraud review. The app generates a token; the server authenticates with Apple and manages two bits plus their meaning and last-modified state.

Choose App Attest when the server needs evidence that a request came from a legitimate instance of the app using an Apple-certified key. The app creates a key, sends an attestation object and key identifier to the server, and later signs server challenges in assertion objects.

Use both only when each answers a separate product/security question. Do not call a DeviceCheck bit “the user is trusted,” and do not call an App Attest assertion “the account is authorized.”

## 2. App Attest lifecycle

The key lifecycle is:

1. register the app ID in the Apple Developer account;
2. check DCAppAttestService.shared.isSupported;
3. ask the server for the operation/challenge context;
4. call generateKey() once for the account/device route;
5. persist the returned key identifier immediately;
6. send a client-data hash and attestation object to the server;
7. let the server validate the attestation and store the verified public key;
8. ask the server for a unique, one-time challenge for a sensitive request;
9. hash the challenge/request context;
10. call generateAssertion(keyId:clientDataHash:);
11. send the assertion and request context to the server;
12. verify the counter, challenge binding, key, app ID, version/environment, and request before deciding.

Apple’s documentation says to create a unique key for each user account on each device. If the app loses the key identifier, it cannot use or retrieve the key later; model re-registration and server revocation rather than silently generating an unrelated key.

Do not generate a new key for every request. Do not store a private key in app storage. The service manages the private key in the Secure Enclave and exposes the key identifier/assertion operations.

## 3. Support and extension boundaries

Check isSupported on the actual runtime. Apple documents that App Attest is not supported on Mac devices, including Mac Catalyst and iPhone/iPad apps running on Apple silicon. Most app extensions do not support App Attest; generateKey can fail from an app extension even when isSupported is true. The documented exception is watchOS extensions in watchOS 9 or later, subject to the target’s actual behavior.

This means:

- do not claim that an iPad-on-Mac path has App Attest evidence;
- do not put key generation in an arbitrary extension and assume the containing app’s support applies;
- choose a server fallback for unsupported devices, or reduce the operation’s risk;
- record device family, extension type, OS, distribution channel, and support result.

DeviceCheck itself also has availability and app-ID registration requirements. A client-only boolean is not a server token validation.

## 4. Server validation is the security boundary

The server must issue fresh, unpredictable, one-time challenges and bind them to the account, request, key identifier, and expiry. For attestation, Apple’s validation guide requires checking the attestation object’s structure, nonce binding, certificate/public-key relationship, app ID/RP ID hash, counter/environment values, key identifier, and relevant app/version evidence. For assertions, the server verifies the signature, challenge, key, request body, and counter progression.

Do not accept:

- a client-generated “valid” flag;
- an assertion without a server challenge;
- a replayed challenge;
- an assertion for a different request body;
- an unknown key identifier;
- a counter regression without a documented recovery policy;
- a development attestation in a production decision;
- a valid app instance as proof that the user is entitled to a purchase/account action.

The server stores the verified public key, key identifier, environment/version context, counter, account/device association, registration time, and revocation/recovery state. Keep raw attestation/assertion material only as long as the audit/privacy policy requires.

## 5. DeviceCheck per-device bits

DCDevice.current.generateToken produces an ephemeral token for the server. The server uses Apple authentication credentials to query or update two binary bits. The app/server team defines what the bits mean and when they reset. Apple stores and reports the bits; the product owns the semantic policy.

Examples of a deliberately narrow bit contract:

- bit 0: limited offer consumed;
- bit 1: require server risk review.

Do not encode a full identity, device fingerprint, or model profile into two bits. Do not treat token generation as a successful fraud decision. The server still needs account, request, rate, payment, abuse, and device-context logic.

## 6. AI and premium actions

App Attest is useful when an app has a server-backed action such as:

- download premium model assets;
- submit a high-cost generation request;
- call a tool that changes server state;
- redeem a limited offer;
- upload a user-approved artifact.

The route is:

authenticated account -> server challenge -> app assertion -> server validation -> policy/risk check -> model/tool action -> auditable result

App Attest does not validate the model output, user intent, consent, copyright, payment fulfillment, or the truth of a generated response. A local model that runs entirely on device usually does not need App Attest for its own inference; use it when the result crosses a server or side-effect boundary.

## 7. Liquid Glass trust presentation

Use native SwiftUI for an app-owned status such as:

- “Device integrity check unavailable”;
- “This request is protected by the server”;
- “Additional verification required”;
- “Premium generation is ready.”

Liquid Glass can group status and retry/support controls. Do not show a permanent green shield based on a client-side assertion. The user should be able to see whether the server accepted, rejected, or deferred the request, and whether the fallback is limited functionality or a retry.

Do not reveal attestation certificates, tokens, key identifiers, challenge material, or detailed fraud signals in a user-facing glass surface.

## 8. Privacy, abuse, and recovery

Define:

- what account/device association the server retains;
- how a user selling or resetting a device is handled;
- how key loss, reinstall, restore, migration, and sign-out behave;
- how unsupported devices continue safely;
- how failed attestation affects access;
- how rate limits and abuse review interact with account support;
- how data is deleted and how audit records are retained.

App Attest is not absolute protection. A legitimate app can still contain a product bug, a user can misuse a valid account, and a compromised environment may bypass assumptions. Use layered server risk controls.

## 9. Evidence boundaries

Prove separately:

1. registered app ID and environment;
2. physical device and support result;
3. key generation and persistent key-ID recovery;
4. server challenge uniqueness/expiry/replay rejection;
5. attestation server validation;
6. assertion signature/request/counter validation;
7. DeviceCheck token and two-bit server path;
8. unsupported Mac/extension fallback;
9. account/sign-out/device-reset/revocation;
10. AI/tool/premium action authorization;
11. privacy, accessibility, logging, and release artifacts.

A key identifier, client assertion, server 2xx, local “verified” flag, or generated result does not prove user identity, entitlement, fraud elimination, model correctness, or production readiness.

## Sources

- [DeviceCheck](https://developer.apple.com/documentation/devicecheck)
- [DCDevice](https://developer.apple.com/documentation/devicecheck/dcdevice)
- [Accessing and modifying per-device data](https://developer.apple.com/documentation/devicecheck/accessing-and-modifying-per-device-data)
- [DCAppAttestService](https://developer.apple.com/documentation/devicecheck/dcappattestservice)
- [DCAppAttestService.isSupported](https://developer.apple.com/documentation/devicecheck/dcappattestservice/issupported)
- [DCAppAttestService.shared](https://developer.apple.com/documentation/devicecheck/dcappattestservice/shared)
- [generateKey(completionHandler:)](https://developer.apple.com/documentation/devicecheck/dcappattestservice/generatekey%28completionhandler%3A%29)
- [Establishing your app’s integrity](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity)
- [Validating apps that connect to your server](https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server)
- [Attestation Object Validation Guide](https://developer.apple.com/documentation/devicecheck/attestation-object-validation-guide)
- [Assessing fraud risk](https://developer.apple.com/documentation/devicecheck/assessing-fraud-risk)
- [Preparing to use the app attest service](https://developer.apple.com/documentation/devicecheck/preparing-to-use-the-app-attest-service)
- [CryptoKit](https://developer.apple.com/documentation/cryptokit)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
