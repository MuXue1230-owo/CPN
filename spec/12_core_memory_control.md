<a id="chapter-12-core-memory-control"></a>

# CXXN Source, Control Flow, and Memory Specification

## 1. Abstract execution and scope

This chapter defines source text, expression sequencing, ordinary control flow, storage, pointer access, and representation operations. The [type specification](10_types_functions_generics.md#chapter-10-types-functions-generics) defines type formation and overload selection. The [construction specification](06_construction_execution.md#chapter-06-construction-execution) governs the beginning and ending of object lifetimes. The [concurrency specification](13_concurrency_memory_model.md#chapter-13-concurrency-memory-model) governs interactions between execution agents.

The [core execution model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance) defines observations and transformation permissions. This chapter shall apply that model to source sequencing, storage, object generations, pointer representations, and release ownership. Each operation shall obtain access and release authority from its declared contract.

Standard native profiles shall use eight-bit addressable bytes. A different addressable-unit model shall publish its distinct byte, UTF-8, layout, serialization, and foreign-interface contract.

## 2. Source text and tokens

### 2.1 Encoding and identifiers

A source file is well-formed UTF-8. A single UTF-8 byte-order mark at the beginning may be accepted and does not form a token. A malformed source encoding is `ERROR`. Source locations shall retain a mapping to the original file bytes. CRLF and CR line endings are treated as line separators for tokenization; an ordinary quoted literal cannot contain an unescaped physical line separator.

ASCII letters and underscore may start identifiers; ASCII digits may continue them. The enabled Unicode identifier profile additionally admits the Unicode 17.0.0 `XID_Start` and `XID_Continue` sets, with underscore admitted explicitly and default-ignorable characters excluded. Identifier identity uses NFC normalization, is case-sensitive, and does not perform compatibility folding or visual-confusable folding. Non-NFC source spelling receives `WARNING` and resolves to its normalized identity. Two declarations whose normalized identifiers coincide are ordinary declarations of the same name and obey duplicate-definition rules.

The selected identifier profile and Unicode data version shall bind before tokenization and remain frozen for the owning Core root unit or named module's source identity. Every source unit belonging to one named module shall use that module's bound profile and version. A provider extension may select a different version for a new Core root or named-module binding; existing bound names shall retain their identity. The relevant character properties and normalization definitions are those of [Unicode identifiers](https://www.unicode.org/reports/tr31/tr31-43.html) and [Unicode normalization](https://www.unicode.org/reports/tr15/tr15-57.html). The language's exclusions and identity policy are the rules stated above.

Keywords have their specified ASCII spellings. Visually similar characters are not keyword aliases. Confusable identifiers and bidirectional control characters in comments or strings may receive `ANOMALY` without changing the literal's data. A control character outside an admitted token is not an invisible punctuation substitute. Identifier escapes, token pasting, and preprocessor replacement are not core lexical mechanisms.

Whitespace separates tokens where required. `//` begins a line comment. `/*` and `*/` delimit a block comment; nested block comments are balanced. Comment delimiters inside a quoted literal have no comment meaning. Unterminated comments and literals are `ERROR`. Comments cannot concatenate identifier fragments into one token.

### 2.2 Character and string literals

`char` denotes one Unicode scalar value: an integer in `0..0x10FFFF` excluding `0xD800..0xDFFF`. Its representation and explicit conversion rules follow the type specification. A character literal such as `'A'` or `'\u{1F642}'` contains exactly one scalar value after escape processing. A grapheme containing several scalar values is not one `char` merely because it displays as one symbol.

The standard escapes are `\\`, `\"`, `\'`, `\n`, `\r`, `\t`, `\0`, and `\u{H...}` with one through six hexadecimal digits denoting a valid scalar. Unknown escapes are `ERROR`. Octal escapes and unbounded hexadecimal escapes are not admitted. Arbitrary byte data can be expressed as byte arrays and explicit byte operations without pretending that it is text.

A string literal contains a sequence of scalar values encoded as UTF-8, followed by one zero byte. If its encoded content has N bytes, its type is `const<byte>[N + 1]`, with static storage duration. Embedded zero values are permitted and count toward N. The terminator is separate from the content length. Adjacent quoted literals do not concatenate implicitly. Explicit compile-time concatenation preserves these length and encoding rules.

Literal objects are read-only. An implementation may share storage for equal literals; their addresses are not unique identifiers for source occurrences. Literal comparison and hashing shall use their declared content/value contract. A string literal does not decay to a pointer or become a zero-terminated foreign string implicitly. An explicit view constructor selects content bytes, all array bytes, or a zero-terminated contract.

The scalar-value and UTF-8 definitions are those of [Unicode 17.0.0, Chapter 3](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/). Text normalization is not automatically applied to string contents.

### 2.3 Tokens and declaration context

Numeric tokens follow the [numeric expression specification](07_numeric_expressions.md#chapter-07-numeric-expressions). Punctuation is recognized by longest applicable token, except that a parser closing a generic argument list may consume `>>` as two closing delimiters. This exception does not change a shift expression into generic syntax without a grammar-established generic argument context.

The [consolidated grammar](15_grammar_binding.md#chapter-15-grammar-binding) defines the punctuation set, declaration decoration, and binding-sensitive disambiguation. Attribute delimiters are pairs of bracket tokens, not indivisible longest-match punctuation; nested indexing such as `array[indices[index]]` therefore remains two index closers. Generic closing does not split >= or >>=. A value argument needing a greater-than comparison or right shift protects that subexpression with parentheses.

Object declarations retain `Type name(arguments);`. Function declarations without a body require `declare`, or their explicit foreign declaration context. Parentheses do not create a second variable-initialization category. A selected declaration production shall retain its interpretation through type checking.

### 2.4 Names and scopes

`namespace name { declarations }` shall introduce or extend a nested namespace owned by the current compilation scope: the Core root owner or the selected named module under Chapter 11. Qualified lookup shall use `::`; selected module/import declarations shall use dots for module names. Equal namespace paths in distinct owning scopes shall retain their respective declaration ownership. Imported namespace members shall follow their explicit lookup and visibility rules.

Names in an ordinary lexical scope are introduced by reachable declarations preceding their use. A record's member declaration index is available throughout that record definition, while runtime access still obeys member construction order. `declare struct T;`, `declare class T;`, and `declare union T;` introduce incomplete nominal types; a later definition must agree. An enum identity may be declared with its fixed underlying type, but its value set and construction require the complete definition.

Types, objects, functions, and aliases share the ordinary declaration-name namespace; only legitimate function overloads may reuse one name for several entities in that scope. Inner scopes may shadow an outer name and receive the configured diagnostic. A local's own initializer does not read a same-named outer object by accident: the new declarator has already introduced its name, and premature value access is a lifetime error. Closure initializer captures retain their expressly specified outer-binding lookup.

`static Type name(arguments);` in a block gives the object static storage duration and lexical visibility. It joins the image's eager static initialization graph and logical shutdown order; it is not initialized lazily on the first execution of that statement. Its initializer cannot capture invocation-specific parameters or automatic locals. Required calls/dependencies are resolved as for other static definitions. No hidden first-use lock is introduced. An explicitly enabled lazy-initialization library type may provide a separate once/admission protocol.

A static member is likewise an image-domain object. `thread_local` selects the separately specified eager per-thread initialization domain. Storage-duration modifiers do not create an alternate initializer grammar or change an existing object type's copy/move behavior. The bound Core root or selected module map shall determine the canonical owning instance for each emitted static or thread-local declaration.

## 3. Expressions and evaluation

### 3.1 Precedence

The following rows run from greatest to least binding strength. Parentheses override grouping. Associativity determines grouping, not evaluation order.

| Group | Operators or forms | Grouping |
| --- | --- | --- |
| Primary and postfix | Qualified names, literals, grouping, calls, indexing, `.`, `->`, postfix `++`, postfix `--` | Left to right. |
| Unary | Prefix `++`, prefix `--`, unary `+`, unary `-`, `!`, `~`, address `&`, indirection `*`, `await` | Right to left. |
| Multiplicative | `*`, `/`, `%` | Left to right. |
| Additive | `+`, `-` | Left to right. |
| Shift | `<<`, `>>` | Left to right. |
| Relational | `<`, `<=`, `>`, `>=` | Left to right; each result is Boolean. |
| Equality | `==`, `!=` | Left to right. |
| Bitwise AND | `&` | Left to right. |
| Bitwise exclusive OR | `^` | Left to right. |
| Bitwise inclusive OR | `\|` | Left to right. |
| Logical AND | `&&` | Left to right; short-circuit. |
| Logical OR | `\|\|` | Left to right; short-circuit. |
| Conditional | `condition ? first : second` | Right to left. |
| Assignment | `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `<<=`, `>>=`, `&=`, `^=`, `\|=` | Right to left. |

A comma is a separator in its specified grammar positions; there is no comma expression operator. Chained relational expressions are not mathematical chained comparisons: `a < b < c` first compares a Boolean with c and requires such an operation to be valid. The compiler shall diagnose a likely chained-comparison mistake with at least `WARNING`; invalid operand types remain `ERROR`.

The built-in logical operators require `bool`. They cannot be overloaded to lose short-circuit semantics. Pointer, integer, enum, and result values have no implicit truth conversion. Explicit comparisons or status predicates supply conditions. The conditional operator requires a Boolean condition and evaluates one branch only. Its branches must establish the same result type or the ordinary lossless common value type; branch conversion shall use that established result type. Two same-type lvalue branches may produce an lvalue with the common read-only qualification.

### 3.2 Sequencing and assignments

Ordinary synchronous calls evaluate the callable and then arguments from left to right, once each until failure. Async creation instead follows its explicit callable/Context/frame-admission protocol; admission failure returns a failed task before later arguments execute. Built-in binary expressions evaluate their left operand before their right operand. Overloaded operator syntax preserves the corresponding operand-evaluation order; the selected function's body then obeys its own contract. Generic instantiation and inlining do not erase an async admission effect or alter these rules.

Assignment locates its destination, evaluates the source, performs the selected update, and yields the destination lvalue on success. Locating the destination does not load its old value. Compound assignment additionally captures the old value before evaluating its source, as specified for numbers. An assignment returning an lvalue does not extend that object's lifetime. `a = b = expression` locates a, then b, then evaluates the source and commits the inner assignment before the outer assignment.

Source-side effects are not rolled back merely because a later update fails. The selected operation's failure guarantee specifies whether its destination remains unchanged. Ordinary user-defined assignment is not automatically a transaction. An assignment to a construction reservation retains the first-construction rules and does not become an ordinary value update prematurely.

A full expression ends at its containing expression statement, initializer completion, control condition, loop update, or returned-result initialization, unless a specialized rule specifies another boundary. Successfully constructed temporaries are destroyed in reverse construction order after the full expression's committed effects. A temporary needed to complete a call remains alive through that call and the surrounding full expression.

Binding a reference does not generally extend a temporary's lifetime. A temporary passed to a borrowed parameter is available for the call. A reference retained beyond its full expression does not retain the temporary; a proved later access is `ERROR`. An unproved escape is `ANOMALY` under the escape contract. Taking `std::move` or `std::forward` does not construct, transfer, or extend an object's lifetime by itself.

### 3.3 Layout queries and unevaluated operands

`sizeof(T)` returns the complete type's size in addressable bytes as `usize`; `alignof(T)` returns its required alignment. `sizeof(expression)` determines the static complete type without evaluating the expression. `decltype(expression)` obtains the type and value-category information under the type rules without performing runtime effects. A context shall inspect declarations made reachable by ordinary source binding, generic rules, and any selected module imports.

These operations do not allocate storage, invoke constructors, or access an uninitialized value. A request requiring the layout of an incomplete type is `ERROR`. A foreign type uses its selected foreign layout, not a guessed equivalent CXXN type. Provider-specific dynamic object extents are obtained through their explicit object or storage interface, not through a variable meaning of `sizeof`.

## 4. Statements and structured control flow

### 4.1 Blocks and selection

A compound statement is `{ statements }` and introduces a lexical scope. Statements and local declarations execute in source order. A local declaration's name is visible after its declarator; its value is accessible only as permitted by construction state. Automatic objects are destroyed in reverse successful-construction order when their scope exits normally or through a permitted cleanup edge.

`if (condition) { ... } else { ... }` evaluates one Boolean condition and selects one body. `else if (...) { ... }` is the nested selection form. Bodies use braces. A condition does not contain an implicit variable declaration or an implicit conversion to Boolean. A Boolean assignment deliberately used as a condition is valid, but receives `WARNING` unless an explicit additional grouping or diagnostic setting states that intent.

`switch (value) { case constant: { ... } default: { ... } }` accepts an integer or enum value and evaluates it once. Each case label is an exactly representable constant of the switch domain. Duplicate values are `ERROR`. At most one default is permitted. Each case body is a scope and exits the switch on normal completion. There is no implicit fallthrough. A terminal `fallthrough;` explicitly enters the next lexical case after destroying the current case's locals; it is invalid in the final case. It does not reevaluate the switch expression.

A switch without a matching case or default completes without executing a body. A switch on a closed enum with omitted cases receives `WARNING` unless an explicit default handles them. A type requiring payload inspection uses `match` rather than an untyped numeric view of its discriminant.

### 4.2 Loops and transfers

The core loop forms are `while (condition) { ... }`, `do { ... } while (condition);`, and `for (initialization; condition; update) { ... }`. Conditions are Boolean. An omitted for-condition means true. Initialization executes once in a scope enclosing the loop; the body has a new scope per iteration. The update executes after each normally completed body and after a continue targeting that loop. A break does not execute the update.

`break;` exits the nearest enclosing loop or switch. `continue;` targets the nearest enclosing loop. A statement label may name a loop or switch; `break label;` and `continue label;` select that enclosing construct, with continue restricted to a loop. Exited automatic scopes are cleaned in reverse order before control reaches the target.

`goto label;` is permitted within one function where the edge can be represented by the same lifetime analysis. It may leave scopes and perform their required cleanup. Its destination shall be an ordinary label in the same function, with every entered lifetime frontier already established on the edge. An edge that would expose an uninitialized automatic object or skip a required construction is `ERROR`. Labels do not make object lifetimes optional. The transfer shall execute the cleanup required by every exited scope.

### 4.3 Matching tagged values

`match (value) { case Type::Case(patterns) { ... } ... }` evaluates its subject once. A borrowed lvalue subject is not copied or moved merely to select an arm. `match (std::move(value))` explicitly selects expiring access; any actual move occurs only when the selected pattern binds an owning payload. An unselected arm performs no construction or move.

Payload binding forms and their types follow the type specification. A `ref` binding aliases a live payload for that arm. A `value` binding explicitly copy-constructs a new local, even when the subject is expiring. A `move` binding requires an expiring subject and explicitly move-constructs its local. No binding extends the source lifetime beyond its ordinary extent. A payload reference shall be used only during its designated active-case generation.

A payload underscore `_` omits that field's binding without copying, moving, abandoning, or suppressing destruction. Every field position is represented. It is distinct from the final whole-arm wildcard below.

Each case may appear once and is matched by discriminant identity. `case _ { ... }` is a final wildcard arm. A match over a closed tagged union shall be exhaustive, either by naming every case or by a wildcard. A missing case is `ERROR`. Match arms have no fallthrough. Normal completion exits the match; `break` and `continue` inside an arm retain their surrounding loop or switch targets. A `return` exits the containing function.

The core match form is a statement. A value selected by a match can be returned from its arms, constructed in an explicitly planned destination, or assigned to an already initialized object. There is no implicit creation of an uninitialized ordinary local solely to support matching syntax.

### 4.4 Return and failure edges

`return expression;` initializes the function's result using the declared return type and the expression's actual value category. A same-type prvalue constructs directly into result storage. A named lvalue shall retain its value category in a return. `std::move(local)` explicitly requests the applicable move construction. Elision of a named-object copy or move shall preserve the selected constructor, destructor, failure, and identity observations.

After result construction, the function cleans its remaining automatic locals. The caller receives a successfully returned result only after these required operations complete. If a permitted cleanup failure prevents return, an already constructed unpublished result has a cleanup obligation; it is destroyed on the applicable unwind path, subject to aggregation or termination. A result is not published once and destroyed again as an abandoned return.

`return;` is valid for a `void` function. Reaching the end of such a function is equivalent to returning. A normally completing non-void function shall construct its result. Control-flow proof uses the source program and declared nonreturning effects, not an optimization-dependent guess. A task body and constructor additionally obey their specialized completion rules.

`throw`, `try`, typed catches, aggregate-view catches, rethrow, Whole control effects, and terminal failure outlets follow their specifications. Numeric Trap and Contract Trap do not become language exceptions. A foreign nonlocal jump cannot cross CXXN scopes with unconsumed cleanup obligations unless a declared provider supplies a conforming equivalent protocol.

## 5. Storage, layout, and object identity

### 5.1 Extents and layout

A storage extent has a byte capacity, alignment, duration, address-space identity, and allocation or enclosing-object identity. A complete ordinary object has positive size. Empty native objects therefore occupy at least one byte; separately addressable live complete objects have distinct storage identities even if an implementation uses an explicitly documented address-sharing representation for an otherwise non-addressable subobject.

For a fixed array `T[N]`, N is a nonnegative compile-time integer representable in the target extent domain. Elements occupy successive slots of size `sizeof(T)` and alignment `alignof(T)`. A positive-size array has size `N * sizeof(T)` including the element type's own padding. Extent multiplication is checked before storage is obtained. A zero-element array has no element lifetime and has size at least one byte with alignment `alignof(T)`; it cannot be indexed. No default constructor of T executes for a zero-element array.

The layout of an ordinary native record is a declared ABI contract. Its members retain their specified construction order even when an explicitly permitted layout policy changes physical offsets. Overlapping live storage requires an expressly defined representation facility; a tagged union overlaps its payload storage but permits one active payload. Empty-base optimization, packing, alignment, and foreign overlays require the applicable target/layout rules rather than a source-order inference.

`sizeof(T)` includes padding. Padding is not an additional field value and is not automatically zeroed by field initialization. Two equal object values may have different padding bytes. Comparing or hashing their raw bytes does not implement value equality unless a representation contract explicitly guarantees it.

### 5.2 Duration and identity

Automatic storage lasts for its lexical activation. Static storage belongs to its initialization domain. Thread storage belongs to the creating thread under the concurrency rules. Dynamic storage lasts until an authorized release by its allocation domain. A task frame has the explicit task owner's duration and allocation contract; suspension does not end its live local objects.

An object lifetime is identified logically by its storage identity, subobject position, type, and generation. This does not require those fields to appear in every object's machine representation. Destroying or abandoning an object ends that generation. A new construction at the same address creates another generation and supplies a new valid view. Equal numerical addresses do not revive old pointers or references.

Pointer and reference analysis may carry lifetime information through bound effects and explicit contracts, extending evidence according to the selected inference depth. Foreign raw aliases shall satisfy their declared lifetime obligations. An explicitly selected checked view or dynamic destruction registration shall realize its tracking function using the representation permitted by the core execution model.

## 6. Pointers, references, and borrowing

### 6.1 Pointer values and access

`T*` is a nullable pointer to T in its declared address space. A null pointer designates no object, even on a target that permits device access at numerical address zero through a separate device interface. A pointer may designate a live object, an admitted construction/storage position, one-past an array, or an ended generation for which value access is forbidden. Merely copying or comparing a representable pointer does not read the designated object.

A pointer's type-directed default is its target-defined null value, not universally zero bytes. `nullptr` supplies an explicit null value. Object and function pointer categories remain distinct. `void*` is an explicitly type-erased object-storage pointer and is not a dereferenceable void object; element arithmetic and sizeof(void) are unavailable. Erasure and restoration use explicit pointer-view operations, preserve address-space/const/provenance obligations, and do not transfer ownership. A checked restoration requires sufficient metadata to validate its claimed type and generation; an uncheckable restoration is an explicit raw contract and receives the applicable ANOMALY. A checked-restoration claim shall identify its supporting registration/validation capability.

Indirection, member access through a pointer, and ordinary typed stores require all relevant conditions: a live matching generation; sufficient extent; required alignment; permissions for the operation; the correct object or permitted base/const view; and synchronization where required. The object must be in an allowed construction or destruction state. `this` is subject to those conditions. Selecting an initialization target, authorized first construction, and expressly construction-aware operations instead use their initialization-frontier/state contract; they do not require the target value to have already become Alive.

On a target whose ABI requires a thin native pointer, an ordinary `T*` retains that representation. Static metadata shall preserve that thin layout. Checked views may have an explicitly different representation. No code may infer an allocator, a destruction operation, a reachable object graph, or transfer authority from an unadorned `T*`.

Adding a nonnegative count to a pointer into an array selects the corresponding element or one-past position when the resulting mathematical index is in `0..N`. Negative offsets are permitted when they remain in that domain. An individual complete object is an array of one for this purpose. Address calculation cannot wrap the address space. Indirection of one-past is invalid. A pointer to a nested subarray does not gain authority over adjacent enclosing fields.

Pointer subtraction is defined for positions in the same array extent and generation; it returns the signed mathematical element difference in `isize` if representable. An unrepresentable difference reports `MemoryError::Capacity` through the memory value outlet in Section 8. `std::mem::try_pointer_distance(left, right)` supplies the corresponding `Result<isize, MemoryError>` outlet; it does not convert a violated uncheckable raw provenance contract into a successful distance. Subsequent explicit numeric conversion uses its own numerical outlet. Relational pointer comparison is defined for positions in that same extent. Comparison of unrelated pointer order requires a declared address-order provider or an explicit opaque identity-order operation; it is not a portable CXXN object order.

Equality tests pointer designations under the target's pointer comparison contract and permits null comparisons. On a flat-address target it may compare machine addresses, so equality alone does not establish the same lifetime generation or permission. A one-past pointer and an adjacent object's pointer can compare equal under such a contract without becoming interchangeable for access.

### 6.2 Qualification and aliases

Pointer-object qualification and pointee qualification are distinct. `const i32* p(...)` declares an immutable pointer object; `const<i32>* p(...)` declares a pointer to a read-only i32 view. `const const<i32>* p(...)` combines the restrictions. For references, `const T&` denotes `const<T>&`, because reference rebinding is not an assignment operation. Postfix qualification variants are not additional core syntax.

A mutable object may be viewed through a read-only reference or pointer. Removing that view restriction requires an explicit provider or representation operation and does not authorize changing an actually const object. A declaration of a const object is a promise about that object's ordinary value lifetime, not a promise that its containing storage can never be destroyed or explicitly reused.

References are borrowed, non-null bindings to objects, not owners. Forming a reference requires a valid object or an expressly construction-aware reference contract. References cannot be reseated by assignment; assignment updates the referent when permitted. Raw pointer arithmetic is not implicitly applied to a reference.

The ordinary native alias model does not grant disjointness merely because two pointers have different element-type spellings. Permitted byte observation, base views, union transitions, foreign calls, and explicit storage reuse must be included in alias analysis. An access through an incompatible typed view still requires its explicit representation/lifetime contract. Conservative aliasing does not make arbitrary type punning a live-object construction.

An explicit no-overlap or unique-access function contract may justify stronger optimization over its declared duration and region. It shall identify the affected storage and whether reads, writes, or lifetime changes are excluded. Unknown aliases receive the applicable `ANOMALY`; they are not proof that an exclusive contract holds. A compiler-internal alias promise stronger than the source contract is forbidden.

### 6.3 Borrow and escape effects

`[[noescape(p)]]` states that a function does not retain p or a pointer/reference derived from its borrowed designation after the call or transfer it to work that outlives the call. Returning such a borrow is permitted only through an explicitly declared `returns_borrowed_from(p)` contract; without that declaration it is an escape. The two annotations together permit that declared return path while forbidding hidden retention. Temporary use by nested synchronous calls satisfying the same bound is permitted. Noescape does not independently promise no mutation or no exceptions.

`[[returns_borrowed_from(p)]]` states that the returned borrowed view designates storage whose available lifetime is bounded by p's declared owner/lifetime contract. It does not extend that duration. Several named parameters may be specified when the result can derive from any of them; a caller must conservatively retain all relevant alternatives unless the selected origin is otherwise established.

The optional `[[retains(p, owner)]]` contract permits an independently retained borrow beyond the immediate call only when the named owner/admission and its referent lifetime contract are valid. It does not extend raw-pointer lifetime or enable silent reference counting. The [effect-boundary rules](25_effect_composition_and_boundaries.md#chapter-25-effect-composition-boundaries) distinguish retention, return of a borrow, ownership transfer, and a merely opaque call.

`[[consumes(p)]]` states the successful ownership or responsibility transition defined by that parameter's interface. It shall specify failure behavior and the particular ownership authority consumed. A `Result`-returning transfer may consume on success only. A source whose transfer fails retains the promised state; a successful transfer prevents a second release through the old owner.

Definitions must satisfy their exposed effects. Opaque functions without a noescape contract conservatively may retain borrowed values. A proved escape of an automatic object beyond its lifetime is `ERROR`. An unresolved external escape is `ANOMALY` with an explicit lifetime obligation. No automatic borrow checker forbids otherwise permitted aliasing merely because two writable pointer values coexist.

## 7. Raw memory and representation access

### 7.1 Bytes and live values

Freshly allocated raw storage contains no live T solely because it is large and aligned enough for T. Raw byte initialization does not by itself invoke a class constructor, establish a tagged union's active case, create pointer authority, or register a destructor. `construct_at` and declared representation-construction facilities start those lifetimes explicitly.

Read-only representation observation through `std::mem::as_bytes(object)` produces a byte view of the object's representation. Reading it does not perform a numerical conversion, quiet a signaling NaN, or invoke user equality. Padding bytes have unspecified byte values on observation and are not promised stable across stores. Exporting them may reveal unwanted data and receives the configured `ANOMALY`. Such observation does not inject a poison value into unrelated computations.

Byte reads of uninitialized raw storage similarly produce unspecified byte values where the target permits the read, without manufacturing a live typed value. They may expose previous contents and are `ANOMALY`. Required constant evaluation cannot depend on such a value. Reading inaccessible storage remains a memory-contract violation. This permission is not a universal permission to read uninitialized class members through their declared types.

`copy_bytes(destination, source)` has overlap-safe memmove-style behavior over the stated byte ranges. It evaluates and validates the ranges before modifying the destination. When either extent or permission is dynamically checkable, a failed check leaves the destination unchanged. It copies bytes and permitted pointer metadata only to the extent declared by the target representation provider; copying arbitrary serialized bytes does not restore capability metadata.

A destination that is inactive raw storage remains inactive after a byte copy. Copying over a live nontrivial object requires an explicit operation that discharges its lifetime obligations and establishes the replacement. No implicit destructor call or implicit Abandon is inserted by a raw byte operation. A plain byte destination has its ordinary byte-array lifetime; that fact does not extend to an unrelated object type later viewed at the same address.

### 7.2 Representation conversion and unaligned access

`std::mem::try_representation_cast<T>(source)` is available when the selected type/provider contract defines a fixed-size, value-independent representation transfer of equal size without copying ownership or an active lifecycle registration. It checks any destination representation restrictions and returns `std::Result<T, MemoryError>`. Its value counterpart uses the specified memory failure outlet. It is distinct from numerical `reinterpret_bits`, checked conversion, and arithmetic conversion.

Integer and floating representation transfer may preserve all their declared bits, including negative zero and NaN payloads. A Boolean, enum, Unicode scalar, pointer, or tagged union has additional validity conditions; their representation operations shall validate the corresponding admitted value set. User-defined nontrivial resource owners are not representation-copyable merely because their size is known. A provider may define explicit encode/decode operations instead.

`load_unaligned<T>(bytes)` and `store_unaligned<T>(bytes, value)` are explicit provider operations for supported representation-copyable types. They perform byte-wise or otherwise target-admitted access without imposing a false natural-alignment assumption. The load constructs a separate T result; it does not declare that a T object is already alive at the byte address. Endianness is native unless an explicit endian load/store operation selects another order.

An incompatible-size, unsupported-representation, or statically invalid range request is `ERROR`. Dynamic checked failures precede the memory access and use the operation's Result or memory-failure outlet. No unaligned operation creates synchronization, ownership transfer, or permission to read memory beyond its supplied extent.

### 7.3 Addresses, device memory, and external representations

Pointer-to-integer conversion and integer-to-pointer reconstruction are explicit target-provider operations. The provider shall state address space, width, bounds, permissions, provenance retention, and whether the reconstruction can identify a still-live generation. On targets where an integer transports address bits only, round-trip bit equality does not supply omitted authority. A numerical bit cast is not a substitute for that contract.

An explicit device-memory capability may designate addresses without ordinary RAM object lifetimes. Its load/store operations declare access width, alignment, endianness, side effects, ordering, and permitted repetitions. A device access shall preserve the repetitions and ordering declared by its device contract. Device ordering and thread atomic ordering are separate; a volatile device access is not automatically an atomic synchronization operation.

Imported C unions, mapped binary formats, and device register overlays may use declared external representation views. Such views state which reads are valid and how representations are decoded. The native `union` keyword remains tagged. Importing an untagged representation does not authorize ordinary native code to read an inactive native payload or copy a resource-owning object as bytes.

## 8. Checked views, raw contracts, and failure

`std::mem::Span<T>` carries a pointer and element count with a bounded-range contract. Its ordinary indexing checks the index before access; `try_at` returns a Result. A zero-length span may contain null; empty subspan construction shall preserve its empty designation through a valid pointer operation. Span bounds alone do not prove the lifetime of its borrowed storage.

`std::mem::CheckedPtr<T>` additionally carries or references an explicit tracking contract capable of rejecting an ended generation. Its tracking metadata shall remain live through every handle operation, including checks after payload release. The selected provider may retain a small tracking record, require an explicit tracking domain, or use statically sufficient information. These costs and resources are explicit. It does not retain the pointee lifetime unless it is separately an owning handle.

A checked pointer cannot be synthesized with complete guarantees from an arbitrary raw address alone. Its creation requires a recognized storage/object registration or an explicit provider validation contract. Admission failure returns a Result before exposing the handle. Its optional tracked representation shall be distinct from an ordinary foreign pointer's bound representation.

Known null dereference, wrong generation, out-of-range access, forbidden lifetime transition, or impossible alignment is `ERROR` at a required diagnostic site. A checkable dynamic violation is rejected before the invalid action. The `try_` memory interface returns `std::Result<T, MemoryError>`; a reference result uses `std::Ref<T>` as its value wrapper. The value interface raises `LifecycleError` carrying the memory error when language exceptions are enabled, or invokes the nonreturning memory-failure terminal hook when they are disabled. Explicit provider operations may specify a nonthrowing terminal outlet instead, and shall identify that in their type/effect contract.

The standard memory error codes are `Null`, `Bounds`, `Alignment`, `Lifetime`, `Representation`, `Ownership`, `AddressSpace`, and `Capacity`. Metadata or allocation admission failures use their resource error contract. Invalid source argument expressions fail under their own rules before the operation begins; a memory Result does not catch arbitrary exceptions from argument evaluation or a called constructor.

An admitted unproved raw-access obligation shall produce ANOMALY and remain the programmer's access contract. Optional validation follows the configured mode. Violations and stronger trusted assumptions shall follow the core execution model.

`ContractTrap` is the nonreturning, noncatchable, nonunwinding terminal event for a violated checked library contract that expressly selects that outlet. It is distinct from a recoverable Result and from a language exception. A target may share terminal machinery with Numeric Trap while retaining the event category. Numeric operations retain their own prescribed Numeric Trap or Result semantics; this chapter does not relabel them.

## 9. Storage allocation, release, and reconstruction

Allocation interfaces declare their allocator domain, resource domain, requested byte extent, alignment, and failure result. Successful allocation grants one exclusive storage-release authority. Borrowed pointers and storage views do not duplicate it. Zero-byte requests are permitted only under a provider's explicit empty-allocation contract; a successful empty token is not an object that may be dereferenced.

Deallocation uses the original allocation domain or an explicitly compatible provider. Its input includes the allocation identity and any required extent/alignment information. Releasing an interior pointer, an automatic extent, an already released allocation, or an incompatible domain is invalid. A checked release validates before committing and leaves ownership unchanged on failure.

The primitive release operation does not invoke object destructors. Its extent must have no live registrations whose objects require ending before release. `destroy`, `abandon`, `construct_at`, and `transfer_storage` retain their distinct meanings. A library owner may deliberately combine these operations in its destructor, but that behavior is the owner type's explicit contract rather than an implicit property of a raw pointer.

Dynamic allocation does not waive the construction specification's rollback rules. A failed constructor can leave an allocated extent owned but without a complete object. A combined allocate-and-construct factory shall say whether it retains that allocation for the caller or releases it before reporting failure. That failure result shall retain or discharge the unique release authority as specified.

`storage_of` observes authorized storage metadata without loading an ended object value. `construct_at<T>` starts a new generation only after its capacity, alignment, availability, and overlap requirements hold. A failed replacement preserves the current storage owner's authority and does not revive the previous generation. A transfer between resource owners additionally obeys accounting and admission contracts; equal addresses do not imply an ownership transfer.

Automatic local storage cannot be transferred past its physical duration. Dynamic storage may be transferred exclusively without moving its address, if the source and destination resource contracts permit it. Transferring metadata does not allow one allocation to be counted as two independent exclusive resources or deallocated twice.

## 10. Compilation contracts and configuration

The source and raw-validation keys, defaults, and freeze points are defined in Chapter 08. The owning Core root or named-module source identity shall bind before tokenization of its source units. `available` validation shall perform the checks supplied by its provider and expose their coverage. `contract` shall use raw programmer obligations with optional instrumentation disabled. Explicit checked interfaces shall retain the function selected by their names and types.

An implementation shall distinguish proven valid access, retained dynamic checks, and unproved raw contracts in its diagnostic/effect information. `MEM001` identifies a proved invalid memory action and is `ERROR`; `MEM002` identifies an unproved raw validity or escape obligation and is `ANOMALY`; `MEM003` identifies representation exposure of uninitialized/padding data and is `ANOMALY`. Ordinary unnecessary copies or unused valid locals may remain `WARNING`.

Lowering to an optimizing intermediate representation shall preserve the source's failure and alias contracts. Non-null, dereferenceable, no-overlap, in-bounds, no-overflow, and nonthrowing promises may be attached only when proved, enforced on the relevant path, or provided by an applicable explicit contract. A backend's more permissive treatment of invalid operations does not automatically become CXXN semantics.

Support dependencies shall follow the core capability model and the explicit selected memory, device, and foreign providers.

