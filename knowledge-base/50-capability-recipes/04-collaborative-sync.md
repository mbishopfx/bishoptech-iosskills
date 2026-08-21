# Collaborative or Multi-Device Sync

## Best fit

Apps where the same user needs data on several Apple devices, or where people intentionally share records.

## Route

local model/store -> sync adapter -> CloudKit private/shared/public database -> change handling -> local merge -> SwiftUI/App Intents

For live co-presence or shared activities, add GroupActivities/SharePlay after the persistent data model is clear.

## Build order

1. Make local create/edit/delete reliable offline.
2. Define record identity, ownership, sharing, and deletion.
3. Choose SwiftData/Core Data integration or direct CloudKit based on control and complexity.
4. Define conflict and merge policy with concrete examples.
5. Handle iCloud account changes, network absence, change tokens, subscriptions, and retries.
6. Expose sync status without making the user debug CloudKit.
7. Test two devices, cold launch, edits on both devices, deletes, account changes, and partial failure.

## Guardrails

CloudKit is not automatically an app’s source of truth or a replacement for local persistence. Do not promise real-time collaboration from a periodic sync path.

## Sources

- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [Deciding whether CloudKit is right for your app](https://developer.apple.com/documentation/cloudkit/deciding-whether-cloudkit-is-right-for-your-app)
- [Remote records](https://developer.apple.com/documentation/cloudkit/remote-records)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [GroupActivities](https://developer.apple.com/documentation/groupactivities)
