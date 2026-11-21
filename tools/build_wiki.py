#!/usr/bin/env python3
"""Build CPN26 GitHub Wiki pages from the normative CPN26 spec tree."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = [
("01_language_lifecycle","Language-and-Lifecycle","Language and Object Lifetime"),
("02_integer_bigint","Integers-and-BigInt","Integers and BigInt"),
("03_floating_exact","Floating-and-Exact-Numerics","Floating and Exact Numerics"),
("04_numeric_integration","Numeric-Integration","Numeric Integration"),
("05_complex_arithmetic","Complex-Arithmetic","Complex Arithmetic"),
("06_construction_execution","Construction-and-Destruction","Construction and Destruction"),
("07_numeric_expressions","Numeric-Expressions","Numeric Expressions"),
("08_runtime_configuration","Configuration","Configuration and Presets"),
("09_native_interoperability","Native-Interoperability","Native Interoperability"),
("10_types_functions_generics","Types-Functions-and-Generics","Types, Functions, and Generics"),
("11_modules_compilation","Modules-and-Compilation","Modules and Compilation"),
("12_core_memory_control","Memory-and-Control","Core Memory and Control"),
("13_concurrency_memory_model","Concurrency-and-Memory-Model","Concurrency and the Memory Model"),
("14_standard_library","Standard-Library","Standard Library"),
("15_grammar_binding","Grammar-and-Binding","Grammar and Binding"),
("16_library_interfaces","Library-Interfaces","Library Interfaces"),
("17_concurrency_interfaces","Concurrency-Interfaces","Concurrency Interfaces"),
("18_mathematical_functions","Mathematical-Functions","Mathematical Functions"),
("19_extended_standard_library","Extended-Standard-Library","Extended Standard Library"),
("20_target_abi_profiles","Target-ABI-Profiles","Target ABI Profiles"),
("21_abstract_machine_and_conformance","Abstract-Machine-and-Conformance","Abstract Machine and Conformance"),
("22_static_reflection","Static-Reflection","Static Reflection"),
("23_compile_time_generation","Compile-Time-Generation","Compile-Time Generation"),
("24_contracts_and_effects","Contracts-and-Effects","Contracts and Effect Signatures"),
("25_effect_composition_and_boundaries","Effect-Composition-and-Boundaries","Effect Composition and Boundaries"),
("26_advanced_generic_families","Advanced-Generic-Families","Advanced Generic Families"),
("27_constraint_solver_and_inference","Constraint-Solving-and-Inference","Constraint Solving and Inference"),
("28_error_and_recovery","Error-and-Recovery","Error and Recovery"),
("29_public_contract_schemas","Public-Contract-Schemas","Public Contract Schemas"),
("30_reference_target_bindings","Reference-Target-Bindings","Reference Target Bindings"),
("31_units_interfaces","Units-and-Quantities","Units and Quantities"),
("32_numeric_resource_interfaces","Numeric-Resource-Interfaces","Numeric Resource Interfaces"),
]
GROUPS = [
("Core-Language","Core Language and Object Model",[1,6,10,12,15,21]),
("Numerics-and-Mathematics","Numerics and Mathematics",[2,3,4,5,7,18,31,32]),
("Configuration-Modules-and-ABI","Configuration, Modules and ABI",[8,9,11,20,29,30]),
("Concurrency-and-Libraries","Concurrency and Standard Libraries",[13,14,16,17,19]),
("Reflection-and-Generics","Reflection, Generation and Advanced Generics",[22,23,26,27]),
("Contracts-and-Recovery","Contracts, Effects and Recovery",[24,25,28]),
]
def main():
    dest=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/"wiki-pages"
    dest.mkdir(parents=True,exist_ok=True)
    def link(i): return f"{i:02d}-{CHAPTERS[i-1][1]}"
    titles={i:t for i,(_,_,t) in enumerate(CHAPTERS,1)}
    files={f"{x}.md":link(i) for i,(x,_,_) in enumerate(CHAPTERS,1)}
    ownership={i:(s,t) for s,t,ns in GROUPS for i in ns}
    assert len(ownership)==32
    def write(name,body): (dest/(name+".md")).write_text(body,encoding="utf-8")
    for i,(source,_,title) in enumerate(CHAPTERS,1):
        txt=(ROOT/"spec"/(source+".md")).read_text(encoding="utf-8")
        def repl(m): return "]("+files[m.group(1)]+(m.group(2) or "")+")"
        txt=re.sub(r"\]\((\d\d_[a-z0-9_]+\.md)(#[A-Za-z0-9_-]+)?\)",repl,txt)
        if i==22:
            txt=txt.replace("](#51-owner-authorized-member-access)","](23-Compile-Time-Generation#51-owner-authorized-member-access)")
        topic,group=ownership[i]
        top=f"[Home](Home) · [{group}]({topic}) · [All chapters](Home#chapters)\n\n"
        nav="\n\n---\n\n**Navigation:** "
        if i>1: nav+=f"[Previous: {titles[i-1]}]({link(i-1)}) · "
        nav+="[Home](Home)"
        if i<32: nav+=f" · [Next: {titles[i+1]}]({link(i+1)})"
        write(link(i),top+txt.rstrip()+nav+"\n")
    home="# CPN26 Language Wiki\n\nCPN26 is the **only standard edition** of the CPN language in this repository. This Wiki presents all 32 normative chapters with topic-based navigation.\n\n"
    home+="[Consolidated standard](https://github.com/MuXue1230-owo/CPN/blob/CPN26/CPN26.md) · [Chapter sources](https://github.com/MuXue1230-owo/CPN/tree/CPN26/spec)\n\n## Topics\n\n"
    sidebar="# CPN26\n\n[Home](Home)\n\n"
    for topic,title,nums in GROUPS:
        home+=f"- [{title}]({topic})\n"
        sidebar+=f"**[{title}]({topic})**\n\n"
        body=f"# {title}\n\n[Home](Home) · CPN26\n\n"
        for i in nums:
            body+=f"- [Chapter {i:02d} — {titles[i]}]({link(i)})\n"
            sidebar+=f"- [{i:02d}. {titles[i]}]({link(i)})\n"
        body+="\n[Back to Home](Home)\n"
        sidebar+="\n"
        write(topic,body)
    home+="\n## Chapters\n\n"
    for topic,title,nums in GROUPS:
        home+=f"### [{title}]({topic})\n\n"
        for i in nums:home+=f"- [Chapter {i:02d} — {titles[i]}]({link(i)})\n"
        home+="\n"
    write("Home",home)
    write("_Sidebar",sidebar)
    write("_Footer","**CPN26 Language Standard** · [Home](Home) · [Source](https://github.com/MuXue1230-owo/CPN/tree/CPN26)\n")
    print(f"Generated 41 Wiki pages in {dest}")
if __name__=="__main__": main()
