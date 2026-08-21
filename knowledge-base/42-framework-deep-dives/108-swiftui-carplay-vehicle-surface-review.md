# SwiftUI CarPlay and vehicle-surface review

This is the focused CarPlay review for an iPhone app that may expose a vehicle experience. It complements the earlier system route in [Watch, CarPlay, and App Clips](../43-system-framework-deep-dives/04-watch-carplay-and-app-clips.md) and the reusable [CarPlay and communications recipes](../70-code-recipes/20-watch-carplay-appclips-and-communications-recipes.md). This page adds the modern entitlement, scene, template, vehicle-limit, voice, accessibility, privacy, attention, local-AI, and release boundaries needed before calling a CarPlay route native or vehicle-ready.

CarPlay is not a second SwiftUI window in a car. CarPlay creates and owns a vehicle scene, renders system-defined templates, and supplies an interface controller. Navigation apps are the special case: they receive a CarPlay window for drawing map content, while the template system remains the interaction layer. SwiftUI can own the iPhone product, domain model, settings, handoff, and test harness, but a CarPlay integration still follows the CarPlay framework’s scene and template contracts.

The central route is:

user outcome -> eligible category -> managed entitlement -> iPhone and CarPlay targets -> scene connection -> system template or navigation map surface -> vehicle-limited state -> reviewed command -> domain truth -> physical vehicle and release proof

A template instance, simulator display, Siri phrase, App Intent, Foundation Models proposal, or Liquid Glass preview is not proof of vehicle behavior, attention safety, privacy, accessibility, or App Store eligibility.

## Route thesis

Choose the smallest CarPlay surface that satisfies the outcome.

| User outcome | First route | Add only when needed | Boundary |
| --- | --- | --- | --- |
| Browse a short set of audio content | CarPlay audio entitlement, CPListTemplate, and CPNowPlayingTemplate | MediaPlayer, Siri media intents, remote commands | The system owns the layout and playback controls; a list row is not proof that playback is ready |
| Show a route and maneuvers | CarPlay maps entitlement, CPTemplateApplicationScene, CPMapTemplate, and a map-drawing CPWindow | CPSearchTemplate, CPManeuver, CPRouteInformation, dashboard scene, instrument cluster | Only navigation apps draw the map base; templates provide interaction and overlays |
| Read or act on conversations | CarPlay communication entitlement, CPListTemplate, CPMessageListItem, CPContactTemplate, SiriKit | CallKit, messaging intents, voice-control state | Message rows invoke Siri flows; do not expose arbitrary message controls |
| Show parking, charging, or quick ordering information | The matching managed entitlement and category templates | CPPointOfInterestTemplate, CPInformationTemplate, payment or account handoff | Category and entitlement decide which templates are allowed |
| Provide a small system action | App Intent, SiriKit intent, or a template handler | Handoff, notification, Watch Connectivity, or Live Activity | A discoverable action is not permission to invent a CarPlay surface |
| Show current progress on the dashboard | ActivityKit Live Activity with CarPlay-aware compact or custom family layout | Navigation or audio template for the primary experience | CarPlay deactivates interactive elements in Live Activities |
| Continue an iPhone task in the car | Handoff or a typed pending record | CarPlay scene and a safe resume point | Handoff carries intent/context; it does not transfer authentication or commit a mutation |
| Suggest a destination, playlist, or order | Deterministic candidate generation plus optional on-device AI | App Intent or Siri confirmation | A model candidate must be revalidated and approved before a side effect |
| Make an Apple-native settings or review screen | SwiftUI and current system controls on iPhone | Liquid Glass on the app-owned surface | Do not attempt to draw a fake CarPlay shell or replace system templates |

## What Apple actually gates

### Category before code

CarPlay’s official documentation lists category-specific managed entitlements. The current route must record the selected category before anyone writes template code.

