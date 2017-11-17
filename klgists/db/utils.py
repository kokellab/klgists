import struct
from array import array
import numpy as np


def blob_to_byte_array(bytes_obj: bytes):
	return _blob_to_dt(bytes_obj, 'b', 1) + 128
def blob_to_float_array(bytes_obj: bytes):
	return _blob_to_dt(bytes_obj, 'f', 4)
def blob_to_double_array(bytes_obj: bytes):
	return _blob_to_dt(bytes_obj, 'd', 8)
def blob_to_short_array(bytes_obj: bytes):
	return _blob_to_dt(bytes_obj, 'H', 2)
def blob_to_int_array(bytes_obj: bytes):
	return _blob_to_dt(bytes_obj, 'I', 4)
def blob_to_long_array(bytes_obj: bytes):
	return _blob_to_dt(bytes_obj, 'Q', 8)
def _blob_to_dt(bytes_obj: bytes, data_type_str: str, data_type_len: int):
	return np.array(next(iter(struct.iter_unpack('>' + data_type_str * int(len(bytes_obj)/data_type_len), bytes_obj))))


def byte_array_to_blob(arr: np.array):
	return _dt_to_blob(arr - 128, '>b')
def float_array_to_blob(arr: np.array):
	return _dt_to_blob(arr, '>f')
def double_array_to_blob(arr: np.array):
	return _dt_to_blob(arr, '>d')
def short_array_to_blob(arr: np.array):
	return _dt_to_blob(arr, '>H')
def int_array_to_blob(arr: np.array):
	return _dt_to_blob(arr, '>I')
def long_array_to_blob(arr: np.array):
	return _dt_to_blob(arr, '>Q')
def _dt_to_blob(arr: np.array, data_type_str: str) -> bytes:
	return array(data_type_str, arr).tobytes()
