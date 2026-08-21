# SwiftUI Core NFC tag-session code recipes

These are compile-oriented Swift sketches for [the Core NFC framework review](../42-framework-deep-dives/120-swiftui-core-nfc-tag-session-review.md). They cover the reader lanes, not a finished app. Compile every selected API against the exact iOS 26 SDK and keep the physical-device proof in the [Core NFC proof matrix](../60-verification/145-swiftui-core-nfc-tag-session-proof-matrix.md).

The sketches intentionally separate raw framework objects, bounded value state, deterministic decoding, AI proposals, review, and side effects. Do not copy a recipe into production without adding entitlement inspection, privacy review, cancellation, accessibility, and physical fixtures.

## Recipe 1: route and availability state

Keep the selected route explicit:

~~~swift
import CoreNFC
import Foundation

enum NFCRoute: Sendable, Hashable {
    case ndefRead
    case ndefWrite
    case protocolTag
    case backgroundURI
    case cardSession
}

enum NFCFeatureAvailability: Sendable, Equatable {
    case checking
    case unsupported
    case configurationRequired
    case restricted
    case ready
}

@MainActor
func readerAvailability() -> NFCFeatureAvailability {
    guard NFCReaderSession.readingAvailable else {
        return .unsupported
    }
    return .ready
}

@MainActor
func cardAvailability() -> NFCFeatureAvailability {
    guard NFCReaderSession.readingAvailable else {
        return .unsupported
    }
    guard CardSession.isSupported else {
        return .unsupported
    }
    guard CardSession.isEligible else {
        return .restricted
    }
    return .ready
}
~~~

Availability is a runtime gate, not proof that the signed app contains the required entitlement. CardSession has separate support and eligibility checks. Check all route-specific gates immediately before starting.

## Recipe 2: value state and generation

Framework objects should not leak into persisted models:

~~~swift
import Foundation

struct NFCRecordEnvelope: Sendable, Hashable {
    let index: Int
    let typeNameFormat: UInt8
    let type: Data
    let identifier: Data
    let payload: Data
    let payloadDigest: String
}

struct NFCSourceEnvelope: Sendable, Hashable {
    let id: UUID
    let route: String
    let generation: UInt64
    let capturedAt: Date
    let records: [NFCRecordEnvelope]
}

enum NFCReviewState: Sendable, Equatable {
    case idle
    case active
    case reading
    case reviewing(NFCSourceEnvelope)
    case failed(String)
    case cancelled
}

@MainActor
final class NFCFeatureModel: ObservableObject {
    @Published private(set) var state: NFCReviewState = .idle
    private(set) var generation: UInt64 = 0

    func begin() -> UInt64 {
        generation &+= 1
        state = .active
        return generation
    }

    func cancel() {
        generation &+= 1
        state = .cancelled
    }

    func accepts(_ callbackGeneration: UInt64) -> Bool {
        callbackGeneration == generation
    }
}
~~~

If the project uses the Observation framework instead of ObservableObject, preserve the same ownership rules: the model owns values, while the coordinator owns the live session.

## Recipe 3: NDEF reader coordinator

This is the one-shot message-reading lane:

~~~swift
import CoreNFC
import Foundation

@MainActor
final class NDEFReaderCoordinator: NSObject, NFCNDEFReaderSessionDelegate {
    private var session: NFCNDEFReaderSession?
    private let callbackQueue = DispatchQueue(label: "nfc.ndef.reader")
    private var generation: UInt64 = 0
    private let onMessages: @MainActor ([NFCNDEFMessage], UInt64) -> Void
    private let onFailure: @MainActor (Error, UInt64) -> Void

    init(
        onMessages: @escaping @MainActor ([NFCNDEFMessage], UInt64) -> Void,
        onFailure: @escaping @MainActor (Error, UInt64) -> Void
    ) {
        self.onMessages = onMessages
        self.onFailure = onFailure
    }

    func start(generation: UInt64) {
        stop()
        self.generation = generation

        let newSession = NFCNDEFReaderSession(
            delegate: self,
            queue: callbackQueue,
            invalidateAfterFirstRead: true
        )
        newSession.alertMessage = "Hold the top of iPhone near the NFC tag."
        session = newSession
        newSession.begin()
    }

    func stop() {
        session?.invalidate()
        session = nil
    }

    nonisolated func readerSessionDidBecomeActive(
        _ session: NFCNDEFReaderSession
    ) {
        // The session is ready; no tag has been read yet.
    }

