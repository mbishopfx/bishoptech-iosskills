# SwiftUI Background Assets and on-device model/media delivery review

Background Assets is the system-managed delivery boundary for additional app resources. In an iOS 26 app, that resource might be a tutorial video, a texture set, a Metal shader library, a Core ML source model, or another static file that a supported framework can consume. SwiftUI owns the explanation of readiness and the user’s choices; Background Assets owns pack discovery and delivery; Core ML, Metal, AVFoundation, Core Image, or another consumer owns resource validation.

This review extends the existing [Background Assets deep dive](37-background-assets-managed-content-and-model-packs.md), [content route](../50-capability-recipes/60-background-assets-content-route.md), [design guide](../21-design-deep-dives/57-background-assets-content-and-model-pack-design.md), [proof matrix](../60-verification/54-background-assets-content-proof-matrix.md), and [code recipes](../70-code-recipes/72-background-assets-content-recipes.md). The distinct question here is: how does a SwiftUI feature move from a declared pack to a truthful, accessible, local-AI-ready, resource-safe state?

## The readiness pipeline

Treat delivery as a pipeline with separate owners and separate evidence:

~~~text
target and deployment gate
-> app/extension capability and App Group
-> manifest and pack policy
-> Apple-hosted or self-hosted publication
-> system scheduling and downloader lifecycle
-> local availability
-> file identity/integrity/version check
-> framework-specific load and compatibility check
-> model/GPU/media quality and performance check
-> SwiftUI readiness state
-> optional local-AI proposal
-> user review and deterministic commit
-> update, eviction, rollback, and release proof
~~~

Do not collapse these states into a Boolean called isDownloaded. A file can be local but stale, malformed, incompatible with the current app schema, unsupported by the device GPU, too large for the current thermal budget, or unacceptable for the feature’s quality threshold.

| State | Owner | Meaning |
| --- | --- | --- |
| declared | app configuration | The feature knows the resource identity and policy. |
| discoverable | Background Assets | The manifest or managed catalog exposes a pack version. |
| scheduled | system/downloader | The system has accepted work; timing is not guaranteed. |
| downloading | system/downloader | The system reports a current download state. |
| local | AssetPackManager or download handoff | The required bytes are available to the app. |
| integrity-checked | app resource layer | Identity, digest, size, and expected file layout passed. |
| compiling/loading | Core ML, Metal, media, or consumer framework | The resource is being prepared for actual use. |
| compatible | consumer validator | Input/output, shader/GPU, codec, schema, and deployment checks passed. |
| ready | app feature | The feature can use the validated resource on this device. |
| stale | app policy | A newer or required version exists, or the current one no longer matches. |
| unavailable | app/system | The resource is missing, evicted, unsupported, denied, or failed. |
| fallback | product | A deterministic lower-resource or bundled path remains available. |

## Managed versus unmanaged delivery

Choose the architecture before writing the SwiftUI view.

| Question | Managed Background Assets | Unmanaged Background Assets |
| --- | --- | --- |
| Who chooses pack-level scheduling? | The system, using manifest policy and the managed extension | The app/extension, using downloads returned to the system |
| Main Swift surface | AssetPack, AssetPackManifest, AssetPackManager actor | BADownloadManager, BADownload, BAURLDownload, downloader extension |
| Apple hosting | Supported through Managed Background Assets and StoreKit’s StoreDownloaderExtension | Not the Apple-hosted route |
| Self hosting | Supported with ManagedDownloaderExtension | Required |
| Best fit | Versioned packs, system scheduling, App Store Connect delivery, large static resources | Custom self-hosted download policy and individual resource operations |
| Main failure boundary | Missing/mismatched managed extension or pack configuration | Manifest, allowlist, size restrictions, extension lifetime, or download handoff |

The first reference to AssetPackManager opts the app into automatic managed asset-pack behavior. Apple documents that the corresponding managed extension protocol must also be present: StoreKit’s StoreDownloaderExtension for Apple-hosted packs or ManagedDownloaderExtension for self-hosted managed packs. Do not add the manager to an app target and assume that a generic background extension is equivalent.

Unmanaged Background Assets has a different contract. The system can obtain the manifest, launch the extension, and terminate or pause it. The extension must reconstruct durable state from the shared App Group, schedule only allowed resources, and validate completed files before the app promotes them. A URLSession download that happens in the foreground is not proof of the unmanaged extension route.

## Apple-hosted managed packs

Apple-hosted Background Assets is useful when the product wants Apple to host additional app resources and wants pack versions to be managed outside the main app build. Apple documents support for resources such as texture files, machine-learning models, Metal shader libraries, and videos, with a current limit of up to 200 GB of compressed assets for supported Apple-hosted distribution. The route is for additional app assets; do not use it to identify a user or device or to perform advertising or advertising measurement.

