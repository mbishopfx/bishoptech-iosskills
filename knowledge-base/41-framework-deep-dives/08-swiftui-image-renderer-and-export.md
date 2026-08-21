# SwiftUI ImageRenderer and user-approved export

## Scope and responsibility boundary

SwiftUI can render a live interface and can also turn a deliberately designed view into an image or another Core Graphics artifact. Those are separate product routes:

    live SwiftUI view -> interaction, accessibility, current scene context
    export snapshot -> deterministic layout, source revision, redaction
    ImageRenderer -> CGImage/UIImage or CGContext drawing
    validated artifact -> Data/FileRepresentation/Transferable
    ShareLink -> user-invoked system sharing

Use this route for achievement cards, receipts, summaries, posters, diagrams, generated previews, print-like pages, and reviewable reports. A successful render is not proof that the live screen, UIKit bridge, media player, web view, glass backdrop, or system interaction was captured faithfully.

The export view should be a small app-owned representation of confirmed state. It should not be a second database view, a copy of the whole navigation hierarchy, or a path for raw model output to become a shareable artifact.

## ImageRenderer surface

Apple documents ImageRenderer as an object that creates images from SwiftUI views. The important route decisions are:

| API/property | Responsibility | Decision |
| --- | --- | --- |
| ImageRenderer<Content> and content | Root renderable SwiftUI view | Use a purpose-built export view with immutable inputs |
| proposedSize | Size proposed to the root view; unspecified uses the original view size | Declare a point size for the artifact |
| scale | Ratio of view points to image pixels; default is 1.0 | Choose an explicit export scale or intentionally use displayScale |
| isOpaque | Whether the image alpha is fully opaque | Set true only when the output really is opaque |
| colorMode | Working color space and storage format | Record and test the export color policy |
| allowedDynamicRange | Dynamic-range limit; Apple documents SDR as the default | Treat HDR as a separate tested capability |
| cgImage / uiImage | Rasterized Core Graphics/UIKit image | Check for nil, then validate dimensions and bytes |
| render(rasterizationScale:renderer:) | Draws current content to an arbitrary CGContext | Use for PDF or a custom Core Graphics destination |
| objectWillChange / isObservationEnabled | Observation when rendered contents may change | Use only for an intentional image stream with an owned cadence |

The current Apple documentation marks the renderer’s image-producing properties and render method as main-actor APIs. Keep view construction, environment decisions, and renderer access on the main actor; move encoding, hashing, file I/O, and upload policy to an appropriate isolated boundary after the artifact exists.

ImageRenderer includes SwiftUI-rendered text, images, shapes, and composites of those types. Apple notes that native platform views such as web views, media players, and some controls are not rendered as their live content and can appear as placeholders. Use a framework-specific export or a dedicated export view for those surfaces.

## Artifact selection

| Outcome | Artifact | Smallest route | Failure state |
| --- | --- | --- | --- |
| Send a visual card | PNG/JPEG or another image type | ImageRenderer -> CGImage/UIImage -> encoded Data -> DataRepresentation | Nil render, encoder failure, wrong size, private field |
| Save a report | PDF | ImageRenderer.render -> PDF CGContext -> validated URL -> FileRepresentation | Page/layout error, incomplete file, unsupported content |
| Move a domain object | Codable/file | Transferable with CodableRepresentation/FileRepresentation | Schema, staging, destination, or cancellation failure |
| Safe fallback | String/URL | ProxyRepresentation | Loss of context or misleading/private projection |
| Show the current screen | Live SwiftUI view | Native UI only | Never infer this from an exported artifact |

An image is not the canonical record. Preserve source revision, export schema, appearance policy, and redaction decision when the artifact matters.

## Build an export view, not a screenshot

Start with a value type containing only the confirmed fields required by the artifact:

    struct ReportExportSnapshot: Sendable, Equatable {
        let title: String
        let value: String
        let status: String
        let sourceRevision: String
    }

