# SwiftUI Wi-Fi Aware and device-discovery route design

The best iOS 26 nearby-device experience feels like one clear native task,
not like a networking console. The user should understand why the app is
looking for a device, which relationship is being created, what the system
picker is doing, what will happen after selection, and how to recover when a
radio, peer, or accessory is unavailable.

This page pairs with the [Wi-Fi Aware, DeviceDiscoveryUI, and
AccessorySetupKit route](../42-framework-deep-dives/140-swiftui-wifi-aware-device-discovery-route.md).

## Design the relationship first

Use different language and visual hierarchy for these two paths:

~~~text
nearby app
  “Choose a device to connect to”
  DevicePicker -> selected WAEndpoint -> app handshake -> operation

hardware accessory
  “Add an accessory”
  AccessorySetupKit picker -> authorization -> accessory control screen
~~~

“Pair” is appropriate for the system pairing moment. It is not always the
right label for the entire product relationship. A nearby app may be selected
for one short transfer, while an accessory may remain authorized in the
system’s accessory list. Tell the user which relationship is being created and
what they can remove later.

Do not combine app-peer and accessory rows in one undifferentiated list. The
system uses different frameworks and trust semantics, and the user needs to
know whether they are selecting another copy of the app or adding a physical
product.

## The screen sequence

A durable route can be modeled as:

~~~text
Nearby task
  -> why this connection is needed
  -> capability / supported-device check
  -> choose App device or Accessory
  -> system pairing or setup UI
  -> selection review
  -> app-owned trust and operation review
  -> Network transport status
  -> applied result or recovery
~~~

The app-owned screen before system UI should be short. It should explain the
user outcome and the relevant privacy boundary, then present one deliberate
primary action. Do not start discovery as soon as the view appears if the
user has not asked to find anything. This avoids an unexplained route attempt
and makes the system picker’s appearance predictable.

## State is the visual system

Keep state in a coordinator or reducer and project a small, stable value to
SwiftUI:

~~~text
Capability
  supported | unsupported | entitlementMissing | noRadioResources

Pairing
  idle | explaining | presenting | selected | cancelled | failed

Selection
  none | peer(candidate) | accessory(candidate) | review | rejected

Authorization
  unknown | requested | denied | awaitingAccessoryAuthorization | authorized

Transport
  idle | browsing | advertising | connecting | handshaking | ready
  waiting(reason) | lost | cancelled | failed

Operation
  idle | proposed | awaitingReview | running | received | validating
  applied | declined | failed | waitingForReconnect
~~~

Make impossible states impossible in the reducer. A `WAEndpoint` can be
selected while the app still has an untrusted candidate, but it must not make
the operation button read “Send” until the app handshake and authorization
review are complete. An `ASAccessory` can be present in the system list while
its state is `awaitingAuthorization`; that should not look like a ready
accessory control surface.

Every state needs a visible label, an accessible equivalent, a permitted
action, and a recovery path. Avoid mapping every error to a blank list or
“Try again.”

## Native composition around system UI

DeviceDiscoveryUI and AccessorySetupKit already provide system-owned pairing
and setup surfaces. The app’s design job is to prepare, contextualize, and
resume the task:

### Before the system surface

Show:

- the user outcome, such as “Transfer this document to another device”;
- the relationship, such as “another copy of this app” or “physical
  accessory”;
- the scope of what will be shared or controlled;
- a short reason for any app-owned local or accessory permission;
- the expected fallback if no compatible device is available.

Use a semantic button with a clear label. A glass button that says only
“Nearby” is decorative ambiguity, not native clarity.

### During the system surface

Let the system picker own the device discovery presentation. Do not layer a
custom fake list over it, intercept its selection with a different identity
model, or imply that a system-displayed name is verified application identity.
For an unsupported device, use the `fallback` view supplied to the SwiftUI
pairing control or a UIKit fallback that keeps the user on the same task.

### After dismissal

Resume with an explicit state. Examples:

~~~text
Device selected
The other app is ready to confirm this transfer.

Pairing cancelled
No device was added. You can search again or choose another method.

Accessory found
Review the accessory before authorizing it.

Accessory unavailable
The setup session ended before authorization. Try again when the accessory is nearby.
~~~

When `DevicePicker` returns a `WAEndpoint`, show a review card that uses a
bounded presentation record. Keep the raw endpoint, service name, and paired
device ID out of the primary copy. For an accessory, show the system-provided
display name and product image, but label the accessory’s authorization state
separately.

## Liquid Glass: functional grouping, not trust decoration

