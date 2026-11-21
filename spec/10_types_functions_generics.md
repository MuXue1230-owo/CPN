<a id="chapter-10-types-functions-generics"></a>

# CXXN Types, Functions, and Generics Specification

## 1. Type identity and declarations

A type shall determine its admissible values, operations, qualification, and representation contract. A typed access shall separately satisfy the storage, live-object, and authority requirements in Chapters 06 and 12. This chapter owns ordinary type and declaration identity, value categories, lookup, and conversion ranks; Chapter 27 owns generic deduction and candidate selection.

Native scalar types, named records, enumerations, and tagged unions shall have nominal identity. A nominal identity SHALL include its owning compilation scope, declaration identity, generic arguments when present, and relevant representation contract. With the module capability selected, the canonical module SHALL supply that owning scope; a Core compilation SHALL use its root-unit scope under Chapter 11. Anonymous closure identities shall additionally identify their lexical expression and enclosing specialization. Independently declared nominal types shall remain distinct even when their layouts match. Public identity SHALL use canonical declarations under the selected compilation contract.

An alias introduces another spelling of the same type:

```text
alias Count = usize;
alias ReadOnlyBytes = const<byte>*;
alias SmallVector = std::collections::Vector<i32>;
```

An alias shall preserve the aliased type's constructor set, overload identity, numerical policies, and ABI identity. A distinct domain type shall use a named record or enumeration. Alias expansion shall terminate at a valid type identity; an alias to an incomplete record is permitted, with layout-dependent operations waiting for its complete definition.

The type grammar shall admit qualified names, generic applications, `const<T>`, `T*`, `T&`, `T&&`, `T[N]`, and `function<R(P1, P2)>`. Type constructors shall compose in written order, with parentheses available for grouping. A declaration shall place its name after the complete type under Chapter 15.

```text
i32[4] samples(1, 2, 3, 4);
function<i32(i32)>* transform(&increment);
const<byte>* data(pointer_to_bytes);
```

An object declaration shall use `Type name(arguments);`, with empty or omitted arguments selecting a viable default. Metadata bindings, aliases, enumerators, and definition controls shall use their separate productions in Chapter 15.

`auto name(expression);` shall deduce a value type from one initializer by removing its reference category and top-level const view while preserving nested qualification, nominal identity, array extent, and numerical family. Array const normalization follows Section 2. Constructing from an lvalue shall require viable copying. A borrowing declaration shall explicitly name its reference type. Numeric literals shall materialize under Chapter 07.

## 2. Qualification and constant values

`const<T>` shall provide a read-only view of T with idempotent qualification and T's representation. Through that view, member access shall preserve const qualification for nonstatic subobjects and select const-qualified receiver operations. Stored pointers shall retain their separately declared pointee permissions. Other aliases and concurrent access shall follow the independent memory and synchronization contracts.

A leading declaration qualifier `const` shall qualify the object's outermost type. For a reference, whose binding is already fixed, it shall qualify the referent. The normalization shall be:

| Declaration | Required interpretation |
|---|---|
| `const i32 value(1);` | Immutable i32 object. |
| `const i32* p(address);` | Immutable pointer object referring to mutable i32. |
| `const<i32>* p(address);` | Mutable pointer object referring through a const i32 view. |
| `const const<i32>* p(address);` | Immutable pointer object and const pointee view. |
| `const i32& r(value);` | Same reference type as `const<i32>&`. |
| `const<i32>& r(value);` | Non-rebindable reference with a const referent view. |

The native const forms shall be those in the table and the `const<T>` type constructor. A member function's trailing const shall qualify its receiver. `catch (const T& value)` shall bind a reference to a const primary-payload view.

Array qualification shall normalize `const<T[N]>` to `const<T>[N]`; reference qualification shall normalize to the const-referent reference. A function type shall express its receiver and nonthrowing contracts through their dedicated forms. By-value top-level const shall restrict the local parameter object and be removed from the canonical caller-facing parameter type. Thus `f(i32)` and `f(const i32)` shall redeclare the same overload. Pointee and reference-referent qualifications shall remain part of the function type.

A qualification conversion shall preserve pointer/reference validity and may add the admitted const view. Removing a view shall require the explicit memory operation and its original-object authority; mutation shall require an originally mutable object. Multilevel pointer qualification shall preserve writable intermediate slots: conversion from `T**` to `const<T>**` fails this requirement.

`constexpr` shall require successful constant evaluation of the initializer and declare the object const. The property shall preserve the ordinary type identity. A constexpr reference shall satisfy constant-address and runtime-lifetime requirements. A constexpr pointer may designate permitted static storage while retaining its separately declared pointee qualification.

## 3. Nonnumeric values and arrays

`bool` shall have exactly false and true and default to false. On standard eight-bit-byte native profiles, its size and alignment shall be one byte, with canonical encodings zero and one. Representation import shall validate other patterns. Conditions shall require bool; other types shall supply an explicit comparison, predicate, or named conversion whose contract admits them.

