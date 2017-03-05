# coding=utf-8

import json
from sshtunnel import SSHTunnelForwarder
import pymysql
import peewee
import contextlib
import logging
from typing import Tuple, Iterator, Dict

class Connection:

	_ssh_username = None
	_ssh_password = None
	_db_username = None
	_db_password = None
	_db_name = None
	_ssh_host = None
	_ssh_port = None
	_db_port = None

	_tunnel = None
	plain_sql_database = None
	peewee_database = None

	def __init__(self, ssh_username: str, ssh_password: str, db_username: str, db_password: str, db_name: str,
				ssh_host: str="localhost", ssh_port: int=22,
				db_port: int=3306):
		self._ssh_username = ssh_username
		self._ssh_password = ssh_password
		self._db_username = db_username
		self._db_password = db_password
		self._db_name = db_name
		self._ssh_host = ssh_host
		self._ssh_port = ssh_port
		self._db_port = db_port
		self._tunnel = SSHTunnelForwarder((self._ssh_host, self._ssh_port),
										  ssh_username=self._ssh_username, ssh_password=self._ssh_password,
										  remote_bind_address=('localhost', self._db_port))

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
		self._tunnel.start()
		logging.info("Opened SSH tunnel to host {} on port {}".format(self._ssh_host, self._ssh_port))

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
		return {'user': self._db_username, 'password': self._db_password, 'host': '127.0.0.1', 'port': self._tunnel.local_bind_port}
