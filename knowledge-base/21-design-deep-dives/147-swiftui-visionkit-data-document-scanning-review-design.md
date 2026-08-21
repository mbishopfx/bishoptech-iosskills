# SwiftUI VisionKit data and document-scanning design

This design route makes VisionKit capture feel native, calm, and reviewable. It pairs with the [framework review](../42-framework-deep-dives/119-swiftui-visionkit-data-document-scanning-review.md), the [capability route](../50-capability-recipes/150-swiftui-visionkit-data-document-scanning-review-route.md), the [proof matrix](../60-verification/144-swiftui-visionkit-data-document-scanning-proof-matrix.md), and the [recipes](../70-code-recipes/162-swiftui-visionkit-data-document-scanning-review-recipes.md).

The visual goal is not “a futuristic camera overlay.” The goal is a clear native workflow in which a person understands the source, the recognition state, the proposed result, and the next action. Liquid Glass can organize controls, but it must never hide the evidence that a person is being asked to review.

## 1. Choose the experience before choosing the treatment

Use a distinct design for each VisionKit surface:

| Surface | Person’s mental model | Primary screen |
| --- | --- | --- |
| Live data scanner | “Point the camera at text or a code, then select it” | Camera view with sparse guidance and an item review sheet |
| Document camera | “Capture pages, then review the document” | Page capture flow followed by page-aware review |
| Image analysis | “This image contains selectable information” | Image with system interaction affordances and a nearby source context |
| Custom Vision/Core ML | “The app is analyzing a frame or page” | Source preview plus explicit analysis status and a review card |
| Foundation Models handoff | “The app can help structure or explain what I selected” | Selected source, bounded proposal, warnings, and explicit apply |

Do not use a single generic “AI scan” label. The person needs to know whether the app is scanning a live camera, capturing a document, analyzing an existing image, or generating a suggestion from a selected observation.

## 2. Native screen hierarchy

### Live scanner

Recommended phone hierarchy:

1. navigation title or concise task title;
2. one-line purpose above or inside the camera experience;
3. system scanner view;
4. optional region-of-interest framing;
5. small status for permission or availability;
6. bottom action group for cancel, capture, or switch-to-import;
7. selected-item review sheet or card.

The scanner view should remain visually open. Use the system highlight and guidance first. A custom overlay should answer one question, such as “scan only the label inside this frame,” without competing with VisionKit’s feedback.

The selected-item review should show:

    recognized kind
    source text or barcode payload
    source location or page/frame note
    validation state
    copy, edit, save, open, or discard action

### Document capture

Recommended phone hierarchy:

1. task title and document purpose;
2. page count or current page context after capture;
3. document page preview;
4. page reorder/delete/add controls;
5. extraction status;
6. editable fields grouped by page;
7. export/save/discard action.

The finished camera capture is not the finished document. Show the scan first, then extraction, then review. A person should never wonder whether “Done” means the page was captured, OCR finished, or the record was saved.

### Image analysis

Keep the image itself central. Put source context, selection state, and app actions around it rather than drawing a heavy custom canvas over every recognized word. When the system Live Text interface is available, let it provide the familiar interaction. Use the app’s own controls for a destination action such as “add to draft” or “use this address.”

## 3. State is visible, not decorative

Use a small state language:

| State | Copy pattern | Visual treatment |
| --- | --- | --- |
| Checking | “Checking camera support” | Quiet progress, no false scanner controls |
| Permission needed | “Allow camera access to scan text and codes” | Primary permission action and import/manual fallback |
| Unsupported | “This device can’t use live scanning” | Explain the alternate route |
| Restricted | “Camera access is restricted” | Settings/recovery guidance |
| Ready | “Point at text or a code” | System scanner with minimal guidance |
| Scanning | “Scanning” | Avoid a redundant full-screen loading layer |
| Recognized | “1 item ready to review” | Review card or list; keep source visible |
| Stale | “This result is no longer in the current view” | Preserve the value but require reselect or confirm |
| Captured | “3 pages captured” | Page review, not a success checkmark alone |
| Analyzing | “Reading page 2” | Show page/source while work runs |
| Needs review | “Check 2 fields” | Focus the first field that needs attention |
| Saved | “Saved to …” | Confirm destination, not only a transient toast |
| Failed | “Couldn’t read this page” | Keep source and offer retry/import/manual entry |

Glass, color, and animation can reinforce a state, but every state must also be expressed in text, accessibility labels, and focus behavior.

## 4. Liquid Glass placement

Use Liquid Glass for small functional groups:

- a scan mode picker;
- a compact capture or stop control;
- source/page navigation;
- a review toolbar;
- a retry/import fallback group;
- a status capsule for “camera unavailable” or “2 fields need review.”

