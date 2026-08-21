# SwiftUI Watch Connectivity and watchOS companion review design

This guide turns the paired iPhone and Apple Watch route into a native design system for a watchOS app, WidgetKit complications, Smart Stack, App Intent actions, and a larger iPhone companion. It extends the existing Watch Connectivity material with explicit freshness, transport, privacy, AI, Liquid Glass, accessibility, and physical-device states.

Read the [companion review](../42-framework-deep-dives/107-swiftui-watch-connectivity-watchos-companion-review.md), [route](../50-capability-recipes/138-swiftui-watch-connectivity-watchos-companion-review-route.md), [proof matrix](../60-verification/132-swiftui-watch-connectivity-watchos-companion-review-proof-matrix.md), and [recipes](../70-code-recipes/150-swiftui-watch-connectivity-watchos-companion-review-recipes.md) together.

## Design thesis

The watch is not a smaller iPhone. It is a close, glanceable surface for short, useful interactions. A complication, Smart Stack widget, notification, watch app, and iPhone app can share a user outcome while retaining separate attention budgets and lifecycles.

Use this sequence:

1. Glance at one timely fact or one next action.
2. Confirm source, freshness, and consequence.
3. Perform one short action.
4. Reconcile as pending, accepted, rejected, or needs iPhone.
5. Expand to the iPhone only when the task genuinely needs its larger surface.

The watch should not be a loading screen for the iPhone. It needs a valuable local fallback, a truthful pending state, and a recovery path when reachability changes.

## Visual state layers

Keep these layers distinct in both code and visual language:

| Layer | Visual responsibility | Example |
| --- | --- | --- |
| Domain truth | What the app committed | Completed item at revision 42 |
| Local projection | What this device can safely show | Last-known item title and age |
| Transport state | What the companion link is doing | Activating, reachable, queued |
| System projection | What WidgetKit may render | Timeline entry or relevance hint |
| AI proposal | What a model suggested | Candidate priority from revision 42 |
| User decision | What the person approved | Confirmed priority |
| Release state | What the installed artifact supports | Signed paired iPhone and watch |

Do not use the same green checkmark for a transfer callback and a committed domain mutation. Sent means handed to a transfer API. Received means a counterpart callback ran. Applied means the local state owner accepted it. Committed means the domain or server accepted the mutation.

## Surface map

| Surface | Primary job | Design shape | Avoid |
| --- | --- | --- | --- |
| iPhone companion | Configure and reconcile | Larger list/detail hierarchy with source and revision | Hiding watch state in one connection badge |
| Watch app glance | Show one current value | Focused vertical hierarchy | Dense dashboard cards |
| Watch app action | Perform one command | One value, one primary action, clear result | Many destructive choices |
| Watch complication | Provide a glance | Family-specific value, symbol, or gauge | Tiny paragraphs |
| Smart Stack | Be relevant at the right moment | Contextual value, age, safe background | Assuming appearance or timing |
| Widget/App Intent | Complete a small command | Native control with result state | Starting a long workflow |
| Notification | Alert about a consequential event | Concise and privacy-safe | Becoming a continuous feed |
| iPhone handoff | Continue a larger task | Preserved record and revision | Dropping at an unrelated home screen |
| AI review | Show a candidate | Source, candidate, constraints, decision | Treating generated text as fact |

## Companion state language

| Internal state | User-facing label | Detail |
| --- | --- | --- |
| Unsupported | Watch features unavailable | Target or device support is missing |
| Unpaired | Pair a watch to continue | No paired watch is available |
| Not installed | Install the watch app | The paired watch lacks the target |
| Activating | Preparing watch connection | Session activation is incomplete |
| Reachable | Ready for a quick exchange | Immediate messaging may work |
| Offline | Watch will catch up later | Use local queue or snapshot |
| Snapshot received | Updated from iPhone | Show revision and time |
| Event pending | Waiting to sync | Do not claim completion |
| Applied locally | Saved on this device | Local state accepted the payload |
| Needs iPhone | Continue on iPhone | The watch cannot finish this task |
| Stale | Last updated at time | Show a recovery action |
| Rejected | Could not apply update | Show a safe reason |
| AI unavailable | Using a simple fallback | Do not imply a model ran |
| AI candidate | Suggested, needs review | Show source revision |

Make transport state secondary to the content. The user came to see or do something, not to inspect session activation.

## Native watchOS composition

### Watch app

Prefer a short vertical composition:

- a small context label;
- one primary value;
- a source or freshness line;
- one primary action;
- an optional secondary action;
- a compact pending or error explanation;
- a clear return path.

Use the Digital Crown for scrolling, selecting, or controlled review when a standard SwiftUI control communicates the action. Keep the first screen useful without scrolling when possible. Put the most important value first when scrolling is necessary.

### iPhone companion

The iPhone can expose the larger reconciliation route:

- paired watch identity;
- app-installed state;
- activation result;
- last sent and received revisions;
- queued event count;
- file-transfer status;
- account scope;
- conflicts and recovery;
- redaction settings;
- AI proposal history;
- retry or refresh actions.

