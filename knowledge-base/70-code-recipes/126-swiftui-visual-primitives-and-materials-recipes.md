# SwiftUI visual primitives and materials recipes

## Recipe rules

These snippets are deliberately small route starters. They show where a native
SwiftUI API belongs; they do not prove the app's deployment target, image
source, model availability, accessibility, performance, or release behavior.

For every recipe:

1. compile it in the named target and deployment target;
2. replace placeholder IDs, labels, and source policy with feature-owned values;
3. add loading/error/cancellation/accessibility states;
4. test light/dark, Dynamic Type, reduced effects, RTL, and alternate input;
5. attach the proof matrix for any physical, media, AI, or release claim.

The code below uses tilde fences so it can be copied into a Markdown notebook
without confusing the surrounding documentation.

## 1. Labeled and decorative local images

Use a labeled image when the image communicates information or participates in
a control. Use the decorative initializer when the image is atmosphere and
nearby text carries the meaning.

~~~swift
struct ProjectThumbnail: View {
    let imageName: String
    let projectName: String
    let isDecorative: Bool

    var body: some View {
        Group {
            if isDecorative {
                Image(decorative: imageName)
                    .resizable()
                    .scaledToFill()
            } else {
                Image(imageName, bundle: nil)
                    .resizable()
                    .scaledToFill()
                    .accessibilityLabel(Text(projectName))
            }
        }
        .frame(width: 88, height: 64)
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }
}
~~~

For a symbol-only action, put the image in a semantic control and label the
action:

~~~swift
Button {
    archiveProject()
} label: {
    Image(systemName: "archivebox")
}
.accessibilityLabel("Archive project")
~~~

Do not rely on the SF Symbol name, tint, or tooltip as the action label.

## 2. AsyncImage with explicit phase states

Use AsyncImage for a simple URL-backed image when URLSession behavior and
phase state are sufficient. Keep the frame stable and give failure a retry or
alternate route.

~~~swift
struct RemoteThumbnail: View {
    let url: URL?
    let retry: () -> Void

    var body: some View {
        AsyncImage(url: url) { phase in
            switch phase {
            case .empty:
                thumbnailPlaceholder(label: "Loading image")
            case .success(let image):
                image
                    .resizable()
                    .scaledToFill()
            case .failure:
                Button(action: retry) {
                    Label("Retry image", systemImage: "arrow.clockwise")
                        .labelStyle(.iconOnly)
                }
                .accessibilityHint("The image could not be loaded")
            @unknown default:
                thumbnailPlaceholder(label: "Image unavailable")
            }
        }
        .frame(width: 112, height: 80)
        .background(.secondary.opacity(0.12))
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .contentShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private func thumbnailPlaceholder(label: LocalizedStringKey) -> some View {
        ProgressView()
            .accessibilityLabel(label)
    }
}
~~~

Do not let a failure branch show a previous row's image. If the URL changes
for the same row, make the resource key and source revision part of the
feature state. For authentication, explicit caching, downsampling, retry
backoff, or a large feed, use a feature-owned loader.

## 3. Feature-owned image loading boundary

A custom loader belongs outside the view. The loader below is a route sketch:
the repository implementation should own URLSession configuration, decode
policy, cache policy, and privacy rules.

~~~swift
struct ImageResourceKey: Hashable, Sendable {
    let itemID: UUID
    let sourceRevision: Int
    let url: URL
}

@MainActor
final class ImageResourceStore: ObservableObject {
    enum State {
        case idle
        case loading
        case ready(Image)
        case failed
    }

    @Published private(set) var state: State = .idle
    private var loadTask: Task<Void, Never>?

    func load(key: ImageResourceKey) {
        loadTask?.cancel()
        state = .loading

        loadTask = Task {
            do {
                let (data, _) = try await URLSession.shared.data(from: key.url)
                try Task.checkCancellation()

                // Decode and downsample in a dedicated media boundary.
                let image = try await decodeImage(data: data)
                try Task.checkCancellation()

                state = .ready(image)
            } catch is CancellationError {
                state = .idle
            } catch {
                state = .failed
            }
        }
    }

