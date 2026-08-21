# SwiftUI App Clips, invocation, and full-app handoff review route

Use this route to decide whether a lightweight task belongs in an App Clip and how it should move from invocation to a full app. Read the [App Clip review](../42-framework-deep-dives/106-swiftui-app-clips-invocation-handoff-review.md), [design guide](../21-design-deep-dives/134-swiftui-app-clips-invocation-handoff-review-design.md), [proof matrix](../60-verification/131-swiftui-app-clips-invocation-handoff-review-proof-matrix.md), and [recipes](../70-code-recipes/149-swiftui-app-clips-invocation-handoff-review-recipes.md) together.

This is a route worksheet, not proof that an App Clip is configured, small enough, associated with a domain, or available from a physical device.

## One-line selector

| Need | Route |
| --- | --- |
| A quick real-world task without installing the full app | App Clip |
| A full product dashboard or settings system | Full app |
| A trusted link that opens the relevant task | Invocation URL and NSUserActivity |
| Physical discovery | App Clip Code, QR, NFC, or advanced experience |
| Website or shared link discovery | Associated domain, Safari, Messages, or App Clip card |
| Persistent identity or rich account history | Full app and server |
| Physical checkout | App Clip plus Apple Pay/provider |
| Digital content entitlement | Full app plus StoreKit rules |
| A full-app suggestion after task completion | StoreKit App Clip overlay |
| System action discovery in the full app | App Intents/App Shortcuts |
| AI-assisted wording or choice | Optional structured proposal with review |

If the task cannot finish without a full-app install, redesign the task or do not use an App Clip.

## Route worksheet

Fill this before adding a target:

~~~text
Task:
Person context:
Completion without install:
Invocation sources:
Default experience:
Advanced experiences:
Demo experience:
Invocation domains:
URL paths and parameters:
Physical location:
Card title:
Card subtitle:
Call-to-action:
App Clip target:
Full app target:
Deployment targets:
Binary size variants:
Frameworks used:
Shared code modules:
App Groups:
CloudKit public-data route:
Keychain route:
Sign in with Apple route:
Apple Pay/provider route:
Ephemeral notification route:
Location confirmation route:
Background Assets:
App Store overlay:
App Intents/full-app route:
AI proposal:
Fallback:
Migration envelope:
Physical-device proof:
Archive/TestFlight/App Store proof:
~~~

## Gate 1: task fit

Confirm:

- the Clip has one finite outcome or demo;
- the person can understand the purpose from the card and first screen;
- no long registration is required unless it is essential;
- no full-app install is required to complete the task;
- the Clip is not only an advertisement;
- a native framework can provide the experience;
- the Clip can launch quickly with required assets included;
- the full app can provide the same task after replacement.

If the Clip needs a dashboard, multiple scenes, rich settings, persistent account history, or a large model, move that portion to the full app.

## Gate 2: target and size

Inspect:

- App Clip target and full app target;
- On Demand Install Capable entitlement;
- Parent Application Identifiers entitlement;
- associated App Clip identifiers;
- App Group and extension membership;
- platform and device family;
- App Clip-specific Info.plist;
- current App Clip binary size rules;
- archive and App Thinning Size Report;
- App Store Connect experience and link type.

Use current docs rather than a hard-coded size memory. The iOS 17-and-later larger limit has conditions involving digital invocations, network reliability, older OS support, physical invocations, and demo links.

## Gate 3: invocation design

Map every supported source:

| Source | URL/context | Proof |
| --- | --- | --- |
| App Clip Code | Short physical URL | Physical code scan |
| QR code | URL path/query | Physical scan |
| NFC | URL or activation payload | Physical tag |
| Safari website | Associated domain URL | Smart Banner/card |
| Messages | Shared website link | Sender/recipient device run |
| Maps | Registered experience URL | Maps/location run |
| Siri Suggestions location | Registered experience URL | Location permission/device run |
| Another app | App Clip link/preview | Link and handoff run |
| Prior Clip/Spotlight | Prior context or no URL | Restore run |

For each source, record whether the system delivers an invocation URL, a physical activation payload, or no URL. Do not assume all sources produce the same input.

## Gate 4: parse and validate the invocation

Use this route:

~~~text
NSUserActivity
    -> activity type is browsing web
    -> URL exists
    -> scheme is HTTPS
    -> host is allowlisted
    -> path matches a known route
    -> query keys are allowlisted and bounded
    -> server/context record is resolved
    -> AppClipInvocation becomes current
~~~

If the URL is absent:

~~~text
no invocation URL
    -> load last safe local task state
    -> verify age and account
    -> resume or show neutral entry
~~~

Do not put raw query parameters into payment, account, location, or entitlement state without server/system validation.

## Gate 5: share the route between Clip and full app

Create a small shared module:

~~~text
AppClipRouteKit
    - invocation URL parser
    - allowlisted route enum
    - migration envelope
    - redaction policy
    - route version
~~~

Keep App Clip-only UI, full-app settings, App Intents, and large dependencies outside the shared module. The full app must handle every URL that the Clip accepts, but it does not need to share the Clip’s entire implementation.

## Gate 6: task state and migration

Use an idempotent envelope:

~~~text
Clip writes:
    taskID
    sourceURLHash
    sourceRevision
    anonymousDraft
    accountHint
    createdAt

