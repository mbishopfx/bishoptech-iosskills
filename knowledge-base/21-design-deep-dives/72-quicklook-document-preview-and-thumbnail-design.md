# Quick Look document preview and thumbnail design

Quick Look design is about helping people recognize, inspect, and decide what to do with a file while preserving the system’s authority over the preview surface. The app owns the surrounding task; Quick Look owns the standard preview experience.

## Recognition before inspection

Use a three-level hierarchy:

~~~text
thumbnail or icon -> identify the item
Quick Look preview -> inspect the content
app-owned editor/review -> change, analyze, or commit
~~~

Each level should have its own state. A thumbnail can be unavailable while the preview works. A preview can be readable while the app parser fails. An AI proposal can be incomplete while the source file remains valid.

For a document row or grid tile, prioritize:

- human-readable title;
- file type or a meaningful content description;
- source or location when it changes the user’s decision;
- revision or unsaved state when relevant;
- thumbnail progress/error state;
- one clear preview action.

Avoid making every file tile a decorative glass card. Use spacing, typography, and semantic controls to create the Apple-native hierarchy; reserve material effects for a small container or action region that benefits from grouping.

## The preview handoff

The app-owned screen should explain why the preview opens and what the person can do next. The transition can be simple:

~~~text
document row
  -> preview action
  -> Quick Look
  -> return to source list or review screen
~~~

Do not duplicate Quick Look’s toolbar, markup controls, page navigation, or media controls in the app’s surrounding shell. A duplicate control can create contradictory state and make it unclear whether a change belongs to the system preview or the app’s canonical document.

If the app needs an advanced inspector, playback controller, annotation model, or side-by-side AI explanation, use a lower-level framework and name that as a different product route. Quick Look is the right surface when the user mainly needs a standard preview with Apple’s familiar interactions.

## Liquid Glass placement

Liquid Glass can frame:

- a document list toolbar;
- a compact preview/review action;
- a source-location or revision capsule;
- an app-owned AI review panel shown after Quick Look;
- a small status control that explains thumbnail generation.

It should not obscure file identity, reduce text contrast, or visually imitate a system-owned Quick Look surface. Keep important text on a stable background and allow the system preview to use its own appearance.

Good glass behavior:

- the material groups related app-owned actions;
- the action remains legible in light/dark and high-contrast modes;
- the glass morphs only when there is a meaningful identity transition;
- reduced transparency leaves a clear opaque fallback;
- motion explains the transition without implying that a document was saved.

## Custom formats

Custom file types need a consistent product language across the app, Files, Spotlight, and Quick Look:

| Surface | Design responsibility |
| --- | --- |
| App list | Explain the document and show a useful thumbnail or generic icon. |
| Quick Look preview | Provide an inspectable view that does not require app navigation. |
| Thumbnail Extension | Render a recognizable, truthful miniature at the requested size. |
| File Provider | Keep titles, revisions, placeholders, and availability consistent. |
| AI review | Show source location and preserve the original file revision. |

Avoid a thumbnail that is just a tiny screenshot of a busy editor. At small sizes, choose a stable composition: document title, one dominant visual, clear type cue, and no unreadable microtext. If the file contains sensitive content, consider whether a generic icon is safer than a revealing thumbnail in Files or Spotlight.

## AI review after Quick Look

Treat Quick Look as an inspection step and AI as a separate user-started action:

1. the person selects or opens a file;
2. the app shows the system preview;
3. the person chooses Analyze, Extract, Summarize, or another named action;
4. the app displays the source scope and privacy impact;
5. the local model or parser produces a proposal;
6. the app shows source locations and editable fields;
7. the person confirms an app-owned save/export/action.

Do not trigger AI because a thumbnail was requested. Thumbnail requests can originate from system surfaces and do not represent an intent to analyze the file. The thumbnail also may not contain enough information to support an accurate conclusion.

## State language

Use precise states:

| State | User-facing language |
| --- | --- |
| Thumbnail pending | “Preparing preview image…” |
| Generic icon fallback | “Preview image unavailable” |
| Preview unavailable | “This file can’t be previewed here” |
| Provider download | “Getting the file from its source…” |
| Stale source | “This file changed; refresh before analyzing” |
| AI proposal | “Suggested from page 2” or another source-linked label |
| App-owned save | “Saved to this app” |
| System edit result | “Quick Look saved an edited copy” where the delegate proves that result |

Never use “Saved” as a generic status after a preview opens.

## Accessibility and files as personal data

Use meaningful accessibility labels for filenames, type, revision, thumbnail state, and actions. Do not make the image itself the only way to identify a document. Test long filenames, localized extensions, right-to-left text, large Dynamic Type, VoiceOver, Voice Control, Switch Control, keyboard navigation, reduced motion, and reduced transparency.

If a thumbnail contains a person’s face, health information, financial data, or private writing, test how it appears in Files, Spotlight, search results, widgets, and locked-device contexts. A thumbnail may travel farther than the in-app screen that created it.

## Sources

- [File management](https://developer.apple.com/design/human-interface-guidelines/file-management)
- [Quick Look](https://developer.apple.com/documentation/quicklook)
- [QLPreviewController](https://developer.apple.com/documentation/quicklook/qlpreviewcontroller)
- [QLPreviewControllerDelegate](https://developer.apple.com/documentation/quicklook/qlpreviewcontrollerdelegate)
- [Quick Look Thumbnailing](https://developer.apple.com/documentation/quicklookthumbnailing)
- [QLThumbnailGenerator](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailgenerator)
- [QLThumbnailRepresentation](https://developer.apple.com/documentation/quicklookthumbnailing/qlthumbnailrepresentation)
- [Providing Thumbnails of Your Custom File Types](https://developer.apple.com/documentation/quicklookthumbnailing/providing-thumbnails-of-your-custom-file-types)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
