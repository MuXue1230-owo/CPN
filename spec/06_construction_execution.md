<a id="chapter-06-construction-execution"></a>

# CPN26 Construction and Destruction Execution Specification

## 1. Scope and Required Distinctions

This chapter owns object and subobject state, construction planning, delegation, destruction responsibility, Whole, Cleanup, Abandon, and storage reuse. Implementations shall apply these transitions within the [abstract machine](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance). Configuration and validation defaults belong to [Chapter 08](08_runtime_configuration.md#chapter-08-runtime-configuration); failure outlets and continuation belong to [Chapter 28](28_error_and_recovery.md#chapter-28-error-recovery).

Each object lifetime shall identify its storage extent and destruction responsibility separately. Lifetime termination consumes the selected destruction obligation; storage release consumes the separate storage-ownership capability. Responsibility transfer preserves object location and storage ownership. Reconstruction shall establish a new generation, including at the same address and with the same type.

For inheritance and Whole, the complete-object boundary shall be the most-derived class lifetime containing the selected base. Each class-valued member or array element shall have its own inheritance boundary. Whole shall affect that boundary and its associated destruction continuations.

The cleanup algorithms below shall execute on the continuing paths admitted by the selected failure outlet. A terminal outlet shall end execution at its defined boundary. Native numerical operations use their selected native fault/result contract; named checked operations retain their specified failure outlet.

## 2. Declaration and Lifecycle Grammar

The [consolidated grammar](15_grammar_binding.md#chapter-15-grammar-binding) is authoritative for lifecycle source forms. This chapter assigns the following operations their meaning:

| Source form | Semantic role |
| --- | --- |
| `T object(arguments) -> { ... };` | Ordinary construction plus a construction tail in one transaction. |
| `init member(arguments);` | Explicit initialization producer. Base and virtual-base selectors identify their corresponding slots. |
| `delegate(arguments);` | Invoke the selected constructor activation at this statement. |
| `~T() { ... } cleanup { ... }` | Destructor body followed by the layer's Cleanup phase. |
| `Complete member;`, `Complete base<B>;`, `Complete virtual_base<V>;`, `Complete;` | Select the local destruction responsibilities in Section 7. |
| `destruction_owner<V> = base_path<...>;` | Bind the unique virtual-base obligation to a nominated class layer. |

`class Manual T` shall select the local-member policy in Section 7. Complete and owner declarations shall appear in the class body. A destructor shall have one zero-parameter declaration with the dedicated return-type-free syntax. Its noexcept contract shall cover its body, Cleanup, and generated obligations. Virtual properties and other function modifiers shall follow Chapter 10.

`base_path<Left, B>` shall identify successive direct-base edges from the operation's statically typed view, or from the declaring layer for an Owner declaration. Each edge shall exist and the final entry shall identify the selected subobject. A type-only selector shall require a unique reachable match. Initialization and takeover selectors shall retain their direct-base or virtual-base scope. The compile-time path shall disambiguate requests such as `destroy_base<base_path<Left, B>>(object)` and corresponding Owner bindings.

Object declarations, function declarations, const qualification, and constexpr requirements shall use Chapter 10 and Chapter 15. In an ordinary declaration context, the parser shall classify `T name(...);` as an object declaration and diagnose its initializer under that classification. An external-linkage declaration context shall use Chapter 15's dedicated function, external-object declaration, and define-object productions; a define-object shall use this chapter's initialization transaction.

An omitted or empty argument list shall select typed default initialization. Basic types shall receive their defined zero value; a class shall invoke viable default construction. A type lacking that operation shall require an explicit initializer. The selected type contract shall determine its representation.

Construction shall initialize a const object through its construction permissions. After the relevant subobject becomes initialized, mutation shall require its ordinary qualification contract. Destruction and authorized storage operations shall use their independent lifetime and ownership permissions.

```text
i32 count(10);
auto copy(count);
const i32 limit(64);
constexpr i32 capacity(256);
Widget item(args) -> {
    init cache(cache_args);
    inspect_initialized_members(this);
};
```

A construction tail shall contribute initialization declarations to the same transaction and execute its ordinary statements after the selected constructor and delegation chain return. The object shall become Alive after the tail completes. An omitted constructor argument list shall select default construction. The transaction shall construct directly in final storage.

A class shall have viable generated default and aggregate candidates. The aggregate shall initialize direct nonstatic members in declaration order and default-construct bases. A user constructor with the same signature shall replace that candidate; other generated candidates shall retain their individual viability requirements. A missing default for a required base or omitted member shall make that candidate unavailable.

## 3. Object State and Canonical Order

A complete-object transaction shall have Constructing, Alive, Destroying, Destroyed, or Abandoned state. Destructor Body and Cleanup shall be subphases of Destroying. Whole shall be the irreversible control condition defined in Section 9.

Each immediate subobject slot records, logically, one of Pending, Constructing, Alive, Destroying, Destroyed, or Abandoned. A slot also identifies its current lifetime generation and destruction strategy. These are semantic distinctions. The implementation shall represent each distinction only to the extent required by selected execution and validation contracts, using control flow, activation data, or an admitted storage registration.

Canonical construction order is:

1. Distinct virtual bases of the most-derived object, in dependency-respecting depth-first order, following base declarations left to right and emitting a virtual base after its own base dependencies; emit each virtual-base identity once.
2. Direct nonvirtual bases in declaration order.
3. Direct nonstatic data members in declaration order.

Each base or member shall complete its recursive construction before the next sibling slot begins. Arrays shall construct in increasing index order. Each class layer shall execute its own hierarchical plan.

The most-derived layer shall supply effective virtual-base initialization declarations. When a constructor is invoked for a base subobject, its virtual-base declarations shall be checked for declaration validity and remain dormant. Evaluation shall visit only producers selected by the effective plan.

The canonical destruction order shall reverse successful construction within this hierarchy. Shared virtual bases shall form one complete-object tail in reverse virtual-base construction order. Intermediate base destruction shall leave that tail to the complete-object coordinator. Explicit early base destruction selects the Whole transition in Section 9.

The following table identifies functional information, independently of optional diagnostic tracking:

| Selected operation | Information required for its result |
| --- | --- |
| Statically determined construction/destruction | Ordered operations, representable entirely by control flow. |
| Catchable partial-construction failure | Successfully completed subobjects or array prefix. |
| Path-dependent first construction or assignment | The selected slot's Pending/Alive distinction. |
| Manual destruction, Whole, and Cleanup | Consumed obligations, continuation, and reverse frontier. |
| Dynamic virtual-base responsibility transfer | The unique current Owner binding. |
| Registered storage reconstruction | Current generation, actual type, and destruction entry. |

An implementation shall preserve this information where the selected functionality observes it. Optional raw-access validation shall follow `memory.raw_validation`; Release's contract mode relies on admitted programmer obligations and omits additional validation metadata. Explicit checked operations shall retain their specified checks. The native ABI determines which activation, sidecar, or storage representation can carry functional state.

## 4. Unified Construction Plan

### 4.1 Plan formation

The compiler shall form one plan for the current construction layer from the selected constructor, statically resolved delegation chain, and construction tail. Each slot shall receive the first applicable producer in this precedence order:

- An explicit `init` declaration.
- Otherwise, an in-class member initializer, if present.
- Otherwise, a source-bound reservation for an ordinary first-assignment operation under the rule below.
- Otherwise, type-directed default construction.

An explicit constructor producer shall override a fallback member or typed default. Every slot shall have at most one effective explicit constructor producer. An ordinary write to a slot with an in-class or explicit initializer shall execute as assignment after that initializer; an eligible uninitialized slot shall use the reservation rule below.

A first-assignment reservation shall require first-write-before-read on every normal completion path in the constructor's source control-flow graph, using explicit `initializes` contracts and bound construction summaries that express declared source contracts. Only this declared interface evidence shall select a producer; additionally inferred implementation summaries shall serve diagnostics and optimization. Required compile-time branch selection applies before this fixed analysis. At a control-flow join, a definite first-write fact holds only when every incoming normal path establishes it. Mutually exclusive first writes share a reservation; successive writes construct and then assign.

When this source-bound rule supplies no reservation, the type-directed default remains the producer. An explicit `initializes` contract shall require the stated entry/exit transition and frontier order. Optional interprocedural analysis may refine diagnostics and code generation; the selected producer, constructor calls, and source effects shall remain those of the bound plan under every analysis mode.

An init declaration shall contribute a declarative producer from the top level of a constructor or construction tail, where it may be interleaved with ordinary statements. Its initializer expression may compute a conditional value. Runtime-dependent control flow shall express construction through eligible ordinary first assignment and its required source-bound state facts.

The declarative initializer environment shall contain constructor parameters, accessible earlier initialized subobjects, static objects, and eligible enclosing lexical bindings. Every referenced lifetime shall cover actual evaluation. Constructor-body and tail-body locals shall instead participate through ordinary statements and frontier-valid first assignment.

A deferred expression shall read its bound environment at its actual evaluation point. Earlier modifications and aliasing effects participate in that value. Each binding shall remain alive through evaluation. Substitution and code motion shall satisfy the core transformation rules for the selected execution contract.

### 4.2 Activation and the initialization frontier

Each constructor invocation has an activation. Its parameter initialization occurs at the actual invocation point. Its explicit producers become available after those parameters exist. A construction tail's declarative environment is available when the object declaration starts its construction transaction, although its ordinary body runs later.

The initialization frontier shall be the first Pending slot in canonical order. Execution shall proceed as follows:

1. Enter the activation and make its declarative producers available.
2. At the frontier, require an available producer and initialized required inputs; evaluate its arguments once, then construct directly in the slot.
3. On success, mark that slot Alive and advance to the next Pending slot.
4. Pause frontier processing at an unavailable activation, first-assignment reservation, or unmet input-state requirement.
5. Execute ordinary statements in source order; resume the frontier after successful first construction or delegated activation entry.
6. Before returning an activation, complete every deferred producer using that activation's parameters.
7. Before committing ordinary construction and its optional tail, establish Alive for every required slot.

A typed-default producer shall be available under its plan; a delegated producer shall become available upon entry to its activation. A plan shall establish a feasible order, live deferred environments, and complete normal paths. Static readiness cycles and violations of those requirements shall fail plan validation.

### 4.3 Delegation

`delegate(arguments);` shall evaluate its arguments once at that statement and invoke the selected overload of the same class using the existing destination and shared plan. The callee's ordinary statements shall complete before execution continues after the delegate statement.

Each activation may contain one direct delegation statement at any unconditional statement position, including an unconditional nested block. The selected chain shall be statically identifiable and acyclic. A surrounding handler may observe and rethrow failure; successful construction shall require successful completion of each reached selected delegation. If a preceding statement exits through failure, subsequent delegation shall remain unexecuted. Runtime-conditional or loop-controlled delegation shall fail this structural requirement.

The caller prelude shall execute before the source-position delegate call. A callee may return with an unrelated caller reservation still Pending when every callee-dependent producer has completed and the callee's accesses satisfy their contracts.

```text
class Example {
    i32 first;
    i32 second;

    Example(i32 x) {
        init second(mark_second(x));
        note();
        delegate(x, 0);
        after_delegate();
    }
    Example(i32 x, i32 tag) {
        init first(mark_first(x));
        inside_delegate();
    }
};
```

The required call order shall be `note`, `mark_first`, `mark_second`, `inside_delegate`, `after_delegate`, following the source-position delegation and canonical frontier.

## 5. First Assignment and Initialization-State Permissions

An ordinary construction-time assignment shall evaluate its destination under the assignment sequencing rule, then dispatch by its state:

| Destination state | Operation |
| --- | --- |
| Alive with the declared type | Execute ordinary assignment. |
| Pending with a first-assignment reservation at the frontier | Evaluate the right-hand side once and construct directly in the slot. |
| Any other state or a Pending slot beyond the frontier | Fail the required state/frontier check. |

Direct construction shall use Chapter 10's prvalue, lvalue-copy, xvalue-move, and explicit-conversion requirements. Ordinary statements shall retain source order.

An initialized assignment shall use its selected assignment operator's failure guarantee. First construction shall publish Alive only after success. Direct construction shall preserve the selected constructor and expression effects.

```text
class Pair {
    i32 first;
    i32 second;
    Pair(i32 x) {
        this->second = compute_second(x);
        this->first = compute_first(x);
    }
};
```

The first assignment is an order error because the first slot is still reserved. A valid declarative rewrite is:

```text
Pair(i32 x) {
    init second(compute_second(x));
    this->first = compute_first(x);
}
```

In the valid rewrite, the assignment shall construct the first slot, then frontier processing shall execute the deferred second producer. A body local may supply the ordinary assignment under its lexical lifetime; declarative producers shall use only Section 4.1's initializer environment.

Address formation, storage metadata, and forwarding a construction-aware view shall preserve the current object state. Reading, member invocation, copying, or value assignment shall require the expected live generation. The this pointer shall carry these same access obligations.

Initialization analysis shall use the resolved `construction.analysis` mode. Local analysis shall examine the current definition's CFG and bound declaration/interface summaries. Interprocedural analysis may additionally inspect available callee definitions. Release defaults to local analysis under Chapter 08; neither mode requires whole-program proof.

Definitions shall satisfy their read, write, initialization, escape, and lifecycle-control contracts. `[[requires_initialized(a, b), initializes(c)]]` publishes construction-state requirements: the named initialized inputs shall be Alive on entry, and each initializes slot shall be Pending on entry and Alive on normal return, respecting the frontier. An opaque call with an open access summary shall require every potentially accessed slot to be Alive. Callers may supply more precise bound contracts. Analysis mode shall preserve the source-bound producer rule in Section 4.

A proved invalid transition shall receive the central mandatory diagnostic. An admitted but unproved ordinary access or caller obligation shall retain its ANOMALY disposition and programmer responsibility. Selected checked views and validation modes shall validate the state before the governed action; contract mode shall retain the source obligation without adding a validation registry. The implementation shall still retain the functional state that selects construction, assignment, ownership, or cleanup. Explicit proof requirements and unavailable type operations retain their acceptance rules.

A selected lifecycle check shall reject before the invalid action and deliver `LifecycleError` through its declared language-failure outlet. Its coverage is the valid object/slot descriptor supplied to that check. Raw and foreign accesses retain their declared access obligations.

## 6. Construction Completion and Rollback

The most-derived object shall commit Alive after its required slots and ordinary constructor bodies, followed by the optional construction tail, complete successfully.

On a permitted construction unwind, the transaction shall destroy completed subobjects in reverse completion order. A failing subobject shall first perform its own partial rollback. An array shall roll back its completed prefix in descending index order. Pending and unsuccessfully Constructing slots shall remain outside completed-object destruction, including the incomplete complete object's ordinary destructor body.

Construction rollback shall discharge established responsibilities for completed subobjects under every Manual, Complete, and Owner policy. Constructor parameters and ordinary locals shall follow their scope-exit contracts. External side effects shall retain their operation-specific postconditions.

Cleanup failure shall follow the failure-outlet table in Chapter 28. A continuing aggregate path shall retain the primary identity, append applicable secondary records, and continue its prescribed attempts.

## 7. Destructors and Responsibility Policies

A class lacking a destructor declaration shall receive an empty-body destructor with generated subobject cleanup. Its availability shall require viable accessible selected cleanup. A user declaration shall supply the body while retaining the specified generated lifetime operations.

`virtual ~T()` shall introduce virtual destruction. Derived destructors, including implicit declarations, shall retain inherited virtual destruction. Other virtual members shall leave the destructor's independently declared status unchanged. Complete derived destruction through a base view shall require virtual destruction or an exact-complete-type checked operation.

Virtual calls during construction or destruction shall dispatch within the active class layer. Same-class delegation shall retain that layer. Each call shall satisfy its receiver-state requirements. Whole shall terminate the affected continuation; calls admitted on remaining independently live subobjects shall use their own active layers.

Local takeover rules are:

| Declaration | Selected local responsibility |
|---|---|
| `Complete member;` | Explicit handling of that direct member before the Cleanup remainder fallback. |
| `Complete base<B>;` | Explicit handling of that direct nonvirtual base subobject. |
| `Complete virtual_base<V>;` | Manual handling of the unique V obligation assigned to this layer. |
| `Complete;` | All direct members and direct nonvirtual bases of this layer. |
| `class Manual T` | All direct members of T; base policies remain separately specified. |

Each takeover shall affect only the named class layer's local obligations. A virtual base shall require its unique Owner binding and, for manual handling, its explicit takeover selection. Base internals shall retain the base layer's own policy.

An ordinary destructor body may destroy or abandon an eligible local slot, or leave a manual slot for Cleanup. Each destruction attempt shall consume its generation's obligation once, including an attempt ending in a continuing exception. A destruction entry shall require an eligible live target; reentry into a Destroying target shall fail that requirement.

## 8. Legal Owners and Virtual-Base Transfer

A legal Owner shall be a compiler-recognized class layer within the same complete object, containing the designated virtual base in its inheritance graph and distinct from that base itself.

After a virtual base completes construction, the most-derived layer shall initially own its obligation. A declaration such as `destruction_owner<Root> = Left;` shall nominate one unambiguous base path and establish its binding when both the obligation and target layer are available. The initial binding shall remain until that point. Competing bindings shall fail validation. Each established binding shall remain until consumed or changed by a permitted explicit transfer.

`transfer_destruction<Root>(left);` shall validate complete-object identity, virtual-base identity, unique current ownership, target eligibility, and lifecycle phase, then commit the new Owner binding. Failure shall retain the original binding and produce the ExceptionAggregate failure record under Chapter 28. Its Result form shall return the same failure record as a value.

Transfer shall require the complete object to be Constructing with an established obligation, or Alive. The virtual base shall be Alive, and the target layer shall have an established Owner record in an eligible Constructing or Alive state. Destruction entry shall freeze transfer eligibility.

Destruction entry shall freeze Owner bindings. The coordinator may retain an existing Owner record after that layer's body ends solely to discharge its obligation. User access shall continue to require a live generation. Virtual bases shall retire in the complete-object tail unless their legal manual Owner requests an early Whole transition. Each obligation shall retain one claim and one consumption.

## 9. Destruction Execution, Whole, and Cleanup

### 9.1 Destruction coordinator

`destroy(object);` shall request destruction of the current object generation. Automatic scope exit shall invoke that operation for its registered live generation, then perform the separate storage action required by its owner. Explicit base-only requests shall use either equivalent form:

```text
destroy_base<Base>(this);
this->Base::~Base();
```

Both forms shall select the base subobject directly and require an unambiguous path and the corresponding destruction responsibility. Their source location shall determine ordinary-body or Cleanup timing. A scheduled automatic base call shall use the coordinator rule below.

The coordinator shall enter Destroying, freeze responsibility bindings, and retain one consumption record per subobject. Its reverse frontier shall be the next unresolved slot in canonical destruction order, skipping ended generations.

For each class layer, the coordinator shall:

1. Enter its ordinary destructor body when Whole has left that containing layer eligible for body entry.
2. On normal completion or a permitted continuing exception, destroy the automatic reverse-frontier prefix up to the first unresolved manual slot.
3. Execute its Cleanup body once, treating an absent body as empty.
4. Sweep all remaining local slots in reverse order, including manual remainders.
5. Leave unconsumed shared virtual-base obligations for the complete-object tail.

Cleanup shall observe the completed prefix as ended and the blocked remainder in its current states. This ordering shall preserve the reverse order across a manual barrier.

An explicit member-destruction request inside Cleanup shall designate its reverse-frontier slot. A proved out-of-order request is invalid; an unknown obligation follows the selected analysis/validation policy. The final reverse sweep shall consume slots left untouched by Cleanup. Ordinary destructor-body manual requests use their separate source-position rule.

### 9.2 Whole control effect

A permitted source-initiated base-only destruction or Abandon request shall latch Whole for the containing inheritance boundary, then perform the selected attempt. This rule includes a request at Cleanup's current frontier. A base invocation generated by the coordinator shall remain scheduled destruction. All other slots shall retain their consumption records.

After the early attempt, control shall exit the affected ordinary body or Cleanup and continue through the coordinator's required Cleanup and reverse-remainder work. An entered Cleanup shall retain its consumed invocation state. Whole shall use the lifecycle control channel, separate from user exception handlers and process termination.

Whole shall propagate through CPN26 helpers executing the affected destructor or Cleanup continuation, causing their generated exits. Its callable contract shall expose the required lifecycle effect through declarations, inferred internal summaries, and indirect function types. Lowering shall use control-flow edges or equivalent internal status while preserving the selected exit work.

An affected body or helper exit shall perform its required local-object and temporary cleanup. Each cleanup failure shall follow Chapter 28's selected outlet, which determines continuation or termination.

An early base request on an Alive complete object shall begin Destroying and Whole together. Containing layers requiring the ended base shall proceed directly to their eligible Cleanup and remainder work. Other live subobjects shall execute their own body/Cleanup sequences. Upon completion, an ordinary external caller shall resume through the operation's return or failure contract. A Constructing object shall use construction rollback; early base requests in that state shall fail lifecycle validation.

The selected base attempt shall deliver its failure before the Whole continuation proceeds. Chapter 28 shall determine aggregation on a continuing path or immediate Release destructor termination.

### 9.3 Cleanup access and failure

Cleanup shall resolve names for automatic, manual, base, virtual-base, destroyed, and abandoned slots under the class's ordinary access rights. Dead slots admit storage/state inspection; typed value operations require a live generation. Remaining live slots retain the current class layer's ordinary typed-operation contracts.

Cleanup shall use destruction and permitted inspection for its local obligations. Abandon eligibility shall be exactly Section 10.1's preconditions. A Cleanup exception shall finish that invocation and pass its record to the selected continuing aggregate path, whose coordinator shall perform remaining reverse work. Control-flow and functional state shall represent that continuation under Section 3.

## 10. Abandon, Arrays, and Storage Reuse

### 10.1 Abandon scope

`abandon(object);` shall end the selected Alive object and recursively its live contained lifetimes, including its virtual bases and member/element lifetimes. It shall consume their destruction obligations through the Abandon transition and preserve storage ownership, storage bytes, and external resource postconditions. Destructors and Cleanup belong to the distinct destruction operation.

Complete-object Abandon shall require Alive before destruction entry. Member Abandon shall require an Alive member and an eligible ordinary-code or destructor-body context. Cleanup and construction rollback shall use their specified cleanup operations. The containing object's other members shall retain their states, and later typed operations shall respect the ended member.

`abandon_base<Base>(object);` shall validate the selected direct or virtual base and its destruction responsibility, abandon its nonvirtual containment subtree, consume its obligation, and initiate Whole for that inheritance boundary. It shall require an Alive selected base and an eligible ordinary-code or destructor-body context. The resulting exit and external-return behavior shall follow Section 9.2.

Abandon of a nonvirtual layer shall preserve separately shared virtual-base obligations. If that layer owns a still-live virtual base, the coordinator shall retain its existing frozen claim until consumption. An explicit Abandon of that virtual base or its complete object shall consume the corresponding claim. Every shared virtual base shall therefore have one resolved obligation.

`abandon(array);` shall end the array and its live elements. `abandon(array[index]);` shall evaluate its index once under ordinary bounds rules and end only that element. Array destruction shall visit remaining live generations once in descending index order.

Abandon shall use Chapter 08's ANOMALY disposition. Diagnostic filtering shall preserve its state and authority preconditions. External raw resources shall retain the postconditions of the deliberately selected Abandon operation.

### 10.2 Storage capabilities and reconstruction

`storage_of(object)` shall return an authorized storage view containing its capacity, alignment, owner, slot identity, and lifetime registration. The view shall remain usable for storage operations while its extent exists, including after the object lifetime ends. The view shall be a borrow with the owner's original authority.

`construct_at<T>(storage, arguments...)` shall require inactive available storage with sufficient capacity, alignment, and a nonoverlapping extent. It shall validate those requirements through its checked storage contract before starting a new T lifetime. T may differ from the prior type. Known violated requirements shall fail compilation under the mandatory memory rules; unresolved runtime conditions shall use the operation's checked failure interface.

Successful reconstruction shall return a pointer to the new generation and register its actual type and destruction operation with the storage owner. A permitted construction unwind shall roll back completed subobjects and leave the extent with its current owner, with no completed replacement generation. The prior ended generation shall remain ended.

An automatic extent's registration shall be bounded by its lexical storage lifetime. Normal scope exit shall destroy its current live registered generation and release the local extent. Replacement shall update that registration; old typed references shall retain their original generation identity.

An inactive member or element extent may host a replacement while its containing storage exists. The replacement shall retain the slot's cleanup rank and register its actual type. Operations on it shall use its new pointer or registration; the original typed member view shall retain its ended generation. Cleanup may manage that registered replacement. Section 11 shall govern any persistent state representation.

`transfer_storage(source, target_owner)` shall require exclusive storage authority, validate the target, then atomically transfer the capability and live registrations. Failure shall retain the original owner. A subsequent failed reconstruction shall retain the storage with the successfully selected new owner.

An automatic extent shall retain its lexical physical lifetime across permitted ownership operations. Release and transfer shall require owning authority. Concurrent mutation, destruction, Abandon, or transfer of one registration shall satisfy Chapter 13's synchronization requirements.

### 10.3 Pointer and state consequences

A new generation shall require its newly returned pointer or an explicit operation identifying that generation. Earlier pointers and references shall retain their original generation identity. Known stale access shall fail validation; an explicitly checked view shall reject a generation mismatch. Raw access shall retain the selected memory contract's liveness and authority obligations.

An implementation shall preserve the functional distinctions in Section 3 and the results of explicitly selected checked operations. It may encode them statically or in minimal execution state. Additional lifetime-validation tracking shall follow the selected validation mode independently of those functional distinctions.

## 11. ABI Compatibility Constraints

The selected interoperability profile shall determine object-file format, C/C++ symbols, calling conventions, exception boundaries, and class representation.

An extern-compatible class shall preserve the chosen ABI's object fields, base offsets, and virtual representation. Its lifecycle features shall use static resolution, transient out-of-object state, or an explicitly accepted sidecar. A feature requiring persistent state shall obtain a compatible representation before that class can satisfy the requested foreign ABI.

A foreign boundary shall contain Whole through a verified aware contract or an explicit adapter that completes lifecycle coordination and returns compatibly. A CPN26 helper interacting with a foreign destructor shall use that declared continuation contract. Foreign virtual destruction shall require the chosen ABI's representation and dispatch guarantees.

## 12. Required Boundary Examples

| Case | Required behavior |
|---|---|
| A deferred expression reads a constructor parameter modified by an earlier ordinary statement while the frontier is blocked | Read the parameter at the initializer's actual evaluation point. |
| A deferred expression names a constructor-body local | Error; compute the local and use frontier-valid ordinary first assignment instead. |
| A delegated activation would return while its parameter-dependent initializer remains blocked by a later caller assignment | Error: the required producer exceeds its captured parameter lifetime. |
| Two constructor activations explicitly initialize one member | Error even when both expressions produce the same value. |
| An ordinary state obligation is unknown | ANOMALY under the central policy; selected validation adds its check. Functional Pending/Alive routing still selects construction or assignment. |
| Third array-element construction throws with a matching user handler outside construction | Roll back completed elements 1 and 0; never call a destructor for the failed element as a completed object. |
| Numeric Trap occurs in the same expression | Terminate without that rollback or any aggregate traversal. |
| An ordinary destructor body destroys an early base, followed by `log_after()` | Perform the base attempt, then exit through the Whole continuation. |
| Cleanup requests early base destruction, followed by another statement | Do not resume that Cleanup; perform the remaining reverse sweep without reentering it. |
| Automatic earlier member A and manual later member B remain at body exit | Do not destroy A across B; Cleanup and the remainder sweep preserve the B-before-A order. |
| A virtual-base owner transfer is requested inside Cleanup | Reject before changing the owner. |
| An abandoned base layer owned a shared virtual base that was not itself abandoned | Retain the existing frozen claim and discharge it once in the virtual tail. |
| An ordinary caller requests early base destruction of an Alive object | Finish that object's Whole coordination, then resume the external caller through its ordinary call contract. |
| Complete-object Abandon is requested after Destroying begins | Reject: complete-object Abandon requires Alive before destruction entry. |
| Array element 2 is abandoned before reverse array destruction | Destroy remaining live elements in descending order, skipping element 2. |
| A new U construction fails after storage was transferred from owner X to owner Y | Y retains inactive storage; the prior generation remains ended. |
| A source-compatible class feature would require changing an extern-compatible object layout | Reject that interoperability combination or require the explicit compatible sidecar contract. |

