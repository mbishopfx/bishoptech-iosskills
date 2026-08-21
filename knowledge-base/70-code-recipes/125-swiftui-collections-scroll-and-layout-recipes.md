# SwiftUI collections, scroll, and adaptive-layout recipes

## Compile boundary

These are compile-oriented route sketches for a named iOS 26 target. Confirm
exact declarations, availability, imports, platform behavior, and deployment
target in Xcode before shipping. The snippets intentionally keep domain
mutation, pagination, viewport state, and AI approval separate.

The recipes do not prove physical scrolling, touch feel, pointer/keyboard
input, VoiceOver completion, model availability, performance, thermal
behavior, or release delivery.

Related pages:

- [SwiftUI collections, scroll, and adaptive layout](../42-framework-deep-dives/82-swiftui-collections-scroll-and-adaptive-layout.md)
- [Collections, scrolling, and adaptive-layout design](../21-design-deep-dives/110-collections-scroll-and-adaptive-layout-design.md)
- [SwiftUI collections, scroll, and layout route](../50-capability-recipes/113-swiftui-collections-scroll-and-layout-route.md)
- [SwiftUI collections, scroll, and layout proof matrix](../60-verification/107-swiftui-collections-scroll-and-layout-proof-matrix.md)

## Recipe 1: stable List identity and selection

Use a domain-owned ID for rows and selection. Keep the selected ID separate
from the full record and route selection to a typed feature action.

~~~swift
import SwiftUI

struct Message: Identifiable, Hashable {
    let id: UUID
    var title: String
    var isUnread: Bool
}

struct MessageList: View {
    let messages: [Message]
    @Binding var selectedID: Message.ID?
    let open: (Message.ID) -> Void

    var body: some View {
        List(messages, selection: $selectedID) { message in
            Button {
                open(message.id)
            } label: {
                HStack {
                    VStack(alignment: .leading) {
                        Text(message.title)
                        Text(message.isUnread ? "Unread" : "Read")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                    if message.isUnread {
                        Image(systemName: "circle.fill")
                            .accessibilityHidden(true)
                    }
                }
            }
            .buttonStyle(.plain)
            .tag(message.id)
        }
        .accessibilityLabel("Messages")
    }
}
~~~

If the row itself should select rather than activate a separate Button, use
the List selection contract directly and make the selected state visible.
Test insert, delete, reorder, filter, VoiceOver, pointer, and keyboard
behavior. Do not use a title or array index as a restoreable ID.

## Recipe 2: a lazy visual grid with stable cells

Use LazyVGrid for a large image-oriented collection. The grid is inside the
ScrollView because lazy grids do not provide scrolling by themselves.

~~~swift
struct Artwork: Identifiable, Hashable {
    let id: UUID
    let title: String
    let imageName: String
}

struct ArtworkGrid: View {
    let items: [Artwork]
    let select: (Artwork.ID) -> Void

    private let columns = [
        GridItem(.adaptive(minimum: 150), spacing: 16)
    ]

