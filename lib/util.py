from collections import OrderedDict
from pathlib import Path
from typing import (
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
)

from mako.template import Template
from thefuzz import fuzz

# type: ignore[no-untyped-def]


class CaseInsensitiveDict(MutableMapping):
    """A case-insensitive ``dict``-like object.

    Implements all methods and operations of
    ``MutableMapping`` as well as dict's ``copy``. Also
    provides ``lower_items``.

    All keys are expected to be strings. The structure remembers the
    case of the last key to be set, and ``iter(instance)``,
    ``keys()``, ``items()``, ``iterkeys()``, and ``iteritems()``
    will contain case-sensitive keys. However, querying and contains
    testing is case insensitive::

        cid = CaseInsensitiveDict()
        cid['Accept'] = 'application/json'
        cid['aCCEPT'] == 'application/json'  # True
        list(cid) == ['Accept']  # True

    For example, ``headers['content-encoding']`` will return the
    value of a ``'Content-Encoding'`` response header, regardless
    of how the header name was originally stored.

    If the constructor, ``.update``, or equality comparison
    operations are given keys that have equal ``.lower()``s, the
    behavior is undefined.
    """

    def __init__(self, data=None, **kwargs):  # type: ignore[no-untyped-def]
        self._store = OrderedDict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):  # type: ignore[no-untyped-def]
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value.
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):  # type: ignore[no-untyped-def]
        return self._store[key.lower()][1]

    def __delitem__(self, key):  # type: ignore[no-untyped-def]
        del self._store[key.lower()]

    def __iter__(self):  # type: ignore[no-untyped-def]
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):  # type: ignore[no-untyped-def]
        return len(self._store)

    def lower_items(self):  # type: ignore[no-untyped-def]
        """Like iteritems(), but with all lowercase keys."""
        return ((lowerkey, keyval[1]) for (lowerkey, keyval) in self._store.items())

    def __eq__(self, other):  # type: ignore[no-untyped-def]
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):  # type: ignore[no-untyped-def]
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):  # type: ignore[no-untyped-def]
        return str(dict(self.items()))


def get_similar_string(target: str, str_arr: set[str]) -> Tuple[str, float]:
    def get_similarity(a: str, b: str) -> float:
        return fuzz.ratio(a, b) / 100.0

    if target in str_arr:
        return target, 1.0
    most_similar = max(str_arr, key=lambda x: get_similarity(target, x))
    similarity = get_similarity(target, most_similar)
    return most_similar, similarity


def template(src: Union[Path, str], dst: Optional[Path], params: dict, newline: str = "\n") -> Optional[str]:
    if isinstance(src, Path):
        with open(src, "r", encoding="UTF-8") as f:
            tmpl_input = f.read()
    else:
        tmpl_input = src
    output = Template(tmpl_input).render(**params)
    if isinstance(dst, Path):
        with open(dst, "w", newline=newline, encoding="UTF-8") as f:
            f.write(output)
    else:
        return output
    return None


def map_yag_platform(exo_platform: Optional[str]) -> str:
    if exo_platform == "Windows":
        return "win"
    elif exo_platform == "DOS":
        return "dos"
    elif exo_platform == "Macintosh":
        return "mac"
    else:
        raise ValueError(f"Unknown platform: {exo_platform}")
