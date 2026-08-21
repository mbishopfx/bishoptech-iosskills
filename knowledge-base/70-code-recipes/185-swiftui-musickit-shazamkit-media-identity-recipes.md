# SwiftUI MusicKit, ShazamKit, and media-identity recipes

These snippets target the installed iOS 26.4 simulator SDK. They show the
current API shape and state boundaries; they are not a complete entitlement,
privacy, audio-engine, Apple Music account, or App Store implementation. Each
`~~~swift` block is intentionally independent and compile-sized.

## 1. Request MusicKit authorization from a route

Permission is a runtime state, not a launch-time boolean. Keep denied and
restricted paths visible to the caller.

~~~swift
import Foundation
import MusicKit

@available(iOS 26.0, *)
func requestMusicAccess() async -> MusicAuthorization.Status {
    switch MusicAuthorization.currentStatus {
    case .notDetermined:
        return await MusicAuthorization.request()
    case .authorized, .denied, .restricted:
        return MusicAuthorization.currentStatus
    @unknown default:
        return MusicAuthorization.currentStatus
    }
}
~~~

## 2. Read subscription capabilities

Authorization and subscription are different checks. Re-evaluate capabilities
before playback or library work that has a user-visible side effect.

~~~swift
import MusicKit

@available(iOS 26.0, *)
func readMusicCapabilities() async throws -> MusicSubscription {
    try await MusicSubscription.current
}
~~~

## 3. Search the Apple Music catalog

Limit the request and keep the typed result collection separate from any
personal-library state.

~~~swift
import MusicKit

@available(iOS 26.0, *)
func searchCatalog(term: String) async throws -> MusicItemCollection<Song> {
    var request = MusicCatalogSearchRequest(term: term, types: [Song.self])
    request.limit = 10
    let response = try await request.response()
    return response.songs
}
~~~

## 4. Resolve a catalog resource with a typed filter

An empty response is a valid route result. Do not turn a title/artist guess
into a stable music identifier.

~~~swift
import Foundation
import MusicKit

@available(iOS 26.0, *)
func resolveCatalogSong(id: MusicItemID) async throws -> Song {
    let request = MusicCatalogResourceRequest<Song>(
        matching: \SongFilter.id,
        equalTo: id
    )
    let response = try await request.response()
    guard let song = response.items.first else {
        throw NSError(domain: "MediaRoute", code: 404)
    }
    return song
}
~~~

## 5. Read the person’s MusicKit library

The library request is user-scoped. It should run only after the app’s
MusicKit authorization route has reached an appropriate state.

~~~swift
import MusicKit

@available(iOS 26.0, *)
func readLibrarySongs() async throws -> MusicItemCollection<Song> {
    var request = MusicLibraryRequest<Song>()
    request.limit = 20
    let response = try await request.response()
    return response.items
}
~~~

## 6. Use an app-owned MusicKit player

`ApplicationMusicPlayer` owns an app-local queue and does not change the Music
app’s state. Still handle subscription, route, interruption, and playback
errors in the surrounding coordinator.

~~~swift
import MusicKit

@available(iOS 26.0, *)
func playInApplicationPlayer(songs: MusicItemCollection<Song>) async throws {
    let player = ApplicationMusicPlayer.shared
    player.queue = ApplicationMusicPlayer.Queue(for: songs)
    try await player.prepareToPlay()
    try await player.play()
}
~~~

## 7. Use the system Music player intentionally

`SystemMusicPlayer` controls the Music app’s state. The UI should explain that
the operation may affect the external Music experience.

~~~swift
import MusicKit

@available(iOS 26.0, *)
func playInSystemPlayer(song: Song) async throws {
    let player = SystemMusicPlayer.shared
    player.queue = MusicPlayer.Queue(for: [song])
    try await player.prepareToPlay()
    try await player.play()
}
~~~

## 8. Load a typed response from an Apple Music API endpoint

`MusicDataRequest` can load an arbitrary endpoint. Keep URL construction,
storefront, token policy, and response decoding in a service layer; never put
private MusicKit signing material in the app bundle.

~~~swift
import Foundation
import MusicKit

@available(iOS 26.0, *)
func loadMusicData(from url: URL) async throws -> Data {
    let request = MusicDataRequest(urlRequest: URLRequest(url: url))
    let response = try await request.response()
    return response.data
}
~~~

## 9. Match a generated Shazam signature

`SHSession.Result` forces the caller to distinguish match, no-match, and
framework error.

~~~swift
import ShazamKit

@available(iOS 26.0, *)
func matchSignature(_ signature: SHSignature) async -> SHSession.Result {
    let session = SHSession()
    return await session.result(from: signature)
}
~~~

## 10. Generate a signature from an audio buffer

The buffer must use a supported PCM format and a continuous time position.
Validate duration against the active catalog before matching.

~~~swift
import AVFAudio
import ShazamKit

@available(iOS 26.0, *)
func makeSignature(
    from buffer: AVAudioPCMBuffer,
    at time: AVAudioTime?
) throws -> SHSignature {
    let generator = SHSignatureGenerator()
    try generator.append(buffer, at: time)
    return generator.signature()
}
~~~

## 11. Use a managed ShazamKit session

The managed session owns the managed recording/match lifecycle. Tie
`cancel()` to the view task and Stop action, and render `state`/`results` in a
separate observable route store.

