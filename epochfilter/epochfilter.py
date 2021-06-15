#!/usr/bin/env python3

# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement


import errno
import os
import signal
import sys
import time
from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
from functools import wraps

import click
import dateparser
from asserttool import maxone
from asserttool import verify
from enumerate_input import enumerate_input
from humanize import naturaldelta
from humanize import naturaltime
from unitcalc import convert


def eprint(*args, **kwargs):
    if 'file' in kwargs.keys():
        kwargs.pop('file')
    print(*args, file=sys.stderr, **kwargs)


try:
    from icecream import ic  # https://github.com/gruns/icecream
    from icecream import icr  # https://github.com/jakeogh/icecream
except ImportError:
    ic = eprint
    icr = eprint


def timestamp_now():
    stamp = str("%.22f" % time.time())
    return stamp


def timestamp_to_epoch(date_time):
    #date_time = '2016-03-14T18:54:56.1942132'.split('.')[0]
    date_time = date_time.split('.')[0]
    pattern = '%Y-%m-%dT%H:%M:%S'
    epoch = int(time.mktime(time.strptime(date_time, pattern)))
    return epoch


def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te-ts))
        return result
    return timed


def get_mtime(infile):
    mtime = os.lstat(infile).st_mtime #does not follow symlinks
    return mtime


def get_amtime(infile):
    try:
        infile_stat = os.lstat(infile)
    except TypeError:
        infile_stat = os.lstat(infile.fileno())
    amtime = (infile_stat.st_atime_ns, infile_stat.st_mtime_ns)
    return amtime


def update_mtime_if_older(*, path, mtime, verbose, debug):
    verify(isinstance(mtime, tuple))
    verify(isinstance(mtime[0], int))
    verify(isinstance(mtime[1], int))
    current_mtime = get_amtime(path)
    if current_mtime[1] > mtime[1]:
        if verbose:
            eprint("{} old: {} new: {}".format(path, current_mtime[1], mtime[1]))
        os.utime(path, ns=mtime, follow_symlinks=False)


