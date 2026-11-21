<a id="chapter-05-complex-arithmetic"></a>

# CPN26 Complex Arithmetic Specification

## 1. Complex feature contract

This chapter defines the Cartesian `complex<T>` representation and its arithmetic deltas for enabled fixed binary/decimal T. [Numeric integration](04_numeric_integration.md#chapter-04-numeric-integration) owns scalar projection, controls, status, NaN selection, and delivery. [Configuration](08_runtime_configuration.md#chapter-08-runtime-configuration) selects the ordinary Complex and scalar execution profiles. [Mathematical functions](18_mathematical_functions.md#chapter-18-mathematical-functions) supplies elementary principal functions separately.

Complex shall be an optional standardized capability under the [core conformance model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance). Its representation, scalar-step arithmetic, component-exact arithmetic, observation, and elementary-function claims shall be selected independently. Materializing a complex object shall require its representation and the construction/conversion operations actually used. An arithmetic expression shall additionally require its selected operation, component format, controls, and delivery claim. Section 12 defines the resource contract for a selected stronger operation.

The implementation shall select the operation/profile pair before evaluation:

| Selected operation | Applicable arithmetic contract |
| --- | --- |
| `component_exact` | Finite references in Section 4, zero signs in Section 5, and nonfinite dispatch in Sections 6-8. This is an explicit stronger accuracy contract. |
| `scalar_steps` with observed scalar execution | The scalar graphs in Section 11.2 for finite arithmetic, Sections 6-8 for nonfinite dispatch, and selected local-status delivery. |
| `scalar_steps` with Native scalar execution | The scalar graphs in Section 11.2 applied through the Native provider for all prepared inputs, with that provider's admitted transformations, special values, and unobserved events. |
| Explicit report/try/checked | The corresponding selected value algorithm with an observed scalar operation contract and Section 9's report aggregation. |

Ordinary Native scalar steps require no complete-operation flag collection or nonfinite repair pass. A selected `component_exact` or named observed interface shall realize its own stronger function. Representation operations retain their specified bit behavior under every arithmetic selector.

## 2. Representation and construction

For a claimed fixed-format representation, `complex<T>` shall contain two inline objects of the same scalar type `T`, in declaration order:

```text
T real;
T imag;
```

The standard layout shall place `real` at offset zero and `imag` at `sizeof(T)`, with size `2 * sizeof(T)` and alignment `alignof(T)`. Scalar padding remains scalar padding; the two scalar objects constitute the complete Complex representation.

Foreign transport shall bind both this representation and the selected calling convention through its explicit ABI descriptor.

Examples:

```cpp
complex<f64> position(3.0, 4.0);
complex<f32> coefficient(1.0, -0.0);
complex<f64> origin(0.0, 0.0);
auto product(position * position);
```

Two-component construction shall directly initialize the scalar subobjects under their selected conversion rules. Storing same-format components is a representation transfer, including for infinity and signaling NaN.

The initializers shall evaluate once in declaration order. Same-format construction and copy shall preserve both scalar encodings, including zero signs and signaling-NaN bits. The core construction and lifetime model supplies their object transitions.

One-real-argument construction shall initialize the imaginary component to positive zero. Typed default construction shall use two scalar positive-zero encodings from their representation provider.

Direct component access shall follow the core subobject lifetime, pointer, and aliasing model.

## 3. Binding, mixed operands, and conversions

### 3.1 One component format per operation

An ordinary binary operation on `complex<A>` and `complex<B>` uses `complex<C>`, where `C` is the existing permitted scalar common type. The common type is selected from enabled formats using the complete finite-value inclusion rule, including subnormals.

Typed cross-family operands shall use their scalar family's explicit conversion rules. A missing or ambiguous common format requires an explicit conversion or destination.

A real operand from the same permitted floating family may participate through the corresponding scalar common type and a lift to `(real,+0)`. An untyped numeric literal can bind to the component format according to existing literal rules. This is one specified lift, not a second arithmetic model for real arguments.

Examples, assuming the relevant capabilities are enabled:

```cpp
complex<f32> z(1.0, 2.0);
f32 scale(2.0);
auto doubled(z * scale);
auto shifted(z + 1.0);
```

A typed integer operand shall enter the floating family through an explicit admitted conversion.

### 3.2 Operand preparation

After source evaluation, the operation shall prepare any required format conversions in order `left.real`, `left.imag`, `right.real`, `right.imag`. Same-format preparation preserves each component's representation. Converted components use their selected scalar conversion; the ensuing algorithm consumes those prepared encodings.

An observed invocation shall include preparation events in its own operation scope and report. If preparation quiets an sNaN, subsequent selection sees the prepared qNaN while the recorded preparation event remains. Native preparation uses the provider's ordinary conversion contract with unobserved events. Argument-expression effects precede this operation-owned preparation under the core call model.

### 3.3 Complex-to-complex conversion

Conversion to complex<U> shall apply the selected scalar conversion to real and then imaginary components. Named Checked and Exact conversions shall retain Chapter 04's acceptance predicates.

The corresponding try_checked_cast<complex<U>> and try_exact_cast<complex<U>> shall return NumericResult<complex<U>>. Both scalar projections shall complete before result selection. The result status shall union their flags and OR their Boolean event fields. If either projection fails, the error code shall come from the first failing component in real/imaginary order. Otherwise the operation shall directly construct the two-component destination. This conversion-error order is separate from arithmetic event-mask priority.

A caller requiring each component's separate failure/status shall explicitly invoke the corresponding scalar conversions on z.real and z.imag. An Exact probe shall preserve ambient status under Chapter 04. A returning failed assignment shall preserve its existing destination; prior operand effects remain complete.

### 3.4 Complex-to-real conversion

A scalar conversion from Complex shall select an explicit interface. try_checked_cast<U> and try_exact_cast<U> shall return NumericResult<U>. They shall first inspect the imaginary representation for numerical zero, admitting either zero sign. A nonzero, infinite, or NaN imaginary component shall return Err(InvalidOperation) with empty NumericStatus while preserving the representation and ambient FP status. On zero, the operation shall apply the selected scalar conversion to the real component and return its result. The matching value interfaces use Chapter 04's delivery.

Direct z.real access selects that component independently of this whole-value conversion predicate.

## 4. Finite arithmetic and result precision

Let `z = (a,b)` and `w = (c,d)` contain finite values of the prepared scalar format. Let `Rr` and `Ri` be the real and imaginary rounding modes. By default both equal the operation's resolved scalar rounding mode; an explicit operation may supply a pair.

A selected `component_exact` operation shall use the corresponding exact mathematical reference in this table:

| Operation | Exact real component | Exact imaginary component |
| --- | --- | --- |
| `z + w` | `a + c` | `b + d` |
| `z - w` | `a - c` | `b - d` |
| `z * w` | `a*c - b*d` | `a*d + b*c` |
| `z / w`, with nonzero `w` | `(a*c + b*d)/(c*c + d*d)` | `(b*c - a*d)/(c*c + d*d)` |

Each exact output component is rounded directly into `T` once. Arithmetic internal to these definitions has no finite-format intermediate overflow, underflow, or Inexact event. The final component roundings produce the applicable flags using the established scalar rules, including tininess-after.

Exact finite division shall classify a zero divisor from c and d themselves. A nonzero subnormal divisor shall take the nonzero-divisor reference regardless of internal arithmetic choices.

Each component shall independently receive its prescribed projection and status, including Overflow for an out-of-range reference.

Examples with `M` the maximum finite scalar, `t` the minimum positive subnormal, and nearest-even rounding:

| Operation | Result | Local flags |
| --- | --- | --- |
| `(M,M)/(M,M)` | `(1,+0)` | None. |
| `(t,t)/(t,t)` | `(1,+0)` | None. |
| `(M,M)/(1,1)` | `(M,+0)` | None. |
| `(M,M)*(M,-M)` | `(+Infinity,+0)` | Overflow and Inexact for the real component only. |
| `(t,t)*(1/2,1/2)` | `(+0,t)` | None. |

The exactness boundary is one complex operator. In z*w+v the product shall project before the addition. Optimization shall preserve these selected values and observations unless the caller explicitly selects a contract admitting another graph.

A component_exact claim shall identify each supported operation, component format, control combination, and delivery form. Within that claim, the provider shall deliver the specified projections and selected status throughout the admitted input domain. Its mathematical reference shall determine the required result; the provider may select any algorithm satisfying that result and its published resource contract.

## 5. Exact signed-zero rules

An exact finite intermediate carries a mathematical value and, if that value is zero, a zero-sign bit.

1. A zero product has the XOR of the two operand sign bits.
2. Subtraction negates the second exact operand before addition, including its zero sign.
3. Exact addition of two same-sign zeros preserves that sign.
4. Any other exact sum equal to zero, including nonzero cancellation or opposite-sign zeros, is negative zero only under toward-negative rounding; it is positive zero under the other four standard modes.
5. Each result component uses its own rounding mode when applying rule 4.
6. In finite complex division, the exact denominator is strictly positive, so an exactly zero numerator retains its sign in the quotient.
7. A nonzero exact result rounded to zero uses the sign of that nonzero result. This is distinct from an exactly zero result.

These rules apply to the specified exact component formulas, including finite axis denominators. No extra division-by-one or multiplication-by-one identity rule overrides them.

For finite nonzero `z`, `z/z` is numerically `(1,0)`. Under toward-negative, its imaginary zero can be negative. Likewise, `(1,-0)*(1,+0)` has imaginary positive zero under nearest-even. Numerical identities are not blanket bit-preserving transformations.

Bitwise conjugation and copying are defined separately in Section 10. They retain their precise representation guarantees.

## 6. Classification and NaN selection

Classification reads the prepared representation without arithmetic. Each scalar is finite (including either zero), positive/negative infinity, quiet NaN, or signaling NaN.

For a complex value:

- `is_zero` means both components are numerical zero.
- `is_finite` means both components are finite.
- `has_infinity` means at least one component is infinite.
- `has_nan` means at least one component is NaN.

The last two properties can both be true. Classification shall retain each component's NaN and infinity information for the selected special-case dispatch.

The implementation shall apply Chapter 04's deterministic propagation algorithm to the ordered prepared components `(a,b,c,d)`. If an input NaN is selected, multiplication/division shall return that selected quiet NaN in both components and place signaling-input Invalid in common status. This selected branch completes the operation; other branches contribute no events. The canonical generated quiet NaN Q and payload mapping are those of Chapter 04.

Addition and subtraction shall select NaNs independently for (a,c) and (b,d). Subtraction shall select from the original operand encodings before the numeric sign negation, preserving the selected NaN sign under Chapter 04.

## 7. Multiplication with nonfinite inputs

The following ordered branches define `z*w` after component preparation:

1. Apply the global NaN selection in Section 6. If selected, return immediately.
2. If all four components are finite, use the exact finite operation in Section 4.
3. If one entire complex operand is zero and the other has an infinity, return `(Q,Q)` with operation-common Invalid.
4. Otherwise evaluate the extended products and sums defined below.

### 7.1 Extended product convention

For each of the four terms `a*c`, `b*d`, `a*d`, and `b*c` in branch 4:

- If either factor is zero, produce exact signed zero with XOR sign, even when the other factor is infinite.
- Otherwise, if either factor is infinite, produce an infinity with XOR sign.
- Otherwise produce the exact finite product, without rounding into `T`.

This zero-term convention belongs only to branch 4 of the complex operation. It does not change scalar `0*Infinity`, and it does not bypass the entire-zero-operand rejection in branch 3.

Compute the real difference and imaginary sum from these extended terms:

- Opposite-sign infinities in an addition produce `Q` and Invalid for that result component.
- Same-sign infinities, or an infinity combined with a finite term, produce the indicated infinity without a new range event.
- Finite exact sums use Section 5 zero signs and one final rounding into `T`.

NaN generated in one result component does not cause a second global input-NaN propagation pass over the other output.

### 7.2 Consequences

| Inputs | Result under nearest-even | Local flags |
| --- | --- | --- |
| `(Infinity,2)*(1,+0)` | `(Infinity,2)` | None. |
| `(Infinity,2)*(+0,1)` | `(-2,Infinity)` | None. |
| `(+0,+0)*(Infinity,2)` | `(Q,Q)` | Invalid. |
| `(Infinity,+0)*(+0,Infinity)` | `(+0,Infinity)` | None. |
| `(Infinity,Infinity)*(1,1)` | `(Q,Infinity)` | Real Invalid. |
| `(Infinity,Infinity)*(1,-1)` | `(Infinity,Q)` | Imaginary Invalid. |

The first two cases explain why a blanket replacement of every finite companion component by zero is not a suitable default: it loses known values. Conversely, an indeterminate infinity cancellation is not converted into a claimed exact finite zero.

## 8. Division: complete ordered dispatch

Let prepared inputs be `(a,b)` and `(c,d)`. Evaluate the branches in the order written; the first matching branch determines the result. Helper calculations that are described as exact do not expose intermediate FP flags.

### D1. Input NaN

Apply Section 6 global NaN selection and return if it selects a NaN.

### D2. All finite, nonzero divisor

If all four components are finite and `(c,d)` is not complex zero, use the exact finite quotient. This branch includes all finite real-axis and imaginary-axis denominators, so their zero signs follow the uniform finite formulas.

### D3. Complex-zero divisor

If `c` and `d` are both numerical zero:

- If `a` and `b` are also both zero, return `(Q,Q)` with common Invalid.
- Otherwise treat `c` as the selected directed real-axis zero. For each numerator component `x`, XOR its sign with the sign of `c`:

| Numerator component `x` | Result component | Component flag |
| --- | --- | --- |
| Either signed zero | The resulting signed zero | None. |
| Finite nonzero | Infinity with the resulting sign | DivideByZero. |
| Either infinity | Infinity with the resulting sign | None. |

The sign of the imaginary divisor zero `d` is not used in this branch. This is an explicit CPN26 convention for a singular complex operation, not an inference about an unspecified path by which a complex value approached zero.

Preserving a zero numerator component here does not redefine scalar `0/0`. Entire complex `0/0` has already selected Invalid.

An infinite numerator with a finite nonzero companion can still generate a component DivideByZero event for that companion. For example, `(Infinity,2)/(+0,+0)` produces `(Infinity,Infinity)` and an imaginary DivideByZero event.

### D4. Real-axis divisor on the nonfinite path

If `d` is zero and `c` is nonzero, return the scalar operations `(a/c,b/c)` with real and imaginary result rounding respectively. Scalar division handles infinity and zero using its established rules.

This preserves independently known components, for example `(Infinity,2)/(1,+0) = (Infinity,2)`.

### D5. Imaginary-axis divisor on the nonfinite path

If `c` is zero and `d` is nonzero, return the scalar operations `(b/d,(-a)/d)`.

The negation of `a` precedes division and its rounding. Computing `a/d`, rounding it, and negating afterward is not generally equivalent under directed rounding.

### D6. Finite numerator, infinite non-axis divisor

If the numerator is finite and the divisor has an infinity, construct two exact direction components:

```text
C = signed 1 if c is infinite; otherwise signed zero with c's sign
D = signed 1 if d is infinite; otherwise signed zero with d's sign

c0 = c if c is finite; otherwise signed zero with c's sign
d0 = d if d is finite; otherwise signed zero with d's sign
```

Compute exact leading and residual terms using the respective result's zero-sign rounding mode:

```text
leading_real = a*C + b*D
leading_imag = b*C - a*D
residual_real = a*c0 + b*d0
residual_imag = b*c0 - a*d0
```

Both output components are zeros. Determine each sign as follows:

1. If its leading term is nonzero, use that sign.
2. Otherwise, if its residual term is nonzero, use the residual sign.
3. Otherwise, use the leading term's exact zero sign from Section 5.

This branch raises no new Underflow or Inexact: the zeros come from the chosen infinity extension, not finite-format rounding of a small nonzero quotient.

Using unit coefficients for infinite inputs is a zero-sign convention. It does not assert that two stored infinities reveal the magnitudes or growth rates of their pre-overflow sources.

The residual matters: `(0,-1)/(Infinity,2)` returns `(-0,-0)`, while a direction-only calculation could lose the real zero's sign. Likewise, `(1,+0)/(Infinity,1)` returns `(+0,-0)`.

### D7. Infinity in both numerator and divisor, remaining non-axis cases

Return `(Q,Q)` with common Invalid. Equal infinity encodings are not evidence that the original magnitudes were equal; this branch does not simplify an infinity-containing self-division to one.

Axis branches have already taken precedence. For example, `(Infinity,2)/(Infinity,+0)` returns `(Q,+0)` with real Invalid through D4, preserving its known imaginary result.

### D8. Infinite numerator, finite non-axis divisor

At this point the numerator has an infinity and `c,d` are finite and both nonzero. Let `A,B` map infinite numerator components to signed one and finite numerator components to signed zero. Compute:

```text
u = A*c + B*d
v = B*c - A*d
```

For each result component:

- A nonzero exact direction yields an infinity with that sign.
- A zero direction yields `Q` and component Invalid.

Here a cancellation between infinite contributions does not establish an exact zero. For example, `(Infinity,Infinity)/(1,1)` yields `(Infinity,Q)` with imaginary Invalid.

### 8.1 Exhaustiveness

After D1 removes NaN cases, each component is finite or infinite. D2 handles every finite/nonzero quotient; D3 handles every remaining zero divisor; D4/D5 handle axes. In the remaining non-axis domain, either only the denominator is infinite (D6), both operands have infinity (D7), or only the numerator is infinite (D8). No residual case has undefined arithmetic behavior.

The component encoding of any returned NaN is specified by the selected input payload or by canonical `Q`. Flags are defined by the selected branch and final scalar roundings, not by incidental instructions used to implement the branch.

## 9. Observed Complex reports

A selected observed Complex operation shall determine its value and local preparation, real/imaginary, and operation-common events. The public NumericStatus shall combine their Boolean fields by OR and their flags by union:

```text
operation_flags = preparation_flags union real_flags
                  union imag_flags union common_flags
```

Common status records whole-operation conditions such as the global signaling-input rule or complex zero/zero. Each component status records that component's projection/events. The semantic calculation shall attribute each event to its source stage. A function exposing detailed component reports shall use its declared public report type; the ordinary NumericStatus exposes the aggregate.

The completed report shall use [Chapter 04](04_numeric_integration.md#chapter-04-numeric-integration)'s delivery algorithm. `require_finite` succeeds precisely when both components are finite. A report retains each computed component, while a failed NumericResult contains no readable complex value. A returning checked mutation commits the whole selected value after successful classification; this commit is an object update rather than a concurrent two-word atomic store.

Ordinary Native scalar-step execution delivers its provider result without establishing this report. Explicitly requesting a report/try/checked operation selects local observation and its necessary support. Preparation and component calculations shall finish under the selected nontrapping observation scope before that stronger interface selects delivery.

## 10. Equality, ordering, and representation operations

### 10.1 Numeric equality

After permitted type binding, equality shall return true when both component numeric comparisons are true. An observed comparison uses quiet scalar equality: either zero sign compares equal, qNaN compares false, and each sNaN comparison contributes Invalid even when another component already decides the Boolean result. A Native comparison uses its provider's admitted comparison graph and unobserved events.

`z != w` is the logical negation of this completed equality operation. It does not perform a second comparison with different status. Numeric equality is not an identity test for an object containing a NaN.

### 10.2 Explicit ordering and representation equality

Ordered use of Complex shall select an explicit comparator. Numeric equality and the following named representation ordering shall use their separately admitted operation claims.

`total_order_lex` and `representation_equal` require identical component formats and compatible representation contracts. They do not perform the arithmetic operand preparation of Section 3.2 or any implicit common-format conversion. A caller requiring a cross-format comparison shall explicitly convert the operands first; any resulting conversion status belongs to that explicit conversion.

The standard named `total_order_lex` compares real components by the component provider's non-arithmetic total order and, if equal in that order, compares imaginary components the same way. It neither quiets sNaNs nor raises Invalid. Its lexicographic ordering is a container/sorting contract, not a claim that complex numbers possess a compatible real-number ordering.

`representation_equal` compares the two meaningful scalar encodings, including zero signs and NaN class/sign/payload. It excludes unrelated object padding. Whole-object `memcmp` is not substituted as a portable definition when a component representation contains padding or noncanonical encodings. Such encodings follow the selected component provider's declared representation contract.

### 10.3 Copy, unary signs, and conjugation

Same-format copy and unary plus preserve both component representations. Unary minus flips each component's sign field. Conjugation copies the real component and flips only the imaginary sign field. These representation transformations:

- preserve NaN payloads and signaling/quiet class;
- do not generate FP flags;
- preserve or change zero signs exactly as specified;
- do not pass through arithmetic addition, multiplication, or conversion.

Thus applying conjugation twice restores both original component encodings, including an sNaN. Replacing conjugation by a general complex multiplication would not meet this contract.

Mathematical simplifications involving arithmetic still need proof about NaNs, zero signs, rounding, and flags. For example, the existence of a representation-preserving unary plus does not make adding an arbitrary signed-zero complex operand a universal bitwise identity.

## 11. Configurable arithmetic profiles and providers

### 11.1 Exact and ordinary selection

The sole preset table in Chapter 08 selects ordinary Complex/scalar execution. That default shall become an arithmetic capability requirement at the operation's use. A component_exact use shall explicitly select the value and special-case references in Sections 4-8. A Native scalar_steps use shall select the following graph and its Native provider permissions. Function definitions shall retain the operation/profile contract they publish across imports and optimization.

### 11.2 Explicit scalar-step arithmetic

The scalar_steps profile shall instantiate this scalar-operation graph for prepared z=(a,b) and w=(c,d):

| Complex operation | Real graph | Imaginary graph |
| --- | --- | --- |
| z+w | add(a,c) | add(b,d) |
| z-w | sub(a,c) | sub(b,d) |
| z*w | sub(mul(a,c),mul(b,d)) | add(mul(a,d),mul(b,c)) |
| z/w | div(add(mul(a,c),mul(b,d)),add(mul(c,c),mul(d,d))) | div(sub(mul(b,c),mul(a,d)),add(mul(c,c),mul(d,d))) |

With observed scalar execution, finite nodes shall project to T under their component's selected rounding mode. The invocation shall sequence the real graph before the imaginary graph and collect each component's node events before Section 9 delivery. It may share a node when both value and observed event semantics agree. Nonfinite inputs and an actual complex-zero divisor shall instead use Sections 6-8.

With Native scalar execution, the graph shall apply to every prepared input, including nonfinite values and complex zero divisors. Every node shall use its Native provider operation and environment. The compiler may share, contract, reassociate, or otherwise transform nodes within that provider's declared permissions. The invocation shall deliver the target result/fault directly with unobserved arithmetic events.

A denominator rounded to zero within the graph shall use its scalar division behavior. Observed intermediate Overflow, Underflow, Invalid, and Inexact belong to this graph; component_exact uses its separate final-projection reference.

### 11.3 Provider and control binding

A provider shall publish its supported operation/profile, component-format, control, and delivery combinations, together with their permitted value/error behavior, special values, observation capability, and resources. A claim for one combination shall bind exactly its stated dependencies. Custom approximations and Native transformations shall use their published contracts. Finite-input assumptions shall require explicit selection. The compiler shall realize a requested claim or diagnose its absence at that use.

Explicit component rounding or stronger accuracy requirements shall bind their requested capability. Ordinary Native execution has no obligatory software fallback. The bound numerical contract shall identify the relevant operation profile independently from the two-component storage layout.

## 12. Selected resources and decimal representation

### 12.1 Resource binding

Each arithmetic claim shall publish its resource requirements together with its operation, format, controls, and delivery contract. The descriptor shall identify fixed internal storage requirements, any explicitly supplied temporary workspace or resource domain, and the resource-failure outlet. An allocation-free claim shall realize the selected result within its published fixed-storage contract. An allocating claim shall acquire and release temporary storage through its named resource domain under the ordinary numeric resource rules.

A source form with explicit resource arguments shall bind those arguments. An ordinary operator or another source form with no resource argument shall bind either an allocation-free implementation or an explicitly configured resource domain admitted by that claim. Binding shall establish this choice before operand evaluation. Its effect signature and support dependencies shall expose the selected resource behavior.

Returning resource failure shall preserve the destination and retire temporary resources under the selected numeric failure contract. A value interface shall use its stated terminal outlet where that contract selects termination. Successful execution shall deliver the selected mathematical result and status. The provider may choose native primitives, scaling, staged computation, or multiprecision work consistent with this observable contract.

The exact formulas in Section 4 shall define mathematical references. They shall leave intermediate representation and workspace organization to the bound provider. Format support, Complex storage, and scalar-step execution shall retain their independently selected resource requirements.

### 12.2 Decimal component formats

The finite component equations and classification rules apply to enabled decimal floating formats as well, using their scalar rounding and flag contracts. Correct numerical values do not alone select a unique decimal cohort or byte encoding.

The selected scalar decimal provider shall declare a deterministic canonical round-from-exact/cohort rule for newly computed components, including zero exponent selection, and bind it to the profile's representation fingerprint. A Complex operation shall use that declared rule to select the computed representation.

Same-format copying and conjugation shall preserve their specified meaningful bits. A computed component shall use its selected decimal arithmetic provider's declared result/cohort rule.

## 13. Constant evaluation and diagnostics

Complex constant evaluation shall use the selected target operation/profile pair and the canonical numeric rules in Chapter 04. Runtime optimization shall preserve the selected observations or remain within its Native provider permissions. The compiler shall apply Chapter 04's numeric applicability cases and Chapter 08's severity policy. This chapter supplies no separate severity or event-priority table.

## 14. SIMD and GPU delta

A Complex vector lane comprises one real/imaginary pair. Its mask selects that whole pair. Chapter 04's vector contract defines inactive representations, observed active-lane aggregation, Native speculative arithmetic permissions, and reduction behavior. A placement provider shall declare any structure-of-arrays or other transport mapping in addition to the scalar Complex object representation.

## 15. Selected conformance

A provider shall satisfy each operation/profile, format, control, and delivery combination it advertises, together with that combination's declared dependencies and resources. A representation claim shall provide the two-component layout and its selected construction/transfers. A component_exact claim shall satisfy the applicable finite and exceptional references above. A Native claim shall satisfy its versioned operation and transformation descriptor. Foreign transport shall follow the native interoperability contract independently of numerical accuracy.

