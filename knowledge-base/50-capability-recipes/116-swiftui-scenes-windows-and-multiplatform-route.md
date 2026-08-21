# SwiftUI scenes, windows, and multiplatform capability route

## Use this route when

Choose this route when a feature needs one or more of the following:

- a primary workspace plus a focused auxiliary task;
- one window per document, project, or review request;
- programmatic opening or closing of a window;
- URL, Handoff, widget, App Intent, notification, or external activity entry;
- per-window draft, selection, focus, or restoration;
- iPadOS multitasking or Stage Manager;
- Mac Catalyst window/menu/keyboard adaptation;
- visionOS window, volume, or immersive composition;
- a watchOS companion projection;
- an on-device AI task that needs a bounded review window.

If the outcome fits cleanly inside the current surface, keep it in the current
surface. A second window is a product decision, not a styling primitive.

## Route contract

Define the route before writing the scene declaration.

| Contract field | Required decision |
| --- | --- |
| User task | What parallel or focused work does the window enable? |
| Scene kind | WindowGroup, Window, DocumentGroup, spatial scene, or target-specific watch scene |
| Presentation value | Lightweight stable ID or typed value; never a live model or unreviewed candidate |
| Scene/window identity | How is this instance distinguished from the domain record? |
| Domain resolution | How does the destination fetch current authorized truth? |
| External request | Which URL/activity/system surface can request the task? |
| Existing-scene policy | Prefer an open scene, allow a new one, or fall back in place |
| Restoration | Which small values restore, and what revalidation runs first? |
| Lifecycle | What pauses, cancels, checkpoints, or releases on phase/disconnect? |
| Target matrix | iPhone, iPadOS, Catalyst, visionOS, watchOS; shared and split code |
| Input | Touch, keyboard, pointer, Pencil, eyes/hands, crown, VoiceOver, Switch Control |
| Material | Native window treatment plus bounded content effects and fallback |
| AI | Capability, source revision, candidate review, commit, and cancellation |
| Proof | Preview, compile, UI, multiwindow, physical, system, archive, release |

## 1. Select the scene route

Start from the user outcome:

~~~text
one task, no parallel context
    -> current view, sheet, popover, or focused navigation

parallel context with one shared task
    -> auxiliary Window

repeated instances of the same task
    -> WindowGroup

typed record or document per instance
    -> WindowGroup(for: LightweightID.self) or DocumentGroup

spatial 3D content
    -> visionOS window, volume, or immersive route

glanceable companion task
    -> watchOS target-specific scene
~~~

Do not use a WindowGroup solely because a platform supports windows. If opening
a new window creates state ambiguity, prefer a native presentation inside the
existing scene.

## 2. Define a lightweight presentation value

Use a small, stable, Codable/Hashable value when the current SDK requires it.

~~~swift
struct ProjectWindowValue: Hashable, Codable, Sendable {
    let projectID: Project.ID
    let sourceRevision: Int?
}
~~~

The destination must still:

1. verify the account and authorization;
2. load current domain state;
3. compare the requested source revision;
4. handle deletion, migration, or conflict;
5. show a recoverable unavailable state;
6. keep the presentation value separate from the model object.

A source revision is useful for deciding whether an AI proposal or external
request is stale. It is not a substitute for a database transaction.

## 3. Declare primary and auxiliary scenes

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

        WindowGroup(for: ProjectWindowValue.self) { $value in
            ProjectWindowRoute(value: value)
        }
    }
}
~~~

Keep the scene graph readable. Each declaration should answer:

- what task it represents;
- whether it is repeated or single-instance;
- which target supports it;
- what closes it;
- which feature owns the route;
- what proof artifact names it.

For document-based work, use the document system rather than wrapping a
generic window group around a file workflow.

## 4. Open by ID or typed value

~~~swift
struct ProjectOpenActions: View {
    let projectID: Project.ID
    @Environment(\.openWindow) private var openWindow

    var body: some View {
        HStack {
            Button("Open project window") {
                openWindow(value: ProjectWindowValue(
                    projectID: projectID,
                    sourceRevision: nil
                ))
            }

            Button("Open connection doctor") {
                openWindow(id: "connection-doctor")
            }
        }
    }
}
~~~

When a typed value already identifies an open window, the system may bring it
forward. Treat that as UI behavior. The feature must still deduplicate
network/model work at its own boundary.

For a platform without multiple-window support, provide a route such as:

~~~swift
enum WindowFallback {
    case presentInCurrentScene
    case showSheet
    case showUnavailable
}
~~~

Choose the fallback from platform capability and task meaning, not from a
preview-only environment override.

## 5. Normalize external entry points

One route should receive Universal Links, custom URLs, Handoff, notifications,
widgets, and App Intents as typed requests.

~~~swift
enum ExternalSceneRequest: Hashable, Sendable {
    case project(Project.ID)
    case compose
    case connectionDoctor
}

struct ExternalRequestRouter {
    func parse(url: URL) -> ExternalSceneRequest? {
        guard url.scheme == "bishop-projects" else { return nil }
        switch (url.host, url.pathComponents.dropFirst().first) {
        case ("project", let rawID?):
            return Project.ID(rawValue: rawID).map(ExternalSceneRequest.project)
        case ("connection", _):
            return .connectionDoctor
        default:
            return nil
        }
    }
}
~~~

