# SwiftUI Family Controls, Device Activity, and Managed Settings route worksheet

Use this worksheet before implementing a Screen Time feature. It is designed to make authorization, opaque selections, extension targets, system settings, privacy, and release evidence explicit.

Related references:

- [Screen Time framework review](../42-framework-deep-dives/129-swiftui-family-controls-device-activity-managed-settings-review.md)
- [Screen Time native design review](../21-design-deep-dives/157-swiftui-family-controls-device-activity-managed-settings-review-design.md)
- [Screen Time proof matrix](../60-verification/154-swiftui-family-controls-device-activity-managed-settings-proof-matrix.md)
- [Screen Time code recipes](../70-code-recipes/172-swiftui-family-controls-device-activity-managed-settings-review-recipes.md)

## Route record

| Field | Decision |
| --- | --- |
| Product outcome | `TBD` |
| Target / deployment | `TBD / iOS 26` |
| Member relationship | `individual` / `child` / `TBD` |
| Family Controls capability | app target + extension targets: `TBD` |
| Distribution entitlement request | status / date / owner: `TBD` |
| Authorization owner | `AuthorizationCenter.shared`: `TBD` |
| Authorization status model | `TBD` |
| Picker presentation | inline / sheet / modifier: `TBD` |
| Selection scope | applications / categories / web domains: `TBD` |
| Token persistence | minimum local state / revocation policy: `TBD` |
| Activity name | stable `DeviceActivityName`: `TBD` |
| Schedule | interval / repeats / warning time / time zone: `TBD` |
| Event names | threshold and `includesPastActivity`: `TBD` |
| Monitor extension | bundle ID / principal class / target: `TBD` |
| Managed Settings store | default or named store / owner: `TBD` |
| Effective policy readback | supported values / unknown state: `TBD` |
| Report extension | bundle ID / context / filter: `TBD` |
| Report privacy boundary | sandbox and no-network behavior: `TBD` |
| Shield configuration | app/site/category overloads / fallback: `TBD` |
| Shield actions | button map / response / parental-controls handoff: `TBD` |
| SwiftUI state | authorization / selection / schedule / policy / report: `TBD` |
| Liquid Glass surface | app-owned control clusters only: `TBD` |
| AI proposal | input fields / output schema / review: `TBD` |
| Accessibility | VoiceOver / Dynamic Type / contrast / alternate input: `TBD` |
| Physical device | individual / parent-child / shield / report: `TBD` |
| Release artifact | archive / TestFlight / App Store: `TBD` |

## Step 1: capability and target map

- [ ] Add Family Controls to the main app target.
- [ ] Add the capability to every Screen Time extension that needs it.
- [ ] Record the entitlement key in the signed artifact, not only in the source project.
- [ ] Confirm the target uses the iOS 26 SDK and intended deployment target.
- [ ] Request Family Controls distribution permission before TestFlight/App Store submission.
- [ ] Confirm app and extension provisioning profiles carry the needed managed capability.
- [ ] Confirm the extension point for each target: Device Activity Monitor, Device Activity Report, Shield Action, or Shield Configuration.
- [ ] Keep extension code independent of foreground-only app memory and network services.

## Step 2: authorization route

Record the person and system interaction:

1. Explain why authorization is needed and whose device is being managed.
2. Call the documented `AuthorizationCenter` request method for `.individual` or `.child`.
3. Capture success, denial, cancellation, and thrown errors as separate states.
4. Observe authorization-status changes after Settings, Family Sharing, account, or revocation changes.
5. Invalidate selections and stop applying new policy when the authorization no longer permits the route.

Do not make a local Boolean called `isAuthorized` the source of truth. Persist a last-known state for UI continuity, then re-read the system state before applying settings or presenting a report.

## Step 3: selection and token route

