// Shared product state only. Keep MWDAT, Kotlin, browser, media, and device
// objects at platform adapter boundaries.

public enum WearableSurface: String, Codable, Equatable, Sendable {
    case nativeDATiOS = "native-dat-ios"
    case nativeDATAndroid = "native-dat-android"
    case nativeDisplay = "native-display"
    case webApp = "web-app"
    case phoneFallback = "phone-fallback"
}

public enum ProcessingLocation: String, Codable, Equatable, Sendable {
    case glassesNative = "glasses-native"
    case phoneLocal = "phone-local"
    case browser
    case remote
    case mixed
    case unknown
}

public enum WearableCapability: String, Codable, Equatable, Sendable {
    case display
    case camera
    case audio
    case input
}

public struct WearableTarget: Codable, Equatable, Sendable {
    public let surface: WearableSurface
    public let runtimeIdentity: String
    public let firmware: String
    public let companionVersion: String
    public let packageOrArtifact: String
    public let processingLocation: ProcessingLocation

    public init(
        surface: WearableSurface,
        runtimeIdentity: String,
        firmware: String,
        companionVersion: String,
        packageOrArtifact: String,
        processingLocation: ProcessingLocation
    ) {
        self.surface = surface
        self.runtimeIdentity = runtimeIdentity
        self.firmware = firmware
        self.companionVersion = companionVersion
        self.packageOrArtifact = packageOrArtifact
        self.processingLocation = processingLocation
    }
}

public enum WearableEvent: Equatable, Sendable {
    case begin
    case registrationChanged(Bool)
    case permissionChanged(Bool)
    case targetResolved(WearableTarget)
    case beginCapability(WearableCapability)
    case capabilitySupportResolved(WearableCapability, supported: Bool)
    case capabilityAction(epoch: UInt64, action: String)
    case operationFinished
    case failure(String)
    case disconnect
    case cancel
}

public enum WearableEffect: Equatable, Sendable {
    case startRegistration
    case requestPermission
    case resolveTarget
    case checkCapability(WearableCapability)
    case startCapability(WearableCapability)
    case deliverAction(String)
    case stopCapability(WearableCapability)
    case stopSession
    case presentPhoneFallback(reason: String)
    case ignoreStaleEvent
}

public enum WearableState: Equatable, Sendable {
    case idle
    case registering
    case awaitingPermission
    case awaitingTarget
    case ready(WearableTarget)
    case active(epoch: UInt64, capability: WearableCapability)
    case phoneFallback(reason: String)
    case failed(reason: String)
}

public struct WearableReducer: Equatable, Sendable {
    public private(set) var state: WearableState = .idle
    public private(set) var epoch: UInt64 = 0

    public init() {}

    public mutating func reduce(_ event: WearableEvent) -> [WearableEffect] {
        switch event {
        case .begin:
            guard state == .idle || isFallback else { return [.ignoreStaleEvent] }
            state = .registering
            return [.startRegistration]

        case let .registrationChanged(isRegistered):
            guard state == .registering else { return [.ignoreStaleEvent] }
            guard isRegistered else { return enterFallback("registration-denied") }
            state = .awaitingPermission
            return [.requestPermission]

        case let .permissionChanged(isGranted):
            guard state == .awaitingPermission else { return [.ignoreStaleEvent] }
            guard isGranted else { return enterFallback("permission-denied") }
            state = .awaitingTarget
            return [.resolveTarget]

        case let .targetResolved(target):
            guard state == .awaitingTarget else { return [.ignoreStaleEvent] }
            state = .ready(target)
            return []

        case let .beginCapability(capability):
            guard case .ready = state else { return [.ignoreStaleEvent] }
            return [.checkCapability(capability)]

        case let .capabilitySupportResolved(capability, supported):
            guard case .ready = state else { return [.ignoreStaleEvent] }
            guard supported else { return enterFallback("capability-unavailable-\(capability.rawValue)") }
            epoch += 1
            state = .active(epoch: epoch, capability: capability)
            return [.startCapability(capability)]

        case let .capabilityAction(actionEpoch, action):
            guard case let .active(currentEpoch, _) = state, currentEpoch == actionEpoch else {
                return [.ignoreStaleEvent]
            }
            return [.deliverAction(action)]

        case .operationFinished:
            guard case .active = state else { return [.ignoreStaleEvent] }
            return []

        case let .failure(reason):
            return enterFailure(reason)

        case .disconnect:
            return enterFallback("disconnected")

        case .cancel:
            return enterFallback("cancelled")
        }
    }

    private var isFallback: Bool {
        if case .phoneFallback = state { return true }
        return false
    }

    private mutating func enterFailure(_ reason: String) -> [WearableEffect] {
        let cleanup = cleanupEffects(reason: reason)
        state = .failed(reason: reason)
        return cleanup
    }

    private mutating func enterFallback(_ reason: String) -> [WearableEffect] {
        let cleanup = cleanupEffects(reason: reason)
        state = .phoneFallback(reason: reason)
        return cleanup
    }

    private mutating func cleanupEffects(reason: String) -> [WearableEffect] {
        defer { epoch += 1 }
        guard case let .active(_, capability) = state else {
            return [.presentPhoneFallback(reason: reason)]
        }
        return [
            .stopCapability(capability),
            .stopSession,
            .presentPhoneFallback(reason: reason),
        ]
    }
}