    nonisolated func readerSession(
        _ session: NFCNDEFReaderSession,
        didDetectNDEFs messages: [NFCNDEFMessage]
    ) {
        Task { @MainActor [weak self] in
            guard let self else { return }
            onMessages(messages, generation)
        }
    }

    nonisolated func readerSession(
        _ session: NFCNDEFReaderSession,
        didInvalidateWithError error: Error
    ) {
        Task { @MainActor [weak self] in
            guard let self else { return }
            self.session = nil
            self.onFailure(error, self.generation)
        }
    }
}
~~~

The exact actor annotations and delegate isolation can vary by SDK. Compile the coordinator with the selected concurrency checking mode. The important behavior is that the live session remains retained, callbacks are converted into value events, and invalidation clears ownership.

## Recipe 4: NDEF message and payload envelope

Capture every record before decoding convenience values:

~~~swift
import CryptoKit
import CoreNFC
import Foundation

func digest(_ data: Data) -> String {
    SHA256.hash(data: data)
        .map { String(format: "%02x", $0) }
        .joined()
}

func envelope(
    from message: NFCNDEFMessage
) -> [NFCRecordEnvelope] {
    message.records.enumerated().map { index, record in
        NFCRecordEnvelope(
            index: index,
            typeNameFormat: record.typeNameFormat.rawValue,
            type: record.type,
            identifier: record.identifier,
            payload: record.payload,
            payloadDigest: digest(record.payload)
        )
    }
}

struct DecodedNDEF: Sendable, Equatable {
    let index: Int
    let kind: String
    let text: String?
    let url: URL?
}

func decode(
    message: NFCNDEFMessage,
    maxTextLength: Int = 4_096
) -> [DecodedNDEF] {
    message.records.enumerated().map { index, record in
        let textPair = record.wellKnownTypeTextPayload()
        if let text = textPair.0, text.utf8.count <= maxTextLength {
            return DecodedNDEF(
                index: index,
                kind: "well-known-text",
                text: text,
                url: nil
            )
        }

        if let url = record.wellKnownTypeURIPayload() {
            return DecodedNDEF(
                index: index,
                kind: "well-known-uri",
                text: nil,
                url: url
            )
        }

        return DecodedNDEF(
            index: index,
            kind: "unsupported-or-custom",
            text: nil,
            url: nil
        )
    }
}
~~~

For a production decoder, bound record count, type size, identifier size, and total message length before allocating or displaying content. The envelope retains raw fields while the decoded type is only a proposal.

## Recipe 5: validate a URI before opening it

Treat a decoded URL as untrusted:

~~~swift
import Foundation

enum URLPolicyError: Error {
    case invalidScheme
    case invalidHost
    case invalidPath
    case tooLong
}

func validatedAppURL(
    _ url: URL,
    allowedHost: String
) throws -> URL {
    guard url.absoluteString.utf8.count <= 2_048 else {
        throw URLPolicyError.tooLong
    }
    guard url.scheme?.lowercased() == "https" else {
        throw URLPolicyError.invalidScheme
    }
    guard url.host?.lowercased() == allowedHost.lowercased() else {
        throw URLPolicyError.invalidHost
    }
    guard url.path.hasPrefix("/items/") else {
        throw URLPolicyError.invalidPath
    }
    return url
}
~~~

Do not call open, navigate, or perform a network mutation before validation and explicit user intent. If the background route can open Safari, apply a similarly strict policy before showing an app action.

## Recipe 6: connect to an NDEF tag for status and write

The delegate overload that reports NFCNDEFTag is useful for a write-capable flow. The exact async/completion-handler spelling is SDK-sensitive, so keep the framework call in one adapter:

~~~swift
import CoreNFC
import Foundation

struct NDEFWritePlan: Sendable {
    let message: NFCNDEFMessage
    let proposedLength: Int
}

