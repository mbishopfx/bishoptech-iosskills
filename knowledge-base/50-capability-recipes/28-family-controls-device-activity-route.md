# Family Controls and Device Activity capability route

Use this route for a focus schedule, parental-control workflow, website-usage report, or privacy-preserving app/category restriction. It is a multi-target system feature. Plan the entitlement, authorization, opaque selection, extension lifecycle, and physical system effect before building the polished SwiftUI surface.

## Outcome

Build a feature that can:

- explain and request Family Controls authorization;
- let a person select apps, categories, and web domains through the privacy-preserving picker;
- schedule Device Activity monitoring;
- react to intervals and thresholds in a monitor extension;
- apply or clear Managed Settings restrictions;
- customize a system shield and respond to shield actions;
- render a privacy-preserving Device Activity report;
- reconcile revocation, stale schedules, failed extensions, and effective-state uncertainty;
- optionally use on-device AI to propose a schedule or summarize an approved report without becoming the enforcement authority.

This route is not a surveillance architecture. The framework’s privacy model is part of the product requirement.

## Select the smallest route

| Need | Route | Avoid adding |
| --- | --- | --- |
| Let a person select a private scope | Family Controls + FamilyActivityPicker | A custom app catalog or raw identity database |
| Run a recurring focus schedule | DeviceActivityCenter + DeviceActivitySchedule | A local Timer as a monitoring substitute |
| Act at a threshold | DeviceActivityEvent + DeviceActivityMonitor extension | Polling raw usage from the main app |
| Block selected apps/sites/categories | ManagedSettingsStore + ShieldSettings | A fake in-app modal that does not enforce |
| Customize the blocked surface | Managed Settings UI extensions | Network-dependent shield rendering |
| Let a person respond to a shield | ShieldActionDelegate | Assuming the extension knows the readable app/domain name |
| Show usage data | DeviceActivityReport + report extension | Exporting report data to a server by default |
| Report web use | Screen Time framework | Treating web history APIs as general activity telemetry |

Add only the extensions required by the user outcome. Every extension increases target membership, signing, App Group, lifecycle, and evidence work.

## Target and entitlement preflight

Write the register before implementation:

| Target | Responsibility | Preflight |
| --- | --- | --- |
| iOS/iPadOS app | Authorization, picker, editor, report host, reconciliation | Family Controls capability, usage/copy review, target availability |
| Device Activity Monitor extension | Schedule and threshold callbacks | Device Activity Monitor template, Family Controls entitlement, principal class |
| Device Activity Report extension | Report scenes and SwiftUI output | Report extension target, privacy sandbox, context/filter contract |
| Shield Configuration extension | Shield appearance | Managed Settings UI target, fast deterministic configuration |
| Shield Action extension | Shield button actions | Managed Settings action target, opaque token handling, response contract |
| App Group container | Minimal commands and reconciliation markers | Shared container membership and versioned schema |
| Developer account | Distribution entitlement | Family Controls distribution request and approval |

Xcode’s Family Controls capability adds the entitlement for development, but distribution needs the approved entitlement path. Verify the signed app and each extension, not only the Xcode capability checkbox.

## Route A: authorize and select

1. Explain whether this is individual or child/guardian authorization.
2. Call AuthorizationCenter.shared through the current async or completion-handler API.
3. Observe authorizationStatus after the result and on foreground.
4. Present FamilyActivityPicker only when the authorization state allows it.
5. Store the minimum selection needed for the schedule.
6. Record the selection version and a re-selection path.
7. Clear or invalidate local tokens when authorization is revoked.

Do not store the picker’s opaque tokens in analytics, logs, AI prompts, or a server. If the product needs a friendly scope summary, use supported labels or counts and clearly identify what the app cannot know.

## Route B: create and submit monitoring

Create one DeviceActivityName per app-owned monitoring intent. Build:

- DeviceActivitySchedule with local start/end components;
- repeats policy;
- optional warning time;
- DeviceActivityEvent names;
- threshold values;
- selected application/category/domain tokens.

Validate:

- interval start/end are coherent;
- the repeats policy matches the product copy;
- warnings are meaningful for the time zone;
- threshold units and values are supported;
- selection tokens are current;
- event names are stable and unique;
- the requested monitor does not conflict with a previous local record.

Submit with DeviceActivityCenter.startMonitoring. Then read back the current activities and schedule. Store “submitted,” “observed,” “failed,” or “unknown”; never show “active” because the call returned without error.

On disable or replace:

1. stop the old named activity;
2. clear or update Managed Settings according to policy;
3. write the new version;
4. start the replacement;
5. reconcile the current system list;
6. show the observed result.

## Route C: monitor extension

The Device Activity Monitor extension responds to:

- interval start and end;
- warnings before start and end;
- event threshold warnings;
- event threshold reached.

Keep the callback path small:

    callback
        -> validate activity/event name
        -> read current app-group policy version
        -> apply or clear Managed Settings
        -> write a redacted result marker
        -> return

Do not call the model, network, or a long-running database migration in the callback. If a richer action is needed, record a bounded command and let the main app process it later.

The callback may run when the main app is not open. It may also be delayed, interrupted, or missing due to the system’s monitoring conditions. The app should expose the last observed callback and avoid claiming exact real-time enforcement.

## Route D: apply Managed Settings

Use a ManagedSettingsStore to apply the exact settings approved by the person:

- app tokens;
- category policies;
- web-domain tokens;
- web-domain category policies.

