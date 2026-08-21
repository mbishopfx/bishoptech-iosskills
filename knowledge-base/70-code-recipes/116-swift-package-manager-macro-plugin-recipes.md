# Swift Package Manager, macro, and plugin recipes

These are compile-oriented route sketches for a named package and Xcode target.
They are not compiled in this documentation workspace and do not prove manifest
compatibility, macro expansion, plugin sandbox behavior, Xcode target linkage,
resource/archive membership, accessibility, device behavior, or release
readiness. Confirm the selected Swift/Xcode toolchain, PackageDescription API,
deployment targets, package product membership, and current compiler diagnostics.

## Recipe 1: package with domain, design, AI, and test targets

Use products to expose stable modules and targets to keep implementation
boundaries clear:

~~~swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "ProductKit",
    platforms: [
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "ProductDomain",
            targets: ["ProductDomain"]
        ),
        .library(
            name: "ProductDesign",
            targets: ["ProductDesign"]
        ),
        .library(
            name: "ProductAIAdapter",
            targets: ["ProductAIAdapter"]
        )
    ],
    targets: [
        .target(
            name: "ProductDomain"
        ),
        .target(
            name: "ProductDesign",
            dependencies: ["ProductDomain"],
            resources: [
                .process("Resources")
            ]
        ),
        .target(
            name: "ProductAIAdapter",
            dependencies: ["ProductDomain"]
        ),
        .testTarget(
            name: "ProductDomainTests",
            dependencies: ["ProductDomain"]
        )
    ]
)
~~~

This is a manifest sketch. Confirm the minimum tools version, iOS platform
spelling, resource rule, and Foundation Models/Core ML availability in the
selected toolchain. A package target’s platform declaration is not a substitute
for API availability checks in source.

## Recipe 2: package resource access

Keep the resource in the target that declares it:

~~~swift
import Foundation

enum DesignResource {
    static func loadPalette() throws -> Data {
        guard let url = Bundle.module.url(
            forResource: "palette",
            withExtension: "json"
        ) else {
            throw ResourceError.missing
        }
        return try Data(contentsOf: url)
    }
}
~~~

Test the package target with the resource present, missing, localized, and
corrupt. Inspect the app/extension archive separately; a package test finding
Bundle.module does not prove the consuming product contains the resource.

## Recipe 3: platform-conditional product dependency

Use manifest conditions for package graph differences and source availability
checks for API differences:

~~~swift
.target(
    name: "ProductAdapters",
    dependencies: [
        "ProductDomain",
        .product(
            name: "DeviceOnlyAdapter",
            package: "DeviceAdapters",
            condition: .when(platforms: [.iOS])
        )
    ]
)
~~~

The exact PackageDescription overloads and platform names are toolchain-sensitive.
If the platform implementation is structurally different, use separate targets
rather than forcing unsupported imports through conditional compilation.

## Recipe 4: declare a macro and implementation target

A macro package normally separates the public declaration target from the
implementation target:

~~~swift
import PackageDescription
import CompilerPluginSupport

let package = Package(
    name: "ProductMacros",
    products: [
        .library(
            name: "ProductSchema",
            targets: ["ProductSchema"]
        )
    ],
    dependencies: [
        .package(
            url: "https://github.com/swiftlang/swift-syntax.git",
            from: "509.0.0"
        )
    ],
    targets: [
        .macro(
            name: "ProductSchemaMacros",
            dependencies: [
                .product(
                    name: "SwiftSyntaxMacros",
                    package: "swift-syntax"
                ),
                .product(
                    name: "SwiftCompilerPlugin",
                    package: "swift-syntax"
                )
            ]
        ),
        .target(
            name: "ProductSchema",
            dependencies: ["ProductSchemaMacros"]
        ),
        .testTarget(
            name: "ProductSchemaTests",
            dependencies: ["ProductSchema"]
        )
    ]
)
~~~

The SwiftSyntax version and exact manifest API must match the selected Swift
toolchain. Keep the macro implementation target out of the app’s runtime
linkage. The library target is what client source imports.

A public macro declaration can look like:

~~~swift
@attached(member, names: named(schemaVersion))
public macro SchemaVersion(_ value: Int) =
    #externalMacro(
        module: "ProductSchemaMacros",
        type: "SchemaVersionMacro"
    )
~~~

Implement the macro using the current SwiftSyntax macro protocol and test both
valid and invalid expansion. Generated names and declarations are part of the
library’s API; review the expansion.

## Recipe 5: macro as a typed proposal helper

A macro may generate boilerplate for a proposal schema, but it should not
generate authorization or side effects:

~~~swift
@attached(member, names: named(modelRoute))
public macro ProposalMetadata(_ route: String) =
    #externalMacro(
        module: "ProductSchemaMacros",
        type: "ProposalMetadataMacro"
    )

struct SummarizeProposal {
    @ProposalMetadata("on-device-visible-context")
    let text: String
}
~~~

Treat this as conceptual syntax until the selected macro role supports the
generated member shape. The generated type still needs source revision,
privacy scope, validation, person review, and an app-owned commit path.

## Recipe 6: build-tool plugin manifest

Use a build plugin when work belongs in the build graph:

~~~swift
import PackageDescription

let package = Package(
    name: "GeneratedAssets",
    products: [
        .plugin(
            name: "AssetGeneratorPlugin",
            targets: ["AssetGeneratorPlugin"]
        )
    ],
    targets: [
        .executableTarget(
            name: "asset-generator"
        ),
        .plugin(
            name: "AssetGeneratorPlugin",
            capability: .buildTool(),
            dependencies: ["asset-generator"]
        ),
        .target(
            name: "AssetConsumer",
            plugins: ["AssetGeneratorPlugin"]
        )
    ]
)
~~~

A real manifest may need an executable product or a package product dependency
instead of a same-package target dependency. Confirm the selected
PackageDescription spelling and target dependency form.

## Recipe 7: build-tool plugin command graph

A build plugin constructs commands and declares inputs/outputs:

~~~swift
import PackagePlugin

@main
struct AssetGeneratorPlugin: BuildToolPlugin {
    func createBuildCommands(
        context: PluginContext,
        target: Target
    ) throws -> [Command] {
        guard let source = target.sourceModule else { return [] }
        let tool = try context.tool(named: "asset-generator")
        let output = context.pluginWorkDirectoryURL
            .appendingPathComponent("GeneratedAssets.swift")

        let inputs = source.sourceFiles
            .filter { $0.url.pathExtension == "asset-spec" }
            .map(\.url)

        guard !inputs.isEmpty else { return [] }

        return [
            .buildCommand(
                displayName: "Generate typed assets",
                executable: tool.url,
                arguments: [
                    "--output", output.path
                ],
                inputFiles: inputs,
                outputFiles: [output]
            )
        ]
    }
}
~~~

The plugin work directory is owned by the package manager. Keep tool arguments
bounded and deterministic. The tool, not the plugin, creates the output. Test
changed inputs, removed inputs, no inputs, tool failure, and output cleanup.

If output names cannot be known before running the tool, use prebuildCommand and
declare an outputFilesDirectory, then ensure the tool performs its own caching.
Do not use a prebuild command for predictable one-file-per-input generation just
because it is simpler.

## Recipe 8: command plugin with explicit permission

Command plugins are user/CI actions, not automatic build work:

~~~swift
import PackagePlugin

@main
struct VerifyRoutePlugin: CommandPlugin {
    func performCommand(
        context: PluginContext,
        arguments: [String]
    ) throws {
        let tool = try context.tool(named: "route-verifier")
        let result = try Process.run(
            tool.url,
            arguments: ["--package", context.package.directory.string]
        )
        result.waitUntilExit()
        guard result.terminationStatus == 0 else {
            Diagnostics.error("Route verification failed")
            throw PluginError.failed
        }
    }
}
~~~

The exact Process/tool API and permission declaration are toolchain-sensitive.
Keep a dry-run mode, make write/network requirements explicit, and invoke the
command only with user/CI approval when it needs to change package files.

## Recipe 9: package integration in Xcode

Use Xcode’s package dependency UI or project configuration, then verify each
target:

1. Add the package dependency to the project.
2. Choose the package product in the app target’s Frameworks/Libraries phase.
3. Add the product separately to any widget, App Intent, share, watch, or test
   target that needs it.
4. Confirm the package identity/revision in Package.resolved.
5. Build each scheme/configuration that claims support.
6. Inspect the generated app/extension bundle for package resources and linked
   products.
7. Archive and inspect Release/TestFlight output.

A package listed under Swift Package Dependencies is not proof that the selected
target links its product.

## Recipe 10: package and Xcode inspection commands

Run from a clean checkout:

~~~text
swift package describe
swift package dump-package
swift package show-dependencies
swift package tools-version
swift package resolve
swift test
swift package plugin --list
~~~

Use the selected Xcode scheme to build the real app/extension target after the
package commands pass. The command-line package graph and Xcode project graph
can differ in target membership, platform, signing, resources, and host behavior.

## Recipe 11: AI adapter boundary

Keep on-device AI behind a protocol:

~~~swift
struct AIInput: Sendable {
    let sourceID: UUID
    let sourceRevision: Int
    let visibleText: String
}

struct AIPolicyProposal: Sendable {
    let sourceID: UUID
    let sourceRevision: Int
    let action: String
    let modelRoute: String
}

protocol OnDeviceIntelligence: Sendable {
    func propose(_ input: AIInput) async throws -> AIPolicyProposal
}
~~~

The app/domain layer validates the proposal against current state and asks for
review. The AI package does not navigate, write SwiftData, call StoreKit,
authorize HealthKit, send GameKit data, or mutate a widget/Live Activity.

## Recipe 12: semantic Liquid Glass package component

Keep glass scoped to a functional group:

~~~swift
struct ActionGroup: View {
    let canApprove: Bool
    let approve: () -> Void
    let retry: () -> Void

    var body: some View {
        HStack {
            if canApprove {
                Button("Approve", action: approve)
            }
            Button("Retry", action: retry)
        }
        .glassEffect()
    }
}
~~~

Use a semantic fallback for the selected deployment target and test
Reduce Transparency, increased contrast, Dynamic Type, VoiceOver, and system
surface hosts. The component emits app-owned intent; it does not own domain truth.

## Recipe 13: package tests for generated and runtime contracts

Test at least:

~~~swift
struct ProposalFixtures {
    static let current = AIPolicyProposal(
        sourceID: UUID(),
        sourceRevision: 4,
        action: "summarize",
        modelRoute: "on-device-visible-context"
    )
}
~~~

Cover:

- manifest/target/product graph;
- Bundle.module resource success and failure;
- macro valid/invalid expansion;
- plugin input/output and permission failures;
- platform-conditional target builds;
- Package.resolved revision changes;
- app/widget/extension product membership;
- generated API availability;
- Liquid Glass accessibility fallback;
- AI stale/invalid/unavailable proposal rejection.

Use the actual Xcode target for app UI and system-surface tests. Package tests
cannot prove WidgetKit, App Intents, Handoff, hardware, APNs, or App Store behavior.

## Recipe 14: release evidence

Record:

- selected Swift/Xcode tools version and SDK;
- Package.swift and Package.resolved;
- dependency provenance, licenses, and checksums;
- package products selected by each target;
- macro/plugin implementation target exclusions from runtime bundles;
- generated sources/resources in the archive;
- app/extension entitlements, privacy manifests, and Info.plist;
- Debug/Release/TestFlight build results;
- physical device accessibility and system-surface results;
- on-device AI availability/latency/privacy evidence;
- known unsupported targets and fallback behavior.

## Sources

- [Swift packages](https://developer.apple.com/documentation/xcode/swift-packages)
- [Adding package dependencies to your app](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
- [Identifying binary dependencies](https://developer.apple.com/documentation/xcode/identifying-binary-dependencies)
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
- [Build system](https://developer.apple.com/documentation/xcode/build-system)
- [Customizing the build schemes for a project](https://developer.apple.com/documentation/xcode/customizing-the-build-schemes-for-a-project)
- [Adding a build configuration file to your project](https://developer.apple.com/documentation/xcode/adding-a-build-configuration-file-to-your-project)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
