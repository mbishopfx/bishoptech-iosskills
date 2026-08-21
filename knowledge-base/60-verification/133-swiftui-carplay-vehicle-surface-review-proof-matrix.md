# SwiftUI CarPlay and vehicle-surface review proof matrix

This matrix defines what each kind of evidence can establish for the [CarPlay and vehicle-surface review](../42-framework-deep-dives/108-swiftui-carplay-vehicle-surface-review.md). Use the [route card](../50-capability-recipes/139-swiftui-carplay-vehicle-surface-review-route.md) to select a route and the [recipes](../70-code-recipes/151-swiftui-carplay-vehicle-surface-review-recipes.md) for implementation sketches.

The evidence rule is:

official claim -> project/configuration proof -> compile or fixture proof -> simulator proof -> locked-phone and system proof -> physical vehicle proof -> signed distribution proof

No single artifact proves the entire route.

## Evidence levels

| Level | Evidence | Supports | Does not support |
| --- | --- | --- | --- |
| L0 | Official Apple source review | Framework, category, entitlement, template, HIG, and availability boundaries | A configured product |
| L1 | Source and project inspection | Target membership, Info.plist scene roles, entitlements intent, App Intent metadata | Developer-account approval or signed behavior |
| L2 | Compile and unit fixtures | Command validation, list limits, stale revision handling, AI fallback, scene-state reducers | Vehicle rendering, Siri, audio, map hardware, or locked-phone behavior |
| L3 | CarPlay Simulator | Scene connection, template hierarchy, list/grid/search handling, basic navigation template layout | Locked iPhone, Siri, real audio, physical controls, ambient light, or production vehicle |
| L4 | Signed iPhone plus approved head unit | CarPlay launch, locked phone, Siri, template input, real audio, appearance, privacy, accessibility | Every vehicle, every OS, App Store approval |
| L5 | Instrumented physical vehicle run | Connect/disconnect delay, keyboard/list limits, route recovery, audio interruptions, focus and hardware controls | Universal fleet coverage or future OS behavior |
| L6 | Archive and TestFlight | Bundle graph, version/build, signed entitlement, target installation, TestFlight route | Vehicle attention safety without a vehicle run |
| L7 | App Store or production observation | Distribution outcome and observed live route | A guarantee about future vehicle, account, or network state |

## Claim-to-evidence matrix

| Claim | Minimum evidence | Strong evidence |
| --- | --- | --- |
| The app is eligible for the selected category | Product decision and Apple category docs | Approved managed entitlement in developer account |
| The target has the CarPlay capability | Entitlements intent and target membership | Exported archive signed entitlements |
| CarPlay creates the intended scene | Scene manifest and delegate source | Signed install on Simulator and head unit |
| Non-navigation root template works | Scene fixture and compile | Head-unit launch with focus and disconnect recovery |
| Navigation app draws the map correctly | CPWindow/map-root source and fixture | Physical vehicle map, maneuver, alert, reroute, and dashboard run |
| Only map content is in the navigation window | Source review | Visual inspection on physical head unit |
| Template hierarchy fits limits | Fixture reads maximum counts/depth | Multiple vehicle configurations with recorded limits |
| Search works with limited keyboard | Limit fixture and fallback | Physical vehicle with keyboard restrictions |
| Audio is a good citizen | MediaPlayer unit and interruption fixture | Radio, Siri, phone-call, prompt, buffering, and resume vehicle run |
| Now Playing is correct | Shared-template source inspection | Physical audio session and Now Playing behavior |
| Communication row invokes correct Siri flow | Intent metadata and mock handler | Locked-phone compose/read/reply/call run |
| CarPlay works while iPhone is locked | Static policy and source review | Physical locked iPhone with primary task completion |
| Disconnect preserves domain state | Reducer test | Physical cable/head-unit disconnect and recovery |
| Content style adapts | Preview and trait fixture | Head-unit light/dark/ambient observation |
| Voice control is accessible | Labels and intent tests | Siri and Voice Control on intended head unit |
| Live Activity dashboard is passive | Activity fixture | Physical CarPlay dashboard observation with controls disabled |
| Watch handoff is coherent | Revisioned bridge fixture | Paired iPhone/watch plus CarPlay cross-surface run |
| App Intent is safe | Entity resolution and idempotency tests | Siri/Shortcuts/App Intent run with current data and recovery |
| Foundation Models fallback works | Availability fixture | Named device/OS run with unavailable/invalid model state |
| AI candidate is not direct truth | Validator and audit test | User-review run with stale candidate and rejection |
| Privacy redaction works | Locked/redacted snapshots | Physical shared-screen, sign-out, and account-switch run |
| Accessibility works | Labels, Dynamic Type, contrast, motion fixtures | VoiceOver/Voice Control/alternate-input head-unit run |
| Archive is releasable | Build settings and plist inspection | Signed archive plus TestFlight install |
| CarPlay release is accepted | Metadata and submission checklist | App Store review outcome and production observation |

