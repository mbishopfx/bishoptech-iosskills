# SwiftUI UserNotifications, communication notifications, and action review proof matrix

Use this matrix to separate app-owned notification intent from system authorization, local scheduling, APNs/provider delivery, system presentation, communication identity, notification extensions, Live Activities, on-device-AI proposals, Liquid Glass design, accessibility, and release behavior.

Read it with the [notification review](../42-framework-deep-dives/105-swiftui-usernotifications-communication-actions-review.md), [design guide](../21-design-deep-dives/133-swiftui-usernotifications-communication-actions-review-design.md), [route](../50-capability-recipes/136-swiftui-usernotifications-communication-actions-review-route.md), and [recipes](../70-code-recipes/148-swiftui-usernotifications-communication-actions-review-recipes.md).

## Evidence levels

| Level | Evidence | What it can establish |
| --- | --- | --- |
| L0 | Current Apple documentation and target SDK review | Documented API, policy, and availability contract |
| L1 | Target settings, entitlements, Info.plist, extension graph, provider configuration | Configuration exists for the named target |
| L2 | Deterministic notification, action, payload, trigger, privacy, and revision fixtures | App-owned validation and route logic |
| L3 | Simulator, local request, provider fixture, extension fixture, or mocked system result | Partial app-side behavior |
| L4 | Signed physical-device run with system notification surfaces | Device authorization, presentation, action, and extension behavior for the tested case |
| L5 | Controlled APNs/provider/communication account, archive, and TestFlight/release installation | Environment-specific distribution behavior |
| L6 | Repeated accessibility, privacy, cancellation, stale-state, retry, and operational evidence | Readiness for the named claim |

An authorization result is not delivery proof. A pending request is not presentation proof. APNs acceptance is not user attention. A communication intent is not proof of sender identity. A model proposal is not a scheduled request.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| The app chose the correct route | Route worksheet mapping local, remote, action, communication, extension, Live Activity, or in-app surface | A bell icon or generic notification API |
| The target can request notifications | Signed target and runtime settings read | A source-level import |
| The person authorized notifications | Physical settings run with status snapshot | A permission prompt screenshot |
| Alerts/sounds/badges are allowed | Current UNNotificationSettings values | Prior authorization |
| A local request is scheduled | add result, stable identifier, pending request inspection | A constructed request object |
| A local request is delivered | Physical system run with trigger and device state | Pending request |
| A remote token is registered | Signed Push Notifications capability and device token callback | A copied token |
| Provider can send | Provider authentication/topic/environment/payload trace | Token callback |
| APNs accepted the push | APNs response tied to event ID and token | Provider queue log |
| Device received the push | Device/system trace for the tested case | APNs acceptance |
| User saw the notification | Physical observation with stated system settings | Delivery callback |
| User selected an action | Physical action run and delegate response | Category declaration |
| Domain mutation succeeded | Current revision check and idempotent commit evidence | Completion handler |
| Communication notification is configured | Capability, SiriKit intent declarations, donation, service extension, and physical run | A normal notification with a contact name |
| Focus status is known | Required authorization and documented system result | Missing or nil status |
| Notification service extension transformed content | Mutable-content alert, extension trace, final presentation, timeout fallback | Service target exists |
| Notification content extension rendered | Category match, extension bundle, physical expanded notification | Main-app preview |
| Attachment is usable | Supported file, size/type validation, system presentation | File URL in source |
| AI proposal is safe | Model availability, source IDs/revisions, schema validation, user review, stale check | Generated title/body |
| Urgency is appropriate | Product policy, HIG review, entitlement if required, payload/content inspection | A red-colored “urgent” badge |
| Live Activity is current | Activity lifecycle, content-state revision, device/system update and stale/end run | One ActivityKit object |
| Liquid Glass composition is appropriate | Standard-control review and reduced-effect/accessibility runs | One screenshot |
| Notification settings task is accessible | VoiceOver, Dynamic Type, contrast, Reduce Motion, reduced transparency, keyboard/pointer/Switch Control task | Accessibility identifiers only |
| Release behavior is ready | Signed archive, extension/entitlement inspection, TestFlight/release install, physical APNs/device evidence | Debug or simulator success |

