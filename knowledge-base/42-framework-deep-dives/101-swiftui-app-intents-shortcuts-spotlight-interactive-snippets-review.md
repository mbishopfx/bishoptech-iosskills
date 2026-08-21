# SwiftUI App Intents, Shortcuts, Spotlight, and interactive system-snippet review

App Intents is the structured bridge between an app’s capabilities and Apple system experiences. A SwiftUI feature can expose an action to Shortcuts, an App Shortcut to Siri and Spotlight, an AppEntity to entity resolution, an IndexedEntity to Spotlight, an interactive snippet as a compact result, and a scene/context route that opens the right app surface. These are related contracts, not one universal “AI integration.”

This review extends the existing [interactive snippet deep dive](../41-framework-deep-dives/10-interactive-app-intent-snippets.md), [entity schema/interoperability deep dive](../41-framework-deep-dives/11-app-intents-schema-and-entity-interoperability.md), [semantic index and onscreen-context deep dive](../41-framework-deep-dives/15-app-intents-semantic-index-search-and-onscreen-context.md), [transfer and execution deep dive](../41-framework-deep-dives/16-app-intents-transfer-ownership-and-execution.md), [Core Spotlight deep dive](31-core-spotlight-and-useractivity-discoverability.md), and the existing [Visual Intelligence route](../50-capability-recipes/95-visual-intelligence-app-intents-and-entity-route.md). Its distinct focus is the end-to-end system handoff from a user-relevant native feature to a current, authorized, reviewable result.

## The system-discoverability contract

Keep the route explicit:

~~~text
user-relevant app capability
-> typed AppIntent action
-> AppEntity projection for app-owned concepts
-> EntityQuery current resolution
-> optional App Shortcut or schema
-> optional IndexedEntity/Core Spotlight donation
-> optional visual/onscreen context
-> system invocation in an eligible process
-> current authorization and domain operation
-> static result, interactive snippet, Live Activity, or app scene
-> user review where required
-> deterministic, idempotent side effect
~~~

The system owns invocation timing, language interpretation, ranking, presentation, and some process selection. The app owns:

- what action or entity it exposes;
- localized metadata and display representation;
- stable identifiers and current resolution;
- authorization and account scope;
- cancellation and concurrency;
- the actual domain mutation;
- the result/snippet content;
- deep-link or scene routing;
- privacy, deletion, and fallback behavior.

An AppIntent declaration is not proof that Siri or Shortcuts will invoke it. An index entry is not current authorization. A snippet preview is not a committed domain mutation. A Visual Intelligence label is not a verified identity or measurement.

## Route selector

| Desired outcome | Primary contract | Keep separate |
| --- | --- | --- |
| Offer a user-configurable action | AppIntent | Parameters, authorization, result, errors |
| Make one common action available immediately after install | AppShortcut and AppShortcutsProvider | Phrase, metadata, parameter defaults, system ranking |
| Support a known domain such as messages, photos, or media | App schema domain | Schema availability, generated requirements, custom additions |
| Represent a record or app concept | AppEntity | Shadow projection, stable ID, display representation |
| Resolve a system-provided ID | EntityQuery | Current store, account, deletion, authorization |
| Make entities searchable | IndexedEntity and CSSearchableIndex | Index metadata, deletion, reindexing, OpenIntent |
| Search a large live catalog | ShowInAppSearchResultsIntent and in-app search | Query cancellation, current results, native navigation |
| Show a small visual result | static result snippet | Audio dialogue, concise visual hierarchy |
| Confirm or follow up without opening app | SnippetIntent and ShowsSnippetView | Repeated render, idempotent nested AppIntent |
| Match camera/onscreen context | IntentValueQuery and SemanticContentDescriptor | Capture privacy, ambiguous match, current entity resolution |
| Open a specific app scene | OpenIntent, AppIntentSceneDelegate, scene intent protocols | Scene selection, route validation, foreground boundary |
| Transfer an entity between system workflows | IntentValueRepresentation and Transferable | Ownership, redaction, destination, source revision |

