# Swift Package Manager, macro, and plugin capability route

## Capability contract

Use this route when an iOS app needs shared modules, reusable UI, platform
adapters, on-device AI contracts, generated code, source generation, formatting,
documentation, or dependency isolation.

The route should produce:

1. a package graph with deliberate products and targets;
2. an explicit platform/deployment and resource policy;
3. Xcode app/extension/test target integration;
4. resolved dependency and binary trust records;
5. macro declaration/implementation separation where macros are justified;
6. build-tool or command plugin inputs/outputs and permission policy;
7. target-safe Liquid Glass and on-device AI modules;
8. package, target, archive, accessibility, device, and release evidence.

Do not add a package merely to make a folder look organized. Add a package when
the module boundary improves dependency direction, testing, reuse, or target
ownership.

## Start with the target graph

Record:

- app, framework, extension, companion, and test targets;
- package products selected by each target;
- platform and minimum deployment target;
- manifest tools version and compiler/Xcode toolchain;
- source/resources and privacy manifest ownership;
- capabilities, entitlements, usage descriptions, and App Groups;
- Debug/Release/evaluation configurations and schemes;
- local versus remote versus binary package dependencies;
- macro/plugin target and product membership;
- generated output directory and archive membership;
- physical-device/system surfaces that consume the package.

A simple feature graph is:

    Domain
      -> Feature
      -> Design
      -> Platform adapter
      -> App/extension/system surface
      -> test/release proof

## Route A: local package for a reusable feature

Use a local package when the domain or feature can compile independently:

1. Create the package with the selected Swift tools version.
2. Define a regular target for the module.
3. Define a library product only if another package/project target consumes it.
4. Add a test target that depends on the regular target.
5. Put resources under the owning target and load them through Bundle.module.
6. Add platform declarations and target-specific conditions.
7. Keep app navigation, permissions, and system controllers in the app target.
8. Add the package product to only the intended Xcode targets.
9. Build/test the package with SwiftPM.
10. Build the actual app/extension scheme and inspect the bundle/archive.

Use one package target per stable boundary, not one target per view. Keep a
small utility target separate from a large UI target when it materially changes
platform availability or process/resource behavior.

## Route B: source dependency

For an external source package:

1. Verify the author, repository, license, platform support, and release practice.
2. Choose a version requirement instead of following a branch for production.
3. Use a branch only while developing coordinated packages.
4. Avoid a commit requirement except for a documented exceptional reason.
5. Select only needed products for each app/extension/test target.
6. Resolve the graph in Xcode and commit Package.resolved when required.
7. Review changes to resolved revisions and binary checksums.
8. Test the package against the selected iOS SDK and deployment target.
9. Remove or replace dependencies that violate privacy, size, target, or release
   constraints.

A package resolution is not a security audit. Keep dependency provenance and
runtime behavior in the project record.

## Route C: binary dependency

Use a binary package only when its distribution and target support are
understood:

1. Record the HTTPS artifact URL and checksum.
2. Inspect the artifact bundle, slices, linked frameworks, resources, and license.
3. Check simulator/device and supported architecture behavior.
4. Determine whether app extensions can link it.
5. Review privacy manifest and required-reason API implications.
6. Verify symbol visibility and release stripping.
7. Build Debug and Release targets that actually link it.
8. Inspect the archive and TestFlight artifact.
9. Test startup, feature use, and failure behavior on a physical device.

Do not treat a matching checksum as proof that the binary is safe, accessible,
compatible, or allowed by App Store review.

## Route D: resources and localized design

1. Decide whether each resource is processed or copied.
2. Place it in the target that owns its API.
3. Use Bundle.module in package code.
4. Add localized resources and default localization deliberately.
5. Test missing, corrupt, and unsupported resources.
6. Inspect the app, widget, extension, and archive bundles separately.
7. Keep user media and on-device model packs out of the package when the product
   needs download, deletion, encryption, or account-scoped retention.
8. Keep app icons and release metadata in the app target unless a system surface
   specifically owns a separate asset.

## Route E: platform conditions and adapters

Use target separation when the semantics or process contract differ:

~~~swift
// In a manifest, use the selected PackageDescription API for a conditional
// target product dependency. Confirm exact spelling in the selected toolchain.
.product(
    name: "DeviceOnlyAdapter",
    package: "DeviceAdapters",
    condition: .when(platforms: [.iOS])
)
~~~

In source, use availability checks for symbols within a supported target. In the
manifest, use platform/dependency conditions for the package graph. In Xcode,
use target membership and product linkage for the actual product. These are three
different gates.

Do not hide a watchOS/iOS/visionOS architecture in a single target if the
framework imports, UI hierarchy, resource bundle, or entitlement set diverges.

## Route F: macro

Use a macro when compile-time generated code provides a clearer, type-checked
API than handwritten repetition.

