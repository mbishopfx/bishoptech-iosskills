# SwiftUI scenes, windows, and multiplatform recipes

## Recipe rules

These snippets are route starters for a named app target. They are not
compiled in this documentation workspace and do not prove multiple-window
system behavior, external event delivery, physical input, spatial comfort,
watch behavior, model readiness, or release packaging.

Before copying a recipe:

1. Confirm the current SDK signature and availability in Xcode.
2. Name the target, deployment target, scene declaration, and platform claim.
3. Keep presentation values lightweight and resolve domain truth inside.
4. Test cold, warm, background, terminated, duplicate, stale, and unauthorized
   entry.
5. Test Dynamic Type, localization/RTL, VoiceOver, keyboard, pointer,
   reduced effects, and the target's primary input.
6. Record signed physical, system-surface, Catalyst, visionOS, watchOS, and
   release evidence separately.

The examples use tilde fences so they can be copied without confusing this
Markdown file's structure.

## 1. Primary and auxiliary scenes

Declare a normal workspace, a single-instance utility, and a typed record
window separately.

~~~swift
@main
struct ProjectsApp: App {
    var body: some Scene {
        WindowGroup {
            ProjectWorkspace()
        }

        Window("Connection doctor", id: "connection-doctor") {
            ConnectionDoctor()
        }

        WindowGroup(for: Project.ID.self) { $projectID in
            ProjectDetailWindow(projectID: projectID)
        }
    }
}
~~~

Document which targets support each scene. For document-based apps, use the
document scene route instead of pretending a generic WindowGroup owns file
coordination.

## 2. Open a single-instance utility by ID

Use a semantic action and let the system manage the window.

~~~swift
struct ConnectionDoctorButton: View {
    @Environment(\.openWindow) private var openWindow

    var body: some View {
        Button {
            openWindow(id: "connection-doctor")
        } label: {
            Label("Connection doctor", systemImage: "network")
        }
    }
}
~~~

The action should remain useful when the window is already open. Test that it
brings the utility forward, does not duplicate model/network work, and has a
fallback on a target without multiple-window support.

## 3. Open a typed window by a lightweight value

Pass a stable ID or small route value.

~~~swift
struct ProjectWindowValue: Hashable, Codable, Sendable {
    let projectID: Project.ID
    let sourceRevision: Int?
}

struct ProjectWindowButton: View {
    let projectID: Project.ID
    @Environment(\.openWindow) private var openWindow

    var body: some View {
        Button("Open project") {
            openWindow(value: ProjectWindowValue(
                projectID: projectID,
                sourceRevision: nil
            ))
        }
    }
}
~~~

The destination resolves the current record. It must handle deletion,
authorization, migrations, and stale source revisions without treating the
presentation value as domain truth.

## 4. Normalize an external URL

Parse external input at a routing boundary.

~~~swift
enum ExternalSceneRequest: Hashable, Sendable {
    case project(id: Project.ID)
    case compose(source: String)
    case connectionDoctor
}

struct ExternalURLParser {
    func parse(_ url: URL) -> ExternalSceneRequest? {
        guard url.scheme == "bishop-projects" else { return nil }

        switch url.host {
        case "project":
            guard let id = Project.ID(rawValue: url.lastPathComponent) else {
                return nil
            }
            return .project(id: id)
        case "compose":
            return .compose(source: "url")
        case "connection":
            return .connectionDoctor
        default:
            return nil
        }
    }
}
~~~

Keep the parser deterministic and side-effect free. The feature coordinator
should validate account, authorization, freshness, and domain existence before
opening or committing anything.

## 5. Route external events to a scene

Use the scene matcher to help choose a new scene, then use view handlers to
process the event.

~~~swift
@main
struct ProjectsApp: App {
    var body: some Scene {
        WindowGroup {
            ProjectWorkspace()
                .onOpenURL { url in
                    handleIncomingURL(url)
                }
                .onContinueUserActivity(
                    "com.bishoptech.project",
                    perform: handleIncomingActivity
                )
        }
        .handlesExternalEvents(matching: [
            "bishop-projects://project",
            "com.bishoptech.project"
        ])
    }

    private func handleIncomingURL(_ url: URL) {
        // Normalize, validate, and send a typed request to a coordinator.
    }

    private func handleIncomingActivity(_ activity: NSUserActivity) {
        // Validate the typed payload and send the same request route.
    }
}
~~~

The exact external-event matching strings and scene/view modifier signatures
are SDK-sensitive. Verify them in the target. Add a multi-scene fixture that
proves which existing or new scene receives the request.

## 6. Keep per-scene state separate

Use scene-scoped state for small UI continuity and a feature-owned model for
domain work.

~~~swift
struct ProjectDetailWindow: View {
    let projectID: Project.ID
    @SceneStorage("project.selectedTab") private var selectedTab: String = "overview"
    @SceneStorage("project.draftText") private var draftText: String = ""
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        ProjectDetail(
            projectID: projectID,
            selectedTab: $selectedTab,
            draftText: $draftText
        )
        .onChange(of: scenePhase) { _, phase in
            if phase != .active {
                checkpointDraftIfNeeded()
            }
        }
    }

    private func checkpointDraftIfNeeded() {
        // Route to a feature-owned draft store when the draft is durable.
    }
}
~~~

Do not store secrets, large model contexts, or durable domain truth in
SceneStorage. Revalidate a restored project ID before displaying an editor.

## 7. Bind task lifetime to scene identity

Keep async work cancellable and reject results after replacement.

~~~swift
@MainActor
final class SceneFeatureModel: ObservableObject {
    @Published private(set) var status = "Idle"
    private var task: Task<Void, Never>?
    private var activeProjectID: Project.ID?

