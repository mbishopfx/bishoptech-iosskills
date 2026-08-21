# Link Presentation preview capability route

Use this route for native rich-link previews, source-aware reading lists, document/link cards, and share-sheet metadata. Keep the URL, fetched metadata, cache, UI state, AI proposal, and destination navigation as separate layers.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | Understand, save, share, or open a link with a native preview |
| Input | User-supplied or app-owned URL after scheme/host/privacy validation |
| Fetch | `LPMetadataProvider` with explicit timeout, cancellation, and subresource policy |
| Metadata | `LPLinkMetadata` or the current SDK’s `LinkMetadata` adapter |
| Presentation | `LPLinkView` via UIKit or a SwiftUI review card |
| Share | `UIActivityItemSource` metadata callback or `UIActivityItemsConfiguration` |
| Cache | Versioned secure-serialized presentation metadata plus source/freshness envelope |
| AI | Optional typed summary, collection, or duplicate proposal with original URL visible |
| Liquid Glass | Containing-app preview/review grouping; not fake browser chrome |
| Proof | URL policy, fetch/cancel/error, redirect/cache, UIKit/SwiftUI layout, share sheet, device/accessibility/release evidence |

## 1. Define the link domain model

Keep the domain record independent from `LPLinkMetadata`:

~~~swift
struct LinkRecord: Codable, Identifiable, Sendable {
    let id: UUID
    let originalURL: URL
    var returnedURL: URL?
    var title: String?
    var fetchedAt: Date?
    var state: State

    enum State: String, Codable, Sendable {
        case awaitingFetch
        case cached
        case fresh
        case failed
        case canceled
    }
}
~~~

The domain model owns user intent, privacy policy, freshness, and navigation. The Link Presentation object owns display metadata and can be regenerated.

## 2. Validate before fetching

Before creating a provider:

1. parse the URL;
2. allow only product-approved schemes;
3. remove or protect secrets from analytics and model context;
4. decide whether the URL is private, user-owned, or public;
5. show the user what will be fetched when the privacy impact is material;
6. assign a request ID so stale completions cannot overwrite the current record.

Do not treat URL validation as destination security validation. The preview only describes returned metadata.

## 3. Fetch with a bounded policy

Choose `LPMetadataProvider.timeout` and `shouldFetchSubresources` for the surface:

- list/feed: short timeout and no subresources for fast title/domain previews;
- detail/review: longer bounded timeout and subresources when the user asks for rich media;
- offline: use a valid cache or URL-only fallback;
- cancellation: cancel when selection changes or the task is no longer needed.

The provider’s default 30-second timeout may be too long for a scrolling list. Measure the selected target and device rather than assuming one budget fits every route.

## 4. Cache and share the same metadata

When metadata succeeds:

- retain original and returned URL separately;
- persist source/fetched time and a schema version;
- securely serialize only the presentation object or convert it into a domain DTO;
- apply a freshness policy before reuse;
- pass the existing metadata to the share-sheet callback;
- refresh asynchronously when the product’s policy allows.

Avoid a cache key that contains raw access tokens or private query strings. When the same URL has different user-specific responses, make the user/session scope explicit instead of sharing metadata globally.

## 5. Compose UIKit and SwiftUI

Use `LPLinkView` when a system-style rich link is enough. Wrap it in `UIViewRepresentable` only after the model owns fetch/cancel state. For a review flow, a custom SwiftUI card can add source, freshness, and Apply/Reject actions around the metadata.

The card should never open a destination merely because metadata arrived. Make Open explicit and route it through the product’s documented browser/authentication policy.

## 6. Share route

The share route is:

user taps Share -> create item source/configuration -> return original payload plus existing LPLinkMetadata -> present system activity view -> verify preview and final payload

On iPad, use the appropriate popover presentation. If an AI-generated summary is shared, separate it from the original URL and show the user the final contents before the system sheet appears.

## 7. AI proposal route

Use a typed proposal:

source metadata + original URL + freshness -> on-device summary/collection/duplicate proposal -> schema and privacy validation -> user review -> domain update

Never pass an access-token-bearing URL to the model just because it is present in metadata. Do not treat the title, image, or model summary as verified facts. A proposal rejected by the user must not alter the cache or destination link.

## 8. Liquid Glass surface

Use a glass container for the preview and review controls only after the URL-only fallback is complete. Keep the source domain, URL, state, and consequence text in high-contrast semantic content. Expose loading, timeout, canceled, stale, and redirected states as text.

## 9. Failure and recovery

Handle:

- invalid or disallowed URL;
- no network, timeout, cancellation, not-allowed, and unknown error;
- title-only or media-only metadata;
- redirected destination;
- stale or corrupted cache;
- superseded request ID;
- `LPLinkView` unavailable on a selected platform;
- share-sheet metadata missing;
- AI model unavailable or proposal rejected;
- user revokes privacy/network expectation.

## 10. Minimum evidence bundle

- URL policy and redaction tests;
- provider timeout/cancel/failure tests;
- subresource on/off fixtures;
- redirect and partial metadata fixtures;
- cache serialization/freshness tests;
- UIKit `LPLinkView` and SwiftUI wrapper layout;
- system share-sheet preview and final payload;
- accessibility/localization/offline evidence;
- signed device and release behavior for open/share/save.

## Sources

- [Link Presentation](https://developer.apple.com/documentation/linkpresentation)
- [LPMetadataProvider](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider)
- [timeout](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/timeout)
- [shouldFetchSubresources](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/shouldfetchsubresources)
- [cancel()](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider/cancel%28%29)
- [LPLinkMetadata](https://developer.apple.com/documentation/linkpresentation/lplinkmetadata)
- [LPLinkView](https://developer.apple.com/documentation/linkpresentation/lplinkview)
- [LinkMetadata](https://developer.apple.com/documentation/linkpresentation/linkmetadata)
- [UIActivityItemSource](https://developer.apple.com/documentation/uikit/uiactivityitemsource)
- [UIActivityViewController](https://developer.apple.com/documentation/uikit/uiactivityviewcontroller)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
