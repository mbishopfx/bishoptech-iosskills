# MapKit Advanced Composition Proof Matrix

## Evidence ladder

MapKit features cross UI, service data, optional location permission, and physical interaction. Use the smallest evidence that proves each claim, and do not let a map preview or a successful search stand in for a different boundary.

| Evidence level | Can prove | Cannot prove |
| --- | --- | --- |
| Source/API review | Current API meaning, documented availability, initializer shape, and framework boundary | The selected target compiles or the service returns data in a region. |
| Deterministic fixture | Camera/selection mapping, normalized model rules, stale-generation rejection, AI schema validation, and UI state rendering | Map service availability, real imagery, location hardware, or physical interaction. |
| Named-target compile | Imports, deployment availability, target membership, and API signatures in the selected project | Runtime service data, permissions, Look Around coverage, map performance, or system handoff. |
| Simulator/UI test | Navigation, search/selection state, camera commands, route review, accessibility identifiers, and failure branches with fakes | Real location authorization, map imagery/service coverage, touch feel, memory/thermal behavior, or release configuration. |
| Physical device | Map interaction, permissions, service behavior, location accuracy states, Look Around availability, memory/thermal behavior, and assistive technology tasks | Universal coverage, every supported device, App Store delivery, or server/provider reliability. |
| Signed/release artifact | Target membership, entitlements, privacy resources, extension/system configuration, and distribution-specific behavior | A guarantee of production service availability or universal user experience. |

## Claim matrix

| Claim | Fixture/compile evidence | Runtime evidence | Required rejection boundary |
| --- | --- | --- | --- |
| The map renders the intended app content | App-owned place fixture with stable IDs and empty/loading/error states; named-target `Map` compile | Device run across standard/satellite/dark/light and supported size classes | A screenshot does not prove selection identity, accessibility, or device performance. |
| Fixed map browsing does not require location | Denied/restricted Core Location fixture; map target has no location-dependent branch | UI run with location denied and a physical permission-reset run | A map centered on a cached coordinate must not be called current location. |
| Camera commands are deterministic | `MapCameraPosition` region/rect/item/camera fixtures; bounds tests | Physical pan/zoom/rotate/pitch and deliberate fit/recenter actions | A requested position does not prove the user saw or accepted the camera result. |
| User positioning is respected | `positionedByUser` state fixture and command suppression tests | Manual map movement followed by app updates, recenter action, and state restoration | A camera callback is not permission to override user intent. |
| Bounds protect a real task area | `MapCameraBounds` region/distance fixtures and invalid bounds handling | Physical exploration at edges, zoom limits, rotation/pitch, and accessibility path | Bounds must not be used to disguise missing content or trap exploration. |
| MapReader conversion is correct | Coordinate/CGPoint fixtures, missing conversion, session-generation rejection | Touch/pointer/keyboard selection on device at multiple zooms/orientations | A coordinate is not a resolved address, business, or person location. |
| App-tagged selection is correct | `MapSelection` and stable tag fixtures, deleted/duplicate ID cases | Tap, VoiceOver, pointer, and alternate-input selection with detail handoff | Selection is not persistence or authorization to mutate data. |
| Apple map-feature selection is handled safely | `MapFeature` category/title/coordinate mapping and unknown-field fixtures | Physical tap/selection across POI and physical feature types | A feature does not prove ownership, opening status, safety, or identity. |
| Viewport POI search matches the displayed region | Region/camera generation fixtures, category filter tests, cancellation tests | Pan/debounce/service/no-network run on device | A viewport is not the user’s current location. |
| Text search matches the query | Completer/search adapter fixtures, query/region/fetched-at mapping, no-result/error tests | Type-ahead cancellation, confirmed search, locale/network variation | A suggestion is not a confirmed search or saved place. |
| Search results can become a saved place | Explicit selection/review fixture with provenance and stable app ID | User correction, save, edit, delete, and relaunch on device | A returned `MKMapItem` must not be persisted as canonical truth automatically. |
| Look Around preview is honest | Scene available/no-scene/cancelled/failed fixtures and selected-place retention | Supported and unsupported/no-imagery places on physical target; viewer open/close | A scene is imagery, not proof the place is current, open, safe, or accessible. |
| Directions represent confirmed inputs | Source/destination/transport fixtures, alternatives, stale route, cancellation, and error tests | Physical service run with changed inputs, transport, recalculation, and detail review | A route/ETA is not navigation completion or a guarantee about roads. |
| Route overlay matches route state | `MKRoute`/polyline normalization and empty/invalid geometry fixtures | MapPolyline rendering with light/dark/satellite/reduced-effects and device interaction | A visual line is not a legal boundary, safe path, or persisted trip. |
| AI place proposal is source-linked | Codable/schema fixtures, unknown/duplicate/stale ID rejection, unsupported claim rejection | Edit/approve/discard/regenerate flow with model unavailable and source changes | Generated coordinates, labels, or route actions never become truth without validation and approval. |
| AI context is minimized | Redaction fixtures for precise coordinates, search history, raw notes, and unrelated places | Privacy review of context, logs, analytics, retention, and deletion on device | “On device” does not remove the need for minimization or user-facing policy. |
| Glass control shell is native and adaptive | State fixtures for loading/empty/selected/error/reduced effects; target compile | Physical light/dark, contrast, transparency, Dynamic Type, RTL, motion, and map-style runs | A screenshot cannot prove legibility, focus, touch, or accessibility. |
| Accessibility task is complete | Semantic labels/values/actions and alternate list/detail fixture | VoiceOver, Voice Control, Switch Control, keyboard, pointer, and physical focus task | An accessibility audit or label alone does not prove reading order or ergonomics. |
| Localization is usable | Long strings, RTL, pluralized distance/time, locale and coordinate-format fixtures | Device locale, Dynamic Type, map labels, search, detail, and route runs | English-only screenshots do not prove localization. |
| Map service errors are recoverable | Offline/no-result/denied/restricted/cancelled/stale fixtures | Network transitions, service failure, retry, and persistence on device | A spinner or empty map must not hide whether data is missing or unavailable. |
| Performance is acceptable | Deterministic content-size and route complexity fixtures; metrics plan | Representative device frame/memory/thermal/energy observation in Release | A simulator or newest device does not prove all target tiers. |
| Release route is configured | Named target compile, entitlements/privacy/Info.plist/target membership inspection | Signed artifact and intended system handoff/provider/account route | A development build or local preview does not prove distribution readiness. |

