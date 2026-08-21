# Background processing and continued-task recipes

## Compile boundary

These are compile-oriented route sketches for BackgroundTasks, iOS 26 BGContinuedProcessingTask, scheduled BGAppRefreshTask/BGProcessingTask, progress, checkpoints, on-device AI, and native review surfaces. They are not compiled in this documentation workspace and do not prove scheduling, entitlements, hardware resources, Neural Engine/GPU use, system Live Activity rendering, force-quit behavior, or release readiness.

Register tasks in the main app target, use stable permitted identifiers, and compile the exact route against the selected SDK. The system chooses background execution time and can terminate work.

## Recipe 1: register and submit a continuous task

This route starts from a foreground user action and keeps the work alive when the app backgrounds if system conditions permit:

~~~swift
import BackgroundTasks

final class ContinuedTaskCoordinator {
    private let taskIdentifier = "com.example.app.export"

    func register() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: taskIdentifier,
            using: nil
        ) { [weak self] task in
            guard let task = task as? BGContinuedProcessingTask else {
                return
            }
            self?.run(task)
        }
    }

    func submitExport() throws {
        let request = BGContinuedProcessingTaskRequest(
            identifier: taskIdentifier,
            title: "Exporting selected media",
            subtitle: "Preparing to start"
        )

        if BGTaskScheduler.supportedResources.contains(.gpu) {
            request.requiredResources = .gpu
        }

        request.strategy = .queue
        try BGTaskScheduler.shared.submit(request)
    }

    private func run(_ task: BGContinuedProcessingTask) {
        task.progress.totalUnitCount = 100

        var cancelled = false
        task.expirationHandler = {
            cancelled = true
        }

        Task {
            let result = await runExport(
                progress: task.progress,
                isCancelled: { cancelled }
            )

            if case .success = result {
                task.updateTitle(
                    "Export complete",
                    subtitle: "Ready to review"
                )
            } else {
                task.updateTitle(
                    "Export interrupted",
                    subtitle: "Your source files are safe"
                )
            }
        }
    }
}
~~~

The sample’s cancellation flag is intentionally illustrative. In a production actor/task design, use a concurrency-safe cancellation token, make output commits idempotent, and persist the task result before presenting completion.

The task identifier must be present in the target’s BGTaskSchedulerPermittedIdentifiers configuration. If the app supports multiple concurrently resumable jobs, design the identifier/job mapping with the current SDK and Info.plist contract rather than inventing dynamic identifiers that are not permitted.

## Recipe 2: report real progress

Use completed units that correspond to actual work:

~~~swift
func runExport(
    progress: Progress,
    isCancelled: () -> Bool
) async -> Result<Void, ExportError> {
    let items = await loadExportItems()
    progress.totalUnitCount = Int64(max(items.count, 1))

    for (index, item) in items.enumerated() {
        if isCancelled() {
            return .failure(.cancelled)
        }

        do {
            try await export(item)
        } catch {
            return .failure(.itemFailed(index: index))
        }

        progress.completedUnitCount = Int64(index + 1)
    }

    return .success(())
}
~~~

Do not set progress to 100 until the output manifest and domain record are safely persisted. If the task has expensive variable-cost stages, use stage-based progress or a truthful indeterminate state rather than a fake percentage.

## Recipe 3: persist a resumable checkpoint

Write a checkpoint before starting each expensive unit and after the unit’s output is durable:

~~~swift
import Foundation

struct ProcessingCheckpoint: Codable, Sendable, Equatable {
    let jobID: UUID
    let sourceRevision: String
    var nextIndex: Int
    var outputURLs: [URL]
    var stage: String
    var status: String
}

actor CheckpointStore {
    private var checkpoint: ProcessingCheckpoint?

    func load(jobID: UUID) -> ProcessingCheckpoint? {
        guard checkpoint?.jobID == jobID else {
            return nil
        }
        return checkpoint
    }

    func save(_ value: ProcessingCheckpoint) {
        checkpoint = value
    }
}
~~~

