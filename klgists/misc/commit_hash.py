from subprocess import Popen, PIPE

def git_commit_hash(git_repo_dir: str='.') -> str:
	"""Gets the hex of the most recent Git commit hash in git_repo_dir."""
	p = Popen(['git', 'rev-parse', 'HEAD'], stdout=PIPE, cwd=git_repo_dir)
	(out, err) = p.communicate()
	exit_code = p.wait()
	if exit_code != 0: raise ValueError("Got nonzero exit code {} from git rev-parse".format(exit_code))
	return out.decode('utf-8').rstrip()

if __name__ == '__main__':
	print(git_commit_hash())
