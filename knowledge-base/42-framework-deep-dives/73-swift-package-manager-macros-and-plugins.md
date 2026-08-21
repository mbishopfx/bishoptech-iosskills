# Swift Package Manager, macros, plugins, and Xcode target composition

## Scope

This page defines the package and build-composition route for native iOS projects:

- Package.swift manifests and the PackageDescription model;
- products, targets, modules, dependencies, resources, and platform conditions;
- package integration in Xcode app, framework, test, and extension targets;
- Package.resolved, source dependencies, binary dependencies, and checksums;
- Swift package build-tool plugins and command plugins;
- Swift macro declaration and implementation targets;
- platform, process, actor, privacy, and target-membership boundaries;
- Liquid Glass design-system modules and on-device AI adapter modules;
- compile, test, archive, device, and release evidence.

A package is a build and distribution boundary. It is not automatically a runtime
service, an app target, a process, a permission boundary, or a guarantee that
every Apple framework is available to every product that imports the package.

## The composition model

Reason from the package graph:

    Package.swift manifest
      -> package products
      -> package targets/modules
      -> target source/resources/dependencies
      -> resolved package graph
      -> Xcode target product linkage
      -> selected scheme/configuration
      -> compiled bundle/archive

A useful app graph is:

    DomainKit
      -> FeatureKit
      -> DesignKit
      -> PlatformAdapters
      -> MainApp / Widget / App Intent / Share / Watch / Test targets

The arrow means the consuming target depends on the module above it. Keep the
direction one way. A package target should not import the app target that consumes
it, and a domain module should not import SwiftUI merely because one app surface
needs a view.

## Package vocabulary

| Term | Owns | Does not prove |
| --- | --- | --- |
| Manifest | Package name, products, targets, dependencies, platforms, tools/language settings | That an Xcode app target links the intended product |
| Product | A library, executable, plugin, or other vended package output | That every target can use it on every platform |
| Target | A module, test suite, executable, binary, system library, plugin, or macro implementation boundary | That its symbols are safe in another process or target |
| Module | An importable namespace and access-control boundary | That runtime permissions, entitlements, or resources are available |
| Resource | A package-owned file processed or copied into a target’s resource bundle | That a separate app/extension target can access it without its own dependency |
| Dependency | A package, product, system library, or binary input | That the author, license, platform support, or runtime behavior is trusted |
| Package.resolved | The exact resolved source revisions/checksums for the project graph | That the graph is secure or compatible with every SDK |
| Macro | Compile-time code generation with declared roles and a separate implementation | That generated code is correct, safe, or available at runtime |
| Plugin | Sandboxed package-manager extension that constructs build/command work | That generated output or an external tool is correct |
| Xcode target | One signed product with its own sources, resources, capabilities, and settings | That a package’s source folder is in the target or archive |
| Scheme/configuration | The selected build/test/archive inputs | That another scheme or Release product uses the same inputs |

## Manifest and tools-version boundary

The swift-tools-version declaration tells Swift Package Manager which
PackageDescription API and manifest language version it should use. It is separate
from the iOS deployment target and separate from the SDK installed in Xcode.

Record three values for every package route:

- manifest tools version;
- Swift compiler/Xcode toolchain;
- each target’s supported platform and minimum deployment version.

A package can have a modern manifest and still declare a lower iOS deployment
target for a reusable module. Conversely, a package can declare an iOS 26
minimum while a consuming app target or extension has a different deployment
target. Resolve the intersection in the selected target and compile the exact
scheme.

Do not use a tools-version comment as an assertion that every iOS 26 API is
available. Use the selected SDK’s availability annotations and target-specific
guards for Apple framework symbols.

## Products and targets

A product is what another package or Xcode project can consume. A target is the
module or test boundary that produces it.

Choose the smallest product surface:

| Need | Package shape | Boundary |
| --- | --- | --- |
| Shared domain models/policies | Library product with regular target | No UI or device-only framework imports |
| Feature state and use cases | Library product with one or more regular targets | Typed protocols, deterministic effects, test fixtures |
| Reusable SwiftUI controls | Library product with SwiftUI/design target | Platform availability, resources, Liquid Glass fallback |
| On-device AI adapter | Library/product target gated to supported platforms | Model/session readiness and reviewable proposals |
| C/Objective-C bridge | Separate C-family target and Swift adapter target | A target cannot casually mix Swift and C-family source |
| Unit tests | Test target | Never ship XCTest or Swift Testing as an end-user dependency |
| Executable tool | Executable target/product | Host platform and command-line behavior |
| Code generation | Build tool plugin plus executable/binary tool | Build graph, inputs/outputs, sandbox, generated-source ownership |
| Formatting/documentation action | Command plugin | User/CI invocation and explicit write/network permission |
| Macro API | Regular target that declares public macros | Client-facing API and macro roles |
| Macro implementation | Macro target | Compile-time SwiftSyntax implementation and host-tool boundary |
| Closed-source artifact | Binary target/product | URL/checksum/license/trust/architecture/release inspection |

