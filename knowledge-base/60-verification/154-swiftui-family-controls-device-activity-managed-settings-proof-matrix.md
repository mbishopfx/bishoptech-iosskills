# SwiftUI Family Controls, Device Activity, and Managed Settings proof matrix

Use this matrix to separate a Screen Time claim from the evidence that actually supports it. A signed app, an authorization Boolean, a token count, a monitor object, a local report fixture, or a model response is not by itself proof of system behavior.

Related pages:

- [Screen Time framework review](../42-framework-deep-dives/129-swiftui-family-controls-device-activity-managed-settings-review.md)
- [Screen Time design review](../21-design-deep-dives/157-swiftui-family-controls-device-activity-managed-settings-review-design.md)
- [Screen Time route worksheet](../50-capability-recipes/160-swiftui-family-controls-device-activity-managed-settings-review-route.md)
- [Screen Time code recipes](../70-code-recipes/172-swiftui-family-controls-device-activity-managed-settings-review-recipes.md)

## Evidence ladder

| Level | What it proves | What it does not prove |
| --- | --- | --- |
| Source review | The implementation plan uses documented Family Controls, Device Activity, Managed Settings, SwiftUI, and release APIs. | That the target has the capability, the system authorizes it, or a physical device applies policy. |
| Target configuration | The app and extension targets declare the intended capability, extension point, deployment target, and signing inputs. | That distribution approval exists or that system callbacks/report data work. |
| Signed artifact | The archive contains the expected entitlements and embedded extensions. | That TestFlight/App Store provisioning or the live system flow accepts the artifact. |
| Authorization proof | A person or parent/guardian completed the documented system authorization flow. | That a token is decoded, a schedule is running, or a shield is effective. |
| Route proof | Picker, schedule, event, settings, report, shield, and action paths produce the expected system callbacks/effects. | That every device family, account relationship, or release channel behaves the same. |
| Physical-device proof | A named iPhone/iPad/account relationship shows the intended system behavior. | That the archive is releasable without signing and distribution evidence. |
| TestFlight/release proof | The distributed build preserves capability, extension, privacy, and user-facing behavior. | That a Debug or local development build was sufficient. |

## Matrix

| Claim | Positive evidence | Negative/edge evidence | Owner |
| --- | --- | --- | --- |
| Family Controls capability is configured | Inspect the app target’s signed entitlement and Xcode capability. | Missing capability, stale profile, or development-only entitlement. | App/release |
| Screen Time extensions are configured | Inspect each embedded extension’s bundle ID, extension point, entitlement, and signed archive. | Extension omitted, wrong point, mismatched profile, or wrong deployment target. | App/release |
| Distribution permission exists | Capture the Account Holder’s Family Controls distribution request/assigned state and provisioning result. | TestFlight upload rejection or archive without distribution support. | Release |
| Individual authorization works | On a physical device, complete the owner authentication flow and record resulting status. | Cancel, deny, revoke in Settings, or unsupported target. | App QA |
| Child authorization works | Use a parent/guardian and child device in the same Family Sharing test setup; record approval and status. | Wrong family relationship, child denial, account transition, or parent revocation. | App QA |
| Authorization state is observed | Change status outside the app and show the UI rehydrates to a revoked/changed state. | UI still exposes Apply or Report as if the first authorization were permanent. | App |
| Picker uses the system route | Physical capture of the `FamilyActivityPicker` sheet and the resulting binding update. | Custom installed-app catalog or bypassed system picker. | App |
| Selection remains opaque | Logs/network/model traces show no decoded app/site identity or token serialization. | Tokens in analytics, crash payloads, remote logs, or prompts. | Privacy |
| Revoked selection is handled | Revoke authorization, exercise persisted selection, and show token invalidation/re-selection behavior. | Stale tokens silently reapply policy or appear as stable identifiers. | App |
| Empty selection is safe | Save/apply with no selected apps/categories/sites and show the deliberate empty state. | Empty selection unexpectedly means all activity. | App |
| Schedule is registered | Capture `DeviceActivityCenter.startMonitoring` success with name, interval, warning, and policy revision. | Duplicate name silently replaces a prior schedule or wrong time zone. | App |
| Event threshold is registered | Capture event name, selected scope, duration, and past-activity policy. | Threshold lacks scope, includes unintended history, or is never stopped. | App |
| Monitor extension receives interval callbacks | Physical device enters/exits a named interval while in use; capture callback and policy revision. | Main app is terminated, device is idle, or callback is assumed from a foreground preview. | Extension |
| Monitor extension receives threshold callbacks | Physical device reaches a short test threshold and callback applies a deterministic consequence. | Network/model dependency, non-idempotent duplicate callback, or callback without system effect. | Extension |
| Managed Settings request is recorded | Capture named store, setting mutation, policy revision, and return/error handling. | A local Boolean says “blocked” without a setting mutation. | App/extension |
| Managed Settings effect is visible | Open a selected real app/site on the authorized device and observe the system shield. | Simulator-only, wrong selection, or a shield caused by another policy. | Device QA |
| Effective policy is distinguished | UI shows requested, app-owned, effective, unknown, and cleared states separately where supported. | App claims all system restrictions are removed or active from one store write. | App |
| Clearing is scoped | Clear the app’s named/default store and verify only its policy contribution is removed. | “Clear all” is presented as a universal system reset. | App |
| Report is configured | Host presents a documented context/filter and the report extension renders the matching view. | Host only shows a placeholder chart or a local fixture. | App/extension |
| Report privacy boundary holds | Extension test shows no network request and no sensitive report content leaves its sandbox. | Report data copied to server, general analytics, or an unrestricted model context. | Privacy |
| Report filter is correct | Physical activity fixture and filter show expected segment, user/device, and selected scope. | Wrong date interval, timezone, user/device, token revocation, or empty data is misrepresented. | Extension |
| Report async lifecycle is safe | Loading, cancellation, empty result, error, and extension relaunch are captured. | Async results are assumed to be a durable database or foreground-only stream. | Extension |
| Shield configuration is fast | Physical shield displays custom fields; timeout/default fallback is also exercised. | Network/model/database delay causes blank or late custom shield. | Extension |
| Shield copy is private and accessible | Shield text does not identify an opaque app/site; VoiceOver, Dynamic Type, contrast, and buttons work. | Icon/color carries the only meaning or copy reveals private identity. | Design/QA |
| Shield action receives no identity | Action logs show token type only; button behavior is mapped to policy intent. | Delegate assumes token reveals app/site name or opens content without approval. | Extension |
| Shield response is intentional | Each button produces documented `.none`, `.defer`, `.close`, or `.openParentalControlsApp` result. | Completion handler omitted, wrong response, or a bypass hidden behind “continue.” | Extension |
| SwiftUI state survives system sheets | Focus, authorization, picker, report, and revocation return to the right state. | Stale Apply button, duplicate sheet, or selection lost after sheet dismissal. | App |
| Liquid Glass is limited | App-owned controls look coherent with glass enabled/disabled and accessibility settings. | Custom glass covers system picker/authorization/shield or destroys contrast. | Design |
| AI proposal is bounded | Proposal contains only allowed app-owned fields, is typed/validated, and requires explicit review. | Raw tokens/report values in prompt, automatic restriction, or unsupported-device dead end. | AI/app |
| AI cancellation and freshness work | Leaving screen, changing selection, revoking auth, or tapping Cancel invalidates/stops proposal. | Stale proposal applies to a new selection or outlives authorization. | AI/app |
| Accessibility route works | VoiceOver, Dynamic Type, Increase Contrast, Reduce Transparency, Reduce Motion, keyboard, and Switch Control pass task tests. | Visual-only state, unreachable Apply/Clear, focus lost after revocation. | Design/QA |
| Physical release behavior works | Archive -> TestFlight install -> authorization -> picker -> schedule/shield/report retest. | Debug-only behavior or simulator result presented as release proof. | Release |

