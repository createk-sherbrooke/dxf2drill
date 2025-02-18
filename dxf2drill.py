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


def get_circles(dxf: Drawing) -> list[Circle]:
    msp = dxf.modelspace()
    result = []
    for c in msp.query("CIRCLE"):
        result.append(
            Circle(
                center=Vec2(x=c.dxf.center.x, y=c.dxf.center.y), dia=c.dxf.radius * 2
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


def get_args():
    parser = argparse.ArgumentParser(
        prog="dxf2drill",
        description="Extract circles from DXF file to XNC drill file",
        epilog="Note: output is written to stdout",
    )
    parser.add_argument("filename", help="Input DXF file")
    return parser.parse_args()


def generate_xnc_header(units: str, tool_map: dict[float, int]) -> Generator[str]:
    """
    units: METRIC or INCH (according to XNC spec)
    tool_map: dict of {diameter: tool_index}
    """
    yield "M48"
    yield units
    for dia, idx in tool_map.items():
        yield f"T{idx:02d}C{dia:.3f}"
    yield "%"


def generate_xnc(circles: list[Circle]) -> Generator[str]:
    dia_groups = group_circles_by_dia(circles)
    dia_list = list(dia_groups.keys())
    tool_map = {dia_list[i]: i for i in range(len(dia_list))}
    for cmd in generate_xnc_header("METRIC", tool_map):
        yield cmd


def main():
    args = get_args
    dxf = ezdxf.readfile(args.filename)
    circles = get_circles(dxf)

    for cmd in generate_xnc(circles):
        sys.stdout.write(cmd)
        sys.stdout.write('\x0A')

if __name__ == "__main__":
    main()