Liquid Glass can make an iOS 26 nearby screen feel native when it clarifies
the action hierarchy. Use it around app-owned controls, not as a substitute
for the system picker or a security boundary.

Recommended shell:

~~~text
opaque content layer
  title, explanation, candidate/review content, status, recovery copy

functional glass group
  [Add device] [Become discoverable] [Cancel]

status group
  [Checking peer] [Waiting for authorization] [Transfer applied]
~~~

Use `GlassEffectContainer` when adjacent glass controls form one functional
group and can morph as the task changes. Give stable identity only to elements
that genuinely participate in that transition. Keep the candidate list and
trust explanation on a legible content layer so that Dynamic Type, Reduce
Transparency, and Increased Contrast do not erase meaning.

Avoid:

- a glass card around every device row;
- a low-contrast “paired” badge that looks like an authenticated badge;
- a glass overlay that hides the picker’s cancellation or recovery path;
- animation that turns a lost peer into a success-like completion;
- using refraction, blur, or tint as the only difference between a peer and an
  accessory;
- placing raw Wi-Fi Aware IDs, service names, or diagnostic endpoints in the
  main user surface.

The visual state must survive when Liquid Glass is unavailable or the user
reduces transparency. Treat system material and tint as decoration around a
stable semantic layout.

## App-peer screen blueprint

### 1. Intent header

Title: “Transfer to a nearby device” or an equally concrete outcome.

Supporting text: “Choose another copy of the app. The selected item is sent
only after you review the device and confirm.”

Primary action: “Choose device.”

Secondary action: “Use another method.”

Do not say “Connect to Wi-Fi Aware.” That is an implementation detail and does
not tell the user what the app will do.

### 2. Discovery state

Before opening `DevicePicker`, show a short explanation of the relationship.
After the picker returns, show a single selected peer row:

~~~text
[device icon] Jordan’s iPhone
             Nearby app · Not yet trusted
             [Review]
~~~

If the paired record has no safe display name, use “Nearby device” and never
fall back to a raw ID. If the candidate set is empty, preserve the distinction
between unsupported hardware, missing entitlement, no paired devices, radio
resource exhaustion, and user cancellation.

### 3. Review sheet

The review sheet must answer:

- Is this another copy of the app or an accessory?
- What item, command, or capability will be shared?
- Is the peer already paired, and has the app handshake completed?
- What does the primary action do right now?
- What will happen if the peer disappears?

Use “Continue to confirm” for a handshake step and “Send selected item” only
when the next action actually begins the approved operation. Put “Cancel” in a
stable location and make it cancel both the UI task and the underlying browser,
listener, or connection operation.

### 4. Transport state

Use plain-language progress:

~~~text
Checking the selected device
Confirming the app identity
Waiting for the other device
Sending the selected item
Waiting for the other device to apply it
Transfer complete
~~~

If a Network path changes, explain the user consequence, not the framework
callback: “The nearby connection is paused” is more useful than “NWPath is
unsatisfied.” Offer “Keep waiting,” “Search again,” or “Use another method” as
appropriate.

## Accessory setup screen blueprint

Accessory setup needs more than a nearby list because authorization can persist
after the picker closes.

~~~text
Add accessory
  explain what the accessory can do
  [Add accessory]
  -> AccessorySetupKit system picker
  -> accessory review
  -> authorize / cancel
  -> “Finish setup in app” if required
  -> authorized accessory control
~~~

Use the product image and name configured for `ASPickerDisplayItem`, but do not
claim that the label proves a particular physical unit until the system and
app identity checks pass. If the descriptor supports Bluetooth and Wi-Fi Aware,
explain which technology is used for setup and which one carries later data.

When an existing SSID-based accessory can be upgraded to Wi-Fi Aware, show a
separate “Enable nearby high-speed connection” review. The user should be able
to decline without losing a working setup if the product has a supported
fallback. When the upgrade fails, keep the original accessory state visible and
do not silently create a second record.

After authorization, the primary accessory screen should show:

- the system accessory name;
- authorized / unavailable / needs attention;
- the current app-owned capability revision;
- the last verified connection state;
- controls whose labels describe the actual side effect;
- “Remove accessory” or equivalent recovery in a clearly separated area.

Never make “discovered” look like “authorized.”

## Accessibility and alternate input

Nearby-device routes have moving state, system sheets, and transient candidates;
they need more semantic structure than a static settings page:

- Use a real `Button` for each app-owned action and let the system controls
  provide their own semantics.
- Combine a candidate’s safe display label, relationship, trust state, and
  action scope into one accessible summary.
