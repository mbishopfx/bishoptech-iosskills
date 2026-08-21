# Privacy-first media and document surfaces

## Design goal

A media or document feature should feel like an extension of Photos, Files, Preview, or a native document app without pretending to own content the person has not selected or authorized. The design should make scope visible:

~~~text
what did the person choose?
what can the app access now?
what representation is loading?
what will be retained?
what will AI change?
what will be exported or shared?
~~~

Do not hide these answers inside a permission prompt, a loading spinner, or an AI-generated summary.

## Surface choice by intent

| Intent | Best first surface | Why |
| --- | --- | --- |
| Choose a few photos for an immediate task | PhotosPicker | System-owned selection with selected-item scope |
| Browse and organize the full library | PhotoKit-backed app surface | Explicit authorization and change reconciliation |
| Open an external file | fileImporter/UIDocumentPicker | User-mediated provider access |
| Edit a document | DocumentGroup or focused document editor | Autosave, format, and scene lifecycle can be explicit |
| Preview a file | Quick Look | Familiar system preview and supported-type behavior |
| Read/mark up a PDF | PDFView/PDFKit | Page/text/annotation semantics |
| Send a copy | ShareLink | System share surface and explicit Transferable representations |
| Sync a remote document collection | File Provider | Other apps can discover the app-owned provider |

The system surface choice is part of the product identity. A custom fake photo library or a permanent custom file browser often adds complexity without producing a more native experience.

## Screen architecture

Use a focused hierarchy:

1. Source explanation and primary choose/open action.
2. Source scope and current access status.
3. Selected items or document list.
4. Preview/reader surface.
5. Reviewable AI or metadata proposal.
6. Save/export/share action.

Keep the source content dominant. Use Liquid Glass for functional controls:

- a compact toolbar over a preview;
- a grouped extraction/review action row;
- a status card for loading/provider state;
- an inspector for metadata and provenance.

Avoid placing a translucent glass panel over dense text or detailed imagery. The material should help the person find actions without reducing the legibility of the content that motivated the action.

## State-driven design

Use explicit source and processing states:

| State | UI copy/feedback | Primary recovery |
| --- | --- | --- |
| no source | “Choose a photo or document” | Open picker/importer |
| selection cancelled | Preserve current draft | Choose again |
| loading representation | “Preparing selected item” | Cancel/retry |
| iCloud/provider download | Explain that content is being retrieved | Wait/cancel |
| unsupported format | Name the format and supported alternatives | Choose another or preview |
| limited access | Explain that access is limited to selected items | Manage access or continue |
| scope unavailable | Explain that the file must be selected again | Reselect |
| draft ready | Show source, extracted fields, and editable content | Review |
| AI proposal ready | Label it as a suggestion | Accept/edit/reject |
| saving | Show destination and cancellability | Wait/cancel |
| external change | “This file changed elsewhere” | Reload/compare/keep a copy |
| provider unavailable | Separate offline from deleted | Retry/local copy |
| export complete | Show the created destination/result | Open/share |
| deletion/revocation | Remove derived access and explain what remains | Reimport or delete |

Never use a green checkmark alone to communicate that the source was saved, synced, or shared. State the destination and the evidence you actually have.

## Photo selection surfaces

PhotosPicker is a strong default for a feature that needs user-selected media. The surrounding app should:

- state why the image/video is needed;
- show selection count and supported types;
- show a selected-item thumbnail only after the picker returns it;
- preserve the original source identity when the representation loads;
- distinguish a local preview from an imported durable copy;
- let the person remove an item before AI processing or saving.

For library-management features, show current authorization and limited-library behavior. Do not make the person guess why an existing photo is missing; distinguish “not selected,” “limited access,” “not downloaded,” “deleted,” and “unsupported.”

## File and document surfaces

### Import

An importer should show:

- allowed file types;
- whether the app copies or edits in place;
- whether a provider download may occur;
- size or processing limits;
- what will be stored after import.

If the app opens a security-scoped URL, the UI does not need to expose the implementation term, but it should provide a meaningful reselect state when access expires or a provider changes the file.

### Document editor

Use a native document hierarchy:

- document title and save status;
- predictable undo/redo;
- focused content editing;
- inspector/details in a sheet or secondary column;
- explicit export/share;
- conflict or external-change resolution;
- accessible content and keyboard/pointer routes.

Do not place a destructive Delete or Replace action beside Save with identical visual weight. Document work is often long-lived and expensive to recreate.

### Preview and PDF

Use Quick Look when preview is the user’s goal. Use PDFKit when page navigation, search, selection, annotations, or editing is part of the product. A PDF page preview should not be confused with a parsed, trusted document model.

