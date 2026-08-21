# App Intents transfer, ownership, relevance, and execution contracts

## Scope

This page covers the App Intents contracts that sit between a typed app model
and the system's multi-step workflows:

- alternate entity representations with Transferable and
  IntentValueRepresentation;
- large entity parameters with EntityCollection;
- ownership and sharing context with OwnershipProvidingEntity;
- contextual entity suggestions with RelevantEntities;
- foreground/background execution with IntentModes and IntentSystemContext;
- target routing with allowedExecutionTargets;
- dependency/package/extension boundaries;
- extended work with LongRunningIntent;
- cancellation cleanup with CancellableIntent;
- reversible actions with UndoableIntent;
- localized and actionable error states.

These contracts are useful when an app wants Apple Intelligence, Siri, Shortcuts,
widgets, or another app to carry a typed value across a workflow. They are not a
permission system, a server job queue, or a substitute for the app's domain
transaction policy.

The route is:

    app record
      -> AppEntity projection
      -> display/type representation
      -> optional system-value transfer representation
      -> system-selected intent parameter
      -> target/process execution
      -> current authorization and domain validation
      -> side effect, long-running work, or reversible change
      -> result/error/recovery

Keep each arrow explicit. The system may hold an entity identifier, a transferred
PlaceDescriptor, or a collection of IDs; the app still needs to resolve current
truth before it acts.

## Version and beta boundary

Several APIs in this route are labeled beta or preliminary in the current Apple
documentation. Record the state in the target project:

| Route | Documentation treatment |
| --- | --- |
| AppEntity, Transferable, IntentValueRepresentation | Verify selected SDK signatures and common system-value types |
| EntityCollection | Verify selected SDK; useful for avoiding eager hydration |
| OwnershipProvidingEntity, EntityOwnership | Beta/preliminary; isolate and test confirmation behavior |
| RelevantEntities | Context-specific; Apple documents media suggestions for workout/audio contexts |
| IntentModes and currentMode | Verify supported foreground/background combinations in the target |
| LongRunningIntent | Beta/preliminary in current docs; report progress and verify runtime behavior |
| CancellableIntent | Beta/preliminary in current docs; cleanup must be fast |
| UndoableIntent | Verify undo manager availability in the actual app/extension process |
| allowedExecutionTargets | Beta/preliminary in current docs; target membership and process proof required |
| AppIntentsPackage/AppIntentsExtension | Package/extension registration and dependency graph are target-specific |

Do not turn a documentation page or WWDC session into a claim that the OS will
select a process, display a confirmation, preserve a background task, or offer
undo on every device. Compile and system invocation remain separate gates.

## AppEntity is a contract, not a storage model

An AppEntity should expose the subset of a domain model that people can use in
system experiences. Keep the projection small and stable:

- a persistent unique ID;
- properties the system can resolve;
- a display representation;
- a type display representation;
- a default query;
- optional transfer representations;
- optional ownership or cross-device identity;
- an OpenIntent or action route when the system can select it.

Apple's documentation notes that the app can define the AppEntity directly on a
data model or create a separate intent-facing model. A separate projection is
usually safer when the domain object contains private fields, UI state,
database contexts, or non-Sendable resources.

### Persistent identity

A shortcut or system workflow can retain an entity identifier. The identifier
must stay unique and meaningful for the entity type. Do not use:

- an array index;
- a transient object address;
- a display title;
- a local cache key that changes during migration;
- a random UUID regenerated on every launch.

If an ID has a local and a stable cross-device form, document both and resolve
the current account/store before returning the entity.

### Display and transfer are different

Use DisplayRepresentation for a compact human-facing description. Use
IntentValueRepresentation when a well-known system type can use the value
directly. For example:

- a place entity can transfer to PlaceDescriptor;
- a contact entity can transfer to IntentPerson;
- a file can use IntentFile/FileEntity routes;
- a domain value may export a safe system-defined value but not its private
  backing record.

A thumbnail or serialized JSON blob is not equivalent to a system value. Maps
cannot generate directions from an arbitrary picture of a landmark; they need a
place representation that carries usable location semantics.

## IntentValueRepresentation and Transferable

