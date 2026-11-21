<a id="chapter-25-effect-composition-boundaries"></a>

# CPN26 Effect Composition, Lifetime, and Foreign Boundaries Specification

## 1. Phase-aware effect composition

An expression's effects shall compose the operations it evaluates in source order, including argument/parameter admission, selected execution, result construction, and required cleanup. Chapter 24 owns effect categories and validation modes. The [abstract machine](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance) owns observations and permitted transformations. This chapter assigns the feature-specific phase boundaries.

A successful ordinary synchronous call shall follow this order:

| Stage | Operations attributed to the call |
| --- | --- |
| Callable selection | Evaluate the callable. |
| Parameter admission | For each parameter in order, evaluate its argument/default and initialize that parameter before the next argument. |
| Entry | Evaluate selected entry contracts, then enter the body. |
| Result preparation | Evaluate return expression and construct the unpublished result once. |
| Body retirement | Retire return-expression temporaries and remaining body locals. |
| Prepared normal return | Check ensures while parameters and admitted receiver designations remain live. |
| Final completion | Retire parameters and perform applicable exit-invariant checks. |
| Publication | Publish the completed result. |

Void returns omit a value construction; reference returns bind their admitted referent. Failure shall follow its selected outlet at the reached stage. A failure before ensures prevents that check; a later retirement failure still governs the unpublished result. Chapter 28 supplies the authorized cleanup and terminal behavior.

The caller's call-expression summary shall include its own argument expressions and parameter-admission work. The callee body bound governs its selected execution phase. Mandatory destination construction shall retain that attribution even when caller evaluation and parameter storage share a physical slot.

### 1.1 Sequencing and effect algebra

A path's effect set shall be the union of its possible operations, including required cleanup. Branch summaries shall conservatively union reachable paths, while execution shall evaluate only selected branches. Composition shall retain source order and synchronization dependencies in addition to the set. Optional interprocedural inference shall follow Chapter 24's analysis mode; opaque calls shall use their bound summary.

A handled throw shall contribute the handler and other observed operations; escaping propagation shall contribute throw. Returning Err shall be ordinary result delivery. Required terminal actions shall remain represented on paths that end at that outlet. Reordering shall satisfy the core equivalence or expressly selected native-transformation contract.

### 1.2 Destructors and generated operations

Generated/defaulted copy, move, destruction, Cleanup, and rollback shall compose the operations required by the selected member/base plan. A manual destructor shall include its reachable explicit and remainder obligations. A live moved-from object shall retain its eventual retirement effects.

Failure-boundary composition shall follow Chapter 28. A Release destruction boundary shall represent its terminal outlet when an exception escapes; a continuing aggregate boundary shall represent its permitted propagation/collection. An ordinary throwing call contributes throw; an actually selected local terminal boundary contributes its terminal effect. Explicit capture handles only propagation reaching its handler.

Storage reconstruction and responsibility changes shall contribute their actual generation, ownership, memory, and lifetime transitions. Whole shall retain Chapter 06's coordinator control effect.

## 2. Borrow regions, escape bounds, and ownership transitions

A borrow contract shall identify its lifetime source, admissible region, qualification, and validity interval. Ordinary raw pointers and aliases shall use the memory chapter's corresponding obligations. Parameter annotations describe the selected callable's permitted use.

| Annotation | Boundary guarantee |
| --- | --- |
| `[[noescape(p)]]` | Retention ends at the call, except the separately declared returned-borrow path. |
| `[[returns_borrowed_from(p)]]` | Returned access is bounded by the source lifetime and compatible qualification. |
| `[[consumes(p)]]` | Perform the selected ownership/responsibility transition under the API's success/failure contract. |
| `[[requires_initialized(slots...)]]` / `[[initializes(slots...)]]` | Apply Chapter 06's bound construction-state summary. |
| `[[lifecycle_effect(whole)]]` | Admit propagation of Chapter 06's Whole control effect. |

