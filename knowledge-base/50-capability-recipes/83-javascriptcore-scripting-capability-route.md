# JavaScriptCore scripting capability route

Use this route for an app-owned, local scripting capability with an explicit
input/output schema and a deliberately small native bridge. It is not a route
for arbitrary web JavaScript, hidden app automation, or unreviewed model code.

## Route decision

| Outcome | Primary route | Boundary |
| --- | --- | --- |
| User invokes a known app action | SwiftUI command or App Intent | Typed parameters, authorization, undo/cancellation, and system-surface proof |
| User authors a small rule or formula | Typed DSL or JSON first | Add JavaScriptCore only if the rule language genuinely needs it |
| Evaluate local JavaScript with no native effects | JavaScriptCore `JSContext`/`JSValue` | Context ownership, exceptions, output validation, memory, and resource budgets |
| Run page/web content | WebKit `WKWebView` and message/origin policy | Web process, navigation, origin, storage, and external handoff |
| Let AI automate the app | Structured proposal plus native validator | Generated code is untrusted; review and deterministic commit are mandatory |

## Step 1: define the capability manifest

Write the bridge before creating a context:

~~~text
ScriptCapabilityManifest
  script ID and source revision
  input schema and maximum size
  output schema and maximum size
  allowed functions/properties
  data scope and redaction policy
  side effects: none / proposal only / native commit after review
  execution budget and cancellation policy
  model-generation metadata, if applicable
  retention/deletion policy
~~~

Start with no native objects. Add one read-only dictionary or one pure function
at a time. Keep capabilities stable and versioned; do not expose an entire
service object because it is convenient.

## Step 2: select the execution owner

Create a named script-runner owner for each trust and lifecycle boundary:

| Owner | Responsibility |
| --- | --- |
| Feature runner | Owns `JSVirtualMachine`, one or more `JSContext`s, source/revision, and cancellation state |
| Native façade | Converts approved values and exposes only allowlisted functions |
| Validator | Checks output schema, bounds, revision, and allowed commands |
| SwiftUI feature store | Presents parse/evaluate/review/error state and commits accepted values |
| Persistence owner | Stores source, proposal, review decision, and derived result; never live JS values |

Do not store `JSContext`, `JSValue`, or exported native objects in a Core Data/
SwiftData model, global singleton, or `Sendable` domain record. Drop the runner
when the feature or source revision no longer needs it.

## Step 3: configure the target

Record before implementation:

- deployment target and SDK for JavaScriptCore symbols;
- iPhone/iPad/Catalyst or multi-platform target scope;
- source file/resource membership and versioning;
- whether inspector visibility is enabled in development only;
- script source origin and document/network import policy;
- data types allowed across the bridge;
- any permissions required by the native functions exposed to scripts;
- memory, source length, input, output, and execution budgets;
- accessibility, localization, keyboard, pointer, and UI update route.

JavaScriptCore does not grant access to contacts, health, files, keychain,
camera, network, messages, payments, or system actions. A native function that
touches those domains must still implement that framework’s authorization and
privacy contract.

## Step 4: create the context safely

Initialize the context on its owner, set a stable non-sensitive name/source
identifier, install an exception handler, and clear any previous output before
each evaluation. If a context is used for independent concurrent work, create
separate virtual machines rather than passing values between machines.

Keep exceptions structured:

~~~text
run ID / script revision / source identifier
  -> syntax or runtime exception
  -> redacted developer diagnostic
  -> customer-facing error and edit/retry action
~~~

Do not set the exception handler to `nil` just to make a run appear successful.
Do not log raw script source, private arguments, or exception objects without a
redaction policy.

## Step 5: bridge a narrow API

Preferred bridge order:

1. no bridge: evaluate pure code against JSON-like input;
2. a single block with bounded input and output;
3. a small `JSExport` façade with read-only/pure methods;
4. a proposal-returning command that the native layer validates and executes;
5. a side-effect method only after a separate product and privacy review.

For every exposed method, write:

