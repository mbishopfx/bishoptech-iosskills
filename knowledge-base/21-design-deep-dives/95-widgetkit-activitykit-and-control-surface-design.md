# WidgetKit, ActivityKit, and control surface design

## Design objective

Design system surfaces as a compact continuation of the product, not as a
shrunken app screen. The user should understand:

- what is happening;
- whether the information is current;
- what action is safe;
- what will happen next;
- how to return to the relevant app route;
- what is hidden when the device or surface is private/locked.

Apple's system spaces supply the outer framing, placement, tinting, and many
interaction affordances. The app supplies a small, original visual language
through type hierarchy, symbol choice, color roles, copy, and domain-specific
status. Apple-native polish comes from respecting the system contract.

## Choose the right surface

| Product need | Best surface | Design test |
| --- | --- | --- |
| Read one small current fact | Widget | It remains useful after a delayed refresh |
| Show predictable future states | Timeline widget | Every entry has a truthful date and state |
| Perform one safe quick action | ControlWidgetButton | The action is idempotent and has a clear result |
| Expose an on/off state | ControlWidgetToggle | The visible value is current enough to act on |
| Track an event for minutes or hours | Live Activity | The state has a clear start, progress, stale, and end |
| Return to detail | widgetURL, Link, or activity deep link | The app can reconstruct the route from cold launch |
| Help the system find content | App Intents/Spotlight | Search and entity resolution are deterministic |
| Propose an AI result | App screen review first | System surface receives only validated projection |

Do not make a Live Activity for a static preference, a widget for a transaction
that needs several confirmation steps, or a control for a multi-item editor.

## System-owned treatment and Liquid Glass

The system may render widgets in fullColor, accented, or vibrant modes and may
remove their background. Controls and Live Activities also receive system-defined
treatment in their host spaces. The app should not assume that a custom material,
blur, shadow, or glass outline will survive those transformations.

Use these composition rules:

1. use semantic system controls and labels;
2. group a widget's background with containerBackground(for: .widget);
3. keep primary information readable when color becomes monochrome;
4. use widgetAccentable only for the content that should be emphasized;
5. reserve full-color imagery for content whose identity depends on color;
6. let the system own the outer glass/material surface;
7. use custom Glass or glassEffect inside an app-owned screen where it clarifies
   hierarchy, not as a decorative layer on every system surface;
8. avoid nested translucent panels that compete with the system host.

The design target is not an Apple screenshot replica. It is an original product
that uses the platform's type, spacing, symbols, semantic controls, motion
limits, and adaptive materials coherently.

## State hierarchy for glanceable surfaces

Every surface should have a small state contract. Avoid using a spinner as the
only signal because a widget or Live Activity may not be actively running.

| State | User-facing meaning | Widget treatment | Live Activity/control treatment |
| --- | --- | --- | --- |
| Preparing | Work has started but no result is ready | Short phase plus stable placeholder | Start only if the event is meaningful |
| Ready/active | Current state is usable | Key value, timestamp or freshness cue | Current progress and next event |
| Updating | A change is being committed | Keep last truthful value; mark updating | Use action/progress feedback |
| Stale | The last update is outside the freshness window | Show last-known state and “Updated…” | Show stale label or end if no longer useful |
| Offline | Local state is available but remote state is not | Local value plus offline cue | Do not imply server confirmation |
| Denied/locked | Content or action is unavailable | Redact; offer a safe app handoff | Require authentication or show safe status |
| Error | The intended route failed | Short repair action/deep link | Actionable error or end |
| Ended | Activity is complete | Final record or no longer relevant | Completion summary, not a live timer |
| Empty | No records or event | Empty-state action | Do not create a meaningless activity |

The projection schema should include freshness and source metadata even if the
surface displays only a short phrase. That allows the app to decide whether a
cached value is still honest.

## Widget composition by family

Begin with the smallest useful content model and adapt the layout to each family.
Do not simply scale a large widget down.

- Small: one dominant value or status, one symbol, one clear tap route.
- Medium: primary value plus one supporting dimension or compact action.
- Large: a short list or timeline with clear scan order, not a full dashboard.
- Accessory: high contrast, minimal text, context-aware background, and no
  dependency on a large color field.
- StandBy/CarPlay/other contexts: verify background removal, input capability,
  contrast, and interaction behavior for that host.

Use a family switch or layout abstraction that keeps domain content shared while
allowing spacing, labels, and emphasis to adapt. A long title that fits in
systemMedium may need a semantic short title in systemSmall. Do not rely on
truncation to preserve meaning.

For a configurable widget, design the edit flow around one bounded choice or
entity. Use stable identifiers; do not serialize the entire object into the
configuration. The provider can resolve the current projection when WidgetKit
requests a timeline.

## Background, tint, and imagery

A widget background is a removable container, not a guarantee of a full-bleed
panel. Put decorative background content in the declared container and ensure
the foreground remains legible without it.

Use a rendering policy for imagery:

| Content | Preferred mode | Reason |
| --- | --- | --- |
| Symbol that communicates state | accented or desaturated | Survives system tint and preserves hierarchy |
| Photo/album/book artwork | fullColor where supported | Color is part of the content identity |
| Decorative gradient | Only if the layout remains legible without it | System may remove/tint it |
| Sensitive face/location/health image | Redacted or omitted in private contexts | Avoid a privacy leak |
| AI-generated image | Explicitly labeled and policy-reviewed | Do not imply source truth |

Test long/short strings, right-to-left text, large Dynamic Type, increased
contrast, reduced transparency, and color settings. A screenshot in one rendering
mode is not a complete design review.

## Live Activity composition

A Live Activity is a compact event narrative:

    what is happening -> current state -> next meaningful change -> completion

