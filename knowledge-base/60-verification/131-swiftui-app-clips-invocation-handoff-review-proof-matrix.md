# SwiftUI App Clips, invocation, and full-app handoff review proof matrix

Use this matrix to separate App Clip task design, signed target configuration, App Store Connect experience matching, invocation URL delivery, physical context, temporary state, account/payment, full-app migration, StoreKit overlay, App Intents boundaries, local AI, Liquid Glass, accessibility, and release behavior.

Read it with the [App Clip review](../42-framework-deep-dives/106-swiftui-app-clips-invocation-handoff-review.md), [design guide](../21-design-deep-dives/134-swiftui-app-clips-invocation-handoff-review-design.md), [route](../50-capability-recipes/137-swiftui-app-clips-invocation-handoff-review-route.md), and [recipes](../70-code-recipes/149-swiftui-app-clips-invocation-handoff-review-recipes.md).

## Evidence levels

| Level | Evidence | What it can establish |
| --- | --- | --- |
| L0 | Current Apple documentation, HIG, and target availability review | Documented App Clip contract |
| L1 | Full-app/App Clip target graph, entitlements, Info.plist, domain, App Store Connect configuration | Configuration for the named release |
| L2 | Invocation URL, parser, migration, size, and task fixtures | App-owned deterministic behavior |
| L3 | Simulator, local experience, local URL environment, mocked account/provider, or preview | Partial development behavior |
| L4 | Signed physical device with local experience and real system surfaces | Device launch, card, URL, location, NFC/QR, payment, and handoff behavior for the tested case |
| L5 | TestFlight/App Store Connect experience, archive, App Clip diagnostics, provider/account environment | Distribution and environment behavior |
| L6 | Repeated physical-source, migration, privacy, accessibility, recovery, and release evidence | Readiness for a named claim |

A URL in source is not an App Clip Experience. A local experience is not App Store release configuration. A shared file is not an account migration. A full-app overlay is not an install receipt.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| App Clip is appropriate | Task worksheet and HIG review | A miniature full-app UI |
| App Clip target exists | Xcode target and signed on-demand entitlement | A source folder |
| Parent/full-app relationship is correct | Signed archive entitlements and identifiers | Matching bundle names |
| Binary fits size rule | Thinned archive size report for variants | Debug build size |
| Invocation URL is configured | App Store Connect experience and domain evidence | A URL constant |
| Card is correct | Physical local/released card run | SwiftUI preview |
| QR/App Clip Code works | Physical scan and selected experience | URL parser unit test |
| NFC works | Physical tag and device run | NFC payload fixture |
| Safari/website works | Associated domain, Smart Banner/card, physical run | Website link |
| Messages works | Shared message and recipient device run | Sending a link to self |
| Maps/location works | Advanced experience/place association and device run | Coordinates in a fixture |
| Invocation reaches the Clip | App Clip card and launch run | App Clip target launch from Xcode |
| URL is parsed safely | Allowlist tests and physical input | URLComponents construction |
| Missing URL recovers | Notification/App Switcher/prior state run | Default URL fallback |
| Full app receives the same invocation | Installed full app with universal link/invocation run | Shared parser code |
| Task completes without install | Clean-device task run | Install overlay screenshot |
| Shared state migrates | App Group/keychain/CloudKit/Sign in with Apple run | File exists in a simulator |
| Server truth continues | Re-fetch/reconciliation and idempotent import | Local draft |
| Apple Pay works | Physical system sheet and provider environment | Payment request object |
| Fulfillment works | Provider/order event | Apple Pay authorization |
| Temporary notifications work | App Clip declaration, card/settings, physical return | Full-app notification proof |
| Location is confirmed | Activation payload and device/location run | Hard-coded coordinate |
| App Store overlay is valid | App Clip configuration and user result | Overlay appears |
| App Intents route is valid | Full-app target system invocation | App Intent source in Clip target |
| AI proposal is safe | Model availability, source/revision, review, deterministic validation | Model text |
| Liquid Glass is appropriate | Standard controls and reduced-effects run | Glass screenshot |
| Task is accessible | VoiceOver/Dynamic Type/contrast/reduced effects/alternate input | Accessibility labels |
| Release is ready | Signed archive, TestFlight/App Store, diagnostics, device run | Debug/App Clip simulator |

## Target and artifact packet

Record:

~~~text
Full app target:
App Clip target:
Full bundle identifier:
App Clip bundle identifier:
SDK/toolchain:
Deployment target:
OS build:
Device model:
Device family:
On Demand Install Capable:
Parent Application Identifiers:
Associated App Clip identifiers:
Associated Domains:
App Groups:
NSAppClip:
App Clip extensions:
Frameworks:
App Clip size report:
App Store Connect app version:
Default experience:
Advanced experiences:
Demo experience:
Tester experience:
Invocation domains:
Archive version/build:
TestFlight/release build:
~~~

Compare project settings, signed archive entitlements, and the installed build. A source-level capability is not artifact proof.

## Invocation matrix

