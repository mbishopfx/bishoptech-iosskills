# SwiftUI Watch Connectivity and watchOS companion proof matrix

This proof matrix defines what can be claimed for an iPhone and watchOS companion route. It separates source review, reducer tests, simulator evidence, paired hardware, WidgetKit system behavior, target artifacts, energy, and release proof.

Read the [companion review](../42-framework-deep-dives/107-swiftui-watch-connectivity-watchos-companion-review.md), [design guide](../21-design-deep-dives/135-swiftui-watch-connectivity-watchos-companion-review-design.md), [route](../50-capability-recipes/138-swiftui-watch-connectivity-watchos-companion-review-route.md), and [recipes](../70-code-recipes/150-swiftui-watch-connectivity-watchos-companion-review-recipes.md).

## Evidence levels

| Level | Evidence | Supports | Does not support |
| --- | --- | --- | --- |
| L0 | Official source review and route design | API family, target, lifecycle, and system boundaries were investigated | Correct behavior in a named build |
| L1 | Typed envelope, reducer, and fixture tests | Schema, revision, deduplication, stale rejection, and fallback logic | Pairing or WidgetKit timing |
| L2 | SwiftUI previews and widget fixtures | Layout, family, redaction, Dynamic Type, motion, and copy inspection | Real transfer or system placement |
| L3 | iOS and watchOS simulator | Target composition, fixture routes, basic app lifecycle | Bluetooth/pairing, exact Smart Stack behavior, energy, production signing |
| L4 | Signed iPhone and paired Apple Watch | Activation, reachability, transfers, app lifecycle, WidgetKit installation, accessibility, and paired behavior | Server fulfillment or every future OS version |
| L5 | Instrumented hardware run | Delivery delay, task expiry, energy, suspension, duplicate/reorder, and recovery observations | App Store approval or universal device coverage |
| L6 | Archive, TestFlight, and release artifact | Bundle graph, signing, entitlements, install, target embedding, release route | A guarantee about a user’s future device state |

A simulator screenshot cannot be promoted to L4. A callback cannot be promoted to domain commit. A widget timeline fixture cannot be promoted to Smart Stack placement. A model output cannot be promoted to model availability.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Strong evidence |
| --- | --- | --- |
| The iOS and watchOS targets are correctly related | Project inspection | Signed archive with bundle identifiers and companion keys |
| WCSession activates | Target fixture or unit test | Both targets activate on paired hardware and record state |
| Immediate message works | Mock bridge | Reachability-on hardware exchange plus failure path |
| Application context carries latest state | Reducer fixture | Paired hardware context update with stale revision rejection |
| User-info events are queued | Reducer fixture | Background delivery, restart, duplicate, and cursor run |
| File transfer is safe | Import unit tests | Paired transfer with invalid, duplicate, and valid files |
| Complication data reaches projection | Widget fixture | Physical complication install, transfer, reload, stale state |
| Smart Stack relevance is configured | Source and provider fixture | Physical watch observation with relevance contexts |
| Widget action is safe | App Intent unit test | Physical tap with authorization, result, and reconciliation |
| Watch background task completes | Cancellation test | Physical delayed delivery and task completion evidence |
| Watch app recovers after purge | Persistence test | Terminate or suspend/relaunch paired watch scenario |
| Model fallback works | Availability fixture | Named device/OS availability and fallback run |
| Liquid Glass composition is accessible | Preview and audit | Hardware with motion/transparency/contrast settings |
| Privacy redaction works | Snapshot fixture | Locked/Always On/system-surface physical observation |
| Energy is acceptable | Static review | Instruments or device energy run |
| Release contains the right targets | Build settings inspection | Archive export and TestFlight install |

## Target and artifact proof

Record these values from the actual built products:

| Artifact | Verify |
| --- | --- |
| iOS application | Bundle identifier, version, build, entitlements, App Group, signing |
| watchOS app | Bundle identifier, companion identifier, version/build, independent or companion configuration |
| watch extension or single-target watch app | Target model, embedded relationship, capabilities, signing |
| Widget extension | Widget bundle identifier, host target, App Group, supported families, signing |
| Archive | Embedded watch app, extension, widget, provisioning, entitlements |
| TestFlight build | Installation on intended iPhone and watchOS pair |
| App Store package | Intended device family, target version, privacy declarations, release route |

Do not infer artifact correctness from source filenames or Xcode’s selected scheme. Inspect the archive and built property lists.

## Session and pairing matrix

| Scenario | Expected observation | Evidence |
| --- | --- | --- |
| Unsupported device | isSupported false or documented unsupported path | Fixture plus target availability |
| No paired watch | isPaired false and no false success | Physical iPhone or controlled fixture |
| Paired but app not installed | Installed-state warning | Physical pair |
| Session before activation | No sends before activation completion | Unit or integration fixture |
| Activation succeeds | Active state recorded | Paired hardware |
| Counterpart reachable | Immediate route available | Paired hardware |
| Counterpart not reachable | Fallback route, no fake success | Paired hardware with reachability loss |
| Watch changes on iPhone | Inactive, deactivated, reactivation sequence | Two-watch or documented switch scenario |
| Watch unpaired | Local projection invalidated or marked unavailable | Physical device plus persistence record |
| App reinstall | Installation scope changes and old data is quarantined | Clean-install physical run |
| Account changes | Old scope is purged or quarantined | Account fixture and physical run |

## Transfer matrix

| Transfer | Fixture | Physical test | Failure proof |
| --- | --- | --- | --- |
| Immediate message | Reply and error reducers | Reachability on and off | Timeout, error, and pending UI |
| Application context | Replace and stale-reject tests | New context followed by older context | Older revision does not roll back |
| User-info | Ordered event and dedupe tests | App suspended or terminated during queue | Cursor resumes and duplicate is safe |
| File transfer | File type, size, checksum, import tests | Image or document on paired device | Invalid and expired payloads are rejected |
| Complication user-info | Budget and projection fixture | Active complication receives update | Remaining budget and no-immediate-render claim |
| Domain commit | Command and receipt tests | Owner accepts update | Transport receipt is separate from commit |

Test at least one delayed delivery and one process termination after the callback begins.

## Background and lifecycle matrix

| Situation | Required evidence |
| --- | --- |
| Watch app active | Immediate UI action and local persistence |
| Watch app inactive | Pending state survives transition |
| Watch app background | Bounded task completes and records checkpoint |
| Watch app suspended | Durable projection remains correct |
| Watch app purged | Relaunch restores cursor and last committed state |
| Background Watch Connectivity task | Task receives, persists, refreshes projection, and completes |
| Background task cancellation | Cancellation handler leaves a recoverable state |
| Preferred refresh date | Actual delivery is recorded as delayed or on time, never assumed |
| Extended runtime | Correct documented session type, expiration, invalidation, and energy evidence |
| Widget render | Projection loads without live app dependency |
| Widget reload | Request is recorded as a hint, not immediate-render proof |

## WidgetKit and Smart Stack matrix

| Test | Expected result |
| --- | --- |
| Circular complication | Value remains legible and semantically complete |
| Corner complication | Anchor and value survive masking |
| Inline complication | Text is concise and accessible |
| Rectangular complication | Supporting context does not obscure main value |
| Full-color mode | Color reinforces but does not carry all meaning |
| Accented or tinted mode | Hierarchy and contrast remain valid |
| Redacted mode | Sensitive content is removed or neutral |
| Stale projection | Age and recovery path are visible |
| Empty projection | No fake value or invented AI placeholder |
| Relevance provider | Valid relevance entry is returned for fixture context |
| Relevance absent | Widget remains useful when not elevated |
| Widget action | App Intent returns a meaningful result |
| Widget process isolation | No reliance on live app bindings or model session |
| Reload request | Timeline generation is tested separately from request submission |

Use a physical Apple Watch for actual Smart Stack placement, appearance, and timing claims.

## App Intent matrix

