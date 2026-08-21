# Accessibility and Adaptability Checklist

## Semantics

- [ ] Every action uses a semantic control where possible.
- [ ] Icon-only controls have meaningful labels.
- [ ] Values and states are exposed for toggles, sliders, progress, and selection.
- [ ] Decorative images are hidden or combined appropriately.
- [ ] Custom actions have labels and predictable order.

## Visual adaptability

- [ ] Light and dark appearance.
- [ ] Increased contrast.
- [ ] Reduced transparency.
- [ ] Dynamic Type through the largest supported sizes.
- [ ] Long localized strings.
- [ ] Right-to-left layout where relevant.
- [ ] Content remains legible beneath glass and scroll-edge surfaces.

## Interaction adaptability

- [ ] VoiceOver can complete the core flow.
- [ ] Focus moves intentionally into sheets and after validation.
- [ ] Reduce Motion removes nonessential movement while preserving meaning.
- [ ] Keyboard and pointer input work where the platform supports them.
- [ ] Touch targets remain usable when text or controls grow.
- [ ] No information depends only on color, position, sound, or animation.

## Evidence

- [ ] Record the device/simulator, OS, settings, and scenario.
- [ ] Test at least one physical device for hardware-dependent features.
- [ ] Recheck after major custom visual changes.

## Task and device matrix

- [ ] List the core tasks for every important screen: first launch, empty state, success state, editing, destructive action, error recovery, settings, deep link, and sign-out/deletion where relevant.
- [ ] Run those tasks with VoiceOver, Voice Control, Switch Control, and Assistive Access one at a time; record whether the task can be completed without sighted/touch-only assistance.
- [ ] Test each supported device family, orientation, and input environment that changes layout or interaction. Accessibility Inspector output can guide diagnosis, but it is not a substitute for task completion.
- [ ] Test visual settings as a matrix: largest supported Dynamic Type sizes, increased contrast, reduced transparency, Reduce Motion, color-filter/contrast conditions, dark/light appearance, and localized or right-to-left strings.
- [ ] Test media alternatives: captions, transcripts, audio descriptions, and visual alternatives for audio-only or motion-only information.
- [ ] Record the accessibility setting, device, OS, build, task, observed label/value/trait/focus order, and result for every failure or exception.

## Native controls, Liquid Glass, and system surfaces

- [ ] Prefer `Button`, `Toggle`, `Slider`, `NavigationLink`, `TextField`, `ProgressView`, and other semantic SwiftUI controls before building a gesture-only or custom-drawn equivalent.
- [ ] Keep the accessibility tree meaningful when grouping or representing custom Liquid Glass content; decorative layers should not interrupt the reading order.
- [ ] Give App Intents, widgets, controls, notifications, Live Activities, and extensions labels, values, actions, and deep links that remain understandable outside the main app screen.
- [ ] Verify focus after presenting/dismissing sheets, completing validation, receiving a notification, opening a deep link, and returning from a system surface.
- [ ] Ensure every animation, haptic, color cue, timer, and spatial relationship has a non-motion, non-color, and non-audio-only interpretation when the feature requires it.

## Audit versus human/device evidence

- [ ] Use automated accessibility audits to catch diagnostic issues and track regressions.
- [ ] Use physical-device task testing for VoiceOver, Voice Control, and Switch Control because Apple documents these assistive technologies as unavailable in Simulator.
- [ ] Do not claim “accessible” from a passing audit, a preview, a large-text screenshot, or a single device. The claim must name the tasks, settings, device families, localization coverage, and known exceptions that were actually tested.

## Sources

- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)
- [Apple accessibility](https://developer.apple.com/accessibility/)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [VoiceOver](https://developer.apple.com/documentation/accessibility/voiceover)
- [Optimizing your app for Assistive Access](https://developer.apple.com/documentation/accessibility/optimizing-your-app-for-assistive-access)
- [Accessibility declarations](https://developer.apple.com/documentation/appstoreconnectapi/configuring-accessibility-declarations)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