On eight-bit addressable-storage core targets, `byte` shall alias u8 and require that representation capability. A target with another addressable-unit model shall publish its representation contract. Byte arithmetic shall use ordinary u8 policy, and object-representation access shall follow Chapter 12.

`char` shall denote one Unicode scalar in zero through `0x10FFFF`, excluding `0xD800` through `0xDFFF`, and default to U+0000. Its native encoding shall be the 32-bit unsigned scalar value with the target's declared alignment and byte order. Character equality shall compare scalar values. Integer reconstruction, locale operations, normalization, case folding, and grapheme operations shall use their explicit interfaces; foreign `ffi::c_char` shall retain its distinct provider type.

A character literal shall contain exactly one scalar after escape processing, for example `'A'`, `'\n'`, or `'\u{1F642}'`. A braced Unicode escape shall contain one through six hexadecimal digits denoting a scalar. Ordinary escapes shall include backslash, single quote, double quote, `n`, `r`, `t`, and `0`. Invalid escapes or source encoding shall fail lexical validation.

A string literal with N UTF-8 content bytes shall denote a static `const<byte>[N + 1]` array containing those bytes and a final zero. Embedded zero bytes shall remain content. A text-view constructor may select the N content bytes; an ordinary array view may include the terminator. Pointer extraction, String construction, concatenation, foreign encoding, and foreign null-termination shall use explicit operations. Neighboring literal tokens shall remain separate tokens under the grammar.

`void` shall denote absence of a result and be admitted as a function result or by a facility expressly providing an absent-payload specialization, such as Result. Object, element, member, and ordinary parameter declarations shall require an object or reference type as appropriate. A zero-parameter function shall write `()`. `std::Unit` shall provide an ordinary inhabited unit value.

`nullptr` shall have the distinct single-value type nullptr_t. It shall convert to a null object or function pointer using the target representation and compare with a compatible pointer as a value operation. Integer zero and bool remain governed by their own conversions. `auto value(nullptr);` shall retain nullptr_t. A nullptr_t object shall default to its sole value and use native one-byte canonical zero storage; foreign nullptr types shall use their provider ABI.

`never` shall identify a computation with no normal completion and have an empty value domain. Its function body shall terminate every reachable path through divergence or a declared failure/terminal outlet. A never expression may terminate a value-producing path. The selected outlet shall determine cleanup under Chapter 28.

An array `T[N]` shall contain N contiguous element slots, with a required nonnegative usize extent and complete object element type T. Extent zero shall create an empty array whose physical size and address identity follow the object-layout contract. Element access shall still require a valid index. Foreign zero-extent representation shall require provider support.

Array arguments shall initialize corresponding elements once in increasing index order. Omitted trailing elements shall use typed defaults; excess arguments shall fail arity checking. Array expressions, calls, returns, and deduction shall preserve the array type. By-value passage shall construct the complete array; explicit pointer or view operations shall provide those alternative representations. Available copy, move, and assignment operations shall operate elementwise under Chapter 06's construction, partial-failure, and reverse-destruction rules.

### 3.1 Explicit scalar-domain conversions

The minimal std module shall export the following nonallocating scalar conversions. S denotes bool, char, or a complete closed native enumeration; I denotes an enabled fixed-width or platform-width integer. Foreign scalars and allocating integer families shall first use their explicitly selected integer conversion. These interfaces preserve each scalar's distinct arithmetic type and ordinary conversion ranks.

| Interface | Result and contract |
| --- | --- |
| `std::to_underlying(S value)` | bool returns u8 zero or one; char returns its scalar value as u32; an enumeration returns its declared underlying integer type with its enumerator value. |
| `std::try_from_underlying<S>(I value)` | `std::Result<S, std::ScalarError>`; succeeds exactly when the source mathematical integer belongs to S's admitted value set. |
| `std::from_underlying<S>(I value)` | S on the same success predicate; otherwise Contract Trap. No language exception or fabricated scalar is produced. |

`ScalarError` is an allocation-free tagged value with payloadless cases `InvalidBoolean`, `InvalidScalar`, and `UndeclaredEnumerator`. Boolean reconstruction admits exactly zero and one. Character reconstruction admits exactly zero through `0x10FFFF` excluding `0xD800` through `0xDFFF`. Enumeration reconstruction admits exactly its declared enumerator values. Each failing target family selects its corresponding error; an out-of-range integer for an enumeration is still `UndeclaredEnumerator`, without a preceding truncation or conversion failure.

Reconstruction shall compare the exact mathematical source integer with the destination's admitted set before representation conversion. An abstract integer expression shall retain its exact value for that validation. Typed integer sources shall retain their mathematical value and sign. Other source categories shall first use an explicitly selected integer conversion.

Each conversion shall evaluate its argument once, be nonthrowing, and be admitted in constant evaluation. Its own effects shall consist of its returned value or the value form's ContractTrap outlet; argument-expression effects remain separate. The result type capability shall be available at use: to_underlying for bool requires u8, and for char requires u32. A typed source shall already satisfy its object-representation validity contract.

