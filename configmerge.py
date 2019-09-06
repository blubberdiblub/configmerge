#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import (
    Any,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
    Text,
)

import click
import pathlib

from numbers import Integral, Real


def load(f) -> MutableMapping:

    p = pathlib.PurePath(f.name)

    if p.suffix.casefold() in ['.yml', '.yaml']:
        return load_yaml(f)

    if p.suffix.casefold() == '.json':
        return load_json(f)

    if p.suffix.casefold() == '.properties':
        return load_props(f)

    raise TypeError("unknown file type")


def load_yaml(f) -> MutableMapping:

    try:

        from ruamel.yaml import YAML

    except ImportError:

        import yaml

        kwargs = {
            'Loader': yaml.SafeLoader,
        }

    else:

        yaml = YAML()
        kwargs = {}

    return yaml.load(f, **kwargs)


def load_json(f) -> MutableMapping:

    import json
    return json.load(f)


def load_props(f) -> MutableMapping:

    import jprops
    return jprops.load_properties(f)


def save(f, d: Mapping) -> None:

    p = pathlib.PurePath(f.name)

    if p.suffix.casefold() in ['.yml', '.yaml']:
        return save_yaml(f, d)

    if p.suffix.casefold() == '.json':
        return save_json(f, d)

    if p.suffix.casefold() == '.properties':
        return save_props(f, d)

    raise TypeError("unknown file type")


def save_yaml(f, d: Mapping) -> None:

    try:

        from ruamel.yaml import YAML

    except ImportError:

        import yaml

        class _IndentDumper(yaml.SafeDumper):

            def increase_indent(self, flow=False, indentless=False):

                return super().increase_indent(flow, False)

        kwargs = {
            'Dumper': _IndentDumper,
            'encoding': 'utf-8',
        }

    else:

        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        kwargs = {}

    yaml.dump(d, f, **kwargs)


def save_json(f, d: Mapping) -> None:

    import json
    f.write(json.dumps(d, ensure_ascii=False, indent=2).encode('utf-8'))


def save_props(f, d: Mapping) -> None:

    import jprops
    jprops.store_properties(f, d)


def merge_dict(d1: MutableMapping, d2: Mapping) -> None:

    for k, v in d2.items():

        if k not in d1:
            d1[k] = v
            continue

        existing = d1[k]

        if isinstance(existing, MutableMapping) and isinstance(v, Mapping):
            merge_dict(existing, v)
            continue

        if isinstance(existing, MutableSequence) and isinstance(v, Sequence):
            merge_list(existing, v)
            continue

        d1[k] = merge_simple(existing, v)


def merge_list(l1: MutableSequence, l2: Sequence) -> None:

    l1[:] = l2


def merge_simple(value1: Any, value2: Any) -> Any:

    if value2 is None:
        return value1

    if value1 is None:
        return value2

    if isinstance(value1, bool) and isinstance(value2, bool):
        return value2

    if isinstance(value1, Integral) and isinstance(value2, Integral):
        return value2

    if isinstance(value1, Real) and isinstance(value2, Real):
        return value2

    if isinstance(value1, Text) and isinstance(value2, Text):
        return value2

    if isinstance(value1, Mapping) and isinstance(value2, Mapping):
        return value2

    if isinstance(value1, Sequence) and isinstance(value2, Sequence):
        return value2

    raise TypeError("unsupported type or type combination")


@click.command()
@click.argument('destination', type=click.Path(dir_okay=False, writable=True))
@click.argument('merge-files', nargs=-1, type=click.File(mode='rb', lazy=True))
def main(destination, merge_files):

    try:
        with open(destination, mode='rb') as f:
            d = load(f)

    except FileNotFoundError:
        d = {}

    for merge_file in merge_files:
        merge_dict(d, load(merge_file))

    with open(destination, mode='wb') as f:
        save(f, d)


if __name__ == '__main__':
    main()
