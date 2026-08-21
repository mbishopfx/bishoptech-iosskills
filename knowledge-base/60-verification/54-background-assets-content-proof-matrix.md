# Background Assets content and model-pack proof matrix

Background Assets crosses app and extension targets, managed versus unmanaged architecture, App Groups, manifests, hosting, system scheduling, storage budgets, file handoff, content validation, model/Metal/media readiness, and release distribution. Prove each boundary separately.

Use this matrix with the [Background Assets deep dive](../42-framework-deep-dives/37-background-assets-managed-content-and-model-packs.md), the [capability route](../50-capability-recipes/60-background-assets-content-route.md), the [content and model-pack design guide](../21-design-deep-dives/57-background-assets-content-and-model-pack-design.md), and the [code recipes](../70-code-recipes/72-background-assets-content-recipes.md).

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Framework is available for the target | Current API page and target compile | A source import |
| Architecture is configured | Signed app/extension targets, App Group, Info.plist keys, and matching managed/unmanaged protocol | An Xcode template |
| Pack is published | App Store Connect/self-hosted manifest and version record | A local asset folder |
| System discovers a pack | Physical-device manifest/status evidence | A hard-coded pack ID |
| Pack downloads | Local mock server or TestFlight/App Store/real self-hosted run with download state | A scheduled request |
| Pack is local | Local availability result and file-access evidence | A download-complete callback |
| Pack is feature-ready | Schema, version, device/GPU/model/codec validation | File presence |
| Managed update works | Current/next version, update check, safe switch/rollback | One successful first install |
| Unmanaged download works | Manifest, allowlist, BAURLDownload, manager schedule, finished/failure callbacks | One URLSession download |
| Essential route works | Fresh install/update/offline/low-storage/extension evidence | App launch on a developer machine |
| Extension survives lifecycle | Termination/relaunch/recovery with durable App Group state | Foreground UI |
| Model asset works | Target device model load, input/output schema, quality/latency/thermal fixtures | Model file downloaded |
| Metal asset works | GPU/library/resource validation and frame/thermal fixtures | Library exists locally |
| Localization works | Supported target/API availability, language selection, localized content, fallback | A translated filename |
| Privacy policy is honored | No user/device identification or advertising use, data inventory, logs redacted | Source comments |
| Release is ready | Signed distribution app/extension, App Store Connect pack/version, physical device, fallback, and metadata | Simulator/preview |

## Environment record

| Field | Value |
| --- | --- |
| App target/bundle ID |  |
| Extension target/bundle ID |  |
| Version/build |  |
| SDK/Xcode |  |
| Device model/OS |  |
| Architecture | managed / unmanaged |
| Hosting | Apple / self-hosted |
| App Group |  |
| Manifest URL or App Store Connect asset ID |  |
| Pack identifiers/versions |  |
| Info.plist keys |  |
| Size accounting revision |  |
| Validation/schema revision |  |
| Model/Metal/media fixture |  |
| Fallback mode |  |
| Signed artifact |  |

Do not put private URLs, credentials, signed requests, or user data into the evidence record.

## Configuration matrix

| Test | Expected evidence |
| --- | --- |
| Managed app without matching extension | Build/configuration blocks release or surfaces a clear failure |
| Apple-hosted managed asset | Apple hosting key, StoreKit downloader extension, pack version, App Store Connect record |
| Self-hosted managed asset | Managed downloader extension, manifest/hosting, App Group, domain availability |
| Unmanaged asset | Unmanaged extension, App Group, manifest URL, allowlist, size keys |
| App/extension App Group mismatch | Handoff fails safely; no silent data loss |
| Missing manifest URL | Feature uses fallback; no arbitrary URL |
| Incorrect compressed allowance | Configuration test catches bound mismatch |
| Incorrect install size | Installation test catches uncompressed-size mismatch |
| Domain allowlist too broad | Review/configuration blocks the route |

## Managed pack matrix

| Test | Expected evidence |
| --- | --- |
| First manifest access | Manager actor returns current manifest or explicit error |
| Status updates | Async status state maps to scheduled/downloading/local/failed |
| Ensure local availability | Pack becomes local or typed failure identifies the pack |
| Require latest version false | Old validated pack remains usable during update |
| Require latest version true | Feature waits or reports failure before using old content |
| Update check | New/removed IDs are reconciled |
| Pack removed | App falls back and removes only replaceable resource |
| Content access by path | Allowlisted path returns expected file/data |
| Invalid path | App rejects without probing arbitrary file paths |
| Manager actor cancellation | Task cancellation does not corrupt readiness state |
| Extension not installed | App does not claim managed downloads are reliable |

