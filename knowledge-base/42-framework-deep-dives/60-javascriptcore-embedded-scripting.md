# JavaScriptCore embedded scripting and native capability boundaries

JavaScriptCore lets an app evaluate JavaScript from Swift, Objective-C, or C
and optionally expose selected native objects, methods, and values to that
JavaScript environment. It is an embedded scripting engine, not a web browser
and not a permission system.

Use this route only when the product genuinely benefits from local scripting,
an embedded rules language, a migration bridge, or a bounded transformation.
For web content, DOM, navigation, JavaScript running in a page, or browser
policy, use WebKit and its process/origin model instead. For app automation,
prefer a typed native command or App Intent when a script engine is not part of
the user outcome.

The safe architecture is:

~~~text
typed app state / user-approved script
  -> dedicated JavaScriptCore context and capability registry
  -> bounded input conversion
  -> evaluation with exception capture
  -> typed output validation
  -> review or deterministic domain commit
~~~

## The JavaScriptCore object graph

| Type | Responsibility | Boundary |
| --- | --- | --- |
| `JSVirtualMachine` | Self-contained execution resources; can own multiple contexts | Values cannot cross to a different virtual machine; concurrent work on one machine waits |
| `JSContext` | JavaScript execution environment, global object, exception state, source name, inspector flag | Context state and values belong to one execution environment |
| `JSValue` | Native/JavaScript value conversion, property access, function invocation, object wrappers | A value is tied to its context and virtual machine; do not treat it as a Sendable value |
| `JSManagedValue` | Conditional retention for a JavaScript value held by a native object | Requires an explicit native ownership relationship through the virtual machine |
| `JSExport` | Selective Objective-C/Swift protocol surface exposed to JavaScript | Only deliberately exported methods/properties are available; the protocol is not an authorization policy |
| C JavaScriptCore API | Lower-level context/value/object/string operations | Manual memory/error/protection rules increase risk; use only where the object API is insufficient |

Keep one explicit owner for a context. A Swift actor or a dedicated serial
executor can own the app’s scripting session, but do not move `JSValue` objects
between actors merely because the compiler accepts an `Any` container. Convert
to immutable Swift values at the boundary.

## `JSVirtualMachine` and concurrency

Contexts created without an argument belong to a new virtual machine. Contexts
created with `init(virtualMachine:)` share the supplied machine and can exchange
values only within that machine. A value from one virtual machine cannot be
passed to a context in another virtual machine; JavaScriptCore raises an
Objective-C exception for that misuse.

Apple documents the JavaScriptCore API as thread-safe, but other threads using
the same virtual machine wait. Use a separate virtual machine per independent
concurrent evaluation when the target and resource budget justify it. In an
app, a simpler and safer default is:

- one script-runner owner per feature;
- one context or one small context pool per trust boundary;
- immutable JSON-like input and output values across the actor boundary;
- no retained `JSValue` in a Swift model, view, or persistence object;
- teardown that drops the context and cancels app-owned work when the feature
  leaves the screen.

JavaScript execution itself is synchronous when `evaluateScript` is called.
Do not run unbounded or user-controlled code on the main actor. If the product
needs a hard execution budget, design an isolated runner/process-like boundary
that the app can abandon and test; do not imply that JavaScriptCore automatically
interrupts a running evaluation.

## `JSContext` evaluation and exceptions

`JSContext` provides `evaluateScript` overloads, a global object, a descriptive
name, an optional source URL, an exception property, and an exception handler.
Use a source URL or stable script identifier so diagnostics can identify which
script failed without logging private source text.

Treat these as separate outcomes:

| Outcome | Product state |
| --- | --- |
| Script parsed and returned a value | Candidate output; still needs schema validation |
| JavaScript exception captured | Failed; preserve a safe error and offer edit/retry |
| Native callback set `context.exception` | Native bridge rejected the call; do not commit |
| Evaluation returned `undefined`/`null` | Valid only if the output schema explicitly allows it |
| Evaluation timed out at the app layer | Cancelled/abandoned; never treat partial side effects as success |

