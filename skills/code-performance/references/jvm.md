# JVM performance adapter

Use this adapter for Java, Kotlin, Scala, and other JVM applications. Treat the
JVM version, collector, heap policy, JIT tier, container limits, and framework
configuration as part of the performance environment.

## Static-only focus

Inspect applicable paths for:

- repeated boxing/unboxing, temporary collections, stream or sequence pipelines,
  string construction, regex, reflection, proxying, and serialization;
- collection choice, hashing, resizing, comparator work, repeated traversal, and
  lazy operations that are consumed more than once;
- allocation inside high-multiplicity paths, retained references, caches without
  bounds, listeners, class loaders, thread locals, and coroutine/future chains;
- broad synchronization, contended-looking shared state, blocking calls on
  executor or event-loop threads, queue bounds, task granularity, and pool sizing;
- virtual/interface call shape, exception-heavy control flow, method size, and
  inlining or escape-analysis preconditions.

Source can establish allocation sites and synchronization structure, but it
cannot prove JIT inlining, scalar replacement, escape analysis, deoptimization,
machine code, GC pressure, or runtime hotness. Keep those as conditional risks.

## Measured diagnosis

Record warm-up state and separate startup, class loading, JIT compilation, and
steady state. Do not compare a cold interpreter/tiered run with a warmed candidate
as if the code change caused the difference.

Use available project and platform tooling to distinguish:

- application CPU from JIT/compiler threads, GC, safepoints, blocking, and I/O;
- allocation rate from live set, retained heap, promotion, and native/off-heap
  memory;
- GC pause from concurrent GC CPU and mutator slowdown;
- monitor contention, executor starvation, queueing, coroutine scheduling, and
  virtual-thread or carrier behavior;
- interpreted, compiled, deoptimized, and uncommon paths when JIT evidence is
  available.

JDK Flight Recorder and Mission Control can provide JVM events for CPU, memory,
latency, allocation, GC, threads, locks, class loading, and exceptions. Choose a
recording profile and duration proportional to the question, measure collection
overhead, and preserve the exact JDK/JVM flags. Use the project's established JVM
benchmark harness when available; ensure results escape dead-code elimination,
include warm-up and forks, and do not treat a microbenchmark as service evidence.

## Interpretation boundaries

- A high allocation rate is not automatically a leak; distinguish short-lived
  churn, promotion, retained objects, and non-heap memory.
- A GC pause metric alone does not measure total GC cost or application
  throughput loss.
- Changing collector, heap size, compiler flags, or tiering changes the runtime
  experiment, not only the code; compare each variable separately.
- Kotlin coroutines and Scala futures may move work across executors. Attribute
  wait and scheduling time across the logical request rather than one thread.
- Reflection, streams, lambdas, and virtual calls are not inherently slow. Report
  them only when multiplicity and runtime evidence make their cost material.
- Android ART, ahead-of-time/mobile compilation, and device power or thermal
  behavior differ from a server JVM. Record the actual Android runtime and use
  platform tooling rather than assuming HotSpot/JFR semantics.
