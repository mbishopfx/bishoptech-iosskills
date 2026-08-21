# SwiftUI Watch Connectivity and watchOS companion review

This page is the focused companion-device review for an iOS app with a watchOS app, Watch Connectivity transport, and WidgetKit complications or Smart Stack surfaces. It extends the earlier Watch Connectivity route instead of replacing it: the earlier material gives a compact recipe, while this page treats paired-device state, transport semantics, watchOS lifecycle, WidgetKit projection, App Intent actions, local AI, native watchOS design, and physical paired-device proof as one auditable product route.

The central rule is:

iOS domain truth or watch domain truth -> typed companion envelope -> WCSession transport -> local watch cache or iPhone cache -> watchOS app or WidgetKit projection -> optional reviewed action

Watch Connectivity is a transport and wake-up mechanism. It is not a server, a database, a guarantee that a live message will arrive, a replacement for account synchronization, or proof that a complication has rendered. WidgetKit is a system-owned projection process, not a continuously running watch app. A model proposal is not a transfer receipt or a committed domain mutation.

## Route thesis

Choose the smallest companion surface that matches the user outcome:

| Outcome | Primary route | What it actually owns | What it does not prove |
| --- | --- | --- | --- |
| Send a response while both apps are visibly active | WCSession immediate message | A reachability-gated request/reply exchange | Durable delivery, offline delivery, or server persistence |
| Replace the counterpart’s latest snapshot | updateApplicationContext | One most-recent contextual dictionary | Delivery at a precise time or preservation of every intermediate state |
| Queue ordered small events or commands | transferUserInfo | Background queued dictionaries | A transactionally committed business operation |
| Move a larger document or image | transferFile | Background file transfer with metadata | That the receiver accepted, decoded, or committed the file |
| Refresh a watch complication from iPhone | transferCurrentComplicationUserInfo plus WidgetKit reload | A complication-oriented transfer subject to system budget | Immediate timeline rendering or fresh data on every wrist raise |
| Show glanceable state | WidgetKit timeline or relevance provider | A cached, archived watchOS system projection | An always-live view, arbitrary network access, or model execution during rendering |
| Perform a small action from a widget or complication | App Intent | A system-triggered action with typed input | That the domain mutation succeeded without an explicit result and reconciliation path |
| Share authoritative account history | Server or CloudKit plus local persistence | Durable identity and conflict resolution | That the paired device is reachable right now |

The route must name the source of truth before choosing a transfer. If the iPhone and watch can both mutate a record, define ownership, revision, conflict policy, and idempotency before writing the bridge.

## Authority map

Apple’s official documentation supplies different pieces of this route:

| Concern | Primary authority | Working interpretation |
| --- | --- | --- |
| Paired application transport | Watch Connectivity and WCSession | Configure and activate a session in both the iOS app and watchOS app. |
| Activation, reachability, and watch switching | WCSession and WCSessionDelegate | Activation is asynchronous; iOS must handle inactive and deactivated states when multiple watches are supported. |
| Background delivery | WatchKit background execution and SwiftUI backgroundTask | Delivery can wake or resume the watch app, but the system controls timing and budget. |
| Watch app lifecycle | WatchKit life cycles and watchOS app guidance | The watch app can be inactive, background, suspended, or purged; state must survive process loss. |
| Glanceable projection | WidgetKit, watch complications, and Smart Stack guidance | The widget extension renders archived entries and relevance-driven content in a separate system-managed process. |
| Small system action | App Intents and WidgetKit interactivity | A widget or complication action should be short, typed, idempotent, and reconciled with domain state. |
| Watch visual language | Designing for watchOS and HIG complications/widgets | Glanceability, short interactions, Digital Crown ergonomics, Always On, privacy, and constrained layouts lead. |
| Local intelligence | Foundation Models and SystemLanguageModel | Availability is a runtime/device/OS condition; AI output must be bounded, reviewed, and revalidated. |
| Distribution proof | Xcode target/project and release-build documentation | Bundle identity, signing, embedded target relationships, and release behavior require artifact and device evidence. |

