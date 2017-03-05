# coding=utf-8

from IPython.display import display, Markdown
import pandas as pd

def head(df: pd.DataFrame, n_rows:int=1) -> None:
    """Pretty-print the head of a Pandas table in a Jupyter notebook and show its dimensions."""
    display(Markdown("**whole table (below):** {} rows × {} columns".format(len(df), len(df.columns))))
    display(df.head(n_rows))