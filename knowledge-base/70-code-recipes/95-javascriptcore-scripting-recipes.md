# JavaScriptCore scripting recipes

These are route sketches for a named iOS target. They are not claimed to
compile in this documentation workspace and do not prove that a script,
permission, native side effect, or release artifact behaves correctly.

## 1. Evaluate a script with explicit exception capture

Keep the context local to the runner and clear any prior result before a new
evaluation.

~~~swift
import Foundation
import JavaScriptCore

struct ScriptEvaluation {
    let output: JSValue?
    let exceptionDescription: String?
}

func evaluate(
    source: String,
    sourceURL: URL,
    contextName: String
) -> ScriptEvaluation {
    guard let context = JSContext() else {
        return ScriptEvaluation(output: nil, exceptionDescription: "No context")
    }

    context.name = contextName
    context.exception = nil
    context.exceptionHandler = { _, exception in
        // Redact source and private argument values before recording this.
        let message = exception?.toString() ?? "JavaScript exception"
        print("Script failed: \(message)")
    }

    let value = context.evaluateScript(source, withSourceURL: sourceURL)
    let message = context.exception?.toString()
    return ScriptEvaluation(output: value, exceptionDescription: message)
}
~~~

The actual route should return a typed result rather than a live JSValue. Keep
the context and value inside the runner and map exceptions to an app-owned
failure state. Recheck the initializer and overload availability against the
selected SDK.

## 2. Install a single pure native function

Use a block when a bounded pure function is enough. The block should accept
value types and return a value type; it should not capture a view controller,
database context, token, or service object.

~~~swift
import JavaScriptCore

