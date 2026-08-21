# AppTrackingTransparency and AdSupport: tracking consent and advertising identity boundaries

AppTrackingTransparency is Apple’s system permission route for access to app-related data used to track a user or device across apps and websites. AdSupport exposes the advertising identifier, but current Apple documentation makes that identifier conditional on the AppTrackingTransparency flow and user authorization.

The route is:

purpose explanation -> active containing-app request -> authorization status -> permitted attribution/advertising path or identifier-free fallback

ATT is not a blanket permission for analytics, first-party product telemetry, on-device AI personalization, or every form of measurement. Define each data use separately.

## 1. What ATT covers

Apple’s AppTrackingTransparency overview says apps must use the framework when they collect data about end users and share it with other companies for tracking across apps and websites. The system presents the tracking request and exposes the app’s status.

The minimum route is:

1. add `NSUserTrackingUsageDescription` to the built target’s Information Property List;
2. explain the actual tracking purpose in plain language;
3. call `ATTrackingManager.requestTrackingAuthorization` from an active containing app;
4. read `ATTrackingManager.trackingAuthorizationStatus`;
5. use the result to select the permitted advertising/attribution route;
6. keep an identifier-free product path for denied, restricted, unavailable, or not-yet-requested states.

Do not use ATT as a cosmetic prompt before a product already works. The copy and data flow should describe a real decision.

## 2. Authorization state machine

`ATTrackingManager.AuthorizationStatus` includes:

- `notDetermined`: the app has not received a final user choice, or the platform cannot determine it in a compatible environment;
- `restricted`: access is controlled or unavailable because of system/profile policy;
- `denied`: the user declined tracking;
- `authorized`: the user granted tracking authorization.

Read status before deciding whether to request. The request is one-time for the installation; iOS remembers the choice and does not prompt again unless the user uninstalls and reinstalls the app. The user can change access later in Settings, so refresh status when the app returns to the foreground.

Do not assume `notDetermined` always means a prompt will appear. The request only prompts while the application is active, does not display while another permission request is pending, and concurrent requests are not preserved by iOS. Calls through an app extension do not prompt.

## 3. System prompt timing and product sequencing

Request ATT at a deliberate point where the user understands the feature that benefits from it. Do not race location, notification, HealthKit, SensorKit, camera, or other permission prompts. Keep a single permission coordinator that waits for the app to be active and for other system prompts to finish.

The system sheet is Apple-owned. The containing app can explain purpose before the call and can explain the result afterward, but it must not recreate the system prompt or imply that denying tracking blocks the app’s core functionality when it does not.

If the feature is optional advertising or cross-app attribution, allow the user to continue without it. If the data flow cannot operate without authorization, explain the exact consequence and provide a useful non-tracking alternative.

## 4. `NSUserTrackingUsageDescription`

The purpose string is part of the permission contract. It should say:

- what data use is requested;
- who receives or compares it, if applicable;
- what user-facing benefit depends on it;
- that the user can decline and still use the non-tracking parts of the app.

Avoid “We value your privacy” as the only explanation. Avoid claiming that ATT enables security, faster performance, or on-device intelligence when the actual use is advertising or cross-app measurement.

Inspect the built Info.plist in the signed artifact. A source setting that is not present in the installed target does not make the prompt valid.

## 5. AdSupport and the advertising identifier

`ASIdentifierManager.shared()` provides an `ASIdentifierManager`; its `advertisingIdentifier` is a UUID specific to the device and intended for advertising use. On iOS 14.5 and later and iPadOS 14.5 and later, Apple documents that the app must request tracking authorization before accessing it.

The identifier can be a unique UUID or all zeros. Apple documents all-zero behavior for cases including:

- simulator;
- macOS and compatible iPhone/iPad apps running in visionOS;
- no ATT request on supported iOS/iPadOS versions;
- a denied ATT status;
- restricted profiles/configurations.

