# SwiftUI App Clips, invocation, and full-app handoff review

This review adds a modern SwiftUI architecture boundary around App Clips, App Clip Experiences, invocation URLs, App Clip Codes, QR/NFC/Safari/Messages/Maps/Location entry, NSUserActivity scene delivery, ephemeral versus shared data, lightweight payment and account flows, full-app replacement, App Store overlays, local AI, Liquid Glass, and release proof. It complements the existing [watch, CarPlay, and App Clip overview](../43-system-framework-deep-dives/04-watch-carplay-and-app-clips.md), [Universal Links and Handoff review](72-universal-links-handoff-and-scene-delivery.md), [App Clip recipes](../70-code-recipes/20-watch-carplay-appclips-and-communications-recipes.md), and [system-surface checklist](../60-verification/05-system-surface-checklist.md).

It is not an App Store Connect setup guide, a size report, a server association service, a sign-in provider, or proof that an App Clip launches from every physical or digital invocation. App Clips are a separate target, a separate signed artifact, and a deliberately constrained product surface.

## The App Clip route has multiple authorities

Name the authority for every fact:

| Fact or outcome | Primary authority | App-owned projection | Proof boundary |
| --- | --- | --- | --- |
| A person needs a focused in-the-moment task | Product and App Clip design | Task route | Deterministic task fixture |
| An invocation is eligible | App Store Connect experience, domain association, and system | Invocation context | Physical/digital invocation run |
| The App Clip receives a URL | NSUserActivity and SwiftUI lifecycle | Parsed invocation context | App Clip/full-app scene run |
| The URL is missing | System lifecycle state | Restored App Clip state | Notification/App Switcher return run |
| The card copy and image are shown | App Store Connect and system card | No in-app replacement | Device card run |
| The target is eligible to install | Signed App Clip target and on-demand entitlement | Build configuration | Archive inspection |
| The App Clip is small enough | Xcode archive and App Store distribution rules | Size report | App thinning report |
| Data survives full-app installation | Shared container, CloudKit, keychain, or Sign in with Apple | Migration record | App Clip-to-full-app run |
| A payment is authorized | Apple Pay system sheet and provider | Payment status | Physical system/provider run |
| The full app is recommended | StoreKit overlay | Install suggestion state | App Clip scene run |
| A model suggested a next step | Foundation Models or another local model | Reviewable proposal | Device/model/source fixture |

Keep the lifecycle separate:

~~~text
invocation source
    -> App Clip Experience matching
    -> App Clip card
    -> App Clip target launch
    -> invocation URL or no-URL restore
    -> focused task
    -> optional payment/account/data migration
    -> task completion
    -> optional full-app recommendation
    -> full app replaces App Clip
    -> same invocation routing and migrated state
~~~

An invocation URL, App Clip card, local preview, URL parser, shared-container file, Apple Pay sheet, StoreKit overlay, model proposal, or simulator run does not alone prove installation, durable account identity, payment fulfillment, data migration, or release behavior.

## Choose an App Clip only for a focused task

App Clips are for a fast real-world task or a focused demo. Use a task worksheet:

| Question | Good App Clip answer | Bad answer |
| --- | --- | --- |
| What does the person need now? | Unlock this bike, order this item, start this short demo | Explore the entire product |
| How many essential screens? | A linear path with minimal entry | Full tab bar and settings hierarchy |
| Can the task finish without the full app? | Yes | No, install is a prerequisite |
| Is the value available with limited account setup? | Anonymous or Sign in with Apple | Long registration form |
| Can the binary launch quickly? | Small, self-contained resources | Large model and media download |
| Is the route native? | SwiftUI/UIKit system components | Embedded website as the core UI |
| Is the App Clip more than marketing? | It completes a useful task or demo | It only advertises the full app |

Apple’s App Clip HIG recommends a linear, focused interface, immediate launch, essential features, and no requirement to install the full app to complete the task. Do not treat an App Clip as a miniature copy of the entire app.

## Target graph and signed artifacts

An App Clip requires a corresponding full app. In Xcode, the App Clip target has its own scheme and identifier, is embedded in the full app’s app bundle, and uses the On Demand Install Capable entitlement. The archive must contain the correct parent/full-app and App Clip identity relationships.

Inspect:

