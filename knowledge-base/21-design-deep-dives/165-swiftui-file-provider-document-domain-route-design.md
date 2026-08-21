# SwiftUI File Provider route design: a native Files-like document surface

The design goal for a File Provider feature is not to imitate every pixel of
Files. It is to make the provider’s state legible inside an Apple-native
document workflow: hierarchy is obvious, system actions stay recognizable,
material and download status are honest, and a person can recover from a
network or authorization problem without losing a draft.

The design contract is:

~~~text
domain/account context
  -> folder or working-set hierarchy
  -> item metadata and availability
  -> action affordance
  -> coordinated document handoff
  -> optional proposal review
  -> explicit commit
~~~

## Start with a route decision

Before designing a glass browser, answer:

| Question | If yes | If no |
| --- | --- | --- |
| Must another app see these items in Files? | Design a File Provider target and domain lifecycle | Keep the data app-owned |
| Is the source remote or multi-device? | Use replicated or nonreplicated provider sync | Prefer FileDocument or app-owned storage |
| Does the person select one external file only? | Use fileImporter or a document picker | Do not add a provider for one import |
| Does the app need continuous editing of a shared file? | Use coordinated access and a document presenter | Use an app-owned copy with explicit export |
| Is AI proposing a filename or folder? | Add a review state tied to item revision | Keep the deterministic action path |

This prevents a visual “Files clone” from acquiring an unnecessary extension,
entitlement, remote-sync, or privacy surface.

## Screen anatomy

Use a system-recognizable hierarchy:

~~~text
navigation title: domain display name
  toolbar: search, sort, account/status, add/import
  path context: current folder and parent navigation
  content: List or adaptive grid of provider items
  row/card: icon, filename, type/size, availability, sync/conflict state
  inspector: selected item, download/open/share/rename/move actions
  transient feedback: progress, retry, offline, conflict
~~~

The hierarchy should remain useful with no custom decoration. Keep the current
domain and folder visible even when the person is offline. If multiple domains
represent accounts or workspaces, show that context as a selection control
with a clear accessibility label, not as an unlabeled avatar or decorative
glass capsule.

Use a List for browse-heavy and action-heavy documents. Use a grid only when
thumbnail recognition materially improves selection. Keep the same item
identity and action state in either layout so a rotation, Dynamic Type change,
or iPad size change does not change the provider’s semantics.

## Native Liquid Glass discipline

The provider’s primary surfaces should be current SwiftUI controls, toolbar
items, navigation, sheets, menus, labels, and progress indicators. These
controls receive system styling and adapt to the current platform appearance.

Use custom Glass for one semantic group at a time:

- a compact download or retry control cluster;
- a selected-item inspector;
- a transient AI proposal review panel;
- a floating filter/status control that does not obscure the hierarchy.

Apply the same rules as any other Liquid Glass design:

1. Keep content behind glass sparse enough to preserve legibility.
2. Put related glass elements in a GlassEffectContainer when they morph or
   need a shared visual context.
3. Avoid nesting multiple opaque materials around every row.
4. Keep hit targets and labels independent of the glass effect.
5. Provide a non-material state for reduced-transparency and high-contrast
   settings.
6. Test with long filenames, large text, VoiceOver, color filters, and a
   busy thumbnail background.

Do not style a provider error as a decorative cloud badge. “Download
required,” “upload pending,” “offline,” and “conflict” must be available as
text or an accessibility value.

## State-to-visual mapping

| Provider state | Visible treatment | Action |
| --- | --- | --- |
| Enumerating | Stable skeleton rows or progress in the list region | Cancel/retry if the operation is user-cancellable |
| Dataless | File icon plus “Download” or equivalent semantic action | Request materialization |
| Downloading | ProgressView with a meaningful label | Cancel if supported, then retry |
| Materialized | Normal open/edit affordance | Open with coordinated access |
| Uploading | Pending badge and progress where available | Keep the item usable; do not promise remote durability |
| Offline | Offline label with local content state | Open materialized content, queue safe work, retry |
| Not authenticated | Account-repair message | Return to host-app authentication |
| Conflict | High-attention but non-destructive state | Preserve local draft and choose a resolution |
| Permission denied | Explain access boundary | Settings or alternate local workflow |
| Empty | Explain why it is empty | Distinguish no data from no access or not-yet-loaded |

The empty state is part of provider correctness. A blank view can mean no
items, an expired cursor, no current domain, user-disabled domain, offline
cache, or an authorization failure. Do not collapse these into “No files.”

## Browse, search, and selection

Search should operate on the provider’s indexed metadata and clearly state
whether results are local, remote, or stale. If Spotlight or the working set
is the source, do not imply that every remote item is searchable offline.

Keep selection state separate from item truth:

~~~text
selectedItemID
  -> resolve current provider item
  -> check capabilities and revision
  -> show action
  -> coordinate or request download
  -> update selection after the provider confirms a change
~~~

Never use an array index as selection identity. When a page refreshes or an
item is moved, preserve selection by stable item identifier. If an item
disappears, announce that it was removed or moved and provide a path back to
the parent.

For destructive actions, use the system confirmation pattern and explain
whether the action means move to Recently Deleted, permanently delete, remove
local download, or disconnect the domain. “Delete” and “Remove Download” are
not interchangeable.

## Inspector and review panel