The target configuration has several coupled pieces:

1. Add an Application Extension target from Xcode’s Background Download template, selecting Apple-Hosted, Managed.
2. Add the same App Group to the app target and downloader extension target.
3. Add BAAppGroupID, BAHasManagedAssetPacks, and BAUsesAppleHosting to the app’s information property list.
4. Omit unrelated Background Assets information-property-list keys for the Apple-hosted configuration.
5. Adopt StoreDownloaderExtension in the extension target as required by the selected SDK/template.
6. Create a manifest and package managed packs with the documented ba-package tool.
7. Upload asset packs separately through App Store Connect and record the pack version associated with the app compatibility range.
8. Let AssetPackManager and the extension provide the system-managed lifecycle.

The default StoreDownloaderExtension/managed implementation handles scheduling, background updates, compression, and other system behavior. The documented shouldDownload(_:) hook can filter candidate packs when product policy requires it. Keep the filter small and deterministic: entitlement, current feature choice, app compatibility, network/storage policy, and resource identity belong in app-owned policy; arbitrary AI output does not.

## Pack authoring and policy

Managed packs begin with a manifest. A practical manifest entry should have:

- a stable assetPackID;
- a human-readable purpose owned by the app;
- a download policy of essential, prefetch, or on-demand;
- file selectors for the resource group;
- target platforms;
- a content/schema revision;
- an app-build compatibility range;
- a validation fixture identifier;
- a fallback identifier;
- an approximate compressed and installed-size record.

Essential means the app’s launch or installation path depends on the resource. Prefetch means the system may obtain it ahead of likely use. On-demand means the app requests it at a deliberate feature boundary. Keep essential packs small. A broken or unavailable essential pack must not strand the person at a glass loading screen with no useful fallback.

Group resources by lifecycle, not just by file type. A model used by one optional feature should not force every person to download a video library. A shader library that has a different device support matrix should not be inseparable from a universally supported configuration file. A pack boundary is a storage, update, and rollback boundary.

The older On-Demand Resources route uses NSBundleResourceRequest and tags. Apple now marks NSBundleResourceRequest deprecated and points developers to Background Assets. For an iOS 26 project, treat Background Assets as the primary new delivery route and keep an older ODR page only for migration or a target that explicitly requires it.

## AssetPackManager actor and local availability

AssetPackManager is an actor. Keep its calls behind an async resource coordinator rather than invoking it in a view body. The manager can expose a manifest, status updates, local status, local-availability checks, content access, and removal. Its current availability methods can require the latest version or allow a previously validated local version to remain active while a newer pack is being obtained.

The critical boundary is ensureLocalAvailability. A successful call means the requested pack is locally available under the manager’s contract. It does not mean:

- a model compiles or accepts the app’s feature schema;
- a Metal library loads on the current GPU;
- a media asset decodes with the desired codec and color pipeline;
- a pack’s content is licensed or semantically appropriate;
- a local AI result is accurate or safe to commit;
- the system will keep the pack forever;
- the current SwiftUI state has observed the latest update.

Use the content accessor that matches the consumer. Small bounded metadata can be read as Data. Large content can use a file descriptor or URL when the API supports it. Apple explicitly places responsibility for closing a returned file descriptor on the app. For model compilation and media APIs that require a URL, preserve the resource as an app-owned validated URL and do not pass a user-controlled arbitrary relative path into the pack.

The manager can remove packs, and Apple’s documentation says the system does not automatically remove asset packs merely because the app is installed. Removal is therefore part of product storage policy. Remove only replaceable resources, keep user-authored data separate, and make re-download behavior explicit. Calling ensureLocalAvailability again is the documented redownload route after removal.

## Downloader and process lifecycle

The managed downloader extension is a system integration point, not an always-running worker. For Apple-hosted packs, StoreDownloaderExtension inherits the managed behavior; for self-hosted managed packs, ManagedDownloaderExtension supplies default implementations and allows the optional shouldDownload filter. Apple warns against implementing inherited downloader requirements that the protocol already supplies, except for the documented optional customization point.

The unmanaged extension has more lifecycle responsibility:

- the system can launch it around install, update, or periodic background events;
- the system can pause or terminate it;
- a manifest URL and domain allowlist constrain where resources may come from;
- initial download restrictions and maximum install-size keys constrain essential and nonessential work;
- completed-file handoff must be validated and persisted in the shared App Group;
- extension termination must leave a recoverable checkpoint;
- repeated launches must be idempotent.

