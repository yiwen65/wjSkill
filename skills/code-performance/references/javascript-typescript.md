# JavaScript and TypeScript performance adapter

Use this adapter for JavaScript or TypeScript running in Node.js or a browser.
Identify which runtime owns the workload; do not transfer Node.js, browser, or
specific engine conclusions to another environment without evidence.

## Static-only focus

Inspect applicable paths for:

- algorithmic work, nested collection operations, repeated traversal, temporary
  arrays/objects, object spread, string and buffer conversion, JSON work, regex,
  cloning, and serialization;
- synchronous CPU or I/O on an event-loop path, promise/timer/task proliferation,
  microtask chains, unbounded concurrency, queue growth, missing backpressure, and
  worker/message-transfer cost;
- listener, timer, closure, cache, DOM, and object-graph retention;
- per-item network/database/file calls, request waterfalls, batching, connection
  limits, and retry amplification;
- browser layout/style invalidation, DOM read/write interleaving, rendering, asset
  and network dependencies when frontend responsiveness is the actual target;
- stable object shapes, dynamic property access, polymorphism, and typed-array or
  buffer opportunities only as JIT/code-generation hypotheses.

TypeScript types do not exist as equivalent runtime checks after compilation.
Inspect the emitted target, bundler/transpiler settings, module format, source-map
quality, and production minification when they affect the executable artifact.

## Measured diagnosis

For Node.js, combine user-visible throughput/latency with:

- `node:perf_hooks` marks/measures and event-loop or request timing when available;
- the stable `node:inspector`/V8 CPU and heap profilers or project-approved
  diagnostic tooling;
- allocation/heap, GC, event-loop delay/utilization, async-resource, worker,
  libuv/thread-pool, I/O, and native-addon evidence as the symptom requires.

For browsers, use the installed browser's performance, memory, network, and
rendering tooling with representative devices and production assets. Separate
laboratory traces from field/user metrics and distinguish scripting, style,
layout, paint, compositing, network, and main-thread queueing.

Warm the same paths before steady-state JIT comparisons, repeat fresh processes
or pages, and record runtime/engine, flags, hardware, bundle, and source maps.
Keep inspector endpoints private and measure instrumentation overhead.

## Interpretation boundaries

- Source patterns do not prove optimization, deoptimization, inline-cache state,
  hidden-class behavior, or generated machine code.
- High event-loop utilization does not identify the responsible work; low CPU can
  still hide I/O, timers, queueing, or worker waits.
- A heap snapshot and retained graph can perturb the process and do not measure
  every native buffer or external allocation.
- Worker threads trade main-thread responsiveness for startup, message transfer,
  memory, synchronization, and scheduling cost.
- Preserve promise ordering, cancellation, error propagation, stream
  backpressure, browser compatibility, and rendering semantics.
