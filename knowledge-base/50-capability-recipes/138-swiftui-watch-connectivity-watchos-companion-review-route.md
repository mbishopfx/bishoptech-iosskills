# SwiftUI Watch Connectivity and watchOS companion review route

This route card helps choose and sequence an iPhone plus watchOS companion build. It is not a raw API list. It asks which target owns the feature, which transfer semantics fit, what WidgetKit or App Intent surface is needed, and what evidence is required before calling the route reliable.

Read the [companion review](../42-framework-deep-dives/107-swiftui-watch-connectivity-watchos-companion-review.md), [design guide](../21-design-deep-dives/135-swiftui-watch-connectivity-watchos-companion-review-design.md), [proof matrix](../60-verification/132-swiftui-watch-connectivity-watchos-companion-review-proof-matrix.md), and [recipes](../70-code-recipes/150-swiftui-watch-connectivity-watchos-companion-review-recipes.md) before implementation.

## Route selector

Start with the user outcome:

| User outcome | First route | Add only when needed |
| --- | --- | --- |
| A current value at a glance | WidgetKit watch complication or Smart Stack | Watch app detail and server or iPhone reconciliation |
| A quick local action | watchOS app or App Intent | Watch Connectivity event queue and iPhone reconciliation |
| A live request while both apps are visible | WCSession immediate message | Application context or queued fallback |
| Latest state on the counterpart | updateApplicationContext | Local persistence, server sync, or conflict policy |
| Ordered small events | transferUserInfo | Durable cursor and idempotent domain command |
| Large image or document | transferFile | App-owned import pipeline and retention policy |
| Update an active complication | transferCurrentComplicationUserInfo | WidgetKit reload and stale projection |
| A larger form or account operation | Handoff or explicit iPhone route | Preserved record ID, revision, and pending state |
| Contextual Smart Stack appearance | WidgetKit relevance provider | App Intents, relevance clues, privacy-safe projection |
| A button or toggle outside the app | App Intent | Authorization, confirmation, and domain reconciliation |
| A local suggestion | Foundation Models when available | Allowlist, review, fallback, and source revision |
| Durable cross-device account truth | Server or CloudKit | Watch Connectivity as opportunistic transport |

## Step 1: define the truth owner

Write one sentence:

The authoritative owner of [record or action] is [watch local store, iPhone domain, CloudKit, or server], and the companion device may [read, queue, propose, or commit] through [named route].

Then answer:

- Can the watch create a record while offline?
- Can the iPhone change the same record?
- Is the operation idempotent?
- What identifies the installation and account scope?
- What revision or cursor orders changes?
- What should happen after unpairing, sign-out, reinstall, or a watch switch?
- What may appear on a locked watch face?
- Does a widget need a projection that is smaller than the app model?

If these answers are unknown, pause implementation at the domain and evidence boundary.

## Step 2: choose target topology

| Decision | Route |
| --- | --- |
| Watch-only product | Create a watch-only project and keep the workflow independent of iPhone reachability |
| New iPhone and watch product | Create a watch app with a new companion iOS app |
| Existing iPhone product | Add a watch app target and widget extension to the existing project |
| Independent watch app with related iPhone app | Use the documented independent watchOS configuration and define sync separately |
| Existing ClockKit complication | Migrate to WidgetKit for supported watchOS versions, retaining a deliberate legacy boundary only when required |

Verify the generated target graph, bundle identifiers, WKCompanionAppBundleIdentifier, watch app and extension prefixes, widget host, App Group, capabilities, and signing profile in an archive. A source file that compiles cannot prove target topology.

## Step 3: choose transfer semantics

| Question | Choose | Contract |
| --- | --- | --- |
| Must a reply arrive now while reachable? | sendMessage or sendMessageData | Live request/reply with explicit error fallback |
| Is only the latest snapshot useful? | updateApplicationContext | New context replaces older pipeline context |
| Must each small event be retained in order? | transferUserInfo | Queued background delivery with event IDs and cursor |
| Is the payload a file? | transferFile | Validate, move, decode, import, and expire |
| Is the payload specifically for an active complication? | transferCurrentComplicationUserInfo | Budgeted hint plus WidgetKit projection |
| Can the watch work without the counterpart? | Watch-local store | Queue events and reconcile later |
| Does the operation require authoritative account state? | iPhone/server/CloudKit | Watch can request or propose; commit in the owner |

