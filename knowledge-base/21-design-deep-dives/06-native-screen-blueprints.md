# Native Screen Blueprints

## Purpose

These blueprints turn Apple’s design principles and SwiftUI’s system components into repeatable screen decisions. They are implementation briefs, not screenshot-cloning prompts. Each one starts with the user’s task, names the hierarchy, chooses native behavior, and makes failure and accessibility states explicit.

Apple-like quality comes from a coherent relationship between content, controls, navigation, typography, motion, and the device—not from putting a translucent rounded rectangle behind every view. Treat Liquid Glass as a functional layer for controls and navigation, while the product’s content remains the subject.

## The screen contract

Before writing a view, record the following:

| Decision | Required answer |
| --- | --- |
| User outcome | What should the person understand, decide, or finish on this screen? |
| Primary content | What proves progress, status, or success? |
| Primary action | What is the one most important action, and is it safe, reversible, or destructive? |
| Navigation | Is the hierarchy a stack, split view, tab, sidebar, sheet, or system surface? |
| State | What does loading, empty, success, error, permission denied, and unavailable mean? |
| Adaptation | What changes for Dynamic Type, compact/regular width, orientation, keyboard, pointer, or localization? |
| Material | Which functional elements need a system style or custom glass effect, and why? |
| Accessibility | What will VoiceOver announce, where does focus go, and what non-gesture route exists? |
| Proof | Which preview, UI test, simulator scenario, and physical-device check are required? |

Do not make the material decision before the hierarchy decision. If a standard `NavigationStack`, `ToolbarItem`, `Form`, `List`, `Button`, `Sheet`, or `confirmationDialog` expresses the interaction, use it first and allow the system to supply the current platform treatment.

## Shared state contract

Every blueprint below includes the same user-visible state vocabulary. The exact copy should be localized and product-specific, but the state must be deliberate.

| State | Design requirement |
| --- | --- |
| Loading | Preserve the screen’s structure where possible; show progress without pretending that content is ready. Disable only actions that truly cannot run. |
| Empty | Explain why the collection is empty and offer the next useful action. Do not use a blank glass panel as the explanation. |
| Content | Keep the primary content visually dominant; expose secondary actions progressively. |
| Error | Say what failed, whether user data is safe, and what can be retried or repaired. Keep the failed state accessible. |
| Permission or unavailable | Explain the capability, why it matters to this task, and how to continue without it when possible. Never imply that a denied permission was granted. |
| Accessibility | Preserve meaning with larger text, increased contrast, reduced transparency, reduced motion, VoiceOver, Voice Control, Switch Control, keyboard, and localization. |

## Blueprint 1: dashboard or home

### Use it when

The person needs a fast read of current status and a small number of next actions. A dashboard is not a decorative wall of cards; it is a prioritized answer to “what matters now?”

### Hierarchy

1. Navigation title or identity of the workspace.
2. One primary status, result, or progress statement.
3. The next action that changes that status.
4. Related sections ordered by the user’s task, not by whichever data is easiest to render.
5. Secondary settings and history in the toolbar, navigation destination, or detail view.

### Native structure

- Use `NavigationStack` for a compact iPhone flow.
- Use `NavigationSplitView` when a regular-width device benefits from a persistent sidebar and detail column.
- Use `List` and `Section` for scan-heavy rows or settings-like content; use `ScrollView` with semantic sections when the content is more editorial or composed.
- Put the primary action in a native `Button` or toolbar location before considering a floating control.
- Use a `ProgressView`, `Gauge`, `ContentUnavailableView`, or `Label` when the state has a standard system expression.
- Keep domain state and side effects outside the view; the screen should render a state contract rather than own the repository or model session.

### State matrix

