# Background Assets, managed content, and model packs

Background Assets lets an iPhone or iPad app obtain additional content outside the main app bundle. The system can manage asset packs, schedule downloads before or after launch, update Apple-hosted packs independently of an app build, and expose downloaded content to the app. The same framework also provides lower-level unmanaged APIs for an app and extension to manage individual downloads.

This is a content-delivery boundary, not a general background worker, analytics channel, user-data transport, or arbitrary code-loading mechanism. Use it for additional app assets such as game levels, 3D models, textures, audio, video, Metal libraries, or on-device model files where the selected target and Apple review path support the asset type.

Use this deep dive with the [Background Assets capability route](../50-capability-recipes/60-background-assets-content-route.md), the [content and model-pack design guide](../21-design-deep-dives/57-background-assets-content-and-model-pack-design.md), the [proof matrix](../60-verification/54-background-assets-content-proof-matrix.md), and the [code recipes](../70-code-recipes/72-background-assets-content-recipes.md).

## The two architecture families

Choose one content-management family deliberately:

| Need | Managed Background Assets | Unmanaged Background Assets |
| --- | --- | --- |
| System manages asset packs | Yes | No; app/extension manages downloads |
| Content unit | AssetPack and manifest | BAURLDownload/BADownload and manifest |
| Hosting | Apple-hosted or self-hosted depending configuration | Self-hosted URL/domain path |
| Main manager | AssetPackManager actor | BADownloadManager singleton |
| Extension | ManagedDownloaderExtension or StoreKit StoreDownloaderExtension for Apple hosting | BADownloaderExtension |
| Best for | Pack-level content, system scheduling, App Store asset versions | Individual downloads and custom scheduling |
| Main risk | Opting into manager without matching extension/configuration | URL/manifest/allowlist/size/extension lifecycle |

Do not reference AssetPackManager and treat the target as unmanaged. Apple’s documentation describes the first reference to the shared manager as opting into automatic management and requires the corresponding managed extension protocol.

## Content lifecycle

Model a pack as a versioned product resource:

~~~text
pack declaration
-> manifest and content identity
-> App Store Connect or self-hosted publication
-> system discovery
-> queued/downloading
-> local availability
-> schema/model/renderer validation
-> app feature readiness
-> replacement/removal
~~~

The download completing is not the same as the feature being ready. A downloaded model may be incompatible with the app’s input schema. A Metal library may not support the GPU family. A level pack may require a newer game schema. A localized pack may not match the current language.

Keep these states distinct:

| State | Meaning |
| --- | --- |
| declared | The pack is in the manifest or target configuration |
| discoverable | The system knows about a pack version |
| scheduled | A download request exists |
| downloading | System reports active progress/state |
| local | Required bytes are locally available |
| validated | The app accepted identity, version, schema, and compatibility |
| ready | The feature can use the resource |
| stale | A newer version exists or the local version no longer matches policy |
| removed | The pack is no longer available or the app removed it |
| failed | Download or validation failed; fallback remains |

## Managed Background Assets

Managed asset packs use AssetPack, AssetPackManifest, AssetPackManager, and the associated managed downloader extension. The manager is an actor and exposes asynchronous status updates, manifest access, local-availability checks, content access, update checks, and removal.

The main managed route:

1. Group app resources into asset packs with a manifest.
2. Declare essential, prefetch, or on-demand policy.
3. Add the appropriate managed Background Download extension.
4. Configure the app group identifier shared with the extension.
5. Choose Apple-hosted or self-hosted asset delivery.
6. Publish and version packs through the corresponding channel.
7. Use AssetPackManager to inspect status and ensure local availability.
8. Validate a pack before enabling the feature.

If the app uses Apple hosting, Apple’s current documentation describes StoreKit’s StoreDownloaderExtension for the corresponding extension protocol. If the app self-hosts managed packs, use the documented ManagedDownloaderExtension route. Verify the exact target and protocol names for the selected SDK.

### AssetPackManager actor

The manager provides:

- a shared actor;
- an asset-pack manifest;
- statusUpdates for all packs or a named pack;
- contents, descriptor, and URL access for a pack file;
- checkForUpdates;
- ensureLocalAvailability with optional latest-version requirements;
- local availability/status checks;
- removal;
- language-related properties and methods where the target supports the API.

Actor isolation matters. Do not pass a mutable manager or an open file descriptor across arbitrary tasks without a defined ownership policy. Make the feature’s readiness state Sendable and publish it to the main actor.

### Update behavior

checkForUpdates can discover current server information, update outdated packs, and remove obsolete packs. It does not mean a feature can use the new content immediately. Revalidate schema and compatibility after an update.

Use requireLatestVersion only when the feature cannot safely run against the older local pack. Otherwise, keep the older validated version available while the newer one downloads, so a person does not lose the feature unnecessarily.

### Reading pack contents

AssetPackManager can return Data, a FileDescriptor, or a URL for a relative path. Choose the smallest access form:

- Data for small configuration or bounded metadata;
- FileDescriptor for streaming/large content paths where the API supports it;
- URL for APIs that require a file URL, such as model or media loading.

Keep relative paths inside the pack contract. Do not let an AI model choose an arbitrary path or asset-pack identifier. Resolve only allowlisted resources from the manifest and feature schema.

## Apple-hosted asset packs

Apple-hosted packs are uploaded and versioned through App Store Connect. They can update additional content without creating a new app version, subject to Apple’s current distribution and review rules.

Use this route for:

- large tutorial or level packs;
- video/audio content;
- textures and 3D models;
- Metal shader libraries;
- on-device machine-learning model files;
- other static resources that belong to the app feature.

The App Store Connect asset pack version and the app’s compatibility policy are separate. The app should record the pack identifier, version, local validation result, and the app build that accepted it.

Do not use Apple-hosted Background Assets to collect or transmit data identifying a user or device, or to perform advertising or advertising measurement. The framework’s purpose is additional app content.

## Self-hosted managed packs

Self-hosted managed packs still use the managed pack model and system scheduling, but the app owns the hosting path. Keep:

- HTTPS and domain ownership;
- manifest schema and versioning;
- pack size and compression accounting;
- server cache/retention policy;
- rollback to an older validated pack;
- outage/offline behavior;
- extension and App Group configuration.

A self-hosted URL being reachable from a development machine is not proof that the system extension can download the same content in production.

## Unmanaged Background Assets

Unmanaged Background Assets uses a self-hosted manifest and an extension that schedules downloads in response to system events. The target adds an unmanaged extension and configures Background Asset Info.plist keys.

The system can launch the extension around install, update, and later background moments. The extension must be short-lived and restartable. It should:

1. Read the manifest.
2. Create or recover download objects.
3. Schedule essential/nonessential downloads within configured allowances.
4. Process completed files.
5. Persist completion/validation state in the shared App Group.
6. Handle authentication challenges and failures.
7. Respond safely to extensionWillTerminate.

### Configuration values

The current unmanaged project guide distinguishes:

- BAManifestURL;
- BADownloadDomainAllowList;
- BAInitialDownloadRestrictions;
- BAEssentialDownloadAllowance;
- BAEssentialMaxInstallSize;
- BADownloadAllowance;
- BAMaxInstallSize.

Size meanings matter. Some allowances use compressed download size; installation-size keys use uncompressed size. The app must set combined bounds accurately, not treat them as per-file budgets.

Use wildcard domains only when the product owns and needs the exact subdomain pattern. Do not put credentials in a manifest URL or allowlist more domains than the feature needs.

### BADownloadManager

BADownloadManager.shared schedules, starts foreground downloads, cancels downloads, and exposes a delegate for progress/completion events. It is shared between the app and extension according to the configured App Group.

Scheduling is not completion. Keep a durable state machine:

~~~text
declared
-> scheduled
-> running
-> finished-with-file
-> validated
-> available
or failed/canceled/needs-retry
~~~

The manager’s startForegroundDownload is a foreground start route, not a guarantee that the download completes before the next view update. Keep progress and feature readiness separate.

### BAURLDownload and BADownload

