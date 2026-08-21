# SwiftUI UserNotifications, communication notifications, and action review

This review adds a modern SwiftUI composition boundary around UserNotifications, actionable notification types, communication notifications, Focus-aware behavior, notification service/content extensions, APNs, Live Activities, and structured on-device-AI proposals. It complements the existing [contacts, calendar, and notifications deep dive](../43-system-framework-deep-dives/01-contacts-calendar-and-notifications.md), [communication and call system surfaces](../44-system-services/01-commerce-and-communication-surfaces.md), [notification design guide](../21-design-deep-dives/28-communication-and-call-system-surfaces.md), and [system-surface proof checklist](../60-verification/05-system-surface-checklist.md).

It is not an APNs provider, a delivery guarantee, a communication service, a SiriKit implementation, a notification extension template, or proof that a user will see or act on an alert. Apple owns the notification presentation, permission state, Focus behavior, timing, and many extension limits. The app owns its domain record, routing, privacy policy, and truthful recovery.

## The notification route has multiple authorities

Name the authority for every fact before composing a SwiftUI surface:

| Fact or outcome | Primary authority | App-owned projection | Proof boundary |
| --- | --- | --- | --- |
| The person wants a reminder or update | App domain and user settings | Notification intent | Deterministic fixture and user review |
| The app may request notification access | UserNotifications and the person | Authorization state | Physical settings run |
| A notification request is scheduled | UNUserNotificationCenter | Request record and identifier | Pending-request inspection |
| A notification is delivered by APNs | APNs and the device | Transport event | Provider/device trace |
| A notification is shown | The system and user settings | Never assume as app truth | Physical system observation |
| A person selected an action | UNUserNotificationCenter delegate | Typed action event | System action run |
| A communication sender is recognized | SiriKit intent and the system | Communication projection | Intent donation and physical notification |
| Focus permits or delays a notification | System Focus and authorization | Bounded status, if authorized | Focus settings and device run |
| A service extension changed content | Notification service extension | Final content snapshot | Extension log and system presentation |
| A content extension rendered a notification | User Notifications UI extension | Extension view state | Category-matched system run |
| A model suggested a notification | Foundation Models or another local model | Reviewable proposal | Input/revision/model fixture |
| A notification caused a domain mutation | App domain/server | Durable record | Idempotent commit and reconciliation |

Keep the authorities separate:

~~~text
domain event
    -> notification intent
    -> authorization/settings preflight
    -> local request or provider payload
    -> UserNotifications/APNs/system delivery
    -> optional extension transformation
    -> system presentation
    -> user action or dismissal
    -> app route and current-state validation
    -> durable domain mutation
~~~

A successful authorization request, pending request, APNs token, provider response, notification delegate callback, banner, model proposal, or simulator injection is evidence of only that layer. None of those artifacts alone proves delivery, attention, identity, consent, business completion, or user-visible truth.

## Choose the right system surface

Use the narrowest system route that matches the outcome:

| Product need | Primary route | Boundary |
| --- | --- | --- |
| A future reminder or local status | UserNotifications local request | Permission, trigger, identifier, and cancellation |
| A server-originated alert | UserNotifications plus APNs/provider | Token, environment, payload, delivery, and privacy |
| A response without opening the app | Notification category and action | Category registration, action identity, background handling |
| A short typed response | UNTextInputNotificationAction | Locked-device state, text privacy, server/domain reconciliation |
| An incoming direct message or call | Communication notification and SiriKit intent | Intent donation, contact context, Focus status, provider event |
| A bounded payload transformation | UNNotificationServiceExtension | Mutable-content payload, extension time/resource limit |
| A custom expanded notification interface | UNNotificationContentExtension | Separate extension target, category, immediate local data |
| A persistent live event | ActivityKit Live Activity | Content-state schema, supported surface, update/end route |
| A long-form in-app settings or review flow | SwiftUI app view | App-owned UI; do not imitate the system banner |

