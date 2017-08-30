import sys
import os
import argparse
import logging
import shutil
from typing import List, Any, Callable, Optional, Union

from colorama import Fore

from klgists.common.exceptions import PathIsNotDirectoryException
from klgists.common import pexists, pdir
from klgists.files.make_dirs import make_dirs


class SubcommandHandler:
	"""A convenient wrapper for a program that uses command-line subcommands.
	Calls any method that belongs to the target
	:param parser: Should contain a description and help text, but should NOT contain any arguments.
	:param target: An object (or type) that contains a method for each subcommand; a dash (-) in the argument is converted to an underscore.
	:param temp_dir: A temporary directory
	:param error_handler: Called logging any exception except for KeyboardInterrupt or SystemExit (exceptions in here are ignored)
	:param cancel_handler: Called after logging a KeyboardInterrupt or SystemExit (exceptions in here are ignored)
	"""

	parser = None  # type: argparse.ArgumentParser
	target = None  # type: Any
	temp_dir = None  # type: str
	error_handler = None  # type: Callable[[BaseException], None]
	cancel_handler = None  # type: Callable[[Union[KeyboardInterrupt, SystemExit]], None]

	def __init__(self,
			parser: argparse.ArgumentParser, target: Any,
			temp_dir: Optional[str] = None,
			error_handler: Callable[[BaseException], None] = lambda e: None,
			cancel_handler: Callable[[Union[KeyboardInterrupt, SystemExit]], None] = lambda e: None
	) -> None:
		parser.add_argument('subcommand', help='Subcommand to run')
		self.parser = parser
		self.target = target
		self.temp_dir = temp_dir
		self.error_handler = error_handler
		self.cancel_handler = cancel_handler


	def run(self, args: List[str]) -> None:

		full_args = self.parser.parse_args(args[1:2])
		subcommand = full_args.subcommand.replace('-', '_')

		if not hasattr(self, subcommand) and not subcommand.startswith('_'):
			print(Fore.RED + 'Unrecognized subcommand {}'.format(subcommand))
			self.parser.print_help()
			exit(1)

		# clever; from Chase Seibert: https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
		# use dispatch pattern to invoke method with same name
		try:
			if self.temp_dir is not None:
				if pexists(self.temp_dir) and pdir(self.temp_dir): shutil.rmtree(self.temp_dir)
				elif pexists(self.temp_dir): raise PathIsNotDirectoryException(self.temp_dir)
				make_dirs(self.temp_dir)
			getattr(self.target, subcommand)()
		except (KeyboardInterrupt, SystemExit) as e:
			try:
				logging.error("Received cancellation signal")
				logging.exception(e)
				self.cancel_handler(e)
			except BaseException: pass
			raise e
		except BaseException as e:
			try:
				logging.error("{} failed!".format(self.parser.prog))
				logging.exception(e)
				self.error_handler(e)
			except BaseException: pass
			raise e
		finally:
			if self.temp_dir is not None:
				if pexists(self.temp_dir):
					shutil.rmtree(self.temp_dir)
			sys.stdout = open(os.devnull, 'w')
			sys.exit()  # TODO workaround
