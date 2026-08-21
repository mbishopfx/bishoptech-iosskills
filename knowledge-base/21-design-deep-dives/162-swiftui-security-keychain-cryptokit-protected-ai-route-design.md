# SwiftUI design for Keychain, CryptoKit, and protected local-AI features

A secure feature should look calm and native without hiding what is protected. The screen is not a decorative “vault”; it is a transparent contract between a person, the app-owned data, the device security state, and any optional local model.

The design target is:

```text
clear purpose
    -> truthful protection state
    -> one intentional unlock action
    -> visible data scope and revision
    -> reviewable AI proposal
    -> explicit save/export/delete boundary
```

Do not let a success-colored card or glass blur imply that the person has been authenticated to an account, that a secret is present, or that AI output has been accepted. Those are separate states.

## Screen anatomy

Use a small number of semantic regions rather than a wall of security terminology:

| Region | Content | Interaction |
| --- | --- | --- |
| Purpose header | “Private journal”, “Local model workspace”, or another concrete user outcome | Back, help, and lock state are available as ordinary controls |
| Protection card | Locked, unlocked-for-this-action, unavailable, missing, invalidated, or corrupt | Unlock, lock, retry, recovery, or settings action |
| Scope card | Count or redacted description of records, last verified revision, retention policy | Open details; never reveal plaintext merely to decorate the card |
| AI proposal card | “Draft summary”, source revision, model availability, confidence/limitations | Review, edit, accept, reject, regenerate, or use deterministic fallback |
| Destructive boundary | Delete local copy, revoke session, export, or reset key | Confirmation dialog with exact scope and recovery consequences |
| System explanation | Why device passcode/biometry, app access, or a target entitlement is needed | Accessible disclosure or help sheet |

The primary action should be phrased as the user outcome: “Unlock private journal,” “Review local summary,” or “Delete this device copy.” “Secure” and “Continue” are weak labels because they do not state what will happen.

## Protection state is a state machine

Render security as an app-owned enum, not a collection of unrelated Booleans:

```text
locked
  -> authenticating
      -> unlockedForAction
      -> cancelled / denied / unavailable
  -> missing
  -> invalidated
  -> corrupt
  -> recoveryRequired
```

The `unlockedForAction` state should carry an expiration or scope, such as “current edit session” or “this save operation.” Do not retain a permanent `isUnlocked` flag after a Keychain or Secure Enclave operation has ended. If the app needs a longer session, state its timeout and lock it when the scene resigns active or the user taps Lock.

| State | Copy pattern | Visual treatment |
| --- | --- | --- |
| Locked | “Your private records are closed on this device.” | Neutral card, familiar lock icon, one primary Unlock button |
| Authenticating | “Confirm to open this private workspace.” | System prompt owns the biometric/passcode interaction; app shows progress only where appropriate |
| Unlocked for action | “Open for this editing session.” | Clear timestamp/scope and a Lock button; do not expose keys |
| Device passcode required | “Set a device passcode to protect this workspace.” | Explain why, with a Settings handoff only if the product supports it |
| Denied/cancelled | “Nothing was opened.” | Keep data locked, provide Retry and a non-biometric path where allowed |
| Missing | “This device has no key for this workspace.” | Recovery or start-new flow; never display old plaintext as if recovered |
| Invalidated | “The device security state changed.” | Explain that recovery may be required; separate from a bad password |
| Corrupt | “This record could not pass integrity verification.” | Preserve the protected original, offer restore/recovery, and avoid destructive auto-repair |
| Proposal ready | “A local draft is ready for review.” | Label source revision, model availability, and that no save/side effect has happened |

## Liquid Glass use with trust-sensitive content

Liquid Glass is a material and interaction system, not a security signal. Use it to group a small number of related controls—such as status, Unlock, and Lock—where the material helps the group float above the app’s content. Keep the following opaque and legible:

- protection state and action label;
- source revision and last verified time;
- error, recovery, and deletion consequences;
- the difference between model proposal and saved result; and
- units, counts, and data scope.

Good uses:

- a compact status/action cluster over a scrolling private-record surface;
- a review toolbar for Accept, Edit, Reject, and Lock;
- a non-destructive filter or scope control that does not contain secrets; and
- a consistent glass container for a short row of native actions.

Risky uses:

- blurring the only explanation of whether the data is locked;
- making an app-owned biometric imitation look like Apple’s system prompt;
- putting raw private text into a persistent floating glass panel;
- applying glass to every list row, chart point, or encrypted-state badge; and
- using material movement to communicate a security transition that must remain understandable with Reduce Motion or reduced transparency.

Prefer standard system controls, `confirmationDialog`, `alert`, `sheet`, `NavigationStack`, `Form`, `List`, and `ContentUnavailableView`. If a custom visual is necessary, keep the security meaning in text and accessibility labels, then add restrained material around it.

## The unlock interaction

Ask at the last responsible moment. The context around the action should answer:

1. What will open?
2. Why does the app need device authentication or a passcode?
3. What happens if the person cancels or cannot authenticate?
4. How long will the session stay open?
5. Can the person use a manual or non-biometric alternative?

