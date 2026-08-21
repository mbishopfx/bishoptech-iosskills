# BackgroundTasks and continued-processing recipes

## How to use these recipes

These are compile-oriented route sketches. Verify deployment availability, target
capabilities, Info.plist identifiers, entitlement approval, process lifetime,
resource options, and completion APIs against the selected Xcode/iOS SDK.

A background API can provide runtime; it does not prove that a job will run at a
specific time, survive every termination, use a GPU, or finish a domain commit.
Every recipe needs a checkpoint, cancellation path, and ordinary foreground
reconciliation.

## Recipe 1: background job record

Use a durable record so the next process can reconstruct work without relying on
an in-memory task object.

~~~swift
import Foundation

struct JobRecord: Codable, Sendable {
    enum State: String, Codable, Sendable {
        case requested
        case queued
        case running
        case backgrounded
        case committing
        case completed
        case canceled
        case expired
        case failed
        case needsReview
    }

    let id: UUID
    let kind: String
    let inputIDs: [String]
    let inputRevision: String
    var state: State
    var completedUnits: Int64
    var totalUnits: Int64?
    var checkpoint: String?
    var resultRevision: String?
    var modelIdentifier: String?
    var updatedAt: Date
}
~~~

Persist through the app's selected storage layer. Do not treat UserDefaults,
App Groups, or a task identifier as authorization.

## Recipe 2: register scheduled task handlers

Register handlers early in the main app launch sequence. Keep task identifiers
stable and ensure they appear in the target's permitted identifier list.

~~~swift
import BackgroundTasks

enum BackgroundTaskID {
    static let refresh = "com.example.focus.refresh"
    static let maintenance = "com.example.focus.maintenance"
    static let continued = "com.example.focus.continued"
}

func registerBackgroundTasks() {
    BGTaskScheduler.shared.register(
        forTaskWithIdentifier: BackgroundTaskID.refresh,
        using: nil
    ) { task in
        guard let task = task as? BGAppRefreshTask else { return }
        Task {
            await BackgroundCoordinator.shared.handleRefresh(task)
        }
    }

    BGTaskScheduler.shared.register(
        forTaskWithIdentifier: BackgroundTaskID.maintenance,
        using: nil
    ) { task in
        guard let task = task as? BGProcessingTask else { return }
        Task {
            await BackgroundCoordinator.shared.handleMaintenance(task)
        }
    }

    BGTaskScheduler.shared.register(
        forTaskWithIdentifier: BackgroundTaskID.continued,
        using: nil
    ) { task in
        guard let task = task as? BGContinuedProcessingTask else { return }
        Task {
            await BackgroundCoordinator.shared.handleContinued(task)
        }
    }
}
~~~

If the selected deployment target does not expose a route, register only the
available handler behind an availability check. A widget extension may schedule,
but the main app owns registration.

## Recipe 3: schedule a short refresh

Use a refresh request for small, deferrable work. The system chooses the actual
launch time.

~~~swift
func scheduleRefresh() {
    let request = BGAppRefreshTaskRequest(
        identifier: BackgroundTaskID.refresh
    )
    request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)

    do {
        try BGTaskScheduler.shared.submit(request)
    } catch {
        BackgroundLog.record(.scheduleFailed)
    }
}
~~~

The date is a hint. If the refresh updates a widget, the widget must remain
truthful when the request is delayed or never delivered.

## Recipe 4: schedule deferred maintenance

Use BGProcessingTask for work that can wait, such as database maintenance or
batch preparation.

~~~swift
func scheduleMaintenance() {
    let request = BGProcessingTaskRequest(
        identifier: BackgroundTaskID.maintenance
    )
    request.requiresNetworkConnectivity = false
    request.requiresExternalPower = true
    request.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 60)

    do {
        try BGTaskScheduler.shared.submit(request)
    } catch {
        BackgroundLog.record(.scheduleFailed)
    }
}
~~~

