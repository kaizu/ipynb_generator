# ipynb_generator

## HOWTO

The following command will generator `sample.ipynb` from `sample.md`.

```
$ python ipynb_generator.py sample.md
```

To show the usage, do as `python ipynb_generator.py -h`.

## SYNTAX

`<!--- --->` works as a separator for cells.

`<!---python--->` tells the following cell is a code for Python. In the cell, lines starts with three back-ticks, \`\`\`, are ignored at the generation. Thus, the typical way to specifying a code for Python is:

    <!---python--->
    ```python
    # do something here
    ```
    <!--- --->
    Markdown here.

## REFERENCES

- http://hplgit.github.io/doconce/doc/pub/ipynb/ipynb_generator.html
- https://github.com/hplgit/doconce/blob/master/doc/src/ipynb/ipynb_generator.py
- http://nbconvert.readthedocs.io/en/stable/execute_api.html
