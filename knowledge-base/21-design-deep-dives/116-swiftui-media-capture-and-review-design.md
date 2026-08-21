# SwiftUI media capture and review design

## Design goal

Media features feel native when source selection, live capture, transfer state,
model output, and the final destination are visually distinct.

Use this flow:

~~~text
choose or capture
    -> prepare representation
    -> preview and inspect
    -> optional on-device observation
    -> review and edit
    -> save in app, export, or save to Photos
~~~

The large image or viewfinder remains primary. Liquid Glass groups the few
controls that help the current task. It never substitutes for source identity,
permission copy, uncertainty, or a destination label.

## Choose the entry point

| User intent | Native entry | Design response |
| --- | --- | --- |
| Bring in an existing photo/video | PhotosPicker | System picker first; show selected scope and transfer state |
| Capture a moment | Custom AVFoundation camera | Large viewfinder, minimal controls, clear shutter/record state |
| Scan text/document | VisionKit or camera route | Show recognized result as editable content before saving |
| Review a video | VideoPlayer/AVPlayerViewController | Use native transport and playback behavior |
| Apply an image model | Vision/Core ML | Show source-linked observation and review |
| Create a structured record | Media plus form/editor | Keep generated fields editable and provenance visible |
| Save to library | PhotoKit change | Name Photos as the external destination and show result |

Do not add a custom camera screen simply because the product has a camera
button. The system picker is usually the least-privilege path for existing
media.

## The screen anatomy

### Picker-to-review

~~~text
Choose media
    -> selected source count/type
    -> loading or iCloud download
    -> preview
    -> [Analyze] [Replace] [Cancel]
    -> observation/review
    -> [Save in app] [Export] [Save to Photos]
~~~

### Camera-to-review

~~~text
camera permission explanation
    -> viewfinder
    -> capture/record controls
    -> processing
    -> preview with metadata/source state
    -> [Retake] [Edit] [Use photo/video]
    -> optional model review
    -> named destination
~~~

Keep the first screen focused. Do not put a full metadata inspector, model
explanation, and destination chooser over the viewfinder before a capture
exists.

## Source state is visible

A media preview needs a state model:

| State | User-facing language |
| --- | --- |
| selection placeholder | “Preparing selected media” |
| iCloud retrieval | “Downloading from iCloud” |
| transfer progress | “Loading photo” or “Loading video” |
| unavailable | “This item can’t be loaded” |
| camera permission | “Camera access is needed to capture a photo” |
| camera ready | “Ready to capture” |
| capture in progress | “Capturing” or “Recording” |
| processing | “Preparing preview” |
| model ready | “Ready to review on this device” |
| model result | “Suggested result” or “Detected text” |
| insufficient evidence | “No reliable result” |
| stale source | “Source changed; run again” |
| saved | “Saved in app,” “Exported,” or “Saved to Photos” |

An image-only spinner is not enough. VoiceOver, Dynamic Type, and reduced
transparency should expose the same state.

## Consent and privacy language

Treat choosing or capturing as a user-controlled scope:

- “Choose a photo” means selected assets only;
- “Allow access to all photos” is a broader permission decision;
- “Use camera” explains what is captured and when;
- “Process on this device” describes processing location, not retention;
- “Save to Photos” means a Photos library write;
- “Save in app” means an app-owned record;
- “Export” means a file destination;
- “Delete source” needs its own explicit action.

Ask for camera/microphone permission at the moment the feature needs it. Do not
ask for full library read access to implement a one-off picker selection. Use
truthful usage descriptions and show a useful denied/restricted fallback.

## Media identity and review

Display enough source context to prevent accidental application:

~~~text
selected image/video
  type · capture/import date · representation
  optional source identifier or album context
  model name/version and local-processing note
  observation or suggestion
  [Edit] [Accept] [Discard]
~~~

Do not expose precise GPS, private filenames, or unrelated EXIF by default.
Separate:

| Fact | Example |
| --- | --- |
| Source | A user-selected HEIF photo |
| Observation | Vision found text in a region |
| Proposal | App suggests a title |
| Review | Person edited and accepted the title |
| Commit | App saved the record |
| Side effect | App wrote a new Photos asset |

A model label does not become a fact because it is rendered over the image.

## Liquid Glass hierarchy

Use a small number of glass groups:

~~~text
source/viewfinder
    -> capture or select control
    -> state/progress control
    -> review action group
    -> destination action
~~~

Good groups:

- a capture/select control cluster;
- a cancel/retry progress cluster;
- a source-linked review toolbar;
- a compact destination/status group.

Avoid:

- a frosted full-screen overlay over the photo;
- duplicated Camera Control controls inside the viewfinder;
- a confidence ring with no text;
- a glass pill that says “done” for all destinations;
- glossy animation that implies inference certainty;
- fake system picker or camera chrome.

Glass should disappear or become opaque without changing the task semantics.
Test it over light, dark, HDR, portrait, video, loading, and error states.

## Camera controls and system surfaces

