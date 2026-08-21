# Swift Package Manager, macro, and plugin proof matrix

## Purpose

Use this matrix to distinguish a valid manifest from a resolved graph, a package
build from an Xcode target build, generated code from correct code, and an archive
from a usable app/extension/system surface. Record the selected Xcode/Swift
toolchain, SDK, deployment targets, package tools version, package identity,
target/product graph, dependency revisions/checksums, schemes/configurations,
device, archive, and release artifact.

## Evidence levels

| Level | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| L0 source | Official Apple/Swift documentation and manifest/API ledger | Documented package/plugin/macro contract | This package graph |
| L1 manifest | Package.swift parses and package describe/dump output | Manifest syntax and declared graph | Xcode target linkage or runtime behavior |
| L2 package build | swift build/test/resolve and package tests | Selected package targets compile/test | App target membership, entitlements, device APIs |
| L3 Xcode compile | Named app/extension/test scheme and SDK compile | Package product integrates into that target | Archive resources/signing or system delivery |
| L4 artifact | Release archive, bundle/resources, Info.plist, privacy manifest, entitlements | Intended generated product contents | Physical UI, hardware, model availability, system host |
| L5 physical/system | Signed app/extension/device/system surface | Named runtime feature behavior | Every platform/device/release combination |
| L6 distribution | TestFlight/release artifact, App Store configuration, dependency record | Selected distribution boundary | Future dependency/OS behavior or App Review approval |

## Manifest and target rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| MAN-01 | Tools version is deliberate | Parse manifest with selected Swift toolchain | tools-version/Swift/Xcode record | Manifest API version is compatible with CI and Xcode |
| MAN-02 | Package platforms are explicit | Inspect Package.platforms and target conditions | Manifest/output | Declared platforms and minimums match consuming targets |
| MAN-03 | Products expose only intended modules | package describe/dump-package and import fixture | Product/target graph | Public products do not leak internal/test/tool modules |
| MAN-04 | Target dependencies are one-way | Graph dependency targets and imports | Dependency graph | No app-to-domain/UI cycle or accidental platform import |
| MAN-05 | Test code stays test-only | Build graph with test dependency inspection | Package graph/build log | XCTest/Swift Testing does not enter distributable product transitively |
| MAN-06 | Resources belong to the right target | Resource fixture and Bundle.module test | Bundle listing/test output | Missing/incorrect resources fail explicitly |
| MAN-07 | Platform conditions are truthful | Build supported/unsupported platform targets | Build matrix | Unsupported code is isolated or cleanly unavailable |
| MAN-08 | Tools/language settings are recorded | Manifest and compiler output | Toolchain record | No unexplained toolchain drift |

## Dependency and supply-chain rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| DEP-01 | Source dependency is trustworthy enough for use | Author/repository/license/platform review | Dependency record | Scope and provenance are documented |
| DEP-02 | Version requirement is intentional | Resolve version/range/branch/commit fixtures | Package.swift and resolution diff | Production uses the selected version policy |
| DEP-03 | Package.resolved is current | Resolve from clean checkout | File hash/graph output | CI and local graph agree |
| DEP-04 | Product selection is target-specific | App/widget/extension/test target inspection | Xcode target package-product matrix | Each target links only what it needs |
| DEP-05 | Binary dependency matches checksum | Clean resolve/download and checksum check | Artifact/checksum record | Artifact bytes match declared checksum |
| DEP-06 | Binary supports the target | Archive/device/simulator link matrix | Slices/link logs | Intended destinations link and run |
| DEP-07 | Dependency change is reviewable | Compare resolved graph and generated/API changes | Diff/approval record | New transitive packages and licenses are known |
| DEP-08 | Runtime failure is handled | Missing/incompatible package resource or adapter | UI/log/error fixture | Package failure becomes a recoverable app state |

## Macro rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| MAC-01 | Declaration and implementation are separate | Inspect regular and macro targets | Manifest/import/build graph | Client imports public macro API, not implementation internals |
| MAC-02 | Roles match generated declarations | Positive/negative expansion fixtures | Compiler diagnostics/generated diff | Macro rejects unsupported attachment and emits intended code |
| MAC-03 | SwiftSyntax/toolchain is compatible | Clean macro build with selected toolchain | Build log/resolution | No hidden version mismatch |
| MAC-04 | Expansion is additive and typed | Generated-source inspection and compile | Expansion fixtures | Generated symbols/type checks match contract |
| MAC-05 | Generated API is available | iOS version/platform compile matrix | Diagnostics/API ledger | Generated code does not bypass availability |
| MAC-06 | Macro has no runtime side effect | Inspect implementation and client tests | Source review/test | No network, secret, permission, or domain mutation at compile time |
| MAC-07 | Accessibility metadata is valid | VoiceOver/Dynamic Type fixture using generated API | UI/device evidence | Generated labels/traits preserve semantics |
| MAC-08 | Macro failure is recoverable | Invalid syntax/argument/SDK fixture | Compiler/UI failure result | Build failure is actionable; no stale generated artifact ships |

