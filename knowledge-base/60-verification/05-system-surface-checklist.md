# System Surface Checklist

Use when a feature is exposed outside the main app.

- [ ] The visible in-app use case works without the system surface.
- [ ] AppIntent metadata is human-readable and localized.
- [ ] AppEntity exposes only the necessary data.
- [ ] EntityQuery resolves stable identifiers and missing records.
- [ ] Widget/extension code does not assume the main app process is alive.
- [ ] Widget actions perform useful work; links are used when opening is the goal.
- [ ] Live Activity lifecycle has start/update/end rules.
- [ ] Notifications route to typed navigation and validate targets.
- [ ] Background work is resumable, cancellable, and idempotent.
- [ ] Siri/Spotlight/Shortcuts behavior is tested from the system surface.
- [ ] Locked-device or permission-restricted behavior is handled where relevant.
- [ ] Deep links work from cold launch and an existing navigation stack.

## Surface-specific evidence matrix

| Surface | Minimum route checks | Stronger proof |
| --- | --- | --- |
| App Intents, Siri, Shortcuts, Spotlight, and visual-intelligence entry points | Intent/entity metadata, localization, stable identifiers, query misses, authorization, confirmation, and deep-link routing | Invoke from the real system surface with the app terminated, locked/restricted where relevant, and signed with the intended capabilities. |
| Widgets and controls | Timeline/intent configuration, placeholder/snapshot states, reload hints, extension process assumptions, action idempotence, and stale data | Install the signed artifact on a supported physical device and exercise the surface after termination, reload, permission changes, and data refresh. |
| Live Activities | Attribute/content-state model, start/update/end/stale rules, lock-screen and Dynamic Island layouts, push token/server reconciliation, and privacy | Test the full ActivityKit lifecycle with the actual device, entitlement, APNs environment, server state, and expiration/recovery paths. |
| Notifications and background work | Authorization/settings, categories/actions, notification-to-route mapping, task registration, expiration, cancellation, and resumability | Reset permissions and use a physical device to verify delivery, lock state, background scheduling, termination, and cold-launch routing. |
| Extensions, Watch, CarPlay, App Clips, and share/file destinations | Separate target membership, host lifecycle, supported context, capabilities, handoff/deep links, and resource limits | Invoke from the real host/system or paired device using the signed distribution artifact; record host/account/vehicle/pairing state. |

## Process and privacy boundaries

- [ ] The system surface still communicates a useful state when the main app process is terminated, suspended, locked, or unable to access protected data.
- [ ] Extension and widget code handles stale, missing, unauthorized, offline, and partially synchronized records without exposing private content in previews or notifications.
- [ ] Privacy manifests, App Intents entities, widget snapshots, Live Activity content, notification previews, and deep-link parameters expose only the data necessary for the surface.
- [ ] Server/APNs/account state is recorded separately from local UI and compile evidence; a local push simulation does not prove delivery from the production environment.
- [ ] Test plans include system-surface UI tests where automatable, but physical-device/system invocation remains a separate proof layer.

## Evidence record

- [ ] Record surface, target/extension bundle identifier, OS/device, build/version, signed state, capability/entitlement, permission/account state, process state, data freshness, and expected versus observed behavior.
- [ ] Record whether the result came from a preview, fixture, simulator, unit/UI test, signed device, TestFlight, App Store submission, or production environment.
- [ ] Use the narrowest claim supported by the evidence; “the widget renders in preview” is not “the widget refreshes on a user’s device,” and “the intent appears” is not “the action completed successfully.”

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents/)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [UserNotifications](https://developer.apple.com/documentation/usernotifications)
- [BackgroundTasks](https://developer.apple.com/documentation/backgroundtasks)
- [AppShortcutsProvider](https://developer.apple.com/documentation/AppIntents/AppShortcutsProvider)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [Widgets, Live Activities, and Controls](https://developer.apple.com/documentation/appintents/widgets-live-activities-and-controls)
- [Developing a WidgetKit strategy](https://developer.apple.com/documentation/WidgetKit/Developing-a-WidgetKit-strategy)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/ActivityKit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases/)
- [TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview)
