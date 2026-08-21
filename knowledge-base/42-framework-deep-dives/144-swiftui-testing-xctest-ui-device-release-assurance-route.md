# SwiftUI testing, XCTest UI, device, and release-assurance route

Testing an Apple-native app is a chain of evidence, not a single green
command. Swift Testing is the preferred modern route for deterministic Swift
logic and async coordination. XCTest and XCUIAutomation remain the route for a
running app, UI workflows, accessibility audits, and performance tests. Xcode
test plans, physical devices, signed Release archives, and TestFlight add
separate evidence layers.

Use the companion pages for implementation work:

- [testable native design and AI evaluation](../21-design-deep-dives/172-swiftui-testing-native-design-and-ai-evaluation.md)
- [testing and release-assurance capability route](../50-capability-recipes/175-swiftui-testing-xctest-ui-device-release-assurance-route.md)
- [testing and release-assurance proof matrix](../60-verification/169-swiftui-testing-xctest-ui-device-release-assurance-proof-matrix.md)
- [testing and release-assurance recipes](../70-code-recipes/187-swiftui-testing-xctest-ui-device-release-assurance-recipes.md)

This page targets the installed Xcode 26.4 / Swift 6.3 toolchain as an API
shape reference. Verify the project’s final SDK, deployment target, device
family, entitlement set, localization configuration, and test-host setup
before making a product claim.

## 1. Keep the claim attached to its evidence layer

Start with the sentence the team wants to be able to say, then route it to the
smallest evidence that can actually support it.

| Claim | Strong first evidence | What it still does not prove |
| --- | --- | --- |
| A reducer maps an input to a state | Swift Testing fixture with explicit expectations | SwiftUI focus, system delivery, or hardware behavior |
| An actor/repository handles async cancellation | Async test with injected clock/service and bounded event confirmation | Real network, account, sensor, or CloudKit availability |
| A person can complete a critical task | XCTest UI workflow on a named target with deterministic launch state | Full accessibility, physical performance, or App Store approval |
| The interface exposes a meaningful accessibility tree | Semantic identifiers, XCUI queries, and automated audit | VoiceOver task success, alternate input, or human usability |
| A Liquid Glass state is legible and responsive | State matrix, UI workflow, accessibility settings, and physical review | Universal device performance or system-owned surfaces |
| An on-device AI result is safe to use | Versioned fixture, schema/grounding validators, quality criteria, and human review | General model quality, future model versions, or automatic correctness |
| A release build behaves like a user build | Release archive, install/run evidence, migration and permission checks, TestFlight run | Approval or behavior on every device and region |

The most common failure is promoting an observation from one row into another:
a preview becomes an accessibility claim, a unit test becomes a device claim, a
model output becomes domain truth, or an archive becomes a shipped app. Preserve
the claim/evidence pair in the handoff record.

## 2. Swift Testing owns deterministic Swift behavior

The `Testing` framework defines test functions and suites with `@Test`,
expectations through `#expect` and `#require`, parameterized cases, traits,
tags, time limits, and asynchronous confirmations. Test types do not need to
subclass `XCTestCase`; structs with no-argument initialization are a natural
default.

Use it for:

- reducers, parsers, validators, route selection, and domain policies;
- typed AI proposal validation, source-revision matching, and idempotency;
- persistence policy with an injected model adapter or temporary store;
- actor/repository behavior with controlled dependencies;
- async streams, cancellation, retry, and recovery state;
- state matrices for authorization, model readiness, sync, migration, and
  system-surface availability.

### Concurrency is part of the test contract

Swift Testing runs tests and parameterized cases with concurrency in mind. A
test must own its fixture and be order-independent. Prefer separate temporary
stores, injected clocks, deterministic random sources, fake network/services,
and actor-owned state. Apply `.serialized` only to a parameterized test or
suite that truly shares a resource; using serialization to hide a race weakens
the evidence.

`confirmation(expectedCount:)` is for an asynchronous event that cannot be
checked as a returned value. Place the confirmation around the operation that
can emit the event, await the task or sequence to finish, and test zero-event
behavior for cancellation, authorization loss, and teardown. A longer timeout
is not a lifecycle fix.

Use `.timeLimit(.minutes(...))` as an upper bound for a test that can stall.
Record why the bound exists and whether a timeout means a product failure,
expected unavailability, or an excluded service environment.

### Availability and modern traits

Put `@available(iOS 26.0, *)` on each test that needs iOS 26 behavior; do not
assume the test suite’s availability annotation will express the correct test
runner behavior. Tags communicate evidence classes such as `unit`,
`integration`, `ui`, `accessibility`, `device`, `aiEvaluation`, and `release`.
Test scoping traits can install task-local fixture configuration without
sharing mutable global state.