Keep advanced diagnostics behind a deliberate connection-details route. Do not make a user debug transport to complete a normal task.

## WidgetKit and complication composition

Design each family from its constraints:

| Family or context | Design intent |
| --- | --- |
| Circular | One value, symbol, or short gauge |
| Corner | Compact metric with a strong anchor |
| Inline | Sentence fragment or concise value |
| Rectangular | One value plus context or progress |
| Smart Stack | Contextual glance with freshness |
| Full color | Color can reinforce meaning |
| Accented or tinted | Hierarchy survives system tint |
| Locked or Always On | Content is redacted and quiet |

A complication may launch the app, but its stronger purpose is relevant glanceable information. Support every family for which the product has meaningful content. If a family cannot carry the detail, show a useful value, icon, or safe launch affordance.

Smart Stack relevance is a system hint, not a guarantee of placement or timing. Design for the widget being pinned, briefly visible, delayed, redacted, stale, or never tapped. Use a notification or another documented route when the user truly needs an explicit signal.

## Liquid Glass rules

Liquid Glass should organize interaction and preserve depth. It is not a reason to place a translucent card behind every value.

- Prefer standard SwiftUI controls and platform styles first.
- Keep glass groups small and semantically related.
- Do not stack materials without a clear hierarchy.
- Keep contrast valid in light, dark, tinted, accented, and reduced-transparency modes.
- Keep the primary value usable when the effect is unavailable.
- Test Reduce Motion and Reduce Transparency.
- Avoid private-system replicas and undocumented blur behavior.
- Never delay comprehension for an animated material transition.
- Keep WidgetKit system rendering separate from a custom watch app shell.

A restrained glass group can contain a watch action and its status. The content should remain readable if the material changes or a widget renders without a background.

## Interaction patterns

### Glance to action

Use the sequence current value, primary action, result state.

Example:

- The complication shows three pending items.
- The watch app opens the top item.
- The person taps Mark done.
- The watch shows Waiting to sync or Saved on watch.
- The iPhone or server later reconciles the revision.

### Quick action with phone fallback

When a command can finish on the watch, perform it locally and queue the event. When it needs account authority or a large form:

- explain why iPhone is needed;
- preserve record identity and expected revision;
- open the corresponding iPhone route;
- keep the watch action pending;
- reconcile when the result returns.

A Continue on iPhone action must not erase the watch’s pending state.

### Conflict

Show conflicts as data:

- This changed on iPhone.
- Review the newer version.
- Keep watch version.
- Use iPhone version.
- Save as a new entry.

Only present choices the domain allows. AI can explain a difference, but it must not silently choose the winner.

## App Intent design

Use App Intents as typed system actions:

| Action | Watch-friendly? | Guard |
| --- | --- | --- |
| Mark one item complete | Usually | Idempotent and revision-aware |
| Toggle a simple preference | Usually | Preserve authorization and current value |
| Start a long export | Usually not | Hand off and report pending |
| Change an entitlement | No direct assumption | Use authorized full-app or server route |
| Generate a plan | Only as a proposal | Return a reviewable candidate |
| Open one record | Yes | Resolve a stable identifier |
| Search an unbounded catalog | Usually not | Use focused query or iPhone handoff |

An action must show what it will do, resolve the target safely, validate expected revision, perform an idempotent command, and return a user-readable result. Sensitive actions need confirmation or a pending/reconciliation state.

## On-device AI review

Use local AI for bounded suggestions:

- choose which user-owned item to show next;
- summarize a local note into a short label;
- propose a queue priority;
- draft a compact notification or complication phrase.

Use this sequence:

accepted source -> deterministic context -> availability check -> constrained generation -> schema decode -> allowlist and length validation -> revision check -> user review or policy -> commit -> companion transfer

Do not assume a watchOS target has the same model availability as iPhone. Check SDK, deployment, device readiness, locale, region, energy, memory, and SystemLanguageModel availability. When unavailable, use source text, deterministic sorting, a manual selection, or a needs-iPhone state.

Never put an unreviewed candidate in a complication. Show source revision, candidate, constraints, approve/edit/reject, commit result, and transfer state. The model is not the transport, identity provider, entitlement authority, or source of truth.

## Accessibility and alternate input

- Use concise accessibility labels and meaningful VoiceOver order.
- Support larger text without clipping.
- Make the primary action discoverable without color.
- Keep Digital Crown scrolling and selection usable.
- Test Reduce Motion and non-animated success.
- Provide haptic or textual confirmation when visual motion is reduced.
- Make the essential complication value the first spoken element.
- Give gauges and progress a useful accessibility value.
- Announce stale and redacted states.
- Test every supported family rather than one rectangular preview.
- On iPhone, expose pairing, pending, conflict, and redaction states to assistive technology.
- Preserve a clear navigation title after a watch handoff.

## Privacy and attention