Do not render extension callbacks directly into SwiftUI. Persist a small, versioned resource record in an app group or app-owned store, then have the app reconcile that record with actual file existence and framework readiness when it launches or returns to the foreground.

## Core ML model delivery

Core ML can run models on the device using available CPU, GPU, and Neural Engine resources. A bundled model is the simplest route: Xcode can compile it and generate a wrapper. A model delivered after installation takes a longer route:

~~~text
download .mlmodel or supported model asset
-> verify source identity, version, size, and digest
-> compile locally with MLModel.compileModel(at:)
-> move compiled output to a persistent app-owned directory
-> load with MLModel.load or MLModel(contentsOf:configuration:)
-> inspect modelDescription and available compute devices
-> validate feature names/types/shapes/image constraints
-> run representative quality/latency/memory/thermal fixtures
-> publish ready state
~~~

Apple’s Core ML documentation says an app that downloads and compiles a model on the user’s device must use the MLModel class directly for predictions. Compilation can be time-consuming, so it belongs off the main actor with cancellation and a visible compiling state. Keep the temporary compiled result separate from the active model directory, promote atomically only after validation, and leave the previously accepted model usable while a candidate is evaluated where possible.

The app must serialize use of one MLModel instance on one thread or dispatch queue, or create separate instances for separate queues. This is an execution-ownership rule, not merely a SwiftUI state rule. A model object stored in an Observable view model still needs a deliberate actor/queue boundary.

Inspect the loaded model’s description before publishing readiness. Validate the input/output feature contract, model revision, expected image or array shapes, supported operations, and chosen MLModelConfiguration/MLComputeUnits policy. Inspect available compute devices when hardware policy matters, but do not treat the existence of a compute device as proof of acceptable accuracy, latency, memory, or thermal behavior.

Keep model versions and model behavior separate. The app may know that a model is version 4 and can load it successfully while having no evidence that version 4 preserves the quality threshold of version 3. Evaluation fixtures and rollback rules belong after load.

## Metal, Core Image, and media asset delivery

The same distinction applies to GPU and media assets:

| Asset | Delivery evidence | Feature-readiness evidence |
| --- | --- | --- |
| Metal shader library | file exists and has expected identity | library loads, required functions exist, resource layout matches, device supports the path, fallback works |
| Core Image filter/configuration | file parses and has expected schema | filter graph renders with expected extent/color/alpha behavior and bounded memory |
| Texture/image set | files exist | decode, dimensions, color space, pixel format, memory budget, and renderer support pass |
| Video/audio | file exists | AVAsset metadata, codec/format, duration, playback/export path, license/content policy, and energy budget pass |
| 3D asset | package exists | RealityKit/Model I/O/SceneKit loader, materials, bounds, animations, and device memory pass |
| VideoToolbox input | sample file exists | format description, pixel planes, timing, orientation, compression/decompression, and downstream ownership pass |

Never let a model or remote manifest choose an arbitrary shader function, executable payload, file path, or renderer command. The signed app owns the code and an allowlisted resource schema owns the data. Downloaded files remain data/resources unless the selected Apple framework explicitly documents how to load them.

For Metal, validate the MTLDevice and supported GPU family before selecting a library or shader variant. For media, retain pixel-format, color-space, orientation, timing, and source provenance alongside the file. For Core Image, treat lazy image graphs and CIContext ownership as runtime concerns rather than proof that a file can render. For all three, measure the real target device, not only the simulator or a preview.

## SwiftUI readiness and local AI

SwiftUI should expose a typed feature state, not a raw downloader state:

~~~text
unavailable(reason)
available-but-not-installed(size)
downloading(progress?)
local-validating(version)
compiling-or-loading(version)
ready(version, capabilitySummary)
stale(activeVersion, candidateVersion)
failed(retryable, fallback)
evicted(reinstallAction)
~~~

Progress is optional. Some system-managed status updates do not provide a meaningful user-facing percentage, and a fabricated percentage is worse than honest indeterminate progress. Show what the resource enables, current version/size when known, and the next action. Use Continue, Download, Retry, Use Basic Mode, Remove Download, or Keep Current Version according to the actual state.

If a local model produces a proposal, keep this boundary:

~~~text
validated local resource
-> bounded input
-> deterministic/model output
-> source/version/provenance record
-> user review
-> typed domain mutation
~~~

“Ready” means the app has validated the resource for this feature. It does not mean that a model output is true, that an image classification identifies a person, or that a generated recommendation should be applied automatically. A deterministic fallback may be a bundled model, a simpler CPU path, rule-based behavior, an export-only mode, or a read-only explanation.

## Liquid Glass resource surfaces

