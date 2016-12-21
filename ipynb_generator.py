#coding:utf-8

"""
http://hplgit.github.io/doconce/doc/pub/ipynb/ipynb_generator.html
https://github.com/hplgit/doconce/blob/master/doc/src/ipynb/ipynb_generator.py
"""

import re

from logging import getLogger, StreamHandler, NullHandler, Formatter, DEBUG
logger = getLogger(__name__)
# handler = NullHandler()
handler = StreamHandler()
formatter = Formatter('%(levelname)s:%(name)s:%(message)s')
handler.setLevel(DEBUG)
handler.setFormatter(formatter)
logger.setLevel(DEBUG)
logger.addHandler(handler)


def readmd(text):
    delimiter = re.compile(r'<!---\s*([a-zA-Z0-9]+)?\s*--->')
    cell_type, language = 'markdown', None
    cells = []
    for line in text.splitlines():
        m = delimiter.search(line)
        if m is not None:
            if m is not None:
                shortname = m.group(1)
                if shortname is not None:
                    cell_type = 'code'
                    language = shortname
                else:
                    cell_type = 'markdown'
                    language = None
                cells.append([cell_type, language, []])
            else:
                raise SyntaxError(
                    'Wrong syntax of cell delimiter: \n{s}'.format(line))
        else:
            if len(cells) == 0:
                cells.append([cell_type, language, []])  ## the first line

            if cell_type == 'markdown':
                cells[-1][2].append(line)
            elif cell_type == 'code':
                if not line.lstrip().startswith('```'):
                    cells[-1][2].append(line)
            else:
                raise SyntaxError(
                    'line\n  {:s}\nhas not beggining cell delimiter [{}]'.format(line, cell_type))
    return cells

def translatenb(cells, nbversion=4):
    if nbversion == 3:
        return translatenb_v3(cells)
    elif nbversion == 4:
        return translatenb_v4(cells)
    else:
        raise ValueError(
            'nbversion [{}] must be either 3 or 4'.format(nbversion))

def translatenb_v3(cells):
    from nbformat.v3 import (
        new_code_cell, new_text_cell, new_worksheet,
        new_notebook, new_metadata, new_author)

    nb = new_worksheet()
    for cell_type, language, block in cells:
        block = '\n'.join(block)

        if cell_type == 'markdown':
            nb.cells.append(
                new_text_cell(u'markdown', source=block))
        elif cell_type == 'code':
            nb.cells.append(new_code_cell(input=block))
        else:
            raise ValueError('Wrong cell_type was given [{}]'.format(cell_type))

    nb = new_notebook(worksheets=[nb], metadata=new_metadata())
    # upgrade notebook to v4
    from nbformat.v4 import upgrade
    nb = upgrade(nb)
    import nbformat.v4.nbjson as nbjson
    return nbjson.writes(nb)

def translatenb_v4(cells):
    from nbformat.v4 import (
        new_code_cell, new_markdown_cell, new_notebook)

    nb_cells = []
    for cell_type, language, block in cells:
        block = '\n'.join(block)

        if cell_type == 'markdown':
            nb_cells.append(
                new_markdown_cell(source=block))
        elif cell_type == 'code':
            nb_cells.append(new_code_cell(source=block))
        else:
            raise ValueError('Wrong cell_type was given [{}]'.format(cell_type))

    nb = new_notebook(cells=nb_cells)
    from nbformat import writes
    return writes(nb, version=4)

def executenb(text, nbversion=4, timeout=600, kernel_name='python3', run_path='.', outputname=None):
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor
    from nbconvert.preprocessors.execute import CellExecutionError

    nb = nbformat.reads(text, as_version=nbversion)
    ep = ExecutePreprocessor(timeout=timeout, kernel_name=kernel_name)

    try:
        out = ep.preprocess(nb, {'metadata': {'path': run_path}})
    except CellExecutionError:
        msg = 'Error executing the notebook.'
        if outputname is not None:
            msg += ' See notebook "{:s}" for the traceback.'.format(outputname)
        logger.error(msg)
        raise
    finally:
        return nbformat.writes(nb)


if __name__ == "__main__":
    def main(text, filename=None, execute=True):
        cells = readmd(text)
        # print(cells)
        output = translatenb(cells)
        if execute:
            output = executenb(output, outputname=filename)
        if filename is None:
            return output
        else:
            with open(filename, 'w') as fout:
                fout.write(output)

    text = """<!--- --->
## Test of Jupyter Notebook generator

This is a generated file using `misc/ipynb_generator.py`.
<!--- --->
## Math

This is a test notebook.

$$y'=ky$$
<!---python--->```python
import numpy as np

print(np.exp(1.0))
```<!--- --->
The above is a Python code for the following:

```python
print(np.log(1.0))
```
<!--- --->
## Text

This is the footer notes for this generated notebook.
"""

    import argparse
    parser = argparse.ArgumentParser(description='Generate Jupyter notebooks from markdown files.')
    parser.add_argument('filenames', metavar='FILENAME', type=str, nargs='*', help='markdown filenames')
    parser.add_argument('--noexec', '-n', action='store_true', help='save notebooks without execution')
    parser.add_argument('--nooverwrite', action='store_true', help='avoid to overwrite an existing file')
    parser.add_argument('--suffix', action='store', type=str, default='.ipynb', help='suffix for the output')
    parser.add_argument('--prefix', action='store', type=str, help='prefix for the output')
    args = parser.parse_args()

    filenames = args.filenames
    execute = not args.noexec
    overwrite = not args.nooverwrite
    suffix = args.suffix
    prefix = args.prefix

    if len(filenames) == 0:
        print(main(text))
        import sys
        sys.exit(0)

    import os.path

    for filename in filenames:
        with open(filename, 'r') as fin:
            text = fin.read()
        header, tail = os.path.split(filename)
        root, ext = os.path.splitext(tail)
        outputname = '{:s}{:s}'.format(root, suffix)
        outputname = os.path.join(header if prefix is None else prefix, outputname)
        if not overwrite and os.path.isfile(outputname):
            raise RuntimeError(
                'An output file [{}] already exists'.format(outputname))
        main(text, outputname, execute)