| Product category | Managed entitlement named by Apple | Typical route |
| --- | --- | --- |
| Audio | com.apple.developer.carplay-audio | CPListTemplate, CPNowPlayingTemplate, MediaPlayer, Siri media intent |
| Communication | com.apple.developer.carplay-communication | CPListTemplate, CPMessageListItem, CPContactTemplate, Siri call/message intent |
| EV charging | com.apple.developer.carplay-charging | Point-of-interest and information routes for charging |
| Navigation | com.apple.developer.carplay-maps | CPMapTemplate, map window, search, maneuvers, dashboard |
| Parking | com.apple.developer.carplay-parking | Point-of-interest and information routes for parking |
| Quick food ordering | com.apple.developer.carplay-quick-ordering | Short list and information route with category-specific depth |

The entitlement is not a convenience switch. Apple’s process requires requesting the appropriate entitlement through CarPlay Contact Us, agreeing to the CarPlay Entitlement Addendum, and configuring the approved managed capability in the App ID, provisioning profile, Entitlements.plist, and code-signing settings. A local Boolean in a plist is not evidence that the developer account or signed archive has the capability.

Keep these states separate:

- requested;
- approved in the developer account;
- present in the App ID;
- present in the provisioning profile;
- present in the target’s signed entitlements;
- accepted by the installed system;
- behavior observed in an eligible vehicle.

A route that skips category selection usually ends up with a template catalog that cannot ship.

### Target graph

A normal project has:

- the iPhone application target;
- any SiriKit Intents extension or App Intents code;
- an iOS scene manifest with a CarPlay scene configuration;
- optional navigation dashboard or instrument-cluster scene configurations;
- optional WidgetKit or ActivityKit targets;
- tests that can run without a head unit;
- a signed archive containing the intended target and entitlements.

CarPlay is configured through the scene manifest in Info.plist or through the app delegate’s configuration method. The CarPlay scene delegate is created by the system; the app does not instantiate it from a SwiftUI view. Record the actual scene role, scene class, configuration name, delegate class, and target membership.

A navigation app may additionally declare a dashboard navigation scene. The dashboard scene has different scene roles and delegate methods from the primary template application scene. Treat dashboard and instrument-cluster support as separate target/configuration proof, not as automatic consequences of a working map scene.

## Scene lifecycle and ownership

### Non-navigation scene

For audio, communication, parking, charging, and quick ordering, CarPlay calls the scene delegate’s connection method with a CPInterfaceController. Store that controller in a long-lived coordinator, set a root template, and release or invalidate scene-specific references when CarPlay disconnects.

The interface controller owns a template navigation hierarchy. Use:

- setRootTemplate for the initial category surface;
- pushTemplate for hierarchical navigation;
- popTemplate or popToRootTemplate to return;
- presentTemplate for a system modal template when the route allows it;
- dismissTemplate for the matching modal.

Do not present an arbitrary SwiftUI view controller and assume it becomes a compliant CarPlay screen. Use the templates and delegate contracts Apple provides.

### Navigation scene

For navigation apps, CarPlay calls the connection method that supplies both a CPInterfaceController and CPWindow. Before returning from that connection method:

1. Create the map-drawing view controller.
2. Assign it as the window’s root view controller.
3. Create the CPMapTemplate.
4. Set the map template as the interface controller’s root template.
5. Start publishing only the navigation state that the template and driver need.

Apple’s boundary is explicit: draw map content in the CarPlay window’s root view controller, but do not draw alerts, custom overlays, or other interface elements there. Use CarPlay templates for the interaction layer. The base map does not receive direct user interaction; panning, controls, alerts, and route selection belong in the template system.

### Disconnect is a real state

When the system removes the CarPlay scene, stop treating the vehicle surface as active. Persist any necessary domain state on the iPhone, cancel scene-scoped work, detach observers, and clear the interface-controller or window reference. Do not delete the user’s route or playback state merely because the head unit disconnected.

A clean state model distinguishes:

| State | Meaning | Safe behavior |
| --- | --- | --- |
| no eligible scene | No CarPlay surface is currently connected | Keep the iPhone route available |
| connecting | The system is creating the scene | Avoid duplicate root setup |
| connected and loading | Scene exists but the first projection is not ready | Show a concise loading or empty template |
| connected and ready | Root template or map surface is installed | Accept only permitted user actions |
| limited interface | Vehicle reports keyboard/list or other limits | Rebuild content within the reported limits |
| disconnected | Scene removed | Cancel vehicle-only work and persist pending state |
| domain unavailable | Phone service, account, network, or data is unavailable | Explain in CarPlay and offer a safe retry or fallback |
| authorization missing | The signed or runtime capability is absent | Do not fabricate a partially working template |
| stale | Data age exceeds the product policy | Show age and recovery, not a confident current claim |

## Template route map

### General-purpose templates

| Template | Good fit | Avoid |
| --- | --- | --- |
| CPListTemplate | Scannable sections, categories, short queues, messages | Deep navigation without checking depth and item limits |
| CPGridTemplate | A small set of high-value actions or categories | Treating the grid as an icon wall; only the first eight buttons are shown |
| CPTabBarTemplate | A small set of stable top-level destinations | Many tabs or changing tab meaning while driving |
| CPSearchTemplate | Destination, content, or place search | Requiring long text entry or assuming a full keyboard |
| CPActionSheetTemplate | A short mutually exclusive choice | A large settings screen |
| CPAlertTemplate | A concise blocking decision or error | Displacing a critical navigation or communication state |
| CPVoiceControlTemplate | Navigation voice-input indicator | A generic chatbot or free-form AI transcript surface |
| CPNowPlayingTemplate | Shared audio playback surface | Instantiating a custom Now Playing template or presenting it modally |

CarPlay owns layout, sizing, interaction affordances, hardware input, dark/light treatment, and much of the error presentation. The app supplies data, handlers, images, localized strings, and domain results.

### List limits and handler completion

A CPListTemplate has maximum section and item limits. Some vehicles impose additional list limits. Hierarchical depth depends on the app entitlement: Apple’s documentation says food-ordering apps are limited to two levels and other categories are restricted to five levels. At runtime, read the template and session limits rather than assuming a simulator or one head unit’s capacity is universal.

A selectable CPListItem handler receives a completion closure. Call it after the selection work reaches the expected state. For a network-backed or account-backed action, keep the row pending until the domain result is known or explicitly present a safe failure. Do not leave CarPlay waiting on an unbounded request.

Use userInfo to attach an opaque local identifier to a list item. Do not put secrets, raw tokens, or a whole model graph into the item. CarPlay does not support arbitrary custom list item types; use the provided item classes and keep the domain object in the app-owned store.

### Grid limits

CPGridTemplate displays a bounded number of buttons and adapts its layout to the vehicle screen. Apple documents that only the first eight buttons are shown and that more than four may be balanced into two rows. Make the first visible actions complete and meaningful. Do not put a low-priority “More” button ahead of the actions the driver actually needs.

### Search limits

CPSearchTemplate provides the search field, cancel behavior, localized keyboard, and result list. Some vehicles limit keyboard display. Read CPSessionConfiguration and its limitedUserInterfaces value, reduce text-entry requirements, and provide a short list of common destinations or recent items when typed search is unavailable.

A search result is an observation, not an authorization or commitment. Re-resolve the selected result against current domain and location data before starting navigation, playing media, or placing an order.

## Category routes

### Navigation and maps

The navigation route has the strongest surface-specific rule:

- the CarPlay maps entitlement is present in the signed target;
- the navigation scene connects with both interface controller and window;
- the window root view controller draws only map content;
- CPMapTemplate is the root interaction template;
- search, route selection, maneuvers, navigation alerts, panning, and voice state are represented with CarPlay types;
- dashboard and instrument-cluster scenes are configured separately if supported;
- route state is current, authorized, and explainable.

A map image or route line is not enough. A complete proof includes location permission, current route state, reroute behavior, map rendering on a named head unit, maneuver selection, alert presentation, disconnect/reconnect, dark/light style, and accessibility/voice input.

### Audio and Now Playing

