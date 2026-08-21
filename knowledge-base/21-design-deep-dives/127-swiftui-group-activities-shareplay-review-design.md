# SwiftUI Group Activities and SharePlay collaborative-native review design

This design companion turns a SharePlay-capable feature into a native SwiftUI task. SwiftUI owns the local shell, state language, accessibility, review, and explicit actions. Group Activities owns the system activation/session lane. The app owns the shared-data schema, reconciliation rule, privacy scope, and durable side effects.

Pair this page with the [SwiftUI Group Activities and SharePlay collaborative-native review](../42-framework-deep-dives/99-swiftui-group-activities-shareplay-review.md), the existing [SharePlay system route](../44-system-services/05-group-activities-shareplay.md), [collaborative native surfaces](29-shareplay-and-collaborative-native-surfaces.md), the [review route](../50-capability-recipes/130-swiftui-group-activities-shareplay-review-route.md), and the [multi-device proof matrix](../60-verification/124-swiftui-group-activities-shareplay-review-proof-matrix.md).

## Design contract

A person should be able to answer these questions without knowing Group Activities:

1. What am I sharing?
2. Who can see or change it?
3. Am I still working locally, inviting, waiting, joined, catching up, or viewing a copy?
4. Which changes are shared, which are private, and which are saved durably?
5. What happens if another participant changes the same thing?
6. Can I leave without losing my local work?
7. If an on-device AI suggests something, who reviews it and what exactly will be applied?

The hierarchy is:

~~~text
task and content context
  -> private/shared scope
  -> SharePlay action or local route
  -> system invitation handoff
  -> participant/session status
  -> shared content and revisions
  -> review/conflict/AI proposal
  -> explicit apply/save/leave
~~~

Do not make a translucent participant pill the primary product. The shared task and its current truth should remain legible without the glass or the system banner.

## Native screen anatomy

| Region | Responsibility | Design rule |
| --- | --- | --- |
| Navigation shell | Title, close, document/game identity | Keep it stable across system handoff and participant changes. |
| Scope label | Private, preparing, shared, local copy | Make the sharing boundary explicit in text and accessibility. |
| Primary content | Board, editor, player, canvas, or task | Keep shared content on a stable layer. |
| SharePlay action | Start, invite, join, or continue locally | Use a concrete label and system SharePlay symbol. |
| Participant status | Count and approved display names | Show only what the product needs; do not imply authentication. |
| Revision/status strip | Current, catching up, conflict, offline, ended | Use semantic copy rather than color alone. |
| Tool group | Shared controls, review, undo, leave | Use a small functional group; avoid glass on every item. |
| Review surface | Proposed/shared change and source | Separate proposal, received event, and committed domain state. |
| Fallback | Solo mode, local copy, retry, export | Preserve the task when a session is unavailable. |

On iPhone, a compact bottom accessory or toolbar can hold SharePlay/status tools. On iPad or Mac, use a side inspector or split view for participant/revision detail. On visionOS, use a target-specific spatial layout and do not call an iOS window composition proof of a shared Full Space.

## State language

| State | Primary copy | Useful action |
| --- | --- | --- |
| Solo | “Working only on this device.” | SharePlay, ShareLink, or Continue. |
| Preparing | “Preparing this board for sharing.” | Review scope, cancel. |
| Eligible | “Ready to start SharePlay.” | Start SharePlay. |
| Not eligible | “SharePlay isn’t active here yet.” | Use share sheet or continue locally. |
| Inviting | “Waiting for people to join.” | Cancel invitation, continue locally if valid. |
| Waiting | “Connecting to the shared activity.” | Keep content context, cancel. |
| Joined | “Shared with 2 people.” | Leave, participant details. |
| Catching up | “Loading the latest shared state.” | Wait, retry, view local copy. |
| Shared update | “Jordan changed the selected item.” | Review, undo if allowed. |
| Conflict | “This changed on another device.” | Compare, keep mine, accept theirs, merge. |
| Attachment loading | “Loading the shared image.” | Cancel, retry, view unavailable state. |
| Activity ended | “SharePlay ended; your local work is still here.” | Save, retry, continue locally. |
| AI proposal | “Suggested change for the shared board.” | Review, edit, reject, apply. |

