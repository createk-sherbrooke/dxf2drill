import argparse

import sys

import ezdxf

# For type annotations

Drawing = ezdxf.document.Drawing


def get_args():
    parser = argparse.ArgumentParser(
        prog="dxfstrip",
        description="Strip entities from DXF files",
        epilog="Note: output is written to stdout",
    )
    parser.add_argument(
        "query",
        help="Query passed to ezdxf's query() method to select entities to be deleted",
    )
    parser.add_argument("filename", help="Input DXF file")
    return parser.parse_args()


def main():
    args = get_args()
    dxf = ezdxf.readfile(args.filename)
    msp = dxf.modelspace()

    entities = msp.query(args.query)
    for e in entities:
        msp.delete_entity(e)

    dxf.write(sys.stdout)


if __name__ == "__main__":
    main()
