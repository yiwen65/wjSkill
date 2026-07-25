# Structured-output prompts

Read this file only when the target output feeds a parser, evaluator, API,
automation, extraction pipeline, or strict schema.

Preserve exact:

- field names and nesting;
- types, required fields, and enums;
- nullability and missing-data behavior;
- error behavior;
- serialization and Markdown requirements.

Check that the contract is satisfiable for every allowed input. In particular,
compare required fields, allowed values, nullability, inference rules, and the
possibility that source data is absent.

If the source can omit a required value while the prompt forbids `null`,
omission, inference, and defaults, follow the core **Resolve conflicts** rule.
Do not silently widen an enum, add an error object, choose a default, or make a
required field optional.

Keep explanations outside machine-readable output unless the schema explicitly
provides a field for them.
