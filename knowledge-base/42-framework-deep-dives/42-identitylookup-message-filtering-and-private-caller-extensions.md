# IdentityLookup: message filtering, reporting, and private caller extensions

IdentityLookup is an extension-first system surface for unwanted-message filtering, user-initiated SMS/call reporting, and Live Caller ID Lookup. It is not a general Messages inbox API, a general SMS reader, or a license to send message content to an arbitrary server.

The route is:

system query or user report -> constrained extension lifecycle -> local/deterministic decision or system-mediated network response -> system action -> user-facing settings/support surface

Keep the containing app, extension, system Messages/Phone surface, and any server as separate trust and lifecycle boundaries.

## 1. Choose the IdentityLookup route

| Product need | Framework route | Important boundary |
| --- | --- | --- |
| Identify/filter unwanted SMS or MMS | IdentityLookup Message Filter app extension | Only unknown senders; not Contacts or iMessage; extension cannot access the network directly or shared containers |
| Ask a system-mediated server about a filter query | ILMessageFilterExtensionContext and associated server configuration | The system handles communication; associated domains/shared credentials are required for the documented route |
| Let a user report an unwanted SMS or call | IdentityLookupUI Unwanted Communication Reporting extension | User starts the report from Messages/Phone; system owns presentation and final report flow |
| Provide caller ID or call blocking | Live Caller ID Lookup extension | Apple relay/PIR/server validation and extension configuration are required |
| Classify arbitrary messages inside your app | Not an IdentityLookup general-app route | Use an app-owned feature only with content the user supplied and a separate privacy contract |

Start from the system capability and the user’s action. Do not build an inbox clone around these APIs.

## 2. SMS and MMS Message Filtering

The Messages app can launch the currently enabled Message Filter extension for an SMS or MMS from an unknown sender. The system provides an ILMessageFilterQueryRequest containing sender, message body, and receiver country information. The extension adopts ILMessageFilterQueryHandling and returns an ILMessageFilterQueryResponse.

The documented scope is deliberately narrow:

- messages from unknown senders;
- SMS and MMS;
- not messages from a person in Contacts;
- not iMessage messages from any source;
- one currently enabled Message Filter extension;
- system-controlled extension launch and response.

The response has an action such as none, allow, junk, promotion, or transaction, plus a subaction for supported transactional/promotional categories. “None” means the extension lacks enough information and the system may show the message unfiltered. Do not treat a filter decision as a legal, financial, medical, or identity determination.

## 3. Extension privacy and server handoff

For privacy, a Message Filter extension cannot contact a server directly and cannot write to containers shared with the containing app. If the extension cannot decide locally, it can defer the query through ILMessageFilterExtensionContext. The system handles the HTTPS request to the associated server and returns an ILNetworkResponse for the extension to interpret.

The documented creation guide requires:

- a Message Filter Extension target;
- the message-filter extension point;
- Associated Domains for an associated server route;
- shared credentials using messagefilter in the documented configuration;
- extension configuration that names the system-mediated network URL.

This is a very different architecture from “send every message to our backend.” Keep the query, server response, local decision, and final system response visible in diagnostics and privacy documentation.

## 4. SMS and Call Spam Reporting

An Unwanted Communication Reporting extension lets a user report an SMS message or call as junk. The user initiates the report from Messages or Phone. The system instantiates the extension’s IdentityLookupUI view controller, calls prepare(for:), and later calls classificationResponse(for:) when the user chooses Done.

The extension can collect the additional information needed for the user’s report. The system owns the Cancel and Done controls, and the extension marks itself ready through its extension context when it has enough information. The resulting ILClassificationResponse can request no action, report junk, report not junk, or report and block the sender depending on the supported action.

If the report is sent to a network endpoint or by SMS, the extension’s configuration and associated-domain/telephony route determine the system-managed delivery. A report response is not a direct API to silently block or message a person.

Apple’s documentation also states that the system deletes the extension’s container after the extension terminates. Do not design durable user data storage inside the reporting extension as if it were a normal app process.

## 5. Live Caller ID Lookup

Live Caller ID Lookup provides caller ID and call-blocking information through a dedicated extension and a server route. The system uses Apple relay servers and Private Information Retrieval to query the provider’s dataset while protecting the incoming phone number and client network details. Endpoint validation and server configuration are required.

The extension supplies a LiveCallerIDLookupExtensionContext with a service URL, token issuer URL, and user-tier token. LiveCallerIDLookupManager can report extension status, open Settings, reset the extension registration, and refresh PIR parameters.

