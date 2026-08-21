# Custom layout and adaptive Liquid Glass proof matrix

Use this matrix for Layout, ProposedViewSize, ViewThatFits, AnyLayout, container-relative sizing, GeometryReader, safe-area edge groups, and responsive functional glass.

## Claim-to-evidence matrix

| Claim | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| Custom Layout compiles | Named target, SDK, imports, availability, compile log | API/signature/target correctness | Device behavior or comfort |
| Proposal behavior is intentional | zero/infinity/unspecified and one-axis fixtures | Layout responds to measured inputs | Every width/locale |
| Placement is bounded | Returned size, placement assertions, debug overlays | Children fit the declared bounds | Touch comfort or visual quality |
| State survives arrangement changes | Stable IDs, focus/draft fixtures, UI test | Identity and user work survive branch changes | Production interruptions |
| ViewThatFits choices are truthful | Ordered alternatives and branch fixtures | First fitting composition preserves task | It is the best design for every person |
| AnyLayout preserves identity | Horizontal/vertical transition test | Same subviews remain associated | Every animation/device |
| Safe-area edge group is correct | Keyboard/rotation/scroll indicator/split-view tests | Content and controls are not obscured | Physical touch comfort |
| Glass remains legible | Light/dark/contrast/reduced-transparency device run | Functional controls retain hierarchy | All displays or future OS |
| Accessibility survives | VoiceOver/Voice Control/Switch Control/keyboard tasks | Person can complete the task non-visually/alternatively | Universal accessibility |
| AI layout proposal is bounded | Typed schema, validator, invalid/refusal fixtures | Model cannot emit code or remove critical action | Model quality |
| Custom layout performs | Max fixture, signed physical device, performance trace | Named workload’s frame/memory/thermal result | All devices or battery lifetime |
| Release contains the route | Archive/resource/target inspection | Packaged route matches test | Review/production delivery |

## Fixture matrix

Include:

- zero, infinity, unspecified, finite-width/unspecified-height, and finite-height/unspecified-width proposals;
- empty, one, many, long, localized, RTL, and Dynamic Type-expanded labels;
- primary/secondary/overflow action priority values;
- compact, regular, split-view, keyboard-visible, rotation, and container-relative frames;
- insertion/removal/reordering while focused or editing;
- idle/loading/partial/ready/stale/failed/canceled source state;
- light/dark/increased contrast/reduced transparency/Reduce Motion;
- custom Layout on/off fallback and missing resource/availability branches;
- valid, unknown, out-of-range, stale, refused, and unavailable AI layout proposals;
- VoiceOver focus, Voice Control naming, Switch Control order, keyboard focus, pointer, and touch fixtures.

Compare semantic action identity, state, bounds, focus, and accessibility tree separately from pixels.

## Physical-device packet

    app/build, Xcode/SDK, deployment target
    device/OS, platform/window size, appearance/accessibility settings
    proposal fixture, layout mode, subview count, strings/localization
    glass/material route, safe-area/keyboard state
    frame/hitch observation, memory/thermal/battery notes
    touch/pointer/keyboard/haptic observations
    fallback result, unproven scope

Simulator and previews can exercise deterministic layout fixtures. They do not close claims about physical touch, safe-area feel, glass rendering, haptics, thermal behavior, or production device coverage.

## Stop conditions

Do not call the route ready when a measurement pass mutates domain state; a custom layout clips or hides critical controls; a ViewThatFits branch drops the only recovery action; AnyLayout destroys focus/draft identity; GeometryReader is used as unbounded screen geometry; a glass edge overlay covers content or keyboard; reduced effects remove meaning; AI emits geometry/code/asset authority; or physical/release claims exceed the recorded evidence.

## Sources

- [Layout](https://developer.apple.com/documentation/swiftui/layout)
- [LayoutSubview](https://developer.apple.com/documentation/swiftui/layoutsubview)
- [LayoutSubviews](https://developer.apple.com/documentation/swiftui/layoutsubviews)
- [ProposedViewSize](https://developer.apple.com/documentation/swiftui/proposedviewsize)
- [LayoutValueKey](https://developer.apple.com/documentation/swiftui/layoutvaluekey)
- [LayoutProperties](https://developer.apple.com/documentation/swiftui/layoutproperties)
- [ViewDimensions](https://developer.apple.com/documentation/swiftui/viewdimensions)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [GeometryReader](https://developer.apple.com/documentation/swiftui/geometryreader)
- [containerRelativeFrame(_:alignment:_:)](https://developer.apple.com/documentation/swiftui/view/containerrelativeframe%28_%3Aalignment%3A_%3A%29)
- [safeAreaInset(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [SafeAreaRegions](https://developer.apple.com/documentation/swiftui/safearearegions)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
