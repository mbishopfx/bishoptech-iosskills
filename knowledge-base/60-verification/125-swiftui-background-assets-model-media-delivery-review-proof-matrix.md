# SwiftUI Background Assets and model/media delivery proof matrix

This matrix proves the boundaries between a declared resource, system delivery, local file state, framework readiness, SwiftUI presentation, local AI behavior, and release distribution. Use it with the [delivery review](../42-framework-deep-dives/100-swiftui-background-assets-model-media-delivery-review.md), [design guide](../21-design-deep-dives/128-swiftui-background-assets-model-media-delivery-review-design.md), [capability route](../50-capability-recipes/131-swiftui-background-assets-model-media-delivery-review-route.md), and [recipes](../70-code-recipes/143-swiftui-background-assets-model-media-delivery-review-recipes.md).

A resource file, progress callback, model load, simulator run, or polished Liquid Glass card is useful evidence for one boundary only. Do not promote it into system scheduling, device support, AI quality, privacy, accessibility, or release proof without the matching test.

## Evidence levels

| Level | Evidence | Boundary |
| --- | --- | --- |
| L0 | Official API page and current SDK availability | Documentation and version awareness |
| L1 | Source/manifest/package/configuration inspection | Declared resource and target contract |
| L2 | Named-target compile and unit/fixture tests | App-owned logic and schema behavior |
| L3 | Local mock-server and extension run | Background Assets delivery and lifecycle |
| L4 | Signed physical-device run | Hardware, storage, network, process, model/media, and accessibility behavior |
| L5 | System/distribution run | App Group, extension, App Store Connect, TestFlight, and system surfaces |
| L6 | Release packet and rollout observation | Repeatable delivery, rollback, support, and production readiness |

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Background Assets is available for the target | Current Apple page, deployment target, named-target compile | Importing the framework |
| Architecture is managed | AssetPack/manifest, matching managed extension, capability/configuration inspection | A downloader extension with an arbitrary name |
| Apple hosting is configured | StoreDownloaderExtension, App Group, BAUsesAppleHosting, pack upload record | Local pack files |
| Self-hosted managed route is configured | ManagedDownloaderExtension, hosting/manifest, App Group, managed keys | A foreground URLSession |
| Unmanaged route is configured | Unmanaged extension, manifest URL, allowlist, size restrictions, App Group | A raw HTTP request |
| Pack is declared correctly | Manifest, assetPackID, policy, selectors, platform, size/revision record | A folder named like the pack |
| Pack is published | App Store Connect asset-pack version or self-hosted manifest/pack endpoint | A local archive |
| System discovers the pack | Device manifest/status evidence | A hard-coded pack ID |
| Pack is scheduled | System/downloader status or extension evidence | A call to a scheduling API |
| Pack is local | ensureLocalAvailability result or finished-file handoff plus file inspection | A scheduled download |
| File identity is valid | Digest, size, version, path, and schema validation | File extension alone |
| File is framework-ready | Core ML/Metal/media consumer load and compatibility fixture | File existence or URL |
| Feature is ready | Consumer validation plus app-owned readiness record | Download complete |
| SwiftUI state is truthful | UI/state tests for missing, downloading, preparing, ready, stale, failed, and fallback | One screenshot |
| Progress is truthful | Status sequence and known progress source | A fabricated percentage |
| Core ML model compiles | Physical target MLModel compile evidence | A source model on disk |
| Core ML model loads | MLModel load result and modelDescription record | Compile result alone |
| Core ML model supports input | Feature names/types/shapes/image constraints fixture | Model version string |
| Core ML compute path is acceptable | Device/compute inspection plus latency/memory/thermal fixture | availableComputeDevices alone |
| Model quality is acceptable | Representative evaluation fixture and acceptance threshold | Model load or confidence score |
| Metal library is usable | MTLDevice/library/function/resource-layout fixture | Shader library file |
| Media is usable | Codec/container/color/timing/render/playback fixture | AVAsset URL |
| AI output is reviewable | Source/version/output/provenance/correction/apply-discard fixture | Model output displayed |
| Offline path works | Physical device with network unavailable and resource local | “On-device” copy |
| Eviction/re-download works | Remove, relaunch, fallback, and ensure-local-availability recovery | Delete button in UI |
| Update is safe | Candidate validation, active-version preservation, promotion/rollback | One successful update |
| Privacy behavior matches copy | Data-flow inventory, redacted logs, network capture where permitted | Privacy sentence in UI |
| Accessibility works | VoiceOver, Dynamic Type, contrast/transparency, motion, Voice Control, Switch Control, keyboard/pointer task runs | Accessibility modifier presence |
| Release is ready | Signed app/extension, entitlements, App Store Connect record, physical run, fallback, metadata | Archive success |

## Configuration packet

Record one row for every feature resource:

| Field | Value |
| --- | --- |
| App target/bundle ID |  |
| Downloader extension target/bundle ID |  |
| Deployment target and SDK/Xcode |  |
| Architecture | managed / unmanaged |
| Hosting | Apple-hosted / self-hosted |
| App Group |  |
| Pack ID and version |  |
| Manifest revision/digest |  |
| File paths and digests |  |
| Policy | essential / prefetch / on-demand |
| Compressed size |  |
| Installed-size estimate |  |
| Info.plist keys |  |
| Managed/unmanaged protocol |  |
| Consumer framework | Core ML / Metal / AVFoundation / Core Image / other |
| Validation/schema revision |  |
| Device/GPU/media/model matrix |  |
| Fallback |  |
| Removal/rollback policy |  |
| Privacy/data-flow note |  |
| App build accepted |  |

Keep signed URLs, credentials, tokens, user data, and raw prompts out of the packet. Use redacted identifiers and store sensitive evidence in the approved secure location.

## Target and capability checks

| Check | Evidence to capture | Failure handling |
| --- | --- | --- |
| App target includes Background Assets | Build settings/linked framework and target compile | Remove unsupported route or gate availability |
| Apple-hosted extension | Extension type, StoreDownloaderExtension, StoreKit linkage | Recreate matching template/configuration |
| Self-hosted managed extension | ManagedDownloaderExtension and manifest route | Do not invoke manager until pairing is fixed |
| Unmanaged extension | BADownloaderExtension route and App Group | Fallback to foreground or bundled content |
| App Group match | Signed app and extension entitlements | Keep app state local until handoff is repaired |
| BAHasManagedAssetPacks | Signed Info.plist | Fix managed configuration |
| BAUsesAppleHosting | Signed Info.plist for Apple hosting | Do not claim Apple-hosted delivery |
| BAAppGroupID | Signed Info.plist and matching entitlement | Stop managed/unmanaged handoff |
| BAManifestURL/allowlist | Signed unmanaged Info.plist | Reject unapproved host or manifest |
| Essential/maximum size values | Configuration and pack-size comparison | Reduce essential pack or reject install policy |
| Deployment availability | Generated interface, availability checks, named-target compile | Use an iOS 26-compatible fallback |

## Managed pack tests

| Test | Expected result |
| --- | --- |
| First manager reference | Matching managed extension is present; no programmer-error route |
| Manifest read | Current pack IDs and policies are visible or a typed failure appears |
| Status observation | SwiftUI receives a cancellable, revision-aware status |
| Essential pack | Minimal installation path works or fallback is usable |
| Prefetch pack | Feature remains usable if prefetch is delayed |
| On-demand pack | User action requests only the selected pack |
| ensureLocalAvailability | Pack is local or a typed error identifies the failure |
| requireLatestVersion false | Last validated version remains usable during update |
| requireLatestVersion true | Feature waits/fails clearly rather than silently using stale content |
| URL/Data access | Consumer receives an allowlisted path/value |
| File descriptor access | Descriptor is closed after use |
| Remove | Replaceable resource is removed without user-data loss |
| Re-download | ensureLocalAvailability restores the resource |
| Status revision | Old status cannot overwrite newer candidate/active state |
| Manager cancellation | Cancellation leaves active version and record consistent |

## Unmanaged extension tests

| Test | Expected result |
| --- | --- |
| Install/update event | Extension reads manifest and schedules within policy |
| Manifest unavailable | Extension persists a retryable failure and app fallback |
| Domain restriction | Only the intended host is accepted |
| Essential allowance | Compressed download and install-size limits are accurate |
| Nonessential allowance | Optional work is bounded and deferrable |
| Download authentication | Challenge handling is explicit and logs are redacted |
| Completed file | Identity, digest, schema, size, and path are validated |
| Partial file | It is not promoted to the active resource |
| Extension termination | Durable checkpoint permits safe re-entry |
| Repeated launch | Scheduling and promotion are idempotent |
| App Group handoff | App reconciles actual file state after relaunch |
| Offline/low storage | Active version or basic path survives |

## Core ML model matrix

| Test | Expected evidence |
| --- | --- |
| Source model identity | Expected file type, digest, version, size, app compatibility |
| Compile | MLModel.compileModel asynchronous result on target device |
| Persistence | Compiled result moved from temporary location to versioned app-owned directory |
| Load | MLModel.load or initializer returns a model |
| Description | modelDescription matches expected feature contract |
| Input validation | Names, types, shapes, image constraints, and units match |
| Output validation | Expected output names/types and bounded values |
| Compute policy | Configuration and available compute devices recorded |
| Queue ownership | One model instance is serialized or separate instances are used |
| Cold/warm latency | Representative physical-device measurements |
| Memory/thermal | Peak memory, energy, and thermal observations |
| Quality | Dataset/fixture and threshold tied to model version |
| Candidate rollback | Failed model remains inactive and active model/fallback survives |
| Offline | Local resource runs without network where promised |
| User data | Input retention and diagnostic redaction are verified |

Loading a model proves a framework boundary. It does not prove quality, safety, privacy, or product suitability.

## Metal and media matrix

