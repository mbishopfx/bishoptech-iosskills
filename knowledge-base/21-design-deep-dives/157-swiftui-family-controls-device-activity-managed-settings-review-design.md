# SwiftUI Family Controls, Device Activity, and Managed Settings design review

This design lane is for a native Screen Time experience: a person or parent chooses apps, categories, or websites, defines a schedule or threshold, and sees the system apply a policy or report activity through Apple’s privacy-preserving APIs.

The visual goal is calm, clear, and system-aligned. The app can use Liquid Glass for its own hierarchy, but it should not imitate the system authorization sheet, rebuild the Family Activity Picker, or treat a custom shield as a marketing billboard. Family Controls and its extensions are trust surfaces first.

## The core screen hierarchy

Use one primary task per screen. A good root flow is:

```text
NavigationStack
  -> status and relationship
  -> selection
  -> schedule or threshold
  -> requested/effective policy
  -> report
  -> advanced recovery and release diagnostics
```

### 1. Outcome header

Start with the person’s goal, not the framework name:

- “Quiet hours”
- “Study window”
- “Family app limits”
- “See this week’s activity”

Place a short explanation below the title. For a child-device route, say that a parent or guardian authorizes the control. For an individual route, say that the device owner authenticates. Do not call both “parental control” if the product supports individual self-management.

### 2. Authorization status

The first card should show a semantic status, not a raw enum:

| Status | Copy and action |
| --- | --- |
| Needs authorization | “Apple needs your approval before this app can manage Screen Time.” Button: “Continue”. |
| Waiting | “Finish the approval sheet from Apple.” Disable duplicate actions. |
| Authorized for this device | “You can choose what this device manages.” |
| Authorized for a child | “A parent or guardian manages the selected child device.” |
| Revoked | “Authorization changed outside this app.” Button: “Review authorization”. |
| Distribution/device unavailable | “This capability is not available for this build or device.” Link to support/debug detail only in a developer surface. |

Use a status icon plus text and an accessible value. Do not use green alone to imply that settings are effective; authorization and effective policy are different facts.

## Selection is a system sheet, not a custom catalog

Present `FamilyActivityPicker` as the source of truth. The app-owned screen can provide:

- a purpose statement above the picker action;
- a count or broad selection summary without revealing token identity;
- an explanation of whether the selection targets this device or a child device;
- a “Change selection” button; and
- an empty-state card when no applications, categories, or web domains are selected.

Avoid showing a fake list of app icons, guessed names, or a server-loaded app catalog. Opaque tokens should stay opaque. If the user needs to understand scope, use labels such as “Selected apps,” “Selected categories,” and “Selected websites,” not a fabricated identity list.

The picker can be presented as a sheet with a normal SwiftUI control, which is a strong place for platform consistency. Avoid putting a large custom glass overlay above it; the system picker owns its presentation and accessibility behavior.

## Schedule and threshold editor

The schedule editor should read like a calendar task, not a technical form:

```text
Study window
Every day
10:00 PM – 7:00 AM
Warn me 5 minutes before it starts

Selected scope
3 categories · 0 apps · 0 websites

[Review policy] [Save schedule]
```

Use native `DatePicker`, `Toggle`, `Picker`, and `Form` controls where they express the task. Keep the warning time and threshold visible but subordinate. A user should be able to answer:

- When does the policy begin and end?
- Does it repeat?
- What happens near the threshold?
- What was selected?
- Who authorized this device?

Show a warning when the same `DeviceActivityName` will replace an existing schedule. Treat replacement as a deliberate edit, not an invisible side effect of tapping Save.

## Requested versus effective policy

Managed Settings can receive app configuration while the system determines the effective device state. Make that distinction visible:

| App-owned state | User-facing language |
| --- | --- |
| Request assembled | “Ready to apply.” |
| Settings request submitted | “Apple is applying this policy.” |
| Active app-owned store | “This app has a restriction configured.” |
| Effective state observed | “The device reports this restriction as active.” |
| Unknown or conflicted | “The system may have another policy in effect.” |
| Cleared by this app | “This app’s policy was cleared.” |

Do not promise “all apps are blocked” because a local Boolean is true. If a policy depends on another app, a child device, or a system-managed effective value, say so.

## Report design

Keep report context and filter controls separate from the report itself:

1. a time segment control such as day, week, or month;
2. a user/device scope control where supported;
3. an activity scope summary;
4. a loading/authorization/unavailable state; and
5. the `DeviceActivityReport` surface.

The host app should not expose raw report objects as generic debug data. The report extension owns the sensitive report view. If a report is unavailable because authorization changed, show a clear recovery state rather than a blank chart.

Useful empty and failure states include:

- “Authorize this device to view activity.”
- “No activity matched this filter.”
- “The selected scope is no longer authorized.”
- “This report is handled by a system extension and is temporarily unavailable.”
- “Report data stays on this device and is not uploaded.”

For charts or summaries, retain the native accessibility path: labels, units, time period, maximum/minimum context, and a concise text summary. Do not make a colorful chart the only way to understand the report.

## Custom shield design

The shield is a moment of interruption. It should be immediate, readable, and emotionally neutral. Use the `ShieldConfiguration` fields intentionally:

| Field | Design guidance |
| --- | --- |
| Icon | A simple system-recognizable symbol or supplied app icon with a meaningful accessibility description. |
| Title | State the policy (“Study time is active”), not a moral judgment. |
| Subtitle | Explain when it ends or what approved next step exists. |
| Primary button | One unambiguous authorized action. |
| Secondary button | Optional, with a small number of predictable submenu items. |
| Background | Use a restrained color/blur that preserves contrast and readability. |

The system provides defaults when properties are `nil` and when the extension is too slow. Test both custom and fallback states. Do not make the shield dependent on a model call, network request, remote image, or a database lookup.

Shield actions receive opaque tokens, not the identity of the shielded app or site. The action UI should therefore use generic policy language and send the user to the parental-controls app for any identity-sensitive or approval-sensitive decision.

## Liquid Glass rules for this lane

Liquid Glass belongs around controls that belong to the app:

- the schedule editor’s toolbar actions;
- the selection summary card;
- a compact policy status capsule;
- report context/filter controls; and
- a review-and-apply action group.

Use one `GlassEffectContainer` or one visually coherent glass group per control cluster. Keep the content behind the glass legible and avoid stacking translucent panels until contrast and Reduce Transparency are tested.

Do not add custom glass to:

- Apple’s authorization sheet;
- the system Family Activity Picker;
- the system device-activity report extension surface unless the extension’s own view owns that treatment;
- the shield’s system presentation beyond the documented configuration fields; or
- an accessibility fallback that needs a solid, high-contrast surface.

For iOS 26 target work, prefer semantic SwiftUI controls and documented Liquid Glass APIs. The design should still look coherent if glass effects are reduced or removed.

## AI review surface

If the product uses Foundation Models to propose a schedule explanation or a policy draft, put the proposal in a review card with explicit provenance:

```text
Suggested by your stated goal
Every weekday · 9:00 PM – 7:00 AM
Scope: the categories you selected

Why this suggestion
A short, deterministic explanation from the model

[Edit] [Apply] [Discard]
```

Rules:

- do not display or expose opaque tokens;
- disclose that the suggestion is generated and may be wrong;
- show the exact values that will be applied;
- make Edit and Discard as available as Apply;
- invalidate the proposal when authorization, selection, or policy revision changes;
- stop generation when the user leaves the screen or taps Cancel; and
- keep a deterministic editor for unsupported devices or model unavailability.

AI should not produce a shield action response, override a parent/guardian decision, infer a child’s identity from activity, or turn a report into a remote behavioral profile.

## Accessibility and alternate input

