# Interactive snippet and App Intent proof matrix

## Scope

This matrix verifies a route that exposes an AppIntent, returns a static or interactive snippet, performs follow-up actions, and re-renders the current state. It separates documentation, compilation, deterministic behavior, signed system invocation, physical-device behavior, privacy/accessibility, and release evidence.

A snippet that renders in a preview is not proof that the system can discover it. A successful perform() fixture is not proof that the extension process, locked device, Apple Intelligence, Siri, or a production release will execute it.

## Evidence levels

| Level | What it can prove | What it cannot prove |
| --- | --- | --- |
| Source record | The intended API and documented constraints were identified | That the selected SDK compiles the exact code |
| Compile fixture | Types, target membership, availability branches, and signatures compile in a named SDK | Runtime authorization, system placement, or hardware behavior |
| Unit or actor test | Parameter validation, authorization decisions, idempotency, projection mapping, and errors | System discovery, voice behavior, or extension lifecycle |
| SwiftUI or UI test | View states, labels, control presence, repeated render fixture, and app handoff route | Actual Siri, Spotlight, or Apple Intelligence selection |
| Simulator or system preview | Layout and deterministic system-surface state | Physical device, locked-device privacy, or model readiness |
| Signed physical-device run | Real target membership, system invocation, permissions, process choice, and interaction | Universal availability, production ranking, or every supported locale |
| Release artifact | Entitlements, extensions, metadata, privacy manifest, and target configuration in the signed build | Successful App Store discovery or real-user behavior |
| TestFlight or production observation | Delivered behavior for the tested account, device, OS, and path | Behavior on untested configurations or future OS versions |

## Core proof matrix

| Proof item | Fixture or command | Passing evidence | Boundary |
| --- | --- | --- | --- |
| AppIntent metadata | Compile and inspect title, description, parameters, summaries, discoverability | Localized metadata appears as intended in the named target | Does not prove ranking or universal Siri or Apple Intelligence discovery |
| Static snippet | Invoke intent with deterministic current data | Static view presents the right result and no interactive control is falsely implied | Does not prove interactive controls can work |
| Interactive result shape | Compile a result using ShowsSnippetIntent | Value and snippet contracts both compile and return correctly | Exact generic signatures remain SDK-sensitive |
| SnippetIntent render | Perform SnippetIntent with fixture data | View is compact, privacy-safe, and complete | Does not prove system container layout |
| Repeated render | Perform the same SnippetIntent multiple times with changed store state | Each render re-fetches current state and contains no render side effect | Does not prove process retention duration |
| Button action | Tap a snippet Button attached to an AppIntent | Domain write commits or returns a truthful error | Does not prove the system will re-run the snippet in every context |
| Toggle action | Toggle on and off with current and stale state | Idempotent result and next render match durable state | Does not prove locked-device behavior |
| Duplicate tap | Send repeated actions or simulate retry | At most one intended mutation; final state is deterministic | Does not prove network delivery semantics |
| Deleted record | Delete the entity before action | No private data leak; action returns recoverable failure | Does not prove every EntityQuery path filters deletion |
| Unauthorized record | Change account or permission before invocation | Query/action rejects or hands off without revealing details | Does not prove system cache has cleared |
| Stale projection | Age snapshot past product threshold | Freshness is visible and retry or open-app route works | Does not prove a remote refresh arrives |
| Confirmation snippet | Invoke requestConfirmation with current draft | Scope, consequence, confirm, and cancel are clear | Does not prove all voice or UI presentation variants |
| Confirmation cancel | Cancel the system confirmation | No domain mutation and honest non-success result | Does not prove cancellation error mapping is identical on all surfaces |
| Parameter edit | Change a value inside confirmation snippet | Intent reads latest value after confirmation returns | Does not prove a stale cached object is impossible elsewhere |
| Reload | Change external data and call SnippetIntent.reload() | Visible snippet refreshes to current state in the tested path | Reload is not a deadline or durability guarantee |
| Long task | Use loading/result fixture and timeout | Snippet remains understandable and exits loading honestly | Does not prove background execution budget |
| Execution target | Inspect target membership and run signed build with app or extension candidates | Intent runs only where intended and dependencies are available | Does not prove a future OS chooses the same process |
| App termination | Terminate main app before system invocation | Headless intent or extension path works or presents an explicit handoff | Does not prove every framework is available in the extension |
| Control Center limitation | Invoke the same action from a Control Center control | Control returns direct value/action result or uses a different route | A control cannot display a snippet |
| Widget reuse | Reuse snippet view/action only where target contract fits | Widget-specific state, timeline, and interaction remain correct | Shared view does not remove extension proof |
| Siri or voice | Invoke from the signed device with supported locale | Spoken request resolves, performs, and returns privacy-safe dialog | Does not prove Apple Intelligence invocation or ranking |
| Spotlight or Shortcuts | Add/use App Shortcut or system search route | Intent/entity is discoverable and parameter resolution is usable | Does not prove every phrase or language |
| Apple Intelligence | Test on an eligible device/configuration with the feature enabled | The documented action/entity route is available in the tested configuration | Never claim guaranteed model selection or universal discovery |
| Privacy | Test locked/unlocked, signed-out, account-switched, and redacted states | No unauthorized text, entity label, or dialog is exposed | Does not prove system caches are instantly purged |
| VoiceOver | Complete the task with VoiceOver | Reading order, labels, values, and actions are usable | Does not replace tests for other assistive technologies |
| Voice Control | Use visible action names by voice | Controls are reachable by clear spoken names | Does not prove every locale’s voice grammar |
| Switch Control | Navigate the complete task | No essential action depends on an inaccessible gesture | Does not prove external hardware compatibility |
| Dynamic Type | Test largest required sizes and long localized strings | No clipped essential content or invisible confirmation action | Does not prove every system container size |
| Reduced transparency or contrast | Test accessibility display settings | Content and state remain legible without relying on glass | Does not prove the OS’s outer treatment |
| Reduce Motion | Test action and re-render states | No essential meaning depends on animation | Does not prove frame pacing |
| Localization | Test expansion, pluralization, RTL, and voice dialog | Labels, summaries, and layout remain understandable | Does not prove every supported locale |
| Error recovery | Force permission, store, model, network, and target failures | Failure preserves prior truth and offers retry/manual/app path | Does not prove server-side recovery |
| Release artifact | Archive/export and inspect app, extension, entitlements, privacy manifest, and metadata | Intended targets and capabilities are in the signed artifact | Upload success is not feature proof |

