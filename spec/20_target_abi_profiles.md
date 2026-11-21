<a id="chapter-20-target-abi-profiles"></a>

# CXXN Target ABI Profiles Specification

Static reflection handles, syntax quotations, and generated-declaration values have no native ABI representation. A generated ordinary native declaration is ABI-checked exactly as a source-authored declaration under its owning module and target profile. Reflection of a foreign declaration is limited to properties made available by the verified foreign ABI descriptor; inferred type layout or compiler metadata identity cannot establish unverified direct C++ compatibility.

## 1. ABI compatibility is a versioned contract

A CXXN native object is interoperable with a C or C++ object only to the extent specified by the **selected target ABI profile**, matching foreign declaration contracts, and required support libraries. The extension `.o` or `.obj` does not determine object format. A conforming implementation of a target profile shall emit an ordinary, machine-code-containing relocatable object suitable for the target's standard linker without mandatory CXXN-specific LTO support.

Direct ABI compatibility shall be established by the relevant declared type, call, lifetime, and effect contracts. Direct C++ interoperability additionally requires a selected C++ ABI provider; an exact library ABI contract is additionally required only for the foreign library types or operations actually crossing that boundary. Opaque adapters remain valid when direct class representation is unavailable or incompatible.

This chapter owns the target-family and capability catalogue and applies Chapter 09's foreign declaration and lifetime model. All profiles below identify **families** of target contracts. The selected object/linking, unwinder, CRT, and ABI-provider contract revisions shall bind the compilation; explicit `none` shall supply an absence binding. Producer compiler and actual tool-input versions shall enter build context independently of the public ABI contract. The [reference native bindings](30_reference_target_bindings.md#chapter-30-reference-target-bindings) supply complete baseline instances. A selected standard contract export shall use the exchange fields in the [public schemas](29_public_contract_schemas.md#chapter-29-public-contract-schemas).

## 2. Standard target families

A conforming implementation may support any declared subset of the following target families. A program requiring a family that the toolchain does not supply receives `ERROR` rather than a substitute output format.

| Profile family | Pointer model | Native relocatable format | Default C data model | Native platform calling convention |
| --- | --- | --- | --- | --- |
| `x86_64-linux-sysv-elf` | 64-bit pointers | ELF64, x86-64 | LP64 | System V AMD64 psABI, plus selected Linux supplement |
| `aarch64-linux-aapcs-elf` | 64-bit pointers | ELF64, AArch64 | LP64 | AAPCS64 with selected Linux ELF supplement |
| `x86_64-windows-msvc-coff` | 64-bit pointers | AMD64 COFF/PE rules | LLP64 | Microsoft x64 convention |
| `aarch64-windows-msvc-coff` | 64-bit pointers | ARM64 COFF/PE rules | LLP64 | Microsoft ARM64 ABI convention |
| `x86_64-apple-darwin-macho` | 64-bit pointers | Mach-O x86-64 | LP64 | Apple x86-64 ABI |
| `aarch64-apple-darwin-macho` | 64-bit pointers | Mach-O arm64 | LP64 | Apple arm64 ABI |

The existing names `x86_64-sysv-elf`, `x86_64-msvc-coff`, and `darwin-<architecture>-macho` may be retained as **profile aliases** only when they resolve to one unique fully qualified family and a fixed revision. An alias that is ambiguous between Linux, another ELF operating system, or incompatible CRTs is not valid at a shared ABI boundary.

Linux targets further declare the C runtime family, such as glibc or musl, and its relevant ABI compatibility contract. Windows targets declare the MSVC-compatible compiler/CRT contract, including static/shared CRT selections when they affect allocation and exception handling. Apple targets declare the SDK/platform deployment contract and the relevant Darwin ABI. Changing any of these on a binary boundary is not a silent source-level configuration override.

## 3. Core foreign scalar correspondence

For the six **standard 64-bit profiles above**, the common C scalar sizes in octets are:

| Foreign scalar | Linux LP64 | Windows LLP64 | Darwin LP64 |
| --- | ---: | ---: | ---: |
| `ffi::c_short` / `ffi::c_ushort` | 2 | 2 | 2 |
| `ffi::c_int` / `ffi::c_uint` | 4 | 4 | 4 |
| `ffi::c_long` / `ffi::c_ulong` | 8 | 4 | 8 |
| `ffi::c_llong` / `ffi::c_ullong` | 8 | 8 | 8 |
| C pointer and `size_t` equivalents | 8 | 8 | 8 |
| `ffi::c_float` | 4 | 4 | 4 |
| `ffi::c_double` | 8 | 8 | 8 |

