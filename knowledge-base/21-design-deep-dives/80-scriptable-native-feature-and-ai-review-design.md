# Scriptable native features and AI review design

Scriptability should feel like a deliberate product capability, not a hidden
escape hatch. The person should know what will run, which data it can read,
what it can return, and whether anything will happen outside the preview.

Use this hierarchy:

~~~text
goal and source/revision
  -> requested capabilities
  -> parse/evaluate state
  -> typed output preview
  -> dry run or fixture result
  -> review and approval
  -> deterministic native commit
~~~

JavaScriptCore belongs behind this shell. A `JSContext` is not the interface;
it is an implementation detail of a controlled script runner.

## Decide whether scripting belongs in the feature

| User outcome | Prefer | Add JavaScriptCore only when |
| --- | --- | --- |
| Toggle a known app action | SwiftUI/App Intent/native command | Users truly author reusable rules and the DSL is insufficient |
| Transform a bounded record | Swift/typed transformation | Existing scripts or user-authored formulas are a product requirement |
| Web page interaction | WebKit and a web bridge | Never use JavaScriptCore as a replacement for page/web-process behavior |
| AI suggestion | Typed proposal/JSON/DSL | A reviewed, sandboxed script is itself the intended output |
| Developer/debug automation | Development-only tooling | The capability is kept out of the customer-facing release path |

The more powerful the scripting route, the more important the visible contract.
Do not add code evaluation to make a prototype feel flexible when a typed
command would be easier to explain, test, localize, and secure.

## Trust is a visible state

Show the relationship between the script and the app:

| State | Useful copy | Design requirement |
| --- | --- | --- |
| Draft | Draft rule | Clearly editable; no execution yet |
| Parsed | Ready to preview | Syntax success is not permission or correctness |
| Requested | Wants access to selected records | List capability names and scope |
| Dry run | Preview only | Make it obvious that no native side effect occurred |
| Waiting for review | Review changes | Show input revision and output values |
| Accepted | Ready to apply | Deterministic native commit still validates current state |
| Failed | Couldn’t run | Preserve a safe error and an edit/retry path |
| Stale | Source changed | Require re-run; do not apply to a newer revision |
| Cancelled | Run cancelled | Do not imply partial success |

Avoid a green checkmark for “script returned a value.” Use explicit language
such as “Preview generated” or “Changes ready for review.”

## The native screen layout

A good iPhone/iPad route can use a standard navigation stack, editor, sheet, or
inspector:

1. title and rule identity;
2. source/revision and last-run state;
3. editor or readable generated proposal;
4. capability list with plain-language scope;
5. output preview with before/after values;
6. dry-run/fixture action;
7. Review, Edit, Accept, Dismiss, and Retry controls.

Keep the script text and result in ordinary SwiftUI content so Dynamic Type,
VoiceOver, selection, copy, keyboard input, and localization work. If the
script is not meant to be edited, show a readable summary or structured rule
instead of presenting a code wall.

## Liquid Glass as functional review chrome

Liquid Glass can group actions that operate on the current proposal:

- Run fixture;
- Review changes;
- Accept;
- Edit;
- Dismiss;
- Retry.

Keep the capability list, output values, exception text, and source/revision
outside the glass group or ensure they remain legible when the material is
reduced/disabled. A glass group should not suggest that code is trusted merely
because it has a polished appearance.

Use native controls and consistent placement. Do not put Accept next to a
destructive action without hierarchy, and do not make the only review action a
gesture over a rendered output.

## AI-generated scripts need stronger review

The safer default is for a local model to produce a typed proposal:

~~~text
user intent + approved local context
  -> closed-set command / DSL / JSON proposal
  -> schema and capability validation
  -> optional JavaScriptCore dry run
  -> visible output and source revision
  -> person review
  -> native commit
~~~

If JavaScript is the product output, show:

- the generated source or a structured explanation;
- the exact data scope and exposed functions;
- a preview of returned values;
- the model route/version and source revision when policy requires it;
- invalid, stale, unavailable, and no-AI fallback states;
- what Accept will and will not mutate.

Do not hide generated code behind a vague “AI completed it” message. Never
evaluate model output as an implicit authorization to access private data,
send a message, make a purchase, delete records, or call a system service.

## Data scope and privacy language

Use capability names a person can understand:

