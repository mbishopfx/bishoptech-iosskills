# HealthKit and Sensitive Data

## Capability boundary

HealthKit is a protected repository for health and fitness data on supported Apple devices. Use it for a clear, user-benefiting health or fitness workflow—not merely because a health-related idea sounds more valuable with a sensor graph.

This is an engineering route, not medical, diagnostic, treatment, prevention, or clinical advice. HealthKit access is not evidence that a feature is clinically valid, that a sample is complete, or that a derived score is safe to act on.

## Smallest native route

1. Define the exact health data types and date range the feature needs.
2. Check `HKHealthStore.isHealthDataAvailable()` and the target platform/device.
3. Enable the HealthKit capability and include truthful health-data usage descriptions.
4. Explain why the feature needs each read/share type immediately before authorization.
5. Request read and share permissions separately through `HKHealthStore`.
6. Query only the fields and time window needed; aggregate locally where possible.
7. Keep raw samples behind a domain service and expose user-understandable state to SwiftUI.
8. Handle no access, limited history, deleted data, errors, account/device changes, and unavailable features without presenting the result as complete.

## Authorization semantics

HealthKit authorization is fine-grained. A person can allow or deny individual types, change access later, and have limited history or no samples. The `success` value from `requestAuthorization(toShare:read:)` reports whether the request processed without an error; it does not mean every requested type was granted.

Reading is intentionally privacy-preserving: a query that returns no samples does not let the app confidently distinguish “access denied” from “there are no readable samples.” Design a safe empty/limited state instead of treating an empty result as proof of consent or proof that a health condition is absent.

The authorization status API is primarily useful for data the app intends to share. Do not build a read pipeline that assumes it can enumerate a person’s complete grants. Ask for the smallest set of types, stage requests by feature, and re-check the route when the app returns to the foreground.

## Read, write, and derived-data routes

| Outcome | Route | Boundary |
| --- | --- | --- |
| Display a recent quantity summary | `HKQuantityType` plus a statistics/sample query | Units, date range, source, missing data, time zone, and aggregation. |
| Inspect individual samples | `HKSampleQuery` or an anchored query | Fine-grained authorization, deletion, duplicates, source attribution, and retention. |
| Keep an incremental local projection | `HKAnchoredObjectQuery` | Anchor persistence, deletions, re-query after error, and stale local state. |
| React to new/deleted samples | `HKObserverQuery` | Background-delivery entitlement, update frequency, completion handler, and device proof. |
| Save an app-created sample/workout | `HKHealthStore.save` or workout APIs | Exact share type, user explanation, idempotency, correction/deletion, and no hidden medical claim. |
| Read clinical records | Clinical-record APIs | Stronger privacy/review boundary; do not summarize as medical advice without separate validation. |

Do not copy all HealthKit data into app storage by default. Store the minimum derived values needed for the user-facing feature, retain source/date/unit metadata, and provide deletion/export behavior that explains what is removed from the app versus what remains in HealthKit.

## HealthKit API route matrix

Choose the narrowest query and type set for the user outcome. HealthKit’s authorization, query, and background APIs report different parts of the contract.

| User need | API route | Normalize | Gate/proof |
| --- | --- | --- | --- |
| Ask for the smallest authorization set | `HKHealthStore.getRequestStatusForAuthorization` then `requestAuthorization(toShare:read:)` | Requested types, request state, processed/error result | Explain each type, request at point of need, and re-evaluate after Settings/account changes; a processed request is not proof every read type was granted. |
| Read individual samples | `HKSampleQuery` | Sample ID, type, quantity/unit or category, start/end, source, metadata | Deduplicate, honor date range/time zone, handle empty/limited/deleted/error, and retain only needed fields. |
| Maintain an incremental local projection | `HKAnchoredObjectQuery` | Added samples, deleted IDs/objects, updated anchor, last-success time | Persist anchor with the projection; recover from invalid anchor/store reset by rebuilding. |
| Calculate aggregates | `HKStatisticsQuery` or `HKStatisticsCollectionQuery` | Sum/average/min/max/count, unit, interval, source/date range | Label aggregation and missing data; do not turn a partial series into a complete health claim. |
| Observe changes | `HKObserverQuery` | “Data changed” signal, then a follow-up query result | Call background-delivery completion after processing; stop/restart intentionally and test device behavior. |
| Write app-created data | `HKHealthStore.save` or workout APIs | Operation ID, exact sample type/value/unit/date/source, user confirmation | Make writes idempotent where possible, show what is written, and test correction/deletion. |
| Workout/live session | `HKWorkoutSession` and related builder/delegate route | Session state, samples, events, end reason, saved workout ID | Workout authorization/device family, pause/resume, interruption, background, and physical device. |
| Clinical records | Clinical-record query/store route | Record type, source, date, user-reviewed summary | Stronger privacy/legal/safety boundary; do not summarize or diagnose from API access alone. |

## Target, capability, and privacy matrix

| Route | Target/configuration | Data boundary |
| --- | --- | --- |
| Read-only summary | App target with HealthKit capability and requested read types | Keep raw samples in HealthKit where possible; store a minimal derived snapshot with source/date/unit. |
| App-created sample/workout | App target with share authorization and exact types | Show the value/type/date before writing; record operation ID and correction/deletion behavior. |
| Observer/background delivery | Main app target with HealthKit background-delivery entitlement and observer setup early in lifecycle | Background callback is a change notification, not the data; query, persist, call completion, and surface stale/error state. |
| Watch/companion data | Each owning target/device route and selected HealthKit capability | Distinguish HealthKit’s store state from WatchConnectivity transfer and account/device reachability. |
| AI-derived feature | App-owned adapter between HealthKit query and local model/session | Pass only the minimum derived context, retain provenance, keep review, and never imply a clinical conclusion. |
| Widget/system surface | Extension projection with privacy-safe data and freshness | Do not expose protected values to an archived surface when authorization/account/privacy state is no longer current. |

