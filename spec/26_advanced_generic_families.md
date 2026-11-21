<a id="chapter-26-advanced-generic-families"></a>

# CXXN Higher-Order Generic Families and Associated Types Specification

## 1. Scope and invariant requirements

This chapter defines recursive type-constructor kinds, constructor expressions and partial application, associated entities, structural witnesses, and explicit public conformance declarations. The [ordinary generic rules](10_types_functions_generics.md#chapter-10-types-functions-generics) own ordinary type identity and instantiation; [Chapter 27](27_constraint_solver_and_inference.md#chapter-27-constraint-solver-inference) owns deduction, proof, candidate selection, and coherence checking.

A *type constructor* SHALL map an admitted finite argument sequence to an ordinary type. Its argument kinds may themselves describe type constructors, and its final parameter may accept a finite pack. A *conformance witness* shall identify a constraint application and the associated entities and operation contracts selected for its subject type. Both are compile-time entities. Their use shall preserve the selected ordinary type's numeric, lifecycle, ownership, and effect contracts. Runtime representation and explicit erased adapters follow [Chapter 21](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance).

## 2. Recursive kinds and constructor expressions

A kind SHALL be a finite structural tree. The admitted descriptors are `type`, `const Type`, and `typefn<kind-list>`. A constructor descriptor SHALL contain its argument-kind sequence and the ordinary-type result kind. A kind-list may be empty and may end in one repeated descriptor. A repeated descriptor SHALL accept a finite ordered sequence of arguments of that kind, including an empty sequence.

| Parameter or descriptor | Argument domain |
| --- | --- |
| `type T` | One canonical ordinary type. |
| `const Type N` | One admitted required constant of the declared type. |
| `typefn F<type>` | One constructor accepting one ordinary type. |
| `typefn H<typefn<type>, type>` | One constructor accepting a unary constructor and an ordinary type. |
| `typefn F<type...>` | One constructor with a final pack of ordinary types. |
| `typefn F<type, typefn<type>...>` | One constructor with a type argument followed by a pack of unary constructors. |
| `typefn... Fs<type>` | A generic parameter pack whose elements are unary constructors. |
| `typefn F<>` | One nullary constructor. Applying `F<>` yields its ordinary type. |

The checker SHALL recursively compare kinds by descriptor, canonical constant-parameter type, fixed-position order, and final-pack structure. Bound names SHALL be alpha-equivalent. The kind grammar SHALL admit every finite nesting depth for higher-order kinds. The configured normalization and arity resources SHALL bound checking work and report exhaustion under Chapter 27.

```cxxn
generic<typefn F<type>, type T>
requires (ObjectType<F<T>> && CompleteType<F<T>>)
struct Cell {
    F<T> value;
};

generic<typefn F<type>, type T>
alias ApplyOne = F<T>;

generic<typefn H<typefn<type>, type>, typefn F<type>, type T>
alias ApplyHigher = H<F, T>;

generic<typefn F<type...>, type... Ts>
alias ApplyPack = F<Ts...>;
```

These constructs SHALL be compile-time mappings. Their applications SHALL retain the selected ordinary types' value, layout, lifetime, and effect contracts.

### 2.1 Formation and full application

A constructor argument SHALL designate a generic record, union, fully defined alias family, a bound constructor parameter or projection, or a constructor expression defined below. Its declared signature SHALL match the required kind. Every fixed parameter SHALL count, including a defaulted position; a final pack SHALL remain a repeated descriptor. Constant-parameter types SHALL match canonically. A fixed signature and a variadic signature SHALL retain their respective shapes; an explicit constructor expression may map between them where the resulting applications are valid.

A constructor identity SHALL contain its canonical declaration or expression identity, kind, captured bindings, and meaning-affecting definition environment. Applying a generic alias-family constructor SHALL yield the mapped type's ordinary identity while preserving the alias-family identity when that constructor itself is an argument. A transparent constructor alias SHALL preserve its referenced constructor identity under Section 3.

A full application through a bound typefn SHALL supply its fixed positions and its final pack elements. The checker SHALL substitute them, select the owning family's published specialization, establish its requirements, and obtain the resulting ordinary type. A direct named-family application may additionally use that family's declared defaults. A required unavailable application SHALL fail type formation under Chapter 27's context rules.

A typefn generic parameter may have a constructor-expression default whose free names bind in its definition environment. An omitted argument SHALL use an admitted deduction or that default. A final constructor-parameter pack SHALL collect the remaining explicit constructor arguments in order. Each application of a member of that pack SHALL use its member kind.

### 2.2 Explicit partial application

`partial_typefn<F, arguments...>` SHALL construct a residual constructor by binding a finite prefix of F's arguments. F SHALL first resolve to one constructor identity. Each supplied argument SHALL match the next fixed descriptor, or an element of its final repeated descriptor. The residual kind SHALL retain the remaining fixed descriptors and any final repeated descriptor.

```cxxn
generic<type Left, type Right>
struct Pair {};

generic<type... Ts>
struct Tuple {};

generic<typefn F<type>, type T>
requires (ObjectType<F<T>> && CompleteType<F<T>>)
struct Holder {
    F<T> item;
};

alias IntPairHolder = Holder<partial_typefn<Pair, i32>, u8>;
```

Applying the residual constructor SHALL prepend its captured prefix and fully apply F. Binding all fixed positions of a fixed constructor SHALL produce a nullary constructor. A prefix entering a final pack SHALL retain an open residual pack and prepend the captured elements to each later application. Binding an empty prefix SHALL preserve F's constructor identity.

Residual identity SHALL use F's identity, the canonical bound prefix, and the residual kind. Repeated prefix application SHALL flatten to this canonical representation: prefix-binding a residual constructor SHALL append to its captured prefix. Family defaults SHALL remain explicit source choices; a residual constructor SHALL retain every unbound fixed position.

A bound ordinary constant SHALL preserve its actual value and declared type; a bound type or constructor SHALL preserve its canonical identity. Capturing an argument SHALL establish its kind and required constant validity. Requirements depending on later arguments SHALL be checked when the residual constructor is applied.

### 2.3 Inline constructor mappings

`typefn<binder-list>(type-id)` SHALL form an inline constructor. Its binders SHALL use the generic type, constant, recursive typefn, and final-pack forms. The parentheses SHALL contain the resulting type expression. The mapping SHALL bind its other names, defaults used by named applications, and policies at its definition site.

```cxxn
alias TextPairHolder = Holder<typefn<type U>(Pair<U, char>), i32>;

generic<typefn F<type>, typefn G<type>, type T>
alias ComposeAt = typefn<type U>(F<G<U>>)<T>;
```

Each application SHALL substitute the inline binders into the captured type expression and establish its ordinary type-formation requirements. The same constructor expression with the same captured arguments SHALL have one constructor identity. Separate expression declarations may retain different constructor identities while their applications yield equal ordinary types.

Formation of an inline mapping SHALL establish binder kinds, captured names, and the mapped expression's nondependent legality. Dependent type formation SHALL occur for each full application under its actual arguments and declared evidence. An inline mapping may bind arbitrary positions, reorder arguments, prepend or append pack elements, and compose constructors. A pack expansion SHALL preserve element order and require compatible lengths for packs expanded together. A final pack SHALL consume the remaining arguments of that mapping. The checker SHALL normalize constructor applications through the finite substitution and cycle rules in Chapter 27.

For `generic<type T, const usize N = 4> struct BufferFamily {};`, bare BufferFamily has kind `typefn<type, const usize>`. The expression `typefn<type T>(BufferFamily<T>)` SHALL expose a unary constructor whose body uses the captured default. The expression `typefn<type T>(BufferFamily<T, 4>)` SHALL expose its explicit-value counterpart. Both SHALL record their captured definition dependencies.

### 2.4 Qualified names and dependent applications

An applied parameter, inline expression, residual constructor, or associated projection SHALL have its established kind before argument binding. For `T::Something<U>`, accessible declarations or declared constraints SHALL establish Something's kind. An imported alias may preserve constructor kind. Definition-site lookup and the grammar's generic-delimiter rules SHALL classify the expression.

A required kind comparison SHALL inspect the finite kind structure. Application SHALL perform substitution at the bound constructor and retain the fixed family or witness catalogue. Higher-order constructor values SHALL be supplied explicitly, by an admitted direct deduction, or by a declared default; Chapter 27 defines the deduction boundary.

## 3. Type and constructor aliases

A nongeneric `alias Name = right-hand-side;` SHALL bind according to the right-hand side's established kind. An ordinary type SHALL create a transparent type alias. An unapplied family, bound typefn, constructor projection, partial expression, or inline mapping SHALL create a transparent constructor alias. Bare family names SHALL retain constructor kind; a full application, including an explicit empty argument list using family defaults, SHALL yield its resulting ordinary type.

```cxxn
alias IntPair = partial_typefn<Pair, i32>;
alias ReversePair = typefn<type T>(Pair<T, i32>);
alias ConcretePair = IntPair<u8>;
```

The first two declarations SHALL preserve the identities of their constructor expressions. The third SHALL have the selected Pair application's ordinary type identity. The alias declaration SHALL retain its own declaration identity for visibility, publication, and reflection. Constructor matching and application SHALL follow the referenced constructor identity.

### 3.1 Generic alias families

`generic<...> alias Name = type-id;` SHALL declare a compile-time alias family with an ordinary-type result. Its parameters and optional requires clause SHALL follow the ordinary generic declaration rules. Definition checking SHALL establish its bound names, kinds, and nondependent legality; each admitted full application SHALL form its dependent mapped type under its actual arguments and constraints.

The selected application shall have the resulting type's canonical identity, including its selected specialization. The alias family shall have a separate stable declaration identity for constructor arguments and witnesses. Thus `SameType<Alias<i32>, Underlying<i32>>` may hold while the two constructor declarations remain distinct.

An exported alias shall publish the type and constraint material needed to validate its permitted public applications. Its runtime layout and foreign compatibility shall be those of the selected underlying type. Recursive alias expansion shall satisfy the termination and cycle rules in Chapter 27.

## 4. Associated type and constant requirements

A constraint containing associated entities SHALL use its first formal parameter, an ordinary `type` parameter, as its single subject. Its remaining type, constant, and constructor parameters SHALL be additional witness arguments. A pure structural constraint may use any admitted parameter sequence. A constraint may declare associated entities:

```cxxn
constraint Sequence<type S> {
    associated type Item;
    associated const usize StaticExtent;
    expression (const<S>& source) {
        source.size() -> usize;
    }
};
```

`associated type Item;` SHALL require one ordinary type binding. `associated const usize StaticExtent;` SHALL require one admitted constant of that type. An associated declaration may provide a default binding with `=`, evaluated under that constraint's captured environment after substitution. The complete constraint application SHALL own the associations; its subject SHALL retain its ordinary members and representation.

`Sequence<S>::Item` and `Sequence<S>::StaticExtent` SHALL project the selected association. A concrete projection SHALL resolve one witness under Section 5; a symbolic projection SHALL use its declared constraint bound. A projected constant may participate in required constant evaluation. The full constraint argument tuple, including every additional parameter, SHALL enter the witness key.

Inside the declaring constraint, an unqualified associated identifier shall denote that constraint's associated declaration. Another generic definition shall establish the relevant bound:

```cxxn
generic<type S>
requires (Sequence<S>)
alias SequenceItem = Sequence<S>::Item;
```

The alias yields the projected ordinary type. An operation such as `source.first()` shall separately have a supporting structural expression requirement or ordinary declaration. Additional associated-type relationships shall use explicit requirements, for example `requires (SameType<Sequence<S>::Item, i32>);`. Access to a private binding shall require its ordinary published authority.

### 4.1 Associated type constructors

`associated typefn Name<kind-list>;` shall require a constructor binding with the kinds in Section 2:

```cxxn
constraint Rebindable<type T> {
    associated typefn Rebind<type>;
};
```

For a selected conformance to `Rebindable<Box<i32>>`, `Rebindable<Box<i32>>::Rebind<u8>` shall apply its bound constructor and yield an ordinary type. The bare projection `Rebindable<Box<i32>>::Rebind` shall retain typefn kind and may supply a matching constructor parameter. Its applications shall satisfy the selected family constraints, completeness, constant-evaluation, and public-reachability requirements.

## 5. Structural and explicit witnesses

The checker SHALL obtain a concrete witness from the subject owner's bound public catalogue and the structural fallback defined here. Explicit `satisfy` declarations SHALL provide customized association tables or certify a chosen contract:

```cxxn
struct SampleBuffer {
    usize size() const { return 4; }
};

satisfy Sequence<SampleBuffer> {
    type Item = i32;
    const usize StaticExtent = 4;
};
```

For one candidate, the checker SHALL form an association table of bound recipes using this precedence for each required entity:

1. The candidate's explicit binding, when present.
2. The associated declaration's default, when present.
3. The subject's uniquely resolved, accessible nested entity of the same name and required kind.

A nested alias or type SHALL supply an ordinary type association. A required constant SHALL supply its declared canonical constant type and value. A nested generic family, constructor alias, or associated constructor expression SHALL supply a matching typefn association. The checker SHALL evaluate the candidate condition and its selected requirements using the recipes needed by that evaluation. A condition that evaluates False SHALL end that candidate's applicability check. An applicable candidate SHALL complete every required binding and establish all structural and Boolean requirements before witness commitment.

The structural fallback SHALL use the same procedure with an empty explicit table. Thus an ordinary type exposing the required operations and nested entities may satisfy the constraint directly. Declared defaults may map differently named members or derive associations under the constraint's captured contract.

```cxxn
struct NativeSequence {
    alias Item = i32;
    static constexpr usize StaticExtent(4);
    usize size() const { return 4; }
};

alias NativeItem = Sequence<NativeSequence>::Item;
```

The example SHALL obtain its associations structurally. The size expression SHALL separately satisfy the declared result and receiver contract. A constraint containing structural requirements alone SHALL use the same requirement checking with an empty association table.

### 5.1 Conformance priority and selection

Each explicit `satisfy` declaration SHALL have one fixed conformance priority. The registered leading attribute `[[conformance_priority(N)]]` SHALL set that priority to its nondependent required integer constant N in the inclusive range 0 through 4294967295. An omitted attribute SHALL supply priority 0. The attribute SHALL apply to an authored `satisfy` declaration, and its value SHALL bind at declaration checking. Duplicate priority attributes, a dependent value, or a value outside the admitted range SHALL produce a declaration error. This compile-time metadata value SHALL have the same ordering on every target.

A bare integer literal SHALL supply its exact literal value to priority admission. A named constant or compound expression SHALL first complete ordinary required integer constant evaluation under its captured definition policy. Admission SHALL compare that mathematical result with the priority interval. The admitted priority SHALL be compiler metadata independently of target integer storage or runtime object materialization.

Priority comparison SHALL apply to the entries considered for one concrete witness request in its bound owner catalogue. Entries in unrelated catalogues may reuse the same integer. Equal priorities among entries whose concrete heads or conditions are mutually exclusive SHALL use the ordinary applicability rules.

Chapter 27 SHALL select each concrete witness by visiting head-matching entries in descending priority tiers. One established entry in the first successful tier SHALL supply the witness. Several established entries in that tier SHALL produce ambiguity. A tier whose entries all produce False SHALL pass selection to the next tier. Exhausting the tiers SHALL request structural fallback. Conformance ranking SHALL use the declared integer priorities; the separately defined function-overload and type-specialization rules SHALL govern those other selections.

Malformed, cyclic, unestablished required-proof, and exhausted-resource outcomes in a visited tier SHALL retain Chapter 27's distinct consequences. Publication SHALL establish every entry's nondependent legality. Dependent requirements in lower tiers SHALL remain demand-driven after an earlier tier supplies the witness.

An explicit association table may omit entities supplied by defaults or nested matches. Every completed table SHALL have one well-kinded, accessible, finite binding for each required entity. Checking the constraint's own associated projections within a candidate SHALL use that provisional table. A dependency that recursively requests selection of the same unresolved witness key SHALL follow Section 8's cycle rule.

#### 5.1.1 Design rationale and catalogue coordination (informative)

Fixed integer priorities give the conformance selector an explicit ordering key. Grouping and comparing these keys determines the order in which the checker visits tiers; head matching, concrete requirement checking, and witness validation remain necessary. The design favors a small, directly implementable selection procedure.

An integer records an absolute rank. Authors express an intended relationship such as one entry taking precedence over another by choosing the corresponding ranks. This places coordination work on the owner of a catalogue assembled by multiple authors. Independently chosen ranks can create an unintended precedence or an equal-priority ambiguity when entries overlap. Continued insertion of intermediate or higher-precedence entries can consume gaps and encourage increasingly large ranks. The finite priority range makes this an explicit library-maintenance constraint.

A catalogue maintainer can centralize named priority constants, document the purpose of each tier, and review newly overlapping entries against that policy. Reserving gaps or allocating ranges to contributors can reduce routine coordination, while later additions still require agreement on precedence. Equal ranks are useful for alternatives with concretely exclusive conditions. The owner can reuse the same numerical conventions in unrelated catalogues, whose selections remain independent.

Priority assignments form part of the published catalogue contract. Changing them can change witness selection; even an order-preserving renumbering changes the identity material specified by Chapter 27. A catalogue revision therefore needs the same dependency and compatibility review as other changes to its conformance contract. These coordination costs are a deliberate tradeoff of explicit scalar ordering, and the language's simple selection procedure leaves them with catalogue authors.

### 5.2 Ownership and catalogue binding

The subject's canonical nominal type or family owner SHALL control its public conformance catalogue. That owner may publish a conformance to a foreign constraint. A constraint owner may publish conformances for its own types and for primitive or built-in families assigned to its registered standard-capability domain. An owning scope needing a different custom public conformance for another owner's type SHALL expose its own nominal adapter; structural satisfaction remains available from accessible declared members.

A family conformance for `Box<T>` SHALL belong to Box's canonical catalogue. `export satisfy`, or an equivalent export block, SHALL publish it. Publication SHALL validate declaration identity, ownership, signature, priority, and nondependent requirements and record the complete candidate set. Overlapping patterns SHALL be admitted; each required concrete use SHALL perform Section 5.1's selection. Ordinary duplicate-definition rules SHALL govern duplicate canonical declaration identities.

A private conformance SHALL concern a private nominal subject in its owning compilation scope and preserve its declared visibility. Exported uses SHALL publish the witness contract they require or expose an explicit public opaque adapter.

For a known subject, a generic definition SHALL capture the required catalogue identity and revision. For a symbolic subject, its declared constraint bound SHALL capture the subject-owner catalogue-selection recipe. Substitution SHALL obtain that catalogue from the actual canonical type argument's published owner contract and freeze its exact identity in the instance. Structural member lookup SHALL use that same subject contract. A later unrelated import SHALL retain these inputs; a catalogue revision becomes a new bound input at the appropriate recompilation boundary. Existing bound projections and emitted instances SHALL retain their selected witnesses.

### 5.3 Conditional conformance and constructor binding

```cxxn
generic<type T>
requires (CompleteType<T>)
satisfy Rebindable<Box<T>> {
    typefn Rebind<type U> = Box<U>;
};
```

The subject owner SHALL publish this conditional entry. Its local constructor binder SHALL follow Section 2's recursive kind and pack rules and map U to `Box<U>`. A conditionally applicable entry SHALL use its declared requirements during selection; the selected constructor's applications SHALL establish their resulting type requirements.

A specialized entry may provide a different association for a concrete subject or a narrower admitted pattern. Its author SHALL select a higher priority when that entry is intended to take precedence over another applicable entry. The selected entry SHALL establish the complete associated and callable contract it advertises.

```cxxn
constraint ElementSource<type S> {
    associated type Item;
};

generic<type T>
struct Pocket {
    alias Item = T;
};

generic<type T>
satisfy ElementSource<Pocket<T>> {
    type Item = T;
};

[[conformance_priority(1)]]
satisfy ElementSource<Pocket<i32>> {
    type Item = u32;
};
```

`ElementSource<Pocket<i32>>::Item` SHALL be u32 through the priority-1 entry. Another `Pocket<T>` SHALL use the priority-0 entry when its requirements hold. Giving both matching entries priority 0 SHALL produce ambiguity for the i32 application. Their textual order SHALL preserve these results.

### 5.4 Structural fallback provenance

Chapter 27 SHALL diagnose a successful structural fallback reached after all head-matching explicit entries produce False. Diagnostic `GEN001` SHALL use Chapter 08's default ANOMALY classification and diagnostic configuration. A purely structural use whose bound catalogue has no head-matching explicit entry SHALL use its ordinary structural result.

For example, consider a separate owner catalogue containing the following sole explicit entry for the preceding `ElementSource` and `Pocket` declarations:

```cxxn
generic<type T>
requires (SameType<T, u8>)
satisfy ElementSource<Pocket<T>> {
    type Item = u8;
};

alias SelectedItem = ElementSource<Pocket<i32>>::Item;
```

The head SHALL match `Pocket<i32>`, its condition SHALL evaluate False, and structural fallback SHALL obtain i32 from the nested Item alias. The successful SelectedItem binding SHALL produce `GEN001` with that provenance. Its diagnostic SHALL distinguish an inapplicable explicit entry from the structural witness actually selected.

## 6. Dependent projection and use-site obligations

A generic requiring `Sequence<S>` shall use its Item as a symbolic ordinary type while checking the definition. Instantiation shall substitute the selected witness binding under the captured environment.

| Source notation | Meaning |
| --- | --- |
| `S::Item` | Ordinary accessible nested type of S. |
| `Sequence<S>::Item` | Associated type from the selected Sequence conformance. |
| `Sequence<S>::StaticExtent` | Constant from that conformance. |
| `Rebindable<S>::Rebind` | Associated constructor of typefn kind. |
| `Rebindable<S>::Rebind<U>` | Ordinary type produced by that constructor. |

An explicit `SameType<S::Item, Sequence<S>::Item>` requirement may relate the first two forms. When multiple constraints declare the same associated name, an external use shall qualify the projection with its constraint application. The chosen witness shall supply that projection.

A proved associated-type equality shall permit type substitution under Chapter 27. Each resulting value operation shall independently satisfy its value category, object state, lifetime, and effect requirements.

## 7. Structural witnesses and callable contracts

An expression requirement shall match the exact result type and value category specified by Chapter 10. A callable witness shall record the selected declaration or intrinsic, generic arguments, receiver qualifiers, signature, effect bounds, nonthrowing guarantee, and returned-borrow provenance.

The checker shall establish the required callable relationship under [Chapter 25](25_effect_composition_and_boundaries.md#chapter-25-effect-composition-boundaries). A closed effect bound requires corresponding evidence; merely naming an open callable in a satisfy table leaves that obligation unestablished. Ownership, destruction responsibility, and foreign-call guarantees shall come from the operation's actual contract or an explicit conforming adapter.

A symbolic associated result shall remain part of the required signature until concrete witness selection substitutes its binding. The generic body shall use the operations supplied by its declared requirements and ordinary language rules.

## 8. Associated-type recursion and well-foundedness

Associated bindings may depend on completed immutable constants and constructor applications. The evaluator shall resolve those dependencies using Chapter 27's cycle and termination rules. A self-projection such as `type Item = Sequence<S>::Item;` requires an independent completed nominal boundary to terminate resolution.

Recursive nominal families may use legal pointer and reference members. Every required value layout shall remain finite and complete under Chapter 10. Constraint, alias, reflection, and generation dependencies shall use their shared staged graph; required completion shall establish a complete witness within the configured resource limit.

## 9. Borrowing, ownership, and lifetime interaction

A projected type shall retain its concrete storage and borrowing obligations. A returned `Sequence<S>::Item&` shall identify its source region under Chapter 25. A generic returning a borrowing wrapper shall publish that source relationship even when its element type varies by witness.

The selected concrete type's copy, move, destructor, numerical, and allocator contracts shall govern those operations. Sharing a constructor family establishes the mapping relationship; each application's operation contracts remain independently checked.

## 10. Publication, ABI, and optimization

A public interface SHALL publish its recursive constructor kinds, pack shapes, constructor-expression mappings and captured arguments, constraints, catalogue bindings, and each explicit entry's conformance priority. A known subject SHALL carry its bound catalogue; a symbolic subject SHALL carry Chapter 27's subject-owner resolution recipe. A completed instance SHALL record its frozen concrete catalogue and selected witness identities. Consumers shall bind the published recipe or completed contract under its definition environment. Changing an associated binding or selected priority contract that changes a public type, ABI, or effects requires a compatible versioned bridge or an incompatible-interface diagnostic.

Publication here SHALL expose the semantic contract to its admitted consumers. The selected compilation and contract-export capabilities SHALL govern its internal transport or standardized external representation under Chapters 11, 21, and 29.

The instance identity in Chapter 10 SHALL additionally include canonical constructor expressions and captured bindings, pack lengths and ordered elements, selected conformance witnesses, and associated bindings relevant to the emitted instance. A structural witness SHALL identify the constraint application, subject, bound catalogue, and canonical default/member/operation declarations used to establish it. Code sharing shall preserve the observations defined by Chapter 21. An explicit erased adapter shall publish its runtime representation, ownership, lifetime, and call contract separately.

A selected `F<T>` shall meet the particular foreign ABI profile before use at a compatible boundary. Native object emission and explicit C/C++ adapters follow [Chapter 09](09_native_interoperability.md#chapter-09-native-interoperability).

## 11. Capability control and diagnostics

[Chapter 08](08_runtime_configuration.md#chapter-08-runtime-configuration) owns the capability domains and defaults. `generic.higher_kinds` controls typefn parameters, recursive constructor kinds, constructor packs, and constructor expressions. `generic.associated_entities` controls associated entities, structural associated witnesses, and explicit conformance. Their use SHALL require the corresponding explicit capability selection. Ordinary type and constant parameters, their packs, generic functions, and structural constraints SHALL retain their Core meaning independently.

A use shall have its required capabilities at parsing, checking, import, and instantiation. Required compilation-resource failures shall use Chapter 27's distinct resource outcome.

| Case | Required result |
| --- | --- |
| A constructor accepts another constructor | Recursively match its finite kind and establish the full application. |
| A fixed kind receives a family with a defaulted second position | Compare the full fixed signature; an explicit mapping may bind the default and expose unary kind. |
| A variadic constructor receives an empty final pack | Apply it with that empty ordered sequence. |
| A constructor-parameter pack receives several constructors | Bind each kind and preserve source order. |
| A prefix binds every fixed constructor parameter | Produce a nullary residual constructor. |
| A prefix enters a final pack | Preserve a residual repeated descriptor and prepend the captured elements. |
| A structural subject supplies all associations and operations | Establish the fallback witness when the explicit candidate set is empty. |
| Two explicit conformances overlap at different priorities | Visit the higher tier first and select its unique established entry, or continue after all its entries produce False. |
| The first successful priority tier has several established entries | Report ambiguity at that use. |
| An earlier successful tier leaves lower dependent requirements unvisited | Preserve the selected witness and the lower entries' declaration checks. |
| Every head-matching explicit entry is False and structural fallback succeeds | Select the structural witness and produce GEN001 under the diagnostic policy. |
| No explicit head matches and structural fallback succeeds | Select the structural witness through ordinary structural checking. |
| Associated bindings form an unresolved cycle | Report the cycle under required type formation. |
| A declared compilation budget is exhausted | Report Resource exhausted separately from False. |
| A caller adds an import | Existing generic definitions retain their bound catalogues and selections. |
| A required constructor capability is unavailable | Report the capability requirement at its use. |

## 12. Conformance requirements

An enabled implementation shall accept well-formed declarations within its published capabilities and resource limits, establish recursive kinds and associated bindings, validate catalogue authority, select coherent witnesses at required uses, and preserve the selected numeric, lifecycle, ABI, and effect contracts. The checker shall report required-proof and resource outcomes using Chapter 27 and the diagnostic policy in Chapter 08.

