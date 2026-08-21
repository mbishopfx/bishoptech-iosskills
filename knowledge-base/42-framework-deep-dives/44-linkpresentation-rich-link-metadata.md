# Link Presentation: rich links, metadata, and source-aware previews

Link Presentation is Apple’s route for fetching, supplying, and presenting content-rich URLs in a consistent native style. It is useful for link cards, share-sheet previews, document headers, source-aware reading lists, and AI review surfaces.

The route is:

user-supplied URL -> URL policy/identity -> metadata request -> cancellable result -> cache or review model -> LPLinkView/share/system surface

Metadata is presentation data. A title, image, redirect, or model summary is not proof that the destination is safe, current, accurate, or endorsed by Apple.

## 1. Choose the Link Presentation route

| Need | API route | Boundary |
| --- | --- | --- |
| Fetch a title, icon, image, or video for a URL | `LPMetadataProvider` | The request can fail, time out, be canceled, or be disallowed; all returned fields are optional. |
| Present a native rich link | `LPLinkView` | It is a UIKit view with intrinsic sizing; wrap it for SwiftUI rather than drawing a fake card first. |
| Supply link preview metadata to a share sheet | `UIActivityItemSource.activityViewControllerLinkMetadata(_:)` | Return known metadata to avoid a duplicate network fetch; sharing still has its own system lifecycle. |
| Cache fetched metadata | `LPLinkMetadata` secure serialization or a typed app cache | Store freshness and source identity beside the presentation object; cached metadata can be stale. |
| Present local file previews | `LPLinkMetadata` with local file URLs and the Quick Look Thumbnailing route | A local thumbnail is a representation of a file, not a remote page preview. |
| Use the current Swift-facing metadata value | `LinkMetadata` in the current SDK docs | Verify target availability and the selected SDK; do not silently substitute it for the class-based route in an older target. |

Do not use Link Presentation as a web crawler, an HTML security scanner, an ad attribution engine, or a guarantee that the content behind a URL is truthful.

## 2. `LPMetadataProvider` request lifecycle

For a remote URL, create an `LPMetadataProvider` for the metadata request and call `startFetchingMetadata(for:completionHandler:)`. The provider also accepts a `URLRequest` when request-level configuration is needed.

The provider exposes three important controls:

- `timeout`: the maximum interval before the request fails; Apple documents a default of 30 seconds;
- `shouldFetchSubresources`: whether icons, images, or video subresources are downloaded; the default is true;
- `cancel()`: cancels a request that has not completed and reports the documented cancellation error.

Set a product-appropriate timeout and decide whether a list screen really needs subresources. A title-only first pass can avoid unnecessary image/video work, then a user-initiated detail surface can request richer media. Do not start a provider on every SwiftUI body evaluation.

Treat the completion as a single state transition:

1. loading begins with a URL identity and request ID;
2. metadata arrives, or an error arrives;
3. the request is canceled or superseded if the user changes selection;
4. the view accepts only the current request ID;
5. the result is cached or discarded according to the source/freshness policy.

The provider is not a view model and is not a permanent cache. Keep it owned by a task or loader that can cancel it when the screen disappears.

## 3. Failure and availability states

`LPError` includes metadata-fetch failures, timeouts, cancellation, not-allowed responses, and unknown errors. The UI should distinguish them without exposing low-level error strings as user truth:

| Error/state | Product meaning | Fallback |
| --- | --- | --- |
| No network or fetch failed | Metadata is unavailable now | Show the original URL and a retry action |
| Timed out | The request exceeded the product’s budget | Keep the placeholder; retry on explicit demand |
| Canceled | The user changed route or left the screen | Do not show an error banner |
| Not allowed | The system/policy did not permit the fetch | Explain limited preview and preserve the URL |
| Missing title/image/icon | The server returned partial metadata | Render the available fields; never invent source facts |
| Redirected URL | The server returned metadata for another URL | Keep original and returned URL separate and visible when relevant |
| Cached | A prior result is available | Show freshness and allow a refresh policy |

All properties on `LPLinkMetadata` are optional. A product must work with only the original URL, a title, an icon, or no metadata at all.

## 4. `LPLinkMetadata` identity and contents

`LPLinkMetadata` can hold:

- `originalURL`: the URL the app asked Link Presentation to fetch;
- `url`: the URL that returned the metadata, including server-side redirects;
- `title`: a representative title;
- `iconProvider`: an `NSItemProvider` for a representative icon;
- `imageProvider`: an `NSItemProvider` for a representative image;
- `remoteVideoURL` or `videoProvider`: representative video data.

Use both URL fields when provenance matters. Never overwrite the original URL with a redirect just because the redirected URL is what the server returned. If the app has its own known metadata, it can construct an `LPLinkMetadata` object directly; Apple’s share-sheet guidance says to provide at least the original and returned URL fields when supplying custom metadata.

The class supports secure coding. Cache with a versioned envelope that includes the canonical URL, fetch timestamp, locale/region policy if relevant, whether subresources were requested, and a privacy-safe source identifier. Avoid treating `LPLinkMetadata` as a domain record; it is a presentation object that can be regenerated.

## 5. `LPLinkView` and UIKit/SwiftUI composition

`LPLinkView` is a UIKit `UIView` on iOS and related Apple platforms. Create it with metadata for a ready rich presentation or with a URL for a placeholder that can later receive metadata. It has an intrinsic size and responds to `sizeToFit`.