## Plugin rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| PLG-01 | Plugin role is correct | Build-tool versus command use-case review | Manifest/plugin record | Build graph work is not hidden in a command plugin and vice versa |
| PLG-02 | Build command inputs/outputs are declared | Change, remove, and add input fixtures | Plugin command graph/log | Incremental rebuilds are correct |
| PLG-03 | Prebuild use is justified | Run unchanged and changed builds | Timing/output record | Unknown outputs are cached by the tool; repeated work is bounded |
| PLG-04 | Tool dependency is available | Clean build/tool lookup | Tool path/build log | Tool is built/available for host invocation |
| PLG-05 | Plugin stays in its sandbox | Attempt network/arbitrary write in a controlled fixture | Permission/diagnostic record | Denials are expected and documented |
| PLG-06 | Command write permission is explicit | Dry run, denied write, approved write | CI/user prompt/log | Package source is not modified without approval |
| PLG-07 | Generated output is target-owned | Build target and inspect generated directory | File/bundle record | Only intended generated Swift/resources enter the product |
| PLG-08 | Xcode/CLI differences are known | Invoke plugin through SwiftPM and Xcode | Separate logs/results | Project-aware behavior is not assumed in CLI mode |

## Xcode and artifact rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| XCO-01 | Package is attached to the right project | Inspect project package dependency | Xcode project record | Correct package identity/revision is present |
| XCO-02 | Product is attached to each required target | Build app/widget/extension/test schemes | Target settings/build log | No target relies on accidental transitive linkage |
| XCO-03 | Package resources ship | Inspect app/extension/archive bundles | Bundle path/listing | Expected resource is present in intended product |
| XCO-04 | Privacy manifest is included | Inspect archive privacy resources | Archive record | Required-reason/API declarations belong to the shipping target |
| XCO-05 | Build configuration is known | Debug/Release/evaluation scheme matrix | Settings/xcconfig record | Selected scheme uses intended package/configuration inputs |
| XCO-06 | Generated code ships when expected | Clean archive with plugin/macro | Archive/source symbol inspection | No generated source exists only in a local DerivedData cache |
| XCO-07 | Archive includes correct target graph | Archive and export inspection | Embedded bundle/entitlement record | App/extension/package resources match release plan |
| XCO-08 | Failure is not masked | Delete package/cache and rebuild | Clean-build log | Build does not silently use stale generated or resolved content |

## Liquid Glass and AI rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| UI-01 | Design package preserves semantic hierarchy | Render content, navigation, action, empty, error states | Preview/UI/device evidence | Glass groups only functional controls |
| UI-02 | Fallbacks work | Older deployment/Reduced Transparency/increased contrast/Reduce Motion | Device/settings matrix | Meaning and controls remain usable |
| UI-03 | System surfaces remain native | Widget/control/Live Activity/App Intent host runs | Physical/system evidence | Package does not imitate a system-owned shell |
| AI-01 | AI adapter is target-safe | Build app/extension/domain/test combinations | Import/target matrix | Device AI imports do not leak into unsupported targets |
| AI-02 | Proposal contract is typed | Valid/stale/invalid/unavailable fixtures | Proposal/rejection tests | Domain validator owns truth and revision checks |
| AI-03 | Privacy scope is explicit | Prompt/log/cache/resource review | Redacted artifacts | Private input is not embedded in generated code or package logs |
| AI-04 | AI fallback is usable | Model unavailable, canceled, low-memory, wrong language/device | Device/UI trace | Local deterministic path remains useful |
| AI-05 | Macro/plugin does not own AI side effects | Source/build review | Architecture record | Build-time tooling never sends user data or mutates domain state |

