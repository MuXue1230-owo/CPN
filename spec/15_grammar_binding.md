<a id="chapter-15-grammar-binding"></a>

# CXXN Grammar and Binding Specification

## 1. Grammar interpretation

This chapter defines the native source grammar and its binding rules. The numerical, type, lifecycle, configuration, module, memory, concurrency, and interoperability chapters determine the semantics of the resulting constructs. Syntactic acceptance does not supply an unavailable type, operation, provider, conversion, or lifetime permission.

The EBNF notation uses quoted terminals, comma for concatenation, `|` for alternatives, brackets for an optional sequence, braces for repetition, and parentheses for grouping. A semicolon terminates a production. Text between question marks defines a lexical terminal class rather than an unresolved nonterminal. A quoted word denotes its exact ASCII spelling. Each production name is defined once in this chapter.

The grammar is binding-sensitive: a name already established as a type, generic family, namespace, or value determines the applicable production. Implementations may construct provisional syntax trees, but shall apply the disambiguation rules below before type checking. The selected production shall retain its interpretation through constructor, accessibility, overload, and conversion checking.

Alphabetic terminals in these productions are reserved keywords except the contextual words `Manual`, `Complete`, `aggregate`, `base`, `base_path`, `expression`, `final`, `move`, `override`, `postfix`, `prefix`, `ref`, `type`, `value`, and `virtual_base`. A contextual word selects its special meaning only in the production requiring it; elsewhere it is an identifier. Attribute names are metadata paths. Configuration paths and values alone use the broader metadata-word class to admit reserved keyword spellings. Ordinary identifiers cannot use a reserved keyword. Predefined numeric type names denote enabled target type bindings, rather than numeric-token suffixes.

`define` shall be a reserved keyword selecting an external object definition under Section 7. The ordinary object-declaration and ordinary function-prototype forms shall retain their own grammar.

## 2. Lexical boundaries

```ebnf
identifier = ? An identifier under the selected Unicode profile,
               normalized to NFC, excluding reserved keywords ?;
metadata-word = ? An identifier-shaped token, including a keyword
                  spelling, interpreted as metadata rather than
                  an ordinary program-name lookup ?;
integer-literal = ? An unsigned decimal, 0b binary, 0o octal,
                    or 0x hexadecimal integer token as defined
                    by Numeric Expressions Section 3.1 ?;
real-literal = ? A decimal real token, or a hexadecimal real
                 token with a mandatory p exponent, as defined
                 by Numeric Expressions Section 3.1 ?;
character-literal = ? One quoted Unicode scalar after the
                      source chapter's escape processing ?;
string-literal = ? A double-quoted UTF-8 string token after
                   the source chapter's escape processing ?;
literal = integer-literal | real-literal | character-literal
        | string-literal | "true" | "false" | "nullptr";
```