- Announce “Picker opened,” “Device selected,” “Pairing cancelled,” “Accessory
  authorized,” and “Connection paused” when focus would otherwise remain on a
  stale control.
- Preserve the user’s selection and focus after a temporary route failure.
- Do not use radio-wave animation, glass tint, signal strength, or color alone
  to communicate availability or trust.
- Test VoiceOver rotor order, Voice Control labels, Switch Control, keyboard
  selection, pointer hover, Dynamic Type, Bold Text, Increase Contrast, Reduce
  Motion, and Reduce Transparency.

For a long discovery timeout, provide a non-animated status and a cancel
button. If an accessory is removed while a control is focused, announce the
state change and move focus to a recovery action, not to an unrelated row.

## Optional AI review surface

The on-device model can help translate a set of verified observations into a
plain-language explanation:

~~~text
“This iPad is eligible for the document transfer because it is paired,
advertises the required service, and supports protocol revision 2.”
~~~

That sentence is useful only if the deterministic route has already computed
those facts. The model must not choose an arbitrary raw endpoint, infer an
accessory’s authorization from its name, or call the pairing/setup APIs.

Render an AI proposal as an optional, labeled explanation:

~~~text
On-device explanation
Why this device is eligible
[Show sources] [Use selected device] [Dismiss]
~~~

Keep source fields visible or inspectable: candidate-set revision, paired state,
service role, protocol revision, and operation scope. The primary action still
runs deterministic checks immediately before the side effect. If the model is
unavailable, the review screen should be complete without it.

## Error and recovery language

| Technical condition | User-facing state | Recovery |
| --- | --- | --- |
| Wi-Fi Aware unsupported | “This device cannot use nearby Wi-Fi connections.” | Use another method; do not show a dead picker. |
| Missing entitlement or bad service declaration | “Nearby connections are not available in this build.” | Diagnostics for the developer; never ask the user to repair signing. |
| No paired devices | “No paired devices are available yet.” | Open pairing or use another method. |
| User cancelled | “No device was added.” | Search again or leave the task. |
| Radio resources unavailable | “The nearby connection is busy right now.” | Retry with backoff; do not loop automatically forever. |
| Peer disappeared | “The other device is no longer available.” | Keep the approved scope; search again or cancel. |
| Accessory awaiting authorization | “Finish accessory setup before using this control.” | Finish or fail authorization; no control side effects. |
| Transport idle timeout | “The nearby connection timed out.” | Reconnect with a new epoch and handshake. |
| App handshake rejected | “This device cannot complete this operation.” | Explain compatibility/trust; never retry a rejected identity blindly. |

Preserve technical details in a support/developer diagnostics view with
privacy-safe redaction. Do not display raw endpoints, paired IDs, or device
advertisement content by default.

## What to test in the design review

Before calling the screen native or finished, review it against these tasks:

1. A first-time user understands why another app or accessory is needed.
2. The picker can be cancelled without changing app state.
3. A candidate’s name is not presented as authentication.
4. The user can review the exact item or side effect before transport starts.
5. A peer loss does not erase the approved scope or silently choose another
   device.
6. An accessory authorization denial leaves a recoverable setup state.
7. The screen works without on-device AI and without Liquid Glass.
8. VoiceOver can find the current state and recovery action after picker
   dismissal.
9. Dynamic Type and Reduce Transparency preserve the identity and trust
   distinction.
10. The signed physical build shows the same labels and target capability as
    the design review.

## Sources

- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [Building peer-to-peer apps](https://developer.apple.com/documentation/wifiaware/building-peer-to-peer-apps)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [DevicePickerSupportedAction](https://developer.apple.com/documentation/devicediscoveryui/devicepickersupportedaction)
- [DDDevicePairingViewController](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingviewcontroller)
- [DDDevicePickerViewController](https://developer.apple.com/documentation/devicediscoveryui/dddevicepickerviewcontroller)
- [DDDevicePairingAccess](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess)
- [Wi-Fi Aware](https://developer.apple.com/documentation/wifiaware)
- [AccessorySetupKit](https://developer.apple.com/documentation/accessorysetupkit)
- [Discovering and configuring accessories](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [ASAccessorySession](https://developer.apple.com/documentation/accessorysetupkit/asaccessorysession)
- [ASAccessory](https://developer.apple.com/documentation/accessorysetupkit/asaccessory)
- [ASDiscoveryDescriptor](https://developer.apple.com/documentation/accessorysetupkit/asdiscoverydescriptor)
- [ASPickerDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/aspickerdisplayitem)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
