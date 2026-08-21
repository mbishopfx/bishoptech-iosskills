# AppTrackingTransparency and advertising-identity capability route

Use this route when a product genuinely needs app-related data for tracking across apps or websites, or needs the advertising identifier for an approved advertising/attribution path. Keep core product analytics, first-party personalization, account identity, on-device AI, and cross-app tracking as separate data uses.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | Understand and choose an optional tracking/advertising feature |
| Purpose | Exact tracking use shown in `NSUserTrackingUsageDescription` and pre-prompt UX |
| System API | `ATTrackingManager.requestTrackingAuthorization` and `trackingAuthorizationStatus` |
| Status | Not determined, restricted, denied, or authorized |
| Identifier | `ASIdentifierManager.shared().advertisingIdentifier` only after the ATT route and status check |
| Fallback | Identifier-free/contextual/aggregate product behavior |
| AI | Local preferences and model context remain separate from IDFA and ATT status |
| UI | Native SwiftUI explanation/status/settings help; Liquid Glass only as an optional grouping layer |
| Proof | Built Info.plist, active-app prompt, status transitions, all-zero identifier cases, physical device, accessibility, privacy, release/review evidence |

## 1. Classify the data use before adding a prompt

Write a data-flow table:

- what is collected;
- where it is processed;
- whether it is shared with another company;
- whether it is used to track across apps/sites;
- whether the app can operate without it;
- what identifier or event is emitted;
- what the user sees and can change.

Only then decide whether ATT applies. Do not use the prompt to ask for generic “analytics permission.”

## 2. Configure the target

Add `NSUserTrackingUsageDescription` to the target that requests authorization. Inspect the built Info.plist and ensure the string describes the actual data use.

Do not request from an app extension. The Apple API documentation states that calls through an app extension do not prompt. Keep the request coordinator in the active containing app.

## 3. Request once and read status

The app should:

1. wait until the app is active;
2. avoid concurrent permission prompts;
3. read `trackingAuthorizationStatus`;
4. request only when status is `notDetermined` and the feature is understood;
5. route `authorized` to the permitted feature;
6. route `denied` and `restricted` to the fallback;
7. refresh status when returning from Settings.

The system remembers a choice for the installation. A completion callback is evidence of the user/system decision for that request, not permission to collect unrelated data.

## 4. Access the advertising identifier narrowly

Use AdSupport only for the advertising purpose documented by Apple. Read the identifier after checking ATT status. Treat an all-zero UUID as unavailable and do not replace it with a fingerprint from other device properties.

Do not store IDFA as an account primary key, pass it into a model by default, include it in logs, or use it for first-party identity. If the route is denied, restricted, simulator, macOS, or visionOS-compatible, keep the identifier-free path active.

## 5. Build the fallback first

The fallback can use:

- contextual content;
- aggregate conversion events;
- explicit campaign codes;
- local user preferences;
- on-device model context;
- first-party account identifiers only when separately authorized;
- platform-provided non-tracking attribution routes where appropriate.

Do not make the fallback intentionally worse to coerce consent.

## 6. AI boundary

Use a typed policy:

ATT status + feature need -> route selection -> identifier allowed/unavailable -> model/analytics configuration

The AI may personalize locally without IDFA. It should not infer consent from model behavior or use a denied status as a user attribute. Keep status diagnostics aggregate and privacy-safe.

## 7. Native design and recovery

Provide a SwiftUI status surface with the current state, exact optional feature, identifier-free behavior, privacy explanation, and Settings help. If the user changes the global or app tracking setting, refresh the state on foreground and recompute the route.

Use Liquid Glass only as a clear status container. Keep Continue without tracking visible, accessible, and functional.

## 8. Failure states

Handle:

- missing purpose string;
- request while inactive;
- another permission request pending;
- concurrent request;
- app extension call;
- not determined, denied, restricted, authorized;
- global tracking setting disabled;
- user changes Settings after authorization;
- all-zero identifier;
- simulator/macOS/visionOS compatible environment;
- attribution service/network failure;
- model/analytics fallback.

## 9. Minimum evidence bundle

- data-flow and App Store privacy classification;
- built Info.plist purpose string;
- active-app first-run request;
- no prompt from extension and no concurrent prompt behavior;
- all status states and Settings refresh;
- authorized and all-zero IDFA physical-device evidence;
- identifier-free analytics/AI route;
- accessibility/localization/reduced-motion check;
- signed archive and review/distribution evidence.

## Sources

- [AppTrackingTransparency](https://developer.apple.com/documentation/apptrackingtransparency)
- [ATTrackingManager](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager)
- [requestTrackingAuthorization(completionHandler:)](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/requesttrackingauthorization%28completionhandler%3A%29)
- [trackingAuthorizationStatus](https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/trackingauthorizationstatus)
- [AdSupport](https://developer.apple.com/documentation/adsupport)
- [ASIdentifierManager](https://developer.apple.com/documentation/adsupport/asidentifiermanager)
- [advertisingIdentifier](https://developer.apple.com/documentation/adsupport/asidentifiermanager/advertisingidentifier)
- [NSUserTrackingUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsusertrackingusagedescription)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
