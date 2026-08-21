# Discovery, Handoff, and Preview Services

TipKit, Spotlight, Handoff, and Quick Look make an app feel native by letting the system help a person discover a feature, find a record, continue work on another device, or inspect a file. They are projections of app-owned state. Keep the source record, system index/activity/preview, and user action separate.

## Route matrix

| User outcome | First route | Target/configuration boundary | Proof that matters |
| --- | --- | --- | --- |
| Teach a non-obvious feature in context | TipKit: `Tip`, `TipView`, `TipGroup`, `Rule`, `Parameter`, `Tips.configure()` | App target, persistent TipKit datastore, rule/parameter/event design, localization, and feature state | Physical task test that the tip appears only when useful, dismisses/resets correctly, respects accessibility, and does not become advertising or a tutorial overlay. |
| Make private records searchable on-device | Core Spotlight: `CSSearchableIndex`, `CSSearchableItem`, `CSSearchableItemAttributeSet` | Index choice/protection class, privacy/retention, stable IDs, content attributes, expiration, deep-link routing, and deletion policy | Create/edit/delete/index failure, locked/protected data, stale ID, ranking uncertainty, search result selection, and revalidation in the app. |
| Make typed app entities discoverable to system features | App Intents `AppEntity`/`EntityQuery` and indexed entities | Stable entity identity, display representation, query authorization, supported system surface, stale/deleted resolution, and mutation confirmation | Spotlight/Siri/Shortcuts/system-intelligence invocation from a terminated app and safe failure for missing or unauthorized entities. |
| Continue an in-progress activity on another device | `NSUserActivity`, SwiftUI `userActivity(_:element:_:)`, Handoff, and scene/user-activity restoration | `NSUserActivityTypes` in `Info.plist`, activity type schema, Team ID/signing for cross-platform Handoff, supported devices, and deep-link/reconciliation route | Two physical devices with the same signed product, current activity updates, handoff accept/fail/expire, account switch, deleted record, and no private data leak. |
| Preview documents, media, PDFs, or USDZ files | Quick Look: `QLPreviewController`, `QLPreviewItem`, `PreviewItem`, `PreviewApplication` | File URL/security scope, UTType support, preview/editing policy, UIKit/SwiftUI bridge, platform behavior, and optional preview extension | Real file types and malformed/large files, preview/edit callback, user cancellation, edited-copy persistence, accessibility, and target platform. |
| Provide a custom preview for an app-owned type | Quick Look preview extension with `QLPreviewingController` or `QLPreviewProvider`/`QLPreviewReply` | Separate extension target, `QLSupportedContentTypes`, preview process/time/resource limits, safe file access, and content-type declaration | Host invocation, supported/unsupported type, extension termination, file scope, render failure, and physical-system preview. |

## TipKit design contract

TipKit is for concise contextual feature discovery. Apple explicitly cautions against using tips as advertising, promotion, or a step-by-step app tutorial. Define a tip around a user action the person can perform now:

```text
feature exists -> context becomes eligible -> tip shown
tip dismissed/invalidated -> feature state changes -> tip stays quiet
```

Configure TipKit once at app launch and model configuration failure. Use `@Parameter` and `Rule` for meaningful app state, `Event` for repeated behavior, and `TipGroup` when a small set of tips must be sequenced or limited. Make the feature usable without the tip, localize the title/message, and ensure custom placement does not obscure controls, Dynamic Type, VoiceOver focus, reduced motion, or reduced transparency.

Do not use a tip impression as proof that the person understood the feature. Measure completion through deterministic app state or an explicit action, and reset the TipKit datastore only in development/test fixtures unless the product has a deliberate reset policy.

## Search and entity indexing contract

Index a small, reviewable projection:

`authorized source record -> redacted searchable attributes/entity -> system result -> stable ID -> current authorization/revalidation -> app route`

Use `CSSearchableIndex` for an app-owned on-device index. A custom index can carry a data-protection class; choose the index and metadata based on the sensitivity of the content. Include stable identifiers, display text, content type, an expiration date where appropriate, and a deep-link route. Keep indexing and deletion idempotent and retryable. When a record is edited or deleted, update or remove every representation, including an `AppEntity` index if both routes are used.

Spotlight ranking and presentation are system-controlled. An indexed item is not guaranteed to appear, and a result selection does not authorize access to the record. Re-resolve the identifier against the current account, protected-data state, schema version, and retention policy before displaying or mutating anything.

## Handoff and user-activity contract

`NSUserActivity` describes what the person is doing at a moment, not a serialized private database row. Keep its payload small and reconstructible:

