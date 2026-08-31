import Foundation
import MWDATCore
import MWDATDisplay

public struct MetaWearablesDisplaySnapshot: Sendable {
    public let title: String
    public let detail: String

    public init(title: String, detail: String) {
        self.title = title
        self.detail = detail
    }
}

public enum MetaWearablesDisplayAction: Sendable {
    case primary
    case secondary
}

public enum MetaWearablesDisplayFallback: Sendable {
    case noEligibleDevice
    case displayCapabilityUnavailable
    case datAppUpdateRequired
    case sendFailed
}

public enum MetaWearablesDisplayFailure: Sendable {
    case session
    case display
    case send
}

public enum MetaWearablesDisplayEvent: Sendable {
    case sessionStarted
    case displayStarted
    case displayStopped
    case action(MetaWearablesDisplayAction)
    case phoneFallback(MetaWearablesDisplayFallback)
    case error(MetaWearablesDisplayFailure)
}

/// A small DAT 0.9 native Display adapter.
///
/// The product layer owns the snapshot and interprets these typed events. This
/// coordinator owns the DAT session/display resources, rejects button events
/// from an older session epoch, and stops the display before its parent session.
@MainActor
public final class MetaWearablesDisplayCoordinator {
    public typealias EventSink = @Sendable (MetaWearablesDisplayEvent) -> Void

    private let wearables: any WearablesInterface
    private let eventSink: EventSink
    private var epoch = 0
    private var session: DeviceSession?
    private var display: Display?
    private var displayStateToken: (any AnyListenerToken)?
    private var sessionStateTask: Task<Void, Never>?
    private var sessionErrorTask: Task<Void, Never>?

    public init(
        wearables: any WearablesInterface,
        eventSink: @escaping EventSink
    ) {
        self.wearables = wearables
        self.eventSink = eventSink
    }

    public func connect() {
        guard session == nil else { return }

        let selector = AutoDeviceSelector(
            wearables: wearables,
            filter: { $0.supportsDisplay() }
        )

        do {
            let nextSession = try wearables.createSession(deviceSelector: selector)
            session = nextSession
            observe(nextSession)
            try nextSession.start()
        } catch {
            handle(error)
        }
    }

    public func present(_ snapshot: MetaWearablesDisplaySnapshot) async {
        epoch += 1
        guard let display, display.state == .started else {
            eventSink(.phoneFallback(.displayCapabilityUnavailable))
            return
        }

        let currentEpoch = epoch
        let actionHandler: @Sendable (MetaWearablesDisplayAction) -> Void = { [weak self] action in
            Task { @MainActor [weak self] in
                guard let self, self.epoch == currentEpoch else { return }
                self.eventSink(.action(action))
            }
        }

        do {
            try await display.send(card(for: snapshot, onAction: actionHandler))
        } catch {
            eventSink(.error(.send))
            eventSink(.phoneFallback(.sendFailed))
        }
    }

    public func stop() async {
        epoch += 1
        sessionStateTask?.cancel()
        sessionStateTask = nil
        sessionErrorTask?.cancel()
        sessionErrorTask = nil

        let token = displayStateToken
        displayStateToken = nil
        await token?.cancel()

        // Child-before-parent: listener, Display, then DeviceSession.
        display?.stop()
        display = nil
        session?.stop()
        session = nil
    }

    private func observe(_ session: DeviceSession) {
        sessionStateTask?.cancel()
        sessionErrorTask?.cancel()

        sessionStateTask = Task { @MainActor [weak self, session] in
            for await state in session.stateStream() {
                guard !Task.isCancelled else { return }
                self?.handle(state, for: session)
            }
        }

        sessionErrorTask = Task { @MainActor [weak self, session] in
            for await error in session.errorStream() {
                guard !Task.isCancelled else { return }
                self?.handle(error)
            }
        }
    }

    private func handle(_ state: DeviceSessionState, for session: DeviceSession) {
        switch state {
        case .started:
            eventSink(.sessionStarted)
            attachDisplay(to: session)
        case .paused, .stopping, .stopped:
            if display != nil {
                eventSink(.displayStopped)
            }
        case .idle, .starting:
            break
        @unknown default:
            break
        }
    }

    private func handle(_ error: DeviceSessionError) {
        switch error {
        case .noEligibleDevice:
            eventSink(.phoneFallback(.noEligibleDevice))
        case .datAppOnTheGlassesUpdateRequired:
            eventSink(.phoneFallback(.datAppUpdateRequired))
        case .capabilityNotFound:
            eventSink(.phoneFallback(.displayCapabilityUnavailable))
        default:
            eventSink(.error(.session))
        }
    }

    private func attachDisplay(to session: DeviceSession) {
        guard display == nil else { return }

        do {
            let nextDisplay = try session.addDisplay()
            display = nextDisplay
            displayStateToken = nextDisplay.statePublisher.listen { [weak self] state in
                Task { @MainActor [weak self] in
                    self?.handle(state)
                }
            }
            nextDisplay.start()
        } catch DeviceSessionError.capabilityNotFound {
            eventSink(.phoneFallback(.displayCapabilityUnavailable))
        } catch {
            eventSink(.error(.display))
            eventSink(.phoneFallback(.displayCapabilityUnavailable))
        }
    }

    private func handle(_ state: DisplayState) {
        switch state {
        case .started:
            eventSink(.displayStarted)
        case .stopping, .stopped:
            eventSink(.displayStopped)
        case .starting:
            break
        @unknown default:
            break
        }
    }

    private func card(
        for snapshot: MetaWearablesDisplaySnapshot,
        onAction: @escaping @Sendable (MetaWearablesDisplayAction) -> Void
    ) -> FlexBox {
        FlexBox(direction: .column, spacing: 12) {
            Icon(name: .smartGlasses, style: .outline)
            Text(snapshot.title, style: .heading)
            Text(snapshot.detail, style: .meta, color: .secondary)
            ButtonGroup(alignment: .center) {
                Button(
                    label: "Do it",
                    style: .primary,
                    iconName: .checkmark,
                    onClick: { onAction(.primary) }
                )
                Button(
                    label: "Later",
                    style: .secondary,
                    iconName: .x,
                    onClick: { onAction(.secondary) }
                )
            }
        }
        .padding(24)
        .background(.card)
    }
}
