# SwiftUI PhotosPicker, PhotoKit, Image I/O, Live Photo, and media-source/editing review route

Use this route when an app accepts photos, videos, Live Photos, or Photos-library edits and needs a trustworthy path from selection to a stored or shared result. The route assumes that the feature may add on-device Vision/Core ML proposals, but keeps proposals separate from source truth and committed changes.

Read the [source/editing deep dive](../42-framework-deep-dives/102-swiftui-photospicker-photokit-imageio-live-photo-source-review.md), [design guide](../21-design-deep-dives/130-swiftui-photospicker-photokit-imageio-live-photo-source-review-design.md), [proof matrix](../60-verification/127-swiftui-photospicker-photokit-imageio-live-photo-source-review-proof-matrix.md), and [recipes](../70-code-recipes/145-swiftui-photospicker-photokit-imageio-live-photo-source-review-recipes.md) before implementation.

## Route selector

| Need | Route | Required boundary |
| --- | --- | --- |
| One image or video | PhotosPicker | Selected placeholder -> requested Transferable/file representation |
| Multiple assets | PhotosPicker with bounded count | Per-item loading, cancellation, deduplication, source manifest |
| Current persistent library | PhotoKit fetch | Access level, limited-library state, current PHAsset resolution |
| Original/current resource | PHAssetResourceManager | Resource type, iCloud policy, progress, file validation |
| Fast thumbnails | PHImageManager or PHCachingImageManager | Target size, degraded callback, cache invalidation |
| Video processing | PHImageManager AVAsset/export session | Network policy, cancellation, codec/export proof |
| Live Photo playback | PHImageManager requestLivePhoto + PHLivePhotoView | Paired content, motion readiness, still fallback |
| Library edit | PHContentEditingInput/Output + PHAssetChangeRequest | Adjustment data, preview, change-block commit |
| New derivative | Image I/O/AVFoundation/file export | Format, dimensions, metadata, retention |
| Model proposal | Vision/Core ML on materialized input | Provenance, model revision, confidence, review |

Do not choose PhotoKit read/write access for a one-off selection unless the feature genuinely needs persistent library browsing or mutation.

## Contract worksheet

Fill this out before writing the SwiftUI view:

~~~text
User job:
Selected media classes:
One-off picker or persistent library:
Required access: none / add-only / read-write:
Maximum items:
Maximum bytes/dimensions/duration:
Accepted UTTypes and representation policy:
Original bytes required: yes/no:
Live Photo playback/edit/export required: yes/no:
Metadata retained:
Metadata excluded:
Temporary-file lifetime:
AI model and revision:
Human review step:
Destination: app record / Photos edit / exported file / share:
Delete/revoke behavior:
Physical-device proof:
Release proof:
~~~

## Target and privacy gate

Inspect the named Xcode target before implementation:

- PhotosUI, Photos, ImageIO, AVFoundation, Vision, and Core ML imports;
- deployment target and device family;
- Photos usage descriptions for the requested access level;
- privacy manifest and data-use declarations;
- Photos editing extension membership if applicable;
- file protection and temporary-storage policy;
- supported media formats and model/device constraints;
- localization, accessibility, and reduced-motion behavior;
- archive entitlements and release configuration.

If the feature can use PhotosPicker without broad PhotoKit access, make that the default. If it needs PhotoKit, distinguish addOnly from readWrite and handle limited explicitly.

## Route A: SwiftUI PhotosPicker to a reviewable import

1. Explain the user job and representation scope.
2. Present PhotosPicker with a narrow PHPickerFilter.
3. Apply a multiple-selection cap.
4. Treat each PhotosPickerItem as a placeholder.
5. Load a custom Transferable or file-backed representation.
6. Track selection generation and cancellation.
7. Inspect bytes with Image I/O or media metadata.
8. Create a source manifest.
9. Show a preview and any AI proposal.
10. Let the person accept, adjust, replace, or discard.
11. Store only the app-owned record or derivative required by the feature.

Keep a late transfer result from overwriting the newest selection. A successful load can still be a temporary or converted representation; record what was actually loaded.

## Route B: PhotoKit library and limited access

