<a id="chapter-09-native-interoperability"></a>

# CXXN Native Object and Foreign ABI Specification

## 1. Scope and terminology

This chapter applies the [core execution model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance) to native objects, foreign declarations, ownership, and image lifetime. A target profile binds a machine/platform ABI; an ABI provider supplies a versioned feature contract; a foreign binding associates a declaration with that contract.

A direct binding shall agree on every used object, call, layout, lifetime, and exception requirement. An adapter shall perform its declared translation between otherwise distinct contracts. The implementation shall publish its supported subset and diagnose an unavailable requested feature as ERROR.

Effect, value, and retention annotations shall use source/interface metadata. Their machine transport shall follow the declared C/C++ signature. [Foreign effect boundaries](25_effect_composition_and_boundaries.md#chapter-25-effect-composition-boundaries) define callback retention and adapters; an opaque import shall use their conservative effect contract.

## 2. Native relocatable objects

A native compilation mode shall emit ordinary relocatable machine-code objects accepted by the selected platform linker. Objects shall contain the applicable code, data, symbols, relocations, section attributes, and required unwind metadata. The exported native interface shall have a usable ordinary platform-linker path.

Optional link-time intermediate representation may accompany an object. Native object mode shall retain usable machine code for that ordinary linker path. Archive extraction, symbol visibility, weak definitions, and section retention shall follow the selected target contract. The implementation may require ordinary linker options and explicitly selected support libraries.

The [target ABI profiles](20_target_abi_profiles.md#chapter-20-target-abi-profiles) own the target-family and compatibility-level catalogue. A selected family shall bind one architecture, operating-system ABI, data model, object format, and revision. The file suffix is a name; the target contract determines its contents. Inconsistent target/format requests yield ERROR.

The target descriptor shall contain required relocation, processor, and unwind features. Code-generation options shall resolve to that declared instruction capability. Native unwind metadata and language exception support are separately bound features.

## 3. ABI descriptors and compatibility

Each image and foreign binding shall identify its exact selected target contract. The [reference native bindings](30_reference_target_bindings.md#chapter-30-reference-target-bindings) instantiate concrete subsets, and Chapter 20 owns compatibility levels. The compiler shall retain the facts needed to validate the used ABI through Chapter 21's semantic records. A selected standard contract export shall serialize them through the [public ABI schema](29_public_contract_schemas.md#chapter-29-public-contract-schemas), whose canonical encoding and fingerprints belong to that optional interchange capability.

A descriptor shall bind its machine/object contract, C transports and calling convention, applicable C++ layout/lifetime/exception features, runtime/library identities, and support dependencies. ABI-relevant packing, character, long-double, enum, CRT, and library options shall be explicit. A libstdc++ binding shall include the applicable [library ABI policy](https://gcc.gnu.org/onlinedocs/libstdc++/manual/abi.html) settings.

Direct linkage shall compare the requirements actually shared by that boundary. Provider-declared compatibility may span compiler versions; private numerical defaults may differ when their effects stay inside each definition. Missing foreign metadata shall be supplied by an explicit binding descriptor. Known contradictions or unavailable lowering yield ERROR; an admitted unproved assertion yields ANOMALY and retains its programmer obligation.

## 4. Linkage declarations and external symbols

Foreign linkage shall use the `extern "C"` or `extern "C++"` declarations defined by the [grammar specification](15_grammar_binding.md#chapter-15-grammar-binding). That chapter owns declaration classification, linkage-block scope, and the `define` object-definition marker. The selected linkage shall bind the external symbol and its call or object contract. CXXN expression, numerical, initialization, and lifetime semantics shall govern a source-defined implementation.

| Foreign source form | Bound entity and definition responsibility |
| --- | --- |
| `extern "C" R function(parameters);` | Function declaration; the selected image/provider supplies its definition. Empty parentheses declare zero parameters. |
| `extern "C" R function(parameters) { statements }` | Function definition with the declared foreign callable contract. |
| `extern "C" T object;` | External object declaration; the binding designates storage and a lifetime established by its defining domain. |
| `extern "C" define T object(arguments);` | Object definition; this definition supplies storage, performs ordinary CXXN initialization, and registers its applicable lifetime obligations. |
| `extern "C" define T object;` | Object definition using type-directed default initialization. |

The corresponding C++ linkage forms shall use the same declaration categories and the selected C++ provider's symbol and ABI contracts. A declaration shall retain its chosen category through type, parameter, capability, and ABI validation. For `extern "C" T name(10);`, the parser shall select a function declaration and diagnose the invalid parameter declaration at `10`.

An external object declaration shall introduce one descriptor-bound object identity. Its defining domain shall own initialization and the destruction obligations specified by the binding. Repeated compatible declarations shall reference that same identity. A source `define` declaration shall provide the definition under the image's existing single-definition and static/thread-lifetime rules. Declaration-level `const` and `thread_local` shall match the shared object's qualified type and storage contract.

```cxxn
extern "C" {
    ffi::c_int read_count();
    ffi::c_int shared_count;
    define ffi::c_int local_count(10);
}
```

Linkage blocks and nested namespace bodies shall apply the foreign declaration categories to their namespace-scope symbols. Record members, function bodies, and construction tails shall use their own ordinary CXXN declaration grammar. Record layout, member bindings, and function-pointer calling conventions shall use their separately selected provider contracts.

The following ABI attributes are standard:

| Attribute | Meaning |
| --- | --- |
| `[[abi_symbol("symbol")]]` | Bind to the exact object-file symbol spelling, overriding automatic language mangling and target decoration. |
| `[[abi_cc("convention")]]` | Select a calling convention supported by the target descriptor. |
| `[[abi_layout("C")]]` | Use the selected C record-layout contract. |
| `[[abi_layout("C++")]]` | Use the selected C++ provider's verified class-layout contract. |
| `[[abi_pack(N)]]` | Select the provider's declared packing rule with argument `N`. |
| `[[abi_align(N)]]` | Require the declared object alignment. |

Attributes are compile-time metadata. Unsupported values or contradictory attributes are `ERROR`. A raw symbol override shall retain the checked ABI signature. The implementation shall emit a raw symbol spelling exactly, including its supplied platform decoration. Import/export visibility and symbol versions belong to the binding descriptor.

An ordinary `extern "C"` function uses its source identifier with the target's normal C decoration. C linkage does not overload one external name by CXXN parameter types. Distinct overloads require distinct external symbols. Multiple definitions of one external symbol shall satisfy the target's permitted definition rules and the same interface contract.

Native CXXN symbols use a provider-declared, stable, versioned naming scheme. The provider shall publish its canonical identity encoding and naming algorithm. The identity includes module, qualified name, declaration kind, signature, specialization identity, and relevant native ABI version. The scheme shall distinguish distinct identities without treating an unchecked truncated hash as collision-free. Names shall derive from the published logical identity fields. Different naming providers do not imply mutual compatibility; exported C or selected C++ linkage remains available independently.

## 5. Foreign scalar identity

The namespace `ffi` provides descriptor-bound foreign scalar types, including `c_char`, `c_schar`, `c_uchar`, `c_short`, `c_ushort`, `c_int`, `c_uint`, `c_long`, `c_ulong`, `c_llong`, `c_ullong`, `c_bool`, `c_float`, `c_double`, and `c_long_double`. A provider may additionally expose named foreign character, extended integer, or vector types through its capability contract.

These names preserve foreign nominal identity. `ffi::c_int` and `ffi::c_long` remain distinct even on a target where they have the same width. Neither becomes a global CXXN `int` or `long` type. Traditional unqualified CXXN integer names remain removed. A foreign typedef preserves its underlying foreign type identity unless the binding explicitly declares a distinct wrapper.

Each foreign scalar specifies its exact target representation and value domain. Conversion to or from CXXN numerical types follows the applicable lossless implicit or explicit numeric-conversion rules. Foreign type spelling alone does not enable unchecked arithmetic. An explicit foreign call's defined effects remain the foreign function's contract.

A CXXN fixed-width type may cross a C boundary when the descriptor supplies a matching C transport type and calling-convention classification. The generated C declaration shall name that transport type, such as an available exact-width typedef. The choice does not establish that two different C++ nominal parameter types have the same mangled name.

Null object pointers, function pointers, Boolean values, and floating values shall use the selected target representations. A non-CXXN pointer is not automatically a valid integer, a function pointer is not automatically an object pointer, and an all-zero byte sequence is not universally a foreign typed default. A cross-family numeric conversion or serialization shall be represented by its explicit adapter operation.

On the standard flat-address target profiles, let `W` be the object-pointer storage size in bits specified by the target descriptor. `usize` is the unsigned platform-width integer with range `[0, 2^W - 1]`; `isize` is its same-width signed two's-complement counterpart with range `[-2^(W-1), 2^(W-1)-1]`. They retain their platform-width type-family identity even when an enabled `uW` or `iW` has the same width. Their alignment and calling-convention classification are declared by the target. A capability-pointer, non-flat, or multiple-address-space target shall instead state its platform-integer width and supported size/index domain explicitly; a pointer's metadata-bearing storage size does not imply an integer encoding of that metadata. No `usize`/`isize` definition grants an implicit pointer conversion or guarantees preservation of pointer provenance, permissions, bounds, or capabilities in an integer round trip. Foreign `size_t` and `ptrdiff_t` bindings preserve their declared foreign type identities and require the appropriate explicit mapping.

## 6. C records, arguments, and generated headers

A directly interoperable C record shall have a complete, checked layout contract: size, alignment, field order and offsets, array extents, padding, and each field's transport type. Nested records shall satisfy the same requirement. The core direct C-record interface has no base classes, virtual dispatch, hidden ownership fields, or nontrivial copy/destruction obligation at the call boundary.

Packing and explicit alignment shall follow the provider's C rules, including their interaction. Member accesses shall use the alignment guaranteed by that packed layout. Bit-fields, unions, flexible array members, nonstandard vector fields, and implementation-specific scalar representations require separately declared provider support. Merely matching `sizeof` is insufficient.

Padding bytes are not additional numerical values and are not guaranteed initialized by field-wise construction. The generated header shall describe the exact exported layout. Value equality shall follow its value operation; auxiliary CXXN state shall use the separately authorized metadata representation.

Arguments and return values shall follow the platform's classification rules, including register classes, stack slots, hidden return-storage parameters, extension requirements, and alignment. Source-level by-value passage does not require an identical machine-level mechanism for every record size. By-value lowering shall use exactly the transport selected by the target classification.

For each exported C interface, an implementation shall support generating a C header and an associated ABI descriptor. The header shall contain complete required declarations, transport types, calling-convention and visibility macros, layout checks where expressible, and a C++ `extern "C"` guard. Its stated C dialect shall be explicit. The header shall be usable by the declared C dialect and faithfully describe the public signature and layout.

`NumericResult<T>`, `ExceptionAggregate`, allocating numerical values, and native ownership-bearing objects are not automatically C records. Their exported forms require an explicit layout contract or opaque handle. A checked numeric adapter may expose a status plus output pointer; its declared success/failure behavior shall specify when the output becomes initialized or is modified. Such an adapter does not change the original operation's failure policy without an explicit translation.

## 7. Callbacks and variadic functions

A callback's type includes its foreign linkage and calling convention. Its prototype, return transport, context lifetime, thread/reentrancy conditions, and failure policy shall be known. A captureless CXXN function may become a foreign function pointer when those requirements are satisfied. A closure with state requires an explicit context parameter or provider-defined adapter; a hidden heap allocation or executable trampoline is not implied.

Registration shall state whether the foreign callee retains the callback and context beyond the call. Their code, context storage, and required library shall remain alive until deregistration and any in-flight calls complete. A retained stack-context pointer without a sufficient lifetime is a lifetime error or an unproved programmer obligation under the ordinary diagnostic rules.

Calling an old-style C function without a prototype is outside the direct interface and is `ERROR`. A declared variadic function is supported only when the provider specifies its variadic ABI. The compiler shall perform the required foreign default argument promotions as part of marshalling and evaluate each argument once. Those promotions apply to the variadic call boundary, not ordinary CXXN arithmetic. Types without a declared variadic transport require an explicit conversion or wrapper.

Foreign calls shall declare relevant floating-environment effects. A wrapper shall preserve or translate controls and observable status according to that contract and the CXXN execution-context rules. Native foreign FP clobber shall use the Native boundary rule; a stronger caller shall select the required state-isolating adapter.

## 8. Selected C++ ABI interoperability

`extern "C++"` selects the image's declared C++ provider. The provider contract shall name the applicable ABI and platform supplements. An Itanium-family provider shall identify the exact revision and deviations from the [C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html); exception support additionally identifies its [exception ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi-eh.html). A Microsoft-family provider shall identify its supported compiler/toolset contract and feature subset. No generic `C++` setting denotes every compiler ABI.

The feature declarations shall distinguish:

| Feature | Required agreement |
| --- | --- |
| Free functions and overloads | External names, foreign type identities, qualifiers, calling convention, and return classification. |
| Member functions | Object parameter, ref/cv qualifiers, adjustment thunks, member-pointer representation, and call rules. |
| Class values | Complete/base layout, padding reuse, alignment, triviality classification, and copy/move passage. |
| Inheritance and virtual calls | Base offsets, virtual-base metadata, vtable layout, dispatch adjustments, and construction/destruction dispatch. |
| RTTI | Type descriptor representation, identity, matching, dynamic casts, and required runtime entry points. |
| Construction and destruction | Complete/base/deleting variants, hidden parameters, array cookies, allocation/deallocation pairing, and unwind obligations. |
| Exceptions | Payload layout, ownership, type matching, personality/unwinder behavior, catch/rethrow protocol, and destruction. |
| Library types | Exact supported library ABI, configuration, ownership, and operation contracts. |

Support for free-function linkage does not imply support for the remaining rows. A class shall be imported from a verified foreign declaration/descriptor, or emitted only when every used layout and lifecycle feature is supported. Identical field names and a matching first virtual call are not a class-ABI contract.

Foreign overload resolution shall use imported nominal identities. Templates and library types shall use the provider's declared instantiation or import mechanism. A CXXN generic instance shall enter that boundary through its verified concrete binding.

A provider may generate an adapter with the selected foreign compiler. The resulting interface and dependencies shall be explicit. Unsupported direct class layout, RTTI, inheritance, or library types may be represented by opaque pointers and named operations. An opaque handle shall expose the inspection and destruction operations stated by its interface.

## 9. Lifecycle compatibility

A direct foreign class binding shall preserve both the required machine representation and the actual lifecycle operations. CXXN lifetime operations shall use the verified foreign entries and retain their fixed layout and responsibility assignment.

A complete-object foreign destructor may already destroy members and bases; a deleting variant may additionally release storage. A call descriptor shall state which obligations the selected entry point discharges. Successful return shall discharge exactly the obligations assigned to that entry. A base-object destructor entry is not interchangeable with a complete-object entry.

If foreign construction throws before completion, the selected constructor/provider owns the rollback specified by its ABI. The CXXN adapter shall retire its separately assigned wrapper and storage obligations. A foreign failed constructor does not establish a successfully constructed complete object.

Native lifetime metadata may be eliminated, kept in activation storage, or stored externally when the provider contract permits it. External metadata shall use activation or separate storage; any in-object placement requires the ABI's explicit layout authorization. Its memory and synchronization requirements shall enter the selected capability's semantic contract.

Early base destruction or responsibility transfer is directly permitted only when its lowering satisfies both contracts. A known incompatible lifecycle operation is `ERROR` for that direct binding. An opaque owner may instead expose a deliberate foreign operation without pretending that the underlying object satisfies unrelated native class rules. Abandoning a native wrapper ends its native lifetime under the Abandon rules; it does not implicitly abandon, destroy, or free an independently owned foreign payload. Lifetime termination and storage reuse of a directly bound foreign object shall satisfy its explicit ownership and lifetime contract.

## 10. Exceptions and terminal boundaries

The default C boundary is non-unwinding in both directions, including callbacks. An escaping exception shall dispatch to `ForeignBoundaryFailure` on its originating side. The implementation shall realize this outcome through proof, native boundary machinery, or an explicit adapter. An admitted unproved effect yields ANOMALY; a provably escaping definition yields ERROR. The terminal route follows the selected execution profile.

An explicit adapter may catch a supported language exception on its originating side and return a declared foreign status, or construct a declared translated exception. Its mapping, payload ownership, allocation failure, and unmapped-type behavior shall be specified. No automatic conversion of arbitrary failures into `NumericResult` is implied.

C++ propagation through CXXN frames requires an explicitly enabled provider contract covering search, cleanup, matching, storage, and rethrow. Without that capability, an `extern "C++"` call shall satisfy a non-unwinding contract or use an explicit non-unwinding adapter. Native CXXN `ExceptionRef` and `ExceptionAggregate` are not assumed to be C++ exception records. Sharing an unwinder does not establish matching payload or handler semantics. Identity-preserving rethrow is permitted only when the adapter retains the original compatible record; a newly translated payload has a new identity.

Release destruction failure and Numeric Trap shall follow their terminal routing in the core and error specifications. An adapter shall preserve that terminal outcome.

Foreign `longjmp`, forced unwinding, asynchronous cancellation, and operating-system exception mechanisms require explicit provider support when they cross CXXN frames. Ordinary C linkage does not authorize bypassing native lifetime obligations. A completed terminal event ends its language execution path.

## 11. Storage ownership and library lifetime

Every transferring interface shall identify whether a pointer is borrowed, shared under an explicit protocol, or transferred exclusively. It shall specify extent/alignment, destruction responsibility, deallocation responsibility, allocator context, failure ownership, and the lifetime of required callbacks and code. Ownership metadata shall use the binding descriptor or the handle's declared representation.

Storage shall be released by the original allocation domain or a declared compatible release operation. Using an unrelated C runtime's `free`, a different C++ `delete` variant, or an incompatible allocator is not justified by equal pointer representations. Sized/aligned deletion, array cookies, and constructor failure deallocation follow the selected provider contract.

Opaque ownership adapters shall provide sufficient operations to destroy and release their object exactly once. They may use separate callbacks or one explicitly combined operation. The contract shall identify which state transitions occur on success and failure. Returning a raw pointer does not by itself transfer its storage ownership.

Allocator and disposal callbacks shall obey their declared nonthrowing boundaries. A known violation is `ERROR`; unproved required effects are `ANOMALY`; an actual escaping violation terminates at that boundary. Disabling language exceptions does not turn a failed allocation into a valid object or remove required status handling.

A library shall remain loaded while an object, callback, vtable, RTTI descriptor, exception record, allocator, or shutdown obligation depends on it. Retaining a foreign object does not automatically retain its library unless the binding explicitly supplies that service. Unload shall coordinate outstanding calls and ownership obligations before removing code or data. Cross-library reference cycles require an explicit ownership protocol and are not implicitly garbage collected.

## 12. Startup, shutdown, and support dependencies

The target provider shall connect the CXXN static initialization domain to the platform's native entry mechanisms or explicit host-callable startup/shutdown functions. Exactly one owner invokes each domain's startup and shutdown. The selected link contract shall identify required entry points and linker-retention requirements. Object emission and linker inputs shall preserve live initialization work under archive extraction and section collection. A selected contract export shall publish these requirements in its applicable link record.

Foreign startup may remain an external domain with declared readiness and shutdown gates, or be represented by explicit initialization units in the native dependency graph. Internal foreign order is governed by its provider contract. An opaque foreign initialization unit shall retain its provider-defined internal order. Cross-domain dependency cycles are `ERROR` when established by the declared graph.

Committed CXXN objects retain reverse logical-rank shutdown. A foreign unit's cleanup shall have one registered owner across the native/foreign domains. Failed startup follows the selected failure profile. An adapter shall follow the selected immediate or aggregate failure route.

Support dependencies shall follow the core capability model. The compilation's resolved link requirements shall identify required compiler helpers, stack protection, unwind support, numeric providers, CRT entry mechanisms, and selected C++ facilities. The implementation shall make its selected dependency contract available through its documented build interface. Standard manifest publication shall use the separately selected export capability.

## 13. Conformance and diagnostics

A compiler claiming a target/interface capability shall implement its declared object format, calls, layout, symbol rules, lifetime actions, and failure behavior. Optimization and LTO shall preserve the bound foreign contract. Inlining shall retain the wrapper's bound policy, nominal identities, and ownership.

Known incompatible layouts, conventions, nominal signatures, library ABI settings, ownership release operations, or exception boundaries are `ERROR`. An unknown fact covered by an allowed explicit programmer contract is `ANOMALY`; it does not become a proof. Missing required capabilities cannot be waived by diagnostic suppression.

A binding shall identify its supported direct feature subset or adapter mapping. A direct-compatibility claim shall match the emitted calling convention, arguments, layout, and lifetime entries.

## Advanced generic and conformance ABI boundaries

A `typefn` family is a compile-time entity and has no standard native parameter, register, vtable, or object-file data layout. An associated type is a selected ordinary type only after its conformance witness and concrete arguments are bound. A public CXXN generic instance must preserve the selected constructor, family-specialization and conformance identities in its native symbol or canonical instance contract.

`extern "C"` and verified `extern "C++"` boundaries expose ordinary concrete ABI-compatible types and functions. Compile-time families and witnesses shall be bound to concrete identities before entering that ABI. The chosen foreign boundary uses an explicit concrete wrapper, a versioned verified provider binding, or a separately declared erased ABI adapter. C/C++ exception, RTTI, vtable, alignment and ownership behavior remain governed by their original target/provider profile.

