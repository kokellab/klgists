# coding=utf-8

from typing import Callable, Optional, Tuple, Iterable
from matplotlib.figure import Figure
import seaborn as sns

def prettify_plot(
		plot_fn: Callable[[], Figure],
		style: str='whitegrid',
		bounds: Tuple[int, int]=(40, 20), font_scale: float=3,
		x_lim: Optional[Tuple[Optional[float], Optional[float]]]=None,
		y_lim: Optional[Tuple[Optional[float], Optional[float]]]=None,
		x_ticks: Optional[Iterable[float]]=None,
		y_ticks: Optional[Iterable[float]]=None
) -> Figure:
	"""Plot something the same I prefer it. Matplotlib determines values if they're passed as None."""
	sns.set(rc={'figure.figsize': bounds}, font_scale=font_scale)
	sns.set_style(style)
	plot = plot_fn()
	if x_lim is not None:
		plot.set(xlim=x_lim)
	if y_lim is not None:
		plot.set(ylim=y_lim)
	if x_ticks is not None:
		plot.axes.set_xticks(x_ticks)
	if y_ticks is not None:
		plot.axes.set_xticks(y_ticks)
	return plot


__all__ = ['prettify_plot']
