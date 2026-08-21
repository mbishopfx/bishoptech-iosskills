# Family Controls and privacy-sensitive system surfaces

Family Controls features sit at the intersection of trust, system authority, and visual design. The main app can feel polished and Apple-native, but the most important interactions may be a system authorization sheet, a privacy-preserving picker, a system shield, an extension callback, or a report rendered outside the main process.

Design the experience as:

    explain authority
        -> select a private scope
        -> preview the consequence
        -> approve a schedule or restriction
        -> show system state
        -> make recovery and revocation obvious

The visual goal is not to imitate Screen Time. It is to make the person understand what the app can do, what the system is enforcing, what data stays private, and how to change their mind.

## The trust hierarchy

The screen should distinguish:

1. Authorization: who allowed the feature and whether that authorization is current.
2. Scope: which opaque categories, apps, or domains the person selected.
3. Intent: the schedule, threshold, or restriction the person wants.
4. System state: what the app last observed from Device Activity or Managed Settings.
5. User-facing effect: what is currently blocked, monitored, or reportable.
6. Generated proposal: any AI suggestion that is not yet approved.

Do not show a single green “Protected” badge for all six. A badge can conceal a revoked token, an unsent schedule, a failed extension, or an effective-state difference.

## Authorization screen

The pre-authorization screen should answer:

- Why does this feature need Family Controls?
- Is the person managing their own device or a child’s device?
- What will the system let the app do?
- What will the app not learn?
- What will happen if authorization is revoked?
- What is the next action?

Use one focused primary action to request authorization. Avoid adding a “not now” escape that leaves the person uncertain about whether the system sheet was reached or whether the feature is half-configured. After the system result, show the actual state and a recovery path.

Design states separately:

| State | Content | Action |
| --- | --- | --- |
| Not configured | Purpose, privacy summary, member type | Request authorization |
| System sheet active | Minimal app chrome behind the system UI | Let the system own the decision |
| Authorized | Member type, selection status, next setup step | Choose scope or build schedule |
| Denied | Plain-language consequence | Try again where valid or continue without enforcement |
| Revoked | Explain that selected tokens are no longer valid | Reauthorize and select again |
| Distribution unavailable | Explain that production access needs entitlement approval | Keep development/demo route separate |

Do not draw a custom approximation of the Family Controls authorization sheet. Use the system request and design the surrounding state.

## Scope selection

FamilyActivityPicker is a privacy boundary and should feel like one. The app’s surrounding UI can explain the selection, but it should not imply that the app has a full database of a child’s applications and websites.

Good scope summary:

- “3 app categories and 2 websites selected”
- “Selection is stored as protected tokens”
- “Changing authorization invalidates this selection”
- “The system will use this scope for the schedule you approve”

Avoid:

- naming every selected app when the framework only gives you opaque tokens;
- showing an invented icon or bundle identifier;
- uploading selection tokens to a server;
- presenting a “scan all apps” action that overstates access;
- treating category selection as exact app-level identity.

If the product needs labels, use Apple’s supported activity-label route and a safe fallback such as category count. Do not manufacture identity from token bytes.

## Schedule editor

A Screen Time-style schedule is a policy editor. Make the policy legible:

| Section | Must show |
| --- | --- |
| Scope | selected categories/apps/domains, selection version, change action |
| Time | local start/end, time-zone behavior, repeating or one-time |
| Thresholds | activity event, unit, threshold, warning behavior |
| Effect | shield, report, notification, or app-owned reminder |
| Recovery | how to disable, edit, revoke, or handle stale tokens |
| Authority | person/member type, authorization state, last observed system state |

Use native forms, pickers, date components, and semantic controls. The resulting layout can use Liquid Glass for grouping and review, but the actual policy values should remain readable without material effects.

Before Apply, show a summary:

    Selected scope: chosen categories and domains
    Schedule: 9:00 PM–7:00 AM, repeats daily
    Effect: system shield selected apps and websites
    Data: app receives callbacks and privacy-preserving report data
    Reset: edit or disable from this screen; revocation invalidates tokens

Do not call a schedule “active” until the app has observed the system state.

## Shield design

A shield interrupts another app or website. It should be:

- immediate;
- understandable without opening the main app;
- readable in bright and dim environments;
- accessible with VoiceOver and large text;
- calm rather than punitive;
- clear about the primary next action;
- resilient if the configuration extension is slow or unavailable.

The shield extension’s custom appearance is a small response to a system-owned surface. Keep text short. Avoid a decorative glass panel that makes the restriction look like an in-app modal. If the app uses a branded icon or color, ensure the system still communicates the reason and action.

Shield action buttons should use ordinary language:

- “Ask for more time”
- “Open focus settings”
- “Return”
- “Close”

Do not promise that an action will immediately unlock another device. A ShieldActionDelegate response is an extension result, not proof that the system changed its effective state.

## Report design

DeviceActivityReport is a report surface, not a raw-data browser. A good report provides:

- a clear time range;
- the selected scope and any filter;
- units and segment interval;
- a privacy note;
- an accessible summary;
- a missing/partial data state;
- a way to change context without losing the task;
- no pressure to export.

