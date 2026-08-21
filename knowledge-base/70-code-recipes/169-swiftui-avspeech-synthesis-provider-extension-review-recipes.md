# SwiftUI custom speech-provider extension review recipes

These are compile-oriented shapes for a host app plus `AVSpeechSynthesisProviderAudioUnit` extension. They are intentionally small. Validate exact initializer labels, `AUAudioUnit` render signatures, extension metadata, and availability against the final iOS 26 SDK in a named host/extension target before shipping. The recipes do not make a simulator run, a generated buffer, or a voice inventory equivalent to physical VoiceOver/Speak Screen proof.

## 1. Versioned provider voice records

Keep the host catalog and the extension inventory on a small, versioned contract. Do not share the entire host database with the extension.

~~~swift
import Foundation

struct ProviderVoiceRecord: Codable, Identifiable, Hashable, Sendable {
    enum Readiness: String, Codable, Sendable {
        case ready
        case installing
        case unavailable
        case retired
    }

    let id: String
    var localizedName: String
    var primaryLanguages: [String]
    var supportedLanguages: [String]
    var voiceVersion: String
    var resourceRevision: String
    var resourceSize: Int64
    var readiness: Readiness
}

struct ProviderCatalogSnapshot: Codable, Sendable {
    var schemaVersion = 1
    var revision: UInt64
    var voices: [ProviderVoiceRecord]
}
~~~

The identifier is the stable key. The localized name is presentation. Keep the catalog’s revision separate from each voice’s resource revision so a provider can reject stale shared state.

## 2. Host App Group publication

The containing app can store a minimal catalog in an App Group and tell the system that the provider voice list changed. The extension should treat the shared value as input, validate it, and never assume that the host app remains alive.

~~~swift
import AVFAudio
import Foundation

enum ProviderCatalogStore {
    static let suiteName = "group.example.speech-provider"
    static let snapshotKey = "provider.catalog.snapshot"

    static func save(_ snapshot: ProviderCatalogSnapshot) throws {
        let data = try JSONEncoder().encode(snapshot)
        guard let defaults = UserDefaults(suiteName: suiteName) else {
            throw CocoaError(.fileNoSuchFile)
        }
        defaults.set(data, forKey: snapshotKey)

        // This asks the system to refresh the provider voice inventory.
        AVSpeechSynthesisProviderVoice.updateSpeechVoices()
    }

    static func load() -> ProviderCatalogSnapshot? {
        guard
            let defaults = UserDefaults(suiteName: suiteName),
            let data = defaults.data(forKey: snapshotKey)
        else { return nil }

        return try? JSONDecoder().decode(ProviderCatalogSnapshot.self, from: data)
    }
}
~~~

Persist before requesting the refresh. The host UI should publish `refreshPending` until a system inventory observation confirms the voice. Avoid writing source text, account identifiers, or secrets to the shared catalog.

## 3. Construct provider voices from validated records

The extension’s `speechVoices` implementation should report only records whose local resources are ready and whose language metadata passes validation. The exact resource-readiness check is product-specific.

~~~swift
import AVFAudio

enum ProviderVoiceFactory {
    static func makeVoice(from record: ProviderVoiceRecord) -> AVSpeechSynthesisProviderVoice? {
        guard record.readiness == .ready else { return nil }
        guard !record.id.isEmpty, !record.primaryLanguages.isEmpty else { return nil }

        return AVSpeechSynthesisProviderVoice(
            name: record.localizedName,
            identifier: record.id,
            primaryLanguages: record.primaryLanguages,
            supportedLanguages: record.supportedLanguages
        )
    }
}

final class ProviderVoiceInventory {
    var voices: [AVSpeechSynthesisProviderVoice] {
        let snapshot = ProviderCatalogStore.load()
        return snapshot?.voices.compactMap(ProviderVoiceFactory.makeVoice(from:)) ?? []
    }
}
~~~

If the final SDK exposes a failable initializer or a different availability annotation, keep the validation boundary and adjust the call site to the SDK. Never report an unavailable voice merely because its catalog record exists.

## 4. Provider Audio Unit skeleton

The provider receives a request on the control side, exposes a voice inventory, and cancels the current generation. The render implementation is deliberately represented as a handoff to a preallocated render state; it must be completed against the selected `AUInternalRenderBlock` signature in the final SDK.

~~~swift
import AVFAudio
import AudioToolbox
import Foundation

final class CustomSpeechProviderAudioUnit: AVSpeechSynthesisProviderAudioUnit {
    private let inventory = ProviderVoiceInventory()
    private let renderState = ProviderRenderState()

