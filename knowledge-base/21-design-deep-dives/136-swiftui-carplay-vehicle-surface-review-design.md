# SwiftUI CarPlay and vehicle-surface review design

This design guide translates the [CarPlay and vehicle-surface review](../42-framework-deep-dives/108-swiftui-carplay-vehicle-surface-review.md) into visual and interaction decisions. CarPlay already supplies the native shell: system templates, hierarchy, focus behavior, hardware-input adaptation, dark and light appearance, and vehicle-specific scaling. The design goal is therefore not to imitate Apple’s CarPlay pixels with custom SwiftUI. The goal is to supply a clear, original, high-value information model that becomes native through the framework.

Use this loop:

driver task -> category and template -> one primary decision -> concise state -> safe confirmation -> domain result -> recovery

## Design north star

A good CarPlay surface is:

- glanceable before it is expressive;
- useful with the iPhone locked or out of reach;
- complete without a custom overlay;
- resilient to small lists, missing keyboards, and changing content style;
- accessible through touch, knob, touch pad, hardware buttons, Voice Control, and Siri;
- honest about stale data, pending commands, and unavailable capabilities;
- quiet when the driver is busy.

A “premium” CarPlay experience is not a dense glass dashboard. It is a small number of well-labeled system templates with predictable focus and a reliable recovery path.

## Surface map

| Surface | Native visual owner | App-owned content | Design rule |
| --- | --- | --- | --- |
| CarPlay Home | CarPlay system | App icon and metadata | Mirror the iPhone icon; supply high-resolution assets and avoid black-on-black backgrounds |
| List | CPListTemplate | Sections, rows, images, state, handlers | Put the highest-value rows first; keep each row understandable without opening it |
| Grid | CPGridTemplate | Bounded action buttons | Make the first visible buttons useful; do not hide the core task after the eighth item |
| Tabs | CPTabBarTemplate | Stable top-level templates | Use only a few destinations with durable labels |
| Search | CPSearchTemplate | Query handling and result content | Offer recent/favorite/voice alternatives when keyboard input is limited |
| Map | CPMapTemplate plus CPWindow | Map base, route data, maneuvers, alerts | Draw only map content in the window; use templates for interaction |
| Now Playing | CPNowPlayingTemplate.shared | MPNowPlaying state and supported buttons | Let the system own playback layout; do not invent a parallel player |
| Communication | CPMessageListItem and related templates | Minimal conversation/contact metadata | Let Siri handle compose/read/reply flows |
| POI and information | CPPointOfInterestTemplate and CPInformationTemplate | Place, charge, parking, or order details | Keep current location, availability, and next action explicit |
| Live Activity dashboard | ActivityKit and system presentation | Timely passive progress | Treat CarPlay presentation as passive; interactive elements are disabled |
| iPhone review shell | SwiftUI | Detailed review, settings, consent, account setup | This is where custom Liquid Glass can support hierarchy if it remains accessible |

## Vehicle-safe hierarchy

Design every route around one primary question:

- What is the next action?
- What changed?
- Is the source current enough?
- What happens if the user selects it?
- What can the user do if the action fails?

Use a small state vocabulary:

| State | Suggested language | Visual behavior |
| --- | --- | --- |
| Ready | Ready, Available, Start | Enabled primary handler |
| Loading | Loading, Checking availability | Spinner or concise loading state |
| Stale | Updated 12 minutes ago | Keep value but expose age and recovery |
| Pending | Sending, Starting, Updating | Disable duplicate action; allow safe cancel if supported |
| Confirm | Confirm destination, Confirm order | Short summary with explicit commit |
| Failed | Could not load, Try again | Explain in CarPlay, never point to the iPhone |
| Unavailable | Not available while driving | Offer a safe alternate route |
| Locked | Needs confirmation | Use Siri or defer to iPhone after stopping |
| Complete | Started, Sent, Saved | Show the committed result and next safe action |

Do not use “connected” as the only status. Pair scene state, data freshness, authorization, and domain commit as separate labels in the internal model even if the visible copy is brief.

## Hierarchy by category

### Navigation

Use a map-first composition:

1. map and route remain the visual base;
2. the next maneuver is the primary information;
3. route alternatives are a bounded decision;
4. search and recenter are secondary;
5. alerts are short and actionable;
6. dashboard or instrument-cluster content is a separate projection.

Avoid a custom glass control bar over the map. Keep route styling legible in light, dark, direct sunlight, and night conditions. Do not rely on hue alone for lanes, warnings, or route choices.

### Audio

Use a predictable browse -> choose -> play -> Now Playing path. A list row should tell the user enough to select it. When playback is ready, make the shared Now Playing state current without waiting for every artwork or metadata field.

Audio design rules:

- do not auto-start unexpected playback;
- do not compete with navigation prompts;
- show a clear loading state while buffering;
- use the system Now Playing surface;
- return gracefully after resumable interruptions;
- do not change the vehicle’s overall volume.

### Communication

Show only what is needed to identify a conversation or contact and choose the Siri flow. Avoid exposing full message bodies, private notifications, or settings forms. Use short contact labels and unread state carefully; an unread indicator should not reveal more than the user expects on a shared vehicle screen.

The assistant cell is a voice entry point, not a decorative assistant panel. Its label should explain the supported Siri action and its visibility should be tested in the signed communication target.

### Charging, parking, and ordering

Make place, availability, distance, and next action explicit. Show a short route to an information template. For ordering, keep the flow bounded: choose place, choose a small number of options, review, confirm, and return a result. Payment, account recovery, and detailed customization should defer safely.

## Native appearance and Liquid Glass boundaries

CarPlay automatically adapts its system templates to display dimensions, vehicle input hardware, content style, and light conditions. This is the native system language. Custom styling should be limited to app-supplied content such as iconography, imagery, concise copy, and map appearance.

On the iPhone app-owned surface:

- use current SwiftUI controls;
- allow the operating system to supply the current Liquid Glass treatment;
- use a small number of glass groups around related controls;
- keep text and actions readable without relying on transparency;
- provide Reduce Transparency and increased-contrast behavior;
- avoid stacking glass over glass.

On the CarPlay surface:

- do not create a custom SwiftUI glass overlay inside the map window;
- do not draw an imitation system navigation bar or alert;
- do not apply decorative blur to rows or buttons;
- do not make a critical state visible only through translucency;
- do use CPImageSet for light/dark artwork and system templates for controls.

If the design review says “make CarPlay look more like our iPhone Liquid Glass screen,” translate that request into “use the same hierarchy, icon vocabulary, content tone, and source-of-truth language.” Do not translate it into a custom vehicle UI.

## Interaction and input

The same route must work through several inputs:

| Input | Design check |
| --- | --- |
| Touch | Target is clear, large enough, and not dependent on a hidden gesture |
| Knob | Focus order is predictable and the focused row remains understandable |
| Touch pad | Selection and back behavior are obvious |
| Hardware buttons | The primary action is reachable without text entry |
| Siri | Intent names and entity labels sound natural |
| Voice Control | Labels identify the intended control without duplicate ambiguity |
| Voice guidance | Prompts do not obscure or compete with critical navigation audio |
| Assistive settings | Contrast, motion, transparency, and Dynamic Type changes retain hierarchy |

Use system-provided focus and selection behavior. Do not simulate focus with a custom glow that disappears in an alternate appearance. Keep labels distinct. Test long localized strings and right-to-left layout.

## Motion, sound, and attention

Motion should explain a change, not advertise the app. Use the system’s template transitions and avoid adding animation that draws attention during route guidance. Honor Reduce Motion and reduce or remove nonessential transitions.

Audio must be coordinated with the vehicle environment. A navigation prompt, music playback, Siri response, call, and error tone can coexist. Test interruptions, ducking, resumption, and silence. A silent UI state is often safer than a repeated alert.

For Live Activities, design the content as an observation of ongoing progress. CarPlay deactivates interactive elements in the Live Activity presentation, so move any action into the appropriate CarPlay template.

## AI design contract

An AI-enabled CarPlay feature should look like a reviewed suggestion, not an autonomous co-driver.

| AI stage | CarPlay-safe representation |
| --- | --- |
| Candidate generation | Small set of named destinations, playlists, or order choices |
| Source context | Show current source and age when it affects the decision |
| Validation | Deterministic checks for ID, permissions, location, availability, and revision |
| Review | Concise template summary or deferred iPhone review |
| Commit | A normal domain command with an explicit result |
| Failure | Deterministic fallback or a safe deferral |
| Audit | Record model availability, candidate, validation, user choice, and committed revision |

Avoid free-form model chat while driving. Avoid model-generated road rules, health claims, urgency, pricing, or identity assertions. Do not pass an entire account, message history, or location history to the model when a few identifiers are sufficient.

## Blueprints

### Navigation blueprint

| Layer | Decision |
| --- | --- |
| iPhone source | Authorized location, route store, and user preferences |
| CarPlay root | CPMapTemplate plus map-drawing CPWindow |
| Supporting templates | CPSearchTemplate, route selection, alerts, voice-control state |
| AI role | Rank user-approved destinations or summarize a route choice |
| Validation | Re-resolve place, route, location, authorization, and freshness |
| Fallback | Recent/favorite destinations and deterministic search |
| Proof | Locked iPhone, Siri, physical head unit, day/night, reroute, disconnect |