1. Request the least required access at the feature boundary.
2. Render not-determined, denied, restricted, limited, and authorized states.
3. Fetch by current identifiers or bounded PHFetchOptions.
4. Project PHAsset metadata into an app-owned value.
5. Resolve again before a mutation or expensive load.
6. Register a change observer for the fetched result or asset.
7. Reconcile deletion, edit, limited-selection, and iCloud changes.
8. Remove or quarantine stale app records.

Do not retain a location or claim a current source merely because an old PHAsset object was once fetched.

## Route C: Underlying resource delivery

Use PHAssetResourceManager when the feature needs resource bytes rather than a rendered preview:

1. Fetch the current PHAsset.
2. Enumerate PHAssetResource values.
3. Select a resource by explicit resource type and content type.
4. Create PHAssetResourceRequestOptions.
5. Choose whether iCloud/network access is allowed.
6. Stream to a temporary file with a byte budget and progress.
7. Validate UTI, dimensions, paired-resource expectations, and digest.
8. Feed the materialized file to Image I/O, AVFoundation, or the model.
9. Delete the temporary file or record a deliberate retention reason.

For a Live Photo, verify both still and video resources when the feature promises motion. For RAW or adjusted content, state which resource policy was chosen.

## Route D: Thumbnail, original, and video requests

Use PHImageManager according to the representation:

- thumbnail: bounded target size and no unnecessary network fetch;
- still bytes: request image data and retain orientation;
- video preview: request a player item or AVAsset;
- video export: request an export session and validate the output;
- Live Photo playback: requestLivePhoto only for motion/sound;
- batch grid: preheat with PHCachingImageManager, then stop caching outside the visible window.

PhotoKit callbacks can deliver degraded and high-quality representations. Keep the degraded state visible, inspect result info, and cancel the PHImageRequestID when the operation is no longer needed.

## Route E: Live Photo playback and fallback

1. Determine whether the current asset is a Live Photo.
2. Request a still for lists and a Live Photo for playback.
3. Set a deliberate network policy and progress handler.
4. Render downloading, playable, failed, and still-only states.
5. Use the system Live Photo view or supported native wrapper.
6. Preserve the paired content in edits and shares.
7. Offer still export for destinations that do not support Live Photos.

Never treat the still thumbnail as proof that motion and sound are ready.

## Route F: Non-destructive Photos-library edit

1. Resolve and authorize the current PHAsset.
2. Check canPerform for the intended operation.
3. Request PHContentEditingInput with an adjustment-data policy.
4. Build a preview from the input.
5. Let the person approve the adjustment.
6. Write rendered photo/video output or run PHLivePhotoEditingContext.
7. Create PHAdjustmentData with format identifier, version, and parameters.
8. Set contentEditingOutput on PHAssetChangeRequest inside performChanges.
9. Observe the library result.
10. Reopen or re-fetch the current asset and update the source manifest.

The rendered URL is a staging artifact. The Photos change block is the commit boundary.

## Route G: App-owned derivative export

Use this route when the user wants a new file or app record rather than a Photos edit:

1. Choose a destination format and byte/pixel budget.
2. Use Image I/O or AVFoundation to write the derivative.
3. Apply orientation, color, gain-map, auxiliary-data, and metadata policy.
4. Reopen the output and inspect the result.
5. Store a source manifest and transformation revision.
6. Present a share/export confirmation with privacy details.
7. Retain or delete the output according to the feature’s documented lifecycle.

An exported file is not automatically synchronized back into Photos. If the user wants that, use a separate authorized creation route and show the destination.

## Route H: On-device AI proposal

1. Materialize the selected representation.
2. Normalize orientation and dimensions.
3. Record source and model revision.
4. Run Vision/Core ML with cancellation and resource budgets.
5. Store a typed proposal, not a domain mutation.
6. Present the proposal with provenance and uncertainty.
7. Re-resolve the current asset before accepting.
8. Require confirmation for library edits, sharing, deletion, or identity-sensitive output.
9. Commit through the same app-owned edit/export operation as a human action.

Do not send a photo to an external service merely because the local model failed. Make fallback and consent explicit.

## SwiftUI state and navigation

Use a state machine that can route to:

- picker;
- access explanation;
- import progress;
- preview;
- model proposal review;
- edit controls;
- export metadata review;
- committed result;
- missing source recovery.

The navigation destination should carry an app-owned source ID and revision, not a raw PHAsset reference. Resolve at the destination and show a recoverable state if the asset changed.

