#!/usr/bin/env python3
# -*- coding: utf8 -*-

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
import re
import sys
from pathlib import Path

import click
from enumerate_input import enumerate_input
from getdents import files
from kcl.configops import click_read_config
from kcl.configops import click_write_config_entry
from Levenshtein import StringMatcher


def eprint(*args, **kwargs):
    if 'file' in kwargs.keys():
        kwargs.pop('file')
    print(*args, file=sys.stderr, **kwargs)


try:
    from icecream import ic  # https://github.com/gruns/icecream
except ImportError:
    ic = eprint


def find_closest_string_distance(*,
                                 string_dict,
                                 in_string,
                                 verbose: bool,
                                 debug: bool,):
    distance = -1
    if verbose:
        ic(len(string_dict))
    for key, string in string_dict.items():
        dist = StringMatcher.distance(in_string, string)
        ic(string, dist)
        if distance < 0:
            distance = dist
            winning_string = string_dict[key]
        else:
            if dist < distance:
                distance = dist
                winning_string = string
    if verbose:
        eprint("Converting {0} to {1}".format(in_string, winning_string))

    return winning_string


def linearize_text(text, *,
                   verbose: bool,
                   debug: bool,):
    if verbose:
        ic(len(text))
    text = re.sub(r'[\W]+', ' ', text).strip().lower()
    if verbose:
        ic(len(text))
    return text


def build_license_dict(path, *,
                       verbose: bool,
                       debug: bool,):
    license_dict = {}

    for index, license_path in enumerate(files(path, verbose=verbose, debug=debug)):
        license_path = Path(license_path)
        if verbose:
            ic(index, license_path)
        with open(license_path, 'r') as fh:
            path_data = fh.read()
        linear_text = linearize_text(path_data, verbose=verbose, debug=debug)
        license_dict[license_path] = linear_text
    return license_dict


@click.command()
@click.argument("license_corpus",
                type=click.Path(exists=True,
                                dir_okay=True,
                                file_okay=False,
                                path_type=str,
                                allow_dash=False),
                nargs=1,
                required=True)
@click.argument("license_files",
                type=click.Path(exists=True,
                                dir_okay=False,
                                file_okay=True,
                                path_type=str,
                                allow_dash=False),
                nargs=-1,
                required=False)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--ipython', is_flag=True)
@click.option("--printn", is_flag=True)
@click.option("--progress", is_flag=True)
@click.pass_context
def cli(ctx,
        license_corpus,
        license_files,
        verbose,
        debug,
        ipython,
        progress,
        printn,):

    null = not printn
    end = '\n'
    if null:
        end = '\x00'
    if sys.stdout.isatty():
        end = '\n'
        assert not ipython

    #progress = False
    if (verbose or debug):
        progress = False

    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug
    ctx.obj['end'] = end
    ctx.obj['null'] = null
    ctx.obj['progress'] = progress

    license_dict = build_license_dict(path=license_corpus,
                                      verbose=verbose,
                                      debug=debug,)

    iterator = license_files

    for index, path in enumerate_input(iterator=iterator,
                                       null=null,
                                       skip=None,
                                       head=None,
                                       tail=None,
                                       progress=progress,
                                       debug=debug,
                                       verbose=verbose,):
        path = Path(path)

        if verbose:
            ic(index, path)

        with open(path, 'r') as fh:
            path_data = fh.read()

        linear_license = linearize_text(text=path_data,
                                        verbose=verbose,
                                        debug=debug,)

        closest_guess = find_closest_string_distance(string_dict=license_dict,
                                                     in_string=linear_license,
                                                     verbose=verbose,
                                                     debug=debug,)
        ic(closest_guess)

