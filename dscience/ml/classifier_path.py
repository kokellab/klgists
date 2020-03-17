"""
Code for machine learning, most noteably including classifiers of wells.
Can depend on core, model, viz, and calc.
"""
from __future__ import annotations
from typing import Sequence
from pathlib import Path
from dscience.core.internal import PathLike
from dscience.core.exceptions import PathError
from dscience.tools.filesys_tools import FilesysTools
from dscience.tools.path_tools import PathTools


class ClassifierPath:
	"""
	A path with standard subpaths for trained model, decision functions, and standard plots.
	Santiize the path beforehand -- it's not done here.
	The classifier might not support all of the paths.
	For example::
	```
	path = ClassifierPath('abc')
	print(path.weight_csv)  # will return path/'weight.csv'
	print(path.weight_csv.exists())  # might be false, even for a trained classifier
	```
	Similarly, `path.decision_csv` will not exist if the model does not support training decision functions (typically out-of-bag).
	"""
	def __init__(self, path: PathLike):
		self.path = Path(path)
	def prep(self):
		PathTools.prep_dir(self.path, exist_ok=True)
	def load_info(self):
		path = self.info_json
		return FilesysTools.load_json(path)
	def save_info(self, info):
		FilesysTools.save_json(info, self.info_json)
	def verify_exists(self) -> None:
		if not self.exists():
			raise PathError("No trained model under {}".format(self), path=self.path)
	def verify_exists_with_decision(self) -> None:
		if not self.exists():
			raise PathError("No trained model under {}".format(self), path=self.path)
		if not self.decision_csv.exists():
			raise PathError("No decision CSV under {}".format(self), path=self.path)
	def exists_with_decision(self) -> bool:
		return self.exists() and self.decision_csv.exists()
	def exists(self) -> bool:
		return (
				self.path.exists() and self.path.is_dir()
				and self.model_pkl.exists() and self.model_pkl.is_file()
				and self.info_json.exists() and self.info_json.is_file()
		)
	def resolve(self) -> ClassifierPath:
		return ClassifierPath(self.path.resolve())
	def parent(self) -> Path:
		return self.path.parent
	def parents(self) -> Sequence[Path]:
		return self.path.parents
	def anchor(self) -> str:
		return self.path.anchor
	def name(self) -> str:
		return self.path.name
	def __truediv__(self, other) -> Path:
		return self.path / other

	@property
	def model_pkl(self) -> Path:
		return self / 'model.pkl'
	@property
	def info_json(self) -> Path:
		return self / 'info.json'
	@property
	def cc_json(self) -> Path:
		return self / 'cc.json'
	@property
	def decision_csv(self) -> Path:
		return self / 'decision.csv'
	@property
	def weight_csv(self) -> Path:
		return self / 'weight.csv'
	@property
	def weight_h5(self) -> Path:
		return self / 'weight.h5'
	@property
	def weight_h5_key(self) -> str:
		return 'weight'
	@property
	def accuracy_csv(self) -> Path:
		return self / 'accuracy.csv'
	@property
	def confusion_csv(self) -> Path:
		return self / 'confusion.csv'
	@property
	def confusion_png(self) -> Path:
		return self / 'confusion.png'
	@property
	def confusion_pdf(self) -> Path:
		return self / 'confusion.pdf'
	@property
	def swarm_png(self) -> Path:
		return self / 'swarm.png'
	@property
	def swarm_pdf(self) -> Path:
		return self / 'swarm.pdf'
	@property
	def bar_png(self) -> Path:
		return self / 'bar.png'
	@property
	def bar_pdf(self) -> Path:
		return self / 'bar.pdf'
	@property
	def boxplot_png(self) -> Path:
		return self / 'boxplot.png'
	@property
	def boxplot_pdf(self) -> Path:
		return self / 'boxplot.pdf'
	@property
	def violin_png(self) -> Path:
		return self / 'violin.png'
	@property
	def violin_pdf(self) -> Path:
		return self / 'violin.pdf'

	def __repr__(self):
		return str(self.path)
	def __str__(self):
		return str(self.path)
	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.path == other.path
	def __hash__(self):
		return hash(self.path)


__all__ = ['ClassifierPath']
