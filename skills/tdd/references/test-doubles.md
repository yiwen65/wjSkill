# Test Doubles

Use test doubles only where real dependencies would make the test
nondeterministic, unsafe, prohibitively slow, or dependent on an unavailable
external system.

## Boundary rule

Prefer real domain and application modules. Consider a double for:

- remote APIs and third-party services;
- time, randomness, and generated identifiers;
- process, network, or hardware boundaries;
- destructive side effects;
- databases or filesystems when an isolated test database or temporary
  directory is not practical.

Wrap third-party SDKs behind a small owned adapter and fake that adapter in
behavior tests. Verify the real adapter separately with an integration or
contract test when its correctness matters.

## Choose the least coupled double

- Use a **stub** to provide a boundary result needed by the scenario.
- Use a **fake** when a lightweight working implementation expresses the
  boundary more clearly, such as an in-memory repository.
- Use a **spy** only when the interaction itself is part of the observable
  contract, such as emitting exactly one external payment request.

Assert the caller's public result or intended side effect whenever possible.
Avoid assertions on internal call order, private methods, or incidental call
counts.

Keep double setup specific to the scenario. If it contains branching that
reimplements production behavior, replace it with a simpler fake or test at a
more appropriate seam.