Avoid an automatic biometric prompt on first launch for a feature that is not yet requested. Explain the purpose in the surrounding SwiftUI surface before invoking the Keychain access-control path. The system-owned prompt should remain the system-owned prompt; the app should not render a fake Face ID, Touch ID, or passcode sheet.

For a local AI action, phrase the boundary precisely:

```text
Review local summary
    -> confirm access to the selected encrypted records
    -> decrypt the bounded feature window
    -> generate a proposal on device if available
    -> show the draft and source revision
    -> user accepts or edits
    -> app encrypts and saves the accepted result
```

The AI card must not jump directly from “model available” to “saved.”

## Proposal cards for local AI

A good proposal card makes uncertainty and provenance visible without overwhelming the person:

| Field | Example |
| --- | --- |
| Label | “Local draft summary” |
| Source | “Based on 6 selected records, revision 42” |
| Execution | “Processed on this device” when that is actually true |
| Status | Draft, edited, accepted, rejected, unavailable, or stale |
| Limit | “May omit context; review before saving or sharing.” |
| Actions | Review, Edit, Accept, Reject, Regenerate, Lock |

If the model is unavailable, show a deterministic local summary or a clear unavailable state. Do not hide a failed AI route by silently switching to a network provider when the screen promised private/on-device processing. If a product intentionally has a provider fallback, name the route and obtain the required consent.

Never display a generated account identifier, access group, Keychain query, algorithm choice, or key-recovery decision as if model output could authorize it. AI can draft text or classify app-owned data; the security coordinator must own commit, deletion, unlock, and key lifecycle.

## Error and recovery surfaces

Use error copy that maps to an actionable state:

| Technical boundary | User-facing surface |
| --- | --- |
| `errSecItemNotFound` | “This device has no saved key for this workspace.” |
| Device locked / interaction not allowed | “Unlock the device, then try again.” |
| User cancelled | “Nothing changed.” |
| Biometry unavailable or enrollment changed | “Use the available device authentication method or recover this workspace.” |
| `errSecMissingEntitlement` | This is a build/configuration failure; never ship it as an end-user retry loop. |
| Wrong associated data or authentication tag | “The record failed its integrity check.” Preserve the original and offer recovery. |
| Unsupported algorithm/version | “This record needs an app update or migration.” |
| Secure Enclave key invalidated | “This device key is no longer available.” Explain whether account recovery or reset is possible. |
| Sync not present | “This device copy is not synchronized.” Do not imply data loss until the sync/recovery authority has been checked. |

The error view should preserve a route back to the safe state. A failed unlock should not clear all data. A failed migration should not overwrite the old envelope. A failed AI proposal should not change the protected source record.

## Accessibility and alternate input

Security actions must be complete with VoiceOver, Dynamic Type, Increase Contrast, Reduce Transparency, Reduce Motion, Switch Control, Voice Control, keyboard, pointer, and localization. Verify:

- the protection state is announced before the primary action;
- “Unlock private journal” and “Lock private journal” are distinct accessible names;
- the current scope, source revision, and proposal status are readable without opening a decorative card;
- errors are announced and do not expose secret values;
- a person can accept, reject, edit, or delete a proposal without a swipe or haptic cue;
- reduced effects remove movement from lock/unlock transitions without removing state text; and
- right-to-left and large text layouts do not hide destructive consequences or the Lock action.

Do not make the person shake the device, stare at a lock animation, or rely on color to prove protection. Use haptics only as optional reinforcement after the accessible state is already clear.

## Design checklist

Before calling the screen Apple-native and trustworthy, verify:

- [ ] The protected object and user outcome are named in plain language.
- [ ] Locked, authenticating, denied, missing, invalidated, corrupt, proposal, and saved states are distinct.
- [ ] Unlock is requested at the point of action and the system prompt is not imitated.
- [ ] Liquid Glass groups a small action/status cluster and does not hide meaning.
- [ ] AI output is labelled as draft/proposal until accepted.
- [ ] Source scope, revision, model route, and freshness are visible or accessible.
- [ ] Delete, export, revoke, and reset actions state their exact scope and recovery effect.
- [ ] The screen works without biometry when the product policy permits a passcode/manual alternative.
- [ ] Dynamic Type, VoiceOver, reduced transparency/motion, contrast, keyboard, pointer, and localization are verified.
- [ ] The signed target, entitlement, Keychain policy, and physical device behavior are tested separately from the visual preview.

## Sources

- [Apple Human Interface Guidelines: Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Apple Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Keychain services](https://developer.apple.com/documentation/security/keychain-services)
- [Restricting keychain item accessibility](https://developer.apple.com/documentation/security/restricting-keychain-item-accessibility)
- [SecAccessControlCreateFlags](https://developer.apple.com/documentation/security/secaccesscontrolcreateflags)
- [Apple CryptoKit](https://developer.apple.com/documentation/cryptokit)
- [AES.GCM](https://developer.apple.com/documentation/cryptokit/aes/gcm)
- [Storing CryptoKit keys in the keychain](https://developer.apple.com/documentation/cryptokit/storing-cryptokit-keys-in-the-keychain)
- [Protecting keys with the Secure Enclave](https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
