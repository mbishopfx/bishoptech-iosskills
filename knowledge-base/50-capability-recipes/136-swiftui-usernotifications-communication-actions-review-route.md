# SwiftUI UserNotifications, communication notifications, and action review route

Use this route to decide whether an idea belongs in UserNotifications, APNs, a notification action, a communication notification, a notification extension, ActivityKit, App Intents, or an app-owned SwiftUI screen. Read the [framework review](../42-framework-deep-dives/105-swiftui-usernotifications-communication-actions-review.md), [design guide](../21-design-deep-dives/133-swiftui-usernotifications-communication-actions-review-design.md), [proof matrix](../60-verification/130-swiftui-usernotifications-communication-actions-review-proof-matrix.md), and [recipes](../70-code-recipes/148-swiftui-usernotifications-communication-actions-review-recipes.md) together.

This is a route worksheet, not a guarantee of notification delivery or a provider implementation.

## One-line route selector

Ask what the person needs:

| Need | Choose |
| --- | --- |
| A future reminder based on time, date, or location | Local UserNotifications request |
| A server event that may need a visible alert | UserNotifications plus APNs/provider |
| A bounded answer from the notification itself | Category and UNNotificationAction |
| A short written reply | UNTextInputNotificationAction |
| Direct human message or call context | Communication notification plus SiriKit intent |
| Decrypt/download/transform a remote alert | Notification service extension |
| A custom expanded notification view | Notification content extension |
| An ongoing event with changing state | ActivityKit Live Activity |
| In-app settings, history, privacy, or review | SwiftUI app view |
| A generated draft that needs user approval | Foundation Models proposal plus SwiftUI review |

If the answer is “make the person notice something,” first ask whether an in-app update, badge, widget, Live Activity, or system action is less intrusive. A notification is high-value attention, not a general-purpose message bus.

## Route worksheet

Fill this before coding:

~~~text
Outcome:
Audience:
Direct communication, task update, reminder, marketing, or emergency:
Local, remote, or both:
Source record IDs:
Source revision:
User-visible data:
Lock-screen redaction:
Registered category:
Action identifiers:
Text input required:
Trigger:
Interruption policy:
Attachment:
Provider/APNs environment:
App target:
Extension target:
Live Activity or App Intent handoff:
AI proposal allowed:
User confirmation point:
Domain mutation:
Cancellation rule:
Fallback:
Physical-device proof:
Release proof:
~~~

Do not proceed if the product cannot name the domain record, source revision, privacy class, and recovery state.

## Gate 1: target and system contract

Check:

- deployment target and SDK support each chosen API;
- Push Notifications capability and signed APS environment;
- Communication Notifications, SiriKit intent declarations, and Focus status usage description only when required;
- critical-alert entitlement only for the approved health/safety route;
- notification service/content extension targets and category Info.plist entries;
- ActivityKit/widget extension/push configuration if the route uses a Live Activity;
- App Intents and scene/deep-link route if actions need the main app;
- privacy manifest, notification preview, attachment, logging, and retention policy;
- named device family, region, account, APNs environment, and archive version/build.

Record the target in a build worksheet. The same source can compile in a target whose entitlements, extension membership, or provider topic are wrong.

## Gate 2: authorization and settings

Implement this state sequence:

~~~text
feature explanation
    -> request only needed options
    -> read UNNotificationSettings
    -> show authorized/provisional/denied/restricted/partial
    -> schedule only if the app-owned policy permits
    -> refresh after scene activation or Settings return
~~~

Use an app-owned NotificationSettingsSnapshot:

~~~text
authorization
alert
sound
badge
lockScreen
notificationCenter
carPlay
scheduledDelivery
criticalAlert
timeSensitive
refreshedAt
~~~

Treat unavailable values as unknown. Do not make a system settings snapshot mutable from a SwiftUI Toggle.

## Gate 3: local notification route

Use a local request when the app has enough information to schedule without a provider:

~~~text
domain record
    -> deterministic NotificationDraft
    -> validate privacy/category/trigger
    -> create UNMutableNotificationContent
    -> create calendar/time/location trigger
    -> create stable UNNotificationRequest
    -> add to UNUserNotificationCenter
    -> inspect pending requests
~~~

Use a request identity function that includes the domain record and purpose, not a random identifier that cannot be canceled. Keep the source revision in userInfo only as a route hint; the action handler must re-read the current record.

