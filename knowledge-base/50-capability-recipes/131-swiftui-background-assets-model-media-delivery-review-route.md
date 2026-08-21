# SwiftUI Background Assets and model/media delivery capability route

Use this route when an iOS 26 SwiftUI feature needs additional content or an on-device model after installation. It covers pack architecture, downloader targets, local readiness, Core ML compilation/loading, Metal/media validation, SwiftUI state, Liquid Glass controls, fallback, and proof. It does not turn a downloaded file, a model score, or a preview into a verified product capability.

Read the [delivery review](../42-framework-deep-dives/100-swiftui-background-assets-model-media-delivery-review.md), [design guide](../21-design-deep-dives/128-swiftui-background-assets-model-media-delivery-review-design.md), [proof matrix](../60-verification/125-swiftui-background-assets-model-media-delivery-review-proof-matrix.md), and [recipes](../70-code-recipes/143-swiftui-background-assets-model-media-delivery-review-recipes.md). For earlier Background Assets coverage, see the [managed content deep dive](../42-framework-deep-dives/37-background-assets-managed-content-and-model-packs.md) and [content route](60-background-assets-content-route.md).

## Choose the narrowest route

| Outcome | Route | Required ownership |
| --- | --- | --- |
| Small, universal app resource | Bundle it | Main app target and signed resource |
| Large pack Apple manages | Apple-hosted managed Background Assets | App, downloader extension, App Group, pack upload |
| Large pack with self-hosted managed scheduling | Self-hosted managed Background Assets | App, managed downloader extension, App Group, manifest/hosting |
| Custom individual self-hosted files | Unmanaged Background Assets | App, unmanaged downloader extension, App Group, manifest/allowlist |
| Resource required before first useful launch | Unmanaged essential-download policy | Essential size restrictions, minimal fallback, install/update proof |
| Optional language/content variant | Target-supported pack APIs | Availability gate and explicit fallback |
| Downloaded Core ML source model | Delivery plus Core ML compile/load gate | File validation, compile, persistent storage, model contract |
| Downloaded Metal shader library | Delivery plus Metal device/library gate | MTLDevice, library/function/resource validation, fallback |
| Downloaded video/audio/image/3D file | Delivery plus media/renderer gate | Format, codec, color/timing, memory, playback/render proof |

Do not choose Background Assets because a feature needs arbitrary background code. The signed app and its extensions own executable behavior; the resource route owns additional data/content accepted by the selected framework.

## Route map

~~~text
feature outcome
  -> pack or bundle decision
  -> managed/unmanaged decision
  -> Apple-hosted/self-hosted decision
  -> app + extension targets + App Group
  -> manifest/pack policy and size contract
  -> local delivery test
  -> manager/extension state reconciliation
  -> resource identity/integrity/schema validation
  -> Core ML/Metal/media readiness
  -> SwiftUI state and Liquid Glass controls
  -> local AI proposal and user review
  -> fallback, eviction, update, and release evidence
~~~

The route is complete only when the feature can explain and recover from missing, partial, incompatible, stale, and removed resources.

## Step 1: define the resource contract

Before opening Xcode, record:

| Field | Decision |
| --- | --- |
| Feature outcome | What the person wants to accomplish |
| Resource kind | model, shader, video, audio, texture, image, 3D, config |
| Pack ID | Stable app-owned identifier |
| File paths | Explicit allowlisted relative paths |
| Version | Pack/content/schema revision |
| Compatibility | App build, deployment target, device/GPU/model/media requirements |
| Policy | essential, prefetch, or on-demand |
| Size | Compressed download and installed-size estimates |
| Hosting | Apple-hosted, self-hosted managed, or self-hosted unmanaged |
| Validation fixture | Named load/quality/performance fixture |
| Fallback | Bundled, basic, read-only, or unavailable behavior |
| Removal | What can be evicted and what must remain |
| Privacy | What is downloaded, processed, retained, or sent |

Use a stable pack identity and a stable file schema. Do not derive a privileged file path or pack ID from local model output.

## Step 2: choose managed or unmanaged

Managed Background Assets is the default starting point for versioned pack delivery where the system should schedule pack downloads and updates. Use AssetPack, AssetPackManifest, AssetPackManager, and a matching managed downloader extension.

For Apple-hosted managed delivery:

1. Create the Apple-Hosted, Managed Background Download extension template.
2. Add a shared App Group to app and extension targets.
3. Set BAAppGroupID, BAHasManagedAssetPacks, and BAUsesAppleHosting in the app target information property list.
4. Adopt StoreDownloaderExtension as the selected SDK requires.
5. Create and package the managed manifest and packs.
6. Upload pack versions separately to App Store Connect.
7. Record the compatible app build, pack version, content digest, and validation fixture.

