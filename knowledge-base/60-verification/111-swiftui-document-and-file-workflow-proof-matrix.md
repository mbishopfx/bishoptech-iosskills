# SwiftUI document and file-workflow proof matrix

## Purpose

Use this matrix for any claim involving DocumentGroup, FileDocument,
ReferenceFileDocument, import/export/move/share, security-scoped URLs, File
Provider, autosave, file versions, document/window identity, Liquid Glass
editors, or on-device AI document review.

A document claim must name the file kind, format, target, persistence boundary,
and evidence level. Record:

- app version, build, Xcode, SDK, deployment target, and configuration;
- target and extension membership;
- document ID, domain ID, scene/window identity, file URL state, and source
  revision;
- UTType, format version, migration result, and byte/attachment fixture;
- provider/account/authentication/offline/materialization state;
- dirty, saving, saved, conflict, cancelled, and failed states;
- import/export/move/share source, destination, cancellation, and result;
- AI capability/model/session state, selected source, candidate revision,
  cancellation, review, and commit;
- locale, layout direction, Dynamic Type, color scheme, contrast, transparency,
  motion, input, and accessibility settings;
- artifact path, test date, target/device identity, and tester.

Never turn a preview or a successful local parse into proof of system file
behavior or release readiness.

## Evidence levels

| Level | Can support | Cannot support alone |
| --- | --- | --- |
| Official source | API intent, file-management guidance, platform boundary | This app's implementation |
| Static route review | Identity, format, ownership, and lifecycle design | Runtime picker/provider/system behavior |
| Named-target compile | API availability, imports, scene declarations, target membership | File bytes, real provider state, physical input |
| Unit/fixture test | Format decoding, migration, routing, state transitions, stale policy | System document browser, real permissions, provider delivery |
| Preview | Editor hierarchy and named visual fixtures | File coordination, autosave, system surfaces, model readiness |
| UI test | In-app editor, commands, labels, deterministic review actions | Files provider, external picker, all real window states |
| Simulator | Many layout, lifecycle, and target behaviors | Physical keyboard/Pencil, provider account, model readiness, release |
| Signed physical target | iPhone/iPadOS/Catalyst/visionOS/watchOS interaction and device capability | App Store distribution or every provider/system combination |
| System-surface run | Files picker, share sheet, external URL, provider, Shortcuts, Handoff | All targets, production population, archive metadata |
| Performance run | Hitches, memory, file size, model/task timing on a target | Correctness of every format/provider case |
| Archive/release artifact | Processed Info.plist, target membership, entitlements, signing | Successful user task, physical ergonomics, system delivery |
| TestFlight/release smoke | Intended signed build and selected user workflow | Universal correctness or untested devices/providers |

## Fixture contract

Use one explicit fixture type for deterministic document tests.

~~~swift
struct DocumentProofFixture: Hashable, Sendable {
    let target: String
    let documentID: String
    let domainID: String?
    let sceneID: String?
    let windowID: String?
    let fileURLState: String
    let providerState: String
    let contentType: String
    let formatVersion: Int
    let sourceRevision: Int
    let documentSaveState: String
    let importExportAction: String?
    let aiState: String
    let localeIdentifier: String
    let layoutDirection: String
    let dynamicType: String
    let accessibilityModes: [String]
}
~~~

Fixtures should cover at least:

- new empty document;
- valid current-format document;
- valid older-format document;
- malformed/truncated/oversized document;
- unsupported content type;
- missing, deleted, unauthorized, and stale source;
- external URL with and without security-scoped access;
- local, provider-downloading, offline, evicted, and conflict states;
- clean, dirty, saving, saved, cancelled, failed, and recovery states;
- AI unavailable, ready, reviewing, partial, candidate, stale, failed, and
  committed states.

