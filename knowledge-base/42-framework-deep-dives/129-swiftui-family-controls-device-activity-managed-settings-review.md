# SwiftUI Family Controls, Device Activity, and Managed Settings review

Screen Time APIs are a system-mediated parental-control and device-activity route, not a generic usage-analytics API. The app, its Screen Time extensions, the person or parent who authorizes the experience, and the system all hold different pieces of the contract. A good implementation keeps those boundaries visible in the product architecture:

```text
Family Controls capability and distribution approval
        -> AuthorizationCenter approval
        -> FamilyActivityPicker opaque selection
        -> DeviceActivity schedules/events OR ManagedSettings stores
        -> monitor/report/shield extensions
        -> SwiftUI status and review surfaces
```

This review covers the route for iOS 26-targeted projects. Recipes are compile-oriented sketches; final API availability, extension templates, entitlement state, and behavior still need to be checked in the named target and on a physical device.

## Choose the product lane first

| Product lane | Primary route | Evidence boundary |
| --- | --- | --- |
| Let a person choose apps, categories, or websites to manage | `FamilyActivityPicker` -> `FamilyActivitySelection` -> `ManagedSettingsStore` | The user confirmed a selection and the system accepted the settings; the app must not infer the real app/site names from opaque tokens. |
| Enforce a recurring schedule or threshold | `DeviceActivityCenter` -> `DeviceActivitySchedule` and `DeviceActivityEvent` -> `DeviceActivityMonitor` extension | The schedule and event are registered, and a physical-device callback changes the intended managed setting. |
| Show a usage report | `DeviceActivityReport` -> `DeviceActivityReportExtension` and `DeviceActivityFilter` | The system delivered a privacy-preserving report to the sandboxed extension; a local preview or fabricated report is not usage proof. |
| Customize a shield | `ManagedSettingsStore.shield` -> `ShieldConfigurationDataSource` | The system displayed the shield with the expected text, icon, color, and fallback behavior. |
| Respond to a shield button | `ShieldActionDelegate` -> `ShieldActionResponse` | The extension receives a token and returns an intentional response such as `none`, `defer`, `close`, or `openParentalControlsApp`. |
| Explain a schedule or suggest a change with on-device AI | App-owned policy/configuration -> Foundation Models proposal -> explicit review -> documented settings mutation | The model never receives raw opaque tokens or unreviewed sensitive report data and never bypasses authorization. |

Do not combine these lanes merely because they all mention “Screen Time.” A report extension, monitor extension, shield configuration extension, and shield action extension have different inputs, execution lifetimes, and privacy boundaries.

## Entitlement and distribution are part of the feature

Family Controls requires the Family Controls capability before the app calls `AuthorizationCenter` request or revoke APIs. Xcode adds the `com.apple.developer.family-controls` entitlement for the target. A Screen Time API extension needs the same capability and a matching signing/provisioning decision.

Development access and distribution access are separate gates. Before submitting an app that uses Family Controls, the Apple Developer Account Holder must request permission to use the distribution entitlement. The request applies to the app and to Screen Time API extensions included in the product. A successful local build, an entitlements file in source control, or an authorization sheet in development does not prove that TestFlight or App Store signing can use the capability.

Record the following as target artifacts:

- the app target’s Family Controls capability and entitlement;
- each Device Activity Monitor, Device Activity Report, Shield Action, and Shield Configuration extension target;
- bundle identifiers, deployment target, extension point, and signing identity;
- provisioning profiles and the distribution entitlement request status;
- a release archive inspection showing the final app and embedded extension entitlements.

Keep this route out of a generic “privacy permission” checklist. Family Controls is a managed capability with Apple review and distribution conditions, not an ordinary runtime prompt.

## Authorization has a person and a relationship

Use the shared `AuthorizationCenter` to request authorization. The system distinguishes an individually authorized device from a child account authorized by a parent or guardian. The UX should explain which relationship the feature needs before showing the system sheet.