The route needs accessible semantics at every handoff:

- VoiceOver announces the current authorization relationship and whether the next action opens an Apple sheet;
- the picker button has a purpose and selection-scope label;
- schedule controls expose start/end, repeat, warning, and threshold values;
- policy state uses a text label in addition to icons/color;
- report filters expose date segment, user/device scope, and activity scope;
- shield title/subtitle/buttons remain understandable without the icon; and
- keyboard, Switch Control, Dynamic Type, Increase Contrast, Reduce Transparency, and Reduce Motion are exercised.

Keep focus predictable after a system sheet returns. If authorization is revoked, move focus to the status explanation and recovery action instead of leaving focus on a now-invalid “Apply” button.

## Privacy copy that earns trust

Use three short layers of copy:

1. **Before authorization:** why access is required and who controls it.
2. **Before selection:** what the app receives (opaque handles) and what it does not receive (decoded identities or uploaded browsing history).
3. **Before applying:** which device behavior may change, which app-owned store will be used, and how to clear it.

Do not hide the fact that Device Activity and Managed Settings use extensions and system behavior outside the foreground app. Explain that reports stay within Apple’s documented privacy boundary and that effective settings may be determined by the system and other policies.

## Review checklist

- [ ] The first screen names the user outcome and authorization relationship.
- [ ] The system Family Activity Picker is the only selection source.
- [ ] Opaque tokens never appear in logs, analytics, network payloads, or model prompts.
- [ ] Schedule replacement using a duplicate name is explicit.
- [ ] Requested policy and effective policy have different labels.
- [ ] Report loading, empty, revoked, and sandbox/unavailable states are designed.
- [ ] Shield configuration is fast, calm, readable, and tested with defaults.
- [ ] Shield actions do not reveal the shielded identity or bypass approval.
- [ ] Liquid Glass is limited to app-owned controls and survives accessibility settings.
- [ ] AI proposals show exact values, provenance, review, cancellation, and fallback.
- [ ] Physical-device proof covers individual and parent/child authorization as applicable.
- [ ] Archive/TestFlight proof includes every Screen Time extension entitlement.

## Sources

- [Family Controls](https://developer.apple.com/documentation/familycontrols)
- [AuthorizationCenter](https://developer.apple.com/documentation/familycontrols/authorizationcenter)
- [FamilyActivityPicker](https://developer.apple.com/documentation/familycontrols/familyactivitypicker)
- [FamilyActivitySelection](https://developer.apple.com/documentation/familycontrols/familyactivityselection)
- [Configuring Family Controls](https://developer.apple.com/documentation/xcode/configuring-family-controls)
- [Requesting the Family Controls entitlement](https://developer.apple.com/documentation/familycontrols/requesting-the-family-controls-entitlement)
- [Device Activity](https://developer.apple.com/documentation/deviceactivity)
- [DeviceActivityReport](https://developer.apple.com/documentation/deviceactivity/deviceactivityreport)
- [DeviceActivityFilter](https://developer.apple.com/documentation/deviceactivity/deviceactivityfilter)
- [DeviceActivityMonitor](https://developer.apple.com/documentation/deviceactivity/deviceactivitymonitor)
- [Managed Settings](https://developer.apple.com/documentation/managedsettings)
- [ManagedSettingsStore](https://developer.apple.com/documentation/managedsettings/managedsettingsstore)
- [ShieldActionDelegate](https://developer.apple.com/documentation/managedsettings/shieldactiondelegate)
- [ShieldActionResponse](https://developer.apple.com/documentation/managedsettings/shieldactionresponse)
- [Managed Settings UI](https://developer.apple.com/documentation/managedsettingsui)
- [ShieldConfiguration](https://developer.apple.com/documentation/managedsettingsui/shieldconfiguration)
- [ShieldConfigurationDataSource](https://developer.apple.com/documentation/managedsettingsui/shieldconfigurationdatasource)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