Then build a stable view with deliberate size, typography, and state:

    struct ReportExportView: View {
        let snapshot: ReportExportSnapshot

        var body: some View {
            VStack(alignment: .leading, spacing: 16) {
                Text(snapshot.title).font(.title2.weight(.semibold))
                Text(snapshot.value)
                    .font(.system(size: 42, weight: .bold, design: .rounded))
                    .monospacedDigit()
                Label(snapshot.status, systemImage: "checkmark.circle")
            }
            .padding(28)
            .frame(width: 420, alignment: .leading)
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 28))
        }
    }

A functional Liquid Glass group from the live app is not automatically appropriate in a static artifact. Export the semantic card and state label with an explicit material/color treatment that remains legible without the live backdrop, system blur context, hover/touch behavior, or system-owned interaction.

## Size, scale, and environment

SwiftUI measures in points while a rasterized result contains pixels. Set both deliberately:

1. Choose the product artifact size in points.
2. Choose a scale from the destination or current display scale.
3. Record point size, scale, appearance, and dynamic-range policy.
4. Validate pixel dimensions and encoded bytes before sharing.

EnvironmentValues.displayScale can support a screen-faithful preview, but it is not a universal file, print, social-image, or upload policy. Use an explicit product scale for deterministic assets. Use page points and a PDF route for print-like output.

Decide whether the export should match the current interface, use a canonical appearance, include both light/dark variants, or follow a user choice. Inject and test color scheme, contrast, Dynamic Type, locale, layout direction, reduced transparency, and Reduce Motion. Keep the semantic value, unit, timestamp, source revision, and state label independent of pixel appearance.

An artifact containing translucency, gradients, or glass-like effects is not automatically opaque. If the destination needs SDR, choose SDR intentionally. If HDR is a requirement, add encoding, destination, metadata, and physical-display proof.

## Bitmap and PDF routes

Bitmap route:

    confirmed snapshot -> ExportView -> ImageRenderer
    -> proposedSize/scale/color/opacity policy -> cgImage/uiImage
    -> ImageIO/UIImage encoding -> validated Data/File -> ShareLink

A nil image is an ordinary export failure. Preserve the snapshot, explain the state, and offer retry or a text/PDF fallback. Check size, bytes, type, metadata, and source freshness. A static card renders once; an image stream needs its own source clock and cancellation policy.

PDF route:

    ExportView -> ImageRenderer.render -> page-sized CGContext
    -> begin/end page -> close -> open/validate -> FileRepresentation

Apple’s example centers a view on a PDF page and notes that the renderer callback uses a bottom-left coordinate-space origin. Define page size, margins, page breaks, truncation, fonts, reading order, metadata, privacy, page count, memory, and cancellation. Supported SwiftUI text, symbols, lines, shapes, and fills can preserve resolution independence; mixed UIKit/web/media content needs a separate route.

## Transferable and ShareLink

Core Transferable describes how a value participates in sharing, drag and drop, copy and paste, and related system interactions. Compose representations deliberately:

| Representation | Use |
| --- | --- |
| CodableRepresentation | Versioned codable format understood by the receiver |
| DataRepresentation | Bounded binary/text encoding owned by the app |
| FileRepresentation | Staged large visual or PDF artifact |
| ProxyRepresentation | Safe text/URL projection when the full object is inappropriate |

Name the content with Uniform Type Identifiers. Add a suggested filename, exporting condition, and visibility policy where appropriate. ShareLink presents the system sharing interface after a person activates it. SharePreview is presentation metadata, not proof of the transported bytes.

For a large/private item: create an immutable snapshot after confirmation, stage it in an app-owned location, validate type/size/filename/redaction, hand it to ShareLink, keep it alive for the transfer lifetime, and reconcile cancel/failure/cleanup/relaunch. Do not mark a record shared merely because the share sheet appeared.

## Optional on-device AI

AI can propose a title, safe summary, or visual treatment token:

    confirmed source -> bounded context -> typed proposal
    -> allowlist/range/privacy validator -> review if meaning changes
    -> ExportSnapshot -> ImageRenderer