## Incremental and background state machine

Use one durable state per data type/projection:

`notConfigured -> authorizationPending -> authorized|limited|denied -> initialQuery -> projected`

with ongoing paths:

`projected -> observerSignal -> anchoredQuery -> applyAdded/deleted -> persistAnchor -> completion`

and recovery branches:

`anchorInvalid -> rebuild`, `storeUnavailable -> retry`, `accountChanged -> reauthorize/reconcile`, `queryError -> stale/error`, `backgroundExpired -> resumeForeground`.

The `HKObserverQuery` callback does not contain the changed samples. Run an `HKSampleQuery`, statistics query, or anchored query, apply it to the local projection, and call the completion handler only after the work is complete. Bound work and avoid making a background callback wait on an unbounded AI/network task.

For every derived value, preserve: source type, date range, unit, aggregation, source/device where available, last successful query, authorization-limited state, and whether the value was user-edited. A blank result, a missing sample, and a denied read are intentionally not interchangeable.

## Query and observation lifecycle

HealthKit queries can be long-running or callback-driven. Make the owner explicit:

`idle -> authorization -> queryStarting -> loading -> ready|empty|limited|failed -> stopped`

For an `HKObserverQuery`, the update handler tells the app that matching data changed; it does not deliver the changed samples. Run a follow-up sample/statistics/anchored query, finish processing, and call the provided completion handler. Stop queries when the feature no longer owns them. Do not perform heavy work indefinitely in a background callback.

Background delivery is a separate route. Enable it only for a user-facing need, review the HealthKit Background Delivery capability/entitlement, choose an appropriate frequency, set up observers early enough for delivery, and call the completion handler. Apple’s documentation states that background server queries are not supported by the Simulator; a physical device is required for that proof.

## Privacy and data handling

Health data can reveal identity, routines, conditions, and relationships. Keep raw samples out of logs, analytics, screenshots, crash metadata, and model prompts by default. If on-device AI enriches a HealthKit-derived feature, pass the smallest derived context and make the boundary explicit; do not silently send health data to a remote tool or service.

Use source/date/unit metadata to keep an aggregate explainable. Avoid presenting a smooth graph as a complete record when authorization, source availability, date range, or device sync makes it partial. A missing sample is not a negative health finding.

## Product and safety boundary

Do not infer diagnosis, treatment, prevention, medical necessity, guaranteed wellness, or personal risk from HealthKit APIs alone. Workouts, trend summaries, reminders, and journaling can be user-facing utilities; clinical decision support, regulated claims, and emergency behavior require separate domain, legal, privacy, safety, and review analysis.

If a feature writes a HealthKit sample, show what will be written and why. Avoid duplicate writes with a stable app operation ID where the API/model allows it, and make correction/deletion behavior understandable. A write callback confirms framework processing, not that an external service or a person accepted the interpretation.

## SwiftUI state model

Use explicit states such as:

`unavailable -> needsExplanation -> authorizationPending -> authorized|limited|denied -> loading -> ready|empty|stale|error`

Display the data source, date range, units, and last refresh where they affect interpretation. Give a person a manual entry or app-local route when HealthKit is unavailable or declined, and keep the core workflow useful without protected data when possible.

## Verification route

- Test unavailable HealthKit, denied share/read access, limited history, empty results, deleted samples, multiple sources, units, time zones, daylight-saving boundaries, and account/device changes.
- Use synthetic fixtures for SwiftUI previews and unit tests; do not place personal health data in source control or test screenshots.
- Test authorization and query behavior on a physical device with a controlled Health app dataset.
- Verify background delivery, observer completion, app relaunch, watch/workout behavior, and entitlements only on the supported device family and target configuration.
- Inspect privacy copy, retention, export, deletion, analytics redaction, and user-facing explanations before release.
- Review any health, clinical, safety, or AI-derived claim independently; an API result is not product validation.

## Sources

- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [HKHealthStore](https://developer.apple.com/documentation/healthkit/hkhealthstore)
- [HealthKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.healthkit)
- [HealthKit background-delivery entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.healthkit.background-delivery)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Reading data from HealthKit](https://developer.apple.com/documentation/healthkit/reading-data-from-healthkit)
- [HKSampleQuery](https://developer.apple.com/documentation/healthkit/hksamplequery)
- [HKAnchoredObjectQuery](https://developer.apple.com/documentation/healthkit/hkanchoredobjectquery)
- [HKStatisticsQuery](https://developer.apple.com/documentation/healthkit/hkstatisticsquery)
- [HKStatisticsCollectionQuery](https://developer.apple.com/documentation/healthkit/hkstatisticscollectionquery)
- [HKObserverQuery](https://developer.apple.com/documentation/healthkit/hkobserverquery)
- [Saving data to HealthKit](https://developer.apple.com/documentation/healthkit/saving-data-to-healthkit)
- [HKWorkoutSession](https://developer.apple.com/documentation/healthkit/hkworkoutsession)
- [Executing observer queries](https://developer.apple.com/documentation/healthkit/executing-observer-queries)
- [enableBackgroundDelivery(for:frequency:withCompletion:)](https://developer.apple.com/documentation/healthkit/hkhealthstore/enablebackgrounddelivery%28for%3Afrequency%3Awithcompletion%3A%29)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
