# WebKit, Sharing, and PDF Deep Dive

## Scope and trust boundaries

WebKit, the system share surface, and PDFKit each handle content that may come from outside the app’s trust boundary. Keep the route explicit:

`source policy -> typed representation -> constrained renderer/hand-off -> validated native action -> user-visible result`

A webpage is not an app command, a share destination is not a trusted recipient, and a PDF is not a safe domain model merely because a framework can render it.

## WebKit architecture

`WKWebView` is a browser surface. Before embedding it, decide whether the product actually needs an embedded web view or should hand off authentication/navigation to a system browser or authentication session. Record these decisions:

| Decision | Safer default | Why it matters |
| --- | --- | --- |
| Allowed navigation | Explicit host/scheme policy in `WKNavigationDelegate` | Redirects and links can leave the intended trust boundary. |
| Cookies/session | Deliberate `WKWebsiteDataStore` choice | Persistent state changes privacy, logout, test isolation, and account switching. |
| JavaScript | Only when the feature needs it | Script increases the interaction surface and should not be treated as native authorization. |
| Native bridge | Named messages in an app-owned `WKContentWorld` | Message names and payloads can be validated separately from page JavaScript. |
| Remote content | TLS/host/content policy and failure state | A successful load does not prove origin identity or content safety. |
| Download/export | `WKDownloadDelegate` or an explicit handoff | A download is untrusted data that needs size/type/destination rules. |
| Offline | App-owned cache or a clear unavailable state | A web view’s current page is not a durable app record. |

Use `WKNavigationDelegate` to make navigation decisions, handle authentication challenges according to the product’s security policy, and publish loading/error state. Treat redirects, downloads, process termination, and content-process crashes as normal lifecycle events. Do not leave a stale “signed in” or “completed” state after the web process has been replaced.

## JavaScript bridge discipline

If a page must communicate with native code, register a narrow `WKScriptMessageHandler` name and validate every message:

1. Confirm the message arrived from the expected frame/web view and content world.
2. Parse a small, versioned payload; reject unknown fields or commands where appropriate.
3. Validate origin/host and the current navigation state.
4. Check user intent and app authorization before side effects.
5. Perform the native action through a typed domain command, not by executing arbitrary strings.
6. Return a bounded result or error; do not expose secrets, tokens, or internal diagnostics to the page.
7. Remove the handler when the web view is torn down or the session changes.

`WKContentWorld` separates JavaScript namespaces, but it does not make the webpage trustworthy and does not apply to the page’s DOM. Keep a clear distinction between app-injected scripts and page scripts. If the bridge is only for analytics or display, avoid exposing a write-capable command at all.

For user-generated or third-party pages, do not inject privileged scripts into the page world. Prefer a content-world-specific bridge and a host allowlist, and treat the webpage’s claimed account, order, or permission state as unverified until the server or app-owned source confirms it.

## Sharing and `Transferable`

`ShareLink` and `Transferable` are the SwiftUI-first route for typed share representations. UIKit’s `UIActivityViewController` remains useful when the app needs explicit presentation control or an older integration seam. Both routes create a system handoff; neither decides what data is safe to send.

Build the share item from a confirmed snapshot:

`domain record -> redacted export snapshot -> typed representation/file -> share presentation`

Do not hand a live reference to a mutable database row to a share provider and then assume the bytes represent the screen the user confirmed. Define:

- the exported content type and filename;
- a display title/subject and preview metadata;
- whether the action is a copy, export, deep link, or collaboration invitation;
- redaction of private fields, location, author, EXIF, embedded thumbnails, and internal IDs;
- streaming/temp-file behavior for large items;
- cancellation and cleanup when the user dismisses the sheet;
- no-destination and destination-failure state.

Use `NSItemProvider` when a representation should be loaded lazily or offered in more than one type. Prefer file-backed or streamed representations over forcing a large asset into memory. A provider callback may execute on a system-controlled schedule and must not depend on a view disappearing or a main-actor-only object remaining alive.

On iPad, present UIKit’s activity controller with the correct popover anchor. On all platforms, verify the real destination list rather than assuming that Mail, Messages, Files, or a third-party app is installed.

## PDFKit route

Use `PDFDocument` for the document model and `PDFView` for viewing/navigation/selection/annotation. Keep PDF rendering separate from the app’s domain model. An imported PDF can be malformed, encrypted, huge, or intentionally adversarial; validate size and open failure before reading page content or running OCR/AI enrichment.

For generated PDFs, define a deterministic export contract:

| Concern | Decision |
| --- | --- |
| Layout | Page size, margins, page breaks, font fallback, and truncation behavior. |
| Accessibility | Reading order, selectable text, meaningful metadata, and a non-PDF alternative where needed. |
| Privacy | Document title/author, embedded images, location metadata, and export destination. |
| Versioning | Export schema and compatibility with earlier app versions. |
| Security | Password/encryption support, key handling, and no claim that rendering proves file safety. |
| Performance | Page count, thumbnail generation, memory release, and cancellation for batch export. |

If the PDF view is wrapped in SwiftUI, keep the `PDFDocument` ownership explicit and release/reload it when the selected document changes. Do not recreate a large document on every SwiftUI state update. Provide zoom, page navigation, selection, annotation, and error states that match the actual product need; a screenshot or preview is not proof of text extraction, annotation persistence, or accessibility.

## Web-to-PDF and export pipeline

