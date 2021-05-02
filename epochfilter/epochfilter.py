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


import os
import sys
import time
from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation

import click
import dateparser
from enumerate_input import enumerate_input
from icecream import ic


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
@click.option('--oldest', is_flag=True)
@click.option('--newest', is_flag=True)
@click.option("--inclusive", is_flag=True)
@click.option("--human", is_flag=True)
@click.option("--exit-after-matches", type=int)
@click.option("--printn", is_flag=True)
def cli(timestamps,
        before: str,
        after: str,
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

    if before:
        try:
            before = Decimal(before)
        except InvalidOperation:
            before = human_date_to_timestamp(before)

    if after:
        try:
            after = Decimal(after)
        except InvalidOperation:
            after = human_date_to_timestamp(after)

    now = Decimal(time.time())

    if (before or after):
        ic(before, after, now)

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

        timestamp = Decimal(timestamp)
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
                    ic(current_newest)
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
                    ic(current_oldest)
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

