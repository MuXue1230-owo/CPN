<a id="chapter-08-runtime-configuration"></a>

# CXXN Configuration, Exceptions, and Static Lifetime Specification

## 1. Normative conventions

The [core execution model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance) defines normative requirements, binding, observations, and transformation permissions. This chapter owns configuration resolution, preset defaults, diagnostic categories, exception records, and static-domain policy.

An **image** is one executable or one independently loaded shared-library lifetime domain. A **provider** is a selected implementation of a capability with a versioned contract. A **configuration capability** declares that a facility is available; an **operation policy** selects behavior when using that facility. Availability does not imply native hardware support.

The compiler shall resolve configuration before binding the affected construct and retain the effective values and provider contracts as semantic compilation state. Compiled definitions shall retain their bound behavior and identity. Chapter 21 defines the internal representation and optional external publication of that state.

## 2. Configuration grammar and resolution

### 2.1 Configuration declarations

The configuration grammar is:

```ebnf
configuration-declaration = "configuration", "{", { binding, ";" }, "}", ";";
configured-declaration = "configured", "(", binding-list, ")", declaration;
configured-block = "configured", "(", binding-list, ")", compound-statement;
configured-expression = "configured", "(", binding-list, ")", "(", expression, ")";
binding-list = binding, { ",", binding };
binding = key, "=", configuration-value;
key = metadata-word, { ".", metadata-word };
metadata-word = ? An identifier-shaped metadata token, including a reserved keyword spelling ?;
configuration-value = metadata-word | string-literal | integer-literal
                    | "[", [ value-list ], "]";
value-list = configuration-value, { ",", configuration-value };
```

The compiler shall interpret configuration values as compile-time metadata and integer metadata as exact mathematical integers. Keys shall be case-sensitive and unique within each binding list or configuration declaration. A key shall resolve to the standard schema or a provider-identified extension beginning with `vendor.`; an unresolved or duplicate key yields ERROR.

