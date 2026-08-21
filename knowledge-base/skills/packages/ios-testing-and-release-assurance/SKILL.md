---
name: ios-testing-and-release-assurance
description: Design, implement, review, or audit native Apple app tests and release evidence across Swift Testing, XCTest, XCUIAutomation, accessibility, Liquid Glass, on-device AI evaluation, performance, physical devices, system surfaces, archives, and TestFlight. Use when an LLM or solo developer needs a precise evidence plan or must determine what a green test actually proves.
---

# iOS testing and release assurance

Route every claim to the smallest Apple-native evidence layer that can support
it. Coordinate deterministic Swift Testing, XCTest/XCUIAutomation, accessibility
tasks, AI evaluation, performance, device/system runs, and signed release
inspection. Never turn a compile, preview, simulator run, model output, archive,
or TestFlight upload into a universal production or App Review claim.

`claim -> target/configuration -> fixture -> deterministic test -> UI/system test -> device -> signed release -> remaining gap`

## Read before acting

- Inspect the actual Xcode project/workspace, targets, schemes, configurations,
  test plans, host applications, deployment targets, SDK, device families,
  extensions, entitlements, privacy manifests, usage descriptions, packages,
  fixtures, and existing test results.
- Read the [testing and release-assurance framework route](../../../42-framework-deep-dives/144-swiftui-testing-xctest-ui-device-release-assurance-route.md), [native-design and AI-evaluation design](../../../21-design-deep-dives/172-swiftui-testing-native-design-and-ai-evaluation.md), [capability route](../../../50-capability-recipes/175-swiftui-testing-xctest-ui-device-release-assurance-route.md), and [proof matrix](../../../60-verification/169-swiftui-testing-xctest-ui-device-release-assurance-proof-matrix.md).
- Load [test-matrix.md](references/test-matrix.md) for fixture, target, plan,
  evidence, device, and release routing; load [release-audit.md](references/release-audit.md)
  when the task reaches archive/TestFlight; load [evaluation-fixtures.md](references/evaluation-fixtures.md)
  when evaluating AI or the role bundle itself.
- Refresh the official Swift Testing, XCTest, XCUIAutomation, accessibility,
  Xcode test-plan, performance, release-build, and distribution pages listed in
  Sources before relying on a version-sensitive API or behavior.

## Role workflow

1. **State the claim.** Write the user-visible operation, consequence of
   failure, target, supported device family, and non-goals.
2. **Choose the evidence layer.** Use Swift Testing for direct Swift logic and
   async coordination; XCTest/XCUIAutomation for a running app, UI workflows,
   accessibility audits, and performance; a physical device or system host for
   hardware/assistive/system behavior; an archive/TestFlight build for signed
   user-like evidence.
3. **Build the fixture matrix.** Include empty, loading, partial, stale,
   denied, unavailable, canceled, interrupted, retry, conflict, migration,
   model-refusal, malformed-output, and commit states as applicable. Assign
   stable fixture IDs and reset policy.
4. **Make dependencies injectable.** Control time, randomness, networking,
   persistence, accounts, permissions, model availability, and system clients.
   Do not let live services leak into deterministic tests.
5. **Write the deterministic tests.** Prefer structs, independent fixtures,
   parameterized cases, `#require` for preconditions, `#expect` for behavior,
   async confirmation around owned work, tags, bounded time limits, and typed
   attachments with approved retention.
6. **Write UI tests only for user workflows.** Launch with explicit arguments,
   query semantic identifiers/roles/labels, wait for meaningful state, perform
   the action, and assert the next semantic state. Keep XCTest for UI testing;
   Swift Testing does not replace XCUIAutomation.
7. **Audit accessibility and native design.** Run automated audits on each
   critical screen, then run VoiceOver/alternate-input/Dynamic Type/contrast/
   reduced-motion/effects tasks on a named physical device. Test Liquid Glass
   grouping, fallback, focus, hit targets, and state changes rather than pixels.
8. **Evaluate generated intelligence.** Validate schema, source revision,
   allowed operations, privacy, refusal, cancellation, and idempotency before
   user review. Keep quality scoring and human calibration separate from
   deterministic validation.
9. **Run performance and system gates.** Fix the workload, baseline, device,
   OS, power/network/model state, test plan, and configuration. Record extension,
   widget, App Intent, notification, background, accessory, or account evidence
   at the owning system boundary.
10. **Audit the signed release.** Inspect archive target membership, bundle IDs,
    versions/builds, entitlements, privacy resources, usage descriptions,
    extensions, signing, and exact TestFlight build. Run fresh-install/update
    and recovery tasks, then state the remaining App Review/production gaps.

## Output contract

Return:

```text
# iOS testing and release-assurance handoff

Claim and consequence:
Target/scheme/test plan/configuration:
SDK/deployment/device/OS facts:
Fixture IDs and reset policy:
Swift Testing coverage:
XCTest/XCUI workflow:
Accessibility and Liquid Glass evidence:
AI evaluation evidence:
Performance/system/physical-device evidence:
Archive/TestFlight evidence:
Commands and artifacts:
What this proves:
What this does not prove:
Open gaps and next smallest gate:
```

Label evidence as source, target/static, compile, fixture/unit, simulator/UI,
physical/system, server/account, signed artifact, TestFlight/App Store, or
production. List skipped/excluded/known-issue tests as scope, not passes.

## Hard boundaries

- Do not use localized strings, element indexes, screenshots alone, or arbitrary
  sleeps as the primary UI contract when semantic state is available.
- Do not globally serialize Swift Testing to hide shared-state defects; isolate
  fixtures or name the narrow serialized resource.
- Do not report an accessibility audit as complete accessibility or a passing
  UI test as VoiceOver task success.
- Do not let model output call a network, write a record, trigger a system or
  paid action, or change permissions without deterministic validation and an
  explicit review/commit boundary.
- Do not retain private prompts, health/contact/media data, credentials, or
  unnecessary screenshots in test artifacts.
- Do not add entitlements, background modes, accounts, servers, telemetry, or
  test-only production behavior without a stated product need and authorization.
- Do not claim Apple approval, universal performance, physical behavior, or
  production readiness without the matching external evidence.

## Sources

- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Defining test functions](https://developer.apple.com/documentation/testing/definingtests)
- [Expectations and confirmations](https://developer.apple.com/documentation/testing/expectations)
- [TestScoping](https://developer.apple.com/documentation/testing/testscoping)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [XCUIAutomation](https://developer.apple.com/documentation/xcuiautomation)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [Performing accessibility audits for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
- [Writing and running performance tests](https://developer.apple.com/documentation/xcode/writing-and-running-performance-tests)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
