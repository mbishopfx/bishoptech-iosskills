# Family Controls, Device Activity, and Managed Settings

Apple’s Screen Time suite is a privacy-sensitive system capability, not a normal analytics API. Family Controls authorizes a parental-control app, Device Activity monitors scheduled application or website activity through extensions, and Managed Settings applies restrictions or shields. The user selects opaque applications, categories, and web domains; the app should not assume it can identify every selected item or read raw child activity.

The central contract is:

    authorized person
        -> privacy-preserving selection
        -> target and extension configuration
        -> scheduled Device Activity monitor
        -> threshold or interval callback
        -> Managed Settings action or report
        -> system-owned shield/report surface
        -> explicit recovery and revocation handling

This route is useful for parental controls, personal focus tools, study schedules, bedtime routines, website-usage reports, and consent-driven digital-wellbeing features. It is not permission to surveil people, bypass system privacy, or claim a medical or behavioral outcome.

## The framework boundary

| Layer | Framework/API | Responsibility | Do not infer |
| --- | --- | --- | --- |
| Authorization | Family Controls, AuthorizationCenter | Request and observe authorization for parental controls | That a request means the user approved every future operation |
| Selection | FamilyActivityPicker, FamilyActivitySelection | Let the person choose apps, categories, and domains while preserving privacy | That the app can freely resolve every app/domain identity |
| Schedule and events | Device Activity, DeviceActivityCenter, DeviceActivitySchedule, DeviceActivityEvent | Describe recurring intervals and threshold events | That a callback is a complete activity history |
| Extension monitor | DeviceActivityMonitor | Receive interval and threshold callbacks in an extension | That an extension runs continuously or has unlimited time |
| Enforcement | ManagedSettingsStore, ShieldSettings | Apply app/category/domain shields and other settings | That the app’s configuration alone determines effective system state |
| Shield appearance | Managed Settings UI, ShieldConfigurationDataSource | Customize the system shield presentation | That the app owns the entire system surface or can perform network work in the shield extension |
| Shield actions | ShieldActionDelegate | Respond to a person’s interaction with a shield | That the extension receives the protected item’s readable identity |
| Reports | DeviceActivityReport, DeviceActivityReportExtension, DeviceActivityFilter | Ask the system for a privacy-preserving report rendered by an extension | That report data can be moved to a server or arbitrary app process |
| Web usage | Screen Time, STWebpageController and related APIs | Report web usage, observe configuration, or delete history for the supported route | That Screen Time is the same as Device Activity or a general browser history API |

