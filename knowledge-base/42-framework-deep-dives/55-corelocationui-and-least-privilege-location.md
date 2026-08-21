# CoreLocationUI and least-privilege location access

CoreLocationUI is the system-owned entry point for a user-initiated, one-time location request. It contains the SwiftUI LocationButton and UIKit CLLocationButton. The button is not a location reader, map, geocoder, tracker, or proof that a location was received. It is a trustworthy authorization interaction that the app can place next to the feature that needs a current location.

The correct boundary is:

~~~text
feature intent
  -> native location button
  -> temporary authorization
  -> Core Location service
  -> location update or failure
  -> optional MapKit/geocoder/domain/AI proposal
  -> user review and app-owned record
~~~

Use the narrowest Core Location service that satisfies the feature. Do not request Always authorization or start a background stream because a map card happens to exist.

## LocationButton and CLLocationButton

LocationButton is a SwiftUI View. CLLocationButton is a UIKit UIControl. Both give the user a standard, recognizable way to grant one-time access to current location data.

The important behavior is:

- the first tap can display a system explanation and confirmation;
- after the person agrees, the app receives temporary authorized-when-in-use access, similar to Allow Once;
- that temporary authorization expires when the app is no longer in use;
- future taps can grant one-time access without repeating the explanation;
- if the person already chose While Using the App, tapping the button does not change the app’s authorization status;
- the button’s action runs every time the person taps it;
- tapping the button grants authorization only; the app still needs to fetch a location using Core Location.

The SwiftUI button can use system-provided title values such as Current Location, Send Current Location, Send My Current Location, Share Current Location, or Share My Current Location. The UIKit button exposes icon and label constants plus corner radius and font size. SwiftUI supports label style and symbol variant customization.

Apple’s Human Interface Guidelines also describe limits on customization. The location button should remain recognizable and legible. The system can warn about low contrast, excessive translucency, or text that does not fit; consistent problems can prevent the button from granting access. Test long translations and all accessibility text sizes, not just the default preview.

The framework has platform-specific behavior. Apple documents that the button ignores user input on Mac Catalyst and on compatible iPad and iPhone apps running in visionOS. Do not use a button interaction as proof of location availability on every Apple platform.

## Authorization is a separate state machine

Core Location authorization includes not determined, restricted, denied, authorized when in use, and authorized always states, with some older names deprecated. The app should observe authorization changes and adapt the feature rather than assuming that a successful button action means an update will arrive.

Also track:

- global Location Services enabled or disabled;
- full versus reduced accuracy;
- whether the app is in use when the feature starts;
- whether a background route is actually required;
- the device’s hardware and service availability;
- a current request or service session;
- location unavailable, denied, restricted, or insufficiently in-use diagnostics.

Usage-description keys are required for standard authorization requests. Apple documents that authorization requests fail immediately when required keys are missing. Add only the usage strings needed by the actual target, and make their copy match the feature that caused the request.

Reduced accuracy is not a failure. A nearby recommendation, coarse weather region, or approximate map context may work with reduced accuracy. A feature that truly needs a precise point should explain why and use the documented temporary full-accuracy request path only after the user engages that feature.

## Choose the Core Location service

| Need | Candidate route | Cost and proof boundary |
| --- | --- | --- |
| A single current point after a tap | LocationButton or a normal when-in-use request, then current-location service | User-initiated, foreground-first, temporary or when-in-use access. |
| Navigation or continuous foreground movement | Standard location updates with a configured manager/service | Higher energy; verify accuracy, update cadence, interruption, and map behavior on device. |
| Coarse movement over large distances | Significant-change service | Lower power and less precise semantics; do not present it as a live track. |
| Visit-like place awareness | Visits service | Delayed, system-selected timing; not a real-time arrival detector. |
| Entry/exit for known boundaries | Region or condition monitoring | Device/service/authorization/system-delivery proof; state may be delivered while the app is not active. |
| Work that truly continues in the background | Background activity/session or an appropriate background service | Requires a product reason, target configuration, usage disclosure, energy proof, and real device evidence. |
| Shared location response | Location Push Service Extension when eligible | Entitlement, server/provider, privacy, and signed extension proof; not a generic background shortcut. |

Start with the least expensive and least persistent route. A map view does not by itself justify continuous updates.

## Live updates and modern Swift concurrency

Current Core Location documentation describes CLLocationUpdate and asynchronous live updates. The update value can carry a location when available and diagnostics such as authorization denied, global denial, reduced accuracy, insufficient use, unavailable location, and a required service session. Treat those properties as state, not as incidental logging.

