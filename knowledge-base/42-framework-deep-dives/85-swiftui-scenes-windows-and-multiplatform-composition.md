# SwiftUI scenes, windows, and multiplatform composition

## Purpose

Use this page when a feature needs more than one user-facing scene, needs to
open content from a URL or system activity, restores state per window, or
claims a shared SwiftUI composition across iPhone, iPadOS, Mac Catalyst,
visionOS, or watchOS.

The central contract is:

~~~text
external event or user intent
    -> validated scene request
    -> scene/window selection
    -> scene-scoped feature state
    -> shared domain use case
    -> target-specific presentation and proof
~~~

A scene is a system-managed user-interface grouping. A window is a
user-facing boundary that may contain a scene. A domain record, account, or
AI source is not automatically the same thing as either one.

## 1. Keep identity layers separate

A robust route names at least these identities:

| Identity | Owns | Examples | What it must not become |
| --- | --- | --- | --- |
| App identity | Process-wide configuration and shared services | environment, package configuration, logging, capability policy | A global store for every window's draft |
| Scene identity | One system-managed lifecycle instance | scene session, window instance, scene phase, restoration scope | A durable project/document identity |
| Window identity | User-facing presentation boundary | primary window, compose window, inspector window, document window | A guarantee that one view tree equals one process |
| Domain identity | Business truth | Project.ID, Document.ID, account ID, source revision | A random UI-only UUID |
| External request identity | Delivery and deduplication | URL/activity nonce, request ID, source application | Authorization to mutate domain state |
| AI proposal identity | Generated candidate and provenance | model/session revision, candidate ID, source revision | A committed record or permission to execute an action |

A WindowGroup is a template for identically structured windows. Each instance
can have independent view state. That independence is useful for drafts,
selection, focus, and transient UI, but it does not replace a domain store or
a conflict policy.

If a feature has a primary workspace and an auxiliary task, model both
explicitly. A user closing an auxiliary window is not necessarily deleting the
draft; it is a scene-lifecycle event that the feature must reconcile.

## 2. Choose the smallest scene type

| User outcome | SwiftUI scene route | Identity and lifecycle note |
| --- | --- | --- |
| One ordinary app surface | WindowGroup with one root view | The platform may still manage more than one scene; do not assume one process-wide view |
| Multiple instances of a workspace | WindowGroup | Each window receives independent scene/view state; domain records need stable IDs |
| One auxiliary utility | Window with a unique identifier | Opening an existing utility brings it forward; choose a clear close/dismiss route |
| One window per typed record | WindowGroup for a lightweight Hashable/Codable value | Pass an ID or small presentation value; resolve current domain state inside |
| Document editor | DocumentGroup or the documented document route | The document system owns file/window behavior; do not recreate it with a generic group |
| Spatial 2D or volumetric content | WindowGroup or the target-specific spatial scene | Choose window, volume, or immersive space for the task, not for visual novelty |
| Glanceable watch task | watchOS target and watchOS scene model | Keep the task shallow and target-specific; do not infer watch behavior from iPad windows |

A normal iPhone app can have a single visible surface while still using the
scene system. A multiwindow claim is target-specific and requires configuration,
runtime, and user-task evidence.

## 3. WindowGroup and Window contract

Use a WindowGroup when the user benefits from multiple instances of the same
composition. Use a Window when the utility should be single-instance.

~~~swift
@main
struct ProjectApp: App {
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

The exact scene signatures and availability are SDK-sensitive. Compile the
smallest target before building a larger scene graph.

For typed windows:

- make the presentation type lightweight;
- conform to the protocols required by the current SDK, normally Hashable and
  Codable for a typed WindowGroup;
- pass a stable ID rather than a live model object;
- resolve current state after the scene is created;
- handle a deleted, unauthorized, or stale ID with a visible fallback;
- do not use a generated AI candidate or URL string as a domain commit.

The system may bring an existing window to the front when its typed
presentation value is already present. That is a presentation behavior, not a
deduplication guarantee for network work or model generation.

## 4. Open windows through typed intent

A view can request a scene through the openWindow environment action. The
feature should own the intent and domain validation around the call.

~~~swift
struct OpenProjectButton: View {
    let projectID: Project.ID
    @Environment(\.openWindow) private var openWindow

