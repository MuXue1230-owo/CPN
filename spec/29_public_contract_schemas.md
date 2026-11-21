<a id="chapter-29-public-contract-schemas"></a>

# CPN26 Public Contract and Configuration Schemas Specification

## 1. Scope and exchange documents

This chapter defines the optional `tooling.contract_export` capability and its public exchange structure for resolved configuration, provider capabilities, module maps, semantic interfaces, native ABI profiles, and build-context records. Source `cpn.config` files use the [configuration declaration grammar](08_runtime_configuration.md#chapter-08-runtime-configuration).

A selected contract-export capability shall support the applicable public records defined here. A request for standard export shall produce their canonical JSON and SHA-256 identities. The claim shall identify its supported schema revision and the record kinds applicable to its other selected capabilities. A Core compiler may claim this capability for its root unit, target, configuration, providers, and native boundaries. Serializing a root owner in a `ModuleId` or `semantic_interface` record conveys its identity; named-module parsing and separate compilation remain independently selected facilities.

With `tooling.contract_export = false`, semantic contracts shall be maintained through the core model and each feature's required internal checks. An implementation may keep direct state or use a declared private protocol. Public JSON, SHA-256 fingerprints, external module maps, and standard document emission are obligations of a selected export request. A private interface consumer shall validate the same relevant identities, declarations, effects, capabilities, and ABI conditions through its supported protocol. Selecting `compilation.modules` or `compilation.separate` establishes their semantic obligations independently of this export capability.

Within this chapter, *document*, *ContractRef*, and *fingerprint* describe the selected standard exchange representation. Other chapters' semantic records acquire this encoding when their export is selected. An implementation's internal database, AST, IR, object metadata placement, and invocation remain implementation choices. A consumer accepting a document in this standard format shall perform Section 9's validation even when it obtains that reader through a separately selected tool or provider.

Every document has exactly these root fields:

| Field | Type | Requirement |
| --- | --- | --- |
| `format` | string | Exactly `cpn.contract`. |
| `version` | positive integer | Exactly `1` for this schema. |
| `kind` | string | One of `configuration`, `provider`, `module_map`, `semantic_interface`, `boundary`, `abi_profile`, or `build_context`. |
| `payload` | object | The closed record selected by `kind` below. |
| `extensions` | array of Extension | Present, possibly empty; sorted by `(provider, name, revision)`. |

A record is **closed** unless a table expressly defines a map: unlisted fields are `ERROR`, not ignored suggestions. Required fields are present even when their array is empty. An optional field is absent when unavailable; JSON `null` is not a substitute. Numbers are exact integers; JSON fractions, exponent syntax, nonfinite literals, and negative zero are forbidden. Booleans are JSON booleans. No declaration gains semantic authority from a field that its owner is not entitled to issue.

A **Digest** is exactly 64 lowercase hexadecimal digits denoting a full SHA-256 digest. A **ContractRef** is the closed record `{kind: string, digest: Digest}`, where `kind` is one of the document kinds above. The referenced document shall be made available through the selected build inputs. A digest is not a URI and does not authorize network lookup. The content-addressed reference graph shall be acyclic. Every referenced digest shall designate a previously complete document outside the referring document's dependency ancestry. Cyclic nominal type references are represented by declaration identities inside a semantic interface, not cyclic hashes of unfinished documents.

An **Extension** has fields `provider: string`, `name: string`, `revision: positive integer`, `required: bool`, and `value: object`. Its provider/name pair uses an owner-controlled namespace, such as `vendor.example.feature`; its published provider contract fixes the value schema. An unsupported required extension is `ERROR` whenever the document is consumed for its contract. An unsupported optional extension may be ignored only when its owner declares it observational metadata that cannot alter source meaning, validation obligations, emitted code, binary layout, dependency selection, or resource ownership. Optional metadata shall reside in `build_context`, not in an ABI or semantic identity document. A semantic extension is always required.

An unknown document version, standard record field, standard configuration key, or required enum case is `ERROR`. A later schema may add a new document version; a reader shall select the schema matching that declared version. Vendor extensions never replace or weaken a standard field. A recognized record may contain additional capabilities only through its specified extension mechanism.

### 1.1 Identity primitives

The following closed records are shared by the schemas:

| Record | Fields and interpretation |
| --- | --- |
| `ModuleId` | `package_identity: string`, `module_identity: string`; package identity is nonempty exact UTF-8, module identity is the canonical dotted NFC identifier path. |
| `DeclarationId` | `owner: ModuleId`, `path: array<string>`, `kind: string`, `overload: string`, `specialization: string`; path components are canonical identifiers; empty overload/specialization strings mean inapplicable. |
| `ProviderId` | `name: string`, `revision: string`; both nonempty exact contract identifiers, with no implicit newest-version resolution. |
| `ContentRef` | `format: string`, `revision: string`, `digest: Digest`; identifies an immutable public source contract or a published provider-specific format. |
| `ArtifactRef` | `role: string`, `content: ContentRef`; role is `interface_source`, `definition_material`, `native_object`, `static_library`, `shared_library`, `binding_descriptor`, or `debug_information`. |
| `Dependency` | `provider: ContractRef`, `capability: string`, `phase: string`; provider ref has kind `provider`; phase is `compile`, `link`, or `execution`. |

Declaration kind is one of `type`, `alias`, `function`, `variable`, `generic`, `constraint`, `conformance`, `namespace`, or `generator`. A constructor, destructor, operator, generated member, or specialization retains the canonical declaration identity required by the type and grammar chapters. The `overload` and `specialization` strings are the owner provider's published canonical identity encoding, identified by the semantic interface's `identity_provider`; their encoding shall use stable logical identity fields. An implementation shall preserve collision-resolving identity material in the referenced interface content. Merely comparing a truncated spelling does not prove identity.

A `ContentRef` does not promise compiler-private AST interchange. `format = cpn.interface.source`, `revision = "1"` identifies canonical UTF-8 CPN26 interface source conforming to this edition, accompanied by its module map and bound configuration. A provider-specific format shall publish its version and declare which implementations can read it. A consuming implementation without a supported source or format alternative shall diagnose unavailable definition/interface material; it shall require the selected source/interface contract.

`ContentRef.digest` is SHA-256 of the exact immutable content octets supplied under its format contract. Contract JSON uses the canonical JSON bytes in Section 2. Standard `cpn.interface.source` and `cpn.boundary.source`, revision `"1"`, use a canonical source-token serialization: tokenize under the stated source profile, discard comments and inter-token whitespace, replace identifier tokens by their canonical NFC spellings where required, preserve every other token's exact spelling, and place one U+0020 byte between consecutive tokens with no prefix or suffix. Whitespace and newlines inside a string, character, raw literal, or quotation token remain part of that token. A quotation whose interior is tokenized source applies the same grammar-defined tokenization; quoted textual data is preserved. This rule preserves the token stream rather than formatting by source line. A reader shall retokenize and validate that stream under the declared profile; it shall preserve token boundaries and literal contents. The empty token stream is zero bytes. Native object/debug artifacts and arbitrary other binary formats use their unmodified published bytes, without JSON re-encoding. A provider-private normalized definition format specifies its own complete canonicalization before those bytes are hashed.

Physical paths, download URLs, authentication data, and search directories belong to an external artifact-location map or build invocation. They are not part of `ModuleId`, `DeclarationId`, `ContentRef`, or a semantic fingerprint. Rebinding an artifact to another physical location does not rename its declarations.

## 2. Canonical encoding, references, and fingerprints

This section owns canonical encoding for a selected standard contract export. The [configuration rules](08_runtime_configuration.md#chapter-08-runtime-configuration) determine the values supplied to the complete root document. Keys are sorted by unsigned UTF-8 byte order. No insignificant whitespace, byte-order mark, or final newline is present in the hashed bytes. Integers use ordinary decimal without a plus sign or redundant leading zero. Strings preserve exact Unicode scalar spelling; only quotation mark, backslash, and U+0000 through U+001F are escaped. The first two use `\"` and `\\`; controls use lowercase four-digit `\u` escapes. A slash, non-ASCII scalar, and U+2028/U+2029 remain their UTF-8 encoding. Unpaired surrogates and ill-formed UTF-8 are `ERROR`. NFC is applied only where the owning language identity rule already requires it.

Object key duplicates are `ERROR` before sorting, including duplicates hidden by an input parser's last-value behavior. Arrays preserve order unless their field is explicitly a set. A set is sorted by the canonical byte encoding of its elements and contains no duplicates. A table that specifies another comparison, such as a static identity tuple, uses that comparison for semantic ordering even when its transport is canonical JSON.

The document fingerprint is SHA-256 of these canonical bytes, without a prefix, suffix, self-digest, or filename. `kind`, `version`, and `format` are inside the bytes and distinguish document domains. A printed pretty version is allowed for inspection; a fingerprint always uses its validated canonical encoding. A detached checksum or artifact-location record may hold the fingerprint outside the document.

The following canonicalization vectors are normative. The `input` and `canonical` columns denote JSON text, not CPN26 source:

| Input | Canonical |
| --- | --- |
| `{ "b": 2, "a": 1 }` | `{"a":1,"b":2}` |
| `{ "list": [3, 1], "flag": true }` | `{"flag":true,"list":[3,1]}` |
| `{ "empty": [], "word": "CPN26" }` | `{"empty":[],"word":"CPN26"}` |

For the first canonical byte sequence, SHA-256 is `43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777`. These vectors validate encoding only; a small example object is not a complete contract document. An empty `extensions` array remains present in a real document and affects its digest.

### 2.1 Distinct identity projections

An implementation shall compute each identity projection from its own relevant fields:

| Identity | Included material | Excluded material |
| --- | --- | --- |
| Semantic document identity | Validated public configuration, identities, interface contracts, used semantic providers, and referenced public content. | Diagnostic display/suppression, physical paths, wall time, and compilation budgets. |
| Shared boundary identity | The participating declaration/type contracts, relevant representation/call/effect/lifetime obligations, and the ABI profile required by that boundary. | Unrelated private defaults, unused modules/providers, private allocator choices, diagnostic-only settings. |
| Definition/cache identity | Canonical definition material and bindings, effective semantic configuration, admitted compile-time inputs, code-generating instrumentation, target/code generation provider revision, and dependent content. | Timestamps as a substitute for input content. |
| Build-context identity | The particular diagnostic, budget, and code-generation context record. | No implied change to the identity of an already compiled declaration. |

A change to a module's private rounding default may change its code-cache identity without changing a shared `i32` parameter contract. A change to the layout of an exported record changes the corresponding boundary identity. A warning-filter change shall affect diagnostic/build context identity. Whole-document fingerprint equality is sufficient only for equality of those complete documents, with collision handling; unequal module documents do not automatically mean that every individual boundary is incompatible.

A declaration's boundary fingerprint is the fingerprint of its `boundary` contract document from Section 6.4. Its explicitly required contract references are fields inside that document. Each such record is interpreted under its `format`/revision; a provider shall retain the lifetime and throwing obligations published by that interface. Definition material and public identity shall be checked before merging repeated generic or inline emissions.

## 3. Resolved configuration schema

A `configuration` payload has fields `language_edition`, `scope`, `owner`, `abi_profile`, `values`, and `providers`:

| Field | Type | Requirement |
| --- | --- | --- |
| `language_edition` | string | Exactly `CPN26`; the CPN26 source semantic standard designation, distinct from the JSON schema version. |
| `scope` | string | `image`, `module`, `declaration`, `block`, `operation`, or `resource`. |
| `owner` | string | Nonempty stable logical scope identity; no physical location or generated address. |
| `abi_profile` | ContractRef | Kind `abi_profile`; exact selected foreign target contract. |
| `values` | object | Resolved standard semantic keys and recognized required vendor keys, under Sections 3.1–3.3. |
| `providers` | set of ContractRef | Kind `provider`; all providers needed to interpret these resolved values. |

Resolution follows the existing hierarchy and frozen boundaries. This record contains effective values, not a second ordered list of unresolved overrides. Two equal effective configurations have the same semantic record even if one came from a preset and another from explicit source bindings. The selected preset and binding-origin display belong to `build_context`. An explicit operation remains authoritative over an inherited default.

### 3.1 Wire value classes

The key names and legal semantic values are those in Configuration Section 2.4. Their exact wire classes are fixed here:

| Wire class | Standard keys |
| --- | --- |
| Boolean | `compilation.modules`, `compilation.separate`, `library.debug_assertions`, `generic.higher_kinds`, `generic.associated_entities`, `meta.reflection`, `meta.generate`, `meta.generate_layout`, `contracts.enabled`, `contracts.trusted_assumptions`, `exceptions.language`, `exceptions.secondary.dynamic_storage`, `numeric.fp.require_finite`, `numeric.software_fallback`, `atomic.software_fallback`. |
| Positive integer | `static.workers`; resolved `thread.stack_bytes` when not the string `provider_default`. |
| Nonnegative integer | `exceptions.secondary.inline_capacity`, `exceptions.secondary.max_records`; finite `resources.hard_bytes` and `resources.temporary_bytes`. |
| Set of positive integers | `numeric.integer.widths`. |
| Set of strings | `library.modules`, `numeric.float.formats`, `numeric.fp.result_mask`, `numeric.fp.initial_trap_mask`, `numeric.fp.relaxations`, `numeric.exact.families`. |
| String or set of strings | `numeric.fp.trap_mask`; string is exactly `current`, otherwise a flag set. |
| String | All remaining semantic enum, identity, default-type, version, provider, and resource-limit keys in Section 2.4, subject to their stated domains. |

`target` resolves to the selected ABI profile's registered `profile_id`; the `abi_profile` reference supplies its complete contract. A provider-valued key is `none` where permitted or the selected ProviderId encoded as an object `{name, revision}`. This provider-object rule takes precedence over the general string row: it applies to `library.provider`, `meta.provider`, `meta.syntax_provider`, `numeric.provider`, `atomic.provider`, `thread.provider`, `task.executor_provider`, and `resources.allocator`. Provider identifiers are never guessed by splitting an arbitrary string at punctuation.

Resource limits use the integer alternative or exactly `unbounded`. `thread.stack_bytes = provider_default` retains a frozen provider-published default, whose concrete bound is included in that provider's capability contract; it is not an unknown runtime default. A versioned relaxed subnormal or Complex policy is encoded as `{provider: ProviderId, policy: string, revision: positive integer}` instead of a bare unregistered name. Standard `current`, `preserve`, `component_exact`, and `scalar_steps` retain their exact standard string spelling.

Compilation-only keys are encoded outside `values`: `preset`, `tooling.contract_export`, `construction.analysis`, `effects.inference`, every `diagnostics.*` key, `generic.max_constructor_arity`, `generic.max_normalization_nodes`, `generic.max_solver_steps`, `generic.max_witness_depth`, `generic.max_instantiations`, `meta.max_handles`, `meta.max_query_steps`, `meta.max_emissions`, `meta.max_generation_steps`, `meta.max_generation_depth`, and `meta.max_generation_bytes`. They are encoded in `build_context`. A declared public kind's actual arity, emitted generated definition, and admitted policy remain semantic even though the limit used to check them is not a runtime representation parameter.

### 3.2 Required and inactive values

Every key applicable to an enabled capability has a resolved value, including a default inherited from its definition. No runtime capability selection may fill an omitted semantic field. The following conditional rules specify when a key is inactive and therefore absent:

| Condition | Inactive or conditional keys |
| --- | --- |
| No enabled standard module | `library.provider` is absent; `library.modules` is an empty set. |
| `meta.reflection = false` and the selected generator uses no reflected entity | `meta.provider` is absent unless a separately declared compile-time capability requires it. |
| `meta.generate = false` | `meta.syntax_provider` is absent; `meta.generate_layout` is false. |
| `exceptions.language = false` | Secondary-record keys are absent; failure profile still binds other image terminal behavior. |
| `exceptions.failure_profile = terminate` | Secondary-record storage keys are absent even when language exceptions are enabled. |
| `numeric.float.formats` empty | Real-literal default and all `numeric.fp.*` keys are absent; a real literal requiring an unavailable default is `ERROR`. |
| No enabled Complex format | `numeric.complex.profile` is absent. |
| No operation/representation needs a numeric or atomic provider | Its provider key may be absent; declaring a core type does not demand an allocating provider. |
| `thread.provider = none` | Thread stack/TLS keys are absent. |
| `task.executor_provider = none` | Task cancellation default may remain a compile-time policy, but no executor or Context instance is created. |
| No configured allocating resource domain | Resource allocator/limit/quota keys are absent; explicit resource-parameter APIs remain available when their module is enabled. |

The `source.*`, core integer, capability Boolean, operation-policy, static-domain, and effect/contract keys remain present where their scopes apply. A custom profile that disables the configured integer literal type retains that exact declared default; materializing a literal that needs it shall produce the configured unavailable-type error. The absence of a floating family is the explicitly inactive case above.

For active resource domains, allocator identity, hard limit, temporary limit, and quota mode shall all be supplied through the domain's inherited or explicit contract. No default process heap or unlimited budget is fabricated. `unbounded` means that this domain adds no finite cap; ancestor hard limits, allocator capacity, and explicit temporary budgets remain binding.

### 3.3 Legal combinations

After hierarchy resolution, validation shall establish the following conditions before binding the affected declaration or operation:

| Binding | Admission condition |
| --- | --- |
| Required representation/operation | Its provider and capability are available. |
| Separate CPN26 compilation | `compilation.modules` and `compilation.separate` are enabled; the selected interface protocol is supported. |
| Standard public export | `tooling.contract_export` is enabled; the requested record kinds apply to the selected capabilities. |
| Layout, exception, target, static-domain setting | Override scope respects the frozen boundary. |
| Generation | Layout generation has generation enabled; typed syntax is available; reflected operations additionally have reflection capability. Quotation-only generation uses its own typed-syntax capability. |
| Trusted/checking contracts | Trusted mode has explicit trust permission; checked invariants have contract support. |
| Secondary records | Maximum capacity covers inline capacity; dynamic growth has a selected allocator. |
| Static workers | Multiple workers have custom-parallel scheduling and the required effect/cancellation contracts. |
| Numeric profile | Its complete control and relaxation combination is supported. Reproducible uses compatible reproducibility rules; Native binds a `numeric.native` contract. |
| Software fallback | Requested fallback has its declared provider/dependencies and enabled permission. |
| Public types | Required widths, formats, layouts, and providers are available at the owning definition. |

An unmet admission condition shall yield ERROR at its requiring use. Importing an optional module supplies capability-gated declarations. Runtime support shall follow actual use under the core model.

Chapter 08 owns preset defaults. Profile-dependent defaults shall be fully resolved before serialization. Native versus Checked/Strict selection is a semantic difference in operation bindings; optional analysis depth is a build-context choice. The exported type or effect actually determined by required source rules remains part of its semantic interface.

## 4. Provider schema

A `provider` payload has fields `identity: ProviderId`, `contract: ContentRef`, `capabilities: array<Capability>`, `dependencies: set<Dependency>`, and `compatibility: array<CompatibilityRule>`.

A `Capability` has `name: string`, `revision: positive integer`, `phase: string`, `parameters: object`, and `contract: ContentRef`. Phase is `compile`, `link`, or `execution`. Capabilities are sorted by `(name, revision)` and unique. Their versioned contract specifies their parameter schema, availability, numerical/ownership/failure behavior, required resources, and supported target subset. The capability name does not itself create a process-global instance.

Standard parameter keys for these capability classes are:

| Capability class | Required parameters |
| --- | --- |
| `numeric.integer` | `widths: set<positive integer>`, `arithmetic_widths: set<positive integer>`, `software_widths: set<positive integer>`. |
| `numeric.float` | `formats: set<string>`, `arithmetic_formats: set<string>`, `software_formats: set<string>`, `rounding_modes: set<string>`, `subnormal_policies: set<string>`. |
| `numeric.native` | `integer_widths: set<positive integer>`, `float_formats: set<string>`, `default_relaxations: set<string>`, `native_subnormal: NativeSubnormal`, `operations: ContentRef`, `environment: ContentRef`; optional `approximations: ContentRef`. |
| `library.modules` | `available: set<string>`, `minimal: set<string>`; minimal is a subset of available. |
| `compilation.modules` | `source_revision: string`; shall identify CPN26 module grammar and binding. |
| `compilation.separate` | `source_revision: string`, `protocols: set<string>`; protocols identify the available versioned semantic-interface formats. |
| `tooling.contract_export` | `schema_versions: set<positive integer>`, `record_kinds: set<string>`; the supported schema versions and applicable document kinds. |
| `thread` | `stack_default_bytes: positive integer`, `tls: string` equal to `eager_domain`. |
| `meta.reflection` | `source_revision: string`, `metadata_revision: string`. |
| `meta.syntax` | `source_revision: string`, `quotation_revision: string`. |
| `native.abi` | `profile: ContractRef` of kind `abi_profile`. |

For `numeric.native`, NativeSubnormal is exactly `preserve` or the versioned provider-policy record defined in Section 3.1. `operations` shall define the supported native operation families and their width/format-specific result or target-fault outcomes, including zero divisor, signed division/remainder overflow, invalid dynamic shift count, NaN propagation, and inactive-lane arithmetic. `environment` shall define compatible rounding/trap/subnormal controls, native clobber, context requirements, and available strong-boundary isolation. Approximation permissions shall supply `approximations`, with permitted algorithms/result relations or numerical error bounds and their input domains; otherwise that field is absent. Each declared relaxation shall have its exact meaning in this capability contract. Its identity shall bind the same operation rules in all consumers.

The three compilation/export capability classes above shall use phase `compile`. The standard export capability shall include schema version `1`; its `record_kinds` shall use the root `kind` enumeration and cover each record needed by its selected export closure. A referenced document shall be supplied as part of the declared input/output contract even when another tool authored it. The capability declarations above describe compile-time services and add their implementation dependencies only when used.

A software subset shall be contained in the corresponding supported arithmetic set. Storage support, arithmetic support, and optional mathematical support shall have their separate declared capabilities. Other standard capability contracts, including exception-record ABI, exact-family resources, codecs, clocks, atomics, Complex policies, and mathematics, shall use their owning chapter's versioned provider contract as `contract`. Their `parameters` shall be empty until that contract registers a closed parameter schema.

An optional Complex or mathematical capability contract shall enumerate the operation/format/control/delivery support relation from Chapters 05 and 18, together with each entry's value/status guarantee, resource contract, and dependencies. A grouped entry shall identify every covered operation and the admitted control/delivery combinations. Availability queries and binding shall test membership in that declared relation. The operation's implementation dependencies shall enter provider and program capability closure. Representation capability, catalogue visibility, and preset policy shall each contribute the dependencies of their own declared function. These claims use the existing Capability contract identity and standard conformance model.

A `CompatibilityRule` has `other: ProviderId`, `capabilities: set<string>`, `direction: string`, and `contract: ContentRef`. Direction is `consume`, `produce`, or `both`. It grants only the listed compatible boundary operations and representation subsets; it is not blanket compatibility between every version of two vendors. Absent an explicit rule or equal relevant contract, provider identity is not interchangeable. Dependency cycles that require one provider to be initialized before itself are `ERROR` under the existing domain graph. A permitted compiler-only nominal reference cycle uses stable ProviderId, ModuleId, or DeclarationId references resolved by a separately selected mapping; its declaration references shall resolve independently of the acyclic content-digest graph. The distinction between a nominal compile-time cycle and a runtime initialization cycle does not waive the acyclic content-addressed document graph.

## 5. Module-map schema

A `module_map` payload has `modules: array<ModuleMapping>` and `roots: set<ModuleId>`. Modules are sorted by canonical `(package_identity, module_identity)` and have unique identities. Roots identify selected non-importable application or library roots as well as any explicitly requested interface build roots; they do not invent an entry function.

A `ModuleMapping` has exactly these fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `identity` | ModuleId | Declaration owner. |
| `identity_namespace` | string | Nonempty static-order namespace, distinct from declaration ownership. |
| `importable` | bool | Whether named external import is permitted. |
| `units` | array<Unit> | Sorted by logical path; every selected source or interface unit. |
| `imports` | array<ImportBinding> | Sorted by `(unit, spelling, mode)`; no conflicting same-unit spelling. |
| `configuration` | ContractRef | Kind `configuration`, scope `module`. |
| `initialization_dependencies` | set<ModuleId> | Explicit startup barriers. |
| `artifacts` | set<ArtifactRef> | Available definitions, interfaces, and native-link material. |

A `Unit` has `logical_path: string`, `kind: string`, `partition: string`, and `content: ContentRef`. Kind is `primary_interface`, `interface_partition`, `implementation_partition`, `implementation`, or `root`. Partition is nonempty only for a partition unit. Paths use the existing normalized logical-path rules. An importable module has exactly one selected primary interface. A non-importable module has none. Partition names are unique in the owner module. Native objects do not substitute for missing generic definition material.

An `ImportBinding` has `unit: string`, `spelling: string`, `mode: string`, `target: ModuleId`, `partition: string`, and optional `interface: ContractRef`. Unit is a selected logical path. Mode is `ordinary`, `type`, `reexport`, or `reexport_alias`; the source declaration fixes any alias and ordinary visibility rules. A nonempty partition is permitted only for an internal partition import allowed by the module chapter. An interface ref, when supplied, has kind `semantic_interface` and matches the target owner. During compilation, a selected source unit may stand in place of an already built interface; that selection is explicit in the unit/artifact mapping.

A complete-interface cycle remains invalid. A permitted type-import cycle is represented by `ModuleId` references and separately sealed interfaces, without requiring cyclic document hashes. One unit cannot give a single import spelling two different target identities. Initialization dependency edges are not inferred from every type-only import.

## 6. Semantic-interface schema

A `semantic_interface` payload has `language_edition: string` (exactly `CPN26`), `identity: ModuleId`, `identity_provider: ProviderId`, `configuration: ContractRef`, `abi_profile: ContractRef`, `source_profile: SourceProfile`, `interface_content: set<ContentRef>`, `providers: set<ContractRef>`, `imports: array<ImportedContract>`, `exports: array<ExportContract>`, `statics: array<StaticContract>`, `metadata_grants: array<Grant>`, `derivations: array<Derivation>`, and `link_requirements: array<LinkRequirement>`.

`SourceProfile` has `identifiers: string` (`ascii` or `unicode`) and `unicode_version: string`. A module's profile is fixed before tokenization. Its language edition agrees with the referenced configuration. A consumer requiring another source-language edition uses an explicitly supported translation/provider contract, not a reinterpretation under its own current defaults. `interface_content` provides at least one supported full declaration contract representation. Export summaries do not replace grammar, generic constraint, effect, or ownership information present in that content. Provider refs have kind `provider`; configuration and ABI refs have their corresponding kinds. Imported native boundary contracts remain independently validated.

An `ImportedContract` has `owner: ModuleId`, `mode: string` (`ordinary` or `type`), `declarations: set<DeclarationId>`, and optional `interface: ContractRef`. It records actually bound canonical imports. A permitted type-only cycle may omit the whole-interface digest but shall identify the required declaration/representation contracts through the interface content. It cannot claim a complete layout before sealing the relevant type.

An `ExportContract` has fields `declaration: DeclarationId`, `state: string`, `visibility: string`, `definition: ContentRef`, `boundary: ContractRef`, `configuration: ContractRef`, `dependencies: set<Dependency>`, and optional `native_symbol: string`. State is `declared`, `generic_recipe`, or `sealed`. Visibility is `public` or `sealed_dependency`. An incomplete declaration is `declared`; an uninstantiated generic family is `generic_recipe`; a completed concrete record/function contract is `sealed`. A pending generation phase is not a completed export. The `definition` includes any available definition material and binding identities; `boundary` references a document of kind `boundary` containing the public representation, calling, phase-aware effect, contract-policy, borrow/lifetime, and failure obligations relevant to this declaration. A function with separate admission, execution, and boundary effects preserves each part under the [effect composition rules](25_effect_composition_and_boundaries.md#chapter-25-effect-composition-boundaries).

The standard public-source boundary format is `cpn.boundary.source`, revision `"1"`, wrapped by the exact boundary document in Section 6.4. An ABI provider may additionally publish an equivalent closed native-descriptor format. The source designation shall select CPN26's grammar and binding semantics within that envelope. For a selected standard export, the public envelope and its declared source format shall supply portable checking material; a private descriptor may accompany it. A private-only boundary follows Chapter 11's semantic identity and compatibility rules in its declared representation.

An exported constructor contract shall retain its recursive kind, fixed and repeated descriptors, captured partial arguments, inline mapping or alias identity, and captured definition bindings. An exported associated contract shall retain its complete constraint arguments and its subject binding. Each captured explicit conformance entry shall retain its fixed `conformance_priority` metadata value, including the effective default value zero, together with its head, conditions, and association bindings. The existing definition and source content shall carry this metadata; changing a priority shall change the corresponding catalogue and dependent selection identity. A known subject shall identify its captured catalogue. A symbolic subject shall identify Chapter 27's owner-resolution recipe and declared constraint evidence; its instantiated canonical type shall supply the exact published owner catalogue. A completed concrete use shall record that frozen catalogue, its selected explicit or structural witness, and association bindings. These components shall enter the existing definition, dependency, and boundary identities under Chapters 26 and 27. Import and code sharing shall use the published identities appropriate to that completion stage.

### 6.1 Static contracts

A `StaticContract` has `identity: StaticId`, `declaration: DeclarationId`, `phase: string` (`constant` or `dynamic`), `destroy: bool`, `after: set<StaticId>`, `cancellation: string` (`cooperative` or `finish`), and `external_effects: string` (`none`, `compensate`, or `finish`). Ordinary logical-file edges and module barriers remain compulsory even when omitted from the explicitly supplied `after` set.

A `StaticId` has `identity_namespace: string`, `module_identity: string`, and exactly one of:

- `source: {logical_path: string, ordinal: nonnegative integer, specialization: string}`; or
- `explicit: string`, containing the owner-issued `static_id` value.

This structured representation transports the existing static identity tuple without delimiter ambiguity. Tuple comparison, graph precedence, logical ranks, atomic commit/cancellation, and reverse logical shutdown remain as defined in the static-lifetime chapter. The map shall serialize the declared logical identity/dependency inputs. A final image may publish computed ranks as derived build information; they are recomputed from the validated graph, not accepted as an authority that can reorder it.

### 6.2 Metadata grants and derivations

A `Grant` has `owner: ModuleId`, `target: DeclarationId`, `kind: string`, and `subject: object`. Kind is `metadata_inspection` or `generated_member_access`. For `metadata_inspection`, subject is exactly `{module: ModuleId}`. For `generated_member_access`, subject is exactly `{generator: DeclarationId, definition: ContentRef}`. Grants are sorted by their canonical encoding and contain no duplicates. Only the target's owner may issue a grant. Its reach remains the [reflection](22_static_reflection.md#chapter-22-static-reflection) and [generation](23_compile_time_generation.md#chapter-23-compile-time-generation) authority of that kind.

A `Derivation` has `target: DeclarationId`, `generator: DeclarationId`, `generator_definition: ContentRef`, `ordinal: nonnegative integer`, `grants: array<nonnegative integer>`, `configuration: ContractRef`, and `emissions: array<DeclarationId>`. Ordinal is zero-based among the target's derive attributes, and emissions retain declared commit order. Grant indices address the canonical sorted grant array in this interface, not a runtime permission token. A generic recipe records the owner-issued grant and captured environment; each sealed concrete derivation records its substituted target identity and selected generator definition.

Public grant summaries do not expose otherwise inaccessible private field contents. Authorized compilers obtain the required access-filtered metadata from the declared interface material. A generator's metadata-inspection grant never becomes runtime friendship; generated-member access never authorizes a call from an unrelated function or access to a base's private declaration. Private metadata may be referenced by opaque canonical identity and content digest without making it visible to ordinary source lookup.

Grant indices shall be valid, unique, and numerically sorted. Every Grant owner equals its target's owner and the interface issuing that grant. A generated-member-access grant's generator and definition reference shall match the selected derivation. Its target shall be that authored target or a concrete instance of the authorized generic definition; an independently authored specialization, derived record, or unrelated target does not inherit the grant. A metadata-inspection grant applies only to queries actually performed in its named module under the reflection access rule; helper calls cannot pass that authority to another module. The derivation ordinal addresses the selected authored definition's exact derive list. Every emission belongs to that one validated transaction, and emission order is its commit order. A grant for one ordinal's emitted members cannot authorize a later unrelated generation transaction. These validations transport source authority and do not create a runtime permission mechanism.

### 6.3 Link requirements

A `LinkRequirement` has `name: string`, `role: string`, `provider: ProviderId`, `contract: ContentRef`, `symbols: set<string>`, and `retention: string`. Role is `object`, `archive`, `shared_library`, `unwinder`, `startup`, `allocator`, `atomic`, `numeric`, `thread`, `task`, or `diagnostic`. Retention is `referenced`, `retain_symbols`, or `explicit_domain_entry`. Symbols use exact target bytes represented as valid UTF-8 strings; a target requiring non-UTF-8 names shall use a registered ABI extension instead of lossy transcoding. Physical library search paths are not embedded here.

An empty set of link requirements is permitted for a self-contained native object. A provider shall list helper routines and runtime dependencies that actual selected operations emit. A disabled exception, allocator, task, or C++ standard-library facility does not create a link requirement just because it is present in the compiler.

### 6.4 Boundary document

A `boundary` payload has exactly the following fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `language_edition` | string | Exactly `CPN26`; shall match the referenced configuration and owning semantic interface. |
| `owner` | ModuleId | Canonical owner issuing the contract. |
| `identity_provider` | ProviderId | Canonical declaration/type identity encoding provider. |
| `declarations` | set<DeclarationId> | Participating declarations; all are resolvable in the accompanying source contract. |
| `configuration` | ContractRef | Kind `configuration`; effective settings applicable to this boundary. |
| `abi_profile` | ContractRef | Kind `abi_profile`; required native interface contract. |
| `source` | ContentRef | Format `cpn.boundary.source`, revision `"1"`, canonical source tokens as defined in Section 1.1. |
| `imports` | array<BoundaryImport> | Exact bound imported declaration identities, sorted by source spelling. |
| `layouts` | array<LayoutContract> | Complete required object layouts, sorted by declaration identity encoding. |
| `native_bindings` | array<NativeBinding> | Explicit external symbols/classifications, sorted by declaration identity encoding. |
| `requirements` | set<Dependency> | Relevant providers and support capabilities. |

`BoundaryImport` is `{spelling: string, declaration: DeclarationId}`; repeated spellings shall resolve to one identity. `LayoutContract` is `{declaration: DeclarationId, size: positive integer, alignment: positive integer, members: array<LayoutMember>, details: ContentRef}`. `LayoutMember` is `{identity: string, role: string, offset_bits: nonnegative integer, size_bits: nonnegative integer, type: ContentRef}`; role is `field`, `base`, `virtual_base`, or `hidden`, and members follow the owning layout contract's declared order. An identity may be an opaque owner-issued member identity where ordinary lookup has no right to its private spelling. Its type content gives the required fully bound type contract under its registered source or provider format. `details` supplies padding, overlap/union/bit-field, active-variant, complete/base layout, and other applicable provider rules not reduced to an offset. A foreign LayoutContract shall contain exactly the members admitted by its bound foreign layout.

`NativeBinding` is `{declaration: DeclarationId, linkage: string, external_name: string, convention: string, classification: ContentRef}`. Linkage is `native`, `C`, or `C++`. The classification content uses the selected ABI provider's published descriptor format to record the exact argument/return transport and required entry variant. A scalar-only baseline C function may use its public C declaration plus the selected profile's complete classifier as that content; a by-value record also requires its LayoutContract. Ownership and failure semantics remain in the source contract even when the classifier is only concerned with machine transport.

The source content shall be a syntactically complete unit owned by `owner`, containing the declaration-contract closure relevant to this boundary and its bound imports. For a named module it is an interface unit; for a Core root it is a headerless root declaration unit under its explicit owner and edition binding. It contains explicit contract annotations and fully bound exported types; generic constraints, conformance identities, admission/body/boundary effects, and borrow/lifetime obligations are preserved. Resolved configuration is supplied by the `configuration` reference; inconsistent source overrides are rejected. Unrelated private function bodies, diagnostic settings, code-generation tuning, and physical artifact locations are excluded. A separately required generic or compile-time definition is referenced through its definition material, without claiming that ordinary binary ABI consumers must instantiate it.

A sealed generated declaration is represented by its committed ordinary declaration contract and provenance; consuming this boundary is not permission to rerun its generator before checking its declared compile-time dependencies and phase. Forward declarations remain incomplete; a required layout cannot be satisfied by an absent LayoutContract or a pending generation result. Format-specific content may use canonical declaration identities to express a recursive pointer type without recursively hashing the same unfinished boundary document.

## 7. ABI-profile schema

An `abi_profile` payload has `profile_id: string`, `family: string`, `revision: positive integer`, `machine: MachineABI`, `object: ObjectABI`, `c: CABI`, `cpp: CppABI`, `runtime: RuntimeABI`, `features: FeatureClaims`, `references: array<ABIReference>`, and `options: object`.

The following closed subrecords define the mandatory information. Byte counts refer to octets only when `byte_bits` is eight; target size units elsewhere are stated by the profile.

| Record | Fields |
| --- | --- |
| `MachineABI` | `architecture: string`, `instruction_set: set<string>`, `byte_order: string` (`little`/`big`), `byte_bits: positive integer`, `pointer_model: string`, `object_pointer_bytes: positive integer`, `function_pointer_bytes: positive integer`, `pointer_alignment: positive integer`, `data_model: string`, `stack_alignment: positive integer`, `address_spaces: set<string>`. |
| `ObjectABI` | `format: string`, `revision: string`, `machine_id: string`, `relocation_contract: string`, `position_model: string`, `symbol_contract: string`, `archive_contract: string`, `comdat_contract: string`, `unwind_contract: string`, `tls_contract: string`. |
| `CABI` | `dialect: string`, `scalar_contract: string`, `record_contract: string`, `call_contract: string`, `variadic_contract: string`, `callback_contract: string`, `header_contract: string`, `scalars: array<ScalarABI>`. |
| `CppABI` | `provider: ProviderId` or literal `"none"`, `dialect: string`, `symbol_contract: string`, `class_contract: string`, `lifetime_contract: string`, `rtti_contract: string`, `exception_contract: string`, `library_contract: string`. The record is always present; a wholly unsupported C++ group has provider `"none"`, every other field `"none"`, and every C++ feature claim false. |
| `RuntimeABI` | `crt: string`, `crt_linkage: string`, `allocation_contract: string`, `startup_contract: string`, `terminal_contract: string`, `native_exception_contract: string`, `foreign_unwind: string`, `support: set<string>`. |
| `FeatureClaims` | `native_object`, `c_call`, `c_record`, `c_callback`, `cpp_symbol`, `cpp_class`, `cpp_lifetime`, `cpp_rtti`, `cpp_exception`, `cpp_stdlib`; every field is Boolean. |
| `ABIReference` | `id: string`, `title: string`, `revision: string`, `location: string`, `sections: set<string>`; a location is a citation, not a moving latest-version selection. |

A `ScalarABI` has `name: string`, `size: positive integer`, `alignment: positive integer`, `representation: string`, and `transport: string`. Entries are unique and sorted by name. Representation identifies exact signedness/range/format or the corresponding pinned profile rule; transport identifies its ABI classification. Native and foreign nominal types remain distinct when the language rules require it. No class-compatible flag is inferred from an equal scalar table.

`options` is a closed map under the named profile revision. It records every ABI-affecting selection, including packing, short-enum mode, plain-char signedness, long-double mode, calling-convention changes, CRT/library configuration, and extensions. A reference profile in the next chapter supplies its exact option set. An additional option requires a new profile revision or a required provider extension with a complete contract. No implicit host compiler option may override these values.

A positive feature claim is limited to the explicit subsets identified by the corresponding contract fields. A negative claim means unsupported direct use, with an explicit adapter permitted under its own contract. `none` is a deliberate absence, not an unresolved version parameter. A target contract with `crt = none` cannot call a C library merely because the object format is ELF or COFF. A C++ symbol contract with `cpp_exception = false` remains non-unwinding across that boundary.

Actual producer compiler identity/version and selected linker input versions are supplied in build context and resolved dependencies. The profile specifies their required ABI behavior; it does not falsely certify that a particular implementation has passed conformance testing. Changing a runtime dependency contract creates a distinct complete binding even when its machine profile remains the same.

## 8. Build-context schema and configuration provenance

A `build_context` payload has `producer: ProviderId`, `configuration: ContractRef`, `preset: string`, `diagnostics: DiagnosticPolicy`, `limits: object`, `generation_inputs: set<ContentRef>`, `instrumentation: set<string>`, `code_generation: ContentRef`, and `binding_origins: array<BindingOrigin>`.

`DiagnosticPolicy` has `minimum: string`, `promote: set<string>`, and `suppress: set<string>`. Minimum uses the existing `INFO`, `WARNING`, `ANOMALY`, `ERROR`, and `none` values. Blocking `ERROR` conditions cannot be suppressed. Promotion and suppression apply to registered category/code identities; conflict resolution applies promotion first, and an error cannot subsequently be hidden. This rule does not transform an unsupported operation into a permitted one.

`limits` contains exactly the active compilation-only integer keys listed in Section 3.1, using their existing positive domains and defaults. Values for disabled facilities are omitted. Exceeding a limit has the prescribed diagnostic and never selects another overload, false constraint, partial declaration, or approximate constant value. Changing limits changes the build-context document; successful identical emitted contracts retain their semantic identities.

`generic.max_constructor_arity` shall be active when higher kinds are enabled. The normalization-node, solver-step, and instantiation limits shall apply to ordinary Core and advanced generic checking with Chapter 08's standard defaults. `generic.max_witness_depth` shall be active when associated entities are enabled. Reflection handle/query limits shall be active when reflection is enabled; generation emission/step/depth/byte limits shall be active when generation is enabled, including quotation-only generation. These limits shall govern compile-time checking resources.

A `BindingOrigin` has `key: string`, `scope: string`, and `owner: string`. Scope is `target`, `preset`, `project`, `package`, `module`, `file`, `declaration`, `block`, or `operation`. The record is explanatory provenance of the already resolved binding, not another precedence rule. Origins are sorted by `(key, scope, owner)`; an implementation may emit an empty array when detailed provenance is not requested.

`instrumentation` identifies optional checks and code-generating instrumentation actually selected. `code_generation` shall identify a versioned, fully resolved provider contract recording architecture/code-generation choices, optimization settings, effective `construction.analysis` and `effects.inference` selections, and the Boolean output-selection field `tooling.contract_export`. That output selection shall describe the requested artifact availability; type, layout, operation, declaration, and shared-boundary identities shall derive from their semantic inputs. Enabling public serialization shall preserve those identities for unchanged semantic inputs. An optimization that preserves semantics need not change a boundary identity, but its compiled-code cache shall identify the actual instruction-producing option set. Producer identity and debug-symbol settings do not change a foreign struct's layout.

## 9. Validation and admissibility

Before consuming an exported contract, an implementation shall validate its root/version/schema, canonical identities, references, required extensions, configuration freeze rules, provider availability, and relevant public boundary compatibility. A missing artifact, unsupported private interface format, unknown mandatory capability, duplicate identity, invalid direct ABI, or inconsistent owner-issued grant is `ERROR` at the use requiring that contract.

A permitted unproved programmer obligation remains `ANOMALY` under the language's existing rules. The document records that obligation as unproved in its referenced contract; the writer shall preserve that unproved classification. A fingerprint asserts identity of the submitted contract bytes, not that the code actually implements the contract or that a permission was issued by the correct owner.

Generated output, type-only cycles, deferred generic recipes, dynamic-resource borrows, and optional providers shall be handled at their existing semantic phases. Public document validation does not execute initializers, allocate a program heap, run a generator out of stage, load arbitrary provider code into the target, or start an executor. Required compiler activity follows the selected compile-time provider and admitted-input contracts.

