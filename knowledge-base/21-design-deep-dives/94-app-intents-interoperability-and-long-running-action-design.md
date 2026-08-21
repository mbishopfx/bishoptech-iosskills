# App Intents interoperability and long-running action design

## Design goal

An Apple-native app can participate in a multi-step system workflow without
turning every interaction into a generic command. The design should communicate
three things clearly:

1. what value is moving between apps or system surfaces;
2. what the app is about to change;
3. whether the action is immediate, background, cancelable, reversible, or
   waiting for user action.

The design route is:

    typed entity/value
      -> system handoff or assistant parameter
      -> ownership/permission/confirmation context
      -> target/process state
      -> progress or immediate result
      -> commit/undo/recovery

The native feel comes from clear hierarchy, system semantics, accessibility, and
restraint. Liquid Glass can support a focused control group or review surface,
but it should not obscure the domain record, progress, or confirmation meaning.

## Interoperability is a user-visible contract

A transferred value is not just a technical representation. It changes what the
person can do next.

| Value | What the person expects |
| --- | --- |
| PlaceDescriptor | The next app can use the place as a place |
| IntentPerson | The next app can use contact/person semantics |
| IntentFile/FileEntity | The next app can inspect or import a file |
| EntityCollection | The action can operate on many chosen records without a slow picker |
| AppEntity display representation | The system can explain the selected record |
| Ownership context | Confirmation reflects shared/public impact |
| Stable entity identity | Another device can attempt current resolution |
| Long-running progress | The person can understand waiting and cancel safely |
| Undoable action | The app can reverse a committed local change when appropriate |

If the app cannot keep that promise, use an app-owned handoff with an explicit
draft/review screen instead of claiming a rich transfer.

## Transfer representation design

### Display first, transfer second

A system result may display an entity before it transfers it. Design the
representations independently:

- type representation answers “what kind of thing?”;
- display representation answers “which thing?”;
- transfer representation answers “what usable system value can move?”;
- app-owned detail answers “what is current and what can I do now?”.

Do not put a long transfer payload into the subtitle. Do not assume the display
thumbnail will travel with the semantic value. Do not use a display title as a
unique identifier.

### Known system types

Use a specific system value when it preserves meaning. For a location, a
coordinate/place descriptor is better than an image. For a contact, an
IntentPerson with appropriate fields is better than a private JSON export.

Design the transfer surface with a small mapping table:

| App concept | Safe transfer candidate | App-owned detail |
| --- | --- | --- |
| Saved place | PlaceDescriptor | Notes, private tags, current access |
| Contact suggestion | IntentPerson | Internal relationship, private metadata |
| Exportable document | IntentFile/FileEntity | Revision, sharing, app-specific annotations |
| Image with analysis | Transferable file/data only if user approved | Source, model version, review state |
| Media item | Documented media AppEntity/value | Playback/account/subscription state |

The transfer candidate must be safe when the destination app has no access to
the source app's private database.

### Import creates a decision point

If another app sends a system value into the app, show a draft or resolution
state when identity or side effects are uncertain:

    incoming value
      -> normalized preview
      -> duplicate/current match
      -> user choice
      -> domain commit

A background intent can store a pending draft, but it should not silently
publish, delete, send, purchase, or overwrite shared data. Use an explicit
confirmation when the action changes external state.

## Large collections and selection design

EntityCollection is a system-friendly way to represent many entity IDs without
hydrating every entity at parameter-resolution time.

Use it when the action reads or mutates a large set:

- show a compact count;
- show representative names only when authorized and needed;
- communicate partial selection or filtered selection;
- provide a progress state for the operation;
- preserve the ID set across cancellation;
- distinguish “selected zero” from “resolution failed.”

For destructive collections, a confirmation surface should include:

- number of records;
- human-readable scope;
- shared/public impact if applicable;
- whether the action is reversible;
- what happens to records that disappeared;
- the cancel path.

Do not use a glass pill with only “128 items.” Give the person enough context
to understand the change without making the confirmation panel dense.

## Ownership and confirmation surfaces

OwnershipProvidingEntity can give the system context about shared/public state,
but the app's design still owns the final review.

### Confirmation hierarchy

Use a clear order:

1. primary statement: what will happen;
2. target scope: which records or entity;
3. ownership/sharing: who else may be affected;
4. consequence: irreversible or reversible;
5. primary confirm action;
6. secondary cancel/review action.

For a private local edit, a compact review may be enough. For deleting shared
content, publishing, or changing a collaborative record, expand the review with
the relevant collaborators/public state. Do not expose private collaborator
details merely to make the confirmation sound more specific.

### Liquid Glass review surfaces

Use a focused glass group for:

- a compact confirmation action cluster;
- a floating progress control over a media/canvas surface;
- an undo/cancel control over a current app-owned task;
- a contextual ownership badge when it improves comprehension.

Keep the record content on an ordinary readable surface. The glass layer should
float above or beside content, preserve contrast, and collapse/adapt with the
platform layout. Standard buttons, menus, sheets, alerts, and navigation are
the default.

Avoid:

- a full-screen glass background behind a destructive confirmation;
- translucent text over a busy image;
- multiple “confirm” buttons with unclear scope;
- a public/shared badge that is color-only;
- an undo affordance that appears before the commit succeeds.

## Relevance and donations

Relevance is a suggestion surface, not a command surface.

For documented RelevantEntities media contexts:

- show the current context in the app if the user can inspect it;
- allow the user to stop/clear suggestions where appropriate;
- avoid making relevance look guaranteed;
- remove stale/deleted entities;
- do not donate more private metadata than the system surface needs.

For intent donations from app UI actions, donate the action a person actually
performed in the app. Do not donate a Siri/Shortcuts invocation as if it were a
fresh direct UI action; that can create feedback loops and misleading
predictions.

If a product has a settings screen for system discoverability, group:

- indexed content;
- contextual relevance;
- onscreen context;
- action donations.

Explain these as separate choices when the privacy impact differs.

## Foreground and background state design

An App Intent can run in a background process, foreground app, or a mode that may
transition. The screen should not assume that a window is available.

### Mode-specific outcomes

| Runtime state | UI/result treatment |
| --- | --- |
| Background and complete | concise success/result; do not fabricate a visible screen |
| Background and needs user input | actionable error or foreground handoff |
| Foreground and opens content | navigate to the current detail |
| Foreground but stale target | re-resolve, then show recovery |
| Extension process | use extension-safe store and no UI singleton |
| Main app cold launch | reconstruct route from intent parameters |
| Mode changes mid-task | continue idempotently; do not double-commit |

A background invocation can update app data without immediately showing a screen.
A foreground invocation can open the app, but the app should still validate
current state before navigation.

### Progress is a design surface

For long-running work, show:

- operation title;
- current phase;
- completed/total or honest indeterminate state;
- stop/cancel action;
- last successful checkpoint if useful;
- error/retry route;
- final committed state.

Do not make a spinner the only progress communication for an operation that
takes long enough to leave the user unsure. Do not show 100 percent until the
domain commit and any required derived-index update are complete.

A compact Liquid Glass progress control can float over media, but the progress
label and cancel button must remain readable with reduced transparency and
larger text.

## Cancellation and partial completion

Cancellation is a state transition, not a decorative button:

    running
      -> cancel requested
      -> stop new work
      -> checkpoint/release resources
      -> canceled or partially committed
      -> resume/retry/inspect

The design must distinguish:

- canceled before any commit;
- canceled after partial commit;
- timed out;
- failed due to permission/network;
- completed successfully.

If the user cancels a file import after three of ten files, say what happened.
Provide resume or retry if the operation supports it. If partial state is not
safe, roll back through a domain transaction and explain the result.

## Undo design