Treat this as a high-sensitivity system route:

- use only the documented extension/server architecture;
- do not log raw phone numbers;
- do not claim that a cached response is live truth;
- distinguish caller identity, block recommendation, and user action;
- verify user enablement and status;
- document the server dataset and retention behavior.

## 6. On-device AI boundary

AI may help with local message-filter classification if the selected extension target supports the model and the feature is compatible with extension constraints. Keep the model optional and bounded:

- use a typed local classification result;
- default to none when confidence or capability is insufficient;
- preserve the system’s supported action/subaction vocabulary;
- do not invent a new category;
- never send message content to a server outside the documented system-mediated route;
- do not let a model silently block, report, or expose message content.

For a user-initiated report, AI can help summarize the information the user supplied, but the user and system-owned Done/Cancel flow remain authoritative. For Live Caller ID, AI does not replace PIR, server authentication, extension status, or the system’s displayed result.

## 7. Containing app and extension composition

The containing app can provide:

- setup instructions and Settings handoff;
- local model/policy configuration where permitted;
- privacy explanation;
- enablement status;
- test fixtures that do not contain real messages or numbers;
- a support and appeal path.

The extension should do the minimum work required by its system callback. Do not assume the extension can launch the containing app, access its shared database, or perform arbitrary background work. Keep extension code small, deterministic, and resilient to termination.

## 8. Native and Liquid Glass design

The containing app can use a native settings/status surface:

- extension enabled or disabled;
- last configuration refresh;
- supported categories;
- local model availability;
- privacy explanation;
- test mode with synthetic fixtures;
- link to system Settings.

Use Liquid Glass for a compact status or review sheet, not to imitate the Messages or Phone app. System-owned query/report views should follow the system’s lifecycle and controls. Always provide visible explanation, accessibility labels, and a conservative fallback.

## 9. Availability and proof

IdentityLookup is extension and system-surface dependent. Record:

- target and extension point;
- currently enabled extension state;
- SMS/MMS unknown-sender fixture versus unsupported iMessage/Contacts case;
- local decision and none/allow/junk/promotion/transaction response;
- system-mediated network deferral and associated-domain configuration;
- reporting Cancel/Done/readiness and container deletion behavior;
- Live Caller ID extension status, PIR/server validation, cache, and Settings handoff;
- model availability, confidence fallback, and privacy boundary;
- accessibility and user-facing copy;
- signed device/TestFlight/system evidence.

## Sources

- [IdentityLookup](https://developer.apple.com/documentation/identitylookup)
- [SMS and MMS Message Filtering](https://developer.apple.com/documentation/identitylookup/sms-and-mms-message-filtering)
- [Creating a Message Filter App Extension](https://developer.apple.com/documentation/identitylookup/creating-a-message-filter-app-extension)
- [ILMessageFilterExtension](https://developer.apple.com/documentation/identitylookup/ilmessagefilterextension)
- [ILMessageFilterExtensionContext](https://developer.apple.com/documentation/identitylookup/ilmessagefilterextensioncontext)
- [ILMessageFilterQueryRequest](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryrequest)
- [ILMessageFilterQueryHandling](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryhandling)
- [ILMessageFilterQueryResponse](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryresponse)
- [ILMessageFilterAction](https://developer.apple.com/documentation/identitylookup/ilmessagefilteraction)
- [ILMessageFilterSubAction](https://developer.apple.com/documentation/identitylookup/ilmessagefiltersubaction)
- [ILNetworkResponse](https://developer.apple.com/documentation/identitylookup/ilnetworkresponse)
- [SMS and Call Spam Reporting](https://developer.apple.com/documentation/identitylookup/sms-and-call-spam-reporting)
- [ILClassificationRequest](https://developer.apple.com/documentation/identitylookup/ilclassificationrequest)
- [ILCallClassificationRequest](https://developer.apple.com/documentation/identitylookup/ilcallclassificationrequest)
- [ILClassificationResponse](https://developer.apple.com/documentation/identitylookup/ilclassificationresponse)
- [IdentityLookupUI](https://developer.apple.com/documentation/identitylookupui)
- [ILClassificationUIExtensionViewController](https://developer.apple.com/documentation/identitylookupui/ilclassificationuiextensionviewcontroller)
- [ILClassificationUIExtensionContext](https://developer.apple.com/documentation/identitylookupui/ilclassificationuiextensioncontext)
- [Getting up-to-date calling and blocking information](https://developer.apple.com/documentation/identitylookup/getting-up-to-date-calling-and-blocking-information-for-your-app)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

***
