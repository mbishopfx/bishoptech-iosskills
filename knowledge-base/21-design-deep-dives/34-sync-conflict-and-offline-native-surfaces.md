# Offline, sync, conflict, and native data surfaces

## Design objective

An Apple-native sync experience makes data state legible without making the person think about transport protocols. The record remains the hero. Sync status qualifies it, conflict resolution gives it a safe next action, and the system owns account or settings handoffs where Apple provides a native route.

The visual goal is coherent native hierarchy, not a replica of an Apple app. Use Liquid Glass to group a small number of related controls and status elements. Do not cover the record with translucent panels merely because the app has a remote service.

## Start with the state, not the badge

Define the state machine before choosing icons, colors, or materials:

| State | Person-facing meaning | Primary action |
| --- | --- | --- |
| Local | Saved on this device | Continue editing or close |
| Pending | The local edit is queued | Keep working; optionally retry |
| Synced | The known remote copy matches this device | Continue |
| Offline | The app cannot currently reach the remote route | Keep local work; explain retry |
| Account unavailable | iCloud access is unavailable or restricted | Use local-only mode or open the system account/settings route |
| Updated elsewhere | Another device changed the record | Review the updated value |
| Conflict | Two edits cannot safely merge | Compare, keep one, or edit a combined draft |
| Deleted elsewhere | The remote copy was deleted | Restore locally, discard, or create a new record |
| Schema/error | The app cannot safely apply the change | Preserve local data and offer recovery/support |

Never use one “syncing” spinner for all of these. A spinner hides whether a save was local, whether a remote notification arrived, or whether a conflict needs human attention.

## Native composition pattern

Use this composition as a default:

~~~text
record content
  ├─ small inline state: pending / offline / updated elsewhere
  ├─ primary task controls
  └─ optional detail affordance
       └─ sheet or inspector:
            what changed
            when it changed
            what is local and what is remote
            deterministic actions
            privacy-safe diagnostics
~~~

The inline state should be readable in a list row and announceable to VoiceOver. The detail surface can contain comparison content, but it should not require the person to understand record IDs, change tokens, container identifiers, or raw server error codes.

For sensitive content, make the preview safe under lock-screen or shared-screen conditions. Show a neutral status such as “Needs review” rather than rendering the full conflicting text in a notification or exposed overlay.

## Liquid Glass as semantic grouping

Liquid Glass should support hierarchy and focus:

- place related sync controls in one compact glass group;
- keep a conflict comparison readable against its background;
- use contrast and material behavior that survives light/dark appearance and increased contrast;
- avoid stacking several glass layers behind every row;
- keep hit targets large enough when the material appears to float;
- let content scroll and adapt rather than pinning a permanent translucent dashboard;
- prefer native toolbar, sheet, navigation, alert, and confirmation patterns for system-adjacent actions.

Good uses include a compact status control in a toolbar, a focused review bar above a record, and a bottom action group in a conflict sheet. Poor uses include making the entire data table a blur surface, hiding a disabled state behind low contrast, or turning a remote error into a decorative animation.

Treat material as a state-dependent presentation:

| State | Surface treatment | Motion |
| --- | --- | --- |
| Synced | Quiet, low-emphasis status | No continuous animation |
| Pending | Small progress or queued indicator | Short transition after a local edit |
| Offline | Clear text plus optional neutral icon | No looping “network” motion |
| Conflict | Higher-emphasis review group | One purposeful reveal of the comparison |
| Account unavailable | Settings/local-only explanation | System handoff feedback only |
| Resolved | Return to the record’s normal hierarchy | Short completion transition, then settle |

Reduced Motion must still leave the state obvious. Do not make a person wait for a morph or pulse to discover that a record is conflicted.

## Conflict review as an editor

A conflict is an editing task, not a toast. The review surface should answer:

1. What record is this?
2. Which value is on this device?
3. Which value came from elsewhere?
4. When were the values observed?
5. What will happen if I keep, replace, combine, or cancel?
6. Can I undo or recover the discarded value?

For text, a side-by-side comparison may work on a wide iPad layout, while a stacked comparison with explicit headings is safer on iPhone. For structured records, compare fields with a stable label and avoid showing a raw JSON diff as the primary interface. For images/audio/documents, show thumbnails or metadata and preserve the original assets until the decision is committed.