| Field | Rule |
| --- | --- |
| `activityType` | Reverse-DNS identifier declared in `NSUserActivityTypes`. |
| `title`/`keywords` | Human-readable, localized discovery text with no secret payload. |
| `targetContentIdentifier`/`appEntityIdentifier` | Stable ID resolved through current app authorization. |
| `webpageURL` | A safe fallback/associated route when the product supports it; validate host/path. |
| `userInfo` | Minimal versioned context; never treat it as trusted authorization. |
| `expirationDate` | Stop offering stale work. |
| eligibility flags | Opt into Handoff/search/prediction only for activity that is appropriate and privacy-reviewed. |

Call `becomeCurrent()` when the activity is actually current and `resignCurrent()`/`invalidate()` when it is no longer relevant. On receipt, treat the activity as an invocation request: parse, resolve, authorize, restore, and show a recoverable unavailable state. Cross-platform Handoff requires the corresponding apps to share the developer Team ID and signing relationship; this is a release/configuration boundary, not a SwiftUI navigation feature.

## Quick Look trust and editing boundary

Quick Look is a system preview/editor surface, not a domain model. Before presenting, validate that the URL is in scope, the security-scoped access is active, the UTType is expected, and size/resource limits are acceptable. `QLPreviewController` uses a data source of `QLPreviewItem`s; the system may edit supported previews and report updates through its delegate. Treat every edited URL/copy as a new artifact, validate it, and persist it only after the product’s save/replace policy succeeds.

For a custom file type, choose a view-based `QLPreviewingController` or data-based `QLPreviewProvider`/`QLPreviewReply` extension. Declare the supported content types in the extension’s `Info.plist`. Keep the preview process independent from the app’s canonical record and handle host/extension termination, malformed input, missing files, and unsupported platform behavior.

## Shared lifecycle and privacy state

```text
unconfigured -> configuring -> ready | configurationFailed
sourceChanged -> projecting -> indexed/current | stale | deleted | projectionFailed
activityIdle -> current -> offered -> restored | rejected | expired | unavailable
fileSelected -> scopeChecked -> preparing -> previewing
previewing -> editedCopy | saved | cancelled | unsupported | failed
```

Record source ID, account, schema, data-protection/lock state, freshness/expiry, system surface, process/extension, and last error. Do not put health, message, precise location, credentials, or unreviewed AI output into a tip, searchable projection, Handoff payload, Quick Look metadata, or log unless the product’s privacy contract explicitly requires it.

## Verification matrix

| Evidence level | Checks |
| --- | --- |
| Source/configuration | Current SDK signatures/availability, TipKit configuration, `Info.plist` activity types, Handoff/associated-domain/signing requirements, index protection, UTType/Quick Look extension declarations, target membership, and privacy strings. |
| Deterministic test | Tip eligibility/reset, index upsert/delete, entity resolution, activity version migration, deep-link validation, preview URL scope, edited-copy validation, and projection failure. |
| Simulator/preview | Tip placement and UI states, search/deep-link fixtures, handoff state reducer, Quick Look bridge layout, large text/dark mode/reduced effects, and missing/unsupported branches. Label system delivery as simulated. |
| Physical system | Two signed devices for Handoff, actual Spotlight selection, TipKit persistence, lock/protected-data behavior, real Quick Look files/editing, extension termination, VoiceOver, Dynamic Type, and device-family variation. |
| Release | App/extension signing, Team ID/entitlements, `Info.plist` keys, associated domains if used, App Store metadata, privacy declarations, and production behavior only after the exact route is tested. |

## Sources

- [TipKit](https://developer.apple.com/documentation/tipkit)
- [Tip](https://developer.apple.com/documentation/tipkit/tip)
- [Tips](https://developer.apple.com/documentation/tipkit/tips)
- [TipKit rules](https://developer.apple.com/documentation/tipkit/tips/rule)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [CSSearchableIndex](https://developer.apple.com/documentation/corespotlight/cssearchableindex)
- [CSSearchableItem](https://developer.apple.com/documentation/corespotlight/cssearchableitem)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [NSUserActivity](https://developer.apple.com/documentation/foundation/nsuseractivity)
- [Implementing Handoff in your app](https://developer.apple.com/documentation/foundation/implementing-handoff-in-your-app)
- [Quick Look](https://developer.apple.com/documentation/quicklook)
- [QLPreviewController](https://developer.apple.com/documentation/quicklook/qlpreviewcontroller)
- [QLPreviewItem](https://developer.apple.com/documentation/quicklook/qlpreviewitem)
- [QLPreviewingController](https://developer.apple.com/documentation/QuickLookUI/QLPreviewingController)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
