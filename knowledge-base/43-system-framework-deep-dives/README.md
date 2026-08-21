# System Framework Deep Dives

These routes cover Apple system data, files, companion surfaces, and extensions. They are especially useful when an app should feel native because the system already provides the right picker, sharing surface, notification mechanism, or companion experience.

## Deep dives

- [Photos, files, and documents](00-photos-files-and-documents.md)
- [Photos, Files, documents, File Provider, Quick Look, and PDF authority](10-photos-files-documents-and-file-provider.md)
- [Contacts, Calendar, and notifications](01-contacts-calendar-and-notifications.md)
- [Contacts, EventKit, and User Notifications](08-contacts-eventkit-and-notifications.md)
- [WebKit, sharing, and PDF](02-webkit-sharing-and-pdf.md)
- [WeatherKit and system data](03-weatherkit-and-system-data.md)
- [Watch, CarPlay, and App Clips](04-watch-carplay-and-app-clips.md)
- [Extensions and background routes](05-extensions-and-background-routes.md)
- [System-surface and extension composition](06-system-surface-and-extension-composition.md)
- [Family Controls, Device Activity, and Managed Settings](07-family-controls-device-activity-managed-settings.md)
- [Background Tasks and continued processing](09-background-tasks-and-continued-processing.md)

## Route rule

System integration is a contract with the OS and the person using it. Prefer the system surface, ask for access in context, share the minimum data, handle the process/lifecycle boundary, and prove the behavior on the actual target surface.

## T058 route register

| Route | API/target focus | Lifecycle/privacy focus | Proof boundary |
| --- | --- | --- | --- |
| Photos, files, documents, and providers | PhotosUI/PhotoKit, `fileImporter`/`fileExporter`, `FileDocument`/`DocumentGroup`, security-scoped URLs, File Provider | User-selected scope, file coordination, provider process, redaction, import/export versioning | Real Files/Photos/share flow, permissions, large/corrupt inputs, provider/network behavior, signed target. |
| Contacts, Calendar, and notifications | Contacts picker/store, EventKit, UserNotifications, APNs | Staged authorization, external-store change state, local/remote notification acceptance versus presentation | Physical permission/settings state, store/account behavior, notification action/deep link, APNs/provider delivery separately. |
| WebKit, sharing, and PDF | `WKWebView`/bridge/download, `ShareLink`/`Transferable`, `PDFDocument`/`PDFView` | Web process and origin trust, immutable export snapshots, provider/file lifetime, malformed/encrypted PDF handling | Host/bridge policy, process restart, real destination, accessibility/text/annotation, output validation. |
| WeatherKit and system data | `WeatherService`, `WeatherQuery`, Core Location adapter, attribution/metadata | Service freshness/availability, location permission, dataset partiality, widget/companion projection | Real entitlement/service/device route, stale/offline/denied data, attribution at every surface. |
| Watch, CarPlay, and App Clips | `WCSession`, CarPlay scene/templates, App Clip invocation/association | Separate target/process, pairing/reachability, vehicle attention, invocation validation, full-app handoff | Two physical devices, real vehicle/system, AASA/experience/App Store configuration, no-URL/offline paths. |
| Extensions and background routes | ExtensionKit, File Provider, WidgetKit, ActivityKit, notification extensions, `BG*Task` APIs | Host/extension lifetime, App Group protocol, budget/scheduling, checkpoint/idempotence, APNs/server state | Actual extension/system invocation, termination/expiration/cancellation, physical resource behavior, signed artifacts. |
| System-surface composition | Versioned projections, deep links, bounded intent/action results, fallback routes | Cross-process ownership, redaction, stale/error/expiry, compile/runtime/physical/release evidence separation | Evidence recorded per target/surface; no surface callback is treated as canonical business completion. |

Every row is a route-planning aid, not a claim that an API is available in every deployment target or that a system surface will deliver on demand. Re-open the linked Apple documentation and inspect the selected Xcode project before implementation.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [User Notifications](https://developer.apple.com/documentation/usernotifications)
- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