The macro route has two targets:

    macro declaration/library target
      -> macro implementation target
      -> generated code in the client target

Start with:

1. select a Swift tools version supported by the macro documentation and target;
2. import CompilerPluginSupport in the package manifest;
3. declare the macro implementation target with .macro;
4. add compatible SwiftSyntax products to the implementation target;
5. declare the public macro in a regular target;
6. attach accurate macro roles;
7. expose only the public macro API;
8. write expansion fixtures and generated-code tests;
9. compile a client target that uses the macro;
10. inspect generated API and availability in the actual app target.

Macros must not hide runtime network requests, model calls, permission prompts,
secret material, or domain mutations. Generated code still follows normal
availability, actor isolation, privacy, accessibility, and release rules.

## Route G: build-tool plugin

Use a build-tool plugin for generated source/resources or work that belongs in a
target’s build graph:

1. add a plugin target with buildTool capability;
2. provide an executable or binary tool dependency;
3. apply the plugin to the exact target(s);
4. identify input files and output files;
5. use a build command when outputs are predictable;
6. use a prebuild command only when output names are discovered at runtime;
7. write into the plugin work directory;
8. return diagnostics with actionable file/line information;
9. compile the generated output in the target;
10. test no-input, changed-input, deleted-input, and tool-failure cases;
11. review generated diffs and archive membership.

A build-tool plugin constructs commands; the external tool performs the work. Keep
the tool deterministic and versioned. Never let the plugin silently download
runtime assets or write outside the declared policy.

## Route H: command plugin

Use a command plugin for a user- or CI-invoked action that is not part of every
build:

- format a package;
- generate documentation;
- audit an API surface;
- migrate a fixture;
- validate a project-local contract.

Declare the command intent and permissions. Expect sandbox constraints. If the
plugin must write to the package directory, require explicit user/CI approval.
If it must use the network, document and request the permission. Keep a no-write
or dry-run mode for review.

## Route I: Liquid Glass and AI package composition

Build the package boundary like this:

    domain state
      -> design component with semantic state
      -> app-owned Liquid Glass action group
      -> AI typed proposal
      -> deterministic validator
      -> review
      -> domain command

The design target can expose a ReviewSurface, StatusCapsule, or NativeActionGroup.
The AI target can expose a ReviewProposal and readiness/error states. The app owns
navigation, authorization, system controllers, and durable effects.

For system surfaces, create a smaller projection target. WidgetKit, ActivityKit,
ControlWidget, App Intents, and notification extensions should not import a full
app shell simply because the package exports it.

## Route J: verification packet

Capture:

- Package.swift and tools-version;
- package description and target graph;
- platform/deployment matrix;
- dependency versions and Package.resolved;
- binary URLs/checksums/artifact inspection;
- target product membership;
- macro/plugin target and generated output;
- resource and privacy manifest ownership;
- package tests and app/extension tests;
- Xcode build/archive logs;
- signed entitlements/Info.plist/bundle inspection;
- physical device/system-surface/accessibility evidence;
- TestFlight/release result.

## Failure states

Provide explicit recovery for:

- package resolution conflict;
- unsupported platform/deployment target;
- missing product selection;
- resource not found;
- macro expansion failure;
- plugin permission denial;
- tool missing or output missing;
- binary slice/link failure;
- generated code incompatible with current SDK;
- app target compiles but extension target cannot link;
- Debug succeeds but Release archive omits resources;
- AI adapter unavailable or proposal stale.

## Sources

- [Swift packages](https://developer.apple.com/documentation/xcode/swift-packages)
- [Adding package dependencies to your app](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
- [Creating a standalone Swift package with Xcode](https://developer.apple.com/documentation/xcode/creating-a-standalone-swift-package-with-xcode)
- [Identifying binary dependencies](https://developer.apple.com/documentation/xcode/identifying-binary-dependencies)
- [PackageDescription](https://docs.swift.org/swiftpm/documentation/packagedescription/)
- [Package](https://docs.swift.org/swiftpm/documentation/packagedescription/package/)
- [Target](https://docs.swift.org/swiftpm/documentation/packagedescription/target/)
- [Target dependencies](https://docs.swift.org/swiftpm/documentation/packagedescription/target/dependencies/)
- [Adding dependencies to a Swift package](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/addingdependencies/)
- [Macros](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/macros/)
- [PackagePlugin](https://docs.swift.org/swiftpm/documentation/packageplugin/)
- [Plugins](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/plugins/)
- [Writing a build tool plugin](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/writingbuildtoolplugin/)
- [Writing a command plugin](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/writingcommandplugin/)
- [Enable a build plugin](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/enablebuildplugin/)
- [Enable a command plugin](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/enablecommandplugin/)
- [Swift package commands](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/swiftpackagecommands/)
- [App Groups Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.security.application-groups)
- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
