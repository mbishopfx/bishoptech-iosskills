# Core NFC reader and contactless code recipes

These are compile-oriented route sketches for a named iOS or iPadOS target. They are not claimed to compile in this documentation-only workspace and they do not prove NFC radio behavior, tag compatibility, HCE eligibility, payment success, or release readiness. Add the target capability, privacy strings, entitlements, associated domains, and physical fixtures before treating any recipe as product code.

The [Core NFC capability route](../50-capability-recipes/57-core-nfc-reader-route.md), [deep dive](../42-framework-deep-dives/34-core-nfc-tag-sessions-and-secure-ndef.md), and [proof matrix](../60-verification/51-core-nfc-reader-proof-matrix.md) define the boundaries around these snippets.

## Recipe 1: Start an NDEF reader session

Keep the session in a long-lived coordinator. Do not create it from a SwiftUI body or from a view that can be recreated while the scan is active.

~~~swift
import CoreNFC
import Foundation

final class NDEFScanCoordinator: NSObject, NFCNDEFReaderSessionDelegate {
    private var session: NFCNDEFReaderSession?

    var onState: ((String) -> Void)?
    var onMessage: ((NFCNDEFMessage) -> Void)?
    var onError: ((Error) -> Void)?

    func start(invalidateAfterFirstRead: Bool = true) {
        guard NFCNDEFReaderSession.readingAvailable else {
            onState?("unavailable")
            return
        }

        let next = NFCNDEFReaderSession(
            delegate: self,
            queue: nil,
            invalidateAfterFirstRead: invalidateAfterFirstRead
        )
        next.alertMessage = "Hold your iPhone near the object to learn more about it."
        session = next
        onState?("starting")
        next.begin()
    }

    func stop() {
        session?.invalidate()
        session = nil
        onState?("stopped")
    }

    func readerSessionDidBecomeActive(_ session: NFCNDEFReaderSession) {
        onState?("active")
    }

    func readerSession(
        _ session: NFCNDEFReaderSession,
        didDetectNDEFs messages: [NFCNDEFMessage]
    ) {
        messages.forEach { onMessage?($0) }
        onState?("message-detected")
    }

    func readerSession(
        _ session: NFCNDEFReaderSession,
        didDetect tags: [any NFCNDEFTag]
    ) {
        guard let tag = tags.first else {
            session.invalidate(errorMessage: "No readable object was found.")
            return
        }

        session.connect(to: tag) { [weak self] error in
            guard let self else { return }
            if let error {
                self.onError?(error)
                session.invalidate(errorMessage: "The object moved away. Please try again.")
                return
            }

            tag.readNDEF { [weak self] message, error in
                if let error {
                    self?.onError?(error)
                    session.invalidate(errorMessage: "The object could not be read.")
                    return
                }
                if let message {
                    self?.onMessage?(message)
                    self?.onState?("tag-read")
                } else {
                    session.invalidate(errorMessage: "The object contains no readable message.")
                }
            }
        }
    }

    func readerSession(
        _ session: NFCNDEFReaderSession,
        didInvalidateWithError error: any Error
    ) {
        self.session = nil
        onError?(error)
        onState?("invalidated")
    }
}
~~~

The exact callback queue, availability, and error policy should be adapted to the target’s concurrency model. Treat an invalidation callback as terminal for that session and release the detected tag references.

## Recipe 2: Turn an NDEF message into a reviewable projection

Keep the raw records and the user-facing projection separate. Apple provides helpers for well-known URI and text records; unknown records should remain typed data rather than being guessed.

~~~swift
import CoreNFC
import Foundation

struct NDEFRecordProjection: Sendable {
    let format: String
    let type: Data
    let identifier: Data
    let byteCount: Int
    let text: String?
    let localeIdentifier: String?
    let url: URL?
}

