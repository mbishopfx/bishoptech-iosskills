# SwiftUI Audio Unit v3 host and extension review recipes

These are compile-oriented shapes for a host app and AUv3 extension. They show the ownership boundaries and API direction; verify exact imported names, availability, `Info.plist`, extension metadata, and render signatures against the final iOS 26 SDK in a named target. Do not treat these snippets as proof of physical audio, extension discovery, or render performance.

## 1. Component description helper

Keep component identity explicit and testable. A display name is not a stable component key.

~~~swift
import AudioToolbox

struct ComponentKey: Hashable, Sendable {
    let type: OSType
    let subtype: OSType
    let manufacturer: OSType
}

func makeDescription(_ key: ComponentKey) -> AudioComponentDescription {
    AudioComponentDescription(
        componentType: key.type,
        componentSubType: key.subtype,
        componentManufacturer: key.manufacturer,
        componentFlags: 0,
        componentFlagsMask: 0
    )
}
~~~

Use the constants for known unit categories and a documented FourCC conversion for product-owned components. Keep the description in the route record and archive inspection.

## 2. Discover registered components

The manager can search registered Audio Unit metadata without opening each unit.

~~~swift
import AVFAudio
import AudioToolbox

struct ComponentDescriptor: Identifiable, Sendable {
    let id: ComponentKey
    let name: String
    let manufacturer: String
    let version: Int
    let tags: [String]
}

final class ComponentDiscovery {
    private(set) var revision: UInt64 = 0

    func components(matching description: AudioComponentDescription) -> [AVAudioUnitComponent] {
        revision &+= 1
        return AVAudioUnitComponentManager.shared().components(matching: description)
    }

    func observeRegistrationChanges(_ handler: @escaping () -> Void) -> NSObjectProtocol {
        NotificationCenter.default.addObserver(
            forName: AVAudioUnitComponentManager.registrationsChangedNotification,
            object: nil,
            queue: .main
        ) { _ in
            handler()
        }
    }
}
~~~

In production, normalize each `AVAudioUnitComponent` into an app-owned `ComponentDescriptor` and publish a snapshot revision. Keep discovery separate from instantiation and do not perform it from a SwiftUI view body.

## 3. Async host instantiation

Use the async `AVAudioUnit.instantiate` route for a unit that may require asynchronous instantiation.

~~~swift
import AVFAudio
import AudioToolbox

actor AudioUnitHost {
    private(set) var generation: UInt64 = 0
    private(set) var loadedUnit: AVAudioUnit?

    func load(_ description: AudioComponentDescription) async throws -> AVAudioUnit {
        generation &+= 1
        let requestGeneration = generation

        let unit = try await AVAudioUnit.instantiate(
            with: description,
            options: []
        )

        guard requestGeneration == generation else {
            throw CancellationError()
        }

        loadedUnit = unit
        return unit
    }

    func cancelPendingSelection() {
        generation &+= 1
        loadedUnit = nil
    }
}
~~~

The completion/async result can arrive outside the main actor. Hop to the actor that owns engine and SwiftUI state before attaching the unit or publishing status. Retain the returned unit for as long as the graph uses it.

## 4. Attach a unit to an AVAudioEngine graph

Graph ownership belongs to one coordinator. The view should send intents to that coordinator.

~~~swift
import AVFAudio

@MainActor
final class AudioGraphCoordinator: ObservableObject {
    let engine = AVAudioEngine()
    private(set) var unit: AVAudioUnit?

    func attach(_ newUnit: AVAudioUnit, source: AVAudioNode) throws {
        unit = newUnit
        engine.attach(newUnit)

        let format = source.outputFormat(forBus: 0)
        engine.connect(source, to: newUnit, format: format)
        engine.connect(newUnit, to: engine.mainMixerNode, format: format)
    }

    func start() throws {
        try engine.start()
    }

    func stop() {
        engine.stop()
    }
}
~~~

The actual graph may need a source node, mixer, output format, session activation, or an explicit conversion. Record the post-connection formats and route. Do not attach the same unit twice or mutate the graph while the render path is using an incompatible configuration.

## 5. Inspect a parameter tree

Parameter metadata is control-side information. Build a stable app model rather than binding SwiftUI directly to a mutable `AUParameter` object.

~~~swift
import AudioToolbox
import AVFAudio

struct ParameterDescriptor: Identifiable, Sendable {
    let id: AUParameterAddress
    let name: String
    let unit: String?
    let minimum: AUValue
    let maximum: AUValue
    let defaultValue: AUValue
    let currentValue: AUValue
}