- full app target and App Clip target;
- separate bundle identifiers and application identifiers;
- On Demand Install Capable entitlement;
- Parent Application Identifiers entitlement;
- associated App Clip app identifiers on the full app;
- Associated Domains entitlement when a website invocation or advanced experience requires it;
- App Groups if data or Background Assets cross the targets;
- App Clip-specific Info.plist keys such as NSAppClip;
- supported devices and platform;
- shared Swift package/module boundaries;
- duplicate assets and target membership;
- size report from a thinned archive;
- App Store Connect default, advanced, demo, and tester experiences;
- archive version/build and full-app/App Clip release relationship.

A source file shared by both targets is not proof that the two signed products have the same entitlements, resources, size, or runtime behavior.

## Size and runtime availability gates

The current App Clip documentation describes different size rules depending on OS and experience:

| Route condition | Documentation boundary | Product implication |
| --- | --- | --- |
| Older supported OS | Smaller legacy uncompressed limit | Keep the target minimal |
| iOS 17 and later digital-only experience | Up to the larger limit when requirements are met | Verify digital invocation, reliable network, and OS support |
| Physical App Clip Code, QR, or NFC | Physical invocation constraints apply | Do not assume the larger limit is available |
| Demo link | App Store Connect demo conditions can support the larger experience | Confirm demo link and invocation policy |
| Any route | Device variant size is measured after thinning | Inspect the exported size report |

For an iOS 26 target, do not memorize a number from a prior SDK. Verify the current App Clip documentation, invocation sources, deployment target, App Store Connect experience type, and thinned archive. The route’s real gate is the signed distribution artifact, not the debug product size.

