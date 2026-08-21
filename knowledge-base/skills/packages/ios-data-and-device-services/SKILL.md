---
name: ios-data-and-device-services
description: Route, implement, or review iOS persistence, CloudKit sync, HealthKit, Contacts, EventKit, WeatherKit, HomeKit, Core Bluetooth, Nearby Interaction, and local-network features. Use when an app stores personal data, syncs across devices, reads protected records, discovers accessories, measures proximity, or connects to a local service.
---

# iOS Data and Device Services

Use this skill to keep app-owned data, Apple-managed records, external service state, device discovery, protocol trust, permissions, sync, and physical-world side effects distinct.

`user intent -> authorization/capability -> typed local state -> external/service operation -> stale/error/conflict handling -> reviewable result -> retention/deletion`

## Read before acting

- Inspect the actual Xcode targets, deployment target, platforms, model containers, schema/migrations, iCloud containers, capabilities, entitlements, usage descriptions, background modes, network/accessory protocols, and persistence/privacy adapters.
- Read the [data/persistence/sync route](../../../40-framework-routes/01-data-persistence-and-sync.md), [location/maps/weather route](../../../40-framework-routes/03-location-maps-and-places.md), [SwiftData/CloudKit deep dives](../../../41-framework-deep-dives/00-swiftdata-and-local-persistence.md), [HealthKit deep dive](../../../42-framework-deep-dives/01-healthkit-and-sensitive-data.md), [HomeKit/Bluetooth/Nearby deep dive](../../../42-framework-deep-dives/02-homekit-bluetooth-and-nearby.md), and [contacts/calendar/network deep dives](../../../43-system-framework-deep-dives/01-contacts-calendar-and-notifications.md).
- Refresh the exact official pages in the Sources section before relying on an authorization status, capability, entitlement, iCloud/account behavior, protected-data rule, radio state, local-network prompt, weather freshness, or background-delivery claim.

## Route workflow

1. State the user-owned outcome and data class: private local record, synced record, selected HealthKit/Contacts/EventKit data, weather observation, HomeKit physical state, Bluetooth protocol, Nearby distance/direction, or local-network service.
2. Choose the smallest storage/service route. Use SwiftData for structured local records, files for large user-owned data, Keychain for secrets, CloudKit only when cross-device/shared replication is needed, and the narrow system framework for protected data or device access. Do not add a backend or account to solve a local-first problem.
3. Record the target matrix before implementation: platform/device family, permission and usage description, capability/entitlement, account/service state, model/schema version, data retention/deletion, supported accessory/protocol, network topology, and offline/manual fallback. Mark unknown availability as `to-verify`.
4. Separate state layers. Keep local persistence, migration, sync/account, authorization, discovery, trust/protocol, operation, freshness, conflict, and user review as separate states; never collapse them into `isConnected`, `isAuthorized`, `isSynced`, or `hasData`.
5. Draw the operation boundary: `intent -> check current state -> validate target/schema -> perform bounded operation -> reconcile callback/change -> persist projection -> show stale/error/retry/manual route`. Make writes idempotent where a duplicate can cause harm.
6. Define privacy and retention before querying or logging. Ask for the minimum type/field/date range, keep raw health/contact/location/home/radio data out of logs, minimize synced projections, explain what leaves the device, and provide app-side deletion/export/revocation behavior.
7. Bound asynchronous work. Cancel queries, observations, sync batches, discovery scans, connections, ranging sessions, and retries when the feature no longer owns them. Finish observer/background callbacks, release radio sessions, and ignore stale callbacks after cancellation.
8. Verify with fixtures first, then signed physical devices and real services/accessories. Record OS, device, account, authorization state, dataset, schema/environment, accessory firmware, network topology, timestamp, and observed latency/freshness; do not generalize one successful run.

## Persistence and sync boundaries

