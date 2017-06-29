import re
from collections import OrderedDict


SUFFIXES = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']


def bytes_to_humanreadable(nbytes):
    "Keyword converts given number of bytes to human readable format"
    nbytes = int(nbytes)
    if nbytes == 0:
        return '0B'
    i = 0
    while nbytes >= 1024 and i < len(SUFFIXES)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s%s' % (f, SUFFIXES[i])


def metric_humanreadable_to_bytes(hum_str):
    """Converts humanreadable format (e.g. 10GB to bytes)"""
    regexp = '([0-9\.]+)([A-Z]+)'
    res = re.findall(regexp, hum_str)
    # expected res [('5.5', 'MB')]
    num = res[0][0]
    letter = res[0][1]
    num = float(num)
    prefix = {SUFFIXES[0]: 1}
    for i, s in enumerate(SUFFIXES[1:]):
        prefix[s] = 1 << (i+1)*10
    # prefix dict is like the following:
    # {'B': 1, 'KB': 1024,'MB': 1048576...}
    return float(num * prefix[letter])


def humanreadable_to_bytes(size):
    "Converts humanreadable format to size in Bytes eg 1MB - 1048576"
    action_dict = {
        'B': 0,
        'KB': 1,
        'MB': 2,
        'GB': 3,
        'TB': 4
    }
    _, size, suffix = re.split('([0-9.]+)', size)
    # expected out ['', '1.11', 'MB']
    size = float(size) * 1024.0 ** action_dict[suffix]

    return size


def human_to_seconds(human_date):
    "Converts human readable time  e.g. 1h:28m:13s to seconds"
    interval_dict = OrderedDict([("Y", 365*86400),  # 1 year
                                ("M", 30*86400),   # 1 month
                                ("W", 7*86400),    # 1 week
                                ("d", 86400),      # 1 day
                                ("h", 3600),       # 1 hour
                                ("m", 60),         # 1 minute
                                ("s", 1)])         # 1 second
    human_date = human_date.replace(':', '')

    interval_exc = "Bad interval format for {0}".format(human_date)

    interval_regex = re.compile("^(?P<value>[0-9]+)(?P<unit>[{0}])".
                                format("".join(interval_dict.keys())))
    seconds = 0

    while human_date:
        match = interval_regex.match(human_date)
        if match:
            value, unit = int(match.group("value")), match.group("unit")
            if unit in interval_dict:
                seconds += value * interval_dict[unit]
                human_date = human_date[match.end():]
            else:
                raise Exception(interval_exc)
        else:
            raise Exception(interval_exc)
    return seconds