The default exception behavior stores the thrown exception in `context.exception`.
Setting the handler to `nil` consumes uncaught exceptions silently, which is
usually the wrong behavior for a user-facing feature. Install a handler that
records a redacted diagnostic and maps the result to a visible, recoverable
state.

Never use `try?` around evaluation and then proceed with a stale output. Clear
the previous output before a new run and tie the result to the input revision.

## `JSValue` conversion and output schemas

JavaScriptCore converts common native values such as strings, numbers,
booleans, arrays, and dictionaries. Blocks can become JavaScript functions.
Native object wrappers expose no methods or properties by default; an explicit
`JSExport` protocol or a deliberately installed block is needed.

Use a narrow, JSON-like contract:

~~~text
Swift input value
  -> dictionary/array/string/number/bool/null
  -> JavaScript function or script
  -> dictionary/array/string/number/bool/null
  -> Swift Decodable or explicit validator
~~~

Do not rely on a generic `toDictionary()` result as proof of the schema. Check
required keys, types, bounds, enum values, string lengths, nested depth, and
source revision. Reject functions, wrapped native objects, unexpected keys,
non-finite numbers, and values that cannot be represented in the product model.

BigInt and numeric conversion need an explicit policy. Do not let JavaScript
number coercion silently turn a large identifier, currency amount, timestamp,
or security value into an imprecise number.

## Expose capabilities, not an object graph

`JSExport` can expose selected properties and methods from an Objective-C or
Swift object. A block installed on a context can expose a single function. Both
routes are capability bridges and must be deliberately designed.

Prefer a small façade:

| Expose | Avoid exposing |
| --- | --- |
| Pure formatting, closed-set calculation, bounded lookup by opaque ID | A database context, file manager, URL session, or arbitrary object graph |
| User-approved draft transformation | Keychain, tokens, credentials, contacts, health data, or raw private records |
| Deterministic command that returns a proposal | Methods that send, purchase, delete, call, or mutate without review |
| Read-only metadata with redaction | Internal object references or callbacks that retain the whole app |

The JavaScript layer should return a typed proposal. The native owner validates
the proposal, checks current authorization and revision, asks for confirmation
when needed, and performs the side effect. A script function returning `true`
does not mean the native operation completed.

## Memory ownership and `JSManagedValue`

`JSValue` retains its `JSContext`, and the context retains exported native
objects. Storing a nonmanaged `JSValue` in an exported native object can create a
retain cycle that prevents the context from being deallocated. Use
`JSManagedValue` and tell the `JSVirtualMachine` about the native ownership
relationship with `addManagedReference(_:withOwner:)` and the matching removal.

This matters for:

- exported delegate/host objects;
- callbacks that capture a context or native owner;
- long-lived script sessions;
- view models that outlive a screen;
- multiple contexts sharing a virtual machine.

Dispose of script sessions explicitly. A weak/managed JavaScript value becoming
`nil` is a lifecycle result, not a script failure. Do not retain a context just
to keep a callback alive.

## Inspector and production policy

`JSContext.isInspectable` allows Safari Web Inspector inspection where the
platform and configuration support it. Treat inspectability as a development
diagnostic setting. It is not a security boundary, and it should not be enabled
as a production feature without a deliberate review of what can be inspected.

Keep script source, source URLs, exception values, and native arguments out of
ordinary analytics unless redacted and explicitly needed. A debugging name can
be stable and non-sensitive, such as a feature ID plus script revision.

## JavaScriptCore versus WebKit

| Need | JavaScriptCore | WebKit |
| --- | --- | --- |
| Evaluate a local calculation/rule | Yes, in an app-owned context | Usually unnecessary |
| DOM, CSS, browser navigation, page JavaScript | No DOM/page model | `WKWebView` and web process/origin boundaries |
| Expose a native object to an embedded script | `JSExport`/blocks | Message handlers and page bridge with origin policy |
| Render a web page | No | Yes |
| Isolate untrusted web content | Not by itself | Use WebKit’s documented process/content configuration and origin policy |
| App Intent/system automation | Prefer typed App Intent/command | Neither framework replaces system intent contracts |

