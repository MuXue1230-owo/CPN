<a id="chapter-32-numeric-resource-interfaces"></a>

# CPN26 Numeric Resource Interfaces Specification

## 1. Scope and identities

Numeric resource operations SHALL apply the [common library model](14_standard_library.md#chapter-14-standard-library), [core operational model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance), and existing BigInt value contracts. This chapter specifies quota geometry, plan binding, temporary epochs, and persistent ownership transfer.

New resource names SHALL belong to std::numeric. BigInt and NumericResult SHALL retain their canonical numeric identities; ResourceRef, AllocatorRef, ResourceError, and Span SHALL use std::mem identities, and Option/Result their std identities. Policy copying SHALL preserve its borrowing terms and selected resource domain. These explicitly selected quota and temporary operations SHALL retain their defined outcomes in Native and observed execution alike.

## 2. Geometry and quota policies

`AllocationShape` SHALL contain usize bytes and usize alignment, with positive provider-supported alignment. GeometryIdentity SHALL be an opaque equality-comparable identity of one versioned reservation/charge contract. A provider factory or exported descriptor SHALL supply nonempty GeometryRef as an immutable copyable borrow of that contract.

| GeometryRef operation | Contract |
| --- | --- |
| `identity() -> GeometryIdentity` | Observe the complete versioned identity. |
| `allocator() -> AllocatorRef` | Borrow the allocator contract for which this geometry is valid. |
| `supports(AllocationShape shape) -> bool` | Whether this size/alignment belongs to the geometry. |
| `charge(AllocationShape shape) -> NumericResult<usize>` | Exact retained charge, including alignment rounding and required allocation metadata. |
| `reservation_charge(usize capacity) -> NumericResult<usize>` | Exact backing and control charge for a reservation of that capacity. |
| `guarantees(usize capacity,Span<const<AllocationShape>> simultaneous) -> bool` | Whether the complete simultaneous request multiset is within the backed guarantee. |

Geometry queries SHALL use zero allocation and leave FP status unchanged. Boolean queries SHALL return false for invalid/unsupported shapes; Result queries SHALL report InvalidOperation for invalid shape/geometry and ResourceLimit for an unrepresentable charge. The guarantee predicate SHALL be order-independent and account for fragmentation, size classes, alignment, and metadata, with the simultaneous charge sum at most capacity. A successful reservation SHALL back every admitted allocation/release sequence satisfying that predicate.

`SoftQuota(usize limit)` SHALL store an immutable nonreserving limit and expose limit_bytes(). A copied policy SHALL copy that limit. Persistent use SHALL bound each selected BigInt's total retained charge, including replacement preparation; temporary use SHALL bound one TempScope, including its control and live values. Zero SHALL admit total charge zero. Shared aggregate limits SHALL use the selected ResourceRef domain.

`QuotaPolicy` SHALL expose DomainOnly(), Soft(SoftQuota), and Reserved(ReservedQuotaRef). DomainOnly SHALL retain inherited limits. Reserved SHALL share the selected pool and its single occupied-capacity account. Each case SHALL return the stated admission failure through its selected resource contract.

## 3. Plans and their lifetime

`PersistentResources` and `TemporaryResources` SHALL be immutable records constructed from (ResourceRef domain,QuotaPolicy quota), exposing those read-only fields. A Reserved choice SHALL designate a live pool in that exact domain.

`ResourcePlan(PersistentResources persistent,TemporaryResources temporary)` SHALL expose those two read-only fields. Each SHALL retain its distinct accounting role. Explicit references to one reserved pool may share that pool between the roles while preserving its single capacity account.

`default_resource_plan() -> ResourcePlan` SHALL expose the plan bound by the containing definition's resolved numerical contract, including supplying owners and lifetime obligations. Missing required binding SHALL use the central capability diagnostic. Explicit local policies SHALL retain inherited hard limits.

Persistent creation SHALL select its destination plan; assignment SHALL preserve that plan. Copying SHALL use independent destination storage and its selected policy. Ordinary scratch SHALL use the temporary policy and full-expression lifetime unless an explicit scope is supplied. A ResourcePlan SHALL describe those selections; reservation and allocation SHALL occur in their named admission operations.

## 4. ReservedQuota ownership

`QuotaState` SHALL expose Open/Closed. ReservedQuota SHALL own backed capacity and stable charged control state. Default construction SHALL select Closed with an empty record. Move construction SHALL transfer the record, preserve derived-reference identity, and empty the source. Assignment SHALL require Closed destination, retire its old record, and transfer; self-move SHALL preserve state. A failed checked destination precondition SHALL dispatch to ContractTrap before either owner changes.

| Operation | Result and meaning |
| --- | --- |
| `try_reserve_quota(ResourceRef domain,usize capacity,GeometryRef geometry)` | NumericResult<ReservedQuota>. |
| `reserve_quota(ResourceRef domain,usize capacity,GeometryRef geometry)` | ReservedQuota or Numeric Trap, with the same admission. |
| `state() -> QuotaState` | Nonallocating observation. |
| `capacity_bytes() -> usize` | Reserved capacity while Open, otherwise zero. |
| `occupied_bytes() -> usize` | Charge currently occupied by allocations within the reservation. |
| `charge_bytes() -> usize` | Actual retained domain charge, including reserved free backing and control storage. |
| `resource() -> Option<ResourceRef>` | Domain while a control record remains, otherwise None. |
| `geometry() -> Option<GeometryRef>` | Geometry while a record remains, otherwise None. |
| `borrow() -> ReservedQuotaRef` | Nonowning pool reference; requires Open. |
| `try_close() -> Result<void,ResourceError>` | Outstanding allocations give Outstanding unchanged; otherwise release backing and become Closed. Already Closed succeeds inertly. |

`ReservedQuotaRef` SHALL be a nonempty copyable borrow exposing state(), capacity_bytes(), occupied_bytes(), resource()->ResourceRef, and geometry()->GeometryRef. It SHALL observe Closed while its record remains live; later use SHALL require that record's valid borrowing interval. Numerical use of Closed SHALL report InvalidOperation before admission.

Reservation admission SHALL establish geometry compatibility, ancestor-budget admission, and actual backing as one transaction under the common model. ResourceLimit and AllocationFailure SHALL retain their distinct identities. An admitted backed shape SHALL receive its advertised allocation guarantee after satisfying independent numerical constraints.

Pool return SHALL lower occupied capacity and retain reserved backing. Close SHALL release backing once; retained control SHALL remain charged through owner retirement. Destruction SHALL require discharged allocations, release remaining backing/control, or dispatch to ContractTrap while unresolved obligations remain.

## 5. Temporary scope and epoch ownership

`TempState` SHALL expose Open/Closed. TempEpoch SHALL identify one scope generation. TempScope(TemporaryResources) SHALL admit its stable epoch/control state and select Open; its value outlet SHALL use NumericTrap on resource failure. TempScope() SHALL select Closed with an empty record. state() SHALL return TempState; epoch() and resources() SHALL return Option<TempEpoch> and Option<TemporaryResources>, selecting None exactly for an empty record. A retained closed record SHALL expose its ended epoch/resources.

A scope SHALL be move-only. Move construction SHALL transfer control, preserve handle epoch identity, and empty the source. Assignment SHALL require Closed destination and retire its old record before transfer; self-move SHALL preserve state. Quiescent close SHALL end the epoch, retire its remaining temporary payloads, and select Closed; repeated close SHALL preserve Closed. Destruction SHALL close and retire the owner's record obligation. Successful transfer SHALL remove the transferred allocation from that cleanup set.

`TempBigInt` SHALL be established by a temporary-result operation as a move-only value/epoch owner. alive() SHALL observe the epoch's open state; epoch() SHALL return its identity. is_zero() SHALL require alive and otherwise dispatch to ContractTrap. A numerical read SHALL validate the selected epoch before accessing its value.

Outstanding handles SHALL retain explicitly charged epoch/control metadata through their final retirement. Scope closure SHALL end values and retire payloads; later handle destruction SHALL retire its metadata obligation. Once the scope owner and all handles have retired those obligations, the metadata SHALL be released. Its resource owner and charge SHALL remain valid through that release.

TempBigInt move SHALL validate source liveness before destination retirement. An expired source SHALL use ContractTrap. Successful movement SHALL transfer the value allocation and leave source zero in its live epoch. Assignment SHALL retire the old destination obligation and adopt the source epoch/value; self-move SHALL preserve state. An expired destination may retire its metadata before assignment. Live-handle destruction SHALL release its remaining allocation and unregister its scope-cleanup obligation. Value duplication SHALL use an explicit persistent Commit or numeric copy operation.

Scope/handle mutation SHALL use declared or external synchronization. Epoch identities SHALL remain distinct while surviving handles can observe their generations. Budget admission SHALL use the common atomic ancestry transaction independently of scope access synchronization.

## 6. Temporary arithmetic catalogue

A and B SHALL independently be BigInt or TempBigInt, borrowed read-only. Fixed/platform operands SHALL first use their explicit family-unification operation.

| Signature family | Result |
| --- | --- |
| `try_temp_add/sub/mul/div/rem<A,B>(TempScope& scope,const<A>& a,const<B>& b)` | NumericResult<TempBigInt>. |
| `temp_add/sub/mul/div/rem<A,B>(TempScope& scope,const<A>& a,const<B>& b)` | TempBigInt or Numeric Trap. |
| The same families without the scope parameter | The same result using the default plan's temporary resources and the enclosing full-expression scope. |

Each slash-separated row SHALL denote the five named declarations. Division/remainder SHALL retain their integer quotient/remainder semantics. After expression evaluation and liveness/policy admission, zero-divisor rejection SHALL precede allocation. Ended scope/operand SHALL report InvalidOperation; exhausted allowance ResourceLimit; failed permitted backing acquisition AllocationFailure.

Success SHALL publish one owning result in the selected epoch. Failure SHALL preserve operands, prior registered temporaries, and committed charges while retiring its uncommitted preparation. The value form SHALL select NumericTrap after the corresponding ordinary Result failure path. Arithmetic status SHALL follow the integer operation; resource administration SHALL contribute an empty FP event set.

The implicit scope SHALL close at the full-expression boundary. A stored handle SHALL then designate its ended epoch, and subsequent Result operations SHALL report expiration. An unintended escape SHALL use the central diagnostic. An explicit scope SHALL keep its epoch open for its own admitted lifetime.

## 7. Commit and exclusive Transfer

| Operation | Result |
| --- | --- |
| `try_commit(const<TempBigInt>& temp,ResourcePlan destination)` | NumericResult<BigInt>. |
| `commit(const<TempBigInt>& temp,ResourcePlan destination)` | BigInt or Numeric Trap. |
| `try_transfer(TempBigInt& temp,ResourcePlan destination)` | NumericResult<BigInt>. |
| `transfer(TempBigInt& temp,ResourcePlan destination)` | BigInt or Numeric Trap. |
| Each operation without destination | Same using default_resource_plan(). |

The resulting BigInt SHALL retain the complete destination ResourcePlan. Its persistent field SHALL select result ownership, and its temporary field SHALL select preparation scratch and later temporary computation.

Commit SHALL prepare independent persistent storage and preserve the temporary value, allocation, and epoch. Both live source and prepared result SHALL count during preparation. Zero may use its provider's empty payload representation; a nonzero result SHALL own independent value storage.

Transfer SHALL require exclusive detachable ownership, compatible release/allocator contracts, destination admission, and preserved source reservation backing. It SHALL transfer the existing payload. An allocation-free zero SHALL transfer as zero. Structural incompatibility SHALL report TransferUnavailable; limits ResourceLimit; preparatory backing failure AllocationFailure; expired source InvalidOperation.

Transfer preparation SHALL secure any replacement backing required by source reservations before commitment. Shared ancestors SHALL charge the transferred physical block once; source-only and destination-only accounts SHALL commit their deltas together. Additional prepared backing SHALL contribute its real peak charge. The ownership transaction SHALL retain one current owner and every promised reservation guarantee throughout.

Transfer success SHALL remove the allocation from scope cleanup, establish persistent release obligations, and leave temp zero in its live epoch. Failure SHALL preserve source, destination policy, backing guarantees, and accounting. Commit/Transfer success SHALL report false loss/clamp/wrap/payload-change flags and an empty FP flag set.

Callbacks, failure routing, strong replacement preparation, and profile-specific retirement SHALL use the common library model. This chapter's concrete quota, epoch, and transfer outcomes SHALL be the selected functional state for those operations.
