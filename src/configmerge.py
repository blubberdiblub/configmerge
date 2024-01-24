#!/usr/bin/env python3

from __future__ import annotations as _annotations

"""
Provides the ability to merge multiple configuration files of
different formats (JSON, YAML, properties) into a single configuration.

The key functions are:

- merge() : Merge multiple configuration files into one config dict.
- merge_dict() : Merge two dicts recursively.
- load() : Depending on file extension, load YAML, JSON or Java properties.
- load_json() : Load a JSON config file.
- load_yaml() : Load a YAML config file.
- load_props() : Load a Java properties config file.

Examples
--------
>>> from pathlib import Path
>>> with Path("config1.json").open('rb') as f1,
...      Path("config2.properties").open('rb') as f2:
...     dest = load(f1)
...     merged = merge(dest, load(f2))
>>> with Path("result.yaml").open('wb') as f:
...     save(f, merged)

"""

import pathlib

from collections.abc import Mapping, MutableMapping, MutableSequence, Sequence
from numbers import Integral, Real
from shutil import get_terminal_size

import click

from frozendict import FrozenOrderedDict

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections.abc import Hashable
    from os import PathLike
    from typing import BinaryIO

TERMINAL_WIDTH = get_terminal_size().columns or 80


def load(f: BinaryIO) -> MutableMapping[Hashable, object]:

    """
    Load a structured data from a YAML, JSON or properties file.

    Parameters
    ----------
    f : BinaryIO
        The file-like object to load the data from.

    Returns
    -------
    MutableMapping
        A mutable mapping (usually a dict) representing the loaded data.

    Examples
    --------
    >>> from io import BytesIO
    >>> data = b'name: John\nage: 30\n---\n'
    >>> _my_file = BytesIO(data)
    >>> _my_file.name = 'file.yml'
    >>> load(_my_file)
    {'name': 'John', 'age': 30}

    >>> data = b'{"name": "John", "age": 30}'
    >>> _my_file = BytesIO(data)
    >>> _my_file.name = 'file.json'
    >>> load(_my_file)
    {'name': 'John', 'age': 30}

    >>> data = b'name=John\nage=30\n'
    >>> _my_file = BytesIO(data)
    >>> _my_file.name = 'file.properties'
    >>> load(_my_file)
    {'name': 'John', 'age': '30'}

    """

    p = pathlib.PurePath(f.name)

    if p.suffix.casefold() in ['.yml', '.yaml']:
        return load_yaml(f)

    if p.suffix.casefold() == '.json':
        return load_json(f)

    if p.suffix.casefold() == '.properties':
        return load_props(f)

    raise TypeError("unknown file type")


def load_yaml(f: BinaryIO) -> MutableMapping[Hashable, object]:

    """
    Load a YAML file into a dictionary.

    Parameters
    ----------
    f : BinaryIO
        The file object to load.

    Returns
    -------
    MutableMapping
        A dictionary containing the loaded YAML data.

    Examples
    --------
    >>> from io import BytesIO
    >>> data = b'{"name": "John", "age": 30}'
    >>> file_object = BytesIO(data)
    >>> load_yaml(file_object)
    {'name': 'John', 'age': 30}

    """

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


def load_json(f: BinaryIO) -> MutableMapping[Hashable, object]:

    """
    Loads a JSON file and returns its content as a mutable mapping.

    Parameters
    ----------
    f : BinaryIO
        The file to load a JSON object from.

    Returns
    -------
    MutableMapping
        A mutable mapping (usually a dict)
        representing the content of the JSON file.

    Examples
    --------
    >>> from io import BytesIO
    >>> data = b'{"name": "John", "age": 30}'
    >>> file_object = BytesIO(data)
    >>> load_json(file_object)
    {'name': 'John', 'age': 30}

    """

    import json
    return json.load(f)


def load_props(f: BinaryIO) -> MutableMapping[Hashable, object]:

    """
    Loads a Java properties file
    and returns its key-value pairs as a mutable mapping.

    Parameters
    ----------
    f : BinaryIO
        The file to load properties from.

    Returns
    -------
    MutableMapping
        A mutable mapping (usually a dict) representing the loaded properties.

    Examples
    --------
    >>> from io import BytesIO
    >>> data = b'key1=value1\nkey2=value2\nkey3=value3'
    >>> file_object = BytesIO(data)
    >>> load_props(file_object)
    {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

    """

    import jprops
    return jprops.load_properties(f)


