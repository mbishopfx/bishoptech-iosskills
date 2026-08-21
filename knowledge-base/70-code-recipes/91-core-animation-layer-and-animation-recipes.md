# Core Animation layer and animation recipes

These are compile-oriented route sketches for custom Core Animation visuals, UIKit property animators, display-linked work, and SwiftUI interoperation. They are not claimed to compile in this documentation-only workspace.

Before using them:

- name the animation owner for every property;
- keep model/UI state outside the layer presentation tree;
- disable implicit actions for setup and reconciliation;
- honor reduced motion, reduced flashing, reduced transparency, and contrast;
- stop display links and tasks when the view disappears;
- measure on physical devices and test the signed target.

## 1. Layer-backed progress ring

Use a real semantic label or control around the visual ring. The layer only renders the bounded progress value.

~~~swift
import UIKit
import QuartzCore

final class ProgressRingView: UIView {
    private let ringLayer = CAShapeLayer()
    var progress: CGFloat = 0 {
        didSet {
            applyProgress(animated: true)
        }
    }

    override init(frame: CGRect) {
        super.init(frame: frame)
        isAccessibilityElement = true
        accessibilityLabel = "Progress"

        ringLayer.fillColor = UIColor.clear.cgColor
        ringLayer.strokeColor = UIColor.systemBlue.cgColor
        ringLayer.lineWidth = 8
        ringLayer.lineCap = .round
        layer.addSublayer(ringLayer)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        ringLayer.frame = bounds
        let inset = ringLayer.lineWidth / 2
        ringLayer.path = UIBezierPath(
            ovalIn: bounds.insetBy(dx: inset, dy: inset)
        ).cgPath
        applyProgress(animated: false)
    }

    private func applyProgress(animated: Bool) {
        let value = min(max(progress, 0), 1)
        let oldValue = ringLayer.strokeEnd
        ringLayer.strokeEnd = value

        guard animated, oldValue != value else { return }
        let animation = CABasicAnimation(keyPath: "strokeEnd")
        animation.fromValue = oldValue
        animation.toValue = value
        animation.duration = 0.22
        animation.timingFunction = CAMediaTimingFunction(
            name: .easeOut
        )
        ringLayer.add(animation, forKey: "progress")
    }
}
~~~

The accessibility value should be updated from the app’s progress model. The layer’s strokeEnd is not the canonical progress value.

## 2. Disable implicit actions during reconciliation

Use a transaction when applying layout or reuse state that should appear immediately.

~~~swift
func applyImmediately(
    to layer: CALayer,
    opacity: Float,
    cornerRadius: CGFloat
) {
    CATransaction.begin()
    CATransaction.setDisableActions(true)
    layer.opacity = opacity
    layer.cornerRadius = cornerRadius
    CATransaction.commit()
}
~~~

Use explicit animation only for an intentional user-visible transition. This prevents a reused cell or a SwiftUI update from animating from stale geometry.

## 3. Coordinate multiple layers with a transaction

Use a transaction for a visual group, not as a substitute for a domain transaction.

~~~swift
func reveal(
    contentLayer: CALayer,
    chromeLayer: CALayer,
    completion: @escaping () -> Void
) {
    CATransaction.begin()
    CATransaction.setAnimationDuration(0.28)
    CATransaction.setAnimationTimingFunction(
        CAMediaTimingFunction(name: .easeInEaseOut)
    )
    CATransaction.setCompletionBlock(completion)

    contentLayer.opacity = 1
    chromeLayer.transform = CATransform3DIdentity

    CATransaction.commit()
}
~~~

The completion describes visual completion. If the screen also saves a record, await that operation separately.

## 4. Animate a layer property and update the model layer

Set the model value first or immediately alongside the animation. Do not rely on removed-on-completion to preserve the visible end state.

~~~swift
func move(
    layer: CALayer,
    to position: CGPoint,
    duration: CFTimeInterval
) {
    let start = layer.presentation()?.position ?? layer.position
    layer.position = position

    let animation = CABasicAnimation(keyPath: "position")
    animation.fromValue = start
    animation.toValue = position
    animation.duration = duration
    animation.timingFunction = CAMediaTimingFunction(name: .easeOut)
    layer.add(animation, forKey: "position")
}
~~~

If the animation is interrupted, remove it and decide whether the model should remain at the final target or settle back to the current interaction state.

## 5. Spring animation for a bounded state change

Use a spring for a physical-feeling transition whose end state has clear meaning.