Do not treat all zeros as a stable user identity, and do not store the advertising identifier as a permanent account key. Apple recommends accessing it rather than storing it, and the user can change tracking authorization in Settings.

The legacy `ASIdentifierManager.isAdvertisingTrackingEnabled` property is deprecated and replaced by AppTrackingTransparency. Do not build new consent logic around it.

## 6. Attribution, analytics, and AI separation

Create a data-use matrix before reading any identifier:

| Use | ATT implication | Safer fallback |
| --- | --- | --- |
| Cross-app/site tracking | ATT authorization required | Contextual or aggregate measurement |
| Advertising identifier for permitted advertising | Check ATT status and identifier result | Non-personalized advertising/attribution route |
| First-party product analytics | Separate privacy/legal/App Store analysis; not automatically ATT | Aggregate, minimized event model |
| On-device AI personalization | Usually a first-party/device-local feature decision | Local preferences and opt-in product data |
| Account authentication | Use a user-approved account/authentication route | Account-free local identity where possible |
| Device performance diagnostics | Use diagnostic/metrics boundaries | Redacted aggregate metrics |

Do not pass IDFA or ATT status into an on-device model merely because the model can consume it. Do not use a denied state to infer a user’s preferences or identity. A model can remain useful with local settings, contextual content, and explicit in-app choices.

## 7. Privacy and reset behavior

Test and design for:

- first launch with `notDetermined`;
- user allows, then changes Settings to deny;
- user denies, then changes Settings to allow;
- restricted device/profile;
- global “Allow Apps to Request to Track” setting changes;
- reinstall/reset behavior;
- simulator all-zero identifier;
- no network or attribution service failure;
- app background/foreground during the request.

Refresh status when the app becomes active. Do not cache authorization forever. Keep logs free of IDFA, raw device identifiers, user-level attribution payloads, and model prompts that include them.

## 8. Native and Liquid Glass consent design

The containing app can use a native SwiftUI surface to explain:

- what tracking means in this product;
- which optional feature uses it;
- current status;
- what works when denied or restricted;
- a link to the app’s privacy explanation;
- a local, identifier-free alternative.

Liquid Glass can group the explanation and status, but the essential copy should be readable in a plain list or form. Avoid an oversized “Allow tracking” call to action, fake urgency, guilt language, or an animation that makes the denial path look broken. Support Dynamic Type, VoiceOver, Reduce Motion, and localization.

## 9. Verification boundary

Prove separately:

- built Info.plist purpose string;
- active-app prompt timing;
- one-time request and concurrent-prompt behavior;
- every authorization status;
- AdSupport all-zero and authorized identifier behavior on physical device;
- simulator/restricted/macOS/visionOS boundaries;
- foreground status refresh after Settings changes;
- identifier-free analytics/AI/advertising fallback;
- privacy copy, accessibility, and App Store review evidence.

A permission prompt, `authorized` enum, nonzero UUID, or local event log does not prove a lawful data flow, correct attribution, consent in another app, universal device behavior, or release readiness.

## Sources

- [AppTrackingTransparency](https://developer.apple.com/documentation/apptrackingtransparency)
- [ATTrackingManager](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager)
- [requestTrackingAuthorization(completionHandler:)](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/requesttrackingauthorization%28completionhandler%3A%29)
- [trackingAuthorizationStatus](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/trackingauthorizationstatus)
- [ATTrackingManager.AuthorizationStatus](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/authorizationstatus)
- [AdSupport](https://developer.apple.com/documentation/adsupport)
- [ASIdentifierManager](https://developer.apple.com/documentation/adsupport/asidentifiermanager)
- [advertisingIdentifier](https://developer.apple.com/documentation/adsupport/asidentifiermanager/advertisingidentifier)
- [isAdvertisingTrackingEnabled](https://developer.apple.com/documentation/adsupport/asidentifiermanager/isadvertisingtrackingenabled)
- [NSUserTrackingUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsusertrackingusagedescription)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
