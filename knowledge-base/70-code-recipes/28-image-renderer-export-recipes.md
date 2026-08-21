# ImageRenderer, PDF, and Transferable recipes

## Compile boundary

These are compile-oriented route sketches, not compiled code in this documentation-only workspace. Before copying them into a named iOS 26 target, confirm current signatures/availability in Xcode, add imports/resources, set the deployment target, define snapshot/redaction/size/scale/color/file policies, and compile the smallest fixture before adding AI or background work.

## Recipe 1: explicit export view and bitmap

    import SwiftUI

    struct ExportCardSnapshot: Sendable, Equatable {
        let title: String
        let value: String
        let status: String
    }

    struct ExportCardView: View {
        let snapshot: ExportCardSnapshot

        var body: some View {
            VStack(alignment: .leading, spacing: 12) {
                Text(snapshot.title).font(.title2.weight(.semibold))
                Text(snapshot.value)
                    .font(.system(size: 40, weight: .bold, design: .rounded))
                    .monospacedDigit()
                Label(snapshot.status, systemImage: "checkmark.circle")
            }
            .padding(24)
            .frame(width: 360, alignment: .leading)
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 24))
        }
    }

    @MainActor
    func renderCard(
        snapshot: ExportCardSnapshot,
        scale: CGFloat = 3
    ) -> CGImage? {
        let renderer = ImageRenderer(content: ExportCardView(snapshot: snapshot))
        renderer.proposedSize = ProposedViewSize(width: 360, height: nil)
        renderer.scale = scale
        renderer.isOpaque = false
        return renderer.cgImage
    }

The exact height depends on measurement. Give the export view an explicit height or use a fully specified ProposedViewSize when the artifact contract requires a fixed rectangle, then assert pixel dimensions.

## Recipe 2: explicit appearance

    enum ExportAppearance: Sendable {
        case light
        case dark
    }

    @MainActor
    func renderCard(
        snapshot: ExportCardSnapshot,
        appearance: ExportAppearance,
        scale: CGFloat
    ) -> CGImage? {
        let scheme: ColorScheme = appearance == .dark ? .dark : .light
        let content = ExportCardView(snapshot: snapshot)
            .environment(\.colorScheme, scheme)
            .environment(\.dynamicTypeSize, .large)
        let renderer = ImageRenderer(content: content)
        renderer.proposedSize = ProposedViewSize(width: 360, height: 220)
        renderer.scale = scale
        return renderer.cgImage
    }

Do not choose a fixed Dynamic Type value to hide layout problems. It represents an explicit export policy that needs testing. For screen-faithful output, capture intended live environment values and record them.

## Recipe 3: encode CGImage as PNG

    import CoreGraphics
    import ImageIO
    import UniformTypeIdentifiers

    func pngData(from image: CGImage) -> Data? {
        guard let data = CFDataCreateMutable(nil, 0),
              let destination = CGImageDestinationCreateWithData(
                data,
                UTType.png.identifier as CFString,
                1,
                nil
              )
        else { return nil }

        CGImageDestinationAddImage(destination, image, nil)
        guard CGImageDestinationFinalize(destination) else { return nil }
        return data as Data
    }

Add maximum pixel and byte limits before encoding user-controlled or model-derived content. Inspect location, author, and embedded metadata separately.

## Recipe 4: DataRepresentation and ShareLink

    import CoreTransferable
    import UniformTypeIdentifiers

    struct RenderedPNG: Transferable, Sendable {
        let data: Data
        let fileName: String

        static var transferRepresentation: some TransferRepresentation {
            DataRepresentation(exportedContentType: .png) { item in
                item.data
            }
            .suggestedFileName { item in item.fileName }
            .exportingCondition { item in
                !item.data.isEmpty && !item.fileName.isEmpty
            }
        }
    }

    struct ShareRenderedPNG: View {
        let artifact: RenderedPNG

        var body: some View {
            ShareLink(item: artifact) {
                Label("Share image", systemImage: "square.and.arrow.up")
            }
        }
    }

The condition is a transport guard, not a privacy review. Present ShareLink only after an approved artifact is ready. SharePreview is presentation metadata, not canonical bytes.