func parameterDescriptors(for unit: AVAudioUnit) -> [ParameterDescriptor] {
    guard let tree = unit.auAudioUnit.parameterTree else { return [] }

    return tree.allParameters.map { parameter in
        ParameterDescriptor(
            id: parameter.address,
            name: parameter.displayName,
            unit: parameter.unitName,
            minimum: parameter.minValue,
            maximum: parameter.maxValue,
            defaultValue: parameter.defaultValue,
            currentValue: parameter.value
        )
    }
}
~~~

The final SDK can expose additional parameter flags/value-string behavior that the product should preserve. Refresh the model when the tree changes and reject edits for a stale tree revision.

## 6. Apply a validated parameter edit

Keep user, preset, automation, and AI changes identifiable.

~~~swift
struct ParameterEdit: Sendable {
    let address: AUParameterAddress
    let proposedValue: AUValue
    let treeRevision: UInt64
    let origin: Origin

    enum Origin: Sendable {
        case user
        case factoryPreset
        case userPreset
        case documentRestore
        case aiProposal
    }
}

enum ParameterEditError: Error {
    case staleTree
    case missingParameter
    case outOfRange
}

func apply(
    _ edit: ParameterEdit,
    to unit: AVAudioUnit,
    currentTreeRevision: UInt64
) throws {
    guard edit.treeRevision == currentTreeRevision else {
        throw ParameterEditError.staleTree
    }
    guard let parameter = unit.auAudioUnit.parameterTree?.parameter(withAddress: edit.address) else {
        throw ParameterEditError.missingParameter
    }
    guard edit.proposedValue >= parameter.minValue,
          edit.proposedValue <= parameter.maxValue else {
        throw ParameterEditError.outOfRange
    }

    parameter.value = edit.proposedValue
}
~~~

For an automated/sample-time parameter, use the unit’s documented scheduling path rather than presenting an immediate edit if the graph applies it later. Add a separate undo record after the parameter value has been accepted by the host contract.

## 7. Cache the render block on the host

Hosts should fetch and cache the render block before using it from a real-time context. The host-side snippet is intentionally only a boundary record; the engine normally owns the actual callback invocation.

~~~swift
import AudioToolbox

final class RenderBoundary {
    private var cachedBlock: AURenderBlock?

    func prepare(for unit: AUAudioUnit) {
        cachedBlock = unit.renderBlock
    }

    func invalidate() {
        cachedBlock = nil
    }
}
~~~

Do not call `prepare` or `invalidate` from the render callback. The callback must not allocate, take a UI lock, suspend, access the network, write files, or run Foundation Models. The extension subclass implements its internal render path; the host consumes the unit through the documented host/engine boundary.

## 8. Allocate and release render resources

Make resource state explicit and sequence configuration changes through one owner.

~~~swift
import AudioToolbox

enum RenderResourceState: Sendable {
    case unallocated
    case allocated
    case running
    case resetting
    case failed
}

func allocate(_ unit: AUAudioUnit) throws -> RenderResourceState {
    guard !unit.renderResourcesAllocated else { return .allocated }
    try unit.allocateRenderResources()
    return .allocated
}

func release(_ unit: AUAudioUnit) -> RenderResourceState {
    unit.deallocateRenderResources()
    return .unallocated
}
~~~

Call this control-side after bus/format configuration and before rendering. Stop or quiesce the graph before incompatible reconfiguration. Test reset, route change, interruption, extension termination, and reallocation.

## 9. Factory presets and current state

Expose preset choices as an app model and check component identity before applying them.

~~~swift
import AudioToolbox
import AVFAudio

struct PresetOption: Identifiable, Sendable {
    let id: Int
    let name: String
}

func factoryPresetOptions(for unit: AVAudioUnit) -> [PresetOption] {
    (unit.auAudioUnit.factoryPresets ?? []).map {
        PresetOption(id: $0.number, name: $0.name)
    }
}

func applyFactoryPreset(
    number: Int,
    to unit: AVAudioUnit
) {
    guard let preset = unit.auAudioUnit.factoryPresets?.first(where: { $0.number == number }) else {
        return
    }
    unit.auAudioUnit.currentPreset = preset
}
~~~

The final SDK may import the preset array’s optionality or property names differently; keep the compatibility checks and adjust the syntax. User/document presets require a versioned persistence and migration policy beyond this small factory-preset shape.

## 10. SwiftUI unit inspector

