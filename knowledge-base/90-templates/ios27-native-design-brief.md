# iOS 27 Native Design Brief

Use this template for a new native surface or a visual refresh that must feel
at home on Apple platforms while preserving an original product identity. It
turns Liquid Glass depth into a functional hierarchy and keeps platform,
accessibility, input, and evidence decisions explicit.

## 1. Outcome and target matrix

- Person and context:
- One-sentence outcome:
- Primary action and consequence of failure:
- Domain truth versus derived presentation:
- Supported targets: iOS, iPadOS, macOS/Catalyst, watchOS, games, iPhone Duo, or other:
- Minimum OS and SDK:
- Xcode/Swift toolchain:
- System-owned surfaces involved: toolbar, tab bar, sheet, search, widget, Live Activity, notification, App Intent, share/file, or none:

| Target | Window/display posture | Input modes | Primary layout | Platform-specific behavior | Fallback or unsupported state |
| --- | --- | --- | --- | --- | --- |
| iPhone |  | Touch, VoiceOver |  |  |  |
| iPad |  | Touch, keyboard, pointer, Pencil |  |  |  |
| Mac/Catalyst |  | Keyboard, pointer, menus |  |  |  |
| Watch |  | Touch, Digital Crown, short glance |  |  |  |
| Game/other |  | Controller, touch, keyboard, pointer |  |  |  |

## 2. HIG and platform adaptation

Read the target-specific HIG page before choosing a shared composition. The
iPhone Duo route is hardware-sensitive: record what is documented, mark what
is only announced or beta-specific as `to-verify`, and never infer fold,
outer-display, or hinge behavior from a normal iPhone preview.

