from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib
import pandas as pd
from typing import Callable, Tuple, Dict, Optional, Union

def plot_dose_response(df: pd.DataFrame,
						drug_column: str='drug name', response_column: str='response', dose_column: str='log(dose)', class_column: str='class', size: Union[str, int, float]=100,
						n_cols: int=5, ylim: Tuple[float, float]=(0, None), horizontal_padding: float=0.1, vertical_padding: float=0.3,
						style: str='whitegrid', font_scale: float=1.2,
						class_to_color: Optional[Dict[str, str]]=None) -> matplotlib.figure.Figure:
	"""Plot a grid of nice-looking dose-response curves."""
	sns.set(font_scale=font_scale)
	sns.set_style(style)
	plot = sns.FacetGrid(df, col=drug_column, col_wrap=n_cols, hue=class_column, palette=class_to_color)
	plot.map(plt.plot, dose_column, response_column)
	size = size if isinstance(size, float) or isinstance(size, int) else df[size]
	plot.map(plt.scatter, dose_column, response_column, s=size)
	plot.set(xlim=(0, None), ylim=ylim)
	plot.set_titles(col_template="{col_name}")
	plot.fig.subplots_adjust(wspace=horizontal_padding, hspace=vertical_padding)
	return plot
