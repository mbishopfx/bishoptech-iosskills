# Proof matrix: MusicKit, ShazamKit, and AVFAudio media identity

This matrix keeps “the API is documented,” “the target is configured,” “the
route works,” and “the distributed app is ready” as separate claims. Record
the exact build, device, account, storefront, audio route, and permission
state for every runtime result.

## Evidence levels

| Level | What it proves | What it does not prove |
| --- | --- | --- |
| S0 source | The official Apple/Swift contract and availability are recorded | That the project configured or called the route correctly |
| S1 static/build | Swift snippets, target settings, usage descriptions, and availability compile or validate | Account, entitlement, hardware, network, or App Store behavior |
| S2 configuration | App ID services, bundle ID, capabilities, `Info.plist`, and signed entitlements align | That the live service or physical route works |
| S3 runtime | A specific flow succeeds or fails with expected state on a specified environment | Other devices, regions, accounts, routes, or a future build |
| S4 physical | The distributed or development build behaves on real microphone/audio hardware | App Store review acceptance or all user environments |
| S5 release | The exact archive/TestFlight/release build is inspected and exercised | A permanent guarantee against future Apple/API/service change |

Never label a simulator preview, a successful `swiftc -typecheck`, or a model
proposal as S4/S5 evidence.

## Source and availability matrix

| Claim | Source evidence | Build check | Runtime follow-up |
| --- | --- | --- | --- |
| MusicKit covers catalog, library, playback, authorization, subscription, and data requests | MusicKit documentation and installed interface | Import `MusicKit`; typecheck route snippets | Run each selected lane with a test account |
| `SHManagedSession` is available on the supported OS boundary | ShazamKit docs + SDK interface | Availability-check the selected deployment target | Verify managed session state and cancellation on device |
| `SHMatchedMediaItem.confidence` is available on its documented boundary | ShazamKit media-item docs/header | Gate the property or provide an older-OS fallback | Compare present/absent confidence UI |
| Liquid Glass APIs are available on the target | SwiftUI Liquid Glass documentation | Check deployment target and import SwiftUI | Exercise appearance/accessibility settings |
| Foundation Models is optional | Foundation Models docs | Compile the deterministic fallback without the framework | Run available/unavailable model paths on supported hardware |

## Target, App ID, and privacy configuration

| Check | Expected evidence | Failure interpretation |
| --- | --- | --- |
| Explicit App ID matches bundle identifier | Developer portal screenshot/export and Xcode target value | MusicKit or ShazamKit service may not attach to the signed app |
| MusicKit App Service enabled | App ID service configuration and signed entitlement | MusicKit catalog/playback route is not release-ready |
| ShazamKit enabled for Shazam catalog matching | App ID service configuration and signed entitlement | Shazam catalog matching may fail even if custom catalog matching works |
| MusicKit capability present in the app target | Project build settings/capability export | Xcode source alone is insufficient; inspect archive |
| `NSAppleMusicUsageDescription` present and truthful | Archive `Info.plist` plus review copy | Access can terminate or fail policy review |
| `NSMicrophoneUsageDescription` present and truthful | Archive `Info.plist` plus review copy | Microphone request is not release-ready |
| Deployment target records all newer APIs | Project settings and source availability annotations | Older devices can fail to compile, launch, or hide required actions |
| No MusicKit private key or developer secret in bundle | Archive/string scan and secret scanner | Treat as a security release blocker |

## Permission and account matrix

| Scenario | Action | Expected state/evidence |
| --- | --- | --- |
| Music permission not determined | Explain and request from a user action | System prompt appears once; route enters requesting/authorized/denied/restricted |
| Music permission denied | Return to the feature | No repeated prompt; Settings recovery and catalog-only fallback are visible |
| Music permission restricted | Request is unavailable | Route explains restriction without claiming account failure |
| Music permission authorized, no subscription capability | Query `MusicSubscription.current` | Catalog/read-only UI remains accurate; playback offers a supported next step |
| Music permission authorized, cloud library unavailable | Query capability | Library UI shows unavailable state; no silent mutation attempt |
| Music permission revoked after launch | Re-enter or refresh route | Existing cached metadata is marked stale; protected work rechecks permission |
| Microphone not determined | Explain capture and request | `AVAudioApplication` prompt appears only for listening feature |
| Microphone denied | Tap Listen again | No audio engine start; Settings recovery is reachable |
| Music account differs from local app account | Use MusicKit only for music authority | No implicit app login or identity merge occurs |

