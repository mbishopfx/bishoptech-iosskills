# Apple Intelligence schema and entity route

## Outcome

Make a real app capability understandable to Apple Intelligence, Siri, Shortcuts, Spotlight, visual intelligence, and cross-device handoff while keeping entity identity, account authorization, ownership, model proposals, and side effects under app control.

This route is for products with meaningful records or actions such as notes, projects, media, reminders, locations, files, messages, or settings. It is not a discoverability checklist for every model object in the database.

## Route shape

    user-owned domain record
      -> privacy-reviewed AppEntity
      -> query and display representation
      -> optional schema domain
      -> optional Spotlight/context/transfer/URL representation
      -> system resolves current entity
      -> ownership and authorization check
      -> AppIntent runs in declared mode/target
      -> result, snippet, error, undo, or full-app handoff

For an AI-assisted product:

    capture/input -> on-device proposal -> typed validation
      -> entity mapping review -> AppIntent approval
      -> durable domain truth -> system projection

## Preflight decisions

- Which user outcome deserves system discovery?
- Which entity type is safe and useful outside the app?
- Which domain schema actually matches the capability?
- Which identifiers are stable across devices?
- What can appear in a title, subtitle, spoken dialog, Spotlight index, or universal link?
- Is the entity private, shared, public, or unknown?
- Does it map to IntentPerson, PlaceDescriptor, IntentFile, or another system value?
- Does the product need onscreen context or visual intelligence search?
- Is the action short, background-capable, long-running, cancellable, or undoable?
- Which target/process can execute it?
- What happens on older OS versions, signed-out state, deleted records, or model unavailability?

## Step 1: model the entity boundary

Create an AppEntity only for data the person expects to use in system experiences. A good entity has:

- stable identifier;
- account scope;
- privacy-reviewed properties;
- localized DisplayRepresentation;
- a default EntityQuery;
- an explicit deleted/unavailable behavior;
- optional schema and transfer/URL routes;
- a shared projection that can be rebuilt.

Keep the full domain object behind the entity. Do not expose raw persistence relationships, credentials, private model context, or arbitrary unbounded text.

## Step 2: choose the schema

Use a documented App schema when the capability genuinely fits. Write down:

| Decision | Evidence |
| --- | --- |
| Domain | The product’s action/content matches the domain description |
| Schema | Required intent/entity/enum properties are identified |
| Group | All required schemas in a group are implemented |
| Macro | The selected SDK supports the macro and generated requirements |
| Result | Output, dialog, open-app, or snippet contract is explicit |
| Fallback | In-app/manual path works when schema/system route is unavailable |

If no schema fits, use a carefully designed custom AppIntent/AppEntity route instead of forcing a misleading schema.

## Step 3: make resolution current

Implement queries as adapters to the domain store:

    system input -> identifier/string/property match
      -> account-scoped current lookup
      -> zero, one, or disambiguated result

Do not resolve from a stale in-memory list only. Support deleted, archived, signed-out, and permission-limited records. Keep the query target-safe if an App Intents or widget extension can run it.

When an entity is stable across devices, adopt SyncableEntity only if the ID contract is real. If the app has local and stable IDs, preserve both with the documented paired identifier type. When continuity fails, return a manual search or full-app destination.

## Step 4: add trust and interoperability

Add only the bridges the product can support:

| Bridge | Add when | Required safety |
| --- | --- | --- |
| OwnershipProvidingEntity | Sharing/public state changes action risk | Refresh ownership and authorize at mutation |
| IntentValueRepresentation | Entity maps to a known system value | Validate imports and minimize exported fields |
| URLRepresentableEntity/Intent | A universal-link destination can reopen exact content | Use opaque stable IDs and revalidate access |
| onscreen entity context | The person needs “this item” conversational references | Expose only the visible, privacy-reviewed entity |
| RelevantEntities | Media suggestions are relevant in a documented context | Replace/clear suggestions and record scope |
| UniqueAppEntity | Exactly one settings/configuration object exists | Use UniqueAppEntityQuery and never return multiple values |
| UnionValue | A parameter has a finite set of legitimate types | Validate every case and localize each case |

Do not add a bridge because it increases API surface. Each one creates another input, privacy, or lifecycle boundary.

## Step 5: choose runtime behavior

Record a runtime contract for each intent:

| Work | Configuration | Product behavior |
| --- | --- | --- |
| Short read/mutation | Background-capable if safe | Finish with current result or error |
| App-only review | Foreground or deferred mode | Explain handoff and preserve pending state |
| File/data/model work over normal limit | LongRunningIntent | Report progress, checkpoint, and allow cancellation |
| Resource-sensitive task | CancellableIntent | Stop work, release resources, preserve recoverable state |
| Reversible mutation | UndoableIntent | Register inverse domain operation when an UndoManager exists |

