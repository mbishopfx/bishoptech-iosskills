# IdentityLookup extension and privacy proof matrix

IdentityLookup evidence must prove the system extension contract, not just a local classifier. The highest-risk errors are treating the API as general inbox access, assuming direct extension networking, or claiming a caller identity without the system/server proof.

## Evidence levels

| Level | Establishes | Does not establish |
| --- | --- | --- |
| Source inspection | Extension points, scope, response vocabulary, system-mediated network and privacy rules | Target enablement, Messages/Phone launch, server validation, user trust |
| Compile | Extension types, principal class, callback signatures, target shape | System query/report delivery, extension status, user action |
| Fixture/unit | Classification mapping, none fallback, response parsing, report form validation | Real SMS/MMS/call launch, system blocking, PIR/cache behavior |
| Simulator | Containing-app setup, synthetic UI, accessibility labels, Settings handoff code | Carrier/SMS/Phone system behavior and extension launch |
| Physical device | Messages/Phone query/report, extension enablement, system actions | Every carrier, region, iMessage/Contacts condition, production scale |
| Signed/TestFlight | Extension embedding, entitlements, associated domains, Info.plist, release configuration | Universal privacy/compliance or server correctness |

## Route matrix

| Claim | Minimum evidence | Failure and recovery cases |
| --- | --- | --- |
| Message Filter extension is enabled | Signed build installs and the user enables it in Settings | Another filter selected, disabled extension, stale setup state |
| Filter receives the intended messages | Physical SMS/MMS from unknown sender triggers query | Contacts sender, iMessage, no service, message never launches extension |
| Local decision works | Known synthetic/approved fixture maps to allow/junk/promotion/transaction/none | Missing body/sender, uncertain model, malformed fixture |
| Filter response is conservative | Insufficient evidence returns none and does not force a category | Model confidence drift, unknown category, timeout |
| Network deferral works | System-mediated request reaches the associated service and ILNetworkResponse is parsed | Direct-network assumption, associated-domain failure, server timeout, invalid response |
| Extension does not leak content | Logs, analytics, shared containers, and crash artifacts contain no raw message data | Debug logging, accidental persistence, model telemetry |
| Reporting extension is launched | User reports an SMS/call from Messages/Phone and the extension view appears | Extension not enabled, unsupported system version, cancel |
| Reporting UI is ready correctly | Done becomes available only after required data is collected | Missing field, premature completion, VoiceOver/focus issue |
| Report action is understood | Classification response produces the expected system report/block flow | User cancels, SMS/network delivery changes, block not confirmed |
| Extension storage assumption is safe | Container reset/deletion is observed and no required state is lost | Process termination, deleted container, restart |
| Live Caller ID works | Signed extension, relay/PIR/server validation, user enablement, caller fixture, and cache behavior are tested | Disabled extension, stale dataset, endpoint failure, token/config refresh |
| Caller identity copy is bounded | UI distinguishes unknown, identified, cached, blocked, and unavailable states | Wrong identity, stale cache, server result interpreted as certainty |
| AI route is safe | Fixed fixture produces typed local proposal; Apple action mapping and none fallback are deterministic | Prompt injection in message body, model unavailable, silent block |
| Accessibility works | Dynamic Type, VoiceOver, localization, system settings, user report, cancel/done, and recovery tasks pass | Color-only category, unreadable content, focus trap |
| Release is ready | TestFlight/signed device confirms extension, privacy, server, and system configuration | Debug-only success, extension not embedded, entitlement/domain drift |

## Environment record

Record:

- app/extension version/build and revision;
- device, OS, carrier/SIM conditions where relevant;
- extension point and enabled extension;
- synthetic test fixture or user-approved physical test;
- message type/sender scope without retaining raw content;
- local/server route and associated-domain configuration;
- system action, cache, report, or block result;
- logs/screenshot artifacts scrubbed of message and phone data;
- accessibility and recovery result;
- signed artifact/TestFlight status.

## Non-claims

Do not infer:

- filter extension = inbox access;
- SMS filter = iMessage filter;
- direct extension networking = supported;
- server response = local model decision;
- classification = factual identity;
- Live Caller ID cache = live truth;
- model confidence = system permission to block/report;
- one device launch = release readiness.

## Sources

- [IdentityLookup](https://developer.apple.com/documentation/identitylookup)
- [SMS and MMS Message Filtering](https://developer.apple.com/documentation/identitylookup/sms-and-mms-message-filtering)
- [Creating a Message Filter App Extension](https://developer.apple.com/documentation/identitylookup/creating-a-message-filter-app-extension)
- [ILMessageFilterQueryHandling](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryhandling)
- [ILMessageFilterQueryRequest](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryrequest)
- [ILMessageFilterQueryResponse](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryresponse)
- [ILNetworkResponse](https://developer.apple.com/documentation/identitylookup/ilnetworkresponse)
- [SMS and Call Spam Reporting](https://developer.apple.com/documentation/identitylookup/sms-and-call-spam-reporting)
- [IdentityLookupUI](https://developer.apple.com/documentation/identitylookupui)
- [ILClassificationUIExtensionViewController](https://developer.apple.com/documentation/identitylookupui/ilclassificationuiextensionviewcontroller)
- [ILClassificationUIExtensionContext](https://developer.apple.com/documentation/identitylookupui/ilclassificationuiextensioncontext)
- [Getting up-to-date calling and blocking information](https://developer.apple.com/documentation/identitylookup/getting-up-to-date-calling-and-blocking-information-for-your-app)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

***
