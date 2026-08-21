# ImageRenderer and export proof matrix

Use this matrix to keep a rendered artifact, a live SwiftUI surface, a system share handoff, and a release claim separate.

## Claim-to-evidence matrix

| Claim | Required evidence | What it proves | What it does not prove |
| --- | --- | --- | --- |
| ImageRenderer works in the target | Current docs, Xcode SDK, named target, compile fixture | Symbols/imports/isolation/availability compile | Physical fidelity or every OS |
| Size is correct | Export schema, point/scale assertions, output dimensions | Declared point/pixel contract | Quality on every destination |
| Artifact is deterministic | Immutable snapshot and injected fixtures | Differences have known inputs | Source correctness or comprehension |
| Fields are approved | Redaction map and output inspection | Tested fixture omits private data | Future fields without schema review |
| PDF is complete | URL, page bounds, open/selection checks | File is inspectable and bounded | Accessibility, print fidelity, destination acceptance |
| Platform content fallback works | Dedicated export view/framework exporter fixtures | No silent claim of live web/media/UI capture | Visual equivalence with live content |
| Live screen is native | Semantic UI task run | Controls/state/accessibility do not depend on artifact | Artifact fidelity |
| Transfer route is typed | Transferable, UTType, filename, representation tests | Intended data/file route is advertised | Every destination accepts it |
| File lifetime is safe | Staging policy, cancellation/relaunch cleanup run | Transfer does not use a view-local or deleted file | All provider behavior |
| AI is bounded | Versioned schema, validator, invalid/refusal fixtures | Model cannot bypass export/privacy policy | Model quality or availability |
| Appearance adapts | Light/dark/contrast/Dynamic Type/RTL/reduced effects artifacts | Meaning and legibility survive tested settings | Every locale/device |
| Physical output is acceptable | Signed device, max fixture, memory/thermal/share run | Named workload behaved on those devices | All devices or production scale |
| Release contains the route | Archive/resource/UTType/privacy inspection | Packaged target matches tested route | Review approval or delivery |

## Fixture matrix

Maintain deterministic fixtures for empty/loading/partial/stale/confirmed/edited/completed/failed/canceled source states; current and replaced source revision; light/dark/increased contrast/reduced transparency; small/large/max point sizes; screen and explicit scales; short/long/localized/RTL/Dynamic Type text; transparent/opaque/gradient/symbol/image/material-like content; supported SwiftUI and excluded UIKit/web/media/control content; image encoder and missing-resource failures; one- and multi-page PDFs; DataRepresentation/FileRepresentation/ProxyRepresentation; no destination/cancellation/cleanup; and valid, unknown, out-of-range, private, stale, refused, and unavailable AI proposals.

Inject dates, UUIDs, locale, color scheme, and revision. Compare semantic fields, artifact metadata, dimensions, and privacy assertions separately from pixels.

## Accessibility task matrix

| Setting/input | Task | Evidence |
| --- | --- | --- |
| VoiceOver | Read source/value/unit/freshness; render/share/cancel/recover | Order, labels, traits, announcements |
| Voice Control | Activate named render/share/retry actions | No pixel-only target |
| Switch Control | Reach controls and complete/cancel | Logical focus and recovery |
| Full Keyboard Access | Focus/activate/cancel/return | Focus visibility and keyboard action |
| Dynamic Type | Read source and status at large sizes | No clipped critical state |
| Contrast/transparency | Read live controls and state | Glass/material preserves hierarchy |
| Reduce Motion | Complete without animation dependency | Static/gentle path remains truthful |
| RTL/localization | Read and operate; inspect filename/page layout | Direction and strings adapt |

The artifact also needs a title, state label, unit/date policy, user-visible filename/content type, and a semantic or selectable alternative where the image removes important information.

## Physical-device packet

    app/build, Xcode/SDK, deployment target
    device model/OS, appearance/accessibility settings
    source fixture/revision, export view, point size/scale
    color mode/opacity/dynamic range, render duration
    output dimensions/bytes/hash, memory/thermal notes
    PDF open/selection result, share destination
    cancellation/cleanup result, unproven scope

A simulator or preview can validate fixtures and layout. It cannot close physical display-scale, memory, thermal, battery, touch, share-destination, or document-provider claims.

## Release packet and stop conditions

Retain target membership, deployment target, imports, image/font/color assets, UTType/filename policy, privacy review, extension/provider configuration, archive inspection, and any TestFlight/store artifact evidence. Do not call the route shipped because an image rendered or a share sheet appeared.

Stop when the route screenshots a mutable navigation hierarchy; assumes UIKit/web/media content is represented; leaves point/scale/opacity/color implicit; includes unreviewed AI/private metadata; treats an opened PDF as accessibility proof; treats SharePreview as bytes; deletes a staged file too early; treats a share preview as destination acceptance; or claims physical/release behavior without matching evidence.

## Sources

- [ImageRenderer](https://developer.apple.com/documentation/swiftui/imagerenderer)
- [ImageRenderer.proposedSize](https://developer.apple.com/documentation/swiftui/imagerenderer/proposedsize)
- [ImageRenderer.scale](https://developer.apple.com/documentation/swiftui/imagerenderer/scale)
- [ImageRenderer.isOpaque](https://developer.apple.com/documentation/swiftui/imagerenderer/isopaque)
- [ImageRenderer.cgImage](https://developer.apple.com/documentation/swiftui/imagerenderer/cgimage)
- [ImageRenderer.render(rasterizationScale:renderer:)](https://developer.apple.com/documentation/swiftui/imagerenderer/render%28rasterizationscale%3Arenderer%3A%29)
- [EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues)
- [EnvironmentValues.displayScale](https://developer.apple.com/documentation/swiftui/environmentvalues/displayscale)
- [EnvironmentValues.colorScheme](https://developer.apple.com/documentation/swiftui/environmentvalues/colorscheme)
- [EnvironmentValues.dynamicTypeSize](https://developer.apple.com/documentation/swiftui/environmentvalues/dynamictypesize)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [TransferRepresentation](https://developer.apple.com/documentation/coretransferable/transferrepresentation)
- [DataRepresentation](https://developer.apple.com/documentation/coretransferable/datarepresentation)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [ProxyRepresentation](https://developer.apple.com/documentation/coretransferable/proxyrepresentation)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [Human Interface Guidelines: Activity views](https://developer.apple.com/design/human-interface-guidelines/activity-views)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