## Fixture plan

Use a named fixture per boundary:

```text
SC-01 entitlement: signed app + four extension targets
SC-02 individual: owner authorization and revocation
SC-03 child: parent/guardian approval on a Family Sharing test setup
SC-04 selection: one app, one category, one web domain, then empty selection
SC-05 schedule: short interval, warning time, duplicate-name replacement
SC-06 threshold: short event, includesPastActivity true/false
SC-07 monitor: interval and threshold callbacks with app terminated
SC-08 settings: shield, clear named store, effective-state mismatch
SC-09 report: daily/hourly filter, empty data, extension relaunch
SC-10 shield: app/site/category configuration, timeout fallback, each button
SC-11 privacy: token/log/network/model trace review
SC-12 accessibility: VoiceOver, Dynamic Type, contrast, Reduce Transparency
SC-13 AI: available/unavailable, stale proposal, cancellation, deterministic fallback
SC-14 release: archive entitlements, TestFlight capability, physical retest
```

For each fixture record device model, iOS build, account relationship, Family Sharing membership, target build, authorization state, selected scope description without token identity, local time zone, and the artifact path. Do not record the selected application or website name in a shared test log unless the user-facing system surface itself is the authorized evidence and the data is handled under the project’s privacy rules.

## Release stop conditions

Stop before release if any of these remain unresolved:

- Family Controls distribution permission is missing or not embedded in the signed archive.
- A Screen Time extension is absent, unsigned, or provisioned differently from the app.
- The app assumes authorization or tokens are permanent.
- The monitor, report, or shield extension depends on a network or long-lived foreground process.
- Requested Managed Settings are presented as effective system state without physical evidence.
- Report data or opaque tokens leave their documented privacy boundary.
- Shield copy is not accessible or reveals private identity.
- AI can apply a policy without explicit review or uses stale authorization/selection.
- TestFlight has not exercised authorization, selection, extension callbacks, shield, report, and clearing.

## Sources

- [Family Controls](https://developer.apple.com/documentation/familycontrols)
- [AuthorizationCenter](https://developer.apple.com/documentation/familycontrols/authorizationcenter)
- [AuthorizationStatus](https://developer.apple.com/documentation/familycontrols/authorizationstatus)
- [FamilyActivityPicker](https://developer.apple.com/documentation/familycontrols/familyactivitypicker)
- [FamilyActivitySelection](https://developer.apple.com/documentation/familycontrols/familyactivityselection)
- [FamilyControlsMember](https://developer.apple.com/documentation/familycontrols/familycontrolsmember)
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
- [DeviceActivityReportScene](https://developer.apple.com/documentation/deviceactivity/deviceactivityreportscene)
- [DeviceActivityFilter](https://developer.apple.com/documentation/deviceactivity/deviceactivityfilter)
- [DeviceActivityData](https://developer.apple.com/documentation/deviceactivity/deviceactivitydata)
- [DeviceActivityResults](https://developer.apple.com/documentation/deviceactivity/deviceactivityresults)
- [Managed Settings](https://developer.apple.com/documentation/managedsettings)
- [Manage settings on devices in a Family Sharing group](https://developer.apple.com/documentation/managedsettings/connectionwithframeworks)
- [ManagedSettingsStore](https://developer.apple.com/documentation/managedsettings/managedsettingsstore)
- [ShieldAction](https://developer.apple.com/documentation/managedsettings/shieldaction)
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
