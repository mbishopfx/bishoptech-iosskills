# AudioToolbox and Audio Unit real-time code recipes

These are compile-oriented sketches for a named iOS target. They show the ownership boundary between AVFAudio, AudioToolbox, render resources, and SwiftUI. Confirm the exact SDK overlay and host/extension configuration before using them in production.

## 1. Describe and instantiate an Audio Unit

~~~swift
import AVFAudio
import AudioToolbox

let description = AudioComponentDescription(
    componentType: kAudioUnitType_Effect,
    componentSubType: kAudioUnitSubType_Delay,
    componentManufacturer: kAudioUnitManufacturer_Apple,
    componentFlags: 0,
    componentFlagsMask: 0
)

AVAudioUnit.instantiate(
    with: description,
    options: []
) { audioUnit, error in
    guard let audioUnit, error == nil else {
        // Surface a recoverable component/host error.
        return
    }

    // Attach/configure on the audio-engine control boundary.
    _ = audioUnit
}
~~~

The component description is identity, not proof of compatible formats or output. Inspect the instantiated unit, busses, parameters, and host lifecycle before attaching it.

## 2. Enumerate a matching component

~~~swift
import AudioToolbox

func findEffect(_ description: AudioComponentDescription) -> AudioComponent? {
    var mutableDescription = description
    return AudioComponentFindNext(nil, &mutableDescription)
}
~~~

Wrap C APIs in a small owner, check nil/OSStatus, and keep component discovery off the render thread. A component may be absent, disabled, or unsupported by the current host.

## 3. Allocate and release AUAudioUnit resources

~~~swift
import AudioToolbox

func prepare(_ unit: AUAudioUnit) throws {
    // Configure busses, formats, parameters, and connections before this point.
    try unit.allocateRenderResources()
}

func teardown(_ unit: AUAudioUnit) {
    unit.deallocateRenderResources()
}
~~~

Do not change engine-owned stream formats, channel layouts, initialization, or graph connections through an arbitrary underlying Audio Unit reference. Stop or quiesce the host according to its lifecycle before reconfiguring.

## 4. Render-block boundary

~~~swift
import AudioToolbox

func installRenderPath(on unit: AUAudioUnit) {
    let renderBlock = unit.internalRenderBlock

    // The actual callback signature is SDK-sensitive.
    // The render path must validate frame counts and buffers, then perform
    // bounded DSP using already allocated resources.
    _ = renderBlock
}
~~~

The render path must not allocate, wait on a lock shared with UI/control code, call SwiftUI, write to disk, make a network request, invoke a model, or perform unbounded logging. Publish control changes through a bounded snapshot or atomic parameter mechanism.

## 5. Engine graph with a hosted Audio Unit

~~~swift
import AVFAudio

final class AudioGraphOwner {
    let engine = AVAudioEngine()

    func attach(_ unit: AVAudioUnit, format: AVAudioFormat) throws {
        engine.attach(unit)
        engine.connect(unit, to: engine.mainMixerNode, format: format)
    }

    func start() throws {
        try engine.start()
    }

    func stop() {
        engine.stop()
    }
}
~~~

Configure AVAudioSession separately and handle route changes, interruptions, sample-rate changes, and engine failures. A running engine is not proof that a user heard the intended output.

## 6. Control-to-render parameter handoff

~~~swift
struct RenderParameters: Sendable {
    var mix: Float
    var cutoff: Float
    var bypassed: Bool
}

final class ParameterStore {
    // Replace with a measured atomic/snapshot mechanism for the render path.
    private var current = RenderParameters(
        mix: 0.5,
        cutoff: 1000,
        bypassed: false
    )

    func publish(_ parameters: RenderParameters) {
        current = parameters
    }

    func snapshot() -> RenderParameters {
        current
    }
}
~~~

This simple class is a boundary illustration, not a proof of thread safety. Use a mechanism appropriate to the target’s concurrency and memory-order requirements. Do not take a UI lock in the render callback.

## 7. Treat Audio Workgroups as a specialized route

~~~swift
import AudioToolbox

func workgroupPolicy() -> String {
    // If the app only uses framework-created audio threads, the system
    // associates them with the audio device workgroup automatically.
    // Add explicit workgroup coordination only when the app or unit owns
    // auxiliary real-time threads and measurement justifies it.
    return "Use the framework render thread unless an auxiliary deadline exists."
}
~~~

Workgroup membership does not make a non-real-time task eligible for the render deadline. Keep UI, model, file, and network operations outside the workgroup.

## 8. Project render status into SwiftUI

~~~swift
import Observation
import SwiftUI

@MainActor
@Observable
final class AudioStatusModel {
    var componentName = "No unit loaded"
    var lifecycle = "Stopped"
    var route = "Audio route unknown"
    var warning: String?
}

struct AudioUnitStatusView: View {
    @State private var model = AudioStatusModel()

    var body: some View {
        List {
            Section("Audio route") {
                Text(model.componentName)
                Text(model.lifecycle)
                Text(model.route)
                if let warning = model.warning {
                    Label(warning, systemImage: "exclamationmark.triangle")
                }
            }
            Section("Recovery") {
                Button("Restart audio") { }
                Button("Choose another unit") { }
            }
        }
        .navigationTitle("Audio")
    }
}
~~~

Keep this model control-side. Add a Liquid Glass inspector only after the plain status states are usable with VoiceOver, Dynamic Type, reduced motion, and a failed audio route.

## 9. Validate an AI parameter proposal

~~~swift
struct ParameterProposal: Codable, Sendable {
    let parameterID: String
    let value: Double
    let reason: String
}

func validate(
    _ proposal: ParameterProposal,
    ranges: [String: ClosedRange<Double>]
) -> Bool {
    guard let range = ranges[proposal.parameterID] else {
        return false
    }
    return range.contains(proposal.value)
}
~~~

The model proposes data. The control layer validates that the parameter belongs to the current unit, is in range, is safe to apply while the graph is running, and has user approval. The model never calls a render block or mutates render resources.

## Sources

- [Audio Toolbox](https://developer.apple.com/documentation/audiotoolbox)
- [AudioComponentDescription](https://developer.apple.com/documentation/audiotoolbox/audiocomponentdescription)
- [AUAudioUnit](https://developer.apple.com/documentation/audiotoolbox/auaudiounit)
- [AudioUnit](https://developer.apple.com/documentation/audiotoolbox/audiounit)
- [AudioUnitRenderActionFlags](https://developer.apple.com/documentation/audiotoolbox/audiounitrenderactionflags)
- [Understanding Audio Workgroups](https://developer.apple.com/documentation/audiotoolbox/understanding-audio-workgroups)
- [Workgroup Management](https://developer.apple.com/documentation/audiotoolbox/workgroup-management)
- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioUnit](https://developer.apple.com/documentation/avfaudio/avaudiounit)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

***
