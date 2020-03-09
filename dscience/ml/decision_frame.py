from __future__ import annotations
from typing import Sequence
from pathlib import Path
import numpy as np
import pandas as pd
from dscience_gists.core.exceptions import *
from dscience_gists.support.extended_df import *
from dscience_gists.ml.confusion_matrix import *
from dscience_gists.ml.accuracy_frame import *


class DecisionFrame(ExtendedDataFrame):
	"""
	An n × m matrix of probabilities (or scores) from a classifier.
	The n rows are samples, and the m columns are predictions. The values are the confidence or pobability of prediction.
	The single index column is named 'correct_label', and the single column name is named 'label'.
	Practically, this is a Pandas wrapper around a scikit-learn decision_function that also has the predicted and correct class labels.
	"""

	@staticmethod
	def of(correct_labels: Sequence[str], labels: Sequence[str], decision_function: np.array, well_ids: Sequence[int], run_ids: Sequence[int]) -> DecisionFrame:
		"""
		Wraps a decision function numpy array into a DecisionFrame instance complete with labels as names and columns.
		:param correct_labels: A length-n list of the correct labels for each of the n samples
		:param labels: A length-m list of class labels matching the predictions (columns) on `probabilities`
		:param decision_function: An n × m matrix of probabilities (or scores) from the classifier.
				The rows are samples, and the columns are predictions.
				scikit-learn decision_functions (ex model.predict_proba) will output this.
			:param well_ids: For reference
			:param run_ids: For reference
		:return: A DecisionFrame
		"""
		decision_function = pd.DataFrame(decision_function)
		decision_function.index = [correct_labels, well_ids, run_ids]
		decision_function.columns = labels
		decision_function.index.names = ['label', 'well', 'run']
		return DecisionFrame(decision_function)

	def confusion(self) -> ConfusionMatrix:
		labels = self.columns
		correct_labels = self.index.get_level_values('label')
		if self.shape[0] != len(correct_labels):
			raise LengthMismatchError("Number of rows of decision function of shape {} is not the length of the correct labels {}".format(self.shape, len(correct_labels)))
		if self.shape[1] != len(labels):
			raise LengthMismatchError("Number of columns of decision function of shape {} is not the length of the class labels {}".format(self.shape, len(labels)))
		correct_confused_with = {c: {p: 0.0 for p in labels} for c in labels}
		for r, row in enumerate(self.index):
			correct_name = correct_labels[r]
			for c, column in enumerate(self.columns):
				confused_name = labels[c]
				correct_confused_with[correct_name][confused_name] += self.iat[r, c]
		correct_confused_with = pd.DataFrame(correct_confused_with)
		correct_confused_with /= correct_confused_with.sum()
		return ConfusionMatrix(correct_confused_with)

	def accuracy(self) -> AccuracyFrame:
		actual_labels = self.index.get_level_values('label').values
		wells = self.index.get_level_values('well').values
		runs = self.index.get_level_values('run').values
		stripped = self.copy().reset_index()
		stripped = stripped.drop('well', axis=1).drop('run', axis=1).set_index('label')
		predicted_labels = stripped.idxmax(axis=1).values
		predicted_probs = stripped.max(axis=1).values
		actual_probs = stripped.apply(lambda r: r.loc[r.name], axis=1).values
		return AccuracyFrame({
			'label': actual_labels,
			'well': wells,
			'run': runs,
			'prediction': predicted_labels,
			'score': actual_probs*100.0,
			'score_for_prediction': predicted_probs*100.0
		})

	@classmethod
	def read_csv(cls, path: Path, *args, **kwargs):
		path = Path(path)
		decision = pd.read_csv(path)
		# these are unfortunately needed to handle slightly older data
		if 'Unnamed: 0' in decision.columns:
			decision = decision.rename(columns={'Unnamed: 0': 'label'})
		if 'well' not in decision.columns:
			decision['well'] = None
		if 'run' not in decision.columns:
			decision['run'] = None
		return DecisionFrame(decision.set_index(['label', 'well', 'run']))


__all__ = ['DecisionFrame']