Audio apps use the audio entitlement. CPNowPlayingTemplate.shared is the system-provided shared instance. It presents information supplied through MPNowPlayingInfoCenter and MPNowPlayingSession and cannot be presented modally. The app configures supported playback buttons and pushes the shared template when the user chooses playable content.

Audio must be a good citizen:

- let the user choose when to start playback except for documented resume cases;
- do not activate an audio session before audio is ready;
- begin playback when content is sufficiently loaded;
- show Now Playing without waiting for every descriptive field;
- handle interruption and resumption according to whether the interruption is resumable;
- do not control the vehicle’s overall volume.

An audio entitlement, a Now Playing screenshot, and a successful simulator playback are separate claims.

### Communication

Communication apps use the communication entitlement and system templates. CPMessageListItem represents a conversation or contact. Selecting it invokes Siri with the parameters supplied by the app and begins a compose, read, or reply flow depending on the item’s configuration. It has no arbitrary selection handler.

The CPListTemplate assistant cell is available for audio and communication routes when the app supports the required Siri intent. Apple documents INPlayMediaIntent for audio and INStartCallIntent for communication. An assistant cell therefore depends on both template configuration and Siri intent handling. A visual assistant cell is not evidence that Siri can actually fulfill the request.

Treat message bodies, contacts, call targets, unread state, and notification previews as privacy-sensitive. Expose the minimum needed for the vehicle flow, honor user settings, and keep locked-phone behavior in the test plan.

### Parking, charging, and quick ordering

These routes are entitlement- and template-gated. Use the specific category’s system templates, short lists, points of interest, and information surfaces. Do not generalize a working navigation or list route into an eligibility claim for charging, parking, or food ordering.

Quick ordering is especially constrained: keep the route short, show the selected place/order context, require current availability and price confirmation, and make payment or account handoff explicit. A model can propose a store or item, but it must not silently place an order.

## Vehicle configuration and limited interfaces

CPSessionConfiguration exposes vehicle properties and configuration for the CarPlay environment. The app can read:

- contentStyle, which reflects the vehicle-selected content style and ambient lighting;
- limitedUserInterfaces, which indicates limits such as keyboard or list display;
- supportsVideoPlayback, where relevant to the current environment.

A session configuration delegate can receive changes to the limits. Rebuild the affected template when a limit changes. Do not merely truncate strings or silently drop controls without preserving the user’s task.

Design against:

- small and wide displays;
- portrait and landscape displays;
- different pixel densities;
- light and dark appearances;
- ambient light changes;
- touchscreens, knobs, touch pads, and hardware buttons;
- limited keyboard availability;
- limited list item counts;
- a locked iPhone;
- a vehicle moving or the driver being unable to complete a long flow.

The CarPlay simulator is valuable for scene and template development, but it is not physical-vehicle proof. Apple specifically documents that the simulator cannot test a locked iPhone, Siri interactions, and real audio behavior. The proof plan must include an approved head unit or physical vehicle for those claims.

## Cross-surface boundaries

### iPhone and CarPlay

The iPhone remains the app’s domain host unless the product architecture says otherwise. CarPlay is a system-managed presentation and command surface. Keep the following separate:

- iPhone UI state;
- CarPlay scene state;
- domain truth;
- external vehicle state;
- transport/network state;
- pending user command;
- committed result.

Never require the driver to pick up or unlock the iPhone to resolve a CarPlay error. Apple’s HIG says CarPlay apps should work when the iPhone is inaccessible and that errors should be reported in CarPlay.

### Handoff

Use Handoff or a typed pending record when a person begins a task on iPhone and should continue in CarPlay. Carry a stable task identifier, source revision, display-safe summary, and expiration. Re-resolve the record after the CarPlay scene connects. Handoff does not grant a CarPlay entitlement, bypass authentication, or prove that the command was committed.

### Watch Connectivity

If a watch companion supplies a destination, playback state, or order draft, Watch Connectivity remains a separate paired-device transport. Its reachability and transfer callbacks do not prove CarPlay connectivity. Use a domain revision and a conflict policy when iPhone, watch, and vehicle can all observe or propose changes.

### Now Playing