- [ ] Present `FamilyActivityPicker` using a `FamilyActivitySelection` binding.
- [ ] Show the person whether the picker is for this device or an authorized child device.
- [ ] Keep `applicationTokens`, `categoryTokens`, and `webDomainTokens` opaque.
- [ ] Do not log, upload, stringify for analytics, or send tokens to Foundation Models.
- [ ] Validate that an empty selection is handled intentionally.
- [ ] Store only the minimum local selection needed to reapply the user’s policy.
- [ ] Treat revocation as token invalidation and offer re-selection.
- [ ] If the app shows labels, use system-provided activity-label mechanisms or generic scope copy.

Selection record:

```text
selectionRevision: UUID
applicationTokenCount: Int
categoryTokenCount: Int
webDomainTokenCount: Int
scopeDescription: app-owned non-identifying text
authorizationRevision: String
createdAt: Date
```

The counts and revision are UI bookkeeping. They do not reveal or prove the selected identities.

## Step 4: schedule and event route

For each activity:

- [ ] Create a stable `DeviceActivityName` and document replacement behavior.
- [ ] Define interval start/end components and repeat policy.
- [ ] Define warning time, if the UX promises a warning.
- [ ] Define the event name and selected scope.
- [ ] Define threshold duration and whether past activity counts.
- [ ] Record the schedule time-zone assumption.
- [ ] Make `startMonitoring` and `stopMonitoring` idempotent.
- [ ] Persist the app-owned policy revision with the activity name.
- [ ] Test duplicate names, replacement, stop, relaunch, reboot, time-zone changes, and revocation.

An event threshold should map to a clear consequence. If the consequence is a shield, document which `ManagedSettingsStore` owns it and how it is cleared. If the consequence is a notification, do not imply that notification delivery proves the shield or report route.

## Step 5: monitor extension route

The monitor extension should be a small adapter:

```text
system callback
  -> validate activity/event name
  -> load app-owned policy revision
  -> apply deterministic local consequence
  -> record minimal outcome / signpost
  -> return promptly
```

- [ ] Subclass `DeviceActivityMonitor` as the principal class for the target.
- [ ] Implement only the callbacks the product needs.
- [ ] Call `super` where required by the documented lifecycle.
- [ ] Make interval and threshold handling idempotent.
- [ ] Avoid network, model calls, long disk work, and foreground SwiftUI assumptions.
- [ ] Apply a pre-approved Managed Settings policy locally.
- [ ] Keep sensitive tokens and policy data inside the permitted app/extension boundary.
- [ ] Capture extension logs without writing token identities.

The monitor being instantiated is not evidence that an interval callback happened. The callback and physical system effect are separate proof items.

## Step 6: Managed Settings route

Choose a store ownership policy:

| Policy | Use when |
| --- | --- |
| One default store | The product owns one coherent set of restrictions and can clear them together. |
| Named stores | Features or policy revisions need independent ownership and targeted cleanup. |
| Monitor-owned mutation | A schedule threshold must apply a pre-approved local shield while the app is not running. |
| App-owned mutation | The person explicitly taps Apply/Clear in the foreground. |

For each setting record:

- requested value;
- store name;
- policy revision;
- expected system effect;
- supported effective-state readback;
- clearing action; and
- physical-device verification fixture.

Treat `nil` as a deliberate clear for the app’s setting. Do not claim that a clear removes restrictions created by a different store, another app, a parent device, or the system.

## Step 7: report route

- [ ] Define report context names in the report extension.
- [ ] Define the host-side `DeviceActivityFilter` segment, users, devices, apps, categories, and websites.
- [ ] Keep filter changes cancellable and revisioned.
- [ ] Present a loading state before the report view is ready.
- [ ] Handle no authorization, no matching data, revoked tokens, and extension failure.
- [ ] Keep report computation and sensitive values in the report extension sandbox.
- [ ] Do not perform network requests or move raw report data outside the extension.
- [ ] Provide accessible text summaries for charts and visual trends.
- [ ] Test report delivery on an authorized physical device with real activity and a deterministic fixture filter.

The host view can own a picker for context and segment interval, but it does not own the sensitive report computation. Keep that distinction in the module boundary.

## Step 8: shield and action route

Shield configuration:

