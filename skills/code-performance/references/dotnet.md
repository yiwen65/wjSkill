# .NET performance adapter

Use this adapter for C#, F#, Visual Basic, and other .NET applications. Record the
runtime version, architecture, GC mode, tiered-compilation policy, ReadyToRun or
NativeAOT state, container limits, and framework configuration when relevant.

## Static-only focus

Inspect applicable paths for:

- boxing, closures, delegates, iterator/state-machine allocation, LINQ pipelines,
  repeated enumeration, reflection, dynamic dispatch, and exception-heavy flow;
- string and array churn, formatting, serialization, large-object allocation,
  pooling lifetime, pinned buffers, and avoidable copies at managed/native edges;
- synchronous blocking inside async paths, `Task` proliferation, thread-pool
  starvation risks, broad locks, shared mutable state, channels, and queue bounds;
- database or RPC fan-out, repeated materialization, per-item I/O, and missing
  batching or backpressure;
- `Span<T>`, stack allocation, pooling, unsafe code, and P/Invoke proposals whose
  lifetime or correctness requirements may outweigh an unmeasured benefit.

Source does not prove tiered JIT output, stack allocation, escape behavior,
devirtualization, GC generation, thread-pool starvation, or runtime hotness.

## Measured diagnosis

Use the narrowest available diagnostic lane:

- `dotnet-counters` or equivalent runtime metrics for first-level CPU, exception,
  allocation, GC, thread-pool, and contention signals;
- `dotnet-trace`/EventPipe, Visual Studio, or PerfView for CPU stacks, runtime
  events, async activity, GC, contention, and request timelines;
- `dotnet-gcdump`, dumps, or heap tooling for live-object and root analysis when
  memory retention is the question;
- the repository's established benchmark harness for isolated code, with warm-up,
  multiple processes, and tiering configuration recorded.

Separate startup and steady-state results. Account for tier promotion,
ReadyToRun-to-JIT transitions, dynamic PGO, GC mode, and thread-pool adaptation.
Measure profiler or event-provider overhead and do not enable production attach,
diagnostic ports, or dump collection without appropriate authority.

## Interpretation boundaries

- Allocation rate, managed heap size, working set, and retained live objects are
  different metrics.
- A GC dump can perturb the process and may trigger a full collection; it is not a
  zero-impact production measurement.
- `async` is not inherently faster, and `ValueTask`, pooling, `Span<T>`, or unsafe
  code is not a default optimization. Validate call frequency, completion mode,
  lifetime, and API constraints.
- High thread count can reflect blocking, pool growth, or workload design rather
  than useful parallelism.
- Preserve async exception/cancellation behavior, disposal, pinning, ownership,
  and P/Invoke ABI semantics in every recommendation.