SwiftPM’s target documentation warns that test libraries belong in test
contexts. Do not make a distributable library or executable depend on XCTest or
Swift Testing transitively.

## Resources

A package resource belongs to the target that declares it. Use the package
resource rules intentionally:

- process images, JSON, localized resources, and other assets that should be
  transformed or localized;
- copy files whose bytes and directory structure must remain intact;
- use Bundle.module from code in the package target;
- keep resource names stable and test missing-resource behavior;
- add resources to the target that owns the API needing them;
- do not assume the main app bundle contains a package resource;
- do not use a resource path from a package as a durable file URL without a copy
  or lifecycle policy.

A design-system package may own symbols, colors, sample data, and localization,
but a widget or extension only receives them if the product target links the
package product and the resource is supported in that target.

An on-device model resource should have an explicit ownership record:

    model resource
      -> package target or app target
      -> compiled/downloaded model policy
      -> model manifest/version
      -> target membership/archive inspection
      -> readiness and fallback state

A successful Bundle.module lookup does not prove that a model is compatible with
the device, language, OS, memory budget, or Foundation Models route.

## Dependencies and resolution

For a source dependency, separate:

    declared requirement
      -> resolver choice
      -> Package.resolved revision
      -> target product selected
      -> compiled module
      -> runtime behavior

Choose version requirements intentionally:

- a version range balances updates and compatibility;
- a branch requirement is useful while developing packages in tandem;
- a commit requirement is exceptional and should be documented;
- Package.resolved records the exact revisions used by an Xcode project;
- package products must be selected for each consuming target;
- removing a package product from one target does not remove the package from all
  other targets.

Commit Package.resolved when the project workflow expects reproducible package
versions. Review changes to it as dependency changes, not as incidental Xcode
noise. A resolved revision can build and still contain an API or behavior change
that needs code review.

Binary dependencies add extra gates:

- URL and checksum;
- artifact bundle contents and supported architectures;
- license/provenance;
- privacy and required-reason API implications;
- linked frameworks and transitive runtime requirements;
- symbol stripping and release behavior;
- whether the binary contains device-only or simulator-only slices;
- whether every app/extension target can link it.

Apple’s Xcode guidance calls out the drawbacks of binary dependencies and asks
developers to use trustworthy authors. A checksum proves the archive matches the
declared artifact; it does not prove the artifact is safe or functionally correct.

## Platform and conditional dependencies

Declare the package’s supported platforms, then apply conditional dependencies or
source availability where a product truly differs by platform.

Examples of distinct boundaries:

- an iOS SwiftUI target may import UIKit;
- a watch target may use WatchKit but not iOS-only UI;
- a visionOS target may use RealityKit/SwiftUI APIs unavailable to iPhone;
- a command-line tool may run on macOS but never ship in the iOS app;
- a model-evaluation executable may use fixtures that must not enter the app
  bundle;
- an extension may be linked to a package product but still be unable to use a
  capability or API within its host/runtime limits.

Use platform conditions to describe dependency availability. Use Swift availability
checks for API availability. Use target separation when the code’s semantics,
resource graph, privacy, or process contract differs. Do not hide a whole
platform architecture inside scattered conditional compilation simply to make one
target compile.

## Swift macros

Swift macros transform source at compile time. Swift documents two broad families:

- freestanding macros invoked independently;
- attached macros applied to declarations.

A macro declaration is the client-facing API. The macro implementation is a
separate program/target that performs expansion, commonly using SwiftSyntax. The
client target and implementation target have different responsibilities:

    Macro API target
      -> public macro declarations and roles
      -> Macro implementation target
      -> generated Swift declarations
      -> client target type checking and compilation

Macros are additive: they generate code, but they do not delete or mutate the
source in place. The compiler checks the macro input and generated output as
Swift. A macro expansion failure is a compile failure.

Keep macro boundaries explicit:

- expose only the intended public macro declarations;
- declare the roles accurately;
- pin/use a SwiftSyntax version compatible with the selected toolchain;
- keep the implementation free of runtime app secrets and user data;
- test expansion with syntax fixtures and generated API expectations;
- review generated code as part of the module’s public behavior;
- do not use a macro to conceal a network call, permission request, or model
  side effect;
- keep iOS-only generated code behind the target/availability boundary that owns it.

For App Intents, model schemas, or AI proposal types, a macro can reduce
boilerplate, but generated code still needs ordinary authorization, freshness,
accessibility, and release proof.

## Swift package plugins

Swift Package Manager has two distinct plugin roles:

| Plugin role | Use | Lifecycle and permission boundary |
| --- | --- | --- |
| Build tool plugin | Generate source/resources or run a tool before/during a target build | Applied to targets; declares inputs/outputs; build graph can cache predictable commands |
| Command plugin | User/CI action such as formatting, documentation, or migration | Invoked on demand; may request explicit write/network permissions |

A build tool plugin constructs commands. The external executable performs the
work. Prefer a build command when inputs and outputs are known; use a prebuild
command when output names are not known until the tool runs, and add caching
because prebuild work can run every build.

