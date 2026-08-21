# NFC, MusicKit, and ShazamKit recipes

## Compile boundary

These are compile-oriented route sketches for Core NFC, MusicKit, ShazamKit, microphone capture, candidate review, and bounded AI enrichment. They are not compiled in this documentation workspace and do not prove NFC hardware, tag protocol behavior, MusicKit accounts/subscriptions, playback, microphone capture, catalog matches, entitlements, privacy, or release readiness.

## Recipe 1: start an NDEF reader session

Start the session from an explicit user action after checking hardware support:

~~~swift
import CoreNFC

final class NDEFReader: NSObject, NFCNDEFReaderSessionDelegate {
    private var session: NFCNDEFReaderSession?

    func begin() {
        guard NFCNDEFReaderSession.readingAvailable else {
            publish(.unsupported)
            return
        }

        let reader = NFCNDEFReaderSession(
            delegate: self,
            queue: nil,
            invalidateAfterFirstRead: true
        )
        reader.alertMessage = "Hold iPhone near the item to read it."
        session = reader
        reader.begin()
    }

    func readerSessionDidBecomeActive(
        _ session: NFCNDEFReaderSession
    ) {
        publish(.active)
    }

    func readerSession(
        _ session: NFCNDEFReaderSession,
        didDetectNDEFs messages: [NFCNDEFMessage]
    ) {
        publish(.candidate(messages))
    }

    func readerSession(
        _ session: NFCNDEFReaderSession,
        didInvalidateWithError error: Error
    ) {
        publish(.invalidated(String(describing: error)))
    }

    private func publish(_ state: ReaderState) {
        // Send a value to the main-actor presentation model.
    }
}
~~~

The exact delegate method availability and imported protocol signatures must be checked in the target SDK. Do not open a URL or perform a domain mutation directly inside the tag callback.

## Recipe 2: parse an NDEF candidate

Treat payload data as untrusted:

~~~swift
struct TagCandidate: Sendable, Equatable {
    let recordType: String
    let payloadSummary: String
    let validatedURL: URL?
    let rawRecordCount: Int
}

func makeCandidate(
    from message: NFCNDEFMessage
) -> TagCandidate {
    let url = message.records
        .compactMap { record in
            URL(string: String(data: record.payload, encoding: .utf8) ?? "")
        }
        .first(where: { url in
            url.scheme == "https" &&
            url.host != nil
        })

    return TagCandidate(
        recordType: "NDEF",
        payloadSummary: "Review \(message.records.count) record(s)",
        validatedURL: url,
        rawRecordCount: message.records.count
    )
}
~~~

This is only a sketch; real NDEF URI/text decoding should use the record type and payload rules for the supported format. Validate scheme, host, size, encoding, version, and app-owned identifiers before navigation or mutation.

## Recipe 3: preview a tag write

Make physical mutation explicit:

~~~swift
struct TagWriteProposal: Sendable, Equatable {
    let messageDescription: String
    let payload: NFCNDEFMessage
    let source: String
}

enum TagWriteState: Equatable {
    case needsConfirmation(TagWriteProposal)
    case writing
    case written
    case failed
}
~~~

The confirmation button should say what will be written. After the tag is detected, perform the write through the supported NDEF tag interface, handle tag loss/capacity, and read back where the protocol supports verification. Keep the original proposal until the result is known.

## Recipe 4: request MusicKit authorization and search

Request access before the first MusicKit operation:

~~~swift
import MusicKit

func authorizeMusic() async -> MusicAuthorization.Status {
    await MusicAuthorization.request()
}

func searchSongs(
    for term: String
) async throws -> MusicCatalogSearchResponse {
    var request = MusicCatalogSearchRequest(
        term: term,
        types: [Song.self]
    )
    request.limit = 10
    request.includeTopResults = true
    return try await request.response()
}
~~~

Add NSAppleMusicUsageDescription to the app target. Handle denied/restricted status, empty responses, network errors, catalog availability, and subscription/playback differences. Preserve catalog identifiers rather than using title/artist text as stable identity.

## Recipe 5: play with the app-owned player

ApplicationMusicPlayer keeps the app’s playback state separate from the Music app:

~~~swift
import MusicKit

func playSong(_ song: Song) async throws {
    let player = ApplicationMusicPlayer.shared
    player.queue = [song]
    try await player.prepareToPlay()
    try await player.play()
}
~~~

The song must be playable in the current account/subscription state. Handle playback errors, interruptions, route changes, stop/pause, and background audio configuration. If the desired behavior is to control the Music app, use SystemMusicPlayer and design a different state/reconciliation contract.

## Recipe 6: match a controlled signature with ShazamKit

Use a saved signature when the input is deterministic:

~~~swift
import ShazamKit

