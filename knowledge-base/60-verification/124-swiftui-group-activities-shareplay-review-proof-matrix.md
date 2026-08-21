# SwiftUI Group Activities and SharePlay collaborative-native review proof matrix

This matrix separates documentation, compile, preview, simulator, signed-device, two-device system, collaboration, privacy, accessibility, and release evidence for a SwiftUI Group Activities route. It extends the existing [Group Activities and SharePlay proof matrix](26-group-activities-shareplay-proof-matrix.md) with explicit revision, shared/private, local AI, and SwiftUI review claims.

## Evidence levels

| Level | Evidence | Can support | Cannot support |
| --- | --- | --- | --- |
| L0 | Official source and target review | API meaning, capability, metadata, HIG, platform questions | Runtime activation, participant delivery, convergence, release |
| L1 | Named-target compile/tests | Imports, Codable/Transferable schemas, availability, reducers, entitlement presence | FaceTime/Messages system UI, participant identity, physical delivery |
| L2 | SwiftUI preview/fixture | State copy, private/shared hierarchy, review, fallback, accessibility structure | GroupSession, system share sheet, real multi-device behavior |
| L3 | Simulator or deterministic protocol fixture | Reducer, duplicate/out-of-order, late-join baseline, local lifecycle | Actual SharePlay invitation, participant transport, two-device convergence |
| L4 | Signed physical-device run | Target capability, system handoff, join/leave, selected session/message/journal path, accessibility/input | Every device/OS, durable server truth, universal delivery |
| L5 | Two-device FaceTime/Messages/AirDrop run | Actual activation, participant session, message/journal behavior, selected late join | All network/participant/content conditions, long-term durability |
| L6 | Archive/TestFlight/release run | Signing, entitlements, target metadata, privacy/release build | Universal collaboration or future system behavior |

Never call L0-L3 “SharePlay working.” Never call a message send “shared truth” without convergence and authority evidence.

## Core acceptance matrix

| Claim | Minimum proof | Capture | Fails if |
| --- | --- | --- | --- |
| The selected app target supports Group Activities | L1/L6 | Target capability, entitlement, provisioning, platform | A framework import is treated as entitlement proof. |
| Activity identity is stable | L1 | Activity identifier registry and migration policy | Identifiers change or collide between activity types. |
| Activity payload is safe | L1/L2 | Codable fixture, size, privacy, schema version | Private tokens, full database, or unbounded data is embedded. |
| Activity metadata is useful | L2/L4/L5 | Title, subtitle, type, image/fallback, truncation review | Metadata exposes private content or hides what will be shared. |
| ShareLink/share sheet route is correct | L2/L4/L5 | SwiftUI action, Transferable representation, system surface | A custom imitation is used or the activity cannot be shared. |
| Eligibility state is truthful | L2/L4 | GroupStateObserver transitions and fallback | False is treated as permanent unavailability. |
| prepareForActivation is handled | L1/L2/L4 | Local/group/cancel/error result and resulting UI | Local mode is called joined or cancellation is ignored. |
| Activation occurred | L4/L5 | System entry point, activity payload, result, device/OS | Button tap alone is called activation. |
| GroupSession is delivered | L4/L5 | sessions sequence, session ID, activity, waiting state | The app constructs a session or assumes delivery. |
| Join boundary is correct | L4/L5 | waiting -> join -> joined state | Shared mutations are claimed before joined. |
| Leave/invalidation cleanup works | L3/L4/L5 | leave/end/error/call-ended, listener cancellation | Invalidated session is reused or tasks keep mutating UI. |
| Participant projection is correct | L4/L5 | count, approved names, source reference, join/leave | Display name is treated as authenticated identity. |
| Small message schema is safe | L1/L3 | Codable version, event ID, revision, bounds, operation | Raw view state or private context is sent. |
| Reliable message route is understood | L3/L4/L5 | Known participant delivery, duplicate and delay behavior | Reliable is described as durable or late-join replay. |
| Unreliable route is appropriate | L3/L4 | Cursor/reaction/drop behavior | A critical mutation uses best-effort delivery. |
| Participant subset is correct | L3/L4/L5 | Role and recipient fixture | Private content reaches the wrong participant. |
| Source context is recorded | L3/L4 | MessageContext source and app-owned participant projection | Source is assumed to be business authorization. |
| Reducer is idempotent | L1/L3 | Duplicate/out-of-order/stale event fixtures | One event can commit twice or corrupt state. |
| Conflict rule converges | L3/L4/L5 | Simultaneous edit, revision, merge/last-writer/role rule | Each device silently keeps different shared truth. |
| Late join gets a baseline | L3/L4/L5 | Join after prior messages/attachment/current snapshot | New participant sees an incomplete state as current. |
| Journal attachment is bounded | L1/L4/L5 | Type, size, encryption/retention policy, load/cancel | Journal is described as unlimited or durable storage. |
| Journal item is validated | L3/L4 | Activity/session/revision/content validation | File is applied before checking provenance or size. |
| Coordinated media is honest | L4/L5 | Shared intent, local buffering, seek, late join | Local player timestamp is called group truth. |
| Durable shared record is separate | L1/L4/L5 | CloudKit/server/custom revision trace | SharePlay session is treated as the database. |
| AI proposal is bounded | L1/L2/L3/L4 | Typed input, model state, allowlist, source revision | Model chooses arbitrary message/side-effect identifiers. |
| AI proposal is reviewed | L2/L4/L5 | Participant-visible proposal, edit/reject/apply, stale cancel | AI output auto-commits to every device. |
| Shared/private boundary is usable | L2/L4/L5 | Copy, scope labels, locked/shared window behavior | Private notes or context are broadcast accidentally. |
| Liquid Glass is functional | L2/L4 | Bright/dark content, reduced transparency, contrast | Glass is the only presence or synchronization signal. |
| Accessibility task is complete | L2/L4/L5 | VoiceOver, Dynamic Type, reduced motion, keyboard/pointer/switch | Cursor or color is the only way to use the shared task. |
| Release target is valid | L6 | Archive, signing, entitlement, privacy, TestFlight | Local preview or simulator is called shipped. |

