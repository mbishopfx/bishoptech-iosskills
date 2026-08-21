# State, Observation, and Data Flow

## The source-of-truth rule

Store a piece of mutable state at the least common ancestor of the views that need to change it. Pass read-only values downward. Pass a Binding only when a child genuinely edits the parent-owned value. This makes ownership visible and reduces accidental two-way coupling.

## Choose the storage by lifetime

| Need | Typical SwiftUI route | Use it for |
| --- | --- | --- |
| Transient view state | State | Selection, focus, sheet visibility, a draft toggle, loading presentation. |
| Child write access | Binding | A reusable editor that changes owner state. |
| Shared observable model | Observation plus environment/injection | Feature state used by multiple views. |
| Persisted records | SwiftData or explicit files | Data that must survive view recreation and launches. |
| Secret or credential | Keychain/Security | Tokens, keys, and secrets—not ordinary app records. |
| Derived value | Computed property or view transformation | Values that can be recalculated from source state. |

Do not use State as a persistence system. SwiftUI state follows view identity and lifecycle; it is not a durable database.

## Observation

The Observation framework can mark a reference type with the Observable macro so SwiftUI tracks the properties read by a view. Keep observable models focused: presentation state can live in a feature model, while domain rules and persistence remain in services or use cases.

~~~swift
@MainActor
@Observable
final class InboxModel {
    enum State { case idle, loading, loaded([Message]), failed(String) }
    var state: State = .idle

    func reload(using service: InboxService) async {
        state = .loading
        do {
            state = .loaded(try await service.fetchMessages())
        } catch is CancellationError {
            state = .idle
        } catch {
            state = .failed(error.localizedDescription)
        }
    }
}
~~~

The example makes UI state explicit and keeps asynchronous work behind a service. In a real app, inject the service and use a test double.

## State transitions are a product surface

Model the states a person can encounter: empty, loading, loaded, refreshing, unavailable, failed, permission-needed, and partially complete. A design that only shows the success state is not a complete design.

## Avoid accidental work

Keep expensive work out of body. Use lifecycle tasks, explicit actions, memoized/derived values, and isolated services. Make task cancellation part of the feature design so a view disappearing does not leave a stale result writing into new state.

## Sources

- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
- [Observation](https://developer.apple.com/documentation/observation)
- [State](https://developer.apple.com/documentation/swiftui/state)
- [Binding](https://developer.apple.com/documentation/swiftui/binding)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
