# SwiftUI Group Activities and SharePlay collaborative-native review

This deep dive extends the existing [Group Activities and SharePlay system routes](../44-system-services/05-group-activities-shareplay.md), [Group Activities route](../50-capability-recipes/32-group-activities-shareplay-route.md), [collaborative native-surface design](../21-design-deep-dives/29-shareplay-and-collaborative-native-surfaces.md), and [SharePlay proof matrix](../60-verification/26-group-activities-shareplay-proof-matrix.md) with a stricter SwiftUI-owned review boundary for iOS 26-era apps.

The important distinction is:

~~~text
app-owned activity/document/game state
  -> GroupActivity definition and system metadata
  -> user-selected activation or share-sheet handoff
  -> system-created GroupSession
  -> local join and participant projection
  -> Messenger/Journal/media synchronization
  -> local validation and revision reconciliation
  -> participant-visible review
  -> explicit shared or durable commit
  -> leave/invalidate/solo fallback
~~~

Group Activities creates a coordinated experience. It does not become the app’s identity provider, database, authorization server, conflict resolver, content-licensing system, or automatic shared-truth layer.

## What the official contracts establish

| Contract | Official boundary | App-owned responsibility |
| --- | --- | --- |
| GroupActivity | A Codable activity type with a unique activity identifier, metadata, activation, session delivery, and optional transfer representation | Keep the payload small, versionable, privacy-safe, and sufficient to locate the intended local content. |
| Group Activities capability | An app-target capability that adds the entitlement/provisioning configuration | Configure each target deliberately; do not assume an import proves entitlement or distribution support. |
| GroupStateObserver | An eligibility signal for whether a group session can be started in the current system context | Keep a discoverable share route when eligibility is false and represent the signal as state, not as a permanent capability verdict. |
| prepareForActivation | A system activation choice that can lead to group, local, or cancellation behavior | Handle every result honestly and keep solo mode usable when it is valid. |
| GroupSession | A system-created session for an in-progress activity, delivered asynchronously | Hold the session for the activity lifetime, join when local UI/state is ready, observe state, and leave/invalidate cleanly. |
| GroupSession.State | waiting, joined, or invalidated with a reason | Do not send shared state before the joined boundary; release session resources after invalidation. |
| Participants | The session’s current participants and their platform/session data | Keep participant presentation privacy-safe and separate from app account/authentication identity. |
| GroupSessionMessenger | Asynchronous transfer of small app-specific Data or Codable messages with a selected delivery mode | Define schema, revisions, event IDs, participant scope, idempotence, expiry, and reconciliation. |
| GroupSessionJournal | Larger file/data attachment route that supports later participants within the framework’s limits | Validate content, size, provenance, retention, and deletion policy; use durable storage when required. |
| Coordinated media | AVFoundation can synchronize supported media playback without custom messages | Keep each device’s player, buffering, entitlement, and local output state separate from shared intent. |
| ShareLink/share sheet | SwiftUI/system entry points for presenting a shareable activity | Let the system own invitation UI and use concise, privacy-safe metadata. |

## Define the activity as context, not the database

The activity value should answer: “Which experience should the system invite people to join?” It should not contain every private note, account token, large binary, or mutable database record.

The minimum contract is:

- a stable, unique activityIdentifier for each activity type;
- Codable activity data;
- GroupActivityMetadata with concise title, subtitle/description, type, and useful image/fallback information;
- a content/document/game identifier that the receiving device can resolve;
- a schema/version policy;
- optional Transferable conformance when the activity is placed in a SwiftUI ShareLink or share sheet;
- a local access check before the shared UI claims that the experience is ready.

When the same activity type supports many content items, use one stable activity identifier and carry a versioned content reference. Do not create a new identifier for every document or title. Conversely, do not overload one activity type with incompatible state machines.

The metadata is system-facing copy. It should be concise enough for a SharePlay banner or share sheet and should not expose private document text, local file paths, hidden prompts, or account identifiers.

## Target and entitlement boundary

Configure the Group Activities capability on the app target that owns the shared experience. Apple’s Xcode guidance states that Group Activities is not available in widgets, extensions, or App Clips, and the capability adds the group-session entitlement to the app target.

Record a matrix rather than assuming one import covers the product:

| Target | Group Activities | SwiftUI shell | Shared content | Proof |
| --- | --- | --- | --- | --- |
| iPhone app | Required for SharePlay | Native | Activity-specific | Signed physical device plus FaceTime/Messages run |
| iPad app | Required if supported | Native/adaptive | Activity-specific | Signed iPad run and size-class review |
| Mac app | Deliberate support decision | SwiftUI/AppKit as selected | Activity-specific | Named target and system context |
| tvOS app | Deliberate support decision | Platform-specific | Coordinated media or activity | Target/API/system proof |
| visionOS app | Separate spatial design | SwiftUI/RealityKit | Shared space/Persona where selected | Physical supported spatial run |
| watchOS/widget/App Clip/extension | Do not assume support | Separate route | Handoff or companion fallback | Explicit unsupported/alternate path |