The watch face, Smart Stack, notifications, and Always On display may be visible to other people. Define data policy before adding content:

| Content | Watch app | Complication | Smart Stack | Notification |
| --- | --- | --- | --- | --- |
| Generic count | Usually | Often | Often | Usually |
| Person name | Deliberate detail | Prefer redact | Prefer redact | Follow system privacy |
| Message text | Deliberate detail | Redact | Redact | Avoid sensitive preview |
| Health value | Authorized route | Policy-approved minimum | Policy-approved minimum | Avoid sensitive preview |
| Account balance | Authorized detail | Usually redact | Usually redact | Usually redact |
| AI candidate | Review only | Never unreviewed | Never unreviewed | Only approved bounded text |

When locked or Always On, use redacted values or a neutral state. On sign-out, account change, deletion, or unpairing, invalidate projections and pending transfers according to retention policy.

## Motion and feedback

Use motion to explain a single state change: pending to applied, accepted action haptic, freshness update, or predictable iPhone handoff.

Avoid loops in complications, animation that hides the new value, cosmetic work that consumes energy, or a transition that blocks the result. The system owns WidgetKit timing and Smart Stack placement.

## Screen blueprint: companion glance

**Purpose:** show the last committed value and one safe next action.

**Structure:**

1. Context label.
2. Primary value.
3. Source and freshness.
4. One primary button.
5. Pending or stale status.
6. Optional Open on iPhone action.

**States:**

- fresh committed;
- stale committed;
- pending local action;
- not reachable;
- account mismatch;
- redacted;
- model unavailable;
- needs iPhone;
- conflict.

**Evidence:**

- watchOS simulator layout;
- Dynamic Type and VoiceOver;
- Always On or redacted state;
- active and inactive session on paired hardware;
- no-reachability fallback;
- queued transfer result;
- installed complication or widget;
- App Intent action result;
- archived watch target.

## Screen blueprint: AI review

**Purpose:** approve a compact candidate from a named source revision.

**Structure:**

1. Source revision and time.
2. Candidate in a bounded native control.
3. Constraint or reason.
4. Approve, edit, regenerate, reject.
5. Commit state.
6. Transfer or handoff state.

**Guardrails:**

- no unreviewed candidate in a complication;
- deterministic fallback when unavailable;
- revalidate when the source revision changes;
- transfer generated content only when explicitly allowed;
- no health, safety, identity, or financial claims from a candidate.

## Design QA matrix

| Check | iPhone | Watch app | Complication | Smart Stack |
| --- | --- | --- | --- | --- |
| Freshness visible | Yes | Yes | If space permits | Yes |
| Redaction | Yes | Yes | Yes | Yes |
| Dynamic Type | Yes | Yes | Family-specific | Family-specific |
| VoiceOver | Yes | Yes | Yes | Yes |
| Reduce Motion | Yes | Yes | Static fallback | Static fallback |
| Reachability loss | Yes | Yes | Last-known state | Last-known state |
| Account switch | Purge/reconcile | Purge/reconcile | Redacted or empty | Redacted or empty |
| AI unavailable | Rules/manual | Rules/manual | Committed fallback | Committed fallback |
| Handoff | Preserve revision | Preserve revision | Stable route | Stable route |
| Physical proof | Signed iPhone | Paired watch | Installed complication | Actual Smart Stack |

## Sources

- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [WCSession](https://developer.apple.com/documentation/watchconnectivity/wcsession)
- [WCSessionDelegate](https://developer.apple.com/documentation/watchconnectivity/wcsessiondelegate)
- [Transferring data with Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity/transferring-data-with-watch-connectivity)
- [WatchKit](https://developer.apple.com/documentation/watchkit)
- [Life cycles](https://developer.apple.com/documentation/watchkit/life-cycles)
- [Background execution](https://developer.apple.com/documentation/watchkit/background-execution)
- [Using background tasks](https://developer.apple.com/documentation/watchkit/using-background-tasks)
- [watchOS apps](https://developer.apple.com/documentation/watchos-apps)
- [Setting up a watchOS project](https://developer.apple.com/documentation/watchos-apps/setting-up-a-watchos-project)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [Creating accessory widgets and watch complications](https://developer.apple.com/documentation/widgetkit/creating-accessory-widgets-and-watch-complications)
- [Developing a WidgetKit strategy](https://developer.apple.com/documentation/widgetkit/developing-a-widgetkit-strategy)
- [Widgets and watch complications](https://developer.apple.com/documentation/widgetkit/widgets-and-complications-collection)
- [Increasing the visibility of widgets in Smart Stacks](https://developer.apple.com/documentation/widgetkit/widget-suggestions-in-smart-stacks)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Widgets, Live Activities, and Controls](https://developer.apple.com/documentation/appintents/widgets-live-activities-and-controls)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos/)
- [Complications](https://developer.apple.com/design/human-interface-guidelines/complications)
- [Widgets](https://developer.apple.com/design/human-interface-guidelines/widgets)