## Target and environment packet

Record exactly what was tested:

~~~text
App target:
Bundle identifier:
SDK/toolchain:
Deployment target:
OS build:
Device model:
Device family:
Region and language:
User account/test account:
UserNotifications capability:
APS environment entitlement:
Communication Notifications capability:
SiriKit intent declarations:
Focus Status usage description:
Time Sensitive policy:
Critical Alert entitlement:
Service extension target:
Content extension target:
Widget/Live Activity extension:
App Groups:
App Intents/deep-link route:
Provider server:
APNs topic:
APNs environment:
Token registration revision:
Payload schema revision:
Model and prompt/schema revision:
Archive version/build:
TestFlight/release build:
~~~

Compare project settings, signed archive entitlements, and installed build. Preserve redacted token and account evidence.

## Authorization and settings matrix

| Case | Setup | Expected observation | Required evidence |
| --- | --- | --- | --- |
| First request | Not determined | Context explanation then request | Physical settings run |
| Allow alerts | Alert allowed | Settings reflect alert authorization | Current snapshot |
| Deny | User denies | App shows fallback and settings route | Physical run |
| Provisional | Provisional path supported | App labels it provisional | Settings snapshot |
| Restricted | System restriction | No permission loop | Device policy state |
| Sound disabled | Alerts on, sound off | App does not claim sound | Settings snapshot |
| Badge disabled | Alerts on, badge off | App does not promise badge | Settings snapshot |
| Notification summary | Scheduled delivery enabled | App does not claim immediate alert | Device setting and run |
| Focus | Focus active | Behavior reflects system policy | Physical run |
| Return from Settings | Settings changed externally | App refreshes current values | Scene activation trace |
| Multiple callers | Two features request together | One serialized owner | Concurrency test |
| App reinstall | Fresh authorization state | No stale local assumption | Clean device run |

## Local request matrix

| Claim | Fixture/run | Required result |
| --- | --- | --- |
| Content is valid | Title/body/privacy/category fixture | Deterministic content |
| Identifier is stable | Same domain record twice | Replacement or deduplication is intentional |
| Calendar trigger is correct | Timezone/DST fixture | Expected next trigger |
| Interval trigger is correct | Termination/background fixture | Documented timing boundary |
| Location trigger is correct | Authorization/region fixture | Expected fallback when unavailable |
| Request accepted | add result | Scheduled state only |
| Pending list reconciles | get pending requests | Identifiers match domain records |
| Cancellation works | Complete/cancel fixture | Pending request removed |
| Replacement works | Revision change fixture | Old request is not left behind |
| Delivered list policy works | Delivered request fixture | Removal does not delete domain record |
| Stale action is safe | Old userInfo revision | No incorrect mutation |

## Content and urgency matrix

| Content field | Validate | Evidence |
| --- | --- | --- |
| Title/body | Concision and privacy | Copy and lock-screen review |
| Subtitle | Context without secret | Physical lock-screen run |
| Thread identifier | Grouping policy | Notification Center run |
| Category identifier | Registered category | Registry/payload match |
| User info | Versioned opaque route data | Redacted payload inspection |
| Attachment | Local file, supported type, size | Service/local and system run |
| Interruption level | Product policy and HIG | Payload/content fixture |
| Relevance score | 0 to 1 summary ranking intent | Unit fixture |
| Sound | User and product policy | Settings/device run |
| Badge | Count semantics | Domain and device run |
| Target content identifier | Window/scene handoff policy | Physical route |

Use a content redaction matrix:

| Device context | Message | Title | Attachment |
| --- | --- | --- | --- |
| Unlocked | Useful current text | Contextual | Allowed if safe |
| Locked | Generic/redacted | Minimal | Only if policy permits |
| Shared display | Generic/redacted | No identity leak | Usually none |
| CarPlay/Watch | Concise and safe | Context first | Test supported media |
| Focus or summary | Accurate urgency | No coercive language | No assumption of timing |

## Action matrix