A well-formed try_from_underlying may return Err during ordinary or constant evaluation. The value form shall use Chapter 28's ContractTrap outlet on validation failure, and required evaluation reaching that outlet shall fail. A statically established runtime value-form failure shall use Chapter 08's ANOMALY policy unless another mandatory-error rule applies. Required type arguments and capabilities shall satisfy ordinary validity checks.

Direct scalar construction shall use a same-type value or its admitted explicit conversion. For example, `bool ready(std::from_underlying<bool>(u8(1)));` shall perform the stated validation. Any wrapping, saturating, or other scalar projection shall require an operation that expressly defines that destination domain.

## 4. Records, members, and inheritance

`struct` and `class` shall declare nominal records with the same layout and lifecycle facilities. Struct shall default to public member access and class to private. Access labels shall control following declarations while preserving their declaration order and destruction responsibility. Static members shall be separate objects.

```text
struct Point {
    i32 x;
    i32 y;
    Point(const<Point>& source) = default;
    Point(Point&& source) = default;
};

class Counter {
    i32 value;
public:
    Counter(i32 initial) { init value(initial); }
    Counter(Counter&& source) = default;
    Counter& operator=(Counter&& source) = default;
    i32 read() const { return this->value; }
    void advance() { this->value += 1; }
};
```

An in-class member initializer shall use the member declaration's parentheses. Chapter 06 shall determine its source-bound producer, execution order, delegation, and construction-tail behavior.

A native base list shall contain comma-separated types, each optionally prefixed virtual, as in `class Derived : Base, virtual Root`. These base relationships shall be public; member visibility shall follow its separate declaration. Foreign bases shall retain the verified provider access contract. Repeated or ambiguous paths shall use the required explicit base selector.

Virtual dispatch shall require a virtual member declaration. An ordinary override of an inherited virtual slot shall carry override and match the slot's parameter and return types, calling convention, receiver qualification, and required effects. It may strengthen nonthrowing guarantees. An inherited virtual destructor shall remain virtual for implicit and user-declared derived destructors; an optional override marker shall be validated. A final virtual override shall close its slot to further overrides, and a final class shall close derivation.

A nonstatic member function shall receive a this pointer of type C* or, for a const receiver, `const<C>*`, subject to the active construction/destruction layer. Trailing & and && shall restrict receiver category as below. Named parameters and receivers shall be lvalue expressions in the body. Static members shall use their ordinary explicit arguments. Qualified calls and virtual destruction shall follow Chapters 06 and 20.

Receiver & shall admit lvalues; && shall admit xvalues and prvalues; an omitted receiver-category suffix shall admit both. Constness and category shall participate in overload identity. For otherwise identical parameter types and receiver constness, & and && overloads may coexist; an unqualified-category overload shall occupy both categories and conflict with either. Exact mutable receiver binding shall outrank added const qualification. Category binding shall preserve the object's lifetime and move state. Receiver suffixes shall apply only to nonstatic members.

Value equality, ordering, serialization, copying, and ownership interpretation shall use their explicit declarations or library contracts. An exported representation shall publish the relevant member/base layout, qualification, and special-operation contracts in its ABI material.

## 5. Enumerations and tagged unions

An enumeration declares an explicit underlying enabled integer type and explicit enumerator values:

```text
enum State : u8 {
    case Idle(0),
    case Running(1),
    case Finished(2)
};
State state(State::Idle);
```

Enumerator values shall be distinct representable required constants and their names shall belong to the enum scope. A closed native enum shall admit exactly those values and have a default exactly when one enumerator has value zero. Equality and inequality shall require the same enum type. Ordering, arithmetic, bit masks, and integer conversion shall use explicit named operations. Checked representation import shall validate the admitted set. Foreign open enums and bit-mask domains shall use their declared provider or library types.

Native `union` is always discriminated:

```text
union Reading {
    default case Missing;
    case Sample(i32 value, State state);
};
Reading reading(Reading::Sample(42, State::Finished));
```

Each union case shall have a distinct identity and zero or more named payload fields. A default case, when present, shall be unique and have default-constructible payload. Default union construction shall require that case. `U::Case(arguments)` shall construct U with the selected payload in ordinary argument and field order, then commit its discriminant after all fields complete. Construction failure shall follow Chapter 06's partial-object rollback.

Typed payload access shall establish the active case through a match, checked projection, or static case proof. Raw overlays and imported C unions shall follow their separate memory and foreign contracts. The public representation descriptor shall fix discriminant and payload layout. A selected niche representation shall preserve all cases and required layout observations.

Chapter 12 shall define exhaustive match execution. A `ref name` payload binding shall borrow the selected field and preserve its const view; `value name` shall copy it; `move name` shall require an expiring matched operand and move-construct the binding. `match (std::move(value))` shall permit those explicit move bindings. Other payloads and each moved-from field shall retain their operation-defined state and active discriminant.

The payload pattern `_` shall leave that field unbound while preserving its lifetime, ownership, and later destruction. Each payload position shall have a binding or underscore. The whole-arm wildcard `case _` shall follow Chapter 12's separate exhaustive-match rule.