    func load(projectID: Project.ID) {
        task?.cancel()
        activeProjectID = projectID
        status = "Loading"

        task = Task { [weak self] in
            do {
                let result = try await loadCurrentProject(projectID)
                try Task.checkCancellation()
                guard let self, self.activeProjectID == projectID else { return }
                self.status = result.title
            } catch is CancellationError {
                // Teardown is not a user-visible failure.
            } catch {
                guard let self, self.activeProjectID == projectID else { return }
                self.status = "Unavailable"
            }
        }
    }

    func cancel() {
        task?.cancel()
        task = nil
        activeProjectID = nil
    }
}
~~~

The real repository or actor must own loadCurrentProject. Do not allow a
released scene to receive a callback from a network, media, or AI task.

## 8. Adapt the window by available space

Use environment and layout tools, not device-name checks.

~~~swift
struct ProjectWindowLayout: View {
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

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

Also test ViewThatFits, container-relative sizing, custom Layout, split view,
Stage Manager, rotation, keyboard, and external display where relevant. A
regular size class is available space, not a promise of a specific device.

## 9. Target-specific scene composition

Keep shared feature meaning and separate target shells.

~~~swift
struct TargetWorkspace: View {
    var body: some View {
        #if targetEnvironment(macCatalyst)
        CatalystWorkspace()
        #elseif os(visionOS)
        SpatialWorkspace()
        #elseif os(watchOS)
        WatchWorkspace()
        #else
        IOSWorkspace()
        #endif
    }
}
~~~

Conditional compilation selects code that cannot exist in the shared target.
Availability checks select APIs whose availability varies by SDK/OS. Compile
each target; do not let a preview of one target stand in for another.

## 10. Liquid Glass inside a native window

Apply a bounded content treatment and leave window chrome to the system.

~~~swift
struct AIReviewCard<Content: View>: View {
    @ViewBuilder let content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            content()
        }
        .padding(20)
        .glassEffect(.regular, in: .rect(cornerRadius: 24))
    }
}
~~~

Use target availability and reduced-transparency fallbacks. Do not construct a
custom fake window frame, and do not multiply glass layers across every row.

## 11. On-device AI window fixture

Preview explicit capability and review states.

~~~swift
struct AIWindowFixture: Sendable {
    enum ModelState: Sendable {
        case unavailable
        case ready
    }

    enum ReviewState: Sendable {
        case loading
        case partial
        case stale
        case readyToReview
        case committed
        case failed
    }

    let sceneRequestID: String
    let sourceRevision: Int
    let modelState: ModelState
    let reviewState: ReviewState
}

#Preview("AI window — stale candidate") {
    AIReviewCard {
        VStack(alignment: .leading) {
            Text("Review required")
            Text("This candidate was generated from an older source revision.")
            Label("Not committed", systemImage: "exclamationmark.triangle")
        }
    }
}
~~~

The fixture does not install or invoke a model. The production adapter owns
availability, cancellation, context, output validation, and commit recheck.

## 12. Accessibility and input fixture

Use a task label and test the same action through supported inputs.

~~~swift
struct WindowCloseAction: View {
    let close: () -> Void

    var body: some View {
        Button("Close review window", action: close)
            .keyboardShortcut(.cancelAction)
            .accessibilityHint("Returns to the source workspace")
    }
}
~~~

Test VoiceOver focus when a new window opens, Dynamic Type at narrow sizes,
long localized strings, RTL, keyboard and pointer on iPad/Catalyst, reduced
motion/transparency, and the actual primary input on visionOS/watchOS.

## 13. Acceptance fixture

Keep scene, domain, external, and AI state explicit.

~~~swift
struct SceneAcceptanceFixture: Hashable, Sendable {
    let target: String
    let sceneKind: String
    let windowID: String?
    let domainID: String?
    let sourceRevision: Int?
    let externalEntry: String?
    let phase: String
    let width: Int
    let height: Int
    let locale: String
    let direction: String
    let dynamicType: String
    let aiState: String
}
~~~

Use the same fixture IDs in preview names, UI-test launch arguments, physical
device logs, and the proof matrix. A screenshot only proves the named visual
state; it does not prove scene selection, restoration, or system delivery.

## Sources

- [Scenes](https://developer.apple.com/documentation/swiftui/scenes)
- [Windows](https://developer.apple.com/documentation/swiftui/windows)
- [WindowGroup](https://developer.apple.com/documentation/swiftui/windowgroup)
- [Window](https://developer.apple.com/documentation/swiftui/window)
- [openWindow](https://developer.apple.com/documentation/swiftui/environmentvalues/openwindow)
- [Presenting windows and spaces](https://developer.apple.com/documentation/visionos/presenting-windows-and-spaces)
- [System events](https://developer.apple.com/documentation/swiftui/system-events)
- [handlesExternalEvents(matching:)](https://developer.apple.com/documentation/swiftui/scene/handlesexternalevents%28matching%3A%29)
- [ScenePhase](https://developer.apple.com/documentation/swiftui/scenephase)
- [SceneStorage](https://developer.apple.com/documentation/swiftui/scenestorage)
- [UIApplicationSupportsMultipleScenes](https://developer.apple.com/documentation/BundleResources/Information-Property-List/UIApplicationSceneManifest/UIApplicationSupportsMultipleScenes)
- [Windows HIG](https://developer.apple.com/design/human-interface-guidelines/windows)
- [Multitasking HIG](https://developer.apple.com/design/human-interface-guidelines/multitasking)
- [Mac Catalyst HIG](https://developer.apple.com/design/human-interface-guidelines/mac-catalyst)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
