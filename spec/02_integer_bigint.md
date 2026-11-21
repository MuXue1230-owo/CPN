<a id="chapter-02-integer-bigint"></a>

# CPN26 Integer and BigInt Specification

## 1. Integer contracts

This chapter owns integer value domains, canonical arithmetic common types, and integer projection policies. [Numeric integration](04_numeric_integration.md#chapter-04-numeric-integration) owns conversion, status, and failure delivery. [Numeric expressions](07_numeric_expressions.md#chapter-07-numeric-expressions) owns expression sequencing and the function catalogue. Execution follows the [core operational model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance); the [configuration specification](08_runtime_configuration.md#chapter-08-runtime-configuration) selects ordinary-operation defaults.

The compiler shall derive an integer operation's source/result types, establish their availability, and resolve its arithmetic policy. Execution shall then evaluate the operands once and apply that policy to their actual mathematical values. A named Checked, Result, Wrapping, or Saturating operation supplies its own policy. The Native policy supplies ordinary Release execution through the preset table.

```cpn
i32 count(10);
u64 mask(255);
auto next(count + 1);
```

Each example requires its displayed type capabilities. The standard language integer names are `iN`, `uN`, `isize`, `usize`, and the explicitly enabled BigInt family. Foreign `int`, `long`, and `short` identities belong to the `ffi` binding catalogue.

## 2. Integer domains and availability

### 2.1 Fixed-width domains

For positive width N, the two fixed integer domains are:

| Type | Mathematical values | Encoding |
| --- | --- | --- |
| `uN` | `0` through `2^N - 1` | N-bit unsigned binary. |
| `iN` | `-2^(N-1)` through `2^(N-1) - 1` | N-bit two's complement. |

The canonical width catalogue is `8,16,32,64,128,...`: powers of two at least eight. A provider may expose additional positive extension widths with their storage, alignment, operations, and ABI contracts. A configured enabled-width set determines which already-derived types can be materialized. Type determination precedes that availability test.

An exported fixed integer's width and signedness identify its value representation. Byte order, serialization, alignment, and foreign call classification follow their respective target contracts. The implementation shall diagnose a required unavailable type at its materialization boundary.

### 2.2 Platform and arbitrary-precision families

`isize` and `usize` use the platform integer domain declared by [native interoperability](09_native_interoperability.md#chapter-09-native-interoperability). BigInt represents mathematical integers under its explicit resource capability. These families retain their nominal identities. A typed operation crossing fixed, platform, or BigInt families shall use the applicable explicit unification interface; matching current values or widths supplies only a possible conversion, not a new overload.

## 3. Canonical arithmetic common types

### 3.1 Type derivation

For two already typed fixed integers, the compiler shall derive the common type by this table, independently of the configured enabled-width set:

| Operand types | Derived type |
| --- | --- |
| Identical types | That type. |
| `iA`, `iB` | `i(max(A,B))`. |
| `uA`, `uB` | `u(max(A,B))`. |
| `iA`, `uB`, with `A > B` | The existing signed operand type `iA`, including an extension width. |
| `iA`, `uB`, with `A <= B` | `iW`, where W is the smallest canonical power-of-two width at least `max(A,B+1,8)`. |

Operand order does not change this derivation. After deriving the type, the compiler shall test its availability. Failure is a missing-type error, with the derived type identified in the diagnostic. An explicit destination on a named operation can request another enabled projection domain; an outer assignment supplies no such arithmetic destination.

For example, `i64` with `u64` derives `i128`. Enabling only `i256` in addition to the operand widths leaves that expression's derived type as `i128`, and therefore leaves it unavailable. Explicit `checked_add<i256>(a,b)` can select the wider destination. `i24` with `u16` retains the already present `i24`; `i24` with `u24` derives canonical `i32`.

The common type contains every operand value. The operation's result retains that width and uses its selected overflow policy. Narrow operands retain their own type when this table selects it.

### 3.2 Comparison

A fixed-integer comparison shall compare the two mathematical values directly. It requires no arithmetic common type. Thus `i64(-1) < u64.MAX` is true with only i64 and u64 enabled. The comparison's implementation may inspect signs and unsigned magnitudes while preserving that ordering. Explicit family-crossing rules still determine which typed comparisons exist.

## 4. Arithmetic policies

### 4.1 Projection and delivery

Let a result type have width N, lower bound L, and upper bound U. For mathematical integer z define `b = z mod 2^N`, with `0 <= b < 2^N`. Its unsigned interpretation is b; its signed interpretation is b below `2^(N-1)` and `b - 2^N` otherwise.

| Policy | Addition, subtraction, multiplication, negation, increment/decrement | Division, remainder, and shifts |
| --- | --- | --- |
| Native | Deliver the N-bit modulo interpretation. Signed and unsigned operations use the same projection. | Use the normal-domain results in Section 4.2 and the target's published native result/fault mapping for the exceptional domain. |
| Checked | Deliver z exactly when `L <= z <= U`; otherwise deliver the operation's checked failure. | Validate the defined domain, then test the result's representability. |
| Wrapping | Deliver the N-bit modulo interpretation. | Validate the defined domain, then apply modulo projection to the mathematical result. |
| Saturating | Deliver `min(max(z,L),U)`. | Validate the defined domain, then clamp the mathematical result. |

A Checked value interface shall deliver its result or NumericTrap. Its corresponding Result interface shall deliver NumericResult. The canonical delivery steps and status definitions are in Chapter 04. Ordinary operators select their policy through Chapter 08; explicitly named interfaces retain their own policy in every preset.

Native addition, subtraction, multiplication, and negation define a result for every operand value. Optimizers shall preserve this modulo meaning, including for signed overflow. This policy introduces no obligatory overflow test or status object. A target provider shall declare its Native operation lowering and observable result/fault contract, and the compiler shall preserve that contract through lower-level optimization.

### 4.2 Quotients, remainders, and shifts

For nonzero divisor b and a representable quotient, ordinary integer division delivers `trunc(a/b)` and remainder delivers `a - trunc(a/b)*b`. A nonzero remainder has a's sign. Native division and remainder use their target contract when b is zero or the signed input pair is `(MIN,-1)`. That contract shall identify the permitted native result or machine fault and its control-flow consequence. Native execution requires no inserted domain-check branch, synthesized NumericResult, or normalized NumericTrap at these sites. The compiler shall retain the declared result/fault possibilities for runtime inputs.

Checked division of `MIN` by `-1` fails with OutOfRange. Checked remainder of that pair succeeds with zero, because remainder has an independent mathematical result. Named Wrapping division delivers MIN and named Saturating division delivers MAX; their remainder forms deliver zero. Each named form rejects a zero divisor through its own declared delivery interface. The Euclidean modulo interface selects the nonnegative representative in `[0,abs(b))` for nonzero b.

A valid fixed shift count k satisfies `0 <= k < N`. Within that domain, left shift projects mathematical `x*2^k` under the selected policy; signed right shift is floor division by `2^k`; unsigned right shift shifts in zeros. Native left shift retains low N bits. For an invalid variable count, a Native ordinary shift follows its target-declared result/fault mapping. Checked and other explicitly validating shift interfaces deliver InvalidShift. The static diagnostic rule continues to reject a known invalid count or evaluated ordinary zero divisor before code generation.

### 4.3 Evaluation and mutation

The expression chapter supplies the one-time operand evaluation and compound-assignment order. A returning checked mutation shall commit its destination only after its numeric operation succeeds. Native mutations commit the projected Native value on a returning path. Operand-expression side effects precede this commit boundary and retain their own effects.

## 5. Literals and conversions

Integer tokens begin as exact mathematical integers. [Numeric expressions](07_numeric_expressions.md#chapter-07-numeric-expressions) specifies their materialization points and the configured default type. A concrete destination shall receive the literal's exact value under its binding rule; unavailable or unrepresentable required bindings are diagnosed at that point.

[Numeric integration](04_numeric_integration.md#chapter-04-numeric-integration) supplies the single conversion table and algorithms. Checked tests the selected projection against the destination range; Exact probes actual finite representability; Wrapping and Truncating use the defined integer modulo map; Saturating clamps after its selected projection. Integer-to-integer Checked conversion has no rounding stage. Real-to-integer conversion uses the source's actual value and its explicit rounding rule.

An implicit conversion shall have the required exact-preservation proof from the whole source domain or language constant evaluation. An explicit conversion supplies the selected loss/projection policy when that proof is unavailable. The Native arithmetic default changes ordinary arithmetic execution; it leaves these named conversion predicates and type-binding requirements intact.

## 6. Representation and bit facilities

Fixed bitwise operands shall have the same width and signedness. `~` complements N representation bits; `&`, `|`, and `^` operate on corresponding bits. The caller supplies an explicit representation conversion when different types participate.

The expression chapter defines `reinterpret_bits`, logical shifts, extraction, insertion, and their function signatures. Indices start at the least-significant bit. Explicit truncating insertion selects low bits; validated insertion requires its value to fit the selected width. Their named range/capacity contracts remain selected functionality under Native execution. Each atomic bit update covers the whole underlying integer and obeys the independently selected memory order from the concurrency model.

## 7. BigInt value and resource contracts

BigInt arithmetic shall produce exact mathematical integers subject to admitted resources. Its bitwise model is infinite two's complement; a logical right shift therefore requires an explicit finite-width representation. A Native fixed-integer policy supplies no implicit BigInt width or modulo boundary.

BigInt object and temporary resource plans, Reserved/Soft quota admission, Commit, Transfer, and concurrent accounting are defined in the expression chapter and the [numeric resource interfaces](32_numeric_resource_interfaces.md#chapter-32-numeric-resource-interfaces). A selected hard quota is an operational resource contract in every preset. The implementation shall account for the resources required by that selected contract and may use any equivalent physical representation of its counters or reservations.

A returning failed mutation shall preserve the destination's value, storage owner, and applicable accounting. The Result form reports ResourceLimit or AllocationFailure as appropriate; the value form uses its explicit numeric terminal outlet. Uncommitted temporary resources follow normal returning-path cleanup. This guarantee concerns the numerical operation's commit, while prior operand effects retain their ordinary semantics.

A copy shall acquire independent value storage. A successful move shall transfer ownership where compatible and leave the source at valid zero. Self-move assignment preserves the object. An incompatible-resource move shall acquire the destination's storage and complete its replacement before discharging the old source; failure preserves both original values and ownership. These are selected BigInt ownership effects, not a default cost attached to fixed integers.

## 8. Diagnostics and configuration

The compiler shall apply Chapter 04's numeric applicability cases and Chapter 08's severity and promotion policy. Missing derived types and required source rules are compilation questions; permitted runtime Native cases retain their declared execution even when a diagnostic is emitted.

Each definition shall bind its numerical configuration and publish the relevant type, provider, operation-policy, and resource contracts. An importing definition uses that published contract. Storage availability, Native operations, strict status support, and optional software support are distinct capabilities. A requested capability shall be supplied by a selected provider or diagnosed at its use.

