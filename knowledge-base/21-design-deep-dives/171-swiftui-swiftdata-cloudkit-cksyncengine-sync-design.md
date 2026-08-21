# SwiftUI local-first sync and conflict-review design

The sync UI should communicate a simple truth: the person can keep working on
the device, while the app tells them what has and has not been confirmed by
the remote authority. Native design here is mostly about calm state language,
recovery, and accessible review—not about adding more badges or animation.

## Screen architecture

| Surface | Job | Required state |
| --- | --- | --- |
| Record list | Show local content immediately | local save, pending sync, stale/error marker, deletion/tombstone state |
| Record detail | Edit one aggregate with stable ownership | local revision, last confirmed remote revision, conflict/migration lock |
| Sync status sheet | Explain account/network/sync behavior | offline, iCloud unavailable, pending count, last attempt, retry |
| Conflict review | Let the person understand and choose a merge | local/server/ancestor fields, changed-field markers, deterministic policy, Apply/Keep actions |
| Migration recovery | Protect data during schema evolution | current/required version, backup/export/retry/update action |
| Account transition | Avoid cross-account leakage | signed-out/switching/new-account boundary, local-data decision |
| Settings/diagnostics | Make release and support state inspectable | container environment/build, schema version, redacted error, no record payloads |

Do not make “sync” a single full-screen loading state. A person should be able
to read and edit locally while a background sync is pending, unless the domain
has a deliberate lock for a migration or security-critical conflict.

## Native state vocabulary

Use semantic labels backed by an enum or state model:

~~~text
Saved on this device
Waiting to sync
Syncing
Up to date as of [time/revision]
Offline — changes will retry
iCloud account unavailable
Conflict needs review
Migration required before editing
Sync paused — tap to retry
~~~

The labels should describe evidence, not hope. “Up to date” means the app has a
defined confirmation boundary; it does not mean all devices in the world have
rendered the same state. If the app cannot know the last server revision, use
“Saved on this device” or “Waiting to sync.”

Use text plus an icon and accessibility value. Color can reinforce the state,
but a green tint must not be the only indication of a remote confirmation.

## Record-list design

Render the local store first. Each row can contain:

1. the record’s canonical title/content;
2. a stable last-edited time formatted for the user’s locale;
3. a compact sync state label;
4. a conflict or migration action when the row is blocked;
5. a disclosure to detail, never an invisible swipe-only recovery path.

Use `List`, `ScrollView`, or a native grid based on content density. Bound
fetches and keep row identity tied to stable domain IDs rather than array
indices. If remote changes arrive, preserve scroll/focus where possible and
announce a meaningful update through accessibility rather than moving the
person unexpectedly.

When a local edit saves immediately, update the row without a blocking spinner.
If the remote write later fails, change the status to a recoverable pending or
error state and keep the content. Never delete a row merely because a sync
request failed.

## Detail and edit design

The detail view should separate editable content from sync facts. A good
layout is:

~~~text
record content
  -> primary edit controls
  -> local save confirmation
  -> “Last confirmed remotely” revision/time (if known)
  -> sync status and retry
  -> conflict/migration action when required
~~~

Use native `TextField`, `TextEditor`, `Toggle`, `DatePicker`, and form controls
where they fit the domain. Disable only the field or action that is actually
unsafe; an unavailable network should not make unrelated local reading
impossible. During a migration lock, explain the reason and preserve a safe
read-only view or export path when the product permits it.

When a save is in progress, disable duplicate commit actions and preserve the
current request ID. If the person navigates away, the model actor or route
coordinator should finish or cancel according to the domain contract, not the
view’s deallocation timing.

## Conflict-review design

A conflict card needs field-level clarity:

- “Your device” — local value and local revision/time;
- “Other device/server” — server value and server revision/time;
- “Before both edits” — ancestor value when available;
- changed-field markers, with no hidden or truncated value that affects the
  decision;
- deterministic policy suggestion, such as “These edits touch different
  fields and can be combined”;
- explicit actions: Keep mine, Keep server, Combine selected fields, or
  Cancel and review later.

Do not ask a model to be the conflict UI. If the optional AI proposal is shown,
put it below the canonical diff with a “Generated suggestion” label and a
source/revision summary. The user’s Apply action should call a deterministic
merge validator that rechecks the current server change tag and can surface a
new conflict if the record changed while the sheet was open.

If the app cannot safely display a full field diff, show the record as blocked
and provide a deterministic fallback/export rather than a prose-only summary.

## Account and migration recovery

