# Call Directory: caller identity and blocking through an extension

Call Directory is the CallKit route for adding caller-ID labels and blocked phone numbers to the system Phone experience. It is an app-extension contract, not a VoIP provider, not a per-call web lookup API, and not general access to call audio, message content, or the user’s full call history.

The route is:

containing app data -> ordered extension snapshot or delta -> Call Directory manager reload -> system Phone lookup -> label or block decision

Keep the containing app, Call Directory extension, Phone/system lookup, source dataset, and optional on-device model as separate boundaries.

## 1. Choose the CallKit route

| Product need | Route | Boundary |
| --- | --- | --- |
| Identify a caller by number | Call Directory app extension with CXCallDirectoryProvider | The system matches a number and displays the supplied label; the label is not proof of identity. |
| Block known numbers | Call Directory app extension with blocking entries | The system telephony provider blocks a matching number; the extension does not inspect the call or decide after ringing. |
| Provide VoIP calling UI and lifecycle | CXProvider, CXProviderDelegate, and the appropriate PushKit/APNs route | This is a separate communication-provider product and should not be conflated with Call Directory. |
| Perform a live server lookup for each incoming call | Not a supported beginRequest pattern | The extension is launched to load data, not called for every individual call; prepare the dataset before reload. |
| Let a user report or filter messages | IdentityLookup / IdentityLookupUI | Message filtering and unwanted-communication reporting have different extension points and privacy boundaries. |

Start with the system capability. If the desired behavior needs audio, call state, a live network decision, or a custom in-call surface, select another CallKit route.

## 2. Extension target and lifecycle

Create a Call Directory Extension target from the Application Extension templates. Its principal object subclasses CXCallDirectoryProvider and overrides beginRequest(with:).

The system passes a CXCallDirectoryExtensionContext to the provider. Do not construct the context yourself. Use the context to add or remove entries, set a failure delegate when useful, and complete the request. The extension is launched to prepare a stored directory; it is not a general-purpose background process.

The containing app is responsible for preparing a safe, bounded data source and asking CXCallDirectoryManager to reload the extension. The extension should read a stable snapshot, not start an unbounded synchronization job. If the snapshot is missing or invalid, fail conservatively and expose recovery in the containing app rather than loading guessed labels or blocks.

## 3. Identification and blocking entry streams

There are two distinct entry types:

- Identification maps a CXCallDirectoryPhoneNumber to a label. When the system finds a matching number, it can display that label for the incoming call.
- Blocking adds a CXCallDirectoryPhoneNumber to the extension’s blocked set. A match is treated as blocked by the system telephony provider.

CXCallDirectoryPhoneNumber is a country calling code followed by a sequence of digits. The input is not a formatted display string, a contact identifier, or an arbitrary text key. Normalize numbers in the containing app, reject ambiguous or out-of-range values, and keep one canonical numeric representation for diffing and proof.

The add APIs are named addIdentificationEntry(withNextSequentialPhoneNumber:label:) and addBlockingEntry(withNextSequentialPhoneNumber:). Apple’s examples sort the phone numbers before adding them. Treat each stream as an ordered, monotonically increasing sequence: sort, deduplicate, validate against CXCallDirectoryPhoneNumberMax, then emit. Keep identification and blocking ordering checks independent.

An identification label is app-provided display data. It may be stale, disputed, or wrong if the source dataset is wrong. In product copy, say “provided caller label” or “directory match” when that distinction matters; do not present a label as government identity, account ownership, or verified caller intent.

## 4. Full reloads and incremental reloads

Read context.isIncremental before mutating the directory:

| Context value | Allowed operation | Implementation rule |
| --- | --- | --- |
| true | Add and remove entries relative to the last system-loaded data | Emit only the delta. Use phone-number removal methods for deleted or changed entries. |
| false | Add the complete identification and blocking lists | Do not remove entries. Rebuild both complete ordered streams. |

The removal methods are only for an incremental request. Calling removeIdentificationEntry(withPhoneNumber:), removeBlockingEntry(withPhoneNumber:), removeAllIdentificationEntries(), or removeAllBlockingEntries() during a non-incremental request violates the documented contract.

Persist a source snapshot version in the containing app so you can compute deltas before requesting a reload. Treat the system’s incremental request as authoritative about its current basis. If the app has lost the source baseline, changed its normalization rules, or cannot prove that a delta is relative to the last loaded data, make the next reload a full rebuild by allowing the system to request a non-incremental load and emitting the complete validated list.

For a changed label, remove the old identification entry and add the new label in the incremental path. A removal targets all identification entries for the number, so do not rely on multiple labels for one number as a durable versioning mechanism.

## 5. Completion and failure handling

Call completeRequest(completionHandler:) after the extension has emitted its valid data. The completion callback reports whether the request completed successfully; the context delegate’s requestFailed(for:withError:) receives a failed request.

Record a redacted diagnostic containing the extension version, source snapshot version, request mode, entry counts, validation result, and error category. Do not log raw phone numbers or labels that are sensitive in the product’s domain. A successful completion proves the extension answered the request; it does not prove that a later incoming call matched the expected number.

Keep failure recovery explicit:

- invalid or unsorted data: reject the snapshot and surface a repair path;
- missing source snapshot: use a safe empty/full-list policy that matches the selected request mode;
- extension disabled: show status and a Settings handoff;
- reload failure: retain the prior known state and show when the next retry is eligible;
- stale data: expose the snapshot timestamp and source freshness, not a false “live” badge.