| Source | Setup | Expected result | Failure to test |
| --- | --- | --- | --- |
| App Clip Code | Encoded physical URL | Card and task context | Wrong code or unsupported device |
| QR code | URL and physical print | Card and task context | Damaged/ambiguous scan |
| NFC | Tag and activation configuration | Card and context | Wrong tag, no NFC, denial |
| Safari Smart Banner | Website association | Card from website | Missing AASA/association |
| Safari card | Published experience | Correct card/URL | Cached old experience |
| Messages | Shared website link | Recipient sees launch path | Sender/recipient mismatch |
| Maps | Advanced place association | Location context | No place match |
| Siri location | Location suggestion | Registered context | Permission/no suggestion |
| Email/site | Associated link | Digital launch | Unsupported URL |
| Another app | App Clip link/preview | Link/handoff | Source app behavior |
| Prior Clip | Cached local state | Restore or neutral entry | Missing URL |
| Notification | Temporary notification return | Restore without URL | Stale Clip state |
| Full app installed | Same invocation | Full app opens same task | Clip-only route |

Record the exact URL, source, card metadata, target bundle, OS/device, and whether the URL was present.

## URL and context validation matrix

| Fixture | Expected result | Evidence |
| --- | --- | --- |
| Allowlisted HTTPS host/path | Route resolves | Unit and device |
| Generic registered prefix | Safe generic route | Device |
| Unknown host | Reject or neutral entry | Unit |
| Unknown path | Reject or neutral entry | Unit |
| Oversized query | Reject | Unit |
| Duplicate query key | Deterministic handling | Unit |
| Missing parameter | Prompt or safe default | Device |
| Untrusted price/location/account parameter | Never trusted | Unit/provider |
| URL from Messages | Current server record | Physical |
| URL from Maps/location | Physical context check | Physical |
| No URL | Restore bounded local state | Physical |
| Old URL after server change | Current record or stale state | Server/device |

## Size and launch matrix

| Claim | Evidence | Boundary |
| --- | --- | --- |
| Size meets current limit | App Thinning Size Report | Per-variant size |
| Required assets are local | Clean-device launch without download | Network condition |
| Background Assets are optional | Offline/slow-network run | Download failure |
| Launch is fast enough | Cold launch measurement | Device/region variance |
| Card is readable | Physical card run | Localized copy/image |
| Experience matches | App Store Connect and device run | Cache/old experience |
| Full app replacement works | Full app install and invocation | Installed state |

Use a clean test device and clear App Clip Experience Cache when testing a new experience.

## Task completion matrix

| Claim | Run | Required result |
| --- | --- | --- |
| Context appears immediately | Physical invocation | Correct task without extra selection |
| Task works anonymously | Clean device | No unnecessary account |
| Sign in works | Sign in with Apple/device account | Server identity reconciled |
| Payment works | Apple Pay physical/provider sandbox | Authorization and provider state separate |
| Order/task fulfills | Provider/server event | Durable current state |
| Failure recovers | Timeout/denial/offline | Clear retry or in-app fallback |
| Full-app install is optional | Complete task without install | No hidden gate |
| Full-app suggestion is polite | Completion pause | Dismissible overlay |
| Future invocation works | Full app installed | Same route in full app |

## Data migration matrix

| Data path | Configuration | Proof | Does not prove it |
| --- | --- | --- | --- |
| Shared App Group file | Matching group in both targets | Clip writes, full app reads | Server account |
| Shared UserDefaults | Matching group and schema | Value migration and cleanup | Secret safety |
| Keychain | Access groups/entitlements | Clip/full-app credential state | All OS versions |
| Sign in with Apple | Apple ID credential and server | Full-app credential state | Local user ID alone |
| CloudKit public database | App Clip entitlement and public read | Current public data | Private/shared writes |
| Background Assets | App group and delivery config | Asset integrity/availability | Instant launch |
| Server record ID | Re-fetch and idempotent import | Current server truth | Draft file |

Test:

- missing envelope;
- old schema;
- duplicate import;
- wrong corresponding app;
- wrong account;
- expired credential;
- corrupted file;
- user signs out;
- full app installed after task completion;
- App Clip removed before full app launch.

## Payment and account matrix

| Claim | Evidence | Boundary |
| --- | --- | --- |
| Apple Pay target is ready | Signed Merchant IDs/certificate/provider setup | Source request |
| Payment sheet is correct | Physical system run and amount comparison | Screenshot |
| Provider accepted | Sandbox/provider response | Apple Pay callback |
| Fulfillment occurred | Server/order event | Provider authorization |
| Digital entitlement is valid | Full-app StoreKit transaction | App Clip local state |
| Sign-in is current | Credential state and server session | Stored user ID |
| Location matches | Documented location confirmation run | Query coordinate |

Never place merchant, payment-processing, or server private keys in either target.

## Temporary notifications and location matrix

| Feature | Setup | Proof |
| --- | --- | --- |
| Ephemeral notification declaration | NSAppClip Info.plist key | App Clip card and settings |
| Temporary local schedule | Physical Clip and trigger | Device delivery |
| Temporary remote notification | Push capability/provider/device | Provider and device run |
| Return from notification | Notification tap | No-URL restore |
| Location confirmation | App Clip activation payload and permission | Physical location run |
| Denied location | Denial path | Neutral task |
| Wrong location | Mismatch path | No false confirmation |

