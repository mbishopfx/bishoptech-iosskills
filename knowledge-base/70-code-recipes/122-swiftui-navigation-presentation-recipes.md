# SwiftUI navigation and presentation recipes

## How to use these recipes

These are compile-oriented route sketches for a named SwiftUI target. They
cover typed navigation, matched zoom transitions, item-based sheets, detents,
presentation sizing, content margins, dismissal safety, Liquid Glass arrival
surfaces, and on-device AI review state.

Check the selected Xcode/SDK signature, deployment target, platform
availability, and target membership before adopting a route. Previews and
simulator runs do not prove public deep-link delivery, physical accessibility,
haptics, system surfaces, or release behavior.

Related pages:

- [SwiftUI navigation transitions and presentation](../42-framework-deep-dives/79-swiftui-navigation-transitions-and-presentation.md)
- [Navigation transitions and presentation design](../21-design-deep-dives/107-navigation-transitions-and-presentation-design.md)
- [SwiftUI navigation and presentation route](../50-capability-recipes/110-swiftui-navigation-presentation-route.md)
- [SwiftUI navigation and presentation proof matrix](../60-verification/104-swiftui-navigation-presentation-proof-matrix.md)

## Recipe 1: typed NavigationStack path

Keep the path lightweight and resolve the current record at the destination.

~~~swift
import SwiftUI

enum AppRoute: Hashable, Codable {
    case inbox
    case detail(id: UUID)
    case review(proposalID: UUID)
}

struct RootScreen: View {
    @State private var path: [AppRoute] = []

    var body: some View {
        NavigationStack(path: $path) {
            List {
                NavigationLink("Open inbox", value: AppRoute.inbox)
                NavigationLink(
                    "Open detail",
                    value: AppRoute.detail(id: UUID())
                )
            }
            .navigationDestination(for: AppRoute.self) { route in
                switch route {
                case .inbox:
                    Text("Inbox")
                case .detail(let id):
                    Text("Detail \(id.uuidString)")
                case .review(let proposalID):
                    Text("Review \(proposalID.uuidString)")
                }
            }
            .navigationTitle("Workspace")
        }
    }
}
~~~

Use a stable domain ID instead of creating a new UUID at the tap site in a
real feature. Keep route decoding and authorization at the destination.

## Recipe 2: matched source and zoom destination

Pair a stable source ID and namespace with a navigation transition.

~~~swift
struct CardToDetail: View {
    let recordID: UUID
    @Namespace private var namespace

    var body: some View {
        NavigationStack {
            NavigationLink(value: recordID) {
                Label("Open record", systemImage: "doc.text")
                    .padding()
                    .matchedTransitionSource(id: recordID, in: namespace)
            }
            .navigationDestination(for: UUID.self) { id in
                RecordDetail(id: id)
                    .navigationTransition(
                        .zoom(sourceID: id, in: namespace)
                    )
            }
        }
    }
}

struct RecordDetail: View {
    let id: UUID

    var body: some View {
        Text("Record \(id.uuidString)")
            .navigationTitle("Record")
    }
}
~~~

The current SDK may require the transition on a specific destination shape or
availability condition. Compile in the target and add automatic/identity
fallback where needed. Preserve title, back action, and VoiceOver meaning
without the zoom.

## Recipe 3: item-based sheet for a review proposal

Use an optional Identifiable item when the presentation has domain identity.

~~~swift
struct Proposal: Identifiable {
    let id: UUID
    let text: String
}

struct ProposalParent: View {
    @State private var proposal: Proposal?

    var body: some View {
        Button("Review proposal") {
            proposal = Proposal(id: UUID(), text: "Candidate text")
        }
        .sheet(item: $proposal) { current in
            ProposalReview(proposal: current)
        }
    }
}

struct ProposalReview: View {
    let proposal: Proposal
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 16) {
                Text(proposal.text)
                Button("Accept") {
                    // Call validation and the domain commit before dismissing.
                    dismiss()
                }
            }
            .padding()
            .navigationTitle("Review")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
        }
    }
}
~~~

The optional item is presentation state. The real proposal should be resolved
from a current model/service and accepted only after validation and commit.

## Recipe 4: sheet detents and selection

Expose detents that correspond to meaningful stages.

~~~swift
struct DetentReview: View {
    @State private var isPresented = false
    @State private var selectedDetent: PresentationDetent = .medium