A returned borrow with several possible origins shall publish all of them; unresolved possible sources shall remain live until a permitted refinement selects the actual origin. Ordinary by-value source objects shall retain their selected moved-from and destruction contracts after a consuming operation.

### 2.1 Additional retention contract

`[[retains(p, owner)]]` shall designate a named owning parameter or explicitly typed returned owner that may retain a borrow derived from p. Referent validity shall follow its own lifetime source; any mechanism prolonging that lifetime shall be explicitly part of the retention contract.

Independent retention beyond the call conflicts with noescape. The separately declared returns_borrowed_from path is admitted when it is the sole surviving designation. A retaining operation shall establish resource admission and last-use/quiescence obligations before publishing its retained handle. Failure shall follow the API's stated ownership guarantee. An opaque callback shall use its declared retention contract or an open conservative summary.

### 2.2 Escape proof obligations

A returned, stored, captured, or task-transferred borrow shall cover every access admitted by its resulting interface. Evidence may be a static lifetime, a selected checked owner token, or an explicit external-lifetime obligation. Ordinary unknown obligations shall use Chapter 24's analysis classification and Chapter 08's ANOMALY policy. Required proof and definitely invalid lifetime rules retain their corresponding acceptance requirements.

Borrow copying, type substitution, const qualification, and handle movement shall preserve the original validity bound. A retained foreign callback shall keep its designated storage live until the provider acknowledges last use/quiescence. Explicit checked-view metadata shall follow that view's representation and resource contract.

### 2.3 Transfers and failure atomicity

A consumes operation shall publish its success transition and failure responsibility. Its more specific storage, BigInt, collection, or Task/Thread guarantee governs which owner remains responsible on failure.

Ownership commitment and successful return publication are separate events. A committed in-place replacement shall retain its new owner through a later retirement failure. An unpublished returning/delivering value shall be retired on its permitted continuing failure path. Source consumption shall remain consumed, including Task delivery that subsequently retires its unpublished receiver. Attempted allocation and deallocation shall retain their selected resource effects, including a normal Err result.

## 3. Async admission, execution, and cancellation effects

An async callable shall publish separate admission and task-execution contracts. `effects` governs task execution, completion, and cleanup; `admission_effects` governs frame/support admission, capture transfer, additional parameter binding, and the cleanup these create. Each omitted bound is open. The admission attribute is admitted on async declarations.

```cpn
[[admission_effects(allocate(context))]]
[[effects(read(input), io, suspend, cancel_point)]]
declare async u32 fetch(std::task::Context context,
                        Span<const<u8>> input);
```

The input borrow shall remain valid for its execution-time uses. Resource attempts shall use the Context's selected domains. Capture transfer and additional parameter binding shall contribute their actual throw, terminal, and resource effects to admission.

The call expression shall follow Chapter 17: evaluate callable/Context, admit final frame storage, then transfer captures and evaluate/construct subsequent arguments and parameters. Explicit/default argument expressions remain caller-side effects, including a prvalue constructor using a frame parameter's final slot. A failed frame admission shall publish the prescribed failed Task before later argument evaluation. Start, join, await, and detach shall use their own later-call contracts.

Selected async requires checks shall execute after complete admission and before successful cold-call execution-initialization commitment and Created publication, under the admission caller's context. Selected ensures checks shall execute on prepared normal task return: construct the result, retire expression temporaries/body locals, check ensures while parameters/captures remain live, then retire those parameters/captures and perform final exit checks. Completion storage shall retain the ownership prescribed by the Task protocol.

A cancellation request shall take effect only at its admitted selection point. If cancellation wins the completion commitment, the unpublished result shall be retired before Cancelled publication. A selected language-failure or terminal outlet shall follow Chapter 28. The task body shall use its bound execution-context policy; explicit strict/status contexts retain their selected observations, while Native uses Chapter 04's native context contract.

