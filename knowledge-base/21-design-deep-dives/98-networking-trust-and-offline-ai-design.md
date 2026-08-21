# Networking trust, offline behavior, and on-device AI design

## Design objective

A networked iOS app should feel native when connected, remain useful when the path
disappears, and make trust boundaries visible without turning every screen into
a diagnostic console.

The design must answer:

- what is local and immediately available;
- what is remote, pending, streaming, or incomplete;
- whether the app is using a server, an on-device model, or a fallback;
- what will happen if the user cancels or the path changes;
- whether the action is read-only, retryable, idempotent, or consequential;
- why local-network permission or sign-in is needed;
- which state is durable and which state is only a transient transport;
- what system surfaces may safely project the result.

Transport state is supporting context. The primary surface should stay focused on
the user's task.

## State contract

Model transport and domain state separately. A useful combined view is:

    idle
      -> preparing
      -> waitingForAuthorization
      -> connecting
      -> receiving
      -> validating
      -> readyToApply
      -> applying
      -> complete

    preparing/connecting/receiving -> canceled
    connecting/receiving -> offline
    receiving -> incomplete
    validating -> rejected
    applying -> failed
    complete -> stale when source or remote state changes

The network state may be:

- local;
- connected;
- limited/expensive;
- waiting for permission;
- offline;
- authenticating;
- reconnecting;
- failed;
- unknown.

The domain state may be:

- draft;
- proposal;
- approved;
- committed;
- pending sync;
- conflict;
- rejected;
- expired.

Do not collapse “the socket is open” into “the record is saved,” or “the model
returned text” into “the person approved the action.”

## Native hierarchy and Liquid Glass

Use the system's navigation, toolbar, sheet, confirmation, alert, menu, and
semantic control patterns first. Liquid Glass should clarify a layer of the
interface, not replace the application's content hierarchy.

Good app-owned glass roles include:

- a compact connection/status control in a toolbar;
- a review sheet for a streamed AI proposal;
- a floating composer action that remains legible over content;
- a conflict comparison surface;
- a focused transfer-progress inspector;
- a local-device pairing confirmation card.

Keep these roles visually subordinate to the task content:

- one prominent glass container is usually stronger than many floating pills;
- use the platform's material and tint behavior rather than drawing faux glass
  in every row;
- preserve continuous shapes and shared containment for related actions;
- let the background/content provide visual depth;
- avoid persistent decorative blobs that compete with text and controls;
- do not apply glass to every network event or token delta;
- avoid tint as the only indication of failure, privacy, or approval.

System-owned surfaces remain system-owned:

- local-network permission alerts;
- sign-in and account settings;
- sharing UI;
- widgets, controls, and Live Activities;
- system progress for supported background work;
- keyboard, dictation, and authentication prompts.

The app should adapt to accessibility settings, reduced transparency, contrast,
Dynamic Type, device orientation, and the host surface without making the network
status disappear.

## Recommended screen anatomy

A focused networked AI or sync screen can use this hierarchy:

1. navigation title and one primary task action;
2. source/content area that remains readable offline;
3. compact status line with words such as On this iPhone, Streaming, Waiting to
   sync, or Review needed;
4. result/proposal content with source and revision context;
5. explicit Apply, Save draft, Retry, Cancel, or Review actions;
6. a secondary detail route for endpoint, last success, permissions, and retry
   diagnostics.

The compact status line is a semantic label, not a spinner-only affordance.
The detail route can explain path, server, model source, and timestamps without
making people understand transport jargon to complete the main task.

## Source and trust language

Use plain language that distinguishes source:

| Situation | Preferred copy | Avoid |
| --- | --- | --- |
| Local model | “Drafted on this iPhone” | “Private and guaranteed” |
| Remote model | “Drafted by the connected service” | “AI knows” |
| Fallback | “On-device mode used because the service was unavailable” | Silent provider change |
| Stream active | “Writing a draft…” | “Final answer” |
| Early disconnect | “The draft stopped before completion” | “Done” |
| Unreviewed output | “Suggestion” | “Fact” |
| Approved output | “Applied by you” | Hide model origin when it matters |
| Local record | “Saved on this iPhone” | “Saved everywhere” |
| Remote pending | “Waiting to sync” | “Synced” |
| Local permission | “Allow access to devices on your network” | Technical Bonjour/ATS terms alone |

If the product makes a consequential recommendation, show the source record,
model/provider route, date or revision, and the action that will be taken. A
confidence score without an explanation or review path is not a trust contract.

## Streaming interaction

Streaming content needs a readable, interruptible state:

- show that the result is still being composed;
- keep the original source visible or one tap away;
- expose cancel without requiring a gesture;
- batch visual updates so text does not stutter or steal focus;
- preserve a draft if the user navigates away and the product promises recovery;
- separate partial text from committed text;
- show an incomplete state after early close or parser rejection;
- require review before a stream can mutate durable user data.

Avoid layout churn from inserting a new control on every delta. Keep the primary
action location stable. A shimmer or animated cursor can be supplemental, but text
such as “Streaming” or “Canceled” must remain available to VoiceOver and users
who reduce motion.

## Offline-first behavior

Choose an explicit degraded-mode policy:

| Feature | Offline behavior |
| --- | --- |
| Browse local records | Full local read |
| Edit local record | Save locally and mark pending when cloud sync exists |
| Remote search | Show cached results with date or disable clearly |
| On-device AI | Continue if the model and assets are available |
| Remote AI | Keep source/draft, explain unavailable service, offer local mode if allowed |
| Large transfer | Queue/defer; show size and network policy |
| Collaboration | Show last known state and prevent false “live” claims |
| Authentication | Preserve draft, route to sign-in, do not discard work |
| Widget/system projection | Project only durable local state with honest freshness |

The main view should not require an internet spinner to display data already saved
on the device. A retry action should not duplicate a command; it should reuse an
idempotency key or create a new intentional attempt.

## Local-network consent and pairing

Local-device features should ask for access at the moment the person understands
the value, not on first launch without context. The explanation should name the
device/service and what the app will do.

A pairing flow should distinguish:

    discovered
      -> selected
      -> permission requested
      -> authenticated
      -> paired
      -> connected
      -> command available

Discovery is not pairing. Pairing is not authorization for every future command.
Show:

- device/service name and owner context;
- whether the connection is local or remote;
- last-seen time;
- protocol or app compatibility;
- permissions and revoke path;
- connection state;
- commands that are available or read-only;
- what data is sent.

Use the system permission prompt and Info.plist declaration as required. Do not
build a fake permission sheet that implies access has been granted.

## Path-aware presentation

A path monitor can inform copy and policy but should not dominate the UI:

- connected: keep status compact or omit it;
- expensive/constrained: show a just-in-time confirmation for large work;
- offline: show a small persistent action to retry or use local mode;
- permission denied: explain the repair path;
- reconnecting: preserve content and action placement;
- server failure: distinguish service failure from device offline.

Do not announce “internet unavailable” when the app only observed a transient
path or a server timeout. Prefer “Couldn’t reach the service” until the evidence
supports a more specific message.

## Error and recovery design

Every recoverable error should answer:

1. what was not completed;
2. what is safe on the device right now;
3. whether retry is safe;
4. what the user can do;
5. whether any data was sent or committed;
6. how to inspect or remove pending data.

Example:

    “The draft is saved on this iPhone. The service stopped before the final
    response. Retry the draft or keep it local.”

For authentication or privacy failures:

    “Your draft was not uploaded. Sign in to continue.”
    “Local-device access is off. Allow access in Settings to connect to Desk Hub.”

Avoid raw URLSession or NWError strings in the primary surface. Put diagnostic
details behind a support/debug route with redaction.

## Accessibility contract

Use semantic SwiftUI controls and labels before custom drawing. Verify:

- VoiceOver announces the current transport and domain state;
- the cancel/retry/apply action has a stable accessible name;
- progress is conveyed through a value/status, not animation alone;
- partial and final text are distinguishable;
- Dynamic Type preserves source, result, and action order;
- the status is not color-only;
- reduced motion disables cursor, pulse, and reconnect animations;
- reduced transparency keeps text and controls legible;
- Voice Control can invoke Retry, Cancel, Apply, Save Draft, and Review;
- Switch Control reaches permission and recovery actions;
- keyboard/controller users can reach the same route;
- localized strings handle long service names, dates, errors, and RTL;
- privacy-sensitive content is not announced or projected when locked.

Do not repeatedly announce every streamed token. Announce state transitions and
meaningful completion/error events, with a user-controlled detail route.

## Privacy and retention

Treat network inputs and outputs as sensitive until the product proves otherwise.
Define:

- which fields leave the device;
- whether the request is encrypted in transit;
- which endpoint/provider receives it;
- whether prompts, transcripts, files, or embeddings are retained;
- what logs and analytics redact;
- how cancellation affects server-side processing;
- how pending uploads are deleted;
- whether local caches are protected and purged;
- whether widgets, notifications, and previews reveal content on a locked device.

Do not market an on-device or private mode from transport selection alone. Verify
the actual model route, telemetry, OS behavior, provider contract, and target
configuration.

## Design checklist

- Is the local source usable with no network?
- Is remote, local, pending, streaming, incomplete, and committed state distinct?
- Does a retry have an idempotency or dedupe story?
- Is a server response validated before persistence?
- Is partial AI output prevented from becoming approved truth?
- Does the person know whether data left the device?
- Are local-network and ATS boundaries explained separately?
- Does Liquid Glass reinforce containment rather than decorate transport noise?
- Does the screen remain readable with large text, VoiceOver, reduced motion, and
  reduced transparency?
- Does the app have a physical-device route for Wi-Fi, cellular, path loss,
  permission, background transfer, and any accessory?
- Does the archive retain privacy strings, ATS, entitlements, and endpoint policy?

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Landmarks: Building an app with Liquid Glass](https://developer.apple.com/documentation/SwiftUI/Landmarks-Building-an-app-with-Liquid-Glass)
- [URL Loading System](https://developer.apple.com/documentation/foundation/url-loading-system)
- [URLSession.AsyncBytes](https://developer.apple.com/documentation/foundation/urlsession/asyncbytes)
- [URLSessionWebSocketTask](https://developer.apple.com/documentation/foundation/urlsessionwebsockettask)
- [Network](https://developer.apple.com/documentation/network)
- [NWPathMonitor](https://developer.apple.com/documentation/network/nwpathmonitor)
- [NSAppTransportSecurity](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapptransportsecurity)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [NSBonjourServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbonjourservices)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