| State | Dashboard behavior |
| --- | --- |
| Loading | Render the title and a meaningful progress indication; do not show stale “complete” metrics as if they were current. |
| Empty | Name the missing setup or data and give one primary “get started” action; keep optional education secondary. |
| Content | Lead with the current outcome, then the smallest set of supporting sections; make rows navigable with visible labels. |
| Error | Preserve the title and explain whether refresh, retry, or offline use is available; keep retry as a labeled button. |
| Permission or unavailable | Explain the blocked capability beside the affected feature and provide a useful manual or read-only fallback. |
| Accessibility | Ensure section headings, status values, and row actions have an intentional reading order; test the dashboard at the largest text sizes and in VoiceOver. |

### Liquid Glass decision

Let the navigation bar, toolbar, tab bar, sheet, and system controls adopt Liquid Glass automatically. A custom glass control is justified only when it is a distinct, high-value functional action that must float above changing content. If used, make the control semantic first, give it a meaningful label, keep tint sparse, and test it over light, dark, colorful, and text-heavy backgrounds.

### Adaptation and proof

- At compact width, prioritize the status and next action in a single reading column.
- At regular width, move navigation or filters into a sidebar rather than shrinking every card.
- Let text styles and flexible stacks grow with Dynamic Type; avoid fixed card heights around text.
- Test no data, stale data, offline data, denied permission, long localized labels, right-to-left layout, Reduce Transparency, Reduce Motion, Increased Contrast, and VoiceOver.
- Verify scrolling, hit targets, and any custom glass action on a physical target device. A preview proves the supplied state renders; it does not prove device material behavior or service availability.

## Blueprint 2: detail view or inspector

### Use it when

The person has selected an item and needs to understand it, inspect its current state, or take a small set of contextual actions.

### Hierarchy

1. Identity: what item is being inspected?
2. State: what is true about it now?
3. Evidence: which fields, media, history, or explanation support that state?
4. Primary contextual action.
5. Secondary, destructive, or advanced actions behind a toolbar menu, confirmation, or separate inspector.

### Native structure

- Navigate with `NavigationLink` and `navigationDestination` inside a `NavigationStack`.
- Use a `NavigationSplitView` for list/detail or list/content/detail layouts when the width and task justify it.
- Use `toolbar` for actions that belong to the current item; use a `Menu` for related secondary actions.
- Use `inspector(isPresented:content:)` or a sheet when an auxiliary panel genuinely helps on supported platforms.
- Use `safeAreaBar` or `safeAreaInset` for a persistent commit/action bar only when the action must remain available while content scrolls.
- Keep identity and state visible in text. A color, icon, or material effect may reinforce state but cannot be the only signal.

### State matrix

| State | Detail behavior |
| --- | --- |
| Loading | Show the item identity when known and a progress state for the fields that are still resolving; keep back navigation available. |
| Empty | If the selection is missing, provide a useful placeholder such as “Select an item” or return to the collection; do not show a misleading blank inspector. |
| Content | Group related fields with headings and readable spacing; place the most consequential action near the item’s state. |
| Error | Identify whether the item, a single field, or a remote resource failed; allow targeted retry without discarding known content. |
| Permission or unavailable | Mark the affected field as unavailable, explain the capability boundary, and provide a manual route or settings path when appropriate. |
| Accessibility | Make the item name, state, values, and actions announce in a predictable order; expose custom state with accessibility values and traits rather than visual styling alone. |

### Liquid Glass decision

Use the system navigation and toolbar treatment. A custom glass action bar is appropriate only when it is a small, related group of contextual actions that must stay above scrolling detail content. Keep destructive actions visually and semantically distinct; do not hide a destructive action inside a visually identical glass cluster.

### Adaptation and proof

- On iPhone, use a stack or sheet for the inspector; on iPad, keep the list and detail visible when that reduces context switching.
- Keep field labels and values flexible for large text and localization.
- Test deep links, missing selections, deleted items, interrupted loads, back navigation during an in-flight operation, and repeated actions.
- Verify the persistent action remains above the keyboard and safe areas, and that content is not hidden beneath a custom bar.

## Blueprint 3: form or editor

### Use it when

