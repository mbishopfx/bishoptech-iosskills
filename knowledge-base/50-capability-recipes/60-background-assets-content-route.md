# Background Assets content and model-pack capability route

Use this route when an iPhone/iPad app needs additional game, media, 3D, shader, or on-device model resources outside the main app bundle. Start with the [Background Assets deep dive](../42-framework-deep-dives/37-background-assets-managed-content-and-model-packs.md), the [content and model-pack design guide](../21-design-deep-dives/57-background-assets-content-and-model-pack-design.md), the [proof matrix](../60-verification/54-background-assets-content-proof-matrix.md), and the [code recipes](../70-code-recipes/72-background-assets-content-recipes.md).

## Route selector

| Product need | Choose | Main target surface |
| --- | --- | --- |
| System-managed packs | Managed Background Assets | AssetPackManager actor plus managed downloader extension |
| Apple-hosted packs | Managed plus StoreKit StoreDownloaderExtension | App Store Connect asset-pack versions |
| Self-hosted managed packs | Managed plus ManagedDownloaderExtension | Manifest/pack hosting and App Group |
| Individual self-hosted downloads | Unmanaged Background Assets | BADownloadManager, BAURLDownload, BADownloaderExtension |
| Assets required before first launch | Unmanaged essential-download route | Manifest and essential-size Info.plist contract |
| On-demand model/Metal/media pack | Managed or unmanaged based on pack/lifecycle needs | Validation/readiness layer after download |
| Future language-specific packs | Localized asset-pack APIs only when target supports them | Current SDK availability gate |

Do not use Background Assets to send user/device identification data, advertising data, or arbitrary application logic. It is for additional app assets.

## Configuration gate

1. Define the asset type, feature, version, and fallback.
2. Decide managed versus unmanaged before adding code.
3. For managed assets, decide Apple-hosted versus self-hosted.
4. Create the app and extension targets required by the selected route.
5. Add App Groups to the app and extension when the route requires shared state.
6. Configure manifest/pack identifiers and size policies.
7. Set the relevant Background Asset Info.plist keys with correct compressed/uncompressed meanings.
8. Configure App Store Connect asset packs for Apple hosting.
9. Add a local mock-server test plan before distribution.
10. Define file/schema/device/quality validation before marking a pack ready.
11. Define storage removal, update rollback, low-storage, offline, and extension-termination behavior.
12. Verify the signed app and extension artifacts.

### Configuration worksheet

| Field | Decision |
| --- | --- |
| App target |  |
| Extension target |  |
| Deployment target |  |
| Managed/unmanaged |  |
| Apple/self-hosted |  |
| App Group |  |
| Asset pack IDs |  |
| Manifest URL, if unmanaged |  |
| Domain allowlist, if unmanaged |  |
| Essential compressed allowance |  |
| Essential install size |  |
| Nonessential download allowance |  |
| Maximum install size |  |
| Model/asset schema |  |
| Validation revision |  |
| Fallback |  |
| TestFlight/App Store asset version |  |

## Managed route

Use AssetPackManager when the product wants the system to manage pack availability:

~~~text
manifest
-> AssetPackManager
   -> status updates
   -> check for updates
   -> ensure local availability
   -> contents/descriptor/URL
      -> app validation
         -> feature ready
~~~

The manager is an actor. Keep resource state in an app-owned model and bridge status updates to the main actor. The first access to the shared manager opts the app into the managed architecture, so add the matching extension protocol before relying on it.

### Pack policy

Classify each pack:

| Policy | Behavior |
| --- | --- |
| Essential | Needed before first useful launch; keep small and prove failure fallback |
| Prefetch | Useful soon but app can launch without it |
| On demand | Download at a feature boundary |
| Optional | Person can keep/remove based on storage |
| Latest required | Feature cannot safely use an old validated version |
| Latest preferred | Old version remains safe while new version downloads |

Use ensureLocalAvailability with the correct latest-version policy. Keep an older validated pack when it is safe to avoid blocking a feature on a network event.

## Apple-hosted route

For Apple-hosted packs:

1. Prepare the asset pack manifest and pack files.
2. Configure the managed asset-pack app/extension target.
3. Set the Apple-hosting Info.plist choice.
4. Upload and version the packs through App Store Connect.
5. Distribute the app through TestFlight/App Store according to the current Apple route.
6. Test updates, removal, rollout, and a pack that is newer than the app.
7. Record App Store Connect asset-pack version in the release packet.

App Store Connect hosting is not a substitute for a server-backed user-data service. Do not put account-specific content or secrets into a public/static asset pack.

## Self-hosted managed route

Self-hosted managed packs still require:

- manifest and pack schema;
- HTTPS hosting;
- domain ownership and cache policy;
- App Group/extension configuration;
- pack identity/version/rollback;
- outage and stale-cache handling;
- validation after local availability.

The system may download later than the app expects. Keep the active pack ready and show a fallback.

## Unmanaged route

Choose the unmanaged route when the app needs individual download objects or custom scheduling:

1. Add the self-hosted unmanaged extension target.
2. Configure App Groups on app and extension.
3. Add BAManifestURL and the relevant size/domain keys.
4. Ensure compressed download and uncompressed install bounds are correct.
5. Build a BAURLDownload with an allowlisted URL/domain and stable identifier.
6. Schedule with BADownloadManager.
7. Handle finished, failed, authentication, cancel, and termination callbacks.
8. Validate and atomically publish the resource to the app.

Do not schedule arbitrary URLs or let a model choose the domain allowlist.

