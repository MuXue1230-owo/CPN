<a id="chapter-21-abstract-machine-conformance"></a>

# CPN26 Core Execution and Conformance Specification

## 1. Normative model and definition ownership

CPN26 specifies CPN26 source and execution under the bound standard designation, resolved configuration, target contract, and selected providers. An implementation **shall** realize an execution admitted by that combination. **Shall** defines a requirement; **may** identifies a permitted implementation choice. An admitted choice **shall** preserve the observations selected by the operation contract.

The language is native and manually manages storage ownership. Runtime support **shall** follow capabilities actually used by the program. Ordinary native scalar code requires its target's execution and terminal mechanisms. Allocating values, tracked handles, language exceptions, tasks, runtime descriptors, and other selected facilities add their declared dependencies. Low-level operations use the same language and declaration model throughout.

The following table assigns each shared definition one normative owner. Feature chapters **shall** apply these definitions and specify their additional inputs, transitions, results, and effects.

| Definition | Normative owner |
| --- | --- |
| Execution, observation, and transformation permissions | This chapter. |
| Configuration keys, defaults, scope, and diagnostic categories | [Configuration](08_runtime_configuration.md#chapter-08-runtime-configuration). |
| Object states, initialization plans, and destruction responsibility | [Construction execution](06_construction_execution.md#chapter-06-construction-execution). |
| Source sequencing, storage, pointer access, and control transfers | [Core memory and control](12_core_memory_control.md#chapter-12-core-memory-control). |
| Integer domains, common type, and arithmetic projection | [Integer types](02_integer_bigint.md#chapter-02-integer-bigint), with expression binding in [numeric expressions](07_numeric_expressions.md#chapter-07-numeric-expressions). |
| Numeric status, error identity, rounding, NaNs, and tininess | [Numeric integration](04_numeric_integration.md#chapter-04-numeric-integration). |
| Coherence, synchronization, and task execution | [Concurrency](13_concurrency_memory_model.md#chapter-13-concurrency-memory-model). |
| Common library invocation, ownership, and guarantees | [Standard library](14_standard_library.md#chapter-14-standard-library). |
| Explicit exception recovery and phase routing | [Error and recovery](28_error_and_recovery.md#chapter-28-error-recovery), using Chapter 08's record and process policy. |
| Effects, predicates, and callable boundaries | [Contracts](24_contracts_and_effects.md#chapter-24-contracts-effects) and [effect composition](25_effect_composition_and_boundaries.md#chapter-25-effect-composition-boundaries). |
| Generation phases and publication | [Compile-time generation](23_compile_time_generation.md#chapter-23-compile-time-generation). |
| Logical declaration identity and compilation boundaries | [Modules and compilation](11_modules_compilation.md#chapter-11-modules-compilation), including the Core root-unit model. |
| Optional public contract encoding and fingerprints | [Contract schemas](29_public_contract_schemas.md#chapter-29-public-contract-schemas). |

A cross-reference imports the owner's rule. Examples illustrate that rule under their stated contract. An explicit operation signature, policy, and result **shall** take priority over an ambient ordinary-operation default.

## 2. Binding and execution

### 2.1 Source edition binding

Each compilation request **shall** explicitly bind its source edition through the compiler invocation or build-target description before source parsing. A CPN26 request **shall** select this standard's grammar, preset defaults, and semantic rules as one binding. The request **shall** retain that edition in its internal compilation identity and in any exported source-semantic record. Named presets choose configuration within the selected edition.

An unsupported edition **shall** yield ERROR before declarations are accepted. An implementation may support several explicitly selected source editions. Edition selection **shall** follow the declared request; successful parsing of an alternative edition establishes no selection. Imported source or interfaces **shall** retain their declared edition and use an explicitly supported translation or boundary contract when joining another edition. The edition binding applies equally to Core root units, jointly compiled modules, and separate compilation. Its enforcement uses the compilation request and internal identities independently of `tooling.contract_export`.

### 2.2 Operation binding and phases

Before runtime evaluation, the implementation **shall** determine declarations, types, overloads, generic arguments, explicit contracts, and effective configuration. Generated declarations **shall** pass the same source rules as authored declarations; each generation transaction publishes one validated batch. Imported definitions and generic recipes **shall** retain their published binding during specialization and inlining.

Source typing **shall** determine the result type before testing its target availability. Enabled integer widths therefore test the materialization of the canonical common type defined in Chapter 02. Required constraints, kind matches, and constant evaluation are source decisions. Optional diagnostic analysis supplies additional evidence after those decisions.

Each invocation **shall** follow the phases required by its feature contract:

| Phase | State transition |
| --- | --- |
| Bind | Select the operation, representation, policy, and resources. |
| Evaluate | Evaluate operands and arguments in source order, producing values and source effects. |
| Admit | Establish the stated domain, capability, access, and resource conditions using the selected validation mode. |
| Prepare | Compute a candidate result and acquire tentative resources. |
| Commit | Publish the stated value, lifetime, ownership, progress, or synchronization transition. |
| Retire | Discharge remaining obligations on that returning path. |
| Deliver | Return a value/error, propagate a selected exception, or perform the terminal action. |

Equivalent phases may be combined. A partial-progress interface identifies its intermediate commits; a transactional interface identifies one commit. Argument effects precede admission. A recovery guarantee covers the state named by its operation, while earlier committed external effects remain part of the execution.

The abstract state describes live object generations, storage/release ownership, values and selected status, control flow, synchronization, tasks, and native bindings. An implementation **shall** realize these facts through control flow, registers, locals, explicit objects, provider records, or compile-time information as needed by selected observations. A state description alone imposes no object header or universal registry. Statically determined cleanup can use direct calls; partial array rollback can use a prefix count; explicit dynamic ownership transfer can carry its current owner.

## 3. Observations and transformation permissions

| Observation | Required when selected |
| --- | --- |
| Value | Committed representation, returned value, or permitted numerical result set. |
| Lifetime | Constructor/destructor effects and discharge or transfer of responsibility. |
| External effect | I/O, foreign calls, volatile/device accesses, and callbacks at their sequencing points. |
| Synchronization | Atomic modification order, reads-from relationships, fences, and publication. |
| Numerical status | Local reports and environment state exposed by an observing contract. |
| Failure | Declared error payload, catchable propagation, or terminal outcome. |
| Resource | Selected admission, retained charge, ownership transfer, and release. |

A transformation **shall** produce an execution within the contract's permitted observations. The compiler may eliminate unobserved work, combine equivalent transitions, select permitted schedules, or use a relaxed numerical result relation granted by the bound profile. Timing and register allocation are implementation properties except where an explicit contract states a bound.

Strict equivalence includes the selected result and events. Native equivalence uses the broader target-declared result, environment, and fault contract. Native freedom is available at binding time and requires no proof that a stronger strict contract would be unobserved.

### 3.1 Release execution

Release presets **shall** select Native ordinary numerical execution, contract-based raw access, and local construction/effect analysis through Chapter 08's default table. Optional diagnostic instrumentation executes when enabled. Feature deltas are:

| Facility | Native execution |
| --- | --- |
| Ordinary fixed integers | Chapter 02's Native projection and target-domain behavior; validation branches are optional. |
| Ordinary floating operations | Target arithmetic and declared relaxations, native NaN/subnormal behavior, and unobserved local/sticky accounting. |
| Ordinary Complex arithmetic | The selected scalar-step/provider operation with bound component policies. |
| Pure masked arithmetic | Compute-and-select for inactive lanes whose additional work contributes only discarded values and unobserved numerical state. |
| Construction and effect analysis | Local control flow and bound declarations/summaries; cross-procedure inference is an enabled enhancement. |
| Raw-access and contract diagnostics | Programmer obligations under their selected contract; instrumentation follows explicit configuration. |

Source operand evaluation, memory access, callbacks, device effects, ownership, and atomic synchronization remain observations of the functions that request them. A masked memory operation **shall** follow its active-lane access contract. A checked/reporting vector operation **shall** collect the events required by its interface. Pure Native arithmetic uses the wider permission above.

### 3.2 Explicit functional contracts

An explicitly named checked, Result, report, exact, wrapping, saturating, tracked-pointer, resource, synchronization, or recovery operation **shall** perform its declared function in every preset. Explicit Strict/Reproducible and accuracy selections establish their stated contracts. Checks may be combined or proved redundant while preserving those results. Cost belongs to the capability selected by source.

A Native caller can invoke a strict function under that function's binding. A strict caller using a native floating boundary **shall** select an adapter or provider guarantee that isolates the native environment effects relevant to its strict observations. Isolation belongs to the stronger boundary; Native entry/exit itself requires no general save/restore wrapper.

A Native status read observes the provider state defined for that interface. Attribution of individual earlier Native operations is outside that observation contract. A source requiring attribution **shall** select reporting operations or a strict observation region before the work.

## 4. Lifetime, resources, and numerical execution

An object generation **shall** identify one lifetime in an authorized extent. Reusing an address creates a new generation. Pointer access **shall** satisfy its generation, extent, alignment, qualification, and access contract. Tracked access realizes its explicit interface; raw access uses the programmer's bound contract.

Each pending destruction action **shall** have one controlling responsibility. Transfer changes that controller. Storage ownership separately identifies release responsibility. Chapter 06 defines admitted transitions and remaining-cleanup order. A returning failure **shall** preserve the invoked operation's promised state; catchable construction failure retires its selected completed subobjects. A terminal action ends the execution path at that point under the target's terminal contract.

An allocating operation **shall** charge actual retained resources under its selected domains and geometry. Optimized preparation and transfer **shall** preserve admission, accounting, and release results. Chapter 14 defines common guarantees; Chapter 32 adds reservation and temporary-epoch rules.

Numeric binding **shall** determine common type, mathematical operation, projection, status, and delivery. A numeric Result **shall** describe its invocation, including repeated events already present in history when local reporting is selected. Constant evaluation **shall** use its target-format contract and isolated compile-time state. A constant Result error is a successful value of its Result type. Native runtime folding uses the Native result set; strict folding reproduces strict observations.

## 5. Concurrency and program images

Shared accesses **shall** follow Chapter 13's location, happens-before, and race rules. An atomic read **shall** obtain a value from a permitted producing modification. Synchronization preserves actual reads-from relationships; bit equality alone establishes value equality. Cancellation and completion **shall** publish the single outcome selected by their atomic commit protocol.

A raw-lifetime or data-race violation leaves the portable contract at the violating action. Target behavior applies from that point. The implementation **shall** preserve preceding valid observations and use an explicitly trusted contract for stronger source assumptions. Native numerical domain outcomes remain the provider's declared fault/result choices rather than evidence that the input was unreachable.

Providers **shall** state their progress guarantees and conditions. Join/close results **shall** identify retained or transferred responsibility. Each program image or independent lifetime domain **shall** have one startup owner and static dependency graph. Initialization commits logical positions; normal shutdown **shall** retire committed statics in reverse logical order. Concurrent startup uses the graph's cancellation/commit protocol.

An image **shall** retain required code and support while live values, callbacks, releases, exception records, or tasks depend on them. Foreign startup relationships use explicit mapped dependencies or independent host lifetimes. Native compatibility follows the declared ABI feature subset.

## 6. Diagnostics and conformance

The compiler **shall** apply Chapter 08's category and mandatory-error rules. An admitted unproved programmer obligation yields its configured ANOMALY. Required types, generic constraints, ABI matches, and explicit proof requirements **shall** be satisfied before acceptance. Suppression controls diagnostic emission; execution follows the bound contract.

### 6.1 Core and selected capability conformance

The standard designation is **CPN26**, and the language name is **CPN26**. A Core conformance claim **shall** cover one root source unit, source edition and declaration binding, ordinary declarations and types, ordinary type/value generics, control flow, object lifetime and manual storage, configuration and diagnostics, and native object emission under its published core target. Its scalar operations **shall** implement the representations and policies required by that resolved core configuration. Source requirements **shall** be checked at their specified binding or execution boundary.

The Core root unit **shall** have an internal owner identity and the source/type/effect information needed to check that unit and its declared native boundaries. An implementation may represent those facts directly in compiler state. External manifests, JSON serialization, SHA-256 hashing, named module graphs, and persistent CPN26 interface artifacts are obligations of the selected capabilities below. A Core compiler can emit an ordinary native object and bind C or supported C++ declarations under its target contract; linking that object with foreign objects uses native symbol and ABI contracts.

| Optional capability | Selected operation and requirement |
| --- | --- |
| `compilation.modules` | Bind named modules, partitions, imports, exports, and their logical dependency graph. A joint compilation may obtain every declaration from the selected source inputs. |
| `compilation.separate` | Produce or consume independently compiled CPN26 interface material under a declared versioned protocol; requires `compilation.modules`. |
| `tooling.contract_export` | Produce the requested standard public records with Chapter 29's canonical JSON, references, and SHA-256 fingerprints. This capability is independent of module and separate-compilation support. |

Chapter 08 defines their disabled defaults. A requiring source construct or artifact request **shall** establish that its capability is available and enabled. Native linkage alone establishes a native boundary, while a separately compiled CPN26 semantic import selects `compilation.separate`. A provider's private interface protocol may realize separate compilation with `tooling.contract_export = false`; its identity, binding, compatibility, and collision-resolution checks **shall** still satisfy Chapter 11. An export request selects the public transport of already established semantic facts.

An implementation may claim any supported combination of the standard's optional capabilities. An optional claim **shall** implement the corresponding clauses for its published support set. Named modules, separate compilation, public contract export, high-accuracy numerics, extended formats, allocating numerical families, mathematical functions, advanced generics, reflection, language exceptions, standard-library modules, and managed concurrency have the capability boundaries defined by their owning chapters. Their presence in this standard defines the contract of a selected feature.

| Capability state | Required transition |
| --- | --- |
| Available | Publish the provider and the exact supported operations and contracts. |
| Enabled | Admit uses under the resolved configuration and expose applicable declarations. |
| Required by a program | Bind each used operation and its transitive dependencies, and supply their selected execution or compile-time support. |

Importing an optional catalogue **shall** expose its capability-gated declarations. A requiring use **shall** establish the needed claim before binding. An unsupported use yields the applicable capability diagnostic. Core conformance remains valid for programs within its declared core support. Capability closure **shall** follow actual semantic dependencies, including a selected operation's own supporting algorithms and resources.

### 6.2 Numerical claims and resource contracts

An optional numerical claim **shall** identify the operation, format, admitted controls, delivery form, value/status contract, and resources defined by Chapters 05 and 18. Support for a representation, one function, or one delivery form **shall** establish that stated subset. The provider may share algorithms across entries and expose groups whose members have explicit contracts. Correctly rounded, component-exact, and approximate entries **shall** bind independently through their actual dependency sets.

A selected exact or correctly rounded entry **shall** deliver its promised result on success. Its provider **shall** choose an implementation and publish the resource and failure contract required by that interface. A mathematical reference formula specifies the result relation; physical algorithms, intermediate representations, and workspace follow the selected provider contract. Approximate results **shall** use a claimed approximation relation.

An implementation's conformance claim **shall** identify CPN26 as its source designation, its core target ABI and configuration, and its selected capability claims with provider identities and dependencies. A documented compiler/target description may supply this information for Core. A selected standard contract export **shall** use Chapter 29's identity and encoding rules. Internal semantic records and private interface protocols **shall** preserve the relevant identities and checks in their declared representation. Compilation budgets and optional analysis belong to the build context.

Portability applies to compatible operation contracts across targets. Explicit representations, exact/checked operations, strict/reproducible policies, versioned providers, and standard wire encodings establish stronger common contracts where requested. Native selection grants the implementation freedoms defined by its bound target contract.