Replace the in-memory property with a durable, protected store. Version the checkpoint schema, keep source revision with it, and verify that an output file exists before advancing nextIndex. A checkpoint must not be treated as a completed domain mutation.

## Recipe 4: handle expiration and cancellation

Cancellation must stop child work and leave a recoverable state:

~~~swift
enum JobStatus: String, Codable {
    case submitted
    case queued
    case running
    case interrupted
    case cancelled
    case failed
    case readyForReview
}

struct JobRecord: Codable {
    var id: UUID
    var status: JobStatus
    var checkpoint: ProcessingCheckpoint?
    var committedSideEffect: Bool
}

func markInterrupted(
    job: inout JobRecord,
    checkpoint: ProcessingCheckpoint?
) {
    guard !job.committedSideEffect else {
        return
    }
    job.status = .interrupted
    job.checkpoint = checkpoint
}
~~~

If a system cancellation arrives after an output was committed, reconciliation should keep the completed result and avoid duplicating the side effect. If no safe checkpoint exists, mark the job interrupted and offer a fresh run.

## Recipe 5: schedule deferrable processing

Use BGProcessingTaskRequest for work that can wait for a system-selected window:

~~~swift
import BackgroundTasks

let processingIdentifier = "com.example.app.maintenance"

func registerMaintenance() {
    BGTaskScheduler.shared.register(
        forTaskWithIdentifier: processingIdentifier,
        using: nil
    ) { task in
        guard let task = task as? BGProcessingTask else {
            return
        }

        task.expirationHandler = {
            cancelMaintenanceWork()
        }

        Task {
            let succeeded = await runMaintenance()
            task.setTaskCompleted(success: succeeded)
        }
    }
}

func scheduleMaintenance() throws {
    let request = BGProcessingTaskRequest(
        identifier: processingIdentifier
    )
    request.requiresNetworkConnectivity = false
    request.requiresExternalPower = true
    try BGTaskScheduler.shared.submit(request)
}
~~~

The system may launch this later or not at the moment the request is submitted. Persist “scheduled” and “last attempted” state, then reschedule only when the product has a real recurring need.

## Recipe 6: resource-aware AI route

Keep the model route behind a capability check and fall back without changing domain truth:

~~~swift
import BackgroundTasks

enum AIProcessingRoute: Sendable {
    case backgroundGPU
    case backgroundInference
    case foregroundOnly
    case deferred
}

func chooseRoute() -> AIProcessingRoute {
    if BGTaskScheduler.supportedResources.contains(.gpu) {
        return .backgroundGPU
    }

    // Background Inference is a separate preliminary entitlement and
    // exact model/API/device gate. Do not infer it from GPU support.
    if backgroundInferenceIsVerifiedForThisTargetAndDevice() {
        return .backgroundInference
    }

    return .foregroundOnly
}
~~~

The function is a product route selector, not a proof of entitlement. Validate the exact Core ML/Core AI/Metal Performance Shaders Graph or other model API in the target. A Foundation Models session may have different availability and lifecycle requirements; compile and test that route independently.

## Recipe 7: type a reviewable AI result

Persist generated output as a proposal with source and revision:

~~~swift
struct ProcessingProposal: Sendable, Equatable {
    let jobID: UUID
    let sourceRevision: String
    let modelRoute: String
    let modelVersion: String
    let generatedText: String
    let createdAt: Date
    var reviewState: String
}

func canReview(
    _ proposal: ProcessingProposal,
    currentSourceRevision: String
) -> Bool {
    proposal.sourceRevision == currentSourceRevision &&
    proposal.reviewState == "needsReview"
}
~~~

The review screen can edit or reject the proposal. Only the domain layer should commit a confirmed value, and system-side effects should perform a fresh authorization/current-state check.

## Recipe 8: progress status in SwiftUI