## 6. CXCallDirectoryManager belongs in the containing app

Use CXCallDirectoryManager.sharedInstance to manage the extension:

- getEnabledStatusForExtension(withIdentifier:completionHandler:) reports unknown, disabled, or enabled;
- reloadExtension(withIdentifier:completionHandler:) asynchronously asks the system to reload the named extension and has an async throwing form;
- openSettings(completionHandler:) opens the Call Blocking & Identification Settings surface.

The bundle identifier supplied to the manager must identify the extension target, not an arbitrary containing-app route. Treat status, reload completion, and actual Phone behavior as separate observations. A reload that succeeds does not mean the user has enabled the extension, a number exists in the supplied dataset, or a physical call has matched it.

## 7. Network, privacy, and data provenance

The Apple guide explicitly notes that Call Directory is loaded when the extension launches, not once for each call. Therefore, a provider should not try to call a web service at the moment an incoming call arrives. Fetch or compute the directory in a permitted containing-app workflow, validate it, store a snapshot through the architecture selected for the extension, and then request a reload.

The directory can be a sensitive dataset. Define:

- why each number is included;
- whether a label is user-entered, business-published, or model-suggested;
- how stale or disputed records are removed;
- who can trigger blocking;
- how long the source and derived snapshot remain;
- which diagnostics are redacted;
- how the user disables the extension and requests correction.

Do not imply that the extension can read the user’s Contacts database, inspect call audio, see the reason a person called, or contact a server on every call. Those are separate capabilities and permissions.

## 8. On-device AI as a bounded proposal layer

An on-device model can help rank or propose labels from data the user or product is authorized to use. Keep the authoritative pipeline deterministic:

1. normalize and validate the phone number;
2. identify the source and freshness of the candidate record;
3. ask the model for a typed label proposal or block recommendation;
4. reject unsupported labels, low confidence, duplicate keys, and numbers outside range;
5. require an explicit product policy or user review before adding a block;
6. emit only the validated ordered Call Directory entries;
7. record the model version and decision reason without storing raw sensitive input.

Never let a model invent a label, silently block a number because it “looks suspicious,” or replace the user’s correction path. A missing or unavailable model should leave the deterministic dataset usable, or result in an explicit no-op—not a hidden network fallback.

## 9. Native and Liquid Glass containing-app design

The system Phone and Settings surfaces are Apple-owned. The containing app should use native SwiftUI controls for:

- extension enabled status and Settings handoff;
- last successful reload and snapshot freshness;
- separate caller-ID and blocking counts;
- source provenance and correction actions;
- model availability and review queue;
- a synthetic test-number fixture;
- accessibility and privacy explanations.

Liquid Glass can frame a compact status card, review sheet, or recovery action in the containing app. Do not recreate Phone’s caller UI or imply that a glass card is the system’s match result. Keep the number, label, last updated time, and consequence readable without blur or motion, and support Dynamic Type, VoiceOver, Reduce Motion, and localized long labels.

## 10. Verification boundary

Prove the route in layers:

- source normalization and ordered stream unit tests;
- provider compilation in the extension target;
- full and incremental fixture requests;
- manager status/reload/settings behavior in the containing app;
- signed device installation with the extension enabled;
- a physical incoming-call fixture with a controlled test number, where permitted;
- blocked-number behavior and the user’s ability to disable it;
- stale, malformed, duplicate, changed-label, and missing-data recovery;
- accessibility tasks and long/localized labels;
- release signing, target membership, privacy text, and distribution evidence.

Do not mark caller-ID or blocking “working” from a sorted array, a successful reload callback, a simulator preview, or an extension compile alone.

## Sources

- [CallKit](https://developer.apple.com/documentation/callkit)
- [Identifying and blocking calls](https://developer.apple.com/documentation/callkit/identifying-and-blocking-calls)
- [CXCallDirectoryProvider](https://developer.apple.com/documentation/callkit/cxcalldirectoryprovider)
- [beginRequest(with:)](https://developer.apple.com/documentation/CallKit/CXCallDirectoryProvider/beginRequest%28with%3A%29)
- [CXCallDirectoryExtensionContext](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext)
- [isIncremental](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/isincremental)
- [addIdentificationEntry(withNextSequentialPhoneNumber:label:)](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/addidentificationentry%28withnextsequentialphonenumber%3Alabel%3A%29)
- [addBlockingEntry(withNextSequentialPhoneNumber:)](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/addblockingentry%28withnextsequentialphonenumber%3A%29)
- [removeIdentificationEntry(withPhoneNumber:)](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/removeidentificationentry%28withphonenumber%3A%29)
- [removeBlockingEntry(withPhoneNumber:)](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/removeblockingentry%28withphonenumber%3A%29)
- [CXCallDirectoryExtensionContextDelegate](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontextdelegate)
- [CXCallDirectoryManager](https://developer.apple.com/documentation/callkit/cxcalldirectorymanager)
- [CXCallDirectoryManager.EnabledStatus](https://developer.apple.com/documentation/callkit/cxcalldirectorymanager/enabledstatus)
- [reloadExtension(withIdentifier:completionHandler:)](https://developer.apple.com/documentation/callkit/cxcalldirectorymanager/reloadextension%28withidentifier%3Acompletionhandler%3A%29)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
