# SwiftUI PhotosPicker, PhotoKit, Image I/O, Live Photo, and media-source/editing proof matrix

This matrix separates evidence for selection, authorization, representation delivery, source identity, decoding, Live Photo readiness, editing, export, local-AI proposals, accessibility, privacy, and release. A picker preview, PHAsset object, model label, or generated file is not proof of the next authority transition.

Use it with the [source/editing review](../42-framework-deep-dives/102-swiftui-photospicker-photokit-imageio-live-photo-source-review.md), [design guide](../21-design-deep-dives/130-swiftui-photospicker-photokit-imageio-live-photo-source-review-design.md), [route](../50-capability-recipes/133-swiftui-photospicker-photokit-imageio-live-photo-source-review-route.md), and [recipes](../70-code-recipes/145-swiftui-photospicker-photokit-imageio-live-photo-source-review-recipes.md).

## Evidence levels

| Level | Evidence | Boundary |
| --- | --- | --- |
| L0 | Current Apple documentation and SDK availability | API/source awareness |
| L1 | Named target, privacy keys, entitlements, and source inspection | Configuration contract |
| L2 | Unit, fixture, metadata, and transformation tests | App-owned pipeline correctness |
| L3 | Simulator/system picker or local library fixture | Some UI and app-side behavior |
| L4 | Signed physical-device Photos/iCloud/media run | Permission, representation, playback, and device behavior |
| L5 | Archive/TestFlight/App Store record | Distribution and release configuration |
| L6 | Repeatable privacy, recovery, accessibility, and support packet | Operational readiness |

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| PhotosPicker is in the target | Named compile and picker presentation | A SwiftUI preview |
| The person selected media | Physical/system picker run with captured selection record | A constructed PhotosPickerItem |
| The item is ready to process | Representation load, UTI, dimensions, byte/type validation | A non-nil placeholder |
| The app uses narrow access | Target privacy/config inspection and picker-only run | A permission screen |
| PhotoKit access is correct | Read/write, add-only, limited, denied, restricted matrix | One authorized run |
| PHAsset is current | Fresh identifier resolution and change observation | A cached PHAsset |
| Resource is the intended source | Resource enumeration, type policy, and manifest | First resource returned |
| iCloud behavior is honest | Offline/local and network-enabled physical runs with progress/error evidence | A network preview |
| Thumbnail is bounded | Target-size/memory tests and Image I/O inspection | A full-resolution decode |
| Image metadata policy works | Reopened export inspection for EXIF/XMP/GPS/auxiliary data | Destination options in source |
| Video output is valid | Physical decode/export/playback and codec/size inspection | AVAsset object existence |
| Live Photo is playable | Paired request and physical playback observation | Still thumbnail |
| Live Photo edit is intact | Frame/audio/pairing test and Photos playback | One processed frame |
| Edit preview is reversible | Adjustment-data reapply/revert fixture | Slider movement |
| Photos edit committed | Successful performChanges plus library observation | RenderedContentURL written |
| Export is app-owned | Destination file inspection and source manifest | Temporary file existence |
| AI proposal has provenance | Source/materialization/model/revision record | A label or confidence |
| AI proposal is user-approved | Review action and decision record | Automatic inference |
| Accessibility works | VoiceOver, Dynamic Type, reduced motion/contrast, keyboard/pointer run | Accessibility modifiers in code |
| Release is ready | Signed archive, privacy, device, TestFlight, and recovery packet | Debug simulator run |

## System and target packet

Capture:

~~~text
App target:
Extension target, if any:
Bundle ID:
Deployment target:
Device family:
PhotosUI/Photos/ImageIO/AVFoundation/Vision/Core ML imports:
NSPhotoLibraryUsageDescription:
NSPhotoLibraryAddUsageDescription:
Privacy manifest/data-use review:
File protection and temporary-storage policy:
Supported formats and model revisions:
Archive/export configuration:
TestFlight build:
~~~

Verify that usage descriptions match the access level and user-facing explanation. If the feature uses only PhotosPicker, record why broad PhotoKit access is absent.

## Authorization matrix

