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
import click
import decimal
import dateparser
from icecream import ic
from enumerate_input import enumerate_input


def human_date_to_timestamp(date):
    dt = dateparser(date)
    timestamp = dt.timestamp()
    return decimal.Decimal(timestamp)


@click.command()
@click.argument("timestamps", type=str, nargs=-1)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--count', type=str)
@click.option('--before', type=str)
@click.option('--after', type=str)
@click.option("--printn", is_flag=True)
def cli(timestamps,
        before,
        after,
        verbose,
        debug,
        count,
        printn,):

    null = not printn

    if before:
        try:
            before = decimal.Decimal(before)
        except ValueError:
            before = human_date_to_timestamp(before)
    if after:
        try:
            after = decimal.Decimal(after)
        except ValueError:
            after = human_date_to_timestamp(after)

    now = decimal.Decimal(time.time())

    if verbose:
        ic(before, after, now)

    for index, timestamp in enumerate_input(iterator=timestamps,
                                            null=null,
                                            debug=debug,
                                            verbose=verbose):

        timestamp = decimal.Decimal(timestamp)
        if verbose:
            ic(index, timestamp)
        if after:
            if not timestamp.compare(after):
                continue

        print(timestamp)

        if count:
            if count > (index + 1):
                ic(count)
                sys.exit(0)


