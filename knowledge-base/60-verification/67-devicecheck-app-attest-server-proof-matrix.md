# DeviceCheck and App Attest server proof matrix

DeviceCheck evidence spans app, device, Apple service, server, account, and release environments. A client callback or server response without cryptographic validation and replay fixtures is not proof.

| Claim | Evidence | Failure fixture / boundary |
| --- | --- | --- |
| The App ID is registered | Apple Developer App ID record and target/bundle mapping | App Attest API present but App ID not registered |
| App Attest is supported | Physical device/OS/support matrix records isSupported | Mac Catalyst, iPhone/iPad on Apple silicon, or extension assumed supported |
| Key generation is correct | One unique key per account/device, key ID persisted and recoverable | Key regenerated per request or key ID stored only in memory |
| Private key is protected | App Attest service creates/uses Secure Enclave key; no private key export/log | App treats key ID as secret or copies private key into app storage |
| Attestation is server-validated | Server verifies CBOR/nonce, certificate/public key, App ID/RP ID hash, counter/environment, key ID, app/version, and stores verified public key | Client sends “verified” Boolean or server trusts payload fields |
| Challenge is fresh | Server produces random one-time challenge bound to account/request/expiry and rejects reuse | Static, client-generated, or replayable challenge |
| Assertion binds to request | Server verifies client-data hash, request body/context, signature, key ID, and expected challenge | Valid assertion replayed for a different request/body |
| Counter policy is enforced | Server stores counter and handles monotonic progression/recovery policy | Counter ignored, regressed, or reset silently |
| Environment is separated | Development/TestFlight/production attestation and app version are recorded and policy-matched | Development attestation accepted as production |
| Account binding is real | Key ID is associated with the intended account/device and sign-out/revocation is tested | App integrity treated as account identity or entitlement |
| DeviceCheck token is available | DCDevice support and generateToken result recorded on target device | Token assumed on unsupported runtime |
| Two bits have explicit meaning | Server query/update/reset fixtures name bit semantics and last-modified state | Bits treated as a generic trust score or identity |
| Device reset/reassignment works | Sale/reset/reinstall/new-account and bit/key revocation recovery are tested | Old device state permanently blocks new owner |
| Unsupported extension fallback is safe | Extension matrix proves generateKey failure/unsupported path and containing-app alternative | Key generation placed in arbitrary extension |
| AI/premium action is protected | Server validates app/account/request before model delivery/tool/side effect and user confirms result | Attestation used to assert model truth or user consent |
| Privacy is bounded | Challenge/assertion/token logs are redacted; raw user content is not retained unnecessarily | Security telemetry includes prompts, tokens, or identifiers |
| Accessibility and recovery work | VoiceOver, Dynamic Type, high contrast, Reduce Motion, network/risk/deferred/support states pass | Green shield/color-only status or no recovery action |
| Release proof exists | Signed archive, bundle/version/environment, device matrix, server configuration, and distribution evidence | Simulator/local server/2xx response treated as release proof |

## Fixture set

- App ID/bundle/team/environment mismatch;
- supported physical device and unsupported Mac/Catalyst/extension;
- first key generation, persistent key ID, lost key ID;
- attestation success, network error, malformed/rejected object, version/environment mismatch;
- fresh one-time challenge, expiry, replay, account mismatch, request-body mismatch;
- valid assertion, bad signature, wrong key, counter regression, key revocation;
- DeviceCheck supported/unsupported, token error, query/update/reset two-bit fixtures;
- reinstall/new device/account sign-out;
- AI premium generation/tool request accepted/deferred/rejected;
- rate limit, risk review, server timeout, offline;
- redacted telemetry, privacy deletion, accessibility, localization, and reduced motion.

## Evidence ladder

1. Pure challenge/hash/request-binding tests.
2. App target and support/build configuration.
3. DeviceCheck/App Attest development environment with server validator.
4. Physical device and distribution-channel attestation/assertion.
5. Production-like server, account, replay, rate, revocation, and AI/tool action tests.
6. Privacy, accessibility, support/recovery, and release review.
7. Signed archive/distribution evidence.

Record the app ID, bundle ID, environment, version, device/OS/extension, account key ID reference, challenge ID, counter, server decision, and remaining gaps. Do not store private keys or raw user content as evidence.

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
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