## Product and target decisions

### Independent watch app or companion app

Start with the product topology:

| Topology | Use when | Configuration questions |
| --- | --- | --- |
| Watch-only app | The watch can deliver the complete product and does not require an iPhone companion | Is the watch data source local, network-backed, or HealthKit-backed? Does the product truly need no companion? |
| Companion iOS and watchOS apps | The watch is a focused extension of an iPhone product | Which records are local to the watch, which are projections from iPhone, and which require a server? |
| Existing iOS project with a watch target | The iOS app already owns the domain and a paired watch surface is an addition | Are bundle prefixes, companion identifiers, capabilities, shared code, and target resources aligned? |

Apple’s watchOS project setup documentation distinguishes watch-only projects, a new watch app with a companion iOS app, and adding a watch target to an existing iOS project. Do not infer that a watch target is independent merely because it has SwiftUI code. Confirm the generated target topology, installation relationship, bundle identifiers, and information-property-list values in the built artifacts.

For a companion target, verify the following:

- The watchOS app and the iOS app have the intended companion relationship.
- The watch target’s WKCompanionAppBundleIdentifier matches the iOS CFBundleIdentifier where the project requires it.
- The watch app and watch extension identifiers follow the project’s expected bundle-ID prefix relationship.
- The watchOS widget extension has the intended host relationship and App Group configuration if it reads shared data.
- Each target has the capabilities and signing profile it actually needs.
- A watch-only or independent watchOS path is not accidentally coupled to iPhone reachability.

### Pairing is runtime state, not entitlement truth

WCSession exposes several facts that should remain separate in the UI and domain projection:

| Observation | Meaning | Safe UI language |
| --- | --- | --- |
| isSupported | The current device can use a session object | Companion transport supported |
| isPaired | The iPhone has a paired Apple Watch | A watch is paired |
| isWatchAppInstalled | The active paired watch has the watch app installed | Watch app installed |
| isCompanionAppInstalled | The counterpart has the app installed | Counterpart installed |
| activationState | The session’s activation lifecycle | Transport session state |
| isReachable | The counterpart is available for immediate messaging | Live message path available |
| isComplicationEnabled | The current watch uses a complication | Complication is in use |
| receivedApplicationContext | Most recent context delivered by the counterpart | Last received snapshot, with revision and age |

Do not turn isPaired or isReachable into a claim that a business account is signed in, that a user owns a record, or that a transfer has been processed. Do not use a green “connected” badge as a substitute for the last successful domain synchronization timestamp.

## Session activation and delegate ownership

Each side configures its own WCSession.default, assigns a long-lived delegate, and calls activate when it is ready to communicate. Activation is asynchronous. The delegate receives activation completion, state changes, reachability changes, incoming application context, messages, user-info transfers, and file-transfer callbacks.

The iOS side has an additional multi-watch responsibility. Apple documents sessionDidBecomeInactive and sessionDidDeactivate for the transition between active watches. While inactive or deactivated, new transfers cannot be initiated; after deactivation, the iOS app activates the session again for the new watch. A route that ignores these callbacks may appear correct with one watch and fail when Auto Switch changes the active watch.

Keep this architecture explicit:

1. A target-local bridge owns WCSession delegate registration and activation.
2. Delegate callbacks are normalized into Sendable envelopes.
3. An actor or serial state owner validates schema, source, revision, and size.
4. The state owner writes a durable local cache or domain event.
5. The UI and WidgetKit extension read a projection with freshness metadata.
6. App Intent actions call a domain command and return a typed result.
7. The bridge reports transport evidence separately from domain commit evidence.

The delegate should not directly mutate SwiftUI view state, perform a long network request, invoke a language model, or assume the app remains alive after the callback returns. Keep the callback fast and make downstream work resumable.

## Transfer semantics

### Immediate message

sendMessage and sendMessageData are for immediate communication with a reachable counterpart. isReachable must currently be true. Use this route for a short request/reply exchange where the user is watching the result and a fallback exists if reachability changes.

Examples:

- Ask the iPhone for a current display label while the user is in the watch app.
- Send a small “mark as seen” request and show pending until the iPhone replies.
- Ask the watch for a local sensor state while both apps are active.

Do not use immediate messages as the only path for a purchase, workout completion, journal entry, or other high-value mutation. If the message fails, the user needs an explicit pending or retry route.

### Application context

updateApplicationContext sends a dictionary representing current app context. A new context replaces the context already in the pipeline. This is the right semantics for “latest known state,” not “every event.”

Use a context envelope with:

- schema version;
- source target;
- account or installation scope without secrets;
- domain revision;
- issued-at time;
- data freshness;
- privacy redaction state;
- payload;
- optional checksum or content identifier.

When a newer context arrives, replace the local snapshot only if the revision and scope are acceptable. A delayed older context must not roll the watch backward. If the app receives a context for a different account or installation, quarantine it and require explicit reconciliation.

### User-info transfer

transferUserInfo queues dictionaries for background delivery and delivers them in order received according to Apple’s transfer documentation. Use it for small events that must not be collapsed into one latest snapshot, such as:

- a bounded sequence of user-approved actions;
- a journal entry created on the watch;
- a durable “read through revision” marker;
- a small change event that the counterpart can idempotently reconcile.

Queued delivery is not the same as business transaction commit. Give every event a stable event ID, source, revision, and operation kind. The receiver records applied IDs or a monotonic cursor and can safely process duplicates or resume after termination.

### File transfer

transferFile is for larger payloads such as images, documents, or export packages. Treat the file URL and metadata as transport input. On receipt:

1. Move or copy the file into app-owned storage before the callback’s temporary location becomes invalid.
2. Validate file type, size, checksum, schema, source, account scope, and revision.
3. Decode off the UI path.
4. Persist an import result or a rejected receipt.
5. Delete or expire the source according to retention policy.

Never pass an unvalidated received file directly into a WidgetKit timeline, a model prompt, or a user-visible share surface.

### Complication-oriented transfer

transferCurrentComplicationUserInfo is a specialized iPhone-to-watch path for active complication data. Apple’s sample documentation describes a daily transfer budget and exposes remainingComplicationUserInfoTransfers. Treat the transfer as a budgeted hint that can update a WidgetKit complication, not as a general synchronization channel. Prefer application context or user-info for broader state, and use a server or local persistence for authoritative history.

## Typed envelope and revision policy

Use one cross-target envelope instead of letting each callback interpret ad hoc dictionaries:

~~~swift
import Foundation

struct CompanionEnvelope<Payload: Codable & Sendable>: Codable, Sendable {
    enum Kind: String, Codable, Sendable {
        case snapshot
        case event
        case file
        case complication
        case commandResult
    }

    let schema: Int
    let kind: Kind
    let source: String
    let installationID: String
    let accountScope: String?
    let revision: Int64
    let eventID: String?
    let issuedAt: Date
    let expiresAt: Date?
    let payload: Payload
}
~~~

The exact encoding can be JSON, a property-list-compatible dictionary, or another target-supported representation. The important contract is semantic:

- schema is explicit and migratable;
- source distinguishes iPhone, watch, server, or extension;
- installationID prevents stale data from a deleted and reinstalled app from being accepted blindly;
- accountScope prevents cross-account leakage;
- revision provides ordering;
- eventID provides idempotency;
- issuedAt and expiresAt expose freshness;
- payload is typed at the domain boundary.

Keep transport adapters at the edge. The domain should receive a typed observation such as CompanionObservation.snapshot, CompanionObservation.event, or CompanionObservation.fileReady rather than a raw dictionary.

## Receiver pipeline

Use this sequence for every incoming transfer:

1. Receive the callback on the target’s session delegate or SwiftUI background task.
2. Capture only the minimum raw data needed for validation.
3. Check source target, installation scope, account scope, schema, byte count, and checksum.
4. Decode into a versioned envelope.
5. Reject expired, future-skewed, or unsupported payloads with a recorded reason.
6. Compare revisions and event IDs with the local cursor.
7. Persist the accepted envelope or a durable pending receipt.
8. Recompute the local projection.
9. Request a bounded WidgetKit reload if a widget or complication depends on the projection.
10. Surface a UI state that distinguishes received, applied, rejected, pending, and failed.