## Recipe 5: render a staged PDF

    import CoreGraphics
    import SwiftUI

    @MainActor
    func writePDF<Content: View>(
        content: Content,
        to url: URL,
        pageSize: CGSize = CGSize(width: 612, height: 792)
    ) {
        let renderer = ImageRenderer(content: content)
        renderer.render { size, draw in
            var mediaBox = CGRect(origin: .zero, size: pageSize)
            guard let consumer = CGDataConsumer(url: url as CFURL),
                  let context = CGContext(
                    consumer: consumer,
                    mediaBox: &mediaBox,
                    nil
                  )
            else { return }

            context.beginPDFPage(nil)
            context.saveGState()
            context.translateBy(
                x: (pageSize.width - size.width) / 2,
                y: (pageSize.height - size.height) / 2
            )
            draw(context)
            context.restoreGState()
            context.endPDFPage()
            context.closePDF()
        }
    }

The callback uses a bottom-left coordinate-space origin. Validate page bounds, openability, metadata, and cleanup before sharing.

## Recipe 6: FileRepresentation for a PDF

    import CoreTransferable
    import UniformTypeIdentifiers

    struct RenderedPDF: Transferable, Sendable {
        let url: URL
        let fileName: String

        static var transferRepresentation: some TransferRepresentation {
            FileRepresentation(exportedContentType: .pdf) { item in
                SentTransferredFile(item.url)
            }
            .suggestedFileName { item in item.fileName }
        }
    }

The export job/staging actor owns the temporary file. Do not delete it merely because ShareLink was presented; reconcile orphaned files on relaunch.

## Recipe 7: safe AI style proposal

    struct ExportStyleProposal: Sendable, Codable {
        let paletteRole: String
        let cornerRadius: Double
        let showSubtitle: Bool
    }

    enum PaletteRole: String, Sendable {
        case standard
        case accent
        case highContrast
    }

    struct ValidatedExportStyle: Sendable {
        let paletteRole: PaletteRole
        let cornerRadius: CGFloat
        let showSubtitle: Bool
    }

    func validate(_ proposal: ExportStyleProposal) -> ValidatedExportStyle {
        let role = PaletteRole(rawValue: proposal.paletteRole) ?? .standard
        let radius = min(max(proposal.cornerRadius, 0), 40)
        return ValidatedExportStyle(
            paletteRole: role,
            cornerRadius: CGFloat(radius),
            showSubtitle: proposal.showSubtitle
        )
    }

The proposal cannot name shader/resource paths, arbitrary executable view code, file destinations, or privacy fields. If the model is unavailable or invalid, use the standard style.

## Recipe 8: test separate seams

    snapshot -> validated fields and redaction
    export view -> proposed size and semantic content
    ImageRenderer -> output and dimensions
    encoder -> type, bytes, failure
    Transferable -> representation and filename
    ShareLink -> presentation and cancellation
    device -> display scale, memory, thermal, destination

A preview, non-nil CGImage, or presented share sheet is not proof of physical-device behavior, destination acceptance, accessibility, or release readiness.

## Sources

- [ImageRenderer](https://developer.apple.com/documentation/swiftui/imagerenderer)
- [ImageRenderer.proposedSize](https://developer.apple.com/documentation/swiftui/imagerenderer/proposedsize)
- [ImageRenderer.scale](https://developer.apple.com/documentation/swiftui/imagerenderer/scale)
- [ImageRenderer.isOpaque](https://developer.apple.com/documentation/swiftui/imagerenderer/isopaque)
- [ImageRenderer.cgImage](https://developer.apple.com/documentation/swiftui/imagerenderer/cgimage)
- [ImageRenderer.uiImage](https://developer.apple.com/documentation/swiftui/imagerenderer/uiimage)
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
- [SharePreview](https://developer.apple.com/documentation/swiftui/sharepreview)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [CGContext](https://developer.apple.com/documentation/coregraphics/cgcontext)
- [Human Interface Guidelines: Activity views](https://developer.apple.com/design/human-interface-guidelines/activity-views)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