For an individual, the system can ask the person to authenticate with Face ID or Touch ID. For a child, the parent or guardian in the Family Sharing group approves or cancels the request. Later authorization-status changes can come from outside the app, including Settings or an account relationship change, so the app must observe and re-evaluate status rather than treating the first success as permanent.

The authorization state machine should include:

| State | App behavior |
| --- | --- |
| Not requested | Explain the feature, relationship, data boundaries, and why the capability is needed; offer the system authorization action. |
| Request in flight | Disable duplicate actions and show that the system approval sheet is active. |
| Approved | Enable the picker, schedule, settings, and report routes that the target actually supports. |
| Denied or revoked | Stop presenting stale controls, invalidate derived selections, and offer a clear path to Settings or reauthorization where supported. |
| Unsupported or failed | Explain the target/device limitation without pretending that a local model or manual toggle can substitute for Family Controls. |

`AuthorizationStatus` is a system fact, not proof that a monitor extension has run or that a shield is currently effective. Keep separate state for authorization, selection, schedule registration, extension callback, managed-setting intent, and observed system result.

## FamilyActivityPicker is a privacy boundary

`FamilyActivityPicker` is a SwiftUI view for selecting applications, categories, and web domains. The app receives a `FamilyActivitySelection` containing opaque values. Those values are deliberately useful as handles for Family Controls, Device Activity, and Managed Settings without revealing the selected identities to the app.

The selection contract has several consequences:

1. The selection is user-mediated. Do not replace it with a custom list of installed apps or a network catalog.
2. Applications, categories, and web domains are represented by tokens. Do not log them, send them to a server, use them as analytics identifiers, or ask a model to decode them.
3. A parent-device picker can represent authorized child-device content; an individually authorized picker represents the same device. The UI should name the scope.
4. A revoked authorization voids selections supplied while the app was authorized. Treat persisted selections as revocable configuration, not durable identity.
5. An empty selection is a valid state. It should produce an explicit “nothing selected” state rather than an accidental all-app or all-web rule.

The right handoff is:

```text
picker binding -> validated app-owned policy -> ManagedSettings / DeviceActivity input
```

The wrong handoff is:

```text
picker binding -> raw token logging -> server analytics -> model-generated block list
```

If the product needs human-readable labels, use the framework’s system-provided activity labels or design copy around categories and user intent. Do not manufacture identity from opaque values.

## Device Activity schedules and events

`DeviceActivityCenter` starts and stops named monitoring activities. A `DeviceActivitySchedule` uses date components for an interval and can repeat. A warning time lets the system notify the monitor extension before an interval or event threshold. `DeviceActivityEvent` describes the applications, categories, or web domains to observe and a threshold such as a duration.

Treat names as durable identifiers. Apple documents that a second activity with the same name overwrites the previous schedule, so use a stable namespace and make replacement intentional. Store the app-owned policy revision alongside the name; do not assume that “start monitoring succeeded” means the latest UI state won the race.

Device activity measures the time an application, category, or web domain is frontmost. Web-domain activity can include Safari and supported third-party browser contributions. The activity accumulates according to the time zone of the scheduled start date. A threshold event with `includesPastActivity` has different semantics from a new-only threshold and needs a visible explanation in the product.

Use a route record for each schedule:

| Field | Required decision |
| --- | --- |
| Activity name | Stable `DeviceActivityName`, namespace, and replacement policy. |
| Calendar interval | Start/end components, repeating behavior, warning time, time-zone assumption. |
| Event key | Stable `DeviceActivityEvent.Name` and the owning policy revision. |
| Scope | Application, category, web-domain, or all-activity input from the user’s selection. |
| Threshold | Duration and whether past activity is included. |
| Consequence | Notification, shield, local UI update, or a parent-approved settings mutation. |
| Recovery | What happens after process termination, authorization change, time-zone change, or selection revocation. |

`DeviceActivityCenter` callbacks and schedule state are not a foreground UI stream. The system can execute Device Activity code when the main app is not running, and the monitor callbacks are system lifecycle events. Make callback handling idempotent, bounded, and independent of an in-memory SwiftUI model.