Do not use a callback as the only record of receipt. If the process is terminated after the callback begins, the app needs a durable cursor or receipt so the next wake can resume.

## Shared containers and local caches

Widget extensions and app targets can share data through an App Group when the target configuration, entitlement, and storage policy are correct. The shared store should contain a small, versioned projection—not a view model, secret, giant database snapshot, or model session.

A useful shared projection includes:

- a last-known domain value;
- a user-visible timestamp;
- source and revision;
- freshness or expiry;
- redacted display fields;
- a pending-action count;
- a sync state;
- a schema version;
- a recovery hint.

Store transport receipts and domain records separately. A received event can exist while its domain mutation is still pending. The WidgetKit extension should render the last safe projection and a clear stale or unavailable state rather than making up freshness.

If the product needs server-authoritative sync, use Watch Connectivity as an opportunistic companion path and retain a server or CloudKit reconciliation route. If the watch can function offline, define the local queue, conflict resolution, and account handoff before implementation.

## Background delivery and watchOS task budgets

watchOS primarily runs apps in the foreground. Background execution is available for specific system-supported cases and is budgeted. The system may delay, throttle, suspend, or terminate the app. A preferred date is not an exact wake time.

For SwiftUI watchOS targets, use the documented backgroundTask modifier for relevant system task kinds where supported. The system executes the closure for a short period and completes the task when the closure returns. Use cancellation handling, bounded work, and durable checkpoints.

For delegate-based targets, WKWatchConnectivityRefreshBackgroundTask is delivered through the app delegate’s handle method when the paired device sends data through application context, user-info, or complication-oriented transfer. The task must be completed. Do not perform an unbounded import, network retry loop, or language-model generation inside a few-second background window.

A background receiver should:

- decode and persist first;
- schedule longer work through a documented route;
- complete or cancel quickly;
- record an expiration or failure state;
- request a projection refresh;
- allow foreground recovery to finish the job.

If a watch app uses WKExtendedRuntimeSession, choose a documented session type that matches the user activity. It is not a general-purpose “keep my app alive” switch. Health, audio, location, Bluetooth, and workout routes have their own capability and proof requirements.

## watchOS lifecycle

The watchOS life-cycle documentation describes not running, inactive, active, background, and suspended states. A suspended app is in memory but not executing, and the system may purge it. A background delivery can be delayed to preserve battery. If the app is running in the foreground, delivery can be more immediate; if it is backgrounded, the system may wake it later.

Model the lifecycle independently from domain state:

| Lifecycle state | UI expectation | Domain behavior |
| --- | --- | --- |
| Not running | Show launch-safe initial state from persisted projection | Load the last committed local snapshot and pending cursor |
| Inactive | Avoid assuming user input is arriving | Finish small transitions and preserve pending route |
| Active | Allow short interaction and immediate messages if reachable | Perform user-approved commands and refresh local truth |
| Background | Do only bounded system-invoked work | Accept, persist, and checkpoint transfers |
| Suspended or purged | No code executes | Recover from durable storage on next launch |

ScenePhase is useful for UI coordination, but it is not a persistence layer. Save route identity, pending command, selected record, and last accepted revision in durable storage before expecting lifecycle transitions.

## WidgetKit complications and Smart Stack

WidgetKit creates a separate extension process that renders a timeline or relevance-driven entry. The watchOS app and the widget extension can share projection data, but the widget cannot assume the watch app is running or that arbitrary app bindings are available at render time.

### Timeline versus relevance

Use a timeline when the product can describe future entries or a bounded refresh policy. Use a relevance entries provider when the watchOS Smart Stack should receive contextual clues for when a widget is useful. Relevance is a hint to the system; it does not force the widget to appear.

On Apple Watch, the Smart Stack is context-driven and people can pin widgets. The system decides placement and rendering context. A product should optimize for:

- one useful glance;
- a clear timestamp or freshness cue;
- a small number of semantic values;
- a fallback when data is unavailable;
- a privacy-safe locked or Always On appearance;
- a deep link or App Intent for the next action.

### Complication families and appearances

WidgetKit accessory families include circular, corner, inline, and rectangular forms for watch complications. Support every family for which the product has meaningful content. Do not force a complex chart into a family that cannot support it; show a useful label, icon, or safe launch affordance instead.

The same watchOS widget may appear as a complication or in the Smart Stack with different appearance and background behavior. Apple documents accented and full-color contexts for Apple Watch. Treat the system rendering mode as input, not as a surface to fight with custom backgrounds.

### Widget refresh

WidgetCenter reload requests are hints. A reload call does not prove that the system immediately requested a new timeline or that the user saw the new value. The shared projection must carry its own revision and freshness so a stale widget can be recognized.

Do not run a generative model in a widget or complication renderer. Generate a bounded proposal in an allowed process, validate it against current data, persist a compact result, and render only the typed projection.

## App Intents and companion actions

App Intents can provide actions for widgets, watch complications, Siri, Shortcuts, and other system experiences. A widget or complication button executes the intent’s perform method in a system extension context. The action should:

- accept typed, minimal parameters;
- resolve the target record safely;
- check account and authorization scope;
- validate the expected revision;
- perform an idempotent domain command;
- return a user-readable result;
- request a projection refresh when appropriate.

An App Intent action is not a license to write arbitrary state from an untrusted widget tap. For sensitive or irreversible actions, require confirmation, use an explicit pending state, and reconcile with the iPhone or server.

Use App Shortcuts or donated intents for discoverability only when the user outcome is stable and the required target can be resolved without hidden UI state. Keep the watch action short enough to finish within system limits.

## On-device AI boundaries

The watch companion route is a strong place for bounded, private suggestions such as:

- proposing which of several user-owned items should be shown next;
- summarizing a local note into a short glanceable label;
- proposing a priority for a queue;
- generating a compact wording candidate for a notification or complication.

The model must not be the transport layer, the identity provider, the entitlement authority, or the source of truth. Use this pipeline:

accepted source data -> deterministic context projection -> availability check -> constrained generation -> schema decode -> allowlist and length validation -> revision check -> user review or explicit policy -> commit -> companion transfer

On watchOS, do not assume Foundation Models is available merely because the iPhone supports Apple Intelligence. Check the target’s SDK and deployment availability, SystemLanguageModel availability, device readiness, region/locale conditions, and any memory or energy constraints. If the model is unavailable, return a deterministic fallback such as the source label, a sorted list, or a “needs iPhone” state.

For a companion proposal, record:

- source revision;
- model availability state;
- prompt/context version;
- generated candidate;
- validation result;
- user decision;
- committed result revision.

Never generate or transfer sensitive data to a paired device solely because the model suggested it. The domain policy decides whether the data is allowed on the watch, in a widget, or on an Always On surface.

## Native watchOS and Liquid Glass design

Liquid Glass is a system material and interaction language, not a reason to place a translucent card behind every value. On watchOS, use native SwiftUI controls, navigation, lists, gauges, labels, symbol rendering, and platform-specific layout behavior first. Apply supported glass effects only where they improve hierarchy, grouping, or interaction.

Design the shell around the wrist:

- one primary task per screen;
- short vertical hierarchy;
- Digital Crown-friendly scrolling or selection;
- clear tap targets;
- meaningful haptics only for state changes;
- concise labels that survive Dynamic Type;
- Always On and reduced-motion variants;
- a surface that still works without a custom background;
- clear transition from glance to detail.

For a watch widget or complication, prefer the system’s accessory families, background behavior, tint, and rendering modes. Do not imitate private Apple surfaces or rely on undocumented blur/shape behavior. The goal is native platform fit, not a screenshot replica that fails under tinted, accented, locked, or Always On conditions.

## Accessibility and alternate input

Test the watch route with:

- VoiceOver and meaningful element order;
- larger text and Dynamic Type;
- Bold Text and increased contrast;
- Reduce Motion and reduced transparency;
- color differentiation without color alone;
- Switch Control or other assistive input where relevant;
- Digital Crown selection and scrolling;
- hand gesture or double-tap behavior when the product uses a primary action;
- haptic alternatives to visual-only status;
- an Always On representation that remains legible and private.

A complication must remain understandable when the system applies tint, masks, or a different family. A widget action must have an accessible label and a result that does not depend on animation.

## Privacy and data minimization

The watch face, Smart Stack, notifications, and Always On display can be visible to nearby people. Redact names, messages, health details, account balances, access codes, and other sensitive fields when the device is locked or the surface is not private.

Define per-surface data policy:

| Surface | Default policy |
| --- | --- |
| Watch app detail | Show only data the user explicitly opened and the target is authorized to access |
| Watch complication | Show the minimum glanceable value, with a privacy-safe fallback |
| Smart Stack | Use relevant context without exposing sensitive content by default |
| Notification | Use the system’s privacy controls and concise, non-sensitive text |
| Shared App Group projection | Store only the fields the widget needs; never store secrets for convenience |
| Watch Connectivity envelope | Exclude credentials, raw tokens, and unnecessary personal data |
| AI context | Include only source fields allowed by the product policy and current device |

If the user signs out, changes account, deletes data, or unpairs a device, invalidate local projections and pending transfers according to the product’s retention policy. A paired watch is not a safe place to keep indefinite copies of every iPhone record.

## Failure and recovery matrix

| Failure | User-visible state | Recovery |
| --- | --- | --- |
| Unsupported session | Companion unavailable | Use local/watch-only route or explain device support |
| Not paired | No watch connected | Keep iPhone workflow complete and offer setup guidance |
| Watch app not installed | Companion not ready | Use the system installation path; do not silently drop a high-value action |
| Session not activated | Preparing companion link | Queue or persist until activation completes |
| Not reachable | Live path unavailable | Use application context, user-info, server sync, or a pending state |
| Context rejected | Stale or out-of-scope snapshot | Keep prior safe projection and record rejection |
| User-info pending | Queued event | Show pending without claiming commitment |
| File transfer failed | Import unavailable | Retry or request a foreground transfer with an error reason |
| Background task delayed | Last-known state | Show timestamp and refresh in foreground |
| Widget reload deferred | Projection may be stale | Render revision and expiry; do not promise immediate update |
| Account scope changed | Re-authentication needed | Purge or quarantine old-scope data and re-establish identity |
| Model unavailable | Deterministic fallback | Use source text, rules, or ask the iPhone to help |
| Watch switched | Rebinding companion | Finish old-session delivery, activate the new watch, reconcile state |
| App purged | Recovered from disk | Reload durable state and resume pending cursor |

## Evidence ladder

| Level | Evidence | Claim it can support |
| --- | --- | --- |
| L0 | Source-linked design and route page | The documented API family and boundary were investigated |
| L1 | Typed envelope and reducer tests | Schema, revision, idempotency, and fallback logic behave in fixtures |
| L2 | SwiftUI previews and widget fixtures | Layout, redaction, Dynamic Type, and appearance variants are inspectable |
| L3 | iOS and watchOS simulator runs | Basic target composition and fixture-driven lifecycle paths work in simulation |
| L4 | Signed paired iPhone and Apple Watch | Activation, reachability, background delivery, transfer, WidgetKit, and input behavior observed on hardware |
| L5 | Instrumented lifecycle and energy run | Timing, suspension, task expiration, duplicate/reorder, and energy behavior measured |
| L6 | Archive/TestFlight/App Store release path | Target embedding, identifiers, entitlements, distribution, and release artifacts verified |

Do not call L1 or L3 “paired-device proof.” Do not call an application-context callback “domain commit.” Do not call a widget screenshot “timeline budget proof.” Do not call a model output “AI availability proof.”

## Build checklist