Do not use a notification as an error dialog, a marketing channel without explicit consent, or a replacement for an in-app record. Do not use a Live Activity when the requirement is a one-time alert, and do not register PushKit for ordinary messages or reminders.

## Target and capability gates

Before writing a SwiftUI view, inspect the named target and signed artifact:

- UserNotifications, UserNotificationsUI, SwiftUI, App Intents, SiriKit Intents, ActivityKit, and any UIKit bridge imports;
- deployment target, SDK/toolchain, platform, and intended device family;
- Push Notifications capability and the signed APS environment entitlement;
- Communication Notifications capability, SiriKit intent declarations, and Focus Status usage description when those routes are actually needed;
- notification service and content extension targets, their bundle identifiers, categories, Info.plist keys, and app-group policy;
- APNs provider topic, environment, authentication method, token registration, payload type, and server logging policy;
- critical-alert entitlement only when the product has the narrow Apple-approved health or safety case;
- Time Sensitive policy and product review for any use of the time-sensitive interruption level;
- privacy manifest, notification preview policy, lock-screen redaction, data retention, and notification-service logging;
- ActivityKit capability, widget extension, push environment, and server topic if the route uses Live Activities;
- Foundation Models availability fallback, model revision, prompt/schema version, and local-data scope;
- archive entitlements, provisioning, version/build, and installed device family.

A capability checkbox or source-level availability annotation is not proof that the signed archive contains the entitlement, that the person granted authorization, that APNs can reach the device, or that an extension will execute.

## Authorization and settings are state, not a Boolean feature flag

Request permission in a context that explains the user value. Ask only for the interaction options the product uses, such as alert, sound, badge, or provisional behavior. Then read UNNotificationSettings after the request and whenever the app returns to the foreground because the person can change alert, sound, badge, lock-screen, notification-center, CarPlay, Focus, and summary behavior outside the app.

Model the important states:

~~~text
notDetermined
    -> requesting
    -> authorized
    -> provisional
    -> ephemeral
    -> denied
    -> restricted
    -> settingsChanged
~~~

Treat the settings object as a snapshot. It reports system configuration at one moment; it does not prove the next notification will be shown. A denied or restricted state should lead to a useful in-app fallback, not a permission loop. A provisional route should explain what the user can expect and should not be represented as full alert authorization.

Keep one authorization/settings owner:

- serialize requests through an app-owned actor or coordinator;
- avoid launching multiple requestAuthorization calls from separate views;
- store only the minimum local preference needed to explain the user’s decision;
- re-read system settings before scheduling a high-value route;
- send the user to the system settings route when a denied state cannot be repaired in-app;
- do not infer a person’s private notification settings from a missing banner.

Assign the UNUserNotificationCenter delegate before app launch finishes if foreground presentation or action handling is needed. Late delegate assignment can miss an incoming notification. In a SwiftUI app, use a small app-delegate bridge or another early lifecycle hook, then forward events into a main-actor store without making the notification center itself the domain model.

## Local requests: content, trigger, identifier

A local notification is a UNNotificationRequest containing editable content and a trigger:

~~~text
stable domain record
    -> notification intent
    -> UNMutableNotificationContent
    -> UNNotificationTrigger
    -> UNNotificationRequest(identifier, content, trigger)
    -> UNUserNotificationCenter.add
~~~

Use a stable app-owned identifier derived from the record and purpose. Replacing or canceling a request must be deliberate. Keep the identifier separate from the user-visible title and do not place mutable business truth only in notification userInfo.

The documented local trigger families are:

- UNCalendarNotificationTrigger for date components and repeating calendar events;
- UNTimeIntervalNotificationTrigger for elapsed-time delivery;
- UNLocationNotificationTrigger for geographic entry or exit;
- no trigger for immediate delivery when the app schedules the request for the system.

When a trigger is repeating, define the product’s timezone, calendar, daylight-saving, and recurrence semantics. A request accepted by the system does not prove exact wall-clock delivery. A location trigger adds location authorization and region-behavior evidence. Use pending-request inspection to reconcile what the app asked the system to hold.

