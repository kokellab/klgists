import pandas as pd
import itertools
import warnings
from typing import Iterator, List

def marker_iterator(df: pd.DataFrame, class_column: str='class') -> Iterator[str]:
    """Returns an iterator of decent marker shapes. The order is such that similar markers aren't used unless they're needed."""
    # Don't use MarkerStyle.markers because some are redundant
    lst = ['o', 's', '*', 'v', '^', 'D', 'h', 'x', '+', '8', 'p', '<', '>', 'd', 'H']
    if df.groupby(class_column).count().max() > len(lst):
        warnings.warn("Currently limited to {} markers; some will be recycled".format(len(lst)))
    return itertools.cycle(lst)

def markers_for_rows(df: pd.DataFrame, class_column: str='class') -> List[str]:
    """Returns a list of markers, one for each row.
    Mostly useful as a reminder not to give Seaborn lmplot markers=a_pandas_series: it needs a list.
    """
    markers = marker_iterator(df)
    # NOTE: With Seaborn lmplot, if you just pass the Series markers_df['marker] without doing .values.tolist(), you'll get an error
    return df.index.map(lambda _: next(markers)).values.tolist()