### 3.1 Cancellation checkpoint vs ordinary return

cancel_point shall admit cooperative cancellation at the lexical async checkpoint defined by Chapter 13. Acceptance shall select the required cleanup and Cancelled outcome. An ordinary helper may observe a token and return to that checkpoint. External retained-frame users shall acknowledge quiescence before frame release.

suspend, block, spawn, and cancel_point are separate effect permissions. A callable performing several of them shall admit each actual category. Progress and compensation guarantees shall come from the selected operation/provider contract.

### 3.2 Thread and detached work effects

Thread creation or detached submission shall contribute spawn at admission. Joining, lock acquisition, and synchronized completion shall contribute synchronize and block where applicable. Close shall include admitted cleanup and completion-callback effects. Each callback shall execute under its declared entry context and failure boundary, including when invoked inline. Detached work shall retain its owned borrow and module-lifetime obligations.

## 4. Static initialization and consteval boundaries

A static initialization summary shall include initializer evaluation, construction, readiness dependencies, observable registration, and continuing failure cleanup. An initializer with external effects shall satisfy its cancellation/compensation contract or use the finish policy. Its readiness edge constrains execution order; the initializer's callable contract governs its other effects.

Constant-initialized nodes shall retain their logical dependency classification. Required constant evaluation shall use the admitted operations and resources of Chapter 10. An unevaluated branch contributes no execution effect; each selected compile-time path shall satisfy that evaluator. Generation shall validate emitted effect contracts at the declaration and completion stages in Chapter 23.

## 5. Foreign calls, callbacks, and native ABI

A foreign boundary shall satisfy its selected object-file, callable ABI, lifetime, failure, resource, and effect contracts. C/C++ consumers shall receive applicable requirements through the provider descriptor, compatible header, or explicit adapter. A foreign import with an unverified body shall use its declared external-contract obligation or the conservative open bound.

A stronger local checking adapter shall implement its own validation. A prohibited exception escape shall follow the selected foreign terminal boundary in Chapter 28; an explicit programmer handler may translate an admissible exception to a declared error value. A Result-to-C adapter shall apply its output-state and write-on-success contract. External side effects and allocator release authority shall retain their provider-defined ownership.

### 5.1 Callback effects

Callback registration shall describe inline execution, concurrency/reentry, retention duration, execution agent, and relevant FP-context behavior. Registration and later callback execution shall have distinct phase contracts. Retained callbacks shall have a matching last-use/quiescence protocol and storage/code lifetime.

The selected callback adapter shall define context representation, calling convention, ownership, allocation, and failure boundary. A verified boundary or explicit wrapper shall supply any guaranteed termination behavior promised by a CPN26 noexcept callback interface.

## 6. Effect-aware generic and callable substitution

For candidate bound A and destination bound B, effect substitution shall require A to be a subset of B after normalizing parameter positions, receiver identity, and callable phase. It shall also satisfy borrow origins, retention, ownership, failure, value-contract variance, and ABI compatibility. Region names at equivalent parameter positions denote the same canonical binding; invocation-specific aliasing leaves that declared identity unchanged.

A compatible narrower bound may adapt to a wider bound. Strengthening an unverified bound shall require the corresponding proof or an adapter implementing that guarantee. A generic closed-bound requirement shall be established by its selected callable signature/witness under Chapter 27.

The optional std.effects module shall provide these compile-time queries:

| Query | Result |
| --- | --- |
| `effect_contract_of(FunctionInfo)` | Descriptor of the callable's public phase-specific bound, if available. |
| `subset(A, B)` | Compile-time Boolean under the standard normalization order. |
| `has(A, effect_kind)` | Whether A admits the requested category. |
| `is_open(A)` | Whether A is conservative/open rather than a closed upper bound. |
| `borrow_sources(FunctionInfo)` | Named/position-based returned-borrow sources and retention contracts. |
| `admission_effects_of(FunctionInfo)` | Bound for an admitted async callable's creation phase. |
| `execution_effects_of(FunctionInfo)` | Bound for the selected callable execution phase. |