Metadata words include Boolean and enum-like spellings such as true, false, and default. Reserved spellings are admitted in these metadata paths and values without becoming ordinary program identifiers. The [consolidated grammar](15_grammar_binding.md#chapter-15-grammar-binding) supplies tokenization and decoration rules; the selected key schema supplies each value's interpretation.

A project configuration file, when supplied, shall be named `cxxn.config` and contain configuration declarations. A compiler request may supply the same project bindings directly. A source-file configuration declaration shall precede the declarations it governs. It applies until the end of the enclosing file or declared configuration region. A configured declaration applies to that declaration and its lexical body. A configured block applies to its body. A configured expression applies to that expression, including its implicit operation policies, and does not change the surrounding scope. The compilation request shall bind the source edition under Chapter 21 before source grammar selection.

```text
configuration {
    preset = Release;
    target = "x86_64-linux-gnu";
    numeric.integer.widths = [8, 16, 32, 64];
    numeric.float.formats = [f32, f64];
};

configured(numeric.integer.overflow = wrapping) {
    u32 next(counter + 1);
}

auto distance(configured(numeric.fp.profile = strict,
                         numeric.fp.rounding = toward_zero) (left / right));
```

The preset table in Section 2.4 supplies ordinary-operation defaults. `numeric.integer.overflow` shall select the policy of ordinary integer arithmetic, shifts, negation, absolute value, and increment/decrement. Native uses the target-domain contract in Chapter 02; the other strategies use their specified domain validation and projection. Typing and literal materialization follow their source rules.

An explicit interface such as `checked_add`, `try_add`, `wrapping_add`, or `exact_cast` shall bind its declared strategy. A configured Strict/Reproducible operation shall bind the corresponding stronger numerical observations. These selections implement the explicit functional-contract rule in the core model.

### 2.2 Hierarchy

The inheritance order, from least local to most local, is:

1. The selected target descriptor and preset.
2. The project manifest.
3. The package manifest.
4. The module declaration.
5. The source-file declaration.
6. The enclosing declaration.
7. The enclosing configured block.
8. The configured expression or explicit operation policy.

For a key admitted at the affected scope, the nearest explicit binding shall win. A preset supplies defaults; an explicit binding at that scope overrides them. A list binding shall replace the inherited list. A use shall resolve against the final capability set; an unavailable required member yields ERROR.

A dependency shall retain its own resolved configuration. Generic specialization shall combine the definition's contract with its declared specialization parameters. Import and instantiation use these published bindings.

A profile-dependent default shall be calculated from the effective profile after explicit bindings are resolved. Changing `numeric.fp.profile` therefore recalculates its otherwise-default controls and relaxation set. Explicit inherited controls remain explicit and require a compatible combination or a local override. The semantic configuration record shall contain the resulting values.

### 2.3 Resolution boundaries

| Key class | Earliest permitted override | Frozen boundary | Required behavior |
| --- | --- | --- | --- |
| Target architecture, object format, pointer model, C ABI, C++ ABI provider | Project or independent image | Image | Conflicting direct linkage is `ERROR`. |
| Source identifier profile and Unicode data version | Compilation request/project/package or selected module map before tokenization | Compilation-unit or module source identity | All source for the bound owner shall use its selected identifier profile. |
| Module compilation, separate compilation, and external contract export | Compilation request/project/package before source binding | Compilation artifact | The selected compilation and publication capabilities shall govern the entire artifact. |
| Exception ABI version and process failure profile | Project or independent image | Image | All participating CXXN frames use the same exception boundary contract. |
| Enabled type families, providers, allocating facilities | Project through declaration | First affected declaration | An exported type retains its declared representation and provider identity. |
| Integer overflow, numeric conversion, rounding, FP and Complex operation defaults | Project through expression | Operation binding | Explicit operation policies have priority. |
| Default literal materialization | Project through expression | Literal binding | A typed expression shall retain its established type. |
| Static initialization scheduling and identity namespace | Project or independent image | Static initialization domain | Object-local annotations may add dependencies and cancellation contracts. |
| Allocator and resource budgets | Project through explicit object/resource domain | Allocation or ownership transition | Ancestor hard limits and existing allocation ownership remain binding. |
| Diagnostic emission, suppression, and promotion | Project through expression | Diagnostic site | Suppression cannot supply missing semantics or remove required runtime behavior. |
| Optional construction and effect analysis | Project through declaration | Analysis of the bound definition | Analysis depth shall change evidence and build context; source typing and initialization-plan selection shall retain their prescribed rules. |
| Callable value contracts and effect signatures | Project through affected declaration, with explicit call-site diagnostics only | Exported declaration/function type boundary | An importer cannot alter the callee's pre/postcondition policy, ABI or promise; effect annotations cannot erase language-invariant lifetime/trap rules. |
| Optional raw-memory validation and debug assertions | Project through declaration/block/operation where admitted | Operation binding | Required checked semantics and destruction state remain binding. |
| Standard-library, atomic, thread, and task providers | Project through capability declaration | Used type/provider ABI or execution context | An enabled module does not create a global allocator, thread, or executor instance. |

Each override shall resolve at an admitted boundary in the table. An override below its frozen boundary yields ERROR. Configuration scope `all` makes the relevant boundary available throughout the language. An exported type identity shall retain its bound layout across those scopes.

### 2.4 Standard keys

The following key families form the standard configuration surface. A provider may expose additional values only under a versioned capability declaration.

| Key | Standard values or domain | Default in the ordinary presets |
| --- | --- | --- |
| `preset` | `Debug`, `Release`, `MinimalDebug`, `MinimalRelease`, `Custom` | Explicit project selection; `Debug` if omitted. |
| `target` | Registered target-descriptor name | Explicit toolchain target. |
| `compilation.modules` | Boolean | `false` in every standard preset; explicitly enabled for named module syntax and imports. |
| `compilation.separate` | Boolean | `false` in every standard preset; requires `compilation.modules = true`. |
| `tooling.contract_export` | Boolean | `false` in every standard preset; explicitly enabled for Chapter 29 interchange. |
| `source.identifiers` | `ascii`, `unicode` | `unicode`; frozen before compilation-unit tokenization. |
| `source.unicode_version` | Supported pinned Unicode data version | `"17.0.0"`. |
| `memory.raw_validation` | `available`, `contract` | Debug: `available`; Release: `contract`; mandatory checked operations unchanged. |
| `library.modules` | Explicit list of standard-module names as strings | Target-declared available standard module set; minimal presets select their nonallocating subset. |
| `library.provider` | Versioned standard-library provider identity | Explicit toolchain provider, if the library is enabled. |
| `library.debug_assertions` | Boolean | Debug: `true`; Release: `false`. |
| `generic.higher_kinds` | Boolean | `false` in every standard preset; explicitly enabled. |
| `generic.associated_entities` | Boolean | `false` in every standard preset; explicitly enabled. |
| `generic.max_constructor_arity` | Positive integer compilation-resource limit | `16` when higher kinds are enabled. |
| `generic.max_normalization_nodes` | Positive integer | `100000` for ordinary and advanced constraint checking. |
| `generic.max_solver_steps` | Positive integer | `1000000` for ordinary and advanced constraint checking. |
| `generic.max_witness_depth` | Positive integer | `128` when associated entities are enabled. |
| `generic.max_instantiations` | Positive integer | `1000000` for ordinary and advanced specialization work. |
| `meta.reflection` | Boolean | Debug/Release: `true`; minimal presets: `false`. |
| `meta.provider` | Versioned reflection provider or `none` | Target toolchain provider if enabled. |
| `meta.max_handles` | Positive integer | `100000` when enabled. |
| `meta.max_query_steps` | Positive integer | `1000000` when enabled. |
| `meta.generate` | Boolean | `false`; explicitly enabled. |
| `meta.generate_layout` | Boolean | `false`; requires `meta.generate = true` when enabled. |
| `meta.max_emissions` | Positive integer | `10000` when enabled. |
| `meta.max_generation_steps` | Positive integer | `1000000` when enabled. |
| `meta.max_generation_depth` | Positive integer | `128` when enabled. |
| `meta.max_generation_bytes` | Positive integer | `67108864` when enabled. |
| `meta.syntax_provider` | Versioned typed-syntax provider or `none` | `none` until generation is enabled. |
| `contracts.enabled` | Boolean | Debug/Release: `true`; minimal presets: `false` unless enabled. |
| `contracts.validation` | `check`, `prove`, `document`, `trusted` | Debug: `check`; Release/Minimal: `document`. |
| `contracts.invariants` | `check`, `document`, `disabled` | Debug: `check`; Release: `document`; Minimal: `disabled`. |
| `contracts.trusted_assumptions` | Boolean | `false`. |
| `construction.analysis` | `local`, `interprocedural` | Debug: `interprocedural`; Release: `local`. |
| `effects.inference` | `local`, `interprocedural` | Debug: `interprocedural`; Release: `local`. |
| `effects.opaque_default` | `conservative` | `conservative`. |
| `effects.diagnostics` | `default`, `strict` | `default`. |
| `exceptions.language` | Boolean | `true`. |
| `exceptions.failure_profile` | `aggregate`, `terminate` | Debug: `aggregate`; Release: `terminate`. |
| `exceptions.secondary.inline_capacity` | Nonnegative integer | `4`. |
| `exceptions.secondary.max_records` | Integer at least inline capacity | `256`. |
| `exceptions.secondary.dynamic_storage` | Boolean | `true` when aggregation and an allocator are enabled. |
| `exceptions.secondary.exhaustion` | `retain_primary` | `retain_primary`. |
| `diagnostics.minimum` | `INFO`, `WARNING`, `ANOMALY`, `ERROR`, `none` | `WARNING`; `ERROR` remains compilation-blocking. |
| `diagnostics.promote` | List of categories or diagnostic codes | Empty. |
| `diagnostics.suppress` | List of non-error codes | Empty. |
| `numeric.integer.widths` | Enabled positive storage widths | Supported members of `[8,16,32,64]`, including `32`. |
| `numeric.integer.overflow` | `native`, `checked`, `wrapping`, `saturating` | Debug: `checked`; Release: `native`. |
| `numeric.literal.integer_default` | Enabled fixed-width signed type | `i32`. |
| `numeric.literal.real_default` | Enabled real floating type | `f64` when the floating family is enabled. |
| `numeric.literal.real_rounding` | One of the five standard rounding modes | `nearest_ties_even`; compile-time literal formation only. |
| `numeric.float.formats` | Explicit format list | Supported members of `[f32,f64]`; other formats are opt-in. |
| `numeric.fp.profile` | `native`, `strict`, `reproducible`, `fast` | Debug: `strict`; Release: `native`. |
| `numeric.fp.rounding` | `current` or one of the five standard rounding modes | Native: `nearest_ties_even`; other profiles: `current`. |
| `numeric.fp.initial_rounding` | One of the five standard rounding modes | `nearest_ties_even`. |
| `numeric.fp.subnormal` | `current`, `preserve`, or a versioned provider policy | Native: the provider's native policy; other profiles: `current`. |
| `numeric.fp.initial_subnormal` | `preserve` or an explicitly named relaxed provider policy | `preserve`. |
| `numeric.fp.result_mask` | Set of the five floating events | `[Invalid, DivideByZero, Overflow]`. |
| `numeric.fp.trap_mask` | `current` or a set of the five floating events | Native: empty; other profiles: `current`. |
| `numeric.fp.initial_trap_mask` | Set of the five floating events | Empty. |
| `numeric.fp.require_finite` | Boolean | `false`. |
| `numeric.fp.relaxations` | Resolved set of provider-supported relaxations | Native: the provider's published default set; other profiles: empty. |
| `numeric.complex.profile` | `component_exact`, `scalar_steps`, provider name | `scalar_steps`; component operations retain the bound scalar policy. |
| `numeric.exact.families` | Subset of `Fixed`, `Rational`, `BigInt`, `BigDecimal` | Empty; explicitly enabled by the project. |
| `numeric.provider` | Versioned provider identifier | Target descriptor's conforming provider. |
| `numeric.software_fallback` | Boolean | `false` unless explicitly permitted by the target preset. |
| `atomic.software_fallback` | Boolean | `false`. |
| `atomic.memory_model` | `cxxn_v1` | `cxxn_v1`. |
| `atomic.provider` | Versioned native/explicit fallback provider identity | Target's declared conforming atomic provider. |
| `thread.provider` | Provider identifier or `none` | `none` unless explicitly selected by the target/project. |
| `thread.stack_bytes` | Positive byte count or `provider_default` | `provider_default`; actual bound exposed by the provider. |
| `thread.tls_initialization` | `eager_domain` | `eager_domain`. |
| `task.executor_provider` | Provider identifier or `none` | `none`; an enabled provider still requires an explicit Context instance. |
| `task.cancellation` | `cooperative`, `finish` | `cooperative`. |
| `static.schedule` | `serial`, `custom_parallel` | `serial`. |
| `static.workers` | Positive integer | `1`; greater values require `custom_parallel`. |
| `static.identity_namespace` | Nonempty UTF-8 string | The compilation request's logical root identity, or the selected module map's logical package identity. |
| `resources.allocator` | Registered allocator identity | No implicit allocator in a minimal preset. |
| `resources.hard_bytes` | Nonnegative integer or `unbounded` | Declared resource domain limit. |
| `resources.temporary_bytes` | Nonnegative integer or `unbounded` | Separate temporary domain limit. |
| `resources.quota_mode` | `reserved`, `soft` | Explicit for an allocating domain. |

Floating event identifiers shall use the canonical FPFlag cases in Chapter 04. A configured set shall denote a subset of those cases.

Preset resolution shall establish the availability of its required core capabilities. Literal materialization shall retain its selected default type and require that type's availability. A custom profile that disables this required type yields ERROR at materialization. Providers shall declare representation support and arithmetic support separately; an arithmetic use shall satisfy its selected result contract.

An optional family's preset entry shall select the ordinary policy used when that family and the required operation are enabled. Complex scalar steps shall inherit the effective scalar arithmetic and observation policies. Exact Complex and mathematical capability selection shall follow the operation/format/control/delivery claims defined by Chapters 05 and 18. Their descriptors and dependencies shall become required through explicit selection or an actual requiring use under Chapter 21's conformance model.

`native` shall select the published `numeric.native` provider capability. Its resolved contract shall state native domain outcomes, environment requirements, NaN/subnormal behavior, numerical transformation permissions, and approximation behavior. `fast` shall use its explicitly resolved relaxation set. The semantic configuration record shall contain each selected relaxation, including contraction, reassociation, reciprocal/elementary approximation, or signed-zero freedom. Finite-only assumptions require a separately selected assumption contract.

The [contracts and effects](24_contracts_and_effects.md#chapter-24-contracts-effects) policy supplies phase-specific verification and effect annotations. Optional instrumentation shall follow its enabled setting; explicit operations shall realize their declared function. Published signatures remain definition-bound. Local construction/effect analysis shall use source control flow and bound summaries. Interprocedural mode may inspect available callees as additional evidence. Both modes shall use the same source-bound initialization plan and mandatory type/constraint decisions.

### 2.4.1 Advanced generic capability resolution

`generic.higher_kinds` enables Chapter 26's finite recursive constructor kinds, constructor packs, partial applications, and inline constructor mappings. `generic.associated_entities` enables associated requirements, structural witnesses, and explicit conformance catalogues. Both capabilities shall require an explicit true binding in every standard preset. Ordinary type/constant generics and their ordinary structural constraints shall remain part of Core. Importing a bound advanced interface shall require its declared capability and retain its static type representation.

The maximum constructor arity shall limit the positions of each realized constructor application, including its expanded pack, under Chapter 26's budget rule. Each finite recursive kind shall use the configured normalization and solver resources. Normalization, solver, witness, and instantiation exhaustion shall report the exhausted compilation resource with the semantic question unresolved. Public recursive kind signatures, captured partial arguments, constructor closure identities, conformance-catalogue identities and priorities, selected structural or explicit witnesses, and relevant provider identities shall enter the definition's semantic interface record. Equivalent admitted instances shall retain their representation and layout identity across private compilation-budget changes.

Ordinary Core constraint checking shall use the normalization, solver-step, and instantiation limits with their standard defaults even when both advanced capabilities are disabled. Witness-depth limits shall apply to selected associated witnesses, and constructor-arity limits shall apply to selected higher kinds.

### 2.4.2 Compilation and publication capabilities

`compilation.modules` shall select Chapter 11's named ownership, import, partition, and module graph rules. `compilation.separate` shall select reusable CXXN semantic interfaces and their separate-compilation consistency rules, with module support as its dependency. Joint compilation of named modules shall require the first capability alone. A Core compilation shall use the single-unit root environment defined by Chapter 21.

`tooling.contract_export` shall select Chapter 29's external contract records, canonical JSON encoding, and SHA-256 identity projections. It shall operate independently of module compilation and separate compilation. A compiler shall satisfy disabled publication through its internal semantic records and the selected target's ordinary object representation. A separate-compilation provider may use its declared private interface representation. A request for standardized external records shall require the export capability.

Configuration shall establish these capabilities before the compilation artifact is bound. Their false defaults shall leave ordinary native object emission, foreign declarations, and internal semantic validation available. Declaration and expression policy overrides shall retain the artifact's selected compilation/publication mode.

### 2.5 Floating control resolution

The configuration rounding names are `nearest_ties_even`, `nearest_ties_away`, `toward_zero`, `toward_positive_infinity`, and `toward_negative_infinity`. Their library enum spellings are respectively `NearestTiesEven`, `NearestTiesAway`, `TowardZero`, `TowardPositiveInfinity`, and `TowardNegativeInfinity`.

For rounding, subnormal policy, and trap mask, an explicit operation argument shall take precedence over resolved configuration. `current` shall select the active FPControl field; a fixed lexical value supplies that operation's override. Initial-control keys shall initialize a newly selected observed root context. A Native root shall use its provider's environment contract. Thread/task initialization shall follow ExecutionInit in Chapter 17, including its Native and observed alternatives. Ordinary function entry shall retain the active context unless a bound operation or boundary selects an explicit change.

An operation whose bound contract selects observed numerical status shall apply Chapter 04's local-event, restoration, and delivery protocol. Explicit control selection shall retain the interface's declared observation mode. A report exposing an Unobservable alternative shall apply its function-specific status-preservation contract. Ordinary Native execution shall use its provider's compatible native environment and unobserved-status contract. A strong boundary that needs isolation shall supply that isolation through its selected provider/adapter. An incompatible requested control combination yields a capability error. Operation-local reporting begins after argument evaluation.

### 2.6 Minimal presets

`MinimalDebug` and `MinimalRelease` shall inherit their corresponding failure profile and diagnostic semantics and enable the target descriptor's declared minimal scalar set. Language exceptions, allocating numeric families, task-context support, custom parallel startup, and software numeric/atomic fallback shall enter the capability closure when explicitly enabled.

A use shall bind an enabled facility and its support dependencies. The core execution model defines capability-proportional runtime support. Numeric Result values and the target terminal outlet remain available independently of language exceptions. MinimalRelease inherits Native ordinary execution; MinimalDebug inherits Checked/Strict defaults within the enabled scalar subset.

## 3. Manifests and diagnostic requirements

### 3.1 Semantic records and optional manifest export

Each compilation shall retain the semantic facts needed for its bound operations: logical owner identity, source identifier/Unicode profile, target contract, enabled representations, provider contracts, used layout and calling conventions, selected exception profile, support dependencies, numerical defaults, and static initialization ownership. The facts required by optional reflection or generation shall include their selected projection contracts, grants, emitted identities, and compile-time requirements. Chapter 21 owns their abstract meaning and permits an implementation's internal representation. Declaration ownership shall use the single-unit root or selected module map. Static ordering shall use its separate namespace and logical tuple.

With `tooling.contract_export = true`, a requested standard export shall expose its applicable semantic records through the [public contract schemas](29_public_contract_schemas.md#chapter-29-public-contract-schemas). That capability shall implement the exact export fields, canonical encoding, version, identity projections, and fingerprint algorithm. With the capability disabled, internal semantic binding and native object generation shall complete using their own representations.

A fingerprint comparison may accelerate rejection and cache lookup where a fingerprint is present. Type and symbol equivalence shall compare the complete relevant identity or resolve possible collisions. Code-cache identity shall account for behavior-affecting optional instrumentation. Diagnostic settings, timestamps, physical build directories, semantics-preserving optimization levels, and debug-symbol presence shall remain build context; selected Chapter 29 export shall place them in its prescribed projections.

Direct exchange shall match every contract relevant to the shared boundary, including an exchanged record's layout. Modules may exchange an explicitly identical `i32` or pointer contract while retaining different internal rounding defaults or allocators. A selected adapter shall perform its declared representation, ownership, exception, or numerical-policy translation.

### 3.2 Diagnostic classes

`ERROR` means that the construct has no permitted meaning under the selected grammar, type, lifetime, or provider contract, or that a rule explicitly requires rejection of a provably failing construct. `ANOMALY` reports a higher-risk pattern with defined execution semantics or an unproven programmer obligation. `WARNING` reports an ordinary, lower-risk issue. `INFO` supplies optional explanatory output.

Display filtering shall order the categories `INFO`, `WARNING`, `ANOMALY`, `ERROR`. `ANOMALY` shall remain independently selectable and nonblocking by default. Promotion to ERROR shall prevent code generation for that compilation unit. Suppression shall affect emission while the operation retains its bound execution contract.

| Code | Default | Required condition |
| --- | --- | --- |
| `CFG001` | ERROR | Unknown key, invalid value, duplicate binding, or forbidden override scope. |
| `CFG002` | ERROR | Required capability or enabled provider is unavailable. |
| `GEN001` | ANOMALY | One or more explicit conformance heads match, every matching explicit candidate is established False, and associated structural fallback succeeds. Chapter 27 defines the resolution event and required evidence. |
| `ABI001` | ERROR | Incompatible direct layout, calling convention, or exception boundary. |
| `LIFE001` | ERROR | Proven duplicate construction or provably impossible initialization frontier. |
| `LIFE002` | ERROR | Proven use of a value outside its permitted lifetime. |
| `LIFE003` | ANOMALY | Required lifetime or destruction responsibility cannot be proved statically and the construct has a defined dynamic check or programmer contract. |
| `LIFE004` | ANOMALY | Explicit abandonment bypasses a nontrivial cleanup obligation. |
| `LIFE005` | ERROR | Transfer during Destroying, member Abandon in Cleanup, or another expressly forbidden phase transition. |
| `NUM001` | ERROR | Provable failure under a rule requiring compile-time rejection. |
| `NUM002` | WARNING | Explicitly selected lossy conversion whose loss is not a higher-risk contract violation. |
| `NUM003` | ANOMALY | Declared fast numerical assumptions or low-level representation assumptions are not proved. |
| `META001`–`META010` | ERROR | Required static-reflection/generation availability, visibility, staging, emission, reproducibility, or budget contract violated, according to the meta specifications. |
| `STAT001` | ERROR | Static dependency cycle or conflicting stable identity. |
| `STAT002` | ANOMALY | Claimed independent task or external-effect contract cannot be verified. |
| `EXC001` | ANOMALY | A callback required to be nonthrowing has an unproved effect contract. |
| `EXC002` | ERROR | A required nonthrowing callback is proved to escape with an exception. |

A frontend shall reject unmet grammar, type, required-proof, or ABI requirements. It shall accept an admitted programmer-contract obligation with its configured ANOMALY when ordinary optional analysis leaves that obligation unknown. Analysis depth shall affect evidence and diagnostics, while the bound operation determines execution.

## 4. Exception records and matching

### 4.1 Unified record and lifetime

A language exception shall own one primary payload under one stable primary-record identity. Appending secondary failures shall preserve that payload's identity and dynamic type. A primary handler shall observe the original payload or the base-subobject reference selected by its type match.

`ExceptionAggregate` shall view the unified record, including its primary and retained secondary records. Each retained secondary shall own its exception record with its type and payload. Appending it shall preserve the primary record.

The [error and recovery interfaces](28_error_and_recovery.md#chapter-28-error-recovery) own the exact source-visible observation, traversal, retain, and release declarations and their error outlets. This section defines the underlying record identity and ownership protocol; Section 5 defines its opaque ABI.

The aggregate interface and secondary traversal shall expose read-only views. A separately selected primary handler may modify a non-const primary reference under that type's permissions.

A propagation path shall own one active reference. Handler entry shall transfer it to the handler context until exit completes. Bare rethrow shall acquire a propagation reference while preserving references owned by active handlers. A nested handler may catch that propagation and return to a still-live outer payload view. Final reference retirement shall dispose of the payload. Shared mutable observation shall follow the ordinary concurrency contract.

The [error and recovery specification](28_error_and_recovery.md#chapter-28-error-recovery) defines source ownership, throw-operand admission and construction, precise type matching, active handler context, and explicit exception capture. Its `std.error` module is the optional source wrapper for this record protocol; the ABI below remains a raw transport with operation-defined ownership. The source `ExceptionAccessError` has the single allocation-free, nonthrowing case `InvalidIndex`.

When a record is shared across execution agents, reference bookkeeping and secondary publication/observation are internally synchronized. Each propagation's sequenced cleanup order is preserved, while unrelated concurrent appends have no deterministic cross-agent order. Cycle validation and publication preserve acyclicity even under concurrent appends; metadata-budget exhaustion uses the existing omission rule. This internal synchronization does not establish arbitrary mutable payload safety or extend borrowed provider/code lifetimes.

### 4.2 Matching and propagation bindings

The record provider shall expose its primary descriptor and matching payload views through Section 5's operations. [Error and recovery](28_error_and_recovery.md#chapter-28-error-recovery) defines source handler forms, eligibility, search order, and aggregate-view binding. Secondary records shall be observed through that interface.

Identity-preserving propagation shall acquire a reference to the existing record. Formation of a new thrown payload shall create a primary record under Chapter 28's construction protocol. Foreign exception translation shall use its declared mapping and translated identity.

### 4.3 Secondary ordering and exhaustion

Secondary inline capacity shall use the resolved value in Section 2.4. The record provider may use contiguous storage, linked chunks, or another representation behind the opaque ABI. When inline capacity is exhausted, dynamic growth is permitted only through the selected exception allocator and budget, up to the configured maximum retained record count.

The coordinator shall append secondary records in the sequenced order in which it observes cleanup failures. Independent initialization tasks shall retain separate primary records under Section 8.3.

If retention cannot grow because of a capacity limit, allocation failure, or resource budget:

1. Preserve the primary record and all already retained secondary records.
2. Set `truncated` and increment `omitted_count`, with saturation.
3. Dispose of the new omitted record through the nonthrowing disposal boundary.
4. Continue the cleanup required by the active aggregate profile.

An append shall preserve an acyclic retained-record graph. If the incoming record is the primary, contains it, or cannot be validated within the metadata budget, the operation shall omit that entry, set `truncated`, increment `omitted_count`, and release the incoming extra reference. The active propagation reference remains owned. Repeated references to an acyclic shared secondary shall count as separate observations.

Append-resource failure shall use the omission transition above. Optional truncation reporting shall use bounded terminal output and preserve the primary record when output fails.

Failure to establish the first primary exception record, or corruption that prevents record disposal, shall select the nonreturning `ExceptionInfrastructureFailure` terminal path.

### 4.4 Disposal boundary

Final exception-payload disposal, reference bookkeeping, type queries, and record-storage release shall satisfy their nonthrowing infrastructure contracts. An ordinary class may provide a payload under that selected finalization contract.

An unproved admitted finalizer obligation shall yield ANOMALY; a proved escaping finalizer shall yield ERROR at payload registration. An actual escape shall select `ExceptionDisposalFailure`. The provider shall realize this terminal dispatch through its declared exception boundary, using established proof, native boundary behavior, or an explicit adapter as appropriate. This protocol governs retained primaries, secondaries, and omitted-secondary retirement. Ordinary object destruction shall use its separately selected profile.

## 5. Exception ABI version 1

### 5.1 Opaque handle

The cross-module exception ABI passes an `ExceptionRef` containing exactly two object-pointer-sized fields, in this order:

```text
record_address
operations_address
```

For a target with object-pointer size `P` and alignment `A`, `record_address` is at offset zero, `operations_address` is at `align_up(P,A)`, and the handle size is `align_up(align_up(P,A)+P,A)`. Both pointers are null for an empty handle; a partially null handle is invalid. The pointed-to record remains opaque. No foreign module may infer its private counters, inline storage, or allocator representation.

The operations table shall begin with `u32 abi_version`, `u32 byte_size`, and a 32-byte ABI contract fingerprint, followed by function pointers in the order below. The target descriptor shall supply scalar and function-pointer size/alignment and apply ordinary target ABI field alignment. The prefix version is `1`. Boundary admission shall establish a supported version and sufficient byte_size before propagation.

### 5.2 Operations table

Each operation shall take `record_address` as its first argument and use the target's declared C-compatible, nonunwinding callback convention.

| Index | Operation | Result and ownership |
| ---: | --- | --- |
| 0 | `retain` | No result; increments the lifetime reference. |
| 1 | `release` | No result; decrements the lifetime reference and disposes at zero. |
| 2 | `identity` | Stable opaque identity pointer. |
| 3 | `primary_type` | Borrowed canonical type-descriptor pointer. |
| 4 | `primary_address` | Borrowed payload address. |
| 5 | `match_primary` | Given a canonical type descriptor, returns the matching payload-view pointer or null. |
| 6 | `secondary_count` | `u64` retained count. |
| 7 | `secondary_at` | Given a `u64` index and output-handle pointer, returns `u32` status and writes one retained handle only on success. |
| 8 | `omitted_count` | Saturating `u64` count. |
| 9 | `flags` | `u32`; bit zero is `truncated`, all unspecified version-1 bits are zero. |

`secondary_at` returns `0` on success and `1` for an invalid index. On failure it shall leave the caller's output handle unchanged. This ABI status return is independent of the higher-level checked-index API's Result/value outlet.

The type descriptor shall provide a canonical type identity, its full collision-resolving name/contract, and the provider's matching operation. Cross-library matching shall use this canonical contract. Payload storage shall remain under the record provider's ownership while receiving modules hold borrowed views.

The target exception provider supplies raise, resume, handler entry, and bare-rethrow entry points. Those entry points use the selected platform unwinder or an equivalent declared mechanism. The C-compatible observation ABI does not make a CXXN exception a C++ exception. Cross-language propagation requires the foreign exception adapter specified by the ABI chapter.

## 6. Exception profiles and terminal behavior

### 6.1 Aggregate profile

When the aggregate profile is enabled, a destructor or Cleanup failure during active exception propagation is appended to that propagation's record. If cleanup begins without an active exception, its first escaping failure becomes the primary record. Remaining required cleanup continues in its specified order, and later failures become secondaries.

A caught constructor failure rolls back completed subobjects automatically. A failed subobject whose constructor never completed does not receive its complete-object destructor. Its own completed subobjects are rolled back by its construction activation. Manual or Complete destruction policy does not disable this rollback.

An aggregate-profile image may install one terminal observation boundary for otherwise unhandled language exceptions. That boundary cancels ordinary continuation, permits specified stack and static-domain cleanup, records failures, emits the final diagnostic, and terminates. It is not an application recovery handler and cannot resume the failed operation. No new static initializer is started after terminal failure has been selected.

### 6.2 Release terminate profile

The Release preset uses the terminate profile. Programmer-defined handlers remain effective. Handler discovery shall determine whether an applicable programmer handler exists before commencing cleanup for that propagation. If none exists, termination occurs without entering the aggregate-profile fallback rollback or collection path.

An exception that escapes a destructor body, a destructor's Cleanup, or generated subobject-destruction work terminates immediately in this profile, even if another language exception is already active. An exception caught within that destructor before it escapes is not a destruction failure at this boundary.

Catchable construction exceptions shall perform their required language cleanup on the path to a programmer handler. Voluntary task cancellation and ordinary Result failure shall perform their own defined lifetime actions. Source-selected handlers, initialization rollback, and explicitly selected checked operations shall retain their functions under the core execution model.

Release shall require support for explicit language handlers and the selected immediate terminal boundary. Explicit exception-observation facilities shall publish their additional dependencies and retain that termination policy.

Generated `LifecycleError`, ownership-transfer errors, and `StaticDependencyFailure` use the language exception mechanism when it is enabled. With language exceptions disabled, a failed generated lifecycle or dependency check enters its named nonreturning terminal path without unwinding. An explicit source `throw` requires the language-exception capability. These rules do not require a mandatory exception runtime merely to perform state checks.

### 6.3 Terminal diagnostics and storage

An enabled hosted terminal reporter shall write a bounded diagnostic to configured standard error. It shall identify the terminal category and use any already available exception type, source location, or symbol data. Reporting shall use bounded nonthrowing work, bounded/preallocated storage, and a progress-preserving output path. Output failure or unavailable metadata shall lead directly to termination, possibly after a smaller message. A freestanding image shall provide its target terminal hook. Reporter selection is an explicit support capability.

Terminal reclamation belongs to the host or explicit allocator arena reset. It is not a guarantee that user destructors execute or externally visible resources are compensated. Numeric Trap, ContractTrap, a memory-failure terminal outlet, ExceptionInfrastructureFailure, ExceptionDisposalFailure, and an uncaught Release exception are nonreturning terminal events; none is converted into an ordinary Result or ExceptionAggregate by this reporting rule. ContractTrap and memory outlets are defined by the [memory specification](12_core_memory_control.md#chapter-12-core-memory-control); their presence does not require a catch-all collector.

## 7. Static identity and logical initialization order

### 7.1 Stable identities

Each static object in an initialization domain has a stable identity tuple:

```text
(identity_namespace, module_identity, logical_source_path,
 declaration_ordinal, specialization_identity)
```

The namespace and owner identity shall be bound logical strings. In a Core unit, `module_identity` shall identify Chapter 11's logical root; in a module compilation it shall identify the owning named module. The compilation request or selected logical map shall establish these fields in semantic state. A logical source path shall be project-relative, use `/`, remove `.` components, and resolve parent components within its logical root. Its spelling shall be case-sensitive UTF-8. These logical inputs shall determine identity independently of checkout location, wall time, object addresses, worker scheduling, and link order.

The declaration ordinal is the zero-based order of static object definitions in the parsed logical source file. A declaration defining multiple objects assigns ordinals in their declared order. A specialization identity is its canonical bound argument tuple; it is empty for a nonspecialized object. Repeated declarations of the same object refer to one identity. Distinct definitions claiming one identity are `ERROR` unless the module contract explicitly identifies them as the same permitted merged definition.

An object may supply `[[static_id("identifier")]]`. This replaces the path/ordinal/specialization portion with an explicit project-unique logical identifier; duplicates are `ERROR`. Renaming a file may change an automatically generated identity and the order among otherwise unrelated objects. An explicit static ID remains stable across such moves.

Identity comparison shall use the tuple lexicographically: unsigned UTF-8 bytes for text and mathematical values for ordinals. An internal implementation may retain the tuple directly. A selected serialization shall preserve its distinct components unambiguously; standard external export shall use Chapter 29's record fields. Hash-assisted lookup shall resolve matches against the complete tuple; tuple comparison determines ties.

### 7.2 Dependency graph

An edge `A -> B` establishes logical precedence and, when B needs dynamic initialization, requires that A be committed before B starts. Constant initialization completes in the earlier constant-initialization phase and is not delayed by incoming dynamic scheduling edges; the edges still determine its logical destruction rank. The graph contains:

- Explicit object initialization dependencies.
- Edges from each static definition to the next static definition in the same logical file, preserving declaration order.
- With named modules enabled, module dependency barriers: every dynamic initializer in a required module shall be committed before a dependent module's dynamic initializers start.

The initialization graph shall contain the selected static contracts and, where named modules are enabled, the module contracts. A Core root shall use its declaration-order and explicit object-dependency edges. A type-only module import contributes an edge when that contract declares one. The compiler shall validate graph acyclicity before selecting an initialization order; a cycle yields ERROR.

The **logical initialization order** is the unique topological order obtained by repeatedly selecting the eligible node with the smallest stable identity. Each node receives its zero-based logical rank. Dependency edges have precedence over identity order. The rank is fixed before tasks run and is independent of completion time.

Constant-initialized objects that require destruction also have identities and ranks. They are initially committed when their storage becomes available, but participate in the same shutdown order. No destructor registration is needed for an object with no destruction work.

### 7.3 Static declarations and effect contracts

The object metadata forms are `[[init_after(object-list)]]`, `[[static_id("identifier")]]`, `[[init_cancel(cooperative)]]`, `[[init_cancel(finish)]]`, and `[[init_effect(none)]]`, `[[init_effect(compensate)]]`, or `[[init_effect(finish)]]`. An object list is a nonempty comma-separated list of fully resolved static-object names. Each `init_after(A)` adds `A -> annotated_object`. A selected named module's logical contract shall list its required module identities; standard export shall encode that list in `initialization_dependencies`.

The default cancellation/effect pair is `finish`/`finish`. `cooperative` requires either `none` or `compensate` effects. A parallel candidate supplies one of these explicit contracts; a serial task need not declare parallel independence. `init_checkpoint()` is the cooperative checkpoint operation. `init_compensation(callback, context)` registers a nonthrowing callback with an explicit context pointer in the current task's compensation stack, returning a task-local registration token. Registration storage failure follows the task's declared resource-failure outlet before the corresponding external effect occurs. `init_effect_commit(token)` marks that registered effect as having occurred. A successful task publication retires its compensation entries without invoking them; cancellation invokes only committed entries, once in reverse order.

Registration and commitment of an external effect shall satisfy that external system's atomicity or compensation contract. A task requiring uninterrupted completion shall select the `finish` contract.

### 7.4 Serial and parallel schedules

Static scheduling shall use the resolved preset in Section 2.4. A serial schedule shall execute dynamic initializers in logical rank order. Under `custom_parallel`, task admission shall require commitment of every dynamic ancestor and satisfaction of module barriers. The readiness graph shall preserve reachability through precommitted constant nodes. Tasks in one file shall retain their file-edge order; independent tasks in different files of an eligible module may run concurrently.

Parallel startup requires an explicit effect/independence contract for each parallel task. The compiler shall check local declarations and bound summaries, extending analysis according to `effects.inference`. An unproved admitted contract yields `ANOMALY` and retains its programmer obligation. A known cyclic or impossible dependency remains `ERROR`.

Reading a static value shall require commitment or synchronized earlier exposure admitted by its construction contract. A detected violation shall raise `StaticDependencyFailure` through the selected language outlet, or terminate when exceptions are disabled. Waiting shall follow declared graph dependencies. Optional access instrumentation follows the execution profile.

## 8. Static task failure, cancellation, and commitment

### 8.1 Task states

A task has exactly one state: `Pending`, `Running`, `Ready`, `Committed`, `Canceled`, or `Failed`. The initialization domain has `Open`, `Canceling`, `Closing`, or `Closed` state. `Ready` means that object construction completed but its publication has not yet committed.

The normal transition is `Pending -> Running -> Ready -> Committed`. A never-started canceled task transitions `Pending -> Canceled` without construction or destruction. A running task that fails transitions to `Failed` after its required construction rollback. A running task that accepts cooperative cancellation transitions `Running -> Canceled` after partial-construction rollback and required compensation. If that rollback escapes with a failure in the aggregate profile, the task instead becomes `Failed` with its own primary record; Release terminates at an escaping destruction boundary. A ready but uncommitted object that loses publication to cancellation is destroyed exactly once. It transitions to `Canceled` if that cleanup succeeds; in the aggregate profile an escaping cleanup failure instead makes the task `Failed` with its own primary record. The consumed object is not destroyed again. Release terminates at an escaping destruction boundary.

Publication and cancellation shall linearize under one domain protocol. A commit shall atomically establish Open-domain admission and registry membership. A winning commit retains that membership; winning cancellation selects the unpublished object's cancellation cleanup. Locks or atomics may realize the same transition.

### 8.2 Mixed cancellation

Winning domain cancellation shall cancel Pending tasks immediately. A Running cooperative task shall observe the request at its next reached checkpoint, where its activation has a consistent cleanup frontier. A finish task shall complete its current work. If it produces an object after cancellation wins, the coordinator shall destroy that unpublished object.

Cancellation shall be a distinct control outcome with generated cleanup edges. These edges may share construction-rollback machinery. An exception escaping that cleanup shall follow the selected destructor failure profile.

The external-effect contract is one of:

| Contract | Cancellation behavior |
| --- | --- |
| `none` | No externally visible effect requires reversal; cooperative cancellation may occur at declared checkpoints. |
| `compensate` | The task supplies a nonthrowing compensation action for each committed external effect. Compensation executes once, in reverse registration order, after object rollback. |
| `finish` | Irreversible effects or an inability to cancel require the task to finish; cancellation prevents only later object publication. |

Compensation failure shall terminate with `CancellationContractFailure`. A successful compensation result shall cover exactly the external effects named by that contract. The task's bound cancellation mode determines whether interruption is admitted.

### 8.3 Separate failures

In Aggregate, each task's first escaping initialization exception shall create its primary entry. Its cleanup failures shall attach to that entry. Independent task entries shall retain their primary identities and report in logical rank order.

The first observed task failure shall request domain cancellation. Other Running tasks may fail before observing the request; their entries shall preserve those failures separately. A recorded failure shall retain its primary identity through cancellation.

Successful startup shall admit application entry. On aggregate-profile startup failure, the coordinator shall close task admission, drain Running tasks to their terminal states, shut down remaining committed objects, report the separate failure entries, and terminate.

In Release Terminate, an initializer exception lacking a programmer handler shall terminate at handler discovery. Result-valued operations and voluntary cancellation shall use their ordinary commit/cancel control flow.

### 8.4 Shutdown

Shutdown visits committed objects in decreasing logical rank, regardless of physical initialization finish order. An already destroyed or abandoned object is skipped. Each live destruction obligation is discharged at most once. A partially constructed failed task is absent from the committed registry; its rollback belongs to its task activation.

In the aggregate profile, shutdown continues after a destructor failure, appending failures belonging to the same shutdown propagation record while retaining separate initialization-task failures. In Release, an escaping destruction exception terminates at its boundary and stops further shutdown work.

Domain unload shall require retirement or explicit transfer of every dependent object, callback, exception record, and destruction obligation. An admitted unproved unload obligation yields ANOMALY; a statically known live dependency yields ERROR. The selected loader adapter shall realize this domain contract.

