# SwiftUI interoperability and adaptive-platform recipes

## Recipe rules

These are route starters for an iOS 26-era SwiftUI feature that may cross
between SwiftUI, UIKit, multiple device families, Liquid Glass, and
on-device AI. They are intentionally small. They are not a claim that this
documentation workspace compiles them as-is.

Before copying a recipe:

1. Confirm the exact SDK signature and availability in Xcode.
2. Inject a deterministic fixture or feature-owned dependency.
3. Define ownership for state, delegates, tasks, cancellation, and teardown.
4. Test light/dark, contrast, Dynamic Type, reduced motion, reduced
   transparency, RTL, VoiceOver, keyboard, pointer, and touch where relevant.
5. Compile and exercise the route on each target it claims to support.
6. Record physical-device, simulator, Catalyst, preview, and release evidence
   separately.

The examples use tilde fences so the Markdown remains easy to copy into a
Swift notebook.

## 1. Named preview with deterministic dependencies

Keep preview construction explicit. A preview should not reach into a live
account, network, clock, location, model session, or device-only permission
without a controlled fixture.

~~~swift
struct ProjectSummary: View {
    struct Dependencies {
        var projectName: String
        var completedCount: Int
        var totalCount: Int
        var openDetails: () -> Void
    }

    let dependencies: Dependencies

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(dependencies.projectName)
                .font(.headline)

            ProgressView(
                value: Double(dependencies.completedCount),
                total: Double(max(dependencies.totalCount, 1))
            )

            Button("Open details", action: dependencies.openDetails)
        }
        .padding()
    }
}

#Preview("Project summary — complete") {
    ProjectSummary(
        dependencies: .init(
            projectName: "Launch checklist",
            completedCount: 8,
            totalCount: 8,
            openDetails: {}
        )
    )
    .padding()
}
~~~

A fixture closure should not silently perform navigation or mutate a shared
store. Use a recorder when the preview must prove an interaction:

~~~swift
@MainActor
final class PreviewRecorder: ObservableObject {
    @Published private(set) var events: [String] = []

    func record(_ event: String) {
        events.append(event)
    }
}

#Preview("Project summary — action") {
    let recorder = PreviewRecorder()

    return ProjectSummary(
        dependencies: .init(
            projectName: "Review queue",
            completedCount: 2,
            totalCount: 5,
            openDetails: { recorder.record("open-details") }
        )
    )
    .environmentObject(recorder)
}
~~~

For a stateful screen, prefer a small fixture store or @Previewable state
supported by the SDK rather than making the preview depend on production
singletons. Keep the fixture ID and state revision visible in the proof log.

## 2. Preview traits and environment matrix

Treat environment values as inputs to layout and visual hierarchy. A single
preview is not evidence for all device conditions.

~~~swift
#Preview("Adaptive surface — dark, large type") {
    AdaptiveSurface()
        .environment(\.colorScheme, .dark)
        .environment(\.dynamicTypeSize, .accessibility2)
        .environment(\.layoutDirection, .rightToLeft)
        .environment(\.locale, Locale(identifier: "ar"))
        .environment(\.horizontalSizeClass, .compact)
        .environment(\.verticalSizeClass, .regular)
}
~~~

Prefer preview traits and named scenarios that make the expected condition
obvious. Add separate scenarios for:

- compact and regular horizontal space;
- short and tall vertical space;
- light and dark appearance;
- increased contrast;
- standard and accessibility Dynamic Type;
- English, a longer localized language, and RTL;
- reduced motion and reduced transparency;
- keyboard, pointer, and touch interaction where the screen changes.

Do not force a size class in production just because it makes a preview look
good. The production environment is owned by the system and the composition
must respond to the available space.

## 3. A small UIKit view escape hatch

Use UIViewRepresentable only when the required behavior is not already
available in SwiftUI or when a UIKit control is the correct system surface.
SwiftUI owns the representable's position and size; the wrapper owns the
UIKit view's configuration and delegate bridge.