A native status component should work even when the system Live Activity is unavailable:

~~~swift
import SwiftUI

struct JobProgressView: View {
    let title: String
    let status: JobStatus
    let progress: Double?
    let cancel: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(title, systemImage: symbol)
                .font(.headline)

            if let progress {
                ProgressView(value: progress)
                    .accessibilityValue(
                        Text("\(Int(progress * 100)) percent")
                    )
            } else {
                ProgressView()
            }

            Text(explanation)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            if status == .queued || status == .running {
                Button("Cancel", role: .cancel, action: cancel)
            }
        }
        .padding()
        .glassEffect()
    }

    private var symbol: String {
        switch status {
        case .queued: "clock"
        case .running: "gearshape.2"
        case .readyForReview: "checkmark.circle"
        case .interrupted: "pause.circle"
        case .cancelled: "xmark.circle"
        case .failed: "exclamationmark.triangle"
        default: "arrow.triangle.2.circlepath"
        }
    }

    private var explanation: String {
        switch status {
        case .queued:
            "Waiting for system resources."
        case .running:
            "Processing selected content."
        case .readyForReview:
            "Your result is ready for review."
        case .interrupted:
            "The source is safe; you can resume or start again."
        case .cancelled:
            "The task was cancelled and no new side effect was applied."
        case .failed:
            "The source is safe; review the error before retrying."
        default:
            "Preparing your task."
        }
    }
}
~~~

The glassEffect modifier and exact material composition must be verified in the selected SDK and target. Keep a plain semantic fallback for reduced transparency and platform variations. The status copy is the important contract.

## Recipe 9: test task transitions with fixtures

Drive the job reducer with deterministic events:

~~~swift
enum JobEvent: Equatable {
    case userStarted
    case submitted
    case queued
    case progress(Int)
    case expired
    case cancelled
    case outputPersisted
    case failed
    case relaunched
}

let expectedPath: [JobEvent] = [
    .userStarted,
    .submitted,
    .queued,
    .progress(25),
    .progress(100),
    .outputPersisted
]
~~~

Add fixtures for submission-not-permitted, no GPU, background inference not entitled, task cancellation from the system UI, force-quit, expired task, corrupt source, insufficient storage, thermal pause, duplicate relaunch, stale source revision, and review rejection.

## Recipe 10: verification stop list

Before claiming completion:

1. Compile the request and handler in the app target.
2. Inspect Info.plist identifiers and signed entitlements.
3. Test a foreground start, background transition, progress, cancellation, expiration, and completion.
4. Test force-quit/relaunch and checkpoint resume.
5. Run on named hardware for GPU/Neural Engine/resource claims.
6. Test system Live Activity and accessibility settings.
7. Validate privacy-safe title/subtitle, source retention, output deletion, and generated-proposal review.
8. Verify the release artifact separately from debugger-started task testing.

## Sources

- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [BGTaskScheduler](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler)
- [BGTask](https://developer.apple.com/documentation/backgroundtasks/bgtask)
- [BGAppRefreshTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgapprefreshtaskrequest)
- [BGProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgprocessingtaskrequest)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
- [Choosing background strategies for your app](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app)
- [Using background tasks to update your app](https://developer.apple.com/documentation/uikit/using-background-tasks-to-update-your-app)
- [BGTaskSchedulerPermittedIdentifiers](https://developer.apple.com/documentation/bundleresources/information-property-list/bgtaskschedulerpermittedidentifiers)
- [BGTaskSchedulerErrorCode.notPermitted](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler/error/code/notpermitted)
- [BGContinuedProcessingTaskRequest.Resources](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest/resources)
- [Background GPU Access](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.background-tasks.continued-processing.gpu)
- [Background Inference](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.background-tasks.continued-processing.inference)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [ProgressView](https://developer.apple.com/documentation/swiftui/progressview)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Vision](https://developer.apple.com/documentation/vision)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