| Action | Category | Physical run | Domain proof |
| --- | --- | --- | --- |
| Open record | Open | Tap action while app closed | Current record resolves |
| Accept | Invitation | Action from locked/unlocked state | Pending to accepted once |
| Decline | Invitation | Action and repeat tap | Pending to declined once |
| Mark read | Message | Background action | Current message revision |
| Reply | Message | Type short response | Account/recipient/thread validation |
| Snooze | Reminder | Action with schedule change | Old request removed |
| Delete | Record | Destructive confirmation policy | Current record and authorization |
| Unknown action | Any | Inject unknown identifier | Safe no-op or open route |
| Dismiss | Category with custom dismiss | Dismiss system UI | Optional analytics only |

Record the response’s action identifier, notification request identifier, source revision, account state, protected-data state, and completion time. Do not log body text or text-input values by default.

## APNs/provider matrix

| Layer | Evidence | Failure to test |
| --- | --- | --- |
| App capability | Signed APS entitlement | Development checkbox only |
| Registration | Current token callback | Old token retained |
| Association | Secure token/account mapping | Token in URL or log |
| Provider trust | Token/certificate auth and topic | Local curl without environment |
| Payload | Versioned redacted JSON | Full record or secret |
| APNs request | Event ID and response | Provider queue only |
| Device receipt | Physical system observation | APNs acceptance |
| Retry | Idempotent event handling | Duplicate mutation |
| Expiration | Expired event fixture | Stale alert |
| Production | Signed release/TestFlight configuration | Debug environment |

For background pushes, also record that the app may not execute immediately or at all. Do not use the background path as proof of a visible alert.

## Communication and Focus matrix

| Claim | Required evidence | Does not prove it |
| --- | --- | --- |
| Direct message route exists | INSendMessageIntent configuration and current participant mapping | UserInfo sender name |
| Call route exists | INStartCallIntent and CallKit/LiveCommunicationKit boundary | Message notification |
| Interaction is donated | Incoming/outgoing donation trace | Intent object in source |
| Notification content is updated | Service extension result using recognized intent context | App-created custom conformance |
| Focus status can be read | Capability, usage description, authorization, physical result | Nil interpreted as false |
| Communication breaks through appropriately | Physical device with configured Focus and allowed people/app | One unlocked run |
| Privacy is safe | Locked-screen and preview review | Full text in a local fixture |

Never expose a person’s Focus status as a social judgment. Keep the status optional and document the perspective of the app.

## Extension matrix

| Extension | Setup | Proof | Boundary |
| --- | --- | --- | --- |
| Notification service | Separate target, mutable-content alert, bundle signing | Remote physical run | About 30-second handler window and fallback |
| Notification content | Separate target, category Info.plist | Expanded physical notification | Immediate data only; system chrome remains |
| Widget/Live Activity | Widget extension and ActivityKit route | Lifecycle/system run | Different process and content-state contract |
| App Intents | Action/entity/deep-link route | System invocation and current re-resolve | Not a notification delivery receipt |

Test missing app-group data, locked device, expired account, attachment failure, service timeout, content-extension category mismatch, and user dismissal.

## AI proposal matrix

| Check | Evidence | Failure |
| --- | --- | --- |
| Model availability | SystemLanguageModel state | Device not eligible or model not ready |
| Source grounding | Source IDs/revisions | Untraceable wording |
| Structured output | Codable/schema validation | Arbitrary action/category |
| Privacy | Redacted input/output review | Secret in notification |
| Urgency | Allowlist and policy | Model escalates interruption |
| Action safety | Registered identifier map | Unknown action mutation |
| Staleness | Revision changes during generation | Proposal for old record |
| User review | UI trace before schedule/send | Silent notification |
| Fallback | Manual deterministic compose | Feature disappears |
| Reproducibility | Model/prompt/schema revision | Unexplained drift |

The model must not select APNs credentials, prove delivery, infer a communication identity, or commit a domain mutation.

## Liquid Glass and accessibility matrix

