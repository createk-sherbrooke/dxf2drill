import argparse

import sys

import ezdxf

from dataclasses import dataclass

# For type annotations
import ezdxf.document

from typing import Generator

Drawing = ezdxf.document.Drawing


@dataclass
class Vec2:
    x: float
    y: float


@dataclass
class Circle:
    center: Vec2
    dia: float


def get_circles(dxf: Drawing, filter_expr: str) -> list[Circle]:
    msp = dxf.modelspace()
    result = []
    query = 'CIRCLE'
    if filter_expr:
        query += f"[{filter_expr}]"
    for c in msp.query(query):
        result.append(
            Circle(
                center=Vec2(x=c.dxf.center.x, y=c.dxf.center.y),
                dia=round(c.dxf.radius * 2, 4),
            )
        )
    return result


def group_circles_by_dia(circles: list[Circle]) -> dict[float, list[Circle]]:
    result = {}
    for c in circles:
        if c.dia not in result:
            result[c.dia] = []
        result[c.dia].append(c)
    return result


def fmt_number(x: float, n: int = 3) -> str:
    """Format float with fixed precision and stripped trailing zeros"""
    fmt = f"{{:.{n}f}}"
    s = fmt.format(x)
    while s[-1] == "0" and s[-2] != ".":
        s = s[:-1]
    return s


def generate_xnc_header(
    units: str, tool_map: dict[float, int]
) -> Generator[str, None, None]:
    """
    units: METRIC or INCH (according to XNC spec)
    tool_map: dict of {diameter: tool_index}
    """
    yield "M48"  # Begin header
    yield units

    # Tool declarations
    for dia, idx in tool_map.items():
        yield f"T{idx:02d}C{dia:.3f}"
    yield "%"  # End of header


def generate_xnc(circles: list[Circle]) -> Generator[str, None, None]:
    dia_groups = group_circles_by_dia(circles)
    dia_list = list(dia_groups.keys())
    tool_map = {dia_list[i]: i + 1 for i in range(len(dia_list))}
    for cmd in generate_xnc_header("METRIC", tool_map):
        yield cmd

    # Drill mode
    yield "G05"
    for tool_dia, tool_idx in tool_map.items():
        # Tool declaration
        yield f"T{tool_idx:02d}"
        # Drill hits for tool
        for circ in dia_groups[tool_dia]:
            yield f"X{fmt_number(circ.center.x)}Y{fmt_number(circ.center.y)}"

    yield "M30"  # End of file


def get_args():
    parser = argparse.ArgumentParser(
        prog="dxf2drill",
        description="Extract circles from DXF file to XNC drill file",
        epilog="Note: output is written to stdout",
    )
    parser.add_argument("filename", help="Input DXF file")
    parser.add_argument(
        "-e",
        "--filter-expression",
        help="Filter expression used to select circles converted to drill hits",
    )
    return parser.parse_args()


def main():
    args = get_args()
    dxf = ezdxf.readfile(args.filename)
    circles = get_circles(dxf, args.filter_expression)

    for cmd in generate_xnc(circles):
        sys.stdout.write(cmd)
        sys.stdout.write("\x0a")


if __name__ == "__main__":
    main()
