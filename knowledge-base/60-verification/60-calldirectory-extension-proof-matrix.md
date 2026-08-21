# Call Directory extension proof matrix

Use this matrix to prove a Call Directory route in layers. A provider compile or reload callback is not proof that a physical Phone call was labeled or blocked.

| Claim | Evidence | Failure fixture / boundary |
| --- | --- | --- |
| The correct extension is installed | Signed build contains the containing app and Call Directory extension target with the expected bundle identifier | Wrong target membership, stale install, or mismatched identifier |
| The provider receives a request | Extension log records a redacted request mode, snapshot version, and counts | No system request, extension disabled, or provider launch failure |
| A full request is valid | `isIncremental == false`; all identification and blocking streams are emitted in ordered form; no removal method is called | Partial list, removal during full request, invalid number, or duplicate |
| An incremental request is valid | `isIncremental == true`; only relative adds/removes are emitted against a known system-loaded baseline | Lost baseline, changed normalization, or treating a delta as a full list |
| Identification entries are usable | Controlled number is present, label is emitted, reload succeeds, and Phone displays the expected source-qualified label | Wrong number normalization, stale label, Contacts match taking precedence, or dataset mismatch |
| Blocking entries are usable | Controlled number is in the blocking stream, reload succeeds, and the physical device exhibits the documented blocked-call behavior | Number absent, user/system list precedence, disabled extension, or test environment limitation |
| Changed labels converge | Incremental fixture removes the old number entry and adds the new label; the resulting snapshot is versioned | Multiple labels retained, removal omitted, or stale system snapshot |
| Removed numbers converge | Incremental fixture calls the correct removal method and subsequent list no longer contains the number | Removal called during a full request or wrong stream removed |
| Provider failures are visible | `CXCallDirectoryExtensionContextDelegate.requestFailed` records a redacted error category and the containing app keeps prior known state | Error swallowed, raw number logged, or UI claims fresh data |
| Manager status is understood | Containing app records `unknown`, `disabled`, or `enabled` separately from reload completion | Treating status as a match guarantee or treating reload success as enabled state |
| Settings recovery works | `openSettings` reaches Call Blocking & Identification settings on a signed device | Preview-only button, wrong extension identifier, or unavailable system route |
| Data provenance is trustworthy | Each record has source, freshness, correction path, and block policy; diagnostics omit raw sensitive data | Unverifiable label, silent model-generated block, or stale source presented as live |
| Model behavior is bounded | Model proposal validation rejects unsupported label/number/action and falls back when unavailable | AI invents a label, auto-blocks, or silently sends raw data to a server |
| Accessibility is usable | VoiceOver, Dynamic Type, increased contrast, Reduce Motion, Voice Control, and Switch Control complete status/reload/review/unblock tasks | Color-only state, hidden consequence, clipped localized label, or gesture-only glass control |
| Release configuration is ready | Archive, signing, extension target membership, privacy text, and distribution metadata are inspected | Development-only evidence, missing extension, or unverified App Store/TestFlight behavior |

## Fixture set

Use synthetic or controlled numbers and labels:

- empty full directory;
- two ordered identification entries;
- two ordered blocked entries;
- duplicate number;
- out-of-order number;
- number above `CXCallDirectoryPhoneNumberMax`;
- changed label for an existing number;
- deleted identification and blocking entries;
- incremental request with no delta;
- manager status unknown/disabled/enabled;
- provider error and reload error;
- unavailable model and low-confidence proposal;
- long localized label and large Dynamic Type;
- extension disabled after a prior successful load.

## Evidence ladder

1. Source and normalization unit tests.
2. Provider compile in the named Call Directory extension target.
3. Full/incremental fixture tests with ordered streams and removal rules.
4. Containing-app manager status/reload/settings test.
5. Signed installation and extension enablement on a physical device.
6. Controlled Phone caller-ID and blocking observation, where permitted.
7. Accessibility/localization task evidence.
8. Archive, signing, and distribution evidence.

Record the device model, OS build, extension version, snapshot version, and test-number provenance. Never claim universal telephony behavior from one device observation.

## Sources

- [CallKit](https://developer.apple.com/documentation/callkit)
- [Identifying and blocking calls](https://developer.apple.com/documentation/callkit/identifying-and-blocking-calls)
- [CXCallDirectoryProvider](https://developer.apple.com/documentation/callkit/cxcalldirectoryprovider)
- [CXCallDirectoryExtensionContext](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext)
- [isIncremental](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/isincremental)
- [removeIdentificationEntry(withPhoneNumber:)](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/removeidentificationentry%28withphonenumber%3A%29)
- [removeBlockingEntry(withPhoneNumber:)](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/removeblockingentry%28withphonenumber%3A%29)
- [CXCallDirectoryExtensionContextDelegate](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontextdelegate)
- [CXCallDirectoryManager](https://developer.apple.com/documentation/callkit/cxcalldirectorymanager)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
