# Evidence and Verification Language

## The evidence ladder

Use precise claims. Each level proves something different:

| Evidence | It can prove | It cannot prove by itself |
| --- | --- | --- |
| Source review | The documented behavior and constraints are understood. | The app compiles or behaves correctly. |
| Code inspection | The intended route appears in source. | Runtime permissions, hardware, or rendering. |
| Swift compile/build | The selected target compiles for the chosen SDK. | Real camera, Apple Intelligence, purchase, or accessibility behavior. |
| Preview | A view renders in a controlled configuration. | Navigation lifecycle, device performance, permissions, or release packaging. |
| Simulator run | Deterministic UI and some flows work in a virtual device. | Physical camera/sensors, model availability, thermal behavior, real signing, or App Store review. |
| Signed physical device | The target hardware and entitlement path works for the tested scenario. | Every device family, locale, OS update, or production backend state. |
| TestFlight/App Store | Distribution and release configuration works through Apple’s delivery path. | Long-term production health or every user’s environment. |
| Production evidence | The deployed route works for real users under a defined observation window. | A permanent guarantee. |

## Claim language

Prefer:

- “Source-backed: Apple documents X.”
- “Build verified for target Y.”
- “Simulator verified for scenario Z.”
- “Physical-device verification still required for camera/model/purchase behavior.”
- “Unavailable path tested and fallback shown.”

Avoid:

- “Apple Intelligence works” when only a mock response was tested.
- “Liquid Glass is correct” when a custom blur was applied without checking system settings.
- “Ready to ship” when no signed-device, accessibility, privacy, or release checks exist.

## Sources

- [SwiftUI performance analysis](https://developer.apple.com/documentation/swiftui/performance-analysis)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