## Format and UTType matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Custom UTType is declared | Named-target compile and bundle/config inspection | Incorrect identifier, missing conformance, extension collision | Intended target recognizes the identifier and conformance |
| Document readable/writable types agree | Compile plus static comparison | Import-only/export-only, unsupported target | FileDocument/ReferenceFileDocument and picker/exporter agree |
| Current format decodes | Unit test with canonical fixture | Empty fields, unknown optional field, max-size field | Model equals expected value and reports revision |
| Current format writes | Unit test and byte/structure inspection | Determinism, attachments, Unicode, large content | Output reopens and preserves intended data |
| Older format migrates | Migration fixture test | Multiple versions, partial migration, rollback | Explicit version result and no silent data loss |
| Unsupported version fails safely | Unit test/UI fixture | Future version, unknown type, malicious bytes | Recovery UI does not overwrite the source |
| Malformed content fails safely | Corrupt/truncated/oversized fixtures | Empty file, invalid encoding, invalid archive | Error maps to a user action and leaves source intact |
| Exported type is honest | Exporter/system run | Filename/type mismatch, cancelled destination | Destination opens only where the declared type is supported |
| Attachments have a defined policy | Unit and size test | Missing, duplicate, external, oversized attachment | Document either embeds, references, or rejects explicitly |

## Document scene and model matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| DocumentGroup is the correct scene | Static route review plus named-target compile | Temporary import mistaken for document, unsupported platform | Scene meaning and fallback are documented |
| New document opens | Compile plus UI/system run | Empty defaults, cancellation, duplicate window | New document has stable identity and editable content |
| Existing document opens | Fixture plus Files/document browser run | Deleted, unauthorized, provider unavailable | Correct document opens or gives recovery UI |
| FileDocument reads/writes | Unit tests plus editor UI run | Parse/write error, cancellation, large file | Editor content and file bytes agree |
| ReferenceFileDocument signals change | Unit/change-state test plus edit UI run | Mutation from background, undo/redo, replacement | Dirty state follows reference mutation without lost updates |
| Document binding is scoped correctly | Static review plus edit/close/reopen UI run | Binding replacement, scene recreation | Editor does not retain an invalid binding |
| fileURL is treated as context | Static review and unavailable-URL fixture | Temporary URL, inaccessible URL, rename/move | Domain and access logic do not depend on a string path alone |
| Scene/window identity is separate | Two-window run or target fixture | Same file in two scenes, separate drafts | Window-local state is isolated and document truth is explicit |
| Document title/status is useful | UI test and accessibility run | Long filename, unsaved state, conflict | User can identify file and save/conflict state |
| Unsupported target fallback works | Availability compile plus target UI run | iPhone/Catalyst/visionOS differences | User sees a supported alternative, not a broken browser |

## Import and security-scoped URL matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Importer presents allowed types | Named-target compile plus UI/system run | Disallowed type, multiple selection, cancellation | Picker filters and route accepts only intended types |
| Selected URL is validated | Unit parser plus picker run | Directory, symlink, missing URL, wrong type | Invalid selection is rejected without opening the editor |
| Security scope is started | Static review plus external file run | Scope cannot start, repeated access, error path | Operation reads/writes only while scope is active |
| Security scope is stopped | Static review plus repeated import/instrumented run | Throw, cancellation, early return | No scope leak is left after the operation |
| Temporary import becomes owned | UI run plus relaunch/reopen test | Source disappears, provider offline, user cancels | Product policy is explicit: copy, reference, or reject |
| Bookmark is justified | Static review plus relaunch test | Stale bookmark, revoked access, sign-out | Bookmark is resolved, refreshed, and revalidated |
| Import does not mutate source | Source hash/metadata test | Read-only source, provider source, duplicate import | Source remains unchanged unless user chose a move/write action |
| Large import is bounded | Performance/size test | Memory pressure, cancellation, partial read | Memory, cancellation, and cleanup behavior are recorded |

## Export, move, and share matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Export creates a new representation | Unit byte test plus destination UI run | Same destination, overwrite, cancellation | Source identity and destination identity remain distinct |
| Exporter uses correct UTType | Compile plus system run | Wrong extension, unavailable type | Receiving surface recognizes the exported representation |
| Default filename is useful | UI/accessibility run | Localization, duplicate names, long names | User can understand and edit the name |
| Move changes ownership/location | System file run plus reopen | Same provider, cross-provider, cancellation | Source is not duplicated or silently destroyed |
| Move failure is recoverable | Provider/system failure fixture | Offline, permission denial, conflict | Source remains available and status explains next action |
| Share uses correct representation | Transferable/share run | Large file, unsupported receiver, cancellation | Recipient gets intended data and no secret metadata |
| Temporary share files are cleaned | Repeated share/termination test | Receiver never reads, app killed | Cleanup/retry policy is explicit |
| Export/share do not imply save | UI review plus state fixture | Dirty source, conflict, pending save | Labels and status match persistence semantics |

