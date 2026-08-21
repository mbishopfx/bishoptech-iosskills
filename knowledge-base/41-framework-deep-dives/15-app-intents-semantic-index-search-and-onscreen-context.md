# App Intents semantic indexing, in-app search, onscreen context, and cross-device identity

## Scope

This page documents the Apple route for making an app's own records discoverable
to Spotlight, Siri, Apple Intelligence, in-app system search, and onscreen
context. It is the companion to the Visual Intelligence route. Visual
Intelligence starts with a system-provided scene descriptor; this route starts
with
the app's durable entities, their searchable metadata, the current UI context,
or a search string supplied by Siri.

The core route is:

    domain record
      -> AppEntity projection
      -> IndexedEntity metadata
      -> named Core Spotlight index
      -> Spotlight and system semantic search
      -> AppEntity re-resolution
      -> OpenIntent or app-owned detail

The large-catalog continuation is:

    Siri or system search string
      -> system.searchInApp
      -> ShowInAppSearchResultsIntent
      -> app-owned search state
      -> native search results UI

The onscreen route is:

    visible SwiftUI/UIKit/custom-rendered entity
      -> entity identifier or AppEntityUIElement
      -> system context
      -> Siri, Apple Intelligence, or a follow-up App Intent
      -> current entity query
      -> authorized app action or detail

The cross-device route is:

    stable entity identity
      -> SyncableEntity
      -> system continuation on another device
      -> local resolution in that device's current account/store
      -> authorization check
      -> detail or honest unavailable state

These are related but not interchangeable. Indexing does not replace an
in-app search screen. An onscreen annotation does not grant permission to read a
record. A stable identifier does not prove that the second device is signed in
to the same account or is allowed to open the record.

## Version and documentation boundary

Apple's App Intents, Spotlight, and Apple Intelligence documentation is
version-sensitive. Some pages in the current documentation set are labeled
beta or preliminary, and some WWDC material describes APIs for a later release.
Use the following labels in this knowledge base:

| Label | Meaning | Implementation treatment |
| --- | --- | --- |
| iOS 26 documented | The selected iOS 26 SDK exposes the symbol and its documentation applies | Compile in the named SDK and gate by availability |
| iOS 26 beta documented | Apple documents the route but marks it beta/preliminary | Isolate behind a small adapter and re-check final SDK spelling |
| Later-release material | A session or page explicitly describes a later OS/release | Keep as a forward-looking note; do not make it an iOS 26 requirement |
| Inference | A design recommendation derived from several Apple contracts | Label the recommendation and test it in the target |
| Local behavior | An observation from a physical-device or archive run | Record OS, device, build, account, and settings |

Do not convert a WWDC chapter title into an availability claim. The compiler,
the SDK interface, the documentation page for the selected OS, and a physical
device are separate evidence sources.

## Capability map

| Goal | Primary Apple contract | App-owned responsibility |
| --- | --- | --- |
| Make records discoverable in Spotlight | IndexedEntity and entity indexing | Stable projection, safe metadata, freshness |
| Let Apple Intelligence use records | App entity indexing and donations | Authorization, truthful representations, open route |
| Search records already indexed | Spotlight and App Intents entity queries | Resolve current records and filter unavailable data |
| Search a large or fast-changing catalog | ShowInAppSearchResultsIntent and system.searchInApp | Route the same query string into the app's search UI |
| Give the system context about one visible item | SwiftUI appEntityIdentifier | Keep identifier current while the view is visible |
| Give context about list selections | appEntityIdentifier(forSelectionType:identifier:) | Stable selection IDs and accessible row semantics |
| Annotate custom drawing | appEntityUIElements and AppEntityUIElement | Bounds, state, subelements, hit target, privacy |
| Resume an entity on another device | SyncableEntity and SyncableEntityIdentifier | Stable identity plus local authorization and re-resolution |
| Open a result | OpenIntent | Current navigation and no hidden irreversible side effect |

## IndexedEntity: the semantic-index projection