Avoid “synced” when the app has only sent a message. Prefer “Sent,” “Received,” “Applied,” or “Saved” according to the actual evidence.

## Functional Liquid Glass composition

Use Liquid Glass for app-owned functional controls:

- SharePlay/start/invite;
- participant/status group;
- compare/review tools;
- undo/redo and leave;
- compact conflict resolution actions;
- local AI suggestion controls.

Keep the canonical shared content in the content layer:

~~~text
document/game/canvas/player + revision + content state
  = shared content layer

navigation + scope + participant/status + review + actions
  = functional layer
~~~

Good compositions:

- a single top scope/status group;
- a toolbar SharePlay action adjacent to the ordinary share action;
- one participant/revision inspector;
- a review sheet for a remote or AI-proposed change;
- a compact leave/continue-local control with explicit copy.

Poor compositions:

- a fake system SharePlay banner;
- participant names hidden behind a transient glow;
- a glass surface over every collaborator cursor;
- a glass veil that makes private and shared content look identical;
- icon-only conflict resolution;
- animated morphing when a person is comparing two revisions.

Test bright and dark content, reduced transparency, increased contrast, large text, and a long localized activity title. If glass is unavailable or unreadable, keep the hierarchy with a system material or opaque surface.

## Private versus shared content

Use a visible data boundary:

| Content | Default treatment |
| --- | --- |
| Local draft not selected for sharing | Private; do not broadcast. |
| Activity metadata | Shared through the system invitation; keep concise. |
| Selected document/game/canvas state | Shared only after the person starts or joins. |
| Account/entitlement state | Local; validate independently on each device. |
| AI prompt/context | Private unless the person explicitly selects shared input. |
| Participant display | Minimized and policy-approved. |
| Durable record | Explicit save/commit with its own authority. |
| Temporary attachment | Shared only with size, type, retention, and deletion policy. |

Use words such as “Private,” “Shared,” “Local copy,” and “Saved” rather than relying on a different background tint. A shared window and a private window should remain distinguishable after a system handoff or when the person returns from another app.

## Participant presence and identity

Presence should answer “who is here?” without claiming “who is authorized to own this record.” Show:

- a participant count;
- approved display names or initials;
- joined/waiting/left state;
- a source label for a recent change when helpful;
- a route to inspect or hide participant detail;
- private/shared scope in VoiceOver labels.

Do not expose raw participant IDs or treat a display name as a verified account. If the product has roles, show the role only after the app has separately validated it.

For accessibility, announce meaningful changes:

- someone joined;
- the activity became shared;
- a participant changed the selected record;
- the shared revision requires review;
- the activity ended.

Do not announce every cursor movement or transient unreliable message.

## Shared content, revisions, and conflicts

Make revision state visible:

| Revision state | Visual treatment | Action |
| --- | --- | --- |
| Current | Quiet status | Continue. |
| Sending | Pending status | Cancel only if safe. |
| Received | Source participant and revision | Review/apply according to policy. |
| Applied locally | Updated content and source | Undo if supported. |
| Conflict | Side-by-side or focused comparison | Select/merge/keep. |
| Stale | “This suggestion is based on an older revision.” | Re-run or discard. |
| Durable save pending | Explicit save state | Save/retry/continue local. |

Do not turn a conflict into a sudden full-screen error when a focused review sheet can explain it. For a destructive or external side effect, require a stronger confirmation than for a reversible visual change.

## Shared media design

For coordinated playback:

- show the shared intent separately from local buffering;
- state when the person is catching up;
- preserve a local pause/interrupt/Picture in Picture path where the product allows it;
- keep subscription/content access steps before the shared player;
- use a concrete Leave SharePlay action;
- avoid a progress animation that implies all devices are at exactly the same frame.