@MainActor
final class NDEFTagAdapter {
    func inspect(
        tag: NFCNDEFTag,
        plan: NDEFWritePlan
    ) async throws -> NFCNDEFStatus {
        try await withCheckedThrowingContinuation { continuation in
            tag.queryNDEFStatus { status, capacity, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }

                guard status == .readWrite else {
                    continuation.resume(returning: status)
                    return
                }

                guard plan.proposedLength <= capacity else {
                    continuation.resume(
                        throwing: NSError(
                            domain: "NFCWritePlan",
                            code: 1,
                            userInfo: [NSLocalizedDescriptionKey: "Message exceeds tag capacity."]
                        )
                    )
                    return
                }

                continuation.resume(returning: status)
            }
        }
    }

    func write(
        tag: NFCNDEFTag,
        plan: NDEFWritePlan
    ) async throws {
        try await withCheckedThrowingContinuation { continuation in
            tag.writeNDEF(plan.message) { error in
                if let error {
                    continuation.resume(throwing: error)
                } else {
                    continuation.resume()
                }
            }
        }
    }
}
~~~

Compile the continuation against the current SDK because callback parameter types and Swift concurrency overlays can change. Query status and capacity after connecting, not from an earlier tag detection. Keep writeLock in a different method and behind a separate destructive confirmation.

## Recipe 7: generic tag-reader coordinator

Use the generic session only when the feature needs protocol adapters:

~~~swift
import CoreNFC
import Foundation

@MainActor
final class TagReaderCoordinator: NSObject, NFCTagReaderSessionDelegate {
    private var session: NFCTagReaderSession?
    private let queue = DispatchQueue(label: "nfc.tag.reader")
    private var generation: UInt64 = 0
    private let onTag: @MainActor (NFCTag, UInt64) -> Void
    private let onError: @MainActor (Error, UInt64) -> Void

    init(
        onTag: @escaping @MainActor (NFCTag, UInt64) -> Void,
        onError: @escaping @MainActor (Error, UInt64) -> Void
    ) {
        self.onTag = onTag
        self.onError = onError
    }

    func start(generation: UInt64) {
        stop()
        self.generation = generation
        let newSession = NFCTagReaderSession(
            pollingOption: [.iso14443, .iso15693, .iso18092],
            delegate: self,
            queue: queue
        )
        newSession.alertMessage = "Hold the top of iPhone near the supported tag."
        session = newSession
        newSession.begin()
    }

    func stop() {
        session?.invalidate()
        session = nil
    }

    nonisolated func tagReaderSessionDidBecomeActive(
        _ session: NFCTagReaderSession
    ) {}

    nonisolated func tagReaderSession(
        _ session: NFCTagReaderSession,
        didDetect tags: [NFCTag]
    ) {
        guard let tag = tags.first else { return }
        Task { @MainActor [weak self] in
            guard let self else { return }
            do {
                try await session.connect(to: tag)
                onTag(tag, generation)
            } catch {
                onError(error, generation)
            }
        }
    }

    nonisolated func tagReaderSession(
        _ session: NFCTagReaderSession,
        didInvalidateWithError error: Error
    ) {
        Task { @MainActor [weak self] in
            guard let self else { return }
            self.session = nil
            self.onError(error, self.generation)
        }
    }
}
~~~

The polling options and the async connect overload should be compiled against the selected SDK. After connecting, switch on the NFCTag case and call only the adapter required by the feature. If more than one tag is detected, show guidance and decide whether to restart polling rather than silently choosing one.

## Recipe 8: ISO 7816 APDU adapter

Keep APDU construction, transport, and status policy separate:

~~~swift
import CoreNFC
import Foundation

struct APDUResult: Sendable, Equatable {
    let payload: Data
    let statusWord1: UInt8
    let statusWord2: UInt8

    var statusWord: UInt16 {
        UInt16(statusWord1) << 8 | UInt16(statusWord2)
    }
}

enum APDUStatus {
    case success
    case retry
    case authenticationRequired
    case rejected
    case unknown
}

func classify(_ result: APDUResult) -> APDUStatus {
    switch result.statusWord {
    case 0x9000:
        return .success
    case 0x6300, 0x6985:
        return .rejected
    case 0x6982, 0x6983:
        return .authenticationRequired
    case 0x6C00...0x6CFF:
        return .retry
    default:
        return .unknown
    }
}

func makeReadAPDU(
    instructionClass: UInt8,
    instructionCode: UInt8,
    parameter1: UInt8,
    parameter2: UInt8,
    expectedResponseLength: Int
) -> NFCISO7816APDU {
    NFCISO7816APDU(
        instructionClass: instructionClass,
        instructionCode: instructionCode,
        p1Parameter: parameter1,
        p2Parameter: parameter2,
        data: Data(),
        expectedResponseLength: expectedResponseLength
    )
}
~~~

