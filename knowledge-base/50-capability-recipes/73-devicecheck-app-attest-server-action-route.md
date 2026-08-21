# DeviceCheck and App Attest server-action route

Use this route when an iOS, iPadOS, or watchOS feature crosses into a server-side premium, high-cost, abuse-sensitive, or state-changing action. Keep local-only work local; add App Attest only when a server needs app-instance evidence.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | Access a server action with bounded abuse/risk controls |
| Account | Authenticate the account separately from app/device integrity |
| App integrity | App ID registration, DCAppAttestService support, key, Apple attestation, server public-key registration |
| Request proof | One-time server challenge, client-data hash, assertion, request/body binding, counter |
| Device state | Optional DCDevice token and two server-side per-device bits |
| Server decision | Verify cryptography, account, key, challenge, version/environment, risk, rate, and entitlement |
| AI | Use for premium generation, model download, or side-effect tool boundary; not model truth |
| Fallback | Unsupported device/extension, network, attestation failure, review, limited local mode |
| UI | Native status, review, cost/limits, retry/support, and final action confirmation |
| Glass | Group trust status; never expose tokens/certificates or imply absolute security |
| Proof | Physical device, server validation fixtures, replay/counter/revocation, account/reset, accessibility, privacy, and signed release evidence |

## 1. Decide whether this route is needed

Use a server trust route when the consequence is meaningful:

- premium content/model delivery;
- costly or rate-limited generation;
- limited redemption;
- state-changing tool call;
- abuse-sensitive upload;
- server decision that must distinguish legitimate app instances.

Do not add App Attest to a local-only model solely to show a shield. A client-side security indicator without a server validation path adds ceremony without authority.

## 2. Configure the app and server

Before coding:

1. register the App ID required by App Attest;
2. identify the development/production environment;
3. decide per-account/per-device key association;
4. define challenge storage and expiry;
5. define key revocation/re-registration;
6. define unsupported-device fallback;
7. define server risk and entitlement policy;
8. define privacy/audit retention.

Keep server authentication keys and team identifiers out of the app. Treat them as server-side credentials and pass only opaque challenge/request data to the app.

## 3. Provision an App Attest key

The app checks isSupported, generates a key once per account/device route, persists the returned key identifier, and sends an attestation object to the server. The server validates and stores the public key before accepting protected requests.

Do not generate a new key on each request. If the identifier is lost, make re-registration/revocation explicit.

## 4. Prove each request

For a protected request:

1. account session is valid;
2. server issues a random one-time challenge;
3. client binds challenge and request context into the documented client-data hash;
4. App Attest generates an assertion with the registered key;
5. client sends assertion, key ID, challenge/request ID, and request;
6. server verifies assertion signature, challenge, request hash, key, counter, environment/version, account, and policy;
7. server allows, rejects, defers, or rate-limits;
8. user reviews any generated draft before an external side effect.

Do not let the app decide that its own assertion is valid. Do not accept an assertion without challenge/request binding.

## 5. Add DeviceCheck only for a bit policy

If the server needs a small per-device state:

1. check DCDevice.current.isSupported;
2. generate an ephemeral token;
3. send it over an authenticated channel;
4. server calls Apple’s DeviceCheck service;
5. server applies the bit meaning and risk policy;
6. server returns a product decision.

Write down what each bit means and when it resets. The app does not receive a generic fraud verdict from the token.

## 6. AI route

The safe composition is:

account auth -> one-time challenge -> App Attest validation -> server policy/rate/entitlement -> model/tool request -> draft/review -> side effect

Use the smallest request body and redact telemetry. Do not upload raw private text merely to attest the app. Keep model input/output, verification evidence, account identity, cost, and user confirmation separate.

## 7. Failure states

Handle:

- isSupported false;
- Mac/Catalyst/Apple silicon path;
- unsupported extension;
- key generation error;
- lost key ID;
- attestation rejected;
- assertion rejected;
- challenge expired/replayed;
- counter regression;
- app version/environment mismatch;
- DeviceCheck token failure;
- account mismatch;
- key revoked;
- network/server timeout;
- rate limit/risk review;
- user cancels final AI action.

The fallback must not silently weaken a high-risk action. It can reduce functionality, require manual review, or keep the operation unavailable.

## 8. Minimum evidence bundle

- registered App ID and environment;
- signed build/device/extension matrix;
- App Attest support and key ID persistence;
- attestation server validation;
- assertion challenge/body/counter/replay tests;
- DeviceCheck two-bit token/query/update/reset;
- account/sign-out/new-device/revocation;
- AI premium/tool action with user review;
- unsupported/network/limited fallbacks;
- redacted logs/privacy/retention;
- accessibility and release artifacts.

## Sources

- [DeviceCheck](https://developer.apple.com/documentation/devicecheck)
- [DCDevice](https://developer.apple.com/documentation/devicecheck/dcdevice)
- [Accessing and modifying per-device data](https://developer.apple.com/documentation/devicecheck/accessing-and-modifying-per-device-data)
- [DCAppAttestService](https://developer.apple.com/documentation/devicecheck/dcappattestservice)
- [DCAppAttestService.isSupported](https://developer.apple.com/documentation/devicecheck/dcappattestservice/issupported)
- [generateKey(completionHandler:)](https://developer.apple.com/documentation/devicecheck/dcappattestservice/generatekey%28completionhandler%3A%29)
- [Establishing your app’s integrity](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity)
- [Validating apps that connect to your server](https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server)
- [Attestation Object Validation Guide](https://developer.apple.com/documentation/devicecheck/attestation-object-validation-guide)
- [Assessing fraud risk](https://developer.apple.com/documentation/devicecheck/assessing-fraud-risk)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
