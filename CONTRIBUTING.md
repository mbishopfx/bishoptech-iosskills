# Contributing

Thank you for helping make Apple-native development guidance more precise.

This repository is a source-linked engineering reference and skill bundle. Contributions should make a future LLM or developer more accurate, more explicit about uncertainty, and better at verifying the real behavior of an Apple app.

## Before opening a change

- Search the knowledge base for an existing route before creating a duplicate.
- Use Apple Developer Documentation, Swift documentation, SDK interfaces, and Human Interface Guidelines as primary sources.
- Record the target SDK, deployment target, device family, entitlement, permission, account, and extension assumptions.
- Preserve source links close to version-sensitive claims.
- Separate source, static configuration, compile, fixture, simulator/UI, physical/system, account/server, signed artifact, TestFlight/App Store, and production evidence.
- Keep Liquid Glass functional and system-first; do not turn it into decorative blur.
- Keep AI outputs typed, reviewable, privacy-aware, cancellable, and unable to commit side effects without deterministic validation and explicit user review.

## Adding a knowledge-base route

Use the smallest set of pages that makes the route useful:

1. framework or capability route;
2. design and interaction contract;
3. proof matrix;
4. compile-oriented recipes when they add real value;
5. section index, coverage matrix, and official source registry wiring.

Every new page should have a Sources section, working local links, official external destinations, failure and fallback states, and a clear statement of what the evidence does not prove.

## Adding or changing a skill

Keep the package main file concise:

- trigger and scope;
- read-before-acting checklist;
- workflow;
- output contract;
- hard boundaries;
- official Sources.

Put detailed matrices, fixtures, recipes, and audits in one-level references. A package must be portable: no private paths, credentials, user data, generated test output, or unrelated repository files.

Update the human-readable package index and the distributable artifact when a package changes. Do not call a seeded or review-ready bundle a guarantee of Apple approval.

## Validation checklist

Before submitting:

- validate every changed skill with the skill creator's package validator;
- inspect the archive contents;
- check Markdown links, Sources headings, official hosts, local links, fence balance, and whitespace;
- typecheck affected Swift recipes against the named SDK when possible;
- live-check official links for version-sensitive routes;
- record what was checked, what it proves, and what remains unverified.

If physical hardware, an account, a signing identity, a system host, TestFlight, or production is required and unavailable, record the missing evidence boundary instead of fabricating a pass.

## Pull requests

Use a descriptive title and include:

- the user problem or route being improved;
- official sources and SDK/toolchain facts;
- files changed;
- validation commands and results;
- evidence level;
- known limitations and next refresh trigger.

Keep unrelated product, website, credential, and local-environment changes out of the pull request.
