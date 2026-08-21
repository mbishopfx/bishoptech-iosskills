# Tools, Agents, and Side Effects

## Tool calling is a controlled bridge

A Foundation Models tool lets the model call app code to retrieve current information, ground an answer in app data, or perform a bounded action. The flow is:

1. Provide the model with the available tools and their arguments.
2. Submit the prompt.
3. The model chooses a tool and generates arguments.
4. The app validates and runs the tool.
5. The tool returns minimal useful output.
6. The model produces a final response.

## Tool modes

The documented modes are:

- allowed: the model may call tools;
- required: the model must call one or more tools before responding;
- disallowed: the model must answer without tools.

If required mode is used, define a clear exit condition. A tool that always remains required can cause the model to continue calling it without producing a final answer.

## Separate query tools from action tools

Query tools should be read-only, scoped, and easy to retry. Action tools should be:

- explicit about the side effect;
- authorized by the user or an existing permission;
- idempotent where possible;
- validated against current domain state;
- bounded in time and output;
- cancellable or recoverable;
- logged with privacy-minimized diagnostics.

Never let a model-generated string directly execute a destructive command, issue a purchase, send a message, delete records, or change a security setting.

## Use the app architecture

The tool should call a domain use case or service, not duplicate business logic. Visible UI, App Intents, widgets, and model tools should converge on the same authorization and state-transition rules.

## Agent-like designs

Foundation Models can support agent-like abstractions through sessions, tools, guided output, and newer dynamic profile APIs. Treat these APIs as update-sensitive. Start with a single bounded task and a small tool set; add planning loops only when evaluation proves they improve the user outcome.

## Review boundary

For actions with external or irreversible consequences:

model proposes -> app validates -> person confirms -> use case commits

The model should not be the sole authority for identity, permission, financial amount, safety status, or privacy scope.

## Sources

- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Foundation Models updates](https://developer.apple.com/documentation/Updates/FoundationModels)