~~~swift
struct SearchFieldRepresentable: UIViewRepresentable {
    @Binding var text: String
    var placeholder: String
    var onSubmit: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self)
    }

    func makeUIView(context: Context) -> UISearchTextField {
        let view = UISearchTextField(frame: .zero)
        view.placeholder = placeholder
        view.delegate = context.coordinator
        view.addTarget(
            context.coordinator,
            action: #selector(Coordinator.textChanged(_:)),
            for: .editingChanged
        )
        return view
    }

    func updateUIView(_ view: UISearchTextField, context: Context) {
        context.coordinator.parent = self
        if view.text != text {
            view.text = text
        }
        view.placeholder = placeholder
    }

    static func dismantleUIView(
        _ view: UISearchTextField,
        coordinator: Coordinator
    ) {
        view.delegate = nil
        view.removeTarget(
            coordinator,
            action: #selector(Coordinator.textChanged(_:)),
            for: .editingChanged
        )
    }

    @MainActor
    final class Coordinator: NSObject, UISearchTextFieldDelegate {
        var parent: SearchFieldRepresentable

        init(parent: SearchFieldRepresentable) {
            self.parent = parent
        }

        @objc func textChanged(_ sender: UISearchTextField) {
            parent.text = sender.text ?? ""
        }

        func textFieldShouldReturn(_ textField: UITextField) -> Bool {
            parent.onSubmit()
            textField.resignFirstResponder()
            return true
        }
    }
}
~~~

The coordinator is a bridge, not a second source of truth. Do not start an
unbounded task in updateUIView. If UIKit emits a callback during update, make
the binding write idempotent and guard against feedback loops. If the wrapped
control has asynchronous work, cancel it in an owner that has a defined
lifetime and stop accepting callbacks after teardown.

## 4. A UIKit view controller route

Use UIViewControllerRepresentable when the system operation has controller
lifecycle, presentation, delegates, or a result/cancel boundary.

~~~swift
struct DocumentPickerRoute: UIViewControllerRepresentable {
    let contentTypes: [UTType]
    let didPick: ([URL]) -> Void
    let didCancel: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self)
    }

    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let controller = UIDocumentPickerViewController(
            forOpeningContentTypes: contentTypes,
            asCopy: true
        )
        controller.allowsMultipleSelection = true
        controller.delegate = context.coordinator
        return controller
    }

    func updateUIViewController(
        _ controller: UIDocumentPickerViewController,
        context: Context
    ) {
        context.coordinator.parent = self
    }

    static func dismantleUIViewController(
        _ controller: UIDocumentPickerViewController,
        coordinator: Coordinator
    ) {
        controller.delegate = nil
    }

    @MainActor
    final class Coordinator: NSObject, UIDocumentPickerDelegate {
        var parent: DocumentPickerRoute
        private var finished = false

        init(parent: DocumentPickerRoute) {
            self.parent = parent
        }

        func documentPicker(
            _ controller: UIDocumentPickerViewController,
            didPickDocumentsAt urls: [URL]
        ) {
            guard !finished else { return }
            finished = true
            parent.didPick(urls)
        }

        func documentPickerWasCancelled(
            _ controller: UIDocumentPickerViewController
        ) {
            guard !finished else { return }
            finished = true
            parent.didCancel()
        }
    }
}
~~~

The real route still needs presentation state, security-scoped URL handling
where required, authorization/error states, and a deterministic test seam.
Do not make a view controller wrapper own a feature repository.

## 5. Hosting SwiftUI inside UIKit

UIHostingController is the route when an existing UIKit navigation,
presentation, or container owns the screen and SwiftUI owns a portion of its
content.

~~~swift
final class ProjectViewController: UIViewController {
    private var hostingController: UIHostingController<ProjectSummary>?

    override func viewDidLoad() {
        super.viewDidLoad()

        let view = ProjectSummary(
            dependencies: .init(
                projectName: "UIKit-owned project",
                completedCount: 3,
                totalCount: 4,
                openDetails: { [weak self] in
                    self?.showDetails()
                }
            )
        )

        let host = UIHostingController(rootView: view)
        addChild(host)
        host.view.translatesAutoresizingMaskIntoConstraints = false
        self.view.addSubview(host.view)
        NSLayoutConstraint.activate([
            host.view.leadingAnchor.constraint(equalTo: self.view.leadingAnchor),
            host.view.trailingAnchor.constraint(equalTo: self.view.trailingAnchor),
            host.view.topAnchor.constraint(equalTo: self.view.safeAreaLayoutGuide.topAnchor),
            host.view.bottomAnchor.constraint(equalTo: self.view.bottomAnchor)
        ])
        host.didMove(toParent: self)
        hostingController = host
    }

    private func showDetails() {
        // UIKit owns navigation; the SwiftUI child reports intent.
    }
}
~~~

Use a feature-owned observable model or explicit input/output closures for
updates. If the UIKit parent replaces rootView, preserve identity and
ownership intentionally; do not rebuild the host on every callback.

