# CoreLocationUI and on-device location route

Use this route when a feature needs a person’s current location for one intentional action: center a map, find a nearby place, attach a place to a note, prepare a location share, or provide a coarse context to an on-device model.

The default route is:

~~~text
feature explanation
  -> SwiftUI LocationButton or UIKit CLLocationButton
  -> temporary authorization
  -> one bounded Core Location request
  -> accuracy/service/result state
  -> optional MapKit/geocoder/AI proposal
  -> user review
  -> app-owned record or explicit share
~~~

If the feature needs continuous movement, background delivery, geofencing, visits, or shared location response, branch into a separate Core Location route. Do not quietly turn a one-time button into a tracking session.

## Route selection

| Outcome | Start here | Keep separate |
| --- | --- | --- |
| Show the current position once | LocationButton plus current-location service | Map marker, stale result, and user dismissal. |
| Find nearby places | LocationButton -> current location -> MapKit search | Provider result, user-selected place, and model ranking. |
| Attach a place to a journal entry | LocationButton -> coarse/precise location -> reverse geocode | User-authored label, raw coordinate, and retention policy. |
| Share a current location | LocationButton with Share Current Location title | Message/share composition and recipient review. |
| Track a workout or route | Core Location service selected for continuous movement | HealthKit/WorkoutKit, background, energy, and watch routes. |
| React to a boundary | Region/condition monitoring | Background delivery, notification, and user intent. |
| Offer a background location feature | Documented background service/session or location push extension | Entitlement, usage disclosure, provider/server, and physical-device proof. |

## Phase 1: make the data request legible

Before the system control appears, show why the feature needs location. Keep the explanation short and local to the action. The person should understand whether the result is:

- a single current point;
- an approximate region;
- a nearby search context;
- a value that will be saved;
- a value that will be shared.

Use the native LocationButton title that matches the consequence. Do not put a generic “Enable GPS” action in an onboarding flow and hope the person remembers why they granted access.

## Phase 2: authorize and fetch

The button grants one-time access; the app must still request a location through Core Location. After the action:

1. observe authorization state;
2. check reduced versus full accuracy;
3. start only the selected service;
4. wait for a current result or a documented failure;
5. stop or cancel as soon as the one-time task is satisfied;
6. publish a state that includes timestamp, accuracy context, and source.

Do not call a location result current merely because it is the newest value in memory. Check its timestamp and the task’s freshness requirement. If the app has only a stale last-known value, label it as stale and ask whether the person wants to use it.

## State model

Use typed state rather than several independent Booleans:

| State | Meaning | UI |
| --- | --- | --- |
| needsUserAction | No request has started | LocationButton and feature explanation. |
| requestingAuthorization | System permission flow is active | Keep the page stable and do not start duplicate work. |
| waitingForLocation | Access is sufficient; no current value yet | Progress plus cancel/retry where appropriate. |
| approximateLocation | A value arrived with reduced accuracy | Show coarse context and precision consequence. |
| currentLocation | Fresh value meets the task’s threshold | Map/result/review action. |
| staleLocation | A value exists but is older than the task allows | Ask for refresh or manual input. |
| denied | User denied or global services are off | Settings guidance and manual fallback. |
| restricted | Device/account policy prevents access | Explain limitation without retry loops. |
| unavailable | Service cannot provide a result | Retry or use manual search. |
| cancelled | The person or lifecycle ended the task | Return to idle without an error alert. |

Every proposal or saved record should include the source revision and selection time. If the person changes the selected place or starts a second request, invalidate older proposals.

## Phase 3: minimize the AI context

The AI handoff should be a separate, user-started step:

~~~text
accepted current or selected place
  -> coarse place/category/context
  -> local model proposal
  -> source and uncertainty disclosure
  -> edit or accept
~~~

Prefer a region, selected place identifier, or user-entered category when it is enough. Avoid passing a full coordinate history, nearby-home inference, or unrelated location metadata. Keep the model route on device when possible, but do not turn “on device” into a claim that the output is correct.

Useful proposals:

- “Add this place to the trip journal”;
- “Show nearby coffee shops that are open” after an explicit search;
- “Suggest a label for this selected place”;
- “Summarize the places selected in this day’s note.”

Unsafe or overconfident routes:

- infer a person’s identity from a coordinate;
- claim that the person visited a place because a GPS point exists;
- infer health, religion, politics, or other sensitive traits from location;
- auto-send a location or message without a reviewable system composer;
- silently retain a raw track because a model may use it later.

## Phase 4: map, geocoder, and domain record