When the system Camera Control or another system overlay is present, leave the
documented overlay area clear. Use short labels and familiar SF Symbols.
Avoid duplicating controls the system already exposes. Design portrait and
landscape separately.

A custom capture UI should prioritize:

- viewfinder;
- shutter/record;
- camera switch;
- flash or exposure only if needed;
- stop/cancel;
- clear permission/error state.

Move advanced settings into a focused sheet or inspector. The person should not
hunt through glass controls while trying to capture a moment.

## Photo/video review

Use a review step before a consequential action:

| Review type | Show |
| --- | --- |
| Still photo | large preview, orientation, crop/edit, source state |
| Live Photo | motion/playability state and still fallback |
| Video | native playback, duration, trim/export state |
| OCR | recognized text with editable correction |
| Object/scene observation | source region, label, uncertainty/availability |
| Generated title/tags | proposal, source, edit, accept/discard |
| Photos save | destination, new asset/edit, success/failure |

Keep a Retake/Choose another route near the preview. Do not trap the user in
a processing state with no cancellation.

## Metadata and export design

For an export or derived image, name the metadata choice:

- preserve orientation;
- remove GPS;
- keep or remove camera/device details;
- preserve HDR/depth/gain-map only when the destination supports it;
- flatten edits or preserve an adjustment recipe;
- choose the output type and filename;
- show the destination and cancellation path.

Metadata is not a decoration. It can reveal location, device, timestamps, faces,
documents, or workflow details. Give the user an understandable policy when
the feature changes it.

## On-device review design

Use deterministic media observations first when they fit the task:

~~~text
source representation
    -> orientation/size normalization
    -> Vision/Core ML observation
    -> source-linked candidate
    -> person review
    -> app-owned commit
~~~

Use Foundation Models after extracting bounded text/regions/labels when a prose
or structured proposal is needed. For every result, show:

- what source was used;
- what the system/model did;
- whether the result is partial, unavailable, or stale;
- what the person can edit;
- what action commits it;
- where the result will be saved.

The feature must remain useful with no model, no network, no iCloud download,
denied permission, or failed transfer.

## Accessibility and input

The media task must work with:

- VoiceOver descriptions for source, progress, preview, model state, and
  actions;
- Voice Control and Switch Control;
- Dynamic Type and large accessibility sizes;
- increased contrast, reduced transparency, and reduced motion;
- hardware keyboard and pointer on iPadOS/Catalyst;
- alternate capture or import path when camera hardware is unavailable;
- no color-only confidence/permission/error language;
- no swipe-only discard or save action.

For images, expose a meaningful content description only when the app has a
source-linked result; do not state uncertain inference as verified fact. For
video, expose playback state and a text alternative where appropriate.

## Adaptive targets

| Target | Design |
| --- | --- |
| iPhone | immersive capture/compact review; keep controls sparse |
| iPadOS | split/Stage Manager-aware preview and inspector; keyboard/Pencil |
| Mac Catalyst | file/import/review shell, menu/pointer, camera availability check |
| visionOS | use windows/spatial media only when the task benefits; no unsupported capture claim |
| watchOS | projection/remote trigger, not full media editing |
| Locked Camera Capture | respect locked-device limits and minimal launch route |

A physical iPhone is required for camera, microphone, haptics, Camera Control,
and real Photos/iCloud evidence. A simulator is useful for state/layout
fixtures only.

## Design acceptance checklist

- The entry point matches the user's intent: choose, capture, scan, or review.
- Source, representation, preview, observation, proposal, and destination are
  separate facts.
- Permission and usage copy matches the actual code path.
- Picker and camera state include loading, cancellation, failure, and retry.
- The viewfinder leaves system overlay space and keeps controls minimal.
- Video uses native AVKit playback behavior where appropriate.
- Metadata and export policy are visible before a side effect.
- Model output is labeled and editable, with source/revision provenance.
- Liquid Glass groups actions and has an accessible opaque fallback.
- The task works when Photos, camera, model, network, or hardware is unavailable.
- Physical-device, privacy, performance, archive, and release evidence are
  tracked separately.

## Sources

- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [Bringing Photos picker to your SwiftUI app](https://developer.apple.com/documentation/PhotoKit/bringing-photos-picker-to-your-swiftui-app)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [AVFoundation Capture setup](https://developer.apple.com/documentation/avfoundation/capture-setup)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [Camera Control HIG](https://developer.apple.com/design/human-interface-guidelines/camera-control)
- [Live Photos HIG](https://developer.apple.com/design/human-interface-guidelines/live-photos)
- [AVKit](https://developer.apple.com/documentation/avkit)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [AVPlayerViewController](https://developer.apple.com/documentation/avkit/avplayerviewcontroller)
- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [Vision](https://developer.apple.com/documentation/vision)
- [RecognizeTextRequest](https://developer.apple.com/documentation/vision/recognizetextrequest)
- [CoreMLRequest](https://developer.apple.com/documentation/vision/coremlrequest)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