- name and version;
- input and output schema;
- data scope;
- failure/exception behavior;
- whether it is pure, proposal-only, or side-effecting;
- authorization and user-review requirement;
- accessibility and system-surface consequence.

Avoid exposing closures that capture view controllers, persistence contexts,
credentials, or arbitrary service objects. If a native façade needs to retain a
JavaScript callback, use the documented managed-value ownership route and test
teardown.

## Step 6: validate the output

Treat `JSValue` as an untrusted dynamic result:

~~~text
JSValue
  -> allowed primitive/array/dictionary conversion
  -> explicit schema validator
  -> current source/revision and authorization check
  -> typed proposal
  -> review or deterministic pure result
~~~

Reject unexpected object wrappers, functions, missing keys, non-finite numbers,
large or deeply nested values, unknown enum cases, invalid identifiers, stale
source revisions, and output that exceeds the user-visible budget.

If the output represents a domain mutation, validate again immediately before
commit. The script can be rerun, the record can change, or authorization can be
revoked while the review sheet is open.

## Step 7: design AI generation as proposal flow

Use a typed DSL or JSON schema as the first model output. If the product must
generate JavaScript, keep it in a visibly reviewable step:

~~~text
user goal + approved local context
  -> local model availability check
  -> typed rule or JavaScript proposal
  -> syntax + capability + output validation
  -> fixture/dry run
  -> review
  -> native commit
~~~

Persist model route/version, source revision, proposal, validation, review, and
commit separately. When the model is unavailable, offer a manual rule editor,
a no-AI path, or a deterministic built-in command. Do not automatically send
the input to a remote model because evaluation failed locally.

## Step 8: native UI and Liquid Glass

Use a normal SwiftUI screen with a source/revision header, editor or summary,
capability list, output preview, and review controls. A Liquid Glass group can
hold Run fixture, Review, Accept, Edit, Dismiss, and Retry. Keep error text,
capabilities, source, and output outside the only material/contrast boundary.

Make `Run` distinct from `Accept`. Make a native side effect distinct from a
preview. Show a clear state when the source became stale or the permission
changed.

## Step 9: persistence and system handoff

Persist:

- script/rule ID and source revision;
- source or user-authored text according to retention policy;
- declared capability manifest;
- input snapshot identifier, not unbounded raw data;
- typed proposal and validation result;
- review decision and timestamp if needed;
- deterministic derived output/commit ID;
- failure, cancellation, and stale states.

Do not persist live JavaScript values, contexts, virtual machines, callback
closures, or an “executed” flag that implies a native side effect completed.

If a rule is exposed through App Intents, widgets, share sheets, or other
system surfaces, create a bounded typed projection and repeat authorization and
revision checks. A system surface can request a route; it does not make script
output canonical.

## Step 10: evidence packet

The [JavaScriptCore proof matrix](../60-verification/77-javascriptcore-scripting-proof-matrix.md)
should contain:

- current Apple source and target availability review;
- compile/test-plan evidence for conversion, errors, and validators;
- same-VM/different-VM/context ownership tests;
- exception and native-callback failure tests;
- memory/managed-value teardown evidence;
- malicious/oversized/deeply nested script fixtures;
- AI proposal freshness, review, and no-AI fallback fixtures;
- accessibility tasks for script review and error recovery;
- physical-device/performance evidence if scripts drive UI/media/sensors;
- permission/system-surface evidence for exposed native side effects;
- signed release configuration, resources, and inspector policy.

## Stop conditions

Stop before implementation if:

- a script can access a raw service/database/file/token object;
- an AI-generated script is evaluated without capability/schema validation;
- `JSValue` is moved across virtual machines or persisted as domain state;
- exceptions are swallowed and the previous output remains visible;
- synchronous evaluation can block the main actor with unbounded input;
- a “run” result is represented as a completed native side effect;
- WebKit page content is bridged as if it were app-owned JavaScriptCore code;
- inspector/debug configuration is being used as a production trust boundary.

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
- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
