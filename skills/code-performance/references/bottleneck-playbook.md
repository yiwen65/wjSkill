# Bottleneck localization playbook

Read this reference when choosing the first discriminating measurement or
deciding which class of intervention fits the observed signals.

## Interpret signal combinations

| Symptom | First evidence | Cross-check | Leading causes |
|---|---|---|---|
| High wall time, low CPU | Off-CPU profile and system/request trace | futex, I/O wait, run-queue delay, faults | Locks, I/O, scheduling, empty queues, paging |
| High CPU and rising instructions/unit | CPU profile and input-size scan | superlinear instruction curve | Complexity, repeated parsing/search, useless work |
| Rising cycles/unit with stable instructions | Hardware counters and memory profile | low IPC, cache/TLB/DRAM or remote NUMA | Layout, pointer chasing, bandwidth, NUMA |
| High branch miss or bad speculation | Branch counters, annotated code, profile feedback | data-dependent branches, indirect calls | Unpredictable control flow or unrepresentative layout/profile |
| Throughput plateaus at few threads | Lock/off-CPU analysis and concurrency trace | wait time, futex, switches, queue imbalance | Serial stages, global locks, tiny tasks, starvation |
| More cores slow down without lock wait | Cache-to-cache, bandwidth, NUMA | shared-line transfers, remote traffic | False sharing, shared atomics, coherence traffic |
| Mean is stable but P99 rises | End-to-end trace and scheduler/I/O timeline | queue depth, faults, slow I/O, periodic pauses | Queueing, batching delay, lock convoy, background work, throttling |
| RSS high but live heap modest | VM mappings plus heap timeline | mmap, page cache, allocator arenas, fragmentation | Non-heap mappings or memory not returned to OS |
| Allocation routines are hot | Allocation sampling and allocations/unit | small short-lived objects, cross-thread free | Container growth, temporaries, object graphs, allocator contention |
| Many tiny syscalls | Syscall/I/O trace | low bytes/call and frequent flush | Per-record I/O, repeated encoding, small buffers |
| Simple source produces expensive code | Optimization reports and annotated assembly | missed inline/vectorization, spills, copies | Alias, ABI, target ISA, code layout, control flow |
| Runs fluctuate or reverse | Raw samples across process starts | migration, frequency, temperature, layout | Measurement bias or unstable environment |

A single signal can have several explanations. Choose a measurement whose
possible outcomes distinguish the leading candidates, and change one primary
variable per experiment.

## Match interventions to the dominant cost

### Unnecessary work and complexity

Inspect repeated traversal, recomputation, conversion, parsing, and the growth of
instructions/unit with input size. Compare construction and lookup cost, memory,
access locality, worst case, invalidation semantics, and the real read/write mix;
Big-O alone does not choose a data structure.

### Data movement, allocation, and working set

Consider contiguous or blocked storage, hot/cold separation, AoS/SoA changes,
indices instead of pointer graphs, capacity planning, reusable buffers, fewer
temporaries, and lifetime-based arenas. Validate bytes touched, allocations,
cache/TLB behavior, peak RSS/live heap, invalidation, destruction, and memory
growth. Do not assume a faster allocator cures excess allocation.

### Concurrency and sharing

Prefer removing shared state, sharding by worker/key/NUMA node, local accumulation
with batch merge, shorter/less frequent critical sections, and better task
granularity before lock-free structures. Validate throughput and P99 across
thread counts, lock wait, run-queue delay, per-thread work, cache-line traffic,
remote memory, shutdown semantics, ordering, and starvation.

Replacing locks with atomics can turn sleep into coherence traffic. Relaxed
ordering requires a proven memory-order invariant. Padding and thread pinning are
target-specific experiments, not universal fixes.

### I/O, serialization, and batching

First remove duplicate encoding, parsing, copying, and allocation; then reuse
buffers, combine small operations, use scatter/gather or batch APIs, and introduce
asynchrony only when it fits the service model. Bound queue depth, batch size, and
maximum wait. Sweep batch parameters and choose a throughput/tail-latency/memory
Pareto point; the throughput maximum is not automatically correct.

### Compiler and instruction-level work

Confirm that the dominant cost is a stable compute kernel. Inspect optimization
reports and generated code before forcing inline, unroll, vector width, prefetch,
or branch hints. Improve alias clarity, data layout, loop dependencies, control
flow, and call boundaries before intrinsics or assembly. Validate on every target
CPU that must run the artifact and retain a correct portable fallback.

## Estimate whether the work is worth doing

For a region taking fraction `p` of total time and local speedup `s`, estimate:

`whole_system_speedup = 1 / ((1 - p) + p / s)`

The infinite local-speedup ceiling is `1 / (1 - p)`. Recompute after each
successful change because the dominant cost can move.

For data-parallel kernels, compare achieved work rate against both sustained
memory bandwidth times operational intensity and attainable compute throughput.
Use measured sustained limits for the target system, not vendor peak numbers.
Far below both ceilings can indicate dependency, control-flow, front-end,
contention, or imbalance limits.