If a person must sign in, download content, or satisfy an entitlement before joining, present that work before the shared activity UI. The SharePlay HIG emphasizes reducing friction so that one participant does not keep the group waiting for avoidable setup.

## Activation is a user decision and a system handoff

Use a clear activation state machine:

~~~text
local ready
  -> user taps SharePlay/share action
  -> prepareForActivation or activate
  -> system result:
       local
       group
       cancel/error
  -> if group:
       system invitation or FaceTime/Messages/nearby handoff
       -> GroupSession delivery
  -> if local:
       continue without claiming a session
~~~

GroupStateObserver’s eligibility is useful for status and affordance copy. It is not a reason to remove the only sharing entry point: a person may still use the system share sheet or start a conversation through the documented route.

Activation evidence must distinguish:

- the button was rendered;
- prepareForActivation returned a result;
- activate was requested;
- the system showed a share/invitation surface;
- the activity reached another device;
- the other device received a session;
- the other participant joined.

Do not draw a fake FaceTime banner, fake SharePlay icon, or app-owned invitation surface that looks like a system confirmation. Use ShareLink, the documented share-sheet path, or the current system presentation API for the selected target.

## GroupSession ownership and state

The app never constructs a GroupSession directly. The system delivers it asynchronously from the activity’s sessions() sequence. A SwiftUI feature model or dedicated session coordinator should own:

- the current session and its UUID;
- the activity payload and content revision;
- the current session state;
- the current participant projection;
- a strong GroupSessionMessenger reference;
- a GroupSessionJournal reference when needed;
- listener tasks and cancellation;
- local and shared state reducers;
- a generation token that rejects callbacks from an old session.

The session normally moves through:

~~~text
no session
  -> waiting
  -> joined
  -> invalidated(reason:)
~~~

Call join only after the local feature has enough state to display the activity. Apple’s joining guidance says messages sent before the session reaches joined may be queued; still, the app should not use that behavior as a substitute for its own state gate. Call leave when the person leaves the shared feature. When invalidated, do not attempt to join, leave, or end the same session again; release the session-owned resources.

The session’s activity can update as the selected activity changes. Update it only within the documented joined boundary and reconcile the new activity to the local route. A session UUID is useful for local diagnostics and stale-callback rejection; it is not an account identity or durable collaboration ID.

## Participants are session context, not authentication

Participants can inform UI and message targeting, but a participant object does not automatically prove the person’s app account, permission to edit a server record, or real-world identity.

Use a separate app-owned identity map when the product requires:

- account authorization;
- role/permission checks;
- ownership of a document or purchase;
- moderation or audit;
- a server-authoritative commit;
- a safety-sensitive or external side effect.

Keep the participant surface minimal. Prefer “3 people here” or a display name chosen under the product’s privacy policy over exposing raw identifiers. If the app shows who changed an item, retain the source participant in the local event envelope and render only the approved display representation.

## Choose the synchronization lane

| Data | Lane | Review boundary |
| --- | --- | --- |
| Cursor, transient pointer, small reaction | Messenger with an intentional unreliable mode | Dropped events are acceptable; never use as durable truth. |
| Small command or mutation | Messenger reliable mode or a selected subset | Reliable delivery is not a database or late-join replay; validate and deduplicate. |
| Current shared state snapshot | Messenger plus deterministic reconstruction, Journal, or server | Snapshot schema, revision, conflict policy, and late-join baseline. |
| Large attachment or shared image | GroupSessionJournal within its documented size limits | Validate before download/use; separate from durable storage and moderation. |
| Durable document/game record | CloudKit/server/custom persistence | SharePlay session is only the live coordination layer. |
| Movie/music playback | AVFoundation coordinated-media route | Local player/buffering/entitlement remains local. |
| Spatial shared activity | Group Activities plus the selected visionOS/SystemCoordinator route | iOS layout and visionOS shared-space behavior require separate proof. |

For Messenger messages, use an envelope such as:

~~~text
schemaVersion
eventID
sourceParticipantReference
sourceSessionID
sourceRevision
targetRecordID
operation
payload
createdAt
expiresAt
~~~

Validate the activity ID, session generation, schema, record authorization, revision, payload bounds, and idempotence key before mutating local state. A message source is useful provenance; it is not a signature for a business action.

## Reliable and unreliable messages

GroupSessionMessenger defaults to reliable delivery for its initializer, and the framework also exposes a deliberate delivery mode. Use reliable for small important state transitions when the product can tolerate the framework’s delivery semantics. Use unreliable only for disposable, time-sensitive events such as a cursor, hover, or temporary animation hint.

