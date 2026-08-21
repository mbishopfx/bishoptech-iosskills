# LiveCommunicationKit and system calling proof matrix

Calling features require layered proof. A SwiftUI preview can prove a state card renders; it cannot prove a PushKit wake-up, system call surface, audio route, default-app entitlement, carrier path, or remote media connection. Use the highest evidence level required by the chosen lane.

Related pages:

- [LiveCommunicationKit framework review](../42-framework-deep-dives/121-swiftui-live-communication-kit-calling-review.md)
- [LiveCommunicationKit design review](../21-design-deep-dives/149-swiftui-live-communication-kit-calling-review-design.md)
- [LiveCommunicationKit route](../50-capability-recipes/152-swiftui-live-communication-kit-calling-review-route.md)
- [LiveCommunicationKit code recipes](../70-code-recipes/164-swiftui-live-communication-kit-calling-review-recipes.md)

## 1. Evidence levels

| Level | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| C0 | Official source and SDK review | API/policy understanding | Build or service behavior |
| C1 | Reducer/decoder unit tests | Deterministic app logic | Entitlement, system UI, network/audio |
| C2 | SwiftUI preview/UI test | Rendering, navigation, accessibility labels | System call UI, PushKit, remote media |
| C3 | Debug physical device | Permission, audio route, system integration | TestFlight signing, App Review, all carriers |
| C4 | Two-device/provider run | Incoming/outgoing VoIP and media state | Default-app program approval |
| C5 | Signed archive/TestFlight | Embedded capability, background mode, release asset | App Store approval or every region |
| C6 | Region/account/carrier runbook | Default dialer/calling eligibility and carrier path | Future OS/device behavior |

## 2. Gate matrix

| ID | Gate | Pass evidence | Failure meaning |
| --- | --- | --- | --- |
| G0 | Lane selection | VoIP, CallKit, PushKit, default calling, default dialer, history, or translation is named | Architecture is conflated |
| G1 | SDK availability | Current target compiles with availability handling | Wrong target assumption |
| G2 | Framework link | LiveCommunicationKit/CallKit/PushKit/AVFAudio target linkage inspected | Missing framework |
| G3 | Calling entitlement | Signed app contains calling-app when required | Debug-only default app |
| G4 | Dialer entitlement | Signed app contains dialing-app when required | Unapproved/unsupported dialer claim |
| G5 | Background mode | voip mode and target configuration match product | Push/system behavior may fail |
| G6 | Manager lifecycle | One retained manager, delegate, reset, invalidate | Duplicate managers/stale callbacks |
| G7 | Action deadline | Every ConversationAction is fulfilled/failed before timeout | Stuck system UI |
| G8 | Conversation state | idle/joining/joined/paused/leaving/left maps to real service state | UI claims connection too early |
| G9 | Event reporting | started/connected/updated/ended events have service evidence | False system state |
| G10 | Incoming wake-up | VoIP push is validated and reported promptly | Push misuse or dropped call |
| G11 | Audio session | Activation/deactivation and route/interruption recovery | Silent or competing audio graph |
| G12 | Fallback | Explicit telephony/system fallback is validated and user initiated | Accidental carrier call |
| G13 | History | Scope, predicate, update, read, and follow-up handle are tested | Overclaiming call history |
| G14 | Translation | Language pair, engine, mute semantics, delay/failure are tested | Translation state is misleading |
| G15 | AI boundary | Proposal source/revision/review/fallback are tested | Generated output becomes call truth |
| G16 | Privacy | handle/push/audio/transcript/history logging and retention reviewed | Communication data leak |
| G17 | Accessibility | VoiceOver, Dynamic Type, alternate input, reduced effects | Inaccessible high-consequence action |
| G18 | Distribution | Archive/TestFlight/metadata/entitlement evidence | Local run only |

## 3. Fixture and account matrix

Record the provider/service version, accounts, device models, OS versions, network, audio route, and test date. Use synthetic handles and test accounts.

| Fixture | Required observation |
| --- | --- |
| Two physical iPhones, VoIP service | Outgoing call connects and ends |
| Incoming push with app terminated | PushKit wake-up and system incoming UI |
| Invalid/expired call UUID | Safe rejection without stale ringing |
| Answer before media readiness | Connecting state until service joins |
| Remote hang-up | Ended state and history projection |
| Local hang-up during connecting | Idempotent end and no later join |
| Two concurrent calls | Configuration limit and merge/hold policy |
| Video-supported call | Capability and pause/route behavior |
| Audio-only call | Video action absent |
| Translation-capable call | Default/custom engine action |
| Translation unavailable | Original audio remains usable |
| Bluetooth receiver/speaker | AVAudioSession route state |
| Interruption/media reset | Recovery or clear end |
| Calling-app selected | VoIP and telephony fallback |
| Calling-app not selected | Confirmation/system route |
| EU default-dialer account/device | Cellular action and history scope |
| Non-EU or ineligible device | Clear restriction/fallback |
| Multiple cellular services | Service selection and routing |