IndexedEntity is the App Intents entity capability for putting an AppEntity into
Spotlight. Apple describes it as making an entity discoverable by Spotlight and
Apple Intelligence, with indexable metadata supplied through the entity
projection.

Treat an IndexedEntity as a search document, not as a serialized database row.
The projection should contain:

- a stable identifier;
- a localized type display representation;
- a concise title;
- a useful subtitle or context string;
- metadata that helps lexical and semantic retrieval;
- an OpenIntent path;
- an entity query that can re-resolve the current record.

The system may display or use the indexed fields outside the app. Do not index
private notes, credentials, secrets, raw model prompts, hidden moderation
signals, or data that the user has not authorized for system discovery.

The identifier is the join key between the index and the current app store. The
index can be stale; the app must treat the identifier as a request to resolve
current truth.

### Indexable fields

Apple's App Intents documentation describes property wrappers for defining
indexed entity metadata. The exact SDK spelling and supported value types must
be compiled against the target SDK, but the conceptual choices are stable:

| Declaration family | Use it for | Review questions |
| --- | --- | --- |
| Property | Stored entity data that is safe to index | Is it localized, bounded, and useful for retrieval? |
| ComputedProperty | Derived metadata available without an expensive fetch | Is computation deterministic and fast? |
| DeferredProperty | Metadata that can be obtained later or on demand | Is the fallback safe if the property is unavailable? |
| indexingKey | A key used to identify the semantic field | Does the key remain stable between releases? |
| customIndexingKey | A custom mapping when the default field is not the desired schema | Is the mapping documented and migration-safe? |

Do not expose a field simply because it exists in the model. Index only fields
that improve discovery or provide context in the system result. Keep the
metadata bounded so a system query does not become a hidden database export.

A useful projection for a saved place might include a name, city, category, and
short public description. A private journal might include only a title and
user-selected tag, or it might opt out entirely. A health-related app needs an
even higher bar: avoid indexing sensitive content unless the user explicitly
expects the system surface and the product's privacy contract supports it.

### Display representation versus index metadata

DisplayRepresentation is the compact presentation used when the system needs
to show an entity. Index metadata is retrieval-oriented. They should overlap,
but they are not identical.

Use the display representation for:

- the shortest useful title;
- a concise subtitle;
- a safe thumbnail or symbol;
- a localized type name.

Use index metadata for:

- search terms and structured context that improve retrieval;
- bounded categories or relationships;
- fields needed for semantic matching;
- metadata that remains safe when surfaced by the system.

Do not put every searchable field into the subtitle. A long subtitle harms
scannability, localization, accessibility, and system presentation. When the
system asks for only a textual representation, return the smallest useful
representation and avoid loading an image or a full record.

Apple documents entity-query support for requesting display representations.
Treat that path as a performance boundary: a system query may ask for a textual
component without needing the full entity or its media.

## Donation and index ownership

Use a named CSSearchableIndex for production indexing. A named index gives the
app an explicit ownership boundary and makes the index lifecycle easier to
reason about. Apple documentation cautions against relying on the default
index except for prototyping.

The app should own a small indexing coordinator that:

1. receives domain create/update/delete events;
2. converts current records into safe IndexedEntity projections;
3. donates or updates entities in the named index;
4. removes deleted or withdrawn entities;
5. schedules a repair/reindex path;
6. records privacy-safe diagnostics and counts.

The coordinator must not be the source of current authorization. It writes
discoverability metadata; the entity query and OpenIntent perform current
resolution and authorization.

### Initial indexing

Initial indexing is a bounded import from the current authorized store.

Use these rules:

- index only records the user can currently discover;
- process in chunks;
- make the operation cancellable;
- avoid blocking first launch;
- persist a schema/version marker;
- record the last successful checkpoint;
- retry transient failures with backoff;
- never treat a partial import as a complete index;
- expose a repair action in diagnostics or debug builds.

If the app has many records, index the most useful recent or user-pinned data
first, then continue in the background within the platform's execution limits.
Do not promise instant index completeness to the UI.

### Incremental updates

