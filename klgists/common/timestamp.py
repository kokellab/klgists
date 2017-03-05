# coding=utf-8

import datetime

def format_time(time: datetime.datetime) -> str:
    """Standard timestamp format. Ex: 2016-05-02_22_35_56."""
    return time.strftime("%Y-%m-%d_%H-%M-%S")

def timestamp() -> str:
    """Standard timestamp of time now. Ex: 2016-05-02_22_35_56."""
    return format_time(datetime.datetime.now())

def timestamp_path(path: str) -> str:
    """Standard way to label a file path with a timestamp."""
    return "{}-{}".format(path, timestamp())