Source encoding, normalized identifier identity, comments, and escapes follow the [source specification](12_core_memory_control.md#chapter-12-core-memory-control). Whitespace and comments separate tokens; they never concatenate fragments. A block comment nests. Ordinary quoted literals cannot contain an unescaped physical line separator. String tokens do not concatenate by adjacency.

Except for generic closing delimiters, punctuation uses the longest applicable token. The multicharacter punctuation tokens are `::`, `->`, `...`, `++`, `--`, `&&`, `||`, `<<`, `>>`, `<=`, `>=`, `==`, `!=`, `+=`, `-=`, `*=`, `/=`, `%=`, `<<=`, `>>=`, `&=`, `^=`, and `|=`. The remaining punctuation terminals are their individually written characters. Attribute delimiters are two bracket tokens, so `a[b[c]]` still closes two index expressions. Comment openers are recognized before punctuation. A digit-starting token that appends an inadmissible radix digit or identifier continuation is a malformed numeric token; `0b102` and `12abc` do not become several valid adjacent tokens. A decimal point belongs to a real token only with the required digits on both sides. A leading sign remains an operator.

A parser may split `>>` into two `>` tokens only when closing established generic argument or parameter lists. The tokens `>=` and `>>=` shall remain whole tokens. Whitespace is required where an intended closing `>` would otherwise combine into one of those tokens. Within a generic list, an unparenthesized `>` at the current delimiter depth closes the list. A value argument containing a greater-than comparison or right shift encloses that subexpression in parentheses, for example `Buffer<i32, (limit >> 1)>`. Parentheses protect the expression's tokens from generic closing interpretation.

## 3. Translation units, modules, and configuration

```ebnf
compilation-unit = { configuration-declaration },
                   [ module-header ], { import-declaration },
                   { file-item };
file-item = configuration-declaration | export-declaration
          | declaration;
module-header = [ "export" ], "module", module-name,
                [ ":", module-name ], ";";
module-name = identifier, { ".", identifier };
import-declaration = [ "export" ], "import", [ "type" ],
                     [ identifier, "=" ], import-target, ";";
import-target = module-name | ":", module-name;
export-declaration = "export",
                     ( declaration | "{", { declaration }, "}" );
configuration-declaration = "configuration", "{",
                            { configuration-binding, ";" },
                            "}", ";";
configuration-prefix = "configured", "(", binding-list, ")";
binding-list = configuration-binding,
               { ",", configuration-binding };
configuration-binding = metadata-key, "=", configuration-value;
metadata-key = metadata-word, { ".", metadata-word };
configuration-value = metadata-word | string-literal
                    | integer-literal
                    | "[", [ configuration-value-list ], "]";
configuration-value-list = configuration-value,
                           { ",", configuration-value };
```

A named module unit shall have exactly one header and select `compilation.modules`. A headerless Core unit shall use the internal root identity specified by the [module specification](11_modules_compilation.md#chapter-11-modules-compilation). A selected multi-unit module compilation shall assign its roots through that chapter's logical map. Imports shall select module compilation and occupy the preamble before file declarations. A later configuration declaration shall affect following declarations subject to already frozen boundaries and preserve the completed import preamble.

Dots separate module and configuration components; `::` separates program-name components. `import std.mem;` establishes the canonical `std::mem` path. A partition import cannot have an alias. Reexport, incomplete type import, namespace ownership, and cycle rules retain their module meanings.

Configuration values are metadata, including `true`, `false`, and enum-like spellings accepted as metadata words. Their interpretation comes from the selected key schema. They do not evaluate constructors or look up runtime objects. Duplicate bindings, unknown standard keys, malformed value kinds, and overrides beneath a frozen boundary are errors. The target-to-expression hierarchy and definition-site capture rules are those of [runtime configuration](08_runtime_configuration.md#chapter-08-runtime-configuration).

## 4. Declaration decoration and names

```ebnf
declaration = configuration-prefix, declaration
            | { attribute-list }, [ generic-prefix ],
              declaration-core;
declaration-core = namespace-declaration | alias-declaration
                 | record-declaration | union-declaration
                 | enum-declaration | incomplete-declaration
                 | constraint-declaration | function-declaration
                 | object-declaration | linkage-declaration
                 | specialization-declaration
                 | satisfaction-declaration
                 | separate-special-member-definition
                 | generation-declaration;
namespace-declaration = "namespace", identifier, "{",
                        { declaration }, "}";
alias-declaration = "alias", identifier, "=",
                    ( type-id | type-constructor-ref ), ";";
attribute-list = "[", "[", attribute, { ",", attribute }, "]", "]";
attribute = attribute-name, [ arguments ];
attribute-name = ( identifier | "requires" ), { "::", identifier };
qualified-id = [ "::" ], name-component,
               { "::", name-component };
name-component = identifier, [ generic-arguments ];
generic-arguments = "<", [ generic-argument-list ], ">";
generic-argument-list = generic-argument, { ",", generic-argument };
generic-argument = ( type-id | expression | type-constructor-ref ),
                   [ "..." ];
type-constructor-ref = qualified-id | inline-constructor
                     | partial-constructor;
inline-constructor = "typefn", "<", [ typefn-binder-list ], ">",
                     "(", type-id, ")";
partial-constructor = "partial_typefn", "<", type-constructor-ref,
                      { ",", generic-argument }, ">";
constructor-application = ( inline-constructor | partial-constructor ),
                          generic-arguments;
```

The standard registered attribute schemas `requires`, `ensures`, `invariant`, `effects`, `admission_effects`, and `retains` use the [contracts and effects grammar](24_contracts_and_effects.md#chapter-24-contracts-effects). Existing `noescape`, `consumes`, `returns_borrowed_from`, `requires_initialized`, `initializes`, and `lifecycle_effect` retain their specialized parameter/slot schemas. Attribute arguments shall bind declaration-site entities and use their schema's compile-time interpretation.

The registered leading attribute `conformance_priority(N)` shall decorate an authored `satisfy` declaration when associated entities are enabled. Its single argument shall be a nondependent required integer constant in the inclusive range 0 through 4294967295, under Chapter 26's metadata rule. Each declaration shall carry at most one such attribute; an omitted attribute shall supply priority zero. A duplicate attribute, a value outside that domain, a dependent argument, or a different declaration kind shall yield ERROR. Chapter 27 owns the resulting descending-priority conformance selection.

The outer decoration order is `export`, then any nested `configured(...)` wrappers, leading attribute lists, the generic prefix, and the declaration's own modifiers. An export block supplies the export decoration to its contained eligible declarations. A namespace body contains declarations, not executable statements. A declaration creates names only in an owning scope permitted by its module contract.

An attribute's documented schema determines whether its arguments name parameters, types, constant values, symbol strings, or metadata words. Attribute arguments do not thereby become evaluated runtime expressions. Leading and permitted trailing function attributes contribute to one contract; duplicates or contradictions cannot create alternative interpretations. An attribute that is invalid for the decorated declaration is an error. ABI attributes retain their foreign-provider checks.

`::` at the beginning of a qualified name selects the current module's root lookup environment, including its visible import bindings; it does not merge unrelated module roots. An unqualified name uses the nearest applicable lexical binding. A record's complete member index is available throughout its definition. The declaration of a local object introduces its name before its initializer is bound. Closure initializer captures use their separately specified outer environment.

A `<` following a name selected as a generic family starts explicit generic arguments. The declared parameter kinds determine whether each argument is parsed as a type or a constant expression. In a type position, names shall resolve to type identities. In a value position, a nongeneric value followed by `<` uses the relational production. Dependent names obtain their kind from the generic parameter and constraint environment; neither `typename` nor `template` is required. Ambiguous or insufficient binding evidence is diagnosed, rather than guessed from later overload success.

A generic argument SHALL use the kind established by its selected parameter. An empty argument list SHALL supply an empty sequence, with applicable direct-family defaults resolved under Chapter 26. A nongeneric alias SHALL preserve the established ordinary-type or constructor kind of its right-hand side. An unapplied family name SHALL retain constructor kind; a complete application SHALL produce its ordinary type. Alias declaration identity SHALL remain separately available to reflection. Partial and inline constructor expressions SHALL use Chapter 26's compile-time substitution and capture rules. The partial_typefn keyword SHALL introduce the partial-constructor production.

## 5. Type formation and object declarations

```ebnf
type-id = type-primary, { type-suffix };
type-primary = qualified-id | "const", "<", type-id, ">"
             | function-type | "decltype", "(", expression, ")"
             | constructor-application | "(", type-id, ")";
type-suffix = "*" | "&" | "&&" | "[", expression, "]";
function-type = "function", "<", [ "async" ], type-id,
                "(", [ type-parameter-list ], ")",
                [ "noexcept" ], { attribute-list }, ">";
type-parameter-list = type-parameter, { ",", type-parameter };
type-parameter = [ "const" ], type-id, [ "..." ], [ identifier ];
object-declaration = object-head, ";";
object-head = [ storage-modifier ], [ object-qualifier ],
              ( type-id, identifier, [ arguments ],
                [ construction-tail ]
              | "auto", identifier, "(", expression, ")" );
storage-modifier = "static" | "thread_local";
object-qualifier = "const" | "constexpr";
arguments = "(", [ argument-list ], ")";
argument-list = argument, { ",", argument };
argument = expression, [ "..." ];
construction-tail = "->", construction-body;
```

A constructor application in a type-primary position SHALL produce an ordinary type. A bare constructor expression SHALL retain its kind in constructor-argument and constructor-alias positions.

The complete type precedes the declared name. Suffixes apply in written order: `T*[4]` is an array of pointers and `T[4]*` is a pointer to an array. Parentheses group types without creating C declarators. A function type denotes a callable contract; `*` explicitly forms its pointer type. Parameter names within it resolve effects only, and defaults are forbidden. `function<async T(...)>` retains the async admission phase and is not an alias for an ordinary function returning a Task.

Leading declaration `const` qualifies the outer object, with reference and array normalization defined by the [type specification](10_types_functions_generics.md#chapter-10-types-functions-generics). `const<T>` qualifies exactly its enclosed type. A `const` immediately followed by `<` starts the type constructor; otherwise it selects an admitted leading declaration or parameter qualifier. `constexpr` is a declaration property. It is not accepted as an arbitrary type suffix.

Typed objects admit empty or omitted arguments only when their default construction is viable. `auto` requires exactly one initializer expression and does not infer borrowing. A construction tail is attached only to the typed declaration whose transaction it extends. An assignment initializer, comma-separated object declarators, or name-following array suffix is not an alternative native form.

A type name followed by call parentheses is explicit construction, while a callable value followed by the same parentheses is a call. This binding distinction does not introduce implicit conversion constructors. A type construction requiring unavailable operations remains an error. Intrinsic queries such as numeric limits may expose type-qualified members under their declared contracts; they do not turn a type identity into an ordinary runtime object.

## 6. Records, enumerations, and lifecycle declarations

```ebnf
record-declaration = record-key, identifier, [ "final" ],
                     [ base-list ], "{", { member-item }, "}", ";";
record-key = "struct" | "class", [ "Manual" ];
base-list = ":", base-specifier, { ",", base-specifier };
base-specifier = [ "virtual" ], type-id;
member-item = access-label | takeover-declaration | owner-declaration
            | generation-declaration
            | { attribute-list },
              ( constructor-declaration | destructor-declaration )
            | declaration;
access-label = ( "public" | "protected" | "private" ), ":";
enum-declaration = "enum", identifier, ":", type-id, "{",
                   enum-case, { ",", enum-case }, [ "," ], "}", ";";
enum-case = "case", identifier, "(", expression, ")";
union-declaration = "union", identifier, "{",
                    { union-case | member-item }, "}", ";";
union-case = [ "default" ], "case", identifier,
             [ "(", payload-field, { ",", payload-field }, ")" ], ";";
payload-field = [ "const" ], type-id, identifier;
incomplete-declaration = "declare",
                        ( ( "class" | "struct" | "union" ), identifier
                        | "enum", identifier, ":", type-id ), ";";
constructor-declaration = [ "declare" ], identifier, parameters,
                          [ "noexcept" ], { attribute-list },
                          ( construction-body | definition-control | ";" );
destructor-declaration = [ "declare" ], [ "virtual" ], "~", identifier,
                         "(", ")", [ "noexcept" ], { attribute-list },
                         [ "override" ], [ "final" ],
                         ( compound-statement,
                           [ "cleanup", compound-statement ]
                         | definition-control | ";" );
construction-body = "{", { initialization-declaration | block-item }, "}";
initialization-declaration = "init", initialization-target, arguments, ";";
initialization-target = identifier
                      | ( "base" | "virtual_base" ), "<", type-id, ">";
takeover-declaration = "Complete",
                      [ identifier
                      | ( "base" | "virtual_base" ), "<", type-id, ">" ], ";";
owner-declaration = "destruction_owner", "<", type-id, ">",
                    "=", base-path, ";";
base-path = type-id
          | "base_path", "<", type-id, { ",", type-id }, ">";
```

A constructor or destructor's identifier names its enclosing record or tagged union. A semicolon-only native special-member declaration requires `declare`. A body or definition control is a definition and does not carry that marker. `= default;` is admitted only for an operation whose generated semantics are specified; `= delete;` participates in selection and rejects a selected use. Destructors have no overload parameters. Neither constructors, destructors, nor Cleanup bodies are async.

Union case payload declarations define per-case fields, not common untagged storage. Ordinary data-member declarations and inheritance are not additional native union representation forms. Union methods and explicitly supplied special operations retain the union's active-payload rules. Enumeration values require the explicit integer underlying type and distinct representable constants.

`init` is permitted only at the direct body level of a constructor or construction tail. Its initializer environment and canonical evaluation frontier follow [construction execution](06_construction_execution.md#chapter-06-construction-execution); textual placement among ordinary statements does not make it an executable assignment. `Complete`, `Manual`, and `destruction_owner` bind destruction responsibilities without disabling failed-construction rollback.

Lifecycle intrinsics such as `destroy`, `destroy_base`, `abandon`, `construct_at`, `storage_of`, and `transfer_destruction` use ordinary expression-call syntax with their specified operand contracts. `base_path<...>` in a lifecycle selector is metadata. The qualified member form `this->Base::~Base()` and `destroy_base<Base>(this)` have the specified equivalent base-only effect. Whole is a control effect of the selected lifecycle operation; there is no `Whole;` statement, catchable Whole exception, or implied process termination. Cleanup is attached to its destructor definition and is not a freestanding declaration.

## 7. Functions, parameters, and operators

```ebnf
function-declaration = [ "declare" ], [ function-mode ],
                       [ member-function-modifier ], type-id,
                       function-name, parameters, function-suffix,
                       ( compound-statement | definition-control | ";" );
function-mode = "constexpr" | "consteval" | "async";
member-function-modifier = "static" | "virtual";
function-name = [ declaration-qualifier ], ( identifier | operator-name );
declaration-qualifier = qualified-id, "::";
parameters = "(", [ parameter-list ], ")";
parameter-list = parameter, { ",", parameter };
parameter = [ "const" ], [ "forward" ], type-id,
            [ "..." ], [ identifier ], [ arguments ];
function-suffix = [ "const" ], [ "&" | "&&" ],
                  [ "noexcept" ], { attribute-list },
                  [ "override" ], [ "final" ];
definition-control = "=", ( "default" | "delete" ), ";";
operator-name = "operator",
                ( overloadable-token | "(", ")" | "[", "]"
                | ( "prefix" | "postfix" ), ( "++" | "--" ) );
overloadable-token = "+" | "-" | "*" | "/" | "%" | "~" | "!"
                   | "&" | "|" | "^" | "<<" | ">>"
                   | "==" | "!=" | "<" | "<=" | ">" | ">="
                   | "=" | "+=" | "-=" | "*=" | "/=" | "%="
                   | "&=" | "|=" | "^=" | "<<=" | ">>=";
linkage-declaration = "extern", linkage-name,
                      ( foreign-declaration
                      | "{", { foreign-declaration }, "}" );
linkage-name = '"C"' | '"C++"';
foreign-declaration = configuration-prefix, foreign-declaration
                    | { attribute-list }, [ generic-prefix ],
                      foreign-declaration-core;
foreign-declaration-core = foreign-function-declaration
                         | external-object-declaration
                         | external-object-definition
                         | foreign-support-declaration;
foreign-function-declaration = [ function-mode ], type-id,
                               function-name, parameters, function-suffix,
                               ( compound-statement
                               | definition-control | ";" );
external-object-declaration = [ "thread_local" ], [ "const" ],
                              type-id, identifier, ";";
external-object-definition = "define", [ "thread_local" ],
                             [ object-qualifier ], type-id, identifier,
                             [ arguments ], [ construction-tail ], ";";
foreign-support-declaration = foreign-namespace-declaration
                            | alias-declaration | record-declaration
                            | union-declaration | enum-declaration
                            | incomplete-declaration | constraint-declaration
                            | specialization-declaration
                            | satisfaction-declaration
                            | generation-declaration | linkage-declaration;
foreign-namespace-declaration = "namespace", identifier, "{",
                                { foreign-declaration }, "}";
separate-special-member-definition = declaration-qualifier,
    ( identifier, parameters, [ "noexcept" ], { attribute-list },
      ( construction-body | definition-control )
    | "~", identifier, "(", ")", [ "noexcept" ], { attribute-list },
      ( compound-statement, [ "cleanup", compound-statement ]
      | definition-control ) );
```

A body-bearing function shall state its return type. An ordinary bodyless prototype shall use `declare` and end with a semicolon. A foreign prototype shall use `foreign-function-declaration`; its leading `extern` linkage context supplies the declaration category. Function definitions shall use their body or admitted definition control. Parameter defaults shall use parentheses, form a trailing suffix, bind at their owning declaration, and evaluate at the actual call in parameter order. Function-pointer identity shall use the parameter types and callable contract.

A parameter pack expansion is not an untyped variadic parameter. Its type shall depend on an admitted pack, and expansion supplies the corresponding positional parameters. Explicit `forward T value` retains the generic forwarding contract; spelling `T&&` does not select that rule. Parameter names may be omitted only when not referenced by a body, default, or effect. `()` denotes no parameters; `(void)` is invalid.

A trailing receiver `&` admits only lvalue objects; `&&` admits xvalues and prvalues. An omitted receiver category admits both. Trailing `const` independently admits read-only receivers and gives `this` type `const<T>*`; its absence requires a writable receiver and gives `this` type `T*`. Receiver constness and category are part of overload identity and required override compatibility. Overload ranking includes the implicit receiver: an otherwise equal exact mutable binding outranks added const qualification. Two declarations with the same name, explicit parameter types, and receiver constness may distinguish `&` from `&&`; an unqualified receiver cannot coexist with either for that otherwise identical signature. Static and nonmember functions have no receiver suffix. A named receiver remains an lvalue inside its body, even for an `&&` member. Calling a member does not extend its receiver's lifetime.

A qualified function definition, such as `i32 Counter::read() const { ... }`, supplies the body of an existing declaration in the same owning module. It cannot add an undeclared member or namespace function. Qualified constructor and destructor definitions identify the same record in the qualifier and final name. Separate definitions preserve signature, receiver, noexcept, effects, and async contract, and neither redeclare defaults nor change layout. The class declaration owns virtual/static status and override/final selection; those selectors are not repeated on a separate definition. Generic ownership, constraints, witnesses, and already fixed declaration and ABI contracts remain binding. Body-private operation defaults bind at the definition and operation under the configuration hierarchy; an earlier prototype does not freeze unspecified body arithmetic. An importer cannot rebind the resulting generic definition's captured policies. The body receives the selected member's ordinary access and this context.

The nonstatic receiver supplies one operator operand. Unary and binary overload forms shall have the corresponding total operand count; `operator()` accepts its declared positional parameters and `operator[]` has one index operand. Assignment, compound assignment, call, and index operators are nonstatic members. At least one operand has the declaring nominal record or union type. Operator declarations cannot use `static` to remove a required receiver.

`operator prefix ++`, `operator postfix ++`, and the corresponding decrement forms each have one writable lvalue operand of nominal type T: a nonstatic nonconst member has no explicit parameters, and a nonmember form has one T& parameter. Prefix returns T& designating the updated operand. Postfix explicitly constructs and returns a T value representing the operand before successful update under T's value contract. Its body supplies that snapshot; the compiler does not invent a copying operation or dummy parameter. Failure follows the declared operation's guarantee, without an implicit transaction. Plain `operator++` and `operator--` declarations are invalid; expression spellings remain ordinary `++x` and `x++`. Built-in operators retain their existing result and failure rules.

There is no overloadable `&&`, `||`, conditional, comma, address-to-member, or conversion-operator declaration. Ordinary pointer member access has no recursive user-defined `operator->` rewriting. An overload does not acquire short-circuit behavior or erase a lifecycle effect. Operator declarations do not replace intrinsic numeric operations.

### 7.1 Foreign declaration classification

After declaration decorations, a foreign declaration shall select its category using this table:

| Source head and ending | Selected production |
| --- | --- |
| `define T name`, followed by optional arguments/tail and `;` | External object definition. |
| `T name(parameters);` | Foreign function declaration. Empty parentheses supply an empty parameter list. |
| `T name(parameters) { ... }` | Foreign function definition. |
| `T name;` | External object declaration. |
| An admitted support-declaration introducer | Its named type, namespace, generation, or other support production. |

The selected production shall remain fixed during semantic checking. Parentheses in a foreign function head shall parse as parameter declarations. An invalid parameter or unavailable callable ABI shall yield its corresponding diagnostic in that category. For example, `extern "C" i32 count(10);` selects a function declaration and diagnoses `10` as an invalid parameter declaration. An object initialized to ten shall use `extern "C" define i32 count(10);`.

An external object declaration shall reference the defining domain's existing object identity. An external object definition shall use its stated type and ordinary initialization transaction, including typed default construction for empty or omitted arguments. The defining domain shall supply storage and its static/thread-lifetime obligations. `thread_local` shall require the selected TLS binding. A generic external declaration shall bind its concrete signature or object representation before ABI emission under Chapter 09.

The foreign declaration context shall begin at the declaration or block immediately governed by `extern`. A nested namespace shall propagate that context to its namespace-scope declarations. A nested explicit linkage declaration shall select its own linkage for its region. A record or union body shall parse with `member-item`; a function body shall parse with `block-item`; a construction tail shall parse with `construction-body`. Their local declarations shall therefore retain ordinary CXXN object and function forms. Class member linkage and representation shall follow the class/provider contract.

Decorations shall retain the selected context through attribute and configuration wrappers. Generated declarations inserted in a foreign region shall satisfy the same category and ABI rules before publication. The `declare` marker shall select ordinary function prototypes and the separately defined incomplete-type forms. Foreign function and object declarations shall use the canonical productions above.


## 8. Generics and constraints

```ebnf
generic-prefix = "generic", "<", generic-parameter-list, ">",
                 [ requires-clause ];
generic-parameter-list = generic-parameter, { ",", generic-parameter };
generic-parameter = "type", [ "..." ], identifier,
                    [ "=", type-id ]
                  | "typefn", [ "..." ], identifier,
                    "<", [ kind-list ], ">",
                    [ "=", type-constructor-ref ]
                  | "const", type-id, [ "..." ], identifier,
                    [ "=", expression ];
kind-list = kind-position, { ",", kind-position };
kind-position = generic-kind, [ "..." ];
generic-kind = "type" | "const", type-id
             | "typefn", "<", [ kind-list ], ">";
requires-clause = "requires", "(", expression, ")";
constraint-declaration = "constraint", identifier, "<",
                         generic-parameter-list, ">", "{",
                         { requirement }, "}", ";";
requirement = "type", qualified-id, ";"
            | "associated", "type", identifier,
              [ "=", type-id ], ";"
            | "associated", "const", type-id, identifier,
              [ "=", expression ], ";"
            | "associated", "typefn", identifier,
              "<", [ kind-list ], ">",
              [ "=", type-constructor-ref ], ";"
            | requires-clause, ";"
            | "expression", "(", [ type-parameter-list ], ")", "{",
              { expression, "->", type-id, [ "noexcept" ], ";" }, "}";
specialization-declaration = "specialize",
                             ( "struct" | "class" | "union" ),
                             qualified-id, [ "final" ], [ base-list ],
                             "{", { member-item | union-case }, "}", ";";
satisfaction-declaration = "satisfy", qualified-id, "{",
                            { associated-binding }, "}", ";";
associated-binding = "type", identifier, "=", type-id, ";"
                   | "const", type-id, identifier, "=", expression, ";"
                   | "typefn", identifier, "<", [ typefn-binder-list ],
                     ">", "=", type-id, ";";
typefn-binder-list = typefn-binder, { ",", typefn-binder };
typefn-binder = "type", [ "..." ], identifier
              | "const", type-id, [ "..." ], identifier
              | "typefn", [ "..." ], identifier,
                "<", [ kind-list ], ">";
```

The typefn parameter SHALL declare the recursive constructor kind specified by its list. A kind SHALL be a finite tree; each list may end in one repeated descriptor whose application supplies a finite ordered sequence. A final generic typefn pack SHALL contain constructors of the declared element kind. Fixed positions, defaulted positions, and final packs SHALL retain their declared signatures. An explicit partial_typefn expression SHALL bind a prefix and produce the residual kind. An inline typefn mapping SHALL bind its named parameters and produce its stated ordinary type upon application. Chapter 26 defines these operations, transparent constructor aliases, capture identities, and full application.

A generic parameter default SHALL bind under its definition environment. A final parameter pack SHALL be the list's single pack and receive its ordered remaining arguments. Inline and associated constructor binders SHALL use the same recursive kind and final-pack rules, with their complete application supplied by the requesting use.

An associated declaration may supply its default type, constant, or constructor expression. A constraint containing associated entities SHALL use its first formal parameter, an ordinary type parameter, as its subject under Chapter 26. Its concrete witness SHALL use Chapter 27's unique applicable entry in the highest successful priority tier, or establish its structural fallback after the explicit search completes with established absence. An explicit satisfy SHALL remain an ordinary authored declaration and may use leading conformance priority, generic/requires, and export decoration. Its association table SHALL contain its customized bindings; omitted entries SHALL follow Chapter 26's default and accessible-nested-entity resolution.

A specialization's selected family kind SHALL determine its body and base forms. A union specialization SHALL use its union body. A fully fixed specialization SHALL use its fixed head. Generic defaults SHALL be metadata bindings. Each final pack SHALL have an empty-sequence default through its pack semantics, while explicit default syntax belongs to fixed parameters. All expansions SHALL preserve their declared order.

The selected generic declaration determines argument kinds before runtime expression binding. Constant value parameters have the admitted scalar domains of the type chapter. Parameter defaults may depend only on preceding parameters. Constraints use required constant evaluation and symbolic expression requirements; their parameter declarations do not create runtime objects. An expression requirement checks exact type and category and any stated nonthrowing condition. Its final top-level `->` before the requirement's semicolon separates the expression from its required result type; parentheses, brackets, and established generic delimiters are respected. Earlier arrows are ordinary pointer member access. Thus `pointer->read() -> i32;` has one pointer access and one result separator. Missing or malformed result separators are errors, not alternate member lookup.

Generic bodies SHALL use definition-site lookup and configuration. Structural constraints SHALL supply their established dependent operations and name kinds. Chapter 27 SHALL classify applicability, apply its specialization ordering to ordinary function/type families, and apply its explicit priority selection to conformance witnesses. Required constant intrinsic operands, including atomic memory orders, SHALL use their own declared argument contracts.

## 9. Expressions and closures

```ebnf
expression = assignment-expression;
assignment-expression = conditional-expression,
                        [ assignment-token, assignment-expression ];
assignment-token = "=" | "+=" | "-=" | "*=" | "/=" | "%="
                 | "<<=" | ">>=" | "&=" | "^=" | "|=";
conditional-expression = logical-or-expression,
                         [ "?", expression, ":", assignment-expression ];
logical-or-expression = logical-and-expression,
                        { "||", logical-and-expression };
logical-and-expression = bit-or-expression, { "&&", bit-or-expression };
bit-or-expression = bit-xor-expression, { "|", bit-xor-expression };
bit-xor-expression = bit-and-expression, { "^", bit-and-expression };
bit-and-expression = equality-expression, { "&", equality-expression };
equality-expression = relational-expression,
                      { ( "==" | "!=" ), relational-expression };
relational-expression = shift-expression,
                        { ( "<" | "<=" | ">" | ">=" ), shift-expression };
shift-expression = additive-expression,
                   { ( "<<" | ">>" ), additive-expression };
additive-expression = multiplicative-expression,
                      { ( "+" | "-" ), multiplicative-expression };
multiplicative-expression = unary-expression,
                            { ( "*" | "/" | "%" ), unary-expression };
unary-expression = unary-token, unary-expression
                 | layout-query | postfix-expression;
unary-token = "++" | "--" | "+" | "-" | "!" | "~" | "&" | "*" | "await";
layout-query = "sizeof", "(", ( type-id | expression ), ")"
             | "alignof", "(", type-id, ")";
postfix-expression = primary-expression, { postfix-suffix };
postfix-suffix = arguments | "[", expression, "]"
               | ( "." | "->" ), member-designator
               | "++" | "--";
member-designator = qualified-id | operator-reference
                  | [ qualified-id, "::" ], "~", identifier;
operator-reference = [ declaration-qualifier ], operator-name,
                     [ generic-arguments ];
primary-expression = literal | qualified-id | operator-reference | "this"
                   | reflection-primary | quotation-expression
                   | "(", expression, ")"
                   | type-id, arguments
                   | lambda-expression
                   | configuration-prefix, "(", expression, ")";
lambda-expression = "[", [ capture-list ], "]", [ "async" ], type-id,
                    parameters, [ "mutable" ], [ "noexcept" ],
                    { attribute-list }, compound-statement;
capture-list = capture, { ",", capture };
capture = identifier | "&", identifier
        | identifier, "(", expression, ")" | "this";
```

The precedence follows the nested expression productions. Repeated binary forms associate left; assignment and conditional forms associate right. Parentheses preserve category. Commas separate list elements and are not expression operators. An assignment target must be a permitted writable or construction-reservation destination; accepting its syntax does not read or initialize it prematurely.

Ordinary calls evaluate the callable and then arguments once, left to right, initializing each parameter before the next argument. Async calls retain the explicit Context and frame-admission boundary in the [concurrency specification](13_concurrency_memory_model.md#chapter-13-concurrency-memory-model). Prefix `await` is available only in an eligible async body and applies its Task-category contract. Parsing an indirect call through an async function pointer preserves that phase distinction.

`sizeof` selects its type or expression operand by established name binding and grammar, without evaluating either. `decltype` is a type-forming unevaluated query, not a runtime function call. Expressions inside metadata or required constant contexts retain the owning context's restrictions.

A closure has only its explicit captures. Plain names copy; `&name` borrows; initializer captures construct in order from their expressions. `this` captures the pointer. Capture initializers bind outer names before the new capture is introduced. `mutable` affects the closure's receiver, and neither it nor `async` implies allocation. The closure's body creates a new control-flow and return context; it does not inherit permission to use an enclosing constructor's `init` or `delegate` declarations.

## 10. Statements, matching, and failure control

```ebnf
compound-statement = "{", { block-item }, "}";
block-item = declaration | statement;
statement = compound-statement | expression-statement
          | emit-statement
          | if-statement | switch-statement | while-statement
          | do-statement | for-statement | match-statement
          | jump-statement | try-statement | delegation-statement
          | identifier, ":", statement
          | configuration-prefix, compound-statement;
expression-statement = [ expression ], ";";
if-statement = "if", [ "constexpr" ], "(", expression, ")",
               compound-statement,
               [ "else", ( compound-statement | if-statement ) ];
switch-statement = "switch", "(", expression, ")", "{",
                   { switch-arm }, "}";
switch-arm = ( "case", expression | "default" ), ":", compound-statement;
while-statement = "while", "(", expression, ")", compound-statement;
do-statement = "do", compound-statement, "while", "(", expression, ")", ";";
for-statement = "for", "(", for-initializer,
                [ expression ], ";", [ expression ], ")", compound-statement;
for-initializer = object-declaration | expression-statement;
match-statement = "match", "(", expression, ")", "{", { match-arm }, "}";
match-arm = "case", ( "_" | qualified-id,
                     [ "(", [ pattern-list ], ")" ] ), compound-statement;
pattern-list = payload-pattern, { ",", payload-pattern };
payload-pattern = ( "ref" | "value" | "move" ), identifier | "_";
jump-statement = ( "break" | "continue" ), [ identifier ], ";"
               | "goto", identifier, ";"
               | "return", [ expression ], ";"
               | "throw", [ expression ], ";"
               | "fallthrough", ";";
try-statement = "try", compound-statement, handler, { handler };
handler = "catch", "(", [ "const" ], type-id, identifier, ")",
          compound-statement
        | "catch", "aggregate", "(", identifier, ")", compound-statement
        | "catch", "(", "...", ")", compound-statement;
delegation-statement = "delegate", arguments, ";";
```

Selection and loop bodies require braces. An `else if` is nested selection. A condition is an expression of Boolean type, never a declaration or implicit truth conversion. A for-initializer includes its own first semicolon. The loop's condition and update contain no comma-operator sequence. Declaration kinds remain scope constrained: a block does not admit a namespace, linkage region, exported declaration, or nested named function merely because `block-item` admits declarations generally.

A label names a statement within the containing function. Labeled break and continue target enclosing eligible constructs; goto obeys the lifecycle-valid edge rules. A transfer cannot enter an unexecuted initializer, handler, another match arm, constructor activation, or suspended frame. Normal scope exits and permitted transfers retain required reverse cleanup. `fallthrough;` is a terminal switch-arm transfer and is invalid in the final arm.

A match arm names a case of the subject's closed tagged union, or uses a final wildcard. Each case appears at most once. Its payload pattern list represents every payload field in declaration order. A payload `_` omits binding without constructing or moving a value. It neither consumes ownership nor suppresses destruction of the active payload. A zero-payload case accepts absent or empty parentheses. `ref`, `value`, and `move` respectively borrow, explicitly copy, and explicitly move with the existing category checks. Matching evaluates the subject once and is a statement, not a result-producing expression. Exhaustiveness and active-payload lifetime rules are mandatory.

A typed catch parameter shall be an admitted lvalue-reference payload view, optionally const. Its apparent general `type-id` production does not permit catch by value, pointer matching by accident, or an expiring-reference handler. Aggregate catches bind read-only aggregate views. Primary, aggregate-view, and catch-all selection follows the exception chapter's prescribed tier priority within the nearest handler set; syntax order does not replace that priority.

`throw expression;` creates a new exception record under the enabled language-exception capability. Its admission, payload construction, and commitment order follow the [error and recovery specification](28_error_and_recovery.md#chapter-28-error-recovery). `throw;` rethrows the active handled record, preserving its primary identity and secondary sequence and the lifetime of any still-active handler. Absence of an active handler is invalid: a proved absence is ERROR, an admitted unproved context obligation receives ANOMALY, and dynamic absence enters ContractTrap before record access. Numeric Trap, ContractTrap, and Whole cannot be caught by these forms. Release termination and aggregate-profile cleanup are semantic policy boundaries, not additional source catch statements supplied by this grammar.

`delegate(...)` is accepted only in the permitted constructor activation, with a statically identified acyclic target chain and the existing unconditional-execution restrictions. A nested block does not itself make delegation conditional, while a runtime branch or loop does. Neither a catch handler nor a syntax-level return can fabricate completed construction or resume a continuation ended by Whole. Compile-time `if constexpr` binds both branches' nondependent names and applies the type chapter's selected-branch rules.

## 11. Static reflection and generation grammar

The reflection and generation capability is specified by the [static reflection specification](22_static_reflection.md#chapter-22-static-reflection) and the [declaration generation specification](23_compile_time_generation.md#chapter-23-compile-time-generation). The following productions extend the primary-expression, declaration-core, record member, and statement productions above:

```ebnf
reflection-primary = "reflect_type", "<", type-id, ">"
                   | "reflect_decl", "(", qualified-id,
                     [ ",", type-id ], ")"
                   | "reflect_expr", "(", expression, ")";
quotation-expression = "quote", "declaration", "{", declaration, "}"
                     | "quote", "expression", "{", expression, "}";
generation-declaration = "generate", "{", { generation-item }, "}";
generation-item = object-declaration | statement;
emit-statement = "emit", "(", expression, ")", ";";
quote-type-splice = "splice_type", "(", expression, ")";
quote-name-splice = "splice_name", "(", expression, ")";
quote-expression-splice = "splice_expr", "(", expression, ")";
```

Within a quotation only, `splice_type` can occupy a type position, `splice_name` an identifier position, and `splice_expr` an expression position. These are contextual quotation constructs, not ordinary runtime overloads. A `generate` body admits its local declarations and the restricted constant-evaluable statement subset stated in the generation specification. `emit` parses as a statement only in that body; elsewhere it is `ERROR` rather than a general declaration producer. `quote` is permitted only as a compile-time syntax value. The constructor and destructor form, generic deduction, access-control, and module-import restrictions continue to apply to emitted declarations.

The following registered attribute schemas replace the generic argument-expression interpretation for their names:

```ebnf
reflection-generation-attribute = "meta_grant", "(", module-name, ")"
                                | "derive", "(", generator-reference, ")"
                                | "derive_access", "(", generator-reference, ")";
generator-reference = qualified-id;
```

Here module-name is the existing dot-separated canonical module-name grammar; generator-reference uses namespace qualification and any explicitly supplied generic arguments. Meta_grant and derive_access shall occur on an authored record definition in its owning module. Derive may occur only on an admitted record target under the generation rules. The generator reference shall resolve to one reachable exported consteval function or fully applied specialization with the exact admitted `Declarations(Info)` contract. The argument is not a runtime function invocation, overload trial, filename, or string-to-code conversion.

The parser shall bind these attributes to the authorization and generation-phase contracts in the [generation specification](23_compile_time_generation.md#chapter-23-compile-time-generation). That chapter owns grant issuers, permission scope, transaction order, and target sealing.

## 12. Required binding boundaries

The following outcomes are required independently of parser implementation strategy:

| Source situation | Required interpretation |
|---|---|
| `i32 value(7);` in an ordinary declaration context | Object definition with its argument expression. |
| `declare i32 read();` | Ordinary function declaration with no parameters. |
| `extern "C" i32 read();` | Foreign function declaration with no parameters. |
| `extern "C" i32 count;` | External object declaration referring to its defining domain. |
| `extern "C" define i32 count(7);` | Object definition with foreign symbol binding and ordinary initialization. |
| `extern "C" i32 count(7);` | Function declaration category; ERROR for the invalid parameter declaration. |
| `extern "C" { namespace N { i32 read(); } }` | Foreign function declaration in N. |
| `extern "C" { struct S { i32 count(); }; }` | S has an ordinary default-initialized count data member. |
| A local `i32 count();` inside an extern-defined function body | Ordinary default-initialized local object. |
| `i32 read() { return 7; }` | Function definition. |
| `auto value(source);` | Value inference with the existing copy/move requirements. |
| `const i32* pointer(address);` | Const pointer object, without implicit pointee const. |
| `const<i32>* pointer(address);` | Pointer to a const i32 view. |
| `std::mem::Span<const<byte>>` | Nested type application; the final token may supply two closers. |
| `Buffer<i32, (limit >> 1)>` | Shift expression inside a protected value argument. |
| `a < b > c` with three value bindings | Relational expressions, followed by ordinary type validation. |
| `[[noescape(input)]] declare void inspect(T& input);` | A named parameter effect, without executing an argument expression. |
| `function<async i32(std::task::Context, i32)>*` | Pointer to an async phase-aware callable contract. |
| `destroy_base<Base>(this);` | Lifecycle intrinsic with its base-only and Whole effects. |
| `catch (...)` during a Numeric Trap | No handler interception; the terminal contract applies. |
| `reflect_type<T>` in required constant evaluation | A compile-time-only reflected type; no runtime type registry. |
| `reflect_expr(x++)` in a constant query | No increment is executed; operand must remain well typed. |
| `generate { emit(quote declaration { ... }); }` in a module scope | Adds an eligible declaration after complete validation and commit, only when enabled. |
| `generate` inside an ordinary function | `ERROR`; no implicit runtime code generation. |
| `splice_name(...)` outside a quotation | `ERROR`; it is not a general textual substitution. |

An implementation shall report malformed syntax and impossible binding as errors. Diagnostic suppression cannot create a missing declaration, choose an ambiguous parse by optimization, or bypass a mandatory lifecycle or capability check. The source form and bound contracts determine behavior before optional optimization, code generation, and native object-file lowering.