~~~swift
import ShazamKit

@available(iOS 26.0, *)
func runManagedMatch() async -> SHSession.Result {
    let session = SHManagedSession()
    await session.prepare()
    let result = await session.result()
    session.cancel()
    return result
}
~~~

## 12. Build a custom ShazamKit catalog

Reference signatures and metadata must come from audio the product has the
right to process. The catalog does not grant Apple Music playback rights.

~~~swift
import ShazamKit

@available(iOS 26.0, *)
func makeCustomCatalog(
    signature: SHSignature,
    title: String,
    artist: String
) throws -> SHCustomCatalog {
    let item = SHMediaItem(properties: [
        .title: title,
        .artist: artist
    ])
    let catalog = SHCustomCatalog()
    try catalog.addReferenceSignature(signature, representing: [item])
    return catalog
}
~~~

## 13. Configure microphone input and permission

The mixer converts the input path to a ShazamKit-friendly format. A real app
must own teardown, handle route/interruption notifications, and add a truthful
`NSMicrophoneUsageDescription` value.

~~~swift
import AVFAudio

@available(iOS 26.0, *)
func configureMicrophoneEngine() throws -> AVAudioEngine {
    let audioSession = AVAudioSession.sharedInstance()
    try audioSession.setCategory(.playAndRecord)

    let engine = AVAudioEngine()
    let mixer = AVAudioMixerNode()
    let inputFormat = engine.inputNode.inputFormat(forBus: 0)
    let outputFormat = AVAudioFormat(standardFormatWithSampleRate: 48_000, channels: 1)!

    engine.attach(mixer)
    engine.connect(engine.inputNode, to: mixer, format: inputFormat)
    engine.connect(mixer, to: engine.outputNode, format: outputFormat)
    mixer.installTap(onBus: 0, bufferSize: 8192, format: outputFormat) { _, _ in }
    return engine
}

@available(iOS 26.0, *)
func requestMicrophoneAccess(completion: @escaping (Bool) -> Void) {
    AVAudioApplication.requestRecordPermission(completionHandler: completion)
}
~~~

## 14. Keep an AI explanation typed and source-bound

This boundary can be fed to an available on-device model or a deterministic
fallback. It does not grant the model authority to identify, play, or mutate
music state.

~~~swift
import ShazamKit

struct MediaExplanationProposal: Codable, Sendable {
    let title: String
    let artist: String
    let explanation: String
    let sourceID: String
}

func makeExplanationProposal(
    for item: SHMediaItem,
    explanation: String
) -> MediaExplanationProposal? {
    guard
        let title = item.title,
        let artist = item.artist,
        let sourceID = item.shazamID
    else {
        return nil
    }

    return MediaExplanationProposal(
        title: title,
        artist: artist,
        explanation: explanation,
        sourceID: sourceID
    )
}
~~~

The proposal is generated text. Before displaying or accepting it, validate
length and source identity, mark it as generated, and keep Play/Add/Open on a
deterministic user-action path.

## Verification notes

Typecheck each fenced block independently against the installed iOS 26.4
simulator SDK. Then verify on a physical device with the configured MusicKit
and ShazamKit App ID services, real music account, microphone permission, and
audio route. The simulator is compile/UI evidence only for protected media and
physical audio behavior.

## Sources

- [MusicKit](https://developer.apple.com/documentation/musickit)
- [MusicAuthorization](https://developer.apple.com/documentation/musickit/musicauthorization)
- [MusicSubscription](https://developer.apple.com/documentation/musickit/musicsubscription)
- [MusicCatalogSearchRequest](https://developer.apple.com/documentation/musickit/musiccatalogsearchrequest)
- [MusicCatalogResourceRequest](https://developer.apple.com/documentation/musickit/musiccatalogresourcerequest)
- [MusicLibraryRequest](https://developer.apple.com/documentation/musickit/musiclibraryrequest)
- [MusicLibrary](https://developer.apple.com/documentation/musickit/musiclibrary)
- [ApplicationMusicPlayer](https://developer.apple.com/documentation/musickit/applicationmusicplayer)
- [SystemMusicPlayer](https://developer.apple.com/documentation/musickit/systemmusicplayer)
- [MusicDataRequest](https://developer.apple.com/documentation/musickit/musicdatarequest)
- [User Authentication for MusicKit](https://developer.apple.com/documentation/applemusicapi/user-authentication-for-musickit)
- [Handling Requests and Responses](https://developer.apple.com/documentation/applemusicapi/handling-requests-and-responses)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)
- [SHManagedSession](https://developer.apple.com/documentation/shazamkit/shmanagedsession)
- [SHCustomCatalog](https://developer.apple.com/documentation/shazamkit/shcustomcatalog)
- [SHSignatureGenerator](https://developer.apple.com/documentation/shazamkit/shsignaturegenerator)
- [SHMediaItem](https://developer.apple.com/documentation/shazamkit/shmediaitem)
- [Matching audio using the built-in microphone](https://developer.apple.com/documentation/shazamkit/matching-audio-using-the-built-in-microphone)
- [Enable ShazamKit for an App ID](https://developer.apple.com/help/account/configure-app-services/shazamkit)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [NSAppleMusicUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapplemusicusagedescription)
- [NSMicrophoneUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nsmicrophoneusagedescription)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
