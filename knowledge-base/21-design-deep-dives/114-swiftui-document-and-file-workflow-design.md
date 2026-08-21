# SwiftUI document and file-workflow design

## Design premise

Document features combine a long-lived user task with a system-managed file
surface. Design the document browser, editor, file status, provider state,
and optional AI review as one understandable workflow with separate ownership.

Use this loop:

~~~text
document task
    -> content type and file identity
    -> browser/open/create
    -> editor and dirty state
    -> autosave/version/conflict
    -> export/share/provider
    -> optional AI review
    -> explicit commit and proof
~~~

The visual goal is native document confidence, not a decorative replica of
Pages, Preview, Files, or another Apple app.

## 1. Start with the person's file task

| Task | Native surface | Design promise |
| --- | --- | --- |
| Create a new document | DocumentGroup/new-document action | A clear document identity and safe first save |
| Open an existing document | DocumentGroup or fileImporter | Only supported types appear; stale/provider states are recoverable |
| Edit a document | Native editor/document scene | Changes are visible, undoable, and saved according to an explicit policy |
| Export a copy | fileExporter | Source remains safe; destination and result are clear |
| Move a document | fileMover | Location changes only after success |
| Share a projection | ShareLink/Transferable | The user understands what leaves the app |
| Review remote/provider files | Files/File Provider/document browser | Local, remote, placeholder, and conflict states are visible |
| Ask AI to help | In-document review panel or focused task | Candidate is sourced, reviewable, and uncommitted until confirmed |

Avoid placing every operation in a custom toolbar. Use system document commands,
menus, keyboard shortcuts, toolbar placement, and share controls where they
fit the platform.

## 2. Make file status legible

A person should be able to answer:

- Which document is open?
- Where is it stored?
- Is it saved, saving, offline, conflicted, or read-only?
- What will happen if I close or move it?
- What content type and version does it use?
- Can I export a copy?
- Is an AI suggestion still based on the current document?

Use semantic text and familiar system affordances. Keep internal terms such as
security-scoped URL, File Provider placeholder, or source revision in
diagnostics unless they help the person recover.

Suggested status hierarchy:

~~~text
document title
    -> saved / saving / unavailable / conflict
    -> source location or account when useful
    -> current task actions: edit, export, share, move, review
~~~

Do not rely on a tiny colored dot, translucency, or a custom glass badge as the
only indicator of unsaved or conflicted work.

## 3. Browser and editor are different surfaces

A document browser helps choose, create, move, and organize files. An editor
helps read, change, review, and save one document.

On iPhone, the browser may become a focused flow. On iPadOS and Catalyst, users
expect a broader workspace with keyboard commands, split views, file menus,
and resizable content. On visionOS, use the documented window and spatial
composition. On watchOS, document browsing and editing are not the normal
platform task.

If the browser and editor share code, share semantic models and actions; do
not force the same layout, navigation depth, toolbar, or input route.

## 4. Document identity and window identity

A document file can be opened in a scene/window, but these are different
identities:

| User-facing concept | Internal contract |
| --- | --- |
| File name/title | Presentation and localization |
| File URL | Current location/access boundary, not necessarily durable identity |
| Document ID | Stable app/file identity when the format supports one |
| Scene/window | Current UI instance and restoration scope |
| Domain record | App-owned validated meaning |
| File version | Current byte/version state |
| AI candidate | Derived proposal tied to document revision |

When the file moves, update the presentation location after the system reports
success. When a provider changes the file, reconcile through the document
lifecycle. When a document is opened twice, define whether the app supports
two windows, one shared editor, or a conflict/duplicate policy.

## 5. Autosave is a confidence feature

People expect document work to be preserved without manually hunting for Save.

Design:

- show a calm saving state during writes;
- do not block typing for every autosave;
- coalesce rapid edits with bounded backpressure;
- preserve a recovery route after termination or provider failure;
- surface conflicts instead of silently selecting last writer;
- make read-only and offline states actionable;
- keep undo/redo meaningful across autosave;
- test close, background, move, and account change as save boundaries.

Do not write “saved” when only an asynchronous write has started. The status
should reflect the result that the document layer can support.

## 6. Import/export/share language

Use user-facing words consistently:

- Open or Import depending on whether the source becomes an ongoing document;
- Export for a new copy;
- Move for changing the file location;
- Share for sending a representation;
- Save or Done according to the document task and platform convention.

Explain what happens to the original. If an AI-generated output is exported,
say whether it is a copy, a suggested edit, or the current document.

For large assets, a file representation can avoid loading the whole file into
memory. The UI should still show progress/error/cancel behavior.

## 7. Liquid Glass in a document editor

Document surfaces benefit from clear hierarchy more than decorative layering.

Good bounded uses:

- a focused AI review panel beside the document;
- a compact tool group with related editing actions;
- a transient status surface that remains readable;
- a floating but semantically labeled inspector when the target supports it.

Keep these native system surfaces intact:

- document browser and file picker;
- title and file status;
- save/export/move/share;
- undo/redo and conflicts;
- toolbar/menu/keyboard command routes;
- accessibility focus and input.

On iPadOS, glass should not collapse a workspace into a phone-like stack.
On Catalyst, use Mac window/toolbar/menu conventions. On visionOS, use the
system window material and spatial hierarchy. On watchOS, prefer concise system
controls over a document glass shell.

## 8. AI review inside a document task

AI should appear as a reviewable tool with a source boundary:

~~~text
current document
    -> select scope
    -> show model/capability state
    -> generate candidate
    -> inspect source and uncertainty
    -> apply to draft or discard
    -> revalidate document revision
    -> commit/save/export
~~~

Design the candidate with:

- source range or document revision;
- generated versus user-authored distinction;
- loading/partial/unavailable/refused/failed state;
- edit, accept, reject, retry, and undo actions;
- privacy and retention explanation where relevant;
- a stale-state warning when the document changes.

Do not let a translucent “AI” panel hide the document status or make a
generated paragraph look like saved text.

## 9. Provider and offline states

A document can be:

- local and available;
- local but read-only;
- remote and loading;
- a placeholder awaiting materialization;
- unavailable because the provider is offline;
- changed externally;
- conflicted;
- moved or deleted;
- no longer authorized.

Give each state a specific recovery route. A spinner without an explanation is
not a provider design. A cached preview is not proof that the document can be
edited or saved.

For File Provider-backed products, distinguish the app's account/session UI
from the Files app's provider surface. Test both.

## 10. Accessibility and alternate input

Document workflows are long and repetitive, so accessibility failures compound.

- Label the document and status in plain language.
- Expose open, create, save, export, move, share, undo, redo, and close.
- Announce saving, conflict, unavailable, and AI review state.
- Keep focus stable while autosaving and moving between browser/editor.
- Support Dynamic Type and long localized file names.
- Use leading/trailing semantics and test RTL.
- Provide keyboard commands on iPadOS/Catalyst and pointer support where claimed.
- Support Pencil or spatial input only when the editor task has a tested route.
- Make generated content distinguishable without relying on color or glass.

Use the actual VoiceOver, keyboard, pointer, and target input flows; an
accessibility inspector or preview is only one evidence level.

## 11. Design review checklist

- Does the user know whether this is a document editor, an import flow, or a share flow?
- Is the content type narrower than the parser's real support?
- Is the file URL treated as a current access/location value rather than universal truth?
- Is the document/window/domain identity separation explicit?
- Does autosave report results honestly?
- Are conflict, provider, offline, move, and reselect states designed?
- Can a user export or share a redacted copy without losing the source?
- Is AI output visibly a candidate until the user confirms it?
- Does the editor adapt to iPhone, iPadOS, Catalyst, visionOS, and watchOS claims?
- Does Liquid Glass group content while preserving file status and system controls?
- Can VoiceOver, Dynamic Type, RTL, keyboard, pointer, and reduced effects complete the task?
- Which physical, provider, system, signed, and release artifacts prove the claims?

## Sources

- [Documents](https://developer.apple.com/documentation/swiftui/documents)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [ReferenceFileDocument](https://developer.apple.com/documentation/swiftui/referencefiledocument)
- [Creating a document-based app](https://developer.apple.com/documentation/swiftui/creating-a-document-based-app)
- [SwiftUI presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [File management HIG](https://developer.apple.com/design/human-interface-guidelines/file-management)
- [Collaboration and sharing HIG](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Windows HIG](https://developer.apple.com/design/human-interface-guidelines/windows)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