## File coordination and provider matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Provider item identity is stable | Extension/unit test | Rename, move, delete, parent change | Same item remains traceable across metadata updates |
| Placeholder is honest | Provider/system run | Offline, not-downloaded, permission denied | Open/download action and status are clear |
| Materialization is cancellable | Extension integration test | Repeated request, termination, partial download | No corrupt partial file is presented as complete |
| Upload is coordinated | Provider integration test | Concurrent editor, network loss, retry | Server and local state converge or conflict is surfaced |
| Local edits remain safe | Editor/provider run | Background sync, rename while editing | Autosave does not overwrite unrelated remote bytes |
| File coordination is bounded | Unit/integration/instrumented run | Nested access, presenter removal, cancellation | Coordinated read/write completes without leaked presenter/scope |
| Versions/conflicts are visible | Version fixture/system run | Multiple writers, remote newer, local newer | Keep/duplicate/merge/retry choices are explicit |
| Account isolation holds | Provider authorization/security test | Sign-out, account switch, revoked token | No prior-account content remains accessible |
| Extension target is packaged | Archive inspection plus provider run | Missing entitlements, wrong extension target | Intended extension and identifiers are in the signed artifact |

## Autosave, recovery, and lifecycle matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Edit marks document dirty | Unit/state test plus UI edit | Undo to clean, rapid typing, external update | Status changes predictably |
| Autosave runs at intended boundary | UI/integration test | Background, scene close, app termination, provider offline | Save policy is recorded, not inferred |
| Save cancellation is safe | Cancellation test | New edit while saving, task replacement | No older write wins after a newer edit |
| Write failure is recoverable | Failure fixture plus UI run | Disk full, permission, provider error, serialization | Content remains available and retry/export action exists |
| Termination does not lose confirmed work | Physical relaunch/test build | Kill during edit/save/AI review | Recovery evidence names the confirmed boundary |
| Restore is validated | Relaunch/scene-restoration run | File moved, deleted, account changed | Invalid state becomes recovery UI |
| Conflict does not overwrite | Multi-writer/provider test | Remote update during local edit | User chooses a resolution and evidence records it |
| “Saved” is scoped | UI review plus state fixture | Local save vs upload vs remote commit | Wording identifies the actual boundary |

## On-device AI document review matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Capability is optional | Device/configuration check plus unavailable fixture | Unsupported device, disabled model, policy change | Editor remains useful with an honest unavailable state |
| Source scope is bounded | Static adapter review plus request fixture | Whole file, selection, attachment, sensitive field | Only intended content crosses the model boundary |
| Source revision is captured | Request/response unit test | Edit during review, undo, external update | Candidate records exact source revision |
| Cancellation is honored | Async test plus UI cancellation | Scene close, new selection, task replacement | No late callback mutates the new document |
| Partial output is provisional | UI fixture/accessibility run | Truncation, failure, user navigates away | Partial text is not presented as committed content |
| Candidate requires review | UI test with explicit apply/discard | No-op, dangerous change, empty result | User sees source, proposed change, and actions |
| Stale candidate is blocked | Revision conflict test | Concurrent edit, save during review | Apply is blocked, rebased, or explicitly confirmed |
| Commit uses document path | Integration test | Serialization failure, provider failure | AI edit follows normal dirty/save/conflict semantics |
| Privacy copy is accurate | Static content review and UI run | Offline/on-device claim, telemetry, logging | Copy states what is and is not sent/stored |
| Model work is bounded | Performance/thermal run | Long document, rapid repeated requests | Limits, cancellation, memory, and thermal evidence exist |