func project(_ message: NFCNDEFMessage) -> [NDEFRecordProjection] {
    message.records.map { record in
        let textAndLocale = record.wellKnownTypeTextPayload()
        let text = textAndLocale.0
        let locale = textAndLocale.1

        return NDEFRecordProjection(
            format: String(describing: record.typeNameFormat),
            type: record.type,
            identifier: record.identifier,
            byteCount: record.payload.count,
            text: text,
            localeIdentifier: locale?.identifier,
            url: record.wellKnownTypeURIPayload()
        )
    }
}

func validateExternalURL(
    _ url: URL,
    allowedHosts: Set<String>
) -> URL? {
    guard
        let scheme = url.scheme?.lowercased(),
        scheme == "https",
        let host = url.host?.lowercased(),
        allowedHosts.contains(host)
    else {
        return nil
    }
    return url
}
~~~

Do not use a URL projection as a reason to open the destination automatically. Put the normalized host, action, and confirmation state in the review model.

## Recipe 3: Query NDEF status before a write

A write route must know whether the tag is writable and whether the serialized message fits. The completion handlers are called on the queue supplied to the reader session.

~~~swift
import CoreNFC

struct NDEFWritePlan {
    let message: NFCNDEFMessage
    let estimatedByteCount: Int
}

func write(
    _ plan: NDEFWritePlan,
    to tag: any NFCNDEFTag,
    session: NFCNDEFReaderSession,
    onResult: @escaping (Result<Void, Error>) -> Void
) {
    tag.queryNDEFStatus { status, capacity, error in
        if let error {
            onResult(.failure(error))
            return
        }

        guard status == .readWrite else {
            onResult(.failure(NSError(
                domain: "NFCWrite",
                code: 1,
                userInfo: [NSLocalizedDescriptionKey: "The object is not writable."]
            )))
            return
        }

        guard plan.estimatedByteCount <= capacity else {
            onResult(.failure(NSError(
                domain: "NFCWrite",
                code: 2,
                userInfo: [NSLocalizedDescriptionKey: "The message is larger than the object capacity."]
            )))
            return
        }

        tag.writeNDEF(plan.message) { error in
            if let error {
                onResult(.failure(error))
            } else {
                onResult(.success(()))
                session.alertMessage = "Write complete."
            }
        }
    }
}
~~~

The user confirmation and exact-byte preview should happen before this function. Keep write-locking in a separate action.

## Recipe 4: Configure a protocol-specific tag reader

Use the current configuration initializer when it is available in the target SDK. Select the smallest polling option and only the identifiers the feature supports.

~~~swift
import CoreNFC

final class TagReaderCoordinator: NSObject, NFCTagReaderSessionDelegate {
    private var session: NFCTagReaderSession?
    private let iso7816AIDs: [String]
    private let felicaSystemCodes: [String]

    init(iso7816AIDs: [String], felicaSystemCodes: [String]) {
        self.iso7816AIDs = iso7816AIDs
        self.felicaSystemCodes = felicaSystemCodes
    }

    func startISO7816() {
        guard NFCTagReaderSession.readingAvailable else { return }

        let configuration = NFCTagReaderSession.Configuration(
            pollingOption: .iso14443,
            iso7816SelectIdentifiers: iso7816AIDs,
            feliCaSystemCodes: []
        )
        let next = NFCTagReaderSession(
            configuration: configuration,
            delegate: self,
            queue: nil
        )
        next.alertMessage = "Hold your iPhone near the object."
        session = next
        next.begin()
    }

    func startFeliCa() {
        guard NFCTagReaderSession.readingAvailable else { return }

        let configuration = NFCTagReaderSession.Configuration(
            pollingOption: .iso18092,
            iso7816SelectIdentifiers: [],
            feliCaSystemCodes: felicaSystemCodes
        )
        let next = NFCTagReaderSession(
            configuration: configuration,
            delegate: self,
            queue: nil
        )
        next.alertMessage = "Hold your iPhone near the object."
        session = next
        next.begin()
    }

    func tagReaderSessionDidBecomeActive(_ session: NFCTagReaderSession) {}

