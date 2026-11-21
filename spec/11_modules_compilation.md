<a id="chapter-11-modules-compilation"></a>

# CPN26 Modules and Separate Compilation Specification

## 1. Scope and compilation model

This chapter defines the Core root-unit boundary and the selected capabilities for named modules, interface and implementation units, partitions, imports, exports, declaration identity, separate compilation, and native linkage. `shall` denotes a requirement. A module is a source-level ownership and visibility boundary; an image is the executable or independently loaded lifetime domain defined by the configuration specification. Module binding uses compile-time state; runtime support follows the selected execution facilities.

### 1.1 Core root unit

With `compilation.modules = false`, a Core compilation shall accept one headerless source unit containing the ordinary declarations supported by its selected capabilities. The compilation request shall bind its edition, target, configuration, and logical root identity before declaration binding. An implementation may supply a documented stable default root identity or accept one from the request. The identity shall distinguish independently owned roots; repeated use of the same logical input under the same request shall preserve that identity. Physical addresses, wall time, worker order, and output paths shall remain outside semantic identity.

The root owns its declarations and local static ordering. Module-qualified ownership rules elsewhere in the standard shall apply to this root owner where the operation needs an owner, including nominal types, generic catalogues, generated declarations, and destruction responsibility. The compiler may represent root and declaration identities by local handles with the information needed to establish equality and ownership. A request that externally publishes such identities shall assign the stable logical fields required by its selected interface contract. An enabled reflection provider shall represent this logical owner with the existing `Module` metadata kind; it shall preserve the root's identity without introducing a source module declaration or namespace prefix. Name queries shall follow the ordinary absent-source-name result for a headerless root.

A Core native object may expose or reference foreign symbols under Chapter 09. The target's ABI contract and linker requirements shall determine that boundary. A native object link adds no CPN26 interface-import requirement by itself. Required local static startup and shutdown shall use the root's ordering and its explicit image entry contract. The root model needs source and internal semantic state; external module maps and exported metadata are selected interfaces.

### 1.2 Selected compilation facilities

`compilation.modules` shall enable the named-unit and import/export rules in Sections 2–9. Without `compilation.separate`, a module compilation shall obtain its semantic dependencies from the explicitly selected joint source-input set; an import denotes a logical source dependency inside that compilation. `compilation.separate` shall enable independently compiled CPN26 interface artifacts and their provider-declared versioned protocol. It requires `compilation.modules`.

`tooling.contract_export` shall enable the public records in Chapter 29 independently of these two facilities. With that capability selected, a requested applicable export shall use its standard encoding. With it disabled, logical maps, contracts, definition records, and capability descriptions in this chapter denote semantic information held internally or in the selected private protocol. Equality, ownership, edition, effect, configuration, and ABI checks shall apply in either representation. A compiler may use direct records or opaque collision-resolving identifiers; serialization and fingerprint algorithms belong to the selected interchange protocol.

A source construct or artifact request requiring a disabled or unavailable capability shall yield ERROR at that use. Source `export` selects module visibility; `tooling.contract_export` selects external contract serialization. These selections have distinct effects.

### 1.3 Dependency classes

The following dependencies are distinct:

| Dependency | Meaning |
| --- | --- |
| Type identity | A declaration needs another nominal type's identity without requiring its definition. |
| Complete interface | Compilation needs definitions, constraints, layouts, or exported operations from another unit. |
| Native linkage | Generated code or data references a definition provided by another artifact. |
| Initialization | An initializer requires another object's commitment or a module readiness barrier. |
| Lifetime | Code, data, ownership, or callbacks require a loaded image to remain alive. |

An import establishes the stated compilation dependency. It does not by itself execute an initializer, transfer storage ownership, or authorize unloading. A linker reference does not prove that the referenced declaration has a compatible type or that its storage is initialized.

## 2. Source grammar and unit roles

The module grammar is:

```ebnf
module-unit = { configuration-declaration }, module-header,
              { import-declaration }, { top-level-declaration };
module-header = [ "export" ], "module", module-name,
                [ ":", partition-name ], ";";
module-name = identifier, { ".", identifier };
partition-name = identifier, { ".", identifier };
import-declaration = [ "export" ], "import", [ "type" ],
                     [ identifier, "=" ], import-target, ";";
import-target = module-name | ":", partition-name;
export-declaration = "export", declaration
                   | "export", "{", { declaration }, "}";
```

