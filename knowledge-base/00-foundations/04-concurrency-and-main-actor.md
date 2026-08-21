# Concurrency and the Main Actor

## The practical model

Swift concurrency gives asynchronous work explicit suspension points and uses actors/isolation to protect shared mutable state. The main actor is the UI isolation domain. Keep UI state and view-facing observable models main-actor isolated when they mutate presentation state; move blocking parsing, media processing, network work, and model inference behind async services or actors as appropriate.

## Choose the right tool

- `async`/`await`: a function can suspend while waiting for work.
- `Task`: start async work from a synchronous UI event or lifecycle callback.
- `async let`: run a small, fixed set of independent operations concurrently.
- task groups: dynamically create and collect child tasks.
- actor: serialize access to mutable state that may be touched by multiple tasks.
- `@MainActor`: make UI-facing code run in the UI isolation domain.
- `Sendable`: communicate values safely across concurrency domains.

## UI rule

Do not update a SwiftUI view’s state from an arbitrary callback without considering isolation and cancellation. Prefer a task tied to view lifetime, an observable model that exposes loading/success/failure state, and a service that can be cancelled when the view disappears.

## Error and cancellation path

Every async feature should define:

- loading state;
- success value;
- expected unavailable state;
- user-cancelled state;
- retry behavior;
- unexpected error presentation;
- cleanup when the task is cancelled.

This is especially important for camera streams, speech, translation downloads, model sessions, and network-backed App Intents.

## Small pattern

```swift
@MainActor
@Observable
final class SearchModel {
    var state: State = .idle
    private let service: SearchService

    func refresh() async {
        state = .loading
        do {
            state = .loaded(try await service.search())
        } catch is CancellationError {
            state = .idle
        } catch {
            state = .failed(error.localizedDescription)
        }
    }
}
```

The pattern is illustrative, not a universal architecture. The important parts are explicit state, async boundaries, main-actor UI mutation, and cancellation.

## Sources

- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [A Swift Tour: Concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/guidedtour/)
- [Observation](https://developer.apple.com/documentation/observation)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
