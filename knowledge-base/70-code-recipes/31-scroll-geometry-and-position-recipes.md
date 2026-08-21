# Scroll geometry and position recipes

## Compile boundary

These are route sketches for a named iOS 26 target, not compiled code in this documentation workspace. Confirm exact overloads, availability, imports, target membership, and device behavior in Xcode. Keep scroll state separate from domain truth and model side effects.

## Recipe 1: semantic position for stable items

    struct Item: Identifiable, Hashable {
        let id: UUID
        let title: String
    }

    struct ItemList: View {
        let items: [Item]
        @State private var position = ScrollPosition(idType: Item.ID.self)

        var body: some View {
            ScrollView {
                LazyVStack(alignment: .leading) {
                    ForEach(items) { item in
                        Text(item.title)
                            .id(item.id)
                            .padding()
                    }
                }
                .scrollTargetLayout()
            }
            .scrollPosition($position)
        }
    }

Use stable app-owned IDs. Decide how reordered, deleted, or filtered items affect the position. Do not use a transient array index for a restoreable record position.

## Recipe 2: jump to an item with an explicit reason

    struct JumpingList: View {
        let items: [Item]
        @State private var position = ScrollPosition(idType: Item.ID.self)

        var body: some View {
            VStack {
                Button("Show current item") {
                    guard let target = items.first else { return }
                    position.scrollTo(id: target.id, anchor: .center)
                    recordScrollReason(.searchResult)
                }

                ScrollView {
                    LazyVStack {
                        ForEach(items) { item in
                            ItemRow(item: item)
                                .id(item.id)
                        }
                    }
                    .scrollTargetLayout()
                }
                .scrollPosition($position)
            }
        }
    }

The recordScrollReason call is product-owned state, not a SwiftUI API. The reason should explain why the view moved and should not contain sensitive text. Scroll only as far as needed to restore context.

## Recipe 3: project geometry into a small state value

    struct ScrollChrome: View {
        @State private var isPastHeader = false
        @State private var isNearBottom = false

        var body: some View {
            ScrollView {
                Content()
            }
            .onScrollGeometryChange(for: Bool.self) { geometry in
                geometry.visibleRect.minY > geometry.contentInsets.top + 40
            } action: { _, newValue in
                isPastHeader = newValue
            }
            .onScrollGeometryChange(for: Bool.self) { geometry in
                geometry.visibleRect.maxY
                    >= geometry.contentSize.height
                    - geometry.contentInsets.bottom
                    - 80
            } action: { _, newValue in
                isNearBottom = newValue
            }
        }
    }

This sketch intentionally projects geometry to Bool values. Tune the thresholds for the actual content and safe-area contract. Do not store or broadcast the raw ScrollGeometry on every scroll tick.

## Recipe 4: follow-bottom only while the person chooses it

    enum FollowMode {
        case followingBottom
        case browsing
    }

    struct StreamingReview: View {
        let sections: [Section]
        @State private var position = ScrollPosition(idType: Section.ID.self)
        @State private var followMode = FollowMode.followingBottom
        @State private var pendingNewContent = 0

        var body: some View {
            ScrollView {
                LazyVStack {
                    ForEach(sections) { section in
                        SectionView(section)
                            .id(section.id)
                    }
                }
                .scrollTargetLayout()
            }
            .scrollPosition($position, anchor: .bottom)
            .onScrollGeometryChange(for: Bool.self) { geometry in
                geometry.visibleRect.maxY
                    >= geometry.contentSize.height
                    - geometry.contentInsets.bottom
                    - 48
            } action: { _, nearBottom in
                if nearBottom {
                    followMode = .followingBottom
                    pendingNewContent = 0
                } else {
                    followMode = .browsing
                }
            }
            .overlay(alignment: .bottom) {
                if pendingNewContent > 0 && followMode == .browsing {
                    Button("Show new content") {
                        position.scrollTo(edge: .bottom)
                        followMode = .followingBottom
                        pendingNewContent = 0
                    }
                    .buttonStyle(.borderedProminent)
                }
            }
        }
    }

The overlay is only a sketch. A production route should own the action in the safe area or toolbar, avoid covering content, and distinguish an explicit return action from incidental proximity to the bottom.

## Recipe 5: observe visible target IDs

    ScrollView {
        LazyVStack {
            ForEach(items) { item in
                ItemRow(item: item)
                    .id(item.id)
            }
        }
        .scrollTargetLayout()
    }
    .onScrollTargetVisibilityChange(
        idType: Item.ID.self,
        threshold: 0.5
    ) { visibleIDs in
        updateVisibleIDs(visibleIDs)
    }

Keep updateVisibleIDs bounded and cheap. Use visible IDs to cancel or prioritize local work, not to mark content read, approve a suggestion, or launch an unbounded model request.

