---
name: code-performance
description: Diagnose and, when authorized, optimize code performance through static-only analysis or reproducible measurements, with dedicated routing for native code, JVM, .NET, Go, Python, and JavaScript/TypeScript runtimes. Use when the primary question concerns latency, throughput, CPU, memory, allocation, I/O, contention, scalability, or a performance regression, including read-only analysis when execution is unavailable or out of scope. Do not use for functional defects or incidental performance comments during ordinary code review.
---

# Code Performance

## Outcome

Turn a performance complaint into either:

- a verified, minimal optimization with measured end-to-end benefit and no
  unacceptable correctness or resource regression; or
- a bounded diagnosis that identifies the strongest supported bottleneck,
  remaining unknowns, and the next discriminating measurement; or
- a static-only report of concrete code facts and conditional performance risks,
  without presenting unmeasured candidates as runtime bottlenecks.

For measured work, use a causal evidence loop:

`contract -> baseline -> attribution -> model -> intervention -> A/B validation`

## Preserve authority and evidence

- Interpret requests to inspect, diagnose, profile, explain, or recommend as
  read-only authority. Change code, build settings, or production configuration
  only when the user authorizes optimization or a fix.
- Preserve repository instructions and unrelated user changes. Keep temporary
  benchmark artifacts outside the worktree unless they are requested deliverables
  or durable regression protection.
- For measured work, distinguish `MEASURED` observations, `SUPPORTED INFERENCE`,
  and `UNKNOWN`. A hot stack, counter, static code smell, or plausible mechanism
  is not alone a proven root cause. Static-only work uses the evidence classes in
  its dedicated reference.
- Never invent a speedup, target, benchmark result, hardware capability, or tool
  availability. Without representative runtime measurements, report optimization
  opportunities as hypotheses rather than performance conclusions.
- Ask only when a missing workload, target environment, invariant, or authority
  boundary would materially change the investigation or proposed change.

## Select one runtime adapter

Identify the runtime from build manifests, entry points, deployment files, and
the actual execution boundary rather than file extensions alone. Read exactly
one matching adapter before entering Static-only or measured mode:

- C, C++, Rust, Swift, Objective-C, or another ahead-of-time native binary:
  [references/native-code.md](references/native-code.md)
- Java, Kotlin, Scala, or another JVM language:
  [references/jvm.md](references/jvm.md)
- C#, F#, Visual Basic, or another .NET language:
  [references/dotnet.md](references/dotnet.md)
- Go: [references/go.md](references/go.md)
- Python: [references/python.md](references/python.md)
- JavaScript or TypeScript in Node.js or a browser:
  [references/javascript-typescript.md](references/javascript-typescript.md)

For JNI, P/Invoke, cgo, Python native extensions, Node.js addons, RPC, or another
cross-runtime boundary, start with the adapter at the observed entry point. Read
one additional adapter only when evidence shows that the suspected cost crosses
that boundary. Keep time, allocations, copies, queueing, and ownership on the
correct side instead of attributing all cost to the caller.

When the authorized target contains several independent runtime components,
analyze one component at a time and load its adapter only while tracing that
component. Do not preload every language reference merely because the repository
is polyglot.

For an unlisted or ambiguous runtime, use the generic workflow without loading a
nearby adapter by analogy. State the missing specialization and inspect current
project tooling before naming commands. Ask only if choosing the wrong runtime
would materially change evidence collection or authorization.

Runtime adapters refine signals and tool choice; they do not override the user's
scope, the Static-only prohibition on execution, or the evidence gates below. In
Static-only mode, apply only the adapter's static focus and interpretation
boundaries; in measured mode, apply its measured guidance and interpretation
boundaries.

## Select the operating mode

Use **Static-only diagnosis** when any of these conditions holds:

- the user explicitly limits the task to reading code, build files, tests, or
  existing static artifacts, or forbids target execution, builds, benchmarks,
  profiling, or instrumentation;
- the executable, target environment, or representative workload is unavailable
  or outside the authorized scope, but the user still wants a code-performance
  assessment; or
- the request is specifically a static performance review of code and does not
  report an observable runtime symptom to reproduce.

Do not select Static-only merely because measurements have not yet been collected
when representative execution is available, authorized, and needed to diagnose a
reported runtime problem. In that case, establish the measured baseline below.

For Static-only diagnosis, read and follow
[references/static-only-diagnosis.md](references/static-only-diagnosis.md). Do not
execute or build the target, instrument it, modify it, or continue into the
measured evidence loop. Use only the files and existing static artifacts permitted
by the request, return the static report defined there, and stop.

Otherwise use **Measured diagnosis or optimization** and continue below.

## Recover the measured performance contract

Establish the smallest contract needed for a meaningful comparison:

- **Workload:** input sizes and distributions, request mix, concurrency, load
  model, cold-start or steady-state mode, and representative dataset.
- **Platform:** hardware, topology, OS/runtime, dependencies, and relevant power,
  frequency, storage, or network policy.
- **Build:** revision and worktree state, compiler/runtime and versions, effective
  build/link flags, allocator, and profile-guided artifacts.
- **Targets:** throughput, latency percentiles, CPU cost per unit, memory,
  allocations, I/O, capacity, or another user-visible performance oracle.
- **Invariants:** output correctness and tolerances, determinism, deadlines,
  resource ceilings, portability, binary size, and maintenance constraints.

Use the current repository and environment to fill harmless gaps. If the target
platform or representative workload is unavailable, continue only as far as the
evidence permits and state the limitation.

Read [references/benchmarking.md](references/benchmarking.md) when designing or
auditing a benchmark, claiming a win or regression, or adding a performance gate.

