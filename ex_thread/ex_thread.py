import threading
import traceback
import Queue
from multiprocessing import TimeoutError
import logging

logger = logging.getLogger("thread")

def run_commands_in_thread(commands, args=()):
    threads = list()
    out = list()
    for command in commands:
        thread = ExThread(target=command, args=args)
        threads.append(thread)
        thread.start()
    for thread in threads:
        result = thread.join()
        out.append(result)
    return out


def run_with_timeout(command, args=(), timeout=300, raise_on_timeout=True):
    # initialize the thread_join variable
    thread_join = None
    thread = ExThread(target=command, args=args)
    thread.start()
    try:
        thread_join = thread.join(timeout)
    except TimeoutError as e:
        if raise_on_timeout:
            raise e
    return thread_join


class ExThread(threading.Thread):
    def __init__(
            self, group=None, target=None, name=None,
            args=(), kwargs=None, verbose=None):

        threading.Thread.__init__(
            self, group, target, name, args, kwargs, verbose)
        self.__status_queue = Queue.Queue()
        self.target = target
        self.result = None
        self.args = args
        if kwargs is None:
            kwargs = {}
        self.kwargs = kwargs
        self.daemon = True

    def run(self):
        """This method should NOT be overriden."""
        logger.debug(
            'Starting %s %s(%s, %s)' % (
                self.name, self.target, self.args, self.kwargs))

        try:
            self.result = self.target(*self.args, **self.kwargs)
            self.__status_queue.put((None, None))
        except Exception as e:
            e_traceback = traceback.format_exc()
            self.__status_queue.put((e, e_traceback))

    def wait_for_exc_info(self):
        return self.__status_queue.get()

    def join_with_exception(self):
        e, trace = self.wait_for_exc_info()
        if e is None:
            logger.debug('Got %s from %s %s' % (
                self.result, self.name, self.target))
        else:
            logger.debug(trace)
            raise e

    def join(self, timeout=None):
        if timeout is not None:
            logger.debug(
                'Waiting for %s thread %s target for %s seconds...' % (
                    self.name, self.target, timeout))
        else:
            logger.debug(
                'WARNING: joining %s thread without timeout' % self.name)

        threading.Thread.join(self, timeout)
        if self.is_alive() is True:
            raise TimeoutError(
                'Timeout of %ss for thread %s join occurred. '
                'Target: %s, args: %s, kwargs: %s' % (
                    timeout, self.name, self.target,
                    self.args, self.kwargs))
        self.join_with_exception()
        return self.result
