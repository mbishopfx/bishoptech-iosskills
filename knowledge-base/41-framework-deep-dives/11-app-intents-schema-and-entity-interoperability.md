# App Intents schema, entity, and execution interoperability

## Scope

iOS 26 expands the App Intents route beyond isolated shortcuts and actions. The system can understand app capabilities more consistently when app intents, entities, and enums adopt the documented App schema domains. Stable entity identifiers can support cross-device continuation, ownership metadata can create better confirmation context for shared data, and transfer representations can bridge app entities to well-known system values.

This page covers the semantic contract behind Apple Intelligence and Siri integration:

    app-owned data and actions
      -> schema/entity/query contract
      -> system discovery, context, and parameter resolution
      -> optional cross-app value transfer or universal-link handoff
      -> explicit authorized AppIntent execution
      -> result, snippet, error, undo, or cancellation state

Schemas improve the system’s understanding of a capability. They do not give an app control over Apple Intelligence ranking, model choice, conversation wording, or device availability.

## The semantic layers

| Layer | Primary types | What it tells the system |
| --- | --- | --- |
| Action | AppIntent and an optional AppIntent schema | What the app can do and what parameters it needs |
| Entity | AppEntity, AppEnum, and an optional schema | What the app’s records or concepts mean |
| Query | EntityQuery, EntityStringQuery, EntityPropertyQuery, IndexedEntityQuery | How the system resolves a spoken, searched, or transferred value |
| Display | DisplayRepresentation and TypeDisplayRepresentation | How an entity is shown or described |
| Context | AppEntity associated with a view/activity or other visible content | What “this item” means in a system conversation |
| Transfer | Transferable and IntentValueRepresentation | How the entity becomes a known system value or crosses app boundaries |
| Identity | SyncableEntity, URLRepresentableEntity, stable identifiers | How an item remains addressable across devices and handoffs |
| Trust | OwnershipProvidingEntity and EntityOwnership | Whether the item is private, shared, public, or unknown |
| Relevance | RelevantEntities and AppEntityContext | Which media entities the system may suggest in a context |
| Runtime | IntentModes, LongRunningIntent, CancellableIntent, UndoableIntent | Where the action runs, how long it can work, how it stops, and how it reverses |

Keep these layers separate. A display title is not an authorization decision. A stable ID is not proof that the record still exists. A universal link is not proof that the app can open private content. A model or system suggestion is not a domain mutation.

## App schema domains

Use a documented schema when the app’s action or entity genuinely matches the domain’s purpose. The current Apple documentation exposes schemas for categories such as audio, calendar, camera, clock, files, mail, maps, messages, notes, phone, photos, reminders, system/in-app search, visual intelligence, and additional Shortcuts-specific domains.

Schema adoption is a contract:

1. Choose a domain whose semantics match the product.
2. Identify the intent, entity, and enum schemas that apply.
3. Apply the documented AppIntent, AppEntity, or AppEnum macro.
4. Add the required properties and parameters.
5. Implement the required result and query behavior.
6. Support the complete schema group when Apple’s documentation says the group is all-or-nothing.
7. Build and let Xcode report missing or incompatible schema requirements.
8. Test the resulting action with real system phrasing and the app’s manual route.

Do not adopt a schema only because its name sounds discoverable. A misleading schema gives the system the wrong semantic contract and can create unsafe invocation or confusing user expectations.

Illustrative schema shape:

~~~swift
@AppEntity(schema: .photos.album)
struct ProjectCollectionEntity: AppEntity {
    let id: UUID
    var name: String
    var creationDate: Date?
    var collectionType: CollectionType

    static let defaultQuery = ProjectCollectionQuery()

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)")
    }
}
~~~

The exact schema names, required properties, macro availability, and generated conformance should be checked in the selected SDK. This is a route sketch, not a claim that a project-specific entity matches the Photos domain.

## App entities and queries

Define an AppEntity for the subset of data a person genuinely needs outside the app. Include only properties that help the system resolve, display, or operate on the item.

An entity route normally has:

- a stable ID;
- a privacy-reviewed display representation;
- a type display representation;
- properties that are safe and useful for resolution;
- a default query;
- identifier lookup through EntityQuery;
- optional string/property/indexed queries;
- optional transfer or URL representation;
- an authorization check at the domain boundary.

EntityQuery is not merely a local array filter. Apple Intelligence, Siri, and Shortcuts may pass known identifiers, natural language, or transferred system values. In entities(for:), look up current data and omit records that no longer exist. Do not manufacture a deleted record from a stale cache just to satisfy a query.

Use specialized query types when their contract is useful:

| Query | Use |
| --- | --- |
| EntityQuery | Resolve known IDs and suggested entities |
| EntityStringQuery | Resolve arbitrary string input |
| EntityPropertyQuery | Match one or more declared properties |
| IndexedEntityQuery | Coordinate entity resolution with Spotlight indexing |
| UniqueAppEntityQuery | Resolve the one singleton entity, such as app settings |
| IntentValueQuery | Provide values to the system for specialized intent-value resolution, such as visual intelligence |