| Case | Verify |
| --- | --- |
| Valid record | Stable ID resolves and command applies |
| Missing record | Intent returns a safe error |
| Unauthorized record | No mutation and no data leak |
| Stale expected revision | Conflict or revalidation result |
| Duplicate invocation | Idempotent result |
| Offline watch | Queue or handoff state |
| Long operation | Pending route, not a blocked widget |
| Destructive operation | Confirmation or explicit policy |
| AI-backed action | Candidate is validated and never silently committed |
| Projection refresh | Updated local projection has a new revision |

## AI availability and review matrix

| State | UI and behavior |
| --- | --- |
| Model ready | Show source, candidate, constraints, and review |
| Model unavailable | Use deterministic fallback |
| Target unsupported | Do not compile or route as if available |
| Low power or memory pressure | Defer or use fallback |
| Locale or region mismatch | Explain unavailability without inventing output |
| Source revision changed | Discard or regenerate candidate |
| Candidate violates allowlist | Reject and show manual route |
| User rejects | Preserve source truth and decision |
| User approves | Commit a new domain revision |
| Committed result transfers | Send typed committed projection, not raw prompt context |

Record model availability, context version, source revision, candidate, validation, user decision, and committed revision.

## Design and accessibility matrix

| Check | Preview | Simulator | Physical watch |
| --- | --- | --- | --- |
| Dynamic Type | Inspect | Run | Run on intended sizes |
| VoiceOver | Inspect labels | Navigate | Navigate complication and app |
| Reduce Motion | Static variant | Run | Run |
| Reduce Transparency | Fallback | Run | Run |
| Increased contrast | Inspect | Run | Run |
| Digital Crown | Not sufficient | Simulate | Rotate and select |
| Hand gesture or double tap | Source review | Simulate where possible | Physical action |
| Haptic feedback | Fixture | Simulate | Observe and record |
| Always On | Static fixture | Limited | Physical watch |
| Locked/redacted | Snapshot fixture | Limited | Physical watch face and Smart Stack |
| Tinted/accented/full-color | Widget fixture | Run | Actual system rendering |

## Privacy matrix

| Data | Allowed in app detail | Allowed in complication | Allowed in Smart Stack | Allowed in AI context |
| --- | --- | --- | --- | --- |
| Generic count | Yes | Usually | Usually | If needed |
| Name | Authorized detail | Prefer redacted | Prefer redacted | Only with policy |
| Message body | Explicit detail | No by default | No by default | Only if allowed |
| Health value | Authorized route | Minimum necessary | Minimum necessary | Avoid unsupported interpretation |
| Account balance | Authorized detail | Usually no | Usually no | Never for a cosmetic proposal |
| Credentials and raw tokens | No display | No | No | No |

Verify sign-out, deletion, unpairing, reinstall, and locked-device behavior.

## Energy and performance matrix

Measure or review:

- callback duration;
- decode and validation time;
- file import duration;
- background task completion time;
- WidgetKit timeline generation time;
- number and size of shared projection reads;
- App Intent execution time;
- model memory and energy when applicable;
- extended runtime expiration and invalidation;
- battery impact of repeated transfers;
- cleanup after cancellation and suspension.

If the route needs continuous work, select a documented watchOS background session or a different product architecture. Do not use a widget or Watch Connectivity callback as an always-on worker.

## Release checklist

- Xcode project has the intended iOS, watchOS, widget, and test targets.
- Bundle prefixes and companion identifiers are correct.
- App Groups are identical only where intended and have a migration plan.
- Entitlements and provisioning are present in the archive.
- Widget extension supports intended families and platforms.
- App Intent metadata and supported target declarations are correct.
- Privacy usage and redaction policy are reviewed.
- Foundation Models availability is runtime-gated.
- A signed iPhone and paired Apple Watch run the primary, offline, delayed, and recovery paths.
- TestFlight installation preserves the target relationship.
- The release archive is inspected rather than assumed from a simulator build.

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
- [Using extended runtime sessions](https://developer.apple.com/documentation/watchkit/using-extended-runtime-sessions)
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
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