## Recipe 6: item-level visibility for cancellable work

    ItemRow(item: item)
        .onScrollVisibilityChange(threshold: 0.5) { isVisible in
            if isVisible {
                startBoundedPreview(for: item.id)
            } else {
                cancelPreview(for: item.id)
            }
        }

The service behind these functions must be cancellable, deduplicated, privacy-reviewed, and able to use a cached/partial result. A visible view may be created and destroyed repeatedly in a lazy container.

## Recipe 7: phase-aware expensive work

    ScrollView {
        Content()
    }
    .onScrollPhaseChange { oldPhase, newPhase, context in
        if newPhase == .idle || newPhase == .decelerating {
            scheduleNonessentialWork(
                contentOffset: context.geometry.contentOffset,
                velocity: context.velocity
            )
        }
        if oldPhase == .interacting, newPhase != .animating {
            finishTransientScrollUI()
        }
    }

Check the exact available overload in the selected SDK. Do not use this callback for primary domain writes, permission requests, or irreversible actions. If a phase-driven visual effect is removed for Reduce Motion or Look to Scroll, the semantic content and controls must remain.

## Recipe 8: paging or view-aligned targets

    ScrollView(.horizontal) {
        LazyHStack(spacing: 16) {
            ForEach(cards) { card in
                CardView(card)
                    .containerRelativeFrame(.horizontal)
            }
        }
        .scrollTargetLayout()
    }
    .scrollTargetBehavior(.viewAligned)

Use paging when the container itself is the meaningful page. Use viewAligned when each card is the meaningful target. Test long labels, variable card heights, keyboard/pointer input, VoiceOver, and incomplete final pages.

## Recipe 9: visibility-aware AI proposal

    func requestVisibleSuggestion(
        for itemID: Item.ID,
        sourceRevision: UUID
    ) async throws -> Suggestion {
        guard userInitiated else {
            throw SuggestionError.userActionRequired
        }
        return try await model.generate(
            itemID: itemID,
            sourceRevision: sourceRevision,
            maximumOutputCharacters: 1200
        )
    }

Visibility can identify the current item, but userInitiated must come from an explicit action or product-approved interaction. Re-check the source revision before presenting or applying the result. Keep the proposal in draft state and provide an unavailable/error/canceled route.

## Recipe 10: input-specific scroll policy

    ScrollView {
        Content()
    }
    .scrollInputBehavior(.enabled, for: .keyboard)

Use ScrollInputBehavior only for a real input conflict. Confirm the exact ScrollInputKind case and availability in the selected SDK. Do not broadly disable scrolling to work around a floating control that should instead be placed in the safe area.

## Sources

- [Scroll views](https://developer.apple.com/documentation/swiftui/scroll-views)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [scrollPosition(_:anchor:)](https://developer.apple.com/documentation/swiftui/view/scrollposition%28_%3Aanchor%3A%29)
- [scrollPosition(id:anchor:)](https://developer.apple.com/documentation/swiftui/view/scrollposition%28id%3Aanchor%3A%29)
- [ScrollGeometry](https://developer.apple.com/documentation/swiftui/scrollgeometry)
- [onScrollGeometryChange(for:of:action:)](https://developer.apple.com/documentation/swiftui/view/onscrollgeometrychange%28for%3Aof%3Aaction%3A%29/)
- [onScrollTargetVisibilityChange(idType:threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrolltargetvisibilitychange%28idtype%3Athreshold%3A_%3A%29)
- [onScrollVisibilityChange(threshold:_:)](https://developer.apple.com/documentation/swiftui/view/onscrollvisibilitychange%28threshold%3A_%3A%29)
- [onScrollPhaseChange(_:)](https://developer.apple.com/documentation/swiftui/view/onscrollphasechange%28_%3A%29)
- [ScrollPhase](https://developer.apple.com/documentation/swiftui/scrollphase)
- [ScrollPhaseChangeContext](https://developer.apple.com/documentation/swiftui/scrollphasechangecontext)
- [ScrollTargetBehavior](https://developer.apple.com/documentation/swiftui/scrolltargetbehavior)
- [scrollTargetBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/scrolltargetbehavior%28_%3A%29)
- [scrollTransition(_:axis:transition:)](https://developer.apple.com/documentation/swiftui/view/scrolltransition%28_%3Aaxis%3Atransition%3A%29)
- [ScrollInputBehavior](https://developer.apple.com/documentation/swiftui/scrollinputbehavior)
- [scrollInputBehavior(_:for:)](https://developer.apple.com/documentation/swiftui/view/scrollinputbehavior%28_%3Afor%3A%29)
- [ScrollAnchorRole](https://developer.apple.com/documentation/swiftui/scrollanchorrole)
- [Human Interface Guidelines: Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views)
- [Human Interface Guidelines: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
