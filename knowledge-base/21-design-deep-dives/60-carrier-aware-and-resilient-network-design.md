# Carrier-aware and resilient network design

Cellular-aware UI should make network uncertainty understandable without turning technical signals into marketing claims. The native design loop is:

user goal -> observed policy/path/service state -> safe product decision -> visible status -> recovery or offline continuation

The design should work when there is no carrier information, no registered service, restricted cellular data, no eligible network slice, or no network at all.

## Design the user outcome first

Good outcomes include:

- continue reading or editing while offline;
- postpone a large transfer until Wi-Fi;
- understand why a live session is degraded;
- request a preferred route for a supported game or stream;
- move an active app session to a newly active iPhone;
- recover after the user changes cellular settings.

Avoid a generic “network dashboard” as the first screen. Most people need to know whether the next action will work and what they can do next.

## A calm status hierarchy

Use a small, semantic hierarchy:

1. Primary task state: ready, syncing, cached, waiting, or failed.
2. Path context: Wi-Fi/cellular/unknown from the Network layer.
3. Policy context: cellular restricted, expensive, constrained, or permitted where the app has evidence.
4. Optional service detail: radio technology or preferred slice state.

Do not show carrier name, radio technology, or an icon merely because it is technically available. Show it when it helps the user decide something and label it as an observation.

## Transfer policy surface

A transfer inspector can offer:

- Use Wi-Fi when possible
- Allow cellular for this transfer
- Download a smaller offline version
- Continue with cached content
- Stop and resume later

Explain the reason with plain language:

- “Cellular data is restricted for this app.”
- “The current path is unavailable.”
- “This transfer is waiting for Wi-Fi.”
- “The preferred gaming route is not available on this network.”

Do not say “the network is slow” unless the app has measured the operation and can support that statement.

## Network slicing as an intent, not a badge

If the app supports CTSlicingManager, the UI should distinguish:

- feature available to the target;
- category available now;
- request submitted;
- preferred slice active;
- active slice observed;
- unavailable or unsupported.

Use a confirmation or settings sheet for the user-facing request. Keep the primary task usable if the request fails. A “Gaming route active” label should appear only after the app has observed the relevant state, and it should still avoid latency guarantees.

## Quick-switch continuity

An app that supports iPhone quick switch should not look like it signed the user out every time the active device changes. Use a transition surface:

- “This iPhone is becoming active.”
- “Moving your local session and pending work.”
- “This iPhone is passive; service is active elsewhere.”
- “We could not determine the active device.”

Show what the app can actually transfer: local session state, encrypted cache, queued work, or a server-side handoff. Do not present cellular state as account identity. Keep a recovery path if background launch or handoff is unavailable.

## eSIM is a specialized system surface

If the target is a carrier app with the required entitlement, eSIM provisioning deserves a dedicated flow with plan identity, eligibility, consent, progress, cancel, failure, and unknown-result states. If the target is not an eligible carrier app, do not display a pretend “Add cellular plan” button. Explain the supported alternative, such as opening the carrier’s documented flow or continuing without provisioning, only when the product has a real handoff.

## Liquid Glass composition

Use Liquid Glass for:

- a route explanation panel;
- a compact transfer-policy control;
- a quick-switch transition sheet;
- a network-slice review card;
- an error/recovery action cluster.

Keep the task content outside the material when possible. Glass should not obscure a warning, make text dependent on blur, or animate on every radio/path update. Provide reduced-motion and reduced-transparency-friendly states.

## Accessibility and localization

Cellular and network states must not rely on signal bars, color, or a radio icon:

- use clear text and VoiceOver descriptions;
- expose the current decision and next action;
- support Dynamic Type and long translated strings;
- announce meaningful state transitions without spamming on every path callback;
- make retry, pause, cancel, and continue offline real buttons;
- avoid abbreviations such as “RAT” in the user-facing surface;
- ensure the screen remains understandable with reduced motion and increased contrast.

## AI should explain, not impersonate the carrier

Good AI copy:

- “Your app can keep this draft locally and upload it when Wi-Fi is available.”
- “The carrier did not make the preferred route available.”
- “This transfer may use cellular data if you approve it.”

Bad AI copy:

- “Your 5G connection is guaranteed fast.”
- “Your carrier approved this account.”
- “The network is secure because the icon is green.”
- “I moved your phone number to this device.”

Show the underlying observation and keep the action deterministic. AI can draft a policy or summarize a transition; it cannot grant an entitlement or change cellular service.

## Failure states to design before the happy path

- no SIM/eSIM or no registered service;
- cellular data restricted;
- radio state unavailable;
- Wi-Fi and cellular both unavailable;
- request created before network-slice activation;
- slice category unavailable;
- activation returns unsupported;
- quick-switch state unknown or passive;
- background launch registration fails;
- transfer interrupted while switching devices;
- carrier eSIM result is cancel, fail, or unknown.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Core Telephony](https://developer.apple.com/documentation/coretelephony)
- [CTTelephonyNetworkInfo](https://developer.apple.com/documentation/coretelephony/cttelephonynetworkinfo)
- [CTCellularData](https://developer.apple.com/documentation/coretelephony/ctcellulardata)
- [CTSlicingManager](https://developer.apple.com/documentation/coretelephony/ctslicingmanager)
- [iPhone quick switch](https://developer.apple.com/documentation/coretelephony/iphone-quick-switch)
- [CTCellularPlanProvisioning](https://developer.apple.com/documentation/coretelephony/ctcellularplanprovisioning)
- [Network](https://developer.apple.com/documentation/network)
- [NWPathMonitor](https://developer.apple.com/documentation/network/nwpathmonitor)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

***
