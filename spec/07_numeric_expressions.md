<a id="chapter-07-numeric-expressions"></a>

# CXXN Numeric Expressions and Resources Specification

## 1. Integer expression binding

The compiler shall bind integer domains and arithmetic common types using the canonical table in [Chapter 02](02_integer_bigint.md#chapter-02-integer-bigint), then test the derived type's availability. The enabled-width set affects materialization, not the derived type. For example, i64 with u64 derives i128 even when i256 is enabled instead; fixed-integer comparisons remain mathematical and require no such widening.

An operation shall retain that selected operand/result type and apply its resolved ordinary policy. An explicit destination on a named arithmetic interface selects that operation's projection type. A surrounding assignment uses the already computed typed value. Narrow integer operands receive exactly the type derived by Chapter 02.

An implicit integer conversion requires whole-domain exact preservation or an exact source value established by language constant evaluation. The compiler shall use those language proofs for binding and overload selection. Optional optimizer analysis may optimize an already bound operation without changing its source type or overload identity. Typed-family unification follows the explicit crossing rules.

## 2. Unary operations and compound assignment

Unary `+` preserves its operand type and value. Unary `~` preserves a fixed integer's type and complements exactly its `N` representation bits. BigInt complement uses the established infinite two's-complement model.

Ordinary unary `-` shall apply the selected integer policy to mathematical negation in the operand type. Native delivers its N-bit modulo interpretation. Checked accepts signed minimum only when its mathematical negation fits the destination; same-type signed minimum therefore fails. Checked unsigned negation accepts zero and reports OutOfRange otherwise. `checked_neg` and `try_neg` select that predicate explicitly; `wrapping_neg` and `saturating_neg` select modulo and clamp projection. Diagnostics follow the central numeric applicability table.

`abs(x)` shall preserve the integer type and apply the selected ordinary policy to its mathematical absolute value. Native therefore maps signed minimum to the same minimum bit pattern; Checked rejects that unrepresentable positive result. `checked_abs` and `try_abs` explicitly select Checked. `magnitude(iN)` returns exact absolute value in enabled `uN`; `magnitude(uN)` is identity. BigInt abs/magnitude retain their exact integer and resource contract.

Prefix and postfix increment/decrement require a writable integer lvalue and use same-type addition/subtraction of one under the resolved ordinary integer policy. Prefix yields the updated lvalue; postfix yields the old value as a value of the operand type. For allocating integers, any snapshot required for postfix must be prepared before mutation; a resource failure leaves the operand unchanged.

For `target op= rhs`, evaluation proceeds as follows:

1. Locate the target once and read its old value.
2. Evaluate `rhs` once.
3. Apply the ordinary operator's type-selection and resolved arithmetic policy.
4. Apply the permitted implicit conversion back to the target type.
5. Commit the write-back on success and yield the target lvalue.

A missing implicit write-back conversion is a type error. It is not a request for implicit truncation or an implicit dynamic narrowing check. Operand side effects are not rolled back. In particular, a right-hand expression's independent mutation is not undone merely because the compound write-back fails.

Explicit `checked_add_assign`, `checked_sub_assign`, `checked_mul_assign`, and `checked_div_assign` instead select the target type as the destination. As ordinary function calls, they evaluate their arguments from left to right; the target argument locates the mutable target, and the function reads its then-current value after argument evaluation. They compute the exact mathematical operation on their admitted integer operands, check that destination, and commit only on success. Their `try_*_assign` counterparts return `NumericResult<void>`; success contains status and no additional value snapshot. The value/Trap forms return `void`. They do not require an otherwise unavailable arithmetic common type because the destination has been selected explicitly. Typed-family restrictions still apply. The compound operator's earlier old-value read is not implicitly transferred to these function calls.

For example, with a runtime `i16 y`, `i8 x; x += y;` requires an implicit write-back proof and is otherwise ill-typed. `try_add_assign(x, y)` explicitly requests checked write-back to `i8`; failure leaves `x` unchanged.

## 3. Numeric tokens, propagation, and materialization

### 3.1 Lexical forms

Integer tokens use decimal digits or explicit radix prefixes:

```text
decimal:  0, 42, 012
binary:   0b101010
octal:    0o52
hex:      0x2A
```

Prefixes are case-insensitive. Leading zero alone does not select octal: `012` is decimal twelve. A single underscore may separate two digits of the same digit sequence, as in `1_000` or `0xDE_AD`. Separators cannot lead, trail, repeat, or immediately follow a radix prefix. An invalid digit for the selected radix is an error. Integer tokens have no implicit unsigned, long, or host-width suffix. Explicit type construction supplies a type.

The sign is a unary operator, not part of an integer token. Exact literal processing nevertheless precedes fixed-width materialization, so `-2147483648` can bind directly to `i32` without first materializing positive `2147483648` as `i32`.

Decimal real tokens have either a decimal point with digits on both sides, an exponent, or both: `0.5`, `1e3`, `1.25e-4`. A hexadecimal real token has a `0x` prefix and mandatory binary exponent introduced by `p`, for example `0x1p0` or `0x1.8p+2`. Its optional point also has digits on both sides. Exponent signs are optional and exponent digits are decimal. The same separator restrictions apply independently to each digit sequence. NaN and infinity are representation values, not numeric-token spellings.

Real tokens denote exact rational mathematical values before materialization. A negative real zero retains its requested sign. No token is parsed through the compiler host's floating format.

Neither integer nor real tokens carry legacy type suffixes. `Type name(exact_literal);` or an explicit numeric construction/cast supplies the destination; additional suffix families are not required.

### 3.2 Untyped integer expressions

An integer token initially has an abstract compile-time integer value. Parentheses, unary `+`/`-`, and literal-only `+`, `-`, `*`, `/`, `%` preserve that abstract category. Division truncates toward zero; `%` uses the corresponding dividend-signed remainder. The compiler does not insert fixed-width overflow into this abstract calculation.

An abstract integer expression materializes when a concrete numeric type is required: an explicit construction, binding to a typed arithmetic operand, a declared numeric destination, a parameter type, or default value inference. Default unconstrained materialization uses the resolved default integer type, as selected by Chapter 08. Failure to fit that type is `ERROR`; there is no automatic unsigned, wider-integer, or BigInt fallback.

For an ordinary arithmetic operation with one typed integer operand and one abstract integer operand, the abstract value binds to that operand's type and must fit it. A surrounding destination cannot change this binding. Both operands then follow the ordinary typed rules. An explicit type on the other operand can instead request a different common type.

Comparison may compare an abstract integer directly with an admitted typed integer's mathematical value without materializing the constant into that type. For example, `u8(255) < 300` is true. An all-abstract comparison returns a Boolean without materializing its operands as runtime integers.

Width-dependent operations—`~`, `&`, `|`, `^`, and shifts—materialize their participating integer values before operating. The type comes from an explicit width-bearing operation, an admitted typed operand, or the direct numeric destination when all relevant operands remain untyped; otherwise it is the default integer type. Shift counts retain their mathematical input value; the selected operation policy determines count validation or Native mapping.

Named numeric conversion functions consume an abstract literal's exact value directly. They do not first materialize it in the destination. Therefore `wrapping_cast<u8>(-1)` yields `255`; `try_checked_cast<u8>(-1)` returns `Err(OutOfRange)`; ordinary direct literal binding `u8(-1)` is a materialization error.

### 3.3 Floating and exact-family boundaries

An abstract numeric literal directly bound to a fixed floating format rounds to that format, using the resolved compile-time literal-rounding policy, as selected by Chapter 08. An unconstrained real token shall use the floating literal default in Chapter 08. Literal formation produces a constant representation; it does not generate an execution-time sticky flag on every use. A finite literal is rejected for target-format Overflow under its selected literal rounding policy. Classification uses the specified precision-rounded unbounded-exponent result; it does not reject every exact source magnitude slightly above `MAX_FINITE` when that source rounds to the finite maximum without Overflow. Inexact or subnormal formation is permitted under the declared policy and applicable diagnostics. Compile-time formation events do not enter runtime sticky status. Named casts retain their own specified predicates and status delivery; Exact still requires exact finite representability.

Floating operators are typed operations. With only untyped operands, their operands first bind to the directly expected floating format, or otherwise to the default floating format; each token is rounded directly to that format. The operation then performs its ordinary floating calculation and status effects. A floating `0.0 / 0.0` remains a floating operation: an observed invocation records Invalid, while an ordinary Native invocation uses its provider result with unobserved events. Mandatory constant evaluation uses its separate target-semantic rule.

An already typed operand or subexpression remains a rounding boundary. `f64(0.1)` converted to Rational uses that encoded `f64`; direct construction of Rational from token `0.1` uses the exact rational token value. Exact-family arithmetic requires the established explicit operand binding; an existing typed floating operation shall retain its selected floating contract across destination binding.

Explicit casts use their own rounding or exactness predicates and report their own status. In particular, `try_exact_cast<f32>(0.1)` probes the exact token value; it does not probe an already rounded `f32` constant.

### 3.4 Named special-value construction

`infinity<T>()` constructs positive infinity; `infinity<T>(Negative)` constructs negative infinity. `quiet_nan<T>(payload, sign)` and `signaling_nan<T>(payload, sign)` construct the requested class, payload, and sign, with sign defaulting to `Positive`. `T` must provide that special-value capability. Payloads are exact nonnegative integers satisfying the selected format/provider's payload constraints.

These are representation operations. They do not round, perform hidden arithmetic, quiet a requested signaling NaN, or generate Invalid merely by constructing it. A value transfer that cannot preserve the requested representation does not implement this interface; an unsupported required capability is a compile-time error.

An inadmissible runtime payload produces the constructor's numeric `OutOfRange` failure, not an IEEE Invalid event. Value constructors use Numeric Trap; corresponding `try_quiet_nan<T>` and `try_signaling_nan<T>` forms return Result. Payload admission shall use the provider encoding limits, including its available signaling payloads. Arithmetic NaN conversion retains its separate prescribed payload mapping.

## 4. Bit-pattern reinterpretation and shifts

`reinterpret_bits<U>(x, extension)` is a dedicated integer representation operation. The source has known width `N`, the destination has enabled width `M`, and `extension` is `Source`, `Zero`, or `Sign`; the default is `Source`.

Let `b` be the source's unsigned `N`-bit encoding. If `M <= N`, retain `b mod 2^M`. If `M > N`:

- `Zero` inserts zero high bits.
- `Sign` replicates the source encoding's most-significant bit, regardless of the source type's signedness.
- `Source` uses `Sign` for a signed source and `Zero` for an unsigned source.

After resizing, interpret the resulting `M` bits as `U`. Extension selection has no effect when no extension occurs. The operation does not perform mathematical-value range checking, generate integer overflow, or expose FP flags. Intentional discarded representation bits remain subject to applicable configured diagnostics.

This operation is independent of byte order and does not alias an unrelated object's storage. Fixed/platform crossings are explicit when selected through this operation. BigInt must first enter an explicitly sized finite representation; it has no implicit source bit width.

For fixed shifts, the compiler shall apply Chapter 02's ordinary policy and static-domain rule. Valid-count right shift is arithmetic for signed operands and logical for unsigned operands. Valid-count left shift projects `x*2^k` under the selected policy, including a negative signed x. An ordinary Native shift uses its declared target result/fault mapping for a variable invalid count. Explicit checked/try and logical-shift interfaces validate the count and return their prescribed InvalidShift outlet.

`logical_shr` shall return same-width uN from the source's unsigned encoding, requiring that type to be enabled. BigInt arithmetic shifts use nonnegative counts without a fixed-width upper bound: right shift beyond the significant bits delivers zero for nonnegative values and -1 for negative values. Left shift retains its explicit resource contract. A BigInt logical shift first establishes a finite representation, for example `logical_shr(wrapping_cast<uN>(big), k)`.

## 5. Scalar numeric interfaces and errors

The following are standard numeric library interfaces. Their names do not introduce new statement grammar. An optional resource or FP policy parameter selects only the contract belonging to that interface.

| Interface | Contract |
| --- | --- |
| Integer `checked_add/sub/mul/div/rem/neg/abs/shl/shr`, and `logical_shr` | Checked mathematical operation and selected result type; value or Numeric Trap. Their predicates remain Checked in every preset; Section 2 defines unsigned negation. |
| Integer `try_add/sub/mul/div/rem/neg/abs/shl/shr` and `try_logical_shr` | The corresponding `NumericResult<T>`; `Err` has no readable value. |
| `euclidean_mod`, `try_euclidean_mod` | Nonnegative remainder in `[0, abs(divisor))`; zero divisor fails. Computing `abs(divisor)` mathematically does not require materializing signed minimum's unrepresentable magnitude in its signed type. |
| `wrapping_add/sub/mul/neg/shl/div/rem` and their `try_` forms | Exact mathematical result followed by destination modulo interpretation; invalid shift counts and zero divisors still fail. |
| `saturating_add/sub/mul/neg/shl/div/rem` and their `try_` forms | Exact mathematical result clamped to destination bounds; invalid shift counts and zero divisors still fail. |
| `try_checked_cast<T>`, `checked_cast<T>` | The fixed Checked conversion acceptance predicate; optional rounding where the destination conversion defines it. |
| `try_exact_cast<T>`, `exact_cast<T>` | Finite representability without approximation or speculative IEEE flags. |
| `try_wrapping_cast<T>`, `try_truncating_cast<T>`, `try_saturating_cast<T>` and their value forms | The established conversion mappings and status. There is no unspecified wrapping-floating conversion. |
| Floating `report_add/sub/mul/div` | Explicit observed floating operation with its default result and local status under Chapter 04. |
| Floating `try_add/sub/mul/div` | Result classified by the selected FP error mask and optional finite-result predicate. |
| Floating `checked_add/sub/mul/div` | Value form of that explicit floating Result policy; Numeric Trap exactly when its corresponding Result is `Err`. Ordinary floating operators retain their separately selected environment/trap behavior. |
| `try_rescale<T>`, `rescale<T>`; `try_exact_rescale<T>`, `exact_rescale<T>` | Fixed-point destination projection or finite exact representability, respectively; each explicit rescale remains a rounding boundary. |
| `try_rational(p,q,resources)`, `rational(p,q,resources)` | Canonical exact Rational construction; zero denominator fails before allocation is committed. |
| BigDecimal `try_exact_div`, `exact_div`; `try_rounded_div`, `rounded_div` | Exact finite expansion or division under an explicit finite decimal context; nonterminating exact division fails rather than inventing precision. |

The integer shorthand entries denote individual names such as `checked_add` and `try_add`, not a slash-containing identifier. An explicitly selected destination type parameter on integer arithmetic selects that destination for exact mathematical projection; absent such a parameter, ordinary operand/common-type rules apply. Ordinary operators never infer that explicit destination from an outer assignment.

Within an explicitly validating interface, domain validation shall precede destination-range classification: zero divisor gives `ZeroDivisor`, invalid shift gives `InvalidShift`, invalid bit range gives `InvalidBitRange`, and an unrepresentable checked integer result gives `OutOfRange`. These are numeric error codes, not IEEE flags. A wrapping or saturating policy affects representable-range projection, not unrelated domain validation. For example, wrapping_div(i8.MIN,-1) yields i8.MIN, whereas saturating_div yields i8.MAX; either named interface classifies a zero divisor as ZeroDivisor. Ordinary Native division uses Chapter 02's separate provider map for exceptional inputs.

Numeric expressions and calls shall use the core left-to-right evaluation model. The interface shall apply its own validation after source/policy argument evaluation. Those earlier effects and independently invoked callbacks retain their own failure outlets; the Result replaces only the numeric invocation's stated outlet.

FP report/Result interfaces shall select the observed numerical transition in [Chapter 04](04_numeric_integration.md#chapter-04-numeric-integration), including their bound projection, NaN, and local-status rules. Adding Inexact to a floating Result mask can reject an inexact arithmetic operation. In contrast, `exact_cast<f64>(a + b)` tests the already computed sum; it does not prove that `a + b` was exact. For observed f32 addition with a=16777216 and b=1, the rounded sum is 16777216 and its f64 conversion is exact despite the addition's Inexact event. Ordinary Native addition carries only its selected value contract and unobserved events.

## 6. Bit extraction and insertion

Bit indices start at the least-significant representation bit. For source width `N`, start `s`, and requested width `w`, validate in this order:

```text
s >= 0
w > 0
s <= N
w <= N - s
```

The implementation shall evaluate N-s after admitting s, so the range predicate uses an exactly representable difference. A full-width range is valid. Zero width is invalid even at the end of storage.

`extract_bits<s,w>(x)` returns exact enabled `uW`, with `W = w`. Dynamic `extract_bits<U>(x,s,w)` requires an unsigned fixed destination `U` with width `M` and additionally requires `w <= M`; it zero-extends the extracted bits. The capacity rule concerns the requested width, not whether a particular value's leading bits happen to be zero.

`insert_bits(x,s,w,value)` returns a new value of the source type, preserving every bit outside the selected range. It does not mutate `x`. Normal insertion requires the mathematical value to satisfy `0 <= value < 2^w`; negative signed values fail even if their low bits would fit. Source-value width need not equal the explicitly selected write width.

`insert_bits_trunc` explicitly uses `value mod 2^w`, including for negative values. In either form, the updated encoding is interpreted in the original source type. Setting a signed sign bit is a bit operation, not arithmetic overflow.

`insert_bits_assign` and `insert_bits_trunc_assign` are the mutating forms. Their arguments evaluate once from left to right, locating the target before evaluating the remaining arguments. On function entry they capture the target's then-current value, validate, and commit the replacement only on success; they return `void`. Argument side effects are not rolled back. Unlike compound assignment, these ordinary calls do not read the target value before evaluating later arguments.

Ordinary dynamic forms use Numeric Trap on failure. The `checked_`-prefixed forms—including `checked_extract_bits`, `checked_insert_bits`, and the corresponding truncating/assignment forms—return Result. For these bit interfaces, `checked_` denotes the established Result naming convention; numeric arithmetic and cast interfaces use the separate `try_` convention specified in Section 5. Statically invalid ranges are `ERROR` in either delivery form. A dynamic range or destination-capacity failure is `InvalidBitRange`; an insertion value that does not fit is `OutOfRange`. Range validation takes priority over value-fit validation.

## 7. Atomic bit-operation delta

An enabled atomic bit operation shall act on one whole fixed-integer atomic location. `atomic_extract_bits<U>` loads one snapshot and extracts from it. `atomic_insert_bits` and `atomic_insert_bits_trunc` replace the selected range by one whole-location read-modify-write and return the previous whole value. The checked Result variants have those same successful synchronization effects.

The operation shall validate its explicit range, destination capacity, insertion value, and capability before its atomic access. A validation failure completes without a load, store, read-modify-write, or fence for this invocation. Its earlier argument effects remain complete. A retry shall recompute from each newly observed whole value and preserve concurrent changes outside the selected range. Source expressions and user callbacks are evaluated at their ordinary call boundary, not on internal retries.

Memory order is a compile-time policy selecting the load or read-modify-write contract in the [concurrency memory model](13_concurrency_memory_model.md#chapter-13-concurrency-memory-model). Runtime selection dispatches to an admitted instantiation. These explicit synchronization effects remain functional observations under Native Release. The atomic provider shall supply the chosen whole-location operation; any selected software fallback shall publish its locking and support contract through Chapter 08's capability rules.

## 8. BigInt resource accounting

### 8.1 Resource plans and charges

A BigInt resource plan identifies the persistent allocator, budget domain, quota handle, and temporary-storage policy. New destinations use an explicitly selected plan or the resolved project default. Assignment preserves the destination plan. Copying a value does not implicitly copy its source's resource-policy override.

The [numeric resource interfaces](32_numeric_resource_interfaces.md#chapter-32-numeric-resource-interfaces) define the canonical ResourcePlan, quota, reservation-geometry, and temporary-scope types, their constructors and observers, and the exact signatures summarized below.

Resource accounting charges allocated capacity, including provider-declared alignment rounding and required private allocation metadata, rather than the number of significant bits in the current value. Providers declare their charge calculation and reservation geometry. Accounting shall report the declared charge for the resources actually retained; optimization may reduce those resources before charging them.

A Reserved Quota handle owns real backed capacity. Its charge is admitted when the reservation is created, including free reserved capacity. Allocating inside that reservation increases its occupied capacity without charging the same backing to ancestors a second time. Soft Quota is only a consumption bound; each unreserved allocation still requires budget admission and successful allocation.

Sharing one reserved pool among objects requires explicitly sharing that quota handle. Capacity is guaranteed for the pool's declared allocation geometry, not independently promised in full to every participating object. A provider cannot advertise an unbacked allowance counter as a reservation. Unsupported allocation shape/alignment or failure beyond the reserved guarantee remains a reported resource failure.

Every allocation or reservation admission is one logical transaction across the applicable hard-budget ancestry: all bounds admit it, or none of the counters is committed. Failed allocation rolls back its pending admission. Parallel requests cannot independently consume the same remaining allowance.

### 8.2 Peak resources and release

A strong-guarantee replacement charges old storage and separately prepared new storage concurrently until commit releases the old storage. It cannot claim the old storage has been freed while still relying on it to preserve the destination on failure. A provider may update in place only when it preserves the same guarantee and no later resource failure can leave a partial value.

Consequently, a replacement can return `ResourceLimit` even when its final representation alone would fit the budget. Freeing or shrinking a value releases actual retained capacity only when that capacity is returned to its owner. Returning a block to a reserved pool increases its free reserved capacity; it does not release the pool's backing charge. Releasing the reservation releases that backing once its owned allocations are no longer in use.

Allocator release and committed accounting release are nonfailing resource-provider operations. An arbitrary exception from a user callback is outside the NumericResult contract and follows the language exception policy; numeric procedures do not add catch-all handlers.

### 8.3 Copy and move

Copy produces independent value storage under the destination plan. Move assigns a valid zero to the source only after success. Self-move assignment is a no-op, including resource accounting.

Direct storage transfer shall require compatible allocators and resource contracts. Destination admission shall cover the new ownership, and the source pool shall retain or replace the backing required by its reservation guarantee.

Where direct transfer is inadmissible, the implementation prepares the required destination allocation and any reservation-preserving work before commit. If that cannot be completed within the selected policies, the move fails with both values and plans unchanged. Incompatible allocators use the destination allocator and the same Strong Guarantee. A move is a logical ownership transaction, not a promise of inter-thread atomic access to either object.

Cross-domain ownership transfer updates accounting by deltas. Common ancestors charge one physical backing only once; source-only ancestors release its charge and destination-only ancestors acquire it in the same admission/commit transaction. Real extra backing prepared for a reservation remains an additional peak charge. The transaction shall maintain exactly one owner for each live allocation and charge each common ancestor for one physical backing throughout commit.

## 9. Temporary storage, Commit, and Transfer

Ordinary BigInt value results own their persistent storage under their selected destination/resource plan. Internal scratch calculations use the separately controlled temporary area. An implementation may construct a final value directly in its persistent destination when that preserves the selected resource contract; it may not substitute a different allocator/quota plan or leave that result referring to scratch that will expire.

An explicit temporary calculation returns `TempBigInt`, an owning temporary handle associated with a `TempScope`. The default temporary scope ends with the enclosing full expression. An explicitly supplied `TempScope` can extend that lifetime. A temporary handle is movable; duplicating value ownership requires an explicit copy operation. Raw pointers or borrowed access do not acquire storage ownership.

`try_commit(temp, destination_plan)` creates independent persistent BigInt storage under the supplied or resolved ResourcePlan. Its persistent field controls output ownership; its temporary field controls required scratch and the resulting object's later temporary operations. It preserves the temporary value and uses the Strong Guarantee. `commit` is its value/Trap form. Both the still-live temporary and the new allocation count during preparation.

`try_transfer(temp, destination_plan)` explicitly detaches temporary storage and transfers its ownership to a persistent BigInt under that complete ResourcePlan. It requires an owning detachable allocation, allocator compatibility, valid destination admission, and preservation of all reservation guarantees. The transfer operation shall test those ownership-transfer requirements before committing the handoff. Such a policy incompatibility reports `TransferUnavailable`; insufficient quota reports `ResourceLimit`; allocation failure during permitted preparatory work reports `AllocationFailure`. `transfer` is the value/Trap form.

Successful Transfer leaves the temporary handle as valid zero within its still-live scope and removes the transferred allocation from scope cleanup. Failure leaves the temporary, destination, and accounting unchanged. Scope exit releases only allocations still owned by that scope. Commit/Transfer resource preparation must finish before the source scope ends; returning or storing a borrowed temporary does not extend its lifetime.

The public ResourcePlan, quota, temporary-arithmetic, Commit, and Transfer signature table is owned by [Chapter 32](32_numeric_resource_interfaces.md#chapter-32-numeric-resource-interfaces). The algorithms above define their accounting transitions. These explicitly selected resource operations retain their Result/value and ownership contracts in every preset.

## 10. Required boundary behavior

The following examples assume the displayed capabilities and explicitly stated policy; literal examples use an i32 literal default. They distinguish ordinary Native execution from named or selected checked functionality.

| Expression or situation | Required behavior |
| --- | --- |
| `auto x(2147483648 - 1);` | The abstract result is `2147483647`, then materializes as `i32`. |
| `auto x(2147483648);` | Default `i32` materialization error; no unsigned or BigInt fallback. |
| `i8 x(127 + 1 - 1);` | Abstract integer arithmetic yields `127`; initialization succeeds. |
| `i16 x(i8(127) + i8(1));` | Under Checked, i8 addition fails. Under Native, it yields i8(-128), which then converts exactly to i16. |
| Initially `x = 1`, and an RHS call writes `x = 10` then returns `2` | `x += rhs()` stores `3` from its earlier old-value read; `checked_add_assign(x, rhs())` instead reads the then-current target on entry and stores `12`. |
| `u8 mask(~0);` | The width-dependent expression binds to `u8`; result is `255`. |
| `-u8(0)` under Checked | Same-type unsigned zero. `try_neg(u8(1))` returns `Err(OutOfRange)`; the ordinary nonzero negation takes its value/Trap outlet. |
| `f16 x(65505.0);` under nearest-ties-even | Initializes to `65504`; compile-time formation is inexact but does not overflow or update runtime sticky flags. |
| `f16 x(65520.0);` under nearest-ties-even | Materialization error from target-format Overflow; the same exact source under toward-zero rounds to finite `65504` without Overflow. |
| `try_checked_cast<f16>(65505, NearestTiesEven)` | `Ok(65504)` with Inexact and no Overflow; the named cast uses its own predicate. |
| `report_add(f16(65504), f16(1))` under nearest-ties-even | Value `65504` with Inexact and no Overflow; this typed arithmetic updates the specified runtime status. |
| `checked_rem(i8.MIN, i8(-1))` | Same-type zero, independent of quotient overflow. Ordinary Native `%` uses the target contract for that input pair. |
| `logical_shr(i8(-1), 1)` | `u8(127)`. |
| `reinterpret_bits<u16>(i8(-128))` | Source-directed sign extension gives `65408`. |
| `reinterpret_bits<u16>(i8(-128), Zero)` | Zero extension gives `128`. |
| `reinterpret_bits<i16>(u8(255), Sign)` | Signed interpretation of `0xFFFF`, therefore `-1`. |
| Dynamic extraction of nine bits into `u8`, even when all extracted bits are zero | `InvalidBitRange`; requested width exceeds destination capacity. |
| Normal insertion of `-1` into an eight-bit field | `OutOfRange`; the separate truncating insertion writes eight one bits. |
| Insert one into bit seven of `i8(0)` | Updated encoding denotes `i8(-128)`; no arithmetic overflow. |
| Invalid atomic range | No atomic location access or synchronization event from this operation. |
| Two atomic insertions into disjoint ranges | Successful operations preserve each other's bits according to whole-integer linearization order. |
| Replace a 64-unit allocation with a prepared 96-unit allocation under a hard limit of 128 | Fails if both allocations must coexist: peak is 160; the original value is retained. |
| Move requiring withdrawal of backing promised by a source Reserved Quota | Prepare a contract-preserving relocation or fail unchanged; allocator equality alone is insufficient. |
| Transfer the same admitted unreserved allocation between child domains of one hard-budget ancestor | Reassign ownership without charging that common ancestor twice. |

The compiler shall apply Chapter 04's numeric diagnostic cases and Chapter 08's severity policy independently of each selected runtime transition.

