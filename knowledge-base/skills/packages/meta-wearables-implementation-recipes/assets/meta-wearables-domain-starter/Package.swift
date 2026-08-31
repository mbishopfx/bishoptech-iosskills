// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "MetaWearablesDomainStarter",
    platforms: [
        .iOS(.v17),
        .macOS(.v14),
    ],
    products: [
        .library(
            name: "MetaWearablesDomain",
            targets: ["MetaWearablesDomain"]
        ),
    ],
    targets: [
        .target(name: "MetaWearablesDomain"),
        .testTarget(
            name: "MetaWearablesDomainTests",
            dependencies: ["MetaWearablesDomain"]
        ),
    ]
)