Choose the narrowest contract. Adding every system surface to one action makes identity, privacy, parameters, error handling, and release proof harder to reason about.

## AppIntent is an action boundary

AppIntent expresses an app-specific capability the system can discover and invoke. It can live in an app, app extension, framework, or Swift package when the target and dependency graph support it. Its metadata should tell a person what will happen, and its perform method should execute one bounded app-owned operation.

For every intent, record:

- localized title and description;
- parameters and resolution rules;
- supported execution modes/targets;
- process and target membership;
- account and authorization dependency;
- whether it opens the app or can run in the background;
- cancellation and timeout behavior;
- confirmation requirement;
- result type and snippet/Live Activity behavior;
- idempotency key or domain revision;
- error mapping and recovery action.

Use AppIntentError cases such as permission-required, unrecoverable, or user-action-required routes when the selected SDK supports them. An error should tell the system and person what can happen next; it should not pretend a failed mutation succeeded.

### Action versus observation

Keep a read/resolve intent separate from a mutation intent when possible:

~~~text
FindCurrentProjectIntent
-> reads current project
-> returns entity/result/snippet

ArchiveProjectIntent
-> resolves current project
-> confirms destructive scope
-> applies one idempotent mutation
-> returns result or error
~~~

Avoid using a generated summary, confidence score, or stale indexed field as the sole input to a destructive AppIntent. Re-resolve the entity and re-check authorization immediately before commit.

## AppEntity is a system-facing projection

AppEntity represents an app concept that Apple Intelligence, Siri, Shortcuts, Spotlight, or Visual Intelligence can reason about. It should be a small, stable projection, not an accidental export of a persistence model.

A good entity has:

- a stable ID that resolves to current domain truth;
- a localized TypeDisplayRepresentation;
- a concise instance DisplayRepresentation;
- only the properties needed for discovery or parameter selection;
- a default EntityQuery;
- a safe URL/open route when applicable;
- explicit ownership/sharing context when the feature exposes it;
- Sendable and actor-safe data boundaries.

Apple notes that an app can conform its data model directly or create app-intent-specific shadow models. Prefer a shadow projection when the persistence model contains private fields, framework objects, mutable relationships, credentials, or large media.

The query is the resolver:

1. accept IDs from the system;
2. check account/session scope;
3. fetch current records;
4. reject deleted, expired, or unauthorized records;
5. return only entities that still exist;
6. preserve input order where the caller expects it;
7. map missing results into an honest no-result or user-action-required path.

EntityQuery is not an index read. A system may pass an identifier from a stale index or an earlier conversation. The current store owns truth.

## App Shortcuts and app schemas

App Shortcuts combine an AppIntent with spoken phrases, short title, SF Symbol/image, and optional preconfigured parameters. Apple’s current HIG says App Shortcuts are available immediately after installation, and each app can include up to ten. Use them for the most common, distinctive actions or content that are not better represented by an app schema. Apple recommends keeping the set focused; the developer guidance commonly describes two to five high-value actions rather than a catalog of every intent.

The provider is static:

~~~swift
import AppIntents

struct TrailShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: OpenFavoritesIntent(),
            phrases: [
                "Open favorites in \(.applicationName)",
                "Show my saved trails in \(.applicationName)"
            ],
            shortTitle: "Open Favorites",
            systemImageName: "star"
        )
    }
}
~~~

This is a compile-oriented shape. The current SDK controls the exact phrase-token and parameter-presentation APIs. Include the app name in spoken phrases, use short verb-led labels, and provide complete dialogue for audio-only contexts. Do not market in the phrase or make the app pretend to be Siri.

When dynamic parameters or options change, use the documented AppShortcutsProvider update route for the selected SDK. Do not assume a newly changed entity or phrase becomes immediately ranked in every system surface. Verify the installed app, Shortcuts, Spotlight, and Siri paths separately.