Use Liquid Glass as a functional hierarchy layer around resource controls, not as a decorative download simulator. A native resource surface can contain:

- a title naming the feature the pack unlocks;
- a concise status label such as Not Installed, Downloading, Preparing, Ready, or Basic Mode;
- a progress indicator only when the system/app has meaningful progress;
- a size/version disclosure;
- a primary action;
- a secondary details or storage action;
- a fallback action that remains visible when AI/GPU/media capability is unavailable.

Keep the glass region compact and content-aware. Do not rebuild system settings or App Store panels inside the app. The app should explain its own pack and its own validation result; system scheduling remains a system behavior. Use standard SwiftUI controls and current Liquid Glass adoption guidance, then test reduced transparency, increased contrast, Dynamic Type, VoiceOver, Voice Control, Switch Control, keyboard, pointer, and reduced motion.

For a feature that uses a model, distinguish “Model installed” from “AI result accepted.” For a feature that uses a media pack, distinguish “Media downloaded” from “Playback available on this device.” For a feature that uses a shader, distinguish “Renderer resource available” from “GPU effect enabled.” These labels prevent a polished glass card from making an unverified capability claim.

## Privacy, storage, network, and energy

Background Assets is still a resource-delivery contract. It does not make the app’s content private by itself, and on-device execution is not a complete privacy promise. Record:

- what resource is downloaded and from which approved hosting path;
- whether the resource contains licensed or sensitive product content;
- whether user input is ever included in a pack request;
- whether local AI inputs remain on device;
- what logs contain, and whether URLs, tokens, or prompts are redacted;
- what the person can remove;
- what happens after eviction, low storage, offline mode, or account change.

System scheduling is opportunistic. Background work can be delayed by network conditions, power policy, Low Power Mode, storage pressure, and process lifetime. Do not promise an exact completion time. Coalesce requests, use small essential packs, avoid duplicate model copies, delete temporary compilation artifacts, and measure peak storage rather than only compressed download size.

The feature should remain useful during a partial download or interrupted compile. Preserve a validated active version until a candidate is ready. Never publish a directory while it is being replaced. Use a temporary directory plus an atomic move/record update, and recover by selecting the last complete validated record after relaunch.

## iOS 26 availability boundary

Apple’s current localized asset-pack article describes newer language-specific APIs and identifies newer availability/beta boundaries. Do not use those APIs as if they were an iOS 26 baseline. For an iOS 26 target, build around the managed/unmanaged pack APIs documented for that deployment target, then use explicit availability checks for any newer localized route.

Likewise, a current documentation page can expose symbols or overloads that are unavailable for the app’s minimum deployment target. Record the SDK and deployment target in the route worksheet, check the generated interface, and compile the named app target. A source link is evidence of documentation, not evidence that a project target can call the symbol.

## Proof boundary

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| Manifest/package | Pack structure and declared policy | Device delivery or feature readiness |
| App Group and Info.plist dump | Target configuration values | Correct extension lifecycle |
| Local mock-server run | Testable managed/unmanaged delivery path | Apple-hosted App Store distribution |
| AssetPackManager status | System/local pack state | Model quality or GPU compatibility |
| File hash/schema check | Resource identity and structure | Framework execution |
| Core ML load/compile | Model can be prepared by that device/framework | Accuracy, privacy, or product suitability |
| Metal/media validation | Asset works on one tested hardware/input matrix | Universal device support |
| SwiftUI preview/screenshot | Information hierarchy and visual state | Real download, accessibility, or system scheduling |
| Simulator run | Some app logic and UI behavior | Camera/GPU/Neural Engine/extension/device proof |
| Signed physical-device run | Target artifact and selected hardware path | App Store/TestFlight rollout |
| App Store Connect asset record | Distribution record | Successful user install/update or quality |

The release packet should tie together the app build, extension build, pack ID/version, manifest revision, file digest, validation fixture, device/OS, fallback result, accessibility run, storage/network tests, and App Store Connect record. Keep this packet distinct from screenshots and previews.

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
- [BAURLDownload](https://developer.apple.com/documentation/backgroundassets/baurldownload)
- [BADownloadManager](https://developer.apple.com/documentation/backgroundassets/badownloadmanager)
- [NSBundleResourceRequest](https://developer.apple.com/documentation/foundation/nsbundleresourcerequest)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelAsset](https://developer.apple.com/documentation/coreml/mlmodelasset)
- [Compiling a model on the user’s device](https://developer.apple.com/documentation/coreml/downloading-and-compiling-a-model-on-the-user-s-device)
- [Reducing the size of your Core ML app](https://developer.apple.com/documentation/coreml/reducing-the-size-of-your-core-ml-app)
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