Apple documents IntentValueRepresentation as a transfer representation between a
custom AppEntity and system intent values. The entity conforms to Transferable
and exposes the representation from its transferRepresentation property.

The representation can be:

- export-only, when the app can safely provide a value but cannot import it;
- bidirectional, when the app can convert the system value back to a current
  domain entity;
- key-path-based, when the entity directly stores a compatible system value.

### Export review

Before exporting, answer:

| Question | Required decision |
| --- | --- |
| Is the exported value semantically equivalent? | A location must represent a location, not an image |
| What precision is safe? | Do not disclose more location or contact detail than needed |
| Is the value current? | Resolve or refresh before exporting |
| Can another app use it without app-private context? | Prefer a common system type |
| Is the transfer reversible? | Add importing only when the app can validate it |
| What happens when importing fails? | Return a localized recoverable conversion error |
| Is the user expecting the handoff? | Keep system transfer within an explicit workflow |

Exporting a system value does not automatically export the rest of the entity.
Do not include credentials, private notes, internal account IDs, or hidden model
signals in the transfer.

### Import review

A bidirectional import is a proposal to construct or locate a domain object. It
must not silently create a record or grant access.

Use this sequence:

    system value
      -> validate required fields
      -> normalize identifiers/locale/precision
      -> resolve current account
      -> match existing record or prepare a draft
      -> ask for confirmation if a mutation is implied
      -> commit only through the app's domain service

If the system value is ambiguous, return a conversion failure or ask the system
for clarification. Do not guess a person or place when the consequences are
material.

### Transferable versus file/data representations

Transferable supports many representation families. A file or binary data
representation is useful for actual file content, but it is not the best
interoperability type for a semantic place or person. Use the most specific
public system intent value that preserves meaning.

A file transfer also creates a lifetime and privacy problem:

- temporary file cleanup;
- security-scoped access;
- content type;
- export size;
- redaction;
- user-approved destination;
- cancellation.

Keep those concerns in the document/file route rather than treating a Data
representation as a universal bridge.

## EntityCollection for large parameter lists

EntityCollection stores entity identifiers initially and can resolve full
AppEntity values later. This matters when an intent accepts hundreds of items.

Use EntityCollection when the operation needs IDs:

~~~swift
@Parameter(title: "Items")
var items: EntityCollection<LibraryEntity>
~~~

Then operate on items.identifiers through a domain service. Only call
resolvedEntities() when the operation truly needs the entity projections for
display or additional validated metadata.

This avoids:

- hydrating hundreds of objects during parameter resolution;
- loading images or summaries that the action does not need;
- unnecessary network requests;
- memory spikes in a system process;
- confusing parameter timeout with domain failure.

EntityCollection is not a bypass around authorization. The identifiers still
need current account and ownership checks when the action runs.

### ID-only action

An ID-only operation is usually safer:

    EntityCollection identifiers
      -> current account
      -> batch domain query
      -> authorization
      -> idempotent mutation
      -> result count and errors

If the operation requires per-entity confirmation, resolve only the bounded
subset needed to present the confirmation. Do not show a private title just
because an ID resolved during parameter completion.

### Partial failure

For a collection action, define partial failure:

- all records authorized and changed;
- some records missing or unauthorized;
- records already in desired state;
- cancellation after a committed prefix;
- validation failure before any mutation;
- mutation failure after a committed prefix.

Prefer a transaction or explicit per-item result model. Do not report “all
done” when a subset failed. If the action is undoable, register the inverse for
the committed set, not for items that never changed.

## OwnershipProvidingEntity and confirmation context

OwnershipProvidingEntity lets an AppEntity provide EntityOwnership flags that
describe sharing/public status. Apple documents this for confirmation context
around destructive or sensitive actions on shared or public entities.

The app should only conform when ownership is meaningful. Do not return .public
because the app has a public marketing page. Do not return .shared because the
record is merely visible on the current device.

Model the flags from current domain truth:

| Domain state | EntityOwnership treatment |
| --- | --- |
| Private to current user | No shared/public flag, unless another documented state applies |
| Shared with named collaborators | shared |
| Publicly accessible record | public |
| Both shared and public | combine documented flags |
| Unknown while store loads | unknown or delay the action |
| Permission revoked | refuse to expose or act |