Apple’s [Screen Time Technology Frameworks](https://developer.apple.com/documentation/screentimeapidocumentation/) groups Family Controls, Managed Settings, and Device Activity. The suite is designed to preserve privacy and keep control in the system and the authorized family context.

## Family Controls authorization

### Entitlement is a product and release boundary

Add the Family Controls capability to the app target and every Screen Time extension target that needs it. Xcode adds the com.apple.developer.family-controls entitlement for development, but distribution requires the Apple Developer Account Holder to request permission for the entitlement. If the app contains a Device Activity Monitor, Device Activity Report, Shield Action, or Shield Configuration extension, submit the same entitlement request for each relevant extension.

Keep these artifacts separate:

1. Xcode capability selection.
2. Entitlements file in the source.
3. Signed app and extension entitlements.
4. Development provisioning status.
5. Distribution capability request and approval.
6. App Store/TestFlight archive validation.

A locally signed development run is not proof that the distribution entitlement is approved.

Use [Configuring Family Controls](https://developer.apple.com/documentation/xcode/configuring-family-controls) and [Requesting the Family Controls entitlement](https://developer.apple.com/documentation/FamilyControls/requesting-the-family-controls-entitlement) for the current project and account process.

### AuthorizationCenter is observable state

Use AuthorizationCenter.shared to request authorization. The current API includes a requestAuthorization(for:) route for a FamilyControlsMember such as an individual, plus an authorizationStatus property and revocation behavior. The authorization experience differs for an individual and a child in a Family Sharing group.

Model the state explicitly:

| State | Meaning | Product response |
| --- | --- | --- |
| unavailable | Target, OS, account, or entitlement cannot use the route | Explain limitation and offer a non-enforcing feature |
| notDetermined | The app has not requested authorization | Explain the feature and request at a purposeful entry point |
| authorized | The system accepted the route for the selected member | Allow picker, schedule, shield, and report paths that are separately configured |
| denied | The request was refused or failed | Preserve the app; show the exact next safe action |
| revoked | Authorization changed externally | Void local assumptions, clear or reconcile settings, and ask again only in a valid context |
| restricted | The environment prevents the route | Do not retry in a loop; show a configuration/support message |

Authorization can change because of external events such as a family-account change or a Settings action. Observe status on launch and foreground. Do not treat a cached authorized flag as durable authority.

Apple’s [AuthorizationCenter](https://developer.apple.com/documentation/FamilyControls/AuthorizationCenter) and [Family Controls](https://developer.apple.com/documentation/familycontrols) pages describe this relationship.

## Privacy-preserving selections

FamilyActivityPicker lets the person choose applications, categories, and web domains. FamilyActivitySelection exposes opaque values and tokens for those selections. The selection is designed so the app can pass the tokens to Managed Settings and Device Activity without automatically learning the private identity of every selected item.

Design rules:

- Store the selection only when the product has a clear need.
- Treat application, category, and domain tokens as revocable capabilities, not stable app names.
- Expect a selection to become invalid when authorization is revoked.
- Do not log token values, serialize them into analytics, or send them to a model or server by default.
- Show human-readable labels only when Apple’s supported label surface supplies them.
- Use the picker as a system-owned privacy surface; do not rebuild it with a custom app catalog.

If a user, parent, or guardian revokes authorization, tokens provided while authorized become void. Make token refresh or re-selection a visible recovery path.

Use [FamilyActivityPicker](https://developer.apple.com/documentation/FamilyControls/FamilyActivityPicker) and [FamilyActivitySelection](https://developer.apple.com/documentation/FamilyControls/FamilyActivitySelection) for the current selection and token behavior.

## Device Activity scheduling and monitoring

### Schedule intervals, not a raw timeline

DeviceActivitySchedule uses DateComponents for an interval start and end, a repeats flag, and an optional warning time. It represents a recurring monitoring window, not a guarantee that the app will receive a sample for every moment.

DeviceActivityEvent represents an application, category, or website activity event with a threshold. Build events from the selected opaque tokens and give each event a stable app-owned name.

The app-owned state should include:

- schedule name;
- local time-zone policy;
- start/end components;
- repeats;
- warning time;
- event name and threshold;
- selected token set and selection version;
- last submit result;
- last observed system schedule;
- revocation and token-expiry state.

Do not use a local Timer as proof that Device Activity is monitoring. Submit through DeviceActivityCenter and query the current activities and schedule when the app launches or becomes active.

### DeviceActivityCenter is a request boundary

DeviceActivityCenter can start and stop monitoring, expose current activities, return a schedule, and return events for a named activity. The operation can throw a MonitoringError. Handle the error and keep the local row in a submitted, observed, failed, or unknown state.

The route is:

    local draft
        -> selection valid
        -> schedule and events validated
        -> startMonitoring
        -> system state re-read
        -> extension callbacks
        -> app-owned action and projection

Do not auto-retry startMonitoring forever. A device may have a limit, an extension may be misconfigured, authorization may have changed, or a prior schedule may still exist.

### DeviceActivityMonitor is an extension process

Subclass DeviceActivityMonitor and designate it as the principal class of a Device Activity Monitor extension. The extension receives callbacks such as:

- intervalWillStartWarning;
- intervalDidStart;
- eventWillReachThresholdWarning;
- eventDidReachThreshold;
- intervalWillEndWarning;
- intervalDidEnd.

Use the callbacks to perform small, deterministic actions such as applying a ManagedSettings shield or writing a minimal app-group command record. Do not assume the extension can do long-running work, access arbitrary app state, make network requests, or keep a full UI model alive.

Apple documents that activity intervals and threshold callbacks depend on device use and system monitoring conditions. A callback is a system event, not a high-frequency telemetry stream. Record the callback timestamp and the named activity, then reconcile the current system state.

Use [DeviceActivity](https://developer.apple.com/documentation/deviceactivity), [DeviceActivityCenter](https://developer.apple.com/documentation/deviceactivity/deviceactivitycenter), [DeviceActivitySchedule](https://developer.apple.com/documentation/deviceactivity/deviceactivityschedule), [DeviceActivityEvent](https://developer.apple.com/documentation/deviceactivity/deviceactivityevent), and [DeviceActivityMonitor](https://developer.apple.com/documentation/deviceactivity/deviceactivitymonitor) as the API source set.

## Managed Settings and shields

### ManagedSettingsStore owns app configuration, not all effective state

ManagedSettingsStore applies settings for the current user or device. Its groups include ShieldSettings for apps, categories, and web domains, plus other settings groups. Assigning nil deletes the app’s configuration for that setting. The system determines effective behavior from all settings it receives, so the app must not claim that its value alone explains the final device state.

Use a named store when multiple features need isolated configuration and when the current target supports that design. Keep a reconciliation record:

| Field | Purpose |
| --- | --- |
| store name | Identify the app-owned configuration scope |
| desired settings | What the user approved |
| last write | When the app submitted a change |
| last observed state | What the current API can inspect |
| source | Schedule callback, manual action, or recovery |
| revocation state | Whether tokens are still valid |
| reset policy | What happens on disable, logout, or authorization loss |

For a shield, the relevant route includes applications, application categories, web domains, and web-domain categories. Use the current ShieldSettings API to confirm the exact token types and policy cases.

### Enforcement is system-owned

When the system covers an app or site with a shield, the app does not own the launch surface. The system decides when the shield appears and applies the effective settings. The app can provide a custom shield configuration and handle defined shield actions through extensions.

Managed Settings can shield:

- selected application tokens;
- selected web-domain tokens;
- application categories;
- web-domain categories.

The user needs a truthful explanation of what is restricted, when it is active, and how to change or revoke it. Do not represent a local toggle as proof that another device is currently blocked.

Use [Managed Settings](https://developer.apple.com/documentation/managedsettings), [ManagedSettingsStore](https://developer.apple.com/documentation/managedsettings/managedsettingsstore), and [ShieldSettings](https://developer.apple.com/documentation/managedsettings/shieldsettings).

## Shield configuration and actions

### ShieldConfigurationDataSource

Managed Settings UI lets a Shield Configuration extension customize a shield’s appearance with a title, subtitle, icon, colors, blur style, and primary/secondary button labels. The system provides defaults for omitted values.

The extension receives a token-aware request and must respond quickly. Apple documents a sandbox that prevents the shield extension from making network requests or moving sensitive content outside the extension’s address space. If the extension is slow, the system can show a default appearance.

Design the shield as a system interruption:

- explain why access is restricted;
- identify the action without leaking private selection details;
- provide one primary recovery or request path;
- use high-contrast text and meaningful button labels;
- avoid a decorative glass layer that makes the shield look optional;
- provide a fallback for the default system appearance.

Use [Managed Settings UI](https://developer.apple.com/documentation/managedsettingsui), [ShieldConfiguration](https://developer.apple.com/documentation/managedsettingsui/shieldconfiguration), and [ShieldConfigurationDataSource](https://developer.apple.com/documentation/managedsettingsui/shieldconfigurationdatasource).

### ShieldActionDelegate

Subclass ShieldActionDelegate in a Shield Action extension when the shield exposes an action. The system supplies a ShieldAction and an opaque application, category, or web-domain token. Apple specifically protects Family Sharing privacy by not providing the shielded item’s readable identity to the action extension.

Return only a documented ShieldActionResponse. Keep actions short and deterministic. If the product wants to request an exception or record a reason, write a minimal app-group command or event and let the app present the next user-facing step later. Do not open a network path from the extension.

Use [ShieldActionDelegate](https://developer.apple.com/documentation/managedsettings/shieldactiondelegate) for the current method and response names.

## Device Activity reports

DeviceActivityReport is a SwiftUI view that asks a Device Activity Report extension to render a report for a selected context and DeviceActivityFilter. The system provides activity data to the extension in a privacy-preserving way. Apple documents that the report extension runs in a sandbox and cannot make network requests or move sensitive content outside the extension’s address space.

The report route is:

    app-owned filter
        -> DeviceActivityReport(context, filter:)
        -> report extension
        -> DeviceActivityReportScene
        -> SwiftUI report view

Keep report context identifiers stable and meaningful. A context such as weekly bar graph or daily category view belongs to the report contract, not to a generated string. Make the report readable without knowing the identity of every app.

Use [DeviceActivityReport](https://developer.apple.com/documentation/deviceactivity/deviceactivityreport), [DeviceActivityReportExtension](https://developer.apple.com/documentation/deviceactivity/deviceactivityreportextension), [DeviceActivityReport.Context](https://developer.apple.com/documentation/deviceactivity/deviceactivityreport/context), and [DeviceActivityFilter](https://developer.apple.com/documentation/deviceactivity/deviceactivityfilter).

## Screen Time web usage boundary

The Screen Time framework has its own web-usage route, including STWebpageController, STScreenTimeConfigurationObserver, STScreenTimeConfiguration, and STWebHistory. It is not interchangeable with Device Activity:

- Device Activity monitors selected apps, categories, and web domains on schedules and thresholds.
- Screen Time web APIs report or respond to supported web usage and configuration changes.
- Managed Settings applies restrictions and shields.
- Family Controls authorizes the parental-control relationship.

Choose the narrowest route and document whether the product needs selection tokens, scheduled callbacks, a system shield, a report, or web history operations. Use [Screen Time](https://developer.apple.com/documentation/screentime) for the web-specific surface.

## Target and process matrix

| Target/process | Responsibility | Main boundary |
| --- | --- | --- |
| Main iOS/iPadOS app | Authorization, picker, plan editor, report host, reconciliation | User interaction, app lifecycle, settings changes |
| Device Activity Monitor extension | Interval and threshold callbacks | Host termination, limited work, app-group communication |
| Device Activity Report extension | Privacy-preserving report view | Extension sandbox, no network, report context/filter |
| Shield Configuration extension | System shield appearance | Fast response, system-owned invocation, no network |
| Shield Action extension | Defined shield-button response | Opaque tokens, short action, response enum |
| App group store | Minimal commands and reconciliation markers | Shared-container schema, concurrency, sensitive-data minimization |
| Apple Developer account | Distribution entitlement request | Review, provisioning, TestFlight/App Store configuration |

Do not place all logic in the main app and assume the extension can call it later. Build a minimal protocol with versioned records, idempotent commands, and expiry timestamps.

## On-device AI boundary

AI can help a person write a focus schedule, summarize a report they are already allowed to view, or explain a token-backed selection in ordinary language. It must not become a covert observer or a direct enforcement authority.

Safe proposal route:

1. Person states a goal such as “block selected categories from 9 PM to 7 AM.”
2. A local model proposes schedule components and a plain-language explanation.
3. Deterministic code validates date components, repeats, warning time, thresholds, selection scope, and current authorization.
4. The UI shows the selected tokens, schedule, enforcement effect, reset behavior, and missing assumptions.
5. The person explicitly approves.
6. The app submits Device Activity and/or Managed Settings changes.

Safe report route:

1. Person chooses a report context and filter.
2. The system provides the privacy-preserving report to the extension.
3. A local model may summarize only the values the person intentionally exports from the report.
4. The generated text is labeled as a summary and retains time range, units, and missing-data caveats.

Do not send token values, child activity, app identity mappings, shield-action context, or report-extension data to a server or model by default. Do not generate “addiction,” diagnosis, parenting judgment, safety certification, or guaranteed focus claims.

Use [Foundation Models](https://developer.apple.com/documentation/foundationmodels) only with explicit availability, cancellation, data-scope, and review states. The system should be able to enforce a rule without a model.

## Liquid Glass and system-owned surfaces

The main app can use SwiftUI and Liquid Glass to group:

- authorization status and next step;
- selected-scope summary;
- schedule editor;
- enforcement status;
- report filters;
- AI proposal review.

The shield is a different surface. It is system-triggered, time-sensitive, and privacy-sensitive. Use the Managed Settings UI configuration APIs, not a fake in-app shield, for the actual enforcement surface. Keep glass around app-owned controls, not over a blocked system action where transparency could imply that the restriction is optional.

The [Human Interface Guidelines design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles) emphasize agency, responsibility, clear feedback, and privacy. The [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy) and [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass) should shape the app-owned surfaces.

## Evidence boundary

For each feature, capture:

1. Family Controls entitlement and distribution request status.
2. Main-app and extension target membership plus signed entitlements.
3. Authorization flow for the intended member type.
4. Picker selection, opaque-token storage, revocation, and re-selection.
5. Device Activity schedule/event submission and current-system reconciliation.
6. Monitor-extension callbacks, process termination, and recovery.
7. Managed Settings write, clear, named-store, and effective-state behavior.
8. Shield configuration/action on a physical device.
9. Report extension filter/context and sandbox behavior.
10. Privacy review of logs, app-group records, reports, and model inputs.
11. Dynamic Type, VoiceOver, high contrast, reduced motion/transparency, and system shield readability.
12. Development, signed device, TestFlight, and distribution entitlement evidence.

Use the [Family Controls and Device Activity proof matrix](../60-verification/22-family-controls-device-activity-proof-matrix.md) and [compile-oriented recipes](../70-code-recipes/40-family-controls-device-activity-recipes.md) before treating a route as built.

## Sources

- [Screen Time Technology Frameworks](https://developer.apple.com/documentation/screentimeapidocumentation/)
- [Family Controls](https://developer.apple.com/documentation/familycontrols)
- [AuthorizationCenter](https://developer.apple.com/documentation/FamilyControls/AuthorizationCenter)
- [FamilyActivityPicker](https://developer.apple.com/documentation/FamilyControls/FamilyActivityPicker)
- [FamilyActivitySelection](https://developer.apple.com/documentation/FamilyControls/FamilyActivitySelection)
- [Requesting the Family Controls entitlement](https://developer.apple.com/documentation/FamilyControls/requesting-the-family-controls-entitlement)
- [Configuring Family Controls](https://developer.apple.com/documentation/xcode/configuring-family-controls)
- [Device Activity](https://developer.apple.com/documentation/deviceactivity)
- [DeviceActivityCenter](https://developer.apple.com/documentation/deviceactivity/deviceactivitycenter)
- [DeviceActivitySchedule](https://developer.apple.com/documentation/deviceactivity/deviceactivityschedule)
- [DeviceActivityEvent](https://developer.apple.com/documentation/deviceactivity/deviceactivityevent)
- [DeviceActivityMonitor](https://developer.apple.com/documentation/deviceactivity/deviceactivitymonitor)
- [DeviceActivityReport](https://developer.apple.com/documentation/deviceactivity/deviceactivityreport)
- [DeviceActivityReportExtension](https://developer.apple.com/documentation/deviceactivity/deviceactivityreportextension)
- [DeviceActivityFilter](https://developer.apple.com/documentation/deviceactivity/deviceactivityfilter)
- [Managed Settings](https://developer.apple.com/documentation/managedsettings)
- [ManagedSettingsStore](https://developer.apple.com/documentation/managedsettings/managedsettingsstore)
- [ShieldSettings](https://developer.apple.com/documentation/managedsettings/shieldsettings)
- [ShieldActionDelegate](https://developer.apple.com/documentation/managedsettings/shieldactiondelegate)
- [Managed Settings UI](https://developer.apple.com/documentation/managedsettingsui)
- [ShieldConfiguration](https://developer.apple.com/documentation/managedsettingsui/shieldconfiguration)
- [ShieldConfigurationDataSource](https://developer.apple.com/documentation/managedsettingsui/shieldconfigurationdatasource)
- [Screen Time](https://developer.apple.com/documentation/screentime)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
