<a id="chapter-13-concurrency-memory-model"></a>

# CXXN Concurrency and Memory Model Specification

## 1. Execution agents and facilities

A thread is a native execution agent with its own stack, thread-storage domain, and root execution context. A task is an explicitly owned logical computation that may suspend and resume on an executor. An executor supplies declared execution and progress services; it need not create native threads. An asynchronous function is a source-level producer of a task, not an implicit thread-creation operation.

The `std.atomic`, `std.sync`, `std.thread`, and `std.task` capabilities are independently declared. Fixed atomics do not require a scheduler. Cancellation flags do not require coroutines. A manual executor can run tasks on one existing thread. No facility creates an unnamed global allocator, executor, garbage collector, or universal support runtime.

Memory access and borrowing obey the [memory specification](12_core_memory_control.md#chapter-12-core-memory-control). Construction, destruction, exceptions, and terminal events retain their [lifecycle](06_construction_execution.md#chapter-06-construction-execution) and [exception](08_runtime_configuration.md#chapter-08-runtime-configuration) contracts. Native and foreign interoperability obey the [ABI specification](09_native_interoperability.md#chapter-09-native-interoperability). A compatible object-file format alone does not establish a shared atomic representation or memory model.

## 2. Actions, races, and compiler obligations

### 2.1 Ordering relations

An execution contains reads, writes, atomic operations, synchronization actions, lifetime transitions, and other observable effects. **Sequenced-before**, written `sb`, is the intra-agent order required by the language, including left-to-right call argument and built-in binary operand evaluation. Suspension preserves the task's sequenced-before relations; moving a task to another worker does not create a new task history.

**Synchronizes-with**, written `sw`, comprises the relationships explicitly defined for atomics, fences, thread/task publication and completion, and declared synchronization providers. **Happens-before**, written `hb`, is the transitive closure of `sb` and `sw`. It is acyclic. A wall-clock observation, a delay, a scheduling hint, or equal numerical values in different objects is not independently a synchronization edge.

Two actions conflict when they access overlapping memory locations and at least one writes, or when a lifetime/storage transition invalidates the object generation used by the other action. Distinct live scalar objects, nonoverlapping array elements, and nonoverlapping ordinary fields are separate locations. Ending or reconstructing an enclosing lifetime can conflict with accesses whose validity depends on that lifetime, even when they select different subobjects.

### 2.2 Non-atomic accesses and races

Conflicting actions in different agents constitute a data race when at least one is non-atomic and neither happens before the other. Construction must precede published value access; synchronization does not revive an ended generation. An atomic and a non-atomic access to the same storage do not become compatible merely because their machine instruction widths match.

For a race-free non-atomic read, the visible value is supplied by the last applicable write ordered before that read, with no intervening ordered write to the location. Object lifetime, representation, and pointer validity remain additional requirements. A read-only view is not proof that all other aliases are read-only.

A proved invalid access or synchronization/lifetime contradiction is `ERROR` at the required diagnostic site. An unproved shared-access or escape contract is `ANOMALY` and a programmer obligation where the interface admits it. No mandatory safe/unsafe partition or universal race detector is introduced. A dynamic data race is a contract violation; when it is not detected, there is no portable value or recovery guarantee from the violating action onward. It is not automatically a library Result or a catchable exception.

Race-freedom obligations and trusted assumptions shall follow the core execution model. A valid synchronization/alias/exclusivity promise shall use its declared proof or contract.

### 2.3 Observable operations

Transformations preserve the permitted values, synchronization, lifetime actions, failures, selected numerical status, and progress obligations of valid executions. A widened store shall preserve each neighboring location's access contract. Atomic lowering shall retain the location's declared coherence and synchronization.

Values cannot be manufactured by circular justification. A read must obtain a value from initialization or an actual permitted write. The graph of read-from edges and necessary value/control dependencies producing those writes shall have no self-supporting cycle. Speculating a store is not permitted when its value or authorization depends only on a read justified by that same speculation.

## 3. Atomic coherence and ordering

### 3.1 Per-location rules

Each atomic location has a total **modification order**, `mo`, containing its initialization and successful modifications. Each atomic read has one **read-from** source, `rf`, naming the modification supplying its representation. Reads observe complete atomic representations without tearing.

For modifications `W`, `W1`, `W2` and reads `R`, `R1`, `R2` of one location:

- If `W1 hb W2`, then `W1` precedes `W2` in `mo`.
- If `W hb R`, the source of `R` is `W` or a later modification in `mo`.
- If `R hb W`, the source of `R` precedes `W` in `mo`.
- If `R1 hb R2`, the source of `R2` is not earlier in `mo` than the source of `R1`.

A successful read-modify-write reads the immediately preceding modification in `mo` and inserts its own modification next. An unsuccessful compare-exchange is a read, not a modification. These rules do not promise the latest value by wall-clock time or impose a global order on all relaxed operations at different locations.

### 3.2 Acquire and release

`Relaxed` supplies atomicity and coherence without itself establishing a synchronization edge. A `Release` modification synchronizes with an `Acquire` operation that reads from it or from its release sequence. A release sequence consists of that release followed by contiguous read-modify-write modifications of the same location, by any agent; an intervening ordinary atomic store ends the sequence.

`AcqRel` combines the acquire effect of a read with the release effect of its modification. A relaxed RMW can participate in a release sequence without becoming an acquire or release operation itself. Equality of observed bits is insufficient: synchronization depends on the actual read-from relation.

### 3.3 Fences

An acquire/release fence orders the corresponding effects in its own agent. Cross-agent synchronization additionally requires an atomic observation:

- A release fence before an atomic write synchronizes with an acquire read observing that write or its contiguous RMW extension.
- A release modification synchronizes with an acquire fence after an atomic read observing that modification or its release sequence.
- A release fence before an atomic write synchronizes with an acquire fence after an atomic read observing that write or its contiguous RMW extension.

“Before” and “after” in these fence rules mean sequenced-before. Two fences alone, without the required atomic observation, do not publish ordinary memory. A relaxed fence is a no-op. An acquire-release fence has both effects.

### 3.4 Sequential consistency

There is one total order `S` of sequentially consistent atomic operations and fences. It respects happens-before between its members. Sequentially consistent loads have acquire semantics; stores have release semantics; RMW operations and fences have both applicable effects.

For distinct events of one atomic location, define **coherence-before** as the transitive closure of modification order, writer-to-reader read-from edges, and reader-to-modification edges when that modification follows the reader's source in modification order. An RMW's own modification is excluded from its reader-to-modification edges.

For `A coherence-before B`, the following constrain `S`:

1. If both are sequentially consistent, `A` precedes `B` in `S`.
2. If `A` is sequentially consistent and `B hb F` for a sequentially consistent fence `F`, `A` precedes `F` in `S`.
3. If a sequentially consistent fence `F hb A` and `B` is sequentially consistent, `F` precedes `B` in `S`.
4. If sequentially consistent fences satisfy `F hb A` and `B hb G`, `F` precedes `G` in `S`.

A candidate execution violating these constraints is not permitted. When all accesses to a location are sequentially consistent atomics, a load observes its latest preceding modification in `S`, or its initialized value. Mixed-order code retains the other orders' weaker guarantees. These requirements define the CXXN atomic contract; a foreign model is not presumed identical.

## 4. Atomic types and operations

`std::atomic::Atomic<T>` is an address-stable, noncopyable owner of one atomic location. Its capability specifies `T`'s representation, alignment, operations, and lock-free properties. Core supported categories are enabled fixed integers, Boolean values, pointers, and floating representations for which the provider supplies the required contract. A nontrivial allocating value is not automatically atomic because it fits in a record.

Load, store, exchange, and comparison transport the declared atomic representation. They do not invoke user equality, round a float, quiet a signaling NaN, or generate FP Invalid merely to move bits. Compare-exchange distinguishes different zero signs and NaN representations. Provider-defined padding or capability metadata follows the declared comparison representation. Pointer CAS success does not prove pointee lifetime, exclusive ownership, or absence of address-reuse ABA.

Construction establishes the initial value before publication. Moving, reconstructing, destroying, or releasing a location while another agent can access it requires the appropriate quiescence protocol. Copying a loaded value into a separately constructed atomic object creates a different location.

The standard call forms are:

| Call | Result and action |
| --- | --- |
| `load(object, order)` | One atomic value snapshot. |
| `store(object, value, order)` | One atomic modification; returns `void`. |
| `exchange(object, value, order)` | One RMW returning the previous value. |
| `compare_exchange_strong(object, expected, desired, success, failure)` | Boolean success; on failure, replace the ordinary `expected` object with the observed value. |
| `compare_exchange_weak(object, expected, desired, success, failure)` | Same contract, but may fail spuriously. |
| `thread_fence(order)` | The selected atomic fence; returns `void`. |

These names are exported by `std::atomic`. The operation shall evaluate arguments once from left to right. `expected` shall designate writable ordinary storage with admitted synchronization and aliasing. A successful update shall preserve expected. A representation mismatch shall select the failure transition; weak CAS may also select that transition on equal representations. The returned success flag shall identify a committed update.

`MemoryOrder` is a compile-time policy argument. The default is `SeqCst`. Runtime selection dispatches to an instantiated permitted policy; invalid order/type/capability combinations are `ERROR`.

| Operation | Permitted orders |
| --- | --- |
| Load | `Relaxed`, `Acquire`, `SeqCst`. |
| Store | `Relaxed`, `Release`, `SeqCst`. |
| Exchange or successful CAS | `Relaxed`, `Acquire`, `Release`, `AcqRel`, `SeqCst`. |
| Fence | `Relaxed`, `Acquire`, `Release`, `AcqRel`, `SeqCst`. |

CAS failure orders are:

| Success order | Permitted failure orders |
| --- | --- |
| `Relaxed` | `Relaxed`. |
| `Acquire` | `Relaxed`, `Acquire`. |
| `Release` | `Relaxed`. |
| `AcqRel` | `Relaxed`, `Acquire`. |
| `SeqCst` | `Relaxed`, `Acquire`, `SeqCst`. |

The single-order CAS form derives failure order by replacing `Release` with `Relaxed` and `AcqRel` with `Acquire`, leaving other orders unchanged. There is no implicit `Consume` policy.

The atomic bit interfaces retain their range validation, whole-location linearization, and retry rules from the [numeric expression specification](07_numeric_expressions.md#chapter-07-numeric-expressions). No numeric or pointer failure from argument evaluation is converted into a false CAS result. Native support is preferred; software fallback requires explicit permission and predeclared support resources. A fallback shall preserve these semantics and report its actual progress class.

## 5. Publication, ownership, and thread storage

Publishing a pointer through a release/acquire protocol can make completed initialization visible. It does not retain the allocation, transfer release authority, synchronize later mutation, or make the pointee safe for unrestricted sharing. An owning transfer additionally uses the object's ownership protocol. Destruction, Abandon, storage reuse, and concurrent access must be ordered so that no access uses an ended generation.

A successful unlock synchronizes with the subsequent successful lock acquiring that mutex under a conforming synchronization provider. Condition waits inherit their specified release/reacquire edges; notification alone does not replace the predicate protocol. Ordinary sleeping, yielding, volatile device access, and successful symbol linkage establish no such edge.

`thread_local T name(arguments);` declares one instance per attached native-thread domain. Block placement controls name visibility, not first-use initialization. Its initializer shall bind through the thread-domain initialization environment.

Thread-local initialization is eager and serial in dependency/logical-rank order. Shared image static initialization completes first. The root thread then attaches its thread-storage domain before entering `main`; another CXXN thread attaches its required domains before executing its user entry. An image static initializer cannot require not-yet-attached user TLS. A proved dependency cycle or readiness violation is `ERROR`; startup providers may use their separately owned bootstrap data.

Normal thread exit destroys completed thread-local instances in reverse logical rank after entry-local cleanup. Failed initialization follows the exception/initialization policy and is not automatically retried. An existing foreign thread or newly loaded domain requires explicit attachment before its TLS is used; no hidden first-use guard supplies that attachment. Detachment and unload wait for dependent work and borrows under their declared contracts.

TLS is native-thread-local, not task-local. A migrated task resolves a TLS name in its current worker. Retaining a pointer to another thread's instance neither migrates that instance nor extends its lifetime. Task FP state has the separate semantics in Section 10.

## 6. Native thread ownership

`std::thread::Thread` is a move-only handle. `std::thread::Options` supplies a native provider, declared stack/control-storage resources, stack size policy, and initial execution-control settings. A stack provider may use host services under its explicit resource contract; selecting threads does not create a general implicit allocator.

`std::thread::start(options, entry)` returns `std::Result<Thread, ThreadError>`. The entry is an owned callable invocable as `void()`. Captures and arguments are evaluated according to ordinary source rules. Resource admission precedes transfer into the worker's storage; construction exceptions remain ordinary call effects. Native start failure returns an error before admitting user-entry execution and disposes any already transferred entry state and worker allocation under the applicable cleanup policy. It does not restore a caller source explicitly moved during argument evaluation or permitted entry-state transfer. Operational failure does not synthesize a language exception.

Successful start publishes fully constructed entry state to the worker. Actions preceding the start commitment happen before the first user-entry action. The worker may execute before the successful call returns. Required TLS readiness precedes user entry. A TLS constructor's unhandled language exception retains the global failure policy rather than becoming `ThreadError`.

`join(thread)` explicitly waits for entry completion, local/capture cleanup, TLS destruction, and required provider completion. It returns `std::Result<ThreadCompletion, ThreadError>`, empties the handle on success, and establishes completion happens-before subsequent caller actions. `ThreadCompletion` shall expose `Option<FPStatus>`: Some for an observed execution context and None for Native unobserved execution. Failure leaves the still-owned handle available for the defined retry or recovery; self-join reports `Deadlock` through this operational interface.

Yield and sleep are scheduling operations, not publication. No bounded scheduling fairness is implied. Join does not secretly run an unrelated task executor to make progress.

`std::thread::detach(thread, owner)` transfers the completion/cleanup obligation to an explicit `std::thread::Owner`, consuming the handle only after successful owner admission. The owner has declared resources and a completion policy. Its lifetime, provider code, and borrowed resources cover the worker and its cleanup. Detachment does not extend borrowed capture lifetimes.

A completed but still joinable handle retains a completion obligation. Destruction of a joinable handle neither joins nor detaches implicitly: an established missing resolution is a diagnostic error, and a dynamic violation invokes `ContractTrap`. A default/moved-from empty handle has no such obligation. Explicit Abandon does not terminate a worker or authorize release of storage that the worker still uses.

The owner rejects new attachments after closing begins. Explicit owner close drains its accepted threads; cooperative stop can be requested through supplied cancellation tokens, but a native thread is never killed by that request. Destroying an owner with unresolved workers invokes its contract-failure outlet. Owner close may wait indefinitely for a worker that does not finish; no hidden forced cleanup is permitted.

Thread owners use Open, Closing, and Closed states under the [concurrency interface contract](17_concurrency_interfaces.md#chapter-17-concurrency-interfaces). Timeout/error retains Closing and unresolved obligations; concurrent close attempts serialize, and a retry cannot repeat an already committed notification. An explicitly selected Notify policy runs on the close caller after the worker's entry, captures, TLS, and provider operations have quiesced. It shall use the caller's attached TLS domain and the owner's execution-initialization policy. Observed-context selection includes its specified restoration; Native selection follows the native provider. Pending Notify delivery shall remain an owned obligation. Discard policy may release already-quiescent completed records under its separate contract.

## 7. Task types, source syntax, and allocation

### 7.1 Context and completion

`std::task::Context` is an ordinary by-value resource/execution description. It supplies a `std::mem::ResourceRef` for frames and support records, an explicit executor instance, cancellation policy/token, and FP initialization policy. Its provider handles are borrowed; copying Context does not extend their lifetime. The Context snapshot used for async admission is a trivial, nonfailing copy of these handles and policy values; it neither allocates nor executes user constructors. A provider may be a manually driven or inline executor and need not create a native thread.

`std::task::Task<T>` is a move-only owner of a computation/completion record. A value result type is a storable, move-constructible object type; `void` is also supported. Borrowed results use an explicit pointer or `std::Ref<T>` with the applicable lifetime contract, not an implicitly retained reference to frame locals.

Its terminal outcome is the tagged value:

```text
generic<type T>
requires (ObjectType<T> && CompleteType<T> && MoveConstructible<T>)
union Outcome {
    case Value(T value);
    case Cancelled(CancelReason reason);
    case Failure(TaskError error);
};

specialize union Outcome<void> {
    case Value;
    case Cancelled(CancelReason reason);
    case Failure(TaskError error);
};
```

For `Outcome<void>`, Value shall be payloadless. `TaskError` shall carry bounded operational data: `AllocationFailure`, `ResourceLimit`, `ProviderUnavailable`, `StartRejected`, `InvalidState`, or `OwnerClosing`, with an optional bounded provider code. Application errors shall use their declared value type, such as `std::Result<T, E>`. CompletionInfo shall separately expose body_entered and an optional final FPStatus. An inline failed task shall report body_entered false and status None. An observed execution context may produce status during cleanup before body entry, retaining body_entered false; a Native context shall report None.

### 7.2 Asynchronous declarations

The function forms are:

```text
declare async i32 compute(std::task::Context context, i32 input);

async i32 compute(std::task::Context context, i32 input) {
    std::task::checkpoint();
    return input + 1;
}
```

The first ordinary parameter of an async function is Context by value. Calling `async T f(...)` produces `std::task::Task<T>`; its body returns T only. It does not accept Outcome as a special alternative or implicitly unwrap an application Result. `return;` completes `async void`. Constructors, destructors, and Cleanup are not async; explicit async factories/finalizers are separate functions.

An async lambda uses `[captures] async T(Context context, parameters) { body }`, with `mutable` after the parameter list where selected. Captures are materialized into the frame according to the closure expression's value category: an lvalue copies eligible owned captures, while `std::move(closure)` or an expiring closure requests their move. A noncopyable lvalue closure therefore requires explicit movement. Borrowed captures remain borrowed. The frame shall own its materialized captures under those copy/move rules.

An async callable's [effect contract](25_effect_composition_and_boundaries.md#chapter-25-effect-composition-boundaries) distinguishes admission (`[[admission_effects(...)]]`) from task execution (`[[effects(...)]]`). A checked `requires` clause belongs to successful frame admission after frame parameters exist; a checked `ensures` clause applies before successful terminal Value publication. A body effect is not performed simply because a cold Task handle is created.

An async member function's receiver remains an explicit borrow unless an owning value is separately moved into the frame. Retained parameter/receiver effects must be exposed by its declaration; `noescape` cannot conceal retention past the call.

An async declaration cannot be constexpr or consteval: its admitted frame, executor, and execution lifetime are runtime entities. A `noexcept` async declaration imposes its nonthrowing callable contract on callee creation work, including closure-state transfer and additional conversion/copy/move needed solely for parameter binding, and on execution of its body. Evaluation of the callable and explicit/default argument expressions remains caller-side. A prvalue constructor explicitly belonging to an argument expression retains that caller-side exception boundary even when mandatory elision writes directly into final frame storage. Physical destination address does not reclassify the origin of an exception. Cleanup of frame-owned parameters and captures during completion, cancellation, or frame destruction observes the declared nonthrowing promise and each destructor's contract under the selected destructor policy. A known violation is ERROR; an actual escaping violation terminates at the applicable boundary. No exception is converted into Outcome::Failure by that promise. A value successfully transferred out of the frame subsequently follows its receiving owner's ordinary lifecycle contract.

### 7.3 Cold creation

An async call has an explicit admission boundary. It evaluates the callable expression once, then evaluates the first Context argument once and snapshots that description. It next admits the final frame and support resources. On successful admission it establishes the frame's Context, transfers or copies the closure's owned capture state in capture order, and then evaluates each remaining argument and directly initializes its final frame parameter before evaluating the next argument. Callable and argument expressions therefore retain left-to-right order; no later argument is evaluated before initialization of an earlier parameter completes. A same-type prvalue constructs directly in its final parameter storage under mandatory elision, without an extra temporary or an intervening move.

If frame-resource admission returns AllocationFailure or ResourceLimit, the call returns a terminal failed Task containing that bounded error inline before evaluating any later argument. No fallback allocation, result T construction, or transfer of the callable's owned state is required. Effects already performed by evaluating the callable expression and Context remain observable. In particular, an expiring closure is not consumed by the admission protocol on this path, although the callable expression itself may already have performed explicit moves or other effects.

After admission, an argument or frame-parameter/capture construction failure stops later argument evaluation and cleans up only successfully constructed frame objects under the ordinary permitted rollback and noexcept rules. On a continuing rollback path, the matching providers then release the failed frame/support allocations exactly once; no unreachable partial task retains them. Caller-side argument-expression exceptions retain their ordinary enclosing handlers. They and callee-side construction exceptions are never converted into task Failure. On success, the call shall resolve execution initialization after argument/parameter construction and return a cold Created task. An observed selection captures its controls/status under Chapter 17; a Native selection uses its declared native environment.

`Task<T>::failed(error)` explicitly constructs that terminal failed form. It does not throw or install a handler. A non-coroutine provider may produce a Task only under the same ownership, completion, and publication protocol; a factory that starts external work during its call must declare that effect rather than claiming cold async-call behavior.

The phase-aware function type `function<async T(Parameters...)>` preserves this protocol through indirect calls. Its native ABI descriptor supplies frame/support admission, final parameter-slot representation/alignment access, successful-construction registration and partial rollback, cold-task commitment, and the matching release operations. A concrete implementation may use constant per-function descriptors and native entry points; it need not install a universal dispatcher or allocator. Caller-constructed slots and their argument types must satisfy the same versioned contract across separate compilation. The pointer representation is declared for this callable category and is not assumed to be an ordinary C/C++ code-entry pointer. An indirect async call shall retain that admission protocol, including the conditional evaluation of later arguments.

## 8. Starting, awaiting, and completing tasks

The execution states are `Created`, `Queued`, `Running`, `Suspended`, `Cancelling`, and `Terminal`. A moved-from or consumed handle is `Empty`. Exactly one executor invocation may execute a frame at a time. Resumption is serialized; suspension never permits concurrent execution of two continuations of one frame.

`std::task::start(task)` returns `std::Result<void, TaskError>`. It commits executor admission before making a Created task runnable. Rejected admission leaves that task owned and unexecuted. An Empty handle or repeated start of an active task reports InvalidState. Start of any valid Terminal task succeeds without executor admission, restart, consumption, or result mutation, including an inline failed task.

Successful start is a publication boundary: actions sequenced before its admission commit happen before the first task-body action. This includes final frame initialization and prior caller effects that happen before start. Await and blocking join use the same publication boundary when starting a cold task. Moving a handle or merely constructing a cold task does not independently publish it to an unrelated agent.

`await expression` is a unary suspension expression valid only in an async body or async lambda. It evaluates its operand once and consumes an expiring `Task<T>`; a named handle uses `await std::move(task)`. Operand evaluation and successful ownership transfer precede the await-entry cancellation checkpoint. A selected cancellation therefore disposes the acquired Created/Terminal child or drains an active child before continuation cleanup; it does not lose an expression-created child. An exception before the transfer commits remains a caller-side expression failure. Without selected cancellation, an Empty operand yields Failure(InvalidState). Await's value is `Outcome<T>`, with no implicit extraction of Value.

Await does not install an exception handler or convert an escaping language exception into an outcome. Exceptions from evaluating its operand or delivering a result follow the executing parent's callable contract and handlers; an uncaught exception from the child follows that child's execution boundary and the selected runtime policy.

Await starts a cold operand on that operand's declared executor. If admission fails, it releases the never-started operand under its lifetime rules and yields Failure. If the operand is terminal, await can complete without physical suspension. Otherwise the parent owns the awaited child while suspended and registers one continuation. Registration and terminal publication use a single synchronized protocol, including the already-completed race; the protocol shall publish readiness or register the continuation as one coherent transition.

Body execution, parameter/capture cleanup, and completion preparation occur before terminal publication. The returned T is constructed before required exit cleanup; it is not published if that cleanup fails. Terminal publication uses release semantics and a receiving await/join observes it with acquire semantics. Parent actions after completion observation therefore happen after the child's published execution effects.

Frame-local objects remain alive across suspension at stable admitted storage. A saved pointer to a local is not retargeted to another worker's stack. A temporary whose lifetime crosses await must have suitable frame/explicit storage. Await is not permitted inside an active constructor, destructor, Cleanup, or construction-tail transaction that cannot suspend under its lifecycle contract.

`std::task::join(task)` returns `std::Result<Outcome<T>, WaitError>`. It is an explicit blocking operation, not implicit executor pumping. An Empty handle reports InvalidState. Unsupported waiting, a known self-dependency, or waiting on work that requires the current sole manual driver reports the corresponding Unsupported, WouldBlock, or Deadlock without losing ownership. Join validates waiting/progress capability before starting a Created task. Poll on Created returns WouldBlock without starting it. An admitted cold join uses the same start protocol; rejection returns WaitError::StartRejected containing TaskError and retains Created. A timeout after successful start preserves the active task rather than reverting it to Created. On successful delivery join consumes the completion and empties the handle.

Value delivery uses T's declared move/construction effects. An exception from a user-defined move or destructor is not converted into TaskError or WaitError. Await retains internal ownership of its consumed terminal child while constructing the receiving Outcome. If that construction fails with a catchable language exception, ordinary destination rollback occurs, then await consumes the child's remaining source-payload obligation and releases completion storage exactly once before propagating into the parent. The original source handle is not restored. Cleanup failures follow the selected aggregate/destructor policy.

Join retains its terminal handle until receiving-value construction commits. If that construction itself fails, destination rollback occurs but the handle and source-payload lifetime remain owned by the caller. The source value has exactly T's failed-move guarantee; retry is permitted only when T's contract permits another move. After successful receiving-value construction, consumption commits and the join handle becomes empty before retirement of the old source payload. A subsequent source-destructor failure does not restore that handle: continuing aggregate cleanup releases the old completion storage, destroys the still-unpublished receiving result, and propagates the failure. Await applies the same post-construction retirement rule to its internally owned source. On normal completion only the receiver owns the transferred value. Completion is never extracted or destroyed twice.

Provider progress guarantees are explicit. A manual executor needs explicit driving; a suspended task need not progress while no provider runs. Blocking a worker does not implicitly permit reentrant execution of unrelated tasks. State queries and cancellation operations use their declared synchronized control state, while concurrent movement/destruction of the same owner handle requires external coordination.

## 9. Cooperative cancellation and detached ownership

### 9.1 Requests and checkpoints

`std::sync::CancelSource` owns cancellation state; `CancelToken` is a copyable borrowed observation handle. The state uses explicit source/control resources where needed and outlives all token uses. `request_cancel(source)` records an idempotent request through a synchronized protocol; observing that request has the declared acquire effect. It is not a permission to destroy an arbitrary stack or frame.

A Task also admits cancellation through its live ownership/control interface. Its Context selects `cooperative` or `finish`. Under cooperative policy, `std::task::checkpoint()` is a task-control intrinsic at an admitted statement boundary. It continues normally without a pending request; otherwise it selects cancellation and exits the task continuation through generated cleanup edges. It is not a language exception and is not caught by `catch (...)`.

Checkpoint is lexically associated with the current async frame. It cannot be address-taken, invoked as an unaware foreign callback, or used to interrupt an ordinary helper while its call is in progress. Helpers can inspect a token and return normally to a checkpoint. Running constructors, allocator mutations, and arbitrary native frames are not asynchronously unwound.

Await entry after operand ownership transfer, a recorded suspended-await point, resumption before user continuation, and successful return commitment are cancellation checkpoints. Constructors, result receiving construction, and source retirement are not asynchronously interrupted by a cancellation request. Under finish policy, requests may be observed but these points do not cancel the computation. No bounded response time is promised when the executor or an external operation does not progress.

For a cooperative successful return, Value publication and cancellation acceptance are linearized by one terminal-state protocol. If publication wins, a later request does not revoke the Value. If cancellation wins, the uncommitted value is destroyed once and Cancelled is published only after required cleanup. An already committed explicit Failure is not replaced by cancellation.

### 9.2 Awaited dependencies and cleanup

Cancellation of a suspended parent does not free its frame while an owned child or registered provider operation may still access it. The cancellation coordinator requests cooperative stop of owned work and drains it to a terminal/quiescent state before destroying the parent's live locals. A finish-policy child is allowed to finish. Cancellation therefore need not complete immediately even when the parent's body is suspended.

Provider cancellation requires acknowledgment that no late callback can access released storage. Completion, cancellation, continuation registration, and unregistering callbacks must prevent double resumption or access after frame release. Previously performed external effects are not automatically compensated. A provider promising reversible effects supplies its explicit compensation contract; irreversible work may require finish semantics.

Cancellation cleanup follows reverse successful construction and the selected destructor profile. In Release, an escaping destructor failure terminates immediately. Numeric Trap or ContractTrap terminates without adding cancellation cleanup. A pending request is not a hidden exception-aggregation mechanism.

### 9.3 Owners and disposal

A Created task can be explicitly closed or normally destroyed without running its body; its initialized parameters/captures and frame are released. A terminal task can be destroyed with its remaining result/record. A Queued, Running, Suspended, or Cancelling task must first be awaited/joined or transferred to an explicit owner. An unresolved active-owner destructor shall invoke ContractTrap.

Explicit close of Empty is a successful no-op. Close rejects an active state without transferring ownership. An accepted Created/Terminal close empties the public handle before consuming frame/payload destruction obligations; continuing cleanup releases its storage. A later destruction failure never restores the handle or permits a second retirement. Completion observers acquire terminal information without consuming it; a state snapshot alone is not permission for concurrent handle movement or destruction.

`std::task::detach(task, owner, completion)` returns a Result and transfers ownership only after successful owner/resource admission. The explicit `std::task::Owner` retains the task and completion callable until both have finished their cleanup. Completion receives the Outcome and CompletionInfo, including the optional readable final FP-status snapshot. Ignoring a value uses an explicitly selected discard completion policy, not an invented anonymous owner.

The owner rejects new work after close begins. Explicit `close(owner, drain_policy)` waits for owned work and callbacks, optionally requesting cooperative cancellation. A failed/timed-out close does not release live resources. Destroying an unresolved owner invokes its contract-failure outlet. Borrowed resources, callback code, and loaded libraries remain valid until quiescence; ownership of Task/Thread does not automatically retain arbitrary captured pointers or foreign modules.

The [concurrency interfaces](17_concurrency_interfaces.md#chapter-17-concurrency-interfaces) specify Open/Closing/Closed transitions, serialized close, reentrant Deadlock, cold admission failure delivery, retry without duplicate callbacks, and completion-executor admission. An accepted detached completion reserves its required support before transferring ownership; later inability to allocate a queue record cannot lose that callback. Its delivery and callback invocation belong to the completion entry's logical exception boundary, including inline execution.

## 10. Execution contexts and failures

Execution initialization shall use Chapter 17's `ExecutionInit` selection. Native supplies the provider's unobserved environment. InheritClear shall inherit the creator's observation contract; an observed parent supplies controls with clear history, while a Native parent supplies Native execution. Explicit controls/status select an observed-context capability.

For an observed task, suspension and resumption shall preserve its logical controls and accumulated flags, with worker restoration at the selected boundary. Execution cleanup shall use that task context. Native-only execution shall carry no compulsory sticky-history record or per-resume FP save/restore. A strict operation or boundary shall obtain the stronger observation/isolation capability it requests under Chapter 04.

Final completion publication shall synchronize the optional observed-status snapshot. Native unobserved completion shall publish None. Join, await, completion callbacks, and drain shall preserve their receiving context; flag merging is an explicit operation. A completion callback shall use its declared initialization policy.

Synchronous disposal of a Created task shall use the disposing caller's active context. Execution/cancellation cleanup shall use the admitted task's policy. Terminal-result delivery and disposal shall use the receiver/discarder context and preserve the already-published completion information.

Task/thread entry is a logical exception boundary independent of whether an executor happens to call inline. Handlers inside that entry remain effective. A surrounding caller's `try` around start or await is not a handler for an otherwise uncaught child-body exception. Release termination occurs immediately when the exception has no permitted programmer handler within its propagation boundary; no implicit catch-all converts it to Outcome Failure. The aggregate profile may perform its specified terminal observation, not resume the failed application.

Programmer-written handlers may explicitly produce application `Result<T,E>` values or retain observations under the exception contract. Admission failure and explicit `Task<T>::failed` remain ordinary Outcome Failure. A language exception in argument evaluation, parameter construction, delivery, or callback code follows its own permitted handlers. Numeric Trap and ContractTrap are never task results, cancellation signals, or catchable language exceptions.

## 11. Providers, foreign operations, and configuration

The atomic provider declares the CXXN memory-model version, supported representations, alignment, lock-free properties, order/fence lowering, and fallback dependencies. Direct sharing with foreign `_Atomic` or C++ atomic objects additionally requires compatible representation and a validated memory-model mapping. Matching size or using the same processor instruction is insufficient. Opaque adapters may require all accesses to pass through one compatible provider; arbitrary foreign plain accesses do not become atomic.

Thread/task providers declare startup/TLS attachment, publication, blocking and progress behavior, frame/control allocation, cancellation quiescence, exception boundaries, FP-context preservation, and code/resource lifetime requirements. A returned native object remains compatible with the selected linker/ABI contract; it does not imply a default C++ Task, closure, atomic, or allocator-object layout.

Chapter 08 owns the configuration keys and defaults. Actual executors and frame ResourceRefs shall be supplied through Context; providers supply declared capabilities. Chapter 17 owns execution-initialization and completion interfaces. Unsupported required capabilities and incompatible direct bindings yield ERROR.

## 12. Required executions and source examples

Assume `x` and `y` are initialized atomic integers and `r1` and `r2` are separate ordinary result slots read only after joining both threads.

| Two-agent execution | Required treatment |
| --- | --- |
| A stores `x=1` Relaxed then loads `y` Relaxed; B stores `y=1` Relaxed then loads `x` Relaxed. | Both reads may observe zero; per-location coherence does not impose cross-location SC. |
| The same operations all use SeqCst. | Both reads cannot observe zero; that would require a cycle in the SC order. |
| Each agent places a SeqCst fence between its relaxed store and relaxed load. | Both-zero is excluded by the fence/coherence constraints. |
| A writes ordinary payload then release-stores a ready flag; B's acquire load reads that release before reading payload. | The payload initialization happens before B's read, provided there is no later conflicting write. |
| The flag operations are only Relaxed, with no other synchronization. | Reading the ordinary payload is a data race; the flag's numerical value does not supply a publication guarantee. |
| Two loads each justify a store solely from the other's hypothetical value. | A self-supporting dependency cycle cannot manufacture the value. |
| Pointer publication succeeds, then the publisher frees the pointee before the consumer finishes. | Atomic publication does not prevent the lifetime violation. |
| Cancellation reaches a parent suspended on a finish-policy child using its locals. | The parent retains its frame and drains the child before destroying those locals. |
| A native worker exits while a migrated task retains a pointer to that worker's TLS. | The pointer requires an independent surviving lifetime; task migration does not preserve TLS. |

An explicit async value-consumption pattern is:

```text
alias IntTask = std::task::Task<i32>;
alias IntOutcome = std::task::Outcome<i32>;

declare void accept_value(i32 value);
declare void accept_cancel(std::task::CancelReason reason);
declare void report_failure(const<std::task::TaskError>& error);

async void use(std::task::Context context) {
    IntTask pending(compute(context, 41));
    IntOutcome outcome(await std::move(pending));
    match (outcome) {
        case IntOutcome::Value(ref value) { accept_value(value); }
        case IntOutcome::Cancelled(ref reason) { accept_cancel(reason); }
        case IntOutcome::Failure(ref error) { report_failure(error); }
    }
    return;
}
```

The match does not copy or unwrap the outcome implicitly. The caller supplies the Context's resources and executor; merely invoking `use` returns a cold task. Starting, awaiting, joining, or transferring that task remains an explicit ownership/execution action.

