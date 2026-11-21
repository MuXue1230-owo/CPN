<a id="chapter-14-standard-library"></a>

# CXXN Standard Library Contracts Specification

## 1. Library identity and availability

The standard library SHALL use the [core operational model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance), ordinary CXXN types and lifetimes, and the resolved configuration. This chapter defines the common library invocation, ownership, resource, effect, and failure model. Specialized interface chapters SHALL supply the state transitions and results specific to their facilities.

An import SHALL select module compilation and make the selected module's exports available. `import std;` selects the minimal value utilities; `import std.mem;` makes that module's exports available through `std::mem::`. Actual operation use SHALL introduce its declared support dependencies. A freestanding capability record SHALL identify its supported subset under Chapter 21. A required unavailable capability SHALL produce the centrally specified diagnostic. Standard module identities SHALL belong to the selected standard-library provider; extension modules SHALL publish their own identities.

| Module | Required contract when enabled | Optional support introduced by actual use |
| --- | --- | --- |
| `std` | `Unit`, `Ref`, `Option`, `Result`, move/forward, fundamental traits, contract termination | Target terminal hook for operations selecting termination. |
| `std.error` | Retained exception ownership, current-record observation, identity-preserving raise, and explicitly invoked exception capture | Selected language-exception and record capabilities for the requested operations. |
| `std.mem` | Bounded views, explicit allocation/resource handles, storage and representation operations, owning handles | Selected allocator, resource accounting, optional lifetime-tracking provider. |
| `std.collections` | Fixed and dynamic containers with explicit guarantees | Allocator and budget only for allocating operations. |
| `std.algorithm` | Explicit Span traversal, copying, sorting, and left folds with operation-specific constraints | An explicit resource for stable sorting; parallel extensions require a separately selected executor. |
| `std.text` | UTF-8 views, validation, scalar iteration, owned text | Allocation for owned/growing text; Unicode tables only for operations using them. |
| `std.text.unicode` | Versioned normalization, grapheme and case-mapping operations | Pinned Unicode tables and explicit allocation where applicable. |
| `std.atomic` | Atomics, ordering, fences, declared fallback | Target intrinsics or explicitly enabled fallback. |
| `std.sync` | Cancellation tokens and selected synchronization objects | Atomic support; blocking provider only for blocking facilities. |
| `std.thread` | Thread ownership, join, and explicit detachment | Selected native thread provider. |
| `std.task` | Task/context/outcome ownership and suspension protocol | Explicit frame resources and selected executor. |
| `std.numeric` | Numerical traits, context adapters, and provider queries | Only the enabled numerical families/providers. |
| `std.effects` | Compile-time effect-set and callable-contract queries | Selected compile-time effect-signature metadata. |
| `std.meta` | Compile-time reflection, typed declaration building, and hygienic quotations | Selected compile-time reflection/generation capability. |
| `std.meta.runtime` | Explicitly generated, versioned runtime descriptors | Explicit descriptor storage and its owning provider. |
| `std.math` | Accuracy-declared real and complex mathematical functions | Selected mathematical provider; per-function correctly rounded and/or approximate capabilities. |
| `std.units` | Quantities, affine points, exact scale metadata | The chosen representation's resource contract. |
| `std.time` | Clock identities, durations, time points, deadline conversion | Clock provider and explicitly requested calendar/time-zone data. |
| `std.io` | Bounded I/O, explicit handles, formatting/parsing contracts | Selected stream/file provider. |
| `std.codec` | Explicit byte encoding and schema-based decoding | Supplied encoding/decoding resources. |
| `std.process` | Hosted arguments, environment queries, process entry/exit contracts | Selected hosted process provider. |