For recurring calendar reminders, test timezone and daylight-saving transitions. For location triggers, test authorization and region behavior. For elapsed-time triggers, test app termination and device power state. A scheduled request is a system-held request, not a delivery receipt.

## Gate 4: remote/APNs route

Use the remote route when a provider has current event knowledge:

~~~text
signed app target
    -> register at launch
    -> receive current device token
    -> secure provider association
    -> provider builds small versioned payload
    -> APNs validates topic/environment/token
    -> device/system applies settings and Focus
    -> app handles foreground/action/background path
~~~

Record:

- bundle ID and APNs topic;
- development or production environment;
- token hash or redacted identifier;
- provider request ID;
- domain event ID and revision;
- payload schema;
- APNs status;
- device receipt or system observation when tested;
- provider retry and expiration behavior.

Never claim “sent” when the app only knows that a server queued an event. Use “queued,” “accepted by APNs,” “device callback observed,” and “user action observed” as separate states.

## Gate 5: actionable notification route

Register categories and actions before scheduling or sending:

~~~text
known action definitions
    -> notification categories registered at launch
    -> local content or APNs payload includes category identifier
    -> system presents action buttons
    -> delegate receives response
    -> typed action parser
    -> current record/revision validation
    -> idempotent domain mutation
    -> completion
~~~

Suggested route table:

| Action | Allowed side effect | Revalidation |
| --- | --- | --- |
| Open | Navigation or scene handoff | Record still exists |
| Mark read | Local/server read state | Current message revision |
| Accept | Domain status transition | State is still pending |
| Decline | Domain status transition | State is still pending |
| Reply | Send message | Account, recipient, content, and current thread |
| Snooze | Replace schedule | New trigger and current record |
| Delete | Destructive mutation | Confirmation policy and current record |

The action identifier is the route key. Localized title text is not. Unknown identifiers should produce a logged, redacted no-op or safe open route, not a guessed mutation.

## Gate 6: communication notification route

Choose this route only for direct calls or messages:

~~~text
incoming/outgoing communication record
    -> SiriKit intent context
    -> interaction donation
    -> communication notification content update
    -> sender/group-aware system presentation
    -> user action or Focus-aware behavior
    -> provider/domain reconciliation
~~~

Verify:

- INSendMessageIntent or INStartCallIntent is appropriate;
- interaction direction and participant identity are current;
- communication notification capability is enabled;
- required Info.plist intent declarations exist;
- Focus status usage and authorization are present only if requested;
- notification service extension can update content in its time limit;
- locked-screen text is safe;
- action routing does not trust the notification body as identity.

Do not use communication notification treatment for marketing, order updates, content recommendations, or generic reminders.

## Gate 7: extension route

### Notification service extension

Use when the remote alert contains mutable-content and an alert and needs a bounded decrypt/download/transform. Keep a safe original payload and finish before the documented deadline.

~~~text
mutable-content alert
    -> extension validates schema
    -> bounded transform
    -> updated content or original fallback
    -> system presentation
~~~

### Notification content extension

Use when the expanded notification needs a custom interface. Configure the supported category in the extension Info.plist, render immediately from available data, and keep shared state minimal.

~~~text
category match
    -> content extension view controller
    -> current notification content
    -> optional supported media/action route
    -> system dismissal or app handoff
~~~

Do not use an extension as a hidden background app. Test missing app-group data, locked device, expired credentials, unavailable media, and extension timeout.

## Gate 8: Live Activity boundary

If the event has ongoing state, compare ActivityKit to a notification:

| Question | Notification | Live Activity |
| --- | --- | --- |
| One-time alert | Good fit | Usually wrong |
| Current state changes repeatedly | Limited | Good fit |
| User action from a compact system surface | Category action | ActivityKit/App Intent route |
| Delivery | APNs or local request | ActivityKit update/push |
| Expiry/stale state | Optional | Explicit content-state policy |
| User sees a banner | System-dependent | System surface-dependent |

Keep activity content state separate from notification categories and action identifiers. A Live Activity update should not be used as a delivery guarantee for a safety or business event.

## Gate 9: on-device-AI proposal route

Use AI only after the deterministic notification intent exists:

~~~text
current source record
    -> bounded prompt/schema
    -> Foundation Models availability check
    -> structured proposal
    -> privacy/category/action/trigger validation
    -> source revision check
    -> user review
    -> schedule or provider send
~~~

Proposal allowlist:

~~~text
title and body wording
registered category
known action identifiers
deterministic trigger candidate
privacy class
explanation
~~~

Proposal denylist:

