# A logger that writes to both a file and stdout

import os
import logging
from typing import Optional


def init_logger(log_path: Optional[str]=None, format: str='%(asctime)s %(levelname)-8s: %(message)s', to_std: bool=True, child_logger_name: Optional[str]=None):
	"""Initializes a logger that can write to a log file and/or stdout."""

	if log_path is not None and not os.path.exists(os.path.dirname(log_path)):
		os.mkdir(os.path.dirname(log_path))

	if child_logger_name is None: logger = logging.getLogger()
	else: logger = logging.getLogger(child_logger_name)

	formatter = logging.Formatter(format)

	if log_path is not None:
		handler = logging.FileHandler(log_path)
		handler.setFormatter(formatter)
		logger.addHandler(handler)

	if to_std:
		handler = logging.StreamHandler()
		handler.setFormatter(formatter)
		logger.addHandler(handler)