Now Playing is a shared audio system surface with its own entitlement and MediaPlayer state. It is not a general-purpose CarPlay detail view. If a CarPlay audio app changes the playing item, update the authoritative playback state and the shared Now Playing information together, then verify interruption and resume behavior.

### Live Activities

Apple’s current Live Activities HIG says CarPlay automatically combines the leading and trailing compact elements for the CarPlay Dashboard. Interactive elements are deactivated in CarPlay. If the activity needs more information, use the supported supplemental activity family and test the documented dimensions.

Use a Live Activity for timely passive progress, not as a substitute for the primary navigation, ordering, or communication template. A Live Activity appearing in a dashboard is not proof that a tappable control will work in the vehicle.

## Siri, App Intents, and local AI

### SiriKit and template voice routes

Use the intent family Apple documents for the category and make resolution, confirmation, and handling explicit. For communication and media, preserve the assistant-cell requirements. For navigation, use the documented voice-control indicator while audio input is active.

A voice phrase should enter a deterministic command pipeline:

voice or system intent -> resolve entity -> check authorization and current state -> confirm any consequential action -> commit domain command -> update template or system surface -> record evidence

A recognized phrase is not a successful command. A Siri response is not proof that the map started, message was sent, or playback was ready.

### App Intents

App Intents make app capabilities available to system experiences such as Siri and Shortcuts and may make actions discoverable by Apple Intelligence. They are valuable for opening the right iPhone route, resolving a stable place or media entity, or performing a small already-authorized action.

App Intents do not:

- grant a CarPlay managed entitlement;
- let an arbitrary SwiftUI view render in CarPlay;
- replace CPTemplateApplicationScene lifecycle;
- make a private model or database system-authoritative;
- authorize a purchase, call, message, route start, or order without the product’s normal checks.

Keep App Intent parameters typed and small. Resolve current entities at execution time, reject stale revisions, make duplicate invocation safe, and return a result that distinguishes proposed, confirmed, committed, failed, and unavailable.

### Foundation Models and on-device proposals

Use Foundation Models only after checking SystemLanguageModel availability and the actual device/OS context. An on-device model can help summarize a trip, rank a few user-authorized destinations, classify a playlist, or prepare a draft. It should not be positioned as a driver, a sensor of road truth, or an autonomous authority.

For a CarPlay proposal:

1. collect a minimal, privacy-reviewed context;
2. give the model a closed task and structured output;
3. validate identifiers, permissions, freshness, geography, and category;
4. show the proposal in an approved CarPlay template or a safe iPhone review surface;
5. require confirmation for consequential actions;
6. commit through the deterministic domain layer;
7. publish the committed result, not raw prompt context, to CarPlay, Watch, or Live Activities.

If the model is unavailable, low on resources, outside the supported locale, or returns an invalid candidate, use a deterministic route. Do not show an AI placeholder as current vehicle or account truth.

## Native design, Liquid Glass, and system ownership

CarPlay’s native look comes from the system-defined templates and the vehicle’s content style. The HIG emphasizes fast, minimal interaction, useful information, consistent hierarchy, and compatibility with the car’s input hardware. A custom Liquid Glass replica can make a surface look familiar while violating the actual CarPlay interaction model.

Use Liquid Glass on app-owned iPhone SwiftUI surfaces when it clarifies hierarchy and remains accessible. Keep it out of the CarPlay template layer:

- do not embed a custom SwiftUI glass panel inside CPMapTemplate’s map window;
- do not draw custom alerts, translucent navigation bars, or fake system controls over the map;
- do not make car controls depend on a glass-only visual cue;
- do not use blur, transparency, or animation to compete with route guidance;
- do use the provided templates, CPImageSet assets, system text, and system interaction states.

For the iPhone companion shell, follow [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass) and [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views). For CarPlay, the system template is the native surface. Treat any custom iPhone review screen as a bridge back to an action-safe CarPlay route, not as a second vehicle UI.

## Accessibility, input, privacy, and attention

CarPlay is designed for drivers. The useful design unit is a task that can be completed with minimal visual attention and a small number of interactions.