For self-hosted managed delivery:

1. Create the Self-Hosted, Managed Background Download extension template.
2. Share the App Group between app and extension.
3. Configure managed asset-pack information property-list values required by the current target.
4. Adopt ManagedDownloaderExtension.
5. Host the manifest and pack files over the product-owned path.
6. Test server outage, rollback, cache, version, and domain behavior.

Use unmanaged Background Assets when the app owns individual download scheduling and file requests. Configure the manifest URL, domain allowlist, initial download restrictions, essential/nonessential allowances, and maximum install-size values from the current unmanaged project guide. Add the unmanaged downloader extension and recover state from the shared App Group after system termination.

Do not mix the route contracts. A managed AssetPackManager call does not substitute for an unmanaged BADownloadManager state machine, and an unmanaged URL download does not prove a managed pack is registered or Apple-hosted.

## Step 3: author pack policy

Package a managed pack with a manifest and a declared download policy. Use:

- essential for the smallest resource truly required by the initial experience;
- prefetch for likely next-use content where opportunistic work is useful;
- on-demand for optional features or large models chosen from inside the app.

Group files by update and validation boundary. Separate:

- configuration from optional media;
- a universal baseline shader from GPU-specific variants;
- the active model from a candidate model;
- a tutorial shell from large tutorial chapters;
- user-created data from replaceable content.

Use the documented ba-package tool to generate a package from a manifest. Upload Apple-hosted packs outside the main app build flow through App Store Connect. A local archive containing a resource is not evidence of the Apple-hosted pack record.

## Step 4: use the manager behind a resource coordinator

AssetPackManager is an actor. Create an app-owned coordinator that:

1. reads the current manifest;
2. resolves only known pack IDs and allowlisted file paths;
3. subscribes to status updates;
4. calls ensureLocalAvailability at a feature boundary;
5. maps manager status into a Sendable app state;
6. retrieves a Data, file descriptor, or URL appropriate for the consumer;
7. closes file descriptors when finished;
8. validates the resource;
9. persists a validated version record;
10. removes replaceable packs on a deliberate storage action.

If the feature can use an older accepted pack while a candidate updates, call the version-tolerant availability route and retain the current record. If the feature truly requires the latest version, require the latest version and present a clear waiting/failure path.

The coordinator must be cancellable and restartable. A canceled SwiftUI task should not publish Ready for a previous request, and a slow status update should not overwrite a newer active version. Associate every operation with a resource ID and a monotonically increasing operation revision.

## Step 5: reconcile extension state

Managed extensions handle system scheduling and are not foreground workers. Unmanaged extensions can be paused or terminated. Persist a small record such as:

~~~text
resourceID
candidateVersion
operationRevision
downloadState
fileURL or app-group handoff reference
expectedDigest
validationState
failureCode
updatedAt
~~~

On app launch or foreground:

1. read the last record;
2. confirm the file or pack still exists;
3. ask the manager or download manager for current state;
4. invalidate records whose identity or digest no longer matches;
5. re-run framework-specific validation when the app build, OS, device, or consumer schema changes;
6. publish the result to SwiftUI.

Never trust a stale extension record without checking the actual resource. Never remove user records because a replaceable pack was evicted.

## Step 6: compile and validate a Core ML asset

For a downloaded Core ML source model:

1. obtain it through the chosen delivery route;
2. check resource identity, version, size, digest, and supported app build;
3. copy or open the local source model from an app-owned validated location;
4. call the asynchronous MLModel.compileModel route off the main actor;
5. persist the compiled result in a versioned directory;
6. load the compiled result with MLModel.load or the documented initializer;
7. inspect modelDescription and available compute devices;
8. validate input/output feature descriptions and expected shapes;
9. run a representative quality, latency, memory, and thermal fixture;
10. promote Ready only after every required check passes.

Keep compilation, model loading, and inference as different states. Core ML’s direct MLModel API is the documented route for dynamically downloaded and compiled models. Serialize access to one model instance on one thread or dispatch queue, or create separate instances for separate queues.

Do not let the model choose an app action. If the output is a candidate title, classification, ranking, or transformation, keep the source input, resource version, output, and correction path available for user review before a typed domain mutation.

## Step 7: validate Metal and media assets

For a Metal library:

1. load the device and determine the supported GPU family/feature path;
2. load the library from the validated URL;
3. check the required function names;
4. check the resource layout and data schema;
5. create a small pipeline or render fixture;
6. measure frame time, memory, and thermal behavior;
7. retain a baseline or disable the effect when validation fails.

