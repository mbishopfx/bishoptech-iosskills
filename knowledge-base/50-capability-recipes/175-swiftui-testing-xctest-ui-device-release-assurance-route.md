# SwiftUI testing, XCTest UI, device, and release-assurance capability route

Use this route when a feature must move from a polished SwiftUI/Liquid Glass
screen to a defensible engineering and release decision. It coordinates Swift
Testing, XCTest UI, accessibility, AI evaluation, performance, physical-device,
archive, and TestFlight evidence without pretending they are interchangeable.

Read the [framework deep dive](../42-framework-deep-dives/144-swiftui-testing-xctest-ui-device-release-assurance-route.md), [native-design contract](../21-design-deep-dives/172-swiftui-testing-native-design-and-ai-evaluation.md), [proof matrix](../60-verification/169-swiftui-testing-xctest-ui-device-release-assurance-proof-matrix.md), and [recipes](../70-code-recipes/187-swiftui-testing-xctest-ui-device-release-assurance-recipes.md) first.

## Outcome contract

Write the capability as a user outcome with evidence boundaries:

    A person can open the seeded review, inspect the current and generated
    values, reject or edit the proposal, save the record, and recover clearly
    if the model, network, permission, account, or system surface is unavailable.

Then identify the claims that must be proven:

| Claim | Route owner |
| --- | --- |
| state/reducer/policy is correct | Swift Testing |
| actor/repository/cancellation is correct | Swift Testing async/integration |
| a critical task works through the app | XCTest/XCUIAutomation |
| accessibility is usable | automated audit plus physical task |
| AI output is admissible | typed validator plus versioned evaluation |
| performance meets a defined baseline | XCTest metrics/Instruments |
| camera/audio/sensor/model/extension/system behavior works | named physical/system run |
| signed user build behaves correctly | Release archive and TestFlight |

## Step 1: audit the target before writing a test

Record:

- app, framework, package, UI-test, performance, and extension targets;
- scheme and active/default test plans;
- host application, test host, bundle IDs, signing, entitlements, privacy
  manifests, usage descriptions, and target membership;
- deployment target, SDK, device family, architecture, OS/device availability;
- debug versus Release configuration differences;
- local stores, App Groups, Keychain, accounts, model assets, permissions,
  network, and system-surface dependencies.

Do not create an assertion for a route that the target cannot build or run. A
test target with the wrong host or entitlement can be green for the wrong reason.

## Step 2: create the fixture matrix

Give each meaningful state a stable ID and keep the fixture small enough to
understand. At minimum include:

- first launch and empty state;
- ready state with a source revision;
- loading, cancellation, timeout, and retry;
- denied, restricted, revoked, and unavailable permission;
- offline, stale, server error, account transition, and conflict;
- model preparing, unavailable, refusal, malformed output, context limit, and
  accepted/rejected proposal;
- large text, reduced motion, reduced transparency/effects, high contrast,
  VoiceOver, keyboard/pointer, and localization variants;
- extension/system-surface delayed, unavailable, duplicate, or stale delivery;
- migration from prior data and fresh install/update behavior.

Use the ID in Swift Testing arguments, UI launch arguments, generated report
names, AI evaluation rows, and proof-matrix evidence. This is the shared
language between the architect, designer, implementer, tester, auditor, and
LLM skill router.

## Step 3: implement the deterministic core first

Test one behavior per test where practical:

1. construct a fixture with no hidden global state;
2. run the reducer, parser, validator, or policy;
3. use `#require` for preconditions and `#expect` for outcomes;
4. assert forbidden side effects did not occur;
5. run boundary and invalid-input cases;
6. add parameterized cases when each case can be diagnosed independently.

For async code, inject the service, clock, store, or model provider. Await
structured work fully. Use confirmation for events and test cancellation with
an expected event count of zero when appropriate.

## Step 4: separate Swift Testing from XCTest

| Tool | Use it for | Avoid claiming |
| --- | --- | --- |
| Swift Testing | direct Swift logic, async coordination, typed validators, state matrices | UI or hardware behavior |
| XCTest | legacy tests, integration seams, UI tests, accessibility audit, performance metrics | universal device or accessibility success |
| XCUIAutomation | user-like app launch, queries, gestures, semantic workflow | domain correctness without a domain assertion |
| Accessibility Inspector | common audit diagnostics and settings | complete assistive-technology usability |
| physical device | hardware, system surfaces, sensors, performance, assistive tasks | every supported device unless tested |
| archive/TestFlight | signed user-like build and distribution handoff | App Store approval or all production conditions |

Both testing frameworks can coexist. Keep the purpose of each target obvious
and do not migrate existing XCTest merely to make the code look modern unless
the project has chosen that migration.

## Step 5: build the UI workflow contract

The app should support a deterministic launch contract such as:

| Input | Purpose |
| --- | --- |
| `-fixtureID <id>` | seed a known domain state |
| `-resetStore YES` | remove test data before launch |
| `-networkMode offline` | force a fallback path |
| `-modelMode unavailable` | test model fallback |
| `-accessibilityMode reducedEffects` | test native fallback |
| deep-link argument | test cold/warm route delivery |

The UI test should query semantic identifiers and assert label/value/role,
enabled state, focus, and resulting state. Do not query by index because a
sorting or loading change can silently target a different element.

## Step 6: make Liquid Glass a regression surface

For glass-bearing screens, add a NativeDesign plan that runs the critical UI
workflow under large text, dark/light appearance, high contrast, reduced motion,
reduced transparency/effects, and localization configurations. Record which
groups are functional and which are decorative.

A screenshot may support a visual review, but it cannot prove hit targets,
focus, labels, accessibility, animation timing, memory, or system-owned surface
behavior. Use semantic UI evidence and physical review for those claims.

## Step 7: evaluate on-device AI without letting it commit

The AI evaluation fixture should include:

- source input and provenance policy;
- source revision and expected schema/profile version;
- proposed fields and allowed operations;
- unavailable/refusal/malformed/timeout outputs;
- deterministic validators and forbidden-side-effect checks;
- quality criteria, score rubric, human-review sample, and regression threshold.

The proposal path ends at a reviewable value. A separate domain/UI test proves
Accept/Edit/Reject and commit idempotency. Use the current source revision to
prevent stale proposals from mutating newer user data.

## Step 8: add performance and device gates

Define a workload and baseline for launch, parsing, migration, rendering,
scrolling/hitches, capture, model handoff, storage, or synchronization. Run
performance plans with the intended Release configuration and record device,
OS, power, network, model, dataset, and build.

For physical/system routes, list exact evidence:

- device model and OS build;
- permissions, account, accessories, and settings;
- input/output route or system host;
- app version/build and target;
- event/action/result logs;
- screenshots/video only where they add diagnostic value;
- teardown/recovery and repeat count.

“Works on simulator” and “archive exists” are not substitutes for this packet.

## Step 9: stage test plans and CI commands

Use explicit plans such as `Fast`, `Feature`, `NativeDesign`, `Performance`,
`AIEvaluation`, and `ReleaseCandidate`. Name the plan in local and CI commands,
and retain the `.xcresult` output.

Before accepting a green result, check:

- the intended plan actually ran;
- skipped/disabled/known-issue tests are recorded as scope;
- destination and configuration match the claim;
- test host and extensions were built;
- fixtures were reset and no live network/account leaked into deterministic
  tests;
- failures were not masked by a broad timeout or suite serialization.

## Step 10: assemble release evidence

The release gate should inspect the archive and run the exact uploaded build:

1. verify bundle IDs, version/build, target families, embedded extensions,
   entitlements, privacy manifests, usage descriptions, resources, and signing;
2. run fresh install and update scenarios with prior data;
3. exercise permission/account/offline/migration/recovery paths;
4. install the TestFlight build on a named physical device;
5. repeat the critical user task and record the actual result;
6. list open issues, exclusions, and claims that still require App Review or
   production observation.

TestFlight is a distribution/evidence layer. It does not promise approval or
prove every hardware, region, account, system, or production condition.

## Agentic skill-bundle output

The route should produce portable artifacts for the future open-source bundle:

- `claim-map.md`: each product claim and required evidence level;
- `fixture-matrix.md`: stable states, IDs, inputs, and reset policy;
- `test-plan-map.md`: targets, plans, tags, configurations, and exclusions;
- `ai-evaluation-record.md`: dataset, schema/profile, criteria, scores, review;
- `device-run.md`: named device/system settings and actual observations;
- `release-audit.md`: archive, signing, entitlements, TestFlight, and gaps.

An LLM can use these artifacts to route work to architect, native designer,
implementer, test engineer, AI evaluator, device verifier, release auditor, and
source maintainer. The bundle should refuse to collapse these artifacts into a
single “passed” claim.

## Stop conditions

Stop and correct the route when:

- the wrong test plan ran or the claimed behavior was excluded;
- a UI test uses an index or localized string where a semantic contract exists;
- a timeout or global serialization hides a lifecycle/race defect;
- an accessibility audit is reported as complete accessibility proof;
- a model output has no source revision, schema validator, or human-review path;
- a simulator, debug run, or archive is reported as physical/release evidence;
- the uploaded build was not checked against the archive and target matrix.

## Sources

- [Xcode testing](https://developer.apple.com/documentation/xcode/testing)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Defining test functions](https://developer.apple.com/documentation/testing/definingtests)
- [Expectations and confirmations](https://developer.apple.com/documentation/testing/expectations)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [XCUIElementQuery](https://developer.apple.com/documentation/xcuiautomation/xcuielementquery)
- [Performing accessibility audits for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
- [Writing and running performance tests](https://developer.apple.com/documentation/xcode/writing-and-running-performance-tests)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
