# AppTrackingTransparency privacy proof matrix

Use this matrix to prove tracking consent and advertising-identifier behavior. A status enum or nonzero UUID is not proof that the product’s complete data flow is permitted or correctly implemented.

| Claim | Evidence | Failure fixture / boundary |
| --- | --- | --- |
| ATT applies to the documented use | Data-flow review identifies cross-app/site tracking and sharing, or documents why a separate data use is not ATT | Generic analytics or AI feature mislabeled as tracking permission |
| Purpose copy is present | Built target Info.plist contains `NSUserTrackingUsageDescription` with accurate product language | Source key absent from installed target or vague copy |
| Request is system-owned | Active containing app shows Apple prompt; no app-owned imitation is used | Request from extension, inactive app, or custom modal |
| Request timing is controlled | Another permission prompt, concurrent call, and background/foreground fixtures show a single coordinator | Prompt silently lost or repeated on every launch |
| Status is modeled correctly | Not determined, restricted, denied, and authorized paths are separately observed | `notDetermined` assumed to guarantee a prompt or denied treated as app failure |
| Choice persistence is understood | Reinstall/reset and Settings changes show status refresh on foreground | Cached status never updates or user cannot change choice |
| IDFA access is gated | Physical authorized device returns permitted identifier path; denied/restricted/unrequested path is handled before access | IDFA read before ATT, all zeros treated as identity, or fingerprint fallback |
| Identifier scope is respected | IDFA is used only for documented advertising/attribution; no account primary key or model telemetry | Cross-purpose reuse or raw identifier logging |
| All-zero behavior is handled | Simulator, denied, unrequested, restricted, macOS, and visionOS-compatible fixtures produce identifier-free route | Test environment gives false confidence from a nonzero value |
| `isAdvertisingTrackingEnabled` is not used for new consent | Source/build scan or code review shows ATT status owns the decision | Deprecated AdSupport property drives the route |
| Fallback is complete | Contextual/aggregate/local preference/identifier-free AI paths complete the intended user task | Denied experience is intentionally broken to coerce consent |
| AI privacy boundary is explicit | Model input contract excludes IDFA by default and does not infer consent from behavior | Model receives IDFA, status as a hidden user trait, or raw attribution payload |
| Accessibility is usable | VoiceOver, Dynamic Type, high contrast, Reduce Motion, Voice Control, Switch Control, keyboard, and pointer complete allow/continue/status tasks | Color-only status, guilt copy, or unreachable fallback |
| Privacy/release evidence is complete | App Privacy details, signed archive, device run, review metadata, and partner/service configuration are inspected | Local prompt or Debug UUID treated as App Store readiness |

## Fixture set

- first launch with `notDetermined`;
- active app request success;
- inactive/background request;
- another permission prompt pending;
- concurrent request;
- app-extension request;
- authorized, denied, restricted;
- global tracking setting disabled;
- app setting changed in Settings while app is suspended;
- reinstall/reset;
- authorized physical device with identifier;
- denied/restricted/unrequested all-zero identifier;
- simulator all-zero identifier;
- macOS/visionOS-compatible all-zero behavior;
- identifier-free analytics and on-device AI;
- long localized purpose, large text, VoiceOver, reduced motion, and high contrast;
- offline attribution service and model-unavailable fallback.

## Evidence ladder

1. Data-flow and purpose-string review.
2. Info.plist and target configuration inspection.
3. Authorization coordinator unit/UI tests.
4. Status/Settings transition tests.
5. Physical-device authorized/denied/restricted IDFA observation.
6. Simulator and unsupported-surface fallback evidence.
7. Accessibility/privacy/App Store review evidence.
8. Signed archive and production attribution configuration review.

Record OS build, device class, target, status, identifier redaction state, feature route, and fallback result. Never print or commit an advertising identifier.

## Sources

- [AppTrackingTransparency](https://developer.apple.com/documentation/apptrackingtransparency)
- [ATTrackingManager](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager)
- [ATTrackingManager.AuthorizationStatus](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/authorizationstatus)
- [requestTrackingAuthorization(completionHandler:)](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/requesttrackingauthorization%28completionhandler%3A%29)
- [trackingAuthorizationStatus](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/trackingauthorizationstatus)
- [AdSupport](https://developer.apple.com/documentation/adsupport)
- [ASIdentifierManager](https://developer.apple.com/documentation/adsupport/asidentifiermanager)
- [advertisingIdentifier](https://developer.apple.com/documentation/adsupport/asidentifiermanager/advertisingidentifier)
- [isAdvertisingTrackingEnabled](https://developer.apple.com/documentation/adsupport/asidentifiermanager/isadvertisingtrackingenabled)
- [NSUserTrackingUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsusertrackingusagedescription)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
