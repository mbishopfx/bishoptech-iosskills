# Link preview and source-trust design

Rich link previews are small but high-trust UI. A title and image can make an external destination feel endorsed, so the design must keep presentation convenience separate from source truth.

## Preview anatomy

A trustworthy preview has a visible hierarchy:

1. source domain or source identity;
2. original URL or a safe, inspectable representation;
3. title and available media;
4. fetch state and freshness;
5. user action: Open, Share, Save, Retry, or Remove;
6. optional AI summary clearly labeled as generated.

The image is supporting content. It should never be the only cue for a destination, a safety claim, or a destructive action.

## Progressive states

Design the card as a state machine rather than a single skeleton:

| State | Treatment | User action |
| --- | --- | --- |
| URL received | Show domain and URL immediately | Open or fetch preview |
| Fetching | Keep the URL visible and show bounded progress | Cancel |
| Partial metadata | Render title/icon without waiting for every subresource | Open or retry media |
| Rich metadata | Show native rich link and freshness | Open, Share, Save |
| Redirected | Show original and returned destination distinctly when relevant | Inspect before opening |
| Timed out/failed | Preserve the URL and explain that preview is unavailable | Retry or open deliberately |
| Canceled | Return to the URL-only state without an error banner | Fetch again |
| Cached | Show cached preview with timestamp | Refresh or use cached result |
| Not allowed | Use a plain URL fallback and explain limited preview | Open or remove |

Do not let a loading spinner replace the source identity. A user should never be unable to see what URL the app is preparing to fetch.

## Native presentation and custom review shells

Prefer `LPLinkView` when the goal is a familiar Apple rich link. Its system-provided layout handles the common title/icon/image/video composition. In a SwiftUI app, wrap it in a small representable and keep loading/caching outside the view.

Use a custom SwiftUI card when the product needs review controls, provenance, or domain-specific actions. Preserve native conventions:

- semantic buttons instead of tappable decorative cards;
- system typography and spacing;
- clear source and action hierarchy;
- adaptive width and readable minimums;
- visible fallback when media is absent;
- no custom browser chrome pretending to be Safari.

## Liquid Glass composition

Liquid Glass works best as a grouping surface around the preview’s state and actions:

- glass container;
- source row with domain and freshness;
- title and media content;
- secondary generated-summary label;
- action row with Open, Share, Save, Retry.

Keep the URL and key source text outside the most translucent region if contrast suffers. Avoid morphing an Open button into a card-wide tap target with an unclear consequence. Reduce Motion should remove decorative transitions while leaving state changes understandable.

## Source trust and redirects

The original URL and metadata-returned URL are different facts. Show a redirect disclosure when:

- the host changes;
- the path indicates a login, download, or document transition;
- the user is about to share or save the link;
- the link entered a review queue or model context.

Do not call a destination “official,” “verified,” or “safe” merely because it produced metadata. A favicon, page title, or familiar logo is content supplied by the destination.

## Share and system surfaces

The share sheet is system-owned. Supply existing `LPLinkMetadata` through the documented activity-item metadata callback so the share preview can appear without another fetch. Do not show a fake share sheet inside a custom glass card.

When the user chooses Share, keep the item’s original URL and the visible title aligned. If the app adds a generated note or AI summary, make it an explicit separate payload and show the user what will be shared.

## AI review patterns

Good AI surfaces:

- “Suggested collection: Research” with the original URL visible;
- “This preview has no title; add a note?”;
- duplicate detection that names the URLs being compared;
- a short summary with a source link and generated label.

Unsafe patterns:

- replacing the URL with a model-created title;
- treating a preview image as evidence of identity or safety;
- auto-opening a destination because the model rated it highly;
- sharing a private URL or query string to a model without consent;
- hiding a redirect from the user.

The model should be optional. The preview remains useful with no model, no network, no image, or no cached metadata.

## Accessibility and localization

Make the full task work with VoiceOver, Dynamic Type, Voice Control, Switch Control, keyboard, and pointer input:

- expose source domain, title, freshness, and state as a coherent accessibility element;
- give Open, Share, Save, Retry, Cancel, and Remove named actions;
- announce failure and redirected destination in text;
- support long translated titles and right-to-left layouts;
- avoid color-only trust or freshness indicators;
- provide an accessible text alternative when an image carries meaningful context;
- use Reduce Motion and increased contrast settings.

A custom preview must not be less accessible than the plain URL fallback.

## Proof handoff

Design specifications should include:

- test URLs for success, redirect, no metadata, timeout, cancellation, and not-allowed states;
- cache freshness and invalidation rules;
- subresource on/off behavior;
- share-sheet metadata reuse;
- large text, localization, RTL, VoiceOver, and Reduce Motion fixtures;
- the exact AI proposal/review boundary;
- the signed device and release surface to verify.

## Sources

- [Link Presentation](https://developer.apple.com/documentation/linkpresentation)
- [LPMetadataProvider](https://developer.apple.com/documentation/linkpresentation/lpmetadataprovider)
- [LPLinkMetadata](https://developer.apple.com/documentation/linkpresentation/lplinkmetadata)
- [LPLinkView](https://developer.apple.com/documentation/linkpresentation/lplinkview)
- [UIActivityItemSource](https://developer.apple.com/documentation/uikit/uiactivityitemsource)
- [activityViewControllerLinkMetadata(_:)](https://developer.apple.com/documentation/uikit/uiactivityitemsource/activityviewcontrollerlinkmetadata%28_%3A%29)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