Put stable identity in the attributes and changing progress/status in the
ContentState. Use short labels and a clear time/progress relationship. Avoid
putting the full app workflow into the Live Activity.

### Start

Start only when the event is meaningful enough to occupy prominent system space.
The starting copy should answer what the person is following and why. If the
event may finish immediately, a local in-app status or notification may be more
appropriate.

### Active updates

Update only meaningful state changes. Keep progress monotonic when the domain is
monotonic; if the source can regress, explain the state instead of animating a
false countdown. Use a server event ID or domain revision to dedupe updates.

### Stale

A stale date is a trust signal. When content passes its freshness window:

- show that the state may be out of date;
- stop implying live progress;
- offer a route to refresh or open the app;
- end the activity if no useful recovery exists.

Do not extend staleDate forever just to keep a surface visible.

### End

End when the domain operation is complete, canceled, invalidated, or no longer
authorized. Choose dismissal timing that lets the person understand completion
without leaving a misleading live card. An ended activity must not continue to
show a live timer or “in progress” language.

### Interaction and handoff

Buttons and toggles should perform only bounded, reversible or clearly
understood actions. A tap that opens the app should land on the activity's current
detail route, even after cold launch. A Live Activity action must re-read current
state before committing because the displayed state may be stale.

## Control design

A control must be legible across the host's available sizes and contexts.

- Use a button for an action without a durable on/off state.
- Use a toggle for a state that a person can inspect and set.
- Keep the label short enough for Control Center and Lock Screen variants.
- Use an SF Symbol whose meaning does not depend on color alone.
- Provide a value label or status only when it improves understanding.
- Make a configurable control's choice narrow and stable.
- Require authentication for sensitive effects.
- Return a localized, actionable error instead of silently failing.

Design the action to be idempotent. If the person taps twice, if the extension is
restarted, or if a push and local action race, the domain service should converge
to one truthful state.

Examples of good control boundaries:

- start/stop a local focus timer;
- turn a private capture mode on/off;
- mark the current local item complete;
- open a camera capture route;
- set a selected local device mode.

Examples that need an app-owned flow instead:

- delete a shared collection;
- publish an AI-generated message;
- spend money or accept a subscription;
- reveal health, location, or contact data on a locked device;
- choose among many records with material consequences.

## AI-to-surface design

AI should improve the product's preparation or interpretation without becoming
an unreviewed system command.

Use three layers:

1. Proposal: Foundation Models, Core ML, Vision, Speech, or another local model
   produces a typed candidate with source IDs and confidence/uncertainty.
2. Review/commit: the main app validates freshness, authorization, user intent,
   and side-effect policy; the person confirms when appropriate.
3. Projection: a compact widget, control value, or Live Activity displays the
   committed state and its freshness.

For read-only summaries, the projection can show the result with an “AI summary”
or source indicator when that helps trust. For actions, the system surface should
call a deterministic App Intent that revalidates and commits; it should not
replay a stale model instruction.

If on-device AI is unavailable, the surface should still be useful:

- show source data without the interpretation;
- show “Model unavailable” only when that is the honest reason;
- offer a deterministic fallback;
- avoid fabricating confidence or implying that a device ran the model.

## Accessibility and adaptability

System surfaces are small, but the accessibility contract is not.

Verify:

- labels, values, traits, hints, and grouped reading order;
- VoiceOver for every widget family and control action;
- Voice Control names and disambiguation;
- Switch Control traversal;
- Dynamic Type and large content sizes;
- increased contrast and color differentiation;
- reduced transparency and background removal;
- Reduce Motion for update animations;
- keyboard, pointer, or controller paths where the host supports them;
- localization, pluralization, dates, units, and right-to-left layout;
- no essential state conveyed only through color or motion.

A visual “status dot” must have a semantic label. A control's short title must
still explain its action when the symbol is hidden or tinted. Generated summaries
need a bounded, localizable accessibility representation.

## Trust, privacy, and instrumentation

Log state transitions, not private content. A useful event record is:

- surface kind and stable version;
- projection revision;
- state category;
- source revision or event ID;
- action outcome;
- stale/denied/error reason category;
- device/OS/build and accessibility test mode.

Do not log full AI prompts, private titles, health values, exact locations,
message content, or push tokens. Redact screenshots and use synthetic fixtures
for proof artifacts.

## Review checklist

Before calling a system-surface design ready:

- Can the product explain why this belongs in a widget, control, or Live Activity?
- Does the smallest supported size preserve the primary meaning?
- Does the UI remain truthful when refreshes are delayed?
- Does the system own the outer material/tint treatment?
- Does locked-device behavior protect private content?
- Does every action revalidate current state?
- Does AI output pass through a proposal and commit boundary?
- Is there a fallback when the model, network, permission, or server is unavailable?
- Are stale, ended, denied, and error states designed rather than omitted?
- Has the real surface been tested on a signed physical device?

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date/)
- [Displaying the right widget background](https://developer.apple.com/documentation/widgetkit/displaying-the-right-widget-background)
- [Optimizing your widget for accented rendering mode and Liquid Glass](https://developer.apple.com/documentation/widgetkit/optimizing-your-widget-for-accented-rendering-mode-and-liquid-glass)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Creating controls to perform actions across the system](https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system)
- [Adding refinements and configuration to controls](https://developer.apple.com/documentation/widgetkit/adding-refinements-and-configuration-to-controls)
- [ControlWidget](https://developer.apple.com/documentation/swiftui/controlwidget)
- [ControlWidgetButton](https://developer.apple.com/documentation/widgetkit/controlwidgetbutton)
- [ControlWidgetToggle](https://developer.apple.com/documentation/widgetkit/controlwidgettoggle)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [ActivityContent](https://developer.apple.com/documentation/activitykit/activitycontent)
- [Liquid Glass adoption](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/accessibility/)