These widths are **not** native aliases: even when two foreign scalar types have the same storage width, their nominal C identities can differ. Native `i32`, `i64`, `usize`, and CXXN `char` do not automatically acquire C argument-passing or C++ name-mangling identity. In particular, native Unicode-scalar `char` is not `ffi::c_char` or the platform's `wchar_t`.

The target descriptor additionally binds:

- whether plain C `char` is signed;
- `_Bool` and foreign `bool` size, alignment, canonical representations, and parameter-passing rules;
- `wchar_t`, `char16_t`, `char32_t`, foreign enumeration and bit-field representation;
- `long double` format, precision, exponent range, storage, alignment, and calling convention;
- signed/unsigned extended integer and compiler vector type ABI, if enabled;
- the address-space and function-pointer representation, including any pointer authentication or capability tagging policies.

A caller cannot assume that `ffi::c_long_double` is `f64`, `f80`, or `f128` solely from the CPU architecture. The provider declares the actual ABI type and its conversion contract. Cross-width conversions obey existing CXXN Checked/Exact and explicit representation operations, not a C-style silent narrowing rule.

## 4. Calling and object-file classification

### 4.1 Cross-platform rule

A supported ABI profile must bind its call and return classification to the **pinned normative revision of the platform ABI**, including parameter/return register selection, by-reference aggregates, hidden result pointers, stack alignment, varargs, red-zone/shadow-space rules, unwind tables, and TLS models. A direct foreign call shall use that bound platform classification.

Scalar C type identity, aggregate field layout, by-value calling classification, and emitted symbol decoration are checked independently. Even a C-compatible in-memory record is not necessarily passed by value identically across different target ABIs. An ABI descriptor shall include packing and compiler switches that affect records, bit-fields, vector types, or empty aggregate handling.

### 4.2 Windows x64

The standard Microsoft x64 profile uses the platform's prescribed register/stack parameter classification and reserves the required caller-provided shadow store. It does not apply the System V AMD64 red-zone or aggregate classification. Its C long type follows LLP64. An `extern "C"` declaration uses the selected Microsoft x64 calling convention and native C naming rule unless a compatible explicit alternative is selected in the binding descriptor.

### 4.3 Windows ARM64

The standard Microsoft ARM64 profile binds to the Windows ARM64 ABI rather than assuming that generic AAPCS64 alone describes Windows exceptions, varargs, unwind records, or platform-specific calling rules. Its C long type follows LLP64. A Windows ARM64 use shall require its supported instruction, vector, and exception capabilities; an unavailable requested capability yields ERROR.

### 4.4 Linux x86-64 and AArch64

The Linux x86-64 profile uses the selected System V AMD64 psABI and Linux ABI supplement. The Linux AArch64 profile uses the selected AAPCS64 and Linux ELF supplement. Both are LP64 in the standard profiles named here. Their C++ provider, libc family, and C++ standard-library ABI are recorded independently; identical ELF files do not establish that two implementations can exchange C++ `std::string`, exceptions, or allocator ownership.

### 4.5 Apple x86-64 and arm64

Apple profiles use Darwin Mach-O, selected Apple platform call conventions, and the declared deployment target. Apple's arm64 ABI has platform-specific differences from generic AAPCS64, including stack-argument placement and caller extension of narrow integer arguments. A generic AAPCS64 code path is not evidence of Apple arm64 call compatibility. The provider's supported C++ ABI subset, library ABI, constructor/destructor entry behavior, and exception bridge remain explicit.

## 5. Direct compatibility levels

A target/provider shall publish each supported capability independently:

| Level | Required guarantee |
| --- | --- |
| `native_object` | Linker-readable ordinary relocatable object with declared symbols, relocations, sections, and required unwind metadata. |
| `c_call` | Correct calls/returns of supported foreign scalars, pointers, and function pointers under the declared C ABI. |
| `c_record` | Verified layout and by-value/by-reference handling of the declared C record subset. |
| `c_callback` | Reverse calls and callback storage, ownership, and lifetime under the declared C ABI. |
| `cpp_symbol` | Provider-matching mangling/decoration for a declared set of C++ symbols and overloads. |
| `cpp_class` | Provider-matching class layout, bases, virtual bases, member pointers, virtual dispatch and this adjustment for the supported subset. |
| `cpp_lifetime` | Compatible construction, base/complete/deleting destructor entry points, ownership, and construction-failure rollback under the supported subset. |
| `cpp_rtti` | Provider-compatible RTTI identity and required dynamic-cast/type-identification operations. |
| `cpp_exception` | Provider-compatible exception record, handler search, cleanup, matching, rethrow, and cross-boundary propagation where explicitly enabled. |
| `cpp_stdlib` | Individually verified binary layouts and semantics for named C++ library types and ABI versions. |

