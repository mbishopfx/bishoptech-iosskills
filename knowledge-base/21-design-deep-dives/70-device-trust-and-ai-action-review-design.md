# Device trust and AI-action review design

DeviceCheck and App Attest are server-trust signals, not user-facing identity badges. The design should explain what the server is checking, what happens when the check is unavailable, and what the user can still do.

Use this chain:

account -> action explanation -> server challenge -> app/device verification -> server decision -> user review -> side effect -> audit/recovery

## 1. Explain the protected action

Ask for a trust check at a consequential boundary:

- “Verify this app before downloading the premium model.”
- “Check this request before running the paid generation.”
- “Protect this limited redemption.”
- “Confirm the app instance before saving the server-side change.”

Do not show “Apple verified you” or “This device is safe.” App Attest validates an app instance/key relationship; DeviceCheck contributes device state; the account and business policy remain separate.

## 2. Make server state visible without exposing security material

Use an app-owned status enum:

- checking;
- ready;
- unsupported device;
- verification required;
- server deferred;
- rejected;
- network unavailable;
- rate limited;
- action completed.

The user needs the action, outcome, and recovery. They do not need a key identifier, nonce, attestation object, certificate chain, fraud score, or bit value.

If a request is deferred for review, say so plainly. Do not render a permanent green shield while the server has not verified the current request.

## 3. AI actions need two confirmations

For a remote model or tool:

1. app/device/server trust establishes whether the request can be considered;
2. user review establishes whether the requested content/action is intended.

App Attest cannot confirm that a generated answer is correct or that a user approved an external side effect. After server validation, show the draft, cost/limits, sources/context, and final action confirmation. Keep “verified request” and “approved result” visually distinct.

For a local-only model, avoid adding a remote trust ceremony that does not protect a remote resource. Use local authentication or no gate based on the actual threat model.

## 4. Liquid Glass without security theater

Liquid Glass can group:

- the action name;
- account/server status;
- verification in progress;
- retry/support;
- cost/limit and user-confirmation controls.

Avoid:

- a shield icon that always says secure;
- a dynamic green glow tied only to a client Boolean;
- hiding “unsupported” behind translucent text;
- flashing fraud warnings with no recovery;
- putting challenge/token material in a debug-like user panel;
- using glass animation as a substitute for server response.

Keep text readable in increased contrast, reduced transparency, Dynamic Type, VoiceOver, Voice Control, and Switch Control.

## 5. Device and account reset flows

Design for:

- new device;
- reinstall;
- app restore;
- signed-out account;
- changed app version;
- revoked key;
- lost key identifier;
- unsupported Mac/Catalyst/extension;
- network outage;
- server migration;
- user sells or resets the device.

Give the user a safe route: retry, sign in again, continue with a limited local feature, contact support, or wait for review. Never ask the user to copy an attestation object or token.

## 6. Privacy and support

Support teams may need a request ID, target, build, OS, device family, server decision, and error category. They should not need raw assertion bytes, tokens, private keys, or user text. Redact request bodies and AI prompts by default.

The privacy explanation should distinguish:

- account data;
- server request metadata;
- DeviceCheck per-device state;
- App Attest key/attestation/assertion data;
- AI input/output;
- audit/abuse records.

Explain retention and deletion. A device-trust record may be necessary for fraud prevention, but it is not a license to keep unrelated user content.

## 7. Accessibility and trust language

VoiceOver should announce:

- the protected action;
- verification state;
- server decision;
- retry/support action;
- whether the feature is limited or completed.

Do not use a color-only shield. Avoid “failed security” language that blames the user for unsupported hardware or network failure. Localize “verification,” “review,” “deferred,” and “limited” carefully; they have different product meanings.

## 8. Proof-oriented interaction fixtures

Test:

- supported physical device;
- unsupported Mac/Catalyst and extension;
- first key generation;
- attestation pending/accepted/rejected;
- assertion accepted/replayed/wrong request/counter failure;
- DeviceCheck token unavailable;
- two-bit state changed/reset;
- server timeout/network offline;
- account sign-out/key revocation;
- premium AI request accepted/deferred/rejected;
- user edits draft before side effect;
- large text, VoiceOver, high contrast, Reduce Motion, and localized copy.

Previews can show status layouts. They cannot prove the server challenge, attestation verification, device support, or abuse behavior.

## Sources

- [DeviceCheck](https://developer.apple.com/documentation/devicecheck)
- [DCDevice](https://developer.apple.com/documentation/devicecheck/dcdevice)
- [DCAppAttestService](https://developer.apple.com/documentation/devicecheck/dcappattestservice)
- [DCAppAttestService.isSupported](https://developer.apple.com/documentation/devicecheck/dcappattestservice/issupported)
- [Establishing your app’s integrity](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity)
- [Validating apps that connect to your server](https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