| State | Picker route | PhotoKit route | Expected app behavior | Evidence |
| --- | --- | --- | --- | --- |
| Not determined | Picker can be offered | Request only at feature boundary | Explain scope before prompt | Physical device |
| Authorized | Selection and load | Fetch current assets | Show ready state | Physical device |
| Limited | Picker can choose additional items | Fetch only selected subset | Show limited badge and manage-access action | Physical device |
| Denied | Offer picker if still suitable | No library fetch/mutation | Explain Settings/reimport fallback | Physical device |
| Restricted | Depends on system state | Do not loop prompts | Explain unavailable access | Physical device |
| Add-only | Not relevant to reading | Create-only route | Do not claim existing-library visibility | Target plus device |
| iCloud unavailable | Item may be selected | Resource may not be local | Show retry/offline state | Offline and network runs |

## PhotosPicker selection matrix

| Check | Evidence | Failure to record |
| --- | --- | --- |
| Filter matches job | Target source and picker run | Picker shows unsupported types |
| Multiple count is bounded | UI inspection and test selection | Unbounded memory/task fan-out |
| Selection replacement is safe | Select A, select B before A loads | A overwrites B |
| Placeholder is not treated as bytes | State test and code review | Preview marked committed |
| Transferable representation is explicit | Type/UTI test | Image used for non-PNG source without review |
| iCloud failure is recoverable | Offline selection/load test | Spinner never resolves |
| Temporary file is deleted | Storage lifecycle test | Source bytes retained indefinitely |

## PHAsset and resource matrix

| Check | Evidence | Boundary |
| --- | --- | --- |
| Local identifier resolves | Fetch by identifier on device | Identifier is not a file URL |
| Asset metadata is current | Re-fetch after Photos edit/delete | Cached fields are not current |
| Limited selection is honored | Remove asset from limited set | Old derivative is not new authorization |
| Resource policy is explicit | Resource type/content type manifest | First resource is not automatically canonical |
| Original/adjusted choice is recorded | PHContentEditingInput options and manifest | Preview does not prove original |
| iCloud policy is explicit | Network access option plus progress/error | Downloaded preview proves nothing about offline |
| Source deletion is handled | Delete in Photos then resume app | Cached app record still says ready |

## Loading, decode, and metadata matrix

| Check | Evidence | Boundary |
| --- | --- | --- |
| Byte budget | Oversized fixture rejected before decode | Device memory does not define safe budget |
| Container type | Image I/O type inspection | Filename extension |
| Orientation | Orientation-aware thumbnail and model input test | Raw pixel orientation |
| Dimensions | Maximum pixel and aspect policy | Thumbnail dimensions |
| Auxiliary data | Depth/matte/gain-map fixture inspection | Presence in source |
| Metadata privacy | Output reopened and GPS/XMP inspected | Source code key |
| Color behavior | Device/export color fixture | Simulator preview |
| Incremental/incomplete input | Image I/O status state tests | Partial data treated as complete |

## Image and video representation matrix

| Representation | Ready evidence | Fallback |
| --- | --- | --- |
| Still thumbnail | Target-size decode and orientation | Placeholder or text |
| Original still data | Data request/resource stream and validation | Ask user to retry or choose another |
| Video AVAsset | Physical load and duration/track inspection | Metadata-only state |
| Video export | Export completed and reopened | Preserve source |
| Live Photo still | Still request succeeds | Still-only card |
| Live Photo pair | Live Photo request/playback succeeds | Still export |
| RAW/adjusted resource | Resource type and decoder/model policy | Unsupported-format message |

## Live Photo matrix

| Claim | Evidence | Not enough |
| --- | --- | --- |
| Asset is a Live Photo | PHAsset subtype/resource pair | A motion-like thumbnail |
| Motion is downloadable | Request options/progress and physical run | Network flag in source |
| Motion is playable | PHLivePhotoView playback with sound policy | PHLivePhoto object alone |
| Edit applies to whole experience | Frame processor plus still/audio/pairing fixture | Still filter only |
| Share preserves content | Preview and destination playback | Exported still |
| Still fallback is usable | Unsupported-surface run and accessible label | Hidden disabled control |

## Non-destructive edit matrix