## Configuration and artifact matrix

| Artifact | Verify | Evidence location |
| --- | --- | --- |
| iPhone target | Bundle ID, deployment target, CarPlay scene, capabilities | Project settings and built app |
| Entitlements.plist | Exact managed entitlement for selected category | Source and archive |
| Provisioning profile | Approved capability and App ID | Exported archive/profile inspection |
| CarPlay scene | Scene role, class, configuration, delegate | Built Info.plist and launch log |
| Navigation scene | CPWindow path, dashboard role if present | Built Info.plist and physical run |
| Siri or App Intent target | Capability, extension membership, metadata, supported platforms | Target settings and intent fixture |
| Widget or Live Activity target | Activity attributes, families, entitlements, signing | Archive and system-surface install |
| Watch target | Bundle relationship and revisioned bridge | Archive plus paired-device run |
| Assets | CPImageSet, light/dark, @2x/@3x, localization | Asset catalog and physical run |
| Archive | Embedded targets, signed entitlements, version/build | Xcode archive report |
| TestFlight | Install, scene discovery, capability behavior | TestFlight device record |

## Scene lifecycle matrix

| Scenario | Expected | Failure evidence |
| --- | --- | --- |
| CarPlay scene connects for first time | Delegate receives the correct connection method | No callback, missing root, or wrong scene role |
| Non-navigation root setup | Interface controller has a bounded root template | Blank surface or custom unsupported view |
| Navigation root setup | CPWindow has map-only root and interface controller has CPMapTemplate | Overlay drawn in window or missing template |
| Template push | User sees next permitted level | Silent no-op or depth violation |
| Handler begins | Row becomes pending or safe state | Duplicate side effects |
| Handler succeeds | Completion called and projection refreshed | Spinner never ends |
| Handler fails | Error is explained in CarPlay | User directed to iPhone |
| Content limit changes | Template is rebuilt within limits | Truncated or unreachable primary action |
| Content style changes | Assets and hierarchy remain legible | Low contrast or wrong asset |
| CarPlay disconnects | Scene work cancels; domain state persists | Lost draft or leaked observer |
| Reconnects | Current state rehydrates with age/revision | Stale or duplicate root |
| iPhone locked | Primary CarPlay route works | Unlock prompt for core task |

## Category matrices

### Navigation

| Test | Fixture | Physical evidence |
| --- | --- | --- |
| Location denied | Authorization reducer | Permission and safe fallback on device |
| No route | Empty state | Recent/favorite search |
| Route current | Deterministic route model | Map, maneuver, route line |
| Reroute | Revision transition | Reroute and stale alert behavior |
| Maneuver selected in background | Delegate action | Physical selection and audio/visual response |
| Navigation alert | Alert reducer | Physical alert and recovery |
| Panning | Map/template state | Physical pan/recenter controls |
| Dashboard | Scene fixture | Dashboard scene on supported head unit |
| Disconnect | Scene reducer | Resume after reconnect |
| Night/day | Trait fixture | Ambient physical vehicle observation |

### Audio and communication

| Test | Audio | Communication |
| --- | --- | --- |
| Primary surface | List and Now Playing | Conversation/contact list |
| Voice entry | INPlayMediaIntent | INStartCallIntent or messaging intent |
| Locked iPhone | Playback path | Read/compose/reply privacy path |
| Interruption | Radio, call, Siri, prompt | Call/message interruption |
| Failure | Buffer/account/network | Recipient/account/network |
| Duplicate action | Queue idempotency | Message/call idempotency |
| Privacy | Artwork/metadata policy | Contact/message redaction |

### Place and order

| Test | Expected |
| --- | --- |
| Category entitlement | Only approved templates are used |
| Current place | Location and service data have age |
| Availability changes | Revalidation before selection |
| Price/order changes | Explicit review before commit |
| Payment/account requirement | Safe handoff or defer |
| Cancellation | Domain state distinguishes canceled and pending |
| Vehicle disconnect | Draft remains recoverable on iPhone |

## Vehicle and attention matrix

| Scenario | Required observation |
| --- | --- |
| Head unit connected | Scene and root template appear |
| Head unit disconnected | No false connected state; domain is preserved |
| iPhone locked | Primary category task works without unlock |
| Vehicle moving | Long or unsafe tasks are limited or deferred |
| Keyboard limited | Voice/favorite/recent fallback is usable |
| List limited | Primary rows remain visible |
| Daylight | Contrast and route emphasis remain legible |
| Night | Brightness and motion do not distract |
| Knob/touch pad | Focus and selection are predictable |
| Touch | Primary targets are clear |
| Siri | Voice path resolves, confirms, commits, and speaks accurately |
| Audio overlap | Radio, prompt, Siri, call, and app audio coexist |
| Passenger privacy | Sensitive content is minimized |
| Error | Recovery is available in CarPlay |