    var body: some View {
        ScrollView {
            LazyVGrid(columns: columns, spacing: 16) {
                ForEach(items) { item in
                    Button {
                        select(item.id)
                    } label: {
                        VStack(alignment: .leading, spacing: 8) {
                            Image(item.imageName)
                                .resizable()
                                .scaledToFill()
                                .containerRelativeFrame(.horizontal)
                                .frame(height: 150)
                                .clipped()
                            Text(item.title)
                                .font(.headline)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel(item.title)
                }
            }
            .padding(.horizontal)
        }
    }
}
~~~

The exact image-loading path belongs to the app’s resource/cache boundary.
Do not assume a lazy cell makes image decoding or model work free. Profile a
representative data set, and test long titles, Dynamic Type, selection,
rotation, split view, and right-to-left layout.

## Recipe 3: semantic ScrollPosition for a feed

Use item identity for programmatic movement and restoration. Mark the
repeating layout as a scroll target layout.

~~~swift
struct FeedItem: Identifiable, Hashable {
    let id: UUID
    let title: String
    let body: String
}

struct FeedView: View {
    let items: [FeedItem]
    @State private var position = ScrollPosition(idType: FeedItem.ID.self)

    var body: some View {
        VStack {
            HStack {
                Button("Show first") {
                    guard let first = items.first else { return }
                    position.scrollTo(id: first.id, anchor: .top)
                }

                Button("Show latest") {
                    position.scrollTo(edge: .bottom)
                }
            }

            ScrollView {
                LazyVStack(alignment: .leading, spacing: 12) {
                    ForEach(items) { item in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(item.title)
                                .font(.headline)
                            Text(item.body)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding()
                        .id(item.id)
                    }
                }
                .scrollTargetLayout()
            }
            .scrollPosition($position, anchor: .top)
        }
        .padding()
    }
}
~~~

The buttons are explicit scroll intents. In a real feature, record why a
programmatic jump occurred and do not replace the person’s current browsing
position when background data arrives.

## Recipe 4: project ScrollGeometry into bounded state

Transform high-frequency geometry into small Equatable values. Use the
projection to control chrome or request a bounded feature action.

~~~swift
struct ScrollState: Equatable {
    var isPastHeader = false
    var isNearBottom = false
}

struct GeometryAwareFeed<Content: View>: View {
    @State private var scrollState = ScrollState()
    @ViewBuilder let content: () -> Content

    var body: some View {
        ScrollView {
            content()
        }
        .onScrollGeometryChange(for: Bool.self) { geometry in
            geometry.visibleRect.minY > geometry.contentInsets.top + 40
        } action: { _, newValue in
            scrollState.isPastHeader = newValue
        }
        .onScrollGeometryChange(for: Bool.self) { geometry in
            geometry.visibleRect.maxY
                >= geometry.contentSize.height
                - geometry.contentInsets.bottom
                - 80
        } action: { _, newValue in
            scrollState.isNearBottom = newValue
        }
        .overlay(alignment: .top) {
            if scrollState.isPastHeader {
                Text("Scrolled")
                    .font(.caption)
                    .padding(8)
            }
        }
    }
}
~~~

Keep the action narrow. Do not publish the raw offset to a broad observable
model or trigger an expensive model/network operation for every geometry
change. If multiple scroll views exist, attach the modifier at the intended
owner and verify which view is observed.

## Recipe 5: visibility-triggered pagination with generation guards

Visibility can signal that the user is near the end of a collection. The
feature owns the cursor, cancellation, deduplication, and query generation.

~~~swift
@MainActor
final class PageStore<Item: Identifiable> where Item.ID: Hashable {
    enum State: Equatable {
        case idle
        case loading
        case loaded
        case failed
    }

    private(set) var items: [Item] = []
    private(set) var state: State = .idle
    private var nextCursor: String?
    private var queryGeneration = UUID()
    private var pageTask: Task<Void, Never>?

    func reset() {
        queryGeneration = UUID()
        pageTask?.cancel()
        pageTask = nil
        items = []
        nextCursor = nil
        state = .idle
    }

    func loadNext(
        fetch: @escaping (String?) async throws -> (items: [Item], next: String?)
    ) {
        guard pageTask == nil, state != .loaded || nextCursor != nil else {
            return
        }

        let generation = queryGeneration
        let cursor = nextCursor
        state = .loading

        pageTask = Task {
            defer { pageTask = nil }
            do {
                let page = try await fetch(cursor)
                guard !Task.isCancelled, generation == queryGeneration else {
                    return
                }

                var seen = Set(items.map(\.id))
                let additions = page.items.filter { seen.insert($0.id).inserted }
                items.append(contentsOf: additions)
                nextCursor = page.next
                state = .loaded
            } catch is CancellationError {
                return
            } catch {
                guard generation == queryGeneration else { return }
                state = .failed
            }
        }
    }
}
~~~

This is a route sketch, not a universal repository. The guard expression and
state policy should be adapted to the project’s Swift version and pagination
semantics. Add deterministic tests for duplicate calls, cancellation, a new
query during an old response, out-of-order pages, and an empty terminal page.

## Recipe 6: trigger the next page from a stable target

Use a stable last-item ID and a threshold. The visibility callback should
call a feature method that can reject duplicate or stale work.

~~~swift
struct PaginatedFeed: View {
    let items: [FeedItem]
    let loadNextPage: () -> Void
    let isLoading: Bool

    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading) {
                ForEach(items) { item in
                    FeedRow(item: item)
                        .onScrollVisibilityChange(threshold: 0.2) { visible in
                            guard visible, item.id == items.last?.id else {
                                return
                            }
                            loadNextPage()
                        }
                }

                if isLoading {
                    ProgressView("Loading more")
                        .frame(maxWidth: .infinity)
                        .padding()
                }
            }
            .scrollTargetLayout()
        }
    }
}
~~~

For larger features, use onScrollTargetVisibilityChange with an ID type and
compare the visible IDs against a feature-owned threshold policy. A fast
fling can make many targets visible; the operation still needs one in-flight
request, cursor deduplication, cancellation, and a model/network fallback.

## Recipe 7: view-aligned cards and page-aligned content

Select a target behavior from the content contract.

~~~swift
struct CardCarousel: View {
    let items: [Artwork]

    var body: some View {
        ScrollView(.horizontal) {
            LazyHStack(spacing: 16) {
                ForEach(items) { item in
                    ArtworkCard(item: item)
                        .containerRelativeFrame(.horizontal, count: 1, span: 1, spacing: 16)
                        .id(item.id)
                }
            }
            .scrollTargetLayout()
        }
        .scrollTargetBehavior(.viewAligned)
        .contentMargins(.horizontal, 20)
    }
}