Attachments are useful for fixture IDs, sanitized state snapshots, validator
diagnostics, and result metadata. They must obey the test target’s privacy and
retention policy. Do not attach raw personal content merely because a report
supports attachments.

## 3. XCTest remains the UI and performance boundary

Swift Testing does not perform UI tests. Use XCTest with XCUIApplication,
XCUIElement, and XCUIElementQuery to launch and drive the app. Keep UI tests in
a UI test target with the correct host application, signing, bundle
identifiers, target membership, and scheme/test-plan membership.

### Semantic UI workflow

Every critical UI workflow should have a deterministic launch contract:

1. launch with a fixture ID and explicit reset/offline/account/model flags;
2. find the screen and controls by stable accessibility identifiers and
   meaningful roles/labels;
3. wait for a semantic state with a bounded timeout;
4. perform the user action;
5. assert the resulting label, value, enabled state, selection, focus, or
   domain-visible screen state;
6. record the target, OS, locale, orientation, fixture, and result bundle.

`waitForExistence` is synchronization, not proof that the element is the right
element. Avoid indices, fragile hierarchy selectors, and localized strings when
the test is not specifically a localization test. Test localization as its
own configuration with localized labels and dates.

The application should own the fixture contract. Launch arguments can select a
seeded local state, reset a store, disable live networking, select a model
availability mode, or open a deep link. Never put secrets or real personal
data in a UI test fixture.

### Accessibility audits are a supporting layer

`performAccessibilityAudit(for:)` can detect common issues on the current
screen, such as missing descriptions, clipping, contrast, and related
problems. Run it across the important workflow screens and preserve the audit
record. Then perform the actual task with VoiceOver and relevant settings:
Dynamic Type, increased contrast, reduced motion, reduced transparency/effects,
Voice Control, Switch Control, keyboard, pointer, and localization where
supported.

An accessibility identifier makes automation possible; it does not prove the
label, role, value, hint, order, focus movement, action feedback, or task
completion is usable. Accessibility Inspector’s audit is a diagnostic and
regression aid, not a universal accessibility certification.

## 4. Test native and Liquid Glass state, not just pixels

Liquid Glass is a system material and interaction language. A screenshot can
show a plausible surface while the real interaction, accessibility, contrast,
focus, Dynamic Type, or reduced-effects behavior is broken.

For every glass-bearing surface, include a state matrix with:

| State | Native review question |
| --- | --- |
| idle | Is the glass grouping necessary, and does the primary action remain obvious? |
| loading | Does progress have a semantic label and cancellation/retry path? |
| ready | Does content remain legible over the current background and color scheme? |
| error | Does the error avoid transparency and decorative motion that compete with recovery? |
| reduced transparency/effects | Is there a solid or simpler fallback with the same actions? |
| large text/VoiceOver | Are hierarchy, focus, labels, values, and actions still complete? |
| keyboard/pointer | Are focus rings, hover, hit targets, and commands coherent? |
| system handoff | Is the app using the system surface rather than imitating it? |

Test the state model and semantic actions with Swift Testing, the critical
workflow with XCTest, and the physical legibility/performance with a named
device. Do not use a visual snapshot as the only proof of a glass design, and
do not place decorative glass over every control or recreate Control Center,
Lock Screen, system pickers, or other Apple-owned surfaces.

## 5. Test on-device AI as a versioned proposal system

An on-device model can be unavailable, loading, interrupted, constrained by
context, refused, or changed by an OS/model revision. Treat generated output as
versioned data with a source revision, schema/profile version, and explicit
review requirement.

The deterministic test layer should verify:

- output decodes into the expected `Codable` type;
- source IDs and revisions still match the current user-approved input;
- fields stay within the allowed enum/range/length constraints;
- no unsupported system action, network call, or paid side effect is encoded;
- the proposal is idempotent or carries a deliberate conflict policy;
- refusal, malformed output, timeout, unavailable model, and cancellation map to
  visible fallback states.

The quality layer should use a versioned fixture set, objective criteria where
possible, calibrated human review for semantic quality, and a regression
record. A model-generated description is not ground truth because it passed a
schema validator. The commit path needs its own domain/UI/system tests and
must require user acceptance where the action has material consequences.

## 6. Test plans stage the feedback loop

An Xcode test plan controls which tests run and which configurations are used.
Use more than one plan when the project has meaningful differences in speed,
device, accessibility, performance, AI evaluation, or release risk.

