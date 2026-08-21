---
name: ios-source-refresh-and-availability
description: Refresh an Apple-platform knowledge route or skill bundle when Apple documentation, SDK interfaces, OS availability, entitlements, privacy rules, or release guidance changes. Use to audit source provenance, locate stale claims, update affected Markdown/recipes/packages, and rerun structural, live-link, compile, and packaging validation.
---

# iOS source refresh and availability maintenance

Keep Apple engineering guidance current without rewriting unrelated history or
turning an SDK symbol into a product guarantee. Trace a change from official
source and installed interface to affected route pages, recipes, availability
matrices, source registry, skill references, evaluation fixtures, and packaged
artifacts.

`change signal -> official source/SDK audit -> affected graph -> narrow update -> validation -> receipt`

## Read before acting

- Inspect the repository’s knowledge-base map, source registry, coverage and
  availability matrices, relevant route/design/recipe/proof pages, package
  references, and current distributable archive.
- Read [refresh-ledger.md](references/refresh-ledger.md) and
  [provenance-and-evidence.md](references/provenance-and-evidence.md).
- Reopen the exact official Apple/Swift pages and installed SDK interfaces. Use
  official primary sources for availability, entitlement, privacy, HIG, and
  release claims. Treat secondary examples as discovery only.
- Record the SDK/Xcode/toolchain, OS, target, device family, package revision,
  and date for the refresh. Mark future/Beta-sensitive behavior as such.

## Refresh workflow

1. **Define the signal.** Capture the changed API, deprecation, availability,
   entitlement, privacy requirement, HIG guidance, compiler diagnostic, or
   release-policy change and its user/project impact.
2. **Audit the source.** Open the canonical Apple/Swift documentation, note
   exact symbols/URLs/availability text, and inspect the installed SDK module or
   headers for the selected target. Do not rely on memory or a stale snippet.
3. **Build the affected graph.** Search route pages, recipes, proof matrices,
   design pages, catalog/availability rows, source registry, packages,
   evaluation fixtures, and packaged archives for the symbol, URL, claim, or
   package reference.
4. **Classify drift.** Mark each occurrence as current, stale, ambiguous,
   target-gated, device-gated, entitlement/permission-gated, deprecated,
   historical, or unrelated. Preserve historical evidence while preventing it
   from reading as current guidance.
5. **Patch the narrowest set.** Update source links, API signatures, guards,
   configuration gates, failure/fallback states, code recipes, tests, indexes,
   and skill references that are actually affected. Do not perform a broad
   stylistic rewrite.
6. **Validate structure and local graph.** Check Sources headings, official
   hosts, local links, fence balance, trailing whitespace, count/coverage, and
   source-registry/index wiring.
7. **Validate behavior and artifacts.** Typecheck affected Swift recipes with
   the installed SDK, run relevant tests/evaluation fixtures, live-check
   official URLs, package changed skills, and inspect archive contents for
   private paths, credentials, stale claims, or generated noise.
8. **Write the receipt.** List changed files, source/SDK evidence, commands and
   results, evidence level, remaining uncertainty, and the next refresh trigger.

## Availability record

For each changed capability, record:

- framework/module and exact symbols;
- minimum OS and SDK observed;
- platform/device family and hardware requirements;
- target type, extension/process, and deployment target;
- entitlement/capability, usage description, privacy manifest, account/service,
  region, language asset, and model gates;
- Beta/deprecation/changed-API status;
- fallback and cancellation/recovery behavior;
- compile/typecheck, simulator, physical/system, archive, TestFlight, or
  production evidence level;
- official source URL and last-reviewed SDK/toolchain/date.

Do not write “available on iOS 26” when the feature also depends on a device,
entitlement, account, region, model asset, extension, or system host.

## Skill-bundle maintenance

When a route change affects a skill:

- update the skill’s trigger description only when its scope changed;
- keep the core workflow concise and move detailed variants into one-level
  references;
- link the affected knowledge-base route and official source near the claim;
- update role-routing, output templates, quality gates, and evaluation fixtures;
- refresh the `.skill` archive through the official package validator;
- inspect archive names/paths and ensure no workspace-private path, secret,
  user data, stale URL, or generated test output is included;
- record whether the artifact is a seeded/open-source-oriented bundle or a
  publication-ready release. Do not imply App Store approval.

## Output contract

Return:

```text
# Apple source-refresh handoff

Change signal:
Official source and SDK evidence:
Affected route graph:
Availability/configuration changes:
Files changed:
Recipe/test/package validation:
Live URL/archive validation:
Current versus historical claims:
Evidence level:
Uncertainty and open gaps:
Next refresh trigger:
```

## Hard boundaries

- Do not use secondary sources as authority for current Apple API or policy
  claims when official documentation or installed interfaces are available.
- Do not change an API claim without checking the target SDK and deployment
  assumptions that make it true or false.
- Do not erase history to hide a stale claim; label it and route readers to the
  current page.
- Do not claim an app compiles, runs on hardware, passes App Review, or behaves
  in production from a documentation refresh alone.
- Do not package secrets, private workspace paths, user data, unreviewed
  generated text, or stale/private source links.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Documentation updates](https://developer.apple.com/documentation/updates)
- [Swift](https://swift.org/documentation/)
- [The Swift Programming Language](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/)
- [Xcode release notes](https://developer.apple.com/documentation/xcode-release-notes)
- [SDK and software release notes](https://developer.apple.com/documentation/xcode-release-notes)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