The exact initializer labels and async response type must be compiled against the current SDK. The AID list in the target entitlement is part of the route: do not build an arbitrary SELECT command for an undeclared application identifier. Keep command bytes and response payloads out of normal analytics and model prompts.

## Recipe 9: protocol adapter switch

Do not collapse all tags into a UID-based object:

~~~swift
import CoreNFC

enum SupportedTag {
    case iso7816(NFCISO7816Tag)
    case iso15693(NFCISO15693Tag)
    case feliCa(NFCFeliCaTag)
    case mifare(NFCMiFareTag)
    case ndef(NFCNDEFTag)
}

func supportedTag(from tag: NFCTag) -> SupportedTag? {
    switch tag {
    case .iso7816(let value):
        return .iso7816(value)
    case .iso15693(let value):
        return .iso15693(value)
    case .feliCa(let value):
        return .feliCa(value)
    case .miFare(let value):
        return .mifare(value)
    @unknown default:
        return nil
    }
}
~~~

The enum cases and protocol spelling are SDK-defined. Keep this adapter narrow and test each case with a real fixture. A protocol value can also conform to NFCNDEFTag; choose the adapter based on the actual operation.

## Recipe 10: background universal-link handoff

Handle cold and warm scene delivery without executing a destructive command:

~~~swift
import Foundation
import UIKit

func handleHandoff(
    _ userActivity: NSUserActivity
) -> URL? {
    guard userActivity.activityType == NSUserActivityTypeBrowsingWeb else {
        return nil
    }
    guard let url = userActivity.webpageURL else {
        return nil
    }
    return try? validatedAppURL(url, allowedHost: "example.com")
}

func application(
    _ application: UIApplication,
    continue userActivity: NSUserActivity,
    restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void
) -> Bool {
    guard let url = handleHandoff(userActivity) else {
        return false
    }
    // Store URL as pending value state. Route after scene/user review.
    NotificationCenter.default.post(
        name: .nfcBackgroundURLReceived,
        object: url
    )
    return true
}

extension Notification.Name {
    static let nfcBackgroundURLReceived =
        Notification.Name("nfcBackgroundURLReceived")
}
~~~

For a scene-based app, also inspect connection options for the NFC-related user activity during scene connection and handle existing-scene delivery. The exact delegate location depends on the project’s scene architecture. The important rule is to validate the URL and route through app state rather than treating the activity as a trusted command.

## Recipe 11: scene NFC events

NFCWindowSceneDelegate reports eligible reader or presentation events:

~~~swift
import CoreNFC
import UIKit

final class SceneDelegate: UIResponder, UIWindowSceneDelegate, NFCWindowSceneDelegate {
    var pendingNFCEvent: NFCWindowSceneEvent?

    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {
        pendingNFCEvent = connectionOptions.nfcEvent
        // Inject pendingNFCEvent into the SwiftUI feature model.
    }

    func windowScene(
        _ windowScene: UIWindowScene,
        didReceiveNFCWindowSceneEvent event: NFCWindowSceneEvent
    ) {
        pendingNFCEvent = event
        // Update value state; do not claim transaction success.
    }
}
~~~

If the event indicates a presentation gesture or reader field, the feature model can prepare the proper card/presentment screen. CardSession eligibility and the actual event stream remain separate checks.

## Recipe 12: CardSession event loop

CardSession is a specialized route with Apple-managed entitlement and physical-reader proof:

~~~swift
import CoreNFC
import Foundation

@MainActor
final class CardSessionCoordinator {
    private var session: CardSession?
    private var eventTask: Task<Void, Never>?

    func start() async {
        guard NFCReaderSession.readingAvailable else { return }
        guard CardSession.isSupported, CardSession.isEligible else { return }

        do {
            let newSession = try await CardSession()
            session = newSession
            newSession.alertMessage = "Hold iPhone near the contactless reader."

            eventTask = Task { @MainActor [weak self, newSession] in
                do {
                    for try await event in newSession.eventStream {
                        guard let self else { return }
                        switch event {
                        case .sessionStarted:
                            break
                        case .readerDetected:
                            break
                        case .received(let apdu):
                            // Respond promptly using precomputed protocol state.
                            _ = apdu
                        case .readerDeselected:
                            return
                        case .sessionInvalidated:
                            return
                        @unknown default:
                            return
                        }
                    }
                } catch {
                    // Map to a safe invalidated state.
                }
            }

            try await newSession.startEmulation()
        } catch {
            session = nil
        }
    }