Set query execution targets when the query must run in a particular process. A query should not require a UI scene simply because its entity is displayed in a system surface.

## Stable identity across devices

Adopt SyncableEntity only when the entity’s identifier is consistent across the person’s devices. A server-issued UUID can already satisfy the requirement. If the app has separate local and stable identifiers, use SyncableEntityIdentifier with the documented local/stable pairing.

Stable identity enables continuity, not automatic synchronization. The receiving device still needs:

- the same account or access scope;
- a query that can resolve the stable ID;
- current data or a truthful unavailable state;
- compatible app version/schema;
- a privacy decision for the destination device;
- a fallback when the record was deleted or access changed.

Never expose a local database row number as a cross-device identity. Never assume a stable ID authorizes a read or write.

## Ownership and shared data

Conform an entity to OwnershipProvidingEntity when its sharing state matters to destructive or sensitive actions. Return EntityOwnership values that describe public, shared, unknown, or unmarked state according to the current documentation.

Ownership metadata helps the system request additional confirmation with relevant context for shared or public entities. It does not replace app authorization:

    entity ownership metadata
      -> system may request contextual confirmation
      -> AppIntent re-checks account, permission, current ownership, and version
      -> domain operation applies or rejects

Refresh ownership before a high-consequence mutation. If an entity changed from private to shared or public since it was resolved, do not use a stale ownership flag to skip review. If ownership is unknown, choose the safer confirmation or handoff.

## Transferable system values

App entities often represent a known system concept such as a person, place, file, or media item. Adopt Transferable and add IntentValueRepresentation when bidirectional conversion is safe and meaningful.

Choose the direction deliberately:

| Direction | Example | Risk to address |
| --- | --- | --- |
| Export only | App trail to PlaceDescriptor | Receiving app gets a valid location but not app-private notes |
| Import and export | ContactEntity and IntentPerson | Validate the system identifier and account scope on import |
| No transfer | Highly private or app-specific record | Keep the route in the app or use a redacted entity |

The transfer representation is a conversion boundary. Treat imported system values as untrusted, re-resolve them through the app’s current store, and reject values that cannot be mapped safely.

Do not put credentials, access tokens, raw model context, hidden metadata, or unbounded private text in a transferable representation.

## Onscreen context

The app’s visible content is private to the app, so system intelligence cannot infer it automatically. Associate an AppEntity with the relevant view or user activity when the product wants people to refer to onscreen content conversationally, such as “this project” or “that image.”

The context route should be:

    visible app state
      -> privacy-reviewed AppEntity
      -> current activity/view association
      -> system conversation uses the entity as context
      -> AppIntent/query re-resolves current truth

The association is a cue, not a durable lock on the record. If the view becomes stale, the account changes, or the record is deleted, the next query must return an honest failure or handoff.

## Relevant entities

RelevantEntities is a system donation route for media-related content such as songs, albums, artists, playlists, radio stations, and podcasts. Provide one current set of suggestions for a documented context. Each update replaces the previous set for that context, and the app can clear or remove donations.

Use relevance only when the suggestions represent a genuine user benefit:

- derive candidates from current local or authorized data;
- keep the set small and explainable;
- use the correct AppEntity type;
- replace the set when the user’s context changes;
- remove it on sign-out, privacy change, or no-suggestion state;
- record the donation context and timestamp for debugging;
- do not treat a donation as a guaranteed display or playback.

The system may expire suggestions. Relevance donation is not a recommendation guarantee, ranking control, or source of truth.

## Singleton and union values

Use UniqueAppEntity for a concept that has exactly one value, such as app settings. Use UniqueAppEntityQuery and uniqueEntity() to provide that value. This is safer than inventing a “default settings record” that can accidentally produce multiple choices.

Use UnionValue when one parameter legitimately accepts one of several predefined intent-value cases. Each case must have clear semantics, safe resolution, and localized display. Do not use a union to hide an ambiguous API or to accept arbitrary untyped model output.

The union route should still have:

- finite and documented cases;
- deterministic case resolution;
- a clear parameter summary;
- authorization per case;
- a failure path for unsupported input;
- test coverage for each case and an unknown/future case.

## Universal-link continuity

URLRepresentableIntent and URLRepresentableEntity can give an App Intent or entity a universal-link representation. Use a real universal link, not a custom URL scheme. The destination must still validate authentication, authorization, account, record existence, and the action’s safety.

Universal links are useful for:

- continuing a task on another device;
- sharing a specific entity;
- opening a precise app destination;
- giving Siri or Shortcuts a stable navigation result;
- recording a pending operation that can resume in the full app.

Do not put private data in the URL. Prefer an opaque stable identifier and resolve the current record after the app receives the link.

## Runtime mode and process

Use supportedModes to declare whether an intent can run in the background, requires the foreground, or can transition using a documented foreground mode. Consult systemContext.currentMode in perform() when behavior differs.