Keep these areas out of glass:

- long recognized transcripts;
- dense editable forms;
- document thumbnails that require careful comparison;
- warnings about privacy or irreversible actions;
- large source images where translucency harms edge contrast.

A restrained screen can use:

    stable source surface
      + sparse system scanner guidance
      + compact glass action group
      + opaque or high-contrast review card

Do not layer multiple glass materials over the camera feed merely to create depth. Material hierarchy should follow interaction hierarchy. If a button is part of the primary task, group it with related controls; if a result needs reading and correction, give it a stable surface.

When the person enables reduced transparency, the design should keep the same grouping, contrast, and action order. Test Liquid Glass fallbacks as a first-class visual state.

## 5. Camera composition and framing

The camera view should make the physical task obvious:

- use a short purpose statement;
- place the guidance near the region the person is aligning;
- avoid edge-to-edge controls where a hand will cover the source;
- do not put the only cancel action under the camera thumb zone;
- preserve system pinch-to-zoom when enabled;
- keep a clearly labeled import/manual route available.

For custom regions:

1. state what the region is for;
2. show a simple frame with enough quiet space around the expected source;
3. do not imply that content outside the frame is impossible to recognize unless the app enforces that policy;
4. keep the region and custom highlights in scanner-view coordinates;
5. test portrait, landscape, Dynamic Island/safe-area changes, and iPad split view.

A visible rectangle is guidance, not evidence that a recognized value came from inside it. Store the actual item bounds, source session, and any app-defined region to make the provenance inspectable.

## 6. Recognized-item review

The review card should be calm and factual:

    Phone number
    (555) 010-0123
    Found in live camera view
    [Copy] [Edit] [Use]

For a barcode:

    QR code
    https://example.invalid/path
    Check destination before opening
    [Copy] [Open after review] [Discard]

For multiple items, use a list with stable item IDs only for the current scan session. Provide:

- a clear count;
- reading order for text;
- type label;
- truncated but expandable content;
- source location or page/frame note;
- stale/unavailable status;
- selection or confirmation affordance.

Never use color alone to distinguish “new,” “selected,” “stale,” or “needs review.” A visual highlight can be paired with a text label and semantic state.

## 7. Document review is a reading task

People reviewing pages need comparison, not spectacle. Use:

- a page strip or sidebar;
- a large page preview;
- page index and title;
- extracted fields grouped by page;
- source crop or line reference when useful;
- deterministic validation messages;
- save/export controls that state the destination.

If the app extracts a name, address, date, amount, or identifier, show the original page or a crop beside the proposed field where space allows. On iPhone, a “View source” action can present the crop. On iPad and Mac, use a split view or inspector.

A page count is not proof of a complete document. A scan may contain blank, skewed, low-quality, duplicate, or out-of-order pages. Let the person add, reorder, delete, and re-run analysis where the product needs that control.

## 8. Image-analysis interaction

ImageAnalysisInteraction should feel like the system’s Live Text, not a custom annotation product. The app’s role is to:

1. show the source image with a clear context;
2. enable only the interaction types the task needs;
3. make the selected text or subject understandable;
4. offer a bounded app action after selection;
5. preserve the source image and current analysis revision.

When text selection is the main task, use a text-focused interaction type. When the image contains app-owned data such as a receipt or business card, data detectors can help the person select structured text before the app normalizes it.

Do not show visual lookup or subject-lift actions as if they are app-owned classification results. The system interaction and the app’s own downstream action should have distinct labels.

## 9. AI handoff design

The handoff should be a visible staircase:

    source page or selected item
      -> recognized observation
      -> normalized candidate
      -> “Ask on-device assistant” or equivalent
      -> generated proposal
      -> warnings and source references
      -> edit/reject/apply

The AI card should show:

- what source was selected;
- what the model was asked to do;
- generated content;
- uncertainty or missing-field warnings;
- source links or page/item references;
- an edit control;
- an explicit apply action.

Avoid labels such as “verified,” “correct,” or “understood” unless the app has deterministic evidence for that claim. Prefer “suggested,” “extracted,” “needs review,” or “based on page 2.”

If a proposal will open a URL, create a contact, send a message, write to HealthKit, change a setting, or trigger a device command, put the confirmation next to the side effect. The AI card is not the authorization boundary.

## 10. Accessibility task map

Test the whole task:

1. understand why camera access is needed;
2. grant, deny, or recover from permission;
3. start a scan;
4. identify that an item was recognized;
5. move to the item through semantic navigation;
6. hear its type, value, freshness, and source;
7. review and edit;
8. confirm or discard;
9. recover from unavailable, stale, or failed states.