## Essential-download route

Use essential downloads only for content the app truly needs before first launch. Keep a small main-bundle shell and test:

- fresh install;
- update;
- restore;
- no network;
- low storage;
- restricted cellular/network policy;
- extension termination;
- corrupt or incompatible file;
- manifest unavailable.

If an essential asset fails, show a useful fallback or an actionable repair state. A launch blocker with no recovery is not a polished native experience.

## Model and shader route

For a downloadable AI/graphics asset, use a second readiness gate:

~~~text
resource local
-> file/schema/identity validation
-> framework load
-> device feature check
-> representative quality/performance test
-> ready for product task
~~~

For Core ML:

- preserve model revision and input/output schema;
- check compute-unit/device conditions;
- measure latency, memory, and thermal behavior;
- keep manual/deterministic fallback.

For Metal:

- validate library load and GPU feature support;
- version shader/resource layouts;
- preserve a simpler renderer;
- measure frame time and thermal state.

For media/3D:

- validate container/codec/asset format;
- handle streaming or file access separately from content availability;
- keep a lower-quality or alternate asset path.

Do not treat an asset file’s presence as model quality, shader correctness, or media playback proof.

## Localized pack route

Apple’s current localized asset-pack documentation describes iOS 27 and later availability. For an iOS 26 target, gate these APIs and use a nonlocalized pack/fallback unless the target’s SDK explicitly supports the route.

For supported targets:

- define language IDs in the documented BCP-47 subset;
- inspect manifest localized packs;
- reconcile preferred language deliberately;
- use language-specific content access when a path is ambiguous;
- test language change and storage cleanup.

## SwiftUI/Liquid Glass route

The app-owned resource screen can use:

- a standard ProgressView and text status;
- a compact glass status card;
- a toolbar download/remove action;
- a review sheet after validation;
- a fallback mode button.

Keep the system downloader extension and resource handoff out of the view body. Use a model/actor to own operation state.

## AI boundary

AI may:

- explain a resource state;
- summarize what an asset unlocks;
- suggest a lower-resource mode;
- draft a local model description.

AI may not:

- schedule an unallowlisted URL;
- choose a manifest or pack ID outside an app catalog;
- mark an unvalidated asset ready;
- load arbitrary code;
- approve a model for production without quality fixtures;
- delete user-owned records because a pack was removed.

## Failure matrix

| Failure | User-facing state | Fallback |
| --- | --- | --- |
| No manifest | Content unavailable | Main-bundle/manual mode |
| Pack not found | Version removed | Older validated pack or fallback |
| Download delayed | Waiting/scheduled | Continue current mode |
| Download failed | Retryable error | Offline/basic mode |
| Low storage | Cannot install | Remove optional pack or use lower quality |
| Device unsupported | Resource cannot load | CPU/basic model/alternate renderer |
| Schema mismatch | Downloaded but incompatible | Keep old version; block new feature |
| Model quality regression | Asset valid but not acceptable | Roll back or disable |
| Extension terminated | Work incomplete | Resume from durable state |
| Self-hosted auth/domain failure | Resource unavailable | Retry/manual support |
| Asset removed | Feature changed | Explain and preserve user records |

## Route completion

- [ ] Managed/unmanaged decision is documented.
- [ ] Apple/self-hosted hosting decision is documented.
- [ ] App and extension targets are configured.
- [ ] Manifest, pack IDs, versions, and size semantics are recorded.
- [ ] App Group and Info.plist values are verified in signed artifacts.
- [ ] Local mock-server tests pass.
- [ ] Install/update/offline/low-storage/termination/rollback paths are tested.
- [ ] Content validation is separate from download completion.
- [ ] Model/Metal/media resource readiness is measured on target devices.
- [ ] iOS 26 versus newer localized-pack availability is explicit.
- [ ] AI is bounded to explanation/proposals.
- [ ] Liquid Glass and accessibility fallbacks are tested.

## Sources

- [Background Assets](https://developer.apple.com/documentation/backgroundassets)
- [Creating managed asset packs](https://developer.apple.com/documentation/backgroundassets/creating-managed-asset-packs)
- [Downloading Apple-hosted asset packs](https://developer.apple.com/documentation/backgroundassets/downloading-apple-hosted-asset-packs)
- [Testing asset packs locally](https://developer.apple.com/documentation/backgroundassets/testing-asset-packs-locally)
- [Configuring an unmanaged Background Assets project](https://developer.apple.com/documentation/backgroundassets/configuring-an-unmanaged-background-assets-project)
- [Downloading essential assets in the background](https://developer.apple.com/documentation/backgroundassets/downloading-essential-assets-in-the-background)
- [AssetPackManager](https://developer.apple.com/documentation/backgroundassets/assetpackmanager)
- [AssetPackManifest](https://developer.apple.com/documentation/backgroundassets/assetpackmanifest)
- [BADownloadManager](https://developer.apple.com/documentation/backgroundassets/badownloadmanager)
- [BADownload](https://developer.apple.com/documentation/backgroundassets/badownload)
- [BAURLDownload](https://developer.apple.com/documentation/backgroundassets/baurldownload)
- [BADownloaderExtension](https://developer.apple.com/documentation/backgroundassets/badownloaderextension)
- [BAUsesAppleHosting](https://developer.apple.com/documentation/bundleresources/information-property-list/bausesapplehosting)
- [BAManifestURL](https://developer.apple.com/documentation/bundleresources/information-property-list/bamanifesturl)
- [Background Assets in the App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi/background-assets)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