Choose the smallest runtime contract:

| Work | Route |
| --- | --- |
| Short local mutation | Background-capable AppIntent with no scene dependency |
| Needs app-only UI | Foreground mode or explicit continueInForeground route |
| Long file/model/data task | LongRunningIntent plus progress and cancellation |
| Reversible domain command | UndoableIntent with a registered inverse |
| Cleanup-sensitive task | CancellableIntent with prompt cancellation handling |

LongRunningIntent does not make arbitrary work unlimited. Report progress regularly, check Task cancellation, checkpoint resumable work, and record partial state. CancellableIntent gives cleanup time, but the process can still be suspended soon after cancellation on mobile platforms.

UndoableIntent exposes a suitable UndoManager when available. Register the inverse operation; the AppIntent should not call undo() or redo() itself. If no undo manager is available, the domain still needs a safe result and recovery path.

## Errors as system vocabulary

Use documented AppIntentError cases when they accurately describe the recovery:

- PermissionRequired when the person must grant a protected capability;
- UserActionRequired when the person must complete an app/system step;
- Unrecoverable when the operation cannot be retried safely.

An error should tell the system and the person what to do next without leaking private state. Do not throw a generic error for a missing photo, denied location, signed-out account, or unavailable model when a more precise route exists.

## AI boundary

App schema domains and entity representations are structured contracts for Apple Intelligence and Siri. They are not prompts to a model and they do not let the app call or control Apple Intelligence directly.

Keep this boundary:

    app schema/entity metadata -> system discovery and context
    on-device model proposal -> app-owned typed validation/review
    AppIntent -> explicit, authorized domain operation

If the app has its own Foundation Models workflow, keep its prompt/context and model availability state inside the app. Use App Intents to expose a bounded action or entity after the app has defined a safe contract.

## Integration checklist

- [ ] The selected schema domain matches the actual product capability.
- [ ] Required schema groups are complete.
- [ ] AppEntity properties are minimal, localized, and privacy-reviewed.
- [ ] EntityQuery resolves current IDs and omits deleted records.
- [ ] SyncableEntity is used only for identifiers stable across devices.
- [ ] OwnershipProvidingEntity describes current sharing state.
- [ ] Transferable import/export is typed, bounded, and re-authorized.
- [ ] Ongoing onscreen context is associated only with safe entities.
- [ ] RelevantEntities donations are current, replaceable, and clearable.
- [ ] UniqueAppEntity or UnionValue is used only when its semantics are exact.
- [ ] Universal links use stable opaque identifiers and revalidate access.
- [ ] supportedModes, process targets, progress, cancellation, and undo are explicit.
- [ ] AppIntent errors have usable recovery semantics.
- [ ] Apple Intelligence and Siri claims are limited to tested configurations.
- [ ] Compile, system, physical-device, privacy, accessibility, and release evidence are attached.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents)
- [App intents](https://developer.apple.com/documentation/appintents/app-intents)
- [App schema domains](https://developer.apple.com/documentation/appintents/app-schema-domains)
- [App schema base types](https://developer.apple.com/documentation/appintents/app-schema-base-types)
- [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [Providing contextual cues to Apple Intelligence and Siri](https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [Defining app entities for your custom data types](https://developer.apple.com/documentation/appintents/defining-app-entities-for-your-custom-data-types)
- [Entity queries](https://developer.apple.com/documentation/appintents/entity-queries)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [SyncableEntity](https://developer.apple.com/documentation/appintents/syncableentity)
- [OwnershipProvidingEntity](https://developer.apple.com/documentation/appintents/ownershipprovidingentity)
- [EntityOwnership](https://developer.apple.com/documentation/appintents/entityownership)
- [IntentValueRepresentation](https://developer.apple.com/documentation/appintents/intentvaluerepresentation)
- [RelevantEntities](https://developer.apple.com/documentation/appintents/relevantentities)
- [UniqueAppEntity](https://developer.apple.com/documentation/appintents/uniqueappentity)
- [UniqueAppEntityQuery](https://developer.apple.com/documentation/appintents/uniqueappentityquery)
- [UnionValue](https://developer.apple.com/documentation/appintents/unionvalue%28%29)
- [URLRepresentableIntent](https://developer.apple.com/documentation/appintents/urlrepresentableintent)
- [URLRepresentableEntity](https://developer.apple.com/documentation/appintents/urlrepresentableentity)
- [Intent modes](https://developer.apple.com/documentation/appintents/intentmodes)
- [AppIntent supported modes](https://developer.apple.com/documentation/appintents/appintent/supportedmodes)
- [LongRunningIntent](https://developer.apple.com/documentation/appintents/longrunningintent)
- [CancellableIntent](https://developer.apple.com/documentation/appintents/cancellableintent)
- [UndoableIntent](https://developer.apple.com/documentation/appintents/undoableintent)
- [AppIntent errors](https://developer.apple.com/documentation/appintents/appintenterror)
- [App Intent updates](https://developer.apple.com/documentation/updates/appintents)