An inspector is a useful place for the provider-specific controls because it
can show details without altering list semantics:

- filename and content type;
- current folder/domain;
- local availability and remote sync state;
- last modified and size when known;
- capabilities supported by this item;
- open, download, share, rename, move, trash, or evict actions;
- conflict and error recovery.

If the inspector contains an AI proposal, separate it visually and
semantically:

~~~text
current provider metadata
  -> proposed change
  -> source revision
  -> reason or selected source
  -> accept / edit / reject
  -> deterministic provider validation
  -> commit
~~~

The proposal must not look like a system-confirmed filename or folder. Use
“Suggested” language, show the source scope, and disable commit when the
current item revision no longer matches the proposal.

## Document handoff

An Open action should tell the person what will happen:

- local materialized content opens immediately;
- dataless content downloads first;
- an external document is opened in place;
- an export creates a copy or moves the original, depending on the chosen
  document-picker mode.

Keep security-scoped access and file coordination in the model/service layer.
The view should receive a domain value such as openInProgress,
needsDownload, externalAccessDenied, or conflict. Do not let a row retain a
security-scoped URL indefinitely just because it is selected.

When another app edits a document, show the provider’s remote/local state
after the document presenter or enumerator reports it. Avoid polling the file
URL from a SwiftUI timer.

## Accessibility and alternate input

The item row is a semantic control, not a decorative card. Provide:

- a stable label containing the filename and useful type;
- a value such as “Available offline,” “Download required,” or “Upload
  pending”;
- actions for Open, Download, Rename, Move, Share, and Remove Download that
  match actual capabilities;
- a visible focus state that remains legible through glass;
- a layout that survives Dynamic Type without truncating the only filename;
- keyboard, pointer, Voice Control, Switch Control, and external controller
  routes where the platform supports them.

Do not convey the provider state through cloud icon color alone. Use text,
labels, and announcements for state changes. When a page appends items, do
not repeatedly announce the entire list. When a file is materialized or
evicted, announce the changed state without stealing focus from an active
document editor.

Reduced Motion should avoid morphing glass transitions that imply a different
item. Reduced Transparency and increased contrast should preserve row
boundaries, focus, separators, and status text. Test a full task:

~~~text
open domain -> enter folder -> locate file -> download -> open -> return
-> rename or move -> recover from an error
~~~

## iPad, Mac Catalyst, and adaptive layout

Treat the provider hierarchy as an adaptable navigation model:

- compact width: one navigation stack with a sheet or inspector;
- regular width: sidebar/domain list, folder list, and optional inspector;
- pointer/keyboard: visible hover/focus and command routes;
- large text: switch from dense metadata columns to stacked rows;
- Mac Catalyst: verify file coordination, menu commands, and URL behavior
  independently from iOS.

Do not assume that a design that resembles the iOS Files app is correct on
iPad or Mac Catalyst. The provider target’s framework availability and
document-browser behavior must be checked for the actual destination.

## AI proposal presentation

For local on-device AI:

1. Show exactly which selected text, document, or metadata is being analyzed.
2. State that the result is a suggestion.
3. Keep the original filename/folder visible.
4. Show model unavailable, refusal, timeout, and stale-source states.
5. Validate the proposed item ID, filename, Uniform Type Identifier, and
   capability against current provider metadata.
6. Require the person to accept or edit before a File Provider mutation.
7. Do not retain more document text than the feature needs.

An AI suggestion should not get the same styling as a completed upload or
system-authenticated account. Use a small review surface with a clear
deterministic action.

## Design review checklist

Before implementation, confirm:

- the route actually needs File Provider;
- domain/account context is visible;
- stable item IDs drive selection and navigation;
- page, anchor, and reset states have user-facing recovery;
- dataless/materialized/evicted content is distinguishable;
- local changes are not described as uploaded before confirmation;
- custom glass is limited to semantic groups;
- reduced-transparency and high-contrast variants remain usable;
- VoiceOver and Dynamic Type can complete browse/download/open/return;
- AI output is typed, revision-bound, and explicitly reviewed;
- external URL access and coordination are owned outside the view;
- physical-device and signed-provider proof are planned.

## Sources

- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [Replicated File Provider extension](https://developer.apple.com/documentation/fileprovider/replicated-file-provider-extension)
- [NSFileProviderDomain](https://developer.apple.com/documentation/fileprovider/nsfileproviderdomain)
- [NSFileProviderManager](https://developer.apple.com/documentation/fileprovider/nsfileprovidermanager)
- [NSFileProviderEnumerator](https://developer.apple.com/documentation/fileprovider/nsfileproviderenumerator)
- [Synchronizing the File Provider extension](https://developer.apple.com/documentation/fileprovider/synchronizing-the-file-provider-extension)
- [Tracking changes to documents](https://developer.apple.com/documentation/fileprovider/tracking-changes-to-documents)
- [UIDocumentPickerViewController](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller)
- [Providing access to directories](https://developer.apple.com/documentation/uikit/providing-access-to-directories)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftUI File Provider route](../42-framework-deep-dives/137-swiftui-file-provider-document-domain-route.md)
- [SwiftUI File Provider capability route](../50-capability-recipes/168-swiftui-file-provider-document-domain-route.md)
- [SwiftUI File Provider proof matrix](../60-verification/162-swiftui-file-provider-document-domain-proof-matrix.md)