For cancellation and replacement:

1. load the current domain revision;
2. derive the expected request identifiers;
3. remove obsolete pending requests;
4. add the request for the new revision;
5. record the local scheduling result separately from the future delivery claim.

The delivered-notification store is also system state. Removing a delivered notification is not the same as deleting the app-owned record. If an item is already completed, the app can remove or update the notification while preserving the domain history.

## Notification content is a privacy and urgency contract

UNMutableNotificationContent can carry title, subtitle, body, sound, badge, categoryIdentifier, threadIdentifier, attachments, userInfo, targetContentIdentifier, interruptionLevel, relevanceScore, and other documented content. Select each field from the product policy, not from an unconstrained model.

Use threadIdentifier to group related notifications and stable category identifiers to connect a payload to registered actions. Keep userInfo small, typed, versioned, and non-sensitive. Treat userInfo as an untrusted route hint; re-resolve the current record before mutating anything.

Interruption levels have different system meanings:

| Level | Appropriate role | Product warning |
| --- | --- | --- |
| Passive | Useful later, no immediate interruption | Do not use it for a promise that requires prompt attention |
| Active | Default useful update | Still subject to user settings and delivery behavior |
| Time Sensitive | A current event that reasonably needs attention now | Never use for marketing or low-priority engagement |
| Critical | Rare health or safety case with entitlement | Requires Apple entitlement and a narrowly justified policy |

Use relevanceScore as a documented ranking signal for notification summaries, not as a guarantee that a message becomes the featured item. A model must never be allowed to promote an ordinary notification to time-sensitive or critical solely to improve engagement.

Treat preview text as potentially visible on a locked or shared screen. Design a redacted version, avoid confidential content in title/body, and do not rely on an app-only setting to hide a secret once a notification is delivered. The system may also transform, summarize, delay, group, or suppress presentation.

## Actionable notifications are typed background routes

Actionable notifications require categories and actions declared at launch. The category identifier in the local content or APNs aps payload must match a registered category. The action identifier is the only stable selector for the action, even when different categories contain similarly named buttons.

Model the flow:

~~~text
category registration
    -> request payload includes category identifier
    -> system presents available actions
    -> user selects, dismisses, or opens
    -> UNNotificationResponse arrives
    -> action identifier and userInfo are parsed
    -> current domain revision is revalidated
    -> app or server mutation is authorized and committed
    -> completion is called exactly once
~~~

Use UNNotificationAction for bounded commands such as “Accept” or “Mark Done.” Use UNTextInputNotificationAction when a typed response is genuinely useful, such as a short reply. Define destructive, authentication-required, foreground, and other options only when their documented behavior matches the product.

Use a small typed action enum in the app:

~~~text
acceptInvitation
declineInvitation
replyWithText
openRecord
dismissed
defaultOpen
unknown
~~~

Never treat an unknown action identifier as permission to perform a fallback mutation. Parse the notification’s record ID, compare the current revision, and show a conflict or stale-state route when the record changed. A notification can be selected hours after it was generated.

Apple’s actionable-notification guidance notes that a person can respond without launching the app. It also warns that the device may be locked when the action runs. If the action needs protected files, credentials, or current network state, save a bounded pending intent and reconcile it when protected data and account state are available.

Call the delegate completion handler after the action route has reached a bounded state. The completion handler is not a provider receipt and does not mean the user-visible action succeeded in the domain.

## Communication notifications and Focus are identity-sensitive

Communication notifications are for direct communications such as calls and messages. They use contact-oriented context, prominent avatars or group names, and system behavior different from ordinary app updates. The system may use SiriKit intent donations and Focus status to decide how a communication is presented or whether it can break through a Focus.

For a communication route:

1. define the communication participant and direction in the app domain;
2. create the supported SiriKit intent, such as INSendMessageIntent or INStartCallIntent, with current contact context;
3. donate the incoming and outgoing interaction according to Apple’s communication-notification guidance;
4. configure the target capabilities and Info.plist intent declarations;
5. let the notification service extension update notification content from the system-recognized intent;
6. treat Focus status as optional, authorized system context rather than an identity or delivery guarantee;
7. record provider/server message or call state separately from notification presentation.

