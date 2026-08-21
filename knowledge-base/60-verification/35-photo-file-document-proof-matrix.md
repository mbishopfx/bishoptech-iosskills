# Photos, Files, documents, provider, PDF, and sharing proof matrix

This matrix separates source selection, permission, scoped file access, document serialization, provider synchronization, preview/editing, AI review, system handoff, and release evidence. A picker appearing or a file URL existing is not proof that the complete workflow is safe, durable, or user-authorized.

## Evidence levels

| Level | Evidence | What it proves |
| --- | --- | --- |
| L0 | Official route and target review | The selected PhotosUI, PhotoKit, SwiftUI, Foundation, File Provider, Quick Look, PDFKit, or sharing boundary is understood |
| L1 | Deterministic fixture | Type validation, schema migration, malformed input, redaction, AI proposal, conflict, and cancellation behavior |
| L2 | Preview/simulator/UI fixture | Native hierarchy, Liquid Glass grouping, source/provenance review, accessibility labels, and fallback surfaces |
| L3 | Signed physical-device run | Photos/Files/provider pickers, permission settings, document lifecycle, PDF/Quick Look behavior, and system handoff on the target |
| L4 | Real account/provider/content environment | iCloud Photos, limited library, third-party provider, offline/remote revision, large media, PDF variation, and destination behavior |
| L5 | Release artifact | Target/extension membership, capabilities, usage/privacy declarations, App Group/provider configuration, supported devices, signing, and App Store metadata |

## PhotosUI selection

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| PhotosPicker selects the supported media | Physical device, filter, one/multiple selection, cancel, selection count | Picker visibility does not prove representation loading |
| Selected representation loads | Local asset, iCloud asset, unsupported encoding, cancellation, size/duration test | A PhotosPickerItem is not decoded bytes |
| AI uses only selected content | Source IDs, selected ranges/representations, model context log, reject path | Picker scope does not authorize library-wide analysis |
| Limited access is explained | Limited authorization or picker-first route, Settings change, missing asset state | “Missing” is not necessarily deleted |
| Large media is safe | Downsample/streaming/memory/cancellation and thermal run | One small photo does not prove video or RAW behavior |

## PhotoKit library access

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Authorization is least privilege | Add-only/read-write/limited/denied/restricted fresh-install runs | A prompt response does not prove later fetch/change behavior |
| Library fetch is current | Change observer, asset deletion/edit, iCloud/limited state, refetch | A PHAsset object can become stale |
| Mutation works | PHPhotoLibrary performChanges, explicit confirmation, success/error, rollback/reload | Constructing a PHAssetChangeRequest is not a committed change |
| AI album/metadata proposal is safe | Asset list/destination preview, permission recheck, user accept/reject | AI output is not PhotoKit authorization |

## Files and scoped URLs

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Import works | Files/iCloud/third-party provider, allowed UTTypes, cancel, type/size validation | A local fixture does not prove provider behavior |
| Security scope is balanced | startAccessing true/false, stop call on success/failure/cancel, relaunch | A URL string does not preserve access |
| Bookmark is durable | Store/resolve, stale bookmark, moved/deleted file, reselect | Bookmark resolution does not prove content availability |
| External change is safe | NSFileCoordinator/read/write, conflict, provider eviction, backgrounding | A direct Data read can race another process |
| Temporary copies are safe | Copy/delete, crash/interruption, sensitive cache/log review | A copied file can outlive the user’s intended retention |

## FileDocument and DocumentGroup

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Document opens | DocumentGroup/open route, all declared UTTypes, multiwindow/scene restoration | One file in app bundle does not prove Files integration |
| Document saves | FileDocument/ReferenceFileDocument serialization, autosave, cancellation, error | A successful fileWrapper call does not prove durable atomic save |
| Schema migrates | Old fixtures, current fixture, unknown version, partial/corrupt package | A version field without migration tests is not compatibility |
| Isolation is correct | Concurrency/sendability checks, no UI mutation from serialization | A main-thread happy path does not prove SwiftUI document safety |
| External edit is reconciled | Same-file changes from Files/provider/second window, reload/keep-copy policy | Last-write-wins without user policy can lose work |

## File Provider

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Items enumerate | Provider extension target, root/child enumeration, stable IDs, pagination | Local mock data is not Files integration |
| Placeholder materializes | Files request, offline/online, progress, cancellation, retry | Metadata availability is not content availability |
| Local change uploads | Create/modify/delete, completion handler, Progress, server response | Request started is not upload complete |
| Remote change reconciles | Remote notification/change signal, item version, local edit, conflict | One device cannot prove multi-side sync |
| Extension survives termination | Kill/relaunch/expiration, pending state, idempotent replay | An extension callback in a test host is not system lifecycle proof |
| Provider privacy is correct | Account change, logout, cache deletion, Files/share previews, logs | Provider presence does not authorize app-wide data exposure |

