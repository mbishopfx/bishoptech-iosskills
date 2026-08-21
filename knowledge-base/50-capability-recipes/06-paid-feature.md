# Paid Feature and Entitlement

## Best fit

Digital functionality, content, subscriptions, or one-time unlocks where the app needs to determine what a person can use.

## Route

StoreKit 2 products -> purchase flow -> verified transaction -> entitlement service -> feature gates -> restore/expiry/revocation handling

## Build order

1. Define the free core workflow and the paid value.
2. Configure products in a StoreKit configuration file for local tests.
3. Build product loading, pending, success, user-cancelled, failure, and unavailable states.
4. Listen for transaction updates and use StoreKit verification.
5. Centralize entitlement calculation; do not scatter product checks through views.
6. Build restore and expiry/degraded behavior.
7. Test sandbox/App Store configuration separately from local StoreKit tests.

## Guardrails

Do not make local user data unreadable because a transaction is unavailable. Do not treat a UI flag as proof of entitlement. Use the current StoreKit API documented for the deployment target.

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [Choosing a StoreKit API for In-App Purchases](https://developer.apple.com/documentation/storekit/choosing-a-storekit-api-for-in-app-purchases)
- [In-App Purchase](https://developer.apple.com/documentation/storekit/in-app-purchase)
- [StoreKit testing](https://developer.apple.com/documentation/storekit/testing-in-app-purchases-in-xcode)
