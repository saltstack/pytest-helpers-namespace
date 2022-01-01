#!/usr/bin/env python
# Copyright 2021-2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# pylint: skip-file
import pathlib

REPO_ROOT = pathlib.Path(__name__).resolve().parent
PYLINT_SPELLING_WORDS = REPO_ROOT / ".pylint-spelling-words"


def sort():
    in_contents = PYLINT_SPELLING_WORDS.read_text()
    out_contents = ""
    out_contents += "\n".join(sorted({line.lower() for line in in_contents.splitlines()}))
    out_contents += "\n"
    if in_contents != out_contents:
        PYLINT_SPELLING_WORDS.write_text(out_contents)


if __name__ == "__main__":
    sort()
