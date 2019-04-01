import seaborn as sns


def whiteout(scale: float = 2):
	"""Sets nice Seaborn defaults, including the 'whitegrid' (white background) style.
	:param  scale: The font_scale, which the figure size is determined based on
	"""
	sns.set(rc={'figure.figsize': (scale * 5, scale * 3)}, font_scale=scale)
	sns.set_style('whitegrid')


__all__ = ['whiteout']
