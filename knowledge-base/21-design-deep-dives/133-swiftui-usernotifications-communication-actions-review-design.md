# SwiftUI UserNotifications, communication notifications, and action review design

This guide turns the [notification review](../42-framework-deep-dives/105-swiftui-usernotifications-communication-actions-review.md) into native SwiftUI design decisions. It is paired with the [notification route](../50-capability-recipes/136-swiftui-usernotifications-communication-actions-review-route.md), [proof matrix](../60-verification/130-swiftui-usernotifications-communication-actions-review-proof-matrix.md), and [compile-oriented recipes](../70-code-recipes/148-swiftui-usernotifications-communication-actions-review-recipes.md).

The goal is Apple-native hierarchy and restraint: let the system own notification presentation, use SwiftUI for app-owned settings and review, use communication conventions only for real direct communication, and keep Liquid Glass behind functional controls rather than turning the app into a replica of Notification Center.

## Design authority map

| Surface | Owner | Design implication |
| --- | --- | --- |
| Permission prompt | iOS | Explain value before requesting; do not recreate the prompt |
| Notification banner, Lock Screen, and Notification Center | iOS | Supply concise, privacy-safe content |
| Notification actions | iOS plus registered category | Use short, reversible, typed actions |
| Communication notification | iOS plus SiriKit intent | Provide honest participant and message context |
| Focus and summary behavior | Person and iOS | Respect delivery choices; never imply guaranteed interruption |
| Notification settings screen | App | Show current settings, privacy, and recovery |
| AI proposal review | App | Make generated content visibly provisional and editable |
| Liquid Glass controls | SwiftUI/system frameworks | Use standard controls and a small number of high-value effects |
| Content/service extension | Extension target and iOS | Render from immediate, redacted, bounded data |

## The screen hierarchy

Use a quiet app-owned settings flow:

~~~text
Notification Settings
    ├── Current system status
    │   ├── Permission and presentation summary
    │   ├── Open System Settings
    │   └── Last refreshed time
    ├── What this app can send
    │   ├── Reminders
    │   ├── Direct messages
    │   ├── Order or status updates
    │   └── Live event status
    ├── Privacy and preview
    │   ├── Lock-screen text policy
    │   ├── Sensitive-content redaction
    │   └── Attachment policy
    ├── Proposed notification
    │   ├── Source record and revision
    │   ├── Edit title/body/actions
    │   ├── Timing and urgency explanation
    │   └── Confirm or discard
    └── Troubleshooting
        ├── Permission denied
        ├── Provider unavailable
        ├── Stale action
        └── Extension or attachment fallback
~~~

Keep the screen task-oriented. A person should understand whether the app is allowed to request notifications, whether the system currently permits alerts/sounds/badges, what privacy tradeoff exists, and how to recover. Do not show a fake preview that looks like a real system notification without labeling it as a preview.

## State presentation

Use semantic states instead of a single enabled switch:

| State | Visual treatment | Primary action |
| --- | --- | --- |
| Not requested | Plain explanation and benefit | Request permission |
| Authorized | Current settings summary | Manage categories or test |
| Provisional | Quiet explanation of provisional delivery | Review system settings |
| Denied | Calm warning with fallback | Open Settings |
| Restricted | Informational state | Explain why no in-app repair exists |
| Partial settings | Row-level status for sound, badge, or alert | Open Settings |
| Provider unconfigured | App-owned warning | Configure server or use local route |
| AI unavailable | Deterministic compose path | Write manually |
| Stale proposal | Revision mismatch | Refresh from current record |

The current system settings should be a read-only fact in the app’s view. Do not let a local Toggle claim it changed iOS authorization until a settings refresh confirms the result. A button labeled “Open Settings” should use an app-owned explanation and then the system destination.

## Native controls first

Use:

- NavigationStack or NavigationSplitView for settings and category detail;
- Form for permission explanation, preview policy, and per-feature choices;
- Section headers that explain a decision, not just a framework name;
- Toggle for app-owned preference such as “allow reminders to be scheduled,” not for system authorization itself;
- DatePicker and Picker for deterministic app-owned schedule choices;
- TextField or TextEditor for an editable, user-reviewed message proposal;
- Button with a clear label such as “Review notification” or “Open Settings”;
- ShareLink or App Intents only when the product actually needs system handoff;
- an unobtrusive status badge for “Draft,” “Scheduled,” “Delivered by provider,” “Action pending,” or “Unknown.”