The monitor extension receives interval and threshold callbacks such as:

- interval will start and did start;
- interval will end and did end;
- event will reach its threshold; and
- event did reach its threshold.

Apple notes that activity begins when the device is first used within the interval and ends when the person first uses the device outside it; corresponding callbacks are not evidence that the device was continuously active. The extension should persist only the minimum app-owned policy state it needs and should not require a network round trip to apply a pre-approved local shield.

## Managed Settings is intent, not an absolute device readout

`ManagedSettingsStore` groups the settings an app controls. A named store lets an app keep policy domains separate. The `shield` settings can cover selected applications, categories, and web domains; other settings cover App Store, media, passcode, cellular, Safari, Siri, and related device behavior.

Setting a value to `nil` removes the app’s configuration for that setting. Multiple stores and system policy can contribute to the effective result, and Apple explicitly states that the system determines the effective state rather than guaranteeing that one app’s requested values govern device behavior. Therefore:

- distinguish requested policy from effective policy;
- treat `clearAllSettings()` as a mutation with a specific store owner, not a universal reset of every source of restriction;
- record the store name and policy revision;
- avoid claiming that a write succeeded merely because no Swift error was thrown; and
- verify a real protected app or website on a physical device.

When an authorization or token expires, refresh or discard the affected token collection according to the documented API. A stale token is not a safe identifier to keep retrying.

## Shields are system surfaces with an extension contract

Managed Settings can cause the system to cover an application or website with a shield. `ShieldConfigurationDataSource` customizes the appearance. The system provides a default appearance for properties left `nil`, and it falls back to the default if the extension takes too long. Return a compact, deterministic configuration quickly; do not fetch remote artwork, call a model, or wait for a server in the configuration path.

`ShieldConfiguration` can define the icon, background blur style/color, title, subtitle, primary button, secondary button, and secondary submenu labels. Use `ShieldConfiguration.Label` for text and keep the message calm, specific, and accessible. A shield should state the policy outcome and the next permitted action, not shame the person or expose a hidden app/site identity.

`ShieldActionDelegate` receives actions for a shield and an opaque application, web-domain, or category token. The system does not provide the shielded identity to preserve Family Sharing privacy. Return an intentional `ShieldActionResponse`:

- `.none` when the extension needs no further system action;
- `.defer` when the decision needs a controlled later step;
- `.close` when the system should close the current app or browser; or
- `.openParentalControlsApp` when the parent-controls app should be opened.

An action delegate is not an authorization bypass. “Open parental controls” must still lead to the product’s authentication and policy review flow.

## Device Activity reports are sandboxed SwiftUI surfaces

`DeviceActivityReport` is a SwiftUI view. The system asks a `DeviceActivityReportExtension` to provide the view for a custom context and `DeviceActivityFilter`. Filters can select a date segment, users, devices, applications, categories, and web domains. `DeviceActivityResults` is an asynchronous sequence for filtered activity data.

The report extension is an extension target with the `com.apple.deviceactivityui.report-extension` point. Apple documents that it runs in a sandbox that prevents network requests and prevents moving sensitive content outside the extension address space. That is a central product boundary:

- the host app can own filter controls and context selection;
- the report extension owns the sensitive report computation and view;
- the extension must not upload report contents or ask a remote service to interpret them;
- a Foundation Models proposal must stay within the permitted process/data boundary; and
- a host screen showing a report container is not proof that report data was delivered.

The report’s input and output should be versioned as a privacy-preserving contract. Do not serialize a report into a general-purpose analytics event. For testing, use fixture filters and synthetic app-owned display data in the host, then separately prove system delivery on a physical authorized device.

## Native SwiftUI and Liquid Glass composition

Use system navigation, sheets, pickers, toggles, date components, and buttons first. Liquid Glass is a surface treatment for the app-owned control layer, not a reason to rebuild Family Activity Picker, the system authorization sheet, or the system shield.

A strong app-owned hierarchy is:

1. a plain-language outcome (“Quiet hours” or “Study window”);
2. a compact authorization/relationship status card;
3. a selection summary that never invents token identity;
4. schedule and threshold controls;
5. a visible requested-versus-effective settings state;
6. an optional report context/filter surface; and
7. a reviewable action row for applying or clearing policy.

Use a single glass container for related controls and keep high-frequency actions legible when Reduce Transparency, Increase Contrast, Dynamic Type, or VoiceOver changes the environment. Do not put a large blurred glass panel behind a system shield or make the user hunt through decorative layers for “clear settings.”

The design page and route worksheet turn this into a reusable shell:

- [Screen Time native design review](../21-design-deep-dives/157-swiftui-family-controls-device-activity-managed-settings-review-design.md)
- [Screen Time capability route worksheet](../50-capability-recipes/160-swiftui-family-controls-device-activity-managed-settings-review-route.md)
- [Screen Time proof matrix](../60-verification/154-swiftui-family-controls-device-activity-managed-settings-proof-matrix.md)
- [Screen Time compile-oriented recipes](../70-code-recipes/172-swiftui-family-controls-device-activity-managed-settings-review-recipes.md)

## Optional on-device AI boundary

Foundation Models can help turn app-owned, non-identifying policy configuration into a draft explanation or suggestion:

```text
user intent + app-owned schedule values + app-owned preference labels
        -> typed explanation/proposal
        -> user review
        -> explicit Family Controls / Managed Settings action
```

Do not pass opaque application, category, or web-domain tokens to the model. Do not ask the model to infer a person’s identity, diagnose behavior, rank a child’s worth, or decide that a restriction should be applied without the authorized adult’s review. Do not pass raw Device Activity report data outside the report extension’s permitted boundary.

Good proposal fields are narrow and reviewable: a human-readable schedule name, a duration, a warning lead time, a consequence label, and a short explanation. Validate every value against hard product limits, discard stale proposals when authorization or policy revision changes, and make “apply” a separate user action. If Foundation Models is unavailable, show the deterministic policy editor; AI is an enhancement, not a capability gate.

## Accessibility, privacy, and trust

Screen Time is a high-trust experience. The app should:

- announce authorization state, scope, and pending system actions to VoiceOver;
- expose selection, schedule, threshold, apply, clear, and report-filter controls with labels and values;
- preserve Dynamic Type and sufficient contrast in app-owned glass controls and shield copy;
- make timeout, revoked authorization, empty selection, and report-unavailable states actionable without color alone;
- avoid using shame, countdown anxiety, or hidden escalation as the primary interaction;
- explain whether the person is managing their own device or a child’s authorized device;
- never log opaque tokens or sensitive report values; and
- provide a deterministic non-AI route for every policy decision.

The privacy story must be understandable in the UI: what the system sees, what the app receives, what stays inside an extension, and what the app will never upload. A generic privacy-policy link does not replace an in-context explanation before authorization.

## Verification boundary

Separate these claims:

| Claim | Minimum proof |
| --- | --- |
| Capability is configured | Inspect app and extension entitlements in the signed archive and verify the distribution request state. |
| Authorization works | On a supported physical device, complete the individual or parent/child system flow and capture the resulting status. |
| Picker is private | Demonstrate that the app receives opaque selections and does not expose or upload identities. |
| Schedule works | Start a named schedule and show monitor-extension callbacks at the intended interval/threshold. |
| Settings work | Apply a selected shield, observe the system shield over a real app/site, then clear the named store and verify the expected result. |
| Report works | Present a `DeviceActivityReport` with a filter and show that the report extension receives system data in its sandbox. |
| Shield works | Exercise custom configuration, timeout/default behavior, each button, and action response on a physical device. |
| AI is safe | Test availability, stale proposal rejection, token exclusion, explicit review, cancellation, and deterministic fallback. |
| Release works | Archive, inspect embedded extension entitlements, install through TestFlight, and repeat the target capability flow. |

The complete evidence table lives in the proof matrix; a simulator preview, an authorization Boolean, a token count, a local report fixture, or an archive key is not enough.

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