Design requirements:

- use a semantic label for the scanner purpose;
- expose item lists and document pages outside tiny overlays;
- preserve focus after a new item appears;
- do not announce every geometry update;
- keep manual entry available;
- allow actions through VoiceOver, Voice Control, and Switch Control;
- support large text without truncating the source or action labels;
- test right-to-left text and mixed scripts;
- keep reduced motion and reduced transparency states intelligible.

For a custom highlight, the visual frame is secondary to the review card. The card should remain usable when the overlay is hidden or when the person cannot precisely point to the recognized bounds.

## 11. Error and fallback composition

Every capture screen should have a graceful alternative:

| Failure | Primary message | Fallback |
| --- | --- | --- |
| No scanner support | “Live scanning isn’t available on this device” | Import image or enter manually |
| Camera denied | “Camera access is off” | Settings, PhotosPicker, or manual entry |
| Camera restricted | “Camera use is restricted” | Explain without repeatedly requesting |
| Scanner becomes unavailable | “Scanning stopped” | Preserve selected source and offer retry/import |
| Document cancelled | “Scan cancelled” | Keep prior pages/draft |
| Document failure | “Couldn’t finish the document” | Retry or keep safe partial pages |
| OCR/analysis failure | “Couldn’t read this source” | Show source and manual fields |
| AI failure | “Suggestion unavailable” | Keep normalized candidate and manual edit |
| Save failure | “Nothing was lost” | Preserve reviewed draft and retry |

Do not put all failure routes behind a single “Try again” button. The best recovery can be import, manual entry, permission settings, a lower-resolution retry, or simply returning to the source.

## 12. iPad and Mac adaptation

On iPad:

- use a split view for source and review when the width allows;
- keep page thumbnails visible;
- place capture controls in a toolbar where pointer and keyboard users can find them;
- avoid a phone-sized bottom sheet that blocks the entire source.

On Mac Catalyst or macOS-supported image analysis surfaces:

- use the documented ImageAnalysisOverlayView route where appropriate;
- keep keyboard selection and copy behavior obvious;
- preserve source and target actions in the same window.

Do not make the iPad layout a stretched phone card. The capture source, item list, and review panel should adapt independently while sharing the same domain state and provenance.

## 13. Visual QA checklist

Check each surface with:

- light and dark appearance;
- Liquid Glass enabled and reduced transparency;
- Dynamic Type at the largest supported sizes;
- VoiceOver and keyboard focus;
- portrait, landscape, and iPad split view;
- long transcripts and long URLs;
- right-to-left text and mixed scripts;
- no results, one result, and many results;
- stale item after camera movement;
- denied, restricted, and unsupported states;
- page count one and many;
- low-quality page and duplicate page;
- AI proposal with missing fields;
- save failure and retry.

The visual pass is complete only when the person can identify the source, the proposed value, the review requirement, and the next action in every state.

## Stop conditions

- A custom glass overlay competes with the system scanner or hides source evidence.
- The design suggests that a highlight is a confirmed field.
- The only item interaction is a precise tap on a camera overlay.
- A document “Done” state does not distinguish capture, analysis, review, and save.
- An AI result is shown without the selected source or an edit/reject path.
- Permission, unsupported, unavailable, and manual fallback states are missing.
- Reduced transparency, Dynamic Type, VoiceOver, or alternate input breaks the complete task.
- A stretched phone layout prevents source/review comparison on iPad or Mac.

## Sources

- [VisionKit](https://developer.apple.com/documentation/visionkit)
- [Scanning data with the camera](https://developer.apple.com/documentation/visionkit/scanning-data-with-the-camera)
- [DataScannerViewController](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller)
- [DataScannerViewControllerDelegate](https://developer.apple.com/documentation/visionkit/datascannerviewcontrollerdelegate)
- [RecognizedItem](https://developer.apple.com/documentation/visionkit/recognizeditem)
- [VNDocumentCameraViewController](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontroller)
- [VNDocumentCameraViewControllerDelegate](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontrollerdelegate)
- [VNDocumentCameraScan](https://developer.apple.com/documentation/visionkit/vndocumentcamerascan)
- [ImageAnalyzer](https://developer.apple.com/documentation/visionkit/imageanalyzer)
- [ImageAnalysis](https://developer.apple.com/documentation/visionkit/imageanalysis)
- [ImageAnalysisInteraction](https://developer.apple.com/documentation/visionkit/imageanalysisinteraction)
- [InteractionTypes](https://developer.apple.com/documentation/visionkit/imageanalysisinteraction/interactiontypes)
- [SwiftUI UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [SwiftUI UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
