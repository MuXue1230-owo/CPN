<a id="chapter-27-constraint-solver-inference"></a>

# CPN26 Constraint Solving, Type Inference, and Coherence Specification

## 1. Scope and required determinism

This chapter owns generic deduction, requirement checking, constrained candidate selection, type-specialization selection, and witness-coherence checking. [Chapter 10](10_types_functions_generics.md#chapter-10-types-functions-generics) owns ordinary type and declaration identity, lookup, and conversion ranks. [Chapter 26](26_advanced_generic_families.md#chapter-26-advanced-generic-families) owns constructor kinds and associated declarations.

For a fixed source, published interface set, target, and effective configuration, the checker shall produce the same successful bindings and candidate selection independently of optimization, worker scheduling, physical source path, process address, and import order. It shall use the standardized proof procedure and report required compilation-resource limits separately.

Required type and generic proofs remain part of language validity under every analysis preset. The local or interprocedural modes in [Chapter 24](24_contracts_and_effects.md#chapter-24-contracts-effects) govern optional analysis of ordinary programmer obligations. The solver shall classify its required proof outcomes by Section 3.

## 2. Constraint proposition model

A constraint shall combine the following admitted propositions:

| Proposition | Required evidence or evaluation |
| --- | --- |
| A constant Boolean expression | Required evaluation under its captured environment. |
| A named constraint application | Expansion of its declared requirements at canonical arguments. |
| A structural type or expression requirement | The specified type or operation contract. |
| A core type predicate, including SameType | The predicate's defined language relation. |
| An associated projection or witness requirement | A declared symbolic bound or a selected concrete conformance. |
| Negation, conjunction, or disjunction | Standard Boolean composition of admitted propositions. |
| An effect, ownership, category, or nonthrowing requirement | The corresponding bound callable contract. |

A canonical atom shall include its predicate kind, declaration or intrinsic identity, canonical type/value/constructor arguments, and meaning-affecting definition policy. Renaming a bound parameter shall preserve its position and atom identity. Same-spelled predicates owned by different declarations shall retain distinct identities.

Normalization shall substitute the named constraint's parameters and expand its requirements under its immutable definition environment. It shall preserve structural-operation and associated-projection identities, and evaluate only the branches selected by the required constant-evaluation rules.

### 2.1 Boolean normalization and subsumption

Subsumption shall use propositional implication over equal canonical atoms after named-constraint expansion. Boolean constants, negations, and duplicate conjuncts or disjuncts shall follow ordinary propositional identities.

For symbolic ordering, `N > 0` and `N >= 1` are distinct atoms. For concrete applicability, each predicate shall evaluate at the selected N under its captured numerical policy. An ordering proof that requires an additional mathematical equivalence remains unestablished by the standard procedure.

If neither constraint propositionally implies the other, the checker shall leave their relative constraint rank tied. Section 5 shall resolve the resulting candidate set using the other standard ranks or report ambiguity.

### 2.2 Type equalities and projections

Proved type identities shall form an equality relation within their evidence scope. The checker may substitute equal types through pointers, references, fixed arrays, and well-formed constructor applications. The resulting value operations shall still satisfy their ordinary conversion and object requirements.

A proposition involving `Sequence<T>::Item` shall first have a declared Sequence bound or a selected witness. Equality of two resulting ordinary types shall preserve the distinct declaration identities of the constructors that produced them.

Successful equality closure shall be finite. Infinite alias expansion, an infinite required value layout, or an invalid witness cycle shall fail under the corresponding type-formation rule.

## 3. Applicability and proof outcomes

The checker shall perform a concrete generic use in this semantic order:

1. Bind nondependent names and catalogue identities at the definition site.
2. Bind explicit arguments and perform the deductions admitted by Section 4.
3. Establish recursive parameter kinds, fixed and final-pack shapes, visibility, capabilities, and constant domains under Chapter 26.
4. Select required owning-family specializations and unique conformance witnesses.
5. Substitute canonical arguments and associated bindings into requirements.
6. Evaluate required constant predicates under the captured target and numerical policy.
7. Establish structural signatures, receiver categories, effects, borrow origins, and required operations from the available evidence.
8. Check the selected body under its immutable definition contract.

Each checking operation shall yield one of these outcomes:

| Outcome | Meaning and consequence |
| --- | --- |
| Established | The proposition or operation has the required evidence; checking may use it. |
| False | A well-formed concrete predicate is false, or a declared structural operation is absent or incompatible; that candidate is inapplicable. |
| Unestablished | The declared symbolic domain supplies insufficient evidence; the dependent operation remains unavailable, and a use requiring that proof fails. |
| Malformed | Grammar, nondependent binding, required declaration legality, or catalogue coherence is invalid; compilation reports the error. |
| Resource exhausted | A required evaluation or solver step exceeds its configured resource limit; compilation reports a distinct resource error. |

Only the False outcome removes an otherwise well-formed candidate through requirement applicability. Once a body is selected, its invalid operation is a body error. Required constraints and explicit proof requests shall use this table even when ordinary optional analysis would report an unknown programmer obligation as ANOMALY.

### 3.1 Short-circuiting and errors

Required Boolean evaluation shall visit the branches selected by ordinary short-circuit rules. Both branches shall retain their parsing, nondependent binding, and declaration-legality obligations. The explicit `if constexpr` rule in Chapter 10 supplies the corresponding dependent-operation branch facts.

A required evaluation reaching Numeric Trap, another terminal failure, or an inadmissible operation shall fail evaluation. A returned Result error remains an ordinary value. Its explicit success or error predicate may yield a Boolean requirement; Result itself requires that explicit interpretation.

## 4. Generic argument deduction

Deduction shall match formal type structure against the actual typed argument's canonical type and value category:

| Formal form | Deduction rule |
| --- | --- |
| By-value T | Deduce the adjusted source value type using Chapter 10's top-level qualification rule. |
| `T&`, `const<T>&`, or `T&&` | Apply the stated reference and category requirement. |
| `forward T` | Deduce U& for an lvalue U and qualified U for an expiring expression; explicit forwarding restores the source category. |
| `T[N]` | Deduce the complete element type and exact constant extent. |
| A repeated parameter | Require one identical canonical deduction at all occurrences. |
| A final type or constant pack | Deduce its ordered elements under the declared kind; include its length in instance identity. |
| `typefn F<...>` | Use an explicit constructor expression, direct canonical-argument deduction below, or its declared default; establish the recursive kind. |
| A final typefn parameter pack | Bind its explicit or directly deduced ordered constructor arguments under the element kind; include its length and identities in instance identity. |
| A parameter appearing only in an associated projection, computed expression, or result context | Require an independent admitted deduction or an explicit argument. |

When a formal and actual ordinary type share one known nominal generic family, the checker SHALL compare the canonical generic arguments stored in that family instance. A formal constructor parameter in one such argument position SHALL deduce the actual stored constructor identity and its kind. For example, matching `Holder<F,T>` against the canonical instance `Holder<Vec,i32>` SHALL deduce F as Vec and T as i32 when Holder's published parameter kinds identify those positions. A final constructor pack in such a known position SHALL deduce the stored ordered sequence. Repeated deductions SHALL agree canonically.

A composed constructor expression in a formal argument position SHALL be compared after its parameters are independently bound. A parameter appearing solely through a constructor's ordinary result SHALL require an independent binding. These rules use preserved family arguments as evidence; actual record layout or result-type similarity supplies its ordinary type identity alone.

The checker SHALL use these structural matches and the constructor expressions explicitly supplied by source. A constructor appearing solely through the ordinary type produced by its application SHALL obtain its argument independently or from a declared default. An explicit argument SHALL fix that parameter, then participate in ordinary constraint and call-conversion checking at every occurrence. Inline and partial constructors SHALL normalize by applying their captured mappings, while constructor identity SHALL follow Chapter 26.

### 4.1 Contextual typing and literals

A concrete parameter type may provide an untyped numeric expression's context under the numeric rules. Deduction of an otherwise unconstrained value type from an untyped expression shall first use the resolved default literal type. An already typed value shall retain its type for deduction.

`auto name(expression);` shall use Chapter 10's value-type deduction. The established result may be an associated type; its object construction and lifetime remain ordinary operations on that selected type.

An exported generic return type shall be expressible using its declared constraints and reachable public interface material. An implementation-private type or proof requires publication of the necessary contract or an explicit public opaque interface.

## 5. Overload candidate selection

The checker shall select a call before evaluating its runtime arguments:

1. Form the reachable declaration set using Chapter 10's lexical and definition-site lookup.
2. Check callable kind, receiver category, required arity, pack binding, generic kinds, and explicit arguments.
3. Deduce permitted arguments and evaluate each candidate's declared requirements.
4. Remove False candidates and report malformed or resource outcomes using Section 3. A deleted or inaccessible declaration shall remain in the set until selected-declaration validation.
5. Compare Chapter 10's conversion ranks argument by argument. One candidate has a better conversion sequence exactly when every argument is at least as good and at least one is better.
6. For indistinguishable conversion ranks, prefer an applicable strictly more specialized generic pattern or a strictly stronger normalized constraint. Otherwise prefer a nongeneric declaration over an otherwise identical unconstrained generic declaration.
7. Select the unique best declaration, or report ambiguity. Validate its access, deletion status, effects, ownership, lifetime, nonthrowing guarantee, ABI, and body.

A declared target function-pointer contract may select an overload address under Chapter 10. Ordinary call ranking shall use the arguments and declared receiver requirements; its result type alone supplies no additional preference. Qualified names and explicit generic arguments may restrict the candidate set.

Two equally ranked applicable predicates remain tied unless the standard subsumption procedure orders them. Declaration position, body size, and estimated runtime cost leave that tie unchanged.

### 5.1 Constraint subsumption examples

```cpn
constraint Readable<type T> {
    expression (const<T>& value) {
        value.read() -> i32;
    }
};

constraint ReadableAndSized<type T> {
    requires (Readable<T>);
    expression (const<T>& value) {
        value.size() -> usize;
    }
};
```

For identical parameters and conversion ranks, ReadableAndSized is stronger because its normalized requirements entail Readable's identical requirements. A selected type shall still supply the required operations.

Overloads constrained by symbolic `N > 0` and `N >= 1` remain tied by constraint rank. At a concrete positive N, both may be applicable; another standard rank or an explicit source selection must distinguish them.

## 6. Type-specialization and conformance selection

An owning type family SHALL select among its published specializations by structural pattern specificity followed by standard constraint subsumption. Selection SHALL yield one unique best applicable entry. The primary definition SHALL serve as the fallback when its own requirements hold and the catalogue contains no better applicable entry. An ambiguous set or invalid selected body SHALL fail that use.

For type specialization and the pattern rank in Section 5, structural specificity SHALL compare head patterns using finite structural matching. Pattern A is strictly more specific than B when B's parameter pattern matches A's symbolic head and the converse match fails. Concrete nominal constructors, fixed arguments, enabled constructor kinds, and ordered pack shapes SHALL participate in that comparison. An identity or expression that this matcher leaves unestablished SHALL leave that relative pattern rank tied. Constraint ordering SHALL use Section 2.1's normalized symbolic requirements. Explicit conformance selection SHALL instead use the fixed priority algorithm below.

### 6.1 Conformance selection by priority

A public conformance catalogue SHALL admit overlapping head patterns. Every entry SHALL carry Chapter 26's conformance priority, with 0 as the default. For one required concrete constraint application, selection SHALL proceed as follows:

1. Obtain the complete bound owner catalogue and group its entries by equal priority. Visit the groups in descending numeric order. One group SHALL constitute one priority tier.
2. In the visited tier, match the complete subject and additional arguments against each entry's head using Section 4's direct argument deduction. A definite structural mismatch SHALL exclude that entry. A matching head SHALL bind its parameters and provisional association recipes. An unresolved required head match SHALL retain Section 3's proof or resource outcome. A tier with zero matching heads SHALL advance to the next tier.
3. For each head-matching entry in the visited tier, evaluate its declared condition under the short-circuit rules. A condition that produces False SHALL complete that entry as False. For an established condition, complete the required associations and establish the constraint's full requirements, evaluating each association recipe when that checking needs it.
4. Establish the complete result of the visited tier. False SHALL remove that entry from that tier's established set. A required-proof failure, malformed dependent use, dependency cycle, or resource exhaustion SHALL produce its distinct error for the required witness. Several established entries SHALL produce ambiguity. Exactly one established entry SHALL become the selected witness. A tier whose head-matching entries all produce False SHALL advance to the next tier.
5. After the tiers are exhausted, establish the structural fallback with an empty explicit association table. Its established, False, or required-error result SHALL become the result of that witness request. A required projection or operation whose constraint is False SHALL fail its corresponding requirement.
6. Commit an established witness's identity, associated bindings, callable evidence, bound catalogue, and selection provenance together.

The first successful tier SHALL complete conformance selection. Lower tiers' concrete head matches, dependent conditions, and association recipes SHALL remain unvisited for that request; their nondependent legality SHALL already have been checked when their declarations entered the catalogue. A selected witness's later invalid use SHALL produce that use's required error under its committed contract.

Conformance priority SHALL be the complete ordering key among matched entries. Head matching SHALL determine argument bindings and eligibility. Conditions SHALL determine applicability. These steps SHALL keep conformance ranking independent of pairwise pattern comparison or predicate implication. Equal priorities SHALL retain their tie until concrete applicability yields one established entry or an ambiguity error. Declaration order, import traversal, and optional optimizer discoveries SHALL preserve the result.

Catalogue publication SHALL validate declaration identity, ownership, enabled kinds, fixed priority, and nondependent legality. Changing a priority SHALL change the catalogue's semantic contract. Selected type specializations and selected structural or explicit witnesses SHALL enter instance identity independently.

### 6.2 Structural fallback provenance

A successful structural witness SHALL produce diagnostic `GEN001` when its selection visited at least one head-matching explicit entry and every such entry produced False. The diagnostic SHALL identify the requiring use, canonical constraint application, bound owner catalogue, head-matching declarations, the established False reason for each entry, and the selected structural bindings or operations. Chapter 08 SHALL determine its default ANOMALY severity and configured presentation, suppression, or promotion.

An owner catalogue's unrelated head patterns SHALL contribute their definite mismatch outcome alone. A structural witness formed with zero head-matching entries SHALL use ordinary structural checking. Selecting a lower-priority explicit entry SHALL preserve its explicit provenance. A structural fallback that itself produces False SHALL retain that False outcome. A visited ambiguity, required-proof failure, malformed use, dependency cycle, or exhausted resource SHALL retain its required error. These outcomes distinguish successful alternative structural selection from explicit selection, absence of conformance, and failed checking.

An implementation may coalesce GEN001 occurrences for one canonical witness key within a compilation request. The reported diagnostic SHALL retain at least one requiring-use location and identify coalesced uses. A successful witness cache entry SHALL retain its selection provenance, including the False explicit entries. Reusing the entry SHALL apply the current request's diagnostic configuration, so caching and checking order preserve the required diagnostic outcome.

### 6.3 Witness coherence and semantic publication

An owning compilation scope SHALL retain canonical identifiers and semantic contracts for the catalogues needed by its constraints. A generic definition SHALL bind known catalogue identities together with its constraint contracts. A symbolic subject bound SHALL bind the subject-owner selection recipe; at instantiation, the actual canonical type argument's owner contract SHALL supply the exact catalogue and structural member contract. The instance SHALL freeze those substituted inputs. Compilations using the same full arguments and bound inputs SHALL select the same witness and associated bindings.

An explicit witness identity SHALL contain the selected satisfy declaration, canonical arguments, fixed priority, bound catalogue, and its relevant bound dependencies. A structural witness identity SHALL contain the constraint application, subject identity, bound catalogue, and canonical default/member/operation declarations forming its association table and requirements. A witness cache SHALL use these complete inputs. A cache entry SHALL become available after successful validation; an in-progress entry SHALL remain a dependency under the cycle rules.

A public boundary exposing an associated type or effect SHALL carry the selected witness dependency needed to interpret it. An image containing incompatible contracts for one canonical public identity SHALL report interface incompatibility. Duplicate-symbol merging SHALL require matching semantic identities. A separately revised catalogue SHALL be a distinct bound input; previously compiled definitions SHALL retain their bound selections until explicitly rebound through recompilation or a supported interface translation. Chapters 11 and 21 SHALL govern the selected compilation capability, and Chapter 29 SHALL encode these contracts when standardized contract export is selected.

## 7. Definition checking, recursion, and termination

A generic value-operation body SHALL establish its dependent operations throughout its declared parameter domain. Chapter 10's compile-time guards may refine that domain for a selected branch. A type mapping SHALL use Chapter 26's recipe rule: its definition establishes kinds and nondependent legality, and a required full application establishes the dependent result type under its concrete bindings. Definition-site name binding SHALL remain fixed in both cases.

An ordinary recursive function shall satisfy its signatures, lifecycle behavior, and effects; its execution may diverge unless it declares a stronger progress contract. Required compile-time recursion shall finish within the declared evaluation resources and satisfy the finite type and dependency rules.

Alias applications, partial and inline constructor normalization, witness formation, constraints, reflection, and generation SHALL resolve through completed acyclic requirements or a well-founded terminating evaluation. The checker SHALL count the visited finite kind nodes, substitutions, expanded argument positions, and proof work against their declared resources. A recursive kind descriptor SHALL remain a finite tree; a type-level computation may recur through separately declared mappings when its required evaluation completes. Recursive nominal records may use pointer or reference boundaries while retaining finite required value layouts. A resource limit shall produce the Resource exhausted outcome rather than a completed proof.

## 8. Effects, ownership, borrowing, and specialization

The selected instance shall retain its definition-site numerical, lifecycle, and effect policies. A callable witness shall satisfy the required receiver, return category, nonthrowing, borrow-source, escape, retention, consumption, and phase-specific effect contracts under Chapters 24 and 25.

A declared closed callable contract shall supply the interface evidence defined by Chapter 24; the implementation's body-checking obligations follow that chapter's selected validation mode. An open callable supplies only its conservative bound. Optional optimizer discoveries shall leave the published witness contract unchanged. A generic requiring a stronger bound shall obtain a supporting declared contract, established proof, or explicit conforming adapter.

Type substitution shall preserve the selected concrete type's independent copy, move, lifetime, destruction, abandonment, resource, and numerical contracts. A required unavailable allocator, format, or provider shall fail the corresponding capability check.

An asynchronous callable witness shall carry its independent admission and execution effects. Substitution shall preserve Chapter 25's phase order and Chapter 28's selected failure outlets.

## 9. Constant evaluation, reflection, and generation

Constraint selection shall use authored declarations and successfully committed generated declarations at the stages defined by [Chapter 23](23_compile_time_generation.md#chapter-23-compile-time-generation). Reflection shall require Chapter 22's capability, query readiness, and access authority.

Explicit satisfy declarations SHALL remain authored catalogue entries. A permitted generation transaction may supply ordinary methods, aliases, generic declarations, and constraints within its typed-syntax capability. After commitment, those declarations may establish a structural witness or an authored conformance's requirements. The checker SHALL resolve the witness after its required declarations become complete and retain their committed identities in its dependency set.

Reflection and derivation shall use Chapter 23's single stage and grant model. A query depending on the querying transaction's uncommitted output shall fail the dependency check. A required constraint or generation budget failure shall use Section 3's resource outcome and preserve candidate-selection determinism.

## 10. ABI, identity, and separate compilation

An exported generic interface shall contain the declaration, kinds, requirements, witness identities, callable contracts, captured configuration, and definition material or precompiled-instance catalogue needed for its admitted uses. Consumers shall check those uses from that published contract.

Instance identity shall use Chapter 10 plus Chapter 26's constructor and associated-binding components. Emitted code sharing shall preserve Chapter 21's selected observations. Foreign boundaries shall use the verified wrappers or provider bindings in Chapters 09 and 20; compile-time constructor and witness identities shall remain compile-time entities.

An interface depending on private associated material SHALL publish the necessary reachable contract or expose a public opaque adapter. Identity matching SHALL use the bound semantic contracts. Standardized external contract export SHALL apply Chapter 29's representation and fingerprint rules when that capability is selected.

## 11. Required boundary behavior

| Case | Required behavior |
| --- | --- |
| A known nominal instance exposes the formal constructor argument position | Deduce the stored canonical constructor identity and validate its kind. |
| An omitted, independently undeduced typefn parameter has a declared default | Bind that constructor expression under its captured environment. |
| A required constructor argument has no explicit binding, direct deduction, or declared default | Report the missing argument. |
| An inline mapping binds a defaulted family position | Apply the default captured by that mapping and retain its dependency identity. |
| A prefix application binds part of a higher-order signature | Produce and check the finite residual kind. |
| T is independently deduced as i8 and i16 | Require one canonical deduction and report the mismatch. |
| Symbolic `N > 0` and `N >= 1` are compared for ordering | Retain distinct atoms and a tied constraint rank unless other standard evidence orders the entries. |
| A well-formed concrete declared constraint is false | Remove that candidate before ranking. |
| A candidate requirement has invalid nondependent syntax | Report the Malformed outcome. |
| Two matching explicit entries have different priorities | Visit the higher tier first; select its unique established entry or continue after an all-False tier. |
| Several entries are established in the first successful priority tier | Report ambiguity at the requiring use. |
| A higher tier succeeds while a lower dependent recipe would fail | Retain the selected witness and leave that lower dependent recipe unvisited. |
| A visited tier contains one Established and one Unestablished entry | Report the required-proof failure for that tier. |
| A visited condition reaches an Unestablished predicate and a lower tier has an applicable entry | Report the required-proof failure at the visited tier; retain the lower tier as unvisited. |
| An established False left operand guards a dependent predicate in a conjunction | Complete that condition as False through short-circuit evaluation, retaining the ordinary nondependent legality checks. |
| An established True left operand reaches an Unestablished predicate in a conjunction | Report the reached required-proof failure. |
| Every head-matching explicit entry is False and structural requirements hold | Select the structural fallback and produce GEN001. |
| No explicit head matches and structural requirements hold | Select the ordinary structural witness. |
| A cached structural witness carries all-False explicit provenance | Apply GEN001 under the current diagnostic configuration. |
| A selected body or association is invalid | Report the selected definition's error. |
| A required witness depends on its own unresolved selection | Apply the dependency-cycle rule. |
| Required solver resources are exhausted | Report the distinct compilation-resource outcome. |
| The caller imports another helper or conformance catalogue | Retain the generic definition's captured binding environment. |
| Optional analysis leaves an ordinary raw-pointer obligation unknown | Apply Chapter 24's ANOMALY policy while retaining required generic evidence. |
| A selected instance requires an unavailable format or ABI | Report its required capability. |

### 11.1 Library author guidance: conditions with insufficient evidence

This subsection is informative. Sections 3 and 6.1 define the proof outcomes and selection transitions illustrated here. `P<T>`, `Q<T>`, and `Gate<T>` below are explanatory notation for already bound library requirements and their checking results. The tables illustrate the checker at the semantic level.

Consider a concrete subject S whose owner catalogue contains the following head-matching entries. All nondependent declaration checks have succeeded:

| Priority | Entry | Result of checking its condition and required contract at S |
| ---: | --- | --- |
| 20 | A, using `P<S>` | Established. |
| 20 | B, using `Q<S>` | Unestablished: a required proposition lacks supporting evidence in its bound domain. |
| 0 | C | Would be Established if visited. |

Selection reaches priority 20 and reports B's required-proof failure. A's established condition does not complete the tier: the evidence has not established whether B is an applicable competitor. Entry C and structural fallback remain unvisited. A library author who intends C to handle an unsupported case needs the higher tier to reach established False outcomes for that case. The presence of C supplies an alternative implementation; its availability supplies no proof about B.

A concrete type argument fixes type identity while a required proposition may still depend on the declared evidence for a callable, associated projection, or generic domain. For example, an algorithm may require a closed callable effect or returned-borrow contract while its available callback interface exposes only an opaque or open bound. Section 8 requires a supporting declared contract, established proof, or conforming adapter for the stronger requirement. Merely obtaining the callback's ordinary parameter and result types supplies that ordinary signature. A rule establishing an incompatible structural contract produces False; the trace above specifically assumes an insufficient-evidence outcome under Section 3. These cases retain their separate classifications.

A useful condition shape is a decidable eligibility gate followed by the proof that the eligible branch needs. For the schematic condition `Gate<T> && Q<T>`, the existing short-circuit rules give:

| Checking at S | Condition result and consequence |
| --- | --- |
| `Gate<S>` is established False | `Q<S>`'s dependent checking remains unvisited; the condition is False. Other entries in the tier still determine that tier's result. |
| `Gate<S>` is established True and `Q<S>` is Established | The condition succeeds; the remaining association and structural requirements are checked. |
| `Gate<S>` is established True and `Q<S>` is Unestablished | The reached proof fails and the visited tier reports ERROR. |

If replacing B's condition by the guarded form makes B False, A becomes the unique established entry in priority 20. If every head-matching entry in that tier becomes False, selection continues to priority 0. A gate such as a declared constant capability flag or a concrete core type predicate can delimit the intended domain. The gate itself needs an established result, and skipped dependent checking still preserves parsing and nondependent declaration legality.

Library authors can make these boundaries reviewable by documenting the supported subject domain and the source of each required fact. A callable's declared effect and lifetime contract can provide interface evidence; an adapter can expose the stronger contract that its implementation actually undertakes. Generic value-operation bodies establish their admitted domain at definition checking, with `if constexpr` supplying the branch refinement defined by Chapter 10. Those definition obligations precede concrete witness selection where applicable.

Review conditions using separate cases for supported input, established ineligibility, insufficient evidence, and exhausted compilation resources. A missing or incompatible structural operation has the False outcome defined in Section 3. An ordinary runtime-only Boolean call used where constant evaluation is required produces a required-evaluation error. Resource exhaustion retains its resource diagnostic. Each outcome keeps its defined classification, including the required-proof failure of an Unestablished proposition. The proof obligation applies to reached conditions and dependencies in visited tiers; lower tiers after a successful selection and short-circuited dependent branches keep their prescribed unvisited status.

## 12. Conformance requirements

An enabled implementation shall accept well-formed programs within its published capabilities and resource limits, produce deterministic candidate and witness selections, preserve required declaration evidence, and report ambiguity, malformed requirements, cycles, and resource exhaustion distinctly. The resulting native instances shall satisfy the same selected numeric, lifecycle, concurrency, effect, and ABI contracts as ordinary declarations.

