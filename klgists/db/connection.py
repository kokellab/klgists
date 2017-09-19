import os, json, logging
from typing import Tuple, Iterator, Dict, Optional, Union

from sshtunnel import SSHTunnelForwarder
import pymysql
import peewee



class Connection:
	"""Convenient way to open a database connection through an SSH tunnel for Pewee or raw SQL.
	You can use an existing tunnel by giving it a local port (local_bind_port) or have it create a new one by giving it an SSH hostname.
	Example usage:
	with Connection(db_name, db_user, db_password) as db:
		db.connect_with_peewee()     # don't worry, this will be closed with the GlobalConnection
		from mymodel.model import *  # you MUST import this AFTER setting global_connection.db
		do_my_stuff()

	Or:
		with Connection.from_json('a_json_file'):
			...
	The JSON file will need to specify a value for each argument in the constructor.
	"""

	_ssh_username = None
	_ssh_password = None
	_db_username = None
	_db_password = None
	_db_name = None
	_ssh_host = None
	_ssh_port = None
	_local_bind_port = None
	_db_port = None

	_tunnel = None
	plain_sql_database = None
	peewee_database = None

	def __init__(self,
			db_name: str, db_username: str, db_password: str,
			ssh_host: Optional[str] = None,
			local_bind_port: Optional[int] = None,
			ssh_port: int = 22,
			db_port: int = 3306
	):
		if (ssh_host is None) == (local_bind_port is None):
			raise ValueError("Must specify either an SSH host to create a tunnel, or the local bind port of an existing tunnel (but not both)")
		self._local_bind_port = local_bind_port
		self._db_username = db_username
		self._db_password = db_password
		self._db_name = db_name
		self._ssh_host = ssh_host
		self._ssh_port = ssh_port
		self._db_port = db_port
		if ssh_host is not None:
			self._tunnel = SSHTunnelForwarder(
				(self._ssh_host, self._ssh_port),
				ssh_username=self._ssh_username, ssh_password=self._ssh_password,
				remote_bind_address=('localhost', self._db_port)
			)

	@classmethod
	def from_json(cls, config_path: str):
		if os.path.isfile(config_path) and os.access(config_path, os.R_OK):
			logging.info("Using Valar connection from '{}'".format(config_path))
			with open(config_path) as jscfg:
				params = json.load(jscfg)  # type: Dict[str, Union[str, int, None]]
				return cls(**params)
		else:
			raise ValueError("{} does not exist, is not a file, or is not readable".format(config_path))

	@classmethod
	def from_dict(cls, dct: Dict[str, str]):
		return cls(**dct)

	def connect_with_peewee(self):
		self.peewee_database = peewee.MySQLDatabase(self._db_name, **self._connection_params())
		self.peewee_database.connect()
		return self.peewee_database

	def connect_with_plain_sql(self):
		self.plain_sql_database = pymysql.connect(**self._connection_params(), db=self._db_name, cursorclass=pymysql.cursors.DictCursor)
		logging.debug("Opened raw pymysql connection to database {}".format(self._db_name))

	def execute(self, statement: str, vals: Tuple = ()) -> None:
		with self.plain_sql_database.cursor() as cursor:
			cursor.execute(statement, vals)
			self.plain_sql_database.commit()

	def select(self, statement: str, vals: Tuple = ()) -> Iterator[Dict]:
		with self.plain_sql_database.cursor() as cursor:
			cursor.execute(statement, vals)
			return cursor

	def __enter__(self):
		self.open()
		return self

	def open(self):
		if self._tunnel is not None:
			self._tunnel.start()
			logging.info("Opened SSH tunnel to host {} on port {}".format(self._ssh_host, self._ssh_port))
		else:
			logging.info("Assuming an SSH tunnel already exists for database connection.")

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	def close(self):
		if self._tunnel is not None:
			self._tunnel.close()
			logging.info("Closed SSH tunnel")
		if self.plain_sql_database is not None:
			self.plain_sql_database.close()
			logging.info("Closed raw pymysql connection")
		if self.peewee_database is not None:
			logging.info("Closed peewee pymysql connection")
			self.peewee_database.close()

	def _connection_params(self):
		local_bind_port = self._tunnel.local_bind_port if self._tunnel is not None else self._local_bind_port
		return {'user': self._db_username, 'password': self._db_password, 'host': '127.0.0.1', 'port': local_bind_port}