## Run the measured evidence loop

### 1. Protect correctness and establish the baseline

Identify the existing behavioral tests, output comparison, numerical tolerance,
thread-safety invariant, or other correctness oracle before optimizing. Keep
sanitizer, tracing, and instrumentation results separate from native performance
comparisons when they materially alter execution.

Reproduce the performance symptom with fixed workload, environment, revision,
command, and measurement boundaries. Measure both:

- a user-visible result such as throughput or latency distribution; and
- normalized machine cost such as cycles, instructions, core-seconds,
  allocations, bytes moved, lock wait, or syscalls per unit of work.

Obtain a known-good version, input, configuration, or expected budget when
practical. Save raw samples and enough environment metadata to repeat the run.

### 2. Locate the first cost divergence

Compare good and bad executions across workload sizes, concurrency levels,
pipeline stages, revisions, or configurations. Find the earliest boundary where
the relevant time or resource cost diverges.

Use complementary evidence as applicable:

1. **Time attribution:** on-CPU samples, off-CPU waits, and request/thread traces.
2. **Resource attribution:** instructions and cycles, cache/TLB/memory traffic,
   allocations, lock contention, scheduling, syscalls, faults, and I/O queues.
3. **Generated-code attribution:** inlining/vectorization reports, assembly,
   code layout, dependency chains, and compiler/runtime configuration.

Do not infer that a wide flame-graph frame is chronological, that low CPU means
no CPU issue, or that high CPU proves useful computation. Check measurement
loss, counter multiplexing, incomplete stacks, observer overhead, and whether
the profiler changed the workload.

Read [references/bottleneck-playbook.md](references/bottleneck-playbook.md) for
signal combinations, discriminating measurements, and intervention choices.

### 3. Model the limit and test hypotheses

Maintain a small ranked hypothesis set. For each candidate, state the evidence it
explains, contrary evidence, the metric that must move if it is causal, and the
cheapest one-variable experiment that distinguishes it from alternatives.

Use the model appropriate to the evidence:

- estimate whole-system benefit from hotspot share before local optimization;
- compare arithmetic intensity with sustained bandwidth and compute limits for
  data-parallel kernels;
- plot throughput, latency, efficiency, waiting, and resource cost across
  concurrency instead of judging one thread count;
- scan input size or working-set size to expose complexity and cache transitions.

Call a bottleneck proven only when the evidence links the workload to the first
cost divergence and a discriminating experiment changes the predicted metric and
user-visible outcome. Otherwise retain it as an inference.

### 4. Apply the earliest authorized high-value intervention

Let measured benefit, implementation cost, correctness risk, portability, and
maintenance decide the order. The default search order is:

1. use a production-equivalent optimized build with usable symbols;
2. remove unnecessary work and improve algorithmic complexity;
3. reduce data movement, working set, allocation, and object churn;
4. reduce serialization, copies, small I/O, and syscall frequency;
5. remove unnecessary sharing, rebalance work, and reduce contention;
6. evaluate whole-program optimization, profile feedback, and code layout;
7. enable compiler auto-vectorization and improve branch behavior or ILP;
8. use manual SIMD, ISA dispatch, assembly, or post-link specialization only for
   stable, important kernels with a portable reference path.

Implement the smallest change that attacks the demonstrated dominant cost. Do
not bundle unrelated refactoring or apply broad flags, lock-free structures,
padding, batching, prefetching, `-march=native`, or forced inlining without
evidence and compatibility analysis.

### 5. Verify the result

Compare baseline and candidate with the same workload, environment, build class,
and measurement boundaries. Use multiple independent process starts and
randomized or interleaved A/B order when noise could affect the decision.

Verify each applicable layer:

1. **Correctness:** behavioral output, edge cases, numerical tolerance, races,
   and failure semantics remain valid.
2. **Performance:** raw samples show an effect larger than measurement
   uncertainty and any project-defined practical threshold.
3. **Resources:** tail latency, peak memory, allocations, CPU, I/O, power, code
   size, and overload behavior have no unacceptable tradeoff.
4. **Mechanism:** the predicted hotspot or resource cost moved as expected;
   re-profile because the bottleneck may migrate.
5. **System:** component and end-to-end results agree for representative input;
   broaden platforms or duration only when risk justifies it.
6. **Diff:** changes remain limited to the supported optimization and regression
   protection.

Treat `not run` as different from `passed`. Do not call a local microbenchmark a
product improvement until the relevant end-to-end result supports it.

## Stop conditions

Stop when the performance budget is met, remaining global benefit is too small,
the system is near a demonstrated capacity bound, the effect is below uncertainty,
risk exceeds likely benefit, or the next step requires unavailable evidence or
new authority. Re-baseline and restart attribution when the bottleneck moves.

## Report the result

For Static-only diagnosis, use the report contract in
[references/static-only-diagnosis.md](references/static-only-diagnosis.md) instead
of inventing empty baseline, profiler, or A/B sections.

For measured diagnosis or optimization, lead with the outcome and include only
supported sections:

```markdown
## Performance contract
Workload, platform, build, targets, invariants, and important gaps.

## Baseline and bottleneck
Reproduction command, raw/summary metrics, first cost divergence, causal chain,
and rejected alternatives.

## Optimization
Authorized change, expected mechanism, scope, and tradeoffs.

## Verification
Comparable before/after results, uncertainty, correctness and resource checks,
commands, and checks not run.

## Residual risks
Unrepresentative inputs or platforms, remaining assumptions, new bottleneck, and
the next discriminating action.
```

Use exact units, metric definitions, commands, versions, and artifact locations
when they are needed to make the conclusion reproducible.
