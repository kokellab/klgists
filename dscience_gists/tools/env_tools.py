from typing import Optional, Mapping, Any
from datetime import datetime
import os, platform, socket, sys, psutil
from getpass import getuser
from dscience_gists.tools.base_tools import BaseTools

class EnvTools(BaseTools):

	@classmethod
	def get_env_info(cls, extras: Optional[Mapping[str, Any]] = None) -> Mapping[str, str]:
		"""
		Get a dictionary of some system and environment information.
		Includes os_release, hostname, username, mem + disk, shell, etc.
		"""
		if extras is None: extras = {}
		mains = {
			'os_release': platform.platform(),
			'hostname': socket.gethostname(),
			'username': getuser(),
			'python_version': sys.version,
			'shell': os.environ['SHELL'],
			'disk_used': psutil.disk_usage('.').used,
			'disk_free': psutil.disk_usage('.').free,
			'memory_used': psutil.virtual_memory().used,
			'memory_available': psutil.virtual_memory().available,
			'environment_info_capture_datetime': datetime.now().isoformat()
		}
		return {k: str(v) for k, v in {**mains, **extras}.items()}


__all__ = ['EnvTools']
