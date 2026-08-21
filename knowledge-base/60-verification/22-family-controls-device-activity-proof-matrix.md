# Family Controls and Device Activity proof matrix

This matrix records the evidence needed for privacy-sensitive Screen Time features. A green app-owned toggle, a successful authorization request, a monitor callback, a shield preview, and a distribution entitlement each prove a different boundary.

## Evidence levels

| Level | Can prove | Cannot prove by itself |
| --- | --- | --- |
| Source review | Intended framework boundary, privacy state, target plan, and fallback logic | Entitlement approval, extension invocation, system policy effect, or App Store readiness |
| Compile | Imports, target membership, API availability for the selected SDK, and type checking | Family Sharing authority, token privacy, scheduled callback, shield, report data, or physical behavior |
| Preview/UI test | Main-app states, picker entry, policy summary, report fixtures, accessibility identifiers | System authorization, opaque token behavior, extension process, effective Managed Settings, or distribution |
| Simulator | Some layout and app lifecycle behavior | Real Family Controls approval, child/individual identity, Device Activity callback, shield enforcement, report sandbox, or entitlement distribution |
| Signed device | Capability, permission, extension, system surface, and selected hardware behavior | All member types, all devices, distribution review, every OS, or long-term callback reliability |
| TestFlight/App Store | Distribution configuration for the observed artifact | Universal entitlement support, every family/account configuration, or system policy guarantees |

## Entitlement and target matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Family Controls capability in main app | Inspect project, built entitlements, and signed app | Wrong target, missing capability, stale profile | The app is configured to request the route |
| Capability in monitor extension | Inspect extension target and signed entitlements | Extension lacks entitlement or principal class | The monitor extension is provisioned |
| Capability in report extension | Inspect extension target and signed entitlements | Report target mismatch or missing extension point | The report extension is provisioned |
| Capability in shield extensions | Inspect configuration/action targets | Wrong extension point, missing profile, slow response | The shield extensions are provisioned |
| Development entitlement | Physical development run with approved development capability | Access denied, profile mismatch, expired signing | Development path works on this account/device |
| Distribution entitlement request | Apple Developer account record and archive validation | Pending/rejected request, extension omitted | Distribution authorization status is recorded, not assumed |
| App Group bridge | Signed multi-target run and schema fixture | Race, missing group, raw data leakage | Minimal cross-process command protocol works |

## Authorization and selection matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| AuthorizationCenter availability | Compile and physical status observation | Unsupported environment, restricted account | Current target can query status |
| Individual authorization | Physical device with biometric/system flow | Cancel, deny, settings revocation | Individual route observed on this device |
| Child/guardian authorization | Supported Family Sharing test configuration | Parent deny, different group, child account change | Guardian route observed for the tested family configuration |
| Status changes | Revoke or change Settings, relaunch/foreground app | Cached authorized state, revoked tokens | App detects and handles external change |
| FamilyActivityPicker presentation | Signed physical device picker flow | Not authorized, cancel, empty selection | System picker opened and returned selection |
| Opaque selection persistence | Local round-trip fixture with redacted values | Serialization failure, token expiry | App can persist its reviewed selection without exposing identity |
| Token revocation | Revoke authorization, reuse old selection | Stale selection accepted by local UI | App invalidates and requests re-selection |
| Scope summary | Physical picker plus supported labels/counts | Invented identity, mismatched category count | Displayed summary is supported and privacy-preserving |

## Device Activity matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Schedule validation | Unit tests for DateComponents, repeat, warning, time zone | Overnight interval, DST, invalid components | Local policy is structurally valid |
| Event validation | Unit tests for tokens, names, threshold units | Empty tokens, duplicate names, invalid threshold | Event request is structurally valid |
| startMonitoring | Signed device call with error/state log | Limit, conflict, revoked token, malformed schedule | Request result for tested configuration |
| Current activity reconciliation | Read activities/schedule after submit and foreground | External removal, stale local row, process termination | Local state reflects observed system state |
| stopMonitoring | Physical device disable flow | Duplicate stop, unknown name, app termination | Named monitor was removed or failure recorded |
| Interval warning | Physical device with time-boxed fixture | No device use, warning delay, process termination | Warning callback occurred on tested configuration |
| intervalDidStart | Monitor extension log and Managed Settings result | Extension not invoked, wrong name, duplicate callback | Interval callback path for the tested schedule |
| eventWillReachThresholdWarning | Threshold fixture and extension log | Warning missing, time boundary, duplicate | Warning path observed, not precise telemetry |
| eventDidReachThreshold | Threshold fixture and system effect | Threshold not reached, stale token, wrong event name | Event callback and action for the tested scope |
| intervalWillEndWarning | Short interval physical run | App/device inactive, callback delay | End-warning behavior observed |
| intervalDidEnd | Physical device and settings clear/reconciliation | Clear failure, extension termination, duplicate end | End callback path and cleanup for this policy |
| Extension cold start | Force-quit main app, wait for callback | No main app, shared-container race, extension launch failure | Monitor extension can execute its narrow route |
| Extension resource behavior | Release-style run with CPU/logging record | Excess work, timeout, memory pressure | Resource profile for the tested callback |

