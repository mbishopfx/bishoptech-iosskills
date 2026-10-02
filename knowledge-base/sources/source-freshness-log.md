# Source Freshness Log

## 2026-10-01 iOS 27.2 beta and current SwiftUI documentation refresh

Checked the current official Apple sources:

- [Xcode SDK and system requirements](https://developer.apple.com/xcode/system-requirements), [Xcode 27.2 beta release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes), and [iOS/iPadOS 27.2 beta release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27_2-release-notes). Apple's requirements page currently lists Xcode 27.2 beta 2 with the iOS 27.2 SDK and Swift 6.4 as the newest prerelease lane. Xcode 27.0 / iOS 27.0 / Swift 6.4 remains the toolchain selected on this machine; `xcrun simctl list runtimes` returned no installed simulator runtimes on this check.
- The [SwiftUI updates](https://developer.apple.com/documentation/updates/swiftui) page, including its June and September 2026 sections, and the [What’s new in SwiftUI](https://developer.apple.com/swiftui/whats-new/) overview.
- The beta-marked `ArrangementView`/`ArrangementViewStyle` split and overlay routes, plus `GeometryProxy.reservedRegions` and `UIView.ReservedRegion` for occlusion/division regions such as a camera or hinge. These sources are not evidence that the APIs are available in the locally selected SDK or a shipping runtime.
- iOS/iPadOS 27.2 beta's AppTrackingTransparency alternative expanded prompt and annual re-prompt behavior for specified EU regions. This remains prerelease guidance and requires a final-release and policy recheck before shipping.

The targeted declarations recorded in the 2026-09-14 entry were previously type-checked with Xcode 27.0. No app target, iOS 27 simulator, physical device, archive, TestFlight, App Store, or production behavior was exercised in this source refresh. Keep that earlier symbol-level result separate from the new beta-only documentation and the current absence of installed simulator runtimes.

## 2026-09-14 iOS 27/Xcode 27 SwiftUI, HIG, and proof refresh

Checked the official Apple source for:

- Xcode 27, Swift 6.4, and the iOS/iPadOS 27 SDK lane;
- SwiftUI toolbar visibility/overflow/pinning/minimization and status-bar
  color-scheme behavior;
- the `Document`, `ReadableDocument`, and `WritableDocument` APIs and their
  `DocumentGroup`/file-coordination boundary;
- reorderable containers, `swipeActionsContainer`, `AsyncImage` caching and
  URL-session control, interactive `.textSelection`, and the macro-backed
  `@State` behavior;
- MetricKit’s `MetricManager` async sequences and the recommended-new-adoption
  boundary for the original `MXMetricManager` subscriber APIs;
- Liquid Glass system-first adoption, materials, custom effects, grouping,
  accessibility, and reduced-effects behavior as the iOS 26+ design baseline;
- HIG design principles and the iOS, iPadOS, macOS, watchOS, games, iPhone
  Duo, and Apple Design Resources routes.

The current `xcode-select` is Xcode 27.0 with the iOS 27.0 SDK and Swift 6.4.
Xcode 26.4 with the iOS 26.4 SDK and Swift 6.3 remains an explicit
earlier-toolchain fallback. A targeted symbol probe passed with the selected
Xcode 27 toolchain. Local installation paths are intentionally omitted from
the portable record. The available simulator runtime is iOS 26.4, so app-target
build, iOS 27 simulator, physical-device, archive, TestFlight, App Store, and
production evidence remain separate open gates. iPhone Duo remains
hardware-sensitive and `to-verify` without the exact supported device path.

## iOS 27 refresh triggers

Recheck the [iOS 27 SwiftUI and SDK refresh](../10-swiftui/13-ios27-swiftui-refresh.md)
when Xcode 27 changes beta/final API names, a target moves its deployment
target, a new SDK changes document concurrency annotations, MetricKit delivery,
toolbar behavior, or Liquid Glass accessibility behavior, or a real project
exposes an availability/compiler diagnostic.

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
