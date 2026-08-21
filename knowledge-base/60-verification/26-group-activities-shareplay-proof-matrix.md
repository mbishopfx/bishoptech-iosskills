# Group Activities and SharePlay proof matrix

Use this matrix to distinguish a local collaborative UI from an actual FaceTime/Messages/AirDrop SharePlay session, a message send from convergence, and a journal transfer from durable shared storage. Record SDK, deployment targets, OS builds, devices, account/content state, FaceTime/Messages context, participant actions, and server/persistence environment.

## Evidence levels

| Level | Can prove | Cannot prove by itself |
| --- | --- | --- |
| Documentation | Activity, session, messenger, journal, capability, and HIG contracts | Project entitlements, system invitation, multi-device behavior |
| Source/compile | Codable activity, metadata, state/message types, target membership, availability branches | FaceTime/Messages activation, participant join, delivery, persistence |
| Preview/UI test | Local/shared-state screens, participant copy, accessibility, Liquid Glass, fallback | System share sheet, GroupSession, participant identity, real delivery |
| Simulator | Layout, fixture protocol, local reconciliation, some app lifecycle | Real FaceTime/Messages session, two-device participant state, journal delivery |
| Signed physical device | Selected target capability, share surface, session/join/leave path | Universal device/OS support, content licensing, stable network convergence |
| Two-device system run | FaceTime/Messages/AirDrop activity activation, participants, message/journal behavior | Durable server truth, all participant/network conditions, future OS behavior |
| Production collaboration | Observed activity/persistence for the tested group | Universal delivery, every conflict pattern, privacy or moderation compliance |

## Target and activity configuration matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Group Activities import | Build the named app target with selected SDK | Wrong target/platform, unavailable symbol | The selected target can compile the route |
| Group Activities capability | Signed entitlements and target configuration | Capability absent, extension target incorrectly configured | The selected app artifact carries the capability |
| Activity identifier | Registry/release review and test uniqueness | Identifier changed, duplicate activity types | Activity identity is stable for the tested version |
| Codable payload | Encode/decode fixtures and migration tests | Non-Codable field, oversized/private payload | Payload serializes for the selected route |
| Transferable/ShareLink | Share-link fixture and supported target | Missing representation, wrong type, share sheet omitted | Activity can use the tested share surface |
| Activity metadata | System UI review for title/type/image/fallback | Truncation, private document data, misleading description | Metadata is readable for the tested activity |
| Platform matrix | Build each supported app target | iOS-only assumption, visionOS/tvOS mismatch | Support is claimed only for recorded targets |
| Content/account access | Two-device entitlement/subscription fixture | One participant cannot load content, paywall blocks join | Selected access behavior is understood |

## Activation and invitation matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| GroupStateObserver | Eligibility changes during FaceTime/no-call transition | UI stale, false interpreted as permanent unavailable | App reacts to the tested eligibility state |
| SharePlay action | Explicit user action starts prepare/activate | Hidden auto-start, wrong activity payload | Activation was requested from the intended context |
| prepareForActivation | Local/shared/cancel result fixtures | Local choice treated as shared, cancel ignored | The selected activation result is handled |
| activate | Physical FaceTime/nearby context and result | Throws/no session/hand-off false result ignored | Activity activation was observed for the tested context |
| Sharing controller/share sheet | Physical invitation run | No active call, copy/share path missing | System invitation route works for the selected device |
| Messages join | Activity message and recipient join | App absent, wrong version, stale link | Messages join behavior is observed for tested devices |
| AirDrop/nearby route | Supported physical proximity run | Unsupported platform, no prompt, privacy mismatch | Nearby initiation is proven only for tested conditions |
| Solo fallback | No-call or declined activation path | App blocks local use or claims joined | Local mode remains honest and usable |

## Session lifecycle matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| sessions AsyncSequence | Activity launch delivers a GroupSession | Session never observed, task canceled, duplicate listener | Session delivery works for tested activity/device |
| waiting state | UI loads content before join | App sends shared state too early | Waiting is handled without shared-only claims |
| join | Physical device calls join and reaches joined | Join error, queued messages misunderstood | Device joined the tested activity |
| active participants | Add/remove/late participant sequence | Presence stale, private identity exposed | Participant projection works for tested group |
| state changes | joined/invalidated/reason trace | Invalidated session reused | State transitions are reconciled |
| leave | Person navigates away/stops sharing | Listener continues, shared UI remains active | Leave stops the selected local participation |
| invalidation | System/network/user invalidation and cleanup | Orphaned tasks, stale controls, local state lost | Invalidated recovery works for tested path |
| process restart | Kill/relaunch with active or ended activity | Duplicate join, stale session object | Relaunch behavior is understood for tested OS |

## Messenger protocol matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Message schema | Codable fixture, version, event ID, revision | Raw view state, secret/context leakage | Message contract is explicit |
| Reliable mode | Lost/delayed message fixture with known participants | Assumed late-join replay, duplicate apply | Reliable attempt behaves for tested participants |
| Unreliable mode | Time-sensitive reaction/cursor fixture | Critical mutation lost | Disposable event uses appropriate mode |
| Participant subset | Role-based subset send and receive | Wrong participant gets private content | Subset behavior works for tested roles |
| Receive validation | Malformed/old/duplicate/out-of-order messages | Direct persistence, crash, wrong revision | Validation and idempotence work |
| Conflict rule | Simultaneous edit fixture | Divergence, invisible last-writer rule | Selected conflict policy converges for tested case |
| Reconnect | Network interruption/rejoin fixture | Duplicate mutation, lost baseline | Reconnect behavior is bounded for tested route |
| Canonical commit | Server/CloudKit/domain write trace | Messenger treated as database | Shared truth is persisted by selected authority |

