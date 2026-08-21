# Guided Generation and Typed Output

## Prefer a type over raw text when the app needs data

Raw model text is useful for a conversation or presentation. It is a poor boundary for persistence, routing, or UI state because the app must parse it and decide whether the parse is trustworthy. Guided generation describes the desired Swift type so the framework can constrain output to the structure the app expects.

## Generable and Guide

Use the Generable macro on a Swift structure or enumeration. Use Guide descriptions and value/count constraints only where they improve the schema. Keep descriptions short because schema text consumes context and can increase latency.

~~~swift
@Generable
struct CaptureDraft {
    @Guide(description: "A short title for the captured item.")
    var title: String

    @Guide(description: "The amount in the user’s local currency.")
    var amount: Decimal?

    @Guide(.minimumCount(0), .maximumCount(6))
    var tags: [String]
}

let session = LanguageModelSession(instructions: "Extract a reviewable draft from the source.")
let draft = try await session.respond(
    to: Prompt("Source text goes here"),
    generating: CaptureDraft.self
)
~~~

The API signature and macro availability are SDK-version-sensitive; use the current Foundation Models reference when compiling.

## Structure is not truth

Guided generation reduces malformed output. It does not prove the values are correct. Validate:

- required fields are present;
- numeric values are plausible;
- dates are in an acceptable range;
- generated identifiers do not replace real identifiers;
- source text supports the proposal;
- the user can edit before committing;
- deterministic rules reject unsafe or impossible values.

## Dynamic schema

Use DynamicGenerationSchema when the shape is known only at runtime. Keep schemas bounded and predictable. If the schema becomes a general-purpose form builder, first consider a deterministic schema and use the model only to fill candidate values.

## Partial results and cancellation

If the feature presents streaming or partial generated content, label it as a draft and make the transition to accepted data explicit. Cancel work when the user leaves or changes the source. Do not persist a partial model result as final domain truth.

## Sources

- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [GeneratedContent](https://developer.apple.com/documentation/foundationmodels/generatedcontent)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
