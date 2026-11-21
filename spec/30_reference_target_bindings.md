<a id="chapter-30-reference-target-bindings"></a>

# CXXN Reference Native Target Bindings Specification

## 1. Complete baseline contracts

This chapter defines two complete baseline bindings: `cxxn.ref.linux-x86_64.core.v1` and `cxxn.ref.windows-x86_64.core.v1`. They instantiate the corresponding [target families](20_target_abi_profiles.md#chapter-20-target-abi-profiles) with fixed interface subsets and explicit runtime absence. They are conformance contracts, not a claim that an existing CXXN compiler or a named foreign toolchain has been tested.

The bindings support ordinary native relocatable objects, C scalar/pointer calls, verified plain C records, and callbacks. A C++ translation unit can consume their generated C interface under `extern "C"`. The Linux binding additionally supports the limited direct C++ symbol subset in Section 4. The supported feature subset shall be exactly the positive claims in its profile record. Additional direct C++ features shall use a separately versioned binding.

Each baseline shall use the explicit absent-runtime bindings in its record for the native CXXN component. The CXXN component/configuration domain selecting it shall set `exceptions.language = false` and use serial native-domain initialization. A capability requiring a missing runtime creates an explicit derived profile with its own complete dependency contract; it does not change the meaning of the baseline identifier. These constraints select a low-level conformance subset rather than changing the language's optional exception, concurrency, or allocation facilities.

All options in the baseline descriptor are fixed. A provider may implement another profile, including a superset, under a distinct identity. Shared boundaries compare their relevant contracts, so an extended image may still use these exact C-compatible function/record interfaces. A different private runtime does not by itself invalidate an unchanged C boundary.

### 1.1 Normative platform references

The following references supply only their specified platform rules. A later webpage edit does not automatically revise a CXXN profile. The named edition and this chapter's subset/options govern. An implementation shall preserve the identified reference edition or equivalent versioned contract in its provider evidence.

| Reference ID | Edition and normative use |
| --- | --- |
| `sysv-amd64-2018` | [System V AMD64 psABI, Version 1.0, January 28, 2018](https://raw.githubusercontent.com/wiki/hjl-tools/x86-psabi/x86-64-psABI-1.0.pdf), LP64 portions of Sections 3 and 4 and Linux conventions relevant to the selected object subset. |
| `itanium-1.86` | [Itanium C++ ABI, revision 1.86](https://refspecs.linuxfoundation.org/cxxabi-1.86.html), Section 5.1 external-name rules restricted by Section 4 below. |
| `ms-x64-call-2025` | [Microsoft x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170), documented revision dated March 19, 2025; default fixed-prototype, scalar/record, callback and supported variadic calls. |
| `ms-x64-layout-2025` | [Microsoft x64 software conventions](https://learn.microsoft.com/en-us/cpp/build/x64-software-conventions?view=msvc-170), documented revision dated March 28, 2025; scalar and ordinary record layout. |
| `ms-pe-coff-2026` | [Microsoft PE/COFF format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format), revision displayed September 10, 2026; AMD64 relocatable COFF sections, symbols, relocations and procedure-data transport. |
| `ms-x64-unwind1` | [Microsoft x64 exception-handling data](https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64?view=msvc-170), `RUNTIME_FUNCTION` and version-1 `UNWIND_INFO` forms without language handlers. |

The Linux call classifier uses the pinned psABI's complete classification for the supported types, including hidden result storage, register exhaustion, stack alignment, and variadic metadata. CXXN evaluation order still governs expression evaluation before ABI marshalling. No change to source integer-promotion rules follows from the foreign variadic boundary.

The Windows classifier uses the default Microsoft x64 convention: its four parameter positions, prescribed integer/floating registers, caller shadow store, and indirect record rules. It does not use a System V red zone. Nonleaf frames use required `.pdata`/`.xdata` unwind metadata even though CXXN language exceptions and a foreign language-unwind bridge are disabled. Metadata permitting a debugger to recover a frame is not permission to bypass its lifetime contract.

## 2. Common scalar, record, and ownership subset

Both profiles use eight-bit bytes, little-endian object representation, flat 64-bit object and function pointers, one default address space, and 16-byte call-stack alignment. A null object or function pointer has zero representation in these bindings. This representation fact does not make arbitrary integers valid pointers or erase pointer lifetime/generation rules. Function pointers and object pointers remain distinct source types.

The scalar descriptor arrays in Section 6 give exact storage and alignment. Signed foreign integers use two's complement. Foreign Boolean objects use one byte and canonical false/true values 0/1. `ffi::c_char` is signed; signed-char and unsigned-char identities remain distinct. The `int`, `long`, and `long long` foreign identities remain distinct even when widths coincide. [Microsoft's data-type contract](https://learn.microsoft.com/en-us/cpp/cpp/data-type-ranges?view=msvc-170) additionally binds its long-double representation to binary64 and wide character to unsigned 16-bit storage. The Linux profile binds long double to the psABI's x87 extended representation in its 16-byte storage slot; its padding is not value data.

A supported direct C record shall be nonempty, use natural packing/alignment and trivial copy/destruction, and contain supported scalar/pointer fields, fixed nonzero arrays of those fields, or recursively supported records. The profile's record-layout capability consists exactly of this grammar. Additional layouts shall use a separately declared capability. Ordinary native CXXN records use their enabled language features.

Every crossing record supplies field offsets, total size/alignment, type identities, and its by-value classification in its binding contract. Its generated C17 header uses the same transport declarations and static size/offset assertions where expressible, with C++ `extern "C"` guards. Assertions do not establish an ownership or exception contract; the descriptor carries those obligations separately. Array members keep exact extents. A scalar-only C function need not carry record metadata it does not use.

A foreign enumeration shall use an explicit integer-transport wrapper with its declared enum-domain validation. `wchar_t` storage is bound for explicitly imported declarations but does not change CXXN's Unicode-scalar `char` identity. Native `usize`/`isize` keep their own family identity; they are not automatic aliases for foreign `size_t`/`ptrdiff_t`.

Callbacks use the same supported C call contract, with explicit context borrowing and retention lifetime. Stateful callback transport shall use the declared context parameter or an explicit adapter. Varargs require a fixed prototype and admit only the profile's supported scalar/pointer variadic transports, with the required foreign default promotions. Other variadic transports shall use a profile declaring their call classification.

A borrowed pointer carries no release authority. An owning pointer transport includes explicit destroy/release callbacks or a named compatible allocator contract. There is no implicit libc `free`, C++ `delete`, or cross-CRT allocation compatibility. A native wrapper cannot independently destroy the members of a foreign object already destroyed by its foreign complete destructor. Ordinary C++ objects can be used through an opaque C interface with its own explicit ownership/effect contract without claiming direct class-layout support.

## 3. Object files and support closure

The Linux binding emits ELF64 relocatable objects with `EM_X86_64`; the Windows binding emits ordinary AMD64 COFF relocatable objects with machine identifier `0x8664`. Neither object is only compiler IR, and neither requires CXXN-specific LTO to link. Reference-compatible C symbols use their exact ASCII source name without a leading underscore. Export/import visibility and any final shared-image export list are explicit binding inputs.

The baseline linker input shall consist of relocatable objects with single-owner definitions and explicit dependencies. Archive extraction shall use an independently declared tool contract. Generic/inline emissions shall use one definition owner or a separately bound COMDAT capability.

The Linux position model is small PIC under the pinned AMD64 relocation rules. Windows uses the standard AMD64 COFF position/relocation model, without claiming that COFF and ELF relocations are interchangeable. Each emitted relocation shall belong to its selected target contract. Native TLS, vector calling conventions, multiversioning, and executable trampolines shall use an extended profile declaring their additional support. A required compiler helper not implemented inside the object becomes an explicit additional dependency and is unavailable until a compatible derived binding selects it.

An admitted cross-frame control transfer shall satisfy the baseline's non-unwinding lifetime boundary. The baseline admits a foreign call or callback only when its non-unwinding requirement is established by verified evidence or by a verified adapter that terminates or translates failure on its originating side before an unwind enters a CXXN frame. An admitted assertion shall satisfy the originating-side terminal boundary required by Chapter 09. If that obligation requires a guard unavailable in this baseline, direct binding is `ERROR`; an explicitly supported guarded or derived binding is required. Other permitted unproved programmer obligations retain their ordinary ANOMALY rules. Numeric and contract terminal outlets remain noncatchable and non-unwinding. The baseline terminal operation emits an x86 `UD2` terminal site; no native code resumes after it. A host handler may report or terminate the image, but resuming a failed CXXN operation is not a supported recovery protocol.

A composed image may contain separately contracted C/C++ components and their explicit CRT, exception-runtime, and library dependencies. Those remain foreign component obligations; they do not create an implicit CXXN runtime requirement or change an unchanged supported C boundary. The absence of native-component CRT support is exact. Its emitted support references shall be exactly the explicit dependency closure of that binding. An explicitly selected diagnostic/support adapter may provide reporting through a derived dependency contract. The general language's Debug/Release semantics still apply to the capabilities actually enabled; this runtime-free baseline does not promise debug aggregation for disabled language exceptions.

### 3.1 Native numerical provider binding

The ABI profile shall determine object format, transport, instruction availability, and support dependencies. Ordinary numerical execution shall additionally bind the `numeric.native` capability described in Chapter 29. That capability shall publish Native integer domain outcomes, floating controls/clobber, NaN/subnormal behavior, and permitted transformations or approximations for the supported widths/formats. A Native lowering shall use the ABI profile's declared instruction set and dependency closure. A stronger numerical operation shall bind the corresponding checked/reporting/accuracy capability. Thus a foreign transport profile and a numerical execution profile have separate, explicit identities.

## 4. Linux direct C++ symbol subset

The Linux baseline's `cpp_symbol` claim covers C++03 non-template free functions with externally linked ASCII identifiers in ordinary namespaces. Parameter and return types are the supported foreign scalar/pointer types, or lvalue references to those types, with ordinary cv qualification. Function overloads use their actual imported foreign nominal types and the pinned Itanium external-name grammar. The direct symbol subset shall consist exactly of this free-function and type grammar.

A reference parameter has the selected ABI's reference transport and a live referent obligation. It does not become a nullable optional reference. Return types and all effect/ownership conditions remain part of the binding even where the external name does not encode them. An imported declaration shall match those conditions independently of successful symbol lookup.

For example, a global foreign `int add(int,int)` has external name `_Z3addii`, while global foreign `long add(long,long)` has `_Z3addll`. The same bit width of a native CXXN type is insufficient to choose either foreign overload. The descriptor names the actual foreign declarations and their non-unwinding contract.

The Linux direct C++ claim shall cover the symbol subset above. A separately verified adapter may call such facilities on its foreign side and expose a supported non-unwinding boundary. Its required compiler, runtime, library ABI switches, and release operations are explicit additional contracts.

## 5. Explicit static-domain entry

A baseline image with dynamic native static objects shall expose two C entry points with prototypes `void start(void)` and `void stop(void)`. These are schematic names; the resolved link contract shall bind their actual unique external symbols. A selected standard export shall place them in `link_requirements`. The explicit host startup/shutdown caller shall own that domain.

The host calls `start` exactly once before any exported operation requiring domain readiness, and calls `stop` exactly once after those operations and retained callbacks cease. The state transition is `Cold -> Starting -> Ready -> Stopping -> Stopped`. Reentry, a second start/stop, start after stop, and access before readiness violate the explicit domain contract. A proven invalid transition is `ERROR`; an unproved host obligation is `ANOMALY`, with the existing contract-failure rule at a validated boundary.

Startup is serial in the language's logical rank order, and shutdown uses reverse logical rank. Constant objects with destruction obligations participate in the same registry. A terminal initializer failure does not return success or call a hidden catch-all collector. There is no automatic restart after partial startup. Domain storage and registration work are statically owned by the image, with no hidden heap allocation. An object with no dynamic startup or shutdown obligation creates no entry point or registry solely to satisfy this section.

The host retains the image and all required code while any exported reference, callback, object destructor, or disposal operation depends on it. Unloading an image cannot discharge live obligations by discarding its code. A richer dynamic loader, parallel startup scheduler, or CRT integration uses a separately declared provider contract.

## 6. Normative profile records

The following reference JSON records instantiate the [public ABI schema](29_public_contract_schemas.md#chapter-29-public-contract-schemas). A claim to a reference target shall implement its stated target facts. An implementation may retain those facts internally; producing these public records and their SHA-256 identities shall follow a selected `tooling.contract_export` request. Contract strings such as `core.records.v1` refer to the exact clauses of this chapter. `none` means intentionally unsupported or absent. Each complete reference document includes its reference list. Pretty-printing aids reading; canonical encoding determines the displayed fingerprint.

`options` has exactly these fields for these profiles: `plain_char` (`signed`), `packing` (`natural`), `short_enums` (`false`), `foreign_enums` (`false`), `vector_abi` (`false`), `record_varargs` (`false`), `language_exceptions` (`false`), `static_schedule` (`serial`), `crt_libraries` (empty set), and `cxx_library` (`none`). Their values cannot be overridden while retaining the profile identifier.

### 6.1 Linux ELF64

```json
{
  "format": "cxxn.contract",
  "version": 1,
  "kind": "abi_profile",
  "payload": {
    "profile_id": "cxxn.ref.linux-x86_64.core.v1",
    "family": "x86_64-linux-sysv-elf",
    "revision": 1,
    "machine": {
      "architecture": "x86_64",
      "instruction_set": [
        "sse2",
        "x86_64_baseline"
      ],
      "byte_order": "little",
      "byte_bits": 8,
      "pointer_model": "flat64",
      "object_pointer_bytes": 8,
      "function_pointer_bytes": 8,
      "pointer_alignment": 8,
      "data_model": "LP64",
      "stack_alignment": 16,
      "address_spaces": [
        "default"
      ]
    },
    "object": {
      "format": "ELF64",
      "revision": "sysv-amd64-2018",
      "machine_id": "EM_X86_64:62",
      "relocation_contract": "sysv-amd64-2018.section4.4",
      "position_model": "small-pic",
      "symbol_contract": "core.ascii-c-symbols.v1",
      "archive_contract": "objects-only",
      "comdat_contract": "none",
      "unwind_contract": "sysv-amd64-2018.eh-frame.no-personality",
      "tls_contract": "none"
    },
    "c": {
      "dialect": "C17",
      "scalar_contract": "core.scalars.v1",
      "record_contract": "core.records.v1",
      "call_contract": "sysv-amd64-2018.lp64",
      "variadic_contract": "core.scalar-varargs.v1",
      "callback_contract": "core.nonunwinding-callback.v1",
      "header_contract": "core.c17-header.v1",
      "scalars": [
        {
          "name": "c_bool",
          "size": 1,
          "alignment": 1,
          "representation": "canonical-0-1",
          "transport": "integer"
        },
        {
          "name": "c_char",
          "size": 1,
          "alignment": 1,
          "representation": "signed-twos-8",
          "transport": "integer"
        },
        {
          "name": "c_double",
          "size": 8,
          "alignment": 8,
          "representation": "ieee-binary64",
          "transport": "sse-double"
        },
        {
          "name": "c_float",
          "size": 4,
          "alignment": 4,
          "representation": "ieee-binary32",
          "transport": "sse-float"
        },
        {
          "name": "c_int",
          "size": 4,
          "alignment": 4,
          "representation": "signed-twos-32",
          "transport": "integer"
        },
        {
          "name": "c_llong",
          "size": 8,
          "alignment": 8,
          "representation": "signed-twos-64",
          "transport": "integer"
        },
        {
          "name": "c_long",
          "size": 8,
          "alignment": 8,
          "representation": "signed-twos-64",
          "transport": "integer"
        },
        {
          "name": "c_long_double",
          "size": 16,
          "alignment": 16,
          "representation": "x87-80-in-128",
          "transport": "sysv-x87"
        },
        {
          "name": "c_ptrdiff",
          "size": 8,
          "alignment": 8,
          "representation": "signed-twos-64",
          "transport": "integer"
        },
        {
          "name": "c_schar",
          "size": 1,
          "alignment": 1,
          "representation": "signed-twos-8",
          "transport": "integer"
        },
        {
          "name": "c_short",
          "size": 2,
          "alignment": 2,
          "representation": "signed-twos-16",
          "transport": "integer"
        },
        {
          "name": "c_size",
          "size": 8,
          "alignment": 8,
          "representation": "unsigned-64",
          "transport": "integer"
        },
        {
          "name": "c_uchar",
          "size": 1,
          "alignment": 1,
          "representation": "unsigned-8",
          "transport": "integer"
        },
        {
          "name": "c_uint",
          "size": 4,
          "alignment": 4,
          "representation": "unsigned-32",
          "transport": "integer"
        },
        {
          "name": "c_ullong",
          "size": 8,
          "alignment": 8,
          "representation": "unsigned-64",
          "transport": "integer"
        },
        {
          "name": "c_ulong",
          "size": 8,
          "alignment": 8,
          "representation": "unsigned-64",
          "transport": "integer"
        },
        {
          "name": "c_ushort",
          "size": 2,
          "alignment": 2,
          "representation": "unsigned-16",
          "transport": "integer"
        },
        {
          "name": "c_wchar",
          "size": 4,
          "alignment": 4,
          "representation": "signed-twos-32",
          "transport": "integer"
        },
        {
          "name": "function_pointer",
          "size": 8,
          "alignment": 8,
          "representation": "code-address64-null-zero",
          "transport": "pointer"
        },
        {
          "name": "object_pointer",
          "size": 8,
          "alignment": 8,
          "representation": "flat64-null-zero",
          "transport": "pointer"
        }
      ]
    },
    "cpp": {
      "provider": {
        "name": "cxxn.ref.itanium-symbol-core",
        "revision": "1.86-subset1"
      },
      "dialect": "C++03",
      "symbol_contract": "core.itanium-symbols.v1",
      "class_contract": "none",
      "lifetime_contract": "none",
      "rtti_contract": "none",
      "exception_contract": "none",
      "library_contract": "none"
    },
    "runtime": {
      "crt": "none",
      "crt_linkage": "none",
      "allocation_contract": "explicit-callback-ownership.v1",
      "startup_contract": "host-domain-serial.v1",
      "terminal_contract": "x86.ud2.no-unwind.v1",
      "native_exception_contract": "none",
      "foreign_unwind": "forbidden",
      "support": []
    },
    "features": {
      "native_object": true,
      "c_call": true,
      "c_record": true,
      "c_callback": true,
      "cpp_symbol": true,
      "cpp_class": false,
      "cpp_lifetime": false,
      "cpp_rtti": false,
      "cpp_exception": false,
      "cpp_stdlib": false
    },
    "references": [
      {
        "id": "sysv-amd64-2018",
        "title": "System V AMD64 psABI",
        "revision": "1.0-2018-01-28",
        "location": "https://raw.githubusercontent.com/wiki/hjl-tools/x86-psabi/x86-64-psABI-1.0.pdf",
        "sections": [
          "3",
          "4"
        ]
      },
      {
        "id": "itanium-1.86",
        "title": "Itanium C++ ABI",
        "revision": "1.86",
        "location": "https://refspecs.linuxfoundation.org/cxxabi-1.86.html",
        "sections": [
          "5.1"
        ]
      }
    ],
    "options": {
      "plain_char": "signed",
      "packing": "natural",
      "short_enums": false,
      "foreign_enums": false,
      "vector_abi": false,
      "record_varargs": false,
      "language_exceptions": false,
      "static_schedule": "serial",
      "crt_libraries": [],
      "cxx_library": "none"
    }
  },
  "extensions": []
}
```

The canonical document SHA-256 is `040d5a9306e1f7e9e442900631f0d124f5932e65cff0debf31292ea9bd1e1cf7`.

### 6.2 Windows AMD64 COFF

```json
{
  "format": "cxxn.contract",
  "version": 1,
  "kind": "abi_profile",
  "payload": {
    "profile_id": "cxxn.ref.windows-x86_64.core.v1",
    "family": "x86_64-windows-msvc-coff",
    "revision": 1,
    "machine": {
      "architecture": "x86_64",
      "instruction_set": [
        "sse2",
        "x86_64_baseline"
      ],
      "byte_order": "little",
      "byte_bits": 8,
      "pointer_model": "flat64",
      "object_pointer_bytes": 8,
      "function_pointer_bytes": 8,
      "pointer_alignment": 8,
      "data_model": "LLP64",
      "stack_alignment": 16,
      "address_spaces": [
        "default"
      ]
    },
    "object": {
      "format": "COFF-AMD64",
      "revision": "ms-pe-coff-2026",
      "machine_id": "IMAGE_FILE_MACHINE_AMD64:0x8664",
      "relocation_contract": "ms-pe-coff-2026.amd64",
      "position_model": "standard-coff",
      "symbol_contract": "core.ascii-c-symbols.v1",
      "archive_contract": "objects-only",
      "comdat_contract": "none",
      "unwind_contract": "win64.unwind1.no-language-handlers",
      "tls_contract": "none"
    },
    "c": {
      "dialect": "C17",
      "scalar_contract": "core.scalars.v1",
      "record_contract": "core.records.v1",
      "call_contract": "ms-x64-call-2025.default",
      "variadic_contract": "core.scalar-varargs.v1",
      "callback_contract": "core.nonunwinding-callback.v1",
      "header_contract": "core.c17-header.v1",
      "scalars": [
        {
          "name": "c_bool",
          "size": 1,
          "alignment": 1,
          "representation": "canonical-0-1",
          "transport": "integer"
        },
        {
          "name": "c_char",
          "size": 1,
          "alignment": 1,
          "representation": "signed-twos-8",
          "transport": "integer"
        },
        {
          "name": "c_double",
          "size": 8,
          "alignment": 8,
          "representation": "ieee-binary64",
          "transport": "sse-double"
        },
        {
          "name": "c_float",
          "size": 4,
          "alignment": 4,
          "representation": "ieee-binary32",
          "transport": "sse-float"
        },
        {
          "name": "c_int",
          "size": 4,
          "alignment": 4,
          "representation": "signed-twos-32",
          "transport": "integer"
        },
        {
          "name": "c_llong",
          "size": 8,
          "alignment": 8,
          "representation": "signed-twos-64",
          "transport": "integer"
        },
        {
          "name": "c_long",
          "size": 4,
          "alignment": 4,
          "representation": "signed-twos-32",
          "transport": "integer"
        },
        {
          "name": "c_long_double",
          "size": 8,
          "alignment": 8,
          "representation": "ieee-binary64",
          "transport": "sse-double"
        },
        {
          "name": "c_ptrdiff",
          "size": 8,
          "alignment": 8,
          "representation": "signed-twos-64",
          "transport": "integer"
        },
        {
          "name": "c_schar",
          "size": 1,
          "alignment": 1,
          "representation": "signed-twos-8",
          "transport": "integer"
        },
        {
          "name": "c_short",
          "size": 2,
          "alignment": 2,
          "representation": "signed-twos-16",
          "transport": "integer"
        },
        {
          "name": "c_size",
          "size": 8,
          "alignment": 8,
          "representation": "unsigned-64",
          "transport": "integer"
        },
        {
          "name": "c_uchar",
          "size": 1,
          "alignment": 1,
          "representation": "unsigned-8",
          "transport": "integer"
        },
        {
          "name": "c_uint",
          "size": 4,
          "alignment": 4,
          "representation": "unsigned-32",
          "transport": "integer"
        },
        {
          "name": "c_ullong",
          "size": 8,
          "alignment": 8,
          "representation": "unsigned-64",
          "transport": "integer"
        },
        {
          "name": "c_ulong",
          "size": 4,
          "alignment": 4,
          "representation": "unsigned-32",
          "transport": "integer"
        },
        {
          "name": "c_ushort",
          "size": 2,
          "alignment": 2,
          "representation": "unsigned-16",
          "transport": "integer"
        },
        {
          "name": "c_wchar",
          "size": 2,
          "alignment": 2,
          "representation": "unsigned-16",
          "transport": "integer"
        },
        {
          "name": "function_pointer",
          "size": 8,
          "alignment": 8,
          "representation": "code-address64-null-zero",
          "transport": "pointer"
        },
        {
          "name": "object_pointer",
          "size": 8,
          "alignment": 8,
          "representation": "flat64-null-zero",
          "transport": "pointer"
        }
      ]
    },
    "cpp": {
      "provider": "none",
      "dialect": "none",
      "symbol_contract": "none",
      "class_contract": "none",
      "lifetime_contract": "none",
      "rtti_contract": "none",
      "exception_contract": "none",
      "library_contract": "none"
    },
    "runtime": {
      "crt": "none",
      "crt_linkage": "none",
      "allocation_contract": "explicit-callback-ownership.v1",
      "startup_contract": "host-domain-serial.v1",
      "terminal_contract": "x86.ud2.no-unwind.v1",
      "native_exception_contract": "none",
      "foreign_unwind": "forbidden",
      "support": []
    },
    "features": {
      "native_object": true,
      "c_call": true,
      "c_record": true,
      "c_callback": true,
      "cpp_symbol": false,
      "cpp_class": false,
      "cpp_lifetime": false,
      "cpp_rtti": false,
      "cpp_exception": false,
      "cpp_stdlib": false
    },
    "references": [
      {
        "id": "ms-x64-call-2025",
        "title": "Microsoft x64 calling convention",
        "revision": "2025-03-19",
        "location": "https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170",
        "sections": [
          "default-call",
          "parameter-passing",
          "return-values",
          "varargs"
        ]
      },
      {
        "id": "ms-x64-layout-2025",
        "title": "Microsoft x64 software conventions",
        "revision": "2025-03-28",
        "location": "https://learn.microsoft.com/en-us/cpp/build/x64-software-conventions?view=msvc-170",
        "sections": [
          "aggregate-layout",
          "scalar-types"
        ]
      },
      {
        "id": "ms-pe-coff-2026",
        "title": "Microsoft PE/COFF format",
        "revision": "2026-09-10",
        "location": "https://learn.microsoft.com/en-us/windows/win32/debug/pe-format",
        "sections": [
          "amd64-relocations",
          "coff-file-header",
          "sections",
          "symbols"
        ]
      },
      {
        "id": "ms-x64-unwind1",
        "title": "Microsoft x64 unwind data",
        "revision": "UNWIND_INFO-1",
        "location": "https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64?view=msvc-170",
        "sections": [
          "RUNTIME_FUNCTION",
          "UNWIND_INFO"
        ]
      }
    ],
    "options": {
      "plain_char": "signed",
      "packing": "natural",
      "short_enums": false,
      "foreign_enums": false,
      "vector_abi": false,
      "record_varargs": false,
      "language_exceptions": false,
      "static_schedule": "serial",
      "crt_libraries": [],
      "cxx_library": "none"
    }
  },
  "extensions": []
}
```

The canonical document SHA-256 is `76b4d6ebc60b264456ff146431d0be2cedd33a9175519fbcdeedf6d8fd987f72`.

## 7. Boundary compatibility and diagnostic rules

A provider claiming either baseline shall implement exactly its selected feature subset and fixed options. Packing, long-double format, C++ ABI, CRT, and exception support shall use the record's bound values. Producer identity/version and actual selected linker/tool inputs are recorded in build context; conformance is to the versioned target contract, not equality of compiler brand names.

A function or record imported from C/C++ is directly usable only when its own binding contract matches the supported subset. A compatible machine architecture alone is insufficient. A verified adapter may explicitly translate to a supported interface with its own ownership and failure contract. Unsupported requested class/RTTI/exception features produce `ERROR` for direct use; an unproved obligation expressly permitted by the language produces `ANOMALY` and is never represented as verified compatibility.

CXXN floating result/status rules, checked integer arithmetic, destruction responsibilities, and explicit terminal behavior remain in force inside native functions. Their ABI marshalling shall preserve required observable representations, including signaling NaNs where an inspection contract requires it. A foreign function's internal arithmetic follows its declared foreign contract; this profile does not retrofit CXXN numerical guarantees onto arbitrary C or C++ code.

