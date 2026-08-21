# GameController input recipes

These are target-oriented Swift sketches for GameController. They are not claimed to compile in this documentation-only workspace and they do not prove a physical controller, system remapping, motion quality, SwiftUI focus, accessibility, performance, or release path.

Read the [GameController framework deep dive](../42-framework-deep-dives/38-gamecontroller-physical-input-and-motion.md), [capability route](../50-capability-recipes/61-gamecontroller-input-route.md), [controller-input design guide](../21-design-deep-dives/58-controller-input-and-accessible-game-design.md), and [proof matrix](../60-verification/55-gamecontroller-input-proof-matrix.md) first.

## Recipe 1: Model semantic actions

Keep device elements out of the domain layer.

~~~swift
import Foundation

enum GameAction: Sendable, Equatable {
    case move(x: Float, y: Float)
    case look(x: Float, y: Float)
    case primary
    case secondary
    case pause
    case cancel
    case nextSection
    case previousSection
}

struct InputSample: Sendable, Equatable {
    var timestamp: TimeInterval
    var primaryPressed: Bool
    var secondaryPressed: Bool
    var moveX: Float
    var moveY: Float
}

struct ActionMapRevision: Sendable, Equatable {
    var profileDescription: String
    var mappingRevision: Int
}
~~~

The game loop or reducer consumes GameAction. It does not need to know whether the action came from a button, a touch control, a key, or a model-generated help card.

## Recipe 2: Discover and track connected controllers

The current GameController documentation exposes typed main-actor message identifiers in addition to notification names. Verify the exact spelling imported by the selected SDK before compiling a target.

~~~swift
import GameController
import Foundation

@MainActor
final class ControllerHub {
    private(set) var controllers: [GCController] = GCController.controllers()
    private(set) var current: GCController?
    private var observations: [NSObjectProtocol] = []

    init() {
        current = GCController.current

        let center = NotificationCenter.default
        observations.append(
            center.addObserver(of: GCController.self, for: .didConnect) {
                [weak self] message in
                self?.refresh(adding: message.controller)
            }
        )
        observations.append(
            center.addObserver(of: GCController.self, for: .didDisconnect) {
                [weak self] message in
                self?.refresh(removing: message.controller)
            }
        )
        observations.append(
            center.addObserver(of: GCController.self, for: .didBecomeCurrent) {
                [weak self] message in
                self?.current = message.controller
                self?.refresh()
            }
        )
    }

    deinit {
        for observation in observations {
            NotificationCenter.default.removeObserver(observation)
        }
    }

    func startDiscovery() {
        GCController.startWirelessControllerDiscovery { }
    }

    func stopDiscovery() {
        GCController.stopWirelessControllerDiscovery()
    }

    private func refresh(
        adding controller: GCController? = nil,
        removing controllerToRemove: GCController? = nil
    ) {
        _ = controller
        _ = controllerToRemove
        controllers = GCController.controllers()
        current = GCController.current
    }

    private func refresh() {
        controllers = GCController.controllers()
    }
}
~~~

This model owns lifecycle only. It does not decide that the current controller is a player account, and it does not retain a controller as durable user identity.

## Recipe 3: Assign a player index deliberately

Player index is an app-owned multiplayer association. Assign it only after the product has chosen an ownership policy.

~~~swift
import GameController

func assignFirstTwoPlayers(_ controllers: [GCController]) {
    guard controllers.count >= 2 else { return }

    controllers[0].playerIndex = .index1
    controllers[1].playerIndex = .index2
}

func releasePlayer(_ controller: GCController) {
    controller.playerIndex = .indexUnset
}
~~~

The LED behavior of a controller, where supported, is feedback from the system. It is not proof that a game’s player routing is correct; exercise both controllers and verify the resulting semantic actions.

## Recipe 4: Read a coherent live-input snapshot

The modern live-input route supports capture. Use one snapshot when multiple values must represent the same moment.

~~~swift
import GameController

struct StickState: Equatable, Sendable {
    var x: Float
    var y: Float
    var primaryPressed: Bool
}

func readSnapshot(from controller: GCController) -> StickState? {
    let snapshot = controller.input.capture()
    guard
        let stick = snapshot.dpads[.leftThumbstick],
        let primary = snapshot.buttons[.a]
    else {
        return nil
    }

    return StickState(
        x: stick.xAxis.value,
        y: stick.yAxis.value,
        primaryPressed: primary.pressedInput.isPressed
    )
}
~~~

The exact generic element and value properties depend on the selected SDK’s imported interfaces. Keep the snapshot boundary even if a legacy profile API is used for a particular target.

## Recipe 5: Normalize an analog stick

Apply dead zones and thresholds in deterministic code before emitting domain actions.

~~~swift
import CoreGraphics

struct NormalizedStick: Sendable, Equatable {
    var x: Float
    var y: Float
}