Keep desired configuration and effective state separate. Setting a property to nil deletes your app’s configuration for that setting, but the system may combine settings from multiple sources. On disable, clear only the store values owned by this feature.

Named stores can isolate independent policies, but they do not create additional authority. Include the store name and policy version in the reconciliation record.

If a token is expired, use the current ManagedSettingsStore refresh APIs where appropriate or ask the person to select again. Never infer identity from a token that the system no longer accepts.

## Route E: shield and action extensions

The Shield Configuration extension should return a compact, accessible ShieldConfiguration without network access. Provide a title, reason, and primary/secondary labels that make sense when the main app is unavailable. The system supplies defaults if the extension does not respond in time.

The Shield Action extension receives the action and an opaque token. Return a documented response. For a request-more-time flow:

1. record an expiring app-group command with a random command ID;
2. return the supported response;
3. let the main app later present approval or policy editing;
4. re-read Managed Settings and Device Activity state after any change.

Do not claim that a shield action unlocked the app unless the authoritative system state confirms it.

## Route F: report

Use DeviceActivityReport from the main app with a stable context and a DeviceActivityFilter. The report extension renders a SwiftUI view from the system-provided privacy-preserving data.

Treat the report as:

- a selected time range;
- a selected member/device scope;
- a selected app/category/domain filter;
- a selected context such as chart or list;
- a system-provided view, not an app-owned raw database.

Do not make a report view dependent on a remote API. Do not copy report values to a shared container unless the current API and privacy review explicitly allow the exact workflow.

## State and reconciliation model

| State | Source | User-facing meaning |
| --- | --- | --- |
| draft | App | Policy is being edited; nothing submitted |
| awaitingAuthorization | AuthorizationCenter | The system decision is pending |
| authorizedNoSelection | Family Controls | The feature can ask for a scope |
| selected | FamilyActivitySelection | A token-backed scope exists |
| submitted | DeviceActivityCenter/ManagedSettings request | The app sent a request |
| observed | Re-read system state | The app confirmed the current system representation |
| monitoring | Extension callback history | A callback has been received, not a continuous telemetry guarantee |
| shielded | Managed Settings action plus observed surface | A shield was observed on the tested device |
| reportReady | DeviceActivityReport host | The system can render the selected report |
| stale | Timestamp/foreground reconciliation | The displayed state is older than policy allows |
| revoked | AuthorizationCenter or failed token | Reauthorization and re-selection are required |
| failed | Error record | The feature did not complete; preserve recovery |
| disabled | Clear result | App-owned settings are removed according to policy |

The “observed” state matters. It prevents a local app from claiming that an external system has adopted the requested policy.

## Privacy and abuse boundaries

- Request only the capability and scope needed.
- Keep opaque tokens opaque.
- Avoid raw child names, app identity maps, and detailed browsing history.
- Do not use the route to monitor another adult without clear authority.
- Do not use AI to infer diagnosis, addiction, psychological state, or parenting quality.
- Do not send extension data to a server by default.
- Redact command logs and crash data.
- Expire app-group commands and delete stale policy records.
- Explain how a person can edit, disable, or revoke the feature.

Apple’s [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy) recommends specific requests, clear use explanations, and on-device processing where possible. Family Controls adds a system privacy model on top of those general practices.

## AI route

Use a local model only after the person intentionally starts a proposal flow:

    user goal
        -> typed schedule proposal
        -> validate date components and thresholds
        -> show selection and consequence
        -> explicit approve
        -> submit monitoring/settings

The proposal should contain:

- local time-zone assumption;
- repeat behavior;
- warning behavior;
- selected scope reference without raw token values;
- intended effect;
- reset/disable path;
- model identifier and generated time.

The model cannot:

- choose a private scope without the person using the picker;
- bypass Family Controls authorization;
- call Managed Settings directly;
- decide that an app should be blocked because of a hidden classification;
- infer a person’s health or mental state from activity data;
- produce a guarantee that the policy improves focus or safety.

## Build sequence

1. Add capability and target register.
2. Build authorization state and copy.
3. Add picker and token lifecycle.
4. Add pure schedule/event validation.
5. Add Device Activity submit/reconciliation.
6. Add a monitor extension with a deterministic test policy.
7. Add Managed Settings clear/apply.
8. Add shield configuration and action extensions.
9. Add a report extension and accessible report fixture.
10. Add optional AI proposal/review.
11. Run signed physical-device and distribution entitlement evidence.

Do not start with a glass dashboard. The system contract is the feature.

## Acceptance checklist

- [ ] Member type and authority are explicit.
- [ ] Family Controls capability is on every required target.
- [ ] Distribution entitlement request is tracked separately from development.
- [ ] Authorization status is observed on launch and foreground.
- [ ] FamilyActivityPicker owns selection.
- [ ] Tokens are opaque, versioned, and revocable.
- [ ] Schedule/event validation is deterministic.
- [ ] DeviceActivityCenter requests are reconciled with system state.
- [ ] Monitor extension callbacks are short and idempotent.
- [ ] Managed Settings desired/effective state is separate.
- [ ] Shield configuration works with default fallback and no network.
- [ ] Shield action does not assume readable identities.
- [ ] Report extension stays within its privacy sandbox.
- [ ] AI proposals are reviewed before side effects.
- [ ] VoiceOver, Dynamic Type, reduced transparency/motion, and age-appropriate copy are tested.
- [ ] Physical device, extension, entitlement, TestFlight, and release evidence are recorded.

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
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
