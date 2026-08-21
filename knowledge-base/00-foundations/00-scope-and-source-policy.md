# Scope and Source Policy

## Purpose

This knowledge base exists to help design and build iOS apps, not to replace the docs. The useful unit is a source-linked decision: “for this capability, start with this framework, model the data this way, and verify these conditions.”

## Primary sources

Use the following source order:

1. Apple Developer API reference and framework articles.
2. Apple Human Interface Guidelines and Technology Overviews.
3. Official Apple sample code and WWDC material linked from Apple Developer pages.
4. The official Swift Book for Swift language and concurrency rules.

Search results, blog posts, generated code, and remembered API names are discovery aids only. They are not evidence for a claim until the official source is checked.

## What each note should contain

Every substantive note should answer:

- What user outcome does this support?
- What is the Apple-native route?
- What is the smallest correct mental model?
- What availability, permission, entitlement, model, or platform caveat matters?
- What should be reviewed by a human?
- What does a preview, simulator, physical device, and release test prove?
- Which official sources support the claims?

## Availability language

Use cautious wording:

- “Available in the SDK” means the compiler can see an API for a selected SDK.
- “Available at runtime” means the installed OS/device satisfies the API’s availability.
- “Available on this device” means the device, settings, permissions, language assets, or Apple Intelligence state satisfy the feature’s requirements.
- “Verified” means the stated evidence was actually collected. It never means “the docs say it should work.”

When a feature is new or model-backed, include an availability branch and a useful fallback. Do not make a primary screen depend on an unavailable model, language asset, permission, or network service.

## Copyright and synthesis

Paraphrase the behavior and decisions. Keep code examples short and original. Link to the source page instead of copying documentation sections, sample projects, or long explanations.

## Design integrity

“Apple-like” in this library means:

- system controls before custom replicas;
- semantic text styles and system colors before fixed pixel values;
- standard navigation, safe areas, sheets, lists, forms, toolbars, and accessibility behavior;
- Liquid Glass used as a functional layer with clear hierarchy;
- custom visuals that are original and do not imply Apple ownership.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [The Swift Programming Language: Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
