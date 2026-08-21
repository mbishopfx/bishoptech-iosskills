# SwiftUI controls, commands, and adaptable-tabs recipes

## How to use these recipes

These are compile-oriented route sketches for native SwiftUI work. They
illustrate the relationship between semantics, styles, forms, commands,
search, tabs, Liquid Glass, and on-device AI review.

Before copying a recipe:

1. Set the app target, SDK, deployment target, and supported device families.
2. Confirm the current declaration and availability in Xcode.
3. Add localization, capabilities, privacy resources, and system configuration
   required by the feature.
4. Compile the smallest slice.
5. Run the fixture and physical/system proof appropriate to the claim.

The snippets do not prove physical VoiceOver, Voice Control, Switch Control,
keyboard, tab customization, system delivery, model availability, persistence,
or release behavior.

Related pages:

- [SwiftUI controls, forms, commands, and adaptable tabs](../42-framework-deep-dives/81-swiftui-controls-forms-commands-and-tabs.md)
- [Controls, forms, commands, and adaptable-tab design](../21-design-deep-dives/109-controls-forms-commands-and-tab-design.md)
- [SwiftUI controls, commands, and adaptable-tabs route](../50-capability-recipes/112-swiftui-controls-commands-and-tabs-route.md)
- [SwiftUI controls, commands, and adaptable-tabs proof matrix](../60-verification/106-swiftui-controls-commands-and-tabs-proof-matrix.md)

## Recipe 1: a styled semantic Button

Use ButtonStyle for visual treatment while retaining Button’s standard
interaction contract.

~~~swift
import SwiftUI

struct NativeActionStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .background(.thinMaterial, in: Capsule())
            .opacity(configuration.isPressed ? 0.72 : 1)
            .scaleEffect(configuration.isPressed ? 0.98 : 1)
            .contentShape(Capsule())
    }
}

struct SaveButton: View {
    let action: () -> Void

    var body: some View {
        Button("Save changes", systemImage: "checkmark", action: action)
            .buttonStyle(NativeActionStyle())
            .accessibilityHint("Commits the validated draft")
    }
}
~~~

The style is not the place to save data or start a second gesture. Test
pressed, disabled, cancel, destructive, Dynamic Type, VoiceOver, Voice
Control, and reduced-effects states.

## Recipe 2: a stateful ToggleStyle

Use a Toggle for a Boolean. A custom style can change presentation while
keeping the binding and state semantics.

~~~swift
struct CapsuleToggleStyle: ToggleStyle {
    func makeBody(configuration: Configuration) -> some View {
        Button {
            configuration.isOn.toggle()
        } label: {
            HStack {
                configuration.label
                Spacer()
                Image(systemName: configuration.isOn
                      ? "checkmark.circle.fill"
                      : "circle")
                    .symbolRenderingMode(.hierarchical)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(
                configuration.isOn
                    ? Color.accentColor.opacity(0.18)
                    : Color.secondary.opacity(0.10),
                in: Capsule()
            )
        }
        .buttonStyle(.plain)
    }
}

struct PreferenceRow: View {
    @State private var enabled = false

    var body: some View {
        Toggle("Use local suggestions", isOn: $enabled)
            .toggleStyle(CapsuleToggleStyle())
    }
}
~~~

Confirm the generated accessibility tree in the selected SDK. The visual
state should not be the only state cue; the label and Boolean value must
remain understandable. If the custom style creates nested or duplicate
semantics, prefer a built-in style or repair the semantic boundary.

## Recipe 3: adaptive Label and ControlGroup

Let the surrounding system choose a useful title/icon representation.

~~~swift
enum ViewMode: Hashable {
    case list
    case grid
}

struct ViewModeControls: View {
    @Binding var mode: ViewMode

    var body: some View {
        ControlGroup("View mode") {
            Button {
                mode = .list
            } label: {
                Label("List", systemImage: "list.bullet")
            }

            Button {
                mode = .grid
            } label: {
                Label("Grid", systemImage: "square.grid.2x2")
            }
        }
        .labelStyle(.titleAndIcon)
    }
}
~~~

In a toolbar or overflow menu, inspect whether the group label and child
labels still make sense. Use a Toggle or Picker if the behavior is actually a
persistent choice rather than two independent actions.

## Recipe 4: draft form with validation and focus

Keep a draft separate from the committed model. Focus is a presentation route;
validation and save authority belong to the feature/domain boundary.

~~~swift
struct NoteDraft: Equatable {
    var title = ""
    var body = ""
}

struct NoteEditor: View {
    enum Field: Hashable {
        case title
        case body
    }

