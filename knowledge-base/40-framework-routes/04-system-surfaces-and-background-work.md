# System Surfaces, Documents, and Background Work

## Design for the surface

Widgets, Live Activities, controls, notifications, App Shortcuts, document providers, share extensions, and background tasks are not miniature copies of the app. They are focused system-owned or system-hosted surfaces with limited space, execution time, memory, and user attention. Choose one useful action or piece of status information for each surface, and keep a durable app-owned model behind it.

## Capability route table

| Need | First route | What it actually grants | Proof boundary |
| --- | --- | --- | --- |
| Let a person choose a photo or video | PhotosUI `PhotosPicker` | Selected `PhotosPickerItem` representations | The picker selection, representation load, iCloud/network state, and retention policy are all explicit. |
| Read or edit the photo library | PhotoKit | Access governed by the requested authorization level | Usage description, limited/add-only/full state, change handling, and physical-device permission proof. |
| Open or export a user document | SwiftUI `fileImporter`/`fileExporter`, `DocumentGroup`, or `UIDocumentPickerViewController` | A user-mediated URL or document representation | Security scope, file coordination, format validation, cancellation, and provider availability. |
| Work with an external folder | `UIDocumentPickerViewController` with directory support | Recursive security-scoped access chosen by the user | Balanced scope lifetime, security-scoped bookmark policy, coordinated reads/writes, and revocation handling. |
| Keep a document open and editable | `FileDocument`/`ReferenceFileDocument`, `UIDocument`, or document browser | A document lifecycle and serialization seam | Thread/isolation behavior, conflict/version handling, autosave, migration, and provider interruption. |
| Share a copy, URL, image, or file | `ShareLink`/`Transferable` or `UIActivityViewController` | A system share presentation and representations | Redaction, metadata, large-file loading, cancellation, destination failure, and iPad presentation. |
| Render web content | WebKit `WKWebView` | A browser view with navigation, data-store, and script-bridge choices | Allowed hosts/schemes, redirects, cookies, JavaScript message validation, process termination, and accessibility. |
| View or annotate a PDF | PDFKit `PDFDocument`/`PDFView` | A native PDF model/view and annotation route | Malformed/encrypted files, untrusted content, memory, text selection, accessibility, and export behavior. |
| Show glanceable status | WidgetKit | A separately rendered timeline or interactive configuration | Refresh policy/budget, stale state, shared-container schema, and real Home Screen/Lock Screen proof. |
| Show a current event/progress | ActivityKit plus WidgetKit | A Live Activity lifecycle with local or push updates | Foreground start rules, authorization, push/environment setup, stale/end state, supported surfaces, and device proof. |
| Run focused system action | App Intents, widget controls, or an extension point | A system-invoked action in a constrained process | Intent authorization/confirmation, app/extension state, idempotence, and system-surface evidence. |
| Teach one contextual feature | TipKit | TipKit eligibility, persistence, frequency, and a native tip surface | Tip usefulness, dismissal, feature completion, accessibility, localization, and any shared datastore behavior are separate proof. |
| Refresh or maintain data later | `BGAppRefreshTask`/`BGProcessingTask` | A request the system may run under its scheduling policy | Registration, permitted identifiers, requirements, expiration, resumability, and no guaranteed time claim. |
| Continue a user-started long job | iOS 26 `BGContinuedProcessingTask` | Foreground-started work that may continue after backgrounding | User action, immediate/queued submission, progress, cancellation, resources/entitlement, and physical-device proof. |
| Expose remote files to other apps | File Provider extension | A system-mediated file namespace and sync contract | Extension type, enumerators/items, placeholders, progress/cancellation, server conflict policy, and signing. |

## Choose by ownership and handoff

| Data ownership | Best first seam | Avoid |
| --- | --- | --- |
| App-owned, private, small | App container plus a typed model | Putting source-of-truth records in a widget cache or shared container without need. |
| App-owned, shared with a widget/extension | App Group container or shared defaults with a versioned schema | Assuming both processes can safely mutate the same file without coordination. |
| User-owned file outside the sandbox | Document picker plus a security-scoped URL/bookmark or `UIDocument` | Persisting a raw path or retaining a scope forever. |
| Remote provider-owned file | File Provider/document-provider contract | Treating a placeholder or metadata row as local bytes. |
| User-selected photo/video | PhotosUI transfer representation | Requesting full-library access for a one-off selection. |
| Live status with a clear beginning and end | ActivityKit | Using a widget timeline as a high-frequency live feed. |
| Predictable glanceable values | WidgetKit timeline and explicit reload | Promising the timeline renders at the exact requested instant. |

## Background strategy table

| Requirement | Route | Scheduling truth |
| --- | --- | --- |
| Short, opportunistic refresh | `BGAppRefreshTask` | The system chooses if and when the request runs. Persist a small checkpoint and finish quickly. |
| Maintenance or longer deferred work | `BGProcessingTaskRequest` | Express network/power requirements; the task can be delayed, expired, or terminated. |
| A person taps Export/Process and then backgrounds the app | `BGContinuedProcessingTaskRequest` on supported iOS 26 targets | Submit from the foreground in response to that action. The system can queue, reject, cancel, or terminate it; report progress and make the job resumable. |
| A widget needs a new value | Timeline, `WidgetCenter`, or WidgetKit push | Reloads are budgeted and may be coalesced; widget rendering is not continuous execution. |
| A Live Activity needs current status | ActivityKit local update or APNs ActivityKit push | Live Activities use ActivityKit updates, not widget timelines; stale/end behavior must be modeled. |
| A system event owns the timing | Framework-specific route such as HealthKit, Core Location, audio, Watch Connectivity, or push | Use the framework’s documented entitlement and lifecycle; do not substitute a generic timer. |

