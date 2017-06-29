"""
Creates and stores timestamp common for tests
"""
import time
import datetime

TEST_START_TIME = time.time()
TIMESTAMP = time.strftime("%Y-%m-%d-%H-%M-%S")


def convert_time_to_epoch(time_string, format_str="%Y-%m-%d %H:%M:%S"):
    epoch_time = time.mktime(datetime.datetime.strptime(
        time_string, format_str).timetuple())
    return epoch_time