Do not use JavaScriptCore as a hidden WebKit bridge. Do not assume a script
loaded from a web page has the same trust boundary as a bundled rules file.

## On-device AI and script generation

Foundation Models or another local model can suggest a structured rule or a
script, but generated code is untrusted output:

~~~text
user goal and approved data
  -> model proposal: typed rule/DSL first, JavaScript only if required
  -> syntax/size/capability/schema validation
  -> human review with readable preview
  -> dry run against a fixture
  -> deterministic native commit
~~~

Prefer a typed DSL or JSON command for app features. If JavaScript is essential,
run it against a fixture and expose only pure, bounded capabilities. Store the
model route/version, prompt/context policy, source revision, generated text or
rule, validation result, review choice, and final native result separately.

Never evaluate model output merely because it is valid JavaScript. Reject code
that attempts to access unavailable globals, unexpected properties, native
objects, or side-effect bridges. A local model’s output is not an authorization
to send data, change account state, delete records, or contact another person.

## SwiftUI and native review surfaces

The native screen should make scripting visible and reversible:

~~~text
script/rule identity and source
  -> parse/evaluate state
  -> output preview and validation errors
  -> requested capabilities
  -> Review / Edit / Run fixture / Accept / Dismiss
  -> deterministic domain commit or fallback
~~~

Use Liquid Glass for the functional review group when it fits the target’s
native shell. Keep code status, output values, and errors readable outside the
material. Do not hide a high-impact Run or Accept action behind a gesture or
make the generated code look like authored product truth.

## Availability, privacy, and proof

Record the target SDK, deployment target, platform, context/VM ownership,
source/resource membership, inspector configuration, and any permissions
required by the native capabilities exposed to scripts. JavaScriptCore itself
does not grant access to protected user data or system actions; every exposed
capability inherits its own authorization, privacy, and lifecycle contract.

Prove separately:

- API/source and target availability;
- compile and unit tests for conversion/validation/exception paths;
- fixture evaluation and output determinism;
- concurrency/context/virtual-machine ownership;
- memory teardown and managed-value lifecycle;
- script review, rejection, and stale-revision behavior;
- physical-device performance if the script drives UI/media/sensors;
- permissions and system surface for any native side effect;
- signed release configuration and inspector/resource policy.

The [JavaScriptCore capability route](../50-capability-recipes/83-javascriptcore-scripting-capability-route.md)
provides the build worksheet. The [JavaScriptCore proof matrix](../60-verification/77-javascriptcore-scripting-proof-matrix.md)
defines fixtures, and the [JavaScriptCore recipes](../70-code-recipes/95-javascriptcore-scripting-recipes.md)
remain route sketches until compiled in a named target.

## Sources

- [JavaScriptCore](https://developer.apple.com/documentation/javascriptcore)
- [JSContext](https://developer.apple.com/documentation/javascriptcore/jscontext)
- [JSVirtualMachine](https://developer.apple.com/documentation/javascriptcore/jsvirtualmachine)
- [JSValue](https://developer.apple.com/documentation/javascriptcore/jsvalue)
- [JSManagedValue](https://developer.apple.com/documentation/javascriptcore/jsmanagedvalue)
- [JSExport](https://developer.apple.com/documentation/javascriptcore/jsexport)
- [C JavaScriptCore API](https://developer.apple.com/documentation/javascriptcore/c-javascriptcore-api)
- [JSContext exception](https://developer.apple.com/documentation/javascriptcore/jscontext/exception)
- [JSContext exception handler](https://developer.apple.com/documentation/javascriptcore/jscontext/exceptionhandler)
- [JSContext virtual machine](https://developer.apple.com/documentation/javascriptcore/jscontext/virtualmachine)
- [JSValueRef](https://developer.apple.com/documentation/javascriptcore/jsvalueref)
- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