## Target and activity packet

Record before implementation:

| Field | Evidence |
| --- | --- |
| Target | App target, platform, bundle/build, deployment target, SDK. |
| Capability | Group Activities capability and entitlement. |
| Activity | Identifier, metadata, payload schema/version, Transferable route. |
| Content | Document/game/media ID and local access/entitlement policy. |
| Entry point | ShareLink, share sheet, FaceTime, Messages, AirDrop/nearby, or spatial route. |
| Fallback | Solo/local copy/cancel/retry behavior. |
| Persistence | Messenger, Journal, CloudKit/server/custom record responsibilities. |
| AI | Model availability, input scope, proposal schema, stale policy. |
| Privacy | Shared fields, participant display, local storage, logs, retention. |
| Release | Archive, provisioning, TestFlight, target matrix. |

## Activation and system-handoff packet

Test and capture:

1. local mode with no active conversation;
2. eligibility changing when a FaceTime/Messages context becomes active;
3. prepareForActivation local/group/cancel paths;
4. activate result/error;
5. ShareLink/share-sheet display;
6. recipient prompt and app launch;
7. activity payload resolution on the recipient;
8. session delivery and waiting state;
9. user cancel before join;
10. unsupported target/device fallback.

Evidence should name the system entry point and not rely on a screenshot of an app-owned button alone.

## Session and participant packet

Record:

- activity identifier and payload revision;
- session UUID;
- waiting/joined/invalidated timeline;
- join/leave/end action and reason;
- active participant count over time;
- approved participant display projection;
- local account/role authorization;
- listener task start/cancel;
- session replacement/generation;
- app background/foreground/termination behavior;
- call ended/network interruption result.

Acceptance rules:

1. The app never constructs GroupSession directly.
2. The app loads enough local content before joining.
3. Shared controls are disabled or labeled correctly while waiting/catching up.
4. Invalidated sessions release resources and are not reused.
5. Participant display does not become an account/authentication claim.

## Message and reconciliation packet

For each message type, record:

| Field | Required |
| --- | --- |
| Activity/session scope | Yes |
| Schema version | Yes |
| Event ID/idempotence key | Yes |
| Source participant reference | When source matters |
| Source revision/logical clock | Yes |
| Operation and bounded payload | Yes |
| Delivery mode | Yes |
| Recipient subset/role | When scoped |
| Expiry | For transient events |
| Duplicate/stale policy | Yes |
| Conflict rule | Yes |
| Durable commit authority | When persistence matters |

Run:

- duplicate delivery;
- out-of-order events;
- stale revision;
- missing/unknown operation;
- oversized payload;
- participant subset mismatch;
- leaving during send;
- session invalidation while receiving;
- reconnect/late join;
- simultaneous edit.

The result should show the reducer outcome, not just a callback log.

## Journal and late-join packet

For an attachment or baseline, capture:

