# ipynb_generator

## HOWTO

The following command will generator `sample.ipynb` from `sample.md`.

```
$ python ipynb_generator.py sample.md
```

To show the usage, do as `python ipynb_generator.py -h`.

## SYNTAX

A code block in the given markdown is automatically translated into a code cell.

`<!--- --->` works as a separator for cells.

## REFERENCES

- http://hplgit.github.io/doconce/doc/pub/ipynb/ipynb_generator.html
- https://github.com/hplgit/doconce/blob/master/doc/src/ipynb/ipynb_generator.py
- http://nbconvert.readthedocs.io/en/stable/execute_api.html
