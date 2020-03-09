import logging
import textwrap
import contextlib
import subprocess
from typing import Callable, Optional, Sequence, Generator
from pathlib import PurePath
from enum import Enum
from copy import copy
from queue import Queue
from threading import Thread
from dscience_gists.core import DevNull
from dscience_gists.core.exceptions import ExternalCommandError
from dscience_gists.tools.base_tools import BaseTools
logger = logging.getLogger('dscience_gists')


class PipeType(Enum):
	STDOUT = 1
	STDERR = 2

@contextlib.contextmanager
def null_context(cls):
	yield


class CallTools(BaseTools):

	@classmethod
	@contextlib.contextmanager
	def silenced(cls, no_stdout: bool = True, no_stderr: bool = True) -> Generator[None, None, None]:
		"""
		Context manager that suppresses stdout and stderr.
		:return:
		"""
		with contextlib.redirect_stdout(DevNull()) if no_stdout else cls.null_context():
			with contextlib.redirect_stderr(DevNull()) if no_stderr else cls.null_context():
				yield

	@classmethod
	def call_cmd(cls, *cmd: str, **kwargs) -> subprocess.CompletedProcess:
		"""
		Calls subprocess.run with capture_output=True, and logs a debug statement with the command beforehand.
		:param cmd: A sequence to call
		:param kwargs: Passed to subprocess.run
		"""
		logger.debug("Calling '{}'".format(' '.join(cmd)))
		return subprocess.run(*[str(c) for c in cmd], capture_output=True, check=True, **kwargs)

	@classmethod
	def call_cmd_utf(cls, *cmd: str, log_fn: Callable[[str], None] = logger.error, **kwargs) -> subprocess.CompletedProcess:
		"""
		Like `call_cmd`, but sets `text=True` and `encoding=utf8`, and strips stdout and stderr of start/end whitespace before returning.
		Can also log formatted stdout and stderr on failure.
		Otherwise, logs the output, unformatted and unstripped, as TRACE
		"""
		logger.debug("Calling '{}'".format(' '.join(cmd)))
		kwargs = copy(kwargs)
		if 'cwd' in kwargs and isinstance(kwargs['path'], PurePath):
			kwargs['cwd'] = str(kwargs['cwd'])
		try:
			x = subprocess.run(*[str(c) for c in cmd], capture_output=True, check=True, text=True, encoding='utf8', **kwargs)
			logger.debug("stdout: '{}'".format(x.stdout))
			logger.debug("stderr: '{}'".format(x.stdout))
			x.stdout = x.stdout.strip()
			x.stderr = x.stderr.strip()
			return x
		except subprocess.CalledProcessError as e:
			if log_fn is not None:
				cls.log_called_process_error(e, log_fn)
			raise

	@classmethod
	def log_called_process_error(
			cls,
			e: subprocess.CalledProcessError,
			log_fn: Callable[[str], None],
			wrap_length: int = 80
	) -> None:
		"""
		Outputs some formatted text describing the error with its full stdout and stderr.
		:param e: The error
		:param log_fn: For example, `logger.warning`
		:param wrap_length: The max number of characters of the header and footer around the stdout and stderr
				The output text is wrapped to this value - 4
				The full line can be longer than this because the text of the command is not wrapped
		"""
		wrap_length = max(10, wrap_length)
		log_fn("Failed on command:[\n{}\n]".format(textwrap.indent("\n".join(['"' + x + '"' for x in e.cmd]), '\t')))
		log_fn("Received exit code {}".format(e.returncode))
		if e.stdout is not None and len(e.stdout.strip()) > 0:
			log_fn(' STDOUT '.center(wrap_length, '.'))
			log_fn(textwrap.indent(textwrap.wrap(e.stdout.strip(), wrap_length-4), '\t'))
			log_fn('.'*wrap_length)
		else:
			log_fn('《no stdout》')
		if e.stderr is not None and len(e.stderr.strip()) > 0:
			log_fn(' STDERR '.center(wrap_length, '.'))
			log_fn(textwrap.indent(textwrap.wrap(e.stderr.strip(), wrap_length-4), '\t'))
			log_fn('.'*wrap_length)
		else:
			log_fn('《no stderr》')

	@classmethod
	def stream_cmd_call(
			cls,
			cmd: Sequence[str], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
			cwd: Optional[str] = None, timeout_secs: Optional[float] = None,
			log_callback: Callable[[PipeType, bytes], None] = None, bufsize: int = 1
	) -> None:
		"""
		Processes stdout and stderr on separate threads, streamed -- can avoid filling a stdout or stderr buffer.
		Calls an external command, waits, and throws a ExternalCommandFailed for nonzero exit codes.
		Returns (stdout, stderr).
		"""
		if log_callback is None:
			log_callback = cls._smart_log_callback
		cmd = [str(p) for p in cmd]
		logger.debug("Streaming '{}'".format(' '.join(cmd)))
		p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, cwd=cwd, bufsize=bufsize)
		try:
			q = Queue()
			Thread(target=cls._reader, args=[PipeType.STDOUT, p.stdout, q]).start()
			Thread(target=cls._reader, args=[PipeType.STDERR, p.stderr, q]).start()
			for _ in range(2):
				for source, line in iter(q.get, None):
					log_callback(source, line)
			exit_code = p.wait(timeout=timeout_secs)
		finally:
			p.kill()
		if exit_code != 0:
			raise ExternalCommandError(
				"Got nonzero exit code {} from '{}'".format(exit_code, ' '.join(cmd)),
				' '.join(cmd), exit_code, '<<unknown>>', '<<unknown>>'
			)

	@classmethod
	def _smart_log_callback(cls, source, line, prefix: str = '') -> None:
		line = line.decode('utf-8')
		if line.startswith('FATAL:'):
			logger.fatal(prefix + line)
		elif line.startswith('ERROR:'):
			logger.error(prefix + line)
		elif line.startswith('WARNING:'):
			logger.warning(prefix + line)
		elif line.startswith('INFO:'):
			logger.info(prefix + line)
		elif line.startswith('DEBUG:'):
			logger.debug(prefix + line)
		else:
			logger.debug(prefix + line)

	@classmethod
	def _disp(cls, out, ell, name):
		out = out.strip()
		if '\n' in out:
			ell(name + ":\n<<=====\n" + out + '\n=====>>')
		elif len(out) > 0:
			ell(name + ": <<===== " + out + " =====>>")
		else:
			ell(name + ": <no output>")

	@classmethod
	def _log(cls, out, err, ell):
		cls._disp(out, ell, "stdout")
		cls._disp(err, ell, "stderr")

	@classmethod
	def _reader(cls, pipe_type, pipe, queue):
		try:
			with pipe:
				for line in iter(pipe.readline, b''):
					queue.put((pipe_type, line))
		finally:
			queue.put(None)


__all__ = ['CallTools']
