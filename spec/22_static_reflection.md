<a id="chapter-22-static-reflection"></a>

# CXXN Static Reflection Specification

## 1. Scope and normative model

Static reflection shall evaluate compiler-established descriptions of declarations, types, expressions, and admitted foreign entities. `std::meta::Info` is a compile-time value: it supports copying, canonical-identity comparison, consteval parameters/results, and compile-time temporary collections. Runtime materialization shall use the explicit descriptor operation in Section 12.

Reflection shall apply ordinary binding, access, completeness, and definition-site policy rules. Its query results describe semantic entities; runtime object access shall use the resulting ordinary operation's own lifetime and ownership contract. Reflection and declaration generation are independently selected capabilities under [Chapter 08](08_runtime_configuration.md#chapter-08-runtime-configuration). Their execution phase follows the [core model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance).

## 2. Intrinsic reflection syntax

The [core grammar](15_grammar_binding.md#chapter-15-grammar-binding) defines three nonoverloadable intrinsic forms: `reflect_type<T>`, `reflect_decl(name[, function_type])`, and `reflect_expr(expression)`.

`reflect_type<T>` describes type `T`; the type need not be complete for its nominal identity to be reflected. `reflect_decl(name)` describes the declaration denoted by its qualified-id in the current binding and accessibility environment. If a callable name denotes multiple overloads, the second argument is a function type that selects one exact declaration by its canonical parameter, return, receiver, and effect contract. The selector shall identify exactly one declaration; failure is ERROR.

`reflect_expr(e)` shall type-check e in an unevaluated context and return its static type, value category, unambiguous selected declaration, and declared effects. The expression shall satisfy its capability and accessibility requirements. Query evaluation contributes compile-time metadata events only.

Each intrinsic shall return Info under the surrounding definition-site configuration. A use within a runtime function shall consume the handle entirely during constant evaluation. For example:

```cxxn
consteval usize count_members() {
    auto t(reflect_type<MyRecord>);
    return std::meta::direct_field_count(t);
}

constexpr usize member_count(count_members());
```

This example requires a complete, sealed `MyRecord` when `direct_field_count` is invoked. If it is incomplete at that point, the evaluator reports the corresponding required-constant error rather than returning an arbitrary count.

## 3. Metadata identity, kinds, and equality

An Info shall describe one semantic entity or expression descriptor. Standard `std::meta::Kind` cases are `Type`, `Variable`, `Function`, `Constructor`, `Destructor`, `Field`, `Base`, `Enumerator`, `UnionCase`, `Alias`, `Namespace`, `Module`, `GenericFamily`, `GenericParameter`, and `Expression`. A versioned provider may expose additional declared kinds. An inapplicable query shall produce its named compile-time MetaError Result or its terminating-query diagnostic.

Declaration identity shall use the owning module/package, declaration, selected specialization, and relevant representation contract. `reflect_type<Alias>` shall identify the underlying type; `reflect_decl(Alias)` shall identify the alias declaration. `underlying_type` obtains the aliased type from its declaration handle.

`same_entity(a,b)` shall compare canonical entity identities. Expression handles shall compare their bound semantic expression identity in the compilation context. Opaque handles support equality; `stable_key(info)` supplies the provider's deterministic logical grouping key. The key's portability and encoding are properties of its published provider version.

Canonical identities and member order shall derive from declared logical inputs. Physical paths, worker order, compiler addresses, and internal allocations are implementation data outside those identities.

## 4. Standard query surface

The standard `std::meta` module provides the following semantic operations. Names in this table are ordinary library-level entry points backed by the static-reflection provider. Their inputs and outputs are compile-time-only unless an output is an ordinary permitted constant scalar or string literal value.

| Query | Required semantics |
| --- | --- |
| `kind(info)` | Return the entity kind. |
| `same_entity(a,b)` | Compare canonical semantic identities. |
| `name(info)` | Return the source-level declared name, if present and accessible. |
| `qualified_name(info)` | Return the canonical CXXN qualified name when the entity has one. |
| `owner(info)` | Return the declaring scope/module entity. |
| `type_of(info)` | Return the reflected type of a field, variable, function result where applicable, or expression. |
| `value_category(info)` | Return the static value category for an expression reflection only. |
| `is_complete(info)` | Return whether the described type is sealed and complete at this query point. |
| `is_const(info)` | Return the declared applicable top-level const qualification. |
| `is_public(info)` | Return whether the declaration is publicly accessible from the query environment. |
| `direct_fields(type_info)` | Return direct fields of a sealed type, excluding inherited fields, filtered for access. |
| `direct_field_count(type_info)` | Return the number of entries that direct_fields would expose, as usize; the same sealing and access requirements apply. An unrepresentable count is a required-constant error. |
| `authored_fields(type_info)` | Return the accessible original source-declared fields of a record, including in an unsealed generation owner. |
| `staged_fields(type_info)` | During its owning generation, return accessible authored fields followed by fields of prior committed generation batches; never return the pending batch. |
| `direct_bases(type_info)` | Return direct base descriptions, including their virtual/nonvirtual attributes. |
| `methods(type_info)` | Return accessible declared member functions with their canonical signatures. |
| `enumerators(enum_info)` | Return the declared enumerators and their exact typed values. |
| `union_cases(union_info)` | Return the declared tagged-union cases and payload declarations. |
| `parameters(function_info)` | Return ordered parameter descriptions. |
| `result_type(function_info)` | Return the declared function result type. |
| `effects(function_info)` | Return declared exception, async, ownership, borrowing, and lifetime-effect contracts. |
| `attributes(info)` | Return only registered, reflectable attributes permitted by this query context. |
| `type_size(type_info)` / `type_alignment(type_info)` | Query the complete type's target size and alignment. |
| `field_layout(field_info)` | Return an optional representable byte/bit-offset description under the target ABI provider. |

Query collections shall be immutable compile-time sequences. Direct collections contain the owner's direct declarations in declaration order, followed by generated declarations in commit order. An inherited-member traversal requires its separate path-identity contract, including virtual-base uniqueness. Query readiness shall follow the single staging table in [Chapter 23](23_compile_time_generation.md#chapter-23-compile-time-generation).

Collection filtering shall use the query environment's access authority. Its length, positions, and returned identities shall describe exactly the accessible declarations.

## 5. Access control and privacy

Each query shall apply lexical visibility, module exports, private/protected access, and the owner-issued grant matrix in [Chapter 23, Section 5.1](23_compile_time_generation.md#51-owner-authorized-member-access). A public caller receives public metadata; a matching meta_grant admits that record's authorized metadata to the named module.

```cxxn
[[meta_grant(geometry.generators)]]
struct Point {
private:
    i32 internal_id(0);
};
```

The provider shall supply authorized private metadata through access-filtered interface material, including a separately sealed sidecar where applicable. Public serialization or re-export of that metadata shall require its own ordinary visibility authorization. A generated public accessor shall satisfy the distinct derive_access and signature rules in Chapter 23.

A required query with insufficient authority shall produce an access ERROR. A valid filtered enumeration may be empty; denied inspection is a failed query. The compiler shall retain that distinction during generic checking.

## 6. Completeness, layout, and class state

A forward declaration or type-only import shall provide its declared identity. Field traversal, size, completed traits, and layout-dependent observations shall require the corresponding completion stage and reachable interface contract. The query-stage table in Chapter 23 governs authored skeletons, active generation, and sealing.

For a sealed complete type, type_size and type_alignment shall use the same target profile as sizeof and alignof. field_layout shall return an offset only when the ABI establishes a stable representable offset. A dynamically adjusted subobject may instead use an explicitly admitted member-access operation.

Lifecycle metadata may describe Manual, Complete, virtual-base ownership, destructor/Cleanup effects, and selected special-operation contracts. It describes the declared protocol. A runtime access or transfer shall execute under Chapter 06's object-state and responsibility rules.

## 7. Reflection of expressions and operations

An operation-availability query shall check the declared generic domain and return its query-specific property result. `std::meta::try_*` distinguishes property inapplicability from malformed source, inaccessible declarations, and failed required evaluation under the standard query error contract. Generic candidate selection shall use Chapter 27's decision procedure.

`addressable_member(info)` shall describe whether an ordinary member-reference operation can designate the selected field. `get(object, field_info)` shall require a compile-time-known field handle and perform ordinary member access once, preserving qualification, category, borrow origin, access authority, and generation validity. Its runtime validation policy is the selected memory/lifecycle policy; the reflected handle supplies the member identity.

## 8. Generic interaction and specialization identity

A generic definition shall justify reflection queries through its declared constraints and reachable metadata. A public consteval function may accept Info and shall publish the metadata needed by its callers. Ordinary generic value arguments retain their admitted kinds from the type specification.

Reflection of a specialization shall return the already selected specialization identity and accessible members. An unapplied family's reflected surface shall contain its declaration, parameters, and constraints. An advanced-generic reflection capability may additionally expose Chapter 26's recursive kind tree, fixed and repeated parameter descriptors, captured partial arguments, and constructor mapping identity. A named constructor alias shall retain its declaration handle and its bound constructor identity as the corresponding query contracts specify.

An associated projection shall retain its full constraint application and selected explicit or structural witness identity. Structural evidence shall use the completed member and catalogue environment required by Chapters 26 and 27. Reflection shall observe that established selection at its admitted stage; the generation staging model determines when the relevant evidence is complete.

## 9. Constants, type information, and evaluation stages

Reflection shall execute under the target constant-evaluation rules in Chapter 10 and the query budgets in Chapter 08. Ordinary constant scalar or literal-string results may be materialized through their normal value contracts. Runtime owned text shall be constructed through its selected text/resource interface. Compiler metadata shall remain in its compile-time phase unless the program explicitly selects Section 12's runtime descriptor operation.

## 10. Representation queries and ABI promises

A foreign reflection provider shall expose the nominal, layout, and callable properties established by its selected ABI contract. An opaque foreign binding supplies only its admitted identity and operations. Generated foreign declarations shall satisfy the same verified ABI or explicit adapter requirements as authored declarations.

## 11. Reflection availability and configuration

Chapter 08 defines reflection capability keys, defaults, and evaluation budgets. The selected provider shall publish supported entity kinds, properties, layout capabilities, and metadata format revision. A required unavailable query shall fail at its use. Required-evaluation resource exhaustion shall retain its distinct compilation-resource outcome.

A compiled generic shall retain its definition-bound reflection requirements. Consumers shall supply those required providers and metadata or a declared compatible bridge.

## 12. Runtime descriptors are explicit

The separately selected `std.meta.runtime` operation shall materialize a descriptor from a sealed type and an explicit visibility/representation selection. The result shall be an ordinary immutable object or caller-owned serialized asset with a declared storage, version, access filter, image owner, allocator if needed, and unloading contract.

Exported descriptor content shall respect the materialization site's permitted export authority. Foreign descriptors shall describe operations under the corresponding foreign provider contract. Runtime invocation shall retain ordinary ABI, object lifetime, ownership, and failure requirements.

## 13. Diagnostics and conformance boundary cases

A conforming implementation shall distinguish unavailable capability, inaccessible property, incomplete type, property inapplicability, dependency cycle, and evaluation-budget exhaustion. Required query failures shall use the central diagnostic disposition and a stable logical location.

| Case | Required result |
| --- | --- |
| Reflect a complete public record type | A valid compile-time type handle. |
| Reflect a forward-declared type | Valid identity; size and fields unavailable until complete. |
| Query `authored_fields` from a generator inside an unsealed record | Accessible authored field skeleton only, with stable source order. |
| Query `direct_fields` for that unsealed record | Incomplete/sealing `ERROR`; no speculative final field set. |
| Reflect a type alias | Underlying type identity; alias declaration separately reflectable. |
| Query direct fields outside a class with private fields | Only members reachable under current access rights. |
| Directly reflect an inaccessible private member from another module with no grant | Access `ERROR`; an authorized public-member enumeration remains visibility-filtered. |
| Inspect private authored fields under a valid owner-authored `meta_grant` | Metadata inspection is admitted; no runtime member-access permission follows. |
| Generate a private-member access using only `meta_grant` | Access ERROR unless independent ordinary access or the applicable `derive_access` supplies authority. |
| Use `derive_access` without permission to inspect the requested private metadata | The metadata query still fails with access ERROR. |
| Query `is_complete` for the currently executing derive target | False; the specialization has its unsealed identity. |
| Query `direct_fields` or final size of that derive target | Premature-observation ERROR under the required query stage. |
| Query an imported type-only declaration's layout | Completeness `ERROR`. |
| Inspect `reflect_expr(++x)` | No increment and no numeric status event; expression must still be well typed. |
| Query a virtual base's fixed offset where no fixed offset exists | NotRepresentable Result/error. |
| Reflect a closed tagged union | Case/payload declarations only; no runtime active-tag read. |
| Pass an Info handle to `extern "C"` | `ERROR`: compile-time-only type has no ABI transport. |
| Store an Info handle in a runtime object | `ERROR` independent of object size. |
| Reflect a generated declaration from its own incomplete generation | Generation-cycle or premature observation `ERROR`. |
| Use a foreign type with no layout descriptor | Opaque reflection only. |
| Request an unavailable provider in an enabled query | Capability `ERROR`, not guessed metadata. |

A Reflection capability claim shall cover the enabled query surface and its access, identity, staging, and error contracts.

