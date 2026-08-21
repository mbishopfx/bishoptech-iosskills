# Message filter and caller-ID system-surface design

IdentityLookup features must feel trustworthy because they sit inside Messages and Phone. The system owns the moment of query or report; the app owns only its constrained extension and its setup/support surface.

## Design the user’s trust task

The user needs to know:

- what the extension does;
- which messages or calls are in scope;
- what happens when the extension is uncertain;
- whether a server is involved and who controls the network handoff;
- how to disable or change the extension;
- how to report or appeal an incorrect result.

Do not market a message filter as reading or controlling the entire inbox. Do not present a classification as truth about a sender.

## Containing-app setup surface

Use a native settings-style screen:

1. Plain-language purpose.
2. Scope: unknown-sender SMS/MMS, or user-started call/SMS reporting.
3. Local versus system-mediated server behavior.
4. Current enabled/disabled state.
5. Model availability and conservative fallback.
6. Link to the relevant system Settings surface.
7. Privacy/support/appeal path.

Show a synthetic test fixture in the containing app if useful, but label it as a preview. A preview cannot prove that the Messages app will launch the extension.

## Message filter decision surface

The extension’s decision vocabulary should be legible:

- Allow
- Junk
- Promotion
- Transaction
- None / not enough information

Subactions should appear as system-defined categories, not as creative AI labels. If the result is uncertain, choose the documented none behavior rather than forcing a category.

The containing app can explain the policy and model confidence, but it should not expose raw message content in logs, analytics, screenshots, or a shared container that the extension cannot use anyway.

## Network deferral is a privacy surface

If the extension defers a query, tell the user:

- the extension cannot contact the server directly;
- the system performs the documented HTTPS request;
- the response returns through the IdentityLookup extension context;
- the associated domain and shared credentials are part of the trust setup.

Avoid a “cloud AI” toggle that implies the extension has ordinary network access. The system-mediated route is a feature boundary and should be documented as such.

## Reporting UI belongs to the user

For SMS/call spam reporting:

- let the system present Cancel and Done;
- use the extension UI only to collect necessary information;
- show why a field is needed;
- enable Done only when the extension context is ready;
- make the resulting action clear;
- do not hide a block/report side effect behind a model suggestion.

The user should see whether they are reporting junk, not junk, or requesting a block. The system’s final presentation and sending flow remain authoritative.

## Live Caller ID design

Caller ID is a high-consequence surface. Separate:

- unknown caller;
- identified caller;
- block recommendation;
- user-controlled blocked list;
- cached result;
- server unavailable;
- extension disabled;
- Settings/configuration stale.

Do not show a confident name when the extension has only a weak or stale dataset. Explain that the system may use cached PIR results and that the user controls extension enablement.

## Liquid Glass and system coherence

Use Liquid Glass in the containing app’s status, setup, or review surfaces. Do not imitate the Messages or Phone UI, and do not style a system-owned extension flow as if it were an in-app modal. Use the platform’s extension template and system lifecycle.

Glass should frame:

- enabled-state status;
- privacy explanation;
- model fallback;
- extension configuration freshness;
- a support/recovery action.

The essential decision must remain readable without blur, translucency, or motion.

## Accessibility and language

Classification and reporting must not depend on color, icon shape, or a hidden confidence meter:

- use visible action names;
- provide VoiceOver labels for category and consequence;
- support Dynamic Type and long translated sender/message labels;
- describe uncertainty in text;
- make Settings, cancel, done, report, and block actions accessible;
- avoid exposing raw phone numbers in accessibility announcements when not necessary;
- use reduced motion for status transitions and extension setup.

## AI boundaries

Useful AI:

- local explanation of why a synthetic fixture received a category;
- a privacy-safe summary of the user’s report before Done;
- a support answer about the extension’s scope;
- a suggestion to default uncertain results to none.

Unsafe AI:

- silently sending message content to a server;
- inventing a filter category;
- automatically reporting or blocking;
- claiming a caller identity from weak evidence;
- replacing system enablement or endpoint validation;
- training on raw extension content without a separate lawful/privacy contract.

## Failure states

Design:

- extension disabled;
- extension not selected because another extension is enabled;
- unsupported iMessage or Contacts message;
- local classifier uncertain;
- system-mediated network unavailable;
- associated-domain/shared-credential misconfiguration;
- report canceled;
- report result unknown;
- extension container reset/deleted;
- Live Caller ID status disabled or stale;
- server dataset/cache unavailable.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [IdentityLookup](https://developer.apple.com/documentation/identitylookup)
- [SMS and MMS Message Filtering](https://developer.apple.com/documentation/identitylookup/sms-and-mms-message-filtering)
- [Creating a Message Filter App Extension](https://developer.apple.com/documentation/identitylookup/creating-a-message-filter-app-extension)
- [SMS and Call Spam Reporting](https://developer.apple.com/documentation/identitylookup/sms-and-call-spam-reporting)
- [IdentityLookupUI](https://developer.apple.com/documentation/identitylookupui)
- [ILClassificationUIExtensionViewController](https://developer.apple.com/documentation/identitylookupui/ilclassificationuiextensionviewcontroller)
- [Getting up-to-date calling and blocking information](https://developer.apple.com/documentation/identitylookup/getting-up-to-date-calling-and-blocking-information-for-your-app)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

***
