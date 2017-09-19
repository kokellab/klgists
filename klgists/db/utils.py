import struct
from array import array
import numpy as np


def blob_to_byte_array(bytes_obj):
	return np.array([z[0] + 128 for z in struct.iter_unpack('>b', bytes_obj)])
def blob_to_float_array(bytes_obj):
	return _blob_to_dt(bytes_obj, '>f')
def blob_to_double_array(bytes_obj):
	return _blob_to_dt(bytes_obj, '>d')
def blob_to_short_array(bytes_obj):
	return _blob_to_dt(bytes_obj, '>H')
def blob_to_int_array(bytes_obj):
	return _blob_to_dt(bytes_obj, '>I')
def blob_to_long_array(bytes_obj):
	return _blob_to_dt(bytes_obj, '>Q')
def _blob_to_dt(bytes_obj, data_type_str: str):
	return np.array([z[0] for z in struct.iter_unpack(data_type_str, bytes_obj)])


def byte_array_to_blob(arr):
	return array('b', [(x - 128) for x in arr]).tobytes()
def float_array_to_blob(arr):
	return _dt_to_blob(arr, '>f')
def double_array_to_blob(arr):
	return _dt_to_blob(arr, '>d')
def short_array_to_blob(arr):
	return _dt_to_blob(arr, '>H')
def int_array_to_blob(arr):
	return _dt_to_blob(arr, '>I')
def long_array_to_blob(arr):
	return _dt_to_blob(arr, '>Q')
def _dt_to_blob(arr, data_type_str: str):
	return array(data_type_str, [x for x in arr]).tobytes()
