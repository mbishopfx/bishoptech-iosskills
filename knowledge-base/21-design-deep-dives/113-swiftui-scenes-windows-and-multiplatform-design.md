# SwiftUI scenes, windows, and multiplatform design

## Design premise

A native Apple surface is not only a view hierarchy. It is a task placed inside
a system-managed scene, window, input environment, and platform convention.

Use this design loop:

~~~text
task boundary
    -> primary or auxiliary window decision
    -> scene and domain identity
    -> available-space composition
    -> input and accessibility
    -> material and motion
    -> restoration and external delivery
    -> target/device proof
~~~

The goal is an original product that feels at home on Apple platforms. Do not
copy Apple's private window chrome, branded layouts, or app-specific screens.

## 1. Primary versus auxiliary work

A primary window holds navigation and the main content of an app. An auxiliary
window holds a focused task or context that benefits from remaining visible
alongside the primary work.

| Question | Keep it in the primary surface | Consider an auxiliary window |
| --- | --- | --- |
| Does the task require app-wide navigation? | Yes | Usually no |
| Does the person compare it with the current workspace? | Sometimes | Often |
| Is the task a one-step utility or editor? | Maybe | Often |
| Would opening it for every tap create clutter? | Prefer inline | Avoid a new window |
| Does it have a clear title, close path, and independent state? | Optional | Required |
| Does it preserve context or enable parallel work? | If not, inline | If yes, window may help |
| Is the value only decorative? | Keep inline | Do not create a window |

Opening a new window should preserve context, not announce visual complexity.
Make the choice available when useful through a native command or context
action and let the person control the window.

## 2. Window identity is visible product architecture

Design the identity contract before drawing the surface:

- the window kind: primary, compose, inspector, connection, document, or
  focused AI review;
- the stable presentation value, normally a lightweight record ID;
- the current domain record and revision;
- the scene-scoped draft, selection, and focus state;
- the external request that opened it;
- the close, cancel, commit, and restore outcomes.

A window title and accessibility label should describe the user task. Do not
expose internal terms such as scene session, model revision, or candidate ID
unless they are meaningful to the person.

If a project has two windows open, the same project ID can be shown in both
while the draft state and review state differ. The design must make the
difference understandable.

## 3. Open a new window for a reason

Good reasons include:

- composing while retaining the source message or document;
- comparing two records;
- inspecting a connection or export result;
- reviewing a generated suggestion beside its source;
- continuing a focused task while a primary workspace remains available.

Avoid:

- opening a window for a toast, tooltip, confirmation, or single button;
- opening a separate window solely to display Liquid Glass;
- forcing a new window when a sheet, split view, or inline state is clearer;
- opening multiple model sessions because view construction repeated.

Use a concise title, system window controls, and a clear dismiss path. Let the
person understand what remains open behind the task.

## 4. Window sizes are design inputs

A surface should have a meaningful composition at the smallest width it claims,
not merely a clipped desktop layout.

At every supported target, define:

| Window condition | Design response |
| --- | --- |
| Narrow iPhone width | One-column hierarchy, primary action reachable, no hidden essential state |
| Wide iPhone landscape | Preserve reading order; use additional space only when it improves scanability |
| iPad compact | Keep task controls visible and avoid a forced desktop sidebar |
| iPad regular | Use split view, inspector, or comparison only when the task benefits |
| Resized iPad/Stage Manager | Re-measure and preserve draft/focus/selection; do not jump unpredictably |
| Catalyst narrow | Keep Mac commands and selection usable at small widths |
| Catalyst wide | Use table/sidebar/inspector space intentionally |
| visionOS window | Respect spatial legibility, scale, depth, and indirect input |
| watchOS | Reduce to one glanceable task and the shortest meaningful action |

Use environment values, container-relative sizing, ViewThatFits, AnyLayout, and
custom Layout where appropriate. Device model names are not a layout strategy.

## 5. Platform visual language

Share task meaning and semantic tokens; allow the shell to follow the target.

| Target | Visual direction | Composition warning |
| --- | --- | --- |
| iPhone | Focused navigation, clear hierarchy, touch-sized controls, restrained glass | Do not stack translucent cards until content becomes noisy |
| iPadOS | Workspace, split content, inspectors, multitasking-aware margins | Do not preserve a phone-width column when the task needs comparison |
| Mac Catalyst | Resizable Mac window, menu/toolbar, pointer, keyboard, selection | Do not frame the experience like a floating iPhone capsule |
| visionOS | System window/volume/space, depth, comfort, indirect input | Do not recreate system window chrome or treat flat glass as spatial design |
| watchOS | Glance, crown/touch, concise status, system controls | Do not port a large window hierarchy or a long AI review flow |

Use semantic styles and system controls first. If custom Liquid Glass is
appropriate, apply it to a bounded content group and preserve the system's
window, toolbar, tab, menu, and accessibility behavior.

## 6. Liquid Glass and the scene shell

Treat the window shell and the content surface as different layers:

1. system chooses the window boundary and platform chrome;
2. the feature chooses content hierarchy and controls;
3. a bounded glass effect may group related content;
4. actions remain native and discoverable;
5. reduced transparency, increased contrast, and Dynamic Type remain legible.

A glass effect should clarify grouping or motion, not obscure the source or
make every element appear interactive. On visionOS, the system window already
communicates depth and material; use the documented target scene style instead
of adding a fake frame.

For a focused AI review window, show:

- source title and source revision;
- model availability or fallback state;
- candidate status;
- review actions;
- commit state;
- close/cancel behavior.

Do not show a blank glass shell while model work is running without an
understandable status and a way to return to the source.

## 7. External-event arrival design

An external URL or activity should arrive as a recognizable task:

- show where the person landed;
- confirm the relevant record or source;
- handle authentication or stale state before showing an edit action;
- preserve an existing scene when it is the right destination;
- create a new scene only when the task benefits from a new context;
- make unsupported, malformed, or unauthorized requests recoverable.

Use the same destination for deep links, Handoff, widgets, App Intents, and
notifications when they represent the same user task. The entry mechanism may
differ; the feature contract should not.

A system event is not a permission shortcut. Visual Intelligence, Siri,
Shortcuts, or a URL can request a record; the app still owns authorization,
freshness, and commit validation.

## 8. Restoration and unsaved work

Restoration should feel like continuity, not a surprising mutation.

Design rules:

- restore a lightweight selection or route only after validating it;
- restore a draft with a visible draft state and an explicit conflict policy;
- distinguish saved domain truth from scene-local edits;
- protect unsaved work on close, scene loss, and account change;
- make model-generated text a reviewable draft until committed;
- keep secrets and large contexts out of scene-scoped storage;
- tell the person when a source, permission, or model is no longer available.

For multiple windows, test closing one window while another remains active.
A scene-phase change in one window must not make another window appear
unavailable or silently discard its state.

## 9. AI task-window design

An AI window is a review surface, not a magic portal.

Use a visible state model:

~~~text
unavailable -> ready to start -> generating -> partial/reviewable
    -> validated candidate -> explicit commit -> domain truth
    -> failed/refused/stale -> retry or manual route
~~~

Show why the candidate exists:

- source record and revision;
- model/capability state;
- whether the result is partial or complete;
- what has been validated;
- which action is safe to commit;
- how to discard or retry.

If the person opens two AI review windows, each needs a clear source/revision
identity. Keep generation task ownership outside the view and cancel when the
task no longer has a valid scene owner.

## 10. Accessibility and input

Test the window as a task, not as a screenshot.

- Name primary and auxiliary surfaces in user language.
- Ensure VoiceOver can discover the title, source, status, and action order.
- Move accessibility focus deliberately when a new task window opens.
- Keep keyboard commands discoverable on iPad and Catalyst.
- Give pointer hover a supporting role; touch and keyboard must still work.
- Test Full Keyboard Access, Voice Control, Switch Control, and reduced effects
  when supported.
- Make Dynamic Type and long localized strings work at narrow window sizes.
- Avoid relying on window chrome, hover, translucency, or spatial depth to
  convey the only meaning.

On watchOS, the same semantic task may need a separate control layout and
shorter wording. On visionOS, test indirect focus and comfort in the actual
spatial route.

## 11. Design review checklist

Before calling the composition native-ready, answer:

- What user task justifies each window?
- Which identity is scene-local and which is domain truth?
- Can the feature resize without losing draft, focus, or selection?
- What happens when an external event arrives cold, warm, or duplicated?
- Does a typed window value remain lightweight and safe to resolve?
- Does the target support multiple windows, and what is the fallback?
- Does Catalyst have real Mac menu, toolbar, pointer, and keyboard behavior?
- Does visionOS use a documented window/volume/space route?
- Does watchOS retain a shallow, glanceable task?
- Does Liquid Glass clarify grouping without replacing system chrome?
- Does on-device AI expose unavailable, partial, stale, and uncommitted states?
- Can VoiceOver, keyboard, pointer, and Dynamic Type complete the task?
- What physical, system, signed, and release evidence exists?

## Sources

- [Windows HIG](https://developer.apple.com/design/human-interface-guidelines/windows)
- [Multitasking HIG](https://developer.apple.com/design/human-interface-guidelines/multitasking)
- [Layout HIG](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Mac Catalyst HIG](https://developer.apple.com/design/human-interface-guidelines/mac-catalyst)
- [Scenes](https://developer.apple.com/documentation/swiftui/scenes)
- [Windows](https://developer.apple.com/documentation/swiftui/windows)
- [WindowGroup](https://developer.apple.com/documentation/swiftui/windowgroup)
- [openWindow](https://developer.apple.com/documentation/swiftui/environmentvalues/openwindow)
- [System events](https://developer.apple.com/documentation/swiftui/system-events)
- [ScenePhase](https://developer.apple.com/documentation/swiftui/scenephase)
- [SceneStorage](https://developer.apple.com/documentation/swiftui/scenestorage)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