~~~text
permission decisions
critical or time-sensitive escalation without policy
recipient identity
APNs credentials or token handling
server fulfillment
exact arithmetic or date validity
guaranteed delivery or attention claims
irreversible domain mutation
~~~

If the model is unavailable, show a manual compose path. If the source revision changes while generating, discard or regenerate. Store model revision and input source IDs for later proof.

## Gate 10: SwiftUI design route

Build the in-app shell:

1. show current notification settings;
2. explain privacy and delivery limits;
3. let the user configure an app-owned preference;
4. show a generated or manual draft;
5. allow editing and discard;
6. confirm the system request or provider send;
7. show the exact known result layer.

Use system controls and navigation. Use Liquid Glass sparingly around a primary review/status function. Never recreate a system banner, Lock Screen, Notification Center, Focus selector, or Apple Watch notification.

## Cancellation and stale-state route

Use a generation or revision ID:

~~~text
intent revision 12
    -> model proposal revision 12
    -> user edits
    -> intent revision 13
    -> proposal 12 becomes stale
    -> cancel or discard
~~~

When a user changes a trigger, category, privacy setting, or source record:

- cancel pending work for the old revision;
- remove or replace the old local request;
- invalidate any provider send not yet committed;
- ignore old delegate or model results;
- refresh system settings;
- show the current draft.

## Proof packet

Collect:

- target settings and signed entitlements;
- notification options and settings snapshots;
- category/action registry and payload fixtures;
- local pending/delivered request identifiers;
- APNs provider/environment/topic/token evidence;
- redacted payload and event IDs;
- service/content extension bundle and Info.plist evidence;
- communication intent donation and Focus authorization evidence;
- Live Activity attribute/content-state evidence when used;
- AI availability/model/source revision and user-review evidence;
- accessibility and alternate-input run;
- signed archive, TestFlight/release installation, and physical-device results.

## Fast route checklist

- [ ] Product outcome is not merely “get attention.”
- [ ] Notification versus Live Activity versus in-app route is intentional.
- [ ] Authorization is requested in context and settings are re-read.
- [ ] Categories/actions are registered at launch.
- [ ] Local identifiers are stable and cancelable.
- [ ] Remote payloads are small, versioned, and redacted.
- [ ] APNs provider evidence is separate from system presentation.
- [ ] Communication notifications use real communication intents.
- [ ] Time Sensitive/Critical use has an explicit policy and entitlement review.
- [ ] Service/content extensions have target and fallback proof.
- [ ] AI output is structured, source-linked, revalidated, and user-reviewed.
- [ ] Liquid Glass is functional, sparse, and accessibility-tested.
- [ ] Physical-device and release evidence exists for every claimed layer.

## Sources

- [User Notifications](https://developer.apple.com/documentation/usernotifications)
- [UNUserNotificationCenter](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter)
- [UNNotificationSettings](https://developer.apple.com/documentation/usernotifications/unnotificationsettings)
- [Asking permission to use notifications](https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications)
- [Scheduling a notification locally from your app](https://developer.apple.com/documentation/usernotifications/scheduling-a-notification-locally-from-your-app)
- [UNNotificationRequest](https://developer.apple.com/documentation/usernotifications/unnotificationrequest)
- [UNNotificationCategory](https://developer.apple.com/documentation/usernotifications/unnotificationcategory)
- [UNNotificationAction](https://developer.apple.com/documentation/usernotifications/unnotificationaction)
- [UNTextInputNotificationAction](https://developer.apple.com/documentation/usernotifications/untextinputnotificationaction)
- [Handling notifications and notification-related actions](https://developer.apple.com/documentation/usernotifications/handling-notifications-and-notification-related-actions)
- [Generating a remote notification](https://developer.apple.com/documentation/usernotifications/generating-a-remote-notification)
- [Setting up a remote notification server](https://developer.apple.com/documentation/usernotifications/setting-up-a-remote-notification-server)
- [Registering your app with APNs](https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns)
- [Modifying content in newly delivered notifications](https://developer.apple.com/documentation/usernotifications/modifying-content-in-newly-delivered-notifications)
- [Customizing the appearance of notifications](https://developer.apple.com/documentation/usernotificationsui/customizing-the-appearance-of-notifications)
- [Handling Communication Notifications and Focus Status Updates](https://developer.apple.com/documentation/UserNotifications/handling-communication-notifications-and-focus-status-updates)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications)
- [Managing notifications HIG](https://developer.apple.com/design/human-interface-guidelines/managing-notifications)