The [configuration chapter](08_runtime_configuration.md#chapter-08-runtime-configuration) owns the enabled-module, provider, profile, and diagnostic settings. A definition SHALL capture the relevant resolved bindings at its specified interface boundary. An import alias SHALL preserve nominal identity. Intrinsic implementations SHALL satisfy the same public contract as other implementations of that operation.

## 2. Common library operation model

### 2.1 Binding and public contract

Each operation SHALL declare its result, admitted inputs and capabilities, resource source, covered state, ordinary errors, callback effects, ownership transfer, borrow origins, invalidation, and synchronization. It SHALL identify observable admission, commitment, publication, and retirement points, including partial external progress and any permitted retry. The [contract/effect rules](24_contracts_and_effects.md#chapter-24-contracts-effects) and [effect-composition rules](25_effect_composition_and_boundaries.md#chapter-25-effect-composition-boundaries) govern the corresponding source and exported descriptors.

Signature tables SHALL describe ordinary declarations. A parameter is required unless a default or shorter overload is explicitly listed. Type parameters SHALL satisfy the stated construction and operation constraints at instantiation. An error record's listed fields and cases SHALL form its complete public shape for that interface revision. Standard bounded error records, policy values, and descriptor observations SHALL use nonallocating, nonthrowing value operations; a user or owning payload SHALL contribute its own declared effects.

A public record SHALL support direct construction from its listed fields in declaration order unless its interface specifies a factory or opaque construction path. An optional field SHALL select its present or absent case explicitly. A failed result SHALL expose its declared error payload and progress/state observations. Exact unavailable information SHALL use the specified absence or overflow representation.

### 2.2 Invocation phases

An invocation SHALL implement the following phases in the order required by its language and specialized interface contract. The table defines responsibilities; an operation's specified interleaving remains binding, including async admission before the remaining argument evaluation.

| Phase | Required operation |
| --- | --- |
| Bind | Resolve the declaration, capabilities, policies, resource sources, and applicable failure outlets. |
| Evaluate | Evaluate source expressions and establish parameter categories under the language sequencing rules. |
| Admit | Establish the specified extent, state, capability, and resource conditions before the mutation they protect. |
| Prepare | Construct the required tentative values or storage while retaining the obligations covered by the failure guarantee. |
| Commit | Apply the specified value, ownership, or progress transition exactly once. |
| Retire | Discharge replaced generations, temporary values, registrations, and storage under the active lifetime profile. |
| Publish | Deliver the completed return value or accepted asynchronous outcome after its required completion steps. |
| Deliver failure | Select the declared operational error, language-handler propagation, cancellation transition, or terminal action. |

A replacement may commit before retiring its old representation. The committed state SHALL remain the current state if retirement subsequently fails. A tentative returned value SHALL remain unpublished until its required completion and retirement steps succeed. A caught failure before publication SHALL retire that tentative value on the profile's continuing cleanup path. The failure profile SHALL determine continuation at a terminal boundary.

A Result's publication SHALL deliver its active tagged value. Ok represents the operation's success; Err represents its stated ordinary failure and any recorded partial progress. Source-expression effects, consumed arguments, and callback effects SHALL retain their own phase and ownership terms.

### 2.3 Ownership and borrows

Acquisition of an owning value SHALL establish its specified destruction and release obligations. A move SHALL apply that type's declared source/destination transition. Retirement SHALL consume each obligation exactly once. An observer or borrowed result SHALL designate the owner, generation where applicable, and access interval stated by its interface. Copying a borrow SHALL preserve those terms. Explicit retention SHALL be represented by the retaining operation or owner.

Synchronous borrowed parameters SHALL have their declared noescape behavior. A returned view SHALL identify its borrow origin. A descriptor or callback retained by an owner SHALL remain valid through its last required use and release. Concurrent access SHALL use the interface's stated synchronization or the caller's external coordination. A shallow handle qualification SHALL expose the referent qualification declared by that handle; read-only element access SHALL use a read-only referent type.

Object relocation, retirement, and generation replacement SHALL invalidate the affected views specified by the owning operation. Checked views SHALL report their selected generation and access conditions. Raw obligations and optional validation SHALL follow the selected memory contract in the core model.

### 2.4 Resources and guarantees

An allocating operation SHALL obtain resources from its explicit parameter or captured configured resource contract. Its accounting SHALL charge the actual retained capacity, required metadata, and selected geometry. Old and prepared replacement storage SHALL count concurrently while both remain retained. Admission across a hard-budget ancestry SHALL commit as one transaction; shared ancestors SHALL charge one physical backing once. Provider release after successful admission/validation SHALL follow its declared nonfailing release contract.

Library extent arithmetic SHALL compute exact mathematical sizes and return its stated capacity/size error when the required extent is unrepresentable. This selected allocation behavior applies independently of the caller's ordinary numerical profile. A reserved resource SHALL provide its advertised backed geometry. A soft quota SHALL bound consumption under its declared sharing scope.

| Guarantee | State on the specified outcome |
| --- | --- |
| Unchanged | The expressly covered state and ownership SHALL equal their preoperation state on the stated failure. |
| Basic | The covered objects SHALL retain valid invariants, destruction obligations, and exclusive ownership; their values may reflect completed work. |
| No-failure | For satisfied preconditions, the declared ordinary-failure and escaping-exception outcome sets SHALL be empty. Declared divergence, terminal effects, and violated external contracts SHALL retain their separate policies. |

The operation SHALL name any expressly consumed argument, alias, or external callback state outside a destination-only unchanged guarantee. Resource admission SHALL precede mutation of the state protected by that guarantee. A basic-guarantee operation SHALL describe its admitted intermediate states. Algorithm complexity, allocation bounds, and deterministic ordering expressly promised by an interface SHALL remain selected functional contracts.

### 2.5 Failure routing

An operation SHALL use the outlet associated with the failure that occurred. A `try_` or Result form SHALL deliver its listed operational errors through its error payload. User construction, assignment, comparison, callbacks, and retirement SHALL retain their separately declared language effects. NumericResult SHALL retain the numeric chapter's status and error identities. Conversion or composition between error types SHALL use an explicit operation.

| Event | Required routing |
| --- | --- |
| Listed ordinary library error | Return the declared Err value with its exact available state/progress information. |
| Admitted language exception | Search the eligible handler interval and select the permitted handler path or boundary dispatch. |
| Explicit exception capture | Execute the selected adapter's handler interval as specified by the [error and recovery chapter](28_error_and_recovery.md#chapter-28-error-recovery). |
| Contract or numeric terminal operation | Dispatch to the specified ContractTrap or NumericTrap outlet. |
| Exception escaping a mandatory terminal boundary | Dispatch to that boundary's terminal action. |
| Cooperative cancellation | Follow the owning coordinator's checkpoint and commitment protocol. |

A source handler or explicit capture adapter SHALL retain its selected function in Release. Unhandled and destruction-boundary exceptions SHALL use the failure profile bound to the declaration. Physical checking, handler representation, and metadata realization SHALL follow the core model's implementation freedoms while preserving the selected outlet.

Result and other declared must-use outcomes SHALL follow the central diagnostic rule. `discard(value)` SHALL acknowledge deliberate noninspection; the value's ordinary lifetime and active-payload destruction remain applicable. The [error and recovery chapter](28_error_and_recovery.md#chapter-28-error-recovery) defines retained exception identity and explicit translation.

### 2.6 Execution profiles and diagnostic operations

The resolved preset SHALL determine optional instrumentation and ordinary numerical execution under the sole configuration table. Release Native operation SHALL use the native contract defined by the core and numeric chapters. Explicit checked operations, resource quotas, atomic synchronization, cancellation commitment, codec validation, and named mathematical accuracy contracts SHALL retain their requested results and effects.

An implementation SHALL realize the semantic state and actions required by the selected observable contract. Proof-established conditions and unobserved physical representations SHALL receive the transformation freedoms defined by the core model. Optional validation and diagnostic state SHALL follow their resolved settings. A facility's explicit resource or complexity guarantee SHALL remain applicable to that selected facility.

`std::ensure(condition)` SHALL evaluate its Boolean condition and select normal continuation for true or ContractTrap for false in every profile. `std::debug_assert(condition)` SHALL first resolve its diagnostic setting: enabled execution SHALL evaluate the condition and use the same Boolean outlets; disabled execution SHALL select an empty execution sequence and leave proof facts unchanged. Diagnostic severity and defaults belong to the configuration chapter.

## 3. Minimal values and utilities

The [core library interfaces](16_library_interfaces.md#chapter-16-library-interfaces) own the declarations and state transitions of Unit, Ref, Option, Result, movement, forwarding, and swap. Their active payloads SHALL follow that catalogue. The minimal std module also SHALL export ScalarError, to_underlying, try_from_underlying, and from_underlying under the [scalar-domain contracts](10_types_functions_generics.md#chapter-10-types-functions-generics).

## 4. Allocators and resource ownership

AllocatorRef SHALL identify its allocation provider, context, supported geometry, and release contract. ResourceRef SHALL bind that allocator to a concrete domain and its admission ancestry. The [core interfaces](16_library_interfaces.md#chapter-16-library-interfaces) own their declarations, Allocation, Owned, and storage operations. The [numeric resource interfaces](32_numeric_resource_interfaces.md#chapter-32-numeric-resource-interfaces) own quota, ResourcePlan, and temporary-value protocols.

A domain closure SHALL discharge or explicitly transfer all outstanding allocations, reservations, and required tracking obligations before retiring domain state. An explicit close with outstanding obligations SHALL report Outstanding and preserve the domain. Destruction with unresolved obligations SHALL dispatch to ContractTrap while the required backing state is still available. An expressly selected Abandon retaining/leak contract SHALL preserve backing needed by its outstanding uses for their full required lifetime.

Allocation SHALL represent manual release authority. Its owning or manual treatment SHALL follow the operation selected by the programmer. Owned SHALL retain the registered complete-object destruction and release entries, including when its visible access uses a base view. Foreign owners SHALL use the admitted complete/base/deleting entry and allocator contracts from their ABI binding.

## 5. Views and fixed storage

Span, Array, and InlineVector SHALL use the exact extents, live element sets, construction order, and invalidation rules in the [core interfaces](16_library_interfaces.md#chapter-16-library-interfaces). The zero-element forms SHALL use their specified empty states. Mutable byte storage and live typed element views SHALL retain their distinct memory designations.

## 6. Dynamic containers

Vector, String, and associative containers SHALL use their selected resource, preparation guarantee, and retirement protocol from the [core interfaces](16_library_interfaces.md#chapter-16-library-interfaces). Empty construction, complete-handle movement, explicit cloning, and basic versus unchanged relocation SHALL have the specific effects stated there. Each indexed container SHALL apply its declared key equivalence/order and iteration policy.

## 7. Text and byte sequences

StringView and String SHALL preserve their UTF-8 and byte-extent contracts. Scalar iteration, grapheme segmentation, native paths, and zero-terminated foreign views SHALL use their separately defined interfaces in the core and [extended library](19_extended_standard_library.md#chapter-19-extended-standard-library) chapters. Explicit Unicode transformations SHALL bind their versioned data contract.

## 8. Algorithms and numerical integration

The [extended library catalogue](19_extended_standard_library.md#chapter-19-extended-standard-library) owns the Span algorithm signatures, traversal, error, complexity, and resource contracts. Each algorithm SHALL invoke callbacks under those terms and use the numeric policy captured by the relevant operation. An explicitly selected ordered fold or reported/checked numeric operation SHALL retain its stated ordering and observations. Parallel extensions SHALL declare their executor, partitioning, cancellation, resources, and reduction contract.

The [mathematical functions](18_mathematical_functions.md#chapter-18-mathematical-functions) and numeric chapters own mathematical domains, rounding, status, accuracy, and reproducibility. Library use SHALL preserve their canonical numeric identities and selected capabilities.

## 9. Quantities, time, and semantic values

The [quantity and affine-point interfaces](31_units_interfaces.md#chapter-31-units-interfaces) own canonical dimensions/scales/origins, Quantity/Point construction, representation access, and named conversion. Time operations SHALL use those Quantity identities and the clock, correlation, and calendar contracts in the extended library chapter.

## 10. I/O, formatting, and serialization

The extended library chapter SHALL define I/O progress and close ownership, formatting/parsing projections, and codec commitment. Those operations SHALL apply their explicit output, partial-progress, and resource protocols through the common phases in Section 2. The standard HandleOwner SHALL use its explicit-close state machine; a provider extension SHALL publish a distinct contract for another owner policy.

## 11. Thread, task, and synchronization integration

The [concurrency memory model](13_concurrency_memory_model.md#chapter-13-concurrency-memory-model) and [concurrency interfaces](17_concurrency_interfaces.md#chapter-17-concurrency-interfaces) own atomic order, execution context, cancellation, task publication, join, and close. Each operation SHALL preserve its selected logical entry boundary and transferred responsibility. Observed FP contexts and Native execution SHALL use their respective numeric contracts.

## 12. Program entry and interface compatibility

A freestanding image SHALL use the entry declared by its target/provider contract. A hosted application SHALL select exactly one admitted entry, `i32 main()` or `i32 main(std::process::Args args)`, through its Core compilation request or selected module map. The Args form SHALL select module support, import std.process, and borrow its provider-backed argument sequence for the lifetime of main. Native startup SHALL complete the declared static-initialization protocol before entry. Normal return SHALL perform normal shutdown and reverse logical static destruction, then map the i32 status to the host's declared exit-status domain.

Immediate termination SHALL dispatch to its selected terminal operation. An ordinary hosted exit extension SHALL identify and successfully close its declared lifetime domain. The module provider and public ABI binding SHALL use the configuration chapter's captured identities. C/C++ boundaries SHALL use verified direct layouts or explicit opaque adapters under the [native interoperability specification](09_native_interoperability.md#chapter-09-native-interoperability).

The implementation SHALL expose and link the support dependencies required by actual uses and their bound contracts. Compile-time facilities SHALL retain their specified evaluation phase; runtime facilities SHALL acquire their declared instances through their source-selected creation operations.