Verify the selected request properties and capability requirements in the target
SDK. Do not treat requiresExternalPower as a guarantee that the task will run.

## Recipe 5: handle a scheduled task with expiration

Use a cancellation-aware operation and report completion through the task API.

~~~swift
actor BackgroundCoordinator {
    func handleRefresh(_ task: BGAppRefreshTask) async {
        scheduleRefresh()

        let operation = RefreshOperation()
        task.expirationHandler = {
            operation.cancel()
        }

        do {
            try await operation.run()
            task.setTaskCompleted(success: true)
        } catch is CancellationError {
            task.setTaskCompleted(success: false)
        } catch {
            BackgroundLog.record(.workFailed)
            task.setTaskCompleted(success: false)
        }
    }

    func handleMaintenance(_ task: BGProcessingTask) async {
        let operation = MaintenanceOperation()
        task.expirationHandler = {
            operation.cancel()
        }

        do {
            try await operation.run()
            task.setTaskCompleted(success: true)
        } catch {
            task.setTaskCompleted(success: false)
        }
    }
}
~~~

The exact async bridging and isolation must be adapted to the project. Ensure
the operation's cancellation actually stops child work and releases resources.

## Recipe 6: create a continued-processing request

Create the request only after a foreground action with a bounded, user-approved
input set.

~~~swift
func startUserJob(job: JobRecord) throws {
    let request = BGContinuedProcessingTaskRequest(
        identifier: BackgroundTaskID.continued,
        title: "Analyze selected items",
        subtitle: "Preparing \(job.inputIDs.count) items"
    )

    if BGTaskScheduler.supportedResources.contains(.gpu) {
        request.requiredResources = .gpu
    }

    request.strategy = .queue

    do {
        try BGTaskScheduler.shared.submit(request)
    } catch {
        throw BackgroundStartError.couldNotStart
    }
}
~~~

The request title/subtitle is user-facing system copy. Keep it localized and
privacy-safe. Requesting GPU requires the selected device support and the
documented Background GPU Access entitlement.

Some SDKs may expose the submission strategy or resource names differently.
Confirm the selected SDK before treating this sketch as compile evidence.

## Recipe 7: fail-fast submission policy

Use fail when an immediate start is part of the product promise and the app can
surface a foreground retry.

~~~swift
func startImmediately(job: JobRecord) throws {
    let request = BGContinuedProcessingTaskRequest(
        identifier: BackgroundTaskID.continued,
        title: "Export selected items",
        subtitle: "Ready to begin"
    )
    request.strategy = .fail

    do {
        try BGTaskScheduler.shared.submit(request)
    } catch {
        throw BackgroundStartError.resourcesUnavailable
    }
}
~~~

Do not spin and resubmit in a loop. A failed request should leave a requested or
blocked job record and a clear retry route.

## Recipe 8: run continued work with progress

A continued task can report progress and update its system title/subtitle.

~~~swift
func handleContinued(_ task: BGContinuedProcessingTask) async {
    let progress = task.progress
    progress.totalUnitCount = 100

    var expired = false
    task.expirationHandler = {
        expired = true
    }

    for step in 0...100 {
        if expired || Task.isCancelled {
            await JobStore.shared.markExpiredOrCanceled()
            task.setTaskCompleted(success: false)
            return
        }

        do {
            try await processUnit(step)
            progress.completedUnitCount = Int64(step)
            task.updateTitle(
                "Analyzing selected items",
                subtitle: "\(step)% complete"
            )
            await JobStore.shared.checkpoint(completed: Int64(step))
        } catch {
            await JobStore.shared.markFailed(category: "unit")
            task.setTaskCompleted(success: false)
            return
        }
    }

    await JobStore.shared.commitIfCurrent()
    task.setTaskCompleted(success: true)
}
~~~

This is a lifecycle sketch. Use synchronization around the expiration flag and
check cancellation at every real unit boundary. Report success only after the
durable commit reaches the product's completion boundary.