- Name the watch outcome and the source of truth.
- Choose independent watch, companion watch, WidgetKit, App Intent, or server route.
- Configure and verify the iOS and watchOS targets and bundle relationship.
- Activate WCSession on both sides and model activation, reachability, pairing, installation, and watch switching.
- Choose immediate message, application context, user-info, file transfer, or complication transfer by semantics.
- Wrap payloads in a versioned, scoped, revisioned, idempotent envelope.
- Persist accepted receipts and projections before rendering.
- Add backgroundTask or the correct WatchKit background route with cancellation and completion.
- Keep WidgetKit rendering small, redacted, and independent of the watch app process.
- Use relevance and timelines as hints; show freshness and fallback.
- Keep App Intents typed, short, authorized, revision-aware, and idempotent.
- Gate Foundation Models on actual target/device availability and preserve a deterministic fallback.
- Use native watchOS controls and supported Liquid Glass composition with reduced-motion and privacy variants.
- Test VoiceOver, Dynamic Type, Always On, tint/accented/full-color modes, and alternate input.
- Run the paired physical-device matrix and record evidence.
- Inspect archive entitlements, bundle identifiers, embedded targets, and release behavior.

## Sources

- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [WCSession](https://developer.apple.com/documentation/watchconnectivity/wcsession)
- [WCSessionDelegate](https://developer.apple.com/documentation/watchconnectivity/wcsessiondelegate)
- [activate](https://developer.apple.com/documentation/watchconnectivity/wcsession/activate%28%29)
- [Transferring data with Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity/transferring-data-with-watch-connectivity)
- [WatchKit](https://developer.apple.com/documentation/watchkit)
- [WKApplication](https://developer.apple.com/documentation/watchkit/wkapplication)
- [WKApplicationDelegate](https://developer.apple.com/documentation/watchkit/wkapplicationdelegate)
- [Life cycles](https://developer.apple.com/documentation/watchkit/life-cycles)
- [Background execution](https://developer.apple.com/documentation/watchkit/background-execution)
- [Using background tasks](https://developer.apple.com/documentation/watchkit/using-background-tasks)
- [WKWatchConnectivityRefreshBackgroundTask](https://developer.apple.com/documentation/watchkit/wkwatchconnectivityrefreshbackgroundtask)
- [Using extended runtime sessions](https://developer.apple.com/documentation/watchkit/using-extended-runtime-sessions)
- [WKExtendedRuntimeSession](https://developer.apple.com/documentation/watchkit/wkextendedruntimesession)
- [watchOS apps](https://developer.apple.com/documentation/watchos-apps)
- [Setting up a watchOS project](https://developer.apple.com/documentation/watchos-apps/setting-up-a-watchos-project)
- [WKCompanionAppBundleIdentifier](https://developer.apple.com/documentation/bundleresources/information-property-list/wkcompanionappbundleidentifier)
- [CFBundleIdentifier](https://developer.apple.com/documentation/bundleresources/information-property-list/cfbundleidentifier)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [Creating accessory widgets and watch complications](https://developer.apple.com/documentation/widgetkit/creating-accessory-widgets-and-watch-complications)
- [Developing a WidgetKit strategy](https://developer.apple.com/documentation/widgetkit/developing-a-widgetkit-strategy)
- [Widgets and watch complications](https://developer.apple.com/documentation/widgetkit/widgets-and-complications-collection)
- [Increasing the visibility of widgets in Smart Stacks](https://developer.apple.com/documentation/widgetkit/widget-suggestions-in-smart-stacks)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Migrating ClockKit complications to WidgetKit](https://developer.apple.com/documentation/widgetkit/converting-a-clockkit-app)
- [Creating views for widgets, Live Activities, and watch complications](https://developer.apple.com/documentation/widgetkit/creating-views-for-widgets-live-activities-and-watch-complications)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Widgets, Live Activities, and Controls](https://developer.apple.com/documentation/appintents/widgets-live-activities-and-controls)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos/)
- [Complications](https://developer.apple.com/design/human-interface-guidelines/complications)
- [Widgets](https://developer.apple.com/design/human-interface-guidelines/widgets)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
