# Data Science Gists

A package of Python 3.7+ snippets and tools for data science work. Not all functions are well-tested.

To get started, call:
```python
from dscience_gists.full import *
```
This will load `Tools`, `Chars`, `J`, and `abcd`.
The `Tools` class has various lightweight utility functions (classmethods):

```python
from dscience_gists.full import *
Tools.git_description('.').tag                # the tag, or None
Tools.ms_to_minsec(7512000)                   # '02:05:12'
Tools.fix_greek('beta,eta and Gamma')         # 'β,η and Γ'
Tools.pretty_function(lambda s: 55)           # '<λ(1)>'
Tools.pretty_function(list)                   # '<list>'
Tools.strip_brackets_and_quotes('(ab[cd)"')   # 'ab[cd' (only strips if paired)
Tools.iceilopt(None), Tools.iceilopt(5.3)     # None, 6
Tools.succeeds(fn_to_try)                     # True or False
Tools.or_null(fn_might_fail)                  # None if it failed
Tools.only([1]), Tools.only([1, 2])           # 1, MultipleMatchesError
Tools.is_probable_null(np.nan)                # True
Tools.read_properties_file('abc.properties')  # returns a dict
important_info = Tools.get_env_info()         # a dict of info like memory usage, cpu, host name, etc.
```

`Chars` contains useful Unicode characters that are hard to type and related functions:
```python
from dscience_gists.full import *
print(x0 + Chars.en + x1)          # en dash
print(Chars.angled('not found'))   # '⟨not found⟩'
```

The class `J` has tools for display in Jupyter:

```python
from dscience_gists.full import *
J.red('This is bad.')            # show red text
if J.prompt('Really delete?'):   # ask the user
    J.bold('Deleting.')
```

And the `abcd` package has useful decorators.
For example, output timing info:
```python
from dscience_gists.full import *
@abcd.takes_seconds
def slow_fn():
    for _ in range(1000000): pass
slow_fn()  # prints 'Done. Took 23s.'
```

Or for an immutable class with nice `str` and `repr`:

```python
from dscience_gists.full import *
@auto_repr_str()  # can also set 'include' or 'exclude'
@abcd.immutable
class CannotChange:
    __init__(self, x: str):
        self.x = x
obj = CannotChange('sdf')
print('obj')  # prints 'CannotChange(x='sdf')
obj.x = 5  # breaks!!
``` 

You can also import just what you need. Plain `Tools` subclasses from all of these. For example:

```python
from dscience_gists.tools.path_tools import PathTools
print(PathTools.sanitize_file_path('ABC|xyz'))  # logs a warning & returns 'ABC_xyz'
print(PathTools.sanitize_file_path('COM1'))     # complains!! illegal path on Windows.
from dscience_gists.tools.prompt_tools import PromptTools
if PromptTools.prompt_yes_no('Delete?'):
    #  Takes 10s, writing Deleting my_dir.......... Done.
    PromptTools.slow_delete('my_dir', wait=10)
```

A couple of other things were imported, including `DevNull`, `DelegatingWriter`, and `TieredIterator`.
There are also more specific classes that were not imported.
These can be imported individually from `dscience.support` and `dscience.analysis`.
- `dscience.support` contains data structures and supporting tools, such as `FlexibleLogger`, `TomlData`, and `Wb1` (for multiwell plates).
- `dscience.analysis` contains code that is more involved, such as `UniprotGoTerms`, `AtcTree`, and `PeakFinder`. Some of these will download web resources.
- `dscience.ml` contains models for machine learning, including `DecisionFrame` and `ConfusionMatrix`

Here are various snippets from these:

```python
wb1 = Wb1(8, 12)               # 96-well plate
print(wb1.index_to_label(13))  # prints 'B01'
for well in wb1.block_range('A01', 'H11'):
    print(well)                # prints 'A01', 'A02', etc.
```

```python
from dscience_gists.ml.confusion_matrix import ConfusionMatrix
mx = ConfusionMatrix.read_csv('mx.csv')                         # just a subclass of pd.DataFrame
print(mx.sum_diagonal() - mx.sum_off_diagonal())
mx = mx.sort(cooling_factor=0.98).symmetrize().triagonalize()   # 
```

```python
from dscience_gists.analysis.tissue_expression import TissueTable
tissues = TissueTable()
# returns a Pandas DataFrame of expression levels per cell type per gene for this tissue.
tissues.tissue('MKNK2')
```

[![CircleCI](https://circleci.com/gh/kokellab/klgists.svg?style=shield)](https://circleci.com/gh/kokellab/klgists)

## license

The authors release these contents and documentation files under the terms of the [Apache License, version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
The project was developed to support research at the Kokel Lab, fulfill requirements for [UCSF QBC](http://qbc.ucsf.edu/) PhD programs, and be useful to the public.

#### authors
- Douglas Myers-Turnbull (primary)
- Chris Ki (contributor)
- Cole Helsell (contributor)