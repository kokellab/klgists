# coding=utf-8

import os
import json
import logging
from typing import Dict
from carp.connection import Connection

# set this
config_env_var = None

db = None

class GlobalConnection(Connection):

	@classmethod
	def from_env_var(cls):
		if config_env_var in os.environ:
			return GlobalConnection.from_json(os.environ[config_env_var])
		else:
			raise ValueError("Environment variable {} not set".format(config_env_var))

	@classmethod
	def from_json(cls, config_path: str):
		if os.path.isfile(config_path) and os.access(config_path, os.R_OK):
			logging.info("Using connection from {}='{}'".format(config_env_var, config_path))
			with open(config_path) as jscfg:
				return cls(**json.load(jscfg))
		else:
			raise ValueError("{} does not exist, is not a file, or is not readable".format(config_path))

	@classmethod
	def from_dict(cls, dct: Dict[str, str]):
		return cls(**dct)
