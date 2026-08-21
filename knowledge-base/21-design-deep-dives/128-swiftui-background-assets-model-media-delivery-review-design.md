# SwiftUI Background Assets and model/media readiness design

The resource screen is not a download dashboard. It is the native explanation of what a person can do now, what additional resource would unlock, what the device is preparing, and what remains available when delivery or local AI is unavailable.

Use this guide with the [Background Assets and model/media delivery review](../42-framework-deep-dives/100-swiftui-background-assets-model-media-delivery-review.md), the [capability route](../50-capability-recipes/131-swiftui-background-assets-model-media-delivery-review-route.md), the [proof matrix](../60-verification/125-swiftui-background-assets-model-media-delivery-review-proof-matrix.md), and the [recipes](../70-code-recipes/143-swiftui-background-assets-model-media-delivery-review-recipes.md). It supplements the existing [content and model-pack design guide](57-background-assets-content-and-model-pack-design.md).

## Design objective

Design for this sequence:

~~~text
feature goal
-> resource explanation
-> consent/choice where needed
-> system-managed delivery
-> local validation
-> capability-ready state
-> bounded AI or media action
-> user review
-> recoverable result
~~~

The interface should never imply that a file’s presence is equivalent to an enabled feature. Use product language that exposes the actual boundary:

| Implementation state | User-facing language |
| --- | --- |
| Pack is known but not local | “Download the sound pack to use guided playback.” |
| System has scheduled work | “Preparing this feature in the background.” |
| Bytes are local and being checked | “Checking this model for this app version.” |
| Core ML is compiling | “Preparing on-device intelligence.” |
| Model/GPU/media validation passed | “Ready on this iPhone.” |
| Resource is local but not compatible | “This device is using Basic Mode.” |
| New candidate is downloading | “Current version stays available while the update prepares.” |
| Pack was removed or evicted | “Re-download to restore the enhanced feature.” |

Avoid “AI is thinking” for delivery or compilation. The person needs to know whether the app is downloading, preparing, unavailable, or producing an output.

## Screen anatomy

A useful SwiftUI resource surface usually has five regions:

1. Feature explanation: name the experience, not the internal pack ID.
2. Readiness status: one semantic label and, where useful, a short detail.
3. Resource facts: size, version, local/on-device processing note, and storage action.
4. Primary action: Download, Retry, Continue, Use Basic Mode, or Update.
5. Recovery and trust: fallback, remove, learn more, privacy, and support path.

Do not put every manifest field on the first screen. Put the essential decision near the action and expose technical details in a secondary sheet or disclosure group. Model revision, shader variant, pack identifier, and validation timestamp can be useful for diagnostics without becoming the product headline.

The system downloader extension should remain invisible as a process. The app can show a truthful app-owned status derived from persisted state and manager updates, but it should not imitate a system panel or claim a completion event that it has not observed.

## Liquid Glass hierarchy

Use the current system Liquid Glass treatment where SwiftUI and system controls provide it. Add custom glass only for a meaningful grouping such as a compact resource status bar, a floating retry control, or a small capability summary. Keep the main content readable if transparency is reduced or the glass effect is unavailable.

Recommended composition:

~~~text
content or preview
    [compact glass status group]
    status + bounded progress or indeterminate activity
    primary action
    fallback / storage action
~~~

The glass group should not float over essential text, obscure a media preview, or create a second navigation hierarchy. Use standard Button, ProgressView, Toggle, Menu, ShareLink, and navigation/presentation behaviors. The glass surface is a visual container; the semantic control still owns the action and accessibility label.

Use motion sparingly:

- animate a transition from Downloading to Preparing only when the state actually changes;
- keep progress animation from implying false precision;
- avoid a looping shimmer that suggests ongoing system work after the task has failed;
- respect Reduce Motion and provide a static status;
- make a new-ready announcement available without relying on animation.

## State language and affordances

Every state needs a user action or a clear explanation:

| State | Primary | Secondary | Avoid |
| --- | --- | --- | --- |
| Not installed | Download | Use Basic Mode | “Enable AI” without size or purpose |
| Downloading | Continue using app or Cancel if supported | Details | Blocking every screen on an opportunistic task |
| Preparing | Wait/use current version | Cancel or Basic Mode when safe | “Downloaded” before compile/load completes |
| Ready | Use feature | Remove or Manage storage | Claiming quality or truth from readiness alone |
| Update available | Update now | Keep current version | Silent replacement of active content |
| Failed | Retry | Basic Mode/details | Hiding network/storage reason |
| Incompatible | Use Basic Mode | Learn why/remove | Repeated retry of a known device mismatch |
| Evicted | Re-download | Continue with fallback | Treating eviction as data loss |

If the resource is optional, make the fallback a first-class action. If the resource is essential, describe what remains usable and why the feature cannot continue. Do not place an indeterminate spinner in a permanent button with no action.

## Model and AI disclosure

Separate four concepts:

1. Model installed: the file is local and has passed the load/contract gate.
2. Model available: the target device and app can select the model.
3. Inference running: a bounded input is being processed locally.
4. Result accepted: the person reviewed and committed a typed result.

For a local model, a concise disclosure can say:

> This feature prepares a model on this device. Your selected input is processed locally when the model is ready. The result remains a suggestion until you apply it.

Only use the offline/local wording when the actual route has been tested with the model local and network unavailable. If the app sends any input, telemetry, or model request off device, say so. “On device” describes an execution route, not a complete privacy claim.

Do not put model confidence, embedding distance, or classifier score in the primary glass status unless the value has a clear user meaning. A score is not proof of identity, diagnosis, intent, safety, or truth. Keep technical evaluation in a diagnostic view or internal proof packet.

## Media and GPU disclosure

Use the same vocabulary for non-AI resources:

| Resource | Readiness label | Fallback |
| --- | --- | --- |
| Video pack | Playback ready | Stream/lower-resolution preview |
| Audio pack | Guided audio ready | Text instructions or bundled clips |
| Texture pack | Enhanced visuals ready | System/bundled textures |
| Shader library | Enhanced effect ready | Native SwiftUI/Metal baseline effect |
| 3D asset | Scene ready | 2D preview or simplified geometry |

Say “Enhanced effect ready on this iPhone” only after the resource loads and the selected device path passes compatibility. A simulator preview can inform visual design but cannot establish GPU support, memory, frame pacing, thermal behavior, or physical camera/media conditions.

## Storage and update design

Expose approximate download and installed size when known. Use understandable labels such as “Download 280 MB” and “Uses about 640 MB while installed,” not only compressed archive terminology. If the exact size is unavailable, say “Size shown before download” or omit false precision.

Model updates as a candidate:

~~~text
active validated version
        |
        +--> candidate downloading
        +--> candidate compiling/loading
        +--> candidate evaluation
        +--> promote or reject
~~~

Keep the active version available while the candidate is prepared unless the feature requires the latest version. A failed update should not erase a working basic mode or user-owned records. A Remove Download action should name what is removed and what remains:

> Remove the enhanced model? Your saved projects stay on this iPhone. The enhanced analysis can be downloaded again later.

For destructive storage actions, require confirmation when the resource is large or the feature is central. Do not call system eviction “deleting your data” unless the app actually deletes user-owned data.

## Accessibility and alternate input

Make the status a semantic group with a concise label/value/action model. A VoiceOver user should hear:

> Enhanced analysis. Preparing model, 42 percent. Use Basic Mode. Button.

If progress is indeterminate:

> Enhanced analysis. Preparing model. Use Basic Mode. Button.

Test:

- VoiceOver focus order from feature content to status to primary action;
- Dynamic Type with long localized names and multi-line error text;
- Bold Text, increased contrast, reduced transparency, and color filters;
- Reduce Motion, with no information conveyed only by glass movement;
- Voice Control phrases for Download, Retry, Use Basic Mode, and Remove;
- Switch Control scanning and activation;
- external keyboard focus and return/escape actions where supported;
- pointer hover and hit target size on iPadOS;
- localized decimal, byte-size, date, and error formatting.

Do not use color alone to distinguish Ready, Failed, and Basic Mode. Pair color with text, icon meaning, and an accessibility value. Keep the glass contrast stable over changing media or imagery.

## Privacy and trust

The resource view is a good place to disclose resource behavior without overwhelming the person:

- what is downloaded;
- where processing occurs;
- what leaves the device, if anything;
- whether the resource can be removed;
- whether a model is optional or required;
- whether data is retained after the feature runs.

Do not expose signed asset URLs, account identifiers, App Group paths, device identifiers, or internal pack IDs in normal UI. Diagnostics can show a redacted resource ID and version behind an explicit debug/support route.

When a resource is licensed or account-scoped, do not present an account-specific download as an anonymous static pack. Use the product’s authenticated data route and state the account dependency. Background Assets’ intended purpose does not erase the app’s own privacy and authorization responsibilities.

## Network, energy, and offline behavior

Design around delayed or interrupted delivery:

- allow the person to continue in Basic Mode;
- preserve the last validated model/media/shader version;
- give Retry a meaningful error reason;
- do not require a foreground screen to remain open for system-managed work;
- avoid promising an exact background completion time;
- show Wi-Fi or cellular implications only when the product actually enforces them;
- let the user cancel or defer optional work where the route supports it;
- preserve an accessible status after relaunch.

For an on-device AI feature, a good offline test is a physical-device run after the model is local, with network unavailable and diagnostics captured. The UI should not say “offline ready” merely because a download finished; compilation, load, and a representative operation must pass.

## Design handoff checklist

- [ ] The feature’s user outcome is named before the pack name.
- [ ] Managed versus unmanaged delivery is reflected in the implementation plan.
- [ ] Apple-hosted versus self-hosted ownership is recorded.
- [ ] Download, local validation, compilation/loading, compatibility, ready, stale, failed, and evicted states are distinct.
- [ ] Progress is real or intentionally indeterminate.
- [ ] Liquid Glass groups controls and hierarchy without hiding content.
- [ ] Basic Mode or another fallback is visible where the feature permits it.
- [ ] Model-ready is distinct from model-output-accepted.
- [ ] Media/GPU readiness is distinct from file presence.
- [ ] Storage, version, update, removal, and re-download behavior are clear.
- [ ] VoiceOver, Dynamic Type, contrast/transparency, motion, keyboard, pointer, Voice Control, and Switch Control paths are tested.
- [ ] Privacy wording matches the actual data flow.
- [ ] Offline, low-storage, interruption, and relaunch states are designed.
- [ ] The design has a target-device proof plan and does not rely on previews alone.

## Sources

- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Background Assets](https://developer.apple.com/documentation/backgroundassets)
- [Downloading Apple-hosted asset packs](https://developer.apple.com/documentation/backgroundassets/downloading-apple-hosted-asset-packs)
- [AssetPackManager](https://developer.apple.com/documentation/backgroundassets/assetpackmanager)
- [ManagedDownloaderExtension](https://developer.apple.com/documentation/backgroundassets/manageddownloaderextension)
- [StoreDownloaderExtension](https://developer.apple.com/documentation/storekit/storedownloaderextension)
- [Testing asset packs locally](https://developer.apple.com/documentation/backgroundassets/testing-asset-packs-locally)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [Reducing the size of your Core ML app](https://developer.apple.com/documentation/coreml/reducing-the-size-of-your-core-ml-app)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Metal](https://developer.apple.com/documentation/metal)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
