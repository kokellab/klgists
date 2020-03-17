import subprocess
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from dscience.core.internal import PathLike
from typing import Sequence


class ClassificationUtils:

	@classmethod
	def viz_tree(cls, tree: DecisionTreeClassifier, classes: Sequence[str], path: PathLike, **kwargs) -> Path:
		"""
		Plots a single tree from a DecisionTreeClassifier to a path.
		"""
		path = Path(path)
		dotpath = path.with_suffix('.dot')
		export_graphviz(tree, class_names=classes, out_file=str(dotpath), label='none', **kwargs)
		command = ["dot", "-T"+path.suffix.lstrip('.'), str(dotpath), "-o", str(path)]
		subprocess.check_output(command)
		dotpath.unlink()
		return path


__all__ = ['ClassificationUtils']