An asynchronous stream still needs lifecycle ownership:

- create the task only when the feature is active;
- cancel when the view or operation ends;
- avoid more than one live stream for the same user action;
- debounce or reduce downstream work when the app does not need every update;
- do not send every raw coordinate to a model or analytics system;
- make a stale or unavailable update visible in the UI;
- keep the last accepted location separate from the latest unreviewed update.

CLLocationManager remains useful for delegate-driven routes, background delivery, service selection, and legacy target compatibility. The manager’s delegate is called on the run loop of the thread where the manager was initialized, so initialize and own it intentionally. Do not create a manager in a short-lived SwiftUI view and expect reliable delivery after the view disappears.

## Map, geocoder, and AI boundaries

CoreLocationUI and Core Location provide location facts and authorization state. MapKit can display or search geographic content. CLGeocoder can translate coordinates into a placemark, but a placemark is not verified identity or proof of a person’s presence.

An on-device model can help:

- summarize a user-selected place;
- rank nearby items after the person requests a recommendation;
- classify a user-provided scene or note using a coarse location context;
- suggest a journal tag from a selected trip segment;
- turn a reviewed place into an app-owned reminder or note.

Keep the location context minimal. A model usually needs a region, selected place, or user-approved label rather than a raw full-resolution track. Store source revision and selection time with a proposal. Do not imply that a model-confirmed place proves someone visited there, that a coordinate proves an address, or that a geofence event proves a person’s intent.

## Privacy and retention

Location is sensitive personal data. The app should:

- request access only when the feature is visibly active;
- use LocationButton for a single user-initiated current-location action when that is enough;
- explain why location is needed in plain language;
- retain the smallest spatial and temporal precision that supports the feature;
- expire temporary location context after the action or user-selected retention period;
- keep raw tracks out of logs and crash payloads;
- separate raw location, derived place label, user-authored note, and AI proposal;
- provide deletion and correction paths;
- avoid using location as a covert identity or advertising signal;
- document whether network services, geocoding, maps, or remote APIs receive location.

If the app exports a photo, note, contact, or message with a location, treat the location as a separate reviewable field. A native location button does not make downstream sharing automatically private.

## Native design with Liquid Glass

Use the system location button as the recognizable authorization control. A custom Liquid Glass pill that says Use Location may look polished but does not carry the same system trust boundary and can cause the person to misunderstand what will happen.

Good composition:

~~~text
feature explanation
  -> LocationButton labeled for the real task
  -> brief progress/current-state row
  -> map or result content
  -> optional AI proposal card
  -> explicit save/share action
~~~

Glass can surround a result toolbar, filter group, or review action after the location is obtained. Do not put a decorative glass layer over a map marker, location accuracy disclosure, or error message. Keep a readable non-glass fallback for reduced transparency and high contrast.

Accessibility requirements include a visible and accessible location action, a clear explanation of approximate versus precise results, VoiceOver labels for the latest state, Dynamic Type support, no gesture-only map task, reduced motion, and alternate input for any save/share action. The location button itself is not a substitute for accessibility testing of the surrounding feature.

## Evidence boundaries

- A LocationButton preview proves only that the SwiftUI view can be constructed.
- A button action proves only that the user interacted with the route; it does not prove that authorization was granted or that a location arrived.
- A CLLocation object proves that Core Location delivered a value; it does not prove accuracy, identity, presence, or semantic place truth.
- A simulator location proves deterministic fixture routing; it does not prove GPS, Wi-Fi/cellular behavior, reduced accuracy, energy, background, or device-specific delivery.
- A map or geocoder result proves a service response, not that the user agreed with or visited the place.
- A model proposal is not a location record or an external side effect until reviewed and committed.

## Related routes

- [Location button and privacy-first map design](../21-design-deep-dives/75-location-button-and-privacy-first-map-design.md)
- [CoreLocationUI and on-device location route](../50-capability-recipes/78-corelocationui-and-on-device-location-route.md)
- [CoreLocationUI proof matrix](../60-verification/72-corelocationui-location-proof-matrix.md)
- [CoreLocationUI and LocationButton recipes](../70-code-recipes/90-corelocationui-locationbutton-recipes.md)
- [MapKit and Core Location deep dive](../41-framework-deep-dives/04-mapkit-and-location.md)

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
- [Getting the current location of a device](https://developer.apple.com/documentation/CoreLocation/getting-the-current-location-of-a-device?changes=_7)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [Human Interface Guidelines privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
