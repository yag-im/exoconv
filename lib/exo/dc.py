from typing import (
    List,
    Optional,
)

from marshmallow_dataclass import dataclass


@dataclass
class GameMeta0:
    @dataclass
    class Entity:
        child_part: str
        has_menu: bool
        platform: Optional[str]
        distro_format: Optional[str]

    parent_part: str
    releases: List[Entity]


@dataclass
class GameMeta1:
    parent_part: str
    title: str
    publisher: str
    rating: str
    release_year: int
    genre: List[str]


@dataclass
class GameMeta2:
    parent_part: str
    scummvm_game: str
    scummvm_ver: Optional[str]


@dataclass
class ScummvmMeta(GameMeta1, GameMeta2):
    @dataclass
    class Entity(GameMeta0.Entity):
        scummvm_game: Optional[str]
        scummvm_ver: Optional[str]

    parent_part: str
    releases: List[Entity]