## Unmanaged download matrix

| Test | Expected evidence |
| --- | --- |
| Install | Extension receives system event and obtains manifest |
| Update | Extension recovers/downloads changed resource |
| Essential asset | Correct compressed/uncompressed budgets and prelaunch behavior |
| Nonessential asset | Scheduled with bounded allowance |
| Domain allowlist | Only intended host is accepted |
| Authentication challenge | Credential handling is explicit and redacted |
| Download finished | Finished file identity/schema/size validated |
| Download failed | Retry/fallback state and no partial publication |
| Download canceled | Resource remains unavailable/old version stays active |
| Extension termination | Durable progress/checkpoint allows safe recovery |
| App Group restart | App can see validated state after relaunch |
| Low storage/offline | No corruption; basic mode remains useful |

## Asset validation matrix

| Resource | Minimum validation |
| --- | --- |
| JSON/config | Version, schema, required keys, bounds, and migration |
| Image/texture | Decode, dimensions, color/format, memory budget |
| Audio | Container/codec, duration, sample rate, license/content policy |
| Video | Container/codec, resolution, playback, storage/thermal budget |
| 3D model | Format, materials, bounds, renderer support, memory |
| Metal library | Library load, shader/resource contract, GPU support |
| Core ML model | Model load, input/output schema, revision, compute units, quality |
| Other supported model file | Framework-specific load, schema, compatibility, privacy |

An asset can be validly downloaded but invalid for the selected device or app build.

## Version and rollback matrix

| Test | Expected evidence |
| --- | --- |
| New compatible pack | Validation passes and feature switches at a safe boundary |
| New incompatible pack | Old validated pack remains active or fallback appears |
| Schema migration | Migration is deterministic and reversible/recorded |
| Model quality regression | Evaluation blocks rollout or rolls back |
| App older than pack | Compatibility policy blocks unsupported combination |
| App newer than pack | Fallback handles missing resource |
| Server removes pack | User-owned data remains; feature state updates |
| Interrupted switch | Active version remains consistent after relaunch |

## Model/AI proof matrix

| Claim | Required evidence |
| --- | --- |
| Model pack is available | Local file and AssetPack/managed status |
| Model loads | Target device/framework load result |
| Model supports device | Availability/compute-unit check |
| Model is accurate enough | Representative quality fixture and acceptance threshold |
| Model is fast enough | Physical latency/memory/thermal measurement |
| AI proposal is reviewable | Source input, pack/model version, output, correction, apply/discard |
| AI can run offline | Physical offline run with model local |
| AI does not expose content | Prompt/input/data-flow audit and redacted diagnostics |
| Model update is safe | Before/after fixture and rollback behavior |

Do not claim “on-device AI support” from a completed asset download.

## Localization matrix

For a target that supports localized packs:

| Test | Expected evidence |
| --- | --- |
| System language | Correct resolved language/pack |
| App language override | Explicit override and reconciliation |
| Missing translation | Documented fallback |
| Same file path across languages | Language-specific content access |
| Language change | Active pack remains usable until replacement is ready |
| Storage cleanup | Removed languages do not delete user records |

For an iOS 26 target, record whether the localized-pack API is unavailable and prove the fallback rather than silently shipping an assumed iOS 27 route.

## Accessibility and Liquid Glass evidence

Run the resource task with:

- VoiceOver status/action announcements;
- Voice Control download/retry/remove/basic-mode activation;
- Switch Control fallback;
- Dynamic Type and long resource names;
- reduced motion;
- reduced transparency/increased contrast;
- external keyboard where supported;
- localized size/date/error text.

Capture the app-owned resource shell separately from downloader-extension/system behavior. A glass card with a simulated progress value is not evidence of system scheduling or completed-file validation.

## Release packet

Include:

1. Signed app and extension artifacts.
2. App Group and Info.plist dump.
3. Managed/unmanaged protocol and hosting record.
4. Manifest and pack version/content hashes.
5. App Store Connect asset-pack record where Apple hosting is used.
6. Local mock-server test report.
7. Physical install/update/offline/low-storage/termination results.
8. Asset-specific validation and rollback results.
9. Model/Metal/media performance and quality fixtures.
10. Localization/accessibility report.
11. Privacy/resource-use review.
12. Fallback and incident rollback plan.

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
- [Reducing download and storage demands with localized asset packs](https://developer.apple.com/documentation/backgroundassets/reducing-download-and-storage-demands-with-localized-asset-packs)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