func match(
    signature: SHSignature,
    catalog: SHCatalog? = nil
) async -> SHSession.Result {
    let session: SHSession
    if let catalog {
        session = SHSession(catalog: catalog)
    } else {
        session = SHSession()
    }
    return await session.result(from: signature)
}
~~~

Handle match, noMatch, and error cases as separate states. A matched SHMediaItem is candidate metadata, not user-confirmed fact.

## Recipe 7: stream microphone audio to ShazamKit

The audio engine route needs microphone permission and a real AVAudioEngine configuration:

~~~swift
import AVFAudio
import ShazamKit

final class AudioMatcher {
    private let audioEngine = AVAudioEngine()
    private let mixerNode = AVAudioMixerNode()
    private let session = SHSession()

    func start() throws {
        let input = audioEngine.inputNode
        let format = input.inputFormat(forBus: 0)

        audioEngine.attach(mixerNode)
        audioEngine.connect(
            input,
            to: mixerNode,
            format: format
        )

        mixerNode.installTap(
            onBus: 0,
            bufferSize: 4096,
            format: mixerNode.outputFormat(forBus: 0)
        ) { [weak self] buffer, time in
            self?.session.matchStreamingBuffer(buffer, at: time)
        }

        try audioEngine.start()
    }

    func stop() {
        mixerNode.removeTap(onBus: 0)
        audioEngine.stop()
    }
}
~~~

Configure and activate AVAudioSession in the app target, request microphone permission, handle interruptions/route changes, and stop the audio engine after match/cancel/error. The code does not prove the format is compatible or that capture is privacy-safe.

## Recipe 8: preserve match provenance

Persist a candidate before any AI enrichment:

~~~swift
struct AudioCandidate: Sendable, Codable, Equatable {
    let source: String
    let catalog: String
    let mediaIdentifier: String?
    let title: String?
    let creator: String?
    let capturedAt: Date
    let confidenceLanguage: String
    var reviewState: String
}
~~~

Keep the raw source kind and catalog version. If a later catalog update changes the result, show the person that the candidate was refreshed rather than silently overwriting a confirmed record.

## Recipe 9: create a bounded AI proposal

Use a proposal type that cannot be mistaken for domain truth:

~~~swift
struct MediaProposal: Sendable, Equatable {
    let sourceCandidate: AudioCandidate
    let proposedTitle: String
    let proposedCollection: String?
    let rationale: String
    let generatedBy: String
    var accepted: Bool
}

func accept(
    _ proposal: MediaProposal,
    currentCandidate: AudioCandidate
) -> Bool {
    proposal.sourceCandidate == currentCandidate &&
    proposal.accepted
}
~~~

The app should validate collection identifiers, permission, subscription, and current source before adding to a library, starting playback, sharing, syncing, or writing a tag.

## Recipe 10: test hardware and fallback

Use a matrix instead of a single “works” check:

~~~text
NFC:
  unsupported device
  user cancels
  one NDEF tag
  multiple tags
  malformed payload
  tag lost during read/write
  capacity exceeded
  background invocation

MusicKit:
  not determined
  authorized
  denied/restricted
  catalog empty/network failure
  library item missing
  subscription unavailable
  application player interruption
  system player state change

ShazamKit:
  no microphone
  silence/noise
  no match
  match
  custom catalog mismatch
  audio interruption
  stop after match
~~~

The UI must offer manual or saved routes where the product can still provide value without the protected capability.

## Recipe 11: verification stop list

1. Compile Core NFC, MusicKit, and ShazamKit in the named target.
2. Inspect usage descriptions, entitlements, MusicKit service configuration, and catalog resources.
3. Test on physical devices with real tags and audio.
4. Separate catalog search, library access, playback, and match evidence.
5. Test malformed/cancelled/no-match/denied/interrupted states.
6. Verify VoiceOver, Dynamic Type, reduced transparency, Reduce Motion, and manual entry.
7. Keep AI proposals editable and preserve provenance.
8. Test the archive/release artifact separately from development fixtures.

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [Building an NFC Tag-Reader App](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcndefreadersessiondelegate)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [MusicKit](https://developer.apple.com/documentation/musickit)
- [MusicAuthorization](https://developer.apple.com/documentation/musickit/musicauthorization)
- [MusicCatalogSearchRequest](https://developer.apple.com/documentation/musickit/musiccatalogsearchrequest)
- [ApplicationMusicPlayer](https://developer.apple.com/documentation/musickit/applicationmusicplayer)
- [SystemMusicPlayer](https://developer.apple.com/documentation/musickit/systemmusicplayer)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)
- [SHManagedSession](https://developer.apple.com/documentation/shazamkit/shmanagedsession)
- [Matching audio using the built-in microphone](https://developer.apple.com/documentation/shazamkit/matching-audio-using-the-built-in-microphone)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioPCMBuffer](https://developer.apple.com/documentation/avfaudio/avaudiopcmbuffer)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