## Test case templates

### Static and interactive render

Record:

- device, OS, Xcode, and SDK;
- intent identifier and target;
- account/authentication state;
- input fixture and expected projection;
- invocation surface;
- screenshot or result bundle;
- whether the app was running, terminated, locked, or backgrounded;
- actual snippet state and dismissal behavior.

### Follow-up mutation

Record:

- starting durable state;
- snippet snapshot state;
- action intent and parameter;
- authorization/version check;
- mutation result;
- duplicate/retry result;
- second SnippetIntent render;
- error state if the write did not commit.

### Confirmation and AI proposal

Record:

- original source IDs;
- proposal value and model/framework revision;
- typed validation result;
- snippet scope and consequence text;
- parameter changes made in the snippet;
- confirm/cancel path;
- final durable record;
- whether the result was accepted, edited, rejected, or unavailable.

## Artifacts to retain

- source URL and SDK availability note;
- compile fixture and build settings;
- Swift Testing or XCTest results;
- UI test screenshots or result bundle;
- signed archive and target/entitlement inspection;
- physical-device model, OS build, locale, and Apple Intelligence settings;
- privacy/accessibility test notes;
- invocation surface and exact phrase/action;
- known limitations and unsupported surfaces.

Do not retain private user content in a public knowledge-base artifact. Use synthetic identifiers and redacted screenshots.

## Release gate

The route is ready to describe as shipped only when:

- the signed target contains the intended AppIntent and SnippetIntent declarations;
- the intended process or extension target is verified;
- the privacy manifest and usage descriptions match the actual route;
- the main app and fallback path work when the system surface is unavailable;
- system invocation is proven on the supported physical device family;
- repeated render, confirmation, cancellation, stale, error, and account-change paths are tested;
- accessibility and localization runs cover the actual system surface;
- product copy does not promise universal Apple Intelligence, Siri, Spotlight, or system placement behavior;
- TestFlight or production evidence exists when the user-facing claim depends on delivery.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [Displaying static and interactive snippets](https://developer.apple.com/documentation/appintents/displaying-static-and-interactive-snippets)
- [SnippetIntent](https://developer.apple.com/documentation/appintents/snippetintent)
- [ShowsSnippetIntent](https://developer.apple.com/documentation/appintents/showssnippetintent)
- [ShowsSnippetView](https://developer.apple.com/documentation/appintents/showssnippetview)
- [SnippetIntent.reload()](https://developer.apple.com/documentation/appintents/snippetintent/reload%28%29)
- [IntentExecutionTargets](https://developer.apple.com/documentation/appintents/intentexecutiontargets)
- [Adopting App Intents to support system experiences](https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences)
- [App Intents updates](https://developer.apple.com/documentation/updates/appintents)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
