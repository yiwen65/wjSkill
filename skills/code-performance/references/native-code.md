# Native-code performance adapter

Read this adapter for C, C++, Rust, Swift, Objective-C, or other ahead-of-time
native binaries. Use it with either Static-only or measured mode; never let its
tool suggestions override the selected mode's execution boundary.

## Measured diagnosis

### Build and symbolization

Use a production-equivalent optimization level with usable debug information and
reliable stack unwinding. A typical Clang/GCC analysis build might include
`-O2` or `-O3`, `-g`, and `-fno-omit-frame-pointer`, but the correct flags depend
on the compiler, ABI, exception/RTTI policy, platform profiler, and production
configuration. Do not assume `-O3` is faster than `-O2`.

Record the effective compile and link commands. Evaluate LTO/ThinLTO when hot
paths cross translation units. Evaluate PGO only with versioned, representative
training workloads covering major and tail paths. Treat profile/source mismatch,
multi-threaded profile collection, code-size growth, and build-chain compatibility
as explicit risks.

Do not ship a generally distributed binary with `-march=native` unless the
deployment CPUs are deliberately identical to the build target. Choose a fixed
deployment ISA, runtime-dispatched variants, or a portable baseline with a small
specialized module.

### Tool routing

#### Linux

- Overall counters: `perf stat`; normalize cycles, instructions, misses, branches,
  switches, and faults per unit of useful work.
- CPU stacks and assembly: `perf record/report/annotate`.
- Waiting and system behavior: off-CPU tracing, `perf sched`, `perf lock`,
  `perf trace`, ftrace/trace-cmd, or bounded eBPF/bpftrace probes.
- Memory and sharing: `perf mem`, `perf c2c`, NUMA placement/maps, vendor tools.
- Allocation and lifetime: heaptrack, Massif, DHAT, or allocation sampling.
- Microarchitecture: Intel VTune or AMD uProf when supported by the target CPU.
- Generated code: Clang/GCC optimization remarks, objdump/LLVM disassembly, and
  `llvm-mca` as a static hypothesis generator rather than a benchmark.

Hardware events, sampling support, and counter definitions differ across CPU
models and kernels. Check multiplexing, lost events, skid, stack quality, and
whether the event exists before interpreting it.

#### Windows

Use WPR/WPA and ETW for system timelines; Visual Studio CPU Usage,
Instrumentation, Flame Graph, Memory Usage, and File I/O for process analysis;
Concurrency Visualizer for running/blocked transitions; VTune or uProf for
supported hardware counters; and MSVC vectorization/LTCG/PGO diagnostics for
generated code.

#### macOS

Use Instruments Time Profiler for CPU stacks, System Trace for scheduling and
system activity, Allocations/Leaks/VM Tracker for memory, CPU Counters or
Processor Trace when supported on the installed Apple hardware/toolchain, and
`xctrace` for command-line capture. Confirm feature availability against the
actual Xcode, macOS, and device.

### Vectorization and microarchitecture

Before intrinsics or assembly:

1. confirm the kernel's whole-program share and compute-bound evidence;
2. inspect compiler inline/vectorization success and missed-reason reports;
3. simplify aliasing, loop dependencies, calls, control flow, layout, and tail
   handling;
4. compare scalar and auto-vectorized generated code;
5. validate native hardware counters and end-to-end performance.

Static instruction models do not predict real cache misses or production
frequency behavior. Manual SIMD must define alignment, tails, exceptional values,
numerical tolerance, target features, dispatch, and a portable reference path.
Watch for spills, dependency chains, front-end/code-size pressure, gather/scatter,
cross-line accesses, and target-specific wide-vector frequency effects.

## Static-only focus

Inspect the language-specific candidates below, but treat compiler output, cache
behavior, instruction mix, contention, and material runtime cost as conditional
until existing artifacts or measured mode establish them.

### C++-specific boundaries

- Container choice depends on bytes accessed, locality, allocation, branch
  behavior, build/query amortization, worst case, and reference invalidation—not
  only asymptotic complexity.
- Continuous or blocked storage, hot/cold separation, and AoS/SoA changes often
  matter before SIMD. Preserve ownership, stable-reference, destruction, and
  exception semantics.
- `reserve`, buffer reuse, pools, arenas, and `std::pmr` can reduce allocation
  cost but may increase retained/peak memory or change release and destructor
  behavior.
- `std::hardware_destructive_interference_size` expresses a layout hint, not a
  runtime guarantee of cache-line size or absence of false sharing.
- `memory_order_relaxed` preserves atomicity but does not establish ordering
  across variables. Prove the happens-before requirements before weakening an
  ordering.
- `[[likely]]` and `[[unlikely]]` are hints. Prefer representative profile
  feedback over guessed branch frequencies.
- Never introduce undefined behavior for speed. Keep correctness checks and
  sanitizer/thread-sanitizer runs separate from absolute timing comparisons.

### Rust-specific boundaries

- Inspect avoidable `clone`, allocation, reference-count traffic, iterator
  materialization, bounds checks, dynamic dispatch, and synchronization, but do
  not infer generated instructions from surface syntax.
- Treat monomorphization and aggressive inlining as potential code-size and
  instruction-cache costs as well as optimization opportunities.
- For async code, separate executor scheduling, wake frequency, blocking work,
  task count, channel pressure, and allocator cost from the future's own CPU work.
- Preserve ownership, pinning, lifetime, panic, `Send`/`Sync`, and unsafe-code
  invariants. A faster unsafe path is invalid without the same safety contract.
- At FFI boundaries, attribute conversion, copying, allocation, callbacks, and
  ownership transfer to the side that performs them.

### Swift and Objective-C boundaries

- Inspect ARC retain/release traffic, autorelease-pool scope, copy-on-write
  materialization, bridging, value/reference semantics, collection growth, and
  string/data conversion without assuming they are material at runtime.
- For async and actor code, separate executor hops, task creation, suspension,
  contention, and blocking work from the function's own CPU time.
- Preserve ownership, actor isolation, cancellation, error, Objective-C runtime,
  and ABI behavior. Unsafe pointers or manual ownership are not default
  optimizations.
- Use the actual Apple platform and Instruments capabilities when measured mode
  is authorized; simulator results do not establish device performance.