- [ ] Implement application, website, and category configuration overloads as needed.
- [ ] Return quickly and deterministically.
- [ ] Use default values for fields that do not need customization.
- [ ] Test timeout and `nil` fallback behavior.
- [ ] Avoid remote images, network, and model inference in the configuration path.

Shield actions:

- [ ] Map primary, secondary, and submenu actions to explicit product intent.
- [ ] Treat the supplied application/category/web-domain value as opaque.
- [ ] Return `.none`, `.defer`, `.close`, or `.openParentalControlsApp` intentionally.
- [ ] Do not open a shielded app merely because the user pressed a button unless the authorized policy allows it.
- [ ] Send approval-sensitive decisions to the parental-controls app.

## Step 9: SwiftUI and AI route

Main-actor app state should model separate revisions:

```text
authorizationRevision
selectionRevision
scheduleRevision
settingsRequestRevision
effectiveStateRevision
reportFilterRevision
aiProposalRevision
```

An AI proposal is valid only when all inputs are still current. Use a typed proposal with fields such as schedule name, start/end, warning lead time, and user-facing explanation. Exclude raw tokens and raw report data. Require the person to review the exact values before applying. On unavailable Foundation Models, show the manual editor without changing the Screen Time route.

Liquid Glass is appropriate for app-owned action clusters, not for the system picker, authorization sheet, report sandbox boundary, or system shield. Document accessibility behavior for each glass group.

## Step 10: evidence package

Collect these artifacts:

- [ ] signed app entitlements;
- [ ] signed extension entitlements and extension-point identifiers;
- [ ] Family Controls distribution request state;
- [ ] individual authorization recording or parent/child test evidence;
- [ ] selection revision and non-identifying counts;
- [ ] schedule/event registration log;
- [ ] monitor-extension callback evidence;
- [ ] Managed Settings requested/effective/cleared evidence;
- [ ] report extension delivery and sandbox behavior;
- [ ] shield configuration, timeout, and action-response evidence;
- [ ] VoiceOver/Dynamic Type/contrast/alternate-input checks;
- [ ] AI availability, stale-proposal, token-exclusion, cancellation, and fallback tests;
- [ ] physical-device screenshots/video of a protected app/site and report;
- [ ] archive inspection;
- [ ] TestFlight install and re-test; and
- [ ] release notes documenting capability and privacy behavior.

## Sources

- [Family Controls](https://developer.apple.com/documentation/familycontrols)
- [AuthorizationCenter](https://developer.apple.com/documentation/familycontrols/authorizationcenter)
- [FamilyActivityPicker](https://developer.apple.com/documentation/familycontrols/familyactivitypicker)
- [FamilyActivitySelection](https://developer.apple.com/documentation/familycontrols/familyactivityselection)
- [Requesting the Family Controls entitlement](https://developer.apple.com/documentation/familycontrols/requesting-the-family-controls-entitlement)
- [Configuring Family Controls](https://developer.apple.com/documentation/xcode/configuring-family-controls)
- [Family Controls entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.family-controls)
- [Device Activity](https://developer.apple.com/documentation/deviceactivity)
- [DeviceActivityCenter](https://developer.apple.com/documentation/deviceactivity/deviceactivitycenter)
- [DeviceActivitySchedule](https://developer.apple.com/documentation/deviceactivity/deviceactivityschedule)
- [DeviceActivityEvent](https://developer.apple.com/documentation/deviceactivity/deviceactivityevent)
- [DeviceActivityMonitor](https://developer.apple.com/documentation/deviceactivity/deviceactivitymonitor)
- [DeviceActivityReport](https://developer.apple.com/documentation/deviceactivity/deviceactivityreport)
- [DeviceActivityReportExtension](https://developer.apple.com/documentation/deviceactivity/deviceactivityreportextension)
- [DeviceActivityFilter](https://developer.apple.com/documentation/deviceactivity/deviceactivityfilter)
- [DeviceActivityResults](https://developer.apple.com/documentation/deviceactivity/deviceactivityresults)
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