UNNotificationContentProviding is a system-defined protocol. The system only accepts the Apple SDK types that conform to it; an app cannot make an arbitrary custom object become recognized communication context merely by declaring conformance.

Focus status requires the appropriate capability and user authorization. Handle an unavailable or nil status as unknown. Do not tell another person that someone is “ignoring” them because the app could not read Focus status, and do not expose private Focus state beyond the documented communication feature.

Marketing or promotional alerts need explicit consent and should never use Time Sensitive or Critical interruption levels. The [Managing notifications HIG](https://developer.apple.com/design/human-interface-guidelines/managing-notifications) emphasizes realistic urgency and user control.

## APNs, provider, and device token boundaries

Remote delivery is a chain:

~~~text
app target and Push Notifications capability
    -> device registers with APNs
    -> current device token and environment go to provider
    -> provider authenticates to APNs
    -> APNs validates topic, payload, and token
    -> device receives or does not receive the notification
    -> system applies settings, Focus, grouping, and presentation
~~~

Register for remote notifications at launch as documented and handle both success and failure. Device tokens are specific to the device and app and can change. Forward the current token securely; do not hard-code it, use one token for multiple apps, or assume development and production tokens are interchangeable.

The provider server owns APNs authentication, topic, environment, token storage, payload construction, retry policy, expiration, collapse behavior, and delivery logging. The app owns the token association and the user-facing domain route. APNs acceptance is not proof that the device displayed the notification, and a delegate callback is not proof that a provider fulfilled a business event.

Keep the visible payload minimal:

- aps alert, sound, badge, category, thread-id, mutable-content, content-available, target-content-id, interruption-level, relevance-score, and other documented keys;
- small primitive custom values with a schema version and opaque record identifier;
- no secrets, raw credentials, full message history, or unbounded model text;
- 4 KB payload limit for ordinary remote notifications and the documented smaller or specialized limits for other push types;
- a server-side event ID for deduplication and a domain revision for stale-event handling.

Separate visible alert pushes from background pushes. A background notification is a request to give the app an opportunity to refresh; it is not a guaranteed execution slot, content delivery receipt, or substitute for a user-facing alert.

## Notification service extension

Use UNNotificationServiceExtension when a remote alert notification needs a bounded transformation before display, such as decrypting a supported payload or downloading an attachment. The payload must contain mutable-content set to 1 and an alert dictionary for the system to invoke the service extension.

The extension is a separate bundle with a short execution window. The documented guidance gives the handler about 30 seconds and calls serviceExtensionTimeWillExpire when time is expiring. Always keep the original content available as a safe fallback. If the completion handler is not called, the system displays the original content.

Design the extension as:

~~~text
remote alert payload
    -> service extension launch
    -> validate schema and privacy policy
    -> bounded decrypt/download/transform
    -> updated UNMutableNotificationContent
    -> completion handler
    -> original-content fallback on timeout/failure
~~~

Do not put a full network synchronization engine, model session, database migration, or unbounded media fetch in the extension. Do not log decrypted notification content. Use a redacted failure state and record only operational diagnostics needed to repair the route.

Attachments must be local and supported before delivery. For local notifications, create the attachment before scheduling. For remote notifications, the service extension can download and attach a supported file. Validate file type, size, lifetime, and privacy before adding it to content.

## Notification content extension

Use User Notifications UI only when the expanded system notification genuinely benefits from a custom interface. A content extension is a separate target with its own lifecycle and category matching. The system still owns the abbreviated banner, header, permission, grouping, and much of the surrounding UI.

The documented content-extension route expects a custom view controller configured with the notification’s immediately available content. Keep the view fast, self-contained, and privacy-safe. Do not depend on a network round trip to render the initial state. Configure supported categories in the extension’s Info.plist and keep categories unique across content extensions.

Interactive controls are an extension-specific route, not a general SwiftUI app screen. Follow the current User Notifications UI contract for supported controls, media playback, selected-action handling, and response options. Do not add arbitrary gesture behavior or assume the extension can access all app state while the device is locked.

Use a SwiftUI view in the main app for notification settings, history, and review. Use the extension target only for the system’s notification interface and keep the shared projection small:

~~~text
app-owned notification record
    -> redacted extension payload
    -> content-extension view
    -> response/action identifier
    -> main-app or background route
~~~

## Live Activities are not ordinary notifications

ActivityKit Live Activities display current content state on supported system surfaces. They have their own attributes, content-state revision, lifecycle, supported device surfaces, push token, server topic, and stale/end behavior. ActivityKit updates can use APNs, but a Live Activity update is not the same as an ordinary notification alert.

Use a Live Activity for an ongoing event that remains useful while its state changes. Use UserNotifications for a discrete alert or action. Do not present a one-time notification as a continuously current Live Activity, and do not assume a Live Activity update reached the device merely because APNs accepted a payload.

Keep the model:

~~~text
domain event
    -> ActivityKit content-state revision
    -> local or remote activity update
    -> system surface
    -> stale/end/final state
~~~

The app should be able to render a truthful stale or ended state if a push is delayed. Test Live Activities separately from notification authorization, action categories, and communication notifications.

## SwiftUI and Liquid Glass composition

The app-owned notification settings and review screens should use native SwiftUI hierarchy:

- NavigationStack or NavigationSplitView for settings and category detail;
- List or Form for authorization state, categories, privacy choices, and test fixtures;
- system Button, Toggle, Picker, DatePicker, and TextField controls;
- accessibility labels, values, hints, and Dynamic Type-aware layouts;
- a clear “Open Settings” route when system authorization cannot be repaired in-app;
- a distinct review state when a local model proposes notification wording or timing.

Liquid Glass belongs around functional app-owned controls and navigation, not inside a fake notification banner meant to impersonate the system. Start with standard SwiftUI bars, sheets, controls, and navigation so the system can supply the current material automatically. Use a small custom glass effect only for a high-value review action or status group, and test reduced transparency, reduced motion, contrast, large text, and content scrolling beneath the control.

For a notification review shell:

~~~text
app-owned content
    -> plain semantic hierarchy
    -> one primary review/confirm control
    -> optional restrained glass effect
    -> system notification request or settings handoff
~~~

Do not place private notification body text underneath a translucent surface where it can be read accidentally. Do not put multiple glass cards over the same notification timeline. Use system controls for the settings and the notification itself.

## On-device AI can propose, never silently notify

Foundation Models can generate structured output on supported Apple Intelligence devices. Availability depends on device, region, Apple Intelligence settings, and model readiness. Check SystemLanguageModel availability and provide a deterministic fallback before creating a LanguageModelSession.

A safe notification proposal has explicit fields:

~~~text
NotificationProposal
    sourceRecordIDs
    sourceRevision
    purpose
    titleCandidate
    bodyCandidate
    categoryCandidate
    actionCandidates
    triggerCandidate
    interruptionLevelCandidate
    privacyClass
    modelRevision
    requiresUserReview
~~~

Restrict generated values with an allowlist:

- category must be one of the app’s registered categories;
- actions must map to known action identifiers with current domain handlers;
- trigger must pass deterministic date/location/interval validation;
- interruption level may default to active or passive according to product policy, but cannot escalate to time-sensitive or critical without an explicit product rule and, where required, entitlement;
- body text must pass privacy redaction and length checks;
- source record IDs and revisions must still exist and be current;
- no model text may be copied into a notification without the user-approved privacy policy.

Revalidate after generation. If the record changed, the time passed, the notification settings changed, or the model returned an unknown category/action, discard the proposal or show a repair state. A local model cannot grant notification permission, bypass Focus, guarantee attention, prove a communication identity, or commit a server-side event.

Use guided generation or another structured output path when available, but keep the schema and domain validation app-owned. Do not use the language model for basic arithmetic, date validity, authorization, token handling, or exact state transitions. The deterministic app should calculate those values.

## Concurrency, cancellation, and lifecycle

Use one owner for each boundary:

| Boundary | Owner | Cancellation rule |
| --- | --- | --- |
| Authorization/settings | Notification coordinator | Ignore stale request results after a newer settings read |
| Local request generation | Notification scheduler actor | Cancel superseded revision before add |
| Delegate response | Main-actor route store | Parse once, commit once, complete once |
| APNs token association | Registration service | Replace the old token after secure server acknowledgement |
| Service extension | Extension instance | Finish with best available content before timeout |
| Content extension | Extension view controller | Render from immediate content and bounded shared data |
| AI proposal | Model session coordinator | Cancel when source revision or user intent changes |
| Live Activity | Activity/session owner | Ignore stale content-state revision and end explicitly |

The modern async delegate form may be available for notification responses, but confirm the signature and availability against the target SDK. Whether using an async method or completion-handler method, finish the callback at the documented boundary. Never call both forms for the same event and never leave the system waiting for completion.

When a SwiftUI view disappears, cancel proposal generation and release view-specific tasks. When the app returns from Settings, re-read UNNotificationSettings rather than replaying cached state. When a notification action runs in the background, do not assume a fully initialized app scene or unlocked protected data.

## Failure states are part of the native experience

Represent failures explicitly:

| Failure | User-facing state | Recovery |
| --- | --- | --- |
| Permission not determined | Explain the value before asking | Request once from the relevant feature |
| Permission denied | Notifications are off | Open system settings or use in-app history |
| Sound/badge/alert limited | Some presentation is unavailable | Continue with truthful in-app state |
| Local scheduling rejected | Request was not accepted | Repair identifier/content/trigger and retry |
| Provider/APNs failure | Delivery is unknown or failed | Retry with idempotency and in-app fallback |
| Device token changed | Provider association is stale | Securely update the server record |
| Action is stale | Record no longer matches | Show conflict or open current record |
| Service extension timeout | Original payload is shown | Keep original content safe |
| Attachment unavailable | Text-only fallback | Deliver without the media |
| Focus status unavailable | Status is unknown | Do not infer another person’s intent |
| AI unavailable | No proposal | Use deterministic compose/settings flow |
| AI output invalid | Proposal discarded | Show manual edit and review |
| ActivityKit update delayed | State may be stale | Render stale/final status |

## Proof-first completion

A notification tranche is complete only when the evidence matches the claim:

- documentation and target availability show which route is supported;
- signed entitlements and Info.plist inspection show the capabilities and extension declarations;
- deterministic fixtures cover permission, settings, content privacy, identifiers, triggers, categories, actions, response routing, and stale revisions;
- a signed physical device receives local and remote test notifications in the selected environment;
- Focus, scheduled summary, lock-screen, foreground, denied, revoked, and notification-settings changes are tested;
- a provider trace is correlated with the device token, environment, payload ID, and server order/event revision;
- service and content extensions are tested with timeout, missing media, redacted data, and fallback content;
- communication notification intent donation and Focus status are tested only on a configured physical device and authorized account;
- Live Activity update/end/stale behavior is tested separately from ordinary alerts;
- the on-device model’s availability, model revision, source revision, user review, and deterministic revalidation are recorded;
- VoiceOver, Dynamic Type, contrast, Reduce Motion, reduced transparency, keyboard, pointer, and alternate input complete the notification-settings task;
- release archive, TestFlight/release install, APNs environment, extension bundles, privacy resources, and version/build are inspected.

## Sources

- [User Notifications](https://developer.apple.com/documentation/usernotifications)
- [Asking permission to use notifications](https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications)
- [UNUserNotificationCenter](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter)
- [UNUserNotificationCenterDelegate](https://developer.apple.com/documentation/usernotifications/unusernotificationcenterdelegate)
- [Requesting authorization](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter/requestauthorization%28options%3Acompletionhandler%3A%29)
- [UNNotificationSettings](https://developer.apple.com/documentation/usernotifications/unnotificationsettings)
- [Scheduling a notification locally from your app](https://developer.apple.com/documentation/usernotifications/scheduling-a-notification-locally-from-your-app)
- [UNNotificationRequest](https://developer.apple.com/documentation/usernotifications/unnotificationrequest)
- [UNMutableNotificationContent](https://developer.apple.com/documentation/usernotifications/unmutablenotificationcontent)
- [UNNotificationContent](https://developer.apple.com/documentation/usernotifications/unnotificationcontent)
- [UNCalendarNotificationTrigger](https://developer.apple.com/documentation/usernotifications/uncalendarnotificationtrigger)
- [UNTimeIntervalNotificationTrigger](https://developer.apple.com/documentation/usernotifications/untimeintervalnotificationtrigger)
- [UNLocationNotificationTrigger](https://developer.apple.com/documentation/usernotifications/unlocationnotificationtrigger)
- [Declaring your actionable notification types](https://developer.apple.com/documentation/usernotifications/declaring-your-actionable-notification-types)
- [UNNotificationCategory](https://developer.apple.com/documentation/usernotifications/unnotificationcategory)
- [UNNotificationCategoryOptions](https://developer.apple.com/documentation/usernotifications/unnotificationcategoryoptions)
- [UNNotificationAction](https://developer.apple.com/documentation/usernotifications/unnotificationaction)
- [UNTextInputNotificationAction](https://developer.apple.com/documentation/usernotifications/untextinputnotificationaction)
- [Handling notifications and notification-related actions](https://developer.apple.com/documentation/usernotifications/handling-notifications-and-notification-related-actions)
- [UNNotificationResponse](https://developer.apple.com/documentation/usernotifications/unnotificationresponse)
- [UNTextInputNotificationResponse](https://developer.apple.com/documentation/usernotifications/untextinputnotificationresponse)
- [UNNotificationInterruptionLevel](https://developer.apple.com/documentation/usernotifications/unnotificationinterruptionlevel)
- [Generating a remote notification](https://developer.apple.com/documentation/usernotifications/generating-a-remote-notification)
- [Setting up a remote notification server](https://developer.apple.com/documentation/usernotifications/setting-up-a-remote-notification-server)
- [Registering your app with APNs](https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns)
- [Pushing background updates to your app](https://developer.apple.com/documentation/usernotifications/pushing-background-updates-to-your-app)
- [Modifying content in newly delivered notifications](https://developer.apple.com/documentation/usernotifications/modifying-content-in-newly-delivered-notifications)
- [UNNotificationServiceExtension](https://developer.apple.com/documentation/usernotifications/unnotificationserviceextension)
- [User Notifications UI](https://developer.apple.com/documentation/usernotificationsui)
- [Customizing the appearance of notifications](https://developer.apple.com/documentation/usernotificationsui/customizing-the-appearance-of-notifications)
- [UNNotificationContentExtension](https://developer.apple.com/documentation/usernotificationsui/unnotificationcontentextension)
- [Handling Communication Notifications and Focus Status Updates](https://developer.apple.com/documentation/UserNotifications/handling-communication-notifications-and-focus-status-updates)
- [UNNotificationContentProviding](https://developer.apple.com/documentation/usernotifications/unnotificationcontentproviding)
- [INSendMessageIntent](https://developer.apple.com/documentation/intents/insendmessageintent)
- [INStartCallIntent](https://developer.apple.com/documentation/intents/instartcallintent)
- [INInteraction](https://developer.apple.com/documentation/sirikit/ininteraction)
- [INFocusStatusCenter](https://developer.apple.com/documentation/intents/infocusstatuscenter)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/ActivityKit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications)
- [Managing notifications HIG](https://developer.apple.com/design/human-interface-guidelines/managing-notifications)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