- Keep a domain model independent of SwiftData/Core Data/CloudKit. Use SwiftData `ModelContainer`/`ModelContext` and explicit schema/migration policy for local records; use `ModelActor` or an intentional isolation boundary for background persistence.
- Store large media/files outside record rows with stable references and coordinated deletion. Keep secrets in Keychain, not UserDefaults, logs, analytics, URLs, or ordinary model fields.
- CloudKit is replication with account, container, environment, network, quota, conflict, deletion, and schema state. It is not automatically the app’s only source of truth. Model iCloud unavailable, account changes, remote deletion, duplicate edits, server-record conflicts, schema migration, and partial/offline state.
- Treat a local write, successful save, change token, sync event, or last-known projection as evidence about one boundary only. Do not label it “synced,” “current,” “backed up,” or “shared” without the corresponding account/environment and reconciliation evidence.
- For reviewable AI-derived or external records, persist source identifiers, timestamps, model/algorithm version, provenance, review/edit state, and deletion relationship. Do not silently promote generated data into domain truth.

## Protected personal data

- HealthKit authorization is fine-grained and privacy-preserving. A processed authorization request does not mean every type was granted; an empty read does not prove denial or absence of data. Query only needed types/ranges and preserve source/date/unit metadata.
- HealthKit observer updates indicate that matching data changed; follow with a bounded query, call the background completion handler, and handle limited history, deletions, account/device changes, and unavailable data. Never turn a missing sample or derived trend into a diagnosis, treatment, medical necessity, or guaranteed wellness claim.
- Contacts and EventKit are external user-owned stores. Choose picker/store authorization deliberately, request the minimum access, handle revoked/limited access, stale identifiers, user edits/deletions, duplicate events, time zones, and write confirmation. An imported contact or event is not permission to message, modify, or expose it elsewhere.
- WeatherKit results have service/entitlement, location, attribution, network, timestamp, forecast/historical scope, and cache/freshness state. Label location and observation time; do not present a forecast as a guarantee or a cached value as current.

## Accessories, proximity, and local network

- HomeKit uses a shared Home database. Observe `HMHomeManager` state, distinguish read from physical write, confirm actions that unlock/open/heat/alarm/monitor, and label last-known values. A callback or discovered accessory does not prove a safe or permanent physical effect.
- Core Bluetooth central and peripheral roles have different radio/protocol/background boundaries. Wait for `CBCentralManager`/`CBPeripheralManager` state, scan only for supported service UUIDs, validate GATT services/characteristics and versioned payloads, stop scans, time out operations, and avoid unbounded reconnect loops.
- Nearby Interaction needs a session-specific peer/accessory configuration, discovery-token exchange, usage description, supported hardware, and session lifecycle. Distance/direction is relative framework output, not identity, location, trust, or safety proof. Use an authenticated/out-of-band exchange and a separate transport.
- Network/Bonjour discovery is not authentication. Request local-network access with the target declarations, model `NWBrowser`/`NWConnection` ready/waiting/failed/cancelled states, authenticate the peer, secure sensitive traffic, handle network changes, and retain a manual pairing route where useful.
- Keep framework availability, discovered candidate, product trust, user selection, protocol compatibility, connection, and operation result distinct. Discovery never silently authorizes a physical side effect.

## Non-negotiable safety and evidence rules

- Never present a local record, sync result, HealthKit value, contact/event, weather observation, accessory discovery, Bluetooth identifier, Nearby result, Bonjour name, or endpoint as current truth, identity, trust, medical validation, safety, or delivery proof without the separate evidence required by that domain.
- Never request a broad permission, protected data class, cloud account, accessory radio, local-network access, or telemetry path because it may be useful later. Tie every capability, entitlement, usage description, and retention rule to the stated feature.
- Treat external records, sync payloads, accessory messages, discovery results, weather responses, and local-network services as untrusted/stale. Validate IDs, dates, units, ranges, versions, signatures/authentication, payload sizes, and action targets before persistence or side effects.
- Never claim background delivery, sync timing, radio continuity, UWB support, accessory compatibility, weather freshness, or physical-world safety from a simulator, mock, fixture, preview, or one device.
- Preserve a useful local/manual path when permission, account, network, sensor, accessory, or service availability is missing. A fallback must not silently weaken security, privacy, paid access, or physical safety.

## Deliverable

Produce a compact route note or implementation change containing:

- selected framework/storage/service and rejected alternatives;
- target/device, model/schema, account, permission, usage-description, capability, entitlement, accessory/protocol, network, privacy, and retention matrix;
- authorization/discovery/trust/operation/sync state machine with conflict, stale, cancellation, retry, manual fallback, and deletion behavior;
- source/date/unit/provenance and user-review policy for imported, synced, protected, or generated values;
- exact compile, fixture, signed physical-device, multi-device/service/accessory, privacy, performance, signing, and release evidence plan;
- remaining `to-verify` gaps and claims deliberately not made.

For implementation, change only the requested target and directly related adapters/configuration. Do not add CloudKit, an account, a server, protected-data access, a radio permission, local-network access, background delivery, physical writes, analytics, or telemetry without a stated user-facing need and authorization.

## Related routes and recipes

- [Data, persistence, and sync](../../../40-framework-routes/01-data-persistence-and-sync.md)
- [Location, maps, and places](../../../40-framework-routes/03-location-maps-and-places.md)
- [SwiftData and local persistence](../../../41-framework-deep-dives/00-swiftdata-and-local-persistence.md)
- [CloudKit and sync](../../../41-framework-deep-dives/01-cloudkit-and-sync.md)
- [HealthKit and sensitive data](../../../42-framework-deep-dives/01-healthkit-and-sensitive-data.md)
- [HomeKit, Bluetooth, and Nearby](../../../42-framework-deep-dives/02-homekit-bluetooth-and-nearby.md)
- [Contacts, calendar, and notifications](../../../43-system-framework-deep-dives/01-contacts-calendar-and-notifications.md)
- [WeatherKit and system data](../../../43-system-framework-deep-dives/03-weatherkit-and-system-data.md)
- [Persistence, local-first, and sync recipes](../../../70-code-recipes/11-persistence-local-first-and-sync-recipes.md)
- [Health, personal-data, and notification recipes](../../../70-code-recipes/16-health-personal-data-and-notification-recipes.md)
- [HomeKit, Bluetooth, Nearby, and local-network recipes](../../../70-code-recipes/15-homekit-bluetooth-and-nearby-recipes.md)
- [Permission, entitlement, and privacy checklist](../../../60-verification/04-permission-entitlement-and-privacy-checklist.md)
- [Build, device, and release checklist](../../../60-verification/01-build-device-and-release-checklist.md)

## Sources

- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [ModelContainer](https://developer.apple.com/documentation/swiftdata/modelcontainer)
- [ModelContext](https://developer.apple.com/documentation/swiftdata/modelcontext)
- [VersionedSchema](https://developer.apple.com/documentation/swiftdata/versionedschema)
- [SchemaMigrationPlan](https://developer.apple.com/documentation/swiftdata/schemamigrationplan)
- [ModelActor](https://developer.apple.com/documentation/swiftdata/modelactor)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [Deciding whether CloudKit is right for your app](https://developer.apple.com/documentation/cloudkit/deciding-whether-cloudkit-is-right-for-your-app)
- [CKContainer](https://developer.apple.com/documentation/cloudkit/ckcontainer)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [HKHealthStore](https://developer.apple.com/documentation/healthkit/hkhealthstore)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Reading data from HealthKit](https://developer.apple.com/documentation/healthkit/reading-data-from-healthkit)
- [Executing observer queries](https://developer.apple.com/documentation/healthkit/executing-observer-queries)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [Contacts](https://developer.apple.com/documentation/contacts)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [ContactsUI](https://developer.apple.com/documentation/contactsui)
- [EventKit](https://developer.apple.com/documentation/eventkit)
- [Accessing the event store](https://developer.apple.com/documentation/eventkit/accessing-the-event-store)
- [EKEventStore](https://developer.apple.com/documentation/eventkit/ekeventstore)
- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [WeatherService](https://developer.apple.com/documentation/weatherkit/weatherservice)
- [WeatherAttribution](https://developer.apple.com/documentation/weatherkit/weatherattribution)
- [HomeKit](https://developer.apple.com/documentation/homekit)
- [HMHomeManager](https://developer.apple.com/documentation/homekit/hmhomemanager)
- [Enabling HomeKit in your app](https://developer.apple.com/documentation/homekit/enabling-homekit-in-your-app)
- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [CBPeripheral](https://developer.apple.com/documentation/corebluetooth/cbperipheral)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [Network](https://developer.apple.com/documentation/network)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