For media:

1. inspect container, codec, duration, size, and metadata;
2. validate color space, orientation, sample rate, timing, and pixel formats where relevant;
3. open through AVFoundation, Core Image, VideoToolbox, RealityKit, or the selected consumer;
4. use a bounded preview/playback/render fixture;
5. test interruption, cancellation, memory pressure, and low-power behavior;
6. keep a lower-resolution, text, bundled, or native fallback.

Do not mark a resource ready because its filename has the expected extension. A file can decode and still be too slow, too large, or semantically wrong for the feature.

## Step 8: publish SwiftUI readiness

The view model should present a typed state such as:

~~~text
missing
scheduled
downloading(progress?)
localValidation
preparing
ready
stale
incompatible
failed
evicted
~~~

Map the state to a compact native surface:

- title: user outcome;
- status: actual current phase;
- detail: size/version/why;
- primary control: action that can succeed now;
- fallback: action that works without the resource;
- storage: remove/re-download where appropriate.

Use a Liquid Glass control group only when it improves hierarchy. Keep the feature content accessible under reduced transparency and when the resource is absent. An indeterminate ProgressView is more truthful than a synthetic percentage. Do not let a glass animation imply that background work is still active after a failure.

## Step 9: add bounded local AI

Add an AI route only after the resource is ready:

~~~text
approved resource
-> typed local input
-> bounded inference
-> output schema validation
-> provenance/evaluation record
-> user review
-> deterministic commit
~~~

For a model that produces a proposal, show the input source and model/resource version where the person needs that context. Keep Apply and Discard explicit. If the model is not ready, use the declared fallback; do not silently substitute a remote model or make an unverified capability claim.

Foundation Models, Vision, Natural Language, Speech, or another local framework can be added at this point only when it owns a separate input/output boundary. A downloaded Core ML model is not interchangeable with Apple’s system Foundation Models availability. Verify each framework’s target and device availability separately.

## Step 10: handle update, eviction, and failure

Use a candidate directory and an atomic promotion record:

~~~text
active/v4
candidate/v5
candidate validation
-> promote v5
-> update active record
-> remove v4 only after recovery window
~~~

Cases to test:

- network disappears during download;
- extension is terminated after a completed file arrives;
- device has low storage during model compilation;
- new pack has an incompatible schema;
- new model loads but fails quality threshold;
- shader library lacks a required function;
- media file has an unsupported codec;
- system evicts a removable pack;
- app launches with an old active version and a new manifest;
- user changes language or feature preference;
- user taps Retry repeatedly;
- app returns from background with a stale progress task.

Keep the last validated active resource or deterministic fallback. Do not expose a half-written directory to the consumer.

## Step 11: local and physical testing

Before TestFlight or App Store distribution, use Apple’s local Background Assets testing path with a mock server. Test HTTPS, trusted certificates, device trust, Development Overrides, installation, update, background delivery, and failure. Then repeat the resource path on a physical device with the actual target build.

Minimum physical-device matrix:

| Test | Evidence |
| --- | --- |
| Fresh install | App/extension target and essential policy behave as expected |
| Foreground on-demand request | User action reaches manager/extension and state recovers |
| Background update | System delivery and app reconciliation work |
| Offline after local install | Local model/media/shader route works or fallback appears |
| Low storage | Temporary files and promotion do not corrupt active version |
| App termination/relaunch | State and active resource recover |
| Device/GPU/model variation | Unsupported paths select fallback |
| Accessibility settings | Resource surface remains usable |
| Archive/TestFlight | Signed app, extension, entitlements, pack record, and metadata match |

## Route completion checklist

- [ ] Resource identity, schema, version, policy, and fallback are recorded.
- [ ] Managed/unmanaged architecture is intentional.
- [ ] Apple-hosted/self-hosted ownership is intentional.
- [ ] App, extension, App Group, and information property-list values are verified.
- [ ] Pack manifest and App Store Connect/self-hosted publication are recorded.
- [ ] Local mock-server tests pass.
- [ ] Manager/extension status reconciles after relaunch and termination.
- [ ] File identity, digest, schema, and size are checked.
- [ ] Core ML compile/load/feature/device checks pass where applicable.
- [ ] Metal/media decoder/renderer checks pass where applicable.
- [ ] SwiftUI state distinguishes delivery from readiness.
- [ ] Liquid Glass is functional and accessible, with a non-glass fallback.
- [ ] Local AI output is bounded, reviewable, and provenance-aware.
- [ ] Update, rollback, eviction, low-storage, offline, cancellation, and retry are tested.
- [ ] Physical-device, signed archive, system, TestFlight, and release evidence are captured.

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
