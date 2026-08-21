# SharePlay and collaborative native surfaces

SharePlay design is about helping people feel together while keeping their private data, local progress, and group state understandable. The activity should feel like a natural extension of FaceTime, Messages, or a nearby shared context—not like a hidden networking mode bolted onto an ordinary screen.

Use a two-layer composition:

    private/local app content
        -> explicit shared selection
        -> system SharePlay invitation/session
        -> shared activity content
        -> participant-aware state
        -> solo/leave/invalidation fallback

## Name the shared action

Make the shared action discoverable without pretending it is always available:

- use the SharePlay name and symbol according to the HIG;
- place a Start SharePlay or SharePlay action near the content it shares;
- explain whether the person is sharing a movie, canvas, game, class, plan, or document;
- show when the current context can create a session;
- offer the system share sheet when no FaceTime/Messages context is active;
- let people continue locally when the activity is not group-only.

Use GroupStateObserver to adapt the app’s UI to session eligibility. Do not remove every share action when the person is not currently on a FaceTime call; the system can provide a sharing controller or share-sheet route that invites people.

Apple’s [SharePlay HIG](https://developer.apple.com/design/human-interface-guidelines/shareplay) recommends concise activity descriptions, correct SharePlay terminology, a visible shared state, preparation before joining, and support for late participants.

## Shared versus private

Make the boundary visible:

| State | Visual treatment | User question answered |
| --- | --- | --- |
| Private | Ordinary app content | What is only mine? |
| Preparing | Review surface or system invitation | What am I about to share? |
| Waiting | Shared-state indicator plus progress | Who has joined and what is pending? |
| Joined | Participant context and shared controls | What is synchronized? |
| Local divergence | Explicit stale/offline/error state | What is only on my device? |
| Invalidated | Return to local content | What remains after the activity ends? |

In a multi-window or spatial app, make it obvious which window or content is shared. Do not let a private note, account page, or model prompt accidentally ride along with the shared activity.

## Activity metadata is part of the UI

GroupActivityMetadata appears in system UI. Treat it like a launch surface:

- use a concise title;
- describe the actual experience, not the app’s marketing slogan;
- include an image only when it improves recognition;
- avoid revealing private document titles or contact data;
- add a fallback URL only when it leads to an honest join/install path;
- keep the activity identifier stable once released.

An unclear metadata string causes confusion before the app’s own view appears. A polished Liquid Glass screen cannot recover from a misleading system invitation.

## Participant presence and late join

Show enough presence to help the group coordinate:

- who is invited;
- who has joined;
- who is still preparing;
- who left;
- who made a relevant change, when attribution helps.

Avoid turning participant presence into a social feed. Use the minimum identity information needed for the activity. If the group has roles, label them clearly and show which content each role can see.

When someone joins late, offer a baseline or current snapshot. Do not replay an unbounded event history into the UI. The shared activity should converge to a state the new participant can understand.

## Controls and conflict

Choose a clear authority rule for each shared action:

| Shared action | Possible rule | UI implication |
| --- | --- | --- |
| Play/pause | Everyone can request; latest accepted revision wins | Show who changed playback when useful |
| Seek/scrub | Host or last change wins | Show the new position and avoid competing animations |
| Whiteboard stroke | All participants append | Attribute strokes and handle out-of-order arrival |
| Shared document edit | Server/CRDT/domain merge | Show conflict or revision state |
| Quiz answer | Role-restricted or first accepted | Show locked/accepted state |
| Physical-world action | Explicit owner plus confirmation | Never let a shared message silently actuate hardware |

The UI should expose the rule when conflict is plausible. “Last change wins” can be fine; invisible races create distrust.

## Liquid Glass composition

Use Liquid Glass for functional groups that float around shared content:

- a participant strip or compact session control;
- a toolbar for shared tools;
- a transient “Shared”/“Private” state control;
- a compact review/action cluster;
- a system-adjacent SharePlay entry point that remains an app-owned control.

Keep shared content, current cursor/tool, media time, and participant-visible status on a stable surface. Glass should not be the only indication of whether a change propagated.

Use native semantic controls, current SwiftUI material APIs, and current HIG hierarchy. Test:

- reduced transparency;
- increased contrast;
- reduced motion;
- large Dynamic Type;
- keyboard/pointer/controller input;
- VoiceOver participant and state announcements;
- split-screen/regular-width/compact-width layouts;
- background/foreground and session invalidation.

Do not redraw FaceTime/Message banners, fake a system SharePlay icon, or make every collaborator action a translucent capsule.

## Shared media and time

For synchronized playback:

- show local buffering separately from shared playback intent;
- indicate when the person is catching up;
- avoid a local progress animation that hides drift;
- support Picture in Picture where appropriate;
- keep a clear action for leaving SharePlay while remaining in the call;
- preserve content entitlement and account state per device.

If a person changes apps but remains in the FaceTime call, the app should preserve a sensible shared state. The HIG specifically calls out continuing a shared activity while people navigate away from the activity.

## Accessibility and social clarity

Collaborative surfaces need announcements that do not overwhelm:

- announce session join/leave only when relevant;
- identify who changed a shared value when it helps;
- expose private/shared status in labels and values;
- provide a direct route to leave;
- let a person review a shared artifact before it becomes local truth;
- ensure shared controls remain usable with VoiceOver and alternate input;
- distinguish network/offline/local-only state through text and accessibility values;
- keep participant identity privacy-safe on locked/shared surfaces.

Do not assume everyone can see the same animation, spatial Persona, cursor, or color. Provide text/state alternatives.

## AI in a shared activity

Design AI as a participant-visible proposal:

    shared selected input
        -> model proposal
        -> provenance/ambiguity
        -> participant review
        -> typed message or domain action
        -> convergence

Examples:

- summarize only the notes the group selected;
- suggest a whiteboard structure;
- draft a group itinerary;
- translate a message before sending;
- propose a conflict resolution that each role can inspect.

Private AI context stays private unless the person explicitly shares it. A model-generated message should not mutate shared state without schema validation, participant permissions, idempotence, and a visible result. Avoid hidden prompts that contain other participants’ contact, account, or conversation data.

## SharePlay-native copy

Prefer clear copy:

- “SharePlay this board”
- “Start Activity”
- “Continue Only for Me”
- “Waiting for people to join”
- “Shared with 2 people”
- “You’re viewing a local copy”
- “Activity ended; your changes are still on this device”

Use SharePlay as the noun or verb according to the HIG. Avoid invented variants or language that suggests the system guarantees every participant sees an action instantly.

## Design checklist

- [ ] The app explains what content becomes shared before activation.
- [ ] SharePlay entry points remain discoverable when no session is currently eligible.
- [ ] Activity metadata is concise, meaningful, and privacy-safe.
- [ ] Private, preparing, waiting, joined, local, and invalidated states are visible.
- [ ] Participant presence and late join behavior are intentional.
- [ ] Each shared mutation has an authority/conflict rule.
- [ ] Messenger versus journal versus server responsibilities are separate.
- [ ] Shared media shows local buffering and shared intent independently.
- [ ] Liquid Glass groups functional app-owned controls without imitating system surfaces.
- [ ] VoiceOver, Dynamic Type, reduced effects, alternate input, and locked/shared privacy states are tested.
- [ ] AI receives explicitly selected shared input and produces reviewable output.

## Sources

- [SharePlay HIG](https://developer.apple.com/design/human-interface-guidelines/shareplay)
- [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [GroupActivity](https://developer.apple.com/documentation/groupactivities/groupactivity)
- [GroupActivityMetadata](https://developer.apple.com/documentation/groupactivities/groupactivitymetadata)
- [GroupStateObserver](https://developer.apple.com/documentation/groupactivities/groupstateobserver)
- [Presenting SharePlay activities from your app’s UI](https://developer.apple.com/documentation/groupactivities/promoting-shareplay-activities-from-your-apps-ui)
- [Defining your app’s SharePlay activities](https://developer.apple.com/documentation/groupactivities/defining-your-apps-shareplay-activities)
- [Joining and managing a shared activity](https://developer.apple.com/documentation/groupactivities/joining-and-managing-a-shared-activity)
- [Synchronizing data during a SharePlay activity](https://developer.apple.com/documentation/groupactivities/synchronizing-data-during-a-shareplay-activity)
- [GroupSession](https://developer.apple.com/documentation/groupactivities/groupsession)
- [GroupSessionMessenger](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionJournal](https://developer.apple.com/documentation/groupactivities/groupsessionjournal)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
