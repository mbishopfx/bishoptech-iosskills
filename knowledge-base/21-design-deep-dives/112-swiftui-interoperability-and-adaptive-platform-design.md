# SwiftUI interoperability and adaptive-platform design

## Design objective

Native polish is not only a visual treatment. It is the feeling that a
screen responds correctly to its target, window, language, input method,
accessibility settings, system surface, and lifecycle.

Use this design loop:

    user outcome
      -> target task slice
      -> shared meaning/state
      -> environment and available space
      -> native SwiftUI composition
      -> smallest UIKit/system bridge
      -> adaptive input and accessibility
      -> preview fixture
      -> device/release proof

A single codebase can share a domain contract without forcing every platform
to share the same hierarchy. An iPhone detail screen, an iPad source/review
workspace, a Catalyst window, a visionOS window, and a watchOS glance can all
represent the same approved record while using different containers and input
routes.

## 1. Design the task slice per target

Begin with the outcome, not the device frame:

| Target | Native design question |
| --- | --- |
| iPhone | What is the shortest focused sequence and how does it recover from interruption? |
| iPad | Does persistent context, split view, selection, keyboard, pointer, or Pencil shorten the task? |
| Mac Catalyst | What changes for window resizing, menus, shortcuts, pointer precision, and selection? |
| visionOS | Is spatial context necessary, and can the person interact comfortably and accessibly? |
| watchOS | What can be understood and completed in a glance with minimal navigation? |

Share:

- domain identity and revisions;
- authorization and privacy rules;
- validation and commit commands;
- loading/error/cancellation meanings;
- AI candidate schema and provenance;
- system handoff payloads where they remain valid.

Allow surfaces to diverge in:

- navigation hierarchy;
- toolbar/tab/sidebar placement;
- card/list/table density;
- input and focus;
- window/scene/companion behavior;
- material and Liquid Glass placement;
- reduced-effects fallback;
- accessible reading order.

Do not call a layout “universal” because it compiles for multiple targets.

## 2. Preview the design system as environments

A useful design review has named fixtures:

| Fixture | What to inspect |
| --- | --- |
| Compact light | Primary task, toolbar, hit regions, text wrapping |
| Regular dark | Context/detail relationship, material hierarchy, contrast |
| Large type | Reflow, control labels, image crop, action reachability |
| RTL | Leading/trailing placement, directional symbols, alignment |
| Reduced transparency | Opaque/stronger surface fallback and same task |
| Reduced motion | Static state and focus continuity |
| Model unavailable | Manual route, source content, honest message |
| UIKit bridge failure | Empty/error/fallback without broken shell |
| Candidate stale | Source revision mismatch and rerun route |
| Keyboard/pointer | Focus, menus, shortcuts, hover supplement |

Use Xcode preview traits, parameters, and scene-specific configuration when
they improve the fixture matrix. Keep each fixture deterministic and
searchable. A preview should expose a design decision, not merely create a
pretty canvas snapshot.

## 3. Visual hierarchy across environments

Preserve semantic levels even when the composition changes:

| Semantic level | iPhone | iPad/Catalyst | Spatial/wrist surface |
| --- | --- | --- | --- |
| Primary content | Focused detail or feed | Persistent source/detail or table | Glanceable value or spatial object |
| Primary action | Toolbar, button, sheet action | Toolbar/menu/keyboard action | One clear action or defer/handoff |
| Context | Secondary metadata | Inspector/sidebar/table columns | Short label/status |
| State | Inline error/progress/retry | Persistent state alongside context | Concise state and recovery |
| Decoration | Low-emphasis image/shape | Supporting background or material | Usually reduced or omitted |

The visual effect should adapt with the hierarchy. Standard materials can
separate content. Liquid Glass can group functional actions. Do not make
content itself look like a control because the platform has a new material.

## 4. UIKit interoperability as a design boundary

Choose UIKit when a specific system capability, existing screen, or framework
surface requires it. The bridge should feel like part of the product's
semantics:

- SwiftUI owns the route, current source, draft/candidate state, and action
  meaning;
- UIKit owns the wrapped view/controller's internal mechanics;
- the coordinator translates callbacks into typed feature events;
- the domain validates and commits results;
- accessibility labels and focus are designed across both trees;
- the bridge has an explicit create/update/teardown story.

A UIKit bridge should not alter the meaning of the task. If a system picker
returns no selection, that is not the same as empty content. If a controller
is dismissed, that is not the same as accepted. If a view is torn down, that
is not the same as saved.

## 5. Adaptive layout decisions

Use environment and layout APIs as evidence about the available composition,
not as device-name switches.

Preferred order:

1. semantic SwiftUI container/control;
2. natural layout with stacks, grids, lists, and layout proposals;
3. ViewThatFits or AnyLayout for equivalent compositions;
4. size classes for broad hierarchy changes;
5. target/platform conditional code for genuinely different frameworks or
   system surfaces;
6. UIKit/AppKit/WatchKit/visionOS bridge at the capability boundary.

Avoid these design traps:

- fixed heights around text and generated AI copy;
- a “regular width equals iPad” assumption;
- a different domain state in each target branch;
- a glass capsule that becomes a hidden overflow menu in compact space;
- a preview fixture that never includes a large localized string;
- moving the primary action out of the accessibility order when the layout
  changes;
- relying on device orientation instead of the view's available proposal.

## 6. Typography, localization, and direction

A native design system has no fixed “safe” string length. Use system text
styles and flexible layout. Test:

- title and button strings that expand substantially;
- pluralization and locale-specific formatting;
- right-to-left layout direction;
- date/time/number/currency formatting;
- mixed-script text and text with combining marks;
- generated AI content that arrives in multiple partial updates;
- UIKit labels and SwiftUI Text at the same Dynamic Type size;
- truncation and accessibility reading of a clipped value.

Use leading/trailing semantics and directional symbols. If a symbol has an
intrinsic direction, verify its RTL behavior or choose a semantic alternative.
Do not put important text into a rasterized preview or a custom-drawn glass
label.

## 7. Input and accessibility composition

Build one action matrix:

| Action | SwiftUI | UIKit/host | Alternate input |
| --- | --- | --- | --- |
| Activate | Button/NavigationLink/Toggle | UIControl target-action or controller delegate | VoiceOver action, Voice Control, keyboard/pointer |
| Edit | TextField/TextEditor/Form | UIKit text input/selection | Focus, hardware keyboard, Switch Control |
| Select | List/table selection | cell/collection selection | keyboard range, pointer, accessibility |
| Cancel | visible Button/dismiss route | controller cancellation | Escape/back/VoiceOver action |
| Commit | typed feature command | validated callback | keyboard shortcut/menu where appropriate |
| Inspect AI result | detail/review route | controller preview result | focusable candidate + source/provenance |

When wrapping UIKit inside SwiftUI, check for duplicate accessibility elements
and for a focus path that enters the UIKit view but cannot leave it. When
hosting SwiftUI inside UIKit, check that the host does not collapse labels,
clip large text, or trap the person inside a cell.

## 8. Liquid Glass and interoperability

A consistent visual system uses the platform's system surfaces first:

1. navigation, tabs, toolbars, sheets, controls, and platform bars;
2. content and media;
3. functional Liquid Glass group where it improves action hierarchy;
4. decorative treatment only when it does not compete with content.

A UIKit view inside a glass group may have its own background and clipping.
Inspect it over light/dark and colorful content. Provide a standard Material,
opaque, or native-control fallback when reduced transparency or contrast
requires it.

Do not use a SwiftUI glass wrapper to imitate a private Apple screen, conceal
an unowned UIKit controller, or make a generated candidate look approved.
Glass should group an action and preserve the same action without the effect.

## 9. AI-aware adaptive composition

An on-device AI feature should have the same meaning on each target but not
necessarily the same surface:

| AI state | iPhone | iPad/Catalyst | visionOS/watchOS |
| --- | --- | --- | --- |
| Preparing | Progress + cancel in focused screen | Persistent progress alongside source | Short status/defer or spatial progress |
| Partial | Candidate row with stable identity | Side-by-side source/candidate | Limited preview or handoff |
| Ready | Review sheet/detail with accept/reject/edit | Persistent review pane and keyboard path | Comfortable inspect/confirm route |
| Stale | “Source changed; run again” | Source revision mismatch in context | Defer/rerun explanation |
| Unavailable | Manual path and reason | Model/device state next to source | Handoff or supported fallback |

Preserve sourceID and sourceRevision across the UI boundary. A UIKit image
picker, SwiftUI review screen, and system handoff must agree on which source
was analyzed. A preview fixture should exercise the same stale and
model-unavailable states without invoking the actual model.

## 10. Design review questions

- Does the target have one clear task slice?
- Which state/meaning is shared, and which hierarchy/input is deliberately
  target-specific?
- Does the layout adapt to available space without fixed-height text traps?
- Are locale, RTL, Dynamic Type, contrast, motion, and transparency part of
  the visual review?
- Is UIKit present because it owns a real capability rather than a cosmetic
  imitation?
- Are make/update/teardown and callback ownership visible?
- Can the person complete the action without animation, color, pointer hover,
  or a hidden gesture?
- Does Liquid Glass group a functional control and keep content primary?
- Does an AI candidate remain a candidate until explicit review and commit?
- Does the preview prove only a deterministic render, with device/system
  evidence kept separate?

## Design token guidance

Keep cross-platform tokens semantic:

| Token | Shared meaning | Platform variation |
| --- | --- | --- |
| primaryContent | Most important information | Size, placement, and container |
| primaryAction | Next user outcome | Button/toolbar/menu/shortcut/crown route |
| supportingContext | Explanation and metadata | Density and reading order |
| reviewCandidate | Uncommitted suggestion | Badge/pane/sheet/spatial review |
| functionalSurface | Action grouping | Native material/Glass/window/toolbar |
| fallbackSurface | Same task without effect/model | Opaque/material/manual route |
| focusState | Current input target | Touch/pointer/keyboard/VoiceOver/spatial |
| unavailableState | Capability cannot run | Reason and alternate route |

A token must describe meaning, not only a color or corner radius. The target
surface can change geometry and material without changing what “primaryAction”
or “reviewCandidate” means.

## Sources

- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Designing for iPadOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ipados)
- [Designing for Mac Catalyst](https://developer.apple.com/design/human-interface-guidelines/mac-catalyst)
- [Designing for visionOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos)
- [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues)
- [UserInterfaceSizeClass](https://developer.apple.com/documentation/swiftui/userinterfacesizeclass)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [UIKit integration](https://developer.apple.com/documentation/swiftui/uikit-integration)
- [UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [UIHostingController](https://developer.apple.com/documentation/swiftui/uihostingcontroller)
- [UIHostingConfiguration](https://developer.apple.com/documentation/swiftui/uihostingconfiguration)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftUI accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