For an update, re-donate the same stable entity identifier with the latest
safe metadata. A changed representation should replace the old representation
rather than create a duplicate identity.

Trigger updates for:

- title or display context changes;
- category or searchable field changes;
- thumbnail changes if the thumbnail is indexed or displayed;
- ownership or sharing changes;
- archive/unarchive;
- account scope changes;
- privacy setting changes.

If the record becomes unavailable, remove it or make the query refuse it
according to the product's deletion policy. A stale system card should never
become an authorization bypass.

### Deletes and withdrawal

Delete from the named index when:

- a record is deleted;
- a user signs out and the entity is account-private;
- a share is revoked;
- the user disables system discovery;
- the record becomes ineligible for indexing;
- the app's index schema can no longer represent it safely.

Keep a repair path for identifiers that disappeared from the store. It is safer
to remove a possibly stale identifier and re-add current records than to leave
private records discoverable indefinitely.

### Reindexing

IndexedEntityQuery provides a reindexing contract for Spotlight. Apple documents
methods for reindexing a subset of entity IDs and for reindexing all entities,
with a CSSearchableIndexDescription supplied by the system.

Use reindexing to recover from:

- a changed indexing schema;
- an app update that changes safe fields;
- a repaired local database;
- a failed migration;
- a user account transition;
- a system request for missing or stale items.

The reindex method should be deterministic and bounded. For a subset request,
resolve only the requested IDs and skip records that no longer exist or are no
longer authorized. For an all-entities request, use a streaming/chunked
enumeration and make the index description accurately describe the current
entity schema.

Reindexing is not a reason to expose an entire private database. Filter by
current account and indexing preference before converting records to entities.

## Search semantics and retrieval policy

Core Spotlight provides lexical and semantic search behavior for indexed
content. The app supplies the searchable representation; the system owns the
ranking surface and may combine the content with other system context.

Design metadata for meaning, not keyword stuffing:

- prefer natural, user-facing names;
- include stable category/context fields;
- use the user's locale;
- avoid repeating the same token across many fields;
- keep synonyms in the domain projection only when they are truthful;
- do not add invented terms to manipulate ranking;
- use a versioned projection when a field mapping changes.

Search results should be re-resolved through the current EntityQuery or OpenIntent
path. Search ranking is a suggestion, not proof of current state.

### When indexing is the right route

Indexing is a good fit when:

- records are durable enough to maintain;
- retrieval should work from Spotlight or Siri;
- the search metadata is safe to expose;
- the record has a stable identity;
- the app can repair stale data;
- the result can open into the app.

### When in-app search is the right route

Use in-app search continuation when:

- the catalog is too large or too dynamic to fully index;
- the app's query needs server-backed or local ranking;
- the user needs facets, filters, previews, or grouped results;
- result visibility depends on live authorization;
- the system should hand the same query string to the app;
- the app needs to show more than the bounded system result list.

Indexed entities and in-app search can coexist. Index a safe subset or a set of
entry points, then use the full in-app route for the complete result set.

## system.searchInApp and ShowInAppSearchResultsIntent

Apple documents the system.searchInApp schema for routing a Siri search to an
app's own search experience. The current documentation replaces the older
system.search schema with system.searchInApp. Treat the older schema as
deprecated/legacy and verify the selected SDK's generated requirements.

ShowInAppSearchResultsIntent is a specialized App Intent for displaying
search results in the app. The route includes:

- StringSearchCriteria for the query text;
- StringSearchScope for the supported areas of the app;
- a localized scope display representation;
- an implementation of the app-owned result presentation;
- foreground execution in the main app target.

Important boundaries from Apple's documentation:

- it must run from the main app, not an app extension;
- if declared in a shared framework, allowed execution targets must include the
  app;
- the system schema adds the expected search support;
- the app should receive the same search string that Siri used;
- the app owns how the result list, filters, empty state, and detail route look.

The system does not require the app to put every record in Spotlight before it
can provide an in-app search route. This makes system.searchInApp useful for a
large, server-backed, private, or fast-changing catalog.