For example, support for `cpp_symbol` is not support for `cpp_class`; successful calls to an opaque wrapper are not evidence of `cpp_rtti`. The standard library's own `std::collections::Vector<T>` is not a C++ `std::vector<T>` ABI merely because both have similar public operations.

A provider shall declare feature-level exclusions, including unsupported inheritance forms, member-pointer models, passing or returning nontrivial classes, variadic templates, sized/aligned deletion, or cross-language exception propagation. An exclusion is not repaired by a compiler warning or by assuming a common compiler vendor.

## 6. Native and foreign exceptional control flow

Non-unwinding boundaries and terminal events shall follow Chapter 09's foreign routing contract.

`extern "C++"` alone does not authorize C++ exception propagation through CXXN frames. A direct `cpp_exception` profile additionally supplies compatible exception object identity, handler-matching rules, stack unwind/cleanup behavior, runtime personality functions or equivalent, and rethrow semantics. A foreign C++ destructor may terminate according to its foreign contract; a CXXN destructor in Release still follows the CXXN Release termination rule where that boundary applies. Each entry shall retain its bound destruction/failure policy.

An explicit adapter may translate a supported C++ exception to a declared CXXN `Result` error. An adapter that raises a translated CXXN exception shall advertise that native throwing effect and perform the translation within a permitted native propagation phase; no exception crosses a boundary declared non-unwinding. Translation changes primary identity unless the provider specifically supports retaining and propagating the compatible original foreign record. Error payloads with allocated storage have a declared allocator and destroy/release owner. The [error and recovery specification](28_error_and_recovery.md#chapter-28-error-recovery) defines these distinctions. A foreign `longjmp`, forced unwind, OS exception, or asynchronous cancellation is not implicitly safe across CXXN frames.

## 7. Native record and ownership binding

`[[abi_layout("C")]]` and `[[abi_layout("C++")]]` attach only the explicitly supported target-provider layout and its required qualifiers. The emitted record shall contain exactly that declared layout. Where CXXN requires state not represented in a foreign object, it may maintain that state externally or in a separate explicit wrapper without changing foreign field offsets.

A foreign class's constructor/destructor entry points discharge their **actual foreign obligations**. A complete-object destructor cannot be followed by a second CXXN member/base destructor run; a deleting destructor may additionally free the foreign allocation. The binding descriptor records which responsibility is discharged by each entry. Virtual-base responsibility and early base destruction remain governed by the existing CXXN lifetime contract and are directly enabled only if the foreign contract genuinely supports them.

Cross-boundary storage transfer identifies an allocator domain and compatible disposal function. Equal raw pointer width does not authorize invoking a different C runtime's `free`, unrelated `delete`, or an allocator with a different resource protocol. Foreign library code and associated RTTI, vtables, callback, allocation, or exception-support records remain loaded as long as an outstanding owner requires them.

## 8. Object emission, static initialization, and module metadata

The target object shall include all sections and relocations required by the selected static-initialization, TLS, unwind, and exception contracts. Object retention and link inputs shall preserve reachable native construction and static initialization obligations through archive extraction and section collection. The resolved link contract shall identify required retention/entry mechanisms and support libraries, with standard external serialization supplied by a selected contract export.

The native initializer graph and foreign CRT's own init/fini mechanisms remain separate unless explicitly mapped. One domain owner is responsible for executing each mapped initialization unit once, with reverse logical destruction for committed CXXN objects. Each foreign destruction obligation shall have one registered owner.

A native interface's signature, type identity, relevant numerical evaluation configuration, and ABI contract shall determine its resolved boundary identity. A direct boundary shall establish equality of its relevant contract fields; a mismatch shall yield ERROR. Standard export shall encode this identity in Chapter 29's boundary projection and fingerprint. A versioned adapter may explicitly translate representationally compatible values with a declared loss/ownership/failure contract.

## 9. Required ABI evidence and diagnostics

A provider claiming one of the levels in Section 5 shall publish a versioned contract including the applicable reference ABI revision and named supported features. Each required public boundary is either:

- **directly compatible**, with matching specified representation, call classification, effects, and lifetime;
- **adapted**, with a declared wrapper and conversion/ownership contract; or
- **unsupported**, in which case direct use is `ERROR`.

An unverified programmer assertion permitted by the configured boundary policy yields `ANOMALY` and preserves its runtime responsibility; it is never recorded as a verified fact. A compiler cannot declare direct compatibility merely because the host linker accepted the symbols.

Target support dependencies shall follow the core capability model. The ordinary target linker shall resolve emitted machine code using the selected dependencies published by that binding.