    var body: some View {
        Button("Open project") {
            openWindow(value: projectID)
        }
    }
}
~~~

Before opening:

1. confirm that the ID is current enough to present;
2. confirm account and authorization scope;
3. pass only the minimum presentation value;
4. let the destination resolve the current record;
5. show unavailable/deleted/offline states inside the destination;
6. record the scene request and resulting window behavior in the proof artifact.

For an auxiliary scene:

~~~swift
struct OpenConnectionDoctorButton: View {
    @Environment(\.openWindow) private var openWindow

    var body: some View {
        Button("Open connection doctor") {
            openWindow(id: "connection-doctor")
        }
    }
}
~~~

Use unique identifiers across Window and WindowGroup declarations. If the
platform does not support multiple windows, the action must have a graceful
single-surface or in-place fallback.

## 5. External events choose scenes before views handle them

URLs, user activities, notifications, widgets, App Intents, and Handoff can
arrive when the app is cold, warm, backgrounded, or already showing multiple
scenes. Normalize them once and route them through a typed request.

SwiftUI has two related boundaries:

- a scene-level handlesExternalEvents(matching:) modifier helps choose a new
  scene when no currently open scene is the right destination;
- a view-level handlesExternalEvents(preferring:allowing:) modifier expresses
  which already-open scene can or prefers to handle an event;
- onOpenURL and onContinueUserActivity process the event after scene selection.

Do not confuse scene selection with domain action. A URL may request that a
project be shown; it does not prove that the project still exists or that the
person is authorized to edit it.

~~~swift
enum SceneRequest: Hashable, Sendable {
    case project(id: Project.ID)
    case compose(source: String)
    case connectionDoctor
}

struct SceneRequestNormalizer {
    func request(for url: URL) -> SceneRequest? {
        guard url.scheme == "bishop-projects" else { return nil }

        if url.host == "project",
           let id = Project.ID(rawValue: url.lastPathComponent) {
            return .project(id: id)
        }

        if url.host == "compose" {
            return .compose(source: "external-url")
        }

        return nil
    }
}
~~~

The application or scene coordinator should parse, validate, and record the
request. The destination view should render the request's result and report
user intent; it should not accept arbitrary URL text as a trusted command.

Test every claimed external route through:

- cold launch;
- warm single-scene delivery;
- warm multi-scene delivery;
- a terminated process;
- duplicate delivery;
- stale or unauthorized IDs;
- malformed URLs and unsupported activities;
- the source app or system surface that actually delivers the event.

## 6. Scene phase and scene-scoped work

scenePhase is an operational signal. Its meaning depends on where it is read.
An app-level observer can reflect an aggregate across scenes; a scene-level
observer can express the lifecycle of the current scene.

Use phase changes to bound work:

- active: allow user-facing work and focused model interaction;
- inactive: preserve focus/draft state and avoid assuming the user can finish;
- background: cancel or checkpoint work according to the feature contract;
- disconnected or destroyed scene: stop accepting callbacks and release
  scene-owned resources.

~~~swift
struct ProjectWorkspace: View {
    @Environment(\.scenePhase) private var scenePhase
    @State private var refreshTask: Task<Void, Never>?

    var body: some View {
        ProjectContent()
            .onChange(of: scenePhase) { _, phase in
                switch phase {
                case .active:
                    startBoundedRefresh()
                case .inactive, .background:
                    refreshTask?.cancel()
                    refreshTask = nil
                @unknown default:
                    refreshTask?.cancel()
                    refreshTask = nil
                }
            }
            .onDisappear {
                refreshTask?.cancel()
                refreshTask = nil
            }
    }

    private func startBoundedRefresh() {
        refreshTask?.cancel()
        refreshTask = Task {
            // Replace with an actor-owned, cancellable feature operation.
        }
    }
}
~~~

A task started by one scene must not silently mutate another scene's draft.
Use actor isolation, source revisions, and explicit feature ownership.

## 7. Restoration is layered

SceneStorage is suitable for small, scene-scoped values that SwiftUI can
restore. It is not a durable database, sync log, secret store, or large AI
context.

| Need | Appropriate boundary |
| --- | --- |
| Selected tab or small filter | State or SceneStorage |
| Current lightweight project ID | SceneStorage or a typed activity payload |
| Navigation path | Codable route plus a deliberate restoration policy |
| Draft text | Feature-owned draft model, optionally restored from scene-scoped identity |
| Durable project record | SwiftData/Core Data/CloudKit or another explicit store |
| AI session/context | Model-owned session policy; do not serialize sensitive context into SceneStorage |
| Cross-device continuity | Handoff, CloudKit, or another explicit transfer/sync contract |
| Secret/token/credential | Keychain or protected credential boundary |

~~~swift
struct ProjectWorkspace: View {
    @SceneStorage("selectedProjectID") private var selectedProjectID: String?

