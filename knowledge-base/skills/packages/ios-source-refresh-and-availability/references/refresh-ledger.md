# Source-refresh ledger

Use one row per affected claim or API route. Keep the ledger close to the
knowledge-base receipt or package revision.

| Field | Record |
| --- | --- |
| signal | API/deprecation/availability/entitlement/privacy/HIG/compiler/policy change |
| official source | canonical Apple/Swift URL and page title |
| SDK evidence | Xcode/toolchain/SDK/module/header observation |
| scope | framework/symbol/target/platform/device/extension |
| old claim | exact prior wording or route |
| classification | current/stale/ambiguous/gated/deprecated/historical |
| new claim | source-grounded replacement and boundary |
| affected graph | pages/recipes/indexes/matrices/packages/fixtures/artifacts |
| tests | typecheck/unit/UI/device/package commands |
| URL sweep | count, status, failures, redirects/fixes |
| artifact | archive path/name/contents and privacy review |
| evidence | source/compile/fixture/UI/device/system/signed/TestFlight/production |
| next trigger | next SDK, OS, source update, or real-project check |

## Search graph

Search for all of the following before changing a route:

- symbol and framework names;
- old and new documentation paths;
- deployment target and OS strings;
- entitlement, capability, privacy, and usage-description keys;
- “available,” “deprecated,” “Beta,” “not supported,” and “to verify”;
- recipe declarations and code fences;
- package names and role-routing links;
- coverage, availability, source-registry, README, and GoalBuddy receipt rows;
- evaluation fixture prompts that may encode the old behavior.

Use `rg` first and inspect each hit in context. Do not replace text globally when
one occurrence is a historical note or a different target route.

## Validation sequence

1. structural Markdown/local-link/official-host audit;
2. source-registry and index audit;
3. affected recipe typecheck against the installed SDK;
4. relevant test/evaluation fixture run;
5. live official URL check with redirect and range fallback;
6. skill quick validation and `.skill` packaging;
7. archive content/secret/private-path inspection;
8. GoalBuddy state check and receipt.

## Sources

- [Documentation updates](https://developer.apple.com/documentation/updates)
- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Swift documentation](https://swift.org/documentation/)
- [Xcode release notes](https://developer.apple.com/documentation/xcode-release-notes)