| Stage | Evidence | Commit boundary |
| --- | --- | --- |
| Current asset | Fresh PHAsset and canPerform | Not a mutation |
| Editing input | PHContentEditingInput with network/adjustment policy | Not a mutation |
| Preview | Rendered preview with parameters | Not a mutation |
| Output | PHContentEditingOutput file and adjustment data | Staging only |
| Change request | performChanges succeeds | Library commit |
| Observation | PHPhotoLibraryChangeObserver sees new state | Current source refresh |
| Reopen/revert | Adjustment data can reconstruct/revert | Reversibility evidence |

Test a user edit over an existing adjustment, an edit while iCloud is offline, cancellation before commit, failed output write, failed change block, and the asset being edited elsewhere.

## Export and privacy matrix

| Output | Required inspection | User-facing decision |
| --- | --- | --- |
| Public share image | GPS/XMP/original filename/auxiliary data | Metadata kept or removed |
| Private app derivative | File protection, retention, source link | Why the app stores it |
| Live Photo share | Paired resources and destination support | Live Photo or still |
| Video derivative | Codec, duration, orientation, audio, size | Quality/size tradeoff |
| AI-rendered image | Source/model/adjustment note | Proposal accepted or generated |

## AI proposal matrix

| Stage | Evidence | Boundary |
| --- | --- | --- |
| Input | Source manifest and preprocessing record | Model does not know source authority |
| Model | Model ID/revision/compute policy | Load does not prove quality |
| Output | Typed proposal and uncertainty | Label is not identity or diagnosis |
| Review | User action and parameters | Preview is not consent |
| Commit | Current source re-resolution and mutation result | Proposal cannot bypass authorization |
| Recovery | Stale-source and model-failure path | Retry is not success |

## Accessibility, privacy, and recovery matrix

| Check | Evidence |
| --- | --- |
| VoiceOver labels identify type, source, readiness, and action | Physical accessibility run |
| Dynamic Type preserves review and commit actions | Large text run |
| Reduce Motion preserves Live Photo/edit comparison | Device setting run |
| High contrast/reduced transparency preserves glass controls | Device setting run |
| Keyboard/pointer/Switch Control can complete route | iPad/Mac-compatible target run |
| Denied/limited access avoids private content claims | Authorization matrix |
| Metadata and temporary bytes follow retention policy | File/storage inspection |
| Deleted/revoked source is removed or quarantined | Revoke/delete run |
| AI output is not logged as raw media or identity fact | Log/privacy inspection |

## Release packet

Include:

~~~text
[ ] Named target compile with current SDK
[ ] Privacy/usage descriptions and access-level review
[ ] PhotosPicker selection and replacement run
[ ] Limited/denied/restricted authorization run
[ ] Offline/iCloud resource matrix
[ ] Image/video/Live Photo physical-device run
[ ] Image I/O metadata/export inspection
[ ] Non-destructive edit and adjustment-data reopen/revert
[ ] AI proposal source/model/review packet
[ ] VoiceOver/Dynamic Type/Reduce Motion/contrast/input run
[ ] Storage/temporary-file cleanup evidence
[ ] Signed archive and entitlement inspection
[ ] TestFlight/release-system run
[ ] Known unsupported formats and recovery copy
~~~

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [Bringing Photos picker to your SwiftUI app](https://developer.apple.com/documentation/PhotoKit/bringing-photos-picker-to-your-swiftui-app)
- [Photos](https://developer.apple.com/documentation/photos)
- [PHPhotoLibrary](https://developer.apple.com/documentation/photos/phphotolibrary)
- [Delivering an enhanced privacy experience in your Photos app](https://developer.apple.com/documentation/photokit/delivering-an-enhanced-privacy-experience-in-your-photos-app)
- [PHAsset](https://developer.apple.com/documentation/photos/phasset)
- [PHAssetResource](https://developer.apple.com/documentation/photos/phassetresource)
- [PHAssetResourceManager](https://developer.apple.com/documentation/photos/phassetresourcemanager)
- [PHAssetResourceRequestOptions](https://developer.apple.com/documentation/photos/phassetresourcerequestoptions)
- [PHImageManager](https://developer.apple.com/documentation/photos/phimagemanager)
- [PHLivePhoto](https://developer.apple.com/documentation/photos/phlivephoto)
- [PHLivePhotoRequestOptions](https://developer.apple.com/documentation/photos/phlivephotorequestoptions)
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