Undo belongs in the app's normal editing language:

- show an undo affordance after the action commits;
- make the inverse specific;
- do not claim undo for a server action the app cannot reverse;
- compare revisions before restoring old values;
- show conflict/review if newer edits exist;
- keep the keyboard/menu/VoiceOver path available;
- make undo work after a system-originated App Intent returns to the app.

If UndoManager is unavailable in the process, the action should still complete
honestly and the app can use a domain-specific recovery route where appropriate.
Do not crash because the system did not provide an undo manager.

## Error and permission copy

System-facing errors should be concise and actionable:

| State | Copy goal |
| --- | --- |
| Sign in | Tell the person which account step is needed |
| Permission | Name the service and the next Settings/app action |
| Confirmation | Explain the pending effect |
| Conversion | Name the missing semantic field |
| Not found | Offer search or current-data recovery |
| Partial | State count and next action |
| Canceled | State whether any changes were committed |
| Timeout | Offer resume or retry |
| Unsupported | Return to the ordinary app workflow |

Do not expose internal exception names, stable IDs, raw prompts, or private
titles. Localize errors with the same care as normal UI and voice output.

## Process and target design

Use target membership as a product architecture choice:

- main app for UI-bound routes;
- App Intents extension for extension-safe actions;
- widget extension for widget-owned configuration/value routes;
- shared package for definitions and pure domain adapters.

Design a package boundary that can build without UIKit/SwiftUI if the system
may execute it outside the main app. Keep dependencies explicit and test an
empty/cold store, account transition, and missing resource.

If a route opens the app, its result should create a navigation request, not
reach into a window singleton from an extension. If a route runs in the
background, it should return data/result state rather than pretending a view
was displayed.

## Accessibility and inclusive review

The transfer and execution design must remain usable when:

- VoiceOver reads the entity and the confirmation;
- Dynamic Type expands the title/ownership/progress labels;
- Reduce Transparency removes the visual glass cue;
- Reduce Motion removes progress morphing;
- Switch Control or keyboard operates cancel/confirm/undo;
- the user cannot see a custom canvas or image.

Use semantic controls, explicit labels, status announcements, and non-color
ownership/selection cues. Make the spoken confirmation state what changes and
how many records are affected without overreading private details.

## Design review checklist

- [ ] Display, type, transfer, and app-owned representations have distinct jobs.
- [ ] Incoming values land in a draft/resolution state when identity is uncertain.
- [ ] Large selections communicate count, scope, partial failure, and recovery.
- [ ] Shared/public actions show clear impact and confirmation.
- [ ] Relevance/donations are framed as suggestions, not guarantees.
- [ ] Background/foreground behavior is visible in the route and copy.
- [ ] Long-running work reports phase/progress and has a stop path.
- [ ] Cancellation explains partial commits and preserves recovery.
- [ ] Undo appears only after commit and handles conflict/unavailability.
- [ ] Errors are localized, actionable, and privacy-safe.
- [ ] Liquid Glass is limited to functional control/review layers.
- [ ] VoiceOver, Dynamic Type, reduced effects, keyboard, and Switch Control
      are tested.
- [ ] Cold launch, extension process, and target-specific navigation are tested.

## Sources

- https://developer.apple.com/documentation/appintents/appentity
- https://developer.apple.com/documentation/appintents/defining-app-entities-for-your-custom-data-types
- https://developer.apple.com/documentation/appintents/intentvaluerepresentation
- https://developer.apple.com/documentation/appintents/entitycollection
- https://developer.apple.com/documentation/appintents/ownershipprovidingentity
- https://developer.apple.com/documentation/appintents/entityownership
- https://developer.apple.com/documentation/appintents/relevantentities
- https://developer.apple.com/documentation/appintents/donations-and-discovery
- https://developer.apple.com/documentation/appintents/intentmodes
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
- https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- https://developer.apple.com/design/human-interface-guidelines/