## Catalog, storefront, and library matrix

| Scenario | Expected assertion | Evidence to capture |
| --- | --- | --- |
| Catalog search | `MusicCatalogSearchRequest` returns typed results or a typed error | Term, selected types, limit, storefront/device/build, redacted response summary |
| Catalog resource lookup | Stable typed filter resolves a known item or empty result | Item ID, filter, response status, availability state |
| Storefront changes | Region-specific content and localization can differ | Storefront, language, account/device region, result IDs |
| Library read | `MusicLibraryRequest` returns only after proper access | Permission, subscription/cloud capability, request, item IDs |
| Library add | `MusicLibrary.shared.add` is called only after user action | Tap event, selected canonical item, success/error, exact build |
| `/catalog` API route | Storefront is present and developer authentication is valid | URL shape, redacted response status, server token source |
| `/me` API route | User authentication is present and data is user-scoped | Redacted endpoint, user-token source, `401`/`403` handling |
| Catalog ID versus library ID | Mapping is explicit | Both IDs where available; no string-only inference |
| Malformed or partial response | Missing artwork/artist/URL is safe | Fallback row and action availability |

## Playback matrix

| Scenario | Application player expectation | System player expectation |
| --- | --- | --- |
| Queue creation | App-local queue is visible and does not claim Music-app control | External Music state is acknowledged in copy |
| Prepare failure | Preserve selected item; show retry/subscription/availability action | Preserve selected item; show external-state recovery |
| Play success | State reports playing only after player transition | State is refreshed from the system player lane |
| Pause/stop | Controls update app-owned state | Controls reflect external player state as documented |
| Phone-call-like interruption | Pause/recover without blind auto-resume | Same, with external-state explanation |
| Route change | Test speaker, wired, Bluetooth, AirPlay where supported | Test Music app/system route behavior separately |
| Cancellation during prepare | No late play request commits | Queue remains coherent and recoverable |
| Account/subscription change | Error is distinguishable from app bug | No “playing” claim without a real state |

## ShazamKit and input matrix

| Scenario | Expected result | Required proof |
| --- | --- | --- |
| Managed session prepare | State moves from idle toward ready/listening | Physical device, permission, session state, cancellation |
| Managed session single result | `.match`, `.noMatch`, or `.error` rendered separately | Recorded result kind and build/device |
| Managed session results sequence | Results stop after `cancel()` | Cancellation timestamp and no late UI mutation |
| `SHSession` signature match | `result(from:)` returns a typed result | Signature duration, catalog kind, result kind |
| Streaming buffer | First audio format is reused for subsequent buffers | Sample rate/channels/route and tap lifecycle |
| Unsupported format | Invalid-audio-format path is visible | Input format and error code |
| Silent or discontinuous input | Invalid signature/no-match state, not a confident identity | Input test fixture and error path |
| Query too short/long | Duration validation or slicing path | Catalog min/max and slice strategy |
| Shazam catalog | App ID ShazamKit service is enabled | Signed entitlement + physical service test |
| Custom catalog | Match works without Shazam catalog service | Catalog version, reference signature source, custom result |
| Multiple matched media items | Ordered review list appears | Item IDs/order and selected user decision |
| Match confidence available | Value is shown with correct OS gate | Device OS and fallback behavior |
| No Apple Music mapping | Apple Music action disabled/hidden | No guessed ID/URL |
| Save to Shazam library | Explicit user action and confirmed async success | `SHLibrary` call result and item ID |
| Match history | Only minimum metadata retained | Data schema, deletion/retention test |

## Audio hardware and lifecycle matrix

| Test | Physical setup | Expected behavior |
| --- | --- | --- |
| Built-in microphone | iPhone built-in mic with known reference audio | Permission, capture, match, stop, tap teardown |
| Speaker playback | Device speaker plays reference audio | Match timing and playback coexistence are documented |
| Wired headset | Input/output route available | Route is detected; no stale speaker claim |
| Bluetooth input/output | Paired supported accessory | Route change state and sample format are handled |
| Route disconnected | Remove accessory during listening | Stop/recover; no crash or infinite matching |
| Interruption | Trigger a system interruption | Observe reason; do not blindly resume |
| Background/foreground | Send app to background and return | Session/player state is reconciled with scene lifecycle |
| Input mute | Toggle supported mute state | UI reports unavailable input when appropriate |
| Media services reset | Reset audio service if testable | Recreate audio resources and require a new match epoch |
| Simulator | Simulated UI/compile fixture only | Never upgrade this result to physical audio proof |

