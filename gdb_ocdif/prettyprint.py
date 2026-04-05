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
