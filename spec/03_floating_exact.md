<a id="chapter-03-floating-exact"></a>

# CXXN Floating and Exact Numeric Families Specification

## 1. Representation and execution

This chapter owns the fixed floating format tables and the value representations of Fixed, Rational, and BigDecimal. [Numeric integration](04_numeric_integration.md#chapter-04-numeric-integration) owns their projection, observation, status, NaN, and error-delivery algorithms. [Configuration](08_runtime_configuration.md#chapter-08-runtime-configuration) selects ordinary-operation defaults, including Native Release execution. A named explicit numerical operation retains its selected contract under the [core operational model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance).

The implementation shall represent the actual value encoded in each typed source. A subsequent conversion shall consume that value. Direct literal formation instead consumes the literal's exact mathematical token value under the numeric-expression binding rules. These two sources can therefore yield different exact rational values even when their source text is similar.

## 2. Fixed floating families

### 2.1 Families and capabilities

| Family | Names | Value contract |
| --- | --- | --- |
| Binary floating | `f16`, `bf16`, `f32`, `f64`, `f128` | The corresponding row below, including infinities, NaNs, signed zeros, and subnormal encodings. |
| Fixed decimal floating | `dec32`, `dec64`, `dec128` | The decimal row below and its selected BID or DPD encoding. |
| BigDecimal | The enabled BigDecimal family | The finite, resource-backed coefficient/exponent model of Section 6. |

A provider shall publish storage, Native arithmetic, observed arithmetic, rounding, and software-support capabilities separately for each enabled format. Materializing a format shall require its storage capability and the construction/conversion operations actually used. Executing an arithmetic operation shall require its selected operation, format, controls, and delivery claim. The compiler shall diagnose a missing required claim at that use. Target byte order, alignment, and ABI transport shall remain part of the representation binding.

The [core conformance model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance) shall determine the required implementation baseline. The tables in this chapter shall define the meaning of each selected representation. Exact families, additional formats, observed arithmetic, component-exact Complex arithmetic, and elementary mathematics shall enter an implementation's obligations through their separately selected capability claims. A floating storage claim shall remain sufficient for storage and representation transfer within its published contract.

### 2.2 Fixed format parameters

Binary formats have the following storage and finite-value parameters. Precision includes the implicit leading significand bit; exponent bounds describe normalized values.

| Type | Storage bits | Precision bits | Exponent bits | Minimum normal exponent | Maximum normal exponent |
| --- | ---: | ---: | ---: | ---: | ---: |
| `f16` | 16 | 11 | 5 | -14 | 15 |
| `bf16` | 16 | 8 | 8 | -126 | 127 |
| `f32` | 32 | 24 | 8 | -126 | 127 |
| `f64` | 64 | 53 | 11 | -1022 | 1023 |
| `f128` | 128 | 113 | 15 | -16382 | 16383 |

In a binary format with precision `p`, exponent width `e`, sign `s`, exponent field `E`, and fraction field `F`, the fraction has `p-1` bits and the bias is `2^(e-1)-1`. For `0 < E < 2^e-1`, the value is `(-1)^s * (2^(p-1)+F) * 2^(E-bias-(p-1))`. For `E=0`, it is `(-1)^s * F * 2^(1-bias-(p-1))`, preserving the sign of zero. Exponent-all-ones and zero fraction encodes infinity; exponent-all-ones and nonzero fraction encodes NaN. The most significant fraction bit is the quiet bit. A signaling encoding has that bit zero and at least one remaining payload bit nonzero. Raw storage uses the target byte order.

The decimal finite-value parameters are:

| Type | Storage bits | Decimal precision | Minimum coefficient exponent | Maximum coefficient exponent | Minimum normal adjusted exponent | Maximum adjusted exponent |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `dec32` | 32 | 7 | -101 | 90 | -95 | 96 |
| `dec64` | 64 | 16 | -398 | 369 | -383 | 384 |
| `dec128` | 128 | 34 | -6176 | 6111 | -6143 | 6144 |

A finite decimal value is `(-1)^s * c * 10^q`, with integer coefficient `0 <= c < 10^p` and the table's coefficient-exponent interval. Subnormals and both signed zeros are included. Nonzero values whose adjusted exponent is below the minimum normal exponent are subnormal. Decimal special values, payload interpretation, and coefficient/exponent encoding use the explicitly selected BID or DPD provider. The provider shall preserve this finite value set and precision.

### 2.3 Decimal encoding and cohorts

A decimal value may have several coefficient/exponent encodings. Numerical equality shall compare values; representation operations shall inspect the selected encoding. The BID or DPD provider shall bind canonical NaNs, payload mappings, admissible encodings, and ordering/canonicalization operations. Its encoding identity participates in the exported representation contract. Decimal Complex arithmetic additionally selects the cohort rules in the [Complex chapter](05_complex_arithmetic.md#chapter-05-complex-arithmetic).

## 3. Binding and numerical execution

Fixed-format construction shall bind the requested destination format and its selected conversion. A native ordinary format conversion uses the provider's Native conversion contract. A named Checked or Exact conversion uses the fixed predicate in Chapter 04. Implicit conversions use that chapter's exact-preservation admission rule.

The compiler shall select a common floating type using Chapter 04's complete-finite-domain inclusion algorithm. Binary/decimal, integer/floating, and allocating-family crossings use their explicitly admitted interfaces. Literal formation and type inference follow [numeric expressions](07_numeric_expressions.md#chapter-07-numeric-expressions).

The Native profile shall use its declared target operations, control environment, NaN behavior, subnormal behavior, and admitted transformations. Its ordinary events are unobserved. Strict and explicit observed interfaces shall use Chapter 04's local-status collection, deterministic NaN selection where applicable, rounding, and tininess algorithms. Representation inspection, total ordering, and explicit exact operations retain their named value contracts. These choices alter operation behavior rather than the format's stored value set.

## 4. Fixed-point representation

An admitted `fixed<I,Radix,Scale>` has one coefficient in enabled integer type I. Radix is 2 or 10 and Scale is a compile-time integer:

```text
quantum = Radix^Scale
value = coefficient * quantum
```

The type identifies its quantum; its runtime object stores the coefficient. Its mathematical values are finite multiples of that quantum within the coefficient range. Its zero is the coefficient zero. Chapter 04 defines arithmetic, rescaling, and selected destination projection. Coefficient addition and subtraction inherit their selected integer arithmetic policy; explicitly named Checked or Exact rescaling selects that stronger operation.

## 5. Rational representation

A Rational shall store a mathematical numerator p and a positive denominator q in reduced form. Its value is p/q and its canonical zero is 0/1. Construction with a zero denominator selects the Rational domain-error outlet. Arithmetic shall retain exactness under its explicitly selected resource contract.

The conversion chapter defines finite floating decoding and representability. In particular, the actual denominator of a reduced value determines whether a binary or decimal expansion terminates; destination precision and exponent bounds additionally determine whether a fixed-format encoding exists. A nonterminating decimal can remain an exact Rational.

## 6. BigDecimal representation and resources

A BigDecimal shall represent a finite value by an integer coefficient and an integer decimal exponent. Its capability shall declare the admitted exponent domain, coefficient resources, arithmetic contexts, and result delivery. Numerical equality compares mathematical values; representation observations inspect the coefficient, exponent, and any separately retained presentation metadata.

An Exact operation shall deliver an exact finite decimal when its value and resources are admitted. Exact division shall report NonTerminatingExpansion when that decimal expansion is infinite. A rounded division shall use its selected finite precision and rounding context. These contexts describe an operation; existing objects retain their representation identity.

A returning failed mutation shall preserve its old value and ownership. ResourceLimit and AllocationFailure have their own numeric error categories. Resource admission, temporary ownership, and the public allocating-family interfaces follow [numeric resources](32_numeric_resource_interfaces.md#chapter-32-numeric-resource-interfaces). Their explicit ownership and quota effects remain functional observations in every execution preset.

## 7. Integration

The compiler shall bind the relevant format, execution, provider, and resource contracts at the owning definition. Exported boundaries shall publish the applicable contracts; imports consume them under the module compatibility rules. Numeric compile-time applicability cases are centralized in Chapter 04, and severity/promotion is centralized in Chapter 08.

[Mathematical functions](18_mathematical_functions.md#chapter-18-mathematical-functions), [Complex arithmetic](05_complex_arithmetic.md#chapter-05-complex-arithmetic), [quantity interfaces](31_units_interfaces.md#chapter-31-units-interfaces), and [codec interfaces](19_extended_standard_library.md#chapter-19-extended-standard-library) supply their own feature deltas. They reuse the representation and numerical definitions owned here and in Chapter 04.

