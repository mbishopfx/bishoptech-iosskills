# Link Presentation preview proof matrix

Use this matrix to separate a successful metadata fetch from a trustworthy, cancellable, accessible, and releasable link experience.

| Claim | Evidence | Failure fixture / boundary |
| --- | --- | --- |
| URL policy is enforced | Scheme/host/private-query tests pass before a provider is created | Unsupported scheme, access token in analytics, or private URL sent without disclosure |
| A fetch is bounded | Provider timeout is configured and the timeout error maps to a URL fallback | Slow server, no network, or default 30-second wait blocks a scrolling surface |
| Cancellation is real | Selection change or task teardown calls `cancel()` and canceled result cannot replace the current record | Late completion overwrites a newer URL or shows a false error |
| Subresource policy is intentional | Title-only and rich-media fixtures show different provider settings and measured behavior | Image/video fetch occurs unexpectedly or metadata is assumed complete |
| Partial metadata is supported | Title, icon, image, video, and empty-field fixtures render without force-unwrapping | Missing field crashes, blank card, or invented source data |
| Original URL is preserved | Domain record and preview retain `originalURL` separately from returned `url` | Redirect silently replaces the user’s requested destination |
| Redirect trust is visible | Host/path-changing redirect fixture presents a disclosure before Open/Share | Preview logo/title is treated as identity or safety verification |
| Cache is safe and fresh | Secure serialization or typed DTO is versioned, scoped, timestamped, removable, and invalidated | Stale/private metadata reused for the wrong user or URL |
| `LPLinkView` is composed correctly | Named UIKit target renders metadata, URL placeholder, intrinsic size, and resize path | SwiftUI body starts networking, fixed height clips, or UIKit view is unavailable on target |
| SwiftUI fallback is equivalent | URL-only custom card remains readable and actionable without rich media | Glass image tile is the only way to discover the source |
| Share preview is reused | `UIActivityItemSource` returns existing metadata and system share sheet shows expected title/icon | Share sheet performs duplicate fetch or generated title replaces URL context |
| Share payload is clear | User can inspect original URL and any generated summary before sharing | AI note or private query string is silently included |
| Error states are accurate | Failed, timed out, canceled, not-allowed, cached, and partial states have distinct UI copy | Cancellation shown as failure or stale cache labeled live |
| AI remains a proposal | Typed summary/collection/duplicate proposal preserves source URL, freshness, and Apply/Reject state | Model hides URL, invents facts, opens link, or shares without review |
| Accessibility works | VoiceOver, Dynamic Type, high contrast, Reduce Motion, keyboard, pointer, Voice Control, and Switch Control complete Open/Share/Save/Retry/Cancel | Color-only state, unlabeled image, truncated title, or gesture-only card |
| Offline behavior is deliberate | No-network fixture renders cached metadata or URL-only state and offers retry | Network failure produces a blank surface or indefinite spinner |
| Release behavior is known | Device/release build checks target availability, share sheet, destination handoff, privacy copy, and cache deletion | Preview compile or simulator run treated as universal proof |

## Fixture set

Use controlled URLs or local fixtures with no private credentials:

- valid URL with title and icon;
- title-only response;
- no metadata response;
- missing icon/image/video;
- redirect to same host;
- redirect to different host;
- slow response and timeout;
- cancellation after selection changes;
- subresources enabled versus disabled;
- cached fresh and cached stale;
- corrupt/old cache schema;
- unsupported scheme/host/private query;
- share-sheet metadata reuse;
- long title, RTL text, large Dynamic Type, VoiceOver, Reduce Motion;
- model unavailable, proposal rejected, and user-edited proposal;
- offline URL-only fallback.

## Evidence ladder

1. URL and privacy unit tests.
2. Provider fetch/cancel/timeout/error tests.
3. Cache serialization/freshness tests.
4. UIKit and SwiftUI layout tests/previews.
5. System share-sheet run with known metadata.
6. Signed physical-device network/offline/accessibility run.
7. Destination navigation/authentication verification in the selected route.
8. Archive/signing/distribution evidence.

Record SDK, target, OS build, device, request policy, cache version, and destination fixture. A rendered preview is never proof that the external destination is safe or truthful.

## Sources

- [Link Presentation](https://developer.apple.com/documentation/linkpresentation)
- [LPMetadataProvider](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider)
- [LPError](https://developer.apple.com/documentation/linkpresentation/lperror)
- [timeout](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/timeout)
- [shouldFetchSubresources](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/shouldfetchsubresources)
- [cancel()](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/cancel%28%29)
- [LPLinkMetadata](https://developer.apple.com/documentation/linkpresentation/lplinkmetadata)
- [LPLinkView](https://developer.apple.com/documentation/linkpresentation/lplinkview)
- [UIActivityItemSource](https://developer.apple.com/documentation/uikit/uiactivityitemsource)
- [activityViewControllerLinkMetadata(_:)](https://developer.apple.com/documentation/uikit/uiactivityitemsource/activityviewcontrollerlinkmetadata%28_%3A%29)
- [UIActivityViewController](https://developer.apple.com/documentation/uikit/uiactivityviewcontroller)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