## Recipe 9: cancellation-aware async operation

Make cancellation propagate into child tasks and framework requests.

~~~swift
func runCancellableWork(
    operation: @escaping () async throws -> Void,
    cancelResources: @escaping () -> Void
) async throws {
    try await withTaskCancellationHandler {
        try await operation()
    } onCancel: {
        cancelResources()
    }
}
~~~

Do not use a detached task for the core job unless its lifetime and cancellation
are explicitly owned. The expiration handler should cause the same cleanup route
as a person pressing cancel.

## Recipe 10: checkpointed batch processing

Commit a single unit only after the output is valid and the source revision is
still current.

~~~swift
func processBatch(
    jobID: UUID,
    inputIDs: [String],
    sourceRevision: String
) async throws {
    for inputID in inputIDs {
        try Task.checkCancellation()

        let checkpoint = await JobStore.shared.checkpoint(for: jobID)
        if checkpoint?.contains(inputID) == true {
            continue
        }

        guard await SourceStore.shared.revision(for: inputID) == sourceRevision else {
            await JobStore.shared.markNeedsReview(jobID)
            return
        }

        let proposal = try await LocalAnalyzer.shared.propose(inputID)
        try await JobStore.shared.commit(
            jobID: jobID,
            inputID: inputID,
            sourceRevision: sourceRevision,
            proposal: proposal
        )
    }
}
~~~

The real commit must be idempotent on job ID, input ID, source revision, and
result hash. Do not mark a checkpoint before the output is durable.

## Recipe 11: local AI workload boundary

Keep model availability and proposal validation explicit.

~~~swift
struct LocalProposal: Sendable {
    let inputID: String
    let sourceRevision: String
    let modelIdentifier: String
    let label: String
    let needsReview: Bool
}

func analyzeSelectedItems(
    job: JobRecord
) async throws -> [LocalProposal] {
    guard await ModelAvailability.shared.isReady else {
        throw AIWorkError.modelUnavailable
    }

    var proposals: [LocalProposal] = []

    for inputID in job.inputIDs {
        try Task.checkCancellation()

        let result = try await LocalAnalyzer.shared.propose(
            inputID,
            sourceRevision: job.inputRevision
        )

        proposals.append(result)
        await JobStore.shared.recordProposal(result)
    }

    return proposals
}
~~~

A proposal is not an approved record. Use a review route before external,
irreversible, financial, health, communication, or destructive side effects.

## Recipe 12: resource-aware GPU fallback

Check support and entitlement policy before requesting GPU work. The task request
alone does not prove the device will run the GPU path.

~~~swift
enum ComputeRoute {
    case gpu
    case cpu
    case foregroundRetry
    case deferred
}

func chooseComputeRoute() async -> ComputeRoute {
    guard BGTaskScheduler.supportedResources.contains(.gpu) else {
        return .cpu
    }

    guard await EntitlementStore.shared.backgroundGPUAccessEnabled else {
        return .cpu
    }

    guard await ThermalStore.shared.allowsIntensiveWork else {
        return .deferred
    }

    return .gpu
}
~~~

Use the actual entitlement/resource inspection route supported by the selected
project. Measure latency, memory, energy, and thermal behavior on representative
physical devices.

## Recipe 13: update a widget projection after commit

Projection refresh belongs after the domain commit.

~~~swift
import WidgetKit

func finishJobAndRefreshSurface(
    jobID: UUID,
    resultRevision: String
) async throws {
    try await JobStore.shared.finalize(jobID, resultRevision: resultRevision)
    try await ProjectionStore.shared.writeCurrentProjection()

    WidgetCenter.shared.reloadTimelines(
        ofKind: "com.example.focus.widget"
    )
}
~~~

A reload request is a hint. The widget must show a truthful current/stale state
if the system delays it.

## Recipe 14: reconcile after relaunch

On launch, reconcile job records with any known task/activity state.