A supplied or explicitly defaulted union copy/move constructor shall construct only the active case and require its operation for every admitted alternative. A declared assignment or emplacement operation shall state active-case replacement and construction/destruction failure postconditions. Explicit reconstruction may leave inactive storage after failure under Chapter 12. A library promising strong replacement shall supply the required preparation storage and nonthrowing commit contract.

## 6. Value categories and special operations

An lvalue shall designate an existing nonexpiring object; an xvalue shall designate an existing object explicitly offered for moving; a prvalue shall supply a value or direct-construction result. Reference types shall describe bindings, and expression categories shall describe their uses. Parentheses shall preserve category. Named objects and named reference parameters shall be lvalues.

`std::move(x)` shall evaluate x once and yield an xvalue preserving its type and qualification. The subsequently selected operation shall determine ownership transfer and source postconditions. Successful moving shall leave a live source supporting destruction and its expressly permitted moved-from operations. BigInt shall retain its specific zero-after-move and self-move contracts.

Copy and move constructors shall use `T(const<T>&)` and `T(T&&)`; assignment shall use `T& operator=(const<T>&)` and `T& operator=(T&&)`. A named class shall explicitly declare each selected operation with a body, `= default;`, or `= delete;`. These declarations shall independently control operation availability, including when a destructor is declared.

Defaulted copy/move construction shall visit bases and members in canonical construction order. Defaulted assignment shall update their live values in that order with the corresponding assignment operation and its stated failure guarantee. An unavailable member operation shall make the defaulted declaration unavailable with a requirement diagnostic. Known incompatible ownership policies shall fail memberwise-generation validation. A raw-pointer copy shall copy its pointer value; pointee ownership shall remain independently governed.

Scalars, arrays, provider-defined standard values, and closures shall have their specified category operations. Their numerical and resource copy/move policies shall remain binding.

A same-type prvalue shall construct directly in the final destination, including a value parameter or returned result. An lvalue shall require viable copying; an xvalue shall require viable moving. A class conversion from another type shall use an explicitly selected constructor. Ordinary implicit conversion shall use only its admitted conversion ranks.

`return local;` shall use the local's lvalue category and copying requirement. `return std::move(local);` shall request moving. A matching prvalue return shall construct the caller's result directly. Machine-work elimination shall preserve Chapter 21's selected constructor, destructor, and move observations.

## 7. Function declarations, calls, and effects

Native functions use:

```text
declare i32 add(i32 left, i32 right);
i32 add(i32 left, i32 right) { return left + right; }

declare void inspect(const<Counter>& object) noexcept;
void reset(Counter& object) { object = Counter(0); }
```

An ordinary-context function declaration SHALL order its optional declare marker, selected constexpr/consteval/async mode, applicable static/virtual modifiers, return type, name, parameters, receiver qualifiers, noexcept, and override/final suffixes under Chapter 15. An external-linkage context SHALL use that chapter's dedicated foreign declaration grammar. A declare form shall end with a semicolon; a definition shall provide its body or an admitted special-operation definition control. Async, constexpr, and consteval shall be distinct declaration modes. Static and virtual shall be mutually exclusive. Constructors and destructors shall use their dedicated forms.

