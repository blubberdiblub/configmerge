#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module provides the ability to merge multiple configuration files of
different formats (JSON, YAML, properties) into a single configuration.

The key functions are:

- merge() - merges multiple configuration files into one config dict
- merge_dict() - merge two dicts recursively
- load() - depending on file extension, load YAML, JSON or Java properties
- load_json(), load_yaml(), load_props() - load individual config files

Example usage:

merged_config = merge(["config1.json", "config2.yml"])

"""


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

from frozendict import FrozenOrderedDict


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

        # noinspection PyUnresolvedReferences
        from ruamel.yaml import YAML

    except ImportError:

        # noinspection PyPackageRequirements
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

        # noinspection PyUnresolvedReferences
        from ruamel.yaml import YAML

    except ImportError:

        # noinspection PyPackageRequirements
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


def merge(value1: Any, value2: Any) -> Any:

    """Merge two configuration data structures recursively.

    This handles merging of various types, e.g.:

    - dictionaries (dict) and other mappings
    - lists, tuples and other sequences
    - strings, numbers, booleans, etc.

    Complex objects like dictionaries are merged recursively.

    Args:
        value1: The first value to merge.
        value2: The second value to merge.

    Returns:
        The merged configuration value.

    Raises:
        TypeError: If types cannot be merged.

    Examples:

        >>> merge({'a': 1}, {'b': 2})
        {'a': 1, 'b': 2}

        >>> merge([1, 2], [3, 4])
        [1, 2, 3, 4]

    """

    if value2 is None:
        return value1

    if value1 is None:
        return value2

    if isinstance(value1, Mapping):

        if not isinstance(value1, MutableMapping):
            raise TypeError("mapping must be mutable")

        if not isinstance(value2, Mapping):
            raise TypeError("can only merge another mapping into mapping")

        merge_dict(value1, value2)
        return value1

    if isinstance(value1, Sequence) and not isinstance(value1, Text):

        if not isinstance(value1, MutableSequence):
            raise TypeError("sequence must be mutable")

        if not isinstance(value2, Sequence):
            raise TypeError("can only merge another sequence into sequence")

        merge_list(value1, value2)
        return value1

    return merge_simple(value1, value2)


def merge_dict(d1: MutableMapping, d2: Mapping) -> None:

    for key, value in d2.items():

        if key not in d1:
            d1[key] = value
            continue

        d1[key] = merge(d1[key], value)


def deep_freeze(obj: Any) -> Any:

    """Recursively freeze a data structure to be immutable.

    Traverses the structure and converts mutable types like mappings
    and sequences to immutable versions to avoid mutation issues.

    Supported conversions:

    - Mappings (e.g. dict) -> FrozenOrderedDict
    - Sequences (e.g. list) -> tuple

    Other mutable types may also be converted to immutable
    equivalents where applicable.

    Args:
        obj: The object to recursively freeze

    Returns:
        The frozen immutable version

    """

    if obj is None:
        return obj

    if isinstance(obj, bool):
        return bool(obj)

    if isinstance(obj, Integral):
        return int(obj)

    if isinstance(obj, Real):
        return float(obj)

    if isinstance(obj, Text):
        return str(obj)

    if isinstance(obj, Mapping):

        if not isinstance(obj, MutableMapping):
            return FrozenOrderedDict(obj)

        return FrozenOrderedDict((deep_freeze(key), deep_freeze(value))
                                 for key, value in obj.items())

    if isinstance(obj, Sequence):

        if not isinstance(obj, MutableSequence):
            return tuple(obj)

        return tuple(deep_freeze(item) for item in obj)

    raise TypeError("unsupported type")


def merge_list(l1: MutableSequence, l2: Sequence) -> None:

    member = set(deep_freeze(item) for item in l1)

    for value in l2:

        frozen = deep_freeze(value)
        if frozen in member:
            continue

        l1.append(value)
        member.add(frozen)


def merge_simple(value1: Any, value2: Any) -> Any:

    """Merge two simple values: strings, numbers, booleans.

    Raises TypeError if types differ or are unsupported.

    If types match, value2 takes precedence.

    Args:
      value1: The first value to merge.
      value2: The second value to merge.

    Returns:
      The merged value.

    Raises:
      TypeError: If types differ or are unsupported.

    Examples:

      >>> merge_simple('a', 'b')
      'b'

      >>> merge_simple(1, 2)
      2

    """

    if isinstance(value1, bool) and isinstance(value2, bool):
        return value2

    if isinstance(value1, Integral) and isinstance(value2, Integral):
        return value2

    if isinstance(value1, Real) and isinstance(value2, Real):
        return value2

    if isinstance(value1, Text) and isinstance(value2, Text):
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
        d = None

    for merge_file in merge_files:

        m = load(merge_file)
        d = merge(d, m)

    with open(destination, mode='wb') as f:
        save(f, d)


if __name__ == '__main__':
    main()