    @State private var draft: NoteDraft
    @State private var error: String?
    @State private var isSaving = false
    @FocusState private var focusedField: Field?

    let commit: (NoteDraft) async throws -> Void

    init(
        draft: NoteDraft = NoteDraft(),
        commit: @escaping (NoteDraft) async throws -> Void
    ) {
        _draft = State(initialValue: draft)
        self.commit = commit
    }

    var body: some View {
        Form {
            Section("Note") {
                TextField("Title", text: $draft.title)
                    .focused($focusedField, equals: .title)
                    .submitLabel(.next)
                    .onSubmit { focusedField = .body }

                TextEditor(text: $draft.body)
                    .focused($focusedField, equals: .body)
                    .frame(minHeight: 160)
            }

            if let error {
                Text(error)
                    .foregroundStyle(.red)
                    .accessibilityLabel("Note error")
                    .accessibilityValue(error)
            }
        }
        .navigationTitle("Edit note")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Save", systemImage: "checkmark") {
                    Task { await save() }
                }
                .disabled(isSaving)
            }
        }
    }

    private func save() async {
        guard !draft.title.trimmingCharacters(in: .whitespacesAndNewlines)
            .isEmpty else {
            error = "Enter a title."
            focusedField = .title
            return
        }

        isSaving = true
        defer { isSaving = false }

        do {
            try await commit(draft)
            error = nil
        } catch {
            self.error = "Could not save. Your draft is still here."
        }
    }
}
~~~

In a real app, inject a domain command that checks authorization and source
revision before persistence. Add AccessibilityFocusState separately when the
screen needs a deliberate VoiceOver focus transition; do not reuse
FocusState for both systems.

## Recipe 5: Menu and destructive role

Keep primary action visible and place secondary/destructive actions in a
predictable menu.

~~~swift
struct RecordToolbarMenu: View {
    let duplicate: () -> Void
    let export: () -> Void
    let delete: () -> Void

    var body: some View {
        Menu {
            Button("Duplicate", systemImage: "plus.square.on.square",
                   action: duplicate)
            Button("Export", systemImage: "square.and.arrow.up",
                   action: export)
            Divider()
            Button("Delete", systemImage: "trash", role: .destructive,
                   action: delete)
        } label: {
            Label("More actions", systemImage: "ellipsis.circle")
        }
        .accessibilityHint("Shows secondary actions for this record")
    }
}
~~~

The delete closure should present confirmation or invoke a domain command
that owns confirmation policy. The menu’s presence is not authorization.

## Recipe 6: focused command context

Use FocusedValue to give a scene command the current editor context without
making every view know about every command.

~~~swift
import SwiftUI

struct EditorCommandContext {
    let suggest: () -> Void
    let canSuggest: Bool
}

private struct EditorCommandContextKey: FocusedValueKey {
    typealias Value = EditorCommandContext
}

extension FocusedValues {
    var editorCommandContext: EditorCommandContext? {
        get { self[EditorCommandContextKey.self] }
        set { self[EditorCommandContextKey.self] = newValue }
    }
}

struct EditorCommands: Commands {
    @FocusedValue(\.editorCommandContext)
    private var context

    var body: some Commands {
        CommandMenu("Review") {
            Button("Suggest summary") {
                context?.suggest()
            }
            .disabled(!(context?.canSuggest ?? false))
            .keyboardShortcut("s", modifiers: [.command, .shift])
        }
    }
}

struct ReviewEditor: View {
    let suggest: () -> Void
    let canSuggest: Bool

    var body: some View {
        TextEditor(text: .constant("Reviewable text"))
            .focusedValue(
                \.editorCommandContext,
                EditorCommandContext(
                    suggest: suggest,
                    canSuggest: canSuggest
                )
            )
    }
}
~~~

Register the Commands value on the App/Scene. Compile the focused-value
property-wrapper shape in the selected SDK and test two documents plus no
focused document. The command must never guess which record to mutate.

## Recipe 7: semantic toolbar and title menu

