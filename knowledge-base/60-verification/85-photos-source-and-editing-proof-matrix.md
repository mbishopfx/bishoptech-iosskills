# Photos source, transfer, editing, and AI proof matrix

This matrix keeps picker privacy, PhotoKit library authority, transfer/resource readiness, model inference, and Photos mutations as separate evidence claims.

## Evidence ladder

| Claim | Minimum useful evidence | Stronger evidence | Does not prove |
| --- | --- | --- | --- |
| The user selected a photo | Picker UI test with a controlled selection | Physical device selection across image/video/Live Photo and cancellation | That bytes loaded or library authorization exists. |
| A representation loaded | Transfer/import fixture with supported content type | Physical iCloud/local load with progress, cancellation, and large-file behavior | Model quality or retention compliance. |
| The app uses least privilege | Code/configuration review showing picker-only path | Permission reset/device run showing no full-library prompt for a one-off selection | That the app’s other features do not request broader access elsewhere. |
| Library access is correct | Authorization state fixtures for read/write, add-only, limited, denied, restricted | Physical device permission/limited-picker/revocation run | Availability of a particular asset or its underlying bytes. |
| A `PHAsset` is current | Fetch by local identifier plus metadata/modification fixture | Change observer run after Photos app/other-device edit/delete | That cached bytes or a model result are current. |
| A thumbnail is fit for display | Size/content-mode/degraded-result fixture | Physical scroll/cache run with memory and cancellation observations | That it is fit for full-resolution AI or export. |
| Original/current data is correct | Version/orientation/content-type fixture | Physical iCloud/resource run with network policy and file inspection | That the user intended hidden EXIF or all metadata to enter a model. |
| A large asset is handled safely | `FileRepresentation`/temporary-file copy/delete tests | Physical large-image/video run with memory/storage/thermal notes | Safe retention outside the tested lifecycle. |
| An AI observation is source-linked | Typed proposal fixture with source ID, version, orientation, timestamp | Device inference with model/version and stale-source invalidation | Accuracy, identity, medical meaning, or user intent. |
| A Photos edit is non-destructive | Adjustment-data reconstruction and before/after tests | Physical edit/reopen/revert run in Photos and app | That every prior edit can be reconstructed. |
| A library mutation was applied | `performChanges` success/failure fixture | Physical user-approved save/edit/delete run with reconciliation | That the user understood an overly broad change block. |
| External changes reconcile | `PHFetchResultChangeDetails`/object-change fixtures | Device run with edits/deletes/reorders from Photos and another process/device | Cross-launch recovery unless persistent-change storage is tested. |
| A Liquid Glass review is accessible | Semantic state/action fixtures | Physical VoiceOver, Voice Control, Switch Control, keyboard/pointer, Dynamic Type, contrast/transparency/motion run | Usability from a screenshot. |
| Release contains the route | Archive/resource/privacy/target inspection | Signed TestFlight/App Store install and photo/model run | App Store review or every hardware/locale tier. |

## Source-state proof matrix

| State | Deterministic fixture | Device proof |
| --- | --- | --- |
| No selection | Empty selection and reset state | Picker open/close without selection. |
| Placeholder selected | Item generation and supersession tests | Rapid replacement while a large asset loads. |
| Transfer in progress | Progress/cancel/failure fixtures | iCloud/offline/slow-network retrieval. |
| Transfer complete | Content type, orientation, size, and file ownership checks | HEIF/JPEG/RAW/video/Live Photo on representative device. |
| Permission limited | Scope state and limited-library prompt adapter | Add/remove selected assets in Settings/system picker. |
| Asset changed/deleted | Local ID fetch and invalidation fixtures | Edit/delete in Photos while app is open/backgrounded. |
| Model ready | Stub model state and source manifest | Real on-device model load/preprocessing/prediction. |
| Proposal stale | Source modification/version mismatch fixture | Change source while proposal review is open. |
| Save to app | App persistence and delete fixture | Relaunch and storage cleanup. |
| Save to Photos | Mutation command and result mapping fixture | User-approved add/edit with Photos reconciliation. |

## PhotoKit mutation proof

Record for every write:

```text
user action and exact destination:
PHAccessLevel / authorization state:
source local/cloud identifier and modification date:
new asset versus edit-to-existing:
content type and output file/resource:
adjustment identifier/version (if editing):
single change block contents:
success/error and system prompt:
post-change fetch/change-observer result:
rollback/delete/reset path:
```

Do not call a callback success without verifying the app projection and displayed state match the library result. If the change fails, preserve the source and proposal; do not mark the item saved.

## AI and privacy proof

Verify:

- only explicitly selected or authorized sources enter preprocessing;
- orientation and representation version are recorded;
- raw media and EXIF are not logged accidentally;
- model output carries source/model/version timestamps;
- stale/deleted sources invalidate proposals;
- user edits are visible before app or Photos persistence;
- derived files and temporary resources are deleted as promised;
- on-device processing does not silently imply no retention or no access risk.

## Accessibility and design proof

Test the same source/proposal states with:

```text
VoiceOver
Voice Control
Switch Control
keyboard and pointer
Dynamic Type extremes
right-to-left locale
dark/light appearance
increased contrast
reduced transparency
reduced motion
long localized errors and source labels
```

The person must be able to choose, wait, understand the source, review the proposal, edit/reject it, and save or discard without relying on the image, color, animation, or a swipe-only gesture.

## Release checklist

- [ ] Picker and PhotoKit access strings match the actual scope.
- [ ] A one-off picker flow works without unnecessary library authorization.
- [ ] Limited/denied/restricted states have an intentional fallback.
- [ ] Large/iCloud/original/current resource routes are exercised.
- [ ] Temporary files and derived outputs have deletion policy and tests.
- [ ] Change observer or explicit refresh invalidates stale sources.
- [ ] AI proposal review is source-linked and deterministic before mutation.
- [ ] Photos add/edit/delete behavior is proved on a physical device.
- [ ] Accessibility tasks are completed on the real review shell.
- [ ] Signed artifact contains target resources, privacy strings, and intended capabilities.

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [Bringing Photos picker to your SwiftUI app](https://developer.apple.com/documentation/PhotoKit/bringing-photos-picker-to-your-swiftui-app)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [PHPhotoLibrary](https://developer.apple.com/documentation/photos/phphotolibrary)
- [PHAccessLevel](https://developer.apple.com/documentation/photos/phaccesslevel)
- [PHAuthorizationStatus](https://developer.apple.com/documentation/photos/phauthorizationstatus)
- [PHAsset](https://developer.apple.com/documentation/photos/phasset)
- [PHImageManager](https://developer.apple.com/documentation/photos/phimagemanager)
- [PHAssetResourceManager](https://developer.apple.com/documentation/photos/phassetresourcemanager)
- [PHContentEditingInputRequestOptions](https://developer.apple.com/documentation/photos/phcontenteditinginputrequestoptions)
- [Editing Asset Content](https://developer.apple.com/documentation/photokit/editing-asset-content)
- [PHPhotoLibraryChangeObserver](https://developer.apple.com/documentation/photos/phphotolibrarychangeobserver)
- [PHFetchResultChangeDetails](https://developer.apple.com/documentation/photos/phfetchresultchangedetails)
- [Core Transferable](https://developer.apple.com/documentation/CoreTransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [DataRepresentation](https://developer.apple.com/documentation/coretransferable/datarepresentation)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