    func cancel() {
        loadTask?.cancel()
        loadTask = nil
        state = .idle
    }

    private func decodeImage(data: Data) async throws -> Image {
        // Replace with an Image I/O or platform-image decoder.
        throw URLError(.cannotDecodeContentData)
    }
}
~~~

The route is intentionally incomplete: a production decoder must handle
orientation, scale, large images, malformed bytes, memory pressure, and
source privacy. A stale response must be rejected if a newer source revision
is active. Do not let a row-level view model become an unbounded image cache.

## 4. Fit, fill, and deliberate clipping

The choice between fit and fill is a content decision.

~~~swift
struct ImageFrame: View {
    let image: Image
    let mode: ContentMode

    var body: some View {
        image
            .resizable()
            .aspectRatio(contentMode: mode)
            .frame(maxWidth: .infinity, minHeight: 180, maxHeight: 280)
            .clipped()
            .contentShape(Rectangle())
    }
}
~~~

Use fit for documents, receipts, diagrams, and any image where missing an
edge changes meaning. Use fill for an approved discovery thumbnail where a
consistent frame matters more than the edges. If the focal point is not the
center, store a focal point or crop rectangle rather than silently accepting
a random crop.

## 5. Semantic SF Symbol control

Use a system symbol as the glyph and keep the action in the control.

~~~swift
struct SaveButton: View {
    let isSaved: Bool
    let save: () -> Void

    var body: some View {
        Button(action: save) {
            Label(
                isSaved ? "Saved" : "Save",
                systemImage: isSaved ? "bookmark.fill" : "bookmark"
            )
        }
        .symbolRenderingMode(.hierarchical)
        .tint(.accentColor)
        .accessibilityValue(isSaved ? "On" : "Off")
    }
}
~~~

If the control must be icon-only in a compact toolbar, preserve the same
accessible action label:

~~~swift
Button(action: save) {
    Image(systemName: isSaved ? "bookmark.fill" : "bookmark")
}
.accessibilityLabel(isSaved ? "Remove bookmark" : "Add bookmark")
~~~

The visible symbol and the accessible action should agree. A filled glyph
should not silently mean a different domain state in another screen.

## 6. Symbol effects tied to committed local state

Use the value form of symbolEffect for local feedback after state changes.

~~~swift
struct FavoriteButton: View {
    @State private var isFavorite = false

    var body: some View {
        Button {
            isFavorite.toggle()
        } label: {
            Image(systemName: isFavorite ? "heart.fill" : "heart")
                .symbolRenderingMode(.hierarchical)
        }
        .symbolEffect(.bounce, value: isFavorite)
        .accessibilityLabel(isFavorite ? "Remove favorite" : "Add favorite")
        .accessibilityValue(isFavorite ? "On" : "Off")
    }
}
~~~

The animation is not proof of persistence, synchronization, or a completed
purchase. If saving is asynchronous, use separate saving/saved/failed state
and trigger the effect only for the intended committed presentation state.

## 7. Hierarchical style and standard Material

Keep geometric shape and appearance separate. Standard Material is a
background/separation layer; it is not a replacement for Liquid Glass.

~~~swift
struct MaterialCard<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        content
            .padding()
            .foregroundStyle(.primary)
            .background(.regularMaterial, in:
                RoundedRectangle(cornerRadius: 20, style: .continuous)
            )
            .overlay {
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .strokeBorder(.separator, lineWidth: 1)
            }
    }
}
~~~

The material should support hierarchy and legibility. Test the card over
colorful content, in dark mode, with increased contrast, and with reduced
transparency. If the card contains a primary action, use a semantic Button
or a native control style rather than making the entire material surface a
gesture-only button.

## 8. Background, overlay, clip, and content shape

This recipe makes the drawing and hit regions explicit.

~~~swift
struct StatusCard: View {
    let title: String
    let isStale: Bool
    let open: () -> Void

