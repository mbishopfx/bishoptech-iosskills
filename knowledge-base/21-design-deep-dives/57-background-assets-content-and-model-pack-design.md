# Background Assets content and model-pack design

Background content should feel like part of the app, not a mystery download happening behind the person’s back. Explain what the resource unlocks, how much space or network time it may require, which version is ready, and what the app can do when it is unavailable.

Use this guide with the [Background Assets deep dive](../42-framework-deep-dives/37-background-assets-managed-content-and-model-packs.md), the [capability route](../50-capability-recipes/60-background-assets-content-route.md), the [proof matrix](../60-verification/54-background-assets-content-proof-matrix.md), and the [code recipes](../70-code-recipes/72-background-assets-content-recipes.md).

## Design objective

The person should always know:

- what content is being downloaded;
- why the app needs it;
- whether it is essential, optional, or on demand;
- how much local space and network cost to expect;
- whether the content is downloaded, validated, or actually ready;
- what works without it;
- how to retry, remove, or choose a smaller route.

Do not use a generic “Preparing…” state for a multi-gigabyte model, level pack, or video library.

## Resource card anatomy

~~~text
Resource title
  What this unlocks
  version 3 • 142 MB • validated on this device
  [Download] or [Use offline]
  Last checked: today
  Manage storage
  Use basic mode instead
~~~

For an on-device AI model:

- name the capability, not the model vendor;
- show supported device/OS conditions when they matter;
- avoid promising accuracy or speed before the model is evaluated;
- use “additional model” or “optional language pack” rather than implying the feature is unavailable forever.

## State language

Use explicit state copy:

| State | Copy direction |
| --- | --- |
| Declared | “Available to download” |
| Scheduled | “Download scheduled” |
| Downloading | “Downloading [resource], [progress]” |
| Waiting | “Waiting for a network or system opportunity” |
| Local | “Downloaded; checking compatibility” |
| Validated | “Ready to use” |
| Updating | “Updating from version 2 to version 3” |
| Stale | “A newer version is available; version 2 remains usable” |
| Failed | “Couldn’t download; basic mode is still available” |
| Removed | “This resource was removed; choose another mode” |
| Unsupported | “This device can’t use this resource” |

“Downloaded” and “ready” should not be the same label.

## Essential versus optional

Essential assets should be rare. If a resource is marked essential, the product is saying that the app’s first useful experience depends on it.

Prefer:

- a small signed shell in the main bundle;
- a compact essential resource;
- optional packs after the first useful screen;
- an on-demand route at the moment of need;
- a deterministic fallback if the pack never arrives.

If an asset is required for first launch, design a clear offline/low-storage/failed-install path. The system’s attempt to download an essential asset is not a guarantee that it finished before the person expects the app to open.

## Version continuity

When a new pack arrives while the person is using the app:

1. keep the validated active version;
2. download or locate the new version;
3. validate schema, device compatibility, and feature policy;
4. switch at a safe boundary;
5. keep rollback metadata;
6. explain if a restart or migration is required.

Avoid swapping a model or shader library halfway through a task. A proposal created with model version 2 should record that version and be revalidated if the app applies model version 3.

## Progress and interruption

Progress is useful only when it is honest. The system may schedule or pause downloads; a progress bar should not imply a fixed completion time when the framework cannot provide one.

Handle:

- Wi-Fi-only or cellular policy;
- low power/thermal state;
- no network;
- low storage;
- user cancellation;
- system termination;
- app update while a pack is downloading;
- server rollback/removal;
- authentication or domain failure for self-hosted content.

Persist resource state in an app-owned projection. Do not claim that the app will resume from an exact byte offset unless the route proves it.

## Model-pack onboarding

For a downloadable model:

~~~text
model explanation
-> device/OS support check
-> size/storage/network disclosure
-> download or later
-> local availability
-> schema/device/quality validation
-> enabled state
-> first-run sample or task
~~~

Separate:

- model installed;
- model loaded;
- model input/output schema accepted;
- model produces an output;
- model quality meets product threshold.

Do not show “AI is ready” immediately after a file appears in the asset directory.

## Metal and 3D assets

For a Metal shader library, texture pack, or 3D model:

- show the feature the resource unlocks;
- do not expose internal file paths;
- include a reduced-quality renderer;
- detect unsupported GPU features;
- avoid freezing the main actor while loading large data;
- expose memory/thermal degradation as a quality mode;
- provide a way to remove optional content.

Apple-native design is not an excuse to hide a loading failure behind a glass card. A plain, legible fallback is better than a polished dead end.

## Localized resource design

The current localized asset-pack material describes APIs for newer targets, including iOS 27 and later. If the selected project targets iOS 26, do not show a language picker that assumes those APIs exist.

For a target that supports localized packs:

- state whether the app follows system language or an app-specific language choice;
- show the resolved language;
- handle language changes without deleting the active pack prematurely;
- use localized content APIs when the same path exists in multiple languages;
- keep fallback language and audio/subtitle combinations explicit.

## Liquid Glass download surface

Use Liquid Glass sparingly:

- a compact resource status card;
- a toolbar action for download/settings;
- a review action after validation;
- an in-context progress control.

Avoid:

- a full-screen glass curtain for every background update;
- multiple translucent cards for one resource;
- tiny progress text floating over video or 3D content;
- making a glass effect the only indication of readiness;
- using system-style marks without the corresponding system action.

Keep the content itself accessible. Pair visual progress with a text announcement, a status label, and a retry/control action.

## Storage management

Show the local resource inventory:

| Resource | Version | Size | Last used | Remove? |
| --- | --- | --- | --- | --- |
| Tutorial audio | 1.4 | 44 MB | Today | Yes |
| Object model | 3.0 | 182 MB | Yesterday | Yes |
| Required core data | 1.0 | 8 MB | Always | No |

Removing a pack should change the feature state to downloadable or fallback, not silently corrupt the app’s local data. Keep user-owned records separate from replaceable resource packs.

## AI review and provenance

If a downloaded model produces a proposal:

- show the source object;
- record model/pack version;
- expose uncertainty;
- let the person correct or discard;
- do not replace source data with generated text;
- re-run or invalidate proposals after a model update when required;
- keep model files and user data in separate retention policies.

If a pack is removed or invalidated, retain the user-approved record if it does not depend on the pack, and mark derived outputs that cannot be reproduced.

## Accessibility

Test:

- VoiceOver announces resource title, status, size, version, and action;
- Voice Control can activate retry/download/remove/basic mode;
- Switch Control can reach the fallback;
- Dynamic Type does not hide storage size or error text;
- reduced motion does not remove download state;
- increased contrast remains legible over media;
- localization handles long pack names and languages;
- external keyboard can reach a download task where supported.

A progress view in a preview is not evidence that the extension, system scheduler, or completed-file handoff is accessible.

## Preview fixtures

Create redacted fixtures for:

- pack available but not local;
- download scheduled;
- paused/waiting;
- downloaded but incompatible;
- validated/ready;
- update available with current version usable;
- low storage;
- no network;
- canceled;
- extension terminated;
- pack removed;
- model quality regression;
- device unsupported;
- localized pack unavailable on iOS 26 fallback.

## Sources

- [Background Assets](https://developer.apple.com/documentation/backgroundassets)
- [Creating managed asset packs](https://developer.apple.com/documentation/backgroundassets/creating-managed-asset-packs)
- [Downloading Apple-hosted asset packs](https://developer.apple.com/documentation/backgroundassets/downloading-apple-hosted-asset-packs)
- [Testing asset packs locally](https://developer.apple.com/documentation/backgroundassets/testing-asset-packs-locally)
- [Configuring an unmanaged Background Assets project](https://developer.apple.com/documentation/backgroundassets/configuring-an-unmanaged-background-assets-project)
- [Downloading essential assets in the background](https://developer.apple.com/documentation/backgroundassets/downloading-essential-assets-in-the-background)
- [AssetPackManager](https://developer.apple.com/documentation/backgroundassets/assetpackmanager)
- [BADownloadManager](https://developer.apple.com/documentation/backgroundassets/badownloadmanager)
- [BADownloaderExtension](https://developer.apple.com/documentation/backgroundassets/badownloaderextension)
- [Reducing download and storage demands with localized asset packs](https://developer.apple.com/documentation/backgroundassets/reducing-download-and-storage-demands-with-localized-asset-packs)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
