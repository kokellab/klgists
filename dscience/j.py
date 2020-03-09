import re
from typing import Optional
from IPython.display import display, Markdown, HTML
import pandas as pd
from dscience.core.exceptions import StringPatternError
_color_pattern = re.compile('#?[A-Z0-9a-z]{6}')


# noinspection PyTypeChecker
class J:
	"""
	Convenience user tools to display HTML text in Jupyter notebooks.
	"""
	from IPython.display import display, clear_output
	from IPython.utils import io as __io

	RED, GREEN, BLUE, PURPLE, CYAN, BOLD = '#cc0000', '#008800', '#0000cc', '#880099', '#007777', '600'

	@classmethod
	def full_width(cls, percent: bool = 100):
		display(HTML("<style>.container { width:" + str(percent) + "% !important; }</style>"))

	@classmethod
	def full(cls, df: pd.DataFrame) -> None:
		with pd.option_context("display.max_rows", 10 ** 10):
			with pd.option_context("display.max_columns", 10 ** 10):
				display(df)

	@classmethod
	def confirm(cls, msg: Optional[str] = None) -> bool:
		#return Tools.confirm(lambda: cls.blue("Confirm? [yes/no]" if msg is None else msg))
		cls.bold_colored("Confirm? [yes/no]" if msg is None else msg, cls.BLUE)
		return cls.__io.ask_yes_no('')

	@classmethod
	def hyperlink(cls, text: str, url: str) -> None:
		display(HTML('<a href="{}">{}</a>'.format(url, text)))

	@classmethod
	def red(cls, text: str) -> None:
		cls.colored(text, cls.RED)

	@classmethod
	def blue(cls, text: str) -> None:
		cls.colored(text, cls.BLUE)

	@classmethod
	def green(cls, text: str) -> None:
		cls.colored(text, cls.GREEN)

	@classmethod
	def bold(cls, text: str) -> None:
		cls.styled(text, font_weight=cls.BOLD)

	@classmethod
	def colored(cls, text: str, color: str, **kwargs) -> None:
		cls.styled(text, color=cls._color(color), **kwargs)

	@classmethod
	def bold_colored(cls, text: str, color: str) -> None:
		cls.styled(text, color=color, font_weight=cls.BOLD)

	@classmethod
	def code(cls, text: str, **kwargs) -> None:
		cls.styled(text, white_space='pre', font_family='monospace', **kwargs)

	@classmethod
	def md(cls, text: str) -> None:
		display(Markdown(text))

	@classmethod
	def html(cls, text: str) -> None:
		display(HTML(text))

	@classmethod
	def styled(cls, text: str, *main, **css: str) -> None:
		"""
		Display a span element styled with free CSS arguments.
		:param text: The text to include in an HTML span
		:param main: Any free text of CSS, or a list of parameters
		:param css: Any free dict of CSS style paramters; spaces and underscores in the keys will be replaced with hypens
		"""
		main = ';'.join(main)
		css = ';'.join("{}: {}".format(k.replace('_', '-').replace(' ', '-'), str(v)) for k, v in css.items())
		if len(main)>0 and not main.endswith(';'):
			main += ';'
		z = (main+css) if (main+css).endswith(';') else (main+css+';')
		display(HTML('<span style="{}">{}</span>'.format(z, text)))

	@classmethod
	def _color(cls, color: str) -> str:
		if _color_pattern.fullmatch(color) is None:
			raise ValueError("Invalid hex color {}".format(color))
		return color if color.startswith('#') else '#' + color


class JFonts:
	"""
	Renders HTML for matplotlib fonts.
	"""

	@classmethod
	def one(cls, name: str) -> None:
		"""
		Shows a single typeface as itself. Ex; will show Helvetica in Helvetica.
		"""
		J.html("<p style='font-family:{font};'>{font}</p>".format(font=name))

	@classmethod
	def mine(cls) -> None:
		"""
		Shows all typefaces currently in the matplotlib rcParams.
		Each typeface is renderered as itself. Ex; will show Helvetica in Helvetica.
		Each font family (`plt.rcParams['font.family']`) is shown separately, with all its fonts underneath.
		"""
		import matplotlib.pyplot as plt
		for family in plt.rcParams['font.family']:
			items = '\n'.join([
				"<li style='font-family:{font};'>{font}</li>".format(font=font)
				for font in plt.rcParams.get('font.' + family, [])
			])
			J.html((
				'<h4 style="padding-bottom:0;margin-bottom:0;">{}:</h4>\n'
				'<ul style="padding-top:0;margin-top:0;margin-bottom:0;margin-top:0;">\n'
				'{}\n</ul>'
			).format(family, items))

	@classmethod
	def every(cls, n_cols: int = 4) -> None:
		"""
		Shows an HTML table of all typefaces rendered as themselves. Ex; will show Helvetica in Helvetica.
		Displays as an HTML table with `n_cols`.
		Thanks to http://jonathansoma.com/lede/data-studio/matplotlib/list-all-fonts-available-in-matplotlib-plus-samples/.
		:param n_cols:
		"""
		from matplotlib.font_manager import fontManager
		def _show_font(name: str):
			return "<p style='font-family:{font};'>{font}</p>".format(font=name)
		fonts = set([f.name for f in fontManager.ttflist])
		code = "\n".join([_show_font(font) for font in sorted(fonts)])
		J.html("<div style='column-count: {};'>{}</div>".format(n_cols, code))


__all__ = ['J', 'JFonts']