WebKit can create PDF data from a view, but it is a snapshot/export operation, not a guarantee that all web content, fonts, animations, cross-origin resources, or accessibility semantics will be preserved. Treat the result as a new generated artifact with its own validation and privacy policy. If the product’s canonical document is app-owned, generate from the domain model rather than scraping the rendered web view.

## API and trust-route matrix

| Outcome | API seam | Domain boundary | Target/configuration/proof gate |
| --- | --- | --- | --- |
| Show a web page | `WKWebView` + `WKNavigationDelegate` | URL/host policy, loading state, authenticated result only after app/server validation | App target, ATS/TLS/host policy, cookies/data store, redirects, process termination, and physical web content. |
| Run app-owned JavaScript | `WKUserContentController`, `WKUserScript`, `WKScriptMessageHandler`, `WKContentWorld` | Versioned typed message/request/result | Message origin/frame/content-world validation, no secret exposure, handler teardown, navigation/process restart, and hostile payload test. |
| Download content | `WKDownloadDelegate` or an explicit URLSession/file route | Temporary file, UTType/size/hash, user-approved destination | Authentication/redirect policy, cancellation, storage, redaction, provider/share handoff, and cleanup. |
| Share/export a record | `Transferable`/`ShareLink`, `NSItemProvider`, `UIActivityViewController` | Immutable redacted snapshot and typed representation | Destination/cancellation, iPad anchor, metadata, large-file memory, and physical system share UI. |
| View a PDF | `PDFDocument`/`PDFView` | Source reference, page/annotation state, reviewable extraction | Malformed/encrypted/large input, memory, text/annotation accessibility, and provider/file lifetime. |
| Generate a PDF | App-owned layout/export or WebKit snapshot | Versioned artifact, page/layout/metadata/redaction policy | Fonts/resources, page breaks, cancellation, output validation, accessibility, and export destination. |

## Process, privacy, and lifecycle register

| Boundary | Record |
| --- | --- |
| Web process | `WKWebView` content-process termination/reload, data-store/session identity, cookie logout, and current navigation policy. |
| Native bridge | Allowed message names, content world, expected frame/origin, payload schema, authorization, and side-effect confirmation. |
| Share/provider process | Immutable snapshot, representation type, temp-file lifetime, destination/cancel/error, and cleanup. |
| PDF/document process | Source scope, page/resource limits, password/encryption policy, render/extract state, and migration/export version. |
| SwiftUI target | View state only; no canonical record mutation from a web callback, share provider, or PDF render callback. |

Use this state model for a web/share/PDF feature:

`idle -> preparing -> loading/importing -> ready -> reviewing -> exporting/sharing -> completed|cancelled|failed`

with independent `webProcessTerminated`, `providerOffline`, `scopeRevoked`, `bridgeRejected`, `documentCorrupt`, `passwordRequired`, `memoryPressure`, and `destinationUnavailable` branches. A successfully rendered page is not proof that a link was safe, a JavaScript command was authorized, a PDF is accessible, or a shared recipient received the artifact.

## Verification matrix

- WebKit: allowed and disallowed hosts, HTTP redirects, authentication, logout, cookies, offline, process termination, script failure, hostile links, downloads, keyboard/pointer, VoiceOver, and Dynamic Type around the container.
- JavaScript bridge: wrong origin, wrong frame, malformed payload, replayed command, missing user intent, handler removal, page navigation, and content-process restart.
- Sharing: text/URL/image/file/PDF, large representations, no destination, cancellation, sensitive metadata redaction, temporary-file cleanup, and iPad popover.
- PDF: malformed/encrypted/password-protected input, huge page count, corrupt page, text selection, annotations, zoom, export, memory pressure, and VoiceOver reading order.
- Device/release: physical-device system share UI, real web credentials only in a safe test account, signed entitlements/capabilities if required, and no claim that a simulator preview proves third-party content behavior.

## Sources

- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [WKNavigationDelegate](https://developer.apple.com/documentation/webkit/wknavigationdelegate)
- [WKWebsiteDataStore](https://developer.apple.com/documentation/webkit/wkwebsitedatastore)
- [WKUserContentController](https://developer.apple.com/documentation/webkit/wkusercontentcontroller)
- [WKScriptMessageHandler](https://developer.apple.com/documentation/webkit/wkscriptmessagehandler)
- [WKContentWorld](https://developer.apple.com/documentation/webkit/wkcontentworld)
- [WKScriptMessage](https://developer.apple.com/documentation/webkit/wkscriptmessage)
- [WKDownloadDelegate](https://developer.apple.com/documentation/webkit/wkdownloaddelegate)
- [WKNavigationAction](https://developer.apple.com/documentation/webkit/wknavigationaction)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [UIActivityViewController](https://developer.apple.com/documentation/uikit/uiactivityviewcontroller)
- [UIActivityItemSource](https://developer.apple.com/documentation/uikit/uiactivityitemsource)
- [NSItemProvider](https://developer.apple.com/documentation/foundation/nsitemprovider)
- [PDFKit](https://developer.apple.com/documentation/pdfkit)
- [PDFDocument](https://developer.apple.com/documentation/pdfkit/pdfdocument)
- [PDFView](https://developer.apple.com/documentation/pdfkit/pdfview)
- [PDFPage](https://developer.apple.com/documentation/pdfkit/pdfpage)
- [PDFAnnotation](https://developer.apple.com/documentation/pdfkit/pdfannotation)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