| HIG route | What it changes in this design | Evidence/status |
| --- | --- | --- |
| [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles) | Purpose, agency, responsibility, familiarity, flexibility, simplicity, craft, and delight |  |
| [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios) | Reachability, orientation, Dark Mode, Dynamic Type, compact hierarchy, permissioned capabilities |  |
| [Designing for iPadOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ipados) | Multitasking, large display, pointer/keyboard/Pencil, drag and drop, window adaptation |  |
| [Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos) | Desktop conventions, menus, multiple windows/displays, pointer and keyboard posture |  |
| [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos) | Glanceable single-screen tasks, shallow navigation, Crown, complications, Always On |  |
| [Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games) | Controller/input mapping, safe areas, aspect ratios, readable text, customizable controls |  |
| [Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo) | Inner/outer display, fold avoidance, control placement, sheet and posture changes | `to-verify` unless the exact supported SDK/device is exercised |
| [Apple Design Resources](https://developer.apple.com/design/resources/) | iOS/iPadOS/macOS UI kits, SF Symbols, Icon Composer, device bezels, supplied assets |  |

Apply the eight current design principles as review questions:

- Purpose: does every major surface help the stated outcome?
- Agency: can the person understand, undo, cancel, and recover?
- Responsibility: are privacy, permissions, uncertainty, and destructive effects legible?
- Familiarity: do standard controls and platform conventions behave as expected?
- Flexibility: does the task survive size, input, language, accessibility, and posture changes?
- Simplicity: is hierarchy doing the work before material or animation?
- Craft: are timing, hit regions, content, performance, and real-device behavior finished?
- Delight: is visual polish serving the task rather than decorating it?

## 3. Spatial hierarchy and Liquid Glass

Describe the design as layers before describing colors or radii:

| Layer | Owns | Design rule | This screen |
| --- | --- | --- | --- |
| Content | Records, media, reading, editing, game world | Remains primary and legible; do not turn dense content into glass |  |
| Functional | Actions, selection, transient controls, status | Floats above content only when the control relationship is real |  |
| System/navigation | Navigation, toolbar, tab, search, sheet, system surfaces | Let SwiftUI/UIKit adopt the system treatment first |  |
| Decorative | Atmosphere, branding, illustration | Never carries essential meaning or replaces contrast |  |

For the raised/spatial Liquid Glass feel:

- Prefer standard SwiftUI/UIKit navigation, tab, toolbar, search, sheet, and
  controls so the OS owns the current material, edge behavior, and interaction
  response.
- Use custom `glassEffect` only for a genuinely functional custom element;
  choose `regular`, `clear`, or no effect from the content and legibility
  requirement, not from a desire to decorate every card.
- Use `GlassEffectContainer` only for related glass elements whose grouping or
  morphing communicates a real relationship. Give participants stable identity
  and keep the transition understandable when motion is reduced.
- Create depth through separation of content and functional layers, readable
  contrast, restrained translucency, and purposeful state/morphing behavior.
  Do not fake a 3D extrusion, stack translucent panels over every region, or
  use blur/color/motion as the only carrier of meaning.
- Test the same surface with reduced transparency, increased contrast, Reduce
  Motion, Dynamic Type, localization, light/dark appearance, and changing
  content behind the material. Record a non-glass or reduced-effects fallback.

| Element | System-owned or custom | Glass variant/container | Why it is functional | Non-glass/reduced-effects behavior |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 4. Composition and behavior

- Navigation/container route:
- Primary hierarchy from top to bottom:
- Standard controls selected:
- Toolbar items and overflow/minimization behavior:
- Scroll and safe-area behavior:
- Compact-width and large-text behavior:
- Keyboard/pointer/controller/Pencil/Crown path:
- Gesture conflicts and visible alternative:
- Motion or morphing purpose and cancellation behavior:
- Haptic purpose and no-hardware fallback:

### State matrix

| State | User-visible meaning | Primary action | Accessibility announcement/focus | Persistence/side effect | Evidence |
| --- | --- | --- | --- | --- | --- |
| Empty |  |  |  |  |  |
| Loading/partial |  |  |  |  |  |
| Ready |  |  |  |  |  |
| Permission/unavailable |  |  |  |  |  |
| Error/offline |  |  |  |  |  |
| Review/confirmation |  |  |  |  |  |
| Saved/completed |  |  |  |  |  |

## 5. Accessibility and adaptability contract

- Semantic role, label, value, hint, traits, and custom actions:
- Reading/focus order:
- Minimum hit region and keyboard/controller equivalent:
- Dynamic Type and text truncation policy:
- VoiceOver, Voice Control, Switch Control, and Assistive Access path:
- Contrast and increased-contrast behavior:
- Reduce Motion behavior:
- Reduce Transparency behavior:
- Color-independent and gesture-independent meaning:
- Localization, pluralization, RTL, and long-string behavior:
- Orientation, split view, window, safe-area, and posture behavior:

## 6. iOS 27 API and fallback gates

For each new API, record the exact SDK signature, minimum OS, deployment
fallback, and proof level. Use the [iOS 27 SwiftUI and SDK refresh](../10-swiftui/13-ios27-swiftui-refresh.md)
as the route index.

| API/behavior | SDK and runtime gate | Earlier fallback | Source/compile evidence | Runtime/device evidence |
| --- | --- | --- | --- | --- |
| Toolbar overflow/priorities/minimization |  | Standard toolbar behavior |  |  |
| `Document`/async document I/O |  | `FileDocument`/`ReferenceFileDocument` |  |  |
| Reorder/swipe containers |  | `List` editing/visible actions |  |  |
| `AsyncImage` request/session behavior |  | Feature-owned loader |  |  |
| `MetricManager` performance reports |  | `MXMetricManager` compatibility route |  |  |

## 7. Verification receipt

Record what each layer actually proves:

| Evidence | Environment and command/task | Result/artifact | Does not prove |
| --- | --- | --- | --- |
| Official source/HIG | URL and review date |  | Target compilation or runtime |
| SDK/interface | Xcode, SDK, platform, architecture |  | App configuration or UI behavior |
| Compile/type-check | Target/scheme/configuration |  | Physical ergonomics or system delivery |
| Preview/UI test | Fixtures, settings, destination |  | Physical accessibility/performance |
| Physical device | Device, OS/build, settings, task |  | Store approval or universal support |
| Signed release | Archive/TestFlight/build |  | Production rollout or App Review |

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Materials HIG](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes)
- [iOS and iPadOS 27 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes)
