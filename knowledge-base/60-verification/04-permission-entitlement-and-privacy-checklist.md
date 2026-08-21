# Permission, Entitlement, and Privacy Checklist

## Permission

- [ ] The permission is requested at the point of need.
- [ ] The usage description explains the user outcome in plain language.
- [ ] Not determined, authorized, limited, denied, restricted, and revoked states are handled.
- [ ] The app remains useful when permission is denied.
- [ ] Settings recovery is clear and optional.

## Entitlement/capability

- [ ] Required capability is enabled in the target.
- [ ] Required entitlement is present in the built artifact.
- [ ] Associated domains, merchant identifiers, iCloud containers, HealthKit identifiers, or background modes are verified where relevant.
- [ ] Extensions have the correct target membership and shared data boundaries.
- [ ] App Store/distribution requirements are understood.

## Data boundary

- [ ] Each collected field has a purpose.
- [ ] Retention and deletion are defined.
- [ ] On-device, synced, exported, and remote data are distinguished.
- [ ] Secrets are stored in Keychain/Security, not ordinary persistence.
- [ ] Large private files have a protection and cleanup strategy.
- [ ] Third-party or server data handling is disclosed accurately.

## Sources

- [Requesting authorization to use location services](https://developer.apple.com/documentation/corelocation/requesting-authorization-to-use-location-services)
- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [AuthenticationServices](https://developer.apple.com/documentation/authenticationservices)
- [Security](https://developer.apple.com/documentation/security)
- [App privacy details](https://developer.apple.com/app-store/app-privacy-details/)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