The person is creating, correcting, or refining information that needs a clear commit boundary. A form and a rich editor share the same state discipline, even when their controls differ.

### Hierarchy

1. What is being created or edited?
2. The smallest set of required fields.
3. Optional details grouped behind clear sections.
4. Inline validation and recovery guidance.
5. Save, apply, cancel, or discard with an explicit commit boundary.

### Native structure

- Use `Form` and grouped sections for structured fields, settings, and short edits.
- Use `TextField`, `TextEditor`, `Picker`, `DatePicker`, `Toggle`, and `Stepper` for their semantic input behavior before building a custom control.
- Use `@FocusState` and submit labels to make keyboard movement and completion predictable.
- Preserve draft state separately from persisted state. Saving is a domain operation whose result must be represented honestly in the UI.
- Use system Writing Tools or text-system integrations where the target field and product task support them; do not present a custom “AI rewrite” control as if it were Apple Intelligence.
- Use a sheet for a focused edit when the person should review or cancel before changing the underlying record.

### State matrix

| State | Form/editor behavior |
| --- | --- |
| Loading | Load the existing draft or reference data before accepting edits that could be overwritten; show which fields are unavailable. |
| Empty | Start with an explicit blank draft and useful field guidance; do not confuse “no saved record” with an error. |
| Content | Show required and optional structure, preserve edits across focus changes, and make the commit action obvious. |
| Error | Keep the draft recoverable, identify field-level versus save-level errors, and offer retry without clearing input. |
| Permission or unavailable | Explain which input or system capability is unavailable and offer a manual input path where possible. |
| Accessibility | Use visible labels, proper focus order, sufficient error announcement, Dynamic Type-safe fields, and non-gesture commit/cancel routes. |

### Liquid Glass decision

Let `Form`, navigation, and sheet chrome use system styling. Do not put a glass panel behind every field. If a save/apply control must remain available over a long editor, use the platform’s safe-area and toolbar mechanisms first; a custom glass action group should contain only the related commit controls and remain legible when effects are reduced.

### Adaptation and proof

- Make the editor scroll when the keyboard and large text require it; never rely on a fixed-height field stack.
- Test focus traversal, keyboard dismissal, undo/redo expectations, draft restoration, cancellation, repeated save, validation while offline, and app backgrounding.
- Test long strings, text selection, VoiceOver editing, Voice Control, Switch Control, right-to-left text, and any Writing Tools or language-model availability boundary.
- Compile the form in the selected SDK and test real text input on a physical device before making claims about editing behavior.

## Blueprint 4: search or browse

### Use it when

The person needs to find an item in a collection, narrow a result set, or browse a meaningful body of content.

### Hierarchy

1. What collection is being searched or browsed?
2. Search field or the smallest useful filter set.
3. Result identity and the reason each result matches.
4. Empty/no-result explanation and recovery.
5. Secondary sorting, filtering, or scope controls.

### Native structure

- Add `.searchable` to a `NavigationStack` or the appropriate column in a `NavigationSplitView`.
- Use `List`, `LazyVStack`, or a platform-appropriate grid based on scanning and selection needs.
- Use `onSubmit(of: .search)` when a search is expensive or should wait for explicit submission; do not make a remote request on every keystroke without a cancellation/debouncing policy.
- Use tokens or scope controls only when they reduce ambiguity; each token needs a readable label and a clear removal route.
- Make result rows semantic `NavigationLink`s or buttons, not tap-sensitive decorative cards.

### State matrix

| State | Search/browse behavior |
| --- | --- |
| Loading | Keep the query visible and show progress near the result region; do not erase the person’s query while work is in flight. |
| Empty | Distinguish an untouched collection from a query with no matches; provide the next useful action for each. |
| Content | Show why a result is relevant, preserve stable identity, and keep selection and navigation predictable. |
| Error | Preserve query and filters, identify whether the failure is local or remote, and allow retry or offline browsing if supported. |
| Permission or unavailable | Explain why the source cannot be searched and offer another source or a manual route. |
| Accessibility | Expose the search purpose, token meaning, result count/status, and row action; ensure focus does not jump unexpectedly as results update. |

