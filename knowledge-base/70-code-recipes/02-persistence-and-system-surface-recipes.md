# Persistence and System Surface Recipes

Use these seams with the [capability-first Apple SDK atlas](../40-framework-routes/10-capability-first-apple-sdk-atlas.md), [cross-framework feature lifecycle](../41-framework-deep-dives/06-cross-framework-feature-lifecycle.md), and [system-surface/extension composition guide](../43-system-framework-deep-dives/06-system-surface-and-extension-composition.md).

## SwiftData shell

```swift
import SwiftData
import SwiftUI

@Model
final class Note {
    var title: String
    var createdAt: Date

    init(title: String, createdAt: Date = .now) {
        self.title = title
        self.createdAt = createdAt
    }
}

@main
struct NotesApp: App {
    var body: some Scene {
        WindowGroup { NoteList() }
            .modelContainer(for: Note.self)
    }
}

struct NoteList: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \Note.createdAt, order: .reverse)
    private var notes: [Note]

    var body: some View {
        List(notes) { note in
            Text(note.title)
        }
        .toolbar {
            Button("Add") {
                modelContext.insert(Note(title: "Draft"))
            }
        }
    }
}
```

Attach the container explicitly in the app or preview. Decide when saves happen, how errors surface, and whether the model later syncs through CloudKit.

## App Intent boundary

```swift
import AppIntents

struct AddQuickNote: AppIntent {
    static var title: LocalizedStringResource = "Add quick note"

    @Parameter(title: "Text")
    var text: String

    func perform() async throws -> some IntentResult {
        try await NotesActions.add(text: text)
        return .result()
    }
}
```

The shared `NotesActions` service must perform validation, persistence, authorization, and error mapping. The intent is a system entry point, not a bypass around the app’s domain rules.

## Interactive widget boundary

An interactive widget or Live Activity uses an App Intent for the action. The extension process cannot assume the main app is running or that arbitrary view bindings exist. Persist the action before returning from `perform()` and make stale/error state renderable.

```swift
Button(intent: AddQuickNote(text: "From widget")) {
    Label("Add", systemImage: "plus")
}
```

The exact initializer and target membership are SDK-sensitive; verify the WidgetKit/App Intents documentation in Xcode.

## Compile/device gate

- Compile SwiftData with a real model container and preview in-memory fixtures.
- Test relaunch, migration, save errors, account/sync state, and deletion.
- Add App Intents/widget extension target membership and test with the app terminated.
- Test localization, entity privacy, unavailable data, and action failure on the actual system surface.

## Sources

- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [ModelContext](https://developer.apple.com/documentation/swiftdata/modelcontext)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Widgets, Live Activities, and Controls](https://developer.apple.com/documentation/appintents/widgets-live-activities-and-controls)
