---
name: ios-system-surfaces-and-background
description: Route, design, implement, or review iOS files/photos, WebKit/PDF, sharing, widgets, Live Activities, app extensions, File Provider, App Groups, and BackgroundTasks including iOS 26 continuous background work. Use when a feature leaves the main app process, touches user-owned documents/media, needs a system surface, or asks for background execution.
---

# iOS System Surfaces and Background

Use this skill to select the narrowest Apple-owned surface and keep user intent, process lifecycle, durable state, privacy, and proof boundaries explicit.

## Read before acting

- Inspect the actual Xcode target, deployment target, platform/device family, scene manifest, extension targets, Info.plist usage descriptions, capabilities, entitlements, App Groups, persistence, and existing system-surface adapters.
- Read the relevant [knowledge-base map](../../../README.md), [system-surface route](../../../40-framework-routes/04-system-surfaces-and-background-work.md), and deep dives for [photos/files/documents](../../../43-system-framework-deep-dives/00-photos-files-and-documents.md), [WebKit/sharing/PDF](../../../43-system-framework-deep-dives/02-webkit-sharing-and-pdf.md), and [extensions/background](../../../43-system-framework-deep-dives/05-extensions-and-background-routes.md).
- Refresh the exact official Apple pages in the Sources section before relying on an API spelling, iOS 26 availability, entitlement, refresh behavior, or extension rule.

## Route workflow

1. State the user outcome and data ownership: app-owned, selected Photos asset, external file, remote provider item, shared projection, live status, or deferred job.
2. Choose the narrowest route: PhotosUI before PhotoKit for one-off selection; SwiftUI document APIs before custom file browsers; ShareLink/Transferable before custom sharing; WebKit only when embedded web content is needed; PDFKit for PDF semantics; WidgetKit for glanceable timelines; ActivityKit for bounded live status; App Intents/extensions for focused system actions; BackgroundTasks for interruptible work.
3. Draw the handoff as `user action -> system picker/surface -> typed input -> validation -> durable checkpoint -> bounded work -> completion|retry|cancel`.
4. List permissions, usage descriptions, document types, extension points, App Groups, capabilities, entitlements, signing, server/APNs needs, and target-device requirements. Mark each as to-verify.
5. Model cancellation, no selection, provider refusal, stale/revoked scope, malformed/oversized data, process termination, no destination, stale widget/Live Activity, task expiration, and retry.
6. Keep shared state minimal and versioned. Use atomic or coordinated writes; keep secrets in Keychain; write redacted projections for widgets/extensions/system surfaces.
7. Verify the smallest target slice first, then test the real system surface and physical device. Report what previews, simulator, signed device, and release evidence each prove.

## Hard boundaries

- Balance every successful `startAccessingSecurityScopedResource()` with `stopAccessingSecurityScopedResource()`.
- Use `NSFileCoordinator`/`NSFilePresenter` or `UIDocument` for external files that can be edited or observed by another process.
- Treat Photos picker items, external URLs, webpage content, PDFs, share representations, provider metadata, widget entries, and push payloads as untrusted or stale until validated.
- A widget timeline is not continuous execution; refresh dates are not exact render guarantees.
- Live Activities use ActivityKit updates, not WidgetKit timelines; model start/update/stale/end separately.
- `BGAppRefreshTask` and `BGProcessingTask` are system-scheduled and interruptible. `BGContinuedProcessingTask` starts from a person’s foreground action and can still be queued, canceled, or terminated.
- An extension is a separate process. Never assume the containing app, navigation stack, main-actor view model, or a long-lived in-memory cache exists.
- Do not claim document availability, widget refresh, background execution, extension delivery, or system UI from a preview or debugger trigger.

## Deliverable

Produce a compact route note with:

- selected framework/surface and rejected alternatives;
- target/extension/process and shared-data boundaries;
- state machine and cancellation/retry/fallback behavior;
- permissions, usage descriptions, document types, capabilities, entitlements, and server dependencies;
- source links and exact proof plan;
- remaining compile, physical-device, system-surface, privacy, signing, and release gaps.

For implementation, change only the requested target and directly related adapters/configuration. Do not add a backend, account, cloud store, analytics, secret, background mode, or entitlement without a stated product need and authorization.

## Related recipes

- [Documents, sharing, extensions, and background recipes](../../../70-code-recipes/19-documents-sharing-extensions-and-background-recipes.md)
- [System-surface checklist](../../../60-verification/05-system-surface-checklist.md)
- [Permission/entitlement/privacy checklist](../../../60-verification/04-permission-entitlement-and-privacy-checklist.md)
- [Build/device/release checklist](../../../60-verification/01-build-device-and-release-checklist.md)

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [UIDocumentPickerViewController](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller)
- [NSURL security-scoped resources](https://developer.apple.com/documentation/foundation/nsurl)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [WebKit](https://developer.apple.com/documentation/webkit)
- [PDFKit](https://developer.apple.com/documentation/pdfkit)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [ExtensionFoundation](https://developer.apple.com/documentation/extensionfoundation)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [Configuring app groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