## 4. Manager and action tests

### Deterministic tests

- Configuration advertises only supported handle types.
- A duplicate ConversationManager is not created by view re-rendering.
- A manager reset clears pending actions safely and rebuilds the service connection.
- Unknown conversation UUIDs fail without creating a new record.
- A duplicate action UUID is idempotent.
- An expired action cannot be fulfilled.
- A late server response does not fulfill a timed-out action.
- Start and Join do not transition to Joined before the media policy allows it.
- End is safe from idle, connecting, joined, paused, and already-left states.
- Capability updates control whether pause, merge, video, tone, or translation appears.
- An event report includes the correct conversation ID and time.
- Local and server call IDs reconcile across cold launch.

### Physical/system tests

- The system call UI is shown for the intended route.
- Do Not Disturb or system interruption behavior is not bypassed.
- Answer/End/Mute actions reach the delegate.
- The app’s system-owned manager survives the app screen disappearing.
- System reset returns the UI to a recoverable state.
- A provider can invalidate without leaving a stuck call badge.

## 5. PushKit tests

For each incoming fixture:

    push received
      -> token/type verified
      -> UUID/handle bounded
      -> minimum decryption/identity work
      -> system call reported
      -> completion called
      -> service connection
      -> answer/join

Assert:

- non-VoIP payloads do not use the VoIP push type;
- malformed UUID or handle does not ring a stale call;
- the call is reported promptly enough for system behavior;
- caller display data is bounded and sanitized;
- the push completion handler is called on every path;
- answer is not fulfilled before media readiness;
- provider failure reports the correct end reason;
- cancellation uses the existing network/service channel rather than a second cancellation push;
- no raw push payload is written to production logs;
- a service outage does not leave the system UI claiming Joined.

Use a real APNs/provider environment for C4 evidence. A local push simulation is C2 at most.

## 6. Audio and route tests

| Test | Expected |
| --- | --- |
| System activates AVAudioSession | App configures its graph once |
| System deactivates session | Graph suspends/releases without deleting call state |
| Speaker route | UI and accessibility label reflect output |
| Bluetooth route | Active route is shown; audio stays connected or recovers |
| Wired/USB route | Route change is handled |
| Interruption | Call state and media recovery are explicit |
| Media-services reset | Graph can rebuild or ends safely |
| Input denied/unavailable | Mute/error state is truthful |
| Translation + mute | Upstream audio behavior follows the translation policy |
| Background/system call UI | App does not require visible SwiftUI view to own audio |

Collect real-device latency and drop observations separately from the UI pass/fail result.

## 7. Default calling and telephony fallback

### Calling-app proof

- signed calling-app entitlement is present;
- App Store Connect configuration meets Apple’s documented criteria;
- voip background mode is present;
- app links the intended framework;
- person can select the app in the eligible system setting;
- incoming/outgoing VoIP path works;
- failed VoIP route presents the explicit telephony fallback;
- fallback occurs only after person intent;
- app distinguishes VoIP requested, cellular requested, and connected.

### Dialer proof

- signed dialing-app entitlement is present;
- Apple Developer account and device meet the documented EU test boundary;
- default-dialer selection is applied and removed;
- non-default confirmation behavior is tested;
- StartCellularConversationAction handles a valid phone handle;
- TelephonyConversationManager reports errors and success-to-routing separately;
- CellularService list and selection are correct;
- carrier/no-service/device conditions have recovery;
- ConversationHistoryManager scope starts at default-dialer selection;
- a recent row revalidates its handle before starting a follow-up call.

Do not mark these gates passed from a non-EU simulator or a local entitlement file.

## 8. Translation tests

- Configuration advertises translation only when the route implements it.
- SetTranslatingAction carries the expected local and remote languages.
- Start translation fulfills with the actual default/custom engine.
- Stop translation fulfills and original audio remains available.
- Microphone mute does not deactivate upstream audio when translation requires it.
- Translation delay is visible without claiming a live translated result.
- Missing language resources/network/model produce a clear fallback.
- Translation output and original audio/transcript retention are privacy-reviewed.
- A generated translation is not labeled as a verified verbatim record.

## 9. History and privacy tests