Full app reads:
    schema and age
    corresponding app identity
    account/server current state
    consumed marker
~~~

Permitted migration data depends on the technology:

- App Group file or shared UserDefaults for small non-secret handoff;
- keychain for an appropriate short-lived credential with matching entitlements;
- Sign in with Apple for account continuity;
- public CloudKit data for documented shared/public content;
- server record ID for current business truth;
- Background Assets for content that is intentionally shareable and available.

Do not migrate passwords, unbounded logs, raw model transcripts, or arbitrary external-app data.

## Gate 7: payment and sign-in

Use system surfaces:

~~~text
invocation context
    -> current item/service and price
    -> Apple Pay or minimal sign-in
    -> provider/server result
    -> task completion
~~~

Separate:

- invocation context;
- person’s current selection;
- Apple Pay authorization;
- provider acceptance;
- fulfillment;
- full-app entitlement.

For digital goods, move to the full app and StoreKit route. For physical services, use the Apple Pay/provider route only after merchant setup and fulfillment are independently proven.

## Gate 8: location and temporary notifications

Request location confirmation only when the physical context is essential and use the documented App Clip activation route. Test denial, inaccurate match, no location, and a user who is near but not at the expected place.

For temporary notifications:

~~~text
NSAppClip temporary-notification declaration
    -> App Clip card disclosure
    -> limited notification window
    -> notification return may omit invocation URL
    -> restore saved Clip state
~~~

Do not use the Clip notification route as full-app notification authorization. Do not assume a notification return includes the original URL.

## Gate 9: App Store overlay

Recommend only after the value moment:

~~~text
task completed
    -> explain full-app benefit
    -> appStoreOverlay with AppClipConfiguration
    -> user dismisses or begins install
    -> keep task result truthful
~~~

The overlay may recommend only the corresponding full app for the App Clip route. It is a system surface, not an install callback.

## Gate 10: App Intents and AI

App Intents route:

~~~text
full app action
    -> AppIntent/App Shortcut
    -> current entity/route resolution
    -> full app surface
~~~

Do not rely on App Intents runtime behavior inside the App Clip; current App Clip guidance lists it among frameworks with no runtime functionality there. Keep App Intent actions in the full app and use the shared invocation parser.

AI route:

~~~text
trusted invocation context
    -> model availability
    -> short proposal
    -> schema/category/price/location/source validation
    -> user review
    -> deterministic task
~~~

The model cannot turn a URL into an identity, grant an entitlement, choose a payment, or make the Clip larger without a measured reason.

## Gate 11: SwiftUI and Liquid Glass

Use:

- a single NavigationStack or a short state-driven flow;
- system Buttons, Forms, Lists, TextFields, and payment controls;
- invocation-aware content at launch;
- standard sheets and system overlays;
- restrained glass around a primary action or context group;
- accessible semantic labels and large-text layout.

Avoid:

- a tab bar;
- fake system cards or overlays;
- overlapping glass panels;
- loading a web view as the main route;
- a visual clone of the full app;
- a hidden model wait screen.

## Gate 12: proof packet

Collect:

- target graph and signed entitlements;
- App Store Connect experience metadata and URLs;
- invocation parser fixtures;
- local XCAppClipURL launch evidence;
- local experience card/device run;
- physical QR/NFC/App Clip Code/Safari/Messages/Maps runs as supported;
- missing-URL and full-app replacement run;
- thinned size reports;
- migration and server reconciliation evidence;
- payment/sign-in/location/temporary-notification evidence;
- StoreKit overlay result;
- AI availability and fallback;
- accessibility and reduced-effects run;
- archive, TestFlight, App Store, and App Clip diagnostics.

## Fast checklist

- [ ] The task finishes without installing the full app.
- [ ] The App Clip is useful, not only promotional.
- [ ] The invocation source and URL contract are named.
- [ ] Missing and malformed URL cases are safe.
- [ ] The full app handles every Clip URL.
- [ ] Target entitlements and App Groups are inspected in the archive.
- [ ] Size is measured after thinning.
- [ ] Shared data is minimal and corresponding-app-only.
- [ ] Payment, account, entitlement, and server truth stay separate.
- [ ] App Intents are reserved for the full-app runtime.
- [ ] AI is optional, structured, source-linked, and reviewed.
- [ ] Liquid Glass is native, sparse, and accessible.
- [ ] Physical and release evidence exists for each claimed invocation.

## Sources

- [App Clips](https://developer.apple.com/documentation/appclip)
- [Choosing the right functionality for your App Clip](https://developer.apple.com/documentation/appclip/choosing-the-right-functionality-for-your-app-clip)
- [Creating an App Clip with Xcode](https://developer.apple.com/documentation/appclip/creating-an-app-clip-with-xcode)
- [Configuring App Clip experiences](https://developer.apple.com/documentation/appclip/configuring-the-launch-experience-of-your-app-clip)
- [Responding to invocations](https://developer.apple.com/documentation/AppClip/responding-to-invocations)
- [Testing the launch experience of your App Clip](https://developer.apple.com/documentation/AppClip/testing-the-launch-experience-of-your-app-clip)
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
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [App Clips HIG](https://developer.apple.com/design/human-interface-guidelines/app-clips)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
