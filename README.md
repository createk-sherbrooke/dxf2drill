# dxf2drill

Extract circles from a DXF file to an
[XNC](https://www.ucamco.com/en/news/xnc-format-specification-revision-202111)
drill file used for PCB fabrication.

## Installation

The simplest to install is with [uv](https://docs.astral.sh/uv/guides/install-python/#getting-started):

```bash
$> uv tool install 'git+https://github.com/createk-sherbrooke/dxf2drill'
```

## Usage

```
usage: dxf2drill [-h] [-e FILTER_EXPRESSION] filename

Extract circles from DXF file to XNC drill file

positional arguments:
  filename              Input DXF file

options:
  -h, --help            show this help message and exit
  -e FILTER_EXPRESSION, --filter-expression FILTER_EXPRESSION
                        Filter expression used to select circles converted to drill hits

Note: output is written to stdout
```

For more information on `FILTER_EXPRESSION`, see the [ezdxf documentation on
queries](https://ezdxf.readthedocs.io/en/stable/tasks/query.html). dxf2drill passes `FILTER_EXPRESSION` to ezdxf like this to find circles:

```python
circles = msp.query(f'CIRCLE[{filter_expression}]')
```

For example, to extract only holes smaller than 10 units of diameter (radius 5
units, DXF is unitless) on layer "0":

```bash
$> dxf2drill -e 'radius < 5 & layer == "0"' example.dxf > example.xnc
```

## dxfstrip tool

This repository also includes the `dxfstrip` tool, which is installed alongside
dxf2drill. It is a simple script that uses ezdxf to delete selected entities
from a DXF file, and outputs the resulting "stripped" DXF to stdout.

This can be useful to remove all `CIRCLE`s which were exported to XNC:

```bash
$> dxfstrip 'CIRCLE[radius < 5]' example.dxf > example_no_holes.dxf
```

Another example, to remove all text (DXF `MTEXT` entities) on layer "0":

```bash
$> dxfstrip 'MTEXT[layer == 0]' example.dxf > example_no_text.dxf
```