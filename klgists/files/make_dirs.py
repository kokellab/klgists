# coding=utf-8

import os

def make_dirs(output_dir: str):
    """Makes a directory if it doesn't exist."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    elif not os.path.isdir(output_dir):
        raise ValueError("{} already exists and is not a directory".format(output_dir))
