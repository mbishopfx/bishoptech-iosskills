# Tracking consent and privacy-status design

AppTrackingTransparency is a system permission, not a conversion trick. The surrounding UX should make the data use legible, keep the core product useful without tracking, and show the current state without implying that the user owes the app a choice.

## Explain the actual decision

Before requesting the system prompt, show:

- what “tracking” means for this app;
- the optional feature that benefits from it;
- what categories of app-related data are shared or compared;
- whether an advertising identifier is involved;
- what still works if the user chooses Don’t Allow;
- where to change the choice later.

Do not call first-party local analytics “tracking” just to make the prompt sound larger, and do not hide cross-app sharing behind vague words such as “personalization.”

## Permission sequencing

Use a permission coordinator with explicit states:

| State | User-facing copy | Action |
| --- | --- | --- |
| Not determined | Explain optional benefit and privacy choice | Continue to system request at an active moment |
| Request pending | “Waiting for your choice” | Do not start another permission prompt |
| Authorized | Explain permitted advertising/attribution behavior | Use only approved route |
| Denied | “The app still works without cross-app tracking” | Use identifier-free fallback; link to Settings only as education |
| Restricted | “Tracking access is restricted on this device” | Use fallback; do not repeatedly prompt |
| Changed in Settings | Refresh on foreground | Recompute route and show current state |
| Unsupported surface | “This environment does not provide a tracking identifier” | Use fallback |

The system prompt only appears when the app is active, and calls from extensions do not prompt. A custom app-owned modal cannot substitute for the system decision.

## Make the fallback first-class

The denied/restricted route should have a complete experience:

- contextual or non-personalized content;
- aggregate measurement;
- local preferences;
- account-free on-device AI features where appropriate;
- user-approved referral or campaign codes that do not depend on cross-app identity;
- clear explanation of which optional feature is unavailable.

Do not show an empty advertising slot, broken personalization label, or “turn on tracking to continue” wall when the feature is optional.

## Status surfaces

A native settings screen can include:

- a compact status row: Not Requested, Allowed, Denied, or Restricted;
- a plain-language purpose summary;
- an “Identifier-free mode” confirmation;
- an explanation of what data the app does not collect in that mode;
- a Settings help link when the user wants to change a prior choice;
- a privacy-policy link;
- a reset/diagnostic explanation without exposing the UUID.

Use “Tracking permission” and “Advertising identifier” as separate concepts. A status of Authorized does not authorize unrelated personal-data uses, and a nonzero identifier does not prove that a tracking vendor received it.

## Liquid Glass without pressure

Liquid Glass can contain the status and optional feature explanation:

- system title and purpose copy;
- a readable state label;
- one primary action for the optional feature;
- a secondary Continue without tracking action;
- a small privacy disclosure.

Do not use bright motion, countdowns, guilt copy, or a visually disabled fallback to pressure Allow. Ensure the primary action is still readable with increased contrast and Reduce Motion. The system-owned prompt remains the final authorization surface.

## AI and personalization design

Keep these separate:

- local preference used for an on-device model;
- first-party event telemetry;
- account state;
- advertising identifier;
- cross-app/site tracking status;
- generated recommendation.

An AI feature should show what local inputs it uses and continue with local context when ATT is denied. Never say “AI needs tracking” unless the actual product contract requires a distinct data flow and the user sees that tradeoff.

## Accessibility and localization

Make consent and fallback tasks work with VoiceOver, Dynamic Type, Voice Control, Switch Control, keyboard, pointer, increased contrast, and reduced motion:

- give the status a text label and accessible value;
- announce the fallback consequence before the system prompt;
- keep Allow and Continue without tracking equally discoverable;
- provide a text link to privacy details and Settings help;
- avoid icons that imply trust or guilt;
- support long localized purpose strings and right-to-left layouts.

Do not localize “tracking” into a generic “data collection” phrase if that changes the legal/user meaning.

## Data-logging design

Store only what operations need:

- status category, not the identifier;
- feature route chosen, not raw attribution payloads;
- aggregate counts and privacy-safe diagnostics;
- timestamp of status observation;
- model availability, not IDFA in model telemetry.

If a support export needs technical details, redact identifiers and make the export user-initiated.

## Proof-oriented handoff

The design handoff should include:

- exact purpose string and data-flow explanation;
- prompt coordinator states;
- active-app/background/another-prompt fixtures;
- status refresh after Settings changes;
- all-zero identifier and simulator fallback;
- denied/restricted identifier-free flow;
- AI personalization without IDFA;
- accessibility/localization/reduced-motion evidence;
- signed device and review/distribution proof.

## Sources

- [AppTrackingTransparency](https://developer.apple.com/documentation/apptrackingtransparency)
- [ATTrackingManager](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager)
- [requestTrackingAuthorization(completionHandler:)](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/requesttrackingauthorization%28completionhandler%3A%29)
- [trackingAuthorizationStatus](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/trackingauthorizationstatus)
- [AdSupport](https://developer.apple.com/documentation/adsupport)
- [ASIdentifierManager](https://developer.apple.com/documentation/adsupport/asidentifiermanager)
- [advertisingIdentifier](https://developer.apple.com/documentation/adsupport/asidentifiermanager/advertisingidentifier)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