struct FullScreenPages: View {
    let pages: [FeedItem]

    var body: some View {
        ScrollView {
            LazyVStack(spacing: 0) {
                ForEach(pages) { page in
                    PageView(page: page)
                        .containerRelativeFrame([.horizontal, .vertical])
                }
            }
        }
        .scrollTargetBehavior(.paging)
    }
}
~~~

Test variable content, long labels, incomplete final pages, keyboard,
VoiceOver, reduced motion, and a page-control decision. Do not claim snap
behavior from a static screenshot.

## Recipe 8: ViewThatFits and AnyLayout for adaptation

Use ViewThatFits for complete alternatives and AnyLayout for the same content
in a different arrangement.

~~~swift
struct AdaptiveActionRow: View {
    let primaryAction: () -> Void
    let secondaryAction: () -> Void

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack {
                Button("Primary action", action: primaryAction)
                Button("Secondary action", action: secondaryAction)
            }

            Button("Primary action", action: primaryAction)

            Menu("More") {
                Button("Primary action", action: primaryAction)
                Button("Secondary action", action: secondaryAction)
            }
        }
    }
}

struct ArrangementSwitch<Content: View>: View {
    let isCompact: Bool
    @ViewBuilder let content: () -> Content

    var body: some View {
        let layout = isCompact
            ? AnyLayout(VStackLayout(alignment: .leading, spacing: 12))
            : AnyLayout(HStackLayout(alignment: .center, spacing: 16))

        layout {
            content()
        }
    }
}
~~~

Every alternative must retain the primary action, labels, selected state,
error, and recovery. Verify that local view state and focus survive an
AnyLayout transition.

## Recipe 9: container-relative card sizing and safe-area action bar

Tie card sizing to the nearest container and reserve space for a functional
bottom action bar.

~~~swift
struct CollectionWithActionBar: View {
    let items: [Artwork]
    let apply: () -> Void

    var body: some View {
        ScrollView {
            LazyVGrid(
                columns: [GridItem(.adaptive(minimum: 150))],
                spacing: 16
            ) {
                ForEach(items) { item in
                    ArtworkCard(item: item)
                        .containerRelativeFrame(.horizontal)
                }
            }
            .padding(.horizontal)
        }
        .safeAreaInset(edge: .bottom, spacing: 0) {
            HStack {
                Button("Apply", action: apply)
                    .buttonStyle(.glassProminent)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(.clear)
        }
        .contentMargins(.bottom, 12, for: .scrollContent)
    }
}
~~~

Confirm the exact glass button style and availability in the selected SDK.
The safe-area inset must be tested with the keyboard, tab bar, rotation,
large text, VoiceOver, and a collection that is shorter than the viewport.

## Recipe 10: a functional Liquid Glass edge group

Keep the material around a small set of controls and let the content remain
the content layer.

~~~swift
struct CollectionChrome: View {
    let showGrid: Bool
    let setGrid: (Bool) -> Void

    var body: some View {
        GlassEffectContainer(spacing: 12) {
            HStack(spacing: 12) {
                Button("Refresh", systemImage: "arrow.clockwise") {
                    // Call the feature refresh command.
                }

                Toggle(isOn: Binding(
                    get: { showGrid },
                    set: setGrid
                )) {
                    Label("Grid", systemImage: "square.grid.2x2")
                }
                .labelsHidden()
            }
            .padding(8)
            .glassEffect(in: .capsule)
        }
    }
}
~~~

This is a composition route, not a promise that every SDK exposes every
style or shape overload shown. Keep the controls semantic, use a named
accessibility label for compact presentations, and test reduced transparency
and increased contrast. Do not place a glass effect on every collection row.

## Recipe 11: an AI candidate row boundary

The view displays a proposal; the feature decides whether it can be accepted.

~~~swift
struct SuggestedTitle: Identifiable, Equatable {
    let id: UUID
    let sourceID: UUID
    let sourceRevision: Int
    var text: String
    var isPartial: Bool
}

struct SuggestionRow: View {
    let suggestion: SuggestedTitle
    let accept: () -> Void
    let reject: () -> Void
    let edit: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(
                suggestion.isPartial ? "Generating suggestion" : "Suggested title",
                systemImage: suggestion.isPartial ? "sparkles" : "lightbulb"
            )
            .font(.caption)
            .foregroundStyle(.secondary)

            Text(suggestion.text)
                .font(.headline)