## Personal data and health route boundaries

Contacts, EventKit, HealthKit, UserNotifications, Photos, and files deserve separate feature routes even when one app idea combines them:

| Need | Route | Proof boundary |
| --- | --- | --- |
| Choose one person | ContactsUI picker/access button | User-mediated selection and no unnecessary full-store permission. |
| Search/sync contact records | Contacts | Keys-to-fetch, partial records, store changes, retention, and redaction. |
| Create an event/reminder | EventKit/EventKit UI | Write-only/full access, usage descriptions, account/time zone, confirmation, and duplicate prevention. |
| Read/write health data | HealthKit | HealthKit capability, fine-grained authorization, protected-data handling, physical device, and no medical claims from API output. |
| Schedule an attention surface | UserNotifications | Authorization/settings, deterministic identifiers, lock-screen privacy, stale content, and no guaranteed delivery claim. |
| Choose or import a photo | PhotosUI/PhotoKit | Selection versus library authorization, representation load failure, metadata, and retention. |
| Open or save a file | File/document APIs | User intent, security scope, coordinated access, format validation, and provider errors. |

Do not let a notification, widget, App Intent, extension, or background callback silently bypass the underlying data authorization and user-confirmation boundary. External records can change while the app is suspended; validate the record and current permission before showing or writing it.

## Extension and shared-state boundary

An app extension is a separate bundle and process hosted or launched by the system. A share/document extension completes or cancels a host request; a widget renders a snapshot/timeline; an App Intent performs a focused action; a Live Activity presents ActivityKit state; and a File Provider answers system requests for metadata/content. None of these should assume that the main app is running, that a view model exists, or that a long-lived in-memory cache is available.

Use an App Group only when related targets genuinely need shared state. Give the shared data a small versioned schema, explicit ownership, atomic writes or file coordination, lock/privacy rules, and a recovery path for an older or partially written record. Keep secrets and high-value credentials in an appropriate Keychain policy rather than a widget or extension container.

## Verification route

- Test cancellation, no selection, provider refusal, unavailable destination, malformed/oversized input, stale data, revoked access, low storage, no network, and app/extension termination.
- Test iCloud Drive, local files, third-party File Provider services, Photos/iCloud Photos, locked device, low-power mode, and real system surfaces.
- Verify every target separately: bundle identifier, extension point, App Group, document types, usage descriptions, capabilities, entitlements, signing, and deployment target.
- Measure import/export, PDF/WebKit memory, widget refresh behavior, extension launch/termination, task runtime, progress, battery, and cancellation.
- Use Xcode’s background-task debug controls as a development aid only; a debugger launch is not proof that the system will schedule the task normally.
- For iOS 26 continuous background work, verify a person-started action, task progress/cancellation UI, supported resources, expiration, restart/resume, and signed physical-device behavior.

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [SwiftUI presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [UIDocumentPickerViewController](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller)
- [Providing access to directories](https://developer.apple.com/documentation/uikit/providing-access-to-directories)
- [NSURL security-scoped URLs and bookmarks](https://developer.apple.com/documentation/foundation/nsurl)
- [startAccessingSecurityScopedResource](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [NSFilePresenter](https://developer.apple.com/documentation/foundation/nsfilepresenter)
- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [WKScriptMessageHandler](https://developer.apple.com/documentation/webkit/wkscriptmessagehandler)
- [WKContentWorld](https://developer.apple.com/documentation/webkit/wkcontentworld)
- [PDFKit](https://developer.apple.com/documentation/pdfkit)
- [PDFDocument](https://developer.apple.com/documentation/pdfkit/pdfdocument)
- [PDFView](https://developer.apple.com/documentation/pdfkit/pdfview)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [UIActivityViewController](https://developer.apple.com/documentation/uikit/uiactivityviewcontroller)
- [UIActivityItemSource](https://developer.apple.com/documentation/uikit/uiactivityitemsource)
- [NSItemProvider](https://developer.apple.com/documentation/foundation/nsitemprovider)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [Timeline](https://developer.apple.com/documentation/widgetkit/timeline)
- [TimelineProvider](https://developer.apple.com/documentation/widgetkit/timelineprovider)
- [WidgetCenter](https://developer.apple.com/documentation/widgetkit/widgetcenter)
- [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Activity](https://developer.apple.com/documentation/activitykit/activity)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [BGTaskScheduler](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler)
- [BGProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgprocessingtaskrequest)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
- [BGTask expirationHandler](https://developer.apple.com/documentation/backgroundtasks/bgtask/expirationhandler)
- [ExtensionFoundation](https://developer.apple.com/documentation/extensionfoundation)
- [AppExtension](https://developer.apple.com/documentation/extensionfoundation/appextension)
- [Adding support for app extensions](https://developer.apple.com/documentation/extensionfoundation/adding-support-for-app-extensions-to-your-app)
- [NSExtensionContext](https://developer.apple.com/documentation/foundation/nsextensioncontext)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [Replicated File Provider extension](https://developer.apple.com/documentation/fileprovider/replicated-file-provider-extension)
- [Synchronizing files using file provider extensions](https://developer.apple.com/documentation/fileprovider/synchronizing-files-using-file-provider-extensions)
- [Configuring app groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
- [Shared data](https://developer.apple.com/documentation/technologyoverviews/shared-data)
- [App Extension Programming Guide: Document Provider](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/FileProvider.html)