Neither mode should be described as:

- guaranteed delivery to every future participant;
- ordered canonical database writes;
- conflict resolution;
- authenticated business authorization;
- offline durable storage.

The incoming message sequence is asynchronous. Use MessageContext.source when source attribution matters, and cancel the listener task when the session becomes invalid. Keep the reducer idempotent so a repeated message does not duplicate the user-visible side effect.

## Journal and late-join design

Apple’s synchronization guidance distinguishes small/time-sensitive messages from larger data and attachments. A GroupSessionJournal can make activity-related attachments available to participants and later joiners; Apple’s current guidance documents a 100 MB attachment limit and end-to-end encryption for that transfer path.

Before accepting a journal item:

1. check the activity and session context;
2. validate type, size, revision, and expected content;
3. write to a bounded temporary location;
4. scan or validate according to the product’s content policy;
5. expose a loading/failed/unavailable state;
6. incorporate it through an app-owned reducer;
7. delete or retain it according to explicit local/server policy.

Use a server or durable store when the app needs central deletion, revocation, moderation, audit, access control, or files larger than the journal limit. Do not tell a person that “the group saved it” when the artifact exists only in a session attachment.

## Late joins and state reconstruction

A late participant should not depend on having received every historical Messenger event. Choose one of these baselines:

- a compact current snapshot sent through an approved path;
- a journal attachment that contains the current shared artifact;
- a server/CloudKit record with a revision;
- deterministic reconstruction from a bounded journal of events.

The new device should:

~~~text
receive session
  -> load local content
  -> join
  -> obtain baseline
  -> validate activity/revision
  -> render shared state
  -> subscribe to future messages
~~~

Do not show a half-applied shared document as if it were current. Show “Preparing shared state,” “Catching up,” or “Viewing a local copy” when the baseline is incomplete.

## Shared media

For synchronized playback, use the AVFoundation coordinated-media route where it meets the need rather than inventing a custom message protocol for every time tick. Each device still owns:

- the local player and output route;
- buffering and decode readiness;
- content entitlement;
- local pause/interrupt/Picture in Picture behavior;
- current rendered frame;
- recovery when the device falls behind.

Share only the intent and coordination state required by the activity. A play command received by a device does not prove that its player rendered the same frame at the same instant. Review drift, late join, seek conflict, and background behavior independently.

## Conflicts, authority, and external effects

Choose a conflict rule before writing code:

| Scenario | Possible rule |
| --- | --- |
| Shared canvas stroke | Append-only event with stable event ID. |
| Shared selection | Last accepted revision wins. |
| Quiz answer | Host/role authority with participant-visible status. |
| Shopping cart | Server or local merge with explicit item revision. |
| Shared game move | Turn authority plus server/persistence validation. |
| External device command | One participant role plus explicit confirmation on the controlling device. |

An AI proposal, message, journal attachment, or participant tap must not directly trigger payment, deletion, physical control, or external communication. Validate against app-owned permissions, current revision, user intent, and the required confirmation step.

## On-device AI in a shared activity

Keep local model context and shared activity input separate:

~~~text
explicitly selected shared content
  -> typed local proposal input
  -> model availability check
  -> local proposal
  -> source/revision/participant review
  -> typed shared message or durable action
  -> deterministic reducer and confirmation
~~~

Good proposals:

- summarize only the content the group selected;
- suggest a whiteboard grouping;
- draft a group itinerary;
- translate a message before sending;
- propose a conflict resolution that each role can inspect;
- suggest a next move in a game without committing it.

Bad boundaries:

- broadcasting hidden private prompts;
- including account tokens or unrelated local data;
- letting generated text select an arbitrary message type;
- auto-committing a model result to every participant;
- treating a local model result as a participant’s consent.

Use an allowlist of app-owned operations and a source revision. If the shared state changes while a proposal is running, mark it stale and require a new review.

## SwiftUI and Liquid Glass surface

SwiftUI owns the task context and state projection:

| State | User-facing surface |
| --- | --- |
| Solo | Local content and an obvious SharePlay action. |
| Preparing | Content/access/entitlement checklist before system handoff. |
| Inviting | System-owned share/invitation surface plus app-owned waiting state. |
| Waiting | “Waiting to join” with cancel and local fallback where valid. |
| Joined | Shared/private scope, participant count, current revision, and Leave action. |
| Catching up | Baseline progress or a clear unavailable state. |
| Invalidated | Activity ended reason, preserved local work, retry/solo path. |

Liquid Glass belongs around functional controls: SharePlay action, participant/status group, review, undo, and Leave. Keep shared content on a stable content layer and maintain a standard-material/opaque fallback for reduced transparency or unsupported targets.

