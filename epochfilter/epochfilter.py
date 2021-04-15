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


@click.command()
@click.argument("timestamps", type=str, nargs=-1)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--count', type=str)
@click.option('--before', type=str)
@click.option('--after', type=str)
@click.option("--inclusive", is_flag=True)
@click.option("--printn", is_flag=True)
def cli(timestamps,
        before: str,
        after: str,
        inclusive: bool,
        verbose: bool,
        debug: bool,
        count: bool,
        printn: bool,
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

    if verbose:
        ic(before, after, now)

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
            acceptable_results = [Decimal('1')]
            if inclusive:
                acceptable_results.append(Decimal('0'))
            if debug:
                ic(acceptable_results)
            result = timestamp.compare(after)
            if debug:
                ic(result)
            if result not in acceptable_results:
                continue

        if before:
            acceptable_results = [Decimal('-1')]
            if inclusive:
                acceptable_results.append(Decimal('0'))
            if debug:
                ic(acceptable_results)
            result = timestamp.compare(before)
            if debug:
                ic(result)
            if result not in acceptable_results:
                continue

        print(timestamp, end=end)

        if count:
            if count > (index + 1):
                ic(count)
                sys.exit(0)

