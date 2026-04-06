# Copyright © 2026 Max Sikström
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List, Dict


def _pad_str(string: str, size: int) -> str:
    return (" " * size + string)[-size:]


def _sized_row(fields: List[str], sizes: List[int]) -> str:
    return " " + "  ".join(_pad_str(field, size) for field, size in zip(fields, sizes))


def print_table(headers: List[str], data: List[Dict[str, str]]) -> None:
    # Clone list, to be able to append later
    headers = [x for x in headers]
    # Keep headers as set for faster search
    hdrset = {x for x in headers}

    # Fill list of all headers
    for elem in data:
        new_headers = set(elem.keys()) - hdrset
        headers.extend(sorted(new_headers))
        hdrset.update(new_headers)

    # Find size of all headers
    # Header name should fit at least
    sizes = [len(name) for name in headers]
    for elem in data:
        for i, name in enumerate(headers):
            if name in elem:
                sizes[i] = max(len(elem[name]), sizes[i])

    # Print headers
    print()
    print(_sized_row(headers, sizes))
    print(_sized_row(["-" * size for size in sizes], sizes))
    for elem in data:
        inforow = [elem.get(name, "") for name in headers]
        print(_sized_row(inforow, sizes))
    print()
