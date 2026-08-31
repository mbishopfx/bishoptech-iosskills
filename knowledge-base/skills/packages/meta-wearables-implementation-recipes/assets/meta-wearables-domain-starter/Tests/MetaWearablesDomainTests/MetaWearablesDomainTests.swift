import Testing
@testable import MetaWearablesDomain

struct MetaWearablesDomainTests {
    @Test
    func deniedRegistrationReturnsPhoneFallback() {
        var reducer = WearableReducer()

        #expect(reducer.reduce(.begin) == [.startRegistration])
        #expect(reducer.reduce(.registrationChanged(false)) == [.presentPhoneFallback(reason: "registration-denied")])
        #expect(reducer.state == .phoneFallback(reason: "registration-denied"))
    }

    @Test
    func staleCapabilityActionsAreIgnored() {
        var reducer = configuredReducer()

        #expect(reducer.reduce(.beginCapability(.display)) == [.checkCapability(.display)])
        #expect(reducer.reduce(.capabilitySupportResolved(.display, supported: true)) == [.startCapability(.display)])

        let currentEpoch = reducer.epoch
        #expect(reducer.reduce(.capabilityAction(epoch: currentEpoch - 1, action: "tap")) == [.ignoreStaleEvent])
        #expect(reducer.reduce(.capabilityAction(epoch: currentEpoch, action: "tap")) == [.deliverAction("tap")])
    }

    @Test
    func disconnectStopsChildBeforeParentAndFallsBack() {
        var reducer = configuredReducer()
        _ = reducer.reduce(.beginCapability(.display))
        _ = reducer.reduce(.capabilitySupportResolved(.display, supported: true))

        let effects = reducer.reduce(.disconnect)

        #expect(effects == [
            .stopCapability(.display),
            .stopSession,
            .presentPhoneFallback(reason: "disconnected"),
        ])
        #expect(reducer.state == .phoneFallback(reason: "disconnected"))
    }

    @Test
    func unsupportedCapabilityNeverStarts() {
        var reducer = configuredReducer()
        _ = reducer.reduce(.beginCapability(.camera))

        let effects = reducer.reduce(.capabilitySupportResolved(.camera, supported: false))

        #expect(effects == [.presentPhoneFallback(reason: "capability-unavailable-camera")])
        #expect(reducer.state == .phoneFallback(reason: "capability-unavailable-camera"))
    }

    private func configuredReducer() -> WearableReducer {
        var reducer = WearableReducer()
        _ = reducer.reduce(.begin)
        _ = reducer.reduce(.registrationChanged(true))
        _ = reducer.reduce(.permissionChanged(true))
        _ = reducer.reduce(.targetResolved(
            WearableTarget(
                surface: .nativeDATiOS,
                runtimeIdentity: "to-verify",
                firmware: "to-verify",
                companionVersion: "to-verify",
                packageOrArtifact: "to-verify",
                processingLocation: .phoneLocal
            )
        ))
        return reducer
    }
}
