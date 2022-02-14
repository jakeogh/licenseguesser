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
from collections import defaultdict
from math import inf
from pathlib import Path
from typing import Union

import click
from asserttool import ic
from clicktool import click_add_options
from clicktool import click_global_options
from clicktool import tv
from eprint import eprint
from getdents import files
from Levenshtein import StringMatcher
from unmp import unmp


def find_closest_string_distance(*,
                                 string_dict: dict,
                                 in_string,
                                 verbose: Union[bool, int, float],
                                 ):

    distances_to_paths = defaultdict(list)
    distance = -1
    if verbose:
        ic(len(string_dict))
    for path_key, string in string_dict.items():
        dist = StringMatcher.distance(in_string, string)
        if verbose:
            ic(dist, path_key)
        distances_to_paths[dist].append(path_key)
        if distance < 0:
            distance = dist
            winning_key = path_key
        else:
            if dist < distance:
                distance = dist
                winning_key = path_key

    if verbose:
        for path_distance in distances_to_paths.keys():
            ic(path_distance)
            for path in distances_to_paths[path_distance]:
                ic(path)

        print("\n", file=sys.stderr)
        eprint('\n', in_string)
        ic(winning_key)
        eprint('\n', string_dict[winning_key])
        ic(distance, winning_key)
        winning_distances = sorted(distances_to_paths.keys())[:10]
        for distance in winning_distances:
            ic(distance, distances_to_paths[distance])

    return winning_key


def linearize_text(text, *,
                   verbose: Union[bool, int, float],
                   ):
    text = text.splitlines()
    if 'copyright' in text[0].lower():
        text = text[1:]
    text = ' '.join(text)
    if verbose == inf:
        ic(len(text))
    text = re.sub(r'[\W]+', ' ', text).strip().lower()
    if verbose == inf:
        ic(len(text))
    return text


def build_license_dict(path, *,
                       verbose: Union[bool, int, float],
                       ):
    license_dict = {}

    for index, license_path in enumerate(files(path, verbose=verbose,)):
        license_path = Path(license_path)
        if verbose:
            ic(index, license_path)
        with open(license_path, 'r') as fh:
            path_data = fh.read()
        linear_text = linearize_text(path_data, verbose=verbose,)
        license_dict[license_path] = linear_text
    return license_dict


def build_license_list(path='/var/db/repos/gentoo/licenses', *,
                       verbose: Union[bool, int, float],
                       ):
    license_list = []

    for license_path in files(path, verbose=verbose,):
        license_path = Path(license_path)
        if verbose:
            ic(license_path)
        license_list.append(license_path.name)

    return sorted(license_list)


@click.command()
#@click.argument("license_corpus",
#                type=click.Path(exists=True,
#                                dir_okay=True,
#                                file_okay=False,
#                                path_type=Path,
#                                allow_dash=False),
#                nargs=1,
#                required=True,
#                default='/var/db/repos/gentoo/licenses',)
@click.argument("license_files",
                type=click.Path(exists=True,
                                dir_okay=False,
                                file_okay=True,
                                path_type=Path,
                                allow_dash=False),
                nargs=-1,
                required=False,)
@click.option('--ipython', is_flag=True)
@click.option('--list', 'list_licenses', is_flag=True)
@click_add_options(click_global_options)
@click.pass_context
def cli(ctx,
        license_files: Path,
        verbose: Union[bool, int, float],
        verbose_inf: bool,
        list_licenses: bool,
        ipython: bool,
        ):

    tty, verbose = tv(ctx=ctx,
                      verbose=verbose,
                      verbose_inf=verbose_inf,
                      )

    license_corpus = Path('/var/db/repos/gentoo/licenses')

    if list_licenses:
        license_list = build_license_list(path=license_corpus,
                                          verbose=verbose,
                                          )
        for license in license_list:
            print(license)
        return

    license_dict = build_license_dict(path=license_corpus,
                                      verbose=verbose,
                                      )

    if license_files:
        iterator = license_files
    else:
        iterator = unmp(valid_types=[bytes], verbose=verbose)

    for index, path in enumerate(iterator):
        _path = Path(os.fsdecode(path)).expanduser()
        if verbose:
            ic(index, _path)

        with open(_path, 'r', encoding='utf8') as fh:
            path_data = fh.read()

        linear_license = linearize_text(text=path_data,
                                        verbose=verbose,
                                        )

        closest_guess = find_closest_string_distance(string_dict=license_dict,
                                                     in_string=linear_license,
                                                     verbose=verbose,
                                                     )
        ic(closest_guess)