MapKit may display a map or search for nearby content. A geocoder may produce a placemark. Treat both as external observations:

- preserve the raw location separately from the place label;
- let the person correct or choose a result;
- show when a label came from a provider or model;
- avoid writing a canonical address until the person accepts it;
- keep the provider response timestamp and source revision;
- do not use a provider’s confidence as identity proof.

The app-owned record should distinguish:

1. raw source location and accuracy;
2. user-approved place or region;
3. provider-derived label;
4. model-generated suggestion;
5. user-authored text;
6. sharing or retention decision.

## Phase 5: stop, expire, or continue

For a one-time action, stop location work after the result is accepted, canceled, or timed out. Clear temporary location context when the feature ends unless the person saved it. If the product needs background or continuous delivery, document the new route separately:

- user-visible reason and usage description;
- appropriate authorization level;
- background indicator/session or service configuration;
- energy and update policy;
- privacy retention and deletion;
- notification or system-surface behavior;
- physical-device and signed artifact evidence.

Do not keep a CLLocationManager alive in a singleton merely to avoid a future permission path.

## Fallbacks

When location is unavailable:

- allow manual place search;
- accept a typed city or region;
- let the person select a map point if the feature supports it;
- offer a saved place without treating it as current;
- explain that approximate data may be sufficient;
- let the person retry without repeating unnecessary prompts.

When the model is unavailable:

- keep the location and map task usable;
- show deterministic nearby search or manual labeling;
- preserve the accepted source without inventing a summary.

When location is denied:

- do not loop the button or present a fake success state;
- offer settings guidance only when useful;
- avoid shaming language;
- allow the feature to continue with manual input if possible.

## Target and privacy checklist

- Link CoreLocationUI and Core Location in the correct app target.
- Add only the required usage description keys for the selected authorization route.
- Confirm the current deployment target and platform behavior in Xcode.
- Keep a MapKit/geocoder route separate from the location permission boundary.
- Do not assume Mac Catalyst or visionOS accepts LocationButton input.
- If background delivery exists, configure its target capabilities and evidence separately.
- Keep raw coordinates, derived labels, proposals, and logs under separate retention policies.
- Describe external geocoding, search, network, or share destinations in the privacy review.

## Evidence boundary

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| SwiftUI Preview | Layout and label composition | Permission, location delivery, or system trust behavior. |
| Unit test | State transitions and stale/fresh policy | Hardware, GPS, reduced accuracy, or Settings state. |
| Simulator fixture | Deterministic map/location UI | Physical radio behavior, energy, background, or real permission prompts. |
| Signed device run | Button interaction, authorization, accuracy, and live result on that device | Every device, OS, geography, or external provider. |
| Map/geocoder result | A provider response was returned | User presence, identity, or canonical address truth. |
| AI proposal | Model route produced a bounded suggestion | Semantic truth, user consent, or external side-effect completion. |
| Share/system surface | The selected build presented the handoff | Recipient receipt or later delivery. |

See the [CoreLocationUI proof matrix](../60-verification/72-corelocationui-location-proof-matrix.md) before marking a route complete.

## Related routes

- [CoreLocationUI and least-privilege location access](../42-framework-deep-dives/55-corelocationui-and-least-privilege-location.md)
- [Location Button and privacy-first map design](../21-design-deep-dives/75-location-button-and-privacy-first-map-design.md)
- [CoreLocationUI and LocationButton recipes](../70-code-recipes/90-corelocationui-locationbutton-recipes.md)
- [MapKit and Core Location route](../41-framework-deep-dives/04-mapkit-and-location.md)

## Sources

- [CoreLocationUI](https://developer.apple.com/documentation/corelocationui)
- [LocationButton](https://developer.apple.com/documentation/corelocationui/locationbutton)
- [CLLocationButton](https://developer.apple.com/documentation/corelocationui/cllocationbutton)
- [Core Location](https://developer.apple.com/documentation/CoreLocation)
- [CLLocationManager](https://developer.apple.com/documentation/corelocation/cllocationmanager)
- [CLLocationUpdate](https://developer.apple.com/documentation/corelocation/cllocationupdate)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/CoreLocation/requesting-authorization-to-use-location-services?changes=_7)
- [Getting the current location of a device](https://developer.apple.com/documentation/CoreLocation/getting-the-current-location-of-a-device?changes=_7)
- [Adopting live updates in Core Location](https://developer.apple.com/documentation/corelocation/adopting-live-updates-in-core-location?changes=lat_5)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Human Interface Guidelines privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