## State fixtures

At minimum, render and test:

```text
fixed map / no permission
loading saved places
empty saved places
searching text
suggestions with query change
search results with fetched-at
viewport results with stale generation
selected app place
selected Apple map feature
coordinate draft without place match
Look Around loading
Look Around unavailable
directions calculating
route alternatives
route stale after input change
AI proposal pending review
AI proposal rejected for unknown ID
AI proposal accepted after edit
permission denied / reduced accuracy / services disabled
offline / service failure / retry
Dynamic Type / RTL / reduced motion / reduced transparency / high contrast
signed-release configuration mismatch
```

Each fixture should identify the map session, camera/region generation, source IDs, locale, appearance, Dynamic Type size, and whether data is deterministic or service-backed.

## Test-plan separation

Keep the following test groups distinct:

- **Map domain tests:** normalization, stable IDs, coordinate validation, source/provenance, route policy, AI proposal validation, privacy redaction.
- **SwiftUI/UI tests:** map shell state, search/selection/detail, camera commands, route review, Look Around launch, accessibility identifiers, deep links, and cancellation behavior with controlled adapters.
- **Service/device tests:** MapKit search/directions/Look Around, map rendering, location permission/accuracy, touch/pointer/pitch/rotation, memory/thermal, and assistive technology tasks on named physical devices.
- **Release/system tests:** signed target, privacy resources, location strings, system handoff, provider/account/service configuration, and App Store/TestFlight evidence where the product depends on it.

Do not place a service-backed MapKit run in the deterministic test suite and call it stable. Do not use a deterministic mock to claim that Look Around imagery or directions are available in production.

## Recording template

```text
Feature:
Target / bundle ID / deployment target / SDK:
Device / OS / locale / appearance / Dynamic Type:
Map route: fixed | search | viewport POI | feature | Look Around | directions | location
Permission and accuracy state:
Map session / camera generation:
Source IDs and provenance:
Fixture or service request:
Expected camera/selection/detail state:
Observed service/error/cancellation state:
AI model/context/version (if used):
Accessibility task and alternate input:
Performance/memory/thermal notes:
Signed/release artifact and entitlements:
Evidence files/screenshots/result bundle:
Known limitation:
```

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
- [MKMapItem](https://developer.apple.com/documentation/mapkit/mkmapitem)
- [MKDirections](https://developer.apple.com/documentation/mapkit/mkdirections)
- [MKRoute](https://developer.apple.com/documentation/mapkit/mkroute)
- [MKLookAroundSceneRequest](https://developer.apple.com/documentation/mapkit/mklookaroundscenerequest)
- [LookAroundPreview](https://developer.apple.com/documentation/mapkit/lookaroundpreview)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
