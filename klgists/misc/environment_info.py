import os
import sys
import getpass
import platform
import psutil
import cpuinfo
import socket
from typing import Dict, Any, Optional
from klgists.misc.commit_hash import git_commit_hash
from klgists.common.datetime_utils import now


def find_environment_info(extras: Optional[Dict[str, Any]]=None) -> Dict[str, str]:
	"""Get a dictionary of some system and environment information."""
	if extras is None: extras = {}
	mains = {
			'os_release': platform.platform(),
			'hostname': socket.gethostname(),
			'username': getpass.getuser(),
			'python_version': sys.version,
			'shell': os.environ['SHELL'],
			'disk_used': psutil.disk_usage('.').used,
			'disk_free': psutil.disk_usage('.').free,
			'memory_used': psutil.virtual_memory().used,
			'memory_available': psutil.virtual_memory().available,
			'cpu': cpuinfo.get_cpu_info()['brand'],
			'sauronx_hash': git_commit_hash(),
			'environment_info_capture_datetime': now().isoformat()
	}
	return  {k: str(v) for k, v in {**mains, **extras}.items()}
