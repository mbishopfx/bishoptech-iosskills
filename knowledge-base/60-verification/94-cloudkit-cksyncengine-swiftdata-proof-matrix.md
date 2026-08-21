# CloudKit, CKSyncEngine, and SwiftData proof matrix

## Purpose

This matrix separates local persistence, sync configuration, server acceptance,
account state, sharing, conflict resolution, and system projections.

A local model container or successful network request is not sufficient proof of
sync. The route needs evidence for:

- schema compatibility and target capabilities;
- private/shared/public database selection;
- CKSyncEngine state persistence and delegate ordering;
- same-account multi-device reconciliation;
- offline edits, conflicts, deletes, and account changes;
- CloudKit sharing permissions and participant lifecycle;
- widget/App Intent/Live Activity/AI projection freshness;
- privacy, accessibility, archive, TestFlight, and production environments.

## Evidence levels

| Level | Establishes | Does not establish |
| --- | --- | --- |
| Source | Apple documents CloudKit/SwiftData behavior | Selected target schema/configuration |
| Compile | Model, CloudKit, sync engine, and sharing symbols resolve | Container/account/notification behavior |
| Fixture/unit | IDs, revisions, outbox, merge, proposal, and privacy logic | iCloud server delivery |
| Simulator | Local data and deterministic UI | iCloud account, push, two-device conflicts |
| Signed physical device | Account, network, notifications, sharing, multi-device behavior | Every production schema/release setting |
| Archive/release | Entitlements, containers, schema/resource membership | User behavior or future sync timing |

Record device model, OS build, app version/build, Xcode/SDK, iCloud account
fixture, CloudKit environment, network/power state, locale, accessibility,
container ID, and redacted artifact paths.

## Source and configuration gates

| ID | Question | Pass evidence | Boundary |
| --- | --- | --- | --- |
| SRC-01 | Is CloudKit available in the selected SDK? | Target compile | Do not infer container setup |
| SRC-02 | Is CKSyncEngine available? | Target compile and SDK status | Do not infer runtime sync |
| SRC-03 | Are CloudKit and remote notification entitlements present? | Signed archive inspection | Do not infer server delivery |
| SRC-04 | Is SwiftData automatic sync intended? | Explicit ModelConfiguration and product decision | Do not infer from iCloud capability alone |
| SRC-05 | Is the schema CloudKit-compatible? | Development schema/model review | Do not infer production deployment |
| SRC-06 | Is the database private/shared/public? | Route record and target config | Do not use CKSyncEngine for public DB |
| SRC-07 | Is sync-engine state persisted? | Relaunch/state recovery test | Do not discard opaque state every launch |
| SRC-08 | Are identifiers stable? | ID/revision fixture | Do not use array index |
| SRC-09 | Is the shared zone/hierarchy intentional? | CKShare/zone review | Do not share the whole private DB accidentally |
| SRC-10 | Is account scope enforced? | Sign-out/account fixture | Do not upload old outbox to new account |
| SRC-11 | Are widget/activity projections downstream? | Commit-order fixture | Do not reload after request creation |
| SRC-12 | Is AI provenance stored? | Proposal/approval/source revision fixture | Do not sync raw private model artifacts |

## Local model and automatic sync tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| SWIFT-01 | Local-only container | ModelConfiguration none/local | App works without iCloud | Cloud UI appears accidentally |
| SWIFT-02 | Private sync container | Compatible schema and iCloud | Same-account sync path configured | Entitlement-only claim |
| SWIFT-03 | Capability missing | Remove iCloud or remote notification | App shows repair/fallback | Silent data loss |
| SWIFT-04 | Schema constraint | Unique/nonoptional unsupported fixture | Schema review catches issue | Production migration surprise |
| SWIFT-05 | Explicit container | Multiple containers | Intended container selected | First entitlement guessed |
| SWIFT-06 | Production schema guard | Existing production schema | No incompatible initialization | Development schema pushed blindly |
| SWIFT-07 | Local write offline | No network | Local record remains usable/pending | Save blocked unnecessarily |
| SWIFT-08 | Reconnect | Pending local write | Record syncs once and projection updates | Duplicate record |
| SWIFT-09 | Account signed out | iCloud unavailable | Cloud work pauses; local policy applies | Old account write |
| SWIFT-10 | Delete | Local delete/offline | Tombstone/recovery policy is truthful | Deleted record reappears silently |
| SWIFT-11 | Relaunch | App killed with pending write | Store reopens and resumes policy | In-memory state lost |
| SWIFT-12 | Widget projection | Commit then reload | Widget shows local revision/state | Surface updates before commit |

