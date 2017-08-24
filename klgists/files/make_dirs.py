import os

from klgists.common.exceptions import PathIsNotDirectoryException

def make_dirs(output_dir: str):
    """Makes a directory if it doesn't exist."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    elif not os.path.isdir(output_dir):
        raise PathIsNotDirectoryException("{} already exists and is not a directory".format(output_dir))