## Managed Settings and shield matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| ManagedSettingsStore creation | Signed target run | Wrong store name, unsupported target | Store can be created on this configuration |
| Apply application tokens | Physical device with selected app and re-read | Empty tokens, revoked tokens, other settings | App submitted the requested setting |
| Apply category policy | Physical device with category selection | Category mismatch, multiple policies | Category setting was observed for this test |
| Apply web-domain tokens | Physical device with supported domain | Domain limit, expired token, Safari route difference | Domain shield request on selected device |
| Named store isolation | Two policy fixtures and clear test | Store collision, unintended clear | App-owned stores remain isolated for this build |
| Clear settings | Disable action and physical observation | Other source setting, partial clear, app termination | App removed its configuration; effective state may differ |
| Effective state | Current API inspection where supported plus physical observation | Other apps/controls, system policy precedence | Effective behavior observed, not solely inferred from write |
| Shield appearance | Shield Configuration extension on physical device | Extension timeout, default fallback, large text, high contrast | Shield appearance for tested app/domain/category |
| Shield privacy | Review token and copy path | Readable identity leak, sensitive subtitle, network attempt | Tested shield does not expose unapproved identity |
| Shield action | Tap primary/secondary action on physical device | Token opaque, duplicate tap, response timeout | Extension response for this action and target |
| Action request workflow | App Group command plus later foreground reconciliation | Expired request, stale policy, authorization revoked | Request was recorded and reconciled, not necessarily granted |

## Report and privacy matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| DeviceActivityReport host | Signed app with context/filter | No authorization, empty filter, unavailable report | Host can request a report on this configuration |
| Report extension scene | Extension target and context fixture | Wrong context, scene not registered, extension failure | Scene renders for tested context |
| DeviceActivityFilter | Physical or official fixture with segment/device/scope options | Wrong member/device, invalid date range | Filter is encoded as intended |
| Report privacy sandbox | Extension run and network/log audit | Network dependency, shared-container leakage, raw export | Report stays within tested privacy boundary |
| Report empty/partial state | Fixture with no data, limited range, revoked selection | Graph implies zero, missing label | Report communicates availability honestly |
| Report accessibility | VoiceOver, Dynamic Type, high contrast, exact-value route | Chart only, color-only categories, clipped labels | Tested report tasks are accessible |
| Report-to-AI summary | Explicit user export, minimized input, output review | Raw activity sent, diagnosis language, invented values | Generated text is a bounded summary of selected data |

## Design and system matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Authorization copy | Physical system sheet and preflight review | Misleading request, unexplained member type | Copy explains the tested route |
| Policy summary | UI test for scope/time/effect/reset | Hidden time zone, no disable path, stale status | App-owned summary is understandable |
| Liquid Glass fallback | Reduce transparency/motion and high contrast | Critical state hidden by blur, moving controls | Tested app surface remains usable |
| System shield hierarchy | Physical shield with large text and VoiceOver | Decorative surface, unreadable button, missing reason | Shield is usable on selected device |
| Locked/shared device privacy | Lock Screen and shared-device review | Sensitive title/value exposed | Tested system surface follows policy |
| Reconciliation UI | External Settings/system change followed by foreground | Local success badge remains after removal | UI distinguishes requested, observed, stale, and failed |

## AI and safety matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Model availability | Device/OS/model fixture | No model, asset unavailable, cancellation | Fallback works; no quality guarantee |
| Schedule proposal | Typed proposal tests and invalid fixtures | Bad DateComponents, hidden time zone, unsupported effect | Proposal is structurally valid after deterministic checks |
| Scope boundary | Review UI with opaque selection reference | Model selects hidden app identity, token in prompt | Model cannot bypass picker or inspect token contents |
| Human approval | UI test and physical approval | Apply before review, changed proposal, revoked auth | Side effect follows explicit review |
| Side-effect isolation | Code review and command tests | Model invokes shield directly, replay, stale command | Only authorized deterministic code changes policy |
| Report summary | Minimized selected values and provenance | Diagnosis, shaming, invented exact values | Summary is labeled and bounded |

## Required evidence packet

- Project, target, extension, bundle identifiers, SDK, deployment target.
- Capability, entitlements, provisioning profile, and distribution request status.
- Authorization member type, date, result, and revocation/recovery evidence.
- Picker selection version with tokens redacted.
- Schedule/event definitions, time zone, submit result, and reconciliation snapshot.
- Extension callback logs with sensitive data redacted.
- Managed Settings desired/observed/effective state.
- Shield screenshots or recording, action sequence, and accessibility settings.
- Report context/filter, empty/partial fixtures, and report-extension evidence.
- AI model availability, input scope, proposal version, review action, and output.
- Device model, OS, account/family test configuration, battery/resource notes.
- Known limitations and untested system surfaces.

## Related routes

- [Family Controls, Device Activity, and Managed Settings](../43-system-framework-deep-dives/07-family-controls-device-activity-managed-settings.md)
- [Family Controls and privacy-sensitive system surfaces](../21-design-deep-dives/25-family-controls-and-privacy-surfaces.md)
- [Family Controls and Device Activity capability route](../50-capability-recipes/28-family-controls-device-activity-route.md)
- [Permission/entitlement/privacy checklist](04-permission-entitlement-and-privacy-checklist.md)
- [System surface checklist](05-system-surface-checklist.md)

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
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