Do not promote temporary notification or location evidence to full-app capability evidence.

## App Store overlay matrix

| Claim | Evidence | Does not prove it |
| --- | --- | --- |
| Correct app is recommended | AppClipConfiguration and matching product | Generic app overlay |
| Overlay timing is appropriate | Task completion pause | First-screen prompt |
| Task remains complete without install | Clean run | Overlay only |
| Dismissal is safe | Dismiss run | Overlay presentation |
| Install result is known | Full-app launch/StoreKit result if available | Overlay appearance |

## App Intents and AI matrix

| Claim | Evidence | Boundary |
| --- | --- | --- |
| Full app action is discoverable | Full-app App Intent/App Shortcut system run | App Clip runtime |
| Clip invocation works | NSUserActivity/URL physical run | App Intent declaration |
| Model is available | SystemLanguageModel state on device | Simulator assumption |
| Proposal is grounded | Source IDs/revision and prompt/schema record | Generated text |
| Proposal is safe | Allowlist for route/price/location/actions | Model confidence |
| User decides | Review/edit/confirm run | Automatic action |
| Fallback works | Model unavailable path | AI-only UX |

## Native design and accessibility matrix

| Claim | Evidence | Does not prove it |
| --- | --- | --- |
| Flow is focused | Task-level screen audit | Smaller full app |
| System surfaces are native | Apple Pay, overlay, location, card runs | Custom imitation |
| Glass is restrained | Standard controls plus one functional effect | Screenshot |
| Large text works | Device Dynamic Type task | Default size |
| VoiceOver works | Complete task | Labels only |
| Reduced effects work | Reduced transparency/motion run | Default visual |
| Alternate input works | Keyboard/pointer/Switch Control | Touch-only run |
| Privacy works | Lock/shared-screen review | Unlocked preview |

## Release packet

Collect:

- documentation/source and availability notes;
- target graph, entitlements, Info.plist, App Groups, and domain association;
- thinned App Clip size reports;
- App Store Connect default/advanced/demo/tester experience records;
- local experience and physical invocation captures;
- missing URL/full-app replacement evidence;
- migration, account, payment, provider, and location evidence;
- overlay result;
- AI availability and fallback;
- accessibility task result;
- signed archive, TestFlight, App Store release, and App Clip diagnostics;
- known unsupported devices, invocation sources, network conditions, and recovery states.

## Release decision

| Decision | Minimum evidence |
| --- | --- |
| Documentation-ready | L0 route and source review |
| UI prototype-ready | L2 task, URL, and migration fixtures |
| Physical-ready | L4 card, invocation, task, and accessibility runs |
| TestFlight-ready | L5 archive, size, experience, and tester run |
| App Store-ready | Released configuration diagnostics and full-app replacement |
| Production-ready | L6 repeated source, migration, privacy, recovery, and operational evidence |

## Sources

- [App Clips](https://developer.apple.com/documentation/appclip)
- [Choosing the right functionality for your App Clip](https://developer.apple.com/documentation/appclip/choosing-the-right-functionality-for-your-app-clip)
- [Creating an App Clip with Xcode](https://developer.apple.com/documentation/appclip/creating-an-app-clip-with-xcode)
- [Configuring App Clip experiences](https://developer.apple.com/documentation/appclip/configuring-the-launch-experience-of-your-app-clip)
- [Responding to invocations](https://developer.apple.com/documentation/AppClip/responding-to-invocations)
- [Testing the launch experience of your App Clip](https://developer.apple.com/documentation/AppClip/testing-the-launch-experience-of-your-app-clip)
- [Distributing your App Clip](https://developer.apple.com/documentation/appclip/distributing-your-app-clip)
- [Sharing data between your App Clip and your full app](https://developer.apple.com/documentation/appclip/sharing-data-between-your-app-clip-and-your-full-app)
- [Recommending your app to App Clip users](https://developer.apple.com/documentation/appclip/recommending-your-app-to-app-clip-users)
- [Enabling notifications in App Clips](https://developer.apple.com/documentation/appclip/enabling-notifications-in-app-clips)
- [Confirming a person’s physical location](https://developer.apple.com/documentation/appclip/confirming-a-person-s-physical-location)
- [NSAppClip](https://developer.apple.com/documentation/bundleresources/information-property-list/nsappclip)
- [APActivationPayload](https://developer.apple.com/documentation/appclip/apactivationpayload)
- [UIScene.ConnectionOptions](https://developer.apple.com/documentation/uikit/uiscene/connectionoptions)
- [StoreKit SKOverlay](https://developer.apple.com/documentation/storekit/skoverlay)
- [SwiftUI appStoreOverlay](https://developer.apple.com/documentation/swiftui/view/appstoreoverlay%28ispresented%3Aconfiguration%3A%29)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [App Clips HIG](https://developer.apple.com/design/human-interface-guidelines/app-clips)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