For PDF annotations, show the page context and the annotation type. For AI highlights, show the source page/selection and provide an undo/reject action. Do not auto-open a link annotation merely because a model or parser found one.

## Provider and offline design

File Provider content can be remote, placeholder-backed, or mid-sync. Use a row or inspector that communicates:

- local/materialized versus remote;
- last-known revision;
- upload/download progress;
- offline/unavailable;
- conflict;
- pending action.

Keep the main app usable when the provider is offline. A cached, read-only preview can be a better fallback than a blocking spinner, but label it as cached and prevent edits that cannot be committed.

## AI review surface

Use a three-column mental model even on a compact phone screen:

| Column | Content |
| --- | --- |
| Source | Thumbnail/page/selection and provenance |
| Proposal | Extracted field, summary, tag, rewrite, or action draft |
| Decision | Edit, accept, reject, save, export, or share |

On iPhone, this can become a stacked card flow. On iPad, it can become a split view. Keep the source visible while reviewing high-consequence proposals.

AI copy should say:

- “Suggested title”
- “Extracted fields — review”
- “Draft summary”
- “Possible duplicate”

Avoid:

- “Verified” when the model only inferred;
- “Safe to share” without a deterministic privacy policy;
- “Saved” before the file/document/Photos/provider operation completes;
- “Recognized” as a guarantee when the source is ambiguous.

## Accessibility and alternate input

Source and action semantics must survive the visual design:

- picker/import/share controls need concise labels;
- source thumbnails need meaningful labels and selected state;
- page/field relationships need VoiceOver ordering;
- AI proposals need explicit acceptance/rejection actions;
- progress must have a textual status;
- PDF annotations need accessible type and page context;
- document rows need keyboard/pointer activation where supported;
- no state may rely on color, blur, motion, or haptics alone.

Test with Dynamic Type and long localized strings. A glass toolbar that looks balanced at the default size can become a clipped or unreachable action row. Allow actions to wrap, move to a menu, or become a larger sheet.

## Privacy-forward empty and error states

An error message should not leak sensitive content. Prefer:

- “This document is unavailable” over showing a provider URL or account detail;
- “The selected file could not be read” over displaying raw parser output;
- “Review the selected fields before saving” over a notification containing extracted health/financial text;
- “Access changed” over assuming the person revoked access intentionally.

Logs and diagnostics should use stable internal IDs rather than names, page text, photo captions, or raw provider paths. A debug build still needs deliberate redaction when using real personal data.

## Liquid Glass checklist

- Use standard system pickers and sharing surfaces when they express the intent.
- Apply glass to action groups, not the source content itself.
- Keep primary action labels explicit and stable.
- Ensure the material has a reduced-transparency fallback.
- Preserve contrast for document text, PDF annotations, and media controls.
- Avoid morphing a toolbar while an async source is loading unless focus and VoiceOver order remain stable.
- Keep destructive actions outside an ambiguous glass group.
- Test in light/dark mode, large text, reduced motion, Increased Contrast, and iPad split view.

## Design review questions

- Can the person tell whether the app has a selected item or broad library access?
- Can they see what will be retained before AI processing?
- Can they identify the source page/asset behind each proposal?
- Can they recover from iCloud/provider download failure?
- Can they edit in place without losing a copy?
- Does a preview remain useful when the file type is unsupported for editing?
- Is the share projection redacted before the share sheet opens?
- Can the core task be completed with VoiceOver and without precise gestures?
- Is “saved,” “synced,” and “shared” evidence-based?

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PHPhotoLibrary](https://developer.apple.com/documentation/photos/phphotolibrary)
- [Delivering an Enhanced Privacy Experience in Your Photos App](https://developer.apple.com/documentation/photokit/delivering-an-enhanced-privacy-experience-in-your-photos-app)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [ReferenceFileDocument](https://developer.apple.com/documentation/swiftui/referencefiledocument)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [File importer and exporter presentation](https://developer.apple.com/documentation/swiftui/view-presentation)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [startAccessingSecurityScopedResource](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [NSFileProviderReplicatedExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderreplicatedextension)
- [Quick Look](https://developer.apple.com/documentation/quicklook)
- [Quick Look Thumbnailing](https://developer.apple.com/documentation/quicklookthumbnailing)
- [PDFKit](https://developer.apple.com/documentation/pdfkit)
- [PDFView](https://developer.apple.com/documentation/pdfkit/pdfview)
- [PDFAnnotation](https://developer.apple.com/documentation/pdfkit/pdfannotation)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