## Liquid Glass and editor hierarchy matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Glass group has semantic purpose | Design review plus preview | Decorative full-page treatment, dense text | Controls remain understandable without material |
| Document content remains primary | Visual run | Long text, selection, images, attachments | Material does not obscure or reduce editing clarity |
| Glass adapts to background | Light/dark visual run | Busy document, image content, scroll | Contrast and separation remain useful |
| Accessibility fallback works | Reduced transparency/contrast/motion run | Accessibility sizes, VoiceOver | Meaning survives without relying on blur or translucency |
| Status is semantic | UI/accessibility fixtures | saving, conflict, stale, unavailable, committed | Text/labels expose state and actions |
| Floating group placement works | iPhone/iPad/Catalyst visual run | narrow width, keyboard, Stage Manager | Group does not cover primary editing or system controls |
| No fake system chrome is claimed | Static/design review | Custom title bar, fake window buttons | App distinguishes custom controls from system window behavior |

## Accessibility and input matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Document browser is navigable | VoiceOver UI task | new/open/import/cancel | User can identify types, files, and actions |
| Editor fields are labeled | VoiceOver task | selection, formatting, attachments, AI review | Labels, values, hints, and traits make state clear |
| Save/conflict state is announced | Accessibility fixture/device run | saving, failed, conflict, offline | User hears status and available recovery action |
| Dynamic Type works | Preview matrix plus target UI run | accessibility sizes, long filenames | No clipped editor action or hidden recovery |
| RTL/localization works | Localized UI run | filenames, dates, toolbar, document text | Meaning and order remain correct |
| Keyboard commands work | iPad keyboard/Catalyst run | focus, selection, undo, save, dismiss | Core document task is completable without touch |
| Pointer works | iPad/Catalyst run | hover, right click, scroll, resize | Pointer interactions are discoverable and optional |
| Pencil/input alternatives work | iPad run where supported | text fallback, handwriting setting | Feature does not require an untested input |
| Reduce effects remains usable | Device settings run | reduced transparency/motion, contrast | Hierarchy and state remain legible |
| Focus is bounded | UI/accessibility run | import completion, AI result, conflict | Focus moves to useful content without disorientation |

## Target and release matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| iPhone document route works | Physical iPhone run | compact browser/editor, share, interruption | Create/open/edit/save/restore task completes |
| iPadOS document route works | Signed iPad run | split view, Stage Manager, resize, keyboard | Browser/editor and file actions remain usable |
| Mac Catalyst works | Actual Catalyst compile/run | menu, pointer, keyboard, multiple windows | File task completes as a Mac app |
| visionOS route is supported | visionOS target run | window sizing, focus, dismissal, unavailable fallback | Spatial claim is limited to tested route |
| watchOS projection is honest | watch target run | small surface, crown, offline/paired state | Watch task links back rather than pretending full editing |
| File Provider is packaged | Archive and system provider run | extension process, account, placeholder, sync | Signed product exposes intended provider behavior |
| Performance is acceptable | Metric/performance run | large document, repeated autosave, AI review | Hitches/memory/thermal evidence names target |
| Release build preserves routes | Archive plus TestFlight smoke | processed types, scenes, entitlements, extensions | Signed build identity and real task evidence are recorded |

## Sources

- [Documents](https://developer.apple.com/documentation/swiftui/documents)
- [DocumentGroup](https://developer.apple.com/documentation/swiftui/documentgroup)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [ReferenceFileDocument](https://developer.apple.com/documentation/swiftui/referencefiledocument)
- [Creating a document-based app](https://developer.apple.com/documentation/swiftui/creating-a-document-based-app)
- [Handling advanced document scenarios](https://developer.apple.com/documentation/swiftui/handling-advanced-document-scenarios)
- [SwiftUI view presentation](https://developer.apple.com/documentation/swiftui/view-presentation)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [URL security-scoped resource access](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [NSFilePresenter](https://developer.apple.com/documentation/foundation/nsfilepresenter)
- [NSFileVersion](https://developer.apple.com/documentation/foundation/nsfileversion)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [Replicated File Provider extension](https://developer.apple.com/documentation/fileprovider/replicated-file-provider-extension)
- [Synchronizing the File Provider extension](https://developer.apple.com/documentation/FileProvider/synchronizing-the-file-provider-extension)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [File management HIG](https://developer.apple.com/design/human-interface-guidelines/file-management)
- [Collaboration and sharing HIG](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Windows HIG](https://developer.apple.com/design/human-interface-guidelines/windows)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