## 6. SwiftUI content in a UIKit cell

UIHostingConfiguration is a focused bridge for SwiftUI content inside UIKit
collection or table cells. The cell still has reuse identity and the data
source still owns the item lifecycle.

~~~swift
cell.contentConfiguration = UIHostingConfiguration {
    ProjectRow(project: project)
        .contentShape(Rectangle())
        .onTapGesture {
            onSelect(project.id)
        }
}
.margins(.vertical, 8)
.background(.clear)
~~~

Prefer a semantic UIKit selection path when the collection view owns
selection. If SwiftUI owns a gesture, test VoiceOver, pointer, keyboard, and
selection-state synchronization. Ensure a reused cell receives the current
project ID and does not retain a stale closure or task.

## 7. Adaptive composition by available space

Use semantic environment values and layout tools to choose composition. Avoid
hard-coding a device model or treating orientation as the only signal.

~~~swift
struct AdaptiveProjectSurface: View {
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @Environment(\.verticalSizeClass) private var verticalSizeClass

    var body: some View {
        Group {
            if horizontalSizeClass == .regular {
                AnyLayout(HStackLayout(spacing: 24)) {
                    ProjectSummaryColumn()
                    ProjectActivityColumn()
                }
            } else {
                AnyLayout(VStackLayout(spacing: 16)) {
                    ProjectSummaryColumn()
                    ProjectActivityColumn()
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
~~~

When the choice is content fit rather than platform semantics, use ViewThatFits
so the system can select the first layout that fits:

~~~swift
ViewThatFits(in: .horizontal) {
    HStack {
        CompactProjectActions()
        ExpandedProjectActions()
    }

    VStack(alignment: .leading) {
        ExpandedProjectActions()
        CompactProjectActions()
    }
}
~~~

For a custom arrangement, implement Layout and measure subviews rather than
using screen width as a proxy. Add a small-width preview and test split view,
Stage Manager, rotation, keyboard, and external display where supported.

## 8. Localized, RTL, and Dynamic Type fixture

Use semantic text alignment, system fonts, and flexible containers. A fixture
should make long strings and RTL visible early.

~~~swift
#Preview("Arabic — accessibility type") {
    ProjectSummary(
        dependencies: .init(
            projectName: "قائمة مراجعة الإطلاق الطويلة",
            completedCount: 4,
            totalCount: 7,
            openDetails: {}
        )
    )
    .environment(\.locale, Locale(identifier: "ar"))
    .environment(\.layoutDirection, .rightToLeft)
    .environment(\.dynamicTypeSize, .accessibility3)
    .frame(width: 340)
}
~~~

Do not manually reverse an HStack or use left/right alignment as a shortcut.
Use leading/trailing semantics and verify text expansion, truncation,
pluralization, date/number formatting, and bidirectional input.

## 9. Liquid Glass-aware hybrid shell

Keep the feature content independent from the material treatment. A bridge
should provide content and actions; the SwiftUI shell should own the visual
surface.

~~~swift
struct HybridGlassShell<Content: View>: View {
    let title: LocalizedStringKey
    @ViewBuilder let content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(title)
                .font(.headline)

            content()
        }
        .padding(20)
        .glassEffect(.regular, in: .rect(cornerRadius: 24))
        .glassEffectID("project-shell", in: GlassEffectContainer())
    }
}
~~~

Use the Liquid Glass APIs supported by the target SDK and follow the
availability boundary. Do not apply a glass layer to every row. Keep one
clearly legible hierarchy, test content behind the surface, and provide a
reduced-transparency or supported fallback route when the environment asks
for it. A UIKit representable should not assume it can recreate the entire
SwiftUI glass system by setting blur properties.

## 10. On-device AI preview fixtures

Preview AI states, not a live model session. Keep input provenance and output
revision in the fixture so a stale result cannot look committed.

~~~swift
struct SuggestionFixture: Identifiable, Sendable {
    enum Status: Sendable {
        case unavailable(reason: String)
        case loading
        case partial
        case ready
        case failed
    }

    let id: String
    let sourceRevision: Int
    let text: String
    let status: Status
    let canCommit: Bool
}

#Preview("AI unavailable") {
    SuggestionReviewRow(
        fixture: SuggestionFixture(
            id: "preview-unavailable-1",
            sourceRevision: 4,
            text: "The device model is unavailable.",
            status: .unavailable(reason: "Not supported on this device"),
            canCommit: false
        ),
        commit: {}
    )
}

#Preview("AI partial — review required") {
    SuggestionReviewRow(
        fixture: SuggestionFixture(
            id: "preview-partial-1",
            sourceRevision: 5,
            text: "Draft suggestion requiring review.",
            status: .partial,
            canCommit: false
        ),
        commit: {}
    )
}
~~~