- descriptor and activity/session scope;
- byte count and documented limit;
- type/UTType and version;
- source participant reference;
- temporary local path and deletion policy;
- cancellation and partial-file handling;
- validation result;
- late participant join timing;
- baseline revision;
- future message subscription after baseline;
- durable copy or server record, if any.

Do not describe journal end-to-end encryption as a replacement for app-side authorization, content validation, moderation, or retention policy.

## Multi-device run matrix

| Run | Setup | Expected evidence |
| --- | --- | --- |
| Solo | No call or declined activation | Local task remains complete and honest. |
| FaceTime initiator | Device A starts activity during FaceTime | System activity/share context and activation. |
| FaceTime recipient | Device B receives and joins | Session delivery, waiting/joined, participant projection. |
| Messages join | Recipient joins from a Messages activity | App launch, payload resolution, join. |
| AirDrop/nearby | Supported physical proximity path | System prompt and selected activity path. |
| Late join | Device B joins after several changes | Baseline then future messages, correct revision. |
| Conflict | Both devices edit same item | Documented rule and convergence. |
| Attachment | Add and receive image/document | Size/type validation, load, cancellation, retention. |
| Leave | One participant leaves | Local fallback and other-device state. |
| Call ended | End FaceTime or invalidate context | Session invalidation, cleanup, user copy. |
| Background | Background/foreground/lock as supported | State freshness and resource behavior. |
| Accessibility | VoiceOver/Dynamic Type/reduced effects | Shared task remains usable and understandable. |

Record device model, OS, build, network/context, account/content access, and the claim level for each run.

## AI, privacy, and Liquid Glass packet

Verify:

- only explicitly selected shared content enters a model request;
- proposal includes source/session/revision;
- unavailable/canceled/stale model states are visible;
- output maps to a typed allowlist;
- participant review precedes shared mutation;
- private prompts, tokens, and unrelated local records remain local;
- shared/private scope is announced by VoiceOver;
- glass fallback preserves status and action hierarchy;
- reduced motion/transparency does not remove necessary feedback.

## Release packet and claim language

Attach:

- archive and signed entitlement;
- target/platform/deployment/SDK matrix;
- activity identifier/metadata review;
- system entry-point screenshots/logs;
- two-device session and reconciliation traces;
- accessibility/privacy/retention review;
- AI proposal fixtures and stale/cancel tests;
- known unsupported platforms and fallbacks.

Use:

- “The tested devices joined the activity from a FaceTime call.”
- “The tested late participant received the current baseline and subsequent revision.”
- “The app continued locally when activation was declined.”
- “The model proposed a typed change that a participant reviewed.”

Avoid:

- “SharePlay guarantees sync.”
- “The participant is authenticated by their display name.”
- “A Messenger event is durable storage.”
- “The AI made the group agree.”

## Sources

- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [Configuring Group Activities](https://developer.apple.com/documentation/Xcode/configuring-group-activities)
- [GroupActivity](https://developer.apple.com/documentation/groupactivities/groupactivity)
- [GroupActivityMetadata](https://developer.apple.com/documentation/groupactivities/groupactivitymetadata)
- [Defining your app’s SharePlay activities](https://developer.apple.com/documentation/groupactivities/defining-your-apps-shareplay-activities)
- [Presenting SharePlay activities from your app’s UI](https://developer.apple.com/documentation/groupactivities/promoting-shareplay-activities-from-your-apps-ui)
- [GroupStateObserver](https://developer.apple.com/documentation/groupactivities/groupstateobserver)
- [GroupSession](https://developer.apple.com/documentation/groupactivities/groupsession)
- [GroupSession.State](https://developer.apple.com/documentation/groupactivities/groupsession/state-swift.enum)
- [GroupSession.State.invalidated(reason:)](https://developer.apple.com/documentation/groupactivities/groupsession/state-swift.enum/invalidated%28reason%3A%29)
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
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

## Related routes

- [SwiftUI Group Activities and SharePlay collaborative-native review](../42-framework-deep-dives/99-swiftui-group-activities-shareplay-review.md)
- [SwiftUI Group Activities and SharePlay collaborative-native design](../21-design-deep-dives/127-swiftui-group-activities-shareplay-review-design.md)
- [Group Activities and SharePlay proof matrix](26-group-activities-shareplay-proof-matrix.md)
- [SwiftUI Group Activities and SharePlay route](../50-capability-recipes/130-swiftui-group-activities-shareplay-review-route.md)
- [SwiftUI Group Activities and SharePlay recipes](../70-code-recipes/142-swiftui-group-activities-shareplay-review-recipes.md)