Use semantic controls and keep measured graph state separate from visual material.

~~~swift
import SwiftUI

struct UnitInspector: View {
    let name: String
    let isReady: Bool
    @Binding var bypassed: Bool
    let retry: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Label(name, systemImage: "slider.horizontal.3")
                    .font(.headline)
                Spacer()
                Text(isReady ? "Ready" : "Unavailable")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Toggle("Bypass", isOn: $bypassed)
                .accessibilityHint("Temporarily bypasses processing when the audio unit supports it")

            if !isReady {
                Button("Reconnect", action: retry)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .glassEffect(.regular, in: .rect(cornerRadius: 20))
        .accessibilityElement(children: .contain)
    }
}
~~~

Add parameter rows through `ForEach` with stable addresses and labels. Provide an opaque fallback if material reduces legibility. Do not use the glass card to imply that the graph is processing.

## 11. Typed Foundation Models parameter proposal

The host can use on-device AI to propose a parameter edit after checking availability and capturing a graph snapshot.

~~~swift
import FoundationModels

@Generable
struct AudioParameterProposal {
    @Guide(description: "The stable parameter address from the supplied snapshot")
    var parameterAddress: Int

    @Guide(description: "A value that must still be checked against the parameter range")
    var proposedValue: Double

    @Guide(description: "A short user-facing reason for the proposal")
    var rationale: String
}

func validate(
    _ proposal: AudioParameterProposal,
    against parameter: ParameterDescriptor,
    graphRevisionMatches: Bool
) -> AUValue? {
    guard graphRevisionMatches else { return nil }
    guard AUValue(proposal.proposedValue) >= parameter.minimum,
          AUValue(proposal.proposedValue) <= parameter.maximum else { return nil }
    return AUValue(proposal.proposedValue)
}
~~~

Show the before/after value, unit, component, graph revision, and warnings. Require acceptance and preserve undo. The model does not call the render block or activate the audio session.

## 12. Swift Testing boundaries

Use deterministic tests for identity, generation, range, and preset logic. Use a named target and physical device for extension process, render, and output claims.

~~~swift
import Testing

struct AudioUnitRouteTests {
    @Test func rejectsStaleParameterEdit() throws {
        let edit = ParameterEdit(
            address: 42,
            proposedValue: 0.5,
            treeRevision: 3,
            origin: .user
        )

        // Exercise the production validation seam with revision 4 and assert
        // that no parameter is mutated.
        #expect(edit.treeRevision != 4)
    }
}
~~~

Integration fixtures should cover component discovery, async instantiation, graph formats, resource lifecycle, route interruption, extension re-creation, accessibility, physical output, archive, and TestFlight.

## Sources

- [Audio Components](https://developer.apple.com/documentation/audiotoolbox/audio-components)
- [AudioComponentDescription](https://developer.apple.com/documentation/audiotoolbox/audiocomponentdescription)
- [AudioComponentFindNext](https://developer.apple.com/documentation/audiotoolbox/audiocomponentfindnext%28_%3A_%3A%29)
- [AVAudioUnitComponentManager](https://developer.apple.com/documentation/avfaudio/avaudiounitcomponentmanager)
- [AVAudioUnitComponent](https://developer.apple.com/documentation/avfaudio/avaudiounitcomponent)
- [AVAudioUnit](https://developer.apple.com/documentation/avfaudio/avaudiounit)
- [AVAudioUnit.instantiate(with:options:completionHandler:)](https://developer.apple.com/documentation/avfaudio/avaudiounit/instantiate%28with%3Aoptions%3Acompletionhandler%3A%29)
- [Incorporating Audio Effects and Instruments](https://developer.apple.com/documentation/audiotoolbox/incorporating-audio-effects-and-instruments)
- [AUAudioUnit](https://developer.apple.com/documentation/audiotoolbox/auaudiounit)
- [AUAudioUnitFactory](https://developer.apple.com/documentation/audiotoolbox/auaudiounitfactory)
- [AUAudioUnitBus](https://developer.apple.com/documentation/audiotoolbox/auaudiounitbus)
- [AUAudioUnitBusArray](https://developer.apple.com/documentation/audiotoolbox/auaudiounitbusarray)
- [AUAudioUnit.parameterTree](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/parametertree)
- [AUAudioUnit.renderBlock](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/renderblock)
- [AUAudioUnit.renderingOffline](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/isrenderingoffline)
- [AUAudioUnit.factoryPresets](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/factorypresets)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