    func tagReaderSession(
        _ session: NFCTagReaderSession,
        didDetect tags: [NFCTag]
    ) {
        guard let candidate = tags.first else {
            session.invalidate(errorMessage: "No supported object was found.")
            return
        }

        guard candidate.isAvailable else {
            session.invalidate(errorMessage: "The object is no longer available.")
            return
        }

        session.connect(to: candidate) { [weak self] error in
            guard let self else { return }
            if let error {
                session.invalidate(errorMessage: "The object could not be connected.")
                self.record(error)
                return
            }

            switch candidate {
            case .iso7816(let tag):
                self.readISO7816(tag, session: session)
            case .iso15693(let tag):
                self.inspectISO15693(tag)
            case .feliCa(let tag):
                self.inspectFeliCa(tag)
            case .miFare(let tag):
                self.inspectMiFare(tag)
            }
        }
    }

    func tagReaderSession(
        _ session: NFCTagReaderSession,
        didInvalidateWithError error: any Error
    ) {
        self.session = nil
        record(error)
    }

    private func readISO7816(
        _ tag: any NFCISO7816Tag,
        session: NFCTagReaderSession
    ) {
        // Call the typed APDU adapter here.
    }

    private func inspectISO15693(_ tag: any NFCISO15693Tag) {}
    private func inspectFeliCa(_ tag: any NFCFeliCaTag) {}
    private func inspectMiFare(_ tag: any NFCMiFareTag) {}
    private func record(_ error: Error) {}
}
~~~

Some SDKs expose newer async overloads and deprecate older initializers. Confirm the signature and availability in the target’s current SDK before copying this sketch.

## Recipe 5: Send an allowlisted ISO 7816 APDU

Construct APDUs from a versioned command table. Never accept command bytes from an untrusted NDEF payload or a model output.

~~~swift
import CoreNFC
import Foundation

struct ISO7816Response: Sendable {
    let payload: Data
    let statusWord1: UInt8
    let statusWord2: UInt8
}

func sendReadCommand(
    to tag: any NFCISO7816Tag,
    onResult: @escaping (Result<ISO7816Response, Error>) -> Void
) {
    let apdu = NFCISO7816APDU(
        instructionClass: 0x00,
        instructionCode: 0xB0,
        p1Parameter: 0x00,
        p2Parameter: 0x00,
        data: Data(),
        expectedResponseLength: 0
    )

    tag.sendCommand(apdu: apdu) { result in
        switch result {
        case .success(let response):
            onResult(.success(ISO7816Response(
                payload: response.payload ?? Data(),
                statusWord1: response.statusWord1,
                statusWord2: response.statusWord2
            )))
        case .failure(let error):
            onResult(.failure(error))
        }
    }
}
~~~

The instruction values above are only an illustration of typed construction, not a claim that a real tag supports that command. For a product route, define the AID, CLA/INS/P1/P2/data/Le, response schema, status-word mapping, and retry policy from the exact protocol contract.

## Recipe 6: Build a protocol result instead of exposing bytes

Keep adapter code close to the protocol and expose a domain-neutral observation to the app.

~~~swift
import CoreNFC
import Foundation

enum NFCObservation: Sendable {
    case ndef(records: Int)
    case iso7816(statusWord: UInt16, payloadLength: Int)
    case iso15693(identifierLength: Int)
    case felica(systemCodeLength: Int)
    case mifare(family: String)
    case unsupported
}

func observe(_ tag: NFCTag) -> NFCObservation {
    switch tag {
    case .iso7816:
        return .iso7816(statusWord: 0, payloadLength: 0)
    case .iso15693(let value):
        return .iso15693(identifierLength: value.identifier.count)
    case .feliCa(let value):
        return .felica(systemCodeLength: value.currentSystemCode.count)
    case .miFare(let value):
        return .mifare(family: String(describing: value.mifareFamily))
    }
}
~~~

The observation is still not authentication. Add a separately named verifier when the feature needs cryptographic or server-backed trust.

## Recipe 7: Handle a background tag activity

Background tag reading delivers an NSUserActivity after the person taps the system notification. Keep this entry point strict and share its parser and action policy with in-app scans.

~~~swift
import CoreNFC
import UIKit

