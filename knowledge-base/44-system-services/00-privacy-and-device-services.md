# Privacy and Device Services

This card groups system capabilities where Apple intentionally controls access to family activity, protected device state, searchable personal content, assistive technologies, or app integrity. Start with the person’s outcome and the minimum data/control needed; do not treat a framework as permission to collect more information than the system contract allows.

## Route matrix

| User outcome | First route | Boundary to verify | Proof that matters |
| --- | --- | --- | --- |
| Let a guardian manage schedules or restrictions across a Family Sharing group | [Screen Time Technology Frameworks](https://developer.apple.com/documentation/ScreenTimeAPIDocumentation) using [Family Controls](https://developer.apple.com/documentation/familycontrols), [Managed Settings](https://developer.apple.com/documentation/managedsettings), and [Device Activity](https://developer.apple.com/documentation/deviceactivity) | Family Controls entitlement, App ID/extension configuration, guardian authorization, Family Sharing context, privacy-preserving tokens, extension targets, and scheduled execution | Signed target plus Screen Time extension on supported devices; test authorization, schedules, extension callbacks, revocation, and recovery. Do not claim raw child activity access. |
| Apply time-based settings without requiring the other device’s app to be open | [Managed Settings connection with frameworks](https://developer.apple.com/documentation/managedsettings/connectionwithframeworks) and Device Activity | Parent/guardian authority, token scope, schedule/event lifecycle, extension execution, and managed-settings failure/recovery | Physical multi-device or supported-device flow with resettable authorization and schedule fixtures; simulator layout is not proof of the system policy effect |
| Make private app records searchable from Spotlight | [Core Spotlight](https://developer.apple.com/documentation/corespotlight) and [adding app content to Spotlight indexes](https://developer.apple.com/documentation/corespotlight/adding-your-app-s-content-to-spotlight-indexes) | What data is appropriate to index, private/named index, protection class, expiration, deletion synchronization, deep-link routing, and user control | On-device indexing/search/deep-link test; delete or edit the source record and verify the index follows it. Avoid indexing sensitive content by default. |
| Make typed app entities available to Spotlight and system intelligence | [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight) with [App Intents](https://developer.apple.com/documentation/appintents/) | Stable entity identifiers, display representation, query/authorization behavior, indexed fields, supported system experiences, and safe intent side effects | Test Spotlight/Siri/Shortcuts invocation against real entities; validate stale/deleted identifiers and confirmation for mutations. |
| Make a SwiftUI app usable with assistive technologies | [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals) and [Accessibility](https://developer.apple.com/documentation/accessibility/) | Labels, values, traits, focus, actions, reading order, Dynamic Type, contrast, motion/transparency settings, VoiceOver, Voice Control, and Switch Control | Physical-device accessibility matrix using the main user tasks; use Accessibility Inspector as a diagnostic tool, not as a substitute for user-perspective testing. |
| Provide a streamlined experience for Assistive Access | [Optimizing your app for Assistive Access](https://developer.apple.com/documentation/Accessibility/optimizing-your-app-for-assistive-access) and SwiftUI `AssistiveAccess` | Whether the standard UI is sufficient, `Info.plist` declaration, scene choice, flexible layout, removed/changed workflows, and system navigation differences | Test Assistive Access on a physical supported device with the actual task matrix. Do not infer Assistive Access behavior from a normal simulator run. |
| Declare accessibility support on an App Store product page | [Accessibility declarations](https://developer.apple.com/documentation/appstoreconnectapi/configuring-accessibility-declarations) | Device-family-specific supported features, declaration state, App Store Connect account/API access, and alignment with observed behavior | Separate in-app accessibility testing from App Store metadata publication; publish only claims the tested build actually supports. |
| Assess app/device integrity or abuse risk | [DeviceCheck](https://developer.apple.com/documentation/devicecheck) and the relevant App Attest route | Server-side verification, keys/attestation, account/service trust boundary, replay/abuse model, privacy, failure/offline behavior, and whether integrity is actually needed | Unit-test the policy and failure modes; signed device plus server verification in a controlled environment. A local token or simulator mock is not fraud-resistance proof. |

## Screen Time route shape

Use this sequence for a parental-control idea:

1. Define the guardian’s decision and the minimum setting or schedule required.
2. Add the Family Controls capability and verify the entitlement/provisioning path for the app and every Screen Time extension target.
3. Request authorization in context and model denied, revoked, unavailable, and extension-failure states.
4. Use the privacy-preserving tokens and framework-owned APIs; never build a hidden analytics pipeline from a child’s app/site identities or activity.
5. Keep scheduled Device Activity work idempotent and resilient to the app not running.
6. Test the parent/device/extension relationship on supported physical configurations and record the exact signing/development entitlement state.

## Search and accessibility route shape

For a local-first utility, a strong system route is:

`trusted local record -> privacy-reviewed index/entity -> system search or assistive technology -> typed deep link -> validated app route`

Maintain the index when records are created, edited, or deleted. Keep system-discoverable content consistent with the app’s privacy and retention contract. Treat accessibility as a behavior and task-completion requirement, not as a final visual checklist.

## Refuse to infer

- Family Controls means the app can inspect a child’s raw activity or identify apps outside the authorized privacy boundary.
- A local Spotlight index is automatically appropriate for every private record.
- An AppEntity or App Intent can mutate data without deterministic validation and confirmation.
- Standard SwiftUI controls eliminate the need to test the actual user tasks with assistive technologies.
- A normal simulator run proves VoiceOver, Assistive Access, family authorization, extension execution, or device-integrity behavior.
- A declared App Store accessibility feature is proof that the shipped build supports it.

## Sources

- [Screen Time Technology Frameworks](https://developer.apple.com/documentation/ScreenTimeAPIDocumentation)
- [Family Controls](https://developer.apple.com/documentation/familycontrols)
- [Configuring Family Controls](https://developer.apple.com/documentation/Xcode/configuring-family-controls)
- [Managed Settings](https://developer.apple.com/documentation/managedsettings)
- [Device Activity](https://developer.apple.com/documentation/deviceactivity)
- [Manage settings on devices in a Family Sharing group](https://developer.apple.com/documentation/managedsettings/connectionwithframeworks)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [Adding your app’s content to Spotlight indexes](https://developer.apple.com/documentation/corespotlight/adding-your-app-s-content-to-spotlight-indexes)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [Accessibility](https://developer.apple.com/documentation/accessibility/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Optimizing your app for Assistive Access](https://developer.apple.com/documentation/Accessibility/optimizing-your-app-for-assistive-access)
- [Configuring accessibility declarations for your app](https://developer.apple.com/documentation/appstoreconnectapi/configuring-accessibility-declarations)
- [DeviceCheck](https://developer.apple.com/documentation/devicecheck)
