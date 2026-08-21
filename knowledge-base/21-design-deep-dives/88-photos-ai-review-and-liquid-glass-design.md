# Photos selection, on-device AI review, and Liquid Glass design

## Design goal

Photo features feel native when the user’s selection, the source state, the model output, and the library side effect are visually separate. The system picker should feel like a system picker. The app’s review surface should feel like the app. Liquid Glass should group actions without hiding the image, privacy scope, or uncertainty.

The design loop is:

`choose -> load -> inspect -> suggest -> review -> save/export/discard`

## Selection is a consent moment

Treat the `PhotosPicker` action label as a clear user intent: “Choose photo,” “Choose images,” or “Choose video.” Do not label it as “Analyze everything” when the route selects a bounded set. If full library access is actually needed, explain the reason before requesting it and show limited/denied/restricted states.

After selection, show:

- the selected count or source name;
- loading/progress state when iCloud or a file transfer is involved;
- the representation being used, such as preview/current/original;
- cancel/retry behavior;
- what will happen next, especially if an AI model runs locally.

Do not treat the picker’s placeholder as a rendered image. Avoid a blank card that gives no indication whether the item is still loading, unavailable, or intentionally filtered.

## Review surface anatomy

```text
selected source
  image/video preview or accessible source summary
  source type · modification date · selected representation
  model status · model version · local processing note
  suggestion / detected candidate / not enough evidence
  evidence or source details
  [Edit] [Accept/save] [Discard] [Choose another]
```

Use “save to Photos” only for a Photos library mutation. Use “save in app” for an app-owned record. If both are possible, make them separate actions. For edits, show a before/after comparison and name whether the result is a new asset, an edit to the existing asset, or only a derived app copy.

## Liquid Glass composition

Use glass for a compact action group, review status, or selection toolbar. Keep it anchored near the task without turning the photo into a decorative backdrop. Prefer standard SwiftUI controls and system picker presentation, then style a small app-owned review surface.

Good glass groups:

- selection actions and filters;
- model status with retry/cancel;
- compact edit/accept/discard actions;
- a source-linked result summary.

Avoid:

- a full-screen frosted overlay over the source;
- a confidence ring with no text or explanation;
- an “AI” icon standing in for provenance;
- a glass save button that silently writes to Photos;
- motion that suggests a result is certain or verified.

Test over bright/dark/HDR images, empty/loading/error states, large Dynamic Type, reduced transparency, increased contrast, reduced motion, and right-to-left layout. The hierarchy should survive if blur, translucency, or animation is reduced.

## Model states are design states

Render distinct state labels:

| State | UI language |
| --- | --- |
| Placeholder | “Preparing selected photo” |
| Loading | “Loading selected media” with progress/cancel |
| Needs network | “Photo is in iCloud; allow download to continue” |
| Ready | “Ready to analyze on this device” |
| Processing | “Analyzing selected photo” |
| Suggestion | “Suggested label” or “Detected candidate” |
| Not enough evidence | “No reliable suggestion” |
| Failed | “Couldn’t load this item” with retry |
| Stale | “Source changed; run again” |
| Saved | “Saved in app” or “Saved to Photos,” never just “Done” |

Do not reuse the last model output after the selected item changes unless the UI clearly labels it as stale or associated with the previous source.

## Accessibility and alternate representation

The photo itself cannot be the only way to understand the task. Supply accessible labels for selected source, media type, loading/error/progress state, model suggestion, source timestamp, and every action. A grid should expose position/count where useful. A review flow must be completable with VoiceOver, Voice Control, Switch Control, keyboard, pointer, and Dynamic Type.

When the output describes visual content, distinguish an image description from verified fact. Preserve user-editable text and let the person correct the result. Do not hide “discard” in a swipe-only gesture. Do not announce a confidence color without its text equivalent.

## Privacy-first copy

Explain local processing accurately:

- “This photo is processed on this device” is an implementation statement.
- “We do not save the photo” is a retention promise and needs deletion/log review.
- “Choose more photos” is a scope expansion and needs the system flow.
- “Save to Photos” is an external library mutation, not a local UI state.

Keep private EXIF, precise location, faces, documents, and unrelated album context out of the AI context unless the feature needs them and the person understands the use. If the model creates a derived image, show whether the source is retained, replaced, or copied.

## Photo editing UX

For a non-destructive PhotoKit edit, present a review that names the edit and keeps the source recognizable. Show the original/current/edited distinction. If adjustment data can be reconstructed, let the user continue editing. If not, explain that the app will work from the rendered current version.

Group multiple Photos changes only when the user understands them as one action. A success callback means Photos applied the request; the app should still reconcile its projection through change observation.

## Design acceptance checklist

| Question | Pass condition |
| --- | --- |
| Is selection explicit? | The action and selected scope are visible before processing. |
| Is transfer state honest? | Placeholder, loading, iCloud retrieval, nil, error, and cancellation are distinct. |
| Is model output reviewable? | Source, model state/version, suggestion, uncertainty, edit, and reject are present. |
| Is saving unambiguous? | App persistence, file export, and Photos mutation are separate named actions. |
| Does Liquid Glass support hierarchy? | Controls remain legible and bounded over real media and reduced-effects settings. |
| Is the route accessible? | The task works without image-only cues, color, motion, or swipe-only actions. |
| Is privacy copy accurate? | Access scope, local processing, retention, download, and deletion match implementation. |
| Is change reconciliation designed? | External Photos edits/deletes invalidate or refresh app projections. |

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [Bringing Photos picker to your SwiftUI app](https://developer.apple.com/documentation/PhotoKit/bringing-photos-picker-to-your-swiftui-app)
- [PHPhotoLibrary](https://developer.apple.com/documentation/photos/phphotolibrary)
- [PHAuthorizationStatus](https://developer.apple.com/documentation/photos/phauthorizationstatus)
- [PHAsset](https://developer.apple.com/documentation/photos/phasset)
- [PHImageManager](https://developer.apple.com/documentation/photos/phimagemanager)
- [PHContentEditingInputRequestOptions](https://developer.apple.com/documentation/photos/phcontenteditinginputrequestoptions)
- [PHPhotoLibraryChangeObserver](https://developer.apple.com/documentation/photos/phphotolibrarychangeobserver)
- [Core Transferable](https://developer.apple.com/documentation/CoreTransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [DataRepresentation](https://developer.apple.com/documentation/coretransferable/datarepresentation)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
