<a id="chapter-18-mathematical-functions"></a>

# CPN26 Mathematical Functions Specification

## 1. Scope, binding, and capabilities

The optional module std.math publishes namespace std::math. The numerical identities and observation/delivery algorithm belong to [Chapter 04](04_numeric_integration.md#chapter-04-numeric-integration). Calls, borrowing, argument effects, and cleanup follow the [core model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance) and [standard-library contract](14_standard_library.md#chapter-14-standard-library). This chapter defines optional standardized function contracts. The core conformance model shall determine the implementation baseline; a selected mathematical capability shall add its stated obligations.

Importing std.math shall make its capability-gated declarations visible to name lookup. A requiring use shall bind the particular function, format, controls, and delivery form it requests. Floating representation support, a Debug/Release preset, and Complex storage shall retain their own capability dependencies. Correctly rounded elementary functions and principal Complex functions shall enter the dependency closure through their separately selected claims.

In the signature tables, F is one enabled floating format, I an enabled fixed signed integer, and C is complex<F>. A row is a schema instantiated with the ordinary generic/declare grammar. Repeated F parameters shall agree under generic inference; an explicit F uses the conversions admitted at that binding. Same-format floating argument transfer shall preserve its representation, including a signaling NaN.

| Capability family | Contract of each selected entry |
| --- | --- |
| `math.basic` | One claimed representation or binary arithmetic operation from Section 3, with its allocation-free public contract. |
| `math.constants` | One claimed constant/format/rounding combination from Section 7. |
| `math.correct` | One claimed real elementary function, format, control set, and delivery form from Section 4, with correct rounding and declared resources. |
| `math.approx` | One claimed approximation entry with its selected domain, accuracy, observation, controls, delivery, and resource contract in Section 5. |
| `math.complex.principal` | One claimed finite-input principal function, component format, control set, and delivery form in Section 6. |
| `math.complex.power` | One claimed finite, nonzero-base principal-power entry from Section 6. |
| `math.complex.extended` | A complete, published, versioned nonfinite table for one claimed complex function/format/control/delivery entry. |

A provider shall enumerate its supported operation/format/control/delivery combinations, accuracy, local-status contract, resources, and reproducibility scope in its semantic capability and boundary contracts under Chapter 21. Each combination shall bind its stated dependencies. An implementation may publish any subset compatible with those dependencies. A requiring use shall bind a supported combination or receive ERROR at that use. A runtime provider reference shall identify the selected contract, and runtime policy admission shall follow Section 2.4.

Correct and approximate claims shall resolve independently. For example, an approximation claim for sin/f64 shall obtain its mathematical reference and parameter shape from the catalogue while binding the approximation provider's own accuracy contract. A provider may implement that claim alone. A claim for one correctly rounded function shall establish the obligations for that declared function/format/control/delivery combination. The selected software-fallback policy shall govern software support added by these claims.

The named basic, correct, and principal contracts below are explicit numerical features. They retain their prescribed results and selected observations when called from Native code. Ordinary Native floating operators use Chapter 04 independently. Approximation entries select their own provider contract through an explicit ApproximationRef.

Sections 3 and 4 define binary-interchange arithmetic. Decimal inspection uses its encoding descriptor; decimal arithmetic and extended formats shall bind per-function capabilities defining their representation, rounding, exceptional cases, and status.

## 2. Public controls, results, and observation

### 2.1 Public type identities

`RoundingMode`, `FPFlagSet`, `SubnormalPolicy`, `NumericStatus`, and `NumericResult<T>` below refer to their public `std::numeric` identities. `Option<T>` and `Result<T,E>` refer to `std::Option<T>` and `std::Result<T,E>`. They are not redeclared by `std.math`.

The following public values have no owning allocation, and copying, moving, and destroying them are nonthrowing:

| Type | Public content |
| --- | --- |
| `MathPolicy` | `Option<RoundingMode> rounding`, `Option<FPFlagSet> trap_mask`, `Option<FPFlagSet> error_mask`, `Option<SubnormalPolicy> subnormal`, `Option<bool> require_finite`. |
| `ComplexMathPolicy` | `MathPolicy common`, `Option<RoundingMode> real_rounding`, `Option<RoundingMode> imag_rounding`. |
| `MathResources` | `Option<std::mem::ResourceRef> temporary_resource`. |
| `MathReport<T>` | `T value`, `NumericStatus status`. Its lifecycle properties also require the corresponding properties of T. |
| `ComplexMathReport<F>` | `complex<F> value`; `NumericStatus real_status`, `imag_status`, `common_status`, and `status`. |
| `FPClass` | Enumeration cases `Zero`, `Subnormal`, `Normal`, `Infinity`, `QuietNaN`, `SignalingNaN`. Sign is observed separately. |
| `Decomposition<F>` | Tagged alternatives `Finite(F significand, i32 exponent)`, `Infinite(F representation)`, and `NaN(F representation)`. |
| `DomainReason` | Enumeration cases `NonFiniteInput`, `OutsideApproximationDomain`, `UnsupportedSpecialCase`. |
| `PolicyReason` | Enumeration cases `UnsupportedControl`, `UnsupportedAccuracy`, `InvalidBound`, `StatusUnavailable`, `WrongFunction`. |
| `MathError` | Tagged alternatives `UnsupportedDomain(DomainReason reason)`, `UnsupportedPolicy(PolicyReason reason)`, and `Allocation(std::mem::AllocationError cause)`. |

The selected CPN26 ABI shall determine these source types' native layout; foreign transport requires its declared binding. `MathPolicy()` initializes all options to None. `ComplexMathPolicy()` contains `MathPolicy()` and absent component overrides. `MathResources()` contains no resource. The record constructors additionally admit their listed fields in declaration order under ordinary aggregate construction. The result and tagged alternatives use the ordinary active-case construction and access rules.

`Decomposition<F>` is available only when `i32` is enabled and can represent every required exponent for F. This is true of the baseline binary formats when `i32` is enabled. The interface shall require that i32 capability at its use.

A MathResources reference shall borrow its selected temporary resource for the call. A claim shall publish its fixed internal storage requirements and any temporary resource requirements. The provider shall acquire dynamic temporary storage through the supplied resource and retire it before successful return or a returning failure. With MathResources() it shall use an admitted allocation-free implementation or report the applicable missing-resource failure. An unmet resource requirement shall return AllocationError, including ProviderUnavailable for a required absent resource, through the selected interface's outer failure route. Returned values shall own their result independently of temporary storage. Algorithmic resource work shall follow its published effect contract.

### 2.2 Bound operation context

After argument evaluation and parameter conversion, a call shall resolve its operation context once under Chapter 04. A present MathPolicy field is its explicit override. An absent field resolves through the function's published binding and any permitted current-context selection. Component modes replace only their respective common rounding mode. The captured contract includes provider, error mask, finite predicate, controls, and selected resources.

A selected standard basic/correct/principal entry shall bind its observed value contract and gradual subnormal semantics. Importing it into Native code shall preserve that binding. Representation inspection, copy_sign, decompose, total ordering, and neighbor selection shall use stored encodings under their stated function contract. A relaxed transformation shall require a distinct admitted provider contract. Policy admission shall establish control compatibility before the selected operation. Approximation entries shall resolve the controls admitted by their selected ApproximationRef.

A statically unsupported combination is ERROR. A runtime unsupported policy uses outer Err(UnsupportedPolicy(UnsupportedControl)); a basic interface without that outer Result uses MathDomainTrap. Observed calls shall establish and restore their requested control scope under Chapter 04. A value-only Unobservable approximation uses its declared Native environment directly. The source argument expressions retain their own prior effects and failure outlets.

### 2.3 Mathematical reference and status

A mathematical reference shall consume actual encoded argument values. A correct function shall project its exact reference once into F under the captured mode; Complex has one projection per component. This reference shall specify the required result while the selected provider determines its algorithm and workspace under the published resource contract. Finite projection, Overflow, Underflow, and local-event accounting use Chapter 04. Function-specific special-value cases below add their stated events.

For basic and correct arithmetic, value_inexact shall equal the operation's Inexact membership; clamped and wrapped shall be false. payload_changed records the representation mapping defined by Chapter 04. Representation inspection shall preserve status. Approximation status follows its selected contract while retaining those fields' canonical meanings.

A ComplexMathReport shall assign each final projection to its component status and whole-function conditions to common_status. Aggregate status shall union flag sets and OR Boolean fields. Each common event is recorded in common_status once.

Admitted NaNs shall use Chapter 04's deterministic selection algorithm unless a function specifies another case. Selection order is displayed parameter order, including (a,b,c) for fma and (y,x) for atan2. Capability-domain admission precedes this arithmetic rule; each function also records the additional conditions it specifies below.

### 2.4 Delivery forms and failures

The signature catalogue in Section 8 fixes return types independently of whether a particular provider happens to allocate. Let `V` be the result value type and `Report` its scalar or complex report:

| Facility | Value form | Report form | Numeric-result form |
| --- | --- | --- | --- |
| Basic arithmetic | V | `MathReport<V>` | `NumericResult<V>` |
| Correct real and complex mathematics | V | `Result<Report,MathError>` | `Result<NumericResult<V>,MathError>` |
| Explicit approximate real mathematics | F | `Result<ApproxReport<F>,MathError>` | `Result<NumericResult<F>,MathError>` |

An observed value/report/try form shall apply Chapter 04's canonical delivery algorithm to the selected function value and local status. Report wraps the value and status in the table's report type. Try classifies its local events and finite predicate into NumericResult; Complex requires both components finite. The error mask and finite predicate belong to Result classification, while a value form uses its captured trap mask.

An outer Err(MathError) reports domain admission, policy admission, or authorized resource acquisition failure before a mathematical result exists. Outer Ok contains the completed report or NumericResult, including an inner Err when its numeric policy rejects the completed computation. A returning outer failure shall preserve caller status except for the independently completed argument/callback effects; algorithm-internal FP events remain private.

DomainReason classifications are:

| Condition | DomainReason |
| --- | --- |
| NaN or infinity outside the selected capability domain | NonFiniteInput. |
| Finite input outside an approximation's published domain | OutsideApproximationDomain. |
| Finite special case requiring an unselected extra table | UnsupportedSpecialCase. |

Admission shall inspect the representation while preserving its signaling class and status. MathDomainTrap specializes ContractTrap for a value form's domain/policy failure. Its allocation failure uses NumericTrap with the resource condition. Result forms replace their own stated outlets; independently invoked user/provider callbacks retain their published effects. Returned tagged values follow their canonical must-use and payload-access contracts.

### 2.5 Accuracy and optimization contracts

| Accuracy | Promise |
| --- | --- |
| `correct` | The prescribed directly rounded value, zero signs, exceptional values, and local status. |
| `bounded_ulp(k)` | At most k adjacent steps from the correctly rounded reference in the declared finite destination lattice. |
| `bounded_absolute(e)` | Absolute error at most the nonnegative mathematical bound e on the declared domain. |
| `bounded_relative(r,a)` | Absolute error at most `max(a, r * abs(reference))`, with explicit nonnegative relative bound r and absolute bound a. |
| `hardware_native` | Only the selected versioned instruction/provider's declared result and status contract; no implicit mathematical-error bound. |

A bounded provider publishes its admitted input domain, reference function, coverage of signed zeros and subnormals, exceptional-value policy, and status observability. A claimed bound includes final storage rounding and every approximation. The absolute term fixes the permitted error at a reference zero. A provider shall prove the declared bound on approximation error throughout its admitted domain.

A bound function shall retain its selected accuracy and observations in every surrounding execution profile. Reproducible selection additionally pins provider/version and output-equality scope. Optimization shall preserve its selected value, status, source effects, and terminal boundaries under the core model.

## 3. Basic real operations

### 3.1 Classification, representation, and neighboring values

`classify(x)` returns the unique `FPClass` case matching x's encoding. `is_nan` recognizes both NaN classes; `is_signaling_nan`, `is_infinite`, `is_normal`, `is_subnormal`, and `is_zero` recognize their named classes. `is_finite` recognizes Zero, Subnormal, or Normal. `signbit` reports the stored sign for every class. These functions preserve even signaling-NaN encodings and generate no flags.

`copy_sign(x,y)` copies only y's sign into x's representation and generates no flags, even for signaling NaNs. `representation_equal(x,y)` compares all representation bits under F's representation contract. `total_order(x,y)` is the non-strict predicate that x precedes or equals y in the specified total order; it is true for identical representations. For the baseline binary formats it compares the numeric integration chapter's sortable bit keys using unsigned `<=`. It distinguishes negative/positive zero and NaN encodings without numeric comparison or Invalid.

`next_up` and `next_down` select adjacent representable numeric values independently of rounding. Let t be the least positive subnormal and M the largest finite positive value:

| Input | `next_up` | `next_down` |
| --- | --- | --- |
| `+infinity` | `+infinity` | `M` |
| `-infinity` | `-M` | `-infinity` |
| `+0` or `-0` | `t` | `-t` |
| `-t` | `-0` | The next more negative value. |
| `t` | The next more positive value. | `+0` |
| `M` | `+infinity` | Its finite predecessor. |
| `-M` | Its finite successor. | `-infinity` |

For all other finite nonzero inputs the usual adjacent value in the named direction is selected. No non-NaN case generates any flag, including a transition between a finite endpoint and infinity or between a subnormal and zero. A NaN follows arithmetic propagation; signaling input generates Invalid. These are neighbor operations, not floating addition by an epsilon.

### 3.2 Square root, fused multiply-add, magnitude, and scaling

`sqrt(x)` rounds the exact nonnegative square root once. Either zero preserves its sign; positive infinity returns positive infinity with no flags. Negative nonzero finite values and negative infinity produce canonical qNaN with Invalid. NaNs follow the propagation rule.

`fma(a,b,c)` rounds the exact reference `a*b+c` once. Its complete nonfinite classification is:

1. A zero factor paired with an infinite factor contributes Invalid, including when c is a quiet NaN. An infinite product opposed by an infinite c also contributes Invalid. The product sign is the XOR of its factors' signs.
2. Every signaling-NaN argument contributes Invalid. If any NaN argument exists, propagate the deterministically selected NaN after recording the applicable Invalid conditions.
3. Without a NaN argument, an Invalid condition produces canonical qNaN. Otherwise an infinite product or infinite c supplies the corresponding signed infinity.
4. Otherwise compute the exact finite expression and its single final projection.

For an exact zero in step 4, a zero product has the XOR sign. If that zero product and a zero c have the same sign, preserve it. Every other exact cancellation returns negative zero only for TowardNegativeInfinity, and positive zero for the other modes. Nonzero values rounded to zero follow ordinary signed rounding. The implementation shall preserve this single-projection value and its local status.

`hypot(x,y)` rounds the exact nonnegative `sqrt(x*x+y*y)` once. Both zeros yield positive zero. If either operand is infinity, return positive infinity even if the other is a NaN; a signaling NaN still contributes Invalid. Without an infinity, NaNs propagate normally. Finite arguments do not generate intermediate Overflow, Underflow, or Invalid from a chosen formula; only the final result's projection contributes range and exactness flags.

`scale_pow2(x,n)` rounds the exact value `x * 2^n` once. The whole mathematical value of the signed integer n participates, without narrowing through a host integer or overflowing exponent arithmetic. A zero or infinity is returned with its sign and no flags; NaNs propagate normally. The function shall classify the whole exponent and deliver its final projection/status within the selected allocation-free basic capability. `compose(x,n)` is the same operation under the same policies.

### 3.3 Decomposition and integral-valued rounding

For finite nonzero binary x, `decompose(x)` returns `Finite(m,e)` with exact `x = m * 2^e`, `1/2 <= abs(m) < 1`, and m's sign equal to x's. Subnormal inputs are normalized in this result without rounding. Either zero returns `Finite(original_zero,0)`. Infinity returns `Infinite(original_representation)` and either NaN returns `NaN(original_representation)`. No case quiets a NaN or generates an FP flag. The nonfinite alternatives do not fabricate a finite fraction/exponent.

`compose(m,e)` accepts arbitrary m, not only a decomposition's significand. It follows scaling, including overflow and underflow. For every finite binary x, composing the two fields from `decompose(x)` under the unmodified contract reproduces x exactly, including its zero sign.

`round_to_integral(x,R)` projects x to the mathematical integers under the explicitly supplied R, then stores the integral value in the same F. R overrides only that rounding choice; the remaining controls come from its MathPolicy. A nonintegral finite input generates Inexact; integral finite inputs do not. A zero result has x's sign. Infinity preserves its sign and generates no flag. NaNs propagate normally. This operation does not narrow through an integer type and has no finite-input Overflow or Underflow in the baseline binary formats. It is distinct from `try_exact_cast` or `try_checked_cast` to an integer destination.

### 3.4 Minimum and maximum

All four operations use operand order `(x,y)` for NaN selection and have no finite-input rounding, Inexact, Overflow, or Underflow event.

| Condition | `minimum` / `maximum` | `minimum_number` / `maximum_number` |
| --- | --- | --- |
| Neither operand is NaN | Select the lesser / greater numeric operand. | Same. |
| Exactly one operand is NaN | Propagate that NaN, quieting if necessary. | Select the non-NaN operand, even when the ignored NaN is signaling. |
| Both operands are NaNs | Deterministic NaN selection. | Deterministic NaN selection. |

Every signaling NaN generates Invalid even when a number is returned. A quiet NaN alone does not generate Invalid. For two numerically equal zeros with different signs, either minimum selects negative zero and either maximum selects positive zero, independently of rounding mode and operand position. Equal zeros of the same sign preserve that sign. Other numeric ties select the first operand's representation. This also fixes a representation tie in an enabled format having multiple encodings for the same finite value.

For example, report_minimum_number(sNaN, 2) shall deliver value 2 with Invalid; its try form classifies that local event under the selected error mask.

### 3.5 Floating remainders

For finite x and finite nonzero y, define the mathematical quotient `q = x/y` without a floating rounding boundary:

- `remainder(x,y)` uses the integer n nearest to q, breaking an exact tie toward the even integer, then returns exact `x - n*y`.
- `fmod(x,y)` uses n equal to q truncated toward zero, then returns exact `x - n*y`.

The mathematical integer n has unbounded conceptual range. The allocation-free basic capability shall realize this reference even when q exceeds every enabled fixed integer or a floating division would overflow.

With the baseline gradual binary contract these finite remainders are representable exactly in F, independent of the active rounding direction, and generate no flags. An exact zero has x's sign. A nonzero `remainder` may have the opposite sign to x and has magnitude at most `abs(y)/2`. A nonzero `fmod` has x's sign and magnitude strictly less than `abs(y)`.

The exceptional cases are applied in this order:

1. If either input is NaN, use deterministic NaN propagation; signaling NaNs contribute Invalid. The remaining zero/infinity rules in this list are not additionally applied to that NaN case.
2. Otherwise, infinite x or zero y produces canonical qNaN and Invalid. This is not DivideByZero, and does not use the integer `ZeroDivisor` code.
3. Otherwise, infinite y returns the original finite x, including its zero sign, with no flags.
4. Otherwise use the finite reference above, including zero x.

Thus both functions distinguish remainder by truncation from remainder by nearest-even quotient, and neither depends on the integer `%` policy.

## 4. Correct real elementary functions

### 4.1 General reference and boundary rules

The `math.correct` catalogue comprises `exp`, `expm1`, `log`, `log1p`, `log2`, `log10`, `sin`, `cos`, `tan`, `atan`, `atan2`, `asin`, `acos`, and real `pow`. A selected claim shall cover its declared function and format's full encoded finite argument domain under its admitted controls and delivery forms. Finite range reduction shall satisfy that function's result contract. A provider may require explicit temporary resources; exhaustion shall select the stated resource-failure route. A successful result shall retain the claimed correct rounding.

The exact references are respectively the real exponential, exponential minus one, natural logarithm, logarithm of one plus its argument, base-two/base-ten logarithms, and the usual real trigonometric/inverse functions in radians. `asin` selects `[-pi/2,+pi/2]`; `acos` selects `[0,pi]`; `atan` selects `[-pi/2,+pi/2]`. They are projected directly once, not through stored approximations to their defining expressions.

Except for the capability-specific power rules, admitted NaNs follow Section 2.3 before ordinary domain branches. The following table fixes all non-NaN exceptional boundaries for the unary functions. “Rounded” includes the ordinary final-projection flags; other listed exact or exceptional results have only the explicitly stated flags.

| Function / input | Result and status |
| --- | --- |
| `exp(±0)`, `exp(+infinity)`, `exp(-infinity)` | Exactly 1, positive infinity, positive zero, respectively. |
| `expm1(±0)`, `expm1(+infinity)`, `expm1(-infinity)` | Original zero, positive infinity, exactly -1, respectively. |
| `log`, `log2`, `log10` at 1 | Positive zero, no flags. |
| `log`, `log2`, `log10` at either zero | Negative infinity and DivideByZero. |
| `log`, `log2`, `log10` at negative nonzero input, including negative infinity | Canonical qNaN and Invalid. |
| `log`, `log2`, `log10` at positive infinity | Positive infinity, no flags. |
| `log1p(±0)` | Original signed zero, no flags. |
| `log1p(-1)` | Negative infinity and DivideByZero. |
| `log1p(x)` for x below -1, including negative infinity | Canonical qNaN and Invalid. |
| `log1p(+infinity)` | Positive infinity, no flags. |
| `sin`, `tan`, `atan`, `asin` at either zero | Original signed zero, no flags. |
| `cos(±0)` | Exactly 1, no flags. |
| `sin`, `cos`, `tan` at either infinity | Canonical qNaN and Invalid. |
| `atan(±infinity)` | Rounded `±pi/2`. |
| `asin(x)` for `abs(x)>1`, including infinity | Canonical qNaN and Invalid. |
| `asin(±1)` | Rounded `±pi/2`. |
| `acos(x)` for `abs(x)>1`, including infinity | Canonical qNaN and Invalid. |
| `acos(+1)` | Positive zero, no flags. |
| `acos(-1)` | Rounded pi. |
| `acos(±0)` | Rounded `pi/2`. |

All other finite inputs use their real reference, or canonical qNaN with Invalid if outside the stated real domain. In particular, a finite result close to a pole is not treated as an exact infinity merely because a low-precision approximation to pi suggests one. Negative nonzero results that round to zero keep the negative sign; the exact zero identities above are binding.

### 4.2 Two-argument angle

`atan2(y,x)` selects the principal polar angle in `[-pi,+pi]`. For finite nonzero x and y it uses the quadrant of the exact values, followed by one rounding. It does not form a potentially overflowing or underflowing rounded `y/x`. NaNs use operand order `(y,x)`.

The following cases complete its zero/infinity definition. `s` means the stored sign of y, and `s*A` means A with that sign, including a zero sign:

| Non-NaN inputs | Exact angular reference |
| --- | --- |
| y is either zero, x positive or positive zero | `s*0`. |
| y is either zero, x negative or negative zero | `s*pi`. |
| y finite nonzero, x either zero | `s*pi/2`. |
| y finite, x positive infinity | `s*0`. |
| y finite, x negative infinity | `s*pi`. |
| y infinite, x finite | `s*pi/2`. |
| y infinite, x positive infinity | `s*pi/4`. |
| y infinite, x negative infinity | `s*3*pi/4`. |

Overlapping zero/infinity rows agree. A zero reference is exact and has no flags. Each nonzero multiple of pi is rounded directly, with Inexact when the destination cannot represent it. These cases never generate DivideByZero merely because an internal ratio would divide by zero.

### 4.3 Real power and restricted nonfinite capability

For finite positive x, `pow(x,y)` has the exact real reference `exp(y*log(x))`, with one final projection. This is not a sequence of rounded library calls. For finite negative nonzero x, y must be an exact integral value; the magnitude is `abs(x)^y`, with a negative sign precisely for odd y. A finite negative nonzero base with a nonintegral exponent produces canonical qNaN and Invalid.

Integrality and oddness refer to the exponent's encoded mathematical value. A conversion through `i32`, `i64`, or any bounded host type is not permitted to change their classification. In particular, sufficiently large encoded integral exponents can all be even without fitting a host integer.

For finite arguments, zero exponent, including either signed zero, returns exactly 1 for every base, including either zero. For nonzero finite y and a zero base, positive y returns zero and negative y returns infinity with DivideByZero. The result is negative only when the base is negative zero and y is an odd integer; all other zero-base cases have positive sign. There is no Invalid event merely because a finite nonintegral exponent is applied to negative zero. These cases have no additional Overflow, Underflow, or Inexact event.

A provider accepting any nonfinite power input must select `math.correct.pow.nonfinite` with a complete versioned special-value table. Without it, any NaN or infinity argument gives `UnsupportedDomain(NonFiniteInput)` before arithmetic NaN handling. The table enumerates both input classes/signs, integral/odd exponent categories where applicable, chosen value bits or reference, and local flags. It shall preserve every finite-input rule and shall report Invalid for each signaling-NaN input even if an explicitly defined identity returns a number. No other nonfinite result is inferred from the finite formula, a host `pow`, or a general claim of IEEE support.

## 5. Explicit approximate mathematics

### 5.1 Policies, bounds, and reports

An approximation provider exports an immutable `ApproximationRef<F>` identifying one function, format, algorithm/version, admitted domain, supported controls, achieved bound, and status-observability contract. The reference is a nonowning, nonthrowing-copy borrow valid for the call. Its `identity()` observer returns `ApproximationIdentity`, an opaque equality-comparable, copyable token that carries no dereference authority. Provider exports and their descriptor establish such references; obtaining one does not create a global registry or a hidden allocation service.

The public approximation types are:

| Type | Public content |
| --- | --- |
| `ApproxBound<F>` | Tagged alternatives `Ulp(usize steps)`, `Absolute(F maximum)`, `Relative(F maximum, F absolute_floor)`, and payloadless `HardwareNative`. |
| `ApproxPolicy<F>` | `ApproximationRef<F> implementation`, `ApproxBound<F> requested_bound`. It has no implicit/default implementation. |
| `ApproxStatus` | Tagged alternatives `Observed(NumericStatus status)` and payloadless `Unobservable`. |
| `ApproxReport<F>` | `F value`, `ApproxBound<F> bound`, `ApproximationIdentity implementation`, `ApproxStatus status`. |

A finite bound field means its exact encoded value, must be finite and nonnegative, and treats either zero sign as a zero bound. The reported bound shall be no weaker than the request and shall apply to the returned value on the selected admitted domain. A relative bound uses the `max` formula of Section 2.5; its absolute floor is always explicit. `Ulp` counts adjacent steps between numerically ordered finite values, treating the two zeros as one numerical position. A contract covering infinities or NaNs separately specifies their permitted output representation and does not count them as finite lattice steps. A Ulp request shall provide a representable usize count. A caller requiring another quantitative domain shall select a supported bound alternative.

`HardwareNative` expressly requests the selected provider's native result contract without a quantitative error promise. It does not fulfill a finite Ulp/Absolute/Relative request by assertion. Bound comparison uses the advertised domain and exact mathematical inequalities; comparing field names alone is insufficient. A provider may accept only the bounds it actually supports.

Malformed bound fields give `UnsupportedPolicy(InvalidBound)`. An unattainable requested bound gives `UnsupportedPolicy(UnsupportedAccuracy)`. A policy for another function/format gives `UnsupportedPolicy(WrongFunction)`. Unsupported runtime controls give `UnsupportedPolicy(UnsupportedControl)`. Static impossibilities are `ERROR` under the normal diagnostic rules. Runtime policy admission precedes input-domain admission; neither stage creates arithmetic flags.

### 5.2 Delivery and numerical status

For any real elementary reference `op` in Section 4, an approximation claim may provide one or more of `approx_op`, `report_approx_op`, and `try_approx_op` with that function's original value parameters followed by a required `ApproxPolicy<F>`. This claim shall bind its own supported formats, controls, delivery forms, and provider dependencies. The corresponding correctly rounded implementation shall remain a separately selected claim. Section 8 defines the complete signatures. An unqualified `op` call shall bind the catalogue's correctly rounded entry.

A successful report returns the numerical result, fulfilled bound, selected implementation identity, and exact status-observability alternative. Its reference is the corresponding mathematical function and the same input values, with exceptional cases explicitly fixed by the selected approximation contract. Outside-domain input uses `OutsideApproximationDomain`, or `NonFiniteInput` when nonfiniteness itself is excluded. The function shall use that selected provider and fulfill the admitted requested bound.

An `Observed` contract defines every operation-local NumericStatus field and its relationship to that approximate function. It does not claim the correctly rounded function's flags merely because hardware happened to set them. Report/result delivery and sticky merging follow Section 2.4 for that declared local status.

For an Unobservable contract, report_approx_op shall return Unobservable and preserve its caller's selected status through that requested report boundary. try_approx_op shall reject it with UnsupportedPolicy(StatusUnavailable), because NumericResult requires local status. A value-only approx_op shall accept an empty captured trap mask and execute its declared Native environment/result contract; a nonempty mask fails UnsupportedPolicy(UnsupportedControl). That value-only call requires no ordinary flag collection or context-isolation wrapper. A caller requiring isolation shall select the explicit boundary from Chapter 21.

On normal return the ApproxReport owns no provider reference or temporary computation storage. An identity token and fixed-size bound remain readable after the borrowed provider object ceases to exist. These records do not permit later provider invocation through that token.

## 6. Complex elementary mathematics

### 6.1 Principal finite-input functions

`complex_sqrt`, `complex_log`, and `complex_exp` accept and return `complex<F>`. Each selected standard entry shall bind its declared component format, controls, delivery, resources, and `correct` accuracy contract. A provider offering a weaker bound shall expose that bound through its distinct approximation/provider interface. Ordinary Complex representation and arithmetic shall retain their independent claims.

For finite inputs, the reference is the exact analytic principal function, with real and imaginary components projected separately under the captured component modes. There are no incidental rounded scalar intermediates. Flags are the union of final component projections and explicitly required special events. The principal argument `Arg(z)` uses the exact angular reference of Section 4.2, including both component zero signs; it is not a stored, rounded `atan2` result subsequently used as an exact angle.

Principal square root has nonnegative real part. Its imaginary component has the input imaginary sign when that component is zero or determines the side of the negative-real cut. In particular:

| Finite input | Exact component references / zero signs |
| --- | --- |
| `complex_sqrt(x, ±0)` with x positive | `(sqrt(x), ±0)`. |
| `complex_sqrt(-x, ±0)` with x positive | `(+0, ±sqrt(x))`. |
| `complex_sqrt(±0, ±0)` | `(+0, zero with the input imaginary sign)`. |
| `complex_log(x, ±0)` with x positive | `(log(x), ±0)`. |
| `complex_log(-x, ±0)` with x positive | `(log(x), ±pi)`. |
| `complex_log(+1, ±0)` | `(+0, ±0)`, exact. |

In general, `complex_log(z)` has exact real reference `log(sqrt(real(z)^2 + imag(z)^2))` and imaginary reference `Arg(z)`. This magnitude and logarithm are exact reference expressions, not a requirement to overflow an intermediate norm or round a stored hypot. For any signed complex zero, its real result is negative infinity with real-component DivideByZero; its imaginary result is the angular reference for those zero signs, rounded as necessary. The infinity is a pole result, not Overflow.

`complex_exp(x+iy)` has exact components `exp(x)*cos(y)` and `exp(x)*sin(y)`. For finite x and either imaginary zero, its imaginary result is that original signed zero, even when rounding its real component overflows. For finite x and y, neither component acquires Invalid from an internal zero-times-infinity formula. `complex_exp(±0,±0)` has exact real value 1 and the input imaginary zero sign. Other nonzero components that underflow keep their mathematical signs. Exact real zeros from these finite references are positive unless a preceding explicit branch convention assigns another sign; explicit imaginary-zero conventions take precedence over a generic cancellation rule.

### 6.2 Principal power, zero bases, and nonfinite inputs

`complex_pow(z,w)` under `math.complex.power` uses the exact reference `exp(w*Log(z))` for finite nonzero z and finite w, with principal Log and one final projection per component. Selecting `scalar_steps` explicitly instead introduces the Complex chapter's declared component-rounding boundaries; the descriptor shall identify the scalar sequence, the handling of nonfinite intermediate values, and its resulting flags. It cannot advertise that sequence as the exact principal contract. In its detailed report, intermediate mathematical-operation events accumulate in `common_status`, while final component projection events remain in the corresponding component status. No incidentally chosen implementation instruction adds an event absent from that declared sequence.

For an exact zero exponent and finite nonzero base, the principal result is exactly `(1,+0)`. Otherwise write the exact principal logarithm as `(L,theta)` and the exponent as `(a,b)`, and form exact `u = a*L - b*theta` and `v = a*theta + b*L`. The zero sign of L at unit magnitude is positive; theta uses the principal argument's zero sign. Exact zero products and sums in u and v follow the Complex chapter's sign rules, with the respective captured component rounding direction for cancellation; this determines signs without introducing a rounding boundary or an intermediate FP event. The final references are `exp(u)*cos(v)` and `exp(u)*sin(v)`. A real component that is mathematically zero has positive sign. An imaginary component that is mathematically zero has v's sign, including its assigned exact-zero sign; a nonzero mathematical component rounded to zero instead has that component's mathematical sign. These are CPN26 principal-power zero conventions, not an inference from a host complex routine.

A zero base requires a separate complete function-specific table, registered as `math.complex.power.zero_base`, covering every finite exponent class and all base/exponent zero signs. In its absence the outer Result returns `UnsupportedDomain(UnsupportedSpecialCase)`. Supplying that table does not authorize nonfinite inputs.

Any complex function admitting a nonfinite component needs its own versioned `math.complex.extended` entry. It covers all combinations of real/imaginary finite, zero, infinity, quiet-NaN, and signaling-NaN classes and signs that the function accepts; specifies component result references or bits, NaN selection, component/common flags, and any identity exceptions; and preserves the finite baseline. Signaling behavior must be explicit, rather than inherited from a host ABI. Absent the entry, nonfinite input gives `UnsupportedDomain(NonFiniteInput)` by representation-only inspection, including for a signaling NaN.

For power, nonfinite classification has priority over the finite zero-base capability test. A provider that accepts nonfinite cases but excludes a particular finite zero case uses the zero-base rule for that finite input. Capability rejection is a library-domain event and does not invent a Complex arithmetic NaN result. A supported finite invocation does not fail merely because no extended entry exists.

## 7. Constants and interval extensions

The constants are ordinary explicitly typed, immediately evaluated generic functions named `pi<F>()`, `tau<F>()`, `e<F>()`, `ln2<F>()`, and `sqrt2<F>()`. Each also accepts one explicit `RoundingMode`. Their references are respectively pi, twice pi, the base of the natural logarithm, the natural logarithm of two, and the positive square root of two. Each constant is projected directly to F, independently; `tau<F>()` is not multiplication of an already rounded `pi<F>()`.

An omitted mode is NearestTiesEven. The mode shall be available during immediate evaluation. The function shall project its mathematical reference directly to F under that mode, independently of runtime controls and status. An unsupported format/mode is ERROR.

For example, the signature of pi uses the existing grammar:

```cpn
generic<type F>
declare consteval F pi(
    std::numeric::RoundingMode rounding(
        std::numeric::RoundingMode::NearestTiesEven));
```

Its availability constraint is the enabled constant/format capability; the other four functions have the same signature. The explicit format is required because it does not appear in a value parameter from which ordinary generic inference could infer it.

An optional interval provider shall publish its Interval<F> interface and function capabilities. A correct-enclosure claim shall provide directed endpoints whose closed interval contains every admitted exact reference.

## 8. Source-visible catalogue

### 8.1 Representation and basic functions

Every name in this table is qualified by `std::math::`. A trailing `MathPolicy` defaults to `MathPolicy()`. A basic arithmetic row defines the listed value form and the identically parameterized `report_` and `try_` forms. Their return types are respectively `MathReport<F>` and `std::numeric::NumericResult<F>`. Each callable form shall require the corresponding declared delivery claim.

| Value parameters | Value name(s) | Value result | Additional requirement |
| --- | --- | --- | --- |
| `(F x)` | `is_nan`, `is_signaling_nan`, `is_infinite`, `is_finite`, `is_normal`, `is_subnormal`, `is_zero`, `signbit` | `bool` | Representation capability; no report/try forms. |
| `(F x)` | `classify` | `FPClass` | Representation capability; no report/try forms. |
| `(F x, F y)` | `copy_sign` | F | Representation capability; no report/try forms. |
| `(F x, F y)` | `total_order`, `representation_equal` | `bool` | Representation capability; no report/try forms. |
| `(F x)` | `decompose` | `Decomposition<F>` | Enabled binary decomposition and i32; no report/try forms. |
| `(F x, MathPolicy policy)` | `next_up`, `next_down`, `sqrt` | F | Named `math.basic` operation. |
| `(F x, F y, MathPolicy policy)` | `hypot`, `minimum`, `maximum`, `minimum_number`, `maximum_number`, `remainder`, `fmod` | F | Named `math.basic` operation. |
| `(F a, F b, F c, MathPolicy policy)` | `fma` | F | Named `math.basic` operation. |
| `(F x, I exponent, MathPolicy policy)` | `scale_pow2`, `compose` | F | I is an enabled fixed-width signed integer. |
| `(F x, RoundingMode rounding, MathPolicy policy)` | `round_to_integral` | F | Explicit rounding argument is required. |

For example, minimum's value, report, and Result claims shall share its mathematical reference while independently binding their delivery requirements. Inspection functions shall return their representation observation directly.

### 8.2 Correct real and complex functions

For each real row, the value form returns F; `report_op` returns `Result<MathReport<F>,MathError>`; and `try_op` returns `Result<NumericResult<F>,MathError>`. A provider shall claim each supported delivery form with its formats and controls. Trailing controls/resources default to `MathPolicy()` and `MathResources()`.

| Names | Parameters |
| --- | --- |
| `exp`, `expm1`, `log`, `log1p`, `log2`, `log10`, `sin`, `cos`, `tan`, `atan`, `asin`, `acos` | `(F x, MathPolicy policy, MathResources resources)` |
| `atan2` | `(F y, F x, MathPolicy policy, MathResources resources)` |
| `pow` | `(F x, F y, MathPolicy policy, MathResources resources)` |

For each complex row, the value form returns `complex<F>`; `report_op` returns `Result<ComplexMathReport<F>,MathError>`; and `try_op` returns `Result<NumericResult<complex<F>>,MathError>`. Trailing controls/resources default to `ComplexMathPolicy()` and `MathResources()`.

| Names | Parameters |
| --- | --- |
| `complex_sqrt`, `complex_log`, `complex_exp` | `(complex<F> z, ComplexMathPolicy policy, MathResources resources)` |
| `complex_pow` | `(complex<F> z, complex<F> w, ComplexMathPolicy policy, MathResources resources)` |

A whole-function report always exists before selecting a NumericResult outcome. A component numeric failure does not erase the other component from the report form, but a failed NumericResult never provides a partially readable complex value. `report_complex_sqrt` and `try_complex_sqrt` therefore have intentionally different nested payloads.

### 8.3 Approximation functions

For each real catalogue reference op in Section 8.2, the approximation signatures retain its original F value parameters, then take `(ApproxPolicy<F> approximation, MathPolicy policy, MathResources resources)`. Their availability shall follow the approximation claim independently of the corresponding correct entry. The last two parameters have their ordinary defaults. The required approximation policy shall be supplied explicitly. The names and results are:

| Name | Return type |
| --- | --- |
| `approx_op` | F |
| `report_approx_op` | `Result<ApproxReport<F>,MathError>` |
| `try_approx_op` | `Result<NumericResult<F>,MathError>` |

Thus the binary approximate angle takes `(F y, F x, ApproxPolicy<F>, MathPolicy, MathResources)` and approximate power takes `(F x, F y, ApproxPolicy<F>, MathPolicy, MathResources)`. A provider does not add arbitrary unnamed overloads to satisfy these catalogue entries. A capability descriptor declares which entries it supplies and binds its ApproximationRef to that exact entry.

All result types in these catalogues are ordinary concrete library identities. For example, `try_log` does not change between a bare NumericResult and a nested Result depending on the selected provider or whether a runtime path allocated. A caller inspects the outer Result before its inner numeric-result alternative.

## 9. Normative boundary examples

These examples assume the named capabilities, binary f64, gradual subnormals, and the default Result error mask. A report suppresses its own numeric trap; it does not suppress failures in argument expressions.

| Operation | Required result |
| --- | --- |
| `report_minimum_number(sNaN, 2)` | Value 2 and local Invalid. |
| `try_minimum_number(sNaN, 2)` | NumericResult Err selected by Invalid; no readable value. |
| `report_minimum(-0, +0)` / `report_maximum(-0, +0)` | Negative zero / positive zero; no flags. |
| `report_remainder(3, 2)` / `report_fmod(3, 2)` | -1 / +1; no flags. |
| `report_remainder(5, 2)` / `report_fmod(5, 2)` | +1 / +1; no flags. |
| Either remainder operation with finite x and zero y | Canonical qNaN and Invalid, not DivideByZero. |
| Either remainder operation with x = negative zero and nonzero finite y | Negative zero; no flags. |
| `report_next_up(M)` for maximum finite M | Positive infinity; no Overflow or Inexact. |
| `report_fma(+0, +infinity, qNaN)` | The propagated qNaN and Invalid. |
| `report_hypot(+infinity, sNaN)` | Positive infinity and Invalid. |
| `try_log(-1)` | Outer Ok containing NumericResult Err selected by Invalid. |
| `try_pow(+infinity, 2)` without a nonfinite-power entry | Outer Err with `UnsupportedDomain(NonFiniteInput)`; no invented FP event. |
| `try_complex_pow((+0,+0), (1,+0))` without a zero-base entry | Outer Err with `UnsupportedDomain(UnsupportedSpecialCase)`. |

The shorthand numeric arguments in this table denote already bound values of the same F, not permission for hidden implicit integer/floating conversion. The following source uses ordinary declarations and qualified generic constant calls:

```cpn
import std.math;

f64 a(-0.0);
f64 b(std::math::sqrt(a));
f64 c(std::math::hypot(a, a));
f64 p(std::math::pi<f64>());
auto report(std::math::report_minimum(a, c));

complex<f64> z(-4.0, -0.0);
auto root(std::math::complex_sqrt(z));
auto checked_log(std::math::try_complex_log(z));
```

Here b preserves negative zero, c is positive zero, and the principal root has positive-zero real component and imaginary value -2. `checked_log` first exposes MathError versus completed computation and, on outer success, the distinct NumericResult status/value alternative. The selected capabilities and resources determine the support required by these calls.