## AI and App Intent matrix

| Case | Required result |
| --- | --- |
| Model ready | Candidate is structured and source-labeled |
| Model unavailable | Deterministic route remains usable |
| Candidate has unknown ID | Reject before presentation or commit |
| Candidate is stale | Re-resolve and request a new choice |
| User rejects | No domain mutation |
| User confirms | Domain command returns committed revision |
| Duplicate invocation | Same idempotent result or safe conflict |
| Unauthorized entity | No private data or mutation |
| Intent cancellation | Pending state is recoverable |
| Model context too broad | Reduce context and record policy |
| Live Activity projection | Committed passive state only |
| Watch projection | Revisioned result, not raw prompt data |

## Privacy and accessibility matrix

| Review | Required checks |
| --- | --- |
| Locked iPhone | Core task does not require unlock; private detail is controlled |
| Shared vehicle | Message, contact, account, location, and order data are minimized |
| Sign-out | CarPlay projection is cleared or marked unavailable |
| Account switch | Old identifiers cannot resolve in the new scope |
| Uninstall/reinstall | Old pending data is quarantined or migrated intentionally |
| VoiceOver | Labels, order, state, and disabled reason are spoken |
| Voice Control | Commands are distinct and discoverable |
| Dynamic Type | Long labels retain meaning |
| Contrast | Light/dark and ambient variants remain legible |
| Reduce Motion | Nonessential motion is removed |
| Reduce Transparency | iPhone review shell retains hierarchy |
| Alternate input | Focus and selection do not depend on touch |
| Localization | Long, plural, and right-to-left strings are tested |

## AI proposal audit record

Record at minimum:

- model availability state and reason;
- device and OS context;
- model or prompt revision;
- source record identifiers and revisions;
- candidate identifiers and structured fields;
- deterministic validation result;
- user choice;
- committed domain revision;
- template or system surface shown;
- fallback path if no proposal was used.

Do not store raw message bodies, credentials, or broad location histories merely because they were available to the model.

## Release proof matrix

| Stage | Required evidence |
| --- | --- |
| Source | Official CarPlay, HIG, Siri/App Intent, Liquid Glass, accessibility, and release docs |
| Project | Category, entitlement, scene manifest, target membership, privacy strings |
| Compile | Correct SDK symbols, tests, fixture reducers, no unsupported target assumptions |
| Simulator | Root template, hierarchy, limits, basic interaction, layout |
| Physical | Locked iPhone, Siri, audio, head unit, map, focus, privacy, accessibility |
| Archive | Version/build, target graph, signed entitlements, assets, extensions |
| TestFlight | Install and scene behavior on intended device |
| App Store | Metadata, CarPlay category review, policy, submission outcome |
| Production | Observed route, crash/metric logs, user support signals |

## Sources

- [CarPlay](https://developer.apple.com/documentation/carplay)
- [Requesting CarPlay entitlements](https://developer.apple.com/documentation/carplay/requesting-carplay-entitlements)
- [Displaying content in CarPlay](https://developer.apple.com/documentation/carplay/displaying-content-in-carplay)
- [Using the CarPlay Simulator](https://developer.apple.com/documentation/carplay/using-the-carplay-simulator)
- [CPTemplateApplicationSceneDelegate](https://developer.apple.com/documentation/carplay/cptemplateapplicationscenedelegate)
- [CPTemplateApplicationDashboardSceneDelegate](https://developer.apple.com/documentation/carplay/cptemplateapplicationdashboardscenedelegate)
- [CPInterfaceController](https://developer.apple.com/documentation/carplay/cpinterfacecontroller)
- [CPListTemplate](https://developer.apple.com/documentation/carplay/cplisttemplate)
- [CPMapTemplate](https://developer.apple.com/documentation/carplay/cpmaptemplate)
- [CPNowPlayingTemplate](https://developer.apple.com/documentation/carplay/cpnowplayingtemplate)
- [CPMessageListItem](https://developer.apple.com/documentation/carplay/cpmessagelistitem)
- [CPSessionConfiguration](https://developer.apple.com/documentation/carplay/cpsessionconfiguration)
- [CarPlay HIG](https://developer.apple.com/design/human-interface-guidelines/carplay)
- [Live Activities HIG](https://developer.apple.com/design/human-interface-guidelines/live-activities)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [Configuring Siri support](https://developer.apple.com/documentation/xcode/configuring-siri-support)
- [Resolving and handling intents](https://developer.apple.com/documentation/sirikit/resolving-and-handling-intents)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