    override var speechVoices: [AVSpeechSynthesisProviderVoice] {
        inventory.voices
    }

    override func synthesizeSpeechRequest(
        _ speechRequest: AVSpeechSynthesisProviderRequest
    ) {
        let voiceID = speechRequest.voice.identifier
        let ssml = speechRequest.ssmlRepresentation

        // Control-side work: validate voice/resource/SSML and stage a new generation.
        renderState.beginRequest(
            voiceID: voiceID,
            ssml: ssml,
            resourceRevision: ProviderCatalogStore.load()?.revision
        )
    }

    override func cancelSpeechRequest() {
        renderState.cancelCurrentRequest()
    }

    // The subclass must provide the documented AUAudioUnit internal render path.
    // Keep the returned block bounded, allocation-free after resource allocation,
    // and independent from SwiftUI, networking, files, and model inference.
    override var internalRenderBlock: AUInternalRenderBlock {
        renderState.internalRenderBlock
    }
}
~~~

The extension factory and `AudioComponents` `Info.plist` entry are target configuration, not SwiftUI code. Keep component identity, extension registration, signing, and target membership in the route record.

## 5. Generation-aware render state

A late render callback must not publish audio or markers from a cancelled request. The exact buffer implementation depends on the provider’s synthesizer and sample format; the generation boundary is the reusable part.

~~~swift
import AudioToolbox
import Foundation

final class ProviderRenderState: @unchecked Sendable {
    private let lock = NSLock()
    private var generation: UInt64 = 0
    private var active: PreparedRequest?

    struct PreparedRequest: Sendable {
        let generation: UInt64
        let voiceID: String
        let ssml: String
        let resourceRevision: UInt64?
    }

    func beginRequest(voiceID: String, ssml: String, resourceRevision: UInt64?) {
        lock.lock()
        generation &+= 1
        active = PreparedRequest(
            generation: generation,
            voiceID: voiceID,
            ssml: ssml,
            resourceRevision: resourceRevision
        )
        lock.unlock()

        // Parse and stage local resources outside the render callback.
    }

    func cancelCurrentRequest() {
        lock.lock()
        generation &+= 1
        active = nil
        lock.unlock()
    }

    var internalRenderBlock: AUInternalRenderBlock {
        // Replace this placeholder with the final SDK's exact render closure.
        // The closure should read a preallocated snapshot, render bounded frames,
        // emit silence or the documented completion status for stale generations,
        // and never call these lock-taking control methods.
        return { _, _, _, _, _, _, _ in
            noErr
        }
    }
}
~~~

`NSLock` is shown only for the control-side sketch. Do not copy it into a render callback. A real provider needs a lock-free or otherwise documented real-time-safe handoff from preparation to rendering, with preallocated buffers and an explicit resource lifecycle.

## 6. Provider markers

Markers use text ranges and byte sample offsets. Build them from the same source-to-buffer map used by the synthesis plan.

~~~swift
import AVFAudio
import Foundation

func makeWordMarker(
    utf16Location: Int,
    utf16Length: Int,
    byteSampleOffset: Int
) -> AVSpeechSynthesisMarker {
    AVSpeechSynthesisMarker(
        wordRange: NSRange(location: utf16Location, length: utf16Length),
        atByteSampleOffset: byteSampleOffset
    )
}

func sendMarkers(
    _ markers: [AVSpeechSynthesisMarker],
    through output: AVSpeechSynthesisProviderOutputBlock?
) {
    output?(markers)
}
~~~

The provider can send word, sentence, paragraph, phoneme, or bookmark markers. Test the range after SSML tags are removed and the offset after the output format is fixed. If additional processing changes marker timing, send replacement metadata for the same buffer range and generation instead of appending contradictory markers.

## 7. Request cancellation with a typed record

Keep cancellation observable in diagnostics without retaining the request’s private source longer than needed.

~~~swift
struct ProviderRequestRecord: Sendable, Equatable {
    let generation: UInt64
    let voiceID: String
    let sourceRevision: String?
    let ssmlHash: String
    var state: State

    enum State: Sendable, Equatable {
        case preparing
        case rendering
        case cancelled
        case completed
        case failed(String)
    }
}
~~~

Store a hash or diagnostic identifier instead of raw private text when logs do not need the text. A request that is `cancelled` must not later become `completed` because a background worker finished after the system replaced it.

## 8. Host SwiftUI voice-management surface

The host can use Liquid Glass around the functional controls while keeping the voice catalog readable and accessible.

~~~swift
import SwiftUI