The production adapter owns capability checks, model/session lifetime,
cancellation, prompt/input policy, authorization, and error mapping. The view
renders explicit unavailable/loading/partial/ready/failed states. Never let a
preview imply that a model is installed, that a result is correct, or that a
suggestion is committed.

## 11. Cancellation and stale-result guard

Any asynchronous route must bind its task to the feature identity and reject
results from a superseded source revision.

~~~swift
@MainActor
final class SuggestionStore: ObservableObject {
    @Published private(set) var fixture: SuggestionFixture?
    private var task: Task<Void, Never>?
    private var activeRevision: Int?

    func refresh(
        sourceRevision: Int,
        run: @escaping @Sendable () async throws -> String
    ) {
        task?.cancel()
        activeRevision = sourceRevision
        fixture = SuggestionFixture(
            id: "runtime-\(sourceRevision)",
            sourceRevision: sourceRevision,
            text: "",
            status: .loading,
            canCommit: false
        )

        task = Task { [weak self] in
            do {
                let text = try await run()
                try Task.checkCancellation()
                guard let self, self.activeRevision == sourceRevision else { return }

                self.fixture = SuggestionFixture(
                    id: "runtime-\(sourceRevision)",
                    sourceRevision: sourceRevision,
                    text: text,
                    status: .ready,
                    canCommit: false
                )
            } catch is CancellationError {
                // Cancellation is not a user-visible model failure.
            } catch {
                guard let self, self.activeRevision == sourceRevision else { return }
                self.fixture = SuggestionFixture(
                    id: "runtime-\(sourceRevision)",
                    sourceRevision: sourceRevision,
                    text: "Suggestion unavailable.",
                    status: .failed,
                    canCommit: false
                )
            }
        }
    }

    func cancel() {
        task?.cancel()
        task = nil
        activeRevision = nil
    }
}
~~~

In production, make the task owner explicit and ensure run cannot update view
state behind the store's back. Test cancellation, repeated refresh,
backgrounding, teardown, and source replacement.

## 12. Accessibility and alternate-input acceptance view

Give the bridge a semantic label and test the same action through supported
input paths.

~~~swift
struct SearchRoute: View {
    @Binding var query: String
    let submit: () -> Void

    var body: some View {
        SearchFieldRepresentable(
            text: $query,
            placeholder: "Search projects",
            onSubmit: submit
        )
        .frame(minHeight: 44)
        .accessibilityLabel("Search projects")
        .accessibilityHint("Enter a project name, then submit")
    }
}
~~~

Do not add a second invisible SwiftUI control merely to make UIKit accessible.
First configure the bridged control's accessibility traits, label, value,
actions, focus behavior, and Dynamic Type behavior. If the wrapper cannot
supply a native semantic element, expose a deliberate proxy with an explicit
interaction contract and test both paths.

## 13. One acceptance fixture for the whole route

Build a fixture that exercises the same feature state through previews,
simulator UI tests, and a physical-device pass.

~~~swift
struct InteroperabilityFixture {
    let targetName: String
    let sizeClass: UserInterfaceSizeClass
    let locale: Locale
    let layoutDirection: LayoutDirection
    let dynamicTypeSize: DynamicTypeSize
    let colorScheme: ColorScheme
    let aiStatus: SuggestionFixture.Status
    let sourceRevision: Int
}
~~~

Record the fixture in the proof matrix. A screenshot proves appearance at one
state; it does not prove UIKit teardown, model cancellation, RTL behavior,
permission behavior, or release packaging. Keep those checks as separate
evidence rows.

## Sources

- [Previewing your app’s interface in Xcode](https://developer.apple.com/documentation/xcode/previewing-your-apps-interface-in-xcode)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [UIKit integration](https://developer.apple.com/documentation/swiftui/uikit-integration)
- [UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable)
- [UIViewRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewrepresentablecontext)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [UIViewControllerRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentablecontext)
- [UIHostingController](https://developer.apple.com/documentation/swiftui/uihostingcontroller)
- [UIHostingConfiguration](https://developer.apple.com/documentation/swiftui/uihostingconfiguration)
- [UIKit](https://developer.apple.com/documentation/uikit)
- [EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