Use intent-based placement. Use the customizable toolbar overload only when
the product wants the person to arrange eligible secondary actions.

~~~swift
struct EditorScreen: View {
    let save: () -> Void
    let share: () -> Void
    let insert: () -> Void

    var body: some View {
        TextEditor(text: .constant("Draft"))
            .navigationTitle("Editor")
            .toolbarRole(.editor)
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button("Save", systemImage: "checkmark", action: save)
                }

                ToolbarItem(placement: .secondaryAction) {
                    Menu {
                        Button("Insert", systemImage: "plus", action: insert)
                        Button("Share", systemImage: "square.and.arrow.up",
                               action: share)
                    } label: {
                        Label("More", systemImage: "ellipsis.circle")
                    }
                }

                ToolbarTitleMenu {
                    Button("Share", systemImage: "square.and.arrow.up",
                           action: share)
                }
            }
    }
}
~~~

For a customizable toolbar, use the selected SDK’s toolbar(id:content:)
declaration and stable ToolbarItem IDs. Test the default, overflow, user
customized, and reset states. Do not infer that a toolbar screenshot proves
the same item placement on every platform.

## Recipe 8: searchable query, scope, and suggestions

Bind search to feature state and derive results. Keep the query and selected
scope separate from the source records.

~~~swift
enum NoteScope: String, CaseIterable, Hashable, Identifiable {
    case all
    case drafts
    case saved

    var id: Self { self }
    var title: String { rawValue.capitalized }
}

struct NoteSearchView: View {
    let notes: [Note]
    @State private var query = ""
    @State private var scope: NoteScope = .all
    @State private var suggestions = ["project", "draft", "meeting"]

    private var results: [Note] {
        let scoped = notes.filter { note in
            switch scope {
            case .all: true
            case .drafts: note.isDraft
            case .saved: !note.isDraft
            }
        }

        guard !query.isEmpty else { return scoped }
        return scoped.filter {
            $0.title.localizedCaseInsensitiveContains(query)
        }
    }

    var body: some View {
        List(results) { note in
            NavigationLink(value: note.id) {
                Label(note.title, systemImage: note.isDraft
                      ? "pencil" : "note.text")
            }
        }
        .searchable(text: $query, placement: .automatic,
                    prompt: "Search notes")
        .searchScopes($scope) {
            ForEach(NoteScope.allCases) { value in
                Text(value.title).tag(value)
            }
        }
        .searchSuggestions {
            ForEach(suggestions, id: \.self) { suggestion in
                Text(suggestion)
                    .searchCompletion(suggestion)
            }
        }
    }
}

struct Note: Identifiable {
    let id: UUID
    let title: String
    let isDraft: Bool
}
~~~

For async or AI-assisted search, add request identity/cancellation and show
the underlying source record for generated summaries. Test toolbar/sidebar/tab
placement separately.

## Recipe 9: adaptable tabs with customization

This shape uses the current Tab/TabSection and sidebarAdaptable APIs. Compile
it in a target whose selected SDK provides those declarations.

~~~swift
enum AppTab: Hashable {
    case home
    case review
    case library
    case settings
    case category(String)
}

struct AppTabs: View {
    @State private var selection: AppTab = .home
    @AppStorage("tab-customization")
    private var customization: TabViewCustomization
    @State private var showStatus = false

    var body: some View {
        TabView(selection: $selection) {
            Tab("Home", systemImage: "house", value: AppTab.home) {
                HomeView()
            }
            .customizationID("app.home")
            .customizationBehavior(.disabled, for: .sidebar, .tabBar)

            Tab("Review", systemImage: "checkmark.circle",
                value: AppTab.review) {
                ReviewView()
            }
            .customizationID("app.review")

            TabSection("Library") {
                Tab("Recent", systemImage: "clock",
                    value: AppTab.library) {
                    LibraryView()
                }
                .customizationID("app.library.recent")

                Tab("Saved", systemImage: "bookmark",
                    value: AppTab.category("saved")) {
                    SavedView()
                }
                .customizationID("app.library.saved")
            }
            .customizationID("app.library.section")

            Tab("Settings", systemImage: "gear",
                value: AppTab.settings) {
                SettingsView()
            }
            .customizationID("app.settings")
        }
        .tabViewStyle(.sidebarAdaptable)
        .tabViewCustomization($customization)
        .tabViewBottomAccessory(isEnabled: showStatus) {
            TabStatusAccessory()
        }
    }
}
~~~