Each query shall use accessible published contract data. Unavailable information shall produce its named capability/query error. Runtime descriptor materialization uses its separate selected operation.

### 6.1 Type-constructor and associated effect substitution

A callable obtained through a constructor or associated projection shall satisfy the same phase and substitution rules. A public projected type retaining an input borrow shall expose that origin/retention contract in the generic signature. A type-equality proof supplies type identity; the corresponding operations shall establish their own value, lifetime, and ownership requirements.

## 7. Function pointer, closure, and virtual-boundary identity

A callable's semantic type shall retain the effect/lifetime contract defined by Chapters 10 and 24. The chosen native ABI or explicit context adapter shall define its machine representation. Closures shall retain their capture and invocation effects.

Virtual overrides shall preserve the base callable contract under Chapter 24's variance rules. Shared callable identities shall carry these requirements in their semantic boundary records under Chapter 21. A conflicting public contract shall require correction or an explicit compatible bridge before linkage. ABI layout and symbol effects shall follow the selected target profile.

## 8. Synchronization, I/O, and FP observability

Atomic and synchronization operations shall retain their selected memory-order and progress contracts under Chapter 13. The effect categories describe their permitted actions; operation descriptors supply lock-free, ownership, waiting, and cancellation details.

An I/O operation shall retain its published partial-success and resource effects. A prefix-producing write may return Err after committed output. Formatting that allocates shall admit its resource effect; serialization into an existing buffer shall describe its destination write and any additional effects.

Floating operations shall contribute fp_status/fp_control according to Chapter 24's vocabulary and Chapter 04's selected observability. Explicit Strict, Reproducible, report, try, and environment operations shall retain their specified status/control effects. Ordinary Native operations shall use the provider's native result, fault, subnormal, NaN, and relaxation contract without required local/sticky accounting. Later status inspection observes that declared provider state; it adds no retrospective strict requirement. Explicit strict boundary adapters shall isolate native clobber where their selected caller contract requires it.

## 9. Diagnostics and decision procedures

The checker shall use Chapter 24's single declared/proved/unknown classification and Chapter 08's diagnostic policy. Release local inference shall consume current-definition facts and bound summaries. Required callable/generic constraints shall use Chapter 27's standard decision procedure independently of optional inference depth.

### 9.1 Transformation obligations

For each proposed transformation, the implementation shall preserve the observations selected by the affected contracts:

| Contract | Required preservation |
| --- | --- |
| Named checked/report/Result operation | Selected failure/value/status outlet and argument evaluation. |
| I/O and resource transition | Committed effects, owner changes, and specified failure guarantees. |
| Lifetime and borrow | Required cleanup, generation identity, and admitted access interval. |
| Async admission | Frame-failure boundary, argument evaluation, and task-phase separation. |
| Foreign callback | Its declared effects, retention, and entry boundary. |
| Explicit Strict/Reproducible arithmetic | The selected zero/NaN/status, rounding, and reduction contract. |
| Ordinary Native arithmetic | Its provider-permitted transformations and all independent source side effects, memory accesses, atomic events, and required fault behavior. |

## 10. Configuration, semantic records, and conformance

The bound callable contract shall retain phase bounds, normalized regions, ownership/borrow contracts, value-contract policy, function ABI, exception boundary, and effect vocabulary revision. Chapter 21 shall govern its semantic identity and optional external publication. The defining declaration shall bind semantic configuration; an importing diagnostic profile affects only the importer's permitted diagnostics.

A conforming effect implementation shall support its admitted syntax, normalization, redeclaration/override checking, open-bound behavior, phase composition, and selected diagnostics. Optional introspection or runtime checking shall follow the resolved capability set. Implementations shall preserve the selected core and feature contracts while choosing their internal analysis, state representation, and code generation.

