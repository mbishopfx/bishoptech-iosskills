# Role routing for the Apple engineering team skill

Use this map to select the smallest specialist set. A role is a reasoning pass,
not permission to make unrelated edits. Keep one implementation writer active.

| User signal | Lead role | Read first | Required handoff |
| --- | --- | --- | --- |
| “Build an app/feature” | Intake + route architect | knowledge-base map, capability atlas, relevant deep dive | outcome, route, state, configuration, proof plan |
| “Make it feel native/Liquid Glass” | Native designer + design verifier | SwiftUI design routes, Liquid Glass routes, HIG | hierarchy, native components, glass boundary, adaptation/a11y fixtures |
| “Add Apple Intelligence/on-device AI” | AI evaluator | AI lifecycle/evaluation routes, Foundation Models/Core ML/Vision route | availability, typed output, privacy, model eval, fallback, human review |
| “Debug/implement SwiftUI” | Implementer + test lead | target/project state, SwiftUI route, current SDK headers | minimal patch, test matrix, lifecycle/cancellation proof |
| “Audit security/privacy/release” | Security/privacy + device/release auditors | security, privacy, testing, archive/release routes | finding severity, evidence, remediation, residual gap |
| “Use HealthKit/Contacts/HomeKit/accessory/media” | Capability specialist | matching framework deep dive and availability matrix | permissions, entitlements, lifecycle, source/device proof |
| “Ship or prepare App Store build” | Project architect + release auditor | Xcode/archive/TestFlight/release routes | signed artifact inspection, device/system evidence, metadata gaps |

## Handoff packet

Each role receives:

- user outcome and non-goals;
- current target/SDK/device/build facts;
- files it may inspect or change;
- source pages and source revision;
- prior role findings and unresolved questions;
- verification commands and stop conditions.

Each role returns:

- decision and alternatives rejected;
- source links for version-sensitive claims;
- exact files or no-write recommendation;
- tests/audits run and results;
- evidence level of every important claim;
- remaining blocker or next smallest action.

## Safe sequencing

Use parallel read-only work for source collection, UI fixture review, and test
inventory. Sequence route selection before implementation, implementation
before behavior tests, and behavior tests before release claims. Security,
privacy, accessibility, and device/release audits may begin from the plan but
must re-check the final changed files and signed artifact.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