Ownership context improves confirmation wording; it does not replace the app's
own requestConfirmation policy, authorization, or server-side access check.

### Destructive action boundary

For update, delete, publish, move, or share actions:

1. resolve the current entity;
2. resolve current ownership/sharing;
3. verify the actor can perform the mutation;
4. request confirmation where the product requires it;
5. commit through a domain transaction;
6. update/delete index and donations;
7. register undo only for committed changes;
8. return a result that names the effect without leaking private data.

A system-generated confirmation is not proof that the user authorized every
domain detail. The app remains responsible for the final mutation boundary.

## RelevantEntities and contextual donations

RelevantEntities is a specialized donation route for media-related entities
such as songs, albums, artists, playlists, radio stations, or podcasts in a
context such as a workout. Apple documents a shared RelevantEntities object
with update, remove, and clear operations. Each update replaces the app's
previous suggestions for that context, and the system may expire them.

Use it only when the entity and context match the documented route. It is not a
generic “boost this entity in all Apple Intelligence surfaces” API.

Donation rules:

- donate only entities the user can currently access;
- donate a bounded, intentional set;
- replace the previous set atomically through the documented update call;
- clear suggestions when the context ends or data becomes unavailable;
- remove an entity after deletion/revocation;
- do not donate actions initiated by Siri or Shortcuts as if they were direct
  interface interactions;
- avoid sensitive titles in relevance logs;
- record the context and donation version for repair.

Relevance is a hint. The system chooses whether and where to surface it. Never
make a product promise that a donation will appear.

## Intent modes: foreground and background

IntentModes declares the execution modes an AppIntent supports. Apple documents
background, foreground, and combinations such as dynamic or deferred foreground
behavior. At runtime, IntentSystemContext.currentMode tells the intent how it is
currently running.

The action needs to decide whether it can:

- complete without a visible app;
- request a foreground continuation;
- update a visible navigation state;
- perform only a background-safe domain mutation;
- return a result that does not depend on a window.

Use supportedModes as a capability declaration, not as a scheduling promise.

### Execution policy table

| Action type | Preferred mode | Why |
| --- | --- | --- |
| Toggle a small setting | background | No UI needed; idempotent |
| Save a record | background or dynamic | Can commit without a view; may show result |
| Open a detail screen | foreground | Needs main app navigation |
| Pick among ambiguous items | foreground or confirmation | Needs user context |
| Upload/process a large file | background plus LongRunningIntent | Progress and cancellation |
| Edit a canvas selection | foreground | Requires visible target/context |
| Delete shared content | mode plus confirmation | Ownership and user review |

If a background action needs foreground UI, consult currentMode and the
documented continuation method. If the app cannot continue in the foreground,
complete safely in background or return a localized user-action-required error.

### Current mode is runtime state

Do not inspect process state through UIApplication as the only signal. Use the
App Intents system context. Keep the action logic independent of a window so
the same intent works from a terminated process when its target permits.

When the current mode changes, do not restart a non-idempotent mutation. Store a
domain operation ID and make resume behavior explicit.

## allowedExecutionTargets and process routing

allowedExecutionTargets tells the system which target may perform an intent or
entity query. The documented targets include the main app, an App Intents
extension, and a WidgetKit extension.

Choose the narrowest target:

| Work | Target |
| --- | --- |
| Open app navigation | main app |
| Short background-safe data mutation | App Intents extension where supported |
| Widget configuration/compact value | widget extension where supported |
| Shared query used by multiple surfaces | explicit target set plus extension-safe dependencies |
| UI-bound route | main app only |

The default target may be any available target. That is convenient for a
prototype but dangerous for code that assumes a window, SwiftData main context,
network session, or app singleton.

Target selection must be tested with:

- app running;
- app terminated;
- App Intents extension running;
- widget extension query;
- shared framework/package resource loading;
- account/store migration in the extension process;
- unavailable main app target.

## Dependency and package architecture

AppDependencyManager/AppDependency provide a documented dependency route for
App Intents. Use it to inject a store, service, or configuration into an
intent-facing type without reaching into a foreground view model.

AppIntentsPackage lets a framework or Swift package describe app intent
definitions and dependencies. AppIntentsExtension registers intents outside
the main app so the system can discover/perform them without launching the app.

A useful module graph is:

    Domain
      -> persistence/protocols, authorization, operation services

    IntentKit
      -> AppEntity, AppIntent, queries, transfer/ownership/execution adapters

    AppIntentsPackage
      -> IntentKit plus package dependencies

    MainApp
      -> UI/navigation plus IntentKit and app package

    AppIntentsExtension
      -> IntentKit, extension-safe dependencies, package registration

Do not put a SwiftUI navigation singleton or an app-only resource loader in
the shared intent module. Keep the shared layer Sendable and process-safe.

## LongRunningIntent and progress

LongRunningIntent extends the time available for an AppIntent's background work.
Apple documents performBackgroundTask with LongRunningTaskOptions and progress
reporting. On iOS-family platforms, ordinary background execution can be
limited; the long-running route is still subject to system policy, cancellation,
resources, and target constraints.

Use it for work such as:

- large file upload;
- data synchronization;
- local media processing;
- large model inference;
- export/finalization;
- a critical disk operation that cannot safely stop at the normal limit.

The operation must:

- checkpoint;
- report progress regularly;
- check Task cancellation;
- bound memory and temporary files;
- keep the domain operation idempotent;
- persist committed progress;
- recover after process termination when the product promises recovery;
- avoid UI-only dependencies.

Progress is user-facing state. Give it a meaningful total or an honest
indeterminate state. Do not report 100 percent before the domain commit and
index/donation updates are complete.

### Long-running is not background permanence

LongRunningIntent does not guarantee unlimited time, network continuity, battery,
or successful completion. A system may suspend or terminate the process. Design
the route like a resumable job, not like a detached server process.

If the app needs server work, persist the operation ID and reconcile the server
state. If the work is purely local, persist checkpoints and clean up temporary
resources on cancellation or failure.

## CancellableIntent and cleanup

CancellableIntent gives an intent a documented cancellation handler and reason.
Apple distinguishes person/system cancellation and runtime timeout conditions in
IntentCancellationReason.

On cancellation:

1. stop starting new work;
2. cancel child tasks;
3. release capture/model/network resources;
4. persist a safe checkpoint;
5. remove incomplete temporary output;
6. leave committed domain changes valid;
7. record a redacted diagnostic;
8. return quickly because the process can still be suspended.

Cancellation is not rollback. If an operation committed a prefix, either resume
from that checkpoint, expose partial completion, or use a domain transaction
that can undo the prefix. Do not pretend cancellation means zero side effects.

Use standard Swift task cancellation when the reason does not matter. Use the
App Intents cancellation handler when product recovery differs for timeout,
user cancellation, or system pressure.

## UndoableIntent and reversible state

UndoableIntent supplies an UndoManager suitable for registering the inverse of
an App Intent action. The manager can be nil. App Intents register undo; the app
initiates undo/redo from its interface.

Use it for:

- editing a local record;
- moving items between folders;
- applying a reversible formatting change;
- changing a setting where the inverse remains valid.

Do not use it as a substitute for a server audit log, a payment reversal, or a
guaranteed cross-device rollback. For remote/shared mutations, define what an
undo means and whether the action is still authorized when the user invokes it.

Register the inverse after the forward operation has committed. Capture only the
minimum prior state needed to restore the domain. If the entity has changed
since the action, compare a revision token before undoing and ask for review or
refuse to overwrite newer data.

## Error routes

Use localized, actionable App Intent errors when the user can fix the issue:

| Error state | Appropriate route |
| --- | --- |
| Sign-in needed | AppIntentError.UserActionRequired.signin or app-owned sign-in recovery |
| Account setup needed | UserActionRequired.accountSetup |
| Confirmation needed | UserActionRequired.confirmation or explicit confirmation |
| Missing permission | AppIntentError.PermissionRequired for the documented service |
| Record deleted | Current unavailable/search recovery |
| Wrong process target | Target configuration fix, not a user error |
| Conversion failed | Localized explanation of missing/invalid transferable fields |
| Partial collection failure | Count and retry/review route, not generic success |
| Cancellation | Persisted checkpoint and honest canceled/incomplete state |
| Long-running timeout | Resume/repair state; do not lose committed progress |
| Unsupported OS/device | Feature fallback to ordinary app workflow |

Do not put private record titles, raw prompt text, stable IDs, or server tokens in
the localized error unless the current authorization and user context make it
safe.

## Native design and Liquid Glass boundary

A system handoff may arrive in a compact Siri, Shortcuts, widget, or system
surface, then continue into the app. The app-owned experience should use:

- standard SwiftUI controls and semantic navigation;
- a clear confirmation or review surface for sensitive actions;
- functional Liquid Glass only around transient controls or focused actions;
- visible progress for long-running work;
- an accessible cancellation/stop route;
- a result state that distinguishes committed, partial, canceled, and failed;
- an undo affordance in the app's normal edit surface where appropriate.

Do not turn a confirmation dialog into a decorative glass billboard. The user
needs to know what will change, which records are affected, whether content is
shared/public, and what the recovery path is.

Use standard system surfaces first. Custom glass should preserve contrast,
Dynamic Type, VoiceOver focus, Reduce Motion, Reduce Transparency, and
platform-adaptive layout.

## Implementation checklist

- [ ] AppEntity IDs are persistent, unique, and current-store resolvable.
- [ ] Display and transfer representations are reviewed separately.
- [ ] IntentValueRepresentation uses a semantically correct system value.
- [ ] Importing a system value validates and does not silently mutate.
- [ ] EntityCollection is used for large ID sets when full hydration is not
      needed.
- [ ] OwnershipProvidingEntity is used only when sharing/public status is real.
- [ ] Destructive/shared/public actions still perform app authorization and
      confirmation.
- [ ] RelevantEntities is limited to the documented contextual media route.
- [ ] Donations are based on direct UI interactions where Apple requires it.
- [ ] supportedModes and allowedExecutionTargets match process assumptions.
- [ ] currentMode is consulted at runtime.
- [ ] Shared App Intent dependencies are extension-safe and Sendable.
- [ ] LongRunningIntent reports progress and checkpoints.
- [ ] CancellableIntent releases resources quickly and records recovery state.
- [ ] UndoableIntent registers inverse state only after commit and handles nil.
- [ ] Errors are localized, actionable, and privacy-safe.
- [ ] Liquid Glass is restrained and accessibility-tested.
- [ ] Physical system invocation and archive target membership are recorded.

## Sources

- https://developer.apple.com/documentation/appintents/appentity
- https://developer.apple.com/documentation/appintents/defining-app-entities-for-your-custom-data-types
- https://developer.apple.com/documentation/appintents/intentvaluerepresentation
- https://developer.apple.com/documentation/appintents/appentity/valuerepresentation
- https://developer.apple.com/documentation/appintents/entitycollection
- https://developer.apple.com/documentation/appintents/ownershipprovidingentity
- https://developer.apple.com/documentation/appintents/entityownership
- https://developer.apple.com/documentation/appintents/relevantentities
- https://developer.apple.com/documentation/appintents/donations-and-discovery
- https://developer.apple.com/documentation/appintents/intentmodes
- https://developer.apple.com/documentation/appintents/intentmodes/current
- https://developer.apple.com/documentation/appintents/intentsystemcontext/currentmode
- https://developer.apple.com/documentation/appintents/appintent/supportedmodes-5zhmb
- https://developer.apple.com/documentation/appintents/appintent/allowedexecutiontargets
- https://developer.apple.com/documentation/appintents/intentexecutiontargets
- https://developer.apple.com/documentation/appintents/longrunningintent
- https://developer.apple.com/documentation/appintents/cancellableintent
- https://developer.apple.com/documentation/appintents/undoableintent
- https://developer.apple.com/documentation/appintents/undoableintent/undomanager
- https://developer.apple.com/documentation/appintents/app-intents
- https://developer.apple.com/documentation/appintents/appintentspackage
- https://developer.apple.com/documentation/appintents/app-extension
- https://developer.apple.com/documentation/appintents/appintenterror
- https://developer.apple.com/documentation/appintents/appintenterror/permissionrequired
- https://developer.apple.com/documentation/appintents/appintenterror/useractionrequired
- https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- https://developer.apple.com/documentation/swiftui/navigation
- https://developer.apple.com/design/human-interface-guidelines/