`declaration` includes the native function, object, type, alias, generic, and foreign declarations permitted by their respective grammars. An exported native function prototype is written `export declare ReturnType name(parameters);`. A function definition retains `ReturnType name(parameters) { body }`. Object initialization remains `Type name(arguments);`.

Each named compilation unit has one module header. Imports occupy its import preamble and cannot appear in a function body, runtime conditional, loop, or construction block. Configuration declarations preceding the header supply file settings subject to their ordinary frozen boundaries; they cannot change an imported module's identity or compiled defaults.

| Header | Role |
| --- | --- |
| `export module M;` | Primary interface of M. |
| `module M;` | Ordinary implementation unit of M. |
| `export module M:P;` | Interface partition P owned by M. |
| `module M:P;` | Private implementation partition P owned by M. |

An importable module has exactly one primary interface. It may have multiple ordinary implementation units and uniquely named partitions. A partition name cannot identify both an interface and an implementation partition. The primary interface determines the public surface; merely compiling an interface partition does not publish it.

An ordinary implementation unit implicitly imports its own primary interface when one exists. Partitions have no implicit import of the primary interface, so that a primary may depend on a partition without creating a hidden cycle. Required partition imports are explicit. An implementation unit may define declarations previously exported by the interface without repeating `export`; it may not create a new exported declaration. Private implementation partitions likewise cannot introduce exports.

A build may contain a non-importable implementation-only module. It has no primary interface and cannot be the target of a named external module import. A source file without a module header shall use the Core root-unit identity from Section 1.1. In a selected multi-unit module compilation, the logical map shall assign each such root its distinct owner. A root may expose an entry point or foreign symbols under their separate contracts; its namespace belongs to that root.

Module composition shall bind declarations through module interfaces. Generated source shall be an ordinary declared input. Foreign preprocessing shall remain within its binding provider and publish typed declarations to CPN26.

## 3. Module maps and logical identities