## CKSyncEngine state and delegate tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| SYNC-01 | Early initialization | App launch | Engine exists before sync events | Late setup misses events |
| SYNC-02 | Private database | Private engine | Private records sync | Public database used |
| SYNC-03 | Shared database | Shared engine | Shared scope reconciles separately | Private/shared data mixed |
| SYNC-04 | Opaque state save | State update event | State persists atomically | Tokens lost on relaunch |
| SYNC-05 | State restore | Relaunch | Engine resumes from saved state | Full re-fetch every launch |
| SYNC-06 | Periodic sync delay | Poor battery/network | App remains truthful | Exact schedule promised |
| SYNC-07 | Manual fetch | User needs freshness | Explicit fetch route runs | Manual call inside event handler |
| SYNC-08 | Manual send | User needs upload | Explicit send route runs | Duplicate event recursion |
| SYNC-09 | Serial event | Multiple events | Delegate preserves order | Concurrent merge race |
| SYNC-10 | Send scope | Context-limited batch | Only allowed changes sent | Out-of-scope send |
| SYNC-11 | Pending outbox | Local mutations | Next batch contains unsent changes | Request creation deletes outbox |
| SYNC-12 | Fetched database change | Zone/database event | Local scope updates | Wrong database applied |
| SYNC-13 | Fetched record change | Remote edit | Merge policy executes | Remote blindly overwrites |
| SYNC-14 | Server record changed | Conflict error | Local policy resolves/reviews | Engine assumed to solve all |
| SYNC-15 | Account change | Sign-out/sign-in | Local store/outbox responds | Old account remains attached |
| SYNC-16 | Missing subscription | Fresh container | Engine can create/use route per docs | Push assumed without config |
| SYNC-17 | Cancel operation | Explicit cancel | Work stops without corrupt state | Background send continues |
| SYNC-18 | State corruption | Invalid persisted state | Rebuild/recovery route documented | User records deleted silently |

## Conflict and revision tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| CONFLICT-01 | Same field edit | Device A/B edit title | Policy is deterministic | Last callback wins accidentally |
| CONFLICT-02 | Independent fields | A title, B note | Field merge preserves both | One edit lost |
| CONFLICT-03 | Rich note | Both edit body | Review/merge route | Silent overwrite |
| CONFLICT-04 | Append event | Both append event IDs | Both stable events remain | Duplicate event |
| CONFLICT-05 | Delete versus edit | A deletes, B edits | Tombstone/review policy | Deleted content resurrects silently |
| CONFLICT-06 | AI proposal versus approval | A proposes, B approves | Approved value wins with provenance | Proposal overwrites approval |
| CONFLICT-07 | Source revision changed | Model result old revision | Result rejected/reviewed | Old output applied |
| CONFLICT-08 | Outbox duplicate | Same mutation twice | Idempotent server/local result | Double commit |
| CONFLICT-09 | Remote older | New local, old remote | Revision policy preserves newer | Older data wins |
| CONFLICT-10 | Clock skew | Different device clocks | Server/revision policy used | Wall clock alone |
| CONFLICT-11 | Partial batch | Some records fail | Counts/checkpoint truthful | All-success claim |
| CONFLICT-12 | Recovery | Conflict resolved | Projection advances once | Widget shows old conflict |

## Sharing and account tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| SHARE-01 | Create share | Private zone/root | CKShare created for intended scope | Whole database shared |
| SHARE-02 | Share hierarchy | Parent/children | Intended descendants accessible | Unrelated record exposed |
| SHARE-03 | Accept share | Participant account | Shared database appears | Link opens wrong account |
| SHARE-04 | Owner edit | Owner device | Owner mutation syncs | Participant authority assumed |
| SHARE-05 | Editor edit | Editor permission | Allowed field syncs | Read-only mutation |
| SHARE-06 | Viewer edit | Viewer permission | Mutation refused | UI says editable |
| SHARE-07 | Stop sharing | Owner stops | Participant access/cache updates | Shared data remains |
| SHARE-08 | Remove participant | Owner revokes | Participant loses access | Old cache writes |
| SHARE-09 | Leave share | Participant exits | Local shared state cleaned/policy applied | Private copy created silently |
| SHARE-10 | Account mismatch | Share link other account | System/account route handles | Wrong account accepted |
| SHARE-11 | Sign-out | Owner/participant sign-out | Outbox/engines/projections reset | Cross-account data leak |
| SHARE-12 | Privacy | Sensitive shared record | Labels/logs minimize detail | Private collaborator data logged |
| SHARE-13 | Projection | Shared record update | Widget/App Intent reflects role/state | Owner controls shown to viewer |

