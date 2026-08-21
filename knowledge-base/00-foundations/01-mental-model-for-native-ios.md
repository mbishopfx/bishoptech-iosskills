# Mental Model for Native iOS

## The layered route

Most app ideas become easier to reason about when they are separated into layers:

1. **App and scenes** — the entry point, windows, scene lifecycle, deep links, and system surfaces.
2. **Features** — user-facing flows such as inbox, capture, editor, player, map, or settings.
3. **Domain** — the nouns, rules, state transitions, and user-visible outcomes that matter without a specific screen.
4. **Services** — persistence, networking, media, sensors, AI, notifications, commerce, and system integration.
5. **Infrastructure** — authorization, logging, clocks, file storage, model loading, retry policy, and adapters.
6. **Views** — SwiftUI composition, layout, interaction, accessibility, and animation.

The direction of dependency should usually point inward: views ask feature/domain services to perform work; services do not reach into a view to mutate presentation state.

## Single source of truth

SwiftUI updates views from data. Put state at the smallest common owner that needs to write it, pass read-only values downward, and pass `Binding` only when a child needs to edit the owner’s value. Do not use view state as a persistence layer. The view lifecycle can recreate views; persistent data belongs in SwiftData, files, Keychain, or another explicit store.

## A useful feature slice

For a new feature, write down:

- the user outcome;
- the domain state and allowed transitions;
- the entry route and exit route;
- the system permission or entitlement;
- the local and remote data boundaries;
- the unavailable/failure state;
- the evidence needed to call it complete.

This prevents “beautiful screen” work from hiding missing persistence, authorization, or recovery behavior.

## Local-first default

For account-free utilities, begin with on-device data and an explicit export/sync decision. Add a backend only when the user outcome genuinely needs multi-device sync, collaboration, server-side computation, or an external source of truth. Keep the cloud adapter behind a domain-facing service so the core workflow remains testable without network access.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
- [Observation](https://developer.apple.com/documentation/observation)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [Preserving your app’s model data across launches](https://developer.apple.com/documentation/swiftdata/preserving-your-apps-model-data-across-launches)
