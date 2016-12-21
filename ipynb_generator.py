#coding:utf-8

"""
http://hplgit.github.io/doconce/doc/pub/ipynb/ipynb_generator.html
https://github.com/hplgit/doconce/blob/master/doc/src/ipynb/ipynb_generator.py
"""

import re

def read(text):
    delimiter = re.compile(r'<!---([a-zA-Z0-9]+)?--->')
    cell_type, language = None, None
    cells = []
    for line in text.splitlines():
        m = delimiter.search(line)
        if m is not None:
            if m is not None:
                shortname = m.group(1)
                if shortname is not None:
                    cell_type = 'code'
                    language = shortname
                    cells.append([cell_type, language, []])
                else:
                    cell_type = 'markdown'
                    language = None
                    cells.append([cell_type, language, []])
            else:
                raise SyntaxError(
                    'Wrong syntax of cell delimiter: \n{s}'.format(line))
        else:
            if cell_type in ('markdown', 'code'):
                cells[-1][2].append(line)
                # do something here
            else:
                raise SyntaxError(
                    'line\n  {s}\nhas not beggining cell delimiter'.format(line))
    return cells

def translate(cells, nbversion=4):
    if nbversion == 3:
        return translate_v3(cells)
    elif nbversion == 4:
        return translate_v4(cells)
    else:
        raise ValueError(
            'nbversion [{}] must be either 3 or 4'.format(nbversion))

def translate_v3(cells):
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

def translate_v4(cells):
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

def execute(text, nbversion=4, timeout=600, kernel_name='python3'):
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor

    nb = nbformat.reads(text, as_version=nbversion)
    ep = ExecutePreprocessor(timeout=timeout, kernel_name=kernel_name)
    ep.preprocess(nb, {'metadata': {'path': '.'}})
    return nbformat.writes(nb)


if __name__ == "__main__":
    def main(text, filename=None):
        cells = read(text)
        # print(cells)
        output = translate(cells)
        output = execute(output)
        if filename is None:
            return output
        else:
            with open(filename, 'w') as fout:
                fout.write(output)

    text = """<!------>
## Test of Jupyter Notebook generator

This is a generated file using `misc/ipynb_generator.py`.
<!------>
## Math

This is a test notebook.

$$y'=ky$$
<!---python--->```python
import numpy as np

print(np.exp(1.0))
```<!------>
The above is a Python code for the following:

```python
print(np.log(1.0))
```
<!------>
## Text

This is the footer notes for this generated notebook.
"""

    import sys

    if len(sys.argv) == 1:
        print(main(text))
    else:
        import os.path

        for filename in sys.argv[1: ]:
            with open(filename, 'r') as fin:
                text = fout.read()
            root, ext = os.path.splitext(filename)
            outputname = '{s}.ipynb'.format(root)
            # if os.path.isfile(outputname):
            #     raise RuntimeError(
            #         'An output file [{}] already exists'.format(outputname))
            main(text, outputname)