## Accessibility and release rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| A11Y-01 | Package controls have labels/traits/actions | VoiceOver traversal of a consuming app | Device recording/tree | Generated/reusable components are semantic |
| A11Y-02 | Text/layout adapts | Largest Dynamic Type, localization, RTL, long content | Device screenshots/UI tests | No clipped/reordered critical controls |
| A11Y-03 | Alternate input works | Voice Control, Switch Control, keyboard/pointer | Device run | Core package surfaces are operable |
| REL-01 | Release graph is reproducible | Clean checkout, resolve, archive | Package.resolved and archive record | Same intended revisions/checksums |
| REL-02 | Release target membership is correct | Inspect final app/extension/archive | Entitlements/bundle/build record | No test/tool/macro implementation artifact ships accidentally |
| REL-03 | Release dependency policy is reviewed | License/provenance/binary/privacy review | Approval record | External packages meet product/release policy |
| REL-04 | TestFlight artifact works | Install/update/launch selected feature | Physical device trace | Package resources/generated code/linkage work in distribution |
| REL-05 | Store/system review metadata is aligned | Privacy, capabilities, extension, AI copy review | Release checklist | Package composition does not hide a disallowed behavior |
| REL-06 | Evidence names exact target | Repeat claim from build/device/release report | Evidence packet | No generic “package works” claim |

## Test matrix

Run:

- swift package describe, dump-package, show-dependencies, and tests from a clean
  checkout;
- package resolution with the selected toolchain and Package.resolved;
- source dependency update, rollback, and conflict fixtures;
- binary checksum, architecture, simulator, device, and Release archive checks;
- resource present/missing/corrupt/localized fixtures;
- supported and unsupported platform target builds;
- macro positive/negative expansion and generated API tests;
- build plugin changed-input/no-input/failed-tool/output cleanup tests;
- command plugin dry-run/denied-write/approved-write and CI invocation;
- Xcode app/widget/extension/test target schemes;
- clean DerivedData/archive inspection;
- Liquid Glass accessibility settings and system-surface hosts;
- on-device AI unavailable/canceled/stale/approved proposal cases;
- VoiceOver, Voice Control, Switch Control, Dynamic Type, RTL, reduced effects,
  and keyboard/pointer routes;
- Debug, Release, TestFlight, and final distribution artifacts.

## Stop conditions

Stop and fix when:

- a package target imports an app target or creates a dependency cycle;
- a test or macro implementation target enters the shipping product;
- a binary dependency has no checksum/provenance/platform review;
- Package.resolved changes are accepted without dependency review;
- a plugin writes source or uses the network without explicit permission;
- generated outputs are undeclared, stale, or unowned;
- a macro hides a runtime side effect or private input;
- a package uses a newer API than its target/deployment declaration supports;
- a widget/extension assumes the app process or full design shell is alive;
- Liquid Glass is applied as a universal background or system UI is imitated;
- AI output bypasses a typed proposal, validation, review, or fallback path;
- a package build is reported as app/archive/device proof;
- Debug success is used to claim Release/TestFlight readiness.

## Sources

- [Swift packages](https://developer.apple.com/documentation/xcode/swift-packages)
- [Adding package dependencies to your app](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
- [Identifying binary dependencies](https://developer.apple.com/documentation/xcode/identifying-binary-dependencies)
- [PackageDescription](https://docs.swift.org/swiftpm/documentation/packagedescription/)
- [Package](https://docs.swift.org/swiftpm/documentation/packagedescription/package/)
- [Target](https://docs.swift.org/swiftpm/documentation/packagedescription/target/)
- [Target dependencies](https://docs.swift.org/swiftpm/documentation/packagedescription/target/dependencies/)
- [Target type](https://docs.swift.org/swiftpm/documentation/packagedescription/target/targettype/)
- [Introducing Packages](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/introducingpackages/)
- [Adding dependencies to a Swift package](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/addingdependencies/)
- [Macros](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/macros/)
- [PackagePlugin](https://docs.swift.org/swiftpm/documentation/packageplugin/)
- [Plugins](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/plugins/)
- [Writing a build tool plugin](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/writingbuildtoolplugin/)
- [Writing a command plugin](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/writingcommandplugin/)
- [Enable a build plugin](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/enablebuildplugin/)
- [Enable a command plugin](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/enablecommandplugin/)
- [Swift package commands](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/swiftpackagecommands/)
- [Customizing the build schemes for a project](https://developer.apple.com/documentation/xcode/customizing-the-build-schemes-for-a-project)
- [Adding a build configuration file to your project](https://developer.apple.com/documentation/xcode/adding-a-build-configuration-file-to-your-project)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
