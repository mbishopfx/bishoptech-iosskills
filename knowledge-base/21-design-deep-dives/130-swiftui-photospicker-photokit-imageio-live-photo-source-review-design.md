# SwiftUI PhotosPicker, PhotoKit, Image I/O, Live Photo, and media-source/editing design

Design the media feature around trust transitions, not around a gallery of framework types. A person should be able to answer four questions at every stage:

1. What did I select?
2. What does the app currently have permission to use?
3. What did the app or on-device model propose?
4. What will be saved, edited, shared, or deleted if I continue?

This page is the visual and interaction companion to the [media-source/editing review](../42-framework-deep-dives/102-swiftui-photospicker-photokit-imageio-live-photo-source-review.md), [route card](../50-capability-recipes/133-swiftui-photospicker-photokit-imageio-live-photo-source-review-route.md), [proof matrix](../60-verification/127-swiftui-photospicker-photokit-imageio-live-photo-source-review-proof-matrix.md), and [recipe set](../70-code-recipes/145-swiftui-photospicker-photokit-imageio-live-photo-source-review-recipes.md).

## Start with a source-aware user job

The entry point should say what the person can do with the selected media:

| Job | Primary surface | First reassurance |
| --- | --- | --- |
| Pick one image for a profile or note | PhotosPicker | “Only the photo you choose is shared with this app.” |
| Review a batch of photos | Bounded multiple-selection PhotosPicker | “You can choose up to N items; each one loads separately.” |
| Browse a private library | PhotoKit-backed app screen | “Access is limited to the library permission you grant.” |
| Apply a reversible filter | Edit review surface | “The original stays available and your adjustment can be changed.” |
| Share a derivative | Export review surface | “Location and other metadata will be included/excluded as shown.” |
| Review a local-AI suggestion | Proposal card | “This is a suggestion from this source and model revision; you decide.” |
| Play a Live Photo | Native playback surface | “Motion and sound are available when the paired asset is ready.” |

Avoid a generic “Import” button when the feature actually means “Choose a photo,” “Scan a receipt,” “Apply a style,” or “Export a clean copy.” Clear verbs make the system picker and the app-owned destination feel like one coherent route.

## The source-aware anatomy

Use a compact hierarchy:

~~~text
media surface
├─ source badge: PhotosPicker / Photos library / app file
├─ content preview: still, video, or Live Photo
├─ readiness: selected / loading / offline / reviewable / committed
├─ provenance: selected item or current asset, representation, timestamp
├─ proposal: model revision, uncertainty, suggested edit
├─ decision: accept, adjust, reject, retry, choose another
└─ destination: app record, Photos edit, exported file, or share
~~~

Do not put raw identifiers in the primary UI. Keep them in an inspector, debug log, or accessible description only when they help the person recover a source. Use human-readable labels for source kind, asset type, and edit state.

## Use the system picker as the trusted entry surface

PhotosPicker is already a system-owned surface. Let it do the browsing, selection, and privacy communication. The app-owned shell should explain the job before opening it and confirm what will happen after the picker closes.

Recommended design:

- a clear button label such as “Choose photo” or “Choose Live Photo”;
- a short scope explanation;
- a visible selection count for multiple selection;
- a selection cap before the picker opens;
- a placeholder state that does not pretend bytes are ready;
- a retry state for iCloud or representation failures;
- a way to replace the current selection without losing the last accepted draft.

Do not recreate a fake Photos picker in Liquid Glass. The system picker has its own navigation, privacy, and selection behavior. App-owned glass belongs around the review, not over a replica of the system surface.

## Distinguish selection, loading, and readiness

Use state-specific copy:

| State | Visual treatment | Action |
| --- | --- | --- |
| No selection | Empty state with one primary control | Choose media |
| Placeholder selected | Neutral thumbnail skeleton and source label | Loading |
| Downloading from iCloud | Progress with network explanation | Cancel or wait |
| Materializing | Subtle progress and no edit claim | Wait |
| Preview ready | Real thumbnail plus type and dimensions | Review |
| Proposal ready | Bounded card with source and model label | Accept, edit, reject |
| Source missing | Plain-language explanation | Reimport or remove |
| Permission limited | Permission badge and Settings/update route | Manage access |
| Edit pending | Draft indicator | Continue or discard |
| Committed | Confirmation tied to destination | Open, share, or undo where supported |

Never use a green check merely because a PhotosPickerItem exists or a PHAsset fetch returned one object. Readiness means the exact representation required by the next action is available and validated.

## Make source provenance visible without making it noisy

For a media review card, show:

- source kind;
- still, video, or Live Photo;
- date or “date unavailable” when relevant;
- dimensions or duration when they affect the action;
- whether the source is local or still downloading;
- whether the app has a preview, original, or exported derivative;
- whether an AI proposal is based on a resized or normalized representation.

Use a secondary “Details” disclosure for file type, original/adjusted status, and metadata policy. The person should not need to understand PHAssetResourceType to know that “Original still + motion available” differs from “Preview only.”

## Live Photo design

Follow the Live Photos Human Interface Guidelines:

- preserve the still, motion, and sound as one experience;
- apply an edit consistently to all frames when editing;
- show when motion is downloading or playable;
- use a system-style Live Photo badge when motion is not obvious;
- provide a still-photo fallback on unsupported surfaces;
- preview the complete Live Photo before sharing;
- let the person choose whether to share it as Live Photo or still.

Use a press or supported native playback interaction. Do not put a conventional video-play button over a Live Photo if the person might interpret it as a separate video. Provide an accessible label such as “Live Photo, press and hold to play” and expose the still fallback.

For an app-owned card:

~~~text
Live Photo badge  [still preview]
“Motion and sound ready”
[Press and hold to play]
[Share as Live Photo] [Share still]
~~~

If motion is unavailable, keep the still preview usable and say why: “Motion is still downloading,” “Motion isn’t available offline,” or “This device can show the still only.”

## Edit review should precede commitment

The design should have three layers:

1. preview of the proposed output;
2. explicit parameters and adjustment data;
3. commit destination.

For a Photos-library edit, label the destination as “Edit in Photos library” and explain whether the original remains recoverable through the app’s adjustment data. For an app-owned export, label it as a new file. Do not use the same “Save” button for a non-destructive Photos edit and a new derivative unless the confirmation sheet distinguishes them.

Use a destructive confirmation only when the operation can remove or overwrite user content. A normal PHAssetChangeRequest for an adjustment is still a user-visible library mutation and should have an understandable result state.

## Metadata review is part of export UX

A clean export should not hide the metadata choice. Use a compact disclosure:

~~~text
Export copy
Photo: HEIF
Location: Removed
Camera details: Kept
Live Photo motion: Not included
AI-generated adjustment: Included in edit note

[Change settings] [Export copy]
~~~

Keep the default policy aligned with the feature’s privacy promise. If the person explicitly needs location or original camera data, allow it with a clear explanation. If the output is for a public share, choose an appropriately privacy-conscious default and test the resulting bytes.

## On-device AI review

Treat local inference as an assistant layer:

- show which source representation the model used;
- show a model or capability label when the distinction matters;
- avoid fake precision in confidence values;
- expose uncertainty or “needs review” when the output is weak;
- let the person edit or discard the proposal;
- preserve the source and model revision in the draft record;
- prevent a proposal from changing the Photos library without a user decision.

For a suggested crop, filter, caption, or organization label, the card can be lightweight. For face, location, health, safety, or identity-adjacent claims, increase provenance and review friction. A local model is a privacy advantage, not a license to make stronger claims.

## Liquid Glass and media hierarchy

Use Liquid Glass to separate controls from content, not to make the media translucent or harder to see. A good hierarchy is:

- full-bleed still or video when the content is the focus;
- a small glass control group for playback, compare, or edit;
- a glass or material-backed bottom action area for accept/reject/export;
- an opaque or high-contrast fallback for the same controls.

Avoid stacked glass cards over bright or moving photos. Excess translucency can reduce text contrast, hide faces or metadata, and make loading indicators look like part of the image. Use native materials, semantic colors, and system controls whenever they already express the task.

Keep the picker, the review card, and the destination screen visually related through typography, spacing, and motion—not by copying Photos app chrome or system icons into a fake interface.

## Motion, comparison, and Reduce Motion

Use motion to communicate state:

- a short hint that a Live Photo can play;
- a crossfade from placeholder to validated preview;
- a before/after transition for a reversible edit;
- a progress change while iCloud bytes arrive.

Respect Reduce Motion. Keep before/after comparison available as a static toggle or slider. Do not require a press-and-hold, parallax effect, or animated mask to discover the result.

## Accessibility and input

Every media card should have a useful combined accessibility label and value. Include type and readiness:

- “Kitchen photo, still image, preview ready”;
- “Beach Live Photo, motion downloading, 40 percent”;
- “Suggested crop, review required, generated on device”;
- “Export copy, location removed.”

Provide labels for badges and actions, not just images. Make the source and result order logical for VoiceOver. Ensure Dynamic Type does not hide the primary action. Support keyboard focus and pointer activation on iPad and Mac Catalyst where the target includes them. Make scrubbing, playback, and comparison available without a precise gesture.

## Permission and recovery surfaces

Permission messaging should explain the smallest next step:

| State | Copy pattern | Recovery |
| --- | --- | --- |
| Not determined | “Allow access to choose from your library” | Request at the feature boundary |
| Limited | “You shared selected photos; add another if needed” | Present limited-library picker |
| Denied | “Photo access is off” | Open Settings or use PhotosPicker where appropriate |
| iCloud unavailable | “This item isn’t on this device” | Retry on network or choose another |
| Asset deleted | “This source is no longer available” | Reimport or remove draft |
| Unsupported type | “This format isn’t supported for this action” | Choose a compatible representation |
| Edit failed | “Nothing was changed in Photos” | Retry, save derivative, or discard |

Do not send a person to Settings when a one-off PhotosPicker route can satisfy the job without broad library access.

## Review checklist

~~~text
[ ] The first action explains the user job and selected media scope.
[ ] The system Photos picker is used for one-off selection where appropriate.
[ ] Selection, placeholder, download, preview, proposal, edit, and commit are distinct states.
[ ] Source kind and representation readiness are visible.
[ ] Live Photo playback, still fallback, download, and share choices are clear.
[ ] Edit preview is separate from Photos-library commit and app-owned export.
[ ] Adjustment data and reversibility are described in plain language.
[ ] Metadata and location policy is visible before export.
[ ] On-device AI proposals show source, uncertainty, and review action.
[ ] Liquid Glass supports hierarchy without obscuring media or imitating system chrome.
[ ] VoiceOver, Dynamic Type, Reduce Motion, contrast, keyboard, pointer, and Switch Control are tested.
[ ] Permission, limited-library, iCloud, missing-source, and unsupported-format recovery are usable.
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
- [PHImageManager](https://developer.apple.com/documentation/photos/phimagemanager)
- [PHLivePhoto](https://developer.apple.com/documentation/photos/phlivephoto)
- [PHLivePhotoView](https://developer.apple.com/documentation/photosui/phlivephotoview)
- [PHContentEditingInput](https://developer.apple.com/documentation/photos/phcontenteditinginput)
- [PHContentEditingOutput](https://developer.apple.com/documentation/photos/phcontenteditingoutput)
- [PHAdjustmentData](https://developer.apple.com/documentation/photos/phadjustmentdata)
- [PHLivePhotoEditingContext](https://developer.apple.com/documentation/photos/phlivephotoeditingcontext)
- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Live Photos HIG](https://developer.apple.com/design/human-interface-guidelines/live-photos)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
