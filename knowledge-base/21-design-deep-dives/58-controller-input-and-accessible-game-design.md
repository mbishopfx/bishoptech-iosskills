# Controller input, accessible game design, and native glass surfaces

A controller-aware app should feel like the same product when the input device changes. The game or utility owns the semantic actions; touch, controller, keyboard, mouse, Apple Pencil, and assistive technologies are different ways to reach those actions.

Apple’s Human Interface Guidelines are especially clear about two ideas: physical controllers are optional, and the platform’s default interaction method still matters. A polished iOS 26 experience can show a connected controller, use its glyphs, and add a Liquid Glass status or remapping surface without turning the entire app into a controller-only imitation of a console UI.

Use this guide with the [GameController framework deep dive](../42-framework-deep-dives/38-gamecontroller-physical-input-and-motion.md), the [capability route](../50-capability-recipes/61-gamecontroller-input-route.md), the [proof matrix](../60-verification/55-gamecontroller-input-proof-matrix.md), the [code recipes](../70-code-recipes/73-gamecontroller-input-recipes.md), and the existing [Liquid Glass interaction guidance](../20-liquid-glass/06-ai-review-shell-and-glass-state.md).

## Start with the platform’s default interaction

Physical controller support is an enhancement on iPhone and iPad. Touch remains available, expected, and important for people who do not own a controller or who cannot use one comfortably.

Design the action model first:

~~~text
semantic action
  -> touch gesture or button
  -> controller element
  -> keyboard shortcut
  -> pointer or Pencil gesture
  -> assistive technology command
~~~

The action model should not know whether the person reached it with a thumbstick or a tap. Input adapters translate into the same domain action. This makes it possible to:

- keep progress and saved state intact when a controller disconnects;
- test the game with deterministic semantic actions;
- preserve a touch route for onboarding and fallback;
- provide alternate actions for reduced motion or motor accessibility;
- explain the same action in a controller legend, VoiceOver label, and tutorial.

If a controller is required on tvOS or visionOS, state that requirement clearly and handle a missing controller gracefully. On iPhone, avoid making a critical path controller-only unless the product’s purpose genuinely requires it.

## Control language that matches the device

Use the connected controller’s labeling scheme when showing a control hint. A standard semantic name such as “button A” helps code share a profile; it does not guarantee that every controller shows the same letter, color, or physical artwork.

Prefer:

- the controller’s localized element name;
- the controller’s SF Symbols name;
- an app-owned semantic action label;
- a short instruction such as “Press to confirm”;
- the current controller profile when displaying a legend.

Avoid:

- hard-coded Xbox or PlayStation artwork in a generic route;
- using A, X, or R1 as the only explanation of an action;
- labeling a control with a symbol that is not present on the connected device;
- showing a stale legend after the current controller changes;
- treating an input name as a player identity.

The HIG’s expected UI behavior outside gameplay is a useful baseline:

| Controller input | Default UI meaning |
| --- | --- |
| A or primary activation | Activate a control |
| B or secondary/cancel | Cancel or go back |
| Left shoulder | Navigate to the previous section |
| Right shoulder | Navigate to the next section |
| Thumbstick or d-pad | Move selection |
| Menu | Open settings or pause |
| Home or logo | Reserved for system controls |

Adapt this to the platform and controller labeling. Do not intercept a system-reserved control merely because it is convenient.

## Connection and absence states

Controller UI should appear at the right level of attention:

| State | User-facing behavior |
| --- | --- |
| No controller | Keep the touch/default route fully usable |
| Controller connected | Show a quiet status or control hint; do not interrupt a task |
| Pairing requested | Explain what to do and how to cancel |
| Unsupported profile | Name the limitation and provide a fallback |
| Current controller changed | Refresh glyphs and control hints |
| Disconnected during play | Preserve domain state and switch to touch or pause safely |
| System remap changed | Refresh the action map and acknowledge the new mapping |
| Controller required | Use a clear connect prompt and a non-destructive exit |

Do not use a modal “controller connected” announcement for every connection. A compact status surface, a changed control legend, or a one-time onboarding hint is usually enough.

