# SwiftUI MapKit, location, and place-exploration proof matrix

## Purpose

Use this matrix for claims involving MapKit for SwiftUI, MapCameraPosition,
MapReader/MapProxy, map content/selection/features/overlays, Core Location
permission and accuracy, search, Look Around, directions, WeatherKit,
Liquid Glass map controls, on-device AI place proposals, accessibility,
performance, or system/release handoff.

Record for every run:

- app/build, Xcode, SDK, deployment target, target membership, platform, and
  MapKit/WeatherKit entitlements;
- map session ID, camera generation, requested camera command, positionedByUser
  state, visible region, bounds, map style, pitch/heading, and content IDs;
- source kind, place IDs, framework IDs, coordinate precision, query, region,
  fetched-at, locale, provider/service result, and stale generation;
- Core Location authorization, accuracy authorization, services state, update
  owner, current route, and stop policy;
- search/completer/POI request, debounce, cancellation, no-result/error state;
- Look Around request/scene state and selected place identity;
- direction inputs, transport type, calculation time, alternatives, selected
  route, stale state, and handoff destination;
- WeatherKit dataset, requested location/date, availability, attribution, and
  stale state;
- AI model/capability state, allowed source IDs/fields, proposal ID, source
  generation, validation, review action, and commit result;
- locale, RTL, Dynamic Type, appearance, map style, reduced motion/transparency,
  contrast, VoiceOver, Voice Control, Switch Control, keyboard, pointer, and
  touch/pitch/rotation input;
- physical device/OS/build, artifact path, test date, tester, and whether
  evidence is static, simulated, service-backed, or live.

A map screenshot does not prove a selected place, current location, service
availability, accessibility task, route correctness, weather freshness, AI
grounding, or release readiness.

## Evidence levels

| Level | Can support | Cannot support alone |
| --- | --- | --- |
| Official source | API intent and platform guidance | This app's runtime behavior |
| Static route review | Identity, permissions, state, privacy, destinations | Map/service/physical behavior |
| Named-target compile | API signatures, availability, target membership | Location permission, service coverage, ergonomics |
| Unit/fixture test | IDs, generations, coordinate validation, proposal schema | Real map data, rendering, user interaction |
| Preview | Map shell states, camera commands, detail hierarchy | Map tiles, service calls, physical gestures |
| UI test | Search/detail/selection/labels with adapters | Actual location, Look Around, directions, weather |
| Simulator | Layout, localization, keyboard, simulated location fixtures | Physical motion, service/device performance, privacy prompt feel |
| Signed physical target | Map rendering, location, search/service, accessibility, input | Every OS/region/device and distribution |
| System-service run | Location prompts, Look Around, share/handoff, WeatherKit | Universal freshness or route safety |
| Performance run | Frame/memory/thermal/response evidence | Correctness of every place/service |
| Archive inspection | Entitlements, location strings, target/resources, signing | A completed map task |
| TestFlight/release smoke | Signed target and selected physical routes | Production health or all regions |

## Fixture contract

~~~swift
struct MapProofFixture: Hashable, Sendable {
    let target: String
    let mapSessionID: String
    let cameraGeneration: Int
    let cameraState: String
    let contentIDs: [String]
    let sourceKind: String
    let query: String?
    let regionDescription: String?
    let locationAuthorization: String
    let accuracyAuthorization: String
    let searchState: String
    let lookAroundState: String
    let directionsState: String
    let weatherState: String
    let aiState: String
    let destinationState: String
    let localeIdentifier: String
    let layoutDirection: String
    let dynamicType: String
    let accessibilityModes: [String]
}
~~~

Minimum fixture families:

- fixed app map, empty/loading/error, duplicate/deleted content, selected and
  unselected content;
- automatic, region, rect, item, camera, user-location fallback, positioned
  by user, fit/recenter/show-place, invalid bounds, and user-pan suppression;
- coordinate draft valid/invalid/no conversion, changed camera generation,
  reverse-geocode no result, approximate result, review, save, discard;
