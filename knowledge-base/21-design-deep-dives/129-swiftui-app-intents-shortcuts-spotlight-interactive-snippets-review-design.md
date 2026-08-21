# SwiftUI App Intents, Shortcuts, Spotlight, and interactive snippet design

System discoverability is a product-design problem before it is an API problem. A person should understand what the app can do, where an action will run, what information is current, and whether a result is a suggestion, a confirmation, or a committed change.

Use this guide with the [system-discoverability review](../42-framework-deep-dives/101-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review.md), the [capability route](../50-capability-recipes/132-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-route.md), the [proof matrix](../60-verification/126-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-proof-matrix.md), and the [recipes](../70-code-recipes/144-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-recipes.md). Existing [interactive snippet](22-interactive-system-snippet-surfaces.md), [Spotlight](51-spotlight-search-and-activity-design.md), and [App Intents/Visual Intelligence](92-app-intents-system-surface-and-visual-intelligence-design.md) guides remain the detailed feature references.

## Design from the person’s job

Start with a job that is small enough to complete from the system:

| Job | Best first surface | Full app destination |
| --- | --- | --- |
| Show current status | static snippet, widget, or Siri dialogue | detail screen |
| Start a frequent action | App Shortcut, Action button, or Shortcuts | live activity or app scene if needed |
| Find one known record | Spotlight/AppEntity/OpenIntent | current detail/editor |
| Search a large catalog | Spotlight handoff to ShowInAppSearchResultsIntent | native search results |
| Confirm a small decision | confirmation snippet | full editor for complex scope |
| Track an ongoing task | Live Activity | progress/detail screen |
| Match something visible | Visual Intelligence/AppEntity result | entity detail |
| Edit complex content | OpenIntent/app scene | full SwiftUI editor |

Avoid exposing “open app” as the main shortcut when the system already provides an app icon or scene launch route. Apple’s Action button guidance also recommends essential, regular actions with short verb-led labels.

## The system handoff anatomy

Design the handoff as four visual and semantic layers:

~~~text
system trigger
  -> compact action/result language
  -> current app-owned representation
  -> explicit next action or app scene
~~~

The system owns the outer shell for Siri, Spotlight, Shortcuts, the Action button, and snippets. The app owns the action metadata, result view, snippet view, and full destination. Do not make the app’s screen look like a counterfeit Spotlight or Siri panel.

For every route, document:

- trigger phrase or system entry;
- what the person sees before running;
- what the action changes;
- what stays private;
- what can fail;
- whether confirmation is required;
- whether the result is spoken, visual, or both;
- where the person goes next;
- how the system surface recovers after account or data changes.

## App Shortcut design

An App Shortcut should represent a high-frequency, memorable job. Keep the set focused and order the most generally useful shortcuts first. Apple’s current HIG says apps can provide up to ten App Shortcuts and that they are available immediately after installation.

Good phrase:

> Start today’s focus session in Cognistration.

Weak phrase:

> Use the app to run the configurable premium focus experience with the current adaptive machine mode.

The first is short, verb-led, and understandable in audio. The second exposes internal product structure and depends on context the person should not need to remember.

Use:

- a short title that begins with a verb;
- a recognizable SF Symbol or representative image;
- the app name in the phrase;
- only the most useful optional parameter;
- localized variants that sound natural;
- complete spoken dialogue for audio-only contexts.

Do not put private record names, internal model revisions, or health/financial details into a phrase or tile label. App Shortcut metadata is discoverability copy and may be used by system machine-learning workflows in anonymized form.

If a feature belongs to a common app schema, use the schema route where it improves system understanding. Use a custom App Shortcut for unique product behavior. Do not create ten shortcuts merely to fill the allowance.

## Spotlight and entity design

Search representation is not a database export. Start with a small card:

~~~text
title
type/category
short context
freshness or status when meaningful
Open action
~~~

Keep the indexed title stable and human-readable. Use a stable ID that can re-resolve the current record. When a record is deleted, hidden, expired, or no longer authorized:

1. remove or invalidate the indexed projection;
2. ensure the OpenIntent rejects the old ID;
3. show a no-result or reauthorization path;
4. do not leak the old title in diagnostics or confirmation.

Use separate domains for accounts, workspaces, or libraries so a logout or deletion operation can remove the correct group. Sensitive content should be minimized or excluded; a local index is still a user-data surface.

For a large catalog, the handoff should keep the system query visible:

> Search in Projects for “solar audit”

Then open the app’s search screen with that query. Do not make a system result look like a complete catalog when the app has more current or filtered data.

## Snippet design

The HIG describes snippets as compact views for results or confirmation. A snippet should communicate its purpose visually; do not rely on repeating dialogue text at the top of the custom view. The full AppIntent dialogue still needs the critical facts for audio-only contexts.

### Result snippet

Use for:

- current status;
- a short summary;
- one result that does not need further action;
- a completed bounded task.

Visual anatomy:

~~~text
small symbol or entity image
title
one current fact
optional freshness/source line
~~~

### Confirmation snippet

Use for:

- archive/delete/send/purchase-like actions;
- a small choice that changes the result;
- a bounded follow-up decision.

Visual anatomy:

~~~text
what will happen
target and scope
important consequence
options or toggle
system Cancel + primary confirmation
~~~

Do not hide the target, count, destination, or irreversible consequence in a disclosure that the person is unlikely to open.

### Interactive snippet

Use buttons and toggles that invoke AppIntents. The snippet view is a projection; the nested intent owns the mutation. The system can re-create and perform the SnippetIntent multiple times, so render from current state and never put a side effect in rendering code.

Prefer one or two high-value controls. A snippet is not a miniature editor, a settings page, or a scrolling dashboard. When the task needs rich editing, open the app scene.

If the snippet’s backing state changes, reload it through the documented SnippetIntent reload route. Never use animation to imply that a mutation succeeded before persistence confirms it.

## Native visual hierarchy and Liquid Glass

Use SwiftUI’s semantic controls, typography, spacing, and current system presentation first. When an app-owned scene needs a Liquid Glass group:

- use it to group the primary action and current status;
- keep entity title and status readable over changing content;
- avoid large decorative translucent backdrops;
- keep a non-glass fallback under reduced transparency;
- preserve contrast and semantic focus;
- avoid mimicking system Siri/Spotlight surfaces.

For an in-app discoverability card:

~~~text
feature content
  [glass action group]
  current status + primary action
  [secondary ShortcutsLink or details]
~~~

For a snippet, the system determines the outer container. The app should supply a compact content view that is legible without assuming the app’s full design system or safe-area shell.

## AI and provenance design

If Apple Intelligence, Visual Intelligence, or an app-owned local model contributes context, show the boundary:

| User sees | Product meaning |
| --- | --- |
| “Suggested for this project” | A candidate matched from current entity/context |
| “From your saved projects” | The source set is app-owned and identified |
| “Review before applying” | The output is not domain truth |
| “This item is no longer available” | Current resolution failed |
| “Open in the app to continue” | The system surface is insufficient for the task |

Do not label an App Intent result “verified” merely because it came from Siri or Apple Intelligence. A system invocation is an external trigger; the app still validates current source truth and authorization.

For Visual Intelligence, labels are broad semantic hints and images may be ephemeral. The result card should communicate a possible match, not factual recognition of a person, object, place, or condition. Keep a no-match and ambiguous-match design.

## Accessibility and audio-only behavior

Every system-facing action has a spoken and visual design:

- title and description are concise and localized;
- dialogue includes critical target, scope, time, and result facts;
- snippets show the purpose without requiring repeated dialogue;
- buttons have verb-led labels and meaningful traits;
- a toggle’s current state is announced;
- no information depends on color, blur, animation, or translucency;
- system handoff and app scene focus land on the relevant element;
- errors offer a concrete next action.

Test:

- VoiceOver in the snippet and full app;
- Siri/Shortcuts with audio-only output;
- Dynamic Type and long localized entity names;
- increased contrast and reduced transparency;
- Reduce Motion;
- Voice Control and Switch Control for the opened app scene;
- keyboard focus and pointer input on iPadOS;
- right-to-left and long dialogue strings.

Do not use an accessibility label such as “AI result” without naming the content and action. Do not make a low-contrast glass card the only confirmation surface.

## Privacy and trust

Treat these as separate exposure choices:

| Surface | Exposure question |
| --- | --- |
| App Shortcut | Does phrase/title expose a private concept? |
| AppEntity | What fields can the system resolve/display? |
| Spotlight | What metadata is indexed and on which protection class? |
| Donation | What behavior signal is sent to system discovery? |
| Snippet | What appears outside the full app context? |
| Visual Intelligence | Is the label/pixel buffer retained or sent elsewhere? |
| Transferable | What representations can another app receive? |
| OpenIntent | Does the current account still permit the route? |

On logout, deletion, privacy-mode changes, or account switch, repair the index and reject stale entity IDs. Never put credentials, private URLs, signed requests, or raw prompt text into system-facing metadata.

## Error and fallback design

Design each route for:

- no entity match;
- ambiguous match;
- stale/deleted entity;
- protected data;
- sign-in or permission required;
- system surface unavailable;
- app extension unavailable;
- network or service failure;
- cancellation;
- current revision changed;
- device/OS feature unavailable.

Use a short spoken error and a clear visual action. “Something went wrong” is not enough for a system shortcut that could not complete. For a destructive action, an error must not read as success.

## Design handoff checklist

- [ ] The user job is small, frequent, and named in ordinary language.
- [ ] App schema versus custom App Shortcut is intentional.
- [ ] The AppEntity is a safe projection with stable current resolution.
- [ ] Spotlight indexing, deletion, reindexing, and OpenIntent are designed together.
- [ ] Large catalogs use an explicit in-app search handoff.
- [ ] Static, result, confirmation, snippet, Live Activity, and full-scene responsibilities are distinct.
- [ ] Interactive snippet controls invoke AppIntents and render from current state.
- [ ] AI/context output is labeled as suggestion or match, with source/freshness where useful.
- [ ] Liquid Glass is limited to app-owned hierarchy and has an accessibility fallback.
- [ ] Audio-only dialogue contains critical facts.
- [ ] VoiceOver, Dynamic Type, contrast, transparency, motion, Voice Control, Switch Control, keyboard, and pointer are tested.
- [ ] Logout, deletion, stale IDs, protected data, no-result, and cancellation are designed.
- [ ] The system route and physical-device proof plan are named.

## Sources

- [App Shortcuts](https://developer.apple.com/design/human-interface-guidelines/app-shortcuts)
- [Snippets](https://developer.apple.com/design/human-interface-guidelines/snippets)
- [Siri](https://developer.apple.com/design/human-interface-guidelines/siri)
- [Action button](https://developer.apple.com/design/human-interface-guidelines/action-button)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Accelerating app interactions with App Intents](https://developer.apple.com/documentation/appintents/acceleratingappinteractionswithappintents)
- [Donations and discovery](https://developer.apple.com/documentation/appintents/donations-and-discovery)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [IndexedEntity](https://developer.apple.com/documentation/appintents/indexedentity)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [Displaying static and interactive snippets](https://developer.apple.com/documentation/appintents/displaying-static-and-interactive-snippets)
- [SnippetIntent](https://developer.apple.com/documentation/appintents/snippetintent)
- [Visual presentation](https://developer.apple.com/documentation/appintents/visual-presentation)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [CSSearchableIndex](https://developer.apple.com/documentation/corespotlight/cssearchableindex)
- [CSUserQuery](https://developer.apple.com/documentation/corespotlight/csuserquery)
- [Building a search interface for your app](https://developer.apple.com/documentation/corespotlight/building-a-search-interface-for-your-app)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