func normalizeStick(x: Float, y: Float, deadZone: Float = 0.15) -> NormalizedStick {
    let length = sqrt(x * x + y * y)
    guard length > deadZone, length > 0 else {
        return NormalizedStick(x: 0, y: 0)
    }

    let scaled = min((length - deadZone) / (1 - deadZone), 1)
    let unitX = x / length
    let unitY = y / length
    return NormalizedStick(x: unitX * scaled, y: unitY * scaled)
}
~~~

Do not tune the dead zone from one controller and silently assume it is correct for every device. Record the controller model, profile, and measured fixture in the proof record.

## Recipe 6: Handle a semantic button callback

Use callbacks for event-driven input such as confirm or pause, then forward a typed action.

~~~swift
import GameController

final class ButtonAdapter {
    private var controller: GCController?

    func install(on controller: GCController, send: @escaping (GameAction) -> Void) {
        self.controller = controller
        guard let primary = controller.input.buttons[.a] else { return }

        primary.pressedInput.pressedDidChangeHandler = {
            _, _, isPressed in
            guard isPressed else { return }
            send(.primary)
        }
    }

    func remove() {
        controller = nil
    }
}
~~~

The callback is an input signal, not an authorization boundary. The domain reducer should decide whether primary is valid in the current context.

## Recipe 7: Buffer high-rate input states

Use a bounded queue when missing intermediate changes would affect correctness.

~~~swift
import GameController

final class BufferedInputAdapter {
    func install(on controller: GCController) {
        let input = controller.input
        input.inputStateQueueDepth = 20
        input.inputStateAvailableHandler = { input in
            while let state = input.nextInputState() {
                if let changed = state.changedElements() {
                    for element in changed {
                        _ = element
                    }
                } else {
                    // The queue overflowed or the diff is unknown.
                    // Emit a diagnostic and move to a safe policy.
                }
            }
        }
    }
}
~~~

Queue depth is a product and performance parameter. Measure the input rate, processing time, frame rate, and overflow behavior on the actual device and controller combination.

## Recipe 8: Observe system-level remapping

Honor the system mapping by default. Rebuild the visible action map after the user changes it.

~~~swift
import GameController
import Foundation

final class MappingObserver {
    private var observation: NSObjectProtocol?

    func start(onChange: @escaping () -> Void) {
        observation = NotificationCenter.default.addObserver(
            forName: .GCControllerUserCustomizationsDidChange,
            object: nil,
            queue: .main
        ) { _ in
            onChange()
        }
    }

    func stop() {
        if let observation {
            NotificationCenter.default.removeObserver(observation)
            self.observation = nil
        }
    }
}
~~~

If the app provides its own remap editor, use the documented unmapped live-input view or profile remapping APIs as the physical source. Validate collisions and recovery controls before applying a mapping.

## Recipe 9: Describe the active controller legend

Build a legend from the active physical elements instead of static vendor artwork.

~~~swift
import GameController

struct ControlHint: Identifiable, Sendable {
    let id: String
    let actionTitle: String
    let localizedInputName: String?
    let sfSymbolsName: String?
}

func hint(
    actionTitle: String,
    actionID: String,
    element: GCPhysicalInputElement
) -> ControlHint {
    ControlHint(
        id: actionID,
        actionTitle: actionTitle,
        localizedInputName: element.localizedName,
        sfSymbolsName: element.sfSymbolsName
    )
}
~~~

The semantic title remains stable while the input name and symbol change with the active controller. Provide an accessibility label that explains the action in words.

## Recipe 10: Read motion only when supported

Motion is optional and must have a non-motion alternative.

~~~swift
import GameController

struct MotionSample: Sendable, Equatable {
    var rotationX: Double
    var rotationY: Double
    var rotationZ: Double
}

func readMotion(from controller: GCController) -> MotionSample? {
    guard let motion = controller.motion else { return nil }
    guard motion.hasRotationRate else { return nil }

    let rate = motion.rotationRate
    return MotionSample(
        rotationX: rate.rotationRateX,
        rotationY: rate.rotationRateY,
        rotationZ: rate.rotationRateZ
    )
}
~~~

Check the exact field names in the selected SDK’s GCRotationRate interface. Do not enable a motion-only action until the capability and calibration state are valid.

## Recipe 11: Read keyboard and mouse profiles

Keyboard and mouse are separate devices with separate lifecycles.

~~~swift
import GameController

func keyboardIsAvailable() -> Bool {
    GCKeyboard.coalesced?.keyboardInput != nil
}

func mouseIsAvailable() -> Bool {
    GCMouse.current?.mouseInput != nil
}

func installEscapeHandler(send: @escaping (GameAction) -> Void) {
    guard
        let input = GCKeyboard.coalesced?.keyboardInput,
        let escape = input.button(forKeyCode: .escape)
    else { return }

    escape.pressedInput.pressedDidChangeHandler = {
        _, _, isPressed in
        guard isPressed else { return }
        send(.cancel)
    }
}
~~~

Use keyboard commands and pointer behavior as alternate adapters into the same action model. Do not make a controller connection hide the touch or pointer route.

## Recipe 12: Project controller state into SwiftUI