### Search scope design

Define scopes that a user can understand:

- All items;
- Saved places;
- Documents;
- Projects;
- Messages;
- Settings or actions, if the product has them.

A scope is not a database table name. It is a user-facing boundary for search.
Keep the scope list short, localized, and stable across versions. If a scope is
not available for the current account, omit it or return a truthful empty route.

A query string should remain a query string. Do not interpret Siri's text as
permission to perform a mutation, send a message, or purchase. Search is
read-oriented; actions require their own explicit intent and authorization.

### App-owned continuation

When the system invokes the intent:

1. validate the criteria;
2. resolve the current account and search scope;
3. create navigation/search state in the app;
4. run the app's ordinary search service;
5. render a native searchable result surface;
6. preserve accessibility focus and back navigation;
7. show a clear empty, offline, or authorization state;
8. do not log private query text by default.

The handoff should feel like a continuation, not a second app. Use the same
search service and entity resolver that the rest of the app uses.

## IntentValueQuery versus IndexedEntityQuery

These protocols solve different retrieval boundaries.

| Protocol | Input/output shape | Best use |
| --- | --- | --- |
| IntentValueQuery | System-provided value or semantic descriptor to bounded entity values | Visual Intelligence or a typed system query |
| EntityQuery | IDs and suggestions to current AppEntity values | Re-resolving entities and providing suggestions |
| IndexedEntityQuery | Reindex subset/all requests plus index description | Spotlight index repair and freshness |
| ShowInAppSearchResultsIntent | Search criteria and scope to app-owned UI | Large/dynamic/full search continuation |

Do not put a full database query into a small system query if the system only
needs a handful of values. Conversely, do not index sensitive, rapidly changing
records merely to avoid implementing an in-app search route.

## Onscreen context: annotating ordinary SwiftUI

Apple documents appEntityIdentifier modifiers for associating a SwiftUI view with
an AppEntity. The simplest form associates one view with an entity identifier.
The selection-type form is useful for lists where the system needs to understand
the type of item people are scrolling through or selecting.

Use the annotation at the smallest stable view boundary:

- attach the entity identifier to the row or card that represents the entity;
- keep the identifier equal to the current domain identity;
- remove the annotation when the view no longer represents that entity;
- avoid annotating a decorative container with a misleading entity;
- ensure VoiceOver can identify the same row meaningfully;
- use the selection-type form for a typed List selection route when appropriate.

The innermost appEntityIdentifier modifier wins when multiple modifiers apply.
That makes modifier placement part of the correctness contract.

Onscreen context is not a screenshot export. It is a semantic cue. It should
not cause the app to retain screen images or expose unrelated rows.

### Lists and collections

For a List or collection:

- give each row a unique current entity ID;
- make the row's label, value, and accessibility label agree;
- annotate the row rather than the whole list when possible;
- test scrolling, insertion, deletion, filtering, and selection;
- verify that a reused cell does not retain the previous ID;
- clear the annotation during loading or placeholder state;
- test empty and authorization-filtered lists.

A cell reuse bug can cause the system to associate the wrong entity with a
visible row. The physical test should scroll, update, and reopen context rather
than checking only the first row.

UIKit table and collection views have corresponding App Intents data-source
routes documented by Apple. Use those contracts when the screen is UIKit-owned;
do not mix a SwiftUI modifier assumption into a UIKit cell implementation.

### Custom drawing and AppEntityUIElement

Canvas, Core Animation, maps, diagrams, and custom rendering do not always have
a normal SwiftUI view to annotate. Apple documents AppEntityUIElement for
wrapping an entity with bounds, state, and subelements.

For custom-rendered content, define:

- the entity's stable ID;
- the element bounds in the documented coordinate space;
- a useful state such as selected, expanded, or available;
- subelements for nested or overlapping entities;
- an accessible name/value for each interactive element;
- updates when the rendering transform, zoom, or data changes.

Bounds are context, not authorization. A custom element should not include raw
private data in its state payload. If an element is not visible, selected, or
current, remove it from the UI-element graph.