def save(f: BinaryIO, d: Mapping[Hashable, object]) -> None:

    """
    Saves the given mapping `d` to the file `f`.

    Parameters
    ----------
    f : BinaryIO
        The file to save the mapping to.
    d : Mapping
        The mapping to be saved.

    Raises
    ------
    TypeError
        If the file type is unknown.

    Returns
    -------
    None

    """

    p = pathlib.PurePath(f.name)

    if p.suffix.casefold() in ['.yml', '.yaml']:
        return save_yaml(f, d)

    if p.suffix.casefold() == '.json':
        return save_json(f, d)

    if p.suffix.casefold() == '.properties':
        return save_props(f, d)

    raise TypeError("unknown file type")


def save_yaml(f: BinaryIO, d: Mapping[Hashable, object]) -> None:

    """
    Saves a YAML representation of the given mapping into a file-like object.

    Parameters
    ----------
    f : BinaryIO
        The file-like object to save the YAML representation into.
    d : Mapping
        The mapping (such as a dict) containing the data to be saved.

    Raises
    ------
    ImportError
        If the required YAML library (ruamel.yaml or yaml) is not installed.

    Notes
    -----
    This function first tries to import ruamel.yaml. If it fails, it falls back
    to using the PyYAML. The YAML representation is rendered with visually
    more pleasing indentation even if only PyYAML is available.

    Examples
    --------
    >>> from io import BytesIO
    >>> data = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
    >>> file_object = BytesIO()
    >>> save_yaml(file_object, data)
    >>> file_object.getvalue()
    b'key1: value1\nkey2: value2\nkey3: value3\n'

    """

    try:

        # noinspection PyUnresolvedReferences
        from ruamel.yaml import YAML

    except ImportError:

        # noinspection PyPackageRequirements
        import yaml

        class _IndentDumper(yaml.SafeDumper):

            def increase_indent(self, flow: bool = False, indentless: bool = False):

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


def save_json(f: BinaryIO, d: Mapping[Hashable, object]) -> None:

    """
    Save a mapping as JSON into a file.

    Parameters
    ----------
    f : BinaryIO
        The file-like object to save the JSON data into.
    d : Mapping
        The mapping (such as a dict) containing the data to be saved as JSON.

    Notes
    -----
    This function converts the mapping into a JSON string
    and writes it into the file-like object, encoded as UTF-8.

    Examples
    --------
    >>> from io import BytesIO
    >>> data = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
    >>> file_object = BytesIO()
    >>> save_json(file_object, data)
    >>> file_object.getvalue()
    b'{\n  "key1": "value1",\n  "key2": "value2",\n  "key3": "value3"\n}'

    """

    import json
    f.write(json.dumps(d, ensure_ascii=False, indent=2).encode('utf-8'))


def save_props(f: BinaryIO, d: Mapping[Hashable, object]) -> None:

    """
    Saves properties from a mapping into a file-like object.

    Parameters
    ----------
    f : BinaryIO
        The file-like object to save the properties into.
    d : Mapping
        The mapping (such as a dict) containing the properties to be saved.

    Examples
    --------
    >>> from io import BytesIO
    >>> data = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
    >>> file_object = BytesIO()
    >>> save_props(file_object, data)
    >>> file_object.getvalue()
    b'key1=value1\nkey2=value2\nkey3=value3\n'

    """

    import jprops
    jprops.store_properties(f, d)