An iCloud account switch is a trust boundary. Use a dedicated confirmation
surface that states which local data is associated with the previous account,
what will remain on the device, and what the app will do next. Do not merge
private data across account IDs because it is convenient.

For migration:

1. announce that the app is upgrading its local data format;
2. prevent concurrent edits while the migration transaction runs;
3. show progress only when it is meaningful and bounded;
4. if migration fails, preserve the original store and show a recovery path;
5. make schema version and build identity available in diagnostics.

Avoid a “repair database” button that silently erases data. If reset is a real
product feature, use explicit destructive confirmation and state what can and
cannot be recovered.

## Functional Liquid Glass

Liquid Glass works best for actions and system-level status grouping:

- a toolbar group with Refresh, Sync Now, and Settings;
- a conflict-action group with Keep, Combine, and Cancel;
- a small floating sync-status control that opens the status sheet;
- a migration or account-transition banner that must remain legible over
  content.

Keep records, text, and diff values on the content layer. Do not wrap every
`List` row, field, conflict column, and status badge in custom glass. Use a
shared glass container for adjacent controls where the current SwiftUI design
system calls for one group. Test light/dark appearance, artwork/background
variation, increased contrast, Reduce Transparency, and large text.

Motion should explain state: a subtle pending-to-confirmed transition is
enough. Respect Reduce Motion; avoid a continuous shimmer that suggests remote
progress when the sync schedule is indeterminate. A failed retry should settle
into visible text and a reachable action.

## Accessibility and alternate input

VoiceOver order for a record should be content, local save state, remote
confirmation state, conflict/migration warning, and the action. The warning
must not be hidden in an unlabeled icon. Use accessibility values such as
“Waiting to sync” and “Conflict needs review.”

At large Dynamic Type sizes:

- allow record titles and diff values to wrap;
- move action groups into a vertical stack;
- keep local/server/ancestor headings adjacent to their values;
- avoid a horizontally scrolling conflict table that cannot be navigated with
  VoiceOver or Switch Control.

Keyboard and pointer users need direct focusable actions for retry, detail,
conflict review, and settings. Voice Control should be able to say “Keep my
version” or “Review conflict” when those actions are present. Color, blur,
opacity, and icon shape are secondary cues only.

## Optional AI merge surface

The AI section should be an opt-in “Explain differences” or “Suggest a merge”
row, not the default authority. The visual contract is:

~~~text
canonical diff
  -> deterministic merge policy
  -> optional generated suggestion
  -> user review
  -> deterministic revalidation
  -> commit or new-conflict state
~~~

Show the model/fallback status, source revisions, and the fields it considered.
Keep generated prose short and editable. If the model is unavailable, show the
same canonical diff and deterministic actions. If generated output is invalid,
hide only the suggestion—not the conflict resolution itself.

The app should never present an AI suggestion as “synced,” “safe,” “correct,”
or “approved.” Only a successful deterministic local/remote commit may update
the relevant evidence state.

## Design acceptance checklist

- [ ] Local save and remote confirmation are visibly different.
- [ ] Offline, pending, account-unavailable, migration, and conflict states
  preserve useful local content and recovery.
- [ ] Record identity and revisions are stable and accessible.
- [ ] Conflict review shows local/server/ancestor values and deterministic
  actions; it does not rely on generated prose.
- [ ] Account switch and logout cannot merge private data across users.
- [ ] Migration failure preserves a safe recovery/export path.
- [ ] Liquid Glass is limited to functional status/action groups and remains
  legible with reduced effects and large text.
- [ ] VoiceOver, Switch Control, keyboard/pointer input, Dynamic Type, and
  reduced-motion paths are tested.
- [ ] AI proposals are marked generated, source-bound, optional, and always
  revalidated before a commit.

## Sources

- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [ModelContainer](https://developer.apple.com/documentation/swiftdata/modelcontainer)
- [ModelContext](https://developer.apple.com/documentation/swiftdata/modelcontext)
- [Concurrency support](https://developer.apple.com/documentation/swiftdata/concurrencysupport)
- [VersionedSchema](https://developer.apple.com/documentation/swiftdata/versionedschema)
- [SchemaMigrationPlan](https://developer.apple.com/documentation/swiftdata/schemamigrationplan)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5)
- [CKSyncEngine.State](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/state-swift.class)
- [CKSyncEngine.Event.AccountChange](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event/accountchange)
- [CKError.serverRecordChanged](https://developer.apple.com/documentation/cloudkit/ckerror/serverrecordchanged)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