Hit-testing and accessibility must agree with the element bounds. A system
surface should not be able to identify a tiny visual mark that the user cannot
find or activate.

## Entity identity across devices

SyncableEntity tells the system that an entity can be identified consistently
across devices. Use it only when the identifier contract is real.

Good stable identities include:

- a server UUID whose meaning is stable;
- a CloudKit record identifier designed for cross-device resolution;
- a product-defined stable ID that survives device replacement;
- a SyncableEntityIdentifier with a stable component.

A device-local database integer, array offset, UUID generated on first install,
or ephemeral cache key is not a cross-device identity.

### Local and stable components

SyncableEntityIdentifier can represent a local identity and a stable identity.
Use the local component for current-device lookup when that is all the local
store understands. Use the stable component when the same record must be
resolved on another device.

Make the mapping explicit:

    stable record ID
      -> account/server/CloudKit lookup
      -> current-device local record ID
      -> current authorization
      -> AppEntity

If a stable ID is absent, return a local-only entity and do not claim that Siri
can continue it across devices.

### Stable does not mean authorized

A stable identifier can identify a record without granting access. On another
device:

1. resolve the signed-in account;
2. determine whether the app's data store is ready;
3. map the stable ID to a current local record;
4. check ownership, sharing, and deletion;
5. return the entity or an unavailable state;
6. offer sign-in, account selection, or app search as recovery.

Do not show a private title in an error message just because the stable ID was
recognized. Keep the unavailable state privacy-safe.

### Cross-device proof

A same-account unit test proves only the mapping logic. Physical proof requires:

- two supported devices or a supported system continuation path;
- the same account and data state;
- a record created or changed on one device;
- the system invocation on the second device;
- current app resolution and open navigation;
- a sign-out or permission-revocation negative test.

Record both devices, OS builds, app build, account state, network state, and
whether the test used a production-like archive.

## Process, target, and execution boundaries

App Intents can execute in a process or target that is not the same as the
foreground SwiftUI scene. Plan for:

- app extensions not having access to the main navigation stack;
- entity queries running without the expected UI environment;
- a shared framework needing explicit allowed execution targets;
- background or system invocation not having a visible window;
- concurrency and cancellation;
- a store that is still opening or migrating;
- no network or a constrained network path.

Use an actor-safe domain service with explicit dependencies. Keep UI routing in a
main-actor handoff after the system invokes the app-owned intent. Do not access a
SwiftUI view model as a hidden global from an entity query.

When an intent must open the main app, make the execution target and supported
mode explicit in the selected SDK. A successful unit-test perform call does not
prove that Siri, Spotlight, or the system can launch the right target.

## Privacy and data minimization

Treat system discovery as a new data surface.

Document for each entity:

| Question | Required answer |
| --- | --- |
| What is indexed? | Exact fields and locale |
| Who can discover it? | Account, sharing, or device scope |
| When is it removed? | Delete, sign-out, revocation, privacy switch |
| What is shown in a card? | Title, subtitle, image, and type |
| What is logged? | Counts/diagnostics, not raw query or private fields |
| What happens offline? | Local safe result, empty result, or honest unavailable |
| What happens after migration? | Reindex and schema version policy |
| What happens on another device? | Stable-ID resolution and authorization |

Do not treat the user saying a search term aloud as consent to upload or retain
it. Use local matching where practical. If the app needs a server search, state
the network and privacy behavior in the product contract and implement an
offline failure path.

## Native Liquid Glass and system-surface design

Semantic search results should look like a native app continuation:

- use the platform search field and navigation patterns;
- keep the hierarchy readable before adding any glass effect;
- let standard SwiftUI controls receive the system treatment;
- use glass as a focused control/surface layer, not as a background texture;
- place toolbar actions in the system toolbar;
- keep search suggestions, result rows, and empty states accessible in high
  contrast and Dynamic Type;
- preserve Reduce Motion and reduced-transparency behavior;
- do not imitate private system UI or make a system result card look like an
  Apple-owned surface.