    var body: some View {
        Button("Show review") {
            isPresented = true
        }
        .sheet(isPresented: $isPresented) {
            ReviewContent()
                .presentationDetents(
                    [.medium, .large],
                    selection: $selectedDetent
                )
                .presentationDragIndicator(.visible)
                .presentationContentInteraction(.scrolls)
        }
    }
}

struct ReviewContent: View {
    var body: some View {
        ScrollView {
            Text("Long review content")
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
        }
    }
}
~~~

Check the current PresentationContentInteraction cases in the selected SDK.
Test the medium detent with large text and the large detent with keyboard/input.

## Recipe 5: presentation background and parent interaction

Make parent interaction a deliberate policy.

~~~swift
struct SupplementarySheet: View {
    @State private var isPresented = false

    var body: some View {
        Button("Show tools") {
            isPresented = true
        }
        .sheet(isPresented: $isPresented) {
            VStack(spacing: 16) {
                Text("Supplementary tools")
                Button("Done") {
                    isPresented = false
                }
            }
            .padding()
            .presentationBackground(.regularMaterial)
            .presentationBackgroundInteraction(.enabled(upThrough: .medium))
            .presentationCornerRadius(28)
        }
    }
}
~~~

Only enable parent interaction when the underlying controls remain safe and
independent. For a review/apply task, choose disabled or the system default and
protect the domain operation from duplicate actions.

## Recipe 6: fitted/page presentation sizing

Use system sizing before hard-coded geometry.

~~~swift
struct SizedInfoSheet: View {
    @State private var isPresented = false

    var body: some View {
        Button("Show information") {
            isPresented = true
        }
        .sheet(isPresented: $isPresented) {
            VStack(alignment: .leading, spacing: 12) {
                Text("Information")
                    .font(.headline)
                Text("Content can grow with localization and Dynamic Type.")
            }
            .padding()
            .presentationSizing(
                .page
                    .fitted(horizontal: false, vertical: true)
                    .sticky(horizontal: false, vertical: true)
            )
        }
    }
}
~~~

PresentationSizing is current SDK-sensitive. The app target should confirm the
available system sizing and test short/long content rather than relying on one
fixed screenshot.

## Recipe 7: content margins for scroll content

Keep content and scroll indicators legible in a presentation.

~~~swift
struct MarginedReview: View {
    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 12) {
                Text("Source")
                    .font(.headline)
                Text(String(repeating: "Long source text. ", count: 30))
            }
        }
        .contentMargins(.horizontal, 20, for: .scrollContent)
        .contentMargins(.horizontal, 8, for: .scrollIndicators)
    }
}
~~~

Use the placement that matches the intent. Avoid negative offsets to push
content under a presentation bar or glass action group.

## Recipe 8: safe draft dismissal

Keep dismissal and draft state explicit.

~~~swift
struct DraftEditor: View {
    @Environment(\.dismiss) private var dismiss
    @State private var text = ""
    @State private var showDiscardConfirmation = false

    var isDirty: Bool {
        !text.isEmpty
    }

    var body: some View {
        NavigationStack {
            TextEditor(text: $text)
                .navigationTitle("Edit")
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button("Cancel") {
                            if isDirty {
                                showDiscardConfirmation = true
                            } else {
                                dismiss()
                            }
                        }
                    }
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Done") {
                            Task {
                                let didSave = await save(text)
                                if didSave {
                                    dismiss()
                                }
                            }
                        }
                    }
                }
                .confirmationDialog(
                    "Discard changes?",
                    isPresented: $showDiscardConfirmation,
                    titleVisibility: .visible
                ) {
                    Button("Discard Changes", role: .destructive) {
                        dismiss()
                    }
                    Button("Keep Editing", role: .cancel) { }
                }
        }
    }

    private func save(_ value: String) async -> Bool {
        true
    }
}
~~~

The save placeholder must be replaced by an authorized domain operation. Do
not dismiss because an animation finished or because a request merely started.

## Recipe 9: Liquid Glass arrival group

Let system presentation own the outer surface and keep custom glass functional.

~~~swift
struct GlassReviewActions: View {
    @Namespace private var namespace
    @State private var isExpanded = false