Keep the raw controller outside the view tree and expose a small main-actor projection.

~~~swift
import GameController
import Observation

@MainActor
@Observable
final class ControllerViewModel {
    private(set) var isConnected = false
    private(set) var profileName = "Touch controls"
    private(set) var currentController: GCController?

    func update(controller: GCController?) {
        currentController = controller
        isConnected = controller != nil
        profileName = profile(for: controller)
    }

    private func profile(for controller: GCController?) -> String {
        guard let controller else { return "Touch controls" }
        if controller.extendedGamepad != nil { return "Extended Gamepad" }
        if controller.microGamepad != nil { return "Micro Gamepad" }
        if controller.gamepad != nil { return "Gamepad" }
        return "Other controller profile"
    }
}
~~~

The view model should render a status, legend, focus destination, and fallback. It should not sample every frame from a SwiftUI body evaluation.

## Recipe 13: Add an explicit remap proposal boundary

An on-device model can propose a mapping, but typed deterministic code owns validation and application.

~~~swift
struct RemapProposal: Sendable, Equatable {
    var mapping: [String: String]
    var explanation: String
    var profileDescription: String
    var mappingRevision: Int
}

enum RemapValidation: Equatable {
    case valid
    case conflict(actionIDs: [String])
    case unsupportedInput(name: String)
    case stale
}

func validate(
    _ proposal: RemapProposal,
    currentProfile: String,
    currentRevision: Int
) -> RemapValidation {
    guard proposal.profileDescription == currentProfile else { return .stale }
    guard proposal.mappingRevision == currentRevision else { return .stale }

    let values = proposal.mapping.values
    let hasDuplicates = Set(values).count != values.count
    return hasDuplicates ? .conflict(actionIDs: Array(proposal.mapping.keys)) : .valid
}
~~~

Never pass a model-generated selector, key path, closure, or framework method to an execution layer. Keep the model’s output as reviewable data.

## Recipe 14: Test with a deterministic semantic adapter

Unit tests should exercise the domain without pretending to be a physical device.

~~~swift
struct FakeInputSource {
    var actions: [GameAction] = []

    mutating func pressPrimary() {
        actions.append(.primary)
    }

    mutating func move(x: Float, y: Float) {
        actions.append(.move(x: x, y: y))
    }
}

func reduce(_ action: GameAction, state: inout String) {
    switch action {
    case .primary:
        state = "primary applied"
    case .move:
        state = "moving"
    default:
        state = "other action"
    }
}
~~~

Use the [proof matrix](../60-verification/55-gamecontroller-input-proof-matrix.md) to pair this fixture with physical-device evidence for hardware claims.

## Sources

- [Game Controller](https://developer.apple.com/documentation/gamecontroller)
- [GCController](https://developer.apple.com/documentation/gamecontroller/gccontroller)
- [GCController.DidDisconnectMessage](https://developer.apple.com/documentation/gamecontroller/gccontroller/diddisconnectmessage)
- [GCController.DidBecomeCurrentMessage](https://developer.apple.com/documentation/gamecontroller/gccontroller/didbecomecurrentmessage)
- [Discovering game controllers](https://developer.apple.com/documentation/gamecontroller/discovering-game-controllers)
- [Handling input events](https://developer.apple.com/documentation/gamecontroller/handling-input-events)
- [GCControllerLiveInput](https://developer.apple.com/documentation/gamecontroller/gccontrollerliveinput)
- [GCControllerLiveInput.unmapped](https://developer.apple.com/documentation/gamecontroller/gccontrollerliveinput/unmapped)
- [GCDevicePhysicalInput](https://developer.apple.com/documentation/gamecontroller/gcdevicephysicalinput)
- [GCDevicePhysicalInputState](https://developer.apple.com/documentation/gamecontroller/gcdevicephysicalinputstate)
- [GCPhysicalInputElement](https://developer.apple.com/documentation/gamecontroller/gcphysicalinputelement)
- [GCPhysicalInputProfile](https://developer.apple.com/documentation/gamecontroller/gcphysicalinputprofile)
- [GCExtendedGamepad](https://developer.apple.com/documentation/gamecontroller/gcextendedgamepad)
- [GCMicroGamepad](https://developer.apple.com/documentation/gamecontroller/gcmicrogamepad)
- [GCMotion](https://developer.apple.com/documentation/gamecontroller/gcmotion)
- [GCKeyboard](https://developer.apple.com/documentation/gamecontroller/gckeyboard)
- [GCKeyboardInput](https://developer.apple.com/documentation/gamecontroller/gckeyboardinput)
- [GCMouse](https://developer.apple.com/documentation/gamecontroller/gcmouse)
- [GCMouseInput](https://developer.apple.com/documentation/gamecontroller/gcmouseinput)
- [Configuring game controllers](https://developer.apple.com/documentation/xcode/configuring-game-controllers)
- [Human Interface Guidelines: Game controls](https://developer.apple.com/design/human-interface-guidelines/game-controls)
- [SwiftUI FocusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