| Claim | Evidence | Does not prove it |
| --- | --- | --- |
| Native hierarchy is used | SwiftUI standard navigation/forms/controls | Glass screenshot |
| Glass is functional | One high-value status/review role | Glass on every row |
| Reduced transparency works | Device accessibility run | Default appearance |
| Reduced motion works | Device transition run | Static preview |
| Dynamic Type works | Largest supported sizes | One text-size screenshot |
| VoiceOver task works | Settings/review/schedule task | Accessibility labels only |
| Alternate input works | Keyboard/pointer/Switch Control | Touch-only run |
| Privacy works beneath translucent UI | Locked/shared-display review | Unlocked simulator |

## Release packet

Collect:

- current Apple/Swift source links and target availability notes;
- signed entitlements and extension Info.plist;
- privacy manifest and notification copy;
- local request/action/payload fixtures;
- APNs provider environment and redacted traces;
- physical-device permission/settings/Focus/lock-screen/action runs;
- service/content extension fallback evidence;
- communication intent and Focus-status evidence if used;
- Live Activity evidence if used;
- AI proposal/revalidation and fallback evidence;
- accessibility task recording;
- archive version/build and installed TestFlight/release build;
- known unsupported devices, settings, regions, provider conditions, and recovery behavior.

## Release decision

| Decision | Minimum evidence |
| --- | --- |
| Documentation-ready | L0 source review and route worksheet |
| UI prototype-ready | L2 deterministic settings/draft/action fixtures |
| Device-ready | L4 physical notification, action, privacy, and accessibility runs |
| Provider-ready | L5 APNs/provider/account/environment evidence |
| TestFlight-ready | Signed archive, extension/entitlement review, release build test |
| Production-ready | Repeatable L6 recovery, idempotency, privacy, accessibility, and operational packet |

## Sources

- [User Notifications](https://developer.apple.com/documentation/usernotifications)
- [UNUserNotificationCenter](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter)
- [UNUserNotificationCenterDelegate](https://developer.apple.com/documentation/usernotifications/unusernotificationcenterdelegate)
- [UNNotificationSettings](https://developer.apple.com/documentation/usernotifications/unnotificationsettings)
- [Requesting authorization](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter/requestauthorization%28options%3Acompletionhandler%3A%29)
- [Scheduling a notification locally from your app](https://developer.apple.com/documentation/usernotifications/scheduling-a-notification-locally-from-your-app)
- [UNNotificationRequest](https://developer.apple.com/documentation/usernotifications/unnotificationrequest)
- [UNMutableNotificationContent](https://developer.apple.com/documentation/usernotifications/unmutablenotificationcontent)
- [UNNotificationInterruptionLevel](https://developer.apple.com/documentation/usernotifications/unnotificationinterruptionlevel)
- [Declaring your actionable notification types](https://developer.apple.com/documentation/usernotifications/declaring-your-actionable-notification-types)
- [UNNotificationCategory](https://developer.apple.com/documentation/usernotifications/unnotificationcategory)
- [UNNotificationAction](https://developer.apple.com/documentation/usernotifications/unnotificationaction)
- [UNTextInputNotificationAction](https://developer.apple.com/documentation/usernotifications/untextinputnotificationaction)
- [Handling notifications and notification-related actions](https://developer.apple.com/documentation/usernotifications/handling-notifications-and-notification-related-actions)
- [Generating a remote notification](https://developer.apple.com/documentation/usernotifications/generating-a-remote-notification)
- [Setting up a remote notification server](https://developer.apple.com/documentation/usernotifications/setting-up-a-remote-notification-server)
- [Registering your app with APNs](https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns)
- [Modifying content in newly delivered notifications](https://developer.apple.com/documentation/usernotifications/modifying-content-in-newly-delivered-notifications)
- [UNNotificationServiceExtension](https://developer.apple.com/documentation/usernotifications/unnotificationserviceextension)
- [User Notifications UI](https://developer.apple.com/documentation/usernotificationsui)
- [Customizing the appearance of notifications](https://developer.apple.com/documentation/usernotificationsui/customizing-the-appearance-of-notifications)
- [Handling Communication Notifications and Focus Status Updates](https://developer.apple.com/documentation/UserNotifications/handling-communication-notifications-and-focus-status-updates)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/ActivityKit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications)
- [Managing notifications HIG](https://developer.apple.com/design/human-interface-guidelines/managing-notifications)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