The model must not choose arbitrary SwiftUI code, shader source, asset paths, file URLs, private metadata, or unbounded text. Validate length, semantic fields, contrast, static/motion policy, and source revision. If Foundation Models is unavailable, refuses, exceeds context, or returns invalid structure, use a deterministic default export.

## Lifecycle and target checklist

    idle -> preparing -> rendering -> validating -> ready
    ready -> presenting-share -> transferred | canceled | failed
    failed -> retrying | fallback | dismissed

Keep source-changed, stale, model-unavailable, nil-render, oversized-file, unsupported-destination, canceled-share, expired-file, termination, and accessibility-variant states explicit.

Before copying a recipe, record:

- selected Xcode SDK, deployment target, imports, and availability branches;
- target membership for fonts, images, symbols, colors, shaders, and document/UTType declarations;
- snapshot/redaction/schema/filename/file-lifetime policy;
- live UI accessibility and text/document alternative;
- archive inspection and any extension/provider configuration.

## Evidence rule

Compile the smallest named target. Unit-test snapshot redaction, dimensions, scale, filename, UTType, and encoding. Generate deterministic appearance/localization fixtures. Test PDF open/close and cleanup. Run the live UI with VoiceOver, Voice Control, Switch Control, keyboard access, Dynamic Type, increased contrast, reduced transparency, RTL, and Reduce Motion. Use physical devices for display scale, large output, memory, thermal, Files, AirDrop, and destination behavior. Inspect the signed archive when release configuration matters.

A preview, non-nil CGImage, or opened share sheet proves only that narrow step. It does not prove accessibility, destination acceptance, physical rendering, file retention, review, or production delivery.

## Sources

- [ImageRenderer](https://developer.apple.com/documentation/swiftui/imagerenderer)
- [ImageRenderer.proposedSize](https://developer.apple.com/documentation/swiftui/imagerenderer/proposedsize)
- [ImageRenderer.scale](https://developer.apple.com/documentation/swiftui/imagerenderer/scale)
- [ImageRenderer.isOpaque](https://developer.apple.com/documentation/swiftui/imagerenderer/isopaque)
- [ImageRenderer.colorMode](https://developer.apple.com/documentation/swiftui/imagerenderer/colormode)
- [ImageRenderer.allowedDynamicRange](https://developer.apple.com/documentation/swiftui/imagerenderer/alloweddynamicrange)
- [ImageRenderer.cgImage](https://developer.apple.com/documentation/swiftui/imagerenderer/cgimage)
- [ImageRenderer.uiImage](https://developer.apple.com/documentation/swiftui/imagerenderer/uiimage)
- [ImageRenderer.render(rasterizationScale:renderer:)](https://developer.apple.com/documentation/swiftui/imagerenderer/render%28rasterizationscale%3Arenderer%3A%29)
- [EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues)
- [EnvironmentValues.displayScale](https://developer.apple.com/documentation/swiftui/environmentvalues/displayscale)
- [EnvironmentValues.colorScheme](https://developer.apple.com/documentation/swiftui/environmentvalues/colorscheme)
- [EnvironmentValues.dynamicTypeSize](https://developer.apple.com/documentation/swiftui/environmentvalues/dynamictypesize)
- [GraphicsContext.environment](https://developer.apple.com/documentation/swiftui/graphicscontext/environment)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [TransferRepresentation](https://developer.apple.com/documentation/coretransferable/transferrepresentation)
- [DataRepresentation](https://developer.apple.com/documentation/coretransferable/datarepresentation)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [ProxyRepresentation](https://developer.apple.com/documentation/coretransferable/proxyrepresentation)
- [TransferRepresentationVisibility](https://developer.apple.com/documentation/coretransferable/transferrepresentationvisibility)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [SharePreview](https://developer.apple.com/documentation/swiftui/sharepreview)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [CGContext](https://developer.apple.com/documentation/coregraphics/cgcontext)
- [Human Interface Guidelines: Activity views](https://developer.apple.com/design/human-interface-guidelines/activity-views)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