Do not use glass to imply that a message arrived, a person consented, or a shared mutation is durable. Those are semantic states that need text, accessibility values, and proof.

## Accessibility and alternate input

The collaboration task must remain understandable with:

- VoiceOver labels and values for solo/shared/private/catching-up/invalidated states;
- a direct SharePlay/start/local/Leave route;
- accessible participant counts and selected identity display;
- Dynamic Type for activity metadata, error copy, and revision status;
- reduced motion for presence and catch-up animations;
- increased contrast/reduced transparency fallbacks;
- keyboard, pointer, Voice Control, and Switch Control routes where the target supports them;
- focus restoration when a system share sheet or activity handoff returns.

Do not announce every transient cursor or message. Announce state changes that affect the person’s task: joined, left, shared revision applied, conflict requiring review, activity ended, or local fallback.

## Proof boundary

| Evidence | Supports | Does not support |
| --- | --- | --- |
| SwiftUI fixture | State hierarchy, copy, semantic controls, local fallback | System activation or multi-device convergence |
| Compile/entitlement check | Symbols, target membership, capability, payload conformance | FaceTime/Messages invitation or participant delivery |
| Simulator | Deterministic reducers, late-join fixtures, accessibility structure | Actual GroupSession, system share sheet, physical multi-device timing |
| Signed one-device run | Selected target and local lifecycle | Two-device session, content entitlement across accounts |
| Two-device FaceTime/Messages run | Activation, session, participants, selected Messenger/Journal behavior | Durable server truth or all OS/device combinations |
| Archive/TestFlight | Signing, target metadata, release build, privacy | Universal collaboration behavior |

The implementation handoff should name the session ID, app revision, participant count, message IDs/revisions, baseline source, device/OS/build, and the exact claim level.

## Sources

- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [Configuring Group Activities](https://developer.apple.com/documentation/Xcode/configuring-group-activities)
- [GroupActivity](https://developer.apple.com/documentation/groupactivities/groupactivity)
- [GroupActivityMetadata](https://developer.apple.com/documentation/groupactivities/groupactivitymetadata)
- [GroupActivityActivationResult](https://developer.apple.com/documentation/groupactivities/groupactivityactivationresult)
- [Defining your app’s SharePlay activities](https://developer.apple.com/documentation/groupactivities/defining-your-apps-shareplay-activities)
- [Presenting SharePlay activities from your app’s UI](https://developer.apple.com/documentation/groupactivities/promoting-shareplay-activities-from-your-apps-ui)
- [GroupStateObserver](https://developer.apple.com/documentation/groupactivities/groupstateobserver)
- [isEligibleForGroupSession](https://developer.apple.com/documentation/groupactivities/groupstateobserver/iseligibleforgroupsession)
- [GroupSession](https://developer.apple.com/documentation/groupactivities/groupsession)
- [GroupSession.State](https://developer.apple.com/documentation/groupactivities/groupsession/state-swift.enum)
- [GroupSession.State.invalidated(reason:)](https://developer.apple.com/documentation/groupactivities/groupsession/state-swift.enum/invalidated%28reason%3A%29)
- [GroupSession activity](https://developer.apple.com/documentation/groupactivities/groupsession/activity)
- [GroupSessionMessenger](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionMessenger.MessageContext](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger/messagecontext)
- [GroupSessionMessenger delivery modes](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger/deliverymode-swift.enum/reliable)
- [GroupSessionJournal](https://developer.apple.com/documentation/groupactivities/groupsessionjournal)
- [Synchronizing data during a SharePlay activity](https://developer.apple.com/documentation/groupactivities/synchronizing-data-during-a-shareplay-activity)
- [Joining and managing a shared activity](https://developer.apple.com/documentation/groupactivities/joining-and-managing-a-shared-activity)
- [SharePlay](https://developer.apple.com/design/human-interface-guidelines/shareplay)
- [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Supporting coordinated media playback](https://developer.apple.com/documentation/avfoundation/supporting-coordinated-media-playback)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

## Related knowledge-base routes

- [Group Activities and SharePlay system routes](../44-system-services/05-group-activities-shareplay.md)
- [Group Activities and SharePlay route](../50-capability-recipes/32-group-activities-shareplay-route.md)
- [SwiftUI Group Activities and SharePlay collaborative-native design](../21-design-deep-dives/127-swiftui-group-activities-shareplay-review-design.md)
- [SwiftUI Group Activities and SharePlay route](../50-capability-recipes/130-swiftui-group-activities-shareplay-review-route.md)
- [SwiftUI Group Activities and SharePlay proof matrix](../60-verification/124-swiftui-group-activities-shareplay-review-proof-matrix.md)
- [SwiftUI Group Activities and SharePlay recipes](../70-code-recipes/142-swiftui-group-activities-shareplay-review-recipes.md)