Use app schemas for common domains when the feature fits the system’s known action/content model. App Shortcuts are better for unique product-specific capabilities. A schema can improve system understanding, but it does not remove current entity resolution, authorization, confirmation, or side-effect proof.

AppShortcutsProvider documentation also notes that Apple may extract anonymized App Shortcut data such as phrases, display values, and related intent metadata to improve machine-learning models. Treat phrases and display representations as public-facing product copy; do not put secrets, private record names, or sensitive context into them.

## Donations and discoverability

Donate an intent when a person performs the matching action directly in the app, not merely when Siri or Shortcuts invokes it. Donations are signals for system discovery and prediction; they are not an analytics replacement or a guarantee of ranking. Donate AppEntities to Spotlight with the safe content projection and delete them when the source is deleted, hidden, unauthorized, or the account changes.

The index coordinator should distinguish:

| State | Meaning |
| --- | --- |
| source-current | App store has current authorized record |
| projection-built | Safe AppEntity/attribute set exists |
| donation-accepted | System index accepted the operation |
| searchable-observed | Physical/system search returned the item |
| open-revalidated | OpenIntent resolved current authorized record |
| stale/withdrawn | App removed or invalidated the projection |

Do not report “discoverable” in app UI merely because an indexing API returned without error. System ranking and presentation are external evidence.

## Spotlight and indexed entities

For AppEntity-based Spotlight indexing:

1. adopt IndexedEntity for safe entities;
2. define only useful bounded properties and indexing keys;
3. donate through a named CSSearchableIndex;
4. provide an OpenIntent for each indexed entity type;
5. implement IndexedEntityQuery when the selected SDK supports the reindexing protocol;
6. repair all or requested entities when Spotlight asks;
7. delete entity IDs/domains when source records disappear or privacy scope changes;
8. re-resolve current state when a result opens.

Apple documents that CSSearchableIndex can index AppEntity values directly and can use named indexes with data-protection boundaries. Use a custom named index for production, not an implicit default with unclear ownership. Keep account/workspace deletion grouped by domain identifier.

For a large or frequently changing catalog, implement ShowInAppSearchResultsIntent as a route into the app’s native search UI. The system can use this route when a query has too many results for a compact result list. The app search screen must use the same query string and current data store, cancel stale searches, and preserve the system’s handoff intent.

CSUserQuery and CSSearchQuery each represent one query operation. When text changes, cancel the old query and create a new one. Debounce typing before starting work. A result batch, suggestion, or completed query is not a current record; resolve it again before opening or applying an action.

## Interactive snippets

Snippets are compact system-presented SwiftUI results for App Intents. A static snippet communicates an outcome. An interactive snippet can show a result or confirmation and provide small follow-up buttons or toggles backed by other AppIntents.

The key lifecycle is:

~~~text
AppIntent.perform
-> current observation or bounded mutation
-> static result or ShowsSnippetIntent
-> system invokes SnippetIntent.perform
-> SnippetIntent re-reads current state
-> system renders SwiftUI view
-> nested Button/Toggle invokes separate AppIntent
-> domain state changes
-> SnippetIntent.reload or system re-perform
-> view shows current state
~~~

Apple documents that the system can call a SnippetIntent multiple times. Keep render-time work side-effect free and avoid long-running tasks. Pass the smallest immutable identifier between intents, then fetch dynamic values from a shared dependency. If data changes while a snippet is visible, use SnippetIntent.reload when supported by the selected SDK.

Only SnippetIntent-backed interactive controls are expected to work as interactive snippet controls. Control Center-invoked app intents cannot display snippets. A snippet-only intent may require explicit discoverability configuration if the product wants it to appear in Shortcuts or Spotlight. Check the exact return type and discovery rules in the selected SDK.