def merge(value1: object, value2: object) -> object:

    """
    Merge two configuration data structures recursively.

    This handles merging of various types, e.g.:

    - dictionaries (dict) and other mappings
    - lists, tuples and other sequences
    - strings, numbers, booleans, etc.

    Complex objects like dictionaries are merged recursively.

    Parameters
    ----------
    value1 : object
        The first value to merge.
    value2 : object
        The second value to merge.

    Returns
    -------
    object
        The merged configuration value.

    Raises
    ------
    TypeError
        If types cannot be merged.

    Examples
    --------
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

    if isinstance(value1, Sequence) and not isinstance(value1, str):

        if not isinstance(value1, MutableSequence):
            raise TypeError("sequence must be mutable")

        if not isinstance(value2, Sequence):
            raise TypeError("can only merge another sequence into sequence")

        merge_list(value1, value2)
        return value1

    return merge_simple(value1, value2)


def merge_dict(d1: MutableMapping[Hashable, object], d2: Mapping[Hashable, object]) -> None:

    """
    Merge two mappings recursively.

    Mutates d1 in-place to contain items from both mappings.
    If keys match, recursively merges values.

    Parameters
    ----------
    d1 : MutableMapping
        The mapping to merge into, mutated in-place.
    d2 : Mapping
        The other mapping to merge from.

    Examples
    --------
    >>> d1 = {'a': 1, 'b': 2}
    >>> d2 = {'b': 3, 'c': 4}
    >>> merge_dict(d1, d2)
    >>> d1
    {'a': 1, 'b': 3, 'c': 4}
    """

    for key, value in d2.items():

        if key not in d1:
            d1[key] = value
            continue

        d1[key] = merge(d1[key], value)


def deep_freeze(obj: object) -> object:

    """
    Recursively freeze a data structure to be immutable.

    Traverses the structure and converts mutable types like mappings
    and sequences to immutable versions to avoid mutation issues.

    Supported conversions:

    - Mappings (e.g. dict) -> FrozenOrderedDict
    - Sequences (e.g. list) -> tuple

    Other mutable types may also be converted to immutable
    equivalents where applicable.

    Parameters
    ----------
    obj : object
        The object to recursively freeze.

    Returns
    -------
    object
        The frozen immutable version of the input object.

    """

    if obj is None:
        return obj

    if isinstance(obj, bool):
        return bool(obj)

    if isinstance(obj, Integral):
        return int(obj)

    if isinstance(obj, Real):
        return float(obj)

    if isinstance(obj, str):
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


def merge_list(l1: MutableSequence[object], l2: Sequence[object]) -> None:

    """
    Merge two sequences, omitting duplicates coming from l2.

    Deep freezes items from both inputs
    and adds items from l2 to l1 if not already present.

    Parameters
    ----------
    l1 : MutableSequence
        The first sequence. Mutated in-place.
    l2 : Sequence
        The second sequence.

    Returns
    -------
    None
        Mutates l1 in-place.

    Examples
    --------
    >>> l1 = [1, 2, 1]
    >>> l2 = [3, 4, 1, 5]
    >>> merge_list(l1, l2)
    >>> l1
    [1, 2, 1, 3, 4, 5]

    """

    member = {deep_freeze(item) for item in l1}

    for value in l2:

        frozen = deep_freeze(value)
        if frozen in member:
            continue

        l1.append(value)
        member.add(frozen)


def merge_simple(value1: object, value2: object) -> object:

    """
    Merge two simple values: strings, numbers, booleans.

    Parameters
    ----------
    value1 : str, Real, Integral, bool
        The first value to merge.
    value2 : str, Real, Integral, bool
        The second value to merge.

    Returns
    -------
    merged_value : str, float, int, bool
        The merged value.

    Raises
    ------
    TypeError
        If types differ or are unsupported.

    Examples
    --------
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

    if isinstance(value1, str) and isinstance(value2, str):
        return value2

    raise TypeError("unsupported type or type combination")


@click.command()
@click.argument('destination', type=click.Path(dir_okay=False, writable=True))
@click.argument('merge-files', nargs=-1, type=click.File(mode='rb', lazy=True))
def main(destination: PathLike[str], merge_files: Sequence[BinaryIO],
         max_content_width: int = TERMINAL_WIDTH) -> None:

    """
    Merge multiple configuration files into a single file.

    This command reads data from one or more source files, merges it with the
    data from a destination file, and saves the result back to the destination
    file. The source files can be in YAML, JSON, or Java properties format.

    \b
    DESTINATION
        The path to the destination file where the merged data will be saved.

    \b
    MERGE_FILES
        Any number of files to be read and merged with the destination file.

    Example:

    \b
    $ configmerge.py output.yaml file1.yaml file2.yaml

    In this example, the command merges the data from file1.yaml and file2.yaml
    with the data from output.yaml and saves the result back to output.yaml.
    """

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
    raise SystemExit(main())
