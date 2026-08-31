# Privacy, publishing, and release

Meta Wearables work crosses camera, microphone/audio, device state, companion
app callbacks, remote APIs, and (for Web Apps) a public URL. Treat each data
flow and distribution gate as explicit. A DAT or Web App prototype is not
automatically a public product.

## Data inventory

Before implementation, record whether the feature handles:

| Data | Questions to answer |
| --- | --- |
| Camera frames/photos/video | Why is capture needed, who can see it, how long is it retained, and can the feature stay on-device? |
| Microphone/audio/transcript | Is audio actually owned by DAT or by the iPhone audio route? Is recording visible and stoppable? |
| Device identifiers/link state | Can the app function without persisting an identifier? Is it logged or sent to a server? |
| Display content | Does the card expose private information in public view? Is there a clear/stop action? |
| Meta AI callback/configuration | Are URL parameters handled only by DAT and excluded from analytics/logs? |
| Web App network/storage | Is the URL HTTPS, are API keys server-side, and is cached data safe when stale? |
| Generated interpretation | Is model output labeled as a suggestion and revalidated against current domain state? |

Minimize capture, redact logs, avoid raw media in crash fixtures, and provide
deletion or retention controls appropriate to the product. Camera and audio
features require honest usage descriptions and a review of Apple's privacy
manifest/required-reason rules where applicable.

## DAT diagnostics and opt-out controls

The official iOS README documents `MWDAT.Analytics.OptOut` and
`MWDAT.CrashReporting.OptOut` controls. The current public behavior says
analytics and crash reporting are enabled unless the app opts out. Decide and
document the product policy rather than silently inheriting a default. Android
uses `com.meta.wearable.mwdat.ANALYTICS_OPT_OUT=true` and
`com.meta.wearable.mwdat.CRASH_REPORTING_OPT_OUT=true` manifest metadata for
the corresponding DAT controls. Check the selected release and target build;
these settings are not a complete product privacy or retention policy.

Do not put `MetaAppID`, `ClientToken`, signing data, release-channel tokens,
personal media, or callback payloads into source control, model context, or
unredacted logs.

## Preview and publishing boundary

The official DAT announcement and repository describe a developer-preview and
controlled tester/release-channel workflow. Current materials also state that
only selected partners may publish integrations publicly during preview. The
Web App toolkit describes a public HTTPS URL plus adding the app through Meta AI
Display Glasses settings. These are different distribution paths:

```text
native DAT app -> Meta project/release channel -> tester/device
Web App -> public HTTPS host -> Meta AI App connections -> Display device
```

Verify current eligibility, review requirements, account/org setup, supported
regions/models, and distribution policy in the authenticated Developer Center
before promising a public launch. Never claim Meta or Apple approval from a
source page, local build, mock test, or QR code.

The current public full-reference page additionally warns that App Store
submission is not supported for the DAT path at this snapshot and attributes the
block to the current `ExternalAccessory`/MFi/privacy-manifest route. Treat that
as a dated release gate to recheck, not as a permanent policy claim.

## Release evidence

For a release candidate, record:

- exact source/package revision, iOS deployment target, build number, and
  `Info.plist`/entitlement/privacy-manifest inspection;
- Meta project, App ID/client-token/channel configuration without exposing
  secrets;
- Meta AI companion app version, glasses model/firmware, DAT app version on
  glasses, Developer Mode/permissions, and network/Bluetooth conditions;
- registration, camera/photo, Display, pause/stop/update, and recovery tasks;
- signed artifact and release-channel evidence for the exact build;
- separate physical Display/Neural Band/camera/audio observations and what is
  still unverified for other models or production.

## Sources

- [DAT iOS README: developer preview and diagnostics controls](https://github.com/facebook/meta-wearables-dat-ios#readme)
- [Meta DAT announcement and preview boundary](https://developers.meta.com/blog/introducing-meta-wearables-device-access-toolkit/)
- [Meta Wearables Developer Terms](https://wearables.developer.meta.com/docs/terms)
- [Meta Wearables Acceptable Use Policy](https://wearables.developer.meta.com/docs/acceptable-use-policy)
- [Web App publishing toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Apple testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