    var body: some View {
        Button(action: open) {
            HStack(spacing: 12) {
                Image(systemName: "doc.text")
                    .foregroundStyle(.tint)

                Text(title)
                    .frame(maxWidth: .infinity, alignment: .leading)

                if isStale {
                    Image(systemName: "clock.badge.exclamationmark")
                        .foregroundStyle(.orange)
                        .accessibilityLabel("Stale")
                }
            }
            .padding()
            .contentShape(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
            )
        }
        .buttonStyle(.plain)
        .background(.background, in:
            RoundedRectangle(cornerRadius: 16, style: .continuous)
        )
        .overlay {
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .strokeBorder(.separator, lineWidth: 1)
        }
        .accessibilityElement(children: .combine)
    }
}
~~~

If the status carries important meaning, expose it in the combined accessible
description or as an accessibility value. Do not rely only on the orange
symbol.

## 9. Safe-area-aware functional edge

A bottom action layer should not cover scrolling content.

~~~swift
struct ReviewScreen: View {
    let accept: () -> Void
    let reject: () -> Void

    var body: some View {
        ScrollView {
            ReviewContent()
                .padding()
        }
        .safeAreaInset(edge: .bottom, spacing: 12) {
            HStack {
                Button("Reject", role: .destructive, action: reject)
                Button("Accept", action: accept)
                    .buttonStyle(.borderedProminent)
            }
            .padding(.horizontal)
            .padding(.top, 8)
            .background(.thinMaterial)
        }
    }
}
~~~

If the product uses Liquid Glass for this functional group, adopt the
documented Liquid Glass route and verify that the content remains legible,
the controls remain semantic, and reduced transparency still leaves a
complete action path.

## 10. Bounded visualEffect

Use visualEffect for appearance derived from geometry, not for feature state.

~~~swift
struct GeometryAwareThumbnail: View {
    let image: Image

    var body: some View {
        image
            .resizable()
            .scaledToFill()
            .frame(height: 220)
            .clipped()
            .visualEffect { content, geometry in
                let width = max(1, geometry.size.width)
                let boundedOpacity = min(1, max(0.7, width / 360))
                return content.opacity(boundedOpacity)
            }
    }
}
~~~

A production effect should use a meaningful geometry signal and should be
tested under reduced effects and representative scrolling. The closure must
not update selection, save state, navigation, or AI work.

## 11. Content transition with an identity fallback

Use a content transition for a local content replacement when it preserves
context. Use identity when a surrounding animation should not animate the
content.

~~~swift
struct ConnectionStatus: View {
    let isConnected: Bool

    var body: some View {
        Label(
            isConnected ? "Connected" : "Offline",
            systemImage: isConnected ? "checkmark.circle" : "wifi.slash"
        )
        .contentTransition(.symbolEffect)
        .animation(.default, value: isConnected)
    }
}
~~~

Add a reduced-motion policy in the feature's design and test a static
version. The transition should not imply that a server is healthy unless the
underlying connection state actually supports that claim.

## 12. AI image candidate review

The view renders a candidate; a feature command owns validation and commit.

~~~swift
struct VisualCandidate: Identifiable, Equatable {
    enum Status {
        case preparing
        case ready
        case stale
        case failed
    }

    let id: UUID
    let sourceID: UUID
    let sourceRevision: Int
    let title: String
    let status: Status
    let confidence: Double?
}

struct CandidateReviewRow: View {
    let sourceImage: Image
    let candidate: VisualCandidate
    let accept: () -> Void
    let reject: () -> Void
    let inspect: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            sourceImage
                .resizable()
                .scaledToFit()
                .frame(maxHeight: 220)
                .accessibilityLabel("Source image")

            Label(candidate.title, systemImage: "sparkles")
                .foregroundStyle(.secondary)

            switch candidate.status {
            case .preparing:
                ProgressView("Preparing suggestion")
            case .ready:
                HStack {
                    Button("Inspect", action: inspect)
                    Button("Reject", role: .destructive, action: reject)
                    Button("Accept", action: accept)
                        .buttonStyle(.borderedProminent)
                }
            case .stale:
                Label("Source changed; run again", systemImage: "arrow.clockwise")
                    .foregroundStyle(.orange)
            case .failed:
                Label("Suggestion unavailable", systemImage: "exclamationmark.triangle")
                    .foregroundStyle(.secondary)
            }
        }
        .accessibilityElement(children: .contain)
    }
}
~~~