### Liquid Glass decision

Use the system search field, toolbar, tab, and navigation surfaces. A custom glass filter cluster is justified only for a small, related set of high-value scopes that remains functional when the user changes appearance or accessibility settings. Do not use glass to make a no-result or loading state look full.

### Adaptation and proof

- Place search structurally in the navigation column that owns the collection.
- Verify result rows with long titles, missing thumbnails, duplicate names, large text, and right-to-left layout.
- Test keyboard submission, cancellation, rapid query changes, network loss, permissions, deep links to a result, and VoiceOver focus stability.

## Blueprint 5: sheet, review, or confirmation

### Use it when

The person needs a focused temporary task, must review a proposed change, or needs to confirm a consequential action before it commits.

### Hierarchy

1. Why is the sheet present?
2. What decision or edit is being requested?
3. What will change if the person commits?
4. Primary commit and safe cancel/dismiss routes.
5. Destructive or advanced alternatives with explicit wording.

### Native structure

- Use `.sheet` for a focused task that has its own navigation or edit lifecycle.
- Use `.presentationDetents` and the system drag indicator when a partial-height presentation helps without hiding required content.
- Use `confirmationDialog` for a small set of contextual choices or destructive confirmation, with a source control that makes the origin clear.
- Use `Alert` only for urgent, concise decisions; do not turn a complex review into an alert.
- Return a result or domain intent from the sheet; do not mutate the parent’s durable model on every keystroke unless that is the documented product behavior.

### State matrix

| State | Sheet/review behavior |
| --- | --- |
| Loading | Explain what is being prepared and keep cancellation available if the operation can be cancelled. |
| Empty | State that there is nothing to review or choose and give a clear dismiss or create path. |
| Content | Summarize the proposed change in plain language, then expose the commit action with its consequence. |
| Error | Keep the review data and explain whether retry is safe; do not dismiss after a failed commit unless the user explicitly chooses it. |
| Permission or unavailable | Explain the blocked step and offer a route back to the parent or a non-privileged alternative. |
| Accessibility | Give the sheet a meaningful title, set focus intentionally, announce validation/commit results, and ensure the decision can be completed without a swipe-only gesture. |

### Liquid Glass decision

Sheets, action sheets, and their system chrome already participate in the platform material. Remove custom background effects that fight the system presentation. A custom glass control inside the sheet must be a functional action, not a decorative panel, and must preserve contrast at partial and full height.

### Adaptation and proof

- Test every supported presentation detent with large text, keyboard, VoiceOver, and localized copy.
- Verify the source control, dismissal behavior, cancellation, and destructive confirmation on iPhone and iPad idioms.
- Test repeated presentation, state restoration, commit failure, backgrounding, and interruption.

## Blueprint 6: compact utility or one-glance tool

### Use it when

The person needs one small, frequent action or a brief piece of status. This may be an in-app utility, a widget, a Live Activity, a control, or a compact screen—not a miniature version of the whole app.

### Hierarchy

1. One glanceable fact or one primary action.
2. The smallest context needed to interpret it.
3. A direct route to the full app when more work is required.

### Native structure

- Use a semantic `Button`, `Toggle`, `ProgressView`, `Gauge`, `Label`, or `ControlGroup` for the compact action.
- Use WidgetKit, Live Activities, App Intents, or system controls when the requirement is truly a system-surface requirement; do not recreate a system surface inside the app without the same lifecycle contract.
- Keep compact content readable at large text and meaningful without color.
- Use one related glass action cluster only when it communicates a small functional group and the target surface supports it.
- Move complex editing, history, and configuration to a full-screen route.

### State matrix

