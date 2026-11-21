<a id="chapter-28-error-recovery"></a>

# CPN26 Error and Recovery Specification

## 1. Scope and failure categories

This chapter SHALL govern language-exception formation, matching, retention, explicit capture, and recovery. The [core semantic model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance) SHALL determine the identities and observable outcomes of error values, language exceptions, terminal failure, cancellation, and Whole transfer. Library calls SHALL use the invocation phases and failure routing in [Chapter 14](14_standard_library.md#chapter-14-standard-library).

Each specialized interface SHALL retain its declared outlet. A factory returning AllocationError SHALL deliver its own admitted allocation failure through that value; a user constructor called by the factory SHALL retain its separately declared exception and terminal effects. An exception-capture interface SHALL cover the interval stated in Section 8.

## 2. Error-value contracts

### 2.1 Error identity and representation

An error value SHALL retain its nominal type and ordinary value semantics. `std::Result<T,E>` SHALL preserve E's canonical identity. A standard error record SHALL carry the discriminant, progress, ownership, and provider information required by its owning interface under Chapter 14's common representation contract.

Optional presentation text SHALL supplement that structured information. An owned presentation SHALL use its selected text/resource interface; a borrowed presentation SHALL use its declared borrow interval. User-supplied payload construction SHALL contribute its own effects. Failure during Err-payload construction SHALL follow that constructor's outlet while the intended Result remains unpublished.

### 2.2 Result composition and explicit decisions

Result construction, observation, movement, and branch adapters SHALL follow [Chapter 16](16_library_interfaces.md#chapter-16-library-interfaces). Normal return of Err SHALL be normal return of a tagged value, including during constant evaluation. Nested Results SHALL preserve each layer until a selected adapter performs its stated composition.

A source `throw error;` SHALL construct a new exception payload under Section 4. A source return of `Err(error)` SHALL construct an ordinary error value. Each action SHALL preserve its own storage, lifetime, and continuation contract. Must-use acknowledgement and `discard(value);` SHALL follow Chapter 14; diagnostic policy SHALL follow Chapter 08.

### 2.3 Locality of a checked outlet

A checked interface SHALL replace the outlet for the phases and error conditions identified by its contract. Callable and argument evaluation, parameter and result construction, callbacks, and retirement SHALL remain assigned to their declaring phase contracts. A checked divide SHALL report its own zero-divisor condition; a NumericTrap raised while computing its numerator SHALL select that earlier operation's terminal outlet before divide invocation.

## 3. Recovery guarantees and commitment

### 3.1 Operation contracts

An operation SHALL identify the covered state, sources, aliases, resource effects, external progress, and observable phase transitions required by Chapter 14. Recovery SHALL use that published contract and the currently committed ownership state.

### 3.2 Guarantee coverage

Unchanged, basic, and no-failure guarantees SHALL have their Chapter 14 meanings. A destination-only guarantee SHALL identify consumed sources and completed external effects separately. A failed constructor SHALL use the construction chapter's completed-subobject rollback on a continuing language-cleanup path. The selected terminal protocol SHALL govern paths entering terminal failure.

### 3.3 Commitment and publication

Replacement commitment and returned-result publication SHALL follow Chapter 14. A retirement failure after replacement commitment SHALL preserve the committed representation and follow the selected retirement outlet. A catchable failure preventing result publication SHALL retire completed tentative output through its prescribed cleanup path. Successful publication of a Result SHALL publish its actual Ok or Err case.

### 3.4 Retry and compensation

A selected retry policy SHALL resume only the phase and remaining prefix or suffix admitted by its contract. It SHALL account for already consumed arguments, released handles, and committed external progress in that continuation. An operation offering whole-operation replay SHALL specify the source states and external-effect contract that make replay valid.

Compensation SHALL be a separately contracted operation with its own progress and failure outcome. Static initialization SHALL use its declared compensation protocol. Other external-effect facilities SHALL use their selected domain compensation, where provided. A failed compensation SHALL expose the remaining committed state under that contract.

## 4. Forming a language exception

### 4.1 Payload type and construction category

`throw expression;` SHALL require the language-exception capability. Its expression SHALL determine a payload type through existing auto value deduction: remove reference category and top-level qualification, preserve nested qualification, nominal identity, and array extent, and materialize abstract literals under their configured defaults. The type SHALL be a complete admitted object type with the required construction and final-disposal contracts.

Payload construction SHALL select copy construction for an lvalue, move construction for an expiring value, and final-destination construction for a same-type prvalue. Each selected construction SHALL satisfy its own availability constraints. A named lvalue SHALL retain its lvalue category. A direct prvalue payload SHALL require the operations actually used by direct construction.

The expression's static type SHALL determine a newly thrown payload. Throwing a base-reference value SHALL construct that static base value. Matching and retention of an existing record SHALL preserve its formed payload and dynamic identity.

A pointer payload SHALL contain the pointer value with its existing pointee borrow obligations. Pointer completeness SHALL depend on the pointer object type. Handler matching SHALL use that pointer-object identity under Section 5.

### 4.2 Admission and operand evaluation

After determining the type, the selected exception provider SHALL admit record and final payload storage before runtime evaluation of the operand. The admitted storage SHALL satisfy the payload's alignment, lifetime, and selected record contract through the declared exception resource.

Admission success SHALL authorize exactly one operand evaluation and the selected final payload construction. Admission failure SHALL enter ExceptionInfrastructureFailure at that phase. The unstarted operand and payload SHALL remain in their pre-evaluation states. The intended primary SHALL commit only after payload formation succeeds.

If operand evaluation or payload construction raises another exception before commitment, that record SHALL propagate through its permitted route. Continuing cleanup SHALL roll back completed payload subobjects and release provisional record storage. The incomplete intended payload SHALL remain uncommitted. An immediate terminal outcome SHALL use the terminal protocol.

### 4.3 The primary commitment point

Successful payload formation SHALL commit one propagation reference and a stable primary identity. Handler discovery SHALL precede cleanup of throw-expression temporaries and exited scopes for that propagation. The throw operand's full-expression temporaries SHALL participate in the ensuing cleanup.

In the aggregate profile, a later failure of a throw-expression temporary SHALL become a secondary of the committed primary. A destruction-boundary escape or uncaught propagation SHALL follow the boundary policy selected under Chapter 08 and Section 9.

A function that constructs the intended payload SHALL finish its own return protocol before its result can complete payload formation. Failure during that return protocol SHALL leave the intended record uncommitted and route its tentative output under the unpublished-result contract.

## 5. Handler matching and rethrow

### 5.1 Primary type matching

Source handlers SHALL use these forms, with T naming an admitted payload view type:

```text
catch (T& value) { statements }
catch (const<T>& value) { statements }
catch aggregate (view) { statements }
catch (...) { statements }
```

The aggregate form SHALL bind a read-only ExceptionAggregate view of the handled record.

A typed handler SHALL bind an lvalue-reference view of the primary payload. Its object type SHALL match the canonical payload type or an accessible, unambiguous base subobject. A shared virtual base SHALL identify one subobject; multiple distinct candidate base subobjects SHALL fail the uniqueness condition.

The view's qualification SHALL determine its mutation permission. Matching SHALL use exact canonical identity or the admitted base relationship, with the existing payload retained in place. A pointer payload SHALL bind through an lvalue reference to its exact pointer-object type. Access and canonical identity SHALL follow the type and module rules.

Within the nearest eligible handler set, selection SHALL consider matching primary handlers in source order, aggregate-view handlers in source order next, and catch-all last. Secondary records SHALL remain observation data of the selected aggregate. A typed handler for a user-thrown ExceptionAggregate payload SHALL retain its ordinary typed-handler identity.

An exception raised from a handler body SHALL search eligible surrounding handler sets. A nested try within that body SHALL establish its own local set.

### 5.2 Active handler context

Handler entry SHALL establish an active record context through completion of its exit protocol, including handler-local cleanup. Exit SHALL restore the previously active context. A propagating record SHALL become a handled record when its handler is entered.

The context SHALL belong to the logical execution. An async handler SHALL retain it across admitted suspension and worker migration. A new Task, thread, or independent callback SHALL begin with its own handler context, including on an inline executor. A synchronous helper SHALL use its caller's context until it crosses a declared independent entry.

### 5.3 Bare rethrow and a new throw

`throw;` SHALL resolve the innermost active handler context and acquire a propagation reference to that record. It SHALL preserve primary identity and the secondary sequence. Each active handler SHALL retain its lifetime reference until its exit protocol completes. A valid synchronous helper SHALL resolve the same logical context.

A nested try that catches this rethrow SHALL preserve the still-active outer handler's payload view and record lifetime. A propagation exiting that outer handler SHALL release its reference at the ordinary exit point. Physical bookkeeping SHALL obey the transformation model while preserving these lifetimes.

A valid active context SHALL select identity-preserving propagation. Dynamic absence SHALL select ContractTrap before record access. A proved invalid context and an admitted unproved context obligation SHALL receive their canonical Chapter 08 diagnostics.

`throw expression;` SHALL follow Section 4 and create a new primary after formation. For `throw caught;`, the static expression type and category SHALL select the new payload. A program requiring a relation to the handled record SHALL retain that earlier record explicitly.

## 6. Source-level retained exception ownership

### 6.1 Module and ABI identities

The optional module std.error SHALL expose Sections 6–8 when language exceptions and a compatible exception provider are selected. Actual interface uses SHALL contribute their provider requirements to the resolved capability record under Chapter 14.

`std::error::ExceptionHandle` SHALL own one retained record reference or have the empty state. The originating provider SHALL own payload storage. The ExceptionRef transport in [Chapter 08](08_runtime_configuration.md#chapter-08-runtime-configuration) SHALL retain its declared two-pointer ABI; acquisition of source ownership SHALL occur through a retain or adopt operation.

ExceptionAggregate SHALL be the read-only observation view of the exception facility. A borrowed view SHALL use its handler's or owner's reference lifetime. A retained ABI result SHALL be adopted exactly once into its source-level ExceptionHandle.

### 6.2 Handle state and operations

The following schemas SHALL use the existing value and receiver rules. Observers SHALL use read-only receivers. The handle's construction and assignment capabilities SHALL be exactly the following catalogue.

| Operation | Required behavior |
| --- | --- |
| `ExceptionHandle()` | Construct an empty handle. |
| Move construction | Transfer the single reference and empty the source. |
| Move assignment | Require an empty destination; self-move preserves state. Transfer the source reference and empty the source. A nonempty distinct destination selects ContractTrap. |
| `bool has_value()` | Return whether the handle owns one reference. |
| `ExceptionHandle retain()` | Acquire and return one additional owner for a nonempty handle; return empty for an empty handle. |
| `ExceptionAggregate aggregate()` | Return the borrowed view of a nonempty record; select ContractTrap for an empty handle. |
| `void reset() noexcept` | Empty the handle, then release its previously owned reference once; preserve empty state when already empty. |
| Destructor | Perform reset through the final-disposal boundary. |

Construction, movement, retention, reset, and observation SHALL perform record-reference bookkeeping using the existing record storage. Bookkeeping success SHALL deliver its specified state transition; impossible bookkeeping SHALL enter ExceptionInfrastructureFailure. Final release SHALL invoke the selected payload finalizer and release record storage. The finalizer SHALL retain its declared resource, I/O, and internally handled exception effects. An exception escaping payload disposal or provider release SHALL enter ExceptionDisposalFailure.

Reset SHALL publish the empty handle state before final release so reentrant observation of that handle sees empty. Other reentrant accesses SHALL satisfy the payload's current lifetime state. Provider, allocator, matching descriptors, finalizer code, and required code images SHALL remain alive through every outstanding reference and active operation under Chapter 14's retention contract.

### 6.3 Aggregate observation ownership

ExceptionAggregate SHALL expose the following read-only source catalogue. u64 counting and indexing SHALL require the enabled u64 capability of the selected exception observation contract.

| Operation | Result and ownership |
| --- | --- |
| `const<void>* identity()` | Opaque record identity stable through the retained record lifetime. |
| `const<void>* primary_type()` | Borrowed canonical dynamic type-descriptor pointer. |
| `const<T>* primary_as<T>()` | Borrowed matching primary/base view, or null under Section 5's matching relation. |
| `u64 secondary_count()` | Count of retained secondary records. |
| `ExceptionHandle secondary(u64 index)` | Adopt one retained reference to the selected secondary; invalid indexing selects NumericTrap. |
| `Result<ExceptionHandle,ExceptionAccessError> try_secondary(u64 index)` | Adopt one selected reference on success; return the bounded payloadless InvalidIndex on failure with the source reference set unchanged. |
| `u64 omitted_count()` | Known omitted-secondary count, saturating at maximum u64. |
| `bool truncated()` | True when a secondary was omitted or the omission counter saturated. |
| `ExceptionHandle retain()` | Acquire one additional owner of this record. |

Identity SHALL remain stable while the retained record is alive. A primary-type descriptor SHALL use Chapter 08's canonical identity and matching protocol for cross-module equivalence. Descriptor pointer values SHALL designate the borrowed local transport descriptor; comparison of payload types SHALL use that canonical protocol. Each returned secondary owner SHALL permit a read-only aggregate view through aggregate().

The exception ABI release operation SHALL discharge an owned reference. A source owner SHALL discharge its reference through reset, destruction, or a declared raw-ABI transfer. A borrowed catch view SHALL observe through the handler-owned reference. Source ownership acquisition SHALL use the catalogue in this chapter and the compatible raw-ABI adoption contract.

`primary_as<T>()` SHALL return a read-only pointer to an exact or admitted base payload view, and null for a mismatched type. The pointer SHALL borrow from the retained owner or active handler supplying the view. Matching SHALL use Section 5's type relation.

### 6.4 Concurrent references and aggregate metadata

A record provider supporting multiple execution agents SHALL synchronize reference acquisition/release, secondary publication, and observation. Sequenced cleanup observations SHALL preserve their order. Concurrent append operations SHALL have one recorded order consistent with existing ordering relations; otherwise the provider SHALL choose that order.

Each count, flag, and indexed-secondary observer SHALL observe a valid published state. Separate calls SHALL be separate observations. Entries SHALL remain retained through the record's lifetime. Concurrent cycle validation and publication SHALL preserve an acyclic secondary-retention graph. An append exceeding the provider's validation budget SHALL follow the existing omission and truncation rule. User payload references SHALL retain their ordinary ownership and cycle-management contract.

Mutable primary-payload access SHALL follow the memory model and its selected synchronization. Borrowed payload resources SHALL retain their ordinary lifetime contract when records are shared or raised on another agent.

## 7. Current record and identity-preserving raise

The enabled std.error module SHALL provide:

```cpn
namespace std {
    namespace error {
        declare Option<ExceptionHandle> current_exception() noexcept;
        declare never raise(const<ExceptionHandle>& record);
    }
}
```

`current_exception()` SHALL return None for an empty active-handler context. Otherwise it SHALL retain the innermost handled record once and return Some of its owning handle.

`raise(record)` SHALL require a live nonempty handle, acquire a propagation reference, and propagate the same record while the source handle keeps its reference. Primary identity, dynamic payload type, and retained secondaries SHALL remain preserved. Permitted subsequent cleanup SHALL append secondaries under its selected profile. Raising an empty handle SHALL select ContractTrap before propagation.

A retained record SHALL remain raisable after its original handler exits while its provider and code obligations remain satisfied. Raising from a handler or another agent SHALL use normal eligible-handler search, logical entry boundaries, and cycle/exhaustion rules. Bare rethrow SHALL obtain its source from the active context; raise SHALL obtain its source from the supplied owner. Each SHALL acquire a propagation reference while preserving still-live source owners.

## 8. Explicit exception capture

### 8.1 `attempt` contract

`std::error::attempt<T>(callable)` SHALL invoke a synchronous nullary callable and return `std::Result<T,std::error::ExceptionHandle>`. T SHALL be a complete admitted object type or void, and the callable result SHALL be exactly T. A reference result SHALL use an explicit std::Ref wrapper.

The parameter SHALL be a forwarding borrow and the adapter SHALL invoke it exactly once with the supplied category. The callable SHALL remain owned by its existing owner. A mutable stored closure SHALL use its admitted mutable receiver. Captures and external state changed by the invocation SHALL follow their own contracts.

The adapter SHALL establish the program-selected language handler for the interval in Section 8.2 in every profile. Surrounding calls and independent entries SHALL retain their separately selected boundaries.

### 8.2 Capture interval

The protected interval SHALL begin after callable-argument evaluation and forwarding designation. It SHALL cover callable invocation in that logical context, the invoked function's return protocol, tentative Ok-payload formation in the final Result destination, and required continuing rollback of that tentative output.

Same-type prvalue construction SHALL target the final Ok payload directly. All adapter-required success-payload construction SHALL complete inside the interval. Thus an immovable prvalue T SHALL be admitted when its actual construction and disposal contracts are satisfied.

Normal completion SHALL publish Ok(value), or payloadless Ok() for void. A caught exception SHALL cause one retain of the handled record and direct construction of Err(handle) in the final destination. Completed unpublished Ok payload SHALL undergo its prescribed cleanup before activation of Err; an incomplete payload SHALL use completed-subobject rollback. Err construction and reference handoff SHALL be nonthrowing, nonallocating handle operations.

With satisfied callable-borrow and provider contracts, every admitted language exception arising within the protected interval SHALL reach this handler. Terminal events SHALL follow their selected terminal dispatch.

### 8.3 Handler selection and phase routing

| Phase or event | Required route |
| --- | --- |
| Callable/capture construction and adapter argument evaluation | Caller-side phase and its applicable handler set. |
| Protected invocation and tentative Ok construction | Attempt's explicit handler, subject to intervening terminal boundaries. |
| Caller temporary retirement, later move, assignment, or destruction | The new caller-side operation and its own boundaries. |
| Escape at noexcept, Release destruction, final disposal, incompatible foreign, or independent-entry boundary | The named terminal dispatch at that boundary. |
| NumericTrap, ContractTrap, memory/infrastructure terminal failure, or platform fault | Its declared terminal protocol. |
| Cooperative cancellation or Whole transfer | Its owning coordinator and control-transfer protocol. |
| Child Task or thread entry, including inline execution | The child's independent entry and source handlers. |
| Normal return of Result<U,E> | Outer Ok containing the unchanged inner Result case. |
| Normal return of a Task or task outcome | Outer Ok containing that value under its existing state/discriminant contract. |

A synchronous call that starts a child SHALL remain within the adapter interval for its own admitted synchronous effects. The child's execution SHALL use its independent entry. A child selecting recoverable language exceptions SHALL establish its handler within that entry.

### 8.4 Explicit translation

A mapping from retained exceptions to domain errors SHALL specify recognized primary types, the fallback for other types, retained context fields, and callback effects. A mapping callback SHALL route its new failures through its applicable enclosing boundary.

A domain error selected for throwing SHALL create a new primary. Identity-preserving forwarding SHALL retain or raise the original record, including its secondary sequence. A mapping retaining only selected information SHALL identify the resulting information reduction in its public contract.

## 9. Terminal boundaries

### 9.1 Search and cleanup

Handler discovery SHALL search eligible handlers inside the nearest terminal boundary. Reaching that boundary SHALL select its terminal action. Under the Release terminate policy, an uncaught propagation SHALL enter termination before propagation cleanup. A Release destructor's internal source handler SHALL remain eligible; an exception escaping its body, Cleanup, or generated subobject destruction SHALL select immediate destruction-failure termination.

These are control-flow outcomes under the core semantic model. An implementation SHALL realize the selected outcome through any permitted representation and transformation. Source-selected handlers and explicit capture SHALL remain functional under the selected boundary policy.

### 9.2 Terminal categories

The standardized terminal identities SHALL include NumericTrap, ContractTrap, the named memory-failure outlet, uncaught Release exception, noexcept violation, Release destruction failure, ExceptionInfrastructureFailure, ExceptionDisposalFailure, ForeignBoundaryFailure, and the specified task/static cancellation contract failures.

Terminal dispatch SHALL perform its configured bounded, nonthrowing report and enter the target termination action. Reporting SHALL use configured standard error in a hosted image or the explicit freestanding hook, with already available selected debug information. Reporting failure SHALL proceed to termination.

The target termination contract SHALL determine host storage reclamation and any stronger provider-published effects. Language cleanup, external compensation, and durability SHALL arise through the separately selected operations that specify them.

## 10. Secondary failures and error-path cleanup

In the aggregate profile, the cleanup coordinator SHALL preserve a committed primary and append later failures in observed cleanup order. If cleanup starts outside propagation, its first escaping exception SHALL become the primary for remaining prescribed cleanup. Exhaustion or cycle rejection SHALL preserve that primary, mark omissions, dispose of omitted references through the final-disposal boundary, and continue the profile's prescribed cleanup.

An ordinary Err SHALL remain an error value. An exception during its return cleanup SHALL prevent publication and enter the language-exception route. A new throw in a handler SHALL follow Section 4; a cleanup secondary SHALL arise through the active cleanup coordinator.

Recovery SHALL preserve already completed source mutations and external progress according to their operation contracts. A failure during handler-local cleanup SHALL use the surrounding handler search and active cleanup profile. The handled record SHALL remain alive through valid explicit owners and its handler-exit protocol.

Final exception-record disposal SHALL use its nonthrowing infrastructure boundary. An escaping disposal failure SHALL dispatch to ExceptionDisposalFailure at the current disposal state.

## 11. Return contracts and recovery

A synchronous return SHALL construct its result in the unpublished state, retire return-expression temporaries and body locals, evaluate enabled postconditions while parameters remain alive, retire parameters and perform applicable final exit-invariant checks, and publish the completed result in that order.

Postconditions SHALL observe current parameter and result values, including admitted moved-from states. Any earlier-state observation SHALL use the program's selected snapshot value and its ordinary lifetime. A referent read SHALL satisfy its current lifetime contract.

A failure before publication SHALL leave the result unpublished and select its prescribed cleanup or terminal route. A failing checked postcondition SHALL enter ContractTrap. Contract selection and diagnostic/default behavior SHALL follow the contract and configuration chapters.

An async body SHALL evaluate its corresponding check after body-local cleanup and before frame parameter/capture retirement. Its successful-return/cancellation arbitration SHALL follow the atomic completion protocol. Terminal completion storage SHALL remain owned until Task delivery or close retires it.

## 12. Concurrency, static lifetime, and foreign translation

### 12.1 Independent execution entries

Thread, Task, and independent callback entry SHALL preserve their logical exception boundaries under synchronous, inline, and asynchronous execution. Task<Result<T,E>> SHALL preserve the task outcome and application Result as distinct layers.

Cross-agent ExceptionHandle transfer SHALL use ordinary ownership transfer and synchronized publication. Record metadata SHALL use Section 6.4; user payload mutation and borrows SHALL use their declared contracts. Join and other completion operations SHALL transfer exactly the record, numeric-context, resource, and outcome components specified by their interfaces.

### 12.2 Static initialization and shutdown

Initialization errors, dependency failure, cancellation, compensation, and commit SHALL follow Chapter 08. Independent failed tasks SHALL retain separate primaries. A combined diagnostic SHALL present those records with their independent identities.

Committed static objects SHALL enter the logical reverse shutdown order defined by their initialization protocol. A failed unpublished object SHALL remain outside that committed set. Uncaught and destruction failures SHALL use the selected terminal boundaries.

### 12.3 C and C++ boundaries

A selected foreign exception adapter SHALL cover record ownership, matching, unwinder/personality compatibility, cleanup, and rethrow for every admitted cross-frame propagation. Native object-file interoperability SHALL follow its separate ABI contract.

An adapter translating an exception to status or Result SHALL perform capture on its originating side. A translated CPN26 throw SHALL occur in a native phase admitting propagation. Identity preservation SHALL retain a compatible original record; payload translation SHALL form a new primary.

An output-pointer/status adapter SHALL publish output initialization, mutation, and ownership for every status. Error-payload storage SHALL use its explicit compatible provider. Terminal events SHALL retain their terminal outlet across the adapter.

## 13. Effects, configuration, and diagnostics

### 13.1 Failure effects and terminal policy

Normal Err return SHALL contribute the effects of constructing, publishing, and retiring its actual payload and participating state. Noexcept SHALL require containment of language propagation within its selected callable phase. Ordinary error values, terminal events, divergence, and cooperative cancellation SHALL retain their own effect identities.

A canonical callable descriptor SHALL contain its declared effect bound and applicable exception-boundary policy. Handler composition SHALL discharge the admitted throw effects handled within its interval while preserving resource, memory, I/O, numeric, synchronization, and terminal effects. Explicit attempt SHALL use that composition for its protected interval.

A potentially throwing callable SHALL record throw. A local terminal boundary SHALL compose an escaping exception into its named terminal effect. The existing trap(any) bound SHALL admit all standardized synchronous terminal outlets; each narrower bound SHALL admit its declared categories.

Body operations SHALL satisfy the callable's source effect bound. The selected terminal policy SHALL determine dispatch on an escaping exception at its boundary. Effect queries, generic witnesses, and exported metadata SHALL preserve that effective policy. Transformation legality and proof obligations SHALL follow the core semantic model; satisfied provider contracts SHALL supply their declared effects.

### 13.2 Configurable facilities

The Chapter 08 configuration model SHALL select language exceptions, std.error capability, aggregate or terminate policy, record/secondary capacity, exception resources, and diagnostic policy. The resulting declaration descriptor SHALL capture every externally relevant requirement. Import SHALL require descriptor compatibility or the explicitly selected compatible adapter.

Actual retained-exception uses SHALL bind the originating provider's storage, synchronization, code-lifetime, and disposal requirements. Core Result and other bounded error values SHALL use their own module capability requirements.

### 13.3 Diagnostic and evaluation outcomes

The compiler SHALL classify unavailable capabilities, malformed handlers, invalid ownership transitions, incompatible descriptors, and unresolved admitted obligations under the canonical Chapter 08 diagnostic rules. Required constant evaluation SHALL produce either its valid value or the required rejection under the constant-evaluation chapter; a valid Err SHALL remain a valid constant value.

Dynamic recoverable failures SHALL produce their declared error values. Dynamic boundary failures SHALL perform the named terminal dispatch. Diagnostic configuration SHALL affect those runtime outcomes only through an explicitly selected semantic policy defined by the owning chapter.

## 14. Normative source examples

The examples use enabled modules and capabilities with live required objects. Statement fragments occur inside valid function bodies; declarations and types retain their module scopes.

### 14.1 Result values and captured exceptions

```cpn
import std;
import std.error;

declare std::Result<i32, DomainError> read_value();

auto operation([] std::Result<i32, DomainError>() {
    return read_value();
});

auto captured(std::error::attempt<std::Result<i32, DomainError>>(operation));
```

A normal Err return from read_value SHALL produce outer Ok and inner Err. An admissible exception reaching the adapter SHALL produce outer Err containing its retained record. NumericTrap SHALL select its terminal outlet.

### 14.2 Capture construction remains outside

```cpn
auto operation([state(make_state())] i32() {
    return use_state(state);
});

auto captured(std::error::attempt<i32>(operation));
```

The capture initializer make_state SHALL execute in the caller phase. A program selecting capture for that synchronous invocation SHALL place it within the invoked closure or another protected interval.

### 14.3 Retaining and raising the same primary

```cpn
std::error::ExceptionHandle saved;

try {
    perform_operation();
}
catch aggregate (record) {
    saved = record.retain();
}

if (saved.has_value()) {
    std::error::raise(saved);
}
```

The assignment SHALL transfer the new reference into the empty destination. Raise SHALL retain a propagation reference while saved keeps its original ownership. A selected handler SHALL observe the same primary identity. An uncaught Release propagation SHALL enter immediate termination.

### 14.4 Explicitly throwing a domain error

```cpn
i32 read_or_throw() {
    auto result(read_value());
    if (result.has_error()) {
        throw std::move(result.error());
    }
    return result.value();
}
```

The function SHALL form a new language-exception record for its selected domain Err. Its payload type SHALL satisfy the construction and final-disposal requirements. read_value and Result::value SHALL retain their declared failure outlets.

## 15. Required boundary behavior

| Case | Required behavior |
| --- | --- |
| Primary-record admission fails before a throw operand with side effects | Enter ExceptionInfrastructureFailure with the operand still unevaluated. |
| Intended payload construction raises another exception | Keep the intended primary uncommitted and route the actual exception through its permitted search and cleanup. |
| A throw-expression temporary destructor fails after primary commitment | Preserve and append under aggregation; dispatch destruction failure under Release termination. |
| A base-reference handler executes `throw caught` | Form the new statically typed payload through the selected construction. |
| An inner aggregate catch and an outer exact typed catch both match | Select the inner eligible handler set. |
| A bare-rethrow helper executes within an active handler | Preserve that record and its secondary sequence. |
| An outer handler catches its own bare rethrow in a nested try and continues | Preserve the outer payload view and active-handler reference through inner exit. |
| Two agents raise a retained record concurrently | Synchronize record bookkeeping and publication while retaining ordinary payload race obligations. |
| A Result error mapper raises an exception | Leave its intended Result unpublished and use the callback's exception route. |
| Attempt returns an ordinary domain Err | Publish outer Ok containing that domain Result. |
| Attempt argument or capture initialization raises | Use the caller-side handler interval. |
| Attempt encloses an escaping Release destructor exception | Enter immediate destruction-failure termination. |
| A Release destructor handles its helper's exception internally | Execute the selected handler and continue according to its body. |
| An inline executor runs an uncaught child-entry exception | Dispatch at the child's logical boundary. |
| Postcondition passes and later parameter cleanup fails | Keep the result unpublished and use the selected cleanup/termination policy. |
| Replacement commits before old-element retirement fails | Preserve the new committed state and route the retirement failure. |
| write_all publishes a prefix then returns WouldBlock | Return the exact cumulative prefix and permit retry of the admitted remaining suffix. |
| try_close returns Err after consuming the provider handle | Preserve Closed and its discharged ownership obligation. |
| A caller discards Err explicitly | Acknowledge inspection and complete the value's ordinary lifetime. |
| Exception-payload disposal raises | Enter ExceptionDisposalFailure. |

These cases SHALL constrain observable outcomes, exported contracts, and transformations under the core semantic model.

