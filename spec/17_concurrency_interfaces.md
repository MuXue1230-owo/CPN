<a id="chapter-17-concurrency-interfaces"></a>

# CPN26 Concurrency Interfaces Specification

## 1. Interface conventions

The atomic, synchronization, thread, and task interfaces SHALL apply the [common library model](14_standard_library.md#chapter-14-standard-library), [core operational model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance), and [concurrency memory model](13_concurrency_memory_model.md#chapter-13-concurrency-memory-model). This chapter supplies their source signatures and state transitions.

T, F, and E SHALL denote constrained value, callable, and error types. Result, Option, Ref, and ResourceRef SHALL use their existing std/std.mem identities. Each table SHALL use its stated namespace; abbreviated default cases SHALL denote their type-qualified values. Operational errors SHALL carry their listed case and optional bounded usize provider detail. WaitLimit, DrainPolicy, ExecutionInit, OwnerState, and CancelToken SHALL denote their std::sync identities; FPControl and FPStatus SHALL denote their std::numeric identities.

Synchronized control queries SHALL require a live stable handle. Handle movement, consumption, and destruction SHALL be coordinated with those queries. An Owner SHALL support its stated concurrent admission and closure protocol while its own lifetime remains active. Borrowed provider/code requirements SHALL cover accepted operations, callbacks, registration retirement, and final release.

## 2. Atomic locations

### 2.1 Types and construction

`std::atomic::MemoryOrder` SHALL expose Relaxed, Acquire, Release, AcqRel, and SeqCst. Its intrinsic order arguments SHALL be required constants in ordinary call positions. Runtime selection SHALL dispatch to an admitted constant-policy call.

`Atomic<T>` SHALL require a provider-supported fixed integer, Boolean, pointer, or floating representation. The provider SHALL publish comparison representation, alignment, operations, and lock-free properties. Atomic<T>() SHALL initialize typed zero; Atomic<T>(T initial) SHALL initialize the supplied bits. A self-contained provider SHALL supply these forms. A provisioned fallback SHALL use Atomic<T>(T initial,SupportRef support), borrowing explicitly admitted support from its provider.

Atomic construction SHALL be nonthrowing under its provider contract and precede publication. The owner SHALL remain at one stable address throughout its lifetime; constructing another Atomic from a loaded value SHALL create a distinct location. Destruction SHALL require quiescence and be nonthrowing. Reconstruction SHALL establish a new location generation with its own admitted accesses.

### 2.2 Operations

The namespace is `std::atomic`.

| Signature | Result |
| --- | --- |
| `T load(const<Atomic<T>>& object, MemoryOrder order = SeqCst) noexcept` | Atomic value snapshot. |
| `void store(Atomic<T>& object, T value, MemoryOrder order = SeqCst) noexcept` | One modification. |
| `T exchange(Atomic<T>& object, T value, MemoryOrder order = SeqCst) noexcept` | Previous representation. |
| `bool compare_exchange_strong(Atomic<T>& object, T& expected, T desired, MemoryOrder success, MemoryOrder failure) noexcept` | Representation comparison and conditional RMW. |
| `bool compare_exchange_weak(Atomic<T>& object, T& expected, T desired, MemoryOrder success, MemoryOrder failure) noexcept` | Same operation permitting spurious failure. |
| `bool is_lock_free(const<Atomic<T>>& object) noexcept` | The actual location/provider guarantee. |
| `void thread_fence(MemoryOrder order = SeqCst) noexcept` | The selected fence. |

Each CAS SHALL also expose the single-order overload with default SeqCst. Failure order SHALL be Relaxed for Release, Acquire for AcqRel, and otherwise equal success order. Load SHALL admit Relaxed/Acquire/SeqCst; store Relaxed/Release/SeqCst; RMW and fence all five. Failure SHALL admit Relaxed for every success order, Acquire for Acquire/AcqRel/SeqCst, and SeqCst for SeqCst. An invalid combination SHALL receive the central required-constant diagnostic.

Arguments SHALL be evaluated once left to right, with desired established before atomic access. expected SHALL be a writable live ordinary object disjoint from the atomic storage and accessed under its ordinary synchronization contract. Success SHALL preserve expected. Failure, including weak spurious failure, SHALL write the representation observed by that attempt into expected. Only successful modification SHALL enter modification order. Aliased source expressions for expected and desired SHALL follow ordinary evaluation and designation rules.

Atomic transport and CAS comparison SHALL operate on stored representations, preserving signed-zero and NaN distinctions and leaving FP status unchanged. Source conversions SHALL retain their separate numeric effects. A successful pointer-bit comparison SHALL preserve the pointee's existing lifetime and ownership terms.

Atomic bit operations SHALL use the numeric chapter's explicit validation and whole-location linearization. Retries SHALL reuse already evaluated arguments. Relaxed fence SHALL provide its empty inter-agent synchronization relation. Foreign atomic sharing SHALL use a validated representation, lifetime, and memory-model mapping.

## 3. Synchronization resources

### 3.1 Waiting and execution initialization

`std::sync::ProviderRef` SHALL borrow its synchronization provider; ClockRef SHALL borrow one of its clocks. WaitLimit SHALL expose Unbounded, Poll, and Until(Deadline). `Deadline(ClockRef clock,u64 tick) noexcept` SHALL preserve clock identity and the provider's tick/wrap interpretation. Until SHALL require that clock capability. An unavailable runtime wait capability SHALL report Unsupported before admission; static availability SHALL follow the central capability rule.

A limit SHALL bound waiting for the requested condition while retaining required ownership and reacquisition steps. Poll inability SHALL return WouldBlock. Expiry observed before commitment SHALL return TimedOut; a completed operation may win a race and commit success. Cancellation SHALL use its separately selected protocol.

`ExecutionInit` SHALL expose Native, InheritClear, and Explicit(FPControl control,FPStatus status), using the canonical numeric types. Native SHALL select the provider-native unobserved execution contract. InheritClear SHALL sample the creator's selected observation contract at creation commitment: Native inheritance SHALL remain Native; observed inheritance SHALL copy effective controls and initialize clear observed status. Explicit SHALL request an observed context with its supplied values. The selected provider SHALL supply the requested context or report its stated capability error before admission. This selector SHALL be nonallocating; physical context actions SHALL follow Section 8.

`SyncError` cases are `InvalidState`, `Busy`, `WouldBlock`, `Deadlock`, `TimedOut`, `Unsupported`, `ResourceLimit`, `AllocationFailure`, `ProviderUnavailable`, and `Closed`, with optional provider code.

### 3.2 Mutex, Guard, and Condvar

Mutex and Condvar SHALL own stable provider state admitted through their factory resource. Default and moved-from handles SHALL be empty. Nonthrowing move construction SHALL transfer the handle while preserving state location; move assignment SHALL require an empty destination and self-move SHALL preserve state. Destruction SHALL require quiescence, with all lock, waiter, and callback obligations discharged, then release provider state.

The namespace is `std::sync`.

| Signature | Contract |
| --- | --- |
| `Result<Mutex, SyncError> make_mutex(ProviderRef provider, ResourceRef resource) noexcept` | Create an unlocked, nonrecursive mutex. |
| `Result<Condvar, SyncError> make_condvar(ProviderRef provider, ResourceRef resource) noexcept` | Create a condition variable. |
| `Result<Guard, SyncError> lock(Mutex& mutex, WaitLimit limit = Unbounded)` | Acquire exclusive ownership or return an error without ownership. |
| `Result<Option<Guard>, SyncError> try_lock(Mutex& mutex)` | Some on acquisition, None on ordinary contention, Err on another reported failure. |
| `void unlock(Guard& guard) noexcept` | Release an owned lock and empty the guard. |
| `Result<void, SyncError> wait(Condvar& condition, Guard& guard, WaitLimit limit = Unbounded)` | Release, wait, and reacquire under the rules below. |
| `void notify_one(Condvar& condition) noexcept` | Make at most one applicable waiter eligible. |
| `void notify_all(Condvar& condition) noexcept` | Make all applicable waiters eligible. |

Guard SHALL be default-empty and move-only, owning one lock-release obligation when nonempty. Move construction SHALL be nonthrowing; move assignment SHALL require an empty destination; self-move SHALL preserve state. Destruction SHALL unlock a nonempty guard, and empty unlock SHALL preserve empty state. Lock ownership SHALL remain affine to its acquiring native thread, including across handle moves and task suspension. A detected recursive lock request SHALL report Deadlock under the nonrecursive mutex contract.

Successful acquisition SHALL have acquire semantics; unlock SHALL have release semantics and be nonfailing for a valid owner. Protected object lifetimes SHALL remain under their designated owners.

Lock/try_lock on empty Mutex SHALL report InvalidState. Wait admission SHALL require live matching provider objects and a nonempty Condvar/Guard; failure SHALL preserve the guard and report InvalidState or the stated error. Concurrent waiters on one Condvar SHALL use one mutex identity. Registration and release SHALL form the provider's atomic wait transition. Notification SHALL make applicable waiters eligible; callers SHALL test their predicate while holding the mutex, including after a spurious successful wait.

After wait releases the mutex, every ordinary return, including timeout/error, SHALL first reacquire that same mutex into the same guard. This reacquisition may extend past the deadline. The suspended wait SHALL retain exclusive control of the guard until return. Notification SHALL affect the currently applicable waiter set. A violated mandatory reacquisition contract SHALL dispatch to its provider boundary.

### 3.3 Cancellation state

`CancelSource` SHALL own stable cancellation state and be default-empty/move-only. CancelToken SHALL be a trivial copyable borrow; its default-empty observation SHALL be false. Nonthrowing source move SHALL preserve state identity and empty the source handle. Move assignment SHALL require an empty destination; self-move SHALL preserve state.

| Signature in `std::sync` | Contract |
| --- | --- |
| `Result<CancelSource, SyncError> make_cancel_source(ResourceRef resource) noexcept` | Admit a fresh, initially unrequested state. |
| `CancelToken token(const<CancelSource>& source) noexcept` | Borrow its state; an empty source produces an empty token. |
| `bool request_cancel(CancelSource& source) noexcept` | True only for the first recorded request; empty source returns false. |
| `bool cancel_requested(CancelToken token) noexcept` | Acquire observation of the request. |

Request publication SHALL be release-ordered and idempotent. A fresh source SHALL establish a fresh unrequested identity. Source destruction SHALL require completed subscription retirement, quiescent access, and ended nonempty-token uses, then release the state. A Task Context SHALL retain its token's borrowing obligation through subscription retirement. Accepted cancellation SHALL proceed at the owning operation's checkpoints.

## 4. Native threads

### 4.1 Creation and completion

`std::thread::ProviderRef` borrows a native-thread provider. `Options` is a nonallocating description with constructor:

```text
Options(ProviderRef provider, ResourceRef stack_resource,
        ResourceRef control_resource, usize stack_bytes,
        std::sync::ExecutionInit initialization,
        std::sync::StopRef stop);
```

Zero stack_bytes SHALL select the declared provider default; another value SHALL request that minimum admitted stack extent using published geometry. A selected host stack service may back stack_resource. StopRef() SHALL be empty; `StopRef(function<void(void*) noexcept>* request,void* state)` SHALL borrow a nonnull request entry and state. Invocation SHALL call request(state), and an empty StopRef SHALL perform the empty request action. Its declared stop adapter may request a CancelSource. Options SHALL require its listed arguments and construct nonthrowingly.

Thread SHALL be default-empty and move-only, with Empty and Joinable handle states. Completion SHALL preserve the Joinable obligation until consumption. Nonthrowing move construction SHALL empty the source; move assignment SHALL require an empty destination; self-move SHALL preserve state.

`ThreadError` SHALL expose InvalidState, ResourceLimit, AllocationFailure, ProviderUnavailable, StartRejected, Busy, WouldBlock, Deadlock, TimedOut, Unsupported, and OwnerClosing. `ThreadCompletion` SHALL contain `Option<FPStatus> final_status`: Some for a selected observed execution context and None for Native execution. The immutable value SHALL report completed execution under that observation contract.

| Signature in `std::thread` | Contract |
| --- | --- |
| `Result<Thread, ThreadError> start(Options options, forward F entry)` | F is constructible from the supplied category and invocable as `void()`. |
| `Result<ThreadCompletion, ThreadError> join(Thread& thread, std::sync::WaitLimit limit = Unbounded)` | Consume on completed successful join. |
| `bool joinable(const<Thread>& thread) noexcept` | Whether the handle owns its join obligation. |
| `Result<void, ThreadError> detach(Thread& thread, Owner& owner)` | Transfer that obligation after owner admission. |

Start SHALL admit stack/control and final callable storage before entry transfer. Operational failure SHALL retire constructed entry state and admitted resources on its continuing path; consumed caller arguments SHALL retain their own effects. Native-start commitment SHALL enable user entry. Inherited execution initialization SHALL be sampled after entry transfer, and the required TLS domain SHALL be ready before entry. The worker may execute before start returns.

Join on Empty SHALL report InvalidState; self-join SHALL report Deadlock. A failed or timed-out wait SHALL preserve Joinable. Successful join SHALL wait for entry/capture cleanup, TLS destruction, and provider quiescence, acquire completion effects, and empty the handle. Its completion value SHALL carry the selected optional status; merging observed status SHALL use an explicit numeric operation. Destruction of Joinable SHALL dispatch to ContractTrap.

### 4.2 Detached thread owners

`OwnerPolicy` SHALL expose Discard and Notify(CompletionSinkRef sink,ExecutionInit initialization). `CompletionSinkRef(function<void(void*,const<ThreadCompletion>&) noexcept>* notify,void* state)` SHALL borrow its nonnull entry and state. Creation SHALL snapshot the selected initialization. After worker/TLS cleanup and quiescence, explicit close SHALL invoke each due notification on its calling thread with that thread's attached TLS and the owner's selected execution context. Observed-context entry/exit SHALL follow Section 8. Sink and stop-adapter borrows SHALL cover every invocation.

`make_owner(ResourceRef records,OwnerPolicy policy) noexcept` SHALL return Result<Owner,ThreadError> and establish Open stable state. Default/moved-from Owner SHALL be Closed. Nonthrowing move SHALL transfer that state; assignment SHALL require Closed destination, with self-move preserving state. `close(Owner&,DrainPolicy,WaitLimit limit=Unbounded)` SHALL return Result<void,ThreadError>. DrainPolicy SHALL expose Drain and RequestCancelAndDrain. `std::sync::OwnerState` SHALL expose Open, Closing, Closed; thread::state(const<Owner>&) SHALL return its synchronized snapshot.

Detach SHALL validate Joinable and Open, admit the owner record, and atomically transfer the obligation. Failure SHALL preserve caller ownership. Finished workers SHALL remain admitted inputs. The owner SHALL retain each accepted record through worker quiescence and notification.

Close SHALL commit Open to Closing and stop further detach admission. A racing detach SHALL either commit into the drain or retain caller ownership with its error. RequestCancelAndDrain SHALL invoke each supplied stop adapter at most once; empty adapters SHALL leave their workers to finish. Close calls SHALL be serialized: competition SHALL report Busy, and reentry from included workers/sinks/adapters SHALL report Deadlock. User callbacks SHALL finish under their own execution contract before waiting policy resumes.

Each notification SHALL commit at most once. Timeout/error SHALL retain Closing and unresolved records, including pending notifications. Retry SHALL continue that retained state and may upgrade Drain to RequestCancelAndDrain while preserving earlier requests. Successful drain SHALL release records and select Closed; close of Closed SHALL succeed. Destruction may retire quiescent completed Discard records. Pending workers, notifications, or admissions SHALL dispatch to ContractTrap before their resources retire.

## 5. Task contexts and handles

`std::task::ExecutorRef` SHALL borrow a concrete executor and versioned admission, queueing, execution, waiting, cancellation-acknowledgment, and retirement protocol. Its provider SHALL publish creation and driver operations, including any manual/inline execution contract. Join SHALL use the selected waiting/progress capability.

`CancellationPolicy` SHALL expose Cooperative and Finish. Context SHALL have this nonthrowing constructor:

```text
Context(ResourceRef frame_resource, ResourceRef support_resource,
        ExecutorRef executor, std::sync::CancelToken cancellation,
        CancellationPolicy policy,
        std::sync::ExecutionInit initialization) noexcept;
```

Context SHALL be a trivial borrowed description of the listed explicit arguments, with an empty token selecting an inactive external cancellation source. Construction SHALL leave frame admission to task creation. Runtime provider unavailability SHALL be an admission error; static incompatibility SHALL use the capability diagnostic. Frame and support SHALL retain distinct accounting roles even when their domains match.

`Task<T>` SHALL require a complete storable move-constructible T, with an explicit void specialization. It SHALL be default-empty and move-only. Nonthrowing move construction SHALL transfer the frame or inline completion while preserving T's location. Move assignment SHALL require Empty destination; self-move SHALL preserve state. `Task<T>::failed(TaskError)` SHALL nonthrowingly construct inline Terminal Failure with an empty live-T set and zero allocation.

`TaskError` has `AllocationFailure`, `ResourceLimit`, `ProviderUnavailable`, `StartRejected`, `InvalidState`, and `OwnerClosing`. `WaitError` has `InvalidState`, `Busy`, `WouldBlock`, `Deadlock`, `TimedOut`, `Unsupported`, `ProviderUnavailable`, and `StartRejected(TaskError error)`. `CancelReason` has `Requested`, `ParentCancelled`, and `OwnerClosing`. Their optional provider details are bounded.

Outcome SHALL select Value(T), Cancelled(CancelReason), or Failure(TaskError); Outcome<void> SHALL have payloadless Value. CompletionInfo SHALL contain bool body_entered and Option<FPStatus> final_status. Inline failure SHALL have false/None. Native execution SHALL publish None. An observed execution/cleanup context SHALL publish Some, including cleanup before body entry. Published information SHALL be immutable.

### 5.1 Cold-call protocol

An async callable SHALL have first ordinary parameter Context by value and the distinct phase-aware type function<async T(...)>. Indirect calls and generic witnesses SHALL preserve its frame-admission and destination-slot contract through the async ABI.

Creation SHALL sequence callable evaluation, Context evaluation/snapshot, final frame/support admission, capture transfer in declaration order, then each remaining argument and final parameter construction before the next argument. Admission error SHALL publish inline Failure at that phase. Same-type argument prvalues SHALL construct directly in their final parameter slots.

After parameter construction, creation SHALL sample the selected inherited initialization and publish Created with its body awaiting start. A catchable creation failure SHALL retire completed frame objects and admitted storage exactly once on its continuing path. Already consumed sources SHALL retain their declared moved-from states.

An async noexcept promise SHALL cover callee capture transfer, extra parameter binding, body execution, and frame-owned cleanup. Callable and explicit/default argument-expression evaluation SHALL remain caller phases, including an argument prvalue constructed in its final frame slot. Each phase SHALL route exceptions through its declared boundary under the common library model.

## 6. Task operations and transitions

`State` SHALL expose Empty, Created, Queued, Running, Suspended, Cancelling, and Terminal. Frame execution SHALL serialize continuation ownership.

| Signature in `std::task` | Contract |
| --- | --- |
| `State state(const<Task<T>>& task) noexcept` | Synchronized state observation under the handle-lifetime contract. |
| `Result<void, TaskError> start(Task<T>& task) noexcept` | Commit executor admission for Created. |
| `bool request_cancel(const<Task<T>>& task, CancelReason reason = Requested) noexcept` | Record a request in live control state. |
| `Result<CompletionInfo, TaskError> completion_info(const<Task<T>>& task) noexcept` | Acquire terminal information; otherwise InvalidState. |
| `Result<Outcome<T>, WaitError> join(Task<T>& task, std::sync::WaitLimit limit = Unbounded)` | Start if needed, wait, deliver, and consume. |
| `Result<void, TaskError> close(Task<T>& task)` | Dispose Empty, Created, or Terminal without starting a body. |

| Input state | start | join | close |
| --- | --- | --- | --- |
| Empty | InvalidState | InvalidState | Success, remains Empty. |
| Created | Admit or retain Created on error. | Admit, then wait and deliver. | Destroy captures/parameters and release frame. |
| Queued, Running, Suspended, Cancelling | InvalidState. | Wait and deliver if permitted. | InvalidState; retains ownership. |
| Terminal | Success preserving the existing terminal completion and handle. | Deliver existing completion. | Dispose remaining completion. |

Join SHALL admit waiting/progress capability before starting Created. A known self-dependency SHALL report Deadlock; a sole manual driver unable to wait SHALL report WouldBlock. Poll on Created SHALL return WouldBlock and preserve Created. Executor rejection SHALL return WaitError::StartRejected with its TaskError and preserve Created. After start commitment, timeout SHALL retain the active state. Terminal readiness may win a simultaneous timeout.

Start publication SHALL order preceding caller actions before the first body action. Terminal release publication SHALL follow body completion, required frame-object retirement, and completion preparation; its receiver SHALL acquire those effects. A tentative T SHALL remain unpublished through required exit cleanup.

Await SHALL evaluate its operand and consume the resulting expiring Task before its await-entry cancellation checkpoint. Earlier operand exceptions SHALL remain caller-side. Accepted cancellation SHALL dispose a Created/Terminal child or drain an active child. Otherwise Empty SHALL yield Failure(InvalidState), Created SHALL start on its own executor, and rejection SHALL dispose that consumed child and yield Failure. Terminal delivery SHALL proceed immediately; other states SHALL combine readiness observation and continuation registration as one synchronized operation. The parent SHALL retain the child through completion or cancellation drain. Invocation failures SHALL follow the common phase routing.

Join SHALL retain its terminal handle until receiving Outcome construction commits. A failed T move SHALL preserve source ownership with T's failed-move guarantee; retry SHALL require that guarantee to admit another move. Await SHALL own the consumed source internally: a catchable receiving-construction failure SHALL roll back the destination, dispose the remaining source, and release its storage before propagation.

Receiving construction commitment SHALL empty the source handle before source retirement. Continuing aggregate cleanup SHALL retire source storage and an unpublished receiving value before propagation. Each delivery SHALL consume the source payload obligation once. Close SHALL empty an accepted Created/Terminal handle before user destruction and release storage on continuing cleanup. Task destruction SHALL use close for Created/Terminal and ContractTrap for active states. Terminal failure SHALL follow the selected boundary action.

## 7. Task cancellation and detached completion

### 7.1 Cancellation commitment

Request_cancel SHALL return false for Empty/Terminal. In a nonterminal state, the first recorded request SHALL return true and retain its reason; later requests SHALL return false and preserve it. External token observation SHALL use Requested; parent/owner requests SHALL use their respective reasons. Finish SHALL record observable requests and continue its normal completion policy.

Created SHALL retain requests until execution or disposal. Close SHALL dispose its frame synchronously. Later cooperative admission SHALL inspect the request before body entry. Queued state SHALL retain its frame through the provider's callback/retirement obligation.

Cooperative cancellation SHALL be selected at explicit checkpoint statements and the defined await-entry, suspended-await, resume, and successful-return boundaries. Requests arriving during construction, delivery, retirement, or native helper execution SHALL remain pending until the next applicable checkpoint. Acceptance SHALL take the task coordinator's cancellation transition.

Successful-return commitment and cancellation acceptance SHALL share one linearization protocol. Value commitment SHALL preserve Value against later requests. Accepted cancellation SHALL retire any unpublished result exactly once and complete cleanup before publishing Cancelled. An already committed Failure SHALL retain its identity.

Parent cancellation SHALL request the appropriate stop and drain each owned child or provider registration. Finish-policy work may complete normally. Retirement SHALL acknowledge that late callbacks have ended their frame access. Completion/cancellation races SHALL select at most one resumption. External side effects SHALL follow their explicit compensation or finish contract.

### 7.2 Owner admission and closure

`std::task::OwnerOptions(ResourceRef records,ExecutorRef completion_executor,ExecutionInit initialization) noexcept` SHALL construct its trivial description. make_owner(OwnerOptions) SHALL return Result<Owner,TaskError>, snapshot the selected completion initialization, and establish Open stable state. Default/moved-from owners SHALL be Closed. Nonthrowing move SHALL transfer state; assignment SHALL require Closed destination and self-move SHALL preserve it. task::state(const<Owner>&) SHALL observe the synchronized OwnerState.

`detach(Task<T>& task,Owner& owner,forward F completion)` SHALL return Result<void,TaskError>. F SHALL be constructible from its supplied category and invocable as void(Outcome<T>,const<CompletionInfo>&). DiscardCompletion SHALL provide that signature and consume the delivered outcome through ordinary destruction. F invocation and destruction SHALL retain their declared effects.

Detach SHALL require a nonempty task and Open owner, then admit record storage, callback state, and completion-executor capacity before commitment. Failure SHALL preserve task ownership while consumed callback sources retain their own effects. A close race SHALL select either committed owner inclusion or rejection with caller ownership. Committed transfer SHALL empty the caller handle.

The owner SHALL start accepted Created tasks. A subsequent rejection SHALL dispose the cold frame and deliver Failure to completion under the committed detach obligation. Completion may execute before detach returns. Detach admission SHALL reserve mandatory completion/retirement support for its accepted callback.

Completion SHALL execute once after terminal publication using its selected context. Outcome SHALL construct directly in the final callback parameter under consumed-source delivery rules. The completion entry SHALL cover delivery, invocation, and callback-argument retirement as one owner obligation. An exception escaping that entry SHALL dispatch to its logical entry boundary. Discarded outcomes SHALL retain their ordinary destruction policy.

`close(Owner& owner,DrainPolicy policy,WaitLimit limit=Unbounded)` SHALL return Result<void,WaitError> and use the thread Owner's Open/Closing/Closed admission, retry, and quiescence transitions. Competing close SHALL report Busy. RequestCancelAndDrain SHALL record OwnerClosing requests while Finish tasks complete normally. A task/callback included in its own drain SHALL report Deadlock. Waiting SHALL require the selected completion executor's admitted progress capability.

Owner close success SHALL require quiescent accepted tasks, callbacks, payload retirement, registrations, and record release. Timeout/error SHALL retain Closing and its unresolved resources, including a terminal completion awaiting retirement. Destruction SHALL retire a quiescent owner or dispatch to ContractTrap while unresolved obligations remain. Storage retirement SHALL follow acknowledged final callback use.

## 8. Execution context and provider boundaries

ExecutionInit SHALL select the numeric execution contract defined by the [numeric integration chapter](04_numeric_integration.md#chapter-04-numeric-integration). Native execution SHALL use the provider-native environment and publish an absent final-status observation. Selected observed task execution and execution/cancellation cleanup SHALL restore their logical controls/status as needed to preserve that contract; leaving such a continuation SHALL restore the worker's required observed context. Synchronous Created disposal SHALL use the caller's current selected context. Terminal value delivery/disposal SHALL use the receiver's selected context and preserve the child's immutable completion information.

An observed caller requiring isolation across a Native call SHALL use the declared boundary adapter. Native-only execution SHALL receive the core model's freedom to realize its context through provider-native state. Explicit FPStatus observation and observed context capabilities SHALL retain their selected function. Status merging SHALL use its named numeric operation.

Thread, Task, and independent callback entries SHALL define handler-search intervals in inline, manual, and asynchronous execution alike. Programmer handlers SHALL operate within their entry interval. An exception reaching an entry's terminal boundary SHALL dispatch to that boundary. ContractTrap and NumericTrap SHALL use their direct terminal outlets under the common model.

Resources and callback code SHALL remain live through acknowledged quiescence. Cross-module async descriptors SHALL preserve final-slot layout, admission, registration, rollback, cold commitment, and release identity. Foreign synchronization SHALL require its validated provider mapping. A changed public ownership, publication, execution-context, or failure contract SHALL carry its corresponding interface identity.

