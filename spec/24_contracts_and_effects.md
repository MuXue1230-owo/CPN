<a id="chapter-24-contracts-effects"></a>

# CPN26 Contracts and Effect Signatures Specification

## 1. Scope and normative terminology

A callable contract shall describe three independent components: value/state requirements at defined boundaries, an effect upper bound for each callable phase, and lifetime/ownership transitions. This chapter owns the predicate rules, effect vocabulary, and validation modes. [Chapter 25](25_effect_composition_and_boundaries.md#chapter-25-effect-composition-boundaries) defines their composition across calls, tasks, ownership transfers, and foreign boundaries.

An effect denotes a possible action under the selected [abstract-machine observation contract](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance). Result alternatives are ordinary values. Failure effects shall use the selected outlet in Chapter 28; numerical operations shall use Chapter 04's resolved profile. Descriptors are static interface material; a runtime check exists when its selected contract requires evaluation.

## 2. Contract and effect syntax

Standard contract declarations use ordinary leading or permitted trailing attribute lists. The schema of these attributes is normative rather than an arbitrary user-defined expression macro:

```ebnf
contract-attribute = "requires", "(", contract-expression, ")"
                   | "ensures", "(", contract-expression, ")"
                   | "invariant", "(", contract-expression, ")"
                   | "effects", "(", effect-bound, ")"
                   | "admission_effects", "(", effect-bound, ")"
                   | "retains", "(", parameter-name, ",", owner-name, ")";
owner-name = parameter-name | "return_value";
effect-bound = "none" | effect-item, { ",", effect-item };
effect-item = "read", "(", effect-region, ")"
            | "write", "(", effect-region, ")"
            | "allocate", "(", effect-domain, ")"
            | "deallocate", "(", effect-domain, ")"
            | "volatile" | "atomic" | "synchronize" | "io"
            | "block" | "spawn" | "suspend" | "cancel_point"
            | "throw" | "trap", "(", trap-kind, ")"
            | "fp_status" | "fp_control"
            | "whole" | "foreign";
effect-region = "any" | "global" | parameter-name | "this";
effect-domain = "any" | parameter-name | "global";
trap-kind = "numeric" | "contract" | "any";
contract-expression = ? a well-typed Boolean expression with only admitted read effects
                        obeying the restrictions of Section 4 ?;
```

The parser shall interpret attribute payloads using their registered schemas. Attribute-schema words retain their ordinary lexical status outside that schema. Payload binding is a declaration-time operation. For example:

```cpn
[[requires(divisor != 0), ensures(return_value >= 0)]]
[[effects(read(data), trap(numeric))]]
declare i32 magnitude(const<i32>& data, i32 divisor);

[[effects(none)]]
declare u32 encode_tag(u8 code) noexcept;
```

The standard effects schema shall retain its registered identity. Parameter names in effects shall resolve to canonical parameter positions for signature identity; overload identity follows the type specification.

A record-level `[[invariant(expression)]]` shall apply to a complete native class, struct, or tagged union. A foreign adapter supplying an invariant shall establish its representation and synchronization contract. The record and all reflected/generated contributions shall retain their owning-module and bound-configuration requirements.

An attribute requires shall state a value precondition. A generic requires clause shall determine compile-time candidate eligibility under Chapter 27. Each shall be checked in its own phase.

## 3. Effective effect signatures and open-world defaults

For each callable phase, `[[effects(S)]]` shall bound every externally observable effect that phase may perform, including selected calls and required completion. A missing bound is open under the selected capabilities. An opaque call shall contribute its declared bound, or the conservative open bound when no narrower contract is available.

`effects(none)` is the empty bound. Computation on independent local values and inert local cleanup may satisfy it. Access through an input pointer/reference contributes its specified region effect. Caller-side argument evaluation and parameter admission retain their own phase attribution in Chapter 25.

`noexcept` shall exclude language-exception propagation across its phase boundary. Internal handled exceptions retain their ordinary effects. Other terminal outlets, Result values, cancellation, Whole, allocation, blocking, and divergence shall be governed by their own effect categories. A simultaneous noexcept and escaping-throw declaration is contradictory. Termination and progress promises require their own contract, including never's normal-return rule.

### 3.1 Effect categories

| Category | Governed observable behavior |
| --- | --- |
| `read(p)` | Read through the region reachable from argument `p` or the receiver `this`, excluding independent local copies. |
| `write(p)` | Modify the region reachable from p or this under its separate authority and synchronization obligations. |
| `read(global)`, `write(global)` | Read/write externally observable global or static state. |
| `read(any)`, `write(any)` | Respective access to any permitted region, including opaque indirect accesses. |
| `allocate(d)`, `deallocate(d)` | Acquire/release storage or persistent allocation accounting in resource domain `d` or `any`; attempted admission that fails without a durable allocation is still a possible allocation effect. |
| `volatile` | Perform a volatile access or provider operation with comparable volatile visibility. |
| `atomic` | Perform atomic access under the selected memory order; synchronization edges follow that order's contract. |
| `synchronize` | Create or participate in lock, fence, wait/notify, release/acquire, or equivalent synchronization actions. |
| `io` | Produce or consume externally observable device, file, network, console, or process/environment I/O. |
| `block` | Potentially stop progress awaiting an external event or other execution agent; this is distinct from suspending a CPN26 coroutine. |
| `spawn` | Initiate a new independent execution agent or schedule owned work. |
| `suspend` | Suspend the current async execution frame and resume through its continuation protocol. |
| `cancel_point` | Accept a cancellation request and transfer along the defined cooperative cancellation exit. |
| `throw` | Allow a language exception to cross this callable phase's exit boundary. |
| `trap(numeric)`, `trap(contract)` | Admit the corresponding terminal outlet. `trap(any)` admits the standardized synchronous nonreturning failure outlets, including mandatory local exception-boundary termination. |
| `fp_status` | Read or update floating status observed under the selected numerical contract. |
| `fp_control` | Read/change observed FP controls or perform a context switch that changes those observed controls. |
| `whole` | Invoke the permitted destructor-coordinator Whole control transfer. |
| `foreign` | Enter a foreign execution boundary with effects not fully represented by native regions, or with a separately declared foreign provider effect contract. |

`read(p)` shall cover the region reachable through p under its declared bounds. A published exact-subregion descriptor may narrow that region when its evidence and schema are available. Pointer validity, alignment, aliasing, provenance, and lifetime remain the corresponding memory obligations; effect regions may overlap.

A write(p) bound shall include the reads of the same value needed to compute that write when those reads have no independent observable effect. An independently observable read shall require read(p). A declaration may list both bounds explicitly.

An atomic operation shall additionally carry synchronize when its selected order participates in inter-agent synchronization. Volatile, atomic, and synchronization obligations shall each follow Chapter 13. I/O shall additionally carry block when it may wait for an external event.

A foreign call shall use its published effect contract. A verified adapter may expose a fully translated native bound when it accounts for all observable behavior and ABI requirements. An opaque foreign call shall retain its conservative foreign bound.

### 3.2 Cleanup and completion effects

A phase bound shall include its return construction, temporary/local/parameter retirement, Cleanup, permitted rollback, resource transitions, and selected calls. Chapter 25 assigns these operations to their caller, admission, execution, and completion phases.

An explicitly checked value operation may contribute trap(numeric); its corresponding Result operation contributes the effects of its value computation, status delivery, and resource work. Each replaces only its own specified failure outlet. Native numerical operations shall use their provider-declared value/fault/environment contract. A selected ContractTrap boundary shall contribute trap(contract). These contributions shall reflect the resolved operation rather than a presumed universal arithmetic mode.

## 4. Preconditions and postconditions

`[[requires(P)]]` shall state a condition at completed parameter admission before body entry. Its variables refer to admitted parameters and an eligible live receiver. An exported condition is a caller obligation and, in check mode, an entry predicate. Argument expressions and parameter construction occur once under the call contract.

`[[ensures(Q)]]` shall state a condition at Chapter 25's prepared normal-return boundary: after result construction and body-local cleanup, while parameters remain live, and before their retirement and final publication. A nonnormal path uses its selected failure/control outlet. Passing ensures establishes that check only; later retirement and completion retain their own failure behavior.

`return_value` shall designate the single constructed result, or the admitted referent of a reference result, through a read-only view. It is available for non-void ensures clauses. Named parameters shall expose their current values, including moved-from states. Returned borrows shall cover the caller's admitted use after publication. A returned Result, including Err, shall satisfy applicable ensures through valid active-case access.

A predicate shall have bool type and a closed admitted evaluation contract: reads of valid live regions and value computations that allocate nothing, propagate no language exception, cause no terminal transfer, suspend no task, block no agent, and produce no observable state/status mutation. Observer calls shall have a compatible closed bound and established nonfailing nested checks. FP predicates shall select nonraising comparison or representation/classification operations. Their required providers shall be available at declaration binding.

Raw or shared designations in a predicate shall carry the appropriate lifetime and synchronization obligation. A proved invalid designation is invalid source; an admitted but unproved ordinary obligation shall use the central ANOMALY policy. Document mode shall retain that obligation without executing the predicate. Prove mode shall establish its required evidence; check mode shall evaluate only under its valid access contract. Volatile, atomic-status, mutation, and exception-aggregate observations lie outside this pure predicate domain.

A selected check whose predicate is false shall enter ContractTrap. A required constant evaluation shall apply its corresponding success rule. The optimizer may use a predicate as an assumption when proved, established by a dominating check, or selected under the explicit trusted contract in Section 6. An unchecked documented requirement remains a programmer obligation.

### 4.1 Completion values and explicit snapshots

An ensures expression shall read values accessible at its completion boundary. A before/after comparison shall carry its prior value through an explicitly constructed argument, object, or operation-specific result. Those values shall use their ordinary construction, resource, and lifetime contracts.

### 4.2 Multiple conditions and failure order

Checks shall evaluate clauses in declaration order, preserving source order within an attribute list and ordinary Boolean short-circuiting. Each reached clause shall execute once. The first false clause shall select the failure boundary. Elimination of a proved-true clause shall preserve the observations selected by the check policy.

A check diagnostic shall identify the stable declaration and clause ordinal. A policy omitting execution shall report only established analysis facts. Invalid memory access during an admitted predicate execution shall follow its memory-failure contract.

## 5. Record invariants and lifecycle boundaries

A record invariant shall describe a complete Alive object at its stable exposure boundaries. Under a checking policy, it shall be evaluated after complete construction, at entry to eligible public Alive-receiver operations, and at the normal-return exposure of eligible public mutating operations. A base invariant shall apply at the corresponding live base boundary. Construction and destruction phases shall use Chapter 06's own state contracts.

An external mutable alias shall retain its memory and synchronization obligations between boundaries. Optimizer reliance shall use Section 6's proof/check/trust rule. A representation constructor or foreign adapter shall establish the invariant before publishing a conforming native record. A raw representation operation that changes the property shall leave restoration to the programmer before subsequent invariant-governed exposure. Optional invariant validation shall follow its selected policy.

## 6. Contract validation and configuration

Chapter 08 supplies the sole key/domain/default table. The owning declaration shall bind its validation policy and publish that policy with its contract. An importer shall use that bound contract.

| Validation mode | Required behavior |
| --- | --- |
| check | Evaluate reached predicates and select ContractTrap on a false result. Attribute their admitted reads and possible terminal outcome as boundary-check effects. |
| prove | Establish every required reachable entry/normal-return condition; failure to establish required evidence is a compilation failure. |
| document | Preserve the stated obligation and applicable analysis diagnostic. Execution and optimizer assumptions require their separate authority. |
| trusted | With contracts.trusted_assumptions selected, permit compiler reliance on the stated condition under the author's explicit correctness obligation. |

An unmet trusted promise falls outside that explicitly selected optimization contract's guarantees. Disabling optional value-contract checking shall preserve the source declarations needed for type, generic, and ABI compatibility. Ordinary language lifetimes and explicitly selected operation checks remain their own functional contracts.

Effect inference shall use the mode resolved by Chapter 08. Local mode shall inspect the current CFG and bound declaration/interface summaries. Interprocedural mode may additionally analyze available callee bodies to a conservative fixed point. Both shall preserve the distinction between a declared obligation, established evidence, and unknown implementation behavior. Release defaults to local mode; whole-program proof is an optional analysis strategy. Explicit proof and generic requirements shall retain their own acceptance rules.

## 7. Callable identity, redeclarations, and override compatibility

A callable signature shall retain its ordinary types, receiver, async admission shape, linkage/ABI, nonthrowing guarantee, normalized lifetime/ownership contracts, and effect bound. Address taking, indirect calls, generic witnesses, and virtual dispatch shall preserve that contract. Declarations differing only in effects shall redeclare the same ordinary overload and require compatible canonical contracts.

Chapter 25 shall define callable-bound substitution, phase-specific compatibility, and foreign adapters. An override shall admit every state permitted by its base precondition and establish at least the base postcondition on successful return. Stronger internal checks shall therefore preserve all valid base-contract calls.

A foreign ABI descriptor shall distinguish semantic contract fields from physical calling representation. Verified local wrappers may strengthen a foreign entry's exposed checks while preserving a consistent underlying symbol contract.

## 8. Generic constraints and effect queries

A generic effect requirement may depend on its declared callable witness and enabled compile-time metadata. The optional std.effects surface and query identities shall have their single definition in Chapter 25.

The definition shall bind its required effects, and Chapter 27 shall establish them for each selected witness. A closed declared contract supplies its published evidence; an open bound remains conservative. A generic returning a callable shall preserve that callable's selected type and captured policies. Changes affecting canonical effects shall enter instance identity and interface compatibility.

### 8.1 Associated callable witnesses

An associated operation witness shall preserve the receiver, return category, nonthrowing, borrowing, retention, consumption, phase effects, and ABI contracts specified in Chapter 26. Chapter 27's proof procedure shall establish its relationship to the required bound, using immutable declaration-site contracts.

## 9. Diagnostics and soundness of optimization

The checker shall classify facts using the following semantic outcomes. Chapter 08 determines their diagnostic categories, filtering, and promotion.

| Fact | Semantic outcome |
| --- | --- |
| Malformed schema, contradictory contract, proved bound violation, or inadmissible phase | Invalid declaration or use. |
| Ordinary opaque call or external lifetime obligation remains unproved | Admitted programmer obligation; retain its ANOMALY disposition and conservative implementation knowledge. |
| Explicit prove requirement or required generic evidence is missing | Required proof/constraint failure. |
| Checked runtime predicate is false | ContractTrap. |
| Required constant contract evaluation fails | Required-evaluation failure. |
| A precise valid implementation summary is established | Evidence available for permitted optimization and diagnostics. |

An inferred implementation summary shall refine internal knowledge while preserving the published declaration contract and source-bound initialization plan. An open-bound witness shall remain open during a generic's closed-bound requirement check. A compiler shall base backend assumptions on established evidence, dominating validation, or explicit trust, and shall preserve required CPN26 terminal edges under its selected lowering. The [core transformation rules](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance) govern code motion, elimination, and folding.

## 10. Required semantic examples

```cpn
[[effects(none)]]
declare u32 identity(u32 n) noexcept;

[[requires(source.size() > 0)]]
[[effects(read(source))]]
declare u8 first(Span<const<u8>> source) noexcept;

[[effects(read(source), write(destination), trap(contract))]]
[[requires(destination.size() >= source.size())]]
declare void copy_into(Span<u8> destination, Span<const<u8>> source);
```

The first declaration shall require a valid nonempty span. Selecting checked entry validation shall add its ContractTrap boundary effect to the body's read(source) effect. Document mode shall retain the caller obligation. Copy_into shall additionally state its permitted overlap behavior under the region contract. Noexcept shall retain its language-exception meaning alongside the independent trap(contract) outlet.

```cpn
[[requires(divisor != 0), ensures(return_value >= 0)]]
[[effects(trap(numeric))]]
declare i32 bounded_quotient(i32 numerator, i32 divisor);
```

A bounded_quotient implementation choosing checked arithmetic shall include its possible NumericTrap in the stated effect bound. Establishing a nonzero divisor shall discharge the division-by-zero condition; the selected division operation shall separately require its signed-overflow policy and range conditions. Native ordinary arithmetic shall use its provider-declared effects under Section 3.2.

```cpn
[[effects(allocate(resource), write(destination))]]
declare Result<void, AllocError>
    initialize_buffer(ResourceRef resource, OwnedBuffer& destination);
```

Err shall be a normal result value. Initialize_buffer shall retain attempted-allocation and permitted-mutation effects. An implementation releasing old storage shall additionally admit deallocate(resource); old-element retirement shall contribute its actual throwing, terminal, or I/O effects under Chapter 25.

```cpn
[[ensures(return_value == input)]]
[[effects(none)]]
i32 identity_with_postcondition(i32 input) noexcept {
    return input;
}
```

The result shall be constructed once. Ensures shall read the still-live input parameter at the prepared-return boundary. A selected checked predicate shall contribute its possible ContractTrap to the contract-boundary descriptor.

The following completion distinctions are required:

| Boundary case | Required behavior |
| --- | --- |
| A return explicitly moves a parameter into its result. | Ensures sees the live parameter's current moved-from state and the constructed result, not a hidden copy of the entry value. |
| Body-local destruction fails before the prepared normal-return boundary. | The selected failure path governs the unpublished result before reaching ensures. |
| Ensures passes, then a parameter destructor propagates a permitted failure. | The caller receives no successful return; continuing cleanup retires the unpublished result without restoring consumed ownership. |
| Ensures evaluates to false under `check`. | ContractTrap occurs without parameter destruction or result rollback being added by the contract facility. |
| A Result-returning body constructs `Err`. | The ordinary normal-return path evaluates ensures for the Result value. |
| An async ensures check passes, then cancellation wins at successful-return commitment. | The uncommitted result is retired and Cancelled is published only after required cleanup; passing ensures did not publish Value. |
| A reference result designates a parameter-owned subobject that will die during exit. | The borrow/lifetime violation remains invalid even if the referent was readable during ensures. |

## 11. Conformance and boundary preservation

Each callable shared across a semantic boundary shall retain its canonical phase bounds, contract policy, parameter-position mapping, lifetime/ownership requirements, and ABI identity in its bound interface contract under Chapter 21. A consumer shall bind that contract, use a verified adapter, or apply the ordinary conservative opaque-import contract. Conformance shall preserve declared phase obligations independently of optional analysis depth and runtime validation selection.