~~~swift
func settle(
    layer: CALayer,
    transform: CATransform3D
) {
    let animation = CASpringAnimation(keyPath: "transform")
    animation.fromValue = layer.presentation()?.transform
        ?? layer.transform
    animation.toValue = transform
    animation.damping = 18
    animation.stiffness = 260
    animation.mass = 1
    animation.initialVelocity = 0
    animation.duration = animation.settlingDuration

    layer.transform = transform
    layer.add(animation, forKey: "settle")
}
~~~

Use a non-spring fallback under Reduce Motion when the transition is large or depth-like. Keep the spring parameters in a design token rather than scattering them through feature code.

## 6. Shape path and gradient layers

Use shape and gradient layers for a contained visual accent. The semantic value belongs to the owning view.

~~~swift
func makeAccentLayer(bounds: CGRect) -> CALayer {
    let container = CALayer()
    container.frame = bounds

    let gradient = CAGradientLayer()
    gradient.frame = bounds
    gradient.colors = [
        UIColor.systemBlue.cgColor,
        UIColor.systemPurple.cgColor
    ]
    gradient.startPoint = CGPoint(x: 0, y: 0.5)
    gradient.endPoint = CGPoint(x: 1, y: 0.5)

    let mask = CAShapeLayer()
    mask.frame = bounds
    mask.path = UIBezierPath(
        roundedRect: bounds,
        cornerRadius: 18
    ).cgPath
    gradient.mask = mask

    container.addSublayer(gradient)
    return container
}
~~~

Avoid using a custom layer as the only contrast or focus indicator. Add a semantic label, control, or accessibility representation.

## 7. Interactive UIViewPropertyAnimator

Use UIViewPropertyAnimator when a UIKit view transition follows a gesture.

~~~swift
final class CardTransitionController {
    private var animator: UIViewPropertyAnimator?

    func begin(for view: UIView) {
        animator?.stopAnimation(true)

        let nextFrame = view.frame.offsetBy(dx: 0, dy: -80)
        let nextAlpha: CGFloat = 0

        let animator = UIViewPropertyAnimator(
            duration: 0.32,
            dampingRatio: 0.86
        ) {
            view.frame = nextFrame
            view.alpha = nextAlpha
        }
        animator.isInterruptible = true
        animator.pausesOnCompletion = true
        self.animator = animator
        animator.startAnimation()
    }

    func update(fractionComplete: CGFloat) {
        animator?.fractionComplete = min(max(fractionComplete, 0), 1)
    }

    func cancel() {
        animator?.stopAnimation(true)
        animator = nil
    }

    func finish() {
        animator?.continueAnimation(
            withTimingParameters: nil,
            durationFactor: 1
        )
    }
}
~~~

In a real feature, retain the starting geometry and reconcile the view if the gesture cancels. Do not let a paused animator retain a view controller longer than the feature needs.

## 8. CADisplayLink with explicit invalidation

Use a display link only for work that needs display cadence. Keep the callback cheap and invalidate it when the owner disappears.

~~~swift
import QuartzCore

final class DisplayLinkDriver: NSObject {
    private var displayLink: CADisplayLink?
    private(set) var phase: Double = 0

    func start() {
        guard displayLink == nil else { return }
        let link = CADisplayLink(
            target: self,
            selector: #selector(step(_:))
        )
        link.preferredFrameRateRange = CAFrameRateRange(
            minimum: 30,
            maximum: 60,
            preferred: 60
        )
        link.add(to: .main, forMode: .common)
        displayLink = link
    }

    func pause() {
        displayLink?.isPaused = true
    }

    func resume() {
        displayLink?.isPaused = false
    }

    func stop() {
        displayLink?.invalidate()
        displayLink = nil
    }

    @objc private func step(_ link: CADisplayLink) {
        let delta = link.targetTimestamp - link.timestamp
        guard delta > 0 else { return }
        phase += delta
        phase.formTruncatingRemainder(dividingBy: 1)
        // Publish a bounded visual value to the renderer.
    }

    deinit {
        displayLink?.invalidate()
    }
}
~~~

The actual frame rate can differ from the preferred range. Use a consistently maintainable range and test Low Power Mode, thermal pressure, and accessibility settings.

## 9. SwiftUI bridge for a layer-backed view

Keep SwiftUI as the state owner and make the UIKit view update idempotently.

~~~swift
import SwiftUI
import UIKit

struct LayerAccentRepresentable: UIViewRepresentable {
    let isActive: Bool
    let reduceMotion: Bool

    func makeUIView(context: Context) -> LayerAccentView {
        LayerAccentView()
    }

    func updateUIView(
        _ view: LayerAccentView,
        context: Context
    ) {
        view.apply(
            isActive: isActive,
            animated: !reduceMotion && context.transaction.animation != nil
        )
    }

    static func dismantleUIView(
        _ view: LayerAccentView,
        coordinator: ()
    ) {
        view.stopAnimations()
    }
}