Review:

- VoiceOver labels and order;
- Voice Control and Siri phrasing;
- Dynamic Type and localized text;
- high contrast, dark/light appearance, and ambient lighting;
- reduced motion and reduced transparency;
- touch, knob, touch-pad, and hardware-button focus;
- disabled and pending controls;
- error recovery without iPhone access;
- audio ducking, speech prompts, and interruption;
- passenger versus driver assumptions;
- sensitive content on a visible shared screen.

Prefer short titles, clear primary actions, strong contrast, and stable focus. Do not encode meaning only in color. Never make the most important control the smallest or least reachable item. If a task requires a long form, account recovery, reading a full message, payment entry, or complicated setup, pause the vehicle route and provide a safe continuation path.

Privacy questions belong in the route, not only in the privacy policy:

- Can a passenger or bystander see the current screen?
- What appears while the iPhone is locked?
- Does the template reveal message text, contact details, account data, location history, or order information?
- Does an App Intent or model context include more than the user asked for?
- What remains after disconnect, sign-out, unpairing, or account switch?
- Does an error reveal a sensitive server or identity condition?

## Failure matrix

| Failure | Wrong conclusion | Correct response |
| --- | --- | --- |
| CarPlay scene is not called | The app is broken | Check entitlement, scene manifest, target membership, provisioning, installation, and eligible category |
| Template appears in Simulator | The vehicle route is shipped | Run locked-phone, Siri, audio, accessibility, and physical head-unit tests |
| isConnected-like state is true | The domain is synchronized | Record scene state separately from data freshness and commit state |
| CPListTemplate truncates items | All content is available | Read maximum counts and session limits; design a bounded route |
| Keyboard is unavailable | Search is impossible | Use recent, favorite, voice, and short-query alternatives |
| Siri recognizes a phrase | The side effect happened | Resolve, confirm, commit, and record the domain result |
| Foundation Models returns a place | The place is current and safe | Revalidate identifier, location, authorization, and freshness |
| Live Activity appears on dashboard | Its buttons work | Treat CarPlay presentation as passive; use templates for actions |
| Liquid Glass looks native on iPhone | It belongs in CarPlay | Keep custom glass on app-owned surfaces; use system templates in the vehicle |
| iPhone displays the error | The driver will see it | Report the actionable error in CarPlay and offer safe recovery |
| Archive contains an entitlement key | The capability is approved | Inspect signed entitlements and account/profile state, then test installation |
| CarPlay disconnects | The user’s record should vanish | Persist domain state; cancel only scene-scoped work |

## Evidence ladder

| Level | Evidence | Supports | Does not support |
| --- | --- | --- | --- |
| L0 | Official docs and category decision | API family, template, entitlement, and HIG boundary | A working target |
| L1 | Source and project inspection | Scene manifest, target membership, Info.plist, entitlement intent | Developer-account approval or installed behavior |
| L2 | Compile and unit fixtures | Scene routing, reducer, list limits, command validation, AI fallback | Vehicle rendering, Siri, locked-phone, or audio behavior |
| L3 | CarPlay Simulator | Template hierarchy, basic interaction, layout fixtures, limited-state handling | Locked iPhone, Siri, real audio, physical vehicle, ambient lighting |
| L4 | Signed iPhone plus approved head unit or physical vehicle | Connect/disconnect, lock state, Siri, audio, driver input, accessibility, privacy, map and template behavior | App Store approval or all vehicles |
| L5 | Instrumented representative vehicle run | Delay, interruption, route recovery, list limits, ambient appearance, thermal/energy observations | Universal fleet coverage |
| L6 | Archive, TestFlight, and installation proof | Signed target graph, entitlements, version/build, install and release configuration | Real-world usage or approval guarantee |
| L7 | App Store and production evidence | Distribution outcome and observed production route | Future vehicle or OS behavior |

Never promote a screenshot to L4, a template callback to a domain commit, a model proposal to a driving decision, or an entitlement request to a signed capability.

## Implementation checklist

Before opening a CarPlay task in an app repo, record:

- product category and why it is eligible;
- requested and approved managed entitlement;
- iPhone bundle identifier and build target;
- CarPlay scene role, class, configuration name, and delegate;
- whether the app is navigation and needs a CPWindow;
- root template and every pushed/presented template;
- list/grid/search limits and fallback copy;
- locked-iPhone behavior;
- SiriKit or App Intent route;
- iPhone, Watch, Handoff, Now Playing, and Live Activity boundaries;
- AI input, output schema, validation, and no-model fallback;
- privacy redaction and deletion behavior;
- accessibility and alternate-input plan;
- named simulator configuration;
- named head unit or physical vehicle;
- archive, signed-entitlement, TestFlight, and release evidence.

## Sources

- [CarPlay](https://developer.apple.com/documentation/carplay)
- [Requesting CarPlay entitlements](https://developer.apple.com/documentation/carplay/requesting-carplay-entitlements)
- [Displaying content in CarPlay](https://developer.apple.com/documentation/carplay/displaying-content-in-carplay)
- [Using the CarPlay Simulator](https://developer.apple.com/documentation/carplay/using-the-carplay-simulator)
- [CPTemplateApplicationScene](https://developer.apple.com/documentation/carplay/cptemplateapplicationscene)
- [CPTemplateApplicationSceneDelegate](https://developer.apple.com/documentation/carplay/cptemplateapplicationscenedelegate)
- [CPTemplateApplicationDashboardSceneDelegate](https://developer.apple.com/documentation/carplay/cptemplateapplicationdashboardscenedelegate)
- [CPInterfaceController](https://developer.apple.com/documentation/carplay/cpinterfacecontroller)
- [CPListTemplate](https://developer.apple.com/documentation/carplay/cplisttemplate)
- [CPListItem](https://developer.apple.com/documentation/carplay/cplistitem)
- [CPGridTemplate](https://developer.apple.com/documentation/carplay/cpgridtemplate)
- [CPTabBarTemplate](https://developer.apple.com/documentation/carplay/cptabbartemplate)
- [CPSearchTemplate](https://developer.apple.com/documentation/carplay/cpsearchtemplate)
- [CPMapTemplate](https://developer.apple.com/documentation/carplay/cpmaptemplate)
- [CPVoiceControlTemplate](https://developer.apple.com/documentation/carplay/cpvoicecontroltemplate)
- [CPNowPlayingTemplate](https://developer.apple.com/documentation/carplay/cpnowplayingtemplate)
- [CPMessageListItem](https://developer.apple.com/documentation/carplay/cpmessagelistitem)
- [CPAssistantCellConfiguration](https://developer.apple.com/documentation/carplay/cpassistantcellconfiguration)
- [CPSessionConfiguration](https://developer.apple.com/documentation/carplay/cpsessionconfiguration)
- [limitedUserInterfaces](https://developer.apple.com/documentation/carplay/cpsessionconfiguration/limiteduserinterfaces)
- [CPSessionConfigurationDelegate](https://developer.apple.com/documentation/carplay/cpsessionconfigurationdelegate)
- [Integrating CarPlay with your navigation app](https://developer.apple.com/documentation/carplay/integrating-carplay-with-your-navigation-app)
- [Integrating CarPlay with your music app](https://developer.apple.com/documentation/carplay/integrating-carplay-with-your-music-app)
- [CarPlay Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/carplay)
- [Live Activities Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/live-activities)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [Configuring Siri support](https://developer.apple.com/documentation/xcode/configuring-siri-support)
- [Resolving and handling intents](https://developer.apple.com/documentation/sirikit/resolving-and-handling-intents)
- [Messaging](https://developer.apple.com/documentation/sirikit/messaging)
- [Improving Siri media interactions](https://developer.apple.com/documentation/sirikit/improving-siri-media-interactions-and-app-selection)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility testing](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Implementing Handoff](https://developer.apple.com/documentation/foundation/implementing-handoff-in-your-app)
- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [MediaPlayer](https://developer.apple.com/documentation/mediaplayer)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines)