    func stop(status: CardSession.EmulationUIStatus) async {
        guard let session else { return }
        await session.stopEmulation(status: status)
        eventTask?.cancel()
        eventTask = nil
        self.session = nil
    }

    func invalidate() {
        session?.invalidate()
        eventTask?.cancel()
        eventTask = nil
        session = nil
    }
}
~~~

Event case labels and APDU response APIs are current-SDK compile points. Do not perform network or model work in the APDU response branch. The documented maximum emulation duration and reader timing are release-test requirements.

## Recipe 13: presentment intent assertion

Acquire the assertion only after the person expresses active contactless intent:

~~~swift
import CoreNFC

@MainActor
final class PresentmentIntentController {
    private var assertion: NFCPresentmentIntentAssertion?

    func acquireAfterUserAction() async -> Bool {
        guard NFCReaderSession.readingAvailable else { return false }
        do {
            assertion = try await NFCPresentmentIntentAssertion.acquire()
            return assertion?.isValid == true
        } catch {
            assertion = nil
            return false
        }
    }

    func release() {
        assertion = nil
    }
}
~~~

The assertion expires when the app backgrounds, its duration elapses, or the object deinitializes. It also has a cooldown after expiration. Treat it as a short-lived intent guard, not a general NFC permission.

## Recipe 14: SwiftUI route shell

The view shows value state and delegates the live route:

~~~swift
import SwiftUI

struct NFCFeatureView: View {
    @StateObject private var model = NFCFeatureModel()
    @State private var coordinator: NDEFReaderCoordinator?

    var body: some View {
        VStack(spacing: 20) {
            Text(statusTitle)
                .accessibilityAddTraits(.isHeader)

            Button("Scan tag") {
                let generation = model.begin()
                let newCoordinator = NDEFReaderCoordinator(
                    onMessages: { messages, callbackGeneration in
                        guard model.accepts(callbackGeneration) else { return }
                        // Convert to envelope, validate, then enter review.
                        _ = messages
                    },
                    onFailure: { error, callbackGeneration in
                        guard model.accepts(callbackGeneration) else { return }
                        model.state = .failed(error.localizedDescription)
                    }
                )
                coordinator = newCoordinator
                newCoordinator.start(generation: generation)
            }
            .buttonStyle(.glassProminent)

            Button("Enter manually") {
                // Offer a non-NFC route.
            }
        }
        .padding()
        .onDisappear {
            coordinator?.stop()
            model.cancel()
        }
    }

    private var statusTitle: String {
        switch model.state {
        case .idle:
            return "Ready to scan"
        case .active:
            return "Hold iPhone near the tag"
        case .reading:
            return "Reading tag"
        case .reviewing:
            return "Review result"
        case .failed(let message):
            return message
        case .cancelled:
            return "Scan cancelled"
        }
    }
}
~~~

This is intentionally schematic: a production model can expose a method for failure instead of mutating state directly, and the coordinator should be stored in a feature-owned reference rather than recreated by view identity. The key points are explicit user intent, generation checking, teardown, semantic labels, and a fallback action.

## Recipe 15: local AI proposal envelope

Give an on-device model only a bounded, non-secret source:

~~~swift
import Foundation

struct NFCModelInput: Codable, Sendable {
    let route: String
    let recordKinds: [String]
    let decodedText: [String]
    let validatedURLs: [URL]
    let sourceDigest: String
}

struct NFCProposal: Codable, Sendable, Equatable {
    let title: String
    let category: String
    let rationale: String
    let sourceDigest: String
}

func makeModelInput(
    decoded: [DecodedNDEF],
    sourceDigest: String
) -> NFCModelInput {
    NFCModelInput(
        route: "ndef-review",
        recordKinds: decoded.map(\.kind),
        decodedText: decoded.compactMap(\.text).prefix(20).map(String.init),
        validatedURLs: decoded.compactMap(\.url).prefix(10),
        sourceDigest: sourceDigest
    )
}
~~~

The model output is a proposal. Compare its source digest with the current review source, show the original decoded values, and require an explicit accept/edit action. Keep APDU response data, UIDs, credentials, secure-messaging material, and payment information out of this envelope.

## Recipe 16: reducer tests without NFC hardware

The deterministic app logic can be tested on every build machine:

~~~swift
import Testing

