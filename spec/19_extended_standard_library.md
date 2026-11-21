<a id="chapter-19-extended-standard-library"></a>

# CPN26 Extended Standard Library Interfaces Specification

## 1. Scope, notation, and closed interface catalogues

This chapter SHALL define the public catalogues of enabled std.io, std.time, std.codec, std.process, std.text.unicode, and std.algorithm facilities. Each invocation SHALL use the common phase, ownership, resource, guarantee, and failure model in [Chapter 14](14_standard_library.md#chapter-14-standard-library) and the [core execution model](21_abstract_machine_and_conformance.md#chapter-21-abstract-machine-conformance). The following sections SHALL supply feature-specific state transitions and outputs.

Tables SHALL use Chapter 14's semantic declaration schemata. T, F, I, and callback names SHALL denote constrained type parameters. Result, Option, and Unit SHALL mean the core std types; Span and ResourceRef SHALL mean std.mem types; text views and String SHALL mean std.text types. Numeric status, rounding, flags, and errors SHALL use their canonical std.numeric identities.

A table's namespace SHALL be its section's named module. Public records, tagged values, opaque creation paths, explicit defaults, and bounded value operations SHALL follow Chapter 14's closed-interface rules. A record-field restriction SHALL be validated by its consuming operation before admission of the affected external effect.

The following capabilities SHALL expose the catalogues shown. A required static use SHALL bind its complete capability contract. A runtime policy/device mismatch SHALL use the interface's declared Unsupported or policy error. Capability diagnostics SHALL follow Chapter 08.

| Capability | Interface sections |
| --- | --- |
| `io.bytes`, `io.files` | Byte operations/owners in Section 2; file/path operations in Section 3. |
| `io.format`, `io.parse.integer`, `io.parse.float` | Section 4; supported scalar formats are declared individually. |
| `unicode.normalize`, `unicode.segment`, `unicode.casefold` | Section 5, with one pinned Unicode data revision. |
| `time.clocks`, `time.calendar`, `time.zones`, `time.sync_bridge` | Section 6; the sync bridge additionally requires the existing synchronization clock contract. |
| `codec.scalar`, `codec.record`, `codec.stream` | Section 7; enabled wire formats are declared individually. |
| `process.arguments`, `process.environment`, `process.exit` | Section 8. |
| `algorithm.span`, `algorithm.stable` | Section 9; stable sorting additionally uses an explicit ResourceRef. |

A provider extension SHALL publish its own versioned names and contracts. Each declaration SHALL capture its resolved provider and semantic policy at its ordinary definition/interface boundary.

## 2. Byte I/O

### 2.1 Provider and owner identities

The namespace SHALL be std::io. ProviderIdentity SHALL be an opaque nonowning identity for a versioned I/O contract, with equality and `fingerprint() -> byte[32]`. Equality SHALL resolve known fingerprint collisions through the complete descriptor. ProviderRef SHALL be a trivial nonempty provider borrow with `identity() -> ProviderIdentity`. The selected hosted capability SHALL supply `host_provider() -> ProviderRef` referring to its preexisting descriptor; a freestanding integration SHALL supply its declared provider-borrow creation path.

HandleState SHALL have Open, Closing, and Closed. HandleOwner SHALL own a stable control record and its closure obligation while Open or Closing. Creation SHALL admit that record and supporting storage through the supplied ResourceRef. Provider and resource borrows SHALL extend through final release. Owner movement SHALL preserve the record's address.

Default construction SHALL produce Closed with an absent record. Move construction SHALL transfer the record and obligation and leave the source in that default state. Move assignment SHALL require a Closed destination and quiescent source/destination, retire the destination's old closed record, and transfer the source; self-move SHALL preserve state. Record retirement SHALL invalidate its derived views. `state() -> HandleState`, `has_record() -> bool`, and `provider() -> Option<ProviderRef>` SHALL be nonallocating observations, with provider absent exactly when the record is absent. Concurrent owner access SHALL satisfy its selected synchronization contract.

ReadHandle and WriteHandle SHALL be move-only borrows of the stable record. Default construction and a moved-from state SHALL be empty, observed by `has_value() -> bool`. Move operations SHALL transfer the borrow; destruction SHALL retire the borrow representation. An Open owner SHALL permit creation of several capabilities under the provider's concurrency contract. Each use SHALL require the record's continued lifetime; observations of Closed SHALL occur while that record remains alive.

| Member operation on HandleOwner | Result and contract |
| --- | --- |
| `try_read_handle()` | `Result<ReadHandle,IoError>`; require Open and read capability. |
| `try_write_handle()` | `Result<WriteHandle,IoError>`; require Open and write capability. |
| `reset()` | `void`; require Closed and no active operation; release the closed control record and become default-empty. |
| Destructor | Require Closed and quiescence, then release any closed control record. Open/Closing violates the checked ownership precondition and enters ContractTrap. |

A program SHALL discharge HandleOwner's closure obligation through try_close and observe its ordinary failures through that operation. Owner retirement SHALL then use the Closed-state contract in the table.

### 2.2 Policies, errors, and progress

ReadState SHALL have Data, EndOfInput, and WouldBlock; WriteState SHALL have Progress and WouldBlock. ReadProgress SHALL contain usize transferred and ReadState state; WriteProgress SHALL contain usize transferred and WriteState state.

`IoErrorCategory` has `Closed`, `InvalidHandle`, `PermissionDenied`, `NotFound`, `AlreadyExists`, `InvalidInput`, `Interrupted`, `BrokenPipe`, `UnexpectedEndOfInput`, `WriteZero`, `NoSpace`, `ResourceLimit`, `AllocationFailure`, `Unsupported`, `DeviceError`, `Cancelled`, `WouldBlock`, and `TimedOut`.

`IoError` contains, in order:

1. `IoErrorCategory category`;
2. `Option<ProviderIdentity> provider`;
3. `usize transferred`;
4. `Option<HandleState> close_state`;
5. `Option<usize> native_code`;
6. `Option<usize> position`.

Native code SHALL be interpreted under its provider identity. Position SHALL be an optional exact input byte offset, including UTF-16 code-unit bytes for a native path. Transferred SHALL be the cumulative public-call byte prefix bounded by the supplied extent. A nontransfer operation SHALL report zero transferred while retaining its stated flush/close/provider effects. A try_close Err SHALL carry Some of the post-call HandleState; other errors SHALL carry None. Unavailable native detail SHALL use its absence case.

RetryLimit SHALL have None, Count(usize additional_attempts), and Unbounded. It SHALL govern Interrupted retries. Each attempt's positive prefix SHALL count once, and Count SHALL decrement for each additional Interrupted retry actually made. The next attempt SHALL address the remaining suffix; other categories SHALL use their own declared outlet.

IoPolicy SHALL be a nonowning record constructed from `(std::sync::WaitLimit wait, RetryLimit interrupted, std::sync::CancelToken cancellation)` with corresponding read-only fields. `poll_policy() -> IoPolicy` SHALL return Poll, None, and an empty token. `blocking_policy(std::sync::CancelToken token) -> IoPolicy` SHALL return Unbounded, None, and that token. These factories SHALL be nonallocating. Nonempty tokens and Until deadlines SHALL bind their selected synchronization/clock capabilities and lifetimes; the empty-token Poll policy SHALL use only its byte-I/O contract.

### 2.3 Public byte operations

| Operation | Result |
| --- | --- |
| `try_read(ReadHandle& source, Span<byte> destination)` | `Result<ReadProgress,IoError>`; one provider attempt. |
| `try_write(WriteHandle& target, Span<const<byte>> source)` | `Result<WriteProgress,IoError>`; one provider attempt. |
| `read_exact(ReadHandle& source, Span<byte> destination, IoPolicy policy)` | `Result<ReadProgress,IoError>`; fill the complete destination. |
| `read_exact(ReadHandle& source, Span<byte> destination)` | Same, exactly using poll_policy(). |
| `write_all(WriteHandle& target, Span<const<byte>> source, IoPolicy policy)` | `Result<WriteProgress,IoError>`; transfer the complete source. |
| `write_all(WriteHandle& target, Span<const<byte>> source)` | Same, exactly using poll_policy(). |
| `try_flush(WriteHandle& target)` | `Result<Unit,IoError>`; request the declared flush boundary once. |
| `sync_durable(WriteHandle& target)` | `Result<Unit,IoError>`; require the provider's separately declared durable-sync capability. |
| `try_close(HandleOwner& owner)` | `Result<Unit,IoError>`; the close state machine in Section 2.5. |

Each shorter overload SHALL be a separate declaration binding the stated policy factory. An operation SHALL validate its live handle and span designation before provider access. An empty capability SHALL produce InvalidHandle; a live record outside Open SHALL produce Closed for new byte operations. A valid empty transfer SHALL succeed with zero and Data/Progress before cancellation acceptance.

try_read and try_write SHALL perform one immediate provider attempt. Nonempty Data/Progress SHALL carry positive transfer; EndOfInput SHALL represent definitive provider EOF. WouldBlock SHALL carry its already-transferred prefix when present. An Interrupted or other Err SHALL carry its prefix in IoError. Each transferred byte SHALL contribute to exactly one progress outcome. A nonempty successful write with zero count and a state other than WouldBlock SHALL produce WriteZero. Invalid provider counts or out-of-bounds access SHALL follow the provider-contract failure outlet.

### 2.4 Complete transfers and partial failure

read_exact SHALL publish Ok when the destination is full, with Data and the requested count. Earlier EOF SHALL produce UnexpectedEndOfInput, including zero-byte EOF. write_all SHALL publish Ok when every byte is accepted at the provider's write boundary, with Progress and the requested count. These normalized successful states SHALL apply to empty calls and to a completing attempt carrying another observational state. Persistence, remote delivery, and multiwriter transactions SHALL use their separately selected capabilities.

Each attempt SHALL address the remaining suffix. Counts SHALL use exact extent arithmetic bounded by the original extent. An ordinary Err SHALL preserve cumulative progress in transferred. Read destination bytes and accepted external writes SHALL remain observable. A selected higher-level replay SHALL use the retry/compensation model in Chapter 14 and Chapter 28.

After validation and the empty-extent check, the operation SHALL observe cancellation, then its deadline, before the first attempt, each further attempt, and each permitted wait. An already completed extent SHALL proceed directly to success. Observed cancellation SHALL select Cancelled before deadline testing; expiry SHALL select TimedOut. Poll SHALL select WouldBlock when progress requires waiting. Unbounded SHALL use the declared provider wait. Until SHALL use its exact clock identity; an unsupported deadline contract SHALL produce Unsupported before transfer admission.

A successful completing attempt SHALL commit success before later token/deadline observation. A provider Err SHALL preserve Err even when its count reaches the extent. Cancelled, TimedOut, WouldBlock, and Interrupted SHALL carry exact cumulative progress. Poll SHALL admit synchronous positive-progress attempts and return WouldBlock at the first wait requirement.

### 2.5 Flush, close, and control-record retirement

try_flush SHALL request the provider's flush boundary. sync_durable SHALL request its distinct durability boundary and produce Unsupported when that capability is absent. A flush failure SHALL preserve the owner's closure obligation and HandleState. A provider selecting destructive flush SHALL expose its owner-aware state transition through a separately named extension.

try_close SHALL transition Open to Closing, consume the closure obligation through the provider protocol, and transition to Closed. Pretransition validation/admission error SHALL preserve Open. Closing SHALL admit only continuation and already-admitted operations under the provider's quiescence/cancellation protocol. Success SHALL return Unit with Closed. Continuation SHALL resume the outstanding release steps with their committed consumption state.

Every close Err SHALL carry Some(Open), Some(Closing), or Some(Closed) matching state(). Open SHALL permit a fresh attempt after its obstruction is resolved. Closing SHALL permit continuation of the existing obligation. A Closed call SHALL return Closed with Some(Closed) through local state observation. Native finalization error after handle consumption SHALL therefore return Err with Closed. The control record SHALL preserve its closed identity across reuse of a native descriptor number.

Closed SHALL retain its control allocation until reset, owner replacement, or owner destruction. Retirement SHALL require quiescence and invalidate derived borrows. A conforming recoverable close provider SHALL report a determinate consumption state. A provider offering an indeterminate native close SHALL use its separately published contract or reject that capability before admission.

## 3. Paths, file acquisition, and seeking

### 3.1 Native path views and ownership

PathEncoding SHALL have Bytes, Utf8, and Utf16. NativePathView SHALL have borrowed cases Bytes(Span<const<byte>> units), Utf8(StringView text), and Utf16(Span<const<u16>> units). A valid path SHALL contain its explicit extent of nonzero code units. Bytes SHALL preserve native units; Utf16 SHALL preserve admitted unpaired native surrogates. Utf16 SHALL require enabled u16.

PathView SHALL be a copyable native-representation borrow with its ProviderIdentity, created through the factories below. It SHALL expose `encoding() -> PathEncoding`, `native() -> NativePathView`, and `provider_identity() -> ProviderIdentity`. Path SHALL own native units through a ResourceRef, with move-only ownership and an empty default/moved-from state. It SHALL expose `has_value() -> bool`, `view() -> PathView`, and `resource() -> Option<ResourceRef>`; view on empty SHALL select ContractTrap. `reset() -> void` and destruction SHALL release units and empty the owner. Move assignment SHALL retire the destination's storage before transfer and be nonthrowing under resource contracts. Views SHALL require live, unchanged source units.

| Operation in std::io | Result and contract |
| --- | --- |
| `try_path_view(ProviderRef provider, NativePathView units)` | `Result<PathView,IoError>`; validate native encoding/zero restrictions and borrow the original units. |
| `try_path(ProviderRef provider, NativePathView units, ResourceRef resource)` | `Result<Path,IoError>`; validate then copy exact native units into owned storage. |
| `try_path_from_utf8(ProviderRef provider, StringView text, ResourceRef resource)` | `Result<Path,IoError>`; perform the provider's declared strict Unicode-to-native conversion. |
| `try_path_to_utf8(PathView path, ResourceRef resource)` | `Result<String,IoError>`; strict conversion, InvalidInput at the first unrepresentable or ill-formed native sequence. |

Path conversions SHALL preserve the exact represented native text through their strict encoding mapping. Normalization, case folding, symlink resolution, and replacement-character conversion SHALL use separately named operations. A provider SHALL accept a PathView under its compatible path descriptor. Empty path storage SHALL use the provider's declared empty-path meaning. Relative-path resolution SHALL occur at the selected open operation.

### 3.2 Open options and acquisition

AccessMode SHALL have Read, Write, and ReadWrite; CreateMode SHALL have Existing, OpenOrCreate, CreateNew, and CreateOrTruncate; SymlinkPolicy SHALL have Follow and RejectFinal. SharePermission SHALL have Read, Write, and Delete. ShareMode SHALL be their nonallocating set, defaulting to empty and constructed from a permission as a singleton. It SHALL provide equality, `contains(SharePermission) -> bool`, `empty() -> bool`, and set operators |, &, ^, ~ and their compound assignment forms; complement SHALL range over those three permissions. OpenOptions SHALL contain AccessMode access, CreateMode create, bool append, SymlinkPolicy symlinks, and ShareMode share, supplied explicitly to its constructor.

CreateOrTruncate SHALL require write access and truncate an existing object. CreateNew SHALL atomically reject an existing final object through its selected provider capability. Append SHALL use the provider's append boundary for each write attempt. A requested capability, sharing restriction, or RejectFinal contract that the provider cannot honor SHALL produce Unsupported before acquisition. RejectFinal SHALL govern the final path component. A whole-write_all atomic append or ancestor-confinement policy SHALL use its separately declared capability.

| Operation | Result |
| --- | --- |
| `open(ProviderRef provider, PathView path, OpenOptions options, ResourceRef resource)` | `Result<HandleOwner,IoError>`; use the provider's declared relative-path resolution context. |
| `open_at(HandleOwner& directory, PathView relative_path, OpenOptions options, ResourceRef resource)` | Same; require a live compatible directory capability, and interpret the path relative to it. |

open and open_at SHALL admit control/storage support before external acquisition. A provider-side failure after native acquisition SHALL discharge the provisional handle before returning Err under its nonthrowing acquisition contract. The returned Err SHALL leave the caller's ownership set unchanged. open_at SHALL require a relative path and report InvalidInput for an absolute one. Parent-component confinement and filesystem-race guarantees SHALL belong to an explicitly selected provider extension.

### 3.3 Seeking

Offset SHALL alias enabled i64. SeekFrom SHALL have Start(Offset absolute), Current(Offset delta), and End(Offset delta). Start SHALL validate a nonnegative absolute position. Current and End SHALL compute their mathematical sum and validate a nonnegative representable result before requesting change. `try_seek(HandleOwner& owner,SeekFrom from) -> Result<Offset,IoError>` SHALL require Open and a seekable byte-addressed capability and return the resulting position.

The provider SHALL bind base-position observation and update under its synchronization contract. An ordinary seek Err SHALL preserve stream position. Successful seek SHALL change position while preserving file contents. Unsupported handles SHALL produce Unsupported. A provider with another failure guarantee or address unit SHALL expose a distinct position interface.

## 4. Formatting and numeric parsing

### 4.1 Format grammar and types

This section's namespace SHALL be std::io. FormatPlan SHALL be a copyable nonallocating borrow of immutable UTF-8 format bytes and their validated lexical plan, created by the listed factories. `pattern() -> StringView` SHALL expose the borrow. Literal plans SHALL borrow static literal storage; runtime plans SHALL require live, unchanged bytes. Physical plan storage and rescanning SHALL follow the core transformation model.

```ebnf
format-text = { plain-character | "{{" | "}}" | replacement };
replacement = "{", [ argument-selector ], [ ":", format-spec ], "}";
argument-selector = unsigned-decimal | format-identifier;
format-identifier = ( ascii-letter | "_" ),
                    { ascii-letter | ascii-digit | "_" };
format-spec = [ fill-align ], [ sign ], [ alternate ],
              [ width ], [ ".", precision ], [ presentation ];
fill-align = [ non-brace-unicode-scalar ], ( "<" | ">" | "^" );
sign = "+" | "-" | " ";
alternate = "#";
width = unsigned-decimal;
precision = unsigned-decimal;
presentation = "d" | "x" | "X" | "b" | "o" | "f" | "e" | "g" | "s";
```

An unsigned-decimal grammar value SHALL contain at least one ASCII digit and accumulate exactly within usize. Selectors SHALL use either automatic empty selectors or explicit numeric/name selectors for the whole plan. Explicit selectors SHALL permit repetition. Names SHALL be case-sensitive ASCII identifiers with unique supplied names. Escaped braces SHALL emit literal text and consume zero arguments. Unmatched braces and unsupported combinations SHALL use their declared format errors.

FormatErrorCode SHALL have InvalidSyntax, InvalidSelector, MissingArgument, UnusedArgument, DuplicateName, TypeMismatch, InvalidSpecifier, UnsupportedPolicy, SizeOverflow, LimitExceeded, BufferTooSmall, and AllocationFailure. FormatError SHALL contain FormatErrorCode code, Option<usize> pattern_position, Option<usize> argument_index, usize written, Option<usize> required, and Option<std::mem::AllocationError> allocation. Positions/counts SHALL be bytes except argument_index. Buffer-size errors SHALL carry the exact representable required count; overflow SHALL carry None. AllocationFailure SHALL carry Some(allocation); other cases SHALL carry None.

FormatResult SHALL contain usize written, usize required, and bool complete. FormatPolicy SHALL contain RoundingMode rounding and usize max_output_bytes. `default_format_policy() -> FormatPolicy` SHALL return NearestTiesEven and maximum usize. Each call SHALL bind that immutable policy. NamedArg<T> SHALL be a factory-created borrow with `value() -> const<T>&` and `name() -> StringView`; `named<T>(StringView name,const<T>& value) -> NamedArg<T>` SHALL return that borrow. Format binding SHALL validate names. Roundtrip<F> SHALL be a factory-created copyable stored representation with `value() -> F`; `roundtrip<F>(F value) -> Roundtrip<F>` SHALL copy the representation while preserving numeric status and signaling-NaN bits.

### 4.2 Formatting catalogue

The standard formatting domain SHALL consist of enabled fixed-width integers, bool, char, StringView, enabled scalar IEEE binary/decimal formats, their Roundtrip wrappers, and NamedArg wrappers of those types. Other types SHALL participate through an explicit conversion into that domain or a separately named provider extension.

| Operation | Result and contract |
| --- | --- |
| `compile_format(StringView literal)` | FormatPlan; the operand is required constant, and lexical errors are ERROR. Statically available binding errors are ERROR at a subsequent formatting call. |
| `try_format_plan(StringView pattern)` | `Result<FormatPlan,FormatError>`; validate grammar and borrow bytes. |
| `format_to(Span<byte> destination, FormatPlan plan, FormatPolicy policy, const<Args>&... arguments)` | `Result<FormatResult,FormatError>`; nontruncating output. |
| `format_to(Span<byte> destination, FormatPlan plan, const<Args>&... arguments)` | Same with default_format_policy(). |
| `format_prefix_to(Span<byte> destination, FormatPlan plan, FormatPolicy policy, const<Args>&... arguments)` | Same result type; allow a complete-scalar prefix. |
| `try_format(ResourceRef resource, FormatPlan plan, FormatPolicy policy, const<Args>&... arguments)` | `Result<String,FormatError>`; return a complete owned UTF-8 String. |

The argument pack SHALL be statically typed. Call evaluation SHALL evaluate each source expression once; formatting SHALL read its stable borrowed value. Providers SHALL measure and emit built-in representations under that borrow contract. User-defined formatting callbacks SHALL use their separately declared interface.

Binding SHALL validate syntax, selectors, duplicate names, presentation/type combinations, and unused arguments. Automatic selectors SHALL consume each supplied argument once in order; explicit selectors SHALL reference every supplied argument at least once. NamedArg SHALL retain its numeric pack index as well as its name. Invalid spelling SHALL produce InvalidSelector; an unbound selector, MissingArgument; a presentation from another argument category, TypeMismatch; an invalid modifier on an admitted presentation, InvalidSpecifier; malformed grammar, InvalidSyntax; and an oversized syntax quantity, SizeOverflow. Duplicate names SHALL be checked in pack order first, pattern errors in pattern order next, and unused arguments last. Successful binding SHALL precede measurement, usize/output-budget validation, and the selected output operation.

format_to SHALL return BufferTooSmall with written zero and an unchanged destination when capacity is insufficient. Success SHALL write exactly required bytes and preserve the unused tail. format_prefix_to SHALL apply the same preflight and limits; insufficient capacity SHALL produce Ok with complete false, exact required, and the longest whole-Unicode-scalar prefix. Other errors SHALL precede output and report written zero. try_format SHALL admit complete String storage through the supplied resource and publish that String on success. Inputs and destination SHALL satisfy a disjoint-storage precondition under the canonical diagnostic and contract policy.

A valid floating presentation SHALL require support for its requested runtime rounding policy. Absent support SHALL produce UnsupportedPolicy before measurement/output, with written zero and absent argument/pattern position except where a specific argument identifies the incompatibility. Integer/text-only calls SHALL bind only their used capabilities. Roundtrip SHALL use its fixed reconstruction direction. Policy rejection SHALL leave numeric status unchanged; static capability failures SHALL follow Chapter 08.

### 4.3 Scalar presentations and rounding

Width and string precision SHALL count Unicode scalar values. Default fill SHALL be ASCII space; numeric alignment SHALL default right and text/char/bool-word alignment left. Centering SHALL place an odd extra fill scalar on the right. Width SHALL be a minimum; text precision SHALL select its scalar prefix before padding. StringView and char SHALL admit omitted or s presentation with their text modifiers; char SHALL admit width/alignment and preserve its one-scalar content.

Fixed integers SHALL default to d; x, X, b, and o SHALL select radix 16, 16, 2, and 8. Signed output SHALL use mathematical sign and magnitude, including the minimum value. Alternate nondecimal form SHALL prefix 0x, 0X, 0b, or 0o after the sign. Integer precision SHALL set the minimum zero-filled digit count, with at least one digit for zero. Alternate decimal form SHALL produce InvalidSpecifier. Plus/space SHALL apply to nonnegative signed or unsigned values; default minus SHALL apply to negative values. Bool SHALL admit omitted/s word output true/false or d output 1/0, with width/alignment modifiers.

An ordinary floating argument SHALL default to g and precision six. f SHALL use precision digits after the point; e SHALL use that many digits after the leading digit and a signed exponent of at least two digits; g SHALL use precision significant digits, treating zero precision as one. g SHALL choose e when the rounded decimal exponent is below -4 or at least precision, otherwise f. Alternate form SHALL preserve the decimal point and requested fractional trailing zeros; ordinary g SHALL remove insignificant fractional trailing zeros. The formatter SHALL round the exact stored value directly to the decimal presentation under FormatPolicy while preserving numeric status. Negative zero SHALL retain its sign; finite nonnegative values SHALL use the requested plus/space policy.

Nonfinite output SHALL use inf, nan, and snan with the stored negative sign or requested plus/space sign. Width/alignment SHALL apply; precision/alternate SHALL preserve those words. Representation inspection SHALL preserve signaling state and numeric status. Roundtrip SHALL admit omitted presentation or g with width/alignment/sign modifiers, and emit an exact finite decimal representation, optional decimal exponent, and necessary leading zeros, recovering the same finite value and zero sign under NearestTiesEven in F. It SHALL use the same nonfinite words. NaN payload preservation SHALL use the wire-representation interface.

### 4.4 Numeric parser types and catalogue

ParseMode SHALL have Complete and Prefix; SpacePolicy SHALL have Reject and AsciiWhitespace, the latter recognizing bytes 09–0D and 20; SpecialValues SHALL have Reject and Canonical. ParseLimits SHALL contain positive usize max_digits and max_exponent_digits. IntegerParsePolicy SHALL contain u8 radix in 2..36, bool allow_radix_prefix, ParseMode mode, SpacePolicy space, and ParseLimits limits. FloatParsePolicy SHALL contain RoundingMode rounding, FPFlagSet error_mask, ParseMode mode, SpacePolicy space, SpecialValues special, and ParseLimits limits. Construction SHALL require every listed field.

ParseErrorCode SHALL have InvalidPolicy, UnsupportedPolicy, Empty, InvalidDigit, InvalidSyntax, TrailingInput, UnsupportedSpecial, and LimitExceeded. ParseError SHALL contain ParseErrorCode code, usize position, and usize consumed; offsets SHALL refer to original UTF-8 bytes. Parsed<T> SHALL contain T value and usize consumed and require the value operations actually used by T.

| Operation | Result |
| --- | --- |
| `parse_integer<I>(StringView input, IntegerParsePolicy policy)` | `Result<Parsed<NumericResult<I>>,ParseError>` for an enabled fixed integer I. |
| `parse_float<F>(StringView input, FloatParsePolicy policy)` | `Result<Parsed<NumericResult<F>>,ParseError>` for an enabled declared scalar float F. |

The outer Result SHALL report lexical/policy errors. A valid token SHALL produce outer Ok containing its NumericResult projection. Integer projection SHALL use exact range checking. Float projection SHALL round the exact decimal token directly to F and apply the explicit error mask to local status. Permitted infinity, zero, or subnormal output SHALL use numeric Ok with its flags; selected numeric failure SHALL use the existing NumericErrorCode/NumericStatus and the inactive-value contract. Numeric status publication SHALL follow Chapter 04's observed-operation contract. Lexical rejection SHALL preserve numeric status. These standard parsers SHALL use bounded nonallocating support for their declared formats/limits; an allocating provider alternative SHALL expose its explicit resource parameter through a separate extension.

parse_float SHALL validate policy domains, then requested rounding/format support, before scanning. Runtime unsupported rounding SHALL produce UnsupportedPolicy with position and consumed zero and unchanged numeric status. The error mask SHALL classify the operation's software-visible local status under its numeric contract. Static format availability SHALL follow the capability diagnostic rules.

Integer syntax SHALL be an optional ASCII sign and at least one radix digit; A–Z/a–z SHALL denote 10..35. An admitted 0b/0o/0x prefix SHALL match radix 2/8/16, otherwise InvalidSyntax. With prefix admission disabled, those bytes SHALL use ordinary digit/token-end processing. An unsigned target SHALL parse a negative token lexically and project its mathematical value, including representable negative zero. Finite float syntax SHALL be optional sign, digits and optional point with at least one digit overall, followed optionally by e/E, optional exponent sign, and at least one exponent digit. max_digits SHALL count significand/integer digits including zeros; max_exponent_digits SHALL count exponent digits separately. The first excess digit SHALL produce LimitExceeded. Zero limits or invalid radix SHALL produce InvalidPolicy at position zero before scanning.

Canonical specials SHALL accept case-insensitive inf, infinity, and nan with optional sign. nan SHALL form the signed canonical quiet NaN. Reject SHALL report UnsupportedSpecial. Complete SHALL consume the token and admitted surrounding ASCII whitespace through input end; Prefix SHALL return the first complete token's end, including leading whitespace and excluding trailing whitespace. A lone sign or incomplete started exponent SHALL produce InvalidSyntax. Error consumed SHALL identify the validated-prefix end; position SHALL identify the rejecting byte or premature input end. Empty input or admitted whitespace alone SHALL report Empty at input length. An initial invalid integer digit SHALL produce InvalidDigit; a later invalid byte SHALL end a Prefix token or produce TrailingInput in Complete. Special matching SHALL choose the longest complete admitted spelling. Constant evaluation SHALL preserve a valid numeric Err as an ordinary value.

## 5. Unicode operations

The namespace SHALL be std::text::unicode. UnicodeVersion SHALL contain u16 major, minor, and patch. ProviderRef SHALL be a nonempty immutable provider/table borrow with `version() -> UnicodeVersion`, created by its declared provider path. `default_provider() -> ProviderRef` SHALL return the provider pinned by the module contract. Each data revision and enabled operation capability SHALL form part of that contract.

NormalizationForm SHALL have NFC, NFD, NFKC, and NFKD. FoldMode SHALL have Default and Turkic, selecting the corresponding full Unicode case-fold mappings. BoundaryKind SHALL have Grapheme and Word. UnicodeErrorCode SHALL have Unsupported, InvalidBoundary, ResourceLimit, AllocationFailure, and ProviderMismatch. UnicodeError SHALL contain UnicodeErrorCode code, Option<usize> byte_position, and Option<std::mem::AllocationError> allocation. Input StringViews SHALL satisfy the core UTF-8 invariant. Folding and normalization SHALL each execute their separately selected operation.

| Operation | Result and behavior |
| --- | --- |
| `try_normalize(StringView input, NormalizationForm form, ResourceRef resource, ProviderRef provider)` | `Result<String,UnicodeError>`; the exact selected UAX #15 normalization. |
| `try_normalize(StringView input, NormalizationForm form, ResourceRef resource)` | Same with default_provider(). |
| `is_normalized(StringView input, NormalizationForm form, ProviderRef provider)` | `Result<bool,UnicodeError>`; no output allocation. |
| `try_casefold(StringView input, FoldMode mode, ResourceRef resource, ProviderRef provider)` | `Result<String,UnicodeError>`; full selected case folding. |
| `try_caseless_equal(StringView left, StringView right, FoldMode mode, ResourceRef scratch, ProviderRef provider)` | `Result<bool,UnicodeError>`; compare folded scalar sequences, without implicit normalization. |
| `segments(StringView input, BoundaryKind kind, ProviderRef provider)` | `Result<SegmentIterator,UnicodeError>`; borrow input and provider. |

Owned-output operations SHALL preserve source text on ordinary failure. Allocation errors SHALL identify the supplied resource failure. Caseless equality SHALL admit any bounded temporary storage through scratch and retire it before returning its boolean. Locale and path state SHALL remain unchanged by these text operations.

Segment SHALL contain StringView text, usize byte_offset, and usize byte_count. SegmentIterator SHALL be a factory-created copyable borrowed state with `next() -> Option<Segment>` and `byte_position() -> usize`. It SHALL use the pinned UAX #29 default extended-grapheme or word-boundary rules. Word mode SHALL return every interval, including punctuation/whitespace. Successful segments SHALL be nonempty and partition original bytes in order; empty input SHALL produce an exhausted iterator. Copy construction SHALL copy the cursor independently. Iteration SHALL use bounded nonallocating state admitted by its provider capability and retain the original input/provider borrow requirements.

A new iterator SHALL begin at byte position zero. Successful next SHALL advance to its segment end; exhaustion SHALL return None with position equal to input size on every later next. Source bytes and provider data SHALL remain unchanged during valid iteration. Source mutation SHALL invalidate the iterator state and require a newly constructed iterator for further traversal.

## 6. Clocks, durations, civil values, and zones

### 6.1 Time representations and identities

The namespace SHALL be std::time. TimeDimension and NanosecondScale SHALL alias canonical std::units::TimeDimension and std::units::NanosecondScale in [Chapter 31](31_units_interfaces.md#chapter-31-units-interfaces), denoting elapsed time and the exact 1/1000000000-second scale. Duration SHALL alias `std::units::Quantity<TimeDimension,i64,NanosecondScale>` and require enabled i64. Other Rep/Scale combinations SHALL remain generic time quantities. Construction, representation access, operations, and explicit scale conversion SHALL use Quantity's contract.

MonotonicClock and SystemClock SHALL be distinct empty descriptor types. ClockIdentity SHALL be a copyable opaque instance identity with equality and `fingerprint() -> byte[32]`; equality SHALL resolve known descriptor collisions. ClockRef<Clock> SHALL be a factory-created nonempty borrow with `identity() -> ClockIdentity`. Enabled hosted clock capabilities SHALL supply `host_monotonic_clock() -> ClockRef<MonotonicClock>` and `host_system_clock() -> ClockRef<SystemClock>`.

Instant<Clock> SHALL contain read-only ClockIdentity clock and i64 nanoseconds, with public construction from `(ClockRef<Clock> source,i64 nanoseconds)` copying source.identity(). Its library operations SHALL preserve validated identity as a value. Admissibility SHALL depend on both static Clock and dynamic instance identity. SystemClock SHALL use the provider's declared Unix/POSIX-style timeline with epoch 1970-01-01T00:00:00. MonotonicClock SHALL use its provider-defined elapsed-time origin. Storage SHALL represent integer nanoseconds; accuracy SHALL use ClockProperties.

ClockProperties SHALL contain bool monotonic, bool advances_during_suspend, Duration resolution, and Duration maximum_read_uncertainty, with positive resolution and nonnegative uncertainty. ClockReading<Clock> SHALL contain Instant<Clock> value and Duration uncertainty. Counter conversion SHALL round a finer native timeline toward negative infinity into integer nanoseconds and include its quantization uncertainty in the bound. The conversion SHALL preserve numeric status.

TimeErrorCode SHALL have InvalidValue, OutOfRange, ClockMismatch, Unsupported, ProviderUnavailable, AmbiguousLocalTime, NonexistentLocalTime, InvalidLeapSecond, UnknownZone, ResourceLimit, and AllocationFailure. TimeError SHALL contain TimeErrorCode code, Option<usize> position, Option<Instant<SystemClock>> earlier, Option<Instant<SystemClock>> later, and Option<std::mem::AllocationError> allocation. Ambiguous mappings SHALL supply representable candidate instants in order on one clock. Other cases SHALL use absent candidates. Position SHALL use the operation's stated byte or field-ordinal coordinate.

### 6.2 Clock operations and deadline bridge

| Operation | Result |
| --- | --- |
| `properties<Clock>(ClockRef<Clock> clock)` | ClockProperties, nonthrowing observation. |
| `try_now<Clock>(ClockRef<Clock> clock)` | `Result<ClockReading<Clock>,TimeError>`. |
| `try_add<Clock>(Instant<Clock> instant, Duration delta)` | `Result<Instant<Clock>,TimeError>`; exact checked nanosecond addition. |
| `try_difference<Clock>(Instant<Clock> later, Instant<Clock> earlier)` | `Result<Duration,TimeError>`; require identical dynamic clock identity. |
| `try_compare<Clock>(Instant<Clock> left, Instant<Clock> right)` | `Result<i32,TimeError>`; -1, 0, or 1 on identical identity. |
| `correlate(ClockRef<MonotonicClock> monotonic, ClockRef<SystemClock> system)` | `Result<ClockCorrelation,TimeError>`. |
| `project_system(ClockCorrelation correlation, Instant<MonotonicClock> value)` | `Result<SystemEstimate,TimeError>`. |
| `to_sync_deadline(ClockRef<MonotonicClock> source, Instant<MonotonicClock> value, std::sync::ClockRef target)` | `Result<std::sync::Deadline,TimeError>`; explicit bridge. |

ClockCorrelation SHALL contain Instant<MonotonicClock> monotonic, Instant<SystemClock> system, Duration uncertainty, and Duration valid_for. SystemEstimate SHALL contain Instant<SystemClock> value and Duration uncertainty. correlate SHALL return a sample pair, inclusive uncertainty bound, and nonnegative validity radius around the monotonic sample. The provider SHALL include sampling latency, quantization, and its promised drift/jump model over that radius; zero radius SHALL admit only the sample point. project_system SHALL require matching monotonic identity and an in-radius displacement, compute the exact sample offset plus displacement, and return the declared bound. Identity mismatch SHALL produce ClockMismatch; range failure SHALL produce OutOfRange.

The sync bridge SHALL bind an explicit mapping between the source instance and target synchronization clock. Deadline conversion SHALL round so reported expiry occurs at or after the represented instant. The mapping SHALL define wrap/epoch handling. Missing mapping SHALL produce Unsupported, arithmetic failure OutOfRange, and mismatched source ClockMismatch. The bridge SHALL return the deadline value under that mapping's contract.

### 6.3 Civil construction and time-zone data

CivilDate SHALL contain read-only i32 year, u8 month, and u8 day; CivilTime SHALL contain read-only u8 hour, minute, second and u32 nanosecond. Their public creation SHALL use the validating factories below. LocalDateTime SHALL be constructed from `(CivilDate date,CivilTime time)`. The calendar SHALL be proleptic Gregorian with years 1..9999: leap years divisible by four, except centuries unless divisible by 400. Calendar month/day ranges SHALL apply; hour SHALL be 0..23, minute/second 0..59, and nanosecond 0..999999999. Second 60 SHALL produce InvalidLeapSecond on this timeline. Leap-aware extensions SHALL publish their distinct timeline.

Construction errors SHALL use zero-based field order for position. `make_date(i32 year,u8 month,u8 day) -> Result<CivilDate,TimeError>` and `make_time(u8 hour,u8 minute,u8 second,u32 nanosecond) -> Result<CivilTime,TimeError>` SHALL validate in that order. LocalDateTime's `date()` and `time()` SHALL return its values nonthrowingly. These operations SHALL be pure nonallocating calendar transformations.

ZoneProviderRef SHALL be a nonempty immutable versioned-data borrow with `version() -> StringView` borrowing from that provider. `default_zone_provider() -> ZoneProviderRef` SHALL return the provider pinned by the module; an explicit integration SHALL supply its stated provider path. TimeZone SHALL be a factory-created copyable provider/name borrow with `name() -> StringView` and `provider() -> ZoneProviderRef`. `find_zone(ZoneProviderRef provider,StringView name) -> Result<TimeZone,TimeError>` SHALL perform exact case-sensitive lookup within that revision. UnknownZone SHALL use absent position. A local mapping SHALL contain zero, one, or two instants; larger provider-specific multiplicity SHALL produce Unsupported.

AmbiguousPolicy SHALL have Reject, Earlier, and Later; GapPolicy SHALL have Reject, ShiftForward, and ShiftBackward. LocalPolicy SHALL contain AmbiguousPolicy ambiguous and GapPolicy gap. Gap shifting SHALL add/subtract the exact gap duration to/from local fields, then resolve once under the same AmbiguousPolicy. A remaining gap SHALL produce NonexistentLocalTime; arithmetic range failure SHALL produce OutOfRange. ZonedLocal SHALL contain LocalDateTime local, i32 utc_offset_seconds, and bool is_later_occurrence.

| Operation | Result and behavior |
| --- | --- |
| `try_to_instant(LocalDateTime local, TimeZone zone, LocalPolicy policy, ClockRef<SystemClock> clock)` | `Result<Instant<SystemClock>,TimeError>`; resolve in the selected data revision and system timeline. |
| `try_to_instant(LocalDateTime local, TimeZone zone, LocalPolicy policy)` | Same using host_system_clock(); unavailable without that capability. |
| `to_local(Instant<SystemClock> instant, TimeZone zone)` | `Result<ZonedLocal,TimeError>`; require the zone provider to support that clock's epoch/timeline contract. |

Reject on an ambiguous mapping SHALL produce AmbiguousLocalTime with representable earlier/later candidates; an unrepresentable requested candidate SHALL produce OutOfRange. Reject on a gap SHALL produce NonexistentLocalTime. Earlier/Later SHALL select instant order. is_later_occurrence SHALL identify the later repeated occurrence and be false for a unique value. Conversion SHALL use the selected zone revision and clock contract. A valid CivilDate outside the Instant range SHALL produce OutOfRange. Calendar-period arithmetic SHALL retain its calendar interpretation across offset changes.

### 6.4 Canonical civil text

CivilParseMode SHALL have Complete and Prefix. CivilParseResult SHALL contain LocalDateTime value and usize consumed. `parse_local(StringView text,CivilParseMode mode) -> Result<CivilParseResult,TimeError>` SHALL accept `YYYY-MM-DDTHH:MM:SS` followed optionally by a dot and one through nine decimal digits, right-padded to nanoseconds. Complete SHALL require input end; Prefix SHALL return the complete token end. Invalid syntax SHALL produce InvalidValue at its rejecting byte; range failure SHALL use the field's first byte, with InvalidLeapSecond for second 60. A started fraction outside the one-to-nine-digit grammar SHALL be a syntax error.

`format_local_to(Span<byte> destination,LocalDateTime value) -> Result<usize,TimeError>` SHALL write the canonical local form, omitting a zero fraction and trimming other fractional trailing zeros. Success SHALL return the exact bytes written and preserve the remaining destination. Insufficient space SHALL produce OutOfRange with unchanged destination. A global instant SHALL be formatted through an explicit to_local operation and any separately selected offset/zone presentation.

## 7. Binary codec and record schemas

### 7.1 Values, errors, and primitive catalogue

The namespace SHALL be std::codec. Endianness SHALL have Little and Big. CodecErrorCode SHALL have InputTooShort, OutputTooSmall, InvalidEncoding, InvalidRepresentation, NonCanonical, OutOfRange, SizeOverflow, SchemaMismatch, DuplicateField, MissingField, UnknownField, InvalidLength, LimitExceeded, InvalidState, ResourceLimit, and AllocationFailure. CodecError SHALL contain CodecErrorCode code, usize consumed, usize written, Option<usize> position, Option<usize> required, Option<u32> field_tag, and Option<std::mem::AllocationError> allocation. Counts SHALL use the current public invocation's bytes; RecordWriter SHALL use its enclosing encoding invocation, and stream positions SHALL use the stated current-record coordinate. Encoding SHALL report consumed zero and decoding written zero. Decoded<T> SHALL contain T value and usize consumed.

CodecLimits SHALL contain positive usize max_record_bytes, max_field_bytes, max_fields, max_elements, and max_depth. Every field SHALL be explicit. Admission SHALL check the applicable limit before the corresponding work or storage. Fixed-width primitives SHALL use their type-determined extent and checked span capacity. An unrepresentable required extent SHALL produce SizeOverflow with required absent.

One top-level record SHALL own cumulative limit accounting. max_record_bytes SHALL count its header, framing, nested payloads, and terminator once per physical byte. max_field_bytes SHALL bound each field payload and array-element payload. max_fields SHALL count every reached occurrence, including repetitions and skipped unknowns. max_elements SHALL count recursively reached array elements, including empty elements; Bytes/Utf8 SHALL use byte bounds. The top Record SHALL have depth one; each known nested Record or Array SHALL add one, and primitive/Bytes/Utf8 values SHALL preserve depth. Skipped unknown payloads SHALL count their outer occurrence, length, and bytes as opaque data. Counters SHALL be admitted before corresponding work/storage/callbacks. Zero limits SHALL produce OutOfRange before input/output with position absent. Exhaustion of declared bounded work storage SHALL produce ResourceLimit before the affected work.

| Operation | Result and fixed behavior |
| --- | --- |
| `encode_integer<I>(I value,Span<byte> output,Endianness order)` | `Result<usize,CodecError>`; exactly N/8 octets for enabled fixed I whose width is divisible by eight. |
| `decode_integer<I>(Span<const<byte>> input,Endianness order)` | `Result<Decoded<I>,CodecError>`; consume exactly that width, leave later bytes unconsumed. |
| `encode_bool(bool value,Span<byte> output)` | Result byte count; exactly 00/01. |
| `decode_bool(Span<const<byte>> input)` | `Result<Decoded<bool>,CodecError>`; other octets InvalidRepresentation. |
| `encode_float<F>(F value,Span<byte> output,Endianness order)` | Result byte count; one format-tag byte followed by the exact stored-format bits. |
| `decode_float<F>(Span<const<byte>> input,Endianness order)` | `Result<Decoded<F>,CodecError>`; require exact format-tag and admissible representation. |
| `encode_varuint<U>(U value,Span<byte> output)` | Result byte count; canonical unsigned LEB128 for enabled fixed unsigned U. |
| `decode_varuint<U>(Span<const<byte>> input)` | `Result<Decoded<U>,CodecError>`; reject overlong or out-of-range values. |
| `encode_utf8(StringView value,Span<byte> output)` | Result byte count; canonical varuint byte length followed by unchanged UTF-8 content. |
| `decode_utf8(Span<const<byte>> input)` | `Result<Decoded<StringView>,CodecError>`; borrow validated content bytes. |

Result byte count SHALL mean Result<usize,CodecError>. Primitive encoders SHALL validate complete output capacity before writing; error SHALL preserve output with written zero. Decoders SHALL inspect octets and construct their output through normal value construction on success, permitting unaligned byte input. Signed integers SHALL use their exact N-bit two's-complement patterns. The standard integer domain SHALL consist of octet-multiple widths; explicit bit-packing extensions SHALL publish other width contracts.

Float tags SHALL be 1 Binary16, 2 BFloat16, 3 Binary32, 4 Binary64, 5 Binary128, 6 Decimal32BID, 7 Decimal32DPD, 8 Decimal64BID, 9 Decimal64DPD, 10 Decimal128BID, and 11 Decimal128DPD. Other tags SHALL produce InvalidEncoding. F's provider SHALL identify its single stored-format tag; a recognized mismatch SHALL produce InvalidRepresentation. Endianness SHALL apply to payload octets. Transport SHALL preserve admitted signed zeros, NaN sign/payload/signaling bits, decimal cohorts, and numeric status. A representation outside F's storage domain SHALL be rejected before F construction.

Canonical varuint SHALL emit seven-bit groups least significant first with continuation set on every nonfinal byte. Zero SHALL encode as 00; a multibyte final zero group SHALL produce NonCanonical when decoded. Excess significant bits SHALL produce OutOfRange; premature end SHALL produce InputTooShort. Error consumed SHALL count the examined prefix through its rejecting byte. UTF-8 length SHALL use the usize varuint domain; an excessive extent SHALL produce SizeOverflow or InputTooShort before view construction. Ill-formed text SHALL produce InvalidEncoding.

For U with N value bits, decoding SHALL examine at most ceil(N/7) bytes. Each group SHALL first be checked against remaining value bits. Excess bits SHALL select OutOfRange; a terminating zero group after the first SHALL select NonCanonical; a continuation on the last admitted group SHALL select OutOfRange. Earlier end SHALL select InputTooShort. Processing SHALL choose the first such condition in byte order and count the examined byte once. UTF-8 decoding SHALL validate the complete length and extent before text encoding, with positions measured from the original input start.

Primitive span/text encoders and RecordWriter.append SHALL support destination overlap with their supplied payload as if all payload bytes were read before any write. Their algorithm-owned dynamic scratch extent SHALL be zero. Schema metadata and callback/control objects SHALL remain live, immutable, and disjoint from writable output. Output writes SHALL invalidate affected text views under their core invariant. Scalar arguments SHALL be acquired before output writes under ordinary call evaluation.

### 7.2 Wire descriptors and schemas

SchemaIdentity SHALL contain byte[16] identifier and u32 version. WireKind SHALL have Unsigned, Signed, Float, Boolean, Bytes, Utf8, Record, and Array with tag octets 1 through 8. WireType SHALL be immutable metadata created by the following constructor alternatives:

- `Unsigned(usize bits,Endianness order)` and `Signed(usize bits,Endianness order)`: enabled positive octet-multiple widths;
- `Float(byte format_tag,Endianness order)`: one of the admitted tags above;
- `Boolean()`, `Bytes()`, and `Utf8()`;
- `Record(const<SchemaInfo>& schema)`;
- `Array(const<WireType>& element,usize maximum_count)`.

`kind() -> WireKind` SHALL observe the active alternative. Checked case matching SHALL expose its read-only fields. Descriptor borrows SHALL remain immutable and alive throughout use. The graph SHALL be finite and acyclic. Dynamic schema validation SHALL report InvalidEncoding for an invalid graph before encoding/decoding; required constant validation SHALL use its canonical diagnostic.

FieldSpec SHALL contain u32 tag, WireType type, bool required, bool repeated, usize min_bytes, and usize max_bytes. Tag SHALL be nonzero and min_bytes SHALL be at most max_bytes. Field arrays SHALL use strictly increasing tags. Required SHALL admit at least one occurrence; repeated SHALL admit consecutive multiple occurrences. UnknownFieldPolicy SHALL have Reject and Skip. SchemaInfo SHALL contain SchemaIdentity identity, Span<const<FieldSpec>> fields, and UnknownFieldPolicy unknown_fields, borrowing immutable graph metadata.

RecordView SHALL borrow one validated input record and SchemaInfo. It SHALL provide `schema() -> const<SchemaInfo>&`, `encoded_size() -> usize`, `count(u32 tag) -> usize`, `field(u32 tag,usize occurrence) -> Option<Span<const<byte>>>`, and `field_offset(u32 tag,usize occurrence) -> Option<usize>`. Offset SHALL identify the payload's first byte relative to this record; unknown or absent occurrences SHALL produce None. Access SHALL return validated bytes. Lookup SHALL use bounded nonallocating state and may rescan validated input.

Schema<T> SHALL be an immutable copyable borrowed descriptor constructed from `(const<SchemaInfo>& info, DecodeFactory<T> factory, EncodeVisitor<T> visitor)`. Callback identity, effects, and borrow contracts SHALL form part of its exported identity. DecodeFactory<T> SHALL be a callable pointer with signature `Result<T,CodecError>(RecordView,ResourceRef)` and construct an owning T independent of input bytes. EncodeVisitor<T> SHALL have signature `Result<Unit,CodecError>(const<T>&,RecordWriter&)` and emit T's selected fields. Both SHALL be synchronous call-scoped invocations with their declared language effects under Chapter 14.

`info() -> const<SchemaInfo>&` SHALL observe Schema<T>'s metadata. Null callbacks SHALL be invalid metadata and rejected before invocation. T SHALL be complete and satisfy its selected construction/destruction contracts. Distinct successful factory and delivery destinations SHALL require the applicable move construction; same-type prvalues SHALL use mandatory direct construction. Borrowed application views SHALL use RecordView and primitive decoders directly under their explicit source borrow.

### 7.3 Canonical record wire format

Each record SHALL use this framing:

1. Octets 43 58 4E 31, the ASCII bytes CXN1.
2. The 16 SchemaIdentity identifier bytes in their declared order.
3. The schema version as canonical unsigned varuint in the u32 domain.
4. Zero or more fields, each consisting of nonzero u32 varuint tag, one WireKind octet, usize varuint payload length, and exactly that many payload bytes.
5. A single canonical zero tag octet 00 ending the record, with no kind/length after it.

Tags SHALL be nondecreasing. Repeated known tags SHALL require repeated metadata. Skip SHALL admit consecutive unknown repetitions and count each occurrence. Every skipped field SHALL have valid ordering, recognized kind, canonical length, and available bytes, then remain outside schema-bound RecordView access. Reject SHALL produce UnknownField. A known field SHALL match kind/length bounds and recursively validate its WireType before factory invocation. Missing required fields, repeated nonrepeated fields, and mismatched schema identity/version SHALL produce their corresponding errors.

Unsigned/Signed/Float/Boolean SHALL use their primitive payload encodings. Bytes SHALL contain its exact octets; Utf8 SHALL contain its exact UTF-8 content. Record SHALL contain exactly one complete nested CXN1 record. Array SHALL contain a canonical usize varuint count followed by each element's canonical usize varuint length and exact WireType payload. Each enclosing payload SHALL end after its final specified component. Count/depth SHALL satisfy descriptor and CodecLimits bounds.

### 7.4 Record operations and writer

| Operation | Result and behavior |
| --- | --- |
| `decode_record<T>(const<Schema<T>>& schema,Span<const<byte>> input,ResourceRef resource,CodecLimits limits)` | `Result<Decoded<T>,CodecError>`; validate one complete record, then invoke its factory exactly once. |
| `encode_record<T>(const<Schema<T>>& schema,const<T>& value,Span<byte> output,CodecLimits limits)` | `Result<usize,CodecError>`; encode one record, including its terminator. |

decode_record SHALL validate framing, limits, metadata, every field payload, and required fields before its one factory invocation. Decoded.consumed SHALL end after the terminator and leave following bytes unconsumed. A factory Err SHALL keep T unpublished and use ordinary temporary retirement. User construction, callback, and retirement failures SHALL follow their declared language routes and Chapter 14's guarantee coverage.

RecordWriter SHALL be an immovable scoped borrow supplied during EncodeVisitor. `append(u32 tag,Span<const<byte>> payload) -> Result<Unit,CodecError>` SHALL validate next tag, repetition, kind/length, payload, and complete capacity before committing that field. `written() -> usize` SHALL return committed output bytes. Payload borrowing SHALL last through append. After metadata/limit validation and header-capacity admission, encoding SHALL commit the complete header and invoke its visitor once. The visitor SHALL append schema-admitted fields during its call-scoped writer borrow. An undersized header SHALL produce OutputTooSmall with written zero before visitor invocation. Successful visitor completion, required-field validation, and final capacity admission SHALL precede terminator commitment.

Record encoding SHALL preserve its committed header/field prefix on later error and report that prefix in written. A failed append SHALL preserve its output interval, cursor, last-tag state, occurrence/required-field accounting, and limit counters, with the error describing the enclosing prefix. The callback SHALL be permitted to handle that error and attempt another admitted append. A subsequently valid visitor result SHALL continue normal finalization. Destination-wide transactional encoding SHALL use explicitly supplied staging and a separately selected commit operation. Nested-record and array payload preparation SHALL use caller-supplied bytes or its selected explicit resources.

The enclosing invocation SHALL own progress counters. A factory CodecError SHALL be normalized to consumed equal to the validated record extent and written zero. A visitor CodecError SHALL be normalized to consumed zero and written equal to committed output. Callback position SHALL use the enclosing coordinate; forwarding a nested position SHALL translate once through field_offset. An out-of-range position SHALL become absent. required SHALL remain present only for a known minimum total extent in the same invocation; otherwise it SHALL become absent. Meaningful code, field, and allocation detail SHALL be preserved. Recursive validation SHALL translate positions/extents once with exact arithmetic; unrepresentable extent SHALL produce SizeOverflow and absent required. Input-end position SHALL be admitted for a premature-end error.

### 7.5 Incremental record decoding

DecoderState SHALL have Ready, Collecting, Failed, and Closed. RecordDecoder<T> SHALL be a move-only owner of buffered storage and a value copy of the borrowed Schema<T> descriptor. Its copied metadata/code borrows SHALL retain their ordinary lifetimes. `make_decoder<T>(const<Schema<T>>& schema,ResourceRef resource,CodecLimits limits) -> Result<RecordDecoder<T>,CodecError>` SHALL validate the descriptor, admit state, and return Ready. Buffer growth SHALL remain within max_record_bytes and be charged before byte acceptance. Admission error SHALL preserve existing buffer and Ready/Collecting state, reporting zero consumption from the new feed.

FeedResult<T> SHALL have NeedInput(usize consumed), Value(usize consumed,T value), and End(usize consumed). `feed(Span<const<byte>> bytes,bool end_of_input) -> Result<FeedResult<T>,CodecError>` SHALL copy an admitted prefix and produce at most one T. A complete record SHALL invoke its owning factory once, prepare Value, and finish required factory-result/temporary retirement before publication. Success commit SHALL consume that buffered record, empty the logical input buffer, and set Ready. Trailing supplied bytes SHALL remain unconsumed. Delivered T SHALL have ownership independent of decoder input storage.

An incomplete record with more input expected SHALL return NeedInput and Collecting. Empty Ready with end_of_input SHALL return End(0) and remain Ready. Incomplete Collecting at end SHALL produce InputTooShort and Failed. A framing/limit/factory Err SHALL leave Failed with accepted input and unpublished T. Error consumed SHALL count new bytes accepted in that feed; position SHALL use the current buffered-record start. A catchable failure during factory, delivery construction, or prepublication retirement SHALL leave Failed on the continuing cleanup path, retain its accepted prefix, retire completed temporary output, and propagate. Terminal events SHALL select their terminal protocol.

`state() -> DecoderState` and `buffered_bytes() -> usize` SHALL be nonthrowing observations. `reset() -> void` SHALL require a quiescent Ready/Collecting/Failed decoder, clear logical content, and set Ready while retaining capacity. `close() -> void` SHALL require quiescence, release storage/state, and set Closed; an already Closed call SHALL preserve Closed. Reset on Closed SHALL select ContractTrap. Destruction SHALL close its storage ownership. Default and moved-from states SHALL be Closed. Move construction SHALL transfer ownership; move assignment SHALL require Closed destination and quiescent source/destination; self-move SHALL preserve state. Feed on Closed or Failed SHALL produce InvalidState with zero consumption. Each successful publication SHALL consume its unique buffered record before further calls.

A decoder SHALL admit one active feed. Move, reset, close, and destruction SHALL require quiescence, including when invoked from the factory. Cross-agent access SHALL satisfy its synchronization contract. Read-only observers SHALL expose the current defined state. Invalid activity/ownership transitions SHALL use the canonical checked-contract diagnostic and failure policy. Every returning feed error SHALL normalize consumed to newly accepted bytes and position to the current-record coordinate.

## 8. Hosted arguments, environment, and exit

The namespace SHALL be std::process. ProcessProviderIdentity SHALL be an opaque versioned process/encoding identity with equality and `fingerprint() -> byte[32]`; collision resolution SHALL use the full descriptor. ProviderRef SHALL be a nonempty trivial borrow with `identity() -> ProcessProviderIdentity`. The selected `host_provider() -> ProviderRef` or explicit freestanding integration SHALL supply the provider through its declared creation path.

NativeTextView SHALL have borrowed cases Bytes(Span<const<byte>> units,ProviderRef encoding_provider), Utf8(StringView text), and Utf16(Span<const<u16>> units). Matching SHALL expose the selected fields. Bytes SHALL carry its provider's native encoding relationship; Utf8 SHALL retain its validated invariant; Utf16 SHALL preserve native code units including admitted unpaired surrogates. Each value SHALL retain its declared encoding identity and borrow.

ProcessErrorCode SHALL have Bounds, InvalidName, InvalidEncoding, Unsupported, PermissionDenied, InvalidState, ResourceLimit, and AllocationFailure. ProcessError SHALL contain ProcessErrorCode code, Option<ProcessProviderIdentity> provider, Option<usize> position, Option<usize> native_code, and Option<std::mem::AllocationError> allocation. Position SHALL count input bytes, including UTF-16 code-unit bytes. A present native code SHALL require its provider identity; pure encoding errors SHALL use the relevant absent detail.

Args SHALL be the copyable borrowed startup sequence supplied to hosted main and remain valid through main under the startup contract. It SHALL expose `size() -> usize`, `empty() -> bool`, `provider() -> ProviderRef`, and `try_at(usize index) -> Result<NativeTextView,ProcessError>`. Valid indexing SHALL return a borrow in the startup encoding; invalid indexing SHALL produce Bounds with that index as position.

| Operation | Result and behavior |
| --- | --- |
| `try_to_utf8(NativeTextView text,ResourceRef resource)` | `Result<String,ProcessError>`; strict conversion under its represented native encoding contract. |
| `environment_get(ProviderRef provider,NativeTextView name)` | `Result<Option<NativeTextView>,ProcessError>`; None means absent, Some(empty) means present and empty. |
| `environment_set(ProviderRef provider,NativeTextView name,NativeTextView value)` | `Result<Unit,ProcessError>`; explicit native-unit mutation. |
| `environment_remove(ProviderRef provider,NativeTextView name)` | `Result<bool,ProcessError>`; true only if an existing variable was removed. |
| `exit_immediately(i32 status)` | never; enter the selected immediate target-exit protocol with its hosted status mapping. |

try_to_utf8 SHALL use Bytes' encoding_provider strict conversion, producing Unsupported when that conversion capability is absent. Utf8 input SHALL copy its validated bytes. Utf16 SHALL validate surrogate pairs and produce InvalidEncoding at the first invalid pair. Conversion SHALL preserve exact mapped text through the supplied resource. All source/provider borrows SHALL remain alive through use.

An environment name SHALL be nonempty and use native units other than zero and =, plus its provider's declared restrictions. Values SHALL use nonzero native units. Encoding incompatibility SHALL produce InvalidEncoding/Unsupported before mutation. An ordinary set/remove Err SHALL preserve environment and existing views. Success SHALL invalidate all earlier environment borrows from that provider, including a successful equal-value set or remove(false). External native mutation SHALL use the provider's corresponding synchronization/invalidation contract. A get borrow SHALL remain valid through that interval; independent ownership SHALL use explicit copying/conversion.

ProcessExitStatus SHALL have Exited(i32 code), Signaled(usize native_signal), and Other(usize native_status), representing provider-observed completion. exit_immediately SHALL accept the requested integer code and apply the target's published host mapping. Normal return from main SHALL use ordinary image shutdown. Process acquisition and joining SHALL belong to separately published provider interfaces.

## 9. Span-based algorithms

### 9.1 Catalogue and value contracts

The namespace/module SHALL be std::algorithm / std.algorithm. This catalogue SHALL operate on live objects through Span. Containers SHALL participate through their explicit span/view interface. Text iteration SHALL retain its separate core-text contract.

AlgorithmError SHALL have Bounds(usize required,usize available), Unordered(usize index), and Allocation(std::mem::AllocationError detail). Required type operations SHALL be generic constraints. Comparators and predicates SHALL be forwarding borrows, invoked synchronously as lvalues for the call duration. Rvalue callable arguments SHALL be borrowed for that same interval. Their parameter categories and results SHALL follow the catalogue; effects SHALL use their captured callable contract.

| Operation | Result, constraints, and traversal |
| --- | --- |
| `for_each<T>(Span<T> values,forward F action)` | void; invoke action(T&) once per element in ascending index order. A read-only span supplies const<T>&. |
| `find_if<T>(Span<const<T>> values,forward P predicate)` | `Option<usize>`; predicate(const<T>&)->bool, stop at the first true in ascending order. |
| `count_if<T>(Span<const<T>> values,forward P predicate)` | usize; predicate(const<T>&)->bool once per element in ascending order. |
| `equal<T,U>(Span<const<T>> left,Span<const<U>> right,forward E equivalent)` | bool; equivalent(const<T>&,const<U>&)->bool; unequal lengths return false without a callback; otherwise compare corresponding elements in order until first false. |
| `lower_bound<T,K>(Span<const<T>> values,const<K>& key,forward C less)` | usize insertion index in 0..size; less(const<T>&,const<K>&)->bool and the required partitioned input. |
| `try_copy<T>(Span<const<T>> source,Span<T> destination)` | `Result<usize,AlgorithmError>`; copy-assign exactly source.size live destination objects; require copy assignment. |
| `fill<T>(Span<T> destination,const<T>& value)` | void; copy-assign each element in ascending order from the live borrowed value. |
| `sort<T>(Span<T> values,forward C less)` | void; less(const<T>&,const<T>&)->bool establishes a strict weak order; unstable ascending sort, in-place without algorithm-owned dynamic allocation. |
| `try_stable_sort<T>(Span<T> values,forward C less,ResourceRef resource)` | `Result<Unit,AlgorithmError>`; the same comparator contract as sort, preserving equivalent-element order with explicit temporary storage. |
| `sort_total<F>(Span<F> values)` | void; scalar floating ascending order induced by the selected nonraising total-order representation contract. |
| `sort_numeric<F>(Span<F> values)` | `Result<Unit,AlgorithmError>`; reject the first NaN before any rearrangement, then order numerical values. |
| `fold_left<T,A>(Span<const<T>> values,A initial,forward F combine)` | A; combine(A&&,const<T>&)->A, one invocation per element in ascending order. |

Span overloads SHALL preserve element qualification. Arbitrary T SHALL supply the required comparator explicitly. Each element SHALL designate a live object throughout the interface's permitted lifetime transitions. Spare capacity/raw storage construction SHALL use the corresponding memory interface.

### 9.2 Failure, overlap, and ordering

try_copy SHALL check capacity before assignment. Insufficient capacity SHALL produce Bounds(source.size,destination.size) with unchanged destination. Identical starting designation SHALL preserve the already-equal prefix. Partial overlap SHALL select ascending assignment when destination begins earlier and descending assignment when it begins later, preserving each original source value until read. Distinct ranges SHALL use their designation relation. Overlap handling SHALL use zero algorithm-owned dynamic storage and preserve the destination tail. User-assignment failure SHALL have the basic guarantee with completed assignments retained. fill SHALL read its live borrowed value at each ascending assignment, including the actual sequenced behavior of a value aliasing the destination.

Sorting SHALL require T movement, assignment, and destruction contracts preserving valid live objects and exclusive ownership on admitted failures. Comparator borrows SHALL keep keys, structure, and ordering relation stable throughout the operation. The algorithm SHALL choose comparator order within its result and complexity guarantees. A callback failure SHALL retain the basic guarantee and required temporary retirement on a continuing cleanup path. Destruction failure SHALL follow its selected boundary.

try_stable_sort SHALL admit temporary storage before element mutation. Admission failure SHALL produce Allocation with unchanged input. Accounting SHALL include simultaneously live original and temporary storage. Later element/comparator failures SHALL use their declared effects and the basic guarantee. Successful return SHALL follow temporary object retirement and release of its charge.

sort_total SHALL use `total_order(x,y) && !total_order(y,x)` from the canonical non-strict representation order and preserve signaling representations and numeric status while comparing. sort_numeric SHALL scan representations in ascending order first; the first NaN SHALL produce Unordered(index) with unchanged input and numeric status. Validated finite values/infinities SHALL use numerical order with equivalent signed zeros and unchanged Invalid status. Their relative equivalent-element order SHALL be selected by the unstable algorithm. Concurrent use SHALL preserve validation's lifetime and synchronization obligations.

Rearrangement SHALL preserve the live range extent and establish its selected positional values. An operation ending/reconstructing element generations SHALL invalidate affected borrows according to T's lifetime contract. Read-only traversal SHALL preserve views. Copy/fill assignment SHALL preserve object lifetime except for an explicitly admitted user assignment lifetime action, which SHALL use its own transition rules.

fold_left SHALL move the explicit initial value into its accumulator, invoke combine once per element in ascending order, construct each next accumulator before retiring the previous one, and publish the final A after required cleanup. A SHALL require move construction and destruction. Empty input SHALL return the admitted initial value through its ordinary return contract. Callback/move/retirement failure SHALL retain already completed consumption and follow its own route. The sequenced invocation and accumulator-retirement order SHALL remain part of this interface under every numeric profile.

### 9.3 Complexity and resource bounds

Excluding callback/element-operation cost and selected validation instrumentation, for_each/count/fill/copy SHALL use O(n) operations; find/equal SHALL use O(n) worst-case and their stated early stop; lower_bound SHALL use at most floor(log2(n))+1 comparator calls for n>0 and zero for n=0; fold SHALL invoke combine exactly n times. Count arithmetic SHALL remain exact within the admitted extent.

sort, sort_total, and sort_numeric SHALL use worst-case O(n log(n+1)) comparisons/moves, O(log(n+1)) automatic control storage, and zero algorithm-owned dynamic storage. try_stable_sort SHALL use O(n log(n+1)) comparisons/moves, at most O(n) temporary elements and O(log(n+1)) control storage, charging dynamic storage to its supplied resource. Element/callback operations SHALL use their own captured resource plans and effects. The provider resource descriptor SHALL publish constants and exact temporary-byte requests relevant to admission. Failure guarantees SHALL be those in Section 9.2.

This catalogue SHALL execute its serial callback protocol. A separately named parallel extension SHALL publish executor, resource, cancellation, partition, failure, and reduction-tree contracts. Ordinary Native arithmetic inside a callback SHALL follow that callback's captured numeric profile; explicit representation-order and sequenced-reduction contracts in this chapter SHALL retain their stated observations.

## 10. Capability, effect, and compatibility requirements

Each enabled exported operation SHALL publish the signature, constraints, capabilities, provider identity, public layout, effects, ownership, progress, and resource contract required by Chapter 14. Actual operation uses SHALL bind the required optional capabilities. Native linkage SHALL use the selected target ABI, while source contract compatibility SHALL use its separately captured library descriptor.