A module compilation shall establish the logical mapping described in this section. An internal table or a declared private input protocol may carry that information. A selected public export shall use the [module-map and semantic-interface schemas](29_public_contract_schemas.md#chapter-29-public-contract-schemas), including their identity and fingerprint rules. A provider may retain private AST material alongside an exported record.

Before compilation, the module map shall resolve each reference to one logical module and selected interface source or artifact. Declared version/content identities shall determine that resolution.

The map supplies the following data:

| Field | Requirement |
| --- | --- |
| `package_identity` | The stable logical package identity owning the module declarations. It is not a build directory or a static-domain configuration override. |
| `identity_namespace` | The resolved namespace used in the static-object identity tuple, under the static-lifetime configuration contract. |
| `module_identity` | The canonical dotted module name, as a case-sensitive UTF-8 string. |
| Unit mapping | Primary interface, partitions, ordinary implementation units, and normalized logical source paths. |
| Import resolution | Exact logical module identities and selected artifact or source contracts for imported names. |
| Configuration | Resolved module defaults and required target, capability, provider, and resource contracts. |
| Initialization | The `initialization_dependencies` module identities and collected object descriptors. |
| Artifacts | Selected interface material, required native objects/libraries, and available definitions for instantiation. |

The map may be supplied through the project/package configuration, the compiler invocation, or a separate equivalent input. Its semantic fields shall establish the identities and dependencies in this section. Canonical public encoding applies when `tooling.contract_export` selects its standard exchange representation.

The owning logical identity is the pair `(package_identity, module_identity)`. A partition changes unit organization, not the owning module. An ordinary implementation unit is distinguished by its normalized logical source path. Import aliases, output filenames, checkout locations, and compiler worker numbers do not change declaration ownership. Changing a static-domain identity namespace does not rename a public type; the static namespace and the owning package identity are distinct logical fields.

Every identifier component of a module name, partition name, import alias, and CPN26 declaration path uses the source specification's NFC identity before the canonical dotted or qualified path is formed. The module map uses those canonical names. Package-identity strings, static identity-namespace strings, logical file paths, and explicit ABI symbol strings retain their own exact-byte contracts and are not globally normalized as identifiers. Source profile and Unicode-version requirements are resolved before tokenization and retained in interface and cache contracts.

Logical source paths follow the static-lifetime normalization rules: project-relative, `/` separators, no absolute prefix or unresolved `..`, and case-sensitive spelling. Different physical locations may implement the same mapped logical path. Two distinct inputs claiming the same unit identity are an error unless the map explicitly selects one alternative before compilation.

Within a source unit, one module spelling resolves to one module identity. A program using multiple incompatible versions shall assign them separately named logical instances with distinct canonical identities and compatible explicit interfaces. Relabeling an artifact is not permission to rewrite its existing type identities or native symbols.

## 4. Qualified names, imports, and aliases

An ordinary import preserves the module's full namespace path. For example:

```text
import engine.geometry;
import std.mem;
```

makes exported declarations accessible through `engine::geometry::...` and `std::mem::...`. It does not introduce implicit `geometry::...` or `mem::...` shortcuts and does not import each declaration unqualified. Intermediate namespace components are naming containers; importing `std.mem` does not also import the root `std` module or other `std` submodules.

An explicit alias changes only the importing unit's lookup path:

```text
import geo = engine.geometry;
```

This declaration provides `geo::...`. It does not independently introduce the canonical `engine::geometry::...` path. A separate ordinary import may provide that path. Both imports then refer to the same declarations and cannot create a second copy of a static object or type.

Declarations written in a module belong to its canonical namespace prefix. Ordinary lexical and member lookup operate within that prefix. A namespace declaration may extend the module's own nested namespaces; it cannot acquire ownership of imported declarations. The compiler preserves the owning module identity even when aliases or re-exports provide several source-level paths.

An alias colliding with another declaration or incompatible namespace binding in the same scope is `ERROR`. Distinct declarations at one qualified lookup path shall follow the conflict/overload rules, independently of import order. Repeated compatible imports of one identity are idempotent. Overload sets are formed by the function rules from declarations legitimately visible at the selected path, not by searching arbitrary imported implementation bodies.

Importing a module exposes its public interface only. Source code cannot name a hidden declaration by guessing its mangled symbol or qualifying it with an implementation partition's filename. Foreign symbol binding remains an explicit ABI operation and does not grant native source access rights.

## 5. Exports and partitions

`export` marks module visibility. It does not change class member access, constness, lifetime permissions, exception effects, allocation ownership, or the type's selected representation. Exporting a class definition makes its required type contract reachable; its private members remain private.

An export block applies to the declarations directly contained in that block. Exported aliases preserve the identity of their targets. An exported object definition denotes one object owned by its module, regardless of how many units import its declaration. Each importer shall refer to the module-owned object identity.

A partition is imported within its owning module using `import :P;`. A partition import cannot declare a namespace alias; its declarations already belong to the owning module's prefix. Qualified external references such as `import M:P;` are not part of the grammar. A module needing independently importable subcomponents shall give them independent module names.

An ordinary partition import provides the declarations admitted by the partition's internal interface to that importing unit. It does not publish them to clients. A primary interface's `export import :P;` incorporates P's exported declarations into the same module public surface. It does not add P as an extra namespace level. Private declarations reachable for implementation remain hidden. Re-exporting a private implementation partition is `ERROR`.

An external `export import other.module;` re-exports that module's public canonical path. A client importing the facade may therefore use `other::module::...`; ownership remains with the other module. An aliased re-export, `export import short_name = other.module;`, instead exports an alias inside the facade's namespace: clients use `facade::short_name::...`. It does not additionally introduce the other module's canonical path. A facade can provide a direct public alias declaration when it intends a different surface.

Ordinary imports are not automatically re-exported. A public signature may depend on a non-re-exported declaration when the information required to type-check and use that signature is reachable in the interface artifact. Reachability does not make the dependency's namespace source-visible. A caller may use a deduced return value while needing an explicit import to spell the dependency's qualified type name.

## 6. Type imports and cycles

`import type M;` and `import type alias = M;` introduce the exported nominal type identities in M's declaration index without importing complete definitions or executable operations. The same qualification rules apply as for ordinary imports. A type import can provide an incomplete class/struct/union identity, an enum identity, or a declared generic type constructor with its recorded parameter signature.

Pointers, references, function declarations, and other constructs permitted to mention incomplete types may use these identities. Type import alone does not provide field layout, size, alignment, enum values, constructors, destructor effects, callable functions, constant values, or generic bodies. A use requiring such information needs a complete import or an explicitly sufficient definition contract. An alias is usable through a type import only when the declaration index already resolves its target identity without performing unavailable evaluation or instantiation.

The compiler may obtain declaration indexes for a mutually dependent group before resolving complete interfaces. Type-identity cycles are permitted. A layout requiring incomplete members by value, a cyclic alias without a concrete identity, or an instantiation requiring unavailable definitions is still an error; a type import does not make an impossible recursive layout finite.

Complete-interface dependencies shall be acyclic. A cycle composed of ordinary full imports is `ERROR`. Type-import edges do not count as complete-interface edges: a mixed dependency group is permitted when its full-import subgraph is acyclic and its uses need no unavailable completeness. Declaration-index extraction shall use compile-time declaration material.

`export import type M;` re-exports only the type-identity view. A later compatible full import supplies completeness for those same identities. Opaque and complete views shall preserve one type identity. Initialization cycles are checked separately and remain `ERROR`, even when the source type-import cycle is valid.

## 7. Canonical declarations and definitions

A canonical declaration identity contains its owning module, namespace/type path, declaration kind, and the overload or specialization identity required by the type system. Partition placement and import aliases are not part of that identity. Repeated declarations shall agree on type, linkage, visibility obligations, constraints, effects, representation, and ABI-relevant configuration.

A non-generic function or object has one owning definition in the linked module instance. Its definition may be in an implementation unit while its declaration is in an interface. A declaration does not become another definition because a compiler imports or caches it. Two independently written ordinary definitions are not merged merely because a linker permits weak symbols.

The same definition may be emitted into multiple artifacts when the language permits interface-defined bodies or generic specialization sharing. Such emissions shall identify the same canonical definition and specialization, including bound configuration and provider requirements. They denote one entity where address or object identity is observable. COMDAT or weak-linkage mechanisms are lowering choices, not permission to merge incompatible definitions.

A definition record contains its normalized declaration/body representation, canonical referenced declarations, effective semantic settings, and required support contracts. Whitespace and comments do not change this record. Different behavior-affecting literals, selected providers, lookup bindings, or policies do. A provider may use a fingerprint for indexing and shall retain the complete or collision-resolving information needed to establish identity. A standard public export shall use Chapter 29's fingerprint projection.

Conflicting records for one required entity are `ERROR` before a conforming final image is accepted. This requirement applies to declarations reconstructed from source and to imported native metadata. The compiler is not required to infer semantic equivalence between unrelated definitions in order to waive a conflict.

## 8. Exported generics and definition environments

An exported generic uses the generic declaration grammar, for example `export generic<type T> ...`. Its interface shall make reachable every definition and semantic fact required for its supported instantiations. A prototype without sufficient definition material cannot promise arbitrary later instantiation.

The definition environment includes resolved nondependent references, declared constraints, relevant defaults, effective numeric/lifetime policies, required capabilities, and provider identities. Dependent lookup and substitution follow the generics specification. Instantiation shall resolve nondependent names in that captured definition environment.

Private helpers, types, and constants may accompany the interface as sealed implementation dependencies. Their visibility remains private, but their canonical definitions must be available wherever required instantiation or constant evaluation occurs. Exported generics shall retain the private lookup visibility of their sealed dependencies.

Specialization shall combine the captured definition contract with its declared dependent generic/policy arguments. The resulting operation bindings shall follow the core definition-binding model.

An implementation may supply source definitions, a supported serialized representation, or an explicitly closed set of precompiled specializations. The artifact shall state which alternatives it supplies. An unsupported request shall produce ERROR for the requested specialization/capability. Consumers unable to read a compiler-private representation may use supplied source under the captured contract or a declared compatible provider.

A repeated specialization's identity includes its generic declaration, canonical arguments, admitted policy parameters, and effective ABI contract. Equivalent emissions do not create one module static per importer. A specialization with static objects uses its canonical specialization identity in the existing static-object tuple and receives one destruction registration per actual owned instance.

### 8.1 Type-constructor and conformance exports

A public `typefn`-kind export shall include its finite recursive kind signature, fixed prefix and any final pack kind, constant parameter types, selected specialization catalogue, and captured definition environment. A partial application shall publish its base constructor and captured arguments; an inline constructor shall publish its bound mapping identity. Public associated contracts shall publish their declared requirements and the catalogue binding appropriate to their subject: a known subject captures its catalogue, while a symbolic subject captures Chapter 27's subject-owner resolution recipe. Instantiation shall obtain the actual canonical subject's published owner contract and freeze that substituted catalogue. A completed concrete projection shall additionally identify its selected explicit or structural witness and the evidence needed to check it. Import shall preserve these recipes and completed selections.

A generic import requiring a witness that is unavailable, inaccessible, owned by another module without authority, or ambiguous under the standardized coherence rules is `ERROR`. Conformance declarations may not be added to an already compiled imported type by a consumer-side module. Type-only imports may name an incomplete family/constraint but cannot prove an operation requiring a complete selected associated layout. The module's generation and sealing stages may not retroactively modify a public conformance after the catalogue is frozen.

Public conformance catalogue contents, each entry's effective priority, kind signatures, and relevant associated type/value bindings shall enter the semantic interface identity. A selected standard export shall include them in its versioned interface fingerprint. Their storage is compile-time metadata; the selected runtime and native ABI contract determine emitted objects. The [advanced generic rules](26_advanced_generic_families.md#chapter-26-advanced-generic-families) and [standard selection algorithm](27_constraint_solver_and_inference.md#chapter-27-constraint-solver-inference) govern imported instances.

## 9. Configuration and linked boundaries

Configuration resolves in the hierarchy already specified for project, package, module, file, declaration, and operation scopes. A module's implementation units may have different permitted private operation defaults. Definitions of the same exported entity must nevertheless agree on the effective settings belonging to that entity's contract.

An interface records required exported layouts, calling conventions, exception ABI/profile, ownership effects, numerical behavior at exposed operations, and support providers. Link checking compares requirements relevant to the shared boundary. Unrelated private diagnostic and allocator settings shall remain local to each implementation.

Conversely, an importer cannot reinterpret a public record under its preferred packing, change a parameter's platform-width family, erase required lifetime effects, or treat a different exception ABI as compatible. A declared adapter performs such translation explicitly where supported. A conflicting direct binding is `ERROR`, not a configurable warning.

Imported functions retain their canonical phase-aware effect bounds and runtime value-contract policy from the owning module. An imported generic witness with an open effect descriptor does not satisfy a closed effect constraint merely because its function machine type matches. The [effect-boundary specification](25_effect_composition_and_boundaries.md#chapter-25-effect-composition-boundaries) defines substitution and adapter rules; a module link shall preserve borrow origins, admission effects, exception boundaries, and terminal behavior.

Inlining, instantiation, and whole-program/link-time optimization shall realize the definition-bound operation contract. Its ordinary execution may be Native or Checked/Strict; explicit interface functions and terminal boundaries shall retain their published behavior. Physical code placement is an implementation choice.

## 10. Compilation stages and artifact contracts

A conforming separate-compilation process shall establish the following information, whether or not implemented as distinct passes:

1. Resolve logical module/unit identities, declared inputs, target descriptors, and configurations.
2. Read module headers and import preambles; obtain the required nominal declaration indexes.
3. Check complete-interface dependencies and resolve interfaces in dependency order.
4. Bind authored declarations, resolve required static-reflection permissions, and complete applicable generation transactions in the prescribed deterministic order before sealing affected records and interfaces.
5. Bind specializations under their captured environments, including generator-dependent definitions and sealed metadata identities.
6. Compile implementation units and produce native code/data plus the semantic interface material selected by the separate-compilation request.
7. Resolve native definitions, configuration/ABI requirements, and the image's static initialization graph.

Independent units may compile concurrently. Overload resolution, versions, declaration identity, and static order shall derive from the bound inputs. A deterministic dependency traversal uses canonical logical identities for otherwise unordered work; its scheduling is not the runtime initializer schedule.

An interface artifact shall provide public declarations, required type/layout/effect contracts, definition-material availability, imported contract identities, provider requirements, and native-link requirements under its declared versioned protocol. Its source edition shall be explicit. A compiler-private representation may supply this material to compatible consumers. A selected public contract export shall additionally provide Chapter 29's applicable canonical records. A consumer shall select a supported representation or diagnose unavailable interface material.

Artifact incompatibility shall be detected before its contents are treated as valid declarations. Rebuilding from supplied source under the recorded contract is permitted. Rebuilding a dependency under the consumer's unrelated defaults is not. A source-less artifact may therefore be usable through its native ABI while unavailable for native generic instantiation by an incompatible frontend.

Compilation shall expose required link objects and support components without running the resulting program. Generic definitions and module-map inputs shall be resolved during compilation.

## 11. Caching and deterministic inputs

A cached result is valid only for the inputs that affect the requested result. A code-cache key shall account for compiler/backend identity, target and ABI options, semantic configuration, relevant source contents, imported interface/definition contracts, and selected providers. Native ABI identity and cache identity are different: an optimization setting may preserve ABI while requiring a different code artifact.

A private implementation change need not invalidate unrelated importers when public contracts and reachable definitions are unchanged. A changed generic body, constant-evaluation dependency, reflected metadata projection, generator implementation, emitted declaration set, exposed layout, effect, or semantic default invalidates consumers that relied on it. A metadata grant/revocation also invalidates artifacts relying on that authorization. Cache reuse shall validate every depended-on exposed definition and authorization.

Diagnostic settings remain excluded from ABI identity. A cached compilation shall retain or recompute the diagnostics needed to apply current suppression and promotion rules. A previously successful build cannot bypass a current promoted `ERROR` by replaying only its machine code.

Declared source and binding inputs shall be identified independently of directory discovery order. Cache keys shall use content identity. Physical paths may supply debug information; canonical module and static identities shall use their logical fields. Optional reproducible-object capabilities may impose stronger byte-level requirements; semantic determinism does not require different compilers to emit identical instruction sequences.

## 12. Native objects and foreign header adapters

Each compiled unit requiring code or data can emit ordinary native `.o`/`.obj` artifacts under the native interoperability specification. An interface-only unit with no emitted entities need not manufacture executable code. Partitioned native output shall retain an ordinary platform-linker path. The selected target, rather than the filename suffix, determines ELF, COFF, or another supported format.

Foreign integration may be declared directly with the existing `extern "C"`/`extern "C++"` and ABI attributes, or imported through a generated binding module. A header adapter consumes explicitly selected foreign headers, compiler dialect/options, include dependencies, target/CRT/library descriptors, and preprocessing inputs. Its output is a CPN26 declaration interface with preserved foreign nominal identities and ABI metadata, plus any required adapter objects.

The adapter's foreign preprocessing context does not become the consumer's CPN26 source context. A foreign macro is not automatically a CPN26 token macro. A binding provider may expose a selected macro as a typed constant or wrapper when its semantics and dependencies are declared. Unsupported definitions require a wrapper or an error rather than a guessed signature. Its CPN26 binding identifiers use native normalization, while original foreign symbol and nominal-type identities remain preserved separately. Two distinct foreign entities whose binding names collide require explicit distinct aliases or a diagnostic; normalization shall preserve distinct foreign identities through those aliases.

A requested CPN26 C interface export shall supply the header and native binding description selected under Chapter 09. The header describes actual exported transport types and symbols. A selected standard contract export shall encode its descriptor using Chapter 29. The interface shall preserve each CPN26 initialization owner and the declared transport for Result, ownership, and exception records.

The module interface's native-link requirements identify symbol providers and required support libraries. Native symbol resolution does not replace declaration, ownership, or exception-boundary validation. Linking a C++ adapter adds the selected support dependencies only when that adapter requires them; ordinary modules do not acquire a universal C++ runtime.

## 13. Initialization domains and readiness

All static definitions contributing to one image are assigned to that image's initialization domain, except where an explicit foreign-domain adapter declares a separate owner. A module and its partitions do not automatically create separate domains. Their static identities retain exactly the prescribed tuple of namespace, module identity, logical source path, declaration ordinal, and specialization identity.

A generated declaration or static object has its owning module identity, an emission-provenance identity, and the ordinary stable initialization and destruction contracts. A generator does not introduce an implicit initializer merely by executing during compilation. It cannot insert imports after the preamble or mutate previously compiled imported modules. An import does not itself add an initialization edge. Required module barriers are stated by `initialization_dependencies`; required object edges use `init_after` and the established static descriptors. Exported operations that require static state carry the corresponding readiness/effect contract. A caller during startup shall satisfy that prerequisite or receive the prescribed diagnostic/dynamic dependency failure. Importing a function declaration does not make its private static dependencies ready.

The effective initialization graph is validated independently of source import graphs. Cycles are `ERROR`. Official presets execute serially in logical rank order; custom parallel execution retains dependency checks, atomic commit/cancel resolution, separate failure records, and cooperative/finish contracts. Precommitted constant objects do not erase dynamic dependencies passing through them.

Shutdown shall visit committed objects in decreasing logical rank under the bound static graph. A merged generic/static definition is registered once. An independent image's startup bridge is invoked by exactly one owner, as required by the native interface contract.

Module execution shall use the core failure routes. Type import, deserialization, and declaration discovery shall operate on compile-time interface material; application initialization belongs to the runtime domain.

## 14. Shared images and unloading

Loading an image exposes declarations only after its identity and applicable native contracts have been checked. Availability of symbols is separate from readiness of its dynamic state. A host or declared loader provider shall complete the required startup contract before permitting operations that require the image's committed objects.

Direct code references, callbacks, vtables, RTTI, exception records, allocator contexts, or destruction obligations can require an image to remain loaded. A module import is a compile-time relation, not an automatic runtime reference-counting scheme. A selected loader/ownership provider may explicitly retain images; otherwise the caller shall enforce the declared lifetime obligations.

Unloading shall stop new admitted calls, account for in-flight activity, and discharge or transfer eligible owned obligations before invalidating code/data. Retirement shall follow declared acyclic readiness dependencies and the explicit object obligations. Known forbidden unloading is `ERROR` where statically established; an unproved permitted obligation retains the ordinary `ANOMALY` and explicit contract.

Two images sharing a public nominal type shall agree on that type's canonical identity and relevant ABI. Loaded copies of an implementation are not assumed to share one static object or one initialization domain. A provider requiring process-wide unique objects shall supply that ownership contract explicitly. Replacing a library does not automatically preserve existing object layouts, outstanding records, or old destruction callbacks.

## 15. Source examples

The following three units select `compilation.modules` and use one importable module and one non-importable application module. A build using precompiled CPN26 interface material additionally selects `compilation.separate`. The module map assigns their logical paths and selects the application's `main` entry under the native entry contract.

**`geometry.cpn` — primary interface**

```text
export module geometry;

export struct Point {
    i32 x;
    i32 y;
};

export declare i32 sum(const<Point>& value);
```

**`geometry_impl.cpn` — implementation**

```text
module geometry;

i32 sum(const<Point>& value) {
    return value.x + value.y;
}
```

**`application.cpn` — application implementation**

```text
module application;
import geometry;

i32 main() {
    geometry::Point point(3, 4);
    i32 result(geometry::sum(point));
    return result - 7;
}
```

The interface declaration and implementation definition denote the same `geometry::sum`. Importing geometry creates neither a second Point type nor another sum definition. The addition inside sum uses the configuration bound to its definition; the application cannot alter it merely by importing the module under a different arithmetic default.

## 16. Required diagnostics

The following conditions require `ERROR`: a requiring use of a disabled compilation or export capability; ambiguous module resolution; duplicate primary interfaces or partition identities; forbidden external partition imports; complete-interface cycles; a completeness requirement unsatisfied by type import; conflicting canonical declarations/definitions; unavailable generic definition material; incompatible direct ABI contracts; and effective static initialization cycles.

A cache miss shall rebuild the same bound semantics. Source acceptance shall follow the language requirements independently of optional optimization opportunities. Diagnostic emission follows Chapter 08.