| Plan | Typical contents | Decision |
| --- | --- | --- |
| Fast | Pure unit and small fixture tests | Continue local iteration |
| Feature | Affected unit/integration and critical UI | Accept feature branch |
| NativeDesign | UI, accessibility audit/task, Dynamic Type, reduced effects, localization | Approve native interaction/design |
| Performance | Metric tests, fixed workload, Release configuration | Investigate regression |
| AIEvaluation | Versioned data, validators, quality criteria, human sample | Accept model/prompt revision |
| ReleaseCandidate | Selected full suite, migrations, extensions, system workflows | Allow signed release evidence |

Record the plan name, configuration, destination, SDK, OS, environment, test
selection/exclusions, and `.xcresult` bundle. An excluded test is scope that
was not run, not a passing test. On the command line, name the scheme and plan
explicitly; a green command can still be the wrong plan.

Useful command shapes include:

```text
xcodebuild -scheme App -showTestPlans
xcodebuild test -scheme App -testPlan Fast
xcodebuild test -scheme App -testPlan ReleaseCandidate -destination 'platform=iOS Simulator,name=iPhone'
```

Adapt the destination, signing, and project arguments to the real workspace.
The command shape does not prove a test target was built, a device was
available, or a service/system surface delivered.

## 7. Performance needs a controlled baseline

XCTest performance tests can measure clock, CPU, memory, storage, launch, and
other metrics. Choose a metric that matches the user risk, fix the workload and
dataset, and capture the device, OS, build configuration, power state, network
state, and model state.

Performance plans should use a Release build for realistic behavior, avoid the
debugger when its presence changes watchdog/suspension behavior, and use
Instruments or signposts when a metric alone cannot identify the regression.
One passing run is a measurement, not universal device compatibility.

For glass-heavy screens, test scrolling, transitions, large data sets, reduced
effects, Dynamic Type, and the supported device range. For capture/model routes,
include memory pressure, cancellation, thermal/power state, and the actual
device class that carries the product claim.

## 8. Release assurance is a separate packet

Apple’s release-build guidance distinguishes Debug behavior from the user
environment. A release assurance packet should include:

- the intended target, bundle ID, version/build, SDK, deployment target,
  architectures, capabilities, entitlements, privacy manifests, and usage
  descriptions;
- the archive path and UUID, signing/distribution method, embedded extensions,
  resources, and verified Info.plist values;
- a fresh install run and an update from the prior build, including migration,
  keychain/App Group, account, permission, and offline/recovery paths;
- physical-device evidence for any camera, microphone, haptic, sensor, model,
  accessory, background, audio, or performance claim;
- TestFlight install/launch/task evidence for the exact uploaded build;
- known exclusions, unresolved issues, and the next required proof.

The archive can be validated and uploaded without proving that a real user
completed the workflows. TestFlight distribution is stronger release evidence
than a local debug run but is still not App Review approval or universal
production proof.

## 9. Handoff into the agentic engineering-team bundle

The open-source skill bundle should route work through roles with explicit
artifacts:

| Role | Handoff artifact |
| --- | --- |
| architect | claim/evidence map, target matrix, risk and capability route |
| native designer | state matrix, semantic UI contract, Liquid Glass fallback and accessibility tasks |
| implementer | injected seams, fixture IDs, cancellation/recovery, source links |
| test engineer | Swift Testing/XCTest targets, test plan, result bundle, exclusions |
| AI evaluator | dataset/provenance, schema/grounding validators, quality score, human sample |
| device/system verifier | named device/OS/settings, physical/system-surface run, logs/screenshots |
| release auditor | archive/entitlement/privacy/version/TestFlight packet and open gaps |
| source maintainer | official URL/API refresh, availability changes, SDK re-check |

Each handoff must state what it proves and what it does not. The bundle can
make an LLM more precise and coordinate a solo developer across these roles; it
cannot guarantee Apple approval, hardware behavior, or production correctness
without the corresponding evidence.

## Sources

- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Defining test functions](https://developer.apple.com/documentation/testing/definingtests)
- [Test](https://developer.apple.com/documentation/testing/test)
- [Expectations and confirmations](https://developer.apple.com/documentation/testing/expectations)
- [TestScoping](https://developer.apple.com/documentation/testing/testscoping)
- [Attachment](https://developer.apple.com/documentation/testing/attachment)
- [Limiting the running time of tests](https://developer.apple.com/documentation/testing/limitingexecutiontime)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [XCUIAutomation](https://developer.apple.com/documentation/xcuiautomation)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [XCUIElement](https://developer.apple.com/documentation/xcuiautomation/xcuielement)
- [XCUIElementQuery](https://developer.apple.com/documentation/xcuiautomation/xcuielementquery)
- [Performing accessibility audits for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
- [Writing and running performance tests](https://developer.apple.com/documentation/xcode/writing-and-running-performance-tests)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