Never use a reachability Boolean to decide whether the domain mutation happened.

## Step 4: model session state

Create a route state with separate fields for:

- support;
- pairing;
- active watch;
- companion installation;
- activation;
- reachability;
- last sent revision;
- last received revision;
- queued transfer count;
- last error;
- last successful domain reconciliation.

The iOS target must account for inactive and deactivated sessions when multiple watches can be selected. The watch target must recover from a purged process and a delayed background task.

## Step 5: define the envelope

Every transfer should include:

| Field | Why |
| --- | --- |
| schema | Decode and migration boundary |
| kind | Snapshot, event, file, complication, or result |
| source | iPhone, watch, server, or extension |
| installation ID | Prevent stale reinstall data |
| account scope | Prevent cross-account leakage |
| revision | Compare current and stale data |
| event ID | Idempotent event application |
| issued and expiry time | Freshness and timeout |
| payload | Typed domain data |

Do not send credentials, raw tokens, hidden model context, or unnecessary personal data.

## Step 6: build the receiver pipeline

Use this route:

1. Activate the session before sending or reading transport state.
2. Receive a callback or background task.
3. Validate source, scope, schema, size, checksum, and expiry.
4. Decode the typed envelope.
5. Reject stale revisions or record duplicate event IDs.
6. Persist an accepted receipt or pending import.
7. Apply the domain command if authorized.
8. Write a small local projection with revision and freshness.
9. Request a WidgetKit reload when appropriate.
10. Show received, applied, committed, rejected, pending, or failed distinctly.

The callback is not a substitute for a durable receipt.

## Step 7: choose the system surface

### Watch app

Use for detail, local interaction, conflict review, short configuration, and a task that cannot fit a glance.

### Complication

Use for timely, relevant, small values. Support the accessory family that carries the meaning and use a safe fallback for others.

### Smart Stack

Use for context-driven glanceable content. Supply relevance clues or a relevance entries provider where documented, but design for the system not choosing the widget.

### Widget action

Use App Intents for short, typed actions. Validate authorization and expected revision inside the command.

### Handoff

Use a stable deep link or user activity that preserves record identity, source revision, and pending state. The iPhone route should not restart the workflow.

## Step 8: add the watchOS lifecycle route

Classify each operation:

| Operation | Foreground | Background | Recovery |
| --- | --- | --- | --- |
| Render current projection | Yes | WidgetKit request | Load persisted projection |
| Immediate message | Reachable counterpart | No guarantee | Queue or show needs iPhone |
| Context or user-info receipt | Yes or delayed | Yes through system task | Persist and checkpoint |
| File import | Prefer foreground | Bounded receipt only | Resume from durable import record |
| Widget refresh | System-owned | Budgeted | Show source revision and age |
| AI proposal | Prefer user-visible process | Avoid unbounded background generation | Use deterministic fallback |
| Long session | Only documented runtime route | Capability-specific | Save checkpoint on expiration |

SwiftUI backgroundTask is preferred for supported watchOS background interactions where available. Delegate-based WatchKit tasks must be completed. The system may throttle or terminate work.

## Step 9: design WidgetKit data

Store a compact projection in the correctly configured shared container:

- title or value;
- semantic status;
- source revision;
- last updated time;
- expiry;
- redacted value;
- pending count;
- safe deep-link or App Intent identifier.

Never let a widget reach into a live app model or assume a network call can run during rendering. WidgetCenter reload requests are hints.

For Smart Stack, separate:

- relevance clue;
- timeline entry;
- visible content;
- privacy mode;
- action route.

A relevance score or entry does not guarantee visibility.

## Step 10: add App Intents safely

For every intent, write:

- user-facing title;
- typed parameters;
- record-resolution rule;
- authorization check;
- expected-revision check;
- idempotency rule;
- domain command;
- user-readable result;
- projection refresh;
- handoff fallback.