            HStack {
                Button("Accept", action: accept)
                Button("Edit", action: edit)
                Button("Reject", role: .destructive, action: reject)
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityValue(
            suggestion.isPartial ? "Still generating" : "Needs review"
        )
    }
}
~~~

The accept closure should verify sourceID and sourceRevision against the
current domain record, run deterministic validation, and commit once. The
candidate’s ID is not the committed record’s ID. If Foundation Models is
unavailable or canceled, show a manual path and preserve the source.

## Recipe 12: compile-oriented Foundation Models feed sketch

Foundation Models declarations evolve. Confirm the current streaming and
Generable overloads in Xcode before using this shape.

~~~swift
import FoundationModels

@Generable
struct SummaryCandidate {
    @Guide(description: "A short title for the source item")
    var title: String

    @Guide(description: "A concise summary grounded in the source")
    var summary: String
}

@MainActor
final class SummaryFeature {
    private(set) var isGenerating = false
    private(set) var candidate: SummaryCandidate?

    func generate(from source: String) async {
        isGenerating = true
        defer { isGenerating = false }

        do {
            let session = LanguageModelSession(
                instructions: "Suggest a concise, source-grounded summary."
            )
            let response = try await session.respond(
                to: source,
                generating: SummaryCandidate.self
            )
            candidate = response.content
        } catch is CancellationError {
            candidate = nil
        } catch {
            candidate = nil
        }
    }
}
~~~

This sketch does not include source revision, availability checks, prompt
versioning, safety policy, or commit authorization. Add those before using it.
Keep the result in a candidate state and make the review action visible.

## Recipe 13: deterministic collection fixture

Use a fixture model to exercise identity, selection, pagination, and viewport
without network or model variability.

~~~swift
struct CollectionFixture {
    static let shortItems = [
        FeedItem(id: UUID(uuidString: "00000000-0000-0000-0000-000000000001")!,
                 title: "First", body: "Short fixture"),
        FeedItem(id: UUID(uuidString: "00000000-0000-0000-0000-000000000002")!,
                 title: "Second", body: "Longer fixture")
    ]

    static let longItems = (0..<200).map { index in
        FeedItem(
            id: UUID(),
            title: "Fixture item",
            body: "Item content for scrolling, visibility, and pagination."
        )
    }
}
~~~

Prefer deterministic IDs in tests and snapshots. Add explicit fixtures for
duplicate page IDs, a removed anchor, long localized strings, RTL, large
Dynamic Type, model unavailable, canceled generation, and stale source
revision.

## Recipe 14: proof harness notes

For every recipe, record:

    target, SDK, deployment target
    device/OS and window/container size
    data fixture and query/scope
    selected IDs, visible target, viewport mode
    Dynamic Type/locale/RTL/accessibility settings
    color scheme/transparency/motion settings
    request generation/cursor/cancellation result
    AI availability/source revision/candidate/approval state
    performance trace or unproven status

Preview and simulator results can validate composition and deterministic state.
Use a signed physical device for physical scrolling, touch/pointer/keyboard,
VoiceOver, material rendering, model availability, and performance claims.

## Sources

- [List](https://developer.apple.com/documentation/swiftui/list)
- [LazyVStack](https://developer.apple.com/documentation/swiftui/lazyvstack)
- [LazyVGrid](https://developer.apple.com/documentation/swiftui/lazyvgrid)
- [Grid](https://developer.apple.com/documentation/swiftui/grid)
- [ScrollView](https://developer.apple.com/documentation/swiftui/scrollview)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [ScrollGeometry](https://developer.apple.com/documentation/swiftui/scrollgeometry)
- [onScrollGeometryChange(for:of:action:)](https://developer.apple.com/documentation/swiftui/view/onscrollgeometrychange%28for%3Aof%3Aaction%3A%29/)
- [onScrollVisibilityChange(threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrollvisibilitychange%28threshold%3A_%3A%29)
- [onScrollTargetVisibilityChange(idType:threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrolltargetvisibilitychange%28idtype%3Athreshold%3A_%3A%29)
- [scrollTargetLayout(isEnabled:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetlayout%28isenabled%3A%29)
- [scrollTargetBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetbehavior%28_%3A%29)
- [PagingScrollTargetBehavior](https://developer.apple.com/documentation/swiftui/pagingscrolltargetbehavior)
- [ViewAlignedScrollTargetBehavior](https://developer.apple.com/documentation/swiftui/viewalignedscrolltargetbehavior)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [containerRelativeFrame(_:alignment:_:)](https://developer.apple.com/documentation/swiftui/view/containerrelativeframe%28_%3Aalignment%3A_%3A%29)
- [safeAreaInset(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [contentMargins(_:_:for:)](https://developer.apple.com/documentation/swiftui/view/contentmargins%28_%3A_%3Afor%3A%29-1lt8b)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Collections](https://developer.apple.com/design/human-interface-guidelines/collections)
- [Lists and tables](https://developer.apple.com/design/human-interface-guidelines/lists-and-tables)
- [Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
- [Swift concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