- History access is limited to the documented default-dialer context.
- Predicate queries are bounded.
- Updates refresh the value projection without duplicate rows.
- Mark-read is distinct from calling.
- Handle values are masked/redacted in logs and screenshots.
- Caller data from pushes is not retained beyond policy.
- Audio/transcript/translation records have explicit retention and deletion.
- System recipient-sharing disclosures are reflected in product privacy copy.
- Health research Speech Metrics opt-out is configured when required by the product.
- AI inputs exclude unnecessary private handles, credentials, and raw push data.

## 10. SwiftUI and scene tests

Run state tests without hardware:

- cold and warm scene delivery converge on one conversation;
- view disappearance does not invalidate an active system call;
- stale callback from an old manager generation is ignored;
- scene phase updates the projection without duplicating actions;
- action timeout is rendered as retryable;
- system reset clears only invalid state;
- AI proposal cannot call or end a conversation;
- inaccessible labels reflect current state and recipient.

UI tests should cover:

- pre-call recipient review;
- explicit Call;
- Connecting versus Joined;
- Mute/translation/End;
- failure/fallback;
- history scope;
- Dynamic Type and VoiceOver labels;
- keyboard/switch/pointer invocation;
- reduced motion/transparency.

## 11. AI evaluation matrix

| Case | Evidence |
| --- | --- |
| model unavailable | Manual call/history remains usable |
| stale transcript | Proposal is rejected or refreshed |
| ambiguous handle | Person sees candidates and chooses |
| wrong model summary | Source text remains visible; no automatic action |
| translated draft | Original and generated text are distinguishable |
| privacy-sensitive call | Input is excluded or consented |
| prompt injection in transcript | No system action occurs |
| network fallback | Disclosure and retention policy are visible |

The model may assist with content. The framework/service state remains the authority for call lifecycle.

## 12. Archive and release evidence

Inspect the signed artifact for:

- LiveCommunicationKit and/or CallKit linkage;
- calling-app entitlement when intended;
- dialing-app entitlement when intended;
- voip background mode;
- notification/push capability;
- target/deployment values;
- privacy strings/manifests;
- system UI assets and localized strings.

Install the TestFlight artifact and repeat:

- one outgoing VoIP call;
- one incoming system call;
- one audio route change;
- one failure/fallback path;
- translation if shipped;
- default-app behavior in the eligible region;
- accessibility state review.

App Review and program approval remain separate from local archive proof.

## 13. Evidence log template

    Feature:
    Lane:
    Build:
    SDK:
    Account/provider:
    Device and region:
    Framework UUID:
    Server call ID:
    Entitlement inspection:
    Push/audio conditions:
    Steps:
    Manager/action events:
    Service evidence:
    System UI evidence:
    Accessibility result:
    Fallback result:
    Privacy/log review:
    Evidence level:
    Open issue:

## Sources

- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [Initiating VoIP conversations with LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit/initiating-voip-conversations-with-livecommunicationkit)
- [Preparing your app to be the default calling app](https://developer.apple.com/documentation/callkit/preparing-your-app-to-be-the-default-calling-app)
- [Preparing your app to be the default dialer app](https://developer.apple.com/documentation/livecommunicationkit/preparing-your-app-to-be-the-default-dialer-app)
- [ConversationManager](https://developer.apple.com/documentation/livecommunicationkit/conversationmanager)
- [ConversationManagerDelegate](https://developer.apple.com/documentation/livecommunicationkit/conversationmanagerdelegate)
- [Conversation](https://developer.apple.com/documentation/livecommunicationkit/conversation)
- [Conversation.State](https://developer.apple.com/documentation/livecommunicationkit/conversation/state-swift.enum)
- [Conversation.Event](https://developer.apple.com/documentation/livecommunicationkit/conversation/event)
- [ConversationAction](https://developer.apple.com/documentation/livecommunicationkit/conversationaction)
- [SetTranslatingAction](https://developer.apple.com/documentation/livecommunicationkit/settranslatingaction)
- [ConversationHistoryManager](https://developer.apple.com/documentation/livecommunicationkit/conversationhistorymanager)
- [TelephonyConversationManager](https://developer.apple.com/documentation/livecommunicationkit/telephonyconversationmanager)
- [StartCellularConversationAction](https://developer.apple.com/documentation/livecommunicationkit/startcellularconversationaction)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [CXCallController](https://developer.apple.com/documentation/callkit/cxcallcontroller)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [Supporting PushKit Notifications in Your App](https://developer.apple.com/documentation/pushkit/supporting-pushkit-notifications-in-your-app)
- [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
- [PKPushType.voIP](https://developer.apple.com/documentation/pushkit/pkpushtype/voip)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
