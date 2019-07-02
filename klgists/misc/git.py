import re
from klgists.common.exceptions import ExternalCommandFailed, ParsingFailedException
from klgists.common import abcd


@abcd.dataclass(frozen=True)
class GitDescription:
	text: str
	tag: str
	commits: str
	hash: str
	is_dirty: bool
	is_broken: bool

	@staticmethod
	def parse(text: str):
		pat = re.compile('''([\d.]+)-(\d+)-g([0-9a-h]{40})(?:-([a-z]+))?''')
		# ex: 1.8.6-43-g0ceb89d3a954da84070858319f177abe3869752b-dirty
		m = pat.fullmatch(text)
		if m is None: raise ParsingFailedException("Bad git describe string {}".format(text))
		# noinspection PyArgumentList
		return GitDescription(text, m.group(1), int(m.group(2)), m.group(3), m.group(4)=='dirty', m.group(4)=='broken')

	def __repr__(self):
		return self.__class__.__name__ + '(' + self.text + ')'
	def __str__(self): return repr(self)


class GitTools:

	@staticmethod
	def commit_hash(git_repo_dir: str = '.') -> str:
		"""Gets the hex of the most recent Git commit hash in git_repo_dir."""
		return GitTools.description(git_repo_dir).hash

	@staticmethod
	def description(git_repo_dir: str = '.') -> GitDescription:
		from subprocess import Popen, PIPE
		p = Popen('git describe --long --dirty --broken --abbrev=40 --tags'.split(' '), stdout=PIPE, cwd=git_repo_dir)
		(out, err) = p.communicate()
		exit_code = p.wait()
		if exit_code != 0: raise ExternalCommandFailed("Got nonzero exit code {} from git describe".format(exit_code))
		return GitDescription.parse(out.decode('utf-8').strip())


__all__ = ['GitDescription', 'GitTools']