The customization binding persists visibility/order preferences. Test default
visibility, reordering, hiding, reset/migration, relaunch, VoiceOver, compact
iPhone, regular iPad, and deep links to hidden tabs. Do not assume that a
customization ID is a user-facing label.

## Recipe 10: placement-aware bottom accessory

The bottom accessory has expanded and inline placements. The environment is
optional because placement can be undefined outside the relevant tab view.

~~~swift
struct TabStatusAccessory: View {
    @Environment(\.tabViewBottomAccessoryPlacement)
    private var placement

    var body: some View {
        switch placement {
        case .some(.inline):
            Button("Resume review", systemImage: "arrow.clockwise") {
                resume()
            }
            .labelStyle(.iconOnly)

        case .some(.expanded):
            HStack {
                Label("Review ready", systemImage: "sparkles")
                Spacer()
                Button("Resume", action: resume)
            }
            .padding(.horizontal)

        case .none:
            EmptyView()
        }
    }

    private func resume() {
        // Resolve the current review ID through the domain authority.
    }
}
~~~

Use concise labels in the inline representation. Keep the same semantic
action in the expanded and inline forms, and provide a screen/toolbar route
when the accessory is disabled.

## Recipe 11: AI action state on a native control surface

Model AI status explicitly. The button should invoke an app-owned command,
not write generated text directly into committed state.

~~~swift
enum ProposalState: Equatable {
    case unavailable(reason: String)
    case checking
    case generating
    case proposal(id: UUID)
    case applying
    case saved
    case stale
    case failed(message: String)
}

struct ProposalActions: View {
    let state: ProposalState
    let suggest: () -> Void
    let cancel: () -> Void
    let apply: () -> Void
    let reject: () -> Void

    var body: some View {
        ControlGroup("Review actions") {
            switch state {
            case .unavailable(let reason):
                Button("Manual edit", systemImage: "pencil",
                       action: suggest)
                    .accessibilityValue(reason)

            case .checking:
                ProgressView("Checking availability")

            case .generating:
                Button("Cancel", systemImage: "xmark", action: cancel)

            case .proposal:
                Button("Apply", systemImage: "checkmark", action: apply)
                Menu("More") {
                    Button("Reject", role: .destructive, action: reject)
                    Button("Keep editing", systemImage: "pencil") {
                        // Return to the editable candidate.
                    }
                }

            case .applying:
                ProgressView("Applying proposal")

            case .saved:
                Label("Saved", systemImage: "checkmark.circle")

            case .stale:
                Button("Review latest", systemImage: "arrow.clockwise",
                       action: suggest)

            case .failed(let message):
                Button("Retry", systemImage: "arrow.clockwise",
                       action: suggest)
                    .accessibilityValue(message)
            }
        }
    }
}
~~~

The suggest action should check capability/language assets, capture source
revision, start a cancellable request, and publish a typed candidate. The
apply action should revalidate the current revision and authorization before
committing. Keep generated text and error messages localized and privacy-safe.

## Recipe 12: Liquid Glass shell with reduced-effects policy

Keep semantic actions inside the shell. The visual effect should be optional
and should not own the state.

~~~swift
struct GlassCommandCluster: View {
    @Environment(\.accessibilityReduceTransparency)
    private var reduceTransparency
    @Environment(\.accessibilityReduceMotion)
    private var reduceMotion

    let save: () -> Void
    let more: () -> Void

    var body: some View {
        HStack(spacing: 10) {
            Button("Save", systemImage: "checkmark", action: save)
            Button("More", systemImage: "ellipsis", action: more)
        }
        .padding(8)
        .background(
            reduceTransparency
                ? AnyShapeStyle(.regularMaterial)
                : AnyShapeStyle(.clear),
            in: Capsule()
        )
        .glassEffect(.regular.interactive(), in: .capsule)
        .transaction { transaction in
            if reduceMotion {
                transaction.animation = nil
            }
        }
    }
}
~~~

Confirm the exact Liquid Glass overloads and availability in the selected
SDK. If a reduced-transparency branch and glassEffect both apply in the target
SDK, inspect the result and choose one clear visual contract rather than
stacking competing materials. Test the accessibility tree for decorative
duplicates and use regular/opaque content treatment when text density requires
it.

