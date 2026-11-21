<a id="chapter-04-numeric-integration"></a>

# CXXN Numeric Integration Specification

## 1. Numerical operation model

This chapter owns numerical conversion, control, status, rounding, NaN, tininess, and error-delivery definitions. Integer domains and canonical common types belong to [Chapter 02](02_integer_bigint.md#chapter-02-integer-bigint); floating encodings and exact-family representations belong to [Chapter 03](03_floating_exact.md#chapter-03-floating-exact). [Chapter 08](08_runtime_configuration.md#chapter-08-runtime-configuration) owns preset/default and severity tables. Evaluation, effects, state changes, and permitted transformations use the [core operational model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance).

The compiler shall resolve an operation's contract from its bound interface and effective configuration. Explicitly named Checked, Exact, report, Result, Wrapping, and Saturating interfaces select their declared operations. Ordinary operators select the configuration's ordinary policy. The implementation shall provide the selected capability or diagnose its absence at the requiring use.

CPN26 shall apply this chapter conditionally to the numerical capabilities selected under the core conformance model. Each operation shall bind its representation, value algorithm, controls, observation, delivery, and resources. A provider shall enumerate the combinations it implements in its semantic capability contract under Chapter 21. Shared mathematical references and status algorithms shall define the result of an admitted combination; implementation algorithms and workspace shall follow the selected provider's resource contract. Capability-gated declarations shall participate in use-site admission through their declared dependencies.

## 2. Execution selectors

| Selector | Numerical transition and observations |
| --- | --- |
| Native | Execute the provider's declared target operations and permitted transformations. Ordinary local/sticky arithmetic events are unobserved; NaN and subnormal behavior follow that Native provider. |
| Strict | Preserve the declared destination projection, signed-zero/special-value rules, observed local events, controls, and selected failure delivery. |
| Reproducible | Apply its declared strict value/status contract and fixed operation tree, accumulator, rounding boundaries, fusion policy, and provider identity for the promised equality scope. |
| Fast | Apply the explicitly published custom value/error/observability contract and its selected relaxations. |

Native shall bind a versioned operation, fault, control-environment, and transformation contract. It may permit contraction, reassociation, reciprocal or elementary approximation, and signed-zero freedom as declared by its provider. Exceptional-value assumptions, such as a finite-input precondition, shall be explicit additional conditions. The compiler shall preserve source side effects, selected memory accesses, volatile effects, atomics, and every explicitly requested stronger operation while using these arithmetic permissions.

A Native operation uses the selected target environment directly. The implementation owes no ordinary-operation flag collection, software sticky union, deterministic NaN repair, or universal entry/exit control wrapper. The complete effective rounding, subnormal, trap, and relaxation combination shall be supported by its provider. An unsupported statically selected combination is a capability error. The defaults and their registered provider-policy values are specified once in Chapter 08.

An explicitly observed operation shall establish its own selected value/control/status contract. A floating interface promising NumericStatus or NumericResult shall provide its defined operation-local status capability even when the surrounding code is Native. An explicitly specified Unobservable report shall use its function-specific contract. An expressly chosen relaxed subnormal policy may have a defined observed contract; an Exact probe and a named finite Checked projection retain their own acceptance rules. An explicit correct/Strict function retains its published accuracy and control requirements when called from Native code.

A later status read shall observe the state supplied by its selected context contract. It places no retrospective event obligation on earlier Native arithmetic. After an unisolated Native call, native FP controls and flags have the provider-declared state. A caller requiring isolation shall use the explicit boundary contract from Chapter 21 to preserve its observed context.

## 3. Numerical transition stages

For each admitted operation, the implementation shall perform the following semantic transition. Physical registers, temporary objects, and metadata are required only when needed to realize its selected observations.

| Stage | Required step |
| --- | --- |
| Bind | Establish operand/result types and the operation's bound policy and provider. |
| Evaluate | Evaluate each source and policy argument under the source-language order. Preserve its completed side effects. |
| Resolve | Resolve the operation's applicable controls once after argument evaluation. Ordinary Native uses its fixed provider environment; an explicit controlled call captures its selected controls here. |
| Compute | Apply the selected mathematical reference/projection or the declared Native operation transition to actual encoded input values. |
| Observe | If the operation selects observation, determine its local NumericStatus and apply its prescribed context update. An ordinary Native transition omits this semantic accounting stage. |
| Deliver | Deliver the selected value, report, Result, or terminal/native-fault outcome. A checked mutation commits its destination on successful delivery. |

An optimizer shall preserve the observations selected by this transition. Within Native's published arithmetic permissions it may choose another permitted value-producing operation tree. Explicit conversion and observed-operation boundaries remain those selected by their interfaces.

### 3.1 Source values and representations

A conversion shall consume its source's actual mathematical value. A direct literal binding instead consumes the token's exact value under Chapter 07. Thus an f64 encoding of decimal `0.1` converts to its encoded rational, whereas an exact decimal token can construct `1/10` directly. A typed source is already a stored-value boundary.

Numerical equality compares values. Representation operations separately observe signed zeros, decimal cohorts, NaN signs/payloads/classes, and other declared representation information. NaN information participates in its representation and arithmetic special-value contracts rather than the finite Exact predicate.

## 4. Conversion interface and status

The standard numeric library catalogue defines these capability-gated semantic operation families:

| Interface family | Result |
| --- | --- |
| `try_checked_cast<T>(x, rounding)` | Status-bearing `NumericResult<T>`. |
| `checked_cast<T>(x, rounding)` | Destination value on success; Numeric Trap on failure. |
| `try_exact_cast<T>(x)` | `NumericResult<T>` with an additional finite-value exactness requirement. |
| `exact_cast<T>(x)` | Exact destination value or Numeric Trap. |
| `saturating_cast<T>(x, rounding)` | Saturated value; inputs without a defined mapping use the corresponding Result/Trap pair. |
| `wrapping_cast<T>(x)` / `truncating_cast<T>(x)` | The integer modulo mapping, after toward-zero projection for a finite nonintegral source. |
| FP `report_*` | IEEE default value and operation-local FP status, with the operation's Trap outlet suppressed. |
| FP `try_*` | `NumericResult<T>`, classified using an explicit or resolved error mask. |

Result variants of Saturating, Wrapping, and Truncating shall expose the same mapping and status through NumericResult. Each strategy is available for the destination families whose value mapping is defined below.

Illustrative declarations retain the specified CXXN construction syntax:

```cpp
f64 source(127.9);
auto rounded(try_checked_cast<i8>(source, TowardZero));
auto exact(try_exact_cast<i8>(source));
i8 value(checked_cast<i8>(source, TowardZero));
```

Here `rounded` contains `Ok` with value `127` and inexact status; `exact` contains `Err(OutOfRange)`, because the actual positive source exceeds the maximum mathematical `i8` value. The direct value form returns `127`. For an in-range fractional input such as `0.5`, the Exact error is `NotExactlyRepresentable`. The interface names denote standard numeric library operations.

The canonical payload and status definitions follow. A report retains an IEEE fallback value when a numeric-result policy would reject it. These fixed-size wrappers use their ordinary value construction and lifetime rules.

### 4.1 Public numeric value identities

`std.numeric` owns the nominal types `NumericResult<T>`, `NumericStatus`, `NumericErrorCode`, `RoundingMode`, `FPFlag`, `FPFlagSet`, `SubnormalPolicy`, `FPControl`, and `FPStatus`. Another standard module shall reference these same identities and declare the floating capabilities its operations require. The declarations below specify source-level value contracts; foreign transport still requires an explicit ABI binding.

RoundingMode is the closed enumeration below. For a finite reference and the selected destination lattice, the operation shall use its case to choose the rounded value; exact members retain their value.

| Case | Projection |
| --- | --- |
| NearestTiesEven | The nearest value; an exact midpoint selects the even integer coefficient in the applicable quantum. |
| NearestTiesAway | The nearest value; an exact midpoint selects the value farther from zero. |
| TowardZero | The nearest value whose magnitude is no greater than the reference. |
| TowardPositiveInfinity | The least value greater than or equal to the reference. |
| TowardNegativeInfinity | The greatest value less than or equal to the reference. |

IntegerRound uses the mathematical integer lattice. A floating projection uses its format precision/exponent and special-value boundary rules. The configuration word current requests environment resolution and is separate from these five mode values.

`FPFlag` is a closed enumeration with cases `Invalid`, `DivideByZero`, `Overflow`, `Underflow`, and `Inexact`. `FPFlagSet` is an allocation-free value representing a subset of exactly these five cases. Default construction yields the empty set; construction from one `FPFlag` yields its singleton. It has value copying, equality, `empty() -> bool`, and `contains(FPFlag) -> bool`. Operators `|`, `&`, `^`, and `~` are set union, intersection, symmetric difference, and complement within these five flags. Their compound-assignment forms update the left set. Set operations shall preserve floating status and operate within this five-member set. Integer encodings require an explicit representation interface. Trap masks and Result error masks use this same type.

`NumericStatus` is an allocation-free record with public fields, in order, `bool value_inexact`, `bool clamped`, `bool wrapped`, `bool payload_changed`, and `FPFlagSet fp_flags`. Default construction makes all Boolean fields false and the flag set empty. Copying or inspecting status has no floating-environment effect. The fields have these meanings:

| Field | Event represented |
| --- | --- |
| `value_inexact` | The operation's value/quantum projection changed the exact source/reference, or an Exact probe detected its specified precision/quantum mismatch. |
| `clamped` | Saturation selected a bound for an out-of-range projection or an explicitly mapped infinity. |
| `wrapped` | Modulo reduction changed the projected mathematical integer. |
| `payload_changed` | A selected representation conversion changed NaN payload information. |
| `fp_flags` | The operation's applicable IEEE event set; empty when that interface defines no IEEE events. |

An Exact probe may report both range and quantum conditions. Integer 128 to i8 is out of range on the integer quantum; -128.9 to i8 additionally has a fractional mismatch. A failed probe provides its status without an approximate destination. Decimal normalization that preserves a value sets no value-inexact event. CXXN integer-destination conversions report their projection events rather than incidental host-instruction flags.

`NumericErrorCode` is a closed enumeration comprising `OutOfRange`, `NonFinite`, `NotExactlyRepresentable`, `ZeroDivisor`, `NonTerminatingExpansion`, `InvalidOperation`, `InvalidShift`, `InvalidBitRange`, `ResourceLimit`, `AllocationFailure`, `TransferUnavailable`, `Invalid`, `DivideByZero`, `Overflow`, `Underflow`, and `Inexact`. `TransferUnavailable` reports an incompatible explicitly requested resource/temporary ownership transfer, independently of resource exhaustion. The last five are selected IEEE-event errors; their names do not conflate them with integer or exact-family failures. An operation shall use the code required by its own classification rule. `ZeroDivisor` applies to the integer/exact zero-divisor contract; `DivideByZero` applies to a floating event. An explicit extension shall define its own error type or publish a translation into this enumeration.

`NumericResult<T>` is the standard nominal tagged result whose `Ok` payload has public `value: T` and `status: NumericStatus` fields, and whose `Err` payload has public `code: NumericErrorCode` and `status: NumericStatus` fields. This field notation describes a payload, not an alternative variable-declaration syntax. Case access, inspection, copying, movement, and destruction follow the ordinary tagged-result rules and the capabilities of `T`. The caller shall select the tagged case before accessing its payload. Failure stores only its code and status; its fixed-size representation records that failure without allocation. Explicit matching and unwrapping follow the standard tagged-result interface.

`SubnormalPolicy` is an allocation-free, equality-comparable control value. `SubnormalPolicy::Preserve` is the standard gradual-subnormal policy. A relaxed policy is an explicitly exported constant of this same type from a named, versioned numeric provider. Such a constant identifies the provider and its policy revision, and that provider declares its input/output subnormal treatment, status, and rounding interactions. Default construction yields `Preserve`. A provider-policy use shall bind the named exported value and the capability that defines its semantics.

`FPControl` has public fields `RoundingMode rounding`, `FPFlagSet trap_mask`, and `SubnormalPolicy subnormal`, in that order. Default construction selects `NearestTiesEven`, an empty mask, and `Preserve`; it does not read or modify an execution context. `FPStatus` has one public `FPFlagSet flags` field and defaults to empty. Both values are copyable without allocation, and neither object owns a thread, task, or scheduler. Provider policy/code lifetime remains an explicit borrowed capability obligation.

### 4.2 Numeric commit and failure

A returning failed checked mutation shall preserve its destination and its selected resource ownership. A successful transition shall commit its completed destination value once. Source/policy argument evaluation precedes that commit and retains its own effects.

NumericTrap shall terminate its selected operation through the core model's nonreturning, noncatchable, nonunwinding numeric terminal transition. A Result operation replaces only its own specified failure outlet. Argument and callback effects retain their declared language or native-fault outcomes. Uncommitted resources on returning paths follow their ordinary cleanup contracts.

## 5. Integer destinations

Let an enabled destination integer have width N and the mathematical bounds L and U defined in Chapter 02. The following named strategies specify its destination projection.

### 5.1 Checked

For a finite source with exact actual value `x`:

1. Compute the mathematical integer `q = IntegerRound(x, R)`.
2. Check `L <= q <= U` using exact integer semantics.
3. On success, encode `q` in the destination.
4. Report `value_inexact` exactly when `q != x`.

The default real-to-integer projection is **toward zero**. Callers may explicitly select nearest-ties-even, nearest-ties-away, toward positive infinity, or toward negative infinity. The implementation shall use that explicit or lexically resolved projection mode regardless of an unrelated native FP register value.

For an integer source, q = x and the operation reduces to integer range checking.

For `i8` with toward-zero projection, successful finite sources satisfy `-129 < x < 128`. For `u8`, they satisfy `-1 < x < 256`. These intervals describe actual source values, not their decimal display strings.

| Actual input | Destination and rounding | Checked result |
| --- | --- | --- |
| `127.9` | `i8`, toward zero | `127`, inexact. |
| `-128.9` | `i8`, toward zero | `-128`, inexact. |
| `128` | `i8`, toward zero | `OutOfRange`. |
| `-0.5` | `u8`, toward zero | `0`, inexact. |
| `-0.5` | `u8`, toward negative infinity | `OutOfRange`. |
| `127.5` | `i8`, nearest-ties-even | `OutOfRange`, because the projected integer is `128`. |
| NaN or either infinity | Any integer | `NonFinite`. |

The decimal fractions in this table are mathematical test values. A floating operand is first interpreted as its actual encoded rational value.

The implementation shall compare against the exact integer boundaries. For example, rounding i64.MAX to f64 yields 2^63; an i64 conversion shall classify that actual value as OutOfRange.

### 5.2 Exact

Finite-value Exact conversion succeeds only if the input value itself belongs to the destination value set. Thus `0.5 -> i8` fails with `NotExactlyRepresentable`, while `127 -> i8` succeeds. A finite value outside the destination's numerical range fails with `OutOfRange`, including `127.9 -> i8`; an in-range value absent from its representable set fails with `NotExactlyRepresentable`. Range classification uses the actual source value before any rounding. Exact has no rounding-mode-dependent success or failure.

`exact_cast` accepts finite inputs. NaNs and infinities use explicit floating-format or representation operations instead. This restriction gives Exact one testable mathematical contract without claiming that a NaN has an exact real value.

`-0.0 -> integer 0` is numerically exact. It is not representation-preserving. A caller needing the zero sign must inspect or preserve the floating representation before conversion.

Exact conversion shall test representability and, on success, encode the exact value. Both outcomes shall preserve ambient FP status and report an empty IEEE event set. Its NumericStatus shall record the applicable precision/quantum mismatch from Section 4. Internal operations shall preserve these selected observations.

### 5.3 Wrapping and Truncating

For finite real input, first take `q = trunc(x)`. Let `r = q mod 2^N`, chosen in `[0, 2^N - 1]`.

```text
unsigned result = r
signed result   = r,         when r < 2^(N-1)
                  r - 2^N,   otherwise
```

This rule applies to both widening and narrowing; it is a numerical modulo conversion, not the source-sign-extension policy of bit reinterpretation. NaNs and infinities fail with `NonFinite`.

`value_inexact` records fractional loss or a changed final finite value; `wrapped` specifically records that the projected integer was changed by modulo reduction. Requesting the wrapping policy does not by itself set `wrapped`.

### 5.4 Saturating

For finite input, compute the selected integer projection and clamp the resulting integer to `[L,U]`. Positive infinity maps to `U`, negative infinity to `L`, and NaN fails with `NonFinite`.

`clamped` shall distinguish selection of a bound from an ordinary in-range projection. A NaN shall take the stated NonFinite failure route.

### 5.5 BigInt destination

Finite real-to-BigInt conversion applies the selected integer projection and the explicit allocation/resource policy. Exact conversion additionally requires an integral input. BigInt has no implicit modulo width; wrapping into a finite bit vector requires an explicit width-bearing operation.

Allocation failure and resource exhaustion remain separate from mathematical integer overflow. A finite result is not promised to fit an unavailable resource budget.

## 6. Floating destinations and cross-family conversion

### 6.1 Ordinary and named floating conversions

An ordinary explicit construction such as `f32 value(source_f64);` shall select the effective floating execution contract. Native conversion shall use the provider's target conversion, special values, subnormal behavior, and unobserved events. An observed format conversion shall round the actual source directly to the destination under its selected controls and record the specified local events. Either contract may produce an inexact, subnormal, infinite, or NaN result where admitted. Implicit assignment and argument conversion additionally require the language's losslessness proof.

A named Checked cast to a floating destination shall take the finite actual source, perform the specified gradual destination projection under the selected rounding mode, and reject Overflow as OutOfRange. Directed rounding to a maximum finite value therefore still fails when that projection incurs Overflow. Inexact and Underflow remain successful status events. A nonfinite source fails NonFinite. The call shall merge its local events under Section 9 while preserving its fixed acceptance predicate.

An Exact cast shall accept a finite value exactly representable in the destination and encode it under the flag-free rule of Section 5.2. A finite out-of-range value fails OutOfRange; an in-range precision mismatch fails NotExactlyRepresentable. A typed input is its actual stored value. Signed-zero or payload preservation belongs to the selected representation interface.

These named predicates remain independent of arithmetic Result error masks and ambient trap masks. Their value-returning variants shall enter NumericTrap exactly when their corresponding Result is Err. A caller selecting another subnormal or event policy shall use an ordinary or explicitly controlled format-conversion interface whose contract defines that policy.

### 6.2 Integration matrix

Every cell below describes an explicit conversion family. Its selected strategy supplies the value projection and execution contract.

| Source | Fixed integer / BigInt | Binary or fixed decimal float | Fixed-point | Rational | BigDecimal |
| --- | --- | --- | --- | --- | --- |
| Integer | Specified integer strategies; BigInt resource contract. | Direct rounding; Exact if representable. | Exact coefficient rescale, then selected projection. | Exact `x/1`; resources as required. | Exact finite decimal; resources as required. |
| Binary float | Actual finite value, then integer projection. | Direct format conversion; explicit crossing into decimal. | Actual value divided by destination quantum, then projection. | Exact rational of finite encoding. | Exact finite expansion of finite binary value, if resources permit. |
| Fixed decimal float | Actual finite value, then integer projection. | Direct conversion; explicit crossing into binary. | Actual value divided by destination quantum, then projection. | Exact rational of finite encoding. | Exact finite decimal value, if resources permit. |
| Fixed-point | Exact scaled value, then selected projection. | Direct rounding from scaled value. | One exact rescale and one projection. | Exact scaled rational. | Exact for the supported radix-2/radix-10 fixed families. |
| Rational | Integer projection; Exact requires integral value. | Direct rounding, or Exact representability test. | Direct quantum projection. | Canonical exact value or explicit resource-policy transfer. | Exact only for a terminating decimal; otherwise explicit finite context. |
| BigDecimal | Exact finite decimal value, then projection. | Direct rounding; bounded destination limits apply. | Direct quantum projection. | Exact rational, subject to resources. | Copy/transfer or explicitly contextual rounding. |

Conversion into a finite-only family shall classify NaN or infinity as NonFinite, except for the Saturating infinity-to-integer-bound mapping in Section 5.4.

Typed cross-family arithmetic shall use the explicit conversions defined for those families. Untyped literals bind under Chapter 07. A conversion shall realize its direct source-to-destination projection; an intermediate representation is admissible when it preserves that selected value and status contract.

### 6.3 Common floating type

Let `V(T)` denote the complete set of finite numerical values representable by format `T`, including all subnormals and zero. A candidate common type `C` must satisfy:

```text
V(A) union V(B) is a subset of V(C).
```

The selected common type is the unique least enabled format under the defined format-inclusion order, within the permitted arithmetic family. If the available format graph contains incomparable minimal candidates and no unique least candidate, the caller must select a destination explicitly. If no candidate exists, the compiler shall diagnose the requiring operation. Enabled capabilities determine this floating-format candidate set.

For the standard enabled formats, `common(f16,bf16) = f32`: `f16` has values needing more significand precision than `bf16`, while `bf16` has both greater magnitude range and smaller positive subnormal values than `f16`.

Finite-value inclusion is not a claim that all NaN payloads or signaling behavior survive an arithmetic format conversion unchanged. Signed-zero and NaN conversion contracts remain separately observable. An implicit permitted floating widening follows its format-conversion contract; exact finite-value preservation alone is not representation identity.

Cross-family explicitness still applies even when a particular cross-radix value or an entire small format could be embedded exactly.

## 7. Fixed-point integration

A fixed type uses the coefficient and compile-time quantum defined in Chapter 03. The operations below add destination selection and projection to that representation.

### 7.1 Rescaling

For source coefficient `c`, source quantum `Ds`, and target quantum `Dt`:

```text
exact_target_coefficient = c * Ds / Dt
target_coefficient      = IntegerRound(exact_target_coefficient, R)
```

The target coefficient is then range-checked. This calculation is an exact mathematical specification, not a requirement to allocate an unbounded intermediate integer. Implementations may cancel factors, use bounded multiword arithmetic, or prove an equivalent sequence.

A selected exact/Checked rescaling shall classify range from the final mathematical projected coefficient. Its provider shall realize that result through bounded arithmetic or its explicitly selected resource contract.

Checked rescaling allows reported quantization loss. Exact rescaling rejects a nonrepresentable scaled value. Wrapping or saturating the coefficient requires the corresponding explicit strategy and does not change the quantum.

Example with destination `fixed<i8,10,-1>` and nearest-ties-even:

| Source value | Exact destination coefficient | Result |
| --- | --- | --- |
| `12.74` | `127.4` | coefficient `127`, value `12.7`, inexact. |
| `12.75` | `127.5` | coefficient would be `128`: `OutOfRange`. |
| `-12.85` | `-128.5` | coefficient `-128`, value `-12.8`, inexact. |

### 7.2 Arithmetic and conversion chains

Addition and subtraction within one fixed type are exact coefficient operations followed by the specified integer overflow policy. Fixed multiplication and division compute the exact mathematical result and quantize once to an explicitly selected destination fixed type. Their named interfaces accept that destination and a rounding policy; the rounding default in the standard profile is nearest-ties-even. Ordinary fixed operators, when provided by the selected fixed-arithmetic capability, use the operand fixed type as their destination. Different fixed types require an explicit common destination rather than an implicit scale guess.

An explicitly validating fixed division shall classify a zero divisor as ZeroDivisor through its Result/Trap outlet. A Native fixed-arithmetic capability shall publish any native domain-fault behavior. Typed operands and untyped literals bind under their established family rules.

An explicit sequence of rescalings is semantically significant. Rounding `1.251` directly to tenths with nearest-ties-even gives `1.3`. Rounding first to hundredths gives `1.25`; rounding that value to tenths gives `1.2`. An optimizer shall preserve the value and selected status of those explicit projection boundaries.

## 8. Rational and BigDecimal integration

### 8.1 Rational value model

Rational uses the canonical finite value model in Chapter 03. Its exact arithmetic shall deliver that value or its declared domain/resource failure. Factor cancellation and normalization may reduce the work needed for the selected exact result.

A finite binary floating value converts to Rational by decoding its significand and exponent. For example, the `f64` encoding `0x3FB999999999999A` converts to:

```text
3602879701896397 / 36028797018963968
```

This is distinct from `1/10`. A Rational created directly from the exact decimal literal value `0.1` can denote `1/10`; the routes have different typed inputs.

### 8.2 Finite expansion is necessary, not sufficient

After reducing a Rational:

- A finite binary expansion requires its denominator to contain no prime factors other than `2`.
- A finite decimal expansion requires its denominator to contain no prime factors other than `2` and `5`.

A fixed destination floating format must additionally have sufficient significand precision, exponent range, and subnormal resolution. For example, `1 + 2^-11` has a terminating binary expansion but is not exactly representable in `f16`.

An unbounded finite decimal representation can hold any finite binary-format value exactly in principle. Its potentially large coefficient and scale still require resources. Conversely, a finite decimal such as `1/10` does not become exactly representable in a finite binary format simply by selecting a larger fixed binary width.

### 8.3 BigDecimal value model

BigDecimal uses the finite coefficient/exponent model in Chapter 03. Its selected capability shall enforce its exponent and resource contract and distinguish their failures from numerical rounding.

Exact BigDecimal arithmetic returns an exact finite decimal whenever that result is representable within the declared resource and exponent limits. If exact division has a nonterminating decimal expansion, it reports `NonTerminatingExpansion`. In particular:

```text
exact BigDecimal: 1 / 8  -> 0.125
exact BigDecimal: 1 / 3  -> NonTerminatingExpansion
Rational:        1 / 3  -> 1/3
```

A rounded BigDecimal division requires a finite precision and a rounding mode supplied through an explicit context or its lexically resolved binding. That context binds the operation. An exact context shall return NonTerminatingExpansion for 1/3; a rounded context shall use its supplied finite precision.

BigDecimal numeric equality shall compare mathematical values. Representation operations shall separately expose coefficient, exponent, and any declared presentation metadata.


## 9. Observed floating operations and contexts

### 9.1 Local status and result classification

For an observed operation, let F_before be the selected context's prior sticky set and F_local the operation's independently determined event set. On a returning path the implementation shall establish:

```text
F_after = F_before union F_local
```

This local set records a repeated event even when the same bit was already sticky. A report contains the defined result and that local status. A NumericResult shall intersect F_local with its resolved error mask and select the first member in this priority order:

```text
Invalid, DivideByZero, Overflow, Underflow, Inexact
```

The remaining local events stay in the returned status. The default result mask is supplied by Chapter 08. If no selected flag fails, `require_finite` additionally tests the delivered value; its failure selects NonFinite. Otherwise the NumericResult is Ok with value and status. Hence quiet-NaN propagation can succeed under a flag-only policy, and can instead fail NonFinite when that predicate is selected.

### 9.2 Canonical delivery algorithm

An observed floating operation shall first compute its complete default value and local events under its captured controls. It shall then restore any temporary control override and merge the applicable events into the selected context without re-raising historical events. Its final delivery is:

| Interface | Delivery |
| --- | --- |
| Observed ordinary value operation | Apply the selected trap mask to its local events, then return the value or enter NumericTrap. |
| `report_*` | Return the default value and NumericStatus. |
| `try_*` | Return the NumericResult classified by Section 9.1. |
| Floating `checked_*` | Return the corresponding try result's value on Ok; enter NumericTrap on Err. |

The report/try delivery route suppresses this operation's own trap outlet while computing its value and status. An ambient trap mask therefore participates only in interfaces that select that mask as their delivery rule. For `try_div(f(),g())`, f and g have already executed before the operation-owned scope begins; their earlier effects and failures remain their own transitions.

Named Checked/Exact conversions use their fixed predicates in Sections 5 and 6. They reuse the applicable local-status collection and restoration steps without replacing those predicates by an arithmetic error mask.

### 9.3 Observed context ownership

`FPControl` and `FPStatus` are the public values defined in Section 4.1. An observed context shall own its selected controls and sticky history for its execution domain. A managed task provider shall preserve that selected context across suspension and migration. Its declared task-creation policy establishes inherited or explicit controls and initial flags; an explicit transfer/reduction operation combines task histories.

An ordinary Native task requires only its provider's native environment contract. Its existence requests no shadow FP state or save/clear/restore instrumentation. Context ownership and task integration are selected features under the core execution model.

### 9.4 Public context interfaces

An enabled `std.numeric` context capability supplies these operations on its selected active context:

| Signature | Required transition |
| --- | --- |
| `FPControl get_fp_control()` | Return its current controls. |
| `FPStatus get_fp_status()` | Snapshot its current supplied flag state. For an observed context this is its accounted sticky history; after unisolated Native work it has only the provider's native-state meaning. |
| `Result<void,FPControlError> try_set_fp_control(FPControl control)` | Validate the complete combination and atomically replace logical controls on success; preserve controls/flags on failure. |
| `void clear_fp_status(FPFlagSet flags)` | Remove the selected bits from this context's state. |
| `void merge_fp_status(FPStatus status)` | Union the supplied bits into this context's state. |

`FPControlError` has allocation-free payloadless cases UnsupportedRounding, UnsupportedSubnormal, and UnsupportedTrapMask. If several fields are unsupported, selection uses that order. These context operations shall complete without allocation, suspension, or language throw. They expose context-read or context-write effects. Clear, merge, and mask replacement change state without creating an arithmetic event or re-raising sticky flags.

The provider shall realize each selected context capability through hardware or explicitly admitted support. Failure to establish a previously promised context uses its declared infrastructure terminal boundary. Concurrent access to an explicitly shared context obeys the memory model. A scoped context or Native/Strict adapter shall publish its storage and restoration ownership; its implementation cost belongs to that explicit feature.

## 10. NaNs, inspection, and ordering

### 10.1 Arithmetic NaN selection

For a Strict operation or named observed interface selecting CXXN deterministic propagation, the implementation shall apply this algorithm:

1. Every signaling-NaN operand contributes Invalid, regardless of which NaN is selected for the result.
2. If any quiet-NaN operand exists, select the first quiet NaN in the operation's defined operand order.
3. Otherwise select the first signaling NaN and quiet the result.
4. Preserve the selected NaN's sign and payload subject to the destination format's specified payload mapping.
5. If an operation generates NaN without a NaN input, use the format's canonical quiet NaN.

The operation shall additionally record its own specified exception conditions. Source evaluation order follows the core model; an operation with several NaN candidates shall declare their selection order. Native ordinary propagation instead follows the selected provider contract.

Consequently, `add(sNaN(payload=1), qNaN(payload=2))` selects payload `2` while still generating Invalid. This is a CXXN deterministic choice; it is not a claim that all hardware IEEE implementations use this exact priority.

For the binary interchange formats in this baseline, a canonical generated qNaN has positive sign, the quiet bit set, and zero payload bits. For arithmetic cross-format conversion, the source payload is interpreted as an unsigned payload integer, zero-extended when it fits, or reduced to the destination payload's low bits when necessary; the result is quiet. Payload loss is observable through `payload_changed`. A same-format bit copy performs no arithmetic conversion and preserves the signaling bit.

The declared decimal encoding provider supplies its canonical NaN and payload mapping, and includes them in its representation contract. A decimal representation crossing shall use its declared encoding conversion.

### 10.2 Representation inspection

Bit inspection, signaling-NaN classification, and total ordering shall preserve the complete operand representation and ambient status. Parameter transfer shall preserve the signaling bit and payload for these operations.


### 10.3 Binary total order

For the canonical binary encodings covered here, define a sortable unsigned key from raw bits `u` of width `W`:

```text
if sign bit is set: key = bitwise_not(u), limited to W bits
otherwise:          key = u xor (1 << (W - 1))
```

Unsigned key comparison supplies the corresponding total order. It distinguishes the zeros and NaN representations, with no FP arithmetic:

```text
negative NaNs < -infinity < negative finite values < -0
             < +0 < positive finite values < +infinity < positive NaNs
```

Among positive NaNs, signaling precedes quiet and payload order is increasing; among negative NaNs, those directions reverse. Ordinary numeric comparison retains its separate unordered-NaN behavior.

This bit-key algorithm is not an assertion about noncanonical extended formats or decimal encodings. Their enabled representation capability must provide its canonicalization and total-order implementation. A numeric container requiring this total order shall select its ordering interface explicitly.

## 11. Floating range projection, tininess, and Underflow

The Strict gradual projection shall use the target radix b, precision p, normal exponent range [emin,emax], and selected rounding mode R. For a finite exact reference r, define:

```text
q = RoundToPrecisionWithUnboundedExponent(r, b, p, R)
M = (b - b^(1-p)) * b^emax
overflow = (abs(q) > M)
tiny_after = (0 < abs(q) < b^emin)
y = RoundDirectlyToDestinationFormat(r, R)
inexact = (y != r)
underflow = tiny_after and inexact
```

For `r = 0`, tininess is false. For nonzero finite `r`, the first rounding can be defined using `k = floor(log_b(abs(r)))`, quantum `u = b^(k-p+1)`, and `q = u * IntegerRound(r/u, R)`.

The implementation shall round the delivered y directly from r. The auxiliary q supplies range classification, rather than an intermediate delivered value. If overflow is true, the projection shall set Overflow and Inexact and select y by this table, with the reference's sign:

| Rounding mode | Positive r | Negative r |
| --- | --- | --- |
| Either nearest mode | Positive infinity | Negative infinity |
| TowardZero | M | -M |
| TowardPositiveInfinity | Positive infinity | -M |
| TowardNegativeInfinity | M | Negative infinity |

Otherwise y shall be the directly rounded finite/subnormal/zero destination value under R. Its signed-zero convention comes from the operation's exact-zero rule or the sign of a nonzero r rounded to zero.

This rule gives the following `f64` to `f32` nearest-ties-even cases:

| Source f64 bits | Exact source | Final f32 bits | Flags |
| --- | --- | --- | --- |
| `0x380FFFFFE1000000` | `2^-126 - 31 * 2^-155` | `0x00800000` | Underflow and Inexact. |
| `0x380FFFFFF0000000` | `2^-126 - 2^-151` | `0x00800000` | Inexact only. |


An explicitly relaxed or Native subnormal policy shall use its published input/output transformations and events. The algorithm above remains the contract for the Strict gradual projection.

An exact subnormal result does not set Underflow. Two operations may deliver the same minimum positive normal result with different Underflow flags; the precision-rounded unbounded-exponent tininess test, together with inexactness, determines the event.

## 12. Constant evaluation, optimization, and diagnostics

### 12.1 Mandatory constant evaluation

Required constant evaluation shall use the target operation contract and resolved static policy. An observed operation shall use an isolated evaluation context. A Native operation shall use the target provider's admitted result/fault relation. Evaluation-time status belongs to that evaluation and runtime state begins under its selected runtime context.

An unhandled numeric failure, observed Invalid event, or terminal/native-fault outcome on a required evaluation path is ERROR. An explicit Result may instead produce a constant Err as its completed value. Only evaluated operations contribute events; all syntax and typing requirements apply under the core compile-time rules.

### 12.2 Runtime transformations

An optimizer shall preserve each selected operation's observable value, status, failure, and source effects. An observed runtime `0.0/0.0` has a value and an Invalid event; replacing it by a qNaN constant shall also realize that selected event. A repeated event stays visible in the local report. Explicit conversion chains retain their declared rounding boundaries.

Native arithmetic permits its provider's selected transformations and unobserved events. Folding Native `0.0/0.0` to an admitted native NaN therefore requires no software event replay. A status read elsewhere supplies only the observations described in Section 9. Runtime-dependent explicit controls shall be accounted for wherever a selected observed operation reads them.

### 12.3 Numeric diagnostic applicability

Severity names, blocking behavior, suppression, and promotion are defined once in Chapter 08. The following table classifies numerical cases under that policy:

| Condition | Classification / required semantic action |
| --- | --- |
| Unavailable derived type, undefined binding rule, or lossy implicit conversion without an admitted rule | ERROR at the requiring use. |
| Unhandled failure on a required constant-evaluation path | ERROR; an explicit constant Result Err is a completed Result value. |
| Statically established zero divisor on an evaluated ordinary integer path | ERROR. |
| Statically invalid fixed shift count or bit range | ERROR under that interface's static-domain rule. |
| Runtime input whose failure is possible | Execute its selected Native, Checked, report, or Result contract. |
| Proven dangerous or deterministically failing ordinary operation outside a mandatory-error case | ANOMALY under the configured severity policy. |
| Explicitly requested precision loss worth reporting | WARNING; routine rounding uses its declared status instead of a diagnostic per operation. |
| Proven suspicious loss contrary to the surrounding contract | ANOMALY. |
| Permitted provider or profile selection worth reporting | INFO or the configured promotion. |

A floating IEEE zero divisor has its selected floating event/value behavior rather than the integer-domain classification. Named Result probes can intentionally return Err. Diagnostic selection changes reporting; semantic operation selection determines the execution transition.

## 13. Configuration and provider binding

Each owning definition shall bind its enabled representations, literal policies, numerical execution selector, operation controls, providers, and selected resource contracts through Chapter 08. Its semantic boundary record shall retain the requirements relevant to each shared interface. Storage, Native execution, observed status, required accuracy, and optional software support are separate capability claims.

A selected explicit stronger operation shall retain its value/status/ownership function in every preset. Ordinary Release operators use the Native defaults from the sole preset table. A software operation is available through an explicitly enabled conforming provider; otherwise a requiring use receives a capability diagnostic. A compiled callee retains its bound contract across import, inlining, and LTO.

## 14. Vector and reduction deltas

An enabled vector operation shall bind the active lanes' scalar type and selected operation policy. Merge masking shall preserve each inactive passthrough representation; zero masking shall supply its declared zero representation. Argument evaluation follows the core source order independently of lane participation.

An explicitly observed, checked, or Result masked operation shall compute arithmetic events for active lanes only. Its aggregate flags are their union. Aggregate Result supplies a whole vector on success and no readable vector on failure; a per-lane report supplies each active lane's result/status and an inactive marker elsewhere. A requested deterministic Trap attribution selects event priority first, then the least lane index among equal-priority failures.

Ordinary Native pure arithmetic may compute inactive register lanes and discard their results when that execution adds no observable store, callback, memory access, or required fault. Incidental unobserved FP flags are permitted by its Native contract. A masked arithmetic operation supplies no permission to perform an otherwise unselected memory load or to violate a separately requested active-only reported operation.

A Reproducible reduction shall use its declared logical tree, accumulator, projection, and fusion policy. A Native reduction may use its provider's admitted trees and transformations. CPU, SIMD, and GPU providers shall publish the selected contract and its supported placement.

## 15. Selected conformance obligations

A conforming numerical provider shall implement the admitted contracts it advertises: canonical type binding, the selected Native result/fault map, explicit projection predicates, observed local status when requested, deterministic representation/NaN operations where selected, and applicable resource/ownership transitions. The Strict tininess examples, reported-mask behavior, and task-context restoration clauses apply to those selected features. Conformance claims shall identify the operation/profile pair they cover.

## 16. Specialized facilities

[Complex arithmetic](05_complex_arithmetic.md#chapter-05-complex-arithmetic) supplies component formulas and exceptional dispatch. [Numeric expressions](07_numeric_expressions.md#chapter-07-numeric-expressions) supplies concrete calls, literals, and resource algorithms. [Mathematical functions](18_mathematical_functions.md#chapter-18-mathematical-functions) and [quantities](31_units_interfaces.md#chapter-31-units-interfaces) supply their selected accuracy, domain, or affine-transform deltas. Each facility shall reuse this chapter's canonical status and delivery definitions.

