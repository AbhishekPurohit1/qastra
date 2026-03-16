"""Parser for Qastra `.qa` test files.

The goal is to keep the syntax simple and close to natural language while
still being easy to interpret reliably.

Example `login.qa`:

    open https://example.com
    click "login button"
    type "abhi" into "username field"
    type "password123" into "password field"
    click "submit"
    verify "dashboard visible"
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple, Union


@dataclass
class QACommand:
    action: str
    target: Optional[str] = None
    value: Optional[str] = None


_CLICK_RE = re.compile(r'^click\s+"(.+)"\s*$', re.IGNORECASE)
_OPEN_RE = re.compile(r"^open\s+(\S+)\s*$", re.IGNORECASE)
_TYPE_RE = re.compile(
    r'^type\s+"(.+)"\s+into\s+"(.+)"\s*$',
    re.IGNORECASE,
)
_VERIFY_RE = re.compile(r'^verify\s+"(.+)"\s*$', re.IGNORECASE)


def parse_qa_line(line: str) -> Optional[QACommand]:
    """Parse a single `.qa` line into a QACommand dataclass."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    if m := _OPEN_RE.match(stripped):
        return QACommand(action="open", target=m.group(1))

    if m := _CLICK_RE.match(stripped):
        return QACommand(action="click", target=m.group(1))

    if m := _TYPE_RE.match(stripped):
        value, target = m.groups()
        return QACommand(action="type", target=target, value=value)

    if m := _VERIFY_RE.match(stripped):
        return QACommand(action="verify", target=m.group(1))

    # Fallback: treat the whole line as a free‑form click/verify target
    return QACommand(action="raw", target=stripped)


def parse_qa_file(path: str) -> List[QACommand]:
    """Parse a `.qa` file into a list of QACommand objects."""
    commands: List[QACommand] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            cmd = parse_qa_line(line)
            if cmd is not None:
                commands.append(cmd)
    return commands


CommandTuple = Tuple[str, Union[str, Tuple[str, str]]]


def parse_qa_line_to_command(line: str) -> Optional[CommandTuple]:
    """Parse a single `.qa` line into an executable command tuple.

    Examples:
        'open https://example.com'
            -> ("open", "https://example.com")
        'click "login button"'
            -> ("click", "login button")
        'type "abhi@test.com" into "email field"'
            -> ("type", ("abhi@test.com", "email field"))
        'verify "dashboard visible"'
            -> ("verify", "dashboard visible")

    Blank lines and comment lines (starting with '#') return None.
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    match = _OPEN_RE.match(stripped)
    if match:
        return ("open", match.group(1))

    match = _CLICK_RE.match(stripped)
    if match:
        return ("click", match.group(1))

    match = _TYPE_RE.match(stripped)
    if match:
        value, target = match.groups()
        return ("type", (value, target))

    match = _VERIFY_RE.match(stripped)
    if match:
        return ("verify", match.group(1))

    # Fallback: treat the whole line as a raw instruction
    return ("raw", stripped)


def parse_qa_lines_to_commands(lines: Iterable[str]) -> List[CommandTuple]:
    """Parse an iterable of `.qa` lines into a list of command tuples."""
    commands: List[CommandTuple] = []
    for line in lines:
        cmd = parse_qa_line_to_command(line)
        if cmd is not None:
            commands.append(cmd)
    return commands


def parse_qa_file_to_commands(path: str) -> List[CommandTuple]:
    """Parse a `.qa` file into a list of executable command tuples."""
    with open(path, "r", encoding="utf-8") as f:
        return parse_qa_lines_to_commands(f)


__all__ = [
    "QACommand",
    "parse_qa_line",
    "parse_qa_file",
    "CommandTuple",
    "parse_qa_line_to_command",
    "parse_qa_lines_to_commands",
    "parse_qa_file_to_commands",
]