- query empty/typing/suggestion/confirmed/no-result/offline/cancelled/stale;
- viewport POI results with region generation, filter, no coverage, and
  out-of-order responses;
- map feature categories/unknown/title/coordinate/discovery/review;
- Look Around loading/ready/no imagery/cancelled/failed;
- directions source/destination/transport/alternatives/calculating/stale/
  cancelled/failed/confirmed;
- location undetermined/when-in-use/denied/restricted/precise/reduced/
  services-disabled/changed-in-Settings;
- WeatherKit current/hourly/daily/alerts/availability/stale/attribution/error;
- AI proposal ready/edit/reject/unknown ID/invented coordinate/stale/unavailable;
- iPhone/iPad/Catalyst/visionOS/watchOS/CarPlay, RTL, Dynamic Type, reduced
  effects, VoiceOver, keyboard, pointer, and high contrast.

## Map rendering and camera matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Map renders app content | Named-target compile plus deterministic fixture | Empty/loading/error, invalid coordinate | Markers/annotations match stable app IDs |
| Fixed map works without location | Permission-denied fixture plus UI run | No location authorization | Browse/search/detail remain useful |
| Camera command frames content | Unit/camera fixture plus UI run | Empty/single/many, invalid bounds | Fit/show/recenter produces intended state |
| User positioning is respected | State/reducer test plus physical run | Pan/zoom then data refresh | App does not snap back unexpectedly |
| Camera generation scopes work | Async/unit test | Late search/weather/AI result | Old generation cannot mutate current map |
| Bounds protect real task area | Geometry fixture plus physical run | Edge zoom/rotation/pitch | Bounds are legible and not a hidden trap |
| Map style is intentional | Visual fixture plus physical run | Standard/satellite/dark/light | Controls/content remain legible |
| Rotation/pitch are usable | Physical input/accessibility run | Reduced motion, pointer, keyboard | Alternative list/detail route exists |
| Map state restores safely | Lifecycle/UI run | Background, scene loss, relaunch | Restore does not override new user intent |

## Content, selection, and coordinate matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| App content identity is stable | Unit/persistence fixture | Rename, duplicate, delete, relaunch | ID survives projection/reopen |
| Marker/annotation semantics are correct | Static/UI/accessibility review | Custom content, long title | Map and detail communicate same item |
| Overlay meaning is explicit | Static/visual fixture | Polyline/polygon/circle, no geometry | Copy does not imply legal/safety truth |
| App selection works | UI/physical/accessibility run | Tap, VoiceOver, pointer, deleted item | Detail opens for current ID |
| MapFeature selection is bounded | Fixture/physical run | POI/physical feature/unknown | Feature remains discovery until review |
| MapReader conversion is correct | Coordinate fixture plus device run | Zoom/orientation/pointer/touch | Coordinate matches gesture within expected tolerance |
| Coordinate draft is provisional | UI/integration test | No place match, move pin, cancel | Save/reverse geocode requires confirmation |
| Coordinates are privacy-scoped | Static/privacy/integration review | Analytics/logs/export | Precision/retention match product policy |

## Location permission and update matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Location purpose string is present | Processed plist/archive | Wrong target/configuration | Built app contains truthful copy |
| Request happens on intent | Physical/system run | Launch without location feature | No surprise prompt |
| Denied state is useful | Physical run | Denied, restricted, services off | Search/fixed map fallback works |
| Accuracy is represented | Physical run | Precise/reduced, Settings change | Copy/actions do not imply precision |
| Updates are owned and bounded | Static/instrumented run | View redraw, route close | One owner starts/stops updates |
| Current location is not fallback | State/visual fixture | Fallback camera, no location | UI does not claim current position |
| User-location camera follows intentionally | Physical run | Follow heading/location, manual pan | Recenter/follow behavior is explicit |
| Background policy is correct | Physical lifecycle run | Home/lock/scene inactive | Updates stop/continue only by supported policy |
| Precise location is not logged | Instrumented release/privacy run | Errors/analytics | Logs omit or redact precise coordinates |