At the application/scene coordinator boundary, record the source and request
ID, validate current account state, and select the scene. Inside the selected
view, use onOpenURL or onContinueUserActivity to finish feature routing.

Use the scene-level external-event matcher to choose a new scene when needed.
Use the view-level preference/allowing route only for an already-open scene.
Test the event source that actually delivers the request.

## 6. Restoration and lifecycle

Keep restoration small and owned:

~~~swift
struct ProjectWindowRoute: View {
    let value: ProjectWindowValue
    @Environment(\.scenePhase) private var scenePhase
    @SceneStorage("project-draft-state") private var draftState: String = ""

    var body: some View {
        ProjectDetail(projectID: value.projectID, draft: $draftState)
            .task(id: value) {
                await loadCurrentProject()
            }
            .onChange(of: scenePhase) { _, phase in
                if phase != .active {
                    cancelSceneOwnedWork()
                }
            }
    }

    private func loadCurrentProject() async {
        // Resolve current authorized data through a feature-owned service.
    }

    private func cancelSceneOwnedWork() {
        // Cancel or checkpoint the feature task; do not erase the draft.
    }
}
~~~

A real implementation should use a task owner or model actor whose lifetime
is explicit. Revalidate restored IDs and drafts before presenting them. Use
SwiftData/Core Data/CloudKit for durable records and conflict handling.

## 7. iPadOS and Catalyst target branches

Use shared meaning with target-specific shell composition:

~~~swift
struct PlatformWorkspace: View {
    var body: some View {
        #if os(iOS)
        iOSWorkspace()
        #elseif targetEnvironment(macCatalyst)
        CatalystWorkspace()
        #elseif os(visionOS)
        SpatialWorkspace()
        #elseif os(watchOS)
        WatchWorkspace()
        #else
        UnsupportedPlatformView()
        #endif
    }
}
~~~

The exact conditional structure depends on the package target and SDK. Keep
platform code close to the presentation boundary; do not leak UIKit,
watchOS-only, or visionOS-only types into a shared domain module.

For iPadOS, test multiple scenes, split view, rotation, Stage Manager, narrow
resizing, pointer, keyboard, and Pencil routes where supported.

For Mac Catalyst, compile and run the actual Catalyst target on Mac and test
window resize, menu/toolbar, pointer, keyboard, selection, and idiom.

For visionOS, choose a documented window/volume/immersive route and test
comfort, depth, scale, indirect focus, and dismissal on the spatial target.

For watchOS, project only the short task data and action needed by the watch;
do not reuse the phone's window assumptions.

## 8. Liquid Glass scene shell

Keep scene/window styling native-first:

~~~swift
struct FocusedReviewWindow<Content: View>: View {
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
    }
}
~~~

Use the current target SDK's Liquid Glass APIs and availability checks. The
scene/window system remains responsible for system chrome, window controls,
spatial treatment, and platform behavior. The custom glass surface should
group related content, not replace a system window or turn every child into a
floating capsule.

## 9. On-device AI task-window state

Use a typed fixture and adapter state:

~~~swift
struct AIWindowState: Sendable {
    enum Availability: Sendable {
        case checking
        case unavailable
        case ready
    }

    enum Review: Sendable {
        case idle
        case generating
        case partial(text: String)
        case stale
        case failed
        case readyToReview(text: String)
        case committed
    }

    let sceneRequestID: String
    let sourceRevision: Int
    let availability: Availability
    let review: Review
}
~~~

The adapter owns model/session lifetime, context, cancellation, and output
validation. The scene view renders the state and reports review intent. A
commit operation rechecks source revision and authorization.

Preview at least unavailable, partial, stale, failed, ready-to-review, and
committed states. Do not create a live model session in the scene initializer
or claim model readiness from a preview.

## 10. Proof packet

For a scene route, collect:

- scene declaration and target membership;
- Info.plist/capability configuration for multiple scenes where claimed;
- typed value and domain-resolution tests;
- openWindow by ID and by value;
- duplicate-value behavior and existing-window focus;
- cold/warm/terminated external event delivery;
- scene restoration and stale-ID recovery;
- iPadOS resize/split/Stage Manager run;
- Catalyst run on Mac;
- visionOS or watchOS target run when claimed;
- VoiceOver, keyboard, pointer, Dynamic Type, locale/RTL, and reduced-effects
  task completion;
- AI unavailable/cancelled/stale/committed fixture and device result;
- signed archive and release metadata.

## Stop conditions

Pause the route if:

- a scene ID is being used as durable domain truth;
- a window presentation value contains a live model or unvalidated side effect;
- an external URL bypasses authorization or source-revision validation;
- a preview hides a required target configuration;
- a new window is opened for decoration rather than task value;
- a target claims iPad/Catalyst/visionOS/watchOS behavior without its own
  compile/runtime evidence;
- an AI candidate appears committed without a reviewable domain action;
- closing/backgrounding a scene has no cancellation or draft policy.

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
- [Mac Catalyst HIG](https://developer.apple.com/design/human-interface-guidelines/mac-catalyst)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
