import typing
from typing import Dict
from enum import Enum
from dscience.core.exceptions import OutOfRangeError

class Edge(Enum):
	LEFT = 1
	RIGHT = 2
	TOP = 3
	BOTTOM = 4

class Axis(Enum):
	HORIZONTAL = 1
	VERTICAL = 2


class RoiError(OutOfRangeError):
	def __init__(self, message, errors=None):
		super().__init__(message, errors)
		self.edge = None
		self.axis = None
	def on_edge(self, edge: Edge): self.edge = edge; return self
	def on_axis(self, axis: Axis): self.axis = axis; return self


class RoiOutOfBoundsError(RoiError): pass
class FlippedRoiBoundsError(RoiError): pass


class Roi:
	def __init__(self, x0: int, y0: int, x1: int, y1: int) -> None:
		if x0 < 0: raise RoiOutOfBoundsError("x0 is negative ({})".format(x0)).on_edge(Edge.LEFT)
		if y0 < 0: raise RoiOutOfBoundsError("y0 is negative ({})".format(y0)).on_edge(Edge.TOP)
		if x0 >= x1: raise FlippedRoiBoundsError("x0 ({}) is past (or equal to) x1 ({})".format(x0, x1)).on_axis(Axis.HORIZONTAL)
		if y0 >= y1: raise FlippedRoiBoundsError("y0 ({}) is past (or equal to) y1 ({})".format(y0, y1)).on_axis(Axis.VERTICAL)
		self.x0 = x0
		self.y0 = y0
		self.x1 = x1
		self.y1 = y1

	def __repr__(self) -> str:
		return "({},{})→({},{})".format(self.x0, self.y0, self.x1, self.y1)
	def __str__(self): return repr(self)


class WellRoi(Roi):
	def __init__(self, row: int, column: int, x0: int, y0: int, x1: int, y1: int) -> None:
		if row < 0: raise OutOfRangeError("Row is negative ({})".format(row), value=row)
		if column < 0: raise OutOfRangeError("Column is negative ({})".format(row))
		super().__init__(x0, y0, x1, y1)
		self.row_index = row
		self.column_index = column

	def __repr__(self) -> str:
		return "{},{}=({},{})→({},{})".format(self.row_index, self.column_index, self.x0, self.y0, self.x1, self.y1)
	def __str__(self): return repr(self)


class PlateRois:
	def __init__(self, n_rows: int, n_columns: int, image_roi: Roi, top_left_roi: Roi, padx: float, pady: float):
		self.n_rows = n_rows
		self.n_columns = n_columns
		self.image_roi = image_roi
		self.well_rois = self._get_roi_coordinates(top_left_roi, padx, pady)

	def __repr__(self) -> str:
		return "PlateRois(img={}; wells={}".format(self.image_roi, self.well_rois.values())
	def __str__(self) -> str: return repr(self)

	def __iter__(self):
		return iter(self.well_rois.keys())
	def __len__(self):
		return len(self.well_rois)
	def __getitem__(self, item):
		try:
			return self.well_rois[item[0], item[1]]
		except (IndexError, AttributeError):
			raise TypeError("Must look up well ROIs by (row, column) tuple indices.")

	def _get_roi_coordinates(self, top_left_roi: Roi, padx: float, pady: float) -> Dict[typing.Tuple[int, int], WellRoi]:
		tl = top_left_roi
		width = top_left_roi.x1 - top_left_roi.x0
		height = top_left_roi.y1 - top_left_roi.y0
		# make sure the wells don't extend outside the image bounds
		# noinspection DuplicatedCode
		if tl.x0 < self.image_roi.x0:
			raise RoiOutOfBoundsError("").on_edge(Edge.LEFT)
		wells_x_edge = tl.x0 + self.n_columns * width + (self.n_columns - 1) * padx
		if wells_x_edge > self.image_roi.x1:
			raise RoiOutOfBoundsError("").on_edge(Edge.RIGHT)
		# noinspection DuplicatedCode
		if tl.y0 < self.image_roi.y0:
			raise RoiOutOfBoundsError("").on_edge(Edge.TOP)
		wells_y_edge = tl.y0 + self.n_rows * height + (self.n_rows - 1) * pady
		if wells_y_edge > self.image_roi.y1:
			raise RoiOutOfBoundsError("").on_edge(Edge.BOTTOM)
		# now build
		rois = {}
		x = tl.x0
		y = tl.y0
		for row in range(0, self.n_rows):
			for column in range(0, self.n_columns):
				rois[(row, column)] = WellRoi(row, column, x, y, x + width, y + height)
				x += width + padx
			y += height + pady
			x = tl.x0
		return rois


__all__ = ['Roi', 'WellRoi', 'PlateRois']
