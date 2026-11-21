<a id="chapter-23-compile-time-generation"></a>

# CXXN Compile-Time Metaprogramming and Declaration Generation Specification

## 1. Purpose and separation of concerns

Declaration generation shall evaluate typed syntax in the compile-time phase and commit validated declarations into an authorized lexical scope. Each emitted declaration shall undergo the grammar, binding, type, access, effect, lifecycle, configuration, and ABI checks applicable to an authored declaration at that insertion point. The [core execution model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance) governs its subsequent runtime behavior.

This chapter owns generation staging, transactions, hygiene, and the permission matrix shared with [static reflection](22_static_reflection.md#chapter-22-static-reflection). Chapter 08 owns capability/default/budget selection.

## 2. Generation blocks and enabled scopes

Chapter 15 owns the generation and quotation grammar. A generation declaration shall use `generate { ... }`, with explicit `emit(expression);` submissions.

A generation body shall admit if, if constexpr, for, while, do, nested compounds, local declarations, and expressions eligible for required evaluation. Break and continue shall target a loop in that body. Each helper invocation shall satisfy the same required-evaluation environment and may return its admitted compile-time value. The admitted statement set shall retain transaction completion in the containing generation body.

A generate declaration shall occupy the file scope of a Core root unit or selected named-module unit, namespace scope, or the body of a directly owned struct or class. Its emitted declarations shall belong to that exact lexical scope. The owning compilation scope shall be the Core root owner or named module established by Chapter 11. Every submitted declaration shall satisfy the scope and ownership validation in Section 7.

Emit shall occur inside a generate body and accept one std::meta::Declaration or immutable ordered Declarations sequence. It shall evaluate the argument once and append the candidates to that body's pending transaction. Publication shall occur through Section 7's atomic commit.

A consteval helper shall return candidate declarations to its caller. The enclosing generate body shall own the transaction and explicitly submit those values with emit.

## 3. Generation values and syntax quotations

The compile-time `std::meta` generation facility supplies:

| Type or operation | Contract |
| --- | --- |
| `std::meta::Name` | A compiler-validated identifier, not a raw source fragment. |
| `std::meta::Declaration` | One parsed, typed declaration-syntax candidate. |
| `std::meta::Declarations` | An immutable ordered sequence of declaration candidates. |
| `std::meta::SyntaxExpr` | A parsed expression-syntax candidate, not an evaluated runtime value. |
| `std::meta::identifier(text)` | Construct a target-scope declaration identifier from an NFC-valid source identifier spelling. |
| `std::meta::data_member(name, type_info, access)` | Construct one ordinary stored field declaration for a record target. |
| `std::meta::static_member(name, type_info, initializer, access)` | Construct one static member declaration with an explicit initialization contract. |
| `std::meta::declarations(elements...)` | Construct an ordered sequence from declaration candidates. |

These types shall belong to the compile-time phase. A versioned provider may add typed constructors for further declaration kinds by publishing their complete syntax-tree and semantic contracts. Every requested constructor shall have its required capability.

A quotation shall use Chapter 15's `quote declaration { ... }` or `quote expression { ... }` form and produce typed syntax parsed at its definition site. It shall contain the selected declaration or expression category. Its splices shall have the following inputs:

| Splice form | Required compile-time input and position |
| --- | --- |
| `splice_type(expression)` | A reflected type at a type position. |
| `splice_name(expression)` | A validated Name at an admitted identifier position. |
| `splice_expr(expression)` | Correctly typed expression or constant syntax at an expression position. |

The checker shall validate each splice before emission and preserve its grammatical category.

Quotation identifiers shall carry Section 8's definition-bound, quotation-local, or target-introduced provenance. A committed declaration head shall enter the target scope. `std::meta::fresh_name()` shall produce a helper identity stable for the same canonical inputs and emission ordinal; its physical spelling may remain private.

Example, with the generation capability enabled and the standard meta module imported:

```cxxn
export module geometry;
import std.meta;

generate {
    emit(quote declaration {
        i32 doubled(i32 value) { return value + value; }
    });
}

struct Header {
    u32 length(0);
    generate {
        emit(std::meta::data_member(
            std::meta::identifier("checksum"),
            reflect_type<u32>,
            std::meta::Access::Private));
    }
};
```

With meta.generate, meta.generate_layout, and the required std.meta provider enabled, doubled shall become an owning-module function and checksum an ordinary field in Header's generated-member segment. Their subsequent execution, arithmetic, initialization, layout, and access shall use the selected ordinary contracts.

## 4. Generated declarations and lexical lookup

Section 6 shall establish the authored skeleton and generated transaction sequence. The skeleton shall retain every authored field's declaration order, allowing authorized skeleton queries throughout the record independently of the generation block's physical position.

Authored stored fields shall retain their order. Generated fields shall follow them in successful-transaction order; methods, aliases, and statics shall preserve that layout order and the base order. A generated constructor or destructor shall enter before sealing and satisfy the ordinary overload, special-operation, and responsibility rules. Existing declarations shall retain their identities and collision rules.

File-scope and namespace emissions shall enter at the generation declaration's logical source position. Earlier nondependent bindings shall retain their candidate sets. Normal declaration-before-use and forward declarations shall remain available. A sealed record shall expose its complete final member index under Chapter 10's binding rule.

A generated declaration shall use its target's owning compilation identity and generation-site configuration. Its generator function shall execute under its own captured definition contract; the returned declaration shall be checked under the target's source, ABI, and lifetime contract while preserving hygienic external bindings. The target configuration shall remain fixed throughout the transaction.

## 5. Derivation attributes

A record may explicitly request generation from a named function through the standard `derive` attribute:

```cxxn
[[derive(geometry::generators::emit_comparisons)]]
struct Coordinate {
    i32 x(0);
    i32 y(0);
};
```

A derive argument shall resolve to one reachable exported consteval function or fully applied specialization with the exact conceptual signature `std::meta::Declarations Generator(std::meta::Info target)`. Section 6 shall schedule that invocation after specialization and skeleton binding, and commit its returned declarations in sequence order.

A derivation transaction shall be identified by selected target specialization, selected generator, zero-based ordinal among that definition's derive attributes, and captured definition environment. Generic attribute references shall be checked at definition; derivation shall execute for each selected concrete specialization. Equivalent separate compilations shall reproduce the same canonical declarations and transaction identity.

A derivation may add functions, nonstorage aliases, constraints, and static declarations under their ordinary contracts. Representation-changing declarations shall require an in-record generate block and meta.generate_layout. Existing user lifecycle declarations shall retain their identities; additional lifecycle declarations shall satisfy ordinary overload rules.

Each derivation shall receive the access-filtered metadata and submitted-member authority established by Section 5.1. Emitted references shall retain their hygiene provenance, and signatures shall satisfy the target's ordinary visibility and ABI contracts.

Derivations shall execute in source attribute order. Repeating a canonical generator on one record shall require its published repeatable contract. Dependency cycles shall fail the required-evaluation check in Section 6.

### 5.1 Owner-authorized member access

The following table is the canonical authorization contract for reflection and derivation grants:

| Owner-authored attribute on record R | Canonical subject | Granted operation |
| --- | --- | --- |
| `meta_grant(M)` | Current owning module or reachable imported module M | Inspect R's otherwise available nonpublic metadata in M's query environment. |
| `derive_access(G)` | One generator selected under derive's signature rule | Form and execute ordinary R-member accesses in member definitions submitted by G's matching derive transactions on R. |

R's owning compilation scope shall author each grant on R's definition and identify that author through its canonical owner identity. Each attribute's subject shall resolve under its schema in the table; meta_grant(M) shall retain its named-module subject. All attribute references shall be resolved before derivation begins, so textual placement of a grant among attributes preserves the same authority. Duplicate grants to the same canonical subject shall be rejected. A valid unused grant shall remain compile-time authority.

Each grant shall apply to R's own declarations under ordinary member-access rules. Private declarations of bases and unrelated records require their separate authority. Inspection authority belongs to the named module; helper calls into another module shall use that helper's authority. Submitted-member authority belongs to the matching target/generator transaction, including its repeatable derive ordinals. Ordinary generator calls, other targets, and unrelated generate blocks shall use their ordinary lexical authority.

A generic definition shall capture its grants for the selected instances derived from that definition. Separately authored specializations, derived records, and nested records shall establish their own grants. The compiler shall reject generated attempts to author, modify, or re-export a grant.

A generator requiring private metadata and private-member references shall supply both applicable authorities, whether from the table or independently valid lexical access. Syntax and Info values carry identity/provenance; the validating transaction supplies authority. Member access shall preserve qualification, overload, active-case, generation, construction state, ownership, and effect requirements.

Submitted members shall retain their declared access. An authorized public member may return a permitted value computed from R's private field. Its signature and exported metadata shall independently satisfy ordinary public visibility. Authorized definition material may include private identities needed to check its body; public reflection shall still use its own access filter.

The semantic interface shall record target identity, subject owner or generator/definition identity, grant kind, and applicable derive ordinals. Validation shall establish the exact matching grant before accepting a private reference. Grant or generator-contract changes shall invalidate dependent generated definitions. Chapter 21 shall govern internal identity and selected external publication of these records.

```cxxn
import schema.generators;

[[meta_grant(schema.generators)]]
[[derive(schema::generators::emit_read_id)]]
[[derive_access(schema::generators::emit_read_id)]]
class Entry {
    i32 internal_id(0);
};
```

Here meta_grant admits field inspection and derive_access admits the submitted member body's field access. Removing either authority leaves that corresponding operation subject to ordinary access checking. Every generated access shall satisfy the field's runtime lifetime requirement.

### 5.2 Conformance catalogue publication

Ordinary aliases, generic declarations, and constraints may be emitted through admitted typed-syntax constructors. A public `satisfy` conformance shall originate in an authored declaration of its owning compilation scope and satisfy Chapter 26's ownership rules. The generation validator shall reject a submitted conformance declaration.

An authored conformance may use generated methods after their required declaration and completion checks succeed. A committed generated alias, constant, constructor family, or ordinary method may supply structural evidence under Chapter 26. Structural witness formation shall use the sealed subject and completed bound catalogue required by Chapter 27. Witness publication shall record the selected evidence and its canonical identities after these dependencies complete.

## 6. Staging, sealing, and determinism

The semantic stages for an owning compilation scope and a record are:

1. Resolve the Core root or named-module identity, any selected imports, configuration, canonical authored declarations, and their access permissions.
2. Build authored record skeletons and dependency edges without demanding complete generated layouts.
3. Process derive attributes in deterministic declaration order. For each attribute, evaluate its function, validate its pending batch, and commit that batch atomically before beginning the next derivation; a failed transaction commits nothing.
4. Process explicit generation bodies in the owning record's source order with the same evaluate, validate, and atomic-commit protocol. Each body sees prior committed derivations and generation batches, never its own pending output.
5. Seal the record/member index and resolve layout-dependent queries, special operations, overload sets, and generic constraints that depend on the final declaration set.
6. Establish exported interface metadata, canonical instantiation identity, native ABI declarations, and static initialization descriptors.

File-scope and namespace generation shall follow source order after their required source binding and any selected import resolution. A generated nested record shall enter the same staged sequence under a well-founded dependency. The owning source identity, tokenization profile, and any resolved imports shall remain fixed during generation.

The query-stage table is authoritative for both reflection and generation:

| Observed entity/stage | Available information |
| --- | --- |
| Incomplete nominal identity | Declared identity and reachable declaration properties. |
| Current authored record skeleton | Accessible authored declarations; authored_fields returns their field subset. |
| Active owning derivation/generation | Authored skeleton plus earlier committed batches through staged_fields; is_complete is false. |
| Current pending batch | Transaction-local syntax under validation; reflected publication begins at commit. |
| Sealed complete record | Final direct_fields, layout, completed overload/trait information, and is_complete true. |
| Unrelated sealed record during generation | Its ordinary complete query surface under the query's access rights. |

The active owning-generation context includes its selected derive function and permitted synchronous constant-evaluation helpers. It supplies stage information; Section 5.1 supplies access authority. A query requiring a later stage shall fail with the required dependency diagnostic. Each derivation shall execute once in its defined semantic order and observe that snapshot; later generation shall preserve earlier completed transactions.

The validator shall check grammar, identity, access provenance, and independently resolvable signatures before batch commit. Completion-dependent body binding, defaulted operations, and layout checks may remain pending until sealing. Their results become available at that completion stage. A sealing failure shall invalidate the enclosing record; publication requires all completion checks to succeed.

The compiler shall detect active dependency cycles across queries, generation, instantiation, and required evaluation. A cycle shall produce a required-evaluation error. Parallel evaluation shall produce the declarations and commit order prescribed by the serial semantics.

## 7. Emission validation and atomic commit

Before a batch is committed, the compiler validates all emitted nodes as though they were written at their logical insertion points, preserving the ordinary completion-dependent checks identified in Section 6. This includes the requirements that are decidable at that declaration phase:

- grammar and identifier validity, source normalization, reserved names, and case-sensitive collisions;
- supported declaration kind and allowed target scope;
- permitted effect attributes and ownership annotations;
- complete type and applicable generic requirements;
- legal initialization, constructor/delegation, destructor/Cleanup and virtual-base responsibility behavior;
- ordinary overload uniqueness, external symbol identity, linkage conventions, and public interface consistency;
- format/width capability availability, numeric-policy binding, and target ABI legality;
- accessibility and hygiene provenance, including attempted nonpublic disclosure;
- static-object declaration identity, explicit initialization dependencies, and deterministic source order.

A transaction shall publish its entire validated batch or publish nothing. Earlier independent committed batches retain their semantic results subject to ordinary whole-unit publication. Generation failure shall remain a compilation failure under the selected declaration contract.

`emit` shall submit compile-time syntax to its active transaction. The evaluator shall count declarations at successful batch validation. Exceeding a generation budget shall fail the current transaction with its compilation-resource diagnostic.

## 8. Hygiene, capture, and private-member contracts

Every syntax identifier shall carry exactly one provenance category. A definition-bound name shall resolve in its captured generator environment. A quotation-local name shall bind inside the generated syntax scope. A target-introduced name shall use its validated Name in the target scope and satisfy ordinary collision checks. Each binding shall retain its selected declaration and policy context.

A generator using a target-site name shall receive an explicit reflected declaration or validated Name with the corresponding binding authority. splice_expr shall preserve already bound declarations and effects. Generated lifecycle operations shall satisfy Chapter 06, and their runtime validation shall follow the target operation's selected policy.

The validator shall establish Section 5.1's authority independently of hygiene provenance. A definition-bound reference shall keep its actual selected declaration. An owner-authored generate block has its ordinary lexical access; external helpers execute under their own access environment. A lower-level syntax provider shall publish its mapping to the three provenance categories.

## 9. Cross-module generation and exports

A generated declaration shall belong to its target module and use that scope's explicit export context. Export validation shall establish public signature visibility, eligible interface-unit placement, and unique nominal identity.

An exported generator shall publish its versioned definition, query capabilities, required reflection material, and syntax-builder dependencies. A consumer may invoke it at an eligible scope owned by that consumer; compiled dependency declarations shall retain their original owner and generation transactions.

A generated field shall enter the owning type's ABI contract. Generated functions, constraints, and attributes shall enter their corresponding semantic interface identities. A selected standard contract export shall project these identities through Chapter 29. Dependency invalidation shall follow every exposed or transitively required definition change, while unrelated private helpers shall retain their independent identity.

An imported generic containing generation shall retain its defining module's policies, generator versions, target scope, and canonical specialization arguments. Grants shall remain those captured under Section 5.1. Repeated imports shall share the resulting canonical symbol and static-object identities under the ordinary instantiation rules.

## 10. Static objects, native code, and C/C++ interoperation

A generated static shall participate in the ordinary initialization, cancellation, commitment, and destruction graph. Its stable identity shall include the owning Core root or named module, generator invocation, target scope, and ordered emission ordinal. Generated native symbols and foreign bindings shall satisfy their selected function, ABI, and adapter contracts.

Runtime output shall contain emitted program entities and explicitly requested runtime descriptors. Compile-time syntax and reflection material remain in their defined phase under Chapter 21.

## 11. Compile-time effects and resource governance

Generation shall execute admitted required-constant operations and declaration transactions. Compiler-local workspace shall use the declared compilation budgets. Its input set shall consist of declared source/module/provider material and any explicitly supplied content-addressed extension inputs. The evaluator shall derive output solely from that set and the bound semantic configuration.

Chapter 08 defines generation capability keys, defaults, and limits. Reflection-dependent operations shall require meta.reflection; a provider may declare quotation-only generation with reflection disabled. Representation-changing emission shall require meta.generate_layout.

Required-evaluation budget exhaustion and dependency cycles shall fail the transaction. Query-specific try operations may return their defined property-inapplicability Results. These outcomes shall retain their distinct meanings in generic candidate selection.

## 12. Error classes, attribution, and reproducibility

A generated diagnostic shall identify the logical declaration, emission site, and originating generator or quotation. Its source mapping shall preserve those validated identities. Diagnostic presentation shall use the consumer's access rights when rendering private source content.

A conforming implementation shall distinguish at least:

| Diagnostic class | Required meaning |
| --- | --- |
| `META001` | Reflection or generation capability disabled/unavailable. |
| `META002` | Metadata access forbidden by visibility/grant contract. |
| `META003` | Property requires a sealed/complete type or interface. |
| `META004` | Quotation, splice, or emitted declaration has invalid kind or type. |
| `META005` | Duplicate name, incompatible overload, or conflicting emitted entity. |
| `META006` | Generated declaration would change a forbidden owner, scope, ABI, or lifecycle contract. |
| `META007` | Reflection/generation dependency cycle. |
| `META008` | Required evaluation resource budget exhausted. |
| `META009` | Nondeterministic or undeclared external input requested. |
| `META010` | Invalid metadata identity, value/category, or hygiene provenance. |

Required generation failure shall use the central ERROR disposition. Optional analysis of an admitted metadata obligation shall use its configured diagnostic. These dispositions shall preserve the distinction between valid emitted syntax and failed required generation.

For equal canonical source, logical owner environment, target ABI, admitted inputs, generator definitions, and effective semantic configuration, implementations shall produce equal emitted declarations and logical order. The logical environment shall be the Core root or selected module map. Machine instruction selection and physical encoding shall follow the chosen implementation and target contract.

## 13. Normative boundary cases

| Case | Required result |
| --- | --- |
| `generate` at file scope in a Core root or named-module unit, or in an owned namespace | May add ordinary eligible declarations to that exact lexical scope. |
| `generate` inside a runtime function | ERROR: the declaration requires an admitted compile-time scope. |
| `emit` called from a normal `consteval` helper, with no enclosing generation block | `ERROR`; the helper may instead return a declaration value. |
| A failed batch emits two declarations, one invalid | Neither declaration from that batch is committed. |
| A field is emitted in a record with `meta.generate_layout = false` | `ERROR` even when `meta.generate = true`. |
| A `derive` function tries to add a stored instance field | `ERROR`; `derive` is nonstorage. |
| A generated function attempts private member access without access permission | `ERROR` despite its resulting class membership. |
| A foreign generator inspects a private field with meta_grant but has no applicable derive_access | Inspection may succeed; a submitted member body gains no private access from that fact. |
| An applicable owner-authored derive_access permits a submitted member body to read the target's private field | Ordinary member access is admitted, subject to qualification, lifetime, effects, and valid public signature rules. |
| A generator tries to emit meta_grant or derive_access | ERROR: these attributes require an authored owner grant. |
| A derive function queries authored_fields for its current unsealed target | Accessible authored fields, independent of the attribute's position in the record definition. |
| A later explicit generate block adds a field after derive completed | The field is appended by its transaction; the completed derive retains its committed output. |
| An emitted member body fails when the final owner index is sealed | The enclosing record fails completion and publication. |
| Generator uses `splice_type` in expression/name position | `ERROR`; splice categories are distinct. |
| A generated name duplicates an existing incompatible authored name | ERROR under ordinary collision validation. |
| Generator queries final layout of its own unsealed record | Dependency `ERROR`, not speculative layout. |
| Two generations commit independent methods under different worker scheduling | Same canonical identities and logical order. |
| Generator imports an undeclared new module | `ERROR`; module imports are frozen before generation. |
| Generation emits a C++ class with no verified target ABI | No direct C++ class ABI claim; explicit wrapper or provider contract required. |
| A generator returns a private metadata handle as a runtime value | `ERROR`; no representation or privilege escape. |
| A generated static object is initialized | Applies normal static logical ordering and destruction responsibility. |
| Generation is disabled while ordinary `consteval` is enabled | `consteval` remains available; emit/generation forms are unavailable. |

## 14. Standard library and conformance boundary

An implementation shall report Reflection, Declaration Generation, and Layout Generation as separate capabilities. Their claims shall respectively cover Chapter 22's query surface; this chapter's typed syntax, transactions, hygiene, and ordering; and generated layout with its ordinary lifecycle validation. The declared std.meta provider shall publish the supported surface. Explicit runtime descriptor materialization shall use std.meta.runtime and its ordinary object/resource contract.

