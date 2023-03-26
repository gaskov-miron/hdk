import re
from collections.abc import Iterable, Iterator

from hdk.assembly.syntax import AInstruction, CInstruction, Label


def remove_comments(line: str) -> str:
    """Removes comment from a text line.

    >>> remove_comments('// The whole line is a comment')
    ''
    >>> remove_comments('Command // comment')
    'Command '
    """
    if "//" not in line:
        return line
    return line[: line.index("//")]


def remove_whitespaces(line: str) -> str:
    """Removes all whitespaces from a text line.

    >>> remove_whitespaces('    DM = A +1 ; JGZ ')
    'DM=A+1;JGZ'
    """
    return re.sub(r"\s+", "", line, flags=re.UNICODE)


def preprocess(line: str) -> str:
    """Preprocesses a text line of the source code.

    >>> preprocess('    D = D - M;JMP  // continue a loop')
    'D=D-M;JMP'
    """
    line = remove_comments(line)
    line = remove_whitespaces(line)
    return line


Instruction = Label | AInstruction | CInstruction


def parse(instruction: str) -> Instruction:
    """Parses a symbolic instruction into an object.

    >>> parse('@i')
    AInstruction(symbol='i')
    >>> parse('(LOOP)')
    Label(symbol='LOOP')
    >>> parse('M=M+1')
    CInstruction(comp='M+1', dest='M', jump=None)
    >>> parse('D;JGT')
    CInstruction(comp='D', dest=None, jump='JGT')
    >>> parse('M=M+1;JGT')
    CInstruction(comp='M+1', dest='M', jump='JGT')
    """
    if instruction.startswith("@"):
        return AInstruction(instruction[1:])
    if instruction.startswith("(") and instruction.endswith(")"):
        return Label(instruction[1:-1])

    semicolon_count = instruction.count(";")
    equal_sign_count = instruction.count("=")
    if semicolon_count > 1:
        raise ValueError('C-Instruction could have at max one ";".')
    if equal_sign_count > 1:
        raise ValueError('C-Instruction could have at max one "=".')

    parts = re.split("=|;", instruction)
    return CInstruction(
        comp=parts[1] if equal_sign_count else parts[0],
        dest=parts[0] if equal_sign_count else None,
        jump=parts[-1] if semicolon_count else None,
    )


def parse_code(lines: Iterable[str]) -> Iterator[Instruction]:
    """Parses lines of source code into symbolic instruction objects."""
    for line_num, line in enumerate(lines):
        instruction = preprocess(line)
        if len(instruction) == 0:
            continue
        try:
            yield parse(instruction)
        except ValueError as e:
            raise ValueError(f"Cannot parse line {line_num  + 1}.") from e