## Liquid Glass without losing game clarity

Liquid Glass is a native surface language, not a reason to put a translucent card over every control. For controller-aware UI, use glass where it clarifies state:

- a compact controller status pill;
- a floating “controls” or “remap” sheet;
- a context-sensitive help panel;
- a review card for an AI-suggested mapping;
- a settings panel that can morph from a button or menu action.

Keep high-frequency gameplay controls and important labels visually stable. A controller legend should remain readable while the scene moves behind it. Test it with bright backgrounds, dark backgrounds, Dynamic Type, increased contrast, reduced transparency, and a connected controller with unfamiliar labels.

Useful glass composition rules:

1. Establish the content hierarchy before adding glass.
2. Keep one glass container for related controls when the layout calls for a shared surface.
3. Use semantic buttons, toggles, menus, and focusable views inside the surface.
4. Preserve hit targets and focus indicators; glass is not a hit target.
5. Keep the material’s contrast and legibility stronger than the scene behind it.
6. Prefer system transitions and bounded morphing over decorative constant motion.
7. Let the surface disappear when it is not useful.

For an iOS 26 target, verify the exact SwiftUI Liquid Glass APIs in the selected SDK. The knowledge base treats the native SwiftUI surface APIs as version-sensitive; it does not treat a visual imitation or a screenshot as proof of correct system integration.

## Gameplay controls versus app navigation

Gameplay can use analog values, dead zones, acceleration curves, and repeat rates. App navigation should remain predictable:

- d-pad and thumbstick move focus;
- primary activation selects;
- cancel returns;
- menu opens the app’s settings or pause surface;
- shoulder buttons move between tabs or sections when that behavior is visible;
- the touch fallback exposes the same destination without requiring a controller.

Do not use a gameplay stick curve for settings navigation. Do not make a settings screen depend on a hidden focus path. When the app enters a menu, pause the gameplay input route or explicitly scope which actions remain active.

Use focus state as a UI concern. The focused element should be visible, have a clear selected or pressed state, and remain reachable if a person increases text size or uses VoiceOver.

## Remapping as a reviewable product surface

System remapping should be honored by default. If the app adds its own mapping layer, show it as an editable semantic table:

~~~text
Move
  physical input: left thumbstick
  displayed glyph: current controller symbol
  source: system mapping

Confirm
  physical input: primary face button
  displayed glyph: current controller symbol
  source: app mapping
~~~

A remap flow should:

- show the action being changed;
- wait for one physical input;
- display its localized name and glyph;
- detect duplicates and conflicts;
- protect pause, exit, and other recovery paths;
- offer reset to the system/default mapping;
- retain the mapping only after explicit confirmation;
- update when the system customization-change event arrives.

Do not force people to memorize a long list of raw control names. Use a grouped action catalog and a short “test this mapping” step.

## Accessibility and personalization

Apple’s game design guidance recommends letting people personalize control mapping, type size, motion intensity, and sound balance. Treat these as product features rather than a late audit.

Controller-aware accessibility work includes:

- VoiceOver labels for actions, not only glyph names;
- visible text or spoken help for unfamiliar symbols;
- Dynamic Type that does not clip or hide the control legend;
- sufficient contrast over dynamic game content;
- reduced-motion alternatives for animated controller hints;
- no action that requires simultaneous presses when a simpler alternative is possible;
- adjustable dead zones, sensitivity, hold duration, and repeat behavior where appropriate;
- touch and keyboard alternatives for controller actions;
- clear focus and selection states;
- subtitles and non-audio feedback for important events;
- an accessible remapping path that does not depend on fast reaction time.

The controller’s SF Symbol can assist sighted recognition, but it is not a replacement for a meaningful accessibility label. A symbol, color, and sound should not be the only way to communicate a critical state.

## Keyboard, pointer, and Apple Pencil parity

On iPad, a physical keyboard, mouse, trackpad, or Apple Pencil may be the person’s preferred input. On Mac, keyboard and pointer input are default. Use the same semantic action model, but tune each interaction:

- keyboard commands should be discoverable and customizable;
- avoid repurposing familiar system shortcuts;
- pointer hover can expose a tooltip or focus affordance without stealing controller focus;
- Pencil drawing or pointing should not be treated as a keyboard-style activation unless the product makes that mapping clear;
- a controller connection should not make the pointer disappear from a settings screen.

For a game UI, a pointer can select a control directly while a controller moves focus. Keep both routes visible and deterministic.

## AI-generated control help

On-device AI can make controller support more approachable:

- explain the current profile in plain language;
- generate a short tutorial from a fixed action catalog;
- suggest a conflict-free remap based on a person’s declared preferences;
- turn a validated action map into a printable or accessible help view;
- summarize which inputs are currently unavailable.

Keep the model outside the control authority:

~~~text
validated controller profile
-> deterministic action catalog
-> on-device model proposal
-> user review
-> deterministic mapping validation
-> app-owned mapping
~~~

The model must not read arbitrary raw controller history by default, infer sensitive traits from play patterns, or invoke gameplay actions without a visible and deterministic path. A generated explanation becomes stale when the controller, system mapping, or app mode changes; attach the profile and mapping revision to the proposal.

## Responsive layout and system surfaces

Controller legends are often transient. A good native layout can move from:

- a compact overlay in landscape gameplay;
- a bottom sheet in portrait;
- a sidebar on iPad;
- a focused panel on Apple TV;
- a window or ornament in visionOS where the target supports it.

Use safe areas and platform conventions. Do not place touch controls below the Home indicator or under the Dynamic Island. HIG guidance for touch controls recommends comfortable thumb reach, visible press states, appropriate hit sizes, and less clutter when a control is unavailable.

For a responsive SwiftUI composition:

1. keep semantic action data independent from geometry;
2. choose the legend layout from available width and input source;
3. keep a short version for transient surfaces;
4. expose a full accessible list for VoiceOver and settings;
5. preserve focus when the layout changes;
6. test portrait, landscape, split view, Stage Manager, and an external display where supported.

## Design review checklist

Before calling a controller-aware screen native and ready for build work, review:

- Does the default platform input still work?
- Does the legend match the connected controller’s labeling?
- Are semantic actions separate from physical elements?
- Does the current-controller change refresh visible hints?
- Does a disconnect preserve or safely pause the task?
- Is the mapping editable without losing recovery controls?
- Does the surface survive Dynamic Type and increased contrast?
- Is reduced motion respected?
- Can VoiceOver describe the action without relying on a glyph?
- Does Liquid Glass clarify state instead of covering content?
- Is any AI output reviewable, bounded, and tied to a mapping revision?
- Have unfamiliar profiles and no-controller states been designed?

## Sources

- [Human Interface Guidelines: Game controls](https://developer.apple.com/design/human-interface-guidelines/game-controls)
- [Human Interface Guidelines: Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Human Interface Guidelines: Dynamic Type](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Human Interface Guidelines: Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)
- [Game Controller](https://developer.apple.com/documentation/gamecontroller)
- [Discovering game controllers](https://developer.apple.com/documentation/gamecontroller/discovering-game-controllers)
- [GCPhysicalInputElement](https://developer.apple.com/documentation/gamecontroller/gcphysicalinputelement)
- [GCPhysicalInputProfile](https://developer.apple.com/documentation/gamecontroller/gcphysicalinputprofile)
- [Configuring game controllers](https://developer.apple.com/documentation/xcode/configuring-game-controllers)
- [SwiftUI focusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [SwiftUI focused](https://developer.apple.com/documentation/swiftui/view/focused%28_%3A%29)
- [SwiftUI focusable](https://developer.apple.com/documentation/swiftui/view/focusable%28_%3A%29)
- [SwiftUI FocusSection](https://developer.apple.com/documentation/swiftui/view/focussection%28%29)
- [SwiftUI keyboardShortcut](https://developer.apple.com/documentation/swiftui/view/keyboardshortcut%28_%3A%29)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [SwiftUI accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [SwiftUI glassEffect](https://developer.apple.com/documentation/swiftui/view/glasseffect%28_%3Ain%3A%29)
- [SwiftUI GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