    var body: some View {
        ProjectList(selection: $selectedProjectID)
    }
}
~~~

On relaunch, restoration data is only a hint. Revalidate account, schema,
authorization, record existence, and current revision before presenting it.
A restored selection that no longer exists should become an empty or repair
state, not a fabricated record.

## 8. iPadOS windows, resize, and Stage Manager

iPadOS window behavior is a user-controlled multitasking surface. Support
fluid widths and heights, split view, Stage Manager, keyboard, pointer, and
rotation when the target claims them.

Design rules:

- do not open auxiliary windows for every tap;
- use a new window when preserving context or parallel work has a clear benefit;
- let window size drive layout through environment and measured available space;
- keep the primary task and its most important action reachable at narrow widths;
- do not use a fixed iPhone frame as the iPad workspace;
- preserve draft, focus, selection, and unsaved changes during resize;
- record the actual app configuration that enables multiple scenes;
- verify same-app windows independently rather than assuming a split-screen
  screenshot proves window identity.

Apple's HIG describes full-screen and windowed iPadOS behaviors and expects
windows to adapt fluidly. The app's feature architecture must tolerate the
system creating, resizing, backgrounding, and restoring scene instances.

## 9. Mac Catalyst composition

Mac Catalyst is a Mac target with its own window, menu, toolbar, pointer,
keyboard, and resize expectations. It is not proof that an iPad layout is a
finished Mac experience.

For a Catalyst route:

- choose and verify the intended Mac idiom;
- use a resizable window and test narrow, wide, and tall sizes;
- expose primary actions through the menu/command hierarchy where appropriate;
- support pointer hover and keyboard navigation without removing touch routes
  from shared iPad composition;
- check title bar, toolbar, table/list density, selection, tooltips, and
  destructive-action confirmation;
- keep Catalyst-only code at the target boundary;
- verify the actual Catalyst target on a Mac, not only a simulated iPad.

## 10. visionOS and watchOS are different scene products

visionOS uses windows, volumes, and immersive spaces with spatial input and
comfort constraints. A default window can already carry a system-provided
glass treatment. Avoid rebuilding a flat iPhone-style window frame.

Choose:

- a default window for a familiar 2D task;
- a volume for bounded 3D content;
- an immersive space only when the task benefits from the space and the user
  can understand how to enter and leave it.

Test scale, depth, indirect/direct input, focus, readability, comfort, and
dismissal on the target route.

watchOS is a glanceable companion surface. It has no reason to inherit a
multiwindow iPad architecture. Keep the watch target focused on one short
task, Digital Crown/touch input, notification/complication context, Always On
behavior, and paired/offline state. Share typed domain projections, not a
phone-sized scene hierarchy.

## 11. Liquid Glass at the scene boundary

Use system scene and window behavior first. Apple's platforms can apply
platform-specific material, controls, window chrome, and presentation. A
custom glass card inside a window is not the same thing as recreating the
window.

| Boundary | Native-first choice | Avoid |
| --- | --- | --- |
| iPhone/iPad content | System controls, semantic materials, clear hierarchy, bounded custom glass | A glass layer behind every row or a custom fake window frame |
| iPad auxiliary window | User-recognizable task window with content that adapts to resize | Opening a window only to showcase a capsule |
| Catalyst | Mac window/toolbar/menu conventions, with restrained content materials | Phone-shaped floating glass controls as the Mac shell |
| visionOS | System window/volume/immersive style and spatial comfort | Replacing system window chrome or forcing flat iOS glass geometry |
| watchOS | Compact system controls and glanceable hierarchy | Transplanting a large translucent surface system |

Liquid Glass is a surface treatment and interaction contract, not a license to
hide ownership, focus, accessibility, or dismissal. Keep the AI state, content
hierarchy, and system actions readable with increased contrast and reduced
transparency settings.

## 12. On-device AI in a scene/window system

A model session may be expensive, unavailable, cancellable, language-sensitive,
or constrained by the selected device. A new window should not accidentally
start a duplicate live generation because a view initializer ran again.

Give AI work:

- a feature-owned adapter and actor/task owner;
- a source ID and source revision;
- a scene/window request ID;
- a capability/availability state;
- a cancellation and checkpoint policy;
- a typed candidate with provenance and review status;
- an explicit commit use case separate from presentation.

Two windows may show the same source with different review state. Two scene
instances must not claim that one candidate is committed merely because it is
visible in both. If the person opens a new AI task window, make that a
deliberate task identity and explain which source revision it reviews.

Preview fixtures should cover:

- model unavailable;
- loading/prewarming;
- partial output;
- stale source revision;
- refusal or validation failure;
- ready but uncommitted candidate;
- committed domain result after explicit confirmation.

## 13. Accessibility and alternate input per window

Accessibility and input state are scene-visible product behavior:

- give each primary or auxiliary surface a clear title and dismiss path;
- keep focus scoped to the active scene/window;
- test VoiceOver reading order and actions after a new window opens;
- test keyboard and pointer routes on iPad and Catalyst;
- test Dynamic Type and localization at narrow and wide window sizes;
- test Voice Control, Switch Control, Full Keyboard Access, and reduced effects
  where supported;
- ensure AI status, unavailable state, and review action are semantic;
- do not make a hover effect or window chrome the only discoverable action.

A screenshot of two windows is not accessibility evidence. Use task completion
with the actual target and input configuration.

## 14. Proof contract

For every scene/window feature record:

- target, deployment target, SDK, build configuration, and OS build;
- scene declaration and identifier/value route;
- domain identity and source revision;
- app configuration for multiple scenes;
- external event source and normalized request;
- cold/warm/background/terminated state;
- window size, orientation, split/Stage Manager state, and input mode;
- appearance, contrast, Dynamic Type, locale, layout direction, motion, and
  transparency settings;
- AI model/capability state and cancellation result;
- accessibility task result;
- physical/Catalyst/visionOS/watchOS artifact and release build identity.

A preview can prove a named composition at a fixture. It cannot prove external
delivery, multiwindow system behavior, model readiness, physical spatial
comfort, or release packaging.

## Common failure modes

- Treating scene identity as a project/document ID.
- Passing a full model or generated candidate through WindowGroup presentation.
- Opening a new window for every user action.
- Parsing URLs inside a destination view and skipping account/revision checks.
- Using scenePhase as proof that durable persistence completed.
- Assuming WindowGroup creates multiple iPad windows without configuration and
  runtime evidence.
- Claiming Mac Catalyst behavior from an iPad simulator.
- Applying a custom glass frame to a visionOS system window.
- Starting model work in a view initializer or failing to cancel on scene loss.
- Showing an AI candidate as committed because two windows render the same text.
- Calling a watchOS projection a shared window instead of a target-specific task.

## Sources

- [Scenes](https://developer.apple.com/documentation/swiftui/scenes)
- [Windows](https://developer.apple.com/documentation/swiftui/windows)
- [WindowGroup](https://developer.apple.com/documentation/swiftui/windowgroup)
- [Window](https://developer.apple.com/documentation/swiftui/window)
- [openWindow](https://developer.apple.com/documentation/swiftui/environmentvalues/openwindow)
- [Presenting windows and spaces](https://developer.apple.com/documentation/visionos/presenting-windows-and-spaces)
- [handlesExternalEvents(matching:)](https://developer.apple.com/documentation/swiftui/scene/handlesexternalevents%28matching%3A%29)
- [System events](https://developer.apple.com/documentation/swiftui/system-events)
- [ScenePhase](https://developer.apple.com/documentation/swiftui/scenephase)
- [SceneStorage](https://developer.apple.com/documentation/swiftui/scenestorage)
- [WindowGroup](https://developer.apple.com/documentation/swiftui/windowgroup)
- [UIApplicationSupportsMultipleScenes](https://developer.apple.com/documentation/BundleResources/Information-Property-List/UIApplicationSceneManifest/UIApplicationSupportsMultipleScenes)
- [UIScene](https://developer.apple.com/documentation/uikit/uiscene)
- [Mac Catalyst](https://developer.apple.com/documentation/uikit/mac-catalyst)
- [Windows HIG](https://developer.apple.com/design/human-interface-guidelines/windows)
- [Multitasking HIG](https://developer.apple.com/design/human-interface-guidelines/multitasking)
- [Layout HIG](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Mac Catalyst HIG](https://developer.apple.com/design/human-interface-guidelines/mac-catalyst)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