A complication action should not perform a hidden destructive operation. If a command needs confirmation, show a confirmation route or move to the full app.

## Step 11: add AI as a bounded proposal

Use a deterministic input revision and constrained output:

source revision -> context projection -> availability -> proposal -> decode -> allowlist -> stale check -> review -> commit

Keep model availability as a state. A missing model, unsupported watch target, low-power condition, or locale mismatch must produce a safe manual route.

Good companion candidates:

- short labels;
- local categorization from an allowlist;
- ordering suggestions;
- summaries with a strict character limit;
- a proposal for which committed item should be shown next.

Avoid automatic transfer of sensitive generated text, medical or safety conclusions, identity decisions, entitlement changes, or user-visible claims without review.

## Step 12: apply native design

Use watchOS guidance as the design constraint:

- short, timely interactions;
- shallow hierarchy;
- Digital Crown support;
- concise text;
- meaningful complications;
- Always On and redacted variants;
- native controls and system materials;
- supported Liquid Glass composition only where it improves hierarchy;
- system tint and accented/full-color behavior;
- reduced motion and reduced transparency.

The goal is Apple-native fit, not a private-system replica.

## Step 13: verification gates

Do not call a route ready until the evidence matches the claim:

| Gate | Evidence |
| --- | --- |
| Target graph | Xcode project and archive show intended iOS, watchOS, and widget targets |
| Session | Both targets activate and report state on paired hardware |
| Reachability | Immediate message works and failure fallback is truthful |
| Snapshot | Context replaces stale data and revision policy holds |
| Queue | User-info events resume, deduplicate, and reconcile |
| File | File transfer validates and imports safely |
| Background | Watch Connectivity task completes under system timing |
| Widget | Timeline/relevance/projection renders with stale and redacted states |
| Action | App Intent validates and returns a result |
| AI | Availability and deterministic fallback are tested |
| Accessibility | VoiceOver, Dynamic Type, motion, contrast, Digital Crown, and gesture paths |
| Privacy | Locked/Always On/system-surface redaction |
| Energy | Background, widget, and extended-runtime resource boundaries |
| Release | Signed archive, TestFlight or App Store artifact, paired physical devices |

## Implementation worksheet

**Product outcome:**
**Truth owner:**
**Watch target topology:**
**iPhone target:**
**Widget or complication kinds:**
**App Group and shared projection:**
**Account scope:**
**Envelope schema:**
**Revision and event-ID policy:**
**Immediate message use:**
**Application-context use:**
**User-info use:**
**File-transfer use:**
**Complication-transfer use:**
**Background task:**
**App Intent:**
**Handoff route:**
**AI proposal and fallback:**
**Privacy redaction:**
**Accessibility checks:**
**Physical paired-device matrix:**
**Archive and release evidence:**

## Stop conditions

Pause before coding if:

- the watch is expected to be a second server;
- a live message is being treated as durable commit;
- a widget is expected to be a continuously running app;
- a Smart Stack hint is treated as guaranteed display;
- a model proposal is treated as domain truth;
- account or entitlement state is copied without scope and revocation;
- a file callback bypasses validation;
- background work has no cancellation or checkpoint;
- the companion target graph is unverified;
- no physical paired-device proof is planned.

## Sources

- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [WCSession](https://developer.apple.com/documentation/watchconnectivity/wcsession)
- [WCSessionDelegate](https://developer.apple.com/documentation/watchconnectivity/wcsessiondelegate)
- [Transferring data with Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity/transferring-data-with-watch-connectivity)
- [WatchKit](https://developer.apple.com/documentation/watchkit)
- [Life cycles](https://developer.apple.com/documentation/watchkit/life-cycles)
- [Background execution](https://developer.apple.com/documentation/watchkit/background-execution)
- [Using background tasks](https://developer.apple.com/documentation/watchkit/using-background-tasks)
- [WKWatchConnectivityRefreshBackgroundTask](https://developer.apple.com/documentation/watchkit/wkwatchconnectivityrefreshbackgroundtask)
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