## SwiftUI and accessibility matrix

| Setting or path | Expected check |
| --- | --- |
| VoiceOver | Listen/Stop, match status, source, title, artist, confidence, and actions are ordered and labeled |
| Dynamic Type | Match and catalog rows wrap; actions remain reachable at large sizes |
| Reduce Motion | Listening and match transitions remain understandable without motion |
| Reduce Transparency/increased contrast | Glass controls and text remain legible over artwork |
| Dark/light appearance | Artwork, source labels, and error states retain contrast |
| Keyboard/Switch Control/Voice Control | All actions have stable semantic targets and focus order |
| No artwork/partial metadata | Text and action fallbacks remain useful |
| Multiple matches | Selection is accessible and does not rely on a visual ranking cue alone |

## On-device AI matrix

| Test | Expected behavior |
| --- | --- |
| Model available | Proposal is typed, bounded, source-bound, and visibly generated |
| Model unavailable | Deterministic canonical result and fallback copy remain available |
| Invalid output | Proposal is rejected without changing match/player/library state |
| Prompt injection in metadata | Metadata is treated as data; no tool/side-effect execution occurs |
| Missing source ID | Explanation is hidden or marked ungrounded; no fabricated ID |
| User accepts explanation | Only explanation text changes, not canonical identity |
| User taps Play/Add | Deterministic action path validates the item again |
| Privacy review | Raw audio, signatures, Music tokens, and unnecessary library payloads are excluded |

## Archive and distribution matrix

Before TestFlight or release, attach:

- the exact archive path, build number, and source revision;
- extracted `Info.plist` and signed entitlements;
- App ID service configuration for MusicKit and, if used, ShazamKit;
- physical-device test log with device OS, region, account, audio route, and
  permission state;
- screenshots or screen recordings of permission, search, match/no-match,
  player, error, and accessibility states;
- any server-side Apple Music API configuration with secrets redacted;
- the open issues and unsupported-route fallback list.

An archive that builds successfully is S1/S2 evidence. A TestFlight install
proves the distributed artifact can be installed and exercised in the tested
environment. It is not a guarantee of Apple approval or of behavior in every
storefront, account, accessory, or future SDK.

## Sources

- [MusicKit](https://developer.apple.com/documentation/musickit)
- [MusicAuthorization](https://developer.apple.com/documentation/musickit/musicauthorization)
- [MusicSubscription](https://developer.apple.com/documentation/musickit/musicsubscription)
- [MusicCatalogSearchRequest](https://developer.apple.com/documentation/musickit/musiccatalogsearchrequest)
- [MusicCatalogResourceRequest](https://developer.apple.com/documentation/musickit/musiccatalogresourcerequest)
- [MusicLibraryRequest](https://developer.apple.com/documentation/musickit/musiclibraryrequest)
- [MusicLibrary](https://developer.apple.com/documentation/musickit/musiclibrary)
- [ApplicationMusicPlayer](https://developer.apple.com/documentation/musickit/applicationmusicplayer)
- [SystemMusicPlayer](https://developer.apple.com/documentation/musickit/systemmusicplayer)
- [User Authentication for MusicKit](https://developer.apple.com/documentation/applemusicapi/user-authentication-for-musickit)
- [Handling Requests and Responses](https://developer.apple.com/documentation/applemusicapi/handling-requests-and-responses)
- [Storefronts and Localization](https://developer.apple.com/documentation/applemusicapi/storefronts_and_localization)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)
- [SHManagedSession](https://developer.apple.com/documentation/shazamkit/shmanagedsession)
- [SHCustomCatalog](https://developer.apple.com/documentation/shazamkit/shcustomcatalog)
- [SHSignatureGenerator](https://developer.apple.com/documentation/shazamkit/shsignaturegenerator)
- [SHMatch](https://developer.apple.com/documentation/shazamkit/shmatch)
- [SHMatchedMediaItem](https://developer.apple.com/documentation/shazamkit/shmatchedmediaitem)
- [SHLibrary](https://developer.apple.com/documentation/shazamkit/shlibrary)
- [Matching audio using the built-in microphone](https://developer.apple.com/documentation/shazamkit/matching-audio-using-the-built-in-microphone)
- [Enable ShazamKit for an App ID](https://developer.apple.com/help/account/configure-app-services/shazamkit)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [NSAppleMusicUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapplemusicusagedescription)
- [NSMicrophoneUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nsmicrophoneusagedescription)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
