# coding=utf-8

import hashlib
import os
import gzip

algorithm = hashlib.sha1
extension = '.sha1'

def hashsum(file_name: str) -> str:
    with open(file_name, 'rb') as f:
        return algorithm(f.read()).hexdigest()

def add_hash(file_name: str) -> None:
    with open(file_name + extension, 'w') as f:
        f.write(hashsum(file_name))

def check_hash(file_name: str) -> bool:
    if not os.path.isfile(file_name + extension): return False
    with open(file_name + extension, 'r') as f:
        return f.read() == hashsum(file_name)

def check_and_open(file_name: str, *args):
    return __o(file_name, opener=open, *args)

def check_and_open_gzip(file_name: str, *args):
    return __o(file_name, opener=gzip.open, *args)

def __o(file_name: str, opener, *args):
    if not os.path.isfile(file_name + extension):
        raise ValueError("Hash for file {} does not exist".format(file_name))
    with open(file_name + extension, 'r') as f:
        if f.read() != hashsum(file_name):
            raise ValueError("Hash for file {} does not match".format(file_name))
    return opener(file_name, *args)