Plugins run in a separate process. SwiftPM sandboxing prevents network access and
most arbitrary filesystem writes. Build plugins cannot modify package source.
Command plugins that need to write the package directory require approval or an
explicit allow-writing flag. Treat plugin permissions as part of the supply-chain
and build-trust review.

A plugin’s output must be declared and owned:

    package input target
      -> plugin command
      -> plugin work directory
      -> generated Swift/resource output
      -> target compile/resource processing
      -> artifact inspection

Do not commit generated output by accident, and do not assume a generated file
exists before the plugin runs. If generated source changes the public API, review
the generated diff and add a fixture that proves the generated symbols are
available to the intended target.

Xcode can extend the PackagePlugin API through XcodeProjectPlugin for project-aware
plugins. Do not assume a package plugin has the same inputs or capabilities when
invoked by the SwiftPM command line and by Xcode.

## Xcode integration

When an Xcode project adds a package dependency:

1. Xcode resolves the package graph.
2. The project selects one or more package products for specific targets.
3. The selected target’s build phases link/compile the product.
4. Xcode records resolution state in Package.resolved.
5. The scheme determines which app, extension, test, or archive action builds it.

Inspect the target’s package products, not only the project’s package list. A
package can be present in the project and absent from the target. A package
product can compile in the app and fail in a widget or App Intent extension due
to platform, resource, linker, or process differences.

Local package editing is useful for development, but the final project should
record whether the dependency is a local package, a repository version, or a
binary artifact. Test the package independently with SwiftPM and then compile the
actual Xcode target that embeds or links it.

## Liquid Glass and Apple-native design modules

Keep the visual system in a target that can legally import SwiftUI and the
relevant platform APIs:

    DesignTokens
      -> NativeComponents
      -> App/extension surface

Design modules should provide semantic components and state, not a generic
translucent coating:

- standard SwiftUI controls and navigation remain the default;
- Liquid Glass is applied to functional groups and platform-appropriate surfaces;
- reduced transparency, contrast, Dynamic Type, and Reduce Motion have a
  component-level fallback;
- widget/control/Live Activity targets use their system-surface rendering rules;
- the design package does not own domain truth or mutate records;
- design previews use deterministic fixtures, not live services;
- platform variants remain explicit rather than hidden in runtime magic.

A package that exports an Apple-like visual language should preserve the platform
hierarchy and original product identity. Reproducing system-owned sheets or
overlays in a package does not create an Apple system surface.

## On-device AI package boundaries

A reusable intelligence package should expose typed contracts:

    source snapshot
      -> AI capability adapter
      -> typed proposal
      -> deterministic validator
      -> person review
      -> domain command
      -> projection

Keep Foundation Models, Core ML, Vision, Speech, Translation, or other device
framework imports in an adapter target when they are not needed by domain code.
The domain module should see:

- an input value with explicit provenance and privacy scope;
- a typed proposal with source revision and model route;
- availability/readiness/error states;
- cancellation and retry semantics;
- a deterministic validation result.

Do not put the model session, prompt text, raw private media, or system side effect
inside a macro or package plugin. Compile-time tools and runtime AI have different
security, privacy, and lifecycle boundaries.

## Testing and evidence

Test in layers:

- manifest parsing and package graph;
- package target/module imports;
- resources and missing-resource fallback;
- macro expansion and generated code;
- plugin command construction and declared outputs;
- pure domain/AI proposal validation;
- Xcode app/extension target integration;
- signed archive resource/entitlement/Info.plist inspection;
- physical device and system-surface behavior;
- TestFlight/release distribution.

A successful swift package resolve is dependency evidence. A successful
Xcode archive is artifact evidence. Neither proves the generated UI is accessible,
the model is available, the system surface invokes the extension, or a released
binary behaves on every target device.

## Sources

- [Swift packages](https://developer.apple.com/documentation/xcode/swift-packages)
- [Adding package dependencies to your app](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
- [Creating a standalone Swift package with Xcode](https://developer.apple.com/documentation/xcode/creating-a-standalone-swift-package-with-xcode)
- [Identifying binary dependencies](https://developer.apple.com/documentation/xcode/identifying-binary-dependencies)
- [Configuring a new target in your project](https://developer.apple.com/documentation/xcode/configuring-a-new-target-in-your-project)
- [Build system](https://developer.apple.com/documentation/xcode/build-system)
- [Customizing the build schemes for a project](https://developer.apple.com/documentation/xcode/customizing-the-build-schemes-for-a-project)
- [Adding a build configuration file to your project](https://developer.apple.com/documentation/xcode/adding-a-build-configuration-file-to-your-project)
- [PackageDescription](https://docs.swift.org/swiftpm/documentation/packagedescription/)
- [Package](https://docs.swift.org/swiftpm/documentation/packagedescription/package/)
- [Target](https://docs.swift.org/swiftpm/documentation/packagedescription/target/)
- [Target dependencies](https://docs.swift.org/swiftpm/documentation/packagedescription/target/dependencies/)
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
- [Xcode release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-14-release-notes)
- [App Groups Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.security.application-groups)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Apple Intelligence and machine learning](https://developer.apple.com/documentation/TechnologyOverviews/ai-machine-learning)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
