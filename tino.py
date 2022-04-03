import re
from os import environ
from pprint import pprint
from random import shuffle
from sys import argv
from typing import Callable


class Norm:
    def __init__(self, rep: str):
        self.rep = rep

    def code(self):
        return self.rep


class ObfuscatedEntry:
    def __init__(self, h: int):
        self.h = h
        self.repeat = 0

    def inc(self):
        self.repeat += 1


class Obfuscator:
    def __init__(self, transform: Callable[[int], str]):
        self.transform = transform
        self.dictionary: dict[Norm, ObfuscatedEntry] = {}

    def assign(self, entry):
        idx = len(self.dictionary) + 1
        self.dictionary[entry] = ObfuscatedEntry(idx)

    def update_or_insert(self, entry):
        if entry in self.dictionary.keys():
            self.dictionary[entry].inc()
        else:
            self.assign(entry)

    def compact(self):
        clone = list(self.dictionary.items())
        shuffle(clone)
        dump = sorted(clone, key=lambda x: x[1].repeat, reverse=True)
        idx = 1
        for entry in dump:
            entry[1].h = idx
            idx += 1
        self.dictionary = dict(dump)

    def fmt(self, token: str):
        return self.transform(self.dictionary[token].h)


class Scanner:
    ops = [
        "...",
        "<=>",
        "->",
        "<<",
        ">>",
        ">=",
        "<=",
        "!=",
        "==",
        "+=",
        "-=",
        "/=",
        "*=",
        "^=",
        "&=",
        "|=",
        "++",
        "--",
        "<",
        ">",
        ";",
        "(",
        ")",
        "::",
        ":",
        "{",
        "}",
        "[",
        "]",
        ",",
        ".",
        "?",
        "~",
        "+",
        "-",
        "*",
        "/",
        "^",
        "&&",
        "||",
        "&",
        "|",
        ",",
        "=",
        "!",
        "%"
    ]
    r_word = r'".*?"[_\w]*|\w+|'
    p_word = re.compile(r_word)
    r_char = r"'.+'"
    p_char = re.compile(r_char)
    r_spacing = r"[\s\n\t\r]*"
    p_spacing = re.compile(r_spacing)
    r_exception = r"#.*"
    p_exception = re.compile(r_exception)

    def __init__(self) -> None:

        notfirst = False
        self.r_ops = r"|".join([re.escape(op) for op in self.ops])
        self.p_ops = self.r_ops

        self.r = (
            self.r_spacing
            + r"//.*|"
            + r"("
            + r"|".join([self.r_word, self.r_char, self.r_ops, self.r_exception])
            + r")"
            + self.r_spacing
        )
        self.p = re.compile(self.r)

    def run(self, text: str) -> list[str]:
        return [t for t in self.p.findall(text) if t != ""]


def parser(tokens: list[str]) -> Obfuscator:
    core = Obfuscator(lambda x: "_" * x)
    for token in filter_source(tokens):
        core.update_or_insert(token)
    core.compact()
    return core


def filter_source(tokens: list[str]) -> list[str]:
    return [token for token in tokens if not Scanner.p_exception.match(token)]


def export(core: Obfuscator, tokens: list[str]) -> str:
    header = [token for token in tokens if Scanner.p_exception.match(token)]
    for token, _ in core.dictionary.items():
        header.append(f"#define {core.fmt(token)} {token}")

    output = []
    for token in tokens:
        if not Scanner.p_exception.match(token):
            output.append(core.fmt(token))

    return "\n".join(header) + "\n" + " ".join(output)


if __name__ == "__main__":
    if len(argv) < 2:
        print("No input!")
        print(f"{argv[0]} <filename>")
    else:
        with open(argv[-1], "r") as fd:
            c = fd.read()
        s = Scanner()
        d = s.run(c)
        p = export(parser(d), d)
        if environ.get("VERBOSE"):
            print("[Scanner]")
            pprint(c)
            print("[Parser]")
            pprint(d)
        with open(argv[-1] + ".tino.cpp", "w") as fd:
            fd.write(p)