| Resource | Required tests |
| --- | --- |
| Metal library | MTLDevice support, library load, function lookup, resource layout, pipeline creation |
| Shader variant | GPU family/feature selection, fallback, frame-time and thermal fixture |
| Texture/image | Decode, dimensions, color space, alpha/pixel format, memory budget |
| Core Image graph | CIContext/graph render, extent/color/alpha, cancellation/memory |
| Video | Container/codec, AVAsset metadata, playback/seek, interruption, energy |
| Audio | Container/codec, duration/sample rate, route/interruption, playback |
| VideoToolbox | Format description, planes, timing, orientation, session, ownership |
| 3D asset | Loader, materials, bounds, animation, renderer support, memory |
| Fallback | Baseline rendering/playback exists for unsupported or failed asset |

Run the matrix on at least one representative older/low-resource device and one target device class relevant to the feature. Expand the matrix when the resource chooses GPU/model/media variants.

## SwiftUI, Liquid Glass, and accessibility matrix

| State | UI evidence |
| --- | --- |
| Not installed | Purpose, size, Download, and fallback are visible |
| Downloading | Actual status or honest indeterminate state; no false completion |
| Preparing | Compilation/load is distinct from bytes downloaded |
| Ready | Resource version and capability summary are accurate |
| Stale | Active version remains visible; update choice is clear |
| Failed | Reason and Retry/Basic Mode path are actionable |
| Incompatible | Device/framework reason and fallback are available |
| Evicted | Re-download and preserved user data are clear |

Run the same task with:

- VoiceOver;
- Dynamic Type at accessibility sizes;
- increased contrast and reduced transparency;
- Reduce Motion;
- Voice Control;
- Switch Control;
- external keyboard;
- pointer or trackpad on iPadOS;
- localization with long resource names, byte sizes, dates, and errors.

Capture semantic labels and actions, not only screenshots. Verify that a glass surface does not reduce contrast or hide the fallback.

## Network, energy, storage, and privacy matrix

| Scenario | Required result |
| --- | --- |
| Wi-Fi available | Optional/prefetch behavior matches documented product policy |
| Cellular only | Policy is disclosed/enforced if the app makes that choice |
| Offline | Active local resource or deterministic fallback |
| Network interruption | No half-published file; retry/recovery record |
| Low Power Mode | Feature remains safe; no exact background timing promise |
| Low storage | Temporary compile/download cleanup and active version preservation |
| App termination | Reconciliation succeeds after relaunch |
| Pack eviction | User data survives and re-download works |
| Account/authorization change | Resource entitlement/data boundary is explicit |
| Sensitive inputs | No unintended request/log/resource disclosure |
| Logs | URLs, tokens, prompts, user content, and device IDs are redacted |
| Removal | User understands what is removed and what remains |

## Local, physical, signed, and release packet

The minimum packet contains:

1. Official source and deployment-target record.
2. App/extension target configuration and signed entitlements.
3. Manifest, pack ID/version, file digest, policy, and size record.
4. Local mock-server results.
5. Device install/update/offline/low-storage/termination results.
6. Framework-specific model/GPU/media validation output.
7. SwiftUI accessibility and alternate-input task results.
8. AI evaluation/provenance/review record where applicable.
9. Fallback, rollback, eviction, and re-download results.
10. Archive/TestFlight/App Store Connect asset-pack record.
11. Redacted privacy and data-flow review.
12. Support/incident route for pack rollback or server failure.

The packet should identify which claims remain unproved. A release checklist that says “asset downloaded” without model, GPU, media, accessibility, privacy, and fallback evidence is incomplete.

## Sources

- [Background Assets](https://developer.apple.com/documentation/backgroundassets)
- [Creating managed asset packs](https://developer.apple.com/documentation/backgroundassets/creating-managed-asset-packs)
- [Downloading Apple-hosted asset packs](https://developer.apple.com/documentation/backgroundassets/downloading-apple-hosted-asset-packs)
- [Testing asset packs locally](https://developer.apple.com/documentation/backgroundassets/testing-asset-packs-locally)
- [Configuring an unmanaged Background Assets project](https://developer.apple.com/documentation/backgroundassets/configuring-an-unmanaged-background-assets-project)
- [Downloading essential assets in the background](https://developer.apple.com/documentation/backgroundassets/downloading-essential-assets-in-the-background)
- [AssetPackManager](https://developer.apple.com/documentation/backgroundassets/assetpackmanager)
- [ManagedDownloaderExtension](https://developer.apple.com/documentation/backgroundassets/manageddownloaderextension)
- [StoreDownloaderExtension](https://developer.apple.com/documentation/storekit/storedownloaderextension)
- [BADownloadManager](https://developer.apple.com/documentation/backgroundassets/badownloadmanager)
- [BAURLDownload](https://developer.apple.com/documentation/backgroundassets/baurldownload)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelAsset](https://developer.apple.com/documentation/coreml/mlmodelasset)
- [Compiling a model on the user’s device](https://developer.apple.com/documentation/coreml/downloading-and-compiling-a-model-on-the-user-s-device)
- [Metal](https://developer.apple.com/documentation/metal)
- [Metal capabilities](https://developer.apple.com/metal/capabilities/)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [VideoToolbox](https://developer.apple.com/documentation/videotoolbox)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Overview of Apple-hosted Background Assets](https://developer.apple.com/help/app-store-connect/manage-asset-packs/overview-of-apple-hosted-background-assets/)
