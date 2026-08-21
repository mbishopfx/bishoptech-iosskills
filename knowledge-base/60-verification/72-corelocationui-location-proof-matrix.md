# CoreLocationUI and location proof matrix

This matrix separates the evidence for a native location button, a Core Location result, a map or geocoder response, an on-device AI proposal, a background route, and a released system experience. Location is physical, privacy-sensitive, and stateful; no single screenshot proves the complete feature.

The proof chain is:

~~~text
native authorization surface -> service state -> location observation
  -> accuracy/freshness -> map/domain/AI proposal -> user review
  -> save/share/background behavior -> signed release artifact
~~~

## Claim-to-evidence matrix

| Claim | Minimum evidence | Stronger evidence | Do not infer |
| --- | --- | --- | --- |
| The target uses LocationButton correctly | Named target compile and SwiftUI UI test | Signed build on each supported platform | That the button grants access or returns a location. |
| The button is recognizable and legible | HIG review, Dynamic Type, contrast, localization, and reduced-transparency checks | Task-based accessibility run on device | That a custom glass pill has the system location trust behavior. |
| One-time authorization works | Physical-device run from not determined state, first confirmation, and later tap | Reset authorization and repeat across supported OS/device families | That an action callback means authorization was granted. |
| The app receives a current location | Device run with authorization, service start, timestamp, accuracy, and cancellation evidence | Representative indoor/outdoor and radio conditions | That the coordinate is exact, current enough for every task, or semantically true. |
| Approximate accuracy is handled | Reduced-accuracy device state with coarse UI and route fallback | Test precise request only at the feature that needs it | That a map pin is precise because it renders. |
| Denied/restricted states work | Settings denial/restriction run and no-loop UI | Revoke permission during an active feature | That a disabled map is a framework bug rather than a state to design. |
| Live updates work | Async stream/delegate fixture and cancellation test | Physical-device foreground/background and energy test | That one update proves sustained delivery or background eligibility. |
| Map/geocoder handoff works | Signed run with selected location and provider result | Offline, stale, ambiguous, and manual-correction scenarios | That a placemark proves identity or presence. |
| AI geo-context is safe | Input record with source revision, precision, model route, and review state | Device memory/cancellation, model unavailable, retention, and user correction tests | That on-device implies correct, private-by-default, or consent for sharing. |
| Sharing works | Actual ShareLink/system composer and selected output | Destination app/recipient path in a TestFlight-like build | That a share sheet callback proves receipt. |
| Background route works | Correct capability/entitlement, signed target, device delivery, and lifecycle logs | Reboot, force quit, low power, denied, and location-settings changes | That foreground simulator updates prove background behavior. |

## Test fixture and device matrix

Use deterministic fixtures for UI/state tests:

- no authorization and system Location Services disabled;
- when-in-use authorization;
- always authorization only for a separately justified route;
- reduced accuracy and temporary full-accuracy response;
- denied and restricted states;
- no location available;
- stale last-known location;
- fresh location with low and high horizontal accuracy;
- ambiguous or missing geocoder result;
- provider/network failure;
- model unavailable or canceled.

Use physical devices for:

- first-tap LocationButton confirmation;
- one-time authorization expiry after leaving the app;
- repeated taps after the explanation has been acknowledged;
- reduced versus full accuracy;
- indoor, outdoor, airplane-mode, and poor-signal behavior where relevant;
- actual map and geocoder services;
- background/foreground transition and battery/thermal behavior;
- camera/photo/contact/message/location combinations when the feature composes them.

The simulator is useful for deterministic location fixtures, state rendering, and UI automation. It is not proof of GPS, Wi-Fi, cellular, compass, radio availability, energy, real authorization prompts, or physical background delivery.

## UI and accessibility proof

Perform the task rather than inspecting only a screenshot:

1. read the explanation;
2. activate the location action with VoiceOver or alternate input;
3. understand the authorization state;
4. inspect approximate/precise/stale status;
5. correct or select a place;
6. accept or reject an AI proposal;
7. save or share;
8. delete or expire the location context.

Repeat at large text sizes, in dark and light appearances, with increased contrast, reduced transparency, Reduce Motion, RTL, long translations, pointer/keyboard, and compact/expanded layouts.

