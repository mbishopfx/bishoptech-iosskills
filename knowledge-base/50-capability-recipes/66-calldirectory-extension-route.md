# Call Directory extension capability route

Use this route when an app needs to provide caller-ID labels or blocked phone numbers through the system Phone surface. The capability is a dedicated Call Directory extension; the containing app handles source preparation, status, reload, corrections, freshness, and proof.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | Identify selected callers or block selected numbers |
| Containing app | Native SwiftUI setup, source review, correction, freshness, reload, and Settings handoff |
| Extension target | Call Directory Extension with `CXCallDirectoryProvider` |
| System context | `CXCallDirectoryExtensionContext` passed to `beginRequest(with:)` |
| Data | Ordered identification entries and ordered blocking entries keyed by `CXCallDirectoryPhoneNumber` |
| Lifecycle | Full list or incremental delta selected by `context.isIncremental`, then `completeRequest` |
| Manager | `CXCallDirectoryManager.sharedInstance` status, reload, and Settings APIs |
| AI | Optional on-device label/block proposal validated before snapshot emission |
| Liquid Glass | Containing-app status/review surfaces; never a replica of Phone’s system UI |
| Proof | Target compile, full/incremental fixtures, status/reload, signed device, system call/block behavior, accessibility, release artifact |

## 1. Configure targets

1. Add the Call Directory Extension template to the Xcode project.
2. Confirm the extension target’s bundle identifier.
3. Keep the provider implementation in the extension target and the manager/status model in the containing app.
4. Define the source snapshot contract before implementing the provider.
5. Add only the privacy text, capabilities, and entitlements required by the selected product; do not assume a Call Directory extension grants Contacts or network access.

## 2. Define the source snapshot

Use a versioned, deterministic model:

~~~swift
struct CallDirectorySnapshot: Codable, Sendable {
    struct Identification: Codable, Sendable {
        let number: UInt64
        let label: String
    }

    let version: String
    let identifications: [Identification]
    let blockedNumbers: [UInt64]
    let generatedAt: Date
}
~~~

The raw storage representation is an app choice. Before emitting entries, convert the country-code-plus-digits representation to `CXCallDirectoryPhoneNumber`, validate range, remove duplicates, and sort. Keep source provenance and freshness outside the extension’s user-facing label string.

## 3. Choose full versus incremental behavior

The extension does not choose the meaning of the request. Read `isIncremental`:

- false: emit every current identification and blocking entry; do not remove entries;
- true: remove deleted/changed entries and add new/current entries relative to the last system-loaded list.

If the source baseline cannot produce a correct delta, fail the delta build and arrange a full reload path. Do not use a partial list as if it were a full list.

## 4. Keep identification and blocking policies separate

Use separate product policies and proof fixtures:

- Caller ID: display a source-qualified label for a matching number.
- Blocking: prevent the system from showing an incoming call that matches the blocked number.

An AI-suggested label can be reviewed without granting block authority. A user-approved block can exist without a caller-ID label. Do not collapse both lists into a single “spam score.”

## 5. Reload and status flow

The containing app should:

1. Load the extension bundle identifier from configuration.
2. Ask `CXCallDirectoryManager` for `EnabledStatus`.
3. Explain disabled or unknown status and offer `openSettings`.
4. Validate the next snapshot locally.
5. Call `reloadExtension`.
6. Record completion/error category and snapshot version.
7. Re-check status and show the data freshness separately from the system status.

Do not call reload for every view appearance. Debounce user-triggered reloads and schedule source updates according to the product’s data policy.

## 6. AI proposal pipeline

The optional local intelligence route is:

authorized source -> normalization -> local model proposal -> schema/policy validation -> user review or deterministic rule -> snapshot -> extension reload

Validation should reject unsupported labels, invalid numbers, duplicates, low-confidence proposals, and a block action without the required product approval. If the model is unavailable, the source route remains functional or the review queue clearly says “No model proposal.”

## 7. Liquid Glass setup composition

Build a compact containing-app surface with:

- one status card for the extension;
- separate Caller ID and Blocking sections;
- one freshness/source row;
- one Reload action;
- one Open Settings action;
- one review queue for AI proposals;
- one correction/unblock path.

Use native semantic controls, system typography, Dynamic Type, accessibility labels, and reduced-motion behavior. The extension’s system lookup and Phone result are outside this SwiftUI surface.

## 8. Route-specific failure states

Handle at least:

- extension identifier mismatch;
- extension not installed or not selected;
- status unknown/disabled;
- source snapshot unavailable or corrupt;
- duplicate/out-of-order/out-of-range number;
- changed label requiring removal plus addition;
- delta baseline unavailable;
- reload failure and provider request failure;
- stale source data;
- caller-ID label correction;
- user-unblock and extension disable;
- model unavailable or rejected proposal.

## 9. Minimum evidence bundle

Keep these artifacts with the route:

- target and bundle-ID manifest;
- sample full snapshot and incremental diff;
- normalization and ordering tests;
- extension log with redacted counts/version only;
- containing-app status/reload screenshots;
- signed physical-device evidence for enabled state;
- controlled caller-ID and blocked-call results where the test environment permits;
- accessibility and localization check;
- archive/signing/distribution evidence.

## Sources

- [CallKit](https://developer.apple.com/documentation/callkit)
- [Identifying and blocking calls](https://developer.apple.com/documentation/callkit/identifying-and-blocking-calls)
- [CXCallDirectoryProvider](https://developer.apple.com/documentation/callkit/cxcalldirectoryprovider)
- [CXCallDirectoryExtensionContext](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext)
- [isIncremental](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/isincremental)
- [CXCallDirectoryManager](https://developer.apple.com/documentation/callkit/cxcalldirectorymanager)
- [CXCallDirectoryManager.EnabledStatus](https://developer.apple.com/documentation/callkit/cxcalldirectorymanager/enabledstatus)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
