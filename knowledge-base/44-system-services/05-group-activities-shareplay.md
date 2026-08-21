# Group Activities and SharePlay system routes

Group Activities lets an app define a shareable activity that people can start from FaceTime, Messages, AirDrop/share interfaces, and supported nearby experiences. The system creates a GroupSession for the activity and provides participants, session lifecycle, and data-transfer objects.

SharePlay is a co-presence and coordination route, not a general database, account system, authorization layer, or guaranteed delivery channel. Keep the boundary explicit:

    app-owned activity record
        -> GroupActivity definition and metadata
        -> system activation/invitation
        -> GroupSession delivery
        -> join/participant/session state
        -> messenger/journal synchronization
        -> local domain reconciliation
        -> leave/invalidate/offline fallback

A successful activity activation does not prove every participant joined. A message send does not prove a late participant received the state. A GroupSession is not a durable server record. A shared model proposal is not shared truth until each device validates and commits it according to the product’s rules.

## Capability map

| User outcome | Primary route | System boundary | Separate responsibility |
| --- | --- | --- | --- |
| Start a shared activity from a FaceTime call | GroupActivity and GroupStateObserver | System activity/invitation UI | App activity content and session handling |
| Let people join from Messages or a share sheet | GroupActivity + Transferable/ShareLink | Messages/share sheet handoff | Universal links, app availability, local state |
| Synchronize small commands or state | GroupSessionMessenger | Session participant/delivery behavior | Message schema, ordering, idempotence, reconciliation |
| Share larger files or attachments | GroupSessionJournal + Transferable | Journal availability to participants | Validation, storage, revocation, moderation |
| Coordinate media playback | Group Activities coordinated-media route | Playback synchronization context | Local player, content entitlement, buffering, seek policy |
| Support spatial shared activity | Group Activities + SystemCoordinator on visionOS | Shared context/Persona/spatial UI | RealityKit content and platform-specific layout |
| Continue solo when sharing is unavailable | App-owned fallback | No session or user chooses local mode | Local domain workflow and later retry |