Do not claim background execution because an intent compiles. Verify supportedModes, currentMode, target membership, process lifetime, resource limits, and system invocation.

## Step 6: keep AI proposals separate

For a local model that maps a capture to an entity:

1. preserve the original input;
2. run an availability-checked model;
3. emit typed candidate IDs or a typed proposal;
4. validate candidates against the current store;
5. display source, candidate, and uncertainty;
6. ask for explicit approval when the mapping changes domain state;
7. run the AppIntent or domain command;
8. re-fetch the entity and rebuild system projections.

The model must not invent a stable ID, ownership state, universal-link path, or permission. If it proposes free text, map it to a typed candidate list before the system-facing action.

## Step 7: design system handoffs

Choose the smallest useful destination:

| Need | Destination |
| --- | --- |
| One fact or safe action | AppIntent result or interactive snippet |
| Browse/disambiguate | AppEntity query or full-app search |
| Continue a visible item | Onscreen context plus precise app destination |
| Cross-app value | Transferable/IntentValueRepresentation |
| Continue on another device | SyncableEntity and/or universal link |
| Long review/edit | Full app with durable pending state |
| Control Center action | Direct control result/value; never rely on snippets |

Keep the system container system-owned. Use the app’s native SwiftUI/Liquid Glass design only after the person enters the app-owned route.

## State and fallback matrix

| State | Entity/system behavior | App fallback |
| --- | --- | --- |
| Current | Resolve and display current record | Full detail/edit |
| Ambiguous | Present meaningful choices | In-app search |
| Missing/deleted | Return unavailable/error without private detail | Recovery or archive |
| Shared/public | Show ownership context and confirm consequence | Full review |
| Signed out | Remove projection or request account | Sign in |
| Stable ID unresolved | Do not fabricate record | Local search or restore |
| Transfer import rejected | Reject and preserve source | Manual mapping |
| Schema unsupported | Use custom intent or app route | In-app action |
| Model unavailable | Keep source and deterministic choice | Manual mapping |
| Long task canceled | Save checkpoint/cleanup state | Resume or discard |
| Undo unavailable | Preserve prior state or app recovery | Full app |
| Permission required | Throw precise permission error | Settings/request route |

## Privacy rules

- Index and donate only content the person expects the system to find.
- Keep titles/subtitles/dialogs free of unnecessary sensitive text.
- Reauthorize every mutation after entity resolution.
- Treat universal links and transferred values as untrusted input.
- Invalidate projections on account changes, deletion, and permission loss.
- Do not use model-generated metadata as proof of access, ownership, or identity.
- Keep public/shared state distinct from private app records.

## Evidence packet

Attach:

- schema selection and required-group audit;
- entity/query/display representation fixture;
- stable-ID and cross-device resolution record;
- ownership/shared/public confirmation run;
- transfer import/export test;
- universal-link and authentication handoff test;
- onscreen context and visual-intelligence test when supported;
- relevance donation/clear test when supported;
- unique/union parameter tests where used;
- mode/target/long-running/cancellation/undo fixture;
- privacy, accessibility, localization, and error-state run;
- signed physical-device and release artifact proof.

The [schema/entity proof matrix](../60-verification/20-app-intent-schema-and-entity-proof-matrix.md) is the acceptance checklist. The [compile-oriented recipes](../70-code-recipes/38-app-intents-schema-entity-and-execution-recipes.md) are route sketches, not compiled project code.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents)
- [App schema domains](https://developer.apple.com/documentation/appintents/app-schema-domains)
- [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [Entity queries](https://developer.apple.com/documentation/appintents/entity-queries)
- [SyncableEntity](https://developer.apple.com/documentation/appintents/syncableentity)
- [OwnershipProvidingEntity](https://developer.apple.com/documentation/appintents/ownershipprovidingentity)
- [IntentValueRepresentation](https://developer.apple.com/documentation/appintents/intentvaluerepresentation)
- [RelevantEntities](https://developer.apple.com/documentation/appintents/relevantentities)
- [UniqueAppEntity](https://developer.apple.com/documentation/appintents/uniqueappentity)
- [UnionValue](https://developer.apple.com/documentation/appintents/unionvalue%28%29)
- [URLRepresentableIntent](https://developer.apple.com/documentation/appintents/urlrepresentableintent)
- [Intent modes](https://developer.apple.com/documentation/appintents/intentmodes)
- [LongRunningIntent](https://developer.apple.com/documentation/appintents/longrunningintent)
- [CancellableIntent](https://developer.apple.com/documentation/appintents/cancellableintent)
- [UndoableIntent](https://developer.apple.com/documentation/appintents/undoableintent)
- [App Intent updates](https://developer.apple.com/documentation/updates/appintents)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