@Test
func staleNFCCallbackCannotCommitNewGeneration() {
    let model = NFCTestModel()
    let first = model.begin()
    _ = model.begin()

    #expect(model.accepts(first) == false)
}

@Test
func oversizedNDEFProposalIsRejectedBeforeWrite() {
    let result = validateCapacity(proposedLength: 100, capacity: 20)
    #expect(result == .tooLarge)
}

@Test
func unexpectedURLHostIsNotOpened() {
    let url = URL(string: "https://evil.example/items/1")!
    #expect(throws: URLPolicyError.self) {
        try validatedAppURL(url, allowedHost: "example.com")
    }
}
~~~

Add physical fixture tests separately. A reducer test that passes with fake NFCNDEFMessage values does not prove the radio, entitlements, tag memory, or CardSession reader timing.

## Recipe 17: sanitized proof logging

Log state transitions and digests, not secrets:

~~~swift
import OSLog

let nfcLog = Logger(
    subsystem: "com.example.app",
    category: "nfc"
)

func logNFCState(
    route: String,
    state: String,
    generation: UInt64,
    sourceDigest: String?
) {
    nfcLog.info(
        "route=\(route, privacy: .public) state=\(state, privacy: .public) generation=\(generation, privacy: .public) sourceDigest=\(sourceDigest ?? "none", privacy: .public)"
    )
}
~~~

Review the privacy mode of every field. Do not log the raw NDEF payload, tag identifier, UID, APDU, credential, URL query, or response bytes in production.

## Recipe 18: implementation stop conditions

Stop and resolve the boundary before adding more UI when:

- the route needs an entitlement that has not been approved;
- the current device or region is ineligible;
- the feature cannot explain what it reads or writes;
- a protocol response is being treated as authentication without a documented protocol;
- the AI proposal would cause a physical or credential side effect automatically;
- the only evidence is simulator output;
- the universal-link association works locally but has not been verified in the TestFlight artifact;
- the session can outlive its SwiftUI feature and still mutate state.

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcndefreadersessiondelegate)
- [NFCReaderSessionProtocol](https://developer.apple.com/documentation/corenfc/nfcreadersessionprotocol)
- [NFCNDEFTag](https://developer.apple.com/documentation/corenfc/nfcndeftag)
- [NFCNDEFStatus](https://developer.apple.com/documentation/corenfc/nfcndefstatus)
- [NFCNDEFMessage](https://developer.apple.com/documentation/corenfc/nfcndefmessage)
- [NFCNDEFPayload](https://developer.apple.com/documentation/corenfc/nfcndefpayload)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [NFCTagReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfctagreadersessiondelegate-2joku?changes=_1)
- [NFCISO7816Tag](https://developer.apple.com/documentation/corenfc/nfciso7816tag)
- [NFCISO7816APDU](https://developer.apple.com/documentation/corenfc/nfciso7816apdu)
- [NFCISO7816ResponseAPDU](https://developer.apple.com/documentation/corenfc/nfciso7816responseapdu)
- [NFCISO15693Tag](https://developer.apple.com/documentation/corenfc/nfciso15693tag)
- [NFCFeliCaTag](https://developer.apple.com/documentation/corenfc/nfcfelicatag)
- [NFCMiFareTag](https://developer.apple.com/documentation/corenfc/nfcmifaretag)
- [Adding support for background tag reading](https://developer.apple.com/documentation/corenfc/adding-support-for-background-tag-reading)
- [CardSession](https://developer.apple.com/documentation/corenfc/cardsession)
- [NFCPresentmentIntentAssertion](https://developer.apple.com/documentation/corenfc/nfcpresentmentintentassertion)
- [NFCWindowSceneDelegate](https://developer.apple.com/documentation/corenfc/nfcwindowscenedelegate)
- [NFCWindowSceneEvent](https://developer.apple.com/documentation/corenfc/nfcwindowsceneevent)
- [Near Field Communication Tag Reader Session Formats Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.formats)
- [ISO7816 application identifiers for NFC Tag Reader Session](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.iso7816.select-identifiers)
- [ISO18092 system codes for NFC Tag Reader Session](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.felica.systemcodes)
- [HCE ISO 7816 select identifier prefixes entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.hce.iso7816.select-identifier-prefixes)
- [SwiftUI Observation](https://developer.apple.com/documentation/observation)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing with Swift Testing](https://developer.apple.com/documentation/testing)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