## Recipe 13: lightweight proof harness

Give every route a fixture and evidence record rather than asserting success
from a callback.

~~~swift
struct SurfaceProofCase: Identifiable {
    let id: String
    let title: String
    let setup: String
    let expected: String
}

let controlsProof = [
    SurfaceProofCase(
        id: "large-text",
        title: "Large text",
        setup: "Largest supported Dynamic Type and long localized labels",
        expected: "Primary action and errors remain visible and readable"
    ),
    SurfaceProofCase(
        id: "voiceover-form",
        title: "VoiceOver form",
        setup: "Physical device with VoiceOver and invalid draft",
        expected: "First actionable error and recovery route are reachable"
    ),
    SurfaceProofCase(
        id: "tab-customization",
        title: "Tab customization",
        setup: "iPad regular window, hide/reorder/relaunch",
        expected: "Customization persists and essential tab remains available"
    ),
    SurfaceProofCase(
        id: "accessory-inline",
        title: "Inline accessory",
        setup: "Collapsed iPhone tab bar with status accessory",
        expected: "Accessory action remains concise, labelled, and reachable"
    )
]
~~~

Store actual build/device/result artifacts outside the code recipe. A fixture
list is a proof plan, not proof.

## Sources

- [Button](https://developer.apple.com/documentation/swiftui/button)
- [ButtonStyle](https://developer.apple.com/documentation/swiftui/buttonstyle)
- [ToggleStyle](https://developer.apple.com/documentation/swiftui/togglestyle)
- [LabelStyle](https://developer.apple.com/documentation/swiftui/labelstyle)
- [ControlGroup](https://developer.apple.com/documentation/swiftui/controlgroup)
- [Form](https://developer.apple.com/documentation/swiftui/form)
- [TextField](https://developer.apple.com/documentation/swiftui/textfield)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [Menus and commands](https://developer.apple.com/documentation/swiftui/menus-and-commands)
- [Commands](https://developer.apple.com/documentation/swiftui/commands)
- [FocusedValues](https://developer.apple.com/documentation/swiftui/focusedvalues)
- [KeyboardShortcut](https://developer.apple.com/documentation/swiftui/keyboardshortcut)
- [ToolbarItemPlacement](https://developer.apple.com/documentation/swiftui/toolbaritemplacement)
- [ToolbarRole](https://developer.apple.com/documentation/swiftui/toolbarrole)
- [ToolbarTitleMenu](https://developer.apple.com/documentation/swiftui/toolbartitlemenu)
- [toolbar(id:content:)](https://developer.apple.com/documentation/swiftui/view/toolbar%28id%3Acontent%3A%29)
- [Adding a search interface to your app](https://developer.apple.com/documentation/swiftui/adding-a-search-interface-to-your-app)
- [Search](https://developer.apple.com/documentation/swiftui/search)
- [Performing a search operation](https://developer.apple.com/documentation/swiftui/performing-a-search-operation)
- [TabView](https://developer.apple.com/documentation/swiftui/tabview)
- [TabSection](https://developer.apple.com/documentation/swiftui/tabsection)
- [TabViewStyle](https://developer.apple.com/documentation/swiftui/tabviewstyle)
- [SidebarAdaptableTabViewStyle](https://developer.apple.com/documentation/swiftui/sidebaradaptabletabviewstyle)
- [TabViewCustomization](https://developer.apple.com/documentation/swiftui/tabviewcustomization)
- [tabViewCustomization(_:)](https://developer.apple.com/documentation/swiftui/view/tabviewcustomization%28_%3A%29)
- [tabViewBottomAccessory(content:)](https://developer.apple.com/documentation/swiftui/view/tabviewbottomaccessory%28content%3A%29)
- [tabViewBottomAccessory(isEnabled:content:)](https://developer.apple.com/documentation/swiftui/view/tabviewbottomaccessory%28isenabled%3Acontent%3A%29)
- [TabViewBottomAccessoryPlacement](https://developer.apple.com/documentation/swiftui/tabviewbottomaccessoryplacement)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Human Interface Guidelines: Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- [Human Interface Guidelines: Menus](https://developer.apple.com/design/human-interface-guidelines/menus)
- [Human Interface Guidelines: Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)
- [Human Interface Guidelines: Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
