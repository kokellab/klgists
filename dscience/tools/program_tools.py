import re
from dscience_gists.core.exceptions import ExternalCommandError, ParsingFailedError
from dscience_gists.core import abcd
from dscience_gists.tools.base_tools import BaseTools


@abcd.dataclass(frozen=True)
class GitDescription:
	text: str
	tag: str
	commits: str
	hash: str
	is_dirty: bool
	is_broken: bool

	@classmethod
	def parse(cls, text: str):
		pat = re.compile(r'([\d.]+)-(\d+)-g([0-9a-h]{40})(?:-([a-z]+))?')
		# ex: 1.8.6-43-g0ceb89d3a954da84070858319f177abe3869752b-dirty
		m = pat.fullmatch(text)
		if m is None: raise ParsingFailedError("Bad git describe string {}".format(text))
		# noinspection PyArgumentList
		return GitDescription(text, m.group(1), int(m.group(2)), m.group(3), m.group(4)=='dirty', m.group(4)=='broken')

	def __repr__(self):
		return self.__class__.__name__ + '(' + self.text + ')'
	def __str__(self): return repr(self)


class ProgramTools(BaseTools):

	@classmethod
	def commit_hash(cls, git_repo_dir: str = '.') -> str:
		"""Gets the hex of the most recent Git commit hash in git_repo_dir."""
		return cls.git_description(git_repo_dir).hash

	@classmethod
	def git_description(cls, git_repo_dir: str = '.') -> GitDescription:
		from subprocess import Popen, PIPE
		p = Popen('git describe --long --dirty --broken --abbrev=40 --tags'.split(' '), stdout=PIPE, cwd=git_repo_dir)
		(out, err) = p.communicate()
		exit_code = p.wait()
		if exit_code != 0: raise ExternalCommandError("Got nonzero exit code {} from git describe".format(exit_code))
		return GitDescription.parse(out.decode('utf-8').strip())


__all__ = ['GitDescription', 'ProgramTools']