func installFormatter(in context: JSContext) {
    let formatter: @convention(block) (String) -> String = { value in
        value.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    context.setObject(formatter, forKeyedSubscript: "normalizeText")
}

func runFormatter(in context: JSContext) -> String? {
    context.exception = nil
    return context.evaluateScript("normalizeText('  draft  ')")?.toString()
}
~~~

Do not construct JavaScript source by interpolating unescaped user strings in a
real route. Pass input through a JSON/value bridge or an explicitly escaped
representation. This sketch is only showing the capability boundary.

## 3. Expose a narrow JSExport façade

JSExport exposes only the methods and properties selected by the protocol. Keep
the façade read-only or proposal-producing.

~~~swift
import Foundation
import JavaScriptCore

@objc protocol ScriptHostExport: JSExport {
    func titleForRecord(_ recordID: String) -> String
}

@objc final class ScriptHost: NSObject, ScriptHostExport {
    private let titles: [String: String]

    init(titles: [String: String]) {
        self.titles = titles
    }

    func titleForRecord(_ recordID: String) -> String {
        titles[recordID] ?? ""
    }
}

func installHost(in context: JSContext, titles: [String: String]) {
    let host = ScriptHost(titles: titles)
    context.setObject(host, forKeyedSubscript: "app")
}
~~~

The façade’s dictionary is already a data projection. In a production route,
limit record IDs, redact values, version the method name, and record the data
scope in the capability manifest. Do not pass a persistence object as the
host.

## 4. Convert and validate a JSON-like output

Map a JSValue into a JSON-compatible object, then decode a Swift schema. The
validator must enforce bounds and the current source revision.

~~~swift
import Foundation
import JavaScriptCore

struct RuleOutput: Codable, Equatable, Sendable {
    let sourceRevision: String
    let label: String
    let score: Double
}

enum RuleOutputError: Error {
    case missingValue
    case notJSONCompatible
    case invalidScore
}

func decodeRuleOutput(
    value: JSValue?,
    currentRevision: String
) throws -> RuleOutput {
    guard let value else { throw RuleOutputError.missingValue }
    guard let object = value.toObject() else {
        throw RuleOutputError.notJSONCompatible
    }
    guard JSONSerialization.isValidJSONObject(object) else {
        throw RuleOutputError.notJSONCompatible
    }

    let data = try JSONSerialization.data(withJSONObject: object)
    let output = try JSONDecoder().decode(RuleOutput.self, from: data)
    guard output.sourceRevision == currentRevision else {
        throw RuleOutputError.notJSONCompatible
    }
    guard output.score.isFinite, (0...1).contains(output.score) else {
        throw RuleOutputError.invalidScore
    }
    return output
}
~~~

The real validator should also check string length, allowed characters,
unexpected keys, nested depth, enum values, identifier scope, and stale
authorization. Never decode the result and commit it in the same unchecked
step.

## 5. Keep values inside one virtual machine

Contexts can share a virtual machine, but a JSValue from one virtual machine
cannot be passed to another. Use immutable Swift values when crossing the
feature boundary.

~~~swift
import JavaScriptCore

func sameMachineContexts() -> (JSContext, JSContext) {
    let machine = JSVirtualMachine()
    let first = JSContext(virtualMachine: machine)!
    let second = JSContext(virtualMachine: machine)!
    return (first, second)
}

func separateMachineContext() -> JSContext {
    JSContext()!
}
~~~

Do not put these contexts in a global pool without a lifecycle and data
isolation policy. If independent work really needs concurrency, use separate
virtual machines and exchange Codable/value snapshots, not JSValue objects.

## 6. Use JSManagedValue for exported callbacks

Do not store a raw JSValue in a native object exported to JavaScript. Use a
managed value and describe the ownership relationship to the virtual machine.

~~~swift
import JavaScriptCore

final class CallbackOwner: NSObject {
    private let machine: JSVirtualMachine
    private let managedValue: JSManagedValue

    init?(value: JSValue, machine: JSVirtualMachine) {
        guard let managedValue = JSManagedValue(value: value) else {
            return nil
        }
        self.machine = machine
        self.managedValue = managedValue
        super.init()
        machine.addManagedReference(managedValue, withOwner: self)
    }

    deinit {
        machine.removeManagedReference(managedValue, withOwner: self)
    }
}
~~~

Recheck the Swift initializer signatures and ownership semantics in the target
SDK. Exercise create/evaluate/teardown repeatedly; a single deallocation test
does not prove there is no callback or context cycle.

## 7. Create a typed AI proposal instead of evaluating raw model output

Keep the model provider separate from the JavaScriptCore runner.

~~~swift
struct ScriptProposal: Codable, Equatable, Sendable {
    let sourceRevision: String
    let script: String
    let capabilities: [String]
    let expectedOutput: String
    let modelRoute: String
}

enum ScriptReview: Equatable {
    case accept
    case edit(String)
    case dismiss
    case stale
}

func validateProposal(
    _ proposal: ScriptProposal,
    currentRevision: String,
    allowedCapabilities: Set<String>,
    maxSourceLength: Int
) -> Bool {
    guard proposal.sourceRevision == currentRevision else { return false }
    guard proposal.script.utf8.count <= maxSourceLength else { return false }
    guard !proposal.script.isEmpty else { return false }
    return proposal.capabilities.allSatisfy(allowedCapabilities.contains)
}
~~~

Add syntax evaluation, output validation, dry-run fixtures, review, and
commit-time revision checks around this type. A valid proposal is still
untrusted until those steps pass.

## 8. Put script status in a native SwiftUI review surface

Use ordinary SwiftUI content for the source, output, and error. Group real
actions with Liquid Glass only after checking the target SDK.

~~~swift
import SwiftUI

struct ScriptReviewView: View {
    let source: String
    let status: String
    let output: String?
    let runFixture: () -> Void
    let accept: () -> Void
    let dismiss: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(status)
                .font(.headline)
                .accessibilityAddTraits(.isHeader)

            ScrollView {
                Text(source)
                    .font(.system(.body, design: .monospaced))
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(minHeight: 180)

            if let output {
                Text(output)
                    .font(.body)
                    .accessibilityLabel("Preview output: \(output)")
            }

            GlassEffectContainer(spacing: 12) {
                HStack {
                    Button("Run fixture", systemImage: "play", action: runFixture)
                    Button("Dismiss", systemImage: "xmark", action: dismiss)
                    Button("Accept", systemImage: "checkmark", action: accept)
                }
                .labelStyle(.iconOnly)
                .padding(8)
                .glassEffect()
            }
        }
        .padding()
    }
}
~~~

Add visible capability scope, source revision, error/retry states, and a plain
fallback when the glass group is reduced or unavailable. Do not mark Accept as
available until the latest validation result is still fresh.

## 9. Use a runner lifecycle instead of main-actor evaluation

JavaScript evaluation is synchronous. A production app needs a runner that
owns its context on a dedicated executor or queue, serializes access, drops
stale generations, and maps cancellation to a result that cannot commit.

~~~text
start generation N
  -> create/own context
  -> evaluate bounded source
  -> convert to immutable output
  -> compare generation and source revision
  -> publish result or discard
cancel generation N
  -> stop observing / abandon runner according to policy
  -> ensure no later completion can commit N
~~~

Do not describe abandonment of an executor as hard preemption of a synchronous
JavaScript call. Test the actual cancellation and stale-result behavior in the
named target.

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
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
