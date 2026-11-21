<a id="chapter-01-language-lifecycle"></a>

# CPN26 Language and Object Lifetime Specification

## 1. Language model

CPN26 is a native systems language with manual storage ownership, explicit object lifetime, C-like declarations, and configurable numerical and execution policies. CPN26 is the standard designation for this specification. A conforming implementation shall evaluate its core and selected optional capabilities according to the [core execution model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance) and produce the native representation required by the selected target contract.

Normative terminology shall use the core execution model's definitions. A normative example shall be interpreted with its named types and capabilities enabled. Configuration defaults and diagnostic dispositions have their sole definition in the [configuration specification](08_runtime_configuration.md#chapter-08-runtime-configuration).

## 2. Source and value model

An object declaration shall use the complete type before its name. Explicit initialization uses `Type name(arguments);`; deduction uses `auto name(expression);`. The pointer `this` designates the current receiver under its active class-layer contract.

```cpn
i32 data(10);
u64 capacity(4096);
auto next(data + 1);
```

The [type specification](10_types_functions_generics.md#chapter-10-types-functions-generics) defines type identity, qualification, values, callable types, and generic declarations. The [grammar specification](15_grammar_binding.md#chapter-15-grammar-binding) defines their complete source forms. Numerical expressions shall use the selected numerical policy and the corresponding named-operation contracts.

## 3. Objects, storage, and responsibility

An object lifetime, its backing storage, and its destruction responsibility are separate semantic entities. Each lifetime shall have one selected construction and destruction contract. Storage ownership shall identify the authority that releases or transfers the backing extent. A new construction in reused storage shall establish a new object generation.

The [construction specification](06_construction_execution.md#chapter-06-construction-execution) owns the state model, initialization plan, delegation, partial-construction rollback, destruction order, Whole, Cleanup, Abandon, and reconstruction transitions. The [memory specification](12_core_memory_control.md#chapter-12-core-memory-control) owns typed designation, storage access, and raw-memory obligations. Implementations shall preserve the functional state required by a selected operation; optional validation follows the resolved validation policy.

## 4. Execution profiles

The selected preset supplies defaults that explicit permitted bindings may replace. Release and MinimalRelease select ordinary native execution and local construction/effect analysis by default. Debug selects its configured diagnostic and analysis facilities. Definitions and imported interfaces shall retain their bound semantic policies across inlining, instantiation, and linking.

An explicitly named checked, try, report, exact, wrapping, or saturating operation shall perform its specified operation. Explicit Strict, Reproducible, accuracy, quota, atomic, ownership, and ABI contracts likewise remain functional requirements under every preset. The abstract-machine observability rules determine which state and events each selected contract exposes.

The compiler shall classify an admitted but unproved ordinary programmer obligation using the configured ANOMALY policy. Required grammar, type, generic-constraint, constant-evaluation, and explicitly selected proof rules shall retain their stated acceptance requirements. Analysis effort shall refine knowledge and diagnostics while preserving source-bound initialization plans and selected definitions.

## 5. Failure and publication boundaries

The [error and recovery specification](28_error_and_recovery.md#chapter-28-error-recovery) defines language exceptions, terminal outlets, and their cleanup consequences. Each construction, call, Result operation, and ownership transition shall publish its result at its specified commit point. Cleanup shall execute on the continuing paths selected by that failure contract.

The [module specification](11_modules_compilation.md#chapter-11-modules-compilation) defines declaration ownership and separate compilation. Static objects shall follow the dependency, cancellation, commitment, and reverse-logical-destruction rules in the configuration specification. Foreign symbols, calls, layouts, and shared-library lifetime shall satisfy their selected [native interoperability contract](09_native_interoperability.md#chapter-09-native-interoperability).

