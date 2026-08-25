# Python performance adapter

Use this adapter for Python applications. Record the interpreter implementation
and version, environment and dependency versions, native extensions, process and
thread model, GC configuration, and deployment worker settings when relevant.

## Static-only focus

Inspect applicable paths for:

- algorithmic complexity, Python-level loops over large data, repeated attribute
  or mapping lookup, repeated parsing, string concatenation, temporary containers,
  comprehensions, generators, and materialization boundaries;
- object churn, copying, serialization, cache bounds, import-time work, global
  state, and accidental retention through closures, registries, or callbacks;
- blocking I/O inside an event loop, unbounded task creation, synchronous work in
  async paths, thread/process fan-out, queue bounds, and cancellation;
- ORM/RPC/file request multiplicity, per-item I/O, batching, and data conversion;
- transitions among Python, native extensions, subprocesses, and remote services,
  including copies, marshaling, and ownership of the observed time.

Do not claim that a vectorized library, native extension, alternative interpreter,
threading, multiprocessing, or async rewrite is faster without workload evidence.
The GIL or interpreter implementation must not be assumed from the `.py` suffix.

## Measured diagnosis

Choose evidence according to the boundary:

- benchmark small deterministic operations with an established framework or
  `timeit`, then return to component and end-to-end measurements;
- use `cProfile`/`profile` for deterministic call statistics when their overhead
  is acceptable, or an available sampling profiler when lower perturbation and
  native-stack visibility are needed;
- use `tracemalloc` for traced Python allocation snapshots and differences, and
  process/OS tooling for RSS, native allocations, mappings, and child processes;
- trace event-loop delay, task/request timelines, I/O waits, worker queues, and
  external calls for async or service latency;
- profile native-extension code with its own runtime adapter when evidence crosses
  into C, C++, Rust, GPU, BLAS, database, or another external execution engine.

Separate import/startup, cache warm-up, adaptive interpreter behavior, and steady
state. Repeat across fresh processes and preserve the exact interpreter and
environment; deterministic profilers are not benchmark timers.

## Interpretation boundaries

- Python allocation tracing does not account for every native allocation or
  process mapping.
- CPU-bound thread scaling depends on the actual interpreter and time spent in
  native code that may release or bypass interpreter locks.
- Multiprocessing can trade CPU parallelism for startup, memory, serialization,
  and inter-process communication cost.
- A function with high cumulative time may be waiting on callees or external I/O;
  separate own CPU, descendant work, and wall time.
- Preserve exception behavior, ordering, iterator laziness, numerical semantics,
  process isolation, and cancellation when proposing faster paths.