BAURLDownload represents a remote asset download with an app-defined identifier, request, size/essential policy, App Group, and priority as supported by the selected SDK. BADownload exposes identifier, unique system identifier, essential state, priority, and current state.

Treat the identifier as app-owned resource identity and the unique identifier as a system-owned operation identity. Never use a model-generated identifier for a privileged or destructive content operation.

### BADownloaderExtension

The unmanaged extension can:

- return downloads for a content request and manifest;
- handle authentication challenges;
- process a finished file URL;
- handle failure;
- respond to extension termination.

A finished file URL is a handoff point. Verify the file’s expected pack/resource identity, schema, size, and compatibility before marking it ready.

## Essential assets before first launch

The unmanaged essential-download route can fetch assets required before the app launches. This is a strong promise and needs a tight contract:

- keep the essential set minimal;
- set compressed/uncompressed size values accurately;
- make the app usable if the download is delayed or fails;
- test install, update, restore, offline, and low-storage states;
- do not call a resource “ready” until the app can open and validate it.

An app that requires a huge asset pack before its first useful screen creates a brittle launch contract. Prefer a small essential shell and a clear on-demand path unless the feature truly cannot begin without the asset.

## Models, Metal libraries, and AI content

Background Assets is a delivery mechanism; it does not prove model quality or hardware compatibility.

For a downloaded Core ML or Foundation Models-adjacent asset:

1. identify model/asset version and supported input schema;
2. validate file identity and local availability;
3. load it through the framework’s documented model API;
4. check compute-unit/device support;
5. run representative quality and latency fixtures;
6. keep the previous validated model while the new one is evaluated where feasible;
7. roll back on incompatibility or quality regression.

For a Metal library:

- validate the library can load on the target GPU;
- keep shader/resource layouts versioned;
- preserve a CPU or simpler rendering fallback;
- measure memory, frame time, and thermal behavior.

Do not download Swift code, executable bundles, or arbitrary scripts as if they were ordinary content. Keep executable behavior in the signed app/extension and treat downloaded files as data/resources that the selected framework explicitly supports.

## Localization

Apple’s current localized asset-pack documentation describes language-specific packs for iOS 27 and later and marks relevant APIs as preliminary/beta. Do not assume those localized-pack APIs are available for an iOS 26 target. For iOS 26, use the target’s documented manifest/pack APIs and test the actual SDK availability.

If a future target supports localized packs:

- publish language identifiers using the documented BCP-47 subset;
- inspect resolved/preferred languages;
- call reconciliation deliberately;
- use localized content-access APIs when paths are ambiguous;
- test system-language changes and explicit in-app language selection.

## Liquid Glass download UI

The app owns the resource explanation and progress surface:

- show what the pack enables;
- show current pack version and local validation status;
- keep a primary Continue/Download/Retry action;
- use a compact glass status card or toolbar only when it improves hierarchy;
- do not obscure the feature with a full-screen glass download wall;
- preserve a low-resource fallback;
- announce completion and failure to VoiceOver.

System-managed downloader/extension behavior does not need a custom replica of an Apple system panel. Use native progress and state semantics in the app-owned shell.

## Privacy and resource safety

Background Assets may contain sensitive product content even when it is not user data:

- models can reveal product capability or domain focus;
- localized audio/video may have licensing constraints;
- account-specific content should use a separate authenticated data route;
- a failed download should not expose URLs or signed requests in logs.

Never use the framework to identify a device/user or for advertising measurement. Keep resource URLs, manifest contents, and server credentials out of diagnostics.

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
- [BAHasManagedAssetPacks](https://developer.apple.com/documentation/bundleresources/information-property-list/bahasmanagedassetpacks)
- [BAAppGroupID](https://developer.apple.com/documentation/bundleresources/information-property-list/baappgroupid)
- [BAManifestURL](https://developer.apple.com/documentation/bundleresources/information-property-list/bamanifesturl)
- [Background Assets in the App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi/background-assets)
- [Reducing download and storage demands with localized asset packs](https://developer.apple.com/documentation/backgroundassets/reducing-download-and-storage-demands-with-localized-asset-packs)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