## Search, Look Around, and directions matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Suggestions are distinct from results | UI/adapter test | Query changes, cancel | No result is saved from typing alone |
| Confirmed search uses query/region | Fixture/integration test | Empty/no-result/offline | Result records request provenance |
| Viewport POI search is scoped | Generation/fixture/UI test | Pan/debounce/filter | Results match displayed region |
| Stale result is blocked | Async test | Out-of-order completion | Old query/region cannot replace new list |
| Map item is normalized | Unit/integration test | Missing title/invalid coordinate | App model has stable/source fields |
| Look Around no imagery works | Fixture/system run | Loading/cancel/error | Selected place remains reviewable |
| Look Around is labeled imagery | Static/accessibility review | No scene, full viewer | UI does not imply current/open/safe place |
| Directions use confirmed inputs | Unit/fixture/UI run | Source/destination/transport edits | Calculation inputs visible |
| Route alternatives are reviewable | Physical/system run | Cancel, stale, changed input | Person chooses or discards route |
| Route is not navigation proof | Static/product review | Deep link/system handoff | No silent navigation or safety promise |

## Weather context matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Weather request is tied to place/time | Unit/integration fixture | Re-selected place, stale date | Response stores coordinate/place/date |
| Dataset is explicit | Named-target compile/run | Current/hourly/daily/minute/alerts | UI matches requested dataset |
| Availability is handled | Service/device run | No data, error, offline | Fallback copy is clear |
| Attribution is present | UI/static/release review | Detail/sheet/compact surface | Required attribution remains visible |
| Weather is not permanent place truth | Static/UI review | Saved place, cached response | Date/freshness is shown |
| AI receives bounded weather | Adapter fixture | Stale/partial/unavailable | Proposal does not invent live conditions |

## AI proposal matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Capability is optional | Availability fixture/device run | Unsupported/disabled model | Map/search/detail remains useful |
| Context uses known sources | Static adapter plus fixture | Unknown ID, duplicate, invented coordinate | Only supplied place/route fields are used |
| Proposal has map generation | Unit request/response test | Camera/search changes | Candidate becomes stale |
| Weather/location privacy is bounded | Redaction/security test | Precise history, unrelated places | Scope and retention are documented |
| Candidate is typed/validated | Schema/fixture tests | Long text, unsupported claim, bad action | Invalid output cannot reach Apply |
| User review is distinct | Physical/accessibility run | Edit/accept/discard/regenerate | Proposal is not system/map fact |
| Commit uses normal path | Integration test | Save/export/handoff failure | AI cannot mutate domain/system directly |

## Liquid Glass and accessibility matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Glass group has task meaning | Design review/preview | Full-map decorative glass | Group can be named and removed |
| Map remains primary | Light/dark/satellite physical run | Busy imagery, selection | Controls do not obscure content |
| Reduced transparency works | Physical settings run | Opaque fallback, contrast | State/actions remain legible |
| Camera controls are semantic | UI/accessibility run | User-positioned/permission denied | Labels/value explain action |
| Map has list/detail alternative | UI/accessibility fixture | No map data, VoiceOver | Task completes without map pixels |
| Dynamic Type/localization works | Physical/UI run | Long place names, RTL | No clipping or lost actions |
| Keyboard/pointer works | iPad/Catalyst physical run | Search/select/recenter/detail | Core task completes without touch |
| Focus is stable | VoiceOver/UI run | Camera updates, selection, sheet close | Focus does not jump continuously |

