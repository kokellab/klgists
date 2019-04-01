# A logger that writes to both a file and stdout

import os
import logging
from typing import Optional
from deprecated import deprecated


@deprecated(reason="Use klgists.common.flexible_logger instead.")
def init_logger(
	log_path: Optional[str]=None,
	format_str: str='%(asctime)s %(levelname)-8s: %(message)s',
	to_std: bool=True,
	child_logger_name: Optional[str]=None,
	std_level = logging.INFO,
	file_level = logging.DEBUG
):
	"""Initializes a logger that can write to a log file and/or stdout."""

	if log_path is not None and not os.path.exists(os.path.dirname(log_path)):
		os.mkdir(os.path.dirname(log_path))

	if child_logger_name is None:
		logger = logging.getLogger()
	else:
		logger = logging.getLogger(child_logger_name)
	logger.setLevel(logging.NOTSET)

	formatter = logging.Formatter(format_str)

	if log_path is not None:
		handler = logging.FileHandler(log_path, encoding='utf-8')
		handler.setLevel(file_level)
		handler.setFormatter(formatter)
		logger.addHandler(handler)

	if to_std:
		handler = logging.StreamHandler()
		handler.setLevel(std_level)
		handler.setFormatter(formatter)
		logger.addHandler(handler)


__all__ = ['init_logger']
