#!/usr/bin/env python3
# Copyright 2021-2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=invalid-name,missing-module-docstring,missing-function-docstring
import argparse
import pathlib
import re
import sys
from datetime import datetime

CODE_ROOT = pathlib.Path(__file__).resolve().parent.parent
SPDX_HEADER = "# SPDX-License-Identifier: Apache-2.0"
COPYRIGHT_HEADER = "# Copyright {year} VMware, Inc."
COPYRIGHT_REGEX = re.compile(
    r"# Copyright (?:(?P<start_year>[0-9]{4})(?:-(?P<cur_year>[0-9]{4}))?) VMware, Inc\."
)
SPDX_REGEX = re.compile(r"# SPDX-License-Identifier:.*")


def check_copyright(files):
    for file in files:
        contents = file.read_text()
        if not contents.strip():
            # Don't add headers to empty files
            continue
        original_contents = contents
        try:
            if not COPYRIGHT_REGEX.search(contents):
                contents = inject_copyright_header(contents)
                if contents != original_contents:
                    print(f"Added the copyright header to {file}")
            else:
                contents = update_copyright_header(contents)
                if contents != original_contents:
                    print(f"Updated the copyright header on {file}")
            if not SPDX_REGEX.search(contents):
                contents = inject_spdx_header(contents)
                if contents != original_contents:
                    print(f"Added the SPDX header to {file}")
        finally:
            if not contents.endswith("\n"):
                contents += "\n"
            if original_contents != contents:
                file.write_text(contents)


def inject_copyright_header(contents):
    lines = contents.splitlines()
    shebang_found = False
    for idx, line in enumerate(lines[:]):
        if idx == 0 and line.startswith("#!"):
            shebang_found = True
            continue
        if shebang_found and line.strip():
            shebang_found = False
            lines.insert(idx, "")
            idx += 1
        lines.insert(idx, COPYRIGHT_HEADER.format(year=datetime.today().year))
        break
    return "\n".join(lines)


def update_copyright_header(contents):
    lines = contents.splitlines()
    for idx, line in enumerate(lines[:]):
        match = COPYRIGHT_REGEX.match(line)
        if match:
            this_year = str(datetime.today().year)
            cur_year = match.group("cur_year")
            if cur_year and cur_year.strip() == this_year:
                return contents
            initial_year = match.group("start_year").strip()
            if initial_year == this_year:
                return contents
            lines[idx] = COPYRIGHT_HEADER.format(year=f"{initial_year}-{this_year}")
            break
    return "\n".join(lines)


def inject_spdx_header(contents):
    lines = contents.splitlines()
    for idx, line in enumerate(lines[:]):
        if COPYRIGHT_REGEX.match(line):
            lines.insert(idx + 1, SPDX_HEADER)
            next_line = lines[idx + 2].strip()
            if next_line and not next_line.startswith('"""'):
                # If the next line is not empty, insert an empty comment
                lines.insert(idx + 2, "#")
            break
    return "\n".join(lines)


def main(argv):
    parser = argparse.ArgumentParser(prog=__name__)
    parser.add_argument("files", nargs="+", type=pathlib.Path)

    options = parser.parse_args(argv)
    return check_copyright(options.files)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
