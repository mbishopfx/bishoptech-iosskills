# IdentityLookup message-filter and caller-ID capability route

Use this route for a system extension that filters unknown-sender SMS/MMS, receives user-initiated unwanted-communication reports, or provides Live Caller ID Lookup. Keep the three products separate; they have different launchers, data, server, and proof boundaries.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | Reduce unwanted messages, report a communication, or identify/block a caller |
| System surface | Messages, Phone, Settings, and an Apple extension point |
| Framework | IdentityLookup; IdentityLookupUI for reporting UI |
| Local route | Message filter logic using the query request and response vocabulary |
| Network route | System-mediated message-filter server or Live Caller ID PIR/relay route |
| Domain state | Extension enabled state, query/report state, result, uncertainty, configuration freshness |
| UI | Containing-app setup/support surface; system-owned query/report UI |
| AI | Optional local proposal/explanation with none/allow fallback |
| Proof | Signed extension, system launch, synthetic/physical message/call, privacy/server/configuration evidence |

## Step 1: Choose one extension product

### Message Filter

Add the Message Filter Extension template. Implement ILMessageFilterExtension and ILMessageFilterQueryHandling. Handle only the query request supplied by Messages and return a typed ILMessageFilterQueryResponse.

### Unwanted Communication Reporting

Add the IdentityLookupUI extension route. Subclass ILClassificationUIExtensionViewController, collect only the information required for the user’s report, set readiness through the extension context, and return an ILClassificationResponse.

### Live Caller ID Lookup

Use the Live Caller ID Lookup extension and its server/PIR configuration. This route requires Apple relay servers, endpoint validation, user authentication/configuration, and a separately verified dataset.

Do not merge these routes into one “phone intelligence” feature. Their system contracts differ.

## Step 2: Define the scope and vocabulary

For Message Filter, document:

- unknown-sender SMS/MMS only;
- no Contacts messages;
- no iMessage messages;
- allow, junk, promotion, transaction, and none;
- supported transactional/promotional subactions;
- local decision versus deferred system-mediated query.

For reporting, document:

- user starts the action;
- system owns Cancel/Done;
- the user chooses the final report flow;
- network/SMS delivery is system-mediated;
- blocking has a visible consequence.

For Live Caller ID, document caller ID, block result, cache, extension enablement, PIR, relay, and server configuration separately.

## Step 3: Build the extension target

Record:

- containing app target;
- extension target and principal class;
- extension point identifier;
- supported deployment target;
- associated domains/shared credentials if the documented server route is used;
- Info.plist network/SMS report destinations where applicable;
- extension status and Settings handoff.

The extension is a constrained process. Do not depend on shared app containers for the Message Filter route when Apple’s documentation says the extension cannot write to them.

## Step 4: Implement local query handling

For a message filter query:

1. receive ILMessageFilterQueryRequest;
2. validate optional sender/body/country values;
3. run deterministic local rules or a bounded local classifier;
4. map to an Apple-defined action/subaction;
5. return none when evidence is insufficient;
6. complete promptly within the extension lifecycle.

Do not log raw message content. Do not return a custom taxonomy to the system. If local logic cannot decide, use the documented defer-to-network route.

## Step 5: Add the system-mediated server route only when needed

For message filtering, configure the associated domain and shared credentials exactly as the Apple route requires. Ask the extension context to defer the query; let the system contact the server and return ILNetworkResponse. Parse only the documented response contract and return a safe action.

For Live Caller ID, configure the relay/PIR/server contract, token issuer, user-tier token, extension status, cache refresh, and endpoint validation. Do not implement a raw direct call from the extension.

## Step 6: Implement user reporting

The reporting extension should:

1. receive prepare(for:);
2. show the minimum additional fields;
3. set isReadyForClassificationResponse when complete;
4. return the appropriate classification response;
5. let the system own sending, blocking, cancellation, and dismissal.

Test the user cancel path and the container deletion/reset behavior.

## Step 7: Add bounded on-device AI

Use a typed local result:

message snapshot -> local classifier -> confidence/uncertainty -> Apple action/subaction -> system response

The model can help with an explanation or proposal, but it must not:

- send content outside the documented system route;
- invent categories;
- automatically block/report;
- claim identity;
- bypass extension enablement;
- persist raw extension content.

## Step 8: Build the containing-app surface

Show:

- setup scope;
- enablement status;
- local/server privacy path;
- model availability;
- test fixture;
- system Settings handoff;
- support/appeal route.

Use native SwiftUI and restrained Liquid Glass. The system-owned Messages/Phone flow remains the source of truth.

## Step 9: Proof gates

Verify:

- signed extension installation and enablement;
- unknown-sender SMS/MMS query;
- Contacts/iMessage exclusion;
- local action/subaction and none fallback;
- system-mediated server deferral and response;
- reporting UI readiness, cancel, done, report, and block behavior;
- Live Caller ID status/PIR/cache/Settings route where supported;
- no direct extension network or shared-container assumption;
- AI uncertainty and privacy fallback;
- accessibility, Dynamic Type, localization, and system-surface behavior;
- TestFlight and production configuration.

## Sources

- [IdentityLookup](https://developer.apple.com/documentation/identitylookup)
- [SMS and MMS Message Filtering](https://developer.apple.com/documentation/identitylookup/sms-and-mms-message-filtering)
- [Creating a Message Filter App Extension](https://developer.apple.com/documentation/identitylookup/creating-a-message-filter-app-extension)
- [ILMessageFilterQueryHandling](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryhandling)
- [ILMessageFilterQueryRequest](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryrequest)
- [ILMessageFilterQueryResponse](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryresponse)
- [ILMessageFilterExtensionContext](https://developer.apple.com/documentation/identitylookup/ilmessagefilterextensioncontext)
- [ILNetworkResponse](https://developer.apple.com/documentation/identitylookup/ilnetworkresponse)
- [ILMessageFilterAction](https://developer.apple.com/documentation/identitylookup/ilmessagefilteraction)
- [ILMessageFilterSubAction](https://developer.apple.com/documentation/identitylookup/ilmessagefiltersubaction)
- [SMS and Call Spam Reporting](https://developer.apple.com/documentation/identitylookup/sms-and-call-spam-reporting)
- [IdentityLookupUI](https://developer.apple.com/documentation/identitylookupui)
- [ILClassificationUIExtensionViewController](https://developer.apple.com/documentation/identitylookupui/ilclassificationuiextensionviewcontroller)
- [ILClassificationUIExtensionContext](https://developer.apple.com/documentation/identitylookupui/ilclassificationuiextensioncontext)
- [ILClassificationResponse](https://developer.apple.com/documentation/identitylookup/ilclassificationresponse)
- [Getting up-to-date calling and blocking information](https://developer.apple.com/documentation/identitylookup/getting-up-to-date-calling-and-blocking-information-for-your-app)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

***