In production, the accept command must compare sourceID/sourceRevision with
the current domain value, validate the candidate, and commit a new revision
only after the person chooses accept. Add explicit confidence/coverage copy
only when the local capability provides a meaningful value. Do not let the
candidate title become the source image's accessibility label automatically.

## 13. Test fixtures for visual primitives

Use a fixture provider that can exercise every branch without a network or
model:

~~~swift
struct VisualPrimitiveFixture {
    let localImageName: String
    let remoteURL: URL
    let unsupportedSymbolName: String
    let sourceID: UUID
    let sourceRevision: Int
    let candidateID: UUID

    static let standard = VisualPrimitiveFixture(
        localImageName: "PreviewPhoto",
        remoteURL: URL(string: "https://example.invalid/test-image")!,
        unsupportedSymbolName: "symbol.not.available",
        sourceID: UUID(uuidString: "00000000-0000-0000-0000-000000000001")!,
        sourceRevision: 3,
        candidateID: UUID(uuidString: "00000000-0000-0000-0000-000000000002")!
    )
}
~~~

Use a local fixture server or injected loader in tests. Do not make
example.invalid a production request. The fixture should include fit/fill,
invalid bytes, source revision changes, model-unavailable, stale candidate,
reduced motion, increased contrast, and accessibility label cases.

## 14. Recipe acceptance checklist

- [ ] The snippet is compiled against the selected deployment target.
- [ ] The source identity is separate from the visual resource key.
- [ ] Loading, success, failure, cancellation, and stale-result states exist.
- [ ] Fit/fill/crop behavior matches the content's meaning.
- [ ] Images are labeled or explicitly decorative.
- [ ] Symbols have availability fallback, semantic labels, and stable colors.
- [ ] Material is used as hierarchy, not as a completion/trust indicator.
- [ ] Liquid Glass is limited to a functional group and has a reduced-effects
      fallback.
- [ ] Background, overlay, clipping, safe area, and hit region are intentional.
- [ ] visualEffect and transitions do not own feature side effects.
- [ ] AI output has source revision, candidate identity, review, and commit
      boundaries.
- [ ] Accessibility, Dynamic Type, RTL, and alternate-input fixtures pass.
- [ ] Performance and physical-device evidence are attached for the actual
      claim.

## Sources

- [Image](https://developer.apple.com/documentation/swiftui/image)
- [AsyncImage](https://developer.apple.com/documentation/swiftui/asyncimage)
- [Fitting images into available space](https://developer.apple.com/documentation/swiftui/fitting-images-into-available-space)
- [SF Symbols HIG](https://developer.apple.com/design/human-interface-guidelines/sf-symbols)
- [Label](https://developer.apple.com/documentation/swiftui/label)
- [ShapeStyle](https://developer.apple.com/documentation/swiftui/shapestyle)
- [ForegroundStyle](https://developer.apple.com/documentation/swiftui/foregroundstyle)
- [Material](https://developer.apple.com/documentation/swiftui/material)
- [backgroundMaterial](https://developer.apple.com/documentation/swiftui/environmentvalues/backgroundmaterial)
- [View appearance](https://developer.apple.com/documentation/swiftui/view-appearance)
- [Adding a background to your view](https://developer.apple.com/documentation/swiftui/adding-a-background-to-your-view)
- [ContentShapeKinds](https://developer.apple.com/documentation/swiftui/contentshapekinds)
- [VisualEffect](https://developer.apple.com/documentation/swiftui/visualeffect)
- [visualEffect(_:)](https://developer.apple.com/documentation/swiftui/view/visualeffect%28_%3A%29)
- [ContentTransition](https://developer.apple.com/documentation/swiftui/contenttransition)
- [View.symbolEffect(_:options:value:)](https://developer.apple.com/documentation/swiftui/view/symboleffect%28_%3Aoptions%3Avalue%3A%29)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Materials HIG](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Color HIG](https://developer.apple.com/design/human-interface-guidelines/color)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [SwiftUI accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [XCUITest](https://developer.apple.com/documentation/xcuiautomation)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