The [Group Activities framework](https://developer.apple.com/documentation/groupactivities) uses FaceTime infrastructure to synchronize activities and invite participants. The [SharePlay HIG](https://developer.apple.com/design/human-interface-guidelines/shareplay) defines user-facing terminology, metadata, preparation, late joins, conflict handling, and private versus shared content.

## Define the activity

### GroupActivity contract

Define a value type conforming to GroupActivity. The type is Codable so the system can serialize it for other participant devices. Each activity type needs a unique activityIdentifier and metadata that helps people decide whether to join:

- concise title;
- short description;
- appropriate activity type;
- image when useful;
- optional fallback URL;
- enough content identity to load the shared experience.

The activity payload should be a launch/context value, not a complete app database or secret. Keep account-specific access checks and server fetches separate from the activity definition.

If the activity is presented through ShareLink or another share sheet, make its data Transferable as required by the chosen path. Use the [Defining your app’s SharePlay activities](https://developer.apple.com/documentation/groupactivities/defining-your-apps-shareplay-activities) guide and current target configuration.

### Capability and target

Add the Group Activities capability to the app target. Apple’s guide describes the capability as app-target configuration that adds the needed entitlements and provisioning updates. Do not assume a framework import alone is enough.

Record:

- supported platform targets;
- app version compatibility;
- activity identifier registry;
- account/subscription/content access;
- iOS/iPadOS/macOS/tvOS/visionOS differences;
- FaceTime/Messages/share-sheet entry points;
- Universal Purchase considerations if the activity crosses platforms.

The SharePlay HIG notes that watchOS is not supported for this route and that visionOS has additional shared-context/Persona design considerations. Keep platform availability explicit.

## Start and activate an activity

### Determine whether a session is eligible

GroupStateObserver exposes isEligibleForGroupSession. Apple describes it as an indicator that the system can start a group session, such as when a FaceTime call is active. Use it to update app UI, but do not hide every share entry point when it is false; present the documented GroupActivitySharingController/share-sheet route when the user wants to invite others.

The activation choice is user-facing:

    user taps SharePlay
        -> if eligible, prepareForActivation or activate
        -> system decides local/shared behavior
        -> app enters local or shared mode

prepareForActivation returns a GroupActivityActivationResult. Use it when a feature can reasonably run locally or as a shared activity so the person can choose. Use activate when the feature is inherently group-only or the current context makes direct activation appropriate.

See [GroupStateObserver](https://developer.apple.com/documentation/groupactivities/groupstateobserver), [isEligibleForGroupSession](https://developer.apple.com/documentation/groupactivities/groupstateobserver/iseligibleforgroupsession), [prepareForActivation](https://developer.apple.com/documentation/GroupActivities/GroupActivity/prepareForActivation%28%29), and [Presenting SharePlay activities from your app’s UI](https://developer.apple.com/documentation/groupactivities/promoting-shareplay-activities-from-your-apps-ui).

### Metadata and preparation

Before displaying the shared activity UI, help people complete prerequisites:

- sign in if required;
- download or select content;
- check subscription/entitlement;
- confirm the relevant document or game;
- explain what will be shared;
- give a local fallback.

Do not make the group wait while each device performs avoidable onboarding. The SharePlay HIG recommends preparing people before the activity appears and keeping the shared activity description concise enough for system UI.

## Receive, join, and manage a GroupSession

The system delivers sessions asynchronously through the activity type’s sessions() AsyncSequence. The app does not instantiate GroupSession directly.

The session state begins in waiting. When the app has loaded enough local state and is ready to participate, call join(). A successful join transitions to joined and enables synchronization. If the person navigates away or chooses to stop participating, call leave(). The session then becomes invalidated and cannot be reused.

Keep strong references to:

- the GroupSession;
- the GroupSessionMessenger;
- the GroupSessionJournal;
- participant/message listener tasks;
- the local activity coordinator.

Cancel listener tasks when the session leaves, invalidates, or the app switches to solo mode. Handle session state changes, active participant changes, late joins, app termination, network loss, and a new session for the same activity payload.

The documented session states are waiting, joined, and invalidated(reason:). Use them to drive local UI:

    noSession
        -> invitationPending
        -> sessionWaiting
        -> joined
        -> participantChanged
        -> leaving
        -> invalidated
        -> soloFallback

See [GroupSession](https://developer.apple.com/documentation/GroupActivities/GroupSession), [GroupSession.State](https://developer.apple.com/documentation/groupactivities/groupsession/state-swift.enum), [GroupSession.Sessions](https://developer.apple.com/documentation/groupactivities/groupsession/sessions), and [Joining and managing a shared activity](https://developer.apple.com/documentation/groupactivities/joining-and-managing-a-shared-activity).

## Synchronize small state with GroupSessionMessenger

GroupSessionMessenger is for small, time-sensitive Codable messages and commands. Choose a delivery mode intentionally:

- reliable attempts to ensure delivery to known participants and may resend;
- unreliable is best effort and can be appropriate for time-sensitive, disposable events.

Neither mode guarantees that a future late joiner receives an old message. Use a journal, a server snapshot, or a deterministic state reconstruction route for late joiners.

Every message should include:

- schema version;
- event ID;
- source participant ID;
- source revision or logical clock;
- target entity ID;
- action or patch type;
- expiry where the event is time-sensitive;
- idempotence key;
- validation outcome.

Use participant subsets only when the privacy/role model is explicit. A quiz host, private draft, or moderator state may not belong in every participant’s message stream.

Do not treat messenger ordering as business truth. Receive events, validate against the current domain snapshot, discard duplicates, resolve conflicts, and update the local projection. If the product needs a canonical record, commit through the app’s server or a deliberate shared persistence route.

See [GroupSessionMessenger](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger) and [Synchronizing data during a SharePlay activity](https://developer.apple.com/documentation/groupactivities/synchronizing-data-during-a-shareplay-activity).

## Share files and late-join data with GroupSessionJournal

GroupSessionJournal transfers files and data objects between participants and makes them available to people who join later. It is not a replacement for GroupSessionMessenger and not durable company storage.

Use a journal for:

- a whiteboard image or attachment;
- a document snapshot;
- a shared media asset;
- a larger activity artifact;
- a late-join baseline that is safe to distribute.

Validate before incorporating journal content:

1. expected type/UTType;
2. size and resource budget;
3. activity/session identity;
4. provenance and participant role;
5. malware/content policy if the product needs it;
6. version and migration;
7. redaction/privacy;
8. cancellation and unavailable data.

If an artifact must be deleted, revoked, moderated, or audited centrally, keep an app server or persistent collaboration store in the architecture. A journal entry is not a guaranteed delete or server retention contract.

See [GroupSessionJournal](https://developer.apple.com/documentation/groupactivities/groupsessionjournal).

## Coordinated media and shared state

For a media experience, each device still owns playback resources while Group Activities coordinates shared playback behavior. Keep:

- local player time and buffering;
- shared playback intent;
- content entitlement;
- current leader/authority policy;
- play/pause/seek revision;
- scrub conflict behavior;
- late-join catch-up;
- audio route and Picture in Picture state.

If two participants issue conflicting changes, choose a simple documented rule such as last change wins, host wins, or a server revision. The SharePlay HIG specifically calls for deliberate conflict handling instead of letting simultaneous edits produce mysterious divergence.

Do not use a shared activity as a substitute for content authorization. Each device must handle content availability and subscription/access requirements according to the product’s legal and technical route.

## Privacy and separate shared/private content

Design shared content as an explicit projection:

    private local record
        -> user chooses activity content
        -> shared activity payload
        -> participant-local projection

Do not send the entire local database, private notes, account token, or model context to GroupSessionMessenger. Keep shared and unshared windows/content visibly distinct. If a participant leaves, clear or retain local copies according to the product’s user-facing privacy policy.

Apple states that the Group Activities framework does not provide Apple visibility into the content the app shares or media playback details. That does not remove the app’s responsibility for participant consent, data minimization, account authorization, content licensing, logs, and local storage.

## On-device AI and collaboration

AI can support a shared activity when its authority is scoped:

- suggest a board-game move for local review;
- summarize shared notes only after the group agrees to the scope;
- classify a shared attachment;
- draft a group decision or action list;
- translate a user-approved message;
- propose a conflict resolution rule.

Keep private and shared model context separate:

    private prompt/context
        -> explicitly selected shared input
        -> model proposal
        -> participant-visible review
        -> deterministic validation
        -> shared message or approved record

Do not broadcast hidden prompts, local contact data, account tokens, or private model context. Do not let an AI output directly mutate a shared domain state without a typed message, participant/role policy, idempotence, and the review path appropriate to the consequence.

## Liquid Glass and collaborative design

The shared state should be legible before it is beautiful:

- show whether the experience is solo, inviting, waiting, joined, or invalidated;
- display participant presence without exposing unnecessary identity;
- make shared versus private content visually distinct;
- show who changed a shared state when that helps resolve confusion;
- keep SharePlay terminology and the system SharePlay symbol;
- use a standard share sheet or ShareLink where the route calls for it;
- use Liquid Glass for app-owned toolbars, participant controls, and transient actions;
- keep the canonical shared content on a stable layer;
- ensure reduced transparency/motion preserves presence and sync state.

Do not place important participant status only in a floating glass overlay that disappears during a scroll or system handoff. Do not fake the SharePlay system banner or Messages/FaceTime surface.

See [SharePlay HIG](https://developer.apple.com/design/human-interface-guidelines/shareplay), [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing), and [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass).

## Evidence boundary

| Evidence | Supports | Does not support |
| --- | --- | --- |
| Activity fixture | Local activity metadata, state, and message rendering | FaceTime/Messages activation, participant join, multi-device delivery |
| Simulator | App-owned layout and deterministic protocol tests | Real SharePlay session, late join, participant identity, system share surface |
| Signed device | Selected session/join/leave path on the device | Universal platform support, stable network delivery, content entitlement |
| Two-device FaceTime/Messages | Actual activity invitation, session, participants, and messaging | Server durability, all device/OS combinations |
| Journal/attachment run | Selected file/data transfer and late-join behavior | Durable storage, revocation, moderation, universal reliability |
| Production collaboration | Observed activity and server/persistence behavior | Universal delivery, future system policy, every conflict pattern |

## Sources

- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [GroupActivity](https://developer.apple.com/documentation/groupactivities/groupactivity)
- [GroupActivityMetadata](https://developer.apple.com/documentation/groupactivities/groupactivitymetadata)
- [GroupStateObserver](https://developer.apple.com/documentation/groupactivities/groupstateobserver)
- [isEligibleForGroupSession](https://developer.apple.com/documentation/groupactivities/groupstateobserver/iseligibleforgroupsession)
- [Presenting SharePlay activities from your app’s UI](https://developer.apple.com/documentation/groupactivities/promoting-shareplay-activities-from-your-apps-ui)
- [Defining your app’s SharePlay activities](https://developer.apple.com/documentation/groupactivities/defining-your-apps-shareplay-activities)
- [prepareForActivation](https://developer.apple.com/documentation/GroupActivities/GroupActivity/prepareForActivation%28%29)
- [activate](https://developer.apple.com/documentation/groupactivities/groupactivity/activate%28%29)
- [GroupSession](https://developer.apple.com/documentation/groupactivities/groupsession)
- [GroupSession.State](https://developer.apple.com/documentation/groupactivities/groupsession/state-swift.enum)
- [GroupSession.Sessions](https://developer.apple.com/documentation/groupactivities/groupsession/sessions)
- [Joining and managing a shared activity](https://developer.apple.com/documentation/groupactivities/joining-and-managing-a-shared-activity)
- [GroupSessionMessenger](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionMessenger delivery modes](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger/deliverymode-swift.enum/reliable)
- [GroupSessionJournal](https://developer.apple.com/documentation/groupactivities/groupsessionjournal)
- [Synchronizing data during a SharePlay activity](https://developer.apple.com/documentation/groupactivities/synchronizing-data-during-a-shareplay-activity)
- [SharePlay HIG](https://developer.apple.com/design/human-interface-guidelines/shareplay)
- [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