| State | Compact utility behavior |
| --- | --- |
| Loading | Show a bounded progress state or last-known status with an honest freshness label; never imply live data if it is stale. |
| Empty | State what must be configured and offer one setup route; keep the compact surface from becoming a dead end. |
| Content | Present one fact and one obvious action; use secondary detail only when it can be read without scanning a miniature dashboard. |
| Error | Use concise status plus a route to repair or retry; preserve the last safe state when appropriate and identify its age. |
| Permission or unavailable | State that the device/service capability is unavailable and link to the full-app explanation or manual fallback. |
| Accessibility | Provide a full spoken description of value, unit, freshness, and action; test Bold Text, Dynamic Type, contrast, VoiceOver, and alternate input. |

### Liquid Glass decision

Use the system style of the target surface. In an in-app compact utility, a glass button can highlight the one functional action; it should not become a translucent canvas behind the entire utility. If several controls are necessary, group only related controls in `GlassEffectContainer` and verify that the group remains understandable without morphing.

### Adaptation and proof

- Test the smallest supported size, large text, long localized status, stale data, denied permissions, and background refresh failure.
- Verify the action’s handoff to the full app, the deep link, and the system surface lifecycle where applicable.
- Profile frequent updates and glass animations on the physical devices that the product supports; previews and simulator runs are not release evidence for device-specific refresh or material performance.

## Cross-blueprint review gates

### Hierarchy gate

- Can a new person state the screen’s purpose after a short glance?
- Is there one primary action, with secondary actions progressively disclosed?
- Does the content remain understandable if all custom color and glass effects are removed?
- Are system controls and standard containers carrying the interaction semantics?

### Adaptive gate

- Does the layout respond to proposals, safe areas, Dynamic Type, orientation, and regular/compact width without magic screen-sized assumptions?
- Are iPad, keyboard, pointer, and multitasking behaviors intentionally supported or explicitly out of scope?
- Do localized strings, right-to-left layout, pluralization, dates, and numbers fit the same state model?

### Accessibility and motion gate

- Does VoiceOver announce the screen title, state, values, actions, and errors in a useful order?
- Do larger text, Increased Contrast, Reduce Transparency, and reduced motion preserve meaning and control discoverability?
- Is every important gesture available through a semantic control, keyboard, Voice Control, or Switch Control route where supported?
- Are haptics and animation confirmations paired with visible/accessibility state?

### Liquid Glass gate

- Is custom glass limited to a justified functional/navigation surface?
- Are custom backgrounds removed from standard bars, sheets, popovers, tabs, and controls where they would fight system behavior?
- Are tint, shape, grouping, identity, and transitions tied to meaning rather than decoration?
- Have effects been checked over varied content, at partial sheet height, with reduced transparency/motion, and on target hardware?

### Evidence gate

Record four separate kinds of evidence:

1. **Source evidence:** the current Apple documentation and HIG page used for the decision.
2. **Compile evidence:** the selected SDK accepts the APIs, modifiers, and availability checks in the target project.
3. **Behavior evidence:** simulator/previews cover states, navigation, focus, and localization fixtures.
4. **Device evidence:** a physical target verifies touch, keyboard, materials, motion, performance, permission prompts, and hardware/service behavior.

Do not turn a design review, preview screenshot, or simulator run into a claim that a feature is device-ready or release-ready.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/SwiftUI/Applying-Liquid-Glass-to-custom-views)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Navigation](https://developer.apple.com/documentation/swiftui/navigation)
- [NavigationSplitView](https://developer.apple.com/documentation/swiftui/navigationsplitview)
- [Picking container views for your content](https://developer.apple.com/documentation/swiftui/picking-container-views-for-your-content)
- [Adding a search interface to your app](https://developer.apple.com/documentation/swiftui/adding-a-search-interface-to-your-app)
- [Managing search interface activation](https://developer.apple.com/documentation/swiftui/managing-search-interface-activation)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Animations](https://developer.apple.com/documentation/swiftui/animations)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [dynamicTypeSize](https://developer.apple.com/documentation/swiftui/environmentvalues/dynamictypesize)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [App Intents](https://developer.apple.com/documentation/appintents)