## AI, projection, and privacy tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| AI-SYNC-01 | Local proposal | Source revision 4 | Proposal marked unreviewed | Auto-approved |
| AI-SYNC-02 | Approved result | Person confirms | Approved value syncs with provenance | Raw prompt synced |
| AI-SYNC-03 | Other device | Model differs/unavailable | Review/rerun/fallback | Destination silently applies |
| AI-SYNC-04 | Source changed | Revision 5 | Proposal invalidated | Old proposal wins |
| AI-SYNC-05 | Private fields | Prompt/transcript/embedding | Retention policy excludes/minimizes | Sensitive artifact sync |
| AI-SYNC-06 | Account sign-out | Pending proposal | Cloud/account cache cleaned | Old proposal uploaded |
| AI-SYNC-07 | Widget pending | Local edit not synced | Pending state visible when important | Synced claim |
| AI-SYNC-08 | Live Activity | Event state remote/local | Activity revision matches domain | Push alone treated as truth |
| AI-SYNC-09 | App Intent | Entity on second device | Current account resolution | Stale local ID opens wrong record |
| AI-SYNC-10 | Search/index | Remote change | Index repair follows commit | Deleted title searchable |
| AI-SYNC-11 | Lock state | Device locked | Sensitive projection redacted | Bystander leak |
| AI-SYNC-12 | Deletion | Source deleted | Proposal/output cleanup policy | Orphaned derived data |

## Physical, performance, accessibility, and release tests

| ID | Scenario | Pass evidence | Boundary |
| --- | --- | --- | --- |
| PHYS-01 | Same-account devices | Signed A/B offline edit/reconnect | Simulator |
| PHYS-02 | Different accounts | Share owner/participant | Same account only |
| PHYS-03 | Network loss | Offline/poor/recovery | Wi-Fi happy path |
| PHYS-04 | iCloud sign-out | Settings/account transition | App toggle only |
| PHYS-05 | Background notifications | Remote change wake/update | Local fetch |
| PHYS-06 | Process termination | Kill/relaunch with outbox/state | Warm process |
| PHYS-07 | Storage/protected data | Locked/low storage | Full battery |
| A11Y-01 | VoiceOver conflict | Reads changed fields/actions | Screenshot |
| A11Y-02 | Dynamic Type | Long conflict/share labels | Default size |
| A11Y-03 | Contrast/transparency | Status remains clear | Default appearance |
| A11Y-04 | RTL/localization | Participant/date/title fixtures | English-only |
| PERF-01 | Batch size | Bounded memory/network | Small fixture |
| PERF-02 | Projection | Widget/activity refresh measured | Manual screenshot |
| PERF-03 | Thermal/battery | Representative device metrics | Newest device |
| REL-01 | Entitlements | Signed archive inspection | Local project |
| REL-02 | Container | Development/production environment | Local schema only |
| REL-03 | Sharing route | Signed TestFlight invite/accept | Preview |
| REL-04 | Migration | Existing records upgrade | Fresh install |
| REL-05 | Privacy | Redacted logs/data deletion | Source claim |

## Evidence record template

~~~yaml
test_id: CONFLICT-06
feature: synced AI classification with user approval
app_version: 0.1.0
build: 43
sdk: Xcode-selected iOS SDK
cloudkit:
  container: iCloud.com.example.app
  environment: development-or-production
  database: private
devices:
  - model: device-A
    os: iOS build
    account: synthetic-account-A
  - model: device-B
    os: iOS build
    account: synthetic-account-A
network: offline-then-online
record:
  stable_id: fixture-record
  source_revision_a: 4
  source_revision_b: 5
  proposal_model: local-model-version
  approval_revision: 5
result: pass
observed_policy: approved-value-wins-and-reviews-stale-proposal
projection_revision: 12
accessibility:
  voice_over: tested
  dynamic_type: large
artifact: redacted-artifact-path
known_limits:
  - CloudKit scheduling remains system-controlled
~~~

## Sources

- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [CKSyncEngineDelegate](https://developer.apple.com/documentation/cloudkit/cksyncenginedelegate)
- [CKSyncEngine.State](https://developer.apple.com/documentation/cloudkit/cksyncengine/state)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Sharing CloudKit Data with Other iCloud Users](https://developer.apple.com/documentation/cloudkit/sharing-cloudkit-data-with-other-icloud-users)
- [Shared Records](https://developer.apple.com/documentation/cloudkit/shared-records)
- [CKShare](https://developer.apple.com/documentation/cloudkit/ckshare)
- [Local Records](https://developer.apple.com/documentation/cloudkit/local-records)
- [Remote Records](https://developer.apple.com/documentation/cloudkit/remote-records)
- [Configuring iCloud services](https://developer.apple.com/documentation/xcode/configuring-icloud-services)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Testing](https://developer.apple.com/documentation/testing)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [UI testing](https://developer.apple.com/documentation/xcuiautomation)
- [Accessibility](https://developer.apple.com/accessibility/)