Avoid custom switches, glowing bell icons, a permanent notification counter, or a decorative glass panel that looks like it can control Focus. Apple’s [Managing notifications HIG](https://developer.apple.com/design/human-interface-guidelines/managing-notifications) puts people in control of timing, Focus, summaries, and app-level settings.

## Liquid Glass belongs to the app-owned context

Apple’s Liquid Glass guidance says standard system components automatically adopt the material and recommends minimizing custom backgrounds in controls and navigation. Apply that principle to notification settings:

1. build the hierarchy with standard SwiftUI navigation, Form, List, sheets, and controls;
2. allow the system bars and controls to adopt the current appearance;
3. use one restrained glassEffect for an app-owned review action or compact status group only if it adds functional focus;
4. use a GlassEffectContainer when several custom glass elements must morph together;
5. test reduced transparency, reduced motion, large text, increased contrast, and content scrolling beneath controls.

Do not use Liquid Glass to imitate the system’s notification banner, Lock Screen, Dynamic Island, or Notification Center. A notification is system-owned and should be supplied through UserNotifications. A fake banner creates the wrong expectations around timing, permissions, actions, and delivery.

### Suggested glass roles

| Role | Good use | Avoid |
| --- | --- | --- |
| Status capsule | “Notifications allowed” or “Settings need review” | Replacing the actual system setting |
| Review action | “Review generated message” | Auto-sending on tap |
| Schedule summary | Date and local schedule status | Hiding timezone or recurrence semantics |
| Privacy callout | Redacted-preview policy | Putting the secret body beneath translucency |
| Recovery action | “Open Settings” or “Use in-app history” | Pretending to repair a denied entitlement |

Keep color restrained. Use system colors and increased-contrast variants. Treat the glass effect as a functional layer, not the visual identity of every row.

## The action-review sheet

For an actionable notification or AI proposal, use an app-owned review sheet before scheduling or sending:

~~~text
Review notification

Why this exists
Source: Meeting with Jordan
Revision: 42

Title
[ Meeting starts soon ]

Message
[ Your meeting starts at 10:00 AM. ]

Action buttons
[ Open meeting ] [ Mark ready ]

Timing
Today at 9:45 AM

Urgency
Active — normal notification behavior

Privacy
Lock screen text is redacted

[Discard]                         [Schedule]
~~~

The primary action should say what will happen. “Schedule” is clearer than “Done.” If a remote provider is involved, distinguish “Save draft” from “Send through provider.” If a notification will mutate a domain record from an action, explain that before the system presents it.

When the proposal is model-generated, show the source record and revision, give the person edit controls, and make the generated status obvious without using alarmist colors. The person should be able to discard the proposal without losing the underlying record.

## Designing urgency without coercion

Use interruption level as a policy explanation:

| Product language | Appropriate presentation |
| --- | --- |
| “Available when you’re ready” | Passive or in-app history |
| “A useful update” | Active |
| “This is happening now” | Time Sensitive only when a real current event justifies it |
| “Health or safety emergency” | Critical only with the Apple entitlement and narrow use case |

Never design a “boost engagement” control that silently upgrades urgency. Never put a promotional offer behind Time Sensitive. Do not say “we will alert you no matter what”; the person, Focus, scheduled summary, system state, connectivity, and device settings remain authoritative.

Use a small explanation next to an app-owned policy choice, not a fake system label. If the person cannot change a system behavior inside the app, link to the actual system settings.

## Communication notification design

Communication notifications should feel like direct human context, not a marketing card:

- show the real sender or group only when the app has the proper communication identity and privacy policy;
- use a redacted lock-screen version for sensitive content;
- separate incoming and outgoing communication records;
- support a small number of useful actions such as Reply, Mark Read, or Call Back;
- use text input only when a short reply is the actual task;
- show a Focus-status explanation only when the documented capability and authorization exist;
- never infer that silence means rejection, ignoring, or loss of interest.

Do not style every ordinary update as a communication notification. The system’s distinction is meaningful: messaging and calling have participant context and different Focus behavior; a purchase update or content recommendation does not.

## Action button design

Actionable notifications have less space than an app screen. Design for:

- two most important actions first;
- short titles that remain understandable without the full app;
- a destructive action only when the user can recognize irreversible impact;
- an authentication-required action when the documented policy requires it;
- a foreground action only when the app must be opened to complete the route;
- a typed action identifier independent of localized button text;
- a safe no-op when the record is stale or the action is unknown.

For a text-input action, the placeholder should describe the expected response and the app should validate length, privacy, account state, and current record before sending. Do not persist raw text input in logs or notification userInfo unnecessarily.

## Notification preview and attachment design

A notification preview may appear on a Lock Screen, Apple Watch, CarPlay, or a shared display. Use:

- a title with enough context but no secret;
- a body that is useful when read out of context;
- thread grouping for one conversation or task;
- a category that maps to known actions;
- an attachment only when the media remains useful and privacy-safe;
- a text-only fallback if the attachment is unavailable, too large, or disallowed.

Do not assume custom typography or a full-color brand image will appear as designed in every system surface. The system can crop, group, summarize, hide, or transform the presentation.

## Content and service extension design

Treat extension UI as a compact projection:

~~~text
main-app record
    -> redacted payload
    -> service extension transformation
    -> content extension category match
    -> system-owned notification chrome
~~~

The service extension should fail open to safe original content, not to decrypted secrets or blank marketing copy. The content extension should render quickly from immediate data and use the documented extension point. It should not look like a hidden second app or require a network request before the first meaningful frame.

Keep extension visuals compatible with Dynamic Type and accessibility. Do not assume the extension shares all app navigation, environment objects, model containers, or authentication state. If an action needs the main app, send a typed route and show a clear handoff.

## Settings and fallback copy

Prefer specific, calm copy:

| State | Copy |
| --- | --- |
| Not determined | “Turn on notifications when you want reminders and status updates from this app.” |
| Denied | “Notifications are off in iPhone Settings. You can still review updates here.” |
| Partial | “Alerts are allowed, but sound or badges are disabled.” |
| Provider unknown | “We saved the update, but delivery is not confirmed.” |
| Stale action | “This notification is out of date. Open the current item to continue.” |
| AI unavailable | “Smart suggestions are unavailable on this device. You can write the notification yourself.” |
| Attachment fallback | “The media could not be loaded. The text update is still available.” |

Avoid “failed to notify” when the app only knows that the request was accepted. Name the layer that is unknown: request scheduling, provider acceptance, device receipt, system presentation, or user action.

## Accessibility and alternate input

Test the actual task:

1. open notification settings;
2. understand the current authorization state;
3. open system settings;
4. edit and review a notification proposal;
5. schedule or discard it;
6. complete or cancel an actionable notification;
7. recover from a stale action.

Check VoiceOver order and labels, Dynamic Type at the largest supported sizes, increased contrast, Reduce Motion, reduced transparency, bold text, color-independent status, keyboard navigation, pointer interaction, and Switch Control. Do not encode “scheduled,” “delivered,” or “unknown” only through color or a glass tint.

For custom glass controls, ensure the semantic control remains discoverable when the effect is reduced or removed. For notification content extensions, test the actual system extension surface rather than only the main-app preview.

## AI proposal design

Make model output visibly provisional:

~~~text
Suggested by on-device intelligence
Based on: Order 204, revision 7
You decide whether to schedule it.
~~~

Use the model for bounded wording, grouping, or a proposed reminder time when the source data is already deterministic. Do not use it to choose private recipients, infer a person’s Focus state, escalate interruption, claim delivery, or commit an irreversible action.

Show the data source, revision, model availability state, and fallback. If the record changes while the model runs, mark the proposal stale. If the model is unavailable, remove the AI framing and present the deterministic compose route.

## Proof-oriented design review

Before calling the visual work complete, verify:

- the screen does not impersonate a system notification;
- the primary app-owned action is clear and reversible;
- system settings are represented as refreshed state;
- privacy is visible in the preview policy;
- urgency language does not encourage Time Sensitive or Critical misuse;
- communication design uses real contact context only for real communication;
- the content extension has a category and immediate fallback;
- the service extension has a safe timeout path;
- AI proposals show source/revision and require review;
- Liquid Glass is sparse, functional, and tested with reduced effects;
- VoiceOver, Dynamic Type, contrast, Reduce Motion, and alternate input complete the task.

## Sources

- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications)
- [Managing notifications HIG](https://developer.apple.com/design/human-interface-guidelines/managing-notifications)
- [User Notifications](https://developer.apple.com/documentation/usernotifications)
- [Asking permission to use notifications](https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications)
- [UNNotificationSettings](https://developer.apple.com/documentation/usernotifications/unnotificationsettings)
- [Declaring your actionable notification types](https://developer.apple.com/documentation/usernotifications/declaring-your-actionable-notification-types)
- [UNNotificationCategory](https://developer.apple.com/documentation/usernotifications/unnotificationcategory)
- [UNNotificationAction](https://developer.apple.com/documentation/usernotifications/unnotificationaction)
- [UNTextInputNotificationAction](https://developer.apple.com/documentation/usernotifications/untextinputnotificationaction)
- [UNNotificationInterruptionLevel](https://developer.apple.com/documentation/usernotifications/unnotificationinterruptionlevel)
- [Customizing the appearance of notifications](https://developer.apple.com/documentation/usernotificationsui/customizing-the-appearance-of-notifications)
- [Modifying content in newly delivered notifications](https://developer.apple.com/documentation/usernotifications/modifying-content-in-newly-delivered-notifications)
- [Handling Communication Notifications and Focus Status Updates](https://developer.apple.com/documentation/UserNotifications/handling-communication-notifications-and-focus-status-updates)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
