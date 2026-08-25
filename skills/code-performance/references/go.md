# Go performance adapter

Use this adapter for Go programs. Record the Go version, target OS/architecture,
`GOMAXPROCS`, GC configuration, PGO input, cgo use, container limits, and effective
build flags when they can change the result.

## Static-only focus

Inspect applicable paths for:

- slice and map growth, per-item allocation, interface conversion, string/byte
  conversion, formatting, reflection, temporary buffers, and retained capacity;
- values that may escape, closures, goroutine captures, pointer-heavy structures,
  and ownership crossing goroutines, while treating actual escape decisions as
  generated-code evidence rather than source fact;
- goroutine-per-item patterns, unbounded fan-out, timers/tickers, channel capacity,
  mutex scope, shared maps, atomics, select loops, cancellation, and leak paths;
- blocking syscalls or cgo on latency-sensitive paths, per-record I/O,
  serialization, batching, and backpressure;
- defer or recover in high-multiplicity paths and generic/interface abstraction,
  without assuming compiler treatment or material cost.

Static-only mode may inspect existing escape or compiler reports but must not run
`go build` or generate them.

## Measured diagnosis

Use Go's built-in lanes according to the signal:

- `go test -bench` with allocation reporting for isolated code, preserving the
  workload, package setup, process repetitions, and raw results;
- CPU, heap/allocs, goroutine, block, and mutex profiles through `runtime/pprof`,
  `net/http/pprof`, or project-approved collection;
- `go tool trace` for scheduler latency, goroutine execution, GC, syscalls, and
  utilization rather than primary CPU-hotspot attribution;
- runtime metrics and GC/scheduler diagnostics for allocation, heap, pause,
  goroutine, and scheduling behavior;
- compiler escape/inlining reports only in an authorized build experiment.

Collect interfering profiles separately: precise memory, block, mutex, CPU, and
runtime tracing can perturb one another. Measure collection overhead, secure any
profiling endpoint, and do not expose or attach to production without authority.

## Interpretation boundaries

- Heap allocation samples, live heap, retained RSS, and total allocation volume
  answer different questions.
- A goroutine stack in a blocked state does not prove harmful contention; relate
  blocked duration and multiplicity to the workload.
- More goroutines do not imply more parallel work; plot throughput, latency,
  runnable work, blocking, and scheduler behavior across `GOMAXPROCS`.
- Race-enabled builds and heavily instrumented traces are correctness or mechanism
  evidence, not native absolute-performance baselines.
- PGO requires representative CPU profiles; do not infer benefit from enabling it
  or from a narrow microbenchmark profile.