Keep AI suggestions in a third lane:

| Lane | Meaning |
| --- | --- |
| This device | User-owned local edit |
| Other device/server | Observed remote version |
| Suggested merge | Optional generated proposal, not yet truth |

The suggested merge must be editable, dismissible, provenance-labeled, and invalidated when either source changes. Confirmation applies the app’s deterministic mutation; the model does not perform the mutation merely by producing text.

## Offline-first hierarchy

Offline mode should feel like a capability state, not a failure screen:

- show the locally available record;
- let the person create or edit work that is safe to keep locally;
- show pending state near the affected record;
- provide a manual retry only when it is useful;
- avoid promising a deadline for system-scheduled sync;
- explain which features need the account or network;
- restore normal status after reconciliation.

If a feature truly requires remote authorization, block only that action and preserve the rest of the local screen. Do not replace an entire app with a network error because one remote operation failed.

## Account and privacy surfaces

An iCloud account transition is not a generic error. Use a clear route:

~~~text
account available
  -> sync-enabled

no account / restricted / temporarily unavailable
  -> local-only explanation
  -> optional system settings handoff
  -> re-check on return
~~~

Do not infer that a person saw a remote update because a silent push was scheduled. Do not show private record content in a notification unless the product has explicitly designed and tested that exposure. Use a redacted or generic preview for sensitive records and keep the full comparison behind the unlocked app.

Privacy copy should answer what stays on device, what syncs to the private or shared database, what a shared participant can see, and what deletion means. Keep credentials and tokens out of the persisted record UI.

## Accessibility and alternate input

Sync state must be understandable without color, animation, audio, or haptics:

- expose a text label such as “Saved on this device; waiting to sync”;
- give a conflict action a meaningful accessibility label and hint;
- make comparison headings part of the reading order;
- ensure Dynamic Type does not truncate the state or hide the action;
- provide keyboard, switch, Voice Control, and pointer paths for keep/merge/cancel;
- move accessibility focus to the conflict heading when the review sheet opens, but verify that focus does not become disorienting;
- allow the person to reach the record when a decorative material fails or transparency is reduced;
- test right-to-left layouts, long localized status strings, and large accessibility text.

Use haptics or animation as reinforcement only. A person using VoiceOver should be able to complete the same conflict task and understand the same outcome.

## Extension and system-surface projections

Widgets, controls, Live Activities, notifications, and other extensions are separate processes and have different freshness and privacy contracts. Publish a small projection:

| Surface | Safe projection |
| --- | --- |
| Widget | Last known value plus stale/pending label; deep link to review |
| Control | Idempotent action over a known local state; report unavailable state |
| Live Activity | Time-bounded operational state; end or mark stale when authority is lost |
| Notification | Neutral reminder or review prompt; do not claim server completion |
| App Intent | Resolve the current record and confirmation requirements again |

An extension’s cached snapshot is not proof that the app’s main model is current. On entry to the main app, reconcile the record and invalidate stale proposals.

## Performance and visual calm

Do not re-render a full conflict screen for every sync event. Debounce status-only updates, keep comparison work off the main actor when safe, and load large assets only when the person requests them. Measure:

- time from local save to visible pending state;
- time to show a conflict after a remote change is applied;
- memory used by two large comparison assets;
- scroll hitching in lists with frequent status changes;
- battery/network behavior during a long reconciliation;
- VoiceOver announcements when several rows update together.

The system should feel calm even when synchronization is busy. A high-frequency cloud callback is an implementation detail, not a reason for continuous motion.

## Review checklist

- Does every status have plain-language text?
- Can the person continue safely while offline?
- Does the conflict surface identify local, remote, and suggested values?
- Is the suggested AI merge separate from the committed value?
- Is the system account/settings route used for account configuration?
- Does the Liquid Glass grouping improve hierarchy at every size?
- Do Dynamic Type, VoiceOver, Reduce Motion, reduced transparency, RTL, and keyboard paths work?
- Are notifications and extensions privacy-safe and stale-aware?
- Does the UI avoid claiming that a record reached iCloud when only local save completed?

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Accessibility testing](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