~~~swift
func reconcileJobsAfterLaunch() async {
    let jobs = await JobStore.shared.activeJobs()

    for job in jobs {
        switch job.state {
        case .requested, .queued, .running, .backgrounded, .committing:
            if await JobStore.shared.hasCommittedResult(for: job.id) {
                await JobStore.shared.markCompleted(job.id)
            } else {
                await JobStore.shared.markNeedsReview(job.id)
            }
        default:
            continue
        }
    }

    await ProjectionStore.shared.writeCurrentProjection()
}
~~~

Never assume a task object survives a process restart. Reconciliation must be
based on durable job state and domain truth.

## Recipe 15: safe system title builder

Keep system progress copy short, localized, and lock-safe.

~~~swift
func systemTitle(for job: JobRecord, isPrivate: Bool) -> String {
    if isPrivate {
        return "Processing selected items"
    }

    switch job.state {
    case .requested:
        return "Preparing selected items"
    case .queued:
        return "Waiting for device resources"
    case .running, .backgrounded:
        return "Processing selected items"
    case .committing:
        return "Saving results"
    case .completed:
        return "Processing complete"
    case .canceled:
        return "Processing canceled"
    case .expired:
        return "Processing paused"
    case .failed:
        return "Processing needs attention"
    case .needsReview:
        return "Results ready to review"
    }
}
~~~

Use localization and pluralization in the actual target. Never place prompts,
private filenames, contact names, exact locations, or internal IDs into a system
title or subtitle.

## Recipe 16: development-only task simulation boundary

Apple documents private debugger commands for starting and terminating tasks
during development on physical devices. Keep them outside release code.

~~~swift
#if DEBUG
func installDevelopmentTaskSimulationNotes() {
    // Development instructions belong in the test plan or local documentation.
    // Do not call private simulation selectors from the shipped binary.
}
#endif
~~~

A Debug-only source block is not automatically safe if it enters an archive.
Scan the release source and archive before distribution.

## Recipe 17: proof fixture

Use synthetic inputs to exercise progress, cancellation, and partial commit.

~~~swift
struct BackgroundFixture {
    static let job = JobRecord(
        id: UUID(uuidString: "00000000-0000-0000-0000-000000000148")!,
        kind: "local-analysis",
        inputIDs: ["fixture-1", "fixture-2", "fixture-3"],
        inputRevision: "fixture-revision-1",
        state: .running,
        completedUnits: 1,
        totalUnits: 3,
        checkpoint: "fixture-1",
        resultRevision: nil,
        modelIdentifier: "fixture-model",
        updatedAt: .now
    )
}
~~~

The fixture proves deterministic state logic only. It does not prove system
scheduling, GPU resources, process lifetime, accessibility, or release behavior.

## Source checklist

Before adapting any recipe, verify:

- selected SDK and deployment target;
- BGTaskScheduler registration timing;
- permitted identifier configuration;
- Background Modes and Background GPU Access capability;
- request strategy/resource names;
- task title/subtitle localization;
- expiration/completion API;
- task cancellation and app-switcher termination;
- model/media/network lifecycle;
- checkpoint/commit/revision policy;
- widget/activity projection;
- physical-device/archive/release evidence.

## Sources

- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks/)
- [BGTaskScheduler](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler)
- [BGAppRefreshTask](https://developer.apple.com/documentation/backgroundtasks/bgapprefreshtask)
- [BGProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgprocessingtask)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados/)
- [Using background tasks to update your app](https://developer.apple.com/documentation/uikit/using-background-tasks-to-update-your-app)
- [Choosing Background Strategies for Your App](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app)
- [Starting and Terminating Tasks During Development](https://developer.apple.com/documentation/backgroundtasks/starting-and-terminating-tasks-during-development)
- [Background GPU Access](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.background-tasks.continued-processing.gpu)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Testing](https://developer.apple.com/documentation/testing)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
