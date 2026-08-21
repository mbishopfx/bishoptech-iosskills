# Data, Persistence, and Sync

## Choose the storage boundary

| Need | Recommended first route | Why |
| --- | --- | --- |
| Small preferences | UserDefaults | Simple settings and feature flags. |
| Structured local records | SwiftData | Swift-native models, queries, persistence, SwiftUI integration. |
| Existing complex object graph | Core Data | Mature migrations, fetches, and CloudKit mirroring. |
| Large or user-visible files | FileManager, FileDocument, iCloud Documents | Keep binary attachments outside record rows. |
| Secrets | Keychain/Security | Protected credential storage. |
| Cross-device/cloud records | CloudKit | User/private/public/shared iCloud data with explicit sync design. |

## Local-first route

For a private utility:

1. Define a domain model independent of storage.
2. Store structured metadata in SwiftData or Core Data.
3. Store large files in a protected file directory and keep a stable reference in the model.
4. Make the app fully usable without a network connection when possible.
5. Add CloudKit only after deciding what sync, conflict, sharing, and account behavior the user needs.
6. Treat sync as replication, not the only source of UI truth.

## SwiftData

SwiftData describes model classes with macros, uses ModelContext to insert/fetch/delete/save, and integrates with SwiftUI through model containers and queries. It can also be used as a local cache for remote data. Decide schema identity, relationships, delete rules, migration, large attachment handling, and error/recovery behavior before building the screen.

## CloudKit

CloudKit moves data between the app and iCloud containers. It is complementary to the app’s local data objects and has network/account implications. Direct CloudKit is powerful but increases schema, change-token, conflict, account, subscription, and offline complexity. Prefer the least complex sync layer that preserves the product’s truth.

## Conflict and deletion policy

Define what happens when:

- a record changes on two devices;
- a record is deleted remotely;
- the user signs out or changes iCloud state;
- the network fails during a write;
- a schema migration is incomplete;
- a file exists without metadata or metadata points to a missing file.

## Privacy

Classify each field. Health, location, financial, identity, audio, image, and journal-like data need a clear retention/deletion story. The user should be able to understand what stays on device, what syncs, and what gets exported.

## Sources

- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [Preserving your app’s model data across launches](https://developer.apple.com/documentation/swiftdata/preserving-your-apps-model-data-across-launches)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [Deciding whether CloudKit is right for your app](https://developer.apple.com/documentation/cloudkit/deciding-whether-cloudkit-is-right-for-your-app)
- [Core Data](https://developer.apple.com/documentation/coredata)
- [Security](https://developer.apple.com/documentation/security)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
