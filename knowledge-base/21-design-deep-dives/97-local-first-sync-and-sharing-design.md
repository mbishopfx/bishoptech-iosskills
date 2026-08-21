# Local-first sync, sharing, and conflict design

## Design objective

A local-first app should remain useful on one device, make cloud state visible
without becoming noisy, and recover honestly when multiple devices or people
change the same record.

The design must answer:

- what is saved locally;
- what is pending upload;
- what is current from the server;
- what conflicted;
- who can see or edit the record;
- what happens on sign-out or iCloud unavailability;
- whether an AI proposal is unreviewed, approved, or stale;
- what a widget, Live Activity, or App Intent is allowed to show.

Do not use a spinning cloud icon as the entire sync model.

## State model

Use a record-level or operation-level state:

    local-only
      -> pending
      -> syncing
      -> synced

    pending/synced -> conflict -> resolved
    any cloud state -> accountUnavailable
    any cloud state -> permissionDenied
    any pending state -> canceled/deleted

The state is domain data, not just network status. A record can be locally usable
while pending, and a synced record can still be stale relative to a remote change.

### Compact status language

| State | Useful copy | Avoid |
| --- | --- | --- |
| Local | “On this iPhone” | “Cloud saved” |
| Pending | “Waiting to sync” | “Saved everywhere” |
| Syncing | “Syncing changes” | Indeterminate spinner only |
| Synced | “Synced” or omit when unimportant | Guaranteed on every device |
| Conflict | “Needs review” | Silent overwrite |
| Account unavailable | “iCloud unavailable” | “Deleted” |
| Permission denied | “Read-only” or repair route | Mutations that will fail |
| Shared | “Shared with…” | Public claim |
| AI proposal | “Suggestion” | Approved fact |
| AI approved | “Applied” | Model-origin hidden when trust needs it |

## SwiftData versus CKSyncEngine

Choose a visual language that reflects the technical owner:

- SwiftData automatic sync can remain mostly invisible for ordinary records;
- CKSyncEngine requires a clearer pending/conflict state because the app owns the
  local/remote record exchange;
- local-only SwiftData should not show cloud affordances;
- a custom server route should use its own connectivity/error language.

The app may expose a compact sync detail screen, but the primary content should
not be covered by a cloud dashboard. Let the person keep working locally.

## Liquid Glass and native hierarchy

Use Liquid Glass in app-owned review and status surfaces:

- a sync detail sheet;
- a conflict comparison card;
- a compact “pending changes” toolbar;
- a share-permission action cluster;
- an AI proposal review surface.

Keep system-owned treatments system-owned:

- iCloud/account prompts;
- CloudKit sharing UI;
- widgets and Live Activities;
- App Intent confirmations and errors;
- system activity indicators and accessibility announcements.

A glass card should reinforce hierarchy, not turn network state into decorative
chrome. Use semantic tint roles for pending, conflict, denied, and approved; never
rely on color alone.

## Conflict design

A conflict is a difference with consequences, not merely an error code.

Show:

- record title/identity with privacy-safe context;
- local version and remote version;
- which fields differ;
- timestamps only when meaningful;
- owner/participant role;
- choices such as keep local, keep remote, merge, or review;
- what will be written;
- whether undo or recovery is possible.

For AI-generated fields, distinguish:

    source facts
      -> local proposal
      -> remote proposal
      -> approved value

Do not place two AI strings side by side and ask the person to guess which is
true. Link each candidate to source revision and model metadata in the detail
route.

## Sharing and role design

CloudKit sharing creates owner and participant relationships. Design roles as
current access state:

| Role | Can see | Can edit | UI route |
| --- | --- | --- | --- |
| Owner | Shared record and controls | According to product policy | Manage participants/share |
| Editor participant | Shared record | Allowed fields/actions | Leave share/report access |
| Viewer participant | Shared record | No mutation | Read-only state |
| Removed participant | No shared record | No | Recovery/empty route |
| Pending invitation | Limited metadata | No | Accept/decline system route |
| Account unavailable | Local policy only | No cloud mutation | Sign-in/Settings repair |

Use the standard sharing UI where it is appropriate. Do not rebuild a private
participant-management system without a clear reason.

## Account and offline design

Offline-first does not mean cloud-independent. Use a small status indicator and a
detail route that explains:

- last successful sync;
- pending count;
- current account;
- local-only records;
- retry and manual-sync actions;
- conflict count;
- privacy/delete behavior.

When the account changes:

1. stop cloud writes;
2. quarantine or clear account-scoped outbox;
3. remove sensitive cloud projections;
4. rebuild from the new account;
5. show local-only data separately;
6. ask before destructive cleanup when the product allows recovery.

## AI and cross-device trust

A model output generated on device A should not silently become approved truth on
device B. Sync either:

- the source record and rerun a compatible local proposal;
- the proposal with review status and source/model revision;
- the user-approved result with provenance.

The receiving device should show:

- source changed;
- model unavailable;
- approval required;
- account/permission mismatch;
- older model version;
- result already applied.

Private prompts, raw embeddings, and intermediate model tensors should not be
included in a sync record by default.

## Projections to widgets and system surfaces

A widget should say “Waiting to sync” when the local record is pending and the
distinction matters. An App Intent should resolve the current local record, not a
stale cloud cache. A Live Activity should reflect the event's durable state and
not remain active because a push was once sent.

Projection revision should advance only after the local transaction reaches the
chosen boundary. If a remote change is fetched but not merged, keep the pending
state explicit.

## Accessibility and localization

Sync status and conflict controls must be accessible:

- VoiceOver announces local/pending/synced/conflict/denied state;
- buttons identify the side they keep or merge;
- Dynamic Type preserves both versions in a conflict view;
- color is paired with text/icon/trait;
- Voice Control can choose Keep Local, Keep Remote, Merge, or Review;
- Switch Control reaches participant and privacy actions;
- RTL and long localized names do not hide the changed field;
- dates, account names, and participant labels are localized and privacy-safe.

Do not announce a record as “synced” when only the local write succeeded.

## Review checklist

- Is the local write useful without network?
- Does the person know whether a change is pending or synced?
- Are private/shared/public scopes distinct?
- Does every conflict have a deterministic policy?
- Does sign-out prevent the old account's outbox from uploading?
- Are shares and permissions rechecked at mutation time?
- Are AI proposals separated from approved records?
- Do widgets and Live Activities display the correct projection revision?
- Is the iCloud/CloudKit system UI used where appropriate?
- Are the physical multi-device and release environments tested?

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [CKSyncEngineDelegate](https://developer.apple.com/documentation/cloudkit/cksyncenginedelegate)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Sharing CloudKit Data with Other iCloud Users](https://developer.apple.com/documentation/cloudkit/sharing-cloudkit-data-with-other-icloud-users)
- [Shared Records](https://developer.apple.com/documentation/cloudkit/shared-records)
- [CKShare](https://developer.apple.com/documentation/cloudkit/ckshare)
- [Configuring iCloud services](https://developer.apple.com/documentation/xcode/configuring-icloud-services)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/accessibility/)