Design snippets for both visual and spoken contexts. The HIG says the custom view should communicate the purpose visually instead of relying on repeated dialogue text. Every critical fact should still be present in the full AppIntent dialogue for people using audio-only devices.

Never put a domain mutation in SnippetIntent.perform. The rendering call may be repeated because of system lifecycle or user interaction. The nested mutation intent should re-check:

- current entity existence;
- account and authorization;
- current revision;
- idempotency key;
- destructive scope;
- user confirmation where required.

## Spotlight, snippets, and Live Activities are different

| Surface | Best for | Lifecycle |
| --- | --- | --- |
| Spotlight/App Shortcut | Discovery and short actions | System-ranked and user-invoked |
| Static snippet | One concise result | Re-rendered around an intent result |
| Interactive snippet | Compact review or follow-up action | Repeated SnippetIntent and nested intents |
| Live Activity | Ongoing time-sensitive progress | ActivityKit state/update/end lifecycle |
| Widget/control | Glanceable state and quick action | Timeline/control/provider budgets and system host |
| App scene | Full editing, complex search, or rich review | Foreground app navigation and scene lifecycle |

Do not force a long-running task into a snippet. Use ActivityKit when ongoing state needs a system surface, and open a scene when editing or confirmation cannot fit the system result.

## Visual Intelligence and onscreen context

Visual Intelligence can call an IntentValueQuery that takes a SemanticContentDescriptor. The descriptor may expose high-level labels and an optional captured pixel buffer. The app searches its own content and returns AppEntity values. Current Apple documentation says an app cannot contain more than one such descriptor-taking query; use a UnionValue result when multiple entity types must be returned.

The route is:

~~~text
system camera/screenshot context
-> SemanticContentDescriptor labels/pixelBuffer
-> one IntentValueQuery
-> bounded app-owned label/image/hybrid matching
-> AppEntity results
-> OpenIntent/current resolver
-> native detail or safe no-result
~~~

Labels are general high-level terms in the en_US locale and may change over time; they are not the actual name of a place/object and do not include synonyms. A pixel buffer is context input, not proof of identity or consent to retain. Release it after the match unless the product has a separate explicit retention policy.

The Visual Intelligence APIs are documented as preliminary/development-sensitive. Keep the query behind an availability and target/device gate. Maintain ordinary in-app search and navigation when the system route is unavailable.

## Onscreen entity context and scene routing

When the app wants Siri or Apple Intelligence to understand what a person is viewing, associate a current AppEntity with the relevant view or scene context. For custom-rendered content, use the documented AppEntityUIElement/AppEntityUIElementsContext route where supported. The entity ID must be current for the visible state and must resolve through the same authorization path as an opened search result.

For intents that need a particular SwiftUI/UIKit scene, use the target scene/AppIntent scene protocols and scene delegate route documented for the selected SDK. Keep:

- intent invocation;
- scene selection;
- navigation path;
- entity re-resolution;
- view-model hydration;
- mutation;

as separate stages. A deep link or TargetContentProvidingIntent can select a destination, but it does not grant access to protected content or prove that the record still exists.

## Transfer, ownership, and cross-device identity

If an AppEntity crosses a system workflow, use IntentValueRepresentation/Transferable with an explicit representation and redaction policy. OwnershipProvidingEntity, SyncableEntity, URLRepresentableEntity, or related contracts can add ownership, stable cross-device identity, or URL routing, but each has a separate proof boundary.

Do not transfer:

- credentials or signed requests;
- private database objects;
- raw model contexts;
- unbounded media;
- stale authorization tokens;
- a local ID that has no stable cross-device mapping.

At the receiving boundary, resolve the representation, current account, current record, and allowed operation again. A transfer payload is a request to resolve content, not a pre-authorized mutation.

## Process, concurrency, and execution targets

Many AppIntents can run in the background, and an App Intents extension can reduce foreground disruption. Some intents, such as opening content, require the app process and scene. Use supported modes and allowed execution targets only after mapping dependencies:

| Dependency | Safe background posture |
| --- | --- |
| Pure bounded calculation | Shared package or extension-safe service |
| Local database read | Actor/service that exists in the chosen process |
| Protected account data | Reauthorize in the chosen process |
| Foreground editor | OpenIntent/app scene route |
| Long operation | Progress/checkpoint/cancellation contract |
| Destructive mutation | Revision/idempotency/confirmation |
| Widget/control action | Short bounded action with extension-safe dependencies |

Do not place a SwiftUI view model, scene-only environment, or arbitrary model context in an App Intents extension. Share Sendable value types and a domain service with explicit storage ownership.

## Local AI boundary

Local model output can help resolve, rank, summarize, or propose, but system integration remains typed:

~~~text
system input/context
-> current entity/query result
-> bounded local model observation
-> typed proposal with source IDs and revision
-> user review when side effects matter
-> AppIntent mutation
-> current result/snippet/scene
~~~

Do not let a Foundation Models or Core ML response invent an AppEntity ID, bypass EntityQuery, or call a destructive AppIntent without the app-owned review boundary. Do not claim Apple Intelligence invoked the action just because a local model produced a similar phrase. Record which system surface, model, entity version, and user action produced the result.

## Liquid Glass and native system-surface design

The system owns the outer presentation for Siri, Spotlight, Shortcuts, snippets, and Action-button flows. The app owns its result view, snippet view, app scene, and any in-app guidance. Use native SwiftUI controls and current Liquid Glass guidance inside app-owned content. Do not reproduce Siri, Spotlight, or system settings with a fake glass shell.

For a snippet or in-app handoff:

- communicate the outcome visually without relying on dialogue;
- make the entity title and current status obvious;
- keep one primary action;
- expose source/freshness when an AI proposal is shown;
- use standard Button/Toggle semantics;
- keep a no-result, unauthorized, stale, and offline state;
- adapt to reduced transparency, increased contrast, Dynamic Type, and reduced motion.

An interaction that looks like an Apple surface is not automatically an Apple system integration. The proof must come from the system invocation and the target process.

## Privacy and data lifecycle

Search indexes, donations, shortcut phrases, snippets, onscreen context, and Visual Intelligence inputs may expose user-relevant information to system experiences. For every surface, record:

- what data is exposed;
- whether it is indexed, donated, transferred, or ephemeral;
- which account/workspace owns it;
- how deletion/expiry/authorization changes propagate;
- what is visible on a locked device;
- what is retained in logs;
- whether the pixel buffer or model input leaves the app/device;
- how the user disables or removes discoverability.

Use custom protected indexes for sensitive content where appropriate and reindex after privacy policy changes. Delete entity/index records when a source record is deleted, revoked, or no longer eligible. App Shortcuts metadata should be considered public product language.

## iOS 26 and availability boundary

Current Apple pages and HIG guidance are updated for iOS 26 and include a mixture of stable, beta, preliminary, deprecated, and platform-specific APIs. Record the selected Xcode SDK and deployment target for:

- IndexedEntityQuery, which Apple currently documents as beta;
- Visual Intelligence and SemanticContentDescriptor, which Apple currently describes as preliminary/development-sensitive;
- App schema macros and generated requirements;
- AppIntentSceneDelegate/scene-target routing;
- snippet result signatures and interactive controls;
- execution-target and package/extension APIs.

Use availability checks and adapter types. Do not make a preliminary Visual Intelligence or beta reindexing protocol a required launch path for the whole app. Compile a named target and verify the physical system surface.