final class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        continue userActivity: NSUserActivity,
        restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void
    ) -> Bool {
        guard userActivity.activityType == NSUserActivityTypeBrowsingWeb else {
            return false
        }

        let message = userActivity.ndefMessagePayload
        guard !message.records.isEmpty else {
            return false
        }

        let projection = project(message)
        guard projection.allSatisfy({ record in
            record.url == nil || record.url?.scheme?.lowercased() == "https"
        }) else {
            return false
        }

        // Route to the review screen. Do not open, write, purchase, or
        // authorize from the activity alone.
        return true
    }
}
~~~

Universal-link association and host validation are configuration and product-policy responsibilities. A direct app launch or custom URL scheme is not evidence that background reading is configured.

## Recipe 8: HCE/CardSession eligibility and event loop

CardSession is only available in an approved route and requires a physical NFC reader for testing. The event loop must answer every received APDU exactly once, except for the documented transmission-error retry.

~~~swift
import CoreNFC
import Foundation

func runCardSession(
    responseForAPDU: @escaping (Data) -> Data
) {
    Task {
        guard
            NFCReaderSession.readingAvailable,
            CardSession.isSupported,
            await CardSession.isEligible
        else {
            return
        }

        do {
            let cardSession = try await CardSession()

            for try await event in cardSession.eventStream {
                switch event {
                case .sessionStarted:
                    cardSession.alertMessage = "Ready to communicate with the reader."

                case .readerDetected:
                    try await cardSession.startEmulation()

                case .received(let apdu):
                    let response = responseForAPDU(apdu.payload)
                    try await apdu.respond(response: response)

                case .readerDeselected:
                    await cardSession.stopEmulation(status: .success)

                case .sessionInvalidated(let reason):
                    cardSession.alertMessage = "Communication ended."
                    recordCardSessionReason(reason)
                }
            }

            cardSession.invalidate()
        } catch {
            recordCardSessionError(error)
        }
    }
}

private func recordCardSessionReason(_ reason: CardSession.Error) {}
private func recordCardSessionError(_ error: Error) {}
~~~

The responseForAPDU function must be a deterministic protocol state machine. Do not call a slow model, network service, or unbounded parser inside the APDU response deadline. Apple documents that responding more than once to the same APDU is fatal, with transmissionError as the documented retry exception.

## Recipe 9: Make an on-device AI proposal from a reviewed scan

The model receives a minimal canonical projection, not raw bytes or commands. The output is a proposal that must be validated and approved.

~~~swift
struct NFCActionProposal: Sendable {
    let title: String
    let category: String
    let sourceObservationID: String
}

struct ReviewedNFCRecord: Sendable {
    let id: String
    let displayText: String
    let externalURL: URL?
    let userApprovedSource: Bool
}

func makeProposal(
    from record: ReviewedNFCRecord
) async throws -> NFCActionProposal? {
    guard record.userApprovedSource else {
        return nil
    }

    // Call the selected on-device model route with displayText only.
    // Validate the returned category against an app-owned enum.
    return NFCActionProposal(
        title: record.displayText,
        category: "review",
        sourceObservationID: record.id
    )
}
~~~

Do not use this shape as a credential verifier or command generator. Persist the source, proposal, model route/version, user edits, validation result, and final action separately.

## Recipe 10: SwiftUI state shell

The view renders the state machine while the coordinator owns Core NFC’s delegate lifetime.

~~~swift
import SwiftUI

@MainActor
final class NFCScanModel: ObservableObject {
    enum State {
        case ready
        case scanning
        case review([NDEFRecordProjection])
        case error(String)
    }

    @Published private(set) var state: State = .ready
    private let coordinator = NDEFScanCoordinator()

    init() {
        coordinator.onState = { [weak self] value in
            Task { @MainActor in
                if value == "starting" || value == "active" {
                    self?.state = .scanning
                }
            }
        }
        coordinator.onMessage = { [weak self] message in
            Task { @MainActor in
                self?.state = .review(project(message))
            }
        }
        coordinator.onError = { [weak self] error in
            Task { @MainActor in
                self?.state = .error(error.localizedDescription)
            }
        }
    }

