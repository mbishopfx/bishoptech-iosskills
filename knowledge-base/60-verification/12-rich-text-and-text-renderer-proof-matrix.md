# Rich text and TextRenderer proof matrix

## Evidence boundary

This matrix separates source correctness, compile evidence, text behavior, accessibility, physical rendering, privacy, and release evidence. A successful parse or preview is not proof that a rich-text route is usable, accessible, or safe in the shipped app.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Stronger evidence | Failure to record |
| --- | --- | --- | --- |
| Markdown parsing is bounded | Unit tests for length, malformed syntax, partial result, and error policy | Test-plan result bundle with representative fixtures | Silent partial parse, unbounded input, or missing raw source |
| Supported attributes are controlled | Unit tests for accepted/removed Foundation and SwiftUI attributes | Fuzzed imported/model strings and policy snapshot | Arbitrary attributes reach the renderer |
| Links are safe | Unit tests for scheme/host policy and malformed URLs | UI test of allowed link plus rejected-link disclosure | Unvalidated model/imported link is clickable |
| TextRenderer compiles | Named target compile with exact SDK and availability branch | Archive build that includes the production target | A documentation sketch is presented as compiled |
| Renderer draws all content | Snapshot or UI fixture with renderer enabled and fallback | Physical-device screenshots across color schemes and sizes | Effect hides, clips, or replaces text |
| displayPadding prevents clipping | Long shadow/highlight fixture at bounds | Physical device with scale/color scheme combinations | Decoration clipped at the view edge |
| Layout attributes map to the right runs | Text.Layout/Text.Layout.Run fixture with known attributes | Multilingual, long-line, wrapping, and Dynamic Type fixture | Highlight depends on a single English line break |
| Truncation is visible | Fixture with lineLimit and Text.Layout.isTruncated assertion | UI review of expansion/recovery action | Important generated content disappears without state |
| Text selection is correct | TextEditor selection unit/UI fixture | Physical keyboard/touch selection in LTR, RTL, and mixed text | Apply action targets stale or wrong range |
| Source revision is enforced | Test that edits invalidate an in-flight proposal | Device run with cancellation and concurrent edit | Proposal applies to changed source |
| VoiceOver understands the route | Accessibility audit plus manual heading/link/status review | Physical device with generated/draft/approved states | Meaning exists only in color/highlight |
| Dynamic Type survives | Preview/UI matrix from standard through accessibility sizes | Physical device with largest supported size and keyboard | Action, source, or warning is truncated away |
| Right-to-left survives | Arabic/Hebrew and mixed-direction fixture | Physical device with selection and custom overlay | Overlay or selection assumes left-to-right coordinates |
| Reduced effects have parity | Reduce Motion and Reduce Transparency fixture | Physical-device run with the actual glass/material route | Renderer is the only indication of state |
| Large text remains legible | HIG-informed minimum/weight review and contrast checks | Physical device under light/dark and increased contrast | Thin/small text becomes unreadable |
| AI output remains a proposal | State-machine tests for raw/proposed/approved states | Screen recording of retry, stale, cancel, apply, and discard | Render completion or model return auto-saves |
| Provenance is inspectable | Unit/UI test for source identifier and fallback label | Physical VoiceOver/device review of source details | Highlight implies unsupported confidence |
| Privacy is consistent | Source/manifest/log review and retention test | Archive privacy report plus App Store Connect reconciliation | Raw text appears in logs or retained unexpectedly |
| Export/share is faithful | Unit test for AttributedString/Transferable representation | Destination acceptance and physical share flow | Preview-only or non-nil data treated as delivery |
| Performance is acceptable | Controlled XCTest/text fixture with long and attributed content | Physical device with Instruments/signposts and thermal observation | Renderer work runs every frame or leaks layout state |
| Release target is correct | Archive target membership, plist, capabilities, entitlements, and signing checks | TestFlight install and production-like account/service state | Simulator/preview used as release proof |

## Deterministic fixture pack

Keep fixtures small, named, and versioned:

- empty, whitespace-only, and single-character text;
- short title and multiline body;
- maximum permitted input and output lengths;
- malformed Markdown and deliberately partial Markdown;
- allowed, disallowed, malformed, and Unicode-domain links;
- nested emphasis, code-like text, emoji, diacritics, and combining marks;
- long unbroken tokens and mixed punctuation;
- English, Spanish, Arabic, Hebrew, and a mixed-direction sentence;
- standard, large, and accessibility Dynamic Type sizes;
- line limit with and without truncation;
- attached source-span markers, overlapping spans, and unmapped spans;
- model unavailable, canceled, filtered, stale, and apply-conflict states;
- reduced motion, reduced transparency, increased contrast, and dark mode;
- keyboard focus, insertion point, selection expansion, and selection replacement.

## TextRenderer-specific checks

1. Confirm the renderer is attached only to the intended text subtree.
2. Confirm the underlying Text is drawn for every branch.
3. Assert that the effect has a finite display padding and no unbounded geometry feedback.
4. Verify run attributes using Text.Layout.Run subscripts.
5. Verify typographic bounds on wrapped and mixed-direction lines.
6. Verify the renderer’s Animatable state does not trigger work unrelated to text.
7. Compare renderer-on and renderer-off screenshots for the same semantic state.
8. Confirm that a custom effect does not alter VoiceOver content, selection, links, or action reachability.

## Reviewable AI text checks

For every proposal, retain:

    source revision
    request identifier
    raw proposal
    validation result
    parse result and warnings
    link/attribute policy result
    displayed draft
    user decision
    approved record or discard result

If the product does not need audit retention, retain only the minimum evidence needed for debugging and state the deletion policy. Do not log raw sensitive text merely because it makes a test easier.

## Target and device notes

Record the Xcode/SDK version, deployment target, device model and OS, locale, Dynamic Type setting, color scheme, accessibility settings, build configuration, and fixture identifier for every screenshot or screen recording. A simulator can help with layout and state coverage; it does not prove physical glass rendering, touch ergonomics, font rasterization, memory pressure, thermal behavior, or system-service availability.

## Sources

- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [TextAttribute](https://developer.apple.com/documentation/swiftui/textattribute)
- [Text.Layout](https://developer.apple.com/documentation/swiftui/text/layout)
- [Text.Layout.Run](https://developer.apple.com/documentation/swiftui/text/layout/run)
- [Text.Layout.TypographicBounds](https://developer.apple.com/documentation/swiftui/text/layout/typographicbounds)
- [Text.LayoutKey](https://developer.apple.com/documentation/swiftui/text/layoutkey)
- [GraphicsContext](https://developer.apple.com/documentation/swiftui/graphicscontext)
- [Text](https://developer.apple.com/documentation/swiftui/text)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [TextSelectionAffinity](https://developer.apple.com/documentation/swiftui/textselectionaffinity)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [MarkdownParsingOptions](https://developer.apple.com/documentation/foundation/attributedstring/markdownparsingoptions)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Human Interface Guidelines: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