The handoff from Spotlight/Siri should land on a clear app-owned title, query
state, scope, and back path. A glass search bar over a complex background is
not a substitute for contrast, hierarchy, or readable result content.

For custom onscreen entity overlays, avoid floating labels that obscure the
underlying content. Use selection state, clear hit targets, and accessible
labels. The system should be able to reason about the entity without the app
turning every visual element into a decorative glass chip.

## Failure modes and recovery

| Failure | Safe behavior | Do not do |
| --- | --- | --- |
| Index is stale | Re-resolve by ID and repair index | Trust the old title as current truth |
| Entity deleted | Omit or show unavailable with recovery | Open a different record by fuzzy match |
| User signed out | Remove private index entries and require sign-in | Leak the old subtitle |
| Search scope unavailable | Omit/empty with explanation | Pretend all records are searchable |
| Entity query times out | Return bounded error/empty state | Block the system surface indefinitely |
| Custom element moved | Update bounds/ID graph | Leave stale overlays active |
| Stable ID not resolvable | Ask for account/app search | Treat stable ID as permission |
| App extension invoked | Use extension-safe route or fail clearly | Access main window singleton |
| Query is sensitive | Minimize/log nothing | Upload or persist by default |
| Index schema changed | Reindex with version marker | Keep mixed stale metadata silently |

## Implementation checklist

Before calling the route implemented:

- [ ] The selected SDK and OS version are written down.
- [ ] Every IndexedEntity field has a privacy and localization review.
- [ ] The entity ID is unique and its local/stable behavior is documented.
- [ ] The named CSSearchableIndex has a lifecycle owner.
- [ ] Initial, incremental, delete, and repair indexing paths exist.
- [ ] IndexedEntityQuery can reindex a requested subset and all records.
- [ ] EntityQuery re-resolves current authorized records.
- [ ] OpenIntent exists for every system-selectable entity type.
- [ ] system.searchInApp is used instead of deprecated system.search where the
      selected SDK documents it.
- [ ] ShowInAppSearchResultsIntent receives a bounded, validated search string.
- [ ] In-app search preserves scope, accessibility focus, and back navigation.
- [ ] SwiftUI list/card annotations are current during updates and reuse.
- [ ] Custom AppEntityUIElements have correct bounds and accessible labels.
- [ ] SyncableEntity is used only with a genuine stable identity.
- [ ] Cross-device resolution checks account and authorization.
- [ ] Indexing and search work with network unavailable where promised.
- [ ] Physical Spotlight/Siri and app-handoff tests are recorded.
- [ ] Archive, entitlements, target membership, localization, and privacy
      configuration are inspected.
- [ ] The release build is not called complete from simulator evidence alone.

## Sources

- https://developer.apple.com/documentation/appintents/indexedentity
- https://developer.apple.com/documentation/appintents/indexedentityquery
- https://developer.apple.com/documentation/appintents/spotlight
- https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight
- https://developer.apple.com/documentation/appintents/app-entities
- https://developer.apple.com/documentation/appintents/showinappsearchresultsintent
- https://developer.apple.com/documentation/appintents/appschema/systemintent/searchinapp
- https://developer.apple.com/documentation/appintents/appschema/systemintent/search
- https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri
- https://developer.apple.com/documentation/appintents/appentityuielement
- https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28_%3A%29
- https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28forselectiontype%3Aidentifier%3A%29
- https://developer.apple.com/documentation/swiftui/view/appentityuielements%28_%3A%29
- https://developer.apple.com/documentation/appintents/syncableentity
- https://developer.apple.com/documentation/appintents/syncableentityidentifier
- https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences
- https://developer.apple.com/documentation/appintents/defining-app-entities-for-your-custom-data-types
- https://developer.apple.com/documentation/appintents/donating-your-apps-data-and-actions-to-the-system
- https://developer.apple.com/documentation/appintents/donations-and-discovery
- https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- https://developer.apple.com/documentation/swiftui/navigation
- https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences
