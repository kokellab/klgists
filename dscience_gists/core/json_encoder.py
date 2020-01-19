import json
from datetime import date, datetime
import numpy as np

class JsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, np.ndarray):
			return obj.tolist()
		elif isinstance(obj, (datetime, date)):
			return obj.isoformat()
		return json.JSONEncoder.default(self, obj)

__all__ = ['JsonEncoder']