| Internal bridge | Customer-facing scope |
| --- | --- |
| Read-only dictionary snapshot | “Read the selected note” |
| Closed-set formatter | “Format the text you selected” |
| Opaque identifier lookup | “Use the selected item’s title and date” |
| Native side-effect proposal | “Prepare a change for your review” |
| Remote/web route | “Open this web content” or “Send using…” |

Do not expose internal object names, raw database contexts, tokens, or
unbounded collections. If the feature uses health, contact, financial, media,
location, or account data, inherit that framework’s authorization and privacy
states in the script UI. A local JavaScript context does not make protected
data safe to disclose.

## WebKit is a different design

If the feature displays or communicates with a web page, make the web boundary
visible: origin, navigation, content process, script-message policy, cookie/
storage policy, and external handoff. A local JavaScript rule editor should not
look like a browser and a `WKWebView` should not be treated like an app-owned
`JSContext`.

Avoid a hidden bridge that accepts arbitrary page messages and forwards them to
native methods. Use origin checks, typed messages, user-mediated actions, and
the narrowest exposed capabilities.

## Accessibility and alternate input

Script review must be possible without understanding JavaScript syntax:

- VoiceOver reads the source/revision, capability scope, output, error, and
  action labels in a meaningful order;
- Dynamic Type keeps long error and output text readable;
- code/editor content supports selection, copy, keyboard, and pointer where
  appropriate;
- syntax color is not the only way to distinguish an error or proposal;
- the same review actions are available as semantic buttons and accessibility
  actions;
- reduced motion/transparency and increased contrast preserve state boundaries;
- localization and right-to-left layouts do not hide the capability list or
  Accept/Dismiss controls;
- a generated rule can be summarized in plain language.

For complex code, provide a structured rule editor or a read-only summary. A
feature is not accessible merely because the editor has an accessibility tree.

## Performance and cancellation UX

Make evaluation state observable. A synchronous script run can block its
executor; a model proposal can be cancelled; a native side effect can be
pending separately. Show those as different states.

Set budgets for source length, input size, output size, nesting, and repeated
runs. If a script exceeds a budget or the app abandons its runner, say “Run
cancelled” or “This rule is too large,” not “Done.” Measure the actual target if
script output drives media, rendering, sensor processing, or a scrolling screen.

## Design review checklist

- Scripting is necessary for the user outcome and is not replacing a simpler
  typed native command.
- JavaScriptCore is separated from WebKit and from the domain model.
- The screen names source/revision, exposed capabilities, output, and side
  effect boundaries.
- Parse, evaluate, dry-run, review, commit, failure, stale, and cancellation
  states are distinct.
- AI-generated code is treated as a proposal and has a no-AI/manual route.
- Liquid Glass groups functional review actions and is not the only contrast or
  status surface.
- Errors and output are readable with VoiceOver, Dynamic Type, localization,
  reduced effects, keyboard, pointer, and alternate input.
- Source/data scope is redacted and deletion/retention behavior is deliberate.
- Target-specific performance, memory, release, and web/native proof are
  planned before the feature is called ready.

## Related routes

- [JavaScriptCore embedded scripting and native capability boundaries](../42-framework-deep-dives/60-javascriptcore-embedded-scripting.md)
- [JavaScriptCore scripting capability route](../50-capability-recipes/83-javascriptcore-scripting-capability-route.md)
- [JavaScriptCore scripting proof matrix](../60-verification/77-javascriptcore-scripting-proof-matrix.md)
- [JavaScriptCore scripting recipes](../70-code-recipes/95-javascriptcore-scripting-recipes.md)
- [WebKit, Safari Services, and web-auth capability route](../50-capability-recipes/52-webkit-safariservices-web-auth-route.md)
- [Web content, native shell, and verified handoff design](../21-design-deep-dives/49-web-content-and-native-shell-design.md)

## Sources

- [JavaScriptCore](https://developer.apple.com/documentation/javascriptcore)
- [JSContext](https://developer.apple.com/documentation/javascriptcore/jscontext)
- [JSVirtualMachine](https://developer.apple.com/documentation/javascriptcore/jsvirtualmachine)
- [JSValue](https://developer.apple.com/documentation/javascriptcore/jsvalue)
- [JSManagedValue](https://developer.apple.com/documentation/javascriptcore/jsmanagedvalue)
- [JSExport](https://developer.apple.com/documentation/javascriptcore/jsexport)
- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