App Clips can use SwiftUI and UIKit, but Apple documents many frameworks as providing no runtime functionality inside an App Clip, including App Intents, Background Tasks, CallKit, Contacts, EventKit, HealthKit, HomeKit, Messages, Nearby Interaction, PhotoKit, ResearchKit, SensorKit, Speech, and others. Confirm every framework against the current [Choosing the right functionality for your App Clip](https://developer.apple.com/documentation/appclip/choosing-the-right-functionality-for-your-app-clip) page.

Important design consequence: an App Clip cannot rely on App Intents runtime behavior merely because the full app uses App Intents. Use the invocation URL and the App Clip lifecycle for the Clip, then use App Intents in the full app where the target and runtime support them.

## Invocation sources and App Clip Experiences

Supported invocations can include:

- App Clip Code;
- NFC tag;
- QR code;
- Smart App Banner or App Clip card in Safari;
- SFSafariViewController;
- link shared in Messages;
- Maps link or location-based Siri Suggestion;
- email or website link;
- App Clip link or preview from another app;
- Spotlight or a prior App Clip entry, depending on the experience.

The system matches an invocation URL against App Store Connect configuration, selects the default or most-specific advanced App Clip Experience, creates the card, and passes the invocation context to the Clip. A website invocation may pass the site URL. A Maps or location route may use the registered experience URL. A demo link has different parameter and physical-invocation behavior than a default or advanced experience.

Use generic URL prefixes deliberately. Apple documents prefix matching for advanced experiences. A generic registered URL must also be handled safely by both the App Clip and full app, even if real physical links use longer paths.

The App Clip card is configured outside the SwiftUI view. Its title, subtitle, call-to-action, header image, localization, and experience association are App Store Connect artifacts. Current documentation describes short card copy limits; verify exact current limits in the target release before shipping.

Do not programmatically change card copy at runtime. Use the invocation context to update the App Clip UI after the card has launched.

## Invocation delivery through NSUserActivity

When an App Clip is invoked, the system makes the invocation URL available through an NSUserActivity of type NSUserActivityTypeBrowsingWeb. In SwiftUI, use the onContinueUserActivity lifecycle modifier. In a scene-based or UIKit lifecycle, use the scene connection/user-activity callbacks documented by Apple.

Model the route:

~~~text
NSUserActivity
    -> verify activity type
    -> read webpageURL
    -> validate scheme/host/path/query
    -> map to AppClipInvocation
    -> update app-owned state
    -> render the focused task
~~~

The URL can be absent. Apple documents that an App Clip resumed from a notification or App Switcher can launch without an invocation URL. Save enough app-owned state before suspension to restore the last task safely.

Do not derive an account, payment amount, location identity, or permission decision from arbitrary query parameters. Treat the URL as an invocation hint and resolve trusted data from the app’s domain or server.

## A typed invocation model

Use a shared parser in the App Clip and full app:

~~~text
AppClipInvocation
    source: physical | safari | messages | maps | location | other
    host: allowlisted host
    path: allowlisted path
    parameters: allowlisted values
    experience: default | advanced | demo | unknown
    receivedAt:
    sourceRevision:
~~~

The full app must handle the same invocation URLs after installation because it replaces the App Clip and receives future invocations. Share the parser and route contract, not the entire App Clip UI or every dependency.

For missing or invalid input:

- restore the last safe Clip task if it is current;
- show a generic entry state when no task is available;
- do not show a blank screen or a crash;
- do not treat a malformed path as a trusted location or order;
- preserve unsaved data before switching invocation contexts;
- record a redacted diagnostic with the target and invocation source.

## Data transition to the full app

When the full app is installed, the App Clip is replaced and all future invocations launch the full app. A smooth handoff can use:

| Data or identity | Route | Boundary |
| --- | --- | --- |
| Public catalog/menu data | CloudKit public database | App Clip can read documented public data; verify write/private restrictions |
| Small app-owned draft | Shared App Group container or shared UserDefaults | Corresponding full app only; no secrets in defaults |
| Sensitive short-lived credential | Keychain with matching entitlements | App Clip/full-app direction and OS-version caveats |
| Account continuity | Sign in with Apple | Credential state and server account reconciliation |
| Downloaded asset | Shared container or Background Assets | Size, group, availability, and integrity |
| Server order/task | Server record plus opaque ID | Authenticate and re-fetch current truth |

The App Clip can only share its data with its corresponding app. Do not treat an App Group as a general sharing channel with unrelated apps. Do not put passwords or raw secrets in shared defaults or a general shared file.

For CloudKit, current App Clip guidance describes public-database access with constraints, including an anonymous iCloud service entitlement and restrictions on writing or using private/shared containers. Verify the current CloudKit route before choosing it for user-owned data.

The migration protocol should be idempotent:

~~~text
App Clip writes migration envelope
    -> full app launches
    -> full app validates envelope schema and age
    -> full app checks account/server identity
    -> full app imports once
    -> full app marks envelope consumed
    -> Clip state is retained or removed according to policy
~~~

An imported file or shared UserDefaults value is not proof that a server account has accepted the state.

## Account, payment, and entitlement boundaries

App Clips should avoid account creation when the task can finish without one. When an account is necessary, keep it narrow and consider Sign in with Apple. Reuse only a privacy-preserving identifier or credential flow supported by the target, then revalidate account state on the server.

Apple Pay is a natural App Clip route for a physical good or service because it reduces typing. Keep the Apple Pay system-sheet/provider/fulfillment boundary from the [commerce review](104-swiftui-passkit-wallet-apple-pay-commerce-review.md). A successful Apple Pay authorization does not prove order fulfillment.

In-App Purchases are a full-app concern for the documented App Clip use cases. Do not use an App Clip to bypass StoreKit rules for digital content. If a Clip needs a physical service, use the correct real-world payment route and verify App Review and provider requirements.

Do not claim that an App Clip’s local account, Apple Pay sheet, or shared identifier is a full-app entitlement. The full app must re-resolve server ownership and current product state.

## Notifications, location, and Background Assets

App Clips can request temporary notification capability for a limited period, documented as up to eight hours after each launch when NSAppClipRequestEphemeralUserNotification is enabled. This route is not normal full-app notification authorization. Test the App Clip card, permission/settings state, notification return without an invocation URL, and full-app replacement.

An App Clip can request location confirmation through the App Clip activation payload and documented location route. Confirm location at the time of invocation with the minimum data and consent needed. Do not store a precise coordinate as proof that a person intended to use a specific physical location.

Background Assets can deliver additional content, but the in-the-moment App Clip should keep required assets in the Clip and avoid making launch depend on a download. A demo App Clip may use Background Assets when network conditions and size policy justify it. Model availability, integrity, cancellation, and a no-download fallback.

## App Store overlay and full-app recommendation

Recommend the corresponding full app at a natural pause, after the Clip has delivered value. In SwiftUI, Apple documents appStoreOverlay with an SKOverlay.AppClipConfiguration. The App Clip may recommend only its corresponding full app through this App Clip configuration.

Do not require installation to finish the task. Do not show the overlay repeatedly or during a critical flow. Explain what the full app adds: saved history, richer settings, more locations, or ongoing account features. The overlay is a StoreKit system surface; its appearance or dismissal is not an install receipt.

## App Intents and full-app system discoverability

App Intents can make full-app actions discoverable by Siri, Spotlight, Shortcuts, widgets, and Apple Intelligence. The current App Clip functionality guidance says App Intents provide no runtime functionality in App Clips. Therefore:

- use the invocation URL and NSUserActivity route inside the App Clip;
- define App Intents in the full app only when that target supports runtime behavior;
- make the full-app intent re-resolve the same invocation or domain record;
- do not expose an App Clip action through a full-app App Shortcut before the full app can satisfy the same current-state contract;
- keep App Clip and full-app route parsers shared where possible.

This is a target boundary, not a visual decision.

## On-device AI in an App Clip

An App Clip may be a poor place for a model-heavy experience. Foundation Models availability depends on Apple Intelligence, device, region, and model readiness. Even when the framework is available to the target, the product must preserve the Clip’s instant, focused behavior.

Use local AI only for a bounded proposal:

~~~text
invocation context + trusted public record
    -> availability check
    -> small structured proposal
    -> source and revision validation
    -> user review
    -> deterministic task route
~~~

Do not use a model to:

- parse an untrusted invocation URL into a trusted payment or location;
- invent a business menu, price, account, or entitlement;
- require a download before the Clip can complete its task;
- create an account or submit a payment without explicit user interaction;
- persist sensitive data in a shared container;
- substitute for unavailable App Intents runtime;
- claim the full app will receive a model session or memory;
- make the App Clip larger or slower without a measured benefit.

If the model is unavailable, provide a deterministic path. Record model availability and source revision only if the product has a real reviewable proposal.

## Native SwiftUI and Liquid Glass

Apple’s App Clip HIG favors native components, a linear focused interface, minimal screens, and no web view as the core experience. Build:

- one task-oriented navigation path;
- an invocation-aware opening screen;
- system controls for payment, sign-in, location, and app installation;
- a small amount of app-owned status context;
- a clear completion state;
- a full-app recommendation only at a natural pause.

Liquid Glass should come from standard SwiftUI controls and navigation wherever possible. If a custom glass effect is used, limit it to the primary action or a compact status group, keep it readable over the task content, and test reduced transparency, reduced motion, large text, and contrast.

Do not create a fake App Clip card, fake Apple Pay sheet, fake system install overlay, or fake notification banner. Those surfaces have system-owned lifecycle and trust semantics.

## Proof-first completion

An App Clip route is complete only when:

- the App Clip and full-app targets have matching route contracts and correct signed relationships;
- the invocation URL is configured in App Store Connect and the domain association is proven when required;
- XCAppClipURL is used for deterministic local URL debugging;
- a local experience tests the card and launch flow on a physical device;
- each intended source is tested: App Clip Code/QR/NFC, Safari, Messages, Maps/location, prior Clip, and full-app replacement as applicable;
- missing URL, malformed URL, generic prefix, and stale invocation cases are handled;
- the thinned archive size report is inspected for each device variant;
- App Clip framework/runtime restrictions are checked against the current docs;
- shared data and account migration are verified with matching entitlements and idempotent import;
- Apple Pay/provider/fulfillment evidence is separate if payment is used;
- temporary notifications, location confirmation, and Background Assets are tested only when needed;
- the App Store overlay is shown only after value and its result is not treated as an install receipt;
- AI availability and fallback are measured on a supported physical device;
- VoiceOver, Dynamic Type, contrast, Reduce Motion, reduced transparency, keyboard, pointer, and switch input complete the task;
- the full signed app archive, TestFlight experience, App Clip bundle, App Store Connect configuration, and release diagnostics are recorded.

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
- [Offering Live Activities with your App Clip](https://developer.apple.com/documentation/appclip/offering-live-activities-with-your-app-clip)
- [Confirming a person’s physical location](https://developer.apple.com/documentation/appclip/confirming-a-person-s-physical-location)
- [Launching another app’s App Clip from your app](https://developer.apple.com/documentation/appclip/launching-another-app-s-app-clip-from-your-app)
- [Encoding a URL in an App Clip Code](https://developer.apple.com/documentation/appclip/encoding-a-url-in-an-app-clip-code)
- [NSAppClip](https://developer.apple.com/documentation/bundleresources/information-property-list/nsappclip)
- [APActivationPayload](https://developer.apple.com/documentation/appclip/apactivationpayload)
- [UIScene.ConnectionOptions](https://developer.apple.com/documentation/uikit/uiscene/connectionoptions)
- [StoreKit SKOverlay](https://developer.apple.com/documentation/storekit/skoverlay)
- [SKOverlay.AppClipConfiguration](https://developer.apple.com/documentation/storekit/skoverlay/appclipconfiguration)
- [SwiftUI appStoreOverlay](https://developer.apple.com/documentation/swiftui/view/appstoreoverlay%28ispresented%3Aconfiguration%3A%29)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [App Clips HIG](https://developer.apple.com/design/human-interface-guidelines/app-clips)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