struct ProviderVoiceRow: View {
    let record: ProviderVoiceRecord
    let preview: () -> Void
    let publish: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(record.localizedName)
                    .font(.headline)
                Text(record.primaryLanguages.joined(separator: ", "))
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                Text(statusText)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Menu {
                Button("Preview in This App", action: preview)
                Button("Publish Voice", action: publish)
            } label: {
                Image(systemName: "ellipsis.circle")
            }
            .accessibilityLabel("Actions for \(record.localizedName)")
        }
        .accessibilityElement(children: .combine)
        .accessibilityValue(statusText)
    }

    private var statusText: String {
        switch record.readiness {
        case .ready: return "Ready for system publication"
        case .installing: return "Preparing voice resource"
        case .unavailable: return "Voice resource unavailable"
        case .retired: return "Voice retired; choose a replacement"
        }
    }
}

struct ProviderToolbar: View {
    let refresh: () -> Void

    var body: some View {
        Button("Refresh System Voice List", systemImage: "arrow.clockwise", action: refresh)
            .buttonStyle(.borderedProminent)
            .glassEffect(.regular.interactive(), in: .capsule)
            .accessibilityHint("Asks the system to refresh voices provided by this app")
    }
}
~~~

Use a real state model for `refreshPending`, `systemVisible`, `previewing`, and `resourceFailure`; do not make the `glassEffect` modifier imply that a voice is available.

## 9. Optional typed pronunciation proposal

If the host app offers on-device AI help, constrain it to a reviewable proposal. The provider extension must remain functional without a model session.

~~~swift
import FoundationModels

@Generable
struct PronunciationProposal {
    @Guide(description: "A short SSML fragment using only the app's supported tags")
    var ssmlFragment: String

    @Guide(description: "A brief explanation of the proposed pronunciation change")
    var explanation: String
}

func acceptProposal(
    _ proposal: PronunciationProposal,
    originalText: String,
    validate: (String) -> Bool
) -> String? {
    guard validate(proposal.ssmlFragment) else { return nil }
    // The caller should show the original and proposed text and obtain acceptance.
    return proposal.ssmlFragment
}
~~~

Store model availability, proposal revision, source revision, validation result, and user acceptance. Never let a model call `synthesizeSpeechRequest`, change provider voice inventory, or bypass the no-network rule.

## 10. Swift Testing boundaries

Deterministic tests can cover catalog, generation, SSML policy, and marker math. Physical tests are still required for system discovery and audible output.

~~~swift
import Testing

struct ProviderGenerationTests {
    @Test func cancellationInvalidatesEarlierGeneration() {
        let state = ProviderRenderState()
        state.beginRequest(voiceID: "voice.en", ssml: "<speak>one</speak>", resourceRevision: 1)
        state.cancelCurrentRequest()
        state.beginRequest(voiceID: "voice.en", ssml: "<speak>two</speak>", resourceRevision: 2)

        // Assert through the production state inspection/diagnostic seam that only
        // the second generation can publish frames and markers.
    }
}
~~~

Add separate integration fixtures for the archived host/extension pair, system Spoken Content inventory, VoiceOver, Speak Screen, route interruption, and physical speaker/headphone output.

## Sources

- [Creating a custom speech synthesizer](https://developer.apple.com/documentation/avfaudio/creating-a-custom-speech-synthesizer)
- [Creating an audio unit extension](https://developer.apple.com/documentation/avfaudio/creating-an-audio-unit-extension)
- [AVSpeechSynthesisProviderAudioUnit](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit)
- [AVSpeechSynthesisProviderRequest](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisproviderrequest)
- [AVSpeechSynthesisProviderVoice](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovidervoice)
- [AVSpeechSynthesisProviderVoice.updateSpeechVoices()](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovidervoice/updatespeechvoices%28%29)
- [AVSpeechSynthesisMarker](https://developer.apple.com/documentation/avfaudio/avspeechsynthesismarker)
- [speechSynthesisOutputMetadataBlock](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit/speechsynthesisoutputmetadatablock)
- [synthesizeSpeechRequest(_:)](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit/synthesizespeechrequest%28_%3A%29)
- [cancelSpeechRequest()](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit/cancelspeechrequest%28%29)
- [AUAudioUnit](https://developer.apple.com/documentation/audiotoolbox/auaudiounit)
- [AUAudioUnit.renderBlock](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/renderblock)
- [AUInternalRenderBlock](https://developer.apple.com/documentation/audiotoolbox/auinternalrenderblock)
- [AUAudioUnit.renderingOffline](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/isrenderingoffline)
- [VoiceOver](https://developer.apple.com/documentation/accessibility/voiceover/)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