The [consolidated grammar](15_grammar_binding.md#chapter-15-grammar-binding) shall govern export/configuration wrappers, leading attributes, and generic prefixes. Effect attributes may also follow the receiver/noexcept suffix before override/final; all applicable attributes shall form one consistent contract. A qualified separate definition shall select an existing same-owner declaration and match its signature, receiver, nonthrowing, async, effects, and ABI contracts. Member static/virtual and override/final selections shall reside in the class declaration. Body-private numerical policies shall bind at the definition or operation under Chapter 08.

The reset example SHALL use Counter's declared move assignment. A function definition SHALL have an explicit return type. An ordinary-context forward declaration SHALL carry declare. Under external linkage, `extern "C" R function();` SHALL declare a function, `extern "C" T object;` SHALL declare an external object, and `extern "C" define T object(arguments);` SHALL define that object. Parameters SHALL use type-before-name syntax; a used parameter SHALL have a name. Native calls SHALL be positional.

A value parameter shall construct an independent T. A T& parameter shall bind a permitted lvalue; `const<T>&` shall bind a read-only borrow; T&& shall bind an expiring object. Call-bound temporaries shall live through their enclosing full expression. Reference, bounds, aliasing, and escape validity shall follow Chapter 12 and Chapter 25.

A parameter default shall use parentheses, as in `declare i32 scale(i32 value, i32 factor(2));`. Defaults shall form a trailing suffix owned by one canonical declaration. A missing argument shall evaluate its bound default in parameter order after supplied arguments. The default may access completed earlier parameters. Defaults shall belong to the declaration's captured environment; the runtime function-pointer type and overload ranks shall use parameter types and contracts independently.

Synchronous calls shall execute the phase sequence in [Chapter 25](25_effect_composition_and_boundaries.md#chapter-25-effect-composition-boundaries), including left-to-right argument and parameter initialization, prepared return construction, required local and parameter retirement, and result publication. Async calls shall use that chapter's frame-admission phase before remaining argument evaluation. Each failure shall follow its selected Chapter 28 outlet and associated cleanup behavior.

Void fallthrough shall complete as `return;`. Other ordinarily returning functions shall produce their declared result on every normally completing path. `return expression;` shall satisfy the declared binding contract, after the expression has its own established type and numerical semantics. A Result return shall publish that value with its selected case.

`noexcept` shall bound escaping language exceptions under Chapter 24. Its validation and boundary behavior shall follow Chapters 24 and 28. Other terminal, allocation, Whole, borrowing, and suspension effects shall remain separately expressed in the callable contract.

Parameter escape, returned-borrow, retention, and consumption attributes shall use Chapter 25's declaration table. `requires_initialized` and `initializes` shall bind Chapter 06's construction-state summaries; `lifecycle_effect(whole)` shall expose Whole propagation. Indirect callable types shall preserve each required contract by canonical parameter position.

[Chapter 24](24_contracts_and_effects.md#chapter-24-contracts-effects) shall define contract predicates, effect vocabulary, bound validation, and analysis modes. Chapter 25 shall define composition, substitution, and async admission/execution deltas. Omitted effect bounds shall be conservative; explicit bounds shall remain interface obligations independently of optional analysis depth.

A function type shall record result and parameter types, linkage/calling convention, nonthrowing guarantee, and required lifecycle or suspension effects. It shall exclude parameter spelling and defaults from identity. `function<R(P...) noexcept>*` shall denote a nonthrowing function pointer. Conversion to an otherwise identical potentially throwing pointer shall be permitted; reverse conversion shall require an explicit compatible contract. The selected ABI shall determine each callable representation and argument/result lowering.

An effect-bearing function type may name parameters to bind attributes, for example `function<void(Widget* p) [[noescape(p), lifecycle_effect(whole)]]>`. Those names shall normalize to parameter positions; the type shall contain parameter types and contracts without argument defaults. A preceding noexcept shall preserve its guarantee. `decltype` of a function or its pointer shall preserve the same contract.

An overload address shall require a unique compatible declaration under an explicit target function-pointer contract. This operation shall select its signature and required effects without executing the function. An unconstrained auto initializer or object-pointer destination shall fail the required-target check.

An async T declaration shall have the Task<T> call result, T body result, required Context parameter, and phase-aware `function<async T(Parameters...)>` type specified by concurrency. Its address shall preserve that type and admission contract. An ordinary synchronous wrapper returning Task<T> shall instead use ordinary synchronous argument evaluation. Await and returned outcomes shall follow their explicit concurrency interfaces.

## 8. Overload selection and operators

An overload set shall contain the declarations visible at its lexical or qualified name. Ordinary parameter and receiver signatures shall distinguish overloads, with explicit generic parameters and constraints providing the generic distinctions in Section 12. Declarations differing only in result type, parameter spelling, defaults, noexcept, effects, or diagnostic policy shall require a compatible redeclaration contract.

Candidate formation, generic deduction, requirement outcomes, tie-breaking, and selected-body validation shall follow [Chapter 27](27_constraint_solver_and_inference.md#chapter-27-constraint-solver-inference). This section defines the conversion ranks used by that procedure.

Conversion ranks, from best to worst, shall be: exact type/category binding; admitted qualification addition, nullptr-to-pointer conversion, or accessible unambiguous base-reference/base-pointer conversion; then admitted lossless numeric conversion. Null conversions to distinct pointer targets shall tie. By-value extraction shall remove only top-level const and preserve pointee qualification and copy/move requirements. Within qualification rank, fewer independent qualification additions shall be better; base-path length shall leave rank unchanged. Distinct admissible numeric targets shall tie unless one exactly matches the source type.

A same-type value parameter shall separately satisfy its copy/move requirement while retaining the exact conversion rank. Otherwise exact by-value and reference overloads shall tie. The admitted ranks shall exclude user-defined constructor search, array decay, pointer truth conversion, and representation reinterpretation.

An untyped numeric expression shall bind independently against each concrete candidate under Chapter 07. A failed binding shall make that candidate nonviable. Among otherwise tied literal bindings, an exact match to the resolved default literal type shall be preferred; other admitted targets shall tie. Thus i8 and u8 overloads tie for abstract 7, while an added i32 overload selects the standard default. Explicit `i8(7)` supplies a typed argument. Typed constant conversions shall use mandatory language evaluation rather than optional optimizer inference.

Section 4 of Chapter 27 shall govern literal contexts during generic deduction. Selected argument evaluation and materialization shall then occur once under Chapter 25's call phases.

An explicit conversion or constructor shall resolve at its source expression. The enclosing call shall independently satisfy its admitted binding conversions. Numeric-family boundaries, comparison rules, and foreign nominal identities shall use their owning numeric and ABI contracts.

A user operator shall have at least one operand of its declaring nominal record or union type and participate in ordinary signature/effect resolution. Built-in numeric operations shall retain their core meaning. The admitted operator set shall leave &&, ||, ?:, assignment sequencing, pointer formation/indirection, and Whole control under their core evaluation rules; Chapter 15 defines its exact declaration forms. Conversions shall use named functions or explicit construction.

A nonstatic member operator's receiver shall count as one operand. Assignment, compound assignment, call, and indexing shall be nonstatic members; indexing shall have one explicit index. Increment/decrement shall declare `operator prefix ++`, `operator postfix ++`, or the corresponding -- form. Each shall use one writable nominal lvalue through a nonconst receiver with zero explicit parameters or one T& nonmember parameter. Prefix shall return updated T&; postfix shall explicitly construct its pre-update T result with the declared failure guarantee. Ordinary source uses remain ++object and object++. Qualified operator designators shall use ordinary lookup and address/call rules. Arrow access shall use the core pointer operation.

## 9. Closures

A lambda has explicit captures and a C-like function body:

```text
auto predicate([limit] bool(i32 value) { return value < limit; });
auto increment([&counter] void() { counter += 1; });
auto operation([owner(std::move(owner))] void() mutable {
    owner.run();
});
```

A lambda shall use `[capture-list] [async] ReturnType(parameters) [mutable] [noexcept] { body }`. An async lambda shall have the concurrency-required Context and result transformation. Each explicit capture shall be name for copying, &name for borrowing, or name(expression) for direct value construction. Initializers shall resolve outer bindings and execute once from left to right; capture fields shall construct in that order and retire in reverse. Failure shall use the selected partial-construction outlet.

A closure shall be an ordinary unnamed object containing its capture fields. Copy and move availability shall derive from those fields' operations. A move-only field shall make the closure noncopyable. Borrow captures shall preserve their source lifetime and alias permissions. Explicit callable views or owning adapters shall provide any requested erased representation and its resource contract under Chapter 21.

An async closure call shall copy or move its concrete closure into the provisioned task frame according to expression category. An owned frame requiring a move-only closure shall receive an expiring closure. Borrowed capture referents shall retain their original lifetime obligations. Frame admission and creation failure shall follow Chapter 25 and the concurrency contract.

The closure body shall have a const receiver unless mutable is present. Stored pointers and references shall preserve their referent permissions. Moving an owned capture shall require a receiver and operation that permit that move.

An explicit this capture shall borrow the pointer; `[self(*this)]` shall construct an owned value capture of the enclosing object. Escaping borrowed captures shall satisfy their declared source lifetime and retention obligations. Known invalid accesses and unknown ordinary obligations shall follow Chapters 12 and 24.

A captureless closure may explicitly initialize a compatible native function pointer retaining its definition policies and effects. Capturing closures shall use their concrete type, an explicit borrowing callable view, or a provisioned owning adapter. Foreign callbacks shall additionally satisfy the selected linkage and provider contract.

## 10. Constant evaluation

A constexpr function shall be eligible for required evaluation when its selected invocation meets the constant-evaluation contract; ordinary runtime calls shall execute as ordinary functions. A consteval function shall execute only during compilation and require compile-time arguments. Its callable identity shall belong to the compile-time environment.

Required evaluation shall cover constexpr initializers, array extents, admitted generic value arguments, enumerator values, and declared constraint predicates. It shall use target domains and selected numerical policies. Typed operations shall retain their policy-defined boundaries; abstract expressions shall use Chapter 07's pre-materialization rules.

The constant evaluator shall admit supported local computations, loops, calls, and bounded temporary objects within its declared target environment. External I/O, host-environment access, runtime-storage mutation, volatile access, thread creation, and undeclared foreign execution shall lie outside that environment. Symbolic static-object and function references shall retain target identities. A selected constant-allocation provider shall bound evaluation storage and require all published constants to be independent of evaluation-temporary addresses.

Required evaluation shall finish through a result admitted by its requiring context. Reaching a terminal failure or inadmissible operation shall fail evaluation; a Result error shall remain an ordinary value when that context admits it. Reflection handles and typed syntax shall follow [Chapters 22](22_static_reflection.md#chapter-22-static-reflection) and [23](23_compile_time_generation.md#chapter-23-compile-time-generation). A helper may return typed declarations; the enclosing generation or derivation transaction shall control their submission and commit. Compile-time resource exhaustion shall produce Chapter 27's distinct resource outcome.

Chapter 04 shall define required-context numerical events, operation-local reports, and isolated compile-time status. Required evaluation shall preserve those selected observations and publish only the resulting admitted constant.

Runtime folding shall preserve the selected observations and transformation permissions in Chapter 21. Required-evaluation contexts shall remain those designated by source and language rules. Statically discovered ordinary runtime failure shall use Chapter 08's diagnostic policy unless a mandatory validity rule applies.

## 11. Generic parameter binding

A generic declaration has an explicit prefix and optional constraint:

```text
generic<type T, const usize N>
requires (ObjectType<T> && CompleteType<T> && N > 0)
struct Buffer {
    T[N] elements;
};

generic<type T>
requires (Addable<T>)
T add_values(const<T>& left, const<T>& right) {
    return left + right;
}
```

`type` shall declare an ordinary type parameter. `const Type Name` shall declare a compile-time constant parameter of bool, char, a native enumeration, or an enabled fixed/platform-width integer. The canonical parameter identity shall use its admitted value and declared type. Higher-order kinds shall follow Chapter 26.

Generic defaults SHALL use metadata binding syntax, for example `type T = i32`, `const usize N = 4`, or `typefn F<type> = Box`, and refer to preceding parameters or definition-site names. Constructor expressions and partial application SHALL follow Chapter 26. Every required position shall receive an explicit argument or admitted deduction/default. `Buffer<i32, 16>` and `add_values<i32>(left, right)` shall apply explicit arguments. Aliases shall preserve underlying identity, and equal admitted constants of one parameter type shall have equal argument identity.

Generic deduction shall follow Chapter 27. An incomplete imported type may bind as an identity; any operation requiring its definition shall obtain a complete reachable contract.

`forward T value` shall declare a category-preserving borrowing parameter for a generic function. Chapter 27 shall deduce T from the source category. `std::forward<T>(value)` shall restore its lvalue or xvalue category while preserving qualification, lifetime, and ownership. The named parameter shall be an lvalue in the body. A prvalue forwarding borrow shall materialize for the enclosing full expression. Ordinary T&& shall retain its expiring-reference contract; other nested-reference forms shall satisfy the type grammar.

A generic parameter list may end in one type, admitted constant, or constructor pack, using `type... Ts`, `const Type... Ns`, or `typefn... Fs<kind-list>`. The constructor form SHALL follow Chapter 26. `Ts... values` SHALL expand to ordered typed runtime parameters, with an explicit reference or forwarding modifier when selected. A list-position pattern followed by `...` SHALL expand its unexpanded pack bindings in order; packs expanded together SHALL have compatible lengths. An empty pack SHALL supply an empty sequence. C variadics SHALL retain their separate foreign ABI contract.

## 12. Constraints and definition checking

A constraint declares structural and constant requirements:

```text
constraint Addable<type T> {
    expression (const<T>& a, const<T>& b) {
        a + b -> T;
    }
};

constraint SizedElements<type T> {
    type T::Element;
    expression (const<T>& value) {
        value.size() -> usize noexcept;
    }
};
```

Constraint parameters shall use the generic parameter grammar. `type T::Name;` shall require an accessible nested type identity. An expression requirement shall bind symbolic parameters and establish each expression's exact result type and category: a value type requires a prvalue, T& an lvalue, and T&& an xvalue. Optional noexcept shall require a nonthrowing expression contract. These requirements shall perform compile-time checking. Additional requires predicates shall compose Boolean and named constraints.

The final top-level -> before an expression requirement's semicolon shall separate its expression and required type, respecting nested parentheses, brackets, and generic delimiters. Earlier arrows shall remain pointer member access. Thus `pointer->read() -> i32;` shall require the i32 result of that member call.

`ObjectType<T>`, `CompleteType<T>`, `SameType<T,U>`, `CopyConstructible<T>`, `MoveConstructible<T>`, and the specified assignment/destruction predicates shall query their declared language relations. Chapter 27 shall distinguish a false structural requirement, unestablished symbolic evidence, malformed requirement, and resource exhaustion.

A generic body shall establish its dependent operations throughout its declared parameter domain, using structural requirements, applicable language rules, or explicit compile-time branch facts. Chapter 27 shall determine those required proofs independently of optional ordinary analysis depth.

`if constexpr (predicate)` shall select a compile-time branch. Both branches shall be parsed and bind nondependent names at definition. Dependent operations shall be checked under their corresponding branch facts; the selected branch shall supply runtime code and effects. A discarded dependent branch shall require only operations admitted by its guard, while retaining syntax and nondependent binding validity.

Nondependent names and overload sets SHALL bind at the definition site. Dependent lookup SHALL use declared associated entities, accessible substituted members, and structural-operation witnesses from constraints. Each dependent name's declared recursive kind SHALL govern parsing. The closed definition environment SHALL retain its known conformance catalogue identities and declared subject-owner selection recipes for symbolic subjects. An actual canonical type argument SHALL supply its published owner contract when that recipe is instantiated. Each required associated witness use SHALL apply Chapters 26 and 27's declared-priority selection and their structural-fallback provenance rules. Ordinary structural constraints SHALL retain their direct requirement checking independently of associated conformance capabilities.

A callable witness shall identify its selected declaration or intrinsic, canonical generic arguments, signature, receiver, effects, and bound policies. Required borrowing, nonthrowing, and Whole guarantees shall remain in that contract. Chapters 26 and 27 shall define associated witness identity and selection; Chapters 21 and 25 shall govern lowering and substitutability.

Constraint normalization, subsumption, candidate rejection, selected-body validation, and cycle handling shall use the single proof procedure in Chapter 27.

## 13. Explicit type specializations

An owning compilation scope may declare a type specialization explicitly:

```text
generic<type T, type E>
requires (ObjectType<T> && CompleteType<T> && ObjectType<E> && CompleteType<E>)
union Result {
    case Ok(T value);
    case Err(E error);
};

generic<type E>
requires (ObjectType<E> && CompleteType<E>)
specialize union Result<void, E> {
    case Ok;
    case Err(E error);
};
```

A specialization shall name its existing family and bind or fix arguments through its structural pattern. Each body shall be checked under its own constraints. A specialization may admit an argument such as void that the primary excludes. Dependent users shall rely on the selected contract or an expressly guaranteed family contract covering their domain.

The owning compilation scope SHALL retain one closed specialization catalogue and expose its semantic contract to admitted consumers. Chapter 27 shall select its unique best applicable entry, use the primary when applicable as the fallback, and validate the selected body.

Function customization shall use constrained overloads. Each type specialization shall publish its own representation and lifecycle contracts; foreign compatibility shall certify the selected instance.

## 14. Instantiation, policies, and emitted identity

Instantiation shall substitute canonical arguments, verify constraints and witnesses, resolve required layouts and constants, and check resource capabilities under the captured environment. The owning compilation scope SHALL provide its admitted consumers with sufficient definition material or a catalogue of supported precompiled instances. A Core compilation may retain that material internally; separately compiled consumers SHALL use the selected interface transport under Chapter 11. Reflection and generation dependencies shall include their captured metadata, generator identity, and provenance contracts.

Definition-site configuration shall bind numerical defaults, literal policies, providers, lifecycle effects, and other semantic behavior. Instantiation and inlining shall retain that environment. An explicit policy parameter shall affect only operations whose definitions use it.

```text
enum AddPolicy : u8 { case Checked(0), case Saturating(1) };
generic<const AddPolicy P>
i32 combine(i32 left, i32 right) {
    if constexpr (P == AddPolicy::Checked) {
        return checked_add(left, right);
    } else {
        return saturating_add(left, right);
    }
}
```

The example shall select the named checked or saturating operation. The caller's ordinary arithmetic policy shall leave that selection unchanged. A changed captured policy shall change the semantic definition contract and invalidate incompatible instance reuse.

Canonical instance identity shall include the owning generic declaration, selected specialization, bound arguments, selected witnesses, relevant definition contract, and ABI/provider requirements. Equivalent emissions shall denote one entity wherever function address or static-object identity is observed. Mergeable object emissions shall require matching identities, and generic statics shall receive one logical registration per canonical instance.

Code generation may specialize, inline, or share code under Chapter 21's observation-preserving rules. Explicit erased adapters shall publish their representation and resources. Foreign generic boundaries shall use the wrappers or selected verified C++ bindings in Chapter 09.

Required instantiation-depth, representation, and resource failures shall use Chapter 27's distinct outcomes and the capability/diagnostic policy in Chapter 08.

## 14.1 Higher-order generic extension

[Chapter 26](26_advanced_generic_families.md#chapter-26-advanced-generic-families) SHALL define recursive typefn kinds, constructor packs and defaults, partial and inline constructor expressions, associated projections, and structural or explicit witnesses as explicitly selected extensions to ordinary type and constant parameters. Ordinary generic types and functions, type and constant packs, and structural constraints SHALL remain available through Core. Chapter 08 SHALL own the advanced capability defaults and activation rules.

[Chapter 27](27_constraint_solver_and_inference.md#chapter-27-constraint-solver-inference) shall define the shared proof and selection procedure. Published generic identities and object lifetimes SHALL retain their owning compilation scope and lifecycle contracts.

## 15. Required boundary behavior

| Construct or situation | Required behavior |
|---|---|
| `const i32* p(address)` followed by reassignment of p | Error: the pointer object is immutable. Mutation of a permitted mutable pointee is a separate operation. |
| Conversion from `T**` to `const<T>**` | ERROR: the conversion requires an explicit admitted operation. |
| `auto copy(existing_owner)` for a move-only class | Error; use an explicit clone contract or `std::move` when ownership transfer is intended. |
| Passing an array to a pointer parameter | No implicit decay; obtain the required pointer/view explicitly. |
| `std::try_from_underlying<bool>(u8(2))` | Err(InvalidBoolean); the admitted Boolean set is zero and one. |
| `std::try_from_underlying<char>(u32(0xD800))` | Err(InvalidScalar); the admitted char domain excludes surrogate code points. |
| A closed enumeration declares values zero and two, then validates integer one | Err(UndeclaredEnumerator); matching the underlying storage range is insufficient. |
| `std::to_underlying` reads an invalid bool representation imported through unchecked bytes | The typed source read violates its representation precondition. |
| Local reference bound to a temporary, then used in the next full expression | Known dangling access is an error; the binding did not extend the temporary lifetime. |
| Passing a closure with borrowed stack state to a retaining API | The call shall satisfy its declared retention interval within the source stack lifetime. |
| Calling two overloads `f(i32)` and `f(i64)` with runtime i16 | Equal lossless-conversion ranks produce ambiguity. |
| `add_values` uses an operation absent from its stated constraints | Error in the generic definition unless another language rule or compile-time guard supplies the evidence. |
| A selected constrained overload contains a type error | Error; no substitution-failure fallback. |
| An importer adds an unrelated same-named helper | No change to an already bound generic definition or witness. |
| A void Result success | The selected explicit specialization has no payload object; no fabricated void value. |
| A C-compatible scalar function is emitted from a generic instance | Apply the verified wrapper and selected signature ABI. |