Use chart patterns only when they clarify change over time. A bar graph can show duration; a pie graph can show distribution; a list can show totals and exact values. Provide an equivalent textual route and do not rely on color alone.

The report extension runs in a privacy-preserving sandbox. Design the report so it does not depend on network fetches, remote images, or main-app mutable state. If the app offers an AI explanation, make it a separate, user-started summary of values the person is allowed to see.

## States across processes

The main app, monitor extension, shield extension, action extension, and report extension do not share a single view lifecycle. Use visible state names:

| State | Main app treatment | Extension treatment |
| --- | --- | --- |
| submitted | Show “request submitted” with timestamp | Wait for system invocation |
| observed | Show schedule/store state last read from the system | Perform the narrow callback action |
| callback received | Show event time and result | Write an idempotent command record |
| stale | Show age and a refresh path | Do not invent a fresh state |
| revoked | Show selection invalid and clear next step | Stop using tokens |
| failed | Show actionable error | Return safe default or documented response |
| unknown | Preserve last known state and explain | Avoid destructive cleanup until reconciled |

App Group records should be minimal:

- schema version;
- command ID;
- named activity or feature;
- desired action;
- created and expires dates;
- result state;
- redacted error code.

Do not put raw app names, child activity, token values, or report details in a shared log by default.

## Liquid Glass composition

Use Liquid Glass where it supports task hierarchy:

- a glass review group for the selected scope and schedule;
- a glass control group for Edit, Apply, Disable, and Refresh;
- an app-owned status card showing last observation and freshness;
- a report toolbar with native filters and context choices.

Keep system content and enforcement visibly distinct:

- App-owned glass: editable proposal and reconciliation state.
- System-owned UI: authorization sheet, shield, system settings, and report extension lifecycle.
- Protected content: never treated as decorative background for a glass effect.

Support reduced transparency and motion. If a translucent status card hides the difference between “enabled” and “unknown,” remove the material before adding a stronger color.

Use [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass), [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles), and [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy) together. Privacy is a visual state and a product promise, not only a plist entry.

## Accessibility and age-appropriate language

For parent/guardian experiences:

- describe authority and scope without legalistic overload;
- use explicit labels for schedule, threshold, and effect;
- keep “disable” and “revoke” separate;
- explain what happens to a selection after revocation;
- avoid shame, fear, or diagnosis language;
- do not rely on app logos or color to identify a policy;
- provide a screen-reader summary of selected count, schedule, and current observed state;
- test the shield and report extension independently from the main app.

For personal focus experiences:

- let the person edit or disable the policy;
- show the local time zone;
- make a stale or failed enforcement state visible;
- distinguish a self-set focus routine from parental control;
- avoid claims that a schedule treats distraction, addiction, anxiety, or attention disorders.

Apple’s [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles) specifically frame agency, responsibility, familiarity, safety, privacy, and feedback as design considerations. Use those principles in copy and state transitions.

## AI review shell

An AI schedule suggestion should look like a proposal:

    “I can prepare a daily 9 PM–7 AM schedule for the selected scope.”
    Assumptions: local time, repeating daily, shield selected apps and domains
    Missing: user has not approved the schedule
    Actions: Edit, Preview effect, Approve

Do not show an AI-generated “Focus score” as if Device Activity produced it. Keep raw report values, the generated explanation, and the approved policy in different sections.

The Apply button should be disabled when:

- authorization is not current;
- the selection is empty or revoked;
- the schedule is invalid;
- the requested effect is not supported by the selected target;
- the person has not reviewed the consequence.

## Preview and physical proof

Preview can prove the app-owned editor, summary, state labels, and accessibility identifiers. It cannot prove:

- Family Controls authorization;
- Family Sharing approval;
- opaque token revocation;
- Device Activity extension callbacks;
- system shield presentation;
- report-extension sandbox behavior;
- effective Managed Settings state;
- distribution entitlement approval.

Physical/system evidence should cover:

1. Individual and child/member authorization routes where permitted.
2. Token selection, storage, revocation, and re-selection.
3. Schedule start/end and threshold warnings.
4. Monitor extension invocation with the device in use and not in use.
5. Shield appearance and action on the selected device.
6. Report context/filter changes.
7. App and extension termination/relaunch.
8. Settings and authorization changes outside the app.
9. Large text, VoiceOver, reduced transparency, and high contrast.
10. Development and TestFlight/distribution entitlement state.

Use the [Family Controls and Device Activity proof matrix](../60-verification/22-family-controls-device-activity-proof-matrix.md) for the evidence record.

## Sources

- [Screen Time Technology Frameworks](https://developer.apple.com/documentation/screentimeapidocumentation/)
- [Family Controls](https://developer.apple.com/documentation/familycontrols)
- [AuthorizationCenter](https://developer.apple.com/documentation/FamilyControls/AuthorizationCenter)
- [FamilyActivityPicker](https://developer.apple.com/documentation/FamilyControls/FamilyActivityPicker)
- [FamilyActivitySelection](https://developer.apple.com/documentation/FamilyControls/FamilyActivitySelection)
- [Device Activity](https://developer.apple.com/documentation/deviceactivity)
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
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