    func start() {
        guard case .ready = state else { return }
        coordinator.start()
    }

    func cancel() {
        coordinator.stop()
        state = .ready
    }
}

struct NFCScanView: View {
    @StateObject private var model = NFCScanModel()

    var body: some View {
        NavigationStack {
            content
                .navigationTitle("Scan object")
                .toolbar {
                    ToolbarItem(placement: .primaryAction) {
                        Button("Scan", systemImage: "wave.3.right") {
                            model.start()
                        }
                        .disabled(!isReady)
                    }
                }
        }
    }

    @ViewBuilder
    private var content: some View {
        switch model.state {
        case .ready:
            ContentUnavailableView(
                "Ready to scan",
                systemImage: "wave.3.right",
                description: Text("Hold your iPhone near the object.")
            )
        case .scanning:
            ProgressView("Scanning…")
        case .review(let records):
            NFCReviewView(records: records)
        case .error(let message):
            ContentUnavailableView("Couldn’t read object", systemImage: "exclamationmark.triangle", description: Text(message))
        }
    }

    private var isReady: Bool {
        if case .ready = model.state { return true }
        return false
    }
}

struct NFCReviewView: View {
    let records: [NDEFRecordProjection]

    var body: some View {
        List(records.indices, id: \.self) { index in
            let record = records[index]
            VStack(alignment: .leading, spacing: 8) {
                Text(record.text ?? record.url?.absoluteString ?? "Unrecognized record")
                    .font(.headline)
                Text("\(record.byteCount) bytes")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }
}
~~~

The exact SwiftUI observation setup depends on the target’s Swift version and project architecture. Keep the app-owned review view separate from the system scanning surface. If Liquid Glass is used, apply it to a small review/action group rather than rebuilding the system NFC sheet.

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcndefreadersessiondelegate)
- [Building an NFC Tag-Reader App](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [NFCNDEFTag](https://developer.apple.com/documentation/corenfc/nfcndeftag)
- [NFCNDEFPayload](https://developer.apple.com/documentation/corenfc/nfcndefpayload)
- [NFCNDEFMessage](https://developer.apple.com/documentation/corenfc/nfcndefmessage)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [NFCTagReaderSession.Configuration](https://developer.apple.com/documentation/corenfc/nfctagreadersession/configuration)
- [NFCTagReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfctagreadersessiondelegate)
- [NFCTag](https://developer.apple.com/documentation/corenfc/nfctag-swift.enum)
- [NFCISO7816Tag](https://developer.apple.com/documentation/corenfc/nfciso7816tag)
- [NFCISO7816APDU](https://developer.apple.com/documentation/corenfc/nfciso7816apdu)
- [NFCISO7816ResponseAPDU](https://developer.apple.com/documentation/corenfc/nfciso7816responseapdu)
- [NFCISO15693Tag](https://developer.apple.com/documentation/corenfc/nfciso15693tag)
- [NFCFeliCaTag](https://developer.apple.com/documentation/corenfc/nfcfelicatag)
- [NFCMiFareTag](https://developer.apple.com/documentation/corenfc/nfcmifaretag)
- [Adding Support for Background Tag Reading](https://developer.apple.com/documentation/corenfc/adding-support-for-background-tag-reading)
- [CardSession](https://developer.apple.com/documentation/corenfc/cardsession)
- [CardSession.Event](https://developer.apple.com/documentation/corenfc/cardsession/event)
- [CardSession.EventStream](https://developer.apple.com/documentation/corenfc/cardsession/eventstream-swift.class)
- [CardSession.APDU](https://developer.apple.com/documentation/corenfc/cardsession/apdu)
- [CardSession.APDU.respond(response:)](https://developer.apple.com/documentation/corenfc/cardsession/apdu/respond%28response%3A%29)
- [NFCReaderUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nfcreaderusagedescription)
- [NFC](https://developer.apple.com/design/human-interface-guidelines/nfc)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