### Audio blueprint

| Layer | Decision |
| --- | --- |
| iPhone source | Playback queue and MediaPlayer state |
| CarPlay root | CPListTemplate |
| Shared system surface | CPNowPlayingTemplate.shared |
| Voice route | INPlayMediaIntent and assistant cell where configured |
| AI role | Rank a small library subset or summarize a queue |
| Validation | Item identity, entitlement, availability, playback policy |
| Fallback | Recent queue or local library |
| Proof | Interruptions, buffering, audio session, Siri, physical vehicle |

### Communication blueprint

| Layer | Decision |
| --- | --- |
| iPhone source | Authorized contacts/conversations and message service |
| CarPlay root | CPListTemplate with CPMessageListItem or contact template |
| Voice route | Siri communication intent and assistant cell where supported |
| AI role | Draft only on iPhone or produce a short candidate for explicit confirmation |
| Validation | Recipient identity, account, message policy, current conversation revision |
| Fallback | Siri or defer to iPhone after stopping |
| Proof | Locked iPhone, privacy redaction, voice flow, duplicate/retry, physical vehicle |

### Charging or ordering blueprint

| Layer | Decision |
| --- | --- |
| iPhone source | Current place/service availability and account state |
| CarPlay root | Point-of-interest or information template |
| AI role | Rank a few eligible options |
| Validation | Current location, hours, price, availability, account, payment/confirmation |
| Fallback | Favorites and deterministic nearby results |
| Proof | Entitlement, stale data, confirmation, cancellation, physical vehicle |

## Error and empty-state copy

Use copy that lets the driver recover without touching the iPhone:

- “Couldn’t load nearby chargers. Try again.”
- “Search is unavailable while the keyboard is limited. Try a favorite.”
- “This destination changed. Review the updated route.”
- “Message not sent. Try again when the connection is stable.”
- “Playback is unavailable. Choose another item.”
- “This action needs review on iPhone after stopping.”
- “CarPlay disconnected. Your draft is saved on iPhone.”
- “This feature isn’t available in this vehicle.”

Avoid:

- “Open the iPhone to fix this.”
- raw server errors;
- opaque error codes;
- “AI failed” without a deterministic fallback;
- a stale result labeled “current”;
- silent selection with no committed-result state.

## Design QA matrix

| Review | Preview or fixture | Simulator | Physical vehicle |
| --- | --- | --- | --- |
| Template hierarchy | Full route fixture | Push/pop/present behavior | Focus and hardware input |
| Long text | Localization fixture | Layout and truncation | Readability at driving distance |
| Light/dark | Color and asset fixture | Content style | Ambient light and night |
| Limited keyboard/list | Limit fixture | Rebuild route | Vehicle-specific limits |
| Siri | Intent metadata and mocks | Not sufficient | Locked-phone Siri route |
| Audio | Interruption fixture | Basic playback | Ducking, radio, prompts, resumption |
| Map | Deterministic route fixture | Map window and templates | Location, reroute, alert, dashboard |
| Privacy | Redacted snapshots | Locked-state approximation | Shared screen and locked iPhone |
| Accessibility | Labels and traits | Navigation | VoiceOver, Voice Control, alternate inputs |
| AI | Candidate fixtures | Availability and fallback | Safe review and commit behavior |
| Liquid Glass | iPhone preview | Settings shell | N/A for system CarPlay templates |
| Release | Target inspection | Signed simulator build | Archive, TestFlight, install |

## Sources

- [CarPlay Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/carplay)
- [Live Activities Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/live-activities)
- [Displaying content in CarPlay](https://developer.apple.com/documentation/carplay/displaying-content-in-carplay)
- [CPListTemplate](https://developer.apple.com/documentation/carplay/cplisttemplate)
- [CPGridTemplate](https://developer.apple.com/documentation/carplay/cpgridtemplate)
- [CPTabBarTemplate](https://developer.apple.com/documentation/carplay/cptabbartemplate)
- [CPSearchTemplate](https://developer.apple.com/documentation/carplay/cpsearchtemplate)
- [CPMapTemplate](https://developer.apple.com/documentation/carplay/cpmaptemplate)
- [CPNowPlayingTemplate](https://developer.apple.com/documentation/carplay/cpnowplayingtemplate)
- [CPMessageListItem](https://developer.apple.com/documentation/carplay/cpmessagelistitem)
- [CPSessionConfiguration](https://developer.apple.com/documentation/carplay/cpsessionconfiguration)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility testing](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Configuring Siri support](https://developer.apple.com/documentation/xcode/configuring-siri-support)
- [Implementing Handoff](https://developer.apple.com/documentation/foundation/implementing-handoff-in-your-app)
- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