## Proof boundary

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| AppIntent compiles | Type and selected SDK contract | Siri/Shortcuts invocation or correct side effect |
| AppEntity display | System-facing projection shape | Current authorization or entity existence |
| EntityQuery result | Resolver behavior for a test ID | System ranking or live system selection |
| AppShortcut provider | Declared phrase/metadata | Immediate ranking or natural-language coverage |
| Donation completion | App submitted a system signal | Search appearance or ranking |
| IndexedEntity/index call | Projection accepted by index API | Freshness, deletion, or physical Spotlight result |
| OpenIntent | Current route code exists | Correct scene/account/device handoff |
| Snippet preview | Visual composition | Repeated system rendering or interactive mutation |
| Snippet button | Nested intent wiring | Idempotency, persistence, or current revision |
| CSUserQuery result | App search query delivered data | Fresh authorization or complete catalog |
| Visual Intelligence descriptor | Query input shape | Object identity, matching quality, or system invocation |
| Local AI proposal | Model generated a bounded candidate | User approval or domain truth |
| Simulator run | Some app-side logic | Physical Siri/Spotlight/Action button/Visual Intelligence surface |
| Signed app/extension | Target artifact and entitlement | System discoverability, release metadata, or rollout |

The release packet should include a named target, SDK/deployment target, app/extension membership, intent/entity schema, index/donation/deletion fixture, system-surface run, current resolver trace, snippet repeat/interaction trace, privacy/accessibility run, physical-device evidence, archive/entitlement inspection, and TestFlight/App Store evidence where applicable.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [App entities](https://developer.apple.com/documentation/appintents/app-entities)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [Getting started with the App Intents framework](https://developer.apple.com/documentation/appintents/getting-started-with-the-app-intents-framework)
- [App Intents updates](https://developer.apple.com/documentation/updates/appintents/)
- [Accelerating app interactions with App Intents](https://developer.apple.com/documentation/appintents/acceleratingappinteractionswithappintents)
- [Adopting App Intents to support system experiences](https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [AppShortcutsProvider](https://developer.apple.com/documentation/appintents/appshortcutsprovider)
- [AppShortcut](https://developer.apple.com/documentation/appintents/appshortcut)
- [Donations and discovery](https://developer.apple.com/documentation/appintents/donations-and-discovery)
- [Displaying static and interactive snippets](https://developer.apple.com/documentation/appintents/displaying-static-and-interactive-snippets)
- [SnippetIntent](https://developer.apple.com/documentation/appintents/snippetintent)
- [Visual presentation](https://developer.apple.com/documentation/appintents/visual-presentation)
- [IndexedEntity](https://developer.apple.com/documentation/appintents/indexedentity)
- [IndexedEntityQuery](https://developer.apple.com/documentation/appintents/indexedentityquery)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [OpenIntent](https://developer.apple.com/documentation/appintents/openintent)
- [ShowInAppSearchResultsIntent](https://developer.apple.com/documentation/appintents/showinappsearchresultsintent)
- [IntentValueRepresentation](https://developer.apple.com/documentation/appintents/intentvaluerepresentation)
- [AppEntityUIElement](https://developer.apple.com/documentation/appintents/appentityuielement)
- [AppIntentSceneDelegate](https://developer.apple.com/documentation/appintents/appintentscenedelegate)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [CSSearchableIndex](https://developer.apple.com/documentation/corespotlight/cssearchableindex)
- [CSSearchQuery](https://developer.apple.com/documentation/corespotlight/cssearchquery)
- [CSUserQuery](https://developer.apple.com/documentation/corespotlight/csuserquery)
- [Building a search interface for your app](https://developer.apple.com/documentation/corespotlight/building-a-search-interface-for-your-app)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [IntentValueQuery](https://developer.apple.com/documentation/appintents/intentvaluequery)
- [App Shortcuts HIG](https://developer.apple.com/design/human-interface-guidelines/app-shortcuts)
- [Snippets HIG](https://developer.apple.com/design/human-interface-guidelines/snippets)
- [Siri HIG](https://developer.apple.com/design/human-interface-guidelines/siri)
- [Action button HIG](https://developer.apple.com/design/human-interface-guidelines/action-button)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