## Performance, targets, and release matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Map is responsive | Release physical performance run | Many annotations, overlays, selection | Frame/memory observations recorded |
| Search is cancellable | Physical/service run | Rapid query/pan, network changes | No request accumulation |
| Location is energy-bounded | Physical run | Long updates, background, accuracy | Update policy/energy evidence |
| iPhone route works | Signed physical iPhone run | Permission, map styles, touch | Device/OS/build artifact named |
| iPadOS route works | Signed physical iPad run | Split view, pointer, keyboard | Target-specific evidence |
| Catalyst route works | Named-target compile/Mac run | Menus, file/search, unsupported APIs | Fallbacks honest |
| Look Around/directions/weather release works | TestFlight/system run | Region/service coverage, attribution | Distributed build result recorded |
| Archive is configured | Archive inspection | Wrong target/configuration | Entitlements/privacy/resources correct |

## Required artifact set

Keep:

1. deterministic map/camera/selection/search/location/weather/AI fixtures;
2. named-target compile and availability output;
3. preview/UI captures for state hierarchy and accessibility labels;
4. physical iPhone/iPad evidence for map interaction, permission, accuracy,
   services, search, Look Around, routes, weather, and assistive technology;
5. performance/thermal/memory observation on representative devices;
6. archive/TestFlight evidence for entitlements, strings, target membership,
   service configuration, attribution, and system handoff;
7. a list of regions/targets/services not verified.

## Sources

- [MapKit for SwiftUI](https://developer.apple.com/documentation/mapkit/mapkit-for-swiftui)
- [Map](https://developer.apple.com/documentation/mapkit/map)
- [MapCameraPosition](https://developer.apple.com/documentation/mapkit/mapcameraposition)
- [MapCamera](https://developer.apple.com/documentation/mapkit/mapcamera)
- [MapCameraBounds](https://developer.apple.com/documentation/mapkit/mapcamerabounds)
- [MapReader](https://developer.apple.com/documentation/mapkit/mapreader)
- [MapProxy](https://developer.apple.com/documentation/mapkit/mapproxy)
- [MapSelection](https://developer.apple.com/documentation/mapkit/mapselection)
- [MapSelectable](https://developer.apple.com/documentation/mapkit/mapselectable)
- [MapFeature](https://developer.apple.com/documentation/mapkit/mapfeature)
- [MapPolyline](https://developer.apple.com/documentation/mapkit/mappolyline)
- [MapPolygon](https://developer.apple.com/documentation/mapkit/mappolygon)
- [MapCircle](https://developer.apple.com/documentation/mapkit/mapcircle)
- [MKLocalSearch](https://developer.apple.com/documentation/mapkit/mklocalsearch)
- [MKLocalSearchCompleter](https://developer.apple.com/documentation/mapkit/mklocalsearchcompleter)
- [MKLocalPointsOfInterestRequest](https://developer.apple.com/documentation/mapkit/mklocalpointsofinterestrequest)
- [MKPointOfInterestFilter](https://developer.apple.com/documentation/mapkit/mkpointofinterestfilter)
- [MKMapItem](https://developer.apple.com/documentation/mapkit/mkmapitem)
- [MKDirections](https://developer.apple.com/documentation/mapkit/mkdirections)
- [MKRoute](https://developer.apple.com/documentation/mapkit/mkroute)
- [MKLookAroundSceneRequest](https://developer.apple.com/documentation/mapkit/mklookaroundscenerequest)
- [LookAroundPreview](https://developer.apple.com/documentation/mapkit/lookaroundpreview)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [CLLocationManager](https://developer.apple.com/documentation/corelocation/cllocationmanager)
- [CLAuthorizationStatus](https://developer.apple.com/documentation/corelocation/clauthorizationstatus)
- [CLLocationUpdate](https://developer.apple.com/documentation/corelocation/cllocationupdate)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/corelocation/requesting-authorization-to-use-location-services)
- [Adopting live updates in Core Location](https://developer.apple.com/documentation/corelocation/adopting-live-updates-in-core-location)
- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [WeatherService](https://developer.apple.com/documentation/weatherkit/weatherservice)
- [CurrentWeather](https://developer.apple.com/documentation/weatherkit/currentweather)
- [Weather](https://developer.apple.com/documentation/weatherkit/weather)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