## Journal and attachment matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Add attachment | Valid Transferable/data fixture and journal trace | Oversized/corrupt content, wrong type | Selected attachment was added |
| Receive attachment | New/late participant loads and validates data | Missing data, unsafe file, no provenance | Attachment projection works for tested device |
| Late join baseline | Join after multiple messages and attachments | Unbounded replay, stale state | Late join receives the intended baseline |
| Remove/revoke | App/server removal policy and device observation | Journal assumed durable delete | Selected removal behavior is documented |
| Retention/privacy | Local storage/log audit | Private files copied to shared area | Tested data scope follows policy |
| Large/slow transfer | Cancellation, progress, process termination | UI hangs, partial file accepted | Selected resource behavior is understood |

## Shared media and spatial matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Coordinated playback | Two-device play/pause/seek trace | Local clock shown as group truth | Tested playback synchronization works |
| Buffering | One device slow/offline | Group progress claims completion | Local buffering is separate from shared intent |
| Content entitlement | Subscriber/non-subscriber join fixture | Paywall blocks or leaks content | Access behavior is proven for selected accounts |
| Picture in Picture/background | Navigate away while call remains | Activity ends unexpectedly, state stale | Tested background behavior works |
| visionOS shared context | Physical supported spatial devices and Persona route | iOS assumptions applied to immersive space | Spatial behavior is claimed only for tested route |
| Private/shared windows | Multi-window review and lock/privacy state | Private window accidentally shared | Shared scope is visible for tested surfaces |

## Privacy, accessibility, and AI matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Shared payload minimization | Payload review and redacted logs | Entire database, tokens, private prompt included | Selected activity data is minimized |
| Participant identity | Presence UI and privacy review | Full contact data exposed | Tested participant display follows policy |
| VoiceOver | Start/join/participant/change/leave tasks | State only visual, focus lost on join | Selected shared task is accessible |
| Dynamic Type/localization | Long activity titles and largest text | Metadata/UI truncation | Tested app-owned surfaces adapt |
| Reduced effects | Reduced motion/transparency/high contrast | Glass hides shared/private state | Fallback remains legible |
| AI input selection | Private versus explicitly shared fixture | Hidden context broadcast | Model input scope is recorded |
| AI review | Proposal, ambiguity, participant approval, typed message trace | Auto-commit or role bypass | AI remains upstream of shared side effect |
| No-model fallback | Model unavailable/canceled path | Activity blocked by AI | Manual shared/local flow remains usable |

## Required evidence packet

- SDK, deployment targets, OS builds, device models, and platform route.
- Group Activities capability and signed entitlement record.
- Activity identifier, metadata, payload schema, and Transferable/share route.
- FaceTime/Messages/AirDrop/nearby context and participant actions.
- Activation result, session state, join/leave/invalidation timeline.
- Participant presence, message IDs/revisions, delivery mode, conflict result.
- Journal attachment metadata, late-join, cancellation, and retention evidence.
- Canonical persistence/server/CloudKit reconciliation if used.
- Accessibility, localization, Dynamic Type, reduced effects, privacy, and shared/private window review.
- AI proposal input scope, model availability, participant review, validation, and commit trace.

## Claim language

Use:

- “The activity was activated from a FaceTime call on the tested devices.”
- “The selected participants joined and received the tested revision.”
- “The journal made this attachment available to the late participant.”
- “The app continued locally after activation was declined.”
- “The AI proposed a shared edit that the participant reviewed.”

Avoid “SharePlay sync is guaranteed,” “the activity is always available,” “the journal is cloud storage,” or “AI collaboratively changed the document” without the matching evidence.

## Sources

- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [GroupActivity](https://developer.apple.com/documentation/groupactivities/groupactivity)
- [GroupActivityMetadata](https://developer.apple.com/documentation/groupactivities/groupactivitymetadata)
- [Defining your app’s SharePlay activities](https://developer.apple.com/documentation/groupactivities/defining-your-apps-shareplay-activities)
- [Presenting SharePlay activities from your app’s UI](https://developer.apple.com/documentation/groupactivities/promoting-shareplay-activities-from-your-apps-ui)
- [GroupStateObserver](https://developer.apple.com/documentation/groupactivities/groupstateobserver)
- [isEligibleForGroupSession](https://developer.apple.com/documentation/groupactivities/groupstateobserver/iseligibleforgroupsession)
- [prepareForActivation](https://developer.apple.com/documentation/GroupActivities/GroupActivity/prepareForActivation%28%29)
- [activate](https://developer.apple.com/documentation/groupactivities/groupactivity/activate%28%29)
- [GroupSession](https://developer.apple.com/documentation/groupactivities/groupsession)
- [GroupSession.State](https://developer.apple.com/documentation/groupactivities/groupsession/state-swift.enum)
- [GroupSession.Sessions](https://developer.apple.com/documentation/groupactivities/groupsession/sessions)
- [Joining and managing a shared activity](https://developer.apple.com/documentation/groupactivities/joining-and-managing-a-shared-activity)
- [GroupSessionMessenger](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionJournal](https://developer.apple.com/documentation/groupactivities/groupsessionjournal)
- [Synchronizing data during a SharePlay activity](https://developer.apple.com/documentation/groupactivities/synchronizing-data-during-a-shareplay-activity)
- [SharePlay HIG](https://developer.apple.com/design/human-interface-guidelines/shareplay)
- [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