For a shared photo, canvas, or attachment:

- show loading and unavailable states;
- state who added it only when useful;
- expose source/revision and whether it is local or shared;
- allow rejection or deletion according to the role policy;
- avoid silently replacing a private original with a shared rendition.

## AI proposal design

An AI surface should look like an editable suggestion:

~~~text
explicit shared selection
  -> source revision and participant scope
  -> local model availability
  -> proposal
  -> participant review
  -> typed message or durable commit
~~~

Good copy:

- “Suggested grouping for the shared notes.”
- “Based on the board revision you selected.”
- “Review before sending this change to everyone.”
- “The on-device model is unavailable; manual controls remain available.”

Bad copy:

- “AI has decided for the group.”
- “Everyone agrees.”
- “Synced and verified” after one message send.
- “The model knows the correct answer.”

Give people edit, reject, and undo controls. Mark a proposal stale when the shared revision or selected participant scope changes.

## Alternate input and adaptive layout

The shared task must work with:

- VoiceOver;
- Dynamic Type;
- keyboard/full keyboard access;
- pointer and hover where supported;
- Voice Control;
- Switch Control;
- reduced motion;
- increased contrast and reduced transparency;
- iPhone compact width and iPad/Mac expanded layouts;
- localization with long activity metadata.

Provide a list, inspector, or command route for actions that are otherwise represented by a cursor, canvas gesture, or collaborator avatar. A live cursor is not an accessible command surface.

## Design checklist

- [ ] The person knows what is shared before activation.
- [ ] Solo, inviting, waiting, joined, catching-up, conflict, and invalidated states are explicit.
- [ ] The system owns invitation/share-sheet UI.
- [ ] Activity metadata is concise and privacy-safe.
- [ ] Participant presence is useful without pretending to be authentication.
- [ ] Messenger, Journal, durable persistence, and media coordination have separate visual semantics.
- [ ] Shared and private content remain visibly and audibly distinct.
- [ ] Conflicts expose a concrete rule and a review action.
- [ ] Liquid Glass groups functional controls without covering canonical content.
- [ ] AI receives explicitly selected shared input and remains reviewable.
- [ ] VoiceOver, Dynamic Type, reduced effects, alternate input, and long text are tested.
- [ ] Leave, cancel, retry, and local fallback preserve user work.

## Sources

- [SharePlay](https://developer.apple.com/design/human-interface-guidelines/shareplay)
- [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [Defining your app’s SharePlay activities](https://developer.apple.com/documentation/groupactivities/defining-your-apps-shareplay-activities)
- [Presenting SharePlay activities from your app’s UI](https://developer.apple.com/documentation/groupactivities/promoting-shareplay-activities-from-your-apps-ui)
- [Joining and managing a shared activity](https://developer.apple.com/documentation/groupactivities/joining-and-managing-a-shared-activity)
- [Synchronizing data during a SharePlay activity](https://developer.apple.com/documentation/groupactivities/synchronizing-data-during-a-shareplay-activity)
- [GroupSession](https://developer.apple.com/documentation/groupactivities/groupsession)
- [GroupSessionMessenger](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionJournal](https://developer.apple.com/documentation/groupactivities/groupsessionjournal)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

## Related routes

- [SwiftUI Group Activities and SharePlay collaborative-native review](../42-framework-deep-dives/99-swiftui-group-activities-shareplay-review.md)
- [Group Activities and SharePlay system routes](../44-system-services/05-group-activities-shareplay.md)
- [Group Activities and SharePlay route](../50-capability-recipes/32-group-activities-shareplay-route.md)
- [SwiftUI Group Activities and SharePlay review route](../50-capability-recipes/130-swiftui-group-activities-shareplay-review-route.md)
- [SwiftUI Group Activities and SharePlay proof matrix](../60-verification/124-swiftui-group-activities-shareplay-review-proof-matrix.md)
- [SwiftUI Group Activities and SharePlay recipes](../70-code-recipes/142-swiftui-group-activities-shareplay-review-recipes.md)
