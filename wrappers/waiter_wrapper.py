import logging
import traceback
from functools import wraps
from time import sleep, time

logger = logging.getLogger("wrapper")

def waiter_wrapper(
        top_attempts=150, sleep_time=2, exception_types=(
            AssertionError, AssertionErrorWithInfo),
        action_on_fail=None):
    """Function takes given keyword with arguments and tries to run it until
    its finished successfully. Usage:

        waiter_wrapper(top_attempts, sleep_time)(keyword)(args)

        waiter_wrapper(
        top_attempts, sleep_time, action_on_fail=some_function)(keyword)(args)

        if some_function need to get args it has to be prepared like:
        functools.partial(some_function, fail_args, )

    where top_attempts, sleep_time and action_on_fail are optional
    keyword - some keyword
    args - args for keyword"""

    def outer_wrapper(keyword):
        @wraps(keyword)
        def inner_wrapper(*args, **kwargs):
            for i in range(int(top_attempts)):
                try:
                    result = keyword(*args, **kwargs)
                    break
                except exception_types as e:
                    logger.debug(
                        'Keyword %s finished unsuccessfully, '
                        'because of following error: %s' % (keyword, e))
                    if i != int(top_attempts)-1:
                        logger.debug('Waiting %s seconds...' % sleep_time)
                        sleep(int(sleep_time))

                        if action_on_fail is not None:
                            logger.debug(
                                'Trying action on fail %s ...' %
                                action_on_fail)
                            action_on_fail()

                    else:
                        logger.debug(
                            'No attempts left while waiting keyword to be '
                            'finished successfully')
                        raise e
            return result
        return inner_wrapper
    return outer_wrapper


def loop_wrapper(time_to_run=600):
    """Runs function in a loop for given time"""
    def outer_wrapper(keyword):
        @wraps(keyword)
        def inner_wrapper(*args, **kwargs):
            start_time = time()
            while (time() - start_time) <= time_to_run:
                keyword(*args, **kwargs)
        return inner_wrapper
    return outer_wrapper


def exception_wrapper(exception_types=(Exception, )):
    """Wrapper prevents exceptions during function execution"""
    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except exception_types as e:
                logger.debug(e)
                logger.debug("Got error %s, traceback is %s" % (
                    e,  traceback.format_exc()))
        return inner_wrapper
    return outer_wrapper