## UTType and transfer

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Custom type is recognized | Export/import declaration, conformance, extension/MIME mapping, Files/Quick Look | Extension alone does not validate file bytes |
| FileDocument/fileImporter/fileExporter agree | Same UTType fixtures, unsupported type, export/reimport | A type identifier can be declared incorrectly |
| Share projection is redacted | Sensitive fields, Transferable representations, destination matrix | Share sheet cannot undo an overly broad representation |
| File representation is accepted | Mail/Messages/Notes/AirDrop or named destinations, file and data variants | One destination does not prove all sharing services |

## Quick Look and PDFKit

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Preview works | Common types, unsupported type, custom preview extension, process restart | Supported common types can change between OS releases |
| Thumbnail works | QLThumbnailGenerator sizes/types, large files, fallback, memory | Thumbnail does not prove open/edit support |
| PDF displays | PDFDocument/PDFView page navigation, search, selection, scale, accessibility | Rendering a page does not prove secure parsing |
| PDF annotation works | Markup/link/widget/ink cases, save/reopen, page coordinates | Annotation creation is not output validation |
| PDF link policy is safe | External links, embedded actions, user confirmation, redaction | Parser/model output must not open links automatically |
| Malformed/encrypted PDF is handled | Corrupt, password, huge-page, embedded-media fixtures | A standard PDF fixture is too weak |

## AI and privacy

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| AI extracts fields | Selected source fixtures, bounding/page references, typed output, edit/reject | Extraction is a proposal, not verified truth |
| AI summarizes a document | Selected pages/ranges, context/model version, source citations, sensitive-data review | A summary may reveal more than the source surface |
| AI rewrites a document | Original revision, diff/undo, accepted/rejected result, migration | Model output must not overwrite canonical content silently |
| AI chooses an export/share route | Redacted projection, explicit confirmation, destination test | AI cannot grant access or authorize sharing |
| AI touches provider content | Materialization consent, privacy/retention, offline/error state | Metadata access does not authorize downloading bytes |

## Design and accessibility

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Native picker/document route is understandable | First-run task test, scope copy, cancel/retry | Technical API names should not be required |
| Glass review surface is legible | Light/dark, Dynamic Type, increased contrast, reduced transparency, long strings | Material does not replace hierarchy |
| Source/proposal relationship is clear | Screen-reader order, page/asset labels, edit/reject/accept | A green check is not evidence of commit |
| Core task works without precision touch | VoiceOver, Voice Control, keyboard/pointer, accessible list/inspector | Thumbnail gestures cannot be the only route |
| Privacy is maintained | Notification/widget/lock-screen/share/log/cache review | Permission and retention are separate claims |

## Release evidence packet

~~~text
feature:
target/bundle/build:
sdk/deployment target:
device/os:
route:
photo authorization/access level:
photos picker or document picker:
source identifiers/revisions:
security scope/bookmark:
uttype:
document schema/version:
file coordination:
provider target/account/network:
quick look/pdf route:
share representations/redaction:
ai model/context/version:
proposal/source citations:
user review/undo:
commit/export/share/sync result:
privacy retention/deletion:
accessibility settings:
large-file/memory/thermal:
extension/app-group/capability artifact:
known failures:
claim supported:
claim not yet supported:
~~~

## Claim language

Use:

- “The user selected the named photo through PhotosPicker; the app loaded the requested representation, showed the source-linked AI draft, and saved only after confirmation.”
- “The signed device run imported a provider-backed file under a balanced security-scoped access interval and handled reselection after the URL became unavailable.”
- “The document opened and migrated the listed schema fixtures; external edits were detected and the user chose the resulting revision.”
- “The provider extension enumerated the declared items and materialized a file on the named device; upload completion and conflict reconciliation were tested separately.”
- “The PDF annotation was saved and reopened with the expected page-space bounds; external link activation remained user-confirmed.”

Avoid:

- “The app has access to the user’s photos” when only selected items were provided.
- “The file is permanently available” because a URL callback succeeded.
- “Synced” because a provider request was queued.
- “The document is safe” because PDFKit rendered it.
- “The AI verified the form” without human review and source evidence.

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [PHPhotoLibrary](https://developer.apple.com/documentation/photos/phphotolibrary)
- [Delivering an Enhanced Privacy Experience in Your Photos App](https://developer.apple.com/documentation/photokit/delivering-an-enhanced-privacy-experience-in-your-photos-app)
- [Requesting Changes to the Photo Library](https://developer.apple.com/documentation/photokit/requesting-changes-to-the-photo-library)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [ReferenceFileDocument](https://developer.apple.com/documentation/swiftui/referencefiledocument)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [File importer and exporter presentation](https://developer.apple.com/documentation/swiftui/view-presentation)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [Defining file and data types for your app](https://developer.apple.com/documentation/uniformtypeidentifiers/defining-file-and-data-types-for-your-app)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [startAccessingSecurityScopedResource](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [NSFileProviderReplicatedExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderreplicatedextension)
- [Replicated File Provider extension](https://developer.apple.com/documentation/fileprovider/replicated-file-provider-extension)
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