## Accessibility and native design gate

Before calling the route ready:

- test VoiceOver labels for source, type, readiness, and proposal;
- test Dynamic Type and long localized metadata;
- provide still and text alternatives for Live Photo motion;
- support Reduce Motion and Reduce Transparency;
- ensure keyboard, pointer, and Switch Control can choose, review, and commit;
- keep Liquid Glass behind hierarchy and controls, not over critical media detail;
- preserve native picker and playback semantics;
- test high contrast and light/dark appearances.

## Proof packet

Attach evidence for:

~~~text
Target/deployment/device family:
Photos privacy keys and access level:
PhotosPicker selection record:
Limited-library matrix:
PHAsset/resource identity:
Local/iCloud representation result:
Image/video/Live Photo validation:
Metadata inspection:
AI model/proposal/decision:
Edit/export commit result:
Photo-library observation:
Accessibility/input result:
Physical-device result:
Archive/TestFlight/release result:
Known unsupported cases:
~~~

## Route completion checklist

~~~text
[ ] The route uses the smallest media-access surface.
[ ] Picker placeholders and representations are separate.
[ ] Selection generations and PhotoKit requests can be cancelled.
[ ] PHAsset and PHAssetResource identity are resolved currently.
[ ] Limited-library and iCloud/offline states are visible.
[ ] Image I/O validates format, dimensions, orientation, and metadata policy.
[ ] Live Photo playback, edit, download, and still fallback are separate states.
[ ] Photos edits use adjustment data and performChanges commit.
[ ] Exports are reopened and inspected before sharing.
[ ] Local AI remains a reviewable proposal.
[ ] SwiftUI/Liquid Glass/accessibility/input behavior is tested.
[ ] Physical-device, system, archive, and release proof is attached.
~~~

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [Bringing Photos picker to your SwiftUI app](https://developer.apple.com/documentation/PhotoKit/bringing-photos-picker-to-your-swiftui-app)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Photos](https://developer.apple.com/documentation/photos)
- [PHPhotoLibrary](https://developer.apple.com/documentation/photos/phphotolibrary)
- [Delivering an enhanced privacy experience in your Photos app](https://developer.apple.com/documentation/photokit/delivering-an-enhanced-privacy-experience-in-your-photos-app)
- [PHAsset](https://developer.apple.com/documentation/photos/phasset)
- [PHAssetResource](https://developer.apple.com/documentation/photos/phassetresource)
- [PHAssetResourceManager](https://developer.apple.com/documentation/photos/phassetresourcemanager)
- [PHAssetResourceRequestOptions](https://developer.apple.com/documentation/photos/phassetresourcerequestoptions)
- [PHImageManager](https://developer.apple.com/documentation/photos/phimagemanager)
- [PHCachingImageManager](https://developer.apple.com/documentation/photos/phcachingimagemanager)
- [PHImageRequestOptions](https://developer.apple.com/documentation/photos/phimagerequestoptions)
- [PHVideoRequestOptions](https://developer.apple.com/documentation/photos/phvideorequestoptions)
- [PHLivePhotoRequestOptions](https://developer.apple.com/documentation/photos/phlivephotorequestoptions)
- [PHLivePhoto](https://developer.apple.com/documentation/photos/phlivephoto)
- [PHLivePhotoView](https://developer.apple.com/documentation/photosui/phlivephotoview)
- [PHPhotoLibraryChangeObserver](https://developer.apple.com/documentation/photos/phphotolibrarychangeobserver)
- [PHContentEditingInput](https://developer.apple.com/documentation/photos/phcontenteditinginput)
- [PHContentEditingOutput](https://developer.apple.com/documentation/photos/phcontenteditingoutput)
- [PHContentEditingInputRequestOptions](https://developer.apple.com/documentation/photos/phcontenteditinginputrequestoptions)
- [PHAdjustmentData](https://developer.apple.com/documentation/photos/phadjustmentdata)
- [PHAssetChangeRequest](https://developer.apple.com/documentation/photos/phassetchangerequest)
- [PHLivePhotoEditingContext](https://developer.apple.com/documentation/photos/phlivephotoeditingcontext)
- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Live Photos HIG](https://developer.apple.com/design/human-interface-guidelines/live-photos)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
