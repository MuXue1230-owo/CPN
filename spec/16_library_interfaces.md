<a id="chapter-16-library-interfaces"></a>

# CPN26 Core Library Interfaces Specification

## 1. Interface interpretation and identity

The enabled std, std.mem, std.collections, and std.text interfaces SHALL apply the [common library operation model](14_standard_library.md#chapter-14-standard-library) and the [core operational model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance). This chapter supplies their concrete payloads, ownership transitions, and callable catalogue.

In signature tables, self denotes the receiver; `const<C>&`, `C&`, and `C&&` denote read-only, mutable, and expiring receivers. `args...` SHALL forward each argument once under ordinary call rules. Type parameters SHALL be complete object types except for a stated void specialization. Public capabilities SHALL consist of the declared operations with their stated static constraints.

Unit, Ref, Option, Result, and AccessError denote their std identities. Memory, collection, and text names belong respectively to std::mem, std::collections, and std::text. Returned references and views SHALL expose the specified borrow origin and referent qualification. Explicit retained-exception operations belong to the [error and recovery chapter](28_error_and_recovery.md#chapter-28-error-recovery).

## 2. Error values

The following tagged errors SHALL use the bounded value contract in the common model. Each selected case SHALL carry exactly its stated detail. The provider ABI SHALL define the tag representation; copying and movement SHALL preserve the selected case and information.

`std::AccessError` SHALL expose payloadless cases `MissingValue` and `WrongCase`. The first denotes an empty Option; the second denotes an accessor selecting the inactive Result case.

`std::mem::MemoryFault` SHALL contain `Option<usize> position`, `Option<usize> requested`, and `Option<usize> available`. A present value is exact in the operation's declared unit; unavailable information SHALL be None. `MemoryError` SHALL expose cases `Null`, `Bounds`, `Alignment`, `Lifetime`, `Representation`, `Ownership`, `AddressSpace`, and `Capacity`, each carrying `MemoryFault`. In a byte operation these fields count bytes; in an element operation they count elements. Alignment uses byte alignment. An ownership or generation failure need not have a numerical position.

`std::mem::AllocationRequest` SHALL contain `Option<usize> bytes`, `usize alignment`, and `Option<usize> available_bytes`. `AllocationError` SHALL expose cases `SizeOverflow`, `UnsupportedAlignment`, `ResourceLimit`, `AllocationFailure`, and `ProviderUnavailable`, each carrying this record. A representable requested byte count is Some of that exact count; an unrepresentable request is None. Unknown available capacity is likewise None. The error SHALL preserve those exact-or-absent values.

`std::mem::ResourceError` SHALL expose cases `Allocation(AllocationError)`, `Memory(MemoryError)`, payloadless `Outstanding`, and payloadless `TransferUnavailable`. `Outstanding` denotes an attempted domain closure with unresolved obligations. `std::mem::ViewError` SHALL expose cases `Memory(MemoryError)` and `Allocation(AllocationError)`; tracking admission can therefore distinguish invalid designation from unavailable metadata storage.

`std::collections::ContainerError` SHALL expose cases `Capacity(MemoryFault)`, `Memory(MemoryError)`, `Allocation(AllocationError)`, and payloadless `TransferUnavailable`. `Capacity` includes an unrepresentable element extent and an exceeded fixed capacity. An out-of-range existing element index uses `Memory(Bounds(...))`. These error identities SHALL apply in every ordinary integer execution profile.

`std::text::TextFault` SHALL contain `usize byte_offset`. `TextError` SHALL expose cases `InvalidEncoding(TextFault)`, `InvalidScalar(TextFault)`, `InvalidBoundary(TextFault)`, `EmbeddedZero(TextFault)`, `MissingTerminator(TextFault)`, `Memory(MemoryError)`, and `Allocation(AllocationError)`. An encoding error identifies the first byte at which validation cannot continue; a truncated final sequence identifies its leading byte. A boundary error identifies the requested boundary. MissingTerminator identifies the supplied extent's end.

## 3. Minimal values

### 3.1 Unit, Ref, movement, and swap

`Unit()` SHALL construct the single Unit value. Copying, movement, and destruction SHALL be nonthrowing; equality SHALL be true and inequality false. `Ref<T>(T& object)` SHALL establish a non-null borrow. `get()` SHALL return T& through either mutable or read-only wrappers. `Ref<const<T>>` SHALL expose a read-only referent; explicit construction from Ref<T> SHALL preserve the existing borrowing terms.

`move(forward T object)` SHALL produce an expiring view of the same object, removing a deduced reference from T and retaining object qualification. An already-expiring argument SHALL remain expiring. A prvalue materialized for this call SHALL retain its ordinary full-expression lifetime. `forward<T>(parameter)` SHALL restore the category and type recorded by the forwarding parameter. `discard(value)` SHALL use the common model's explicit acknowledgement operation.

`swap(T& left,T& right)` SHALL use the type's explicit swap contract when supplied. Its value fallback SHALL require move construction and move assignment, then move into a temporary, assign right to left, and assign the temporary to right. Self-swap SHALL preserve both designations. Each failing move SHALL retain its declared guarantee. Owning-library overloads SHALL exchange complete handles and resource identities while preserving element locations.

### 3.2 Option

| Receiver or construction | Result | Contract |
| --- | --- | --- |
| `Option<T>()`, `Option<T>::None()` | `Option<T>` | None case with an empty live-payload set. |
| `Option<T>::Some(value)` | `Option<T>` | Directly constructs the active T from value. |
| `has_value()` | `bool` | Tests the discriminant. |
| `value()` on mutable/read-only receiver | `T&` / `const<T>&` | MissingValue invokes ContractTrap. |
| `try_value()` on mutable/read-only receiver | `Result<Ref<T>, AccessError>` / `Result<Ref<const<T>>, AccessError>` | MissingValue returns Err. |
| `reset()` | `void` | Ends Some, then leaves None. |
| `emplace(args...)` | `T&` | Ends old payload, then directly constructs Some. |

Option copy/move construction SHALL require the corresponding T operation statically. Moving Some SHALL preserve the source case and T's moved-from state. Reset SHALL discharge the active payload and select None exactly once. A propagating retirement failure SHALL leave None and select propagation; successful retirement SHALL permit emplacement to construct the new payload. A failed new construction SHALL leave None. Payload retirement SHALL invalidate that generation's views. Lifetime transitions SHALL be serialized for each Option. Its public capabilities SHALL be the table's operations and the stated copy/move construction.

### 3.3 Result

`Result<T,E>::Ok(value)` and `Result<T,E>::Err(error)` SHALL directly construct their selected payloads. `Result<void,E>::Ok()` SHALL select payloadless success. Construction SHALL select a case explicitly or copy/move an existing case. `has_value()` and `has_error()` SHALL inspect that case. `value()` and `error()` SHALL return the receiver-qualified active payload reference and dispatch to ContractTrap on the wrong case. The void value accessor SHALL verify Ok and return void. The public operation set SHALL be construction, observation, and the following adapters.

`try_value()` SHALL return Result<Ref<T>,AccessError> or its read-only referent form; the void specialization SHALL return Result<void,AccessError>. `try_error()` SHALL return the corresponding Ref<E> Result. Wrong-case access SHALL report WrongCase. Copy/move availability SHALL depend on every possible payload's required operation; void contributes an empty requirement set. A successful move SHALL preserve the source's case and active payload's moved-from state.

`map<U>(callable)` and `and_then<U>(callable)` SHALL provide read-only and expiring receiver overloads. Read-only success SHALL pass const<T>&, with an empty argument list for void; the error branch SHALL copy E. Expiring success SHALL pass T&&, with an empty argument list for void; its error branch SHALL move E. The requisite E operation SHALL be a static constraint. Map SHALL require exactly U as its callable result; and_then SHALL require exactly Result<U,E>. U may be void. The selected branch SHALL execute once and preserve its declared error identity and Result nesting.

`map_error<F>(callable)` SHALL pass the appropriately qualified E and require exactly F; success SHALL copy or move T as required. Each adapter SHALL preserve its receiver's discriminant and borrowing terms. A callback exception SHALL follow the common propagation path before successful adapter-result publication.

## 4. Resources, storage, and owners

### 4.1 Borrowed resource interfaces

`AllocatorRef` and `ResourceRef` SHALL be established from a live provider/domain binding. Their identity() observers SHALL return AllocatorIdentity and ResourceIdentity, opaque equality-comparable values identifying that live provider or domain. `ResourceRef::allocator()` SHALL return its AllocatorRef. Provider factories SHALL publish their concrete domain types, metadata storage, parent budgets, limits, and reservation geometry.

An owning domain SHALL expose `resource() -> ResourceRef` and `try_close() -> Result<void,ResourceError>`. Outstanding allocations, retained reservations, or tracking obligations SHALL report Outstanding and preserve state. Successful close SHALL retire further borrowing availability. Transfer and destruction SHALL follow the common domain-closure contract.

`StorageView` SHALL designate an authorized extent with its permissions, owning registration, and slot association. `capacity_bytes()`, `alignment()`, and `identity()` SHALL observe capacity, guaranteed alignment, and StorageIdentity. A copied view SHALL preserve its borrowing terms. The core `storage_of` intrinsic SHALL return this type.

| Operation | Result | Effect |
| --- | --- | --- |
| `try_allocate(ResourceRef resource, usize bytes, usize alignment)` | `Result<Allocation,AllocationError>` | Admits the full request before creating one exclusive token. |
| `try_release(Allocation& allocation)` | `Result<void,MemoryError>` | Validates and consumes an exclusively owned inactive extent on success only. |
| `try_transfer_resource(Allocation& allocation, ResourceRef target)` | `Result<void,ResourceError>` | Atomically transfers compatible release/accounting ownership while preserving object locations and values. |
| `try_adopt_owned<T>(Allocation& allocation)` | `Result<Owned<T>,MemoryError>` | Validates one complete registered object and transfers its token on success. |
| `try_make_owned<T>(ResourceRef resource, args...)` | `Result<Owned<T>,AllocationError>` | Allocates, directly constructs T, then returns its owner. |

Allocation admission SHALL validate positive supported alignment and exact byte extent. Zero-byte allocation SHALL use the provider's declared empty-allocation contract and empty dereferenceable extent. Failure SHALL return its error with pending charges retired. Invalid provider borrows SHALL use their memory-contract outlet.

### 4.2 Allocation

`Allocation()` SHALL be empty and move-only. Move construction SHALL transfer authority and empty the source. Move assignment SHALL require an empty destination, with self-move preserving state; a failed checked destination precondition SHALL dispatch to ContractTrap before either token changes. `empty()`, `capacity_bytes()`, and `alignment()` SHALL observe the token; empty capacity is zero and alignment one. `resource()` SHALL return None when empty. `storage()` SHALL return a StorageView for a nonempty mutable token and use the memory value outlet on empty access.

`try_object<T>() -> Result<Ref<T>,MemoryError>` SHALL authorize T or its admitted base view through the allocation's complete-object registration. Empty, ended, or mismatched registrations SHALL return the corresponding error. A successful borrow SHALL designate the registered generation and preserve its exclusive owner. Multiple independently registered objects SHALL retain their separate registrations.

Raw Allocation destruction SHALL retire the token representation while leaving its manual release obligation to the program. Losing a nonempty token SHALL follow the central resource-abandonment diagnostic. `try_release` SHALL require an exclusively owned inactive complete extent with a live provider; violations SHALL return the appropriate memory error unchanged. Empty release SHALL report Ownership and preserve empty state. Success SHALL invoke the selected release provider and empty the token. The provider boundary SHALL dispatch any escaping release violation to its terminal action.

Resource transfer SHALL validate compatibility and destination admission while retaining source authority. Failure SHALL preserve token, charges, registration, and address. Commitment SHALL transfer ownership and charge deltas together under the common accounting model. Required release-provider code SHALL remain live through final release. Later construction failure SHALL leave storage with its committed owner.

### 4.3 Owned

`Owned<T>()` SHALL be empty and move-only. `empty()` SHALL inspect its state. Mutable/read-only get() SHALL return T* / const<T>*, with null for empty. value() SHALL return the corresponding reference or dispatch to ContractTrap on empty; try_value() SHALL return the Ref Result or MissingValue. Move construction SHALL transfer the complete destruction entry and storage token, preserve T's location, and empty the source.

`reset()` SHALL end the registered complete object, release its inactive extent on the continuing cleanup path, and leave the owner empty. Move assignment SHALL reset the destination before transferring; a propagating reset failure SHALL leave it empty and the source unchanged. Self-move SHALL preserve state. `swap(Owned<T>&,Owned<T>&)` SHALL exchange complete ownership and resource contracts while preserving T's value and location.

`release() -> Allocation` SHALL transfer the token, complete-object registration, and destruction entry to Allocation and empty Owned. T and its extent SHALL remain live under that manual token. The returned token's checked object view SHALL designate the current T generation. `try_adopt_owned<T>` SHALL accept that pair or an equivalent single complete registration; success SHALL consume the Allocation token atomically with establishing Owned, and rejection SHALL preserve it.

Factory admission failure SHALL publish AllocationError before T construction. A catchable constructor failure SHALL roll back its completed subobjects and release the newly acquired extent through the common continuing path. Reset/destruction SHALL consume T once, then retire its inactive storage on that path. An owner exposing a base view SHALL retain the registered complete-type destruction entry. Terminal outcomes SHALL use the common failure routing.

## 5. Borrowed memory and representation operations

`Span<T>()` SHALL be empty. `Span<T>(T* data,usize count)` SHALL establish the borrowed range, admitting null at count zero. `Span<T>(T[N]& array)` SHALL preserve N, including zero. Explicit Span<const<T>>(span) SHALL establish read-only element access. Span wrapper qualification SHALL be shallow: Span<T> exposes T references, and Span<const<T>> exposes read-only elements.

| Operation | Result | Rule |
| --- | --- | --- |
| `data()`, `size()`, `empty()` | `T*`, `usize`, `bool` | Observe pointer, element count, emptiness. |
| `operator[](usize index)` | `T&` | Check index before access; memory value outlet on failure. |
| `try_at(usize index)` | `Result<Ref<T>,MemoryError>` | Bounds failure before accessing the element. |
| `subspan(usize offset, usize count)` | `Span<T>` | Check offset and remaining count; memory value outlet. |
| `try_subspan(usize offset, usize count)` | `Result<Span<T>,MemoryError>` | Same range test, Result outlet. |
| `size_bytes()` | `usize` | Checked count-times-size; memory Capacity on unrepresentable extent. |

Subspan SHALL validate `offset <= size` and `count <= size - offset`. An empty null-based subspan SHALL retain the null designation directly. Access SHALL satisfy the separate liveness, generation, and synchronization conditions of the selected memory contract.

`as_bytes(const<T>& object)` SHALL return Span<const<byte>> over that object representation. `as_element_bytes(Span<T> objects)` SHALL cover the checked representation extent of its elements. `storage_bytes(StorageView storage)` SHALL cover the authorized extent, including admitted inactive storage, and preserve existing lifetime state. These names SHALL distinguish descriptor representation, designated-element representation, and storage. Padding and uninitialized-byte observation SHALL use the central diagnostics.

`try_copy_bytes(Span<byte> destination,Span<const<byte>> source)` and its StorageView destination overload SHALL return Result<void,MemoryError>. Unequal extents SHALL report Bounds. Admission SHALL establish the specified ranges and permissions before mutation. Copy SHALL be overlap-safe; copy_bytes SHALL use the same operation through the memory value outlet. Raw-storage copying SHALL preserve the existing typed-lifetime state.

`try_representation_cast<T>(const<S>& source) -> Result<T,MemoryError>` SHALL require equal sizes and an admitted representation-copyable pair. representation_cast<T> SHALL use the memory value outlet. try_load_unaligned<T>(Span<const<byte>>) and try_store_unaligned<T>(Span<byte>,const<T>&) SHALL return Result<T,MemoryError> and Result<void,MemoryError>; their value forms SHALL use the memory value outlet. Extents SHALL equal sizeof(T). Admission SHALL validate restricted representations before value publication or destination mutation. Native byte order SHALL apply. The operations SHALL preserve the storage's existing registrations and ownership while transporting the represented value.

`try_pointer_distance(T* left,T* right) -> Result<isize,MemoryError>` SHALL use the same-array, same-generation contract and report Capacity when the mathematical element difference is unrepresentable. Raw provenance obligations SHALL use the core model's selected raw-validation mode.

An enabled tracking provider SHALL export TrackingRef with its explicit owner and metadata resource. `try_checked<T>(StorageView storage,T* pointer,TrackingRef tracking) -> Result<CheckedPtr<T>,ViewError>` SHALL validate the registered designation and admit the required tracking state. The tracking owner SHALL retain records through the declared borrowing interval, independently of the pointee's storage. `try_get() -> Result<Ref<T>,MemoryError>` SHALL validate the generation before returning a borrow; get() SHALL use the same operation through the memory value outlet. CheckedPtr SHALL be created through this factory and copied as a borrow. Its shallow wrapper qualification SHALL use CheckedPtr<const<T>> for a read-only referent. Its selected checked behavior SHALL apply under every execution profile.

## 6. Sequence containers

### 6.1 Fixed and inline storage

`Array<T,N>()` SHALL apply typed default initialization to N elements. Construction SHALL accept up to N arguments, directly construct supplied elements in index order, and default-initialize trailing elements. The zero-size specialization SHALL have an empty element-operation requirement set and null data. Positive-size copy/move SHALL require the corresponding element operation; a moved source SHALL retain N live objects in their moved-from states. Destruction SHALL proceed in descending index order. size() and capacity() SHALL equal N; data(), indexed access, try_at(), and span() SHALL use the corresponding mutable/read-only Span element rules.

`InlineVector<T,N>()` SHALL have size zero and capacity N with an empty live prefix. Its observations and views SHALL follow Vector. try_push(const<T>&), try_push(T&&), and try_emplace(args...) SHALL return Result<void,ContainerError> and admit remaining capacity before constructing the final element. Capacity failure SHALL preserve arguments; constructor failure SHALL preserve size while consumed arguments retain their own effects. try_pop() SHALL retire the last element or report Bounds when empty. clear() SHALL retire the live prefix in reverse and retain inline storage. Copying SHALL require T copying. Move construction SHALL relocate elements in ascending order and retain the source size and moved-from elements; a catchable failure SHALL retire the completed destination prefix. The public capability set SHALL contain these operations and construction, using inline storage for the fixed capacity.

### 6.2 Vector surface

`Vector<T>(ResourceRef resource)` SHALL establish an empty move-only owner with zero allocated capacity. Whole-handle move SHALL transfer buffer and resource ownership while preserving element locations, and leave a zero-capacity source with a usable resource contract. Move assignment SHALL retire the destination first; a propagating retirement failure SHALL preserve the source. swap SHALL exchange buffer and resource contracts together.

| Interface | Result | Requirement or effect |
| --- | --- | --- |
| `size()`, `capacity()`, `empty()`, `resource()` | `usize`, `usize`, `bool`, `ResourceRef` | Counts are elements; size denotes the live prefix and capacity the admitted storage extent. |
| `data()`, `span()` | pointer / Span of live prefix | Read-only receiver supplies read-only elements. |
| `operator[](usize index)`, `try_at(usize index)` | reference / Ref Result | Access the existing live prefix. |
| `try_reserve(usize count)` | `Result<void,ContainerError>` | Ensures capacity at least count using unchanged preparation. |
| `try_reserve_basic(usize count)` | same | Admits potentially throwing move relocation. |
| `try_push(const<T>& value)` | same | Requires T copying and unchanged relocation preparation. |
| `try_push(T&& value)` | same | Requires T movement and unchanged relocation preparation. |
| `try_push_basic(T&& value)` | same | Admits throwing moves and explicitly consumed aliases. |
| `try_emplace(args...)` | same | Direct construction; unchanged relocation preparation. |
| `try_insert(usize position, const<T>& value)` | same | Position in 0..size; general basic guarantee. |
| `try_erase(usize position, usize count)` | same | Validates range before shifting; general basic guarantee. |
| `try_pop()` | same | Bounds if empty; otherwise ends the final generation. |
| `clear()` | `void` | Reverse destruction; retains capacity. |
| `try_shrink(usize minimum_capacity)` | Result as above | Request must be in size..capacity; exact reduction is optional. |
| `try_clone(ResourceRef destination)` | `Result<Vector<T>,ContainerError>` | Requires copying T; source unchanged. |

Vector SHALL support read-only observation and explicit cloning. Clone SHALL construct an independent live prefix under the destination resource, preserve the source, and retire an uncommitted partial destination on its continuing failure path.

Unchanged relocation SHALL require nonthrowing movement or a copy path preserving old elements until commit. Resource Err SHALL precede element mutation. A failed copy preparation SHALL retire the replacement prefix and preserve the original buffer and size. Basic relocation SHALL retain valid source lifetimes, original buffer, and size until commit, while permitting moved-from values after a throwing move.

Replacement commitment SHALL install the fully prepared buffer, size, and capacity. Retirement SHALL then destroy old generations in reverse and release their extent on continuing paths. A retirement failure SHALL retain the committed Vector; an aggregate profile SHALL complete retirement and propagate. A wholly nonthrowing operation SHALL require nonthrowing retirement effects. Resource Err SHALL belong to the precommit admission/preparation phases.

Push/emplacement SHALL construct the payload or owned staging while any aliased input generation remains live. Growth SHALL construct the appended payload in its final replacement slot before relocating the prefix. A failed payload construction SHALL preserve the prior buffer and size. Subsequent unchanged preparation SHALL use nonthrowing movement or preserving copy. An expressly consumed expiring element alias may remain moved-from after later failure; unaffected generations, buffer ownership, and size SHALL retain the unchanged guarantee. A throwing relocation with only a basic guarantee SHALL select the basic overload.

Insert/erase SHALL require their selected move-construction and assignment operations statically. Resource admission and bounds errors SHALL precede commitment. A later element exception SHALL preserve a valid live prefix and exclusive buffer under the basic guarantee; insertion size SHALL be at most old size plus one, and erasure size at most old size. Each container SHALL serialize structural transitions, including callbacks into its elements.

Reallocation SHALL invalidate every element view. An append retaining storage SHALL preserve preexisting generations. Insertion/erasure SHALL invalidate affected moved, replaced, or ended generations at and after their position. Pop SHALL consume its last obligation before a permitted destruction failure propagates. Clear SHALL retire remaining elements in reverse, reach size zero, and then propagate collected failures under aggregation; its buffer SHALL remain allocated. Shrink SHALL use reserve's preparation/retirement rules, select capacity between its requested minimum and old capacity, and invalidate views when storage changes. An invalid shrink request SHALL report Bounds. Spare capacity SHALL remain inactive storage; its capacity and metadata charges SHALL last until actual release.

## 7. Associative containers

The canonical associative families SHALL be Map<K,V,Order>, Set<K,Order>, HashMap<K,V,KeyPolicy>, and HashSet<K,KeyPolicy>. Their explicit or type-canonical policy SHALL provide less(const<K>&,const<K>&)->bool, or equal(const<K>&,const<K>&)->bool and hash(const<K>&)->usize. Order SHALL establish a strict weak or total order; equality SHALL be an equivalence relation and equivalent keys SHALL have equal hashes. A floating-key policy SHALL explicitly select its finite, representation, or canonical-NaN/zero treatment. Providers SHALL publish hash seeding, collision handling, and iteration order. A selected deterministic policy SHALL identify its algorithm/seed and repeatable input domain.

Construction SHALL take (ResourceRef resource,Policy policy) and establish an empty container with zero container-owned allocation. Stored policy installation/movement/destruction SHALL be nonallocating and nonthrowing. A policy may borrow explicit longer-lived state. Read-only policy receivers SHALL invoke callbacks while indexed keys, their ordering/equivalence, and the container's structural transition remain stable. Key changes SHALL use removal and reinsertion under the selected policy.

All families SHALL expose size(), empty(), resource(), clear(), and try_clone(ResourceRef). Clone SHALL copy every stored key/value and policy. Whole-handle move SHALL empty the source and preserve its policy's valid moved-from state. Operations requiring a functioning policy SHALL require that source state to satisfy it; destruction, empty/size observation, and fresh-handle assignment SHALL remain available. Move assignment SHALL retire the destination before transfer and preserve the source on propagating retirement failure. Mutable/read-only Map find(const<K>&) SHALL return Option<Ref<V>> / Option<Ref<const<V>>>; Set find SHALL return Option<Ref<const<K>>>. contains SHALL return bool. Lookup SHALL invoke the selected policy callbacks with zero container-owned allocation.

`try_insert(const<K>&,const<V>&)` and `try_insert(K&&,V&&)` SHALL return Result<bool,ContainerError>; set overloads SHALL omit V. True SHALL mean one committed new entry. False SHALL preserve an existing equivalent entry and all expiring arguments. Static constraints SHALL include the required copy/move operations. Search and admission SHALL precede argument consumption. Ordinary Err SHALL preserve the index and arguments. A later constructor exception SHALL preserve a valid index and retire uncommitted entry storage; explicitly consumed arguments SHALL retain their own effects.

`try_erase(const<K>&) -> Result<bool,ContainerError>` SHALL report whether an entry existed. It SHALL perform policy callbacks, commit removal with zero container-owned allocation, then retire key/value. Retirement failure SHALL preserve that removal. Clear SHALL retire entries in reverse successful insertion-commit order, mapped values before keys, under the active lifetime profile. Clone SHALL preserve logical entry content using its selected provider layout.

`for_each(callable)` SHALL visit each entry once in the provider's iteration order. Maps SHALL pass a read-only key and the appropriately qualified value; sets SHALL pass a read-only key. Synchronous callbacks SHALL borrow their callable, permit mapped-value changes, and retain a stable structural traversal. A language exception SHALL use the common propagation path. Mutation SHALL invalidate all entry views unless the provider declares a narrower set. Serialized order or stable hashing SHALL use an explicitly selected deterministic policy.

## 8. UTF-8 text

### 8.1 Views and iteration

`StringView()` SHALL be empty. Literal construction SHALL retain the checked UTF-8 content and embedded zeros, with the final literal terminator outside its extent. `try_from_bytes(Span<const<byte>>) -> Result<StringView,TextError>` SHALL validate the complete extent before publishing its borrowed view, using zero allocation. External mutation SHALL preserve the borrowed UTF-8 and storage invariants.

`bytes() -> Span<const<byte>>`, byte_size(), and empty() SHALL observe the content. byte_slice(offset,count) SHALL validate byte bounds through the memory value outlet. try_slice(offset,count) SHALL additionally validate both scalar boundaries and return Result<StringView,TextError>. All offsets/counts SHALL count bytes. Scalar access SHALL use the scalar iterator.

`scalars() -> ScalarIterator` SHALL start a copyable borrowed cursor at byte offset zero. next() SHALL return None at the end or the next Scalar and advance its encoded width. Scalar SHALL contain char value, usize byte_offset, and usize byte_width relative to the original view. Iteration SHALL preserve original UTF-8 content with zero allocation. equals(StringView) SHALL compare exact content bytes, including embedded zero. Unicode transformation and grapheme operations SHALL use their named extended interfaces.

`ZStringView::try_from_bytes(Span<const<byte>> terminated_bytes) -> Result<ZStringView,TextError>` SHALL require one final accessible zero, a preceding zero-free UTF-8 sequence, and its declared storage lifetime. An empty extent SHALL report MissingTerminator. This factory SHALL establish ZStringView. data() SHALL return its const<byte>* borrow, byte_size() the extent before the terminator, and view() the corresponding StringView.

### 8.2 Owned String

`String(ResourceRef resource)` SHALL establish an empty move-only owner with zero allocated content capacity. Whole-handle movement SHALL transfer buffer/resource obligations, preserve content locations, and leave an empty source with a usable resource contract. resource(), byte_size(), byte_capacity(), empty(), view(), and bytes() SHALL observe it; views SHALL expose read-only content. Capacity SHALL count allocated content-byte positions.

| Mutation | Result | Meaning |
| --- | --- | --- |
| `try_reserve(usize bytes)` | `Result<void,TextError>` | Ensures at least the requested byte capacity. |
| `try_append(StringView text)` | same | Appends valid UTF-8 content. |
| `try_insert(usize byte_offset, StringView text)` | same | Requires a scalar boundary at the insertion position. |
| `try_erase(usize byte_offset, usize byte_count)` | same | Requires scalar boundaries at both endpoints. |
| `try_append_scalar(char value)` | same | Encodes exactly one valid scalar. |
| `try_clone(ResourceRef resource)` | `Result<String,TextError>` | Deep copy under the supplied resource. |
| `try_zview()` | `Result<ZStringView,TextError>` | Rejects embedded zero and ensures accessible trailing zero storage. |
| `clear()` | `void` | Sets byte size zero, retaining allocated capacity. |

String byte-storage mutations SHALL provide the unchanged guarantee on ordinary Err. Exact extent, encoding/boundary validation, and allocation admission SHALL precede commitment. Aliased input SHALL be copied or staged while its source remains valid. Staging SHALL use the String's resource and count with old and replacement storage. Byte transport SHALL preserve the specified text invariant.

try_zview SHALL establish accessible final-zero storage, admitting an additional byte when required while preserving content size. The view SHALL borrow the String and remain valid through the stated content/terminator interval. Reallocation SHALL invalidate all prior views. With retained storage, insert/erase SHALL invalidate affected suffixes and clear SHALL invalidate content views; append SHALL preserve prior content bytes and end any previous final-terminator designation. Successful mutation SHALL preserve UTF-8. Destruction SHALL release the buffer through its selected resource.

## 9. Source examples

These declarations use explicit imports and the uniform initialization syntax. They require the named modules' enabled capabilities.

```cpn
import std;
import std.mem;
import std.collections;
import std.text;

bool append_sample(std::collections::Vector<i32>& values, i32 sample) {
    auto result(values.try_push(sample));
    return result.has_value();
}

usize count_bytes(std::text::StringView text) {
    return text.byte_size();
}

void inspect_array() {
    i32[3] samples(10, 20, 30);
    std::mem::Span<i32> view(samples);
    auto selected(view.try_at(1));
    if (selected.has_value()) {
        selected.value().get() = 21;
    }
}

bool use_owned(std::mem::ResourceRef resource) {
    auto created(std::mem::try_make_owned<i32>(resource, 42));
    if (created.has_error()) {
        return false;
    }
    std::mem::Owned<i32> owner(std::move(created.value()));
    i32 observed(owner.value());
    return observed == 42;
}
```

The last example SHALL leave the Result Ok with an empty moved-from Owned and transfer the object obligation to the local owner. That owner SHALL perform the selected scope destruction and storage release. A raw Allocation variant SHALL use explicit lifetime ending and try_release.

