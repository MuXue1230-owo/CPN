<a id="chapter-31-units-interfaces"></a>

# CPN26 Quantity and Affine Point Interfaces Specification

## 1. Scope and identity

The optional std.units module supplies the following names in namespace std::units. Signature tables instantiate the ordinary generic grammar: descriptors are types, and numerical metadata parameters are admitted integer constants. [Chapter 04](04_numeric_integration.md#chapter-04-numeric-integration) owns numerical projection, status, and failure; the [core model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance) owns execution and object lifetime.

Descriptors shall determine static type identity. Quantity and Point shall store one representation object and use that object's construction, ownership, and operation contracts. Ordinary arithmetic inherits the selected Rep policy, including Native Release. Named conversions below select their stronger projection contracts explicitly.

## 2. Canonical descriptors

### 2.1 Dimensions

`Dimensionless` denotes an empty dimension. `Axis<Tag>` denotes exponent one of the nominal type Tag. Tag is a complete nominal object type; its exported type identity, not its fields, spelling, or layout, identifies the axis. Aliases of one Tag identify the same axis. Different nominal tags remain different even when both are empty records.

`ProductDimension<A,B>`, `QuotientDimension<A,B>`, and `PowerDimension<A,Exponent>` are type aliases forming the product, quotient, and integer power of admitted dimension descriptors. Exponent is a `const i32` parameter. Their canonical identity is the finite map from axis identity to nonzero i32 exponent: products add exponents, quotients subtract, powers multiply, and zero entries disappear. Equivalent maps denote one type regardless of expression order. Required metadata evaluation shall diagnose ERROR for an unrepresentable exponent.

The following empty tag types and dimension aliases are standard. Each dimension alias means Axis of its row's tag; the canonical unit fixes the interpretation of Scale.

| Tag | Dimension alias | Canonical unit |
| --- | --- | --- |
| `LengthTag` | `LengthDimension` | metre |
| `MassTag` | `MassDimension` | kilogram |
| `TimeTag` | `TimeDimension` | second |
| `ElectricCurrentTag` | `ElectricCurrentDimension` | ampere |
| `TemperatureTag` | `TemperatureDimension` | kelvin |
| `AmountTag` | `AmountDimension` | mole |
| `LuminousIntensityTag` | `LuminousIntensityDimension` | candela |
| `AngleTag` | `AngleDimension` | radian |
| `InformationTag` | `InformationDimension` | bit |

Angle and information shall retain their axis identities. Applications may supply nominal currency or domain tags through Axis. Dimension multiplication shall apply this algebra; exchange rates and other domain conversions require their own operation contracts.

### 2.2 Ratios and scales

`Ratio<N,D>` is a canonical descriptor alias whose parameters are `const i64 N` and `const u64 D`. D shall be positive. It reduces N/D by the mathematical greatest common divisor, retaining the numerator sign and a positive denominator; zero canonicalizes to 0/1. Equal reduced fractions denote the same descriptor type. The descriptor exposes public associated constants `i64 numerator` and `u64 denominator`. Computing the magnitude of i64.MIN for reduction is mathematical metadata evaluation, not an overflowing signed negation.

`Scale<N,D>` aliases Ratio<N,D> but rejects N equal to zero. `Offset<N,D>` aliases Ratio<N,D> without that restriction. `ProductScale<A,B>` and `QuotientScale<A,B>` require nonzero ratio descriptors, compute their exact product or quotient, reduce it, and produce the canonical scale type. Required metadata evaluation shall use the exact reduced result and diagnose ERROR when its numerator or denominator exceeds the declared domain.

`UnitScale`, `PercentScale`, `NanosecondScale`, `BitScale`, and `ByteScale` alias respectively Scale<1,1>, Scale<1,100>, Scale<1,1000000000>, Scale<1,1>, and Scale<8,1>. The bit/byte aliases apply to InformationDimension; a scalar ratio does not itself acquire that dimension. These descriptor facilities shall require their stated i32/i64/u64 constant-parameter capabilities.

### 2.3 Affine origins

`Origin<D,Frame,O>` is a descriptor type with a canonical dimension D, a complete nominal frame type Frame, and an Offset descriptor O. Its public nested type aliases `Dimension`, `FrameType`, and `OffsetType` name those arguments. Its offset is measured in D's canonical unit relative to that frame's zero. `ZeroOrigin<D,Frame>` aliases Origin<D,Frame,Offset<0,1>>. Equal canonical arguments produce the same origin identity.

Origin conversion shall require identical dimension and frame identities. Distinct frames remain distinct even when their offsets match. Clock correlation, currency exchange, physical calibration, and conversion to std::time::Instant<Clock> shall use their own explicit interfaces.

## 3. Construction, access, and lifetime

`Quantity<D,Rep,S>` requires a canonical dimension D, a nonzero scale S, and a complete nonreference object type Rep. `Point<D,Rep,S,O>` additionally requires an Origin whose dimension is D. Both expose public nested type aliases `Dimension`, `Representation`, and `ScaleType`; Point additionally exposes `OriginType`. They name the canonical supplied arguments. Each wrapper shall construct its sole representation subobject in place; its foreign ABI transport uses its declared wrapper binding.

| Operation on either wrapper | Required contract |
| --- | --- |
| Direct construction from `args...` | Directly construct Rep from the individually forwarded arguments, evaluated once under ordinary construction rules. Available exactly when that Rep construction is available. |
| Default construction | Use the zero-argument Rep construction and its typed default value/resource contract. |
| Same-type copy/move construction | Copy/move the representation with its ordinary requirements, effects, and moved-from state. |
| Same-type copy/move assignment | Apply the corresponding Rep assignment when available; preserve its failure and self-assignment contract. |
| `representation()` on mutable receiver | `Rep&`, borrowing the existing representation subobject. |
| `representation()` on read-only receiver | `const<Rep>&`, with the same borrow origin. |
| Destruction | Destroy the representation exactly once under the selected lifecycle profile. |

Same-type copy/move construction shall select its dedicated operation. A single argument of another wrapper type is admitted by forwarding exactly when that type is Rep, including an explicitly nested representation. Other metadata changes shall use the named conversion catalogue. Explicit extraction followed by construction asserts the caller's chosen new interpretation.

Representation access shall borrow the existing subobject for its lifetime. Mutation changes its stored value under the same static metadata. Copying an allocating Rep shall use that representation's resource contract. Construction and failure shall follow the core lifecycle rules for the one subobject.

## 4. Arithmetic and comparisons

An overload shall require the corresponding Rep operation with exactly Rep as its value result, or bool for a comparison. It shall invoke that operation once under the source order and selected numerical contract. A Native representation operation retains its native value/fault behavior and unobserved events; an explicitly observed/Checked representation operation retains its own guarantees. Different representations require explicit unification.

| Operands and operation | Result |
| --- | --- |
| `Quantity<D,Rep,S>` plus/minus the same type | The same Quantity type. |
| Unary plus/minus of a Quantity | The same type, using the corresponding Rep operation. |
| `Quantity<A,Rep,SA>` multiplied by `Quantity<B,Rep,SB>` | Quantity<ProductDimension<A,B>,Rep,ProductScale<SA,SB>>. |
| Those quantities divided | Quantity<QuotientDimension<A,B>,Rep,QuotientScale<SA,SB>>. |
| `Point<D,Rep,S,O>` minus the same Point type | Quantity<D,Rep,S>. |
| That Point plus/minus Quantity<D,Rep,S> | The same Point type. Quantity plus Point has the corresponding addition overload. |
| Equality/inequality of identical wrapper types | The corresponding representation comparison. |
| Ordered comparison of identical wrapper types | The representation comparison, with operands reversed when S is negative. |

The table defines the standard overload set. Comparisons shall use Rep's declared comparison behavior and require its corresponding overload. Integer division, overflow, and floating rounding occur at the Rep operation boundaries. Required metadata shall be representable before admission of the resulting type.

## 5. Named conversions

### 5.1 Catalogue and admissibility

The following functions use the canonical `std::numeric::NumericResult`, `NumericStatus`, `NumericErrorCode`, and `RoundingMode`. Destination and Source are complete Quantity types of the same dimension, or complete Point types of the same dimension and frame. Quantity and Point shall each convert within their own wrapper family. Scale and origin offset may differ.

The baseline source representations are enabled fixed integers and scalar IEEE binary/fixed-decimal floats. Exact destinations may use either of those families. Checked destinations also admit both families; Saturating destinations are fixed integers. Other Rep families may supply explicit conversion extensions publishing their signatures, resources, and projection semantics.

| Function | Result and projection |
| --- | --- |
| `convert_exact<Destination>(const<Source>& source)` | NumericResult<Destination>; finite representability probe, no rounding. |
| `convert_checked<Destination>(const<Source>& source,RoundingMode rounding)` | NumericResult<Destination>; one final rounded projection with the numeric Checked acceptance rule. |
| `convert_saturating<Destination>(const<Source>& source,RoundingMode rounding)` | NumericResult<Destination>; selected integer rounding followed by clamping. |

The caller shall supply every argument and handle the must-use NumericResult. Each named conversion shall retain its defined acceptance predicate across execution presets.

### 5.2 Exact transformed value

Let x be the actual source representation value, Ss/St the source/destination scales, and Os/Ot their origin offsets. Quantity conversion computes the exact mathematical target coefficient `y = x * Ss / St`. Point conversion computes `y = (x * Ss + Os - Ot) / St`. The operation projects y once to the destination Rep, then directly constructs Destination from that projected representation.

An encoded floating source contributes its actual value. The implementation shall realize the exact affine formula and one destination projection through the selected bounded capability. Admission requires support for the enabled source/destination formats and metadata; classification shall use the final mathematical projection, independently of avoidable intermediate overflow.

For a floating destination, exact zero retains the source floating zero sign multiplied by the scale ratio's sign when the net offset is zero. Other exact cancellations to zero produce positive zero. Rounding a nonzero negative y to floating zero retains its negative sign. Numerical conversion does not promise decimal cohort or other nonnumeric representation preservation.

### 5.3 Failure and status

The implementation shall apply Chapter 04's corresponding Exact, Checked, or Saturating destination projection to y. Exact probes preserve FP status; Checked floating projection uses gradual subnormals and its local events; integer projection uses its CPN26 status. Their acceptance predicates and delivery remain independent of ambient arithmetic trap/error masks.

Exact and Checked shall reject a nonfinite source as NonFinite through representation inspection that preserves the signaling class and FP status. Saturating integer conversion shall reject NaN as NonFinite and map infinity to the destination bound after applying the scale ratio's sign. This catalogue sets wrapped and payload_changed false and otherwise uses the selected projection's canonical status fields.

Success shall directly construct Destination from the projected representation and return it with local status. Failure shall return Err without a Destination payload and preserve the source. Argument evaluation and independent user effects retain their core execution boundaries.

