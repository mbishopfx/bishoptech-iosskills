# Source Freshness Log

## 2026-08-19 initial scout

Checked official Apple documentation for:

- SwiftUI overview, state, navigation, layout, animation, accessibility, and previews.
- Liquid Glass overview, adoption guidance, custom effects, `Glass`, `GlassEffectContainer`, and the Landmarks sample.
- Foundation Models overview, `LanguageModelSession`, model availability, guided generation/tool calling routes, and updates.
- Apple Intelligence and machine-learning technology overview.
- Core ML, Vision, VisionKit, Speech, Translation, Natural Language, and Sound Analysis.
- App Intents, app entities, entity queries, App Shortcuts, WidgetKit, and ActivityKit.
- SwiftData, StoreKit, maps/location, media, sensors, security, networking, and spatial frameworks.

## Refresh triggers

Recheck the source registry before implementation when:

- the selected SDK or deployment target changes;
- an API is marked beta, deprecated, or changed in an update page;
- Foundation Models behavior changes after an OS update;
- a feature depends on Apple Intelligence availability, language assets, camera hardware, or an entitlement;
- an App Store, privacy, or permission requirement is involved;
- a framework route has not been revisited in the current project.

## 2026-08-22 Meta Wearables extension

Checked the public official Meta surface for:

- DAT iOS 0.9.0 repository/release and changelog, including iOS 17.2 minimum, `DeviceSession`/camera lifecycle, Display capability/input, MockDevice, and stream terminal behavior.
- DAT Android 0.9.0 repository/changelog for cross-platform route comparison without assuming symbol parity.
- Meta Wearables Web App repository, Display/performance references, public HTTPS/600×600/additive/input constraints, and the official browser simulator listing.
- Wearables Developer Center routes for iOS integration, API reference, Mock Device Kit, Web Apps, terms, acceptable use, and MCP access.
- The public full `llms.txt?full=true` reference, which broadens the static map to the DAT module families, HFP/A2DP audio, IMU and Web App boundaries, version dependencies, release channels, MockDevice UI-test server, and current App Store warning. Treat machine-index names as `to-verify` until the pinned Swift package exposes them.
- The upstream DAT iOS README, conventions, sample-app, debugging, live-debugging-MCP, and plugin surfaces. The reviewed public commit is `225f64ff1617e7acc8c407bb8d3ee132f7263d00`; the README’s older iOS prerequisite wording conflicts with the 0.9.0 changelog’s iOS 17.2 minimum, so the pinned package/changelog wins for build decisions.
- The public Wearables MCP endpoint. The upstream guidance names `search_dat_docs` and `search_webapps_docs`; public docs lookup is source evidence only and does not grant account, release-channel, compile, or physical-device proof.

The current public snapshot does not establish a runtime “Gen 3” mapping. The Developer Center’s authenticated/API details, physical glasses, Developer Mode/release channel, signed app, live Web App, and production behavior remain `to-verify` gates.

## Meta refresh triggers

Recheck the Meta registry before implementation when:

- the DAT iOS/Android tag, package products, minimum OS, or changelog changes;
- camera/audio/session/Display/MockDevice symbols or model enums change;
- Web App display dimensions, input, metadata, simulator, or hosting requirements change;
- a new Ray-Ban/Oakley/Meta product generation is mentioned;
- developer-preview, terms, acceptable-use, release-channel, or publishing access changes;
- authenticated Developer Center or MCP access becomes available for a task that needs exact API details.

## Sources

- [Apple Developer Documentation updates](https://developer.apple.com/documentation/Updates)
- [Foundation Models updates](https://developer.apple.com/documentation/Updates/FoundationModels)
- [Apple Developer Documentation](https://developer.apple.com/documentation/)
