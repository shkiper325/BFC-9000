# BFC-9000
Translator of brainfuck code to AT&amp;T assembler.

Use compile.py to get the job done.
Options:

>--bf-code *filename*

If *filename* is empty or not specified, translator reads code from **stdin** until "!" is reached; else, code is loaded from the file named *filename*.

>--out *filename*

File to save result code in. Default name is "out.s".

To compile resulting code with gcc, use

> gcc -m32 code_file.s -o prgram_file

Pipeline sample is shown in test.sh. For demonstration put some brainfuck code to file "code.bf" and run "sh test.sh".

From v0.1.1 gcc is replaced with clang

TODO:
- [ ] Add correctness check to translator (same amount of "[" and "]")
- [ ] More tests on nested interpretators
- [ ] Migrate to nasm for x64 platform
- [ ] Add no-OS start from GRUB for nasm and x64
- [ ] Add compilation to ARM assembler
- [ ] Add Raspberry Pi no-OS support
- [ ] Run Bad Apple on PC and Raspberry Pi without OS
- [ ] Add Windows support
- [ ] Optimizations!

BFC-9000 ignores any symbols instead brainfuck symbols. Encoding is ASCII.

Version history:
- v0.1: Raw script provided.
- v0.1.1: Testing '+' sum optimization