    var body: some View {
        GlassEffectContainer(spacing: 32) {
            HStack(spacing: 16) {
                Button("Accept") {
                    isExpanded = true
                }
                .buttonStyle(.glassProminent)
                .glassEffectID("accept", in: namespace)

                if isExpanded {
                    Button("Reject") {
                        isExpanded = false
                    }
                    .buttonStyle(.glass)
                    .glassEffectID("reject", in: namespace)
                    .glassEffectTransition(.materialize)
                }
            }
        }
    }
}
~~~

Use real model state and a confirmation/commit route. Add a reduced-motion
identity route and profile multiple effects on the target device.

## Recipe 10: route from an external payload

Normalize deep links into the same typed route reducer used by in-app actions.

~~~swift
struct DeepLinkRoot: View {
    @State private var path: [AppRoute] = []

    var body: some View {
        NavigationStack(path: $path) {
            Text("Home")
                .onOpenURL { url in
                    guard let route = AppRoute(url: url) else { return }
                    path = [route]
                }
        }
    }
}

extension AppRoute {
    init?(url: URL) {
        guard url.scheme == "example" else { return nil }
        guard let id = UUID(uuidString: url.lastPathComponent) else { return nil }
        self = .detail(id: id)
    }
}
~~~

The URL parser is not authorization. Re-check the current account, record,
freshness, and permissions before resolving the destination.

## Recipe 11: AI review state and presentation

Keep model state and presentation state separate.

~~~swift
enum ReviewPresentation: Identifiable {
    case proposal(id: UUID)

    var id: UUID {
        switch self {
        case .proposal(let id):
            id
        }
    }
}

enum AIReviewState: Equatable {
    case unavailable(String)
    case idle
    case generating
    case proposal
    case applying
    case saved
    case failed(String)
}

struct AIReviewHost: View {
    @State private var presentation: ReviewPresentation?
    let state: AIReviewState

    var body: some View {
        Button("Review") {
            presentation = .proposal(id: UUID())
        }
        .sheet(item: $presentation) { item in
            AIReviewView(item: item, state: state)
        }
    }
}

struct AIReviewView: View {
    let item: ReviewPresentation
    let state: AIReviewState
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack {
            Text("Proposal \(item.id.uuidString)")
            Text(String(describing: state))
            Button("Close") {
                dismiss()
            }
        }
        .padding()
    }
}
~~~

The real host should only present when a current proposal exists and is
available for review. Keep generated text, validation, and commit outside the
presentation Boolean/item.

## Recipe 12: test matrix fixture

Create named fixtures for route/presentation states:

~~~swift
struct PresentationFixture {
    let route: AppRoute
    let presentation: ReviewPresentation?
    let textLength: Int
    let reduceMotion: Bool
    let reducedTransparency: Bool
    let modelAvailable: Bool
}

let fixtures = [
    PresentationFixture(
        route: .inbox,
        presentation: nil,
        textLength: 20,
        reduceMotion: false,
        reducedTransparency: false,
        modelAvailable: true
    ),
    PresentationFixture(
        route: .review(proposalID: UUID()),
        presentation: .proposal(id: UUID()),
        textLength: 4000,
        reduceMotion: true,
        reducedTransparency: true,
        modelAvailable: false
    )
]
~~~

Pair fixtures with UI tasks for cold/warm navigation, presentation/dismissal,
Dynamic Type, VoiceOver, reduced motion, external payloads, and physical
device/system surfaces.

## Sources

- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [NavigationTransition](https://developer.apple.com/documentation/swiftui/navigationtransition)
- [matchedTransitionSource(id:in:)](https://developer.apple.com/documentation/swiftui/view/matchedtransitionsource%28id%3Ain%3A%29)
- [ZoomNavigationTransition](https://developer.apple.com/documentation/swiftui/zoomnavigationtransition)
- [Modal presentations](https://developer.apple.com/documentation/swiftui/modal-presentations)
- [Presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [PresentationSizing](https://developer.apple.com/documentation/SwiftUI/PresentationSizing)
- [presentationSizing(_:)](https://developer.apple.com/documentation/swiftui/view/presentationsizing%28_%3A%29)
- [contentMargins(_:_:for:)](https://developer.apple.com/documentation/SwiftUI/View/contentMargins%28_%3A_%3Afor%3A%29-1lt8b)
- [PresentationBackgroundInteraction](https://developer.apple.com/documentation/swiftui/presentationbackgroundinteraction)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Modality](https://developer.apple.com/design/human-interface-guidelines/modality)
- [Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets)