def timeout(seconds, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


# in epochfilter
#def human_date_to_timestamp(date):
#    dt = dateparser(date)
#    return dt.timestamp()


def seconds_duration_to_human_readable(seconds, ago):
    if seconds is None:
        return None
    seconds = float(seconds)
    if ago:
        result = naturaltime(seconds)
    else:
        result = naturaldelta(seconds)

    result = result.replace(" seconds", "s")
    result = result.replace("a second", "1s")

    result = result.replace(" minutes", "min")
    result = result.replace("a minute", "1min")

    result = result.replace(" hours", "hr")
    result = result.replace("an hour", "1hr")

    result = result.replace(" days", "days")
    result = result.replace("a day", "1day")

    result = result.replace(" months", "mo")
    result = result.replace("a month", "1mo")

    result = result.replace(" years", "yrs")
    result = result.replace("a year", "1yr")
    result = result.replace("1 year", "1yr")

    result = result.replace(" ago", "_ago")
    result = result.replace(", ", ",")
    return result



def human_date_to_timestamp(date):
    dt = dateparser.parse(date)
    timestamp = dt.timestamp()
    return Decimal(str(timestamp))


def timestamp_to_human_date(timestamp):
    timestamp = Decimal(str(timestamp))
    human_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S %Z')
    return human_date


def is_before(*,
              timestamp: Decimal,
              before: Decimal,
              inclusive: bool,
              verbose: bool,
              debug: bool,
              ):
    acceptable_results = [Decimal('-1')]
    if inclusive:
        acceptable_results.append(Decimal('0'))
    if debug:
        ic(acceptable_results)
    result = timestamp.compare(before)
    if debug:
        ic(result)
    if result not in acceptable_results:
        return False
    return True


def is_after(*,
             timestamp: Decimal,
             after: Decimal,
             inclusive: bool,
             verbose: bool,
             debug: bool,
             ):
    acceptable_results = [Decimal('1')]
    if inclusive:
        acceptable_results.append(Decimal('0'))
    if debug:
        ic(acceptable_results)
    result = timestamp.compare(after)
    if debug:
        ic(result)
    if result not in acceptable_results:
        return False
    return True


def print_result(*,
                 timestamp,
                 human: bool,
                 end: str,
                 verbose: bool,
                 debug: bool,
                 ):
    if human:
        human_date = timestamp_to_human_date(timestamp)
        if verbose:
            print(timestamp, human_date, end=end)
        else:
            print(human_date, end=end)
    else:
        print(timestamp, end=end)


@click.command()
@click.argument("timestamps", type=str, nargs=-1)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--before', type=str)
@click.option('--after', type=str)
@click.option('--around', type=str)
@click.option('--within', type=str)
@click.option('--oldest', is_flag=True)
@click.option('--newest', is_flag=True)
@click.option("--inclusive", is_flag=True)
@click.option("--human", is_flag=True)
@click.option("--exit-after-matches", type=int)
@click.option("--printn", is_flag=True)
def cli(timestamps,
        before: str,
        after: str,
        around: str,
        within: str,
        inclusive: bool,
        verbose: bool,
        debug: bool,
        oldest: bool,
        newest: bool,
        human: bool,
        printn: bool,
        exit_after_matches: int,
        ):

    null = not printn
    end = '\n'
    if null:
        end = '\0'
    if sys.stdout.isatty():
        end = '\n'
    if verbose:
        #ic(sys.stdout.isatty())
        ic(end)

    if verbose:
        ic(before, after)

    if within is not None:
        maxone([before, after, around], msg='--within requires one of --before/--after/--around')

    if around is not None:
        if within is None:
            raise ValueError('--around requires --within')
        if (before is not None) or (after is not None):
            raise ValueError('--around can not be used with --before/--after')

    if before is not None:
        try:
            before = Decimal(before)
        except InvalidOperation:
            before = human_date_to_timestamp(before)

    if after is not None:
        try:
            after = Decimal(after)
        except InvalidOperation:
            after = human_date_to_timestamp(after)

    if around is not None:
        try:
            around = Decimal(around)
        except InvalidOperation:
            around = human_date_to_timestamp(around)

    if within is not None:
        try:
            within = Decimal(within)
        except InvalidOperation:
            within_converted = convert(human_input_units=within,
                                       human_output_unit="seconds",
                                       verbose=verbose,
                                       debug=debug,)
            ic(within_converted)
            within = Decimal(within_converted.magnitude)
            ic(within)

        # at this point, before and after need to be configured
        assert before is None
        assert after is None

        after = around - within
        before = around + within
        ic(after, before)

    now = Decimal(time.time())

    if (before or after or within):
        ic(before, after, within, now)

    match_count = 0

    current_newest = None
    current_oldest = None
    for index, timestamp in enumerate_input(iterator=timestamps,
                                            null=null,
                                            skip=None,
                                            head=None,
                                            tail=None,
                                            debug=debug,
                                            verbose=verbose):

        try:
            timestamp = Decimal(timestamp)
        except InvalidOperation as e:
            ic(e)
            ic(index, timestamp)
            #import IPython; IPython.embed()
            if timestamp == '':
                continue
            raise e

        if debug:
            ic(index, timestamp)

        if after:
            if not is_after(timestamp=timestamp,
                            after=after,
                            inclusive=inclusive,
                            verbose=verbose,
                            debug=debug,):
                continue

        if before:
            if not is_before(timestamp=timestamp,
                             before=before,
                             inclusive=inclusive,
                             verbose=verbose,
                             debug=debug,):
                continue

        if newest:
            if not current_newest:
                current_newest = timestamp
                if verbose:
                    current_newest_human = timestamp_to_human_date(current_newest)
                    ic(current_newest, current_newest_human)
            else:
                if is_after(timestamp=timestamp,
                            after=current_newest,
                            inclusive=False,
                            verbose=verbose,
                            debug=debug,):
                    current_newest = timestamp
                    if verbose:
                        current_newest_human = timestamp_to_human_date(current_newest)
                        ic(current_newest, current_newest_human)

        if oldest:
            if not current_oldest:
                current_oldest = timestamp
                if verbose:
                    current_oldest_human = timestamp_to_human_date(current_oldest)
                    ic(current_oldest, current_oldest_human)
            else:
                if is_before(timestamp=timestamp,
                             before=current_oldest,
                             inclusive=False,
                             verbose=verbose,
                             debug=debug,):
                    current_oldest = timestamp
                    if verbose:
                        current_oldest_human = timestamp_to_human_date(current_oldest)
                        ic(current_oldest, current_oldest_human)

        if not (newest or oldest):
            print_result(timestamp=timestamp,
                         human=human,
                         end=end,
                         verbose=verbose,
                         debug=debug,)

        match_count += 1
        if exit_after_matches:
            if match_count >= exit_after_matches:
                sys.exit(0)

    if (newest or oldest):
        if newest:
            print_result(timestamp=current_newest,
                         human=human,
                         end=end,
                         verbose=verbose,
                         debug=debug,)
        if oldest:
            print_result(timestamp=current_oldest,
                         human=human,
                         end=end,
                         verbose=verbose,
                         debug=debug,)

