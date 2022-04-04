# tino

### Description

_**T**ino **I**s **N**ot **O**bfuscator_

C++20 source code scanner to replace C++ keywords and identifiers with `_`. This was done in less than 1 day.

What works:

- Most of C++ features
- `#define`, `#include`, ... macros exclusion.
- `//` inline comments

What doesn't work:

- Multi-line macros
- Multi-line comments
- Variable names with only underscore (causes conflict)
- _Some edge cases that I didn't have time to figure out_


> This program was originally designed to generate valid file for challenge `tino` in UMassCTF 2022.

### License

MIT License.