In SwiftUI, use `UIViewRepresentable` for the UIKit view when the platform’s native rich-link presentation is the right choice. Keep the SwiftUI model responsible for loading/canceling/cache state; keep the representable responsible for applying metadata and participating in layout. Do not put asynchronous networking inside `makeUIView` or `updateUIView`.

If a custom SwiftUI card is necessary for a product-specific review flow, use the metadata as input to a semantic card with a visible source URL, title, loading state, and fallback. The custom card is not automatically equivalent to `LPLinkView` or the share sheet’s preview.

## 6. Share-sheet metadata handoff

When a URL is shared through `UIActivityViewController`, a `UIActivityItemSource` can implement `activityViewControllerLinkMetadata(_:)` and return an existing `LPLinkMetadata` object. That lets the share sheet show the known title/icon/image without fetching metadata again.

The share sheet is system-owned. Keep the item source lightweight because its methods run on the main thread, and do not construct large media objects synchronously. On iPad, the containing app must present the activity view controller using the appropriate popover configuration. A share preview is a context cue; it does not verify the destination or guarantee that every activity uses all metadata fields.

## 7. Current Swift `LinkMetadata` route

The current Link Presentation documentation also exposes a Swift `LinkMetadata` value. It is serializable and Codable, can be created from a URL, can fetch with an explicit timeout and `includeSubresources` choice, and can load media through Transferable types.

This route is useful for a Swift-native model layer when the selected SDK and target availability support it. Keep it separate from class-based `LPLinkMetadata` at boundaries. Convert only in a small adapter, record the source URL and timestamp, and verify the exact availability in the target SDK before using it as a cross-platform abstraction.

## 8. Privacy, URL policy, and source trust

Treat a URL as user-controlled input:

- accept only the schemes and hosts the product intends to preview;
- preserve the original URL for display and audit;
- distinguish redirect results from the original request;
- avoid sending private URLs to a metadata service without user understanding;
- do not put query strings, access tokens, or document identifiers in analytics;
- redact URLs in logs unless the user explicitly requests a diagnostic export;
- make cached data removable and show freshness where it affects decisions;
- never infer safety, identity, ownership, or truth from a title, icon, image, or redirect.

Link Presentation fetches remote content. Use the app’s networking/privacy policy and document why a URL is fetched. If the product opens the destination, use the separate WebKit/Safari authentication and navigation guidance rather than assuming a preview fetch is a safe browser handoff.

## 9. On-device AI with link metadata

AI can help with a user-approved review task:

- summarize a title and visible metadata for a reading list;
- suggest a collection label such as “research” or “reference”;
- identify duplicate URLs after canonicalization;
- draft a note that visibly cites the original source;
- flag missing or conflicting metadata for human review.

Keep the model output typed and reviewable. Include the original URL, redirected URL when relevant, fetched timestamp, and source fields next to the proposal. Do not use an AI summary to replace the link, hide a redirect, claim that a page is safe, or silently share private URLs. If the model is unavailable, the rich-link route should still show the native preview or an original-URL fallback.

## 10. Liquid Glass and Apple-native preview design

Use the native `LPLinkView` when a familiar rich link is the product’s goal. For a custom review shell, use Liquid Glass as a container around:

- a plain “Link preview” title;
- source domain and original URL;
- title and available image/icon;
- loading/error/freshness status;
- Open, Share, Save, and Retry actions;
- optional AI summary labeled as generated.

Keep the original URL and the actionable destination visually distinct. Never make a glass image tile the only cue for a destructive action or automatic navigation. Support Dynamic Type, reduced motion, VoiceOver labels, high contrast, keyboard/pointer input, and long localized titles.

## 11. Verification boundary

Prove separately:

- URL validation and redaction;
- provider timeout/cancel/error behavior;
- title-only versus subresource-fetch configuration;
- redirect identity and cache freshness;
- partial metadata and missing-media fallback;
- `LPLinkView` layout in a named UIKit/SwiftUI target;
- share-sheet metadata reuse;
- user-controlled open/share/save actions;
- AI proposal review and no-model fallback;
- accessibility, localization, offline, and privacy settings;
- signed device/release behavior for the actual destination and share surfaces.

A preview, successful fetch, cached object, or generated summary does not prove that the destination is safe, current, accessible, or authoritative.

## Sources

- [Link Presentation](https://developer.apple.com/documentation/linkpresentation)
- [LPMetadataProvider](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider)
- [LPMetadataProvider fetch link metadata](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider)
- [timeout](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/timeout)
- [shouldFetchSubresources](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/shouldfetchsubresources)
- [cancel()](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/cancel%28%29)
- [LPError](https://developer.apple.com/documentation/linkpresentation/lperror)
- [LPLinkMetadata](https://developer.apple.com/documentation/linkpresentation/lplinkmetadata)
- [LPLinkView](https://developer.apple.com/documentation/linkpresentation/lplinkview)
- [LinkMetadata](https://developer.apple.com/documentation/linkpresentation/linkmetadata)
- [UIActivityItemSource](https://developer.apple.com/documentation/uikit/uiactivityitemsource)
- [activityViewControllerLinkMetadata(_:)](https://developer.apple.com/documentation/uikit/uiactivityitemsource/activityviewcontrollerlinkmetadata%28_%3A%29)
- [UIActivityViewController](https://developer.apple.com/documentation/uikit/uiactivityviewcontroller)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