Check that:

- LocationButton text never truncates;
- permission and service changes are announced once and clearly;
- map markers do not trap accessibility focus;
- approximate location is not described as exact;
- stale results are distinct from current results;
- AI text has a generated/proposed label;
- every externally visible action has a semantic control and confirmation boundary.

## Accuracy and freshness assertions

For every location accepted into a domain record, record:

- source timestamp;
- acceptance timestamp;
- horizontal accuracy or coarse/precise state;
- selected Core Location service;
- whether the person selected or corrected a place;
- source revision;
- retention expiration.

Test task-specific freshness thresholds. A one-minute-old value might be acceptable for a journal tag and unsafe for turn-by-turn navigation. Do not use a single global “location valid” Boolean.

## AI and privacy assertions

Verify that:

- the model receives only the precision/context needed for the selected task;
- a raw track is not included when a place label is sufficient;
- source, derived place, proposal, and user-authored text are separate;
- proposal acceptance is explicit;
- model version/route and device availability are recorded;
- cancellation and memory pressure stop the route cleanly;
- denied permission does not trigger a hidden fallback request;
- raw coordinates and sensitive place inferences do not enter analytics or crash logs;
- deletion removes raw location and derived/proposal copies according to the product policy;
- any remote map, geocoder, share, or server route is disclosed and separately tested.

## Background and extension proof

If the feature claims background behavior, add a distinct matrix:

| Route | Evidence |
| --- | --- |
| Background live updates | Capability/usage configuration, signed device run, foreground/background transitions, energy, delivery gaps, and stop conditions. |
| Region or condition monitoring | Registered condition, system event, relaunch behavior, stale condition handling, and notification/user-action proof. |
| Location Push Service Extension | Entitlement, provider/server challenge, signed extension invocation, response policy, privacy, and failure retry. |
| Watch or companion | Phone/watch authorization and handoff separately, with two-device reconciliation and offline behavior. |

Do not use the simple LocationButton route as release evidence for one of these extensions.

## Release artifact proof

Inspect the archived/signed target for:

- correct bundle identifier and build identity;
- intended deployment target and SDK;
- CoreLocationUI and Core Location linkage;
- required usage descriptions;
- background modes, capabilities, and entitlements only when justified;
- privacy manifest and App Store privacy declarations;
- MapKit/geocoder/network configuration;
- model asset or Foundation Models availability handling;
- no debug coordinate, mock provider, or test-only bypass in the release path.

Record the evidence with a named device, OS, build, authorization state, and test timestamp. A source-link or simulator run is not release proof.

## Related routes

- [CoreLocationUI and least-privilege location access](../42-framework-deep-dives/55-corelocationui-and-least-privilege-location.md)
- [Location Button and privacy-first map design](../21-design-deep-dives/75-location-button-and-privacy-first-map-design.md)
- [CoreLocationUI and on-device location route](../50-capability-recipes/78-corelocationui-and-on-device-location-route.md)
- [CoreLocationUI and LocationButton recipes](../70-code-recipes/90-corelocationui-locationbutton-recipes.md)

## Sources

- [CoreLocationUI](https://developer.apple.com/documentation/corelocationui)
- [LocationButton](https://developer.apple.com/documentation/corelocationui/locationbutton)
- [CLLocationButton](https://developer.apple.com/documentation/corelocationui/cllocationbutton)
- [Core Location](https://developer.apple.com/documentation/CoreLocation)
- [CLLocationManager](https://developer.apple.com/documentation/corelocation/cllocationmanager)
- [CLLocationUpdate](https://developer.apple.com/documentation/corelocation/cllocationupdate)
- [CLAuthorizationStatus](https://developer.apple.com/documentation/corelocation/clauthorizationstatus)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/CoreLocation/requesting-authorization-to-use-location-services?changes=_7)
- [Adopting live updates in Core Location](https://developer.apple.com/documentation/corelocation/adopting-live-updates-in-core-location?changes=lat_5)
- [Human Interface Guidelines privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performance testing](https://developer.apple.com/documentation/xctest/performance-tests)
