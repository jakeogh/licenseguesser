#!/usr/bin/env python3
# -*- coding: utf8 -*-

# pylint: disable=invalid-name                    # [C0103] single letter var names, name too descriptive
# pylint: disable=too-many-return-statements      # [R0911]
# pylint: disable=too-many-branches               # [R0912]
# pylint: disable=too-many-statements             # [R0915]
# pylint: disable=too-many-arguments              # [R0913]
# pylint: disable=too-many-nested-blocks          # [R1702]
# pylint: disable=too-many-locals                 # [R0914]
# pylint: disable=too-few-public-methods          # [R0903]
# pylint: disable=no-member                       # [E1101] no member for base
# pylint: disable=attribute-defined-outside-init  # [W0201]
# pylint: disable=too-many-boolean-expressions    # [R0916] in if statement
from __future__ import annotations

import os
import re
from collections import defaultdict
from pathlib import Path

import click
from asserttool import ic
from clicktool import click_add_options
from clicktool import click_global_options
from clicktool import tvicgvd
from getdents import files_pathlib
from globalverbose import gvd
from Levenshtein import StringMatcher
from unmp import unmp


def find_closest_string_distance(
    *,
    string_dict: dict,
    in_string,
):
    distances_to_paths = defaultdict(list)
    distance = -1
    #ic(len(string_dict))
    for path_key, string in string_dict.items():
        dist = StringMatcher.distance(in_string, string)
        #ic(dist, path_key)
        distances_to_paths[dist].append(path_key)
        if distance < 0:
            distance = dist
            winning_key = path_key
        else:
            if dist < distance:
                distance = dist
                winning_key = path_key

    #if verbose:
    #    for path_distance in distances_to_paths.keys():
    #        ic(path_distance)
    #        for path in distances_to_paths[path_distance]:
    #            ic(path)

    #    print("\n", file=sys.stderr)
    #    eprint("\n", in_string)
    #    ic(winning_key)
    #    eprint("\n", string_dict[winning_key])
    #    ic(distance, winning_key)
    #    winning_distances = sorted(distances_to_paths.keys())[:10]
    #    for distance in winning_distances:
    #        ic(distance, distances_to_paths[distance])

    return winning_key


def linearize_text(text):
    text = text.splitlines()
    if "copyright" in text[0].lower():
        text = text[1:]
    text = " ".join(text)
    #ic(len(text))
    text = re.sub(r"[\W]+", " ", text).strip().lower()
    #ic(len(text))
    return text


def build_license_dict(path):
    license_dict = {}

    for index, license_path in enumerate(files_pathlib(path)):
        with open(license_path, "r") as fh:
            path_data = fh.read()
        linear_text = linearize_text(
            path_data,
        )
        license_dict[license_path] = linear_text
    return license_dict


def build_license_list(path="/var/db/repos/gentoo/licenses"):
    license_list = []

    for license_path in files_pathlib(path):
        ic(license_path)
        license_list.append(license_path.name)

    return sorted(license_list)


@click.command()
# @click.argument("license_corpus",
#                type=click.Path(exists=True,
#                                dir_okay=True,
#                                file_okay=False,
#                                path_type=Path,
#                                allow_dash=False),
#                nargs=1,
#                required=True,
#                default='/var/db/repos/gentoo/licenses',)
@click.argument(
    "license_files",
    type=click.Path(
        exists=True, dir_okay=False, file_okay=True, path_type=Path, allow_dash=False
    ),
    nargs=-1,
    required=False,
)
@click.option("--list", "list_licenses", is_flag=True)
@click_add_options(click_global_options)
@click.pass_context
def cli(
    ctx,
    license_files: Path,
    verbose_inf: bool,
    dict_output: bool,
    list_licenses: bool,
    verbose: bool = False,
):
    tty, verbose = tvicgvd(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
        ic=ic,
        gvd=gvd,
    )

    license_corpus = Path("/var/db/repos/gentoo/licenses")

    if list_licenses:
        license_list = build_license_list(
            path=license_corpus,
        )
        for license in license_list:
            print(license)
        return

    license_dict = build_license_dict(
        path=license_corpus,
    )

    if license_files:
        iterator = license_files
    else:
        iterator = unmp(valid_types=[bytes])

    for index, path in enumerate(iterator):
        _path = Path(os.fsdecode(path)).expanduser()
        #ic(index, _path)

        with open(_path, "r", encoding="utf8") as fh:
            path_data = fh.read()

        linear_license = linearize_text(
            text=path_data,
        )

        closest_guess = find_closest_string_distance(
            string_dict=license_dict,
            in_string=linear_license,
        )
        ic(closest_guess)