final class LayerAccentView: UIView {
    private let accentLayer = CALayer()

    override init(frame: CGRect) {
        super.init(frame: frame)
        layer.addSublayer(accentLayer)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        accentLayer.frame = bounds.insetBy(dx: 8, dy: 8)
    }

    func apply(isActive: Bool, animated: Bool) {
        let target: Float = isActive ? 1 : 0
        if animated {
            let animation = CABasicAnimation(keyPath: "opacity")
            animation.fromValue = accentLayer.presentation()?.opacity
                ?? accentLayer.opacity
            animation.toValue = target
            animation.duration = 0.22
            accentLayer.opacity = target
            accentLayer.add(animation, forKey: "active")
        } else {
            CATransaction.begin()
            CATransaction.setDisableActions(true)
            accentLayer.opacity = target
            CATransaction.commit()
        }
    }

    func stopAnimations() {
        accentLayer.removeAllAnimations()
    }
}
~~~

The bridge should also expose semantic labels/actions if the layer communicates a user-facing state. In a real target, use the relevant SwiftUI transaction and environment values rather than treating a Boolean as the entire design.

## 10. Reduced-motion policy

Read the environment in SwiftUI and choose a semantic fallback:

~~~swift
struct MotionAwareAccent: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let isActive: Bool

    var body: some View {
        LayerAccentRepresentable(
            isActive: isActive,
            reduceMotion: reduceMotion
        )
        .accessibilityLabel(isActive ? "Active" : "Inactive")
    }
}
~~~

For large moves, replace the animation with an immediate update, a short opacity change, a color/weight change, or a semantic announcement. Do not keep a flashing layer visible simply because the visual code expects a completion.

## 11. Presentation-layer observation for a gesture handoff

Use presentation values only to preserve visual continuity when an interaction interrupts an animation.

~~~swift
func beginDrag(layer: CALayer) -> CGPoint {
    let current = layer.presentation()?.position ?? layer.position
    layer.removeAllAnimations()
    layer.position = current
    return current
}
~~~

The returned point belongs to the transient visual interaction. Save the user’s final intent in the feature model, then animate or reconcile the layer to that model value.

## 12. Recipe proof checklist

- Compile the layer, transaction, property animator, display-link, and SwiftUI bridge in a named target.
- Repeat updates and verify no duplicate animations or display links appear.
- Interrupt, reverse, cancel, background, rotate, and rebuild the view.
- Verify model-layer state after every path.
- Test Reduce Motion, dim flashing lights, reduced transparency, increased contrast, large text, VoiceOver, and alternate input.
- Measure frame time, hitches, memory, energy, and thermal behavior on physical devices.
- Verify the preferred frame-rate range against actual device cadence.
- Keep display-link callback work bounded and invalidate it on teardown.
- Confirm Liquid Glass remains SwiftUI/system-owned and custom layers remain accents or renderer details.
- Verify signed artifact target membership and the absence of test-only visual bypasses.

## Related routes

- [Core Animation layers, transactions, timing, and display cadence](../42-framework-deep-dives/56-core-animation-layers-transactions-and-timing.md)
- [Core Animation native motion and Liquid Glass design](../21-design-deep-dives/76-core-animation-native-motion-and-glass-design.md)
- [Core Animation layer and display-link route](../50-capability-recipes/79-core-animation-layer-and-display-link-route.md)
- [Core Animation motion proof matrix](../60-verification/73-core-animation-motion-proof-matrix.md)

## Sources

- [Core Animation](https://developer.apple.com/documentation/quartzcore)
- [CALayer](https://developer.apple.com/documentation/quartzcore/calayer)
- [CABasicAnimation](https://developer.apple.com/documentation/quartzcore/cabasicanimation)
- [CASpringAnimation](https://developer.apple.com/documentation/quartzcore/caspringanimation)
- [CATransaction](https://developer.apple.com/documentation/quartzcore/catransaction)
- [CAMediaTimingFunction](https://developer.apple.com/documentation/quartzcore/camediatimingfunction)
- [CADisplayLink](https://developer.apple.com/documentation/QuartzCore/CADisplayLink?changes=_9)
- [CADisplayLink preferred frame rate range](https://developer.apple.com/documentation/quartzcore/cadisplaylink/preferredframeraterange)
- [UIViewPropertyAnimator](https://developer.apple.com/documentation/uikit/uiviewpropertyanimator)
- [UIViewRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewrepresentablecontext)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityDimFlashingLights](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilitydimflashinglights)
- [accessibilityRepresentation](https://developer.apple.com/documentation/swiftui/view/accessibilityrepresentation%28representation%3A%29)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
